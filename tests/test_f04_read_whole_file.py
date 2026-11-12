"""Tests of F04 for read_recipe on a whole file: order, no catalog, and read errors (T32 to T36)."""

import shutil

import pytest

from f03_support import (
    M_BAD_KEY,
    M_DEFINED_TWICE,
    M_FILE_IS_FOLDER,
    M_FILE_MISSING,
    M_ITEM_NOT_A_TEXT,
    M_MISSING_BRACKET,
    M_NOT_UTF8,
    M_NUMBER_TOO_LONG,
    at_line,
    m_missing_key,
    m_unknown_key,
)
from f04_support import (
    M_FOLDER_DENIED,
    M_NO_EN_NAME,
    M_NO_EN_STEPS,
    M_NO_ZH_NOTE,
    NAME,
    RECIPE_KEYS,
    SERVINGS,
    STEPS,
    TAGS,
    check_problems,
    dish,
    dish_catalog,
    dish_text,
    err,
    ingredient_n,
    listing_denied,
    m_amount_unit,
    m_no_unit,
    m_too_few,
    m_unknown_ing,
    m_unknown_tag,
    m_zero,
    put_bytes,
    read_dish,
    tag_n,
    tomato,
    warn,
    write,
    write_dish,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.recipes import list_recipe_ids, read_recipe, read_recipes


def put_lines(folder: DataFolder, *lines: str) -> None:
    """Writes ``recipes/dish.toml`` from its lines."""
    write(folder.recipe_file("dish"), "".join(f"{line}\n" for line in lines))


def test_f04_t32_the_parts_give_their_problems_in_one_order(folder: DataFolder) -> None:
    """The order of the parts, whatever the order of the file. An empty file misses five keys."""
    put_lines(
        folder,
        "version = 1",
        "ingredients = [",
        '  { item = "番茄", amount = "0 g" },',
        "]",
        'tags = ["breakfast"]',
        "servings = 0",
        'colour = "red"',
        'name = { zh = "番茄炒蛋" }',
        "[steps]",
        'zh = ["番茄切块。"]',
    )
    recipe, problems = read_recipe(folder, dish_catalog, "dish")
    assert recipe is None
    check_problems(
        problems,
        [
            warn(NAME, M_NO_EN_NAME),
            err(SERVINGS, m_too_few(0)),
            err(TAGS, m_unknown_tag("breakfast")),
            err(ingredient_n(1), m_zero("0 g")),
            warn(STEPS, M_NO_EN_STEPS),
            err(None, m_unknown_key("version", RECIPE_KEYS)),
            err(None, m_unknown_key("colour", RECIPE_KEYS)),
        ],
    )
    write(folder.recipe_file("dish"), "version = 1\n" + dish_text())
    recipe, problems = read_recipe(folder, dish_catalog, "dish")
    assert recipe is None
    check_problems(problems, [err(None, m_unknown_key("version", RECIPE_KEYS))])
    write(folder.recipe_file("dish"), "")
    recipe, problems = read_recipe(folder, dish_catalog, "dish")
    assert recipe is None
    keys = ("name", "servings", "tags", "ingredients", "steps")
    check_problems(problems, [err(None, m_missing_key(key)) for key in keys])


def test_f04_t33_with_no_catalog_there_is_no_recipe_but_the_other_checks_run(
    folder: DataFolder,
) -> None:
    """Every check except UNKNOWN_TAG, UNKNOWN_INGREDIENT, and AMOUNT_NO_UNIT, and the warnings."""
    write_dish(folder)
    assert read_recipe(folder, None, "dish") == (None, ())
    items = (
        '{ item = "豆瓣酱", amount = "3" }',
        '{ item = "番茄", amount = "3" }',
        '{ item = "番茄", amount = "1 cups" }',
        '{ item = "番茄", amount = "0 g", note = { en = "cut" } }',
    )
    parts = {"name": '{ zh = "番茄炒蛋" }', "tags": '["breakfast", 3]', "ingredients": items}
    recipe, problems = read_dish(folder, None, **parts)
    assert recipe is None
    check_problems(
        problems,
        [
            warn(NAME, M_NO_EN_NAME),
            err(tag_n(2), M_ITEM_NOT_A_TEXT),
            err(ingredient_n(3), m_amount_unit("cups", "1 cups")),
            err(ingredient_n(4), m_zero("0 g")),
            warn(ingredient_n(4), M_NO_ZH_NOTE),
        ],
        "no catalog",
    )
    recipe, problems = read_recipe(folder, dish_catalog, "dish")
    assert recipe is None
    check_problems(
        problems,
        [
            warn(NAME, M_NO_EN_NAME),
            err(TAGS, m_unknown_tag("breakfast")),
            err(tag_n(2), M_ITEM_NOT_A_TEXT),
            err(ingredient_n(1), m_unknown_ing("豆瓣酱")),
            err(ingredient_n(2), m_no_unit("3", tomato)),
            err(ingredient_n(3), m_amount_unit("cups", "1 cups")),
            err(ingredient_n(4), m_zero("0 g")),
            warn(ingredient_n(4), M_NO_ZH_NOTE),
        ],
        "dish_catalog",
    )


@pytest.mark.usefixtures("default_int_limit")
def test_f04_t34_a_problem_of_read_toml_is_the_only_one(folder: DataFolder) -> None:
    """The file cannot be read, so there is one problem and no recipe, with a catalog or not."""
    path = folder.recipe_file("dish")
    base = dish_text()
    folder.recipes.mkdir()
    cases = [
        (None, err(None, M_FILE_MISSING)),
        ("folder", err(None, M_FILE_IS_FOLDER)),
        (base.encode("gbk"), err(at_line(1), M_NOT_UTF8)),
        (
            base.replace('"番茄炒蛋", en', '"番茄炒蛋",\n  en').encode(),
            err(at_line(1), M_BAD_KEY),
        ),
        (dish_text(tags='["快手" "家常"]').encode(), err(at_line(3), M_MISSING_BRACKET)),
        ((base + '[steps]\nen = ["Fry."]\n').encode(), err(at_line(11), M_DEFINED_TWICE)),
        (dish_text(servings="1" * 4301).encode(), err(at_line(2), M_NUMBER_TOO_LONG)),
    ]
    for number, (content, expected) in enumerate(cases, 1):
        shutil.rmtree(path, ignore_errors=True)
        path.unlink(missing_ok=True)
        if isinstance(content, str):
            path.mkdir()
        elif content is not None:
            put_bytes(path, content)
        for catalog in (dish_catalog, None):
            recipe, problems = read_recipe(folder, catalog, "dish")
            assert recipe is None, number
            check_problems(problems, [expected], number)


def test_f04_t35_an_id_that_breaks_the_rule_raises_before_any_read(folder: DataFolder) -> None:
    """The file ``Tomato-Egg.toml`` exists, so the check comes before the read."""
    write(folder.recipes / "Tomato-Egg.toml", dish_text())
    for recipe_id in (
        "Tomato-Egg",
        "",
        "../catalog",
        "a/b",
        "a:b",
        "tomato egg",
        "con",
        "番茄炒蛋",
    ):
        for catalog in (dish_catalog, None):
            with pytest.raises(ValueError):
                read_recipe(folder, catalog, recipe_id)


def test_f04_t36_read_recipe_lists_no_folder(folder: DataFolder) -> None:
    """With the listing of ``recipes/`` denied, only the two listing readers give a problem."""
    write_dish(folder)
    with listing_denied(folder.recipes):
        assert read_recipe(folder, dish_catalog, "dish") == (dish, ())
        ids, id_problems = list_recipe_ids(folder)
        recipes, problems = read_recipes(folder, dish_catalog)
    assert ids == ()
    assert recipes == ()
    check_problems(id_problems, [err(None, M_FOLDER_DENIED, "recipes")])
    check_problems(problems, [err(None, M_FOLDER_DENIED, "recipes")])
