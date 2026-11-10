"""Functions that read and add quantities."""

import re
from collections.abc import Iterable
from fractions import Fraction
from typing import Final

from recipe_menu.lang import Lang
from recipe_menu.units._model import (
    TO_TASTE,
    Quantity,
    Unit,
    WrongQuantity,
    WrongQuantityReason,
)

_NUMBER: Final = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_MAX_DIGITS: Final = 15


def _fold(text: str) -> str:
    """Folds case only when the text is ASCII.

    Args:
        text: The text to fold.

    Returns:
        The lower-case text if it is ASCII, otherwise the text itself, so that only real English
        spellings match in any case.
    """
    return text.lower() if text.isascii() else text


_SPELLINGS: Final[dict[str, Unit]] = {
    **{
        _fold(unit.label(lang, plural=plural)): unit
        for unit in Unit
        for lang in Lang
        for plural in (False, True)
    },
    "克": Unit.G,
    "千克": Unit.KG,
    "公斤": Unit.KG,
    "毫升": Unit.ML,
    "升": Unit.L,
}


def _is_to_taste(text: str) -> bool:
    """Tells whether a stripped text means "to taste".

    Args:
        text: The text without whitespace at either end.

    Returns:
        ``True`` for the Chinese to taste text, or for ``to taste`` in any ASCII case with
        whitespace between the words.
    """
    parts = text.split()
    return text == "适量" or (len(parts) == 2 and [_fold(p) for p in parts] == ["to", "taste"])


def _split_number(text: str) -> tuple[str, str]:
    """Splits a text at its first letter or whitespace character.

    Args:
        text: The text without whitespace at either end.

    Returns:
        The number part and the rest.
    """
    for index, char in enumerate(text):
        if char.isalpha() or char.isspace():
            return text[:index], text[index:]
    return text, ""


def parse_unit(text: str) -> Unit | None:
    """Finds the unit that a word names, in either language.

    Args:
        text: A unit as written, such as ``"g"``, ``"kg"``, or ``"cloves"``. Any string.

    Returns:
        The unit that has ``text`` among its spellings after whitespace at both ends is removed.
        English spellings match in any case. ``None`` when no unit has that spelling.
    """
    return _SPELLINGS.get(_fold(text.strip()))


def _resolve_unit(text: str, rest: str, default_unit: Unit | None) -> Unit | WrongQuantity:
    """Finds the unit of an amount text.

    Args:
        text: The whole amount text, for the wrong value.
        rest: The text after the number, without whitespace at either end.
        default_unit: The unit of an amount that names none.

    Returns:
        The unit, or a ``WrongQuantity`` for an unknown unit or for no unit at all.
    """
    if not rest:
        if default_unit is None:
            return WrongQuantity(WrongQuantityReason.NO_UNIT, text)
        return default_unit
    unit = parse_unit(rest)
    if unit is None:
        return WrongQuantity(WrongQuantityReason.UNKNOWN_UNIT, text, rest)
    return unit


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
    text = text.strip()
    if not text:
        return WrongQuantity(WrongQuantityReason.EMPTY, text)
    if _is_to_taste(text):
        return TO_TASTE
    number, rest = _split_number(text)
    if not _NUMBER.fullmatch(number) or len(number.replace(".", "")) > _MAX_DIGITS:
        return WrongQuantity(WrongQuantityReason.NOT_A_NUMBER, text)
    unit = _resolve_unit(text, rest.strip(), default_unit)
    if isinstance(unit, WrongQuantity):
        return unit
    amount = Fraction(number)
    if amount == 0:
        return WrongQuantity(WrongQuantityReason.ZERO, text)
    return Quantity(amount, unit)


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
    sums: dict[Unit, Fraction] = {}
    for quantity in quantities:
        base = quantity.in_base_unit()
        if base.amount is None or base.unit is None:
            continue
        sums[base.unit] = sums.get(base.unit, Fraction(0)) + base.amount
    return tuple(Quantity(amount, unit) for unit, amount in sums.items())
