"""Tests of F11 for MENU_NEW_COMMAND, MENU_SHOW_COMMAND, NO_MENU, and the week (T01 to T04)."""

from datetime import date
from pathlib import Path

import pytest

from f05_support import make_home
from f06_support import MEALS_DINNER, m_unknown_meal
from f07_support import call
from f07_texts import Prob, p_slot
from f08_support import faults
from f09_support import at, new_context, run_command
from f09_texts import E_NO_CATALOG, EN, FOLDER_MISSING, ZH, err, out, stop
from f11_support import menu_text
from f11_texts import (
    BLOCK_D,
    DATES,
    EVERY_MEAL,
    HELP,
    HELP_ZH,
    LUNCH_DINNER,
    SHOW_47,
    exists,
    fail,
    new,
    new_zh,
    no_menu,
    no_menu_zh,
    not_a_week,
    not_a_week_zh,
)
from recipe_menu.app import Argument, Arguments, FolderUse, UsageError
from recipe_menu.commands.browse import LIST_COMMAND, SHOW_COMMAND
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.commands.menu import MENU_NEW_COMMAND, MENU_SHOW_COMMAND
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import NO_MENU
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message, display_width

SEVEN = (
    INIT_COMMAND,
    CHECK_COMMAND,
    LIST_COMMAND,
    SHOW_COMMAND,
    SEARCH_COMMAND,
    MENU_NEW_COMMAND,
    MENU_SHOW_COMMAND,
)
LATER = date(2030, 1, 1)
# The help lines of both commands: English, then Chinese.
HELP_LINES = (
    (
        "  search WORD... ",
        ("  menu new [WEEK] ", "Create an empty week menu."),
        ("  menu show [WEEK] ", "Show a week menu."),
        "The language of the output. Default: the settings, else English.",
    ),
    (
        "  search 词... ",
        ("  menu new [周] ", "创建一个空的周菜单。"),
        ("  menu show [周] ", "查看一个周菜单。"),
        "输出语言。默认：设置里的语言，否则英文。",
    ),
)


def _check_new_fields() -> None:
    """Checks the fields of ``MENU_NEW_COMMAND``."""
    assert MENU_NEW_COMMAND.words == ("menu", "new")
    assert MENU_NEW_COMMAND.usage == BiText("menu new [WEEK]", "menu new [周]")
    assert MENU_NEW_COMMAND.help_line.render(Lang.EN) == "Create an empty week menu."
    assert MENU_NEW_COMMAND.help_line.render(Lang.ZH) == "创建一个空的周菜单。"
    assert MENU_NEW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
    assert MENU_NEW_COMMAND.options == ()
    assert MENU_NEW_COMMAND.folder is FolderUse.READ


def _check_show_fields() -> None:
    """Checks the fields of ``MENU_SHOW_COMMAND``."""
    assert MENU_SHOW_COMMAND.words == ("menu", "show")
    assert MENU_SHOW_COMMAND.usage == BiText("menu show [WEEK]", "menu show [周]")
    assert MENU_SHOW_COMMAND.help_line.render(Lang.EN) == "Show a week menu."
    assert MENU_SHOW_COMMAND.help_line.render(Lang.ZH) == "查看一个周菜单。"
    assert MENU_SHOW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
    assert MENU_SHOW_COMMAND.options == ()
    assert MENU_SHOW_COMMAND.folder is FolderUse.READ


def _text_column(line: str, text: str) -> int:
    """Gives the display width of what comes before the text at the end of a help line."""
    assert line.endswith(text), (line, text)
    return display_width(line[: len(line) - len(text)])


def _check_real_help(home: Path, argv: list[str], spec: tuple) -> None:
    """Checks the two lines of the menu commands in the help of the real ``COMMANDS``.

    The line of ``menu new`` is found by its start after the line of ``search``.
    """
    search, (new_head, new_text), (show_head, show_text), lang_text = spec
    code, text, error = call(home, argv)
    assert (code, error) == (0, "")
    lines = text.split("\n")
    first = next(index for index, line in enumerate(lines) if line.startswith(search))
    found = next(
        index for index, line in enumerate(lines) if index > first and line.startswith(new_head)
    )
    new_line, show_line = lines[found], lines[found + 1]
    assert new_line.startswith(new_head)
    assert show_line.startswith(show_head)
    lang_line = next(line for line in lines if line.startswith("  --lang en|zh"))
    column = _text_column(lang_line, lang_text)
    assert _text_column(new_line, new_text) == column
    assert _text_column(show_line, show_text) == column


def _check_new_example(example: DataFolder, home: Path) -> None:
    """Runs the example of 2.1 up to its call that raises."""
    dinner = Settings(Lang.EN, (Meal.DINNER,), 2)
    arguments = Arguments(("next",))
    result = run_command(
        MENU_NEW_COMMAND, Lang.ZH, example, arguments, dinner, today=date(2026, 11, 17)
    )
    file = example.menu_file("2026-W48")
    assert result == out(new_zh(file, DATES["2026-W48"][1], "晚餐"))
    assert file.read_bytes() == menu_text("2026-W48", [Meal.DINNER])
    existing = example.menu_file("2026-W47")
    result = run_command(MENU_NEW_COMMAND, Lang.EN, example, Arguments(("2026-W47",)))
    assert result == (1, "", f"{exists(existing)}\n")
    assert call(home, ["--help"], commands=SEVEN) == out(HELP)
    assert call(home, ["--help", "--lang", "zh"], commands=SEVEN) == out(HELP_ZH)
    context, output, error = new_context(Lang.EN, example)
    with pytest.raises(UsageError):
        MENU_NEW_COMMAND.run(context, Arguments(("2026-W99",)))
    assert (output.getvalue(), error.getvalue()) == ("", "")
    names = sorted(path.name for path in example.menus.iterdir())
    assert names == ["2026-W47.toml", "2026-W48.toml"]


def test_f11_t01_the_menu_new_command_creates_the_file_and_the_help_lists_it(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1, then the runs of inputs 1 to 3, and the help of the seven commands."""
    home = make_home(tmp_path)
    _check_new_fields()
    assert len(HELP) == len(HELP_ZH) == 20
    _check_new_example(example_folder, home)
    every = Settings(Lang.ZH, tuple(Meal), 5)
    file = example_folder.menu_file("2026-W49")
    result = run_command(
        MENU_NEW_COMMAND, Lang.EN, example_folder, Arguments(("2026-W49",)), every, today=LATER
    )
    dates = DATES["2026-W49"][0]
    assert result == out(new(file, dates, "breakfast, lunch, and dinner"))
    assert file.read_bytes() == menu_text("2026-W49", EVERY_MEAL)
    file = example_folder.menu_file("2026-W53")
    result = run_command(
        MENU_NEW_COMMAND, Lang.EN, example_folder, Arguments(()), today=date(2026, 12, 30)
    )
    assert result == out(new(file, DATES["2026-W53"][0], "lunch and dinner"))
    assert file.read_bytes() == menu_text("2026-W53", LUNCH_DINNER)
    again = run_command(
        MENU_NEW_COMMAND, Lang.EN, example_folder, Arguments(()), today=date(2026, 12, 30)
    )
    assert again == (1, "", f"{exists(file)}\n")
    _check_real_help(home, ["--help"], HELP_LINES[0])
    _check_real_help(home, ["--help", "--lang", "zh"], HELP_LINES[1])


def _check_show_example(example: DataFolder) -> None:
    """Runs the example of 2.3 up to its call that raises."""
    arguments = Arguments(("next",))
    assert run_command(MENU_SHOW_COMMAND, Lang.EN, example, arguments) == out(SHOW_47)
    context, output, error = new_context(Lang.EN, example)
    with pytest.raises(UsageError):
        MENU_SHOW_COMMAND.run(context, Arguments(("this week",)))
    assert (output.getvalue(), error.getvalue()) == ("", "")


def test_f11_t02_the_menu_show_command_writes_the_week_and_keeps_no_state(
    example_folder: DataFolder,
) -> None:
    """The example of 2.3, then the runs of inputs 1 to 4."""
    _check_show_fields()
    _check_show_example(example_folder)
    every = Settings(Lang.ZH, tuple(Meal), 3)
    week = Arguments(("2026-W47",))
    result = run_command(MENU_SHOW_COMMAND, Lang.EN, example_folder, week, every, today=LATER)
    assert result == out(BLOCK_D)
    dinner = Settings(Lang.EN, (Meal.DINNER,), 5)
    saturday = Prob(
        "menus/2026-W47.toml",
        p_slot("saturday", "lunch"),
        m_unknown_meal("lunch", MEALS_DINNER),
    )
    this_week = Arguments(())
    result = run_command(
        MENU_SHOW_COMMAND, Lang.ZH, example_folder, this_week, dinner, today=date(2026, 11, 17)
    )
    assert result == stop(saturday, ZH)
    other = Arguments(("2026-W48",))
    result = run_command(MENU_SHOW_COMMAND, Lang.EN, example_folder, other)
    assert result == err(1, [no_menu("2026-W48")])
    for _ in range(2):
        again = run_command(MENU_SHOW_COMMAND, Lang.EN, example_folder, Arguments(("next",)))
        assert again == out(SHOW_47)


BAD_WEEKS = [
    "2026-W99",
    "Next",
    "THIS",
    "",
    " 2026-W47",
    "2026-W47\n",
    "2026-w47",
    "2026-W7",
    "2025-W53",
    "2026-W00",
    "this week",
    "\uff12\uff10\uff12\uff16-W47",
]
GOOD_WEEKS = [(), ("this",), ("next",), ("2026-W47",), ("2026-W53",), ("0001-W01",)]


def _check_wrong_week(command, folder: DataFolder, value: str) -> None:
    """Runs a command with a value that is not a week and checks the error and the streams."""
    context, output, error = new_context(EN, folder)
    with pytest.raises(UsageError) as caught:
        command.run(context, Arguments((value,)))
    assert (output.getvalue(), error.getvalue()) == ("", "")
    raised = caught.value
    assert raised.text(EN) == not_a_week(value)
    assert raised.text(ZH) == not_a_week_zh(value)
    assert (raised.hint, raised.values) == (None, (("week", value),))


def test_f11_t03_a_value_that_is_not_a_week_raises_before_the_disk_is_touched(
    tmp_path: Path,
) -> None:
    """Both commands raise ``UsageError`` for each wrong value, and pass each good one."""
    folder = DataFolder(tmp_path / "missing")
    with faults(tmp_path) as state:
        for command in (MENU_NEW_COMMAND, MENU_SHOW_COMMAND):
            for value in BAD_WEEKS:
                _check_wrong_week(command, folder, value)
        assert (state.calls, state.listings) == ([], [])
        menus = tmp_path / "missing" / "menus"
        for values in GOOD_WEEKS:
            arguments = Arguments(values)
            result = run_command(MENU_NEW_COMMAND, EN, folder, arguments)
            assert result == err(1, fail(menus, FOLDER_MISSING))
            assert run_command(MENU_SHOW_COMMAND, EN, folder, arguments) == stop(E_NO_CATALOG)
    assert not (tmp_path / "missing").exists()


def test_f11_t04_no_menu_is_one_line_for_a_week_with_no_menu_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 3.1, then ``menu show`` for two weeks in both languages."""
    home = make_home(tmp_path)
    assert NO_MENU.placeholders == frozenset({"week"})
    for week in ("2026-W48", "2027-W01"):
        english = NO_MENU.render(Lang.EN, week=week)
        chinese = NO_MENU.render(Lang.ZH, week=week)
        assert (english, chinese) == (no_menu(week), no_menu_zh(week))
        assert at(home, example_folder, "menu", "show", week) == (1, "", english + "\n")
        shown = at(home, example_folder, "menu", "show", week, "--lang", "zh")
        assert shown == (1, "", chinese + "\n")
