"""The text of a new menu file and the lines that ``menu new`` writes for each outcome."""

from pathlib import Path
from typing import cast

from recipe_menu.app import Context
from recipe_menu.commands.menu.messages import (
    ALREADY_EXISTS,
    CHANGED_NOTHING,
    CREATED,
    EMPTY_DAYS,
    LEFT_BEHIND,
    NEXT_STEP,
)
from recipe_menu.datafile import FileCreation, FileOutcome, Problem
from recipe_menu.lang import Lang
from recipe_menu.menus import Day, IsoWeek
from recipe_menu.settings import Meal
from recipe_menu.text import and_list

# The two comment lines that show the two forms of a dish, the same in both languages.
_DISH_COMMENTS = (
    '# A dish is a recipe ID, such as "tomato-egg",',
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
)


def menu_text(week: IsoWeek, meals: tuple[Meal, ...]) -> str:
    """Builds the text of the new menu file of a week, with every day and meal empty.

    Args:
        week: The week of the menu.
        meals: The meals of each day, in the order of ``Meal``.

    Returns:
        The lines of the file, each ended by LF, with only ASCII characters: the comment with the
        week and its dates in English, the two comments of the forms of a dish, the line
        ``week = "<week>"``, and then for each day an empty line, ``[<day>]``, and
        ``<meal> = []`` for each meal. The text is the same in both languages.
    """
    lines = [f"# {week}: {week.date_range.get(Lang.EN)}", *_DISH_COMMENTS, f'week = "{week}"']
    for day in Day:
        lines += ["", f"[{day.value}]", *(f"{meal.value} = []" for meal in meals)]
    return "".join(f"{line}\n" for line in lines)


def report_creation(context: Context, week: IsoWeek, path: Path, creation: FileCreation) -> int:
    """Writes the lines of the outcome of ``create_file`` and gives the exit code.

    Args:
        context: The language, the data folder, the settings for the meals, and the streams.
        week: The week of the menu.
        path: The file that ``create_file`` was asked to create.
        creation: What ``create_file`` gave.

    Returns:
        0 for ``CREATED``, with the three lines of a new menu on ``context.out``. 1 for ``EXISTS``,
        with ``ALREADY_EXISTS`` on ``context.err``, and 1 for ``FAILED``, with the three lines of
        a failure on ``context.err``.
    """
    if creation.outcome is FileOutcome.CREATED:
        context.out.write(_created_lines(context, week, path))
        return 0
    if creation.outcome is FileOutcome.EXISTS:
        text = ALREADY_EXISTS.render(context.lang, file=str(creation.existing))
        context.err.write(f"{text}\n")
        return 1
    # FAILED always holds a problem.
    problem = cast(Problem, creation.problem)
    context.err.write(_failure_lines(context, week, problem, creation.left))
    return 1


def _created_lines(context: Context, week: IsoWeek, path: Path) -> str:
    """Writes the three lines of a new menu.

    Args:
        context: The language and the settings for the meals.
        week: The week of the menu.
        path: The new file.

    Returns:
        ``CREATED``, ``EMPTY_DAYS``, and ``NEXT_STEP``, each ended by a line break.
    """
    meals = and_list(meal.label for meal in context.settings.meals)
    lines = (
        CREATED.render(context.lang, file=str(path), dates=week.date_range),
        EMPTY_DAYS.render(context.lang, meals=meals),
        NEXT_STEP.render(context.lang),
    )
    return "".join(f"{line}\n" for line in lines)


def _failure_lines(
    context: Context,
    week: IsoWeek,
    problem: Problem,
    left: tuple[Path, ...],
) -> str:
    """Writes the three lines of a failure.

    Args:
        context: The language and the data folder.
        week: The week of the menu.
        problem: What stopped ``create_file``.
        left: The file that could not be removed, or empty.

    Returns:
        The full path of the problem's file, two spaces and the problem, and then
        ``CHANGED_NOTHING`` or, for a file that was left, ``LEFT_BEHIND``, each ended by a line
        break.
    """
    if left:
        last = LEFT_BEHIND.render(context.lang, week=str(week))
    else:
        last = CHANGED_NOTHING.render(context.lang)
    lines = (str(context.folder.root / problem.file), f"  {problem.text(context.lang)}", last)
    return "".join(f"{line}\n" for line in lines)
