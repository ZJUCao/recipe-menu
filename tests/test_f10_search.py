"""Tests of F10 for ``recipe-menu search`` in the examples of the design and prototype."""

from pathlib import Path

from f05_support import make_home
from f07_changes import mapo_mistake
from f09_support import at, empty_recipes
from f09_texts import E_MAPO, ZH, err, stop
from f10_support import searches
from f10_texts import (
    AND_EGG_FOUND,
    EMPTY,
    EMPTY_ZH,
    MAPO_FOUND,
    NOODLE_FOUND,
    NOODLE_FOUND_ZH,
    PORK_FOUND,
    PROTOTYPE_ZH,
    SCALLION_QUICK_TABLE,
    TOMATO,
    TOMATO_TABLE,
    TOMATO_TABLE_ZH,
    TOMATO_ZH,
    found,
    no_option,
    none,
    too_few,
)
from recipe_menu.datafile import DataFolder

NONE_PAIR = none("没有菜谱同时匹配“豆腐”和“quick”。")


def _prototype_and_rules(home: Path, example: DataFolder) -> None:
    """Checks the five outputs of the prototype and the rules of choices 3 to 6."""
    searches(
        home,
        example,
        [
            (("番茄",), TOMATO),
            (("TOMATO",), found(TOMATO_TABLE, '2 recipes match "TOMATO".')),
            (("葱", "quick", "--lang", "zh"), PROTOTYPE_ZH),
            (("lamb",), none('No recipe matches "lamb".')),
            (("豆腐", "quick", "--lang", "zh"), NONE_PAIR),
            (("番茄", "--lang", "zh"), TOMATO_ZH),
            (("mapo",), MAPO_FOUND),
            (("pork",), PORK_FOUND),
            (("and egg",), AND_EGG_FOUND),
            (("scallion", "QUICK", "noodle"), NOODLE_FOUND),
            (("葱", "quick", "面", "--lang", "zh"), NOODLE_FOUND_ZH),
            (("egg", "egg"), found(TOMATO_TABLE, '2 recipes match "egg".')),
            (("egg", "EGG"), found(TOMATO_TABLE, '2 recipes match "egg" and "EGG".')),
            (("\u3000番茄",), found(TOMATO_TABLE, '2 recipes match "\u3000番茄".')),
        ],
    )


def _things_that_do_not_count(home: Path, example: DataFolder) -> None:
    """Checks a note, a step, a category, an ID, a look-alike letter, and a no-break space."""
    words = ["wedges", "切块", "scramble", "dairy", "tomato-egg", "\uff34omato", "tomato\u00a0and"]
    searches(home, example, [((word,), none(f'No recipe matches "{word}".')) for word in words])


def _the_errors(home: Path, example: DataFolder) -> None:
    """Checks the empty words, the lines that ``cli`` rejects, and the mistake in ``mapo-tofu``."""
    for words in ([""], ["番茄", "\u3000"], [" ", "lamb"]):
        assert at(home, example, "search", *words) == err(2, [EMPTY])
    assert at(home, example, "search", "", "--lang", "zh") == err(2, [EMPTY_ZH])
    assert at(home, example, "search") == too_few()
    assert at(home, example, "search", "番茄", "--tag", "quick") == no_option("--tag")
    mapo_mistake(example.root)
    assert at(home, example, "search", "番茄") == stop(E_MAPO)
    assert at(home, example, "search", "") == err(2, [EMPTY])
    assert at(home, example, "search", "番茄", "--lang", "zh") == stop(E_MAPO, ZH)
    empty_recipes(example.root)
    assert at(home, example, "search", "番茄") == none('No recipe matches "番茄".')


def test_f10_t03_the_example_of_the_search_command_gives_the_outputs_of_its_rules(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.2, in order, with the real commands."""
    home = make_home(tmp_path)
    _prototype_and_rules(home, example_folder)
    _things_that_do_not_count(home, example_folder)
    _the_errors(home, example_folder)


def test_f10_t04_the_prototype_gives_each_output_in_both_languages(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S11 at ``main``, and the same lines in the other language."""
    home = make_home(tmp_path)
    scallion_quick = found(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')
    searches(
        home,
        example_folder,
        [
            (("番茄",), TOMATO),
            (("TOMATO",), found(TOMATO_TABLE, '2 recipes match "TOMATO".')),
            (("葱", "quick", "--lang", "zh"), PROTOTYPE_ZH),
            (("lamb",), none('No recipe matches "lamb".')),
            (("豆腐", "quick", "--lang", "zh"), NONE_PAIR),
            (("番茄", "--lang", "zh"), TOMATO_ZH),
            (("TOMATO", "--lang", "zh"), found(TOMATO_TABLE_ZH, "2 个菜谱匹配“TOMATO”。")),
            (("葱", "quick"), scallion_quick),
            (("lamb", "--lang", "zh"), none("没有菜谱匹配“lamb”。")),
            (("豆腐", "quick"), none('No recipe matches "豆腐" and "quick".')),
        ],
    )
