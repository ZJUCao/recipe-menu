"""The reads of ``shop``: the files of a week menu and its recipes, and the stop at an error."""

from typing import cast

from recipe_menu.app import Context, first_error, stop_at_error
from recipe_menu.catalog import Catalog, Pantry, read_catalog, read_pantry
from recipe_menu.datafile import Problem
from recipe_menu.menus import NO_MENU, IsoWeek, WeekMenu, list_menu_weeks, read_week_menu
from recipe_menu.recipes import Recipe, list_recipe_ids, read_recipe

type WeekFiles = tuple[WeekMenu, dict[str, Recipe], Catalog, Pantry]


def read_week_files(context: Context, week: IsoWeek) -> WeekFiles | int:
    """Reads the files that ``shop`` needs, each once, and stops at the first error.

    Args:
        context: The language, the data folder, the settings, and the error stream.
        week: The week to shop for.

    Returns:
        The menu, the recipes that its dishes name by ID in the order of the first dish that
        names each, the catalog, and the pantry. Or the exit code 1 when a reader gave an error,
        after the three lines of ``stop_at_error``, or when the week has no menu, after
        ``NO_MENU`` on ``context.err``.
    """
    first = _read_before_menu(context, week)
    if isinstance(first, int):
        return first
    catalog, pantry, ids = first
    found, problems = read_week_menu(context.folder, week, context.settings, ids)
    code = _stop(context, problems)
    if code is not None:
        return code
    # The menu is None only after an error.
    menu = cast(WeekMenu, found)
    recipes = _read_recipes(context, catalog, menu)
    if isinstance(recipes, int):
        return recipes
    return menu, recipes, catalog, pantry


def _read_before_menu(
    context: Context,
    week: IsoWeek,
) -> tuple[Catalog, Pantry, frozenset[str]] | int:
    """Reads the catalog, the pantry, and the two listings, and looks for the week.

    Args:
        context: The language, the data folder, and the error stream.
        week: The week to shop for.

    Returns:
        The catalog, the pantry, and the recipe IDs, or the exit code 1 after the first error or
        after ``NO_MENU`` for a week that the listing of ``menus/`` lacks.
    """
    catalog, problems = read_catalog(context.folder)
    code = _stop(context, problems)
    if code is not None:
        return code
    pantry, problems = read_pantry(context.folder, catalog)
    code = _stop(context, problems)
    if code is not None:
        return code
    ids, problems = list_recipe_ids(context.folder)
    code = _stop(context, problems)
    if code is not None:
        return code
    weeks, problems = list_menu_weeks(context.folder)
    code = _stop(context, problems)
    if code is not None:
        return code
    if week not in weeks:
        context.err.write(f"{NO_MENU.render(context.lang, week=str(week))}\n")
        return 1
    # The catalog and the pantry are None only after an error.
    return cast(Catalog, catalog), cast(Pantry, pantry), frozenset(ids)


def _read_recipes(context: Context, catalog: Catalog, menu: WeekMenu) -> dict[str, Recipe] | int:
    """Reads each recipe that a dish names, once, in the order of its first dish.

    Args:
        context: The language, the data folder, and the error stream.
        catalog: The catalog.
        menu: The week menu.

    Returns:
        The recipes by ID, or the exit code 1 after the first error.
    """
    recipes: dict[str, Recipe] = {}
    for recipe_id in dict.fromkeys(dish.recipe_id for slot in menu.slots for dish in slot.dishes):
        recipe, problems = read_recipe(context.folder, catalog, recipe_id)
        code = _stop(context, problems)
        if code is not None:
            return code
        # The recipe is None only after an error.
        recipes[recipe_id] = cast(Recipe, recipe)
    return recipes


def _stop(context: Context, problems: tuple[Problem, ...]) -> int | None:
    """Stops the command at the first error among the problems of a reader.

    Args:
        context: The language and the error stream.
        problems: The problems that a reader gave.

    Returns:
        The exit code of ``stop_at_error`` when the problems hold an error, else ``None``.
    """
    error = first_error(problems)
    return None if error is None else stop_at_error(context, error)
