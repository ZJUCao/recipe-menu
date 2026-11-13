"""Tests of F08 for the removal of create_data_folder: a failure, Ctrl+C, and a skipped removal.

These are T10 to T13.
"""

from pathlib import Path

import pytest

from f08_support import (
    BUG,
    CTRL_C,
    DENIED,
    FOLDER,
    IO,
    NO_SPACE,
    Effect,
    Rule,
    assert_failed,
    faults,
    file_of,
    items,
    make_steps,
    problem_file,
    record_of,
    rel,
    rule,
    tree,
)
from f08_texts import (
    FILE_WRITE_DENIED,
    FOLDER_CREATE_DENIED,
    file_error,
)
from recipe_menu.datafile import DataFolder, create_data_folder

PANTRY_ERROR = file_error("No space left on device")


def _setup(tmp_path: Path, name: str, above: bool = True) -> tuple[Path, Path]:
    """Makes ``base``, and gives it with R: ``a/recipe-menu`` missing, or ``recipe-menu`` empty."""
    base = tmp_path / name
    base.mkdir()
    root = base / "a" / "recipe-menu" if above else base / "recipe-menu"
    if not above:
        root.mkdir()
    return base, root


def _denied_at(steps: list[tuple[str, Path]], k: int) -> Rule:
    """Gives the rule ``DENIED`` at step ``k``, counted from 1."""
    kind, path = steps[k - 1]
    return rule(kind, path, DENIED)


def test_f08_t10_a_failure_at_any_step_removes_each_earlier_step_and_nothing_else(
    tmp_path: Path,
) -> None:
    """DENIED at each step: 9 steps with `a` missing, and 7 steps in an empty R."""
    for above, count in ((True, 9), (False, 7)):
        for k in range(1, count + 1):
            base, root = _setup(tmp_path, f"t{int(above)}_{k}", above)
            folders, files = items(root)
            steps = make_steps(root, folders, files)
            assert len(steps) == count
            with faults(base, _denied_at(steps, k)) as seen:
                creation = create_data_folder(DataFolder(root), folders, files)
            kind, path = steps[k - 1]
            msg = FOLDER_CREATE_DENIED if kind == "mkdir" else FILE_WRITE_DENIED
            assert_failed(creation, problem_file(root, path), msg)
            assert seen.calls == record_of(base, steps, k, k - 1), (above, k)
            assert tree(base) == ({} if above else {"recipe-menu": FOLDER}), (above, k)


def _t11_case(
    tmp_path: Path, number: int, found: tuple[str, str, Effect], error: type | None
) -> None:
    """Runs one case of F08-T11: a rule of a kind at a path of R, and the error to expect."""
    base, root = _setup(tmp_path, f"t{number}")
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    kind, name, effect = found
    with faults(base, rule(kind, root / name, effect)) as seen:
        if error is None:
            creation = create_data_folder(DataFolder(root), folders, files)
        else:
            with pytest.raises(error):
                create_data_folder(DataFolder(root), folders, files)
    if number == 4:
        assert seen.calls == record_of(base, steps, 4, 3)
    else:
        assert seen.calls == record_of(base, steps, 8, 8)
        assert len(seen.halves) == 1
        assert seen.halves[0].closed
    if error is None:
        assert_failed(creation, "pantry.toml", PANTRY_ERROR)
    assert not (base / "a").exists()


def test_f08_t11_a_half_written_file_and_any_other_exception_run_the_removal(
    tmp_path: Path,
) -> None:
    """A write that fails halfway gives FAILED, and a bug or Ctrl+C goes on after the removal."""
    _t11_case(tmp_path, 1, ("write", "pantry.toml", NO_SPACE), None)
    _t11_case(tmp_path, 2, ("write", "pantry.toml", BUG), RuntimeError)
    _t11_case(tmp_path, 3, ("write", "pantry.toml", CTRL_C), KeyboardInterrupt)
    _t11_case(tmp_path, 4, ("mkdir", "menus", BUG), RuntimeError)


def _t12_step(tmp_path: Path, k: int) -> None:
    """Runs case 1 of F08-T12 for step ``k``."""
    base, root = _setup(tmp_path, f"t1_{k}")
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    kind, path = steps[k - 1]
    with faults(base, rule(kind, path, CTRL_C)) as seen, pytest.raises(KeyboardInterrupt):
        create_data_folder(DataFolder(root), folders, files)
    assert seen.calls == record_of(base, steps, k, k - 1), k
    assert tree(base) == {}, k


def _t12_killed(tmp_path: Path) -> None:
    """Runs cases 2 to 4 of F08-T12: the three cases that act like a killed process."""
    base, root = _setup(tmp_path, "t2")
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    found = rule("open", root / "pantry.toml", CTRL_C, "after")
    with faults(base, found) as seen, pytest.raises(KeyboardInterrupt):
        create_data_folder(DataFolder(root), folders, files)
    assert seen.calls == record_of(base, steps, 8, 7)
    assert tree(root) == {"pantry.toml": file_of(b"")}

    base, root = _setup(tmp_path, "t3")
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    rules = (
        rule("open", root / "catalog.toml", CTRL_C),
        rule("unlink", root / "settings.toml", CTRL_C),
    )
    with faults(base, *rules) as seen, pytest.raises(KeyboardInterrupt):
        create_data_folder(DataFolder(root), folders, files)
    assert seen.calls == [*record_of(base, steps, 7, 0), f"unlink {rel(base, root)}/settings.toml"]
    kept = {"recipes": FOLDER, "menus": FOLDER, "shopping": FOLDER}
    assert tree(root) == {"settings.toml": file_of(b"s\n")} | kept

    base, root = _setup(tmp_path, "t4")
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    found = rule("mkdir", root / "menus", CTRL_C, "after")
    with faults(base, found) as seen, pytest.raises(KeyboardInterrupt):
        create_data_folder(DataFolder(root), folders, files)
    assert seen.calls == record_of(base, steps, 4, 3)
    assert tree(root) == {"menus": FOLDER}


def test_f08_t12_ctrl_c_at_any_step_runs_the_removal_and_goes_on(tmp_path: Path) -> None:
    """KeyboardInterrupt leaves the call after the removal, except in the killed cases."""
    for k in range(1, 10):
        _t12_step(tmp_path, k)
    _t12_killed(tmp_path)


def _t13_case(tmp_path: Path, number: int) -> None:
    """Runs case ``number`` of F08-T13."""
    above = number in (1, 4)
    base, root = _setup(tmp_path, f"t{number}", above)
    if number == 3:
        root.rmdir()
    folders, files = items(root)
    steps = make_steps(root, folders, files)
    settings, pantry = root / "settings.toml", root / "pantry.toml"
    recipe = root / "recipes" / "tomato-egg.toml"
    if number == 3:
        rules = [rule("open", settings, IO), rule("rmdir", root / "menus", DENIED)]
        problem, msg, attempted, created = "settings.toml", file_error("Input/output error"), 5, 4
        left, kept = (root / "menus", root), {"menus": FOLDER}
    else:
        rules = [rule("open", recipe, DENIED), rule("unlink", settings, DENIED)]
        problem, msg, attempted, created = "recipes/tomato-egg.toml", FILE_WRITE_DENIED, 9, 8
        left, kept = (settings, root, base / "a"), {"settings.toml": file_of(b"s\n")}
        if number == 2:
            attempted, created, left = 7, 6, (settings,)
        if number == 4:
            rules.append(rule("unlink", pantry, DENIED))
            left, kept = (pantry, *left), kept | {"pantry.toml": file_of(b"p\n")}
    with faults(base, *rules) as seen:
        creation = create_data_folder(DataFolder(root), folders, files)
    assert_failed(creation, problem, msg, left)
    assert seen.calls == record_of(base, steps, attempted, created), number
    assert tree(root) == kept, number


def test_f08_t13_a_failed_removal_is_skipped_and_left_holds_every_path_that_stayed(
    tmp_path: Path,
) -> None:
    """Four calls with a denied removal: left lists each path, in the order of the removal."""
    for number in (1, 2, 3, 4):
        _t13_case(tmp_path, number)
