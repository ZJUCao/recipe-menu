"""Tests of F15 for what cli does before it runs add: usage, the folder, the settings (T24)."""

from pathlib import Path

from f05_support import copy_example, make_home, record
from f05_texts import ZH, lines_text, no_data_folder
from f07_changes import broken_settings
from f07_support import call
from f09_texts import E_SETTINGS, RUN_HELP_COMMANDS, RUN_HELP_OPTIONS, err, stop
from f10_support import chinese_settings
from f13_support import pristine
from f15_support import BASE, Watched, add, answers, fresh, line
from f15_texts import base_out
from recipe_menu.datafile import DataFolder

UNEXPECTED = ('Unexpected argument "garlic-broccoli". Write "recipe-menu add".',)
UNEXPECTED_ZH = ("多余的参数“garlic-broccoli”。请写成“recipe-menu add”。",)
NO_OPTION = ('"add" has no option "--tag". It has no options of its own.',)
NO_OPTION_ZH = ("“add”没有选项“--tag”。它没有自己的选项。",)
ZH_OPTION = ("--lang", "zh")


def _check_usage(home: Path, example: DataFolder) -> None:
    """Line 1: the mistakes on the command line, with a watched stream."""
    before = record(example.root)
    lines = (
        (("add", "garlic-broccoli"), 2, [*UNEXPECTED, RUN_HELP_COMMANDS[0]]),
        (("add", "garlic-broccoli", *ZH_OPTION), 2, [*UNEXPECTED_ZH, RUN_HELP_COMMANDS[1]]),
        (("add", "--tag", "quick"), 2, [*NO_OPTION, RUN_HELP_OPTIONS[0]]),
        (("add", "--tag", "quick", *ZH_OPTION), 2, [*NO_OPTION_ZH, RUN_HELP_OPTIONS[1]]),
    )
    for argv, code, shown in lines:
        assert line(home, example, Watched(), *argv) == err(code, shown), argv
    for option in (["--lang", "fr"], ["--lang"]):
        expected = call(home, ["list", "--data", str(example.root), *option])
        assert expected[0] == 2
        assert add(home, example, Watched(), *option) == expected, option
    assert record(example.root) == before


def _check_help(home: Path, example: DataFolder) -> None:
    """Line 2: ``--help`` shows the help and does not run ``add``."""
    lines = (
        (("add", "--help"), ["--help"]),
        (("add", "garlic-broccoli", "--help", *ZH_OPTION), ["--help", *ZH_OPTION]),
    )
    before = record(example.root)
    for argv, plain in lines:
        expected = call(home, plain)
        assert (expected[0], expected[2]) == (0, "")
        assert line(home, example, Watched(), *argv) == expected, argv
    assert record(example.root) == before


def test_f15_t24_cli_reports_its_mistakes_before_add_asks_anything(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven lines: the command line, the help, a missing folder, the settings, and the language."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_usage(home, example_folder)
    _check_help(home, example_folder)
    missing = tmp_path / "missing"
    assert line(home, missing, Watched(), "add") == no_data_folder(missing)
    assert line(home, missing, Watched(), "add", *ZH_OPTION) == no_data_folder(missing, ZH)
    assert not missing.exists()
    broken = fresh(source, tmp_path, "broken", broken_settings)
    before = record(broken.root)
    assert add(home, broken, Watched()) == stop(E_SETTINGS)
    assert record(broken.root) == before
    chinese = fresh(source, tmp_path, "chinese", chinese_settings)
    assert add(home, chinese, BASE) == (0, lines_text(*base_out(chinese, True)), "")
    second = answers("new-dish-2")
    expected = lines_text(*base_out(chinese, False, "new-dish-2"))
    assert add(home, chinese, second, "--lang", "en") == (0, expected, "")
    default = DataFolder(copy_example(source, home / "recipe-menu"))
    assert add(home, None, BASE) == (0, lines_text(*base_out(default)), "")
    assert add(home, example_folder, BASE) == (0, lines_text(*base_out(example_folder)), "")
