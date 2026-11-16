"""Tests of F13 for shop when the save fails: the harness, Ctrl+C, real failures (T19-T21)."""

import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from f05_support import make_home
from f05_texts import Result
from f08_support import (
    CTRL_C,
    DENIED,
    IO,
    NO_SPACE,
    Effect,
    Rule,
    call_main,
    dangling_link,
    rule,
)
from f08_texts import FILE_WRITE_DENIED, FOLDER_CREATE_DENIED, file_error, folder_error
from f09_support import at, made
from f09_texts import err, out
from f11_support import first_half, held
from f13_support import (
    TEMP_47,
    W47,
    empty_shopping,
    held_open,
    move_message,
    old_list,
    pristine,
    shop_faults,
    shopping_as_file,
)
from f13_texts import (
    FILE_47,
    PROTOTYPE_FILE,
    parent,
    shop_47,
    shop_47_zh,
    shop_fail,
    shop_fail_zh,
    shop_left,
    shop_left_zh,
)
from recipe_menu.datafile import DataFolder

NO_SPACE_MSG = file_error("No space left on device")
IO_MSG = file_error("Input/output error")
OLD = b"old\n"
UNLINK = f"unlink {TEMP_47}"
OPEN = f"open {TEMP_47}"
MOVE = f"move {TEMP_47} shopping/2026-W47.md"
EN = ["2026-W47"]
ZH = ["2026-W47", "--lang", "zh"]


def _paths(root: Path) -> tuple[Path, Path]:
    """Gives P and T of 2026-W47 in a data folder."""
    path = root / "shopping" / "2026-W47.md"
    return path, path.with_name("2026-W47.md.tmp")


def _run_lines(
    home: Path, root: Path, rules: Sequence[Rule], *lines: list[str]
) -> tuple[list[Result], list[str]]:
    """Runs ``shop`` once for each list of arguments inside one harness.

    Returns:
        The results in order, and the record of the last call.
    """
    done = []
    record: list[str] = []
    with shop_faults(root, *rules) as state:
        for argv in lines:
            before = len(state.calls)
            done.append(at(home, root, "shop", *argv))
            record = state.calls[before:]
    return done, record


def _entries(root: Path) -> list[str]:
    """Gives the sorted names in ``shopping/``."""
    return sorted(entry.name for entry in (root / "shopping").iterdir())


class Failure(NamedTuple):
    """An input of F13-T19.

    Attributes:
        old: Whether an old list is in place.
        kind: The kind of the rule, such as ``open``.
        target: ``"shopping"`` or ``"temp"``, the path that the rule names.
        effect: The exception that the rule raises.
        message: The problem's text in English and in Chinese.
        lines: The arguments of each run of ``shop``.
    """

    old: bool
    kind: str
    target: str
    effect: Effect
    message: tuple[str, str]
    lines: tuple[list[str], ...]


CASES_19 = {
    1: Failure(False, "mkdir", "shopping", DENIED, FOLDER_CREATE_DENIED, (EN, ZH)),
    2: Failure(False, "mkdir", "shopping", IO, folder_error("Input/output error"), (EN,)),
    3: Failure(True, "open", "temp", DENIED, FILE_WRITE_DENIED, (EN, ZH)),
    4: Failure(True, "open", "temp", IO, IO_MSG, (EN,)),
    5: Failure(True, "write", "temp", NO_SPACE, NO_SPACE_MSG, (EN,)),
    8: Failure(True, "close", "temp", IO, IO_MSG, (EN,)),
    9: Failure(True, "move", "temp", DENIED, FILE_WRITE_DENIED, (EN, ZH)),
}


def test_f13_t19_a_failed_save_is_three_lines_on_the_error_stream(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Ten inputs: the full path, the problem, the last line, the old file, and the next run."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    for number, case in CASES_19.items():
        root = made(source, tmp_path, f"in{number}", *([old_list] if case.old else []))
        path, temp = _paths(root)
        target = root / "shopping" if case.target == "shopping" else temp
        results, record = _run_lines(
            home, root, [rule(case.kind, target, case.effect)], *case.lines
        )
        assert results[0] == err(1, shop_fail(path, case.message)), number
        if len(results) == 2:
            assert results[1] == err(1, shop_fail_zh(path, case.message)), number
        if number == 5:
            assert record[-3:] == [UNLINK, OPEN, UNLINK], number
        if number == 9:
            assert record[-2:] == [MOVE, UNLINK], number
        assert held(path) == (OLD if case.old else None), number
        assert (root / "shopping").exists() == case.old, number
        assert not [entry for entry in root.rglob("*") if entry.name.endswith(".tmp")], number
    _check_left(home, source, tmp_path)
    _check_folder_stays(home, source, tmp_path)


def _check_left(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 6 and 7 of F13-T19: the temporary file cannot be removed, and the line names it."""
    root = made(source, tmp_path, "in6", old_list)
    path, temp = _paths(root)
    rules = [rule("write", temp, NO_SPACE), rule("unlink", temp, DENIED, "later")]
    results, _ = _run_lines(home, root, rules, ["next"])
    assert results == [err(1, shop_left(path, NO_SPACE_MSG, temp))]
    assert temp.read_bytes() == first_half(FILE_47)
    assert held(path) == OLD
    assert at(home, root, "shop", "next") == out(shop_47(path))
    assert (path.read_bytes(), _entries(root)) == (FILE_47, ["2026-W47.md"])
    root = made(source, tmp_path, "in7", old_list)
    path, temp = _paths(root)
    rules = [rule("write", temp, NO_SPACE), rule("unlink", temp, DENIED, "later")]
    results, _ = _run_lines(home, root, rules, ZH)
    assert results == [err(1, shop_left_zh(path, NO_SPACE_MSG, temp))]
    assert held(path) == OLD


def _check_folder_stays(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Input 10 of F13-T19: a folder that ``shop`` made stays when the write fails."""
    root = made(source, tmp_path, "in10")
    path, temp = _paths(root)
    results, _ = _run_lines(home, root, [rule("write", temp, NO_SPACE)], EN)
    assert results == [err(1, shop_fail(path, NO_SPACE_MSG))]
    assert (root / "shopping").is_dir()
    assert _entries(root) == []
    assert at(home, root, "shop", "2026-W47") == out(shop_47(path))
    assert path.read_bytes() == FILE_47


class Stop(NamedTuple):
    """An input of F13-T20: the rules, the line, and the end of the record the case expects."""

    rules: tuple[tuple[str, Effect, str], ...]
    line: list[str]
    record: list[str]


CASES_20 = {
    1: Stop((("write", CTRL_C, "raise"),), EN, [UNLINK, OPEN, UNLINK]),
    2: Stop((("move", CTRL_C, "raise"),), EN, [OPEN, MOVE, UNLINK]),
    3: Stop((("open", CTRL_C, "after"),), EN, [UNLINK, OPEN]),
    4: Stop((("write", CTRL_C, "raise"), ("unlink", DENIED, "later")), ZH, [UNLINK, OPEN, UNLINK]),
}


def test_f13_t20_ctrl_c_during_the_save_exits_with_130_and_keeps_the_old_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four inputs: ``temp`` is removed, or it stays empty after an open that was cut."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    for number, case in CASES_20.items():
        root = made(source, tmp_path, f"in{number}", old_list)
        path, temp = _paths(root)
        rules = [rule(kind, temp, effect, how) for kind, effect, how in case.rules]
        with shop_faults(root, *rules) as state:
            result = call_main(home, ["shop", *case.line, "--data", str(root)])
        assert result == (130, "", ""), number
        assert state.calls[-len(case.record) :] == case.record, number
        assert held(path) == OLD, number
        if number == 3:
            assert held(temp) == b"", number
        elif number == 4:
            half = PROTOTYPE_FILE.decode("utf-8")
            assert held(temp) == half[: len(half) // 2].encode("utf-8")
        else:
            assert not temp.exists(), number
        if number in (3, 4):
            with shop_faults(root) as again:
                shown = call_main(home, ["shop", *case.line, "--data", str(root)])
            expected = shop_47(path) if number == 3 else shop_47_zh(path)
            assert shown == out(expected), number
            assert again.calls[-3:] == W47, number
            assert not temp.exists()
            assert path.read_bytes() == (FILE_47 if number == 3 else PROTOTYPE_FILE)


def _check_not_a_folder(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 1 and 2 of F13-T21: a file and a dangling link at ``shopping``."""
    root = made(source, tmp_path, "in1", shopping_as_file)
    path, _ = _paths(root)
    assert at(home, root, "shop", "2026-W47") == err(1, shop_fail(path, parent("shopping")))
    assert at(home, root, "shop", *ZH) == err(1, shop_fail_zh(path, parent("shopping")))
    assert (root / "shopping").read_bytes() == b"x\n"
    (root / "shopping").unlink()
    assert at(home, root, "shop", "2026-W47") == out(shop_47(path))
    assert (path.read_bytes(), _entries(root)) == (FILE_47, ["2026-W47.md"])
    root = made(source, tmp_path, "in2")
    dangling_link(root / "shopping")
    path, _ = _paths(root)
    assert at(home, root, "shop", "2026-W47") == err(1, shop_fail(path, parent("shopping")))
    link = root / "shopping"
    assert link.is_symlink() or os.path.isjunction(link)


def _check_file_system(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 3 and 4 of F13-T21: a folder at the list file's path, and a file held open."""
    root = made(source, tmp_path, "in3", empty_shopping)
    path, temp = _paths(root)
    path.mkdir()
    messages = tmp_path / "messages"
    messages.mkdir()
    message = move_message(messages)
    assert at(home, root, "shop", "2026-W47") == err(1, shop_fail(path, message))
    assert path.is_dir()
    assert not temp.exists()
    path.rmdir()
    assert at(home, root, "shop", "2026-W47") == out(shop_47(path))
    assert path.read_bytes() == FILE_47
    root = made(source, tmp_path, "in4", old_list)
    path, temp = _paths(root)
    with held_open(path):
        shown = at(home, root, "shop", "2026-W47")
    if sys.platform == "win32":
        assert shown == err(1, shop_fail(path, FILE_WRITE_DENIED))
        assert (path.read_bytes(), temp.exists()) == (OLD, False)
    else:
        assert shown == out(shop_47(path))
        assert path.read_bytes() == FILE_47
    assert at(home, root, "shop", "2026-W47") == out(shop_47(path))
    assert (path.read_bytes(), _entries(root)) == (FILE_47, ["2026-W47.md"])


def test_f13_t21_real_failures_of_the_file_system_give_the_failure_lines(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A file at ``shopping``, a dangling link, a folder at the list file, and a held file."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_not_a_folder(home, source, tmp_path)
    _check_file_system(home, source, tmp_path)
