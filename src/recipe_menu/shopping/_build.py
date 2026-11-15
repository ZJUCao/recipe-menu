"""The function that turns a week menu into its shopping list."""

from collections.abc import Mapping
from fractions import Fraction

from recipe_menu.catalog import Catalog, Category, Ingredient, Pantry
from recipe_menu.menus import WeekMenu
from recipe_menu.recipes import Recipe
from recipe_menu.shopping._model import ShoppingGroup, ShoppingLine, ShoppingList
from recipe_menu.units import Quantity, add_quantities


def build_shopping_list(
    menu: WeekMenu,
    recipes: Mapping[str, Recipe],
    catalog: Catalog,
    pantry: Pantry,
) -> ShoppingList:
    """Turns a week menu into its shopping list: scale, merge, add up, skip the pantry, group.

    The function first checks that every ingredient of ``pantry.ingredients`` is in
    ``catalog.ingredients``, also for a menu with no dish. It then checks each dish's recipe ID
    and each ingredient of that recipe as it walks the dishes, and raises at the first wrong
    one. It reads no file, changes none of its arguments, and keeps no state between calls.

    Args:
        menu: The week menu, as ``read_week_menu`` gave it with no error.
        recipes: The recipe of each ID that a dish of ``menu`` names. It holds each such ID, and
            the ID of ``recipes[recipe_id]`` equals ``recipe_id``. It may hold other recipes,
            which are not looked at, and it may be empty when ``menu`` holds no dish.
        catalog: The catalog that the recipes and the pantry were read with. It holds every
            ingredient of the recipes that the dishes name and every ingredient of ``pantry``.
        pantry: The pantry, as ``read_pantry`` gave it with ``catalog``.

    Returns:
        A ``ShoppingList``, built in these steps. Ingredients and categories are compared by
        equality, never by identity. ``meal_count`` is the number of slots of ``menu.slots``
        that hold at least one dish, and ``dish_count`` is the number of dishes in all the
        slots. The function goes through the slots in their order, the dishes of each slot in
        the file's order, and the ingredient lines of each dish's recipe in their order. It
        scales each line's quantity with ``Quantity.scale`` by ``Fraction(dish.servings,
        recipe.servings)``, and keeps it for its ingredient after the quantities kept before.
        A recipe that two dishes name gives its quantities twice, each scaled by its own dish.
        ``add_quantities`` of an ingredient's kept quantities, in that order, gives the
        ``amounts`` of its line. An empty ``amounts`` (to taste) occurs only when no dish gives
        the ingredient a quantity, because to taste adds nothing to a sum. The ingredients go in
        the order of their category in ``catalog.categories``, and then of their position in
        ``catalog.ingredients``. In that order, an ingredient of ``pantry.ingredients`` gets no
        line and goes into ``pantry_used``, also when the menu uses it only to taste. Each
        other ingredient becomes a ``ShoppingLine``. The lines of each category go into one
        ``ShoppingGroup``, and a category with no line has no group. A menu with no dish gives
        ``ShoppingList(menu.week, 0, 0, (), ())`` when the pantry check passes.

    Raises:
        ValueError: An ingredient of ``pantry.ingredients`` is not in ``catalog.ingredients``.
            A dish of ``menu`` names an ID that ``recipes`` does not hold, or the ID of
            ``recipes[dish.recipe_id]`` does not equal ``dish.recipe_id``. An ingredient of a
            recipe that a dish names is not in ``catalog.ingredients``.
    """
    positions = {ingredient: index for index, ingredient in enumerate(catalog.ingredients)}
    _check_pantry(pantry, positions)
    kept = _collect(menu, recipes, positions)
    slots = [slot for slot in menu.slots if slot.dishes]
    dish_count = sum(len(slot.dishes) for slot in slots)
    groups, pantry_used = _arrange(kept, catalog, pantry, positions)
    return ShoppingList(menu.week, len(slots), dish_count, groups, pantry_used)


def _check_pantry(pantry: Pantry, positions: Mapping[Ingredient, int]) -> None:
    """Checks that every pantry ingredient is in the catalog.

    Args:
        pantry: The pantry.
        positions: The catalog's ingredients, each with its position.

    Raises:
        ValueError: A pantry ingredient is not in the catalog.
    """
    if any(ingredient not in positions for ingredient in pantry.ingredients):
        raise ValueError("an ingredient of the pantry is not in the catalog")


def _collect(
    menu: WeekMenu, recipes: Mapping[str, Recipe], positions: Mapping[Ingredient, int]
) -> dict[Ingredient, list[Quantity]]:
    """Scales the lines of every dish and keeps them for each ingredient, in order.

    Args:
        menu: The week menu.
        recipes: The recipes of the dishes, by ID.
        positions: The catalog's ingredients, each with its position.

    Returns:
        The scaled quantities of each ingredient that a dish uses, in the order of the menu.

    Raises:
        ValueError: A dish names a wrong recipe, or a recipe has an ingredient that is not in
            the catalog.
    """
    kept: dict[Ingredient, list[Quantity]] = {}
    for slot in menu.slots:
        for dish in slot.dishes:
            recipe = _find_recipe(recipes, dish.recipe_id)
            factor = Fraction(dish.servings, recipe.servings)
            for line in recipe.ingredients:
                if line.ingredient not in positions:
                    raise ValueError("an ingredient of a recipe is not in the catalog")
                kept.setdefault(line.ingredient, []).append(line.quantity.scale(factor))
    return kept


def _find_recipe(recipes: Mapping[str, Recipe], recipe_id: str) -> Recipe:
    """Finds the recipe of a dish.

    Args:
        recipes: The recipes, by ID.
        recipe_id: The ID that the dish names.

    Returns:
        The recipe.

    Raises:
        ValueError: The mapping lacks the ID, or holds a recipe with another ID under it.
    """
    if recipe_id not in recipes:
        raise ValueError("a dish names a recipe that recipes does not hold")
    recipe = recipes[recipe_id]
    if recipe.id != recipe_id:
        raise ValueError("a recipe is held under another ID")
    return recipe


def _arrange(
    kept: Mapping[Ingredient, list[Quantity]],
    catalog: Catalog,
    pantry: Pantry,
    positions: Mapping[Ingredient, int],
) -> tuple[tuple[ShoppingGroup, ...], tuple[Ingredient, ...]]:
    """Adds up the quantities, leaves out the pantry, and groups the lines by category.

    Args:
        kept: The scaled quantities of each ingredient.
        catalog: The catalog, which gives the order.
        pantry: The pantry.
        positions: The catalog's ingredients, each with its position.

    Returns:
        The groups, in the catalog's order, and the pantry ingredients that were used.
    """
    category_positions = {category: index for index, category in enumerate(catalog.categories)}
    ordered = sorted(kept, key=lambda item: (category_positions[item.category], positions[item]))
    lines: dict[Category, list[ShoppingLine]] = {}
    pantry_used: list[Ingredient] = []
    for ingredient in ordered:
        if ingredient in pantry.ingredients:
            pantry_used.append(ingredient)
        else:
            line = ShoppingLine(ingredient, add_quantities(kept[ingredient]))
            lines.setdefault(ingredient.category, []).append(line)
    groups = tuple(ShoppingGroup(category, tuple(group)) for category, group in lines.items())
    return groups, tuple(pantry_used)
