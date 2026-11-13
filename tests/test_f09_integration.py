"""Tests of F09 for the scenarios of version 0.1 at ``main`` and at the entry point (T21 to T26)."""

from pathlib import Path

import pytest

from f03_support import edit_ingredients, ing, put_bytes, write
from f05_support import copy_example, make_home, run_module
from f05_texts import lines_text, no_data_folder
from f07_changes import broken_settings, edit, make_init, mapo_mistake
from f07_support import snapshot
from f09_support import CUCUMBER_FILE, assert_among_check, at
from f09_texts import (
    BREAKFAST,
    CUCUMBER,
    CUCUMBER_ZH,
    E_CUCUMBER,
    E_MAPO,
    E_SETTINGS,
    FOUR,
    FOUR_ZH,
    INIT_LIST,
    LIST,
    LIST_ZH,
    MAPO,
    MAPO_ZH,
    PORK_ZH,
    QUICK,
    RICE,
    RUN_HELP_COMMANDS,
    S04_LIST,
    TOMATO,
    VEG,
    VEG_ZH,
    ZH,
    err,
    not_a_recipe_id,
    out,
    servings_not_1_to_100,
    stop,
    unknown_id,
)
from recipe_menu.datafile import DataFolder


def test_f09_t21_a_new_recipe_with_an_unknown_ingredient_stops_both_commands_until_it_is_fixed(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S04 on the init folder: the error of ``check``, then the lists after the fix."""
    home = make_home(tmp_path)
    root = make_init(example_folder, home / "recipe-menu")
    write(root / "recipes" / "cucumber-salad.toml", CUCUMBER_FILE)
    assert at(home, None, "list") == stop(E_CUCUMBER)
    assert at(home, None, "show", "cucumber-salad") == stop(E_CUCUMBER)
    assert at(home, None, "show", "tomato-egg") == out(TOMATO)
    assert_among_check(home, root, E_CUCUMBER)
    edit_ingredients(DataFolder(root), added=[ing("黄瓜", "Cucumber")])
    assert at(home, None, "list") == out(S04_LIST)
    assert at(home, None, "show", "cucumber-salad") == out(CUCUMBER)
    assert at(home, None, "show", "cucumber-salad", "--lang", "zh") == out(CUCUMBER_ZH)


def test_f09_t22_a_byte_order_mark_and_crlf_line_ends_give_the_same_output(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S08: every data file written with a BOM and CRLF gives the outputs of before."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    for path in sorted(root.rglob("*.toml")):
        put_bytes(path, b"\xef\xbb\xbf" + path.read_bytes().replace(b"\n", b"\r\n"))
    assert at(home, None, "show", "tomato-egg") == out(TOMATO)
    assert at(home, None, "list") == out(LIST)
    assert at(home, None, "list", "--tag", "快手") == out(QUICK)
    assert at(home, None, "show", "red-braised-pork", "--lang", "zh") == out(PORK_ZH)
    assert at(home, None, "show", "tomato-egg", "--servings", "4", "--lang", "zh") == out(FOUR_ZH)


def test_f09_t23_both_commands_read_the_data_folder_that_cli_picks(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S20: ``--data``, else ``RECIPE_MENU_DATA``, else ``~/recipe-menu``, and none."""
    home = make_home(tmp_path)
    folder_b = copy_example(example_folder, tmp_path / "One Drive" / "菜谱")
    folder_c = make_init(example_folder, tmp_path / "c")
    environ = {"RECIPE_MENU_DATA": str(folder_c)}
    assert at(home, folder_b, "list") == out(LIST)
    assert at(home, None, "list", environ=environ) == out(INIT_LIST)
    assert at(home, folder_b, "list", environ=environ) == out(LIST)
    default = home / "recipe-menu"
    assert at(home, None, "list") == no_data_folder(default)
    assert at(home, None, "list", "--lang", "zh") == no_data_folder(default, ZH)
    four = at(home, None, "show", "tomato-egg", "--servings", "4", "--lang", "zh", environ=environ)
    assert four == out(FOUR_ZH)
    assert at(home, None, "show", "rice", environ=environ) == err(1, [unknown_id("rice")])
    assert at(home, folder_b, "show", "rice", environ=environ) == out(RICE)


def test_f09_t24_without_lang_both_commands_speak_the_language_of_the_settings(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S21 and v0.1-S22: the settings give the language, and broken settings stop both."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    settings = root / "settings.toml"
    original = settings.read_text(encoding="utf-8")
    edit(settings, 'language = "en"', 'language = "zh"')
    assert at(home, None, "list", "--tag", "素") == out(VEG_ZH)
    assert at(home, None, "list", "--tag", "素", "--lang", "en") == out(VEG)
    assert at(home, None, "show", "tomato-egg", "--servings", "4") == out(FOUR_ZH)
    assert at(home, None, "show", "mapo") == err(1, [MAPO_ZH])
    assert at(home, None, "show", "Mapo") == err(2, [not_a_recipe_id("Mapo", ZH)])
    kept = [line for line in original.splitlines(keepends=True) if not line.startswith("language")]
    write(settings, "".join(kept))
    assert at(home, None, "list", "--tag", "素") == out(VEG)
    assert at(home, None, "show", "tomato-egg") == out(TOMATO)
    broken_settings(root)
    assert at(home, None, "list") == stop(E_SETTINGS)
    assert at(home, None, "show", "tomato-egg") == stop(E_SETTINGS)


def test_f09_t25_neither_command_writes_a_file_whatever_it_reports(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """v0.1-S23: bytes, times, and entries under ``home`` and the current folder."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    (root / "shopping").mkdir()
    current = tmp_path / "cwd"
    current.mkdir()
    monkeypatch.chdir(current)
    before = (snapshot(home), snapshot(current))
    help_text = at(home, None, "--help")[1]
    lines = [
        (("list",), out(LIST)),
        (("list", "--tag", "快手"), out(QUICK)),
        (("list", "--tag", "breakfast"), err(1, [BREAKFAST])),
        (("show", "tomato-egg", "--servings", "4"), out(FOUR)),
        (("show", "mapo"), err(1, [MAPO])),
        (("show", "Mapo"), err(2, [not_a_recipe_id("Mapo")])),
        (("show", "tomato-egg", "--servings", "0"), err(2, [servings_not_1_to_100("0")])),
        (
            ("list", "extra"),
            err(
                2, ['Unexpected argument "extra". Write "recipe-menu list".', RUN_HELP_COMMANDS[0]]
            ),
        ),
        (("show", "--help"), (0, help_text, "")),
    ]
    for argv, result in lines:
        assert at(home, None, *argv) == result, argv
    assert (snapshot(home), snapshot(current)) == before
    mapo_mistake(root)
    before = (snapshot(home), snapshot(current))
    assert at(home, None, "list") == stop(E_MAPO)
    assert at(home, None, "show", "mapo-tofu") == stop(E_MAPO)
    assert (snapshot(home), snapshot(current)) == before


def test_f09_t26_the_entry_point_writes_the_output_as_utf_8_and_the_errors_to_stderr(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``python -m recipe_menu`` runs ``list`` and ``show`` with the real commands."""
    root = example_folder.root
    result = run_module(tmp_path, "list", "--lang", "zh", "--data", str(root))
    assert result == (0, lines_text(*LIST_ZH), "")
    result = run_module(
        tmp_path, "show", "tomato-egg", "--servings", "4", "--lang", "zh", "--data", str(root)
    )
    assert result == (0, lines_text(*FOUR_ZH), "")
    result = run_module(tmp_path, "show", "mapo", "--lang", "zh", "--data", str(root))
    assert result == (1, "", lines_text(MAPO_ZH))
    result = run_module(tmp_path, "show", "Mapo", "--data", str(root))
    assert result == (2, "", lines_text(not_a_recipe_id("Mapo")))
    assert run_module(tmp_path, "list", "--tag", "快手", data=root) == (0, lines_text(*QUICK), "")
