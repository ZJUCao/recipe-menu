# Prototype: start a data folder

Feature: F08. A PowerShell session in Windows Terminal, before any data folder exists. `init` writes the files of `example-data.md`: the settings, the catalog, the pantry, and `recipes\tomato-egg.toml`.

## In English

```text
PS> recipe-menu init
Created the data folder C:\Users\Troy\recipe-menu:
  settings.toml              English, lunch and dinner, 2 servings per dish
  catalog.toml               6 categories, 22 ingredients, 5 tags
  pantry.toml                5 ingredients
  recipes\tomato-egg.toml    an example recipe in both languages
  menus\                     empty
  shopping\                  empty

Next: add your recipes to recipes\, then run "recipe-menu check".

PS> recipe-menu check
Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.

No errors. No warnings.
```

## In Chinese

`init` writes the language it runs in into the settings, so this data folder speaks Chinese from now on.

```text
PS> recipe-menu init --lang zh
已创建数据文件夹 C:\Users\Troy\recipe-menu：
  settings.toml              中文，午餐和晚餐，每道菜 2 份
  catalog.toml               6 个分类，22 种食材，5 个标签
  pantry.toml                5 种食材
  recipes\tomato-egg.toml    一个中英双语的示例菜谱
  menus\                     空
  shopping\                  空

下一步：把你的菜谱加进 recipes\，然后运行“recipe-menu check”。
```

## The folder already holds files

```text
PS> recipe-menu init
C:\Users\Troy\recipe-menu already holds files. init changed nothing.
PS> $LASTEXITCODE
1

PS> recipe-menu init --data D:\OneDrive\recipe-menu
Created the data folder D:\OneDrive\recipe-menu:
...
```
