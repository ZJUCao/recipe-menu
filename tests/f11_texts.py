"""The expected texts of F11: the outputs of both commands, the new file, and the messages.

Every text but the output of an empty menu is written out as a literal, so a test imports no
message of ``menu`` or ``menus`` and reads no prototype file. The output of an empty menu takes its
dates from F06 and its table layout from F02, as the test plan says, and uses no code of F11.
Nothing here calls an interface of F11 when the module is imported. The module holds the helps,
the blocks A to F of the test plan as lists of lines, the menu file of the prototype, the dates of
the case weeks, the labels and headings of the meals, the meal sets, the ``menu show`` output of
the example week, and the outputs of a new file, an existing file, a failure, a file left behind,
a missing menu, a value that is not a week, and an empty menu. U+00D7 and U+2014 are written as
escapes.
"""

from collections.abc import Sequence

from f05_texts import HELP_EN_LINES, HELP_ZH_LINES, Msg
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, short_date
from recipe_menu.settings import Meal
from recipe_menu.text import format_table

EN, ZH = Lang.EN, Lang.ZH

LUNCH_DINNER = (Meal.LUNCH, Meal.DINNER)
EVERY_MEAL = (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER)

# ---------------------------------------------------------------- the help

HELP = [line for line in HELP_EN_LINES if not line.startswith("  shop ")]
HELP_ZH = [line for line in HELP_ZH_LINES if not line.startswith("  shop ")]

# ---------------------------------------------------------------- the blocks of outputs

BLOCK_A = [
    "Menu for 2026-W48, 23 to 29 November 2026",
    "",
    "Day          Lunch                     Dinner",
    "Mon 23 Nov   Mapo tofu \u00d72              Steamed rice \u00d72",
    "                                       Steamed rice \u00d72",
    "Tue 24 Nov   \u2014                         \u2014",
    "Wed 25 Nov   \u2014                         \u2014",
    "Thu 26 Nov   \u2014                         \u2014",
    "Fri 27 Nov   Stir-fried choy sum \u00d710   \u2014",
    "Sat 28 Nov   \u2014                         \u2014",
    "Sun 29 Nov   \u2014                         Red-braised pork belly \u00d72",
    "",
    "4 meals, 5 dishes. \u00d7n: servings.",
]

BLOCK_A_ZH = [
    "2026-W48 菜单，2026年11月23日至29日",
    "",
    "日期            午餐           晚餐",
    "周一 11月23日   麻婆豆腐 \u00d72    米饭 \u00d72",
    "                               米饭 \u00d72",
    "周二 11月24日   \u2014              \u2014",
    "周三 11月25日   \u2014              \u2014",
    "周四 11月26日   \u2014              \u2014",
    "周五 11月27日   清炒菜心 \u00d710   \u2014",
    "周六 11月28日   \u2014              \u2014",
    "周日 11月29日   \u2014              红烧肉 \u00d72",
    "",
    "4 餐，5 道菜。\u00d7n：份数。",
]

BLOCK_B = [
    "Menu for 2026-W49, 30 November to 6 December 2026",
    "",
    "Day          Breakfast",
    "Mon 30 Nov   \u2014",
    "Tue 1 Dec    Boiled egg \u00d72",
    "             蒸蛋 \u00d71",
    "Wed 2 Dec    \u2014",
    "Thu 3 Dec    \u2014",
    "Fri 4 Dec    \u2014",
    "Sat 5 Dec    \u2014",
    "Sun 6 Dec    Boiled water \u00d72",
    "",
    "2 meals, 3 dishes. \u00d7n: servings.",
]

BLOCK_B_ZH = [
    "2026-W49 菜单，2026年11月30日至12月6日",
    "",
    "日期            早餐",
    "周一 11月30日   \u2014",
    "周二 12月1日    Boiled egg \u00d72",
    "                蒸蛋 \u00d71",
    "周三 12月2日    \u2014",
    "周四 12月3日    \u2014",
    "周五 12月4日    \u2014",
    "周六 12月5日    \u2014",
    "周日 12月6日    白开水 \u00d72",
    "",
    "2 餐，3 道菜。\u00d7n：份数。",
]

BLOCK_C = [
    "Menu for 2026-W50, 7 to 13 December 2026",
    "",
    "Day          Lunch               Dinner",
    "Mon 7 Dec    A long first line   \u2014",
    "             end \u00d72",
    "             Steamed rice \u00d72",
    "Tue 8 Dec    \u2014                   \u2014",
    "Wed 9 Dec    \u2014                   \u2014",
    "Thu 10 Dec   \u2014                   \u2014",
    "Fri 11 Dec   \u2014                   \u2014",
    "Sat 12 Dec   \u2014                   \u2014",
    "Sun 13 Dec   \u2014                   \u2014",
    "",
    "1 meal, 2 dishes. \u00d7n: servings.",
]

BLOCK_C_ZH = [
    "2026-W50 菜单，2026年12月7日至13日",
    "",
    "日期            午餐           晚餐",
    "周一 12月7日    长长的第一行   \u2014",
    "                尾 \u00d72",
    "                米饭 \u00d72",
    "周二 12月8日    \u2014              \u2014",
    "周三 12月9日    \u2014              \u2014",
    "周四 12月10日   \u2014              \u2014",
    "周五 12月11日   \u2014              \u2014",
    "周六 12月12日   \u2014              \u2014",
    "周日 12月13日   \u2014              \u2014",
    "",
    "1 餐，2 道菜。\u00d7n：份数。",
]

BLOCK_E = [
    "Menu for 2026-W48, 23 to 29 November 2026",
    "",
    "Day          Breakfast                    Lunch   Dinner",
    "Mon 23 Nov   Tomato and egg stir-fry \u00d73   \u2014       \u2014",
    "Tue 24 Nov   \u2014                            \u2014       \u2014",
    "Wed 25 Nov   \u2014                            \u2014       \u2014",
    "Thu 26 Nov   \u2014                            \u2014       \u2014",
    "Fri 27 Nov   \u2014                            \u2014       \u2014",
    "Sat 28 Nov   \u2014                            \u2014       \u2014",
    "Sun 29 Nov   \u2014                            \u2014       \u2014",
    "",
    "1 meal, 1 dish. \u00d7n: servings.",
]

BLOCK_E_ZH = [
    "2026-W48 菜单，2026年11月23日至29日",
    "",
    "日期            早餐          午餐   晚餐",
    "周一 11月23日   番茄炒蛋 \u00d73   \u2014      \u2014",
    "周二 11月24日   \u2014             \u2014      \u2014",
    "周三 11月25日   \u2014             \u2014      \u2014",
    "周四 11月26日   \u2014             \u2014      \u2014",
    "周五 11月27日   \u2014             \u2014      \u2014",
    "周六 11月28日   \u2014             \u2014      \u2014",
    "周日 11月29日   \u2014             \u2014      \u2014",
    "",
    "1 餐，1 道菜。\u00d7n：份数。",
]

BLOCK_D = [
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    "Day          Breakfast   Lunch                       Dinner",
    "Mon 16 Nov   \u2014           \u2014                           "
    "Tomato and egg stir-fry \u00d73",
    "                                                     Stir-fried choy sum \u00d73",
    "                                                     Steamed rice \u00d73",
    "Tue 17 Nov   \u2014           \u2014                           Mapo tofu \u00d73",
    "                                                     Steamed rice \u00d73",
    "Wed 18 Nov   \u2014           \u2014                           \u2014",
    "Thu 19 Nov   \u2014           \u2014                           \u2014",
    "Fri 20 Nov   \u2014           \u2014                           \u2014",
    "Sat 21 Nov   \u2014           Tomato and egg noodles \u00d73   \u2014",
    "Sun 22 Nov   \u2014           \u2014                           Cola chicken wings \u00d74",
    "                                                     Stir-fried choy sum \u00d74",
    "                                                     Steamed rice \u00d74",
    "",
    "4 meals, 9 dishes. \u00d7n: servings.",
]

BLOCK_F47 = [
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    "Day          Lunch   Dinner",
    "Mon 16 Nov   \u2014       \u2014",
    "Tue 17 Nov   \u2014       \u2014",
    "Wed 18 Nov   \u2014       \u2014",
    "Thu 19 Nov   \u2014       \u2014",
    "Fri 20 Nov   \u2014       \u2014",
    "Sat 21 Nov   \u2014       \u2014",
    "Sun 22 Nov   \u2014       \u2014",
    "",
    "The menu has no dishes yet.",
]

BLOCK_F47_ZH = [
    "2026-W47 菜单，2026年11月16日至22日",
    "",
    "日期            午餐   晚餐",
    "周一 11月16日   \u2014      \u2014",
    "周二 11月17日   \u2014      \u2014",
    "周三 11月18日   \u2014      \u2014",
    "周四 11月19日   \u2014      \u2014",
    "周五 11月20日   \u2014      \u2014",
    "周六 11月21日   \u2014      \u2014",
    "周日 11月22日   \u2014      \u2014",
    "",
    "这个菜单还没有菜。",
]

BLOCK_F53 = [
    "Menu for 2026-W53, 28 December 2026 to 3 January 2027",
    "",
    "Day          Lunch   Dinner",
    "Mon 28 Dec   \u2014       \u2014",
    "Tue 29 Dec   \u2014       \u2014",
    "Wed 30 Dec   \u2014       \u2014",
    "Thu 31 Dec   \u2014       \u2014",
    "Fri 1 Jan    \u2014       \u2014",
    "Sat 2 Jan    \u2014       \u2014",
    "Sun 3 Jan    \u2014       \u2014",
    "",
    "The menu has no dishes yet.",
]

BLOCK_F53_ZH = [
    "2026-W53 菜单，2026年12月28日至2027年1月3日",
    "",
    "日期            午餐   晚餐",
    "周一 12月28日   \u2014      \u2014",
    "周二 12月29日   \u2014      \u2014",
    "周三 12月30日   \u2014      \u2014",
    "周四 12月31日   \u2014      \u2014",
    "周五 1月1日     \u2014      \u2014",
    "周六 1月2日     \u2014      \u2014",
    "周日 1月3日     \u2014      \u2014",
    "",
    "这个菜单还没有菜。",
]

BLOCK_F23 = [
    "Menu for 2026-W23, 1 to 7 June 2026",
    "",
    "Day         Lunch   Dinner",
    "Mon 1 Jun   \u2014       \u2014",
    "Tue 2 Jun   \u2014       \u2014",
    "Wed 3 Jun   \u2014       \u2014",
    "Thu 4 Jun   \u2014       \u2014",
    "Fri 5 Jun   \u2014       \u2014",
    "Sat 6 Jun   \u2014       \u2014",
    "Sun 7 Jun   \u2014       \u2014",
    "",
    "The menu has no dishes yet.",
]

BLOCK_F23_ZH = [
    "2026-W23 菜单，2026年6月1日至7日",
    "",
    "日期          午餐   晚餐",
    "周一 6月1日   \u2014      \u2014",
    "周二 6月2日   \u2014      \u2014",
    "周三 6月3日   \u2014      \u2014",
    "周四 6月4日   \u2014      \u2014",
    "周五 6月5日   \u2014      \u2014",
    "周六 6月6日   \u2014      \u2014",
    "周日 6月7日   \u2014      \u2014",
    "",
    "这个菜单还没有菜。",
]

SHOW_47 = [
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    "Day          Lunch                       Dinner",
    "Mon 16 Nov   \u2014                           Tomato and egg stir-fry \u00d72",
    "                                         Stir-fried choy sum \u00d72",
    "                                         Steamed rice \u00d72",
    "Tue 17 Nov   \u2014                           Mapo tofu \u00d72",
    "                                         Steamed rice \u00d72",
    "Wed 18 Nov   \u2014                           \u2014",
    "Thu 19 Nov   \u2014                           \u2014",
    "Fri 20 Nov   \u2014                           \u2014",
    "Sat 21 Nov   Tomato and egg noodles \u00d72   \u2014",
    "Sun 22 Nov   \u2014                           Cola chicken wings \u00d74",
    "                                         Stir-fried choy sum \u00d74",
    "                                         Steamed rice \u00d74",
    "",
    "4 meals, 9 dishes. \u00d7n: servings.",
]

SHOW_47_ZH = [
    "2026-W47 菜单，2026年11月16日至22日",
    "",
    "日期            午餐            晚餐",
    "周一 11月16日   \u2014               番茄炒蛋 \u00d72",
    "                                清炒菜心 \u00d72",
    "                                米饭 \u00d72",
    "周二 11月17日   \u2014               麻婆豆腐 \u00d72",
    "                                米饭 \u00d72",
    "周三 11月18日   \u2014               \u2014",
    "周四 11月19日   \u2014               \u2014",
    "周五 11月20日   \u2014               \u2014",
    "周六 11月21日   番茄鸡蛋面 \u00d72   \u2014",
    "周日 11月22日   \u2014               可乐鸡翅 \u00d74",
    "                                清炒菜心 \u00d74",
    "                                米饭 \u00d74",
    "",
    "4 餐，9 道菜。\u00d7n：份数。",
]

PROTOTYPE_FILE_TEXT = (
    "# 2026-W47: 16 to 22 November 2026\n"
    '# A dish is a recipe ID, such as "tomato-egg",\n'
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.\n'
    'week = "2026-W47"\n'
    "\n"
    "[monday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[tuesday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[wednesday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[thursday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[friday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[saturday]\n"
    "lunch = []\n"
    "dinner = []\n"
    "\n"
    "[sunday]\n"
    "lunch = []\n"
    "dinner = []\n"
)

PROTOTYPE_FILE = PROTOTYPE_FILE_TEXT.encode("utf-8")

# ---------------------------------------------------------------- the dates of the weeks

# The dates of each week of the cases, in English and in Chinese.
DATES: dict[str, Msg] = {
    "2020-W53": ("28 December 2020 to 3 January 2021", "2020年12月28日至2021年1月3日"),
    "2026-W01": ("29 December 2025 to 4 January 2026", "2025年12月29日至2026年1月4日"),
    "2026-W02": ("5 to 11 January 2026", "2026年1月5日至11日"),
    "2026-W23": ("1 to 7 June 2026", "2026年6月1日至7日"),
    "2026-W46": ("9 to 15 November 2026", "2026年11月9日至15日"),
    "2026-W47": ("16 to 22 November 2026", "2026年11月16日至22日"),
    "2026-W48": ("23 to 29 November 2026", "2026年11月23日至29日"),
    "2026-W49": ("30 November to 6 December 2026", "2026年11月30日至12月6日"),
    "2026-W50": ("7 to 13 December 2026", "2026年12月7日至13日"),
    "2026-W52": ("21 to 27 December 2026", "2026年12月21日至27日"),
    "2026-W53": ("28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日"),
    "2027-W01": ("4 to 10 January 2027", "2027年1月4日至10日"),
}

# The labels of the meals in a sentence, and the headings of their columns.
LABELS: dict[Meal, Msg] = {
    Meal.BREAKFAST: ("breakfast", "早餐"),
    Meal.LUNCH: ("lunch", "午餐"),
    Meal.DINNER: ("dinner", "晚餐"),
}
HEADINGS: dict[Meal, Msg] = {
    Meal.BREAKFAST: ("Breakfast", "早餐"),
    Meal.LUNCH: ("Lunch", "午餐"),
    Meal.DINNER: ("Dinner", "晚餐"),
}

# ---------------------------------------------------------------- the lines of the commands


def new(path: object, dates: str, meals: str) -> list[str]:
    """Gives the three lines of a new menu in English."""
    return [
        f"Created {path} for {dates}:",
        f"7 days with {meals}, all empty.",
        'Add recipe IDs to the meals, then run "recipe-menu check".',
    ]


def new_zh(path: object, dates: str, meals: str) -> list[str]:
    """Gives the three lines of a new menu in Chinese."""
    return [
        f"已创建 {path}，日期为 {dates}：",
        f"共 7 天，每天有{meals}，都还是空的。",
        "在各餐里填上菜谱 ID，然后运行“recipe-menu check”。",
    ]


def exists(path: object) -> str:
    """Gives the refusal of ``menu new`` in English."""
    return f"{path} already exists. Nothing was changed."


def exists_zh(path: object) -> str:
    """Gives the refusal of ``menu new`` in Chinese."""
    return f"{path} 已存在。没有做任何修改。"


def fail(path: object, msg: Msg) -> list[str]:
    """Gives the three lines of a failure of ``menu new`` in English."""
    return [str(path), f"  {msg[0]}", "Nothing was changed."]


def fail_zh(path: object, msg: Msg) -> list[str]:
    """Gives the three lines of a failure of ``menu new`` in Chinese."""
    return [str(path), f"  {msg[1]}", "没有做任何修改。"]


def left(path: object, msg: Msg, week: str) -> list[str]:
    """Gives the three lines of a failure that left the file, in English."""
    third = (
        "menu new could not remove the file that it created. "
        f'Delete it, then run "recipe-menu menu new {week}" again.'
    )
    return [str(path), f"  {msg[0]}", third]


def left_zh(path: object, msg: Msg, week: str) -> list[str]:
    """Gives the three lines of a failure that left the file, in Chinese."""
    third = (
        f"menu new 没能删除它创建的文件。请删除这个文件，然后再运行“recipe-menu menu new {week}”。"
    )
    return [str(path), f"  {msg[1]}", third]


def no_menu(week: str) -> str:
    """Gives ``NO_MENU`` in English."""
    return f'There is no menu for {week}. Run "recipe-menu menu new {week}" to create it.'


def no_menu_zh(week: str) -> str:
    """Gives ``NO_MENU`` in Chinese."""
    return f"{week} 没有菜单。运行“recipe-menu menu new {week}”创建它。"


def not_a_week(value: str) -> str:
    """Gives ``NOT_A_WEEK`` in English for a value as typed."""
    return f'"{value}" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'


def not_a_week_zh(value: str) -> str:
    """Gives ``NOT_A_WEEK`` in Chinese for a value as typed."""
    return f"“{value}”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。"


def empty(week: str, lang: Lang, meals: Sequence[Meal]) -> list[str]:
    """Gives the lines of ``menu show`` for a week with no dish, in a language.

    The table is laid out with ``format_table`` and no ``min_widths``. Each meal of ``meals``
    shows the dash in every row.
    """
    index = 1 if lang is ZH else 0
    year, number = week.split("-W")
    iso = IsoWeek(int(year), int(number))
    heading = ("Day", "日期")[index]
    ordered = sorted(meals, key=list(Meal).index)
    rows = [[heading, *(HEADINGS[meal][index] for meal in ordered)]]
    rows += [[short_date(day).get(lang), *["\u2014"] * len(ordered)] for day in iso.dates]
    dates = iso.date_range.get(lang)
    top = f"Menu for {week}, {dates}" if lang is EN else f"{week} 菜单，{dates}"
    last = "The menu has no dishes yet." if lang is EN else "这个菜单还没有菜。"
    return [top, "", *format_table(rows), "", last]
