"""Tests of F02 for Plural, render_counted, and the shared messages (F02-T25 to F02-T28)."""

from functools import partial

from f02_support import EN, ONE_ERROR, QUICK, WITH_TAG, ZH, raises
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import (
    RUN_CHECK,
    RUN_HELP_FOR_COMMANDS,
    RUN_HELP_FOR_OPTIONS,
    Message,
    Plural,
)


def test_f02_t25_pick_gives_one_for_a_count_of_1() -> None:
    """``pick`` gives ``one`` for 1 and ``other`` for every other count."""
    for count in (1, 0, 2, 3, 7, 11, 21, 101, -1, 10**20):
        expected = WITH_TAG.one if count == 1 else WITH_TAG.other
        assert WITH_TAG.pick(count) is expected
    first = Message("{count} {tag}", "{count}{tag}")
    second = Message("{tag} {count} {count}", "{tag}{count}")
    plural = Plural(first, second)
    assert plural.pick(1) is first
    assert plural.pick(2) is second
    same = Message("No errors.", "没有错误。")
    both = Plural(same, same)
    assert both.pick(1) is same
    assert both.pick(5) is same


def test_f02_t26_plural_with_different_names_is_a_wrong_call() -> None:
    """Two messages with different placeholder names raise ``ValueError``."""
    raises(ValueError, partial(Plural, ONE_ERROR, Message("errors", "错误")))
    raises(
        ValueError,
        partial(
            Plural,
            Message("{count} recipe", "{count} 个菜谱"),
            Message("{count} recipes with {tag}", "{count} 个带{tag}的菜谱"),
        ),
    )
    raises(
        ValueError,
        partial(
            Plural,
            Message("one recipe", "一个菜谱"),
            Message("{count} recipes", "{count} 个菜谱"),
        ),
    )


def render_counted(plural: Plural, count: int, lang: Lang, **values: str | BiText) -> str:
    """Picks a message by its count and renders it with that count.

    Args:
        plural: The plural.
        count: The count.
        lang: The language.
        **values: The other values.

    Returns:
        The rendered line.
    """
    return plural.pick(count).render(lang, count=count, **values)


def test_f02_t27_lines_with_a_count_of_the_prototypes() -> None:
    """Lines with a count in the F05, F07, and F09 prototypes and in v0.1-S20."""
    vegetarian = BiText("vegetarian", "素")
    assert render_counted(WITH_TAG, 3, EN, tag=QUICK) == '3 recipes have the tag "quick".'
    assert render_counted(WITH_TAG, 3, ZH, tag=QUICK) == "共 3 个菜谱带有标签“快手”。"
    assert render_counted(WITH_TAG, 1, EN, tag=QUICK) == '1 recipe has the tag "quick".'
    assert render_counted(WITH_TAG, 1, EN, tag=vegetarian) == '1 recipe has the tag "vegetarian".'
    assert render_counted(WITH_TAG, 1, ZH, tag=vegetarian) == "共 1 个菜谱带有标签“素”。"
    recipes_line = Plural(
        Message("{count} recipe.", "共 {count} 个菜谱。"),
        Message("{count} recipes.", "共 {count} 个菜谱。"),
    )
    assert render_counted(recipes_line, 7, EN) == "7 recipes."
    assert render_counted(recipes_line, 7, ZH) == "共 7 个菜谱。"
    assert render_counted(recipes_line, 1, EN) == "1 recipe."
    errors = Plural(
        Message("{count} error:", "{count} 个错误："),
        Message("{count} errors:", "{count} 个错误："),
    )
    assert render_counted(errors, 2, EN) == "2 errors:"
    assert render_counted(errors, 2, ZH) == "2 个错误："
    assert render_counted(errors, 1, EN) == "1 error:"
    warnings = Plural(
        Message("{count} warning:", "{count} 个警告："),
        Message("{count} warnings:", "{count} 个警告："),
    )
    assert render_counted(warnings, 1, EN) == "1 warning:"
    assert render_counted(warnings, 1, ZH) == "1 个警告："


def test_f02_t28_shared_messages_have_the_texts_of_the_design() -> None:
    """The three shared messages have no placeholders and the texts of design 2.5."""
    cases = [
        (
            RUN_CHECK,
            'Run "recipe-menu check" to see every problem.',
            "运行“recipe-menu check”查看所有问题。",
        ),
        (
            RUN_HELP_FOR_OPTIONS,
            'Run "recipe-menu --help" to see the options.',
            "运行“recipe-menu --help”查看选项。",
        ),
        (
            RUN_HELP_FOR_COMMANDS,
            'Run "recipe-menu --help" to see the commands.',
            "运行“recipe-menu --help”查看命令。",
        ),
    ]
    for message, english, chinese in cases:
        assert message.placeholders == frozenset()
        assert message.render(EN) == english
        assert message.render(ZH) == chinese
