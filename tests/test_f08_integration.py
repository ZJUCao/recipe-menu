"""Tests of F08 for the version scenarios v0.1-S01 to S03 and S06, and the real entry point.

These are T24 to T27.
"""

from pathlib import Path

from f03_support import put_bytes
from f05_support import make_home, run_module
from f07_changes import make_init, the_comma
from f07_support import check
from f08_support import full_record, init, tree
from f08_texts import (
    CHECK_NEW,
    CHECK_NEW_ZH,
    err_of,
    holds,
    new,
    new_zh,
    out_of,
)
from recipe_menu.datafile import DataFolder

ONE_RECIPE = "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus."
ONE_RECIPE_ZH = "已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。"
COMMA = [
    ONE_RECIPE,
    "",
    "1 error:",
    "  pantry.toml, line 2",
    '    The file cannot be read: a closing "]" is missing.',
    "",
    'Fix the errors and run "recipe-menu check" again.',
]
COMMA_ZH = [
    ONE_RECIPE_ZH,
    "",
    "1 个错误：",
    "  pantry.toml，第 2 行",
    "    无法读取文件：缺少右方括号“]”。",
    "",
    "改正错误后，再运行“recipe-menu check”。",
]


def test_f08_t24_the_folder_that_init_creates_is_the_init_folder_of_f07_and_checks_as_it_does(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S01 and v0.1-S06 at main, and the folder equals F07's init folder byte for byte."""
    home = make_home(tmp_path)
    root = home / "recipe-menu"
    assert init(home) == out_of(0, new(root))
    assert check(home, None) == out_of(0, CHECK_NEW)
    made = make_init(example_folder, tmp_path / "f07-init")
    assert tree(made) == tree(root)
    the_comma(root)
    assert check(home, None) == out_of(1, COMMA)
    assert check(home, None, "--lang", "zh") == out_of(1, COMMA_ZH)


def test_f08_t25_init_writes_its_language_into_the_settings_so_the_folder_speaks_it(
    tmp_path: Path,
) -> None:
    """v0.1-S02 at main: a Chinese folder checks in Chinese, and differs in one file."""
    home = make_home(tmp_path)
    root = home / "recipe-menu"
    assert init(home, "--lang", "zh") == out_of(0, new_zh(root))
    assert check(home, None) == out_of(0, CHECK_NEW_ZH)
    english = tmp_path / "en"
    assert init(home, folder=english) == out_of(0, new(english))
    chinese_tree, english_tree = tree(root), tree(english)
    assert chinese_tree.keys() == english_tree.keys()
    different = {key for key in chinese_tree if chinese_tree[key] != english_tree[key]}
    assert different == {"settings.toml"}
    english_bytes = english_tree["settings.toml"][1]
    assert english_bytes is not None
    assert chinese_tree["settings.toml"][1] == english_bytes.replace(
        b'language = "en"', b'language = "zh"'
    )


def test_f08_t26_init_refuses_a_folder_with_files_and_creates_a_new_one_elsewhere(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S03 at main: the refused folder keeps every byte and time, the other one is new."""
    home = make_home(tmp_path)
    root = home / "recipe-menu"
    put_bytes(root / "notes.txt", b"Ideas\n")
    before = full_record(home)
    assert init(home) == err_of(1, [holds(root)])
    assert full_record(home) == before
    other = tmp_path / "other"
    assert init(home, folder=other) == out_of(0, new(other))
    made = make_init(example_folder, tmp_path / "f07-init")
    assert tree(other) == tree(made)


def test_f08_t27_the_real_entry_point_writes_the_output_as_utf_8(tmp_path: Path) -> None:
    """`python -m recipe_menu init` with PYTHONIOENCODING=ascii: stdout for a new folder."""
    root = tmp_path / "home" / "recipe-menu"
    assert run_module(tmp_path, "init") == out_of(0, new(root))
    chinese = tmp_path / "zh"
    result = run_module(tmp_path, "init", "--lang", "zh", "--data", str(chinese))
    assert result == out_of(0, new_zh(chinese))
    assert run_module(tmp_path, "init") == err_of(1, [holds(root)])
    data = tmp_path / "w"
    assert run_module(tmp_path, "init", data=data) == out_of(0, new(data))
