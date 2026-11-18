"""Helpers that the F14 tests share: the sources of random choices, calls, and the named changes.

The module makes the generators that record each random choice a command asks for and fail the
case on any other draw, runs the command line with a generator, makes the data folder with 40
recipes, and builds the bytes of a filled menu file and the text of a week of dinners. It also
holds the named changes of the test plan, the records of the calls that the fault harness sees,
and the checks of a problem of a file and of the settings. Nothing here calls an interface of F14
when the module is imported, so the test files import against the mock and against a broken
implementation. The expected texts are in ``f14_texts``.
"""

import io
import re
from collections.abc import Callable, Iterable, Sequence
from datetime import date
from pathlib import Path
from random import Random
from typing import Any

import pytest

from f03_support import put_bytes, write
from f05_support import TODAY, copy_example
from f05_texts import KEYS_MARK, Expected, Msg, Result, assert_problems, lines_text
from f07_changes import append, edit
from f07_support import AFTER
from f08_support import EXAMPLE, Rule
from f11_support import menu_text, settings_meals
from f13_support import Change, shop_faults
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
EXAMPLE_IDS = (
    "choy-sum",
    "cola-wings",
    "mapo-tofu",
    "red-braised-pork",
    "rice",
    "tomato-egg",
    "tomato-egg-noodles",
)
QUICK_IDS = (
    "choy-sum",
    *(f"quick-{number:02d}" for number in range(1, 14)),
    "tomato-egg",
    "tomato-egg-noodles",
)
SPICY_IDS = ("mapo-tofu", "spicy-01", "spicy-02")
EXAMPLE_FILES = [f"recipes/{recipe_id}.toml" for recipe_id in EXAMPLE_IDS]
SUGGEST_IDS = tuple(
    sorted(
        [
            *EXAMPLE_IDS,
            *(f"quick-{number:02d}" for number in range(1, 14)),
            *(f"spicy-{number:02d}" for number in range(1, 3)),
            *(f"home-{number:02d}" for number in range(1, 19)),
        ]
    )
)
LUNCH_DINNER = (Meal.LUNCH, Meal.DINNER)
EVERY_MEAL = (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER)
W47 = "2026-W47"
WEEK_48 = "2026-W48"
FILE_47 = "menus/2026-W47.toml"
IN_ZH = ("--lang", "zh")
AFTER_40 = [
    AFTER[0].replace("7 recipes, and 1 week menu", "40 recipes, and 2 week menus"),
    *AFTER[1:],
]

# ---------------------------------------------------------------- the sources of random choices


class Source(Random):
    """A generator that records each choice of items and fails the case on any other draw.

    Attributes:
        calls: Each choice in order, as the list of the population and the count.
    """

    def __init__(self) -> None:
        """Makes a source with no calls."""
        super().__init__(0)
        self.calls: list[tuple[list[str], int]] = []

    def pick(self, items: list[str], count: int) -> list[str]:
        """Gives the ``count`` items that the source chooses. A subclass decides which."""
        raise NotImplementedError

    def sample(  # type: ignore[override]
        self, population: Sequence[str], k: int, *, counts: Iterable[int] | None = None
    ) -> list[str]:
        """Records the call, and gives what ``pick`` gives."""
        assert counts is None
        items = list(population)
        self.calls.append((items, k))
        return self.pick(items, k)


def _forbidden(name: str) -> Callable[..., Any]:
    """Makes the method that fails the case when the command draws with ``name``."""

    def draw(self: Source, *args: object, **kwargs: object) -> Any:
        """Fails the case: the command may draw only with ``sample``."""
        pytest.fail(f"the command drew with {name}, and not with sample")

    draw.__name__ = name
    return draw


for _name in (
    "random",
    "getrandbits",
    "randrange",
    "randint",
    "choice",
    "choices",
    "shuffle",
    "randbytes",
    "uniform",
):
    setattr(Source, _name, _forbidden(_name))


class FrontSource(Source):
    """A source that gives the first items of the population."""

    def pick(self, items: list[str], count: int) -> list[str]:
        """Gives the first ``count`` items, in order."""
        return items[:count]


class BackSource(Source):
    """A source that gives the last items of the population, the last one first."""

    def pick(self, items: list[str], count: int) -> list[str]:
        """Gives the last ``count`` items, the last one first."""
        return items[::-1][:count]


def seeded(seed: int) -> Random:
    """Gives a generator with a fixed seed: ``Random(seed)``."""
    return Random(seed)  # noqa: S311 - a fixed seed, no security


def picks(seed: int, population: Sequence[str], count: int) -> list[str]:
    """Gives the picks of ``Random(seed)``: ``Random(seed).sample`` of the population."""
    return seeded(seed).sample(list(population), count)


# ---------------------------------------------------------------- calls


def suggest(
    home: Path,
    folder: Path | DataFolder | None,
    *argv: str,
    random: Random | None = None,
    today: date = TODAY,
) -> Result:
    """Runs ``main`` with the real commands and a generator, as the test plan's conventions say.

    Args:
        home: The home folder.
        folder: The data folder, or ``None`` for a line with no ``--data``.
        *argv: The command line before ``--data``.
        random: The generator to pass on. A new front source when ``None``.
        today: The date that ``main`` gets as today.
    """
    full = list(argv)
    if folder is not None:
        full += ["--data", str(folder.root if isinstance(folder, DataFolder) else folder)]
    out, err = io.StringIO(), io.StringIO()
    code = main(
        full,
        environ={},
        home=home,
        today=today,
        stdout=out,
        stderr=err,
        random=FrontSource() if random is None else random,
    )
    return code, out.getvalue(), err.getvalue()


def traced(
    home: Path, root: Path, rules: Sequence[Rule], *argv: str, random: Random | None = None
) -> tuple[Result, list[str], list[str]]:
    """Runs ``menu suggest`` in the fault harness, and gives the result, calls, and listings.

    Args:
        home: The home folder.
        root: The data folder, which the harness records its paths against.
        rules: The rules of the harness.
        *argv: The command line before ``--data``.
        random: The generator to pass on. A new front source when ``None``.
    """
    with shop_faults(root, *rules) as state:
        result = suggest(home, root, *argv, random=random)
    return result, state.calls, state.listings


def week_line(week: str, *rest: str) -> tuple[str, ...]:
    """Gives the words of ``menu suggest`` for a week, and the rest of the line."""
    return ("menu", "suggest", week, *rest)


# ---------------------------------------------------------------- the data folders


_NEW_RECIPE = """name = {{ zh = "{zh} {number:02d}", en = "{en} {number:02d}" }}
servings = 2
tags = ["{tag}"]

ingredients = [{{ item = "番茄", amount = "300 g" }}]

[steps]
zh = ["番茄切块。"]
en = ["Cut the tomatoes."]
"""
_KINDS = (
    ("quick", "快手", 13, "快手菜", "Quick dish"),
    ("spicy", "辣", 2, "辣菜", "Spicy dish"),
    ("home", "家常", 18, "家常菜", "Home dish"),
)


def suggest_folder(example: DataFolder, tmp_path: Path, name: str) -> Path:
    """Makes a new example at ``tmp_path / name`` with 33 more recipes, and gives its path.

    The recipes are ``quick-01`` to ``quick-13`` with the tag quick, ``spicy-01`` and
    ``spicy-02`` with the tag spicy, and ``home-01`` to ``home-18`` with the tag home-style.
    Each has one tag, 2 servings, a name in each language, one ingredient of the catalog, and a
    step in each language.
    """
    root = copy_example(example, tmp_path / name)
    for prefix, tag, count, zh, en in _KINDS:
        for number in range(1, count + 1):
            text = _NEW_RECIPE.format(zh=zh, en=en, tag=tag, number=number)
            write(root / "recipes" / f"{prefix}-{number:02d}.toml", text)
    return root


# ---------------------------------------------------------------- the texts of menu files


def dish_list(ids: Sequence[str]) -> str:
    """Gives the list of the dishes of a meal as the command writes it: ``["a", "b"]``."""
    return "[" + ", ".join(f'"{recipe_id}"' for recipe_id in ids) + "]"


def filled(week: str, meals: Sequence[Meal], fills: Sequence[Sequence[str] | None]) -> bytes:
    """Gives the bytes of a new menu file with its empty meals filled, in order.

    Args:
        week: The week.
        meals: The meals of the settings.
        fills: The recipe IDs for the first empty meals, in order. ``None`` keeps a meal empty.
            A meal after the last item keeps its ``[]``.
    """
    lines = menu_text(week, meals).decode("utf-8").splitlines()
    empty = [index for index, line in enumerate(lines) if line.endswith(" = []")]
    assert len(fills) <= len(empty)
    for index, fill in zip(empty, fills, strict=False):
        if fill is not None:
            lines[index] = lines[index][:-2] + dish_list(fill)
    return lines_text(*lines).encode("utf-8")


def one_each(ids: Iterable[str]) -> list[list[str]]:
    """Gives each recipe ID as the one dish of one meal."""
    return [[recipe_id] for recipe_id in ids]


def dinners(week: str, *lists: Sequence[str]) -> str:
    """Gives the text of a week with dinner alone: one list of recipe IDs for each day."""
    assert len(lists) == 7
    lines = [f'week = "{week}"']
    for day, ids in zip(DAYS, lists, strict=True):
        lines += ["", f"[{day}]", f"dinner = {dish_list(ids)}"]
    return lines_text(*lines)


def w47_filled() -> bytes:
    """Gives the bytes of the example week 47 after ``red-braised-pork`` fills Monday lunch."""
    data = (EXAMPLE / "menus" / "2026-W47.toml").read_bytes().replace(b"\r\n", b"\n")
    return data.replace(b"lunch = []", b'lunch = ["red-braised-pork"]', 1)


def stamp(path: Path) -> tuple[bytes, int]:
    """Gives the bytes and the ``st_mtime_ns`` of a file."""
    return path.read_bytes(), path.stat().st_mtime_ns


# ---------------------------------------------------------------- the named changes


def with_meals(*meals: Meal) -> Change:
    """Gives the change that writes the settings as one line with the meals, in the given order."""
    return lambda root: settings_meals(root, *meals)


DINNER = with_meals(Meal.DINNER)


def with_dishes(table: str) -> Change:
    """Gives the change that adds the line ``dishes = <table>`` at the end of the settings."""
    return lambda root: append(root / "settings.toml", f"dishes = {table}\n")


def new_menu(week: str, meals: Sequence[Meal]) -> Change:
    """Gives the change that writes ``menus/<week>.toml`` as the file that ``menu new`` writes."""
    return lambda root: put_bytes(root / "menus" / f"{week}.toml", menu_text(week, meals))


def menu_as(week: str, text: str) -> Change:
    """Gives the change that writes ``menus/<week>.toml`` with a text, with LF line ends."""
    return lambda root: write(root / "menus" / f"{week}.toml", text)


def refuse_one(root: Path) -> None:
    """Deletes the three dishes of Sunday dinner of the example week, and keeps its two lines."""
    path = root / "menus" / "2026-W47.toml"
    for recipe in ("cola-wings", "choy-sum", "rice"):
        edit(path, f'  {{ recipe = "{recipe}", servings = 4 }},\n', "")


def refuse_two(root: Path) -> None:
    """Does what ``refuse_one`` does, and adds a comment to the line ``dinner = [``."""
    refuse_one(root)
    edit(root / "menus" / "2026-W47.toml", "dinner = [\n", "dinner = [  # later\n")


# ---------------------------------------------------------------- the records of the harness

READ_CATALOG = "read catalog.toml"


def reads(*names: str) -> list[str]:
    """Gives the records of the reads of files, such as ``read recipes/rice.toml``."""
    return [f"read {name}" for name in names]


def save_of(week: str) -> list[str]:
    """Gives the three calls that the write of ``menus/<week>.toml`` makes."""
    temp = f"menus/{week}.toml.tmp"
    return [f"unlink {temp}", f"open {temp}", f"move {temp} menus/{week}.toml"]


def assert_no_write(calls: Sequence[str]) -> None:
    """Checks that no call of a record removes, opens for writing, or moves a file."""
    assert not [call for call in calls if call.split()[0] in ("unlink", "open", "move")], calls


# ---------------------------------------------------------------- the checks of a problem


def assert_text_problem(problem: object, file: str, place: BiText | None, msg: Msg) -> None:
    """Checks a problem of a file: an error with the file, the place, and both texts."""
    assert isinstance(problem, Problem), problem
    assert problem.severity is Severity.ERROR
    assert str(problem.file) == str(Path(*file.split("/")))
    assert problem.place == place
    assert (problem.text(Lang.EN), problem.text(Lang.ZH)) == msg


def assert_settings_problems(problems: Sequence[Problem], expected: Sequence[Expected]) -> None:
    """Checks the problems of ``read_settings`` as ``assert_problems`` does, with a fourth key.

    The list of keys in an unknown-key text must also have ``dishes`` as its fourth key, so it
    starts with ``language``, ``meals``, ``servings``, and ``dishes``, in this order, and it may
    go on with later keys.
    """
    assert_problems(problems, expected)
    for problem, (_, en, _) in zip(problems, expected, strict=True):
        if KEYS_MARK in en:
            head, tail = en.split(KEYS_MARK)
            got = problem.text(Lang.EN)
            keys = re.split(r", (?:and )?", got[len(head) : len(got) - len(tail)])
            assert keys[3:4] == ["dishes"], got
