"""Tests of F07 for the settings, the options of cli, and the help of check (T15 to T17)."""

from pathlib import Path

from f03_support import write
from f05_support import copy_example, make_home
from f06_support import MEALS_LUNCH_DINNER
from f07_changes import add_friday_key, edit, mapo_mistake, menu_path, the_typo
from f07_support import AFTER, AFTER_ZH, call, check, expect, rep
from f07_texts import (
    MAPO,
    MENU_FILE,
    P_MEALS,
    PORK,
    TYPO,
    Prob,
    Result,
    m_day_key,
    m_menu_meal,
    m_settings_meal,
    p_slot,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

USAGE_EN = "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]"
USAGE_ZH = "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]"
CHECK_EN = "Check every data file for mistakes."
CHECK_ZH = "检查每个数据文件有没有错误。"


def test_f07_t15_settings_with_an_error_do_not_stop_check(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The menus are read with no settings, and good settings give the meals of the settings."""
    home = make_home(tmp_path)
    root = example_folder.root
    settings = root / "settings.toml"
    original = settings.read_text(encoding="utf-8")
    edit(settings, 'meals = ["lunch", "dinner"]', 'meals = ["lunch", "supper"]')
    edit(settings, 'language = "en"', 'language = "zh"')
    add_friday_key(menu_path(root))
    broken = [
        Prob("settings.toml", P_MEALS, m_settings_meal("supper")),
        Prob(MENU_FILE, p_slot("friday", "supper"), m_day_key("supper")),
    ]
    assert check(home, root) == rep(1, 7, 1, broken, [PORK])
    assert check(home, root, "--lang", "zh") == rep(1, 7, 1, broken, [PORK], Lang.ZH)

    write(settings, original)
    good = [Prob(MENU_FILE, p_slot("friday", "supper"), m_menu_meal("supper", MEALS_LUNCH_DINNER))]
    assert check(home, root) == rep(1, 7, 1, good, [PORK])
    assert check(home, root, "--lang", "zh") == rep(1, 7, 1, good, [PORK], Lang.ZH)


def test_f07_t16_check_reads_the_folder_and_the_language_that_cli_picks(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """--data, RECIPE_MENU_DATA, and the home folder; --lang, the settings, and English."""
    home = make_home(tmp_path)
    root = example_folder.root
    empty = tmp_path / "empty"
    empty.mkdir()
    zh_settings = copy_example(example_folder, tmp_path / "zh_settings")
    edit(zh_settings / "settings.toml", 'language = "en"', 'language = "zh"')
    in_home = copy_example(example_folder, home / "recipe-menu")
    the_typo(in_home)

    assert check(home, root, "--lang", "zh") == expect(0, AFTER_ZH)
    assert check(home, None, environ={"RECIPE_MENU_DATA": str(root)}) == expect(0, AFTER)
    assert check(home, root, environ={"RECIPE_MENU_DATA": str(empty)}) == expect(0, AFTER)
    assert check(home, None) == rep(1, 7, 1, [TYPO], [PORK])
    assert check(home, zh_settings) == expect(0, AFTER_ZH)
    assert check(home, zh_settings, "--lang", "en") == expect(0, AFTER)


def _check_help(result: Result, lang: Lang) -> None:
    """Checks that a call gave the help with the line of ``check`` in its place."""
    code, out, err = result
    assert (code, err) == (0, "")
    lines = out.splitlines()
    zh = lang is Lang.ZH
    assert lines[0] == (USAGE_ZH if zh else USAGE_EN)
    assert lines[4] == ("命令：" if zh else "Commands:")
    block = lines[5 : lines.index("", 5)]
    mine = [line for line in block if line.startswith("  check ")]
    assert len(mine) == 1
    assert mine[0].endswith(CHECK_ZH if zh else CHECK_EN)
    options = [line for line in lines if line.startswith("  --lang en|zh")]
    assert len(options) == 1
    text = "输出语言。" if zh else "The language of the output."
    assert mine[0].index(CHECK_ZH if zh else CHECK_EN) == options[0].index(text)


def test_f07_t17_the_help_lists_check_and_check_help_does_not_run_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The line of check in the help of the real commands, and --help ahead of a run."""
    home = make_home(tmp_path)
    root = example_folder.root
    assert check(home, root) == expect(0, AFTER)
    _check_help(call(home, ["--help"]), Lang.EN)
    _check_help(call(home, ["--help", "--lang", "zh"]), Lang.ZH)

    mapo_mistake(root)
    _check_help(check(home, root, "--help"), Lang.EN)
    _check_help(check(home, root, "--help", "--lang", "zh"), Lang.ZH)
    assert check(home, root) == rep(1, 7, 1, [MAPO], [PORK])
