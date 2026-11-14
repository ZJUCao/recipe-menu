"""Tests of F10 for SEARCH_COMMAND, its fields, its help line, and its check of words (T01, T02)."""

from datetime import date
from pathlib import Path

from f05_support import make_home
from f07_changes import mapo_mistake
from f07_support import call
from f08_support import faults
from f09_support import new_context, run_command
from f09_texts import E_MAPO, E_NO_CATALOG, EN, ZH, stop
from f10_support import EMPTY_WORDS, FINE_WORDS, raises_empty
from f10_texts import (
    EMPTY,
    EMPTY_ZH,
    HELP,
    HELP_ZH,
    PROTOTYPE_ZH,
    SCALLION_QUICK_TABLE,
    TOMATO,
    found,
    none,
    out,
)
from recipe_menu.app import Argument, Arguments, FolderUse
from recipe_menu.commands.browse import LIST_COMMAND, SHOW_COMMAND
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message, display_width

OTHER = Settings(Lang.ZH, (Meal.BREAKFAST,), 5)
LATER = date(2030, 1, 1)
FIVE_COMMANDS = (INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND)
HELP_LINE = ("Find recipes by name, ingredient, or tag.", "按名称、食材或标签找菜谱。")


def _check_fields() -> None:
    """Checks the fields of ``SEARCH_COMMAND``."""
    assert SEARCH_COMMAND.words == ("search",)
    assert SEARCH_COMMAND.usage == BiText("search WORD...", "search 词...")
    assert SEARCH_COMMAND.help_line.render(Lang.EN) == HELP_LINE[0]
    assert SEARCH_COMMAND.help_line.render(Lang.ZH) == HELP_LINE[1]
    assert SEARCH_COMMAND.argument == Argument(Message("WORD", "词"), repeats=True)
    assert SEARCH_COMMAND.options == ()
    assert SEARCH_COMMAND.folder is FolderUse.READ


def _check_runs(example: DataFolder) -> None:
    """Checks steps 1 to 3 of the case and the Chinese run of the example of 2.1.

    The runs of steps 1 to 3 use settings and a date that ``run`` ignores.
    """
    for words, expected in [
        (("番茄",), TOMATO),
        (("葱", "quick"), found(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')),
        (("lamb",), none('No recipe matches "lamb".')),
    ]:
        got = run_command(SEARCH_COMMAND, Lang.EN, example, Arguments(words), OTHER, today=LATER)
        assert got == expected, words
    zh = run_command(SEARCH_COMMAND, Lang.ZH, example, Arguments(("葱", "quick")))
    assert zh == PROTOTYPE_ZH


def _second_column(line: str) -> int:
    """Gives the index of the second column of a line of the help."""
    gap = line.index("  ", 2)
    return gap + len(line[gap:]) - len(line[gap:].lstrip(" "))


def _check_real_help(home: Path, argv: list[str], text: str, start: str) -> None:
    """Checks the line of ``search`` in the help of the real ``COMMANDS``."""
    code, shown, error = call(home, argv)
    assert (code, error) == (0, "")
    lines = shown.split("\n")
    show = next(index for index, line in enumerate(lines) if line.startswith("  show ID "))
    line = lines[show + 1]
    assert line.startswith(start)
    assert line.endswith(text)
    option = next(line for line in lines if line.startswith("  --lang en|zh"))
    assert display_width(line[: -len(text)]) == display_width(option[: _second_column(option)])


def test_f10_t01_the_search_command_runs_in_the_context_language_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1: the fields, the runs, the raise, and the help of five commands."""
    home = make_home(tmp_path)
    _check_fields()
    _check_runs(example_folder)
    error = raises_empty(example_folder, Lang.ZH, ("番茄", "\u3000"))
    assert error.text(EN) == EMPTY
    mapo_mistake(example_folder.root)
    result = run_command(SEARCH_COMMAND, Lang.ZH, example_folder, Arguments(("lamb",)))
    assert result == stop(E_MAPO, ZH)
    assert call(home, ["--help"], commands=FIVE_COMMANDS) == out(HELP)
    assert call(home, ["--help", "--lang", "zh"], commands=FIVE_COMMANDS) == out(HELP_ZH)
    _check_real_help(home, ["--help"], HELP_LINE[0], "  search WORD... ")
    _check_real_help(home, ["--help", "--lang", "zh"], HELP_LINE[1], "  search 词... ")


def test_f10_t02_run_checks_every_word_before_it_reads_a_file_or_writes_a_line(
    tmp_path: Path, default_int_limit: None
) -> None:
    """An empty matching form raises ``UsageError``, and any other word passes the check."""
    folder = DataFolder(tmp_path / "missing")
    with faults(tmp_path) as state:
        for words in EMPTY_WORDS:
            error = raises_empty(folder, Lang.EN, words)
            assert error.text(EN) == EMPTY, words
            assert error.text(ZH) == EMPTY_ZH, words
            assert (error.hint, error.values) == (None, ()), words
        assert (state.calls, state.listings) == ([], [])
        for words in FINE_WORDS:
            context, output, error_stream = new_context(Lang.EN, folder)
            code = SEARCH_COMMAND.run(context, Arguments(words))
            result = (code, output.getvalue(), error_stream.getvalue())
            assert result == stop(E_NO_CATALOG), words
