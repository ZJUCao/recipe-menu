"""Tests of F09 for the widths of ``list``, a missing language, and an error that stops it."""

from pathlib import Path

from f05_support import make_home
from f07_changes import catalog_brace, mapo_mistake
from f09_support import (
    assert_among_check,
    at,
    capital_rice,
    extra_recipes,
    folder_x,
    long_name,
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
    EXTRA,
    EXTRA_VEG,
    EXTRA_ZH,
    LONG,
    LONG_QUICK,
    LONG_QUICK_ZH,
    LONG_STAPLE,
    LONG_STAPLE_ZH,
    LONG_ZH,
    ZH,
    out,
    stop,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.text import display_width

# The six commands of F09-T09 and the output of each.
LONG_RUNS = [
    (("list",), LONG),
    (("list", "--tag", "staple"), LONG_STAPLE),
    (("list", "--tag", "quick"), LONG_QUICK),
    (("list", "--lang", "zh"), LONG_ZH),
    (("list", "--tag", "主食", "--lang", "zh"), LONG_STAPLE_ZH),
    (("list", "--tag", "快手", "--lang", "zh"), LONG_QUICK_ZH),
]
# The escapes of a line break, as the file holds them with their backslashes.
LINE_BREAKS = ["\\n", "\\r\\n", "\\u2028"]


def _assert_columns(text: str, zh: bool) -> None:
    """Checks where the Name and Servings columns start in the heading of a table."""
    heading = text.split("\n", maxsplit=1)[0]
    name, servings = ("名称", "份数") if zh else ("Name", "Servings")
    assert display_width(heading[: heading.index(name)]) == 9
    assert display_width(heading[: heading.index(servings)]) == (24 if zh else 29)


def test_f09_t09_a_name_of_two_lines_does_not_widen_the_tables_of_a_tag(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The widths take the lines of a cell, whichever line break the name holds."""
    home = make_home(tmp_path)
    for escape in LINE_BREAKS:
        root = made(
            example_folder, tmp_path, f"long{len(escape)}", lambda r, e=escape: long_name(r, e)
        )
        for argv, lines in LONG_RUNS:
            result = at(home, root, *argv)
            assert result == out(lines), (escape, argv)
            assert "\r" not in result[1] and "\u2028" not in result[1]
            _assert_columns(result[1], "zh" in argv)


def test_f09_t10_a_name_without_the_language_of_the_output_shows_the_other_one(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The extra recipes: a missing name, no tags, and the widths of the names that show."""
    home = make_home(tmp_path)
    root = made(example_folder, tmp_path, "extra", extra_recipes)
    assert at(home, root, "list") == out(EXTRA)
    assert at(home, root, "list", "--lang", "zh") == out(EXTRA_ZH)
    assert at(home, root, "list", "--tag", "vegetarian") == out(EXTRA_VEG)


# Each input of F09-T11: the changes, and the first error that stops ``list``.
ERROR_INPUTS = [
    ((no_catalog,), E_NO_CATALOG),
    ((catalog_brace,), E_BRACE),
    ((no_recipes_folder,), E_NO_RECIPES),
    ((recipes_as_file,), E_RECIPES_FILE),
    ((rice_bowl,), E_RICE_BOWL),
    ((capital_rice,), E_CAPITAL),
    ((folder_x,), E_FOLDER_X),
    ((mapo_mistake,), E_MAPO),
    ((mapo_and_rice_at_0,), E_MAPO),
    ((mapo_mistake, rice_bowl), E_RICE_BOWL),
]


def test_f09_t11_an_error_stops_list_at_the_first_error_that_check_also_reports(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The catalog, then the listing, then the recipes in the order of the IDs."""
    home = make_home(tmp_path)
    for number, (changes, error) in enumerate(ERROR_INPUTS, 1):
        root = made(example_folder, tmp_path, f"input{number}", *changes)
        assert at(home, root, "list") == stop(error), number
        assert at(home, root, "list", "--lang", "zh") == stop(error, ZH), number
        assert_among_check(home, root, error)
