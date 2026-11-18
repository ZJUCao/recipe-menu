"""The settings of a data folder."""

from dataclasses import dataclass

from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS
from recipe_menu.lang import Lang
from recipe_menu.settings._meal import Meal

# The fewest and the most dishes of one meal.
MIN_DISHES = 1
MAX_DISHES = 10

# The place of each meal in ``Settings.dishes``, which is the order of ``Meal``.
_MEAL_POSITIONS = {meal: position for position, meal in enumerate(Meal)}


def _check_meals(meals: object) -> None:
    """Checks the meals of a ``Settings``.

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


def _check_dishes(dishes: object) -> None:
    """Checks the dishes of a ``Settings``.

    Args:
        dishes: The value of the field ``dishes``.

    Raises:
        TypeError: ``dishes`` is not a tuple, or it holds an item that is not an ``int``, or
            that is a ``bool``.
        ValueError: ``dishes`` does not hold exactly three items, or it holds a number less than
            1 or more than 10.
    """
    if not isinstance(dishes, tuple) or any(
        isinstance(number, bool) or not isinstance(number, int) for number in dishes
    ):
        raise TypeError("dishes must be a tuple of int")
    if len(dishes) != len(Meal):
        raise ValueError("dishes must hold exactly three numbers")
    if any(not MIN_DISHES <= number <= MAX_DISHES for number in dishes):
        raise ValueError(f"dishes must be from {MIN_DISHES} to {MAX_DISHES}")


@dataclass(frozen=True, slots=True)
class Settings:
    """The settings of a data folder: language, meals of each day, servings, and dishes.

    ``Settings()`` gives the defaults. Two settings are equal when their four fields are equal,
    and a ``Settings`` is hashable.

    Attributes:
        language: The language of the commands when the command line has no ``--lang``, or
            ``None`` when the settings name no language. Then the commands speak English.
        meals: The meals of each day of a week menu: 1 to 3 meals, in the order of ``Meal``,
            each once.
        servings: The servings of a dish that gives none: from ``MIN_SERVINGS`` to
            ``MAX_SERVINGS``, which are 1 and 100. Not a ``bool``.
        dishes: The number of dishes of breakfast, lunch, and dinner, in the order of ``Meal``:
            exactly three whole numbers from 1 to 10, none a ``bool``.

    Raises:
        TypeError: ``language`` is neither a ``Lang`` nor ``None``, such as the text ``"zh"``.
        TypeError: ``meals`` is not a tuple, or it holds an item that is not a ``Meal``.
        ValueError: ``meals`` is empty, holds a meal twice, or is not in the order of ``Meal``.
        TypeError: ``servings`` is not an ``int``, or it is a ``bool``.
        ValueError: ``servings`` is less than 1 or more than 100.
        TypeError: ``dishes`` is not a tuple, or it holds an item that is not an ``int``, or
            that is a ``bool``.
        ValueError: ``dishes`` does not hold exactly three items, or it holds a number less than
            1 or more than 10.
    """

    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
    dishes: tuple[int, int, int] = (1, 1, 1)

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: A field has the wrong type.
            ValueError: ``meals``, ``servings``, or ``dishes`` has a wrong value.
        """
        if self.language is not None and not isinstance(self.language, Lang):
            raise TypeError("language must be a Lang or None")
        _check_meals(self.meals)
        if isinstance(self.servings, bool) or not isinstance(self.servings, int):
            raise TypeError("servings must be an int")
        if not MIN_SERVINGS <= self.servings <= MAX_SERVINGS:
            raise ValueError(f"servings must be from {MIN_SERVINGS} to {MAX_SERVINGS}")
        _check_dishes(self.dishes)

    def dishes_for(self, meal: Meal) -> int:
        """Gives the number of dishes of a meal.

        Args:
            meal: Any ``Meal``, also one that ``meals`` does not name.

        Returns:
            The item of ``dishes`` at the place of ``meal`` in the order of ``Meal``.
        """
        return self.dishes[_MEAL_POSITIONS[meal]]
