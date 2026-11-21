"""Tests of F15 for the text of the file that ``add`` writes (T16)."""

import re
from pathlib import Path

from f05_support import make_home
from f13_support import pristine
from f15_blocks import BASE_FILE, TEXT_G
from f15_support import ESCAPES, add, answers, fresh
from f15_texts import EN_NAME_PROMPT, ZH_NAME_PROMPT, recipe_path, saved
from recipe_menu.catalog import read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.recipes import read_recipe

CTRL_LINE = re.compile(r'name = \{ zh = "中\\u001[bB]文", en = "E\\u007[fF]N" \}')


def _check_texts(folder: DataFolder, result: tuple[int, str, str]) -> None:
    """Checks the result and the file of ``add`` with ESCAPES."""
    code, out, err = result
    assert (code, err) == (0, "")
    lines = out.split("\n")
    assert lines[1:3] == [ZH_NAME_PROMPT[0] + ESCAPES[1], EN_NAME_PROMPT[0] + ESCAPES[2]]
    assert lines[-2:-1] == [saved(recipe_path(folder, "odd-text"))[0]]
    data = folder.recipe_file("odd-text").read_bytes()
    assert data == TEXT_G.encode("utf-8")
    assert b"\r" not in data
    assert not data.startswith(b"\xef\xbb\xbf")


def test_f15_t16_the_file_holds_the_answers_as_toml_strings_that_read_back_exactly(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: ESCAPES and its read-back, control characters, and a character above the BMP."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = fresh(source, tmp_path, "first")
    _check_texts(first, add(home, first, ESCAPES))
    catalog, _ = read_catalog(first)
    recipe, problems = read_recipe(first, catalog, "odd-text")
    assert problems == ()
    assert recipe is not None
    assert (recipe.name.zh, recipe.name.en) == (ESCAPES[1], ESCAPES[2])
    assert recipe.steps.zh == (ESCAPES[7], ESCAPES[8])
    assert recipe.steps.en == (ESCAPES[10],)
    second = fresh(source, tmp_path, "second")
    result = add(home, second, answers("ctrl-text", zh_name="中\x1b文", en_name="E\x7fN"))
    code, out, err = result
    assert (code, err) == (0, "")
    assert out.split("\n")[-2:-1] == [saved(recipe_path(second, "ctrl-text"))[0]]
    data = second.recipe_file("ctrl-text").read_text(encoding="utf-8")
    assert CTRL_LINE.fullmatch(data.split("\n")[0])
    catalog, _ = read_catalog(second)
    recipe, problems = read_recipe(second, catalog, "ctrl-text")
    assert problems == ()
    assert recipe is not None
    assert (recipe.name.zh, recipe.name.en) == ("中\x1b文", "E\x7fN")
    third = fresh(source, tmp_path, "third")
    assert add(home, third, answers(en_steps=["Rice bowl \U0001f35a"]))[0] == 0
    expected = BASE_FILE.replace("Cut the tomatoes.", "Rice bowl \U0001f35a")
    assert third.recipe_file("new-dish").read_bytes() == expected.encode("utf-8")
