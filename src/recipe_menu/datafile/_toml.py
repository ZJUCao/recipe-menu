"""Reading one data file as TOML."""

import os
import re
import tomllib
from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem
from recipe_menu.datafile.messages import (
    ACCESS_DENIED,
    BAD_ESCAPE,
    BAD_KEY,
    BAD_LINE,
    BAD_VALUE,
    CONTROL_CHARACTER,
    DEFINED_TWICE,
    EXTRA_TEXT,
    FILE_IS_FOLDER,
    FILE_MISSING,
    LINE,
    MISSING_BRACE,
    MISSING_BRACKET,
    MISSING_EQUALS,
    MISSING_QUOTE,
    NESTED_TOO_DEEPLY,
    NOT_TOML,
    NOT_UTF8,
    NUMBER_TOO_LONG,
    SYSTEM_ERROR,
)
from recipe_menu.lang import BiText
from recipe_menu.text import Message

_ENDING = re.compile(r" \(at (?:line (\d+), column \d+|end of document)\)$")

# The reasons of ``tomllib`` that have a message of their own, by exact text.
_EXACT_REASONS: dict[str, Message] = {
    "Unclosed array": MISSING_BRACKET,
    "Expected ']' at the end of a table declaration": MISSING_BRACKET,
    "Expected ']]' at the end of an array declaration": MISSING_BRACKET,
    "Unclosed inline table": MISSING_BRACE,
    "Unterminated string": MISSING_QUOTE,
    "Illegal character '\\n'": MISSING_QUOTE,
    "Found invalid character '\\n'": MISSING_QUOTE,
    'Expected "\'"': MISSING_QUOTE,
    "Expected \"'''\"": MISSING_QUOTE,
    "Invalid value": BAD_VALUE,
    "Expected '=' after a key in a key/value pair": MISSING_EQUALS,
    "Invalid initial character for a key part": BAD_KEY,
    "Expected newline or end of document after a statement": EXTRA_TEXT,
    "Invalid statement": BAD_LINE,
    "Cannot overwrite a value": DEFINED_TWICE,
    "Unescaped '\\' in a string": BAD_ESCAPE,
    "Invalid hex value": BAD_ESCAPE,
    "Escaped character is not a Unicode scalar value": BAD_ESCAPE,
}

# The reasons of ``tomllib`` that have a message of their own, by their start. The first
# prefix that fits decides.
_PREFIX_REASONS: tuple[tuple[str, Message], ...] = (
    ("Cannot declare ", DEFINED_TWICE),
    ("Duplicate inline table key ", DEFINED_TWICE),
    ("Cannot mutate immutable namespace ", DEFINED_TWICE),
    ("Cannot redefine namespace ", DEFINED_TWICE),
    ("Illegal character ", CONTROL_CHARACTER),
    ("Found invalid character ", CONTROL_CHARACTER),
)


def _line_place(line: int) -> BiText:
    """Gives the place of a line.

    Args:
        line: The line, counted from 1.

    Returns:
        The ``LINE`` message with ``line``, in both languages.
    """
    return LINE.to_bitext(line=line)


def _reason_message(reason: str) -> Message:
    """Finds the message for the reason of a ``TOMLDecodeError``.

    Args:
        reason: The error's text without its ending.

    Returns:
        The message of the reason, or ``NOT_TOML`` for a reason that is not known.
    """
    exact = _EXACT_REASONS.get(reason)
    if exact is not None:
        return exact
    for prefix, message in _PREFIX_REASONS:
        if reason.startswith(prefix):
            return message
    return NOT_TOML


def _is_folder(path: Path) -> bool:
    """Tells whether a path is a folder, and never raises.

    Args:
        path: The path to look at.

    Returns:
        ``True`` when ``path`` is a folder. ``False`` when it is not, or when the probe fails.
    """
    return os.path.isdir(path)  # noqa: PTH112


def _read_failure(relative: Path, path: Path, error: OSError) -> Problem:
    """Makes the problem of an ``OSError`` from reading the bytes.

    Args:
        relative: The file, relative to the data folder.
        path: The file that could not be read.
        error: The error.

    Returns:
        The problem, with no place.
    """
    if _is_folder(path):
        return Problem.error(relative, None, FILE_IS_FOLDER)
    if isinstance(error, FileNotFoundError | NotADirectoryError):
        return Problem.error(relative, None, FILE_MISSING)
    if isinstance(error, PermissionError):
        return Problem.error(relative, None, ACCESS_DENIED)
    reason = error.strerror or type(error).__name__
    return Problem.error(relative, None, SYSTEM_ERROR, reason=reason)


def _decode_failure(relative: Path, error: UnicodeDecodeError) -> Problem:
    """Makes the problem of text that is not UTF-8.

    Args:
        relative: The file, relative to the data folder.
        error: The error.

    Returns:
        The problem, at the line of the first byte that is not UTF-8.
    """
    line = error.object[: error.start].count(b"\n") + 1
    return Problem.error(relative, _line_place(line), NOT_UTF8)


def _syntax_failure(relative: Path, text: str, error: tomllib.TOMLDecodeError) -> Problem:
    """Makes the problem of a ``TOMLDecodeError``.

    Args:
        relative: The file, relative to the data folder.
        text: The text that was parsed.
        error: The error.

    Returns:
        The problem, with the message of the error's reason, at the error's line if it has one.
    """
    ending = _ENDING.search(str(error))
    reason = str(error)[: ending.start()] if ending else str(error)
    line: int | None = getattr(error, "lineno", None)
    if line is None and ending is not None:
        line = int(ending.group(1)) if ending.group(1) else text.count("\n") + 1
    place = None if line is None else _line_place(line)
    return Problem.error(relative, place, _reason_message(reason))


def _raises(text: str, kind: type[Exception]) -> bool:
    """Tells whether parsing a text raises an exception of one kind.

    Args:
        text: The text to parse.
        kind: ``ValueError`` for a plain ``ValueError`` that is not a ``TOMLDecodeError``, or
            ``RecursionError``.

    Returns:
        ``True`` when the parse raises that kind of exception.
    """
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return False
    except (ValueError, RecursionError) as error:
        return isinstance(error, kind)
    return False


def _first_failing_line(text: str, kind: type[Exception]) -> int:
    """Finds the first line for which parsing the text up to it raises the same kind of error.

    Args:
        text: The whole text, which raises ``kind``.
        kind: The kind of exception.

    Returns:
        The line N, counted from 1, found by a binary search.
    """
    lines = text.split("\n")
    low, high = 1, len(lines)
    while low < high:
        middle = (low + high) // 2
        if _raises("\n".join(lines[:middle]) + "\n", kind):
            high = middle
        else:
            low = middle + 1
    return low


def _parse(relative: Path, text: str) -> dict[str, object] | Problem:
    """Parses the text of a file as TOML.

    Args:
        relative: The file, relative to the data folder.
        text: The decoded text.

    Returns:
        The table, or the problem of the first failure.
    """
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        return _syntax_failure(relative, text, error)
    except ValueError:
        line = _first_failing_line(text, ValueError)
        return Problem.error(relative, _line_place(line), NUMBER_TOO_LONG)
    except RecursionError:
        line = _first_failing_line(text, RecursionError)
        return Problem.error(relative, _line_place(line), NESTED_TOO_DEEPLY)


def read_toml(folder: DataFolder, path: Path) -> dict[str, object] | Problem:
    r"""Reads one data file as TOML 1.0.

    The file is read in three steps. Step 1 reads the bytes. Step 2 decodes them with the
    ``utf-8-sig`` codec and strict errors. Step 3 parses the text with ``tomllib.loads``. A
    failure in a step gives one ``Problem`` and no exception.

    Args:
        folder: The data folder.
        path: The file to read, such as ``folder.catalog``. Inside ``folder.root``.

    Returns:
        The file's table, or a ``Problem`` with ``Severity.ERROR`` and the file
        ``folder.relative(path)``. The rules that decide the problem are these:

        * An ``OSError`` in step 1 gives a problem with no place. The message comes from the
          first row that applies: ``path`` is a folder, ``FILE_IS_FOLDER`` (the probe never
          raises, like ``os.path.isdir``, and a probe that fails counts as not a folder); a
          ``FileNotFoundError``, or a ``NotADirectoryError`` because a folder in the path is a
          file, ``FILE_MISSING``; a ``PermissionError``, ``ACCESS_DENIED``; any other
          ``OSError``, ``SYSTEM_ERROR`` with the value ``reason`` set to the error's
          ``strerror``, or to the name of the error's class when ``strerror`` is ``None`` or
          empty.
        * A ``UnicodeDecodeError`` in step 2 gives ``NOT_UTF8``, at the line of the first byte
          that is not UTF-8: one more than the number of LF bytes in
          ``error.object[:error.start]``.
        * A ``tomllib.TOMLDecodeError`` in step 3 gives the message for its reason: the reason
          is the error's text without the ending `` (at line N, column M)`` or `` (at end of
          document)``. ``MISSING_BRACKET`` for ``Unclosed array`` and for a missing ``]`` or
          ``]]`` at the end of a declaration; ``MISSING_BRACE`` for ``Unclosed inline table``;
          ``MISSING_QUOTE`` for ``Unterminated string``, an illegal or invalid ``\n``, and an
          expected ``'`` or ``'''``; ``BAD_VALUE`` for ``Invalid value``; ``MISSING_EQUALS``
          for a missing ``=`` after a key; ``BAD_KEY`` for ``Invalid initial character for a
          key part``; ``EXTRA_TEXT`` for ``Expected newline or end of document after a
          statement``; ``BAD_LINE`` for ``Invalid statement``; ``DEFINED_TWICE`` for ``Cannot
          overwrite a value`` and the reasons that start with ``Cannot declare ``,
          ``Duplicate inline table key ``, ``Cannot mutate immutable namespace ``, or
          ``Cannot redefine namespace ``; ``BAD_ESCAPE`` for an unescaped backslash, an invalid
          hex value, and an escaped character that is not a Unicode scalar value;
          ``CONTROL_CHARACTER`` for the other reasons that start with ``Illegal character `` or
          ``Found invalid character ``; ``NOT_TOML`` for every other reason. Its line is the
          error's ``lineno`` where there is one, else the N of the ending, else, for an end of
          document, one more than the number of LF characters in the text, else no place.
        * A ``ValueError`` that is not a ``TOMLDecodeError``, from a decimal integer of more
          than 4,300 digits, gives ``NUMBER_TOO_LONG``. A ``RecursionError``, from lists or
          tables nested too deeply, gives ``NESTED_TOO_DEEPLY``. Their line is the first line N
          for which parsing only lines 1 to N, each with its line break, raises the same kind
          of exception, found by a binary search.

        Every problem that has a line has the place of the ``LINE`` message with that line.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, as ``DataFolder.relative`` finds.
            It is checked before the file is read.
    """
    relative = folder.relative(path)
    try:
        data = path.read_bytes()
    except OSError as error:
        return _read_failure(relative, path, error)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        return _decode_failure(relative, error)
    return _parse(relative, text)
