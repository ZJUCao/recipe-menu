"""Tests of F05 for read_settings: servings, unknown keys, order, and file errors (T09 to T12)."""

from pathlib import Path

import pytest

from f03_support import put_bytes, write
from f05_texts import (
    ITEM_NOT_A_TEXT,
    LANGUAGE,
    MEALS,
    NO_MEALS,
    SERVINGS,
    SERVINGS_NOT_A_NUMBER,
    Msg,
    assert_problems,
    empty_text,
    entry,
    language_not_en_or_zh,
    line_n,
    meal_n,
    not_a_list,
    not_a_text,
    servings_too_few,
    servings_too_many,
    unknown_key,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText
from recipe_menu.settings import Settings, read_settings

HEX_5000 = "0x" + "f" * 5000
FILE_MISSING: Msg = ("The file is missing.", "文件不存在。")


@pytest.mark.usefixtures("default_int_limit")
def test_f05_t09_servings_follow_the_rule_of_read_servings(folder: DataFolder) -> None:
    """Integers from 1 to 100 are read by value, and every other value is an error."""
    accepted = [("1", 1), ("100", 100), ("+7", 7), ("1_0", 10), ("0x64", 100)]
    for value, servings in accepted:
        write(folder.settings, f"servings = {value}\n")
        assert read_settings(folder) == (Settings(servings=servings), ()), value
    few = [("0", 0), ("-1", -1), ("-999999999999999", -999999999999999)]
    many = [("101", 101), ("0x65", 101), ("999999999999999", 999999999999999)]
    not_a_number = [
        "1000000000000000",
        "-1000000000000000",
        '"2"',
        "2.5",
        "2.0",
        "true",
        "false",
        "[2]",
        "{ n = 2 }",
        "2026-11-12",
        "inf",
        "nan",
        HEX_5000,
        "1" * 4300,
    ]
    for value, servings in few:
        _servings_error(folder, value, servings_too_few(servings))
    for value, servings in many:
        _servings_error(folder, value, servings_too_many(servings))
    for value in not_a_number:
        _servings_error(folder, value, SERVINGS_NOT_A_NUMBER)


def _servings_error(folder: DataFolder, value: str, message: Msg) -> None:
    """Checks that ``servings = value`` gives no settings and one problem at servings."""
    write(folder.settings, f"servings = {value}\n")
    settings, problems = read_settings(folder)
    assert settings is None, value[:30]
    assert_problems(problems, [entry(SERVINGS, message)])


def test_f05_t10_unknown_keys_are_errors_with_no_place(folder: DataFolder) -> None:
    """A key that is not language, meals, or servings stops the file, in the file's order."""
    cases = [
        ('language = "zh"\ncolour = "red"\n', ["colour"]),
        ('Language = "en"\n', ["Language"]),
        ("b = 1\na = 2\n", ["b", "a"]),
        ("servings = 2\n[menu]\ndays = 7\n", ["menu"]),
    ]
    for text, keys in cases:
        write(folder.settings, text)
        settings, problems = read_settings(folder)
        assert settings is None, text
        assert_problems(problems, [entry(None, unknown_key(key)) for key in keys])


def test_f05_t11_problems_come_in_the_order_of_the_checks(folder: DataFolder) -> None:
    """Language, then meals, then servings, then the unknown keys in the file's order."""
    lines = [
        'language = "fr"',
        'meals = ["lunch", 3]',
        f"servings = {HEX_5000}",
        "colour = 1",
    ]
    write(folder.settings, "\n".join(lines) + "\n")
    settings, problems = read_settings(folder)
    assert settings is None
    assert_problems(
        problems,
        [
            entry(LANGUAGE, language_not_en_or_zh("fr")),
            entry(meal_n(2), ITEM_NOT_A_TEXT),
            entry(SERVINGS, SERVINGS_NOT_A_NUMBER),
            entry(None, unknown_key("colour")),
        ],
    )
    lines = ["zebra = 1", "servings = 0", 'meals = "lunch"', "alpha = 2", "language = 3"]
    write(folder.settings, "\n".join(lines) + "\n")
    settings, problems = read_settings(folder)
    assert settings is None
    assert_problems(
        problems,
        [
            entry(LANGUAGE, not_a_text("language")),
            entry(MEALS, not_a_list("meals")),
            entry(SERVINGS, servings_too_few(0)),
            entry(None, unknown_key("zebra")),
            entry(None, unknown_key("alpha")),
        ],
    )
    write(folder.settings, 'meals = []\nlanguage = ""\n')
    settings, problems = read_settings(folder)
    assert settings is None
    assert_problems(problems, [entry(LANGUAGE, empty_text("language")), entry(MEALS, NO_MEALS)])


def _only_problem(folder: DataFolder, place: BiText | None, message: Msg) -> None:
    """Checks that the folder gives no settings and the one problem of ``read_toml``."""
    settings, problems = read_settings(folder)
    assert settings is None
    assert_problems(problems, [entry(place, message)])


@pytest.mark.usefixtures("default_int_limit")
def test_f05_t12_a_problem_of_read_toml_is_the_only_problem(
    folder: DataFolder, tmp_path: Path
) -> None:
    """A file that cannot be read gives that one problem, whatever its earlier lines hold."""
    _only_problem(folder, None, FILE_MISSING)
    _only_problem(DataFolder(tmp_path / "nowhere"), None, FILE_MISSING)
    folder.settings.mkdir()
    is_folder = ("The file cannot be read: it is a folder.", "无法读取文件：它是一个文件夹。")
    _only_problem(folder, None, is_folder)
    folder.settings.rmdir()
    gbk = '# 设置\nlanguage = "zh"\n'.encode("gbk")
    not_utf8 = (
        "The file cannot be read: it is not UTF-8 text. Save it as UTF-8.",
        "无法读取文件：它不是 UTF-8 文本。请把它另存为 UTF-8。",
    )
    put_bytes(folder.settings, gbk)
    _only_problem(folder, line_n(1), not_utf8)
    bracket = (
        'The file cannot be read: a closing "]" is missing.',
        "无法读取文件：缺少右方括号“]”。",
    )
    write(folder.settings, 'language = "fr"\nmeals = ["lunch" "dinner"]\n')
    _only_problem(folder, line_n(2), bracket)
    extra = (
        "The file cannot be read: something follows the value on this line. "
        "Write one key and its value on each line.",
        "无法读取文件：这一行的值后面还有别的内容。每行只写一个键和它的值。",
    )
    write(folder.settings, 'language = "zh"\nservings = 2 份\n')
    _only_problem(folder, line_n(2), extra)
    twice = (
        "The file cannot be read: a key or a table is defined twice.",
        "无法读取文件：同一个键或表定义了两次。",
    )
    write(folder.settings, 'language = "zh"\nlanguage = "zh"\n')
    _only_problem(folder, line_n(2), twice)
    too_long = (
        "The file cannot be read: a number has too many digits.",
        "无法读取文件：有一个数字的位数太多。",
    )
    write(folder.settings, "servings = " + "1" * 4301 + "\n")
    _only_problem(folder, line_n(1), too_long)
