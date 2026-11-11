"""Tests of F03 for read_pantry (F03-T72 to F03-T78)."""

from pathlib import Path

from f03_support import (
    IN_PANTRY,
    M_FILE_IS_FOLDER,
    M_FILE_MISSING,
    M_ITEM_EMPTY,
    M_ITEM_NOT_A_TEXT,
    M_MISSING_BRACKET,
    PANTRY_FILE,
    at_item,
    at_line,
    check_problems,
    m_missing_key,
    m_not_a_list,
    m_unknown_ingredient,
    m_unknown_pantry_key,
    pantry_catalog,
    salt,
    sugar,
    write,
)
from recipe_menu.catalog import Pantry, read_catalog, read_pantry
from recipe_menu.datafile import DataFolder


def test_f03_t72_the_example_pantry_gives_five_ingredients_of_the_catalog(
    example_folder: DataFolder,
) -> None:
    """Each ingredient of the pantry is an object of the catalog."""
    catalog, _ = read_catalog(example_folder)
    assert catalog is not None
    pantry, problems = read_pantry(example_folder, catalog)
    assert problems == ()
    assert isinstance(pantry, Pantry)
    assert isinstance(pantry.ingredients, frozenset)
    assert len(pantry.ingredients) == 5
    names = {ingredient.name.en for ingredient in pantry.ingredients}
    assert names == {"Cooking oil", "Salt", "Sugar", "Soy sauce", "Sichuan pepper"}
    wanted = {id(catalog.ingredients[number]) for number in (13, 14, 15, 16, 19)}
    assert {id(ingredient) for ingredient in pantry.ingredients} == wanted
    assert catalog.find_ingredient("Salt") in pantry.ingredients


def test_f03_t73_the_design_example_with_and_without_the_catalog(
    example_folder: DataFolder,
) -> None:
    """An unknown name, an item that is not a text, and an item of whitespace."""
    write(example_folder.pantry, 'pantry = ["食用油", "Salt", "sesame oil", 3, " "]\n')
    catalog, _ = read_catalog(example_folder)
    pantry, problems = read_pantry(example_folder, catalog)
    assert pantry is not None
    assert {ingredient.name.en for ingredient in pantry.ingredients} == {"Cooking oil", "Salt"}
    unknown = (at_item(3), m_unknown_ingredient("sesame oil"))
    shape = [(at_item(4), M_ITEM_NOT_A_TEXT), (at_item(5), M_ITEM_EMPTY)]
    check_problems(problems, PANTRY_FILE, [unknown, *shape])
    pantry, problems = read_pantry(example_folder, None)
    assert pantry is None
    check_problems(problems, PANTRY_FILE, shape)


def test_f03_t74_a_problem_of_read_toml_gives_no_pantry_and_only_that_problem(
    tmp_path: Path,
) -> None:
    """A missing file, a folder, and a missing comma, with a catalog or with ``None``."""
    missing = DataFolder(tmp_path / "missing")
    isfolder = DataFolder(tmp_path / "isfolder")
    isfolder.pantry.mkdir(parents=True)
    syntax = DataFolder(tmp_path / "syntax")
    write(syntax.pantry, 'pantry = ["盐" "糖"]\n')
    cases = [
        (missing, None, M_FILE_MISSING),
        (isfolder, None, M_FILE_IS_FOLDER),
        (syntax, at_line(1), M_MISSING_BRACKET),
    ]
    for folder, place, msg in cases:
        for catalog in (pantry_catalog, None):
            pantry, problems = read_pantry(folder, catalog)
            assert pantry is None
            check_problems(problems, PANTRY_FILE, [(place, msg)])


def test_f03_t75_the_list_that_is_missing_or_wrong_reads_as_empty(folder: DataFolder) -> None:
    """``MISSING_KEY``, ``NOT_A_LIST``, and an unknown key at the top, after the items."""
    missing = (None, m_missing_key("pantry"))
    not_a_list = (IN_PANTRY, m_not_a_list("pantry"))
    empty = Pantry(frozenset())
    cases = [
        ('items = ["盐"]\n', empty, [missing, (None, m_unknown_pantry_key("items"))]),
        ("", empty, [missing]),
        ('pantry = "盐"\n', empty, [not_a_list]),
        ("[pantry]\nsalt = true\n", empty, [not_a_list]),
        ("pantry = []\n", empty, []),
        (
            'note = "x"\npantry = ["盐", 3]\n',
            Pantry(frozenset({salt})),
            [(at_item(2), M_ITEM_NOT_A_TEXT), (None, m_unknown_pantry_key("note"))],
        ),
    ]
    for text, pantry_wanted, problems_wanted in cases:
        write(folder.pantry, text)
        pantry, problems = read_pantry(folder, pantry_catalog)
        assert pantry == pantry_wanted
        check_problems(problems, PANTRY_FILE, problems_wanted)


def test_f03_t76_an_item_that_is_not_a_text_or_is_empty_is_skipped_and_counted(
    folder: DataFolder,
) -> None:
    """The numbering counts the skipped items."""
    write(
        folder.pantry,
        'pantry = [3, true, ["盐"], { zh = "盐" }, "", " ", "\u3000", "\t", "盐", 1.5]\n',
    )
    pantry, problems = read_pantry(folder, pantry_catalog)
    assert pantry == Pantry(frozenset({salt}))
    not_text = [at_item(number) for number in (1, 2, 3, 4, 10)]
    empty = [at_item(number) for number in (5, 6, 7, 8)]
    wanted = [(place, M_ITEM_NOT_A_TEXT) for place in not_text[:4]]
    wanted += [(place, M_ITEM_EMPTY) for place in empty]
    wanted.append((not_text[4], M_ITEM_NOT_A_TEXT))
    check_problems(problems, PANTRY_FILE, wanted)


def test_f03_t77_each_item_is_found_by_the_rules_of_design_2_6(folder: DataFolder) -> None:
    """An ingredient that several items name is in the set once, with no problem."""
    items = '"SALT", " salt\u3000", "盐", "Sa lt", "盐\u200b", "\uff33alt", "sugar", " sesame oil "'
    write(folder.pantry, f"pantry = [{items}]\n")
    pantry, problems = read_pantry(folder, pantry_catalog)
    assert pantry == Pantry(frozenset({salt, sugar}))
    assert {id(ingredient) for ingredient in pantry.ingredients} == {id(salt), id(sugar)}
    check_problems(
        problems,
        PANTRY_FILE,
        [
            (at_item(4), m_unknown_ingredient("Sa lt")),
            (at_item(5), m_unknown_ingredient("盐\u200b")),
            (at_item(6), m_unknown_ingredient("\uff33alt")),
            (at_item(8), m_unknown_ingredient("sesame oil")),
        ],
    )


def test_f03_t78_with_no_catalog_only_the_shape_of_the_file_is_checked(folder: DataFolder) -> None:
    """The pantry is ``None``, and no item is unknown."""
    cases = [
        (
            'pantry = ["盐", "sesame oil", 3, ""]\n',
            [(at_item(3), M_ITEM_NOT_A_TEXT), (at_item(4), M_ITEM_EMPTY)],
        ),
        (
            'items = ["盐"]\n',
            [(None, m_missing_key("pantry")), (None, m_unknown_pantry_key("items"))],
        ),
        ('pantry = "盐"\n', [(IN_PANTRY, m_not_a_list("pantry"))]),
    ]
    for text, problems_wanted in cases:
        write(folder.pantry, text)
        pantry, problems = read_pantry(folder, None)
        assert pantry is None
        check_problems(problems, PANTRY_FILE, problems_wanted)
