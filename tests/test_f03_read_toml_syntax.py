"""Tests of F03 for the reasons that read_toml gives for TOML mistakes (F03-T21 to F03-T35)."""

from collections.abc import Sequence
from pathlib import Path

from f03_support import (
    M_BAD_ESCAPE,
    M_BAD_KEY,
    M_BAD_LINE,
    M_BAD_VALUE,
    M_CONTROL_CHARACTER,
    M_DEFINED_TWICE,
    M_EXTRA_TEXT,
    M_MISSING_BRACE,
    M_MISSING_BRACKET,
    M_MISSING_EQUALS,
    M_MISSING_QUOTE,
    M_NESTED_TOO_DEEPLY,
    M_NOT_TOML,
    M_NUMBER_TOO_LONG,
    SETTINGS_FILE,
    Msg,
    at_line,
    check_toml,
    write,
)
from recipe_menu.datafile import DataFolder, read_toml


def check_lines(folder: DataFolder, cases: Sequence[tuple[str, int]], msg: Msg) -> None:
    """Writes each text to ``settings.toml`` and checks the one problem, at the given line."""
    for text, line in cases:
        write(folder.settings, text)
        check_toml(read_toml(folder, folder.settings), SETTINGS_FILE, at_line(line), msg)


def test_f03_t21_the_three_reasons_of_missing_bracket(folder: DataFolder) -> None:
    """An unclosed list, a header with no ``]``, and a header with no ``]]``."""
    files = [
        (folder.pantry, '# The pantry.\npantry = ["盐" "糖"]\n', Path("pantry.toml")),
        (
            folder.menu_file("2026-W47"),
            'week = "2026-W47"\n[monday\nlunch = []\n',
            Path("menus", "2026-W47.toml"),
        ),
        (
            folder.recipe_file("tomato-egg"),
            'servings = 2\n[[ingredients]\nitem = "番茄"\n',
            Path("recipes", "tomato-egg.toml"),
        ),
    ]
    for path, text, relative in files:
        write(path, text)
        check_toml(read_toml(folder, path), relative, at_line(2), M_MISSING_BRACKET)


def test_f03_t22_an_unclosed_inline_table_gives_missing_brace(folder: DataFolder) -> None:
    """No comma between two keys, and a table whose line ends before its ``}``."""
    cases = [
        ('# Tomato\nname = { zh = "番茄" en = "Tomato" }\n', 2),
        ('# Tomato\nname = { zh = "番茄", en = "Tomato"\n}\n', 2),
    ]
    check_lines(folder, cases, M_MISSING_BRACE)


def test_f03_t23_the_five_reasons_of_missing_quote(folder: DataFolder) -> None:
    """Each kind of unterminated string gives ``MISSING_QUOTE``."""
    cases = [
        ('servings = 2\nzh = "番茄\n', 2),
        ('servings = 2\nzh = "番茄', 2),
        ("servings = 2\nzh = '番茄\nen = 'Tomato'\n", 2),
        ("servings = 2\nzh = '番茄", 2),
        ("servings = 2\nzh = '''番茄\n", 3),
    ]
    check_lines(folder, cases, M_MISSING_QUOTE)


def test_f03_t24_a_value_that_is_missing_or_not_valid_gives_bad_value(folder: DataFolder) -> None:
    """A text with no quotation marks, with Chinese ones, or no value at all."""
    cases = [
        ("servings = 2\nzh = 番茄\n", 2),
        ("servings = 2\nzh = \u201c番茄\u201d\n", 2),
        ("servings = 2\nzh =\n", 2),
    ]
    check_lines(folder, cases, M_BAD_VALUE)


def test_f03_t25_a_key_with_no_equals_sign_gives_missing_equals(folder: DataFolder) -> None:
    """A key followed by a text, or by a colon."""
    cases = [('servings = 2\nzh "番茄"\n', 2), ('servings = 2\nzh: "番茄"\n', 2)]
    check_lines(folder, cases, M_MISSING_EQUALS)


def test_f03_t26_a_key_that_is_missing_or_not_valid_gives_bad_key(folder: DataFolder) -> None:
    """A trailing comma, a break after a comma, and a Chinese key with no quotation marks."""
    cases = [
        ('servings = 2\nname = { zh = "番茄", }\n', 2),
        ('servings = 2\nname = { zh = "番茄",\n  en = "Tomato" }\n', 2),
        ('servings = 2\nname = { 中文 = "番茄" }\n', 2),
    ]
    check_lines(folder, cases, M_BAD_KEY)


def test_f03_t27_text_after_a_value_gives_extra_text(folder: DataFolder) -> None:
    """A unit after a number, and two keys on one line."""
    cases = [
        ('language = "zh"\nservings = 2 份\n', 2),
        ('language = "zh"\nzh = "番茄" en = "Tomato"\n', 2),
    ]
    check_lines(folder, cases, M_EXTRA_TEXT)


def test_f03_t28_a_line_with_no_key_gives_bad_line(folder: DataFolder) -> None:
    """A line of Chinese text, and a line that starts with a Chinese quotation mark."""
    cases = [
        ("servings = 2\n番茄\n", 2),
        ('servings = 2\n\u201czh\u201d = "番茄"\n', 2),
    ]
    check_lines(folder, cases, M_BAD_LINE)


def test_f03_t29_the_five_kinds_of_reasons_of_defined_twice(folder: DataFolder) -> None:
    """A key or a table defined twice, in five ways."""
    cases = [
        ("servings = 2\nservings = 3\n", 2),
        ("[monday]\nlunch = []\n[monday]\ndinner = []\n", 3),
        ('# Scallion\nname = { zh = "葱", zh = "大葱" }\n', 2),
        ('name = { zh = "葱" }\nname.en = "Scallion"\n', 2),
        ("[monday.lunch]\n[monday]\nlunch.x = 1\n", 3),
    ]
    check_lines(folder, cases, M_DEFINED_TWICE)


def test_f03_t30_the_three_reasons_of_bad_escape(folder: DataFolder) -> None:
    """A backslash that starts no escape, no hex digits, and a surrogate."""
    cases = [
        ('language = "zh"\neditor = "C:\\Program Files\\notepad.exe"\n', 2),
        ('language = "zh"\neditor = "C:\\users"\n', 2),
        ('language = "zh"\nx = "\\uD800"\n', 2),
    ]
    check_lines(folder, cases, M_BAD_ESCAPE)


def test_f03_t31_a_control_character_gives_control_character(folder: DataFolder) -> None:
    """NUL, a lone CR, SOH, and DEL, in a text or in a comment."""
    cases = [
        ('servings = 2\nzh = "a\x00b"\n', 2),
        ("servings = 2\n# note \x00\n", 2),
        ("servings = 2\n# note \r more\n", 2),
        ('servings = 2\nzh = "a\rb"\n', 2),
        ("servings = 2\nzh = 'a\x01b'\n", 2),
        ('servings = 2\nzh = "a\x7fb"\n', 2),
    ]
    check_lines(folder, cases, M_CONTROL_CHARACTER)


def test_f03_t32_a_reason_that_the_table_does_not_list_gives_not_toml(folder: DataFolder) -> None:
    """A date that does not exist gives ``NOT_TOML`` with its line."""
    cases = [
        ('language = "zh"\nday = 2026-11-31\n', 2),
        ('language = "zh"\nday = 2026-02-29\n', 2),
    ]
    check_lines(folder, cases, M_NOT_TOML)


def test_f03_t33_a_mistake_at_the_end_is_on_the_line_after_the_last_lf(folder: DataFolder) -> None:
    """The end of the document is on one more line than the LF characters of the text."""
    cases = [
        ('servings = 2\npantry = ["盐"', 2, M_MISSING_BRACKET),
        ('servings = 2\npantry = ["盐"\n', 3, M_MISSING_BRACKET),
        ('servings = 2\npantry = ["盐",', 2, M_BAD_VALUE),
        ('note = "a\u2028b"\nzh = "番茄', 2, M_MISSING_QUOTE),
    ]
    for text, line, msg in cases:
        check_lines(folder, [(text, line)], msg)


def test_f03_t34_a_number_with_too_many_digits_gives_number_too_long(
    folder: DataFolder, default_int_limit: None
) -> None:
    """More than 4,300 decimal digits is a mistake, and 4,300 digits or a hex integer is not."""
    cases = [
        ('language = "en"\nservings = ' + "1" * 5000 + "\n", 2),
        ("servings = " + "1" * 5000 + "\n", 1),
        ('language = "en"\nmeals = [\n  ' + "1" * 5000 + ",\n]\nservings = 2\n", 3),
        ('language = "en"\nservings = -' + "1" * 4301 + "\n", 2),
    ]
    check_lines(folder, cases, M_NUMBER_TOO_LONG)
    write(folder.settings, "servings = " + "1" * 4300 + "\n")
    assert read_toml(folder, folder.settings) == {"servings": int("1" * 4300)}
    write(folder.settings, "servings = 0x" + "f" * 5000 + "\n")
    assert read_toml(folder, folder.settings) == {"servings": int("f" * 5000, 16)}


def test_f03_t35_nesting_that_is_too_deep_gives_nested_too_deeply(folder: DataFolder) -> None:
    """Lists and tables nested 1,000 deep give the line where the nesting starts."""
    cases = [
        ("servings = 2\nx = " + "[" * 1000 + "]" * 1000 + "\n", 2),
        ("servings = 2\nx = " + "{ a = " * 1000 + "1" + " }" * 1000 + "\n", 2),
        ("servings = 2\nx = " + "[{ a = " * 500 + "1" + " }]" * 500 + "\n", 2),
        ("x = " + "[" * 1000 + "\n" + "]" * 1000 + "\n", 1),
    ]
    check_lines(folder, cases, M_NESTED_TOO_DEEPLY)
