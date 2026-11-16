"""Expected texts of the plan and shop flows (F11, F13), from the prototypes.

Every text is a tuple of lines written out as literals, so no test reads a prototype file.
`<data>` stands for the data folder (the folder recipe-menu in the home folder by default)
and `<home>` for the home folder. `support.text` fills them in.
"""

# F11 "Create next week's menu", output 1.
MENU_NEW_EN: tuple[str, ...] = (
    "Created <data>\\menus\\2026-W47.toml for 16 to 22 November 2026:",
    "7 days with lunch and dinner, all empty.",
    'Add recipe IDs to the meals, then run "recipe-menu check".',
)

# F11 "Create next week's menu", output 2.
MENU_NEW_EXISTS_ZH: tuple[str, ...] = (
    "<data>\\menus\\2026-W47.toml 已存在\u3002没有做任何修改\u3002",
)

# F11 "Show the week after you fill it", output 1.
MENU_SHOW_EN: tuple[str, ...] = (
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    "Day          Lunch                       Dinner",
    "Mon 16 Nov   \u2014                           Tomato and egg stir-fry \u00d72",
    "                                         Stir-fried choy sum \u00d72",
    "                                         Steamed rice \u00d72",
    "Tue 17 Nov   \u2014                           Mapo tofu \u00d72",
    "                                         Steamed rice \u00d72",
    "Wed 18 Nov   \u2014                           \u2014",
    "Thu 19 Nov   \u2014                           \u2014",
    "Fri 20 Nov   \u2014                           \u2014",
    "Sat 21 Nov   Tomato and egg noodles \u00d72   \u2014",
    "Sun 22 Nov   \u2014                           Cola chicken wings \u00d74",
    "                                         Stir-fried choy sum \u00d74",
    "                                         Steamed rice \u00d74",
    "",
    "4 meals, 9 dishes. \u00d7n: servings.",
)

# F11 "Show the week after you fill it", output 2.
MENU_SHOW_ZH: tuple[str, ...] = (
    "2026-W47 菜单\uff0c2026年11月16日至22日",
    "",
    "日期            午餐            晚餐",
    "周一 11月16日   \u2014               番茄炒蛋 \u00d72",
    "                                清炒菜心 \u00d72",
    "                                米饭 \u00d72",
    "周二 11月17日   \u2014               麻婆豆腐 \u00d72",
    "                                米饭 \u00d72",
    "周三 11月18日   \u2014               \u2014",
    "周四 11月19日   \u2014               \u2014",
    "周五 11月20日   \u2014               \u2014",
    "周六 11月21日   番茄鸡蛋面 \u00d72   \u2014",
    "周日 11月22日   \u2014               可乐鸡翅 \u00d74",
    "                                清炒菜心 \u00d74",
    "                                米饭 \u00d74",
    "",
    "4 餐\uff0c9 道菜\u3002\u00d7n\uff1a份数\u3002",
)

# F11 "A week without a menu", output 1.
NO_MENU: tuple[str, ...] = (
    'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.',
)

# F11 "A week without a menu", output 2.
NOT_A_WEEK: tuple[str, ...] = (
    '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".',
)

# F11 "A menu with a mistake", output 1.
MENU_MISTAKE: tuple[str, ...] = (
    "menus\\2026-W47.toml, Monday dinner",
    '  Unknown recipe "tomato-eggs".',
    'Run "recipe-menu check" to see every problem.',
)

# F13 "In English", output 1.
SHOP_EN: tuple[str, ...] = (
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
    "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, "
    "Soy sauce, Sichuan pepper",
    "",
    "Saved <data>\\shopping\\2026-W47.md",
)

# F13 "In Chinese", output 1.
SHOP_ZH: tuple[str, ...] = (
    "2026-W47 购物清单\uff0c2026年11月16日至22日\uff1a4 餐\uff0c9 道菜",
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
    "常备\uff0c不用买\uff1a食用油\u3001盐\u3001糖\u3001生抽\u3001花椒",
    "",
    "已保存 <data>\\shopping\\2026-W47.md",
)

# F13 "No menu, or an empty menu", output 1.
SHOP_NO_MENU: tuple[str, ...] = (
    'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.',
)

# F13 "No menu, or an empty menu", output 2.
SHOP_EMPTY: tuple[str, ...] = (
    "The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.",
)

# F13 "The saved file", the whole file.
SHOP_FILE_ZH: tuple[str, ...] = (
    "# 2026-W47 购物清单",
    "",
    "2026年11月16日至22日\uff1a4 餐\uff0c9 道菜\u3002",
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
    "常备\uff0c不用买\uff1a食用油\u3001盐\u3001糖\u3001生抽\u3001花椒",
)

# F13 "Quantities that cannot be added", the two lines.
SHOP_MIXED: tuple[str, ...] = (
    "  Scallion        5 stalks + 1 bunch",
    "  Soy sauce       30 ml + 10 g",
)

# F11 "Create next week's menu", the file that it creates.
NEW_MENU_FILE: tuple[str, ...] = (
    "# 2026-W47: 16 to 22 November 2026",
    '# A dish is a recipe ID, such as "tomato-egg",',
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
    'week = "2026-W47"',
    "",
    "[monday]",
    "lunch = []",
    "dinner = []",
    "",
    "[tuesday]",
    "lunch = []",
    "dinner = []",
    "",
    "[wednesday]",
    "lunch = []",
    "dinner = []",
    "",
    "[thursday]",
    "lunch = []",
    "dinner = []",
    "",
    "[friday]",
    "lunch = []",
    "dinner = []",
    "",
    "[saturday]",
    "lunch = []",
    "dinner = []",
    "",
    "[sunday]",
    "lunch = []",
    "dinner = []",
)
