"""The help of the ``recipe-menu`` command."""

from collections.abc import Sequence

from recipe_menu.app import Command
from recipe_menu.cli.messages import (
    COMMANDS_HEADING,
    DATA_HELP,
    DATA_OPTION,
    HELP_HELP,
    HELP_OPTION,
    LANG_HELP,
    LANG_OPTION,
    OPTIONS_HEADING,
    SUMMARY,
    USAGE_LINE,
    VERSION_HELP,
    VERSION_OPTION,
    WEEK_NOTE,
)
from recipe_menu.lang import Lang
from recipe_menu.text import Message, display_width, format_table

_OPTIONS = (
    (LANG_OPTION, LANG_HELP),
    (DATA_OPTION, DATA_HELP),
    (VERSION_OPTION, VERSION_HELP),
    (HELP_OPTION, HELP_HELP),
)


def _width(commands: Sequence[Command]) -> int:
    """Finds the width of the first column of both tables, in either language.

    Args:
        commands: The commands.

    Returns:
        The largest display width of a first cell of either table, in either language.
    """
    cells = [command.usage.get(lang) for command in commands for lang in Lang]
    cells += [option.render(lang) for option, _ in _OPTIONS for lang in Lang]
    return max(display_width(cell) for cell in cells)


def help_text(commands: Sequence[Command], lang: Lang) -> str:
    """Gives the text of the help.

    Args:
        commands: The commands, in the order of the help.
        lang: The language of the help.

    Returns:
        The lines of the help, each ended by a line break.
    """
    width = _width(commands)
    command_rows = [
        (command.usage.get(lang), command.help_line.render(lang)) for command in commands
    ]
    option_rows = [(first.render(lang), second.render(lang)) for first, second in _OPTIONS]

    def table(rows: list[tuple[str, str]]) -> tuple[str, ...]:
        """Lays out one table with the common width.

        Args:
            rows: The rows.

        Returns:
            The lines of the table.
        """
        return format_table(rows, indent=2, min_widths=(width,))

    def text(message: Message) -> str:
        """Gives the text of a message of the help.

        Args:
            message: The message.

        Returns:
            Its text in the language of the help.
        """
        return message.render(lang)

    lines = [text(USAGE_LINE), "", text(SUMMARY), "", text(COMMANDS_HEADING), *table(command_rows)]
    lines += ["", text(OPTIONS_HEADING), *table(option_rows), "", text(WEEK_NOTE)]
    return "".join(f"{line}\n" for line in lines)
