"""Tests of F10 for how a word is compared and how several words combine (T07 to T09)."""

from pathlib import Path

from f05_support import make_home
from f09_support import at, made
from f10_support import creme, eggplant, searches, span
from f10_texts import (
    ALL_THREE_TABLE,
    ALL_THREE_TABLE_ZH,
    BLOCK_A,
    BLOCK_C,
    BLOCK_D,
    SCALLION_QUICK_TABLE,
    SCALLION_QUICK_TABLE_ZH,
    TOMATO_TABLE,
    found,
    no_option,
    none,
)
from recipe_menu.catalog import matching_form
from recipe_menu.datafile import DataFolder

TRIMMED = ["tomato", "Tomato", "tOmAtO", " tomato ", "\u00a0番茄\t", "\u3000TOMATO\u3000"]
# Words that find nothing: whitespace inside, look-alike letters, and invisible characters.
FINDS_NOTHING = [
    "and  egg",
    "choy\u00a0sum",
    "stir fry",
    "番\u200b茄",
    "\u200b",
    "\ufeff番茄",
    "T\u043emato",
    "R\u0130CE",
    "-x",
]
CASE_ONLY = ["CR\u00c8ME", "creme", "Cre\u0300me"]


def _check_matching_form() -> None:
    """Checks the example of 3.1."""
    assert matching_form(" TOMATO\t") == "tomato"
    assert matching_form("\u3000番茄") == "番茄"
    assert matching_form("Choy  Sum") == "choy  sum"
    assert matching_form("\u212aale") == "\u212aale"
    assert matching_form("\uff34omato") == "\uff34omato"
    assert matching_form("\u3000") == ""
    assert matching_form("egg") in matching_form("Eggplant")


def _no_match_text(word: str) -> str:
    """Gives the line of no match for one word, in English."""
    return f'No recipe matches "{word}".'


def test_f10_t07_a_word_appears_in_a_text_by_the_matching_form_and_nothing_is_normalized(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 3.1, the words of choice 4, and the two folders with new names."""
    home = make_home(tmp_path)
    _check_matching_form()
    trimmed = [((word,), found(TOMATO_TABLE, f'2 recipes match "{word}".')) for word in TRIMMED]
    searches(home, example_folder, trimmed)
    searches(home, example_folder, span(BLOCK_A, ("choy sum",), ("MAPO", "--lang", "zh")))
    nothing = [((word,), none(_no_match_text(word))) for word in FINDS_NOTHING]
    searches(home, example_folder, nothing)
    assert at(home, example_folder, "search", "--x") == no_option("--x")
    egg = made(example_folder, tmp_path, "eggplant", eggplant)
    searches(home, egg, list(BLOCK_C.items()))
    french = made(example_folder, tmp_path, "creme", creme)
    searches(home, french, list(BLOCK_D.items()))
    only = [((word,), none(_no_match_text(word))) for word in CASE_ONLY]
    only.insert(1, (("CR\u00c8ME", "--lang", "zh"), none("没有菜谱匹配“CR\u00c8ME”。")))
    searches(home, french, only)


def test_f10_t08_a_recipe_matches_when_every_word_appears_in_one_of_its_places(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Two words may appear in different places, and the order changes only the count line."""
    home = make_home(tmp_path)
    searches(
        home,
        example_folder,
        [
            (("quick", "葱"), found(SCALLION_QUICK_TABLE, '2 recipes match "quick" and "葱".')),
            (
                ("quick", "葱", "--lang", "zh"),
                found(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“quick”和“葱”。"),
            ),
            (("tomato", "egg"), found(TOMATO_TABLE, '2 recipes match "tomato" and "egg".')),
            *span(BLOCK_A, ("egg", "noodle"), ("home", "葱")),
            (
                ("tomato", "egg", "quick", "葱"),
                found(ALL_THREE_TABLE, '2 recipes match "tomato", "egg", "quick", and "葱".'),
            ),
            (
                ("tomato", "egg", "quick", "葱", "--lang", "zh"),
                found(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“tomato”、“egg”、“quick”和“葱”。"),
            ),
            (("egg", "spicy"), none('No recipe matches "egg" and "spicy".')),
            (("egg", "spicy", "--lang", "zh"), none("没有菜谱同时匹配“egg”和“spicy”。")),
            (("葱", "quick", "lamb"), none('No recipe matches "葱", "quick", and "lamb".')),
            (
                ("葱", "quick", "lamb", "--lang", "zh"),
                none("没有菜谱同时匹配“葱”、“quick”和“lamb”。"),
            ),
        ],
    )


def test_f10_t09_the_matched_in_cell_names_each_place_once_in_the_order_of_the_table(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The places of several words combine, whatever the order of the words."""
    home = make_home(tmp_path)
    searches(
        home,
        example_folder,
        [
            (("quick", "番茄"), found(ALL_THREE_TABLE, '2 recipes match "quick" and "番茄".')),
            (("番茄", "tomato"), found(TOMATO_TABLE, '2 recipes match "番茄" and "tomato".')),
            (
                ("番茄", "快手", "--lang", "zh"),
                found(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“番茄”和“快手”。"),
            ),
            *span(BLOCK_A, ("米饭", "主食"), ("scallion", "QUICK", "noodle", "--lang", "zh")),
        ],
    )
