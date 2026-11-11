"""Helpers and example values that the F02 tests share."""

from collections.abc import Callable
from enum import Enum, IntEnum, StrEnum

import pytest

from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural

EN, ZH = Lang.EN, Lang.ZH

BRACED = "{" * 2 + "name" + "}" * 2


class MealKind(StrEnum):
    """A ``StrEnum`` that stands for the ``Meal`` of the architecture."""

    DINNER = "dinner"


class Size(IntEnum):
    """An ``IntEnum`` with the value 1."""

    ONE = 1


class Colour(Enum):
    """An ``Enum`` with a ``str`` value."""

    RED = "red"


UNKNOWN_RECIPE = Message('Unknown recipe "{recipe}".', "未知菜谱“{recipe}”。")
SERVINGS = Message("Servings: {count}   Tags: {tags}", "份数：{count}   标签：{tags}")
TAGS = BiText("quick, home-style", "快手、家常")
NO_OTHER = Message('No other recipe has the tag "{tag}".', "没有别的菜谱带有标签“{tag}”。")
WITH_TAG = Plural(
    Message('{count} recipe has the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
    Message('{count} recipes have the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
)
QUICK = BiText("quick", "快手")
ONE_ERROR = Message("{count} error", "{count} 个错误")
MEALS = [BiText("breakfast", "早餐"), BiText("lunch", "午餐"), BiText("dinner", "晚餐")]
QUOTED = Message('"{word}"', "“{word}”")
SETTINGS = Message("the settings", "设置")
CATALOG = Message("the catalog", "目录")
PANTRY = Message("the pantry", "常备清单")
RECIPES = Plural(
    Message("{count} recipe", "{count} 个菜谱"),
    Message("{count} recipes", "{count} 个菜谱"),
)
WEEK_MENUS = Plural(
    Message("{count} week menu", "{count} 个周菜单"),
    Message("{count} week menus", "{count} 个周菜单"),
)
CHECKED = Message("Checked {files}.", "已检查{files}。")


def raises(error: type[Exception], call: Callable[[], object]) -> None:
    """Asserts that a call raises an error of the given type.

    Args:
        error: The type that the call must raise.
        call: A call with no arguments.
    """
    try:
        call()
    except error:
        return
    pytest.fail(f"{call!r} did not raise {error.__name__}")
