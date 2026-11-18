"""Tests of F14 for MENU_SUGGEST_COMMAND: its fields, its help, and its run as a unit (T01, T02)."""

import io
from datetime import date
from pathlib import Path
from random import Random

import pytest

from f03_support import write
from f05_support import TODAY, make_home
from f05_texts import lines_text
from f07_support import call
from f09_support import made
from f11_texts import not_a_week
from f13_support import pristine, shop_faults
from f14_support import (
    EXAMPLE_IDS,
    WEEK_48,
    FrontSource,
    filled,
    new_menu,
    one_each,
    picks,
    seeded,
    stamp,
    w47_filled,
)
from f14_texts import HELP_14, HELP_14_ZH, first, some, some_zh
from recipe_menu.app import Argument, Arguments, Command, Context, FolderUse, UsageError
from recipe_menu.cli import main
from recipe_menu.commands.suggest import MENU_SUGGEST_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message, display_width
from v01_commands import V01_COMMANDS

DINNER_ONLY = Settings(Lang.EN, (Meal.DINNER,), 2)
RUN = MENU_SUGGEST_COMMAND.run


def _check_fields() -> None:
    """Checks the fields of ``MENU_SUGGEST_COMMAND``."""
    assert MENU_SUGGEST_COMMAND.words == ("menu", "suggest")
    assert MENU_SUGGEST_COMMAND.usage == BiText("menu suggest [WEEK]", "menu suggest [周]")
    assert MENU_SUGGEST_COMMAND.help_line.render(Lang.EN) == "Fill the empty meals of a week menu."
    assert MENU_SUGGEST_COMMAND.help_line.render(Lang.ZH) == "给一个周菜单的空餐填上菜。"
    assert MENU_SUGGEST_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
    assert MENU_SUGGEST_COMMAND.options == ("--tag",)
    assert MENU_SUGGEST_COMMAND.folder is FolderUse.READ


def _nine_commands() -> list[Command]:
    """Gives the eight commands of v0.1 with the new one after ``menu show``."""
    after = next(i for i, c in enumerate(V01_COMMANDS) if c.words == ("menu", "show")) + 1
    return [*V01_COMMANDS[:after], MENU_SUGGEST_COMMAND, *V01_COMMANDS[after:]]


def _help_lines(home: Path, *argv: str) -> list[str]:
    """Runs ``main`` with the nine commands and gives the lines of its help."""
    output = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=TODAY,
        stdout=output,
        stderr=io.StringIO(),
        commands=_nine_commands(),
    )
    assert code == 0
    return output.getvalue().splitlines()


def _check_example_run(example: DataFolder) -> tuple[Path, bytes]:
    """Runs the example of 2.1 up to its call that raises, and gives the file and its bytes."""
    file = example.menu_file(WEEK_48)
    write(file, f'week = "{WEEK_48}"\n' + "".join(f"\n[{day.value}]\ndinner = []\n" for day in Day))
    out, err = io.StringIO(), io.StringIO()
    context = Context(Lang.EN, example, DINNER_ONLY, out, err, TODAY, seeded(7))
    assert RUN(context, Arguments((WEEK_48,))) == 0
    assert out.getvalue() == lines_text(*first(WEEK_48, 7))
    assert err.getvalue() == ""
    chosen = picks(7, EXAMPLE_IDS, 7)
    ids = frozenset(EXAMPLE_IDS)
    menu, problems = read_week_menu(example, IsoWeek(2026, 48), DINNER_ONLY, ids)
    assert problems == ()
    assert menu is not None
    assert [slot.dishes for slot in menu.slots] == [(Dish(pick, 2),) for pick in chosen]
    lines = file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == f'week = "{WEEK_48}"'
    assert [line for line in lines if line.startswith("dinner")] == [
        f'dinner = ["{pick}"]' for pick in chosen
    ]
    return file, file.read_bytes()


def _check_the_wrong_week(example: DataFolder, file: Path, written: bytes) -> None:
    """Runs the call of the example that raises, with new streams."""
    out, err = io.StringIO(), io.StringIO()
    context = Context(Lang.EN, example, DINNER_ONLY, out, err, TODAY, seeded(7))
    with pytest.raises(UsageError) as caught:
        RUN(context, Arguments(("2026-W99",)))
    assert caught.value.text(Lang.EN) == not_a_week("2026-W99")
    assert caught.value.hint is None
    assert (out.getvalue(), err.getvalue()) == ("", "")
    assert file.read_bytes() == written


def _check_help_of_nine(home: Path) -> None:
    """Checks the help of the nine commands in both languages and its lines of the example."""
    english = _help_lines(home, "--help")
    assert len(english) == 22
    assert english[11:14] == [
        "  menu show [WEEK]      Show a week menu.",
        "  menu suggest [WEEK]   Fill the empty meals of a week menu.",
        "  shop [WEEK]           Make the shopping list of a week menu.",
    ]
    assert english[16].startswith("  --lang en|zh          The language of the output.")
    chinese = _help_lines(home, "--help", "--lang", "zh")
    assert chinese[12] == "  menu suggest [周]     给一个周菜单的空餐填上菜。"
    assert english == HELP_14
    assert chinese == HELP_14_ZH


def _text_column(line: str, text: str) -> int:
    """Gives the display width of what comes before the text at the end of a help line."""
    assert line.endswith(text), (line, text)
    return display_width(line[: len(line) - len(text)])


def _check_real_help(home: Path, argv: list[str], spec: tuple[str, str, str, str]) -> None:
    """Checks the line of ``menu suggest`` in the help of the real ``COMMANDS``."""
    show_head, suggest_head, suggest_text, lang_text = spec
    code, text, error = call(home, argv)
    assert (code, error) == (0, "")
    lines = text.split("\n")
    at = next(index for index, line in enumerate(lines) if line.startswith(show_head))
    line = lines[at + 1]
    assert line.startswith(suggest_head)
    lang_line = next(item for item in lines if item.startswith("  --lang en|zh"))
    assert _text_column(line, suggest_text) == _text_column(lang_line, lang_text)


def test_f14_t01_the_command_fills_the_dinners_and_the_help_lists_it_after_menu_show(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.1, the help of nine commands, and the help of the real commands."""
    home = make_home(tmp_path)
    _check_fields()
    file, written = _check_example_run(example_folder)
    _check_the_wrong_week(example_folder, file, written)
    _check_help_of_nine(home)
    english = (
        "  menu show [WEEK] ",
        "  menu suggest [WEEK] ",
        "Fill the empty meals of a week menu.",
    )
    chinese = ("  menu show [周] ", "  menu suggest [周] ", "给一个周菜单的空餐填上菜。")
    _check_real_help(
        home,
        ["--help"],
        (*english, "The language of the output. Default: the settings, else English."),
    )
    _check_real_help(
        home,
        ["--help", "--lang", "zh"],
        (*chinese, "输出语言。默认：设置里的语言，否则英文。"),
    )


def _context(
    lang: Lang, folder: DataFolder, settings: Settings, today: date, source: Random | None = None
) -> tuple[Context, io.StringIO, io.StringIO]:
    """Makes a ``Context`` with new streams, with no generator when ``source`` is ``None``."""
    out, err = io.StringIO(), io.StringIO()
    if source is None:
        return Context(lang, folder, settings, out, err, today), out, err
    return Context(lang, folder, settings, out, err, today, source), out, err


def _check_dishes_of_a_meal(example: DataFolder) -> None:
    """Input 1: the language of the context, the dishes of the settings, and the week of today."""
    new_menu(WEEK_48, [Meal.DINNER])(example.root)
    source = FrontSource()
    settings = Settings(Lang.EN, (Meal.DINNER,), 3, (1, 1, 2))
    context, out, err = _context(Lang.ZH, example, settings, date(2026, 11, 24), source)
    assert RUN(context, Arguments(())) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(*some_zh(WEEK_48, 3, 7, 0, "few")), "")
    assert source.calls == [(list(EXAMPLE_IDS), 7)]
    fills = [["choy-sum", "cola-wings"], ["mapo-tofu", "red-braised-pork"], ["rice", "tomato-egg"]]
    assert example.menu_file(WEEK_48).read_bytes() == filled(WEEK_48, [Meal.DINNER], fills)


def _check_next_week_twice(folder: DataFolder) -> FrontSource:
    """Inputs 2 and 3: ``next``, the language of the context, and a second call with no state."""
    source = FrontSource()
    settings = Settings(Lang.ZH)
    context, out, err = _context(Lang.EN, folder, settings, TODAY, source)
    assert RUN(context, Arguments(("next",))) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(*some("2026-W47", 1, 10, 4, "left")), "")
    assert source.calls == [(["red-braised-pork"], 1)]
    file = folder.menu_file("2026-W47")
    assert file.read_bytes() == w47_filled()
    before = stamp(file)
    context, out, err = _context(Lang.EN, folder, settings, TODAY, source)
    assert RUN(context, Arguments(("next",))) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(*some("2026-W47", 0, 9, 5, "left")), "")
    assert source.calls[1:] == [([], 0)]
    assert stamp(file) == before
    return source


def _check_default_generator(folder: DataFolder) -> None:
    """Input 4: a context with no generator holds a new ``Random(0)``."""
    new_menu(WEEK_48, [Meal.DINNER])(folder.root)
    context, out, err = _context(Lang.EN, folder, Settings(Lang.EN, (Meal.DINNER,), 2), TODAY)
    assert RUN(context, Arguments((WEEK_48,))) == 0
    assert (out.getvalue(), err.getvalue()) == (lines_text(*first(WEEK_48, 7)), "")
    expected = filled(WEEK_48, [Meal.DINNER], one_each(picks(0, EXAMPLE_IDS, 7)))
    assert folder.menu_file(WEEK_48).read_bytes() == expected


def _check_wrong_week_first(folder: DataFolder, source: FrontSource) -> None:
    """Input 5: a value that is not a week raises before the disk is touched."""
    context, out, err = _context(Lang.EN, folder, Settings(Lang.ZH), TODAY, source)
    with shop_faults(folder.root) as state, pytest.raises(UsageError) as caught:
        RUN(context, Arguments(("2026-W99",)))
    assert caught.value.text(Lang.EN) == not_a_week("2026-W99")
    assert caught.value.hint is None
    assert (out.getvalue(), err.getvalue()) == ("", "")
    assert (state.calls, state.listings) == ([], [])
    assert len(source.calls) == 2


def test_f14_t02_run_takes_the_week_the_meals_and_the_dishes_from_its_context(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five inputs: dishes of a meal, ``next`` twice, the default generator, and a wrong week."""
    source = pristine(example_folder, tmp_path)
    _check_dishes_of_a_meal(example_folder)
    folder = DataFolder(made(source, tmp_path, "f"))
    used = _check_next_week_twice(folder)
    _check_default_generator(DataFolder(made(source, tmp_path, "g")))
    _check_wrong_week_first(folder, used)
