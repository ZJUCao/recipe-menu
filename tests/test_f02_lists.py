"""Tests of F02 for and_list, comma_list, and choose_lang (F02-T29 to F02-T42)."""

from collections.abc import Callable, Iterable, Iterator
from functools import partial

from f02_support import (
    CATALOG,
    CHECKED,
    EN,
    MEALS,
    PANTRY,
    QUICK,
    QUOTED,
    RECIPES,
    SERVINGS,
    SETTINGS,
    WEEK_MENUS,
    ZH,
    Colour,
    MealKind,
    Size,
    raises,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural, and_list, choose_lang, comma_list

SIX_LISTS = [
    [],
    ["a"],
    ["a", "b"],
    ["a", "b", "c"],
    ["a", "b", "c", "d"],
    ["a", "b", "c", "d", "e"],
]


def letters() -> Iterator[str]:
    """Yields the items ``a``, ``b``, and ``c``.

    Yields:
        One item at a time.
    """
    yield from "abc"


def mixed() -> Iterator[object]:
    """Yields a ``str`` and then ``None``.

    Yields:
        One item at a time.
    """
    yield "a"
    yield None


def test_f02_t29_and_list_follows_the_table_of_the_design() -> None:
    """Lists of 0 to 5 items follow the table of design 2.6 in both languages."""
    expected = [
        BiText("", ""),
        BiText("a", "a"),
        BiText("a and b", "a 和 b"),
        BiText("a, b, and c", "a、b 和 c"),
        BiText("a, b, c, and d", "a、b、c 和 d"),
        BiText("a, b, c, d, and e", "a、b、c、d 和 e"),
    ]
    for items, text in zip(SIX_LISTS, expected, strict=True):
        assert and_list(items) == text


def test_f02_t30_comma_list_follows_the_table_of_the_design() -> None:
    """Lists of 0 to 5 items follow the table of design 2.6, with no extra spaces."""
    expected = [
        BiText("", ""),
        BiText("a", "a"),
        BiText("a, b", "a、b"),
        BiText("a, b, c", "a、b、c"),
        BiText("a, b, c, d", "a、b、c、d"),
        BiText("a, b, c, d, e", "a、b、c、d、e"),
    ]
    for items, text in zip(SIX_LISTS, expected, strict=True):
        assert comma_list(items) == text
    assert comma_list(["1", "2"]) == BiText("1, 2", "1、2")


def test_f02_t31_each_language_joins_the_texts_in_that_language() -> None:
    """An item that lacks a language falls back on its own, and a ``str`` is the same in both."""
    assert and_list(MEALS) == BiText("breakfast, lunch, and dinner", "早餐、午餐和晚餐")
    assert and_list(MEALS[1:]) == BiText("lunch and dinner", "午餐和晚餐")
    assert and_list(MEALS[2:]) == BiText("dinner", "晚餐")
    quick_veg = comma_list([BiText("quick", "快手"), BiText("vegetarian", "素")])
    assert quick_veg == BiText("quick, vegetarian", "快手、素")
    assert comma_list([BiText("quick", "快手"), BiText(zh="素")]) == BiText("quick, 素", "快手、素")
    tofu = and_list([BiText("tofu", "豆腐"), BiText(en="quick")])
    assert tofu == BiText("tofu and quick", "豆腐和 quick")
    assert and_list([BiText(zh="素")]) == BiText("素", "素")
    assert comma_list([BiText(en="quick")]) == BiText("quick", "quick")
    assert and_list(["produce", "meat", "eggs"]) == BiText(
        "produce, meat, and eggs", "produce、meat 和 eggs"
    )
    assert comma_list(["tomato-egg", BiText("rice", "米饭")]) == BiText(
        "tomato-egg, rice", "tomato-egg、米饭"
    )


def test_f02_t32_space_next_to_he_depends_on_the_ascii_character() -> None:
    """In Chinese, a space goes next to the joining word only beside an ASCII letter or digit."""
    cases = [
        (["番茄", "quick"], "番茄和 quick"),
        (["quick", "番茄"], "quick 和番茄"),
        (["7 个菜谱", "1 个周菜单"], "7 个菜谱和 1 个周菜单"),
        (["W47", "2026"], "W47 和 2026"),
        (["0", "z"], "0 和 z"),
        (["Z", "9"], "Z 和 9"),
        (["A", "a"], "A 和 a"),
        (["“葱”", "“quick”"], "“葱”和“quick”"),
        (["x.", "(y)"], "x.和(y)"),
        (["x_", "_y"], "x_和_y"),
        (["café", "茶"], "café和茶"),
        (["茶", "été"], "茶和été"),
        (["\uff21", "\uff11"], "\uff21和\uff11"),
        (["番茄", "quick", "tofu"], "番茄、quick 和 tofu"),
        (["quick", "tofu", "番茄"], "quick、tofu 和番茄"),
    ]
    for items, chinese in cases:
        result = and_list(items)
        assert result.zh == chinese
        if len(items) == 2:
            assert result.en == f"{items[0]} and {items[1]}"
    assert and_list(["番茄", "quick", "tofu"]).en == "番茄, quick, and tofu"
    assert and_list(["quick", "tofu", "番茄"]).en == "quick, tofu, and 番茄"


def test_f02_t33_empty_item_has_no_character_next_to_he() -> None:
    """No space goes between an empty item and the joining word, and English joins it as usual."""
    assert and_list(["", "b"]) == BiText(" and b", "和 b")
    assert and_list(["a", ""]) == BiText("a and ", "a 和")
    assert and_list(["", ""]) == BiText(" and ", "和")
    assert and_list(["a", "", "c"]) == BiText("a, , and c", "a、和 c")
    assert and_list([""]) == BiText("", "")
    assert and_list([BiText("x", ""), "b"]) == BiText("x and b", "和 b")
    assert comma_list(["", "b"]) == BiText(", b", "、b")


def test_f02_t34_spacing_reads_the_chinese_text_of_each_item() -> None:
    """For an item with no Chinese, the spacing rules read its English text."""
    both = and_list([BiText("quick", "快手"), BiText("tofu", "豆腐")])
    assert both == BiText("quick and tofu", "快手和豆腐")
    assert and_list([BiText(en="tofu"), BiText("rice", "米饭")]) == BiText(
        "tofu and rice", "tofu 和米饭"
    )
    assert and_list([BiText(zh="素"), BiText(en="quick")]) == BiText("素 and quick", "素和 quick")
    assert and_list([BiText("tofu", "豆腐"), BiText(en="quick")]) == BiText(
        "tofu and quick", "豆腐和 quick"
    )


def test_f02_t35_items_can_be_any_iterable() -> None:
    """``items`` can be a generator, a tuple, or an iterator."""
    assert and_list(letters()) == BiText("a, b, and c", "a、b 和 c")
    assert and_list(("a", "b")) == BiText("a and b", "a 和 b")
    assert and_list(iter([])) == BiText("", "")
    assert comma_list(item for item in MEALS) == BiText(
        "breakfast, lunch, dinner", "早餐、午餐、晚餐"
    )


def test_f02_t36_wrong_items_are_a_wrong_call() -> None:
    """A single ``str`` as ``items`` and an item of a wrong type raise ``TypeError``."""
    wrong_items: list[object] = [
        None,
        3,
        b"a",
        ["a"],
        Lang.ZH,
        MealKind.DINNER,
        Colour.RED,
        Size.ONE,
        Message("a", "甲"),
    ]
    functions: list[Callable[[Iterable[object]], object]] = [and_list, comma_list]  # type: ignore[list-item]
    for function in functions:
        raises(TypeError, partial(function, "abc"))
        raises(TypeError, partial(function, ""))
        for item in wrong_items:
            raises(TypeError, partial(function, [item]))
            raises(TypeError, partial(function, ["a", item]))

        raises(TypeError, partial(function, mixed()))


def test_f02_t37_a_list_of_rendered_messages_inside_a_message() -> None:
    """The first line of ``check``: rendered messages and plurals inside another message."""
    expected = [
        (
            7,
            1,
            "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
            "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。",
        ),
        (
            1,
            0,
            "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
            "已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。",
        ),
        (
            2,
            0,
            "Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus.",
            "已检查设置、目录、常备清单、2 个菜谱和 0 个周菜单。",
        ),
    ]
    for recipes, week_menus, english, chinese in expected:
        files = and_list(
            [
                SETTINGS.to_bitext(),
                CATALOG.to_bitext(),
                PANTRY.to_bitext(),
                RECIPES.pick(recipes).to_bitext(count=recipes),
                WEEK_MENUS.pick(week_menus).to_bitext(count=week_menus),
            ]
        )
        assert CHECKED.render(EN, files=files) == english
        assert CHECKED.render(ZH, files=files) == chinese


def quoted_list(words: list[str]) -> BiText:
    """Joins the quoted words with ``and_list``.

    Args:
        words: The words.

    Returns:
        The list of the quoted words.
    """
    return and_list([QUOTED.to_bitext(word=word) for word in words])


def test_f02_t38_quoted_words_of_the_search_prototype() -> None:
    """The quoted words of the F10 prototype."""
    match = Message("{count} recipes match {words}.", "{count} 个菜谱同时匹配{words}。")
    no_match = Message("No recipe matches {words}.", "没有菜谱同时匹配{words}。")
    assert quoted_list(["葱", "quick"]) == BiText('"葱" and "quick"', "“葱”和“quick”")
    assert quoted_list(["豆腐", "quick"]) == BiText('"豆腐" and "quick"', "“豆腐”和“quick”")
    two = quoted_list(["葱", "quick"])
    assert match.render(ZH, count=2, words=two) == "2 个菜谱同时匹配“葱”和“quick”。"
    none = quoted_list(["豆腐", "quick"])
    assert no_match.render(ZH, words=none) == "没有菜谱同时匹配“豆腐”和“quick”。"
    assert match.render(EN, count=2, words=quoted_list(["番茄"])) == '2 recipes match "番茄".'
    assert match.render(EN, count=2, words=quoted_list(["TOMATO"])) == '2 recipes match "TOMATO".'
    assert no_match.render(EN, words=quoted_list(["lamb"])) == 'No recipe matches "lamb".'


INIT_SETTINGS = Message(
    "{language}, {meals}, {count} servings per dish", "{language}，{meals}，每道菜 {count} 份"
)
DAYS = Message("7 days with {meals}, all empty.", "7 天都有{meals}，都是空的。")
UNKNOWN_TAG = Message(
    'Unknown tag "{tag}". The tags are {tags}.', "未知标签“{tag}”。标签有{tags}。"
)
UNKNOWN_CATEGORY = Message(
    'Unknown category "{category}". The categories are {categories}.',
    "未知分类“{category}”。分类有{categories}。",
)
UNKNOWN_MEAL = Message(
    'Unknown meal "{meal}". The meals are {meals}.', "未知餐次“{meal}”。餐次有{meals}。"
)
MEAL_NOT_SET = Message(
    'Unknown meal "{meal}". The settings name {meals}.',
    "未知餐次“{meal}”。设置里的餐次是{meals}。",
)
TAGS5 = [
    BiText("quick", "快手"),
    BiText("home-style", "家常"),
    BiText("vegetarian", "素"),
    BiText("spicy", "辣"),
    BiText("staple", "主食"),
]
CATEGORIES = ["produce", "meat", "eggs", "staples", "seasonings", "other"]


def test_f02_t39_lists_inside_sentences_of_the_prototypes() -> None:
    """Lists inside sentences of the F05, F07, F08, F09, and F11 prototypes and of v0.1-S16."""
    assert (
        INIT_SETTINGS.render(EN, language="English", meals=and_list(MEALS[1:]), count=2)
        == "English, lunch and dinner, 2 servings per dish"
    )
    assert (
        INIT_SETTINGS.render(ZH, language="中文", meals=and_list(MEALS[1:]), count=2)
        == "中文，午餐和晚餐，每道菜 2 份"
    )
    assert DAYS.render(EN, meals=and_list(MEALS[1:])) == "7 days with lunch and dinner, all empty."
    assert (
        DAYS.render(EN, meals=and_list(MEALS))
        == "7 days with breakfast, lunch, and dinner, all empty."
    )
    assert and_list(TAGS5) == BiText(
        "quick, home-style, vegetarian, spicy, and staple", "快手、家常、素、辣和主食"
    )
    assert (
        UNKNOWN_TAG.render(EN, tag="breakfast", tags=and_list(TAGS5))
        == 'Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.'
    )
    assert and_list(CATEGORIES) == BiText(
        "produce, meat, eggs, staples, seasonings, and other",
        "produce、meat、eggs、staples、seasonings 和 other",
    )
    assert (
        UNKNOWN_CATEGORY.render(EN, category="meats", categories=and_list(CATEGORIES))
        == 'Unknown category "meats". The categories are '
        "produce, meat, eggs, staples, seasonings, and other."
    )
    assert (
        UNKNOWN_MEAL.render(EN, meal="supper", meals=and_list(MEALS))
        == 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
    )
    assert (
        MEAL_NOT_SET.render(EN, meal="supper", meals=and_list(MEALS[1:]))
        == 'Unknown meal "supper". The settings name lunch and dinner.'
    )


def test_f02_t40_plain_lists_inside_lines_of_the_prototypes() -> None:
    """Plain lists inside lines of the F09 and F13 prototypes and of v0.1-S16."""
    pantry_line = Message(
        "Not on the list, because they are in the pantry: {items}", "常备，不用买：{items}"
    )
    items = [
        BiText("cooking oil", "食用油"),
        BiText("salt", "盐"),
        BiText("sugar", "糖"),
        BiText("soy sauce", "生抽"),
        BiText("Sichuan pepper", "花椒"),
    ]
    assert pantry_line.render(EN, items=comma_list(items)) == (
        "Not on the list, because they are in the pantry: "
        "cooking oil, salt, sugar, soy sauce, Sichuan pepper"
    )
    assert (
        pantry_line.render(ZH, items=comma_list(items))
        == "常备，不用买：食用油、盐、糖、生抽、花椒"
    )
    assert pantry_line.render(EN, items=comma_list(items[:3])) == (
        "Not on the list, because they are in the pantry: cooking oil, salt, sugar"
    )
    home = BiText("home-style", "家常")
    both = comma_list([QUICK, home])
    assert SERVINGS.render(EN, count=2, tags=both) == "Servings: 2   Tags: quick, home-style"
    assert SERVINGS.render(EN, count=2, tags=comma_list([home])) == "Servings: 2   Tags: home-style"
    assert SERVINGS.render(ZH, count=2, tags=both) == "份数：2   标签：快手、家常"


def test_f02_t41_two_counts_in_one_line() -> None:
    """Two counts in one line, as in F11 and v0.1-S16."""
    meals = Plural(Message("{count} meal", "{count} 餐"), Message("{count} meals", "{count} 餐"))
    dishes = Plural(
        Message("{count} dish", "{count} 道菜"), Message("{count} dishes", "{count} 道菜")
    )
    summary = Message("{meals}, {dishes}. ×n: servings.", "{meals}，{dishes}。×n：份数。")
    for meal_count, dish_count, english in [
        (4, 9, "4 meals, 9 dishes. ×n: servings."),
        (1, 1, "1 meal, 1 dish. ×n: servings."),
    ]:
        values = {
            "meals": meals.pick(meal_count).to_bitext(count=meal_count),
            "dishes": dishes.pick(dish_count).to_bitext(count=dish_count),
        }
        assert summary.render(EN, **values) == english
    values = {
        "meals": meals.pick(4).to_bitext(count=4),
        "dishes": dishes.pick(9).to_bitext(count=9),
    }
    assert summary.render(ZH, **values) == "4 餐，9 道菜。×n：份数。"


def test_f02_t42_option_comes_first_then_setting_then_english() -> None:
    """``--lang`` comes first, then the settings, then English."""
    cases: list[tuple[Lang | None, Lang | None, Lang]] = [
        (EN, EN, EN),
        (EN, ZH, EN),
        (EN, None, EN),
        (ZH, EN, ZH),
        (ZH, ZH, ZH),
        (ZH, None, ZH),
        (None, EN, EN),
        (None, ZH, ZH),
        (None, None, EN),
    ]
    for option, setting, expected in cases:
        assert choose_lang(option, setting) is expected
