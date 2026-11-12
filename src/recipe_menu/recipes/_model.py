"""The values of ``recipes``: a recipe, its ingredient lines, and its steps."""

from dataclasses import dataclass
from typing import cast

from recipe_menu.catalog import Ingredient, Tag
from recipe_menu.lang import BiText, Lang
from recipe_menu.recipes._ids import is_recipe_id
from recipe_menu.units import Quantity

_MAX_SERVINGS = 100


def _check_texts(name: BiText, what: str) -> None:
    """Checks that each language that is set holds more than whitespace.

    Args:
        name: The text in two languages.
        what: What the text is, for the message of the error.

    Raises:
        ValueError: A language that is set is empty or holds only whitespace.
    """
    for text in (name.en, name.zh):
        if text is not None and not text.strip():
            raise ValueError(f"a language of {what} that is set must hold more than whitespace")


def _check_steps(steps: object) -> None:
    """Checks the steps of one language.

    Args:
        steps: The tuple of steps, or ``None`` for a missing language.

    Raises:
        TypeError: ``steps`` is neither a tuple nor ``None``, or it holds a step that is not a
            ``str``.
        ValueError: ``steps`` is the empty tuple, or it holds a blank step.
    """
    if steps is None:
        return
    if not isinstance(steps, tuple):
        raise TypeError(f"steps must be a tuple or None, not {type(steps).__name__}")
    if not all(isinstance(step, str) for step in steps):
        raise TypeError("a step must be a str")
    if not steps or not all(step.strip() for step in steps):
        raise ValueError("steps must hold at least one step, and each more than whitespace")


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    """One ingredient line of a recipe: the catalog's ingredient, its quantity, and its note.

    It refers to the same ``Ingredient`` object as the catalog, so a shopping list merges
    ingredients by identity. Two lines are equal when their three fields are equal, and a
    ``RecipeIngredient`` is hashable.

    The constructor checks its values.

    Attributes:
        ingredient: The ingredient of the catalog that the recipe was read with.
        quantity: The amount with its unit, or to taste. ``read_recipe`` gives an amount without
            a unit the default unit of the ingredient.
        note: The note, or ``None`` when the line has no note. Each language that is set holds
            more than whitespace. One language may be missing.

    Raises:
        ValueError: A language of ``note`` that is set is empty or holds only whitespace.
    """

    ingredient: Ingredient
    quantity: Quantity
    note: BiText | None = None

    def __post_init__(self) -> None:
        """Checks the note.

        Raises:
            ValueError: A language of ``note`` that is set is blank.
        """
        if self.note is not None:
            _check_texts(self.note, "a note")


@dataclass(frozen=True, slots=True)
class Steps:
    """The steps of a recipe, as a tuple of texts for each language, with at least one language.

    Like ``BiText``, it gives the asked language, or the other language when the asked one is
    missing. Two ``Steps`` values are equal when their ``en`` and their ``zh`` are equal, and a
    ``Steps`` is hashable.

    The constructor checks its values.

    Attributes:
        en: The English steps, in order. ``None`` when the recipe has no English steps.
            Otherwise one or more steps, and each holds more than whitespace.
        zh: The Chinese steps, as for ``en``. ``en`` and ``zh`` are not both ``None``.

    Raises:
        ValueError: ``en`` and ``zh`` are both ``None``, or ``en`` or ``zh`` is the empty tuple
            or holds a step that is empty or holds only whitespace.
        TypeError: ``en`` or ``zh`` is neither a tuple nor ``None``, such as a list, or holds a
            step that is not a ``str``.
    """

    en: tuple[str, ...] | None = None
    zh: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        """Checks both languages.

        Raises:
            ValueError: Both are ``None``, or one is empty or holds a blank step.
            TypeError: One is neither a tuple nor ``None``, or holds a step that is not a ``str``.
        """
        if self.en is None and self.zh is None:
            raise ValueError("steps need at least one language")
        _check_steps(self.en)
        _check_steps(self.zh)

    def get(self, lang: Lang) -> tuple[str, ...]:
        """Gives the steps in a language, with a fallback.

        Args:
            lang: The language to give.

        Returns:
            The steps in ``lang``, or the steps in the other language when the ones in ``lang``
            are ``None``. It never gives ``None``.
        """
        first, second = (self.en, self.zh) if lang is Lang.EN else (self.zh, self.en)
        # __post_init__ keeps at least one of the two languages set.
        return first if first is not None else cast(tuple[str, ...], second)

    def exact(self, lang: Lang) -> tuple[str, ...] | None:
        """Gives the steps in a language, with no fallback.

        Args:
            lang: The language to give.

        Returns:
            The steps in ``lang``, or ``None`` when they are missing. F09 uses ``None`` to say
            that it shows the steps in the other language.
        """
        return self.en if lang is Lang.EN else self.zh


@dataclass(frozen=True, slots=True)
class Recipe:
    """One recipe: its ID, its names, its servings, its tags, its ingredients, and its steps.

    The ID is the file name without ``.toml``, and IDs compare exactly as written. The tags and
    the ingredients are values of the catalog. Two recipes are equal when their six fields are
    equal, and a ``Recipe`` is hashable.

    The constructor checks its values.

    Attributes:
        id: The ID, such as ``tomato-egg``. ``is_recipe_id(id)`` is true.
        name: The names. Each language that is set holds more than whitespace. One language may
            be missing.
        servings: The servings that the recipe makes, from 1 to 100. Not a ``bool``.
        tags: The tags of the catalog, in the file's order. ``read_recipe`` gives each tag once.
            May be empty.
        ingredients: The ingredient lines, in the file's order. May be empty.
        steps: The steps.

    Raises:
        ValueError: ``is_recipe_id(id)`` is false, ``servings`` is less than 1 or more than 100,
            or a language of ``name`` that is set is empty or holds only whitespace.
        TypeError: ``servings`` is not an ``int``, or it is a ``bool``.
    """

    id: str
    name: BiText
    servings: int
    tags: tuple[Tag, ...]
    ingredients: tuple[RecipeIngredient, ...]
    steps: Steps

    def __post_init__(self) -> None:
        """Checks the ID, the name, and the servings.

        Raises:
            ValueError: The ID breaks the rule, a language of ``name`` is blank, or ``servings``
                is out of range.
            TypeError: ``servings`` is not an ``int``, or it is a ``bool``.
        """
        if not is_recipe_id(self.id):
            raise ValueError(f"not a recipe ID: {self.id!r}")
        _check_texts(self.name, "a name")
        if isinstance(self.servings, bool) or not isinstance(self.servings, int):
            raise TypeError("servings must be an int")
        if not 1 <= self.servings <= _MAX_SERVINGS:
            raise ValueError(f"servings must be from 1 to {_MAX_SERVINGS}")
