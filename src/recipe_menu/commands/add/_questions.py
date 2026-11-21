"""The eight questions of ``add``, each asked again after a wrong answer."""

import re
from collections.abc import Callable

from recipe_menu.app import Context
from recipe_menu.catalog import Catalog, Tag
from recipe_menu.commands.add._ask import ask_line, write_line
from recipe_menu.commands.add._ingredient import check_line
from recipe_menu.commands.add._model import IngredientLine, NewRecipe
from recipe_menu.commands.add.messages import (
    EN_NAME_PROMPT,
    EN_STEPS_OPTIONAL_PROMPT,
    EN_STEPS_PROMPT,
    ID_EXISTS,
    ID_PROMPT,
    INGREDIENTS_PROMPT,
    INPUT_ENDED,
    NAME_NEEDED,
    NO_TAGS,
    NOT_AN_ID,
    SERVINGS_PROMPT,
    SERVINGS_WRONG,
    STEPS_NEEDED,
    TAGS_PROMPT,
    UNKNOWN_TAG,
    ZH_NAME_PROMPT,
    ZH_STEPS_PROMPT,
)
from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS
from recipe_menu.recipes import is_recipe_id
from recipe_menu.text import and_list

# Splits a list of tags at "," and at U+FF0C and U+3001, built from code points.
_COMMA = re.compile(f"[,{chr(0xFF0C)}{chr(0x3001)}]")
_INDENT = "  "


def _id_problem(context: Context, answer: str, ids: frozenset[str]) -> str | None:
    """Finds what is wrong with an ID.

    Args:
        context: The language.
        answer: The ID as typed, not empty.
        ids: The IDs that ``recipes/`` holds.

    Returns:
        The message, or ``None`` when the ID is right.
    """
    if not is_recipe_id(answer):
        return NOT_AN_ID.render(context.lang, id=answer)
    if answer in ids:
        return ID_EXISTS.render(context.lang, id=answer)
    return None


def _ask_id(context: Context, ids: frozenset[str]) -> str | None:
    """Asks question 1 until the ID is right or the answer is empty.

    Args:
        context: The streams and the language.
        ids: The IDs that ``recipes/`` holds.

    Returns:
        The ID, or the empty text, or ``None`` at the end of the input.
    """
    while True:
        answer = ask_line(context, ID_PROMPT.render(context.lang))
        problem = _id_problem(context, answer, ids) if answer else None
        if problem is None:
            return answer
        write_line(context, problem)


def _ask_names(context: Context) -> tuple[str, str] | None:
    """Asks questions 2 and 3.

    Args:
        context: The streams and the language.

    Returns:
        The Chinese and the English name, either one possibly empty but not both, or ``None`` at
        the end of the input.
    """
    zh_name = ask_line(context, ZH_NAME_PROMPT.render(context.lang))
    if zh_name is None:
        return None
    while True:
        en_name = ask_line(context, EN_NAME_PROMPT.render(context.lang))
        if en_name is None:
            return None
        if zh_name or en_name:
            return zh_name, en_name
        write_line(context, NAME_NEEDED.render(context.lang))


def _servings(answer: str) -> int | None:
    """Reads the servings.

    Args:
        answer: The answer, not empty.

    Returns:
        The servings, or ``None`` when the answer is not ASCII digits for a whole number from
        ``MIN_SERVINGS`` to ``MAX_SERVINGS``.
    """
    if not (answer.isascii() and answer.isdigit()):
        return None
    digits = answer.lstrip("0")
    if len(digits) > len(str(MAX_SERVINGS)):
        return None
    value = int(digits or "0")
    return value if MIN_SERVINGS <= value <= MAX_SERVINGS else None


def _ask_servings(context: Context) -> int | None:
    """Asks question 4.

    Args:
        context: The streams, the language, and the settings.

    Returns:
        The servings, the servings of the settings for an empty answer, or ``None`` at the end
        of the input.
    """
    prompt = SERVINGS_PROMPT.render(context.lang, servings=context.settings.servings)
    while True:
        answer = ask_line(context, prompt)
        if answer is None:
            return None
        servings = context.settings.servings if not answer else _servings(answer)
        if servings is not None:
            return servings
        write_line(context, SERVINGS_WRONG.render(context.lang))


def _unknown_tag(context: Context, catalog: Catalog, value: str) -> str:
    """Writes the message for a tag that the catalog does not have.

    Args:
        context: The language.
        catalog: The catalog, whose tags the message lists.
        value: The part of the answer that names no tag.

    Returns:
        The message.
    """
    count = len(catalog.tags)
    if count == 0:
        return NO_TAGS.render(context.lang, value=value)
    tags = and_list(tag.name for tag in catalog.tags)
    return UNKNOWN_TAG.pick(count).render(context.lang, value=value, tags=tags)


def _read_tags(context: Context, catalog: Catalog, answer: str) -> tuple[str, ...] | str:
    """Reads the tags of an answer.

    Args:
        context: The language.
        catalog: The catalog.
        answer: The answer, split at three kinds of comma.

    Returns:
        The tags as typed, each naming a different tag, or the message for the first part that
        names no tag.
    """
    found: dict[Tag, str] = {}
    for part in (piece.strip() for piece in _COMMA.split(answer)):
        tag = catalog.find_tag(part) if part else None
        if part and tag is None:
            return _unknown_tag(context, catalog, part)
        if tag is not None:
            found.setdefault(tag, part)
    return tuple(found.values())


def _ask_tags(context: Context, catalog: Catalog) -> tuple[str, ...] | None:
    """Asks question 5.

    Args:
        context: The streams and the language.
        catalog: The catalog.

    Returns:
        The tags, or ``None`` at the end of the input.
    """
    while True:
        answer = ask_line(context, TAGS_PROMPT.render(context.lang))
        if answer is None:
            return None
        tags = _read_tags(context, catalog, answer)
        if not isinstance(tags, str):
            return tags
        write_line(context, tags)


def _ask_list(
    context: Context, prompt: str, wrong: Callable[[str], str | None]
) -> tuple[str, ...] | None:
    """Asks for a list, one line at a time, until an empty line.

    Args:
        context: The streams.
        prompt: The prompt of the list.
        wrong: Gives the message for a line that is wrong, or ``None`` for a right line.

    Returns:
        The right lines, or ``None`` at the end of the input.
    """
    write_line(context, prompt)
    lines: list[str] = []
    while True:
        line = ask_line(context, _INDENT)
        if not line:
            return None if line is None else tuple(lines)
        message = wrong(line)
        if message is None:
            lines.append(line)
        else:
            write_line(context, message, _INDENT)


def _ask_ingredients(context: Context, catalog: Catalog) -> tuple[IngredientLine, ...] | None:
    """Asks question 6.

    Args:
        context: The streams and the language.
        catalog: The catalog.

    Returns:
        The ingredient lines, or ``None`` at the end of the input.
    """
    kept: list[IngredientLine] = []

    def wrong(line: str) -> str | None:
        """Checks one line, and keeps it when it is right.

        Args:
            line: The line.

        Returns:
            The message, or ``None`` for a right line.
        """
        checked = check_line(catalog, line, context.lang)
        if isinstance(checked, str):
            return checked
        kept.append(checked)
        return None

    prompt = INGREDIENTS_PROMPT.render(context.lang)
    return None if _ask_list(context, prompt, wrong) is None else tuple(kept)


def _accept(line: str) -> None:
    """Accepts every step.

    Args:
        line: The step.
    """


def _ask_steps(context: Context) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    """Asks questions 7 and 8.

    Args:
        context: The streams and the language.

    Returns:
        The Chinese and the English steps, not both empty, or ``None`` at the end of the input.
    """
    zh_steps = _ask_list(context, ZH_STEPS_PROMPT.render(context.lang), _accept)
    if zh_steps is None:
        return None
    optional = EN_STEPS_OPTIONAL_PROMPT if zh_steps else EN_STEPS_PROMPT
    while True:
        en_steps = _ask_list(context, optional.render(context.lang), _accept)
        if en_steps is None:
            return None
        if zh_steps or en_steps:
            return zh_steps, en_steps
        write_line(context, STEPS_NEEDED.render(context.lang))


def _ended(context: Context) -> int:
    """Writes the message for an input that ended before the last question.

    Args:
        context: The language and the error stream.

    Returns:
        1.
    """
    context.err.write(INPUT_ENDED.render(context.lang) + "\n")
    return 1


def ask_recipe(context: Context, catalog: Catalog, ids: frozenset[str]) -> NewRecipe | int:
    """Asks the eight questions in order.

    Args:
        context: The streams, the language, and the settings.
        catalog: The catalog that tags and ingredients are checked against.
        ids: The IDs that ``recipes/`` holds.

    Returns:
        The answers. Or 0 when the first answer is empty or the input ends at the first
        question, and 1, after a message on the error stream, when the input ends later.
    """
    recipe_id = _ask_id(context, ids)
    if not recipe_id:
        return 0
    names = _ask_names(context)
    servings = None if names is None else _ask_servings(context)
    tags = None if servings is None else _ask_tags(context, catalog)
    ingredients = None if tags is None else _ask_ingredients(context, catalog)
    steps = None if ingredients is None else _ask_steps(context)
    if names is None or servings is None or tags is None:
        return _ended(context)
    if ingredients is None or steps is None:
        return _ended(context)
    return NewRecipe(recipe_id, *names, servings, tags, ingredients, *steps)
