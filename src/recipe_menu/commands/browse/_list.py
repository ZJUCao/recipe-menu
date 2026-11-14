"""The steps of ``list`` after the files are read: the tag, the table, and the other lines."""

from collections.abc import Sequence

from recipe_menu.app import Context
from recipe_menu.catalog import Catalog, Tag
from recipe_menu.commands.browse.messages import (
    ID_HEADING,
    NAME_HEADING,
    NO_RECIPE_WITH_TAG,
    NO_RECIPES,
    NO_TAGS,
    RECIPE_COUNT,
    RECIPES_WITH_TAG,
    SERVINGS_HEADING,
    TAGS_HEADING,
    UNKNOWN_TAG,
)
from recipe_menu.recipes import Recipe
from recipe_menu.text import and_list, comma_list, display_width, format_table

# The columns that ``min_widths`` covers: the ID, the name, and the servings.
_SIZED_COLUMNS = 3


def unknown_tag(context: Context, catalog: Catalog, value: str) -> int:
    """Writes the error for a tag that the catalog lacks.

    Args:
        context: The language and the error stream.
        catalog: The catalog, whose tags the message lists in the catalog's order.
        value: The value of ``--tag`` as typed.

    Returns:
        1, after one line went to ``context.err``.
    """
    count = len(catalog.tags)
    if count == 0:
        text = NO_TAGS.render(context.lang, value=value)
    else:
        tags = and_list(tag.name for tag in catalog.tags)
        text = UNKNOWN_TAG.pick(count).render(context.lang, value=value, tags=tags)
    context.err.write(f"{text}\n")
    return 1


def _sized_cells(recipe: Recipe, context: Context) -> tuple[str, str, str]:
    """Builds the first three cells of a recipe's row.

    Args:
        recipe: The recipe.
        context: The language of the cells.

    Returns:
        The ID, the name, and the servings.
    """
    return recipe.id, recipe.name.get(context.lang), str(recipe.servings)


def _row(recipe: Recipe, cells: tuple[str, str, str], context: Context) -> tuple[str, ...]:
    """Builds the four cells of a kept recipe's row.

    Args:
        recipe: The recipe.
        cells: The first three cells of the row.
        context: The language of the cells.

    Returns:
        The ID, the name, the servings, and the tags in the recipe's order.
    """
    return (*cells, comma_list(tag.name for tag in recipe.tags).get(context.lang))


def _widths(rows: Sequence[Sequence[str]]) -> list[int]:
    """Measures the first three columns over every row.

    Args:
        rows: The rows, without the heading.

    Returns:
        For each of the ID, the name, and the servings, the largest ``display_width`` of a line
        of its cells, with each cell split as rule 1 of ``format_table`` splits it.
    """
    widths = [0] * _SIZED_COLUMNS
    for row in rows:
        for index in range(_SIZED_COLUMNS):
            for line in row[index].splitlines():
                widths[index] = max(widths[index], display_width(line))
    return widths


def _count_line(context: Context, count: int, tag: Tag | None) -> str:
    """Writes the line that counts the kept recipes.

    Args:
        context: The language.
        count: The number of kept recipes, 1 or more.
        tag: The tag of ``--tag``, or ``None`` without it.

    Returns:
        ``RECIPE_COUNT``, or ``RECIPES_WITH_TAG`` with a tag.
    """
    if tag is None:
        return RECIPE_COUNT.pick(count).render(context.lang, count=count)
    return RECIPES_WITH_TAG.pick(count).render(context.lang, count=count, tag=tag.name)


def list_output(context: Context, recipes: Sequence[Recipe], tag: Tag | None) -> str:
    """Writes everything that ``list`` writes to ``context.out``.

    Args:
        context: The language.
        recipes: Every recipe that was read, in the order of the IDs.
        tag: The tag of ``--tag``, or ``None`` to keep every recipe.

    Returns:
        The table and the count line, or the one line for no recipe, each ended by a line break.
    """
    rows = [(recipe, _sized_cells(recipe, context)) for recipe in recipes]
    kept = [
        _row(recipe, cells, context) for recipe, cells in rows if tag is None or tag in recipe.tags
    ]
    if not kept:
        if tag is None:
            return f"{NO_RECIPES.render(context.lang)}\n"
        return f"{NO_RECIPE_WITH_TAG.render(context.lang, tag=tag.name)}\n"
    headings = (ID_HEADING, NAME_HEADING, SERVINGS_HEADING, TAGS_HEADING)
    heading = tuple(message.render(context.lang) for message in headings)
    table = format_table([heading, *kept], min_widths=_widths([cells for _, cells in rows]))
    lines = [*table, "", _count_line(context, len(kept), tag)]
    return "".join(f"{line}\n" for line in lines)
