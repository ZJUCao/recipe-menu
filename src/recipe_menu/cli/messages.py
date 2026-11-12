"""The messages of ``cli``: the mistakes on the command line, the data folder, and the help.

All are internal to the module.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The mistakes on the command line. Each ends a command with exit code 2.
OPTION_NEEDS_VALUE: Final[Message] = Message(
    "{option} needs a value.",
    "{option} 后面要写一个值。",
)
OPTION_TWICE: Final[Message] = Message("{option} is given twice.", "{option} 写了两次。")
LANG_NOT_EN_OR_ZH: Final[Message] = Message(
    '--lang must be en or zh, not "{lang}".',
    "--lang 必须是 en 或 zh，不能是“{lang}”。",
)
NO_COMMAND: Final[Message] = Message(
    'Name a command, such as "recipe-menu list".',
    "请写上一个命令，比如“recipe-menu list”。",
)
UNKNOWN_COMMAND: Final[Message] = Message(
    'Unknown command "{command}".',
    "未知命令“{command}”。",
)
INCOMPLETE_COMMAND: Final[Plural] = Plural(
    Message(
        'The only command that starts with "{word}" is {commands}.',
        "以“{word}”开头的命令只有{commands}。",
    ),
    Message(
        'The commands that start with "{word}" are {commands}.',
        "以“{word}”开头的命令有{commands}。",
    ),
)
# The form of ``UNKNOWN_OPTION`` for a command with no options has no ``{options}``, so it is a
# ``Message``. The forms for one option and for more are a ``Plural``.
UNKNOWN_OPTION_NONE: Final[Message] = Message(
    '"{command}" has no option "{option}". It has no options of its own.',
    "“{command}”没有选项“{option}”。它没有自己的选项。",
)
UNKNOWN_OPTION: Final[Plural] = Plural(
    Message(
        '"{command}" has no option "{option}". Its own option is {options}.',
        "“{command}”没有选项“{option}”。它自己的选项是{options}。",
    ),
    Message(
        '"{command}" has no option "{option}". Its own options are {options}.',
        "“{command}”没有选项“{option}”。它自己的选项有{options}。",
    ),
)
TOO_FEW_ARGUMENTS: Final[Message] = Message(
    'An argument is missing. Write "recipe-menu {usage}".',
    "缺少参数。请写成“recipe-menu {usage}”。",
)
TOO_MANY_ARGUMENTS: Final[Message] = Message(
    'Unexpected argument "{argument}". Write "recipe-menu {usage}".',
    "多余的参数“{argument}”。请写成“recipe-menu {usage}”。",
)

# The messages that end a command with exit code 1.
NO_DATA_FOLDER: Final[Message] = Message(
    "There is no data folder at {folder}.",
    "{folder} 没有数据文件夹。",
)
RUN_INIT: Final[Message] = Message(
    'Run "recipe-menu init" to create it, or name another folder with --data.',
    "运行“recipe-menu init”创建它，或用 --data 指定别的文件夹。",
)

# The texts of the help and of the version.
USAGE_LINE: Final[Message] = Message(
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
)
SUMMARY: Final[Message] = Message(
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "保存菜谱，排一周的菜单，并生成它的购物清单。",
)
COMMANDS_HEADING: Final[Message] = Message("Commands:", "命令：")
OPTIONS_HEADING: Final[Message] = Message("Options:", "选项：")
WEEK_NOTE: Final[Message] = Message(
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
    "“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。",
)
VERSION_LINE: Final[Message] = Message("recipe-menu {version}", "recipe-menu {version}")

# The rows of the table of the options in the help: the first cell, then the second.
LANG_OPTION: Final[Message] = Message("--lang en|zh", "--lang en|zh")
LANG_HELP: Final[Message] = Message(
    "The language of the output. Default: the settings, else English.",
    "输出语言。默认：设置里的语言，否则英文。",
)
DATA_OPTION: Final[Message] = Message("--data FOLDER", "--data 文件夹")
DATA_HELP: Final[Message] = Message(
    "The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
)
VERSION_OPTION: Final[Message] = Message("--version", "--version")
VERSION_HELP: Final[Message] = Message("Show the version.", "显示版本。")
HELP_OPTION: Final[Message] = Message("--help", "--help")
HELP_HELP: Final[Message] = Message("Show this help.", "显示这份帮助。")
