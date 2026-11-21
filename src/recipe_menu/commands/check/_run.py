"""The run function of the ``check`` command."""

from recipe_menu.app import Arguments, Context, first_error
from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.commands.check._recipe import problem_block
from recipe_menu.commands.check.messages import (
    CHECKED,
    ERRORS_HEADING,
    FIX_AND_CHECK_AGAIN,
    NO_ERRORS,
    NO_ERRORS_OR_WARNINGS,
    RECIPE_COUNT,
    THE_CATALOG,
    THE_PANTRY,
    THE_SETTINGS,
    WARNINGS_HEADING,
    WEEK_MENU_COUNT,
)
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import Lang
from recipe_menu.menus import list_menu_weeks, read_week_menu
from recipe_menu.recipes import list_recipe_ids, read_recipe
from recipe_menu.settings import read_settings
from recipe_menu.text import Message, Plural, and_list


def _read_all(folder: DataFolder) -> tuple[int, int, list[Problem]]:
    """Reads every data file, in the seven steps of the design.

    Args:
        folder: The data folder.

    Returns:
        The number of recipe IDs, the number of weeks, and every problem in the order of the
        steps.
    """
    problems: list[Problem] = []
    settings, found = read_settings(folder)
    problems.extend(found)
    catalog, found = read_catalog(folder)
    problems.extend(found)
    problems.extend(read_pantry(folder, catalog)[1])
    ids, found = list_recipe_ids(folder)
    problems.extend(found)
    for recipe_id in ids:
        problems.extend(read_recipe(folder, catalog, recipe_id)[1])
    weeks, found = list_menu_weeks(folder)
    problems.extend(found)
    recipe_ids = frozenset(ids)
    for week in weeks:
        problems.extend(read_week_menu(folder, week, settings, recipe_ids)[1])
    return len(ids), len(weeks), problems


def _count_line(recipes: int, weeks: int, lang: Lang) -> str:
    """Writes the count line.

    Args:
        recipes: The number of recipe IDs.
        weeks: The number of weeks.
        lang: The language of the line.

    Returns:
        The line that names what ``check`` looked at.
    """
    files = and_list(
        [
            THE_SETTINGS.to_bitext(),
            THE_CATALOG.to_bitext(),
            THE_PANTRY.to_bitext(),
            RECIPE_COUNT.pick(recipes).to_bitext(count=recipes),
            WEEK_MENU_COUNT.pick(weeks).to_bitext(count=weeks),
        ]
    )
    return CHECKED.render(lang, files=files)


def _block(problems: list[Problem], heading: Plural, lang: Lang) -> list[str]:
    """Writes a heading and the two lines of each problem.

    Args:
        problems: The problems of the block, not empty.
        heading: The heading, picked by the number of problems.
        lang: The language of the lines.

    Returns:
        The lines of the block.
    """
    count = len(problems)
    return [heading.pick(count).render(lang, count=count), *problem_block(problems, lang)]


def _report_lines(recipes: int, weeks: int, problems: list[Problem], lang: Lang) -> list[str]:
    """Writes the lines of the report.

    Args:
        recipes: The number of recipe IDs.
        weeks: The number of weeks.
        problems: Every problem, in the order of the steps.
        lang: The language of the report.

    Returns:
        The lines of the report, without line breaks.
    """
    errors = [problem for problem in problems if problem.severity is Severity.ERROR]
    warnings = [problem for problem in problems if problem.severity is Severity.WARNING]
    lines = [_count_line(recipes, weeks, lang), ""]
    if errors:
        lines.extend(_block(errors, ERRORS_HEADING, lang))
    else:
        none: Message = NO_ERRORS if warnings else NO_ERRORS_OR_WARNINGS
        lines.append(none.render(lang))
    if warnings:
        lines.extend(["", *_block(warnings, WARNINGS_HEADING, lang)])
    if errors:
        lines.extend(["", FIX_AND_CHECK_AGAIN.render(lang)])
    return lines


def run_check(context: Context, arguments: Arguments) -> int:
    """Reads every data file and writes the report to ``context.out``.

    It reads the files in seven steps: the settings, the catalog, the pantry, the listing of
    ``recipes/``, each recipe, the listing of ``menus/``, and each week menu. It passes the
    settings that it read itself to the menus, and never ``context.settings``. The report goes to
    ``context.out`` once, after the last file.

    Args:
        context: The language, the data folder, and the output stream. It uses neither
            ``context.settings``, ``context.err``, nor ``context.today``.
        arguments: What the command line gave. Empty, because ``check`` takes no argument.

    Returns:
        1 when the report has an error, and 0 otherwise.
    """
    recipes, weeks, problems = _read_all(context.folder)
    lines = _report_lines(recipes, weeks, problems, context.lang)
    context.out.write("".join(f"{line}\n" for line in lines))
    return int(first_error(problems) is not None)
