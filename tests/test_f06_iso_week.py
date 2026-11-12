"""Tests of F06 for IsoWeek, IsoWeek.of, IsoWeek.parse, and IsoWeek.dates (T01 to T08)."""

import random
from datetime import date, timedelta

import pytest

from recipe_menu.menus import IsoWeek

WEEKS = (
    "0001-W01",
    "0999-W52",
    "2020-W53",
    "2025-W52",
    "2026-W01",
    "2026-W47",
    "2026-W53",
    "9999-W51",
)
NOT_WEEKS = (
    "2025-W53",
    "2024-W53",
    "2026-W54",
    "2026-W99",
    "2026-W00",
    "0000-W01",
    "9999-W52",
    "9999-W53",
    "10000-W01",
    "2026-w47",
    "2026-W7",
    "2026-W047",
    "02026-W47",
    "26-W47",
    "2026W47",
    "2026-47",
    "2026_W47",
    "2026\u2013W47",
    "2026-W47-2",
    "2026-W47.toml",
    " 2026-W47",
    "2026-W47 ",
    "2026-W47\n",
    "\ufeff2026-W47",
    "2026-W47\x00",
    "+026-W47",
    "-026-W47",
    "2026-W+7",
    "2026-W 7",
    "2026-W-1",
    "\uff12\uff10\uff12\uff16-W47",
    "2026-W\uff14\uff17",
    "2026-\uff3747",
    "\u0662\u0660\u0662\u0666-W47",
    "2026-W4\u00b2",
    "",
    "W47",
    "this",
    "next",
)
OF_CASES = (
    (date(2026, 11, 10), (2026, 46)),
    (date(2026, 11, 16), (2026, 47)),
    (date(2026, 11, 22), (2026, 47)),
    (date(2026, 11, 23), (2026, 48)),
    (date(2026, 12, 27), (2026, 52)),
    (date(2026, 12, 28), (2026, 53)),
    (date(2026, 12, 31), (2026, 53)),
    (date(2027, 1, 1), (2026, 53)),
    (date(2027, 1, 3), (2026, 53)),
    (date(2027, 1, 4), (2027, 1)),
    (date(2025, 12, 28), (2025, 52)),
    (date(2025, 12, 29), (2026, 1)),
    (date(2026, 1, 1), (2026, 1)),
    (date(2024, 12, 29), (2024, 52)),
    (date(2024, 12, 30), (2025, 1)),
    (date(2020, 12, 31), (2020, 53)),
    (date(2021, 1, 1), (2020, 53)),
    (date(2022, 1, 1), (2021, 52)),
    (date(2023, 1, 1), (2022, 52)),
    (date(2024, 2, 29), (2024, 9)),
    (date(1, 1, 1), (1, 1)),
    (date(1, 1, 8), (1, 2)),
    (date(9999, 12, 20), (9999, 51)),
    (date(9999, 12, 26), (9999, 51)),
)
DATES_CASES = (
    ((2026, 47), date(2026, 11, 16)),
    ((2026, 53), date(2026, 12, 28)),
    ((2026, 1), date(2025, 12, 29)),
    ((2025, 1), date(2024, 12, 30)),
    ((2024, 9), date(2024, 2, 26)),
    ((1, 1), date(1, 1, 1)),
    ((9999, 51), date(9999, 12, 20)),
)


def test_f06_t01_the_design_example_of_iso_week() -> None:
    """Every assertion of the design's example of 2.1 holds, and its five calls raise."""
    week = IsoWeek(2026, 47)
    assert str(week) == "2026-W47"
    assert IsoWeek.parse("2026-W47") == week
    assert str(IsoWeek(2027, 1)) == "2027-W01"
    assert IsoWeek.parse("0001-W01") == IsoWeek(1, 1)
    assert IsoWeek.of(date(2026, 11, 10)) == IsoWeek(2026, 46)
    assert IsoWeek.of(date(2027, 1, 1)) == IsoWeek(2026, 53)
    assert IsoWeek.of(date(2024, 12, 30)) == IsoWeek(2025, 1)
    assert week.dates == tuple(date(2026, 11, day) for day in range(16, 23))
    assert IsoWeek(2026, 53).dates[-1] == date(2027, 1, 3)
    assert IsoWeek.parse("2026-W53") == IsoWeek(2026, 53)
    assert IsoWeek(2026, 53) < IsoWeek(2027, 1)
    wrong = ["2025-W53", "2026-W99", "2026-W00", "2026-w47", "2026-W7", " 2026-W47", "2026-W47\n"]
    assert [IsoWeek.parse(text) for text in wrong] == [None] * 7
    fullwidth = "".join(chr(0xFF10 + int(digit)) for digit in "2026")
    assert IsoWeek.parse(fullwidth + "-W47") is None

    with pytest.raises(ValueError):
        IsoWeek(2025, 53)
    with pytest.raises(ValueError):
        IsoWeek(2026, 0)
    with pytest.raises(ValueError):
        IsoWeek(9999, 52)
    with pytest.raises(TypeError):
        IsoWeek(2026, True)
    with pytest.raises(ValueError):
        IsoWeek.of(date(9999, 12, 31))


def test_f06_t02_the_constructor_accepts_the_weeks_of_a_year_and_nothing_else() -> None:
    """A year from 1 to 9999 and a week of that year are kept, and every other value raises."""
    accepted = (
        ((1, 1), "0001-W01"),
        ((1, 52), "0001-W52"),
        ((999, 52), "0999-W52"),
        ((2020, 53), "2020-W53"),
        ((2025, 52), "2025-W52"),
        ((2026, 1), "2026-W01"),
        ((2026, 53), "2026-W53"),
        ((9999, 1), "9999-W01"),
        ((9999, 51), "9999-W51"),
    )
    for (year, number), text in accepted:
        week = IsoWeek(year, number)
        assert str(week) == text
        assert (week.year, week.week) == (year, number)
    value_errors = (
        (0, 1),
        (-1, 1),
        (10000, 1),
        (2026, 0),
        (2026, -1),
        (2026, 54),
        (2025, 53),
        (2024, 53),
        (9999, 52),
        (9999, 53),
    )
    for pair in value_errors:
        with pytest.raises(ValueError):
            IsoWeek(*pair)
    type_errors = (
        ("2026", 47),
        (2026, "47"),
        (2026.0, 47),
        (2026, 47.0),
        (None, 1),
        (2026, None),
        (True, 1),
        (2026, True),
        (2026, False),
    )
    for pair in type_errors:
        with pytest.raises(TypeError):
            IsoWeek(*pair)


def test_f06_t03_parse_reads_exactly_the_text_that_str_writes() -> None:
    """Eight weeks read back, and every other text gives None and raises nothing."""
    for text in WEEKS:
        week = IsoWeek.parse(text)
        assert week == IsoWeek(int(text[:4]), int(text[6:])), text
        assert str(week) == text
    for text in NOT_WEEKS:
        assert IsoWeek.parse(text) is None, repr(text)


def test_f06_t04_of_gives_the_week_that_holds_the_date() -> None:
    """The week agrees with the table across the edges of a week and a year."""
    for day, (year, number) in OF_CASES:
        week = IsoWeek.of(day)
        assert week == IsoWeek(year, number), day
        assert str(week) == f"{year:04d}-W{number:02d}", day
    for day in (date(9999, 12, 27), date(9999, 12, 28), date.max):
        with pytest.raises(ValueError):
            IsoWeek.of(day)


def test_f06_t05_dates_give_the_seven_days_from_monday() -> None:
    """The dates cross a month, a year, a leap day, and the limits of date."""
    for (year, number), first in DATES_CASES:
        week = IsoWeek(year, number)
        dates = week.dates
        assert isinstance(dates, tuple)
        assert dates == tuple(first + timedelta(days=i) for i in range(7)), week
        assert all(type(item) is date for item in dates)
        assert first.weekday() == 0
        assert all(IsoWeek.of(item) == week for item in dates), week
    assert IsoWeek(2024, 9).dates[3] == date(2024, 2, 29)


def test_f06_t06_weeks_sort_in_the_order_of_time_and_of_their_text() -> None:
    """Sorting by year and week equals sorting the texts, and equal weeks are one key."""
    texts = [
        "2027-W01",
        "2026-W10",
        "0999-W52",
        "2026-W53",
        "1000-W01",
        "2026-W09",
        "9999-W51",
        "0001-W01",
        "2026-W47",
    ]
    weeks = [IsoWeek.parse(text) for text in texts]
    assert [str(week) for week in sorted(weeks)] == [
        "0001-W01",
        "0999-W52",
        "1000-W01",
        "2026-W09",
        "2026-W10",
        "2026-W47",
        "2026-W53",
        "2027-W01",
        "9999-W51",
    ]
    assert [str(week) for week in sorted(weeks)] == sorted(texts)
    assert IsoWeek(2026, 53) < IsoWeek(2027, 1)
    assert IsoWeek(2026, 9) < IsoWeek(2026, 10)
    assert IsoWeek(999, 52) < IsoWeek(1000, 1)
    same = {IsoWeek.parse("2026-W47"), IsoWeek(2026, 47), IsoWeek.of(date(2026, 11, 16))}
    assert len(same) == 1
    assert {IsoWeek(2026, 47): "x"}[IsoWeek.parse("2026-W47")] == "x"


def test_f06_t07_a_year_has_53_weeks_when_28_december_is_in_week_53() -> None:
    """Every year from 1 to 9999 has week 53 exactly when 28 December falls in it."""
    with_53 = []
    for year in range(1, 10000):
        parsed = IsoWeek.parse(f"{year:04d}-W53")
        has_53 = date(year, 12, 28).isocalendar().week == 53
        assert (parsed == IsoWeek(year, 53)) if has_53 else (parsed is None), year
        if has_53:
            with_53.append(year)
        else:
            with pytest.raises(ValueError):
                IsoWeek(year, 53)
        last = IsoWeek.parse(f"{year:04d}-W52")
        assert (last is None) if year == 9999 else (last == IsoWeek(year, 52)), year
    assert len(with_53) == 1775
    assert [year for year in with_53 if 2000 <= year <= 2040] == [
        2004,
        2009,
        2015,
        2020,
        2026,
        2032,
        2037,
    ]
    assert 9999 not in with_53


def test_f06_t08_of_agrees_with_isocalendar_for_many_dates() -> None:
    """For every date of 2000 to 2040 and 2,000 random dates, the week and its text agree."""
    rng = random.Random(20261114)  # noqa: S311
    last = date(9999, 12, 26).toordinal()
    start, stop = date(2000, 1, 1).toordinal(), date(2040, 12, 31).toordinal()
    days = [date.fromordinal(n) for n in range(start, stop + 1)]
    days += [date.fromordinal(rng.randint(1, last)) for _ in range(2000)]
    for day in days:
        week = IsoWeek.of(day)
        calendar = day.isocalendar()
        assert week == IsoWeek(calendar.year, calendar.week), day
        assert week.dates[day.weekday()] == day, day
        assert str(week) == f"{week.year:04d}-W{week.week:02d}", day
        assert IsoWeek.parse(str(week)) == week, day
