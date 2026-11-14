"""The steps of ``show`` after the files are read: the checks and the lines of the recipe."""

from fractions import Fraction

from recipe_menu.app import Context
from recipe_menu.commands.browse.messages import (
    INGREDIENTS_HEADING,
    SCALED_SERVINGS,
    SERVINGS_LINE,
    SERVINGS_ONLY,
    STEPS_HEADING,
    STEPS_IN_OTHER_LANGUAGE,
)
from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS
from recipe_menu.lang import Lang
from recipe_menu.recipes import Recipe
from recipe_menu.text import MessageValue, comma_list, format_table


def parse_servings(value: str) -> int | None:
    """Reads the value of ``--servings``.

    Args:
        value: The text as typed.

    Returns:
        The number when the text is ASCII digits with no leading ``0`` and the number is from
        ``MIN_SERVINGS`` to ``MAX_SERVINGS``. Otherwise ``None``. No long text reaches ``int``.
    """
    if not (value.isascii() and value.isdigit()) or value.startswith("0"):
        return None
    if len(value) > len(str(MAX_SERVINGS)):
        return None
    servings = int(value)
    return servings if MIN_SERVINGS <= servings <= MAX_SERVINGS else None


def _names_line(recipe: Recipe, lang: Lang) -> str:
    """Writes the first line: each name that the recipe has, the chosen language first.

    Args:
        recipe: The recipe.
        lang: The chosen language.

    Returns:
        The names with two spaces between them.
    """
    other = Lang.ZH if lang is Lang.EN else Lang.EN
    names = (recipe.name.exact(lang), recipe.name.exact(other))
    return "  ".join(name for name in names if name is not None)


def _servings_line(recipe: Recipe, servings: int | None, lang: Lang) -> str:
    """Writes the servings line.

    Args:
        recipe: The recipe.
        servings: The value of ``--servings``, or ``None`` without it.
        lang: The language of the line.

    Returns:
        ``SERVINGS_LINE``, or ``SERVINGS_ONLY`` for a recipe with no tags. With a number other
        than the recipe's servings, its servings is ``SCALED_SERVINGS``.
    """
    shown: MessageValue = recipe.servings
    if servings is not None and servings != recipe.servings:
        shown = SCALED_SERVINGS.to_bitext(servings=servings, recipe_servings=recipe.servings)
    if not recipe.tags:
        return SERVINGS_ONLY.render(lang, servings=shown)
    tags = comma_list(tag.name for tag in recipe.tags)
    return SERVINGS_LINE.render(lang, servings=shown, tags=tags)


def _ingredient_lines(recipe: Recipe, servings: int | None, lang: Lang) -> list[str]:
    """Writes the ingredient block.

    Args:
        recipe: The recipe.
        servings: The value of ``--servings``, or ``None`` without it.
        lang: The language of the block.

    Returns:
        The heading, the rows, and an empty line, or no line for a recipe with no ingredients.
    """
    if not recipe.ingredients:
        return []
    factor = Fraction(recipe.servings if servings is None else servings, recipe.servings)
    rows = [
        (
            line.ingredient.name.get(lang),
            line.quantity.scale(factor).to_text(lang),
            "" if line.note is None else line.note.get(lang),
        )
        for line in recipe.ingredients
    ]
    return [INGREDIENTS_HEADING.render(lang), *format_table(rows, indent=2), ""]


def show_output(context: Context, recipe: Recipe, servings: int | None) -> str:
    """Writes everything that ``show`` writes to ``context.out``.

    Args:
        context: The language.
        recipe: The recipe to show.
        servings: The value of ``--servings``, or ``None`` without it.

    Returns:
        The lines of the recipe, each ended by a line break.
    """
    lang = context.lang
    heading = STEPS_HEADING if recipe.steps.exact(lang) is not None else STEPS_IN_OTHER_LANGUAGE
    steps = [f"  {number}. {step}" for number, step in enumerate(recipe.steps.get(lang), 1)]
    lines = [
        _names_line(recipe, lang),
        _servings_line(recipe, servings, lang),
        "",
        *_ingredient_lines(recipe, servings, lang),
        heading.render(lang),
        *steps,
    ]
    return "".join(f"{line}\n" for line in lines)
