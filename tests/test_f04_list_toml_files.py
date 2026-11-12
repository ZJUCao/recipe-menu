"""Tests of F04 for list_toml_files (T48 to T54)."""

import shutil
import sys
from pathlib import Path

import pytest

from f04_support import (
    M_FOLDER_DENIED,
    M_FOLDER_IS_FILE,
    M_FOLDER_MISSING,
    M_TOML_ENDING,
    check_problems,
    dish_text,
    err,
    listing_denied,
    m_folder_system,
    put_bytes,
    touch,
    write,
)
from recipe_menu.datafile import DataFolder, list_toml_files
from recipe_menu.recipes import list_recipe_ids


def test_f04_t48_the_design_example_on_the_menus_folder(example_folder: DataFolder) -> None:
    """A capital ending, a missing folder, a file in its place, and a path outside the data."""
    folder = example_folder
    assert list_toml_files(folder, folder.menus) == (("2026-W47",), ())
    write(folder.menus / "notes.txt", "Ideas\n")
    touch(folder.menus, "2026-W48.TOML")
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ("2026-W47",)
    check_problems(problems, [err(None, M_TOML_ENDING, "menus/2026-W48.TOML")])
    shutil.rmtree(folder.menus)
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "menus")])
    write(folder.menus, "")
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_IS_FILE, "menus")])
    with pytest.raises(ValueError):
        list_toml_files(folder, Path("D:/other"))


def test_f04_t49_which_entries_count_and_how_the_names_sort(
    folder: DataFolder, tmp_path: Path
) -> None:
    """The names sort by code point as strings, so Z comes before a, and a before a-b."""
    path = tmp_path / "x"
    put_bytes(path / "b.toml", b"\xff")
    touch(
        path,
        "a.toml",
        "a-b.toml",
        ".toml",
        "d.toml.toml",
        "e.TOML.toml",
        "f .toml",
        "Z.toml",
        "notes.txt",
        "rice.toml.bak",
        "toml",
        "atoml",
        "g.tom",
        "g.\uff54oml",
        "i.toml\u200b",
    )
    (path / "c.toml").mkdir()
    write(path / "sub" / "h.toml", "")
    names, problems = list_toml_files(folder, path)
    assert names == ("", "Z", "a", "a-b", "b", "c", "d.toml", "e.TOML", "f ")
    assert problems == ()


def test_f04_t50_a_capital_in_the_ending_gives_an_error_sorted_by_the_whole_name(
    folder: DataFolder,
) -> None:
    """The problems sort by the whole entry name as a string: Z.TOML, a-b.TOML, then a.TOML."""
    touch(
        folder.menus,
        "a.TOML",
        "a-b.TOML",
        ".TOML",
        "b.Toml",
        "c.toML",
        "d.tomL",
        "Z.TOML",
        "h.toml",
        "e.TOML.bak",
        "f.TOM",
        "g.\uff34OML",
    )
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ("h",)
    ordered = (".TOML", "Z.TOML", "a-b.TOML", "a.TOML", "b.Toml", "c.toML", "d.tomL")
    check_problems(problems, [err(None, M_TOML_ENDING, f"menus/{name}") for name in ordered])


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows compares file names without case, so rice.TOML there is rice.toml, and a "
    "folder cannot hold the three files. CI runs this case on Linux.",
)
def test_f04_t51_three_files_that_differ_in_case_give_one_name_and_two_errors(
    folder: DataFolder,
) -> None:
    """``rice.toml`` is the recipe, and ``rice.TOML`` and ``rice.Toml`` are errors, in order."""
    write(folder.recipes / "rice.toml", dish_text())
    touch(folder.recipes, "rice.TOML", "rice.Toml")
    expected = [
        err(None, M_TOML_ENDING, "recipes/rice.TOML"),
        err(None, M_TOML_ENDING, "recipes/rice.Toml"),
    ]
    names, problems = list_toml_files(folder, folder.recipes)
    assert names == ("rice",)
    check_problems(problems, expected, "list_toml_files")
    ids, problems = list_recipe_ids(folder)
    assert ids == ("rice",)
    check_problems(problems, expected, "list_recipe_ids")


def test_f04_t52_a_folder_that_cannot_be_listed_gives_one_error(
    folder: DataFolder, tmp_path: Path
) -> None:
    """A missing folder, a file in its place, and a denied listing, with no place."""
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "menus")], 1)
    nowhere = DataFolder(tmp_path / "nowhere")
    names, problems = list_toml_files(nowhere, nowhere.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "menus")], 2)
    write(tmp_path / "data.txt", "x\n")
    below_file = DataFolder(tmp_path / "data.txt")
    names, problems = list_toml_files(below_file, below_file.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_MISSING, "menus")], 3)
    write(folder.menus, "")
    names, problems = list_toml_files(folder, folder.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_IS_FILE, "menus")], 4)
    folder.menus.unlink()
    folder.menus.mkdir()
    with listing_denied(folder.menus):
        names, problems = list_toml_files(folder, folder.menus)
    assert names == ()
    check_problems(problems, [err(None, M_FOLDER_DENIED, "menus")], 5)


def test_f04_t53_any_other_oserror_gives_the_system_message(
    folder: DataFolder, tmp_path: Path
) -> None:
    """The reason is the ``strerror`` of the error, and the probe with ``is_file`` never raises."""
    if sys.platform == "win32":
        name = "a?b"
        reason = "The filename, directory name, or volume label syntax is incorrect"
    else:
        name = "a" * 256
        reason = "File name too long"
    names, problems = list_toml_files(folder, tmp_path / name)
    assert names == ()
    check_problems(problems, [err(None, m_folder_system(reason), name)])


def test_f04_t54_a_path_outside_the_data_folder_raises(tmp_path: Path) -> None:
    """``list_toml_files`` finds the wrong call before it lists."""
    folder = DataFolder(tmp_path / "recipe-menu")
    folder.root.mkdir()
    touch(tmp_path / "other", "a.toml")
    (tmp_path / "recipe-menu2").mkdir()
    for path in (
        tmp_path / "other",
        tmp_path / "recipe-menu2",
        tmp_path,
        Path("menus"),
        Path("D:/other"),
    ):
        with pytest.raises(ValueError):
            list_toml_files(folder, path)
