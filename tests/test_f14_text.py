"""Tests of F14 for how the text of a menu file changes, line ends, and refused files (T16-T19)."""

from collections.abc import Sequence
from pathlib import Path

from f03_support import put_bytes
from f05_support import make_home, record
from f09_support import at, empty_recipes, made
from f09_texts import err, out
from f10_support import bom_and_crlf
from f13_support import READ_SETTINGS, Change, pristine
from f14_support import (
    DINNER,
    EVERY_MEAL,
    EXAMPLE_FILES,
    FILE_47,
    IN_ZH,
    READ_CATALOG,
    W47,
    WEEK_48,
    assert_no_write,
    filled,
    menu_as,
    new_menu,
    reads,
    refuse_one,
    refuse_two,
    stamp,
    suggest,
    traced,
    w47_filled,
    week_line,
    with_dishes,
    with_meals,
)
from f14_texts import (
    R3,
    R4,
    R5,
    R6,
    SHOW_47_FILLED,
    TEXT_A,
    TEXT_A_AFTER,
    TEXT_B,
    TEXT_B_AFTER,
    TEXT_C,
    TEXT_C_AFTER,
    TEXT_D,
    TEXT_D_AFTER,
    TEXT_D_LF,
    cannot,
    cannot_zh,
    first,
    refill,
    some,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.settings import Meal

W49 = "2026-W49"


def test_f14_t16_an_empty_line_gets_its_list_and_keeps_its_comment_and_its_shape(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Text A: bare and quoted names, spaces and tabs, a day that the file leaves out."""
    home = make_home(tmp_path)
    menu_as(WEEK_48, TEXT_A)(example_folder.root)
    result = suggest(home, example_folder, *week_line(WEEK_48))
    assert result == out(some(WEEK_48, 7, 14, 0, "left"))
    assert example_folder.menu_file(WEEK_48).read_bytes() == TEXT_A_AFTER.encode("utf-8")
    shown = at(home, example_folder, "menu", "show", WEEK_48)
    assert (shown[0], shown[2]) == (0, "")


def _t17_input(  # noqa: PLR0917 - the values of one input, in the order of the plan
    home: Path,
    source: DataFolder,
    tmp_path: Path,
    name: str,
    changes: Sequence[Change],
    expected_lines: list[str],
    expected_text: str,
) -> None:
    """Makes a new example with the changes, runs the line, and checks the output and the file."""
    root = DataFolder(made(source, tmp_path, name, *changes))
    assert suggest(home, root, *week_line(WEEK_48)) == out(expected_lines), name
    assert root.menu_file(WEEK_48).read_bytes() == expected_text.encode("utf-8"), name


def test_f14_t17_new_lines_and_new_tables_follow_the_rules_of_the_layout(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Texts B, C, and D, and a dinner of three dishes."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    every = with_meals(*EVERY_MEAL)
    lines = some(WEEK_48, 7, 21, 0, "left")
    _t17_input(home, source, tmp_path, "b", [every, menu_as(WEEK_48, TEXT_B)], lines, TEXT_B_AFTER)
    lines = refill(WEEK_48, 6, 1)
    _t17_input(home, source, tmp_path, "c", [DINNER, menu_as(WEEK_48, TEXT_C)], lines, TEXT_C_AFTER)
    lines = first(WEEK_48, 7)
    _t17_input(home, source, tmp_path, "d", [DINNER, menu_as(WEEK_48, TEXT_D)], lines, TEXT_D_AFTER)
    changes = [DINNER, menu_as(WEEK_48, TEXT_D_LF)]
    _t17_input(home, source, tmp_path, "e", changes, lines, TEXT_D_AFTER)
    three = [DINNER, with_dishes("{ dinner = 3 }"), new_menu(WEEK_48, [Meal.DINNER])]
    root = DataFolder(made(source, tmp_path, "f", *three))
    assert suggest(home, root, *week_line(WEEK_48)) == out(some(WEEK_48, 2, 7, 0, "few"))
    fills = [["choy-sum", "cola-wings", "mapo-tofu"], ["red-braised-pork", "rice", "tomato-egg"]]
    assert root.menu_file(WEEK_48).read_bytes() == filled(WEEK_48, [Meal.DINNER], fills)


def _with_bom(root: Path) -> None:
    """Writes ``menus/2026-W47.toml`` again with a byte order mark before its bytes."""
    path = root / "menus" / "2026-W47.toml"
    put_bytes(path, b"\xef\xbb\xbf" + path.read_bytes())


def _with_crlf(root: Path) -> None:
    """Writes ``menus/2026-W47.toml`` again with each LF replaced by CR LF."""
    path = root / "menus" / "2026-W47.toml"
    put_bytes(path, path.read_bytes().replace(b"\n", b"\r\n"))


def test_f14_t18_a_file_with_crlf_or_a_mark_keeps_its_lines_and_gets_lf_and_no_mark(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Three inputs: both, the mark alone, and CR LF alone. No other file changes."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    expected = w47_filled()
    both = made(source, tmp_path, "both", bom_and_crlf)
    before = record(both)
    result = suggest(home, both, *week_line(W47))
    assert result == out(some(W47, 1, 10, 4, "left"))
    assert (both / "menus" / "2026-W47.toml").read_bytes() == expected
    assert at(home, both, "menu", "show", W47) == out(SHOW_47_FILLED)
    after = record(both)
    assert after.pop(FILE_47) == expected
    assert after == {key: value for key, value in before.items() if key != FILE_47}
    for name, change in (("mark", _with_bom), ("crlf", _with_crlf)):
        root = made(source, tmp_path, name, change)
        assert suggest(home, root, *week_line(W47)) == out(some(W47, 1, 10, 4, "left")), name
        assert (root / "menus" / "2026-W47.toml").read_bytes() == expected, name


def _refused(
    source: DataFolder,
    tmp_path: Path,
    name: str,
    changes: Sequence[Change],
    week: str,
) -> tuple[Path, tuple[bytes, int]]:
    """Makes a new example with the changes, and gives its path and the stamp of its menu file."""
    root = made(source, tmp_path, name, *changes)
    return root, stamp(root / "menus" / f"{week}.toml")


def _assert_kept(root: Path, week: str, before: tuple[bytes, int]) -> None:
    """Checks that the menu file keeps its bytes and its time, and that ``menus/`` has no .tmp."""
    assert stamp(root / "menus" / f"{week}.toml") == before
    assert not [path for path in (root / "menus").iterdir() if path.name.endswith(".tmp")]


def _check_first_and_second(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 1 and 2: a meal written over several lines, with the reads of the record."""
    root, before = _refused(source, tmp_path, "r1", [refuse_one], W47)
    assert suggest(home, root, *week_line(W47)) == err(1, cannot(W47))
    assert suggest(home, root, *week_line(W47, *IN_ZH)) == err(1, cannot_zh(W47))
    result, calls, _ = traced(home, root, [], *week_line(W47))
    assert result == err(1, cannot(W47))
    assert calls == [READ_SETTINGS, READ_CATALOG, *reads(FILE_47, FILE_47)]
    assert_no_write(calls)
    _assert_kept(root, W47, before)
    root, before = _refused(source, tmp_path, "r2", [refuse_two], W47)
    assert suggest(home, root, *week_line(W47)) == err(1, cannot(W47))
    _assert_kept(root, W47, before)


def _check_new_text_refused(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 3 to 6: a new text that does not read as the old table with the new dishes."""
    root, before = _refused(source, tmp_path, "r3", [menu_as(W49, R3)], W49)
    assert suggest(home, root, *week_line(W49)) == err(1, cannot(W49))
    result, calls, _ = traced(home, root, [], *week_line(W49))
    assert result == err(1, cannot(W49))
    assert [call for call in calls if call.startswith("read recipes/")] == reads(*EXAMPLE_FILES)
    assert_no_write(calls)
    _assert_kept(root, W49, before)
    for name, text in (("r4", R4), ("r5", R5), ("r6", R6)):
        root, before = _refused(source, tmp_path, name, [menu_as(W49, text)], W49)
        assert suggest(home, root, *week_line(W49)) == err(1, cannot(W49)), name
        if name == "r6":
            assert suggest(home, root, *week_line(W49, *IN_ZH)) == err(1, cannot_zh(W49))
        _assert_kept(root, W49, before)


def test_f14_t19_a_file_that_the_command_cannot_fill_is_refused_and_never_broken(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven inputs: a refusal before any recipe, a refusal after the recipes, and no refusal."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_first_and_second(home, source, tmp_path)
    _check_new_text_refused(home, source, tmp_path)
    root, before = _refused(source, tmp_path, "r7", [menu_as(W49, R3), empty_recipes], W49)
    assert suggest(home, root, *week_line(W49)) == out(some(W49, 0, 14, 0, "left"))
    _assert_kept(root, W49, before)
