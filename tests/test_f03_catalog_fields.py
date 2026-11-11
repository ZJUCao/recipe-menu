"""Tests of F03 for the fields of catalog.toml items (F03-T58 to F03-T62)."""

from f03_support import (
    CATALOG_FILE,
    MEAT_ITEM,
    PRODUCE_ITEM,
    TOMATO_ITEM,
    at_category,
    at_ingredient,
    check_problems,
    en_names,
    ing,
    m_empty_text,
    m_missing_key,
    m_not_a_text,
    m_unknown_category,
    m_unknown_unit,
    produce,
    quick,
    write_catalog,
)
from recipe_menu.catalog import Catalog, Category, Ingredient, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.units import Unit


def test_f03_t58_the_required_texts_of_a_category(folder: DataFolder) -> None:
    """A category with a problem in its key or in both names is skipped, and otherwise kept."""
    write_catalog(
        folder,
        [
            '{ zh = "蔬菜水果", en = "Vegetables and fruit" }',
            '{ key = 3, zh = "肉类水产", en = "Meat and seafood" }',
            '{ key = "\u3000", zh = "蛋奶豆制品", en = "Eggs, dairy, and tofu" }',
            '{ key = "staples", en = "Rice, flour, and oil" }',
            '{ key = "seasonings", zh = "调味品", en = true }',
            '{ key = "other", zh = "", en = " " }',
        ],
        [TOMATO_ITEM, ing("大米", "Rice", "staples"), ing("盐", "Salt", "seasonings")],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    staples = Category("staples", BiText(en="Rice, flour, and oil"))
    spices = Category("seasonings", BiText(zh="调味品"))
    assert catalog.categories == (staples, spices)
    assert en_names(catalog.ingredients) == ["Rice", "Salt"]
    assert catalog.ingredients[0].category is catalog.categories[0]
    assert catalog.ingredients[1].category is catalog.categories[1]
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), m_missing_key("key")),
            (at_category(2), m_not_a_text("key")),
            (at_category(3), m_empty_text("key")),
            (at_category(4), m_missing_key("zh")),
            (at_category(5), m_not_a_text("en")),
            (at_category(6), m_empty_text("zh")),
            (at_category(6), m_empty_text("en")),
            (at_ingredient(1), m_unknown_category("produce", "staples", "seasonings")),
        ],
    )


def test_f03_t59_the_required_texts_of_an_ingredient(folder: DataFolder) -> None:
    """Each field has its own problem, and the ingredient is skipped."""
    write_catalog(
        folder,
        [PRODUCE_ITEM],
        [
            '{ en = "Tomato", category = "produce" }',
            '{ zh = "葱", en = 3, category = "produce" }',
            '{ zh = "姜", en = "", category = "produce" }',
            '{ zh = "\u3000", en = "Garlic", category = "produce" }',
            '{ zh = "菜心", en = "Choy sum" }',
            '{ zh = "西兰花", en = "Broccoli", category = ["produce"] }',
            '{ zh = "番茄", en = "Tomato", category = " " }',
            "{ zh = [], en = {}, category = 1 }",
            TOMATO_ITEM,
        ],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert catalog.ingredients == (Ingredient(BiText("Tomato", "番茄"), produce),)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(1), m_missing_key("zh")),
            (at_ingredient(2), m_not_a_text("en")),
            (at_ingredient(3), m_empty_text("en")),
            (at_ingredient(4), m_empty_text("zh")),
            (at_ingredient(5), m_missing_key("category")),
            (at_ingredient(6), m_not_a_text("category")),
            (at_ingredient(7), m_empty_text("category")),
            (at_ingredient(8), m_not_a_text("zh")),
            (at_ingredient(8), m_not_a_text("en")),
            (at_ingredient(8), m_not_a_text("category")),
        ],
    )


def test_f03_t60_a_unit_that_is_wrong_keeps_the_ingredient_with_no_unit(
    folder: DataFolder,
) -> None:
    """A missing or blank unit is no problem, and a known spelling works in any case."""
    rows = [
        ("葱", "Scallion", "3"),
        ("姜", "Ginger", '["片"]'),
        ("大蒜", "Garlic", '"cups"'),
        ("番茄", "Tomato", '" 适量 "'),
        ("菜心", "Choy sum", '""'),
        ("西兰花", "Broccoli", '"\u3000"'),
        ("土豆", "Potato", None),
        ("黄瓜", "Cucumber", '" Pieces "'),
        ("生菜", "Lettuce", '"把"'),
        ("芹菜", "Celery", '"STALKS"'),
    ]
    write_catalog(folder, [PRODUCE_ITEM], [ing(zh, en, unit=unit) for zh, en, unit in rows])
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert len(catalog.ingredients) == 10
    units = [ingredient.unit for ingredient in catalog.ingredients]
    assert units == [None] * 7 + [Unit.PIECE, Unit.BUNCH, Unit.STALK]
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(1), m_not_a_text("unit")),
            (at_ingredient(2), m_not_a_text("unit")),
            (at_ingredient(3), m_unknown_unit("cups")),
            (at_ingredient(4), m_unknown_unit("适量")),
        ],
    )


def test_f03_t61_unknown_category_lists_the_kept_keys_and_finds_by_key_only(
    folder: DataFolder,
) -> None:
    """The form depends on the number of kept categories, and the keys are as written."""
    coriander = ing("香菜", "Coriander", " meats ")
    write_catalog(folder, [PRODUCE_ITEM], [coriander])
    _, problems = read_catalog(folder)
    check_problems(
        problems, CATALOG_FILE, [(at_ingredient(1), m_unknown_category("meats", "produce"))]
    )
    by_name = ing("番茄", "Tomato", "Vegetables and fruit")
    write_catalog(folder, [PRODUCE_ITEM, MEAT_ITEM], [coriander, by_name])
    _, problems = read_catalog(folder)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(1), m_unknown_category("meats", "produce", "meat")),
            (at_ingredient(2), m_unknown_category("Vegetables and fruit", "produce", "meat")),
        ],
    )
    upper = '{ key = "Produce", zh = "蔬菜水果", en = "Vegetables and fruit" }'
    write_catalog(
        folder,
        [upper, MEAT_ITEM],
        [
            ing("番茄", "Tomato", "PRODUCE"),
            ing("猪肉末", "Minced pork", "Meat "),
            ing("香菜", "Coriander", "vegetables"),
        ],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert en_names(catalog.ingredients) == ["Tomato", "Minced pork"]
    assert catalog.ingredients[0].category is catalog.categories[0]
    assert catalog.categories[0].key == "Produce"
    assert catalog.ingredients[1].category is catalog.categories[1]
    check_problems(
        problems,
        CATALOG_FILE,
        [(at_ingredient(3), m_unknown_category("vegetables", "Produce", "meat"))],
    )


def test_f03_t62_names_and_keys_are_stored_without_whitespace_at_both_ends(
    folder: DataFolder,
) -> None:
    """Whitespace inside a name stays."""
    write_catalog(
        folder,
        ['{ key = " produce\t", zh = "\u3000蔬菜水果", en = "Vegetables and fruit\u00a0" }'],
        [
            '{ zh = " 葱 ", en = "\tScallion", category = " produce", unit = " 根 " }',
            '{ zh = "菜心", en = "Choy  sum", category = "produce" }',
        ],
        ['{ zh = "快手\u3000", en = " quick" }'],
    )
    catalog, problems = read_catalog(folder)
    assert problems == ()
    expected = Catalog(
        (produce,),
        (
            Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK),
            Ingredient(BiText("Choy  sum", "菜心"), produce),
        ),
        (quick,),
    )
    assert catalog == expected
