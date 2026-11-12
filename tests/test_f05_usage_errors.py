"""Tests of F05 for main: every row of the Errors table of 2.10, in both languages.

These are T28 and T29.
"""

from pathlib import Path

from f05_support import V01, go, in_folder, make_folder, make_home
from f05_texts import COMMANDS_EN, COMMANDS_ZH, OPTIONS_EN, OPTIONS_ZH, err_result
from recipe_menu.datafile import DataFolder

type Case = tuple[tuple[str, ...], dict[str, str], list[str]]


def _t28_items(bare: str, zh: dict[str, str], example: dict[str, str]) -> list[tuple[Case, Case]]:
    """Gives the English and the Chinese input of each item of T28."""
    return [
        (
            (("list", "--lang"), {}, ["--lang needs a value.", OPTIONS_EN]),
            (("list", "--lang", "--lang", "zh"), {}, ["--lang 后面要写一个值。", OPTIONS_ZH]),
        ),
        (
            (("list", "--data"), {}, ["--data needs a value.", OPTIONS_EN]),
            (("list", "--data", "--lang", "zh"), {}, ["--data 后面要写一个值。", OPTIONS_ZH]),
        ),
        (
            (("list", "--tag"), {}, ["--tag needs a value."]),
            (("list", "--tag", "--lang", "zh"), {}, ["--tag 后面要写一个值。"]),
        ),
        (
            (("list", "--lang", "en", "--lang", "en"), {}, ["--lang is given twice.", OPTIONS_EN]),
            (("list", "--lang", "zh", "--lang", "zh"), {}, ["--lang 写了两次。", OPTIONS_ZH]),
        ),
        (
            (("list", "--data", bare, "--data", bare), {}, ["--data is given twice.", OPTIONS_EN]),
            (
                ("list", "--data", bare, "--data", bare, "--lang", "zh"),
                {},
                ["--data 写了两次。", OPTIONS_ZH],
            ),
        ),
        (
            (
                ("show", "a", "--servings", "2", "--servings", "3"),
                {},
                ["--servings is given twice."],
            ),
            (
                ("show", "a", "--servings", "2", "--servings", "3", "--lang", "zh"),
                {},
                ["--servings 写了两次。"],
            ),
        ),
        (
            (
                ("list", "--lang", "fr"),
                example,
                ['--lang must be en or zh, not "fr".', OPTIONS_EN],
            ),
            (
                ("list", "--lang", "fr"),
                zh,
                ["--lang 必须是 en 或 zh，不能是“fr”。", OPTIONS_ZH],
            ),
        ),
    ]


def test_f05_t28_global_and_command_options_in_both_languages(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """Each error of an option, with its hint for --lang and --data and none for --tag."""
    home = make_home(tmp_path)
    bare = str(make_folder(tmp_path, "bare"))
    zh = in_folder(make_folder(tmp_path, "zh"))
    example = in_folder(example_folder.root)
    items = _t28_items(bare, zh, example)
    for pair in items:
        for argv, environ, lines in pair:
            result, kit = go(home, *argv, environ=environ)
            assert result == err_result(2, *lines), argv
            assert kit.nothing_ran(), argv


COMMAND_HINTS, OPTION_HINTS = (COMMANDS_EN, COMMANDS_ZH), (OPTIONS_EN, OPTIONS_ZH)
TWO = ("LIST", "MENU_SHOW")
ROWS = [
    (V01, (), COMMAND_HINTS, 'Name a command, such as "recipe-menu list".'),
    (V01, ("cook",), COMMAND_HINTS, 'Unknown command "cook".'),
    (V01, ("menu", "cook"), COMMAND_HINTS, 'Unknown command "menu cook".'),
    (
        TWO,
        ("menu",),
        COMMAND_HINTS,
        'The only command that starts with "menu" is "menu show".',
    ),
    (
        V01,
        ("menu",),
        COMMAND_HINTS,
        'The commands that start with "menu" are "menu new" and "menu show".',
    ),
    (
        V01,
        ("init", "--tag", "x"),
        OPTION_HINTS,
        '"init" has no option "--tag". It has no options of its own.',
    ),
    (
        V01,
        ("list", "--tags", "素"),
        OPTION_HINTS,
        '"list" has no option "--tags". Its own option is "--tag".',
    ),
    (
        ("SHOW_TWO",),
        ("show", "x", "--serving", "4"),
        OPTION_HINTS,
        '"show" has no option "--serving". Its own options are "--servings" and "--tag".',
    ),
    (
        V01,
        ("show",),
        COMMAND_HINTS,
        'An argument is missing. Write "recipe-menu show ID".',
    ),
    (
        V01,
        ("search",),
        COMMAND_HINTS,
        'An argument is missing. Write "recipe-menu search WORD...".',
    ),
    (
        V01,
        ("show", "a", "b"),
        COMMAND_HINTS,
        'Unexpected argument "b". Write "recipe-menu show ID".',
    ),
    (
        V01,
        ("menu", "new", "2026-W47", "2026-W48"),
        COMMAND_HINTS,
        'Unexpected argument "2026-W48". Write "recipe-menu menu new [WEEK]".',
    ),
]
CHINESE = [
    "请写上一个命令，比如“recipe-menu list”。",
    "未知命令“cook”。",
    "未知命令“menu cook”。",
    "以“menu”开头的命令只有“menu show”。",
    "以“menu”开头的命令有“menu new”和“menu show”。",
    "“init”没有选项“--tag”。它没有自己的选项。",
    "“list”没有选项“--tags”。它自己的选项是“--tag”。",
    "“show”没有选项“--serving”。它自己的选项有“--servings”和“--tag”。",
    "缺少参数。请写成“recipe-menu show ID”。",
    "缺少参数。请写成“recipe-menu search 词...”。",
    "多余的参数“b”。请写成“recipe-menu show ID”。",
    "多余的参数“2026-W48”。请写成“recipe-menu menu new [周]”。",
]


def test_f05_t29_command_errors_in_both_languages_with_their_hints(tmp_path: Path) -> None:
    """Each error of the command, as written and with --lang zh, with its hint."""
    home = make_home(tmp_path)
    for (names, argv, hints, english), zh in zip(ROWS, CHINESE, strict=True):
        result, kit = go(home, *argv, names=names)
        assert result == err_result(2, english, hints[0]), argv
        assert kit.nothing_ran(), argv
        result, kit = go(home, *argv, "--lang", "zh", names=names)
        assert result == err_result(2, zh, hints[1]), argv
        assert kit.nothing_ran(), argv
