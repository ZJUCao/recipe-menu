"""Tests of F06 for list_menu_weeks (T23 to T29)."""

import shutil
import sys
from pathlib import Path

import pytest

from f03_support import M_FILE_MISSING, put_bytes, write
from f04_support import (
    M_FOLDER_DENIED,
    M_FOLDER_IS_FILE,
    M_FOLDER_MISSING,
    M_TOML_ENDING,
    listing_denied,
    touch,
)
from f06_support import (
    bad,
    check_fails,
    check_reads,
    check_weeks,
    example_filled,
    example_settings,
    name_entries,
    put_menu,
    week47,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, list_menu_weeks

CASE_FILES = (
    "2026-W53.toml",
    "2026-W48.TOML",
    "2026-W49.Toml",
    "2026-w47.toml",
    "2026-W7.toml",
    "2026-W99.toml",
    "2026-W00.toml",
    "2025-W53.toml",
    "9999-W52.toml",
    "0000-W01.toml",
    "10000-W01.toml",
    "plan.toml",
    ".toml",
    "2026-W47 (copy).toml",
    "2026-W47.toml.toml",
    "\uff12\uff10\uff12\uff16-W47.toml",
)


def test_f06_t23_the_design_example_of_list_menu_weeks(example_folder: DataFolder) -> None:
    """The example menu, names that are not weeks, a capital ending, and a missing folder."""
    folder = example_folder
    assert list_menu_weeks(folder) == ((IsoWeek(2026, 47),), ())

    names = ["2026-W53.toml", "2027-W01.toml", "2026-w48.toml", "2026-W99.toml", "2026-W49.TOML"]
    touch(folder.menus, *names)
    write(folder.menus / "notes.txt", "Ideas\n")
    weeks, problems = list_menu_weeks(folder)
    assert weeks == (IsoWeek(2026, 47), IsoWeek(2026, 53), IsoWeek(2027, 1))
    assert [problem.file.name for problem in problems] == [
        "2026-W49.TOML",
        "2026-W99.toml",
        "2026-w48.toml",
    ]
    assert all(problem.place is None for problem in problems)
    assert problems[2].text(Lang.ZH) == "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。"
    expected = [
        bad(None, M_TOML_ENDING, "menus/2026-W49.TOML"),
        *name_entries("2026-W99.toml", "2026-w48.toml"),
    ]
    check_weeks(folder, [IsoWeek(2026, 47), IsoWeek(2026, 53), IsoWeek(2027, 1)], expected)

    shutil.rmtree(folder.menus)
    weeks, problems = list_menu_weeks(folder)
    assert weeks == ()
    assert [problem.file for problem in problems] == [Path("menus")]
    assert problems[0].text(Lang.EN) == "The folder is missing."
    check_weeks(folder, [], [bad(None, M_FOLDER_MISSING, "menus")])


def test_f06_t24_an_empty_menus_folder_and_entries_that_are_no_menu_files_give_nothing(
    folder: DataFolder,
) -> None:
    """No weeks and no problems, and a folder below ``menus/`` is not looked into."""
    folder.menus.mkdir()
    assert list_menu_weeks(folder) == ((), ())
    write(folder.menus / "notes.txt", "Ideas\n")
    touch(
        folder.menus,
        "2026-W47.toml.bak",
        "2026-W47",
        "2026-W47.tomlx",
        "2026-W47toml",
        "old/2026-W46.toml",
    )
    assert list_menu_weeks(folder) == ((), ())


def test_f06_t25_the_weeks_come_in_the_order_of_time_from_the_file_names_alone(
    folder: DataFolder,
) -> None:
    """A file that cannot be read, or is empty, or is a folder, still gives its week."""
    touch(folder.menus, "2027-W01.toml")
    put_bytes(folder.menus / "9999-W51.toml", b"\xff")
    write(folder.menus / "0001-W01.toml", 'week = "')
    touch(
        folder.menus,
        "2026-W53.toml",
        "2026-W10.toml",
        "2026-W09.toml",
        "1000-W01.toml",
        "0999-W52.toml",
        "2020-W53.toml",
    )
    (folder.menus / "2026-W50.toml").mkdir()
    pairs = (
        (1, 1),
        (999, 52),
        (1000, 1),
        (2020, 53),
        (2026, 9),
        (2026, 10),
        (2026, 50),
        (2026, 53),
        (2027, 1),
        (9999, 51),
    )
    check_weeks(folder, [IsoWeek(*pair) for pair in pairs], [])


def test_f06_t26_a_menu_file_that_is_no_week_gives_an_error_in_the_order_of_the_names(
    folder: DataFolder,
) -> None:
    """The capital endings come first, then the names that are not weeks, each with no place."""
    touch(folder.menus, *CASE_FILES)
    expected = [
        bad(None, M_TOML_ENDING, "menus/2026-W48.TOML"),
        bad(None, M_TOML_ENDING, "menus/2026-W49.Toml"),
        *name_entries(
            ".toml",
            "0000-W01.toml",
            "10000-W01.toml",
            "2025-W53.toml",
            "2026-W00.toml",
            "2026-W47 (copy).toml",
            "2026-W47.toml.toml",
            "2026-W7.toml",
            "2026-W99.toml",
            "2026-w47.toml",
            "9999-W52.toml",
            "plan.toml",
            "\uff12\uff10\uff12\uff16-W47.toml",
        ),
    ]
    check_weeks(folder, [IsoWeek(2026, 53)], expected)


def test_f06_t27_a_menus_folder_that_cannot_be_listed_gives_no_weeks_and_one_problem(
    folder: DataFolder, tmp_path: Path
) -> None:
    """A missing folder, a file, a denied listing, and a missing root each give one problem."""
    check_weeks(folder, [], [bad(None, M_FOLDER_MISSING, "menus")], "missing")
    put_bytes(folder.menus, b"")
    check_weeks(folder, [], [bad(None, M_FOLDER_IS_FILE, "menus")], "file")
    folder.menus.unlink()
    touch(folder.menus, "2026-W47.toml")
    with listing_denied(folder.menus):
        check_weeks(folder, [], [bad(None, M_FOLDER_DENIED, "menus")], "denied")
    check_weeks(DataFolder(tmp_path / "missing"), [], [bad(None, M_FOLDER_MISSING, "menus")])


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="A folder on Windows cannot hold 2026-W47.toml and 2026-w47.toml side by side. "
    "CI runs this case on Linux.",
)
def test_f06_t28_only_the_exact_name_gives_the_week_on_linux(example_folder: DataFolder) -> None:
    """Three names that differ in case sit side by side, and only ``2026-W47.toml`` is read."""
    example = example_folder
    put_menu(example, "[monday]", 'dinner = ["rice"]', name="2026-w47")
    touch(example.menus, "2026-W47.TOML")
    expected = [bad(None, M_TOML_ENDING, "menus/2026-W47.TOML"), *name_entries("2026-w47.toml")]
    check_weeks(example, [week47()], expected)
    check_reads(example, example_settings(), example_filled())


def test_f06_t29_a_name_with_the_wrong_case_is_no_week_on_either_system(
    example_folder: DataFolder,
) -> None:
    """Both systems list no week, and only Windows opens the file whose case differs."""
    example = example_folder
    text = example.menu_file("2026-W47").read_text(encoding="utf-8")
    example.menu_file("2026-W47").unlink()
    write(example.menus / "2026-w47.toml", text)
    write(example.menus / "2026-W48.TOML", 'week = "2026-W48"\n')
    expected = [bad(None, M_TOML_ENDING, "menus/2026-W48.TOML"), *name_entries("2026-w47.toml")]
    check_weeks(example, [], expected)
    settings = example_settings()
    if sys.platform == "win32":
        check_reads(example, settings, example_filled(), label="2026-W47")
        check_reads(example, settings, week=IsoWeek(2026, 48), label="2026-W48")
        return
    for week in (week47(), IsoWeek(2026, 48)):
        file = f"menus/{week}.toml"
        check_fails(example, settings, [bad(None, M_FILE_MISSING, file)], week=week)
