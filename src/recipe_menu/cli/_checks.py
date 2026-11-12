"""The checks of the command line that give a ``UsageError``."""

from collections.abc import Sequence

from recipe_menu.app import Command, UsageError
from recipe_menu.cli._parse import GLOBAL_VALUED, LANG_OPTION_NAME, Line
from recipe_menu.cli.messages import (
    INCOMPLETE_COMMAND,
    LANG_NOT_EN_OR_ZH,
    NO_COMMAND,
    OPTION_NEEDS_VALUE,
    OPTION_TWICE,
    TOO_FEW_ARGUMENTS,
    TOO_MANY_ARGUMENTS,
    UNKNOWN_COMMAND,
    UNKNOWN_OPTION,
    UNKNOWN_OPTION_NONE,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import RUN_HELP_FOR_COMMANDS, RUN_HELP_FOR_OPTIONS, and_list


def check_commands(commands: Sequence[Command]) -> None:
    """Checks the commands that ``main`` gets.

    Args:
        commands: The commands.

    Raises:
        ValueError: Two commands have the same words, or a one-word command has the first word
            of a two-word command.
    """
    two_words = {command.words[0] for command in commands if len(command.words) == 2}
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        if command.words in seen or (len(command.words) == 1 and command.words[0] in two_words):
            raise ValueError(f"the commands clash at {command.words!r}")
        seen.add(command.words)


def _check_global(name: str, value: str | None, seen: set[str]) -> None:
    """Checks one ``--lang`` or ``--data``.

    Args:
        name: The name of the option.
        value: Its value, or ``None`` when it has none.
        seen: The names that an earlier option with a value gave. This adds ``name``.

    Raises:
        UsageError: The option has no value, comes twice, or is a ``--lang`` that is neither
            ``en`` nor ``zh``.
    """
    if value is None:
        raise UsageError(OPTION_NEEDS_VALUE, RUN_HELP_FOR_OPTIONS, option=name)
    if name in seen:
        raise UsageError(OPTION_TWICE, RUN_HELP_FOR_OPTIONS, option=name)
    if name == LANG_OPTION_NAME and value not in Lang:
        raise UsageError(LANG_NOT_EN_OR_ZH, RUN_HELP_FOR_OPTIONS, lang=value)
    seen.add(name)


def check_globals(line: Line) -> None:
    """Checks each ``--lang`` and each ``--data`` in the order of the line (step 4).

    Args:
        line: The arguments.

    Raises:
        UsageError: For the first option that is wrong. The first rule that applies gives the
            error: no value, a second option of the name, or a wrong language.
    """
    seen: set[str] = set()
    for name, value in line.options:
        if name in GLOBAL_VALUED:
            _check_global(name, value, seen)


def _quoted(text: str) -> BiText:
    """Puts a text in the quotation marks of each language.

    Args:
        text: The text.

    Returns:
        The text in straight quotation marks in English and in curved ones in Chinese.
    """
    return BiText(f'"{text}"', f"“{text}”")


def _unknown_command(words: Sequence[str]) -> UsageError:
    """Makes the error of words that name no command.

    Args:
        words: The words that name no command.

    Returns:
        The error.
    """
    return UsageError(UNKNOWN_COMMAND, RUN_HELP_FOR_COMMANDS, command=" ".join(words))


def find_command(
    words: Sequence[str], commands: Sequence[Command]
) -> tuple[Command, tuple[str, ...]]:
    """Finds the command in the words (step 6).

    Args:
        words: The words of the line.
        commands: The commands.

    Returns:
        The command and the words that follow its own, which are the values of its argument.

    Raises:
        UsageError: There is no word, the first word starts no command, a two-word command
            lacks its second word, or the second word completes no command.
    """
    if not words:
        raise UsageError(NO_COMMAND, RUN_HELP_FOR_COMMANDS)
    starting = [command for command in commands if command.words[0] == words[0]]
    if not starting:
        raise _unknown_command(words[:1])
    if len(starting[0].words) == 1:
        return starting[0], tuple(words[1:])
    if len(words) < 2:
        listed = and_list(_quoted(" ".join(command.words)) for command in starting)
        message = INCOMPLETE_COMMAND.pick(len(starting))
        raise UsageError(message, RUN_HELP_FOR_COMMANDS, word=words[0], commands=listed)
    for command in starting:
        if command.words == tuple(words[:2]):
            return command, tuple(words[2:])
    raise _unknown_command(words[:2])


def _unknown_option(command: Command, name: str) -> UsageError:
    """Makes the error of an option that the command does not declare.

    Args:
        command: The command.
        name: The option.

    Returns:
        The error, in the form for the number of the command's options.
    """
    words = " ".join(command.words)
    if not command.options:
        return UsageError(UNKNOWN_OPTION_NONE, RUN_HELP_FOR_OPTIONS, command=words, option=name)
    listed = and_list(_quoted(option) for option in command.options)
    message = UNKNOWN_OPTION.pick(len(command.options))
    return UsageError(message, RUN_HELP_FOR_OPTIONS, command=words, option=name, options=listed)


def check_options(command: Command, line: Line) -> tuple[tuple[str, str], ...]:
    """Checks the command's options in the order of the line (step 7).

    Args:
        command: The command.
        line: The arguments.

    Returns:
        The options of the command with their values, in the order of the line.

    Raises:
        UsageError: For the first option that is wrong. The first rule that applies gives the
            error: the command does not declare it, it has no value, or it comes twice.
    """
    found: list[tuple[str, str]] = []
    for name, value in line.options:
        if name in GLOBAL_VALUED:
            continue
        if name not in command.options:
            raise _unknown_option(command, name)
        if value is None:
            raise UsageError(OPTION_NEEDS_VALUE, None, option=name)
        if any(name == earlier for earlier, _ in found):
            raise UsageError(OPTION_TWICE, None, option=name)
        found.append((name, value))
    return tuple(found)


def check_values(command: Command, values: Sequence[str]) -> None:
    """Checks the number of values of the command's argument (step 8).

    Args:
        command: The command.
        values: The values that the line gives.

    Raises:
        UsageError: The argument has too few values or too many.
    """
    argument = command.argument
    if argument is None:
        fewest, most = 0, 0
    else:
        fewest = 1 if argument.required else 0
        most = len(values) if argument.repeats else 1
    if len(values) < fewest:
        raise UsageError(TOO_FEW_ARGUMENTS, RUN_HELP_FOR_COMMANDS, usage=command.usage)
    if len(values) > most:
        raise UsageError(
            TOO_MANY_ARGUMENTS, RUN_HELP_FOR_COMMANDS, argument=values[most], usage=command.usage
        )
