"""The meals of a day."""

from enum import StrEnum

from recipe_menu.lang import BiText


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

        The mock raises ``NotImplementedError``. The implementation gives the name by the rule
        below.

        Returns:
            The English name is ``breakfast``, ``lunch``, or ``dinner``, as the value is. The
            Chinese name is the two characters for breakfast (U+65E9 U+9910), for lunch
            (U+5348 U+9910), or for dinner (U+665A U+9910).

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    @property
    def heading(self) -> BiText:
        """Gives the meal's name at the top of a column.

        The mock raises ``NotImplementedError``. The implementation gives the name by the rule
        below.

        Returns:
            The English name is ``Breakfast``, ``Lunch``, or ``Dinner``, with a capital letter.
            The Chinese name is the same as the Chinese name of ``label``.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError
