"""The one rule for a servings number in a data file."""

from typing import Final

from recipe_menu.datafile._shape import Report
from recipe_menu.datafile.messages import (
    SERVINGS_NOT_A_NUMBER,
    SERVINGS_TOO_FEW,
    SERVINGS_TOO_MANY,
)
from recipe_menu.lang import BiText

MIN_SERVINGS: Final[int] = 1
MAX_SERVINGS: Final[int] = 100
_MAX_DIGITS_VALUE: Final[int] = 999_999_999_999_999


def read_servings(value: object, place: BiText, report: Report) -> int | None:
    """Reads a servings number: an integer from 1 to 100.

    Args:
        value: A servings value as ``read_toml`` gives it, such as ``2`` or ``"2"``. The caller
            has found the key.
        place: The place of the value, such as "servings" and its Chinese name.
        report: Where the problem goes.

    Returns:
        ``value`` when it is an ``int``, not a ``bool``, from ``MIN_SERVINGS`` to
        ``MAX_SERVINGS``. Otherwise ``None``, after one error at ``place`` in ``report``. The
        error is ``SERVINGS_NOT_A_NUMBER`` for a value that is not an integer, such as ``"2"``,
        ``2.5``, or ``True``, and for an integer of 16 or more digits. It is
        ``SERVINGS_TOO_FEW`` with ``servings`` set to the value for an integer from
        -999,999,999,999,999 to 0, and ``SERVINGS_TOO_MANY`` with ``servings`` set to the value
        for an integer from 101 to 999,999,999,999,999. So a message never shows more than 15
        digits.
    """
    if isinstance(value, bool) or not isinstance(value, int) or abs(value) > _MAX_DIGITS_VALUE:
        report.add(place, SERVINGS_NOT_A_NUMBER)
    elif value < MIN_SERVINGS:
        report.add(place, SERVINGS_TOO_FEW, servings=value)
    elif value > MAX_SERVINGS:
        report.add(place, SERVINGS_TOO_MANY, servings=value)
    else:
        return value
    return None
