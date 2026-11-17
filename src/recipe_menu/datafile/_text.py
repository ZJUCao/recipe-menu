"""Reading a file's text and parsing a TOML text that is not a file."""

from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem


def read_file_text(folder: DataFolder, path: Path) -> str | Problem:
    """Reads one data file as UTF-8 text.

    It takes steps 1 and 2 of ``read_toml``, with their problems, and does not parse the text.
    The text has no byte order mark, and a CR LF stays a CR LF. The mock gives the empty text.

    Args:
        folder: The data folder.
        path: The file to read, such as ``folder.menu_file("2026-W47")``. Inside
            ``folder.root``.

    Returns:
        The text of the file, or a ``Problem`` with ``Severity.ERROR`` and the file
        ``folder.relative(path)``.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, as ``DataFolder.relative`` finds.
            It is checked before the file is read.
    """
    return ""


def parse_toml(text: str) -> dict[str, object] | None:
    """Parses a TOML text that is not a file.

    It gives ``tomllib.loads(text)``, or ``None`` when ``tomllib`` raises ``TOMLDecodeError``,
    the plain ``ValueError`` of a number of too many digits, or ``RecursionError``. The mock
    gives ``None``.

    Args:
        text: The text to parse. Any string.

    Returns:
        The table of the text, or ``None`` when the text does not parse.
    """
    return None
