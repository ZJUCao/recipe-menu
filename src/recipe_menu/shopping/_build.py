"""The function that turns a week menu into its shopping list."""

from collections.abc import Mapping

from recipe_menu.catalog import Catalog, Pantry
from recipe_menu.menus import WeekMenu
from recipe_menu.recipes import Recipe
from recipe_menu.shopping._model import ShoppingList


def build_shopping_list(
    menu: WeekMenu,
    recipes: Mapping[str, Recipe],
    catalog: Catalog,
    pantry: Pantry,
) -> ShoppingList:
    """Turns a week menu into its shopping list: scale, merge, add up, skip the pantry, group.

    The mock raises ``NotImplementedError``.

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
        NotImplementedError: The mock does not build the list yet.
    """
    raise NotImplementedError
