"""The run function of the ``add`` command."""

from recipe_menu.app import Arguments, Context


def run_add(context: Context, arguments: Arguments) -> int:
    """Asks the questions of ``add``, writes the new recipe file, and checks it.

    It reads the catalog and the listing of ``recipes/``, asks eight questions with the answers
    from ``context.input``, writes ``recipes/<id>.toml`` through ``create_file``, and checks the
    file with ``check_recipe``. It writes only to ``context.out`` and ``context.err``, and lets
    ``KeyboardInterrupt`` go on to ``cli``. The mock reads no file, reads no answer, writes
    nothing, and gives 0.

    Args:
        context: The language, the data folder, the settings, the streams, and the input stream.
            It uses neither ``context.today`` nor ``context.random``.
        arguments: What the command line gave. Empty, because ``add`` takes no argument.

    Returns:
        0 when the first answer is empty or the file is saved with no error in its check, and 1
        for an error in a data file, an input that ends early, a failed save, or an error in the
        check after saving.
    """
    return 0
