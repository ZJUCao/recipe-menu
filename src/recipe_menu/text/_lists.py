"""Lists of texts in both languages."""

from collections.abc import Iterable
from enum import Enum

from recipe_menu.lang import BiText, Lang

_ASCII_ALNUM = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
_ZH_COMMA = "、"
_ZH_AND = "和"


def _collect(items: Iterable[str | BiText]) -> list[str | BiText]:
    """Checks the items of a list and gathers them.

    Args:
        items: The items to check.

    Returns:
        The items, in order.

    Raises:
        TypeError: ``items`` is a ``str``, or an item is neither a ``str`` nor a ``BiText``, or
            is an ``enum.Enum`` member.
    """
    if isinstance(items, str):
        raise TypeError("items must not be a str")
    gathered = list(items)
    for item in gathered:
        if isinstance(item, Enum) or not isinstance(item, str | BiText):
            raise TypeError(f"an item must be a str or a BiText, not {type(item).__name__}")
    return gathered


def _texts(items: list[str | BiText], lang: Lang) -> list[str]:
    """Gives each item in one language.

    Args:
        items: The checked items.
        lang: The language to give.

    Returns:
        The text of each item, with the fallback of ``BiText.get``.
    """
    return [item if isinstance(item, str) else item.get(lang) for item in items]


def _english_and(texts: list[str]) -> str:
    """Joins English texts for a sentence.

    Args:
        texts: The texts to join.

    Returns:
        The joined text.
    """
    if len(texts) < 3:
        return " and ".join(texts)
    return ", ".join(texts[:-1]) + ", and " + texts[-1]


def _chinese_and(texts: list[str]) -> str:
    """Joins Chinese texts for a sentence.

    Args:
        texts: The texts to join.

    Returns:
        The joined text, with a space next to U+548C only beside an ASCII letter or digit.
    """
    if len(texts) < 2:
        return "".join(texts)
    head = _ZH_COMMA.join(texts[:-1])
    last = texts[-1]
    left = " " if head and head[-1] in _ASCII_ALNUM else ""
    right = " " if last and last[0] in _ASCII_ALNUM else ""
    return head + left + _ZH_AND + right + last


def and_list(items: Iterable[str | BiText]) -> BiText:
    """Joins texts into a list for a sentence, in both languages.

    Args:
        items: The texts to join, in order. A ``str`` item is the same in both languages. Any
            number of items, none included. Not a single ``str``.

    Returns:
        A ``BiText`` with both languages set. The English text joins each item's
        ``get(Lang.EN)``, and the Chinese text joins each item's ``get(Lang.ZH)``. No items give
        the empty string, and one item gives that item. In English, two items are joined with
        " and ", and three or more with ", " between the items and "and " before the last one.
        In Chinese, the separator is U+3001 between the items and U+548C before the last one.
        Spacing in Chinese: no space goes next to U+3001. A space goes between U+548C and an item
        when the item's character next to U+548C is an ASCII letter or digit (the last character
        of the item before it, or the first of the item after it). An empty item has no
        character next to U+548C, so no space goes there. The rules read each item's
        ``get(Lang.ZH)``, so they also apply to the English text of an item that has no Chinese.

    Raises:
        TypeError: ``items`` is a ``str``, or an item is neither a ``str`` nor a ``BiText``,
            such as ``None`` or an ``enum.Enum`` member (a ``StrEnum`` member included).
    """
    gathered = _collect(items)
    return BiText(_english_and(_texts(gathered, Lang.EN)), _chinese_and(_texts(gathered, Lang.ZH)))


def comma_list(items: Iterable[str | BiText]) -> BiText:
    """Joins texts into a plain list, in both languages.

    Args:
        items: The texts to join, in order. A ``str`` item is the same in both languages. Any
            number of items, none included. Not a single ``str``.

    Returns:
        A ``BiText`` with both languages set. The English text joins each item's
        ``get(Lang.EN)`` with ", ", and the Chinese text joins each item's ``get(Lang.ZH)``
        with U+3001. No space goes next to U+3001. No items give the empty string, and one item
        gives that item.

    Raises:
        TypeError: ``items`` is a ``str``, or an item is neither a ``str`` nor a ``BiText``,
            such as ``None`` or an ``enum.Enum`` member (a ``StrEnum`` member included).
    """
    gathered = _collect(items)
    return BiText(", ".join(_texts(gathered, Lang.EN)), _ZH_COMMA.join(_texts(gathered, Lang.ZH)))
