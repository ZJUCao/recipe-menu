"""Tests of F02 for the tables of the prototypes (F02-T57 to F02-T66).

The expected lines are copied from the prototypes in ``docs/prototypes``.
"""

from f02_support import EN, ZH
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import comma_list, format_table

HELP_EN_COMMAND_ROWS = [
    ("init", "Create the data folder with example data."),
    ("check", "Check every data file for mistakes."),
    ("list", "List the recipes."),
    ("show ID", "Show one recipe."),
    ("search WORD...", "Find recipes by name, ingredient, or tag."),
    ("menu new [WEEK]", "Create an empty week menu."),
    ("menu show [WEEK]", "Show a week menu."),
    ("shop [WEEK]", "Make the shopping list of a week menu."),
]

HELP_EN_OPTION_ROWS = [
    ("--lang en|zh", "The language of the output. Default: the settings, else English."),
    ("--data FOLDER", "The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu."),
    ("--version", "Show the version."),
    ("--help", "Show this help."),
]

HELP_EN_COMMAND_LINES = (
    "  init               Create the data folder with example data.",
    "  check              Check every data file for mistakes.",
    "  list               List the recipes.",
    "  show ID            Show one recipe.",
    "  search WORD...     Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]    Create an empty week menu.",
    "  menu show [WEEK]   Show a week menu.",
    "  shop [WEEK]        Make the shopping list of a week menu.",
)

HELP_EN_OPTION_LINES = (
    "  --lang en|zh       The language of the output. Default: the settings, else English.",
    "  --data FOLDER      The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version          Show the version.",
    "  --help             Show this help.",
)

HELP_ZH_COMMAND_ROWS = [
    ("init", "创建数据文件夹和示例数据。"),
    ("check", "检查每个数据文件有没有错误。"),
    ("list", "列出菜谱。"),
    ("show ID", "查看一个菜谱。"),
    ("search 词...", "按名称、食材或标签找菜谱。"),
    ("menu new [周]", "创建一个空的周菜单。"),
    ("menu show [周]", "查看一个周菜单。"),
    ("shop [周]", "生成一个周菜单的购物清单。"),
]

HELP_ZH_OPTION_ROWS = [
    ("--lang en|zh", "输出语言。默认：设置里的语言，否则英文。"),
    ("--data 文件夹", "数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。"),
    ("--version", "显示版本。"),
    ("--help", "显示这份帮助。"),
]

HELP_ZH_COMMAND_LINES = (
    "  init               创建数据文件夹和示例数据。",
    "  check              检查每个数据文件有没有错误。",
    "  list               列出菜谱。",
    "  show ID            查看一个菜谱。",
    "  search 词...       按名称、食材或标签找菜谱。",
    "  menu new [周]      创建一个空的周菜单。",
    "  menu show [周]     查看一个周菜单。",
    "  shop [周]          生成一个周菜单的购物清单。",
)

HELP_ZH_OPTION_LINES = (
    "  --lang en|zh       输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹      数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version          显示版本。",
    "  --help             显示这份帮助。",
)

INIT_EN_ROWS = [
    ("settings.toml", "English, lunch and dinner, 2 servings per dish"),
    ("catalog.toml", "6 categories, 22 ingredients, 5 tags"),
    ("pantry.toml", "5 ingredients"),
    ("recipes\\tomato-egg.toml", "an example recipe in both languages"),
    ("menus\\", "empty"),
    ("shopping\\", "empty"),
]

INIT_EN_LINES = (
    "  settings.toml              English, lunch and dinner, 2 servings per dish",
    "  catalog.toml               6 categories, 22 ingredients, 5 tags",
    "  pantry.toml                5 ingredients",
    "  recipes\\tomato-egg.toml    an example recipe in both languages",
    "  menus\\                     empty",
    "  shopping\\                  empty",
)

INIT_ZH_ROWS = [
    ("settings.toml", "中文，午餐和晚餐，每道菜 2 份"),
    ("catalog.toml", "6 个分类，22 种食材，5 个标签"),
    ("pantry.toml", "5 种食材"),
    ("recipes\\tomato-egg.toml", "一个中英双语的示例菜谱"),
    ("menus\\", "空"),
    ("shopping\\", "空"),
]

INIT_ZH_LINES = (
    "  settings.toml              中文，午餐和晚餐，每道菜 2 份",
    "  catalog.toml               6 个分类，22 种食材，5 个标签",
    "  pantry.toml                5 种食材",
    "  recipes\\tomato-egg.toml    一个中英双语的示例菜谱",
    "  menus\\                     空",
    "  shopping\\                  空",
)

LIST_EN_LINES = (
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "cola-wings           Cola chicken wings        2          home-style",
    "mapo-tofu            Mapo tofu                 2          spicy, home-style",
    "red-braised-pork     Red-braised pork belly    2          home-style",
    "rice                 Steamed rice              2          staple",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
)

LIST_ZH_LINES = (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣、家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
)

RECIPE_DATA = [
    (
        "choy-sum",
        BiText("Stir-fried choy sum", "清炒菜心"),
        [BiText("quick", "快手"), BiText("vegetarian", "素")],
    ),
    ("cola-wings", BiText("Cola chicken wings", "可乐鸡翅"), [BiText("home-style", "家常")]),
    (
        "mapo-tofu",
        BiText("Mapo tofu", "麻婆豆腐"),
        [BiText("spicy", "辣"), BiText("home-style", "家常")],
    ),
    (
        "red-braised-pork",
        BiText("Red-braised pork belly", "红烧肉"),
        [BiText("home-style", "家常")],
    ),
    ("rice", BiText("Steamed rice", "米饭"), [BiText("staple", "主食")]),
    (
        "tomato-egg",
        BiText("Tomato and egg stir-fry", "番茄炒蛋"),
        [BiText("quick", "快手"), BiText("home-style", "家常")],
    ),
    (
        "tomato-egg-noodles",
        BiText("Tomato and egg noodles", "番茄鸡蛋面"),
        [BiText("quick", "快手"), BiText("staple", "主食")],
    ),
]

TAG_EN_LINES = (
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
)

TAG_ZH_LINES = (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
)

TOMATO_EGG_ROWS = [
    ("Tomato", "300 g", "cut into wedges"),
    ("Egg", "3 pieces", ""),
    ("Scallion", "1 stalk", "chopped"),
    ("Salt", "to taste", ""),
    ("Sugar", "1 tsp", ""),
    ("Cooking oil", "2 tbsp", ""),
]

TOMATO_EGG_LINES = (
    "  Tomato        300 g      cut into wedges",
    "  Egg           3 pieces",
    "  Scallion      1 stalk    chopped",
    "  Salt          to taste",
    "  Sugar         1 tsp",
    "  Cooking oil   2 tbsp",
)

PORK_ROWS = [
    ("Pork belly", "1 jin", "cut into 3 cm cubes"),
    ("Rock sugar", "30 g", ""),
    ("Soy sauce", "2 tbsp", ""),
    ("Ginger", "3 slices", ""),
    ("Scallion", "2 stalks", ""),
]

PORK_LINES = (
    "  Pork belly   1 jin      cut into 3 cm cubes",
    "  Rock sugar   30 g",
    "  Soy sauce    2 tbsp",
    "  Ginger       3 slices",
    "  Scallion     2 stalks",
)

CHINESE_INGREDIENT_ROWS = [
    ("番茄", "600 g", "切块"),
    ("鸡蛋", "6 个", ""),
    ("葱", "2 根", "切葱花"),
    ("盐", "适量", ""),
    ("糖", "2 茶匙", ""),
    ("食用油", "4 汤匙", ""),
]

CHINESE_INGREDIENT_LINES = (
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  葱       2 根     切葱花",
    "  盐       适量",
    "  糖       2 茶匙",
    "  食用油   4 汤匙",
)

SEARCH_WORD_LINES = (
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
)

SEARCH_UPPER_LINES = (
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
)

SEARCH_ZH_LINES = (
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     食材、标签",
    "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
)

WEEK_EN_LINES = (
    "Day          Lunch                       Dinner",
    "Mon 16 Nov   —                           Tomato and egg stir-fry ×2",
    "                                         Stir-fried choy sum ×2",
    "                                         Steamed rice ×2",
    "Tue 17 Nov   —                           Mapo tofu ×2",
    "                                         Steamed rice ×2",
    "Wed 18 Nov   —                           —",
    "Thu 19 Nov   —                           —",
    "Fri 20 Nov   —                           —",
    "Sat 21 Nov   Tomato and egg noodles ×2   —",
    "Sun 22 Nov   —                           Cola chicken wings ×4",
    "                                         Stir-fried choy sum ×4",
    "                                         Steamed rice ×4",
)

WEEK_ZH_LINES = (
    "日期            午餐            晚餐",
    "周一 11月16日   —               番茄炒蛋 ×2",
    "                                清炒菜心 ×2",
    "                                米饭 ×2",
    "周二 11月17日   —               麻婆豆腐 ×2",
    "                                米饭 ×2",
    "周三 11月18日   —               —",
    "周四 11月19日   —               —",
    "周五 11月20日   —               —",
    "周六 11月21日   番茄鸡蛋面 ×2   —",
    "周日 11月22日   —               可乐鸡翅 ×4",
    "                                清炒菜心 ×4",
    "                                米饭 ×4",
)

SHOP_EN_ROWS = [
    ("Tomato", "600 g"),
    ("Choy sum", "1.5 kg"),
    ("Scallion", "5 stalks"),
    ("Ginger", "6 slices"),
    ("Garlic", "11 cloves"),
    ("Minced pork", "100 g"),
    ("Chicken wings", "1 kg"),
    ("Egg", "5 pieces"),
    ("Tofu", "1 block"),
    ("Rice", "640 g"),
    ("Noodles", "200 g"),
    ("Doubanjiang", "15 ml"),
    ("White pepper", "to taste"),
    ("Cola", "2 cans"),
]

SHOP_EN_LINES = (
    "  Tomato          600 g",
    "  Choy sum        1.5 kg",
    "  Scallion        5 stalks",
    "  Ginger          6 slices",
    "  Garlic          11 cloves",
    "  Minced pork     100 g",
    "  Chicken wings   1 kg",
    "  Egg             5 pieces",
    "  Tofu            1 block",
    "  Rice            640 g",
    "  Noodles         200 g",
    "  Doubanjiang     15 ml",
    "  White pepper    to taste",
    "  Cola            2 cans",
)

SHOP_ZH_ROWS = [
    ("番茄", "600 g"),
    ("菜心", "1.5 kg"),
    ("葱", "5 根"),
    ("姜", "6 片"),
    ("大蒜", "11 瓣"),
    ("猪肉末", "100 g"),
    ("鸡翅中", "1 kg"),
    ("鸡蛋", "5 个"),
    ("豆腐", "1 块"),
    ("大米", "640 g"),
    ("面条", "200 g"),
    ("郫县豆瓣酱", "15 ml"),
    ("白胡椒粉", "适量"),
    ("可乐", "2 罐"),
]

SHOP_ZH_LINES = (
    "  番茄         600 g",
    "  菜心         1.5 kg",
    "  葱           5 根",
    "  姜           6 片",
    "  大蒜         11 瓣",
    "  猪肉末       100 g",
    "  鸡翅中       1 kg",
    "  鸡蛋         5 个",
    "  豆腐         1 块",
    "  大米         640 g",
    "  面条         200 g",
    "  郫县豆瓣酱   15 ml",
    "  白胡椒粉     适量",
    "  可乐         2 罐",
)


def test_f02_t57_help_in_english() -> None:
    """F05 "Help in English": the commands and the options, both with the width of the commands."""
    commands = format_table(HELP_EN_COMMAND_ROWS, indent=2, min_widths=(16,))
    options = format_table(HELP_EN_OPTION_ROWS, indent=2, min_widths=(16,))
    assert commands == HELP_EN_COMMAND_LINES
    assert options == HELP_EN_OPTION_LINES


def test_f02_t58_help_in_chinese() -> None:
    """F05 "Help in Chinese": the commands and the options, with the widths of the English help."""
    commands = format_table(HELP_ZH_COMMAND_ROWS, indent=2, min_widths=(16,))
    options = format_table(HELP_ZH_OPTION_ROWS, indent=2, min_widths=(16,))
    assert commands == HELP_ZH_COMMAND_LINES
    assert options == HELP_ZH_OPTION_LINES


def test_f02_t59_list_of_files_with_a_gap_of_4() -> None:
    """F08 "In English" and "In Chinese": the list of files, with a gap of 4."""
    assert format_table(INIT_EN_ROWS, indent=2, gap=4) == INIT_EN_LINES
    assert format_table(INIT_ZH_ROWS, indent=2, gap=4) == INIT_ZH_LINES


def recipe_table(lang: Lang, only: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Lays out the recipe list as ``list`` prints it.

    Args:
        lang: The language of the table.
        only: The IDs to keep, or no IDs for every recipe.

    Returns:
        The lines of the table.
    """
    header = ("ID", "Name", "Servings", "Tags") if lang is EN else ("ID", "名称", "份数", "标签")
    rows = [header]
    for recipe_id, name, tags in RECIPE_DATA:
        if not only or recipe_id in only:
            rows.append((recipe_id, name.get(lang), "2", comma_list(tags).get(lang)))
    return format_table(rows)


def test_f02_t60_list_the_recipes() -> None:
    """F09 "List the recipes", in English and in Chinese."""
    assert recipe_table(EN) == LIST_EN_LINES
    assert recipe_table(ZH) == LIST_ZH_LINES


def test_f02_t61_list_the_recipes_with_one_tag() -> None:
    """F09 "List the recipes with one tag", in English and in Chinese."""
    only = ("choy-sum", "tomato-egg", "tomato-egg-noodles")
    assert recipe_table(EN, only) == TAG_EN_LINES
    assert recipe_table(ZH, only) == TAG_ZH_LINES


def test_f02_t62_ingredients_in_english() -> None:
    """F09 "Show one recipe" and "A missing language": ingredients with empty notes."""
    assert format_table(TOMATO_EGG_ROWS, indent=2) == TOMATO_EGG_LINES
    assert format_table(PORK_ROWS, indent=2) == PORK_LINES


def test_f02_t63_ingredients_in_chinese() -> None:
    """F09 "Show one recipe for 4 servings, in Chinese": ingredients in Chinese."""
    assert format_table(CHINESE_INGREDIENT_ROWS, indent=2) == CHINESE_INGREDIENT_LINES


def test_f02_t64_search_results() -> None:
    """F10 "One word" and "Two words, in Chinese"."""
    where_en = comma_list([BiText("name", "名称"), BiText("ingredient", "食材")]).get(EN)
    english = format_table(
        [
            ("ID", "Name", "Matched in"),
            ("tomato-egg", "Tomato and egg stir-fry", where_en),
            ("tomato-egg-noodles", "Tomato and egg noodles", where_en),
        ]
    )
    assert english == SEARCH_WORD_LINES
    assert english == SEARCH_UPPER_LINES
    where_zh = comma_list([BiText("ingredient", "食材"), BiText("tag", "标签")]).get(ZH)
    chinese = format_table(
        [
            ("ID", "名称", "匹配于"),
            ("tomato-egg", "番茄炒蛋", where_zh),
            ("tomato-egg-noodles", "番茄鸡蛋面", where_zh),
        ]
    )
    assert chinese == SEARCH_ZH_LINES


def test_f02_t65_week_menu_with_cells_of_several_lines() -> None:
    """F11 "Show the week after you fill it", in English and in Chinese."""
    nl = "\n"
    empty = "—"
    english = format_table(
        [
            ("Day", "Lunch", "Dinner"),
            (
                "Mon 16 Nov",
                empty,
                nl.join(
                    ["Tomato and egg stir-fry ×2", "Stir-fried choy sum ×2", "Steamed rice ×2"]
                ),
            ),
            ("Tue 17 Nov", empty, nl.join(["Mapo tofu ×2", "Steamed rice ×2"])),
            ("Wed 18 Nov", empty, empty),
            ("Thu 19 Nov", empty, empty),
            ("Fri 20 Nov", empty, empty),
            ("Sat 21 Nov", "Tomato and egg noodles ×2", empty),
            (
                "Sun 22 Nov",
                empty,
                nl.join(["Cola chicken wings ×4", "Stir-fried choy sum ×4", "Steamed rice ×4"]),
            ),
        ]
    )
    assert english == WEEK_EN_LINES
    chinese = format_table(
        [
            ("日期", "午餐", "晚餐"),
            ("周一 11月16日", empty, nl.join(["番茄炒蛋 ×2", "清炒菜心 ×2", "米饭 ×2"])),
            ("周二 11月17日", empty, nl.join(["麻婆豆腐 ×2", "米饭 ×2"])),
            ("周三 11月18日", empty, empty),
            ("周四 11月19日", empty, empty),
            ("周五 11月20日", empty, empty),
            ("周六 11月21日", "番茄鸡蛋面 ×2", empty),
            ("周日 11月22日", empty, nl.join(["可乐鸡翅 ×4", "清炒菜心 ×4", "米饭 ×4"])),
        ]
    )
    assert chinese == WEEK_ZH_LINES


def test_f02_t66_shopping_list_as_one_table() -> None:
    """F13 "In English" and "In Chinese": the 14 items as one table, with no headings."""
    assert format_table(SHOP_EN_ROWS, indent=2) == SHOP_EN_LINES
    assert format_table(SHOP_ZH_ROWS, indent=2) == SHOP_ZH_LINES
