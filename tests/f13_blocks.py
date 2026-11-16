"""The blocks A to H of the F13 test plan: the outputs of ``shop`` that no prototype shows.

Each block is a function that gives its lines, with the full path of the list file in place of
``P`` in the last line, or the bytes of a file. They are literals, and nothing here calls an
interface of F13 when the module is imported.
"""

from pathlib import Path

from f05_texts import lines_text

# The dates of the weeks of the cases, in English and in Chinese.
DATES: dict[str, tuple[str, str]] = {
    "2026-W01": ("29 December 2025 to 4 January 2026", "2025年12月29日至2026年1月4日"),
    "2026-W23": ("1 to 7 June 2026", "2026年6月1日至7日"),
    "2026-W47": ("16 to 22 November 2026", "2026年11月16日至22日"),
    "2026-W48": ("23 to 29 November 2026", "2026年11月23日至29日"),
    "2026-W49": ("30 November to 6 December 2026", "2026年11月30日至12月6日"),
    "2026-W53": ("28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日"),
    "2027-W01": ("4 to 10 January 2027", "2027年1月4日至10日"),
}

# ---------------------------------------------------------------- block A


def block_a(path: Path | str) -> list[str]:
    """Gives block A: 2026-W47 in English with the settings of all meals and 3 servings."""
    return [
        "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes",
        "",
        "Vegetables and fruit",
        "  Tomato          900 g",
        "  Choy sum        1.75 kg",
        "  Scallion        7 stalks",
        "  Ginger          6 slices",
        "  Garlic          14 cloves",
        "Meat and seafood",
        "  Minced pork     150 g",
        "  Chicken wings   1 kg",
        "Eggs, dairy, and tofu",
        "  Egg             8 pieces",
        "  Tofu            2 blocks",
        "Rice, flour, and oil",
        "  Rice            800 g",
        "  Noodles         300 g",
        "Seasonings",
        "  Doubanjiang     23 ml",
        "  White pepper    to taste",
        "Other",
        "  Cola            2 cans",
        "",
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, "
        "Sichuan pepper",
        "",
        f"Saved {path}",
    ]


# ---------------------------------------------------------------- block B


def block_b(path: Path | str) -> list[str]:
    """Gives the English output of block B: week B in a new example."""
    return [
        "Shopping list for 2026-W48, 23 to 29 November 2026: 4 meals, 5 dishes",
        "",
        "Vegetables and fruit",
        "  Choy sum      2.5 kg",
        "  Scallion      3 stalks",
        "  Ginger        3 slices",
        "  Garlic        17 cloves",
        "Meat and seafood",
        "  Pork belly    500 g",
        "  Minced pork   100 g",
        "Eggs, dairy, and tofu",
        "  Tofu          1 block",
        "Rice, flour, and oil",
        "  Rice          320 g",
        "Seasonings",
        "  Rock sugar    30 g",
        "  Doubanjiang   15 ml",
        "",
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Soy sauce, "
        "Sichuan pepper",
        "",
        f"Saved {path}",
    ]


def block_b_zh(path: Path | str) -> list[str]:
    """Gives the Chinese output of block B."""
    return [
        "2026-W48 购物清单，2026年11月23日至29日：4 餐，5 道菜",
        "",
        "蔬菜水果",
        "  菜心         2.5 kg",
        "  葱           3 根",
        "  姜           3 片",
        "  大蒜         17 瓣",
        "肉类水产",
        "  五花肉       500 g",
        "  猪肉末       100 g",
        "蛋奶豆制品",
        "  豆腐         1 块",
        "米面粮油",
        "  大米         320 g",
        "调味品",
        "  冰糖         30 g",
        "  郫县豆瓣酱   15 ml",
        "",
        "常备，不用买：食用油、盐、生抽、花椒",
        "",
        f"已保存 {path}",
    ]


# ---------------------------------------------------------------- block C


def block_c(path: Path | str) -> list[str]:
    """Gives the English output of block C: v0.1-S16 in the S16 folder."""
    return [
        "Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish",
        "",
        "Vegetables and fruit",
        "  Tomato     450 g",
        "  Scallion   2 stalks",
        "Eggs, dairy, and tofu",
        "  Egg        5 pieces",
        "",
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar",
        "",
        f"Saved {path}",
    ]


def block_c_zh(path: Path | str) -> list[str]:
    """Gives the Chinese output of block C."""
    return [
        "2026-W48 购物清单，2026年11月23日至29日：1 餐，1 道菜",
        "",
        "蔬菜水果",
        "  番茄   450 g",
        "  葱     2 根",
        "蛋奶豆制品",
        "  鸡蛋   5 个",
        "",
        "常备，不用买：食用油、盐、糖",
        "",
        f"已保存 {path}",
    ]


# ---------------------------------------------------------------- block D


def block_d(path: Path | str) -> list[str]:
    """Gives block D: the chicken break, whatever the line break S is."""
    return [
        "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes",
        "",
        "Vegetables and fruit",
        "  Tomato         600 g",
        "  Choy sum       1.5 kg",
        "  Scallion       5 stalks",
        "  Ginger         6 slices",
        "  Garlic         11 cloves",
        "Meat and seafood",
        "  Minced pork    100 g",
        "  Chicken        1 kg",
        "  wings",
        "Eggs, dairy, and tofu",
        "  Egg            5 pieces",
        "  Tofu           1 block",
        "Rice, flour, and oil",
        "  Rice           640 g",
        "  Noodles        200 g",
        "Seasonings",
        "  Doubanjiang    15 ml",
        "  White pepper   to taste",
        "Other",
        "  Cola           2 cans",
        "",
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, "
        "Sichuan pepper",
        "",
        f"Saved {path}",
    ]


# ---------------------------------------------------------------- blocks E and F


def _file(lines: list[str]) -> bytes:
    """Gives the lines as UTF-8 bytes, each ended by LF, the last one included."""
    return lines_text(*lines).encode("utf-8")


def block_e(path: Path | str) -> list[str]:
    """Gives the English output of block E: the water week."""
    return [
        "Shopping list for 2026-W50, 7 to 13 December 2026: 1 meal, 1 dish",
        "",
        "There is nothing to buy.",
        "",
        f"Saved {path}",
    ]


def block_e_zh(path: Path | str) -> list[str]:
    """Gives the Chinese output of block E."""
    return [
        "2026-W50 购物清单，2026年12月7日至13日：1 餐，1 道菜",
        "",
        "没有要买的东西。",
        "",
        f"已保存 {path}",
    ]


FILE_E = _file(
    [
        "# Shopping list for 2026-W50",
        "",
        "7 to 13 December 2026: 1 meal, 1 dish.",
        "",
        "There is nothing to buy.",
    ]
)
FILE_E_ZH = _file(
    [
        "# 2026-W50 购物清单",
        "",
        "2026年12月7日至13日：1 餐，1 道菜。",
        "",
        "没有要买的东西。",
    ]
)


def block_f(path: Path | str) -> list[str]:
    """Gives the English output of block F: the egg week."""
    return [
        "Shopping list for 2026-W51, 14 to 20 December 2026: 1 meal, 2 dishes",
        "",
        "There is nothing to buy.",
        "",
        "Not on the list, because they are in the pantry: Egg, Salt",
        "",
        f"Saved {path}",
    ]


def block_f_zh(path: Path | str) -> list[str]:
    """Gives the Chinese output of block F."""
    return [
        "2026-W51 购物清单，2026年12月14日至20日：1 餐，2 道菜",
        "",
        "没有要买的东西。",
        "",
        "常备，不用买：鸡蛋、盐",
        "",
        f"已保存 {path}",
    ]


FILE_F = _file(
    [
        "# Shopping list for 2026-W51",
        "",
        "14 to 20 December 2026: 1 meal, 2 dishes.",
        "",
        "There is nothing to buy.",
        "",
        "Not on the list, because they are in the pantry: Egg, Salt",
    ]
)
FILE_F_ZH = _file(
    [
        "# 2026-W51 购物清单",
        "",
        "2026年12月14日至20日：1 餐，2 道菜。",
        "",
        "没有要买的东西。",
        "",
        "常备，不用买：鸡蛋、盐",
    ]
)

# ---------------------------------------------------------------- block G


def block_g(path: Path | str) -> list[str]:
    """Gives the English output of block G: v0.1-S18."""
    return [
        "Shopping list for 2026-W48, 23 to 29 November 2026: 5 meals, 5 dishes",
        "",
        "Vegetables and fruit",
        "  Tomato         900 g",
        "  Scallion       5 stalks + 1 bunch",
        "  Ginger         3 slices",
        "Meat and seafood",
        "  Pork belly     500 g",
        "Eggs, dairy, and tofu",
        "  Egg            8 pieces",
        "Rice, flour, and oil",
        "  Noodles        400 g",
        "Seasonings",
        "  Soy sauce      30 ml + 10 g",
        "  Rock sugar     30 g",
        "  White pepper   to taste",
        "",
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar",
        "",
        f"Saved {path}",
    ]


def block_g_zh(path: Path | str) -> list[str]:
    """Gives the Chinese output of block G."""
    return [
        "2026-W48 购物清单，2026年11月23日至29日：5 餐，5 道菜",
        "",
        "蔬菜水果",
        "  番茄       900 g",
        "  葱         5 根 + 1 把",
        "  姜         3 片",
        "肉类水产",
        "  五花肉     500 g",
        "蛋奶豆制品",
        "  鸡蛋       8 个",
        "米面粮油",
        "  面条       400 g",
        "调味品",
        "  生抽       30 ml + 10 g",
        "  冰糖       30 g",
        "  白胡椒粉   适量",
        "",
        "常备，不用买：食用油、盐、糖",
        "",
        f"已保存 {path}",
    ]


# ---------------------------------------------------------------- block H


def block_h(week: str, dates: str, path: Path | str) -> list[str]:
    """Gives ``H(W, D)`` of block H in English: the rice week ``week`` with its English dates."""
    return [
        f"Shopping list for {week}, {dates}: 1 meal, 1 dish",
        "",
        "Rice, flour, and oil",
        "  Rice   160 g",
        "",
        f"Saved {path}",
    ]


def block_h_zh(week: str, dates: str, path: Path | str) -> list[str]:
    """Gives ``H_ZH(W, D)`` of block H: the rice week ``week`` with its Chinese dates."""
    return [
        f"{week} 购物清单，{dates}：1 餐，1 道菜",
        "",
        "米面粮油",
        "  大米   160 g",
        "",
        f"已保存 {path}",
    ]


def file_h(week: str, dates: str) -> bytes:
    """Gives ``FILE_H(W, D)``: the file of the English run of the rice week."""
    lines = [
        f"# Shopping list for {week}",
        "",
        f"{dates}: 1 meal, 1 dish.",
        "",
        "## Rice, flour, and oil",
        "",
        "- [ ] Rice 160 g",
    ]
    return _file(lines)


def file_h_zh(week: str, dates: str) -> bytes:
    """Gives ``FILE_H_ZH(W, D)``: the file of the Chinese run of the rice week."""
    lines = [
        f"# {week} 购物清单",
        "",
        f"{dates}：1 餐，1 道菜。",
        "",
        "## 米面粮油",
        "",
        "- [ ] 大米 160 g",
    ]
    return _file(lines)
