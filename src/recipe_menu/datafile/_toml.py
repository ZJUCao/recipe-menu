"""Reading one data file as TOML."""

from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem


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
          first row that applies: ``path`` is a folder, ``FILE_IS_FOLDER`` (a probe that fails
          counts as not a folder, and it never raises, as ``os.path.isdir`` does); a
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
        NotImplementedError: In the mock.
    """
    raise NotImplementedError
