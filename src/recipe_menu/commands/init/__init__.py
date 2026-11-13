"""The ``init`` command: creates the data folder with example data."""

from typing import Final

from recipe_menu.app import Command, FolderUse
from recipe_menu.commands.init._run import run_init
from recipe_menu.commands.init.messages import INIT_HELP

__all__ = ["INIT_COMMAND"]

# The description of ``recipe-menu init``, which ``cli`` reads to parse the command line, write
# the help, check the data folder, and run the command.
INIT_COMMAND: Final[Command] = Command(
    words=("init",),
    help_line=INIT_HELP,
    run=run_init,
    argument=None,
    options=(),
    folder=FolderUse.CREATE,
)
