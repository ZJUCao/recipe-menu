"""Tests of F05 for python -m recipe_menu (T48 and T49)."""

from pathlib import Path

from f03_support import write
from f05_support import VERSION_LINE, make_folder, run_module
from f05_texts import COMMANDS_EN, COMMANDS_ZH, err_result

NO_COMMAND_ZH = err_result(2, "请写上一个命令，比如“recipe-menu list”。", COMMANDS_ZH)
NO_COMMAND_EN = err_result(2, 'Name a command, such as "recipe-menu list".', COMMANDS_EN)


def test_f05_t48_python_m_recipe_menu_writes_utf8_and_exits_with_the_code(tmp_path: Path) -> None:
    """Main reads sys.argv and uses COMMANDS, and the streams write UTF-8 whatever they were."""
    assert run_module(tmp_path, "--version") == (0, VERSION_LINE, "")
    assert run_module(tmp_path, "--lang", "zh") == NO_COMMAND_ZH
    unknown = err_result(2, 'Unknown command "cook".', COMMANDS_EN)
    assert run_module(tmp_path, "cook") == unknown
    code, out, err = run_module(tmp_path, "--help", "--lang", "zh")
    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert lines[0] == "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]"
    assert (
        lines[-1]
        == "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。"
    )


def test_f05_t49_python_m_recipe_menu_reads_the_environment_and_the_home_folder(
    tmp_path: Path,
) -> None:
    """RECIPE_MENU_DATA comes from os.environ, and the home folder from Path.home()."""
    home = tmp_path / "home"
    home.mkdir()
    write(home / "recipe-menu" / "settings.toml", 'language = "zh"\n')
    assert run_module(tmp_path, home=home) == NO_COMMAND_ZH
    zh = make_folder(tmp_path, "zh")
    other = tmp_path / "other"
    assert run_module(tmp_path, data=zh, home=other) == NO_COMMAND_ZH
    assert run_module(tmp_path, "--lang", "en", data=zh, home=other) == NO_COMMAND_EN
