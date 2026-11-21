"""The text of the new recipe file."""

from recipe_menu.commands.add._model import IngredientLine, NewRecipe

_BACKSLASH = chr(92)


def _quote(text: str) -> str:
    """Writes a text as a TOML basic string.

    Args:
        text: Any text.

    Returns:
        The text in double quotation marks, with the backslash, the double quotation mark, and
        each control character from U+0000 to U+001F and U+007F escaped.
    """
    escaped = text.replace(_BACKSLASH, _BACKSLASH * 2).replace('"', _BACKSLASH + '"')
    pieces = [
        f"{_BACKSLASH}u{ord(char):04x}" if ord(char) < 0x20 or ord(char) == 0x7F else char
        for char in escaped
    ]
    return '"' + "".join(pieces) + '"'


def _name_line(recipe: NewRecipe) -> str:
    """Writes the ``name`` line, which leaves out an empty language.

    Args:
        recipe: The answers.

    Returns:
        The line, without a line break.
    """
    parts = [
        f"{key} = {_quote(name)}"
        for key, name in (("zh", recipe.zh_name), ("en", recipe.en_name))
        if name
    ]
    return "name = { " + ", ".join(parts) + " }"


def _ingredient_lines(lines: tuple[IngredientLine, ...]) -> list[str]:
    """Writes the ``ingredients`` list.

    Args:
        lines: The ingredient lines.

    Returns:
        The lines of the list, which is one line for no ingredients.
    """
    if not lines:
        return ["ingredients = []"]
    rows = [
        f"  {{ item = {_quote(line.name)}, amount = {_quote(line.quantity)} }}," for line in lines
    ]
    return ["ingredients = [", *rows, "]"]


def _steps_lines(key: str, steps: tuple[str, ...]) -> list[str]:
    """Writes the steps of one language.

    Args:
        key: ``zh`` or ``en``.
        steps: The steps.

    Returns:
        The lines of the list, or no line for no steps.
    """
    if not steps:
        return []
    return [f"{key} = [", *(f"  {_quote(step)}," for step in steps), "]"]


def recipe_text(recipe: NewRecipe) -> str:
    """Writes the text of the recipe file, in the layout of the example data.

    Args:
        recipe: The answers.

    Returns:
        The text of the file. Every line ends with LF, the last one too.
    """
    tags = ", ".join(_quote(tag) for tag in recipe.tags)
    lines = [
        _name_line(recipe),
        f"servings = {recipe.servings}",
        f"tags = [{tags}]",
        "",
        *_ingredient_lines(recipe.ingredients),
        "",
        "[steps]",
        *_steps_lines("zh", recipe.zh_steps),
        *_steps_lines("en", recipe.en_steps),
    ]
    return "".join(f"{line}\n" for line in lines)
