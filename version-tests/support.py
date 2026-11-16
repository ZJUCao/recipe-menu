"""Helpers of the version tests: run ``recipe-menu`` as a user does, and read the results.

A test runs the program as a new process, the way Troy types it, and reads its exit code, its
output streams, and its files. No test imports ``recipe_menu``. Expected texts are tuples of lines
written out as literals in the ``texts_*`` modules, and ``text`` turns them into a string.
"""

import os
import re
import subprocess
import sysconfig
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "tests" / "data" / "example"
SCRIPT = Path(sysconfig.get_path("scripts")) / "recipe-menu.exe"
TIMEOUT = 120


class Result(NamedTuple):
    """The result of one process: its exit code and its two streams, with LF line ends."""

    code: int
    out: str
    err: str


def environment(home: Path, data: str | Path | None = None) -> dict[str, str]:
    """Gives the environment of a run: the home folder, and ``RECIPE_MENU_DATA`` only if named."""
    env = dict(os.environ)
    env.pop("RECIPE_MENU_DATA", None)
    env["USERPROFILE"] = str(home)
    env["HOME"] = str(home)
    if data is not None:
        env["RECIPE_MENU_DATA"] = str(data)
    return env


def start(command: Sequence[str | Path], cwd: Path, env: Mapping[str, str]) -> Result:
    """Starts a new process and gives its result, with CRLF read as LF."""
    done = subprocess.run(  # noqa: S603
        [str(part) for part in command],
        cwd=cwd,
        env=dict(env),
        capture_output=True,
        check=False,
        timeout=TIMEOUT,
    )
    out = done.stdout.decode("utf-8").replace("\r\n", "\n")
    err = done.stderr.decode("utf-8").replace("\r\n", "\n")
    return Result(done.returncode, out, err)


class World:
    """The folders of one scenario: a home folder, an empty working folder, and the data folder.

    Attributes:
        root: The temporary folder that holds all of them.
        home: The home folder, given to the program through ``USERPROFILE`` and ``HOME``.
        work: The current folder of every run. It starts empty.
        data: The default data folder, the folder ``recipe-menu`` in the home folder.
    """

    def __init__(self, root: Path) -> None:
        """Makes the home folder and the working folder under ``root``."""
        self.root = root
        self.home = root / "home"
        self.work = root / "work"
        self.data = self.home / "recipe-menu"
        self.home.mkdir(parents=True)
        self.work.mkdir()

    def run(self, *args: str | Path, data: str | Path | None = None) -> Result:
        """Runs ``recipe-menu`` with the arguments, as Troy types them.

        Args:
            *args: The arguments after ``recipe-menu``.
            data: The value of ``RECIPE_MENU_DATA``, or ``None`` to leave it out.
        """
        return start([SCRIPT, *args], self.work, environment(self.home, data))

    def copy_example(self, target: Path | None = None, shopping: bool = True) -> Path:
        """Copies ``tests/data/example/`` to the target, with LF line ends.

        It makes an empty ``shopping`` folder, unless ``shopping`` is false.

        Args:
            target: The new data folder, the default data folder when ``None``.
            shopping: Whether to make the empty ``shopping`` folder.
        """
        target = self.data if target is None else target
        for source in sorted(EXAMPLE.rglob("*")):
            path = target / source.relative_to(EXAMPLE)
            if source.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
        if shopping:
            (target / "shopping").mkdir()
        return target

    def init_folder(self) -> Path:
        """Runs ``recipe-menu init`` and gives the data folder that it made."""
        result = self.run("init")
        assert result.code == 0, result
        return self.data

    def clear_menus(self) -> None:
        """Deletes the menu files of the data folder and keeps the empty ``menus`` folder."""
        for path in (self.data / "menus").iterdir():
            path.unlink()


def text(lines: Sequence[str], data: str | Path, home: str | Path | None = None) -> str:
    """Joins the lines of an expected text with LF, ends it with LF, and fills in the folders."""
    joined = "\n".join(lines).replace("<data>", str(data))
    if home is not None:
        joined = joined.replace("<home>", str(home))
    return joined + "\n"


def check_result(
    world: World,
    result: Result,
    code: int,
    lines: Sequence[str],
    *,
    data: str | Path | None = None,
    report: bool = False,
) -> None:
    """Checks that a run exited with ``code`` and printed ``lines`` on the right stream.

    A message of an exit code 1 or 2 is on stderr, and any other output is on stdout. The report
    of ``check`` (``report=True``) is on stdout with every exit code. The other stream must stay
    empty.
    """
    expected = text(lines, world.data if data is None else data, world.home)
    if code in (1, 2) and not report:
        assert result == Result(code, "", expected)
    else:
        assert result == Result(code, expected, "")


def put(path: Path, lines: Sequence[str]) -> None:
    """Writes a file in UTF-8 without a byte order mark, with LF line ends."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_bytes(lines))


def file_bytes(lines: Sequence[str]) -> bytes:
    """Gives the bytes of a file of these lines: UTF-8 without a byte order mark, LF line ends."""
    return ("\n".join(lines) + "\n").encode("utf-8")


def read(path: Path) -> str:
    """Reads a file as UTF-8 and checks that it has no byte order mark and no CR."""
    data = path.read_bytes()
    assert not data.startswith(b"\xef\xbb\xbf"), f"{path} starts with a byte order mark"
    assert b"\r" not in data, f"{path} holds a CR"
    return data.decode("utf-8")


def change(path: Path, old: str, new: str) -> None:
    """Replaces the first ``old`` in a data file with ``new``, and keeps UTF-8 and LF."""
    content = read(path)
    assert old in content, f"{old!r} is not in {path}"
    path.write_bytes(content.replace(old, new, 1).encode("utf-8"))


def to_bom_crlf(root: Path) -> None:
    """Saves every file under ``root`` again in UTF-8 with a byte order mark and CRLF line ends."""
    for path in sorted(root.rglob("*")):
        if path.is_file():
            body = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            path.write_bytes(b"\xef\xbb\xbf" + body)


def cells(line: str) -> list[str]:
    """Splits a table line into its cells, at every run of 2 or more spaces."""
    return re.split(r"\s{2,}", line.strip())


class Snapshot(NamedTuple):
    """The files with their bytes and times, and the folders with their times."""

    files: dict[Path, tuple[bytes, int]]
    folders: dict[Path, int]


def snapshot(*roots: Path) -> Snapshot:
    """Records the bytes and modification time of every file, and the time of every folder."""
    files: dict[Path, tuple[bytes, int]] = {}
    folders: dict[Path, int] = {}
    for root in roots:
        for path in [root, *sorted(root.rglob("*"))]:
            if path.is_dir():
                folders[path] = path.stat().st_mtime_ns
            else:
                files[path] = (path.read_bytes(), path.stat().st_mtime_ns)
    return Snapshot(files, folders)


def today() -> date:
    """Gives the PC's date."""
    return datetime.now().astimezone().date()


def iso_week(day: date) -> str:
    """Gives the ISO week of a date as ``2026-W47``."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def on_one_day(root: Path, body: Callable[[World, str, str], None]) -> None:
    """Runs a scenario with ``this`` and ``next`` weeks from the date read just before it.

    ``body`` gets a fresh world, ``<T>`` (the ISO week of the PC's date), and ``<N>`` (the ISO week
    of the date 7 days later). When the date changes while the steps run, the scenario starts
    again in a new world. The scenario runs at most 3 times in all, and a run that crosses
    midnight is never judged. A failure of a run during which the date changed, whether an
    ``AssertionError`` or an ``OSError`` such as a missing file, starts the next run. The function
    raises ``AssertionError`` when the date changes in all 3 runs.
    """
    for attempt in range(3):
        before = today()
        world = World(root / f"attempt-{attempt}")
        try:
            body(world, iso_week(before), iso_week(before + timedelta(days=7)))
        except (AssertionError, OSError):
            if today() == before:
                raise
            continue
        if today() == before:
            return
    raise AssertionError("the PC's date changed during each of 3 runs of the scenario")
