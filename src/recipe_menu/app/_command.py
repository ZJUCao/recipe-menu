"""The description of one command."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from recipe_menu.app._arguments import Arguments
from recipe_menu.app._context import Context
from recipe_menu.lang import BiText
from recipe_menu.text import Message


class FolderUse(Enum):
    """What ``cli`` checks before it runs a command.

    ``READ``: a missing data folder makes ``cli`` write ``NO_DATA_FOLDER`` and ``RUN_INIT`` and
    exit with 1, and an error in the settings makes it stop at the first error with
    ``stop_at_error`` and exit with 1. ``context.settings`` holds the settings of the file. This
    is for the commands that read the data.

    ``CHECK``: a missing data folder acts as for ``READ``, but an error in the settings does not
    stop the command, which reports the problems itself. ``context.settings`` holds the settings
    of the file, or ``Settings()`` after an error.

    ``CREATE``: neither a missing folder nor an error in the settings stops the command.
    ``context.settings`` holds the settings of the file, or ``Settings()`` when the folder is
    missing or the settings have an error.
    """

    READ = "read"
    CHECK = "check"
    CREATE = "create"


@dataclass(frozen=True, slots=True)
class Argument:
    """The argument of a command, which follows its words.

    The two flags give how many values the command line may give it, and how the help writes it:
    ``required`` and not ``repeats`` is exactly 1 value, written ``NAME``. Not ``required`` and
    not ``repeats`` is 0 or 1, written ``[NAME]``. ``required`` and ``repeats`` is 1 or more,
    written ``NAME...``. Neither is 0 or more, written ``[NAME...]``. Two arguments are equal
    when their three fields are equal, and an ``Argument`` is hashable.

    Attributes:
        name: The argument's name in the help, such as ``ID``, or ``WORD`` and its Chinese name.
            It has no placeholders.
        required: Whether the command line must give the argument.
        repeats: Whether the command line can give the argument more than once.
    """

    name: Message
    required: bool = True
    repeats: bool = False


@dataclass(frozen=True, slots=True)
class Command:
    """The description of one command.

    It holds the command's words, its help line, the function that runs it, its argument, its
    options, and what ``cli`` checks before it runs the command. Each command module defines its
    own, and ``cli`` reads the command line and writes the help from them. Two commands are equal
    when their six fields are equal, and a ``Command`` is hashable.

    The mock leaves the checks below out.

    Attributes:
        words: The command's words, such as ``("list",)`` or ``("menu", "show")``. There are 1 or
            2 words, each with only the small letters ``a`` to ``z``.
        help_line: The command's line in the help. It has no placeholders.
        run: Runs the command and gives its exit code, 0 or 1. It raises ``UsageError`` for a
            wrong argument value, before it writes any output.
        argument: The command's argument, or ``None`` for a command with no argument.
        options: The options of the command, each with a value, such as ``("--tag",)``. Each is
            ``--`` followed by a small letter and then small letters and ``-``. None is
            ``--lang``, ``--data``, ``--help``, or ``--version``. Each appears once.
        folder: What ``cli`` checks before it runs the command.

    Raises:
        ValueError: ``words`` is empty, has more than 2 words, or has a word with a character
            other than ``a`` to ``z``.
        ValueError: ``help_line`` or the argument's ``name`` has a placeholder.
        ValueError: An option breaks the rule of ``options``, is a global option, or appears
            twice.
    """

    words: tuple[str, ...]
    help_line: Message
    run: Callable[[Context, Arguments], int]
    argument: Argument | None = None
    options: tuple[str, ...] = ()
    folder: FolderUse = FolderUse.READ

    @property
    def usage(self) -> BiText:
        """Gives the command's usage, as the help and the usage errors show it.

        The mock raises ``NotImplementedError``. The implementation gives the usage by the rule
        below.

        Returns:
            The command's words joined by a space, and then, for a command with an argument, a
            space and the form of the argument in each language, as the table of ``Argument``
            gives it: ``show ID``, ``search WORD...`` and ``search`` with the Chinese name and
            ``...``, or ``menu show [WEEK]`` and ``menu show`` with the Chinese name in square
            brackets. A command with no argument gives only its words, in both languages.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError
