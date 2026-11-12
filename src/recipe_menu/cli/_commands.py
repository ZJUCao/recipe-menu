"""The commands of recipe-menu, in the order of the help."""

from typing import Final

from recipe_menu.app import Command

# Each command feature imports its command module's ``Command`` values here, in its mock PR, at
# its place in the order of the help.
COMMANDS: Final[tuple[Command, ...]] = ()
