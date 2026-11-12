"""Tests of F04 for the readers together: nothing is written, and random recipe files (T57, T58)."""

import random
from pathlib import Path

import pytest

from f04_support import (
    EN,
    NAME,
    STEPS,
    ZH,
    dish_catalog,
    dish_text,
    example_catalog,
    ingredient_n,
    put_bytes,
    touch,
    write,
)
from recipe_menu.catalog import Catalog
from recipe_menu.datafile import DataFolder, Problem, Severity, list_toml_files
from recipe_menu.recipes import Recipe, list_recipe_ids, read_recipe, read_recipes

# ---------------------------------------------------------------- T57: reading writes nothing


def snapshot(root: Path) -> tuple[dict[str, bytes], set[str]]:
    """Records the bytes of every file and the path of every folder under a folder."""
    files: dict[str, bytes] = {}
    folders: set[str] = set()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            folders.add(relative)
        else:
            files[relative] = path.read_bytes()
    return files, folders


def read_everything(folder: DataFolder, catalog: Catalog) -> None:
    """Calls every reader of F04 in every way that a command does."""
    list_toml_files(folder, folder.recipes)
    list_toml_files(folder, folder.menus)
    ids, _ = list_recipe_ids(folder)
    for recipe_id in ids:
        read_recipe(folder, catalog, recipe_id)
        read_recipe(folder, None, recipe_id)
    read_recipes(folder, catalog)
    read_recipes(folder, None)


def test_f04_t57_reading_writes_nothing(example_folder: DataFolder) -> None:
    """The folder holds the same files with the same bytes, also after files with mistakes."""
    catalog = example_catalog(example_folder)
    before = snapshot(example_folder.root)
    read_everything(example_folder, catalog)
    assert snapshot(example_folder.root) == before
    touch(example_folder.recipes, "Rice Bowl.toml", "pancakes.TOML")
    write(example_folder.recipe_file("rice"), "servings = 0\n")
    put_bytes(example_folder.recipe_file("gbk"), dish_text().encode("gbk"))
    before = snapshot(example_folder.root)
    read_everything(example_folder, catalog)
    assert snapshot(example_folder.root) == before


# ---------------------------------------------------------------- T58: random recipe files

LANGUAGE_VALUES = [
    '"番茄炒蛋"',
    '"Tomato"',
    '" Tomato\u3000"',
    '""',
    '" "',
    '"\u3000"',
    "3",
    "true",
    "[]",
]
SERVINGS_VALUES = [
    "2",
    "1",
    "100",
    "0",
    "101",
    "-1",
    "999999999999999",
    "1000000000000000",
    '"2"',
    "2.5",
    "true",
    "0x" + "f" * 5000,
]
TAG_ITEMS = [
    '"快手"',
    '"quick"',
    '" QUICK "',
    '"家常"',
    '"breakfast"',
    '""',
    '" "',
    "3",
    '["快手"]',
]
ITEM_NAMES = ['"番茄"', '"Egg"', '"葱"', '"豆瓣酱"', '""', '" "', "3"]
AMOUNTS = [
    '"300 g"',
    '"3"',
    '"适量"',
    '"to taste"',
    '"1 cups"',
    '"0 g"',
    '"a few"',
    '"1234567890123456 g"',
    '""',
    "300",
]
STEP_LISTS = ["[]", '["番茄切块。"]', '["Cut.", "Fry."]', '[" "]', "[3]", '""', '" "', "3"]


def inline_table(parts: list[str]) -> str:
    """Writes an inline table from its ``key = value`` parts."""
    return "{ " + ", ".join(parts) + " }" if parts else "{}"


def language_table(rng: random.Random) -> str:
    """Writes a table of ``zh`` and ``en`` for a name or a note, each missing 1 time in 4."""
    parts = [f"{key} = {rng.choice(LANGUAGE_VALUES)}" for key in ("zh", "en") if rng.randrange(4)]
    if rng.randrange(8) == 0:
        parts.append('fr = "x"')
    return inline_table(parts)


def random_ingredient(rng: random.Random) -> str:
    """Writes one item of ``ingredients``: a number 1 time in 10, and otherwise a table."""
    if rng.randrange(10) == 0:
        return "7"
    parts = []
    if rng.randrange(6):
        parts.append(f"item = {rng.choice(ITEM_NAMES)}")
    if rng.randrange(6):
        parts.append(f"amount = {rng.choice(AMOUNTS)}")
    if rng.randrange(2) == 0:
        note = rng.choice(['"切块"', "{}", language_table(rng)])
        parts.append(f"note = {note}")
    if rng.randrange(8) == 0:
        parts.append('unit = "g"')
    return inline_table(parts)


def random_value(rng: random.Random, key: str) -> str:
    """Writes the value of one of the five keys at the top of a recipe file."""
    if key == "name":
        return language_table(rng) if rng.randrange(5) else rng.choice(['"番茄炒蛋"', "3", "[]"])
    if key == "servings":
        return rng.choice(SERVINGS_VALUES)
    if key == "tags":
        if rng.randrange(10) == 0:
            return '"快手"'
        return "[" + ", ".join(rng.choice(TAG_ITEMS) for _ in range(rng.randrange(5))) + "]"
    if rng.randrange(10) == 0:
        return '"番茄"'
    return "[" + ", ".join(random_ingredient(rng) for _ in range(rng.randrange(5))) + "]"


def random_recipe(rng: random.Random) -> str:
    """Writes a recipe file of random mixes of the checks of design 2.6."""
    top = [
        f"{key} = {random_value(rng, key)}"
        for key in ("name", "servings", "tags", "ingredients")
        if rng.randrange(8)
    ]
    if rng.randrange(8) == 0:
        top.append("extra = 1")
    tail: list[str] = []
    if rng.randrange(8):
        if rng.randrange(10) == 0:
            top.append('steps = "x"')
        else:
            tail = ["[steps]"]
            tail += [
                f"{key} = {rng.choice(STEP_LISTS)}" for key in ("zh", "en") if rng.randrange(4)
            ]
            if rng.randrange(8) == 0:
                tail.append('note = "x"')
    rng.shuffle(top)
    return "".join(f"{line}\n" for line in [*top, *tail])


def check_problems_of_a_file(problems: tuple[Problem, ...], label: object) -> None:
    """Checks the file, the severity, the texts, and the places of the warnings."""
    for problem in problems:
        assert str(problem.file) == str(Path("recipes", "dish.toml")), label
        assert problem.severity in (Severity.ERROR, Severity.WARNING), label
        assert isinstance(problem.text(EN), str), label
        assert isinstance(problem.text(ZH), str), label
        if problem.severity is Severity.WARNING:
            assert problem.place is not None, label
            words = problem.place.en.split()
            is_ingredient = words[0] == "ingredient" and problem.place == ingredient_n(
                int(words[1])
            )
            assert problem.place in (NAME, STEPS) or is_ingredient, label


def check_recipe(recipe: Recipe, label: object) -> None:
    """Checks that a recipe meets the constraints of design 2.3 and holds the catalog's objects."""
    assert recipe.id == "dish", label
    assert 1 <= recipe.servings <= 100, label
    texts = [recipe.name.en, recipe.name.zh]
    texts += [
        text for line in recipe.ingredients if line.note for text in (line.note.en, line.note.zh)
    ]
    for steps in (recipe.steps.en, recipe.steps.zh):
        texts += list(steps or ())
    assert all(text == text.strip() for text in texts if text is not None), label
    assert all(any(tag is known for known in dish_catalog.tags) for tag in recipe.tags), label
    assert len({id(tag) for tag in recipe.tags}) == len(recipe.tags), label
    for line in recipe.ingredients:
        assert any(line.ingredient is known for known in dish_catalog.ingredients), label


@pytest.mark.usefixtures("default_int_limit")
def test_f04_t58_random_recipe_files_give_problems_and_never_an_exception(
    folder: DataFolder,
) -> None:
    """500 files from a fixed seed. A recipe comes exactly when no problem is an error."""
    rng = random.Random(20261111)  # noqa: S311 - a fixed seed, no security
    for number in range(500):
        write(folder.recipe_file("dish"), random_recipe(rng))
        recipe, problems = read_recipe(folder, dish_catalog, "dish")
        no_catalog, no_catalog_problems = read_recipe(folder, None, "dish")
        recipes, listed = read_recipes(folder, dish_catalog)
        assert no_catalog is None, number
        for found in (problems, no_catalog_problems):
            check_problems_of_a_file(found, number)
        has_error = any(problem.severity is Severity.ERROR for problem in problems)
        assert (recipe is None) == has_error, number
        if recipe is not None:
            check_recipe(recipe, number)
        assert recipes == (() if recipe is None else (recipe,)), number
        assert listed == problems, number
        assert read_recipe(folder, dish_catalog, "dish") == (recipe, problems), number
