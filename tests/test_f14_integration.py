"""Tests of F14 for the whole program: the v0.2 scenarios and the entry point (T28-T32)."""

import tomllib
from datetime import date
from pathlib import Path

import pytest

from f05_support import copy_example, make_home, run_module
from f07_changes import append, edit, the_typo
from f07_support import call, check, expect, snapshot
from f07_texts import TYPO
from f09_support import at, made
from f09_texts import err, out, stop
from f11_support import empty_menus, menu_text, on
from f11_texts import no_menu, not_a_week, not_a_week_zh
from f13_support import pristine
from f14_support import (
    AFTER_40,
    DAYS,
    EVERY_MEAL,
    EXAMPLE_IDS,
    IN_ZH,
    LUNCH_DINNER,
    SUGGEST_IDS,
    W47,
    WEEK_48,
    filled,
    new_menu,
    one_each,
    picks,
    seeded,
    suggest,
    suggest_folder,
    w47_filled,
    week_line,
    with_meals,
)
from f14_texts import first, some, some_zh, tags
from recipe_menu.datafile import DataFolder
from recipe_menu.settings import Meal


def test_f14_t28_v0_2_s06_dishes_of_a_dinner_give_28_recipes_to_a_week_of_21_meals(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Three meals a day with two dishes at dinner: the file, the table, ``check``, and ``shop``."""
    home = make_home(tmp_path)
    root = suggest_folder(pristine(example_folder, tmp_path), tmp_path, "r")
    settings = root / "settings.toml"
    edit(settings, 'meals = ["lunch", "dinner"]', 'meals = ["breakfast", "lunch", "dinner"]')
    append(settings, "dishes = { dinner = 2 }\n")
    folder = DataFolder(root)
    file = folder.menu_file(WEEK_48)
    assert at(home, folder, "menu", "new", WEEK_48)[0] == 0
    assert file.read_bytes() == menu_text(WEEK_48, EVERY_MEAL)
    result = suggest(home, folder, *week_line(WEEK_48), random=seeded(11))
    assert result == out(first(WEEK_48, 21))
    chosen = iter(picks(11, SUGGEST_IDS, 28))
    fills = []
    for _ in DAYS:
        fills += [[next(chosen)], [next(chosen)], [next(chosen), next(chosen)]]
    assert file.read_bytes() == filled(WEEK_48, EVERY_MEAL, fills)
    shown = at(home, folder, "menu", "show", WEEK_48)
    assert (shown[0], shown[2]) == (0, "")
    lines = shown[1].splitlines()
    assert lines[:2] == ["Menu for 2026-W48, 23 to 29 November 2026", ""]
    heading = lines[2]
    assert heading.startswith("Day")
    assert heading.index("Breakfast") < heading.index("Lunch") < heading.index("Dinner")
    assert lines[-1] == "21 meals, 28 dishes. \u00d7n: servings."
    assert check(home, root) == expect(0, AFTER_40)
    listed = at(home, folder, "shop", WEEK_48)
    assert (listed[0], listed[2]) == (0, "")
    lines = listed[1].splitlines()
    dates = "23 to 29 November 2026"
    assert lines[0] == f"Shopping list for 2026-W48, {dates}: 21 meals, 28 dishes"
    assert lines[-1] == f"Saved {root / 'shopping' / '2026-W48.md'}"
    assert (root / "shopping" / "2026-W48.md").exists()


def test_f14_t29_v0_2_s07_seven_recipes_fill_the_first_seven_meals_of_next_week(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``this`` and ``next`` follow the date that ``main`` gets: the end of the year of 53 weeks."""
    home = make_home(tmp_path)
    root = made(pristine(example_folder, tmp_path), tmp_path, "e", empty_menus)
    today = date(2026, 12, 30)
    assert on(home, root, today, "menu", "new", "next")[0] == 0
    file = root / "menus" / "2027-W01.toml"
    assert file.read_bytes() == menu_text("2027-W01", LUNCH_DINNER)
    result = suggest(home, root, *week_line("next"), today=today)
    assert result == out(some("2027-W01", 7, 14, 0, "left"))
    assert file.read_bytes() == filled("2027-W01", LUNCH_DINNER, one_each(EXAMPLE_IDS))
    assert suggest(home, root, "menu", "suggest", today=today) == err(1, [no_menu("2026-W53")])
    assert [path.name for path in (root / "menus").iterdir()] == ["2027-W01.toml"]


def test_f14_t30_v0_2_s08_a_wrong_week_no_menu_an_unknown_tag_and_a_mistake_stop_the_run(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Four lines with no folder: each stops, and no file under ``home`` or the folder changes."""
    home = make_home(tmp_path)
    root = copy_example(pristine(example_folder, tmp_path), home / "recipe-menu")
    (root / "shopping").mkdir()
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    def run(*argv: str) -> tuple[int, str, str]:
        """Runs a line with no folder, and checks that both snapshots stay the same."""
        before = (snapshot(home), snapshot(cwd))
        result = suggest(home, None, *argv)
        assert (snapshot(home), snapshot(cwd)) == before
        return result

    assert run(*week_line("2026-W99")) == err(2, [not_a_week("2026-W99")])
    assert run(*week_line(WEEK_48)) == err(1, [no_menu(WEEK_48)])
    assert run(*week_line(W47, "--tag", "breakfast")) == err(1, [tags("breakfast")])
    the_typo(root)
    assert run(*week_line(W47)) == stop(TYPO)


def test_f14_t31_v0_2_s15_a_fill_changes_only_the_menu_file_of_the_week(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The snapshot of ``home`` changes in one file and the time of ``menus/``, and no more."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    root = copy_example(source, home / "recipe-menu")
    (root / "shopping").mkdir()
    new_menu(WEEK_48, LUNCH_DINNER)(root)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    before = (snapshot(home), snapshot(cwd))
    assert suggest(home, None, *week_line(WEEK_48)) == out(some(WEEK_48, 7, 14, 0, "left"))
    after = snapshot(home)
    skip = {"recipe-menu/menus", "recipe-menu/menus/2026-W48.toml"}
    assert {k: v for k, v in after.items() if k not in skip} == {
        k: v for k, v in before[0].items() if k not in skip
    }
    assert after["recipe-menu/menus/2026-W48.toml"][0] == filled(
        WEEK_48, LUNCH_DINNER, one_each(EXAMPLE_IDS)
    )
    assert sorted(path.name for path in (root / "menus").iterdir()) == [
        "2026-W47.toml",
        "2026-W48.toml",
    ]
    assert snapshot(cwd) == before[1]
    helped = call(home, ["--help"])
    lines = [
        (week_line(WEEK_48), out(some(WEEK_48, 0, 7, 7, "left"))),
        (("menu", "suggest", "--help"), helped),
        (week_line("2026-W99"), err(2, [not_a_week("2026-W99")])),
        (week_line(WEEK_48, "--tag", "x"), err(1, [tags("x")])),
    ]
    assert helped[0] == 0
    for argv, expected in lines:
        before = (snapshot(home), snapshot(cwd))
        assert suggest(home, None, *argv) == expected, argv
        assert (snapshot(home), snapshot(cwd)) == before, argv


def test_f14_t32_python_dash_m_runs_menu_suggest_and_writes_utf8(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The real entry point: a Chinese fill, a second run, a wrong week, no menu, a first fill."""
    source = pristine(example_folder, tmp_path)
    root = str(example_folder.root)
    data = ["--data", root]
    shown = run_module(tmp_path, "menu", "suggest", W47, *IN_ZH, *data)
    assert shown == out(some_zh(W47, 1, 10, 4, "left"))
    assert example_folder.menu_file(W47).read_bytes() == w47_filled()
    shown = run_module(tmp_path, "menu", "suggest", W47, *data)
    assert shown == out(some(W47, 0, 9, 5, "left"))
    shown = run_module(tmp_path, "menu", "suggest", "2026-W99", *IN_ZH, *data)
    assert shown == err(2, [not_a_week_zh("2026-W99")])
    assert run_module(tmp_path, "menu", "suggest", WEEK_48, *data) == err(1, [no_menu(WEEK_48)])
    dinners = made(source, tmp_path, "f", with_meals(Meal.DINNER), new_menu(WEEK_48, [Meal.DINNER]))
    shown = run_module(tmp_path, "menu", "suggest", WEEK_48, "--data", str(dinners))
    assert shown == out(first(WEEK_48, 7))
    table = tomllib.loads((dinners / "menus" / "2026-W48.toml").read_text(encoding="utf-8"))
    held = [table[day]["dinner"] for day in DAYS]
    assert all(len(items) == 1 for items in held)
    assert sorted(items[0] for items in held) == list(EXAMPLE_IDS)
