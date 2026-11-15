"""Tests of F11 for recipe-menu menu show: the example of 2.4 and the files that it reads."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f07_changes import catalog_brace, edit, mapo_mistake, the_typo
from f07_texts import NOT_A_WEEK_NAME, TYPO, Prob
from f08_support import faults
from f09_support import at, made, rice_bowl
from f09_texts import E_BRACE, E_MAPO, E_RICE_BOWL, FOLDER_MISSING, err, out, stop
from f11_support import held, menu_text, no_menus_folder, week_b
from f11_texts import (
    BLOCK_A,
    DATES,
    LUNCH_DINNER,
    SHOW_47,
    SHOW_47_ZH,
    empty,
    exists,
    new,
    no_menu,
    no_menu_zh,
    not_a_week,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

BOTH = "lunch and dinner"
SETTINGS = "read settings.toml"
CATALOG = "read catalog.toml"
RECIPES_47 = ["tomato-egg", "choy-sum", "rice", "mapo-tofu", "tomato-egg-noodles", "cola-wings"]
# The reads of ``menu show 2026-W47`` on the example, in order, and the listings.
R47 = [
    SETTINGS,
    CATALOG,
    "read menus/2026-W47.toml",
    *[f"read recipes/{r}.toml" for r in RECIPES_47],
]
LISTINGS = ["recipes", "menus"]


def test_f11_t26_the_example_of_menu_show_runs_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.4, in order: the Chinese table, no menu, two errors, and a new menu."""
    home = make_home(tmp_path)
    folder = example_folder

    def show(*argv: str) -> tuple:
        """Runs ``menu show`` with the arguments in the example."""
        return at(home, folder, "menu", "show", *argv)

    assert show("2026-W47", "--lang", "zh") == out(SHOW_47_ZH)
    assert show("2026-W48") == err(1, [no_menu("2026-W48")])
    assert show("2026-W48", "--lang", "zh") == err(1, [no_menu_zh("2026-W48")])
    assert show("2026-W99") == err(2, [not_a_week("2026-W99")])
    edit(folder.recipe_file("red-braised-pork"), "servings = 2", "servings = 0")
    edit(folder.recipe_file("rice"), ', en = "Steamed rice"', "")
    assert show("2026-W47") == out([line.replace("Steamed rice", "米饭") for line in SHOW_47])
    mapo_mistake(folder.root)
    assert show("2026-W47") == stop(E_MAPO)
    edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
    assert show("next") == stop(TYPO)
    file = folder.menu_file("2026-W48")
    assert at(home, folder, "menu", "new", "2026-W48") == out(new(file, DATES["2026-W48"][0], BOTH))
    assert held(file) == menu_text("2026-W48", LUNCH_DINNER)
    assert show("2026-W48") == out(empty("2026-W48", Lang.EN, LUNCH_DINNER))
    no_menus_folder(folder.root)
    assert show("2026-W48") == stop(Prob("menus", None, FOLDER_MISSING))


def _traced(home: Path, root: Path, *argv: str) -> tuple[list[str], list[str], tuple]:
    """Runs a line inside a new fault harness and gives the record, the listings, and the result."""
    with faults(root) as state:
        result = at(home, root, *argv)
    return state.calls, state.listings, result


def _check_reads_of_the_week(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Checks lines 1 to 3 of F11-T27: the order of the reads, and a week that has no menu."""
    root = example.root
    for argv, shown in (((), SHOW_47), (("--lang", "zh"), SHOW_47_ZH)):
        record, listings, result = _traced(home, root, "menu", "show", "2026-W47", *argv)
        assert (record, listings, result) == (R47, LISTINGS, out(shown))
    b = made(example, tmp_path, "b", week_b)
    reads = [SETTINGS, CATALOG, "read menus/2026-W48.toml"]
    reads += [
        f"read recipes/{r}.toml" for r in ("mapo-tofu", "rice", "choy-sum", "red-braised-pork")
    ]
    assert _traced(home, b, "menu", "show", "2026-W48") == (reads, LISTINGS, out(BLOCK_A))
    expected = ([SETTINGS, CATALOG], LISTINGS, err(1, [no_menu("2026-W48")]))
    assert _traced(home, root, "menu", "show", "2026-W48") == expected


def _check_wrong_week_and_help(home: Path, example: DataFolder) -> None:
    """Checks line 4 of F11-T27: a wrong week reads one file, and ``--help`` runs nothing."""
    expected = ([SETTINGS], [], err(2, [not_a_week("2026-W99")]))
    assert _traced(home, example.root, "menu", "show", "2026-W99") == expected
    help_text = at(home, None, "--help")[1]
    shown = _traced(home, example.root, "menu", "show", "2026-W47", "--help")
    assert shown == ([SETTINGS], [], (0, help_text, ""))


def _check_errors(home: Path, example: DataFolder, tmp_path: Path) -> None:
    """Checks line 5 of F11-T27: the files that ``menu show`` reads before each error."""
    week48 = Prob("menus/2026-w48.toml", None, NOT_A_WEEK_NAME)

    def small(root: Path) -> None:
        """Writes the empty file ``menus/2026-w48.toml``."""
        write(root / "menus" / "2026-w48.toml", "")

    inputs = [
        (catalog_brace, [SETTINGS, CATALOG], [], E_BRACE),
        (rice_bowl, [SETTINGS, CATALOG], ["recipes"], E_RICE_BOWL),
        (small, [SETTINGS, CATALOG], LISTINGS, week48),
        (the_typo, [SETTINGS, CATALOG, "read menus/2026-W47.toml"], LISTINGS, TYPO),
        (mapo_mistake, R47[:7], LISTINGS, E_MAPO),
    ]
    for number, (change, reads, listings, problem) in enumerate(inputs):
        root = made(example, tmp_path, f"e{number}", change)
        got = _traced(home, root, "menu", "show", "2026-W47")
        assert got == (reads, listings, stop(problem)), number


def _check_new_reads(home: Path, example: DataFolder) -> None:
    """Checks line 6 of F11-T27: ``menu new`` reads no file and lists ``menus/`` once."""
    root = example.root
    file = example.menu_file("2026-W48")
    created = out(new(file, DATES["2026-W48"][0], BOTH))
    expected = ([SETTINGS, "open menus/2026-W48.toml"], ["menus"], created)
    assert _traced(home, root, "menu", "new", "2026-W48") == expected
    refused = err(1, [exists(example.menu_file("2026-W47"))])
    assert _traced(home, root, "menu", "new", "2026-W47") == ([SETTINGS], ["menus"], refused)
    expected = ([SETTINGS], [], err(2, [not_a_week("2026-W99")]))
    assert _traced(home, root, "menu", "new", "2026-W99") == expected
    assert held(file) == menu_text("2026-W48", LUNCH_DINNER)


def test_f11_t27_each_command_reads_only_the_files_that_it_needs_and_reads_each_once(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The record of the reads and the listings for both commands, and the plain run."""
    home = make_home(tmp_path)
    _check_reads_of_the_week(home, example_folder, tmp_path)
    _check_wrong_week_and_help(home, example_folder)
    _check_errors(home, example_folder, tmp_path)
    _check_new_reads(home, example_folder)
    assert at(home, example_folder, "menu", "show", "2026-W47") == out(SHOW_47)
