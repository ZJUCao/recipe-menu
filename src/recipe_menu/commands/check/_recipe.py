"""The check of one recipe, and the lines that show problems."""

from collections.abc import Iterable

from recipe_menu.app import problem_lines
from recipe_menu.catalog import read_catalog
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import Lang
from recipe_menu.recipes import is_recipe_id, read_recipe


def check_recipe(folder: DataFolder, recipe_id: str) -> tuple[Problem, ...]:
    """Checks one recipe as ``check`` checks it.

    It gives the errors of ``read_catalog``, then the problems of ``read_recipe`` with that
    catalog. It reads ``catalog.toml`` and ``recipes/<id>.toml`` once each, lists no folder, and
    writes nothing.

    Args:
        folder: The data folder.
        recipe_id: The ID of the recipe, such as ``garlic-broccoli``. It is an ID that
            ``list_recipe_ids`` gave, or the ID of a file that the caller has just created.

    Returns:
        The problems of the recipe, in order. The empty tuple means no problem.

    Raises:
        ValueError: ``is_recipe_id(recipe_id)`` is false. It is raised before any file is read.
    """
    if not is_recipe_id(recipe_id):
        raise ValueError(f"not a recipe ID: {recipe_id!r}")
    catalog, found = read_catalog(folder)
    errors = tuple(problem for problem in found if problem.severity is Severity.ERROR)
    return (*errors, *read_recipe(folder, catalog, recipe_id)[1])


def problem_block(problems: Iterable[Problem], lang: Lang) -> tuple[str, ...]:
    """Shows problems with the indents of the report of ``check``.

    Each problem gives two lines with no line break: two spaces and ``where``, then four spaces
    and ``what``, from ``problem_lines``.

    Args:
        problems: The problems to show, in their order.
        lang: The language of the lines.

    Returns:
        The lines of the problems, in order. No problems give the empty tuple.
    """
    lines: list[str] = []
    for problem in problems:
        where, what = problem_lines(problem, lang)
        lines.extend((f"  {where}", f"    {what}"))
    return tuple(lines)
