"""Tests of F11 for the table of menu show: a week with dishes and a week with none (T30, T31)."""

from functools import partial
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f09_support import at, extra_recipes, long_name, made
from f09_texts import EN, ZH, out
from f11_support import (
    LINE_BREAKS,
    breakfast_only,
    empty_menus,
    held,
    menu_text,
    week_b,
    week_c,
    week_d,
)
from f11_texts import (
    BLOCK_A,
    BLOCK_A_ZH,
    BLOCK_B,
    BLOCK_B_ZH,
    BLOCK_C,
    BLOCK_C_ZH,
    BLOCK_F23,
    BLOCK_F23_ZH,
    BLOCK_F47,
    BLOCK_F47_ZH,
    BLOCK_F53,
    BLOCK_F53_ZH,
    DATES,
    LUNCH_DINNER,
    SHOW_47,
    SHOW_47_ZH,
    empty,
    new,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.text import display_width


def _check_columns(lines: list[str], headings: tuple[str, ...], columns: tuple[int, ...]) -> None:
    """Checks the display column where each heading starts in the header line of a table."""
    header = lines[2]
    found = tuple(display_width(header[: header.index(heading)]) for heading in headings)
    assert found == columns, header


def _show(home: Path, root: Path, *argv: str) -> tuple:
    """Runs ``menu show`` with the arguments in a data folder."""
    return at(home, root, "menu", "show", *argv)


def _check_week_47(home: Path, example: DataFolder) -> None:
    """Checks input 1 of F11-T30: the example, and the widths of its columns."""
    english = _show(home, example, "2026-W47")
    chinese = _show(home, example, "2026-W47", "--lang", "zh")
    assert english == out(SHOW_47)
    assert chinese == out(SHOW_47_ZH)
    _check_columns(SHOW_47, ("Lunch", "Dinner"), (13, 41))
    _check_columns(SHOW_47_ZH, ("午餐", "晚餐"), (16, 32))


def _check_week_b(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Checks input 2 of F11-T30: week B, with a dish twice and ten servings."""
    root = made(example, tmp_path, "b", week_b)
    assert _show(home, root, "2026-W48") == out(BLOCK_A)
    assert _show(home, root, "2026-W48", "--lang", "zh") == out(BLOCK_A_ZH)
    _check_columns(BLOCK_A, ("Lunch", "Dinner"), (13, 39))
    _check_columns(BLOCK_A_ZH, ("午餐", "晚餐"), (16, 31))


def test_f11_t30_the_table_has_a_row_for_each_day_and_a_column_for_each_meal(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example, weeks B to D, and a name with a line break of three kinds."""
    home = make_home(tmp_path)
    _check_week_47(home, example_folder)
    _check_week_b(home, example_folder, tmp_path)
    c = made(example_folder, tmp_path, "c", extra_recipes, week_c, breakfast_only)
    assert _show(home, c, "2026-W49") == out(BLOCK_B)
    assert _show(home, c, "2026-W49", "--lang", "zh") == out(BLOCK_B_ZH)
    for number, line_break in enumerate(LINE_BREAKS):
        change = partial(long_name, escape=line_break)
        d = made(example_folder, tmp_path, f"d{number}", change, week_d)
        for argv, block in (((), BLOCK_C), (("--lang", "zh"), BLOCK_C_ZH)):
            result = _show(home, d, "2026-W50", *argv)
            assert result == out(block), line_break
            assert "\r" not in result[1]
            assert "\u2028" not in result[1]


def _check_blocks_of_f(home: Path, root: Path) -> None:
    """Checks the six outputs of block F, and that ``empty`` gives the same lines."""
    blocks = [
        ("2026-W47", BLOCK_F47, BLOCK_F47_ZH),
        ("2026-W53", BLOCK_F53, BLOCK_F53_ZH),
        ("2026-W23", BLOCK_F23, BLOCK_F23_ZH),
    ]
    for week, english, chinese in blocks:
        assert empty(week, EN, LUNCH_DINNER) == english
        assert empty(week, ZH, LUNCH_DINNER) == chinese
        assert _show(home, root, week) == out(english)
        assert _show(home, root, week, "--lang", "zh") == out(chinese)
    _check_columns(BLOCK_F23, ("Lunch",), (12,))
    _check_columns(BLOCK_F23_ZH, ("午餐",), (14,))


def test_f11_t31_a_week_with_no_dish_shows_a_dash_in_every_meal_and_no_count_line(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """New menus for three weeks, block F, and two files that hold no dish."""
    home = make_home(tmp_path)
    root = made(example_folder, tmp_path, "empty", empty_menus)
    for week in ("2026-W47", "2026-W53", "2026-W23"):
        file = Path(root, "menus", f"{week}.toml")
        assert at(home, root, "menu", "new", week) == out(
            new(file, DATES[week][0], "lunch and dinner")
        )
        assert held(file) == menu_text(week, LUNCH_DINNER)
    _check_blocks_of_f(home, root)
    other = made(example_folder, tmp_path, "other")
    write(other / "menus" / "2026-W51.toml", 'week = "2026-W51"\n\n[monday]\nbreakfast = []\n')
    write(other / "menus" / "2026-W52.toml", 'week = "2026-W52"\n')
    assert _show(home, other, "2026-W51") == out(empty("2026-W51", EN, LUNCH_DINNER))
    shown = _show(home, other, "2026-W51", "--lang", "zh")
    assert shown == out(empty("2026-W51", ZH, LUNCH_DINNER))
    assert _show(home, other, "2026-W52") == out(empty("2026-W52", EN, LUNCH_DINNER))
