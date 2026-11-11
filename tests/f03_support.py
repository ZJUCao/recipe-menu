"""Helpers and example values that the F03 tests share."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import BiText, Lang

EN, ZH = Lang.EN, Lang.ZH

type Msg = tuple[str, str]
type Expected = tuple[BiText | None, Msg]

CATALOG_FILE = Path("catalog.toml")
PANTRY_FILE = Path("pantry.toml")
SETTINGS_FILE = Path("settings.toml")

# ---------------------------------------------------------- example values (design 2.4 to 2.7)

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
greens = Category("greens", BiText("Vegetables and fruit", "青菜"))
fruit = Category("Produce", BiText("Fruit", "水果"))
seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
pork = Ingredient(BiText("Pork belly", "五花肉"), meat)
tomato_again = Ingredient(BiText("tomato", "西红柿"), produce)
kale = Ingredient(BiText("Kale", "羽衣甘蓝"), produce)
scallion = Ingredient(BiText("Scallion", "葱"), produce)
choy_sum = Ingredient(BiText("Choy sum", "菜心"), produce)
jalapeno = Ingredient(BiText("Jalape\u00f1o", "墨西哥辣椒"), produce)
puree = Ingredient(BiText("Tomato pur\u00e9e", "番茄泥"), produce)
xo_sauce = Ingredient(BiText("XO sauce", "XO酱"), produce)
salt = Ingredient(BiText("Salt", "盐"), seasonings)
sugar = Ingredient(BiText("Sugar", "糖"), seasonings)
quick = Tag(BiText("quick", "快手"))

find_catalog = Catalog(
    (produce,),
    (kale, scallion, choy_sum, jalapeno, puree, xo_sauce, tomato),
    (quick,),
)
pantry_catalog = Catalog((seasonings,), (salt, sugar), ())

# ---------------------------------------------------------------- items of a catalog file (2.8)

PRODUCE_ITEM = '{ key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" }'
MEAT_ITEM = '{ key = "meat", zh = "肉类水产", en = "Meat and seafood" }'
TOMATO_ITEM = '{ zh = "番茄", en = "Tomato", category = "produce" }'
QUICK_ITEM = '{ zh = "快手", en = "quick" }'

EXAMPLE_PANTRY = ['"食用油"', '"盐"', '"糖"', '"生抽"', '"花椒"']


def ing(zh: str, en: str, category: str = "produce", unit: str | None = None) -> str:
    """Writes an ingredient item. ``unit`` is a TOML value, such as ``'"cups"'`` or ``"3"``."""
    tail = "" if unit is None else f", unit = {unit}"
    return f'{{ zh = "{zh}", en = "{en}", category = "{category}"{tail} }}'


# ---------------------------------------------------------------- writing files


def write(path: Path, text: str) -> None:
    """Writes a UTF-8 file with LF line ends, and makes its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def put_bytes(path: Path, data: bytes) -> None:
    """Writes the bytes of a file, and makes its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _list(name: str, items: Sequence[str]) -> str:
    """Writes one list of a catalog, each item on its own line."""
    if not items:
        return f"{name} = []\n"
    body = "".join(f"  {item},\n" for item in items)
    return f"{name} = [\n{body}]\n"


def catalog_text(
    categories: Sequence[str] = (),
    ingredients: Sequence[str] = (),
    tags: Sequence[str] = (),
) -> str:
    """Gives the text of a catalog from its items, in the layout of design 2.8."""
    return _list("categories", categories) + _list("ingredients", ingredients) + _list("tags", tags)


def write_catalog(
    folder: DataFolder,
    categories: Sequence[str] = (),
    ingredients: Sequence[str] = (),
    tags: Sequence[str] = (),
) -> None:
    """Writes ``catalog.toml`` of the folder from its items."""
    write(folder.catalog, catalog_text(categories, ingredients, tags))


def edit_ingredients(
    folder: DataFolder,
    changed: Mapping[int, str] | None = None,
    added: Sequence[str] = (),
) -> None:
    """Changes the example catalog: replaces ingredients by number and adds some at the end."""
    lines = folder.catalog.read_text(encoding="utf-8").split("\n")
    first = lines.index("ingredients = [")
    for number, item in (changed or {}).items():
        lines[first + number] = f"  {item},"
    last = lines.index("]", first)
    lines[last:last] = [f"  {item}," for item in added]
    write(folder.catalog, "\n".join(lines))


def write_pantry(folder: DataFolder, changed: Mapping[int, str] | None = None) -> None:
    """Writes the example pantry, with some of its five items changed by number."""
    items = list(EXAMPLE_PANTRY)
    for number, item in (changed or {}).items():
        items[number - 1] = item
    write(folder.pantry, f"pantry = [{', '.join(items)}]\n")


# ---------------------------------------------------------------- places


def at_line(number: int) -> BiText:
    """The place of a line."""
    return BiText(f"line {number}", f"第 {number} 行")


def at_item(number: int) -> BiText:
    """The place of an item of the pantry."""
    return BiText(f"item {number}", f"第 {number} 项")


def at_category(number: int) -> BiText:
    """The place of a category."""
    return BiText(f"category {number}", f"分类 {number}")


def at_ingredient(number: int) -> BiText:
    """The place of an ingredient."""
    return BiText(f"ingredient {number}", f"食材 {number}")


def at_tag(number: int) -> BiText:
    """The place of a tag."""
    return BiText(f"tag {number}", f"标签 {number}")


IN_CATEGORIES = BiText("categories", "分类")
IN_INGREDIENTS = BiText("ingredients", "食材")
IN_TAGS = BiText("tags", "标签")
IN_PANTRY = BiText("pantry", "常备清单")

# ---------------------------------------------------------------- messages: reading a file (2.3)

M_FILE_MISSING: Msg = ("The file is missing.", "文件不存在。")
M_FILE_IS_FOLDER: Msg = (
    "The file cannot be read: it is a folder.",
    "无法读取文件：它是一个文件夹。",
)
M_ACCESS_DENIED: Msg = (
    "The file cannot be read: access is denied.",
    "无法读取文件：没有访问权限。",
)
M_NOT_UTF8: Msg = (
    "The file cannot be read: it is not UTF-8 text. Save it as UTF-8.",
    "无法读取文件：它不是 UTF-8 文本。请把它另存为 UTF-8。",
)
M_MISSING_BRACKET: Msg = (
    'The file cannot be read: a closing "]" is missing.',
    "无法读取文件：缺少右方括号“]”。",
)
M_MISSING_BRACE: Msg = (
    'The file cannot be read: a closing "}" is missing. A table in braces must be on one line.',
    "无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。",
)
M_MISSING_QUOTE: Msg = (
    "The file cannot be read: a closing quotation mark is missing.",
    "无法读取文件：缺少结尾的引号。",
)
M_BAD_VALUE: Msg = (
    "The file cannot be read: a value is missing or not valid. "
    'Write a text in straight quotation marks, such as "Tomato".',
    '无法读取文件：缺少值，或者值写得不对。文字要放在英文双引号里，比如 "番茄"。',
)
M_MISSING_EQUALS: Msg = (
    'The file cannot be read: an "=" is missing after a key.',
    "无法读取文件：键后面缺少“=”。",
)
M_BAD_KEY: Msg = (
    "The file cannot be read: a key is missing or not valid. "
    "A table in braces must be on one line, and it cannot end with a comma.",
    "无法读取文件：缺少键，或者键写得不对。花括号里的表必须写在一行里，而且不能以逗号结尾。",
)
M_EXTRA_TEXT: Msg = (
    "The file cannot be read: something follows the value on this line. "
    "Write one key and its value on each line.",
    "无法读取文件：这一行的值后面还有别的内容。每行只写一个键和它的值。",
)
M_BAD_LINE: Msg = (
    'The file cannot be read: this line does not start with a key, "[", or "#".',
    "无法读取文件：这一行的开头不是键、“[”或“#”。",
)
M_DEFINED_TWICE: Msg = (
    "The file cannot be read: a key or a table is defined twice.",
    "无法读取文件：同一个键或表定义了两次。",
)
M_BAD_ESCAPE: Msg = (
    'The file cannot be read: a "\\" in a text does not start a valid escape. '
    'Write "\\\\" for one "\\", or put the text in single quotation marks.',
    "无法读取文件：文字里的“\\”没有构成有效的转义。一个“\\”要写成“\\\\”，或者把文字放在单引号里。",
)
M_CONTROL_CHARACTER: Msg = (
    "The file cannot be read: this line holds a control character, which TOML does not allow.",
    "无法读取文件：这一行有 TOML 不允许的控制字符。",
)
M_NOT_TOML: Msg = (
    "The file cannot be read: this line is not valid TOML.",
    "无法读取文件：这一行不是有效的 TOML。",
)
M_NUMBER_TOO_LONG: Msg = (
    "The file cannot be read: a number has too many digits.",
    "无法读取文件：有一个数字的位数太多。",
)
M_NESTED_TOO_DEEPLY: Msg = (
    "The file cannot be read: lists or tables are nested too deeply.",
    "无法读取文件：列表或表嵌套得太深。",
)


def m_system_error(reason: str) -> Msg:
    """The message of an ``OSError`` that has no message of its own."""
    return (
        f"The file cannot be read. The system says: {reason}",
        f"无法读取文件。系统提示：{reason}",
    )


# ------------------------------------------------------- messages: the shape of a file (2.10)

M_ITEM_NOT_A_TABLE: Msg = (
    "This item must be a table in braces, { ... }.",
    "这一项必须是放在花括号 { ... } 里的表。",
)
M_ITEM_NOT_A_TEXT: Msg = (
    "This item must be a text in quotation marks.",
    "这一项必须是放在引号里的文字。",
)
M_ITEM_EMPTY: Msg = ("This item is empty.", "这一项是空的。")

CATEGORY_KEYS: Msg = ("key, zh, and en", "key、zh 和 en")
INGREDIENT_KEYS: Msg = ("zh, en, category, and unit", "zh、en、category 和 unit")
TAG_KEYS: Msg = ("zh and en", "zh 和 en")
TOP_KEYS: Msg = ("categories, ingredients, and tags", "categories、ingredients 和 tags")


def m_missing_key(key: str) -> Msg:
    """The message of a key that is missing."""
    return (f'The key "{key}" is missing.', f"缺少键“{key}”。")


def m_not_a_list(key: str) -> Msg:
    """The message of a value that is not a list."""
    return (
        f'"{key}" must be a list in square brackets, [ ... ].',
        f"“{key}”必须是放在方括号 [ ... ] 里的列表。",
    )


def m_not_a_text(key: str) -> Msg:
    """The message of a value that is not a text."""
    return (f'"{key}" must be a text in quotation marks.', f"“{key}”必须是放在引号里的文字。")


def m_empty_text(key: str) -> Msg:
    """The message of a text that is empty."""
    return (f'"{key}" is empty.', f"“{key}”是空的。")


def m_unknown_key(key: str, keys: Msg) -> Msg:
    """The message of an unknown key, with the keys of its kind, for two or more keys."""
    return (
        f'Unknown key "{key}". The keys are {keys[0]}.',
        f"未知键“{key}”。可用的键：{keys[1]}。",
    )


def m_unknown_pantry_key(key: str) -> Msg:
    """The message of an unknown key of the pantry, which has one key."""
    return (
        f'Unknown key "{key}". The only key is pantry.',
        f"未知键“{key}”。可用的键：pantry。",
    )


# ---------------------------------------------------------------- messages of catalog (2.8, 2.9)


def _join(keys: Sequence[str]) -> Msg:
    """Joins keys as ``and_list`` does, for one to six keys."""
    if len(keys) == 1:
        return (keys[0], keys[0])
    if len(keys) == 2:
        return (f"{keys[0]} and {keys[1]}", f"{keys[0]} 和 {keys[1]}")
    return (
        ", ".join(keys[:-1]) + f", and {keys[-1]}",
        "、".join(keys[:-1]) + f" 和 {keys[-1]}",
    )


def m_unknown_category(category: str, *keys: str) -> Msg:
    """The message of an unknown category, with the keys of the kept categories."""
    en, zh = _join(keys)
    form = "The only category is" if len(keys) == 1 else "The categories are"
    return (
        f'Unknown category "{category}". {form} {en}.',
        f"未知分类“{category}”。现有分类：{zh}。",
    )


def m_no_categories(category: str) -> Msg:
    """The message of an unknown category when the catalog kept no category."""
    return (
        f'Unknown category "{category}". The catalog has no categories.',
        f"未知分类“{category}”。目录里没有分类。",
    )


def m_unknown_unit(unit: str) -> Msg:
    """The message of a unit that ``parse_unit`` does not know."""
    return (f'Unknown unit "{unit}".', f"未知单位“{unit}”。")


def m_dup_key(key: str, other: BiText) -> Msg:
    """The message of a key that an earlier category has."""
    return (
        f'The key "{key}" is also {other.en}\'s key. Keys must be unique.',
        f"键“{key}”也是{other.zh} 的键。键不能重复。",
    )


def m_dup_zh(name: str, other: BiText) -> Msg:
    """The message of a Chinese name that an earlier item has."""
    return (
        f'The Chinese name "{name}" is also {other.en}\'s name. Names must be unique.',
        f"中文名称“{name}”也是{other.zh} 的名称。名称不能重复。",
    )


def m_dup_en(name: str, other: BiText) -> Msg:
    """The message of an English name that an earlier item has."""
    return (
        f'The English name "{name}" is also {other.en}\'s name. Names must be unique.',
        f"英文名称“{name}”也是{other.zh} 的名称。名称不能重复。",
    )


def m_unknown_ingredient(name: str) -> Msg:
    """The message of a pantry item that names no ingredient."""
    return (f'Unknown ingredient "{name}".', f"未知食材“{name}”。")


# ---------------------------------------------------------------- comparing problems


def view(problems: Sequence[Problem]) -> list[Expected]:
    """Gives each problem as its place and its two texts."""
    return [(p.place, (p.text(EN), p.text(ZH))) for p in problems]


def check_problems(
    problems: tuple[Problem, ...],
    file: Path,
    expected: Sequence[Expected],
) -> None:
    """Checks a tuple of problems: its type, the severity and file of each, and the whole list."""
    assert isinstance(problems, tuple)
    assert all(isinstance(p, Problem) for p in problems)
    assert all(p.severity is Severity.ERROR for p in problems)
    assert all(p.file == file for p in problems)
    assert view(problems) == list(expected)


def check_toml(result: object, file: Path, place: BiText | None, msg: Msg) -> None:
    """Checks that ``read_toml`` gave one problem at a place."""
    assert isinstance(result, Problem)
    check_problems((result,), file, [(place, msg)])


def en_names(items: Sequence[Ingredient | Tag | Category]) -> list[str | None]:
    """Gives the English name of each item."""
    return [item.name.en for item in items]
