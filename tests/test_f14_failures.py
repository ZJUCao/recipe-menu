"""Tests of F14 for a failed save: the harness, Ctrl+C, and real failures of the system (T20)."""

import sys
from pathlib import Path

from f03_support import put_bytes
from f05_support import copy_example, make_home
from f08_support import CTRL_C, DENIED, IO, NO_SPACE, Effect, call_main, rule
from f08_texts import FILE_WRITE_DENIED, file_error
from f09_support import made
from f09_texts import err, out
from f11_support import first_half
from f13_support import held_open, pristine, shop_faults
from f14_support import IN_ZH, W47, save_of, suggest, w47_filled, week_line
from f14_texts import failed, failed_zh, left_behind, left_behind_zh, some
from recipe_menu.datafile import DataFolder

NO_SPACE_MSG = file_error("No space left on device")
IO_MSG = file_error("Input/output error")
UNLINK_T, OPEN_T, MOVE_T = save_of(W47)
# The inputs 1, 2, 3, 6, and 7: the kind of the rule, its effect, the message, and the languages.
SIMPLE: dict[int, tuple[str, Effect, tuple[str, str], tuple[tuple[str, ...], ...]]] = {
    1: ("open", DENIED, FILE_WRITE_DENIED, ((), IN_ZH)),
    2: ("open", IO, IO_MSG, ((),)),
    3: ("write", NO_SPACE, NO_SPACE_MSG, ((),)),
    6: ("close", IO, IO_MSG, ((),)),
    7: ("move", DENIED, FILE_WRITE_DENIED, ((),)),
}


def _paths(root: Path) -> tuple[Path, Path]:
    """Gives P, the menu file of 2026-W47, and T, its temporary file."""
    path = root / "menus" / "2026-W47.toml"
    return path, path.with_name("2026-W47.toml.tmp")


def _entries(root: Path) -> list[str]:
    """Gives the sorted names in ``menus/``."""
    return sorted(entry.name for entry in (root / "menus").iterdir())


def _check_simple(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 1, 2, 3, 6, and 7: a rule on the temporary file gives three lines, and no file."""
    for number, (kind, effect, message, languages) in SIMPLE.items():
        root = made(source, tmp_path, f"in{number}")
        path, temp = _paths(root)
        before = path.read_bytes()
        for rest in languages:
            with shop_faults(root, rule(kind, temp, effect)) as state:
                result = suggest(home, root, *week_line(W47, *rest))
            lines = failed_zh(W47, message) if rest else failed(W47, message)
            assert result == err(1, lines), (number, rest)
            if number == 3:
                assert state.calls[-3:] == [UNLINK_T, OPEN_T, UNLINK_T]
            if number == 7:
                assert state.calls[-2:] == [MOVE_T, UNLINK_T]
            assert path.read_bytes() == before, number
            assert _entries(root) == ["2026-W47.toml"], number


def _check_left(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 4 and 5: the temporary file cannot be removed, and the last line names it."""
    lines = (("One Drive", ("next",)), ("Two Drive", (W47, *IN_ZH)))
    for index, (parent, rest) in enumerate(lines):
        root = copy_example(source, tmp_path / parent / "菜谱")
        path, temp = _paths(root)
        before = path.read_bytes()
        rules = [rule("write", temp, NO_SPACE), rule("unlink", temp, DENIED, "later")]
        with shop_faults(root, *rules):
            result = suggest(home, root, "menu", "suggest", *rest)
        build = left_behind_zh if "--lang" in rest else left_behind
        assert result == err(1, build(W47, NO_SPACE_MSG, temp)), index
        assert path.read_bytes() == before
        if index == 0:
            assert temp.read_bytes() == first_half(w47_filled())
            assert suggest(home, root, *week_line(W47)) == out(some(W47, 1, 10, 4, "left"))
            assert path.read_bytes() == w47_filled()
            assert _entries(root) == ["2026-W47.toml"]


def _check_ctrl_c(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 8 and 9: Ctrl+C at the move and at the read of a recipe leaves no temporary file."""
    for number in (8, 9):
        root = made(source, tmp_path, f"in{number}")
        path, temp = _paths(root)
        before = path.read_bytes()
        target = temp if number == 8 else root / "recipes" / "red-braised-pork.toml"
        with shop_faults(root, rule("move" if number == 8 else "read", target, CTRL_C)):
            result = call_main(home, ["menu", "suggest", W47, "--data", str(root)])
        assert result == (130, "", ""), number
        assert path.read_bytes() == before, number
        assert _entries(root) == ["2026-W47.toml"], number


def _check_system(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 10 and 11: a menu file that another program holds open, and a half-written file."""
    root = made(source, tmp_path, "in10")
    path, temp = _paths(root)
    before = path.read_bytes()
    with held_open(path):
        result = suggest(home, root, *week_line(W47))
    if sys.platform == "win32":
        assert result == err(1, failed(W47, FILE_WRITE_DENIED))
        assert (path.read_bytes(), temp.exists()) == (before, False)
    else:
        assert result == out(some(W47, 1, 10, 4, "left"))
        assert path.read_bytes() == w47_filled()
    assert _entries(root) == ["2026-W47.toml"]
    root = made(source, tmp_path, "in11")
    path, temp = _paths(root)
    put_bytes(temp, b"half\n")
    assert suggest(home, root, *week_line(W47)) == out(some(W47, 1, 10, 4, "left"))
    assert path.read_bytes() == w47_filled()
    assert _entries(root) == ["2026-W47.toml"]


def test_f14_t20_a_failed_save_gives_three_lines_and_keeps_the_old_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Eleven inputs: the harness, a file left behind, Ctrl+C, a file held open, a half file."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_simple(home, source, tmp_path)
    _check_left(home, source, tmp_path)
    _check_ctrl_c(home, source, tmp_path)
    _check_system(home, source, tmp_path)
