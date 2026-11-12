"""The values of ``recipes``: a recipe, its ingredient lines, and its steps."""

from dataclasses import dataclass

from recipe_menu.catalog import Ingredient, Tag
from recipe_menu.lang import BiText, Lang
from recipe_menu.units import Quantity


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    """One ingredient line of a recipe: the catalog's ingredient, its quantity, and its note.

    It refers to the same ``Ingredient`` object as the catalog, so a shopping list merges
    ingredients by identity. Two lines are equal when their three fields are equal, and a
    ``RecipeIngredient`` is hashable.

    The constructor checks its values.

    The mock leaves these checks out.

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


@dataclass(frozen=True, slots=True)
class Steps:
    """The steps of a recipe, as a tuple of texts for each language, with at least one language.

    Like ``BiText``, it gives the asked language, or the other language when the asked one is
    missing. Two ``Steps`` values are equal when their ``en`` and their ``zh`` are equal, and a
    ``Steps`` is hashable.

    The constructor checks its values.

    The mock leaves these checks out.

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

    def get(self, lang: Lang) -> tuple[str, ...]:
        """Gives the steps in a language, with a fallback.

        The mock only raises ``NotImplementedError``.

        Args:
            lang: The language to give.

        Returns:
            The steps in ``lang``, or the steps in the other language when the ones in ``lang``
            are ``None``. It never gives ``None``.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    def exact(self, lang: Lang) -> tuple[str, ...] | None:
        """Gives the steps in a language, with no fallback.

        The mock only raises ``NotImplementedError``.

        Args:
            lang: The language to give.

        Returns:
            The steps in ``lang``, or ``None`` when they are missing. F09 uses ``None`` to say
            that it shows the steps in the other language.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Recipe:
    """One recipe: its ID, its names, its servings, its tags, its ingredients, and its steps.

    The ID is the file name without ``.toml``, and IDs compare exactly as written. The tags and
    the ingredients are values of the catalog. Two recipes are equal when their six fields are
    equal, and a ``Recipe`` is hashable.

    The constructor checks its values.

    The mock leaves these checks out.

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
