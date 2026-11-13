"""Tests of F08 for the errors of create_data_folder: the error table, a root, and a listing.

These are T07 to T09.
"""

from pathlib import Path

from f03_support import put_bytes
from f05_support import unreadable_name
from f08_support import (
    DENIED,
    EMPTY_IO,
    FOLDER,
    IO,
    Rule,
    assert_failed,
    dangling_link,
    faults,
    file_of,
    items,
    rel,
    rule,
    system_message,
    tree,
)
from f08_texts import (
    FILE_EXISTS,
    FILE_WRITE_DENIED,
    FOLDER_ACCESS_DENIED,
    FOLDER_CREATE_DENIED,
    FOLDER_EXISTS,
    Msg,
    file_error,
    folder_error,
    folder_system_error,
)
from recipe_menu.datafile import DataFolder, create_data_folder

FOLDER_ERROR_START = "The folder cannot be created. The system says: "
FILE_ERROR_START = "The file cannot be written. The system says: "


def _plain_cases(root: Path) -> list[tuple[Rule, str, Msg, dict]]:
    """Gives cases 1 to 4 and 7 to 9 of F08-T07: a rule, the problem's file and message, R after."""
    pantry = root / "pantry.toml"
    return [
        (rule("mkdir", root / "menus", how="race"), "menus", FOLDER_EXISTS, {"menus": FOLDER}),
        (
            rule("open", root / "catalog.toml", how="race"),
            "catalog.toml",
            FILE_EXISTS,
            {"catalog.toml": file_of(b"mine\n")},
        ),
        (rule("mkdir", root / "shopping", DENIED), "shopping", FOLDER_CREATE_DENIED, {}),
        (
            rule("open", root / "recipes" / "tomato-egg.toml", DENIED),
            "recipes/tomato-egg.toml",
            FILE_WRITE_DENIED,
            {},
        ),
        (rule("mkdir", root / "menus", TimeoutError), "menus", folder_error("TimeoutError"), {}),
        (rule("open", pantry, EMPTY_IO), "pantry.toml", file_error("OSError"), {}),
        (rule("open", pantry, IO), "pantry.toml", file_error("Input/output error"), {}),
    ]


def _t07_table(tmp_path: Path) -> None:
    """Runs cases 1 to 4 and 7 to 9: the rows of the error table."""
    for index, number in enumerate((1, 2, 3, 4, 7, 8, 9)):
        base = tmp_path / f"t{number}"
        root = base / "recipe-menu"
        root.mkdir(parents=True)
        folders, files = items(root)
        found, file, msg, after = _plain_cases(root)[index]
        with faults(base, found):
            creation = create_data_folder(DataFolder(root), folders, files)
        assert_failed(creation, file, msg)
        assert tree(root) == after, number


def _t07_long_names(tmp_path: Path) -> None:
    """Runs cases 5 and 6: a folder and a file whose names the system rejects."""
    name = "x" * 300
    base = tmp_path / "t5"
    root = base / "recipe-menu"
    root.mkdir(parents=True)
    msg = system_message("folder", base / name)
    with faults(base):
        creation = create_data_folder(DataFolder(root), (root / "recipes", root / name), ())
    assert_failed(creation, name, msg)
    assert msg[0].startswith(FOLDER_ERROR_START)
    assert tree(root) == {}

    base = tmp_path / "t6"
    root = base / "recipe-menu"
    root.mkdir(parents=True)
    msg = system_message("file", base / (name + ".toml"))
    files = ((root / "settings.toml", "s\n"), (root / (name + ".toml"), "t\n"))
    with faults(base):
        creation = create_data_folder(DataFolder(root), (), files)
    assert_failed(creation, name + ".toml", msg)
    assert msg[0].startswith(FILE_ERROR_START)
    assert tree(root) == {}


def _t07_race_above(tmp_path: Path) -> None:
    """Runs case 10: the other program's folder keeps R and the folder above it."""
    base = tmp_path / "t10"
    base.mkdir()
    root = base / "a" / "recipe-menu"
    folders, files = items(root)
    with faults(base, rule("mkdir", root / "menus", how="race")):
        creation = create_data_folder(DataFolder(root), folders, files)
    assert_failed(creation, "menus", FOLDER_EXISTS, (root, base / "a"))
    assert tree(base) == {"a": FOLDER, "a/recipe-menu": FOLDER, "a/recipe-menu/menus": FOLDER}


def test_f08_t07_each_row_of_the_error_table_gives_its_problem_and_removes_what_it_made(
    tmp_path: Path,
) -> None:
    """The rows of 3.2 for a folder and a file: exists, denied, and any other OSError."""
    _t07_table(tmp_path)
    _t07_long_names(tmp_path)
    _t07_race_above(tmp_path)


def _t08_root_and_above(tmp_path: Path) -> None:
    """Runs cases 1 to 3: a mkdir that fails at the root, above it, and by a race."""
    base = tmp_path / "t1"
    base.mkdir()
    root = base / "a" / "b" / "recipe-menu"
    folders, files = items(root)
    names = ["mkdir a", "mkdir a/b", "mkdir a/b/recipe-menu", "rmdir a/b", "rmdir a"]
    for number, target, record in ((1, root, names), (2, root.parent, [*names[:2], "rmdir a"])):
        with faults(base, rule("mkdir", target, DENIED)) as seen:
            creation = create_data_folder(DataFolder(root), folders, files)
        assert_failed(creation, ".", FOLDER_CREATE_DENIED)
        assert seen.calls == record, number
        assert tree(base) == {}, number
    other = tmp_path / "t3"
    other.mkdir()
    root = other / "recipe-menu"
    folders, files = items(root)
    with faults(other, rule("mkdir", root, how="race")):
        creation = create_data_folder(DataFolder(root), folders, files)
    assert_failed(creation, ".", FOLDER_EXISTS)
    assert tree(other) == {"recipe-menu": FOLDER}


def _t08_file_or_link(tmp_path: Path) -> None:
    """Runs cases 5 to 8: the first mkdir is of the path just below the file or the link."""
    base = tmp_path / "t5"
    base.mkdir()
    put_bytes(base / "notes.txt", b"Ideas\n")
    dangling_link(base / "old")
    cases = [
        (base / "notes.txt" / "recipe-menu", base / "notes.txt" / "recipe-menu"),
        (base / "old" / "recipe-menu", base / "old" / "recipe-menu"),
        (base / "notes.txt" / "a" / "recipe-menu", base / "notes.txt" / "a"),
        (base / "old" / "a" / "recipe-menu", base / "old" / "a"),
    ]
    for root, first in cases:
        folders, files = items(root)
        msg = system_message("folder", first)
        before = tree(base)
        with faults(base) as seen:
            creation = create_data_folder(DataFolder(root), folders, files)
        assert_failed(creation, ".", msg)
        assert seen.calls == [f"mkdir {rel(base, first)}"], root
        assert msg[0].startswith(FOLDER_ERROR_START)
        assert tree(base) == before, root


def test_f08_t08_a_failure_at_the_root_or_above_has_the_file_dot_and_removes_the_folders_above(
    tmp_path: Path,
) -> None:
    """Failures at or above the root have the file dot, and a file or link is never missing."""
    _t08_root_and_above(tmp_path)
    base = tmp_path / "t4"
    base.mkdir()
    unreadable = unreadable_name(base)
    for root in (unreadable, unreadable / "recipe-menu"):
        folders, files = items(root)
        msg = system_message("folder", unreadable)
        creation = create_data_folder(DataFolder(root), folders, files)
        assert_failed(creation, ".", msg)
        assert msg[0].startswith(FOLDER_ERROR_START)
        assert tree(base) == {}
    _t08_file_or_link(tmp_path)


def test_f08_t09_a_listing_that_fails_gives_the_problem_of_the_listing_and_creates_nothing(
    tmp_path: Path,
) -> None:
    """The listing problems of list_toml_files for DENIED, IO, and an OSError with no text."""
    cases = [
        (DENIED, FOLDER_ACCESS_DENIED),
        (IO, folder_system_error("Input/output error")),
        (OSError, folder_system_error("OSError")),
    ]
    for number, (effect, msg) in enumerate(cases, 1):
        base = tmp_path / f"t{number}"
        root = base / "recipe-menu"
        root.mkdir(parents=True)
        folders, files = items(root)
        with faults(base, rule("list", root, effect)) as seen:
            creation = create_data_folder(DataFolder(root), folders, files)
        assert_failed(creation, ".", msg)
        assert seen.calls == [], number
        assert tree(root) == {}, number
