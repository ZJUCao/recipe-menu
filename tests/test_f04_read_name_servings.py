"""Tests of F04 for read_recipe: the name and the servings (T14 to T19)."""

from dataclasses import replace

import pytest

from f03_support import m_missing_key, m_not_a_text, m_unknown_key
from f04_support import (
    M_NO_EN_NAME,
    M_NO_NAME,
    M_NO_ZH_NAME,
    M_SERVINGS_NOT_A_NUMBER,
    NAME,
    SERVINGS,
    ZH_EN_KEYS,
    check_fails,
    check_reads,
    dish,
    dish_catalog,
    err,
    m_not_a_zh_en,
    m_too_few,
    m_too_many,
    qty,
    tomato,
    warn,
    write_dish,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.recipes import RecipeIngredient, Steps, read_recipe
from recipe_menu.units import Unit


def test_f04_t14_the_base_recipe_reads_and_each_text_is_stripped(folder: DataFolder) -> None:
    """Whitespace at both ends goes, and whitespace inside a text stays."""
    write_dish(folder)
    assert read_recipe(folder, dish_catalog, "dish") == (dish, ())
    padded_item = (
        '{ item = " 番茄 ", amount = " 300 g ", '
        'note = { zh = " 切块 ", en = "cut into\u00a0wedges\u3000" } }'
    )
    expected = replace(
        dish,
        name=BiText("Tomato and  egg stir-fry", "番茄炒蛋"),
        ingredients=(
            RecipeIngredient(tomato, qty(300, Unit.G), BiText("cut into\u00a0wedges", "切块")),
        ),
        steps=Steps(("Cut the  tomatoes.",), ("番茄切块。",)),
    )
    check_reads(
        folder,
        expected,
        name='{ zh = " 番茄炒蛋\u3000", en = "\tTomato and  egg stir-fry " }',
        tags='[" 快手 "]',
        ingredients=(padded_item,),
        steps=('zh = [" 番茄切块。\u3000"]', 'en = ["\tCut the  tomatoes. "]'),
    )


def test_f04_t15_a_name_with_one_usable_language_gives_a_warning(folder: DataFolder) -> None:
    """A blank text in the name counts as a missing language."""
    only_en = replace(dish, name=BiText(en="Tomato and egg stir-fry"))
    only_zh = replace(dish, name=BiText(zh="番茄炒蛋"))
    en_names = (
        '{ en = "Tomato and egg stir-fry" }',
        '{ zh = "", en = "Tomato and egg stir-fry" }',
        '{ zh = "\u3000", en = "Tomato and egg stir-fry" }',
    )
    for name in en_names:
        check_reads(folder, only_en, [warn(NAME, M_NO_ZH_NAME)], name=name)
    for name in ('{ zh = "番茄炒蛋" }', '{ zh = "番茄炒蛋", en = "\t" }'):
        check_reads(folder, only_zh, [warn(NAME, M_NO_EN_NAME)], name=name)


def test_f04_t16_the_errors_of_the_name(folder: DataFolder) -> None:
    """A wrong language gets no warning for the other language, and no NO_NAME."""
    cases = [
        (None, [err(None, m_missing_key("name"))]),
        ('"番茄炒蛋"', [err(NAME, m_not_a_zh_en("name"))]),
        ('["番茄炒蛋"]', [err(NAME, m_not_a_zh_en("name"))]),
        ('{ zh = 3, en = "Tomato and egg stir-fry" }', [err(NAME, m_not_a_text("zh"))]),
        ('{ zh = "番茄炒蛋", en = true }', [err(NAME, m_not_a_text("en"))]),
        ("{ zh = [], en = 3 }", [err(NAME, m_not_a_text("zh")), err(NAME, m_not_a_text("en"))]),
        ("{ zh = 3 }", [err(NAME, m_not_a_text("zh"))]),
        (
            '{ zh = "番茄炒蛋", en = "Tomato and egg stir-fry", fr = "x" }',
            [err(NAME, m_unknown_key("fr", ZH_EN_KEYS))],
        ),
        ("{}", [err(NAME, M_NO_NAME)]),
        ('{ zh = "", en = " " }', [err(NAME, M_NO_NAME)]),
    ]
    for name, expected in cases:
        check_fails(folder, expected, name=name)


def test_f04_t17_the_order_within_the_name(folder: DataFolder) -> None:
    """Problems of zh, then en, then the unknown keys, then NO_NAME or the warning."""
    unknown = m_unknown_key
    check_fails(
        folder,
        [
            err(NAME, m_not_a_text("zh")),
            err(NAME, m_not_a_text("en")),
            err(NAME, unknown("b", ZH_EN_KEYS)),
            err(NAME, unknown("a", ZH_EN_KEYS)),
        ],
        name="{ en = 3, b = 1, zh = true, a = 2 }",
    )
    check_fails(
        folder,
        [err(NAME, unknown("x", ZH_EN_KEYS)), err(NAME, M_NO_NAME)],
        name='{ x = 1, en = "", zh = "" }',
    )
    check_fails(
        folder,
        [err(NAME, unknown("y", ZH_EN_KEYS)), warn(NAME, M_NO_EN_NAME)],
        name='{ y = 1, zh = "番茄炒蛋" }',
    )


def test_f04_t18_servings_are_read_by_value_and_bounded(folder: DataFolder) -> None:
    """An integer of up to 15 digits outside the range gives its error with the number."""
    for literal, servings in (("1", 1), ("100", 100), ("+7", 7), ("1_0", 10), ("0x64", 100)):
        check_reads(folder, replace(dish, servings=servings), servings=literal)
    wrong = [
        ("0", m_too_few(0)),
        ("-1", m_too_few(-1)),
        ("-999999999999999", m_too_few(-999999999999999)),
        ("101", m_too_many(101)),
        ("0x65", m_too_many(101)),
        ("999999999999999", m_too_many(999999999999999)),
    ]
    for literal, message in wrong:
        check_fails(folder, [err(SERVINGS, message)], servings=literal)
    assert m_too_few(0) == (
        "Servings must be a whole number of 1 or more, not 0.",
        "份数必须是不小于 1 的整数，不能是 0。",
    )


@pytest.mark.usefixtures("default_int_limit")
def test_f04_t19_a_value_that_is_no_usable_integer_shows_no_number(folder: DataFolder) -> None:
    """Hexadecimal of 5,000 digits and decimal of 4,300 digits raise nothing."""
    literals = [
        '"2"',
        "2.5",
        "2.0",
        "true",
        "false",
        "[2]",
        "{ n = 2 }",
        "2026-11-11",
        "inf",
        "1000000000000000",
        "-1000000000000000",
        "0x" + "f" * 5000,
        "1" * 4300,
    ]
    for literal in literals:
        check_fails(folder, [err(SERVINGS, M_SERVINGS_NOT_A_NUMBER)], servings=literal)
    check_fails(folder, [err(None, m_missing_key("servings"))], servings=None)
