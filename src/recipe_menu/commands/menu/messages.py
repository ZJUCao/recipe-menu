r"""The messages of ``menu``: the help lines, the argument name, and the lines of both commands.

Every message is internal to the module. The output of ``recipe-menu menu new`` and
``recipe-menu menu show`` is made of them, of ``NO_MENU`` of ``menus``, and of the problems that
the readers and ``create_file`` give. The symbols U+00D7 and U+2014 in the cells of ``menu show``
belong to no language and are not messages. The sign U+00D7 in ``COUNT_LINE`` is part of that
message's text.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The name of the optional argument of both commands, in their usage and in the help.
WEEK_ARGUMENT: Final[Message] = Message("WEEK", "周")

# The lines of the two commands in the help.
MENU_NEW_HELP: Final[Message] = Message("Create an empty week menu.", "创建一个空的周菜单。")
MENU_SHOW_HELP: Final[Message] = Message("Show a week menu.", "查看一个周菜单。")

# The three lines of a new menu, written on the output stream.
CREATED: Final[Message] = Message(
    "Created {file} for {dates}:",
    "已创建 {file}，日期为 {dates}：",
)
EMPTY_DAYS: Final[Message] = Message(
    "7 days with {meals}, all empty.",
    "共 7 天，每天有{meals}，都还是空的。",
)
NEXT_STEP: Final[Message] = Message(
    'Add recipe IDs to the meals, then run "recipe-menu check".',
    "在各餐里填上菜谱 ID，然后运行“recipe-menu check”。",
)

# The refusal of ``menu new`` for an entry that is already there.
ALREADY_EXISTS: Final[Message] = Message(
    "{file} already exists. Nothing was changed.",
    "{file} 已存在。没有做任何修改。",
)

# The last line of a failure of ``menu new``.
CHANGED_NOTHING: Final[Message] = Message("Nothing was changed.", "没有做任何修改。")
LEFT_BEHIND: Final[Message] = Message(
    'menu new could not remove the file that it created. Delete it, then run "recipe-menu menu '
    'new {week}" again.',
    "menu new 没能删除它创建的文件。请删除这个文件，然后再运行“recipe-menu menu new {week}”。",
)

# The heading of ``menu show`` and the heading of the column of days.
MENU_HEADING: Final[Message] = Message("Menu for {week}, {dates}", "{week} 菜单，{dates}")
DAY_HEADING: Final[Message] = Message("Day", "日期")

# The counts of the count line, picked by the number of meals and of dishes.
MEAL_COUNT: Final[Plural] = Plural(
    Message("{count} meal", "{count} 餐"),
    Message("{count} meals", "{count} 餐"),
)
DISH_COUNT: Final[Plural] = Plural(
    Message("{count} dish", "{count} 道菜"),
    Message("{count} dishes", "{count} 道菜"),
)

# The count line under the table, and the line for a week with no dish.
COUNT_LINE: Final[Message] = Message(
    "{meals}, {dishes}. \u00d7n: servings.",
    "{meals}，{dishes}。\u00d7n：份数。",
)
NO_DISHES: Final[Message] = Message("The menu has no dishes yet.", "这个菜单还没有菜。")
