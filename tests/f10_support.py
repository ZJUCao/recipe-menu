"""Helpers that the F10 tests share: the searches of a case, the named changes, and the files.

Nothing here calls an interface of F10 when the module is imported. ``searches`` and ``real_help``
call ``main`` with the real commands through ``at``, ``raises_empty`` calls ``SEARCH_COMMAND.run``
with a context from ``new_context``, ``span`` and ``lines_of`` pick lines of a block, and the named
changes change the folders of a case. The expected texts are in ``f10_texts``. The module reuses
``at`` and ``new_context`` of ``f09_support``, ``edit`` of ``f07_changes``, ``write`` and
``put_bytes`` of ``f03_support``, and ``Result`` of ``f05_texts``. The F10 tests import
``make_home``, ``make_init``, ``faults``, ``snapshot``, ``run_module``, and the other named
changes from their own modules.
"""

from collections.abc import Iterable
from pathlib import Path

from f03_support import put_bytes, write
from f05_texts import Result
from f07_changes import edit
from f09_support import at, new_context
from f10_texts import Block, Words
from recipe_menu.app import Arguments, UsageError
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

type Case = tuple[Words, Result]

# ---------------------------------------------------------------- the searches of a case


def searches(home: Path, folder: Path | DataFolder | None, cases: Iterable[Case]) -> None:
    """Runs ``search`` with each words line through ``main``, and checks the whole result.

    Args:
        home: The home folder.
        folder: The data folder, or ``None`` for a line with no ``--data``.
        cases: Each case is the words after ``search`` and the result that ``main`` must give.
    """
    for words, expected in cases:
        assert at(home, folder, "search", *words) == expected, words


def span(block: Block, first: Words, last: Words) -> list[Case]:
    """Gives the lines of a block from the line ``first`` to the line ``last``, both included."""
    keys = list(block)
    return [(key, block[key]) for key in keys[keys.index(first) : keys.index(last) + 1]]


def lines_of(block: Block, *keys: Words) -> list[Case]:
    """Gives the lines of a block that the keys name, in the order of the keys."""
    return [(key, block[key]) for key in keys]


def real_help(home: Path, *extra: str) -> Result:
    """Runs ``--help`` with no folder and the real commands, and gives its result.

    It checks that the result is exit code 0 with an empty error stream and a table of commands
    that holds the line of ``search``, and leaves the whole text to the case.
    """
    code, text, error = at(home, None, "--help", *extra)
    assert (code, error) == (0, "")
    assert "search WORD..." in text or "search 词..." in text
    return code, text, error


def raises_empty(folder: DataFolder, lang: Lang, words: Words) -> UsageError:
    """Runs ``SEARCH_COMMAND.run`` for words that must raise, and checks that no stream got text."""
    context, output, error = new_context(lang, folder)
    try:
        SEARCH_COMMAND.run(context, Arguments(words))
    except UsageError as caught:
        assert (output.getvalue(), error.getvalue()) == ("", "")
        return caught
    raise AssertionError(f"run did not raise for {words!r}")


# ---------------------------------------------------------------- the named changes

_TOMATO_LINE = '  { zh = "番茄", en = "Tomato", category = "produce" },\n'
_EGGPLANT_LINE = '  { zh = "茄子", en = "Eggplant", category = "produce" },\n'
AUBERGINE_FILE = """name = { zh = "烧茄子", en = "Braised aubergine" }
servings = 2
tags = ["素"]
ingredients = [
  { item = "茄子", amount = "2 个" },
  { item = "大蒜", amount = "3 瓣" },
]
[steps]
zh = ["茄子切条，和蒜一起烧软。"]
en = ["Cut the eggplant into strips, and braise it with the garlic."]
"""
CREME_FILE = """name = { zh = "焦糖布丁", en = "Cr\u00e8me caramel" }
servings = 4
tags = []
ingredients = [
  { item = "鸡蛋", amount = "3" },
  { item = "糖", amount = "100 g" },
]
[steps]
zh = ["烤 40 分钟。"]
en = ["Bake for 40 minutes."]
"""


def chinese_settings(root: Path) -> None:
    """Replaces ``language = "en"`` by ``language = "zh"`` in ``settings.toml``."""
    edit(root / "settings.toml", 'language = "en"', 'language = "zh"')


def egg_in_english(root: Path) -> None:
    """Makes ``tomato-egg`` write its egg as ``EGG``, which F04 finds as the catalog's egg."""
    path = root / "recipes" / "tomato-egg.toml"
    edit(path, '{ item = "鸡蛋", amount = "3" }', '{ item = "EGG", amount = "3" }')


def eggplant(root: Path) -> None:
    """Adds the ingredient Eggplant to the catalog and writes ``recipes/aubergine.toml``."""
    edit(root / "catalog.toml", _TOMATO_LINE, _TOMATO_LINE + _EGGPLANT_LINE)
    write(root / "recipes" / "aubergine.toml", AUBERGINE_FILE)


def creme(root: Path) -> None:
    """Writes ``recipes/creme.toml``."""
    write(root / "recipes" / "creme.toml", CREME_FILE)


def bom_and_crlf(root: Path) -> None:
    """Writes each ``.toml`` file again with a byte order mark and CRLF line ends."""
    for path in sorted(root.rglob("*.toml")):
        put_bytes(path, b"\xef\xbb\xbf" + path.read_bytes().replace(b"\n", b"\r\n"))


# ---------------------------------------------------------------- the words of the cases

EMPTY_WORDS: list[Words] = [
    ("",),
    (" ",),
    ("\t",),
    ("\n",),
    ("\u00a0",),
    ("\u3000",),
    ("\u2028",),
    (" \u3000\t",),
    ("番茄", ""),
    ("", "番茄"),
    (" ", "lamb"),
    ("番茄", "\u3000"),
    ("番茄", "quick", "\t"),
]
FINE_WORDS: list[Words] = [
    ("\u200b",),
    ("\ufeff",),
    ("-x",),
    ("a",),
    (" a ",),
    ("\u3000番茄",),
    ("9" * 5000,),
    ("番茄", "\u200b"),
]
