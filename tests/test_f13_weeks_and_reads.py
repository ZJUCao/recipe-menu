"""Tests of F13 for the week of shop and for the files that it reads and writes (T15, T16)."""

from datetime import date
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f05_texts import Result
from f07_changes import catalog_brace, mapo_mistake, pantry_sesame, the_typo
from f07_texts import TYPO
from f08_support import full_record
from f09_support import at, made, rice_bowl
from f09_texts import E_BRACE, E_MAPO, E_RICE_BOWL, err, out, stop
from f10_support import chinese_settings
from f11_support import on, week_b
from f11_texts import no_menu, no_menu_zh, not_a_week, not_a_week_zh
from f13_blocks import DATES, block_b, block_h, block_h_zh, file_h, file_h_zh
from f13_support import (
    E_LOWER_48,
    E_PANTRY,
    LISTINGS,
    R47,
    READ_SETTINGS,
    W47,
    empty_menu_file,
    old_list,
    pristine,
    rice_week,
    shopping_as_file,
    traced,
)
from f13_texts import FILE_47, PROTOTYPE_FILE, shop_47, shop_47_zh
from recipe_menu.datafile import DataFolder

RICE_WEEKS = ["2026-W01", "2026-W23", "2026-W49", "2026-W53", "2027-W01"]
# The dates of F13-T15 input 2, with the week of the date and the week 7 days later.
DAYS = [
    (date(2026, 11, 10), "2026-W46", "2026-W47"),
    (date(2026, 11, 22), "2026-W47", "2026-W48"),
    (date(2026, 12, 27), "2026-W52", "2026-W53"),
    (date(2026, 12, 30), "2026-W53", "2027-W01"),
    (date(2027, 1, 3), "2026-W53", "2027-W01"),
    (date(2025, 12, 29), "2026-W01", "2026-W02"),
]
BAD_WEEKS = ["2026-W99", "Next", "", "2026-w47", "2025-W53", " this"]


def _expected(root: Path, week: str, zh: bool) -> Result:
    """Gives the result of ``shop`` for a week in the folder of input 2 of F13-T15."""
    file = DataFolder(root).shopping_file(week)
    if week == "2026-W47":
        return out(shop_47_zh(file) if zh else shop_47(file))
    if week in RICE_WEEKS:
        en_dates, zh_dates = DATES[week]
        return out(block_h_zh(week, zh_dates, file) if zh else block_h(week, en_dates, file))
    return err(1, [no_menu_zh(week) if zh else no_menu(week)])


def _check_rice_weeks(home: Path, root: Path) -> None:
    """Input 1 of F13-T15: each rice week, in both languages, with its dates and its file."""
    file_of = DataFolder(root).shopping_file
    for week in RICE_WEEKS:
        en_dates, zh_dates = DATES[week]
        assert at(home, root, "shop", week) == out(block_h(week, en_dates, file_of(week))), week
        assert file_of(week).read_bytes() == file_h(week, en_dates), week
        zh = at(home, root, "shop", week, "--lang", "zh")
        assert zh == out(block_h_zh(week, zh_dates, file_of(week))), week
        assert file_of(week).read_bytes() == file_h_zh(week, zh_dates), week


def _check_days(home: Path, root: Path) -> None:
    """Input 2 of F13-T15: ``shop``, ``shop this``, and ``shop next`` on six dates."""
    for today, this, following in DAYS:
        for argv in (("shop",), ("shop", "this")):
            assert on(home, root, today, *argv) == _expected(root, this, False), (today, argv)
        shown = on(home, root, today, "shop", "next", "--lang", "zh")
        assert shown == _expected(root, following, True), today


def test_f13_t15_shop_takes_its_week_from_the_argument_and_the_date_of_today(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Rice weeks, ``this`` and ``next`` across years, and values that are not a week."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    changes = [rice_week(week) for week in RICE_WEEKS]
    root = made(source, tmp_path, "rice", *changes)
    _check_rice_weeks(home, root)
    _check_days(home, root)
    old_list(example_folder.root)
    for value in BAD_WEEKS:
        before = full_record(example_folder.root)
        result, calls, listings = traced(home, example_folder.root, "shop", value)
        assert result == err(2, [not_a_week(value)]), value
        assert (calls, listings) == ([READ_SETTINGS], []), value
        assert full_record(example_folder.root) == before, value
    for value in ("2026-W99", "Next"):
        shown = at(home, example_folder, "shop", value, "--lang", "zh")
        assert shown == err(2, [not_a_week_zh(value)]), value
    for change, value in ((catalog_brace, "2026-W99"), (pantry_sesame, "Next")):
        folder = made(source, tmp_path, f"wrong-{value}", change)
        assert at(home, folder, "shop", value) == err(2, [not_a_week(value)]), value
    folder = made(source, tmp_path, "as-file", shopping_as_file)
    assert at(home, folder, "shop", "") == err(2, [not_a_week("")])
    assert (folder / "shopping").read_bytes() == b"x\n"
    zh = made(source, tmp_path, "zh", chinese_settings)
    assert at(home, zh, "shop", "2026-W99") == err(2, [not_a_week_zh("2026-W99")])
    assert at(home, zh, "shop", "2026-W99", "--lang", "en") == err(2, [not_a_week("2026-W99")])


def _check_example_reads(home: Path, example: DataFolder) -> None:
    """Input 1 of F13-T16: ``shop 2026-W47`` in English and then in Chinese."""
    file = example.shopping_file("2026-W47")
    result, calls, listings = traced(home, example.root, "shop", "2026-W47")
    assert result == out(shop_47(file))
    assert calls == [*R47, "mkdir shopping", *W47]
    assert listings == LISTINGS
    result, calls, listings = traced(home, example.root, "shop", "2026-W47", "--lang", "zh")
    assert result == out(shop_47_zh(file))
    assert (calls, listings) == ([*R47, *W47], LISTINGS)
    assert file.read_bytes() == PROTOTYPE_FILE


def _check_week_b_reads(
    home: Path, example: DataFolder, source: DataFolder, tmp_path: Path
) -> None:
    """Inputs 2 and 3 of F13-T16: week B, and a week that has no menu."""
    root = made(source, tmp_path, "b", week_b)
    file = root / "shopping" / "2026-W48.md"
    result, calls, listings = traced(home, root, "shop", "2026-W48")
    assert result == out(block_b(file))
    reads = [READ_SETTINGS, "read catalog.toml", "read pantry.toml", "read menus/2026-W48.toml"]
    reads += [f"read recipes/{name}.toml" for name in ("mapo-tofu", "rice", "choy-sum")]
    reads += ["read recipes/red-braised-pork.toml", "mkdir shopping"]
    temp = "shopping/2026-W48.md.tmp"
    writes = [f"unlink {temp}", f"open {temp}", f"move {temp} shopping/2026-W48.md"]
    assert calls == [*reads, *writes]
    assert listings == LISTINGS
    result, calls, listings = traced(home, example.root, "shop", "2026-W48")
    assert result == err(1, [no_menu("2026-W48")])
    assert calls == [READ_SETTINGS, "read catalog.toml", "read pantry.toml"]
    assert listings == LISTINGS


def _check_no_reads(home: Path, example: DataFolder) -> None:
    """Input 4 of F13-T16: a wrong week, and ``--help``, read nothing but the settings."""
    result, calls, listings = traced(home, example.root, "shop", "2026-W99")
    assert result == err(2, [not_a_week("2026-W99")])
    assert (calls, listings) == ([READ_SETTINGS], [])
    result, calls, listings = traced(home, example.root, "shop", "2026-W47", "--help")
    assert result == (0, at(home, None, "--help")[1], "")
    assert (calls, listings) == ([READ_SETTINGS], [])


def _check_stops(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Input 5 of F13-T16: the reads stop at the first error of each reader."""
    three = [READ_SETTINGS, "read catalog.toml", "read pantry.toml"]
    menu = [*three, "read menus/2026-W47.toml"]
    stops = [
        (catalog_brace, [READ_SETTINGS, "read catalog.toml"], [], E_BRACE),
        (pantry_sesame, three, [], E_PANTRY),
        (rice_bowl, three, LISTINGS[:1], E_RICE_BOWL),
        (empty_menu_file("2026-w48.toml"), three, LISTINGS, E_LOWER_48),
        (the_typo, menu, LISTINGS, TYPO),
        (mapo_mistake, [*R47[: R47.index("read recipes/mapo-tofu.toml") + 1]], LISTINGS, E_MAPO),
    ]
    for number, (change, calls, listings, problem) in enumerate(stops):
        root = made(example, tmp_path, f"stop-{number}", change)
        result, found, seen = traced(home, root, "shop", "2026-W47")
        assert result == stop(problem), number
        assert (found, seen) == (calls, listings), number
        assert not (root / "shopping").exists()


def _check_other_files(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Input 6 of F13-T16: ``shop`` reads nothing in ``shopping/``, and keeps its other files."""
    root = made(example, tmp_path, "others", old_list)
    write(root / "shopping" / "2026-W48.md", "other\n")
    write(root / "shopping" / "notes.txt", "x\n")
    others = {
        name: (root / "shopping" / name).stat().st_mtime_ns for name in ("2026-W48.md", "notes.txt")
    }
    result, calls, _ = traced(home, root, "shop", "2026-W47")
    assert result == out(shop_47(root / "shopping" / "2026-W47.md"))
    assert calls == [*R47, *W47]
    assert (root / "shopping" / "2026-W47.md").read_bytes() == FILE_47
    assert (root / "shopping" / "2026-W48.md").read_bytes() == b"other\n"
    assert (root / "shopping" / "notes.txt").read_bytes() == b"x\n"
    for name, stamp in others.items():
        assert (root / "shopping" / name).stat().st_mtime_ns == stamp


def test_f13_t16_shop_reads_each_file_once_in_order_and_writes_through_replace_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The record of the reads and the writes for a list, a failure, a wrong week, and a stop."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_example_reads(home, example_folder)
    _check_week_b_reads(home, example_folder, source, tmp_path)
    _check_no_reads(home, example_folder)
    _check_stops(home, source, tmp_path)
    _check_other_files(home, source, tmp_path)
