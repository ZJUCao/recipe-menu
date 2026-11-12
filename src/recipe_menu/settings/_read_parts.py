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
from recipe_menu.settings.messages import (
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
