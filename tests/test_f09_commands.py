"""Tests of F09 for LIST_COMMAND, SHOW_COMMAND, and their checks of values (T01 to T03)."""

from datetime import date
from pathlib import Path

import pytest

from f05_support import make_home
from f07_changes import mapo_mistake
from f07_support import call
from f08_support import faults
from f09_support import WRONG_IDS, WRONG_SERVINGS, new_context, run_command
from f09_texts import (
    E_MAPO,
    E_NO_CATALOG,
    EN,
    FOUR_ZH,
    HELP,
    HELP_ZH,
    LIST,
    LIST_HELP,
    MAPO_ZH,
    QUICK_ZH,
    RICE,
    SHOW_HELP,
    TOMATO_ZH,
    VEG,
    ZH,
    err,
    not_a_recipe_id,
    out,
    patch,
    servings_not_1_to_100,
    stop,
)
from recipe_menu.app import Argument, Arguments, FolderUse, UsageError
from recipe_menu.commands.browse import LIST_COMMAND, SHOW_COMMAND
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

OTHER = Settings(Lang.ZH, (Meal.BREAKFAST,), 5)
OTHER_EN = Settings(Lang.EN, (Meal.BREAKFAST,), 5)
LATER = date(2030, 1, 1)
FOUR_COMMANDS = (INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND)
RICE_FOR_3 = patch(
    RICE, {2: "Servings: 3 (the recipe makes 2)   Tags: staple", 5: "  Rice   240 g"}
)


def _second_column(line: str) -> int:
    """Gives the index of the second column of a line of the help."""
    gap = line.index("  ", 2)
    return gap + len(line[gap:]) - len(line[gap:].lstrip(" "))


def _check_real_help(home: Path, argv: list[str], list_text: str, show_text: str) -> None:
    """Checks the lines of ``list`` and ``show`` in the help of the real ``COMMANDS``."""
    code, text, error = call(home, argv)
    assert (code, error) == (0, "")
    lines = text.split("\n")
    check = next(index for index, line in enumerate(lines) if line.startswith("  check "))
    list_line, show_line = lines[check + 1], lines[check + 2]
    assert list_line.startswith("  list ")
    assert show_line.startswith("  show ID ")
    column = _second_column(next(line for line in lines if line.startswith("  --lang en|zh")))
    assert list_line[column - 1] == show_line[column - 1] == " "
    assert (list_line[column:], show_line[column:]) == (list_text, show_text)


def _check_list_fields() -> None:
    """Checks the fields of ``LIST_COMMAND``."""
    assert LIST_COMMAND.words == ("list",)
    assert LIST_COMMAND.usage == BiText("list", "list")
    assert LIST_COMMAND.help_line.render(Lang.EN) == LIST_HELP[0]
    assert LIST_COMMAND.help_line.render(Lang.ZH) == LIST_HELP[1]
    assert (LIST_COMMAND.argument, LIST_COMMAND.options) == (None, ("--tag",))
    assert LIST_COMMAND.folder is FolderUse.READ


def _check_show_fields() -> None:
    """Checks the fields of ``SHOW_COMMAND``."""
    assert SHOW_COMMAND.words == ("show",)
    assert SHOW_COMMAND.usage == BiText("show ID", "show ID")
    assert SHOW_COMMAND.help_line.render(Lang.EN) == SHOW_HELP[0]
    assert SHOW_COMMAND.help_line.render(Lang.ZH) == SHOW_HELP[1]
    assert SHOW_COMMAND.argument == Argument(Message("ID", "ID"))
    assert SHOW_COMMAND.options == ("--servings",)
    assert SHOW_COMMAND.folder is FolderUse.READ


def test_f09_t01_the_list_command_runs_in_the_context_language_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1: the fields, four runs, and the help of four commands and of all."""
    home = make_home(tmp_path)
    _check_list_fields()
    tag = Arguments((), (("--tag", "素"),))
    assert run_command(
        LIST_COMMAND, Lang.EN, example_folder, Arguments(), OTHER, today=LATER
    ) == out(LIST)
    assert run_command(LIST_COMMAND, Lang.EN, example_folder, tag, OTHER, today=LATER) == out(VEG)
    quick = Arguments((), (("--tag", "quick"),))
    assert run_command(LIST_COMMAND, Lang.ZH, example_folder, quick) == out(QUICK_ZH)
    mapo_mistake(example_folder.root)
    assert run_command(LIST_COMMAND, Lang.ZH, example_folder, Arguments()) == stop(E_MAPO, ZH)
    english = call(home, ["--help"], commands=FOUR_COMMANDS)
    assert english == out(HELP)
    assert call(home, ["--help", "--lang", "zh"], commands=FOUR_COMMANDS) == out(HELP_ZH)
    _check_real_help(home, ["--help"], LIST_HELP[0], SHOW_HELP[0])
    _check_real_help(home, ["--help", "--lang", "zh"], LIST_HELP[1], SHOW_HELP[1])


def _raises(folder: DataFolder, arguments: Arguments) -> UsageError:
    """Runs ``show`` for arguments that must raise, and checks that both streams stay empty."""
    context, output, error = new_context(EN, folder)
    with pytest.raises(UsageError) as caught:
        SHOW_COMMAND.run(context, arguments)
    assert (output.getvalue(), error.getvalue()) == ("", "")
    return caught.value


def test_f09_t02_the_show_command_writes_the_recipe_and_raises_before_it_writes(
    example_folder: DataFolder,
) -> None:
    """The example of 2.3: the fields, the runs, the raises, and the settings that it ignores."""
    _check_show_fields()
    rice = Arguments(("rice",))
    assert run_command(SHOW_COMMAND, Lang.EN, example_folder, rice, Settings(servings=4)) == out(
        RICE
    )
    three = Arguments(("rice",), (("--servings", "3"),))
    assert run_command(SHOW_COMMAND, Lang.EN, example_folder, three) == out(RICE_FOR_3)
    _raises(example_folder, Arguments(("Mapo",)))
    _raises(example_folder, Arguments(("rice",), (("--servings", "0"),)))
    tomato = Arguments(("tomato-egg",))
    four = Arguments(("tomato-egg",), (("--servings", "4"),))
    mapo = Arguments(("mapo",))
    args = (tomato, four, mapo)
    results = [
        run_command(SHOW_COMMAND, Lang.ZH, example_folder, each, OTHER_EN, today=LATER)
        for each in args
    ]
    assert results == [out(TOMATO_ZH), out(FOUR_ZH), err(1, [MAPO_ZH])]


def test_f09_t03_a_wrong_servings_or_id_raises_before_a_file_is_read(
    tmp_path: Path, default_int_limit: None
) -> None:
    """Both checks come before any read, in order, and the error holds the typed text."""
    folder = DataFolder(tmp_path / "missing")
    with faults(tmp_path) as state:
        for value in WRONG_IDS:
            error = _raises(folder, Arguments((value,)))
            assert error.text(EN) == not_a_recipe_id(value)
            assert error.text(ZH) == not_a_recipe_id(value, ZH)
            assert (error.hint, error.values) == (None, (("id", value),))
        for servings in WRONG_SERVINGS:
            error = _raises(folder, Arguments(("rice",), (("--servings", servings),)))
            assert error.text(EN) == servings_not_1_to_100(servings)
            assert error.text(ZH) == servings_not_1_to_100(servings, ZH)
            assert (error.hint, error.values) == (None, (("servings", servings),))
        both = _raises(folder, Arguments(("Mapo",), (("--servings", "0"),)))
        assert both.text(EN) == servings_not_1_to_100("0")
        assert both.text(ZH) == servings_not_1_to_100("0", ZH)
        assert (both.hint, both.values) == (None, (("servings", "0"),))
        assert (state.calls, state.listings) == ([], [])
        for value in ("1", "9", "10", "100"):
            arguments = Arguments(("rice",), (("--servings", value),))
            assert run_command(SHOW_COMMAND, Lang.EN, folder, arguments) == stop(E_NO_CATALOG)
        long_id = Arguments(("9" * 5000,))
        assert run_command(SHOW_COMMAND, Lang.EN, folder, long_id) == stop(E_NO_CATALOG)
