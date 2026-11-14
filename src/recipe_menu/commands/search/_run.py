"""The run function of the ``search`` command."""

from recipe_menu.app import Arguments, Context


def run_search(context: Context, arguments: Arguments) -> int:
    """Finds the recipes that match every word and writes them as a table on ``context.out``.

    The mock reads no file, writes nothing, raises nothing, and gives 0.

    The implementation checks every word first, in order, with ``matching_form``, before it reads
    a file. Then it reads the catalog with ``read_catalog``, and then every recipe with
    ``read_recipes`` (no separate ``list_recipe_ids``). It stops at the first error of each
    reader with ``stop_at_error``, which gives exit code 1. The warnings are not written and
    change nothing. The matching forms of the catalog's names are built once per run, with no
    module-level cache. It raises no other exception, and none for bad data.

    A word appears in a text when its matching form is part of the text's matching form. A word
    has three places in a recipe, in this order: the recipe's name in each language that it
    has, both catalog names of the ``Ingredient`` of each ingredient line, and both catalog names
    of each ``Tag``. Notes, steps, IDs, servings, quantities, units, and categories do not
    count. A recipe is kept when every word has at least one place.

    Args:
        context: The language, the data folder, and the output and error streams. It uses neither
            ``context.settings`` nor ``context.today``.
        arguments: What the command line gave. ``arguments.values`` holds one or more words, in
            the order of the command line.

    Returns:
        0 when the command wrote its result, also when no recipe matches, and 1 when a file has
        an error. For an error, the error stream gets the three lines of ``stop_at_error`` and
        nothing goes to the output stream. When one or more recipes match, the output is the
        lines of ``format_table`` with no indent, the default gap, and no ``min_widths``, an
        empty line, and the count line. The rows come in the order of ``read_recipes``, after a
        heading row. A row holds ``recipe.id``, ``recipe.name.get(context.lang)``, and
        ``comma_list`` of the messages of the recipe's places, each place once, in the order
        name, ingredient, tag, in ``context.lang``. The count line is ``RECIPES_MATCH`` for one
        word and ``RECIPES_MATCH_ALL`` for two or more words, picked by the number of recipes. Its
        ``words`` are the words as typed, in order, each word that equals an earlier word exactly
        left out, each one through ``QUOTED_WORD`` and ``and_list``. ``RECIPES_MATCH`` or
        ``NO_RECIPE_MATCHES`` is for one word and the ``_ALL`` message for two or more, counted
        after the repeated words are left out. When no recipe matches, also for a ``recipes/``
        folder with no recipe file, the output is one line, ``NO_RECIPE_MATCHES`` or
        ``NO_RECIPE_MATCHES_ALL``, with no table, and the code is 0.

    Raises:
        UsageError: The implementation raises it with ``EMPTY_WORD`` and no hint for the first
            word whose matching form is empty, before it reads a file or writes any output.
    """
    return 0
