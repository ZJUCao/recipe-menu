"""Reading the name and the steps of a recipe file."""

from collections.abc import Mapping

from recipe_menu.datafile import MISSING_KEY, NOT_A_LIST, Report, report_unknown_keys
from recipe_menu.lang import BiText
from recipe_menu.recipes._model import Steps
from recipe_menu.recipes._texts import Gaps, Side, read_bitext, read_item_text, report_gaps
from recipe_menu.recipes.messages import (
    EN_STEP_N,
    NAME,
    NO_EN_NAME,
    NO_EN_STEPS,
    NO_NAME,
    NO_STEPS,
    NO_ZH_NAME,
    NO_ZH_STEPS,
    NOT_A_STEPS_TABLE,
    NOT_A_ZH_EN_TABLE,
    STEPS,
    ZH_STEP_N,
)
from recipe_menu.text import Message

_NAME_GAPS = Gaps(NO_NAME, NO_ZH_NAME, NO_EN_NAME)
_STEPS_GAPS = Gaps(NO_STEPS, NO_ZH_STEPS, NO_EN_STEPS)


def read_name(table: Mapping[str, object], report: Report) -> BiText | None:
    """Reads the name of the recipe.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The name, or ``None`` after a problem when it is missing, is not a table, or has a
        wrong or no language.
    """
    if "name" not in table:
        report.add(None, MISSING_KEY, key="name")
        return None
    place = NAME.to_bitext()
    value = table["name"]
    if not isinstance(value, dict):
        report.add(place, NOT_A_ZH_EN_TABLE, key="name")
        return None
    return read_bitext(value, place, _NAME_GAPS, report)


def _read_steps_side(
    table: Mapping[str, object],
    key: str,
    step_place: Message,
    report: Report,
) -> Side:
    """Reads the list of steps of one language.

    Args:
        table: The table of the steps.
        key: ``zh`` or ``en``.
        step_place: The place of a step, such as ``ZH_STEP_N``.
        report: Where the problems go.

    Returns:
        The state of the language. The empty list is missing, and a value that is no list is
        wrong.
    """
    if key not in table:
        return Side((), True, False)
    value = table[key]
    if not isinstance(value, list):
        report.add(STEPS.to_bitext(), NOT_A_LIST, key=key)
        return Side((), False, True)
    found = (
        read_item_text(item, step_place.to_bitext(number=number), report)
        for number, item in enumerate(value, 1)
    )
    return Side(tuple(text for text in found if text is not None), not value, False)


def read_steps(table: Mapping[str, object], report: Report) -> Steps | None:
    """Reads the steps of the recipe.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The steps, or ``None`` after a problem when they are missing, are not a table, or have
        a wrong or no language.
    """
    if "steps" not in table:
        report.add(None, MISSING_KEY, key="steps")
        return None
    place = STEPS.to_bitext()
    value = table["steps"]
    if not isinstance(value, dict):
        report.add(place, NOT_A_STEPS_TABLE)
        return None
    zh = _read_steps_side(value, "zh", ZH_STEP_N, report)
    en = _read_steps_side(value, "en", EN_STEP_N, report)
    report_unknown_keys(value, ("zh", "en"), place, report)
    report_gaps(zh, en, place, _STEPS_GAPS, report)
    if zh.wrong or en.wrong or not (zh.texts or en.texts):
        return None
    return Steps(en.texts or None, zh.texts or None)
