# Prototype: shopping list

Features: F12 builds the list, and F13 prints and saves it. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`, including `menus\2026-W47.toml`.

## How the example adds up

| Line | Where it comes from |
| --- | --- |
| 番茄 600 g | `tomato-egg` 300 g + `tomato-egg-noodles` 300 g |
| 菜心 1.5 kg | `choy-sum` 1 斤 = 500 g on Monday, + 500 g × 2 on Sunday (4 servings of a 2-serving recipe) |
| 葱 5 根 | `tomato-egg` 1 + `mapo-tofu` 1 + `tomato-egg-noodles` 1 + `cola-wings` 1 × 2 |
| 姜 6 片 | `cola-wings` 3 × 2 |
| 大蒜 11 瓣 | `choy-sum` 3 + 3 × 2, + `mapo-tofu` 2 |
| 猪肉末 100 g | `mapo-tofu` |
| 鸡翅中 1 kg | `cola-wings` 500 g × 2 |
| 鸡蛋 5 个 | `tomato-egg` 3 + `tomato-egg-noodles` 2 |
| 豆腐 1 块 | `mapo-tofu` |
| 大米 640 g | `rice` 160 g on Monday and Tuesday, + 160 g × 2 on Sunday |
| 面条 200 g | `tomato-egg-noodles` |
| 郫县豆瓣酱 15 ml | `mapo-tofu` 1 tbsp |
| 白胡椒粉 适量 | `tomato-egg-noodles`, with no quantity |
| 可乐 2 罐 | `cola-wings` 1 × 2 |
| Left out | 食用油, 盐, 糖, 生抽, and 花椒 are in the pantry. |

## In English

```text
PS> recipe-menu shop next
Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes

Vegetables and fruit
  Tomato          600 g
  Choy sum        1.5 kg
  Scallion        5 stalks
  Ginger          6 slices
  Garlic          11 cloves
Meat and seafood
  Minced pork     100 g
  Chicken wings   1 kg
Eggs, dairy, and tofu
  Egg             5 pieces
  Tofu            1 block
Rice, flour, and oil
  Rice            640 g
  Noodles         200 g
Seasonings
  Doubanjiang     15 ml
  White pepper    to taste
Other
  Cola            2 cans

Not on the list, because they are in the pantry: cooking oil, salt, sugar, soy sauce, Sichuan pepper

Saved C:\Users\Troy\recipe-menu\shopping\2026-W47.md
```

## In Chinese

```text
PS> recipe-menu shop next --lang zh
2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜

蔬菜水果
  番茄         600 g
  菜心         1.5 kg
  葱           5 根
  姜           6 片
  大蒜         11 瓣
肉类水产
  猪肉末       100 g
  鸡翅中       1 kg
蛋奶豆制品
  鸡蛋         5 个
  豆腐         1 块
米面粮油
  大米         640 g
  面条         200 g
调味品
  郫县豆瓣酱   15 ml
  白胡椒粉     适量
其他
  可乐         2 罐

常备，不用买：食用油、盐、糖、生抽、花椒

已保存 C:\Users\Troy\recipe-menu\shopping\2026-W47.md
```

## The saved file

`shopping\2026-W47.md` after the Chinese run. A run in English writes the same list in English. Each run replaces the file of that week.

~~~markdown
# 2026-W47 购物清单

2026年11月16日至22日：4 餐，9 道菜。

## 蔬菜水果

- [ ] 番茄 600 g
- [ ] 菜心 1.5 kg
- [ ] 葱 5 根
- [ ] 姜 6 片
- [ ] 大蒜 11 瓣

## 肉类水产

- [ ] 猪肉末 100 g
- [ ] 鸡翅中 1 kg

## 蛋奶豆制品

- [ ] 鸡蛋 5 个
- [ ] 豆腐 1 块

## 米面粮油

- [ ] 大米 640 g
- [ ] 面条 200 g

## 调味品

- [ ] 郫县豆瓣酱 15 ml
- [ ] 白胡椒粉 适量

## 其他

- [ ] 可乐 2 罐

常备，不用买：食用油、盐、糖、生抽、花椒
~~~

## Quantities that cannot be added

When one ingredient comes in two kinds of quantity, the line shows both. In another week, the dishes use 葱 5 根 in total, and one more recipe uses 葱 1 把. 生抽 is not in the pantry that week: one recipe uses 2 tbsp of it, and another uses 10 g.

```text
  Scallion        5 stalks + 1 bunch
  Soy sauce       30 ml + 10 g
```

## No menu, or an empty menu

```text
PS> recipe-menu shop 2026-W48
There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.
PS> $LASTEXITCODE
1

PS> recipe-menu shop this
The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.
PS> $LASTEXITCODE
0
```
