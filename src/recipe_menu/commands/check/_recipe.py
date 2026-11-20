"""The check of one recipe, and the lines that show problems."""

from collections.abc import Iterable

from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import Lang


def check_recipe(folder: DataFolder, recipe_id: str) -> tuple[Problem, ...]:
    """Checks one recipe as ``check`` checks it.

    It gives the errors of ``read_catalog``, then the problems of ``read_recipe`` with that
    catalog. The mock reads no file and gives ``()``.

    Args:
        folder: The data folder.
        recipe_id: The ID of the recipe, such as ``garlic-broccoli``.

    Returns:
        The problems of the recipe, in order. The empty tuple means no problem.

    Raises:
        ValueError: ``is_recipe_id(recipe_id)`` is false. The mock does not raise it.
    """
    return ()


def problem_block(problems: Iterable[Problem], lang: Lang) -> tuple[str, ...]:
    """Shows problems with the indents of the report of ``check``.

    Each problem gives two lines with no line break: two spaces and ``where``, then four spaces
    and ``what``, from ``problem_lines``. The mock gives ``()``.

    Args:
        problems: The problems to show, in their order.
        lang: The language of the lines.

    Returns:
        The lines of the problems, in order. No problems give the empty tuple.
    """
    return ()
