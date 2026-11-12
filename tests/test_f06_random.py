"""Test of F06 for read_week_menu on random menu files (T55)."""

import random
from collections.abc import Sequence

from f03_support import write
from f05_support import record
from f06_support import (
    AT_WEEK,
    MENU_PATH,
    at_day,
    at_dish,
    at_key,
    dinner_only,
    every_meal,
    example_settings,
    ids_of,
    make_menu,
)
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, WeekMenu, read_week_menu
from recipe_menu.settings import Meal, Settings

WEEK_VALUES = (
    '"2026-W47"',
    '" 2026-W47 "',
    '"2026-W48"',
    '"2026-w47"',
    '"next"',
    '""',
    '" "',
    "2026",
    "true",
    '["2026-W47"]',
)
ITEMS = (
    ('"rice"', "rice"),
    ('"tomato-egg"', "tomato-egg"),
    ('" choy-sum "', "choy-sum"),
    ('"Rice"', "Rice"),
    ('"tomato-eggs"', "tomato-eggs"),
    ('""', ""),
    ('" "', ""),
    ("3", None),
    ("true", None),
    ('["rice"]', None),
)
RECIPES = (
    ('"cola-wings"', "cola-wings"),
    ('" mapo-tofu "', "mapo-tofu"),
    ('"Rice"', "Rice"),
    ('""', ""),
    ("3", None),
)
SERVINGS = (
    ("1", 1),
    ("4", 4),
    ("100", 100),
    ("0", None),
    ("101", None),
    ("-1", None),
    ("999999999999999", None),
    ("1000000000000000", None),
    ('"4"', None),
    ("2.5", None),
    ("true", None),
    ("0x" + "f" * 5000, None),
)
TOP_VALUES = ("[]", '"x"', "3")
MEAL_KEYS = ("breakfast", "lunch", "dinner")
DAY_KEYS = (*MEAL_KEYS, "supper", "Dinner")

type Spec = tuple[str | None, int | None]
type Written = dict[tuple[Day, str], list[Spec]]


def _table(rng: random.Random) -> tuple[str, Spec]:
    """Makes a dish in braces and gives its text and what it says, in the file's keys."""
    parts: list[str] = []
    recipe: str | None = None
    servings: int | None = None
    if rng.randrange(6) != 0:
        text, recipe = rng.choice(RECIPES)
        parts.append(f"recipe = {text}")
    if rng.randrange(2) == 0:
        text, servings = rng.choice(SERVINGS)
        parts.append(f"servings = {text}")
    if rng.randrange(8) == 0:
        parts.append('note = "x"')
    rng.shuffle(parts)
    return ("{ " + ", ".join(parts) + " }" if parts else "{}"), (recipe, servings)


def _list(rng: random.Random) -> tuple[str, list[Spec]]:
    """Makes a list of 0 to 4 items and gives its text and what its items say."""
    texts: list[str] = []
    specs: list[Spec] = []
    for _ in range(rng.randint(0, 4)):
        if rng.randrange(3) == 0:
            text, spec = _table(rng)
        else:
            text, value = rng.choice(ITEMS)
            spec = (value, None)
        texts.append(text)
        specs.append(spec)
    return "[" + ", ".join(texts) + "]", specs


def _day_table(rng: random.Random, day: Day, written: Written) -> list[str]:
    """Makes the lines of a day table, and records the dishes of its meals in ``written``."""
    keys = [key for key in MEAL_KEYS if rng.randrange(3) != 0]
    if rng.randrange(6) == 0:
        keys.append("supper")
    if rng.randrange(10) == 0:
        keys.append("Dinner")
    rng.shuffle(keys)
    lines = [f"[{day.value}]"]
    for key in keys:
        if rng.randrange(10) != 0:
            text, specs = _list(rng)
            written[(day, key)] = specs
        else:
            text = rng.choice(('"rice"', "3"))
        lines.append(f"{key} = {text}")
    return lines


def make_file(rng: random.Random) -> tuple[str, Written]:
    """Makes the text of one random menu file and the dishes that it writes for each meal."""
    written: Written = {}
    head: list[str] = []
    tables: list[list[str]] = []
    if rng.randrange(8) != 0:
        head.append(f"week = {rng.choice(WEEK_VALUES)}")
    if rng.randrange(8) == 0:
        head.append("extra = 1")
    for day in Day:
        if rng.randrange(4) == 0:
            continue
        if rng.randrange(10) == 0:
            head.append(f"{day.value} = {rng.choice(TOP_VALUES)}")
        else:
            tables.append(_day_table(rng, day, written))
    if rng.randrange(10) == 0:
        tables.append(["[funday]"])
    rng.shuffle(head)
    rng.shuffle(tables)
    lines = [*head, *(line for table in tables for line in table)]
    return "".join(f"{line}\n" for line in lines), written


def _expected_menu(settings: Settings, written: Written) -> WeekMenu:
    """Builds the menu that a file without problems must give with the settings."""
    filled = {}
    for (day, key), specs in written.items():
        meal = Meal(key) if key in MEAL_KEYS else None
        if meal in settings.meals:
            filled[(day, meal)] = tuple(
                Dish(recipe or "", servings or settings.servings) for recipe, servings in specs
            )
    return make_menu(IsoWeek(2026, 47), settings.meals, filled)


def _places() -> tuple[set[BiText], dict[BiText, int]]:
    """Gives the places that a problem may have, and the index of the day of each."""
    days: dict[BiText, int] = {}
    for index, day in enumerate(Day):
        days[at_day(day.value)] = index
        for key in DAY_KEYS:
            days[at_key(day.value, key)] = index
        for key in MEAL_KEYS:
            for number in range(1, 5):
                days[at_dish(day.value, key, number)] = index
    return {AT_WEEK, *days}, days


def _check_problems(problems: Sequence[Problem], places: set[BiText], days: dict) -> None:
    """Checks the severity, the file, the texts, and the places of the problems."""
    indexes = []
    for problem in problems:
        assert problem.severity is Severity.ERROR
        assert str(problem.file) == str(MENU_PATH)
        assert isinstance(problem.text(Lang.EN), str)
        assert isinstance(problem.text(Lang.ZH), str)
        assert problem.place is None or problem.place in places, problem.place
        if problem.place in days:
            indexes.append(days[problem.place])
    assert indexes == sorted(indexes)


def _same_but_for_kind(many: Sequence[Problem], none: Sequence[Problem]) -> None:
    """Checks that two runs differ only where an unknown key became an unknown meal."""
    assert [problem.place for problem in many] == [problem.place for problem in none]
    for with_meals, without in zip(many, none, strict=True):
        en, zh = with_meals.text(Lang.EN), with_meals.text(Lang.ZH)
        if (en, zh) != (without.text(Lang.EN), without.text(Lang.ZH)):
            assert en.startswith('Unknown meal "')
            assert without.text(Lang.EN).startswith('Unknown key "')


def test_f06_t55_random_menu_files_give_problems_and_never_an_exception(
    example_folder: DataFolder, default_int_limit: None
) -> None:
    """500 files, each read with four settings and again with the first, in the same way."""
    example = example_folder
    rng = random.Random(20261115)  # noqa: S311
    ids = ids_of(example)
    menu_file = example.menu_file("2026-W47")
    others = {
        key: data for key, data in record(example.root).items() if key != "menus/2026-W47.toml"
    }
    places, days = _places()
    week = IsoWeek(2026, 47)
    for number in range(500):
        text, written = make_file(rng)
        write(menu_file, text)
        results = {}
        for name, settings in (
            ("settings", example_settings()),
            ("none", None),
            ("every", every_meal()),
            ("dinner", dinner_only()),
        ):
            menu, problems = read_week_menu(example, week, settings, ids)
            results[name] = (menu, problems)
            assert isinstance(problems, tuple), number
            _check_problems(problems, places, days)
            if settings is None:
                assert menu is None, number
            else:
                assert (menu is not None) == (problems == ()), (number, name)
                if menu is not None:
                    assert menu == _expected_menu(settings, written), (number, name)
        _same_but_for_kind(results["every"][1], results["none"][1])
        again = read_week_menu(example, week, example_settings(), ids)
        assert again == results["settings"], number
        assert menu_file.read_text(encoding="utf-8") == text
    after = {
        key: data for key, data in record(example.root).items() if key != "menus/2026-W47.toml"
    }
    assert after == others
