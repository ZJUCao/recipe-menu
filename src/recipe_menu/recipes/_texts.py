"""Reading the texts of a recipe file: an item of a list, and the two languages of a table."""

from collections.abc import Mapping
from typing import NamedTuple

from recipe_menu.datafile import (
    EMPTY_ITEM,
    ITEM_NOT_A_TEXT,
    NOT_A_TEXT,
    Report,
    report_unknown_keys,
)
from recipe_menu.lang import BiText
from recipe_menu.text import Message


class Side(NamedTuple):
    """What one language of a name, a note, or the steps holds.

    Attributes:
        texts: The usable texts, each without whitespace at both ends. Empty when the language
            has none.
        missing: Whether the language is missing: its key is missing, or it holds a blank text
            or the empty list.
        wrong: Whether the language holds a value of the wrong kind. An error was reported.
    """

    texts: tuple[str, ...]
    missing: bool
    wrong: bool


class Gaps(NamedTuple):
    """The problems of a missing language.

    Attributes:
        none: The error for both languages missing, or ``None`` when that is no problem.
        no_zh: The warning for a missing Chinese text, when the English one is usable.
        no_en: The warning for a missing English text, when the Chinese one is usable.
    """

    none: Message | None
    no_zh: Message
    no_en: Message


def read_item_text(item: object, place: BiText, report: Report) -> str | None:
    """Reads an item of a list that must be a text.

    Args:
        item: The item, as the file gives it.
        place: The place of the item.
        report: Where the problems go.

    Returns:
        The text without whitespace at both ends, or ``None`` after a problem when the item is
        not a text or holds only whitespace.
    """
    if not isinstance(item, str):
        report.add(place, ITEM_NOT_A_TEXT)
        return None
    text = item.strip()
    if not text:
        report.add(place, EMPTY_ITEM)
        return None
    return text


def _read_side(table: Mapping[str, object], key: str, place: BiText, report: Report) -> Side:
    """Reads one language of a name or a note, which is a text.

    Args:
        table: The table of the name or the note.
        key: ``zh`` or ``en``.
        place: The place of the table.
        report: Where the problem goes.

    Returns:
        The state of the language. A blank text is missing, and a value that is no text is wrong.
    """
    if key not in table:
        return Side((), True, False)
    value = table[key]
    if not isinstance(value, str):
        report.add(place, NOT_A_TEXT, key=key)
        return Side((), False, True)
    text = value.strip()
    return Side((text,), False, False) if text else Side((), True, False)


def report_gaps(zh: Side, en: Side, place: BiText, gaps: Gaps, report: Report) -> None:
    """Reports a missing language, unless a language is wrong.

    Args:
        zh: The Chinese side.
        en: The English side.
        place: The place of the table.
        gaps: The problems to report.
        report: Where the problem goes.
    """
    if zh.wrong or en.wrong:
        return
    if zh.missing and en.missing:
        if gaps.none is not None:
            report.add(place, gaps.none)
    elif zh.missing and en.texts:
        report.warn(place, gaps.no_zh)
    elif en.missing and zh.texts:
        report.warn(place, gaps.no_en)


def read_bitext(
    table: Mapping[str, object],
    place: BiText,
    gaps: Gaps,
    report: Report,
) -> BiText | None:
    """Reads a table with a text in each language.

    The problems come in the order of ``zh``, ``en``, the unknown keys, and then the problem of a
    missing language.

    Args:
        table: The table, which has the keys ``zh`` and ``en``.
        place: The place of the table.
        gaps: The problems of a missing language.
        report: Where the problems go.

    Returns:
        The texts, or ``None`` when a language is wrong or both are missing.
    """
    zh = _read_side(table, "zh", place, report)
    en = _read_side(table, "en", place, report)
    report_unknown_keys(table, ("zh", "en"), place, report)
    report_gaps(zh, en, place, gaps, report)
    if zh.wrong or en.wrong or not (zh.texts or en.texts):
        return None
    return BiText(en.texts[0] if en.texts else None, zh.texts[0] if zh.texts else None)
