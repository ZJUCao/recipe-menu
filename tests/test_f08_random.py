"""Tests of F08 for create_data_folder with random calls (T28).

The test builds each call from a seeded generator and computes the expected record, result, and
tree from the steps of design 3.2 and the rules of the fault harness. It uses no code of F08.
"""

import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from f08_support import (
    CTRL_C,
    DENIED,
    FOLDER,
    IO,
    NO_SPACE,
    Entry,
    Rule,
    Step,
    assert_failed,
    faults,
    file_of,
    make_steps,
    problem_file,
    rel,
    rule,
    tree,
)
from f08_texts import (
    FILE_EXISTS,
    FILE_WRITE_DENIED,
    FOLDER_CREATE_DENIED,
    FOLDER_EXISTS,
    Msg,
    file_error,
    folder_error,
)
from recipe_menu.datafile import Creation, CreationOutcome, DataFolder, create_data_folder

PIECES = ("x", "\n", "\r\n", "番茄", " ")
EFFECTS = ("DENIED", "IO", "race", "CTRL_C", "after CTRL_C")
ROWS: dict[str, tuple[Msg, Msg]] = {
    "DENIED": (FOLDER_CREATE_DENIED, FILE_WRITE_DENIED),
    "IO": (folder_error("Input/output error"), file_error("Input/output error")),
    "race": (FOLDER_EXISTS, FILE_EXISTS),
    "write": (FOLDER_EXISTS, file_error("No space left on device")),
}


@dataclass
class Plan:
    """One random call: the start, the arguments, the fault, and the denied removals."""

    base: Path
    start: int
    folders: list[Path]
    files: list[tuple[Path, str]]
    fault: tuple[int, str] | None = None
    denied: set[int] = field(default_factory=set)

    @property
    def root(self) -> Path:
        """Gives the data folder of the call."""
        return self.base / "a" / "b" / "recipe-menu"


def _prepare(plan: Plan) -> None:
    """Makes the start state on the disk: the folders above R and R, as far as the start says."""
    for path in [plan.base / "a", plan.base / "a" / "b", plan.root][: plan.start]:
        path.mkdir()


def _random_items(rng: random.Random, plan: Plan) -> None:
    """Picks the folders and the files of a call."""
    for number in range(1, rng.randint(0, 4) + 1):
        plan.folders.append(rng.choice([plan.root, *plan.folders]) / f"d{number}")
    for number in range(1, rng.randint(0, 5) + 1):
        parent = rng.choice([plan.root, *plan.folders])
        text = "".join(rng.choice(PIECES) for _ in range(rng.randint(0, 6)))
        plan.files.append((parent / f"f{number}.toml", text))


def _random_faults(rng: random.Random, plan: Plan, steps: list[Step]) -> None:
    """Picks the fault of a call, and the removals that are denied."""
    if not steps:
        return
    if rng.random() >= 0.25:
        index = rng.randrange(len(steps))
        options = [*EFFECTS, "write"] if steps[index][0] == "open" else list(EFFECTS)
        plan.fault = (index, rng.choice(options))
    if rng.random() < 1 / 3:
        count = rng.choice([1, 2])
        plan.denied = set(rng.sample(range(len(steps)), min(count, len(steps))))


def _rules(plan: Plan, steps: list[Step]) -> list[Rule]:
    """Makes the rules of the harness from the fault and the denied removals."""
    rules = []
    if plan.fault is not None:
        index, effect = plan.fault
        kind, path = steps[index]
        if effect == "write":
            rules.append(rule("write", path, NO_SPACE))
        elif effect == "race":
            rules.append(rule(kind, path, how="race"))
        elif effect == "after CTRL_C":
            rules.append(rule(kind, path, CTRL_C, "after"))
        else:
            rules.append(rule(kind, path, {"DENIED": DENIED, "IO": IO, "CTRL_C": CTRL_C}[effect]))
    for index in sorted(plan.denied):
        kind, path = steps[index]
        rules.append(rule("rmdir" if kind == "mkdir" else "unlink", path, DENIED))
    return rules


@dataclass
class Expected:
    """What the steps of 3.2 and the rules give for one call."""

    calls: list[str]
    outcome: str
    problem: tuple[str, Msg] | None
    left: list[Path]
    present: dict[Path, Entry]


def _fault_at(plan: Plan, steps: list[Step], present: dict[Path, Entry]) -> tuple[str, str | None]:
    """Applies the fault of the call to its step: gives the outcome, and the effect or ``None``.

    The entries that the fault leaves are added to ``present``. A ``write`` fault leaves the
    file that the call opened, with the first half of its text.
    """
    assert plan.fault is not None
    index, effect = plan.fault
    kind, path = steps[index]
    if effect == "race":
        present[path] = FOLDER if kind == "mkdir" else file_of(b"mine\n")
    elif effect == "after CTRL_C":
        present[path] = FOLDER if kind == "mkdir" else file_of(b"")
    elif effect == "write":
        text = dict(plan.files)[path]
        present[path] = file_of(text[: len(text) // 2].encode("utf-8"))
    return ("interrupted" if "CTRL_C" in effect else "failed"), effect


def _remove(plan: Plan, steps: list[Step], created: list[int], expected: Expected) -> None:
    """Adds the removal of the created steps to the record, and gives ``left`` and ``present``."""
    for index in reversed(created):
        kind, path = steps[index]
        expected.calls.append(f"{'rmdir' if kind == 'mkdir' else 'unlink'} {rel(plan.base, path)}")
        full = kind == "mkdir" and any(other.parent == path for other in expected.present)
        if index in plan.denied or full:
            expected.left.append(path)
        else:
            del expected.present[path]


def _expected(plan: Plan, steps: list[Step]) -> Expected:
    """Computes the record, the result, and the entries of a call from the steps and the rules."""
    expected = Expected([], "created", None, [], {})
    texts = dict(plan.files)
    created: list[int] = []
    for index, (kind, path) in enumerate(steps):
        expected.calls.append(f"{kind} {rel(plan.base, path)}")
        if plan.fault is not None and plan.fault[0] == index:
            expected.outcome, effect = _fault_at(plan, steps, expected.present)
            if effect in ROWS:
                row = ROWS[effect][0 if kind == "mkdir" else 1]
                expected.problem = (problem_file(plan.root, path), row)
            if effect == "write":
                created.append(index)
            break
        created.append(index)
        if kind == "mkdir":
            expected.present[path] = FOLDER
        else:
            expected.present[path] = file_of(texts[path].encode("utf-8"))
    if expected.outcome != "created":
        _remove(plan, steps, created, expected)
    return expected


def _run_one(plan: Plan, steps: list[Step]) -> Creation | None:
    """Runs the call inside the harness, and gives its result, or ``None`` for Ctrl+C."""
    expected = _expected(plan, steps)
    start = tree(plan.base)
    result = None
    with faults(plan.base, *_rules(plan, steps)) as seen:
        folder = DataFolder(plan.root)
        if expected.outcome == "interrupted":
            with pytest.raises(KeyboardInterrupt):
                create_data_folder(folder, plan.folders, plan.files)
        else:
            result = create_data_folder(folder, plan.folders, plan.files)
    assert seen.calls == expected.calls
    assert seen.listings == ([rel(plan.base, plan.root)] if plan.start == 3 else [])
    after = start | {rel(plan.base, path): entry for path, entry in expected.present.items()}
    assert tree(plan.base) == after
    _check_result(result, expected)
    return result


def _check_result(result: Creation | None, expected: Expected) -> None:
    """Checks the result of a call against the expected one."""
    if expected.outcome == "created":
        assert result == Creation(CreationOutcome.CREATED)
    elif expected.outcome == "failed":
        assert expected.problem is not None
        file, msg = expected.problem
        assert_failed(result, file, msg, expected.left)
    else:
        assert result is None


def test_f08_t28_random_calls_create_everything_or_leave_the_disk_as_it_was(
    tmp_path: Path,
) -> None:
    """200 calls with a fault at a random step: the record, the result, and the tree follow 3.2."""
    rng = random.Random(20261113)  # noqa: S311 - a fixed seed, no security
    seen: Counter[str] = Counter()
    for number in range(200):
        base = tmp_path / f"c{number}"
        base.mkdir()
        plan = Plan(base, rng.randrange(4), [], [])
        _prepare(plan)
        _random_items(rng, plan)
        steps = make_steps(plan.root, plan.folders, plan.files)
        _random_faults(rng, plan, steps)
        result = _run_one(plan, steps)
        seen["interrupted" if result is None else result.outcome.value] += 1
        seen["left"] += bool(result is not None and result.left)
    assert seen["created"] > 0
    assert seen["failed"] > 0
    assert seen["interrupted"] > 0
    assert seen["left"] > 0
