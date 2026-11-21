"""The lines of ``add`` after the last answer: the check of the saved file, and a failed save."""

from pathlib import Path
from typing import cast

from recipe_menu.app import Context, problem_lines
from recipe_menu.commands.add._ask import write_line
from recipe_menu.commands.add.messages import (
    ERROR_COUNT,
    FIX_AND_CHECK,
    LEFT_BEHIND,
    NOTHING_SAVED,
    SAVED,
    SAVED_WITH_PROBLEMS,
    WARNING_COUNT,
)
from recipe_menu.commands.check import check_recipe, problem_block
from recipe_menu.datafile import FileCreation, Problem, Severity
from recipe_menu.lang import BiText
from recipe_menu.text import and_list


def _counts(errors: int, warnings: int) -> list[BiText]:
    """Writes the counts of problems for the line after saving, leaving out a count of 0.

    Args:
        errors: The number of errors.
        warnings: The number of warnings.

    Returns:
        The count of errors and the count of warnings, each as a ``BiText``.
    """
    counts: list[BiText] = []
    if errors:
        counts.append(ERROR_COUNT.pick(errors).to_bitext(count=errors))
    if warnings:
        counts.append(WARNING_COUNT.pick(warnings).to_bitext(count=warnings))
    return counts


def report_check(context: Context, recipe_id: str, path: Path) -> int:
    """Checks the saved file and writes the lines after saving.

    Args:
        context: The language, the data folder, and the output stream.
        recipe_id: The ID of the file that was just created.
        path: The full path of the file.

    Returns:
        1 when the check found an error, and 0 otherwise.
    """
    problems = check_recipe(context.folder, recipe_id)
    if not problems:
        write_line(context, SAVED.render(context.lang, file=str(path)))
        return 0
    errors = [problem for problem in problems if problem.severity is Severity.ERROR]
    warnings = [problem for problem in problems if problem.severity is Severity.WARNING]
    counts = and_list(_counts(len(errors), len(warnings)))
    header = SAVED_WITH_PROBLEMS.render(context.lang, file=str(path), problems=counts)
    lines = [header, *problem_block(errors, context.lang), *problem_block(warnings, context.lang)]
    if errors:
        lines.append(FIX_AND_CHECK.render(context.lang))
    context.out.write("".join(f"{line}\n" for line in lines))
    return int(bool(errors))


def report_failure(context: Context, creation: FileCreation) -> int:
    """Writes the three lines of a failed save to the error stream.

    Args:
        context: The language and the error stream.
        creation: The result of ``create_file``, with the outcome ``FAILED``.

    Returns:
        1.
    """
    where, what = problem_lines(cast(Problem, creation.problem), context.lang)
    last = (
        LEFT_BEHIND.render(context.lang, file=str(creation.left[0]))
        if creation.left
        else NOTHING_SAVED.render(context.lang)
    )
    context.err.write(f"{where}\n  {what}\n{last}\n")
    return 1
