"""Test of F15 for a data folder of the size of requirements 7: 1,000 recipes (T29)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import lines_text
from f09_support import at
from f15_blocks import PT01_FILE
from f15_support import PT01_ANSWERS, add
from f15_texts import ID_PROMPT, id_exists, pt01_out
from pt01_support import PT01_LINES, make_pt01
from recipe_menu.datafile import DataFolder


def test_f15_t29_add_and_check_work_on_a_data_folder_with_1000_recipes(tmp_path: Path) -> None:
    """The run of v0.2-S16 step 2: an ID that exists, names with digits, and a clean check."""
    home = make_home(tmp_path)
    root = tmp_path / "pt01"
    make_pt01(root)
    folder = DataFolder(root)
    result = add(home, folder, ["recipe-0001", *PT01_ANSWERS])
    shown = [ID_PROMPT[0] + "recipe-0001", id_exists("recipe-0001")[0], *pt01_out(folder)]
    assert result == (0, lines_text(*shown), "")
    assert folder.recipe_file("size-check").read_bytes() == PT01_FILE.encode("utf-8")
    checked = [PT01_LINES[0].replace("1000 recipes", "1001 recipes"), *PT01_LINES[1:]]
    assert at(home, folder, "check") == (0, lines_text(*checked), "")
