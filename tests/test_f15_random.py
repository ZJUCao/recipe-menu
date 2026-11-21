"""Test of F15 for random answers: the saved file reads back as the answers (T28)."""

import string
from pathlib import Path
from random import Random
from typing import NamedTuple

from f04_support import NAME, STEPS, check_problems, warn
from f05_support import make_home
from f05_texts import lines_text
from f07_texts import P_NAME, Prob
from f15_support import add, answers
from f15_texts import (
    block,
    no_en_name,
    no_en_steps,
    no_zh_name,
    no_zh_steps,
    recipe_path,
    saved,
    saved_with_problems,
)
from recipe_menu.catalog import Catalog, Ingredient, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.recipes import read_recipe
from recipe_menu.units import parse_quantity

CORE = [
    *string.ascii_letters,
    *string.digits,
    *"中文菜谱番茄",
    '"',
    "\\",
    "'",
    "#",
    "=",
    "[",
    "]",
    "{",
    "}",
    "\U0001f35a",
]
INNER = [" ", "\t", "\x00", "\x7f", "\u00a0", "\u2028", "\u3000"]
PADS = [" ", "\t", "\u3000"]
SEPARATORS = [",", "，", "、"]
UNITS = [" g", "g", " kg", " ml"]
SPECIAL = ["适量", "to taste", "TO taste"]


class Case(NamedTuple):
    """The random answers of one run, and what each of them should give.

    Attributes:
        recipe_id: The ID, such as ``random-007``.
        names: The Chinese and the English name, or ``None`` for an empty answer.
        servings: The answer to question 4.
        tags: The parts of the answer to question 5, each by a name of a tag.
        joiner: The comma, with spaces, that joins the parts.
        lines: The ingredient lines, as the name and the quantity that make each of them.
        zh_steps: The Chinese steps.
        en_steps: The English steps.
    """

    recipe_id: str
    names: tuple[str | None, str | None]
    servings: str
    tags: list[str]
    joiner: str
    lines: list[tuple[str, str]]
    zh_steps: list[str]
    en_steps: list[str]


def _text(rng: Random) -> str:
    """Gives a text of 1 to 12 characters with padding of spaces, tabs, or U+3000 at both ends."""
    size = rng.randint(1, 12)
    middle = [rng.choice(CORE + INNER) for _ in range(size)]
    middle[0], middle[-1] = rng.choice(CORE), rng.choice(CORE)
    left, right = rng.choice(PADS) * rng.randint(1, 2), rng.choice(PADS) * rng.randint(1, 2)
    return left + "".join(middle) + right


def _random_case(rng: Random, number: int, catalog: Catalog) -> Case:
    """Builds the random answers of run ``number`` from the generator."""
    zh_name = None if rng.random() < 0.25 else _text(rng)
    en_name = None if rng.random() < 0.25 else _text(rng)
    if zh_name is None and en_name is None:
        en_name = _text(rng)
    zh_steps = [_text(rng) for _ in range(rng.randint(0, 3) if rng.random() < 0.75 else 0)]
    en_steps = [_text(rng) for _ in range(rng.randint(0, 3) if rng.random() < 0.75 else 0)]
    if not zh_steps and not en_steps:
        en_steps = [_text(rng)]
    servings = "" if rng.random() < 0.3 else "0" * rng.randint(0, 2) + str(rng.randint(1, 100))
    chosen = rng.sample(catalog.tags, rng.randint(0, 3))
    tags = [_case_of(rng, rng.choice([tag.name.en or "", tag.name.zh or ""])) for tag in chosen]
    joiner = rng.choice(SEPARATORS) + " " * rng.randint(0, 2)
    count = rng.randint(0, 5)
    lines = [_ingredient_line(rng, rng.choice(catalog.ingredients)) for _ in range(count)]
    names = (zh_name, en_name)
    return Case(f"random-{number:03d}", names, servings, tags, joiner, lines, zh_steps, en_steps)


def _case_of(rng: Random, text: str) -> str:
    """Gives the text with a random case for each of the letters A to Z."""
    return "".join(ch.upper() if rng.random() < 0.5 else ch.lower() for ch in text)


def _ingredient_line(rng: Random, ingredient: Ingredient) -> tuple[str, str]:
    """Gives the name and the quantity of one ingredient line."""
    name = _case_of(rng, rng.choice([ingredient.name.en or "", ingredient.name.zh or ""]))
    if rng.random() < 0.2:
        return name, rng.choice(SPECIAL)
    if ingredient.unit is not None:
        return name, str(rng.randint(1, 999))
    return name, rng.choice([str(rng.randint(1, 999)), "1.5"]) + rng.choice(UNITS)


def _typed(case: Case) -> list[str]:
    """Gives the answers of the case, in the order of the questions."""
    zh_name, en_name = case.names
    return answers(
        case.recipe_id,
        zh_name=zh_name or "",
        en_name=en_name or "",
        servings=case.servings,
        tags=case.joiner.join(case.tags),
        ingredients=[f"{name} {quantity}" for name, quantity in case.lines],
        zh_steps=case.zh_steps,
        en_steps=case.en_steps,
    )


def _warnings(case: Case) -> list[Prob]:
    """Gives the warnings that the languages left out make, in the order name and steps."""
    found: list[Prob] = []
    if case.names[0] is None:
        found.append(no_zh_name(case.recipe_id))
    if case.names[1] is None:
        found.append(no_en_name(case.recipe_id))
    if not case.zh_steps:
        found.append(no_zh_steps(case.recipe_id))
    if not case.en_steps:
        found.append(no_en_steps(case.recipe_id))
    return found


def _check_output(folder: DataFolder, case: Case, result: tuple[int, str, str]) -> list[Prob]:
    """Checks the exit code, the streams, and the lines after saving. Gives the warnings."""
    code, out, err = result
    assert (code, err) == (0, ""), case
    path = recipe_path(folder, case.recipe_id)
    warnings = _warnings(case)
    if warnings:
        counts = saved_with_problems(path, 0, len(warnings))[0]
        tail = lines_text(counts, *block(False, *warnings))
    else:
        tail = lines_text(saved(path)[0])
    assert out.endswith(tail), case
    return warnings


def _strip(texts: list[str]) -> tuple[str, ...] | None:
    """Gives the texts without whitespace at both ends, or ``None`` for no text."""
    return tuple(text.strip() for text in texts) or None


def _check_recipe(folder: DataFolder, catalog: Catalog, case: Case) -> None:
    """Reads the file back and compares it with the answers."""
    recipe, problems = read_recipe(folder, catalog, case.recipe_id)
    warnings = _warnings(case)
    expected = []
    for problem in warnings:
        place = NAME if problem.place == P_NAME else STEPS
        expected.append(warn(place, problem.msg, problem.file))
    check_problems(problems, expected, case)
    assert recipe is not None, case
    zh_name, en_name = (None if name is None else name.strip() for name in case.names)
    assert (recipe.name.zh, recipe.name.en) == (zh_name, en_name), case
    assert (recipe.steps.zh, recipe.steps.en) == (_strip(case.zh_steps), _strip(case.en_steps))
    assert recipe.servings == (int(case.servings) if case.servings else 2), case
    found_tags = tuple(catalog.find_tag(part) for part in case.tags)
    assert recipe.tags == found_tags, case
    lines = []
    for name, quantity in case.lines:
        ingredient = catalog.find_ingredient(name)
        assert ingredient is not None, case
        lines.append((ingredient, parse_quantity(quantity, ingredient.unit)))
    assert [(line.ingredient, line.quantity) for line in recipe.ingredients] == lines, case
    data = folder.recipe_file(case.recipe_id).read_bytes()
    assert b"\r" not in data
    assert data.endswith(b"\n")
    assert not data.startswith(b"\xef\xbb\xbf")


def test_f15_t28_random_answers_read_back_through_read_recipe_as_typed(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """For 200 seeds: the saved file gives back the names, servings, tags, lines, and steps."""
    home = make_home(tmp_path)
    catalog, _ = read_catalog(example_folder)
    assert catalog is not None
    for number in range(200):
        case = _random_case(Random(number), number, catalog)  # noqa: S311 - a fixed seed
        result = add(home, example_folder, _typed(case))
        _check_output(example_folder, case, result)
        _check_recipe(example_folder, catalog, case)
