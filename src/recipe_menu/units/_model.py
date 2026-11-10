"""The unit and quantity types."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Final

from recipe_menu.lang import Lang


class UnitKind(Enum):
    """The kind of a unit: mass, volume, or count.

    Mass converts to grams and volume to millilitres. A count unit converts to nothing else, and
    no kind converts to another kind.
    """

    MASS = "mass"
    VOLUME = "volume"
    COUNT = "count"


class Unit(Enum):
    """One member for each unit, with its kind, its size, and its labels in both languages.

    Each member's value is its English label. Find a unit by its spelling with ``parse_unit``.
    """

    G = "g"
    KG = "kg"
    JIN = "jin"
    LIANG = "liang"
    ML = "ml"
    L = "L"
    TSP = "tsp"
    TBSP = "tbsp"
    PIECE = "piece"
    STALK = "stalk"
    CLOVE = "clove"
    SLICE = "slice"
    BLOCK = "block"
    BUNCH = "bunch"
    CAN = "can"
    PACK = "pack"

    @property
    def kind(self) -> UnitKind:
        """The kind of this unit.

        Returns:
            The ``UnitKind`` of this unit.
        """
        raise NotImplementedError

    @property
    def size(self) -> Fraction | None:
        """The size of this unit in grams or millilitres.

        Returns:
            The grams in one mass unit or the millilitres in one volume unit, exact, and ``None``
            for a count unit.
        """
        raise NotImplementedError

    def label(self, lang: Lang, *, plural: bool = False) -> str:
        """Gives the label of this unit.

        Args:
            lang: The language of the label.
            plural: Whether the label follows an amount other than 1. Changes English count
                labels only.

        Returns:
            The label from the unit table.
        """
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Quantity:
    """An exact amount in a unit, or "to taste".

    Attributes:
        amount: The exact amount, counted in ``unit``. Greater than 0, and ``None`` only for to
            taste.
        unit: The unit of ``amount``. ``None`` only for to taste. ``amount`` and ``unit`` are
            both set or both ``None``.

    Raises:
        TypeError: ``amount`` is neither a ``Fraction`` nor ``None``.
        ValueError: Exactly one of ``amount`` and ``unit`` is ``None``.
        ValueError: ``amount`` is 0 or less.
    """

    amount: Fraction | None
    unit: Unit | None

    @property
    def is_to_taste(self) -> bool:
        """Whether this quantity is "to taste".

        Returns:
            ``True`` when ``amount`` and ``unit`` are ``None``.
        """
        raise NotImplementedError

    def in_base_unit(self) -> "Quantity":
        """Converts mass to grams and volume to millilitres, exactly.

        Returns:
            The quantity in ``Unit.G`` or ``Unit.ML``. A count or to taste is returned as it is.
        """
        raise NotImplementedError

    def scale(self, factor: Fraction) -> "Quantity":
        """Multiplies the amount by a factor and keeps the unit.

        Args:
            factor: The number to multiply by. Greater than 0.

        Returns:
            ``Quantity(amount * factor, unit)``, or ``TO_TASTE`` for to taste. The factor is
            checked first, so to taste raises too for a bad factor.

        Raises:
            TypeError: ``factor`` is not a ``Fraction``, to taste included.
            ValueError: ``factor`` is 0 or less, to taste included.
        """
        raise NotImplementedError

    def to_text(self, lang: Lang) -> str:
        """Writes the quantity in its own unit.

        Args:
            lang: The language to write in.

        Returns:
            The amount rounded up to at most two decimals and the unit label, or the to taste
            text.

        Raises:
            ValueError: The rounded amount has more than 4,300 digits before the point.
        """
        raise NotImplementedError

    def to_rounded_text(self, lang: Lang) -> str:
        """Writes the quantity by the shopping list's rounding rules.

        Args:
            lang: The language to write in.

        Returns:
            The text, or the to taste text for to taste. Grams and millilitres are rounded up to
            whole numbers before they are compared with 1000; 1000 g or more is written in kg and
            1000 ml or more in L, and kg and L are rounded up to at most two decimals. Counts
            are rounded up to whole numbers.

        Raises:
            ValueError: The rounded amount that is written has more than 4,300 digits before the
                point.
        """
        raise NotImplementedError


TO_TASTE: Final[Quantity] = Quantity(None, None)


class WrongQuantityReason(Enum):
    """What is wrong with an amount text that ``parse_quantity`` cannot read."""

    EMPTY = "empty"
    NOT_A_NUMBER = "not-a-number"
    UNKNOWN_UNIT = "unknown-unit"
    NO_UNIT = "no-unit"
    ZERO = "zero"


@dataclass(frozen=True, slots=True)
class WrongQuantity:
    """An amount text that ``parse_quantity`` cannot read.

    Attributes:
        reason: What is wrong.
        text: The amount text, without whitespace at either end.
        unit: The unknown unit as written. Set for ``UNKNOWN_UNIT`` only.
    """

    reason: WrongQuantityReason
    text: str
    unit: str | None = None
