"""The messages of ``shop``: the help line, the argument name, and the lines of the command.

Every message is internal to the module. The output of ``recipe-menu shop`` and the text of the
saved file are made of them, of ``NO_MENU`` of ``menus``, and of the problems that the readers
and ``replace_file`` give. The Markdown signs of the file belong to no language and are not
messages.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The name of the optional argument, in the usage and in the help.
WEEK_ARGUMENT: Final[Message] = Message("WEEK", "周")

# The line of the command in the help.
SHOP_HELP: Final[Message] = Message(
    "Make the shopping list of a week menu.",
    "生成一个周菜单的购物清单。",
)

# The heading of the list in the terminal.
LIST_HEADING: Final[Message] = Message(
    "Shopping list for {week}, {dates}: {meals}, {dishes}",
    "{week} 购物清单，{dates}：{meals}，{dishes}",
)

# The counts of the heading and of the dates line, picked by the number of meals and of dishes.
MEAL_COUNT: Final[Plural] = Plural(
    Message("{count} meal", "{count} 餐"),
    Message("{count} meals", "{count} 餐"),
)
DISH_COUNT: Final[Plural] = Plural(
    Message("{count} dish", "{count} 道菜"),
    Message("{count} dishes", "{count} 道菜"),
)

# The line for a list with no group, and the line of the pantry ingredients that the menu uses.
NOTHING_TO_BUY: Final[Message] = Message("There is nothing to buy.", "没有要买的东西。")
PANTRY_LINE: Final[Message] = Message(
    "Not on the list, because they are in the pantry: {items}",
    "常备，不用买：{items}",
)

# The last line of the output of a saved list.
SAVED: Final[Message] = Message("Saved {file}", "已保存 {file}")

# The line for a week with no dish.
NO_DISHES: Final[Message] = Message(
    "The menu for {week} has no dishes, so there is nothing to buy. No file was saved.",
    "{week} 的菜单没有菜，所以没有要买的东西。没有保存文件。",
)

# The title and the dates line at the top of the saved file.
FILE_TITLE: Final[Message] = Message("Shopping list for {week}", "{week} 购物清单")
FILE_DATES: Final[Message] = Message(
    "{dates}: {meals}, {dishes}.",
    "{dates}：{meals}，{dishes}。",
)

# The last line of a failed save.
NO_FILE_SAVED: Final[Message] = Message("No file was saved.", "没有保存文件。")
LEFT_BEHIND: Final[Message] = Message(
    "No file was saved, but shop could not remove {file}. Delete it.",
    "没有保存文件，但 shop 没能删除 {file}。请删除它。",
)
