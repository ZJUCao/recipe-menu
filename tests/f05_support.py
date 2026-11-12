"""Helpers and example values that the F05 tests share.

Nothing here makes a ``Command``, a ``Settings``, or a ``UsageError`` when the module is
imported, because the mock leaves out their checks. Functions and fixtures make them.
"""

import io
import os
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from pathlib import Path

from f03_support import put_bytes, write
from f05_texts import Msg, Result
from recipe_menu.app import Argument, Arguments, Command, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.text import (
    Message,
)

type Call = tuple[Context, Arguments]

TODAY = date(2026, 11, 10)
ROOT = Path(__file__).resolve().parents[1]
VERSION: str = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
    "version"
]
VERSION_LINE = f"recipe-menu {VERSION}\n"

# ---------------------------------------------------------------------- stand-in commands

V01 = ("INIT", "CHECK", "LIST", "SHOW", "SEARCH", "MENU_NEW", "MENU_SHOW", "SHOP")

type Spec = tuple[
    tuple[str, ...],
    Msg,
    tuple[str, str, bool, bool] | None,
    tuple[str, ...],
    FolderUse,
]

_SHOW_HELP: Msg = ("Show one recipe.", "查看一个菜谱。")
_SHOW_ARG = ("ID", "ID", True, False)
_WEEK_ARG = ("WEEK", "周", False, False)
_MENU_SHOW_HELP: Msg = ("Show a week menu.", "查看一个周菜单。")
_READ, _CHECK, _CREATE = FolderUse.READ, FolderUse.CHECK, FolderUse.CREATE

SPECS: dict[str, Spec] = {
    "INIT": (
        ("init",),
        ("Create the data folder with example data.", "创建数据文件夹和示例数据。"),
        None,
        (),
        _CREATE,
    ),
    "CHECK": (
        ("check",),
        ("Check every data file for mistakes.", "检查每个数据文件有没有错误。"),
        None,
        (),
        _CHECK,
    ),
    "LIST": (("list",), ("List the recipes.", "列出菜谱。"), None, ("--tag",), _READ),
    "SHOW": (("show",), _SHOW_HELP, _SHOW_ARG, ("--servings",), _READ),
    "SEARCH": (
        ("search",),
        ("Find recipes by name, ingredient, or tag.", "按名称、食材或标签找菜谱。"),
        ("WORD", "词", True, True),
        (),
        _READ,
    ),
    "MENU_NEW": (
        ("menu", "new"),
        ("Create an empty week menu.", "创建一个空的周菜单。"),
        _WEEK_ARG,
        (),
        _READ,
    ),
    "MENU_SHOW": (("menu", "show"), _MENU_SHOW_HELP, _WEEK_ARG, (), _READ),
    "SHOP": (
        ("shop",),
        ("Make the shopping list of a week menu.", "生成一个周菜单的购物清单。"),
        _WEEK_ARG,
        (),
        _READ,
    ),
    "TAGS": (
        ("tags",),
        ("List the tags.", "列出标签。"),
        ("TAG", "标签", False, True),
        (),
        _READ,
    ),
    "SHOW_TWO": (("show",), _SHOW_HELP, _SHOW_ARG, ("--servings", "--tag"), _READ),
    "SHOW_THREE": (("show",), _SHOW_HELP, _SHOW_ARG, ("--tag", "--servings", "--week"), _READ),
    "MENU_SUGGEST": (
        ("menu", "suggest"),
        ("Fill the empty meals of a week menu.", "填满一个周菜单里空着的餐次。"),
        _WEEK_ARG,
        (),
        _READ,
    ),
    "WIDE": (
        ("menu", "show"),
        _MENU_SHOW_HELP,
        ("WEEK", "一周的编号", False, False),
        (),
        _READ,
    ),
}


class Recorder:
    """The ``run`` of a stand-in command.

    It keeps each ``(context, arguments)`` that it gets, writes nothing unless ``action`` does,
    and returns ``code``.

    Attributes:
        calls: The calls so far, in order.
    """

    def __init__(self, code: int = 0, action: Callable[[Context], None] | None = None) -> None:
        """Starts a recorder with no calls.

        Args:
            code: The exit code that it returns.
            action: Called with the context after the call is recorded, to write or to raise.
        """
        self.calls: list[Call] = []
        self.code = code
        self.action = action

    def __call__(self, context: Context, arguments: Arguments) -> int:
        """Records the call, runs the action, and gives the exit code."""
        self.calls.append((context, arguments))
        if self.action is not None:
            self.action(context)
        return self.code


def make_command(name: str, run: Callable[[Context, Arguments], int]) -> Command:
    """Makes the stand-in command of a name from ``SPECS``, with a ``run``."""
    words, (en, zh), argument, options, folder = SPECS[name]
    made = None
    if argument is not None:
        made = Argument(Message(argument[0], argument[1]), argument[2], argument[3])
    return Command(words, Message(en, zh), run, made, options, folder)


class StandIns:
    """A set of stand-in commands, each with its recorder.

    Attributes:
        names: The names of the stand-ins, in the order of the help.
        recorders: The recorder of each name.
        commands: The commands, in the order of ``names``.
    """

    def __init__(
        self, names: Sequence[str] = V01, behave: Mapping[str, Recorder] | None = None
    ) -> None:
        """Makes the commands.

        Args:
            names: The names of ``SPECS`` to make, in order.
            behave: A recorder with its own behavior for some names. Other names get a plain one.
        """
        given = behave or {}
        self.names = tuple(names)
        self.recorders = {name: given.get(name) or Recorder() for name in self.names}
        self.commands = tuple(make_command(name, self.recorders[name]) for name in self.names)

    def calls(self, name: str) -> list[Call]:
        """Gives the calls that the stand-in of a name got."""
        return self.recorders[name].calls

    def nothing_ran(self) -> bool:
        """Tells whether every recorder is empty."""
        return all(not recorder.calls for recorder in self.recorders.values())

    def ran(self, name: str) -> Call:
        """Checks that the stand-in ran once and no other did, and gives its call."""
        for other, recorder in self.recorders.items():
            assert len(recorder.calls) == (1 if other == name else 0), other
        return self.recorders[name].calls[0]

    def snapshot(self) -> list[tuple[str, str, str, object, date, Arguments]]:
        """Gives each call as a tuple of the values that two runs must share."""
        return [
            (name, c.lang.value, str(c.folder.root), c.settings, c.today, a)
            for name, recorder in self.recorders.items()
            for c, a in recorder.calls
        ]


def run_main(
    home: Path,
    *argv: str,
    environ: Mapping[str, str] | None = None,
    kit: StandIns | None = None,
    commands: Sequence[Command] | None = None,
    today: date = TODAY,
) -> Result:
    """Runs ``main`` as a line of the test plan does and gives ``(code, out, err)``.

    Args:
        home: The home folder.
        *argv: The arguments.
        environ: The environment, ``{}`` when ``None``.
        kit: The stand-ins to run with, new v0.1 ones when ``None``.
        commands: The commands to pass, the commands of ``kit`` when ``None``.
        today: The date that ``main`` gets.
    """
    stand_ins = kit if kit is not None else StandIns()
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ={} if environ is None else environ,
        home=home,
        today=today,
        stdout=out,
        stderr=err,
        commands=stand_ins.commands if commands is None else commands,
    )
    return code, out.getvalue(), err.getvalue()


def in_folder(folder: Path) -> dict[str, str]:
    """Gives the environment that names the data folder."""
    return {"RECIPE_MENU_DATA": str(folder)}


# --------------------------------------------------------------------------- folders

FOLDER_SETTINGS: dict[str, str | None] = {
    "zh": 'language = "zh"\n',
    "broken": 'meals = ["lunch", "supper"]\n',
    "broken_zh": 'language = "zh"\nmeals = []\n',
    "bare": None,
}


def make_home(tmp_path: Path) -> Path:
    """Makes the empty home folder ``tmp_path / "home"``."""
    home = tmp_path / "home"
    home.mkdir()
    return home


def make_folder(tmp_path: Path, name: str) -> Path:
    """Makes a named data folder under ``tmp_path``: ``zh``, ``broken``, ``broken_zh``, ``bare``.

    ``missing`` is not made: it gives the path ``tmp_path / "missing"``.
    """
    path = tmp_path / name
    if name == "missing":
        return path
    path.mkdir()
    text = FOLDER_SETTINGS[name]
    if text is not None:
        write(path / "settings.toml", text)
    return path


def make_settings_folder(tmp_path: Path, name: str, text: str) -> Path:
    """Makes a folder under ``tmp_path`` whose ``settings.toml`` holds a text."""
    path = tmp_path / name
    path.mkdir()
    write(path / "settings.toml", text)
    return path


def copy_example(source: DataFolder, target: Path) -> Path:
    """Copies the example folder to ``target``, byte for byte, and gives ``target``."""
    for path in sorted(source.root.rglob("*")):
        goal = target / path.relative_to(source.root)
        if path.is_dir():
            goal.mkdir(parents=True, exist_ok=True)
        else:
            put_bytes(goal, path.read_bytes())
    return target


def record(root: Path) -> dict[str, bytes | None]:
    """Records the relative path and the bytes of every file under ``root``.

    A folder is recorded with ``None`` in place of its bytes.
    """
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(root.rglob("*"))
    }


def unreadable_name(tmp_path: Path) -> Path:
    """Gives a path whose name the system cannot look at, as ``os.path.isdir`` reports it."""
    if sys.platform == "win32":
        return tmp_path / "a?b"
    return tmp_path / ("a" * 256)


# ---------------------------------------------------------------- python -m recipe_menu


def run_module(
    tmp_path: Path, *argv: str, data: Path | None = None, home: Path | None = None
) -> Result:
    """Runs ``python -m recipe_menu`` in ``tmp_path`` and gives ``(code, stdout, stderr)``.

    The environment is a copy of ``os.environ`` without ``RECIPE_MENU_DATA``, with ``HOME`` and
    ``USERPROFILE`` set to the home folder and ``PYTHONIOENCODING`` set to ``ascii``.

    Args:
        tmp_path: The folder to run in.
        *argv: The arguments.
        data: The value of ``RECIPE_MENU_DATA``, or ``None`` to leave it out.
        home: The home folder, ``tmp_path / "home"`` when ``None``. It is made when missing.
    """
    home = tmp_path / "home" if home is None else home
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env.pop("RECIPE_MENU_DATA", None)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["PYTHONIOENCODING"] = "ascii"
    if data is not None:
        env["RECIPE_MENU_DATA"] = str(data)
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "recipe_menu", *argv],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        check=False,
        timeout=60,
    )
    out = done.stdout.decode("utf-8").replace("\r\n", "\n")
    err = done.stderr.decode("utf-8").replace("\r\n", "\n")
    return done.returncode, out, err


def go(
    home: Path,
    *argv: str,
    environ: Mapping[str, str] | None = None,
    names: Sequence[str] = V01,
    behave: Mapping[str, Recorder] | None = None,
) -> tuple[Result, StandIns]:
    """Runs ``main`` with new stand-ins and gives the result and the stand-ins.

    Args:
        home: The home folder.
        *argv: The arguments.
        environ: The environment, ``{}`` when ``None``.
        names: The names of the stand-ins to pass as the commands.
        behave: A recorder with its own behavior for some names.
    """
    kit = StandIns(names, behave)
    return run_main(home, *argv, environ=environ, kit=kit), kit


def assert_ran(kit: StandIns, name: str, lang: Lang, arguments: Arguments) -> None:
    """Checks that one stand-in ran once, in a language, with the arguments, and no other ran."""
    context, got = kit.ran(name)
    assert context.lang is lang
    assert got == arguments
