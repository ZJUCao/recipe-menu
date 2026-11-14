"""The messages of ``search``: the help line, the argument name, headings, places, and counts.

Every message is internal to the module, with the empty-word error. The output of
``recipe-menu search`` is made of them and of the problems that the readers of ``catalog`` and
``recipes`` give.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The line of ``search`` in the help, and the name of its argument.
SEARCH_HELP: Final[Message] = Message(
    "Find recipes by name, ingredient, or tag.",
    "按名称、食材或标签找菜谱。",
)
WORD_ARGUMENT: Final[Message] = Message("WORD", "词")

# The headings of the table.
ID_HEADING: Final[Message] = Message("ID", "ID")
NAME_HEADING: Final[Message] = Message("Name", "名称")
MATCHED_IN_HEADING: Final[Message] = Message("Matched in", "匹配于")

# The three places where a word can appear, rendered once per run.
NAME_PLACE: Final[Message] = Message("name", "名称")
INGREDIENT_PLACE: Final[Message] = Message("ingredient", "食材")
TAG_PLACE: Final[Message] = Message("tag", "标签")

# One word in quotation marks, as the count line names it.
QUOTED_WORD: Final[Message] = Message('"{word}"', "“{word}”")

# The count line for one word, and for two or more words, picked by the number of recipes.
RECIPES_MATCH: Final[Plural] = Plural(
    Message("{count} recipe matches {words}.", "{count} 个菜谱匹配{words}。"),
    Message("{count} recipes match {words}.", "{count} 个菜谱匹配{words}。"),
)
RECIPES_MATCH_ALL: Final[Plural] = Plural(
    Message("{count} recipe matches {words}.", "{count} 个菜谱同时匹配{words}。"),
    Message("{count} recipes match {words}.", "{count} 个菜谱同时匹配{words}。"),
)

# The one line when no recipe matches, for one word and for two or more words.
NO_RECIPE_MATCHES: Final[Message] = Message("No recipe matches {words}.", "没有菜谱匹配{words}。")
NO_RECIPE_MATCHES_ALL: Final[Message] = Message(
    "No recipe matches {words}.",
    "没有菜谱同时匹配{words}。",
)

# The usage error for a word with nothing in it.
EMPTY_WORD: Final[Message] = Message(
    'A word is empty. Look for a name, such as "recipe-menu search tomato".',
    "有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。",
)
