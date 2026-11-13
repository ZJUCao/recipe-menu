"""Helpers that the F09 tests share: calls, the named changes, and the extra recipes.

Nothing here calls an interface of F09 when the module is imported. Functions call ``main`` or a
command's ``run``, and change the folders of a case. The expected texts are in ``f09_texts``. The
module reuses ``TODAY`` and ``copy_example`` of ``f05_support``, ``Result`` of ``f05_texts``,
``call`` of ``f07_support``, ``edit``, ``mapo_mistake``, and ``servings_zero`` of ``f07_changes``,
``Prob`` of ``f07_texts``, ``write`` of ``f03_support``, and ``pair`` of ``f09_texts``. The F09
tests import ``make_home``, ``run_module``, ``snapshot``, ``make_init``, ``faults``, and the other
named changes from their own modules.
"""

import io
import itertools
import re
import shutil
from collections.abc import Callable, Mapping
from datetime import date
from pathlib import Path

from f03_support import write
from f05_support import TODAY, copy_example
from f05_texts import Result
from f07_changes import edit, mapo_mistake, servings_zero
from f07_support import call
from f07_texts import Prob
from f09_texts import EN, ZH, pair
from recipe_menu.app import Arguments, Command, Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

# ---------------------------------------------------------------- calls


def at(
    home: Path,
    folder: Path | DataFolder | None,
    *argv: str,
    environ: Mapping[str, str] | None = None,
) -> Result:
    """Runs ``main`` with the real commands, as the test plan's conventions say.

    Args:
        home: The home folder.
        folder: The data folder, or ``None`` for a line with no ``--data``.
        *argv: The command line before ``--data``.
        environ: The environment, ``{}`` when ``None``.
    """
    full = list(argv)
    if folder is not None:
        root = folder.root if isinstance(folder, DataFolder) else folder
        full += ["--data", str(root)]
    return call(home, full, environ)


def new_context(
    lang: Lang, folder: DataFolder, settings: Settings | None = None, today: date = TODAY
) -> tuple[Context, io.StringIO, io.StringIO]:
    """Makes a ``Context`` with new streams, and gives it with its output and error streams."""
    out, err = io.StringIO(), io.StringIO()
    context = Context(lang, folder, Settings() if settings is None else settings, out, err, today)
    return context, out, err


def run_command(
    command: Command,
    lang: Lang,
    folder: DataFolder,
    arguments: Arguments,
    settings: Settings | None = None,
    *,
    today: date = TODAY,
) -> Result:
    """Calls ``command.run`` with a new ``Context`` and new streams, and gives the result."""
    context, out, err = new_context(lang, folder, settings, today)
    code = command.run(context, arguments)
    return code, out.getvalue(), err.getvalue()


def made(example: DataFolder, tmp_path: Path, name: str, *changes: Callable[[Path], None]) -> Path:
    """Makes a new example at ``tmp_path / name`` and applies the changes to it, in order."""
    root = copy_example(example, tmp_path / name)
    for change in changes:
        change(root)
    return root


# ---------------------------------------------------------------- the check of ``check``

_ERRORS_HEADING = re.compile(r"\d+ errors?:|\d+ 个错误：")


def _errors_block(report: str) -> list[str]:
    """Gives the lines under the heading of errors of a report, up to the empty line."""
    lines = report.split("\n")
    start = next(index for index, line in enumerate(lines) if _ERRORS_HEADING.fullmatch(line))
    block: list[str] = []
    for line in lines[start + 1 :]:
        if not line:
            break
        block.append(line)
    return block


def assert_among_check(home: Path, root: Path, *problems: Prob) -> None:
    """Checks that ``check`` exits with 1 and lists each problem, in both languages.

    A problem is among the errors of ``check`` when its report holds the two lines ``  W`` and
    four spaces and the text of M under its heading of errors.
    """
    for lang, argv in ((EN, ("check",)), (ZH, ("check", "--lang", "zh"))):
        code, report, _ = at(home, root, *argv)
        assert code == 1, (lang, report)
        block = _errors_block(report)
        lines = list(itertools.pairwise(block))
        for problem in problems:
            where, what = pair(problem, lang)
            assert (f"  {where}", f"    {what}") in lines, (lang, problem)


# ---------------------------------------------------------------- the named changes

_STAPLE = '{ zh = "主食", en = "staple" },'
_QUICK = '  { zh = "快手", en = "quick" },\n'
_HOME_STYLE = '  { zh = "家常", en = "home-style" },\n'


def mapo_and_rice_at_0(root: Path) -> None:
    """Makes the mapo mistake and rice at 0, as input 9 of F09-T11 and input 7 of F09-T18."""
    mapo_mistake(root)
    servings_zero(root, "rice")


def no_catalog(root: Path) -> None:
    """Deletes ``catalog.toml``."""
    (root / "catalog.toml").unlink()


def no_recipes_folder(root: Path) -> None:
    """Deletes ``recipes/`` with everything in it."""
    shutil.rmtree(root / "recipes")


def recipes_as_file(root: Path) -> None:
    """Deletes ``recipes/`` and writes an empty file at its path."""
    no_recipes_folder(root)
    write(root / "recipes", "")


def empty_recipes(root: Path) -> None:
    """Deletes every entry of ``recipes/``."""
    for entry in (root / "recipes").iterdir():
        entry.unlink()


def not_recipes(root: Path) -> None:
    """Empties ``recipes/``, then adds the file ``notes.txt`` and the empty folder ``old``."""
    empty_recipes(root)
    write(root / "recipes" / "notes.txt", "Ideas\n")
    (root / "recipes" / "old").mkdir()


def rice_bowl(root: Path) -> None:
    """Adds the empty file ``recipes/Rice Bowl.toml``."""
    write(root / "recipes" / "Rice Bowl.toml", "")


def capital_rice(root: Path) -> None:
    """Renames ``recipes/rice.toml`` to ``recipes/rice.TOML``."""
    (root / "recipes" / "rice.toml").rename(root / "recipes" / "rice.TOML")


def folder_x(root: Path) -> None:
    """Makes the empty folder ``recipes/x.toml``."""
    (root / "recipes" / "x.toml").mkdir()


def soup(root: Path) -> None:
    """Adds the tag ``soup`` after ``staple`` in the catalog."""
    edit(root / "catalog.toml", _STAPLE, _STAPLE + '\n  { zh = "汤", en = "soup" },')


def _replace_tags(root: Path, tail: str) -> None:
    """Replaces the text of the catalog from ``tags = [`` to its end by ``tail``."""
    path = root / "catalog.toml"
    text = path.read_text(encoding="utf-8")
    write(path, text[: text.index("tags = [")] + tail)


def one_tag(root: Path) -> None:
    """Leaves the tag ``quick`` in the catalog."""
    _replace_tags(root, f"tags = [\n{_QUICK}]\n")


def two_tags(root: Path) -> None:
    """Leaves the tags ``quick`` and ``home-style`` in the catalog."""
    _replace_tags(root, f"tags = [\n{_QUICK}{_HOME_STYLE}]\n")


def no_tags(root: Path) -> None:
    """Leaves no tag in the catalog."""
    _replace_tags(root, "tags = []\n")


def rice_for_3(root: Path) -> None:
    """Replaces ``servings = 2`` by ``servings = 3`` in ``recipes/rice.toml``."""
    edit(root / "recipes" / "rice.toml", "servings = 2", "servings = 3")


BOILED_EGG_FILE = """name = { en = "Boiled egg" }
servings = 1
tags = []
ingredients = [
  { item = "鸡蛋", amount = "2", note = { en = "at room temperature" } },
  { item = "盐", amount = "适量" },
]
[steps]
en = ["Boil the eggs for 8 minutes."]
"""
STEAMED_EGG_FILE = """name = { zh = "蒸蛋" }
servings = 3
tags = ["快手", "素"]
ingredients = [
  { item = "鸡蛋", amount = "2", note = { zh = "打散" } },
  { item = "葱", amount = "1", note = { zh = "切葱花" } },
  { item = "盐", amount = "适量" },
]
[steps]
zh = ["鸡蛋加温水和盐打散。", "撒上葱花，蒸 10 分钟。"]
"""
WATER_FILE = """name = { zh = "白开水", en = "Boiled water" }
servings = 1
tags = []
ingredients = []
[steps]
zh = ["把水烧开。"]
en = ["Boil the water."]
"""
PIZZA_FILE = """name = { zh = "Pizza", en = "Pizza" }
servings = 2
tags = []
ingredients = []
[steps]
zh = ["烤 12 分钟。"]
en = ["Bake for 12 minutes."]
"""
LONG_FILE = """name = { zh = "长长的第一行{S}尾", en = "A long first line{S}end" }
servings = 2
tags = ["快手"]
ingredients = [{ item = "大米", amount = "100 g" }]
[steps]
zh = ["煮饭。"]
en = ["Cook the rice."]
"""
CUCUMBER_FILE = """name = { zh = "拍黄瓜", en = "Smashed cucumber" }
servings = 2
tags = ["快手", "素"]
ingredients = [
  { item = "黄瓜", amount = "2 个" },
  { item = "大蒜", amount = "2 瓣" },
]
[steps]
zh = ["黄瓜拍碎，加蒜末拌匀。"]
en = ["Smash the cucumbers and toss them with the garlic."]
"""


def extra_recipes(root: Path) -> None:
    """Writes ``boiled-egg``, ``steamed-egg``, and ``water`` into ``recipes/``."""
    write(root / "recipes" / "boiled-egg.toml", BOILED_EGG_FILE)
    write(root / "recipes" / "steamed-egg.toml", STEAMED_EGG_FILE)
    write(root / "recipes" / "water.toml", WATER_FILE)


def long_name(root: Path, escape: str) -> None:
    """Keeps only ``rice`` and writes ``a-long``, with the TOML escape in place of ``{S}``.

    Args:
        root: The data folder.
        escape: The escape as the file holds it, with its backslash.
    """
    for path in (root / "recipes").glob("*.toml"):
        if path.name != "rice.toml":
            path.unlink()
    write(root / "recipes" / "a-long.toml", LONG_FILE.replace("{S}", escape))


# The wrong IDs of input 1 of F09-T03, and the wrong values of --servings of its input 2.
WRONG_IDS = [
    "Mapo",
    "../rice",
    "",
    "con",
    "tomato\u2010egg",
    "Tomato-Egg",
    "tomato egg",
    "tomato_egg",
    "-tomato",
    "rice.",
    "a:b",
    "nul",
    "lpt9",
    "番茄炒蛋",
    "tomato-egg\u200b",
    "\uff54omato-egg",
]
WRONG_SERVINGS = [
    "0",
    "101",
    "04",
    "+4",
    "4.0",
    " 4",
    "4 ",
    "-1",
    "1_0",
    "\uff14",
    "\u0664",
    "\u00b2",
    "1000",
    "9" * 5000,
]
