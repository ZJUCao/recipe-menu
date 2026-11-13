"""Tests of F07 for the count line, the folders, and the files that check reads (T11 to T14)."""

import shutil
from pathlib import Path

from f03_support import put_bytes, write
from f04_support import listing_denied
from f05_support import copy_example, make_home
from f07_changes import add_monday_breakfast, menu_path
from f07_support import AFTER, check, expect, rep
from f07_texts import (
    DISHES,
    FILE_IS_FOLDER,
    FILE_MISSING,
    FOLDER_ACCESS_DENIED,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    NOT_A_RECIPE_ID,
    NOT_A_WEEK_NAME,
    PORK,
    TOML_ENDING_NOT_SMALL,
    Prob,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang


def test_f07_t11_the_count_line_counts_the_ids_and_the_weeks_of_the_listings(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Names that are no ID or no week do not count, and each listing reports its problems once."""
    home = make_home(tmp_path)
    root = example_folder.root
    for name in ("Rice Bowl.toml", "pancakes.TOML", "notes.txt"):
        write(root / "recipes" / name, "")
    (root / "recipes" / "drafts").mkdir()
    (root / "recipes" / "old.toml").mkdir()
    for name in ("plan.toml", "2026-w48.toml", "2026-W49.TOML", "notes.txt", "2026-W47.toml.bak"):
        write(root / "menus" / name, "")
    (root / "menus" / "2026-W50.toml").mkdir()
    errors = [
        Prob("recipes/pancakes.TOML", None, TOML_ENDING_NOT_SMALL),
        Prob("recipes/Rice Bowl.toml", None, NOT_A_RECIPE_ID),
        Prob("recipes/old.toml", None, FILE_IS_FOLDER),
        Prob("menus/2026-W49.TOML", None, TOML_ENDING_NOT_SMALL),
        Prob("menus/2026-w48.toml", None, NOT_A_WEEK_NAME),
        Prob("menus/plan.toml", None, NOT_A_WEEK_NAME),
        Prob("menus/2026-W50.toml", None, FILE_IS_FOLDER),
    ]
    assert check(home, root) == rep(1, 8, 2, errors, [PORK])


def test_f07_t12_the_count_line_names_the_first_three_files_when_they_are_missing(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A missing settings file does not stop check, and the menus are read with no settings."""
    home = make_home(tmp_path)
    root = example_folder.root
    (root / "settings.toml").unlink()
    (root / "pantry.toml").unlink()
    (root / "catalog.toml").unlink()
    (root / "catalog.toml").mkdir()
    add_monday_breakfast(menu_path(root))
    errors = [
        Prob("settings.toml", None, FILE_MISSING),
        Prob("catalog.toml", None, FILE_IS_FOLDER),
        Prob("pantry.toml", None, FILE_MISSING),
    ]
    assert check(home, root) == rep(1, 7, 1, errors, [PORK])
    assert check(home, root, "--lang", "zh") == rep(1, 7, 1, errors, [PORK], Lang.ZH)


def test_f07_t13_a_folder_that_cannot_be_listed_gives_one_error_of_the_folder(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A missing folder, a file, and a denied listing, for recipes and for menus."""
    home = make_home(tmp_path)
    source = example_folder
    cases = {
        "recipes_missing": ("recipes", "missing", FOLDER_MISSING),
        "recipes_file": ("recipes", "file", FOLDER_IS_FILE),
        "recipes_denied": ("recipes", "denied", FOLDER_ACCESS_DENIED),
        "menus_missing": ("menus", "missing", FOLDER_MISSING),
        "menus_file": ("menus", "file", FOLDER_IS_FILE),
        "menus_denied": ("menus", "denied", FOLDER_ACCESS_DENIED),
    }
    for name, (folder, how, msg) in cases.items():
        root = copy_example(source, tmp_path / name)
        lang = Lang.ZH if name == "recipes_file" else Lang.EN
        argv = ("--lang", "zh") if lang is Lang.ZH else ()
        problem = Prob(folder, None, msg)
        expected = (
            rep(1, 0, 1, [problem, *DISHES], [], lang)
            if folder == "recipes"
            else rep(1, 7, 0, [problem], [PORK], lang)
        )
        target = root / folder
        if how == "denied":
            with listing_denied(target):
                assert check(home, root, *argv) == expected, name
            continue
        shutil.rmtree(target)
        if how == "file":
            write(target, "")
        assert check(home, root, *argv) == expected, name


def test_f07_t14_check_reads_only_the_files_that_it_names(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Other files and folders hold no TOML or no UTF-8, and check does not read them."""
    home = make_home(tmp_path)
    root = example_folder.root
    for relative in (
        "notes.txt",
        "catalog.toml.bak",
        "recipes/notes.txt",
        "recipes/drafts/pancakes.toml",
        "menus/2026-W47.toml.bak",
    ):
        write(root.joinpath(*relative.split("/")), "[[[")
    put_bytes(root / "shopping" / "2026-W47.md", b"\xff\xfe")
    assert check(home, root) == expect(0, AFTER)
    shutil.rmtree(root / "shopping")
    write(root / "shopping", "[[[")
    assert check(home, root) == expect(0, AFTER)
