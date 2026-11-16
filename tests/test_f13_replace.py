"""Tests of F13 for replace_file: the example, a wrong call, a call that works, and a bad parent."""

import os
from pathlib import Path

import pytest

from f03_support import put_bytes
from f08_support import FOLDER, dangling_link, file_of, full_record, tree
from f11_support import assert_failed
from f13_support import folder_link, new_shop, shop_faults
from f13_texts import parent
from recipe_menu.datafile import DataFolder, FileCreation, FileOutcome, replace_file
from recipe_menu.lang import Lang

CREATED = FileCreation(FileOutcome.CREATED)
S = "recipe-menu/shopping"
Q = f"{S}/2026-W47.md"
T = f"{Q}.tmp"
MOVE = [f"unlink {T}", f"open {T}", f"move {T} {Q}"]
TEXT_2 = "# 2\n番茄 600 g\n"


def test_f13_t03_the_example_of_replace_file_holds(tmp_path: Path) -> None:
    """A new ``shopping/``, a file replaced, a folder at the path, a file at ``shopping``."""
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    folder = DataFolder(tmp / "recipe-menu")
    folder.root.mkdir()
    file = folder.shopping_file("2026-W47")
    assert replace_file(folder, file, "# 1\n") == CREATED
    assert file.read_bytes() == b"# 1\n"
    assert replace_file(folder, file, TEXT_2).outcome is FileOutcome.CREATED
    assert file.read_bytes() == TEXT_2.encode()
    assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]
    week48 = folder.shopping_file("2026-W48")
    week48.mkdir()
    blocked = replace_file(folder, week48, "# 3\n")
    assert blocked.outcome is FileOutcome.FAILED
    assert blocked.problem is not None
    assert (blocked.problem.file, blocked.problem.place) == (Path("shopping", "2026-W48.md"), None)
    assert blocked.problem.text(Lang.EN).startswith("The file cannot be written")
    assert blocked.left == ()
    assert sorted(path.name for path in folder.shopping.iterdir()) == ["2026-W47.md", "2026-W48.md"]
    other = DataFolder(tmp / "other")
    other.root.mkdir()
    other.shopping.write_text("", encoding="utf-8")
    failed = replace_file(other, other.shopping_file("2026-W47"), "# 1\n")
    assert failed.outcome is FileOutcome.FAILED
    assert failed.problem is not None
    assert failed.problem.text(Lang.EN) == parent("shopping")[0]
    assert other.shopping.read_bytes() == b""
    with pytest.raises(ValueError):
        replace_file(folder, tmp / "elsewhere.md", "")
    with pytest.raises(ValueError):
        replace_file(folder, folder.root, "")
    with pytest.raises(UnicodeEncodeError):
        replace_file(folder, file, "\udc80")
    assert tree(tmp) == {
        "recipe-menu": FOLDER,
        "recipe-menu/shopping": FOLDER,
        "recipe-menu/shopping/2026-W47.md": file_of(TEXT_2.encode("utf-8")),
        "recipe-menu/shopping/2026-W48.md": FOLDER,
        "other": FOLDER,
        "other/shopping": file_of(b""),
    }


def test_f13_t04_a_wrong_call_raises_before_the_disk_is_touched(tmp_path: Path) -> None:
    """A path outside the root, the root, a relative path, and a text that UTF-8 cannot encode."""
    base, folder = new_shop(tmp_path, "t04")
    q = folder.shopping_file("2026-W47")
    calls = [
        (ValueError, base / "elsewhere.md", ""),
        (ValueError, folder.root, ""),
        (ValueError, Path("shopping", "2026-W47.md"), ""),
        (UnicodeEncodeError, q, "\udc80"),
        (UnicodeEncodeError, q, "ok\n\ud800"),
        (UnicodeEncodeError, folder.root / "a" / "b.md", "\udc80"),
    ]
    for number, (error, path, text) in enumerate(calls, 1):
        before = tree(base)
        with shop_faults(base) as state, pytest.raises(error):
            replace_file(folder, path, text)
        assert (state.calls, state.listings) == ([], []), number
        assert tree(base) == before, number
    assert not folder.shopping.exists()
    assert not (folder.root / "a").exists()


def _fill(folder: DataFolder, files: dict[str, bytes]) -> None:
    """Makes ``F.shopping`` and writes the files into it."""
    folder.shopping.mkdir()
    for name, data in files.items():
        put_bytes(folder.shopping / name, data)


# Inputs 1, 3 to 6, and 10 of F13-T05: the files that ``F.shopping`` holds, and the text.
OLD = b"old\n"
PREPARED: dict[int, dict[str, bytes]] = {
    1: {},
    3: {"2026-W47.md": OLD},
    4: {"2026-W47.md": OLD, "2026-W47.md.tmp": b"half\n"},
    5: {},
    6: {},
    10: {"2026-W48.md": b"other\n", "notes.txt": b"x\n"},
}
TEXTS = {3: TEXT_2, 5: "", 6: "a\r\nb\n", 7: 'week = "2026-W47"\n\n[monday]\n'}
WRITTEN = {3: TEXT_2.encode("utf-8"), 5: b"", 6: b"a\r\nb\n", 7: b'week = "2026-W47"\n\n[monday]\n'}


def _t05_input(base: Path, folder: DataFolder, number: int) -> tuple[Path, list[str]]:
    """Makes input ``number`` of F13-T05 and gives the path to write and the expected record."""
    path = folder.shopping_file("2026-W47")
    record = MOVE
    if number in PREPARED:
        _fill(folder, PREPARED[number])
    elif number == 2:
        record = [f"mkdir {S}", *MOVE]
    elif number == 7:
        put_bytes(folder.menus / "2026-W47.toml", b'week = "2026-W47"\n')
        path = folder.menu_file("2026-W47")
        stem = "recipe-menu/menus/2026-W47.toml"
        record = [f"unlink {stem}.tmp", f"open {stem}.tmp", f"move {stem}.tmp {stem}"]
    elif number == 8:
        path = folder.root / "notes.md"
        stem = "recipe-menu/notes.md"
        record = [f"unlink {stem}.tmp", f"open {stem}.tmp", f"move {stem}.tmp {stem}"]
    else:
        (base / "synced").mkdir()
        folder_link(folder.shopping, base / "synced")
    return path, record


def test_f13_t05_a_call_that_works_replaces_the_file_through_a_temporary_file(
    tmp_path: Path,
) -> None:
    """Ten inputs: the folder, the temporary file, the bytes, the record, and ``CREATED``."""
    for number in range(1, 11):
        base, folder = new_shop(tmp_path, f"t05-{number}")
        path, record = _t05_input(base, folder, number)
        others = {}
        if number == 10:
            others = {
                n: (folder.shopping / n).stat().st_mtime_ns for n in ("2026-W48.md", "notes.txt")
            }
        with shop_faults(base) as state:
            creation = replace_file(folder, path, TEXTS.get(number, "# 1\n"))
        assert creation == CREATED, number
        assert state.calls == record, number
        assert state.listings == [], number
        assert path.read_bytes() == WRITTEN.get(number, b"# 1\n"), number
        assert not [entry for entry in base.rglob("*") if entry.name.endswith(".tmp")], number
        for name, mtime in others.items():
            assert (folder.shopping / name).stat().st_mtime_ns == mtime
        if number == 10:
            assert (folder.shopping / "2026-W48.md").read_bytes() == b"other\n"
            assert (folder.shopping / "notes.txt").read_bytes() == b"x\n"
        if number == 2:
            assert sorted(entry.name for entry in folder.shopping.iterdir()) == ["2026-W47.md"]
        if number == 9:
            assert [entry.name for entry in (base / "synced").iterdir()] == ["2026-W47.md"]
            assert folder.shopping.is_symlink() or os.path.isjunction(folder.shopping)


def _t06_input(base: Path, folder: DataFolder, number: int) -> tuple[Path, str, str]:
    """Makes input ``number`` of F13-T06 and gives the path, the problem's file and the folder."""
    if number == 1:
        put_bytes(folder.shopping, b"x\n")
    elif number == 2:
        dangling_link(folder.shopping)
    elif number == 3:
        put_bytes(folder.root / "notes.md", b"x\n")
        return folder.root / "notes.md" / "2026-W47.md", "notes.md/2026-W47.md", "notes.md"
    elif number == 4:
        put_bytes(folder.root / "a" / "b", b"")
        return folder.root / "a" / "b" / "c.md", "a/b/c.md", str(Path("a", "b"))
    return folder.shopping_file("2026-W47"), "shopping/2026-W47.md", "shopping"


def test_f13_t06_something_other_than_a_folder_at_the_parent_gives_failed(tmp_path: Path) -> None:
    """A file, a dangling link, and a file higher up: ``PARENT_NOT_A_FOLDER``, nothing touched."""
    for number in range(1, 5):
        base, folder = new_shop(tmp_path, f"t06-{number}")
        path, file, shown = _t06_input(base, folder, number)
        before = full_record(base)
        with shop_faults(base) as state:
            creation = replace_file(folder, path, "x")
        assert_failed(creation, file, parent(shown))
        assert (state.calls, state.listings) == ([], []), number
        assert full_record(base) == before, number
