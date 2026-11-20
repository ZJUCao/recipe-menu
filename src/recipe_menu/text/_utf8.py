"""UTF-8 output for console streams."""

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
    """Makes a console input stream read UTF-8.

    When ``stream`` is an ``io.TextIOWrapper``, the implementation calls its ``reconfigure`` with
    ``encoding="utf-8-sig"`` and ``errors="replace"``. Any other stream, such as an
    ``io.StringIO``, stays as it is. The mock changes nothing.

    Args:
        stream: An open input stream, such as ``sys.stdin``, that nothing has read yet.
    """
