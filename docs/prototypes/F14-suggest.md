# Prototype: suggest a week menu

Feature: F14, in v0.2. A PowerShell session in Windows Terminal. This session assumes a data folder with 40 recipes, 16 of them with the tag 快手 (quick). The settings give each meal 1 dish.

## Fill an empty week

```text
PS> recipe-menu menu new 2026-W48
Created C:\Users\Troy\recipe-menu\menus\2026-W48.toml for 23 to 29 November 2026:
7 days with lunch and dinner, all empty.
Add recipe IDs to the meals, then run "recipe-menu check".

PS> recipe-menu menu suggest 2026-W48 --tag quick
Filled 14 empty meals of 2026-W48 with recipes that have the tag "quick".
No recipe appears twice in the week.
Run "recipe-menu menu show 2026-W48" to see the week.
To swap a dish, empty its meal in menus\2026-W48.toml, then run "recipe-menu menu suggest 2026-W48" again.
```

## Swap one dish

Troy empties Wednesday dinner in the file and runs `suggest` again. The other 13 meals stay as they are.

```text
PS> recipe-menu menu suggest 2026-W48 --lang zh
已为 2026-W48 填好 1 个空餐。保留了已经有菜的 13 餐。
运行“recipe-menu menu show 2026-W48”查看这一周。
```

## Not enough recipes

```text
PS> recipe-menu menu suggest 2026-W49 --tag spicy
Filled 3 of 14 empty meals of 2026-W49 with recipes that have the tag "spicy".
11 meals stay empty: no other recipe has the tag "spicy".
```
