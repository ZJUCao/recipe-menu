"""The command line and the settings: v0.1-S19 to v0.1-S22."""

from support import World, cells, change, check_result, read
from texts_find import LIST_EN
from texts_start import (
    BAD_COMMAND,
    BAD_LANG,
    BROKEN_SETTINGS,
    HELP_EN,
    HELP_ZH,
    NO_FOLDER_EN,
    NO_FOLDER_ZH,
    SETTINGS_EN_TAG,
    SETTINGS_ZH_TAG,
)


def test_v0_1_s19_help_version_and_mistakes_on_the_command_line(world: World) -> None:
    """v0.1-S19: help and version need no data folder, and a mistake exits with 2."""
    check_result(world, world.run("--help"), 0, HELP_EN)
    check_result(world, world.run("--help", "--lang", "zh"), 0, HELP_ZH)
    check_result(world, world.run("--version"), 0, ["recipe-menu 0.1.0"])
    world.copy_example()
    check_result(world, world.run("list", "--lang", "fr"), 2, BAD_LANG)
    check_result(world, world.run("cook"), 2, BAD_COMMAND)


def test_v0_1_s20_choose_the_data_folder(world: World) -> None:
    """v0.1-S20: `--data` beats `RECIPE_MENU_DATA`, which beats the default folder."""
    folder_b = world.copy_example(world.root / "One Drive" / "菜谱")
    folder_c = world.root / "other"
    assert world.run("init", "--data", folder_c).code == 0
    check_result(world, world.run("list", "--data", folder_b), 0, LIST_EN)
    only_one = world.run("list", data=folder_c)
    assert (only_one.code, only_one.err) == (0, "")
    lines = only_one.out.split("\n")
    assert [cells(line)[0] for line in lines[1:-3]] == ["tomato-egg"]
    assert lines[-3:] == ["", "1 recipe.", ""]
    check_result(world, world.run("list", "--data", folder_b, data=folder_c), 0, LIST_EN)
    check_result(world, world.run("list"), 1, NO_FOLDER_EN)
    check_result(world, world.run("list", "--lang", "zh"), 1, NO_FOLDER_ZH)


def test_v0_1_s21_the_language_comes_from_the_settings(world: World) -> None:
    """v0.1-S21: `language` in the settings sets the language, and `--lang` beats it."""
    world.copy_example()
    settings = world.data / "settings.toml"
    change(settings, 'language = "en"', 'language = "zh"')
    check_result(world, world.run("list", "--tag", "素"), 0, SETTINGS_ZH_TAG)
    check_result(world, world.run("list", "--tag", "素", "--lang", "en"), 0, SETTINGS_EN_TAG)
    kept = [line for line in read(settings).split("\n") if not line.startswith("language")]
    settings.write_bytes("\n".join(kept).encode("utf-8"))
    check_result(world, world.run("list", "--tag", "素"), 0, SETTINGS_EN_TAG)


def test_v0_1_s22_a_broken_settings_file_stops_a_command(world: World) -> None:
    """v0.1-S22: an unknown meal in `settings.toml` stops `list` with exit code 1."""
    world.copy_example()
    change(world.data / "settings.toml", '["lunch", "dinner"]', '["lunch", "supper"]')
    result = world.run("list")
    assert result.code == 1
    assert result.out == ""
    assert result.err.startswith("\n".join(BROKEN_SETTINGS[:2]) + "\n")
