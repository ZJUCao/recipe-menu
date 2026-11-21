"""UTF-8 output and input for console streams."""

import io
from typing import TextIO


def use_utf8(stream: TextIO) -> None:
    """Makes a console stream write UTF-8.

    When ``stream`` is an ``io.TextIOWrapper``, this calls its ``reconfigure`` with
    ``encoding="utf-8"`` and ``errors="backslashreplace"``, so a lone surrogate is written as an
    escape and never raises. Any other stream, such as an ``io.StringIO``, stays as it is.

    Args:
        stream: An open output stream, such as ``sys.stdout``.
    """
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def use_utf8_input(stream: TextIO) -> None:
    """Makes a console input stream read UTF-8 and end each line with LF.

    When ``stream`` is an ``io.TextIOWrapper``, this calls its ``reconfigure`` with
    ``encoding="utf-8-sig"``, ``errors="replace"``, and ``newline=None``. The stream then drops a
    byte order mark at the start, turns a byte that is not UTF-8 into U+FFFD, and ends each line
    with LF on every system, also after CR LF or a lone CR. Any other stream, such as an
    ``io.StringIO``, stays as it is.

    Args:
        stream: An open input stream, such as ``sys.stdin``, that nothing has read yet.
    """
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8-sig", errors="replace", newline=None)
