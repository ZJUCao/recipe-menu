"""Tests of F03 for the duplicate checks and the order of the problems (F03-T63 to F03-T71)."""

from f03_support import (
    CATALOG_FILE,
    CATEGORY_KEYS,
    INGREDIENT_KEYS,
    M_ITEM_NOT_A_TABLE,
    PRODUCE_ITEM,
    QUICK_ITEM,
    TAG_KEYS,
    TOP_KEYS,
    at_category,
    at_ingredient,
    at_tag,
    check_problems,
    en_names,
    ing,
    m_dup_en,
    m_dup_key,
    m_dup_zh,
    m_empty_text,
    m_missing_key,
    m_not_a_text,
    m_unknown_category,
    m_unknown_key,
    m_unknown_unit,
    produce,
    write,
    write_catalog,
)
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag, read_catalog
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.units import Unit


def test_f03_t63_a_duplicate_ingredient_name_gives_a_problem_and_is_skipped(
    folder: DataFolder,
) -> None:
    """The Chinese name, then the English name, is matched against both names of kept items."""
    rows = [
        ("番茄", "Tomato"),
        ("西兰花", "Broccoli"),
        ("番茄", "Tomatoes"),
        ("西红柿", " tomato "),
        ("Broccoli", "Chinese broccoli"),
        ("芥兰", "番茄"),
        ("番茄", "broccoli"),
        ("芥兰", "Chinese broccoli"),
    ]
    write_catalog(folder, [PRODUCE_ITEM], [ing(zh, en) for zh, en in rows])
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert en_names(catalog.ingredients) == ["Tomato", "Broccoli", "Chinese broccoli"]
    one, two = at_ingredient(1), at_ingredient(2)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(3), m_dup_zh("番茄", one)),
            (at_ingredient(4), m_dup_en("tomato", one)),
            (at_ingredient(5), m_dup_zh("Broccoli", two)),
            (at_ingredient(6), m_dup_en("番茄", one)),
            (at_ingredient(7), m_dup_zh("番茄", one)),
            (at_ingredient(7), m_dup_en("broccoli", two)),
        ],
    )


def test_f03_t64_the_duplicate_check_matches_names_by_the_rules_of_design_2_6(
    folder: DataFolder,
) -> None:
    """Ends and the case of A to Z do not count, and look-alikes and inner spaces do."""
    rows = [
        ("大米", "Rice"),
        ("米", "RICE"),
        ("米饭", "\u3000rice\t"),
        ("羽衣甘蓝", "Kale"),
        ("甘蓝", "\u212aale"),
        ("葱", "Scallion"),
        ("葱\u200b", "\u017fcallion"),
        ("菜心", "Choy sum"),
        ("小菜心", "Choy  sum"),
        ("墨西哥辣椒", "Jalape\u00f1o"),
        ("辣椒", "jalapen\u0303o"),
        ("青椒", "JALAPE\u00d1O"),
    ]
    write_catalog(folder, [PRODUCE_ITEM], [ing(zh, en) for zh, en in rows])
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert len(catalog.ingredients) == 10
    assert [i.name.zh for i in catalog.ingredients] == [
        zh for number, (zh, _) in enumerate(rows, start=1) if number not in (2, 3)
    ]
    first = at_ingredient(1)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(2), m_dup_en("RICE", first)),
            (at_ingredient(3), m_dup_en("rice", first)),
        ],
    )


def test_f03_t65_an_item_that_is_kept_with_a_problem_is_still_checked_for_duplicates(
    folder: DataFolder,
) -> None:
    """An item that is skipped by an earlier check is not, and every field is checked."""
    write_catalog(
        folder,
        [PRODUCE_ITEM],
        [
            ing("葱", "Scallion", unit='"根"'),
            ing("葱", "Green onion", unit='"cups"'),
            '{ zh = "大葱", en = "scallion", category = "produce", size = "big" }',
            ing("小葱", "SCALLION", unit="2"),
            ing("葱", "Scallion", "meats"),
            ing("葱", "", "produce"),
            ing("葱", "", "meats", unit='"cups"'),
        ],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert en_names(catalog.ingredients) == ["Scallion"]
    assert catalog.ingredients[0].unit is Unit.STALK
    one = at_ingredient(1)
    meats = m_unknown_category("meats", "produce")
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_ingredient(2), m_unknown_unit("cups")),
            (at_ingredient(2), m_dup_zh("葱", one)),
            (at_ingredient(3), m_unknown_key("size", INGREDIENT_KEYS)),
            (at_ingredient(3), m_dup_en("scallion", one)),
            (at_ingredient(4), m_not_a_text("unit")),
            (at_ingredient(4), m_dup_en("SCALLION", one)),
            (at_ingredient(5), meats),
            (at_ingredient(6), m_empty_text("en")),
            (at_ingredient(7), m_empty_text("en")),
            (at_ingredient(7), meats),
            (at_ingredient(7), m_unknown_unit("cups")),
        ],
    )


def test_f03_t66_a_skipped_item_holds_no_key_and_no_name(folder: DataFolder) -> None:
    """A later item may use the key or the name of a skipped category or tag."""
    write_catalog(
        folder,
        [
            '{ zh = "其他", en = "Other" }',
            '{ key = "other", zh = "其他", en = "Other" }',
            PRODUCE_ITEM,
            '{ key = "produce", zh = "水果", en = "Fruit" }',
            '{ key = "fruit", zh = "水果", en = "Fruit" }',
        ],
        [ing("苹果", "Apple", "fruit")],
        ['{ zh = "快手", en = "" }', QUICK_ITEM],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert [category.key for category in catalog.categories] == ["other", "produce", "fruit"]
    assert en_names(catalog.ingredients) == ["Apple"]
    assert catalog.ingredients[0].category is catalog.categories[2]
    assert en_names(catalog.tags) == ["quick"]
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), m_missing_key("key")),
            (at_category(4), m_dup_key("produce", at_category(3))),
            (at_tag(1), m_empty_text("en")),
        ],
    )


def test_f03_t67_a_category_with_a_key_that_matches_is_skipped_and_its_names_are_checked(
    folder: DataFolder,
) -> None:
    """The ingredients of that key find the first category."""
    write_catalog(
        folder,
        [
            PRODUCE_ITEM,
            '{ key = " Produce ", zh = "水果", en = "Fruit" }',
            '{ key = "PRODUCE", zh = "青菜", en = "" }',
            '{ key = "produce", zh = "蔬菜水果", en = "Greens" }',
        ],
        [ing("番茄", "Tomato", "Produce")],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert catalog.categories == (produce,)
    assert en_names(catalog.ingredients) == ["Tomato"]
    assert catalog.ingredients[0].category is catalog.categories[0]
    one = at_category(1)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(2), m_dup_key("Produce", one)),
            (at_category(3), m_empty_text("en")),
            (at_category(3), m_dup_key("PRODUCE", one)),
            (at_category(4), m_dup_key("produce", one)),
            (at_category(4), m_dup_zh("蔬菜水果", one)),
        ],
    )


def test_f03_t68_a_category_with_a_name_that_matches_is_kept(folder: DataFolder) -> None:
    """Its ingredients still find it, and only the usable names are compared."""
    write_catalog(
        folder,
        [
            PRODUCE_ITEM,
            '{ key = "greens", zh = "青菜", en = "vegetables and fruit" }',
            '{ key = "fruit", zh = "水果", en = "Vegetables and fruit" }',
            '{ key = "veg", zh = "Vegetables and fruit", en = "蔬菜水果" }',
            '{ key = "misc", zh = "", en = "Other" }',
            '{ key = "misc2", zh = "", en = "Misc" }',
        ],
        [ing("青菜", "Greens", "greens"), ing("苹果", "Apple", "fruit")],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    keys = [category.key for category in catalog.categories]
    assert keys == ["produce", "greens", "fruit", "veg", "misc", "misc2"]
    assert catalog.categories[4] == Category("misc", BiText(en="Other"))
    assert catalog.categories[5] == Category("misc2", BiText(en="Misc"))
    assert en_names(catalog.ingredients) == ["Greens", "Apple"]
    assert catalog.ingredients[0].category is catalog.categories[1]
    assert catalog.ingredients[1].category is catalog.categories[2]
    one = at_category(1)
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(2), m_dup_en("vegetables and fruit", one)),
            (at_category(3), m_dup_en("Vegetables and fruit", one)),
            (at_category(4), m_dup_zh("Vegetables and fruit", one)),
            (at_category(4), m_dup_en("蔬菜水果", one)),
            (at_category(5), m_empty_text("zh")),
            (at_category(6), m_empty_text("zh")),
        ],
    )


def test_f03_t69_a_tag_with_a_name_that_matches_is_skipped(folder: DataFolder) -> None:
    """Tags are compared only with tags."""
    write_catalog(
        folder,
        [PRODUCE_ITEM],
        [ing("豆腐", "Tofu")],
        [
            QUICK_ITEM,
            '{ zh = "快速", en = "Quick" }',
            '{ zh = "快手", en = "fast" }',
            '{ zh = "豆腐", en = "Tofu" }',
        ],
    )
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert en_names(catalog.ingredients) == ["Tofu"]
    assert en_names(catalog.tags) == ["quick", "Tofu"]
    one = at_tag(1)
    check_problems(
        problems,
        CATALOG_FILE,
        [(at_tag(2), m_dup_en("Quick", one)), (at_tag(3), m_dup_zh("快手", one))],
    )


def test_f03_t70_the_problems_come_in_the_order_of_design_2_8(folder: DataFolder) -> None:
    """The lists, then the other keys at the top, and inside an item the fields come first."""
    lines = [
        'note = "x"',
        "tags = [",
        '  { zh = "快手", en = "quick", extra = 1 },',
        "]",
        "ingredients = [",
        '  { zh = "番茄", en = "Tomato", category = "produce" },',
        '  { extra = 1, unit = "cups", category = "produce", en = "tomato", zh = "番茄" },',
        '  { b = 1, a = 2, zh = "葱", en = "Scallion", category = "meats" },',
        "]",
        "categories = [",
        '  "produce",',
        '  { key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" },',
        '  { en = "", zh = "蔬菜水果", key = "produce", x = 1 },',
        "]",
    ]
    write(folder.catalog, "\n".join(lines) + "\n")
    catalog, problems = read_catalog(folder)
    assert catalog is not None
    assert catalog.categories == (produce,)
    assert en_names(catalog.ingredients) == ["Tomato"]
    assert catalog.tags == (Tag(BiText("quick", "快手")),)
    two, one = at_category(2), at_ingredient(1)
    ing_keys = INGREDIENT_KEYS
    check_problems(
        problems,
        CATALOG_FILE,
        [
            (at_category(1), M_ITEM_NOT_A_TABLE),
            (at_category(3), m_empty_text("en")),
            (at_category(3), m_unknown_key("x", CATEGORY_KEYS)),
            (at_category(3), m_dup_key("produce", two)),
            (at_category(3), m_dup_zh("蔬菜水果", two)),
            (at_ingredient(2), m_unknown_unit("cups")),
            (at_ingredient(2), m_unknown_key("extra", ing_keys)),
            (at_ingredient(2), m_dup_zh("番茄", one)),
            (at_ingredient(2), m_dup_en("tomato", one)),
            (at_ingredient(3), m_unknown_category("meats", "produce")),
            (at_ingredient(3), m_unknown_key("b", ing_keys)),
            (at_ingredient(3), m_unknown_key("a", ing_keys)),
            (at_tag(1), m_unknown_key("extra", TAG_KEYS)),
            (None, m_unknown_key("note", TOP_KEYS)),
        ],
    )


def test_f03_t71_the_two_names_of_one_item_may_match_each_other(folder: DataFolder) -> None:
    """A category, an ingredient, and a tag with matching names give no problem."""
    write_catalog(
        folder,
        ['{ key = "other", zh = "Other", en = "other" }'],
        [ing("Pizza", "pizza", "other")],
        ['{ zh = "BBQ", en = "bbq" }'],
    )
    catalog, problems = read_catalog(folder)
    assert problems == ()
    other = Category("other", BiText("other", "Other"))
    pizza = Ingredient(BiText("pizza", "Pizza"), other)
    assert catalog == Catalog((other,), (pizza,), (Tag(BiText("bbq", "BBQ")),))
