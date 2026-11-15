"""The ``menu new`` and ``menu show`` commands: create and show a week menu."""

from typing import Final

from recipe_menu.app import Argument, Command, FolderUse
from recipe_menu.commands.menu._run import run_menu_new, run_menu_show
from recipe_menu.commands.menu.messages import (
    MENU_NEW_HELP,
    MENU_SHOW_HELP,
    WEEK_ARGUMENT,
)

__all__ = ["MENU_NEW_COMMAND", "MENU_SHOW_COMMAND"]

# The description of ``recipe-menu menu new``, with the optional argument ``WEEK``.
MENU_NEW_COMMAND: Final[Command] = Command(
    words=("menu", "new"),
    help_line=MENU_NEW_HELP,
    run=run_menu_new,
    argument=Argument(WEEK_ARGUMENT, required=False),
    options=(),
    folder=FolderUse.READ,
)

# The description of ``recipe-menu menu show``, with the optional argument ``WEEK``.
MENU_SHOW_COMMAND: Final[Command] = Command(
    words=("menu", "show"),
    help_line=MENU_SHOW_HELP,
    run=run_menu_show,
    argument=Argument(WEEK_ARGUMENT, required=False),
    options=(),
    folder=FolderUse.READ,
)
