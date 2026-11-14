"""What ``list`` and ``show`` share: reading the catalog and stopping at its first error."""

from typing import cast

from recipe_menu.app import Context, first_error, stop_at_error
from recipe_menu.catalog import Catalog, read_catalog


def read_catalog_or_stop(context: Context) -> Catalog | int:
    """Reads the catalog, and stops at its first error.

    Args:
        context: The data folder, the language, and the error stream.

    Returns:
        The catalog when it has no error. Otherwise 1, after ``stop_at_error`` wrote the first
        error to ``context.err``. Warnings change nothing.
    """
    catalog, problems = read_catalog(context.folder)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    # The catalog is None only after an error.
    return cast(Catalog, catalog)
