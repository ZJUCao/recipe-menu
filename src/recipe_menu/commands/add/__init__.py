"""The ``add`` command: ask for a new recipe one line at a time and write its file."""

from typing import Final

from recipe_menu.app import Command, FolderUse
from recipe_menu.commands.add._run import run_add
from recipe_menu.commands.add.messages import ADD_HELP

__all__ = ["ADD_COMMAND"]

# The description of ``recipe-menu add``, which takes no argument and no option.
ADD_COMMAND: Final[Command] = Command(
    words=("add",),
    help_line=ADD_HELP,
    run=run_add,
    argument=None,
    options=(),
    folder=FolderUse.READ,
)
