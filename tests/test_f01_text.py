"""Tests of F01 for to_text and to_rounded_text (F01-T38 to F01-T47 and F01-T54 to F01-T57)."""

from fractions import Fraction

import pytest

from f01_support import q
from recipe_menu.lang import Lang
from recipe_menu.units import TO_TASTE, Quantity, Unit

EN, ZH = Lang.EN, Lang.ZH
G, KG, JIN, LIANG = Unit.G, Unit.KG, Unit.JIN, Unit.LIANG
ML, L, TSP, TBSP = Unit.ML, Unit.L, Unit.TSP, Unit.TBSP
PIECE, STALK, CAN, BLOCK = Unit.PIECE, Unit.STALK, Unit.CAN, Unit.BLOCK


def test_f01_t38_to_text_writes_amount_and_label() -> None:
    """A quantity is written as its amount, a space, and its unit's label."""
    en = [
        (q(1, STALK), "1 stalk"),
        (q(3, PIECE), "3 pieces"),
        (q(1, JIN), "1 jin"),
        (q(2, JIN), "2 jin"),
        (q(2, LIANG), "2 liang"),
        (q(1500, G), "1500 g"),
        (q(2, TBSP), "2 tbsp"),
        (q(1, L), "1 L"),
    ]
    for quantity, text in en:
        assert quantity.to_text(EN) == text
    zh = [
        (q(2, TSP), "2 茶匙"),
        (q(600, G), "600 g"),
        (q(3, PIECE), "3 个"),
        (q(1, JIN), "1 斤"),
        (q(2, LIANG), "2 两"),
        (q(1, L), "1 L"),
    ]
    for quantity, text in zh:
        assert quantity.to_text(ZH) == text


def test_f01_t39_to_text_rounds_up_to_two_decimals() -> None:
    """The amount is rounded up to at most two decimals, with no trailing zeros."""
    en = [
        (q(4, TBSP, 3), "1.34 tbsp"),
        (q(1, G, 3), "0.34 g"),
        (q(2, G, 3), "0.67 g"),
        (q(9, PIECE, 2), "4.5 pieces"),
        (q(5, G, 2), "2.5 g"),
        (q(21, G, 10), "2.1 g"),
        (q(201, G, 100), "2.01 g"),
        (q(1, G, 1000), "0.01 g"),
        (q(1, G, 200), "0.01 g"),
        (q(12345, G), "12345 g"),
    ]
    for quantity, text in en:
        assert quantity.to_text(EN) == text
    assert q(9, PIECE, 2).to_text(ZH) == "4.5 个"


def test_f01_t40_to_text_rounds_up_exactly() -> None:
    """Rounding up is exact where float arithmetic would round one step too far."""
    assert q(7, G, 100).to_text(EN) == "0.07 g"
    assert q(7, G, 50).to_text(EN) == "0.14 g"
    assert q(11, KG, 10).to_text(EN) == "1.1 kg"


def test_f01_t41_english_label_is_plural_unless_amount_is_one() -> None:
    """In English, the label is plural unless the written amount is 1."""
    assert q(1, PIECE).to_text(EN) == "1 piece"
    assert q(999, PIECE, 1000).to_text(EN) == "1 piece"
    assert q(1001, PIECE, 1000).to_text(EN) == "1.01 pieces"
    assert q(1, PIECE, 2).to_text(EN) == "0.5 pieces"
    assert q(2, PIECE).to_text(EN) == "2 pieces"
    assert q(2, PIECE).to_text(ZH) == "2 个"


def test_f01_t42_to_text_to_taste() -> None:
    """To taste, in each language."""
    assert TO_TASTE.to_text(EN) == "to taste"
    assert TO_TASTE.to_text(ZH) == "适量"


def test_f01_t43_to_rounded_text_to_taste() -> None:
    """To taste, in each language."""
    assert TO_TASTE.to_rounded_text(EN) == "to taste"
    assert TO_TASTE.to_rounded_text(ZH) == "适量"


def test_f01_t44_rounded_text_below_1000() -> None:
    """Below 1000, mass is in grams and volume in millilitres, rounded up to a whole number."""
    en = [
        (q(1, JIN), "500 g"),
        (q(2, LIANG), "100 g"),
        (q(1, TSP, 3), "2 ml"),
        (q(1, G, 10), "1 g"),
        (q(2, KG, 3), "667 g"),
        (q(999, G), "999 g"),
        (q(999, ML), "999 ml"),
    ]
    for quantity, text in en:
        assert quantity.to_rounded_text(EN) == text
    assert q(1, TBSP).to_rounded_text(ZH) == "15 ml"
    assert q(600, G).to_rounded_text(ZH) == "600 g"


def test_f01_t45_rounded_text_from_1000_uses_kg_and_l() -> None:
    """1000 g or more is in kg, and 1000 ml or more in L, rounded up to two decimals."""
    en = [
        (q(1500, G), "1.5 kg"),
        (q(1001, G), "1.01 kg"),
        (q(1999, G), "2 kg"),
        (q(1999, G, 2), "1 kg"),
        (q(2, JIN), "1 kg"),
        (q(12345, G), "12.35 kg"),
        (q(1234567, G), "1234.57 kg"),
        (q(1, L), "1 L"),
        (q(67, TBSP), "1.01 L"),
        (q(3, L, 2), "1.5 L"),
    ]
    for quantity, text in en:
        assert quantity.to_rounded_text(EN) == text
    assert q(1000, G).to_rounded_text(ZH) == "1 kg"
    assert q(1500, ML).to_rounded_text(ZH) == "1.5 L"


def test_f01_t46_rounded_text_of_a_count() -> None:
    """A count is rounded up to a whole number and stays in its unit."""
    en = [
        (q(3, STALK, 2), "2 stalks"),
        (q(9, PIECE, 2), "5 pieces"),
        (q(1, PIECE, 3), "1 piece"),
        (q(1, BLOCK), "1 block"),
        (q(1000, PIECE), "1000 pieces"),
    ]
    for quantity, text in en:
        assert quantity.to_rounded_text(EN) == text
    assert q(5, STALK).to_rounded_text(ZH) == "5 根"
    assert q(2, CAN).to_rounded_text(ZH) == "2 罐"


def test_f01_t47_rounded_text_rounds_up_exactly() -> None:
    """Rounding up is exact where float arithmetic would round one step too far."""
    assert q(1100, G).to_rounded_text(EN) == "1.1 kg"
    assert q(1090, G).to_rounded_text(EN) == "1.09 kg"
    assert q(11, KG, 10).to_rounded_text(EN) == "1.1 kg"
    assert q(403, KG, 100).to_rounded_text(EN) == "4.03 kg"


@pytest.mark.usefixtures("default_int_limit")
def test_f01_t54_to_text_writes_4300_digits() -> None:
    """An amount with 4,300 digits before the point is written in full."""
    big = Quantity(Fraction(10**4300 - 1), G)
    assert big.to_text(EN) == "9" * 4300 + " g"
    half = Quantity(Fraction(2 * 10**4300 - 1, 2), G)
    assert half.to_text(EN) == "9" * 4300 + ".5 g"


@pytest.mark.usefixtures("default_int_limit")
def test_f01_t55_to_text_rejects_more_than_4300_digits() -> None:
    """A rounded amount with more than 4,300 digits before the point is a wrong call."""
    for quantity in [
        Quantity(Fraction(10**4300), G),
        Quantity(Fraction(10**4303 - 1, 1000), G),
    ]:
        for lang in (EN, ZH):
            with pytest.raises(ValueError):
                quantity.to_text(lang)


@pytest.mark.usefixtures("default_int_limit")
def test_f01_t56_rounded_text_counts_digits_after_kg_and_l() -> None:
    """The limit counts the digits of the amount that to_rounded_text writes."""
    cases = [
        (Quantity(Fraction(10**4300), G), "1" + "0" * 4297 + " kg"),
        (Quantity(Fraction(10**4303 - 500), G), "9" * 4300 + ".5 kg"),
        (Quantity(Fraction(10**4303 - 1000), ML), "9" * 4300 + " L"),
        (Quantity(Fraction(10**4300 - 1), PIECE), "9" * 4300 + " pieces"),
    ]
    for quantity, text in cases:
        assert quantity.to_rounded_text(EN) == text
    with pytest.raises(ValueError):
        cases[0][0].to_text(EN)


@pytest.mark.usefixtures("default_int_limit")
def test_f01_t57_rounded_text_rejects_more_than_4300_digits() -> None:
    """An amount that to_rounded_text would write with over 4,300 digits is a wrong call."""
    quantities = [
        Quantity(Fraction(10**4303), G),
        Quantity(Fraction(10**4303 - 1), G),
        Quantity(Fraction(10**4303), ML),
        Quantity(Fraction(10**4300), PIECE),
        Quantity(Fraction(2 * 10**4300 - 1, 2), PIECE),
    ]
    for quantity in quantities:
        for lang in (EN, ZH):
            with pytest.raises(ValueError):
                quantity.to_rounded_text(lang)
