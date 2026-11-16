"""Expected texts of the start and check flow (F05, F07, F08), from the prototypes.

Every text is a tuple of lines written out as literals, so no test reads a prototype file.
`<data>` stands for the data folder (the folder recipe-menu in the home folder by default).
The helper module ``support`` fills it in.

At import the module holds only these tuples of text lines, and it imports nothing and calls
nothing.
"""

# F05 "Help in English", output 1.
HELP_EN: tuple[str, ...] = (
    "Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]",
    "",
    "Keep your recipes, plan a week's menu, and make its shopping list.",
    "",
    "Commands:",
    "  init               Create the data folder with example data.",
    "  check              Check every data file for mistakes.",
    "  list               List the recipes.",
    "  show ID            Show one recipe.",
    "  search WORD...     Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]    Create an empty week menu.",
    "  menu show [WEEK]   Show a week menu.",
    "  shop [WEEK]        Make the shopping list of a week menu.",
    "",
    "Options:",
    "  --lang en|zh       The language of the output. Default: the settings, else English.",
    "  --data FOLDER      The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version          Show the version.",
    "  --help             Show this help.",
    "",
    'WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.',
)

# F05 "Help in Chinese", output 1.
HELP_ZH: tuple[str, ...] = (
    "用法\uff1arecipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]",
    "",
    "保存菜谱\uff0c排一周的菜单\uff0c并生成它的购物清单\u3002",
    "",
    "命令\uff1a",
    "  init               创建数据文件夹和示例数据\u3002",
    "  check              检查每个数据文件有没有错误\u3002",
    "  list               列出菜谱\u3002",
    "  show ID            查看一个菜谱\u3002",
    "  search 词...       按名称\u3001食材或标签找菜谱\u3002",
    "  menu new [周]      创建一个空的周菜单\u3002",
    "  menu show [周]     查看一个周菜单\u3002",
    "  shop [周]          生成一个周菜单的购物清单\u3002",
    "",
    "选项\uff1a",
    "  --lang en|zh       输出语言\u3002默认\uff1a设置里的语言\uff0c否则英文\u3002",
    "  --data 文件夹      数据文件夹\u3002默认\uff1aRECIPE_MENU_DATA\uff0c否则 ~/recipe-menu\u3002",
    "  --version          显示版本\u3002",
    "  --help             显示这份帮助\u3002",
    "",
    "\u201c周\u201d是 ISO 周\uff0c比如 2026-W47\uff0c也可以是 this\uff08本周"
    "\uff09或 next\uff08下周\uff09\u3002默认\uff1a本周\u3002",
)

# F05 "Mistakes on the command line", output 1.
BAD_LANG: tuple[str, ...] = (
    '--lang must be en or zh, not "fr".',
    'Run "recipe-menu --help" to see the options.',
)

# F05 "Mistakes on the command line", output 2.
BAD_COMMAND: tuple[str, ...] = (
    'Unknown command "cook".',
    'Run "recipe-menu --help" to see the commands.',
)

# F05 "No data folder yet", output 1.
NO_FOLDER_EN: tuple[str, ...] = (
    "There is no data folder at <data>.",
    'Run "recipe-menu init" to create it, or name another folder with --data.',
)

# F05 "No data folder yet", output 2.
NO_FOLDER_ZH: tuple[str, ...] = (
    "<data> 没有数据文件夹\u3002",
    "运行\u201crecipe-menu init\u201d创建它\uff0c或用 --data 指定别的文件夹\u3002",
)

# F05 "A broken settings file", output 1.
BROKEN_SETTINGS: tuple[str, ...] = (
    "settings.toml, meals",
    '  Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
    'Run "recipe-menu check" to see every problem.',
)

# F05 "The language from the settings", output 1.
SETTINGS_ZH_TAG: tuple[str, ...] = (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手\u3001素",
    "",
    "共 1 个菜谱带有标签\u201c素\u201d\u3002",
)

# F05 "The language from the settings", output 2.
SETTINGS_EN_TAG: tuple[str, ...] = (
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "",
    '1 recipe has the tag "vegetarian".',
)

# F07 "Errors and a warning, in English", output 1.
CHECK_ERRORS_EN: tuple[str, ...] = (
    "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
    "",
    "2 errors:",
    "  recipes\\mapo-tofu.toml, ingredient 3",
    '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    "  menus\\2026-W47.toml, Monday dinner",
    '    Unknown recipe "tomato-eggs".',
    "",
    "1 warning:",
    "  recipes\\red-braised-pork.toml, steps",
    "    No English steps. Commands show the Chinese steps instead.",
    "",
    'Fix the errors and run "recipe-menu check" again.',
)

# F07 "The same check in Chinese", output 1.
CHECK_ERRORS_ZH: tuple[str, ...] = (
    "已检查设置\u3001目录\u3001常备清单\u30017 个菜谱和 1 个周菜单\u3002",
    "",
    "2 个错误\uff1a",
    "  recipes\\mapo-tofu.toml\uff0c食材 3",
    "    未知食材\u201c豆瓣酱\u201d\u3002请把它加入目录\uff0c或改用目录里的名称\u3002",
    "  menus\\2026-W47.toml\uff0c周一晚餐",
    "    未知菜谱\u201ctomato-eggs\u201d\u3002",
    "",
    "1 个警告\uff1a",
    "  recipes\\red-braised-pork.toml\uff0c步骤",
    "    没有英文步骤\u3002命令会改为显示中文步骤\u3002",
    "",
    "改正错误后\uff0c再运行\u201crecipe-menu check\u201d\u3002",
)

# F07 "A syntax mistake", output 1.
CHECK_SYNTAX: tuple[str, ...] = (
    "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
    "",
    "1 error:",
    "  pantry.toml, line 2",
    '    The file cannot be read: a closing "]" is missing.',
    "",
    "1 warning:",
    "  recipes\\red-braised-pork.toml, steps",
    "    No English steps. Commands show the Chinese steps instead.",
    "",
    'Fix the errors and run "recipe-menu check" again.',
)

# F07 "After the fixes", output 1.
CHECK_FIXED: tuple[str, ...] = (
    "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
    "",
    "No errors.",
    "",
    "1 warning:",
    "  recipes\\red-braised-pork.toml, steps",
    "    No English steps. Commands show the Chinese steps instead.",
)

# F08 "In English", output 1.
INIT_EN: tuple[str, ...] = (
    "Created the data folder <data>:",
    "  settings.toml              English, lunch and dinner, 2 servings per dish",
    "  catalog.toml               6 categories, 22 ingredients, 5 tags",
    "  pantry.toml                5 ingredients",
    "  recipes\\tomato-egg.toml    an example recipe in both languages",
    "  menus\\                     empty",
    "  shopping\\                  empty",
    "",
    'Next: add your recipes to recipes\\, then run "recipe-menu check".',
)

# F08 "In English", output 2.
CHECK_INIT: tuple[str, ...] = (
    "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
    "",
    "No errors. No warnings.",
)

# F08 "In Chinese", output 1.
INIT_ZH: tuple[str, ...] = (
    "已创建数据文件夹 <data>\uff1a",
    "  settings.toml              中文\uff0c午餐和晚餐\uff0c每道菜 2 份",
    "  catalog.toml               6 个分类\uff0c22 种食材\uff0c5 个标签",
    "  pantry.toml                5 种食材",
    "  recipes\\tomato-egg.toml    一个中英双语的示例菜谱",
    "  menus\\                     空",
    "  shopping\\                  空",
    "",
    "下一步\uff1a把你的菜谱加进 recipes\\\uff0c然后运行\u201crecipe-menu check\u201d\u3002",
)

# F08 "The folder already holds files", output 1.
INIT_REFUSED: tuple[str, ...] = ("<data> already holds files. init changed nothing.",)
