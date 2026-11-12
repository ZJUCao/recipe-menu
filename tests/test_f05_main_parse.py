"""Tests of F05 for main: reading the line, the command, its options, and its values.

These are T21 to T25.
"""

from pathlib import Path

from f05_support import V01, StandIns, go, in_folder, make_home
from f05_texts import COMMANDS_EN, COMMANDS_ZH, EN, OPTIONS_EN, ZH, err_result
from recipe_menu.app import Arguments
from recipe_menu.datafile import DataFolder

TAG = "--tag"


def test_f05_t21_options_and_words_come_in_any_order(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """The command gets its own options and its values, and never a global option."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    cases = [
        (("--lang", "zh", "list", TAG, "素"), "LIST", ZH, Arguments((), ((TAG, "素"),))),
        (
            ("show", "tomato-egg", "--servings", "4"),
            "SHOW",
            EN,
            Arguments(("tomato-egg",), (("--servings", "4"),)),
        ),
        (
            ("show", "--servings", "4", "tomato-egg"),
            "SHOW",
            EN,
            Arguments(("tomato-egg",), (("--servings", "4"),)),
        ),
        (("search", "番茄", "quick"), "SEARCH", EN, Arguments(("番茄", "quick"))),
        (("menu", "--lang", "zh", "show", "2026-W47"), "MENU_SHOW", ZH, Arguments(("2026-W47",))),
        (("menu", "new"), "MENU_NEW", EN, Arguments()),
        (("search", "-x"), "SEARCH", EN, Arguments(("-x",))),
        (("list", TAG, "show"), "LIST", EN, Arguments((), ((TAG, "show"),))),
        (("show", ""), "SHOW", EN, Arguments(("",))),
    ]
    for argv, name, lang, arguments in cases:
        result, kit = go(home, *argv, environ=env)
        assert result == (0, "", ""), argv
        context, got = kit.ran(name)
        assert (context.lang, got) == (lang, arguments), argv
    result, kit = go(home, "--data", str(example_folder.root), "list", "--lang", "en")
    assert result == (0, "", "")
    context, got = kit.ran("LIST")
    assert (context.lang, got) == (EN, Arguments())


def test_f05_t22_an_option_of_a_command_needs_one_value_and_comes_once(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """A missing value, an empty value, or a second value is an error with no hint."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    needs = err_result(2, "--tag needs a value.")
    twice = err_result(2, "--tag is given twice.")
    cases = [
        (("list", TAG), needs),
        (("list", TAG, ""), needs),
        (("list", TAG, "--lang", "zh"), err_result(2, "--tag 后面要写一个值。")),
        (
            ("--tag", "list"),
            err_result(2, 'Name a command, such as "recipe-menu list".', COMMANDS_EN),
        ),
        (("list", TAG, "a", TAG, "b"), twice),
        (("list", TAG, "a", TAG, "a"), twice),
        (("list", TAG, "a", TAG), needs),
        (("show", "--servings"), err_result(2, "--servings needs a value.")),
    ]
    for argv, expected in cases:
        result, kit = go(home, *argv, environ=env)
        assert result == expected, argv
        assert kit.nothing_ran(), argv
    for value in (" ", "-"):
        result, kit = go(home, "list", TAG, value, environ=env)
        assert result == (0, "", ""), value
        assert_arguments(kit, Arguments((), ((TAG, value),)))


def assert_arguments(kit: StandIns, arguments: Arguments) -> None:
    """Checks that ``LIST`` ran once, in English, with the arguments."""
    context, got = kit.ran("LIST")
    assert context.lang is EN
    assert got == arguments


def test_f05_t23_the_command_is_found_in_the_words(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """No word, an unknown word, and a first word that needs a second one."""
    home = make_home(tmp_path)
    no_command = 'Name a command, such as "recipe-menu list".'
    no_command_zh = "请写上一个命令，比如“recipe-menu list”。"
    plain = [
        ((), err_result(2, no_command, COMMANDS_EN)),
        (("--lang", "zh"), err_result(2, no_command_zh, COMMANDS_ZH)),
        (("--data", str(example_folder.root)), err_result(2, no_command, COMMANDS_EN)),
    ]
    for argv, expected in plain:
        result, kit = go(home, *argv)
        assert result == expected, argv
        assert kit.nothing_ran()
    unknown = [
        (("cook",), "cook"),
        (("cook", "tomato-egg"), "cook"),
        (("List",), "List"),
        (("lis",), "lis"),
        (("new",), "new"),
        (("",), ""),
        (("menu", "cook"), "menu cook"),
        (("menu", "cook", "show"), "menu cook"),
    ]
    for argv, command in unknown:
        result, kit = go(home, *argv)
        assert result == err_result(2, f'Unknown command "{command}".', COMMANDS_EN), argv
        assert kit.nothing_ran()


def test_f05_t23_incomplete_and_unknown_two_word_commands(tmp_path: Path) -> None:
    """A first word of two-word commands lists them in the order of commands."""
    home = make_home(tmp_path)
    more = 'The commands that start with "menu" are "menu new" and "menu show".'
    cases = [
        (V01, ("menu",), err_result(2, more, COMMANDS_EN)),
        (
            ("MENU_SHOW", "MENU_NEW"),
            ("menu",),
            err_result(
                2,
                'The commands that start with "menu" are "menu show" and "menu new".',
                COMMANDS_EN,
            ),
        ),
        (
            ("LIST", "MENU_SHOW"),
            ("menu",),
            err_result(2, 'The only command that starts with "menu" is "menu show".', COMMANDS_EN),
        ),
        (("LIST", "MENU_SHOW"), ("show",), err_result(2, 'Unknown command "show".', COMMANDS_EN)),
        (
            (*V01, "MENU_SUGGEST"),
            ("menu",),
            err_result(
                2,
                'The commands that start with "menu" are "menu new", "menu show", '
                'and "menu suggest".',
                COMMANDS_EN,
            ),
        ),
        (
            (*V01, "MENU_SUGGEST"),
            ("menu", "--lang", "zh"),
            err_result(
                2,
                "以“menu”开头的命令有“menu new”、“menu show”和“menu suggest”。",
                COMMANDS_ZH,
            ),
        ),
    ]
    for names, argv, expected in cases:
        result, kit = go(home, *argv, names=names)
        assert result == expected, (names, argv)
        assert kit.nothing_ran()


def test_f05_t24_an_option_that_the_command_does_not_declare(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """UNKNOWN_OPTION has three forms, and the option is quoted as the line writes it."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    none = "It has no options of its own."
    one = 'Its own option is "--tag".'
    cases = [
        (V01, ("init", TAG, "x"), "init", TAG, none),
        (V01, ("menu", "show", TAG, "x"), "menu show", TAG, none),
        (V01, ("list", "--tags", "素"), "list", "--tags", one),
        (V01, ("list", "--lang=zh"), "list", "--lang=zh", one),
        (V01, ("list", "--lan", "zh"), "list", "--lan", one),
        (V01, ("list", "--"), "list", "--", one),
        (V01, ("list", "--Tag", "素"), "list", "--Tag", one),
        (V01, ("list", "--x", "1", "--y", "2"), "list", "--x", one),
        (
            ("SHOW_TWO",),
            ("show", "x", "--serving", "4"),
            "show",
            "--serving",
            'Its own options are "--servings" and "--tag".',
        ),
        (
            ("SHOW_THREE",),
            ("show", "x", "--serving", "4"),
            "show",
            "--serving",
            'Its own options are "--tag", "--servings", and "--week".',
        ),
    ]
    for names, argv, command, option, tail in cases:
        result, kit = go(home, *argv, environ=env, names=names)
        first = f'"{command}" has no option "{option}". {tail}'
        assert result == err_result(2, first, OPTIONS_EN), argv
        assert kit.nothing_ran()
    result, kit = go(home, "list", "-l", "zh", environ=env)
    assert result == err_result(
        2, 'Unexpected argument "-l". Write "recipe-menu list".', COMMANDS_EN
    )
    assert kit.nothing_ran()
    data = str(example_folder.root)
    result, kit = go(home, "init", "--lang", "zh", "--data", data)
    assert result == (0, "", "")
    context, arguments = kit.ran("INIT")
    assert (context.lang, arguments) == (ZH, Arguments())
    result, kit = go(home, "check", "--lang", "en", "--data", data)
    assert result == (0, "", "")
    context, arguments = kit.ran("CHECK")
    assert (context.lang, arguments) == (EN, Arguments())


def test_f05_t25_the_number_of_values_of_the_argument(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """Too few and too many values, for each form of an argument and for no argument."""
    home = make_home(tmp_path)
    env = in_folder(example_folder.root)
    names = (*V01, "TAGS")

    def error(first: str, usage: str) -> tuple[int, str, str]:
        """Gives the result of a usage error with its hint."""
        return err_result(2, f'{first} Write "recipe-menu {usage}".', COMMANDS_EN)

    missing = "An argument is missing."
    errors = [
        (("show",), error(missing, "show ID")),
        (("show", "a", "b", "c"), error('Unexpected argument "b".', "show ID")),
        (
            ("menu", "new", "2026-W47", "2026-W48"),
            error('Unexpected argument "2026-W48".', "menu new [WEEK]"),
        ),
        (("search",), error(missing, "search WORD...")),
        (("list", "x"), error('Unexpected argument "x".', "list")),
        (("init", "a", "b"), error('Unexpected argument "a".', "init")),
    ]
    for argv, expected in errors:
        result, kit = go(home, *argv, environ=env, names=names)
        assert result == expected, argv
        assert kit.nothing_ran()
    runs = [
        (("show", "a"), "SHOW", ("a",)),
        (("menu", "new"), "MENU_NEW", ()),
        (("menu", "new", "2026-W47"), "MENU_NEW", ("2026-W47",)),
        (("search", "a"), "SEARCH", ("a",)),
        (("search", "a", "b", "c"), "SEARCH", ("a", "b", "c")),
        (("tags",), "TAGS", ()),
        (("tags", "a"), "TAGS", ("a",)),
        (("tags", "a", "b", "c", "d", "e"), "TAGS", ("a", "b", "c", "d", "e")),
        (("list",), "LIST", ()),
    ]
    for argv, name, values in runs:
        result, kit = go(home, *argv, environ=env, names=names)
        assert result == (0, "", ""), argv
        assert kit.ran(name)[1] == Arguments(values), argv
    result, _ = go(home, "show", "--lang", "zh", environ=env)
    assert result == err_result(2, "缺少参数。请写成“recipe-menu show ID”。", COMMANDS_ZH)
    result, _ = go(home, "menu", "new", "a", "b", "--lang", "zh", environ=env)
    assert result == err_result(
        2, "多余的参数“b”。请写成“recipe-menu menu new [周]”。", COMMANDS_ZH
    )
