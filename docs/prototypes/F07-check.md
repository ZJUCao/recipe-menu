# Prototype: check the data files

Feature: F07. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`, with two mistakes: ingredient 3 of `mapo-tofu` says 豆瓣酱 in place of the catalog name 郫县豆瓣酱, and Monday dinner of `2026-W47` says `tomato-eggs`.

## Errors and a warning, in English

```text
PS> recipe-menu check
Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.

2 errors:
  recipes\mapo-tofu.toml, ingredient 3
    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.
  menus\2026-W47.toml, Monday dinner
    Unknown recipe "tomato-eggs".

1 warning:
  recipes\red-braised-pork.toml, steps
    No English steps. Commands show the Chinese steps instead.

Fix the errors and run "recipe-menu check" again.
PS> $LASTEXITCODE
1
```

## The same check in Chinese

```text
PS> recipe-menu check --lang zh
已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。

2 个错误：
  recipes\mapo-tofu.toml，食材 3
    未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。
  menus\2026-W47.toml，周一晚餐
    未知菜谱“tomato-eggs”。

1 个警告：
  recipes\red-braised-pork.toml，步骤
    没有英文步骤。命令会改为显示中文步骤。

改正错误后，再运行“recipe-menu check”。
```

## A syntax mistake

A file that cannot be read gets its line number.

```text
PS> recipe-menu check
Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.

1 error:
  pantry.toml, line 2
    The file cannot be read: a closing "]" is missing.

1 warning:
  recipes\red-braised-pork.toml, steps
    No English steps. Commands show the Chinese steps instead.

Fix the errors and run "recipe-menu check" again.
PS> $LASTEXITCODE
1
```

## After the fixes

A warning alone does not fail the check.

```text
PS> recipe-menu check
Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.

No errors.

1 warning:
  recipes\red-braised-pork.toml, steps
    No English steps. Commands show the Chinese steps instead.
PS> $LASTEXITCODE
0
```

## Other problems that check reports

The messages follow the same shape: the file and the place on one line, then what is wrong and what to do.

| Place | Message |
| --- | --- |
| `catalog.toml, ingredient 12` | The English name "Rice" is also ingredient 4's name. Names must be unique. |
| `catalog.toml, ingredient 7` | Unknown category "meats". The categories are produce, meat, eggs, staples, seasonings, and other. |
| `pantry.toml, item 3` | Unknown ingredient "sesame oil". |
| `recipes\rice.toml, servings` | Servings must be a whole number of 1 or more, not 0. |
| `recipes\rice.toml, ingredient 1` | Unknown unit "cups" in "1 cups". |
| `recipes\rice.toml, tags` | Unknown tag "breakfast". Add it to the catalog's tags. |
| `menus\2026-W47.toml, week` | The file name says 2026-W47, but the file says 2026-W48. |
| `menus\2026-W47.toml, Friday supper` | Unknown meal "supper". The settings name lunch and dinner. |
| `menus\2026-W47.toml, Sunday dinner, dish 1` | Servings must be a whole number of 1 or more, not 0. |
