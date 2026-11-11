"""Tests of F02 for BiText and Message (F02-T01 to F02-T24)."""

import datetime
import sys
from collections.abc import Callable
from decimal import Decimal
from fractions import Fraction
from functools import partial
from string import Formatter

import pytest

from f02_support import (
    BRACED,
    EN,
    NO_OTHER,
    SERVINGS,
    TAGS,
    UNKNOWN_RECIPE,
    ZH,
    Colour,
    MealKind,
    Size,
    raises,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import (
    Message,
)


def test_f02_t01_both_languages_give_the_asked_language() -> None:
    """When both languages are set, each method gives the asked language."""
    name = BiText("Tomato and egg stir-fry", "番茄炒蛋")
    assert name.get(EN) == "Tomato and egg stir-fry"
    assert name.exact(EN) == "Tomato and egg stir-fry"
    assert name.get(ZH) == "番茄炒蛋"
    assert name.exact(ZH) == "番茄炒蛋"


def test_f02_t02_missing_language_falls_back_in_get_only() -> None:
    """``get`` falls back to the other language and ``exact`` gives ``None``."""
    for pork in (BiText(zh="红烧肉"), BiText(None, "红烧肉")):
        assert pork.get(EN) == "红烧肉"
        assert pork.get(ZH) == "红烧肉"
        assert pork.exact(EN) is None
        assert pork.exact(ZH) == "红烧肉"
    salt = BiText(en="Salt")
    assert salt.get(ZH) == "Salt"
    assert salt.get(EN) == "Salt"
    assert salt.exact(ZH) is None
    assert salt.exact(EN) == "Salt"


def test_f02_t03_empty_string_is_a_text() -> None:
    """An empty string counts as a text, so ``get`` gives it with no fallback."""
    assert BiText("", "盐").get(EN) == ""
    assert BiText("", "盐").exact(EN) == ""
    assert BiText("Salt", "").get(ZH) == ""
    assert BiText(" ", "盐").get(EN) == " "
    both_empty = BiText("", "")
    assert both_empty.get(EN) == ""
    assert both_empty.get(ZH) == ""
    only_en = BiText(en="")
    assert only_en.get(ZH) == ""
    assert only_en.exact(ZH) is None


def test_f02_t04_text_with_neither_language_is_a_wrong_call() -> None:
    """A ``BiText`` with neither language raises ``ValueError``."""
    raises(ValueError, BiText)
    raises(ValueError, partial(BiText, None, None))
    raises(ValueError, partial(BiText, en=None, zh=None))


def test_f02_t05_language_that_is_not_a_str_is_a_wrong_call() -> None:
    """A language that is neither a ``str`` nor ``None`` raises ``TypeError``."""
    calls: list[Callable[[], object]] = [
        partial(BiText, en=3),
        partial(BiText, zh=3),
        partial(BiText, 3, "三"),
        partial(BiText, "Three", 3.0),
        partial(BiText, en=True),
        partial(BiText, en=b"Salt"),
        partial(BiText, zh=["盐"]),
        partial(BiText, en=datetime.date(2026, 11, 10)),
        partial(BiText, 3, 4),
    ]
    for call in calls:
        raises(TypeError, call)


def test_f02_t06_placeholders_give_the_set_of_names() -> None:
    """``placeholders`` gives a ``frozenset`` of the names in the templates."""
    cases = [
        (UNKNOWN_RECIPE, {"recipe"}),
        (Message("No errors.", "没有错误。"), set()),
        (Message("{a} or {b}, {a}", "{b}{a}"), {"a", "b"}),
        (Message("{count_2} {a1} {x_}", "{x_}{a1}{count_2}"), {"count_2", "a1", "x_"}),
        (Message("{z9}", "{z9}"), {"z9"}),
        (Message("Language: {lang}", "语言：{lang}"), {"lang"}),
    ]
    for message, names in cases:
        assert isinstance(message.placeholders, frozenset)
        assert message.placeholders == frozenset(names)


def test_f02_t07_doubled_brace_is_not_a_placeholder() -> None:
    """A doubled brace is a brace, not part of a placeholder."""
    assert Message("Use {{ and }}.", "用 {{ 和 }}。").placeholders == frozenset()
    assert Message(BRACED + " is {name}", BRACED + "是{name}").placeholders == {"name"}
    triple = "{" * 3 + "name" + "}" * 3
    assert Message(triple, triple).placeholders == {"name"}


def test_f02_t08_template_that_is_not_a_str_is_a_wrong_call() -> None:
    """A template that is not a ``str`` raises ``TypeError``."""
    calls: list[Callable[[], object]] = [
        partial(Message, 3, "三"),
        partial(Message, "Three", 3),
        partial(Message, None, "无"),
        partial(Message, "None", None),
        partial(Message, b"Saved.", "已保存。"),
    ]
    for call in calls:
        raises(TypeError, call)


def test_f02_t09_empty_or_blank_template_is_a_wrong_call() -> None:
    """A template that is empty or only whitespace raises ``ValueError``."""
    pairs = [
        ("", "没有错误。"),
        ("No errors.", ""),
        (" ", "没有错误。"),
        ("No errors.", " "),
        ("No errors.", "\u3000"),
        ("\t\n", "没有错误。"),
        ("Saved {path}.", " "),
    ]
    for en, zh in pairs:
        raises(ValueError, partial(Message, en, zh))


def test_f02_t10_invalid_format_string_is_a_wrong_call() -> None:
    """A template that is not a valid format string raises ``ValueError``."""
    pairs = [
        ("a { b", "a b"),
        ("a b", "a { b"),
        ("a } b", "a b"),
        ("a b", "a } b"),
        ("{name", "{name}"),
        ("{name}", "{name}}"),
        ("{{name}", "{name}"),
    ]
    for en, zh in pairs:
        raises(ValueError, partial(Message, en, zh))


def test_f02_t11_placeholder_with_a_bad_name_is_a_wrong_call() -> None:
    """A placeholder name must follow rule 1 of design 2.2."""
    templates = [
        "Saved {}.",
        "Saved {0}.",
        "Saved {Name}.",
        "Saved {NAME}.",
        "Saved { name }.",
        "Saved {tag.en}.",
        "Saved {items[0]}.",
        "Saved {1a}.",
        "Saved {_a}.",
        "Saved {a-b}.",
        "Saved {名称}.",
        "Saved {é}.",
    ]
    for template in templates:
        raises(ValueError, partial(Message, template, template))
    raises(ValueError, partial(Message, "Saved {0}.", "已保存 {0}。"))


def test_f02_t12_conversion_or_format_spec_is_a_wrong_call() -> None:
    """A conversion or a format spec, even an empty one, raises ``ValueError``."""
    templates = [
        "{count!r} recipes",
        "{count!s} recipes",
        "{count!a} recipes",
        "{count:>3} recipes",
        "{count:} recipes",
        "{count:d} recipes",
        "{count!r:>3} recipes",
        "{count:{width}} recipes",
    ]
    for template in templates:
        raises(ValueError, partial(Message, template, template))
    raises(ValueError, partial(Message, "{count:>3} recipes.", "{count:>3} 个菜谱。"))
    # The standard parser reads "{count:}" as "{count}", so the names agree and it still raises.
    assert [part[1] for part in Formatter().parse("{count:}")] == ["count"]
    raises(ValueError, partial(Message, "{count} recipes.", "{count:} 个菜谱。"))


def test_f02_t13_different_names_in_the_templates_are_a_wrong_call() -> None:
    """Templates with different sets of names raise ``ValueError``."""
    pairs = [
        ("{count} recipes.", "共 {total} 个菜谱。"),
        ("{a} {b}", "{a}"),
        ("{a}", "{a} {b}"),
        ("No errors.", "{count} 个错误"),
        ("{count} errors", "错误"),
    ]
    for en, zh in pairs:
        raises(ValueError, partial(Message, en, zh))


def test_f02_t14_render_gives_the_template_with_str_values() -> None:
    """``render`` writes the template in the asked language with each ``str`` as it is."""
    cases = [
        ("tomato-eggs", 'Unknown recipe "tomato-eggs".', "未知菜谱“tomato-eggs”。"),
        ("番茄炒蛋", 'Unknown recipe "番茄炒蛋".', "未知菜谱“番茄炒蛋”。"),
        ("", 'Unknown recipe "".', "未知菜谱“”。"),
    ]
    for recipe, english, chinese in cases:
        assert UNKNOWN_RECIPE.render(EN, recipe=recipe) == english
        assert UNKNOWN_RECIPE.render(ZH, recipe=recipe) == chinese
    no_errors = Message("No errors.", "没有错误。")
    assert no_errors.render(EN) == "No errors."
    assert no_errors.render(ZH) == "没有错误。"


def test_f02_t15_int_value_has_no_thousands_separator() -> None:
    """An ``int`` goes in as its decimal digits."""
    message = Message("{count} recipes.", "共 {count} 个菜谱。")
    expected = [
        (0, "0 recipes.", "共 0 个菜谱。"),
        (7, "7 recipes.", "共 7 个菜谱。"),
        (1000, "1000 recipes.", "共 1000 个菜谱。"),
        (1234567, "1234567 recipes.", "共 1234567 个菜谱。"),
    ]
    for count, english, chinese in expected:
        assert message.render(EN, count=count) == english
        assert message.render(ZH, count=count) == chinese


def test_f02_t16_bitext_value_falls_back_to_the_other_language() -> None:
    """A ``BiText`` value goes in as its ``get(lang)``."""
    assert SERVINGS.render(EN, count=2, tags=TAGS) == "Servings: 2   Tags: quick, home-style"
    assert SERVINGS.render(ZH, count=2, tags=TAGS) == "份数：2   标签：快手、家常"
    assert NO_OTHER.render(EN, tag=BiText(zh="素")) == 'No other recipe has the tag "素".'
    assert NO_OTHER.render(ZH, tag=BiText(en="quick")) == "没有别的菜谱带有标签“quick”。"


def test_f02_t17_brace_in_a_value_is_never_a_placeholder() -> None:
    """A value goes in as it is."""
    assert UNKNOWN_RECIPE.render(EN, recipe="{x}") == 'Unknown recipe "{x}".'
    assert UNKNOWN_RECIPE.render(EN, recipe="{recipe}") == 'Unknown recipe "{recipe}".'
    message = Message("{a}{b}", "{b}{a}")
    assert message.render(EN, a="{b}", b="{{") == "{b}{{"
    assert message.render(ZH, a="{b}", b="{{") == "{{{b}"
    assert NO_OTHER.render(ZH, tag=BiText("{x}", "{y}")) == "没有别的菜谱带有标签“{y}”。"


def test_f02_t18_repeated_placeholders_and_doubled_braces() -> None:
    """Each copy of a repeated placeholder gets its value, and a doubled brace is written once."""
    repeated = Message("{a} and {a}", "{a}和{a}")
    assert repeated.render(EN, a="x") == "x and x"
    assert repeated.render(ZH, a="x") == "x和x"
    order = Message("{a} before {b}", "{b}在{a}之后")
    assert order.render(EN, a="1", b="2") == "1 before 2"
    assert order.render(ZH, a="1", b="2") == "2在1之后"
    doubled = Message("Use " + BRACED + " for {name}.", "用 " + BRACED + " 表示{name}。")
    assert doubled.render(EN, name="the recipe") == "Use {name} for the recipe."
    assert doubled.render(ZH, name="the recipe") == "用 {name} 表示the recipe。"
    triple = "{" * 3 + "name" + "}" * 3
    both = Message(triple, triple)
    assert both.render(EN, name="x") == "{x}"
    assert both.render(ZH, name="x") == "{x}"


def test_f02_t19_placeholder_named_lang_or_self() -> None:
    """A template can have a placeholder named ``lang`` or ``self``."""
    language = Message("Language: {lang}", "语言：{lang}")
    assert language.render(ZH, lang="中文") == "语言：中文"
    assert language.render(EN, lang=BiText("English", "英文")) == "Language: English"
    assert language.to_bitext(lang="中文") == BiText("Language: 中文", "语言：中文")
    me = Message("Me: {self}", "我：{self}")
    assert me.render(EN, self="Troy") == "Me: Troy"
    assert me.to_bitext(self="Troy") == BiText("Me: Troy", "我：Troy")


def test_f02_t20_to_bitext_renders_both_languages() -> None:
    """``to_bitext`` gives the message rendered in each language."""
    assert UNKNOWN_RECIPE.to_bitext(recipe="tomato-eggs") == BiText(
        'Unknown recipe "tomato-eggs".', "未知菜谱“tomato-eggs”。"
    )
    assert SERVINGS.to_bitext(count=2, tags=TAGS) == BiText(
        "Servings: 2   Tags: quick, home-style", "份数：2   标签：快手、家常"
    )
    assert NO_OTHER.to_bitext(tag=BiText(zh="素")) == BiText(
        'No other recipe has the tag "素".', "没有别的菜谱带有标签“素”。"
    )
    assert Message("No errors.", "没有错误。").to_bitext() == BiText("No errors.", "没有错误。")


def render_en(message: Message, **values: object) -> object:
    """Calls ``render`` in English.

    Args:
        message: The message.
        **values: The values, of any type, so that a wrong call can be made.

    Returns:
        The rendered text.
    """
    return message.render(EN, **values)  # type: ignore[arg-type]


def render_zh(message: Message, **values: object) -> object:
    """Calls ``render`` in Chinese.

    Args:
        message: The message.
        **values: The values, of any type, so that a wrong call can be made.

    Returns:
        The rendered text.
    """
    return message.render(ZH, **values)  # type: ignore[arg-type]


def bitext_of(message: Message, **values: object) -> object:
    """Calls ``to_bitext``.

    Args:
        message: The message.
        **values: The values, of any type, so that a wrong call can be made.

    Returns:
        The two-language text.
    """
    return message.to_bitext(**values)  # type: ignore[arg-type]


ALL_WAYS = (render_en, render_zh, bitext_of)


def test_f02_t21_values_that_are_not_the_placeholders_are_a_wrong_call() -> None:
    """Values whose names are not exactly the placeholders raise ``ValueError``."""
    no_errors = Message("No errors.", "没有错误。")
    for way in ALL_WAYS:
        raises(ValueError, partial(way, UNKNOWN_RECIPE))
        raises(ValueError, partial(way, UNKNOWN_RECIPE, recipe="rice", meal="dinner"))
        raises(ValueError, partial(way, UNKNOWN_RECIPE, meal="dinner"))
        raises(ValueError, partial(way, no_errors, count=1))


def test_f02_t22_value_of_a_wrong_type_is_a_wrong_call() -> None:
    """A value that is not a ``str``, an ``int``, or a ``BiText`` raises ``TypeError``."""
    wrong: list[object] = [
        None,
        1.5,
        Fraction(1, 2),
        Decimal("2"),
        b"rice",
        ["rice"],
        True,
        False,
        Lang.ZH,
        Lang.EN,
        MealKind.DINNER,
        Size.ONE,
        Colour.RED,
    ]
    for value in wrong:
        for way in ALL_WAYS:
            raises(TypeError, partial(way, UNKNOWN_RECIPE, recipe=value))
    raises(TypeError, partial(SERVINGS.render, EN, count=True, tags=TAGS))


def test_f02_t23_names_are_checked_before_types() -> None:
    """The names of the values are checked before their types."""
    raises(ValueError, partial(UNKNOWN_RECIPE.render, EN, recipe=None, meal="dinner"))
    raises(ValueError, partial(UNKNOWN_RECIPE.render, ZH, meal=1.5))
    raises(ValueError, partial(UNKNOWN_RECIPE.to_bitext, recipe=Lang.ZH, meal="dinner"))
    raises(ValueError, partial(Message("No errors.", "没有错误。").render, EN, count=True))


@pytest.mark.usefixtures("default_int_limit")
def test_f02_t24_int_with_4300_digits_is_the_limit() -> None:
    """An ``int`` with 4,300 digits is written in full and one with more digits is a wrong call."""
    assert sys.get_int_max_str_digits() == 4300
    message = Message("{count} recipes.", "共 {count} 个菜谱。")
    count = 10**4300 - 1
    english = "9" * 4300 + " recipes."
    chinese = "共 " + "9" * 4300 + " 个菜谱。"
    assert message.render(EN, count=count) == english
    assert message.render(ZH, count=count) == chinese
    assert message.to_bitext(count=count) == BiText(english, chinese)
    for too_many in (10**4300, 7 * 10**4300):
        for way in ALL_WAYS:
            raises(ValueError, partial(way, message, count=too_many))
