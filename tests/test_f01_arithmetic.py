"""Tests of F01 for in_base_unit, scale, and add_quantities (F01-T25 to F01-T37)."""

from collections.abc import Iterable, Iterator
from decimal import Decimal
from fractions import Fraction

import pytest

from f01_support import q, same
from recipe_menu.units import TO_TASTE, Quantity, Unit, add_quantities

G, KG, JIN, LIANG = Unit.G, Unit.KG, Unit.JIN, Unit.LIANG
ML, L, TSP, TBSP = Unit.ML, Unit.L, Unit.TSP, Unit.TBSP
PIECE, STALK, CLOVE, BUNCH, PACK = Unit.PIECE, Unit.STALK, Unit.CLOVE, Unit.BUNCH, Unit.PACK


def test_f01_t25_base_unit_conversion_is_exact() -> None:
    """Mass converts to grams and volume to millilitres, exactly."""
    cases = [
        (q(2, KG), q(2000, G)),
        (q(1, JIN), q(500, G)),
        (q(3, LIANG), q(150, G)),
        (q(7, G), q(7, G)),
        (q(3, KG, 2), q(1500, G)),
        (q(1, KG, 3), q(1000, G, 3)),
        (q(2, L), q(2000, ML)),
        (q(3, TSP), q(15, ML)),
        (q(2, TBSP), q(30, ML)),
        (q(7, ML), q(7, ML)),
        (q(1, TSP, 3), q(5, ML, 3)),
    ]
    for quantity, expected in cases:
        same(quantity.in_base_unit(), expected)


def test_f01_t26_count_and_to_taste_stay() -> None:
    """A count and to taste stay as they are."""
    for quantity in [q(3, CLOVE), q(1, PIECE, 2), q(1, PACK), TO_TASTE]:
        same(quantity.in_base_unit(), quantity)


def test_f01_t27_different_units_are_unequal_but_same_size() -> None:
    """Quantities in different units are unequal, and in_base_unit compares their sizes."""
    pairs = [(q(1, KG), q(1000, G)), (q(1, JIN), q(10, LIANG)), (q(1, TBSP), q(3, TSP))]
    for first, second in pairs:
        assert first != second
        same(first.in_base_unit(), second.in_base_unit())


def test_f01_t28_scale_multiplies_exactly() -> None:
    """Scaling multiplies the amount exactly and keeps the unit."""
    cases = [
        (q(2, TBSP), Fraction(4, 2), q(4, TBSP)),
        (q(3, PIECE), Fraction(3, 2), q(9, PIECE, 2)),
        (q(1, JIN), Fraction(2), q(2, JIN)),
        (q(300, G), Fraction(3, 2), q(450, G)),
        (q(300, G), Fraction(1, 2), q(150, G)),
        (q(1, PIECE), Fraction(1, 3), q(1, PIECE, 3)),
        (q(3, KG, 2), Fraction(2, 3), q(1, KG)),
    ]
    for quantity, factor, expected in cases:
        same(quantity.scale(factor), expected)


def test_f01_t29_to_taste_stays_to_taste_when_scaled() -> None:
    """To taste stays to taste."""
    assert TO_TASTE.scale(Fraction(2)) == TO_TASTE
    assert TO_TASTE.scale(Fraction(1, 2)) == TO_TASTE


def test_f01_t30_factor_must_be_fraction() -> None:
    """A factor that is not a Fraction is a wrong call."""
    for quantity in (q(2, TBSP), TO_TASTE):
        for factor in (2, 2.0, "2", Decimal("2")):
            with pytest.raises(TypeError):
                quantity.scale(factor)  # type: ignore[arg-type]


def test_f01_t31_factor_must_be_greater_than_zero() -> None:
    """A factor of 0 or less is a wrong call, for to taste too."""
    for quantity in (q(2, TBSP), TO_TASTE):
        for factor in (Fraction(0), Fraction(-1), Fraction(-1, 2)):
            with pytest.raises(ValueError):
                quantity.scale(factor)


def check_sums(quantities: Iterable[Quantity], expected: tuple[Quantity, ...]) -> None:
    """Asserts the result of ``add_quantities``, with exact ``Fraction`` amounts.

    Args:
        quantities: The quantities to add.
        expected: The expected sums.
    """
    result = add_quantities(quantities)
    assert isinstance(result, tuple)
    assert result == expected
    for item in result:
        assert type(item.amount) is Fraction


def test_f01_t32_mass_and_volume_add_in_base_units() -> None:
    """Mass adds up in grams and volume in millilitres."""
    check_sums([q(1, KG), q(1, JIN), q(1, LIANG), q(1, G)], (q(1551, G),))
    check_sums([q(1, L), q(1, TSP), q(1, TBSP), q(1, ML)], (q(1021, ML),))
    check_sums([q(1, KG)], (q(1000, G),))
    check_sums([q(1, TBSP)], (q(15, ML),))


def test_f01_t33_each_count_unit_adds_on_its_own() -> None:
    """Each count unit adds up on its own."""
    check_sums(
        [q(2, STALK), q(1, STALK), q(1, BUNCH), q(3, PIECE), q(2, PIECE)],
        (q(3, STALK), q(1, BUNCH), q(5, PIECE)),
    )
    check_sums([q(2, PIECE), q(100, G), q(1, TBSP)], (q(2, PIECE), q(100, G), q(15, ML)))


def test_f01_t34_sums_come_in_order_of_first_appearance() -> None:
    """The sums come in the order in which their groups first appear."""
    check_sums([q(2, TBSP), q(10, G)], (q(30, ML), q(10, G)))
    check_sums([q(10, G), q(2, TBSP)], (q(10, G), q(30, ML)))
    check_sums(
        [q(1, BUNCH), q(10, G), q(2, TBSP), q(1, STALK), q(5, G), q(1, ML), q(1, BUNCH)],
        (q(2, BUNCH), q(15, G), q(31, ML), q(1, STALK)),
    )


def test_f01_t35_to_taste_adds_nothing() -> None:
    """To taste adds nothing, and no amounts give no sums."""
    check_sums([TO_TASTE, q(2, TBSP), TO_TASTE], (q(30, ML),))
    check_sums([TO_TASTE, TO_TASTE], ())
    check_sums([TO_TASTE], ())
    check_sums([], ())


def test_f01_t36_sums_are_exact() -> None:
    """The sums are exact and not rounded."""
    check_sums([q(1, G, 3), q(1, G, 3)], (q(2, G, 3),))
    check_sums([q(1, KG, 10)] * 3, (q(300, G),))
    check_sums([q(1, PIECE, 2), q(1, PIECE, 3)], (q(5, PIECE, 6),))
    check_sums([q(1, TSP, 3), q(1, TSP, 3)], (q(10, ML, 3),))


def test_f01_t37_any_iterable_works() -> None:
    """Any iterable works, a generator included."""

    def generate() -> Iterator[Quantity]:
        """Yields 1 jin and 2 jin.

        Yields:
            The quantities.
        """
        yield q(1, JIN)
        yield q(2, JIN)

    check_sums(generate(), (q(1500, G),))
    check_sums((q(1, JIN), q(2, JIN)), (q(1500, G),))
