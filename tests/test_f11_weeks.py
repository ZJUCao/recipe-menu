"""Tests of F11 for the week of both commands: today, this, next, and a wrong value (T20, T21)."""

from datetime import date
from functools import partial
from pathlib import Path

from f05_support import make_home
from f07_changes import catalog_brace, the_typo
from f08_support import faults, full_record
from f09_support import at, made
from f09_texts import EN, ZH, err, out
from f10_support import chinese_settings
from f11_support import empty_menus, held, menu_text, no_menus_folder, on
from f11_texts import (
    BLOCK_F53,
    DATES,
    LUNCH_DINNER,
    empty,
    exists,
    exists_zh,
    new,
    not_a_week,
    not_a_week_zh,
)
from recipe_menu.datafile import DataFolder

# Each date of F11-T20, with the week of today and the week of the date 7 days later.
TODAYS = [
    (date(2026, 11, 10), "2026-W46", "2026-W47"),
    (date(2026, 11, 22), "2026-W47", "2026-W48"),
    (date(2026, 12, 27), "2026-W52", "2026-W53"),
    (date(2026, 12, 30), "2026-W53", "2027-W01"),
    (date(2027, 1, 3), "2026-W53", "2027-W01"),
    (date(2025, 12, 29), "2026-W01", "2026-W02"),
]
BAD_WEEKS = ["2026-W99", "Next", "", "2026-w47", "2025-W53", " this"]
BOTH = "lunch and dinner"


def _check_date(home: Path, root: Path, today: date, this: str, later: str) -> None:
    """Runs the eight lines of F11-T20 on one date, in an empty-menus example."""
    run = partial(on, home, root, today)
    file_this, file_next = root / "menus" / f"{this}.toml", root / "menus" / f"{later}.toml"
    assert run("menu", "new") == out(new(file_this, DATES[this][0], BOTH))
    assert held(file_this) == menu_text(this, LUNCH_DINNER)
    assert run("menu", "new", "next") == out(new(file_next, DATES[later][0], BOTH))
    assert held(file_next) == menu_text(later, LUNCH_DINNER)
    assert run("menu", "new", "this", "--lang", "zh") == err(1, [exists_zh(file_this)])
    assert run("menu", "new", later) == err(1, [exists(file_next)])
    shown = out(empty(this, EN, LUNCH_DINNER))
    assert run("menu", "show", "this") == shown
    assert run("menu", "show") == shown
    assert run("menu", "show", "next", "--lang", "zh") == out(empty(later, ZH, LUNCH_DINNER))
    assert run("menu", "show", this) == shown
    names = sorted(path.name for path in (root / "menus").iterdir())
    assert names == sorted([f"{this}.toml", f"{later}.toml"])
    if this == "2026-W53":
        assert shown == out(BLOCK_F53)


def test_f11_t20_both_commands_take_the_week_from_today_this_and_next(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Six dates, with a year change, and the lines of v0.1-S14 on 30 December 2026."""
    home = make_home(tmp_path)
    for index, (today, this, later) in enumerate(TODAYS):
        root = made(example_folder, tmp_path, f"date{index}", empty_menus)
        _check_date(home, root, today, this, later)


def _check_wrong_values(home: Path, example: DataFolder) -> None:
    """Runs input 1 and input 2 of F11-T21 in the example."""
    before = full_record(example.root)
    for value in BAD_WEEKS:
        for command in ("new", "show"):
            with faults(example.root) as state:
                result = at(home, example, "menu", command, value)
            assert result == err(2, [not_a_week(value)]), (command, value)
            assert (state.calls, state.listings) == (["read settings.toml"], [])
    assert full_record(example.root) == before
    result = at(home, example, "menu", "new", "2026-W99", "--lang", "zh")
    assert result == err(2, [not_a_week_zh("2026-W99")])
    result = at(home, example, "menu", "show", "Next", "--lang", "zh")
    assert result == err(2, [not_a_week_zh("Next")])


def test_f11_t21_a_value_that_is_not_a_week_gives_exit_code_2_before_any_file_is_touched(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Wrong values give ``NOT_A_WEEK`` whatever the folder holds, in the language of the output."""
    home = make_home(tmp_path)
    _check_wrong_values(home, example_folder)
    no_menus = made(example_folder, tmp_path, "no-menus", no_menus_folder)
    assert at(home, no_menus, "menu", "new", "2026-W99") == err(2, [not_a_week("2026-W99")])
    assert not (no_menus / "menus").exists()
    brace = made(example_folder, tmp_path, "brace", catalog_brace)
    assert at(home, brace, "menu", "show", "2026-W99") == err(2, [not_a_week("2026-W99")])
    typo = made(example_folder, tmp_path, "typo", the_typo)
    assert at(home, typo, "menu", "show", "") == err(2, [not_a_week("")])
    chinese = made(example_folder, tmp_path, "chinese", chinese_settings)
    assert at(home, chinese, "menu", "show", "2026-W99") == err(2, [not_a_week_zh("2026-W99")])
    result = at(home, chinese, "menu", "show", "2026-W99", "--lang", "en")
    assert result == err(2, [not_a_week("2026-W99")])
