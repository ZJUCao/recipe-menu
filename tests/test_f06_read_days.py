"""Tests of F06 for read_week_menu: the key week, the days, and the meals (T33 to T39)."""

from f03_support import m_empty_text, m_missing_key, m_not_a_list, m_not_a_text
from f04_support import check_problems
from f06_support import (
    AT_WEEK,
    M_NOT_A_DISH,
    MEALS_DINNER,
    MEALS_EVERY,
    MEALS_LUNCH_DINNER,
    at_day,
    at_dish,
    at_key,
    bad,
    check_fails,
    check_reads,
    dinner_only,
    dishes_of,
    every_meal,
    example_settings,
    m_not_a_day_table,
    m_unknown_day_key,
    m_unknown_meal,
    m_unknown_recipe,
    m_week_not_file_name,
    m_week_not_iso,
    make_menu,
    put_menu,
    read_menu,
    week47,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.menus import Day, Dish, IsoWeek
from recipe_menu.settings import Meal

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

WEEK_VALUES = (
    ("week = 2026", "not a text"),
    ("week = true", "not a text"),
    ("week = 2026-11-16", "not a text"),
    ('week = ["2026-W47"]', "not a text"),
    ("week = { year = 2026 }", "not a text"),
    ('week = ""', "empty"),
    ('week = " "', "empty"),
    ('week = "\u3000"', "empty"),
    ('week = "2026-w47"', "2026-w47"),
    ('week = " next "', "next"),
    ('week = "this"', "this"),
    ('week = "2026-W7"', "2026-W7"),
    ('week = "2026-W99"', "2026-W99"),
    ('week = "2025-W53"', "2025-W53"),
    ('week = "2026 W47"', "2026 W47"),
    ('week = "\uff12\uff10\uff12\uff16-W47"', "\uff12\uff10\uff12\uff16-W47"),
)
WEEK_READS = ('week = "2026-W47"', 'week = " 2026-W47 "', 'week = "\u30002026-W47\t"')


def _monday_rice() -> dict[tuple[Day, Meal], tuple[Dish, ...]]:
    """Gives the filled slots of a file with one dish, ``rice``, in Monday dinner."""
    return {(Day.MONDAY, Meal.DINNER): dishes_of(("rice", 2))}


def test_f06_t33_the_key_week_is_checked_and_its_problem_is_the_only_one(
    example_folder: DataFolder,
) -> None:
    """A missing, wrong, empty, or not ISO ``week`` gives one problem, and a good one reads."""
    example = example_folder
    settings = example_settings()
    tail = ("[monday]", 'dinner = ["rice"]')
    put_menu(example, *tail, exact=True)
    check_fails(example, settings, [bad(None, m_missing_key("week"))], label="no line")
    for line, kind in WEEK_VALUES:
        put_menu(example, line, *tail, exact=True)
        if kind == "not a text":
            message = m_not_a_text("week")
        elif kind == "empty":
            message = m_empty_text("week")
        else:
            message = m_week_not_iso(kind)
        check_fails(example, settings, [bad(AT_WEEK, message)], label=line)
    for line in WEEK_READS:
        put_menu(example, line, *tail, exact=True)
        check_reads(example, settings, _monday_rice(), label=line)


def test_f06_t34_the_week_must_name_the_week_of_the_file_name(
    example_folder: DataFolder,
) -> None:
    """Whitespace does not count, and the weeks 53 and 1 and 9999 read the same way."""
    example = example_folder
    settings = example_settings()
    put_menu(example, 'week = "2026-W48"', exact=True)
    mismatch = bad(AT_WEEK, m_week_not_file_name("2026-W47", "2026-W48"))
    check_fails(example, settings, [mismatch], label=1)
    assert mismatch[3:] == (
        "The file name says 2026-W47, but the file says 2026-W48.",
        "文件名是 2026-W47，但文件里写的是 2026-W48。",
    )
    put_menu(example, 'week = " 2026-W46\t"', exact=True)
    check_fails(example, settings, [bad(AT_WEEK, m_week_not_file_name("2026-W47", "2026-W46"))])
    put_menu(example, 'week = "2027-W01"', exact=True, name="2026-W53")
    wrong = bad(AT_WEEK, m_week_not_file_name("2026-W53", "2027-W01"), "menus/2026-W53.toml")
    check_fails(example, settings, [wrong], week=IsoWeek(2026, 53), label=3)
    put_menu(example, 'week = "2026-W53"', exact=True, name="2026-W53")
    check_reads(example, settings, week=IsoWeek(2026, 53), label=4)
    put_menu(example, 'week = "9999-W51"', exact=True, name="0001-W01")
    wrong = bad(AT_WEEK, m_week_not_file_name("0001-W01", "9999-W51"), "menus/0001-W01.toml")
    check_fails(example, settings, [wrong], week=IsoWeek(1, 1), label=5)
    put_menu(example, 'week = "9999-W51"', exact=True, name="9999-W51")
    check_reads(example, settings, week=IsoWeek(9999, 51), label=6)


def test_f06_t35_a_day_that_is_not_a_table_gives_one_problem_in_the_order_of_the_week(
    example_folder: DataFolder,
) -> None:
    """Each day has its label as its place, and the days come Monday to Sunday."""
    example = example_folder
    put_menu(
        example,
        "sunday = 1.5",
        "saturday = 2026-11-21",
        "thursday = true",
        "wednesday = 3",
        'tuesday = "rice"',
        "monday = []",
        "[[friday]]",
        'dinner = ["rice"]',
    )
    expected = [bad(at_day(day), m_not_a_day_table(day)) for day in DAYS]
    check_fails(example, example_settings(), expected, label="settings")
    check_fails(example, None, expected, label="none")


def test_f06_t36_a_day_or_a_meal_that_the_file_lacks_holds_no_dishes(
    example_folder: DataFolder,
) -> None:
    """The slots run Monday to Sunday and in the order of the meals, whatever the file's order."""
    example = example_folder
    settings, every, dinner = example_settings(), every_meal(), dinner_only()
    put_menu(example)
    for given in (settings, every, dinner):
        check_reads(example, given, label=given.meals)
    assert read_menu(example, None) == (None, ())

    put_menu(example, "[tuesday]", 'dinner = ["rice"]')
    check_reads(example, settings, {(Day.TUESDAY, Meal.DINNER): dishes_of(("rice", 2))})
    put_menu(example, 'monday = { dinner = ["rice"], lunch = ["mapo-tofu"] }')
    filled = {
        (Day.MONDAY, Meal.LUNCH): dishes_of(("mapo-tofu", 2)),
        (Day.MONDAY, Meal.DINNER): dishes_of(("rice", 2)),
    }
    check_reads(example, settings, filled)
    put_menu(example, "[monday]", "[friday]", "lunch = []")
    check_reads(example, settings)

    put_menu(
        example,
        "[sunday]",
        'dinner = ["rice"]',
        'lunch = ["choy-sum"]',
        "[wednesday]",
        'dinner = ["mapo-tofu"]',
        "[monday]",
        'lunch = ["tomato-egg"]',
    )
    for given in (settings, every):
        number = given.servings
        filled = {
            (Day.MONDAY, Meal.LUNCH): dishes_of(("tomato-egg", number)),
            (Day.WEDNESDAY, Meal.DINNER): dishes_of(("mapo-tofu", number)),
            (Day.SUNDAY, Meal.LUNCH): dishes_of(("choy-sum", number)),
            (Day.SUNDAY, Meal.DINNER): dishes_of(("rice", number)),
        }
        menu, problems = read_menu(example, given)
        check_problems(problems, [])
        assert menu == make_menu(week47(), given.meals, filled)
        assert len(menu.slots) == 7 * len(given.meals)
        assert [(slot.day, slot.meal) for slot in menu.slots] == [
            (day, meal) for day in Day for meal in given.meals
        ]


def test_f06_t37_with_settings_a_key_that_names_no_meal_of_the_settings_is_an_error(
    example_folder: DataFolder,
) -> None:
    """``UNKNOWN_MEAL`` sits at the key of the day, and the key is not checked further."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'breakfast = ["rice"]',
        "lunch = []",
        "[tuesday]",
        "breakfast = []",
        'dinner = ["rice"]',
        "[wednesday]",
        'breakfast = "rice"',
        "[thursday]",
        'breakfast = ["Rice", 3]',
        "[friday]",
        "supper = []",
        "Dinner = []",
        "[saturday]",
        '"晚饭" = ["rice"]',
        "[sunday]",
        'week = "2026-W47"',
    )
    rest = (("friday", "supper"), ("friday", "Dinner"), ("saturday", "晚饭"), ("sunday", "week"))

    def unknown(meals: tuple[str, str], *places: tuple[str, str]) -> list:
        """Gives the ``UNKNOWN_MEAL`` errors of the places."""
        return [bad(at_key(d, k), m_unknown_meal(k, meals)) for d, k in places]

    first = (("monday", "breakfast"), ("wednesday", "breakfast"), ("thursday", "breakfast"))
    expected = unknown(MEALS_LUNCH_DINNER, *first, *rest)
    check_fails(example, example_settings(), expected, label="settings")
    thursday = at_key("thursday", "breakfast")
    with_every = [
        bad(at_key("wednesday", "breakfast"), m_not_a_list("breakfast")),
        bad(thursday, m_unknown_recipe("Rice")),
        bad(at_dish("thursday", "breakfast", 2), M_NOT_A_DISH),
        *unknown(MEALS_EVERY, *rest),
    ]
    check_fails(example, every_meal(), with_every, label="every")
    check_fails(example, dinner_only(), unknown(MEALS_DINNER, *first, *rest), label="dinner")


def test_f06_t38_with_no_settings_each_key_of_a_day_is_an_unknown_key(
    example_folder: DataFolder,
) -> None:
    """All three meals are in use, and each other key has its own place and no menu comes."""
    example = example_folder
    assert read_menu(example, None) == (None, ())
    put_menu(example)
    assert read_menu(example, None) == (None, ())
    put_menu(
        example,
        "[monday]",
        'breakfast = "rice"',
        "[friday]",
        "supper = []",
        'Dinner = ["rice"]',
        'breakfast = ["Rice"]',
        "lunch = []",
        "[saturday]",
        '"晚饭" = []',
    )
    monday = bad(at_key("monday", "breakfast"), m_not_a_list("breakfast"))
    rice = bad(at_key("friday", "breakfast"), m_unknown_recipe("Rice"))
    keys = (("friday", "supper"), ("friday", "Dinner"), ("saturday", "晚饭"))
    one = [bad(at_key(d, k), m_unknown_day_key(k)) for d, k in keys]
    many = [bad(at_key(d, k), m_unknown_meal(k, MEALS_EVERY)) for d, k in keys]
    check_fails(example, None, [monday, one[0], one[1], rice, one[2]], label="none")
    check_fails(example, every_meal(), [monday, many[0], many[1], rice, many[2]], label="every")


def test_f06_t39_a_meal_that_is_not_a_list_gives_one_problem_at_the_meal(
    example_folder: DataFolder,
) -> None:
    """``NOT_A_LIST`` names the key as the file writes it, and it is the only check of the meal."""
    example = example_folder
    put_menu(
        example,
        "[monday]",
        'lunch = "rice"',
        'dinner = ["rice"]',
        "[tuesday]",
        'dinner = { recipe = "rice" }',
        "[wednesday]",
        "lunch = 3",
        "dinner = true",
        "[thursday]",
        'dinner = ""',
        "[friday.dinner]",
        'recipe = "rice"',
    )
    places = (
        ("monday", "lunch"),
        ("tuesday", "dinner"),
        ("wednesday", "lunch"),
        ("wednesday", "dinner"),
        ("thursday", "dinner"),
        ("friday", "dinner"),
    )
    expected = [bad(at_key(day, key), m_not_a_list(key)) for day, key in places]
    check_fails(example, example_settings(), expected)
