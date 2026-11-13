"""Tests of F09 for ``recipe-menu list``: the example, the tags, the counts, and no recipe."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f07_changes import edit, make_init, mapo_mistake
from f09_support import (
    at,
    empty_recipes,
    made,
    no_catalog,
    no_tags,
    not_recipes,
    one_tag,
    rice_bowl,
    soup,
    two_tags,
)
from f09_texts import (
    BREAKFAST,
    BREAKFAST_ZH,
    E_CHOY_TAG_QUICK,
    E_CHOY_TAG_VEG,
    E_MAPO,
    E_NO_CATALOG,
    INIT_LIST,
    INIT_LIST_ZH,
    LIST,
    LIST_ZH,
    QUICK,
    QUICK_ZH,
    RUN_HELP_COMMANDS,
    TAGS_LINE,
    VEG,
    VEG_ZH,
    err,
    out,
    stop,
    tagged,
    unknown_tag,
)
from recipe_menu.datafile import DataFolder

LIST_EXTRA = err(
    2, ['Unexpected argument "extra". Write "recipe-menu list".', RUN_HELP_COMMANDS[0]]
)


def _tags_and_languages(home: Path, example: DataFolder) -> None:
    """Checks the lists, the tags in both languages, and an unknown tag, as in the example."""
    assert at(home, example, "list") == out(LIST)
    assert at(home, example, "list", "--lang", "zh") == out(LIST_ZH)
    assert at(home, example, "list", "--tag", "快手") == out(QUICK)
    assert at(home, example, "list", "--tag", " QUICK ") == out(QUICK)
    assert at(home, example, "list", "--tag", "quick", "--lang", "zh") == out(QUICK_ZH)
    assert at(home, example, "list", "--tag", "breakfast") == err(1, [BREAKFAST])
    zh = at(home, example, "list", "--tag", "breakfast", "--lang", "zh")
    assert zh == err(1, [BREAKFAST_ZH])


def _language_of_the_settings(home: Path, example: DataFolder) -> None:
    """Checks that the settings give the language, and that ``--lang`` wins."""
    edit(example.settings, 'language = "en"', 'language = "zh"')
    assert at(home, example, "list", "--tag", "素") == out(VEG_ZH)
    assert at(home, example, "list", "--tag", "素", "--lang", "en") == out(VEG)
    edit(example.settings, 'language = "zh"', 'language = "en"')


def _catalog_changes(home: Path, example: DataFolder) -> None:
    """Checks a tag that no recipe has, and a catalog with no tags."""
    original = example.catalog.read_text(encoding="utf-8")
    soup(example.root)
    assert at(home, example, "list", "--tag", "汤") == out(['No recipe has the tag "soup".'])
    zh = at(home, example, "list", "--tag", "soup", "--lang", "zh")
    assert zh == out(["没有菜谱带有标签“汤”。"])
    write(example.catalog, original)
    no_tags(example.root)
    no_quick = ['Unknown tag "quick". The catalog has no tags.']
    assert at(home, example, "list", "--tag", "quick") == err(1, no_quick)
    assert at(home, example, "list") == stop(E_CHOY_TAG_QUICK)
    write(example.catalog, original)


def _mistakes(home: Path, example: DataFolder) -> None:
    """Checks a mistake in ``mapo-tofu``, a word after ``list``, and a folder with no recipe."""
    mapo_mistake(example.root)
    assert at(home, example, "list") == stop(E_MAPO)
    assert at(home, example, "list", "--tag", "breakfast") == err(1, [BREAKFAST])
    assert at(home, example, "list", "extra") == LIST_EXTRA
    empty_recipes(example.root)
    assert at(home, example, "list") == out(["No recipes."])
    assert at(home, example, "list", "--lang", "zh") == out(["没有菜谱。"])
    assert at(home, example, "list", "--tag", "quick") == out(['No recipe has the tag "quick".'])


def test_f09_t04_the_example_of_list_runs_in_order_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.2, step by step, with ``main`` and the real ``COMMANDS``."""
    home = make_home(tmp_path)
    _tags_and_languages(home, example_folder)
    _language_of_the_settings(home, example_folder)
    _catalog_changes(home, example_folder)
    _mistakes(home, example_folder)


def test_f09_t05_scenarios_s09_and_s10_give_the_prototype_lists_and_find_a_tag_by_its_names(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype outputs, the tag in either language, and what counts as the same tag."""
    home = make_home(tmp_path)
    assert at(home, example_folder, "list") == out(LIST)
    assert at(home, example_folder, "list", "--lang", "zh") == out(LIST_ZH)
    assert at(home, example_folder, "list", "--tag", "快手") == out(QUICK)
    quick_zh = at(home, example_folder, "list", "--tag", "quick", "--lang", "zh")
    assert quick_zh == out(QUICK_ZH)
    assert at(home, example_folder, "list", "--tag", "breakfast") == err(1, [BREAKFAST])
    for tag in ("quick", "QUICK", "Quick", " quick ", "\u00a0quick\u3000", "快手 ", "\t快手"):
        assert at(home, example_folder, "list", "--tag", tag) == out(QUICK), repr(tag)
    for tag in ("quick\u200b", "home style"):
        assert at(home, example_folder, "list", "--tag", tag) == err(1, [unknown_tag(tag)]), tag


def test_f09_t06_the_count_line_takes_its_form_for_one_or_for_more(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """One recipe, two, and four, and the tag in the language of the output."""
    home = make_home(tmp_path)
    home_style = tagged(LIST, (1, 3, 4, 5, 7), '4 recipes have the tag "home-style".')
    home_style_zh = tagged(LIST_ZH, (1, 3, 4, 5, 7), "共 4 个菜谱带有标签“家常”。")
    assert at(home, example_folder, "list", "--tag", "home-style") == out(home_style)
    zh = at(home, example_folder, "list", "--tag", "家常", "--lang", "zh")
    assert zh == out(home_style_zh)
    spicy = tagged(LIST, (1, 4), '1 recipe has the tag "spicy".')
    assert at(home, example_folder, "list", "--tag", "spicy") == out(spicy)
    assert at(home, example_folder, "list", "--tag", "辣") == out(spicy)
    staple_zh = tagged(LIST_ZH, (1, 6, 8), "共 2 个菜谱带有标签“主食”。")
    assert at(home, example_folder, "list", "--tag", "staple", "--lang", "zh") == out(staple_zh)
    init = make_init(example_folder, tmp_path / "init")
    assert at(home, init, "list") == out(INIT_LIST)
    assert at(home, init, "list", "--lang", "zh") == out(INIT_LIST_ZH)


# One tag, two tags, and no tags: the change, the message for one name, and the first error.
TAG_CASES = [
    (
        one_tag,
        'Unknown tag "breakfast". The only tag is quick.',
        "未知标签“breakfast”。现有标签：快手。",
        E_CHOY_TAG_VEG,
    ),
    (
        two_tags,
        'Unknown tag "breakfast". The tags are quick and home-style.',
        "未知标签“breakfast”。现有标签：快手和家常。",
        E_CHOY_TAG_VEG,
    ),
    (
        no_tags,
        'Unknown tag "breakfast". The catalog has no tags.',
        "未知标签“breakfast”。目录里没有标签。",
        E_CHOY_TAG_QUICK,
    ),
]


def test_f09_t07_an_unknown_tag_names_the_value_and_the_tags_and_comes_before_the_recipes(
    example_folder: DataFolder, tmp_path: Path, default_int_limit: None
) -> None:
    """The three forms of the message, the typed value, and the order of the reads."""
    home = make_home(tmp_path)
    spaced = " Breakfast "
    assert at(home, example_folder, "list", "--tag", spaced) == err(
        1, [f'Unknown tag "{spaced}". {TAGS_LINE}']
    )
    long_tag = "9" * 5000
    assert at(home, example_folder, "list", "--tag", long_tag) == err(1, [unknown_tag(long_tag)])
    both = made(example_folder, tmp_path, "both", mapo_mistake, rice_bowl)
    assert at(home, both, "list", "--tag", "breakfast") == err(1, [BREAKFAST])
    assert at(home, both, "list", "--tag", "breakfast", "--lang", "zh") == err(1, [BREAKFAST_ZH])
    for change, english, chinese, error in TAG_CASES:
        root = made(example_folder, tmp_path, change.__name__, change)
        assert at(home, root, "list", "--tag", "breakfast") == err(1, [english])
        assert at(home, root, "list", "--tag", "breakfast", "--lang", "zh") == err(1, [chinese])
        assert at(home, root, "list") == stop(error)
    bare = made(example_folder, tmp_path, "bare", no_catalog)
    assert at(home, bare, "list", "--tag", "breakfast") == stop(E_NO_CATALOG)


def test_f09_t08_a_list_with_no_recipe_is_one_line_with_exit_code_0(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """No recipe files, no recipe with the tag, and entries that are no recipe files."""
    home = make_home(tmp_path)
    empty = made(example_folder, tmp_path, "empty", empty_recipes)
    assert at(home, empty, "list") == out(["No recipes."])
    assert at(home, empty, "list", "--lang", "zh") == out(["没有菜谱。"])
    assert at(home, empty, "list", "--tag", "quick") == out(['No recipe has the tag "quick".'])
    assert at(home, empty, "list", "--tag", "快手", "--lang", "zh") == out(
        ["没有菜谱带有标签“快手”。"]
    )
    other = made(example_folder, tmp_path, "other", not_recipes)
    assert at(home, other, "list") == out(["No recipes."])
    with_soup = made(example_folder, tmp_path, "soup", soup)
    assert at(home, with_soup, "list", "--tag", "汤") == out(['No recipe has the tag "soup".'])
    zh = at(home, with_soup, "list", "--tag", "soup", "--lang", "zh")
    assert zh == out(["没有菜谱带有标签“汤”。"])
    no_choy = made(example_folder, tmp_path, "no_choy")
    (no_choy / "recipes" / "choy-sum.toml").unlink()
    no_veg = at(home, no_choy, "list", "--tag", "vegetarian")
    assert no_veg == out(['No recipe has the tag "vegetarian".'])
    zh = at(home, no_choy, "list", "--tag", "素", "--lang", "zh")
    assert zh == out(["没有菜谱带有标签“素”。"])
