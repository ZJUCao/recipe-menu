"""Tests of F12 for the arguments of ``build_shopping_list`` and its bounds (T26 to T28)."""

import dataclasses
from fractions import Fraction
from types import MappingProxyType

import pytest

from f06_support import example_menu, example_settings
from f12_support import (
    EN,
    EVERY_MEAL,
    NO_PANTRY,
    ZH,
    category,
    code_catalog,
    code_pantry,
    code_recipes,
    every_slot,
    expect,
    expected_w47,
    group,
    hold,
    menu_of,
    recipes_of,
    texts,
)
from recipe_menu.catalog import Catalog, Ingredient, Pantry
from recipe_menu.lang import BiText
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.shopping import build_shopping_list
from recipe_menu.units import TO_TASTE, Quantity, Unit


def test_f12_t26_the_mapping_may_hold_other_recipes_and_no_argument_changes() -> None:
    """Any ``Mapping`` works, extra recipes are not looked at, and two calls give equal lists."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    menu = example_menu(example_settings())
    recipes = code_recipes(catalog)
    before, keys = hold(recipes)
    lard = Ingredient(BiText("Lard", "猪油"), category(catalog, "staples"))
    lard_line = RecipeIngredient(lard, Quantity(Fraction(100), Unit.G))
    lard_cake = Recipe("lard-cake", BiText("lard-cake"), 2, (), (lard_line,), Steps(("Cook.",)))
    extended = {**recipes, "lard-cake": lard_cake, "other-id": recipes["rice"]}
    expected = expected_w47(catalog)

    for mapping in (recipes, MappingProxyType(recipes), extended, recipes):
        shopping = build_shopping_list(menu, mapping, catalog, pantry)
        assert shopping == expected
        assert hash(shopping) == hash(expected)
    assert recipes == before
    assert list(recipes) == keys
    assert len(extended) == len(recipes) + 2


def test_f12_t27_a_wrong_call_raises_value_error() -> None:
    """Each wrong call breaks one row of the Errors table of 2.5."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    menu = example_menu(example_settings())
    recipes = code_recipes(catalog)
    seasonings = category(catalog, "seasonings")
    lard = Ingredient(BiText("Lard", "猪油"), category(catalog, "staples"))
    pepper = Ingredient(BiText("Black pepper", "黑胡椒"), seasonings)
    same_names = Ingredient(BiText("White pepper", "白胡椒粉"), seasonings, Unit.PIECE)
    noodles = recipes["tomato-egg-noodles"]
    more = (*noodles.ingredients, RecipeIngredient(pepper, TO_TASTE))
    changed = tuple(
        RecipeIngredient(same_names, item.quantity)
        if item.ingredient.name.zh == "白胡椒粉"
        else item
        for item in noodles.ingredients
    )
    without_cola = {name: item for name, item in recipes.items() if name != "cola-wings"}
    no_cola = Catalog(catalog.categories, catalog.ingredients[:-1], ())
    calls = (
        ({}, catalog, pantry),
        (without_cola, catalog, pantry),
        ({**recipes, "rice": recipes["choy-sum"]}, catalog, pantry),
        (recipes, no_cola, pantry),
        ({**recipes, noodles.id: dataclasses.replace(noodles, ingredients=more)}, catalog, pantry),
        (
            {**recipes, noodles.id: dataclasses.replace(noodles, ingredients=changed)},
            catalog,
            pantry,
        ),
        (recipes, catalog, Pantry(frozenset({lard}))),
        (recipes, catalog, Pantry(pantry.ingredients | {lard})),
    )
    for mapping, wrong_catalog, wrong_pantry in calls:
        with pytest.raises(ValueError):
            build_shopping_list(menu, mapping, wrong_catalog, wrong_pantry)
    with pytest.raises(ValueError):
        build_shopping_list(menu_of(week=46), {}, catalog, Pantry(frozenset({lard})))


def test_f12_t28_the_bounds_of_choice_10_give_exact_sums_and_texts(
    default_int_limit: None,
) -> None:
    """The largest, the smallest, and the odd amounts give exact sums and texts with no error."""
    catalog = code_catalog()
    _check_largest(catalog)
    _check_smallest(catalog)
    _check_odd_servings(catalog)


def _check_largest(catalog: Catalog) -> None:
    """Checks 100 servings of 15-digit amounts in 63 dishes."""
    big = "999999999999999"
    mapping = recipes_of(catalog, f"big 1: 番茄 {big} kg, 生抽 {big} L, 可乐 {big} 罐")
    menu = every_slot("big 100", times=3)
    groups = (
        group(catalog, "produce", "番茄: 6299999999999993700000 G"),
        group(catalog, "seasonings", "生抽: 6299999999999993700000 ML"),
        group(catalog, "other", "可乐: 6299999999999993700 CAN"),
    )
    shopping = build_shopping_list(menu, mapping, catalog, NO_PANTRY)
    assert shopping == expect(catalog, 48, 21, 63, groups)
    amount = "6299999999999993700"
    assert texts(shopping, EN) == [f"{amount} kg", f"{amount} L", f"{amount} cans"]
    assert texts(shopping, ZH) == [f"{amount} kg", f"{amount} L", f"{amount} 罐"]


def _check_smallest(catalog: Catalog) -> None:
    """Checks the smallest amount of a recipe of 100 servings, cooked for 1."""
    tiny = "0.00000000000001"
    mapping = recipes_of(catalog, f"tiny 100: 番茄 {tiny} g, 鸡蛋 {tiny}, 生抽 {tiny} ml")
    small = f"1/{10**16}"
    groups = (
        group(catalog, "produce", f"番茄: {small} G"),
        group(catalog, "eggs", f"鸡蛋: {small} PIECE"),
        group(catalog, "seasonings", f"生抽: {small} ML"),
    )
    shopping = build_shopping_list(
        menu_of("monday dinner: tiny 1", meals=EVERY_MEAL), mapping, catalog, NO_PANTRY
    )
    assert shopping == expect(catalog, 48, 1, 1, groups)
    assert texts(shopping, EN) == ["1 g", "1 piece", "1 ml"]
    assert texts(shopping, ZH) == ["1 g", "1 个", "1 ml"]


def _check_odd_servings(catalog: Catalog) -> None:
    """Checks 97 dishes of 1 serving from a recipe of 97 servings."""
    mapping = recipes_of(catalog, "odd 97: 鸡蛋 1, 番茄 1 g, 生抽 1 ml")
    menu = menu_of("monday dinner: " + ", ".join(["odd 1"] * 97), meals=EVERY_MEAL)
    groups = (
        group(catalog, "produce", "番茄: 1 G"),
        group(catalog, "eggs", "鸡蛋: 1 PIECE"),
        group(catalog, "seasonings", "生抽: 1 ML"),
    )
    shopping = build_shopping_list(menu, mapping, catalog, NO_PANTRY)
    assert shopping == expect(catalog, 48, 1, 97, groups)
    assert texts(shopping, EN) == ["1 g", "1 piece", "1 ml"]
    assert texts(shopping, ZH) == ["1 g", "1 个", "1 ml"]
