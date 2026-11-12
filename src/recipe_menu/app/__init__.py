"""The values that connect ``cli`` with the commands, and the shared way to stop at an error."""

from recipe_menu.app._arguments import Arguments
from recipe_menu.app._command import Argument, Command, FolderUse
from recipe_menu.app._context import Context
from recipe_menu.app._problems import first_error, problem_lines, stop_at_error
from recipe_menu.app._usage_error import UsageError

__all__ = [
    "Argument",
    "Arguments",
    "Command",
    "Context",
    "FolderUse",
    "UsageError",
    "first_error",
    "problem_lines",
    "stop_at_error",
]
