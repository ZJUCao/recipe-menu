"""Tests of F05 for main: the version and the help (T44 to T47)."""

from pathlib import Path

import recipe_menu
from f05_support import VERSION, VERSION_LINE, go, in_folder, make_folder, make_home
from f05_texts import BARE_HELP_EN_LINES, BARE_HELP_ZH_LINES, HELP_EN, HELP_ZH, lines_text


def test_f05_t44_version_writes_the_version_of_the_project(tmp_path: Path) -> None:
    """--version writes recipe-menu and the version, and the version equals pyproject.toml's."""
    assert recipe_menu.__version__ == VERSION
    home = make_home(tmp_path)
    broken_zh = in_folder(make_folder(tmp_path, "broken_zh"))
    for argv, environ in [(("--version",), {}), (("--version", "--lang", "zh"), {})]:
        result, kit = go(home, *argv, environ=environ)
        assert result == (0, VERSION_LINE, ""), argv
        assert kit.nothing_ran()
    result, kit = go(home, "--version", environ=broken_zh)
    assert result == (0, VERSION_LINE, "")
    assert kit.nothing_ran()


def test_f05_t45_help_is_the_prototype_help_and_needs_no_data_folder(tmp_path: Path) -> None:
    """The 21 lines of each prototype, with no data folder and with a broken settings file."""
    home = make_home(tmp_path)
    broken = in_folder(make_folder(tmp_path, "broken"))
    cases = [
        (("--help",), {}, HELP_EN),
        (("--help", "--lang", "zh"), {}, HELP_ZH),
        (("--help",), broken, HELP_EN),
    ]
    for argv, environ, expected in cases:
        result, kit = go(home, *argv, environ=environ)
        assert result == (0, expected, ""), argv
        assert kit.nothing_ran()


def test_f05_t46_the_first_column_is_as_wide_as_the_widest_cell(tmp_path: Path) -> None:
    """An option or a Chinese usage can set the width, and the commands keep their order."""
    home = make_home(tmp_path)
    bare = [(("--help",), BARE_HELP_EN_LINES), (("--help", "--lang", "zh"), BARE_HELP_ZH_LINES)]
    for argv, lines in bare:
        result, _ = go(home, *argv, names=())
        assert result == (0, lines_text(*lines), ""), argv
    names = ("WIDE", "LIST")
    result, _ = go(home, "--help", names=names)
    code, out, err = result
    lines = out.splitlines()
    assert (code, err, len(lines)) == (0, "", 15)
    assert lines[5] == "  menu show [WEEK]         Show a week menu."
    assert lines[6] == "  list                     List the recipes."
    wide_data = "  --data FOLDER            "
    assert (
        lines[10] == wide_data + "The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu."
    )
    result, _ = go(home, "--help", "--lang", "zh", names=names)
    code, out, err = result
    lines = out.splitlines()
    assert (code, err, len(lines)) == (0, "", 15)
    assert lines[5] == "  menu show [一周的编号]   查看一个周菜单。"
    assert lines[6] == "  list                     列出菜谱。"
    assert (
        lines[10]
        == "  --data 文件夹            数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。"
    )
    result, _ = go(home, "--help", names=("SHOP", "INIT"))
    code, out, err = result
    lines = out.splitlines()
    assert (code, err) == (0, "")
    assert lines[5] == "  shop [WEEK]     Make the shopping list of a week menu."
    assert lines[6] == "  init            Create the data folder with example data."


def test_f05_t47_help_comes_whatever_else_the_line_holds(tmp_path: Path) -> None:
    """The design's example with SHOW and MENU_SHOW, and a second --help changes nothing."""
    home = make_home(tmp_path)

    def help_lines(*argv: str) -> list[str]:
        """Gives the lines of the help of a line."""
        result, _ = go(home, *argv, names=("SHOW", "MENU_SHOW"))
        assert result[0] == 0
        assert result[2] == ""
        return result[1].splitlines()

    lines = help_lines("--help", "--lang", "zh")
    assert len(lines) == 15
    assert lines[0] == "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]"
    assert lines[4] == "命令："
    assert lines[5] == "  show ID            查看一个菜谱。"
    assert lines[6] == "  menu show [周]     查看一个周菜单。"
    assert lines[10].startswith("  --data 文件夹      数据文件夹。")
    english = help_lines("show", "x", "--help")
    assert english[6] == "  menu show [WEEK]   Show a week menu."
    assert english[9].startswith("  --lang en|zh       The language of the output.")
    assert help_lines("--help", "--help") == english
