"""Tests of F09 for what ``cli`` checks before a command, and for the files that each reads."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f05_texts import no_data_folder
from f07_changes import broken_settings, mapo_mistake, menu_path, the_comma, the_typo
from f08_support import faults
from f09_support import at, made
from f09_texts import (
    BREAKFAST,
    E_SETTINGS,
    IDS,
    LIST,
    MAPO,
    PORK_ZH,
    QUICK_ZH,
    RUN_HELP_COMMANDS,
    RUN_HELP_OPTIONS,
    TOMATO,
    ZH,
    err,
    not_a_recipe_id,
    out,
    servings_not_1_to_100,
    stop,
)
from recipe_menu.datafile import DataFolder

SHOW_USAGE = 'Write "recipe-menu show ID".'
LIST_LINE_ERRORS = [
    (
        ("list", "extra"),
        ['Unexpected argument "extra". Write "recipe-menu list".', RUN_HELP_COMMANDS[0]],
    ),
    (
        ("list", "extra", "--lang", "zh"),
        ["多余的参数“extra”。请写成“recipe-menu list”。", RUN_HELP_COMMANDS[1]],
    ),
    (
        ("list", "--tags", "x"),
        ['"list" has no option "--tags". Its own option is "--tag".', RUN_HELP_OPTIONS[0]],
    ),
    (
        ("list", "--tags", "x", "--lang", "zh"),
        ["“list”没有选项“--tags”。它自己的选项是“--tag”。", RUN_HELP_OPTIONS[1]],
    ),
    (("list", "--tag"), ["--tag needs a value."]),
    (("list", "--tag", "--lang", "zh"), ["--tag 后面要写一个值。"]),
    (("list", "--tag", "a", "--tag", "b"), ["--tag is given twice."]),
]
SHOW_LINE_ERRORS = [
    (
        ("show",),
        ['An argument is missing. Write "recipe-menu show ID".', RUN_HELP_COMMANDS[0]],
    ),
    (
        ("show", "--lang", "zh"),
        ["缺少参数。请写成“recipe-menu show ID”。", RUN_HELP_COMMANDS[1]],
    ),
    (
        ("show", "rice", "tomato-egg"),
        ['Unexpected argument "tomato-egg". Write "recipe-menu show ID".', RUN_HELP_COMMANDS[0]],
    ),
    (
        ("show", "rice", "--tag", "quick"),
        ['"show" has no option "--tag". Its own option is "--servings".', RUN_HELP_OPTIONS[0]],
    ),
    (
        ("show", "rice", "--tag", "quick", "--lang", "zh"),
        ["“show”没有选项“--tag”。它自己的选项是“--servings”。", RUN_HELP_OPTIONS[1]],
    ),
    (("show", "rice", "--servings"), ["--servings needs a value."]),
    (("show", "rice", "--servings", ""), ["--servings needs a value."]),
    (("show", "rice", "--servings", "2", "--servings", "3"), ["--servings is given twice."]),
    (("show", "rice", "--servings", "--lang", "zh"), ["--servings 后面要写一个值。"]),
]


def _check_lines(home: Path, example: DataFolder, table: list) -> None:
    """Checks that each command line gives exit code 2 and its lines on the error stream."""
    for argv, lines in table:
        assert at(home, example, *argv) == err(2, lines), argv


def _check_missing_folder(home: Path, tmp_path: Path) -> None:
    """Checks that ``cli`` stops on a missing data folder before ``run`` checks the values."""
    missing = tmp_path / "missing"
    assert at(home, missing, "list") == no_data_folder(missing)
    assert at(home, missing, "list", "--lang", "zh") == no_data_folder(missing, ZH)
    assert at(home, missing, "show", "Mapo") == no_data_folder(missing)
    assert at(home, missing, "show", "rice", "--servings", "0") == no_data_folder(missing)


def _check_help(home: Path, root: Path) -> None:
    """Checks that ``--help`` shows the help and runs neither command."""
    english, chinese = at(home, None, "--help"), at(home, None, "--help", "--lang", "zh")
    assert english[0] == chinese[0] == 0
    assert "Commands:" in english[1]
    assert "命令：" in chinese[1]
    assert english[2] == chinese[2] == ""
    assert at(home, root, "list", "--help") == english
    assert at(home, root, "show", "mapo-tofu", "--help", "--lang", "zh") == chinese
    assert at(home, root, "show", "Mapo", "--help") == english


def test_f09_t19_cli_reports_the_command_line_the_folder_and_the_settings_before_run(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The wrong lines, a missing folder, broken settings, ``--help``, and then the outputs."""
    home = make_home(tmp_path)
    _check_lines(home, example_folder, LIST_LINE_ERRORS)
    _check_lines(home, example_folder, SHOW_LINE_ERRORS)
    _check_missing_folder(home, tmp_path)
    broken = made(example_folder, tmp_path, "broken", broken_settings)
    for argv in (("list",), ("show", "Mapo"), ("show", "tomato-egg")):
        assert at(home, broken, *argv) == stop(E_SETTINGS), argv
    _check_help(home, made(example_folder, tmp_path, "mapo", mapo_mistake))
    assert at(home, example_folder, "list") == out(LIST)
    assert at(home, example_folder, "show", "tomato-egg") == out(TOMATO)


SETTINGS = "read settings.toml"
CATALOG = "read catalog.toml"
READ_EACH = [SETTINGS, CATALOG, *[f"read recipes/{recipe_id}.toml" for recipe_id in IDS]]
READ_TOMATO = [SETTINGS, CATALOG, "read recipes/tomato-egg.toml"]
# Each line of F09-T20: the line, the reads, the listings, and the result.
READS = [
    (("list",), READ_EACH, ["recipes"], out(LIST)),
    (("list", "--tag", "快手", "--lang", "zh"), READ_EACH, ["recipes"], out(QUICK_ZH)),
    (("list", "--tag", "breakfast"), [SETTINGS, CATALOG], [], err(1, [BREAKFAST])),
    (("show", "tomato-egg"), READ_TOMATO, ["recipes"], out(TOMATO)),
    (("show", "mapo"), [SETTINGS, CATALOG], ["recipes"], err(1, [MAPO])),
    (("show", "Mapo"), [SETTINGS], [], err(2, [not_a_recipe_id("Mapo")])),
    (
        ("show", "rice", "--servings", "0"),
        [SETTINGS],
        [],
        err(2, [servings_not_1_to_100("0")]),
    ),
]


def test_f09_t20_each_command_reads_only_the_files_that_it_needs_and_reads_each_once(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The record of the reads and the listings, and no read of the pantry or a menu."""
    home = make_home(tmp_path)
    for argv, reads, listings, result in READS:
        with faults(example_folder.root) as state:
            got = at(home, example_folder, *argv)
        assert (state.calls, state.listings, got) == (reads, listings, result), argv
    the_comma(example_folder.root)
    the_typo(example_folder.root)
    write(menu_path(example_folder.root, "2026-W48"), "[[[\n")
    assert at(home, example_folder, "list") == out(LIST)
    assert at(home, example_folder, "list", "--tag", "quick", "--lang", "zh") == out(QUICK_ZH)
    assert at(home, example_folder, "show", "tomato-egg") == out(TOMATO)
    assert at(home, example_folder, "show", "red-braised-pork", "--lang", "zh") == out(PORK_ZH)
