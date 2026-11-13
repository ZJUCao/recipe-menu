"""The PT01 data folder and the timed runs of ``recipe-menu`` commands on it.

PT01 is the performance target of requirements 7.1: 1,000 recipes, 300 catalog ingredients, and
52 week menus. ``make_pt01`` writes the folder with the shape that the v0.1 test plan gives
v0.1-S27, and ``timed_runs`` times ``python -m recipe_menu check`` on it. ``command_run`` and
``command_runs`` time any command, and ``pt01_list`` and ``pt01_show`` give the expected output
of ``list`` and ``show recipe-0500`` on the folder. Nothing here calls an interface of a command
when the module is imported.
"""

import statistics
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path

from f03_support import write
from f05_support import run_module
from f05_texts import Result
from f06_support import MEALS_EVERY
from f07_support import lines_text, rep
from f07_texts import P_STEPS, Prob, m_menu_meal, m_steps_key, p_slot

RECIPES = 1000
INGREDIENTS = 300
WEEKS = 52
PT01_LINES = [
    "Checked the settings, the catalog, the pantry, 1000 recipes, and 52 week menus.",
    "",
    "No errors. No warnings.",
]
PT01_STDOUT = lines_text(PT01_LINES)

_CATEGORIES = ("produce", "meat", "eggs", "staples", "seasonings", "other")
_TAGS = ("快手", "家常", "素", "辣", "主食")
_AMOUNTS = ("200 g", "15 ml", "2 个", "适量")
_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
_MEALS = ("breakfast", "lunch", "dinner")
_EXAMPLE_CATALOG = Path(__file__).parent / "data" / "example" / "catalog.toml"


def time_limit() -> float:
    """Gives the limit of F07-T25, F09-T28, and F09-T29 in seconds: 1 on Windows, 3 otherwise."""
    return 1.0 if sys.platform == "win32" else 3.0


def _catalog() -> str:
    """Writes ``catalog.toml``: the categories and the tags of the example and 300 ingredients."""
    text = _EXAMPLE_CATALOG.read_text(encoding="utf-8")
    categories = text[: text.index("ingredients = [")]
    tags = text[text.index("tags = [") :]
    items = "".join(
        f'  {{ zh = "食材{k:03d}", en = "Ingredient {k:03d}", '
        f'category = "{_CATEGORIES[(k - 1) % len(_CATEGORIES)]}" }},\n'
        for k in range(1, INGREDIENTS + 1)
    )
    return f"{categories}ingredients = [\n{items}]\n\n{tags}"


def _steps(zh: bool) -> str:
    """Writes the six steps of one language of a recipe."""
    lines = [
        f'  "第 {n} 步：把食材洗净切好，放进锅里翻炒两分钟。",'
        if zh
        else f'  "Step {n}: Wash and cut the ingredients, and stir-fry them for two minutes.",'
        for n in range(1, 7)
    ]
    return "".join(f"{line}\n" for line in lines)


def _recipe(k: int) -> str:
    """Writes recipe number ``k``."""
    tags = [_TAGS[k % 5], _TAGS[(k + 1) % 5]]
    note = 'note = { zh = "切块", en = "cut into pieces" }'
    lines = [f'  {{ item = "食材001", amount = "1 tsp", {note} }},']
    for j in range(11):
        number = 2 + (11 * k + j) % 299
        amount = _AMOUNTS[j % 4]
        lines.append(f'  {{ item = "食材{number:03d}", amount = "{amount}", {note} }},')
    ingredients = "".join(f"{line}\n" for line in lines)
    return (
        f'name = {{ zh = "菜谱{k:04d}", en = "Recipe {k:04d}" }}\n'
        f"servings = {1 + k % 4}\n"
        f'tags = ["{tags[0]}", "{tags[1]}"]\n'
        f"ingredients = [\n{ingredients}]\n"
        f"[steps]\nzh = [\n{_steps(True)}]\nen = [\n{_steps(False)}]\n"
    )


def _menu(week: int) -> str:
    """Writes the menu of week ``week`` of 2026."""
    lines = [f'week = "2026-W{week:02d}"']
    for d, day in enumerate(_DAYS):
        lines += ["", f"[{day}]"]
        for m, meal in enumerate(_MEALS):
            dishes = []
            for s in range(3):
                number = ((week - 1) * 63 + 9 * d + 3 * m + s) % RECIPES + 1
                recipe = f"recipe-{number:04d}"
                if meal == "dinner" and s == 0:
                    dishes.append(f'{{ recipe = "{recipe}", servings = 4 }}')
                else:
                    dishes.append(f'"{recipe}"')
            lines.append(f"{meal} = [{', '.join(dishes)}]")
    return "".join(f"{line}\n" for line in lines)


def make_pt01(root: Path) -> None:
    """Writes the PT01 data folder at ``root``, with LF line ends and no ``shopping/``."""
    write(
        root / "settings.toml",
        'language = "en"\nmeals = ["breakfast", "lunch", "dinner"]\nservings = 2\n',
    )
    write(root / "catalog.toml", _catalog())
    last = ", ".join(f'"食材{k:03d}"' for k in range(INGREDIENTS - 9, INGREDIENTS + 1))
    write(root / "pantry.toml", f"pantry = [{last}]\n")
    for k in range(1, RECIPES + 1):
        write(root / "recipes" / f"recipe-{k:04d}.toml", _recipe(k))
    for week in range(1, WEEKS + 1):
        write(root / "menus" / f"2026-W{week:02d}.toml", _menu(week))


def _run(tmp_path: Path, root: Path) -> tuple[tuple[int, str, str], float]:
    """Starts ``python -m recipe_menu check --data <root>`` and gives its result and its time.

    The time covers all of ``run_module``, not only the ``subprocess.run`` call inside it.
    """
    start = time.perf_counter()
    result = run_module(tmp_path, "check", "--data", str(root))
    return result, time.perf_counter() - start


def check_run(tmp_path: Path, root: Path) -> float:
    """Runs ``check`` on the PT01 folder once, checks its result, and gives its time in seconds.

    The run must exit with 0, write the three lines of PT01 on stdout, and write nothing on
    stderr, whatever its time.
    """
    result, seconds = _run(tmp_path, root)
    assert result == (0, PT01_STDOUT, "")
    return seconds


def timed_runs(tmp_path: Path, root: Path, count: int = 5) -> list[float]:
    """Runs ``check`` on the PT01 folder ``count`` times and gives the times in seconds.

    It checks each result through ``check_run``.
    """
    return [check_run(tmp_path, root) for _ in range(count)]


def median_and_range(times: list[float]) -> tuple[float, float, float]:
    """Gives the median, the least, and the greatest of the times."""
    return statistics.median(times), min(times), max(times)


def check_after_mistakes(tmp_path: Path, root: Path) -> None:
    """Puts a mistake in the last recipe and the last menu, and checks the two errors.

    The line ``fr = [...]`` goes at the end of ``recipes/recipe-1000.toml``, which puts the key
    ``fr`` in ``[steps]``, and the line ``supper = []`` at the end of ``menus/2026-W52.toml``,
    which puts the key in ``[sunday]``.
    """
    recipe = root / "recipes" / "recipe-1000.toml"
    write(recipe, recipe.read_text(encoding="utf-8") + 'fr = ["\u00c9tape 1."]\n')
    menu = root / "menus" / "2026-W52.toml"
    write(menu, menu.read_text(encoding="utf-8") + "supper = []\n")
    errors = [
        Prob("recipes/recipe-1000.toml", P_STEPS, m_steps_key("fr")),
        Prob("menus/2026-W52.toml", p_slot("sunday", "supper"), m_menu_meal("supper", MEALS_EVERY)),
    ]
    result, _ = _run(tmp_path, root)
    assert result == rep(1, RECIPES, WEEKS, errors, [])


# ---------------------------------------------------------------- the general timed run


def command_run(tmp_path: Path, root: Path, argv: Sequence[str], expected: Result) -> float:
    """Starts ``python -m recipe_menu`` with the arguments and ``--data <root>`` once.

    It times the whole call of ``run_module`` with ``time.perf_counter()``, checks that the result
    equals ``expected``, and gives the time in seconds. A result that differs fails the check,
    whatever the time.

    Args:
        tmp_path: The folder to run in. Its ``home`` folder is the home of the run.
        root: The data folder.
        argv: The arguments before ``--data``.
        expected: The ``(code, stdout, stderr)`` that the run must give.
    """
    start = time.perf_counter()
    result = run_module(tmp_path, *argv, "--data", str(root))
    seconds = time.perf_counter() - start
    assert result == expected
    return seconds


def command_runs(
    tmp_path: Path, root: Path, argv: Sequence[str], expected: Result, count: int = 5
) -> list[float]:
    """Runs a command ``count`` times with ``command_run`` and gives the times in seconds."""
    return [command_run(tmp_path, root, argv, expected) for _ in range(count)]


def record_times(record_property: Callable[[str, object], None], times: list[float]) -> float:
    """Records the times, the median, and the range for the JUnit report, and gives the median."""
    median, least, greatest = median_and_range(times)
    record_property("pt01_times_seconds", ", ".join(f"{seconds:.3f}" for seconds in times))
    record_property("pt01_median_seconds", f"{median:.3f}")
    record_property("pt01_range_seconds", f"{least:.3f} to {greatest:.3f}")
    return median


# ---------------------------------------------------------------- the expected outputs

_TAG_NAMES = ("quick", "home-style", "vegetarian", "spicy", "staple")
_LIST_ROW = "{id}   {name}   {servings:<8}   {tags}"


def pt01_list() -> Result:
    """Gives the result of ``list`` on the PT01 folder: 1,003 lines, built from the generator."""
    lines = ["ID            Name          Servings   Tags"]
    for k in range(1, RECIPES + 1):
        tags = f"{_TAG_NAMES[k % 5]}, {_TAG_NAMES[(k + 1) % 5]}"
        lines.append(
            _LIST_ROW.format(
                id=f"recipe-{k:04d}", name=f"Recipe {k:04d}", servings=1 + k % 4, tags=tags
            )
        )
    lines += ["", f"{RECIPES} recipes."]
    return 0, lines_text(lines), ""


def pt01_show() -> Result:
    """Gives the result of ``show recipe-0500`` on the PT01 folder: 24 lines."""
    lines = [
        "Recipe 0500  菜谱0500",
        "Servings: 1   Tags: quick, home-style",
        "",
        "Ingredients",
        f"  Ingredient 001   {'1 tsp':<8}   cut into pieces",
    ]
    quantities = ("200 g", "15 ml", "2 pieces", "to taste")
    for j in range(11):
        number = 2 + (11 * 500 + j) % 299
        lines.append(f"  Ingredient {number:03d}   {quantities[j % 4]:<8}   cut into pieces")
    lines += ["", "Steps"]
    for n in range(1, 7):
        lines.append(
            f"  {n}. Step {n}: Wash and cut the ingredients, and stir-fry them for two minutes."
        )
    return 0, lines_text(lines), ""
