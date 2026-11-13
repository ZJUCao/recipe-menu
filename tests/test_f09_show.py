"""Tests of F09 for ``recipe-menu show``: the example, the sections, a missing part, scaling."""

import tomllib
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f07_changes import mapo_mistake
from f09_support import (
    BOILED_EGG_FILE,
    PIZZA_FILE,
    WRONG_IDS,
    at,
    extra_recipes,
    made,
    rice_for_3,
)
from f09_texts import (
    BOILED,
    BOILED_ZH,
    E_MAPO,
    E_RICE_BOWL,
    FOUR,
    FOUR_ZH,
    MAPO,
    MAPO_ZH,
    PORK,
    PORK_ZH,
    RICE,
    RUN_HELP_COMMANDS,
    STEAMED,
    STEAMED_ZH,
    STEPS_ZH,
    TOMATO,
    TOMATO_ZH,
    WATER,
    WATER_ZH,
    ZH,
    err,
    not_a_recipe_id,
    out,
    patch,
    servings_not_1_to_100,
    stop,
)
from recipe_menu.datafile import DataFolder

THREE_ROWS = {
    2: "Servings: 3 (the recipe makes 2)   Tags: quick, home-style",
    5: "  Tomato        450 g        cut into wedges",
    6: "  Egg           4.5 pieces",
    7: "  Scallion      1.5 stalks   chopped",
    8: "  Salt          to taste",
    9: "  Sugar         1.5 tsp",
    10: "  Cooking oil   3 tbsp",
}
ELEVEN_WRONG_VALUES = [
    "0",
    "101",
    "04",
    "+4",
    "4.0",
    " 4",
    "-1",
    "1_0",
    "\uff14",
    "\u0664",
    "9" * 5000,
]


def _scaling_and_pork(home: Path, example: DataFolder) -> None:
    """Checks the prototype outputs, ``--servings``, and the steps of ``red-braised-pork``."""
    assert at(home, example, "show", "tomato-egg") == out(TOMATO)
    assert at(home, example, "show", "tomato-egg", "--servings", "2") == out(TOMATO)
    zh = at(home, example, "show", "tomato-egg", "--servings", "4", "--lang", "zh")
    assert zh == out(FOUR_ZH)
    assert at(home, example, "show", "tomato-egg", "--servings", "3") == out(
        patch(TOMATO, THREE_ROWS)
    )
    assert at(home, example, "show", "red-braised-pork") == out(PORK)
    text = example.recipe_file("red-braised-pork").read_text(encoding="utf-8")
    assert tomllib.loads(text)["steps"]["zh"] == STEPS_ZH


def _boiled_egg_and_unknown_id(home: Path, example: DataFolder) -> None:
    """Checks a recipe that lacks its Chinese name, note, and steps, and an unknown ID."""
    write(example.recipe_file("boiled-egg"), BOILED_EGG_FILE)
    assert at(home, example, "show", "boiled-egg") == out(BOILED)
    zh = at(home, example, "show", "boiled-egg", "--servings", "3", "--lang", "zh")
    boiled_zh = patch(
        BOILED_ZH, {2: "份数：3（菜谱按 1 份写）", 5: "  鸡蛋   6 个   at room temperature"}
    )
    assert zh == out(boiled_zh)
    assert at(home, example, "show", "mapo") == err(1, [MAPO])
    assert at(home, example, "show", "mapo", "--lang", "zh") == err(1, [MAPO_ZH])


def _wrong_values(home: Path, example: DataFolder) -> None:
    """Checks the wrong IDs, the wrong values of ``--servings``, and a line with no ID."""
    for wrong in WRONG_IDS[:5]:
        assert at(home, example, "show", wrong) == err(2, [not_a_recipe_id(wrong)])
    zh = at(home, example, "show", "Mapo", "--lang", "zh")
    assert zh == err(2, [not_a_recipe_id("Mapo", ZH)])
    for wrong in ELEVEN_WRONG_VALUES:
        result = at(home, example, "show", "tomato-egg", "--servings", wrong)
        assert result == err(2, [servings_not_1_to_100(wrong)])
    zero = err(2, [servings_not_1_to_100("0")])
    assert at(home, example, "show", "Mapo", "--servings", "0") == zero
    assert at(home, example, "show", "tomato-egg", "--servings", "100")[0] == 0
    missing = ['An argument is missing. Write "recipe-menu show ID".', RUN_HELP_COMMANDS[0]]
    assert at(home, example, "show") == err(2, missing)


def _mistakes(home: Path, example: DataFolder) -> None:
    """Checks that a mistake in one recipe stops only ``show`` of it, and a bad file name all."""
    mapo_mistake(example.root)
    assert at(home, example, "show", "mapo-tofu") == stop(E_MAPO)
    assert at(home, example, "show", "tomato-egg") == out(TOMATO)
    write(example.recipes / "Rice Bowl.toml", "")
    assert at(home, example, "show", "tomato-egg") == stop(E_RICE_BOWL)


def test_f09_t12_the_example_of_show_runs_in_order_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """The example of 2.4, step by step, with ``main`` and the real ``COMMANDS``."""
    home = make_home(tmp_path)
    _scaling_and_pork(home, example_folder)
    _boiled_egg_and_unknown_id(home, example_folder)
    _wrong_values(home, example_folder)
    _mistakes(home, example_folder)


def test_f09_t13_scenario_s12_and_the_prototype_sections_of_show_in_both_languages(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The names line, the servings line, the table, the steps, and the missing steps."""
    home = make_home(tmp_path)
    assert at(home, example_folder, "show", "tomato-egg") == out(TOMATO)
    zh = at(home, example_folder, "show", "tomato-egg", "--servings", "4", "--lang", "zh")
    assert zh == out(FOUR_ZH)
    assert at(home, example_folder, "show", "red-braised-pork") == out(PORK)
    assert at(home, example_folder, "show", "mapo") == err(1, [MAPO])
    assert at(home, example_folder, "show", "tomato-egg", "--lang", "zh") == out(TOMATO_ZH)
    assert at(home, example_folder, "show", "tomato-egg", "--servings", "4") == out(FOUR)
    assert at(home, example_folder, "show", "red-braised-pork", "--lang", "zh") == out(PORK_ZH)
    assert at(home, example_folder, "show", "mapo", "--lang", "zh") == err(1, [MAPO_ZH])


def test_f09_t14_a_recipe_that_lacks_a_language_or_a_part_is_shown_as_far_as_it_goes(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The names line, no tags, a note and steps in the other language, and no ingredients."""
    home = make_home(tmp_path)
    root = made(example_folder, tmp_path, "extra", extra_recipes)
    write(root / "recipes" / "pizza.toml", PIZZA_FILE)
    assert at(home, root, "show", "boiled-egg") == out(BOILED)
    assert at(home, root, "show", "boiled-egg", "--lang", "zh") == out(BOILED_ZH)
    assert at(home, root, "show", "steamed-egg") == out(STEAMED)
    assert at(home, root, "show", "steamed-egg", "--lang", "zh") == out(STEAMED_ZH)
    assert at(home, root, "show", "water") == out(WATER)
    assert at(home, root, "show", "water", "--lang", "zh") == out(WATER_ZH)
    pizza = ["Pizza  Pizza", "Servings: 2", "", "Steps", "  1. Bake for 12 minutes."]
    pizza_zh = ["Pizza  Pizza", "份数：2", "", "步骤", "  1. 烤 12 分钟。"]
    assert at(home, root, "show", "pizza") == out(pizza)
    assert at(home, root, "show", "pizza", "--lang", "zh") == out(pizza_zh)


def _scale_tomato(home: Path, example: DataFolder) -> None:
    """Checks ``--servings`` 1, 2, 3, 7, and 100 on ``tomato-egg``, which has whole stalks."""
    cases = {
        "1": {
            2: "Servings: 1 (the recipe makes 2)   Tags: quick, home-style",
            5: "  Tomato        150 g        cut into wedges",
            6: "  Egg           1.5 pieces",
            7: "  Scallion      0.5 stalks   chopped",
            8: "  Salt          to taste",
            9: "  Sugar         0.5 tsp",
            10: "  Cooking oil   1 tbsp",
        },
        "7": {
            2: "Servings: 7 (the recipe makes 2)   Tags: quick, home-style",
            5: "  Tomato        1050 g        cut into wedges",
            6: "  Egg           10.5 pieces",
            7: "  Scallion      3.5 stalks    chopped",
            8: "  Salt          to taste",
            9: "  Sugar         3.5 tsp",
            10: "  Cooking oil   7 tbsp",
        },
        "100": {
            2: "Servings: 100 (the recipe makes 2)   Tags: quick, home-style",
            5: "  Tomato        15000 g      cut into wedges",
            6: "  Egg           150 pieces",
            7: "  Scallion      50 stalks    chopped",
            8: "  Salt          to taste",
            9: "  Sugar         50 tsp",
            10: "  Cooking oil   100 tbsp",
        },
    }
    for servings, changes in cases.items():
        result = at(home, example, "show", "tomato-egg", "--servings", servings)
        assert result == out(patch(TOMATO, changes)), servings
    assert at(home, example, "show", "tomato-egg", "--servings", "2") == out(TOMATO)
    assert at(home, example, "show", "tomato-egg", "--servings", "3") == out(
        patch(TOMATO, THREE_ROWS)
    )


def _scale_pork(home: Path, example: DataFolder) -> None:
    """Checks ``--servings 4`` on ``red-braised-pork`` in both languages."""
    english = patch(
        PORK,
        {
            2: "Servings: 4 (the recipe makes 2)   Tags: home-style",
            5: "  Pork belly   2 jin      cut into 3 cm cubes",
            6: "  Rock sugar   60 g",
            7: "  Soy sauce    4 tbsp",
            8: "  Ginger       6 slices",
            9: "  Scallion     4 stalks",
        },
    )
    chinese = patch(
        PORK_ZH,
        {
            2: "份数：4（菜谱按 2 份写）   标签：家常",
            5: "  五花肉   2 斤     切成 3 厘米见方的块",
            6: "  冰糖     60 g",
            7: "  生抽     4 汤匙",
            8: "  姜       6 片",
            9: "  葱       4 根",
        },
    )
    assert at(home, example, "show", "red-braised-pork", "--servings", "4") == out(english)
    zh = at(home, example, "show", "red-braised-pork", "--servings", "4", "--lang", "zh")
    assert zh == out(chinese)


def _scale_extras(home: Path, root: Path) -> None:
    """Checks the rounding up and the units of the extra recipes."""
    one = {
        2: "Servings: 1 (the recipe makes 3)   Tags: quick, vegetarian",
        5: "  Egg        0.67 pieces   打散",
        6: "  Scallion   0.34 stalks   切葱花",
    }
    two_zh = {
        2: "份数：2（菜谱按 3 份写）   标签：快手、素",
        5: "  鸡蛋   1.34 个   打散",
        6: "  葱     0.67 根   切葱花",
    }
    assert at(home, root, "show", "steamed-egg", "--servings", "1") == out(patch(STEAMED, one))
    zh = at(home, root, "show", "steamed-egg", "--servings", "2", "--lang", "zh")
    assert zh == out(patch(STEAMED_ZH, two_zh))
    assert at(home, root, "show", "steamed-egg", "--servings", "3") == out(STEAMED)
    hundred = {
        2: "Servings: 100 (the recipe makes 1)",
        5: "  Egg    200 pieces   at room temperature",
    }
    assert at(home, root, "show", "boiled-egg", "--servings", "100") == out(patch(BOILED, hundred))
    zh = at(home, root, "show", "boiled-egg", "--servings", "3", "--lang", "zh")
    assert zh == out(
        patch(BOILED_ZH, {2: "份数：3（菜谱按 1 份写）", 5: "  鸡蛋   6 个   at room temperature"})
    )
    zh = at(home, root, "show", "water", "--servings", "2", "--lang", "zh")
    assert zh == out(patch(WATER_ZH, {2: "份数：2（菜谱按 1 份写）"}))


def test_f09_t15_servings_scales_each_quantity_in_its_unit_and_rounds_up(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Scaling by ``Fraction(servings, recipe.servings)``, in the unit of the recipe."""
    home = make_home(tmp_path)
    _scale_tomato(home, example_folder)
    _scale_pork(home, example_folder)
    _scale_extras(home, made(example_folder, tmp_path, "extra", extra_recipes))
    three = made(example_folder, tmp_path, "three", rice_for_3)
    one = patch(RICE, {2: "Servings: 1 (the recipe makes 3)   Tags: staple", 5: "  Rice   53.34 g"})
    two = patch(
        RICE, {2: "Servings: 2 (the recipe makes 3)   Tags: staple", 5: "  Rice   106.67 g"}
    )
    assert at(home, three, "show", "rice", "--servings", "1") == out(one)
    assert at(home, three, "show", "rice", "--servings", "2") == out(two)
