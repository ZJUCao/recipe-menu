"""Tests of F04 for read_recipes (T44 to T47)."""

from dataclasses import replace

from f03_support import M_FILE_IS_FOLDER, m_missing_key
from f04_support import (
    EXAMPLE_IDS,
    M_FOLDER_IS_FILE,
    M_FOLDER_MISSING,
    M_NO_EN_NAME,
    M_NO_EN_STEPS,
    M_NOT_A_RECIPE_ID,
    M_TOML_ENDING,
    SERVINGS,
    STEPS,
    check_problems,
    dish,
    dish_catalog,
    dish_text,
    err,
    example_catalog,
    m_too_few,
    put_bytes,
    touch,
    warn,
    write,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.recipes import read_recipe, read_recipes

PORK = "recipes/red-braised-pork.toml"
RICE = "recipes/rice.toml"
PORK_WARNING = warn(STEPS, M_NO_EN_STEPS, PORK)


def test_f04_t44_the_design_example_of_read_recipes(example_folder: DataFolder) -> None:
    """Seven recipes and one warning. Bad names and files add their problems, in order."""
    catalog = example_catalog(example_folder)
    recipes, problems = read_recipes(example_folder, catalog)
    assert tuple(recipe.id for recipe in recipes) == EXAMPLE_IDS
    for recipe in recipes:
        assert read_recipe(example_folder, catalog, recipe.id)[0] == recipe
    check_problems(problems, [PORK_WARNING])
    touch(example_folder.recipes, "Rice Bowl.toml")
    write(example_folder.recipe_file("rice"), "servings = 0\n")
    recipes, problems = read_recipes(example_folder, catalog)
    assert tuple(recipe.id for recipe in recipes) == tuple(i for i in EXAMPLE_IDS if i != "rice")
    expected = [
        err(None, M_NOT_A_RECIPE_ID, "recipes/Rice Bowl.toml"),
        PORK_WARNING,
        err(None, m_missing_key("name"), RICE),
        err(SERVINGS, m_too_few(0), RICE),
        err(None, m_missing_key("tags"), RICE),
        err(None, m_missing_key("ingredients"), RICE),
        err(None, m_missing_key("steps"), RICE),
    ]
    check_problems(problems, expected)
    recipes, problems = read_recipes(example_folder, None)
    assert recipes == ()
    check_problems(problems, expected, "no catalog")


def test_f04_t45_the_problems_come_in_the_order_of_the_ids(folder: DataFolder) -> None:
    """The listing problems first. A file with an error gives no recipe, and a warning keeps it."""
    write(folder.recipes / "c.toml", dish_text())
    write(folder.recipes / "a.toml", dish_text(servings="0"))
    write(folder.recipes / "b.toml", dish_text(name='{ zh = "番茄炒蛋" }'))
    (folder.recipes / "x.toml").mkdir()
    write(folder.recipes / "d.TOML", dish_text())
    write(folder.recipes / "Rice Bowl.toml", dish_text())
    expected = [
        err(None, M_TOML_ENDING, "recipes/d.TOML"),
        err(None, M_NOT_A_RECIPE_ID, "recipes/Rice Bowl.toml"),
        err(SERVINGS, m_too_few(0), "recipes/a.toml"),
        warn(BiText("name", "名称"), M_NO_EN_NAME, "recipes/b.toml"),
        err(None, M_FILE_IS_FOLDER, "recipes/x.toml"),
    ]
    recipes, problems = read_recipes(folder, dish_catalog)
    assert recipes == (
        replace(dish, id="b", name=BiText(zh="番茄炒蛋")),
        replace(dish, id="c"),
    )
    check_problems(problems, expected, "dish_catalog")
    recipes, problems = read_recipes(folder, None)
    assert recipes == ()
    check_problems(problems, expected, "no catalog")


def test_f04_t46_a_folder_that_cannot_be_listed_gives_only_its_problem(
    folder: DataFolder,
) -> None:
    """A missing folder and a file give their problems. An empty folder gives nothing."""
    for catalog in (dish_catalog, None):
        assert folder.recipes.exists() is False
        recipes, problems = read_recipes(folder, catalog)
        assert recipes == ()
        check_problems(problems, [err(None, M_FOLDER_MISSING, "recipes")], 1)
        write(folder.recipes, "x\n")
        recipes, problems = read_recipes(folder, catalog)
        assert recipes == ()
        check_problems(problems, [err(None, M_FOLDER_IS_FILE, "recipes")], 2)
        folder.recipes.unlink()
        folder.recipes.mkdir()
        assert read_recipes(folder, catalog) == ((), ())
        folder.recipes.rmdir()


def test_f04_t47_a_byte_order_mark_and_crlf_read_the_same(example_folder: DataFolder) -> None:
    """Scenario v0.1-S08 at the reader: files saved by Notepad read like the example."""
    catalog = example_catalog(example_folder)
    first = read_recipes(example_folder, catalog)
    assert len(first[0]) == 7
    for path in sorted(example_folder.recipes.glob("*.toml")):
        data = path.read_bytes()
        put_bytes(path, b"\xef\xbb\xbf" + data.replace(b"\n", b"\r\n"))
    assert read_recipes(example_folder, catalog) == first
