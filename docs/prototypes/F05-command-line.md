# Prototype: help, language, and data folder

Feature: F05. A PowerShell session in Windows Terminal. The data folder holds the example data in `example-data.md`.

## Help in English

The help lists the commands of the accepted features: those of v0.1 and `menu suggest`. F15 adds `add`, and F16 adds `edit`. In v0.1 the help had no `menu suggest` line, and its second column started after 21 columns.

```text
PS> recipe-menu --help
Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]

Keep your recipes, plan a week's menu, and make its shopping list.

Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  menu new [WEEK]       Create an empty week menu.
  menu show [WEEK]      Show a week menu.
  menu suggest [WEEK]   Fill the empty meals of a week menu.
  shop [WEEK]           Make the shopping list of a week menu.

Options:
  --lang en|zh          The language of the output. Default: the settings, else English.
  --data FOLDER         The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version             Show the version.
  --help                Show this help.

WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.

PS> recipe-menu --version
recipe-menu 0.1.0
```

## Help in Chinese

```text
PS> recipe-menu --help --lang zh
用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]

保存菜谱，排一周的菜单，并生成它的购物清单。

命令：
  init                  创建数据文件夹和示例数据。
  check                 检查每个数据文件有没有错误。
  list                  列出菜谱。
  show ID               查看一个菜谱。
  search 词...          按名称、食材或标签找菜谱。
  menu new [周]         创建一个空的周菜单。
  menu show [周]        查看一个周菜单。
  menu suggest [周]     给一个周菜单的空餐填上菜。
  shop [周]             生成一个周菜单的购物清单。

选项：
  --lang en|zh          输出语言。默认：设置里的语言，否则英文。
  --data 文件夹         数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version             显示版本。
  --help                显示这份帮助。

“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。
```

## The language from the settings

After you set `language = "zh"` in `settings.toml`, every command speaks Chinese without `--lang`. `--lang en` still switches one command to English.

```text
PS> recipe-menu list --tag 素
ID                   名称         份数   标签
choy-sum             清炒菜心     2      快手、素

共 1 个菜谱带有标签“素”。

PS> recipe-menu list --tag 素 --lang en
ID                   Name                      Servings   Tags
choy-sum             Stir-fried choy sum       2          quick, vegetarian

1 recipe has the tag "vegetarian".
```

## Another data folder

```text
PS> recipe-menu list --data D:\OneDrive\recipe-menu
ID                   Name                      Servings   Tags
...

PS> $env:RECIPE_MENU_DATA = "D:\OneDrive\recipe-menu"
PS> recipe-menu list
ID                   Name                      Servings   Tags
...
```

## Mistakes on the command line

```text
PS> recipe-menu list --lang fr
--lang must be en or zh, not "fr".
Run "recipe-menu --help" to see the options.
PS> $LASTEXITCODE
2

PS> recipe-menu cook
Unknown command "cook".
Run "recipe-menu --help" to see the commands.
PS> $LASTEXITCODE
2
```

## No data folder yet

```text
PS> recipe-menu list
There is no data folder at C:\Users\Troy\recipe-menu.
Run "recipe-menu init" to create it, or name another folder with --data.
PS> $LASTEXITCODE
1

PS> recipe-menu list --lang zh
C:\Users\Troy\recipe-menu 没有数据文件夹。
运行“recipe-menu init”创建它，或用 --data 指定别的文件夹。
```

## A broken settings file

```text
PS> recipe-menu list
settings.toml, meals
  Unknown meal "supper". The meals are breakfast, lunch, and dinner.
Run "recipe-menu check" to see every problem.
PS> $LASTEXITCODE
1
```
