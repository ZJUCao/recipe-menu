"""The expected texts of F10: the tables, the helps, the messages, and the outputs of the blocks.

Every text is written out as a literal, so a test imports no message of ``search`` and reads no
prototype file. Nothing here calls an interface of F10 when the module is imported. Blocks A to F
are the blocks of the test plan: each ``PS>`` line gives the words after ``search``, and the lines
that follow it up to its count line are its output, with exit code 0 and an empty error stream.
``found`` and ``none`` give the result of a search.
"""

import shlex

from f05_texts import Result
from f09_texts import EN, RUN_HELP_COMMANDS, RUN_HELP_OPTIONS, ZH, Lines, err, out
from f09_texts import HELP as _HELP09
from f09_texts import HELP_ZH as _HELP09_ZH
from recipe_menu.lang import Lang

type Words = tuple[str, ...]
type Block = dict[Words, Result]


def found(table: Lines, count_line: str) -> Result:
    """Gives ``FOUND(T, C)``: exit code 0, the table, an empty line, and the count line."""
    return out([*table, "", count_line])


def none(count_line: str) -> Result:
    """Gives ``NONE(C)``: exit code 0 and the one line of no match."""
    return out([count_line])


TOMATO_TABLE = [
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
]
TOMATO_TABLE_ZH = [
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     名称、食材",
    "tomato-egg-noodles   番茄鸡蛋面   名称、食材",
]
SCALLION_QUICK_TABLE_ZH = [
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     食材、标签",
    "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
]
SCALLION_QUICK_TABLE = [row.replace("name, ingredient", "ingredient, tag") for row in TOMATO_TABLE]
ALL_THREE_TABLE = [row.replace("name, ingredient", "name, ingredient, tag") for row in TOMATO_TABLE]
ALL_THREE_TABLE_ZH = [row.replace("名称、食材", "名称、食材、标签") for row in TOMATO_TABLE_ZH]
EMPTY = 'A word is empty. Look for a name, such as "recipe-menu search tomato".'
EMPTY_ZH = "有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。"

# The outputs of the prototype and of the design's examples that no block holds.
PROTOTYPE_ZH = found(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“葱”和“quick”。")
MAPO_TABLE = ["ID          Name        Matched in", "mapo-tofu   Mapo tofu   name"]
PORK_TABLE = [
    "ID                 Name                     Matched in",
    "mapo-tofu          Mapo tofu                ingredient",
    "red-braised-pork   Red-braised pork belly   name, ingredient",
]
NOODLE_TABLE = [
    "ID                   Name                     Matched in",
    "tomato-egg-noodles   Tomato and egg noodles   name, ingredient, tag",
]
NOODLE_TABLE_ZH = [
    "ID                   名称         匹配于",
    "tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签",
]
TOMATO = found(TOMATO_TABLE, '2 recipes match "番茄".')
TOMATO_ZH = found(TOMATO_TABLE_ZH, "2 个菜谱匹配“番茄”。")
MAPO_FOUND = found(MAPO_TABLE, '1 recipe matches "mapo".')
PORK_FOUND = found(PORK_TABLE, '2 recipes match "pork".')
AND_EGG_FOUND = found(
    [TOMATO_TABLE[0], *(row.replace("name, ingredient", "name") for row in TOMATO_TABLE[1:])],
    '2 recipes match "and egg".',
)
NOODLE_FOUND = found(NOODLE_TABLE, '1 recipe matches "scallion", "QUICK", and "noodle".')
NOODLE_FOUND_ZH = found(NOODLE_TABLE_ZH, "1 个菜谱同时匹配“葱”、“quick”和“面”。")

# ---------------------------------------------------------------- the messages of cli

TOO_FEW = (
    'An argument is missing. Write "recipe-menu search WORD...".',
    "缺少参数。请写成“recipe-menu search 词...”。",
)


def too_few(lang: Lang = EN) -> Result:
    """Gives exit code 2 and the two lines of ``TOO_FEW_ARGUMENTS`` for ``search``."""
    index = 1 if lang is ZH else 0
    return err(2, [TOO_FEW[index], RUN_HELP_COMMANDS[index]])


def no_option(option: str, lang: Lang = EN) -> Result:
    """Gives exit code 2 and the two lines of ``UNKNOWN_OPTION`` for ``search`` and an option."""
    if lang is ZH:
        first = f"“search”没有选项“{option}”。它没有自己的选项。"
        return err(2, [first, RUN_HELP_OPTIONS[1]])
    first = f'"search" has no option "{option}". It has no options of its own.'
    return err(2, [first, RUN_HELP_OPTIONS[0]])


def empty_word(lang: Lang = EN) -> Result:
    """Gives exit code 2 and the one line of ``EMPTY_WORD``."""
    return err(2, [EMPTY_ZH if lang is ZH else EMPTY])


# ---------------------------------------------------------------- the help

_COMMANDS = [
    "Commands:",
    "  init             Create the data folder with example data.",
    "  check            Check every data file for mistakes.",
    "  list             List the recipes.",
    "  show ID          Show one recipe.",
    "  search WORD...   Find recipes by name, ingredient, or tag.",
    "",
    "Options:",
    "  --lang en|zh     The language of the output. Default: the settings, else English.",
    "  --data FOLDER    The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version        Show the version.",
    "  --help           Show this help.",
]
_COMMANDS_ZH = [
    "命令：",
    "  init             创建数据文件夹和示例数据。",
    "  check            检查每个数据文件有没有错误。",
    "  list             列出菜谱。",
    "  show ID          查看一个菜谱。",
    "  search 词...     按名称、食材或标签找菜谱。",
    "",
    "选项：",
    "  --lang en|zh     输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹    数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version        显示版本。",
    "  --help           显示这份帮助。",
]
HELP = [*_HELP09[:4], *_COMMANDS, *_HELP09[-2:]]
HELP_ZH = [*_HELP09_ZH[:4], *_COMMANDS_ZH, *_HELP09_ZH[-2:]]

# ---------------------------------------------------------------- blocks A to F

_BLOCK_A = """\
PS> recipe-menu search 炒蛋
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name

1 recipe matches "炒蛋".
PS> recipe-menu search 鸡蛋
ID                   Name                      Matched in
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

2 recipes match "鸡蛋".
PS> recipe-menu search 鸡蛋 --lang zh
ID                   名称         匹配于
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

2 个菜谱匹配“鸡蛋”。
PS> recipe-menu search scallion
ID                   Name                      Matched in
cola-wings           Cola chicken wings        ingredient
mapo-tofu            Mapo tofu                 ingredient
red-braised-pork     Red-braised pork belly    ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    ingredient

5 recipes match "scallion".
PS> recipe-menu search scallion --lang zh
ID                   名称         匹配于
cola-wings           可乐鸡翅     食材
mapo-tofu            麻婆豆腐     食材
red-braised-pork     红烧肉       食材
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   食材

5 个菜谱匹配“scallion”。
PS> recipe-menu search home
ID                 Name                      Matched in
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    tag
tomato-egg         Tomato and egg stir-fry   tag

4 recipes match "home".
PS> recipe-menu search 家常 --lang zh
ID                 名称       匹配于
cola-wings         可乐鸡翅   标签
mapo-tofu          麻婆豆腐   标签
red-braised-pork   红烧肉     标签
tomato-egg         番茄炒蛋   标签

4 个菜谱匹配“家常”。
PS> recipe-menu search 素
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   tag

1 recipe matches "素".
PS> recipe-menu search vegetarian --lang zh
ID         名称       匹配于
choy-sum   清炒菜心   标签

1 个菜谱匹配“vegetarian”。
PS> recipe-menu search staple
ID                   Name                     Matched in
rice                 Steamed rice             tag
tomato-egg-noodles   Tomato and egg noodles   tag

2 recipes match "staple".
PS> recipe-menu search 主食 --lang zh
ID                   名称         匹配于
rice                 米饭         标签
tomato-egg-noodles   番茄鸡蛋面   标签

2 个菜谱匹配“主食”。
PS> recipe-menu search 豆瓣
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient

1 recipe matches "豆瓣".
PS> recipe-menu search red-braised
ID                 Name                     Matched in
red-braised-pork   Red-braised pork belly   name

1 recipe matches "red-braised".
PS> recipe-menu search "choy sum"
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   name, ingredient

1 recipe matches "choy sum".
PS> recipe-menu search 鸡
ID                   Name                      Matched in
cola-wings           Cola chicken wings        name, ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "鸡".
PS> recipe-menu search -fr
ID           Name                      Matched in
choy-sum     Stir-fried choy sum       name
tomato-egg   Tomato and egg stir-fry   name

2 recipes match "-fr".
PS> recipe-menu search -
ID                 Name                      Matched in
choy-sum           Stir-fried choy sum       name
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    name, tag
tomato-egg         Tomato and egg stir-fry   name, tag

5 recipes match "-".
PS> recipe-menu search MAPO --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“MAPO”。
PS> recipe-menu search egg noodle
ID                   Name                     Matched in
tomato-egg-noodles   Tomato and egg noodles   name, ingredient

1 recipe matches "egg" and "noodle".
PS> recipe-menu search egg noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材

1 个菜谱同时匹配“egg”和“noodle”。
PS> recipe-menu search 番茄 家常
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient, tag

1 recipe matches "番茄" and "家常".
PS> recipe-menu search pork spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient, tag

1 recipe matches "pork" and "spicy".
PS> recipe-menu search home 葱
ID                 Name                      Matched in
cola-wings         Cola chicken wings        ingredient, tag
mapo-tofu          Mapo tofu                 ingredient, tag
red-braised-pork   Red-braised pork belly    ingredient, tag
tomato-egg         Tomato and egg stir-fry   ingredient, tag

4 recipes match "home" and "葱".
PS> recipe-menu search 米饭 主食
ID     Name           Matched in
rice   Steamed rice   name, tag

1 recipe matches "米饭" and "主食".
PS> recipe-menu search 米饭 主食 --lang zh
ID     名称   匹配于
rice   米饭   名称、标签

1 个菜谱同时匹配“米饭”和“主食”。
PS> recipe-menu search spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   tag

1 recipe matches "spicy".
PS> recipe-menu search 辣 --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   标签

1 个菜谱匹配“辣”。
PS> recipe-menu search rice
ID     Name           Matched in
rice   Steamed rice   name, ingredient

1 recipe matches "rice".
PS> recipe-menu search 米 --lang zh
ID     名称   匹配于
rice   米饭   名称、食材

1 个菜谱匹配“米”。
PS> recipe-menu search scallion QUICK noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签

1 个菜谱同时匹配“scallion”、“QUICK”和“noodle”。
PS> recipe-menu search mapo --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“mapo”。
PS> recipe-menu search cola
ID           Name                 Matched in
cola-wings   Cola chicken wings   name, ingredient

1 recipe matches "cola".
PS> recipe-menu search cola --lang zh
ID           名称       匹配于
cola-wings   可乐鸡翅   名称、食材

1 个菜谱匹配“cola”。
"""

_BLOCK_B = """\
PS> recipe-menu search boiled
ID           Name           Matched in
boiled-egg   Boiled egg     name
water        Boiled water   name

2 recipes match "boiled".
PS> recipe-menu search boiled --lang zh
ID           名称         匹配于
boiled-egg   Boiled egg   名称
water        白开水       名称

2 个菜谱匹配“boiled”。
PS> recipe-menu search 蒸
ID            Name   Matched in
steamed-egg   蒸蛋   name

1 recipe matches "蒸".
PS> recipe-menu search 蒸 --lang zh
ID            名称   匹配于
steamed-egg   蒸蛋   名称

1 个菜谱匹配“蒸”。
PS> recipe-menu search egg
ID                   Name                      Matched in
boiled-egg           Boiled egg                name, ingredient
steamed-egg          蒸蛋                      ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

4 recipes match "egg".
PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
boiled-egg           Boiled egg   名称、食材
steamed-egg          蒸蛋         食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

4 个菜谱匹配“egg”。
"""

_BLOCK_C = """\
PS> recipe-menu search egg
ID                   Name                      Matched in
aubergine            Braised aubergine         ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "egg".
PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
aubergine            烧茄子       食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

3 个菜谱匹配“egg”。
PS> recipe-menu search 茄
ID                   Name                      Matched in
aubergine            Braised aubergine         name, ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "茄".
PS> recipe-menu search plant
ID          Name                Matched in
aubergine   Braised aubergine   ingredient

1 recipe matches "plant".
"""

_BLOCK_D = """\
PS> recipe-menu search cr\u00e8me
ID      Name            Matched in
creme   Cr\u00e8me caramel   name

1 recipe matches "cr\u00e8me".
PS> recipe-menu search Cr\u00e8me --lang zh
ID      名称       匹配于
creme   焦糖布丁   名称

1 个菜谱匹配“Cr\u00e8me”。
PS> recipe-menu search CARAMEL
ID      Name            Matched in
creme   Cr\u00e8me caramel   name

1 recipe matches "CARAMEL".
"""

_BLOCK_E = """\
PS> recipe-menu search long
ID       Name                Matched in
a-long   A long first line   name
         end

1 recipe matches "long".
PS> recipe-menu search long --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“long”。
PS> recipe-menu search 尾 --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“尾”。
PS> recipe-menu search 大米
ID       Name                Matched in
a-long   A long first line   ingredient
         end
rice     Steamed rice        ingredient

2 recipes match "大米".
PS> recipe-menu search 大米 --lang zh
ID       名称           匹配于
a-long   长长的第一行   食材
         尾
rice     米饭           食材

2 个菜谱匹配“大米”。
PS> recipe-menu search steamed
ID     Name           Matched in
rice   Steamed rice   name

1 recipe matches "steamed".
"""

_BLOCK_F = """\
PS> recipe-menu search 番茄
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient

1 recipe matches "番茄".
PS> recipe-menu search 番茄 --lang zh
ID           名称       匹配于
tomato-egg   番茄炒蛋   名称、食材

1 个菜谱匹配“番茄”。
"""


def _parse(text: str) -> Block:
    """Turns the ``PS>`` lines of a block into a dict from the words to the result of the line."""
    block: Block = {}
    for part in text.split("PS> recipe-menu search ")[1:]:
        command, *lines = part.rstrip("\n").split("\n")
        key = tuple(shlex.split(command))
        assert key not in block, key
        block[key] = out(lines)
    return block


BLOCK_A = _parse(_BLOCK_A)
BLOCK_B = _parse(_BLOCK_B)
BLOCK_C = _parse(_BLOCK_C)
BLOCK_D = _parse(_BLOCK_D)
BLOCK_E = _parse(_BLOCK_E)
BLOCK_F = _parse(_BLOCK_F)
