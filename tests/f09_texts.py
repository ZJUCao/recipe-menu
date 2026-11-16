"""The expected texts of F09, and the problems of the expected reports.

The texts are the outputs of ``list`` and ``show``, the helps, and the messages.

Every text is written out as a literal, so a test imports no message of ``browse`` and reads no
prototype file. Nothing here calls an interface of F09 when the module is imported.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path

from f05_texts import Msg, Result, err_result, lines_text, stopped
from f07_texts import Prob
from f08_texts import HELP as _HELP08
from f08_texts import HELP_ZH as _HELP08_ZH
from recipe_menu.lang import Lang

EN, ZH = Lang.EN, Lang.ZH

type Lines = Sequence[str]


def out(lines: Lines) -> Result:
    """Gives the result ``(0, out L)``: the lines on stdout, each ended by a line break."""
    return 0, lines_text(*lines), ""


def err(code: int, lines: Lines) -> Result:
    """Gives the result ``(c, err L)``: the lines on stderr, each ended by a line break."""
    return err_result(code, *lines)


def pick(lines: Lines, *numbers: int) -> list[str]:
    """Gives the lines with the given numbers, counted from 1."""
    return [lines[number - 1] for number in numbers]


def patch(lines: Lines, changes: Mapping[int, str]) -> list[str]:
    """Gives a copy of the lines with the lines at the given numbers, from 1, replaced."""
    return [changes.get(number, line) for number, line in enumerate(lines, 1)]


def tagged(lines: Lines, numbers: Sequence[int], count_line: str) -> list[str]:
    """Gives the table lines of a list with a tag: those lines, an empty line, and the count."""
    return [*pick(lines, *numbers), "", count_line]


# ---------------------------------------------------------------- list

LIST = [
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "cola-wings           Cola chicken wings        2          home-style",
    "mapo-tofu            Mapo tofu                 2          spicy, home-style",
    "red-braised-pork     Red-braised pork belly    2          home-style",
    "rice                 Steamed rice              2          staple",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
    "",
    "7 recipes.",
]
LIST_ZH = [
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣、家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "",
    "共 7 个菜谱。",
]
IDS = [line.split()[0] for line in LIST[1:8]]
QUICK = tagged(LIST, (1, 2, 7, 8), '3 recipes have the tag "quick".')
QUICK_ZH = tagged(LIST_ZH, (1, 2, 7, 8), "共 3 个菜谱带有标签“快手”。")
TAGS_LINE = "The tags are quick, home-style, vegetarian, spicy, and staple."
BREAKFAST = f'Unknown tag "breakfast". {TAGS_LINE}'
BREAKFAST_ZH = "未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。"
VEG = tagged(LIST, (1, 2), '1 recipe has the tag "vegetarian".')
VEG_ZH = tagged(LIST_ZH, (1, 2), "共 1 个菜谱带有标签“素”。")
INIT_LIST = [
    "ID           Name                      Servings   Tags",
    "tomato-egg   Tomato and egg stir-fry   2          quick, home-style",
    "",
    "1 recipe.",
]
INIT_LIST_ZH = [
    "ID           名称       份数   标签",
    "tomato-egg   番茄炒蛋   2      快手、家常",
    "",
    "共 1 个菜谱。",
]
EXTRA = [
    "ID                   Name                      Servings   Tags",
    "boiled-egg           Boiled egg                1",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "cola-wings           Cola chicken wings        2          home-style",
    "mapo-tofu            Mapo tofu                 2          spicy, home-style",
    "red-braised-pork     Red-braised pork belly    2          home-style",
    "rice                 Steamed rice              2          staple",
    "steamed-egg          蒸蛋                      3          quick, vegetarian",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
    "water                Boiled water              1",
    "",
    "10 recipes.",
]
EXTRA_ZH = [
    "ID                   名称         份数   标签",
    "boiled-egg           Boiled egg   1",
    "choy-sum             清炒菜心     2      快手、素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣、家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "steamed-egg          蒸蛋         3      快手、素",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "water                白开水       1",
    "",
    "共 10 个菜谱。",
]
EXTRA_VEG = tagged(EXTRA, (1, 3, 8), '2 recipes have the tag "vegetarian".')
LONG = [
    "ID       Name                Servings   Tags",
    "a-long   A long first line   2          quick",
    "         end",
    "rice     Steamed rice        2          staple",
    "",
    "2 recipes.",
]
LONG_ZH = [
    "ID       名称           份数   标签",
    "a-long   长长的第一行   2      快手",
    "         尾",
    "rice     米饭           2      主食",
    "",
    "共 2 个菜谱。",
]
LONG_STAPLE = tagged(LONG, (1, 4), '1 recipe has the tag "staple".')
LONG_QUICK = tagged(LONG, (1, 2, 3), '1 recipe has the tag "quick".')
LONG_STAPLE_ZH = tagged(LONG_ZH, (1, 4), "共 1 个菜谱带有标签“主食”。")
LONG_QUICK_ZH = tagged(LONG_ZH, (1, 2, 3), "共 1 个菜谱带有标签“快手”。")
S04_LIST = [
    "ID               Name                      Servings   Tags",
    "cucumber-salad   Smashed cucumber          2          quick, vegetarian",
    "tomato-egg       Tomato and egg stir-fry   2          quick, home-style",
    "",
    "2 recipes.",
]

# ---------------------------------------------------------------- show

TOMATO = [
    "Tomato and egg stir-fry  番茄炒蛋",
    "Servings: 2   Tags: quick, home-style",
    "",
    "Ingredients",
    "  Tomato        300 g      cut into wedges",
    "  Egg           3 pieces",
    "  Scallion      1 stalk    chopped",
    "  Salt          to taste",
    "  Sugar         1 tsp",
    "  Cooking oil   2 tbsp",
    "",
    "Steps",
    "  1. Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.",
    "  2. Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.",
    "  3. Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.",
    "  4. Return the eggs, season with salt, and scatter the scallion on top.",
]
FOUR_ZH = [
    "番茄炒蛋  Tomato and egg stir-fry",
    "份数：4（菜谱按 2 份写）   标签：快手、家常",
    "",
    "食材",
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  葱       2 根     切葱花",
    "  盐       适量",
    "  糖       2 茶匙",
    "  食用油   4 汤匙",
    "",
    "步骤",
    "  1. 番茄切块。鸡蛋加少许盐打散。",
    "  2. 热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。",
    "  3. 下剩下的油，炒番茄至软，加糖。",
    "  4. 倒回鸡蛋，加盐调味，撒上葱花。",
]
TOMATO_ZH = patch(
    FOUR_ZH,
    {
        2: "份数：2   标签：快手、家常",
        5: "  番茄     300 g    切块",
        6: "  鸡蛋     3 个",
        7: "  葱       1 根     切葱花",
        8: "  盐       适量",
        9: "  糖       1 茶匙",
        10: "  食用油   2 汤匙",
    },
)
FOUR = patch(
    TOMATO,
    {
        2: "Servings: 4 (the recipe makes 2)   Tags: quick, home-style",
        5: "  Tomato        600 g      cut into wedges",
        6: "  Egg           6 pieces",
        7: "  Scallion      2 stalks   chopped",
        8: "  Salt          to taste",
        9: "  Sugar         2 tsp",
        10: "  Cooking oil   4 tbsp",
    },
)
STEPS_ZH = [
    "五花肉冷水下锅，焯水后捞出。",
    "小火把冰糖炒成焦糖色，下五花肉翻炒上色。",
    "加生抽、姜片和热水，没过肉，小火炖 1 小时。",
    "大火收汁，撒上葱段。",
]
PORK = [
    "Red-braised pork belly  红烧肉",
    "Servings: 2   Tags: home-style",
    "",
    "Ingredients",
    "  Pork belly   1 jin      cut into 3 cm cubes",
    "  Rock sugar   30 g",
    "  Soy sauce    2 tbsp",
    "  Ginger       3 slices",
    "  Scallion     2 stalks",
    "",
    "Steps (no English steps, so these are the Chinese steps)",
    *[f"  {number}. {step}" for number, step in enumerate(STEPS_ZH, 1)],
]
PORK_ZH = [
    "红烧肉  Red-braised pork belly",
    "份数：2   标签：家常",
    "",
    "食材",
    "  五花肉   1 斤     切成 3 厘米见方的块",
    "  冰糖     30 g",
    "  生抽     2 汤匙",
    "  姜       3 片",
    "  葱       2 根",
    "",
    "步骤",
    *PORK[11:],
]
MAPO = 'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.'
MAPO_ZH = "没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。"
RICE = [
    "Steamed rice  米饭",
    "Servings: 2   Tags: staple",
    "",
    "Ingredients",
    "  Rice   160 g",
    "",
    "Steps",
    "  1. Rinse the rice, add water, and soak it for 20 minutes.",
    "  2. Cook it in a rice cooker, and let it rest for 10 minutes.",
]
BOILED = [
    "Boiled egg",
    "Servings: 1",
    "",
    "Ingredients",
    "  Egg    2 pieces   at room temperature",
    "  Salt   to taste",
    "",
    "Steps",
    "  1. Boil the eggs for 8 minutes.",
]
BOILED_ZH = [
    "Boiled egg",
    "份数：1",
    "",
    "食材",
    "  鸡蛋   2 个   at room temperature",
    "  盐     适量",
    "",
    "步骤（没有中文步骤，所以这里是英文步骤）",
    "  1. Boil the eggs for 8 minutes.",
]
WATER = [
    "Boiled water  白开水",
    "Servings: 1",
    "",
    "Steps",
    "  1. Boil the water.",
]
WATER_ZH = ["白开水  Boiled water", "份数：1", "", "步骤", "  1. 把水烧开。"]
STEAMED = [
    "蒸蛋",
    "Servings: 3   Tags: quick, vegetarian",
    "",
    "Ingredients",
    "  Egg        2 pieces   打散",
    "  Scallion   1 stalk    切葱花",
    "  Salt       to taste",
    "",
    "Steps (no English steps, so these are the Chinese steps)",
    "  1. 鸡蛋加温水和盐打散。",
    "  2. 撒上葱花，蒸 10 分钟。",
]
STEAMED_ZH = [
    "蒸蛋",
    "份数：3   标签：快手、素",
    "",
    "食材",
    "  鸡蛋   2 个   打散",
    "  葱     1 根   切葱花",
    "  盐     适量",
    "",
    "步骤",
    "  1. 鸡蛋加温水和盐打散。",
    "  2. 撒上葱花，蒸 10 分钟。",
]
CUCUMBER = [
    "Smashed cucumber  拍黄瓜",
    "Servings: 2   Tags: quick, vegetarian",
    "",
    "Ingredients",
    "  Cucumber   2 pieces",
    "  Garlic     2 cloves",
    "",
    "Steps",
    "  1. Smash the cucumbers and toss them with the garlic.",
]
CUCUMBER_ZH = [
    "拍黄瓜  Smashed cucumber",
    "份数：2   标签：快手、素",
    "",
    "食材",
    "  黄瓜   2 个",
    "  大蒜   2 瓣",
    "",
    "步骤",
    "  1. 黄瓜拍碎，加蒜末拌匀。",
]

# ---------------------------------------------------------------- the help

HELP = [
    *_HELP08[:7],
    "  list            List the recipes.",
    "  show ID         Show one recipe.",
    *_HELP08[7:],
]
HELP_ZH = [
    *_HELP08_ZH[:7],
    "  list            列出菜谱。",
    "  show ID         查看一个菜谱。",
    *_HELP08_ZH[7:],
]
LIST_HELP = ("List the recipes.", "列出菜谱。")
SHOW_HELP = ("Show one recipe.", "查看一个菜谱。")

# ---------------------------------------------------------------- the messages of the readers

FILE_MISSING: Msg = ("The file is missing.", "文件不存在。")
FILE_IS_FOLDER: Msg = (
    "The file cannot be read: it is a folder.",
    "无法读取文件：它是一个文件夹。",
)
MISSING_BRACE: Msg = (
    'The file cannot be read: a closing "}" is missing. A table in braces must be on one line.',
    "无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。",
)
FOLDER_MISSING: Msg = ("The folder is missing.", "文件夹不存在。")
FOLDER_IS_FILE: Msg = (
    "The folder cannot be read: it is a file.",
    "无法读取文件夹：它是一个文件。",
)
NOT_A_RECIPE_ID_FILE: Msg = (
    'This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", '
    'and starts with a letter or a digit, such as "tomato-egg". Rename the file.',
    "这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，"
    "比如“tomato-egg”。请给文件改名。",
)
TOML_ENDING_NOT_SMALL: Msg = (
    'The file name must end with ".toml" in small letters. Rename the file.',
    "文件名必须以小写的“.toml”结尾。请给文件改名。",
)
SERVINGS_ZERO: Msg = (
    "Servings must be a whole number of 1 or more, not 0.",
    "份数必须是不小于 1 的整数，不能是 0。",
)
UNKNOWN_MEAL: Msg = (
    'Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
    "未知餐次“supper”。可用的餐次：breakfast、lunch 和 dinner。",
)


def unknown_ingredient(name: str) -> Msg:
    """Gives ``UNKNOWN_INGREDIENT`` of a recipe for a name."""
    return (
        f'Unknown ingredient "{name}". Add it to the catalog, or use its name in the catalog.',
        f"未知食材“{name}”。请把它加入目录，或改用目录里的名称。",
    )


def unknown_tag_of_recipe(tag: str) -> Msg:
    """Gives ``UNKNOWN_TAG`` of a recipe for a tag."""
    return (
        f'Unknown tag "{tag}". Add it to the catalog\'s tags.',
        f"未知标签“{tag}”。请把它加入目录里的标签。",
    )


P_LINE_11: Msg = ("line 11", "第 11 行")
P_INGREDIENT_1: Msg = ("ingredient 1", "食材 1")
P_INGREDIENT_3: Msg = ("ingredient 3", "食材 3")
P_TAGS: Msg = ("tags", "标签")
P_SERVINGS: Msg = ("servings", "份数")
P_MEALS: Msg = ("meals", "餐次")

E_NO_CATALOG = Prob("catalog.toml", None, FILE_MISSING)
E_BRACE = Prob("catalog.toml", P_LINE_11, MISSING_BRACE)
E_NO_RECIPES = Prob("recipes", None, FOLDER_MISSING)
E_RECIPES_FILE = Prob("recipes", None, FOLDER_IS_FILE)
E_RICE_BOWL = Prob("recipes/Rice Bowl.toml", None, NOT_A_RECIPE_ID_FILE)
E_CAPITAL = Prob("recipes/rice.TOML", None, TOML_ENDING_NOT_SMALL)
E_FOLDER_X = Prob("recipes/x.toml", None, FILE_IS_FOLDER)
E_MAPO = Prob("recipes/mapo-tofu.toml", P_INGREDIENT_3, unknown_ingredient("豆瓣酱"))
E_RICE_ZERO = Prob("recipes/rice.toml", P_SERVINGS, SERVINGS_ZERO)
E_SETTINGS = Prob("settings.toml", P_MEALS, UNKNOWN_MEAL)
E_CUCUMBER = Prob("recipes/cucumber-salad.toml", P_INGREDIENT_1, unknown_ingredient("黄瓜"))
E_CHOY_TAG_VEG = Prob("recipes/choy-sum.toml", P_TAGS, unknown_tag_of_recipe("素"))
E_CHOY_TAG_QUICK = Prob("recipes/choy-sum.toml", P_TAGS, unknown_tag_of_recipe("快手"))


def pair(problem: Prob, lang: Lang = EN) -> tuple[str, str]:
    """Gives the line of the place and the text of a problem, with the system's separator."""
    index = 1 if lang is ZH else 0
    where = str(Path(*problem.file.split("/")))
    if problem.place is not None:
        where += ("，" if lang is ZH else ", ") + problem.place[index]
    return where, problem.msg[index]


def stop(problem: Prob, lang: Lang = EN) -> Result:
    """Gives the result of ``stop_at_error`` for a problem: exit code 1 and three lines."""
    where, what = pair(problem, lang)
    return stopped(where, what, lang)


# ---------------------------------------------------------------- the messages of the commands

RUN_HELP_COMMANDS = (
    'Run "recipe-menu --help" to see the commands.',
    "运行“recipe-menu --help”查看命令。",
)
RUN_HELP_OPTIONS = (
    'Run "recipe-menu --help" to see the options.',
    "运行“recipe-menu --help”查看选项。",
)


def not_a_recipe_id(value: str, lang: Lang = EN) -> str:
    """Gives ``NOT_A_RECIPE_ID`` of ``show`` for a value."""
    if lang is ZH:
        return f"“{value}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。"
    return f'"{value}" is not a recipe ID. Run "recipe-menu list" to see the IDs.'


def servings_not_1_to_100(value: str, lang: Lang = EN) -> str:
    """Gives ``SERVINGS_NOT_1_TO_100`` for a value."""
    if lang is ZH:
        return f"--servings 必须是 1 到 100 之间的整数，不能是“{value}”。"
    return f'--servings must be a whole number from 1 to 100, not "{value}".'


def unknown_id(value: str, lang: Lang = EN) -> str:
    """Gives ``UNKNOWN_ID`` for an ID."""
    if lang is ZH:
        return f"没有 ID 为“{value}”的菜谱。运行“recipe-menu search {value}”查找它。"
    return f'No recipe has the ID "{value}". Run "recipe-menu search {value}" to find it.'


def unknown_tag(value: str) -> str:
    """Gives ``UNKNOWN_TAG`` in English for a value, with the five tags of the example."""
    return f'Unknown tag "{value}". {TAGS_LINE}'
