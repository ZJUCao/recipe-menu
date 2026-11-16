"""Tests of F13 for replace_file when the disk fails (T07 to T10)."""

from pathlib import Path
from typing import NamedTuple

import pytest

from f03_support import put_bytes
from f05_support import unreadable_name
from f08_support import (
    BUG,
    CTRL_C,
    DENIED,
    EMPTY_IO,
    IO,
    NO_SPACE,
    Effect,
    Rule,
    rule,
    system_message,
    tree,
)
from f08_texts import FILE_WRITE_DENIED, FOLDER_CREATE_DENIED, file_error, folder_error
from f11_support import assert_failed, held
from f13_support import EXISTS, move_message, new_shop, shop_faults
from recipe_menu.datafile import DataFolder, FileCreation, FileOutcome, replace_file

S = "recipe-menu/shopping"
Q = f"{S}/2026-W47.md"
T = f"{Q}.tmp"
FILE = "shopping/2026-W47.md"
OLD = b"old\n"
FULL = "0123456789\n"
HALF = b"01234"
CREATED = FileCreation(FileOutcome.CREATED)
WRITE = [f"unlink {T}", f"open {T}", f"unlink {T}"]
MOVE = [f"unlink {T}", f"open {T}", f"move {T} {Q}", f"unlink {T}"]
NO_SPACE_MSG = file_error("No space left on device")
IO_MSG = file_error("Input/output error")


def _folder_input(
    tmp_path: Path, number: int
) -> tuple[Path, DataFolder, list[Rule], Path, tuple[str, str | None]]:
    """Makes input ``number`` of F13-T07 and gives ``base``, ``F``, the rules, the path, the result.

    The result is the problem's file and its message.
    """
    base, folder = new_shop(tmp_path, f"t07-{number}")
    effects: dict[int, Effect] = {1: DENIED, 2: IO, 3: EXISTS, 4: OSError, 5: TimeoutError}
    effects |= {6: EMPTY_IO, 9: CTRL_C}
    rules = [rule("mkdir", folder.shopping, effects[number])] if number in effects else []
    messages = {
        1: FOLDER_CREATE_DENIED,
        2: folder_error("Input/output error"),
        3: folder_error("File exists"),
        4: folder_error("OSError"),
        5: folder_error("TimeoutError"),
        6: folder_error("OSError"),
    }
    path, result = folder.shopping_file("2026-W47"), (FILE, messages.get(number))
    if number == 7:
        folder.root.rmdir()
        result = (FILE, system_message("folder", folder.shopping))
    if number == 8:
        name = unreadable_name(base).name
        path = folder.root / name / "x.md"
        result = (f"{name}/x.md", system_message("folder", folder.root / name))
    return base, folder, rules, path, result


def test_f13_t07_a_folder_that_cannot_be_made_gives_the_problem_of_the_folder_rows(
    tmp_path: Path,
) -> None:
    """Nine inputs: the first two rows of the error table, a probe that fails, and Ctrl+C."""
    for number in range(1, 10):
        base, folder, rules, path, (file, message) = _folder_input(tmp_path, number)
        before = tree(base)
        if number == 9:
            with shop_faults(base, *rules) as state, pytest.raises(KeyboardInterrupt):
                replace_file(folder, path, "x")
        else:
            with shop_faults(base, *rules) as state:
                creation = replace_file(folder, path, "x")
            assert_failed(creation, file, message)
        made = f"mkdir recipe-menu/{path.parent.name}" if number == 8 else f"mkdir {S}"
        assert state.calls == [made], number
        assert tree(base) == before, number


class Open(NamedTuple):
    """An input of F13-T08: the rule on ``temp``, and the message of the problem."""

    kind: str
    effect: Effect | None
    how: str
    message: tuple[str, str]


CASES_08 = {
    1: Open("unlink", DENIED, "raise", FILE_WRITE_DENIED),
    2: Open("unlink", IO, "raise", IO_MSG),
    3: Open("open", DENIED, "raise", FILE_WRITE_DENIED),
    4: Open("open", IO, "raise", IO_MSG),
    5: Open("open", EXISTS, "raise", file_error("File exists")),
    6: Open("open", None, "race", file_error("File exists")),
    7: Open("open", TimeoutError, "raise", file_error("TimeoutError")),
    8: Open("open", EMPTY_IO, "raise", file_error("OSError")),
}


def test_f13_t08_a_failure_before_temp_exists_removes_nothing(tmp_path: Path) -> None:
    """Eight inputs: the rows of steps 3 to 5, with ``FileExistsError`` as ``FILE_WRITE_ERROR``."""
    for number, case in CASES_08.items():
        base, folder = new_shop(tmp_path, f"t08-{number}")
        path, temp = folder.shopping_file("2026-W47"), folder.shopping / "2026-W47.md.tmp"
        put_bytes(path, OLD)
        if number <= 2:
            put_bytes(temp, b"half\n")
        with shop_faults(base, rule(case.kind, temp, case.effect, case.how)) as state:
            creation = replace_file(folder, path, "new\n")
        assert_failed(creation, FILE, case.message)
        assert state.calls == ([f"unlink {T}"] if number <= 2 else [f"unlink {T}", f"open {T}"])
        expected = {2: b"half\n", 1: b"half\n", 6: b"mine\n"}.get(number)
        assert held(temp) == expected, number
        assert held(path) == OLD, number
        names = sorted(entry.name for entry in folder.shopping.iterdir())
        assert names == (
            ["2026-W47.md"] if expected is None else ["2026-W47.md", "2026-W47.md.tmp"]
        )


class After(NamedTuple):
    """An input of F13-T09.

    Attributes:
        rules: The rules as kind, effect, and how.
        text: The text to write.
        message: The problem's text, or ``None`` for the message of the move.
        record: The calls that the harness records.
        left: Whether the temporary file is reported as left.
        temp: The bytes of the temporary file afterwards, or ``None`` when it is gone.
        no_shopping: Whether ``F.shopping`` is empty and has no old file.
    """

    rules: tuple[tuple[str, Effect, str], ...]
    text: str
    message: tuple[str, str] | None
    record: list[str]
    left: bool = False
    temp: bytes | None = None
    no_shopping: bool = False


CASES_09 = {
    1: After((("write", NO_SPACE, "raise"),), FULL, NO_SPACE_MSG, WRITE),
    2: After((("write", DENIED, "raise"),), FULL, FILE_WRITE_DENIED, WRITE),
    3: After(
        (("write", IO, "raise"), ("unlink", DENIED, "later")), FULL, IO_MSG, WRITE, True, HALF
    ),
    4: After((("write", NO_SPACE, "raise"),), "", NO_SPACE_MSG, WRITE),
    5: After((("close", NO_SPACE, "raise"),), FULL, NO_SPACE_MSG, WRITE),
    6: After(
        (("close", DENIED, "raise"), ("unlink", IO, "later")),
        FULL,
        FILE_WRITE_DENIED,
        WRITE,
        True,
        FULL.encode(),
    ),
    7: After((("move", DENIED, "raise"),), FULL, FILE_WRITE_DENIED, MOVE),
    8: After((("move", IO, "raise"),), FULL, IO_MSG, MOVE),
    9: After((("move", OSError, "raise"),), FULL, file_error("OSError"), MOVE),
    10: After(
        (("move", DENIED, "raise"), ("unlink", DENIED, "later")),
        FULL,
        FILE_WRITE_DENIED,
        MOVE,
        True,
        FULL.encode(),
    ),
    11: After((), FULL, None, MOVE),
    12: After(
        (("write", NO_SPACE, "raise"),),
        FULL,
        NO_SPACE_MSG,
        [f"mkdir {S}", *WRITE],
        False,
        None,
        True,
    ),
    13: After(
        (("move", DENIED, "raise"),),
        FULL,
        FILE_WRITE_DENIED,
        [f"mkdir {S}", *MOVE],
        False,
        None,
        True,
    ),
}


def test_f13_t09_a_failure_after_the_open_removes_temp_and_keeps_the_old_file(
    tmp_path: Path,
) -> None:
    """Thirteen inputs: a write, a close, or a move that fails, and a removal that fails too."""
    for number, case in CASES_09.items():
        base, folder = new_shop(tmp_path, f"t09-{number}")
        path, temp = folder.shopping_file("2026-W47"), folder.shopping / "2026-W47.md.tmp"
        if number == 11:
            path.mkdir(parents=True)
        elif not case.no_shopping:
            put_bytes(path, OLD)
        message = case.message or move_message(base)
        rules = [rule(kind, temp, effect, how) for kind, effect, how in case.rules]
        with shop_faults(base, *rules) as state:
            creation = replace_file(folder, path, case.text)
        assert_failed(creation, FILE, message, (temp,) if case.left else ())
        assert state.calls == case.record, number
        assert held(temp) == case.temp, number
        if number == 11:
            assert path.is_dir()
            assert list(path.iterdir()) == []
        elif case.no_shopping:
            assert list(folder.shopping.iterdir()) == []
        else:
            assert held(path) == OLD, number


class Stop(NamedTuple):
    """An input of F13-T10.

    Attributes:
        rules: The rules as kind, effect, and how.
        error: The exception that must come out of ``replace_file``.
        record: The calls that the harness records.
        temp: The bytes of the temporary file afterwards, or ``None`` when it is gone.
    """

    rules: tuple[tuple[str, Effect, str], ...]
    error: type[BaseException]
    record: list[str]
    temp: bytes | None = None


CASES_10 = {
    1: Stop((("write", BUG, "raise"),), RuntimeError, WRITE),
    2: Stop((("write", CTRL_C, "raise"),), KeyboardInterrupt, WRITE),
    3: Stop((("close", CTRL_C, "raise"),), KeyboardInterrupt, WRITE),
    4: Stop((("move", CTRL_C, "raise"),), KeyboardInterrupt, MOVE),
    5: Stop(
        (("write", CTRL_C, "raise"), ("unlink", DENIED, "later")), KeyboardInterrupt, WRITE, HALF
    ),
    6: Stop(
        (("write", CTRL_C, "raise"), ("unlink", CTRL_C, "later")), KeyboardInterrupt, WRITE, HALF
    ),
    7: Stop((("open", CTRL_C, "after"),), KeyboardInterrupt, WRITE[:2], b""),
    9: Stop((("unlink", CTRL_C, "raise"),), KeyboardInterrupt, WRITE[:1], b"half\n"),
}


def test_f13_t10_an_interruption_or_a_bug_removes_temp_and_goes_on(tmp_path: Path) -> None:
    """Nine inputs: the ``finally`` block, an open that was cut, and the rerun."""
    for number, case in CASES_10.items():
        base, folder = new_shop(tmp_path, f"t10-{number}")
        path, temp = folder.shopping_file("2026-W47"), folder.shopping / "2026-W47.md.tmp"
        put_bytes(path, OLD)
        if number == 9:
            put_bytes(temp, b"half\n")
        rules = [rule(kind, temp, effect, how) for kind, effect, how in case.rules]
        with shop_faults(base, *rules) as state, pytest.raises(case.error):
            replace_file(folder, path, FULL)
        assert state.calls == case.record, number
        assert held(temp) == case.temp, number
        assert held(path) == OLD, number
        if number == 7:
            with shop_faults(base) as again:
                creation = replace_file(folder, path, "# 1\n")
            assert creation == CREATED
            assert again.calls == [f"unlink {T}", f"open {T}", f"move {T} {Q}"]
            assert held(temp) is None
            assert held(path) == b"# 1\n"
