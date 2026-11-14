"""Matching: which recipes hold every word, and where each word appears."""

from collections.abc import Sequence
from dataclasses import dataclass

from recipe_menu.catalog import Catalog, Ingredient, Tag, matching_form
from recipe_menu.lang import Lang
from recipe_menu.recipes import Recipe

# The places of a word, as indexes into the places in the order name, ingredient, tag.
NAME, INGREDIENT, TAG = 0, 1, 2


@dataclass(frozen=True, slots=True)
class WordHits:
    """What the catalog holds for one word, built once per run.

    Attributes:
        form: The matching form of the word.
        ingredients: The catalog's ingredients with a name that holds the word.
        tags: The catalog's tags with a name that holds the word.
    """

    form: str
    ingredients: frozenset[Ingredient]
    tags: frozenset[Tag]


def has_empty_word(words: Sequence[str]) -> bool:
    """Tells whether a word has nothing in it.

    Args:
        words: The words as typed.

    Returns:
        True when the matching form of a word is empty.
    """
    return any(not matching_form(word) for word in words)


def word_hits(catalog: Catalog, words: Sequence[str]) -> tuple[WordHits, ...]:
    """Finds, for each word, the catalog's ingredients and tags that hold it.

    Args:
        catalog: The catalog.
        words: The words as typed, each with a matching form that is not empty.

    Returns:
        One ``WordHits`` for each word, in order.
    """
    # Both names of a catalog value are set, so ``get`` gives each one as written.
    ingredient_forms = [
        (i, matching_form(i.name.get(Lang.EN)), matching_form(i.name.get(Lang.ZH)))
        for i in catalog.ingredients
    ]
    tag_forms = [
        (t, matching_form(t.name.get(Lang.EN)), matching_form(t.name.get(Lang.ZH)))
        for t in catalog.tags
    ]
    hits = []
    for word in words:
        form = matching_form(word)
        ingredients = frozenset(i for i, en, zh in ingredient_forms if form in en or form in zh)
        tags = frozenset(t for t, en, zh in tag_forms if form in en or form in zh)
        hits.append(WordHits(form, ingredients, tags))
    return tuple(hits)


def _name_forms(recipe: Recipe) -> tuple[str, ...]:
    """Builds the matching forms of the names that a recipe has.

    Args:
        recipe: The recipe.

    Returns:
        The matching forms of ``name.en`` and ``name.zh``, each when it is not ``None``.
    """
    names = (recipe.name.en, recipe.name.zh)
    return tuple(matching_form(name) for name in names if name is not None)


def recipe_places(recipe: Recipe, hits: Sequence[WordHits]) -> tuple[int, ...] | None:
    """Finds where the words appear in a recipe.

    Args:
        recipe: The recipe.
        hits: The ``WordHits`` of every word.

    Returns:
        ``None`` when a word has no place in the recipe. Otherwise each place where at least one
        word appears, once, in the order name, ingredient, tag.
    """
    forms = _name_forms(recipe)
    found: set[int] = set()
    for hit in hits:
        places = set()
        if any(hit.form in form for form in forms):
            places.add(NAME)
        if any(line.ingredient in hit.ingredients for line in recipe.ingredients):
            places.add(INGREDIENT)
        if any(tag in hit.tags for tag in recipe.tags):
            places.add(TAG)
        if not places:
            return None
        found |= places
    return tuple(sorted(found))
