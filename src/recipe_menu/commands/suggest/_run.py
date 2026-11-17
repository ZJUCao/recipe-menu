"""The run function of the ``menu suggest`` command."""

from recipe_menu.app import Arguments, Context


def run_menu_suggest(context: Context, arguments: Arguments) -> int:
    """Fills the empty meals of the week's menu file with recipes chosen at random.

    It turns the value of ``WEEK`` into a week, reads the catalog, the listings, the week's menu
    and its text, and the recipes that the week does not hold, chooses recipes with one call of
    ``context.random.sample``, changes the menu file through ``replace_file``, and writes its
    output. It writes only to ``context.out`` and ``context.err``. The mock reads no file,
    writes nothing, raises nothing, and gives 0.

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
    return 0
