"""The unit and quantity types."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from math import ceil
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
        return _UNIT_DATA[self][0]

    @property
    def size(self) -> Fraction | None:
        """The size of this unit in grams or millilitres.

        Returns:
            The grams in one mass unit or the millilitres in one volume unit, exact, and ``None``
            for a count unit.
        """
        return _UNIT_DATA[self][1]

    def label(self, lang: Lang, *, plural: bool = False) -> str:
        """Gives the label of this unit.

        Args:
            lang: The language of the label.
            plural: Whether the label follows an amount other than 1. Changes English count
                labels only.

        Returns:
            The label from the unit table.
        """
        _, _, english, english_plural, chinese = _UNIT_DATA[self]
        if lang == Lang.ZH:
            return chinese
        return english_plural if plural else english


# Each row: kind, size, English label, English plural, Chinese label. Every member has a row.
_UNIT_DATA: Final[dict[Unit, tuple[UnitKind, Fraction | None, str, str, str]]] = {
    Unit.G: (UnitKind.MASS, Fraction(1), "g", "g", "g"),
    Unit.KG: (UnitKind.MASS, Fraction(1000), "kg", "kg", "kg"),
    Unit.JIN: (UnitKind.MASS, Fraction(500), "jin", "jin", "斤"),
    Unit.LIANG: (UnitKind.MASS, Fraction(50), "liang", "liang", "两"),
    Unit.ML: (UnitKind.VOLUME, Fraction(1), "ml", "ml", "ml"),
    Unit.L: (UnitKind.VOLUME, Fraction(1000), "L", "L", "L"),
    Unit.TSP: (UnitKind.VOLUME, Fraction(5), "tsp", "tsp", "茶匙"),
    Unit.TBSP: (UnitKind.VOLUME, Fraction(15), "tbsp", "tbsp", "汤匙"),
    Unit.PIECE: (UnitKind.COUNT, None, "piece", "pieces", "个"),
    Unit.STALK: (UnitKind.COUNT, None, "stalk", "stalks", "根"),
    Unit.CLOVE: (UnitKind.COUNT, None, "clove", "cloves", "瓣"),
    Unit.SLICE: (UnitKind.COUNT, None, "slice", "slices", "片"),
    Unit.BLOCK: (UnitKind.COUNT, None, "block", "blocks", "块"),
    Unit.BUNCH: (UnitKind.COUNT, None, "bunch", "bunches", "把"),
    Unit.CAN: (UnitKind.COUNT, None, "can", "cans", "罐"),
    Unit.PACK: (UnitKind.COUNT, None, "pack", "packs", "包"),
}

_TO_TASTE_TEXT: Final = {Lang.EN: "to taste", Lang.ZH: "适量"}


def _hundredths_text(hundredths: int) -> str:
    """Writes a number of hundredths as a decimal without trailing zeros.

    Args:
        hundredths: The amount times 100, a whole number.

    Returns:
        The text with ``.`` as the decimal point and no thousands separator.

    Raises:
        ValueError: The whole part has more digits than Python's limit on writing an ``int``.
    """
    whole, part = divmod(hundredths, 100)
    text = str(whole)
    if part:
        text += "." + f"{part:02d}".rstrip("0")
    return text


def _with_label(hundredths: int, unit: Unit, lang: Lang) -> str:
    """Joins a written amount and the label of its unit.

    Args:
        hundredths: The amount times 100, a whole number.
        unit: The unit to label the amount with.
        lang: The language of the label.

    Returns:
        The amount, a space, and the label. An English label is plural unless the amount is 1.

    Raises:
        ValueError: The whole part has more digits than Python's limit on writing an ``int``.
    """
    return f"{_hundredths_text(hundredths)} {unit.label(lang, plural=hundredths != 100)}"


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

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: ``amount`` is neither a ``Fraction`` nor ``None``.
            ValueError: Exactly one of ``amount`` and ``unit`` is ``None``, or ``amount`` is 0 or
                less.
        """
        if self.amount is not None and not isinstance(self.amount, Fraction):
            raise TypeError("amount must be a Fraction or None")
        if (self.amount is None) != (self.unit is None):
            raise ValueError("amount and unit must be both set or both None")
        if self.amount is not None and self.amount <= 0:
            raise ValueError("amount must be greater than 0")

    @property
    def is_to_taste(self) -> bool:
        """Whether this quantity is "to taste".

        Returns:
            ``True`` when ``amount`` and ``unit`` are ``None``.
        """
        return self.amount is None

    def in_base_unit(self) -> "Quantity":
        """Converts mass to grams and volume to millilitres, exactly.

        Returns:
            The quantity in ``Unit.G`` or ``Unit.ML``. A count or to taste is returned as it is.
        """
        if self.amount is None or self.unit is None:
            return self
        size = self.unit.size
        if size is None:
            return self
        base = Unit.G if self.unit.kind is UnitKind.MASS else Unit.ML
        return Quantity(self.amount * size, base)

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
        if not isinstance(factor, Fraction):
            raise TypeError("factor must be a Fraction")
        if factor <= 0:
            raise ValueError("factor must be greater than 0")
        if self.amount is None:
            return self
        return Quantity(self.amount * factor, self.unit)

    def to_text(self, lang: Lang) -> str:
        """Writes the quantity in its own unit.

        Args:
            lang: The language to write in.

        Returns:
            ``to taste`` in English or U+9002 U+91CF in Chinese for to taste. Otherwise the
            amount, a space, and the label of the unit. The amount is rounded up to at most two
            decimals and written with ``.`` as the decimal point, with no trailing zeros and no
            thousands separator. In English, the label is plural unless the written amount is 1.

        Raises:
            ValueError: The rounded amount has more than 4,300 digits before the point, Python's
                default limit on writing an ``int``, which ``PYTHONINTMAXSTRDIGITS`` can change.
        """
        if self.amount is None or self.unit is None:
            return _TO_TASTE_TEXT[lang]
        return _with_label(ceil(self.amount * 100), self.unit, lang)

    def to_rounded_text(self, lang: Lang) -> str:
        """Writes the quantity by the shopping list's rounding rules.

        Args:
            lang: The language to write in.

        Returns:
            ``to taste`` in English or U+9002 U+91CF in Chinese for to taste. Otherwise the
            quantity is first converted with ``in_base_unit`` and its amount is rounded up to a
            whole number. 1000 g or more is written in kg and 1000 ml or more in L, rounded up to
            at most two decimals. Any other amount is written as the whole number, a space, and
            the unit label. Numbers use ``.`` with no trailing zeros and no thousands separator.
            In English, the label is plural unless the written number is 1.

        Raises:
            ValueError: The rounded amount that is written has more than 4,300 digits before the
                point, Python's default limit on writing an ``int``, which
                ``PYTHONINTMAXSTRDIGITS`` can change.
        """
        base = self.in_base_unit()
        if base.amount is None or base.unit is None:
            return _TO_TASTE_TEXT[lang]
        whole = ceil(base.amount)
        if whole >= 1000 and base.unit in (Unit.G, Unit.ML):
            big = Unit.KG if base.unit is Unit.G else Unit.L
            return _with_label(ceil(Fraction(whole, 10)), big, lang)
        return _with_label(whole * 100, base.unit, lang)


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
