"""Flow 2, find a recipe: v0.1-S09 to v0.1-S12."""

from support import World, check_result
from texts_find import (
    LIST_EN,
    LIST_ZH,
    SEARCH_LAMB,
    SEARCH_ONE_EN_WORD,
    SEARCH_ONE_ZH_WORD,
    SEARCH_TOFU_ZH,
    SEARCH_TWO_ZH,
    SHOW_EN,
    SHOW_MISSING,
    SHOW_UNKNOWN,
    SHOW_ZH_4,
    TAG_BREAKFAST,
    TAG_QUICK_EN,
    TAG_QUICK_ZH,
)


def test_v0_1_s09_list_the_recipes_in_both_languages(world: World) -> None:
    """v0.1-S09: `list` prints the table in English, and `list --lang zh` in Chinese."""
    world.copy_example()
    check_result(world, world.run("list"), 0, LIST_EN)
    check_result(world, world.run("list", "--lang", "zh"), 0, LIST_ZH)


def test_v0_1_s10_list_the_recipes_with_one_tag_in_either_language(world: World) -> None:
    """v0.1-S10: `--tag` takes the tag's Chinese or English name, and refuses an unknown tag."""
    world.copy_example()
    check_result(world, world.run("list", "--tag", "快手"), 0, TAG_QUICK_EN)
    check_result(world, world.run("list", "--tag", "quick", "--lang", "zh"), 0, TAG_QUICK_ZH)
    check_result(world, world.run("list", "--tag", "breakfast"), 1, TAG_BREAKFAST)


def test_v0_1_s11_search_recipes_in_either_language(world: World) -> None:
    """v0.1-S11: `search` matches Chinese and English words, and no match is not an error."""
    world.copy_example()
    check_result(world, world.run("search", "番茄"), 0, SEARCH_ONE_ZH_WORD)
    check_result(world, world.run("search", "TOMATO"), 0, SEARCH_ONE_EN_WORD)
    check_result(world, world.run("search", "葱", "quick", "--lang", "zh"), 0, SEARCH_TWO_ZH)
    check_result(world, world.run("search", "lamb"), 0, SEARCH_LAMB)
    check_result(world, world.run("search", "豆腐", "quick", "--lang", "zh"), 0, SEARCH_TOFU_ZH)


def test_v0_1_s12_show_a_recipe_scaled_and_with_a_missing_language(world: World) -> None:
    """v0.1-S12: `show` scales with `--servings`, falls back to Chinese steps, and names a miss."""
    world.copy_example()
    check_result(world, world.run("show", "tomato-egg"), 0, SHOW_EN)
    result = world.run("show", "tomato-egg", "--servings", "4", "--lang", "zh")
    check_result(world, result, 0, SHOW_ZH_4)
    check_result(world, world.run("show", "red-braised-pork"), 0, SHOW_MISSING)
    check_result(world, world.run("show", "mapo"), 1, SHOW_UNKNOWN)
