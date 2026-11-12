"""Tests of F06 joined with the readers of F04 and F05 and with main (T49 to T54)."""

import io
from datetime import date
from pathlib import Path

from f03_support import write
from f05_support import in_folder, make_home, run_main
from f06_support import (
    MEALS_BREAKFAST_DINNER,
    MEALS_DINNER,
    MEALS_LUNCH,
    MENU_PATH,
    TODAY,
    at_key,
    bad,
    breakfast_dinner,
    check_fails,
    check_reads,
    dinner_only,
    every_meal,
    example_filled,
    example_menu,
    example_settings,
    ids_of,
    lunch_only,
    m_unknown_meal,
    make_menu,
    menu_show_command,
    mistakes,
    put_menu,
    read_menu,
    typo,
    week47,
)
from recipe_menu.app import Context, first_error, problem_lines, stop_at_error
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, list_menu_weeks, read_week_menu, short_date
from recipe_menu.settings import read_settings

EN, ZH = Lang.EN, Lang.ZH

NEW_MENU = (
    "# 2026-W47: 16 to 22 November 2026",
    '# A dish is a recipe ID, such as "tomato-egg",',
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
    'week = "2026-W47"',
    *(
        line
        for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
        for line in ("", f"[{day}]", "lunch = []", "dinner = []")
    ),
)
ROWS = (
    ("Mon 16 Nov", "周一 11月16日"),
    ("Tue 17 Nov", "周二 11月17日"),
    ("Wed 18 Nov", "周三 11月18日"),
    ("Thu 19 Nov", "周四 11月19日"),
    ("Fri 20 Nov", "周五 11月20日"),
    ("Sat 21 Nov", "周六 11月21日"),
    ("Sun 22 Nov", "周日 11月22日"),
)
COUNTS = (3, 2, 0, 0, 0, 1, 3)


def test_f06_t49_the_file_of_menu_new_reads_with_every_slot_empty(
    example_folder: DataFolder,
) -> None:
    """The F11 prototype file gives no problem, and its first comment holds the week."""
    example = example_folder
    put_menu(example, *NEW_MENU, exact=True)
    for settings in (example_settings(), every_meal(), dinner_only()):
        check_reads(example, settings, label=settings.meals)
    assert read_menu(example, None) == (None, ())
    menu, _ = read_menu(example, example_settings())
    assert menu is not None
    assert len(menu.slots) == 14
    assert f"# {menu.week}: {menu.week.date_range.get(EN)}" == NEW_MENU[0]
    assert menu == make_menu(week47(), example_settings().meals)


def test_f06_t50_the_example_menu_with_other_settings(example_folder: DataFolder) -> None:
    """A meal that the settings do not name is an error only when it holds a dish."""
    example = example_folder
    saturday = bad(at_key("saturday", "lunch"), m_unknown_meal("lunch", MEALS_DINNER))
    check_fails(example, dinner_only(), [saturday], label="dinner only")
    dinners = [
        bad(at_key(day, "dinner"), m_unknown_meal("dinner", MEALS_LUNCH))
        for day in ("monday", "tuesday", "sunday")
    ]
    check_fails(example, lunch_only(), dinners, label="lunch only")
    both = bad(at_key("saturday", "lunch"), m_unknown_meal("lunch", MEALS_BREAKFAST_DINNER))
    check_fails(example, breakfast_dinner(), [both], label="breakfast and dinner")
    settings = every_meal()
    check_reads(example, settings, example_filled(3), label="every meal")
    menu, _ = read_menu(example, settings)
    assert menu == example_menu(settings)


def test_f06_t51_the_problems_give_the_lines_of_the_prototypes_through_f05(
    example_folder: DataFolder,
) -> None:
    """``problem_lines`` and ``stop_at_error`` write the lines of F07, v0.1-S07, and F11."""
    example = example_folder
    path = str(MENU_PATH)
    original = example.menu_file("2026-W47").read_text(encoding="utf-8")
    typo(example)
    settings = example_settings()
    _, problems = read_menu(example, settings)
    assert len(problems) == 1
    english = problem_lines(problems[0], EN)
    assert english == (f"{path}, Monday dinner", 'Unknown recipe "tomato-eggs".')
    assert problem_lines(problems[0], ZH) == (f"{path}，周一晚餐", "未知菜谱“tomato-eggs”。")
    out, err = io.StringIO(), io.StringIO()
    error = first_error(problems)
    assert error is not None
    assert stop_at_error(Context(EN, example, settings, out, err, TODAY), error) == 1
    assert out.getvalue() == ""
    assert err.getvalue() == (
        f'{path}, Monday dinner\n  Unknown recipe "tomato-eggs".\n'
        'Run "recipe-menu check" to see every problem.\n'
    )

    write(example.menu_file("2026-W47"), original)
    mistakes(example)
    _, problems = read_menu(example, settings)
    assert [problem_lines(problem, EN) for problem in problems] == [
        (f"{path}, week", "The file name says 2026-W47, but the file says 2026-W48."),
        (f"{path}, Friday supper", 'Unknown meal "supper". The settings name lunch and dinner.'),
        (f"{path}, Sunday dinner, dish 1", "Servings must be a whole number of 1 or more, not 0."),
    ]


def test_f06_t52_a_menu_show_stand_in_gives_the_outputs_of_v0_1_s15_through_main(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A wrong week gives exit code 2 with no hint, and no week, this, and next follow today."""
    example = example_folder
    home = make_home(tmp_path)
    commands = [menu_show_command()]
    environ = in_folder(example.root)
    path = str(MENU_PATH)

    def show(*argv: str, today: date = TODAY) -> tuple[int, str, str]:
        """Runs ``main`` with the stand-in and gives ``(code, out, err)``."""
        return run_main(
            home, "menu", "show", *argv, environ=environ, commands=commands, today=today
        )

    tail = 'is not a week. Write an ISO week such as 2026-W47, "this", or "next".\n'
    assert show("2026-W99") == (2, "", f'"2026-W99" {tail}')
    zh = "不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。\n"
    assert show("2026-W99", "--lang", "zh") == (2, "", f"“2026-W99”{zh}")
    assert show("Next") == (2, "", f'"Next" {tail}')
    for argv in ((), ("this",)):
        assert show(*argv) == (1, "", "No menu for 2026-W46\n")
    english = "2026-W47, 16 to 22 November 2026\n" + "".join(
        f"{row[0]}: {count}\n" for row, count in zip(ROWS, COUNTS, strict=True)
    )
    for argv in (("next",), ("2026-W47",)):
        assert show(*argv) == (0, english, "")
    chinese = "2026-W47, 2026年11月16日至22日\n" + "".join(
        f"{row[1]}: {count}\n" for row, count in zip(ROWS, COUNTS, strict=True)
    )
    assert show("next", "--lang", "zh") == (0, chinese, "")
    assert show(today=date(2026, 11, 16)) == (0, english, "")

    typo(example)
    english_error = (
        f'{path}, Monday dinner\n  Unknown recipe "tomato-eggs".\n'
        'Run "recipe-menu check" to see every problem.\n'
    )
    assert show("next") == (1, "", english_error)
    chinese_error = (
        f"{path}，周一晚餐\n  未知菜谱“tomato-eggs”。\n运行“recipe-menu check”查看所有问题。\n"
    )
    assert show("next", "--lang", "zh") == (1, "", chinese_error)


def test_f06_t53_the_example_menu_gives_the_table_of_the_f11_prototype(
    example_folder: DataFolder,
) -> None:
    """The dishes of each cell, the days of the rows, and the week in the first comment."""
    example = example_folder
    settings, _ = read_settings(example)
    ids = ids_of(example)
    menu, problems = read_week_menu(example, week47(), settings, ids)
    assert problems == ()
    assert menu == make_menu(week47(), settings.meals, example_filled())
    assert sum(1 for slot in menu.slots if slot.dishes) == 4
    assert sum(len(slot.dishes) for slot in menu.slots) == 9
    for index, (en, zh) in enumerate(ROWS):
        cell = short_date(menu.week.dates[index])
        assert (cell.get(EN), cell.get(ZH)) == (en, zh)
    assert str(menu.week) == "2026-W47"
    heading = menu.week.date_range
    assert (heading.get(EN), heading.get(ZH)) == ("16 to 22 November 2026", "2026年11月16日至22日")
    first = example.menu_file("2026-W47").read_text(encoding="utf-8").split("\n")[0]
    assert first == f"# {menu.week}: {heading.get(EN)}"


def test_f06_t54_the_flow_of_check_reads_53_week_menus_with_one_listing(
    example_folder: DataFolder,
) -> None:
    """One listing of ``menus/``, one set of recipe IDs, and one read of each week."""
    example = example_folder
    original = example.menu_file("2026-W47").read_bytes()
    expected = [IsoWeek(2026, number) for number in range(1, 54)]
    for week in expected:
        if week != week47():
            text = original.replace(b'week = "2026-W47"', f'week = "{week}"'.encode())
            example.menu_file(str(week)).write_bytes(text)
    weeks, problems = list_menu_weeks(example)
    assert weeks == tuple(expected)
    assert problems == ()
    recipe_ids = ids_of(example)
    settings = example_settings()
    dishes = 0
    for week in weeks:
        menu, problems = read_week_menu(example, week, settings, recipe_ids)
        assert problems == (), week
        assert menu == make_menu(week, settings.meals, example_filled()), week
        dishes += sum(len(slot.dishes) for slot in menu.slots)
    assert dishes == 477
