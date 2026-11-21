"""Tests of F15 for the sessions of the design's examples and of the prototype (T07 to T09)."""

from pathlib import Path

from f03_support import put_bytes
from f05_support import make_home
from f05_texts import lines_text
from f07_support import AFTER, snapshot
from f09_support import at
from f13_support import pristine
from f15_blocks import PARTLY_FILE, S09_FILE, S10_FILE
from f15_support import PARTLY, S09, S10, add, fresh, listing, recipe_names
from f15_texts import (
    EN_NAME_PROMPT,
    ID_PROMPT,
    INPUT_ENDED,
    ZH_NAME_PROMPT,
    id_exists,
    partly_out,
    s09_out,
    s10_out,
)
from recipe_menu.datafile import DataFolder

EXISTS_RICE = [" rice\t", "tomato-egg-noodles", "choy-sum", ""]


def test_f15_t07_the_example_of_the_add_session_holds(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.2: S09, S10, a partly empty recipe, and the three early ends."""
    home = make_home(tmp_path)
    chinese = add(home, example_folder, S09, "--lang", "zh")
    assert chinese == (0, lines_text(*s09_out(example_folder)), "")
    broccoli = example_folder.recipe_file("garlic-broccoli")
    assert broccoli.read_bytes() == S09_FILE.encode("utf-8")
    english = add(home, example_folder, S10)
    assert english == (0, lines_text(*s10_out(example_folder)), "")
    assert example_folder.recipe_file("egg-fried-rice").read_bytes() == S10_FILE.encode("utf-8")
    partly = add(home, example_folder, PARTLY)
    assert partly == (0, lines_text(*partly_out(example_folder)), "")
    assert example_folder.recipe_file("scallion-egg").read_bytes() == PARTLY_FILE.encode("utf-8")
    ended = add(home, example_folder, ["new-dish", "新菜"])
    lines = [ID_PROMPT[0] + "new-dish", ZH_NAME_PROMPT[0] + "新菜", EN_NAME_PROMPT[0]]
    assert ended == (1, lines_text(*lines), lines_text(INPUT_ENDED[0]))
    assert not example_folder.recipe_file("new-dish").exists()
    assert add(home, example_folder, [""], "--lang", "zh") == (0, lines_text(ID_PROMPT[1]), "")
    assert add(home, example_folder, []) == (0, lines_text(ID_PROMPT[0]), "")
    assert len(recipe_names(example_folder)) == 10


def test_f15_t08_the_prototype_session_in_chinese_saves_a_recipe_that_other_commands_read(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype and v0.2-S09: the run, the file, and ``show``, ``list``, and ``check``."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    before = {name: path.read_bytes() for name, path in _recipe_files(source).items()}
    result = add(home, example_folder, S09, "--lang", "zh")
    assert result == (0, lines_text(*s09_out(example_folder)), "")
    assert example_folder.recipe_file("garlic-broccoli").read_bytes() == S09_FILE.encode("utf-8")
    assert recipe_names(example_folder) == listing("garlic-broccoli.toml")
    after = {name: path.read_bytes() for name, path in _recipe_files(example_folder).items()}
    assert {name: after[name] for name in before} == before
    other = fresh(source, tmp_path, "other")
    put_bytes(other.recipe_file("garlic-broccoli"), S09_FILE.encode("utf-8"))
    for argv in (
        ["show", "garlic-broccoli"],
        ["show", "garlic-broccoli", "--lang", "zh"],
        ["list"],
        ["check"],
    ):
        assert at(home, example_folder, *argv) == at(home, other, *argv), argv
    code, shown, error = at(home, example_folder, "show", "garlic-broccoli")
    assert (code, error) == (0, "")
    assert shown.startswith("Garlic broccoli  蒜蓉西兰花\nServings: 2   Tags: quick, vegetarian\n")
    code, listed, error = at(home, example_folder, "list")
    rows = listed.split("\n")
    first = next(index for index, row in enumerate(rows) if row.startswith("cola-wings"))
    assert rows[first + 1].startswith("garlic-broccoli")
    assert (code, rows[-2], error) == (0, "8 recipes.", "")
    checked = [AFTER[0].replace("7 recipes", "8 recipes"), *AFTER[1:]]
    assert at(home, example_folder, "check") == (0, lines_text(*checked), "")


def _recipe_files(folder: DataFolder) -> dict[str, Path]:
    """Gives the files of ``recipes/`` by name."""
    return {path.name: path for path in (folder.root / "recipes").iterdir()}


def test_f15_t09_an_id_that_exists_is_asked_again_and_an_empty_answer_ends_add(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype and v0.2-S11: six lines, and no change of the folder."""
    home = make_home(tmp_path)
    root = example_folder.root
    first = snapshot(root)
    exists = id_exists("tomato-egg")
    result = add(home, example_folder, ["tomato-egg", ""])
    lines = [ID_PROMPT[0] + "tomato-egg", exists[0], ID_PROMPT[0]]
    assert result == (0, lines_text(*lines), "")
    assert snapshot(root) == first
    result = add(home, example_folder, ["tomato-egg", ""], "--lang", "zh")
    lines = [ID_PROMPT[1] + "tomato-egg", exists[1], ID_PROMPT[1]]
    assert result == (0, lines_text(*lines), "")
    assert snapshot(root) == first
    assert add(home, example_folder, [""], "--lang", "zh") == (0, lines_text(ID_PROMPT[1]), "")
    assert snapshot(root) == first
    assert add(home, example_folder, []) == (0, lines_text(ID_PROMPT[0]), "")
    assert snapshot(root) == first
    assert add(home, example_folder, ["   "]) == (0, lines_text(ID_PROMPT[0] + "   "), "")
    assert snapshot(root) == first
    result = add(home, example_folder, EXISTS_RICE)
    expected = [ID_PROMPT[0] + " rice\t", id_exists("rice")[0]]
    for name in ("tomato-egg-noodles", "choy-sum"):
        expected += [ID_PROMPT[0] + name, id_exists(name)[0]]
    assert result == (0, lines_text(*expected, ID_PROMPT[0]), "")
    assert snapshot(root) == first
