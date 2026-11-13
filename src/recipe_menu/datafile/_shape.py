"""The checks of the shape of a data file that the readers share."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from recipe_menu.datafile._problem import Problem
from recipe_menu.datafile.messages import (
    EMPTY_TEXT,
    MISSING_KEY,
    NOT_A_LIST,
    NOT_A_TABLE,
    NOT_A_TEXT,
    UNKNOWN_KEY,
)
from recipe_menu.lang import BiText
from recipe_menu.text import Message, MessageValue, and_list


class Report:
    """The problems that a reader has found so far, all of one file.

    Attributes:
        file: The file, relative to the data folder.
        problems: The problems, in the order they were found. ``add`` gives each one
            ``Severity.ERROR``, and ``warn`` gives each one ``Severity.WARNING``.
    """

    def __init__(self, file: Path) -> None:
        """Starts an empty report.

        Args:
            file: The file, relative to the data folder.
        """
        self.file = file
        self.problems: list[Problem] = []

    def add(self, place: BiText | None, message: Message, /, **values: MessageValue) -> None:
        """Adds an error.

        Args:
            place: The place in the file, or ``None`` for a problem of the whole file.
            message: What is wrong.
            **values: The value of each placeholder of ``message``.

        Raises:
            ValueError: ``file`` is an absolute path, the names of ``values`` are not exactly the
                placeholders of ``message``, or an ``int`` value has more than 4,300 digits.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
                or an ``enum.Enum`` member.
        """
        self.problems.append(Problem.error(self.file, place, message, **values))

    def warn(self, place: BiText | None, message: Message, /, **values: MessageValue) -> None:
        """Adds a warning.

        It appends ``Problem.warning(file, place, message, **values)`` to ``problems``, so the
        problem has ``Severity.WARNING``.

        Args:
            place: The place in the file, or ``None`` for a problem of the whole file.
            message: What is wrong.
            **values: The value of each placeholder of ``message``.

        Raises:
            ValueError: ``file`` is an absolute path, the names of ``values`` are not exactly the
                placeholders of ``message``, or an ``int`` value has more than 4,300 digits.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
                or an ``enum.Enum`` member.
        """
        self.problems.append(Problem.warning(self.file, place, message, **values))


def read_list(table: Mapping[str, object], key: str, place: BiText, report: Report) -> list[object]:
    """Reads a list at the top of a file.

    Args:
        table: The table of the file.
        key: The key of the list.
        place: The place of the list.
        report: Where the problems go.

    Returns:
        The list, or an empty list when the key is missing or its value is not a list. A missing
        key and a wrong value each add a problem.
    """
    if key not in table:
        report.add(None, MISSING_KEY, key=key)
        return []
    value = table[key]
    if not isinstance(value, list):
        report.add(place, NOT_A_LIST, key=key)
        return []
    return value


def read_table(item: object, place: BiText, report: Report) -> dict[str, object] | None:
    """Checks that an item of a list is a table.

    Args:
        item: The item.
        place: The place of the item.
        report: Where the problem goes.

    Returns:
        The item as a table, or ``None`` after a problem when it is not one.
    """
    if isinstance(item, dict):
        return item
    report.add(place, NOT_A_TABLE)
    return None


def read_text(table: Mapping[str, object], key: str, place: BiText, report: Report) -> str | None:
    """Reads a required text of a table.

    Args:
        table: The table.
        key: The key of the text.
        place: The place of the table.
        report: Where the problems go.

    Returns:
        The text without whitespace at both ends, or ``None`` after a problem when the key is
        missing, its value is not a text, or the text holds only whitespace.
    """
    if key not in table:
        report.add(place, MISSING_KEY, key=key)
        return None
    value = table[key]
    if not isinstance(value, str):
        report.add(place, NOT_A_TEXT, key=key)
        return None
    text = value.strip()
    if not text:
        report.add(place, EMPTY_TEXT, key=key)
        return None
    return text


def report_unknown_keys(
    table: Mapping[str, object],
    known: Sequence[str],
    place: BiText | None,
    report: Report,
) -> None:
    """Reports each key of a table that its kind does not have.

    Args:
        table: The table.
        known: The keys of its kind, in the order of the design.
        place: The place of the table, or ``None`` for the top of the file.
        report: Where the problems go.
    """
    unknown = [key for key in table if key not in known]
    if not unknown:
        return
    message = UNKNOWN_KEY.pick(len(known))
    keys = and_list(known)
    for key in unknown:
        report.add(place, message, key=key, keys=keys)
