"""Tests of F10 for the count line under the table, and for a word that is empty (T10, T11)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import no_data_folder
from f07_changes import broken_settings, catalog_brace, mapo_mistake
from f09_support import at, made, no_catalog, no_recipes_folder, rice_bowl
from f09_texts import (
    E_BRACE,
    E_MAPO,
    E_NO_CATALOG,
    E_NO_RECIPES,
    E_RICE_BOWL,
    E_SETTINGS,
    EN,
    ZH,
    stop,
)
from f10_support import Case, chinese_settings, real_help, searches
from f10_texts import (
    BLOCK_A,
    NOODLE_FOUND,
    NOODLE_FOUND_ZH,
    PROTOTYPE_ZH,
    SCALLION_QUICK_TABLE,
    TOMATO_TABLE,
    TOMATO_TABLE_ZH,
    empty_word,
    found,
    no_option,
    none,
)
from recipe_menu.datafile import DataFolder

LONG_WORD = "9" * 5000
NAMED_ONCE: list[Case] = [
    (("scallion", "QUICK", "noodle"), NOODLE_FOUND),
    (("mapo", "--lang", "zh"), BLOCK_A[("mapo", "--lang", "zh")]),
    (("葱", "quick", "面", "--lang", "zh"), NOODLE_FOUND_ZH),
    (("egg", "egg"), found(TOMATO_TABLE, '2 recipes match "egg".')),
    (("egg", "egg", "--lang", "zh"), found(TOMATO_TABLE_ZH, "2 个菜谱匹配“egg”。")),
    (("egg", "EGG"), found(TOMATO_TABLE, '2 recipes match "egg" and "EGG".')),
    (("egg", "EGG", "--lang", "zh"), found(TOMATO_TABLE_ZH, "2 个菜谱同时匹配“egg”和“EGG”。")),
    (("egg", " egg"), found(TOMATO_TABLE, '2 recipes match "egg" and " egg".')),
    (("葱", "quick", "葱"), found(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')),
    (("葱", "quick", "葱", "--lang", "zh"), PROTOTYPE_ZH),
]
NO_MATCH: list[Case] = [
    (("lamb", "lamb"), none('No recipe matches "lamb".')),
    (("lamb", "lamb", "--lang", "zh"), none("没有菜谱匹配“lamb”。")),
    (("quick", "1"), none('No recipe matches "quick" and "1".')),
    (("quick", "1", "--lang", "zh"), none("没有菜谱同时匹配“quick”和“1”。")),
    (("lamb", "beef", "fish"), none('No recipe matches "lamb", "beef", and "fish".')),
    (
        ("lamb", "beef", "fish", "--lang", "zh"),
        none("没有菜谱同时匹配“lamb”、“beef”和“fish”。"),
    ),
]
AS_TYPED: list[Case] = [
    (('say "hi"',), none('No recipe matches "say "hi"".')),
    (('say "hi"', "--lang", "zh"), none('没有菜谱匹配“say "hi"”。')),
    (("{words}",), none('No recipe matches "{words}".')),
    (("{count}", "--lang", "zh"), none("没有菜谱匹配“{count}”。")),
    (("to\nmato",), none('No recipe matches "to\nmato".')),
    (("番茄\n",), found(TOMATO_TABLE, '2 recipes match "番茄\n".')),
    ((LONG_WORD,), none(f'No recipe matches "{LONG_WORD}".')),
]
EMPTY_LINES = [
    [""],
    [" "],
    ["\t"],
    ["\u00a0"],
    ["\u3000"],
    ["\u2028"],
    ["番茄", ""],
    ["", "番茄"],
    [" ", "lamb"],
    ["番茄", "\u3000"],
    ["", ""],
]
# The five folders of F10-T11 input 3: the change, the words, their language, and the problem
# that the search for tomato stops at.
BROKEN = [
    (no_catalog, [""], EN, E_NO_CATALOG),
    (catalog_brace, [" ", "--lang", "zh"], ZH, E_BRACE),
    (no_recipes_folder, ["\u3000"], EN, E_NO_RECIPES),
    (rice_bowl, [""], EN, E_RICE_BOWL),
    (mapo_mistake, ["", "番茄"], EN, E_MAPO),
]


def test_f10_t10_the_count_line_names_each_word_once_as_typed_and_picks_its_text_by_count(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """One word and several words, a repeated word, no match, and words with odd characters."""
    home = make_home(tmp_path)
    searches(home, example_folder, NAMED_ONCE)
    searches(home, example_folder, NO_MATCH)
    searches(home, example_folder, AS_TYPED)


def _check_broken_folders(example: DataFolder, tmp_path: Path, home: Path) -> None:
    """Checks that the empty word comes before the error of each file, which ``search`` reports."""
    for number, (change, words, lang, problem) in enumerate(BROKEN):
        folder = made(example, tmp_path, f"broken{number}", change)
        assert at(home, folder, "search", *words) == empty_word(lang)
        assert at(home, folder, "search", "番茄") == stop(problem)


def test_f10_t11_a_word_with_nothing_in_it_gives_the_empty_word_error_with_exit_code_2(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The error comes before any read, so a broken folder gives the same line."""
    home = make_home(tmp_path)
    lines: list[Case] = [(tuple(words), empty_word()) for words in EMPTY_LINES]
    lines += [
        (("", "--lang", "zh"), empty_word(ZH)),
        (("番茄", " ", "--lang", "zh"), empty_word(ZH)),
    ]
    searches(home, example_folder, lines)
    chinese = made(example_folder, tmp_path, "chinese", chinese_settings)
    searches(home, chinese, [(("",), empty_word(ZH)), (("", "--lang", "en"), empty_word())])
    _check_broken_folders(example_folder, tmp_path, home)
    missing = tmp_path / "missing"
    assert at(home, missing, "search", "") == no_data_folder(missing)
    assert at(home, missing, "search", "", "--lang", "zh") == no_data_folder(missing, ZH)
    settings = made(example_folder, tmp_path, "settings", broken_settings)
    assert at(home, settings, "search", "") == stop(E_SETTINGS)
    assert at(home, example_folder, "search", "", "--help") == real_help(home)
    assert at(home, example_folder, "search", "", "--tag", "x") == no_option("--tag")
