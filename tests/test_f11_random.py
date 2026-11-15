"""Test of F11 for random menus: the file of menu new and the table of menu show (T37).

The expected output of ``menu show`` is built here from the dishes that the test writes, by the
rules of design 2.4, with the dates of F06 and the table of F02 and no code of F11.
"""

import random
from datetime import timedelta
from pathlib import Path

from f03_support import write
from f05_support import TODAY, make_home
from f09_support import made
from f09_texts import out
from f11_support import SETS, empty_menus, held, meals_en, meals_of, meals_zh, menu_text, on
from f11_texts import DATES, HEADINGS, new, new_zh
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import Day, IsoWeek, short_date
from recipe_menu.settings import Meal
from recipe_menu.text import format_table

NAMES = {
    "tomato-egg": ("Tomato and egg stir-fry", "番茄炒蛋"),
    "choy-sum": ("Stir-fried choy sum", "清炒菜心"),
    "rice": ("Steamed rice", "米饭"),
    "mapo-tofu": ("Mapo tofu", "麻婆豆腐"),
    "tomato-egg-noodles": ("Tomato and egg noodles", "番茄鸡蛋面"),
    "cola-wings": ("Cola chicken wings", "可乐鸡翅"),
    "red-braised-pork": ("Red-braised pork belly", "红烧肉"),
}
WEEKS = ["2026-W01", "2026-W23", "2026-W47", "2026-W49", "2026-W53", "2027-W01"]
FOLDERS = 100
TIMES = "\u00d7"
DASH = "\u2014"

type Dishes = dict[tuple[Day, Meal], list[tuple[str, int]]]


def _iso(week: str) -> IsoWeek:
    """Turns a week such as ``2026-W47`` into an ``IsoWeek``."""
    year, number = week.split("-W")
    return IsoWeek(int(year), int(number))


def _dish(rng: random.Random, servings: int) -> tuple[str, str, int]:
    """Makes one dish: the recipe, its text in the file, and the servings that it shows."""
    recipe = rng.choice(sorted(NAMES))
    form = rng.choice(["id", "table", "servings"])
    if form == "id":
        return recipe, f'"{recipe}"', servings
    if form == "table":
        return recipe, f'{{ recipe = "{recipe}" }}', servings
    count = rng.randint(1, 12)
    return recipe, f'{{ recipe = "{recipe}", servings = {count} }}', count


def _file_and_dishes(
    rng: random.Random, week: str, order: list[str], servings: int
) -> tuple[str, Dishes]:
    """Makes the text of a menu file with random dishes, and the dishes of each slot."""
    lines = [f'week = "{week}"']
    dishes: Dishes = {}
    for day in Day:
        if rng.randrange(4) == 0:
            continue
        lines += ["", f"[{day.value}]"]
        for meal in rng.sample(order, len(order)):
            chosen = [_dish(rng, servings) for _ in range(rng.randint(0, 3))]
            lines.append(f"{meal} = [{', '.join(text for _, text, _ in chosen)}]")
            dishes[(day, Meal(meal))] = [(recipe, shown) for recipe, _, shown in chosen]
    return "".join(f"{line}\n" for line in lines), dishes


def _count_line(meals: int, dishes: int, zh: bool) -> str:
    """Writes the count line, or the line for a week with no dish."""
    if dishes == 0:
        return "这个菜单还没有菜。" if zh else "The menu has no dishes yet."
    if zh:
        return f"{meals} 餐，{dishes} 道菜。{TIMES}n：份数。"
    meal_word = "meal" if meals == 1 else "meals"
    dish_word = "dish" if dishes == 1 else "dishes"
    return f"{meals} {meal_word}, {dishes} {dish_word}. {TIMES}n: servings."


def _expected(week: str, lang: Lang, meals: list[Meal], dishes: Dishes) -> list[str]:
    """Builds the lines of ``menu show`` for the dishes, by the rules of design 2.4."""
    zh = lang is Lang.ZH
    index = 1 if zh else 0
    iso = _iso(week)
    rows = [[("Day", "日期")[index], *(HEADINGS[meal][index] for meal in meals)]]
    meal_count = dish_count = 0
    for day, when in zip(Day, iso.dates, strict=True):
        row = [short_date(when).get(lang)]
        for meal in meals:
            items = dishes.get((day, meal), [])
            meal_count += bool(items)
            dish_count += len(items)
            row.append("\n".join(f"{NAMES[r][index]} {TIMES}{n}" for r, n in items) or DASH)
        rows.append(row)
    dates = iso.date_range.get(lang)
    top = f"{week} 菜单，{dates}" if zh else f"Menu for {week}, {dates}"
    return [top, "", *format_table(rows), "", _count_line(meal_count, dish_count, zh)]


def _check_new(rng: random.Random, home: Path, root: Path, week: str, meals: list[Meal]) -> None:
    """Runs ``menu new`` on a random date and with a random value, and checks it."""
    choice = rng.choice([week, "this", None, "next"])
    today = rng.choice(_iso(week).dates)
    if choice == "next":
        today -= timedelta(days=7)
    zh = rng.choice([False, True])
    argv = ["menu", "new", *([choice] if choice else []), "--lang", "zh" if zh else "en"]
    file = root / "menus" / f"{week}.toml"
    english, chinese = DATES[week]
    lines = new_zh(file, chinese, meals_zh(meals)) if zh else new(file, english, meals_en(meals))
    assert on(home, root, today, *argv) == out(lines), (week, argv)
    assert held(file) == menu_text(week, meals), (week, argv)


def _check_show(
    rng: random.Random, home: Path, root: Path, week: str, settings: tuple[list[str], int]
) -> None:
    """Writes the file of the week with random dishes and checks ``menu show``."""
    order, servings = settings
    text, dishes = _file_and_dishes(rng, week, order, servings)
    write(root / "menus" / f"{week}.toml", text)
    lang = rng.choice([Lang.EN, Lang.ZH])
    result = on(home, root, TODAY, "menu", "show", week, "--lang", lang.value)
    assert result == out(_expected(week, lang, meals_of(order), dishes)), (week, text)


def test_f11_t37_random_menus_are_created_and_shown_by_the_rules_of_the_design(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """100 folders: the settings, the week, ``menu new`` with any value, and ``menu show``."""
    home = make_home(tmp_path)
    rng = random.Random(20261114)  # noqa: S311 - a fixed seed, no security
    for number in range(FOLDERS):
        order = list(rng.choice(SETS))
        rng.shuffle(order)
        servings = rng.randint(1, 5)
        week = rng.choice(WEEKS)
        names = ", ".join(f'"{meal}"' for meal in order)
        settings = f"meals = [{names}]\nservings = {servings}\n"
        root = made(
            example_folder,
            tmp_path,
            f"r{number}",
            empty_menus,
            lambda path, text=settings: write(path / "settings.toml", text),
        )
        _check_new(rng, home, root, week, meals_of(order))
        _check_show(rng, home, root, week, (order, servings))
