"""Tests of F11 for both commands with the real cli: folders, languages, v0.1 steps (T33 to T36)."""

from pathlib import Path

import pytest

from f05_support import copy_example, make_home, run_module
from f05_texts import no_data_folder
from f07_changes import edit, make_init, the_typo
from f07_support import call, snapshot
from f07_texts import TYPO
from f09_support import at, made
from f09_texts import RUN_HELP_COMMANDS, RUN_HELP_OPTIONS, err, out, stop
from f10_support import bom_and_crlf, chinese_settings
from f11_support import held, menu_text
from f11_texts import (
    BLOCK_E,
    BLOCK_E_ZH,
    DATES,
    EVERY_MEAL,
    LUNCH_DINNER,
    SHOW_47,
    SHOW_47_ZH,
    exists,
    new,
    new_zh,
    no_menu,
    not_a_week,
    not_a_week_zh,
)
from recipe_menu.datafile import DataFolder

BOTH = "lunch and dinner"
BOTH_ZH = "午餐和晚餐"
WEEK_48 = DATES["2026-W48"]


def _check_new_file(root: Path, week: str) -> None:
    """Checks that a new file holds the text of its week, with no byte order mark and no CR."""
    data = held(root / "menus" / f"{week}.toml")
    assert data == menu_text(week, LUNCH_DINNER), week
    assert data is not None
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in data


def _check_settings_and_bom(home: Path, example_folder: DataFolder, tmp_path: Path) -> None:
    """Chinese settings and a BOM with CRLF: the output follows them, the file does not."""
    c = made(example_folder, tmp_path, "c", chinese_settings)
    assert at(home, c, "menu", "show", "2026-W47") == out(SHOW_47_ZH)
    assert at(home, c, "menu", "show", "2026-W47", "--lang", "en") == out(SHOW_47)
    created = at(home, c, "menu", "new", "2026-W48")
    assert created == out(new_zh(c / "menus" / "2026-W48.toml", WEEK_48[1], BOTH_ZH))
    _check_new_file(c, "2026-W48")
    d = made(example_folder, tmp_path, "d", bom_and_crlf)
    assert at(home, d, "menu", "show", "2026-W47") == out(SHOW_47)
    created = at(home, d, "menu", "new", "2026-W48")
    assert created == out(new(d / "menus" / "2026-W48.toml", WEEK_48[0], BOTH))
    _check_new_file(d, "2026-W48")


def test_f11_t33_both_commands_use_the_folder_and_the_language_that_cli_picks(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--data``, ``RECIPE_MENU_DATA``, ``~/recipe-menu``, ``--lang``, the settings, and BOM."""
    home = make_home(tmp_path)
    b = copy_example(example_folder, tmp_path / "One Drive" / "菜谱")
    environ = {"RECIPE_MENU_DATA": str(b)}
    assert at(home, None, "menu", "show", "2026-W47", environ=environ) == out(SHOW_47)
    file = b / "menus" / "2026-W48.toml"
    created = at(home, None, "menu", "new", "2026-W48", environ=environ)
    assert created == out(new(file, WEEK_48[0], BOTH))
    _check_new_file(b, "2026-W48")
    assert at(home, None, "menu", "show", "2026-W47") == no_data_folder(home / "recipe-menu")
    home_folder = copy_example(example_folder, home / "recipe-menu")
    created = at(home, None, "menu", "new", "2026-W48")
    assert created == out(new(home_folder / "menus" / "2026-W48.toml", WEEK_48[0], BOTH))
    _check_new_file(home_folder, "2026-W48")
    cwd = tmp_path / "cwd"
    copy_example(example_folder, cwd / "rel")
    monkeypatch.chdir(cwd)
    created = call(home, ["menu", "new", "2026-W49", "--data", "rel"])
    expected = new(Path.cwd() / "rel" / "menus" / "2026-W49.toml", DATES["2026-W49"][0], BOTH)
    assert created == out(expected)
    _check_new_file(Path.cwd() / "rel", "2026-W49")
    other = copy_example(example_folder, home / "other")
    created = call(home, ["menu", "new", "2026-W50", "--data", "~/other"])
    assert created == out(new(other / "menus" / "2026-W50.toml", DATES["2026-W50"][0], BOTH))
    _check_new_file(other, "2026-W50")
    _check_settings_and_bom(home, example_folder, tmp_path)


def test_f11_t34_v0_1_s16_the_settings_name_the_meals_and_the_servings(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The init folder with three meals and 3 servings: a new menu, one dish, and the table."""
    home = make_home(tmp_path)
    root = make_init(example_folder, tmp_path / "init")
    edit(
        root / "settings.toml",
        'meals = ["lunch", "dinner"]',
        'meals = ["breakfast", "lunch", "dinner"]',
    )
    edit(root / "settings.toml", "servings = 2 ", "servings = 3 ")
    file = root / "menus" / "2026-W48.toml"
    created = at(home, root, "menu", "new", "2026-W48")
    assert created == out(new(file, WEEK_48[0], "breakfast, lunch, and dinner"))
    assert created[1].split("\n")[1] == "7 days with breakfast, lunch, and dinner, all empty."
    assert held(file) == menu_text("2026-W48", EVERY_MEAL)
    edit(file, "[monday]\nbreakfast = []", '[monday]\nbreakfast = ["tomato-egg"]')
    assert at(home, root, "menu", "show", "2026-W48") == out(BLOCK_E)
    assert at(home, root, "menu", "show", "2026-W48", "--lang", "zh") == out(BLOCK_E_ZH)


def test_f11_t35_the_lines_that_create_nothing_change_no_file_under_home_or_the_current_folder(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """v0.1-S23: a snapshot of ``home`` and of the current folder is the same after each line."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    (root / "shopping").mkdir()
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    help_text = at(home, None, "--help")
    tag = ['"menu show" has no option "--tag". It has no options of its own.']
    two_weeks = ['Unexpected argument "2026-W48". Write "recipe-menu menu new [WEEK]".']
    existing = root / "menus" / "2026-W47.toml"
    lines = [
        (("menu", "show", "2026-W47"), out(SHOW_47)),
        (("menu", "show", "2026-W48"), err(1, [no_menu("2026-W48")])),
        (("menu", "show", "2026-W99"), err(2, [not_a_week("2026-W99")])),
        (("menu", "show"), err(1, [no_menu("2026-W46")])),
        (("menu", "show", "--tag", "x"), err(2, [*tag, RUN_HELP_OPTIONS[0]])),
        (("menu", "show", "--help"), (0, help_text[1], "")),
        (("menu", "new", "2026-W47"), err(1, [exists(existing)])),
        (("menu", "new", "2026-W99"), err(2, [not_a_week("2026-W99")])),
        (("menu", "new", "2026-W47", "2026-W48"), err(2, [*two_weeks, RUN_HELP_COMMANDS[0]])),
    ]
    before = (snapshot(home), snapshot(cwd))
    for argv, expected in lines:
        assert at(home, None, *argv) == expected, argv
    assert (snapshot(home), snapshot(cwd)) == before
    the_typo(root)
    before = (snapshot(home), snapshot(cwd))
    assert at(home, None, "menu", "show", "2026-W47") == stop(TYPO)
    assert at(home, None, "menu", "new", "2026-W47") == err(1, [exists(existing)])
    assert (snapshot(home), snapshot(cwd)) == before


def test_f11_t36_python_dash_m_runs_both_commands_and_writes_utf8(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The real entry point: a table, a new menu, a refusal, a wrong week, and no menu."""
    root = example_folder.root
    data = str(root)
    shown = run_module(tmp_path, "menu", "show", "2026-W47", "--lang", "zh", "--data", data)
    assert shown == out(SHOW_47_ZH)
    file = example_folder.menu_file("2026-W48")
    created = run_module(tmp_path, "menu", "new", "2026-W48", "--lang", "zh", "--data", data)
    assert created == out(new_zh(file, WEEK_48[1], BOTH_ZH))
    assert held(file) == menu_text("2026-W48", LUNCH_DINNER)
    refused = run_module(tmp_path, "menu", "new", "2026-W48", "--data", data)
    assert refused == (1, "", f"{exists(file)}\n")
    wrong = run_module(tmp_path, "menu", "show", "2026-W99", "--lang", "zh", "--data", data)
    assert wrong == (2, "", f"{not_a_week_zh('2026-W99')}\n")
    no_menu_result = run_module(tmp_path, "menu", "show", "2026-W49", data=root)
    assert no_menu_result == (1, "", f"{no_menu('2026-W49')}\n")
