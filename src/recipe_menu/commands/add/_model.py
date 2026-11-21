"""The answers of ``add`` that make a recipe file."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IngredientLine:
    """One right ingredient line, split into its name and its quantity.

    Attributes:
        name: The name as typed, without whitespace at both ends.
        quantity: The quantity as typed, from its first word to the end of the line.
    """

    name: str
    quantity: str


@dataclass(frozen=True, slots=True)
class NewRecipe:
    """The answers to the eight questions, ready to be written as a file.

    Attributes:
        recipe_id: The ID, which is also the name of the file.
        zh_name: The Chinese name, or the empty text for no Chinese name.
        en_name: The English name, or the empty text for no English name.
        servings: The servings, from 1 to 100.
        tags: The tags as typed, each naming a different tag of the catalog.
        ingredients: The ingredient lines, in the order typed.
        zh_steps: The Chinese steps, in the order typed.
        en_steps: The English steps, in the order typed.
    """

    recipe_id: str
    zh_name: str
    en_name: str
    servings: int
    tags: tuple[str, ...]
    ingredients: tuple[IngredientLine, ...]
    zh_steps: tuple[str, ...]
    en_steps: tuple[str, ...]
