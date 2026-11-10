# Prototype: create and show a week menu

Feature: F11. A PowerShell session in Windows Terminal on Tuesday 10 November 2026, so this week is 2026-W46 and next week is 2026-W47. The data folder holds the example data in `example-data.md`, except that `menus\` is empty at the start.

## Create next week's menu

```text
PS> recipe-menu menu new next
Created C:\Users\Troy\recipe-menu\menus\2026-W47.toml for 16 to 22 November 2026:
7 days with lunch and dinner, all empty.
Add recipe IDs to the meals, then run "recipe-menu check".

PS> recipe-menu menu new next --lang zh
C:\Users\Troy\recipe-menu\menus\2026-W47.toml 已存在。没有做任何修改。
PS> $LASTEXITCODE
1
```

The new file has every day and meal, empty, with a comment that shows how to write a dish:

```toml
# 2026-W47: 16 to 22 November 2026
# A dish is a recipe ID, such as "tomato-egg",
# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.
week = "2026-W47"

[monday]
lunch = []
dinner = []

[tuesday]
lunch = []
dinner = []

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
lunch = []
dinner = []

[sunday]
lunch = []
dinner = []
```

## Show the week after you fill it

Troy fills the file as `menus\2026-W47.toml` in `example-data.md` shows. ×n is the servings of a dish, and — is an empty meal.

```text
PS> recipe-menu menu show next
Menu for 2026-W47, 16 to 22 November 2026

Day          Lunch                       Dinner
Mon 16 Nov   —                           Tomato and egg stir-fry ×2
                                         Stir-fried choy sum ×2
                                         Steamed rice ×2
Tue 17 Nov   —                           Mapo tofu ×2
                                         Steamed rice ×2
Wed 18 Nov   —                           —
Thu 19 Nov   —                           —
Fri 20 Nov   —                           —
Sat 21 Nov   Tomato and egg noodles ×2   —
Sun 22 Nov   —                           Cola chicken wings ×4
                                         Stir-fried choy sum ×4
                                         Steamed rice ×4

4 meals, 9 dishes. ×n: servings.

PS> recipe-menu menu show 2026-W47 --lang zh
2026-W47 菜单，2026年11月16日至22日

日期            午餐            晚餐
周一 11月16日   —               番茄炒蛋 ×2
                                清炒菜心 ×2
                                米饭 ×2
周二 11月17日   —               麻婆豆腐 ×2
                                米饭 ×2
周三 11月18日   —               —
周四 11月19日   —               —
周五 11月20日   —               —
周六 11月21日   番茄鸡蛋面 ×2   —
周日 11月22日   —               可乐鸡翅 ×4
                                清炒菜心 ×4
                                米饭 ×4

4 餐，9 道菜。×n：份数。
```

## A week without a menu

```text
PS> recipe-menu menu show 2026-W48
There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.
PS> $LASTEXITCODE
1

PS> recipe-menu menu show 2026-W99
"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".
PS> $LASTEXITCODE
2
```

## A menu with a mistake

`menu show` reads the menu as `check` does, and stops at an error.

```text
PS> recipe-menu menu show next
menus\2026-W47.toml, Monday dinner
  Unknown recipe "tomato-eggs".
Run "recipe-menu check" to see every problem.
PS> $LASTEXITCODE
1
```
