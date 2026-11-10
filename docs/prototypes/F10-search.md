# Prototype: search recipes

Feature: F10. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`.

A recipe matches when every word appears in its name, in one of its ingredients' names, or in one of its tags' names, in either language. English matches ignore case. The last column says where the words matched.

## One word

```text
PS> recipe-menu search 番茄
ID                   Name                      Matched in
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

2 recipes match "番茄".

PS> recipe-menu search TOMATO
ID                   Name                      Matched in
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

2 recipes match "TOMATO".
```

## Two words, in Chinese

```text
PS> recipe-menu search 葱 quick --lang zh
ID                   名称         匹配于
tomato-egg           番茄炒蛋     食材、标签
tomato-egg-noodles   番茄鸡蛋面   食材、标签

2 个菜谱同时匹配“葱”和“quick”。
```

## No match

No match is not an error.

```text
PS> recipe-menu search lamb
No recipe matches "lamb".
PS> $LASTEXITCODE
0

PS> recipe-menu search 豆腐 quick --lang zh
没有菜谱同时匹配“豆腐”和“quick”。
```
