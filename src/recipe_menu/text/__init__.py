"""Messages, lists, plurals, width, tables, and UTF-8 output, in two languages."""

from recipe_menu.text._lang import choose_lang
from recipe_menu.text._lists import and_list, comma_list
from recipe_menu.text._message import Message, MessageValue, Plural
from recipe_menu.text._table import display_width, format_table
from recipe_menu.text._utf8 import use_utf8, use_utf8_input
from recipe_menu.text.messages import RUN_CHECK, RUN_HELP_FOR_COMMANDS, RUN_HELP_FOR_OPTIONS

__all__ = [
    "RUN_CHECK",
    "RUN_HELP_FOR_COMMANDS",
    "RUN_HELP_FOR_OPTIONS",
    "Message",
    "MessageValue",
    "Plural",
    "and_list",
    "choose_lang",
    "comma_list",
    "display_width",
    "format_table",
    "use_utf8",
    "use_utf8_input",
]
