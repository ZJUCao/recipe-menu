"""Helpers and example values that the F04 tests share."""

import contextlib
import os
import sys
from collections.abc import Iterator, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from f03_support import TAG_KEYS, put_bytes, write
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag, read_catalog
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps, read_recipe
from recipe_menu.units import Quantity, Unit

if sys.platform == "win32":
    import _winapi

GENERIC_READ = 0x80000000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

EN, ZH = Lang.EN, Lang.ZH

type Msg = tuple[str, str]
type Entry = tuple[Severity, str, BiText | None, str, str]

DISH_FILE = "recipes/dish.toml"
EXAMPLE_IDS = (
    "choy-sum",
    "cola-wings",
    "mapo-tofu",
    "red-braised-pork",
    "rice",
    "tomato-egg",
    "tomato-egg-noodles",
)

# ------------------------------------------------------ example values (design 2.1 to 2.3)

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
eggs = Category("eggs", BiText("Eggs, dairy, and tofu", "蛋奶豆制品"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
egg = Ingredient(BiText("Egg", "鸡蛋"), eggs, Unit.PIECE)
scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
choy_sum = Ingredient(BiText("Choy sum", "菜心"), produce)
quick = Tag(BiText("quick", "快手"))
home = Tag(BiText("home-style", "家常"))
dish_catalog = Catalog((produce, eggs), (tomato, egg, scallion), (quick, home))

wedges = BiText("cut into wedges", "切块")
chinese = ("五花肉切块，冷水下锅焯水。", "小火炖 60 分钟，再大火收汁。")
both = Steps(("Cut the tomatoes into wedges.",), ("番茄切块。",))
choy_name = BiText("Stir-fried choy sum", "清炒菜心")
choy_lines = (RecipeIngredient(choy_sum, Quantity(Fraction(1), Unit.JIN)),)
choy_steps = Steps(("Stir-fry the choy sum.",), ("炒菜心。",))


def qty(amount: int | Fraction, unit: Unit) -> Quantity:
    """Gives the quantity of an amount and a unit."""
    return Quantity(Fraction(amount), unit)


dish = Recipe(
    "dish",
    BiText("Tomato and egg stir-fry", "番茄炒蛋"),
    2,
    (quick,),
    (RecipeIngredient(tomato, qty(300, Unit.G)),),
    Steps(("Cut the tomatoes.",), ("番茄切块。",)),
)

# ---------------------------------------------------------------- writing files


def touch(folder: Path, *names: str) -> None:
    """Writes an empty file for each name in a folder, and makes the folder."""
    for name in names:
        put_bytes(folder / name, b"")


BASE_NAME = '{ zh = "番茄炒蛋", en = "Tomato and egg stir-fry" }'
BASE_ITEMS = ('{ item = "番茄", amount = "300 g" }',)
BASE_STEPS = ('zh = ["番茄切块。"]', 'en = ["Cut the tomatoes."]')


def dish_text(
    name: str | None = BASE_NAME,
    servings: str | None = "2",
    tags: str | None = '["快手"]',
    ingredients: str | Sequence[str] | None = BASE_ITEMS,
    steps: str | Sequence[str] | None = BASE_STEPS,
) -> str:
    """Gives the text of the base recipe, with parts changed or left out.

    ``name``, ``servings``, ``tags``, and a text for ``ingredients`` or ``steps`` are the value
    after the key's ``=``. A tuple for ``ingredients`` gives its items, one on each line, and a
    tuple for ``steps`` gives the lines after ``[steps]``. ``None`` leaves the part out.
    """
    lines = [
        f"{key} = {value}"
        for key, value in (("name", name), ("servings", servings), ("tags", tags))
        if value is not None
    ]
    if isinstance(ingredients, str):
        lines.append(f"ingredients = {ingredients}")
    elif ingredients is not None:
        lines += ["ingredients = [", *(f"  {item}," for item in ingredients), "]"]
    if isinstance(steps, str):
        lines.append(f"steps = {steps}")
    elif steps is not None:
        lines += ["", "[steps]", *steps]
    return "\n".join(lines) + "\n"


def write_dish(folder: DataFolder, file_id: str = "dish", **parts: Any) -> None:
    """Writes ``recipes/<file_id>.toml``: the base recipe with the parts changed."""
    write(folder.recipe_file(file_id), dish_text(**parts))


def read_dish(
    folder: DataFolder, catalog: Catalog | None = dish_catalog, **parts: Any
) -> tuple[Recipe | None, tuple[Problem, ...]]:
    """Writes the base recipe with the parts changed, and reads it as ``dish``."""
    write_dish(folder, **parts)
    return read_recipe(folder, catalog, "dish")


# ---------------------------------------------------------------- places (design 2.6)

NAME = BiText("name", "名称")
SERVINGS = BiText("servings", "份数")
TAGS = BiText("tags", "标签")
INGREDIENTS = BiText("ingredients", "食材")
STEPS = BiText("steps", "步骤")


def tag_n(number: int) -> BiText:
    """The place of an item of ``tags``."""
    return BiText(f"tag {number}", f"标签 {number}")


def ingredient_n(number: int) -> BiText:
    """The place of an item of ``ingredients``."""
    return BiText(f"ingredient {number}", f"食材 {number}")


def zh_step(number: int) -> BiText:
    """The place of a Chinese step."""
    return BiText(f"Chinese step {number}", f"中文步骤 {number}")


def en_step(number: int) -> BiText:
    """The place of an English step."""
    return BiText(f"English step {number}", f"英文步骤 {number}")


# ------------------------------------------------------------ messages of recipes (2.6)

RECIPE_KEYS: Msg = (
    "name, servings, tags, ingredients, and steps",
    "name、servings、tags、ingredients 和 steps",
)
ITEM_KEYS: Msg = ("item, amount, and note", "item、amount 和 note")
ZH_EN_KEYS: Msg = TAG_KEYS


def m_not_a_zh_en(key: str) -> Msg:
    """The message of a name or a note that is not a table."""
    return (
        f'"{key}" must be a table in braces with "zh" and "en", '
        'such as { zh = "...", en = "..." }.',
        f'“{key}”必须是放在花括号里、带有“zh”和“en”的表，比如 {{ zh = "...", en = "..." }}。',
    )


M_NO_NAME: Msg = (
    'The name has no text in either language. Write "zh", "en", or both.',
    "名称在两种语言里都没有文字。请写上“zh”、“en”或两者。",
)
M_NO_ZH_NAME: Msg = (
    "No Chinese name. Commands show the English name instead.",
    "没有中文名称。命令会改为显示英文名称。",
)
M_NO_EN_NAME: Msg = (
    "No English name. Commands show the Chinese name instead.",
    "没有英文名称。命令会改为显示中文名称。",
)
M_SERVINGS_NOT_A_NUMBER: Msg = (
    "Servings must be a whole number from 1 to 100, such as 2.",
    "份数必须是 1 到 100 之间的整数，比如 2。",
)


def m_too_few(servings: int) -> Msg:
    """The message of servings below 1."""
    return (
        f"Servings must be a whole number of 1 or more, not {servings}.",
        f"份数必须是不小于 1 的整数，不能是 {servings}。",
    )


def m_too_many(servings: int) -> Msg:
    """The message of servings above 100."""
    return (
        f"Servings must be a whole number of 100 or less, not {servings}.",
        f"份数必须是不大于 100 的整数，不能是 {servings}。",
    )


def m_unknown_tag(tag: str) -> Msg:
    """The message of a tag that the catalog lacks."""
    return (
        f'Unknown tag "{tag}". Add it to the catalog\'s tags.',
        f"未知标签“{tag}”。请把它加入目录里的标签。",
    )


def m_unknown_ing(name: str) -> Msg:
    """The message of an ingredient that the catalog lacks."""
    return (
        f'Unknown ingredient "{name}". Add it to the catalog, or use its name in the catalog.',
        f"未知食材“{name}”。请把它加入目录，或改用目录里的名称。",
    )


def m_not_a_number(amount: str) -> Msg:
    """The message of an amount that does not start with a number."""
    return (
        f'The amount "{amount}" must start with a number of at most 15 digits, such as 300 '
        'or 1.5, or be "适量" or "to taste".',
        f"数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，"
        "或者写成“适量”或“to taste”。",
    )


def m_amount_unit(unit: str, amount: str) -> Msg:
    """The message of an amount with an unknown unit."""
    return (f'Unknown unit "{unit}" in "{amount}".', f"数量“{amount}”里有未知单位“{unit}”。")


def m_no_unit(amount: str, ingredient: Ingredient) -> Msg:
    """The message of an amount with no unit, for an ingredient with no default unit."""
    en, zh = ingredient.name.en, ingredient.name.zh
    return (
        f'The amount "{amount}" has no unit, and the catalog gives "{en}" no default unit. '
        'Write a unit after the number, such as "300 g".',
        f"数量“{amount}”没有单位，目录也没有给“{zh}”默认单位。请在数字后面写上单位，比如“300 g”。",
    )


def m_zero(amount: str) -> Msg:
    """The message of an amount that is 0."""
    return (
        f'The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".',
        f"数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。",
    )


M_NO_ZH_NOTE: Msg = (
    "No Chinese note. Commands show the English note instead.",
    "没有中文备注。命令会改为显示英文备注。",
)
M_NO_EN_NOTE: Msg = (
    "No English note. Commands show the Chinese note instead.",
    "没有英文备注。命令会改为显示中文备注。",
)
M_NOT_A_STEPS_TABLE: Msg = (
    '"steps" must be a table. Write the line [steps] at the end of the file, '
    "and below it zh = [ ... ] and en = [ ... ].",
    "“steps”必须是表。请在文件末尾写一行 [steps]，在它下面写 zh = [ ... ] 和 en = [ ... ]。",
)
M_NO_STEPS: Msg = (
    'The recipe has no steps. Write the steps in "zh", "en", or both.',
    "菜谱没有步骤。请在“zh”、“en”或两者里写上步骤。",
)
M_NO_ZH_STEPS: Msg = (
    "No Chinese steps. Commands show the English steps instead.",
    "没有中文步骤。命令会改为显示英文步骤。",
)
M_NO_EN_STEPS: Msg = (
    "No English steps. Commands show the Chinese steps instead.",
    "没有英文步骤。命令会改为显示中文步骤。",
)

# ------------------------------------------- messages of recipe IDs and folders (2.5, 3.1)

M_NOT_A_RECIPE_ID: Msg = (
    'This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", '
    'and starts with a letter or a digit, such as "tomato-egg". Rename the file.',
    "这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，"
    "并以字母或数字开头，比如“tomato-egg”。请给文件改名。",
)
M_RESERVED_ID: Msg = (
    "This file name cannot be a recipe ID, because Windows keeps it for a device. Rename the file.",
    "这个文件名不能用作菜谱 ID，因为 Windows 把它留给设备使用。请给文件改名。",
)
M_TOML_ENDING: Msg = (
    'The file name must end with ".toml" in small letters. Rename the file.',
    "文件名必须以小写的“.toml”结尾。请给文件改名。",
)
M_FOLDER_MISSING: Msg = ("The folder is missing.", "文件夹不存在。")
M_FOLDER_IS_FILE: Msg = (
    "The folder cannot be read: it is a file.",
    "无法读取文件夹：它是一个文件。",
)
M_FOLDER_DENIED: Msg = (
    "The folder cannot be read: access is denied.",
    "无法读取文件夹：没有访问权限。",
)


def m_folder_system(reason: str) -> Msg:
    """The message of an ``OSError`` of listing a folder that has no message of its own."""
    return (
        f"The folder cannot be read. The system says: {reason}",
        f"无法读取文件夹。系统提示：{reason}",
    )


# ---------------------------------------------------------------- comparing problems


def err(place: BiText | None, msg: Msg, file: str = DISH_FILE) -> Entry:
    """Gives an expected error, with its file as a ``/`` path."""
    return (Severity.ERROR, str(Path(*file.split("/"))), place, msg[0], msg[1])


def warn(place: BiText | None, msg: Msg, file: str = DISH_FILE) -> Entry:
    """Gives an expected warning, with its file as a ``/`` path."""
    return (Severity.WARNING, str(Path(*file.split("/"))), place, msg[0], msg[1])


def view(problems: Sequence[Problem]) -> list[Entry]:
    """Gives each problem as severity, file name text, place, and its two texts.

    The file is compared as ``str``, so a test checks the case of a name on Windows too.
    """
    return [(p.severity, str(p.file), p.place, p.text(EN), p.text(ZH)) for p in problems]


def check_problems(
    problems: tuple[Problem, ...], expected: Sequence[Entry], label: object = ""
) -> None:
    """Checks a tuple of problems: its type, and then the whole list, in order."""
    assert isinstance(problems, tuple), label
    assert all(isinstance(p, Problem) for p in problems), label
    assert view(problems) == list(expected), label


def check_fails(
    folder: DataFolder,
    expected: Sequence[Entry],
    catalog: Catalog | None = dish_catalog,
    **parts: Any,
) -> None:
    """Reads the base recipe with parts changed: no recipe, and the expected problems."""
    recipe, problems = read_dish(folder, catalog, **parts)
    assert recipe is None, parts
    check_problems(problems, expected, parts)


def check_reads(
    folder: DataFolder,
    expected: Recipe,
    expected_problems: Sequence[Entry] = (),
    **parts: Any,
) -> None:
    """Reads the base recipe with parts changed: the expected recipe and problems."""
    recipe, problems = read_dish(folder, **parts)
    check_problems(problems, expected_problems, parts)
    assert recipe == expected, parts


# ---------------------------------------------------------------- the example data


def example_catalog(folder: DataFolder) -> Catalog:
    """Reads the catalog of the example folder, which has no problems."""
    catalog, problems = read_catalog(folder)
    assert problems == ()
    assert catalog is not None
    return catalog


def check_lines(
    recipe: Recipe,
    catalog: Catalog,
    tags: Sequence[str],
    lines: Sequence[tuple[str, Quantity, BiText | None]],
) -> None:
    """Checks the tags and the ingredient lines of a recipe against the catalog's objects.

    ``tags`` and the first item of each line are Chinese names, found with ``find_tag`` and
    ``find_ingredient`` and compared by ``is``.
    """
    for tag, zh in zip(recipe.tags, tags, strict=True):
        assert tag is catalog.find_tag(zh)
    for line, (zh, quantity, note) in zip(recipe.ingredients, lines, strict=True):
        assert line.ingredient is catalog.find_ingredient(zh)
        assert line.quantity == quantity
        assert line.note == note


# ---------------------------------------------------------------- denying a listing


@contextlib.contextmanager
def listing_denied(path: Path) -> Iterator[None]:
    """Makes listing a folder fail with ``PermissionError``, and undoes it afterwards.

    On Windows, it holds the folder open with the share mode 0. On Linux, it removes the read
    permission and keeps the search permission. It first checks that listing fails.
    """
    if sys.platform == "win32":
        handle = _winapi.CreateFile(
            str(path), GENERIC_READ, 0, 0, _winapi.OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, 0
        )
    else:
        path.chmod(0o100)
    try:
        with pytest.raises(PermissionError):
            os.listdir(path)  # noqa: PTH208
        yield
    finally:
        if sys.platform == "win32":
            _winapi.CloseHandle(handle)
        else:
            path.chmod(0o755)
