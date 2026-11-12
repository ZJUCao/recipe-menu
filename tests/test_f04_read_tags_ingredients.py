"""Tests of F04 for read_recipe: the tags and the ingredients (T20 to T26)."""

from dataclasses import replace
from fractions import Fraction

from f03_support import (
    M_ITEM_EMPTY,
    M_ITEM_NOT_A_TABLE,
    M_ITEM_NOT_A_TEXT,
    m_empty_text,
    m_missing_key,
    m_not_a_list,
    m_not_a_text,
    m_unknown_key,
)
from f04_support import (
    INGREDIENTS,
    ITEM_KEYS,
    TAGS,
    check_fails,
    dish,
    egg,
    err,
    home,
    ingredient_n,
    m_amount_unit,
    m_no_unit,
    m_not_a_number,
    m_unknown_ing,
    m_unknown_tag,
    m_zero,
    qty,
    quick,
    read_dish,
    scallion,
    tag_n,
    tomato,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.recipes import RecipeIngredient
from recipe_menu.units import TO_TASTE, Quantity, Unit


def test_f04_t20_a_tag_is_found_by_either_name_and_held_once(folder: DataFolder) -> None:
    """The order is that of the first item that names the tag. Empty lists give empty tuples."""
    recipe, problems = read_dish(folder, tags='["家常", "quick", "快手", " QUICK ", "Home-Style"]')
    assert problems == ()
    assert recipe == replace(dish, tags=(home, quick))
    assert recipe is not None
    assert recipe.tags[0] is home
    assert recipe.tags[1] is quick
    recipe, problems = read_dish(folder, tags="[]", ingredients="[]")
    assert problems == ()
    assert recipe == replace(dish, tags=(), ingredients=())


def test_f04_t21_the_errors_of_the_tags(folder: DataFolder) -> None:
    """Items that are no text or blank are at ``tag N``, and unknown tags are at ``tags``."""
    check_fails(folder, [err(None, m_missing_key("tags"))], tags=None)
    for value in ('"快手"', '{ zh = "快手" }'):
        check_fails(folder, [err(TAGS, m_not_a_list("tags"))], tags=value)
    items = '[3, "", " ", "\u3000", ["快手"], true, " breakfast ", "快手", "breakfast", "dinner"]'
    check_fails(
        folder,
        [
            err(tag_n(1), M_ITEM_NOT_A_TEXT),
            err(tag_n(2), M_ITEM_EMPTY),
            err(tag_n(3), M_ITEM_EMPTY),
            err(tag_n(4), M_ITEM_EMPTY),
            err(tag_n(5), M_ITEM_NOT_A_TEXT),
            err(tag_n(6), M_ITEM_NOT_A_TEXT),
            err(TAGS, m_unknown_tag("breakfast")),
            err(TAGS, m_unknown_tag("breakfast")),
            err(TAGS, m_unknown_tag("dinner")),
        ],
        tags=items,
    )


def test_f04_t22_the_errors_of_the_list_of_ingredients(folder: DataFolder) -> None:
    """A missing key, a value that is no list, items that are no table, and an unknown key."""
    check_fails(folder, [err(None, m_missing_key("ingredients"))], ingredients=None)
    for value in ('"番茄"', '{ item = "番茄", amount = "300 g" }'):
        check_fails(folder, [err(INGREDIENTS, m_not_a_list("ingredients"))], ingredients=value)
    items = (
        '"番茄"',
        "3",
        "[]",
        "{}",
        '{ item = "番茄", amount = "300 g", unit = "g" }',
        '{ item = "番茄", amount = "300 g" }',
    )
    check_fails(
        folder,
        [
            err(ingredient_n(1), M_ITEM_NOT_A_TABLE),
            err(ingredient_n(2), M_ITEM_NOT_A_TABLE),
            err(ingredient_n(3), M_ITEM_NOT_A_TABLE),
            err(ingredient_n(4), m_missing_key("item")),
            err(ingredient_n(4), m_missing_key("amount")),
            err(ingredient_n(5), m_unknown_key("unit", ITEM_KEYS)),
        ],
        ingredients=items,
    )


def test_f04_t23_item_and_amount_must_be_texts_with_more_than_whitespace(
    folder: DataFolder,
) -> None:
    """An unknown name is shown without whitespace, and a blank amount gets EMPTY_TEXT."""
    items = (
        '{ amount = "300 g" }',
        '{ item = 3, amount = "300 g" }',
        '{ item = " ", amount = "300 g" }',
        '{ item = "番茄" }',
        '{ item = "番茄", amount = 300 }',
        '{ item = "番茄", amount = "\u3000" }',
        '{ item = " 豆瓣酱 ", amount = "1 tbsp" }',
        '{ item = ["番茄"], amount = [] }',
    )
    check_fails(
        folder,
        [
            err(ingredient_n(1), m_missing_key("item")),
            err(ingredient_n(2), m_not_a_text("item")),
            err(ingredient_n(3), m_empty_text("item")),
            err(ingredient_n(4), m_missing_key("amount")),
            err(ingredient_n(5), m_not_a_text("amount")),
            err(ingredient_n(6), m_empty_text("amount")),
            err(ingredient_n(7), m_unknown_ing("豆瓣酱")),
            err(ingredient_n(8), m_not_a_text("item")),
            err(ingredient_n(8), m_not_a_text("amount")),
        ],
        ingredients=items,
    )


def test_f04_t24_an_amount_without_a_unit_gets_the_default_unit(folder: DataFolder) -> None:
    """A unit in the amount wins. Each line refers to the catalog's object."""
    items = (
        '{ item = "鸡蛋", amount = "3" }',
        '{ item = "Egg", amount = "2 tbsp" }',
        '{ item = "番茄", amount = "1.5 kg" }',
        '{ item = "番茄", amount = "300克" }',
        '{ item = "葱", amount = "适量" }',
        '{ item = "scallion", amount = "To  taste" }',
        '{ item = "葱", amount = "2" }',
        '{ item = " TOMATO ", amount = "12345678901234.5 g" }',
    )
    wanted = (
        (egg, qty(3, Unit.PIECE)),
        (egg, qty(2, Unit.TBSP)),
        (tomato, Quantity(Fraction(3, 2), Unit.KG)),
        (tomato, qty(300, Unit.G)),
        (scallion, TO_TASTE),
        (scallion, TO_TASTE),
        (scallion, qty(2, Unit.STALK)),
        (tomato, Quantity(Fraction(24691357802469, 2), Unit.G)),
    )
    lines = tuple(RecipeIngredient(ingredient, quantity) for ingredient, quantity in wanted)
    recipe, problems = read_dish(folder, ingredients=items)
    assert problems == ()
    assert recipe == replace(dish, ingredients=lines)
    assert recipe is not None
    for line, (ingredient, _) in zip(recipe.ingredients, wanted, strict=True):
        assert line.ingredient is ingredient
        assert line.note is None


def test_f04_t25_each_reason_of_a_wrong_quantity_gives_its_message(folder: DataFolder) -> None:
    """The amount is shown without whitespace at both ends."""
    amounts = (
        "a few",
        "1/2 tsp",
        "-1 g",
        "1234567890123456 g",
        "\uff11 g",
        " 1 cups ",
        "1 适量",
        "3",
        "0 g",
    )
    items = tuple(f'{{ item = "番茄", amount = "{amount}" }}' for amount in amounts)
    expected = [err(ingredient_n(n), m_not_a_number(a)) for n, a in enumerate(amounts[:5], 1)]
    expected += [
        err(ingredient_n(6), m_amount_unit("cups", "1 cups")),
        err(ingredient_n(7), m_amount_unit("适量", "1 适量")),
        err(ingredient_n(8), m_no_unit("3", tomato)),
        err(ingredient_n(9), m_zero("0 g")),
    ]
    check_fails(folder, expected, ingredients=items)


def test_f04_t26_an_item_with_a_problem_is_read_with_no_default_unit(folder: DataFolder) -> None:
    """The amount gives every reason except NO_UNIT, because only the ingredient decides it."""
    items = (
        '{ item = "豆瓣酱", amount = "3" }',
        '{ item = "豆瓣酱", amount = "1 cups" }',
        '{ item = 3, amount = "3" }',
        '{ item = "", amount = "0 g" }',
        '{ amount = "a few" }',
        '{ item = "鸡蛋", amount = "3" }',
    )
    check_fails(
        folder,
        [
            err(ingredient_n(1), m_unknown_ing("豆瓣酱")),
            err(ingredient_n(2), m_unknown_ing("豆瓣酱")),
            err(ingredient_n(2), m_amount_unit("cups", "1 cups")),
            err(ingredient_n(3), m_not_a_text("item")),
            err(ingredient_n(4), m_empty_text("item")),
            err(ingredient_n(4), m_zero("0 g")),
            err(ingredient_n(5), m_missing_key("item")),
            err(ingredient_n(5), m_not_a_number("a few")),
        ],
        ingredients=items,
    )
