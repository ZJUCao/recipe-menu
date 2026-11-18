"""Tests of F14 for what cli does before it runs menu suggest, and for the help (T21)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import ZH, no_data_folder
from f07_changes import broken_settings
from f07_support import call
from f09_support import made
from f09_texts import E_SETTINGS, err, out, stop
from f13_support import pristine
from f14_support import IN_ZH, W47, WEEK_48, suggest, week_line, with_dishes
from f14_texts import E_DISHES_ZERO, some
from recipe_menu.datafile import DataFolder

TO_COMMANDS = 'Run "recipe-menu --help" to see the commands.'
TO_COMMANDS_ZH = "运行“recipe-menu --help”查看命令。"
TO_OPTIONS = 'Run "recipe-menu --help" to see the options.'
TO_OPTIONS_ZH = "运行“recipe-menu --help”查看选项。"
LINES = [
    (
        ("menu", "suggest", W47, WEEK_48),
        [
            'Unexpected argument "2026-W48". Write "recipe-menu menu suggest [WEEK]".',
            TO_COMMANDS,
        ],
    ),
    (
        ("menu", "suggest", W47, WEEK_48, *IN_ZH),
        ["多余的参数“2026-W48”。请写成“recipe-menu menu suggest [周]”。", TO_COMMANDS_ZH],
    ),
    (
        ("menu", "suggest", "--tags", "quick"),
        ['"menu suggest" has no option "--tags". Its own option is "--tag".', TO_OPTIONS],
    ),
    (
        ("menu", "suggest", "--tags", "quick", *IN_ZH),
        ["“menu suggest”没有选项“--tags”。它自己的选项是“--tag”。", TO_OPTIONS_ZH],
    ),
    (("menu", "suggest", "--tag"), ["--tag needs a value."]),
    (("menu", "suggest", "--tag", ""), ["--tag needs a value."]),
    (("menu", "suggest", "--tag", *IN_ZH), ["--tag 后面要写一个值。"]),
    (("menu", "suggest", "--tag", "a", "--tag", "b"), ["--tag is given twice."]),
    (("menu", "suggest", "--tag", "a", "--tag", "b", *IN_ZH), ["--tag 写了两次。"]),
    (
        ("menu",),
        [
            'The commands that start with "menu" are "menu new", "menu show", and "menu suggest".',
            TO_COMMANDS,
        ],
    ),
    (
        ("menu", *IN_ZH),
        ["以“menu”开头的命令有“menu new”、“menu show”和“menu suggest”。", TO_COMMANDS_ZH],
    ),
    (("menu", "suggestion"), ['Unknown command "menu suggestion".', TO_COMMANDS]),
]


def _check_the_line(home: Path, example: DataFolder) -> None:
    """Inputs 1 and 2: the mistakes on the command line, and ``menu`` alone."""
    for argv, lines in LINES:
        assert suggest(home, example, *argv) == err(2, lines), argv


def _check_help(home: Path, example: DataFolder) -> None:
    """Input 3: ``--help`` shows the help and runs nothing."""
    english = call(home, ["--help"])
    chinese = call(home, ["--help", *IN_ZH])
    assert (english[0], english[2]) == (0, "")
    assert suggest(home, example, "menu", "suggest", "next", "--help") == english
    assert suggest(home, example, "menu", "suggest", "2026-W99", "--help", *IN_ZH) == chinese


def _check_data_folder(home: Path, tmp_path: Path) -> None:
    """Input 4: a data folder that is not there."""
    missing = tmp_path / "missing"
    assert suggest(home, missing, "menu", "suggest") == no_data_folder(missing)
    result = suggest(home, missing, "menu", "suggest", "next", *IN_ZH)
    assert result == no_data_folder(missing, ZH)
    assert not missing.exists()
    result = suggest(home, None, *week_line(WEEK_48))
    assert result == no_data_folder(home / "recipe-menu")


def test_f14_t21_cli_reports_its_mistakes_before_it_runs_the_command(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven inputs: the command line, ``menu`` alone, the help, no folder, and the settings."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    week = example_folder.menu_file(W47)
    before = week.read_bytes()
    _check_the_line(home, example_folder)
    _check_help(home, example_folder)
    _check_data_folder(home, tmp_path)
    broken = made(source, tmp_path, "broken", broken_settings)
    assert suggest(home, broken, *week_line(W47)) == stop(E_SETTINGS)
    zero = made(source, tmp_path, "zero", with_dishes("{ dinner = 0 }"))
    assert suggest(home, zero, *week_line(W47)) == stop(E_DISHES_ZERO)
    assert suggest(home, zero, *week_line(W47, *IN_ZH)) == stop(E_DISHES_ZERO, ZH)
    assert week.read_bytes() == before
    assert [entry.name for entry in example_folder.menus.iterdir()] == ["2026-W47.toml"]
    assert suggest(home, example_folder, *week_line(W47)) == out(some(W47, 1, 10, 4, "left"))
