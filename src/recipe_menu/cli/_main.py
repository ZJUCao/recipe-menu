"""The entry point of the ``recipe-menu`` command."""

import os
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import TextIO

from recipe_menu import __version__
from recipe_menu.app import (
    Arguments,
    Command,
    Context,
    FolderUse,
    UsageError,
    first_error,
    stop_at_error,
)
from recipe_menu.cli._checks import (
    check_commands,
    check_globals,
    check_options,
    check_values,
    find_command,
)
from recipe_menu.cli._commands import COMMANDS
from recipe_menu.cli._folder import find_root
from recipe_menu.cli._help import help_text
from recipe_menu.cli._parse import LANG_OPTION_NAME, Line, parse_line
from recipe_menu.cli.messages import NO_DATA_FOLDER, RUN_INIT, VERSION_LINE
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings, read_settings
from recipe_menu.text import choose_lang, use_utf8


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    today: date | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    commands: Sequence[Command] | None = None,
) -> int:
    r"""Runs the ``recipe-menu`` command line and gives its exit code.

    It reads the outside world, runs the command line, and gives the exit code. The console
    script and ``python -m recipe_menu`` pass the code to ``sys.exit``. Tests call it with fixed
    values.

    Args:
        argv: The arguments after the program's name. ``None`` gives ``sys.argv[1:]``.
        environ: The environment variables. ``main`` reads only ``RECIPE_MENU_DATA``. ``None``
            gives ``os.environ``.
        home: The home folder, for the default data folder and a leading ``~``. ``None`` gives
            ``Path.home()``.
        today: Today's date. ``None`` gives the local date of the PC's clock.
        stdout: The output stream. ``None`` gives ``sys.stdout``, after ``use_utf8``.
        stderr: The error stream. ``None`` gives ``sys.stderr``, after ``use_utf8``.
        commands: The commands, in the order of the help. ``None`` gives ``COMMANDS``. No two
            commands have the same words, and no one-word command has the first word of a
            two-word command.

    Returns:
        The exit code. It is 0 for the help, the version, or a command that worked. It is 1
        when the data folder is missing, the settings have an error, or the command gave 1. It
        is 2 for a ``UsageError``. It is 130 for Ctrl+C at any step, with nothing more written.
        ``main`` turns only a ``UsageError`` into 2 and ``KeyboardInterrupt`` into 130. Any other
        exception from a command is a bug and goes on to Python, which shows its traceback. It
        catches no error of the console streams.

        The rules for reading the arguments are these. An argument that starts with ``--`` is an
        option. ``--help`` and ``--version`` are flags. A flag may repeat. Every other option
        takes the next argument as its value, unless that argument is missing, empty, or starts
        with ``--``. Then the option has no value, and the next argument is read on its own.
        Every other argument is a word: the first one or two words are the command's words, and
        the rest are the values of its argument, in order. Options and words can come in any
        order. ``--lang``, ``--data``, ``--help``, and ``--version`` are global, and every other
        option belongs to the command. The forms ``--lang=zh`` and ``-l zh`` and abbreviations
        are not accepted.

        The data folder is the value of the first ``--data`` that has a value. Without one, it is
        the value of ``RECIPE_MENU_DATA`` when it is set and not empty. Without either, it is
        ``home / "recipe-menu"``. A value that is ``~``, or starts with ``~/``, or on Windows
        starts with ``~\``, has its first part replaced with ``home``. The text decides, not
        ``Path(value).parts``, because ``pathlib`` drops a leading ``.``. So ``./~/x``, and on
        Windows ``.\~\x``, name the folder ``~`` in the current folder. No other form of ``~``
        and no variable is expanded. A relative path is made absolute with ``Path.absolute()``
        from the current folder, and links are not resolved.

        ``main`` takes these steps, in order. It reads the arguments and finds the data folder.
        It reads the settings with ``read_settings`` when ``os.path.isdir`` says that the data
        folder is a folder. It picks the language with ``choose_lang``, from the first ``--lang``
        that has a value when that value is ``en`` or ``zh``, and from the ``language`` of the
        settings when ``read_settings`` gave a ``Settings``. Every message from here on is in
        that language, a usage error included. It checks each ``--lang`` and each ``--data`` in
        the order of the line, where the first rule that applies gives the error: no value gives
        ``OPTION_NEEDS_VALUE``, a second one gives ``OPTION_TWICE``, and a value of ``--lang``
        other than ``en`` and ``zh`` gives ``LANG_NOT_EN_OR_ZH``. With ``--help`` on the line it
        writes the help to ``stdout`` and gives 0, and otherwise with ``--version`` it writes
        the version line with ``__version__`` to ``stdout`` and gives 0. It finds the command in
        the words: no word gives ``NO_COMMAND``, a first word that starts no command gives
        ``UNKNOWN_COMMAND``, a first word that starts two-word commands with no second word gives
        ``INCOMPLETE_COMMAND``, and a second word that completes no command gives
        ``UNKNOWN_COMMAND`` with both words. It checks the command's options in the order of the
        line, where the first rule that applies gives the error: an option that the command does
        not declare gives ``UNKNOWN_OPTION``, no value gives ``OPTION_NEEDS_VALUE`` with no
        hint, and the second of two gives ``OPTION_TWICE`` with no hint. So
        ``list --tag a --tag`` gives ``OPTION_NEEDS_VALUE``. It checks the number of values of
        the argument: too few give ``TOO_FEW_ARGUMENTS``, and too many give
        ``TOO_MANY_ARGUMENTS``, which names the first value too many. It checks the data folder
        and the settings as the command's ``FolderUse`` says: a missing data folder gives
        ``NO_DATA_FOLDER`` and ``RUN_INIT`` on ``stderr`` with 1, and an error in the settings
        gives ``stop_at_error`` with the first error and 1. It builds the ``Context`` and the
        ``Arguments``, runs the command, and gives the code that ``run`` gives.

        For a ``UsageError`` from the checks of the options, the command, or the argument, or
        from ``run``, it writes ``error.text(lang)`` and then the hint when there is one, each
        on its own line, to ``stderr``, and gives 2. The hint of ``UNKNOWN_OPTION``,
        ``LANG_NOT_EN_OR_ZH``, and ``OPTION_NEEDS_VALUE`` and ``OPTION_TWICE`` of ``--lang`` and
        ``--data`` is ``RUN_HELP_FOR_OPTIONS``. The hint of ``NO_COMMAND``, ``UNKNOWN_COMMAND``,
        ``INCOMPLETE_COMMAND``, ``TOO_FEW_ARGUMENTS``, and ``TOO_MANY_ARGUMENTS`` is
        ``RUN_HELP_FOR_COMMANDS``. ``OPTION_NEEDS_VALUE`` and ``OPTION_TWICE`` of an option of
        the command have no hint.

        The help is these lines, each ended by a line break: the usage line, an empty line, the
        summary, an empty line, the heading of the commands, the table of the commands, an empty
        line, the heading of the options, the table of the options, an empty line, and the note
        on weeks. The commands come in the order of ``commands``, each with ``usage`` and its
        help line. The options are ``--lang``, ``--data``, ``--version``, and ``--help``, in this
        order. Both tables are ``format_table(rows, indent=2, min_widths=(width,))``, where
        ``width`` is the largest ``display_width`` of a first cell of either table in either
        language, so the second column starts at the same place in both languages.

        The values of the messages are these. ``option`` and ``lang`` are as the line writes
        them. ``command`` is the command's words, or the words that name no command, joined by a
        space. ``word`` is the first word. ``commands`` is ``and_list`` of the quoted words of
        each command that starts with ``word``, in the order of ``commands``. ``options`` is
        ``and_list`` of the command's options, each in quotation marks, in the order of the
        command's ``options``. ``UNKNOWN_OPTION`` has three forms: one for a command with no
        options, one for one option, and one for more. ``INCOMPLETE_COMMAND`` has two forms,
        picked by the number of commands that start with ``word``: one for one command, and
        one for more. ``usage`` is the command's ``usage``. ``argument`` is the first value too
        many. ``folder`` is ``str(folder.root)``, the full
        path. ``version`` is ``__version__``.

    Raises:
        ValueError: ``commands`` has two commands with the same words, or a one-word command
            has the first word of a two-word command. It is raised before the arguments are
            read.
    """
    selected = tuple(COMMANDS if commands is None else commands)
    check_commands(selected)
    try:
        outside = _Outside(
            os.environ if environ is None else environ,
            _home_getter(home),
            datetime.now().astimezone().date() if today is None else today,
            _stream(stdout, sys.stdout),
            _stream(stderr, sys.stderr),
            selected,
        )
        return _run(sys.argv[1:] if argv is None else argv, outside)
    except KeyboardInterrupt:
        return 130


@dataclass(frozen=True, slots=True)
class _Outside:
    """The outside world that ``main`` reads once.

    Attributes:
        environ: The environment variables.
        get_home: Gives the home folder. It is called only when a rule needs it.
        today: Today's date.
        out: The output stream.
        err: The error stream.
        commands: The commands, in the order of the help.
    """

    environ: Mapping[str, str]
    get_home: Callable[[], Path]
    today: date
    out: TextIO
    err: TextIO
    commands: tuple[Command, ...]


@dataclass(frozen=True, slots=True)
class _Start:
    """What ``main`` knows after steps 1 to 3.

    Attributes:
        folder: The data folder.
        present: Whether the data folder is a folder.
        settings: The settings of the folder, or ``None`` when it has none or they have an error.
        problems: The problems of the settings.
        lang: The language of every message.
    """

    folder: DataFolder
    present: bool
    settings: Settings | None
    problems: tuple[Problem, ...]
    lang: Lang


def _home_getter(home: Path | None) -> Callable[[], Path]:
    """Makes the function that gives the home folder.

    Args:
        home: The home folder that ``main`` got, or ``None``.

    Returns:
        A function that gives ``home``, or ``Path.home()`` when ``home`` is ``None``.
    """

    def get_home() -> Path:
        """Gives the home folder.

        Returns:
            The home folder.
        """
        return Path.home() if home is None else home

    return get_home


def _stream(stream: TextIO | None, console: TextIO) -> TextIO:
    """Picks a stream, and makes the console write UTF-8.

    Args:
        stream: The stream that ``main`` got, or ``None``.
        console: The console stream for ``None``.

    Returns:
        ``stream``, or ``console`` after ``use_utf8``.
    """
    if stream is not None:
        return stream
    use_utf8(console)
    return console


def _write_lines(stream: TextIO, lines: Sequence[str]) -> None:
    """Writes lines, each ended by a line break.

    Args:
        stream: The stream.
        lines: The lines.
    """
    stream.write("".join(f"{line}\n" for line in lines))


def _write_version(outside: _Outside, lang: Lang) -> int:
    """Writes the version line.

    Args:
        outside: The outside world.
        lang: The language of the line.

    Returns:
        0.
    """
    _write_lines(outside.out, [VERSION_LINE.render(lang, version=__version__)])
    return 0


def _option_lang(line: Line) -> Lang | None:
    """Finds the language that the first ``--lang`` with a value names.

    Args:
        line: The arguments.

    Returns:
        The language, or ``None`` when there is no such option or its value is not a language.
    """
    value = line.first_value(LANG_OPTION_NAME)
    return Lang(value) if value is not None and value in Lang else None


def _start(line: Line, outside: _Outside) -> _Start:
    """Takes steps 1 to 3: the data folder, the settings, and the language.

    Args:
        line: The arguments.
        outside: The outside world.

    Returns:
        What the later steps need.
    """
    folder = DataFolder(find_root(line, outside.environ, outside.get_home))
    present = os.path.isdir(folder.root)  # noqa: PTH112 (it never raises)
    settings, problems = read_settings(folder) if present else (None, ())
    lang = choose_lang(_option_lang(line), None if settings is None else settings.language)
    return _Start(folder, present, settings, problems, lang)


def _run(argv: Sequence[str], outside: _Outside) -> int:
    """Runs the steps of the command line and writes a usage error.

    A line with ``--version`` and no ``--help``, ``--lang``, or ``--data`` takes a fast path: it
    writes the version line in English and gives 0, without steps 1 to 4. The output is the same
    as steps 1 to 5 give. Step 4 has no ``--lang`` or ``--data`` to check, step 5 ignores the
    rest of the line, and the version line has the same text in both languages, so the language
    that steps 1 to 3 would choose does not matter. The fast path also keeps ``--version``
    working when there is no home folder.

    Args:
        argv: The arguments.
        outside: The outside world.

    Returns:
        The exit code.
    """
    line = parse_line(argv)
    if line.version and not line.help and not line.has_global_option():
        return _write_version(outside, Lang.EN)
    start = _start(line, outside)
    try:
        return _answer(line, outside, start)
    except UsageError as error:
        lines = [error.text(start.lang)]
        if error.hint is not None:
            lines.append(error.hint.render(start.lang))
        _write_lines(outside.err, lines)
        return 2


def _answer(line: Line, outside: _Outside, start: _Start) -> int:
    """Takes steps 4 to 10.

    Args:
        line: The arguments.
        outside: The outside world.
        start: What steps 1 to 3 found.

    Returns:
        The exit code.

    Raises:
        UsageError: The command line is wrong, or the command raises it.
    """
    check_globals(line)
    if line.help:
        outside.out.write(help_text(outside.commands, start.lang))
        return 0
    if line.version:
        return _write_version(outside, start.lang)
    command, values = find_command(line.words, outside.commands)
    arguments = Arguments(values, check_options(command, line))
    check_values(command, values)
    return _execute(command, arguments, outside, start)


def _execute(command: Command, arguments: Arguments, outside: _Outside, start: _Start) -> int:
    """Takes steps 9 and 10: checks the data folder and the settings, and runs the command.

    Args:
        command: The command.
        arguments: What the line gives it.
        outside: The outside world.
        start: What steps 1 to 3 found.

    Returns:
        The exit code.

    Raises:
        UsageError: The command raises it.
    """
    lang = start.lang
    settings = Settings() if start.settings is None else start.settings
    context = Context(lang, start.folder, settings, outside.out, outside.err, outside.today)
    if command.folder is not FolderUse.CREATE and not start.present:
        folder = str(start.folder.root)
        _write_lines(
            outside.err, [NO_DATA_FOLDER.render(lang, folder=folder), RUN_INIT.render(lang)]
        )
        return 1
    error = first_error(start.problems)
    if command.folder is FolderUse.READ and error is not None:
        return stop_at_error(context, error)
    return command.run(context, arguments)
