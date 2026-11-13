"""Tests of F07 for the order of the problems and what one file gives the next (T07 to T10)."""

from pathlib import Path

from f03_support import edit_ingredients, ing, write
from f05_support import copy_example, make_home
from f06_support import MEALS_LUNCH_DINNER
from f07_changes import (
    add_friday_key,
    broken_settings,
    catalog_brace,
    catalog_two,
    edit,
    mapo_mistake,
    menu_copy,
    pantry_not_text,
    pantry_sesame,
    s07_mistakes,
    servings_zero,
    the_typo,
)
from f07_support import AFTER, check, expect, rep
from f07_texts import (
    FILE_MISSING,
    ITEM_NOT_A_TEXT,
    MISSING_BRACE,
    NO_EN_NAME,
    NO_EN_NOTE,
    NOT_A_RECIPE_ID,
    NOT_A_WEEK_NAME,
    P_NAME,
    P_SERVINGS,
    P_TAGS,
    P_WEEK,
    PORK,
    TYPO,
    Prob,
    m_category,
    m_day_key,
    m_duplicate_en,
    m_menu_meal,
    m_pantry_ingredient,
    m_servings,
    m_settings_meal,
    m_unknown_ingredient,
    m_unknown_tag,
    m_unknown_unit,
    m_week_name,
    p_dish,
    p_ingredient,
    p_item,
    p_line,
    p_slot,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

MENU = "menus/2026-W47.toml"
RICE = "recipes/rice.toml"


def test_f07_t07_every_problem_of_four_files_comes_in_the_order_of_the_steps(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The 9 mistakes of v0.1-S07 give 9 errors in order, and the warning has its own block."""
    home = make_home(tmp_path)
    root = example_folder.root
    s07_mistakes(root)
    errors = [
        Prob("catalog.toml", p_ingredient(23), m_duplicate_en("Broccoli", 3)),
        Prob("catalog.toml", p_ingredient(24), m_category("meats")),
        Prob("pantry.toml", p_item(3), m_pantry_ingredient("sesame oil")),
        Prob(RICE, P_SERVINGS, m_servings(0)),
        Prob(RICE, P_TAGS, m_unknown_tag("breakfast")),
        Prob(RICE, p_ingredient(1), m_unknown_unit("cups", "1 cups")),
        Prob(MENU, P_WEEK, m_week_name("2026-W47", "2026-W48")),
        Prob(MENU, p_slot("friday", "supper"), m_menu_meal("supper", MEALS_LUNCH_DINNER)),
        Prob(MENU, p_dish("sunday", "dinner", 1), m_servings(0)),
    ]
    assert check(home, root) == rep(1, 7, 1, errors, [PORK])
    assert check(home, root, "--lang", "zh") == rep(1, 7, 1, errors, [PORK], Lang.ZH)


def test_f07_t08_the_two_blocks_keep_the_order_when_a_recipe_has_both_kinds(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Warnings and errors of the recipes come in turn, and one recipe has both."""
    home = make_home(tmp_path)
    root = example_folder.root
    edit(root / "recipes" / "choy-sum.toml", ', en = "crushed"', "")
    servings_zero(root, "cola-wings")
    tomato = root / "recipes" / "tomato-egg.toml"
    edit(tomato, ', en = "Tomato and egg stir-fry"', "")
    edit(tomato, '["快手", "家常"]', '["快手", "breakfast"]')
    the_typo(root)
    errors = [
        Prob("recipes/cola-wings.toml", P_SERVINGS, m_servings(0)),
        Prob("recipes/tomato-egg.toml", P_TAGS, m_unknown_tag("breakfast")),
        TYPO,
    ]
    warnings = [
        Prob("recipes/choy-sum.toml", p_ingredient(2), NO_EN_NOTE),
        PORK,
        Prob("recipes/tomato-egg.toml", P_NAME, NO_EN_NAME),
    ]
    assert check(home, root) == rep(1, 7, 1, errors, warnings)


def test_f07_t09_the_problems_come_in_the_order_of_the_seven_steps(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The settings, the catalog, the pantry, the recipes, and then the menus in time order."""
    home = make_home(tmp_path)
    root = example_folder.root
    broken_settings(root)
    edit_ingredients(DataFolder(root), added=[ing("芥兰", "Broccoli")])
    pantry_sesame(root)
    write(root / "recipes" / "Rice Bowl.toml", "")
    servings_zero(root, "choy-sum")
    noodles = root / "recipes" / "tomato-egg-noodles.toml"
    edit(noodles, '["快手", "主食"]', '["快手", "breakfast"]')
    write(root / "menus" / "plan.toml", "")
    add_friday_key(menu_copy(root, "2026-W53"))
    edit(
        menu_copy(root, "2027-W01"),
        '"cola-wings", servings = 4',
        '"cola-wings", servings = 0',
    )
    the_typo(root)
    errors = [
        Prob("settings.toml", ("meals", "餐次"), m_settings_meal("supper")),
        Prob("catalog.toml", p_ingredient(23), m_duplicate_en("Broccoli", 3)),
        Prob("pantry.toml", p_item(3), m_pantry_ingredient("sesame oil")),
        Prob("recipes/Rice Bowl.toml", None, NOT_A_RECIPE_ID),
        Prob("recipes/choy-sum.toml", P_SERVINGS, m_servings(0)),
        Prob("recipes/tomato-egg-noodles.toml", P_TAGS, m_unknown_tag("breakfast")),
        Prob("menus/plan.toml", None, NOT_A_WEEK_NAME),
        TYPO,
        Prob("menus/2026-W53.toml", p_slot("friday", "supper"), m_day_key("supper")),
        Prob("menus/2027-W01.toml", p_dish("sunday", "dinner", 1), m_servings(0)),
    ]
    assert check(home, root) == rep(1, 7, 3, errors, [PORK])


def test_f07_t10_what_an_earlier_file_gives_decides_the_checks_of_a_later_one(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A catalog that cannot be read, is missing, or has problems reaches the later files."""
    home = make_home(tmp_path)
    root = example_folder.root
    two = copy_example(example_folder, tmp_path / "two")
    catalog_two(two)
    original = example_folder.catalog.read_text(encoding="utf-8")
    catalog_brace(root)
    mapo_mistake(root)
    pantry_not_text(root)
    brace = Prob("catalog.toml", p_line(11), MISSING_BRACE)
    not_text = Prob("pantry.toml", p_item(3), ITEM_NOT_A_TEXT)
    assert check(home, root) == rep(1, 7, 1, [brace, not_text], [PORK])
    (root / "catalog.toml").unlink()
    missing = Prob("catalog.toml", None, FILE_MISSING)
    assert check(home, root) == rep(1, 7, 1, [missing, not_text], [PORK])

    errors = [
        Prob("catalog.toml", p_ingredient(7), m_category("meats")),
        Prob("catalog.toml", p_ingredient(12), m_duplicate_en("Rice", 4)),
        *(
            Prob(f"recipes/{recipe}.toml", p_ingredient(number), m_unknown_ingredient(name))
            for recipe, number, name in (
                ("cola-wings", 4, "葱"),
                ("mapo-tofu", 6, "葱"),
                ("red-braised-pork", 1, "五花肉"),
                ("red-braised-pork", 5, "葱"),
                ("rice", 1, "大米"),
                ("tomato-egg", 3, "葱"),
                ("tomato-egg-noodles", 4, "葱"),
            )
        ),
    ]
    assert check(home, two) == rep(1, 7, 1, errors, [PORK])
    assert check(home, two, "--lang", "zh") == rep(1, 7, 1, errors, [PORK], Lang.ZH)

    write(two / "catalog.toml", original)
    assert check(home, two) == expect(0, AFTER)
