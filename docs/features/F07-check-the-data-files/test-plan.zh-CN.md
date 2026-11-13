---
troy-doc: "F07-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-12"
status: "Troy 已于 2026-11-12 批准"
mirror-of: "test-plan.md"
---

# F07 检查数据文件：测试方案

## 1. 功能

- 编号和名称：F07 检查数据文件
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.check` 的 `CHECK_COMMAND`、`recipe_menu.cli` 的 `main` 和 `python -m recipe_menu`。单元用例用它自己构造的 `Context` 调用 `CHECK_COMMAND.run`。功能用例像你输入 `recipe-menu check` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 里就有 `CHECK_COMMAND`（设计第 2 节）。集成用例在 `main` 上运行原型或 v0.1 场景，启动 `python -m recipe_menu`，或者随机组合错误。性能用例为 `python -m recipe_menu check` 计时（第 3 节）。每个用例在括号里注明它来自设计的哪一节，比如（2.2）。

架构师的审查（设计第 4 节）有五条发现和一条留给后续阶段的意见。用例在涉及测试的地方覆盖它们：

- 发现 1，PT01 很紧：F07-T25 在 PT01 数据文件夹上为 `check` 计时，第 3 节描述这个文件夹，`tests/pt01_support.py` 生成它。架构师建议的 `[refactor]` PR 可以在同一个文件夹上为 F04 的读取函数计时。
- 发现 2，Troy 随设计一起批准的文字 没有错误。 和 没有错误，也没有警告。：F07-T05 和 F07-T06 检查它们。
- 发现 3 关于选择 3 的措辞，不改变任何行为。
- 发现 4，缺少 `recipes/`，Troy 接受了设计的做法：F07-T13 检查这个文件夹的错误，以及随后 `2026-W47` 的 9 道菜各一个 `UNKNOWN_RECIPE`。
- 发现 5，F07 原型“A syntax mistake”：下一段说明 F07-T19 怎样测试它。
- 留给后续阶段的意见：下面关于 R09 的一段说明每个用例怎样用到 mock 省略的代码。

**F07 原型“A syntax mistake”。** 在示例文件夹上，设计 2.2 给出这一节的各行，还给出 `recipes\red-braised-pork.toml` 的警告，而这一节没有显示这个警告。原型的修改要走需求变更流程，目前还没有决定。在那之前，F07-T19 在两个文件夹上检查设计 2.2。在 init 文件夹上，它期望这一节第一行之后的各行，再加上 init 文件夹的计数行，正如 v0.1-S06 所期望的。在示例文件夹上，它期望设计 2.2 示例的各行，包括这个警告。测试把这些行写成字面量，从不读取原型文件。所以产品经理可能做的两种修改，无论是给这一节加上警告，还是给它换上 init 文件夹的计数行，都不会改动 F07 的任何测试，v0.1-S06 按原文成立。

每个用例都直接、通过 `main` 或通过 `python -m recipe_menu` 运行 `CHECK_COMMAND` 的 `run`，并检查报告的各行。mock 的 `run` 不读文件，也不写报告（设计第 2 节），所以每个测试在 mock 上都会失败（R09）。mock 定义了 `CHECK_COMMAND` 的所有字段和每条消息，并把它加进 `COMMANDS`。所以只测字段、帮助、用法错误或缺少数据文件夹的测试会在 mock 上通过，只检查退出码 0 的测试也会通过。F07-T01、F07-T04、F07-T17 和 F07-T22 只在检查过一次运行的报告之后才检查这些内容，每个期望退出码 0 的用例也都检查报告的各行。`tests/f07_support.py` 和 `tests/pt01_support.py` 在被导入时不调用 `check` 的任何接口。

每个用例都在 Linux 和 Windows 上运行。报告用系统的路径分隔符写出每个文件。所以单元格里的文件，比如 `recipes/mapo-tofu.toml`，代表 `str(Path("recipes", "mapo-tofu.toml"))`：在 Windows 上是原型里的 `recipes\mapo-tofu.toml`，在 Linux 上是 `recipes/mapo-tofu.toml`。根目录下的文件，比如 `settings.toml`，以及文件夹，比如 `recipes`，在两个系统上写法相同。F07-T13 用 `tests/f04_support.py` 的 `listing_denied` 拒绝列出一个文件夹，它在两个系统上的做法不同。F07-T25 在两个系统上的时间上限不同（第 3 节）。没有只在一个系统上运行的用例。

测试数据遵守这些规则：

- `tests/data/example/` 保存 `docs/prototypes/example-data.md` 的示例数据文件夹（架构第 10 节）。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这份副本上的 `DataFolder`。用例里的 `example` 就是这个 `DataFolder`。“一份新的示例副本”是用 `tests/f05_support.py` 的 `copy_example` 在 `tmp_path` 下另一个路径上复制的又一份副本，供需要多个文件夹的用例使用。
- “init 文件夹”代替 F08 的 `init` 创建的文件夹。它是一份新的示例副本，去掉 `tomato-egg` 以外的六个菜谱和 `menus/2026-W47.toml`，带有空文件夹 `menus/` 和 `shopping/`。这些就是 v0.1-S01 期望 `init` 写出的文件，与 `example-data.md` 所示逐字节相同。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。它在 `example` 之外，所以不带 `--data` 的一行找不到数据文件夹，除非用例在 `home / "recipe-menu"` 放了一个。`empty` 是空文件夹 `tmp_path / "empty"`，`missing` 是不存在的 `tmp_path / "missing"`。
- 测试用字节写出每个文件，或者用 `tests/f03_support.py` 的 `write` 写，它以 UTF-8 和 LF 换行写文件，并先创建所在的文件夹。所以一个文件在两个系统上字节相同。“把 F 里的 X 换成 Y”替换文件 F 里的第一个 X。
- 测试不改动代码仓库，不碰 `~/recipe-menu`，也不读时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`，F07-T23 和 F07-T25 启动 `python -m recipe_menu` 时把 `HOME` 和 `USERPROFILE` 设成 `tmp_path` 里的文件夹。F07-T13 拒绝列出某个文件夹之后，会还原它的权限。

调用 `main` 遵守这些约定：

- 像“在 F 中 `check --lang zh`”这样的一行代表 `main(["check", "--lang", "zh", "--data", str(F)], environ=environ, home=home, today=date(2026, 11, 10), stdout=out, stderr=err)`，其中 F 是一个文件夹或一个 `DataFolder` 的 `root`。它不传 `commands`。“不指定文件夹”的一行没有 `--data`。除非用例另给，`environ` 是 `{}`，out 和 err 是调用之后两个新的 `io.StringIO` 流里的文字。
- 结果是 `(code, out, err)`。对一个行列表 L，`(c, L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟一个 `"\n"`，此外没有别的内容。

预期的报告遵守这些约定：

- 一个问题写成它的 `where` 和它的消息，比如 `recipes/mapo-tofu.toml, ingredient 3`：菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`。它代表两行：两个空格加 `where`，然后四个空格加消息的文字。英文里，`where` 是文件、`, ` 和英文位置。中文里，它是文件、`，` 和中文位置，比如 `recipes/mapo-tofu.toml，食材 3`。没有位置的问题，`where` 只有文件，比如 `settings.toml` 或 `recipes`。下面的表给出消息和位置的文字。
- `R(r, w, E, W)` 代表调用所用语言里 2.2 的报告。`r` 和 `w` 是计数行里菜谱和周菜单的个数，`E` 和 `W` 是按顺序排列的错误列表和警告列表。它的各行是：计数行；一个空行；有错误时，按错误个数选的 `ERRORS_HEADING` 和每个错误的两行，没有错误时，有警告就写 `NO_ERRORS`，没有警告就写 `NO_ERRORS_OR_WARNINGS`；有警告时，一个空行、按警告个数选的 `WARNINGS_HEADING` 和每个警告的两行；有错误时，一个空行和 `FIX_AND_CHECK_AGAIN`。计数行是 `Checked the settings, the catalog, the pantry, r recipes, and w week menus.`，计数为 1 时写 `1 recipe` 和 `1 week menu`，或者是 `已检查设置、目录、常备清单、r 个菜谱和 w 个周菜单。`。其他文字来自 2.2 的消息表。F07-T05 和 F07-T06 把每种报告的各行完整写出，`tests/f07_support.py` 里构造 `R` 的辅助函数照它们来写。
- `COUNTS` 是 `Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.` 这一行，`COUNTS_ZH` 是 `已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。`。
- `PORK` 是警告 `recipes/red-braised-pork.toml, steps`：`NO_EN_STEPS`。`MAPO` 是错误 `recipes/mapo-tofu.toml, ingredient 3`：菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`。`TYPO` 是错误 `menus/2026-W47.toml, Monday dinner`：`UNKNOWN_RECIPE(recipe="tomato-eggs")`。
- `DISHES` 是没有任何已知菜谱 ID 时 `2026-W47` 给出的 9 个错误，按这个顺序：`menus/2026-W47.toml, Monday dinner` 处 `tomato-egg`、`choy-sum` 和 `rice` 的 `UNKNOWN_RECIPE`，`menus/2026-W47.toml, Tuesday dinner` 处 `mapo-tofu` 和 `rice` 的，`menus/2026-W47.toml, Saturday lunch` 处 `tomato-egg-noodles` 的，以及 `menus/2026-W47.toml, Sunday dinner` 处 `cola-wings`、`choy-sum` 和 `rice` 的。
- `AFTER` 是英文的 `R(7, 1, [], [PORK])`，即 F07 原型“After the fixes”的 7 行：`COUNTS`、``、`No errors.`、``、`1 warning:`、`  recipes/red-braised-pork.toml, steps` 和 `    No English steps. Commands show the Chinese steps instead.`。`AFTER_ZH` 是同一份报告的中文：`COUNTS_ZH`、``、`没有错误。`、``、`1 个警告：`、`  recipes/red-braised-pork.toml，步骤` 和 `    没有英文步骤。命令会改为显示中文步骤。`。
- `TWO` 是英文的 `R(7, 1, [MAPO, TYPO], [PORK])`，即 F07 原型“Errors and a warning, in English”的 13 行。`TWO_ZH` 是同一份报告的中文，即“The same check in Chinese”的 13 行。
- `EMPTY` 是设计 2.2 示例里空文件夹的 15 行，即英文的 `R(0, 0, [settings.toml: FILE_MISSING, catalog.toml: FILE_MISSING, pantry.toml: FILE_MISSING, recipes: FOLDER_MISSING, menus: FOLDER_MISSING], [])`。`EMPTY_ZH` 是同一份报告的中文，F07-T03 把它完整写出。
- `tests/f07_support.py` 把 `AFTER`、`TWO`、`EMPTY` 和它们的中文形式写成字面量，每个文件都用 `Path` 构造，所以这些用例不依赖 `R` 的辅助函数。

下面这些有名字的改动在文件夹里制造原型和场景的错误：

- 麻婆错误：把 `recipes/mapo-tofu.toml` 里的 `"郫县"` 换成 `""`，使食材 3 写成 豆瓣酱，与设计 2.2 的示例相同。
- 错字：把 `menus/2026-W47.toml` 里的 `"tomato-egg"` 换成 `"tomato-eggs"`，与 `tests/f06_support.py` 的 `typo` 写法相同。两处错误指麻婆错误和错字，即 F07 原型里的错误。
- 红烧肉的英文步骤：在 `recipes/red-braised-pork.toml` 末尾加上 `en = ["Braise the pork."]` 这一行，它去掉 `PORK`，与设计 2.2 的示例相同。
- 删逗号：删掉 `pantry.toml` 第 2 行里 `"盐"` 和 `"糖"` 之间的逗号，与 v0.1-S06 相同。
- 损坏的设置：把 `settings.toml` 写成 `meals = ["lunch", "supper"]` 这一行，与设计 2.2 的示例相同。
- S07 的错误：v0.1-S07 的 9 处错误。在目录食材列表末尾加上 `  { zh = "芥兰", en = "Broccoli", category = "produce" },` 和 `  { zh = "香菜", en = "Coriander", category = "meats" },`，作为食材 23 和 24。把 `pantry.toml` 里的 `"糖"` 换成 `"sesame oil"`。在 `recipes/rice.toml` 里，把 `servings = 2` 换成 `servings = 0`，把 `["主食"]` 换成 `["breakfast"]`，把 `"160 g"` 换成 `"1 cups"`。菜单由 `tests/f06_support.py` 的 `mistakes` 写出。
- W 的副本：`menus/W.toml` 保存示例菜单，其中 `week = "2026-W47"` 换成 `week = "W"`。
- 给一天加键：比如给周五加上 `supper = []`，即把菜单里的 `[friday]\n` 换成 `[friday]\nsupper = []\n`。

用例用到的消息如下，占位符已经填好。F07 自己的消息就是 2.2 消息表里的那些。测试把每段文字写成字面量，不引用任何消息，因为 `check` 和各读取函数的消息都是内部的（设计第 2 节，架构第 8 节）。

| 消息 | 英文 | 中文 |
| --- | --- | --- |
| 菜谱的 `UNKNOWN_INGREDIENT(name="N")` | `Unknown ingredient "N". Add it to the catalog, or use its name in the catalog.` | `未知食材“N”。请把它加入目录，或改用目录里的名称。` |
| 常备清单的 `UNKNOWN_INGREDIENT(name="N")` | `Unknown ingredient "N".` | `未知食材“N”。` |
| `UNKNOWN_TAG(tag="T")` | `Unknown tag "T". Add it to the catalog's tags.` | `未知标签“T”。请把它加入目录里的标签。` |
| `AMOUNT_UNKNOWN_UNIT(unit="U", amount="A")` | `Unknown unit "U" in "A".` | `数量“A”里有未知单位“U”。` |
| `SERVINGS_TOO_FEW(servings=S)` | `Servings must be a whole number of 1 or more, not S.` | `份数必须是不小于 1 的整数，不能是 S。` |
| `NO_EN_NAME` | `No English name. Commands show the Chinese name instead.` | `没有英文名称。命令会改为显示中文名称。` |
| `NO_EN_NOTE` | `No English note. Commands show the Chinese note instead.` | `没有英文备注。命令会改为显示中文备注。` |
| `NO_EN_STEPS` | `No English steps. Commands show the Chinese steps instead.` | `没有英文步骤。命令会改为显示中文步骤。` |
| `steps` 里的 `UNKNOWN_KEY(key="fr")` | `Unknown key "fr". The keys are zh and en.` | `未知键“fr”。可用的键：zh 和 en。` |
| `NOT_A_RECIPE_ID` | `This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Rename the file.` | `这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。请给文件改名。` |
| `UNKNOWN_CATEGORY(category="meats")` | `Unknown category "meats". The categories are produce, meat, eggs, staples, seasonings, and other.` | `未知分类“meats”。现有分类：produce、meat、eggs、staples、seasonings 和 other。` |
| `DUPLICATE_EN_NAME(name="N", other="ingredient K")` | `The English name "N" is also ingredient K's name. Names must be unique.` | `英文名称“N”也是食材 K 的名称。名称不能重复。` |
| `ITEM_NOT_A_TEXT` | `This item must be a text in quotation marks.` | `这一项必须是放在引号里的文字。` |
| 设置的 `UNKNOWN_MEAL(meal="M")` | `Unknown meal "M". The meals are breakfast, lunch, and dinner.` | `未知餐次“M”。可用的餐次：breakfast、lunch 和 dinner。` |
| 菜单的 `UNKNOWN_MEAL(meal="M")`，带 L | `Unknown meal "M". The settings name L.` | `未知餐次“M”。设置里的餐次：L。` |
| 没有设置时一天里的 `UNKNOWN_KEY(key="K")` | `Unknown key "K". The keys are breakfast, lunch, and dinner.` | `未知键“K”。可用的键：breakfast、lunch 和 dinner。` |
| `UNKNOWN_RECIPE(recipe="R")` | `Unknown recipe "R".` | `未知菜谱“R”。` |
| `WEEK_NOT_FILE_NAME(name="N", week="W")` | `The file name says N, but the file says W.` | `文件名是 N，但文件里写的是 W。` |
| `NOT_A_WEEK_NAME` | `This file name is not an ISO week such as 2026-W47. Rename the file.` | `这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。` |
| `TOML_ENDING_NOT_SMALL` | `The file name must end with ".toml" in small letters. Rename the file.` | `文件名必须以小写的“.toml”结尾。请给文件改名。` |
| `FILE_MISSING` | `The file is missing.` | `文件不存在。` |
| `FILE_IS_FOLDER` | `The file cannot be read: it is a folder.` | `无法读取文件：它是一个文件夹。` |
| `MISSING_BRACKET` | `The file cannot be read: a closing "]" is missing.` | `无法读取文件：缺少右方括号“]”。` |
| `MISSING_BRACE` | `The file cannot be read: a closing "}" is missing. A table in braces must be on one line.` | `无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。` |
| `FOLDER_MISSING` | `The folder is missing.` | `文件夹不存在。` |
| `FOLDER_IS_FILE` | `The folder cannot be read: it is a file.` | `无法读取文件夹：它是一个文件。` |
| `FOLDER_ACCESS_DENIED` | `The folder cannot be read: access is denied.` | `无法读取文件夹：没有访问权限。` |

F04 设计 2.5 和 2.6 给出菜谱的消息，F03 设计 2.8 到 2.10 给出目录、常备清单和文件形式的消息，F05 设计 2.3 给出设置的消息，F06 设计 2.8 和 2.9 给出菜单的消息，F03 设计 2.3 给出读取错误，F04 设计 3.1 给出文件夹的消息。在菜单的 `UNKNOWN_MEAL` 里，对示例的设置，L 是 `lunch and dinner` 和 `lunch 和 dinner`；对 `meals = ["dinner"]`，L 是 `dinner`；对 PT01 数据文件夹的设置，L 是 `breakfast, lunch, and dinner` 和 `breakfast、lunch 和 dinner`。

| 用例里的位置 | 英文 | 中文 |
| --- | --- | --- |
| `line N` | `line N` | `第 N 行` |
| 常备清单的 `item N` | `item N` | `第 N 项` |
| `ingredient N` | `ingredient N` | `食材 N` |
| 设置的 `meals` | `meals` | `餐次` |
| 菜谱的 `name`、`servings`、`tags` 和 `steps` | `name`、`servings`、`tags` 和 `steps` | `名称`、`份数`、`标签` 和 `步骤` |
| 菜单的 `week` | `week` | `周次` |
| 一天里的一餐，比如 `Monday dinner` 或 `Saturday lunch` | 星期的标签和餐次的标签，中间有空格 | `周一晚餐` 或 `周六午餐` |
| 一天里的其他键，比如 `Friday supper` | 星期的标签和这个键，中间有空格 | `周五 supper` |
| `Sunday dinner, dish 1` | `Sunday dinner, dish 1` | `周日晚餐，菜品 1` |

用例分在这些文件里，使每个文件都不超过 R06 的 500 行：

| 文件 | 用例 |
| --- | --- |
| `tests/test_f07_command.py` | F07-T01 到 F07-T03 |
| `tests/test_f07_report.py` | F07-T04 到 F07-T06 |
| `tests/test_f07_order.py` | F07-T07 到 F07-T10 |
| `tests/test_f07_folders.py` | F07-T11 到 F07-T14 |
| `tests/test_f07_options.py` | F07-T15 到 F07-T17 |
| `tests/test_f07_integration.py` | F07-T18 到 F07-T23 |
| `tests/test_f07_random.py` | F07-T24 |
| `tests/test_f07_performance.py` | F07-T25 |
| `tests/f07_support.py` | 没有测试。几个文件共用的辅助内容：用真正的命令调用 `main` 并给出 `(code, out, err)` 的函数，init 文件夹，有名字的改动，`R` 以及有名字的问题和报告，每个文件和文件夹的相对路径、字节和修改时间的记录，以及 F07-T24 的预期报告。它复用 `tests/f05_support.py` 的 `TODAY`、`make_home`、`copy_example` 和 `run_module`，`tests/f03_support.py` 的 `write` 和 `put_bytes`，`tests/f04_support.py` 的 `listing_denied`，以及 `tests/f06_support.py` 的 `typo` 和 `mistakes`。 |
| `tests/pt01_support.py` | 没有测试。第 3 节 PT01 数据文件夹的生成函数，以及 F07-T25 的计时运行。F09、F10、F11 和 F13 可以在它们自己的 PT01 用例里复用这两者。 |
| `tests/conftest.py` | 不变。F07 使用它的 fixture `example_folder`，以及 pytest 的 `tmp_path` 和 `record_property`。 |

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F07-T01 | 单元 | `CHECK_COMMAND`、`CHECK_COMMAND.run`、`main` | 设计 2.1 的示例。`CHECK_COMMAND` 的词是 `check`，用法在两种语言里都是 `check`，帮助行是 F05 原型里的那一行，没有参数，没有选项，`folder` 是 `FolderUse.CHECK`。它的 `run` 读取文件里的设置，而不是上下文里的设置，并用上下文的语言写出报告。只有 `check` 时，帮助在每种语言里都是选择 1 的 14 行，第二列从第 18 列之后开始（2.1，选择 1 和 2）。 | 示例里的各行，`folder` 是 `example`，`home` 是空的 `home`。在 `help_lines` 里，`main` 的调用还传入 `commands=(CHECK_COMMAND,)`。F08 到 F13 会把它们的命令加进 `COMMANDS`（选择 1），而这 14 行只在 `COMMANDS` 里只有 `check` 时成立。然后取 `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部内容。 | 示例的每个断言都成立，所以 `run` 给出 0，out 是 `AFTER`，err 为空。英文帮助正好是选择 1 第一个 `text` 块的 14 行，中文帮助正好是第二个块的 14 行。两者里，`  check` 一行和 `  --lang en\|zh` 一行的第二列都从下标 18 开始。 |
| F07-T02 | 单元 | `CHECK_COMMAND.run` | `run` 把文件里的设置传给 `read_week_menu`，从不传 `context.settings`。所以一个有效的设置文件即使写的餐次与上下文不同，也由它决定菜单可以有哪些餐次。报告只跟随 `context.lang`。`context.today` 和 `context.settings` 都不改变它，`context.err` 里也没有任何内容（2.1，选择 2）。 | `example`，其中 `settings.toml` 写成 `meals = ["dinner"]` 这一行。1. `run(Context(Lang.ZH, example, Settings(), out, err, date(2030, 1, 1)), Arguments())`。2. `run(Context(Lang.EN, example, Settings(Lang.ZH, tuple(Meal), 5), out, err, date(2026, 11, 10)), Arguments())`，用新的流。 | 每次都给出 1，err 为空。1. 中文的 `R(7, 1, [menus/2026-W47.toml, Saturday lunch: 菜单的 UNKNOWN_MEAL(meal="lunch")，带 dinner], [PORK])`。2. 同一份报告的英文。其他几天空的 `lunch` 列表不产生问题（F06 设计 2.9）。 |
| F07-T03 | 单元 | `CHECK_COMMAND.run` | `run` 从不抛异常。不存在的数据文件夹给出与空文件夹相同的五个错误，每个文件和每个文件夹各一个，计数都是 0，两种语言都是如此（2.1 的错误部分，选择 5）。 | 对 `DataFolder(missing)` 和 `DataFolder(empty)` 里的每个 F，以及 `Lang.EN` 和 `Lang.ZH` 里的每个 L：`run(Context(L, F, Settings(), out, err, date(2026, 11, 10)), Arguments())`，每次都用新的流。 | 每次都给出 1，err 为空。英文的 out 是 `EMPTY`。中文的 out 是 `EMPTY_ZH`：`已检查设置、目录、常备清单、0 个菜谱和 0 个周菜单。`、``、`5 个错误：`、`  settings.toml`、`    文件不存在。`、`  catalog.toml`、`    文件不存在。`、`  pantry.toml`、`    文件不存在。`、`  recipes`、`    文件夹不存在。`、`  menus`、`    文件夹不存在。`、`` 和 `改正错误后，再运行“recipe-menu check”。`。之后 `missing` 仍然不存在。 |
| F07-T04 | 功能 | `recipe-menu check`、`main` | 设计 2.2 的示例，按顺序，用真正的命令：F07 原型的两处错误的英文和中文报告，常备清单的语法错误，带周一早餐的损坏的设置，没有问题的报告，空的数据文件夹，缺少的数据文件夹，以及命令行上的两处错误（2.2）。 | 示例里的各行，`folder` 是 `example`，`home` 是空的 `home`，用示例的 `check`，它调用 `main` 时不传 `commands`。 | 示例的每个断言都成立。损坏的设置那次运行给出完整的报告 `R(7, 1, [settings.toml, meals: 设置的 UNKNOWN_MEAL(meal="supper")], [PORK])`。早餐不产生问题，因为 `read_week_menu` 得到的设置是 `None`（选择 2）。缺少文件夹之前的每次运行，err 都为空。 |
| F07-T05 | 功能 | `recipe-menu check` | 2.2 表里的四种报告，两种语言，各行完整写出：计数行之后的那一行，各块之间的空行，以及退出码。每行都以换行结束，最后一行之后没有别的内容。无论退出码是什么，错误流里都没有内容，警告从不改变退出码（2.2，选择 6）。 | 在下面每个文件夹中先运行 `check`，再运行 `check --lang zh`：1. 带红烧肉的英文步骤的 `example`。2. `example`。3. 带红烧肉的英文步骤和麻婆错误的 `example`。4. 带两处错误的 `example`。 | 1. `(0, [COUNTS, "", "No errors. No warnings."])` 和 `(0, [COUNTS_ZH, "", "没有错误，也没有警告。"])`。2. `(0, AFTER)` 和 `(0, AFTER_ZH)`。3. `(1, [COUNTS, "", "1 error:", "  recipes/mapo-tofu.toml, ingredient 3", '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.', "", 'Fix the errors and run "recipe-menu check" again.'])` 和 `(1, [COUNTS_ZH, "", "1 个错误：", "  recipes/mapo-tofu.toml，食材 3", "    未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。", "", "改正错误后，再运行“recipe-menu check”。"])`。4. `(1, TWO)` 和 `(1, TWO_ZH)`。 |
| F07-T06 | 功能 | `recipe-menu check` | `RECIPE_COUNT`、`WEEK_MENU_COUNT` 和 `WARNINGS_HEADING` 在计数为 1 时用单数形式，在计数为 0 和 2 时用复数形式。中文里每个计数的形式都相同（2.2）。`1 error:` 和 `2 errors:` 在 F07-T05 里。 | 在下面每个文件夹中先运行 `check`，再运行 `check --lang zh`：1. init 文件夹。2. `example`，从 `recipes/tomato-egg.toml` 里删掉 `, en = "Tomato and egg stir-fry"`，并加上 `2026-W48` 的副本。3. `empty`。 | 1. `(0, ["Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.", "", "No errors. No warnings."])` 和 `(0, ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"])`。2. `(0, ["Checked the settings, the catalog, the pantry, 7 recipes, and 2 week menus.", "", "No errors.", "", "2 warnings:", "  recipes/red-braised-pork.toml, steps", "    No English steps. Commands show the Chinese steps instead.", "  recipes/tomato-egg.toml, name", "    No English name. Commands show the Chinese name instead."])` 和 `(0, ["已检查设置、目录、常备清单、7 个菜谱和 2 个周菜单。", "", "没有错误。", "", "2 个警告：", "  recipes/red-braised-pork.toml，步骤", "    没有英文步骤。命令会改为显示中文步骤。", "  recipes/tomato-egg.toml，名称", "    没有英文名称。命令会改为显示中文名称。"])`。3. `(1, EMPTY)` 和 `(1, EMPTY_ZH)`。 |
| F07-T07 | 功能 | `recipe-menu check` | v0.1-S07 和 F07 原型“Other problems that check reports”。一次运行列出四个文件的每个问题，错误按步骤的顺序排列，`red-braised-pork` 的警告在它自己的块里（选择 4 和 6）。 | 带 S07 的错误的 `example`。先运行 `check`，再运行 `check --lang zh`。 | 先英文、再中文的 `(1, R(7, 1, E, [PORK]))`。E 依次是：`catalog.toml, ingredient 23`：`DUPLICATE_EN_NAME(name="Broccoli", other="ingredient 3")`。`catalog.toml, ingredient 24`：`UNKNOWN_CATEGORY(category="meats")`。`pantry.toml, item 3`：常备清单的 `UNKNOWN_INGREDIENT(name="sesame oil")`。`recipes/rice.toml, servings`：`SERVINGS_TOO_FEW(servings=0)`。`recipes/rice.toml, tags`：`UNKNOWN_TAG(tag="breakfast")`。`recipes/rice.toml, ingredient 1`：`AMOUNT_UNKNOWN_UNIT(unit="cups", amount="1 cups")`。`menus/2026-W47.toml, week`：`WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`。`menus/2026-W47.toml, Friday supper`：菜单的 `UNKNOWN_MEAL(meal="supper")`，带 lunch 和 dinner。`menus/2026-W47.toml, Sunday dinner, dish 1`：`SERVINGS_TOO_FEW(servings=0)`。英文的各行包含 v0.1-S07 期望的 9 个位置和消息。 |
| F07-T08 | 功能 | `recipe-menu check` | 错误块和警告块各自保持步骤的顺序，菜谱的警告和错误交替出现时，以及一个菜谱同时有两者时，也是如此（选择 4 和 6）。 | 带这些改动的 `example`。从 `recipes/choy-sum.toml` 里删掉 `, en = "crushed"`。把 `recipes/cola-wings.toml` 里的 `servings = 2` 换成 `servings = 0`。从 `recipes/tomato-egg.toml` 里删掉 `, en = "Tomato and egg stir-fry"`，并把 `["快手", "家常"]` 换成 `["快手", "breakfast"]`。错字。运行 `check`。 | `(1, R(7, 1, E, W))`。E 依次是 `recipes/cola-wings.toml, servings`：`SERVINGS_TOO_FEW(servings=0)`，`recipes/tomato-egg.toml, tags`：`UNKNOWN_TAG(tag="breakfast")`，然后是 `TYPO`。W 依次是 `recipes/choy-sum.toml, ingredient 2`：`NO_EN_NOTE`，`PORK`，然后是 `recipes/tomato-egg.toml, name`：`NO_EN_NAME`。按步骤的顺序，`choy-sum` 的警告在 `cola-wings` 的错误之前，`tomato-egg` 的警告在它自己的错误之前。 |
| F07-T09 | 功能 | `recipe-menu check` | 问题按 2.2 七个步骤的顺序出现：设置、目录、常备清单、`recipes/` 的列表、按 ID 顺序的每个菜谱、`menus/` 的列表，以及按时间顺序的每个周菜单。损坏的设置以 `None` 传到菜单（选择 2 和 4）。 | 带这些改动的 `example`。损坏的设置。在目录食材列表末尾加上 `  { zh = "芥兰", en = "Broccoli", category = "produce" },`。把 `pantry.toml` 里的 `"糖"` 换成 `"sesame oil"`。空文件 `recipes/Rice Bowl.toml`。把 `recipes/choy-sum.toml` 里的 `servings = 2` 换成 `servings = 0`。把 `recipes/tomato-egg-noodles.toml` 里的 `["快手", "主食"]` 换成 `["快手", "breakfast"]`。空文件 `menus/plan.toml`。`2026-W53` 的副本，给周五加上 `supper = []`。`2027-W01` 的副本，把 `"cola-wings", servings = 4` 换成 `"cola-wings", servings = 0`。做完两份副本之后，在 `menus/2026-W47.toml` 里做错字。运行 `check`。 | `(1, R(7, 3, E, [PORK]))`。E 依次是：`settings.toml, meals`：设置的 `UNKNOWN_MEAL(meal="supper")`。`catalog.toml, ingredient 23`：`DUPLICATE_EN_NAME(name="Broccoli", other="ingredient 3")`。`pantry.toml, item 3`：常备清单的 `UNKNOWN_INGREDIENT(name="sesame oil")`。`recipes/Rice Bowl.toml`：`NOT_A_RECIPE_ID`。`recipes/choy-sum.toml, servings`：`SERVINGS_TOO_FEW(servings=0)`。`recipes/tomato-egg-noodles.toml, tags`：`UNKNOWN_TAG(tag="breakfast")`。`menus/plan.toml`：`NOT_A_WEEK_NAME`。`TYPO`。`menus/2026-W53.toml, Friday supper`：没有设置时一天里的 `UNKNOWN_KEY(key="supper")`。`menus/2027-W01.toml, Sunday dinner, dish 1`：`SERVINGS_TOO_FEW(servings=0)`。 |
| F07-T10 | 功能 | `recipe-menu check` | 前一个文件给出的结果决定后一个文件的检查。读不了的目录以 `None` 传到常备清单和菜谱，所以它们只报告自身形式上的问题。有问题的目录会跳过一些食材，用到这些食材的菜谱就有错误，目录改好后这些错误就消失（2.2 的步骤 3 和 5，选择 4）。 | 1. `example`，把 `catalog.toml` 里的 `{ zh = "番茄", en = "Tomato", category = "produce" }` 换成 `{ zh = "番茄" en = "Tomato", category = "produce" }`，与 F03-T81 相同，再加上麻婆错误，并把 `pantry.toml` 里的 `"糖"` 换成 `3`。运行 `check`。2. 然后删掉 `catalog.toml`，运行 `check`。3. 一份新的示例副本，在 `catalog.toml` 里把 `{ zh = "葱", en = "Scallion", category = "produce", unit = "根" }` 换成 `{ zh = "米", en = "Rice", category = "staples" }`，并把 `{ zh = "五花肉", en = "Pork belly", category = "meat" }` 换成 `{ zh = "五花肉", en = "Pork belly", category = "meats" }`。这是 F03-T50 的两处目录错误。先运行 `check`，再运行 `check --lang zh`。4. 把它的 `catalog.toml` 写回示例的内容，运行 `check`。 | 1. `(1, R(7, 1, [catalog.toml, line 11: MISSING_BRACE, pantry.toml, item 3: ITEM_NOT_A_TEXT], [PORK]))`。`mapo-tofu` 里的 豆瓣酱，以及 `tomato-egg` 里 鸡蛋 的数量 `3`，都不产生问题（F03 设计 2.9，F04 设计 2.6）。2. `(1, R(7, 1, [catalog.toml: FILE_MISSING, pantry.toml, item 3: ITEM_NOT_A_TEXT], [PORK]))`。3. 先英文、再中文的 `(1, R(7, 1, E, [PORK]))`。E 依次是：`catalog.toml, ingredient 7`：`UNKNOWN_CATEGORY(category="meats")`。`catalog.toml, ingredient 12`：`DUPLICATE_EN_NAME(name="Rice", other="ingredient 4")`。然后是菜谱的 `UNKNOWN_INGREDIENT`：`recipes/cola-wings.toml, ingredient 4` 处的 葱，`recipes/mapo-tofu.toml, ingredient 6` 处的 葱，`recipes/red-braised-pork.toml, ingredient 1` 处的 五花肉，`recipes/red-braised-pork.toml, ingredient 5` 处的 葱，`recipes/rice.toml, ingredient 1` 处的 大米，`recipes/tomato-egg.toml, ingredient 3` 处的 葱，以及 `recipes/tomato-egg-noodles.toml, ingredient 4` 处的 葱。两行目录的问题就是 F07 原型“Other problems that check reports”里的两行。4. `(0, AFTER)`。 |
| F07-T11 | 功能 | `recipe-menu check` | 计数行计数的是 `list_recipe_ids` 给出的 ID 和 `list_menu_weeks` 给出的周，即使它们的文件有错误。不是菜谱 ID 或不是周的名称不计数，它的错误会写出这个名称。没有 `.toml` 结尾的条目不产生任何内容。每次列出的问题只出现一次（选择 3 和 5，F04 设计 3.1）。 | 加上这些条目的 `example`。在 `recipes/` 里：空文件 `Rice Bowl.toml`、`pancakes.TOML` 和 `notes.txt`，空文件夹 `drafts`，以及空文件夹 `old.toml`。在 `menus/` 里：空文件 `plan.toml`、`2026-w48.toml`、`2026-W49.TOML`、`notes.txt` 和 `2026-W47.toml.bak`，以及空文件夹 `2026-W50.toml`。运行 `check`。 | `(1, R(8, 2, E, [PORK]))`。E 依次是：`recipes/pancakes.TOML`：`TOML_ENDING_NOT_SMALL`。`recipes/Rice Bowl.toml`：`NOT_A_RECIPE_ID`。`recipes/old.toml`：`FILE_IS_FOLDER`。`menus/2026-W49.TOML`：`TOML_ENDING_NOT_SMALL`。`menus/2026-w48.toml`：`NOT_A_WEEK_NAME`。`menus/plan.toml`：`NOT_A_WEEK_NAME`。`menus/2026-W50.toml`：`FILE_IS_FOLDER`。8 个菜谱里包括 `old`，2 个周菜单里包括 `2026-W50`。 |
| F07-T12 | 功能 | `recipe-menu check` | 文件缺少或是一个文件夹时，计数行仍然写出设置、目录和常备清单，由错误说明出了什么问题。缺少 `settings.toml` 不会让 `check` 停下，菜单在没有设置的情况下读取（选择 2 和 5，F05 设计 2.5）。 | `example`，删掉 `settings.toml` 和 `pantry.toml`，把 `catalog.toml` 换成一个空文件夹，并给周一加上 `breakfast = ["rice"]`。先运行 `check`，再运行 `check --lang zh`。 | 先英文、再中文的 `(1, R(7, 1, [settings.toml: FILE_MISSING, catalog.toml: FILE_IS_FOLDER, pantry.toml: FILE_MISSING], [PORK]))`。早餐不产生问题。没有目录时，菜谱只给出自身形式上的问题。 |
| F07-T13 | 功能 | `recipe-menu check` | `recipes/` 或 `menus/` 缺少、是一个文件或列不出来时，计数为 0，并有这个文件夹的一个错误。没有菜谱 ID 时，每个菜单的每道菜都在这个文件夹的错误之后得到 `UNKNOWN_RECIPE`，这是 Troy 接受的做法（发现 4，选择 3 和 5）。 | 每个输入都从一份新的示例副本开始。1. 删掉 `recipes/`，运行 `check`。2. 把 `recipes` 换成一个空文件，运行 `check --lang zh`。3. 用 `listing_denied` 拒绝列出 `recipes/`，运行 `check`。4. 删掉 `menus/`，运行 `check`。5. 把 `menus` 换成一个空文件，运行 `check`。6. 拒绝列出 `menus/`，运行 `check`。 | 1. `(1, R(0, 1, [recipes: FOLDER_MISSING, *DISHES], []))`。2. 中文的 `(1, R(0, 1, [recipes: FOLDER_IS_FILE, *DISHES], []))`。3. `(1, R(0, 1, [recipes: FOLDER_ACCESS_DENIED, *DISHES], []))`。4. `(1, R(7, 0, [menus: FOLDER_MISSING], [PORK]))`。5. `(1, R(7, 0, [menus: FOLDER_IS_FILE], [PORK]))`。6. `(1, R(7, 0, [menus: FOLDER_ACCESS_DENIED], [PORK]))`。在 1 到 3 里，没有菜谱被读取，所以没有 `PORK`。 |
| F07-T14 | 功能 | `recipe-menu check` | `check` 只读取 `settings.toml`、`catalog.toml`、`pantry.toml`，以及 `recipes/` 和 `menus/` 里的 `.toml` 文件。它不读 `shopping/` 里的任何内容，不读根目录下的其他文件，也不读 `recipes/` 下层文件夹里的文件（2.2）。 | `example`，加上这些文件，每个都保存不是 TOML 的文字 `[[[`：根目录下的 `notes.txt` 和 `catalog.toml.bak`，`recipes/notes.txt`，`recipes/drafts/pancakes.toml`，以及 `menus/2026-W47.toml.bak`。再加上 `shopping/2026-W47.md`，保存不是 UTF-8 的字节 `b"\xff\xfe"`。运行 `check`。然后把 `shopping/` 换成一个保存 `[[[` 的文件，运行 `check`。 | 每次都给出 `(0, AFTER)`。 |
| F07-T15 | 功能 | `recipe-menu check`、`main` | 有错误的设置不会让 `check` 停下。它报告设置的问题，并用 `None` 读取菜单，所以一天里不是餐次的键得到没有设置时那种形式的 `UNKNOWN_KEY`。有错误的文件里的语言不算数。设置正常时，同一个键得到带设置里餐次的 `UNKNOWN_MEAL`（选择 2，F05 设计 2.5 和选择 4）。 | 1. `example`，在 `settings.toml` 里把 `meals = ["lunch", "dinner"]` 换成 `meals = ["lunch", "supper"]`，把 `language = "en"` 换成 `language = "zh"`，并给周五加上 `supper = []`。先运行 `check`，再运行 `check --lang zh`。2. 把 `settings.toml` 写回示例的内容。先运行 `check`，再运行 `check --lang zh`。 | 1. 先英文、再中文的 `(1, R(7, 1, [settings.toml, meals: 设置的 UNKNOWN_MEAL(meal="supper"), menus/2026-W47.toml, Friday supper: 没有设置时一天里的 UNKNOWN_KEY(key="supper")], [PORK]))`。2. 先英文、再中文的 `(1, R(7, 1, [menus/2026-W47.toml, Friday supper: 菜单的 UNKNOWN_MEAL(meal="supper")，带 lunch 和 dinner], [PORK]))`。 |
| F07-T16 | 功能 | `recipe-menu check`、`main` | `check` 读取 `cli` 选定的数据文件夹，并用 `cli` 选定的语言写报告：先 `--data`，再 `RECIPE_MENU_DATA`，再 `~/recipe-menu`；先 `--lang`，再设置，再英文（2.2 的参数，F05 设计 2.10）。 | 1. 在 `example` 中 `check --lang zh`。2. 不指定文件夹的 `check`，`environ` 为 `{"RECIPE_MENU_DATA": str(example.root)}`。3. 在 `example` 中 `check`，`environ` 为 `{"RECIPE_MENU_DATA": str(empty)}`。4. 在 `home / "recipe-menu"` 放一份带错字的新示例副本，运行不指定文件夹的 `check`。5. 把 `example` 设置里的 `language = "en"` 换成 `language = "zh"`。在 `example` 中先运行 `check`，再运行 `check --lang en`。 | 1. `(0, AFTER_ZH)`。2. `(0, AFTER)`。3. `(0, AFTER)`，因为 `--data` 优先于 `RECIPE_MENU_DATA`。4. `(1, R(7, 1, [TYPO], [PORK]))`。5. `(0, AFTER_ZH)`，然后 `(0, AFTER)`。 |
| F07-T17 | 功能 | `recipe-menu --help`、`main` | 真正的 `recipe-menu` 的帮助列出 `check` 和它的帮助行，第二列与选项的第二列对齐，两种语言都是如此。`check --help` 显示帮助，不运行 `check`，所以有错误的文件夹也给出退出码 0（选择 1，2.2 的参数）。 | 1. 在 `example` 中 `check`。2. 不指定文件夹的 `--help` 和 `--help --lang zh`。3. 在 `example` 里做麻婆错误。在 `example` 中 `check --help` 和 `check --help --lang zh`。4. 在 `example` 中 `check`。 | 1. `(0, AFTER)`。2. 每次都给出退出码 0，err 为空。在 out 里，第一行是 F05 设计 2.10 的用法行，第五行是 `Commands:` 或 `命令：`。从这一行到下一个空行之间，正好有一行以 `  check ` 开头，并以 `Check every data file for mistakes.` 或 `检查每个数据文件有没有错误。` 结尾。它的第二列开始的下标，与以 `  --lang en\|zh` 开头、接着是 `The language of the output.` 或 `输出语言。` 的那一行相同。无论 F08 到 F13 加入什么命令，这些规则都成立。3. 每次都给出与 2 在同一语言里相同的结果。4. `(1, R(7, 1, [MAPO], [PORK]))`。 |
| F07-T18 | 集成 | `recipe-menu check`、`main` | 在 `main` 上的 v0.1-S05，以及 F07 原型的三个输出：“Errors and a warning, in English”、“The same check in Chinese”和“After the fixes”。场景的文件夹在 `home / "recipe-menu"`，`check` 不带 `--data` 运行，与场景的步骤相同（2.2）。 | 在 `home / "recipe-menu"` 放一份带两处错误的新示例副本。1. 不指定文件夹的 `check`。2. 不指定文件夹的 `check --lang zh`。3. 撤销两处错误。4. 不指定文件夹的 `check`。 | 1. `(1, TWO)`。2. `(1, TWO_ZH)`。4. `(0, AFTER)`，v0.1-S13 的步骤 4 也期望这个结果。 |
| F07-T19 | 集成 | `recipe-menu check`、`main` | v0.1-S06 和 F07 原型“A syntax mistake”，按上面关于这一节的一段来测。在 init 文件夹上，报告是这一节的输出，换上 init 文件夹的计数行。在示例文件夹上，报告是设计 2.2 示例的输出，带有这一节没有显示的警告（发现 5）。 | 1. 在 `home / "recipe-menu"` 放 init 文件夹，并删逗号。不指定文件夹的 `check` 和 `check --lang zh`。2. 删逗号的 `example`。`check` 和 `check --lang zh`。 | 1. `(1, ["Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.", "", "1 error:", "  pantry.toml, line 2", '    The file cannot be read: a closing "]" is missing.', "", 'Fix the errors and run "recipe-menu check" again.'])`，这就是 v0.1-S06 期望的结果。中文是 `(1, ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "1 个错误：", "  pantry.toml，第 2 行", "    无法读取文件：缺少右方括号“]”。", "", "改正错误后，再运行“recipe-menu check”。"])`。2. 先英文、再中文的 `(1, R(7, 1, [pantry.toml, line 2: MISSING_BRACKET], [PORK]))`，英文就是设计示例的 11 行。 |
| F07-T20 | 集成 | `recipe-menu check`、`main` | 在 `main` 上、在 init 文件夹上的 v0.1-S01 步骤 2、v0.1-S02 步骤 2 和 v0.1-S04，以及 F08 原型“In English”的第二个输出（2.2）。 | 在 `home / "recipe-menu"` 放 init 文件夹，每次 `check` 都不指定文件夹。1. `check`。2. 把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`，然后 `check`。3. 把 `settings.toml` 写回，再写出 v0.1-S04 的菜谱 `recipes/cucumber-salad.toml`，各行是 `name = { zh = "拍黄瓜", en = "Smashed cucumber" }`、`servings = 2`、`tags = ["快手", "素"]`、`ingredients = [`、`  { item = "黄瓜", amount = "2 个" },`、`  { item = "大蒜", amount = "2 瓣" },`、`]`、`[steps]`、`zh = ["黄瓜拍碎，加蒜末拌匀。"]` 和 `en = ["Smash the cucumbers and toss them with the garlic."]`。然后 `check`。4. 在目录食材列表末尾加上 `  { zh = "黄瓜", en = "Cucumber", category = "produce" },`，然后 `check`。 | 1. `(0, ["Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.", "", "No errors. No warnings."])`。2. `(0, ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"])`。3. `(1, R(2, 0, [recipes/cucumber-salad.toml, ingredient 1: 菜谱的 UNKNOWN_INGREDIENT(name="黄瓜")], []))`。4. `(0, ["Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus.", "", "No errors. No warnings."])`。 |
| F07-T21 | 集成 | `recipe-menu check`、`main` | 在 `main` 上的 v0.1-S08 步骤 1：带字节顺序标记和 CRLF 换行的数据文件给出相同的报告（2.2，F03 设计 2.3）。 | 在 `home / "recipe-menu"` 放一份新的示例副本，把每个 `.toml` 文件重新写成 `b"\xef\xbb\xbf"` 加上它的文字的 UTF-8 字节，文字里每个 `"\n"` 换成 `"\r\n"`。不指定文件夹的 `check`。 | `(0, AFTER)`。 |
| F07-T22 | 集成 | `recipe-menu check`、`main` | 针对 `check` 的 v0.1-S23。`check` 不写文件，也不保存状态。每个文件和文件夹都保持它的字节和修改时间，没有新增文件或文件夹，同一行运行两次给出相同的结果（2.2 的副作用）。 | 先准备好 `example`、一份带 S07 的错误的新示例副本和 `empty`。测试记录 `tmp_path` 下每个文件和文件夹的相对路径、字节和 `st_mtime_ns`。它把下面每一行各运行两次，每次都用新的流：在 `example` 中 `check`，在 `example` 中 `check --lang zh`，在带 S07 的错误的副本中 `check`，在 `empty` 中 `check`，不指定文件夹的 `check`，在 `example` 中 `check --help`，以及在 `example` 中 `check extra`。然后再记录一次。 | 第一行给出 `(0, AFTER)`。每一行的两次运行结果相同。运行之后的记录与之前的记录相同。 |
| F07-T23 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令运行 `check`，把报告以 UTF-8 写到 stdout，不管 Python 给这个流设定了什么编码，stderr 里没有内容（2.2，F05 设计 2.9）。 | 用 `tests/f05_support.py` 的 `run_module`，与 F05-T48 相同，它把 `PYTHONIOENCODING` 设成 `ascii`。带两处错误的 `example`：1. `check --data <example>`。2. `check --data <example> --lang zh`。3. 撤销两处错误，用 `data=example.root` 运行 `check`，这会设置 `RECIPE_MENU_DATA`。 | 1. 退出码 1，stdout 是 `TWO` 的各行，stderr 为空。2. 退出码 1，stdout 是 `TWO_ZH` 的各行，stderr 为空。3. 退出码 0，stdout 是 `AFTER` 的各行，stderr 为空。 |
| F07-T24 | 集成 | `recipe-menu check`、`main` | 随机组合的错误。每种组合都给出退出码 0 或 1，输出流上是 2.2 的报告，错误流里没有内容，从不抛异常。报告里的问题就是各读取函数在 2.2 七个步骤里给出的问题，计数行计数的是两次列出给出的 ID 和周，语言遵循 F05。随机组合会碰到其他用例没有列出的顺序和文件之间的影响（2.2，选择 2 到 6）。 | `random.Random(20261114)` 构造 150 个数据文件夹，每个都是一份新的示例副本。对下面六组，按这个顺序，文件夹以 1/2 的机会得到这一组里的一个改动，组内各改动的机会相同。1. `settings.toml`：损坏的设置；删掉；把 `language = "en"` 换成 `language = "zh"`；把 `meals = ["lunch", "dinner"]` 换成 `meals = ["dinner"]`。2. `catalog.toml`：F07-T10 输入 1 的目录改动；F07-T10 输入 3 的两处目录改动；S07 的错误加上的两个食材；删掉。3. `pantry.toml`：删逗号；把 `"糖"` 换成 `"sesame oil"`；把 `"糖"` 换成 `3`。4. 一个菜谱：麻婆错误；把 `recipes/rice.toml` 里的 `servings = 2` 换成 `servings = 0`；红烧肉的英文步骤；从 `recipes/tomato-egg.toml` 里删掉 `, en = "Tomato and egg stir-fry"`。5. `recipes/`：空文件 `Rice Bowl.toml`；空文件 `pancakes.TOML`；空文件夹 `old.toml`；删掉这个文件夹。6. `menus/`：错字；给周五加上 `supper = []`；给周一加上 `breakfast = ["rice"]`；`2026-W53` 的副本；空文件 `plan.toml`；删掉这个文件夹。命令行是在这个文件夹中的 `check`、`check --lang en` 或 `check --lang zh`，机会相同。每一行运行两次，每次都用新的流。 | 没有调用抛异常，两次运行结果相同，err 为空。预期的报告有错误时，退出码正好是 1。out 是预期语言里的预期报告 `R(r, w, E, W)`。`r` 是 `list_recipe_ids` 给出的 ID 个数，`w` 是 `list_menu_weeks` 给出的周数。E 和 W 是下面这些问题里按顺序排列的错误和警告：`read_settings` 的，`read_catalog` 的，用这个目录调用 `read_pantry` 的，用这个目录调用 `read_recipes` 的，`list_menu_weeks` 的，以及用设置或 `None` 和这些 ID 的 `frozenset` 对每个周调用 `read_week_menu` 的。`read_recipes` 按顺序给出步骤 4 和 5 的问题（选择 3）。预期语言是 `--lang` 的语言；没有时，如果 `read_settings` 给出了设置，就是设置的 `language`；否则是英文（F05 设计 2.10 的步骤 3）。 |
| F07-T25 | 性能 | `recipe-menu check`、`python -m recipe_menu` | PT01：有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`check` 在 1 秒内完成，取从启动到退出的 5 次运行的中位数（需求 7.1，2.2）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"`。先不计时运行一次，然后计时运行 5 次 `python -m recipe_menu check --data <pt01>`，最后在最后一个菜谱和最后一个菜单里各做一处错误，再不计时运行一次，按第 3 节所说。 | 最后一次之前的每次运行都以 0 退出，stdout 是 `Checked the settings, the catalog, the pantry, 1000 recipes, and 52 week menus.`、`` 和 `No errors. No warnings.` 这几行，stderr 为空。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。最后一次运行以 1 退出，给出 `R(1000, 52, [recipes/recipe-1000.toml, steps: steps 里的 UNKNOWN_KEY(key="fr"), menus/2026-W52.toml, Sunday supper: 菜单的 UNKNOWN_MEAL(meal="supper")，带 breakfast、lunch 和 dinner], [])`。 |

## 3. 性能用例

| 编号 | 指标 | 机器 | 余量 | 基线 |
| --- | --- | --- | --- | --- |
| F07-T25 | PT01：有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`recipe-menu check` 在 1 秒内完成。以从启动到退出的 5 次运行的中位数为准。 | Troy 的电脑：Windows 11，使用 `recipe-menu` 环境的 Python 3.13。这个用例也在 CI 里运行，在 `.github/workflows/troy-mode.yml` 的 `ubuntu-24.04` 运行器上，那不是固定的机器（架构第 10 节）。 | Windows 上没有余量：中位数必须小于 1 秒，因为高于 PT01 的余量会让达不到 PT01 的命令通过（v0.1 测试方案第 3 节）。Linux 上是 3 秒，即指标的三倍，使这个用例在速度未知的运行器上能够通过，同时仍能发现慢了好几倍的情况。 | 首次运行。架构师的设计模型在 Troy 的电脑上取得 1.006 秒的中位数（设计第 4 节），但模型不是实现。F07 的实现 PR 记录第一个基线。 |

**哪个系统是 Troy 的电脑。** CI 只在 Linux 上运行（[需求第 7 节](../../requirements.zh-CN.md#7-非功能需求)，`.github/workflows/troy-mode.yml`），只有 Troy 的电脑在 Windows 上运行测试。所以 `sys.platform == "win32"` 时，用例使用 1 秒的上限，否则使用 3 秒的上限。如果 CI 将来在 Windows 上运行，要先修改本方案。

**PT01 数据文件夹。** `tests/pt01_support.py` 在用例开始计时之前，在 `tmp_path / "pt01"` 里生成它，形式与 v0.1 测试方案为 v0.1-S27 给出的相同。所以功能用例和版本测试为同一种数据计时。生成函数以 LF 换行写出每个文件：

- `settings.toml`：`language = "en"`、`meals = ["breakfast", "lunch", "dinner"]` 和 `servings = 2` 这几行。
- `catalog.toml`：示例目录的 `categories` 和 `tags`，以及有 300 项的 `ingredients` 列表。对 1 到 300 的 k，第 k 项是 `{ zh = "食材NNN", en = "Ingredient NNN", category = "C" }`，其中 NNN 是三位数字的 k，C 从 k = 1 起依次是 produce、meat、eggs、staples、seasonings 和 other。
- `pantry.toml`：`pantry = ["食材291", ..., "食材300"]`，即最后 10 种食材。
- 对 1 到 1,000 的 k，`recipes/recipe-NNNN.toml`，其中 NNNN 是四位数字的 k。名称是 `{ zh = "菜谱NNNN", en = "Recipe NNNN" }`，份数是 `1 + k % 4`。标签是 快手、家常、素、辣 和 主食 中从 0 开始数的第 `k % 5` 项和第 `(k + 1) % 5` 项。12 种食材都带备注 `{ zh = "切块", en = "cut into pieces" }`。第一种是数量为 `1 tsp` 的 食材001，所以每个菜谱都用到这种食材。然后，对 0 到 10 的 j，是编号为 `2 + (11 * k + j) % 299` 的食材，`j % 4` 为 0、1、2、3 时数量分别是 `200 g`、`15 ml`、`2 个` 和 `适量`。`[steps]` 在最后，`zh` 和 `en` 列表各有 6 步，比如 `第 1 步：把食材洗净切好，放进锅里翻炒两分钟。` 和 `Step 1: Wash and cut the ingredients, and stir-fry them for two minutes.`。
- 从 `2026-W01` 到 `2026-W52` 的每一周，`menus/2026-WNN.toml`：`week = "2026-WNN"` 这一行，以及从 `[monday]` 到 `[sunday]` 每天一个表，表里有 `breakfast`、`lunch` 和 `dinner` 三个键，每个是有 3 道菜的列表。第 w 周第 d 天第 m 餐的第 s 道菜（都从 0 开始数）用编号为 `((w - 1) * 63 + 9 * d + 3 * m + s) % 1000 + 1` 的菜谱。每顿晚餐的第一道菜写成 `{ recipe = "recipe-NNNN", servings = 4 }`，其他的写成放在引号里的 ID。所以每周有 63 道菜，来自 63 个不同的菜谱。
- 没有 `shopping/`。

一个菜谱文件约 2 KB，一个菜单文件约 1.5 KB。在 Troy 的电脑上写出这个文件夹约需 0.4 秒，用例不为它计时。测试经理在 F03 到 F06 读取函数之上的模型运行里检查过这个生成函数：这个文件夹给出 `No errors. No warnings.`。

**用例的步骤。**

1. 生成文件夹。
2. 不计时启动一次 `python -m recipe_menu check --data <pt01>`，并像步骤 3 那样检查它的输出。架构师的第一次运行用了 5.3 秒，之后几次约 1.0 秒（设计第 4 节）。Windows 第一次读取这 1,053 个新文件时很慢，而 Troy 自己的数据文件夹不会在每次运行时都付出这个代价。
3. 把同一条命令启动 5 次，每次都是新的进程，像 `tests/f05_support.py` 的 `run_module` 那样启动：`sys.executable -m recipe_menu`，在 `tmp_path` 里运行，`HOME` 和 `USERPROFILE` 设成一个空的家目录，不带 `RECIPE_MENU_DATA`。在 `subprocess.run` 之前和它返回之后各取一次 `time.perf_counter()`，两者之差就是从启动到退出的时间。每次运行都必须以 0 退出，stdout 正好是这个用例的三行，stderr 为空。不符合的运行会让用例失败，无论它用了多少时间。
4. 取 5 次时间的中位数，与所在系统的上限比较。
5. 用 `record_property` 记录 5 次时间、中位数和范围，使 JUnit 报告保存它们，供下次比较。
6. 不计时：在 `recipes/recipe-1000.toml` 末尾加上 `fr = ["Étape 1."]` 这一行，它把键 `fr` 放进 `[steps]`；在 `menus/2026-W52.toml` 末尾加上 `supper = []` 这一行，它把这个键放进 `[sunday]`。再运行一次。这是 `check` 最后读取的菜谱和菜单（选择 4）。报告写出它们的两个错误，说明命令读取了它们，所以计时的几次运行做了同样的工作。

**它怎样在 Troy 的电脑上运行。** 这个用例在 `tests/` 里，所以 Troy 的电脑上每次完整的测试运行都会运行它，主会话为每个 PR 用 `recipe-menu` 环境的 Python 启动这些测试。在 F07 的实现 PR 里，主会话还会在没有其他测试运行、构建或安装进行时，用 `python -m pytest tests/test_f07_performance.py --junitxml=reports/pt01.xml` 单独运行这个用例。PR 描述报告中位数和范围。这次运行就是基线。架构师建议在实现 PR 之前，为 F04 的读取函数提一个 `[refactor]` PR（设计第 4 节，发现 1）。它可以在 `tests/pt01_support.py` 生成的文件夹上为这些读取函数计时，这个文件由测试 PR 加入，所以它的数字和本用例的数字来自同一份数据。发布测试在同一台机器上运行 v0.1-S27。

**基准测试检查清单。** 这个用例这样回答 `benchmark-checklist` 的问题：

- 瓶颈：设计第 4 节指出了它。1,000 个菜谱的 `read_recipe` 占了约 1 秒里的 0.77 秒，大部分花在为没有问题的文件构造位置文字上。用例不做性能剖析，因为剖析工具会拖慢运行。`[refactor]` PR 会做剖析。
- 调优：用例像 Troy 那样运行命令。每次运行都是一个新的 Python 进程，使用已安装的包和它的编译文件，没有覆盖率统计，没有调试器，读取的文件已经被步骤 2 的不计时运行读过一次。coverage.py 只统计测试进程，所以 CI 里的 `coverage run -m pytest` 不会拖慢计时的进程。
- 极限：这 1,053 个文件约 2 MB，磁盘几毫秒就能读完。所以测出的时间是 Python 处理它们的工作。
- 错误：步骤 2 和 3 检查每次运行的退出码、完整的 stdout 和空的 stderr。
- 可重复性：计时运行 5 次，记录中位数和范围。与基线的差别如果小于基线各次运行的范围，就不是可测量的变化。
- 相关性：用例为整条命令从启动到退出计时，这正是 Troy 等待的时间。
- 工作确实发生了：每次运行的计数行写出 1,000 个菜谱和 52 个周菜单，步骤 6 说明命令读取了最后一个菜谱和最后一个菜单。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 单独的 `CHECK_COMMAND` 字段，`recipe_menu.commands.check` 的 `__all__` 列出的名称，以及作为 `check/messages.py` 里常量的消息。 | mock 完整声明了它们，所以只测它们的测试会在 mock 上通过（R09）。F07-T01 在一次运行之后检查字段，各用例通过报告检查每段文字。代码审查检查文字放在哪里。 |
| `check` 只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`，只通过 F03 到 F06 的读取函数接触磁盘。 | R07。CI 里的依赖检查器把每个引用与架构第 3 节的表比较。代码审查检查 `check` 自己不打开也不列出任何内容。 |
| `run` 不读参数、环境变量、日期或控制台流，也不保存状态。 | F07-T02 检查 `context.today` 不改变任何内容，`context.err` 里没有任何内容。F07-T22 检查两次运行结果相同，并且没有文件改变。架构第 8 节的 lint 规则和代码审查检查其余部分。 |
| `check` 每个数据文件只读一次，`recipes/` 和 `menus/` 各只列出一次，ID 集合只构造一次，报告只在最后一个文件之后写一次（设计第 2 节，选择 6）。 | 没有接口显示一个文件被读了几次。F07-T25 按 PT01 为整条命令计时，代码审查检查读取。F07-T07 到 F07-T11 检查这些规则带来的顺序和计数。 |
| `check` 运行中按 Ctrl+C，以及 `check` 还没读完每个文件时不写报告（2.2 的错误部分）。 | `check` 没有针对 Ctrl+C 的代码。F05-T41 检查命令的 `run` 里出现 `KeyboardInterrupt` 时退出码是 130。要在 `check` 中途让读取函数停下，就得替换一个读取函数，而没有外部接口允许这样做。 |
| 用非空的 `Arguments` 调用 `run`。 | 超出 2.1 的约束。`check` 不声明参数，也不声明选项，所以 `cli` 不会传入任何值。 |
| 设计示例里两处用法错误以外的 `check` 用法错误、它们的中文文字，以及中文的 `NO_DATA_FOLDER`。 | 它们由 `cli` 给出。F05-T28、F05-T29 和 F05-T36 用替身 `CHECK` 检查它们，它的词、帮助行、参数、选项和 `FolderUse` 与 `CHECK_COMMAND` 相同，F07-T01 检查了这一点。F07-T04 用真正的命令检查设计里的两处用法错误和缺少的数据文件夹。 |
| 在列出和读取之间被删掉的菜谱或菜单的 `FILE_MISSING`，文件的 `ACCESS_DENIED` 和 `SYSTEM_ERROR`，以及文件夹的 `FOLDER_SYSTEM_ERROR`。 | 第一种需要在 `check` 运行时删掉文件。F03-T17、F03-T18、F04-T53、F06-T27 和 F06-T48 通过读取函数检查其余几种。`check` 以同样的方式写出读取函数给出的每个问题，F07-T12 和 F07-T13 对其他读取错误展示了这一点。 |
| 带 v0.1 八个命令的帮助。 | F05-T45 用替身检查这些行，v0.1-S19 用真正的命令检查它们。F07-T17 在真正的 `COMMANDS` 的帮助里检查 `check` 这一行，所用的形式在后续功能加入命令后仍然成立。 |
| Windows Terminal 里的中文输出。 | CI 机器都没有 Windows 控制台（架构第 10 节），所以 v0.1-S25 由 Troy 检查。F07-T23 检查 `python -m recipe_menu` 以 UTF-8 写出中文报告。 |
| 文档注释只用英文。 | R05。troy-check 会拒绝文档注释里的汉字。 |
| 设计第 2 节对后续功能的计划：F08 的 `init` 和它的 `menus/`，F09 到 F14 的读取函数和参数，以及 F15 和 F16 复用 `check`。关于选择 3 措辞的发现 3。 | 每个后续功能的设计和测试方案覆盖它们。F07-T20 在 v0.1-S01 期望 `init` 写出的文件上检查报告。发现 3 不改变任何行为。 |
| 按原文、在示例文件夹上的 F07 原型“A syntax mistake”（发现 5）。 | 在这个文件夹上，它的各行与设计 2.2 不一致，修改由 Troy 通过变更流程决定。F07-T19 在 init 文件夹和示例文件夹上检查设计 2.2。 |

## 5. 与接口设计师的对齐记录

无。设计没有留下不清楚的用例，所以测试经理没有向接口设计师提问。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-12 | 初稿。 |
| 1.0 | 2026-11-12 | Troy 批准。 |
