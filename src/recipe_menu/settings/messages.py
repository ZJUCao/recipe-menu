"""The messages of ``settings``: the places in ``settings.toml`` and its own problems.

All are internal to the module. The other problems of the file use the messages of ``datafile``.
"""

from typing import Final

from recipe_menu.text import Message

# The places in ``settings.toml``. ``MEAL_N`` names the item N of ``meals``, counted from 1.
LANGUAGE: Final[Message] = Message("language", "语言")
MEALS: Final[Message] = Message("meals", "餐次")
MEAL_N: Final[Message] = Message("meal {number}", "餐次 {number}")
SERVINGS: Final[Message] = Message("servings", "份数")

# The names of the meals: a label inside a sentence, and a heading at the top of a column.
BREAKFAST_LABEL: Final[Message] = Message("breakfast", "早餐")
LUNCH_LABEL: Final[Message] = Message("lunch", "午餐")
DINNER_LABEL: Final[Message] = Message("dinner", "晚餐")
BREAKFAST_HEADING: Final[Message] = Message("Breakfast", "早餐")
LUNCH_HEADING: Final[Message] = Message("Lunch", "午餐")
DINNER_HEADING: Final[Message] = Message("Dinner", "晚餐")

# The problems of ``settings.toml`` that ``datafile`` has no message for.
LANGUAGE_NOT_EN_OR_ZH: Final[Message] = Message(
    'The language must be "en" or "zh", not "{language}".',
    "语言必须是“en”或“zh”，不能是“{language}”。",
)
UNKNOWN_MEAL: Final[Message] = Message(
    'Unknown meal "{meal}". The meals are {meals}.',
    "未知餐次“{meal}”。可用的餐次：{meals}。",
)
NO_MEALS: Final[Message] = Message(
    '"meals" must name at least one meal. The meals are {meals}.',
    "“meals”至少要写上一个餐次。可用的餐次：{meals}。",
)
