"""The texts of F05 that the tests share: the help, the hint lines, and the settings messages.

Every text is written out in full as a literal, so a test does not import a message of the code.
"""

from collections.abc import Sequence
from pathlib import Path

from recipe_menu.datafile import Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import RUN_CHECK, RUN_HELP_FOR_COMMANDS, RUN_HELP_FOR_OPTIONS

EN, ZH = Lang.EN, Lang.ZH

type Result = tuple[int, str, str]
type Msg = tuple[str, str]
type Expected = tuple[BiText | None, str, str]

# --------------------------------------------------------------------- the help texts

HELP_EN_LINES = (
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "",
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "",
    "Commands:",
    "  init               Create the data folder with example data.",
    "  check              Check every data file for mistakes.",
    "  list               List the recipes.",
    "  show ID            Show one recipe.",
    "  search WORD...     Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]    Create an empty week menu.",
    "  menu show [WEEK]   Show a week menu.",
    "  shop [WEEK]        Make the shopping list of a week menu.",
    "",
    "Options:",
    "  --lang en|zh       The language of the output. Default: the settings, else English.",
    "  --data FOLDER      The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version          Show the version.",
    "  --help             Show this help.",
    "",
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
)
HELP_ZH_LINES = (
    "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
    "",
    "保存菜谱，排一周的菜单，并生成它的购物清单。",
    "",
    "命令：",
    "  init               创建数据文件夹和示例数据。",
    "  check              检查每个数据文件有没有错误。",
    "  list               列出菜谱。",
    "  show ID            查看一个菜谱。",
    "  search 词...       按名称、食材或标签找菜谱。",
    "  menu new [周]      创建一个空的周菜单。",
    "  menu show [周]     查看一个周菜单。",
    "  shop [周]          生成一个周菜单的购物清单。",
    "",
    "选项：",
    "  --lang en|zh       输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹      数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version          显示版本。",
    "  --help             显示这份帮助。",
    "",
    "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。",
)
HELP_EN = "".join(f"{line}\n" for line in HELP_EN_LINES)
HELP_ZH = "".join(f"{line}\n" for line in HELP_ZH_LINES)

BARE_HELP_EN_LINES = (
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "",
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "",
    "Commands:",
    "",
    "Options:",
    "  --lang en|zh    The language of the output. Default: the settings, else English.",
    "  --data FOLDER   The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version       Show the version.",
    "  --help          Show this help.",
    "",
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
)
BARE_HELP_ZH_LINES = (
    "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
    "",
    "保存菜谱，排一周的菜单，并生成它的购物清单。",
    "",
    "命令：",
    "",
    "选项：",
    "  --lang en|zh    输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹   数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version       显示版本。",
    "  --help          显示这份帮助。",
    "",
    "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。",
)

# ----------------------------------------------------- lines that follow a usage error

OPTIONS_EN = RUN_HELP_FOR_OPTIONS.render(EN)
OPTIONS_ZH = RUN_HELP_FOR_OPTIONS.render(ZH)
COMMANDS_EN = RUN_HELP_FOR_COMMANDS.render(EN)
COMMANDS_ZH = RUN_HELP_FOR_COMMANDS.render(ZH)
CHECK_EN = RUN_CHECK.render(EN)
CHECK_ZH = RUN_CHECK.render(ZH)
INIT_EN = 'Run "recipe-menu init" to create it, or name another folder with --data.'
INIT_ZH = "运行“recipe-menu init”创建它，或用 --data 指定别的文件夹。"


def lines_text(*lines: str) -> str:
    """Joins lines into the text of a stream, each line ended by a line break."""
    return "".join(f"{line}\n" for line in lines)


def err_result(code: int, *lines: str) -> Result:
    """Gives the result of a call that writes lines to the error stream and nothing else."""
    return code, "", lines_text(*lines)


def no_data_folder(folder: Path | str, lang: Lang = EN) -> Result:
    """Gives the result of ``NO_DATA_FOLDER`` for a folder, in a language."""
    if lang is EN:
        return err_result(1, f"There is no data folder at {folder}.", INIT_EN)
    return err_result(1, f"{folder} 没有数据文件夹。", INIT_ZH)


def stopped(where: str, what: str, lang: Lang = EN) -> Result:
    """Gives the result of ``stop_at_error`` for the lines ``where`` and ``what``."""
    check = CHECK_EN if lang is EN else CHECK_ZH
    return err_result(1, where, f"  {what}", check)


# ------------------------------------------------------------ places and messages of settings

LANGUAGE = BiText("language", "语言")
MEALS = BiText("meals", "餐次")
SERVINGS = BiText("servings", "份数")
KEYS_EN = "language, meals, and servings"
MEALS_EN = "breakfast, lunch, and dinner"
MEALS_ZH = "breakfast、lunch 和 dinner"


def meal_n(number: int) -> BiText:
    """Gives the place of item N of ``meals``."""
    return BiText(f"meal {number}", f"餐次 {number}")


def line_n(number: int) -> BiText:
    """Gives the place of a line, as ``read_toml`` gives it."""
    return BiText(f"line {number}", f"第 {number} 行")


def not_a_text(key: str) -> Msg:
    """Gives the two texts of ``NOT_A_TEXT``."""
    return f'"{key}" must be a text in quotation marks.', f"“{key}”必须是放在引号里的文字。"


def empty_text(key: str) -> Msg:
    """Gives the two texts of ``EMPTY_TEXT``."""
    return f'"{key}" is empty.', f"“{key}”是空的。"


def not_a_list(key: str) -> Msg:
    """Gives the two texts of ``NOT_A_LIST``."""
    return (
        f'"{key}" must be a list in square brackets, [ ... ].',
        f"“{key}”必须是放在方括号 [ ... ] 里的列表。",
    )


ITEM_NOT_A_TEXT: Msg = (
    "This item must be a text in quotation marks.",
    "这一项必须是放在引号里的文字。",
)
EMPTY_ITEM: Msg = ("This item is empty.", "这一项是空的。")
NO_MEALS: Msg = (
    f'"meals" must name at least one meal. The meals are {MEALS_EN}.',
    f"“meals”至少要写上一个餐次。可用的餐次：{MEALS_ZH}。",
)
SERVINGS_NOT_A_NUMBER: Msg = (
    "Servings must be a whole number from 1 to 100, such as 2.",
    "份数必须是 1 到 100 之间的整数，比如 2。",
)


def unknown_key(key: str) -> Msg:
    """Gives the two texts of ``UNKNOWN_KEY`` in the settings."""
    return (
        f'Unknown key "{key}". The keys are {KEYS_EN}.',
        f"未知键“{key}”。可用的键：language、meals 和 servings。",
    )


def language_not_en_or_zh(language: str) -> Msg:
    """Gives the two texts of ``LANGUAGE_NOT_EN_OR_ZH``."""
    return (
        f'The language must be "en" or "zh", not "{language}".',
        f"语言必须是“en”或“zh”，不能是“{language}”。",
    )


def unknown_meal(meal: str) -> Msg:
    """Gives the two texts of ``UNKNOWN_MEAL``."""
    return (
        f'Unknown meal "{meal}". The meals are {MEALS_EN}.',
        f"未知餐次“{meal}”。可用的餐次：{MEALS_ZH}。",
    )


def servings_too_few(servings: int) -> Msg:
    """Gives the two texts of ``SERVINGS_TOO_FEW``."""
    return (
        f"Servings must be a whole number of 1 or more, not {servings}.",
        f"份数必须是不小于 1 的整数，不能是 {servings}。",
    )


def servings_too_many(servings: int) -> Msg:
    """Gives the two texts of ``SERVINGS_TOO_MANY``."""
    return (
        f"Servings must be a whole number of 100 or less, not {servings}.",
        f"份数必须是不大于 100 的整数，不能是 {servings}。",
    )


def entry(place: BiText | None, message: Msg) -> Expected:
    """Gives an expected problem: its place and the two texts of its message."""
    return place, message[0], message[1]


def assert_problems(problems: Sequence[Problem], expected: Sequence[Expected]) -> None:
    """Checks the whole tuple of problems of ``read_settings`` in order.

    Every problem must be an error with the file ``settings.toml``, and the place and both texts
    of each must be the expected ones.
    """
    got = [(p.severity, str(p.file), p.place, p.text(EN), p.text(ZH)) for p in problems]
    want = [(Severity.ERROR, "settings.toml", place, en, zh) for place, en, zh in expected]
    assert got == want
