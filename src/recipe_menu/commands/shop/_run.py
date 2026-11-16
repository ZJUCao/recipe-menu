r"""The run function of the ``shop`` command."""

from recipe_menu.app import Arguments, Context


def run_shop(context: Context, arguments: Arguments) -> int:
    r"""Makes the shopping list of a week, saves it as a Markdown file, and writes it.

    The mock reads no file, writes nothing, raises nothing, and gives 0.

    It turns the value of ``WEEK`` into a week with ``week_from_argument(value, context.today)``,
    where ``value`` is the value of the argument or ``None``, and raises
    ``UsageError(NOT_A_WEEK, None, week=value)`` for a result of ``None``, before it touches the
    disk or writes any output. It then reads the files in this order. First ``read_catalog``,
    then ``read_pantry(context.folder, catalog)``, then ``list_recipe_ids``, then
    ``list_menu_weeks``, whose first error stops it also when the error names another file. When
    the weeks lack the week, it writes ``NO_MENU`` with ``week=str(week)`` to ``context.err`` and
    gives 1. Then ``read_week_menu(context.folder, week, context.settings, frozenset(ids))``.
    Then ``read_recipe`` for each recipe ID that a dish names, once, in the order of the first
    dish that names it: Monday to Sunday, the meals in the order of ``menu.meals``, and the
    dishes in the file's order. The first error of each reader stops it through ``first_error``
    and ``stop_at_error``. No warning is written, and a warning changes nothing. It never reads
    a file in ``shopping/``, and it reads neither another menu nor a recipe that the menu does
    not name. It keeps the recipes in a dictionary for one run, with no module-level cache, and
    passes them to ``build_shopping_list(menu, recipes, catalog, pantry)``. A week with no dish,
    which is a list with ``dish_count`` 0, gives ``NO_DISHES`` with ``week=str(week)`` on
    ``context.out`` and the code 0, and it saves no file.

    Otherwise it builds the text of the file and calls
    ``replace_file(context.folder, path, text)`` once, with
    ``path = context.folder.shopping_file(str(week))``. The text is in the language of the run,
    in UTF-8 with each line ended by LF, the last one included, in these blocks with one empty
    line between two blocks: ``# `` and ``FILE_TITLE`` with ``week``; ``FILE_DATES`` with
    ``dates``, ``meals``, and ``dishes`` of ``LIST_HEADING``; for each group in its order, the
    line ``## `` and the category's name as a block of its own, and then the block of its
    lines, one line ``- [ ] `` for each ``ShoppingLine`` of the group, with the ingredient's
    name, a space, and ``amount_text``, or ``NOTHING_TO_BUY`` for a list with no group; and
    ``PANTRY_LINE`` when the menu uses a pantry ingredient. It writes the output only after the
    file, once. It writes only to ``context.out`` and ``context.err``. The implementation raises
    nothing for bad data or for a failure on the disk. ``week_from_argument`` passes on
    ``ValueError`` when the week ends after 31 December 9999 (no value or ``this`` from 27 to 31
    December 9999, or ``next`` from 20 to 24 December 9999), and ``OverflowError`` for ``next``
    from 25 December 9999.

    Args:
        context: The language, the data folder, the settings for ``read_week_menu``, the output
            and error streams, and today's date.
        arguments: What the command line gave. ``arguments.values`` is ``()`` or holds one value,
            the week. It has no options.

    Returns:
        0 when ``replace_file`` gave ``CREATED``, and also for a week with no dish. 1 for a week
        with no menu file, for the first error of a file, or when ``replace_file`` gave
        ``FAILED``. For a saved list, the output has four blocks with one empty line between two
        blocks. First ``LIST_HEADING`` with ``week=str(week)``, ``dates`` as ``week.date_range``,
        and ``meals`` and ``dishes`` as ``MEAL_COUNT`` and ``DISH_COUNT`` picked by
        ``meal_count`` and ``dish_count`` of the list, each with ``count`` set to that number.
        Then, for each group in its order, the line of the category's name and the lines of
        ``format_table(rows, indent=2, min_widths=(width,))``, where ``rows`` holds the
        ingredient's name and ``amount_text`` of each line and ``width`` is the largest
        ``display_width`` of a line of a name of the whole list, each name split by
        ``str.splitlines``, or ``NOTHING_TO_BUY`` for a list with no
        group. Then ``PANTRY_LINE`` with ``items`` as ``comma_list`` of the names of
        ``pantry_used``, in that order, only when one is used. Last ``SAVED`` with
        ``file=str(path)``. For an error, the error stream gets the three lines of
        ``stop_at_error``. For ``FAILED``, three lines go to ``context.err``, with nothing on
        ``context.out``: the full path ``str(context.folder.root / problem.file)``, then two
        spaces and the problem's text in ``context.lang``, then ``NO_FILE_SAVED`` when ``left``
        is empty and ``LEFT_BEHIND`` with ``file`` as the full path of the temporary file
        otherwise.

    Raises:
        UsageError: ``NOT_A_WEEK`` with no hint for a value that is not a week, before it
            touches the disk or writes any output.
        ValueError: Passed on from ``week_from_argument`` when the week ends after 31 December
            9999: no value or ``this`` from 27 to 31 December 9999, or ``next`` from 20 to 24
            December 9999.
        OverflowError: Passed on from ``week_from_argument`` for ``next`` from 25 December 9999.
    """
    return 0
