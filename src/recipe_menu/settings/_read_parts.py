"""The checks of each key of ``settings.toml``."""

from collections.abc import Mapping

from recipe_menu.datafile import (
    EMPTY_ITEM,
    ITEM_NOT_A_TEXT,
    NOT_A_LIST,
    Report,
    read_servings,
    read_text,
)
from recipe_menu.lang import Lang
from recipe_menu.settings._meal import Meal
from recipe_menu.settings._settings import MAX_DISHES, MIN_DISHES
from recipe_menu.settings.messages import (
    DISHES,
    DISHES_NOT_1_TO_10,
    DISHES_NOT_A_TABLE,
    DISHES_OF,
    LANGUAGE,
    LANGUAGE_NOT_EN_OR_ZH,
    MEAL_N,
    MEALS,
    NO_MEALS,
    SERVINGS,
    UNKNOWN_MEAL,
)
from recipe_menu.text import and_list


def read_language(table: Mapping[str, object], report: Report) -> Lang | None:
    """Reads the ``language`` of the file.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The language, or ``None`` when the key is missing or its value gave a problem.
    """
    if "language" not in table:
        return None
    place = LANGUAGE.to_bitext()
    text = read_text(table, "language", place, report)
    if text is None:
        return None
    try:
        return Lang(text)
    except ValueError:
        report.add(place, LANGUAGE_NOT_EN_OR_ZH, language=text)
        return None


def _read_meal(item: object, number: int, report: Report) -> Meal | None:
    """Reads one item of ``meals``.

    Args:
        item: The item.
        number: The number of the item, counted from 1.
        report: Where the problems go.

    Returns:
        The meal, or ``None`` after a problem.
    """
    place = MEAL_N.to_bitext(number=number)
    if not isinstance(item, str):
        report.add(place, ITEM_NOT_A_TEXT)
        return None
    text = item.strip()
    if not text:
        report.add(place, EMPTY_ITEM)
        return None
    if text not in Meal:
        report.add(
            MEALS.to_bitext(), UNKNOWN_MEAL, meal=text, meals=and_list(meal.value for meal in Meal)
        )
        return None
    return Meal(text)


def read_meals(table: Mapping[str, object], report: Report) -> tuple[Meal, ...] | None:
    """Reads the ``meals`` of the file.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The meals, each once, in the order of ``Meal``. ``None`` when the key is missing or the
        value gave a problem.
    """
    if "meals" not in table:
        return None
    value = table["meals"]
    if not isinstance(value, list):
        report.add(MEALS.to_bitext(), NOT_A_LIST, key="meals")
        return None
    if not value:
        report.add(MEALS.to_bitext(), NO_MEALS, meals=and_list(meal.value for meal in Meal))
        return None
    found = [_read_meal(item, number, report) for number, item in enumerate(value, 1)]
    return tuple(meal for meal in Meal if meal in found)


def read_servings_key(table: Mapping[str, object], report: Report) -> int | None:
    """Reads the ``servings`` of the file.

    Args:
        table: The table of the file.
        report: Where the problem goes.

    Returns:
        The servings, or ``None`` when the key is missing or the value gave a problem.
    """
    if "servings" not in table:
        return None
    return read_servings(table["servings"], SERVINGS.to_bitext(), report)


def _read_dishes_of(key: str, value: object, report: Report) -> int | None:
    """Reads the number of dishes of one key of ``dishes``.

    Args:
        key: The key as the file writes it.
        value: The value of the key.
        report: Where the problems go.

    Returns:
        The number, or ``None`` after a problem.
    """
    if key not in Meal:
        report.add(
            DISHES.to_bitext(), UNKNOWN_MEAL, meal=key, meals=and_list(meal.value for meal in Meal)
        )
        return None
    place = DISHES_OF.to_bitext(meal=Meal(key).label)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not MIN_DISHES <= value <= MAX_DISHES
    ):
        report.add(place, DISHES_NOT_1_TO_10)
        return None
    return value


def read_dishes(table: Mapping[str, object], report: Report) -> tuple[int, int, int] | None:
    """Reads the ``dishes`` of the file.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The number of dishes of each meal in the order of ``Meal``, 1 for a meal that the table
        leaves out. ``None`` when the key is missing. The numbers are not used when a problem
        was reported.
    """
    if "dishes" not in table:
        return None
    value = table["dishes"]
    if not isinstance(value, dict):
        report.add(DISHES.to_bitext(), DISHES_NOT_A_TABLE)
        return None
    found = {key: _read_dishes_of(key, number, report) for key, number in value.items()}
    breakfast, lunch, dinner = (found.get(meal.value) or 1 for meal in Meal)
    return breakfast, lunch, dinner
