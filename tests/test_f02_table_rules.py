"""Tests of F02 for display_width and the rules of format_table (F02-T43 to F02-T56)."""

from collections.abc import Callable
from functools import partial

from f02_support import raises
from recipe_menu.text import display_width, format_table


def check_widths(cases: list[tuple[str, int]]) -> None:
    """Asserts the display width of each text.

    Args:
        cases: Pairs of a text and its width.
    """
    for text, width in cases:
        assert display_width(text) == width, text


def test_f02_t43_ordinary_characters_take_1_column() -> None:
    """A character that is neither wide, fullwidth, nor a combining mark takes 1 column."""
    check_widths(
        [
            ("Tomato", 6),
            ("", 0),
            ("a b", 3),
            ("recipes\\tomato-egg.toml", 23),
            ("\uff71", 1),
            ("\N{LATIN SMALL LETTER E WITH ACUTE}", 1),
            ("\xa0", 1),
            ("\t", 1),
            ("a\nb", 3),
            ("\udcff", 1),
        ]
    )


def test_f02_t44_wide_and_fullwidth_characters_take_2_columns() -> None:
    """A character whose East Asian width is W or F takes 2 columns."""
    check_widths(
        [
            ("番茄鸡蛋面", 10),
            ("周一 11月16日", 13),
            ("，、：", 6),
            ("\uff21", 2),
            ("\uff11", 2),
            ("\u3000", 2),
            ("\u3042", 2),
            ("\uac00", 2),
            ("\U0001f600", 2),
            ("\U00020000", 2),
        ]
    )


def test_f02_t45_ambiguous_characters_and_spacing_marks_take_1_column() -> None:
    """An ambiguous character and a spacing mark of category Mc take 1 column."""
    check_widths(
        [
            ("—×“”", 4),
            ("\u2460", 1),
            ("\xb0", 1),
            ("\u2026", 1),
            ("\u0915\u093e", 2),
            ("\u0915\u0903", 2),
        ]
    )


def test_f02_t46_combining_marks_take_0_columns() -> None:
    """A mark of category Mn or Me takes 0 columns, even one whose East Asian width is W."""
    check_widths(
        [
            ("e\N{COMBINING ACUTE ACCENT}", 1),
            ("\u0301", 0),
            ("a\u20dd", 1),
            ("\u0488", 0),
            ("\u3099", 0),
            ("\u302a", 0),
            ("\u304b\u3099", 2),
            ("番\u0301", 2),
        ]
    )


def test_f02_t47_columns_are_padded_and_followed_by_a_gap() -> None:
    """Each column but the last is padded to its widest cell and followed by 3 spaces."""
    result = format_table([("a", "bb", "c"), ("ccc", "d", "eeee")])
    assert result == ("a     bb   c", "ccc   d    eeee")
    assert isinstance(result, tuple)


def test_f02_t48_columns_are_aligned_by_display_width() -> None:
    """Columns are aligned by ``display_width``, not by the number of characters."""
    assert format_table([("番茄", "x"), ("a", "y"), ("e\u0301", "z")]) == (
        "番茄   x",
        "a      y",
        "e\u0301      z",
    )
    assert format_table([("—", "x"), ("ab", "y")]) == ("—    x", "ab   y")
    assert format_table([("，、", "x"), ("Tomato", "y")]) == ("，、     x", "Tomato   y")


def test_f02_t49_indent_and_gap() -> None:
    """``indent`` puts spaces before each line, and ``gap`` sets the spaces between two columns."""
    rows = [("a", "b"), ("cc", "d")]
    assert format_table(rows, indent=2) == ("  a    b", "  cc   d")
    assert format_table(rows, gap=1) == ("a  b", "cc d")
    assert format_table(rows, gap=4) == ("a     b", "cc    d")
    assert format_table(rows, indent=4, gap=2) == ("    a   b", "    cc  d")


def test_f02_t50_min_widths_widen_a_column() -> None:
    """An item of ``min_widths`` widens its column when it is larger than the widest cell."""
    rows = [("a", "b", "c"), ("dd", "e", "f")]
    wide = ("a      b   c", "dd     e   f")
    assert format_table(rows, min_widths=(4,)) == wide
    assert format_table(rows, min_widths=[4]) == wide
    narrow = ("a    b   c", "dd   e   f")
    assert format_table(rows, min_widths=(1,)) == narrow
    assert format_table(rows, min_widths=(0, 0, 10)) == narrow
    assert format_table(rows, min_widths=()) == narrow
    assert format_table(rows, min_widths=(0, 3)) == ("a    b     c", "dd   e     f")
    assert format_table([("a",)], min_widths=(10,)) == ("a",)


def test_f02_t51_a_row_takes_as_many_lines_as_its_longest_cell() -> None:
    """A cell with fewer lines is empty in the later lines, and a width counts every line."""
    first = format_table([("a", "x\ny\nz", "1"), ("bb", "w", "2\n3")])
    assert first == ("a    x   1", "     y", "     z", "bb   w   2", "         3")
    second = format_table([("番茄\nabcdefgh", "x"), ("a", "y")])
    assert second == ("番茄       x", "abcdefgh", "a          y")


def test_f02_t52_lines_of_a_cell_are_those_of_splitlines() -> None:
    """A cell's lines are those of ``str.splitlines``, or one empty line when that gives none."""
    breaks = [
        "a\nb",
        "a\r\nb",
        "a\rb",
        "a\vb",
        "a\fb",
        "a\x1cb",
        "a\x85b",
        "a\u2028b",
        "a\u2029b",
    ]
    for text in breaks:
        assert format_table([(text,)]) == ("a", "b"), repr(text)
    assert format_table([("a\n",)]) == ("a",)
    assert format_table([("\n",)]) == ("",)
    assert format_table([("a\n\nb",)]) == ("a", "", "b")
    assert format_table([("",)]) == ("",)
    assert format_table([("a\r\nb", "x"), ("c", "y")]) == ("a   x", "b", "c   y")


def test_f02_t53_trailing_spaces_are_removed() -> None:
    """Spaces at the end of each line are removed and no other character is."""
    assert format_table([("a", "b", ""), ("cc", "", "")]) == ("a    b", "cc")
    assert format_table([("", ""), ("", "")]) == ("", "")
    assert format_table([("", ""), ("a", "")], indent=2) == ("", "  a")
    assert format_table([("a", "b  ")]) == ("a   b",)
    assert format_table([("a", "b\t"), ("a", "b\u3000")]) == (
        "a   b\t",
        "a   b\u3000",
    )
    assert format_table([("a", "", "c"), ("b", "", "d")]) == ("a      c", "b      d")


def test_f02_t54_no_rows_and_no_cutting() -> None:
    """No rows give the empty tuple, rows keep their order, and a cell is never cut."""
    assert format_table([]) == ()
    assert format_table(()) == ()
    assert format_table([], indent=2, gap=4, min_widths=(16,)) == ()
    assert format_table([], min_widths=(1, 2, 3)) == ()
    assert format_table([("z",), ("a",), ("m",)]) == ("z", "a", "m")
    assert format_table([("x" * 300, "y"), ("a", "b")]) == (
        "x" * 300 + "   y",
        "a" + " " * 302 + "b",
    )
    assert format_table([("番" * 100,)]) == ("番" * 100,)
    assert format_table([["a", "b"], ["cc", "d"]]) == ("a    b", "cc   d")


def test_f02_t55_a_str_as_rows_or_as_a_row_is_a_wrong_call() -> None:
    """A ``str`` as ``rows`` or as a row raises ``TypeError``, before every other error."""
    calls: list[Callable[[], object]] = [
        partial(format_table, "ab"),
        partial(format_table, ""),
        partial(format_table, ["ab", "cd"]),
        partial(format_table, [("a", "b"), "cd"]),
        partial(format_table, ("ab",)),
        partial(format_table, ["ab", ("c",)]),
        partial(format_table, "ab", gap=0),
        partial(format_table, ["ab"], indent=-1),
        partial(format_table, ["abc"], min_widths=(1, 1, 1, 1)),
    ]
    for call in calls:
        raises(TypeError, call)


def test_f02_t56_bad_shapes_and_bad_numbers_are_a_wrong_call() -> None:
    """Uneven rows, empty rows, and bad numbers raise ``ValueError``."""
    uneven = [[("a", "b"), ("c",)], [("a",), ("b", "c")], [()], [(), ()]]
    for rows in uneven:
        raises(ValueError, partial(format_table, rows))
    for rows in ([("a", "b")], []):
        raises(ValueError, partial(format_table, rows, indent=-1))
        raises(ValueError, partial(format_table, rows, gap=0))
        raises(ValueError, partial(format_table, rows, gap=-1))
        raises(ValueError, partial(format_table, rows, min_widths=(-1,)))
        raises(ValueError, partial(format_table, rows, min_widths=(0, -1)))
    raises(
        ValueError,
        partial(format_table, [("a", "b", "c", "d")], min_widths=(1, 1, 1, 1, 1)),
    )
    raises(ValueError, partial(format_table, [("a",)], min_widths=(1, 1)))
