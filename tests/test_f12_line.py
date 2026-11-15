"""Tests of F12 for ``ShoppingLine`` and ``ShoppingLine.amount_text`` (T01 to T07)."""

import dataclasses
from fractions import Fraction

import pytest

from f12_support import EN, ZH, amt, category, code_catalog, copy_of, find, line_of
from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.shopping import ShoppingLine
from recipe_menu.units import TO_TASTE, Quantity, Unit

TEN = (
    "1500 G",
    "1000 ML",
    "1 PIECE",
    "3/2 STALK",
    "3 CLOVE",
    "6 SLICE",
    "1 BLOCK",
    "2 BUNCH",
    "2 CAN",
    "1 PACK",
)
TEN_EN = (
    "1.5 kg + 1 L + 1 piece + 2 stalks + 3 cloves + 6 slices + 1 block + 2 bunches + 2 cans"
    " + 1 pack"
)
TEN_ZH = "1.5 kg + 1 L + 1 个 + 2 根 + 3 瓣 + 6 片 + 1 块 + 2 把 + 2 罐 + 1 包"
TEN_EN_REVERSED = (
    "1 pack + 2 cans + 2 bunches + 1 block + 6 slices + 3 cloves + 2 stalks + 1 piece + 1 L"
    " + 1.5 kg"
)
TEN_ZH_REVERSED = "1 包 + 2 罐 + 2 把 + 1 块 + 6 片 + 3 瓣 + 2 根 + 1 个 + 1 L + 1.5 kg"
# Each row: ingredient name, amounts, English text, Chinese text.
TEXTS = (
    ("葱", "", "to taste", "适量"),
    ("番茄", "1/10 G", "1 g", "1 g"),
    ("番茄", "999 G", "999 g", "999 g"),
    ("番茄", "1999/2 G", "1 kg", "1 kg"),
    ("番茄", "1000 G", "1 kg", "1 kg"),
    ("番茄", "1001 G", "1.01 kg", "1.01 kg"),
    ("番茄", "12345 G", "12.35 kg", "12.35 kg"),
    ("生抽", "2/3 ML", "1 ml", "1 ml"),
    ("生抽", "999 ML", "999 ml", "999 ml"),
    ("生抽", "1500 ML", "1.5 L", "1.5 L"),
    ("生抽", "1001 ML", "1.01 L", "1.01 L"),
    ("鸡蛋", "1 PIECE", "1 piece", "1 个"),
    ("鸡蛋", "1/3 PIECE", "1 piece", "1 个"),
    ("葱", "3/2 STALK", "2 stalks", "2 根"),
    ("葱", "1 BUNCH", "1 bunch", "1 把"),
    ("葱", "2 BUNCH", "2 bunches", "2 把"),
    ("葱", "5 STALK, 1 BUNCH", "5 stalks + 1 bunch", "5 根 + 1 把"),
    ("葱", "100 G", "100 g", "100 g"),
    ("生抽", "30 ML, 10 G", "30 ml + 10 g", "30 ml + 10 g"),
    ("生抽", "10 G, 30 ML", "10 g + 30 ml", "10 g + 30 ml"),
)


def _scallion() -> Ingredient:
    """Builds the scallion of the example of 2.1, with its own category."""
    produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    return Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)


def test_f12_t01_the_example_of_shopping_line() -> None:
    """The lines of the example of 2.1 hold, and the five wrong lines raise their errors."""
    seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
    scallion = _scallion()
    soy_sauce = Ingredient(BiText("Soy sauce", "生抽"), seasonings)
    white_pepper = Ingredient(BiText("White pepper", "白胡椒粉"), seasonings)
    stalks = Quantity(Fraction(5), Unit.STALK)
    bunch = Quantity(Fraction(1), Unit.BUNCH)
    grams = Quantity(Fraction(10), Unit.G)

    shopping = ShoppingLine(scallion, (stalks, bunch))
    assert shopping.ingredient is scallion
    assert shopping.amounts == (stalks, bunch)
    assert shopping == ShoppingLine(scallion, (stalks, bunch))
    assert ShoppingLine(white_pepper, ()).amounts == ()
    soy = ShoppingLine(soy_sauce, (Quantity(Fraction(30), Unit.ML), grams))
    assert soy.amounts[1].unit is Unit.G

    with pytest.raises(ValueError):
        ShoppingLine(soy_sauce, (Quantity(Fraction(2), Unit.TBSP),))
    with pytest.raises(ValueError):
        ShoppingLine(soy_sauce, (grams, grams))
    with pytest.raises(ValueError):
        ShoppingLine(white_pepper, (TO_TASTE,))
    with pytest.raises(TypeError):
        ShoppingLine(scallion, [stalks, bunch])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ShoppingLine("Scallion", (stalks,))  # type: ignore[arg-type]


def test_f12_t02_a_line_keeps_its_amounts_and_writes_them_in_order() -> None:
    """A line keeps ten kinds in order, equal lines are equal, and ``amount_text`` joins them."""
    scallion = _scallion()
    a = ShoppingLine(scallion, tuple(amt(text) for text in TEN))
    b = ShoppingLine(scallion, tuple(amt(text) for text in reversed(TEN)))
    c = ShoppingLine(copy_of(scallion), tuple(amt(text) for text in TEN))
    assert c.ingredient is not scallion
    empty = ShoppingLine(scallion, ())
    one = ShoppingLine(scallion, (amt("1500 G"),))
    garlic = Ingredient(BiText("Garlic", "大蒜"), scallion.category, Unit.CLOVE)
    other = ShoppingLine(garlic, (amt("1500 G"),))

    assert a.ingredient is scallion
    assert a.amounts == tuple(amt(text) for text in TEN)
    assert empty.amounts == ()
    assert c == a
    assert hash(c) == hash(a)
    assert b != a
    assert one != other
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.amounts = ()  # type: ignore[misc]
    assert a.amount_text(EN) == TEN_EN
    assert a.amount_text(ZH) == TEN_ZH
    assert b.amount_text(EN) == TEN_EN_REVERSED
    assert b.amount_text(ZH) == TEN_ZH_REVERSED


def test_f12_t03_a_field_of_the_wrong_type_is_a_type_error() -> None:
    """A wrong type for the ingredient, the tuple, or an item of it raises ``TypeError``."""
    catalog = code_catalog()
    scallion = find(catalog, "葱")
    stalks, bunch = amt("5 STALK"), amt("1 BUNCH")
    for ingredient in ("Scallion", None, category(catalog, "produce")):
        with pytest.raises(TypeError):
            ShoppingLine(ingredient, (stalks,))  # type: ignore[arg-type]
    for amounts in ([stalks, bunch], stalks, None):
        with pytest.raises(TypeError):
            ShoppingLine(scallion, amounts)  # type: ignore[arg-type]
    for item in ("1 bunch", Fraction(1), None):
        with pytest.raises(TypeError):
            ShoppingLine(scallion, (stalks, item))  # type: ignore[arg-type]


def test_f12_t04_amounts_hold_only_grams_millilitres_and_each_count_unit_once() -> None:
    """To taste, another unit, or a unit twice in ``amounts`` raises ``ValueError``."""
    soy_sauce = find(code_catalog(), "生抽")
    to_taste = (
        (TO_TASTE,),
        (Quantity(None, None),),
        (amt("5 STALK"), TO_TASTE),
    )
    other_units = (
        (amt("1 KG"),),
        (amt("1 JIN"),),
        (amt("1 LIANG"),),
        (amt("1 L"),),
        (amt("1 TSP"),),
        (amt("2 TBSP"),),
        (amt("10 G"), amt("1 KG")),
    )
    twice = (
        (amt("10 G"), amt("10 G")),
        (amt("10 G"), amt("30 ML"), amt("5 G")),
        (amt("1 STALK"), amt("1 BUNCH"), amt("2 STALK")),
        (amt("1 PIECE"), amt("1 PIECE")),
    )
    for amounts in (*to_taste, *other_units, *twice):
        with pytest.raises(ValueError):
            ShoppingLine(soy_sauce, amounts)


def test_f12_t05_the_example_of_amount_text() -> None:
    """The ``amount_text`` lines of the example of 2.2 hold."""
    produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
    scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
    choy_sum = Ingredient(BiText("Choy sum", "菜心"), produce)
    soy_sauce = Ingredient(BiText("Soy sauce", "生抽"), seasonings)
    white_pepper = Ingredient(BiText("White pepper", "白胡椒粉"), seasonings)
    five = Quantity(Fraction(5), Unit.STALK)
    bunch = Quantity(Fraction(1), Unit.BUNCH)
    half = Quantity(Fraction(3, 2), Unit.STALK)
    kilo = Quantity(Fraction(1500), Unit.G)
    grams = Quantity(Fraction(1001), Unit.G)
    ml = Quantity(Fraction(30), Unit.ML)
    soy_grams = Quantity(Fraction(10), Unit.G)

    scallion_line = ShoppingLine(scallion, (five, bunch))
    assert scallion_line.amount_text(EN) == "5 stalks + 1 bunch"
    assert scallion_line.amount_text(ZH) == "5 根 + 1 把"
    assert ShoppingLine(scallion, (half,)).amount_text(EN) == "2 stalks"
    assert ShoppingLine(choy_sum, (kilo,)).amount_text(ZH) == "1.5 kg"
    assert ShoppingLine(choy_sum, (grams,)).amount_text(EN) == "1.01 kg"
    assert ShoppingLine(soy_sauce, (ml, soy_grams)).amount_text(ZH) == "30 ml + 10 g"
    assert ShoppingLine(white_pepper, ()).amount_text(EN) == "to taste"
    assert ShoppingLine(white_pepper, ()).amount_text(ZH) == "适量"


def test_f12_t06_the_text_follows_the_rules_of_the_shopping_list() -> None:
    """Rounding up, kg and L, plural labels, to taste, and the join are right in both languages."""
    catalog = code_catalog()
    for name, amounts, english, chinese in TEXTS:
        shopping = line_of(catalog, f"{name}: {amounts}")
        assert shopping.amount_text(EN) == english, (name, amounts)
        assert shopping.amount_text(ZH) == chinese, (name, amounts)


def test_f12_t07_an_amount_of_more_than_4300_digits_is_a_value_error(
    default_int_limit: None,
) -> None:
    """4,300 digits are written in full, and 4,301 digits raise ``ValueError`` at any place."""
    catalog = code_catalog()
    egg, tomato, soy = (find(catalog, name) for name in ("鸡蛋", "番茄", "生抽"))
    grams = amt("1 G")
    nines = Quantity(Fraction(10**4300 - 1), Unit.PIECE)
    over = Quantity(Fraction(10**4300), Unit.PIECE)

    assert ShoppingLine(egg, (nines,)).amount_text(EN) == "9" * 4300 + " pieces"
    big = ShoppingLine(tomato, (Quantity(Fraction(10**4300), Unit.G),))
    assert big.amount_text(EN) == "1" + "0" * 4297 + " kg"
    assert ShoppingLine(egg, (grams, nines)).amount_text(ZH) == "1 g + " + "9" * 4300 + " 个"

    wrong = (
        ShoppingLine(egg, (over,)),
        ShoppingLine(egg, (grams, over)),
        ShoppingLine(tomato, (Quantity(Fraction(10**4303), Unit.G),)),
        ShoppingLine(soy, (Quantity(Fraction(10**4303), Unit.ML), grams)),
    )
    for shopping in wrong:
        for lang in (EN, ZH):
            with pytest.raises(ValueError):
                shopping.amount_text(lang)
