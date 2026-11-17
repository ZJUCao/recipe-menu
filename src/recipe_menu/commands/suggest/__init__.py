"""The ``menu suggest`` command: fill the empty meals of a week menu with random recipes."""

from typing import Final

from recipe_menu.app import Argument, Command, FolderUse
from recipe_menu.commands.suggest._run import run_menu_suggest
from recipe_menu.commands.suggest.messages import MENU_SUGGEST_HELP, WEEK_ARGUMENT

__all__ = ["MENU_SUGGEST_COMMAND"]

# The description of ``recipe-menu menu suggest``, with the optional argument ``WEEK`` and the
# option ``--tag``.
MENU_SUGGEST_COMMAND: Final[Command] = Command(
    words=("menu", "suggest"),
    help_line=MENU_SUGGEST_HELP,
    run=run_menu_suggest,
    argument=Argument(WEEK_ARGUMENT, required=False),
    options=("--tag",),
    folder=FolderUse.READ,
)
