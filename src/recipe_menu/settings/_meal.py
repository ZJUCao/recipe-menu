"""The meals of a day."""

from enum import StrEnum

from recipe_menu.lang import BiText
from recipe_menu.settings.messages import (
    BREAKFAST_HEADING,
    BREAKFAST_LABEL,
    DINNER_HEADING,
    DINNER_LABEL,
    LUNCH_HEADING,
    LUNCH_LABEL,
)

_LABELS = {"breakfast": BREAKFAST_LABEL, "lunch": LUNCH_LABEL, "dinner": DINNER_LABEL}
_HEADINGS = {"breakfast": BREAKFAST_HEADING, "lunch": LUNCH_HEADING, "dinner": DINNER_HEADING}


class Meal(StrEnum):
    """The meals of a day, in the order of the day, with their names in both languages.

    Each member's value is the word that the settings and the menu files use. ``list(Meal)``
    gives ``BREAKFAST``, ``LUNCH``, and ``DINNER``, in the order of a day. ``Meal(value)`` gives
    the member whose value is ``value``, and ``value in Meal`` tells whether a word is a meal,
    without an exception. A ``Meal`` is a ``str``, so ``sorted`` sorts meals by their words,
    which is not the order of a day. Sort them with ``key=list(Meal).index``. A message shows a
    meal through ``label`` or ``heading``, because ``Message.render`` rejects an enum member.

    Raises:
        ValueError: ``Meal(value)`` gets a word that is not a member's value, such as ``supper``
            or ``Lunch``.
    """

    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

    @property
    def label(self) -> BiText:
        """Gives the meal's name inside a sentence or a place.

        Returns:
            The English name is ``breakfast``, ``lunch``, or ``dinner``, as the value is. The
            Chinese name is the two characters for breakfast (U+65E9 U+9910), for lunch
            (U+5348 U+9910), or for dinner (U+665A U+9910).
        """
        return _LABELS[self.value].to_bitext()

    @property
    def heading(self) -> BiText:
        """Gives the meal's name at the top of a column.

        Returns:
            The English name is ``Breakfast``, ``Lunch``, or ``Dinner``, with a capital letter.
            The Chinese name is the same as the Chinese name of ``label``.
        """
        return _HEADINGS[self.value].to_bitext()
