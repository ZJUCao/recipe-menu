"""The change of the menu file's text: the place of each empty meal, the new text, its check."""

import copy
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from recipe_menu.commands.suggest._choose import Fill
from recipe_menu.datafile import parse_toml
from recipe_menu.menus import Day, MealSlot
from recipe_menu.settings import Meal

type Places = dict[tuple[Day, Meal], Place]

# The pattern of any number of spaces and tabs.
_BLANK = "[ \\t]*"


class Where(Enum):
    """Where the dishes of an empty meal go in the text.

    Attributes:
        LINE: Into the empty line of the meal, in place of its ``[]``.
        HEADER: Into a new line right after the header of the day.
        END: Into a new table of the day at the end of the text.
    """

    LINE = auto()
    HEADER = auto()
    END = auto()


@dataclass(frozen=True, slots=True)
class Place:
    """The place of one empty meal in the text.

    Attributes:
        where: The kind of place.
        index: The index of the line: the meal's line for ``LINE``, the day's header for
            ``HEADER``, and 0 for ``END``.
    """

    where: Where
    index: int


def _key(word: str) -> str:
    """Writes the pattern of a day or a meal that may be bare or in quotation marks.

    Args:
        word: The value of a ``Day`` or a ``Meal``.

    Returns:
        The pattern, with no group of its own.
    """
    return f"(?:\"{word}\"|'{word}'|{word})"


def _is_header(line: str) -> bool:
    """Tells whether a line is a header: its first character that is no space or tab is ``[``.

    Args:
        line: The line.

    Returns:
        ``True`` for a header.
    """
    return line.lstrip(" \t").startswith("[")


def _find_header(lines: list[str], day: Day) -> int | None:
    """Finds the line that is the header of a day.

    Args:
        lines: The lines of the text.
        day: The day.

    Returns:
        The index of the first line like ``[monday]``, or ``None`` when there is none.
    """
    pattern = rf"{_BLANK}\[{_BLANK}{_key(day.value)}{_BLANK}\]{_BLANK}(?:#.*)?"
    return next((i for i, line in enumerate(lines) if re.fullmatch(pattern, line)), None)


def _table(lines: list[str], header: int) -> range:
    """Finds the lines of a day's table.

    Args:
        lines: The lines of the text.
        header: The index of the day's header.

    Returns:
        The indexes after the header, up to the next header or the end of the text.
    """
    end = next((i for i in range(header + 1, len(lines)) if _is_header(lines[i])), len(lines))
    return range(header + 1, end)


def _place(lines: list[str], slot: MealSlot) -> Place | None:
    """Finds the place of one empty meal.

    Args:
        lines: The lines of the text.
        slot: The empty meal.

    Returns:
        The place by the first row of the table of places that applies, or ``None`` when the
        meal has no place.
    """
    header = _find_header(lines, slot.day)
    if header is None:
        return Place(Where.END, 0)
    start = rf"{_BLANK}{_key(slot.meal.value)}{_BLANK}="
    found = [i for i in _table(lines, header) if re.match(start, lines[i])]
    if not found:
        return Place(Where.HEADER, header)
    empty = rf"{start}{_BLANK}\[{_BLANK}\]{_BLANK}(?:#.*)?"
    if len(found) == 1 and re.fullmatch(empty, lines[found[0]]):
        return Place(Where.LINE, found[0])
    return None


def find_places(text: str, empties: tuple[MealSlot, ...]) -> Places | None:
    """Finds the place of every empty meal in the text.

    Args:
        text: The text of the menu file, with LF line ends.
        empties: The empty meals.

    Returns:
        The place of each meal by its day and meal, or ``None`` when one has no place.
    """
    lines = text.split("\n")
    places: Places = {}
    for slot in empties:
        place = _place(lines, slot)
        if place is None:
            return None
        places[slot.day, slot.meal] = place
    return places


def _dish_list(ids: tuple[str, ...]) -> str:
    """Writes the list of the dishes of a meal.

    Args:
        ids: The recipe IDs.

    Returns:
        ``[``, the IDs each in double quotation marks and separated by a comma and a space, and
        ``]``.
    """
    return "[" + ", ".join(f'"{recipe_id}"' for recipe_id in ids) + "]"


def _fill_line(line: str, fill: Fill) -> str:
    """Puts the dishes into the empty line of a meal.

    Args:
        line: The line, such as ``dinner = []  # nothing yet``.
        fill: The dishes of the meal.

    Returns:
        The line with the dishes in place of its ``[]``, and the rest of the line as it was.
    """
    start = line.index("[")
    end = line.index("]", start) + 1
    return line[:start] + _dish_list(fill.ids) + line[end:]


def _edited_lines(lines: list[str], fills: list[Fill], places: Places) -> list[str]:
    """Changes the lines of the empty meals and adds the lines after the headers.

    Args:
        lines: The lines of the text.
        fills: The meals that get dishes.
        places: The place of each empty meal.

    Returns:
        The new lines.
    """
    changed = dict(enumerate(lines))
    added: dict[int, list[str]] = {}
    for fill in fills:
        place = places[fill.day, fill.meal]
        if place.where is Where.LINE:
            changed[place.index] = _fill_line(lines[place.index], fill)
        elif place.where is Where.HEADER:
            added.setdefault(place.index, []).append(f"{fill.meal.value} = {_dish_list(fill.ids)}")
    result: list[str] = []
    for index in range(len(lines)):
        result.append(changed[index])
        result.extend(added.get(index, ()))
    return result


def _new_tables(fills: list[Fill], places: Places) -> str:
    """Writes the tables of the days that the text lacks.

    Args:
        fills: The meals that get dishes.
        places: The place of each empty meal.

    Returns:
        For each such day in the order of the week, an empty line, the header, and a line for
        each meal that gets dishes, each line ended by LF.
    """
    out = ""
    for day in Day:
        mine = [f for f in fills if f.day is day and places[f.day, f.meal].where is Where.END]
        if mine:
            out += f"\n[{day.value}]\n"
            out += "".join(f"{f.meal.value} = {_dish_list(f.ids)}\n" for f in mine)
    return out


def new_text(text: str, fills: list[Fill], places: Places) -> str:
    """Builds the new text of the menu file.

    Args:
        text: The old text, with LF line ends.
        fills: The meals that get dishes, in the order of the week and of the settings' meals.
        places: The place of each empty meal.

    Returns:
        The text in which only the empty lines of the filled meals changed, a missing line of a
        meal follows its day's header, and a missing day's table is at the end.
    """
    body = "\n".join(_edited_lines(text.split("\n"), fills, places))
    tables = _new_tables(fills, places)
    if tables and body and not body.endswith("\n"):
        body += "\n"
    return body + tables


def _expected(table: dict[str, object], fills: list[Fill]) -> dict[str, Any]:
    """Makes the table that the new text must read as.

    Args:
        table: The table of the old text.
        fills: The meals that got dishes.

    Returns:
        A copy of the table in which each filled meal holds the list of its IDs, in a new table
        of its day when the old table lacks the day.
    """
    expected: dict[str, Any] = copy.deepcopy(table)
    for fill in fills:
        expected.setdefault(fill.day.value, {})[fill.meal.value] = list(fill.ids)
    return expected


def passes_check(old_text: str, new: str, fills: list[Fill]) -> bool:
    """Checks that the new text reads as the old table with the new dishes.

    Args:
        old_text: The old text, with LF line ends.
        new: The new text.
        fills: The meals that got dishes.

    Returns:
        ``True`` when both texts parse and the new table equals the old table in which each
        filled meal holds the list of its IDs, in a new table when the old table lacks the day.
    """
    old_table, new_table = parse_toml(old_text), parse_toml(new)
    return (
        old_table is not None and new_table is not None and new_table == _expected(old_table, fills)
    )
