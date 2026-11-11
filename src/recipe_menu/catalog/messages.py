"""The messages of ``catalog``: the places in its files and its problems. All are internal."""

from typing import Final

from recipe_menu.text import Message, Plural

# The places in ``catalog.toml``.
CATEGORIES: Final[Message] = Message("categories", "分类")
INGREDIENTS: Final[Message] = Message("ingredients", "食材")
TAGS: Final[Message] = Message("tags", "标签")
CATEGORY_N: Final[Message] = Message("category {number}", "分类 {number}")
INGREDIENT_N: Final[Message] = Message("ingredient {number}", "食材 {number}")
TAG_N: Final[Message] = Message("tag {number}", "标签 {number}")

# The places in ``pantry.toml``.
PANTRY: Final[Message] = Message("pantry", "常备清单")
ITEM_N: Final[Message] = Message("item {number}", "第 {number} 项")

# The problems of ``catalog.toml``.
UNKNOWN_CATEGORY: Final[Plural] = Plural(
    Message(
        'Unknown category "{category}". The only category is {categories}.',
        "未知分类“{category}”。现有分类：{categories}。",
    ),
    Message(
        'Unknown category "{category}". The categories are {categories}.',
        "未知分类“{category}”。现有分类：{categories}。",
    ),
)
NO_CATEGORIES: Final[Message] = Message(
    'Unknown category "{category}". The catalog has no categories.',
    "未知分类“{category}”。目录里没有分类。",
)
UNKNOWN_UNIT: Final[Message] = Message('Unknown unit "{unit}".', "未知单位“{unit}”。")
DUPLICATE_KEY: Final[Message] = Message(
    'The key "{key}" is also {other}\'s key. Keys must be unique.',
    "键“{key}”也是{other} 的键。键不能重复。",
)
DUPLICATE_ZH_NAME: Final[Message] = Message(
    'The Chinese name "{name}" is also {other}\'s name. Names must be unique.',
    "中文名称“{name}”也是{other} 的名称。名称不能重复。",
)
DUPLICATE_EN_NAME: Final[Message] = Message(
    'The English name "{name}" is also {other}\'s name. Names must be unique.',
    "英文名称“{name}”也是{other} 的名称。名称不能重复。",
)

# The problem of ``pantry.toml``.
UNKNOWN_INGREDIENT: Final[Message] = Message(
    'Unknown ingredient "{name}".',
    "未知食材“{name}”。",
)
