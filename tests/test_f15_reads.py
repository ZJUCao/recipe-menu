"""Tests of F15 for what add reads before it asks, and what it reads and writes (T19, T20)."""

from collections.abc import Callable
from pathlib import Path

from f05_support import make_home, record
from f05_texts import ZH, lines_text
from f07_changes import catalog_brace, mapo_mistake, pantry_not_text, the_typo
from f07_texts import Prob
from f09_support import (
    assert_among_check,
    capital_rice,
    no_catalog,
    no_recipes_folder,
    recipes_as_file,
    rice_bowl,
)
from f09_texts import (
    E_BRACE,
    E_CAPITAL,
    E_NO_CATALOG,
    E_NO_RECIPES,
    E_RECIPES_FILE,
    E_RICE_BOWL,
    NOT_A_RECIPE_ID_FILE,
    TOML_ENDING_NOT_SMALL,
    stop,
)
from f11_support import no_menus_folder
from f13_support import READ_SETTINGS, pristine
from f15_support import BASE, Watched, add, entry, fresh, listing, recipe_names, traced_add
from f15_texts import ID_PROMPT, base_out, id_exists
from recipe_menu.datafile import DataFolder

type Change = Callable[[Path], None]

E_CAPITAL_GARLIC = Prob("recipes/garlic-broccoli.TOML", None, TOML_ENDING_NOT_SMALL)
E_GARLIC = Prob("recipes/Garlic-Broccoli.toml", None, NOT_A_RECIPE_ID_FILE)
CASES: list[tuple[tuple[Change, ...], Prob]] = [
    ((no_catalog,), E_NO_CATALOG),
    ((catalog_brace,), E_BRACE),
    ((no_recipes_folder,), E_NO_RECIPES),
    ((recipes_as_file,), E_RECIPES_FILE),
    ((rice_bowl,), E_RICE_BOWL),
    ((capital_rice,), E_CAPITAL),
    ((entry("Garlic-Broccoli.toml"),), E_GARLIC),
    ((entry("garlic-broccoli.TOML"),), E_CAPITAL_GARLIC),
    ((no_catalog, no_recipes_folder), E_NO_CATALOG),
    ((catalog_brace, rice_bowl), E_BRACE),
]


def test_f15_t19_the_first_error_of_the_catalog_or_the_listing_stops_add_before_it_asks(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Eleven lines: the stop lines of ten folders, and the Chinese lines of two of them."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    for number, (changes, problem) in enumerate(CASES, 1):
        folder = fresh(source, tmp_path, f"line-{number}", *changes)
        before = record(folder.root)
        assert add(home, folder, Watched()) == stop(problem), number
        assert record(folder.root) == before, number
        assert_among_check(home, folder.root, problem)
    for number in (2, 7):
        changes, problem = CASES[number - 1]
        folder = fresh(source, tmp_path, f"zh-{number}", *changes)
        before = record(folder.root)
        assert add(home, folder, Watched(), "--lang", "zh") == stop(problem, ZH), number
        assert record(folder.root) == before, number
        assert_among_check(home, folder.root, problem)


def test_f15_t20_add_reads_the_catalog_lists_the_recipes_and_reads_nothing_else(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: the record of the reads and the listings, with mistakes in other files."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    reads = [
        READ_SETTINGS,
        "read catalog.toml",
        "open recipes/new-dish.toml",
        "read catalog.toml",
        "read recipes/new-dish.toml",
    ]
    variants = (
        ("one", ()),
        ("two", (mapo_mistake, the_typo, pantry_not_text)),
        ("three", (no_menus_folder,)),
    )
    for name, changes in variants:
        folder = fresh(source, tmp_path, name, *changes)
        result, calls, listings = traced_add(home, folder, BASE)
        assert result == (0, lines_text(*base_out(folder)), ""), name
        assert (calls, listings) == (reads, ["recipes", "recipes"]), name
        assert recipe_names(folder) == listing("new-dish.toml"), name
    folder = fresh(source, tmp_path, "four")
    result, calls, listings = traced_add(home, folder, ["tomato-egg", ""])
    lines = [ID_PROMPT[0] + "tomato-egg", id_exists("tomato-egg")[0], ID_PROMPT[0]]
    assert result == (0, lines_text(*lines), "")
    assert (calls, listings) == ([READ_SETTINGS, "read catalog.toml"], ["recipes"])
