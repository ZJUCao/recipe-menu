"""The output of ``search``: the table, the count line, and the line for no match."""

from collections.abc import Sequence

from recipe_menu.app import Context
from recipe_menu.commands.search._match import WordHits, recipe_places
from recipe_menu.commands.search.messages import (
    ID_HEADING,
    INGREDIENT_PLACE,
    MATCHED_IN_HEADING,
    NAME_HEADING,
    NAME_PLACE,
    NO_RECIPE_MATCHES,
    NO_RECIPE_MATCHES_ALL,
    QUOTED_WORD,
    RECIPES_MATCH,
    RECIPES_MATCH_ALL,
    TAG_PLACE,
)
from recipe_menu.lang import BiText
from recipe_menu.recipes import Recipe
from recipe_menu.text import and_list, comma_list, format_table


def _words_text(context: Context, words: Sequence[str]) -> tuple[str, int]:
    """Names the words of the count line.

    Args:
        context: The language.
        words: The words as typed.

    Returns:
        ``and_list`` of the quoted words, each word that equals an earlier word left out, and the
        number of words that are left.
    """
    distinct = list(dict.fromkeys(words))
    quoted = [QUOTED_WORD.to_bitext(word=word) for word in distinct]
    return and_list(quoted).get(context.lang), len(distinct)


def _rows(
    context: Context,
    recipes: Sequence[Recipe],
    hits: Sequence[WordHits],
) -> list[tuple[str, str, str]]:
    """Builds the row of each recipe that matches.

    Args:
        context: The language.
        recipes: Every recipe, in order.
        hits: The ``WordHits`` of every word.

    Returns:
        The rows of the recipes that hold every word: the ID, the name, and the places.
    """
    names: tuple[BiText, ...] = (
        NAME_PLACE.to_bitext(),
        INGREDIENT_PLACE.to_bitext(),
        TAG_PLACE.to_bitext(),
    )
    rows = []
    for recipe in recipes:
        places = recipe_places(recipe, hits)
        if places is not None:
            matched = comma_list(names[place] for place in places).get(context.lang)
            rows.append((recipe.id, recipe.name.get(context.lang), matched))
    return rows


def search_output(
    context: Context,
    recipes: Sequence[Recipe],
    hits: Sequence[WordHits],
    words: Sequence[str],
) -> str:
    """Writes everything that ``search`` writes to ``context.out``.

    Args:
        context: The language.
        recipes: Every recipe that was read, in order.
        hits: The ``WordHits`` of every word.
        words: The words as typed.

    Returns:
        The table, an empty line, and the count line, or the one line for no match, each ended by
        a line break.
    """
    rows = _rows(context, recipes, hits)
    text, count = _words_text(context, words)
    several = count > 1
    if not rows:
        message = NO_RECIPE_MATCHES_ALL if several else NO_RECIPE_MATCHES
        return f"{message.render(context.lang, words=text)}\n"
    plural = RECIPES_MATCH_ALL if several else RECIPES_MATCH
    line = plural.pick(len(rows)).render(context.lang, count=len(rows), words=text)
    headings = (ID_HEADING, NAME_HEADING, MATCHED_IN_HEADING)
    heading = tuple(message.render(context.lang) for message in headings)
    return "".join(f"{each}\n" for each in [*format_table([heading, *rows]), "", line])
