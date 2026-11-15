"""Helpers that the F11 tests share: calls on a date, the named changes, and the checks.

Nothing here calls an interface of F11 when the module is imported. Functions call ``main``, make
the folders of the cases, and check a ``FileCreation``. The expected texts are in ``f11_texts``.
The module imports ``write`` of ``f03_support``, ``Result`` of ``f05_texts``, ``made`` of
``f09_support``, ``LABELS`` of ``f11_texts``, and ``main`` and the types of the package. The F11
tests import the other helpers that they use from their own modules.
"""

import io
import shutil
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

from f03_support import write
from f05_texts import Result
from f09_support import made
from f11_texts import LABELS
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder, FileCreation, FileOutcome, Severity
from recipe_menu.lang import Lang
from recipe_menu.menus import Day, IsoWeek
from recipe_menu.settings import Meal

type Msg = tuple[str, str]

# ---------------------------------------------------------------- calls


def on(
    home: Path,
    folder: Path | DataFolder | None,
    today: date,
    *argv: str,
    environ: Mapping[str, str] | None = None,
) -> Result:
    """Runs ``main`` with the real commands on a date, as the test plan's conventions say.

    Args:
        home: The home folder.
        folder: The data folder, or ``None`` for a line with no ``--data``.
        today: The date that ``main`` gets as today.
        *argv: The command line before ``--data``.
        environ: The environment, ``{}`` when ``None``.
    """
    full = list(argv)
    if folder is not None:
        full += ["--data", str(folder.root if isinstance(folder, DataFolder) else folder)]
    out, err = io.StringIO(), io.StringIO()
    code = main(
        full,
        environ={} if environ is None else environ,
        home=home,
        today=today,
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------- the named changes

WEEK_B_FILE = """week = "2026-W48"

[monday]
dinner = ["rice", "rice"]
lunch = ["mapo-tofu"]

[friday]
lunch = [{ recipe = "choy-sum", servings = 10 }]

[sunday]
dinner = ["red-braised-pork"]
"""
WEEK_C_FILE = """week = "2026-W49"

[tuesday]
breakfast = ["boiled-egg", { recipe = "steamed-egg", servings = 1 }]

[sunday]
breakfast = ["water"]
"""
WEEK_D_FILE = """week = "2026-W50"

[monday]
lunch = ["a-long", "rice"]
"""
LINE_BREAKS = ["\\n", "\\r\\n", "\\u2028"]


def empty_menus(root: Path) -> None:
    """Deletes every entry of ``menus/``, which is the start of the F11 prototype."""
    for entry in sorted((root / "menus").iterdir()):
        entry.unlink()


def no_menus_folder(root: Path) -> None:
    """Deletes ``menus/`` with everything in it."""
    shutil.rmtree(root / "menus")


def menus_as_file(root: Path) -> None:
    """Deletes ``menus/`` and writes an empty file at its path."""
    no_menus_folder(root)
    write(root / "menus", "")


def week_b(root: Path) -> None:
    """Writes week B, ``menus/2026-W48.toml``."""
    write(root / "menus" / "2026-W48.toml", WEEK_B_FILE)


def week_c(root: Path) -> None:
    """Writes week C, ``menus/2026-W49.toml``."""
    write(root / "menus" / "2026-W49.toml", WEEK_C_FILE)


def week_d(root: Path) -> None:
    """Writes week D, ``menus/2026-W50.toml``."""
    write(root / "menus" / "2026-W50.toml", WEEK_D_FILE)


def settings_meals(root: Path, *meals: Meal) -> None:
    """Writes ``settings.toml`` with only a ``meals`` line, with the meals in the given order."""
    names = ", ".join(f'"{meal.value}"' for meal in meals)
    write(root / "settings.toml", f"meals = [{names}]\n")


def breakfast_only(root: Path) -> None:
    """Writes ``settings.toml`` as ``meals = ["breakfast"]``."""
    settings_meals(root, Meal.BREAKFAST)


# The seven sets of meals of F11-T17, as the settings list them, and the meals of each set as the
# English and the Chinese line of a new menu shows them.
SETS = [
    ("breakfast",),
    ("lunch",),
    ("dinner",),
    ("lunch", "breakfast"),
    ("dinner", "breakfast"),
    ("dinner", "lunch"),
    ("dinner", "lunch", "breakfast"),
]
SET_LABELS: list[Msg] = [
    ("breakfast", "早餐"),
    ("lunch", "午餐"),
    ("dinner", "晚餐"),
    ("breakfast and lunch", "早餐和午餐"),
    ("breakfast and dinner", "早餐和晚餐"),
    ("lunch and dinner", "午餐和晚餐"),
    ("breakfast, lunch, and dinner", "早餐、午餐和晚餐"),
]


def meals_of(words: Sequence[str]) -> list[Meal]:
    """Gives the meals of a set of words, in the order of ``Meal``."""
    return sorted((Meal(word) for word in words), key=list(Meal).index)


def meal_set(example: DataFolder, tmp_path: Path, name: str, words: Sequence[str]) -> Path:
    """Makes an empty-menus example at ``tmp_path / name`` whose settings list the words."""

    def settings(root: Path) -> None:
        """Writes the settings of the case."""
        settings_meals(root, *(Meal(word) for word in words))

    return made(example, tmp_path, name, empty_menus, settings)


# ---------------------------------------------------------------- the new file and its lines


def in_order(meals: Sequence[Meal]) -> list[Meal]:
    """Gives the meals in the order of ``Meal``, whatever order they come in."""
    return sorted(meals, key=list(Meal).index)


def menu_text(week: str, meals: Sequence[Meal]) -> bytes:
    """Gives the bytes of a new menu file for a week and the meals of the settings.

    The file is built from the rules of 2.2: the comment with the week and its English dates, the
    two comments of a dish, the line ``week``, and for each day an empty line, ``[day]``, and an
    empty list for each meal in the order of ``Meal``.
    """
    year, number = week.split("-W")
    dates = IsoWeek(int(year), int(number)).date_range.get(Lang.EN)
    lines = [
        f"# {week}: {dates}",
        '# A dish is a recipe ID, such as "tomato-egg",',
        '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
        f'week = "{week}"',
    ]
    for day in Day:
        lines += ["", f"[{day.value}]", *(f"{meal.value} = []" for meal in in_order(meals))]
    return "".join(f"{line}\n" for line in lines).encode("utf-8")


def held(path: Path) -> bytes | None:
    """Gives the bytes of a file, or ``None`` when no file is at the path."""
    return path.read_bytes() if path.is_file() else None


def first_half(data: bytes) -> bytes:
    """Gives the first half of an ASCII text, as the fault harness writes it before it raises."""
    return data[: len(data) // 2]


def meals_en(meals: Sequence[Meal]) -> str:
    """Gives the meals as the English line of a new menu shows them."""
    names = [LABELS[meal][0] for meal in in_order(meals)]
    if len(names) < 3:
        return " and ".join(names)
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def meals_zh(meals: Sequence[Meal]) -> str:
    """Gives the meals as the Chinese line of a new menu shows them."""
    names = [LABELS[meal][1] for meal in in_order(meals)]
    if len(names) < 3:
        return "和".join(names)
    return f"{'、'.join(names[:-1])}和{names[-1]}"


# ---------------------------------------------------------------- direct calls of create_file


def new_base(tmp_path: Path, name: str) -> tuple[Path, DataFolder]:
    """Makes the empty folder ``base`` of one call, and gives it with ``F`` on ``base/recipe-menu``.

    ``F`` is a ``DataFolder`` that does not exist yet, so a case makes the folders that it needs.
    """
    base = tmp_path / name
    base.mkdir()
    return base, DataFolder(base / "recipe-menu")


def base_with_menus(tmp_path: Path, name: str) -> tuple[Path, DataFolder]:
    """Gives ``base`` and ``F`` as ``new_base`` does, after it makes the empty ``F.menus``."""
    base, folder = new_base(tmp_path, name)
    folder.menus.mkdir(parents=True)
    return base, folder


def assert_created(creation: FileCreation) -> None:
    """Checks a ``FileCreation`` of the outcome ``CREATED`` with its other three fields empty."""
    assert creation.outcome is FileOutcome.CREATED, creation
    assert (creation.problem, creation.left, creation.existing) == (None, (), None)


def assert_exists(creation: FileCreation, existing: Path) -> None:
    """Checks an ``EXISTS`` result: no problem, an empty ``left``, and the entry as ``str``."""
    assert creation.outcome is FileOutcome.EXISTS, creation
    assert (creation.problem, creation.left) == (None, ())
    assert creation.existing is not None
    assert str(creation.existing) == str(existing)


def assert_failed(creation: FileCreation, file: str, msg: Msg, left: Sequence[Path] = ()) -> None:
    """Checks a ``FAILED`` result: the problem's file, no place, both texts, ``left``, no entry.

    Args:
        creation: The result.
        file: The problem's file with ``/`` separators, or ``.`` for the data folder itself.
        msg: The English and the Chinese text of the problem.
        left: The paths that the call could not remove.
    """
    assert creation.outcome is FileOutcome.FAILED, creation
    problem = creation.problem
    assert problem is not None
    assert problem.severity is Severity.ERROR
    assert str(problem.file) == str(Path(*file.split("/")))
    assert problem.place is None
    assert (problem.text(Lang.EN), problem.text(Lang.ZH)) == msg
    assert tuple(str(path) for path in creation.left) == tuple(str(path) for path in left)
    assert creation.existing is None
