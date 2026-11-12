"""Tests of F04 for the values RecipeIngredient, Steps, and Recipe (T01 to T05)."""

from fractions import Fraction

import pytest

from f04_support import (
    EN,
    ZH,
    both,
    chinese,
    choy_lines,
    choy_name,
    choy_steps,
    choy_sum,
    qty,
    quick,
    tomato,
    wedges,
)
from recipe_menu.lang import BiText
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.units import TO_TASTE, Unit


def test_f04_t01_a_line_keeps_its_ingredient_quantity_and_note() -> None:
    """The note is None by default and may have one language. A blank language is rejected."""
    grams = qty(300, Unit.G)
    line = RecipeIngredient(tomato, grams, wedges)
    assert line.ingredient is tomato
    assert line.quantity == grams
    assert line.note == wedges
    assert line == RecipeIngredient(tomato, grams, wedges)
    to_taste = RecipeIngredient(tomato, TO_TASTE)
    assert to_taste.quantity.is_to_taste
    assert to_taste.note is None
    assert RecipeIngredient(tomato, TO_TASTE, BiText(zh="切块")).note == BiText(zh="切块")
    assert RecipeIngredient(tomato, TO_TASTE, BiText(en="chopped")).note == BiText(en="chopped")
    blanks = (
        BiText("chopped", " "),
        BiText(en=""),
        BiText(zh=""),
        BiText(zh="\u3000"),
        BiText("\t\n", "切块"),
        BiText("", ""),
    )
    for note in blanks:
        with pytest.raises(ValueError):
            RecipeIngredient(tomato, TO_TASTE, note)


def test_f04_t02_get_falls_back_and_exact_does_not() -> None:
    """``get`` gives the other language when the asked one is None, ``exact`` gives None."""
    only_zh = Steps(zh=chinese)
    assert only_zh.get(EN) == chinese
    assert only_zh.get(ZH) == chinese
    assert only_zh.exact(ZH) == chinese
    assert only_zh.exact(EN) is None
    assert both.get(EN) == ("Cut the tomatoes into wedges.",)
    assert both.exact(EN) == ("Cut the tomatoes into wedges.",)
    assert both.get(ZH) == ("番茄切块。",)
    assert both.exact(ZH) == ("番茄切块。",)
    only_en = Steps(en=("Stir.",))
    assert only_en.get(ZH) == ("Stir.",)
    assert only_en.exact(ZH) is None


def test_f04_t03_steps_reject_wrong_calls() -> None:
    """No language, an empty tuple, or a blank step is a ValueError. A wrong type is a TypeError."""
    value_errors = (
        {},
        {"en": None, "zh": None},
        {"en": ()},
        {"zh": ()},
        {"en": (), "zh": ("番茄切块。",)},
        {"en": ("Stir.", " ")},
        {"zh": ("",)},
        {"zh": ("\u3000",)},
    )
    for kwargs in value_errors:
        with pytest.raises(ValueError):
            Steps(**kwargs)
    type_errors = (
        {"en": ["Stir."]},
        {"en": []},
        {"zh": "番茄切块。"},
        {"en": ("Stir.", 3)},
        {"zh": (None,)},
        {"en": ("Stir.",), "zh": ["番茄切块。"]},
    )
    for kwargs in type_errors:
        with pytest.raises(TypeError):
            Steps(**kwargs)


def test_f04_t04_a_recipe_keeps_its_fields_and_rejects_a_wrong_id_or_name() -> None:
    """The design's example, with the empty tags and ingredients and the ID rule."""
    recipe = Recipe("choy-sum", choy_name, 2, (quick,), choy_lines, choy_steps)
    Recipe("choy-sum", choy_name, 2, (), (), choy_steps)
    Recipe("2-minute-noodles", BiText(zh="清炒菜心"), 2, (), choy_lines, choy_steps)
    assert recipe.name.get(ZH) == "清炒菜心"
    assert recipe.ingredients[0].ingredient is choy_sum
    assert recipe.tags == (quick,)
    assert recipe == Recipe("choy-sum", choy_name, 2, (quick,), choy_lines, choy_steps)
    for recipe_id in ("Choy Sum", "", "choy_sum", "-choy-sum", "choy-sum ", "con"):
        with pytest.raises(ValueError):
            Recipe(recipe_id, choy_name, 2, (), choy_lines, choy_steps)
    blank_names = (BiText(zh=""), BiText("Stir-fried choy sum", " "), BiText(en="\u3000"))
    for name in blank_names:
        with pytest.raises(ValueError):
            Recipe("choy-sum", name, 2, (), choy_lines, choy_steps)


def test_f04_t05_servings_are_an_int_from_1_to_100_and_not_a_bool() -> None:
    """A bool raises TypeError, even with the value 0 or 1."""
    for servings in (1, 2, 100):
        recipe = Recipe("choy-sum", choy_name, servings, (), choy_lines, choy_steps)
        assert recipe.servings == servings
    for servings in (0, 101, -1):
        with pytest.raises(ValueError):
            Recipe("choy-sum", choy_name, servings, (), choy_lines, choy_steps)
    wrong_types = (True, False, 2.0, "2", Fraction(2), None)
    for servings in wrong_types:
        with pytest.raises(TypeError):
            Recipe("choy-sum", choy_name, servings, (), choy_lines, choy_steps)
