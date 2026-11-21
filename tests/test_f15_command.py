"""Tests of F15 for ADD_COMMAND and for how ``run`` uses its context (T01 and T02)."""

import io
from datetime import date
from pathlib import Path

from f05_support import copy_example, make_home
from f05_texts import lines_text
from f07_support import call
from f14_support import FrontSource
from f15_blocks import BASE_FILE, HELP_15, HELP_15_ZH
from f15_support import BASE, TEN_COMMANDS, fresh, listing, recipe_names
from f15_texts import (
    ADD_HELP,
    ID_PROMPT,
    base_out,
    id_exists,
    servings_prompt,
)
from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.commands.add import ADD_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import display_width

LANG_TEXT_EN = "The language of the output. Default: the settings, else English."
LANG_TEXT_ZH = "输出语言。默认：设置里的语言，否则英文。"


def _check_fields() -> None:
    """Checks the fields of ``ADD_COMMAND``."""
    assert ADD_COMMAND.words == ("add",)
    assert ADD_COMMAND.usage == BiText("add", "add")
    assert ADD_COMMAND.help_line.render(Lang.EN) == ADD_HELP[0]
    assert ADD_COMMAND.help_line.render(Lang.ZH) == ADD_HELP[1]
    assert (ADD_COMMAND.argument, ADD_COMMAND.options) == (None, ())
    assert ADD_COMMAND.folder is FolderUse.READ


def _check_example_run(example: DataFolder) -> None:
    """Runs the example of 2.1: an ID that exists, and then an empty answer."""
    out, err = io.StringIO(), io.StringIO()
    answers = io.StringIO("tomato-egg\n\n")
    context = Context(Lang.EN, example, Settings(), out, err, date(2026, 11, 10), input=answers)
    assert ADD_COMMAND.run(context, Arguments()) == 0
    assert out.getvalue().splitlines() == [
        ID_PROMPT[0] + "tomato-egg",
        id_exists("tomato-egg")[0],
        ID_PROMPT[0],
    ]
    assert err.getvalue() == ""
    assert len(recipe_names(example)) == 7


def _text_column(line: str, text: str) -> int:
    """Gives the display width of what comes before the text at the end of a help line."""
    assert line.endswith(text), (line, text)
    return display_width(line[: len(line) - len(text)])


def _check_real_help(home: Path, argv: list[str], search: str, add_text: str, lang: str) -> None:
    """Checks that the line of ``add`` comes after the line of ``search``, in its column."""
    code, text, error = call(home, argv)
    assert (code, error) == (0, "")
    lines = text.split("\n")
    first = next(index for index, line in enumerate(lines) if line.startswith(search))
    found = next(
        index for index, line in enumerate(lines) if index > first and line.startswith("  add ")
    )
    lang_line = next(line for line in lines if line.startswith("  --lang en|zh"))
    assert _text_column(lines[found], add_text) == _text_column(lang_line, lang)


def test_f15_t01_the_add_command_is_described_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1, the help of ten commands, and the help of the real commands."""
    home = make_home(tmp_path)
    _check_fields()
    _check_example_run(example_folder)
    assert len(HELP_15) == len(HELP_15_ZH) == 23
    assert call(home, ["--help"], commands=TEN_COMMANDS) == (0, lines_text(*HELP_15), "")
    zh_argv = ["--help", "--lang", "zh"]
    assert call(home, zh_argv, commands=TEN_COMMANDS) == (0, lines_text(*HELP_15_ZH), "")
    _check_real_help(home, ["--help"], "  search WORD... ", ADD_HELP[0], LANG_TEXT_EN)
    _check_real_help(home, zh_argv, "  search 词... ", ADD_HELP[1], LANG_TEXT_ZH)


def _run_with(
    folder: DataFolder, lang: Lang, settings: Settings, today: date
) -> tuple[tuple[int, str, str], list[tuple[list[str], int]]]:
    """Calls ``ADD_COMMAND.run`` with the answers of BASE, and gives the result and the draws."""
    out, err = io.StringIO(), io.StringIO()
    source = FrontSource()
    answers = io.StringIO("".join(f"{answer}\n" for answer in BASE))
    context = Context(lang, folder, settings, out, err, today, random=source, input=answers)
    code = ADD_COMMAND.run(context, Arguments())
    return (code, out.getvalue(), err.getvalue()), source.calls


def _expect_run(
    folder: DataFolder, lang: Lang, servings: int, result: tuple[int, str, str]
) -> None:
    """Checks the result of a run of BASE with the servings of the settings, and the file."""
    zh = lang is Lang.ZH
    prompt = servings_prompt(servings)[zh]
    expected = base_out(folder, zh, servings=[prompt])
    assert result == (0, lines_text(*expected), "")
    data = BASE_FILE.replace("servings = 2", f"servings = {servings}").encode("utf-8")
    assert folder.recipe_file("new-dish").read_bytes() == data


def test_f15_t02_run_uses_its_context_and_keeps_no_state(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four runs: the language and servings of the context, no draw, and no state."""
    source = DataFolder(copy_example(example_folder, tmp_path / "source"))
    dinner = Settings(Lang.EN, (Meal.DINNER,), 5)
    every = Settings(Lang.ZH, tuple(Meal), 1)
    first = fresh(source, tmp_path, "one")
    result, draws = _run_with(first, Lang.ZH, dinner, date(2030, 1, 1))
    _expect_run(first, Lang.ZH, 5, result)
    assert draws == []
    second = fresh(source, tmp_path, "two")
    result, draws = _run_with(second, Lang.EN, every, date(2026, 11, 10))
    _expect_run(second, Lang.EN, 1, result)
    assert draws == []
    third = fresh(source, tmp_path, "three")
    result, draws = _run_with(third, Lang.EN, Settings(servings=100), date(2026, 11, 10))
    _expect_run(third, Lang.EN, 100, result)
    assert draws == []
    fourth = fresh(source, tmp_path, "four")
    again, draws = _run_with(fourth, Lang.EN, every, date(2026, 11, 10))
    _expect_run(fourth, Lang.EN, 1, again)
    assert draws == []
    assert recipe_names(fourth) == listing("new-dish.toml")
