"""Helpers that the F01 tests share."""

from fractions import Fraction

from recipe_menu.units import Quantity, Unit, WrongQuantity, WrongQuantityReason


def q(amount: int, unit: Unit, den: int = 1) -> Quantity:
    """Builds the quantity ``amount / den`` in ``unit``.

    Args:
        amount: The numerator.
        unit: The unit.
        den: The denominator.

    Returns:
        The quantity.
    """
    return Quantity(Fraction(amount, den), unit)


def wrong(reason: WrongQuantityReason, text: str, unit: str | None = None) -> WrongQuantity:
    """Builds a ``WrongQuantity``.

    Args:
        reason: The reason.
        text: The text of the wrong amount.
        unit: The unknown unit as written.

    Returns:
        The value.
    """
    return WrongQuantity(reason, text, unit)


def same(result: object, expected: Quantity | WrongQuantity) -> None:
    """Asserts that a result equals the expected value and that its amount is a ``Fraction``.

    Args:
        result: The value under test.
        expected: The expected value.
    """
    assert result == expected
    if isinstance(result, Quantity) and result.amount is not None:
        assert type(result.amount) is Fraction
