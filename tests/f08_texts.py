"""The expected texts of the F08 test plan: the messages, the output, and the help.

Each text is written out as a literal, so a test does not import a message of the code. The
module calls no interface of F08 when it is imported.
"""

import os
from collections.abc import Sequence
from pathlib import Path

from f07_support import lines_text

type Msg = tuple[str, str]
type Result = tuple[int, str, str]

# ---------------------------------------------------------------- the messages of the plan

FOLDER_EXISTS: Msg = ("The folder already exists.", "文件夹已存在。")
FILE_EXISTS: Msg = ("The file already exists.", "文件已存在。")
FOLDER_CREATE_DENIED: Msg = (
    "The folder cannot be created: access is denied.",
    "无法创建文件夹：没有访问权限。",
)
FILE_WRITE_DENIED: Msg = (
    "The file cannot be written: access is denied.",
    "无法写入文件：没有访问权限。",
)
FOLDER_ACCESS_DENIED: Msg = (
    "The folder cannot be read: access is denied.",
    "无法读取文件夹：没有访问权限。",
)
MISSING_PANTRY: Msg = ('The key "pantry" is missing.', "缺少键“pantry”。")
CHANGED_NOTHING: Msg = ("init changed nothing.", "init 没有做任何修改。")


def folder_error(reason: str) -> Msg:
    """Gives ``FOLDER_CREATE_ERROR`` with its reason."""
    return (
        f"The folder cannot be created. The system says: {reason}",
        f"无法创建文件夹。系统提示：{reason}",
    )


def file_error(reason: str) -> Msg:
    """Gives ``FILE_WRITE_ERROR`` with its reason."""
    return (
        f"The file cannot be written. The system says: {reason}",
        f"无法写入文件。系统提示：{reason}",
    )


def folder_system_error(reason: str) -> Msg:
    """Gives ``FOLDER_SYSTEM_ERROR`` with its reason."""
    return (
        f"The folder cannot be read. The system says: {reason}",
        f"无法读取文件夹。系统提示：{reason}",
    )


# ---------------------------------------------------------------- the expected output

_NEW_BODY = [
    "  settings.toml              English, lunch and dinner, 2 servings per dish",
    "  catalog.toml               6 categories, 22 ingredients, 5 tags",
    "  pantry.toml                5 ingredients",
    "  recipes/tomato-egg.toml    an example recipe in both languages",
    "  menus/                     empty",
    "  shopping/                  empty",
    "",
    'Next: add your recipes to recipes/, then run "recipe-menu check".',
]
_NEW_BODY_ZH = [
    "  settings.toml              中文，午餐和晚餐，每道菜 2 份",
    "  catalog.toml               6 个分类，22 种食材，5 个标签",
    "  pantry.toml                5 种食材",
    "  recipes/tomato-egg.toml    一个中英双语的示例菜谱",
    "  menus/                     空",
    "  shopping/                  空",
    "",
    "下一步：把你的菜谱加进 recipes/，然后运行“recipe-menu check”。",
]
CHECK_NEW = [
    "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
    "",
    "No errors. No warnings.",
]
CHECK_NEW_ZH = [
    "已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。",
    "",
    "没有错误，也没有警告。",
]
_HELP = [
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "",
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "",
    "Commands:",
    "  check           Check every data file for mistakes.",
    "",
    "Options:",
    "  --lang en|zh    The language of the output. Default: the settings, else English.",
    "  --data FOLDER   The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version       Show the version.",
    "  --help          Show this help.",
    "",
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
]
_HELP_ZH = [
    "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
    "",
    "保存菜谱，排一周的菜单，并生成它的购物清单。",
    "",
    "命令：",
    "  check           检查每个数据文件有没有错误。",
    "",
    "选项：",
    "  --lang en|zh    输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹   数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version       显示版本。",
    "  --help          显示这份帮助。",
    "",
    "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。",
]
HELP = [*_HELP[:5], "  init            Create the data folder with example data.", *_HELP[5:]]
HELP_ZH = [*_HELP_ZH[:5], "  init            创建数据文件夹和示例数据。", *_HELP_ZH[5:]]


def _sep(lines: Sequence[str]) -> list[str]:
    """Writes the paths of the lines with the system's separator."""
    return [line.replace("/", os.sep) for line in lines]


def new(folder: Path | str) -> list[str]:
    """Gives ``NEW(P)``, the 9 lines of a new folder in English."""
    return [f"Created the data folder {folder}:", *_sep(_NEW_BODY)]


def new_zh(folder: Path | str) -> list[str]:
    """Gives ``NEW_ZH(P)``, the 9 lines of a new folder in Chinese."""
    return [f"已创建数据文件夹 {folder}：", *_sep(_NEW_BODY_ZH)]


def holds(folder: Path | str) -> str:
    """Gives ``HOLDS(P)``."""
    return f"{folder} already holds files. init changed nothing."


def holds_zh(folder: Path | str) -> str:
    """Gives ``HOLDS_ZH(P)``."""
    return f"{folder} 里已经有文件。init 没有做任何修改。"


def is_file(folder: Path | str) -> str:
    """Gives ``IS_FILE(P)``."""
    return f"{folder} is a file, not a folder. init changed nothing."


def is_file_zh(folder: Path | str) -> str:
    """Gives ``IS_FILE_ZH(P)``."""
    return f"{folder} 是一个文件，不是文件夹。init 没有做任何修改。"


def left_behind(folder: Path | str, zh: bool = False) -> str:
    """Gives ``LEFT_BEHIND(P)`` in a language."""
    if zh:
        return f"init 没能删除它创建的全部内容。请清空 {folder}，然后再运行“recipe-menu init”。"
    first = "init could not remove all that it created."
    return f'{first} Empty {folder}, then run "recipe-menu init" again.'


def fail(where: Path | str, msg: Msg, zh: bool = False) -> list[str]:
    """Gives ``FAIL(Q, M)``: the three lines of a failure."""
    return [str(where), "  " + msg[1 if zh else 0], CHANGED_NOTHING[1 if zh else 0]]


def leftover(where: Path | str, msg: Msg, folder: Path | str, zh: bool = False) -> list[str]:
    """Gives ``LEFT(Q, M, P)``: a failure with ``LEFT_BEHIND`` as its third line."""
    return [*fail(where, msg, zh)[:2], left_behind(folder, zh)]


def out_of(code: int, lines: Sequence[str]) -> Result:
    """Gives ``(c, out L)``."""
    return code, lines_text(lines), ""


def err_of(code: int, lines: Sequence[str]) -> Result:
    """Gives ``(c, err L)``."""
    return code, "", lines_text(lines)
