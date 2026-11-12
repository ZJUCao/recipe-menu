"""Tests of F05 for main: the language of a command and of a mistake (T33 and T34)."""

from pathlib import Path

from f05_support import go, in_folder, make_folder, make_home, make_settings_folder
from f05_texts import COMMANDS_EN, COMMANDS_ZH, EN, HELP_EN, HELP_ZH, ZH, err_result
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang


def _lang(home: Path, name: str, *argv: str, environ: dict[str, str]) -> Lang:
    """Runs a line and gives the language that the stand-in called ``name`` got."""
    result, kit = go(home, *argv, environ=environ)
    assert result == (0, "", ""), argv
    context, _ = kit.ran(name)
    return context.lang


def test_f05_t33_a_command_speaks_lang_then_the_settings_then_english(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """Settings with an error give no language, and no data folder gives no settings."""
    home = make_home(tmp_path)
    example = in_folder(example_folder.root)
    zh = in_folder(make_folder(tmp_path, "zh"))
    lunch = in_folder(make_settings_folder(tmp_path, "lunch", 'meals = ["lunch"]\n'))
    broken_zh = in_folder(make_folder(tmp_path, "broken_zh"))
    bare = in_folder(make_folder(tmp_path, "bare"))
    cases = [
        ("LIST", ("list",), example, EN),
        ("LIST", ("list", "--lang", "zh"), example, ZH),
        ("LIST", ("list",), zh, ZH),
        ("LIST", ("list", "--lang", "en"), zh, EN),
        ("LIST", ("list",), lunch, EN),
        ("LIST", ("list", "--lang", "zh"), lunch, ZH),
        ("CHECK", ("check",), broken_zh, EN),
        ("CHECK", ("check", "--lang", "zh"), broken_zh, ZH),
        ("INIT", ("init",), {}, EN),
        ("INIT", ("init", "--lang", "zh"), {}, ZH),
        ("INIT", ("init",), bare, EN),
    ]
    for name, argv, environ, expected in cases:
        assert _lang(home, name, *argv, environ=environ) is expected, argv


def test_f05_t34_a_mistake_comes_in_the_language_of_the_settings(tmp_path: Path) -> None:
    """The settings are read before a usage error is reported, and the help follows the rule."""
    home = make_home(tmp_path)
    zh = in_folder(make_folder(tmp_path, "zh"))
    broken_zh = in_folder(make_folder(tmp_path, "broken_zh"))
    unknown_en = err_result(2, 'Unknown command "cook".', COMMANDS_EN)
    cases = [
        (("cook",), zh, err_result(2, "未知命令“cook”。", COMMANDS_ZH)),
        (("show",), zh, err_result(2, "缺少参数。请写成“recipe-menu show ID”。", COMMANDS_ZH)),
        (("list", "--tag"), zh, err_result(2, "--tag 后面要写一个值。")),
        (("cook", "--lang", "en"), zh, unknown_en),
        (("cook",), broken_zh, unknown_en),
        (("cook",), {}, unknown_en),
        (("--help",), zh, (0, HELP_ZH, "")),
        (("--help", "--lang", "en"), zh, (0, HELP_EN, "")),
        (("--help",), broken_zh, (0, HELP_EN, "")),
    ]
    for argv, environ, expected in cases:
        result, kit = go(home, *argv, environ=environ)
        assert result == expected, argv
        assert kit.nothing_ran(), argv
