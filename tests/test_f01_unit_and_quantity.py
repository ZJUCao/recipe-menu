"""Tests of F01 for Unit, UnitKind, and Quantity (F01-T01 to F01-T06)."""

from decimal import Decimal
from fractions import Fraction

import pytest

from recipe_menu.lang import Lang
from recipe_menu.units import TO_TASTE, Quantity, Unit, UnitKind

ALL_UNITS = [
    Unit.G, Unit.KG, Unit.JIN, Unit.LIANG, Unit.ML, Unit.L, Unit.TSP, Unit.TBSP,
    Unit.PIECE, Unit.STALK, Unit.CLOVE, Unit.SLICE, Unit.BLOCK, Unit.BUNCH, Unit.CAN, Unit.PACK,
]  # fmt: skip
COUNT_UNITS = ALL_UNITS[8:]


def test_f01_t01_units_have_kind_and_size() -> None:
    """Each unit has the kind and the size of the table."""
    assert list(Unit.__members__) == [
        "G", "KG", "JIN", "LIANG", "ML", "L", "TSP", "TBSP",
        "PIECE", "STALK", "CLOVE", "SLICE", "BLOCK", "BUNCH", "CAN", "PACK",
    ]  # fmt: skip
    values = ["g", "kg", "jin", "liang", "ml", "L", "tsp", "tbsp"]
    values += ["piece", "stalk", "clove", "slice", "block", "bunch", "can", "pack"]
    assert [u.value for u in Unit] == values
    assert {k.name: k.value for k in UnitKind} == {
        "MASS": "mass",
        "VOLUME": "volume",
        "COUNT": "count",
    }
    for unit in ALL_UNITS[:4]:
        assert unit.kind is UnitKind.MASS
    for unit in ALL_UNITS[4:8]:
        assert unit.kind is UnitKind.VOLUME
    for unit in COUNT_UNITS:
        assert unit.kind is UnitKind.COUNT
        assert unit.size is None
    sizes = [1, 1000, 500, 50, 1, 1000, 5, 15]
    for unit, size in zip(ALL_UNITS[:8], sizes, strict=True):
        assert unit.size == Fraction(size)
        assert type(unit.size) is Fraction


def test_f01_t02_unit_labels() -> None:
    """Each unit has its labels, and only English count labels change in the plural."""
    en = ["g", "kg", "jin", "liang", "ml", "L", "tsp", "tbsp"]
    en += ["piece", "stalk", "clove", "slice", "block", "bunch", "can", "pack"]
    plural = ["pieces", "stalks", "cloves", "slices", "blocks", "bunches", "cans", "packs"]
    zh = ["g", "kg", "斤", "两", "ml", "L", "茶匙", "汤匙", "个", "根", "瓣", "片", "块", "把"]
    zh += ["罐", "包"]
    for i, unit in enumerate(ALL_UNITS):
        assert unit.label(Lang.EN) == en[i]
        assert unit.label(Lang.EN, plural=False) == en[i]
        expected_plural = plural[i - 8] if i >= 8 else en[i]
        assert unit.label(Lang.EN, plural=True) == expected_plural
        assert unit.label(Lang.ZH) == zh[i]
        assert unit.label(Lang.ZH, plural=False) == zh[i]
        assert unit.label(Lang.ZH, plural=True) == zh[i]


def test_f01_t03_quantity_keeps_amount_and_unit() -> None:
    """A quantity keeps its amount and unit, and only to taste is to taste."""
    grams = Quantity(Fraction(300), Unit.G)
    assert grams.amount == Fraction(300)
    assert grams.unit is Unit.G
    assert grams.is_to_taste is False
    half = Quantity(Fraction(1, 2), Unit.PIECE)
    assert half.amount == Fraction(1, 2)
    assert half.unit is Unit.PIECE
    assert half.is_to_taste is False
    for taste in (Quantity(None, None), TO_TASTE):
        assert taste.amount is None
        assert taste.unit is None
        assert taste.is_to_taste is True


def test_f01_t04_amount_must_be_fraction_or_none() -> None:
    """An amount that is neither a Fraction nor None is a wrong call."""
    for amount in (300.0, 300, "300", Decimal("300")):
        with pytest.raises(TypeError):
            Quantity(amount, Unit.G)  # type: ignore[arg-type]


def test_f01_t05_amount_and_unit_come_together() -> None:
    """An amount and a unit are both set or both None."""
    with pytest.raises(ValueError):
        Quantity(None, Unit.G)
    with pytest.raises(ValueError):
        Quantity(Fraction(1), None)


def test_f01_t06_amount_is_greater_than_zero() -> None:
    """An amount is greater than 0."""
    for amount in (Fraction(0), Fraction(-1), Fraction(-1, 2)):
        for unit in (Unit.G, Unit.PIECE):
            with pytest.raises(ValueError):
                Quantity(amount, unit)
