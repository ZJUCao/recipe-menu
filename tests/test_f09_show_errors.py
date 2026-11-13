"""Tests of F09 for the errors of ``recipe-menu show``: the ID, ``--servings``, and the files."""

from pathlib import Path

from f05_support import make_home
from f07_changes import catalog_brace
from f09_support import (
    WRONG_IDS,
    WRONG_SERVINGS,
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
    FOUR_ZH,
    MAPO_ZH,
    PORK,
    RICE,
    ZH,
    err,
    not_a_recipe_id,
    out,
    servings_not_1_to_100,
    stop,
    unknown_id,
)
from recipe_menu.datafile import DataFolder


def test_f09_t16_an_id_that_cannot_be_an_id_gives_exit_code_2_and_one_that_has_no_file_gives_1(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """``NOT_A_RECIPE_ID`` before any read, and ``UNKNOWN_ID`` after the catalog and listing."""
    home = make_home(tmp_path)
    for wrong in WRONG_IDS:
        assert at(home, example_folder, "show", wrong) == err(2, [not_a_recipe_id(wrong)]), wrong
    zh = at(home, example_folder, "show", "Mapo", "--lang", "zh")
    assert zh == err(2, [not_a_recipe_id("Mapo", ZH)])
    for missing in ("mapo", "com10", "console", "2-minute-noodles", "a", "9" * 5000):
        result = at(home, example_folder, "show", missing)
        assert result == err(1, [unknown_id(missing)]), missing
    assert at(home, example_folder, "show", "mapo", "--lang", "zh") == err(1, [MAPO_ZH])
    bare = made(example_folder, tmp_path, "bare", no_catalog)
    assert at(home, bare, "show", "Mapo") == err(2, [not_a_recipe_id("Mapo")])
    assert at(home, bare, "show", "mapo") == stop(E_NO_CATALOG)
    no_folder = made(example_folder, tmp_path, "no_folder", no_recipes_folder)
    assert at(home, no_folder, "show", "mapo") == stop(E_NO_RECIPES)
    bowl = made(example_folder, tmp_path, "bowl", rice_bowl)
    assert at(home, bowl, "show", "mapo") == stop(E_RICE_BOWL)


def test_f09_t17_a_wrong_servings_gives_exit_code_2_before_the_id_and_before_any_read(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """Every wrong value is written as typed, in one line with no hint."""
    home = make_home(tmp_path)
    for wrong in WRONG_SERVINGS:
        result = at(home, example_folder, "show", "tomato-egg", "--servings", wrong)
        assert result == err(2, [servings_not_1_to_100(wrong)]), wrong
    zh = at(home, example_folder, "show", "tomato-egg", "--servings", "0", "--lang", "zh")
    assert zh == err(2, [servings_not_1_to_100("0", ZH)])
    zero = err(2, [servings_not_1_to_100("0")])
    assert at(home, example_folder, "show", "Mapo", "--servings", "0") == zero
    big = err(2, [servings_not_1_to_100("101")])
    assert at(home, example_folder, "show", "mapo", "--servings", "101") == big
    bare = made(example_folder, tmp_path, "bare", no_catalog)
    leading = err(2, [servings_not_1_to_100("04")])
    assert at(home, bare, "show", "tomato-egg", "--servings", "04") == leading


# Each input of F09-T18: the changes, the runs with their results, and the errors to find.
ERROR_INPUTS = [
    (
        [no_catalog],
        [
            (("show", "tomato-egg"), stop(E_NO_CATALOG)),
            (("show", "tomato-egg", "--lang", "zh"), stop(E_NO_CATALOG, ZH)),
        ],
        [E_NO_CATALOG],
    ),
    ([catalog_brace], [(("show", "rice", "--lang", "zh"), stop(E_BRACE, ZH))], [E_BRACE]),
    ([recipes_as_file], [(("show", "rice"), stop(E_RECIPES_FILE))], [E_RECIPES_FILE]),
    ([rice_bowl], [(("show", "tomato-egg"), stop(E_RICE_BOWL))], [E_RICE_BOWL]),
    (
        [capital_rice],
        [
            (("show", "rice"), stop(E_CAPITAL)),
            (("show", "tomato-egg", "--lang", "zh"), stop(E_CAPITAL, ZH)),
        ],
        [E_CAPITAL],
    ),
    (
        [folder_x],
        [(("show", "x"), stop(E_FOLDER_X)), (("show", "rice"), out(RICE))],
        [E_FOLDER_X],
    ),
    (
        [mapo_and_rice_at_0],
        [
            (("show", "mapo-tofu"), stop(E_MAPO)),
            (("show", "mapo-tofu", "--lang", "zh"), stop(E_MAPO, ZH)),
            (("show", "rice"), stop(E_RICE_ZERO)),
            (("show", "tomato-egg", "--servings", "4", "--lang", "zh"), out(FOUR_ZH)),
            (("show", "red-braised-pork"), out(PORK)),
        ],
        [E_MAPO, E_RICE_ZERO],
    ),
]


def test_f09_t18_an_error_stops_show_at_the_first_error_of_a_file_that_it_reads(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The catalog, the listing, and the recipe's own file stop ``show``, and no other file."""
    home = make_home(tmp_path)
    for number, (changes, runs, errors) in enumerate(ERROR_INPUTS, 1):
        root = made(example_folder, tmp_path, f"input{number}", *changes)
        for argv, result in runs:
            assert at(home, root, *argv) == result, (number, argv)
        assert_among_check(home, root, *errors)
