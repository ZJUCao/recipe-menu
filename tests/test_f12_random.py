"""Tests of F12 on random weeks of random catalogs, with its own computation of the list (T33)."""

import itertools
import random
from fractions import Fraction

from f06_support import make_menu
from f12_support import EN, ZH, copy_category
from recipe_menu.catalog import Catalog, Category, Ingredient, Pantry
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, MealSlot, WeekMenu
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.settings import Meal
from recipe_menu.shopping import ShoppingGroup, ShoppingLine, ShoppingList, build_shopping_list
from recipe_menu.units import TO_TASTE, Quantity, Unit, UnitKind

SEED = 20261115
WEEKS = 1000
TO_TASTE_TEXT = {EN: "to taste", ZH: "适量"}

type Week = tuple[WeekMenu, dict[str, Recipe], Catalog, Pantry]


def _random_catalog(rng: random.Random) -> tuple[Catalog, Pantry]:
    """Builds a catalog of 1 to 6 categories and 1 to 30 ingredients, and a pantry."""
    categories = tuple(
        Category(f"c{number}", BiText(f"Category {number}", f"分类{number}"))
        for number in range(1, rng.randint(1, 6) + 1)
    )
    ingredients = []
    for number in range(1, rng.randint(1, 30) + 1):
        owner = rng.choice(categories)
        if rng.random() < 0.25:
            owner = copy_category(owner)
        unit = rng.choice([None, *Unit])
        ingredients.append(Ingredient(BiText(f"Ingredient {number}", f"食材{number}"), owner, unit))
    pantry = Pantry(frozenset(item for item in ingredients if rng.random() < 0.25))
    return Catalog(categories, tuple(ingredients), ()), pantry


def _random_quantity(rng: random.Random) -> Quantity:
    """Builds to taste 1 time in 6, and otherwise an amount that ``parse_quantity`` could read."""
    if rng.random() < 1 / 6:
        return TO_TASTE
    digits = rng.randint(1, 15)
    number = rng.randint(1, 10**digits - 1)
    return Quantity(Fraction(number, 10 ** rng.randint(0, 14)), rng.choice(list(Unit)))


def _random_recipes(rng: random.Random, catalog: Catalog) -> dict[str, Recipe]:
    """Builds 1 to 8 recipes of 0 to 8 lines, and 1 time in 4 also ``x-extra``."""
    recipes = {}
    for number in range(1, rng.randint(1, 8) + 1):
        lines = tuple(
            RecipeIngredient(rng.choice(catalog.ingredients), _random_quantity(rng))
            for _ in range(rng.randint(0, 8))
        )
        servings = rng.randint(1, 100)
        recipes[f"r-{number}"] = Recipe(
            f"r-{number}", BiText(f"r-{number}"), servings, (), lines, Steps(("Cook.",))
        )
    return recipes


def _random_menu(rng: random.Random, recipe_ids: list[str]) -> WeekMenu:
    """Builds a menu of a random week and random meals, with 0 to 3 dishes in each slot."""
    sets = [c for size in (1, 2, 3) for c in itertools.combinations(Meal, size)]
    meals = rng.choice(sets)
    filled = {
        (day, meal): tuple(
            Dish(rng.choice(recipe_ids), rng.randint(1, 100)) for _ in range(rng.randint(0, 3))
        )
        for day in Day
        for meal in meals
    }
    return make_menu(IsoWeek(2026, rng.randint(1, 53)), meals, filled)


def _random_week(rng: random.Random) -> Week:
    """Builds one random week: the menu, the mapping, the catalog, and the pantry."""
    catalog, pantry = _random_catalog(rng)
    recipes = _random_recipes(rng, catalog)
    menu = _random_menu(rng, list(recipes))
    mapping = dict(recipes)
    if rng.random() < 0.25:
        outside = Ingredient(BiText("Outside", "外部"), catalog.categories[0])
        extra = RecipeIngredient(outside, Quantity(Fraction(1), Unit.G))
        mapping["x-extra"] = Recipe("x-extra", BiText("x"), 2, (), (extra,), Steps(("Cook.",)))
    return menu, mapping, catalog, pantry


def _add(sums: dict[Unit, Fraction], quantity: Quantity, factor: Fraction) -> None:
    """Adds the scaled quantity to the sums: mass in grams, volume in ml, a count by its unit."""
    if quantity.amount is None or quantity.unit is None:
        return
    size = quantity.unit.size
    if size is None:
        key, value = quantity.unit, quantity.amount * factor
    else:
        key = Unit.G if quantity.unit.kind is UnitKind.MASS else Unit.ML
        value = quantity.amount * size * factor
    sums[key] = sums.get(key, Fraction(0)) + value


def _expected(week: Week) -> ShoppingList:
    """Builds the list from the rules of the design, with no code of F12."""
    menu, mapping, catalog, pantry = week
    sums: dict[Ingredient, dict[Unit, Fraction]] = {}
    for slot in menu.slots:
        for dish in slot.dishes:
            recipe = mapping[dish.recipe_id]
            factor = Fraction(dish.servings, recipe.servings)
            for item in recipe.ingredients:
                _add(sums.setdefault(item.ingredient, {}), item.quantity, factor)
    order = sorted(
        sums,
        key=lambda item: (catalog.categories.index(item.category), catalog.ingredients.index(item)),
    )
    lines: dict[int, list[ShoppingLine]] = {}
    for ingredient in order:
        if ingredient not in pantry.ingredients:
            amounts = tuple(Quantity(value, unit) for unit, value in sums[ingredient].items())
            lines.setdefault(catalog.categories.index(ingredient.category), []).append(
                ShoppingLine(ingredient, amounts)
            )
    groups = tuple(ShoppingGroup(catalog.categories[at], tuple(lines[at])) for at in sorted(lines))
    used = tuple(item for item in order if item in pantry.ingredients)
    filled = [slot for slot in menu.slots if slot.dishes]
    dishes = sum(len(slot.dishes) for slot in filled)
    return ShoppingList(menu.week, len(filled), dishes, groups, used)


def _text(line: ShoppingLine, lang: Lang) -> str:
    """Gives the text that the rules give for the line: the rounded amounts joined by `` + ``."""
    if not line.amounts:
        return TO_TASTE_TEXT[lang]
    return " + ".join(amount.to_rounded_text(lang) for amount in line.amounts)


def _slots_with_dishes(menu: WeekMenu) -> list[MealSlot]:
    """Gives the slots of the menu that hold a dish."""
    return [slot for slot in menu.slots if slot.dishes]


def test_f12_t33_random_weeks_give_the_list_that_the_rules_give(default_int_limit: None) -> None:
    """1,000 random weeks: no error, the list of the rules, every text, and the same list twice."""
    rng = random.Random(SEED)  # noqa: S311
    for number in range(WEEKS):
        week = _random_week(rng)
        menu, mapping, catalog, pantry = week
        shopping = build_shopping_list(menu, mapping, catalog, pantry)
        assert shopping == _expected(week), number
        assert shopping.week == menu.week
        assert shopping.meal_count == len(_slots_with_dishes(menu))
        for entry in shopping.groups:
            for line in entry.lines:
                for lang in (EN, ZH):
                    assert line.amount_text(lang) == _text(line, lang), number
        assert build_shopping_list(menu, mapping, catalog, pantry) == shopping, number
