"""Tests of F10 for the widths of the table and for the error that stops ``search`` (T12, T13)."""

from functools import partial
from pathlib import Path

from f05_support import make_home
from f07_changes import catalog_brace, mapo_mistake
from f09_support import (
    assert_among_check,
    at,
    capital_rice,
    empty_recipes,
    folder_x,
    long_name,
    made,
    mapo_and_rice_at_0,
    no_catalog,
    no_recipes_folder,
    not_recipes,
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
    EN,
    ZH,
    stop,
)
from f10_support import lines_of, searches
from f10_texts import BLOCK_A, BLOCK_E, MAPO_FOUND, PORK_FOUND, found, none
from recipe_menu.datafile import DataFolder

# The escapes of a line break, as the file holds them with their backslashes.
LINE_BREAKS = [r"\n", r"\r\n", r"\u2028"]
RICE_TABLE_ZH = ["ID     名称   匹配于", "rice   米饭   名称、食材"]
# The inputs 1 to 11 of F10-T13: the changes, and the problem that stops ``search``.
STOPPED = [
    ([no_catalog], E_NO_CATALOG),
    ([catalog_brace], E_BRACE),
    ([no_recipes_folder], E_NO_RECIPES),
    ([recipes_as_file], E_RECIPES_FILE),
    ([rice_bowl], E_RICE_BOWL),
    ([capital_rice], E_CAPITAL),
    ([folder_x], E_FOLDER_X),
    ([mapo_mistake], E_MAPO),
    ([mapo_and_rice_at_0], E_MAPO),
    ([mapo_mistake, rice_bowl], E_RICE_BOWL),
    ([catalog_brace, mapo_mistake], E_BRACE),
]


def test_f10_t12_each_column_is_as_wide_as_its_own_cells_and_a_name_takes_its_lines(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A narrow result stays narrow, and a name with a line break takes two lines."""
    home = make_home(tmp_path)
    searches(
        home,
        example_folder,
        [
            (("mapo",), MAPO_FOUND),
            *lines_of(BLOCK_A, ("mapo", "--lang", "zh"), ("rice",)),
            (("rice", "--lang", "zh"), found(RICE_TABLE_ZH, "1 个菜谱匹配“rice”。")),
            *lines_of(BLOCK_A, ("spicy",), ("cola",), ("cola", "--lang", "zh")),
        ],
    )
    heading = at(home, example_folder, "search", "mapo")[1].split("\n")[0]
    assert heading.index("Name") == 12
    for number, line_break in enumerate(LINE_BREAKS):
        change = partial(long_name, escape=line_break)
        folder = made(example_folder, tmp_path, f"long{number}", change)
        searches(home, folder, list(BLOCK_E.items()))


def test_f10_t13_an_error_stops_search_at_the_first_error_and_a_warning_changes_nothing(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The catalog, the listing, then the recipes in the order of the IDs, and the folders."""
    home = make_home(tmp_path)
    for number, (changes, problem) in enumerate(STOPPED):
        root = made(example_folder, tmp_path, f"stopped{number}", *changes)
        for words, lang in ((("番茄",), EN), (("lamb",), EN), (("番茄", "--lang", "zh"), ZH)):
            assert at(home, root, "search", *words) == stop(problem, lang), (number, words)
        assert_among_check(home, root, problem)
    empty = made(example_folder, tmp_path, "empty", empty_recipes)
    searches(
        home,
        empty,
        [
            (("番茄",), none('No recipe matches "番茄".')),
            (("番茄", "--lang", "zh"), none("没有菜谱匹配“番茄”。")),
            (("番茄", "quick"), none('No recipe matches "番茄" and "quick".')),
        ],
    )
    other = made(example_folder, tmp_path, "other", not_recipes)
    searches(home, other, [(("番茄",), none('No recipe matches "番茄".'))])
    searches(home, example_folder, [(("pork",), PORK_FOUND)])
