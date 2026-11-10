"""Functions that read and add quantities."""

from collections.abc import Iterable

from recipe_menu.units._model import Quantity, Unit, WrongQuantity


def parse_unit(text: str) -> Unit | None:
    """Finds the unit that a word names, in either language.

    Args:
        text: A unit as written, such as ``"g"``, ``"kg"``, or ``"cloves"``. Any string.

    Returns:
        The unit that has ``text`` among its spellings after whitespace at both ends is removed.
        English spellings match in any case. ``None`` when no unit has that spelling.
    """
    raise NotImplementedError


def parse_quantity(text: str, default_unit: Unit | None = None) -> Quantity | WrongQuantity:
    """Reads an amount as a recipe writes it.

    The amount is a number with or without a unit, or "to taste". This function never
    raises, because a number of more than 15 digits is a wrong quantity and not an error. The
    reasons are checked in the order of the design.

    Args:
        text: The amount as written, such as ``"300 g"``, ``"1.5 kg"``, or ``"3"``.
        default_unit: The unit of an amount that names none. A unit in ``text`` always wins.

    Returns:
        A ``Quantity``, or a ``WrongQuantity`` with the first reason that applies when ``text``
        cannot be read.
    """
    raise NotImplementedError


def add_quantities(quantities: Iterable[Quantity]) -> tuple[Quantity, ...]:
    """Adds up quantities of the same kind.

    Mass is added in grams, volume in millilitres, and each count unit on its own. Mass, volume,
    and counts are never converted into each other. To taste adds nothing.

    Args:
        quantities: The quantities to add, to taste included. May be empty.

    Returns:
        One exact, unrounded sum for each group, in the order in which the groups first appear.
        The tuple is empty when no quantity has an amount.
    """
    raise NotImplementedError
