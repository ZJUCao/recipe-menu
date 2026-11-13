"""Helpers and expected texts that the F08 tests share.

The module holds the fault harness, the steps of ``create_data_folder``, the trees of a folder,
the links and hidden files, and the message from the system. The expected texts of the test
plan are in ``f08_texts``. It calls no interface of F08 and makes no ``Creation`` when it is
imported. At import it holds only texts, numbers, and functions.
"""

import builtins
import errno
import io
import os
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from f03_support import put_bytes
from f07_support import call
from f08_texts import (
    FILE_EXISTS,
    FILE_WRITE_DENIED,
    FOLDER_CREATE_DENIED,
    FOLDER_EXISTS,
    Msg,
    Result,
    file_error,
    folder_error,
)
from recipe_menu.datafile import CreationOutcome, DataFolder, Severity
from recipe_menu.lang import Lang

type Entry = tuple[str, bytes | None]
type Step = tuple[str, Path]
type Effect = Callable[[], BaseException]

EXAMPLE = Path(__file__).parent / "data" / "example"

# ---------------------------------------------------------------- the exceptions of the plan

DENIED: Effect = partial(PermissionError, errno.EACCES, "Permission denied")
IO: Effect = partial(OSError, errno.EIO, "Input/output error")
NO_SPACE: Effect = partial(OSError, errno.ENOSPC, "No space left on device")
CTRL_C: Effect = KeyboardInterrupt
BUG: Effect = partial(RuntimeError, "bug")
EMPTY_IO: Effect = partial(OSError, errno.EIO, "")

# ---------------------------------------------------------------- the fault harness


@dataclass(frozen=True)
class Rule:
    """One rule of the fault harness.

    Attributes:
        kind: ``mkdir``, ``rmdir``, ``unlink``, ``open``, ``write``, or ``list``.
        path: The path that the rule names.
        effect: Makes the exception to raise, or ``None`` for ``race``.
        how: ``raise``, ``race``, or ``after``.
    """

    kind: str
    path: Path
    effect: Effect | None = None
    how: str = "raise"


def rule(kind: str, path: Path, effect: Effect | None = None, how: str = "raise") -> Rule:
    """Makes a ``Rule``: ``rule("mkdir", R / "menus", DENIED)`` is ``mkdir R/menus: DENIED``."""
    return Rule(kind, path, effect, how)


class _HalfFile:
    """A file whose first write puts down half of its text and then raises."""

    def __init__(self, real: Any, effect: Effect) -> None:
        """Wraps the real file that an ``open`` gave."""
        self._real = real
        self._effect = effect

    def __getattr__(self, name: str) -> Any:
        """Passes every other call to the real file."""
        return getattr(self._real, name)

    def __enter__(self) -> "_HalfFile":
        """Gives the wrapper, as a file does."""
        return self

    def __exit__(self, *exc: object) -> Any:
        """Closes the real file."""
        return self._real.__exit__(*exc)

    def write(self, text: str) -> int:
        """Writes the first half of the text, flushes it, and raises."""
        self._real.write(text[: len(text) // 2])
        self._real.flush()
        raise self._effect()


class Faults:
    """The record of the calls on the paths under ``base``, and the rules of one harness.

    Attributes:
        calls: The calls in order, each as a kind and the path relative to ``base``.
        listings: The paths of the listings, relative to ``base``.
        halves: The files that a ``write`` rule gave.
    """

    def __init__(self, base: Path, rules: Sequence[Rule]) -> None:
        """Takes the originals of the functions before they are replaced."""
        self.base = base
        self.calls: list[str] = []
        self.listings: list[str] = []
        self.halves: list[_HalfFile] = []
        self._rules = [(item.kind, self._rel(item.path), item) for item in rules]
        names = ("mkdir", "rmdir", "unlink", "remove", "scandir", "listdir")
        self._os = {name: getattr(os, name) for name in names}
        self._open = io.open

    def _rel(self, path: object) -> str | None:
        """Gives the path relative to ``base`` with ``/``, or ``None`` for another path."""
        if not isinstance(path, str | os.PathLike):
            return None
        try:
            return Path(path).relative_to(self.base).as_posix()  # type: ignore[arg-type]
        except ValueError:
            return None

    def _find(self, kind: str, rel: str) -> Rule | None:
        """Finds the rule of a kind and a path."""
        for rule_kind, rule_rel, item in self._rules:
            if rule_kind == kind and rule_rel == rel:
                return item
        return None

    def _make_other(self, kind: str, path: Any) -> None:
        """Creates the entry of another program: a folder, or a file that holds ``mine``."""
        if kind == "mkdir":
            self._os["mkdir"](path)
        else:
            with self._open(path, "xb") as handle:
                handle.write(b"mine\n")

    def _run(self, kind: str, path: object, original: Callable[[], Any]) -> Any:
        """Records a call, and applies the rule that names it."""
        rel = self._rel(path)
        if rel is None:
            return original()
        self.calls.append(f"{kind} {rel}")
        found = self._find(kind, rel)
        if found is None:
            return original()
        if found.how == "race":
            self._make_other(kind, path)
            return original()
        assert found.effect is not None
        if found.how == "after":
            result = original()
            if kind == "open":
                result.close()
        raise found.effect()

    def _list(self, path: object, original: Callable[[], Any]) -> Any:
        """Records a listing, and applies the rule that names it."""
        rel = self._rel(path)
        if rel is None:
            return original()
        self.listings.append(rel)
        found = self._find("list", rel)
        if found is not None and found.effect is not None:
            raise found.effect()
        return original()

    def mkdir(self, path: Any, *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``os.mkdir``."""
        return self._run("mkdir", path, lambda: self._os["mkdir"](path, *args, **kwargs))

    def rmdir(self, path: Any, *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``os.rmdir``."""
        return self._run("rmdir", path, lambda: self._os["rmdir"](path, *args, **kwargs))

    def unlink(self, path: Any, *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``os.unlink``."""
        return self._run("unlink", path, lambda: self._os["unlink"](path, *args, **kwargs))

    def remove(self, path: Any, *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``os.remove``."""
        return self._run("unlink", path, lambda: self._os["remove"](path, *args, **kwargs))

    def scandir(self, path: Any = ".") -> Any:
        """Stands in for ``os.scandir``."""
        return self._list(path, lambda: self._os["scandir"](path))

    def listdir(self, path: Any = ".") -> Any:
        """Stands in for ``os.listdir``."""
        return self._list(path, lambda: self._os["listdir"](path))

    def open(self, file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``io.open`` and ``builtins.open``."""
        kind = "open" if "x" in mode else "read"
        handle = self._run(kind, file, lambda: self._open(file, mode, *args, **kwargs))
        rel = self._rel(file)
        found = self._find("write", rel) if kind == "open" and rel is not None else None
        if found is None or found.effect is None:
            return handle
        half = _HalfFile(handle, found.effect)
        self.halves.append(half)
        return half


@contextmanager
def faults(base: Path, *rules: Rule) -> Iterator[Faults]:
    """Replaces the calls of design 3.2 for one call, and puts them back when it closes.

    Args:
        base: The folder whose paths the harness records.
        *rules: The rules to apply.

    Yields:
        The ``Faults`` with the record and the listings.
    """
    state = Faults(base, rules)
    with pytest.MonkeyPatch.context() as patch:
        for name in ("mkdir", "rmdir", "unlink", "remove", "scandir", "listdir"):
            patch.setattr(os, name, getattr(state, name))
        patch.setattr(io, "open", state.open)
        patch.setattr(builtins, "open", state.open)
        yield state


def call_main(home: Path, argv: Sequence[str], environ: Mapping[str, str] | None = None) -> Result:
    """Runs ``main`` as ``call`` does, and turns a ``KeyboardInterrupt`` into a failure."""
    try:
        return call(home, argv, environ)
    except KeyboardInterrupt:
        pytest.fail("KeyboardInterrupt left main")


def init(home: Path, *argv: str, folder: Path | str | None = None) -> Result:
    """Runs ``init`` with the arguments, in a folder when it is given."""
    full = ["init", *argv]
    if folder is not None:
        full += ["--data", str(folder)]
    return call_main(home, full)


# ---------------------------------------------------------------- the steps of 3.2


def rel(base: Path, path: Path) -> str:
    """Gives a path relative to ``base``, with ``/``."""
    return path.relative_to(base).as_posix()


def items(root: Path) -> tuple[tuple[Path, ...], tuple[tuple[Path, str], ...]]:
    """Gives ``ITEMS`` of the test plan for a data folder: its three folders and four files."""
    folder = DataFolder(root)
    folders = (folder.recipes, folder.menus, folder.shopping)
    files = (
        (folder.settings, "s\n"),
        (folder.catalog, "c\n"),
        (folder.pantry, "p\n"),
        (folder.recipe_file("tomato-egg"), "t\n"),
    )
    return folders, files


def make_steps(
    root: Path, folders: Sequence[Path], files: Sequence[tuple[Path, str]]
) -> list[Step]:
    """Gives the steps of a call: each missing folder from the top, the folders, the files."""
    above = []
    path = root
    while not os.path.lexists(path):
        above.append(path)
        path = path.parent
    steps = [("mkdir", missing) for missing in reversed(above)]
    steps += [("mkdir", folder) for folder in folders]
    return steps + [("open", file) for file, _ in files]


def record_of(base: Path, steps: Sequence[Step], attempted: int, created: int) -> list[str]:
    """Gives the record of a call.

    Args:
        base: The folder of the record.
        steps: The steps of the call.
        attempted: The number of steps whose call the harness saw.
        created: The number of leading steps that count as created, which the removal undoes
            from the last.
    """
    undo = {"mkdir": "rmdir", "open": "unlink"}
    record = [f"{kind} {rel(base, path)}" for kind, path in steps[:attempted]]
    return record + [f"{undo[kind]} {rel(base, path)}" for kind, path in reversed(steps[:created])]


def problem_file(root: Path, path: Path) -> str:
    """Gives the file of a problem at a path: ``.`` at the data folder or above it."""
    if path == root or path in root.parents:
        return "."
    return path.relative_to(root).as_posix()


# ---------------------------------------------------------------- the checks of a result


def assert_failed(creation: Any, file: str, msg: Msg, left: Sequence[Path] = ()) -> None:
    """Checks a failed ``Creation``: the problem's file and message, and ``left``."""
    assert creation.outcome is CreationOutcome.FAILED, creation
    problem = creation.problem
    assert problem is not None
    assert problem.severity is Severity.ERROR
    assert str(problem.file) == str(Path(*file.split("/")))
    assert problem.place is None
    assert (problem.text(Lang.EN), problem.text(Lang.ZH)) == msg
    assert tuple(str(path) for path in creation.left) == tuple(str(path) for path in left)


def system_message(kind: str, path: Path | str) -> Msg:
    """Gives the message from the system for ``os.mkdir`` (kind ``folder``) or ``open`` of a file.

    The call is made here, before the call that a test checks. It must raise an ``OSError`` and
    create nothing. The row of the error table comes from the class of the error, and the
    reason from its ``strerror``, or the name of its class when that is ``None`` or empty.
    """
    folder = kind == "folder"
    try:
        if folder:
            Path(path).mkdir()
        else:
            with Path(path).open("x", encoding="utf-8"):
                pass
    except FileExistsError:
        message = FOLDER_EXISTS if folder else FILE_EXISTS
    except PermissionError:
        message = FOLDER_CREATE_DENIED if folder else FILE_WRITE_DENIED
    except OSError as error:
        reason = error.strerror or type(error).__name__
        message = folder_error(reason) if folder else file_error(reason)
    else:
        raise AssertionError(f"{path} did not raise")
    assert not os.path.lexists(path)
    return message


# ---------------------------------------------------------------- trees and records

FOLDER: Entry = ("folder", None)
LINK: Entry = ("link", None)


def file_of(data: bytes) -> Entry:
    """Gives the entry of a file that holds the bytes."""
    return ("file", data)


def _entry(path: Path) -> Entry:
    """Gives the kind of an entry, with the bytes of a file. A link is never followed."""
    if path.is_symlink() or os.path.isjunction(path):
        return LINK
    if path.is_dir():
        return FOLDER
    return file_of(path.read_bytes())


def _walk(root: Path, folder: Path, found: dict[str, Entry]) -> None:
    """Adds each entry under a folder to ``found``, and goes into the folders."""
    with os.scandir(folder) as scan:
        paths = sorted(Path(item.path) for item in scan)
    for path in paths:
        found[rel(root, path)] = entry = _entry(path)
        if entry == FOLDER:
            _walk(root, path, found)


def tree(root: Path) -> dict[str, Entry]:
    """Gives the tree of a folder: each entry under it, by its relative path, with its kind."""
    found: dict[str, Entry] = {}
    _walk(root, root, found)
    return found


def full_record(root: Path) -> dict[str, tuple[Entry, int]]:
    """Gives the tree of a folder with the ``st_mtime_ns`` of each entry."""
    return {key: (entry, os.lstat(root / key).st_mtime_ns) for key, entry in tree(root).items()}


def under(prefix: str, entries: Mapping[str, Entry]) -> dict[str, Entry]:
    """Moves a tree into a folder of its own, which the result holds too."""
    return {prefix: FOLDER} | {f"{prefix}/{key}": entry for key, entry in entries.items()}


def _example_bytes(name: str) -> bytes:
    """Gives a file of the example folder as UTF-8 with LF line ends."""
    return (EXAMPLE / name).read_text(encoding="utf-8").encode("utf-8")


def new_tree(zh: bool = False) -> dict[str, Entry]:
    """Gives the tree of a new data folder, from the files of ``tests/data/example/``."""
    settings = _example_bytes("settings.toml")
    if zh:
        settings = settings.replace(b'language = "en"', b'language = "zh"')
    return {
        "settings.toml": file_of(settings),
        "catalog.toml": file_of(_example_bytes("catalog.toml")),
        "pantry.toml": file_of(_example_bytes("pantry.toml")),
        "recipes": FOLDER,
        "recipes/tomato-egg.toml": file_of(_example_bytes("recipes/tomato-egg.toml")),
        "menus": FOLDER,
        "shopping": FOLDER,
    }


def dangling_link(path: Path) -> None:
    """Makes a link at ``path`` that leads to no folder: a symbolic link, or a junction."""
    if sys.platform == "win32":
        import _winapi  # noqa: PLC0415 - exists on Windows only

        target = path.with_name(path.name + "-target")
        target.mkdir()
        _winapi.CreateJunction(str(target), str(path))
        target.rmdir()
    else:
        path.symlink_to(path.with_name(path.name + "-nowhere"))
    assert os.path.lexists(path)
    assert not path.is_dir()


def hide(path: Path, system: bool = False) -> None:
    """Hides a file with its attributes on Windows. A leading dot hides it on Linux."""
    if sys.platform == "win32":
        import ctypes  # noqa: PLC0415 - used on Windows only

        assert ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x6 if system else 0x2)


def fill_entry(root: Path, number: int) -> None:
    """Puts the entry of case ``number`` of F08-T05 and F08-T17 into the folder ``root``.

    1 is the file ``notes.txt``. 2 is the empty folder ``menus``. 3 is ``old/a.toml``, empty.
    4 is the hidden empty file ``.keep``. 5 is the hidden and system file ``desktop.ini``. 6 is
    a dangling link ``old``. The folder ``root`` is made when it is missing.
    """
    root.mkdir(exist_ok=True)
    if number == 1:
        put_bytes(root / "notes.txt", b"Ideas\n")
    elif number == 2:
        (root / "menus").mkdir()
    elif number == 3:
        put_bytes(root / "old" / "a.toml", b"")
    elif number == 4:
        put_bytes(root / ".keep", b"")
        hide(root / ".keep")
    elif number == 5:
        put_bytes(root / "desktop.ini", b"")
        hide(root / "desktop.ini", system=True)
    else:
        dangling_link(root / "old")
