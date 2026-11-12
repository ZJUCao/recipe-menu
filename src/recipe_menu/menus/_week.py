"""The ISO week, the dates of a week, and the week of a command-line argument."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from recipe_menu.lang import BiText


@dataclass(frozen=True, slots=True, order=True)
class IsoWeek:
    """One ISO week, such as ``2026-W47``, which runs from Monday to Sunday.

    It writes and reads the form of a file name, gives its seven dates, and gives the week of a
    date, so a caller finds this week from today's date. Two weeks are equal when their year and
    their week are equal. Weeks compare by year and then by week, so ``sorted`` gives the order
    of time, which is also the order of their ``str``. An ``IsoWeek`` is hashable.

    Attributes:
        year: The ISO year, from 1 to 9999. Near New Year, it can differ from the calendar year
            of a date in the week. Not a ``bool``.
        week: The week of the ISO year, from 1 to the number of weeks of ``year``, which is 53
            when 28 December of ``year`` falls in week 53, and 52 otherwise. Not a ``bool``.
            The week's Sunday is on or before 31 December 9999, so ``9999-W52`` is not a week.

    Raises:
        TypeError: ``year`` or ``week`` is not an ``int``, or it is a ``bool``.
        ValueError: ``year`` and ``week`` break the constraints above, such as
            ``IsoWeek(2025, 53)``, ``IsoWeek(2026, 0)``, or ``IsoWeek(9999, 52)``.

    The mock leaves these checks out.
    """

    year: int
    week: int

    @classmethod
    def of(cls, day: date) -> IsoWeek:
        """Gives the week that holds a date, as ``day.isocalendar()`` gives its year and week.

        The mock raises ``NotImplementedError``.

        Args:
            day: A date. Not from 27 to 31 December 9999, which fall in ``9999-W52``.

        Returns:
            The ``IsoWeek`` of ``day``. So 10 November 2026 is in ``2026-W46``, 1 January 2027
            is in ``2026-W53``, and 30 December 2024 is in ``2025-W01``.

        Raises:
            ValueError: ``day`` is from 27 to 31 December 9999.
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    @classmethod
    def parse(cls, text: str) -> IsoWeek | None:
        """Reads the written form of a week, in a file name, the key ``week``, or an argument.

        The mock raises ``NotImplementedError``.

        Args:
            text: A text to read, such as a file name without ``.toml``. Any string.

        Returns:
            The week whose ``str`` equals ``text``, or ``None`` when there is no such week. So
            ``text`` is four ASCII digits, ``-W``, and two ASCII digits, with nothing before or
            after them, and it names a week by the constraints of the fields. The implementation
            never raises for a ``str``.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    @property
    def dates(self) -> tuple[date, ...]:
        """Gives the seven dates of the week.

        The mock raises ``NotImplementedError``.

        Returns:
            The dates from Monday to Sunday, in the order of ``Day``.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    @property
    def date_range(self) -> BiText:
        """Writes the week's Monday and Sunday as one text in both languages.

        The mock raises ``NotImplementedError``.

        Returns:
            A ``BiText`` with both languages set. The template depends on the first of these
            cases that applies: Monday and Sunday are in one month, in two months of one year,
            or in two years. A day and a year are numbers with no leading zero. A month is its
            name in English and its number in Chinese. So ``2026-W47`` gives
            ``16 to 22 November 2026`` in English. The implementation never raises.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """Writes the week as the ISO year in four digits, ``-W``, and the week in two digits.

        The mock raises ``NotImplementedError``.

        Returns:
            The text, such as ``2026-W47``, ``2027-W01``, or ``0001-W01``. A file name, the key
            ``week``, and every message write a week this way.

        Raises:
            NotImplementedError: Always, in the mock.
        """
        raise NotImplementedError


def short_date(day: date) -> BiText:
    """Writes the date of one day as a short text in both languages.

    The mock raises ``NotImplementedError``.

    Args:
        day: The date to write.

    Returns:
        A ``BiText`` with both languages set. The English text is the short name of the weekday,
        the day, and the short name of the month, such as ``Mon 16 Nov``. The Chinese text is
        the day's label, the month number, and the day number, with the characters for month and
        day after their numbers. The implementation never raises.

    Raises:
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError


def week_from_argument(text: str | None, today: date) -> IsoWeek | None:
    """Turns the argument ``WEEK`` of a command into an ISO week.

    The mock raises ``NotImplementedError``.

    Args:
        text: The value of the argument as you typed it, or ``None`` when the command line
            gives none. Any string.
        today: Today's date, from ``Context.today``.

    Returns:
        The week by the first row of this list that applies. ``None`` or ``this`` gives
        ``IsoWeek.of(today)``. ``next`` gives ``IsoWeek.of(today + timedelta(days=7))``. A text
        that ``IsoWeek.parse`` reads gives that week. Any other text, such as ``2026-W99``,
        ``This``, ``2026-w47``, or the empty text, gives ``None``, and the caller raises
        ``UsageError(NOT_A_WEEK, None, week=text)``. The words are exact, in small letters.

    Raises:
        ValueError: ``IsoWeek.of`` gets a date from 27 to 31 December 9999.
        OverflowError: ``text`` is ``next``, and ``today`` is on or after 25 December 9999.
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError
