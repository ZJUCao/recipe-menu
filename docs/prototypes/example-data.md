# Prototype: example data

Every prototype uses this data folder, `C:\Users\Troy\recipe-menu`. The files are shown as TOML. The architecture picks the real format. `recipe-menu init` (F08) writes the settings, the catalog, the pantry, and `recipes\tomato-egg.toml` exactly as shown here.

## settings.toml

```toml
# recipe-menu settings
language = "en"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
```

## catalog.toml

The shopping list shows the categories in this order, and the ingredients of a category in this order. A recipe may name an ingredient or a tag in either language. `unit` is the default unit for a quantity without a unit.

```toml
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
```

## pantry.toml

```toml
# Ingredients you always have at home. The shopping list leaves them out.
pantry = ["食用油", "盐", "糖", "生抽", "花椒"]
```

## recipes\tomato-egg.toml

```toml
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
```

## The other recipes

Each of these recipes makes 2 servings and has steps in both languages, except `red-braised-pork`, whose steps are in Chinese only.

| ID | Chinese name | English name | Tags | Ingredients |
| --- | --- | --- | --- | --- |
| `choy-sum` | 清炒菜心 | Stir-fried choy sum | 快手, 素 | 菜心 1 斤; 大蒜 3 瓣 (拍碎, crushed); 盐 适量; 食用油 1 tbsp |
| `rice` | 米饭 | Steamed rice | 主食 | 大米 160 g |
| `mapo-tofu` | 麻婆豆腐 | Mapo tofu | 辣, 家常 | 豆腐 1 块 (切丁, diced); 猪肉末 100 g; 郫县豆瓣酱 1 tbsp; 花椒 1 tsp; 大蒜 2 瓣; 葱 1 根; 生抽 1 tbsp; 食用油 2 tbsp |
| `cola-wings` | 可乐鸡翅 | Cola chicken wings | 家常 | 鸡翅中 500 g; 可乐 1 罐; 姜 3 片; 葱 1 根; 生抽 2 tbsp |
| `tomato-egg-noodles` | 番茄鸡蛋面 | Tomato and egg noodles | 快手, 主食 | 面条 200 g; 番茄 300 g; 鸡蛋 2; 葱 1 根; 盐 适量; 白胡椒粉 适量 |
| `red-braised-pork` | 红烧肉 | Red-braised pork belly | 家常 | 五花肉 1 斤 (切成 3 厘米见方的块, cut into 3 cm cubes); 冰糖 30 g; 生抽 2 tbsp; 姜 3 片; 葱 2 根 |

## menus\2026-W47.toml

The week runs from Monday 16 November to Sunday 22 November 2026. A dish is a recipe ID, or a recipe ID with its servings.

```toml
# 2026-W47: 16 to 22 November 2026
week = "2026-W47"

[monday]
lunch = []
dinner = ["tomato-egg", "choy-sum", "rice"]

[tuesday]
lunch = []
dinner = ["mapo-tofu", "rice"]

[wednesday]
lunch = []
dinner = []

[thursday]
lunch = []
dinner = []

[friday]
lunch = []
dinner = []

[saturday]
lunch = ["tomato-egg-noodles"]
dinner = []

[sunday]
lunch = []
dinner = [
  { recipe = "cola-wings", servings = 4 },
  { recipe = "choy-sum", servings = 4 },
  { recipe = "rice", servings = 4 },
]
```
