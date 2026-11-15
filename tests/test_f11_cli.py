"""Tests of F11 for what cli checks before it runs menu new or menu show (T32)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import no_data_folder
from f07_changes import broken_settings
from f09_support import at, made
from f09_texts import E_SETTINGS, RUN_HELP_COMMANDS, RUN_HELP_OPTIONS, ZH, err, out, stop
from f11_support import held, menu_text
from f11_texts import LUNCH_DINNER, SHOW_47, new
from recipe_menu.datafile import DataFolder

TOO_MANY = 'Unexpected argument "2026-W48". Write "recipe-menu menu {name} [WEEK]".'
NO_OPTION = '"menu {name}" has no option "--tag". It has no options of its own.'
# Inputs 1 and 2 of F11-T32: the command line, the exit code, and the two lines on stderr.
LINES = [
    (
        ("menu", "new", "2026-W47", "2026-W48"),
        [TOO_MANY.format(name="new"), RUN_HELP_COMMANDS[0]],
    ),
    (
        ("menu", "new", "2026-W47", "2026-W48", "--lang", "zh"),
        ["多余的参数“2026-W48”。请写成“recipe-menu menu new [周]”。", RUN_HELP_COMMANDS[1]],
    ),
    (
        ("menu", "show", "2026-W47", "2026-W48"),
        [TOO_MANY.format(name="show"), RUN_HELP_COMMANDS[0]],
    ),
    (("menu", "new", "--tag", "quick"), [NO_OPTION.format(name="new"), RUN_HELP_OPTIONS[0]]),
    (("menu", "show", "--tag", "quick"), [NO_OPTION.format(name="show"), RUN_HELP_OPTIONS[0]]),
    (
        ("menu", "show", "--tag", "quick", "--lang", "zh"),
        ["“menu show”没有选项“--tag”。它没有自己的选项。", RUN_HELP_OPTIONS[1]],
    ),
    (
        ("menu",),
        [
            'The commands that start with "menu" are "menu new" and "menu show".',
            RUN_HELP_COMMANDS[0],
        ],
    ),
    (
        ("menu", "--lang", "zh"),
        ["以“menu”开头的命令有“menu new”和“menu show”。", RUN_HELP_COMMANDS[1]],
    ),
    (("menu", "cook"), ['Unknown command "menu cook".', RUN_HELP_COMMANDS[0]]),
]
HELP_LINES = [
    (("menu", "--help"), ()),
    (("menu", "new", "2026-W48", "--help"), ()),
    (("menu", "show", "next", "--help"), ()),
    (("menu", "new", "2026-W99", "--help", "--lang", "zh"), ("--lang", "zh")),
]


def _check_lines(home: Path, example: DataFolder) -> None:
    """Checks inputs 1 and 2 of F11-T32: each wrong line gives exit code 2 and two lines."""
    for argv, lines in LINES:
        assert at(home, example, *argv) == err(2, lines), argv


def _check_help(home: Path, example: DataFolder) -> None:
    """Checks the last line of input 2 and input 3: ``--help`` shows the help and runs nothing."""
    english = at(home, None, "--help")
    chinese = at(home, None, "--help", "--lang", "zh")
    assert english[0] == chinese[0] == 0
    assert "Commands:" in english[1]
    assert "命令：" in chinese[1]
    for argv, extra in HELP_LINES:
        expected = chinese if extra else english
        assert at(home, example, *argv) == expected, argv


def test_f11_t32_cli_reports_the_command_line_the_folder_and_the_settings_before_run(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Wrong lines, ``--help``, a missing folder, broken settings, and then the outputs."""
    home = make_home(tmp_path)
    _check_lines(home, example_folder)
    _check_help(home, example_folder)
    missing = tmp_path / "missing"
    assert at(home, missing, "menu", "new") == no_data_folder(missing)
    assert at(home, missing, "menu", "show", "next", "--lang", "zh") == no_data_folder(missing, ZH)
    assert not missing.exists()
    broken = made(example_folder, tmp_path, "broken", broken_settings)
    assert at(home, broken, "menu", "new", "2026-W48") == stop(E_SETTINGS)
    assert at(home, broken, "menu", "show", "2026-W47") == stop(E_SETTINGS)
    assert [path.name for path in (broken / "menus").iterdir()] == ["2026-W47.toml"]
    names = [path.name for path in example_folder.menus.iterdir()]
    assert names == ["2026-W47.toml"]
    file = example_folder.menu_file("2026-W48")
    created = out(new(file, "23 to 29 November 2026", "lunch and dinner"))
    assert at(home, example_folder, "menu", "new", "2026-W48") == created
    assert held(file) == menu_text("2026-W48", LUNCH_DINNER)
    assert at(home, example_folder, "menu", "show", "2026-W47") == out(SHOW_47)
