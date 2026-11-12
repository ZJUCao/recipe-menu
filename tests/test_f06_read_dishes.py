"""Tests of F06 for read_week_menu: the dishes of a meal and their servings (T40 to T45)."""

import shutil

from f03_support import M_ITEM_EMPTY, m_empty_text, m_missing_key, m_not_a_text, put_bytes
from f04_support import (
    M_SERVINGS_NOT_A_NUMBER,
    m_too_few,
    m_too_many,
)
from f06_support import (
    M_NOT_A_DISH,
    at_dish,
    at_key,
    bad,
    check_fails,
    check_reads,
    dishes_of,
    every_meal,
    example_settings,
    ids_of,
    m_unknown_dish_key,
    m_unknown_recipe,
    put_menu,
    settings_of,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.menus import Day
from recipe_menu.settings import Meal

MONDAY_DINNER = at_key("monday", "dinner")
BAD_IDS = (
    "tomato-eggs",
    "Rice",
    "Rice",
    "rice.toml",
    "con",
    "tomato egg",
    "番茄炒蛋",
    "rice\u200b",
    "Mapo-Tofu",
)
SERVINGS_VALUES = (
    "1",
    "100",
    "0",
    "-1",
    "101",
    "999999999999999",
    "-999999999999999",
    "1000000000000000",
    "-1000000000000000",
    '"4"',
    "2.5",
    "4.0",
    "true",
    "[4]",
    "0x" + "f" * 5000,
    "2026-11-16",
)


def test_f06_t40_a_dish_is_an_id_or_a_table_and_a_meal_keeps_the_file_order(
    example_folder: DataFolder,
) -> None:
    """The ID loses its outer whitespace, and a dish without servings gets the settings'."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'dinner = ["rice", " rice ", "\u3000choy-sum\t", { recipe = "mapo-tofu" }, '
        '{ recipe = " cola-wings ", servings = 1 }, { servings = 100, recipe = "rice" }, "rice"]',
        "[saturday]",
        'lunch = ["tomato-egg-noodles"]',
    )
    for number in (2, 1, 100):
        filled = {
            (Day.MONDAY, Meal.DINNER): dishes_of(
                ("rice", number),
                ("rice", number),
                ("choy-sum", number),
                ("mapo-tofu", number),
                ("cola-wings", 1),
                ("rice", 100),
                ("rice", number),
            ),
            (Day.SATURDAY, Meal.LUNCH): dishes_of(("tomato-egg-noodles", number)),
        }
        check_reads(example, settings_of(Meal.LUNCH, Meal.DINNER, servings=number), filled)


def test_f06_t41_an_item_that_is_no_dish_gives_not_a_dish_or_empty_item(
    example_folder: DataFolder,
) -> None:
    """N counts every item of the meal from 1, the items with problems included."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'dinner = [3, "rice", "", true, " ", ["rice"], "\u3000", 2.5, 2026-11-16]',
        "[saturday]",
        'lunch = ["rice", [], "\t"]',
    )
    dinner = (
        (1, M_NOT_A_DISH),
        (3, M_ITEM_EMPTY),
        (4, M_NOT_A_DISH),
        (5, M_ITEM_EMPTY),
        (6, M_NOT_A_DISH),
        (7, M_ITEM_EMPTY),
        (8, M_NOT_A_DISH),
        (9, M_NOT_A_DISH),
    )
    expected = [bad(at_dish("monday", "dinner", n), message) for n, message in dinner]
    expected += [
        bad(at_dish("saturday", "lunch", 2), M_NOT_A_DISH),
        bad(at_dish("saturday", "lunch", 3), M_ITEM_EMPTY),
    ]
    check_fails(example, example_settings(), expected, label=1)
    put_menu(example, "[wednesday]", 'breakfast = [{ recipe = "rice" }, 7]')
    only = [bad(at_dish("wednesday", "breakfast", 2), M_NOT_A_DISH)]
    check_fails(example, every_meal(), only, label=2)


def test_f06_t42_a_dish_in_braces_needs_a_recipe_that_is_a_text_and_not_blank(
    example_folder: DataFolder,
) -> None:
    """``MISSING_KEY``, ``NOT_A_TEXT``, and ``EMPTY_TEXT`` sit at dish N."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'dinner = [{ servings = 2 }, {}, { recipe = 3 }, { recipe = ["rice"] }, { recipe = "" }, '
        '{ recipe = "\u3000" }, { recipe = "rice" }]',
    )
    messages = (
        m_missing_key("recipe"),
        m_missing_key("recipe"),
        m_not_a_text("recipe"),
        m_not_a_text("recipe"),
        m_empty_text("recipe"),
        m_empty_text("recipe"),
    )
    expected = [
        bad(at_dish("monday", "dinner", number), message)
        for number, message in enumerate(messages, start=1)
    ]
    check_fails(example, example_settings(), expected)


def test_f06_t43_a_recipe_that_is_not_in_the_set_or_breaks_the_id_rule_is_unknown(
    example_folder: DataFolder,
) -> None:
    """The ID without outer whitespace is in the message, and U+200B is not whitespace."""
    example = example_folder
    settings = example_settings()
    put_menu(
        example,
        "[monday]",
        'dinner = ["tomato-eggs", "Rice", " Rice ", "rice.toml", "con", "tomato egg", '
        '"番茄炒蛋", "rice\u200b", { recipe = " Mapo-Tofu " }, "rice"]',
    )
    nine = [bad(MONDAY_DINNER, m_unknown_recipe(recipe)) for recipe in BAD_IDS]
    ids = ids_of(example)
    check_fails(example, settings, nine, ids=ids, label=1)
    assert bad(MONDAY_DINNER, m_unknown_recipe("番茄炒蛋"))[4] == "未知菜谱“番茄炒蛋”。"
    extra = ids | {"Rice", "con", "tomato egg", "rice.toml"}
    check_fails(example, settings, nine, ids=extra, label=4)

    put_bytes(example.recipes / "tomato-eggs.toml", b"")
    with_file = ids_of(example)
    check_fails(example, settings, nine[1:], ids=with_file, label=3)
    put_menu(example, "[monday]", 'dinner = ["tomato-eggs"]')
    check_reads(
        example,
        settings,
        {(Day.MONDAY, Meal.DINNER): dishes_of(("tomato-eggs", 2))},
        ids=with_file,
        label=3,
    )

    shutil.rmtree(example.recipes)
    empty = ids_of(example)
    assert empty == frozenset()
    put_menu(
        example,
        "[monday]",
        'dinner = ["tomato-eggs", "Rice", " Rice ", "rice.toml", "con", "tomato egg", '
        '"番茄炒蛋", "rice\u200b", { recipe = " Mapo-Tofu " }, "rice"]',
    )
    both = [*nine, bad(MONDAY_DINNER, m_unknown_recipe("rice"))]
    check_fails(example, settings, both, ids=empty, label=2)


def test_f06_t44_the_servings_of_a_dish_follow_the_rule_of_read_servings(
    example_folder: DataFolder, default_int_limit: None
) -> None:
    """A number of up to 15 digits shows in the message, and any other value is not a number."""
    example = example_folder
    dishes_lines = [f'  {{ recipe = "rice", servings = {value} }},' for value in SERVINGS_VALUES]
    put_menu(example, "[monday]", "dinner = [", *dishes_lines, "]")
    too_few = (m_too_few(0), m_too_few(-1))
    too_many = (m_too_many(101), m_too_many(999999999999999))
    expected = [
        bad(at_dish("monday", "dinner", 3), too_few[0]),
        bad(at_dish("monday", "dinner", 4), too_few[1]),
        bad(at_dish("monday", "dinner", 5), too_many[0]),
        bad(at_dish("monday", "dinner", 6), too_many[1]),
        bad(at_dish("monday", "dinner", 7), m_too_few(-999999999999999)),
        *(
            bad(at_dish("monday", "dinner", number), M_SERVINGS_NOT_A_NUMBER)
            for number in range(8, 17)
        ),
    ]
    check_fails(example, example_settings(), expected)
    put_menu(
        example,
        "[monday]",
        'dinner = [{ recipe = "rice", servings = 1 }, { recipe = "rice", servings = 100 }]',
    )
    both = {(Day.MONDAY, Meal.DINNER): dishes_of(("rice", 1), ("rice", 100))}
    check_reads(example, example_settings(), both)


def test_f06_t45_the_problems_of_one_dish_come_in_the_order_recipe_servings_keys(
    example_folder: DataFolder,
) -> None:
    """A problem of ``recipe`` does not stop the checks of ``servings`` or of the other keys."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'dinner = [{ note = 1, servings = 0, recipe = "Rice", colour = "red" }, '
        '{ servings = "x", Recipe = "rice" }, { recipe = 3, servings = 101 }, '
        '{ recipe = "rice", servings = 2, note = "x" }]',
    )
    one, two, three, four = (at_dish("monday", "dinner", n) for n in (1, 2, 3, 4))
    expected = [
        bad(MONDAY_DINNER, m_unknown_recipe("Rice")),
        bad(one, m_too_few(0)),
        bad(one, m_unknown_dish_key("note")),
        bad(one, m_unknown_dish_key("colour")),
        bad(two, m_missing_key("recipe")),
        bad(two, M_SERVINGS_NOT_A_NUMBER),
        bad(two, m_unknown_dish_key("Recipe")),
        bad(three, m_not_a_text("recipe")),
        bad(three, m_too_many(101)),
        bad(four, m_unknown_dish_key("note")),
    ]
    check_fails(example, example_settings(), expected)
    assert bad(four, m_unknown_dish_key("note"))[3:] == (
        'Unknown key "note". The keys are recipe and servings.',
        "未知键“note”。可用的键：recipe 和 servings。",
    )
