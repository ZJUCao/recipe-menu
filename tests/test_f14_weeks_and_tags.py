"""Tests of F14 for the week, the tag, and a week with no menu file (T10, T11, T12)."""

from datetime import date
from pathlib import Path

from f05_support import make_home
from f07_changes import mapo_mistake
from f07_support import snapshot
from f09_support import made, no_tags, one_tag
from f09_texts import E_MAPO, err, out, stop
from f11_texts import no_menu, no_menu_zh, not_a_week, not_a_week_zh
from f13_support import E_LOWER_48, LISTINGS, READ_SETTINGS, empty_menu_file, pristine
from f14_support import (
    IN_ZH,
    LUNCH_DINNER,
    READ_CATALOG,
    W47,
    WEEK_48,
    FrontSource,
    filled,
    new_menu,
    suggest,
    traced,
    w47_filled,
    week_line,
    with_meals,
)
from f14_texts import (
    no_tags_text,
    no_tags_text_zh,
    one_tag_text,
    one_tag_text_zh,
    some,
    some_zh,
    tags,
    tags_zh,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.settings import Meal

BAD_WEEKS = [
    "2026-W99",
    "Next",
    "THIS",
    "",
    " 2026-W47",
    "2026-W47\n",
    "2026-w47",
    "2026-W7",
    "2025-W53",
    "2026-W00",
    "this week",
    "\uff12\uff10\uff12\uff16-W47",
]


def _check_this_and_next(home: Path, example: DataFolder) -> None:
    """Input 1: no week and ``this`` mean the week of today, and ``next`` the week after."""
    assert suggest(home, example, "menu", "suggest") == err(1, [no_menu("2026-W46")])
    assert suggest(home, example, "menu", "suggest", "this") == err(1, [no_menu("2026-W46")])
    result = suggest(home, example, "menu", "suggest", "next")
    assert result == out(some(W47, 1, 10, 4, "left"))


def _check_other_dates(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 2 and 3: the week of a given day, also at the end of a year of 53 weeks."""
    fresh = DataFolder(made(source, tmp_path, "t2"))
    result = suggest(home, fresh, "menu", "suggest", today=date(2026, 11, 17))
    assert result == out(some(W47, 1, 10, 4, "left"))
    wide = DataFolder(made(source, tmp_path, "t3", new_menu("2026-W53", LUNCH_DINNER)))
    today = date(2026, 12, 30)
    assert suggest(home, wide, "menu", "suggest", "next", today=today) == err(
        1, [no_menu("2027-W01")]
    )
    result = suggest(home, wide, "menu", "suggest", today=today)
    assert result == out(some("2026-W53", 7, 14, 0, "left"))


def _check_wrong_weeks(home: Path, example: DataFolder) -> None:
    """Input 4: each text that is not a week gives ``NOT_A_WEEK`` alone with exit code 2."""
    for value in BAD_WEEKS:
        result = suggest(home, example, "menu", "suggest", value)
        assert result == err(2, [not_a_week(value)]), repr(value)
    result = suggest(home, example, "menu", "suggest", "2026-W99", *IN_ZH)
    assert result == err(2, [not_a_week_zh("2026-W99")])
    assert suggest(home, example, "menu", "suggest", "Next", *IN_ZH) == err(
        2, [not_a_week_zh("Next")]
    )
    assert example.menu_file(W47).read_bytes() == w47_filled()


def test_f14_t10_the_week_is_this_week_next_week_or_an_iso_week(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five inputs: the default week, other days, texts that are not a week, and no disk."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_this_and_next(home, example_folder)
    _check_other_dates(home, source, tmp_path)
    _check_wrong_weeks(home, example_folder)
    watched = FrontSource()
    argv = week_line("2026-W99")
    result, calls, listings = traced(home, example_folder.root, [], *argv, random=watched)
    assert result == err(2, [not_a_week("2026-W99")])
    assert calls == [READ_SETTINGS]
    assert listings == []
    assert watched.calls == []


def _check_tag_names(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Input 1: a tag by either name, with white space at its ends, in a week of dinners."""
    root = DataFolder(made(source, tmp_path, "t1", with_meals(Meal.DINNER)))
    expected = filled(
        WEEK_48, [Meal.DINNER], [["choy-sum"], ["tomato-egg"], ["tomato-egg-noodles"]]
    )
    values = ["quick", "QUICK", "Quick", " quick ", "\u00a0quick\u3000", "快手 ", "\t快手"]
    for value in values:
        new_menu(WEEK_48, [Meal.DINNER])(root.root)
        result = suggest(home, root, *week_line(WEEK_48, "--tag", value))
        assert result == out(some(WEEK_48, 3, 7, 0, "left", "quick")), repr(value)
        assert root.menu_file(WEEK_48).read_bytes() == expected, repr(value)
    for value in ("快手", "quick"):
        new_menu(WEEK_48, [Meal.DINNER])(root.root)
        result = suggest(home, root, *week_line(WEEK_48, "--tag", value, *IN_ZH))
        assert result == out(some_zh(WEEK_48, 3, 7, 0, "left", "快手")), value


def _check_unknown_tags(home: Path, example: DataFolder) -> None:
    """Input 2: an unknown tag in the five-tag catalog, with the value as it was typed."""
    for value, lang, text in (
        ("breakfast", (), tags("breakfast")),
        ("breakfast", IN_ZH, tags_zh("breakfast")),
        (" Breakfast ", (), tags(" Breakfast ")),
        ("quick\u200b", (), tags("quick\u200b")),
        ("home style", (), tags("home style")),
    ):
        result = suggest(home, example, *week_line(W47, "--tag", value, *lang))
        assert result == err(1, [text]), repr(value)


def _check_few_tags(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 3 and 4: the forms for one tag and for no tags."""
    one = DataFolder(made(source, tmp_path, "t3", one_tag))
    before = snapshot(one.root)
    result = suggest(home, one, *week_line(W47, "--tag", "breakfast"))
    assert result == err(1, [one_tag_text("breakfast")])
    result = suggest(home, one, *week_line(W47, "--tag", "breakfast", *IN_ZH))
    assert result == err(1, [one_tag_text_zh("breakfast")])
    none = DataFolder(made(source, tmp_path, "t4", no_tags))
    none_before = snapshot(none.root)
    assert suggest(home, none, *week_line(W47, "--tag", "quick")) == err(1, [no_tags_text("quick")])
    result = suggest(home, none, *week_line(W47, "--tag", "quick", *IN_ZH))
    assert result == err(1, [no_tags_text_zh("quick")])
    assert snapshot(one.root) == before
    assert snapshot(none.root) == none_before


def _check_no_candidate_and_mistake(
    home: Path, example: DataFolder, source: DataFolder, tmp_path: Path
) -> None:
    """Inputs 5 to 7: the record of an unknown tag, a tag no candidate has, and a mistake."""
    watched = FrontSource()
    argv = week_line(W47, "--tag", "breakfast")
    result, calls, listings = traced(home, example.root, [], *argv, random=watched)
    assert result == err(1, [tags("breakfast")])
    assert calls == [READ_SETTINGS, READ_CATALOG]
    assert listings == []
    assert watched.calls == []
    vegetarian = FrontSource()
    result = suggest(home, example, *week_line(W47, "--tag", "vegetarian"), random=vegetarian)
    assert result == out(some(W47, 0, 10, 4, "left", "vegetarian"))
    assert vegetarian.calls == [([], 0)]
    changes = (mapo_mistake, new_menu(WEEK_48, LUNCH_DINNER))
    broken = DataFolder(made(source, tmp_path, "t7", *changes))
    before = snapshot(broken.root)
    result = suggest(home, broken, *week_line(WEEK_48, "--tag", "quick"))
    assert result == stop(E_MAPO)
    assert snapshot(broken.root) == before


def test_f14_t11_the_tag_is_found_by_either_name_and_an_unknown_one_stops_the_run(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven inputs: names of a tag, unknown tags, one tag and none, the record, and a mistake."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_tag_names(home, source, tmp_path)
    before = snapshot(example_folder.root)
    _check_unknown_tags(home, example_folder)
    assert snapshot(example_folder.root) == before
    _check_few_tags(home, source, tmp_path)
    _check_no_candidate_and_mistake(home, example_folder, source, tmp_path)
    assert snapshot(example_folder.root) == before


def test_f14_t12_a_week_with_no_menu_file_stops_after_the_two_listings(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``NO_MENU`` before any menu or recipe is read, and a file of the wrong case."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    assert suggest(home, example_folder, *week_line(WEEK_48)) == err(1, [no_menu(WEEK_48)])
    result = suggest(home, example_folder, *week_line(WEEK_48, *IN_ZH))
    assert result == err(1, [no_menu_zh(WEEK_48)])
    assert [path.name for path in example_folder.menus.iterdir()] == ["2026-W47.toml"]
    mapo = made(source, tmp_path, "f", mapo_mistake)
    watched = FrontSource()
    result, calls, listings = traced(home, mapo, [], *week_line(WEEK_48), random=watched)
    assert result == err(1, [no_menu(WEEK_48)])
    assert calls == [READ_SETTINGS, READ_CATALOG]
    assert listings == LISTINGS
    assert watched.calls == []
    lower = made(source, tmp_path, "lower", empty_menu_file("2026-w48.toml"))
    assert suggest(home, lower, *week_line(WEEK_48)) == stop(E_LOWER_48)
    assert suggest(home, lower, *week_line(W47)) == stop(E_LOWER_48)
