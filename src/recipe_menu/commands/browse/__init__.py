"""The ``list`` and ``show`` commands: list the recipes, and show one recipe."""

from typing import Final

from recipe_menu.app import Argument, Command, FolderUse
from recipe_menu.commands.browse._run import run_list, run_show
from recipe_menu.commands.browse.messages import ID_ARGUMENT, LIST_HELP, SHOW_HELP

__all__ = ["LIST_COMMAND", "SHOW_COMMAND"]

# The description of ``recipe-menu list``, which ``cli`` reads to parse the command line, write the
# help, check the data folder, and run the command.
LIST_COMMAND: Final[Command] = Command(
    words=("list",),
    help_line=LIST_HELP,
    run=run_list,
    argument=None,
    options=("--tag",),
    folder=FolderUse.READ,
)

# The description of ``recipe-menu show``, with the required argument ``ID``.
SHOW_COMMAND: Final[Command] = Command(
    words=("show",),
    help_line=SHOW_HELP,
    run=run_show,
    argument=Argument(ID_ARGUMENT),
    options=("--servings",),
    folder=FolderUse.READ,
)
