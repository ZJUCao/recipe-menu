"""Tests of F13 for what cli reports before it runs shop (T22)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import HELP_EN, HELP_ZH, no_data_folder
from f07_changes import broken_settings
from f09_support import at, made
from f09_texts import E_SETTINGS, RUN_HELP_COMMANDS, RUN_HELP_OPTIONS, ZH, err, out, stop
from f13_support import pristine
from f13_texts import shop_47
from recipe_menu.datafile import DataFolder


def test_f13_t22_cli_reports_the_mistakes_of_the_command_line_before_it_runs_shop(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Two weeks, an option, ``--help``, a missing folder, broken settings, and then the list."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    two_weeks = 'Unexpected argument "2026-W48". Write "recipe-menu shop [WEEK]".'
    two_weeks_zh = "多余的参数“2026-W48”。请写成“recipe-menu shop [周]”。"
    tag = '"shop" has no option "--tag". It has no options of its own.'
    tag_zh = "“shop”没有选项“--tag”。它没有自己的选项。"
    lines = [
        (("shop", "2026-W47", "2026-W48"), err(2, [two_weeks, RUN_HELP_COMMANDS[0]])),
        (
            ("shop", "2026-W47", "2026-W48", "--lang", "zh"),
            err(2, [two_weeks_zh, RUN_HELP_COMMANDS[1]]),
        ),
        (("shop", "--tag", "x"), err(2, [tag, RUN_HELP_OPTIONS[0]])),
        (("shop", "--tag", "x", "--lang", "zh"), err(2, [tag_zh, RUN_HELP_OPTIONS[1]])),
        (("shop", "next", "--help"), (0, HELP_EN, "")),
        (("shop", "2026-W99", "--help", "--lang", "zh"), (0, HELP_ZH, "")),
    ]
    for argv, expected in lines:
        assert at(home, example_folder, *argv) == expected, argv
    assert not example_folder.shopping.exists()
    missing = tmp_path / "missing"
    assert at(home, missing, "shop") == no_data_folder(missing)
    assert at(home, missing, "shop", "next", "--lang", "zh") == no_data_folder(missing, ZH)
    assert not missing.exists()
    broken = made(source, tmp_path, "broken", broken_settings)
    assert at(home, broken, "shop", "2026-W47") == stop(E_SETTINGS)
    assert not (broken / "shopping").exists()
    assert not example_folder.shopping.exists()
    file = example_folder.shopping_file("2026-W47")
    assert at(home, example_folder, "shop", "2026-W47") == out(shop_47(file))
