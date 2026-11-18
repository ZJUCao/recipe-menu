"""Tests of F14 for the first error, the reads of one run, and the order of the stops (T13-T15)."""

from collections.abc import Sequence
from pathlib import Path

from f03_support import M_ACCESS_DENIED
from f05_support import make_home, record
from f05_texts import ZH
from f06_support import mistakes
from f07_changes import catalog_brace, mapo_mistake, servings_zero, the_typo
from f07_texts import P_WEEK, TYPO, Prob, m_week_name
from f08_support import DENIED, rule
from f09_support import (
    assert_among_check,
    capital_rice,
    folder_x,
    made,
    mapo_and_rice_at_0,
    no_catalog,
    no_recipes_folder,
    recipes_as_file,
    rice_bowl,
)
from f09_texts import (
    E_BRACE,
    E_CAPITAL,
    E_FOLDER_X,
    E_MAPO,
    E_NO_CATALOG,
    E_NO_RECIPES,
    E_RECIPES_FILE,
    E_RICE_BOWL,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    err,
    out,
    stop,
)
from f11_support import menus_as_file, no_menus_folder
from f13_support import LISTINGS, READ_SETTINGS, Change, pristine
from f14_support import (
    EXAMPLE_FILES,
    FILE_47,
    IN_ZH,
    LUNCH_DINNER,
    READ_CATALOG,
    W47,
    WEEK_48,
    assert_no_write,
    menu_as,
    new_menu,
    reads,
    refuse_one,
    save_of,
    suggest,
    traced,
    week_line,
)
from f14_texts import R3, cannot, cannot_zh, some, tags
from recipe_menu.datafile import DataFolder

NO_MENUS = Prob("menus", None, FOLDER_MISSING)
MENUS_FILE = Prob("menus", None, FOLDER_IS_FILE)
MENU_WEEK = Prob(FILE_47, P_WEEK, m_week_name("2026-W47", "2026-W48"))


def _menu_mistakes(root: Path) -> None:
    """Makes the three menu mistakes of v0.1-S07 in a data folder."""
    mistakes(DataFolder(root))


def _rice_at_0(root: Path) -> None:
    """Gives ``recipes/rice.toml`` 0 servings."""
    servings_zero(root, "rice")


def _pork_at_0(root: Path) -> None:
    """Gives ``recipes/red-braised-pork.toml`` 0 servings."""
    servings_zero(root, "red-braised-pork")


# The inputs 1 to 13 of F14-T13: the name, the week, the change, and the first error.
INPUTS = [
    ("i01", WEEK_48, no_catalog, E_NO_CATALOG),
    ("i02", WEEK_48, catalog_brace, E_BRACE),
    ("i03", WEEK_48, no_recipes_folder, E_NO_RECIPES),
    ("i04", WEEK_48, recipes_as_file, E_RECIPES_FILE),
    ("i05", WEEK_48, rice_bowl, E_RICE_BOWL),
    ("i06", WEEK_48, capital_rice, E_CAPITAL),
    ("i07", WEEK_48, no_menus_folder, NO_MENUS),
    ("i08", WEEK_48, menus_as_file, MENUS_FILE),
    ("i09", W47, the_typo, TYPO),
    ("i10", W47, _menu_mistakes, MENU_WEEK),
    ("i11", WEEK_48, folder_x, E_FOLDER_X),
    ("i12", WEEK_48, mapo_mistake, E_MAPO),
    ("i13", WEEK_48, mapo_and_rice_at_0, E_MAPO),
]


def test_f14_t13_an_error_stops_the_run_at_the_first_error_and_writes_no_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Thirteen inputs in both languages, which ``check`` reports too, and two with no read."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    for name, week, change, problem in INPUTS:
        changes = (new_menu(WEEK_48, LUNCH_DINNER), change) if week == WEEK_48 else (change,)
        root = made(source, tmp_path, name, *changes)
        before = record(root)
        assert suggest(home, root, *week_line(week)) == stop(problem), name
        assert suggest(home, root, *week_line(week, *IN_ZH)) == stop(problem, ZH), name
        assert_among_check(home, root, problem)
        assert record(root) == before, name
    for name, change in (("i14", _rice_at_0), ("i15", mapo_mistake)):
        root = made(source, tmp_path, name, change)
        result = suggest(home, root, *week_line(W47))
        assert result == out(some(W47, 1, 10, 4, "left")), name


def test_f14_t14_the_run_reads_each_file_once_in_the_order_of_the_design(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: the reads of a fill, of seven recipes, of a mistake, and of a failure."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    first = made(source, tmp_path, "r1")
    result, calls, listings = traced(home, first, [], *week_line(W47))
    assert result == out(some(W47, 1, 10, 4, "left"))
    wanted = [READ_SETTINGS, READ_CATALOG]
    wanted += reads(FILE_47, FILE_47, "recipes/red-braised-pork.toml") + save_of(W47)
    assert calls == wanted
    assert listings == LISTINGS
    two_weeks = (new_menu(WEEK_48, LUNCH_DINNER), new_menu("2026-W49", LUNCH_DINNER))
    second = made(source, tmp_path, "r2", *two_weeks)
    result, calls, listings = traced(home, second, [], *week_line(WEEK_48))
    assert result == out(some(WEEK_48, 7, 14, 0, "left"))
    week_48 = "menus/2026-W48.toml"
    wanted = [READ_SETTINGS, READ_CATALOG, *reads(week_48, week_48, *EXAMPLE_FILES)]
    assert calls == wanted + save_of(WEEK_48)
    third = made(source, tmp_path, "r3", mapo_mistake, *two_weeks)
    result, calls, _ = traced(home, third, [], *week_line(WEEK_48))
    assert result == stop(E_MAPO)
    assert calls == [READ_SETTINGS, READ_CATALOG, *reads(week_48, week_48, *EXAMPLE_FILES[:3])]
    assert_no_write(calls)
    fourth = made(source, tmp_path, "r4")
    path = fourth / "menus" / "2026-W47.toml"
    before = path.read_bytes()
    denied = [rule("read", path, DENIED, how="later")]
    result, calls, _ = traced(home, fourth, denied, *week_line(W47))
    assert result == stop(Prob(FILE_47, None, M_ACCESS_DENIED))
    assert calls == [READ_SETTINGS, READ_CATALOG, *reads(FILE_47, FILE_47)]
    assert path.read_bytes() == before


def _stops(  # noqa: PLR0917 - the values of one input, in the order of the plan
    home: Path,
    source: DataFolder,
    tmp_path: Path,
    name: str,
    changes: Sequence[Change],
    week: str = W47,
    rest: Sequence[str] = (),
) -> tuple[tuple[int, str, str], Path]:
    """Makes a new example with the changes, runs the line, and checks that no file changed."""
    root = made(source, tmp_path, name, *changes)
    before = record(root)
    result = suggest(home, root, *week_line(week, *rest))
    assert record(root) == before, name
    return result, root


def test_f14_t15_the_first_step_that_finds_a_problem_gives_the_result(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven inputs: the catalog, the tag, the listings, the menu, the refusal, and a recipe."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    tag = ("--tag", "breakfast")
    one, _ = _stops(home, source, tmp_path, "n1", [no_catalog], rest=tag)
    assert one == stop(E_NO_CATALOG)
    two, _ = _stops(home, source, tmp_path, "n2", [no_recipes_folder], rest=tag)
    assert two == err(1, [tags("breakfast")])
    three, _ = _stops(home, source, tmp_path, "n3", [no_recipes_folder, no_menus_folder])
    assert three == stop(E_NO_RECIPES)
    four, _ = _stops(home, source, tmp_path, "n4", [catalog_brace, the_typo])
    assert four == stop(E_BRACE)
    five, _ = _stops(home, source, tmp_path, "n5", [rice_bowl, the_typo])
    assert five == stop(E_RICE_BOWL)
    six, root = _stops(home, source, tmp_path, "n6", [refuse_one, _pork_at_0])
    assert six == err(1, cannot(W47))
    kept = record(root)
    assert suggest(home, root, *week_line(W47, *IN_ZH)) == err(1, cannot_zh(W47))
    assert record(root) == kept
    seven, _ = _stops(
        home, source, tmp_path, "n7", [menu_as("2026-W49", R3), mapo_mistake], "2026-W49"
    )
    assert seven == stop(E_MAPO)
