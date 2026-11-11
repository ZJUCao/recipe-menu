"""Lists of texts in both languages."""

from collections.abc import Iterable

from recipe_menu.lang import BiText


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
        NotImplementedError: In the mock.
    """
    raise NotImplementedError


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
        NotImplementedError: In the mock.
    """
    raise NotImplementedError
