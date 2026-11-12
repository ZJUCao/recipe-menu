"""Showing the problems of a data file, and stopping a command at the first error."""

from collections.abc import Iterable

from recipe_menu.app._context import Context
from recipe_menu.datafile import Problem
from recipe_menu.lang import Lang


def problem_lines(problem: Problem, lang: Lang) -> tuple[str, str]:
    r"""Gives the two lines of a problem, in the layout of the prototypes, with no indent.

    The mock raises ``NotImplementedError``. The implementation follows the rules below.

    Args:
        problem: The problem to show.
        lang: The language of the lines.

    Returns:
        The pair ``(where, what)``. ``where`` is ``str(problem.file)`` when the problem has no
        place, and otherwise ``FILE_AT_PLACE`` with the file as ``str(problem.file)`` and the
        place as a ``BiText``, rendered in ``lang``. On Windows that is
        ``recipes\mapo-tofu.toml, ingredient 3`` in English. ``what`` is ``problem.text(lang)``.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError


def first_error(problems: Iterable[Problem]) -> Problem | None:
    """Finds the first error among the problems of a reader.

    The mock raises ``NotImplementedError``. The implementation follows the rule below.

    Args:
        problems: The problems that a reader gave, in its order.

    Returns:
        The first problem with ``Severity.ERROR``, or ``None`` when there is none.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError


def stop_at_error(context: Context, error: Problem) -> int:
    """Ends a command at the first error in a data file.

    The mock raises ``NotImplementedError``. The implementation follows the rules below.

    Args:
        context: The language and the error stream.
        error: The error that stops the command. It has ``Severity.ERROR``.

    Returns:
        1, the exit code of a command that an error in a data file stopped. It writes three
        lines to ``context.err``, all in ``context.lang``: ``where`` of ``problem_lines``, then
        two spaces and ``what`` of ``problem_lines``, and then ``RUN_CHECK``.

    Raises:
        ValueError: ``error`` has ``Severity.WARNING``. It is raised before anything is written.
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError
