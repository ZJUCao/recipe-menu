"""The expected texts of F13: the output of ``shop`` for the example week, its files, and the lines.

Every text is written out as a literal, so a test reads no message of ``shop`` or of ``datafile``
and no prototype file. The two outputs and the file of the Chinese run are those of the F13
prototype, the file of an English run follows the F13 design, and each output ends with the full
path of the list file. The module also holds the lines of a week with no dish, of a failed save,
and of a parent that is not a folder. Nothing here calls an interface of F13 when the module is
imported. At import the module holds lists of texts, two byte strings, and functions. The texts
of a problem of the readers and of its stop lines are in ``f07_texts`` and ``f09_texts``.
"""

from pathlib import Path

from f05_texts import Msg, lines_text

# ---------------------------------------------------------------- the example week 2026-W47

_EN_GROUPS = [
    "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes",
    "",
    "Vegetables and fruit",
    "  Tomato          600 g",
    "  Choy sum        1.5 kg",
    "  Scallion        5 stalks",
    "  Ginger          6 slices",
    "  Garlic          11 cloves",
    "Meat and seafood",
    "  Minced pork     100 g",
    "  Chicken wings   1 kg",
    "Eggs, dairy, and tofu",
    "  Egg             5 pieces",
    "  Tofu            1 block",
    "Rice, flour, and oil",
    "  Rice            640 g",
    "  Noodles         200 g",
    "Seasonings",
    "  Doubanjiang     15 ml",
    "  White pepper    to taste",
    "Other",
    "  Cola            2 cans",
    "",
    "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, "
    "Sichuan pepper",
    "",
]
_ZH_GROUPS = [
    "2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜",
    "",
    "蔬菜水果",
    "  番茄         600 g",
    "  菜心         1.5 kg",
    "  葱           5 根",
    "  姜           6 片",
    "  大蒜         11 瓣",
    "肉类水产",
    "  猪肉末       100 g",
    "  鸡翅中       1 kg",
    "蛋奶豆制品",
    "  鸡蛋         5 个",
    "  豆腐         1 块",
    "米面粮油",
    "  大米         640 g",
    "  面条         200 g",
    "调味品",
    "  郫县豆瓣酱   15 ml",
    "  白胡椒粉     适量",
    "其他",
    "  可乐         2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
    "",
]


def shop_47(path: Path | str) -> list[str]:
    """Gives the 26 lines of the English output for 2026-W47, saved at the list file ``path``."""
    return [*_EN_GROUPS, f"Saved {path}"]


def shop_47_zh(path: Path | str) -> list[str]:
    """Gives the 26 lines of the Chinese output for 2026-W47, saved at the list file ``path``."""
    return [*_ZH_GROUPS, f"已保存 {path}"]


_FILE_ZH = [
    "# 2026-W47 购物清单",
    "",
    "2026年11月16日至22日：4 餐，9 道菜。",
    "",
    "## 蔬菜水果",
    "",
    "- [ ] 番茄 600 g",
    "- [ ] 菜心 1.5 kg",
    "- [ ] 葱 5 根",
    "- [ ] 姜 6 片",
    "- [ ] 大蒜 11 瓣",
    "",
    "## 肉类水产",
    "",
    "- [ ] 猪肉末 100 g",
    "- [ ] 鸡翅中 1 kg",
    "",
    "## 蛋奶豆制品",
    "",
    "- [ ] 鸡蛋 5 个",
    "- [ ] 豆腐 1 块",
    "",
    "## 米面粮油",
    "",
    "- [ ] 大米 640 g",
    "- [ ] 面条 200 g",
    "",
    "## 调味品",
    "",
    "- [ ] 郫县豆瓣酱 15 ml",
    "- [ ] 白胡椒粉 适量",
    "",
    "## 其他",
    "",
    "- [ ] 可乐 2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
]
_FILE_EN = [
    "# Shopping list for 2026-W47",
    "",
    "16 to 22 November 2026: 4 meals, 9 dishes.",
    "",
    "## Vegetables and fruit",
    "",
    "- [ ] Tomato 600 g",
    "- [ ] Choy sum 1.5 kg",
    "- [ ] Scallion 5 stalks",
    "- [ ] Ginger 6 slices",
    "- [ ] Garlic 11 cloves",
    "",
    "## Meat and seafood",
    "",
    "- [ ] Minced pork 100 g",
    "- [ ] Chicken wings 1 kg",
    "",
    "## Eggs, dairy, and tofu",
    "",
    "- [ ] Egg 5 pieces",
    "- [ ] Tofu 1 block",
    "",
    "## Rice, flour, and oil",
    "",
    "- [ ] Rice 640 g",
    "- [ ] Noodles 200 g",
    "",
    "## Seasonings",
    "",
    "- [ ] Doubanjiang 15 ml",
    "- [ ] White pepper to taste",
    "",
    "## Other",
    "",
    "- [ ] Cola 2 cans",
    "",
    "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, "
    "Sichuan pepper",
]


def _file_bytes(lines: list[str]) -> bytes:
    """Gives the lines as UTF-8 bytes, each ended by LF, the last one included."""
    return lines_text(*lines).encode("utf-8")


# The file of the Chinese run, the block "The saved file" of the prototype, and of an English run.
PROTOTYPE_FILE = _file_bytes(_FILE_ZH)
FILE_47 = _file_bytes(_FILE_EN)
LINES_FILE_ZH = _FILE_ZH
LINES_FILE_EN = _FILE_EN

# ---------------------------------------------------------------- a week with no dish


def no_dishes(week: str) -> str:
    """Gives ``NO_DISHES`` in English for a week."""
    return f"The menu for {week} has no dishes, so there is nothing to buy. No file was saved."


def no_dishes_zh(week: str) -> str:
    """Gives ``NO_DISHES`` in Chinese for a week."""
    return f"{week} 的菜单没有菜，所以没有要买的东西。没有保存文件。"


# ---------------------------------------------------------------- a failed save


def shop_fail(path: Path | str, msg: Msg) -> list[str]:
    """Gives the three lines of a failure in English: the list file, the problem, and the end."""
    return [str(path), f"  {msg[0]}", "No file was saved."]


def shop_fail_zh(path: Path | str, msg: Msg) -> list[str]:
    """Gives the three lines of a failure in Chinese."""
    return [str(path), f"  {msg[1]}", "没有保存文件。"]


def shop_left(path: Path | str, msg: Msg, temp: Path | str) -> list[str]:
    """Gives the three lines of a failure in English when ``temp`` could not be removed."""
    last = f"No file was saved, but shop could not remove {temp}. Delete it."
    return [str(path), f"  {msg[0]}", last]


def shop_left_zh(path: Path | str, msg: Msg, temp: Path | str) -> list[str]:
    """Gives the three lines of a failure in Chinese when ``temp`` could not be removed."""
    return [str(path), f"  {msg[1]}", f"没有保存文件，但 shop 没能删除 {temp}。请删除它。"]


def parent(folder: str) -> Msg:
    """Gives ``PARENT_NOT_A_FOLDER`` for a folder written as the problem writes it."""
    return (
        f'The file cannot be written: "{folder}" is not a folder.',
        f"无法写入文件：“{folder}”不是文件夹。",
    )
