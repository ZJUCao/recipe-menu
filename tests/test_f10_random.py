"""Test of F10 for random folders (T20): ``search`` against the rules of 2.2, in both languages.

The test builds the expected output from the recipes that it wrote, with its own matching form
(``str.strip()`` and then each A to Z changed to a to z), F02's ``format_table``, ``comma_list``,
and ``and_list``, and the texts of the headings, the places, and the count lines as literals. It
calls neither ``matching_form`` nor any code of F10.
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from f03_support import write
from f05_support import copy_example, make_home
from f05_texts import Result
from f09_support import at
from f09_texts import EN, ZH
from f10_texts import empty_word, found, none
from recipe_menu.catalog import Catalog, Ingredient, Tag, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import and_list, comma_list, format_table

POOL = ["a", "a-b", "b", "egg", "rice", "tomato-egg", "tomato-egg-noodles", "z"]
WORDS = ["Tomato", "egg", "stir-fry", "Pork", "belly", "Mapo", "tofu", "rice", "Noodles"]
HANS = "番茄炒蛋红烧肉面葱米"
NOWHERE = ["lamb", "dairy", "-x", "\u200b", "\uff34omato"]
EMPTY_WORDS = ["", " ", "\u3000"]
ENDS = [" ", "\t", "\u00a0", "\u3000"]
PLACES = (BiText("name", "名称"), BiText("ingredient", "食材"), BiText("tag", "标签"))
LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


@dataclass(frozen=True)
class Rec:
    """A recipe that the test wrote: its ID, name, tags, and ingredients.

    ``written_tags`` and ``written_items`` are the tags and the items as the test wrote them.
    """

    id: str
    name: BiText
    tags: tuple[Tag, ...]
    written_tags: tuple[str, ...]
    items: tuple[Ingredient, ...]
    written_items: tuple[str, ...]


# ---------------------------------------------------------------- the random folders


def _name(rng: random.Random) -> BiText:
    """Gives a name with an English text, a Chinese text, or both, with equal chances."""
    english = " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 3)))
    chinese = "".join(rng.choice(HANS) for _ in range(rng.randint(1, 4)))
    kind = rng.randrange(3)
    return BiText(en=english if kind != 1 else None, zh=chinese if kind != 0 else None)


def _recipe(rng: random.Random, recipe_id: str, catalog: Catalog) -> Rec:
    """Gives a random recipe with the ID: 0 to 3 tags and 0 to 4 ingredients, each by a name."""
    tags = tuple(rng.sample(catalog.tags, rng.randint(0, 3)))
    items = tuple(rng.sample(catalog.ingredients, rng.randint(0, 4)))
    written_tags = tuple(rng.choice((tag.name.en, tag.name.zh)) for tag in tags)
    written_items = tuple(rng.choice((item.name.en, item.name.zh)) for item in items)
    return Rec(recipe_id, _name(rng), tags, written_tags, items, written_items)


def _quoted(text: str) -> str:
    """Writes a text as a TOML string."""
    return '"' + text + '"'


def _file(rec: Rec) -> str:
    """Writes the file of a recipe."""
    names = (("zh", rec.name.zh), ("en", rec.name.en))
    parts = [f"{key} = {_quoted(text)}" for key, text in names if text is not None]
    tags = ", ".join(_quoted(name) for name in rec.written_tags)
    lines = [f"name = {{ {', '.join(parts)} }}", "servings = 2", f"tags = [{tags}]"]
    lines.append("ingredients = [")
    lines += [
        f"  {{ item = {_quoted(name)}, amount = {_quoted('适量')} }}," for name in rec.written_items
    ]
    lines += ["]", "[steps]", 'zh = ["煮。"]', 'en = ["Cook."]']
    return "".join(f"{line}\n" for line in lines)


def _folder(rng: random.Random, example: DataFolder, root: Path, catalog: Catalog) -> list[Rec]:
    """Makes a new example at ``root`` with 1 to 6 random recipes, and gives them in ID order."""
    copy_example(example, root)
    for path in (root / "recipes").glob("*.toml"):
        path.unlink()
    ids = sorted(rng.sample(POOL, rng.randint(1, 6)))
    recs = [_recipe(rng, recipe_id, catalog) for recipe_id in ids]
    for rec in recs:
        write(root / "recipes" / f"{rec.id}.toml", _file(rec))
    return recs


# ---------------------------------------------------------------- the random words


def _texts(recs: Sequence[Rec]) -> list[str]:
    """Gives the names of the recipes and both names of each ingredient and tag that they use."""
    texts: list[str] = []
    for rec in recs:
        texts += [text for text in (rec.name.en, rec.name.zh) if text is not None]
        for each in (*rec.items, *rec.tags):
            texts += [text for text in (each.name.en, each.name.zh) if text is not None]
    return texts


def _run(rng: random.Random, texts: Sequence[str]) -> str:
    """Gives 1 to 4 characters from a random place of a random text, in random case."""
    text = rng.choice(texts)
    length = min(rng.randint(1, 4), len(text))
    start = rng.randrange(len(text) - length + 1)
    chars = text[start : start + length]
    return "".join(
        (char.upper() if rng.randrange(2) else char.lower()) if char.isascii() else char
        for char in chars
    )


def _padded(rng: random.Random, word: str) -> str:
    """Gives the word, with a chance of 1 in 4 of whitespace at both ends."""
    if rng.randrange(4) != 0:
        return word
    return rng.choice(ENDS) + word + rng.choice(ENDS)


def _word(rng: random.Random, texts: Sequence[str], earlier: Sequence[str]) -> str:
    """Gives a run, a word found nowhere, an earlier word again, or an empty word."""
    roll = rng.randrange(20)
    if roll >= 19:
        return rng.choice(EMPTY_WORDS)
    if roll >= 15 and earlier:
        return rng.choice(earlier)
    if 13 <= roll < 15:
        return _padded(rng, rng.choice(NOWHERE))
    return _padded(rng, _run(rng, texts))


def _words(rng: random.Random, texts: Sequence[str]) -> list[str]:
    """Gives 1 to 3 words."""
    words: list[str] = []
    for _ in range(rng.randint(1, 3)):
        words.append(_word(rng, texts, words))
    return words


# ---------------------------------------------------------------- the expected output


def _form(text: str) -> str:
    """Gives the matching form of a text: without whitespace at its ends, A to Z as a to z."""
    return text.strip().translate(LOWER)


def _places(rec: Rec, forms: Sequence[str]) -> list[int] | None:
    """Gives the sorted indexes of the places that hold at least one of the words.

    Gives ``None`` when some word is in no place.
    """
    held = [
        [_form(text) for text in (rec.name.en, rec.name.zh) if text is not None],
        [
            _form(text)
            for item in rec.items
            for text in (item.name.en, item.name.zh)
            if text is not None
        ],
        [
            _form(text)
            for tag in rec.tags
            for text in (tag.name.en, tag.name.zh)
            if text is not None
        ],
    ]
    found_in: set[int] = set()
    for form in forms:
        where = {index for index, texts in enumerate(held) if any(form in text for text in texts)}
        if not where:
            return None
        found_in |= where
    return sorted(found_in)


def _count_line(count: int, words: Sequence[str], lang: Lang) -> str:
    """Writes the count line, or the line of no match when ``count`` is 0."""
    shown = list(dict.fromkeys(words))
    quoted = and_list(BiText(f'"{word}"', f"“{word}”") for word in shown).get(lang)
    together = "" if len(shown) == 1 else "同时"
    if lang is ZH:
        return (
            f"{count} 个菜谱{together}匹配{quoted}。"
            if count
            else f"没有菜谱{together}匹配{quoted}。"
        )
    if not count:
        return f"No recipe matches {quoted}."
    return f"{count} recipe matches {quoted}." if count == 1 else f"{count} recipes match {quoted}."


def _expected(recs: Sequence[Rec], words: Sequence[str], lang: Lang) -> Result:
    """Gives the result of ``search`` for the words, by the rules of 2.2."""
    forms = [_form(word) for word in words]
    if "" in forms:
        return empty_word(lang)
    heading = ["ID", "名称", "匹配于"] if lang is ZH else ["ID", "Name", "Matched in"]
    rows = []
    for rec in recs:
        places = _places(rec, forms)
        if places is not None:
            cell = comma_list(PLACES[index] for index in places).get(lang)
            rows.append([rec.id, rec.name.get(lang), cell])
    line = _count_line(len(rows), words, lang)
    return found(format_table([heading, *rows]), line) if rows else none(line)


def test_f10_t20_random_folders_and_words_give_the_lines_that_the_rules_give(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """100 random folders with 3 searches each, in both languages."""
    rng = random.Random(20261113)  # noqa: S311 - a fixed seed, no security
    home = make_home(tmp_path)
    catalog, _ = read_catalog(example_folder)
    assert catalog is not None
    for number in range(100):
        root = tmp_path / f"folder{number}"
        recs = _folder(rng, example_folder, root, catalog)
        texts = _texts(recs)
        for _ in range(3):
            lang = rng.choice((EN, ZH))
            words = _words(rng, texts)
            argv = ["search", *words, "--lang", "zh" if lang is ZH else "en"]
            assert at(home, root, *argv) == _expected(recs, words, lang), (root, argv)
