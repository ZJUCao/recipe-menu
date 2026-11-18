"""The messages of ``suggest``: the help line, the argument name, and the lines of the command.

Every message is internal to the module. The output of ``recipe-menu menu suggest`` is made of
them, of ``NOT_A_WEEK`` and ``NO_MENU`` of ``menus``, and of the problems that the readers and
``replace_file`` give. ``FILLED``, ``FILLED_WITH_TAG``, ``FILLED_SOME``,
``FILLED_SOME_WITH_TAG``, ``KEPT``, ``STAY_EMPTY``, ``STAY_EMPTY_WITH_TAG``, ``TOO_FEW``,
``TOO_FEW_WITH_TAG``, and ``UNKNOWN_TAG`` are plurals, each picked by its ``count``, or
``UNKNOWN_TAG`` by the number of the catalog's tags.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The name of the optional argument, in the usage and in the help.
WEEK_ARGUMENT: Final[Message] = Message("WEEK", "周")

# The line of the command in the help.
MENU_SUGGEST_HELP: Final[Message] = Message(
    "Fill the empty meals of a week menu.",
    "给一个周菜单的空餐填上菜。",
)

# The first line when every empty meal got its dishes, with and without ``--tag``.
FILLED: Final[Plural] = Plural(
    Message("Filled {count} empty meal of {week}.", "已为 {week} 填好 {count} 个空餐。"),
    Message("Filled {count} empty meals of {week}.", "已为 {week} 填好 {count} 个空餐。"),
)
FILLED_WITH_TAG: Final[Plural] = Plural(
    Message(
        'Filled {count} empty meal of {week} with recipes that have the tag "{tag}".',
        "已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。",
    ),
    Message(
        'Filled {count} empty meals of {week} with recipes that have the tag "{tag}".',
        "已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。",
    ),
)

# The first line when some empty meals stay empty, with and without ``--tag``.
FILLED_SOME: Final[Plural] = Plural(
    Message(
        "Filled {filled} of {count} empty meal of {week}.",
        "已为 {week} 填好 {count} 个空餐中的 {filled} 个。",
    ),
    Message(
        "Filled {filled} of {count} empty meals of {week}.",
        "已为 {week} 填好 {count} 个空餐中的 {filled} 个。",
    ),
)
FILLED_SOME_WITH_TAG: Final[Plural] = Plural(
    Message(
        'Filled {filled} of {count} empty meal of {week} with recipes that have the tag "{tag}".',
        "已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。",
    ),
    Message(
        'Filled {filled} of {count} empty meals of {week} with recipes that have the tag "{tag}".',
        "已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。",
    ),
)

# The kept meals, and the line that joins the first line with them.
KEPT: Final[Plural] = Plural(
    Message("Kept the {count} meal that already has dishes.", "保留了已经有菜的 {count} 餐。"),
    Message("Kept the {count} meals that already have dishes.", "保留了已经有菜的 {count} 餐。"),
)
WITH_KEPT: Final[Message] = Message("{first} {kept}", "{first}{kept}")

# The lines of a fill that gave every empty meal its dishes.
NO_TWICE: Final[Message] = Message(
    "No recipe appears twice in the week.", "这一周里没有重复的菜谱。"
)
RUN_SHOW: Final[Message] = Message(
    'Run "recipe-menu menu show {week}" to see the week.',
    "运行“recipe-menu menu show {week}”查看这一周。",
)
SWAP_HINT: Final[Message] = Message(
    'To swap a dish, empty its meal in {file}, then run "recipe-menu menu suggest {week}" again.',
    "要换掉一道菜，就在 {file} 里清空它那一餐，然后再运行“recipe-menu menu suggest {week}”。",
)

# The reasons that some empty meals stay empty, with and without ``--tag``.
STAY_EMPTY: Final[Plural] = Plural(
    Message(
        "{count} meal stays empty: no other recipe is left.",
        "{count} 餐仍是空的：没有别的菜谱可选了。",
    ),
    Message(
        "{count} meals stay empty: no other recipe is left.",
        "{count} 餐仍是空的：没有别的菜谱可选了。",
    ),
)
STAY_EMPTY_WITH_TAG: Final[Plural] = Plural(
    Message(
        '{count} meal stays empty: no other recipe has the tag "{tag}".',
        "{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。",
    ),
    Message(
        '{count} meals stay empty: no other recipe has the tag "{tag}".',
        "{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。",
    ),
)
TOO_FEW: Final[Plural] = Plural(
    Message(
        "{count} meal stays empty: too few other recipes are left.",
        "{count} 餐仍是空的：剩下的菜谱不够了。",
    ),
    Message(
        "{count} meals stay empty: too few other recipes are left.",
        "{count} 餐仍是空的：剩下的菜谱不够了。",
    ),
)
TOO_FEW_WITH_TAG: Final[Plural] = Plural(
    Message(
        '{count} meal stays empty: too few other recipes have the tag "{tag}".',
        "{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。",
    ),
    Message(
        '{count} meals stay empty: too few other recipes have the tag "{tag}".',
        "{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。",
    ),
)

# The line for a week with no empty meal.
NO_EMPTY_MEAL: Final[Message] = Message(
    "{week} has no empty meal. Nothing was changed.",
    "{week} 没有空餐。没有做任何修改。",
)

# The refusal for a file that cannot be filled, and the last line of a failed save.
CANNOT_FILL: Final[Message] = Message(
    "menu suggest cannot fill this file: write each day as a line such as [monday], and each "
    'empty meal as a line such as dinner = [], as "recipe-menu menu new" does.',
    "menu suggest 无法填写这个文件：请把每一天写成 [monday] 这样的一行，把每个空餐写成 "
    "dinner = [] 这样的一行，和“recipe-menu menu new”写的一样。",
)
CHANGED_NOTHING: Final[Message] = Message("Nothing was changed.", "没有做任何修改。")
LEFT_BEHIND: Final[Message] = Message(
    "Nothing was changed, but menu suggest could not remove {file}. Delete it.",
    "没有做任何修改，但 menu suggest 没能删除 {file}。请删除它。",
)

# The errors of ``--tag``, picked by the number of the catalog's tags. ``NO_TAGS`` is for a
# catalog with no tags.
UNKNOWN_TAG: Final[Plural] = Plural(
    Message(
        'Unknown tag "{value}". The only tag is {tags}.',
        "未知标签“{value}”。现有标签：{tags}。",
    ),
    Message(
        'Unknown tag "{value}". The tags are {tags}.',
        "未知标签“{value}”。现有标签：{tags}。",
    ),
)
NO_TAGS: Final[Message] = Message(
    'Unknown tag "{value}". The catalog has no tags.',
    "未知标签“{value}”。目录里没有标签。",
)
