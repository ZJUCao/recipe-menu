"""The run function of the ``check`` command."""

from recipe_menu.app import Arguments, Context


def run_check(context: Context, arguments: Arguments) -> int:
    """Reads every data file and writes the report to ``context.out``.

    The mock raises ``NotImplementedError``.

    Args:
        context: The language, the data folder, and the output stream. It uses neither
            ``context.settings``, ``context.err``, nor ``context.today``.
        arguments: What the command line gave. Empty, because ``check`` takes no argument.

    Returns:
        1 when the report has an error, and 0 otherwise.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError
