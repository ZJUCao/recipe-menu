"""What a command gets from the outside world."""

import io
from dataclasses import dataclass, field
from datetime import date
from random import Random
from typing import TextIO

from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings


@dataclass(frozen=True, slots=True)
class Context:
    """What a command gets from the outside world through ``cli``.

    ``cli`` builds it, and a test can build one with fixed values. Two contexts are equal when
    their eight fields are equal, and the streams and the generator compare as objects. A
    ``Context`` is hashable.

    Attributes:
        lang: The language that ``cli`` picked.
        folder: The data folder. Its ``root`` is absolute when ``cli`` builds it. The folder may
            be missing for a command with ``FolderUse.CREATE``.
        settings: The settings of the data folder. For a command with ``FolderUse.READ``, the
            settings that ``read_settings`` gave. For ``FolderUse.CHECK`` and
            ``FolderUse.CREATE``, those settings, or ``Settings()`` when the folder is missing
            or the settings have an error.
        out: Where the command writes its output. Open.
        err: Where the command writes a message that ends it with exit code 1. Open.
        today: Today's date on the PC, from which ``this`` and ``next`` weeks are found.
        random: The generator that a command draws its random choices from. ``cli`` passes the
            generator that ``main`` got or made. Without it, a new ``Random(0)`` for each
            context, so a test that builds a context gets the same choices every time.
        input: The stream that a command reads lines from. Open. ``cli`` passes the stream that
            ``main`` got, else ``sys.stdin``. Without it, a new empty ``io.StringIO`` for each
            context, so a command that reads finds the end of the input at once.
    """

    lang: Lang
    folder: DataFolder
    settings: Settings
    out: TextIO
    err: TextIO
    today: date
    random: Random = field(default_factory=lambda: Random(0))  # noqa: S311 - a fixed seed, no security
    input: TextIO = field(default_factory=io.StringIO)
