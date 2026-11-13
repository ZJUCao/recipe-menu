"""The short text of one date, in both languages."""

from datetime import date
from typing import Final

from recipe_menu.lang import BiText
from recipe_menu.menus._model import Day
from recipe_menu.menus.messages import (
    FRIDAY_SHORT,
    MONDAY_SHORT,
    SATURDAY_SHORT,
    SHORT_DATE,
    SHORT_MONTH_NAMES,
    SUNDAY_SHORT,
    THURSDAY_SHORT,
    TUESDAY_SHORT,
    WEDNESDAY_SHORT,
)
from recipe_menu.text import Message

_SHORT_NAMES: Final[tuple[Message, ...]] = (
    MONDAY_SHORT,
    TUESDAY_SHORT,
    WEDNESDAY_SHORT,
    THURSDAY_SHORT,
    FRIDAY_SHORT,
    SATURDAY_SHORT,
    SUNDAY_SHORT,
)


def short_date(day: date) -> BiText:
    """Writes the date of one day as a short text in both languages.

    Args:
        day: The date to write.

    Returns:
        A ``BiText`` with both languages set. The English text is the short name of the weekday,
        the day, and the short name of the month, such as ``Mon 16 Nov``. The Chinese text is
        the day's label, the month number, and the day number, with the characters for month and
        day after their numbers. It never raises.
    """
    index = day.weekday()
    weekday = BiText(_SHORT_NAMES[index].en, list(Day)[index].label.zh)
    month = SHORT_MONTH_NAMES[day.month - 1].to_bitext()
    return SHORT_DATE.to_bitext(weekday=weekday, day=day.day, month=month)
