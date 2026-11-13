"""The messages of ``check``: the help line, the count line, the headings, and the other lines.

The other lines are the lines for no errors and the closing line. Every message is internal to the
module. The report of ``recipe-menu check`` is made of them and of the problems that the readers
of ``catalog``, ``recipes``, ``settings``, and ``menus`` give.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The line of ``check`` in the help.
CHECK_HELP: Final[Message] = Message(
    "Check every data file for mistakes.",
    "检查每个数据文件有没有错误。",
)

# The count line. ``files`` is the ``and_list`` of the five parts below.
CHECKED: Final[Message] = Message("Checked {files}.", "已检查{files}。")

# The parts of the count line.
THE_SETTINGS: Final[Message] = Message("the settings", "设置")
THE_CATALOG: Final[Message] = Message("the catalog", "目录")
THE_PANTRY: Final[Message] = Message("the pantry", "常备清单")
RECIPE_COUNT: Final[Plural] = Plural(
    Message("{count} recipe", "{count} 个菜谱"),
    Message("{count} recipes", "{count} 个菜谱"),
)
WEEK_MENU_COUNT: Final[Plural] = Plural(
    Message("{count} week menu", "{count} 个周菜单"),
    Message("{count} week menus", "{count} 个周菜单"),
)

# The headings of the two blocks of problems, picked by the number of problems.
ERRORS_HEADING: Final[Plural] = Plural(
    Message("{count} error:", "{count} 个错误："),
    Message("{count} errors:", "{count} 个错误："),
)
WARNINGS_HEADING: Final[Plural] = Plural(
    Message("{count} warning:", "{count} 个警告："),
    Message("{count} warnings:", "{count} 个警告："),
)

# The lines for a report with no errors, and the closing line of a report with errors.
NO_ERRORS: Final[Message] = Message("No errors.", "没有错误。")
NO_ERRORS_OR_WARNINGS: Final[Message] = Message(
    "No errors. No warnings.",
    "没有错误，也没有警告。",
)
FIX_AND_CHECK_AGAIN: Final[Message] = Message(
    'Fix the errors and run "recipe-menu check" again.',
    "改正错误后，再运行“recipe-menu check”。",
)
