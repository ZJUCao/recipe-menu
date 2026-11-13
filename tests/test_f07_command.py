"""Tests of F07 for CHECK_COMMAND and its run (T01 to T03)."""

import io
from datetime import date
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f06_support import MEALS_DINNER
from f07_support import AFTER, EMPTY, EMPTY_ZH, call, lines_text, rep, report
from f07_texts import MENU_FILE, PORK, Prob, m_menu_meal, p_slot
from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings

HELP_EN = [
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "",
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "",
    "Commands:",
    "  check           Check every data file for mistakes.",
    "",
    "Options:",
    "  --lang en|zh    The language of the output. Default: the settings, else English.",
    "  --data FOLDER   The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version       Show the version.",
    "  --help          Show this help.",
    "",
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
]
HELP_ZH = [
    "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
    "",
    "保存菜谱，排一周的菜单，并生成它的购物清单。",
    "",
    "命令：",
    "  check           检查每个数据文件有没有错误。",
    "",
    "选项：",
    "  --lang en|zh    输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹   数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version       显示版本。",
    "  --help          显示这份帮助。",
    "",
    "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。",
]


def _help_lines(home: Path, *argv: str) -> list[str]:
    """Runs ``main`` with ``CHECK_COMMAND`` alone and gives the lines of the help."""
    code, out, err = call(home, argv, commands=(CHECK_COMMAND,))
    assert (code, err) == (0, ""), argv
    return out.splitlines()


def test_f07_t01_the_command_runs_with_the_file_settings_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1: the fields, a run with other settings in the context, and the help."""
    home = make_home(tmp_path)
    assert CHECK_COMMAND.words == ("check",)
    assert CHECK_COMMAND.usage == BiText("check", "check")
    assert CHECK_COMMAND.help_line.render(Lang.EN) == "Check every data file for mistakes."
    assert CHECK_COMMAND.help_line.render(Lang.ZH) == "检查每个数据文件有没有错误。"
    assert (CHECK_COMMAND.argument, CHECK_COMMAND.options) == (None, ())
    assert CHECK_COMMAND.folder is FolderUse.CHECK

    out, err = io.StringIO(), io.StringIO()
    dinner_only = Settings(Lang.ZH, (Meal.DINNER,), 3)
    context = Context(Lang.EN, example_folder, dinner_only, out, err, date(2026, 11, 10))
    assert CHECK_COMMAND.run(context, Arguments()) == 0
    assert out.getvalue() == lines_text(AFTER)
    assert err.getvalue() == ""

    english = _help_lines(home, "--help")
    assert english == HELP_EN
    chinese = _help_lines(home, "--help", "--lang", "zh")
    assert chinese == HELP_ZH
    for lines, check_cell, lang_cell in (
        (english, "Check every", "The language"),
        (chinese, "检查每个", "输出语言"),
    ):
        check_line = next(line for line in lines if line.startswith("  check "))
        lang_line = next(line for line in lines if line.startswith("  --lang en|zh"))
        assert check_line.index(check_cell) == 18
        assert lang_line.index(lang_cell) == 18


def test_f07_t02_run_reads_the_settings_of_the_file_and_the_language_of_the_context(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The settings of the file decide the meals, and the context decides the language."""
    write(example_folder.settings, 'meals = ["dinner"]\n')
    saturday = Prob(MENU_FILE, p_slot("saturday", "lunch"), m_menu_meal("lunch", MEALS_DINNER))
    first_out, first_err = io.StringIO(), io.StringIO()
    first = Context(Lang.ZH, example_folder, Settings(), first_out, first_err, date(2030, 1, 1))
    assert CHECK_COMMAND.run(first, Arguments()) == 1
    expected = rep(1, 7, 1, [saturday], [PORK], Lang.ZH)
    assert (1, first_out.getvalue(), first_err.getvalue()) == expected

    second_out, second_err = io.StringIO(), io.StringIO()
    other = Settings(Lang.ZH, tuple(Meal), 5)
    second = Context(Lang.EN, example_folder, other, second_out, second_err, date(2026, 11, 10))
    assert CHECK_COMMAND.run(second, Arguments()) == 1
    assert second_out.getvalue() == lines_text(report(7, 1, [saturday], [PORK]))
    assert second_err.getvalue() == ""


def test_f07_t03_run_never_raises_and_reports_a_missing_folder_as_an_empty_one(
    tmp_path: Path,
) -> None:
    """A missing data folder and an empty one give the same five errors, in both languages."""
    missing, empty = tmp_path / "missing", tmp_path / "empty"
    empty.mkdir()
    for root in (missing, empty):
        for lang, lines in ((Lang.EN, EMPTY), (Lang.ZH, EMPTY_ZH)):
            out, err = io.StringIO(), io.StringIO()
            context = Context(lang, DataFolder(root), Settings(), out, err, date(2026, 11, 10))
            assert CHECK_COMMAND.run(context, Arguments()) == 1, (root, lang)
            assert out.getvalue() == lines_text(lines), (root, lang)
            assert err.getvalue() == ""
    assert not missing.exists()
