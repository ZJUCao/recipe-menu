"""Reading the tags and the ingredient lines of a recipe file."""

from collections.abc import Mapping

from recipe_menu.catalog import Catalog, Ingredient, Tag
from recipe_menu.datafile import (
    Report,
    read_list,
    read_table,
    read_text,
    report_unknown_keys,
)
from recipe_menu.lang import BiText
from recipe_menu.recipes._model import RecipeIngredient
from recipe_menu.recipes._texts import Gaps, read_bitext, read_item_text
from recipe_menu.recipes.messages import (
    AMOUNT_NO_UNIT,
    AMOUNT_NOT_A_NUMBER,
    AMOUNT_UNKNOWN_UNIT,
    AMOUNT_ZERO,
    INGREDIENT_N,
    INGREDIENTS,
    NO_EN_NOTE,
    NO_ZH_NOTE,
    NOT_A_ZH_EN_TABLE,
    TAG_N,
    TAGS,
    UNKNOWN_INGREDIENT,
    UNKNOWN_TAG,
)
from recipe_menu.units import Quantity, WrongQuantity, WrongQuantityReason, parse_quantity

_NOTE_GAPS = Gaps(None, NO_ZH_NOTE, NO_EN_NOTE)
_LINE_KEYS = ("item", "amount", "note")
_AMOUNT_MESSAGES = {
    WrongQuantityReason.NOT_A_NUMBER: AMOUNT_NOT_A_NUMBER,
    WrongQuantityReason.ZERO: AMOUNT_ZERO,
}


def read_tags(
    table: Mapping[str, object],
    catalog: Catalog | None,
    report: Report,
) -> tuple[Tag, ...]:
    """Reads the tags of the recipe.

    Args:
        table: The table of the file.
        catalog: The catalog that the tags come from, or ``None``.
        report: Where the problems go.

    Returns:
        The tags that the items name, each once, in the order of the first item that names it.
    """
    place = TAGS.to_bitext()
    tags: list[Tag] = []
    for number, item in enumerate(read_list(table, "tags", place, report), 1):
        text = read_item_text(item, TAG_N.to_bitext(number=number), report)
        if text is None or catalog is None:
            continue
        tag = catalog.find_tag(text)
        if tag is None:
            report.add(place, UNKNOWN_TAG, tag=text)
        elif tag not in tags:
            tags.append(tag)
    return tuple(tags)


def _read_item(
    row: Mapping[str, object],
    place: BiText,
    catalog: Catalog | None,
    report: Report,
) -> Ingredient | None:
    """Reads the ``item`` of an ingredient line.

    Args:
        row: The table of the line.
        place: The place of the line.
        catalog: The catalog that the names come from, or ``None``.
        report: Where the problems go.

    Returns:
        The ingredient that ``item`` names, or ``None`` after a problem, or when ``catalog`` is
        ``None``.
    """
    name = read_text(row, "item", place, report)
    if name is None or catalog is None:
        return None
    ingredient = catalog.find_ingredient(name)
    if ingredient is None:
        report.add(place, UNKNOWN_INGREDIENT, name=name)
    return ingredient


def _report_wrong(
    wrong: WrongQuantity,
    ingredient: Ingredient | None,
    place: BiText,
    report: Report,
) -> None:
    """Reports the reason why an amount cannot be read.

    Args:
        wrong: What ``parse_quantity`` gave.
        ingredient: The ingredient of the line, or ``None`` when it has a problem.
        place: The place of the line.
        report: Where the problem goes.
    """
    if wrong.reason is WrongQuantityReason.UNKNOWN_UNIT:
        report.add(place, AMOUNT_UNKNOWN_UNIT, amount=wrong.text, unit=str(wrong.unit))
    elif wrong.reason is WrongQuantityReason.NO_UNIT:
        if ingredient is not None:
            report.add(place, AMOUNT_NO_UNIT, amount=wrong.text, ingredient=ingredient.name)
    elif wrong.reason in _AMOUNT_MESSAGES:
        report.add(place, _AMOUNT_MESSAGES[wrong.reason], amount=wrong.text)


def _read_amount(
    row: Mapping[str, object],
    place: BiText,
    ingredient: Ingredient | None,
    report: Report,
) -> Quantity | None:
    """Reads the ``amount`` of an ingredient line.

    Args:
        row: The table of the line.
        place: The place of the line.
        ingredient: The ingredient of the line, or ``None`` when it has a problem. Its default
            unit goes to ``parse_quantity``.
        report: Where the problems go.

    Returns:
        The quantity, or ``None`` after a problem, or when ``ingredient`` is ``None`` and the
        amount has no unit.
    """
    text = read_text(row, "amount", place, report)
    if text is None:
        return None
    quantity = parse_quantity(text, None if ingredient is None else ingredient.unit)
    if isinstance(quantity, WrongQuantity):
        _report_wrong(quantity, ingredient, place, report)
        return None
    return quantity


def _read_note(row: Mapping[str, object], place: BiText, report: Report) -> BiText | None:
    """Reads the optional ``note`` of an ingredient line.

    Args:
        row: The table of the line.
        place: The place of the line.
        report: Where the problems go.

    Returns:
        The note, or ``None`` when it is missing, wrong, or has no language.
    """
    if "note" not in row:
        return None
    value = row["note"]
    if not isinstance(value, dict):
        report.add(place, NOT_A_ZH_EN_TABLE, key="note")
        return None
    return read_bitext(value, place, _NOTE_GAPS, report)


def _read_line(
    item: object,
    number: int,
    catalog: Catalog | None,
    report: Report,
) -> RecipeIngredient | None:
    """Reads one ingredient line.

    Args:
        item: The item of the list, as the file gives it.
        number: The number of the item, counted from 1.
        catalog: The catalog that the names come from, or ``None``.
        report: Where the problems go.

    Returns:
        The line, or ``None`` after a problem, or when ``catalog`` is ``None``.
    """
    place = INGREDIENT_N.to_bitext(number=number)
    row = read_table(item, place, report)
    if row is None:
        return None
    ingredient = _read_item(row, place, catalog, report)
    quantity = _read_amount(row, place, ingredient, report)
    note = _read_note(row, place, report)
    report_unknown_keys(row, _LINE_KEYS, place, report)
    if ingredient is None or quantity is None:
        return None
    return RecipeIngredient(ingredient, quantity, note)


def read_ingredients(
    table: Mapping[str, object],
    catalog: Catalog | None,
    report: Report,
) -> tuple[RecipeIngredient, ...]:
    """Reads the ingredient lines of the recipe.

    Args:
        table: The table of the file.
        catalog: The catalog that the names come from, or ``None``.
        report: Where the problems go.

    Returns:
        The lines in the file's order, without the lines that have a problem.
    """
    items = read_list(table, "ingredients", INGREDIENTS.to_bitext(), report)
    lines = [_read_line(item, number, catalog, report) for number, item in enumerate(items, 1)]
    return tuple(line for line in lines if line is not None)
