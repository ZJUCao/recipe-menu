"""The random choice of ``menu suggest``: the one draw, and the dishes of each empty meal."""

from dataclasses import dataclass

from recipe_menu.app import Context
from recipe_menu.menus import Day, MealSlot
from recipe_menu.settings import Meal


@dataclass(frozen=True, slots=True)
class Fill:
    """The dishes that one empty meal gets.

    Attributes:
        day: The day of the meal.
        meal: The meal.
        ids: The recipe IDs of its dishes, in the order of the draw.
    """

    day: Day
    meal: Meal
    ids: tuple[str, ...]


def draw(context: Context, candidates: tuple[str, ...], empties: tuple[MealSlot, ...]) -> list[str]:
    """Draws the recipes for all the empty meals with one call of ``context.random.sample``.

    Args:
        context: The settings and the random generator.
        candidates: The IDs that can be chosen, in the order of the listing.
        empties: The empty meals.

    Returns:
        ``min(need, len(candidates))`` different IDs, where ``need`` is the sum of
        ``dishes_for`` over the empty meals.
    """
    need = sum(context.settings.dishes_for(slot.meal) for slot in empties)
    return context.random.sample(list(candidates), min(need, len(candidates)))


def distribute(context: Context, empties: tuple[MealSlot, ...], chosen: list[str]) -> list[Fill]:
    """Gives the chosen recipes to the empty meals in their order.

    A meal takes ``dishes_for(meal)`` recipes from the front of what is left when that many are
    left. Otherwise it stays empty, and the next meals go on.

    Args:
        context: The settings.
        empties: The empty meals, in the order of the week.
        chosen: The drawn IDs.

    Returns:
        One ``Fill`` for each empty meal that got its dishes, in the order of the meals.
    """
    fills: list[Fill] = []
    used = 0
    for slot in empties:
        count = context.settings.dishes_for(slot.meal)
        if used + count <= len(chosen):
            fills.append(Fill(slot.day, slot.meal, tuple(chosen[used : used + count])))
            used += count
    return fills
