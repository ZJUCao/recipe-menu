"""Display width and aligned tables."""

from collections.abc import Sequence


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

    Raises:
        NotImplementedError: In the mock.
    """
    raise NotImplementedError


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
        NotImplementedError: In the mock.
    """
    raise NotImplementedError
