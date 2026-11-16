"""The PT01 data folder of the v0.1 test plan, and the output that its commands must give.

``make_pt01`` writes the folder of section 3 of the plan: 300 ingredients, 10 in the pantry,
1,000 recipes of 12 ingredients each (all with one shared ingredient, the first in the catalog),
and 52 week menus of 63 dishes from 63 different recipes. The ``pt01_*`` functions give the
expected output of ``list``, ``show recipe-0500``, ``search`` for the shared ingredient, and
``menu show 2026-W26`` on that folder, built from the rules of the generator. Nothing here
imports ``recipe_menu``.
"""

from pathlib import Path

RECIPES = 1000
INGREDIENTS = 300
WEEKS = 52
CHECK_LINES = [
    "Checked the settings, the catalog, the pantry, 1000 recipes, and 52 week menus.",
    "",
    "No errors. No warnings.",
]

_CATEGORIES = (
    ("produce", "蔬菜水果", "Vegetables and fruit"),
    ("meat", "肉类水产", "Meat and seafood"),
    ("eggs", "蛋奶豆制品", "Eggs, dairy, and tofu"),
    ("staples", "米面粮油", "Rice, flour, and oil"),
    ("seasonings", "调味品", "Seasonings"),
    ("other", "其他", "Other"),
)
_TAGS = (
    ("快手", "quick"),
    ("家常", "home-style"),
    ("素", "vegetarian"),
    ("辣", "spicy"),
    ("主食", "staple"),
)
_AMOUNTS = ("200 g", "15 ml", "2 个", "适量")
_QUANTITIES = ("200 g", "15 ml", "2 pieces", "to taste")
_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
_MEALS = ("breakfast", "lunch", "dinner")


def _write(path: Path, content: str) -> None:
    """Writes a file in UTF-8 with LF line ends, and makes its folder."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def _catalog() -> str:
    """Gives ``catalog.toml``: the six categories, 300 ingredients, and the five tags."""
    categories = "".join(
        f'  {{ key = "{key}", zh = "{zh}", en = "{en}" }},\n' for key, zh, en in _CATEGORIES
    )
    items = "".join(
        f'  {{ zh = "食材{k:03d}", en = "Ingredient {k:03d}", '
        f'category = "{_CATEGORIES[(k - 1) % len(_CATEGORIES)][0]}" }},\n'
        for k in range(1, INGREDIENTS + 1)
    )
    tags = "".join(f'  {{ zh = "{zh}", en = "{en}" }},\n' for zh, en in _TAGS)
    return f"categories = [\n{categories}]\n\ningredients = [\n{items}]\n\ntags = [\n{tags}]\n"


def _steps(chinese: bool) -> str:
    """Gives the six steps of one language of a recipe."""
    if chinese:
        lines = [
            f'  "第 {n} 步\uff1a把食材洗净切好\uff0c放进锅里翻炒两分钟\u3002",' for n in range(1, 7)
        ]
    else:
        lines = [
            f'  "Step {n}: Wash and cut the ingredients, and stir-fry them for two minutes.",'
            for n in range(1, 7)
        ]
    return "".join(f"{line}\n" for line in lines)


def _recipe(k: int) -> str:
    """Gives recipe number ``k``: 12 ingredients, the first one shared by every recipe."""
    tags = [_TAGS[k % 5][0], _TAGS[(k + 1) % 5][0]]
    note = 'note = { zh = "切块", en = "cut into pieces" }'
    lines = [f'  {{ item = "食材001", amount = "1 tsp", {note} }},']
    for j in range(11):
        number = 2 + (11 * k + j) % 299
        lines.append(f'  {{ item = "食材{number:03d}", amount = "{_AMOUNTS[j % 4]}", {note} }},')
    ingredients = "".join(f"{line}\n" for line in lines)
    return (
        f'name = {{ zh = "菜谱{k:04d}", en = "Recipe {k:04d}" }}\n'
        f"servings = {1 + k % 4}\n"
        f'tags = ["{tags[0]}", "{tags[1]}"]\n'
        f"ingredients = [\n{ingredients}]\n"
        f"[steps]\nzh = [\n{_steps(True)}]\nen = [\n{_steps(False)}]\n"
    )


def _menu(week: int) -> str:
    """Gives the menu of week ``week`` of 2026: 3 dishes in each of 21 meals."""
    lines = [f'week = "2026-W{week:02d}"']
    for d, day in enumerate(_DAYS):
        lines += ["", f"[{day}]"]
        for m, meal in enumerate(_MEALS):
            dishes = []
            for s in range(3):
                number = ((week - 1) * 63 + 9 * d + 3 * m + s) % RECIPES + 1
                recipe = f"recipe-{number:04d}"
                if meal == "dinner" and s == 0:
                    dishes.append(f'{{ recipe = "{recipe}", servings = 4 }}')
                else:
                    dishes.append(f'"{recipe}"')
            lines.append(f"{meal} = [{', '.join(dishes)}]")
    return "".join(f"{line}\n" for line in lines)


def make_pt01(root: Path) -> None:
    """Writes the PT01 data folder at ``root``, with no ``shopping`` folder."""
    settings = 'language = "en"\nmeals = ["breakfast", "lunch", "dinner"]\nservings = 2\n'
    _write(root / "settings.toml", settings)
    _write(root / "catalog.toml", _catalog())
    last = ", ".join(f'"食材{k:03d}"' for k in range(INGREDIENTS - 9, INGREDIENTS + 1))
    _write(root / "pantry.toml", f"pantry = [{last}]\n")
    for k in range(1, RECIPES + 1):
        _write(root / "recipes" / f"recipe-{k:04d}.toml", _recipe(k))
    for week in range(1, WEEKS + 1):
        _write(root / "menus" / f"2026-W{week:02d}.toml", _menu(week))


def pt01_list() -> list[str]:
    """Gives the lines of ``list`` on the PT01 folder: the header, 1,000 rows, and the count."""
    lines = ["ID            Name          Servings   Tags"]
    for k in range(1, RECIPES + 1):
        tags = f"{_TAGS[k % 5][1]}, {_TAGS[(k + 1) % 5][1]}"
        lines.append(f"recipe-{k:04d}   Recipe {k:04d}   {1 + k % 4:<8}   {tags}")
    return [*lines, "", f"{RECIPES} recipes."]


def pt01_show() -> list[str]:
    """Gives the lines of ``show recipe-0500`` on the PT01 folder."""
    lines = [
        "Recipe 0500  菜谱0500",
        "Servings: 1   Tags: quick, home-style",
        "",
        "Ingredients",
        f"  Ingredient 001   {'1 tsp':<8}   cut into pieces",
    ]
    for j in range(11):
        number = 2 + (11 * 500 + j) % 299
        lines.append(f"  Ingredient {number:03d}   {_QUANTITIES[j % 4]:<8}   cut into pieces")
    lines += ["", "Steps"]
    lines += [
        f"  {n}. Step {n}: Wash and cut the ingredients, and stir-fry them for two minutes."
        for n in range(1, 7)
    ]
    return lines


def pt01_search() -> list[str]:
    """Gives the lines of the search for the shared ingredient: all 1,000 recipes."""
    lines = [f"{'ID':<14}{'Name':<14}Matched in"]
    lines += [f"recipe-{k:04d}   Recipe {k:04d}   ingredient" for k in range(1, RECIPES + 1)]
    return [*lines, "", f'{RECIPES} recipes match "食材001".']


def pt01_menu_show() -> list[str]:
    """Gives the lines of ``menu show 2026-W26`` on the PT01 folder: 63 dishes in 21 meals.

    The Day column is 10 columns wide, and the columns of breakfast and lunch are 14 columns wide,
    each followed by 3 spaces. The cell of meal ``m`` on day ``d`` in line ``s`` is ``Recipe NNNN``
    with NNNN as ``576 + 9 * d + 3 * m + s``, and the servings are 4 for the first dish of a dinner
    and 2 for the others.
    """
    days = (
        "Mon 22 Jun",
        "Tue 23 Jun",
        "Wed 24 Jun",
        "Thu 25 Jun",
        "Fri 26 Jun",
        "Sat 27 Jun",
        "Sun 28 Jun",
    )
    lines = [
        "Menu for 2026-W26, 22 to 28 June 2026",
        "",
        f"{'Day':<10}   {'Breakfast':<14}   {'Lunch':<14}   Dinner",
    ]
    for d, day in enumerate(days):
        for s in range(3):
            cells = [
                f"Recipe {576 + 9 * d + 3 * m + s:04d} \u00d7{4 if m == 2 and s == 0 else 2}"
                for m in range(3)
            ]
            first = day if s == 0 else ""
            lines.append(f"{first:<10}   {cells[0]:<14}   {cells[1]:<14}   {cells[2]}")
    return [*lines, "", "21 meals, 63 dishes. \u00d7n: servings."]
