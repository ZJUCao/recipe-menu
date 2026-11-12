"""What a command gets from the outside world."""

from dataclasses import dataclass
from datetime import date
from typing import TextIO

from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings


@dataclass(frozen=True, slots=True)
class Context:
    """What a command gets from the outside world through ``cli``.

    ``cli`` builds it, and a test can build one with fixed values. Two contexts are equal when
    their six fields are equal, and the streams compare as objects. A ``Context`` is hashable.

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
    """

    lang: Lang
    folder: DataFolder
    settings: Settings
    out: TextIO
    err: TextIO
    today: date
