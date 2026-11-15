"""Tests of F11 for menu show when a file has an error or the week has no menu (T28, T29)."""

from collections.abc import Callable
from datetime import date
from functools import partial
from pathlib import Path

from f03_support import write
from f05_support import make_home
from f06_support import mistakes
from f07_changes import (
    catalog_brace,
    edit,
    mapo_mistake,
    menu_path,
    servings_zero,
    the_typo,
)
from f07_texts import NOT_A_WEEK_NAME, P_WEEK, TYPO, Prob, m_week_name
from f09_support import (
    assert_among_check,
    at,
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
    E_RICE_ZERO,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    TOML_ENDING_NOT_SMALL,
    ZH,
    err,
    out,
    stop,
)
from f11_support import empty_menus, menus_as_file, no_menus_folder, on
from f11_texts import SHOW_47, no_menu, no_menu_zh, not_a_week, not_a_week_zh
from recipe_menu.datafile import DataFolder

Change = Callable[[Path], None]


def _empty(name: str) -> Change:
    """Gives the change that writes the empty file ``menus/<name>``."""
    return lambda root: write(root / "menus" / name, "")


def _menu_mistakes(root: Path) -> None:
    """Makes the three menu mistakes of v0.1-S07."""
    mistakes(DataFolder(root))


def _rice_at_0(root: Path) -> None:
    """Replaces the servings of ``rice`` by 0."""
    servings_zero(root, "rice")


def _folder_x_dish(root: Path) -> None:
    """Makes the folder ``recipes/x.toml`` and adds ``"x"`` to Wednesday's dinner."""
    folder_x(root)
    old = "[wednesday]\nlunch = []\ndinner = []"
    edit(menu_path(root), old, '[wednesday]\nlunch = []\ndinner = ["x"]')


MENUS = "menus/2026-W47.toml"
LOWER_48 = Prob("menus/2026-w48.toml", None, NOT_A_WEEK_NAME)
WEEK_NAME = m_week_name("2026-W47", "2026-W48")
# Inputs 1 to 21 of F11-T28: the changes of the folder, and the error that stops menu show.
STOPPED: list[tuple[list[Change], Prob]] = [
    ([no_catalog], E_NO_CATALOG),
    ([catalog_brace], E_BRACE),
    ([no_recipes_folder], E_NO_RECIPES),
    ([recipes_as_file], E_RECIPES_FILE),
    ([rice_bowl], E_RICE_BOWL),
    ([capital_rice], E_CAPITAL),
    ([no_menus_folder], Prob("menus", None, FOLDER_MISSING)),
    ([menus_as_file], Prob("menus", None, FOLDER_IS_FILE)),
    ([_empty("2026-w48.toml")], LOWER_48),
    ([_empty("plan.toml")], Prob("menus/plan.toml", None, NOT_A_WEEK_NAME)),
    ([_empty("2026-W48.TOML")], Prob("menus/2026-W48.TOML", None, TOML_ENDING_NOT_SMALL)),
    ([the_typo], TYPO),
    ([_menu_mistakes], Prob(MENUS, P_WEEK, WEEK_NAME)),
    ([mapo_mistake], E_MAPO),
    ([_rice_at_0], E_RICE_ZERO),
    ([mapo_and_rice_at_0], E_RICE_ZERO),
    ([catalog_brace, the_typo], E_BRACE),
    ([rice_bowl, _empty("2026-w48.toml")], E_RICE_BOWL),
    ([_empty("2026-w48.toml"), the_typo], LOWER_48),
    ([the_typo, mapo_mistake], TYPO),
    ([_folder_x_dish], E_FOLDER_X),
]


def test_f11_t28_the_first_error_of_each_reader_stops_menu_show_in_the_order_of_the_readers(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Twenty-five inputs: the error that stops ``menu show``, and the errors that do not."""
    home = make_home(tmp_path)
    for number, (changes, problem) in enumerate(STOPPED, 1):
        root = made(example_folder, tmp_path, f"in{number}", *changes)
        assert at(home, root, "menu", "show", "2026-W47") == stop(problem), number
        shown = at(home, root, "menu", "show", "2026-W47", "--lang", "zh")
        assert shown == stop(problem, ZH), number
        assert_among_check(home, root, problem)
    fine = [
        (22, [folder_x]),
        (23, [partial(servings_zero, recipe="red-braised-pork")]),
        (24, [_broken_pantry_and_week]),
    ]
    for number, changes in fine:
        root = made(example_folder, tmp_path, f"in{number}", *changes)
        assert at(home, root, "menu", "show", "2026-W47") == out(SHOW_47), number
    root = made(example_folder, tmp_path, "in25", _empty("2026-w48.toml"))
    assert at(home, root, "menu", "show", "2026-W48") == stop(LOWER_48)


def _broken_pantry_and_week(root: Path) -> None:
    """Writes ``[[[`` in the pantry and in the menu of week 48."""
    write(root / "pantry.toml", "[[[\n")
    write(root / "menus" / "2026-W48.toml", "[[[\n")


def _first_input(home: Path, example: DataFolder) -> None:
    """Runs input 1 of F11-T29: the lines of v0.1-S15 in English, and then in Chinese."""
    expected = {
        "": [err(1, [no_menu("2026-W48")]), err(2, [not_a_week("2026-W99")]), stop(TYPO)],
        "zh": [
            err(1, [no_menu_zh("2026-W48")]),
            err(2, [not_a_week_zh("2026-W99")]),
            stop(TYPO, ZH),
        ],
    }
    lang: list[str] = []
    for key in ("", "zh"):
        if key:
            lang = ["--lang", key]
        first = at(home, example, "menu", "show", "2026-W48", *lang)
        second = at(home, example, "menu", "show", "2026-W99", *lang)
        if not key:
            the_typo(example.root)
        third = at(home, example, "menu", "show", "2026-W47", *lang)
        assert [first, second, third] == expected[key], key


def _not_menus(root: Path) -> None:
    """Adds to ``menus/`` a backup with the bytes of week 47, a folder, and a text file."""
    week47 = (root / "menus" / "2026-W47.toml").read_bytes()
    (root / "menus" / "2026-W48.toml.bak").write_bytes(week47)
    (root / "menus" / "2026-W48").mkdir()
    write(root / "menus" / "notes.txt", "Ideas\n")


def test_f11_t29_a_week_with_no_menu_file_gives_no_menu_and_exit_code_1(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The lines of v0.1-S15, this and next week, names that are not menus, and the readers."""
    home = make_home(tmp_path)
    _first_input(home, example_folder)
    assert at(home, example_folder, "menu", "show") == err(1, [no_menu("2026-W46")])
    assert at(home, example_folder, "menu", "show", "this", "--lang", "zh") == err(
        1, [no_menu_zh("2026-W46")]
    )
    assert on(home, example_folder, date(2026, 11, 17), "menu", "show", "next") == err(
        1, [no_menu("2026-W48")]
    )
    others = made(example_folder, tmp_path, "others", _not_menus)
    assert at(home, others, "menu", "show", "2026-W48") == err(1, [no_menu("2026-W48")])
    empty_root = made(example_folder, tmp_path, "empty", empty_menus)
    assert at(home, empty_root, "menu", "show", "2026-W47") == err(1, [no_menu("2026-W47")])
    for number, (change, problem) in enumerate(
        [(catalog_brace, E_BRACE), (no_recipes_folder, E_NO_RECIPES), (rice_bowl, E_RICE_BOWL)]
    ):
        root = made(example_folder, tmp_path, f"reader{number}", change)
        assert at(home, root, "menu", "show", "2026-W48") == stop(problem), number
