"""The parts of the catalog: categories, ingredients, tags, and the pantry."""

from dataclasses import dataclass

from recipe_menu.lang import BiText
from recipe_menu.units import Unit


@dataclass(frozen=True, slots=True)
class Category:
    """A shopping category. The catalog's order of categories is the shopping order.

    Two categories are equal when all their fields are equal, and a ``Category`` is hashable.

    The constructor checks its values. The mock leaves these checks out.

    Attributes:
        key: The category's key, which an ingredient's ``category`` names, such as ``produce``.
            It holds more than whitespace.
        name: The category's names in both languages. Each language that is set holds more than
            whitespace. One language may be missing, because ``read_catalog`` keeps a category
            whose other name is wrong.

    Raises:
        ValueError: ``key`` is empty or holds only whitespace, or a language of ``name`` that is
            set is empty or holds only whitespace.
    """

    key: str
    name: BiText


@dataclass(frozen=True, slots=True)
class Ingredient:
    """An ingredient with its names in both languages, its category, and its default unit.

    Two ingredients are equal when all their fields are equal, and an ``Ingredient`` is
    hashable. A ``Catalog`` holds no two ingredients with matching names, so two equal
    ingredients of one catalog are the same object.

    The constructor checks its values. The mock leaves these checks out.

    Attributes:
        name: The names in English and Chinese. Both are set, and each holds more than
            whitespace.
        category: The ingredient's shopping category. One of the catalog's categories.
        unit: The default unit of a quantity without a unit, or ``None`` when the ingredient has
            no default unit.

    Raises:
        ValueError: A language of ``name`` is ``None``, is empty, or holds only whitespace.
    """

    name: BiText
    category: Category
    unit: Unit | None = None


@dataclass(frozen=True, slots=True)
class Tag:
    """A tag with its names in both languages.

    Two tags are equal when their names are equal, and a ``Tag`` is hashable.

    The constructor checks its values. The mock leaves these checks out.

    Attributes:
        name: The names in English and Chinese. Both are set, and each holds more than
            whitespace.

    Raises:
        ValueError: A language of ``name`` is ``None``, is empty, or holds only whitespace.
    """

    name: BiText


@dataclass(frozen=True, slots=True)
class Pantry:
    """The ingredients that you always have at home. The shopping list leaves them out.

    Two pantries are equal when their sets are equal, and a ``Pantry`` is hashable. The set has
    no order, so a caller gives the pantry line its order, such as the catalog's order. It has
    no checks.

    Attributes:
        ingredients: The pantry's ingredients, which are ingredients of the catalog that
            ``read_pantry`` got.
    """

    ingredients: frozenset[Ingredient]
