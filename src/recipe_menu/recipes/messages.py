"""The messages of ``recipes``: the places in a recipe file and its problems. All are internal."""

from typing import Final

from recipe_menu.text import Message

# The places in a recipe file.
NAME: Final[Message] = Message("name", "名称")
SERVINGS: Final[Message] = Message("servings", "份数")
TAGS: Final[Message] = Message("tags", "标签")
TAG_N: Final[Message] = Message("tag {number}", "标签 {number}")
INGREDIENTS: Final[Message] = Message("ingredients", "食材")
INGREDIENT_N: Final[Message] = Message("ingredient {number}", "食材 {number}")
STEPS: Final[Message] = Message("steps", "步骤")
ZH_STEP_N: Final[Message] = Message("Chinese step {number}", "中文步骤 {number}")
EN_STEP_N: Final[Message] = Message("English step {number}", "英文步骤 {number}")

# The problems of a file name in ``recipes/``.
NOT_A_RECIPE_ID: Final[Message] = Message(
    "This file name is not a recipe ID. An ID has only the small letters a to z, digits, "
    'and "-", and starts with a letter or a digit, such as "tomato-egg". Rename the file.',
    "这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，"
    "并以字母或数字开头，比如“tomato-egg”。请给文件改名。",
)
RESERVED_RECIPE_ID: Final[Message] = Message(
    "This file name cannot be a recipe ID, because Windows keeps it for a device. Rename the file.",
    "这个文件名不能用作菜谱 ID，因为 Windows 把它留给设备使用。请给文件改名。",
)

# The problems of a recipe file.
NOT_A_ZH_EN_TABLE: Final[Message] = Message(
    '"{key}" must be a table in braces with "zh" and "en", such as {{ zh = "...", en = "..." }}.',
    '“{key}”必须是放在花括号里、带有“zh”和“en”的表，比如 {{ zh = "...", en = "..." }}。',
)
NO_NAME: Final[Message] = Message(
    'The name has no text in either language. Write "zh", "en", or both.',
    "名称在两种语言里都没有文字。请写上“zh”、“en”或两者。",
)
NO_ZH_NAME: Final[Message] = Message(
    "No Chinese name. Commands show the English name instead.",
    "没有中文名称。命令会改为显示英文名称。",
)
NO_EN_NAME: Final[Message] = Message(
    "No English name. Commands show the Chinese name instead.",
    "没有英文名称。命令会改为显示中文名称。",
)
UNKNOWN_TAG: Final[Message] = Message(
    'Unknown tag "{tag}". Add it to the catalog\'s tags.',
    "未知标签“{tag}”。请把它加入目录里的标签。",
)
UNKNOWN_INGREDIENT: Final[Message] = Message(
    'Unknown ingredient "{name}". Add it to the catalog, or use its name in the catalog.',
    "未知食材“{name}”。请把它加入目录，或改用目录里的名称。",
)
AMOUNT_NOT_A_NUMBER: Final[Message] = Message(
    'The amount "{amount}" must start with a number of at most 15 digits, such as 300 or 1.5, '
    'or be "适量" or "to taste".',
    "数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，或者写成“适量”或“to taste”。",
)
AMOUNT_UNKNOWN_UNIT: Final[Message] = Message(
    'Unknown unit "{unit}" in "{amount}".',
    "数量“{amount}”里有未知单位“{unit}”。",
)
AMOUNT_NO_UNIT: Final[Message] = Message(
    'The amount "{amount}" has no unit, and the catalog gives "{ingredient}" no default unit. '
    'Write a unit after the number, such as "300 g".',
    "数量“{amount}”没有单位，目录也没有给“{ingredient}”默认单位。"
    "请在数字后面写上单位，比如“300 g”。",
)
AMOUNT_ZERO: Final[Message] = Message(
    'The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".',
    "数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。",
)
NO_ZH_NOTE: Final[Message] = Message(
    "No Chinese note. Commands show the English note instead.",
    "没有中文备注。命令会改为显示英文备注。",
)
NO_EN_NOTE: Final[Message] = Message(
    "No English note. Commands show the Chinese note instead.",
    "没有英文备注。命令会改为显示中文备注。",
)
NOT_A_STEPS_TABLE: Final[Message] = Message(
    '"steps" must be a table. Write the line [steps] at the end of the file, and below it '
    "zh = [ ... ] and en = [ ... ].",
    "“steps”必须是表。请在文件末尾写一行 [steps]，在它下面写 zh = [ ... ] 和 en = [ ... ]。",
)
NO_STEPS: Final[Message] = Message(
    'The recipe has no steps. Write the steps in "zh", "en", or both.',
    "菜谱没有步骤。请在“zh”、“en”或两者里写上步骤。",
)
NO_ZH_STEPS: Final[Message] = Message(
    "No Chinese steps. Commands show the English steps instead.",
    "没有中文步骤。命令会改为显示英文步骤。",
)
NO_EN_STEPS: Final[Message] = Message(
    "No English steps. Commands show the Chinese steps instead.",
    "没有英文步骤。命令会改为显示中文步骤。",
)
