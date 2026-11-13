"""The messages of ``init``: the help line, the lines of a new folder, and the refusals.

Every message is internal to the module. The output of ``recipe-menu init`` is made of them. The
counts and the servings are ``Plural`` values, each picked by its ``count``.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The line of ``init`` in the help.
INIT_HELP: Final[Message] = Message(
    "Create the data folder with example data.",
    "创建数据文件夹和示例数据。",
)

# The first line of a new folder. ``folder`` is the data folder's full path.
CREATED: Final[Message] = Message(
    "Created the data folder {folder}:",
    "已创建数据文件夹 {folder}：",
)

# The line of ``settings.toml`` and its parts.
SETTINGS_LINE: Final[Message] = Message(
    "{language}, {meals}, {servings}",
    "{language}，{meals}，{servings}",
)
ENGLISH: Final[Message] = Message("English", "英文")
CHINESE: Final[Message] = Message("Chinese", "中文")
SERVINGS_PER_DISH: Final[Plural] = Plural(
    Message("{count} serving per dish", "每道菜 {count} 份"),
    Message("{count} servings per dish", "每道菜 {count} 份"),
)

# The line of ``catalog.toml`` and its parts.
CATALOG_LINE: Final[Message] = Message(
    "{categories}, {ingredients}, {tags}",
    "{categories}，{ingredients}，{tags}",
)
CATEGORY_COUNT: Final[Plural] = Plural(
    Message("{count} category", "{count} 个分类"),
    Message("{count} categories", "{count} 个分类"),
)
INGREDIENT_COUNT: Final[Plural] = Plural(
    Message("{count} ingredient", "{count} 种食材"),
    Message("{count} ingredients", "{count} 种食材"),
)
TAG_COUNT: Final[Plural] = Plural(
    Message("{count} tag", "{count} 个标签"),
    Message("{count} tags", "{count} 个标签"),
)

# The lines of the example recipe and of the two empty folders.
EXAMPLE_RECIPE: Final[Message] = Message(
    "an example recipe in both languages",
    "一个中英双语的示例菜谱",
)
EMPTY_FOLDER: Final[Message] = Message("empty", "空")

# The last line of a new folder. ``recipes`` is the folder of the recipes, with a separator.
NEXT_STEP: Final[Message] = Message(
    'Next: add your recipes to {recipes}, then run "recipe-menu check".',
    "下一步：把你的菜谱加进 {recipes}，然后运行“recipe-menu check”。",
)

# The refusals. ``folder`` is the data folder's full path.
ALREADY_HOLDS_FILES: Final[Message] = Message(
    "{folder} already holds files. init changed nothing.",
    "{folder} 里已经有文件。init 没有做任何修改。",
)
IS_A_FILE: Final[Message] = Message(
    "{folder} is a file, not a folder. init changed nothing.",
    "{folder} 是一个文件，不是文件夹。init 没有做任何修改。",
)

# The last line of a failure.
CHANGED_NOTHING: Final[Message] = Message(
    "init changed nothing.",
    "init 没有做任何修改。",
)
LEFT_BEHIND: Final[Message] = Message(
    'init could not remove all that it created. Empty {folder}, then run "recipe-menu init" again.',
    "init 没能删除它创建的全部内容。请清空 {folder}，然后再运行“recipe-menu init”。",
)
