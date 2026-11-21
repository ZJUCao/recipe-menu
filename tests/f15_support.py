"""Helpers that the F15 tests share: the calls of ``add``, the answer streams, and the changes.

The module runs the command line with a stream of answers, and makes the streams that stand in for
a console, for a pipe that has no answers to give, for another window that changes the data
folder while the command waits, and for Ctrl+C. It starts ``python -m recipe_menu`` with bytes on
its standard input, holds the commands of the help in the order of the help, the lists of answers,
and the named changes of the data folders. Nothing here calls an interface of F15 when the module
is imported, so the test files import against the mock and against a broken implementation. The
expected texts are in ``f15_texts``.
"""

import io
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

import pytest

from f03_support import put_bytes
from f05_support import TODAY, copy_example
from f05_texts import Result
from f07_changes import edit
from f08_support import Rule
from f13_support import Change, shop_faults
from recipe_menu.app import Command
from recipe_menu.cli import main
from recipe_menu.commands.add import ADD_COMMAND
from recipe_menu.commands.menu import MENU_SHOW_COMMAND
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.commands.suggest import MENU_SUGGEST_COMMAND
from recipe_menu.datafile import DataFolder
from v01_commands import V01_COMMANDS

type Answers = Sequence[str]

# ---------------------------------------------------------------- the commands of the help


def _ten_commands() -> tuple[Command, ...]:
    """Gives the commands of the help of ten, in its order.

    They are those of v0.1 with ``add`` after ``search`` and ``menu suggest`` after ``menu show``.
    """
    commands = list(V01_COMMANDS)
    commands.insert(commands.index(SEARCH_COMMAND) + 1, ADD_COMMAND)
    commands.insert(commands.index(MENU_SHOW_COMMAND) + 1, MENU_SUGGEST_COMMAND)
    return tuple(commands)


TEN_COMMANDS = _ten_commands()

# ---------------------------------------------------------------- the answers


def many(value: str | Answers) -> list[str]:
    """Gives one answer, or the answers of a question that is asked again, as a list."""
    return [value] if isinstance(value, str) else list(value)


def answers(
    recipe_id: str = "new-dish",
    *,
    zh_name: str | Answers = "新菜",
    en_name: str | Answers = "New dish",
    servings: str | Answers = "",
    tags: str | Answers = "quick",
    ingredients: Answers = ("番茄 300 g",),
    zh_steps: Answers = ("番茄切块。",),
    en_steps: Answers = ("Cut the tomatoes.",),
) -> list[str]:
    """Gives BASE of the test plan, with the answers of some questions replaced.

    The three lists get the empty answer that ends each of them. A question that is asked again
    takes all the answers that it gets, in order.
    """
    return [
        recipe_id,
        *many(zh_name),
        *many(en_name),
        *many(servings),
        *many(tags),
        *ingredients,
        "",
        *zh_steps,
        "",
        *en_steps,
        "",
    ]


BASE = answers()

S09 = [
    "garlic-broccoli",
    "蒜蓉西兰花",
    "Garlic broccoli",
    "",
    "快手, 素",
    "西兰花 300 g",
    "大蒜 4 瓣",
    "橄榄油 1 tbsp",
    "食用油 1 tbsp",
    "盐 适量",
    "",
    "西兰花切小朵，焯水 1 分钟，捞出沥干。",
    "大蒜切末，热油爆香。",
    "倒入西兰花翻炒，加盐调味。",
    "",
    "Cut the broccoli into florets. Blanch them for 1 minute and drain.",
    "Mince the garlic, and fry it in the hot oil until fragrant.",
    "Add the broccoli, stir-fry it, and season with salt.",
    "",
]
S10 = [
    "egg-fried-rice",
    "蛋炒饭",
    "Egg fried rice",
    "0",
    "two",
    "3",
    "breakfast",
    "quick, staple",
    "Rice 1 cups",
    "Rice 300 g",
    "Egg 3",
    "Peanut 30 g",
    "Scallion 1 stalk",
    "Salt to taste",
    "Cooking oil 2 tbsp",
    "",
    "鸡蛋打散。",
    "热油炒蛋，加米饭和葱花翻炒。",
    "",
    "Beat the eggs.",
    "Scramble the eggs, then stir-fry them with the rice and scallion.",
    "",
]
PARTLY = [
    "scallion-egg",
    "葱花蛋",
    "",
    "",
    "快手，quick",
    "鸡蛋 3",
    "葱 2",
    "",
    "鸡蛋打散，加葱花煎熟。",
    "",
    "",
]
ESCAPES = [
    "odd-text",
    '老"家"\\菜',
    'Home\tstyle \x00\x01\x10 "best"',
    "",
    "素",
    "番茄 300 g",
    "",
    "第一行\u2028第二行",
    '加 1 勺"糖"\u3000和盐。',
    "",
    'Use C:\\path and "x".',
    "",
]
PT01_ANSWERS = [
    "size-check",
    "规模检查",
    "Size check",
    "",
    "quick",
    "食材300 100 g",
    "食材150 适量",
    "",
    "把食材洗净切好。",
    "",
    "Wash and cut the ingredients.",
    "",
]

# ---------------------------------------------------------------- the answer streams


def lines_of(texts: Answers) -> str:
    """Gives the text of an input stream: each answer followed by a line break."""
    return "".join(f"{text}\n" for text in texts)


def plain(texts: Answers) -> io.StringIO:
    """Gives the plain stream of answers, whose ``isatty()`` gives false."""
    return io.StringIO(lines_of(texts))


class Terminal(io.StringIO):
    """A stream of answers whose ``isatty()`` gives true, as a console's does."""

    def isatty(self) -> bool:
        """Gives true."""
        return True


def terminal(texts: Answers) -> Terminal:
    """Gives a terminal stream of answers."""
    return Terminal(lines_of(texts))


class Watched(io.StringIO):
    """A stream with no answers that fails the case when anything reads it."""

    def read(self, size: int | None = -1, /) -> str:
        """Fails the case."""
        pytest.fail("the input was read with read")

    def readline(self, size: int | None = -1, /) -> str:
        """Fails the case."""
        pytest.fail("the input was read with readline")

    def readlines(self, hint: int = -1, /) -> list[str]:
        """Fails the case."""
        pytest.fail("the input was read with readlines")

    def __iter__(self) -> "Watched":
        """Fails the case."""
        pytest.fail("the input was read by iteration")

    def __next__(self) -> str:
        """Fails the case."""
        pytest.fail("the input was read by iteration")


class Hooked(io.StringIO):
    """A stream that runs a change on the data folder just before it gives its k-th line.

    Attributes:
        count: The number of lines that were asked for.
    """

    def __init__(self, texts: Answers, root: Path, change: Change, at: int | None = None) -> None:
        """Makes the stream.

        Args:
            texts: The answers.
            root: The data folder, which the change gets.
            change: The change, run as another program would run it.
            at: The number of the line, counted from 1. The last line when ``None``.
        """
        super().__init__(lines_of(texts))
        self._root = root
        self._change = change
        self._at = len(texts) if at is None else at
        self.count = 0

    def readline(self, size: int | None = -1, /) -> str:
        """Runs the change before it gives the line that the change comes before."""
        self.count += 1
        if self.count == self._at:
            self._change(self._root)
        return super().readline(size)


class Stopping(io.StringIO):
    """A stream that raises ``KeyboardInterrupt`` in place of its k-th line."""

    def __init__(self, texts: Answers, at: int) -> None:
        """Makes the stream. ``at`` is the number of the line, counted from 1."""
        super().__init__(lines_of(texts))
        self._at = at
        self._count = 0

    def readline(self, size: int | None = -1, /) -> str:
        """Gives the next line, or raises ``KeyboardInterrupt`` in place of the k-th."""
        self._count += 1
        if self._count == self._at:
            raise KeyboardInterrupt
        return super().readline(size)


class FlushOut(io.StringIO):
    """An output stream that records its whole text at each flush.

    Attributes:
        last: The text of the stream at its last flush.
    """

    def __init__(self) -> None:
        """Makes an empty stream."""
        super().__init__()
        self.last = ""

    def flush(self) -> None:
        """Records the text."""
        self.last = self.getvalue()
        super().flush()


class RecordingIn(io.StringIO):
    """An input stream that records, at each read, the text of an output stream.

    Attributes:
        seen: For each read, the text of the output stream and its text at its last flush.
    """

    def __init__(self, texts: Answers, out: FlushOut) -> None:
        """Makes the stream of the answers that watches ``out``."""
        super().__init__(lines_of(texts))
        self._out = out
        self.seen: list[tuple[str, str]] = []

    def readline(self, size: int | None = -1, /) -> str:
        """Records the output stream, and gives the next line."""
        self.seen.append((self._out.getvalue(), self._out.last))
        return super().readline(size)


# ---------------------------------------------------------------- the calls


def _root(folder: DataFolder | Path) -> Path:
    """Gives the path of a data folder."""
    return folder.root if isinstance(folder, DataFolder) else folder


def main_call(home: Path, argv: Sequence[str], stdin: TextIO | None) -> Result:
    """Runs ``main`` with new streams on a date, and gives ``(code, out, err)``.

    A ``KeyboardInterrupt`` that leaves ``main`` fails the case, as ``call_main`` of
    ``f08_support`` does.
    """
    out, err = io.StringIO(), io.StringIO()
    try:
        code = main(
            list(argv),
            environ={},
            home=home,
            today=TODAY,
            stdout=out,
            stderr=err,
            stdin=stdin,
        )
    except KeyboardInterrupt:
        pytest.fail("a KeyboardInterrupt left main")
    return code, out.getvalue(), err.getvalue()


def _stream(source: Answers | TextIO) -> TextIO:
    """Gives the plain stream of a list of answers, or the stream that it already is."""
    return plain(source) if isinstance(source, list | tuple) else source


def add(
    home: Path, folder: DataFolder | Path | None, source: Answers | TextIO, *extra: str
) -> Result:
    """Runs ``add --data FOLDER`` and the extra words, with answers or a stream as the input.

    Args:
        home: The home folder.
        folder: The data folder, or ``None`` for a line with no ``--data``.
        source: The list of answers, or the stream to pass as ``stdin``.
        *extra: The words after ``--data FOLDER``, such as ``--lang`` and ``zh``.
    """
    argv = ["add"]
    if folder is not None:
        argv += ["--data", str(_root(folder))]
    return main_call(home, [*argv, *extra], _stream(source))


def line(
    home: Path, folder: DataFolder | Path | None, source: Answers | TextIO, *argv: str
) -> Result:
    """Runs a command line with ``--data FOLDER`` at its end, and the input of ``add``."""
    full = list(argv)
    if folder is not None:
        full += ["--data", str(_root(folder))]
    return main_call(home, full, _stream(source))


def traced_add(
    home: Path,
    folder: DataFolder,
    source: Answers | TextIO,
    *rules: Rule,
    extra: Sequence[str] = (),
) -> tuple[Result, list[str], list[str]]:
    """Runs ``add`` in the fault harness, and gives the result, the calls, and the listings."""
    with shop_faults(folder.root, *rules) as state:
        result = add(home, folder, source, *extra)
    return result, state.calls, state.listings


def pipe_module(tmp_path: Path, data: bytes, *argv: str) -> Result:
    """Runs ``python -m recipe_menu`` with bytes on its standard input, which it then closes.

    The run is that of ``run_module`` of ``f05_support``: the current folder is ``tmp_path``,
    ``HOME`` and ``USERPROFILE`` name ``tmp_path / "home"``, and ``PYTHONIOENCODING`` is
    ``ascii``.
    """
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env.pop("RECIPE_MENU_DATA", None)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["PYTHONIOENCODING"] = "ascii"
    done = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "recipe_menu", *argv],
        cwd=tmp_path,
        env=env,
        input=data,
        capture_output=True,
        check=False,
        timeout=60,
    )
    out = done.stdout.decode("utf-8").replace("\r\n", "\n")
    err = done.stderr.decode("utf-8").replace("\r\n", "\n")
    return done.returncode, out, err


# ---------------------------------------------------------------- the data folders


def fresh(source: DataFolder, tmp_path: Path, name: str, *changes: Change) -> DataFolder:
    """Makes a new example at ``tmp_path / name``, applies the changes, and gives its folder.

    The copy is of ``source`` as it is now, so ``source`` must be a pristine example that was
    copied before any case ran ``add`` in the fixture.
    """
    root = copy_example(source, tmp_path / name)
    for change in changes:
        change(root)
    return DataFolder(root)


def listing(*extra: str) -> list[str]:
    """Gives the sorted names of the example's seven recipes and the extra names."""
    names = ["choy-sum", "cola-wings", "mapo-tofu", "red-braised-pork", "rice", "tomato-egg"]
    return sorted([*(f"{name}.toml" for name in names), "tomato-egg-noodles.toml", *extra])


def recipe_names(folder: DataFolder) -> list[str]:
    """Gives the sorted names of the entries of ``recipes/``, as the system keeps them."""
    return sorted(path.name for path in (folder.root / "recipes").iterdir())


def no_tomato(root: Path) -> None:
    """Deletes the tomato from ``catalog.toml``, which leaves no error in the catalog."""
    edit(root / "catalog.toml", '  { zh = "番茄", en = "Tomato", category = "produce" },\n', "")


def entry(name: str) -> Change:
    """Makes the change that writes the file ``recipes/NAME`` with the bytes of ``mine`` and LF."""

    def make(root: Path) -> None:
        """Writes the file."""
        put_bytes(root / "recipes" / name, b"mine\n")

    return make


def folder_new_dish(root: Path) -> None:
    """Makes the empty folder ``recipes/new-dish.toml``."""
    (root / "recipes" / "new-dish.toml").mkdir()
