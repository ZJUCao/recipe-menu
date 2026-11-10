# Prototype: list and show recipes

Feature: F09. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`. In the Chinese tables, each Chinese character takes two columns, so the columns line up.

## List the recipes

```text
PS> recipe-menu list
ID                   Name                      Servings   Tags
choy-sum             Stir-fried choy sum       2          quick, vegetarian
cola-wings           Cola chicken wings        2          home-style
mapo-tofu            Mapo tofu                 2          spicy, home-style
red-braised-pork     Red-braised pork belly    2          home-style
rice                 Steamed rice              2          staple
tomato-egg           Tomato and egg stir-fry   2          quick, home-style
tomato-egg-noodles   Tomato and egg noodles    2          quick, staple

7 recipes.

PS> recipe-menu list --lang zh
ID                   名称         份数   标签
choy-sum             清炒菜心     2      快手、素
cola-wings           可乐鸡翅     2      家常
mapo-tofu            麻婆豆腐     2      辣、家常
red-braised-pork     红烧肉       2      家常
rice                 米饭         2      主食
tomato-egg           番茄炒蛋     2      快手、家常
tomato-egg-noodles   番茄鸡蛋面   2      快手、主食

共 7 个菜谱。
```

## List the recipes with one tag

`--tag` takes the tag's name in either language.

```text
PS> recipe-menu list --tag 快手
ID                   Name                      Servings   Tags
choy-sum             Stir-fried choy sum       2          quick, vegetarian
tomato-egg           Tomato and egg stir-fry   2          quick, home-style
tomato-egg-noodles   Tomato and egg noodles    2          quick, staple

3 recipes have the tag "quick".

PS> recipe-menu list --tag quick --lang zh
ID                   名称         份数   标签
choy-sum             清炒菜心     2      快手、素
tomato-egg           番茄炒蛋     2      快手、家常
tomato-egg-noodles   番茄鸡蛋面   2      快手、主食

共 3 个菜谱带有标签“快手”。

PS> recipe-menu list --tag breakfast
Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.
PS> $LASTEXITCODE
1
```

## Show one recipe

The heading gives the name in the chosen language, then the name in the other language.

```text
PS> recipe-menu show tomato-egg
Tomato and egg stir-fry  番茄炒蛋
Servings: 2   Tags: quick, home-style

Ingredients
  Tomato        300 g      cut into wedges
  Egg           3 pieces
  Scallion      1 stalk    chopped
  Salt          to taste
  Sugar         1 tsp
  Cooking oil   2 tbsp

Steps
  1. Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.
  2. Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.
  3. Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.
  4. Return the eggs, season with salt, and scatter the scallion on top.
```

## Show one recipe for 4 servings, in Chinese

`--servings` scales the quantities. The steps stay as written.

```text
PS> recipe-menu show tomato-egg --servings 4 --lang zh
番茄炒蛋  Tomato and egg stir-fry
份数：4（菜谱按 2 份写）   标签：快手、家常

食材
  番茄     600 g    切块
  鸡蛋     6 个
  葱       2 根     切葱花
  盐       适量
  糖       2 茶匙
  食用油   4 汤匙

步骤
  1. 番茄切块。鸡蛋加少许盐打散。
  2. 热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。
  3. 下剩下的油，炒番茄至软，加糖。
  4. 倒回鸡蛋，加盐调味，撒上葱花。
```

## A missing language

`red-braised-pork` has its steps in Chinese only. `show` says so and shows the Chinese steps. 斤 is "jin" in English.

```text
PS> recipe-menu show red-braised-pork
Red-braised pork belly  红烧肉
Servings: 2   Tags: home-style

Ingredients
  Pork belly   1 jin      cut into 3 cm cubes
  Rock sugar   30 g
  Soy sauce    2 tbsp
  Ginger       3 slices
  Scallion     2 stalks

Steps (no English steps, so these are the Chinese steps)
  1. 五花肉冷水下锅，焯水后捞出。
  2. 小火把冰糖炒成焦糖色，下五花肉翻炒上色。
  3. 加生抽、姜片和热水，没过肉，小火炖 1 小时。
  4. 大火收汁，撒上葱段。
```

## An unknown ID

```text
PS> recipe-menu show mapo
No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.
PS> $LASTEXITCODE
1
```
