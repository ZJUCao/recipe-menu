"""Tests of F11 for create_file when the disk fails: the listing, the open, and the write."""

import sys
from pathlib import Path

import pytest

from f03_support import put_bytes
from f08_support import (
    BUG,
    CTRL_C,
    DENIED,
    EMPTY_IO,
    IO,
    NO_SPACE,
    faults,
    rel,
    rule,
    system_message,
    tree,
)
from f08_texts import FILE_WRITE_DENIED, FOLDER_ACCESS_DENIED, file_error, folder_system_error
from f09_texts import FOLDER_IS_FILE, FOLDER_MISSING
from f11_support import (
    assert_created,
    assert_exists,
    assert_failed,
    base_with_menus,
    held,
    new_base,
)
from recipe_menu.datafile import DataFolder, FileCreation, create_file

NEW = "new\n"
# Input 3 to 6 of F11-T12: the effect of the rule, and the message of the problem.
LISTING_FAULTS = {
    3: (DENIED, FOLDER_ACCESS_DENIED),
    4: (IO, folder_system_error("Input/output error")),
    5: (OSError, folder_system_error("OSError")),
    6: (TimeoutError, folder_system_error("TimeoutError")),
}


def _listing_input(tmp_path: Path, number: int) -> tuple[Path, DataFolder, Path, list, tuple]:
    """Makes input ``number`` of F11-T12 and gives ``base``, ``F``, the path, the rules, the result.

    The result is the file of the problem and its message.
    """
    base, folder = new_base(tmp_path, f"t12-{number}")
    folder.root.mkdir()
    path = folder.menu_file("2026-W47")
    rules: list = []
    result: tuple = ("menus", FOLDER_MISSING)
    if number == 2:
        put_bytes(folder.menus, b"x\n")
        result = ("menus", FOLDER_IS_FILE)
    elif number in LISTING_FAULTS:
        folder.menus.mkdir()
        effect, message = LISTING_FAULTS[number]
        rules = [rule("list", folder.menus, effect)]
        result = ("menus", message)
    elif number == 7:
        path = folder.root / "a" / "b.toml"
        result = ("a", FOLDER_MISSING)
    elif number == 8:
        folder.root.rmdir()
        path = folder.root / "notes.toml"
        result = (".", FOLDER_MISSING)
    return base, folder, path, rules, result


def test_f11_t12_a_listing_that_fails_gives_failed_and_creates_nothing(tmp_path: Path) -> None:
    """Eight inputs: the problem names the folder, with the message of the listing."""
    for number in range(1, 9):
        base, folder, path, rules, (file, message) = _listing_input(tmp_path, number)
        before = tree(base)
        with faults(base, *rules) as state:
            creation = create_file(folder, path, NEW)
        assert_failed(creation, file, message)
        assert state.calls == [], number
        assert tree(base) == before, number


def _open_fails(tmp_path: Path, number: int, effect: object, message: tuple) -> None:
    """Runs an input of F11-T13 whose open raises an error, and checks the problem."""
    base, folder = base_with_menus(tmp_path, f"t13-{number}")
    path = folder.menu_file("2026-W47")
    with faults(base, rule("open", path, effect)) as state:
        creation = create_file(folder, path, NEW)
    assert_failed(creation, "menus/2026-W47.toml", message)
    assert state.calls == [f"open {rel(base, path)}"], number
    assert list(folder.menus.iterdir()) == [], number


def _open_races(tmp_path: Path) -> None:
    """Runs input 1 of F11-T13: another program creates the file after the listing."""
    base, folder = base_with_menus(tmp_path, "t13-1")
    path = folder.menu_file("2026-W47")
    with faults(base, rule("open", path, how="race")) as state:
        creation = create_file(folder, path, NEW)
    assert_exists(creation, path)
    assert held(path) == b"mine\n"
    assert state.calls == [f"open {rel(base, path)}"]
    assert [entry.name for entry in folder.menus.iterdir()] == ["2026-W47.toml"]


def _open_long_name(tmp_path: Path) -> None:
    """Runs input 6 of F11-T13: a file name of 300 characters that the system rejects."""
    base, folder = base_with_menus(tmp_path, "t13-6")
    name = "x" * 300 + ".toml"
    message = system_message("file", folder.menus / name)
    with faults(base) as state:
        creation = create_file(folder, folder.menus / name, NEW)
    assert_failed(creation, f"menus/{name}", message)
    assert message[0].startswith("The file cannot be written. The system says: ")
    assert state.calls == [f"open {rel(base, folder.menus / name)}"]
    assert list(folder.menus.iterdir()) == []


def _open_folded_name(tmp_path: Path) -> None:
    """Runs input 7 of F11-T13: a name that the file system folds beyond A to Z."""
    base, folder = base_with_menus(tmp_path, "t13-7")
    put_bytes(folder.menus / "\u00c4.toml", b"x\n")
    target = folder.menus / "\u00e4.toml"
    with faults(base) as state:
        creation = create_file(folder, target, NEW)
    assert state.calls == [f"open {rel(base, target)}"]
    names = sorted(entry.name for entry in folder.menus.iterdir())
    if sys.platform == "win32":
        assert_exists(creation, target)
        assert names == ["\u00c4.toml"]
        assert held(folder.menus / "\u00c4.toml") == b"x\n"
    else:
        assert_created(creation)
        assert names == ["\u00c4.toml", "\u00e4.toml"]


def test_f11_t13_an_error_of_the_open_gives_the_first_row_of_the_error_table(
    tmp_path: Path,
) -> None:
    """Seven inputs: a race, four errors, a name of 300 characters, and a folded name."""
    _open_races(tmp_path)
    errors = [
        (2, DENIED, FILE_WRITE_DENIED),
        (3, IO, file_error("Input/output error")),
        (4, TimeoutError, file_error("TimeoutError")),
        (5, EMPTY_IO, file_error("OSError")),
    ]
    for number, effect, message in errors:
        _open_fails(tmp_path, number, effect, message)
    _open_long_name(tmp_path)
    _open_folded_name(tmp_path)


OPENED = ["open recipe-menu/menus/2026-W47.toml"]
REMOVED = [*OPENED, "unlink recipe-menu/menus/2026-W47.toml"]
TEN = "0123456789\n"


def _write_case(
    tmp_path: Path,
    number: int,
    rules: list[tuple],
    text: str = TEN,
    raises: type[BaseException] | None = None,
) -> tuple[Path, list[str], FileCreation | None]:
    """Runs an input of F11-T14: ``create_file`` with the rules of the write.

    Args:
        tmp_path: The folder of the test.
        number: The number of the input.
        rules: Each rule as its kind, its effect, and its way.
        text: The text of the file.
        raises: The exception that the call must raise, or ``None`` when it gives a result.

    Returns:
        The path, the record of the harness, and the result, or ``None`` when the call raised.
    """
    base, folder = base_with_menus(tmp_path, f"t14-{number}")
    path = folder.menu_file("2026-W47")
    made = [rule(kind, path, effect, how) for kind, effect, how in rules]
    creation = None
    with faults(base, *made) as state:
        if raises is None:
            creation = create_file(folder, path, text)
        else:
            with pytest.raises(raises):
                create_file(folder, path, text)
    return path, state.calls, creation


def _check_failures(tmp_path: Path) -> None:
    """Checks inputs 1 to 4 of F11-T14: an error of the write gives ``FAILED``."""
    file = "menus/2026-W47.toml"
    no_space = file_error("No space left on device")
    cases = [
        (1, [("write", NO_SPACE, "raise")], TEN, no_space, False),
        (2, [("write", DENIED, "raise")], TEN, FILE_WRITE_DENIED, False),
        (
            3,
            [("write", IO, "raise"), ("unlink", DENIED, "raise")],
            TEN,
            file_error("Input/output error"),
            True,
        ),
        (4, [("write", NO_SPACE, "raise")], "", no_space, False),
    ]
    for number, rules, text, message, left in cases:
        path, record, creation = _write_case(tmp_path, number, rules, text)
        assert creation is not None
        assert_failed(creation, file, message, (path,) if left else ())
        assert record == REMOVED, number
        assert held(path) == (b"01234" if left else None), number


def _check_exceptions(tmp_path: Path) -> None:
    """Checks inputs 5 to 9 of F11-T14: the exceptions that are not an ``OSError`` go on."""
    cases = [
        (5, [("write", BUG, "raise")], RuntimeError, None),
        (6, [("write", CTRL_C, "raise")], KeyboardInterrupt, None),
        (7, [("write", CTRL_C, "raise"), ("unlink", DENIED, "raise")], KeyboardInterrupt, b"01234"),
        (8, [("write", CTRL_C, "raise"), ("unlink", CTRL_C, "raise")], KeyboardInterrupt, b"01234"),
    ]
    for number, rules, error, after in cases:
        path, record, creation = _write_case(tmp_path, number, rules, raises=error)
        assert creation is None
        assert (record, held(path)) == (REMOVED, after), number
    path, record, _ = _write_case(
        tmp_path, 9, [("open", CTRL_C, "after")], raises=KeyboardInterrupt
    )
    assert (record, held(path)) == (OPENED, b"")


def test_f11_t14_a_failed_write_removes_the_file_and_a_failed_removal_leaves_it(
    tmp_path: Path,
) -> None:
    """Nine inputs: a write that fails, a removal that fails, and the exceptions that go on."""
    _check_failures(tmp_path)
    _check_exceptions(tmp_path)
