"""The checks of the days, the meals, and the dishes of a menu file."""

from collections.abc import Mapping
from dataclasses import dataclass

from recipe_menu.datafile import (
    EMPTY_ITEM,
    NOT_A_LIST,
    UNKNOWN_KEY,
    Report,
    read_servings,
    read_text,
    report_unknown_keys,
)
from recipe_menu.lang import BiText
from recipe_menu.menus._model import Day, Dish
from recipe_menu.menus.messages import (
    DAY_KEY,
    DAY_MEAL,
    DISH_N,
    NOT_A_DAY_TABLE,
    NOT_A_DISH,
    UNKNOWN_MEAL,
    UNKNOWN_RECIPE,
)
from recipe_menu.recipes import is_recipe_id
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import and_list

_DISH_KEYS = ("recipe", "servings")


@dataclass(frozen=True, slots=True)
class DayReader:
    """What the checks of the days need: the settings, the known recipes, and the report.

    Attributes:
        settings: The settings, or ``None`` when they could not be read.
        recipe_ids: The recipe IDs that a dish may name.
        report: Where the problems go.
    """

    settings: Settings | None
    recipe_ids: frozenset[str]
    report: Report

    @property
    def meals(self) -> tuple[Meal, ...]:
        """Gives the meals in use: the settings' meals, or every meal with no settings.

        Returns:
            The meals, in the order of ``Meal``.
        """
        return self.settings.meals if self.settings is not None else tuple(Meal)

    def read_day(self, day: Day, value: object) -> dict[Meal, tuple[Dish, ...]]:
        """Checks one day of the file.

        Args:
            day: The day.
            value: The value of the day's key.

        Returns:
            The dishes of each meal in use that the day names. Empty after a problem of the day.
        """
        if not isinstance(value, dict):
            self.report.add(day.label, NOT_A_DAY_TABLE, key=day.value)
            return {}
        found: dict[Meal, tuple[Dish, ...]] = {}
        for key, items in value.items():
            if key in Meal and Meal(key) in self.meals:
                found[Meal(key)] = self._read_meal(day, Meal(key), items)
            else:
                self._report_unknown(day, key, items)
        return found

    def _report_unknown(self, day: Day, key: str, items: object) -> None:
        """Reports a key of a day that names no meal in use.

        Args:
            day: The day.
            key: The key.
            items: The value of the key.
        """
        if self.settings is None:
            keys = and_list([meal.value for meal in Meal])
            place = _key_place(day, key)
            self.report.add(place, UNKNOWN_KEY.pick(len(Meal)), key=key, keys=keys)
        elif not (key in Meal and items == []):
            place = _key_place(day, key)
            meals = and_list([meal.value for meal in self.settings.meals])
            self.report.add(place, UNKNOWN_MEAL, meal=key, meals=meals)

    def _read_meal(self, day: Day, meal: Meal, items: object) -> tuple[Dish, ...]:
        """Checks the list of dishes of one meal.

        Args:
            day: The day.
            meal: The meal.
            items: The value of the meal's key.

        Returns:
            The valid dishes, in the file's order.
        """
        place = DAY_MEAL.to_bitext(day=day.label, meal=meal.label)
        if not isinstance(items, list):
            self.report.add(place, NOT_A_LIST, key=meal.value)
            return ()
        dishes = (self._read_dish(place, number, item) for number, item in enumerate(items, 1))
        return tuple(dish for dish in dishes if dish is not None)

    def _read_dish(self, meal_place: BiText, number: int, item: object) -> Dish | None:
        """Checks one item of a meal's list.

        Args:
            meal_place: The place of the meal.
            number: The number of the item in the list, from 1.
            item: The item.

        Returns:
            The dish, or ``None`` after a problem.
        """
        place = DISH_N.to_bitext(place=meal_place, number=number)
        if isinstance(item, str):
            recipe = item.strip()
            if not recipe:
                self.report.add(place, EMPTY_ITEM)
                return None
            return self._make_dish(meal_place, recipe, self._default_servings())
        if isinstance(item, dict):
            return self._read_dish_table(meal_place, place, item)
        self.report.add(place, NOT_A_DISH)
        return None

    def _read_dish_table(
        self, meal_place: BiText, place: BiText, item: Mapping[str, object]
    ) -> Dish | None:
        """Checks a dish that is a table in braces.

        The problems of the recipe come first, then those of the servings, then the unknown keys.

        Args:
            meal_place: The place of the meal.
            place: The place of the dish.
            item: The table.

        Returns:
            The dish, or ``None`` after a problem.
        """
        recipe = read_text(item, "recipe", place, self.report)
        known = recipe is not None and self._is_known(meal_place, recipe)
        servings: int | None = self._default_servings()
        if "servings" in item:
            servings = read_servings(item["servings"], place, self.report)
        report_unknown_keys(item, _DISH_KEYS, place, self.report)
        if recipe is None or not known or servings is None:
            return None
        return Dish(recipe, servings)

    def _default_servings(self) -> int:
        """Gives the servings of a dish that names none.

        Returns:
            The settings' servings. With no settings, 1, which no menu holds.
        """
        return self.settings.servings if self.settings is not None else 1

    def _is_known(self, meal_place: BiText, recipe: str) -> bool:
        """Checks a recipe ID against the rule and the known recipes.

        Args:
            meal_place: The place of the meal, where ``UNKNOWN_RECIPE`` goes.
            recipe: The ID without whitespace at both ends.

        Returns:
            ``True`` when the ID follows ``is_recipe_id`` and is in the known recipes. Otherwise
            ``False``, after the error ``UNKNOWN_RECIPE``.
        """
        if is_recipe_id(recipe) and recipe in self.recipe_ids:
            return True
        self.report.add(meal_place, UNKNOWN_RECIPE, recipe=recipe)
        return False

    def _make_dish(self, meal_place: BiText, recipe: str, servings: int) -> Dish | None:
        """Makes the dish of a recipe ID in quotation marks.

        Args:
            meal_place: The place of the meal.
            recipe: The ID without whitespace at both ends.
            servings: The servings.

        Returns:
            The dish, or ``None`` after the error ``UNKNOWN_RECIPE``.
        """
        return Dish(recipe, servings) if self._is_known(meal_place, recipe) else None


def _key_place(day: Day, key: str) -> BiText:
    """Gives the place of a key of a day.

    Args:
        day: The day.
        key: The key as the file writes it.

    Returns:
        The day and the meal when the key is the value of a ``Meal``, and otherwise the day and
        the key.
    """
    if key in Meal:
        return DAY_MEAL.to_bitext(day=day.label, meal=Meal(key).label)
    return DAY_KEY.to_bitext(day=day.label, key=key)
