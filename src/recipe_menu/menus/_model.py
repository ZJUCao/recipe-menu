"""The values of a week menu: the days, the dishes, the meal slots, and the menu."""

from dataclasses import dataclass
from enum import StrEnum

from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS
from recipe_menu.lang import BiText
from recipe_menu.menus._week import IsoWeek
from recipe_menu.menus.messages import (
    FRIDAY_LABEL,
    MONDAY_LABEL,
    SATURDAY_LABEL,
    SUNDAY_LABEL,
    THURSDAY_LABEL,
    TUESDAY_LABEL,
    WEDNESDAY_LABEL,
)
from recipe_menu.recipes import is_recipe_id
from recipe_menu.settings import Meal

_LABELS = {
    "monday": MONDAY_LABEL,
    "tuesday": TUESDAY_LABEL,
    "wednesday": WEDNESDAY_LABEL,
    "thursday": THURSDAY_LABEL,
    "friday": FRIDAY_LABEL,
    "saturday": SATURDAY_LABEL,
    "sunday": SUNDAY_LABEL,
}


class Day(StrEnum):
    """The seven days of a week, Monday to Sunday, with their names in both languages.

    Each member's value is the key of the day's table in a menu file. ``list(Day)`` gives the
    members in the order of a week. ``IsoWeek.dates[i]`` is the date of ``list(Day)[i]``.
    ``Day(value)`` gives the member whose value is ``value``, and ``value in Day`` tells
    whether a word is a day, without an exception. A ``Day`` is a ``str``, so ``sorted`` sorts
    days by their words, which is not the order of a week. Sort them with
    ``key=list(Day).index``. A message shows a day through ``label``, because
    ``Message.render`` rejects an enum member.

    Raises:
        ValueError: ``Day(value)`` gets a word that is not a member's value, such as ``funday``
            or ``Monday``.
    """

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @property
    def label(self) -> BiText:
        """Gives the day's name inside a place, such as "Monday dinner".

        Returns:
            The English name is ``Monday`` to ``Sunday``. The Chinese name is the character
            for week and the character for the day, such as the one for Monday.
        """
        return _LABELS[self.value].to_bitext()


def _check_meals(meals: object) -> None:
    """Checks the meals of a ``WeekMenu``.

    Args:
        meals: The value of the field ``meals``.

    Raises:
        TypeError: ``meals`` is not a tuple, or it holds an item that is not a ``Meal``.
        ValueError: ``meals`` is empty, holds a meal twice, or is not in the order of ``Meal``.
    """
    if not isinstance(meals, tuple) or not all(isinstance(meal, Meal) for meal in meals):
        raise TypeError("meals must be a tuple of Meal")
    if not meals:
        raise ValueError("meals must hold at least one meal")
    order = list(Meal)
    positions = [order.index(meal) for meal in meals]
    if positions != sorted(set(positions)):
        raise ValueError("meals must hold each meal once, in the order of Meal")


@dataclass(frozen=True, slots=True)
class Dish:
    """One dish of a meal: the ID of its recipe and its servings.

    ``read_week_menu`` fills in the servings of the settings when the file gives none. Two
    dishes are equal when their two fields are equal, and a ``Dish`` is hashable.

    Attributes:
        recipe_id: The ID of the recipe, such as ``cola-wings``. ``is_recipe_id(recipe_id)`` is
            true.
        servings: The servings of the dish, from ``MIN_SERVINGS`` to ``MAX_SERVINGS``, which
            are 1 and 100. Not a ``bool``.

    Raises:
        TypeError: ``recipe_id`` is not a ``str``.
        ValueError: ``is_recipe_id(recipe_id)`` is false.
        TypeError: ``servings`` is not an ``int``, or it is a ``bool``.
        ValueError: ``servings`` is less than 1 or more than 100.
    """

    recipe_id: str
    servings: int

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: ``recipe_id`` is not a ``str``, or ``servings`` is not an ``int``.
            ValueError: ``recipe_id`` or ``servings`` has a wrong value.
        """
        if not isinstance(self.recipe_id, str):
            raise TypeError("recipe_id must be a str")
        if not is_recipe_id(self.recipe_id):
            raise ValueError("recipe_id is not a recipe ID")
        if isinstance(self.servings, bool) or not isinstance(self.servings, int):
            raise TypeError("servings must be an int")
        if not MIN_SERVINGS <= self.servings <= MAX_SERVINGS:
            raise ValueError(f"servings must be from {MIN_SERVINGS} to {MAX_SERVINGS}")


@dataclass(frozen=True, slots=True)
class MealSlot:
    """One meal of one day, such as Monday dinner, with its dishes in the file's order.

    A meal holds zero or more dishes. Two slots are equal when their three fields are equal,
    and a ``MealSlot`` is hashable.

    Attributes:
        day: The day.
        meal: The meal.
        dishes: The dishes, in the file's order. May be empty. A dish may appear more than once.

    Raises:
        TypeError: ``day`` is not a ``Day``, ``meal`` is not a ``Meal``, or ``dishes`` is not
            a tuple or holds an item that is not a ``Dish``.
    """

    day: Day
    meal: Meal
    dishes: tuple[Dish, ...] = ()

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: A field has a wrong type.
        """
        if not isinstance(self.day, Day) or not isinstance(self.meal, Meal):
            raise TypeError("day must be a Day and meal must be a Meal")
        if not isinstance(self.dishes, tuple) or not all(
            isinstance(dish, Dish) for dish in self.dishes
        ):
            raise TypeError("dishes must be a tuple of Dish")


@dataclass(frozen=True, slots=True)
class WeekMenu:
    """The menu of one week: its ISO week, its meals, and one slot for each day and meal.

    It holds the meals that the settings name, and it refers to recipes by ID only. Two menus
    are equal when their three fields are equal, and a ``WeekMenu`` is hashable.

    Attributes:
        week: The week.
        meals: The meals of each day, from the settings: 1 to 3 meals, in the order of
            ``Meal``, each once.
        slots: Exactly one slot for each day and each meal of ``meals``: Monday to Sunday, and
            within a day in the order of ``meals``. So it holds ``7 * len(meals)`` slots.

    Raises:
        TypeError: ``week`` is not an ``IsoWeek``, ``meals`` is not a tuple of ``Meal`` values,
            or ``slots`` is not a tuple of ``MealSlot`` values.
        ValueError: ``meals`` is empty, holds a meal twice, or is not in the order of ``Meal``.
        ValueError: ``slots`` does not hold exactly one slot for each day and each meal of
            ``meals``, in the order above.
    """

    week: IsoWeek
    meals: tuple[Meal, ...]
    slots: tuple[MealSlot, ...]

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: A field has a wrong type.
            ValueError: ``meals`` or ``slots`` has a wrong value.
        """
        if not isinstance(self.week, IsoWeek):
            raise TypeError("week must be an IsoWeek")
        _check_meals(self.meals)
        if not isinstance(self.slots, tuple) or not all(
            isinstance(slot, MealSlot) for slot in self.slots
        ):
            raise TypeError("slots must be a tuple of MealSlot")
        wanted = [(day, meal) for day in Day for meal in self.meals]
        if [(slot.day, slot.meal) for slot in self.slots] != wanted:
            raise ValueError("slots must hold one slot for each day and meal, in order")

    def dishes(self, day: Day, meal: Meal) -> tuple[Dish, ...]:
        """Gives the dishes of one slot.

        Args:
            day: The day of the slot.
            meal: The meal of the slot. It is in ``meals``.

        Returns:
            The dishes of the slot of ``day`` and ``meal``, in the file's order.

        Raises:
            ValueError: ``meal`` is not in ``meals``.
        """
        if meal not in self.meals:
            raise ValueError("meal is not in meals")
        return self.slots[list(Day).index(day) * len(self.meals) + self.meals.index(meal)].dishes
