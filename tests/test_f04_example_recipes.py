"""Tests of F04 for read_recipe on the example data and the scenarios (T37 to T43)."""

import tomllib

import pytest

from f03_support import M_FILE_MISSING, edit_ingredients, ing, m_not_a_list
from f04_support import (
    EN,
    EXAMPLE_IDS,
    M_NO_EN_NAME,
    M_NO_EN_STEPS,
    M_NO_ZH_NOTE,
    M_NO_ZH_STEPS,
    M_SERVINGS_NOT_A_NUMBER,
    NAME,
    SERVINGS,
    STEPS,
    TAGS,
    ZH,
    check_lines,
    check_problems,
    dish_text,
    err,
    example_catalog,
    ingredient_n,
    m_amount_unit,
    m_no_unit,
    m_not_a_number,
    m_too_few,
    m_unknown_ing,
    m_unknown_tag,
    qty,
    warn,
    write,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.recipes import Steps, list_recipe_ids, read_recipe
from recipe_menu.units import TO_TASTE, Unit

RICE = "recipes/rice.toml"
PORK = "recipes/red-braised-pork.toml"
MAPO = "recipes/mapo-tofu.toml"

# The tags (Chinese names) and the ingredient lines of six example recipes, in the file's order.
EXPECTED = {
    "choy-sum": (
        ["快手", "素"],
        [
            ("菜心", qty(1, Unit.JIN), None),
            ("大蒜", qty(3, Unit.CLOVE), BiText("crushed", "拍碎")),
            ("盐", TO_TASTE, None),
            ("食用油", qty(1, Unit.TBSP), None),
        ],
    ),
    "cola-wings": (
        ["家常"],
        [
            ("鸡翅中", qty(500, Unit.G), None),
            ("可乐", qty(1, Unit.CAN), None),
            ("姜", qty(3, Unit.SLICE), None),
            ("葱", qty(1, Unit.STALK), None),
            ("生抽", qty(2, Unit.TBSP), None),
        ],
    ),
    "mapo-tofu": (
        ["辣", "家常"],
        [
            ("豆腐", qty(1, Unit.BLOCK), BiText("diced", "切丁")),
            ("猪肉末", qty(100, Unit.G), None),
            ("郫县豆瓣酱", qty(1, Unit.TBSP), None),
            ("花椒", qty(1, Unit.TSP), None),
            ("大蒜", qty(2, Unit.CLOVE), None),
            ("葱", qty(1, Unit.STALK), None),
            ("生抽", qty(1, Unit.TBSP), None),
            ("食用油", qty(2, Unit.TBSP), None),
        ],
    ),
    "rice": (["主食"], [("大米", qty(160, Unit.G), None)]),
    "tomato-egg-noodles": (
        ["快手", "主食"],
        [
            ("面条", qty(200, Unit.G), None),
            ("番茄", qty(300, Unit.G), None),
            ("鸡蛋", qty(2, Unit.PIECE), None),
            ("葱", qty(1, Unit.STALK), None),
            ("盐", TO_TASTE, None),
            ("白胡椒粉", TO_TASTE, None),
        ],
    ),
    "red-braised-pork": (
        ["家常"],
        [
            ("五花肉", qty(1, Unit.JIN), BiText("cut into 3 cm cubes", "切成 3 厘米见方的块")),
            ("冰糖", qty(30, Unit.G), None),
            ("生抽", qty(2, Unit.TBSP), None),
            ("姜", qty(3, Unit.SLICE), None),
            ("葱", qty(2, Unit.STALK), None),
        ],
    ),
}

TOMATO_EGG_ZH = (
    "番茄切块。鸡蛋加少许盐打散。",
    "热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。",
    "下剩下的油，炒番茄至软，加糖。",
    "倒回鸡蛋，加盐调味，撒上葱花。",
)
TOMATO_EGG_EN = (
    "Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.",
    "Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.",
    "Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.",
    "Return the eggs, season with salt, and scatter the scallion on top.",
)


def test_f04_t37_the_tomato_egg_file_gives_every_field(example_folder: DataFolder) -> None:
    """The design's first example, with the catalog's own objects. With no catalog, nothing."""
    catalog = example_catalog(example_folder)
    recipe, problems = read_recipe(example_folder, catalog, "tomato-egg")
    assert problems == ()
    assert recipe is not None
    assert recipe.id == "tomato-egg"
    assert recipe.name == BiText("Tomato and egg stir-fry", "番茄炒蛋")
    assert recipe.servings == 2
    check_lines(
        recipe,
        catalog,
        ["快手", "家常"],
        [
            ("番茄", qty(300, Unit.G), BiText("cut into wedges", "切块")),
            ("鸡蛋", qty(3, Unit.PIECE), None),
            ("葱", qty(1, Unit.STALK), BiText("chopped", "切葱花")),
            ("盐", TO_TASTE, None),
            ("糖", qty(1, Unit.TSP), None),
            ("食用油", qty(2, Unit.TBSP), None),
        ],
    )
    assert recipe.steps == Steps(TOMATO_EGG_EN, TOMATO_EGG_ZH)
    assert read_recipe(example_folder, None, "tomato-egg") == (None, ())


def test_f04_t38_the_other_six_example_recipes(example_folder: DataFolder) -> None:
    """Only red-braised-pork gives a warning: the one of the F07 prototype."""
    catalog = example_catalog(example_folder)
    for recipe_id, (tags, lines) in EXPECTED.items():
        recipe, problems = read_recipe(example_folder, catalog, recipe_id)
        assert recipe is not None, recipe_id
        data = tomllib.loads(example_folder.recipe_file(recipe_id).read_text(encoding="utf-8"))
        assert recipe.id == recipe_id
        assert recipe.name == BiText(data["name"]["en"], data["name"]["zh"])
        assert recipe.servings == 2
        check_lines(recipe, catalog, tags, lines)
        zh_steps = tuple(data["steps"]["zh"])
        if recipe_id == "red-braised-pork":
            assert len(zh_steps) == 4
            assert recipe.steps == Steps(zh=zh_steps)
            assert recipe.steps.exact(EN) is None
            assert recipe.steps.get(EN) == recipe.steps.exact(ZH) == zh_steps
            check_problems(problems, [warn(STEPS, M_NO_EN_STEPS, PORK)])
        else:
            assert recipe.steps == Steps(tuple(data["steps"]["en"]), zh_steps)
            assert problems == (), recipe_id


def test_f04_t39_an_ingredient_that_is_not_in_the_catalog_gives_the_f07_error(
    example_folder: DataFolder,
) -> None:
    """Doubanjiang without its prefix is no catalog name, so ingredient 3 is unknown."""
    catalog = example_catalog(example_folder)
    path = example_folder.recipe_file("mapo-tofu")
    text = path.read_text(encoding="utf-8")
    assert "郫县" in text
    write(path, text.replace("郫县", ""))
    recipe, problems = read_recipe(example_folder, catalog, "mapo-tofu")
    assert recipe is None
    check_problems(problems, [err(ingredient_n(3), m_unknown_ing("豆瓣酱"), MAPO)])


def test_f04_t40_the_three_mistakes_of_scenario_v0_1_s07(example_folder: DataFolder) -> None:
    """The servings, the tag, and the unit of ``rice.toml`` give the three lines of F07."""
    catalog = example_catalog(example_folder)
    path = example_folder.recipe_file("rice")
    text = path.read_text(encoding="utf-8")
    for old in ("servings = 2", '["主食"]', '"160 g"'):
        assert old in text
    changed = text.replace("servings = 2", "servings = 0")
    changed = changed.replace('["主食"]', '["breakfast"]').replace('"160 g"', '"1 cups"')
    expected = [
        err(SERVINGS, m_too_few(0), RICE),
        err(TAGS, m_unknown_tag("breakfast"), RICE),
        err(ingredient_n(1), m_amount_unit("cups", "1 cups"), RICE),
    ]
    seven_lines = dish_text(
        name='{ zh = "米饭", en = "Steamed rice" }',
        servings="0",
        tags='["breakfast"]',
        ingredients='[{ item = "大米", amount = "1 cups" }]',
        steps=('zh = ["煮饭。"]', 'en = ["Cook the rice."]'),
    ).replace("\n\n", "\n")
    for content in (changed, seven_lines):
        write(path, content)
        recipe, problems = read_recipe(example_folder, catalog, "rice")
        assert recipe is None
        check_problems(problems, expected)
    write(path, changed)
    recipe, problems = read_recipe(example_folder, None, "rice")
    assert recipe is None
    check_problems(problems, [expected[0], expected[2]], "no catalog")


@pytest.mark.usefixtures("default_int_limit")
def test_f04_t41_the_third_file_of_the_design_example(example_folder: DataFolder) -> None:
    """Errors and warnings keep the order of the parts, and no number of 5,000 digits raises."""
    catalog = example_catalog(example_folder)
    lines = [
        'name = { zh = "番茄", en = " " }',
        "servings = 0x" + "f" * 5000,
        "tags = []",
        "ingredients = [",
        '  { item = "番茄", amount = "3" },',
        '  { item = "葱", amount = "1234567890123456 根", note = { en = "chopped" } },',
        "]",
        "[steps]",
        'en = ["Cook."]',
    ]
    write(example_folder.recipe_file("rice"), "\n".join(lines) + "\n")
    recipe, problems = read_recipe(example_folder, catalog, "rice")
    assert recipe is None
    tomato = catalog.find_ingredient("番茄")
    assert tomato is not None
    check_problems(
        problems,
        [
            warn(NAME, M_NO_EN_NAME, RICE),
            err(SERVINGS, M_SERVINGS_NOT_A_NUMBER, RICE),
            err(ingredient_n(1), m_no_unit("3", tomato), RICE),
            err(ingredient_n(2), m_not_a_number("1234567890123456 根"), RICE),
            warn(ingredient_n(2), M_NO_ZH_NOTE, RICE),
            warn(STEPS, M_NO_ZH_STEPS, RICE),
        ],
    )


def test_f04_t42_an_empty_text_in_the_steps_is_an_error_and_a_missing_file_a_problem(
    example_folder: DataFolder,
) -> None:
    """``en = ""`` is no list. An ID with no file gives FILE_MISSING. A wrong ID raises."""
    catalog = example_catalog(example_folder)
    path = example_folder.recipe_file("red-braised-pork")
    write(path, path.read_text(encoding="utf-8") + 'en = ""\n')
    recipe, problems = read_recipe(example_folder, catalog, "red-braised-pork")
    assert recipe is None
    check_problems(problems, [err(STEPS, m_not_a_list("en"), PORK)])
    recipe, problems = read_recipe(example_folder, catalog, "mapo")
    assert recipe is None
    check_problems(problems, [err(None, M_FILE_MISSING, "recipes/mapo.toml")])
    with pytest.raises(ValueError):
        read_recipe(example_folder, catalog, "Tomato-Egg")


def test_f04_t43_scenario_v0_1_s04_at_the_readers(example_folder: DataFolder) -> None:
    """A recipe with an ingredient that the catalog lacks reads once the catalog has it."""
    for recipe_id in EXAMPLE_IDS:
        if recipe_id != "tomato-egg":
            example_folder.recipe_file(recipe_id).unlink()
    cucumber = dish_text(
        name='{ zh = "拍黄瓜", en = "Smashed cucumber" }',
        servings="2",
        tags='["快手", "素"]',
        ingredients=('{ item = "黄瓜", amount = "2 个" }', '{ item = "大蒜", amount = "2 瓣" }'),
        steps=(
            'zh = ["黄瓜拍碎，加蒜末和盐拌匀。"]',
            'en = ["Smash the cucumber, and toss it with the garlic and salt."]',
        ),
    )
    write(example_folder.recipe_file("cucumber-salad"), cucumber)
    catalog = example_catalog(example_folder)
    assert list_recipe_ids(example_folder) == (("cucumber-salad", "tomato-egg"), ())
    recipe, problems = read_recipe(example_folder, catalog, "cucumber-salad")
    assert recipe is None
    file = "recipes/cucumber-salad.toml"
    check_problems(problems, [err(ingredient_n(1), m_unknown_ing("黄瓜"), file)])
    edit_ingredients(example_folder, added=[ing("黄瓜", "Cucumber")])
    catalog = example_catalog(example_folder)
    assert len(catalog.ingredients) == 23
    recipe, problems = read_recipe(example_folder, catalog, "cucumber-salad")
    assert problems == ()
    assert recipe is not None
    assert recipe.ingredients[0].ingredient is catalog.ingredients[22]
    check_lines(
        recipe,
        catalog,
        ["快手", "素"],
        [("黄瓜", qty(2, Unit.PIECE), None), ("大蒜", qty(2, Unit.CLOVE), None)],
    )
