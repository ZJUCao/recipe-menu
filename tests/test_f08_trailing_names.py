"""Tests of F08 for data folders whose last part ends with spaces or dots (choice 9).

These are T22 and T23. On Windows, the system drops trailing spaces and dots of a name, and on
Linux they are ordinary characters, so each case says what it expects on each system.
"""

import os
import sys
from pathlib import Path

from f03_support import put_bytes
from f05_support import make_home
from f07_support import check
from f08_support import file_of, init, new_tree, system_message, tree, under
from f08_texts import CHECK_NEW, err_of, fail, holds, new, out_of

WINDOWS = sys.platform == "win32"
ENDINGS = (" ", "  ", "..", " .", ". ")


def _state(tmp_path: Path, name: str, state: int) -> tuple[Path, Path, Path]:
    """Makes the ``base`` of one run in its state, and gives ``base``, ``X``, and ``Y``.

    State 1 has ``X`` and no ``Y``, state 2 has neither, state 3 has an empty ``Y``, and state
    4 has a ``Y`` that holds ``notes.txt``.
    """
    base = tmp_path / name
    base.mkdir()
    folder_x = base / "x"
    folder_y = folder_x / "recipe-menu"
    if state == 1:
        folder_x.mkdir()
    elif state == 3:
        folder_y.mkdir(parents=True)
    elif state == 4:
        put_bytes(folder_y / "notes.txt", b"Ideas\n")
    return base, folder_x, folder_y


def _t22_run(tmp_path: Path, home: Path, name: str, ending: str, state: int) -> None:
    """Runs one ending in one state of F08-T22."""
    base, _, folder_y = _state(tmp_path, name, state)
    value = str(folder_y) + ending
    before = tree(base)
    y_before = tree(folder_y) if state >= 3 else {}
    if WINDOWS:
        recipes = value + os.sep + "recipes"
        message = system_message("folder", recipes)
        expected = err_of(1, [holds(value)]) if state == 4 else err_of(1, fail(recipes, message))
    else:
        expected = out_of(0, new(value))
    assert init(home, folder=value) == expected, (ending, state)
    if WINDOWS:
        assert tree(base) == before, (ending, state)
    else:
        assert tree(Path(value)) == new_tree(), (ending, state)
        assert state < 3 or tree(folder_y) == y_before, (ending, state)


def test_f08_t22_an_ending_of_spaces_or_dots_fails_at_recipes_on_windows_and_works_on_linux(
    tmp_path: Path,
) -> None:
    """Five endings in four states: Windows leaves every folder as it was, Linux creates one."""
    home = make_home(tmp_path)
    for index, ending in enumerate(ENDINGS):
        for state in (1, 2, 3, 4):
            _t22_run(tmp_path, home, f"t{index}_{state}", ending, state)


def test_f08_t23_a_single_trailing_dot_names_the_folder_that_windows_uses(
    tmp_path: Path,
) -> None:
    """The dot is dropped by Windows and kept by Linux: init, check, and a second init agree."""
    home = make_home(tmp_path)
    for state in (1, 2, 3, 4):
        base, folder_x, folder_y = _state(tmp_path, f"t{state}", state)
        value = str(folder_y) + "."
        if state == 4:
            expected = err_of(1, [holds(value)]) if WINDOWS else out_of(0, new(value))
            assert init(home, folder=value) == expected, state
            assert tree(folder_y) == {"notes.txt": file_of(b"Ideas\n")}, state
            continue
        assert init(home, folder=value) == out_of(0, new(value)), state
        assert check(home, Path(value)) == out_of(0, CHECK_NEW), state
        assert init(home, folder=value) == err_of(1, [holds(value)]), state
        if WINDOWS:
            assert tree(folder_x) == under("recipe-menu", new_tree()), state
        else:
            assert tree(Path(value)) == new_tree(), state
            assert state != 3 or tree(folder_y) == {}, state
        assert base.exists()
