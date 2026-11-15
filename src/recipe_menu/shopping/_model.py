"""The values of a shopping list: the line, the group of a category, and the list."""

from dataclasses import dataclass

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek
from recipe_menu.units import Quantity


@dataclass(frozen=True, slots=True)
class ShoppingLine:
    """One line of the shopping list: a catalog ingredient and its sums for the week.

    ``amounts`` holds one sum for each kind that cannot be added to another: grams,
    millilitres, and each count unit. An empty ``amounts`` means "to taste". Two lines are equal
    when their two fields are equal, and a ``ShoppingLine`` is hashable. The constructor checks
    its values, as Raises gives them.

    The mock leaves these checks out.

    Attributes:
        ingredient: The catalog ingredient, such as Scallion.
        amounts: The exact sums of the week, as ``add_quantities`` gives them, such as 5 stalks
            and 1 bunch. Each quantity has an amount, so none is to taste. Each unit is
            ``Unit.G``, ``Unit.ML``, or a count unit, and no two quantities have the same unit.
            Empty for to taste.

    Raises:
        TypeError: ``ingredient`` is not an ``Ingredient``, or ``amounts`` is not a tuple or
            holds an item that is not a ``Quantity``.
        ValueError: A quantity of ``amounts`` is to taste, has a unit other than ``Unit.G``,
            ``Unit.ML``, and the count units, such as ``Unit.KG`` or ``Unit.TBSP``, or has
            the same unit as another quantity of ``amounts``.
    """

    ingredient: Ingredient
    amounts: tuple[Quantity, ...]

    def amount_text(self, lang: Lang) -> str:
        """Writes the line's amounts by the rules of the shopping list.

        The mock raises ``NotImplementedError``.

        Args:
            lang: The language to write in.

        Returns:
            For an empty ``amounts``, the text of ``TO_TASTE.to_rounded_text(lang)``, which is
            ``to taste`` in English and the Chinese text U+9002 U+91CF in Chinese. Otherwise,
            each quantity of ``amounts``, in its order, written with
            ``Quantity.to_rounded_text(lang)`` and joined with " + ": a space, U+002B PLUS
            SIGN, and a space. Each sum is rounded once, on the week's total: grams,
            millilitres, and counts go up to whole numbers. The limits of 1000 g and 1000 ml
            apply to the amount after that rounding: 1000 g or more is written in kg, and
            1000 ml or more in L, with at most two decimals. So 5 stalks and 1 bunch give
            ``5 stalks + 1 bunch``, 1500 g gives ``1.5 kg``, 1001 g gives ``1.01 kg``, 1999/2 g
            gives ``1 kg``, and 3/2 stalks give ``2 stalks``.

        Raises:
            ValueError: A rounded amount has more than 4,300 digits before the point. Only a
                line built by hand can hold such an amount. A line that ``build_shopping_list``
                gave never raises, because its sums are far below that size.
            NotImplementedError: The mock does not write the text yet.
        """
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class ShoppingGroup:
    """The lines of one category, in the catalog's order of ingredients.

    ``ShoppingList.groups`` holds one group for each category that has a line. Two groups are
    equal when their two fields are equal, and a ``ShoppingGroup`` is hashable. The constructor
    checks its values, as Raises gives them.

    The mock leaves these checks out.

    Attributes:
        category: The category, such as Vegetables and fruit.
        lines: The lines of the category, in the catalog's order of ingredients. At least one
            line. The category of each line's ingredient equals ``category``. No two lines have
            equal ingredients.

    Raises:
        TypeError: ``category`` is not a ``Category``, or ``lines`` is not a tuple or holds an
            item that is not a ``ShoppingLine``.
        ValueError: ``lines`` is empty, the category of a line's ingredient does not equal
            ``category``, or two lines have equal ingredients.
    """

    category: Category
    lines: tuple[ShoppingLine, ...]


@dataclass(frozen=True, slots=True)
class ShoppingList:
    """The shopping list of one week.

    It holds the week, the number of meals and of dishes, the lines grouped by category in the
    catalog's order, and the pantry ingredients that the menu uses. ``build_shopping_list``
    gives it, and the ``shop`` command writes it. Two lists are equal when their five fields are
    equal, and a ``ShoppingList`` is hashable. A ``ShoppingList`` holds no catalog, so it cannot
    check the order of ``groups`` and ``pantry_used``. ``build_shopping_list`` gives that order.
    The constructor checks its other values, as Raises gives them.

    The mock leaves these checks out.

    Attributes:
        week: The week of the menu.
        meal_count: The number of meals of the week that hold at least one dish. 0 or more, and
            at most ``dish_count``. 0 only when ``dish_count`` is 0. Not a ``bool``.
        dish_count: The number of dishes of the week. 0 or more. Not a ``bool``.
        groups: One group for each category that has a line, in the catalog's order of
            categories. No two groups have equal categories. Empty when ``dish_count`` is 0.
        pantry_used: The pantry's ingredients that the menu uses, by category in the catalog's
            order and then in the catalog's order of ingredients. Empty when ``dish_count`` is
            0. No ingredient appears twice in ``pantry_used`` and the lines of ``groups``
            together.

    Raises:
        TypeError: ``week`` is not an ``IsoWeek``, ``meal_count`` or ``dish_count`` is not an
            ``int`` or is a ``bool``, ``groups`` is not a tuple of ``ShoppingGroup`` values, or
            ``pantry_used`` is not a tuple of ``Ingredient`` values.
        ValueError: ``meal_count`` or ``dish_count`` is less than 0, ``meal_count`` is more than
            ``dish_count``, ``meal_count`` is 0 and ``dish_count`` is not, ``dish_count`` is 0
            and ``groups`` or ``pantry_used`` is not empty, two groups have equal categories, or
            an ingredient appears twice in ``pantry_used`` and the lines of ``groups`` together.
    """

    week: IsoWeek
    meal_count: int
    dish_count: int
    groups: tuple[ShoppingGroup, ...]
    pantry_used: tuple[Ingredient, ...]
