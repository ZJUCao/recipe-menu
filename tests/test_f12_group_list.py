"""Tests of F12 for ``ShoppingGroup`` and ``ShoppingList`` (T08 to T13)."""

import dataclasses
from fractions import Fraction
from types import SimpleNamespace

import pytest

from f12_support import amt, code_catalog, group
from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek
from recipe_menu.shopping import ShoppingGroup, ShoppingLine, ShoppingList
from recipe_menu.units import Quantity, Unit


def _group_values() -> SimpleNamespace:
    """Builds the values of the example of 2.3."""
    produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
    tomato = Ingredient(BiText("Tomato", "番茄"), produce)
    pork = Ingredient(BiText("Minced pork", "猪肉末"), meat)
    tomatoes = ShoppingLine(tomato, (amt("600 G"),))
    minced_pork = ShoppingLine(pork, (amt("100 G"),))
    return SimpleNamespace(
        produce=produce,
        meat=meat,
        tomato=tomato,
        tomatoes=tomatoes,
        minced_pork=minced_pork,
        group=ShoppingGroup(produce, (tomatoes,)),
    )


def _list_values() -> SimpleNamespace:
    """Builds the values of the example of 2.4."""
    staples = Category("staples", BiText("Rice, flour, and oil", "米面粮油"))
    rice = Ingredient(BiText("Rice", "大米"), staples)
    oil = Ingredient(BiText("Cooking oil", "食用油"), staples)
    rice_line = ShoppingLine(rice, (Quantity(Fraction(640), Unit.G),))
    return SimpleNamespace(
        staples=staples,
        rice=rice,
        oil=oil,
        rice_line=rice_line,
        group=ShoppingGroup(staples, (rice_line,)),
        week=IsoWeek(2026, 47),
    )


def test_f12_t08_the_example_of_shopping_group() -> None:
    """The lines of the example of 2.3 hold, and the four wrong groups raise their errors."""
    v = _group_values()
    assert v.group.category is v.produce
    assert v.group.lines == (v.tomatoes,)
    same_produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    assert ShoppingGroup(same_produce, (v.tomatoes,)) == v.group

    with pytest.raises(ValueError):
        ShoppingGroup(v.produce, ())
    with pytest.raises(ValueError):
        ShoppingGroup(v.produce, (v.tomatoes, v.minced_pork))
    with pytest.raises(ValueError):
        ShoppingGroup(v.produce, (v.tomatoes, v.tomatoes))
    with pytest.raises(TypeError):
        ShoppingGroup(v.produce, [v.tomatoes])  # type: ignore[arg-type]


def test_f12_t09_a_group_field_of_the_wrong_type_is_a_type_error() -> None:
    """A wrong type for the category, the tuple, or an item of it raises ``TypeError``."""
    v = _group_values()
    for wrong_category in ("produce", v.tomato, None):
        with pytest.raises(TypeError):
            ShoppingGroup(wrong_category, (v.tomatoes,))  # type: ignore[arg-type]
    for lines in ([v.tomatoes], v.tomatoes, (v.tomatoes, v.tomato), ((v.tomato, (amt("600 G"),)),)):
        with pytest.raises(TypeError):
            ShoppingGroup(v.produce, lines)  # type: ignore[arg-type]


def test_f12_t10_a_group_has_lines_of_its_category_and_keeps_their_order() -> None:
    """The group checks its lines, compares by equality, keeps the order, and is frozen."""
    v = _group_values()
    same_produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
    same_tomato = Ingredient(BiText("Tomato", "番茄"), same_produce)
    scallion = Ingredient(BiText("Scallion", "葱"), v.produce, Unit.STALK)
    scallions = ShoppingLine(scallion, (amt("5 STALK"),))
    copy_line = ShoppingLine(same_tomato, (amt("1 G"),))

    for category, lines in (
        (v.produce, ()),
        (v.produce, (v.tomatoes, v.minced_pork)),
        (v.produce, (v.tomatoes, v.tomatoes)),
        (v.produce, (v.tomatoes, copy_line)),
        (v.meat, (v.tomatoes,)),
    ):
        with pytest.raises(ValueError):
            ShoppingGroup(category, lines)

    first = ShoppingGroup(v.produce, (scallions, v.tomatoes))
    second = ShoppingGroup(v.produce, (v.tomatoes, scallions))
    third = ShoppingGroup(v.produce, (ShoppingLine(same_tomato, (amt("600 G"),)),))
    fourth = ShoppingGroup(same_produce, (v.tomatoes,))
    assert first.lines == (scallions, v.tomatoes)
    assert second.lines == (v.tomatoes, scallions)
    assert first != second
    for same in (third, fourth):
        assert same == v.group
        assert hash(same) == hash(v.group)
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.group.lines = ()  # type: ignore[misc]


def test_f12_t11_the_example_of_shopping_list() -> None:
    """The lines of the example of 2.4 hold, and the nine wrong lists raise their errors."""
    v = _list_values()
    shopping = ShoppingList(v.week, 4, 9, (v.group,), (v.oil,))
    assert shopping.groups[0].lines[0] is v.rice_line
    assert shopping.pantry_used == (v.oil,)
    assert shopping == ShoppingList(v.week, 4, 9, (v.group,), (v.oil,))
    empty = ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())
    assert (empty.meal_count, empty.dish_count, empty.groups) == (0, 0, ())
    assert ShoppingList(v.week, 1, 1, (), (v.oil,)).groups == ()

    with pytest.raises(TypeError):
        ShoppingList(v.week, 4, True, (v.group,), ())
    with pytest.raises(TypeError):
        ShoppingList(v.week, 4, 9, [v.group], ())  # type: ignore[arg-type]
    wrong = (
        (-1, 9, (v.group,), ()),
        (10, 9, (v.group,), ()),
        (0, 9, (v.group,), ()),
        (0, 0, (v.group,), ()),
        (4, 9, (v.group, v.group), ()),
        (4, 9, (v.group,), (v.rice,)),
        (4, 9, (v.group,), (v.oil, v.oil)),
    )
    for meals, dishes, groups, pantry in wrong:
        with pytest.raises(ValueError):
            ShoppingList(v.week, meals, dishes, groups, pantry)


def test_f12_t12_a_list_field_of_the_wrong_type_is_a_type_error() -> None:
    """A wrong type for a field raises ``TypeError``, and a ``bool`` is not a count."""
    v = _list_values()
    g = (v.group,)
    calls = [(w, 4, 9, g, ()) for w in ("2026-W47", (2026, 47))]
    calls += [(v.week, m, 9, g, ()) for m in (4.0, "4", True)]
    calls += [(v.week, 4, d, g, ()) for d in (9.0, Fraction(9), True)]
    calls += [(v.week, False, 0, (), ())]
    calls += [(v.week, 4, 9, groups, ()) for groups in ([v.group], v.group, (v.rice_line,))]
    calls += [
        (v.week, 4, 9, g, used)
        for used in ([v.oil], frozenset({v.oil}), ("食用油",), (v.rice_line,))
    ]
    for args in calls:
        with pytest.raises(TypeError):
            ShoppingList(*args)  # type: ignore[arg-type]


def test_f12_t13_a_list_checks_its_counts_and_keeps_the_order_of_its_groups() -> None:
    """The list checks counts, groups, and the pantry, compares by equality, and is frozen."""
    v = _list_values()
    catalog = code_catalog()
    same_staples = Category("staples", BiText("Rice, flour, and oil", "米面粮油"))
    same_rice = Ingredient(BiText("Rice", "大米"), same_staples)
    noodles = ShoppingLine(
        Ingredient(BiText("Noodles", "面条"), v.staples), (Quantity(Fraction(200), Unit.G),)
    )
    other = ShoppingGroup(same_staples, (noodles,))
    g, o, r = (v.group,), (v.oil,), (v.rice,)
    wrong = (
        (-1, 9, g, ()),
        (0, -1, (), ()),
        (-1, -1, (), ()),
        (10, 9, g, ()),
        (2, 1, (), ()),
        (0, 9, g, ()),
        (0, 1, (), ()),
        (0, 0, g, ()),
        (0, 0, (), o),
        (4, 9, (v.group, v.group), ()),
        (4, 9, (v.group, other), ()),
        (4, 9, g, (v.oil, v.oil)),
        (4, 9, g, r),
        (4, 9, g, (same_rice,)),
    )
    for meals, dishes, groups, pantry in wrong:
        with pytest.raises(ValueError):
            ShoppingList(v.week, meals, dishes, groups, pantry)

    pepper = group(catalog, "seasonings", "白胡椒粉:")
    for meals, dishes, groups, pantry in ((9, 9, g, ()), (1, 1, (), ()), (1, 1, (), o)):
        s = ShoppingList(v.week, meals, dishes, groups, pantry)
        assert (s.week, s.meal_count, s.dish_count, s.groups, s.pantry_used) == (
            (v.week, meals, dishes, groups, pantry)
        )
    shopping = ShoppingList(v.week, 21, 63, (pepper, v.group), o)
    assert shopping.week == v.week
    assert (shopping.meal_count, shopping.dish_count) == (21, 63)
    assert shopping.groups == (pepper, v.group)
    assert shopping.pantry_used == o
    again = ShoppingList(v.week, 21, 63, (pepper, v.group), o)
    assert again == shopping
    assert hash(again) == hash(shopping)
    assert ShoppingList(IsoWeek(2026, 48), 21, 63, (pepper, v.group), o) != shopping
    assert ShoppingList(v.week, 21, 63, (v.group, pepper), o) != shopping
    example = ShoppingList(v.week, 4, 9, g, o)
    with pytest.raises(dataclasses.FrozenInstanceError):
        example.dish_count = 0  # type: ignore[misc]
