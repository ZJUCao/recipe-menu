"""The split and the check of one ingredient line."""

import re

from recipe_menu.catalog import Catalog, Ingredient
from recipe_menu.commands.add._model import IngredientLine
from recipe_menu.commands.add.messages import (
    AMOUNT_NO_UNIT,
    AMOUNT_NOT_A_NUMBER,
    AMOUNT_UNKNOWN_UNIT,
    AMOUNT_ZERO,
    NAME_AND_QUANTITY,
    UNKNOWN_INGREDIENT,
)
from recipe_menu.lang import Lang
from recipe_menu.units import WrongQuantity, WrongQuantityReason, parse_quantity

_WORD = re.compile(r"\S+")
_ASCII_DIGITS = "0123456789"
_TO_TASTE_ZH = "适量"


def _quantity_start(words: list[str]) -> int | None:
    """Finds the word where the quantity starts.

    Args:
        words: The words of the line, not empty.

    Returns:
        The index of the first word of the quantity, or ``None`` when the line has none.
    """
    if words[-1] == _TO_TASTE_ZH:
        return len(words) - 1
    if len(words) > 1 and words[-2].lower() == "to" and words[-1].lower() == "taste":
        return len(words) - 2
    return next((i for i in reversed(range(len(words))) if words[i][0] in _ASCII_DIGITS), None)


def split_line(line: str) -> IngredientLine | None:
    """Splits an ingredient line into its name and its quantity.

    Args:
        line: The line without whitespace at both ends, not empty.

    Returns:
        The name and the quantity, or ``None`` when the line has no quantity or no name.
    """
    matches = list(_WORD.finditer(line))
    start = _quantity_start([match.group() for match in matches])
    if start is None:
        return None
    cut = matches[start].start()
    name = line[:cut].strip()
    return IngredientLine(name, line[cut:]) if name else None


def _wrong_amount(wrong: WrongQuantity, ingredient: Ingredient, lang: Lang) -> str:
    """Writes the message for a quantity that cannot be read.

    Args:
        wrong: What is wrong with the quantity.
        ingredient: The ingredient of the line.
        lang: The language of the message.

    Returns:
        The message of the reason of ``wrong``.
    """
    if wrong.reason is WrongQuantityReason.UNKNOWN_UNIT:
        return AMOUNT_UNKNOWN_UNIT.render(lang, amount=wrong.text, unit=str(wrong.unit))
    if wrong.reason is WrongQuantityReason.NO_UNIT:
        return AMOUNT_NO_UNIT.render(lang, amount=wrong.text, ingredient=ingredient.name)
    if wrong.reason is WrongQuantityReason.ZERO:
        return AMOUNT_ZERO.render(lang, amount=wrong.text)
    return AMOUNT_NOT_A_NUMBER.render(lang, amount=wrong.text)


def check_line(catalog: Catalog, line: str, lang: Lang) -> IngredientLine | str:
    """Checks one ingredient line against the catalog.

    Args:
        catalog: The catalog.
        line: The line without whitespace at both ends, not empty.
        lang: The language of a message.

    Returns:
        The split line when it is right, else the message of the first check that fails: the
        split, the name, or the quantity.
    """
    split = split_line(line)
    if split is None:
        return NAME_AND_QUANTITY.render(lang)
    ingredient = catalog.find_ingredient(split.name)
    if ingredient is None:
        return UNKNOWN_INGREDIENT.render(lang, name=split.name)
    quantity = parse_quantity(split.quantity, ingredient.unit)
    if isinstance(quantity, WrongQuantity):
        return _wrong_amount(quantity, ingredient, lang)
    return split
