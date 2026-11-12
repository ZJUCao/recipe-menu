"""Tests of F06 for read_week_menu on the example folder (T30 to T32)."""

from f03_support import (
    M_FILE_MISSING,
    M_ITEM_EMPTY,
    m_missing_key,
    m_not_a_list,
    m_not_a_text,
    write,
)
from f04_support import EXAMPLE_IDS, M_SERVINGS_NOT_A_NUMBER, check_problems, m_too_few
from f06_support import (
    AT_WEEK,
    M_NOT_A_DISH,
    MEALS_LUNCH_DINNER,
    at_day,
    at_dish,
    at_key,
    bad,
    check_fails,
    every_meal,
    example_menu,
    example_settings,
    m_not_a_day_table,
    m_unknown_day_key,
    m_unknown_dish_key,
    m_unknown_meal,
    m_unknown_recipe,
    m_unknown_top,
    m_week_not_file_name,
    m_week_not_iso,
    mistakes,
    put_menu,
    read_menu,
    typo,
    week47,
)
from recipe_menu.datafile import DataFolder, Severity
from recipe_menu.lang import Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, read_settings


def test_f06_t30_the_example_menu_reads_with_the_example_settings(
    example_folder: DataFolder,
) -> None:
    """With the example settings, with all three meals, and with none, as the design shows."""
    folder = example_folder
    settings, problems = read_settings(folder)
    assert problems == ()
    assert settings == example_settings()
    listed, problems = list_recipe_ids(folder)
    assert problems == ()
    assert listed == EXAMPLE_IDS
    ids = frozenset(listed)
    week = week47()
    menu, problems = read_week_menu(folder, week, settings, ids)
    assert problems == ()
    assert menu is not None
    assert menu.week == week
    assert menu.meals == (Meal.LUNCH, Meal.DINNER)
    assert len(menu.slots) == 14
    monday = (Dish("tomato-egg", 2), Dish("choy-sum", 2), Dish("rice", 2))
    assert menu.dishes(Day.MONDAY, Meal.DINNER) == monday
    assert menu.dishes(Day.SUNDAY, Meal.DINNER)[0] == Dish("cola-wings", 4)
    assert sum(1 for slot in menu.slots if slot.dishes) == 4
    assert sum(len(slot.dishes) for slot in menu.slots) == 9
    assert menu == example_menu(settings)

    menu, problems = read_week_menu(folder, week, every_meal(), ids)
    assert problems == ()
    assert menu is not None
    assert menu.dishes(Day.MONDAY, Meal.BREAKFAST) == ()
    assert menu.dishes(Day.MONDAY, Meal.DINNER)[0] == Dish("tomato-egg", 3)
    assert read_week_menu(folder, week, None, ids) == (None, ())


def test_f06_t31_the_mistakes_of_the_f07_prototype_and_of_v0_1_s07(
    example_folder: DataFolder,
) -> None:
    """One unknown recipe, then three mistakes, with the settings and with none."""
    example = example_folder
    original = example.menu_file("2026-W47").read_text(encoding="utf-8")
    typo(example)
    settings = example_settings()
    monday = at_key("monday", "dinner")
    check_fails(example, settings, [bad(monday, m_unknown_recipe("tomato-eggs"))])

    write(example.menu_file("2026-W47"), original)
    mistakes(example)
    week = bad(AT_WEEK, m_week_not_file_name("2026-W47", "2026-W48"))
    servings = bad(at_dish("sunday", "dinner", 1), m_too_few(0))
    supper = at_key("friday", "supper")
    check_fails(
        example,
        settings,
        [week, bad(supper, m_unknown_meal("supper", MEALS_LUNCH_DINNER)), servings],
    )
    check_fails(example, None, [week, bad(supper, m_unknown_day_key("supper")), servings])


def _lines() -> list[str]:
    """Gives the file of the design's example, with a mistake in nearly every part."""
    return [
        "week = 2026",
        "wednesday = []",
        "[monday]",
        'lunch = "rice"',
        'dinner = ["Rice", 3, " ", { recipe = "rice", servings = 0x' + "f" * 5000 + ", note = 1 }]",
        "breakfast = []",
        "[tuesday]",
        'breakfast = ["rice"]',
        "[funday]",
    ]


def test_f06_t32_a_file_with_a_mistake_in_nearly_every_part_gives_ten_problems(
    example_folder: DataFolder, default_int_limit: None
) -> None:
    """The ten problems come in order, nine with no settings, and then single problems."""
    example = example_folder
    put_menu(example, *_lines(), exact=True)
    settings = example_settings()
    first = [
        bad(AT_WEEK, m_not_a_text("week")),
        bad(at_key("monday", "lunch"), m_not_a_list("lunch")),
        bad(at_key("monday", "dinner"), m_unknown_recipe("Rice")),
        bad(at_dish("monday", "dinner", 2), M_NOT_A_DISH),
        bad(at_dish("monday", "dinner", 3), M_ITEM_EMPTY),
        bad(at_dish("monday", "dinner", 4), M_SERVINGS_NOT_A_NUMBER),
        bad(at_dish("monday", "dinner", 4), m_unknown_dish_key("note")),
    ]
    last = [
        bad(at_day("wednesday"), m_not_a_day_table("wednesday")),
        bad(None, m_unknown_top("funday")),
    ]
    breakfast = bad(at_key("tuesday", "breakfast"), m_unknown_meal("breakfast", MEALS_LUNCH_DINNER))
    menu, problems = read_menu(example, settings)
    assert menu is None
    assert all(problem.severity is Severity.ERROR for problem in problems)
    check_problems(problems, [*first, breakfast, *last])
    english = [problem.text(Lang.EN) for problem in problems]
    assert english[0] == '"week" must be a text in quotation marks.'
    assert english[7].startswith('Unknown meal "breakfast". The settings name')
    assert english[9].startswith('Unknown key "funday". The keys are week, monday,')
    check_fails(example, None, [*first, *last])
    assert len(read_menu(example, None)[1]) == 9

    put_menu(example, 'week = " 2026-W47 "', exact=True)
    menu, problems = read_menu(example, settings)
    assert problems == ()
    assert menu is not None
    assert all(slot.dishes == () for slot in menu.slots)
    put_menu(example, 'week = "2026-w47"', exact=True)
    check_fails(example, settings, [bad(AT_WEEK, m_week_not_iso("2026-w47"))])
    put_menu(example, "[monday]", "dinner = []", exact=True)
    check_fails(example, settings, [bad(None, m_missing_key("week"))])
    missing = bad(None, M_FILE_MISSING, "menus/2026-W48.toml")
    check_fails(example, settings, [missing], week=IsoWeek(2026, 48))
