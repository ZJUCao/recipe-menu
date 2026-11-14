"""The commands of recipe-menu, in the order of the help."""

from typing import Final

from recipe_menu.app import Command
from recipe_menu.commands.browse import LIST_COMMAND, SHOW_COMMAND
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.commands.search import SEARCH_COMMAND

# Each command feature imports its command module's ``Command`` values here, in its mock PR, at
# its place in the order of the help.
COMMANDS: Final[tuple[Command, ...]] = (
    INIT_COMMAND,
    CHECK_COMMAND,
    LIST_COMMAND,
    SHOW_COMMAND,
    SEARCH_COMMAND,
)
