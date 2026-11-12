"""Reading the arguments of the command line into words and options."""

from collections.abc import Sequence
from dataclasses import dataclass

FLAGS = ("--help", "--version")
LANG_OPTION_NAME = "--lang"
DATA_OPTION_NAME = "--data"
GLOBAL_VALUED = (LANG_OPTION_NAME, DATA_OPTION_NAME)


@dataclass(frozen=True, slots=True)
class Line:
    """The arguments of the command line, split into words, options, and flags.

    Attributes:
        words: The arguments that are not options, in the order of the line.
        options: Each option that takes a value, in the order of the line, as a pair of its name
            and its value. The value is ``None`` when the option has no value.
        help: Whether ``--help`` is on the line.
        version: Whether ``--version`` is on the line.
    """

    words: tuple[str, ...]
    options: tuple[tuple[str, str | None], ...]
    help: bool
    version: bool

    def first_value(self, name: str) -> str | None:
        """Gives the value of the first option of a name that has a value.

        Args:
            name: The name of the option, such as ``--lang``.

        Returns:
            The value, or ``None`` when no such option has a value.
        """
        for option, value in self.options:
            if option == name and value is not None:
                return value
        return None

    def has_global_option(self) -> bool:
        """Tells whether the line has a ``--lang`` or a ``--data``.

        Returns:
            ``True`` when it has one, with a value or without.
        """
        return any(name in GLOBAL_VALUED for name, _ in self.options)


def _takes(argv: Sequence[str], index: int) -> bool:
    """Tells whether the argument after an option is its value.

    Args:
        argv: The arguments.
        index: The place of the option.

    Returns:
        ``True`` when the next argument exists, is not empty, and does not start with ``--``.
    """
    following = argv[index + 1 : index + 2]
    return bool(following) and bool(following[0]) and not following[0].startswith("--")


def parse_line(argv: Sequence[str]) -> Line:
    """Reads the arguments by rules 1 to 3 of the command line.

    Args:
        argv: The arguments after the program's name.

    Returns:
        The words, the options with their values, and the two flags.
    """
    words: list[str] = []
    options: list[tuple[str, str | None]] = []
    flags: set[str] = set()
    index = 0
    while index < len(argv):
        argument = argv[index]
        index += 1
        if argument in FLAGS:
            flags.add(argument)
        elif not argument.startswith("--"):
            words.append(argument)
        elif _takes(argv, index - 1):
            options.append((argument, argv[index]))
            index += 1
        else:
            options.append((argument, None))
    return Line(tuple(words), tuple(options), "--help" in flags, "--version" in flags)
