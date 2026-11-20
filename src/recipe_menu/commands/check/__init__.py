"""The ``check`` command: reads every data file and reports its errors and warnings."""

from typing import Final

from recipe_menu.app import Command, FolderUse
from recipe_menu.commands.check._recipe import check_recipe, problem_block
from recipe_menu.commands.check._run import run_check
from recipe_menu.commands.check.messages import CHECK_HELP

__all__ = ["CHECK_COMMAND", "check_recipe", "problem_block"]

# The description of ``recipe-menu check``, which ``cli`` reads to parse the command line, write
# the help, check the data folder, and run the command.
CHECK_COMMAND: Final[Command] = Command(
    words=("check",),
    help_line=CHECK_HELP,
    run=run_check,
    argument=None,
    options=(),
    folder=FolderUse.CHECK,
)
