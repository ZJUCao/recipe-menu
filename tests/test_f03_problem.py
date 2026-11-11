"""Tests of F03 for Problem and the messages of the shape of a file (F03-T05 to F03-T11)."""

from pathlib import Path

import pytest

from recipe_menu.datafile import (
    EMPTY_ITEM,
    EMPTY_TEXT,
    ITEM_NOT_A_TEXT,
    MISSING_KEY,
    NOT_A_LIST,
    NOT_A_TABLE,
    NOT_A_TEXT,
    UNKNOWN_KEY,
    Problem,
    Severity,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, and_list

EN, ZH = Lang.EN, Lang.ZH

UNKNOWN_TAG = Message('Unknown tag "{tag}".', "未知标签“{tag}”。")
NO_ENGLISH_STEPS = Message("No English steps.", "没有英文步骤。")
rice = Path("recipes", "rice.toml")
tags = BiText("tags", "标签")
CATALOG = Path("catalog.toml")


def test_f03_t05_error_and_warning_keep_their_parts_and_text_renders() -> None:
    """The factories set the severity, and ``text`` renders each language."""
    p = Problem.error(rice, tags, UNKNOWN_TAG, tag="breakfast")
    q = Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG, (("tag", "breakfast"),))
    w = Problem.warning(rice, BiText("steps", "步骤"), NO_ENGLISH_STEPS)
    n = Problem.error(CATALOG, None, NO_ENGLISH_STEPS)
    assert p.severity is Severity.ERROR
    assert p.file == rice
    assert p.place == tags
    assert p.message is UNKNOWN_TAG
    assert p.values == (("tag", "breakfast"),)
    assert p.text(EN) == 'Unknown tag "breakfast".'
    assert p.text(ZH) == "未知标签“breakfast”。"
    assert p == q
    assert hash(p) == hash(q)
    assert len({p, q}) == 1
    assert w.severity is Severity.WARNING
    assert w.values == ()
    assert w.text(EN) == "No English steps."
    assert n.place is None
    assert n.text(ZH) == "没有英文步骤。"
    assert Problem.warning(rice, tags, UNKNOWN_TAG, tag="breakfast") != p


def test_f03_t06_values_are_sorted_by_name() -> None:
    """The order of the values does not matter."""
    order = Message("{b} then {a}", "先 {b} 后 {a}")
    problems = [
        Problem.error(rice, None, order, b="2", a="1"),
        Problem.error(rice, None, order, a="1", b="2"),
        Problem(Severity.ERROR, rice, None, order, (("b", "2"), ("a", "1"))),
    ]
    for problem in problems:
        assert problem.values == (("a", "1"), ("b", "2"))
        assert problem.text(EN) == "2 then 1"
        assert problem.text(ZH) == "先 2 后 1"
    assert problems[0] == problems[1] == problems[2]


def test_f03_t07_a_placeholder_may_be_named_file_place_or_message() -> None:
    """The first three parameters are positional only."""
    names = Message("{file}, {place}, {message}", "{file}，{place}，{message}")
    problems = [
        Problem.error(rice, None, names, file="a", place="b", message="c"),
        Problem.warning(rice, None, names, file="a", place="b", message="c"),
    ]
    for problem in problems:
        assert problem.text(EN) == "a, b, c"
        assert problem.text(ZH) == "a，b，c"
        assert problem.values == (("file", "a"), ("message", "c"), ("place", "b"))
        assert problem.file == rice


def test_f03_t08_wrong_files_and_wrong_values_are_wrong_calls(tmp_path: Path) -> None:
    """An absolute file, a missing value, an extra value, and a repeated name raise."""
    absolute = tmp_path / "rice.toml"
    calls = [
        lambda: Problem.error(absolute, None, NO_ENGLISH_STEPS),
        lambda: Problem.warning(absolute, None, NO_ENGLISH_STEPS),
        lambda: Problem(Severity.ERROR, absolute, None, NO_ENGLISH_STEPS),
        lambda: Problem.error(rice, tags, UNKNOWN_TAG),
        lambda: Problem.error(rice, tags, UNKNOWN_TAG, tag="breakfast", meal="dinner"),
        lambda: Problem.error(rice, None, NO_ENGLISH_STEPS, tag="x"),
        lambda: Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG),
        lambda: Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG, (("tag", "a"), ("tag", "b"))),
    ]
    for call in calls:
        with pytest.raises(ValueError):
            call()


def test_f03_t09_a_value_must_be_text_a_short_int_or_bitext(default_int_limit: None) -> None:
    """A wrong value fails at once, and an int has at most 4,300 digits."""
    for v in [None, 1.5, b"breakfast", ["breakfast"], True, Lang.ZH, Severity.ERROR]:
        with pytest.raises(TypeError):
            Problem.error(rice, tags, UNKNOWN_TAG, tag=v)
        with pytest.raises(TypeError):
            Problem.warning(rice, tags, UNKNOWN_TAG, tag=v)
        with pytest.raises(TypeError):
            Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG, (("tag", v),))
    count = Message("{count} recipes.", "共 {count} 个菜谱。")
    with pytest.raises(ValueError):
        Problem.error(rice, None, count, count=10**4300)
    long = Problem.error(rice, None, count, count=10**4300 - 1)
    assert long.text(EN) == "9" * 4300 + " recipes."
    seven = Problem.error(rice, None, count, count=7)
    assert seven.text(EN) == "7 recipes."
    assert seven.text(ZH) == "共 7 个菜谱。"


def test_f03_t10_the_messages_of_the_shape_of_a_file_have_the_texts_of_the_design() -> None:
    """Each message of 2.10 renders its English and its Chinese text."""
    calls = [
        (MISSING_KEY, {"key": "tags"}),
        (NOT_A_LIST, {"key": "categories"}),
        (NOT_A_TEXT, {"key": "unit"}),
        (EMPTY_TEXT, {"key": "en"}),
        (NOT_A_TABLE, {}),
        (ITEM_NOT_A_TEXT, {}),
        (EMPTY_ITEM, {}),
        (UNKNOWN_KEY.pick(1), {"key": "items", "keys": and_list(["pantry"])}),
        (UNKNOWN_KEY.pick(2), {"key": "colour", "keys": and_list(["zh", "en"])}),
        (
            UNKNOWN_KEY.pick(4),
            {"key": "units", "keys": and_list(["zh", "en", "category", "unit"])},
        ),
    ]
    expected = [
        ('The key "tags" is missing.', "缺少键“tags”。"),
        (
            '"categories" must be a list in square brackets, [ ... ].',
            "“categories”必须是放在方括号 [ ... ] 里的列表。",
        ),
        ('"unit" must be a text in quotation marks.', "“unit”必须是放在引号里的文字。"),
        ('"en" is empty.', "“en”是空的。"),
        (
            "This item must be a table in braces, { ... }.",
            "这一项必须是放在花括号 { ... } 里的表。",
        ),
        ("This item must be a text in quotation marks.", "这一项必须是放在引号里的文字。"),
        ("This item is empty.", "这一项是空的。"),
        ('Unknown key "items". The only key is pantry.', "未知键“items”。可用的键：pantry。"),
        ('Unknown key "colour". The keys are zh and en.', "未知键“colour”。可用的键：zh 和 en。"),
        (
            'Unknown key "units". The keys are zh, en, category, and unit.',
            "未知键“units”。可用的键：zh、en、category 和 unit。",
        ),
    ]
    for (message, values), texts in zip(calls, expected, strict=True):
        problem = Problem.error(CATALOG, None, message, **values)
        assert (problem.text(EN), problem.text(ZH)) == texts


def test_f03_t11_each_message_takes_exactly_its_placeholders() -> None:
    """A missing, an extra, or a wrongly named value raises."""
    for message in (NOT_A_TABLE, ITEM_NOT_A_TEXT, EMPTY_ITEM):
        with pytest.raises(ValueError):
            Problem.error(CATALOG, None, message, key="x")
    for message in (MISSING_KEY, NOT_A_LIST, NOT_A_TEXT, EMPTY_TEXT):
        with pytest.raises(ValueError):
            Problem.error(CATALOG, None, message)
    with pytest.raises(ValueError):
        Problem.error(CATALOG, None, UNKNOWN_KEY.pick(1), key="x")
    with pytest.raises(ValueError):
        Problem.error(CATALOG, None, UNKNOWN_KEY.pick(2), key="x", keys="zh", extra="y")
