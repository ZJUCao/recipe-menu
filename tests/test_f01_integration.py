"""Integration tests of F01 across several interfaces (F01-T48 to F01-T53)."""

from fractions import Fraction

from f01_support import q, same
from recipe_menu.lang import Lang
from recipe_menu.units import (
    Quantity,
    Unit,
    WrongQuantity,
    add_quantities,
    parse_quantity,
)

EN, ZH = Lang.EN, Lang.ZH

TOMATO_EGG: list[tuple[str, Unit | None]] = [
    ("300 g", None),
    ("3", Unit.PIECE),
    ("1 根", None),
    ("适量", None),
    ("1 tsp", None),
    ("2 tbsp", None),
]


def read(text: str, default: Unit | None = None) -> Quantity:
    """Reads an amount text that must be valid.

    Args:
        text: The amount text.
        default: The default unit.

    Returns:
        The quantity.
    """
    result = parse_quantity(text, default)
    assert not isinstance(result, WrongQuantity)
    return result


def sums(items: list[tuple[str, Unit | None, int]]) -> tuple[Quantity, ...]:
    """Reads, scales, and adds the amounts of one ingredient.

    Args:
        items: Each amount text, its default unit, and the servings of its dish. Every
            recipe serves 2, so each amount is scaled by ``servings / 2``.

    Returns:
        The sums.
    """
    return add_quantities(read(t, d).scale(Fraction(s, 2)) for t, d, s in items)


def test_f01_t48_recipes_are_read_and_written_in_english() -> None:
    """The recipes of the F09 sections read and write their quantities in English."""
    tomato_egg = ["300 g", "3 pieces", "1 stalk", "to taste", "1 tsp", "2 tbsp"]
    for (text, default), expected in zip(TOMATO_EGG, tomato_egg, strict=True):
        assert read(text, default).to_text(EN) == expected
    pork = [("1 斤", "1 jin"), ("30 g", "30 g"), ("2 tbsp", "2 tbsp")]
    pork += [("3 片", "3 slices"), ("2 根", "2 stalks")]
    for text, expected in pork:
        assert read(text).to_text(EN) == expected


def test_f01_t49_tomato_egg_for_four_servings_in_chinese() -> None:
    """The amounts of tomato-egg are scaled at 4 and written in the recipe's own units."""
    expected = ["600 g", "6 个", "2 根", "适量", "2 茶匙", "4 汤匙"]
    for (text, default), want in zip(TOMATO_EGG, expected, strict=True):
        assert read(text, default).scale(Fraction(4, 2)).to_text(ZH) == want


def test_f01_t50_week_adds_up_to_the_lines_of_f13() -> None:
    """The week 2026-W47 adds up to the lines of the F13 sections."""
    piece = Unit.PIECE
    ingredients: list[list[tuple[str, Unit | None, int]]] = [
        [("300 g", None, 2), ("300 g", None, 2)],
        [("1 斤", None, 2), ("1 斤", None, 4)],
        [("1 根", None, 2)] * 3 + [("1 根", None, 4)],
        [("3 片", None, 4)],
        [("3 瓣", None, 2), ("3 瓣", None, 4), ("2 瓣", None, 2)],
        [("100 g", None, 2)],
        [("500 g", None, 4)],
        [("3", piece, 2), ("2", piece, 2)],
        [("1 块", None, 2)],
        [("160 g", None, 2), ("160 g", None, 2), ("160 g", None, 4)],
        [("200 g", None, 2)],
        [("1 tbsp", None, 2)],
        [("1 罐", None, 4)],
    ]
    pepper = [("适量", None, 2)]
    assert sums(pepper) == ()
    en = ["600 g", "1.5 kg", "5 stalks", "6 slices", "11 cloves", "100 g", "1 kg", "5 pieces"]
    en += ["1 block", "640 g", "200 g", "15 ml", "2 cans"]
    zh = ["600 g", "1.5 kg", "5 根", "6 片", "11 瓣", "100 g", "1 kg", "5 个", "1 块", "640 g"]
    zh += ["200 g", "15 ml", "2 罐"]
    for items, want_en, want_zh in zip(ingredients, en, zh, strict=True):
        result = sums(items)
        assert len(result) == 1
        assert result[0].to_rounded_text(EN) == want_en
        assert result[0].to_rounded_text(ZH) == want_zh


def test_f01_t51_quantities_that_cannot_be_added_stay_side_by_side() -> None:
    """The dinners of 2026-W48 keep quantities of different groups side by side."""
    scallion = sums([("2 根", None, 2)] + [("1 根", None, 2)] * 3 + [("1 把", None, 2)])
    assert len(scallion) == 2
    same(scallion[0], q(5, Unit.STALK))
    same(scallion[1], q(1, Unit.BUNCH))
    assert [s.to_rounded_text(EN) for s in scallion] == ["5 stalks", "1 bunch"]
    assert [s.to_rounded_text(ZH) for s in scallion] == ["5 根", "1 把"]
    soy = sums([("2 tbsp", None, 2), ("10 g", None, 2)])
    assert len(soy) == 2
    same(soy[0], q(30, Unit.ML))
    same(soy[1], q(10, Unit.G))
    for lang in (EN, ZH):
        assert [s.to_rounded_text(lang) for s in soy] == ["30 ml", "10 g"]


def test_f01_t52_three_servings_round_up_to_what_you_buy() -> None:
    """Three servings of a 2-serving recipe round up."""
    expected = ["450 g", "5 pieces", "2 stalks"]
    for text, default, want in [
        ("300 g", None, expected[0]),
        ("3", Unit.PIECE, expected[1]),
        ("1 根", None, expected[2]),
    ]:
        total = add_quantities([read(text, default).scale(Fraction(3, 2))])
        assert len(total) == 1
        assert total[0].to_rounded_text(EN) == want


def test_f01_t53_amounts_stay_exact_from_text_to_sum() -> None:
    """Amounts stay exact from the text to the written sum."""
    total = add_quantities([read("0.1 kg")] * 3)
    assert len(total) == 1
    same(total[0], q(300, Unit.G))
    assert total[0].to_rounded_text(EN) == "300 g"
    assert read("1.1 kg").to_rounded_text(EN) == "1.1 kg"
