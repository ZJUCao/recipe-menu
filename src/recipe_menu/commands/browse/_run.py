"""The run functions of the ``list`` and ``show`` commands."""

from typing import cast

from recipe_menu.app import Arguments, Context, UsageError, first_error, stop_at_error
from recipe_menu.commands.browse._common import read_catalog_or_stop
from recipe_menu.commands.browse._list import list_output, unknown_tag
from recipe_menu.commands.browse._show import parse_servings, show_output
from recipe_menu.commands.browse.messages import (
    NOT_A_RECIPE_ID,
    SERVINGS_NOT_1_TO_100,
    UNKNOWN_ID,
)
from recipe_menu.recipes import Recipe, is_recipe_id, list_recipe_ids, read_recipe, read_recipes


def run_list(context: Context, arguments: Arguments) -> int:
    """Lists the recipes, or the recipes with one tag, as a table on ``context.out``.

    It reads the catalog with ``read_catalog`` and stops at the first error with
    ``stop_at_error``. With ``--tag`` it then looks for the tag with ``Catalog.find_tag``, before
    it reads a recipe. Then it reads every recipe with ``read_recipes`` and stops at the first
    error with ``stop_at_error``. The warnings change nothing.

    Args:
        context: The language, the data folder, and the output and error streams. It uses neither
            ``context.settings`` nor ``context.today``.
        arguments: What the command line gave. It has no values. ``arguments.option("--tag")`` is
            the name of the tag to keep, or ``None``.

    Returns:
        0 when the command wrote its list, also an empty one, and 1 when a file has an error or
        the catalog has no tag with the name of ``--tag``. For a tag that is not found, the error
        stream gets ``UNKNOWN_TAG`` (one tag or more, with the catalog's tags in the catalog's
        order) or ``NO_TAGS`` (a catalog with no tags), one line, and nothing goes to the output
        stream. When no recipe is kept, the output is one line and no table: ``NO_RECIPES``, or
        ``NO_RECIPE_WITH_TAG`` with ``--tag``. Otherwise the output is the lines of
        ``format_table`` with one row for each kept recipe, an empty line, and the count line
        (``RECIPE_COUNT``, or ``RECIPES_WITH_TAG`` with ``--tag``). The rows come in the order of
        the IDs, and the rows keep each recipe whose tags hold the tag. A row holds the ID, the
        name in the chosen language (the name in the other language when the chosen one is
        missing), the servings, and the tags in the recipe's order. ``min_widths`` holds, for the
        first three columns, the largest ``display_width`` of a line of the cell over every recipe
        that was read, kept or not, with each cell split into lines as rule 1 of ``format_table``
        splits it, so a list with a tag lines up with the list without one. It raises no exception
        for bad data.
    """
    catalog = read_catalog_or_stop(context)
    if isinstance(catalog, int):
        return catalog
    value = arguments.option("--tag")
    tag = None if value is None else catalog.find_tag(value)
    if value is not None and tag is None:
        return unknown_tag(context, catalog, value)
    recipes, problems = read_recipes(context.folder, catalog)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    context.out.write(list_output(context, recipes, tag))
    return 0


def run_show(context: Context, arguments: Arguments) -> int:
    """Shows one recipe, scaled to ``--servings`` when the option is given, on ``context.out``.

    It checks ``--servings`` first and then ``ID``, before it reads a file. Then
    it reads the catalog with ``read_catalog``, lists ``recipes/`` with ``list_recipe_ids``, and
    reads only the recipe with ``read_recipe``. It stops at the first error of each reader with
    ``stop_at_error``. The warnings change nothing.

    Args:
        context: The language, the data folder, and the output and error streams. It uses neither
            ``context.settings`` nor ``context.today``.
        arguments: What the command line gave. ``arguments.values`` is ``(ID,)``, and
            ``arguments.option("--servings")`` is the servings to scale to, or ``None``.

    Returns:
        0 when the recipe was written, and 1 when a file has an error or the listing lacks the
        ID. For an ID that the listing lacks, the error stream gets ``UNKNOWN_ID``, and nothing
        goes to the output stream. The output is these lines. The first line holds each name that
        ``recipe.name.exact`` gives, the chosen language first, with two spaces between them, so
        a name that the recipe lacks is left out and two names with the same text are both
        written. The servings line follows: ``SERVINGS_LINE``, or ``SERVINGS_ONLY`` for a recipe
        with no tags. Its servings is the recipe's servings, or ``SCALED_SERVINGS`` with the value
        of ``--servings`` and the recipe's servings when ``--servings`` differs from them. Then an
        empty line. A recipe with ingredients has ``INGREDIENTS_HEADING``, one row for each
        ingredient line, and an empty line. A row holds the ingredient's name, the quantity, and
        the note. The quantity is scaled by ``Fraction(servings, recipe.servings)`` with
        ``Quantity.scale`` and written with ``Quantity.to_text``, which keeps the recipe's unit,
        and a quantity to taste stays to taste. The steps follow: ``STEPS_HEADING``, or
        ``STEPS_IN_OTHER_LANGUAGE`` when ``Steps.exact`` gives ``None`` for the chosen language,
        and then each step as a numbered line, as the file writes it.

    Raises:
        UsageError: Raised with ``SERVINGS_NOT_1_TO_100`` when the text of
            ``--servings`` is not ASCII digits with no leading ``0`` and from 1 to 100, and then
            with ``NOT_A_RECIPE_ID`` when ``is_recipe_id`` is false for ``ID``. Neither has a
            hint, and neither reads a file or writes any output.
    """
    value = arguments.option("--servings")
    servings = None if value is None else parse_servings(value)
    if value is not None and servings is None:
        raise UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)
    (recipe_id,) = arguments.values
    if not is_recipe_id(recipe_id):
        raise UsageError(NOT_A_RECIPE_ID, None, id=recipe_id)
    catalog = read_catalog_or_stop(context)
    if isinstance(catalog, int):
        return catalog
    ids, problems = list_recipe_ids(context.folder)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    if recipe_id not in ids:
        context.err.write(f"{UNKNOWN_ID.render(context.lang, id=recipe_id)}\n")
        return 1
    recipe, problems = read_recipe(context.folder, catalog, recipe_id)
    error = first_error(problems)
    if error is not None:
        return stop_at_error(context, error)
    # A recipe is None only after an error.
    context.out.write(show_output(context, cast(Recipe, recipe), servings))
    return 0
