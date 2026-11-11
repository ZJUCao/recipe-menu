"""Tests of F03 for the lists and the shape of catalog.toml (F03-T48 to F03-T57)."""

from pathlib import Path

from f03_support import (
    CATALOG_FILE,
    CATEGORY_KEYS,
    IN_CATEGORIES,
    IN_INGREDIENTS,
    IN_TAGS,
    INGREDIENT_KEYS,
    M_BAD_KEY,
    M_FILE_IS_FOLDER,
    M_FILE_MISSING,
    M_ITEM_NOT_A_TABLE,
    M_NOT_UTF8,
    PRODUCE_ITEM,
    QUICK_ITEM,
    TAG_KEYS,
    TOMATO_ITEM,
    TOP_KEYS,
    at_category,
    at_ingredient,
    at_line,
    at_tag,
    check_problems,
    edit_ingredients,
    en_names,
    ing,
    m_dup_en,
    m_dup_zh,
    m_missing_key,
    m_no_categories,
    m_not_a_list,
    m_unknown_category,
    m_unknown_key,
    m_unknown_unit,
    produce,
    put_bytes,
    quick,
    write,
    write_catalog,
)
from recipe_menu.catalog import Catalog, Category, Ingredient, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.units import Unit

INGREDIENTS = [
    ("Tomato", "番茄"),
    ("Choy sum", "菜心"),
    ("Broccoli", "西兰花"),
    ("Scallion", "葱"),
    ("Ginger", "姜"),
    ("Garlic", "大蒜"),
    ("Pork belly", "五花肉"),
    ("Minced pork", "猪肉末"),
    ("Chicken wings", "鸡翅中"),
    ("Egg", "鸡蛋"),
    ("Tofu", "豆腐"),
    ("Rice", "大米"),
    ("Noodles", "面条"),
    ("Cooking oil", "食用油"),
    ("Salt", "盐"),
    ("Sugar", "糖"),
    ("Soy sauce", "生抽"),
    ("Rock sugar", "冰糖"),
    ("Doubanjiang", "郫县豆瓣酱"),
    ("Sichuan pepper", "花椒"),
    ("White pepper", "白胡椒粉"),
    ("Cola", "可乐"),
]
UNITS = {3: Unit.STALK, 4: Unit.SLICE, 5: Unit.CLOVE, 9: Unit.PIECE, 10: Unit.BLOCK, 21: Unit.CAN}
CATEGORY_OF = [0] * 6 + [1] * 3 + [2] * 2 + [3] * 3 + [4] * 7 + [5]
TAGS = [
    ("quick", "快手"),
    ("home-style", "家常"),
    ("vegetarian", "素"),
    ("spicy", "辣"),
    ("staple", "主食"),
]


def test_f03_t48_the_example_catalog_gives_every_item_in_the_files_order(
    example_folder: DataFolder,
) -> None:
    """The categories, the ingredients, and the tags are as the prototype shows them."""
    catalog, problems = read_catalog(example_folder)
    assert problems == ()
    assert isinstance(catalog, Catalog)
    assert isinstance(catalog.categories, tuple)
    assert isinstance(catalog.ingredients, tuple)
    assert isinstance(catalog.tags, tuple)
    assert [len(catalog.categories), len(catalog.ingredients), len(catalog.tags)] == [6, 22, 5]
    keys = ["produce", "meat", "eggs", "staples", "seasonings", "other"]
    assert [category.key for category in catalog.categories] == keys
    eggs = Category("eggs", BiText("Eggs, dairy, and tofu", "蛋奶豆制品"))
    assert catalog.categories[2] == eggs
    assert [(i.name.en, i.name.zh) for i in catalog.ingredients] == INGREDIENTS
    for number, ingredient in enumerate(catalog.ingredients):
        assert ingredient.category is catalog.categories[CATEGORY_OF[number]]
        assert ingredient.unit is UNITS.get(number)
    assert [(t.name.en, t.name.zh) for t in catalog.tags] == TAGS


def test_f03_t49_the_design_example_with_duplicates_unknown_units_and_a_missing_file(
    folder: DataFolder,
) -> None:
    """A duplicate name, an unknown category, two unknown units, and a missing file."""
    write_catalog(
        folder,
        [PRODUCE_ITEM],
        [
            ing("西兰花", "Broccoli"),
            ing("芥兰", "broccoli"),
            ing("香菜", "Coriander", "meats"),
            ing("葱", "Scallion", unit='"cups"'),
            ing("葱", "Green onion", unit='"cups"'),
        ],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert en_names(catalog.ingredients) == ["Broccoli", "Scallion"]
    assert catalog.ingredients[1].unit is None
    ingredient_1, ingredient_4 = at_ingredient(1), at_ingredient(4)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(2), m_dup_en("broccoli", ingredient_1)),
            (at_ingredient(3), m_unknown_category("meats", "produce")),
            (ingredient_4, m_unknown_unit("cups")),
            (at_ingredient(5), m_unknown_unit("cups")),
            (at_ingredient(5), m_dup_zh("葱", ingredient_4)),
        ],
    )
    folder.catalog.unlink()
    catalog, problems = read_catalog(folder)
    assert catalog is None
    check_problems(problems, CATALOG_FILE, [(None, M_FILE_MISSING)])


def test_f03_t50_the_two_catalog_lines_of_the_f07_prototype(example_folder: DataFolder) -> None:
    """An unknown category at ingredient 7, and a duplicate English name at ingredient 12."""
    edit_ingredients(
        example_folder,
        {
            4: '{ zh = "米", en = "Rice", category = "staples" }',
            7: '{ zh = "五花肉", en = "Pork belly", category = "meats" }',
        },
    )
    catalog, problems = read_catalog(example_folder)
    assert catalog is not None
    assert len(catalog.ingredients) == 20
    six = ("produce", "meat", "eggs", "staples", "seasonings", "other")
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(7), m_unknown_category("meats", *six)),
            (at_ingredient(12), m_dup_en("Rice", at_ingredient(4))),
        ],
    )


def test_f03_t51_a_problem_of_read_toml_gives_no_catalog_and_only_that_problem(
    tmp_path: Path,
) -> None:
    """A missing file, a folder, bytes that are not UTF-8, and a table that spans two lines."""
    missing = DataFolder(tmp_path / "missing")
    isfolder = DataFolder(tmp_path / "isfolder")
    isfolder.catalog.mkdir(parents=True)
    bad_bytes = DataFolder(tmp_path / "bad_bytes")
    put_bytes(bad_bytes.catalog, b"categories = []\n# caf\xe9\n")
    spans = DataFolder(tmp_path / "spans")
    spans_text = (
        'categories = [\n  { key = "produce", zh = "蔬菜水果",\n'
        '    en = "Vegetables and fruit" },\n]\n'
    )
    write(spans.catalog, spans_text)
    cases = [
        (missing, None, M_FILE_MISSING),
        (isfolder, None, M_FILE_IS_FOLDER),
        (bad_bytes, at_line(2), M_NOT_UTF8),
        (spans, at_line(2), M_BAD_KEY),
    ]
    for folder, place, msg in cases:
        catalog, problems = read_catalog(folder)
        assert catalog is None
        check_problems(problems, CATALOG_FILE, [(place, msg)])


def test_f03_t52_a_missing_list_or_a_value_that_is_not_a_list_reads_as_empty(
    folder: DataFolder,
) -> None:
    """``MISSING_KEY`` has no place, and ``NOT_A_LIST`` is at the list."""
    write(folder.catalog, "")
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    check_problems(
        problems,
        CATALOG_FILE,
        [(None, m_missing_key(key)) for key in ("categories", "ingredients", "tags")],
    )
    text = 'categories = "produce"\ningredients = 3\n[tags]\nzh = "快手"\nen = "quick"\n'
    write(folder.catalog, text)
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (IN_CATEGORIES, m_not_a_list("categories")),
            (IN_INGREDIENTS, m_not_a_list("ingredients")),
            (IN_TAGS, m_not_a_list("tags")),
        ],
    )


def test_f03_t53_an_ingredient_gets_no_categories_when_no_category_was_kept(
    folder: DataFolder,
) -> None:
    """The list is missing or empty, or each category is skipped."""
    first = (
        'ingredients = [\n  { zh = "番茄", en = "Tomato", category = "produce" },\n]\ntags = []\n'
    )
    write(folder.catalog, first)
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    no_category = (at_ingredient(1), m_no_categories("produce"))
    check_problems(problems, CATALOG_FILE, [(None, m_missing_key("categories")), no_category])
    write_catalog(folder, ingredients=[TOMATO_ITEM])
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    check_problems(problems, CATALOG_FILE, [no_category])
    write_catalog(folder, ['{ key = "produce" }'], [TOMATO_ITEM])
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), m_missing_key("zh")),
            (at_category(1), m_missing_key("en")),
            no_category,
        ],
    )


def test_f03_t54_each_table_of_the_double_bracket_form_is_an_item(folder: DataFolder) -> None:
    """The tables are numbered like the items of a list."""
    text = (
        "tags = []\n\n"
        '[[categories]]\nkey = "produce"\nzh = "蔬菜水果"\nen = "Vegetables and fruit"\n\n'
        '[[ingredients]]\nzh = "番茄"\nen = "Tomato"\ncategory = "produce"\n\n'
        '[[ingredients]]\nzh = "葱"\nen = "Scallion"\ncategory = "produce"\n'
        'unit = "根"\nunits = "根"\n'
    )
    write(folder.catalog, text)
    catalog, problems = read_catalog(folder)
    expected = Catalog(
        (produce,),
        (
            Ingredient(BiText("Tomato", "番茄"), produce),
            Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK),
        ),
        (),
    )
    assert catalog == expected
    check_problems(
        problems, CATALOG_FILE, [(at_ingredient(2), m_unknown_key("units", INGREDIENT_KEYS))]
    )


def test_f03_t55_an_item_that_is_not_a_table_is_skipped_and_counted(folder: DataFolder) -> None:
    """An empty table is a table with missing keys."""
    write_catalog(
        folder,
        ['"produce"', PRODUCE_ITEM],
        ["3", '["番茄"]', "{}", TOMATO_ITEM],
        ['"quick"', QUICK_ITEM],
    )
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog(
        (produce,), (Ingredient(BiText("Tomato", "番茄"), produce),), (quick,)
    )
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), M_ITEM_NOT_A_TABLE),
            (at_ingredient(1), M_ITEM_NOT_A_TABLE),
            (at_ingredient(2), M_ITEM_NOT_A_TABLE),
            (at_ingredient(3), m_missing_key("zh")),
            (at_ingredient(3), m_missing_key("en")),
            (at_ingredient(3), m_missing_key("category")),
            (at_tag(1), M_ITEM_NOT_A_TABLE),
        ],
    )


def test_f03_t56_a_key_that_its_kind_does_not_have_is_reported_and_ignored(
    folder: DataFolder,
) -> None:
    """The item is kept, and an unknown key sets no unit."""
    write_catalog(
        folder,
        ['{ key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit", order = 1 }'],
        [
            '{ zh = "番茄", en = "Tomato", category = "produce", units = "个" }',
            '{ zh = "葱", en = "Scallion", category = "produce", "单位" = "根", note = "x" }',
        ],
        ['{ zh = "快手", en = "quick", colour = "red" }'],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert catalog.categories == (produce,)
    assert en_names(catalog.ingredients) == ["Tomato", "Scallion"]
    assert [ingredient.unit for ingredient in catalog.ingredients] == [None, None]
    assert catalog.tags == (quick,)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), m_unknown_key("order", CATEGORY_KEYS)),
            (at_ingredient(1), m_unknown_key("units", INGREDIENT_KEYS)),
            (at_ingredient(2), m_unknown_key("单位", INGREDIENT_KEYS)),
            (at_ingredient(2), m_unknown_key("note", INGREDIENT_KEYS)),
            (at_tag(1), m_unknown_key("colour", TAG_KEYS)),
        ],
    )


def test_f03_t57_a_key_at_the_top_other_than_the_three_lists_is_reported(
    folder: DataFolder,
) -> None:
    """The problems come after those of the lists, in the file's order, with no place."""
    text = 'version = 1\ncategories = []\ningredients = []\ntags = []\npantry = ["盐"]\n'
    write(folder.catalog, text)
    catalog, problems = read_catalog(folder)
    assert catalog == Catalog((), (), ())
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (None, m_unknown_key("version", TOP_KEYS)),
            (None, m_unknown_key("pantry", TOP_KEYS)),
        ],
    )
