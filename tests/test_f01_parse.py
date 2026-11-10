"""Tests of F01 for parse_unit and parse_quantity (F01-T07 to F01-T24)."""

from fractions import Fraction

import pytest

from f01_support import q, same, wrong
from recipe_menu.units import (
    TO_TASTE,
    Quantity,
    Unit,
    WrongQuantity,
    WrongQuantityReason,
    parse_quantity,
    parse_unit,
)

EMPTY = WrongQuantityReason.EMPTY
NOT_A_NUMBER = WrongQuantityReason.NOT_A_NUMBER
UNKNOWN_UNIT = WrongQuantityReason.UNKNOWN_UNIT
NO_UNIT = WrongQuantityReason.NO_UNIT
ZERO = WrongQuantityReason.ZERO

SPELLINGS = {
    Unit.G: ["g", "克"],
    Unit.KG: ["kg", "千克", "公斤"],
    Unit.JIN: ["jin", "斤"],
    Unit.LIANG: ["liang", "两"],
    Unit.ML: ["ml", "毫升"],
    Unit.L: ["L", "升"],
    Unit.TSP: ["tsp", "茶匙"],
    Unit.TBSP: ["tbsp", "汤匙"],
    Unit.PIECE: ["piece", "pieces", "个"],
    Unit.STALK: ["stalk", "stalks", "根"],
    Unit.CLOVE: ["clove", "cloves", "瓣"],
    Unit.SLICE: ["slice", "slices", "片"],
    Unit.BLOCK: ["block", "blocks", "块"],
    Unit.BUNCH: ["bunch", "bunches", "把"],
    Unit.CAN: ["can", "cans", "罐"],
    Unit.PACK: ["pack", "packs", "包"],
}


def test_f01_t07_every_spelling_names_its_unit() -> None:
    """Each spelling of the table names its unit."""
    count = 0
    for unit, spellings in SPELLINGS.items():
        for spelling in spellings:
            assert parse_unit(spelling) is unit
            count += 1
    assert count == 41


def test_f01_t08_english_spellings_match_in_any_case() -> None:
    """English spellings match in any case."""
    texts = ["G", "KG", "Kg", "kG", "JIN", "Liang", "ML", "Ml", "l", "TSP", "Tbsp", "PIECE"]
    texts += ["Pieces", "STALKS", "Clove", "SLICES", "Block", "BUNCHES", "Can", "PACKS"]
    units = [Unit.G, Unit.KG, Unit.KG, Unit.KG, Unit.JIN, Unit.LIANG, Unit.ML, Unit.ML, Unit.L]
    units += [Unit.TSP, Unit.TBSP, Unit.PIECE, Unit.PIECE, Unit.STALK, Unit.CLOVE, Unit.SLICE]
    units += [Unit.BLOCK, Unit.BUNCH, Unit.CAN, Unit.PACK]
    assert len(texts) == len(units)
    for text, unit in zip(texts, units, strict=True):
        assert parse_unit(text) is unit


def test_f01_t09_whitespace_at_both_ends_does_not_matter() -> None:
    """Whitespace at both ends of a unit does not matter."""
    assert parse_unit(" Tbsp ") is Unit.TBSP
    assert parse_unit("\t公斤\n") is Unit.KG
    assert parse_unit("　个　") is Unit.PIECE
    assert parse_unit("  l") is Unit.L


def test_f01_t10_a_text_that_is_no_spelling_names_no_unit() -> None:
    """A text that is no spelling names no unit."""
    texts = ["", "   ", "cups", "cup", "kgs", "gs", "jins", "liangs", "to taste", "适量"]
    texts += ["茶 匙", "g.", "克克", "ｋｇ"]
    for text in texts:
        assert parse_unit(text) is None


def test_f01_t11_number_and_unit_in_either_language() -> None:
    """A number and a unit in either language, with or without a space."""
    cases = [
        ("300 g", q(300, Unit.G)),
        ("300g", q(300, Unit.G)),
        ("300克", q(300, Unit.G)),
        ("1.5kg", q(3, Unit.KG, 2)),
        ("1.5 公斤", q(3, Unit.KG, 2)),
        ("1 斤", q(1, Unit.JIN)),
        ("2 两", q(2, Unit.LIANG)),
        ("1 L", q(1, Unit.L)),
        ("500 毫升", q(500, Unit.ML)),
        ("1 tsp", q(1, Unit.TSP)),
        ("2汤匙", q(2, Unit.TBSP)),
        ("3 个", q(3, Unit.PIECE)),
        ("1 根", q(1, Unit.STALK)),
        ("3 cloves", q(3, Unit.CLOVE)),
        ("1 罐", q(1, Unit.CAN)),
    ]
    for text, expected in cases:
        same(parse_quantity(text), expected)


def test_f01_t12_decimal_becomes_exact_fraction() -> None:
    """A decimal number becomes an exact fraction."""
    cases = [
        ("0.25 tsp", q(1, Unit.TSP, 4)),
        ("0.1 g", q(1, Unit.G, 10)),
        ("1.50 kg", q(3, Unit.KG, 2)),
        ("1.005 kg", q(201, Unit.KG, 200)),
        ("10.0 ml", q(10, Unit.ML)),
        ("0.5 个", q(1, Unit.PIECE, 2)),
    ]
    for text, expected in cases:
        same(parse_quantity(text), expected)
    tenth = parse_quantity("0.1 g")
    assert isinstance(tenth, Quantity)
    assert tenth.amount == Fraction(1, 10)
    assert tenth.amount != Fraction(0.1)


def test_f01_t13_whitespace_does_not_matter() -> None:
    """Whitespace at both ends and before the unit does not matter."""
    cases = [
        (" 300 g ", q(300, Unit.G)),
        ("　300 g　", q(300, Unit.G)),
        ("300   g", q(300, Unit.G)),
        ("300\tg", q(300, Unit.G)),
        ("3　个", q(3, Unit.PIECE)),
        ("\n1 斤\n", q(1, Unit.JIN)),
    ]
    for text, expected in cases:
        same(parse_quantity(text), expected)


def test_f01_t14_to_taste_in_either_language() -> None:
    """To taste, in either language."""
    texts = ["适量", " 适量 ", "　适量", "to taste", "To taste", "TO TASTE", "tO tAsTe"]
    texts += ["To  taste", "to\ttaste", "to　taste", " to taste "]
    for text in texts:
        assert parse_quantity(text) == TO_TASTE
        assert parse_quantity(text, Unit.PIECE) == TO_TASTE


def test_f01_t15_number_without_unit_takes_default() -> None:
    """A number without a unit takes the default unit."""
    same(parse_quantity("3", Unit.PIECE), q(3, Unit.PIECE))
    same(parse_quantity("300", Unit.G), q(300, Unit.G))
    same(parse_quantity("1.5", Unit.KG), q(3, Unit.KG, 2))
    same(parse_quantity("0.5", Unit.PIECE), q(1, Unit.PIECE, 2))


def test_f01_t16_unit_in_text_wins_over_default() -> None:
    """A unit in the text wins over the default unit."""
    same(parse_quantity("2 tbsp", Unit.PIECE), q(2, Unit.TBSP))
    same(parse_quantity("300 g", Unit.PIECE), q(300, Unit.G))
    same(parse_quantity("1 斤", Unit.G), q(1, Unit.JIN))
    same(parse_quantity("3 瓣", Unit.STALK), q(3, Unit.CLOVE))


def test_f01_t17_empty_text() -> None:
    """A text that is empty or holds only whitespace is EMPTY."""
    for text in ["", " ", "\t\n", "　", "　 　"]:
        assert parse_quantity(text) == wrong(EMPTY, "")
        assert parse_quantity(text, Unit.PIECE) == wrong(EMPTY, "")


def test_f01_t18_not_a_number() -> None:
    """A missing number, or one that is not a decimal of ASCII digits, is NOT_A_NUMBER."""
    texts = ["a few", "g", "1/2 tsp", "1,5 g", "-1 g", "+1 g", "½ tsp", "３ 个", "٣ g", "三 个"]
    texts += [".5 g", "1. g", "1.2.3 g", "1_000 g", "1-2 个", "to tastes", "to-taste"]
    for text in texts:
        assert parse_quantity(text) == wrong(NOT_A_NUMBER, text)
    assert parse_quantity(" a few ", Unit.PIECE) == wrong(NOT_A_NUMBER, "a few")


def test_f01_t19_unknown_unit() -> None:
    """A unit that is no spelling is UNKNOWN_UNIT, and holds the unit as written."""
    cases = [
        ("1 cups", "1 cups", "cups"),
        (" 1 cups ", "1 cups", "cups"),
        ("2 Cups", "2 Cups", "Cups"),
        ("1   cup", "1   cup", "cup"),
        ("300 gs", "300 gs", "gs"),
        ("1 适量", "1 适量", "适量"),
        ("1 to taste", "1 to taste", "to taste"),
        ("2 茶 匙", "2 茶 匙", "茶 匙"),
    ]
    for text, shown, unit in cases:
        assert parse_quantity(text) == wrong(UNKNOWN_UNIT, shown, unit)
    assert parse_quantity("1 cups", Unit.PIECE) == wrong(UNKNOWN_UNIT, "1 cups", "cups")


def test_f01_t20_no_unit() -> None:
    """A number with no unit and no default unit is NO_UNIT."""
    assert parse_quantity("3") == wrong(NO_UNIT, "3")
    assert parse_quantity("1.5") == wrong(NO_UNIT, "1.5")
    assert parse_quantity(" 3 ") == wrong(NO_UNIT, "3")
    assert parse_quantity("　3") == wrong(NO_UNIT, "3")


def test_f01_t21_zero() -> None:
    """A number equal to 0 is ZERO."""
    for text in ["0 g", "0.00 个", "00 kg", "0.0kg"]:
        assert parse_quantity(text) == wrong(ZERO, text)
    assert parse_quantity("0", Unit.PIECE) == wrong(ZERO, "0")


def test_f01_t22_first_reason_wins() -> None:
    """When several reasons apply, the first one in the table wins."""
    assert parse_quantity("0 cups") == wrong(UNKNOWN_UNIT, "0 cups", "cups")
    assert parse_quantity("0 cups", Unit.PIECE) == wrong(UNKNOWN_UNIT, "0 cups", "cups")
    assert parse_quantity("0") == wrong(NO_UNIT, "0")
    assert parse_quantity("-0 g") == wrong(NOT_A_NUMBER, "-0 g")
    assert parse_quantity("a cups") == wrong(NOT_A_NUMBER, "a cups")
    for text in ["1234567890123456 cups", "1234567890123456", "0" * 16 + " g"]:
        assert parse_quantity(text) == wrong(NOT_A_NUMBER, text)


def test_f01_t23_to_taste_needs_whitespace_between_words() -> None:
    """To taste needs at least one whitespace character between the two words."""
    for text in ["totaste", "TOTASTE"]:
        assert parse_quantity(text) == wrong(NOT_A_NUMBER, text)
        assert parse_quantity(text, Unit.PIECE) == wrong(NOT_A_NUMBER, text)


@pytest.mark.usefixtures("default_int_limit")
def test_f01_t24_number_has_at_most_15_digits() -> None:
    """A number has at most 15 digits, and a longer one is NOT_A_NUMBER without raising."""
    ok = [
        ("123456789012345 g", q(123456789012345, Unit.G)),
        ("12345678901234.5 g", q(24691357802469, Unit.G, 2)),
        ("0" * 14 + "1 g", q(1, Unit.G)),
        ("1." + "0" * 14 + " g", q(1, Unit.G)),
        ("0." + "0" * 13 + "1 g", q(1, Unit.G, 10**14)),
    ]
    for text, expected in ok:
        same(parse_quantity(text), expected)
    too_long = ["1234567890123456 g", "0" * 15 + "1 g", "1." + "0" * 15 + " g"]
    too_long += ["0.000000000000001 g", "1" * 5000 + " g"]
    for text in too_long:
        result = parse_quantity(text)
        assert isinstance(result, WrongQuantity)
        assert result == wrong(NOT_A_NUMBER, text)
    same(parse_quantity("123456789012345", Unit.PIECE), q(123456789012345, Unit.PIECE))
    assert parse_quantity("1234567890123456", Unit.PIECE) == wrong(NOT_A_NUMBER, "1234567890123456")
