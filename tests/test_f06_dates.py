"""Tests of F06 for IsoWeek.date_range and short_date (T09 to T13)."""

from datetime import date, timedelta

from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import IsoWeek, short_date

ONE_MONTH = (
    (2, "5 to 11 January 2026", "2026年1月5日至11日"),
    (6, "2 to 8 February 2026", "2026年2月2日至8日"),
    (10, "2 to 8 March 2026", "2026年3月2日至8日"),
    (15, "6 to 12 April 2026", "2026年4月6日至12日"),
    (19, "4 to 10 May 2026", "2026年5月4日至10日"),
    (23, "1 to 7 June 2026", "2026年6月1日至7日"),
    (28, "6 to 12 July 2026", "2026年7月6日至12日"),
    (32, "3 to 9 August 2026", "2026年8月3日至9日"),
    (37, "7 to 13 September 2026", "2026年9月7日至13日"),
    (41, "5 to 11 October 2026", "2026年10月5日至11日"),
    (45, "2 to 8 November 2026", "2026年11月2日至8日"),
    (50, "7 to 13 December 2026", "2026年12月7日至13日"),
)
TWO_MONTHS = (
    (2026, 5, "26 January to 1 February 2026", "2026年1月26日至2月1日"),
    (2026, 9, "23 February to 1 March 2026", "2026年2月23日至3月1日"),
    (2026, 14, "30 March to 5 April 2026", "2026年3月30日至4月5日"),
    (2026, 18, "27 April to 3 May 2026", "2026年4月27日至5月3日"),
    (2026, 27, "29 June to 5 July 2026", "2026年6月29日至7月5日"),
    (2026, 31, "27 July to 2 August 2026", "2026年7月27日至8月2日"),
    (2026, 36, "31 August to 6 September 2026", "2026年8月31日至9月6日"),
    (2026, 40, "28 September to 4 October 2026", "2026年9月28日至10月4日"),
    (2026, 44, "26 October to 1 November 2026", "2026年10月26日至11月1日"),
    (2026, 49, "30 November to 6 December 2026", "2026年11月30日至12月6日"),
    (2025, 22, "26 May to 1 June 2025", "2025年5月26日至6月1日"),
)
EDGES = (
    (2026, 53, "28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日"),
    (2026, 1, "29 December 2025 to 4 January 2026", "2025年12月29日至2026年1月4日"),
    (2025, 1, "30 December 2024 to 5 January 2025", "2024年12月30日至2025年1月5日"),
    (2020, 53, "28 December 2020 to 3 January 2021", "2020年12月28日至2021年1月3日"),
    (2024, 1, "1 to 7 January 2024", "2024年1月1日至7日"),
    (2023, 52, "25 to 31 December 2023", "2023年12月25日至31日"),
    (2024, 9, "26 February to 3 March 2024", "2024年2月26日至3月3日"),
    (1, 1, "1 to 7 January 1", "1年1月1日至7日"),
    (9999, 51, "20 to 26 December 9999", "9999年12月20日至26日"),
)
WEEK_47 = (
    (date(2026, 11, 16), "Mon 16 Nov", "周一 11月16日"),
    (date(2026, 11, 17), "Tue 17 Nov", "周二 11月17日"),
    (date(2026, 11, 18), "Wed 18 Nov", "周三 11月18日"),
    (date(2026, 11, 19), "Thu 19 Nov", "周四 11月19日"),
    (date(2026, 11, 20), "Fri 20 Nov", "周五 11月20日"),
    (date(2026, 11, 21), "Sat 21 Nov", "周六 11月21日"),
    (date(2026, 11, 22), "Sun 22 Nov", "周日 11月22日"),
)
FIRST_DAYS = (
    (date(2026, 1, 1), "Thu 1 Jan", "周四 1月1日"),
    (date(2026, 2, 1), "Sun 1 Feb", "周日 2月1日"),
    (date(2026, 3, 1), "Sun 1 Mar", "周日 3月1日"),
    (date(2026, 4, 1), "Wed 1 Apr", "周三 4月1日"),
    (date(2026, 5, 1), "Fri 1 May", "周五 5月1日"),
    (date(2026, 6, 1), "Mon 1 Jun", "周一 6月1日"),
    (date(2026, 7, 1), "Wed 1 Jul", "周三 7月1日"),
    (date(2026, 8, 1), "Sat 1 Aug", "周六 8月1日"),
    (date(2026, 9, 1), "Tue 1 Sep", "周二 9月1日"),
    (date(2026, 10, 1), "Thu 1 Oct", "周四 10月1日"),
    (date(2026, 11, 1), "Sun 1 Nov", "周日 11月1日"),
    (date(2026, 12, 1), "Tue 1 Dec", "周二 12月1日"),
)
OTHER_DAYS = (
    (date(1, 1, 1), "Mon 1 Jan", "周一 1月1日"),
    (date(2024, 2, 29), "Thu 29 Feb", "周四 2月29日"),
    (date(9999, 12, 26), "Sun 26 Dec", "周日 12月26日"),
    (date(9999, 12, 27), "Mon 27 Dec", "周一 12月27日"),
    (date(9999, 12, 31), "Fri 31 Dec", "周五 12月31日"),
)
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
SHORT_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
SHORT_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
ZH_DAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


def check_text(got: BiText, en: str, zh: str, label: object = "") -> None:
    """Checks that a text has both languages and that they are the expected texts."""
    assert isinstance(got, BiText), label
    assert got.get(Lang.EN) == en, label
    assert got.get(Lang.ZH) == zh, label
    assert got == BiText(en, zh), label


def test_f06_t09_the_design_example_of_date_range_and_short_date() -> None:
    """Every assertion of the design's example of 2.2 holds."""
    november = BiText("16 to 22 November 2026", "2026年11月16日至22日")
    assert IsoWeek(2026, 47).date_range == november
    december = BiText("30 November to 6 December 2026", "2026年11月30日至12月6日")
    assert IsoWeek(2026, 49).date_range == december
    new_year = BiText("28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日")
    assert IsoWeek(2026, 53).date_range == new_year
    assert short_date(date(2026, 11, 16)) == BiText("Mon 16 Nov", "周一 11月16日")
    assert short_date(date(2026, 11, 22)) == BiText("Sun 22 Nov", "周日 11月22日")
    assert short_date(date(2026, 12, 1)) == BiText("Tue 1 Dec", "周二 12月1日")


def test_f06_t10_a_week_in_one_month_or_two_months_names_each_month() -> None:
    """The first two rows give each month's English name and its number in Chinese."""
    for number, en, zh in ONE_MONTH:
        check_text(IsoWeek(2026, number).date_range, en, zh, number)
    for year, number, en, zh in TWO_MONTHS:
        check_text(IsoWeek(year, number).date_range, en, zh, (year, number))


def test_f06_t11_a_week_around_new_year_stays_in_one_year_or_names_both() -> None:
    """The third row holds the weeks around New Year, with no leading zero in a day or a year."""
    for year, number, en, zh in EDGES:
        check_text(IsoWeek(year, number).date_range, en, zh, (year, number))


def test_f06_t12_short_date_writes_the_weekday_the_day_and_the_month() -> None:
    """The short date has both languages, for every month and every short day name."""
    for day, en, zh in (*WEEK_47, *FIRST_DAYS, *OTHER_DAYS):
        check_text(short_date(day), en, zh, day)


def _expected_range(monday: date) -> tuple[str, str]:
    """Builds the expected ``date_range`` texts of the week that starts on a Monday.

    The test holds the tables of the design as literals and applies the first row that fits.
    """
    sunday = monday + timedelta(days=6)
    first, last = monday.day, sunday.day
    if monday.year != sunday.year:
        en = (
            f"{first} {MONTHS[monday.month - 1]} {monday.year} to "
            f"{last} {MONTHS[sunday.month - 1]} {sunday.year}"
        )
        zh = f"{monday.year}年{monday.month}月{first}日至{sunday.year}年{sunday.month}月{last}日"
    elif monday.month != sunday.month:
        en = (
            f"{first} {MONTHS[monday.month - 1]} to {last} {MONTHS[sunday.month - 1]} {monday.year}"
        )
        zh = f"{monday.year}年{monday.month}月{first}日至{sunday.month}月{last}日"
    else:
        en = f"{first} to {last} {MONTHS[monday.month - 1]} {monday.year}"
        zh = f"{monday.year}年{monday.month}月{first}日至{last}日"
    return en, zh


def test_f06_t13_every_week_of_2000_to_2040_follows_the_templates() -> None:
    """``date_range`` and ``short_date`` equal the texts that the tables of 2.2 and 2.3 build."""
    monday = date(2000, 1, 3)
    while monday <= date(2040, 12, 31):
        week = IsoWeek.of(monday)
        en, zh = _expected_range(monday)
        check_text(week.date_range, en, zh, str(week))
        for index, day in enumerate(week.dates):
            weekday = f"{SHORT_DAYS[index]} {day.day} {SHORT_MONTHS[day.month - 1]}"
            chinese = f"{ZH_DAYS[index]} {day.month}月{day.day}日"
            check_text(short_date(day), weekday, chinese, day)
        monday += timedelta(days=7)
