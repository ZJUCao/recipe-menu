"""The reads of ``menu suggest``: the files up to the week's menu, and the candidate recipes."""

from dataclasses import dataclass
from typing import cast

from recipe_menu.app import Context, first_error, stop_at_error
from recipe_menu.catalog import Catalog, Tag, read_catalog
from recipe_menu.commands.suggest.messages import NO_TAGS, UNKNOWN_TAG
from recipe_menu.datafile import Problem
from recipe_menu.menus import NO_MENU, IsoWeek, WeekMenu, list_menu_weeks, read_week_menu
from recipe_menu.recipes import Recipe, list_recipe_ids, read_recipe
from recipe_menu.text import and_list


@dataclass(frozen=True, slots=True)
class MenuFiles:
    """What ``menu suggest`` knows after it read the week's menu.

    Attributes:
        catalog: The catalog.
        tag: The tag of ``--tag``, or ``None`` when the line gives none.
        ids: The recipe IDs, in the order of the listing.
        menu: The week's menu.
    """

    catalog: Catalog
    tag: Tag | None
    ids: tuple[str, ...]
    menu: WeekMenu


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


def _unknown_tag(context: Context, catalog: Catalog, value: str) -> int:
    """Writes the error for a tag that the catalog lacks.

    Args:
        context: The language and the error stream.
        catalog: The catalog, whose tags the message lists in the catalog's order.
        value: The value of ``--tag`` as typed.

    Returns:
        1, after one line went to ``context.err``.
    """
    count = len(catalog.tags)
    if count == 0:
        text = NO_TAGS.render(context.lang, value=value)
    else:
        tags = and_list(tag.name for tag in catalog.tags)
        text = UNKNOWN_TAG.pick(count).render(context.lang, value=value, tags=tags)
    context.err.write(f"{text}\n")
    return 1


def _find_tag(context: Context, catalog: Catalog, value: str | None) -> Tag | int | None:
    """Finds the tag of ``--tag``.

    Args:
        context: The language and the error stream.
        catalog: The catalog.
        value: The value of ``--tag``, or ``None``.

    Returns:
        ``None`` when there is no ``--tag``, the tag when the catalog has it, and otherwise the
        exit code 1 after the error line.
    """
    if value is None:
        return None
    tag = catalog.find_tag(value)
    return _unknown_tag(context, catalog, value) if tag is None else tag


def _list_week(context: Context, week: IsoWeek) -> tuple[str, ...] | int:
    """Lists the recipes and the menus, and looks for the week.

    Args:
        context: The language, the data folder, and the error stream.
        week: The week.

    Returns:
        The recipe IDs, or the exit code 1 after the first error or after ``NO_MENU`` for a
        week that the listing of ``menus/`` lacks.
    """
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
    return tuple(ids)


def read_menu_files(context: Context, week: IsoWeek, value: str | None) -> MenuFiles | int:
    """Reads the catalog, the tag, the two listings, and the week's menu, and stops at an error.

    Args:
        context: The language, the data folder, the settings, and the error stream.
        week: The week.
        value: The value of ``--tag``, or ``None``.

    Returns:
        The files, or the exit code 1 after the first error, an unknown tag, or ``NO_MENU``.
    """
    found, problems = read_catalog(context.folder)
    code = _stop(context, problems)
    if code is not None:
        return code
    # The catalog is None only after an error.
    catalog = cast(Catalog, found)
    tag = _find_tag(context, catalog, value)
    if isinstance(tag, int):
        return tag
    ids = _list_week(context, week)
    if isinstance(ids, int):
        return ids
    menu, problems = read_week_menu(context.folder, week, context.settings, frozenset(ids))
    code = _stop(context, problems)
    if code is not None:
        return code
    # The menu is None only after an error.
    return MenuFiles(catalog, tag, ids, cast(WeekMenu, menu))


def read_candidates(context: Context, files: MenuFiles) -> tuple[str, ...] | int:
    """Reads each recipe that the week does not hold, and keeps the IDs that can be chosen.

    Args:
        context: The language, the data folder, and the error stream.
        files: What was read up to the menu.

    Returns:
        The IDs, in the order of the listing, that no dish of the week names, whose recipe reads
        with no error, and that have the tag when ``--tag`` is given. Or the exit code 1 after
        the first error.
    """
    named = {dish.recipe_id for slot in files.menu.slots for dish in slot.dishes}
    candidates: list[str] = []
    for recipe_id in files.ids:
        if recipe_id in named:
            continue
        recipe, problems = read_recipe(context.folder, files.catalog, recipe_id)
        code = _stop(context, problems)
        if code is not None:
            return code
        # The recipe is None only after an error.
        if files.tag is None or files.tag in cast(Recipe, recipe).tags:
            candidates.append(recipe_id)
    return tuple(candidates)
