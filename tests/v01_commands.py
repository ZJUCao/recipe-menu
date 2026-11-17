"""The commands of version 0.1, in the order of the help, for tests that must not see later ones.

A test that checks the help or the line of a command family against the F05 prototype passes
these commands to the command line in place of the real list, so a command that a later feature
adds does not change what it compares. The module holds a fixed tuple and does nothing else.
Nothing here calls an interface of the commands when the module is imported, and the module keeps
the real list of commands away.
"""

from recipe_menu.commands.browse import LIST_COMMAND, SHOW_COMMAND
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.commands.menu import MENU_NEW_COMMAND, MENU_SHOW_COMMAND
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.commands.shop import SHOP_COMMAND

V01_COMMANDS = (
    INIT_COMMAND,
    CHECK_COMMAND,
    LIST_COMMAND,
    SHOW_COMMAND,
    SEARCH_COMMAND,
    MENU_NEW_COMMAND,
    MENU_SHOW_COMMAND,
    SHOP_COMMAND,
)
