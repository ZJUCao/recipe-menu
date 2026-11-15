"""Tests of F12 with the readers of F03 to F06 on the example folder and v0.1 weeks (T29-T32)."""

from pathlib import Path

from f03_support import put_bytes
from f04_support import M_NO_EN_STEPS, STEPS, view, warn
from f06_support import example_menu, example_settings
from f11_support import menu_text
from f12_support import (
    EN,
    EVERY_MEAL,
    LUNCH_DINNER,
    PANTRY_NAMES,
    S16_EN,
    S18_CELLS,
    W47_EN,
    W47_PANTRY_EN,
    W47_ZH,
    ZH,
    code_catalog,
    code_pantry,
    code_recipes,
    expected_s16,
    expected_s18,
    expected_w47,
    find,
    lines_of,
    menu_of,
    names_of,
    read_week,
    s16_folder,
    s18_changes,
    written,
)
from recipe_menu.catalog import Pantry
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.menus import Day, Dish, IsoWeek
from recipe_menu.settings import Meal
from recipe_menu.shopping import ShoppingList, build_shopping_list

S16_ZH = ["蔬菜水果", "- 番茄 450 g", "- 葱 2 根", "蛋奶豆制品", "- 鸡蛋 5 个"]


def test_f12_t29_the_example_week_gives_the_prototypes_table_and_both_outputs(
    example_folder: DataFolder,
) -> None:
    """2026-W47 of the example folder gives 6 groups, 14 lines, 4 meals, 9 dishes, 5 pantry."""
    menu, mapping, catalog, pantry = read_week(example_folder, IsoWeek(2026, 47))
    shopping = build_shopping_list(menu, mapping, catalog, pantry)

    assert shopping == expected_w47(catalog)
    assert (len(shopping.groups), len(lines_of(shopping))) == (6, 14)
    assert (shopping.meal_count, shopping.dish_count) == (4, 9)
    assert written(shopping, EN) == W47_EN
    assert written(shopping, ZH) == W47_ZH
    assert names_of(shopping.pantry_used, EN) == W47_PANTRY_EN
    assert names_of(shopping.pantry_used, ZH) == list(PANTRY_NAMES)

    code = code_catalog()
    in_code = build_shopping_list(
        example_menu(example_settings()), code_recipes(code), code, code_pantry(code)
    )
    assert in_code == shopping
    assert hash(in_code) == hash(shopping)


def test_f12_t30_v0_1_s16_three_servings_of_tomato_egg_in_monday_breakfast(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The files of v0.1-S16 give Tomato 450 g, Scallion 2 stalks, and Egg 5 pieces."""
    folder = s16_folder(example_folder, tmp_path / "init")
    menu, mapping, catalog, pantry = read_week(folder, IsoWeek(2026, 48))
    assert menu.dishes(Day.MONDAY, Meal.BREAKFAST) == (Dish("tomato-egg", 3),)
    shopping = build_shopping_list(menu, mapping, catalog, pantry)

    assert shopping == expected_s16(catalog)
    assert written(shopping, EN) == S16_EN
    assert written(shopping, ZH) == S16_ZH
    assert names_of(shopping.pantry_used, EN) == ["Cooking oil", "Salt", "Sugar"]

    code = code_catalog()
    week = menu_of("monday breakfast: tomato-egg 3", meals=EVERY_MEAL)
    in_code = build_shopping_list(week, code_recipes(code), code, code_pantry(code))
    assert in_code == shopping
    assert hash(in_code) == hash(shopping)


def test_f12_t31_v0_1_s18_amounts_that_cannot_be_added_share_a_line(
    example_folder: DataFolder,
) -> None:
    """The files of v0.1-S18 give ``5 stalks + 1 bunch`` and ``30 ml + 10 g``."""
    s18_changes(example_folder)
    problems: list[Problem] = []
    menu, mapping, catalog, pantry = read_week(example_folder, IsoWeek(2026, 48), problems)
    assert view(problems) == [warn(STEPS, M_NO_EN_STEPS, "recipes/red-braised-pork.toml")]
    shopping = build_shopping_list(menu, mapping, catalog, pantry)

    assert shopping == expected_s18(catalog)
    by_name = {item.ingredient.name.zh: item for item in lines_of(shopping)}
    assert by_name["葱"].amount_text(EN) == "5 stalks + 1 bunch"
    assert by_name["葱"].amount_text(ZH) == "5 根 + 1 把"
    assert by_name["生抽"].amount_text(EN) == "30 ml + 10 g"
    assert by_name["生抽"].amount_text(ZH) == "30 ml + 10 g"

    code = code_catalog()
    no_soy_sauce = Pantry(code_pantry(code).ingredients - {find(code, "生抽")})
    in_code = build_shopping_list(menu_of(*S18_CELLS), code_recipes(code), code, no_soy_sauce)
    assert in_code == shopping
    assert hash(in_code) == hash(shopping)


def test_f12_t32_v0_1_s14_a_new_menu_gives_the_list_with_no_dish(
    example_folder: DataFolder,
) -> None:
    """A menu that ``menu new`` created gives ``ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())``."""
    put_bytes(example_folder.menu_file("2026-W46"), menu_text("2026-W46", LUNCH_DINNER))
    menu, mapping, catalog, pantry = read_week(example_folder, IsoWeek(2026, 46))
    assert mapping == {}
    shopping = build_shopping_list(menu, mapping, catalog, pantry)
    assert shopping == ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())
