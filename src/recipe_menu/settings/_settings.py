"""The settings of a data folder."""

from dataclasses import dataclass

from recipe_menu.lang import Lang
from recipe_menu.settings._meal import Meal


@dataclass(frozen=True, slots=True)
class Settings:
    """The settings of a data folder: the language, the meals of each day, and the servings.

    ``Settings()`` gives the defaults. Two settings are equal when their three fields are equal,
    and a ``Settings`` is hashable.

    The mock leaves the checks below out.

    Attributes:
        language: The language of the commands when the command line has no ``--lang``, or
            ``None`` when the settings name no language. Then the commands speak English.
        meals: The meals of each day of a week menu: 1 to 3 meals, in the order of ``Meal``,
            each once.
        servings: The servings of a dish that gives none: from ``MIN_SERVINGS`` to
            ``MAX_SERVINGS``, which are 1 and 100. Not a ``bool``.

    Raises:
        TypeError: ``language`` is neither a ``Lang`` nor ``None``, such as the text ``"zh"``.
        TypeError: ``meals`` is not a tuple, or it holds an item that is not a ``Meal``.
        ValueError: ``meals`` is empty, holds a meal twice, or is not in the order of ``Meal``.
        TypeError: ``servings`` is not an ``int``, or it is a ``bool``.
        ValueError: ``servings`` is less than 1 or more than 100.
    """

    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
