"""Tests of F14 for the setting dishes: Settings, read_settings, and every command (T22-T24)."""

from pathlib import Path

import pytest

from f03_support import write
from f05_support import make_home
from f05_texts import (
    LANGUAGE,
    MEALS,
    SERVINGS,
    entry,
    language_not_en_or_zh,
    lines_text,
    not_a_list,
    servings_too_few,
    unknown_key,
    unknown_meal,
)
from f07_support import AFTER, check, expect, rep
from f07_texts import PORK
from f09_support import at, made
from f09_texts import LIST, out, stop
from f11_texts import SHOW_47
from f13_support import pristine
from f13_texts import shop_47
from f14_support import assert_settings_problems, with_dishes
from f14_texts import (
    DISHES,
    DISHES_NOT_1_TO_10,
    DISHES_NOT_A_TABLE,
    E_DISHES_TABLE,
    E_DISHES_ZERO,
    dishes_of,
)
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings, read_settings

NOT_1_TO_10 = [entry(dishes_of("dinner"), DISHES_NOT_1_TO_10)]
NOT_A_TABLE = [entry(DISHES, DISHES_NOT_A_TABLE)]


def test_f14_t22_settings_hold_the_dishes_of_each_meal_and_check_them() -> None:
    """The example of 3.1, ``dishes_for`` of each meal, equality and hash, and the wrong values."""
    defaults = Settings()
    assert defaults.dishes == (1, 1, 1)
    assert [defaults.dishes_for(meal) for meal in Meal] == [1, 1, 1]
    two = Settings(Lang.ZH, tuple(Meal), 3, (1, 1, 2))
    assert two.dishes_for(Meal.DINNER) == 2
    assert two.dishes_for(Meal.BREAKFAST) == 1
    assert Settings(Lang.EN) == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2, (1, 1, 1))
    three = Settings(dishes=(3, 5, 7))
    assert [three.dishes_for(meal) for meal in Meal] == [3, 5, 7]
    lunch = Settings(Lang.EN, (Meal.LUNCH,), 2, (4, 1, 1))
    assert (lunch.dishes_for(Meal.BREAKFAST), lunch.dishes_for(Meal.LUNCH)) == (4, 1)
    for numbers in ((1, 1, 10), (10, 10, 10)):
        assert Settings(dishes=numbers).dishes == numbers
    same, other = Settings(dishes=(1, 1, 1)), Settings(dishes=(1, 1, 2))
    assert defaults == same
    assert hash(defaults) == hash(same)
    assert len({defaults, same, other}) == 2
    assert other != defaults
    for numbers in ((1, 1), (1, 0, 1), (1, 1, 11), (0, 1, 1), (1, 1, 1, 1), (), (1, -1, 1)):
        with pytest.raises(ValueError):
            Settings(dishes=numbers)
    for wrong in ([1, 1, 2], (1, 1, True), (1, 1, 2.0), None, (1, "2", 1), (1, 1, None)):
        with pytest.raises(TypeError):
            Settings(dishes=wrong)
    with pytest.raises(TypeError):
        Settings(dishes=(False, 1, 1))


def _lines_of_the_example(example: DataFolder) -> None:
    """The lines of the example of 3.2 that read settings, with the checks of the key list."""
    lines = ['meals = ["breakfast", "lunch", "dinner"]', "dishes = { dinner = 2 }"]
    write(example.settings, "\n".join(lines) + "\n")
    assert read_settings(example) == (Settings(None, tuple(Meal), 2, (1, 1, 2)), ())
    write(example.settings, "[dishes]\nlunch = 3\n")
    assert read_settings(example) == (Settings(dishes=(1, 3, 1)), ())
    lines = ["dishes = { dinner = 0, supper = 2, lunch = true }", "colour = 1"]
    write(example.settings, "\n".join(lines) + "\n")
    settings, problems = read_settings(example)
    assert settings is None
    assert_settings_problems(
        problems,
        [
            entry(dishes_of("dinner"), DISHES_NOT_1_TO_10),
            entry(DISHES, unknown_meal("supper")),
            entry(dishes_of("lunch"), DISHES_NOT_1_TO_10),
            entry(None, unknown_key("colour")),
        ],
    )
    write(example.settings, "dishes = []\n")
    assert_settings_problems(read_settings(example)[1], NOT_A_TABLE)


def _read(folder: DataFolder, *lines: str) -> tuple[Settings | None, list[Problem]]:
    """Writes the lines as ``settings.toml`` and reads them."""
    write(folder.settings, lines_text(*lines))
    settings, problems = read_settings(folder)
    return settings, list(problems)


def _check_values(folder: DataFolder) -> None:
    """Inputs 1 to 4: tables that read, and the numbers that TOML writes in other forms."""
    assert _read(folder, "dishes = {}") == (Settings(), [])
    assert _read(folder, "dishes = { breakfast = 10, lunch = 1 }") == (
        Settings(dishes=(10, 1, 1)),
        [],
    )
    lines = ('meals = ["lunch"]', "dishes = { breakfast = 3 }")
    assert _read(folder, *lines) == (Settings(None, (Meal.LUNCH,), 2, (3, 1, 1)), [])
    for value, number in (("0x2", 2), ("+3", 3), ("1_0", 10)):
        assert _read(folder, f"dishes = {{ dinner = {value} }}") == (
            Settings(dishes=(1, 1, number)),
            [],
        ), value


def _check_wrong_numbers(folder: DataFolder) -> None:
    """Inputs 5 and 6: a number that is not from 1 to 10, and a value that is not a table."""
    values = ["0", "11", "-1", "2.5", "2.0", '"2"', "true", "[2]", "{ n = 2 }", "2026-11-12"]
    values += ["inf", "nan", "0x" + "f" * 5000]
    for value in values:
        settings, problems = _read(folder, f"dishes = {{ dinner = {value} }}")
        assert settings is None, value[:20]
        assert_settings_problems(problems, NOT_1_TO_10)
    for value in ("2", "[]", '"dinner"', "[{ dinner = 2 }]", "true"):
        settings, problems = _read(folder, f"dishes = {value}")
        assert settings is None, value
        assert_settings_problems(problems, NOT_A_TABLE)


def _check_meals_and_order(folder: DataFolder) -> None:
    """Inputs 7 to 9: an unknown meal, two wrong numbers, and the order of every problem."""
    for key, number in (("supper", "2"), ("Dinner", "2"), ("supper", "0")):
        settings, problems = _read(folder, f"dishes = {{ {key} = {number} }}")
        assert settings is None
        assert_settings_problems(problems, [entry(DISHES, unknown_meal(key))])
    settings, problems = _read(folder, "[dishes]", "lunch = 0", 'breakfast = "x"')
    assert settings is None
    assert_settings_problems(
        problems,
        [
            entry(dishes_of("lunch"), DISHES_NOT_1_TO_10),
            entry(dishes_of("breakfast"), DISHES_NOT_1_TO_10),
        ],
    )
    lines = ("colour = 1", "dishes = { dinner = 11 }", "servings = 0", "meals = 3")
    settings, problems = _read(folder, *lines, 'language = "fr"')
    assert settings is None
    assert_settings_problems(
        problems,
        [
            entry(LANGUAGE, language_not_en_or_zh("fr")),
            entry(MEALS, not_a_list("meals")),
            entry(SERVINGS, servings_too_few(0)),
            entry(dishes_of("dinner"), DISHES_NOT_1_TO_10),
            entry(None, unknown_key("colour")),
        ],
    )


def test_f14_t23_read_settings_reads_the_key_dishes_and_reports_its_problems(
    example_folder: DataFolder, folder: DataFolder, default_int_limit: None
) -> None:
    """The example of 3.2, then nine inputs for the key."""
    _lines_of_the_example(example_folder)
    _check_values(folder)
    _check_wrong_numbers(folder)
    _check_meals_and_order(folder)


def test_f14_t24_every_command_reads_the_settings_with_the_dishes(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A right value changes no output, and a wrong one is an error that stops each command."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    root = made(source, tmp_path, "f", with_dishes("{ dinner = 2 }"))
    assert check(home, root) == expect(0, AFTER)
    assert at(home, root, "list") == out(LIST)
    assert at(home, root, "menu", "show", "2026-W47") == out(SHOW_47)
    shop = at(home, root, "shop", "2026-W47")
    assert shop == out(shop_47(root / "shopping" / "2026-W47.md"))
    zero = made(source, tmp_path, "g", with_dishes("{ dinner = 0 }"))
    assert check(home, zero) == rep(1, 7, 1, [E_DISHES_ZERO], [PORK])
    assert check(home, zero, "--lang", "zh") == rep(1, 7, 1, [E_DISHES_ZERO], [PORK], Lang.ZH)
    week = zero / "menus" / "2026-W47.toml"
    before = week.read_bytes()
    for argv in (("list",), ("menu", "new", "2026-W48"), ("menu", "suggest", "2026-W47")):
        assert at(home, zero, *argv) == stop(E_DISHES_ZERO), argv
    assert at(home, zero, "menu", "suggest", "2026-W47", "--lang", "zh") == stop(
        E_DISHES_ZERO, Lang.ZH
    )
    assert not (zero / "menus" / "2026-W48.toml").exists()
    assert week.read_bytes() == before
    table = made(source, tmp_path, "h", with_dishes("[]"))
    assert check(home, table) == rep(1, 7, 1, [E_DISHES_TABLE], [PORK])
