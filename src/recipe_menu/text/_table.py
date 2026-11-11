"""Display width and aligned tables."""

import unicodedata
from collections.abc import Sequence


def _char_width(char: str) -> int:
    """Gives the columns of one character.

    Args:
        char: One character.

    Returns:
        0 for a combining mark, 2 for a wide or fullwidth character, else 1.
    """
    if unicodedata.category(char) in ("Mn", "Me"):
        return 0
    if unicodedata.east_asian_width(char) in ("W", "F"):
        return 2
    return 1


def display_width(text: str) -> int:
    """Counts the columns that a text takes in Windows Terminal.

    Args:
        text: The text to measure. Any string. A line break counts as one column like any other
            character, so measure one line at a time.

    Returns:
        The sum of the columns of the characters in ``text``, 0 for the empty string. Each
        character takes the columns of the first rule that applies, with ``unicodedata``: a
        combining mark (general category ``Mn`` or ``Me``) takes 0 columns; a character whose
        East Asian width is ``W`` or ``F`` takes 2 columns; every other character takes 1
        column, including the ambiguous ones such as the curly quote, the em dash, and the
        multiplication sign, and the spacing marks of category ``Mc``.
    """
    return sum(_char_width(char) for char in text)


def _check_args(
    rows: Sequence[Sequence[str]], indent: int, gap: int, min_widths: Sequence[int]
) -> None:
    """Checks the arguments of ``format_table``.

    Args:
        rows: The rows.
        indent: The spaces before each line.
        gap: The spaces between two columns.
        min_widths: The smallest width of each column.

    Raises:
        TypeError: ``rows`` or one of its rows is a ``str``.
        ValueError: An argument is out of range, or the rows are not of one width.
    """
    if isinstance(rows, str) or any(isinstance(row, str) for row in rows):
        raise TypeError("rows and each row must not be a str")
    if indent < 0 or gap < 1 or any(width < 0 for width in min_widths):
        raise ValueError("indent, gap, or min_widths is out of range")
    if not rows:
        return
    count = len(rows[0])
    if count == 0 or any(len(row) != count for row in rows):
        raise ValueError("the rows must all have the same number of cells, 1 or more")
    if len(min_widths) > count:
        raise ValueError("min_widths has more items than a row has cells")


def _row_lines(row: Sequence[str]) -> list[list[str]]:
    """Splits the cells of a row into lines, padded to the same height.

    Args:
        row: The cells of one row.

    Returns:
        One list of lines for each line of the row, each with one text per cell.
    """
    cells = [cell.splitlines() or [""] for cell in row]
    height = max(len(lines) for lines in cells)
    return [[lines[i] if i < len(lines) else "" for lines in cells] for i in range(height)]


def _join_line(cells: Sequence[str], widths: Sequence[int], indent: int, gap: int) -> str:
    """Joins the cells of one line into a padded line.

    Args:
        cells: One text for each column.
        widths: The width of each column.
        indent: The spaces before the line.
        gap: The spaces after each column but the last.

    Returns:
        The line, with no trailing spaces.
    """
    last = len(cells) - 1
    parts = [" " * indent]
    for index, text in enumerate(cells):
        parts.append(text)
        if index < last:
            parts.append(" " * (widths[index] - display_width(text) + gap))
    return "".join(parts).rstrip(" ")


def format_table(
    rows: Sequence[Sequence[str]],
    *,
    indent: int = 0,
    gap: int = 3,
    min_widths: Sequence[int] = (),
) -> tuple[str, ...]:
    """Lays out rows as left-aligned columns by display width.

    Args:
        rows: The rows, with the header first when the table has one. Not a ``str``, and no row
            is a ``str``. Every row has the same number of cells, 1 or more. May be empty.
        indent: The spaces before each line. 0 or more.
        gap: The spaces between two columns. 1 or more.
        min_widths: The smallest width of each column, from the left, in columns, before the
            gap. Each 0 or more. No more items than a row has cells. A column after the last
            item has no minimum.

    Returns:
        The lines of the table, without line ends, by these rules. (1) A cell's lines are
        ``cell.splitlines()``, or one empty line when that gives none. A row takes as many lines
        as its cell with the most lines, and a cell with fewer lines is empty in the later lines.
        (2) A column's width is the largest ``display_width`` of the lines in its cells, or its
        item of ``min_widths`` when that is larger. (3) Each line starts with ``indent`` spaces.
        Each column follows, left-aligned. A column other than the last is padded with spaces to
        its width and ``gap`` more spaces follow it. The last column is not padded, so its
        ``min_widths`` item has no effect. (4) Spaces (U+0020) at the end of each line are
        removed, so a line whose cells are all empty is the empty string. (5) The lines come in
        the order of the rows, and no rows give the empty tuple. (6) A cell is never cut or
        wrapped.

    Raises:
        TypeError: ``rows`` or one of its rows is a ``str``. This is checked before the other
            errors.
        ValueError: The rows do not all have the same number of cells, or the rows have no
            cells. Also when ``indent`` is less than 0, ``gap`` is less than 1, or an item of
            ``min_widths`` is less than 0 (checked with no rows too). Also when ``min_widths``
            has more items than a row has cells.
    """
    _check_args(rows, indent, gap, min_widths)
    if not rows:
        return ()
    lines = [line for row in rows for line in _row_lines(row)]
    widths = [0] * len(rows[0])
    for index in range(len(widths)):
        floor = min_widths[index] if index < len(min_widths) else 0
        widths[index] = max([floor, *(display_width(line[index]) for line in lines)])
    return tuple(_join_line(line, widths, indent, gap) for line in lines)
