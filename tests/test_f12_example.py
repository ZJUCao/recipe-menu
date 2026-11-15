"""Tests of F12 for the example of ``build_shopping_list`` in design 2.5 (T14)."""

from fractions import Fraction

import pytest

from f12_support import (
    EN,
    EVERY_MEAL,
    S16_EN,
    S18_CELLS,
    W47_EN,
    W47_ZH,
    ZH,
    category,
    code_catalog,
    code_pantry,
    code_recipes,
    find,
    menu_of,
    names_of,
    texts,
    written,
)
from recipe_menu.catalog import Catalog, Ingredient, Pantry
from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek, WeekMenu
from recipe_menu.recipes import Recipe
from recipe_menu.shopping import ShoppingList, build_shopping_list
from recipe_menu.units import Quantity, Unit

type Recipes = dict[str, Recipe]

W47_CELLS = (
    "monday dinner: tomato-egg 2, choy-sum 2, rice 2",
    "tuesday dinner: mapo-tofu 2, rice 2",
    "saturday lunch: tomato-egg-noodles 2",
    "sunday dinner: cola-wings 4, choy-sum 4, rice 4",
)


def test_f12_t14_the_example_of_build_shopping_list() -> None:
    """The example week, the weeks of v0.1-S16 and v0.1-S18, a week with no dish, and the errors."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    recipes = code_recipes(catalog)

    w47 = menu_of(*W47_CELLS, week=47)
    shopping = build_shopping_list(w47, recipes, catalog, pantry)
    week = (shopping.week, shopping.meal_count, shopping.dish_count)
    assert week == (IsoWeek(2026, 47), 4, 9)
    assert written(shopping, ZH) == W47_ZH
    assert written(shopping, EN) == W47_EN
    assert names_of(shopping.pantry_used, ZH) == ["食用油", "盐", "糖", "生抽", "花椒"]
    assert texts(shopping, EN)[:5] == ["600 g", "1.5 kg", "5 stalks", "6 slices", "11 cloves"]
    assert texts(shopping, EN)[-3:] == ["15 ml", "to taste", "2 cans"]
    assert shopping.groups[0].lines[1].amounts == (Quantity(Fraction(1500), Unit.G),)

    _check_s16(catalog, pantry, recipes)
    _check_s18(catalog, pantry, recipes)
    _check_empty_and_wrong(catalog, pantry, recipes, w47)


def _check_s16(catalog: Catalog, pantry: Pantry, recipes: Recipes) -> None:
    """Checks the week of v0.1-S16: 3 servings of ``tomato-egg`` in Monday breakfast."""
    w48 = menu_of("monday breakfast: tomato-egg 3", meals=EVERY_MEAL)
    s16 = build_shopping_list(w48, {"tomato-egg": recipes["tomato-egg"]}, catalog, pantry)
    assert (s16.meal_count, s16.dish_count) == (1, 1)
    assert written(s16, EN) == S16_EN
    assert s16.groups[1].lines[0].amounts == (Quantity(Fraction(9, 2), Unit.PIECE),)
    assert names_of(s16.pantry_used, EN) == ["Cooking oil", "Salt", "Sugar"]


def _check_s18(catalog: Catalog, pantry: Pantry, recipes: Recipes) -> None:
    """Checks the week of v0.1-S18: amounts that cannot be added share a line."""
    no_soy_sauce = Pantry(pantry.ingredients - {find(catalog, "生抽")})
    s18 = build_shopping_list(menu_of(*S18_CELLS), recipes, catalog, no_soy_sauce)
    by_name = {item.ingredient.name.en: item for entry in s18.groups for item in entry.lines}
    assert by_name["Scallion"].amount_text(EN) == "5 stalks + 1 bunch"
    assert by_name["Scallion"].amount_text(ZH) == "5 根 + 1 把"
    assert by_name["Soy sauce"].amount_text(EN) == "30 ml + 10 g"


def _check_empty_and_wrong(
    catalog: Catalog, pantry: Pantry, recipes: Recipes, w47: WeekMenu
) -> None:
    """Checks a week with no dish and the four wrong calls of the example."""
    empty = build_shopping_list(menu_of(week=46), {}, catalog, pantry)
    assert empty == ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())

    staples = category(catalog, "staples")
    wrong_id = {**recipes, "rice": recipes["choy-sum"]}
    no_cola = Catalog(catalog.categories, catalog.ingredients[:-1], ())
    lard = Pantry(frozenset({Ingredient(BiText("Lard", "猪油"), staples)}))
    with pytest.raises(ValueError):
        build_shopping_list(w47, {}, catalog, pantry)
    with pytest.raises(ValueError):
        build_shopping_list(w47, wrong_id, catalog, pantry)
    with pytest.raises(ValueError):
        build_shopping_list(w47, recipes, no_cola, pantry)
    with pytest.raises(ValueError):
        build_shopping_list(w47, recipes, catalog, lard)
