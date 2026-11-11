"""Reading ``pantry.toml`` into a pantry."""

from recipe_menu.catalog._catalog import Catalog
from recipe_menu.catalog._model import Ingredient, Pantry
from recipe_menu.catalog._shape import Report, read_list, report_unknown_keys
from recipe_menu.catalog.messages import ITEM_N, PANTRY, UNKNOWN_INGREDIENT
from recipe_menu.datafile import EMPTY_ITEM, ITEM_NOT_A_TEXT, DataFolder, Problem, read_toml


def _read_item(
    item: object,
    number: int,
    catalog: Catalog | None,
    report: Report,
) -> Ingredient | None:
    """Reads one item of the pantry list.

    Args:
        item: The item, as the file gives it.
        number: The number of the item, counted from 1.
        catalog: The catalog that names come from, or ``None``.
        report: Where the problems go.

    Returns:
        The ingredient that the item names, or ``None`` when the item has a problem or when
        ``catalog`` is ``None``.
    """
    place = ITEM_N.to_bitext(number=number)
    if not isinstance(item, str):
        report.add(place, ITEM_NOT_A_TEXT)
        return None
    name = item.strip()
    if not name:
        report.add(place, EMPTY_ITEM)
        return None
    if catalog is None:
        return None
    ingredient = catalog.find_ingredient(name)
    if ingredient is None:
        report.add(place, UNKNOWN_INGREDIENT, name=name)
    return ingredient


def read_pantry(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[Pantry | None, tuple[Problem, ...]]:
    """Reads ``pantry.toml`` into a ``Pantry`` and reports each problem with its place.

    The file has one list of texts, ``pantry``. Each item names an ingredient of the catalog in
    either language, and ``Catalog.find_ingredient`` finds it. The file is read through
    ``read_toml``. The reader never raises for bad data.

    Args:
        folder: The data folder.
        catalog: The catalog that the names come from, or ``None`` when the catalog could not
            be read. Then only the form of the file is checked.

    Returns:
        A pair ``(pantry, problems)``.

        * ``pantry`` is ``None`` when ``read_toml`` gives a problem, or when ``catalog`` is
          ``None``. Otherwise it is a ``Pantry`` of the ingredient of every item that names
          one, even when ``problems`` is not empty. An ingredient that two items name is in the
          set once and gives no problem.
        * ``problems`` holds the problem of ``read_toml`` alone, or the problems of the checks
          below. Each has ``Severity.ERROR`` and the file ``pantry.toml``. They come in this
          order: the list, then each item in order, then the other keys at the top of the file.

        These rules decide the problems, with the places ``pantry`` and ``item N``, where N
        counts the items from 1, skipped items included:

        * A missing ``pantry`` gives ``MISSING_KEY`` with no place, and a value that is not a
          list gives ``NOT_A_LIST`` at ``pantry``. Either is read as an empty list.
        * An item that is not a text gives ``ITEM_NOT_A_TEXT``, and one that is empty or only
          whitespace gives ``EMPTY_ITEM``. Both are skipped.
        * When ``catalog`` is not ``None``, an item for which ``find_ingredient`` finds nothing
          gives ``UNKNOWN_INGREDIENT`` with the item without whitespace at both ends, and is
          skipped.
        * A key at the top of the file other than ``pantry`` gives ``UNKNOWN_KEY``, in its form
          for one key, with no place, and is ignored.

    """
    table = read_toml(folder, folder.pantry)
    if isinstance(table, Problem):
        return None, (table,)
    report = Report(folder.relative(folder.pantry))
    items = read_list(table, "pantry", PANTRY.to_bitext(), report)
    found = {_read_item(item, number, catalog, report) for number, item in enumerate(items, 1)}
    report_unknown_keys(table, ("pantry",), None, report)
    pantry = None if catalog is None else Pantry(frozenset(i for i in found if i is not None))
    return pantry, tuple(report.problems)
