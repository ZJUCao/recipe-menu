"""Expected texts of the find-a-recipe flow (F09, F10), from the prototypes.

Every text is a tuple of lines written out as literals, so no test reads a prototype file.
`<data>` stands for the data folder (the folder recipe-menu in the home folder by default)
and `<home>` for the home folder. `support.text` fills them in.
"""

# F09 "List the recipes", output 1.
LIST_EN: tuple[str, ...] = (
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
)

# F09 "List the recipes", output 2.
LIST_ZH: tuple[str, ...] = (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手\u3001素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣\u3001家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "tomato-egg           番茄炒蛋     2      快手\u3001家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手\u3001主食",
    "",
    "共 7 个菜谱\u3002",
)

# F09 "List the recipes with one tag", output 1.
TAG_QUICK_EN: tuple[str, ...] = (
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
    "",
    '3 recipes have the tag "quick".',
)

# F09 "List the recipes with one tag", output 2.
TAG_QUICK_ZH: tuple[str, ...] = (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手\u3001素",
    "tomato-egg           番茄炒蛋     2      快手\u3001家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手\u3001主食",
    "",
    "共 3 个菜谱带有标签\u201c快手\u201d\u3002",
)

# F09 "List the recipes with one tag", output 3.
TAG_BREAKFAST: tuple[str, ...] = (
    'Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.',
)

# F09 "Show one recipe", output 1.
SHOW_EN: tuple[str, ...] = (
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
)

# F09 "Show one recipe for 4 servings, in Chinese", output 1.
SHOW_ZH_4: tuple[str, ...] = (
    "番茄炒蛋  Tomato and egg stir-fry",
    "份数\uff1a4\uff08菜谱按 2 份写\uff09   标签\uff1a快手\u3001家常",
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
    "  1. 番茄切块\u3002鸡蛋加少许盐打散\u3002",
    "  2. 热锅下 1 汤匙油\uff0c炒鸡蛋至刚凝固\uff0c盛出\u3002",
    "  3. 下剩下的油\uff0c炒番茄至软\uff0c加糖\u3002",
    "  4. 倒回鸡蛋\uff0c加盐调味\uff0c撒上葱花\u3002",
)

# F09 "A missing language", output 1.
SHOW_MISSING: tuple[str, ...] = (
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
    "  1. 五花肉冷水下锅\uff0c焯水后捞出\u3002",
    "  2. 小火把冰糖炒成焦糖色\uff0c下五花肉翻炒上色\u3002",
    "  3. 加生抽\u3001姜片和热水\uff0c没过肉\uff0c小火炖 1 小时\u3002",
    "  4. 大火收汁\uff0c撒上葱段\u3002",
)

# F09 "An unknown ID", output 1.
SHOW_UNKNOWN: tuple[str, ...] = (
    'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.',
)

# F10 "One word", output 1.
SEARCH_ONE_ZH_WORD: tuple[str, ...] = (
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
    "",
    '2 recipes match "番茄".',
)

# F10 "One word", output 2.
SEARCH_ONE_EN_WORD: tuple[str, ...] = (
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
    "",
    '2 recipes match "TOMATO".',
)

# F10 "Two words, in Chinese", output 1.
SEARCH_TWO_ZH: tuple[str, ...] = (
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     食材\u3001标签",
    "tomato-egg-noodles   番茄鸡蛋面   食材\u3001标签",
    "",
    "2 个菜谱同时匹配\u201c葱\u201d和\u201cquick\u201d\u3002",
)

# F10 "No match", output 1.
SEARCH_LAMB: tuple[str, ...] = ('No recipe matches "lamb".',)

# F10 "No match", output 2.
SEARCH_TOFU_ZH: tuple[str, ...] = ("没有菜谱同时匹配\u201c豆腐\u201d和\u201cquick\u201d\u3002",)
