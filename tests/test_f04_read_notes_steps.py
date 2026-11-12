"""Tests of F04 for read_recipe: the notes and the steps (T27 to T31)."""

from dataclasses import replace

from f03_support import (
    M_ITEM_EMPTY,
    M_ITEM_NOT_A_TEXT,
    m_missing_key,
    m_not_a_list,
    m_not_a_text,
    m_unknown_key,
)
from f04_support import (
    BASE_STEPS,
    ITEM_KEYS,
    M_NO_EN_NOTE,
    M_NO_EN_STEPS,
    M_NO_STEPS,
    M_NO_ZH_NOTE,
    M_NO_ZH_STEPS,
    M_NOT_A_STEPS_TABLE,
    STEPS,
    ZH_EN_KEYS,
    check_fails,
    check_reads,
    dish,
    en_step,
    err,
    ingredient_n,
    m_amount_unit,
    m_not_a_zh_en,
    m_unknown_ing,
    m_zero,
    qty,
    tomato,
    warn,
    zh_step,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.units import Unit

ONE_ZH = 'zh = ["番茄切块。"]'
ONE_EN = 'en = ["Cut the tomatoes."]'


def with_note(note: BiText | None) -> Recipe:
    """Gives ``dish`` with its one ingredient line holding ``note``, which may be ``None``."""
    line = RecipeIngredient(tomato, qty(300, Unit.G), note)
    return replace(dish, ingredients=(line,))


def test_f04_t27_the_note_of_an_ingredient(folder: DataFolder) -> None:
    """One usable language gives a warning, no language gives no note, and wrong values fail."""
    at = ingredient_n(1)
    both_notes = BiText("cut into wedges", "切块")
    reads = [
        ('{ en = "cut into wedges" }', [warn(at, M_NO_ZH_NOTE)], BiText(en="cut into wedges")),
        ('{ zh = "切块", en = " " }', [warn(at, M_NO_EN_NOTE)], BiText(zh="切块")),
        (
            '{ zh = "\u3000", en = "cut into wedges" }',
            [warn(at, M_NO_ZH_NOTE)],
            BiText(en="cut into wedges"),
        ),
        ("{}", [], None),
        ('{ zh = "", en = "\t" }', [], None),
        ('{ zh = "切块", en = "cut into wedges" }', [], both_notes),
    ]
    for note, expected, kept in reads:
        item = f'{{ item = "番茄", amount = "300 g", note = {note} }}'
        check_reads(folder, with_note(kept), expected, ingredients=(item,))
    fails = [
        ('"切块"', [err(at, m_not_a_zh_en("note"))]),
        ('["切块"]', [err(at, m_not_a_zh_en("note"))]),
        ("{ zh = 3 }", [err(at, m_not_a_text("zh"))]),
        ('{ en = 3, zh = "" }', [err(at, m_not_a_text("en"))]),
        (
            '{ zh = "切块", en = "cut into wedges", size = 1 }',
            [err(at, m_unknown_key("size", ZH_EN_KEYS))],
        ),
    ]
    for note, expected in fails:
        item = f'{{ item = "番茄", amount = "300 g", note = {note} }}'
        check_fails(folder, expected, ingredients=(item,))
    assert with_note(None) == dish


def test_f04_t28_the_order_of_the_problems_of_an_ingredient(folder: DataFolder) -> None:
    """Item, amount, note, and then the unknown keys of the item, in the file's order."""
    items = (
        '{ b = 1, note = 3, amount = "0 g", a = 2, item = "豆瓣酱" }',
        '{ z = 1, note = { x = 1, en = "cut" }, amount = "300 g", item = "番茄" }',
        '{ note = { en = 3, zh = true }, item = "番茄", amount = "1 cups" }',
    )
    expected = [
        err(ingredient_n(1), m_unknown_ing("豆瓣酱")),
        err(ingredient_n(1), m_zero("0 g")),
        err(ingredient_n(1), m_not_a_zh_en("note")),
        err(ingredient_n(1), m_unknown_key("b", ITEM_KEYS)),
        err(ingredient_n(1), m_unknown_key("a", ITEM_KEYS)),
        err(ingredient_n(2), m_unknown_key("x", ZH_EN_KEYS)),
        warn(ingredient_n(2), M_NO_ZH_NOTE),
        err(ingredient_n(2), m_unknown_key("z", ITEM_KEYS)),
        err(ingredient_n(3), m_amount_unit("cups", "1 cups")),
        err(ingredient_n(3), m_not_a_text("zh")),
        err(ingredient_n(3), m_not_a_text("en")),
    ]
    check_fails(folder, expected, ingredients=items)


def test_f04_t29_the_steps_with_one_usable_language(folder: DataFolder) -> None:
    """A missing key or an empty list gives the warning, and several steps keep their order."""
    only_zh = replace(dish, steps=Steps(zh=("番茄切块。",)))
    only_en = replace(dish, steps=Steps(en=("Cut the tomatoes.",)))
    for steps in ((ONE_ZH,), (ONE_ZH, "en = []")):
        check_reads(folder, only_zh, [warn(STEPS, M_NO_EN_STEPS)], steps=steps)
    for steps in ((ONE_EN,), ("zh = []", ONE_EN)):
        check_reads(folder, only_en, [warn(STEPS, M_NO_ZH_STEPS)], steps=steps)
    two = replace(
        dish,
        steps=Steps(("Cut the tomatoes.", "Fry them."), ("番茄切块。", "炒番茄。")),
    )
    steps = ('zh = ["番茄切块。", "炒番茄。"]', 'en = ["Cut the tomatoes.", "Fry them."]')
    check_reads(folder, two, steps=steps)


def test_f04_t30_the_wrong_values_of_the_steps(folder: DataFolder) -> None:
    """The steps hold only lists, and a wrong language gets no warning and no NO_STEPS."""
    for value in ('["番茄切块。"]', '"番茄切块。"'):
        check_fails(folder, [err(STEPS, M_NOT_A_STEPS_TABLE)], steps=value)
    for line in ('zh = ""', 'zh = " "', "zh = 3", "zh = { a = 1 }"):
        check_fails(folder, [err(STEPS, m_not_a_list("zh"))], steps=(line, ONE_EN))
    check_fails(folder, [err(zh_step(1), M_ITEM_EMPTY)], steps=('zh = [" "]', ONE_EN))
    check_fails(
        folder,
        [
            err(zh_step(2), M_ITEM_NOT_A_TEXT),
            err(zh_step(3), M_ITEM_EMPTY),
            err(zh_step(4), M_ITEM_EMPTY),
        ],
        steps=('zh = ["番茄切块。", 3, "", "\u3000"]', ONE_EN),
    )
    check_fails(folder, [err(en_step(1), M_ITEM_NOT_A_TEXT)], steps=("en = [3]",))
    check_fails(folder, [err(STEPS, m_not_a_list("zh"))], steps=('zh = ""', "en = []"))
    check_fails(folder, [err(STEPS, m_not_a_list("en"))], steps=(ONE_ZH, 'en = " "'))


def test_f04_t31_the_other_errors_of_the_steps(folder: DataFolder) -> None:
    """A missing key, no usable language, and unknown keys, in the order of the steps."""
    check_fails(folder, [err(None, m_missing_key("steps"))], steps=None)
    for steps in ((), ("zh = []", "en = []"), ("en = []",)):
        check_fails(folder, [err(STEPS, M_NO_STEPS)], steps=steps)
    check_fails(
        folder,
        [err(STEPS, m_unknown_key("note", ZH_EN_KEYS))],
        steps=(ONE_ZH, ONE_EN, 'note = "x"'),
    )
    check_fails(
        folder,
        [
            err(None, m_missing_key("servings")),
            err(STEPS, m_unknown_key("servings", ZH_EN_KEYS)),
        ],
        servings=None,
        steps=(*BASE_STEPS, "servings = 2"),
    )
    check_fails(
        folder,
        [
            err(en_step(2), M_ITEM_NOT_A_TEXT),
            err(STEPS, m_unknown_key("x", ZH_EN_KEYS)),
            err(STEPS, m_unknown_key("y", ZH_EN_KEYS)),
            warn(STEPS, M_NO_ZH_STEPS),
        ],
        steps=("x = 1", 'en = ["Stir.", 3]', "zh = []", "y = 2"),
    )
