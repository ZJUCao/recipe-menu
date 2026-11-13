"""Tests of F08 for create_data_folder: the example, wrong calls, refusals, and a new folder.

These are T03 to T06.
"""

from pathlib import Path

import pytest

from f03_support import put_bytes
from f08_support import (
    FOLDER,
    dangling_link,
    faults,
    file_of,
    fill_entry,
    full_record,
    items,
    make_steps,
    record_of,
    rel,
    tree,
)
from recipe_menu.datafile import Creation, CreationOutcome, DataFolder, create_data_folder
from recipe_menu.lang import Lang


def _example_first_calls(tmp: Path) -> DataFolder:
    """Makes the first two calls and the file call of the example of 3.2."""
    folder = DataFolder(tmp / "a" / "recipe-menu")
    folders = (folder.recipes, folder.menus)
    files = (
        (folder.settings, 'language = "en"\n'),
        (folder.recipe_file("rice"), "servings = 2\n"),
    )
    creation = create_data_folder(folder, folders, files)
    assert creation.outcome is CreationOutcome.CREATED
    assert (creation.problem, creation.left) == (None, ())
    assert folder.settings.read_bytes() == b'language = "en"\n'
    names = sorted(entry.name for entry in folder.root.iterdir())
    assert names == ["menus", "recipes", "settings.toml"]
    assert [entry.name for entry in folder.recipes.iterdir()] == ["rice.toml"]

    assert create_data_folder(folder, folders, files).outcome is CreationOutcome.HOLDS_FILES
    assert folder.settings.read_bytes() == b'language = "en"\n'
    not_a_folder = create_data_folder(DataFolder(folder.settings), (), ())
    assert not_a_folder.outcome is CreationOutcome.NOT_A_FOLDER
    return folder


def _example_failure(tmp: Path) -> None:
    """Runs the failure of the example of 3.2: a name of 300 characters after the settings."""
    other = DataFolder(tmp / "b" / "recipe-menu")
    name = "x" * 300 + ".toml"
    files = ((other.settings, "\n"), (other.root / name, "\n"))
    failed = create_data_folder(other, (other.recipes,), files)
    assert failed.outcome is CreationOutcome.FAILED
    assert failed.problem is not None
    assert (failed.problem.file, failed.problem.place) == (Path(name), None)
    text = failed.problem.text(Lang.EN)
    assert text.startswith("The file cannot be written. The system says: ")
    assert failed.left == ()
    assert not (tmp / "b").exists()


def _example_wrong_calls(tmp: Path) -> None:
    """Runs the four wrong calls of the example of 3.2."""
    fresh = DataFolder(tmp / "c")
    with pytest.raises(ValueError, match=r"."):
        create_data_folder(fresh, (), ((tmp / "elsewhere.toml", ""),))
    with pytest.raises(ValueError, match=r"."):
        create_data_folder(fresh, (), ((fresh.recipe_file("rice"), ""),))
    with pytest.raises(ValueError, match=r"."):
        create_data_folder(fresh, (fresh.menus, fresh.menus), ())
    with pytest.raises(UnicodeEncodeError):
        create_data_folder(fresh, (), ((fresh.settings, chr(0xDC80)),))


def test_f08_t03_the_example_of_3_2_creates_finds_refuses_fails_and_rejects_wrong_calls(
    tmp_path: Path,
) -> None:
    """The example of 3.2: four calls, a failure at a name of 300 characters, four wrong calls."""
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    _example_first_calls(tmp)
    _example_failure(tmp)
    _example_wrong_calls(tmp)
    root = "a/recipe-menu"
    assert tree(tmp) == {
        "a": FOLDER,
        root: FOLDER,
        f"{root}/menus": FOLDER,
        f"{root}/recipes": FOLDER,
        f"{root}/recipes/rice.toml": file_of(b"servings = 2\n"),
        f"{root}/settings.toml": file_of(b'language = "en"\n'),
    }


def _wrong_calls(folder: DataFolder, base: Path) -> list[tuple[tuple, tuple, type[Exception]]]:
    """Gives the 13 wrong calls of F08-T04 for a data folder: folders, files, and the error."""
    root = folder.root
    return [
        ((base / "other",), (), ValueError),
        ((root,), (), ValueError),
        ((folder.menus, folder.menus), (), ValueError),
        ((root / "a" / "b",), (), ValueError),
        ((root / "a" / "b", root / "a"), (), ValueError),
        ((Path("menus"),), (), ValueError),
        ((), ((base / "elsewhere.toml", ""),), ValueError),
        ((), ((root, ""),), ValueError),
        ((), ((folder.recipe_file("rice"), ""),), ValueError),
        ((), ((folder.settings, "a\n"), (folder.settings, "b\n")), ValueError),
        ((folder.menus,), ((folder.menus, ""),), ValueError),
        ((), ((folder.settings, chr(0xDC80)),), UnicodeEncodeError),
        ((), ((folder.settings, "ok\n"), (folder.catalog, chr(0xD800))), UnicodeEncodeError),
    ]


def test_f08_t04_a_wrong_call_raises_before_the_call_touches_the_disk(tmp_path: Path) -> None:
    """13 wrong calls for a missing and an empty data folder raise, and touch nothing."""
    base = tmp_path / "t4"
    empty = DataFolder(base / "e")
    empty.root.mkdir(parents=True)
    missing = DataFolder(base / "m")
    for folder in (missing, empty):
        for number, (folders, files, error) in enumerate(_wrong_calls(folder, base), 1):
            with faults(base) as seen, pytest.raises(error):
                create_data_folder(folder, folders, files)
            assert (seen.calls, seen.listings) == ([], []), number
            assert not missing.root.exists(), number
            assert list(empty.root.iterdir()) == [], number


def _hold(root: Path, number: int) -> None:
    """Makes the data folder of case ``number`` of F08-T05."""
    if number <= 6:
        fill_entry(root, number)
    elif number == 7:
        root.mkdir()
        put_bytes(root / "settings.toml", b"[[[")
    elif number == 8:
        put_bytes(root, b"Ideas\n")
    else:
        dangling_link(root)


def test_f08_t05_a_folder_with_an_entry_and_a_non_folder_are_refused_and_nothing_changes(
    tmp_path: Path,
) -> None:
    """HOLDS_FILES for an entry of any kind, NOT_A_FOLDER for a file or a dangling link."""
    for number in range(1, 10):
        base = tmp_path / f"t{number}"
        base.mkdir()
        root = base / "recipe-menu"
        _hold(root, number)
        folders, files = items(root)
        before = full_record(base)
        with faults(base) as seen:
            creation = create_data_folder(DataFolder(root), folders, files)
        if number <= 7:
            assert creation == Creation(CreationOutcome.HOLDS_FILES), number
            assert seen.listings
            assert set(seen.listings) == {rel(base, root)}, number
        else:
            assert creation == Creation(CreationOutcome.NOT_A_FOLDER), number
            assert seen.listings == [], number
        assert seen.calls == [], number
        assert full_record(base) == before, number


def _many(root: Path) -> tuple[tuple[Path, ...], tuple[tuple[Path, str], ...]]:
    """Gives the folders and files of F08-T06 cases 1 and 2."""
    folders = (root / "recipes", root / "menus", root / "recipes" / "old")
    files = (
        (root / "settings.toml", 'language = "en"\n'),
        (root / "recipes" / "old" / "x.toml", "a\r\nb\n"),
        (root / "note.toml", "番茄\n"),
        (root / "empty.toml", ""),
    )
    return folders, files


def test_f08_t06_a_working_call_creates_the_folders_and_files_in_order_with_their_bytes(
    tmp_path: Path,
) -> None:
    """Missing folders above the root come first, then the root, the folders, and the files."""
    bytes_of = {
        "settings.toml": b'language = "en"\n',
        "recipes/old/x.toml": b"a\r\nb\n",
        "note.toml": "番茄\n".encode(),
        "empty.toml": b"",
    }
    expected = {key: file_of(data) for key, data in bytes_of.items()}
    expected |= {"recipes": FOLDER, "menus": FOLDER, "recipes/old": FOLDER}
    for number, root_path in ((1, Path("a", "b", "recipe-menu")), (2, Path("recipe-menu"))):
        base = tmp_path / f"t{number}"
        base.mkdir()
        root = base / root_path
        if number == 2:
            root.mkdir(parents=True)
        folders, files = _many(root)
        steps = make_steps(root, folders, files)
        with faults(base) as seen:
            creation = create_data_folder(DataFolder(root), folders, files)
        assert creation == Creation(CreationOutcome.CREATED), number
        assert seen.calls == record_of(base, steps, len(steps), 0), number
        assert seen.listings == ([] if number == 1 else [rel(base, root)]), number
        assert not any(call.startswith("read") for call in seen.calls)
        assert tree(root) == expected, number
    base = tmp_path / "t3"
    base.mkdir()
    with faults(base) as seen:
        creation = create_data_folder(DataFolder(base / "c"), (), ())
    assert creation == Creation(CreationOutcome.CREATED)
    assert seen.calls == ["mkdir c"]
    assert tree(base) == {"c": FOLDER}
