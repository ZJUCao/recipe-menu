"""Tests of F06 for read_week_menu: the top of the file and the whole file (T46 to T48)."""

from f03_support import (
    M_DEFINED_TWICE,
    M_FILE_IS_FOLDER,
    M_FILE_MISSING,
    M_MISSING_QUOTE,
    M_NOT_UTF8,
    M_NUMBER_TOO_LONG,
    at_line,
    m_missing_key,
    m_not_a_list,
    put_bytes,
)
from f06_support import (
    AT_WEEK,
    M_NOT_A_DISH,
    MEALS_LUNCH_DINNER,
    at_day,
    at_dish,
    at_key,
    bad,
    check_fails,
    check_reads,
    example_filled,
    example_settings,
    m_not_a_day_table,
    m_unknown_day_key,
    m_unknown_meal,
    m_unknown_recipe,
    m_unknown_top,
    m_week_not_file_name,
    put_menu,
    week47,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.menus import IsoWeek

TOP_KEYS = ("zzz", "Week", "notes", "Monday", "funday", "2026-W47")


def test_f06_t46_a_key_at_the_top_of_the_file_that_is_no_day_is_an_unknown_key(
    example_folder: DataFolder,
) -> None:
    """The unknown keys come after the days, in the file's order, and each has no place."""
    example = example_folder
    put_menu(
        example,
        "zzz = 1",
        'week = "2026-W47"',
        'Week = "2026-W47"',
        'notes = "x"',
        "[Monday]",
        'dinner = ["Rice"]',
        "[monday]",
        'dinner = ["rice"]',
        "[funday]",
        "[2026-W47]",
        exact=True,
    )
    expected = [bad(None, m_unknown_top(key)) for key in TOP_KEYS]
    check_fails(example, example_settings(), expected, label="settings")
    check_fails(example, None, expected, label="none")
    assert expected[0][3:] == (
        'Unknown key "zzz". The keys are week, monday, tuesday, wednesday, thursday, friday, '
        "saturday, and sunday.",
        "未知键“zzz”。可用的键：week、monday、tuesday、wednesday、thursday、friday、"
        "saturday 和 sunday。",
    )
    put_menu(example, 'Week = "2026-W47"', exact=True)
    both = [bad(None, m_missing_key("week")), bad(None, m_unknown_top("Week"))]
    check_fails(example, example_settings(), both)


def test_f06_t47_one_run_reports_every_problem_in_the_order_of_the_design(
    example_folder: DataFolder,
) -> None:
    """The problems come as week, the days Monday to Sunday, and then the other top keys."""
    example = example_folder
    put_menu(
        example,
        "zzz = 1",
        'week = "2026-W48"',
        'aaa = "x"',
        "saturday = []",
        "[sunday]",
        'dinner = ["Rice"]',
        "[monday]",
        "supper = []",
        "dinner = [3]",
        'lunch = "rice"',
        "[funday]",
        exact=True,
    )
    first = bad(AT_WEEK, m_week_not_file_name("2026-W47", "2026-W48"))
    dish = bad(at_dish("monday", "dinner", 1), M_NOT_A_DISH)
    lunch = bad(at_key("monday", "lunch"), m_not_a_list("lunch"))
    saturday = bad(at_day("saturday"), m_not_a_day_table("saturday"))
    sunday = bad(at_key("sunday", "dinner"), m_unknown_recipe("Rice"))
    last = [bad(None, m_unknown_top(key)) for key in ("zzz", "aaa", "funday")]
    supper = at_key("monday", "supper")
    meal = bad(supper, m_unknown_meal("supper", MEALS_LUNCH_DINNER))
    check_fails(example, example_settings(), [first, meal, dish, lunch, saturday, sunday, *last])
    key = bad(supper, m_unknown_day_key("supper"))
    check_fails(example, None, [first, key, dish, lunch, saturday, sunday, *last])


def test_f06_t48_a_problem_of_read_toml_is_the_only_problem_and_a_byte_order_mark_is_fine(
    example_folder: DataFolder, default_int_limit: None
) -> None:
    """The file, its syntax, and its numbers give one problem, with settings and with none."""
    example = example_folder
    menu = example.menu_file("2026-W47")
    original = menu.read_bytes()
    settings = example_settings()
    later = IsoWeek(2026, 48)
    for given in (settings, None):
        missing = bad(None, M_FILE_MISSING, "menus/2026-W48.toml")
        check_fails(example, given, [missing], week=later, label=(1, given))
    menu.unlink()
    menu.mkdir()
    for given in (settings, None):
        check_fails(example, given, [bad(None, M_FILE_IS_FOLDER)], label=(2, given))
    menu.rmdir()
    broken = (
        (b'week = "2026-W47"\n\xff\n', 2, M_NOT_UTF8),
        (b'week = "2026-W47\n', 1, M_MISSING_QUOTE),
        (b"[monday]\ndinner = []\n[monday]\n", 3, M_DEFINED_TWICE),
        (
            b'week = "2026-W47"\n[monday]\ndinner = [{ recipe = "rice", servings = 1'
            + b"0" * 4300
            + b" }]\n",
            3,
            M_NUMBER_TOO_LONG,
        ),
    )
    for number, (data, line, message) in enumerate(broken, start=3):
        put_bytes(menu, data)
        for given in (settings, None):
            check_fails(example, given, [bad(at_line(line), message)], label=(number, given))
    put_bytes(menu, b"\xef\xbb\xbf" + original)
    check_reads(example, settings, example_filled(), week=week47())
