"""Tests of F06 for Day, Dish, MealSlot, and WeekMenu (T14 to T18)."""

import pytest

from f06_support import dishes_of
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, MealSlot, WeekMenu, short_date
from recipe_menu.settings import Meal

LABELS = (
    ("monday", "Monday", "周一", "Mon"),
    ("tuesday", "Tuesday", "周二", "Tue"),
    ("wednesday", "Wednesday", "周三", "Wed"),
    ("thursday", "Thursday", "周四", "Thu"),
    ("friday", "Friday", "周五", "Fri"),
    ("saturday", "Saturday", "周六", "Sat"),
    ("sunday", "Sunday", "周日", "Sun"),
)


def test_f06_t14_the_days_have_their_labels_in_the_order_of_a_week() -> None:
    """The design's example of 2.3, the labels, the order, and the words that are no day."""
    assert len(Day) == 7
    assert next(iter(Day)) is Day.MONDAY
    assert list(Day)[-1] is Day.SUNDAY
    assert Day("sunday") is Day.SUNDAY
    assert "friday" in Day
    assert "Friday" not in Day
    assert Day.MONDAY.label == BiText("Monday", "周一")
    assert Day.SUNDAY.label == BiText("Sunday", "周日")
    assert sorted(Day)[0] is Day.FRIDAY
    with pytest.raises(ValueError):
        Day("funday")
    with pytest.raises(ValueError):
        Day("Monday")

    members = list(Day)
    assert [member.value for member in members] == [row[0] for row in LABELS]
    week = IsoWeek(2026, 47)
    for index, (value, en, zh, short) in enumerate(LABELS):
        member = Day(value)
        assert member is members[index]
        assert member.label == BiText(en, zh)
        dated = short_date(week.dates[index])
        assert dated.get(Lang.ZH).startswith(f"{zh} ")
        assert dated.get(Lang.EN).startswith(f"{short} ")
    assert "周五" not in Day
    assert sorted(Day, key=members.index) == members
    for word in ("funday", "Monday", "MONDAY", "mon", "周一", ""):
        with pytest.raises(ValueError):
            Day(word)


def test_f06_t15_a_dish_keeps_a_recipe_id_and_servings_from_1_to_100() -> None:
    """The design's example of 2.4, and every wrong ID, servings, and type."""
    dish = Dish("cola-wings", 4)
    assert dish.recipe_id == "cola-wings"
    assert dish.servings == 4
    assert dish == Dish("cola-wings", 4)
    with pytest.raises(TypeError):
        Dish(3, 4)
    with pytest.raises(ValueError):
        Dish("Cola-Wings", 4)
    with pytest.raises(ValueError):
        Dish("cola-wings", 0)
    with pytest.raises(ValueError):
        Dish("cola-wings", 101)
    with pytest.raises(TypeError):
        Dish("cola-wings", True)

    for recipe, servings in (("rice", 1), ("tomato-egg-noodles", 100), ("2-minute-noodles", 2)):
        kept = Dish(recipe, servings)
        assert (kept.recipe_id, kept.servings) == (recipe, servings)
    for args in (
        (None, 2),
        (b"rice", 2),
        ("rice", False),
        ("rice", 2.0),
        ("rice", "2"),
        ("rice", None),
    ):
        with pytest.raises(TypeError):
            Dish(*args)
    for args in (
        ("", 2),
        (" rice", 2),
        ("rice ", 2),
        ("con", 2),
        ("rice.toml", 2),
        ("-rice", 2),
        ("rice", -1),
        ("rice", 0),
    ):
        with pytest.raises(ValueError):
            Dish(*args)
    assert len({Dish("rice", 2), Dish("rice", 2)}) == 1
    assert Dish("rice", 2) != Dish("rice", 3)


def test_f06_t16_a_slot_keeps_its_day_its_meal_and_its_dishes_in_order() -> None:
    """The design's example of 2.5, a dish that appears twice, and every wrong type."""
    slot = MealSlot(Day.TUESDAY, Meal.DINNER, (Dish("mapo-tofu", 2), Dish("rice", 2)))
    assert [dish.recipe_id for dish in slot.dishes] == ["mapo-tofu", "rice"]
    assert MealSlot(Day.WEDNESDAY, Meal.LUNCH).dishes == ()
    with pytest.raises(TypeError):
        MealSlot(Day.TUESDAY, Meal.DINNER, [Dish("rice", 2)])
    with pytest.raises(TypeError):
        MealSlot("tuesday", Meal.DINNER)

    twice = MealSlot(Day.SUNDAY, Meal.BREAKFAST, (Dish("rice", 2), Dish("rice", 2)))
    assert twice.dishes == (Dish("rice", 2), Dish("rice", 2))
    rice = Dish("rice", 2)
    for args in (
        (Day.TUESDAY, "dinner"),
        (Meal.DINNER, Day.TUESDAY),
        (Day.TUESDAY, Meal.DINNER, (rice, "rice")),
        (Day.TUESDAY, Meal.DINNER, (None,)),
        (Day.TUESDAY, Meal.DINNER, None),
        (Day.TUESDAY, Meal.DINNER, rice),
    ):
        with pytest.raises(TypeError):
            MealSlot(*args)
    assert Day.TUESDAY == "tuesday"
    first = MealSlot(Day.MONDAY, Meal.LUNCH, (rice,))
    second = MealSlot(Day.MONDAY, Meal.LUNCH, (rice,))
    assert first == second
    assert hash(first) == hash(second)


def test_f06_t17_a_week_menu_checks_its_week_its_meals_and_its_slots() -> None:
    """The design's example of 2.6 and every row of its Errors table."""
    week48 = IsoWeek(2026, 48)
    meals = (Meal.LUNCH, Meal.DINNER)
    friday_dinner = (Dish("rice", 2),)
    slots = tuple(
        MealSlot(day, meal, friday_dinner if day is Day.FRIDAY and meal is Meal.DINNER else ())
        for day in Day
        for meal in meals
    )
    menu = WeekMenu(week48, meals, slots)
    assert len(menu.slots) == 14
    assert menu.slots[0] == MealSlot(Day.MONDAY, Meal.LUNCH)
    assert menu.dishes(Day.FRIDAY, Meal.DINNER) == friday_dinner
    assert menu.dishes(Day.MONDAY, Meal.LUNCH) == ()
    assert sum(1 for slot in menu.slots if slot.dishes) == 1
    with pytest.raises(ValueError):
        WeekMenu(week48, meals, slots[:-1])
    with pytest.raises(ValueError):
        WeekMenu(week48, (Meal.DINNER, Meal.LUNCH), slots)
    with pytest.raises(ValueError):
        menu.dishes(Day.MONDAY, Meal.BREAKFAST)

    for args in (
        ("2026-W48", meals, slots),
        ((2026, 48), meals, slots),
        (week48, list(meals), slots),
        (week48, ("lunch", "dinner"), slots),
        (week48, meals, list(slots)),
    ):
        with pytest.raises(TypeError):
            WeekMenu(*args)
    for args in (
        (week48, (), ()),
        (week48, (Meal.LUNCH, Meal.LUNCH), slots),
        (week48, meals, slots + slots[-1:]),
        (week48, meals, slots[1:] + slots[:1]),
        (week48, meals, (slots[1], slots[0], *slots[2:])),
        (week48, meals, slots[2:4] + slots[:2] + slots[4:]),
        (week48, meals, (MealSlot(Day.MONDAY, Meal.BREAKFAST), *slots[1:])),
        (week48, (Meal.DINNER,), slots),
        (week48, tuple(Meal), slots),
    ):
        with pytest.raises(ValueError):
            WeekMenu(*args)
    with pytest.raises((TypeError, ValueError)):
        WeekMenu(week48, meals, (*slots[:-1], None))
    with pytest.raises(ValueError):
        menu.dishes(Day.SUNDAY, Meal.BREAKFAST)


def test_f06_t18_a_menu_of_one_two_or_three_meals_holds_seven_slots_for_each() -> None:
    """``dishes`` gives each slot's dishes, and menus with equal fields are equal."""
    week = IsoWeek(2026, 53)
    for meals, count in (
        ((Meal.DINNER,), 7),
        ((Meal.LUNCH, Meal.DINNER), 14),
        ((Meal.BREAKFAST, Meal.DINNER), 14),
        (tuple(Meal), 21),
    ):
        slots = tuple(
            MealSlot(day, meal, dishes_of(("rice", number)))
            for number, (day, meal) in enumerate(
                ((day, meal) for day in Day for meal in meals), start=1
            )
        )
        menu = WeekMenu(week, meals, slots)
        assert len(menu.slots) == count
        number = 0
        for day in Day:
            for meal in meals:
                number += 1
                assert menu.dishes(day, meal) == (Dish("rice", number),)
        assert menu.dishes(Day.SUNDAY, meals[-1]) == (Dish("rice", 7 * len(meals)),)
        for other in Meal:
            if other not in meals:
                with pytest.raises(ValueError):
                    menu.dishes(Day.SUNDAY, other)
        same = WeekMenu(week, meals, slots)
        assert same == menu
        assert hash(same) == hash(menu)
        assert WeekMenu(IsoWeek(2026, 52), meals, slots) != menu
