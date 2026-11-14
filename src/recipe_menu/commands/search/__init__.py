"""The ``search`` command: find the recipes that match every word."""

from typing import Final

from recipe_menu.app import Argument, Command, FolderUse
from recipe_menu.commands.search._run import run_search
from recipe_menu.commands.search.messages import SEARCH_HELP, WORD_ARGUMENT

__all__ = ["SEARCH_COMMAND"]

# The description of ``recipe-menu search``, with the required, repeating argument ``WORD``.
SEARCH_COMMAND: Final[Command] = Command(
    words=("search",),
    help_line=SEARCH_HELP,
    run=run_search,
    argument=Argument(WORD_ARGUMENT, repeats=True),
    options=(),
    folder=FolderUse.READ,
)
