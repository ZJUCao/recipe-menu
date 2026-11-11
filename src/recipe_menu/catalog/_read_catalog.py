"""Reading ``catalog.toml`` into a catalog."""

from recipe_menu.catalog._catalog import Catalog
from recipe_menu.datafile import DataFolder, Problem


def read_catalog(folder: DataFolder) -> tuple[Catalog | None, tuple[Problem, ...]]:
    """Reads ``catalog.toml`` into a ``Catalog`` and reports each problem with its place.

    The file has three lists of tables: ``categories`` (keys ``key``, ``zh``, ``en``),
    ``ingredients`` (keys ``zh``, ``en``, ``category``, ``unit``), and ``tags`` (keys ``zh``,
    ``en``). It is read through ``read_toml``. The reader never raises for bad data.

    Args:
        folder: The data folder.

    Returns:
        A pair ``(catalog, problems)``.

        * ``catalog`` is ``None`` when ``read_toml`` gives a problem. Then ``problems`` holds
          only that problem. Otherwise it is a ``Catalog`` of every category, ingredient, and
          tag that no check skips, in the file's order, even when ``problems`` is not empty.
          Each name and each key is stored without whitespace at both ends, and the
          ``category`` of each ingredient is the same ``Category`` object as the one in
          ``catalog.categories``.
        * ``problems`` is a tuple of ``Problem`` values, each with ``Severity.ERROR`` and the
          file ``catalog.toml``. They come in this order: the list ``categories``, then
          ``ingredients``, then ``tags``, then the other keys at the top of the file. Within a
          list, the problems of the list itself come first, then those of each item in order:
          each field in the order of its keys, then its unknown keys in the file's order, then
          its duplicates, the key of a category first, then the Chinese name, then the English
          name.

        These rules decide the problems, with the places ``categories``, ``ingredients``,
        ``tags``, ``category N``, ``ingredient N``, and ``tag N``, where N counts the items of a
        list from 1, skipped items included. ``NOT_A_LIST`` is at the list, and every problem of
        an item is at the item. In ``UNKNOWN_KEY``, the form is chosen by the number of keys of
        the kind, and ``keys`` is the ``and_list`` of those keys in the order of the design's
        table of keys. In ``UNKNOWN_CATEGORY``, the form is chosen by the number of kept
        categories, and ``categories`` is the ``and_list`` of their keys in order. The values
        ``key`` of ``DUPLICATE_KEY``, ``category``, ``unit``, and ``name`` are stripped of
        whitespace at both ends.

        * A list that is missing gives ``MISSING_KEY`` with no place, and one that is not a list
          gives ``NOT_A_LIST``. Either is read as empty.
        * An item that is not a table gives ``NOT_A_TABLE`` and is skipped. A key that its kind
          does not have gives ``UNKNOWN_KEY`` and is ignored, and a key at the top of the file
          other than ``categories``, ``ingredients``, and ``tags`` gives ``UNKNOWN_KEY`` with no
          place and is ignored.
        * A required text (all three keys of a category, ``zh``, ``en``, and ``category`` of an
          ingredient, both keys of a tag) that is missing gives ``MISSING_KEY``, one that is not
          a text gives ``NOT_A_TEXT``, and one that is empty or only whitespace gives
          ``EMPTY_TEXT``. A category is skipped when its ``key`` has a problem or both its
          ``zh`` and ``en`` have one, and otherwise kept with its usable name. An ingredient or
          a tag is skipped.
        * An ingredient whose ``category`` matches the key of no kept category gives
          ``UNKNOWN_CATEGORY``, or ``NO_CATEGORIES`` when no category was kept, and is skipped.
        * An ingredient whose ``unit`` is not a text gives ``NOT_A_TEXT``, and one whose
          ``unit`` is a text that ``parse_unit`` does not know gives ``UNKNOWN_UNIT``. Both are
          kept with no default unit. A ``unit`` that is missing, empty, or only whitespace gives
          no problem.
        * An item that one check keeps is still skipped when another check skips it.
        * An item that no other check skips is checked for duplicates against the items of the
          same kind that were kept. Only the usable names of a category are compared. A category
          whose key matches gives ``DUPLICATE_KEY`` and is skipped. A category whose Chinese or
          English name matches a name, in either language, of a kept category gives
          ``DUPLICATE_ZH_NAME`` or ``DUPLICATE_EN_NAME`` and is kept.
          An ingredient or a tag whose names match gives the same messages and is skipped. Each
          problem names the first earlier item with that key or name. Matching follows the
          rules of ``Catalog.find_ingredient``.

    Raises:
        NotImplementedError: In the mock.
    """
    raise NotImplementedError
