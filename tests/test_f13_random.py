"""Tests of F13 on random weeks of random catalogs, checked with the builders of the plan (T29)."""

import random
import string
import tomllib
from datetime import date, timedelta
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f09_support import WATER_FILE, made
from f09_texts import out
from f11_support import on
from f13_support import pristine, shop_file, shop_lines, shop_list
from f13_texts import no_dishes, no_dishes_zh
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek

SEED = 20261116
FOLDERS = 100
WEEKS = ["2026-W01", "2026-W23", "2026-W47", "2026-W49", "2026-W53", "2027-W01"]
POOL = string.ascii_letters + "\u00e9" + "番茄鸡蛋豆腐葱姜蒜米面油"
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
RECIPES = (
    "tomato-egg",
    "choy-sum",
    "rice",
    "mapo-tofu",
    "cola-wings",
    "tomato-egg-noodles",
    "red-braised-pork",
    "water",
)
EXAMPLE = tomllib.loads(
    (Path(__file__).parent / "data" / "example" / "catalog.toml").read_text("utf-8")
)


def _word(rng: random.Random, size: int) -> str:
    """Builds a word of 1 to ``size`` characters from the pool."""
    return "".join(rng.choice(POOL) for _ in range(rng.randint(1, size)))


def _names(
    rng: random.Random, heads: tuple[str, str], number: str, ingredient: bool
) -> tuple[str, str]:
    r"""Builds the Chinese and the English name of an item, as the TOML text of the two strings.

    The English name has 0 to 3 words. 1 time in 10, the name of an ingredient with a word has the
    TOML escape ``\n`` in place of the space before its last word.
    """
    zh = heads[0] + number + "".join(_word(rng, 4) for _ in range(rng.randint(0, 3)))
    words = [_word(rng, 6) for _ in range(rng.randint(0, 3))]
    en = heads[1] + number
    if ingredient and words and rng.random() < 0.1:
        return zh, en + "".join(f" {word}" for word in words[:-1]) + "\\n" + words[-1]
    return zh, en + "".join(f" {word}" for word in words)


def _write_catalog(rng: random.Random, root: Path) -> dict[str, str]:
    """Writes ``catalog.toml`` with new names, and gives the new Chinese name of each old one."""
    lines = ["categories = ["]
    for number, item in enumerate(EXAMPLE["categories"], 1):
        zh, en = _names(rng, ("类", "C"), str(number), False)
        lines.append(f'  {{ key = "{item["key"]}", zh = "{zh}", en = "{en}" }},')
    lines += ["]", "", "ingredients = ["]
    renamed = {}
    for number, item in enumerate(EXAMPLE["ingredients"], 1):
        zh, en = _names(rng, ("食", "I"), f"{number:02d}", True)
        renamed[item["zh"]] = zh
        unit = f', unit = "{item["unit"]}"' if "unit" in item else ""
        lines.append(f'  {{ zh = "{zh}", en = "{en}", category = "{item["category"]}"{unit} }},')
    lines += ["]", ""]
    lines.append("tags = [")
    lines += [f'  {{ zh = "{tag["zh"]}", en = "{tag["en"]}" }},' for tag in EXAMPLE["tags"]]
    lines.append("]")
    write(root / "catalog.toml", "\n".join(lines) + "\n")
    return renamed


def _rename_in_recipes(root: Path, renamed: dict[str, str]) -> None:
    """Replaces each ``item = "<old name>"`` of the recipes by the new Chinese name."""
    for path in sorted((root / "recipes").glob("*.toml")):
        text = path.read_text(encoding="utf-8")
        for old, new in renamed.items():
            text = text.replace(f'item = "{old}"', f'item = "{new}"')
        write(path, text)


def _dish(rng: random.Random) -> str:
    """Writes one dish of a random recipe in one of the three forms."""
    recipe = rng.choice(RECIPES)
    form = rng.randrange(3)
    if form == 0:
        return f'"{recipe}"'
    if form == 1:
        return f'{{ recipe = "{recipe}" }}'
    return f'{{ recipe = "{recipe}", servings = {rng.randint(1, 12)} }}'


def _write_menu(rng: random.Random, root: Path, week: str, meals: list[str]) -> None:
    """Writes ``menus/<week>.toml``: days left out, meals in a random order, 0 to 3 dishes."""
    lines = [f'week = "{week}"']
    bare = rng.random() < 0.1
    for day in DAYS:
        if rng.random() < 0.25:
            continue
        lines += ["", f"[{day}]"]
        for meal in rng.sample(meals, len(meals)):
            count = 0 if bare else rng.randint(0, 3)
            lines.append(f"{meal} = [{', '.join(_dish(rng) for _ in range(count))}]")
    write(root / "menus" / f"{week}.toml", "\n".join(lines) + "\n")


def _make_folder(
    rng: random.Random, source: DataFolder, tmp_path: Path, number: int
) -> tuple[Path, str]:
    """Makes random folder ``number``, a new example with the extra recipe ``water``."""
    root = made(source, tmp_path, f"random-{number}")
    write(root / "recipes" / "water.toml", WATER_FILE)
    renamed = _write_catalog(rng, root)
    _rename_in_recipes(root, renamed)
    items = [renamed[name] for name in renamed if rng.random() < 1 / 3]
    write(root / "pantry.toml", "pantry = [" + ", ".join(f'"{name}"' for name in items) + "]\n")
    meals = rng.sample(["breakfast", "lunch", "dinner"], rng.randint(1, 3))
    text = f'language = "en"\nmeals = [{", ".join(f"{meal!r}" for meal in meals)}]\n'
    write(root / "settings.toml", text.replace("'", '"') + f"servings = {rng.randint(1, 5)}\n")
    week = rng.choice(WEEKS)
    _write_menu(rng, root, week, meals)
    return root, week


def _run(rng: random.Random, home: Path, root: Path, week: str) -> None:
    """Runs ``shop`` twice in the folder and checks the output and the file of each run."""
    folder = DataFolder(root)
    parsed = IsoWeek.parse(week)
    assert parsed is not None, week
    shopping = shop_list(folder, parsed)
    file = folder.shopping_file(week)
    dates: list[date] = list(parsed.dates)
    value = rng.choice([[week], ["this"], [], ["next"]])
    today = rng.choice(dates)
    if value == ["next"]:
        today -= timedelta(days=7)
    for argv, day, lang in (
        (value, today, rng.choice(["en", "zh"])),
        ([week], dates[0], rng.choice(["en", "zh"])),
    ):
        language = Lang(lang)
        shown = on(home, root, day, "shop", *argv, "--lang", lang)
        if shopping.dish_count == 0:
            line = no_dishes(week) if language is Lang.EN else no_dishes_zh(week)
            assert shown == out([line]), (root, argv, lang)
            assert not folder.shopping.exists()
        else:
            assert shown == out(shop_lines(shopping, language, file)), (root, argv, lang)
            assert file.read_bytes() == shop_file(shopping, language), (root, argv, lang)
            assert [path.name for path in folder.shopping.iterdir()] == [f"{week}.md"]


def test_f13_t29_random_weeks_give_the_output_and_the_file_of_the_rules(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A hundred random folders: names of any width, any pantry, any meals, and any mix."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    rng = random.Random(SEED)  # noqa: S311 - a fixed seed, no security
    for number in range(FOLDERS):
        root, week = _make_folder(rng, source, tmp_path, number)
        _run(rng, home, root, week)
