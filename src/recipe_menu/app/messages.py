"""The messages of ``app``. All are internal to the module."""

from typing import Final

from recipe_menu.text import Message

# The line of ``problem_lines`` for a problem with a place. ``{file}`` is ``str(problem.file)``,
# and ``{place}`` is the problem's place as a ``BiText``.
FILE_AT_PLACE: Final[Message] = Message("{file}, {place}", "{file}，{place}")
