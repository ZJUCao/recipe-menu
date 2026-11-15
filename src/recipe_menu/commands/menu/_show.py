"""The reads of ``menu show`` and the lines of its table and count line."""

from typing import cast

from recipe_menu.app import Context, first_error, stop_at_error
from recipe_menu.catalog import Catalog, read_catalog
from recipe_menu.commands.menu.messages import (
    COUNT_LINE,
    DAY_HEADING,
    DISH_COUNT,
    MEAL_COUNT,
    MENU_HEADING,
    NO_DISHES,
)
from recipe_menu.datafile import Problem
from recipe_menu.menus import (
    NO_MENU,
    Day,
    IsoWeek,
    WeekMenu,
    list_menu_weeks,
    read_week_menu,
    short_date,
)
from recipe_menu.recipes import Recipe, list_recipe_ids, read_recipe
from recipe_menu.settings import Meal
from recipe_menu.text import format_table

# The symbol of an empty meal, U+2014, and the sign before the servings of a dish, U+00D7. They
# belong to no language, so they are not messages.
_DASH = "\u2014"
_TIMES = "\u00d7"


def read_week(context: Context, week: IsoWeek) -> tuple[WeekMenu, dict[str, Recipe]] | int:
    """Reads the files that ``menu show`` needs, each once, and stops at the first error.

    Args:
        context: The language, the data folder, the settings, and the error stream.
        week: The week to show.

    Returns:
        The menu and the recipes that its dishes name, by ID, in the order of the first dish
        that names each. Or the exit code 1 when a reader gave an error, after the three lines of
        ``stop_at_error``, or when the week has no menu, after ``NO_MENU`` on ``context.err``.
    """
    first = _read_before_menu(context, week)
    if isinstance(first, int):
        return first
    catalog, ids = first
    found, problems = read_week_menu(context.folder, week, context.settings, ids)
    code = _stop(context, problems)
    if code is not None:
        return code
    # The menu is None only after an error.
    menu = cast(WeekMenu, found)
    recipes: dict[str, Recipe] = {}
    for recipe_id in _recipe_ids(menu):
        recipe, problems = read_recipe(context.folder, catalog, recipe_id)
        code = _stop(context, problems)
        if code is not None:
            return code
        # The recipe is None only after an error.
        recipes[recipe_id] = cast(Recipe, recipe)
    return menu, recipes


def _read_before_menu(
    context: Context,
    week: IsoWeek,
) -> tuple[Catalog, frozenset[str]] | int:
    """Reads the catalog and the two listings, and looks for the week among the menus.

    Args:
        context: The language, the data folder, and the error stream.
        week: The week to show.

    Returns:
        The catalog and the recipe IDs, or the exit code 1 after the first error or after
        ``NO_MENU`` for a week that the listing of ``menus/`` lacks.
    """
    catalog, problems = read_catalog(context.folder)
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
    # The catalog is None only after an error.
    return cast(Catalog, catalog), frozenset(ids)


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


def _recipe_ids(menu: WeekMenu) -> tuple[str, ...]:
    """Finds the recipes that the dishes name, each once, in the order of its first dish.

    Args:
        menu: The week menu. Its slots go from Monday to Sunday, the meals in the order of the
            settings.

    Returns:
        The recipe IDs without repeats.
    """
    ids = (dish.recipe_id for slot in menu.slots for dish in slot.dishes)
    return tuple(dict.fromkeys(ids))


def menu_output(
    context: Context,
    week: IsoWeek,
    menu: WeekMenu,
    recipes: dict[str, Recipe],
) -> str:
    """Writes the whole output of ``menu show``.

    Args:
        context: The language.
        week: The week.
        menu: The menu of the week.
        recipes: The recipe of each ID that a dish names.

    Returns:
        The heading, an empty line, the table, an empty line, and the count line or
        ``NO_DISHES``, each line ended by a line break.
    """
    lang = context.lang
    heading = MENU_HEADING.render(lang, week=str(week), dates=week.date_range)
    table = format_table(_rows(context, week, menu, recipes))
    lines = [heading, "", *table, "", _count_line(context, menu)]
    return "".join(f"{line}\n" for line in lines)


def _rows(
    context: Context,
    week: IsoWeek,
    menu: WeekMenu,
    recipes: dict[str, Recipe],
) -> list[list[str]]:
    """Builds the rows of the table: the heading row and one row for each day.

    Args:
        context: The language.
        week: The week.
        menu: The menu of the week.
        recipes: The recipe of each ID that a dish names.

    Returns:
        The rows, each with the day and one cell for each meal of the menu.
    """
    lang = context.lang
    rows = [[DAY_HEADING.render(lang), *(meal.heading.get(lang) for meal in menu.meals)]]
    for day, date in zip(Day, week.dates, strict=True):
        cells = [_cell(context, menu, recipes, day, meal) for meal in menu.meals]
        rows.append([short_date(date).get(lang), *cells])
    return rows


def _cell(
    context: Context,
    menu: WeekMenu,
    recipes: dict[str, Recipe],
    day: Day,
    meal: Meal,
) -> str:
    """Writes the cell of one meal of one day.

    Args:
        context: The language.
        menu: The menu of the week.
        recipes: The recipe of each ID that a dish names.
        day: The day.
        meal: The meal, one of ``menu.meals``.

    Returns:
        The symbol U+2014 for a meal with no dish, else one line for each dish: the recipe's
        name, a space, the sign U+00D7, and the servings.
    """
    dishes = menu.dishes(day, meal)
    if not dishes:
        return _DASH
    lines = (f"{recipes[d.recipe_id].name.get(context.lang)} {_TIMES}{d.servings}" for d in dishes)
    return "\n".join(lines)


def _count_line(context: Context, menu: WeekMenu) -> str:
    """Writes the line under the table.

    Args:
        context: The language.
        menu: The menu of the week.

    Returns:
        ``COUNT_LINE`` with the number of meals that hold a dish and the number of dishes, or
        ``NO_DISHES`` when no meal holds a dish.
    """
    counts = [len(slot.dishes) for slot in menu.slots]
    meals, dishes = sum(1 for count in counts if count), sum(counts)
    if dishes == 0:
        return NO_DISHES.render(context.lang)
    return COUNT_LINE.render(
        context.lang,
        meals=MEAL_COUNT.pick(meals).to_bitext(count=meals),
        dishes=DISH_COUNT.pick(dishes).to_bitext(count=dishes),
    )
