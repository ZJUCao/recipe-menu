"""Tests of F05 for read_servings, MIN_SERVINGS, and MAX_SERVINGS (T50)."""

from fractions import Fraction
from pathlib import Path

import pytest

from f05_texts import EN, SERVINGS_NOT_A_NUMBER, ZH, Msg, servings_too_few, servings_too_many
from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS, Report, Severity, read_servings
from recipe_menu.lang import BiText

NOT = SERVINGS_NOT_A_NUMBER


@pytest.mark.usefixtures("default_int_limit")
def test_f05_t50_read_servings_gives_a_number_from_1_to_100_or_one_error() -> None:
    """The design's example, then the values of every kind in a report of another file."""
    report = Report(Path("settings.toml"))
    place = BiText("servings", "份数")
    assert read_servings(4, place, report) == 4
    assert read_servings(MIN_SERVINGS, place, report) == 1
    assert read_servings(MAX_SERVINGS, place, report) == 100
    assert report.problems == []
    assert read_servings(0, place, report) is None
    assert read_servings(True, place, report) is None
    assert read_servings(10**15, place, report) is None
    assert read_servings(101, place, report) is None
    assert [problem.text(EN) for problem in report.problems] == [
        "Servings must be a whole number of 1 or more, not 0.",
        "Servings must be a whole number from 1 to 100, such as 2.",
        "Servings must be a whole number from 1 to 100, such as 2.",
        "Servings must be a whole number of 100 or less, not 101.",
    ]
    assert report.problems[0].place == place
    assert (MIN_SERVINGS, MAX_SERVINGS) == (1, 100)
    _other_report()


def _other_report() -> None:
    """Reads values of every kind into a report of a menu file."""
    file = Path("menus", "2026-W47.toml")
    report = Report(file)
    place = BiText("Monday dinner, dish 2", "周一晚餐，第 2 道菜")
    assert read_servings(2, place, report) == 2
    assert read_servings(50, place, report) == 50
    assert report.problems == []
    rejected: list[tuple[object, Msg]] = [
        (MIN_SERVINGS - 1, servings_too_few(0)),
        (MAX_SERVINGS + 1, servings_too_many(101)),
        (-1, servings_too_few(-1)),
        (-999_999_999_999_999, servings_too_few(-999999999999999)),
        (999_999_999_999_999, servings_too_many(999999999999999)),
        (-(10**15), NOT),
        (int("f" * 5000, 16), NOT),
        (10**5000, NOT),
        (False, NOT),
        (2.5, NOT),
        (2.0, NOT),
        ("2", NOT),
        (None, NOT),
        ([2], NOT),
        (Fraction(2), NOT),
    ]
    for value, _ in rejected:
        assert read_servings(value, place, report) is None
    got = [(p.severity, str(p.file), p.place, p.text(EN), p.text(ZH)) for p in report.problems]
    want = [(Severity.ERROR, str(file), place, en, zh) for _, (en, zh) in rejected]
    assert got == want
