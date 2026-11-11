"""Reading ``catalog.toml`` into a catalog."""

from collections.abc import Callable

from recipe_menu.catalog._catalog import Catalog
from recipe_menu.catalog._matching import matching_form
from recipe_menu.catalog._model import Category, Ingredient, Tag
from recipe_menu.catalog._shape import (
    Report,
    read_list,
    read_table,
    read_text,
    report_unknown_keys,
)
from recipe_menu.catalog.messages import (
    CATEGORIES,
    CATEGORY_N,
    DUPLICATE_EN_NAME,
    DUPLICATE_KEY,
    DUPLICATE_ZH_NAME,
    INGREDIENT_N,
    INGREDIENTS,
    NO_CATEGORIES,
    TAG_N,
    TAGS,
    UNKNOWN_CATEGORY,
    UNKNOWN_UNIT,
)
from recipe_menu.datafile import NOT_A_TEXT, DataFolder, Problem, read_toml
from recipe_menu.lang import BiText
from recipe_menu.text import Message, and_list
from recipe_menu.units import Unit, parse_unit

_CATEGORY_KEYS = ("key", "zh", "en")
_INGREDIENT_KEYS = ("zh", "en", "category", "unit")
_TAG_KEYS = ("zh", "en")
_TOP_KEYS = ("categories", "ingredients", "tags")


class _Names:
    """The keys or names of the items of one kind that were kept, by matching form.

    Each entry gives the number of the first kept item that has the key or name.
    """

    def __init__(self) -> None:
        """Starts with no names."""
        self._first: dict[str, int] = {}

    def find(self, text: str) -> int | None:
        """Finds the first kept item that has a key or name.

        Args:
            text: A key or a name.

        Returns:
            The number of the item, or ``None`` when no kept item has a text that matches.
        """
        return self._first.get(matching_form(text))

    def add(self, number: int, *texts: str | None) -> None:
        """Keeps the key or names of an item, unless an earlier item has them.

        Args:
            number: The number of the item.
            *texts: The keys or names, where ``None`` is skipped.
        """
        for text in texts:
            if text is not None:
                self._first.setdefault(matching_form(text), number)


class _Kept:
    """What ``read_catalog`` has kept so far, with the names of each kind."""

    def __init__(self) -> None:
        """Starts with nothing kept."""
        self.categories: list[Category] = []
        self.ingredients: list[Ingredient] = []
        self.tags: list[Tag] = []
        self.category_keys = _Names()
        self.category_names = _Names()
        self.ingredient_names = _Names()
        self.tag_names = _Names()
        self.category_by_key: dict[str, Category] = {}


def _report_name_duplicates(
    names: _Names,
    place: Message,
    zh: str | None,
    en: str | None,
    *,
    where: BiText,
    report: Report,
) -> bool:
    """Reports the Chinese and the English name of an item that an earlier item has.

    Args:
        names: The names of the kept items of the kind.
        place: The message of the place of an item of the kind, with ``number``.
        zh: The Chinese name, or ``None`` when it is not usable.
        en: The English name, or ``None`` when it is not usable.
        where: The place of the item.
        report: Where the problems go.

    Returns:
        ``True`` when at least one name is a duplicate.
    """
    found = False
    for name, message in ((zh, DUPLICATE_ZH_NAME), (en, DUPLICATE_EN_NAME)):
        number = None if name is None else names.find(name)
        if name is not None and number is not None:
            report.add(where, message, name=name, other=place.to_bitext(number=number))
            found = True
    return found


def _read_category(item: object, number: int, kept: _Kept, report: Report) -> None:
    """Reads one category and keeps it when no check skips it.

    Args:
        item: The item, as the file gives it.
        number: The number of the item, counted from 1.
        kept: What has been kept.
        report: Where the problems go.
    """
    where = CATEGORY_N.to_bitext(number=number)
    table = read_table(item, where, report)
    if table is None:
        return
    key = read_text(table, "key", where, report)
    zh = read_text(table, "zh", where, report)
    en = read_text(table, "en", where, report)
    report_unknown_keys(table, _CATEGORY_KEYS, where, report)
    if key is None or (zh is None and en is None):
        return
    earlier = kept.category_keys.find(key)
    if earlier is not None:
        report.add(where, DUPLICATE_KEY, key=key, other=CATEGORY_N.to_bitext(number=earlier))
    _report_name_duplicates(kept.category_names, CATEGORY_N, zh, en, where=where, report=report)
    if earlier is None:
        category = Category(key, BiText(en, zh))
        kept.categories.append(category)
        kept.category_by_key[matching_form(key)] = category
        kept.category_keys.add(number, key)
        kept.category_names.add(number, zh, en)


def _read_unit(table: dict[str, object], where: BiText, report: Report) -> Unit | None:
    """Reads the optional ``unit`` of an ingredient.

    Args:
        table: The ingredient's table.
        where: The place of the ingredient.
        report: Where the problems go.

    Returns:
        The unit, or ``None`` when the key is missing, empty, not a text, or not a known unit.
    """
    if "unit" not in table:
        return None
    value = table["unit"]
    if not isinstance(value, str):
        report.add(where, NOT_A_TEXT, key="unit")
        return None
    text = value.strip()
    if not text:
        return None
    unit = parse_unit(text)
    if unit is None:
        report.add(where, UNKNOWN_UNIT, unit=text)
    return unit


def _find_category(name: str, where: BiText, kept: _Kept, report: Report) -> Category | None:
    """Finds the category that an ingredient names, or reports it as unknown.

    Args:
        name: The ingredient's ``category``, without whitespace at both ends.
        where: The place of the ingredient.
        kept: What has been kept.
        report: Where the problems go.

    Returns:
        The kept category whose key matches, or ``None`` after a problem.
    """
    category = kept.category_by_key.get(matching_form(name))
    if category is not None:
        return category
    if not kept.categories:
        report.add(where, NO_CATEGORIES, category=name)
        return None
    keys = and_list([kept_category.key for kept_category in kept.categories])
    message = UNKNOWN_CATEGORY.pick(len(kept.categories))
    report.add(where, message, category=name, categories=keys)
    return None


def _read_ingredient(item: object, number: int, kept: _Kept, report: Report) -> None:
    """Reads one ingredient and keeps it when no check skips it.

    Args:
        item: The item, as the file gives it.
        number: The number of the item, counted from 1.
        kept: What has been kept.
        report: Where the problems go.
    """
    where = INGREDIENT_N.to_bitext(number=number)
    table = read_table(item, where, report)
    if table is None:
        return
    zh = read_text(table, "zh", where, report)
    en = read_text(table, "en", where, report)
    name = read_text(table, "category", where, report)
    category = None if name is None else _find_category(name, where, kept, report)
    unit = _read_unit(table, where, report)
    report_unknown_keys(table, _INGREDIENT_KEYS, where, report)
    if zh is None or en is None or category is None:
        return
    if _report_name_duplicates(
        kept.ingredient_names, INGREDIENT_N, zh, en, where=where, report=report
    ):
        return
    kept.ingredients.append(Ingredient(BiText(en, zh), category, unit))
    kept.ingredient_names.add(number, zh, en)


def _read_tag(item: object, number: int, kept: _Kept, report: Report) -> None:
    """Reads one tag and keeps it when no check skips it.

    Args:
        item: The item, as the file gives it.
        number: The number of the item, counted from 1.
        kept: What has been kept.
        report: Where the problems go.
    """
    where = TAG_N.to_bitext(number=number)
    table = read_table(item, where, report)
    if table is None:
        return
    zh = read_text(table, "zh", where, report)
    en = read_text(table, "en", where, report)
    report_unknown_keys(table, _TAG_KEYS, where, report)
    if zh is None or en is None:
        return
    if _report_name_duplicates(kept.tag_names, TAG_N, zh, en, where=where, report=report):
        return
    kept.tags.append(Tag(BiText(en, zh)))
    kept.tag_names.add(number, zh, en)


_ItemReader = Callable[[object, int, _Kept, Report], None]


def _read_lists(table: dict[str, object], report: Report) -> Catalog:
    """Reads the three lists of a catalog file, then the unknown keys at the top.

    Args:
        table: The table of the file.
        report: Where the problems go.

    Returns:
        The catalog of everything that was kept.
    """
    kept = _Kept()
    lists: tuple[tuple[str, Message, _ItemReader], ...] = (
        ("categories", CATEGORIES, _read_category),
        ("ingredients", INGREDIENTS, _read_ingredient),
        ("tags", TAGS, _read_tag),
    )
    for key, place, read_item in lists:
        for number, item in enumerate(read_list(table, key, place.to_bitext(), report), 1):
            read_item(item, number, kept, report)
    report_unknown_keys(table, _TOP_KEYS, None, report)
    return Catalog(tuple(kept.categories), tuple(kept.ingredients), tuple(kept.tags))


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
          ``DUPLICATE_ZH_NAME`` or ``DUPLICATE_EN_NAME`` and is kept. An ingredient or a tag whose
          names match gives the same messages and is skipped. Each problem names the first
          earlier item with that key or name. Matching follows the rules of
          ``Catalog.find_ingredient``.
    """
    table = read_toml(folder, folder.catalog)
    if isinstance(table, Problem):
        return None, (table,)
    report = Report(folder.relative(folder.catalog))
    catalog = _read_lists(table, report)
    return catalog, tuple(report.problems)
