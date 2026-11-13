"""The texts of the example files that ``init`` writes, and the counts that it reports.

Each text is the text of one code block of ``docs/prototypes/example-data.md``. A test keeps
each one equal to the same file of ``tests/data/example/``, byte for byte.
"""

from typing import Final

# The text of ``settings.toml``, with ``en`` in its ``language`` line.
SETTINGS_TEXT: Final[str] = """\
# recipe-menu settings
language = "en"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
"""

# The text of ``catalog.toml``.
CATALOG_TEXT: Final[str] = """\
categories = [
  { key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" },
  { key = "meat", zh = "肉类水产", en = "Meat and seafood" },
  { key = "eggs", zh = "蛋奶豆制品", en = "Eggs, dairy, and tofu" },
  { key = "staples", zh = "米面粮油", en = "Rice, flour, and oil" },
  { key = "seasonings", zh = "调味品", en = "Seasonings" },
  { key = "other", zh = "其他", en = "Other" },
]

ingredients = [
  { zh = "番茄", en = "Tomato", category = "produce" },
  { zh = "菜心", en = "Choy sum", category = "produce" },
  { zh = "西兰花", en = "Broccoli", category = "produce" },
  { zh = "葱", en = "Scallion", category = "produce", unit = "根" },
  { zh = "姜", en = "Ginger", category = "produce", unit = "片" },
  { zh = "大蒜", en = "Garlic", category = "produce", unit = "瓣" },
  { zh = "五花肉", en = "Pork belly", category = "meat" },
  { zh = "猪肉末", en = "Minced pork", category = "meat" },
  { zh = "鸡翅中", en = "Chicken wings", category = "meat" },
  { zh = "鸡蛋", en = "Egg", category = "eggs", unit = "个" },
  { zh = "豆腐", en = "Tofu", category = "eggs", unit = "块" },
  { zh = "大米", en = "Rice", category = "staples" },
  { zh = "面条", en = "Noodles", category = "staples" },
  { zh = "食用油", en = "Cooking oil", category = "staples" },
  { zh = "盐", en = "Salt", category = "seasonings" },
  { zh = "糖", en = "Sugar", category = "seasonings" },
  { zh = "生抽", en = "Soy sauce", category = "seasonings" },
  { zh = "冰糖", en = "Rock sugar", category = "seasonings" },
  { zh = "郫县豆瓣酱", en = "Doubanjiang", category = "seasonings" },
  { zh = "花椒", en = "Sichuan pepper", category = "seasonings" },
  { zh = "白胡椒粉", en = "White pepper", category = "seasonings" },
  { zh = "可乐", en = "Cola", category = "other", unit = "罐" },
]

tags = [
  { zh = "快手", en = "quick" },
  { zh = "家常", en = "home-style" },
  { zh = "素", en = "vegetarian" },
  { zh = "辣", en = "spicy" },
  { zh = "主食", en = "staple" },
]
"""

# The text of ``pantry.toml``.
PANTRY_TEXT: Final[str] = """\
# Ingredients you always have at home. The shopping list leaves them out.
pantry = ["食用油", "盐", "糖", "生抽", "花椒"]
"""

# The text of ``recipes/tomato-egg.toml``.
RECIPE_TEXT: Final[str] = """\
name = { zh = "番茄炒蛋", en = "Tomato and egg stir-fry" }
servings = 2
tags = ["快手", "家常"]

ingredients = [
  { item = "番茄", amount = "300 g", note = { zh = "切块", en = "cut into wedges" } },
  { item = "鸡蛋", amount = "3" },
  { item = "葱", amount = "1 根", note = { zh = "切葱花", en = "chopped" } },
  { item = "盐", amount = "适量" },
  { item = "糖", amount = "1 tsp" },
  { item = "食用油", amount = "2 tbsp" },
]

[steps]
zh = [
  "番茄切块。鸡蛋加少许盐打散。",
  "热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。",
  "下剩下的油，炒番茄至软，加糖。",
  "倒回鸡蛋，加盐调味，撒上葱花。",
]
en = [
  "Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.",
  "Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.",
  "Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.",
  "Return the eggs, season with salt, and scatter the scallion on top.",
]
"""

# The counts of the catalog and the pantry above, which ``init`` reports.
CATEGORY_TOTAL: Final[int] = 6
INGREDIENT_TOTAL: Final[int] = 22
TAG_TOTAL: Final[int] = 5
PANTRY_TOTAL: Final[int] = 5
