"""The ``shop`` command: make the shopping list of a week menu and save it."""

from typing import Final

from recipe_menu.app import Argument, Command, FolderUse
from recipe_menu.commands.shop._run import run_shop
from recipe_menu.commands.shop.messages import SHOP_HELP, WEEK_ARGUMENT

__all__ = ["SHOP_COMMAND"]

# The description of ``recipe-menu shop``, with the optional argument ``WEEK``.
SHOP_COMMAND: Final[Command] = Command(
    words=("shop",),
    help_line=SHOP_HELP,
    run=run_shop,
    argument=Argument(WEEK_ARGUMENT, required=False),
    options=(),
    folder=FolderUse.READ,
)
