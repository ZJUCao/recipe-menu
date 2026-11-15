r"""The run functions of the ``menu new`` and ``menu show`` commands."""

from recipe_menu.app import Arguments, Context


def run_menu_new(context: Context, arguments: Arguments) -> int:
    r"""Creates the week's menu file with every day and meal empty, and writes the result.

    The mock reads no file, writes nothing, and gives 0.

    The implementation turns the value of ``WEEK`` into a week with
    ``week_from_argument(value, context.today)``, where ``value`` is the value of the argument or
    ``None``, and raises ``UsageError(NOT_A_WEEK, None, week=value)`` for a result of ``None``,
    before it touches the disk or writes any output. It builds the text of the file and calls
    ``create_file(context.folder, path, text)`` once, with
    ``path = context.folder.menu_file(str(week))``. It reads no data file, so a mistake in
    another file does not stop it. It writes only to ``context.out`` and ``context.err``, and
    raises no other exception, and none for bad data or for a failure on the disk.

    The text of the file is these lines, each ended by LF, with only ASCII characters and the
    same bytes in both languages: the comment ``# {week}: {dates}`` with ``str(week)`` and
    ``week.date_range.get(Lang.EN)``, two comments in English that show the two forms of a dish
    (a recipe ID such as ``"tomato-egg"``, and a recipe ID with servings such as
    ``{ recipe = "tomato-egg", servings = 4 }``), the line ``week = "{week}"`` with
    ``str(week)``, and then, for each day of ``Day`` from Monday to Sunday, an empty line, the
    line ``[{day}]`` with the day's value, and the line ``{meal} = []`` with the value of each
    meal of ``context.settings.meals``, in the order of ``Meal``.

    Args:
        context: The language, the data folder, the settings for the meals, the output and error
            streams, and today's date.
        arguments: What the command line gave. ``arguments.values`` is ``()`` or holds one value,
            the week. It has no options.

    Returns:
        0 when ``create_file`` gave ``CREATED``, and 1 for a refusal or a failure. A new menu
        writes three lines to ``context.out``: ``CREATED`` with ``file=str(path)`` and
        ``dates=week.date_range``, ``EMPTY_DAYS`` with ``meals`` set to ``and_list`` of the
        ``Meal.label`` of each meal of ``context.settings.meals``, and ``NEXT_STEP``. For
        ``EXISTS``, ``ALREADY_EXISTS`` with ``file=str(creation.existing)``, the entry that is
        there, goes to ``context.err`` and the code is 1, and nothing goes to ``context.out``.
        For ``FAILED``, three lines go to ``context.err``, with code 1 and nothing on
        ``context.out`` (ADR-0010): the full path of the problem's file,
        ``str(context.folder.root / problem.file)``, then two spaces and the problem's text in
        ``context.lang``, then ``CHANGED_NOTHING`` when ``left`` is empty and ``LEFT_BEHIND``
        with ``week=str(week)`` otherwise.

    Raises:
        UsageError: The implementation raises it with ``NOT_A_WEEK`` and no hint for a value that
            is not a week, before it touches the disk or writes any output.
    """
    return 0


def run_menu_show(context: Context, arguments: Arguments) -> int:
    r"""Shows a week menu as a table of days and meals on ``context.out``.

    The mock reads no file, writes nothing, and gives 0.

    The implementation turns the value of ``WEEK`` into a week with
    ``week_from_argument(value, context.today)`` and raises
    ``UsageError(NOT_A_WEEK, None, week=value)`` for a result of ``None``, before it reads a file
    or writes any output. It then reads the files in this order. First ``read_catalog``, then
    ``list_recipe_ids``, then ``list_menu_weeks``, whose first error stops it also when the error
    names another file. When the weeks lack the week, it writes ``NO_MENU`` with ``week=str(week)``
    to ``context.err`` and gives 1. Then ``read_week_menu(context.folder, week,
    context.settings, frozenset(ids))``. Then ``read_recipe`` for each recipe ID that a dish
    names, once, in the order of the first dish that names it: Monday to Sunday, the meals in the
    order of ``menu.meals``, and the dishes in the file's order. The first error of each reader
    stops it through ``first_error`` and ``stop_at_error``. No warning is written, and a warning
    changes nothing. It keeps the recipes that it read in a dictionary for one run, with no
    module-level cache, and writes its output once, after the last file. It writes no file, reads
    neither the pantry, another menu, nor a recipe that the menu does not name, and raises no
    other exception, and none for bad data.

    Args:
        context: The language, the data folder, the settings for ``read_week_menu``, the output
            and error streams, and today's date.
        arguments: What the command line gave. ``arguments.values`` is ``()`` or holds one value,
            the week. It has no options.

    Returns:
        0 when the command wrote the week, also a week with no dish, and 1 for a week with no
        menu file or for the first error of a file. For an error, the error stream gets the three
        lines of ``stop_at_error``, and nothing goes to the output stream. The output is these
        lines: ``MENU_HEADING`` with ``week=str(week)`` and ``dates=week.date_range``, an empty
        line, the lines of ``format_table(rows)`` with no indent, the default gap, and no
        ``min_widths``, an empty line, and ``COUNT_LINE``, or ``NO_DISHES`` when no slot of the
        menu holds a dish. ``rows`` is the heading row, with ``DAY_HEADING`` and the
        ``Meal.heading`` of each meal of ``menu.meals``, and then one row for each day of ``Day``
        from Monday to Sunday. Its first cell is ``short_date`` of the day's date in
        ``context.lang``. A meal's cell is the symbol U+2014 for a meal with
        no dish, and otherwise one line for each dish in the file's order, joined by ``\n``, as
        ``f"{name} {times}{dish.servings}"``, with ``times`` the symbol U+00D7 and ``name`` as
        ``recipe.name.get(context.lang)``.
        The same dish twice in one meal gives two lines, and both count. ``COUNT_LINE`` has
        ``meals`` as ``MEAL_COUNT`` picked by the number of slots that hold at least one dish,
        and ``dishes`` as ``DISH_COUNT`` picked by the number of dishes in all the slots, each
        with ``count`` set to that number.

    Raises:
        UsageError: The implementation raises it with ``NOT_A_WEEK`` and no hint for a value that
            is not a week, before it reads a file or writes any output.
    """
    return 0
