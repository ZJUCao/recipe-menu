"""Tests of F11 for create_file: the example, the checks, a new file, and the names (T07 to T11)."""

import sys
from pathlib import Path

import pytest

from f03_support import put_bytes
from f08_support import (
    FOLDER,
    dangling_link,
    faults,
    file_of,
    full_record,
    rel,
    system_message,
    tree,
)
from f09_texts import FOLDER_MISSING
from f11_support import assert_created, assert_exists, assert_failed, base_with_menus, held
from recipe_menu.datafile import DataFolder, FileOutcome, create_file
from recipe_menu.lang import Lang


def test_f11_t07_create_file_makes_a_new_file_and_never_overwrites_an_entry(
    tmp_path: Path,
) -> None:
    """The example of 3.3: a new file, a second call, a case difference, and the wrong calls."""
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    folder = DataFolder(tmp / "recipe-menu")
    folder.menus.mkdir(parents=True)
    file = folder.menu_file("2026-W47")
    created = create_file(folder, file, 'week = "2026-W47"\n')
    assert created.outcome is FileOutcome.CREATED
    assert held(file) == b'week = "2026-W47"\n'
    assert_exists(create_file(folder, file, ""), file)
    assert held(file) == b'week = "2026-W47"\n'
    wrong_case = folder.menus / "2026-w48.toml"
    put_bytes(wrong_case, b"")
    assert_exists(create_file(folder, folder.menu_file("2026-W48"), ""), wrong_case)
    missing = create_file(folder, folder.recipe_file("rice"), "servings = 2\n")
    assert_failed(missing, "recipes", FOLDER_MISSING)
    name = "x" * 300 + ".toml"
    msg = system_message("file", folder.menus / name)
    failed = create_file(folder, folder.menus / name, "\n")
    assert_failed(failed, f"menus/{name}", msg)
    assert failed.problem is not None
    assert failed.problem.text(Lang.EN).startswith("The file cannot be written. The system says: ")
    with pytest.raises(ValueError):
        create_file(folder, tmp / "elsewhere.toml", "")
    with pytest.raises(ValueError):
        create_file(folder, folder.root, "")
    with pytest.raises(UnicodeEncodeError):
        create_file(folder, file, "\udc80")
    assert tree(tmp) == {
        "recipe-menu": FOLDER,
        "recipe-menu/menus": FOLDER,
        "recipe-menu/menus/2026-W47.toml": file_of(b'week = "2026-W47"\n'),
        "recipe-menu/menus/2026-w48.toml": file_of(b""),
    }


def test_f11_t08_a_wrong_call_raises_before_the_disk_is_touched(tmp_path: Path) -> None:
    """A path outside the root, the root, a relative path, and a text that UTF-8 cannot encode."""
    base, folder = base_with_menus(tmp_path, "t8")
    path = folder.menu_file("2026-W47")
    wrong_paths = [base / "elsewhere.toml", folder.root, Path("menus", "2026-W47.toml")]
    wrong_texts = ["\udc80", "ok\n\ud800"]
    with faults(base) as state:
        for bad in wrong_paths:
            with pytest.raises(ValueError) as caught:
                create_file(folder, bad, "")
            assert not isinstance(caught.value, UnicodeEncodeError)
        for text in wrong_texts:
            with pytest.raises(UnicodeEncodeError):
                create_file(folder, path, text)
    assert (state.calls, state.listings) == ([], [])
    assert list(folder.menus.iterdir()) == []


def test_f11_t09_a_new_file_is_listed_once_opened_once_and_holds_the_utf8_text(
    tmp_path: Path,
) -> None:
    """Six calls in folders of the root: the record, the listings, and the bytes."""
    base, folder = base_with_menus(tmp_path, "t9")
    folder.recipes.mkdir()
    calls = [
        (folder.menu_file("2026-W47"), 'week = "2026-W47"\n', b'week = "2026-W47"\n', folder.menus),
        (folder.menu_file("2026-W48"), "a\r\nb\n", b"a\r\nb\n", folder.menus),
        (folder.menu_file("2026-W49"), "番茄\n", "番茄\n".encode(), folder.menus),
        (folder.menu_file("2026-W50"), "", b"", folder.menus),
        (folder.recipe_file("rice"), "servings = 2\n", b"servings = 2\n", folder.recipes),
        (folder.root / "notes.toml", "x", b"x", folder.root),
    ]
    for path, text, data, parent in calls:
        with faults(base) as state:
            creation = create_file(folder, path, text)
        assert_created(creation)
        assert state.calls == [f"open {rel(base, path)}"]
        assert state.listings == [rel(base, parent)]
        assert held(path) == data
    folders = (folder.root, folder.menus, folder.recipes)
    expected = {rel(base, each): FOLDER for each in folders}
    expected |= {rel(base, path): file_of(data) for path, _, data, _ in calls}
    assert tree(base) == expected


def _fill(folder: DataFolder, number: int) -> tuple[Path, Path]:
    """Makes the entries of input ``number`` of F11-T10, and gives the path and the entry."""
    menus, recipes = folder.menus, folder.recipes
    if number >= 9:
        recipes.mkdir()
    entries = {
        1: ("2026-W47.toml", b"old\n"),
        2: ("2026-w47.toml", b""),
        3: ("2026-W47.TOML", b""),
        4: ("2026-W47.Toml", b""),
        5: ("2026-w47.TOML", b""),
        8: ("2026-W47.toml", b"[[[\n"),
    }
    if number in entries:
        name, data = entries[number]
        put_bytes(menus / name, data)
        return folder.menu_file("2026-W47"), menus / name
    if number == 6:
        (menus / "2026-W47.toml").mkdir()
    elif number == 7:
        dangling_link(menus / "2026-W47.toml")
    elif number in (9, 10):
        name = "Rice.toml" if number == 9 else "RICE.TOML"
        put_bytes(recipes / name, b"")
        return folder.recipe_file("rice"), recipes / name
    return folder.menu_file("2026-W47"), menus / "2026-W47.toml"


def test_f11_t10_an_entry_that_differs_only_in_case_gives_exists_and_changes_nothing(
    tmp_path: Path,
) -> None:
    """Ten entries give EXISTS and keep their bytes and times, and a different name is free."""
    for number in range(1, 11):
        base, folder = base_with_menus(tmp_path, f"t10-{number}")
        path, entry = _fill(folder, number)
        before = full_record(base)
        with faults(base) as state:
            creation = create_file(folder, path, "new\n")
        assert_exists(creation, entry)
        assert state.calls == [], number
        assert state.listings == [rel(base, path.parent)], number
        assert full_record(base) == before, number
    base, folder = base_with_menus(tmp_path, "t10-11")
    names = ["2026-W47.toml.bak", "2026-W47", "2026-W470.toml", "x2026-W47.toml", "2026-W47.tom"]
    for name in names:
        put_bytes(folder.menus / name, b"")
    before = full_record(base)
    path = folder.menu_file("2026-W47")
    with faults(base):
        creation = create_file(folder, path, "new\n")
    assert_created(creation)
    assert held(path) == b"new\n"
    after = full_record(base)
    for key, value in before.items():
        if value[0] != FOLDER:
            assert after[key] == value, key


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows cannot hold two names that differ only in case"
)
def test_f11_t11_the_exact_name_counts_first_and_then_the_first_match_in_sorted_order(
    tmp_path: Path,
) -> None:
    """Three folders of Linux with several matches: the entry that ``create_file`` names."""
    inputs = [
        (["2026-w47.toml", "2026-W47.TOML"], "2026-W47.TOML"),
        (["2026-w47.toml", "2026-W47.toml", "2026-W47.TOML"], "2026-W47.toml"),
        (["2026-w47.toml", "2026-W47.Toml", "2026-W47.TOML"], "2026-W47.TOML"),
    ]
    for number, (names, expected) in enumerate(inputs, 1):
        base, folder = base_with_menus(tmp_path, f"t11-{number}")
        for name in names:
            put_bytes(folder.menus / name, b"")
        before = full_record(base)
        with faults(base) as state:
            creation = create_file(folder, folder.menu_file("2026-W47"), "new\n")
        assert_exists(creation, folder.menus / expected)
        assert state.calls == []
        assert full_record(base) == before
