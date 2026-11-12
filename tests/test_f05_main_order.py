"""Tests of F05 for main: the order of the steps and the rules for --lang and --data.

These are T26 and T27.
"""

from pathlib import Path

from f05_support import VERSION_LINE, go, in_folder, make_folder, make_home
from f05_texts import COMMANDS_EN, HELP_EN, OPTIONS_EN, OPTIONS_ZH, Result, err_result
from recipe_menu.datafile import DataFolder

LANG_FR = '--lang must be en or zh, not "fr".'


def _check(home: Path, argv: tuple[str, ...], expected: Result, environ: dict[str, str]) -> None:
    """Runs a line and checks its result and that no stand-in ran."""
    result, kit = go(home, *argv, environ=environ)
    assert result == expected, argv
    assert kit.nothing_ran(), argv


def test_f05_t26_the_first_step_that_finds_a_mistake_gives_the_error(tmp_path: Path) -> None:
    """Step 4 comes before the help and the version, which come before the command."""
    home = make_home(tmp_path)
    missing = make_folder(tmp_path, "missing")
    bare = make_folder(tmp_path, "bare")
    broken_zh = make_folder(tmp_path, "broken_zh")
    lang_fr = err_result(2, LANG_FR, OPTIONS_EN)
    no_data = err_result(2, "--data needs a value.", OPTIONS_EN)
    no_lang = err_result(2, "--lang needs a value.", OPTIONS_EN)
    one_option = '"list" has no option "--tags". Its own option is "--tag".'
    too_few = 'An argument is missing. Write "recipe-menu show ID".'
    cases = [
        (("cook", "--lang", "fr"), lang_fr),
        (("cook", "--data"), no_data),
        (("--help", "--lang", "fr"), lang_fr),
        (("--help", "--lang"), no_lang),
        (
            ("--version", "--data", str(missing), "--data", str(bare)),
            err_result(2, "--data is given twice.", OPTIONS_EN),
        ),
        (("--lang", "--help"), no_lang),
        (("--help", "cook"), (0, HELP_EN, "")),
        (("--version", "list", "--tags", "x", "extra"), (0, VERSION_LINE, "")),
        (("cook", "--tags", "x"), err_result(2, 'Unknown command "cook".', COMMANDS_EN)),
        (("list", "--tags", "x", "extra"), err_result(2, one_option, OPTIONS_EN)),
        (("show",), err_result(2, too_few, COMMANDS_EN)),
        (("list", "--lang", "fr", "--data"), lang_fr),
        (("list", "--data", "--lang", "fr"), no_data),
    ]
    for argv, expected in cases:
        _check(home, argv, expected, {})
    _check(home, ("show",), err_result(2, too_few, COMMANDS_EN), in_folder(broken_zh))


def test_f05_t27_lang_and_data_pick_the_first_value_and_reject_a_second(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """The first --lang and --data with a value count, and a later one is given twice."""
    home = make_home(tmp_path)
    zh = make_folder(tmp_path, "zh")
    bare = make_folder(tmp_path, "bare")
    needs_lang = err_result(2, "--lang 后面要写一个值。", OPTIONS_ZH)
    needs_data = err_result(2, "--data 后面要写一个值。", OPTIONS_ZH)
    twice_lang = err_result(2, "--lang 写了两次。", OPTIONS_ZH)
    lang_fr_zh = err_result(2, "--lang 必须是 en 或 zh，不能是“fr”。", OPTIONS_ZH)
    cases = [
        (("list", "--lang", "--lang", "zh"), {}, needs_lang),
        (("list", "--lang", "zh", "--lang", "fr"), {}, twice_lang),
        (("list", "--lang", "fr", "--lang", "zh"), in_folder(zh), lang_fr_zh),
        (
            ("list", "--lang", "fr", "--lang", "zh"),
            in_folder(example_folder.root),
            err_result(2, LANG_FR, OPTIONS_EN),
        ),
        (("list", "--lang", "zh", "--lang"), {}, needs_lang),
        (("list", "--lang", "zh", "--lang", "zh"), {}, twice_lang),
        (
            ("list", "--lang", "en", "--lang", "en"),
            {},
            err_result(2, "--lang is given twice.", OPTIONS_EN),
        ),
        (
            ("list", "--data", str(bare), "--data", str(bare)),
            {},
            err_result(2, "--data is given twice.", OPTIONS_EN),
        ),
        (("list", "--data"), in_folder(zh), needs_data),
        (("list", "--data", "--data", str(zh)), {}, needs_data),
        (("list", "--data", str(zh), "--data", str(example_folder.root)), {}, _data_twice()),
        (("--help", "--help"), {}, (0, HELP_EN, "")),
        (("--version", "--version"), {}, (0, VERSION_LINE, "")),
        (("--help", "--version", "--help"), {}, (0, HELP_EN, "")),
    ]
    for argv, environ, expected in cases:
        _check(home, argv, expected, environ)
    needs = err_result(2, "--lang needs a value.", OPTIONS_EN)
    _check(home, ("list", "--lang", ""), needs, {})
    for value in (" ", "EN", " zh", "-x", "中文"):
        expected = err_result(2, f'--lang must be en or zh, not "{value}".', OPTIONS_EN)
        _check(home, ("list", "--lang", value), expected, {})


def _data_twice() -> Result:
    """Gives the Chinese result of ``OPTION_TWICE`` for ``--data``."""
    return err_result(2, "--data 写了两次。", OPTIONS_ZH)
