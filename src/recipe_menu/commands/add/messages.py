"""The messages of ``add``: the help line, the prompts, and the lines it writes.

``UNKNOWN_TAG`` is a plural, picked by the number of the catalog's tags. ``ERROR_COUNT`` and
``WARNING_COUNT`` are plurals, each picked by its ``count``. Every message is internal to the
module.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The line of ``add`` in the help.
ADD_HELP: Final[Message] = Message(
    "Add a recipe by answering questions.",
    "回答问题，添加一个菜谱。",
)
# The prompts of the eight questions. Those of questions 1 to 5 end with no line break.
ID_PROMPT: Final[Message] = Message(
    "Recipe ID (also the file name): ",
    "菜谱 ID（也是文件名）：",
)
ZH_NAME_PROMPT: Final[Message] = Message(
    "Chinese name: ",
    "中文名：",
)
EN_NAME_PROMPT: Final[Message] = Message(
    "English name: ",
    "英文名：",
)
SERVINGS_PROMPT: Final[Message] = Message(
    "Servings [{servings}]: ",
    "份数 [{servings}]：",
)
TAGS_PROMPT: Final[Message] = Message(
    "Tags, separated by commas: ",
    "标签，用逗号分隔：",
)
INGREDIENTS_PROMPT: Final[Message] = Message(
    'Ingredients, one per line, as "name quantity". An empty line ends the list:',
    "食材，每行一个，写“名称 数量”，空行结束：",
)
ZH_STEPS_PROMPT: Final[Message] = Message(
    "Chinese steps, one per line. An empty line ends the list:",
    "中文步骤，每行一步，空行结束：",
)
EN_STEPS_PROMPT: Final[Message] = Message(
    "English steps, one per line. An empty line ends the list:",
    "英文步骤，每行一步，空行结束：",
)
EN_STEPS_OPTIONAL_PROMPT: Final[Message] = Message(
    "English steps, one per line. An empty line ends the list (optional):",
    "英文步骤，每行一步，空行结束（可以不写）：",
)
# The messages after a wrong answer.
NOT_AN_ID: Final[Message] = Message(
    '"{id}" cannot be a recipe ID. An ID has only the small letters a to z, digits, '
    'and "-", and starts with a letter or a digit, such as "tomato-egg". Windows '
    'device names, such as "con", are not IDs.',
    "“{id}”不能用作菜谱 ID。ID 只能由小写字母 a 到"
    " z、数字和“-”组成，并以字母或数字开头，比如“tomat"
    "o-egg”。“con”这样的 Windows 设备名不能用"
    "作 ID。",
)
ID_EXISTS: Final[Message] = Message(
    'The recipe {id} already exists. Enter another ID, or run "recipe-menu edit {id}".',
    "菜谱 {id} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {id}”。",
)
NAME_NEEDED: Final[Message] = Message(
    "A recipe needs a name in at least one language. Enter its English name.",
    "菜谱至少要有一种语言的名称。请输入它的英文名。",
)
SERVINGS_WRONG: Final[Message] = Message(
    "Servings must be a whole number from 1 to 100, such as 2.",
    "份数必须是 1 到 100 之间的整数，比如 2。",
)
NO_TAGS: Final[Message] = Message(
    'Unknown tag "{value}". The catalog has no tags.',
    "未知标签“{value}”。目录里没有标签。",
)
NAME_AND_QUANTITY: Final[Message] = Message(
    'Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".',
    "请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。",
)
UNKNOWN_INGREDIENT: Final[Message] = Message(
    'The catalog has no "{name}". Enter a name from the catalog, or add it to the '
    "catalog first and then run add again.",
    "目录里没有“{name}”。请输入目录里的名称，或先把它加入目录后再运行 add。",
)
# The four amount messages, with the texts of ``read_recipe``.
AMOUNT_NOT_A_NUMBER: Final[Message] = Message(
    'The amount "{amount}" must sta'
    "rt with a number of at most 15"
    " digits, such as 300 or 1.5, o"
    'r be "适量" or "to taste".',
    "数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，或者写成“适量”或“to taste”。",
)
AMOUNT_UNKNOWN_UNIT: Final[Message] = Message(
    'Unknown unit "{unit}" in "{amount}".',
    "数量“{amount}”里有未知单位“{unit}”。",
)
AMOUNT_NO_UNIT: Final[Message] = Message(
    'The amount "{amount}" has no unit, and the catalog gives "{ingredient}" no '
    'default unit. Write a unit after the number, such as "300 g".',
    "数量“{amount}”没有单位，目录也没有给“{ingredient}”默认单位。"
    "请在数字后面写上单位，比如“300 g”。",
)
AMOUNT_ZERO: Final[Message] = Message(
    'The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".',
    "数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。",
)
STEPS_NEEDED: Final[Message] = Message(
    "A recipe needs steps in at least one language. Enter at least one English step.",
    "菜谱至少要有一种语言的步骤。请至少输入一步英文步骤。",
)
# The lines after saving.
SAVED: Final[Message] = Message(
    "Saved {file}. The check found no problems.",
    "已保存 {file}。检查没有发现问题。",
)
SAVED_WITH_PROBLEMS: Final[Message] = Message(
    "Saved {file}. The check found {problems}:",
    "已保存 {file}。检查发现了 {problems}：",
)
FIX_AND_CHECK: Final[Message] = Message(
    'Fix the errors, then run "recipe-menu check".',
    "改正错误后，运行“recipe-menu check”。",
)
# The lines of an early end and of a failed save.
INPUT_ENDED: Final[Message] = Message(
    "The answers ended before the recipe was complete. Nothing was saved.",
    "回答在菜谱完成之前就结束了。没有保存任何东西。",
)
APPEARED: Final[Message] = Message(
    'Nothing was saved: {file} appeared while you answered. Run "recipe-menu add" '
    "again with another ID.",
    "没有保存任何东西：你回答问题时出现了 {file}。请换一个 ID，再运行“recipe-menu add”。",
)
NOTHING_SAVED: Final[Message] = Message(
    "Nothing was saved.",
    "没有保存任何东西。",
)
LEFT_BEHIND: Final[Message] = Message(
    "Nothing was saved, but add could not remove {file}. Delete it.",
    "没有保存任何东西，但 add 没能删除 {file}。请删除它。",
)

# The error of a tag that the catalog does not have, picked by the number of the catalog's tags.
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

# The counts of problems in ``SAVED_WITH_PROBLEMS``.
ERROR_COUNT: Final[Plural] = Plural(
    Message("{count} error", "{count} 个错误"),
    Message("{count} errors", "{count} 个错误"),
)
WARNING_COUNT: Final[Plural] = Plural(
    Message("{count} warning", "{count} 个警告"),
    Message("{count} warnings", "{count} 个警告"),
)
