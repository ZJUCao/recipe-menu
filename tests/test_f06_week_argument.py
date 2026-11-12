"""Tests of F06 for week_from_argument and NOT_A_WEEK (T19 to T22)."""

from datetime import date

import pytest

from f06_support import TODAY, m_not_a_week
from recipe_menu.app import UsageError
from recipe_menu.lang import Lang
from recipe_menu.menus import NOT_A_WEEK, IsoWeek, week_from_argument

EN, ZH = Lang.EN, Lang.ZH

THIS_AND_NEXT = (
    *((date(2026, 11, day), (2026, 47), (2026, 48)) for day in range(16, 23)),
    (date(2026, 11, 10), (2026, 46), (2026, 47)),
    (date(2026, 12, 27), (2026, 52), (2026, 53)),
    (date(2026, 12, 28), (2026, 53), (2027, 1)),
    (date(2026, 12, 31), (2026, 53), (2027, 1)),
    (date(2027, 1, 1), (2026, 53), (2027, 1)),
    (date(2027, 1, 3), (2026, 53), (2027, 1)),
    (date(2024, 12, 23), (2024, 52), (2025, 1)),
    (date(2024, 12, 30), (2025, 1), (2025, 2)),
    (date(2020, 12, 25), (2020, 52), (2020, 53)),
    (date(2020, 12, 31), (2020, 53), (2021, 1)),
    (date(1, 1, 1), (1, 1), (1, 2)),
)
NOT_WEEKS = (
    "This",
    "THIS",
    "Next",
    "NEXT",
    " this",
    "this ",
    "next\n",
    "",
    " ",
    "last",
    "this week",
    "本周",
    "下周",
    "2026-W99",
    "2026-w47",
    "2026-W7",
    "2025-W53",
    "9999-W52",
    "W47",
    "47",
    "\uff12\uff10\uff12\uff16-W47",
)


def test_f06_t19_the_design_example_of_week_from_argument() -> None:
    """Every assertion of the design's example of 2.7 holds, and the last call raises."""
    today = date(2026, 11, 10)
    assert week_from_argument(None, today) == IsoWeek(2026, 46)
    assert week_from_argument("this", today) == IsoWeek(2026, 46)
    assert week_from_argument("next", today) == IsoWeek(2026, 47)
    assert week_from_argument("2026-W47", today) == IsoWeek(2026, 47)
    assert week_from_argument("2026-W53", today) == IsoWeek(2026, 53)
    assert week_from_argument("next", date(2026, 12, 30)) == IsoWeek(2027, 1)
    assert week_from_argument("2026-W99", today) is None
    assert week_from_argument("Next", today) is None
    assert week_from_argument("", today) is None

    error = UsageError(NOT_A_WEEK, None, week="2026-W99")
    assert error.text(Lang.EN) == (
        '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
    )
    chinese = error.text(Lang.ZH)
    assert chinese == "“2026-W99”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。"
    with pytest.raises(ValueError):
        week_from_argument("next", date(9999, 12, 20))


def test_f06_t20_none_this_and_next_follow_today_across_the_edges() -> None:
    """None and this give the week of today, next gives the week 7 days later."""
    for today, this, following in THIS_AND_NEXT:
        assert week_from_argument(None, today) == IsoWeek(*this), today
        assert week_from_argument("this", today) == IsoWeek(*this), today
        assert week_from_argument("next", today) == IsoWeek(*following), today
    for text, pair in (
        ("2026-W47", (2026, 47)),
        ("2026-W53", (2026, 53)),
        ("0001-W01", (1, 1)),
        ("9999-W51", (9999, 51)),
    ):
        for today in (TODAY, date(1, 1, 1)):
            assert week_from_argument(text, today) == IsoWeek(*pair), (text, today)


def test_f06_t21_every_other_text_gives_none_and_the_error_shows_it_as_typed() -> None:
    """The texts that are not weeks give None, also near the last date."""
    for text in NOT_WEEKS:
        assert week_from_argument(text, TODAY) is None, repr(text)
        assert week_from_argument(text, date(9999, 12, 31)) is None, repr(text)
        error = UsageError(NOT_A_WEEK, None, week=text)
        assert error.text(EN) == m_not_a_week(text)[0]
        assert error.text(ZH) == m_not_a_week(text)[1]
    empty = UsageError(NOT_A_WEEK, None, week="")
    assert empty.text(EN) == (
        '"" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
    )
    chinese = UsageError(NOT_A_WEEK, None, week="本周")
    assert (
        chinese.text(ZH) == "“本周”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。"
    )
    wrong = UsageError(NOT_A_WEEK, None, week="2026-W99")
    assert wrong.text(EN) == (
        '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
    )


def test_f06_t22_near_the_last_date_this_and_next_raise_and_other_texts_do_not() -> None:
    """None and this raise for 27 to 31 December 9999, and next raises two errors."""
    for text in (None, "this"):
        assert week_from_argument(text, date(9999, 12, 26)) == IsoWeek(9999, 51)
        for day in (date(9999, 12, 27), date(9999, 12, 31)):
            with pytest.raises(ValueError):
                week_from_argument(text, day)
    assert week_from_argument("next", date(9999, 12, 19)) == IsoWeek(9999, 51)
    for day in (date(9999, 12, 20), date(9999, 12, 24)):
        with pytest.raises(ValueError):
            week_from_argument("next", day)
    for day in (date(9999, 12, 25), date(9999, 12, 31)):
        with pytest.raises(OverflowError):
            week_from_argument("next", day)
    assert week_from_argument("2026-W47", date(9999, 12, 31)) == IsoWeek(2026, 47)
    assert week_from_argument("x", date(9999, 12, 31)) is None
