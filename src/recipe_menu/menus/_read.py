"""Listing the menu files of a data folder, and reading one week's file."""

from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.menus._model import WeekMenu
from recipe_menu.menus._week import IsoWeek
from recipe_menu.settings import Settings


def list_menu_weeks(folder: DataFolder) -> tuple[tuple[IsoWeek, ...], tuple[Problem, ...]]:
    """Lists the weeks that have a menu file in ``menus/``, from the file names.

    It lists ``menus/`` through ``list_toml_files``, reads no file, and writes nothing. The
    mock raises ``NotImplementedError``.

    Args:
        folder: The data folder.

    Returns:
        A pair ``(weeks, problems)``.

        A menu file is an entry of ``menus/`` whose name ends with ``.toml`` in small letters,
        as ``list_toml_files`` gives it. Every other entry gives no problem. An entry such as
        ``2026-W48.TOML`` is not a menu file either, and ``list_toml_files`` gives an error
        for it.

        ``weeks`` holds the week of each menu file whose name without ``.toml`` is read by
        ``IsoWeek.parse``, in the order of time, which is also the order of the names.

        ``problems`` holds the problems that ``list_toml_files`` gives, and then the error
        ``NOT_A_WEEK_NAME`` for each other menu file, in the order of the names, such as
        ``2026-w47.toml``, ``2026-W99.toml``, or ``plan.toml``. Each problem's file is its
        entry, relative to the data folder, and it has no place. A name with a problem is not
        in ``weeks``.

        When ``menus/`` is missing, is a file, or cannot be read, ``weeks`` is empty and
        ``problems`` holds only the one problem of ``list_toml_files``, with the file ``menus``.

        The implementation never raises for bad data.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError


def read_week_menu(
    folder: DataFolder,
    week: IsoWeek,
    settings: Settings | None,
    recipe_ids: frozenset[str],
) -> tuple[WeekMenu | None, tuple[Problem, ...]]:
    """Reads the menu file of one week into a ``WeekMenu``, and reports each problem.

    It reads ``menus/<week>.toml`` through ``read_toml``, lists no folder, and writes nothing.
    It checks the whole file and records a problem for each mistake, so one run lists every
    problem. Every problem is an error. A problem has its place when it has one: the key, the
    day, the meal, or the dish of the mistake. A missing ``week`` and an unknown top-level key
    have no place, a read error of ``read_toml`` has ``line N`` or none, and ``UNKNOWN_RECIPE``
    sits at the meal of the day. The mock raises ``NotImplementedError``.

    Args:
        folder: The data folder.
        week: The week of the file, such as ``2026-W47``. A week that ``list_menu_weeks`` gave.
        settings: The meals of each day and the servings of a dish that gives none, or ``None``
            when the settings could not be read. Then only the checks that do not depend on
            the settings are made, and every meal of ``Meal`` is accepted. With ``None``, a day
            key that names no meal gets ``UNKNOWN_KEY``. A meal that the settings do not name,
            written as ``breakfast = []``, gives no problem and is not in the menu.
        recipe_ids: The recipe IDs that a dish may name, as ``list_recipe_ids`` gave them.

    Returns:
        A pair ``(menu, problems)``. ``menu`` is ``None`` when ``settings`` is ``None``, or
        when ``problems`` holds an error. Otherwise it is a ``WeekMenu`` with the week
        ``week``, the meals ``settings.meals``, and one slot for each day and each of those
        meals. A day or a meal that the file lacks holds no dishes. A dish without servings
        gets ``settings.servings``. Each dish's ID loses the whitespace at both ends.

        ``problems`` holds the problem of ``read_toml`` alone when the file is missing, cannot
        be read, is not UTF-8, or is not valid TOML. Otherwise it holds the problems of the
        checks of the file, in this order: the problems of ``week``, then the days from Monday
        to Sunday, each with its keys in the file's order, then the other keys of the top of
        the file, in the file's order.

        The implementation never raises for bad data.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError
