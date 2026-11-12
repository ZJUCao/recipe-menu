"""Tests of F05 for Meal and Settings (T01 to T03)."""

from fractions import Fraction

import pytest

from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import and_list


def test_f05_t01_meal_names_order_and_words() -> None:
    """The design's example: labels, headings, the order of a day, and the words of the files."""
    assert Meal.BREAKFAST.label == BiText("breakfast", "早餐")
    assert Meal.BREAKFAST.heading == BiText("Breakfast", "早餐")
    assert Meal.LUNCH.label == BiText("lunch", "午餐")
    assert Meal.LUNCH.heading == BiText("Lunch", "午餐")
    assert Meal.DINNER.label == BiText("dinner", "晚餐")
    assert Meal.DINNER.heading == BiText("Dinner", "晚餐")
    two = and_list(meal.label for meal in (Meal.LUNCH, Meal.DINNER))
    assert two == BiText("lunch and dinner", "午餐和晚餐")
    every = and_list(meal.label for meal in Meal)
    assert every == BiText("breakfast, lunch, and dinner", "早餐、午餐和晚餐")
    assert list(Meal) == [Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER]
    assert Meal("lunch") is Meal.LUNCH
    assert "dinner" in Meal
    assert "supper" not in Meal
    assert "Lunch" not in Meal
    assert sorted(Meal) == [Meal.BREAKFAST, Meal.DINNER, Meal.LUNCH]
    by_day = sorted([Meal.DINNER, Meal.BREAKFAST], key=list(Meal).index)
    assert by_day == [Meal.BREAKFAST, Meal.DINNER]
    for word in ("supper", "Lunch", "午餐"):
        with pytest.raises(ValueError):
            Meal(word)


def test_f05_t02_settings_accept_and_reject_meals_and_servings() -> None:
    """Settings keep their fields, compare equal, and reject empty or unordered meals."""
    defaults = Settings()
    assert defaults.language is None
    assert defaults.meals == (Meal.LUNCH, Meal.DINNER)
    assert defaults.servings == 2
    every = Settings(Lang.ZH, tuple(Meal), 3)
    assert every.meals == (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER)
    assert every.language is Lang.ZH
    assert every.servings == 3
    same = Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2)
    assert same == Settings(Lang.EN)
    assert hash(same) == hash(Settings(Lang.EN))
    assert Settings(meals=(Meal.DINNER,)).meals == (Meal.DINNER,)
    assert Settings(meals=(Meal.BREAKFAST, Meal.DINNER)).meals == (Meal.BREAKFAST, Meal.DINNER)
    assert Settings(servings=1).servings == 1
    assert Settings(servings=100).servings == 100
    bad_meals = [
        (),
        (Meal.DINNER, Meal.LUNCH),
        (Meal.LUNCH, Meal.LUNCH),
        (Meal.DINNER, Meal.BREAKFAST),
        (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER, Meal.DINNER),
    ]
    for meals in bad_meals:
        with pytest.raises(ValueError):
            Settings(meals=meals)
    for servings in (0, 101, -1):
        with pytest.raises(ValueError):
            Settings(servings=servings)


def test_f05_t03_settings_reject_values_of_a_wrong_type() -> None:
    """A text for a language or a meal, and a bool, a float, or a text for servings, are wrong."""
    for language in ("zh", "en", 1):
        with pytest.raises(TypeError):
            Settings(language=language)  # type: ignore[arg-type]
    meals_values = [[Meal.LUNCH], "lunch", None, ("lunch",), (Meal.LUNCH, "dinner"), (Lang.EN,)]
    for meals in meals_values:
        with pytest.raises(TypeError):
            Settings(meals=meals)  # type: ignore[arg-type]
    for servings in (True, False, 2.0, "2", None, Fraction(2)):
        with pytest.raises(TypeError):
            Settings(servings=servings)  # type: ignore[arg-type]
