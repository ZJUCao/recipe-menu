"""Tests of F03 for the readers together, on the example data and random files (T79 to T86)."""

import random
from pathlib import Path

from f03_support import (
    CATALOG_FILE,
    EN,
    M_ITEM_NOT_A_TEXT,
    M_MISSING_BRACE,
    M_MISSING_BRACKET,
    PANTRY_FILE,
    ZH,
    at_ingredient,
    at_item,
    at_line,
    check_problems,
    edit_ingredients,
    ing,
    m_dup_en,
    m_unknown_category,
    m_unknown_ingredient,
    put_bytes,
    write_pantry,
)
from recipe_menu.catalog import Catalog, Pantry, read_catalog, read_pantry
from recipe_menu.datafile import DataFolder, Problem, Severity, read_toml

SIX = ("produce", "meat", "eggs", "staples", "seasonings", "other")


def names(pantry: Pantry | None) -> set[str | None]:
    """Gives the English names of the ingredients of a pantry."""
    assert pantry is not None
    return {ingredient.name.en for ingredient in pantry.ingredients}


def test_f03_t79_a_comma_deleted_in_the_pantry_gives_the_f07_syntax_problem(
    example_folder: DataFolder,
) -> None:
    """The catalog is read, and the pantry gives the one problem at line 2."""
    text = example_folder.pantry.read_text(encoding="utf-8")
    assert '"盐", "糖"' in text
    example_folder.pantry.write_text(
        text.replace('"盐", "糖"', '"盐" "糖"'), encoding="utf-8", newline="\n"
    )
    catalog, problems = read_catalog(example_folder)
    assert isinstance(catalog, Catalog)
    assert problems == ()
    pantry, problems = read_pantry(example_folder, catalog)
    assert pantry is None
    check_problems(problems, PANTRY_FILE, [(at_line(2), M_MISSING_BRACKET)])


def test_f03_t80_the_problems_of_scenario_v0_1_s07_at_the_readers(
    example_folder: DataFolder,
) -> None:
    """A duplicate name and an unknown category in the catalog, and an unknown pantry name."""
    edit_ingredients(
        example_folder,
        added=[ing("芥兰", "Broccoli"), ing("香菜", "Coriander", "meats")],
    )
    write_pantry(example_folder, {3: '"sesame oil"'})
    catalog, problems = read_catalog(example_folder)
    assert catalog is not None
    assert len(catalog.ingredients) == 22
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(23), m_dup_en("Broccoli", at_ingredient(3))),
            (at_ingredient(24), m_unknown_category("meats", *SIX)),
        ],
    )
    pantry, problems = read_pantry(example_folder, catalog)
    assert names(pantry) == {"Cooking oil", "Salt", "Soy sauce", "Sichuan pepper"}
    check_problems(problems, PANTRY_FILE, [(at_item(3), m_unknown_ingredient("sesame oil"))])


def test_f03_t81_a_catalog_that_cannot_be_read_does_not_hide_the_mistakes_of_the_pantry(
    example_folder: DataFolder,
) -> None:
    """``read_pantry`` with ``None`` reports the pantry's own mistakes, and only those."""
    broken = '{ zh = "番茄" en = "Tomato", category = "produce" }'
    edit_ingredients(example_folder, {1: broken})
    catalog, problems = read_catalog(example_folder)
    assert catalog is None
    check_problems(problems, CATALOG_FILE, [(at_line(11), M_MISSING_BRACE)])
    assert read_pantry(example_folder, catalog) == (None, ())
    write_pantry(example_folder, {3: "3"})
    pantry, problems = read_pantry(example_folder, None)
    assert pantry is None
    check_problems(problems, PANTRY_FILE, [(at_item(3), M_ITEM_NOT_A_TEXT)])


def test_f03_t82_the_pantry_finds_names_only_in_the_catalog_that_was_kept(
    example_folder: DataFolder,
) -> None:
    """An ingredient that the catalog skips is unknown in the pantry."""
    edit_ingredients(example_folder, {15: '{ zh = "盐", en = "Salt", category = "seasoning" }'})
    catalog, problems = read_catalog(example_folder)
    assert catalog is not None
    assert len(catalog.ingredients) == 21
    check_problems(
        problems, CATALOG_FILE, [(at_ingredient(15), m_unknown_category("seasoning", *SIX))]
    )
    pantry, problems = read_pantry(example_folder, catalog)
    assert names(pantry) == {"Cooking oil", "Sugar", "Soy sauce", "Sichuan pepper"}
    check_problems(problems, PANTRY_FILE, [(at_item(2), m_unknown_ingredient("盐"))])


def test_f03_t83_files_with_a_byte_order_mark_and_crlf_read_the_same(
    example_folder: DataFolder,
) -> None:
    """The settings, the catalog, and the pantry give equal results in both rounds."""
    folder = example_folder

    def read_all() -> tuple[object, object, object]:
        """Reads the three files and checks that no reader gives a problem."""
        settings = read_toml(folder, folder.settings)
        catalog, catalog_problems = read_catalog(folder)
        pantry, pantry_problems = read_pantry(folder, catalog)
        assert isinstance(settings, dict)
        assert isinstance(catalog, Catalog)
        assert isinstance(pantry, Pantry)
        assert catalog_problems == ()
        assert pantry_problems == ()
        return settings, catalog, pantry

    first = read_all()
    for path in (folder.settings, folder.catalog, folder.pantry):
        data = path.read_bytes()
        put_bytes(path, b"\xef\xbb\xbf" + data.replace(b"\n", b"\r\n"))
    assert read_all() == first


def test_f03_t84_lookups_in_the_catalog_that_read_catalog_gives(
    example_folder: DataFolder,
) -> None:
    """Names from the prototypes find the catalog's own objects."""
    catalog, _ = read_catalog(example_folder)
    assert catalog is not None
    ingredients = catalog.ingredients
    found = [
        catalog.find_ingredient(name)
        for name in [
            "郫县豆瓣酱",
            "doubanjiang",
            "SICHUAN PEPPER",
            " Choy sum ",
            "choy  sum",
            "豆瓣酱",
        ]
    ]
    wanted = [ingredients[18], ingredients[18], ingredients[19], ingredients[1], None, None]
    for result, want in zip(found, wanted, strict=True):
        assert result is want
    tags = [catalog.find_tag(name) for name in ["快手", "Home-Style", "辣", "breakfast"]]
    wanted_tags = [catalog.tags[0], catalog.tags[1], catalog.tags[3], None]
    for result, want in zip(tags, wanted_tags, strict=True):
        assert result is want
    assert catalog.find_ingredient("quick") is None
    assert catalog.find_tag("番茄") is None


def snapshot(root: Path) -> tuple[dict[Path, bytes], set[Path]]:
    """Records the bytes of every file and the path of every folder under ``root``."""
    files = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    folders = {p.relative_to(root) for p in root.rglob("*") if p.is_dir()}
    return files, folders


def read_everything(folder: DataFolder) -> None:
    """Calls every reader of F03 on the folder."""
    for path in (folder.settings, folder.catalog, folder.pantry, folder.recipe_file("tomato-egg")):
        read_toml(folder, path)
    catalog, _ = read_catalog(folder)
    read_pantry(folder, catalog)
    read_pantry(folder, None)


def test_f03_t85_reading_writes_nothing(example_folder: DataFolder) -> None:
    """The data folder holds the same files with the same bytes after each round of reads."""
    before = snapshot(example_folder.root)
    read_everything(example_folder)
    assert snapshot(example_folder.root) == before
    text = example_folder.pantry.read_text(encoding="utf-8")
    example_folder.pantry.write_text(
        text.replace('"盐", "糖"', '"盐" "糖"'), encoding="utf-8", newline="\n"
    )
    before = snapshot(example_folder.root)
    read_everything(example_folder)
    assert snapshot(example_folder.root) == before


# ---------------------------------------------------------------- F03-T86: random files

KEYS = ['"produce"', '"Produce"', '" meat "', '"x"', '""', '"\u3000"', "3", "true", '["a"]']
NAMES = [
    '"番茄"',
    '"Tomato"',
    '"tomato"',
    '" Tomato\u3000"',
    '"葱"',
    '"Scallion"',
    '"\u212aale"',
    '"Kale"',
    '""',
    '" "',
    "3",
    "false",
    "[]",
]
CATEGORIES = ['"produce"', '"PRODUCE"', '"meat"', '"meats"', '""', "1"]
UNITS = ['"根"', '"cups"', '""', '"\u3000"', "2", '["个"]']
PANTRY_ITEMS = ['"番茄"', '"tomato"', '"Scallion"', '"sesame oil"', '""', '" "', "3", '["盐"]']
POOLS = {
    "key": KEYS,
    "zh": NAMES,
    "en": NAMES,
    "category": CATEGORIES,
    "unit": UNITS,
}
KINDS = {
    "categories": ("key", "zh", "en"),
    "ingredients": ("zh", "en", "category", "unit"),
    "tags": ("zh", "en"),
}
MAX_ITEMS = {"categories": 5, "ingredients": 8, "tags": 4}


def random_item(rng: random.Random, keys: tuple[str, ...]) -> str:
    """Writes one item: the number 7, or a table with some keys missing."""
    if rng.randrange(10) == 0:
        return "7"
    parts = [f"{key} = {rng.choice(POOLS[key])}" for key in keys if rng.randrange(6) != 0]
    if rng.randrange(8) == 0:
        parts.append("extra = 1")
    return "{ " + ", ".join(parts) + " }" if parts else "{}"


def random_catalog(rng: random.Random) -> tuple[str, dict[str, int]]:
    """Writes a catalog file, and gives the number of items of each list that is a list."""
    lines: list[str] = []
    counts: dict[str, int] = {}
    for name, keys in KINDS.items():
        shape = rng.randrange(20)
        if shape == 0:
            continue
        if shape == 1:
            lines.append(f'{name} = "x"')
            continue
        items = [random_item(rng, keys) for _ in range(rng.randint(0, MAX_ITEMS[name]))]
        counts[name] = len(items)
        body = "".join(f"  {item},\n" for item in items)
        lines.append(f"{name} = [\n{body}]" if items else f"{name} = []")
    return "\n".join(lines) + "\n", counts


def random_pantry(rng: random.Random) -> str:
    """Writes a pantry file of 0 to 6 items, and sometimes an unknown key."""
    items = [rng.choice(PANTRY_ITEMS) for _ in range(rng.randint(0, 6))]
    text = f"pantry = [{', '.join(items)}]\n"
    return text + ("items = []\n" if rng.randrange(10) == 0 else "")


def check_reader_problems(problems: tuple[Problem, ...], file: Path) -> None:
    """Checks the severity, the file, and the two texts of each problem."""
    for problem in problems:
        assert problem.severity is Severity.ERROR
        assert problem.file == file
        assert isinstance(problem.text(EN), str)
        assert isinstance(problem.text(ZH), str)


def check_stripped(catalog: Catalog) -> None:
    """Checks that each key and each name that is set equals its ``strip()``."""
    names_set = [category.name for category in catalog.categories]
    names_set += [item.name for item in (*catalog.ingredients, *catalog.tags)]
    for name in names_set:
        for text in (name.en, name.zh):
            assert text is None or text == text.strip()
    for category in catalog.categories:
        assert category.key == category.key.strip()


def test_f03_t86_random_files_never_raise_and_give_catalogs_that_meet_the_rules(
    folder: DataFolder,
) -> None:
    """500 random pairs of files give problems and never an exception."""
    rng = random.Random(20261111)  # noqa: S311 - a fixed seed, no security
    for _ in range(500):
        catalog_text, counts = random_catalog(rng)
        put_bytes(folder.catalog, catalog_text.encode("utf-8"))
        put_bytes(folder.pantry, random_pantry(rng).encode("utf-8"))
        catalog, c = read_catalog(folder)
        assert isinstance(catalog, Catalog)
        pantry, p = read_pantry(folder, catalog)
        assert isinstance(pantry, Pantry)
        check_reader_problems(c, CATALOG_FILE)
        check_reader_problems(p, PANTRY_FILE)
        for ingredient in catalog.ingredients:
            assert any(ingredient.category is category for category in catalog.categories)
        for ingredient in pantry.ingredients:
            assert any(ingredient is kept for kept in catalog.ingredients)
        check_stripped(catalog)
        if not c:
            kept = {
                "categories": len(catalog.categories),
                "ingredients": len(catalog.ingredients),
                "tags": len(catalog.tags),
            }
            assert kept == counts
        assert read_catalog(folder) == (catalog, c)
        assert read_pantry(folder, catalog) == (pantry, p)
