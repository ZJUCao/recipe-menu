"""Tests of F12 for scaling, merging, and adding the quantities of a week (T15 to T19)."""

from collections.abc import Mapping

from f12_support import (
    EN,
    EVERY_MEAL,
    NO_PANTRY,
    ZH,
    code_catalog,
    code_pantry,
    code_recipes,
    expect,
    group,
    menu_of,
    recipes_of,
    texts,
)
from recipe_menu.catalog import Catalog, Pantry
from recipe_menu.menus import WeekMenu
from recipe_menu.recipes import Recipe
from recipe_menu.shopping import ShoppingList, build_shopping_list


def _build(
    menu: WeekMenu,
    mapping: Mapping[str, Recipe],
    catalog: Catalog,
    pantry: Pantry = NO_PANTRY,
) -> ShoppingList:
    """Calls ``build_shopping_list`` with the arguments of the plan's ``build``."""
    return build_shopping_list(menu, mapping, catalog, pantry)


def _check_texts(shopping: ShoppingList, english: list[str], chinese: list[str]) -> None:
    """Checks the ``amount_text`` of every line in both languages."""
    assert texts(shopping, EN) == english
    assert texts(shopping, ZH) == chinese


def _one_group(catalog: Catalog, key: str, text: str, meals: int, dishes: int) -> ShoppingList:
    """Gives the list of one group with one line and no pantry ingredient, in week 2026-W48."""
    return expect(catalog, 48, meals, dishes, (group(catalog, key, text),))


def test_f12_t15_each_dish_is_scaled_by_its_servings_over_the_recipes_exactly() -> None:
    """The factor is exact at both ends of the servings, and each sum has its own unit."""
    catalog = code_catalog()
    mapping = recipes_of(
        catalog,
        "three 3: 番茄 100 g, 鸡蛋 1, 郫县豆瓣酱 1 tsp",
        "one 1: 菜心 1 斤",
        "hundred 100: 大米 1 kg",
        "seven 7: 可乐 1 罐",
    )
    menu = menu_of(
        "monday lunch: three 2",
        "monday dinner: one 100",
        "tuesday lunch: hundred 1",
        "tuesday dinner: seven 3",
    )
    groups = (
        group(catalog, "produce", "番茄: 200/3 G", "菜心: 50000 G"),
        group(catalog, "eggs", "鸡蛋: 2/3 PIECE"),
        group(catalog, "staples", "大米: 10 G"),
        group(catalog, "seasonings", "郫县豆瓣酱: 10/3 ML"),
        group(catalog, "other", "可乐: 3/7 CAN"),
    )
    shopping = _build(menu, mapping, catalog)
    assert shopping == expect(catalog, 48, 4, 4, groups)
    english = ["67 g", "50 kg", "1 piece", "10 g", "4 ml", "1 can"]
    _check_texts(shopping, english, ["67 g", "50 kg", "1 个", "10 g", "4 ml", "1 罐"])

    full = menu_of("monday lunch: three 3")
    groups = (
        group(catalog, "produce", "番茄: 100 G"),
        group(catalog, "eggs", "鸡蛋: 1 PIECE"),
        group(catalog, "seasonings", "郫县豆瓣酱: 5 ML"),
    )
    assert _build(full, mapping, catalog) == expect(catalog, 48, 1, 1, groups)


def test_f12_t16_kinds_that_cannot_be_added_stay_side_by_side_and_sums_are_exact() -> None:
    """Mass adds up in grams, volume in millilitres, and each count unit on its own."""
    catalog = code_catalog()
    mapping = recipes_of(
        catalog,
        "r1: 番茄 1 kg, 生抽 1 L, 葱 2 根, 鸡蛋 2, 大米 0.1 kg",
        "r2: 番茄 1 斤, 生抽 1 tsp, 葱 1 把, 鸡蛋 100 g, 大米 0.2 kg",
        "r3: 番茄 2 两, 生抽 1 tbsp, 葱 3 根, 鸡蛋 1 tbsp",
        "r4: 番茄 7 g, 生抽 1 ml, 葱 2 把",
    )
    menu = menu_of(
        "monday dinner: r1 2, r2 2",
        "tuesday dinner: r3 2",
        "wednesday dinner: r4 2",
    )
    groups = (
        group(catalog, "produce", "番茄: 1607 G", "葱: 5 STALK, 3 BUNCH"),
        group(catalog, "eggs", "鸡蛋: 2 PIECE, 100 G, 15 ML"),
        group(catalog, "staples", "大米: 300 G"),
        group(catalog, "seasonings", "生抽: 1021 ML"),
    )
    shopping = _build(menu, mapping, catalog)
    assert shopping == expect(catalog, 48, 3, 4, groups)
    english = ["1.61 kg", "5 stalks + 3 bunches", "2 pieces + 100 g + 15 ml", "300 g", "1.03 L"]
    chinese = ["1.61 kg", "5 根 + 3 把", "2 个 + 100 g + 15 ml", "300 g", "1.03 L"]
    _check_texts(shopping, english, chinese)


def test_f12_t17_the_sums_of_a_line_follow_the_order_in_which_the_week_uses_each_kind() -> None:
    """Neither the recipe IDs nor the order of the mapping decides the order of the sums."""
    catalog = code_catalog()
    stalks, bunch = "a-stalks: 葱 2 根", "z-bunch: 葱 1 把"
    # Every mapping lists its recipes in the reverse of the order in which the week names them.
    first = _build(
        menu_of(
            "monday dinner: z-bunch 2",
            "friday lunch: a-stalks 2",
            "sunday dinner: z-bunch 2",
        ),
        recipes_of(catalog, stalks, bunch),
        catalog,
    )
    assert first == _one_group(catalog, "produce", "葱: 2 BUNCH, 2 STALK", 3, 3)
    _check_texts(first, ["2 bunches + 2 stalks"], ["2 把 + 2 根"])

    ml, grams = "a-ml: 生抽 1 tbsp", "z-g: 生抽 10 g"
    soy_a = _build(
        menu_of("monday breakfast: z-g 2", "monday dinner: a-ml 2", meals=EVERY_MEAL),
        recipes_of(catalog, ml, grams),
        catalog,
    )
    assert soy_a == _one_group(catalog, "seasonings", "生抽: 10 G, 15 ML", 2, 2)
    _check_texts(soy_a, ["10 g + 15 ml"], ["10 g + 15 ml"])
    soy_b = _build(
        menu_of("monday dinner: a-ml 2", "tuesday breakfast: z-g 2", meals=EVERY_MEAL),
        recipes_of(catalog, grams, ml),
        catalog,
    )
    assert soy_b == _one_group(catalog, "seasonings", "生抽: 15 ML, 10 G", 2, 2)
    _check_texts(soy_b, ["15 ml + 10 g"], ["15 ml + 10 g"])

    _check_two_dishes_of_a_slot(catalog, stalks, bunch)
    _check_two_lines_of_a_recipe(catalog)


def _check_two_dishes_of_a_slot(catalog: Catalog, stalks: str, bunch: str) -> None:
    """Checks that the dishes of one slot go in their order."""
    a = _build(
        menu_of("wednesday dinner: z-bunch 2, a-stalks 2"),
        recipes_of(catalog, stalks, bunch),
        catalog,
    )
    assert a == _one_group(catalog, "produce", "葱: 1 BUNCH, 2 STALK", 1, 2)
    _check_texts(a, ["1 bunch + 2 stalks"], ["1 把 + 2 根"])
    b = _build(
        menu_of("wednesday dinner: a-stalks 2, z-bunch 2"),
        recipes_of(catalog, bunch, stalks),
        catalog,
    )
    assert b == _one_group(catalog, "produce", "葱: 2 STALK, 1 BUNCH", 1, 2)
    _check_texts(b, ["2 stalks + 1 bunch"], ["2 根 + 1 把"])


def _check_two_lines_of_a_recipe(catalog: Catalog) -> None:
    """Checks that the lines of a recipe go in their order."""
    grams_first = recipes_of(catalog, "g-first: 姜 10 g, 姜 2 片")
    slices_first = recipes_of(catalog, "s-first: 姜 2 片, 姜 10 g")
    a = _build(menu_of("monday dinner: g-first 2"), grams_first, catalog)
    assert a == _one_group(catalog, "produce", "姜: 10 G, 2 SLICE", 1, 1)
    _check_texts(a, ["10 g + 2 slices"], ["10 g + 2 片"])
    b = _build(menu_of("monday dinner: s-first 2"), slices_first, catalog)
    assert b == _one_group(catalog, "produce", "姜: 2 SLICE, 10 G", 1, 1)
    _check_texts(b, ["2 slices + 10 g"], ["2 片 + 10 g"])


def test_f12_t18_a_recipe_of_several_dishes_counts_once_for_each_dish_and_rounds_once() -> None:
    """A repeated recipe or ingredient adds up exactly, to taste adds nothing, rounding is last."""
    catalog = code_catalog()
    recipes = code_recipes(catalog)
    both = menu_of("monday dinner: tomato-egg 2, tomato-egg 4")
    groups = (
        group(catalog, "produce", "番茄: 900 G", "葱: 3 STALK"),
        group(catalog, "eggs", "鸡蛋: 9 PIECE"),
        group(catalog, "staples", "食用油: 90 ML"),
        group(catalog, "seasonings", "盐:", "糖: 15 ML"),
    )
    assert _build(both, recipes, catalog) == expect(catalog, 48, 1, 2, groups)

    twice = menu_of("monday dinner: tomato-egg 3", "thursday lunch: tomato-egg 3")
    groups = (
        group(catalog, "produce", "番茄: 900 G", "葱: 3 STALK"),
        group(catalog, "eggs", "鸡蛋: 9 PIECE"),
    )
    pantry = code_pantry(catalog)
    shopping = _build(twice, recipes, catalog, pantry)
    assert shopping == expect(catalog, 48, 2, 2, groups, pantry=("食用油", "盐", "糖"))
    _check_texts(shopping, ["900 g", "3 stalks", "9 pieces"], ["900 g", "3 根", "9 个"])

    double = recipes_of(catalog, "double: 葱 1 根, 番茄 100 g, 葱 2 根, 葱 适量")
    shopping = _build(menu_of("monday dinner: double 4"), double, catalog)
    groups = (group(catalog, "produce", "番茄: 200 G", "葱: 6 STALK"),)
    assert shopping == expect(catalog, 48, 1, 1, groups)


def test_f12_t19_to_taste_shows_only_when_no_dish_gives_a_quantity() -> None:
    """An ingredient with no quantity in any dish has no amounts, and others have only sums."""
    catalog = code_catalog()
    mapping = recipes_of(
        catalog,
        "a: 白胡椒粉 适量",
        "b: 白胡椒粉 适量",
        "c: 盐 适量",
        "d: 盐 5 g, 糖 适量, 糖 1 tsp",
    )
    menu = menu_of("monday dinner: a 2, c 2", "tuesday dinner: b 2, d 2")
    shopping = _build(menu, mapping, catalog)
    groups = (group(catalog, "seasonings", "盐: 5 G", "糖: 5 ML", "白胡椒粉:"),)
    assert shopping == expect(catalog, 48, 2, 4, groups)
    _check_texts(shopping, ["5 g", "5 ml", "to taste"], ["5 g", "5 ml", "适量"])
