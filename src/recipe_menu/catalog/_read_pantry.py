"""Reading ``pantry.toml`` into a pantry."""

from recipe_menu.catalog._catalog import Catalog
from recipe_menu.catalog._model import Pantry
from recipe_menu.datafile import DataFolder, Problem


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

    Raises:
        NotImplementedError: In the mock.
    """
    raise NotImplementedError
