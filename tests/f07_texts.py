"""The texts of F07 that the tests share: the places and the messages of the readers.

Each text is a pair of the English and the Chinese text, written out in full as a literal, so a
test does not import a message of the code. A problem of an expected report is a ``Prob``.
Nothing here calls an interface of ``check`` when the module is imported.
"""

from typing import NamedTuple

from f06_support import at_dish, at_key
from recipe_menu.lang import BiText, Lang

EN, ZH = Lang.EN, Lang.ZH

type Msg = tuple[str, str]
type Result = tuple[int, str, str]


class Prob(NamedTuple):
    """A problem of an expected report.

    Attributes:
        file: The file with ``/`` separators, such as ``recipes/mapo-tofu.toml``.
        place: The place in English and in Chinese, or ``None`` for a problem of the whole file.
        msg: The message in English and in Chinese.
    """

    file: str
    place: Msg | None
    msg: Msg


# ---------------------------------------------------------------- places


def at(place: BiText) -> Msg:
    """Gives a ``BiText`` place as a pair of the English and the Chinese text."""
    return place.get(EN), place.get(ZH)


def p_line(number: int) -> Msg:
    """The place of a line."""
    return f"line {number}", f"第 {number} 行"


def p_item(number: int) -> Msg:
    """The place of an item of the pantry."""
    return f"item {number}", f"第 {number} 项"


def p_ingredient(number: int) -> Msg:
    """The place of an ingredient."""
    return f"ingredient {number}", f"食材 {number}"


def p_slot(day: str, key: str) -> Msg:
    """The place of a key of a day, such as ``monday`` and ``dinner``."""
    return at(at_key(day, key))


def p_dish(day: str, key: str, number: int) -> Msg:
    """The place of dish N of a key of a day."""
    return at(at_dish(day, key, number))


P_MEALS: Msg = ("meals", "餐次")
P_NAME: Msg = ("name", "名称")
P_SERVINGS: Msg = ("servings", "份数")
P_TAGS: Msg = ("tags", "标签")
P_STEPS: Msg = ("steps", "步骤")
P_WEEK: Msg = ("week", "周次")

# ---------------------------------------------------------------- messages


def m_unknown_ingredient(name: str) -> Msg:
    """The message of an ingredient of a recipe that the catalog does not have."""
    return (
        f'Unknown ingredient "{name}". Add it to the catalog, or use its name in the catalog.',
        f"未知食材“{name}”。请把它加入目录，或改用目录里的名称。",
    )


def m_pantry_ingredient(name: str) -> Msg:
    """The message of an ingredient of the pantry that the catalog does not have."""
    return f'Unknown ingredient "{name}".', f"未知食材“{name}”。"


def m_unknown_tag(tag: str) -> Msg:
    """The message of a tag that the catalog does not have."""
    return (
        f'Unknown tag "{tag}". Add it to the catalog\'s tags.',
        f"未知标签“{tag}”。请把它加入目录里的标签。",
    )


def m_unknown_unit(unit: str, amount: str) -> Msg:
    """The message of an amount with an unknown unit."""
    return f'Unknown unit "{unit}" in "{amount}".', f"数量“{amount}”里有未知单位“{unit}”。"


def m_servings(servings: int) -> Msg:
    """The message of servings below 1."""
    return (
        f"Servings must be a whole number of 1 or more, not {servings}.",
        f"份数必须是不小于 1 的整数，不能是 {servings}。",
    )


def m_steps_key(key: str) -> Msg:
    """The message of an unknown key in ``steps``."""
    return f'Unknown key "{key}". The keys are zh and en.', f"未知键“{key}”。可用的键：zh 和 en。"


def m_category(category: str) -> Msg:
    """The message of an unknown category."""
    return (
        f'Unknown category "{category}". The categories are produce, meat, eggs, staples, '
        "seasonings, and other.",
        f"未知分类“{category}”。现有分类：produce、meat、eggs、staples、seasonings 和 other。",
    )


def m_duplicate_en(name: str, number: int) -> Msg:
    """The message of an English name that ingredient ``number`` has too."""
    return (
        f'The English name "{name}" is also ingredient {number}\'s name. Names must be unique.',
        f"英文名称“{name}”也是食材 {number} 的名称。名称不能重复。",
    )


def m_settings_meal(meal: str) -> Msg:
    """The message of an unknown meal in the settings."""
    return (
        f'Unknown meal "{meal}". The meals are breakfast, lunch, and dinner.',
        f"未知餐次“{meal}”。可用的餐次：breakfast、lunch 和 dinner。",
    )


def m_menu_meal(meal: str, meals: Msg) -> Msg:
    """The message of an unknown meal in a menu, when the settings name the ``meals``."""
    return (
        f'Unknown meal "{meal}". The settings name {meals[0]}.',
        f"未知餐次“{meal}”。设置里的餐次：{meals[1]}。",
    )


def m_day_key(key: str) -> Msg:
    """The message of an unknown key of a day, when there are no settings."""
    return (
        f'Unknown key "{key}". The keys are breakfast, lunch, and dinner.',
        f"未知键“{key}”。可用的键：breakfast、lunch 和 dinner。",
    )


def m_unknown_recipe(recipe: str) -> Msg:
    """The message of a dish that names no recipe."""
    return f'Unknown recipe "{recipe}".', f"未知菜谱“{recipe}”。"


def m_week_name(name: str, week: str) -> Msg:
    """The message of a ``week`` that differs from the file name."""
    return (
        f"The file name says {name}, but the file says {week}.",
        f"文件名是 {name}，但文件里写的是 {week}。",
    )


NO_EN_NAME: Msg = (
    "No English name. Commands show the Chinese name instead.",
    "没有英文名称。命令会改为显示中文名称。",
)
NO_EN_NOTE: Msg = (
    "No English note. Commands show the Chinese note instead.",
    "没有英文备注。命令会改为显示中文备注。",
)
NO_EN_STEPS: Msg = (
    "No English steps. Commands show the Chinese steps instead.",
    "没有英文步骤。命令会改为显示中文步骤。",
)
NOT_A_RECIPE_ID: Msg = (
    'This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", '
    'and starts with a letter or a digit, such as "tomato-egg". Rename the file.',
    "这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，"
    "比如“tomato-egg”。请给文件改名。",
)
NOT_A_WEEK_NAME: Msg = (
    "This file name is not an ISO week such as 2026-W47. Rename the file.",
    "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。",
)
TOML_ENDING_NOT_SMALL: Msg = (
    'The file name must end with ".toml" in small letters. Rename the file.',
    "文件名必须以小写的“.toml”结尾。请给文件改名。",
)
ITEM_NOT_A_TEXT: Msg = (
    "This item must be a text in quotation marks.",
    "这一项必须是放在引号里的文字。",
)
FILE_MISSING: Msg = ("The file is missing.", "文件不存在。")
FILE_IS_FOLDER: Msg = (
    "The file cannot be read: it is a folder.",
    "无法读取文件：它是一个文件夹。",
)
MISSING_BRACKET: Msg = (
    'The file cannot be read: a closing "]" is missing.',
    "无法读取文件：缺少右方括号“]”。",
)
MISSING_BRACE: Msg = (
    'The file cannot be read: a closing "}" is missing. A table in braces must be on one line.',
    "无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。",
)
FOLDER_MISSING: Msg = ("The folder is missing.", "文件夹不存在。")
FOLDER_IS_FILE: Msg = (
    "The folder cannot be read: it is a file.",
    "无法读取文件夹：它是一个文件。",
)
FOLDER_ACCESS_DENIED: Msg = (
    "The folder cannot be read: access is denied.",
    "无法读取文件夹：没有访问权限。",
)


MENU_FILE = "menus/2026-W47.toml"
PORK = Prob("recipes/red-braised-pork.toml", P_STEPS, NO_EN_STEPS)
MAPO = Prob("recipes/mapo-tofu.toml", p_ingredient(3), m_unknown_ingredient("豆瓣酱"))
TYPO = Prob(MENU_FILE, p_slot("monday", "dinner"), m_unknown_recipe("tomato-eggs"))
DISHES = [
    Prob(MENU_FILE, p_slot(day, meal), m_unknown_recipe(recipe))
    for day, meal, recipe in (
        ("monday", "dinner", "tomato-egg"),
        ("monday", "dinner", "choy-sum"),
        ("monday", "dinner", "rice"),
        ("tuesday", "dinner", "mapo-tofu"),
        ("tuesday", "dinner", "rice"),
        ("saturday", "lunch", "tomato-egg-noodles"),
        ("sunday", "dinner", "cola-wings"),
        ("sunday", "dinner", "choy-sum"),
        ("sunday", "dinner", "rice"),
    )
]
