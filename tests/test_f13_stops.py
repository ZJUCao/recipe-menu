"""Tests of F13 for shop when a file has an error or the week has no menu (T17, T18)."""

from collections.abc import Callable
from datetime import date
from functools import partial
from pathlib import Path

from f03_support import m_missing_key, write
from f05_support import make_home
from f06_support import mistakes
from f07_changes import (
    catalog_brace,
    edit,
    mapo_mistake,
    menu_path,
    pantry_not_text,
    pantry_sesame,
    servings_zero,
    the_typo,
)
from f07_texts import (
    ITEM_NOT_A_TEXT,
    NOT_A_WEEK_NAME,
    P_WEEK,
    TYPO,
    Prob,
    m_week_name,
    p_ingredient,
    p_item,
)
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
    FILE_MISSING,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    TOML_ENDING_NOT_SMALL,
    ZH,
    err,
    out,
    stop,
)
from f11_support import empty_menus, menus_as_file, no_menus_folder, on
from f11_texts import no_menu, no_menu_zh, not_a_week
from f13_support import (
    E_LOWER_48,
    E_PANTRY,
    empty_menu_file,
    empty_shopping,
    missing_name,
    no_pantry,
    pristine,
)
from f13_texts import shop_47
from recipe_menu.datafile import DataFolder

Change = Callable[[Path], None]
MENUS = "menus/2026-W47.toml"
PLAN = Prob("menus/plan.toml", None, NOT_A_WEEK_NAME)
UPPER = Prob("menus/2026-W48.TOML", None, TOML_ENDING_NOT_SMALL)
NAME_EN = Prob("catalog.toml", p_ingredient(22), m_missing_key("en"))
PANTRY_TEXT = Prob("pantry.toml", p_item(3), ITEM_NOT_A_TEXT)
WEEK_NAME = Prob(MENUS, P_WEEK, m_week_name("2026-W47", "2026-W48"))


def _menu_mistakes(root: Path) -> None:
    """Makes the three menu mistakes of v0.1-S07."""
    mistakes(DataFolder(root))


def _folder_x_dish(root: Path) -> None:
    """Makes the folder ``recipes/x.toml`` and adds ``"x"`` to Wednesday's dinner."""
    folder_x(root)
    old = "[wednesday]\nlunch = []\ndinner = []"
    edit(menu_path(root), old, '[wednesday]\nlunch = []\ndinner = ["x"]')


# Inputs 1 to 27 of F13-T17: the changes of the folder, and the error that stops shop.
STOPPED: list[tuple[list[Change], Prob]] = [
    ([no_catalog], E_NO_CATALOG),
    ([catalog_brace], E_BRACE),
    ([missing_name], NAME_EN),
    ([pantry_sesame], E_PANTRY),
    ([pantry_not_text], PANTRY_TEXT),
    ([no_pantry], Prob("pantry.toml", None, FILE_MISSING)),
    ([no_recipes_folder], E_NO_RECIPES),
    ([recipes_as_file], E_RECIPES_FILE),
    ([rice_bowl], E_RICE_BOWL),
    ([capital_rice], E_CAPITAL),
    ([no_menus_folder], Prob("menus", None, FOLDER_MISSING)),
    ([menus_as_file], Prob("menus", None, FOLDER_IS_FILE)),
    ([empty_menu_file("2026-w48.toml")], E_LOWER_48),
    ([empty_menu_file("plan.toml")], PLAN),
    ([empty_menu_file("2026-W48.TOML")], UPPER),
    ([the_typo], TYPO),
    ([_menu_mistakes], WEEK_NAME),
    ([mapo_mistake], E_MAPO),
    ([partial(servings_zero, recipe="rice")], E_RICE_ZERO),
    ([mapo_and_rice_at_0], E_RICE_ZERO),
    ([catalog_brace, pantry_sesame], E_BRACE),
    ([pantry_sesame, rice_bowl], E_PANTRY),
    ([pantry_sesame, no_menus_folder], E_PANTRY),
    ([rice_bowl, empty_menu_file("2026-w48.toml")], E_RICE_BOWL),
    ([empty_menu_file("2026-w48.toml"), the_typo], E_LOWER_48),
    ([the_typo, mapo_mistake], TYPO),
    ([_folder_x_dish], E_FOLDER_X),
]


def _breaks_week_48(root: Path) -> None:
    """Writes ``[[[`` in ``menus/2026-W48.toml``."""
    write(root / "menus" / "2026-W48.toml", "[[[\n")


def test_f13_t17_the_first_error_of_each_reader_stops_shop_in_the_order_of_the_readers(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Thirty-two inputs: the error that stops ``shop``, and the errors that do not."""
    home = make_home(tmp_path)
    for number, (changes, problem) in enumerate(STOPPED, 1):
        root = made(example_folder, tmp_path, f"in{number}", *changes)
        assert at(home, root, "shop", "2026-W47") == stop(problem), number
        shown = at(home, root, "shop", "2026-W47", "--lang", "zh")
        assert shown == stop(problem, ZH), number
        assert_among_check(home, root, problem)
        assert not (root / "shopping").exists(), number
    fine = [
        (28, [folder_x]),
        (29, [partial(servings_zero, recipe="red-braised-pork")]),
        (30, [_breaks_week_48]),
    ]
    for number, changes in fine:
        root = made(example_folder, tmp_path, f"in{number}", *changes)
        file = root / "shopping" / "2026-W47.md"
        assert at(home, root, "shop", "2026-W47") == out(shop_47(file)), number
    root = made(example_folder, tmp_path, "in31", empty_menu_file("2026-w48.toml"))
    assert at(home, root, "shop", "2026-W48") == stop(E_LOWER_48)
    root = made(example_folder, tmp_path, "in32", pantry_sesame)
    assert at(home, root, "shop", "2026-W48") == stop(E_PANTRY)


def _check_s15(home: Path, root: Path) -> None:
    """Input 1 of F13-T18: the lines of v0.1-S15 in English, and then ``shop`` in Chinese."""
    no_48 = err(1, [no_menu("2026-W48")])
    assert at(home, root, "menu", "show", "2026-W48") == no_48
    assert at(home, root, "menu", "show", "2026-W99") == err(2, [not_a_week("2026-W99")])
    assert at(home, root, "shop", "2026-W48") == no_48
    the_typo(root)
    assert at(home, root, "menu", "show", "2026-W47") == stop(TYPO)
    assert at(home, root, "shop", "2026-W47") == stop(TYPO)
    assert at(home, root, "shop", "2026-W48", "--lang", "zh") == err(1, [no_menu_zh("2026-W48")])
    assert at(home, root, "shop", "2026-W47", "--lang", "zh") == stop(TYPO, ZH)
    assert list((root / "shopping").iterdir()) == []


def _not_menus(root: Path) -> None:
    """Adds to ``menus/`` a backup with the bytes of week 47, a folder, and a text file."""
    week47 = (root / "menus" / "2026-W47.toml").read_bytes()
    (root / "menus" / "2026-W48.toml.bak").write_bytes(week47)
    (root / "menus" / "2026-W48").mkdir()
    write(root / "menus" / "notes.txt", "Ideas\n")


def test_f13_t18_a_week_with_no_menu_file_gives_no_menu_and_exit_code_1(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The lines of v0.1-S15, this and next week, names that are not menus, and the readers."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    _check_s15(home, made(source, tmp_path, "s15", empty_shopping))
    assert at(home, example_folder, "shop") == err(1, [no_menu("2026-W46")])
    assert at(home, example_folder, "shop", "this", "--lang", "zh") == err(
        1, [no_menu_zh("2026-W46")]
    )
    assert on(home, example_folder, date(2026, 11, 17), "shop", "next") == err(
        1, [no_menu("2026-W48")]
    )
    assert not example_folder.shopping.exists()
    others = made(source, tmp_path, "others", _not_menus)
    assert at(home, others, "shop", "2026-W48") == err(1, [no_menu("2026-W48")])
    empty = made(source, tmp_path, "empty", empty_menus)
    assert at(home, empty, "shop", "2026-W47") == err(1, [no_menu("2026-W47")])
    cases = [(catalog_brace, E_BRACE), (no_recipes_folder, E_NO_RECIPES), (rice_bowl, E_RICE_BOWL)]
    for number, (change, problem) in enumerate(cases):
        root = made(source, tmp_path, f"reader{number}", change)
        assert at(home, root, "shop", "2026-W48") == stop(problem), number
    for name in ("others", "empty", "reader0", "reader1", "reader2"):
        assert not (tmp_path / name / "shopping").exists(), name
