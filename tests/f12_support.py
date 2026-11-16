"""Helpers and example values that the F12 tests share.

Nothing here calls an interface of F12 when the module is imported. At import the module builds
only texts, ``None``, tuples, lists, dicts, enum members, and the empty pantry. It makes shopping
lines, groups, and lists only inside its functions, so the test files import against the mock and
against a broken implementation. It also reads the files of a week as the shopping command does
and writes the folders of two v0.1 scenarios. The cases write their values in the notation of the
test plan, and the doc comment of each function that reads it says how.
"""

from collections.abc import Iterable, Mapping, Sequence
from fractions import Fraction
from pathlib import Path

from f03_support import put_bytes, write
from f06_support import make_menu, read_menu
from f07_changes import edit, make_init
from f11_support import menu_text
from recipe_menu.catalog import Catalog, Category, Ingredient, Pantry, read_catalog, read_pantry
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, WeekMenu
from recipe_menu.recipes import (
    Recipe,
    RecipeIngredient,
    Steps,
    list_recipe_ids,
    read_recipe,
)
from recipe_menu.settings import Meal, read_settings
from recipe_menu.shopping import ShoppingGroup, ShoppingLine, ShoppingList
from recipe_menu.units import Quantity, Unit, parse_quantity

EN, ZH = Lang.EN, Lang.ZH
LUNCH_DINNER = (Meal.LUNCH, Meal.DINNER)
EVERY_MEAL = tuple(Meal)

CATEGORIES = (
    ("produce", "Vegetables and fruit", "蔬菜水果"),
    ("meat", "Meat and seafood", "肉类水产"),
    ("eggs", "Eggs, dairy, and tofu", "蛋奶豆制品"),
    ("staples", "Rice, flour, and oil", "米面粮油"),
    ("seasonings", "Seasonings", "调味品"),
    ("other", "Other", "其他"),
)
INGREDIENTS = (
    ("produce", "番茄", "Tomato", None),
    ("produce", "菜心", "Choy sum", None),
    ("produce", "西兰花", "Broccoli", None),
    ("produce", "葱", "Scallion", Unit.STALK),
    ("produce", "姜", "Ginger", Unit.SLICE),
    ("produce", "大蒜", "Garlic", Unit.CLOVE),
    ("meat", "五花肉", "Pork belly", None),
    ("meat", "猪肉末", "Minced pork", None),
    ("meat", "鸡翅中", "Chicken wings", None),
    ("eggs", "鸡蛋", "Egg", Unit.PIECE),
    ("eggs", "豆腐", "Tofu", Unit.BLOCK),
    ("staples", "大米", "Rice", None),
    ("staples", "面条", "Noodles", None),
    ("staples", "食用油", "Cooking oil", None),
    ("seasonings", "盐", "Salt", None),
    ("seasonings", "糖", "Sugar", None),
    ("seasonings", "生抽", "Soy sauce", None),
    ("seasonings", "冰糖", "Rock sugar", None),
    ("seasonings", "郫县豆瓣酱", "Doubanjiang", None),
    ("seasonings", "花椒", "Sichuan pepper", None),
    ("seasonings", "白胡椒粉", "White pepper", None),
    ("other", "可乐", "Cola", Unit.CAN),
)
S18_CELLS = (
    "monday dinner: red-braised-pork 2",
    "tuesday dinner: tomato-egg 2",
    "wednesday dinner: tomato-egg 2",
    "thursday dinner: tomato-egg-noodles 2",
    "friday dinner: scallion-noodles 2",
)
PANTRY_NAMES = ("食用油", "盐", "糖", "生抽", "花椒")
NO_PANTRY = Pantry(frozenset())
S16_EN = [
    "Vegetables and fruit",
    "- Tomato 450 g",
    "- Scallion 2 stalks",
    "Eggs, dairy, and tofu",
    "- Egg 5 pieces",
]
RECIPE_LINES = {
    "tomato-egg": "番茄 300 g, 鸡蛋 3, 葱 1 根, 盐 适量, 糖 1 tsp, 食用油 2 tbsp",
    "choy-sum": "菜心 1 斤, 大蒜 3 瓣, 盐 适量, 食用油 1 tbsp",
    "rice": "大米 160 g",
    "mapo-tofu": (
        "豆腐 1 块, 猪肉末 100 g, 郫县豆瓣酱 1 tbsp, 花椒 1 tsp, 大蒜 2 瓣, 葱 1 根, "
        "生抽 1 tbsp, 食用油 2 tbsp"
    ),
    "cola-wings": "鸡翅中 500 g, 可乐 1 罐, 姜 3 片, 葱 1 根, 生抽 2 tbsp",
    "tomato-egg-noodles": "面条 200 g, 番茄 300 g, 鸡蛋 2, 葱 1 根, 盐 适量, 白胡椒粉 适量",
    "red-braised-pork": "五花肉 1 斤, 冰糖 30 g, 生抽 2 tbsp, 姜 3 片, 葱 2 根",
    "scallion-noodles": "面条 200 g, 葱 1 把, 生抽 10 g",
}

W47_EN = [
    "Vegetables and fruit",
    "- Tomato 600 g",
    "- Choy sum 1.5 kg",
    "- Scallion 5 stalks",
    "- Ginger 6 slices",
    "- Garlic 11 cloves",
    "Meat and seafood",
    "- Minced pork 100 g",
    "- Chicken wings 1 kg",
    "Eggs, dairy, and tofu",
    "- Egg 5 pieces",
    "- Tofu 1 block",
    "Rice, flour, and oil",
    "- Rice 640 g",
    "- Noodles 200 g",
    "Seasonings",
    "- Doubanjiang 15 ml",
    "- White pepper to taste",
    "Other",
    "- Cola 2 cans",
]
W47_ZH = [
    "蔬菜水果",
    "- 番茄 600 g",
    "- 菜心 1.5 kg",
    "- 葱 5 根",
    "- 姜 6 片",
    "- 大蒜 11 瓣",
    "肉类水产",
    "- 猪肉末 100 g",
    "- 鸡翅中 1 kg",
    "蛋奶豆制品",
    "- 鸡蛋 5 个",
    "- 豆腐 1 块",
    "米面粮油",
    "- 大米 640 g",
    "- 面条 200 g",
    "调味品",
    "- 郫县豆瓣酱 15 ml",
    "- 白胡椒粉 适量",
    "其他",
    "- 可乐 2 罐",
]
W47_PANTRY_EN = ["Cooking oil", "Salt", "Sugar", "Soy sauce", "Sichuan pepper"]

# ---------------------------------------------------------------- the code catalog and recipes


def code_catalog() -> Catalog:
    """Gives the catalog that the example of 2.5 builds: six categories and 22 ingredients."""
    categories = {key: Category(key, BiText(en, zh)) for key, en, zh in CATEGORIES}
    ingredients = tuple(
        Ingredient(BiText(en, zh), categories[key], unit) for key, zh, en, unit in INGREDIENTS
    )
    return Catalog(tuple(categories.values()), ingredients, ())


def find(catalog: Catalog, name: str) -> Ingredient:
    """Gives the ingredient of the catalog with the Chinese name."""
    ingredient = catalog.find_ingredient(name)
    assert ingredient is not None, name
    return ingredient


def category(catalog: Catalog, key: str) -> Category:
    """Gives the category of the catalog with the key."""
    return next(item for item in catalog.categories if item.key == key)


def code_pantry(catalog: Catalog, names: Iterable[str] = PANTRY_NAMES) -> Pantry:
    """Gives the pantry of the ingredients with the Chinese names, the code pantry by default."""
    return Pantry(frozenset(find(catalog, name) for name in names))


def subset(catalog: Catalog, keys: Sequence[str], names: Sequence[str]) -> Catalog:
    """Gives a catalog of the categories and ingredients of ``catalog`` with these keys and names.

    The items are the objects of ``catalog``, in the order of the arguments, and it has no tags.
    """
    return Catalog(
        tuple(category(catalog, key) for key in keys),
        tuple(find(catalog, name) for name in names),
        (),
    )


def copy_category(item: Category) -> Category:
    """Gives an equal but separate copy of the category."""
    return Category(item.key, BiText(item.name.en, item.name.zh))


def copy_of(ingredient: Ingredient) -> Ingredient:
    """Gives an equal but separate copy of the ingredient, with a copy of its category."""
    names = BiText(ingredient.name.en, ingredient.name.zh)
    return Ingredient(names, copy_category(ingredient.category), ingredient.unit)


def recipe(catalog: Catalog, recipe_id: str, lines: Sequence[str], servings: int = 2) -> Recipe:
    """Builds ``R(recipe_id, servings: lines)`` of the plan, with the catalog's ingredients.

    Each line is the Chinese name of an ingredient and an amount text, which ``parse_quantity``
    reads with the ingredient's default unit.
    """
    items = []
    for text in lines:
        name, amount = text.split(" ", 1)
        ingredient = find(catalog, name)
        quantity = parse_quantity(amount, ingredient.unit)
        assert isinstance(quantity, Quantity), text
        items.append(RecipeIngredient(ingredient, quantity))
    return Recipe(recipe_id, BiText(recipe_id), servings, (), tuple(items), Steps(("Cook.",)))


def recipes_of(catalog: Catalog, *texts: str) -> dict[str, Recipe]:
    """Builds a mapping of recipes from texts such as ``"three 3: <name> 100 g, <name> 1"``.

    The text before the colon is the recipe ID and, after a space, its servings, which is 2
    when it is left out. The text after the colon holds the lines, separated by ``, ``.
    """
    mapping = {}
    for text in texts:
        head, _, body = text.partition(":")
        words = head.split()
        servings = int(words[1]) if len(words) > 1 else 2
        lines = [item.strip() for item in body.split(",") if item.strip()]
        mapping[words[0]] = recipe(catalog, words[0], lines, servings)
    return mapping


def code_recipes(catalog: Catalog) -> dict[str, Recipe]:
    """Gives the eight recipes of the example of 2.5, each with 2 servings, in its order."""
    return {
        recipe_id: recipe(catalog, recipe_id, lines.split(", "))
        for recipe_id, lines in RECIPE_LINES.items()
    }


def nothing_recipe() -> Recipe:
    """Gives ``nothing`` of F12-T23: a recipe with 2 servings and no ingredient line."""
    return Recipe("nothing", BiText("nothing"), 2, (), (), Steps(("Cook.",)))


# ---------------------------------------------------------------- menus


def menu_of(*cells: str, meals: Sequence[Meal] = LUNCH_DINNER, week: int = 48) -> WeekMenu:
    """Builds a menu of the week 2026-W<week> from cells such as ``"monday dinner: r1 2, r2 3"``.

    A cell is a day, a meal, a colon, and dishes written as a recipe ID and its servings. Every
    slot that no cell names holds no dish.
    """
    filled = {}
    for cell in cells:
        head, _, body = cell.partition(":")
        day, meal = head.split()
        pairs = (dish.split() for dish in body.split(","))
        filled[(Day(day), Meal(meal))] = tuple(Dish(name, int(count)) for name, count in pairs)
    return make_menu(IsoWeek(2026, week), meals, filled)


def every_slot(
    text: str, meals: Sequence[Meal] = EVERY_MEAL, week: int = 48, times: int = 1
) -> WeekMenu:
    """Builds a menu that holds the same dishes ``times`` times in each slot of every day.

    ``text`` holds dishes as a cell of ``menu_of`` writes them, such as ``"rice 2"``.
    """
    body = ", ".join([text] * times)
    return menu_of(
        *(f"{day.value} {meal.value}: {body}" for day in Day for meal in meals),
        meals=meals,
        week=week,
    )


# ---------------------------------------------------------------- expected values


def amt(text: str) -> Quantity:
    """Builds the quantity of a text such as ``"200/3 G"``: an exact number and a ``Unit`` name."""
    number, name = text.split(" ")
    return Quantity(Fraction(number), Unit[name])


def line(catalog: Catalog, name: str, *amounts: Quantity | str) -> ShoppingLine:
    """Builds ``name: amounts`` of the plan, with the catalog's ingredient of that name.

    An amount is a ``Quantity`` or a text that ``amt`` reads, such as ``"200/3 G"``.
    """
    items = tuple(item if isinstance(item, Quantity) else amt(item) for item in amounts)
    return ShoppingLine(find(catalog, name), items)


def line_of(catalog: Catalog, text: str) -> ShoppingLine:
    """Builds a line from a text such as ``"name: 5 STALK, 1 BUNCH"``, or ``"name:"``."""
    name, _, rest = text.partition(":")
    amounts = [item.strip() for item in rest.split(",") if item.strip()]
    return line(catalog, name.strip(), *amounts)


def group(catalog: Catalog, key: str, *lines: ShoppingLine | str) -> ShoppingGroup:
    """Builds ``key [lines]`` of the plan: the category with the key and its lines.

    A line may be a ``ShoppingLine`` or a text for ``line_of``.
    """
    items = tuple(
        item if isinstance(item, ShoppingLine) else line_of(catalog, item) for item in lines
    )
    return ShoppingGroup(category(catalog, key), items)


def expect(
    catalog: Catalog,
    week: int | IsoWeek,
    meals: int,
    dishes: int,
    groups: Sequence[ShoppingGroup] = (),
    *,
    pantry: Sequence[str] = (),
) -> ShoppingList:
    """Builds ``List(week, meals, dishes, groups, pantry)`` of the plan.

    ``week`` is a number of 2026 or an ``IsoWeek``. ``pantry`` holds Chinese names.
    """
    iso = week if isinstance(week, IsoWeek) else IsoWeek(2026, week)
    used = tuple(find(catalog, name) for name in pantry)
    return ShoppingList(iso, meals, dishes, tuple(groups), used)


def expected_w47(catalog: Catalog) -> ShoppingList:
    """Gives the list of F12-T29, the example week 2026-W47, with the items of the catalog."""
    groups = (
        group(
            catalog,
            "produce",
            "番茄: 600 G",
            "菜心: 1500 G",
            "葱: 5 STALK",
            "姜: 6 SLICE",
            "大蒜: 11 CLOVE",
        ),
        group(catalog, "meat", "猪肉末: 100 G", "鸡翅中: 1000 G"),
        group(catalog, "eggs", "鸡蛋: 5 PIECE", "豆腐: 1 BLOCK"),
        group(catalog, "staples", "大米: 640 G", "面条: 200 G"),
        group(catalog, "seasonings", "郫县豆瓣酱: 15 ML", "白胡椒粉:"),
        group(catalog, "other", "可乐: 2 CAN"),
    )
    return expect(catalog, 47, 4, 9, groups, pantry=PANTRY_NAMES)


def expected_s16(catalog: Catalog) -> ShoppingList:
    """Gives the list of F12-T30, v0.1-S16, with the items of the catalog."""
    groups = (
        group(catalog, "produce", "番茄: 450 G", "葱: 3/2 STALK"),
        group(catalog, "eggs", "鸡蛋: 9/2 PIECE"),
    )
    return expect(catalog, 48, 1, 1, groups, pantry=("食用油", "盐", "糖"))


def expected_s18(catalog: Catalog) -> ShoppingList:
    """Gives the list of F12-T31, v0.1-S18, with the items of the catalog."""
    groups = (
        group(catalog, "produce", "番茄: 900 G", "葱: 5 STALK, 1 BUNCH", "姜: 3 SLICE"),
        group(catalog, "meat", "五花肉: 500 G"),
        group(catalog, "eggs", "鸡蛋: 8 PIECE"),
        group(catalog, "staples", "面条: 400 G"),
        group(catalog, "seasonings", "生抽: 30 ML, 10 G", "冰糖: 30 G", "白胡椒粉:"),
    )
    return expect(catalog, 48, 5, 5, groups, pantry=("食用油", "盐", "糖"))


def lines_of(shopping: ShoppingList) -> list[ShoppingLine]:
    """Gives every line of the list, in the order of the groups and of their lines."""
    return [item for entry in shopping.groups for item in entry.lines]


def texts(shopping: ShoppingList, lang: Lang) -> list[str]:
    """Gives the ``amount_text`` of every line of the list, in the order of the lines."""
    return [item.amount_text(lang) for item in lines_of(shopping)]


def written(shopping: ShoppingList, lang: Lang) -> list[str]:
    """Writes each heading and each line in one language, as the example of 2.5 does."""
    result = []
    for entry in shopping.groups:
        result.append(entry.category.name.get(lang))
        for item in entry.lines:
            result.append(f"- {item.ingredient.name.get(lang)} {item.amount_text(lang)}")
    return result


def names_of(items: Iterable[Ingredient], lang: Lang) -> list[str]:
    """Gives the names of the ingredients in one language."""
    return [item.name.get(lang) for item in items]


# ---------------------------------------------------------------- reading folders


def read_week(
    folder: DataFolder, week: IsoWeek, problems: list[Problem] | None = None
) -> tuple[WeekMenu, dict[str, Recipe], Catalog, Pantry]:
    """Reads the files that F13's ``shop`` reads, and checks that each reader gives its value.

    It calls ``read_settings``, ``list_recipe_ids``, ``read_week_menu`` with the settings and
    the IDs, ``read_catalog``, ``read_pantry`` with the catalog, and ``read_recipe`` once for
    each ID that a dish names, in the order in which the dishes first name them. No reader gives
    an error. When ``problems`` is ``None``, no reader gives a warning either. Otherwise the
    warnings are added to ``problems``.

    Returns:
        The menu, the mapping from each ID to its recipe, the catalog, and the pantry.
    """
    found: list[Problem] = []
    settings, issues = read_settings(folder)
    found += issues
    ids, issues = list_recipe_ids(folder)
    found += issues
    assert settings is not None
    menu, issues = read_menu(folder, settings, frozenset(ids), week)
    found += issues
    catalog, issues = read_catalog(folder)
    found += issues
    assert menu is not None
    assert catalog is not None
    pantry, issues = read_pantry(folder, catalog)
    found += issues
    assert pantry is not None
    mapping: dict[str, Recipe] = {}
    for slot in menu.slots:
        for dish in slot.dishes:
            if dish.recipe_id not in mapping:
                read, issues = read_recipe(folder, catalog, dish.recipe_id)
                found += issues
                assert read is not None
                mapping[dish.recipe_id] = read
    assert all(item.severity is Severity.WARNING for item in found), found
    if problems is None:
        assert found == []
    else:
        problems.extend(found)
    return menu, mapping, catalog, pantry


def s16_folder(example: DataFolder, target: Path) -> DataFolder:
    """Writes the files of v0.1-S16 into the init folder at ``target``, and gives its folder.

    The settings name breakfast, lunch, and dinner with 3 servings. The menu of 2026-W48 holds
    ``tomato-egg`` in Monday breakfast, with no servings.
    """
    root = make_init(example, target)
    settings = 'language = "en"\nmeals = ["breakfast", "lunch", "dinner"]\nservings = 3\n'
    write(root / "settings.toml", settings)
    path = root / "menus" / "2026-W48.toml"
    put_bytes(path, menu_text("2026-W48", EVERY_MEAL))
    edit(path, "breakfast = []", 'breakfast = ["tomato-egg"]')
    return DataFolder(root)


S18_RECIPE = """name = { zh = "葱油拌面", en = "Scallion oil noodles" }
servings = 2
tags = ["快手", "主食"]

ingredients = [
  { item = "面条", amount = "200 g" },
  { item = "葱", amount = "1 把" },
  { item = "生抽", amount = "10 g" },
]

[steps]
zh = ["葱切段，小火煎出葱油。", "面条煮熟，拌上葱油和生抽。"]
en = ["Cut the scallion, and fry it in oil on low heat.", "Toss the noodles in the oil and soy."]
"""
S18_DINNERS = (
    "red-braised-pork",
    "tomato-egg",
    "tomato-egg",
    "tomato-egg-noodles",
    "scallion-noodles",
)


def s18_changes(folder: DataFolder) -> None:
    """Writes the three changes of v0.1-S18 into the example folder.

    The pantry lists cooking oil, salt, sugar, and Sichuan pepper. The recipe
    ``scallion-noodles`` is new. The menu of 2026-W48 holds the dinners of Monday to Friday, and
    every other meal is empty.
    """
    write(folder.pantry, 'pantry = ["食用油", "盐", "糖", "花椒"]\n')
    write(folder.recipe_file("scallion-noodles"), S18_RECIPE)
    path = folder.menu_file("2026-W48")
    put_bytes(path, menu_text("2026-W48", LUNCH_DINNER))
    for recipe_id in S18_DINNERS:
        edit(path, "dinner = []", f'dinner = ["{recipe_id}"]')


def hold(mapping: Mapping[str, Recipe]) -> tuple[dict[str, Recipe], list[str]]:
    """Gives a copy of the mapping and the list of its keys, to compare after a call."""
    return dict(mapping), list(mapping)
