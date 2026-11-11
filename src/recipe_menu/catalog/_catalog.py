"""The catalog: categories, ingredients, and tags, with a lookup by name."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from recipe_menu.catalog._matching import matching_form
from recipe_menu.catalog._model import Category, Ingredient, Tag
from recipe_menu.lang import BiText


def _name_forms(name: BiText) -> set[str]:
    """Gives the matching forms of the two names of an ingredient or a tag.

    Args:
        name: Names with both languages set.

    Returns:
        The matching forms, as one set, so that two names that match each other count once.
    """
    return {matching_form(text) for text in (name.en, name.zh) if text is not None}


def _build_index[T: (Ingredient, Tag)](items: Iterable[T], kind: str) -> dict[str, T]:
    """Builds the index from the matching form of each name to its item.

    Args:
        items: Ingredients or tags.
        kind: The word for the items in the error message.

    Returns:
        The index.

    Raises:
        ValueError: Two items have names that match.
    """
    index: dict[str, T] = {}
    for item in items:
        forms = _name_forms(item.name)
        if not forms.isdisjoint(index):
            raise ValueError(f"two {kind} have names that match")
        index.update(dict.fromkeys(forms, item))
    return index


@dataclass(frozen=True, slots=True)
class Catalog:
    """The categories, the ingredients, and the tags, in the file's order.

    Two catalogs are equal when their three tuples are equal, and a ``Catalog`` is hashable. The
    constructor builds an index of the names, so a lookup takes the same time whatever the size
    of the catalog. The index is internal: it is not compared, hashed, or printed. Each
    index is stored as a ``dict``, typed as a read-only ``Mapping``.

    The constructor checks its values and builds the index.

    Two texts match when their matching forms are equal. The matching form of a text is the text
    without whitespace at both ends, as ``str.strip()`` removes it, with each ASCII capital
    letter from A to Z changed to its small letter. Look-alike letters stay as they are, no text
    is normalized, and a text whose matching form is empty matches nothing.

    Attributes:
        categories: The categories, in shopping order. No two keys match. Two categories may
            share a name, because nothing finds a category by its name.
        ingredients: The ingredients, in the catalog's order. Each one's ``category`` is in
            ``categories``. No two ingredients have matching names.
        tags: The tags, in the file's order. No two tags have matching names.

    Raises:
        ValueError: The keys of two categories match, the ``category`` of an ingredient is not
            in ``categories``, or two ingredients have matching names, or two tags do, in the
            same language or in different languages. The two names of one ingredient, or of one
            tag, may match each other.
    """

    categories: tuple[Category, ...]
    ingredients: tuple[Ingredient, ...]
    tags: tuple[Tag, ...]
    _ingredient_index: Mapping[str, Ingredient] = field(
        init=False, repr=False, compare=False, hash=False
    )
    _tag_index: Mapping[str, Tag] = field(init=False, repr=False, compare=False, hash=False)

    def __post_init__(self) -> None:
        """Checks the values and builds the two indexes.

        Raises:
            ValueError: The keys of two categories match, the ``category`` of an ingredient is
                not in ``categories``, or two ingredients have matching names, or two tags do.
        """
        keys = {matching_form(category.key) for category in self.categories}
        if len(keys) != len(self.categories):
            raise ValueError("the keys of two categories match")
        known = set(self.categories)
        if any(ingredient.category not in known for ingredient in self.ingredients):
            raise ValueError("the category of an ingredient is not in the catalog")
        object.__setattr__(self, "_ingredient_index", _build_index(self.ingredients, "ingredients"))
        object.__setattr__(self, "_tag_index", _build_index(self.tags, "tags"))

    def find_ingredient(self, name: str) -> Ingredient | None:
        """Finds an ingredient by its name in either language.

        Args:
            name: A name as written, such as ``Scallion`` or its Chinese name. Any string.

        Returns:
            The ingredient that has a name, in either language, whose matching form equals the
            matching form of ``name``, or ``None`` when no name matches. A tag is never given.
            The matching form is the text without whitespace at both ends (``str.strip()``),
            with each ASCII capital letter from A to Z changed to its small letter. Whitespace
            inside a text counts as written, case counts only for A to Z, look-alike letters
            such as U+212A and U+017F stay as they are, no text is normalized, and a text whose
            matching form is empty matches nothing.
        """
        return self._ingredient_index.get(matching_form(name))

    def find_tag(self, name: str) -> Tag | None:
        """Finds a tag by its name in either language.

        Args:
            name: A name as written, such as ``quick`` or its Chinese name. Any string.

        Returns:
            The tag that has a name, in either language, whose matching form equals the matching
            form of ``name``, or ``None`` when no name matches. An ingredient is never given.
            The matching form is the text without whitespace at both ends (``str.strip()``),
            with each ASCII capital letter from A to Z changed to its small letter. Whitespace
            inside a text counts as written, case counts only for A to Z, look-alike letters
            such as U+212A and U+017F stay as they are, no text is normalized, and a text whose
            matching form is empty matches nothing.
        """
        return self._tag_index.get(matching_form(name))
