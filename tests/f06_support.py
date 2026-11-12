"""Helpers and example values that the F06 tests share.

Nothing here makes an ``IsoWeek``, a ``Dish``, a ``MealSlot``, a ``WeekMenu``, or a ``Settings``
when the module is imported, because the mock leaves out the checks of their constructors, and
a value made at import would stop pytest from collecting the test files. At import the module
holds only texts, numbers, and tuples of them. Functions make every value, and none calls an
interface of ``menus`` at import.
"""

from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

from f03_support import M_ITEM_EMPTY, m_unknown_key, write
from f04_support import Entry, Msg, check_problems, err
from f05_support import make_command
from recipe_menu.app import Arguments, Command, Context, UsageError, first_error, stop_at_error
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import (
    NOT_A_WEEK,
    Day,
    Dish,
    IsoWeek,
    MealSlot,
    WeekMenu,
    list_menu_weeks,
    read_week_menu,
    short_date,
    week_from_argument,
)
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, Settings

TODAY = date(2026, 11, 10)
MENU_FILE = "menus/2026-W47.toml"
MENU_PATH = Path("menus", "2026-W47.toml")
WEEK_LINE = 'week = "2026-W47"'

DAY_LABELS: dict[str, Msg] = {
    "monday": ("Monday", "周一"),
    "tuesday": ("Tuesday", "周二"),
    "wednesday": ("Wednesday", "周三"),
    "thursday": ("Thursday", "周四"),
    "friday": ("Friday", "周五"),
    "saturday": ("Saturday", "周六"),
    "sunday": ("Sunday", "周日"),
}
MEAL_LABELS: dict[str, Msg] = {
    "breakfast": ("breakfast", "早餐"),
    "lunch": ("lunch", "午餐"),
    "dinner": ("dinner", "晚餐"),
}

# The words that the messages list: ``and_list`` of the meals, and of the keys of each table.
MEALS_LUNCH_DINNER: Msg = ("lunch and dinner", "lunch 和 dinner")
MEALS_EVERY: Msg = ("breakfast, lunch, and dinner", "breakfast、lunch 和 dinner")
MEALS_DINNER: Msg = ("dinner", "dinner")
MEALS_LUNCH: Msg = ("lunch", "lunch")
MEALS_BREAKFAST_DINNER: Msg = ("breakfast and dinner", "breakfast 和 dinner")
WEEK_KEYS: Msg = (
    "week, monday, tuesday, wednesday, thursday, friday, saturday, and sunday",
    "week、monday、tuesday、wednesday、thursday、friday、saturday 和 sunday",
)
DAY_KEYS: Msg = MEALS_EVERY
DISH_KEYS: Msg = ("recipe and servings", "recipe 和 servings")

M_NOT_A_WEEK_NAME: Msg = (
    "This file name is not an ISO week such as 2026-W47. Rename the file.",
    "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。",
)
M_NOT_A_DISH: Msg = (
    'A dish must be a recipe ID in quotation marks, such as "tomato-egg", or a table in braces, '
    'such as { recipe = "tomato-egg", servings = 4 }.',
    '一道菜必须是放在引号里的菜谱 ID，比如 "tomato-egg"，或者是放在花括号里的表，'
    '比如 { recipe = "tomato-egg", servings = 4 }。',
)
M_EMPTY_ITEM: Msg = M_ITEM_EMPTY

# ---------------------------------------------------------------- places

AT_WEEK = BiText("week", "周次")


def at_day(day: str) -> BiText:
    """Gives the place of a day, its label, from the value of the day such as ``monday``."""
    en, zh = DAY_LABELS[day]
    return BiText(en, zh)


def at_key(day: str, key: str) -> BiText:
    """Gives the place of a key of a day.

    A key that is the value of a ``Meal`` gives the day's label and the meal's label, with a space
    in English and none in Chinese. Any other key gives the label and the key, with a space in
    both languages.
    """
    day_en, day_zh = DAY_LABELS[day]
    if key in MEAL_LABELS:
        meal_en, meal_zh = MEAL_LABELS[key]
        return BiText(f"{day_en} {meal_en}", f"{day_zh}{meal_zh}")
    return BiText(f"{day_en} {key}", f"{day_zh} {key}")


def at_dish(day: str, key: str, number: int) -> BiText:
    """Gives the place of dish N of a meal of a day."""
    place = at_key(day, key)
    return BiText(f"{place.get(Lang.EN)}, dish {number}", f"{place.get(Lang.ZH)}，菜品 {number}")


# ---------------------------------------------------------------- messages


def m_unknown_recipe(recipe: str) -> Msg:
    """The message of a recipe that is not known."""
    return (f'Unknown recipe "{recipe}".', f"未知菜谱“{recipe}”。")


def m_week_not_iso(week: str) -> Msg:
    """The message of a ``week`` that is not an ISO week."""
    return (
        f'"week" must be an ISO week such as 2026-W47, not "{week}".',
        f"“week”必须是 2026-W47 这样的 ISO 周，不能是“{week}”。",
    )


def m_week_not_file_name(name: str, week: str) -> Msg:
    """The message of a ``week`` that is not the week of the file name."""
    return (
        f"The file name says {name}, but the file says {week}.",
        f"文件名是 {name}，但文件里写的是 {week}。",
    )


def m_not_a_day_table(key: str) -> Msg:
    """The message of a day that is not a table."""
    return (
        f'"{key}" must be a table. Write the line [{key}], and below it a list of dishes for '
        'each meal, such as dinner = ["tomato-egg"].',
        f"“{key}”必须是表。请写一行 [{key}]，在它下面为每一餐写一个菜的列表，"
        '比如 dinner = ["tomato-egg"]。',
    )


def m_unknown_meal(meal: str, meals: Msg) -> Msg:
    """The message of a key of a day that names no meal of the settings."""
    return (
        f'Unknown meal "{meal}". The settings name {meals[0]}.',
        f"未知餐次“{meal}”。设置里的餐次：{meals[1]}。",
    )


def m_unknown_top(key: str) -> Msg:
    """The message of an unknown key at the top of the file."""
    return m_unknown_key(key, WEEK_KEYS)


def m_unknown_day_key(key: str) -> Msg:
    """The message of an unknown key of a day, when there are no settings."""
    return m_unknown_key(key, DAY_KEYS)


def m_unknown_dish_key(key: str) -> Msg:
    """The message of an unknown key of a dish in braces."""
    return m_unknown_key(key, DISH_KEYS)


def m_not_a_week(text: str) -> Msg:
    """The message of a week that a command line gives and that is not a week."""
    return (
        f'"{text}" is not a week. Write an ISO week such as 2026-W47, "this", or "next".',
        f"“{text}”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。",
    )


def bad(place: BiText | None, msg: Msg, file: str = MENU_FILE) -> Entry:
    """Gives an expected error of a menu file, with its file as a ``/`` path."""
    return err(place, msg, file)


# ---------------------------------------------------------------- values


def week47() -> IsoWeek:
    """Gives ``IsoWeek(2026, 47)``, the week of the example menu."""
    return IsoWeek(2026, 47)


def settings_of(*meals: Meal, servings: int = 2) -> Settings:
    """Gives English settings with the meals and the servings."""
    return Settings(Lang.EN, meals, servings)


def example_settings() -> Settings:
    """Gives the settings of the example folder: lunch and dinner, 2 servings."""
    return settings_of(Meal.LUNCH, Meal.DINNER)


def every_meal() -> Settings:
    """Gives the settings with all three meals and 3 servings."""
    return Settings(Lang.EN, tuple(Meal), 3)


def dinner_only() -> Settings:
    """Gives the settings with dinner only."""
    return settings_of(Meal.DINNER)


def lunch_only() -> Settings:
    """Gives the settings with lunch only."""
    return settings_of(Meal.LUNCH)


def breakfast_dinner() -> Settings:
    """Gives the settings with breakfast and dinner."""
    return settings_of(Meal.BREAKFAST, Meal.DINNER)


def dishes_of(*pairs: tuple[str, int]) -> tuple[Dish, ...]:
    """Gives the dishes of ``(recipe_id, servings)`` pairs."""
    return tuple(Dish(recipe, servings) for recipe, servings in pairs)


def make_menu(
    week: IsoWeek,
    meals: Sequence[Meal],
    filled: Mapping[tuple[Day, Meal], Sequence[Dish]] | None = None,
) -> WeekMenu:
    """Makes the menu whose slots hold the dishes of ``filled``, and no dish elsewhere."""
    given = filled or {}
    slots = tuple(
        MealSlot(day, meal, tuple(given.get((day, meal), ()))) for day in Day for meal in meals
    )
    return WeekMenu(week, tuple(meals), slots)


def example_filled(servings: int = 2) -> dict[tuple[Day, Meal], tuple[Dish, ...]]:
    """Gives the dishes of the example menu, with ``servings`` for the dishes that give none."""
    return {
        (Day.MONDAY, Meal.DINNER): dishes_of(
            ("tomato-egg", servings), ("choy-sum", servings), ("rice", servings)
        ),
        (Day.TUESDAY, Meal.DINNER): dishes_of(("mapo-tofu", servings), ("rice", servings)),
        (Day.SATURDAY, Meal.LUNCH): dishes_of(("tomato-egg-noodles", servings)),
        (Day.SUNDAY, Meal.DINNER): dishes_of(("cola-wings", 4), ("choy-sum", 4), ("rice", 4)),
    }


def example_menu(settings: Settings) -> WeekMenu:
    """Gives the menu that the example menu file gives with the settings."""
    return make_menu(week47(), settings.meals, example_filled(settings.servings))


# ---------------------------------------------------------------- writing and reading menus


def put_menu(folder: DataFolder, *lines: str, exact: bool = False, name: str = "2026-W47") -> None:
    """Writes the menu file ``menus/<name>.toml`` with LF line ends.

    Args:
        folder: The data folder.
        *lines: The lines of the file, without line ends.
        exact: Whether the file holds only ``lines``. Otherwise the line ``week = "2026-W47"``
            comes first.
        name: The file name without ``.toml``.
    """
    head = () if exact else (WEEK_LINE,)
    write(folder.menus / f"{name}.toml", "".join(f"{line}\n" for line in (*head, *lines)))


def ids_of(folder: DataFolder) -> frozenset[str]:
    """Gives the recipe IDs that ``list_recipe_ids`` gives for the folder."""
    return frozenset(list_recipe_ids(folder)[0])


def typo(folder: DataFolder) -> None:
    """Writes the example menu with ``tomato-eggs`` in Monday dinner, as in the F07 prototype."""
    file = folder.menu_file("2026-W47")
    write(file, file.read_text(encoding="utf-8").replace('"tomato-egg"', '"tomato-eggs"'))


def mistakes(folder: DataFolder) -> None:
    """Writes the example menu with the three menu mistakes of v0.1-S07."""
    file = folder.menu_file("2026-W47")
    text = file.read_text(encoding="utf-8")
    text = text.replace('week = "2026-W47"', 'week = "2026-W48"')
    text = text.replace("[friday]\n", "[friday]\nsupper = []\n")
    text = text.replace('"cola-wings", servings = 4', '"cola-wings", servings = 0')
    write(file, text)


def read_menu(
    folder: DataFolder,
    settings: Settings | None,
    ids: frozenset[str] | None = None,
    week: IsoWeek | None = None,
) -> tuple[WeekMenu | None, tuple[Problem, ...]]:
    """Calls ``read_week_menu`` for the week 2026-W47 unless a week is given.

    The recipe IDs are those of ``list_recipe_ids`` unless ``ids`` is given.
    """
    return read_week_menu(
        folder,
        week47() if week is None else week,
        settings,
        ids_of(folder) if ids is None else ids,
    )


def check_fails(
    folder: DataFolder,
    settings: Settings | None,
    expected: Sequence[Entry],
    *,
    ids: frozenset[str] | None = None,
    week: IsoWeek | None = None,
    label: object = "",
) -> None:
    """Reads the menu and checks that there is no menu and that the problems are the expected."""
    menu, problems = read_menu(folder, settings, ids, week)
    assert menu is None, label
    check_problems(problems, expected, label)


def check_reads(
    folder: DataFolder,
    settings: Settings,
    filled: Mapping[tuple[Day, Meal], Sequence[Dish]] | None = None,
    *,
    ids: frozenset[str] | None = None,
    week: IsoWeek | None = None,
    label: object = "",
) -> None:
    """Reads the menu and checks no problems and the menu with the dishes of ``filled``."""
    menu, problems = read_menu(folder, settings, ids, week)
    check_problems(problems, (), label)
    assert menu == make_menu(week47() if week is None else week, settings.meals, filled), label


def check_weeks(
    folder: DataFolder, weeks: Sequence[IsoWeek], expected: Sequence[Entry], label: object = ""
) -> None:
    """Checks the weeks and the problems that ``list_menu_weeks`` gives."""
    got, problems = list_menu_weeks(folder)
    assert isinstance(got, tuple), label
    assert got == tuple(weeks), label
    check_problems(problems, expected, label)


def name_entries(*names: str) -> list[Entry]:
    """Gives the expected ``NOT_A_WEEK_NAME`` errors of file names in ``menus/``, with no place."""
    return [bad(None, M_NOT_A_WEEK_NAME, f"menus/{name}") for name in names]


# ---------------------------------------------------------------- the stand-in menu show


def menu_show_command() -> Command:
    """Makes the ``menu show`` stand-in that uses F06 as design section 2 plans for F11."""

    def run(context: Context, arguments: Arguments) -> int:
        """Shows the week of the argument, or stops with the first error of its file."""
        value = arguments.values[0] if arguments.values else None
        week = week_from_argument(value, context.today)
        if week is None:
            assert value is not None
            raise UsageError(NOT_A_WEEK, None, week=value)
        weeks, _ = list_menu_weeks(context.folder)
        if week not in weeks:
            context.err.write(f"No menu for {week}\n")
            return 1
        ids = ids_of(context.folder)
        menu, problems = read_week_menu(context.folder, week, context.settings, ids)
        if menu is None:
            error = first_error(problems)
            assert error is not None
            return stop_at_error(context, error)
        lang = context.lang
        context.out.write(f"{week}, {week.date_range.get(lang)}\n")
        for day, when in zip(Day, week.dates, strict=True):
            count = sum(len(slot.dishes) for slot in menu.slots if slot.day is day)
            context.out.write(f"{short_date(when).get(lang)}: {count}\n")
        return 0

    return make_command("MENU_SHOW", run)
