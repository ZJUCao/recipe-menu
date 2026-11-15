"""Tests of F12 for the pantry, the groups, equality, the counts, and empty lists (T20 to T25)."""

from fractions import Fraction

from f06_support import make_menu
from f12_support import (
    EN,
    EVERY_MEAL,
    NO_PANTRY,
    ZH,
    category,
    code_catalog,
    code_pantry,
    code_recipes,
    copy_category,
    copy_of,
    every_slot,
    expect,
    find,
    group,
    menu_of,
    nothing_recipe,
    recipe,
    recipes_of,
    subset,
    texts,
)
from recipe_menu.catalog import Catalog, Ingredient, Pantry
from recipe_menu.lang import BiText
from recipe_menu.menus import Day, Dish, IsoWeek
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.settings import Meal
from recipe_menu.shopping import ShoppingList, build_shopping_list
from recipe_menu.units import TO_TASTE, Quantity, Unit


def test_f12_t20_a_pantry_ingredient_gets_no_line_and_is_named_in_pantry_used() -> None:
    """``pantry_used`` follows the catalog's order, and a category of only pantry has no group."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    mapping = recipes_of(catalog, "p: 生抽 2 tbsp, 生抽 10 g, 盐 适量, 食用油 1 tbsp, 番茄 100 g")
    menu = menu_of("monday dinner: p 2")
    groups = (group(catalog, "produce", "番茄: 100 G"),)
    expected = expect(catalog, 48, 1, 1, groups, pantry=("食用油", "盐", "生抽"))
    assert build_shopping_list(menu, mapping, catalog, pantry) == expected

    small = subset(catalog, ("staples", "seasonings"), ("盐", "食用油", "糖"))
    everything = Pantry(frozenset(small.ingredients))
    mapping = recipes_of(small, "q: 糖 1 tsp, 食用油 1 tbsp, 盐 适量")
    shopping = build_shopping_list(menu_of("monday dinner: q 2"), mapping, small, everything)
    assert shopping == expect(small, 48, 1, 1, pantry=("食用油", "盐", "糖"))


def test_f12_t21_groups_and_lines_follow_the_catalogs_order() -> None:
    """The catalog may list a category's ingredients in several places, and has empty ones."""
    catalog = code_catalog()
    names = ("猪肉末", "番茄", "鸡蛋", "五花肉", "葱", "可乐")
    ordered = subset(catalog, ("produce", "meat", "eggs", "other", "seasonings"), names)
    mapping = recipes_of(ordered, "g: 鸡蛋 2, 葱 1 根, 五花肉 100 g, 番茄 100 g, 猪肉末 50 g")
    groups = (
        group(ordered, "produce", "番茄: 100 G", "葱: 1 STALK"),
        group(ordered, "meat", "猪肉末: 50 G", "五花肉: 100 G"),
        group(ordered, "eggs", "鸡蛋: 2 PIECE"),
    )
    shopping = build_shopping_list(menu_of("monday dinner: g 2"), mapping, ordered, NO_PANTRY)
    assert shopping == expect(ordered, 48, 1, 1, groups)


def test_f12_t22_the_list_compares_by_equality_and_never_by_identity() -> None:
    """Equal but separate categories, ingredients, and recipe IDs give the same list."""
    catalog = code_catalog()
    _check_copied_category(catalog)
    _check_copied_ingredients(catalog)
    _check_copied_recipe_id(catalog)


def _check_copied_category(catalog: Catalog) -> None:
    """Checks an ingredient whose category is an equal but separate copy of the catalog's."""
    produce = category(catalog, "produce")
    same_produce = copy_category(produce)
    same_tomato = Ingredient(BiText("Tomato", "番茄"), same_produce)
    assert same_produce == produce
    assert same_produce is not produce
    both = Catalog((produce, category(catalog, "meat")), (same_tomato, find(catalog, "五花肉")), ())
    mapping = recipes_of(both, "e: 番茄 100 g, 五花肉 200 g")
    shopping = build_shopping_list(menu_of("monday dinner: e 2"), mapping, both, NO_PANTRY)
    groups = (group(both, "produce", "番茄: 100 G"), group(both, "meat", "五花肉: 200 G"))
    assert shopping == expect(both, 48, 1, 1, groups)
    assert shopping.groups[0].category == produce


def _check_copied_ingredients(catalog: Catalog) -> None:
    """Checks equal but separate ingredients in a recipe and in the pantry."""
    copies = {name: copy_of(find(catalog, name)) for name in ("番茄", "葱", "盐", "食用油", "糖")}
    for name, copied in copies.items():
        assert copied == find(catalog, name)
        assert copied is not find(catalog, name)
        assert copied.category is not find(catalog, name).category
    pantry = Pantry(frozenset(copies[name] for name in ("食用油", "盐", "糖")))
    lines = (
        RecipeIngredient(copies["番茄"], Quantity(Fraction(100), Unit.G)),
        RecipeIngredient(copies["葱"], Quantity(Fraction(1), Unit.STALK)),
        RecipeIngredient(copies["盐"], TO_TASTE),
    )
    copy_egg = Recipe("copy-egg", BiText("copy-egg"), 2, (), lines, Steps(("Cook.",)))
    mapping = {"tomato-egg": code_recipes(catalog)["tomato-egg"], "copy-egg": copy_egg}
    menu = menu_of("monday dinner: tomato-egg 2, copy-egg 2")
    shopping = build_shopping_list(menu, mapping, catalog, pantry)
    groups = (
        group(catalog, "produce", "番茄: 400 G", "葱: 2 STALK"),
        group(catalog, "eggs", "鸡蛋: 3 PIECE"),
    )
    assert shopping == expect(catalog, 48, 1, 2, groups, pantry=("食用油", "盐", "糖"))


def _check_copied_recipe_id(catalog: Catalog) -> None:
    """Checks a dish ID and a mapping key that equal the recipe's ID and are separate strings."""
    dish_id = "".join(["ri", "ce"])
    key = "".join(["ric", "e"])
    recipe_id = "".join(["r", "ice"])
    assert dish_id == key == recipe_id == "rice"
    assert dish_id is not key
    assert key is not recipe_id
    assert dish_id is not recipe_id
    mapping = {key: recipe(catalog, recipe_id, ["大米 160 g"])}
    filled = {(Day.MONDAY, Meal.DINNER): (Dish(dish_id, 2),)}
    menu = make_menu(IsoWeek(2026, 48), (Meal.LUNCH, Meal.DINNER), filled)
    shopping = build_shopping_list(menu, mapping, catalog, NO_PANTRY)
    assert shopping == expect(catalog, 48, 1, 1, (group(catalog, "staples", "大米: 160 G"),))


def test_f12_t23_the_counts_are_the_filled_slots_and_every_dish() -> None:
    """``meal_count`` counts slots with a dish, and ``dish_count`` counts a dish with no line."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    code = code_recipes(catalog)
    mapping = {"rice": code["rice"], "tomato-egg": code["tomato-egg"], "nothing": nothing_recipe()}
    menu = menu_of(
        "monday breakfast: rice 2, rice 2, rice 2",
        "monday dinner: tomato-egg 2",
        "wednesday lunch: nothing 2",
        "sunday dinner: rice 2",
        meals=EVERY_MEAL,
    )
    groups = (
        group(catalog, "produce", "番茄: 300 G", "葱: 1 STALK"),
        group(catalog, "eggs", "鸡蛋: 3 PIECE"),
        group(catalog, "staples", "大米: 640 G"),
    )
    expected = expect(catalog, 48, 4, 6, groups, pantry=("食用油", "盐", "糖"))
    assert build_shopping_list(menu, mapping, catalog, pantry) == expected

    dinners = menu_of(*(f"{day.value} dinner: rice 1" for day in Day), meals=(Meal.DINNER,))
    groups = (group(catalog, "staples", "大米: 560 G"),)
    expected = expect(catalog, 48, 7, 7, groups)
    assert build_shopping_list(dinners, mapping, catalog, pantry) == expected

    everything = every_slot("rice 2", times=3)
    shopping = build_shopping_list(everything, mapping, catalog, pantry)
    assert shopping == expect(catalog, 48, 21, 63, (group(catalog, "staples", "大米: 10080 G"),))
    assert texts(shopping, EN) == ["10.08 kg"]
    assert texts(shopping, ZH) == ["10.08 kg"]


def test_f12_t24_a_menu_with_no_dish_gives_the_empty_list() -> None:
    """The empty list comes with an empty or a full mapping, whatever the meals and the pantry."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    empty = ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())
    first = build_shopping_list(menu_of(week=46), {}, catalog, pantry)
    full = code_recipes(catalog)
    second = build_shopping_list(menu_of(week=46, meals=EVERY_MEAL), full, catalog, pantry)
    for shopping in (first, second):
        assert shopping == empty
        assert hash(shopping) == hash(empty)
    breakfast = menu_of(week=53, meals=(Meal.BREAKFAST,))
    third = build_shopping_list(breakfast, {}, catalog, NO_PANTRY)
    assert third == ShoppingList(IsoWeek(2026, 53), 0, 0, (), ())


def test_f12_t25_a_week_with_dishes_and_no_group_gives_a_list_with_no_group() -> None:
    """Dishes that use only the pantry, or recipes with no line, give dishes and no group."""
    catalog = code_catalog()
    pantry = code_pantry(catalog)
    mapping = recipes_of(catalog, "oil-salt: 食用油 1 tbsp, 盐 适量")
    shopping = build_shopping_list(menu_of("monday dinner: oil-salt 2"), mapping, catalog, pantry)
    assert shopping == expect(catalog, 48, 1, 1, pantry=("食用油", "盐"))

    mapping = {"nothing": nothing_recipe()}
    menu = menu_of("monday dinner: nothing 2", "tuesday lunch: nothing 3")
    assert build_shopping_list(menu, mapping, catalog, pantry) == expect(catalog, 48, 2, 2)
