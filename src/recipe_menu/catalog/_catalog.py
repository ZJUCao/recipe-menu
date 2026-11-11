"""The catalog: categories, ingredients, and tags, with a lookup by name."""

from collections.abc import Mapping
from dataclasses import dataclass, field

from recipe_menu.catalog._model import Category, Ingredient, Tag


@dataclass(frozen=True, slots=True)
class Catalog:
    """The categories, the ingredients, and the tags, in the file's order.

    Two catalogs are equal when their three tuples are equal, and a ``Catalog`` is hashable. The
    constructor builds an index of the names, so a lookup takes the same time whatever the size
    of the catalog. The index is internal: it is not compared, hashed, or printed. The
    implementation stores each index as a ``types.MappingProxyType``, so it cannot be changed.

    The constructor checks its values and builds the index. The mock leaves both out.

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

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

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

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError
