"""Tests of F10 for the places where a word can appear, and for what does not count (T05, T06)."""

from pathlib import Path

from f05_support import make_home
from f09_support import extra_recipes, made, soup
from f10_support import Case, egg_in_english, eggplant, lines_of, searches, span
from f10_texts import BLOCK_A, BLOCK_B, none
from recipe_menu.datafile import DataFolder

# The words of F10-T06 input 1, and the one word of each of the other inputs.
NOT_COUNTED = [
    "wedges",
    "切块",
    "crushed",
    "scramble",
    "热锅",
    "dairy",
    "蛋奶",
    "produce",
    "mapo-tofu",
    "cola-wings",
    "2",
    "300",
    "tbsp",
    "适量",
    "片",
    "broccoli",
    "西兰花",
]


def _no_match(word: str, lang: str = "en") -> Case:
    """Gives the words line and the result of ``search`` with one word that matches nothing."""
    if lang == "zh":
        return (word, "--lang", "zh"), none(f"没有菜谱匹配“{word}”。")
    return (word,), none(f'No recipe matches "{word}".')


def test_f10_t05_a_word_appears_in_a_name_an_ingredient_or_a_tag_in_either_language(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The first 13 lines of block A, a file that writes ``EGG``, and the extra recipes."""
    home = make_home(tmp_path)
    searches(home, example_folder, span(BLOCK_A, ("炒蛋",), ("red-braised",)))
    english = made(example_folder, tmp_path, "egg", egg_in_english)
    egg_lines = lines_of(BLOCK_A, ("鸡蛋",), ("鸡蛋", "--lang", "zh"))
    searches(home, english, egg_lines)
    extra = made(example_folder, tmp_path, "extra", extra_recipes)
    searches(home, extra, list(BLOCK_B.items()))


def test_f10_t06_nothing_else_counts_no_note_step_id_servings_quantity_unit_or_category(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Each such word gives the one line of no match, with exit code 0."""
    home = make_home(tmp_path)
    cases = [_no_match(word) for word in NOT_COUNTED]
    cases += [_no_match("切块", "zh"), _no_match("dairy", "zh")]
    searches(home, example_folder, cases)
    extra = made(example_folder, tmp_path, "extra", extra_recipes)
    searches(home, extra, [_no_match(word) for word in ("room", "打散", "烧开")])
    searches(home, made(example_folder, tmp_path, "eggplant", eggplant), [_no_match("strips")])
    soup_folder = made(example_folder, tmp_path, "soup", soup)
    searches(home, soup_folder, [_no_match("soup"), _no_match("汤", "zh")])
