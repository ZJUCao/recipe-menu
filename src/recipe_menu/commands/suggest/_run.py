"""The run function of the ``menu suggest`` command."""

from pathlib import Path
from typing import cast

from recipe_menu.app import Arguments, Context, UsageError, stop_at_error
from recipe_menu.commands.suggest._choose import Fill, distribute, draw
from recipe_menu.commands.suggest._edit import Places, find_places, new_text, passes_check
from recipe_menu.commands.suggest._output import (
    Counts,
    cannot_fill,
    failure_output,
    fill_output,
    no_empty_meal,
)
from recipe_menu.commands.suggest._read import MenuFiles, read_candidates, read_menu_files
from recipe_menu.datafile import FileOutcome, Problem, read_file_text, replace_file
from recipe_menu.menus import NOT_A_WEEK, IsoWeek, MealSlot, week_from_argument


def run_menu_suggest(context: Context, arguments: Arguments) -> int:
    """Fills the empty meals of the week's menu file with recipes chosen at random.

    It turns the value of ``WEEK`` into a week, reads the catalog, the listings, the week's menu
    and its text, and the recipes that the week does not hold, chooses recipes with one call of
    ``context.random.sample``, changes the menu file through ``replace_file``, and writes its
    output. It writes only to ``context.out`` and ``context.err``.

    Args:
        context: The language, the data folder, the settings, the output and error streams,
            today's date, and the random generator.
        arguments: What the command line gave. ``arguments.values`` is ``()`` or holds one value,
            the week. ``arguments.option("--tag")`` is the tag, or ``None``.

    Returns:
        0 when the command filled meals, filled none, or found no empty meal, and 1 for an
        unknown tag, a week with no menu file, an error in a file, a file that it cannot fill,
        or a failed save.

    Raises:
        UsageError: ``NOT_A_WEEK`` with no hint for a value that is not a week, before it
            touches the disk or writes any output.
    """
    value = arguments.values[0] if arguments.values else None
    week = week_from_argument(value, context.today)
    if week is None:
        # Only a value that is given can fail, so it is a str here.
        raise UsageError(NOT_A_WEEK, None, week=cast(str, value))
    files = read_menu_files(context, week, arguments.option("--tag"))
    if isinstance(files, int):
        return files
    return _suggest(context, week, files)


def _suggest(context: Context, week: IsoWeek, files: MenuFiles) -> int:
    """Reads the text and the recipes, chooses, and saves the new text.

    Args:
        context: The language, the data folder, the settings, the streams, and the generator.
        week: The week.
        files: What was read up to the menu.

    Returns:
        The exit code of ``run_menu_suggest``.
    """
    path = context.folder.menu_file(str(week))
    empties = tuple(slot for slot in files.menu.slots if not slot.dishes)
    if not empties:
        context.out.write(no_empty_meal(context, week, path))
        return 0
    text = read_file_text(context.folder, path)
    if isinstance(text, Problem):
        return stop_at_error(context, text)
    text = text.replace("\r\n", "\n")
    places = find_places(text, empties)
    if places is None:
        context.err.write(cannot_fill(context, path))
        return 1
    candidates = read_candidates(context, files)
    if isinstance(candidates, int):
        return candidates
    chosen = draw(context, candidates, empties)
    fills = distribute(context, empties, chosen)
    if fills:
        code = _save(context, path, text, fills, places)
        if code != 0:
            return code
    counts = _counts(files, empties, fills, len(chosen))
    context.out.write(fill_output(context, week, path, files.tag, counts))
    return 0


def _save(context: Context, path: Path, text: str, fills: list[Fill], places: Places) -> int:
    """Builds the new text, checks it, and saves it with ``replace_file``.

    Args:
        context: The language, the data folder, and the error stream.
        path: The menu file.
        text: The old text, with LF line ends.
        fills: The meals that get dishes.
        places: The place of each empty meal.

    Returns:
        0 after the save, and 1 after the lines of a refusal or of a failure.
    """
    changed = new_text(text, fills, places)
    if not passes_check(text, changed, fills):
        context.err.write(cannot_fill(context, path))
        return 1
    creation = replace_file(context.folder, path, changed)
    if creation.outcome is not FileOutcome.CREATED:
        context.err.write(failure_output(context, creation))
        return 1
    return 0


def _counts(
    files: MenuFiles, empties: tuple[MealSlot, ...], fills: list[Fill], chosen: int
) -> Counts:
    """Counts the meals for the output.

    Args:
        files: What was read up to the menu.
        empties: The empty meals.
        fills: The meals that got dishes.
        chosen: The number of recipes that were drawn.

    Returns:
        The numbers that the output reports.
    """
    used = sum(len(fill.ids) for fill in fills)
    kept = len(files.menu.slots) - len(empties)
    return Counts(len(empties), len(fills), kept, used < chosen)
