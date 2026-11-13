"""The messages of ``list`` and ``show``: help lines, headings, count lines, and errors.

Every message is internal to the module. The output of ``recipe-menu list`` and
``recipe-menu show`` is made of them and of the problems that the readers of ``catalog`` and
``recipes`` give.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The lines of ``list`` and ``show`` in the help, and the name of the argument of ``show``.
LIST_HELP: Final[Message] = Message("List the recipes.", "列出菜谱。")
SHOW_HELP: Final[Message] = Message("Show one recipe.", "查看一个菜谱。")
ID_ARGUMENT: Final[Message] = Message("ID", "ID")

# The headings of the table of ``list``.
ID_HEADING: Final[Message] = Message("ID", "ID")
NAME_HEADING: Final[Message] = Message("Name", "名称")
SERVINGS_HEADING: Final[Message] = Message("Servings", "份数")
TAGS_HEADING: Final[Message] = Message("Tags", "标签")

# The count line of ``list`` without ``--tag``, and with it, picked by the number of recipes.
RECIPE_COUNT: Final[Plural] = Plural(
    Message("{count} recipe.", "共 {count} 个菜谱。"),
    Message("{count} recipes.", "共 {count} 个菜谱。"),
)
RECIPES_WITH_TAG: Final[Plural] = Plural(
    Message(
        '{count} recipe has the tag "{tag}".',
        "共 {count} 个菜谱带有标签“{tag}”。",
    ),
    Message(
        '{count} recipes have the tag "{tag}".',
        "共 {count} 个菜谱带有标签“{tag}”。",
    ),
)

# The one line of ``list`` when it keeps no recipe.
NO_RECIPES: Final[Message] = Message("No recipes.", "没有菜谱。")
NO_RECIPE_WITH_TAG: Final[Message] = Message(
    'No recipe has the tag "{tag}".',
    "没有菜谱带有标签“{tag}”。",
)

# The errors of ``--tag``, picked by the number of the catalog's tags. ``NO_TAGS`` is for a catalog
# with no tags.
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

# The servings line of ``show``, with and without tags, and the servings of a scaled recipe.
SERVINGS_LINE: Final[Message] = Message(
    "Servings: {servings}   Tags: {tags}",
    "份数：{servings}   标签：{tags}",
)
SERVINGS_ONLY: Final[Message] = Message("Servings: {servings}", "份数：{servings}")
SCALED_SERVINGS: Final[Message] = Message(
    "{servings} (the recipe makes {recipe_servings})",
    "{servings}（菜谱按 {recipe_servings} 份写）",
)

# The headings of the ingredients and of the steps. ``STEPS_IN_OTHER_LANGUAGE`` names the language
# that is missing.
INGREDIENTS_HEADING: Final[Message] = Message("Ingredients", "食材")
STEPS_HEADING: Final[Message] = Message("Steps", "步骤")
STEPS_IN_OTHER_LANGUAGE: Final[Message] = Message(
    "Steps (no English steps, so these are the Chinese steps)",
    "步骤（没有中文步骤，所以这里是英文步骤）",
)

# The errors of ``show``. The first is written, and the other two are raised as usage errors.
UNKNOWN_ID: Final[Message] = Message(
    'No recipe has the ID "{id}". Run "recipe-menu search {id}" to find it.',
    "没有 ID 为“{id}”的菜谱。运行“recipe-menu search {id}”查找它。",
)
NOT_A_RECIPE_ID: Final[Message] = Message(
    '"{id}" is not a recipe ID. Run "recipe-menu list" to see the IDs.',
    "“{id}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。",
)
SERVINGS_NOT_1_TO_100: Final[Message] = Message(
    '--servings must be a whole number from 1 to 100, not "{servings}".',
    "--servings 必须是 1 到 100 之间的整数，不能是“{servings}”。",
)
