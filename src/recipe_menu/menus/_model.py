"""The values of a week menu: the days, the dishes, the meal slots, and the menu."""

from dataclasses import dataclass
from enum import StrEnum

from recipe_menu.lang import BiText
from recipe_menu.menus._week import IsoWeek
from recipe_menu.settings import Meal


class Day(StrEnum):
    """The seven days of a week, Monday to Sunday, with their names in both languages.

    Each member's value is the key of the day's table in a menu file. ``list(Day)`` gives the
    members in the order of a week. ``IsoWeek.dates[i]`` is the date of ``list(Day)[i]``.
    ``Day(value)`` gives the member whose value is ``value``, and ``value in Day`` tells
    whether a word is a day, without an exception. A ``Day`` is a ``str``, so ``sorted`` sorts
    days by their words, which is not the order of a week. Sort them with
    ``key=list(Day).index``.

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

        The mock raises ``NotImplementedError``.

        Returns:
            The English name is ``Monday`` to ``Sunday``. The Chinese name is the character
            for week and the character for the day, such as the one for Monday.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError


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

    The mock leaves these checks out.
    """

    recipe_id: str
    servings: int


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

    The mock leaves these checks out.
    """

    day: Day
    meal: Meal
    dishes: tuple[Dish, ...] = ()


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

    The mock leaves these checks out.
    """

    week: IsoWeek
    meals: tuple[Meal, ...]
    slots: tuple[MealSlot, ...]

    def dishes(self, day: Day, meal: Meal) -> tuple[Dish, ...]:
        """Gives the dishes of one slot.

        The mock raises ``NotImplementedError``.

        Args:
            day: The day of the slot.
            meal: The meal of the slot. It is in ``meals``.

        Returns:
            The dishes of the slot of ``day`` and ``meal``, in the file's order.

        Raises:
            ValueError: ``meal`` is not in ``meals``.
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError
