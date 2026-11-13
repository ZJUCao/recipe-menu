"""Test of F09 for random folders (T27): ``list`` and ``show`` against the rules of 2.2 and 2.4.

The test builds the expected lines from the recipes that it wrote, with F01's ``parse_quantity``,
``Quantity.scale``, and ``Quantity.to_text`` and F02's ``format_table``, ``display_width``, and
``comma_list``. It uses no code of F09.
"""

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from f03_support import write
from f05_support import copy_example, make_home
from f05_texts import Result
from f09_support import at
from f09_texts import BREAKFAST, BREAKFAST_ZH, EN, ZH, err, out, unknown_id
from recipe_menu.catalog import Catalog, Ingredient, Tag, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import comma_list, display_width, format_table
from recipe_menu.units import Quantity, parse_quantity

POOL = [
    "a",
    "a-b",
    "a0",
    "ab",
    "b-1",
    "0",
    "0-a",
    "9",
    "rice",
    "tomato-egg",
    "tomato-egg-noodles",
    "z",
]
WORDS = ["Tomato", "egg", "stir-fry", "A", "long", "pork", "Mapo"]
HANS = "番茄炒蛋红烧肉面"
UNITS = ["g", "kg", "斤", "两", "ml", "L", "tsp", "汤匙", "个", "stalks", "瓣", "slice", "块"]
UNITS += ["bunch", "罐", "pack"]
SERVINGS = (1, 2, 3, 4, 7, 100)


@dataclass(frozen=True)
class Line:
    """One ingredient line: the catalog ingredient, the name written, the amount, and the note."""

    ingredient: Ingredient
    written: str
    amount: str
    note: BiText | None


@dataclass(frozen=True)
class Rec:
    """A recipe that the test wrote: its values, and the names that its file writes."""

    id: str
    name: BiText
    servings: int
    tags: tuple[Tag, ...]
    written_tags: tuple[str, ...]
    lines: tuple[Line, ...]
    en_steps: tuple[str, ...] | None
    zh_steps: tuple[str, ...] | None

    def steps(self, lang: Lang) -> tuple[str, ...] | None:
        """Gives the steps of a language, or ``None`` when the recipe has none in it."""
        return self.en_steps if lang is Lang.EN else self.zh_steps


# ---------------------------------------------------------------- the random recipes


def _words(rng: random.Random) -> str:
    """Gives 1 to 3 English words, joined by spaces."""
    return " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 3)))


def _hans(rng: random.Random) -> str:
    """Gives 1 to 5 Chinese characters."""
    return "".join(rng.choice(HANS) for _ in range(rng.randint(1, 5)))


def _lined(rng: random.Random, make: Callable[[random.Random], str]) -> str:
    """Gives a text, with a chance of 1 in 4 of a line break and a second part."""
    text = make(rng)
    return f"{text}\n{make(rng)}" if rng.randrange(4) == 0 else text


def _bitext(
    rng: random.Random,
    make_en: Callable[[random.Random], str],
    make_zh: Callable[[random.Random], str],
) -> BiText:
    """Gives a text in English only, in Chinese only, or in both, with equal chances."""
    kind = rng.randrange(3)
    return BiText(en=make_en(rng) if kind != 1 else None, zh=make_zh(rng) if kind != 0 else None)


def _note(rng: random.Random) -> BiText | None:
    """Gives no note, an English note, a Chinese note, or both, each one word."""
    if rng.randrange(4) == 0:
        return None
    return _bitext(rng, lambda r: r.choice(WORDS), lambda r: _hans(r)[:2])


def _amount(rng: random.Random, ingredient: Ingredient) -> str:
    """Gives an amount that the ingredient accepts."""
    kinds = ["适量", "to taste", "whole", "decimal"] + (["bare"] if ingredient.unit else [])
    kind = rng.choice(kinds)
    if kind == "whole":
        return f"{rng.randint(1, 999)} {rng.choice(UNITS)}"
    if kind == "decimal":
        return f"{rng.randint(1, 999) / 10:.1f} {rng.choice(UNITS)}"
    if kind == "bare":
        return str(rng.randint(1, 999))
    return kind


def _steps(rng: random.Random, make: Callable[[random.Random], str]) -> tuple[str, ...]:
    """Gives 1 to 3 steps."""
    return tuple(make(rng) for _ in range(rng.randint(1, 3)))


def _recipe(rng: random.Random, recipe_id: str, catalog: Catalog) -> Rec:
    """Gives a random recipe with the ID."""
    tags = tuple(rng.sample(catalog.tags, rng.randint(0, 3)))
    written = tuple(rng.choice((tag.name.en, tag.name.zh)) for tag in tags)
    chosen = rng.sample(catalog.ingredients, rng.randint(0, 4))
    lines = tuple(
        Line(item, rng.choice((item.name.en, item.name.zh)), _amount(rng, item), _note(rng))
        for item in chosen
    )
    kind = rng.randrange(3)
    return Rec(
        recipe_id,
        _bitext(rng, lambda r: _lined(r, _words), lambda r: _lined(r, _hans)),
        rng.choice(SERVINGS),
        tags,
        written,
        lines,
        _steps(rng, _words) if kind != 1 else None,
        _steps(rng, _hans) if kind != 0 else None,
    )


def _quote(text: str) -> str:
    """Writes a text as a TOML string, with the escape of a line break for each one."""
    return '"' + text.replace("\n", "\\n") + '"'


def _table(text: BiText) -> str:
    """Writes a ``BiText`` as an inline table."""
    parts = [f"en = {_quote(text.en)}"] if text.en is not None else []
    if text.zh is not None:
        parts.append(f"zh = {_quote(text.zh)}")
    return "{ " + ", ".join(parts) + " }"


def _file(rec: Rec) -> str:
    """Writes the file of a recipe."""
    items = []
    for line in rec.lines:
        note = f", note = {_table(line.note)}" if line.note is not None else ""
        items.append(
            f"  {{ item = {_quote(line.written)}, amount = {_quote(line.amount)}{note} }},"
        )
    tags = ", ".join(_quote(tag) for tag in rec.written_tags)
    lines = [f"name = {_table(rec.name)}", f"servings = {rec.servings}", f"tags = [{tags}]"]
    lines += ["ingredients = [", *items, "]", "[steps]"]
    for key, steps in (("en", rec.en_steps), ("zh", rec.zh_steps)):
        if steps is not None:
            lines.append(f"{key} = [{', '.join(_quote(step) for step in steps)}]")
    return "".join(f"{line}\n" for line in lines)


def _write_recipes(rng: random.Random, root: Path, catalog: Catalog) -> list[Rec]:
    """Deletes the recipe files of a new example, writes 1 to 6 random ones, and gives them."""
    for path in (root / "recipes").glob("*.toml"):
        path.unlink()
    ids = sorted(rng.sample(POOL, rng.randint(1, 6)))
    recs = [_recipe(rng, recipe_id, catalog) for recipe_id in ids]
    for rec in recs:
        write(root / "recipes" / f"{rec.id}.toml", _file(rec))
    return recs


# ---------------------------------------------------------------- the expected lines


def _widths(rows: Sequence[Sequence[str]]) -> list[int]:
    """Gives the largest ``display_width`` of a line of each of the first three columns."""
    return [
        max(display_width(line) for row in rows for line in (row[column].splitlines() or [""]))
        for column in range(3)
    ]


def _count_line(count: int, tag: Tag | None, lang: Lang) -> str:
    """Writes the count line of ``list``."""
    zh = lang is Lang.ZH
    if tag is None:
        return f"共 {count} 个菜谱。" if zh else f"{count} recipe{'' if count == 1 else 's'}."
    name = tag.name.get(lang)
    if zh:
        return f"共 {count} 个菜谱带有标签“{name}”。"
    return (
        f'{count} recipe has the tag "{name}".'
        if count == 1
        else (f'{count} recipes have the tag "{name}".')
    )


def expected_list(recs: Sequence[Rec], lang: Lang, tag: Tag | None) -> list[str]:
    """Gives the lines of ``list`` for the recipes, in the order of their IDs."""
    zh = lang is Lang.ZH
    rows = [
        [
            rec.id,
            rec.name.get(lang),
            str(rec.servings),
            comma_list(item.name for item in rec.tags).get(lang),
        ]
        for rec in recs
    ]
    kept = [row for row, rec in zip(rows, recs, strict=True) if tag is None or tag in rec.tags]
    if not kept:
        name = tag.name.get(lang) if tag is not None else ""
        return [f"没有菜谱带有标签“{name}”。" if zh else f'No recipe has the tag "{name}".']
    heading = ["ID", "名称", "份数", "标签"] if zh else ["ID", "Name", "Servings", "Tags"]
    table = format_table([heading, *kept], min_widths=_widths(rows))
    return [*table, "", _count_line(len(kept), tag, lang)]


def _quantity(line: Line, factor: Fraction, lang: Lang) -> str:
    """Writes the amount of a line as ``parse_quantity``, ``scale``, and ``to_text`` give it."""
    quantity = parse_quantity(line.amount, line.ingredient.unit)
    assert isinstance(quantity, Quantity), line.amount
    return quantity.scale(factor).to_text(lang)


def _servings_line(rec: Rec, servings: int | None, lang: Lang) -> str:
    """Writes the servings line of ``show``."""
    zh = lang is Lang.ZH
    shown = str(rec.servings)
    if servings is not None and servings != rec.servings:
        shown = (
            f"{servings}（菜谱按 {rec.servings} 份写）"
            if zh
            else f"{servings} (the recipe makes {rec.servings})"
        )
    if not rec.tags:
        return f"份数：{shown}" if zh else f"Servings: {shown}"
    tags = comma_list(item.name for item in rec.tags).get(lang)
    return f"份数：{shown}   标签：{tags}" if zh else f"Servings: {shown}   Tags: {tags}"


def expected_show(rec: Rec, lang: Lang, servings: int | None) -> list[str]:
    """Gives the lines of ``show`` for a recipe, scaled to ``servings`` when it is not ``None``."""
    zh = lang is Lang.ZH
    other = Lang.EN if zh else Lang.ZH
    names = [name for name in (rec.name.exact(lang), rec.name.exact(other)) if name is not None]
    lines = ["  ".join(names), _servings_line(rec, servings, lang), ""]
    factor = Fraction(1) if servings is None else Fraction(servings, rec.servings)
    if rec.lines:
        rows = [
            [
                line.ingredient.name.get(lang),
                _quantity(line, factor, lang),
                line.note.get(lang) if line.note is not None else "",
            ]
            for line in rec.lines
        ]
        lines += ["食材" if zh else "Ingredients", *format_table(rows, indent=2), ""]
    own = rec.steps(lang)
    if own is not None:
        lines.append("步骤" if zh else "Steps")
    else:
        lines.append(
            "步骤（没有中文步骤，所以这里是英文步骤）"
            if zh
            else "Steps (no English steps, so these are the Chinese steps)"
        )
    steps = own if own is not None else rec.steps(other)
    assert steps is not None
    return [*lines, *(f"  {number}. {step}" for number, step in enumerate(steps, 1))]


# ---------------------------------------------------------------- the commands


def _tag_value(rng: random.Random, tag: Tag) -> str:
    """Gives a name of the tag in random case, with spaces at both ends with a chance of 1 in 2."""
    name = rng.choice((tag.name.en, tag.name.zh))
    assert name is not None
    value = "".join(char.upper() if rng.randrange(2) else char for char in name)
    return f" {value} " if rng.randrange(2) else value


def _check_list(
    rng: random.Random, home: Path, root: Path, recs: list[Rec], catalog: Catalog
) -> None:
    """Runs a random ``list`` line and compares it with the expected lines."""
    lang = rng.choice((EN, ZH))
    argv = ["list", "--lang", "zh" if lang is ZH else "en"]
    kind = rng.randrange(3)
    expected: Result
    if kind == 0:
        expected = out(expected_list(recs, lang, None))
    elif kind == 1:
        tag = rng.choice(catalog.tags)
        argv += ["--tag", _tag_value(rng, tag)]
        expected = out(expected_list(recs, lang, tag))
    else:
        argv += ["--tag", "breakfast"]
        expected = err(1, [BREAKFAST_ZH if lang is ZH else BREAKFAST])
    assert at(home, root, *argv) == expected, (root, argv)


def _check_show(rng: random.Random, home: Path, root: Path, recs: list[Rec]) -> None:
    """Runs a random ``show`` line and compares it with the expected lines."""
    lang = rng.choice((EN, ZH))
    unknown = rng.randrange(6) == 0
    rec = rng.choice(recs)
    argv = ["show", "zz" if unknown else rec.id, "--lang", "zh" if lang is ZH else "en"]
    servings = rng.choice((None, rec.servings, rng.randint(1, 100)))
    if servings is not None:
        argv += ["--servings", str(servings)]
    if unknown:
        assert at(home, root, *argv) == err(1, [unknown_id("zz", lang)]), (root, argv)
    else:
        assert at(home, root, *argv) == out(expected_show(rec, lang, servings)), (root, argv)


def test_f09_t27_random_folders_give_the_lines_that_the_rules_give(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """100 random folders: ``list`` and ``show`` in both languages, with and without options."""
    rng = random.Random(20261113)  # noqa: S311 - a fixed seed, no security
    home = make_home(tmp_path)
    catalog, _ = read_catalog(example_folder)
    assert catalog is not None
    for number in range(100):
        root = copy_example(example_folder, tmp_path / f"folder{number}")
        recs = _write_recipes(rng, root, catalog)
        for _ in range(3):
            _check_list(rng, home, root, recs, catalog)
            _check_show(rng, home, root, recs)
