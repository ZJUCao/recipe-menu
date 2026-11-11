"""The parts of the catalog: categories, ingredients, tags, and the pantry."""

from dataclasses import dataclass

from recipe_menu.catalog._matching import is_blank
from recipe_menu.lang import BiText
from recipe_menu.units import Unit


def _check_both_names(name: BiText) -> None:
    """Checks that a name has both languages, each with more than whitespace.

    Args:
        name: The names of an ingredient or a tag.

    Raises:
        ValueError: A language is ``None`` or holds only whitespace.
    """
    for text in (name.en, name.zh):
        if text is None or is_blank(text):
            raise ValueError("both names must be set and hold more than whitespace")


@dataclass(frozen=True, slots=True)
class Category:
    """A shopping category. The catalog's order of categories is the shopping order.

    Two categories are equal when all their fields are equal, and a ``Category`` is hashable.

    The constructor checks its values.

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

    def __post_init__(self) -> None:
        """Checks the key and the names.

        Raises:
            ValueError: ``key`` is blank, or a language of ``name`` that is set is blank.
        """
        if is_blank(self.key):
            raise ValueError("the key of a category must hold more than whitespace")
        for text in (self.name.en, self.name.zh):
            if text is not None and is_blank(text):
                raise ValueError("a name of a category must hold more than whitespace")


@dataclass(frozen=True, slots=True)
class Ingredient:
    """An ingredient with its names in both languages, its category, and its default unit.

    Two ingredients are equal when all their fields are equal, and an ``Ingredient`` is
    hashable. A ``Catalog`` holds no two ingredients with matching names, so two equal
    ingredients of one catalog are the same object.

    The constructor checks its values.

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

    def __post_init__(self) -> None:
        """Checks the names.

        Raises:
            ValueError: A language of ``name`` is ``None`` or blank.
        """
        _check_both_names(self.name)


@dataclass(frozen=True, slots=True)
class Tag:
    """A tag with its names in both languages.

    Two tags are equal when their names are equal, and a ``Tag`` is hashable.

    The constructor checks its values.

    Attributes:
        name: The names in English and Chinese. Both are set, and each holds more than
            whitespace.

    Raises:
        ValueError: A language of ``name`` is ``None``, is empty, or holds only whitespace.
    """

    name: BiText

    def __post_init__(self) -> None:
        """Checks the names.

        Raises:
            ValueError: A language of ``name`` is ``None`` or blank.
        """
        _check_both_names(self.name)


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
