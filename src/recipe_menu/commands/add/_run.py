"""The run function of the ``add`` command."""

from typing import cast

from recipe_menu.app import Arguments, Context, first_error, stop_at_error
from recipe_menu.catalog import Catalog, read_catalog
from recipe_menu.commands.add._file import recipe_text
from recipe_menu.commands.add._model import NewRecipe
from recipe_menu.commands.add._questions import ask_recipe
from recipe_menu.commands.add._report import report_check, report_failure
from recipe_menu.commands.add.messages import APPEARED
from recipe_menu.datafile import FileOutcome, create_file
from recipe_menu.recipes import list_recipe_ids


def _read_catalog(context: Context) -> Catalog | int:
    """Reads the catalog, and stops at its first error.

    Args:
        context: The data folder, the language, and the error stream.

    Returns:
        The catalog, or 1 after the first error went to ``context.err``.
    """
    catalog, problems = read_catalog(context.folder)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    # The catalog is None only after an error.
    return cast(Catalog, catalog)


def _read_ids(context: Context) -> frozenset[str] | int:
    """Lists ``recipes/``, and stops at the first error of the listing.

    Args:
        context: The data folder, the language, and the error stream.

    Returns:
        The recipe IDs, or 1 after the first error went to ``context.err``.
    """
    ids, problems = list_recipe_ids(context.folder)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    return frozenset(ids)


def _save(context: Context, recipe: NewRecipe) -> int:
    """Writes the file of the recipe, and checks it.

    Args:
        context: The streams, the language, and the data folder.
        recipe: The answers.

    Returns:
        The exit code of the save and the check.
    """
    path = context.folder.recipe_file(recipe.recipe_id)
    creation = create_file(context.folder, path, recipe_text(recipe))
    if creation.outcome is FileOutcome.CREATED:
        return report_check(context, recipe.recipe_id, path)
    if creation.outcome is FileOutcome.EXISTS:
        context.err.write(APPEARED.render(context.lang, file=str(creation.existing)) + "\n")
        return 1
    return report_failure(context, creation)


def run_add(context: Context, arguments: Arguments) -> int:
    """Asks the questions of ``add``, writes the new recipe file, and checks it.

    It reads the catalog and the listing of ``recipes/``, asks eight questions with the answers
    from ``context.input``, writes ``recipes/<id>.toml`` through ``create_file``, and checks the
    file with ``check_recipe``. It writes only to ``context.out`` and ``context.err``, and lets
    ``KeyboardInterrupt`` go on to ``cli``.

    Args:
        context: The language, the data folder, the settings, the streams, and the input stream.
            It uses neither ``context.today`` nor ``context.random``.
        arguments: What the command line gave. Empty, because ``add`` takes no argument.

    Returns:
        0 when the first answer is empty or the file is saved with no error in its check, and 1
        for an error in a data file, an input that ends early, a failed save, or an error in the
        check after saving.
    """
    catalog = _read_catalog(context)
    if isinstance(catalog, int):
        return catalog
    ids = _read_ids(context)
    if isinstance(ids, int):
        return ids
    recipe = ask_recipe(context, catalog, ids)
    return recipe if isinstance(recipe, int) else _save(context, recipe)
