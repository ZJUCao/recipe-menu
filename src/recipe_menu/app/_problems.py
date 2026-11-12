"""Showing the problems of a data file, and stopping a command at the first error."""

from collections.abc import Iterable

from recipe_menu.app._context import Context
from recipe_menu.app.messages import FILE_AT_PLACE
from recipe_menu.datafile import Problem, Severity
from recipe_menu.lang import Lang
from recipe_menu.text import RUN_CHECK


def problem_lines(problem: Problem, lang: Lang) -> tuple[str, str]:
    r"""Gives the two lines of a problem, in the layout of the prototypes, with no indent.

    Args:
        problem: The problem to show.
        lang: The language of the lines.

    Returns:
        The pair ``(where, what)``. ``where`` is ``str(problem.file)`` when the problem has no
        place, and otherwise ``FILE_AT_PLACE`` with the file as ``str(problem.file)`` and the
        place as a ``BiText``, rendered in ``lang``. On Windows that is
        ``recipes\mapo-tofu.toml, ingredient 3`` in English. ``what`` is ``problem.text(lang)``.
    """
    if problem.place is None:
        where = str(problem.file)
    else:
        where = FILE_AT_PLACE.render(lang, file=str(problem.file), place=problem.place)
    return where, problem.text(lang)


def first_error(problems: Iterable[Problem]) -> Problem | None:
    """Finds the first error among the problems of a reader.

    Args:
        problems: The problems that a reader gave, in its order.

    Returns:
        The first problem with ``Severity.ERROR``, or ``None`` when there is none.
    """
    return next((problem for problem in problems if problem.severity is Severity.ERROR), None)


def stop_at_error(context: Context, error: Problem) -> int:
    """Ends a command at the first error in a data file.

    Args:
        context: The language and the error stream.
        error: The error that stops the command. It has ``Severity.ERROR``.

    Returns:
        1, the exit code of a command that an error in a data file stopped. It writes three
        lines to ``context.err``, all in ``context.lang``: ``where`` of ``problem_lines``, then
        two spaces and ``what`` of ``problem_lines``, and then ``RUN_CHECK``.

    Raises:
        ValueError: ``error`` has ``Severity.WARNING``. It is raised before anything is written.
    """
    if error.severity is not Severity.ERROR:
        raise ValueError("stop_at_error needs an error, not a warning")
    where, what = problem_lines(error, context.lang)
    context.err.write(f"{where}\n  {what}\n{RUN_CHECK.render(context.lang)}\n")
    return 1
