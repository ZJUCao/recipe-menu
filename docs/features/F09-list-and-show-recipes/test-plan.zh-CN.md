---
troy-doc: "F09-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-13"
status: "Troy 已于 2026-11-13 批准"
mirror-of: "test-plan.md"
---

# F09 列出和查看菜谱：测试方案

## 1. 功能

- 编号和名称：F09 列出和查看菜谱
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.browse` 的 `LIST_COMMAND` 和 `SHOW_COMMAND`，`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的 `Context` 调用 `LIST_COMMAND.run` 或 `SHOW_COMMAND.run`。功能用例像你输入 `recipe-menu list` 或 `recipe-menu show` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 里是 `INIT_COMMAND`、`CHECK_COMMAND`、`LIST_COMMAND` 和 `SHOW_COMMAND`（设计选择 1）。集成用例在 `main` 上运行 v0.1 场景，启动 `python -m recipe_menu`，或者构造随机文件夹。两个性能用例为 `python -m recipe_menu list` 和 `show` 计时（第 3 节）。每个用例在括号里注明它来自设计的哪一节，比如（2.2）。设计的四个示例及其两行 `# raises` 分别在 F09-T01（2.1）、F09-T02（2.3）、F09-T04（2.2）和 F09-T12（2.4）里。

**A 点：`red-braised-pork` 的步骤。** Troy 于 2026-11-13 随设计选定了 A 点的方案 1。所以测试 PR（PR 4）除了新测试，还做两处修改，因为测试数据和测试都属于测试阶段（R02、R08）：

1. 在 `tests/data/example/recipes/red-braised-pork.toml` 里，`[steps]` 的 `zh` 列表换成 F09 原型“A missing language”的四个步骤，逐字照抄，顺序不变，代替原来的三个步骤：`五花肉冷水下锅，焯水后捞出。`、`小火把冰糖炒成焦糖色，下五花肉翻炒上色。`、`加生抽、姜片和热水，没过肉，小火炖 1 小时。` 和 `大火收汁，撒上葱段。`。文件的其余部分保持原有字节，文件仍然没有 `en` 步骤。
2. 在 F04-T38，即 `tests/test_f04_example_recipes.py` 里的 `test_f04_t38_the_other_six_example_recipes` 中，中文步骤的个数从 3 改为 4。这个测试的其他部分不变。F04 测试方案 1.1 版在 F04-T38 那一行里写明了这一点。

在架构师的模型上，只改文件时，只有 F04-T38 失败，把它的个数改成 4 之后，每个测试都通过（设计第 4 节）。没有别的测试读取这个文件的中文步骤（设计 A 点）。所以已验收功能的测试保持通过，符合 R10 的要求。F09-T13 把这四个步骤写成字面量来期望，这也正是 v0.1-S12 第 3 步所期望的。

**之前功能的测试。** 设计第 3 节说，运行真正 `COMMANDS` 的测试在 `COMMANDS` 加上 `list` 和 `show` 之后仍然成立：F05-T48、F05-T49、F07-T17 和 F08-T14。架构师在一个 `COMMANDS` 里有这两个命令的模型上运行了分支上的每个测试，全部通过（设计第 4 节）。F09 不改动这些测试。F09-T01 检查真正 `COMMANDS` 的帮助里 `list` 和 `show` 的两行，所用的形式在 F10 到 F13 加入它们的命令之后仍然成立。

**R09。** mock 定义了每条消息和带全部字段的两个命令，并把它们加进 `COMMANDS`。它的 `run` 函数不读文件，什么都不写，什么都不抛，并给出 0（设计第 2 节）。所以只检查命令的字段、某条消息、帮助、退出码 0，或者 `cli` 在运行命令之前所做的事情的测试，会在 mock 上通过。这包括缺少数据文件夹、损坏的设置、`list extra` 和没有值的 `--tag`，也包括只检查没有文件被修改的测试。每个检查这类内容的用例，也检查 mock 弄错的东西：`list` 或 `show` 的输出，退出码 1 或 2，`run` 抛出的 `UsageError`，或者故障工具记录的读取。F09-T01、F09-T02、F09-T19 和 F09-T25 只在一个 mock 会弄错的结果旁边检查这类内容。每个期望退出码 0 的用例也检查完整的输出。`tests/f09_support.py` 和 `tests/f09_texts.py` 在被导入时不调用 F09 的任何接口。

**两个系统。** 每个用例都在 Linux 和 Windows 上运行，在哪个系统上都不跳过。CI 只在 Linux 上运行，而 R09 把跳过的测试算作没有失败的测试。问题用系统的路径分隔符写出它的文件。所以在预期的一行里，`recipes/mapo-tofu.toml` 代表 `str(Path("recipes", "mapo-tofu.toml"))`：在 Windows 上是原型里的 `recipes\mapo-tofu.toml`，在 Linux 上是 `recipes/mapo-tofu.toml`。根目录下的文件，比如 `catalog.toml`，以及文件夹 `recipes`，在两个系统上写法相同。`list` 和 `show` 的表格里没有路径，所以它们的各列在两个系统上宽度相同，中文表格里每个汉字占两列，和原型一样。有三类输入涉及两个系统不同的地方，每类在两个系统上给出相同的结果：

- `recipes/rice.TOML`（F09-T11 和 F09-T18）。用例用 `Path.rename` 把 `rice.toml` 改名为 `rice.TOML`，这在两个系统上都可行，在文件名不区分大小写的 Windows 上也可行。改名之后 `recipes/` 里有 `rice.TOML`，没有 `rice.toml`，所以 `list_recipe_ids` 为它给出 `TOML_ENDING_NOT_SMALL`，并且没有 ID `rice`（F04 设计 2.5）。Linux 可以让 `rice.toml` 和 `rice.TOML` 同时存在，Windows 不行，所以没有用例同时创建两者。
- `show Tomato-Egg` 和 `show con`（F09-T03 和 F09-T16）。对前者，Windows 会打开 `tomato-egg.toml`，而 `con` 被 Windows 留给设备。`show` 在读文件之前用 `is_recipe_id` 检查这个值，所以两者在两个系统上都给出退出码 2。没有用例创建以设备名命名的文件，Windows 会拒绝创建它（F04-T12 因此只在 Linux 上运行）。
- F09-T23 的数据文件夹 `One Drive/菜谱` 的路径里有空格和汉字，在两个系统上都是合法路径。

测试经理用 Python 3.13.18 在 Troy 的电脑上做了这次改名。测试经理还在那里用 main 上的读取函数和一个按设计实现这两个命令的模型，算出了下面的预期文本。

**读取记录。** F09-T20 记录 `list` 和 `show` 打开了哪些文件、列出了哪些文件夹。它使用 `tests/f08_support.py` 的故障工具 `faults(base)`，不带规则。故障工具把对 `base` 下每个路径的打开记为 `read` 加上相对于 `base`、用 `/` 写的路径，把每次 `os.scandir` 或 `os.listdir` 的列出记进“列出记录”（F08 测试方案第 2 节）。`browse` 只通过 F03 和 F04 的读取函数访问磁盘（设计第 2 节），这些函数已经在 main 上。在那里，用 Python 3.13.18 时，`read_toml` 通过 `open` 或 `io.open` 把每个文件打开一次，`list_toml_files` 通过 `os.scandir` 或 `os.listdir` 把一个文件夹列出一次。所以记录取决于 F09 调用哪些读取函数，不取决于 F09 的其他代码。`cli` 在运行命令之前读取 `settings.toml`，所以每份记录都以 `read settings.toml` 开头。测试经理在 Troy 的电脑上用 main 上的读取函数和那个模型得到了 F09-T20 的记录。

测试数据遵守这些规则：

- `EXAMPLE` 是代码仓库里的 `tests/data/example/` 文件夹，带有 A 点的修改（架构第 10 节）。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这份副本上的 `DataFolder`。用例里的 `example` 就是这个 `DataFolder`。“P 处的一份新的示例副本”是用 `tests/f05_support.py` 的 `copy_example` 复制的又一份副本。不带 P 的“一份新的示例副本”在 `tmp_path` 下它自己的路径上。
- “P 处的 init 文件夹”由 `tests/f07_changes.py` 的 `make_init` 创建：一份新的示例副本，除 `tomato-egg` 外没有菜谱，没有菜单，带有空文件夹 `menus/` 和 `shopping/`。F08-T24 显示 `init` 创建的字节与它相同。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。它在 `example` 之外，所以不带 `--data` 的一行找不到数据文件夹，除非用例在 `home / "recipe-menu"` 放了一个。
- 测试用 `tests/f03_support.py` 的 `write` 写出每个文件，它以 UTF-8 和 LF 换行写文件，并先创建所在的文件夹，或者直接写字节。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 替换文件 F 里的第一个 X，`edit` 会检查 F 里有 X。
- 测试不改动代码仓库，不碰 `~/recipe-menu`，也不读时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`，F09-T26、F09-T28 和 F09-T29 启动 `python -m recipe_menu` 时把 `HOME` 和 `USERPROFILE` 设成 `tmp_path` 里的一个文件夹。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

下面这些有名字的改动构造用例的文件夹。每个改动作用于它所在用例的数据文件夹：

- 麻婆错误：用 `tests/f07_changes.py` 的 `mapo_mistake` 把 `recipes/mapo-tofu.toml` 里的 `"郫县"` 换成 `""`。食材 3 于是写成目录里没有的 豆瓣酱。
- 米饭 0 份：用 `servings_zero` 把 `recipes/rice.toml` 里的 `servings = 2` 换成 `servings = 0`。米饭 3 份：把同一个文件里的 `servings = 2` 换成 `servings = 3`。
- 删逗号、错字、损坏的设置和目录花括号错误：`tests/f07_changes.py` 的 `the_comma`、`the_typo`、`broken_settings` 和 `catalog_brace`。目录花括号错误删掉 `catalog.toml` 第 11 行里 `zh = "番茄"` 后面的逗号。
- 没有目录：删掉 `catalog.toml`。
- 没有菜谱文件夹：删掉 `recipes/` 和它里面的一切。菜谱是文件：同样删掉，然后在 `recipes` 的路径上写一个空文件。
- 空的菜谱文件夹：删掉 `recipes/` 里的每个条目，使这个文件夹为空。不是菜谱：同样删掉，然后写出内容为 `Ideas\n` 的 `recipes/notes.txt`，并创建空文件夹 `recipes/old`。
- Rice Bowl：加上空文件 `recipes/Rice Bowl.toml`。大写的 rice：把 `recipes/rice.toml` 改名为 `recipes/rice.TOML`。文件夹 x：创建空文件夹 `recipes/x.toml`。
- 汤：在 `catalog.toml` 的标签里 `staple` 那一行后面加上 `  { zh = "汤", en = "soup" },` 这一行，与设计 2.2 的示例相同。
- 一个标签、两个标签和没有标签：把 `catalog.toml` 从 `tags = [` 到末尾的文字分别换成 `tags = [\n  { zh = "快手", en = "quick" },\n]\n`，换成同样的文字并在 `quick` 那一行后面加上 `  { zh = "家常", en = "home-style" },` 这一行，以及换成 `tags = []\n`。
- 额外的菜谱：用下面的文字写出 `recipes/boiled-egg.toml`、`recipes/steamed-egg.toml` 和 `recipes/water.toml`。`boiled-egg` 是设计 2.4 示例里的菜谱，没有中文名称、备注和步骤。`steamed-egg` 没有英文名称、备注和步骤，做 3 份。`water` 没有标签，也没有食材。
- 带 S 的长名称：删掉 `recipes/rice.toml` 以外的每个菜谱文件，用下面的文字写出 `recipes/a-long.toml`，其中 `{S}` 换成 S。S 是 TOML 转义 `\n`、`\r\n` 和 `\u2028` 之一，文件按这里的写法保存它们，带着反斜杠，所以文件里没有控制字符。`read_recipe` 给出的名称于是在 S 的位置上有 U+000A、U+000D U+000A 或 U+2028 LINE SEPARATOR，`str.splitlines` 把每个名称拆成两行。

```toml
name = { en = "Boiled egg" }
servings = 1
tags = []
ingredients = [
  { item = "鸡蛋", amount = "2", note = { en = "at room temperature" } },
  { item = "盐", amount = "适量" },
]
[steps]
en = ["Boil the eggs for 8 minutes."]
```

```toml
name = { zh = "蒸蛋" }
servings = 3
tags = ["快手", "素"]
ingredients = [
  { item = "鸡蛋", amount = "2", note = { zh = "打散" } },
  { item = "葱", amount = "1", note = { zh = "切葱花" } },
  { item = "盐", amount = "适量" },
]
[steps]
zh = ["鸡蛋加温水和盐打散。", "撒上葱花，蒸 10 分钟。"]
```

```toml
name = { zh = "白开水", en = "Boiled water" }
servings = 1
tags = []
ingredients = []
[steps]
zh = ["把水烧开。"]
en = ["Boil the water."]
```

```toml
name = { zh = "长长的第一行{S}尾", en = "A long first line{S}end" }
servings = 2
tags = ["快手"]
ingredients = [{ item = "大米", amount = "100 g" }]
[steps]
zh = ["煮饭。"]
en = ["Cook the rice."]
```

调用 `main` 遵守这些约定：

- 像“在 F 里 `list --tag 快手`”这样的一行，代表 `tests/f07_support.py` 的 `call(home, ["list", "--tag", "快手", "--data", str(F)], environ)`。它用 `home`、`environ`、`today=date(2026, 11, 10)` 和两个新的 `io.StringIO` 流运行 `main`，不传 `commands`，所以 `main` 使用真正的 `COMMANDS`。F 是一个文件夹或一个 `DataFolder` 的 `root`。“不指定文件夹”的一行没有 `--data`。除非用例给出，`environ` 是 `{}`。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟着 `"\n"`，此外没有别的。`(c, err L)` 代表 `(c, "", err)`，其中 err 是 L 的各行，每行后面跟着 `"\n"`。测试比较完整的文字，从不比较它们的 `splitlines()`，因为 `splitlines()` 也在 U+000D 和 U+2028 处拆分，会掩盖 F09-T09 必须确认输出里没有的行分隔符。
- `STOP(W, M)` 是 `stop_at_error` 的三行英文：W，两个空格加 M 的英文文字，以及 `Run "recipe-menu check" to see every problem.`。`STOP_ZH(W, M)` 是同样的中文：中文的 W，两个空格加 M 的中文文字，以及 `运行“recipe-menu check”查看所有问题。`。W 是一个文件，比如 `catalog.toml`，或者一个文件加一个位置，比如 `recipes/mapo-tofu.toml, ingredient 3`，中文是 `recipes/mapo-tofu.toml，食材 3`。`tests/f05_texts.py` 的 `stopped` 构造这个结果。
- “在 `check` 的错误之中”指的是：在同一个文件夹里、用同一种语言运行的 `check` 以退出码 1 结束，它的报告在错误标题下有 `  W` 和四个空格加 M 的文字这两行，正如 F07 设计 2.2 写出一个错误那样。

预期文本如下。测试在 `tests/f09_texts.py` 里把每一段都写成字面量。它们不引用任何消息，也从不读原型文件，因为 `browse` 和各读取函数的消息都是内部的（设计第 2 节，架构第 8 节）。

- `LIST` 和 `LIST_ZH` 是 F09 原型“List the recipes”的两段输出，各 10 行，设计 2.2 的示例把它们写成 `ENGLISH` 和 `CHINESE`。它们的行从 1 开始数：第 1 行是标题，第 2 到 8 行依次是 `choy-sum`、`cola-wings`、`mapo-tofu`、`red-braised-pork`、`rice`、`tomato-egg` 和 `tomato-egg-noodles` 的行，第 9 行为空，第 10 行是计数行。
- `QUICK` 是 F09 原型“List the recipes with one tag”的第一段输出：`LIST` 的第 1、2、7 和 8 行，一个空行，以及 `3 recipes have the tag "quick".`。`QUICK_ZH` 是它的第二段输出：`LIST_ZH` 的同样几行，一个空行，以及 `共 3 个菜谱带有标签“快手”。`。`BREAKFAST` 是它的第三段输出，即 `Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.` 这一行，`BREAKFAST_ZH` 是 `未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。`。
- `VEG_ZH` 和 `VEG` 是 F05 原型“The language from the settings”的两段输出，各 4 行：`LIST_ZH` 或 `LIST` 的第 1 和 2 行，一个空行，以及 `共 1 个菜谱带有标签“素”。` 或 `1 recipe has the tag "vegetarian".`。
- `INIT_LIST` 是 init 文件夹的列表：`ID           Name                      Servings   Tags`、`tomato-egg   Tomato and egg stir-fry   2          quick, home-style`、一个空行和 `1 recipe.`。`INIT_LIST_ZH` 是 `ID           名称       份数   标签`、`tomato-egg   番茄炒蛋   2      快手、家常`、一个空行和 `共 1 个菜谱。`。
- `TOMATO` 是 F09 原型“Show one recipe”的 16 行，设计 2.4 的示例把它写成 `TOMATO_EGG`。`FOUR_ZH` 是“Show one recipe for 4 servings, in Chinese”的 16 行。`PORK` 是“A missing language”的 15 行，第 12 到 15 行是 A 点的四个步骤。`MAPO` 是“An unknown ID”的那一行 `No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.`，`MAPO_ZH` 是 `没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。`。
- `TOMATO_ZH` 是 `FOUR_ZH`，但第 2 行是 `份数：2   标签：快手、家常`，第 5 到 10 行是 `  番茄     300 g    切块`、`  鸡蛋     3 个`、`  葱       1 根     切葱花`、`  盐       适量`、`  糖       1 茶匙` 和 `  食用油   2 汤匙`。`FOUR` 是 `TOMATO`，但第 2 行是 `Servings: 4 (the recipe makes 2)   Tags: quick, home-style`，第 5 到 10 行是 `  Tomato        600 g      cut into wedges`、`  Egg           6 pieces`、`  Scallion      2 stalks   chopped`、`  Salt          to taste`、`  Sugar         2 tsp` 和 `  Cooking oil   4 tbsp`。
- `PORK_ZH` 有 15 行：`红烧肉  Red-braised pork belly`、`份数：2   标签：家常`、一个空行、`食材`、`  五花肉   1 斤     切成 3 厘米见方的块`、`  冰糖     30 g`、`  生抽     2 汤匙`、`  姜       3 片`、`  葱       2 根`、一个空行、`步骤`，以及 `PORK` 的第 12 到 15 行。
- `RICE` 有 9 行：`Steamed rice  米饭`、`Servings: 2   Tags: staple`、一个空行、`Ingredients`、`  Rice   160 g`、一个空行、`Steps`、`  1. Rinse the rice, add water, and soak it for 20 minutes.` 和 `  2. Cook it in a rice cooker, and let it rest for 10 minutes.`。
- `BOILED` 是设计 2.4 示例里 `boiled` 的 9 行。`BOILED_ZH` 是 `Boiled egg`、`份数：1`、一个空行、`食材`、`  鸡蛋   2 个   at room temperature`、`  盐     适量`、一个空行、`步骤（没有中文步骤，所以这里是英文步骤）` 和 `  1. Boil the eggs for 8 minutes.`。
- `WATER` 是 `Boiled water  白开水`、`Servings: 1`、一个空行、`Steps` 和 `  1. Boil the water.`。`WATER_ZH` 是 `白开水  Boiled water`、`份数：1`、一个空行、`步骤` 和 `  1. 把水烧开。`。
- `HELP` 是 F08 测试方案里 `HELP` 的 15 行，在 `check` 那一行后面加上 `  list            List the recipes.` 和 `  show ID         Show one recipe.`，共 17 行。`HELP_ZH` 是 F08 测试方案里 `HELP_ZH` 的 15 行，在 `check` 那一行后面加上 `  list            列出菜谱。` 和 `  show ID         查看一个菜谱。`。这是 `COMMANDS` 里只有 `init`、`check`、`list` 和 `show` 时设计 2.1 的帮助。

`STEAMED` 和 `STEAMED_ZH` 是 `show steamed-egg` 的输出：

```text
蒸蛋
Servings: 3   Tags: quick, vegetarian

Ingredients
  Egg        2 pieces   打散
  Scallion   1 stalk    切葱花
  Salt       to taste

Steps (no English steps, so these are the Chinese steps)
  1. 鸡蛋加温水和盐打散。
  2. 撒上葱花，蒸 10 分钟。
```

```text
蒸蛋
份数：3   标签：快手、素

食材
  鸡蛋   2 个   打散
  葱     1 根   切葱花
  盐     适量

步骤
  1. 鸡蛋加温水和盐打散。
  2. 撒上葱花，蒸 10 分钟。
```

`EXTRA` 和 `EXTRA_ZH` 是在带额外菜谱的一份新的示例副本上运行 `list` 的输出。第 2、8 和 11 行是 `boiled-egg`、`steamed-egg` 和 `water` 的行：

```text
ID                   Name                      Servings   Tags
boiled-egg           Boiled egg                1
choy-sum             Stir-fried choy sum       2          quick, vegetarian
cola-wings           Cola chicken wings        2          home-style
mapo-tofu            Mapo tofu                 2          spicy, home-style
red-braised-pork     Red-braised pork belly    2          home-style
rice                 Steamed rice              2          staple
steamed-egg          蒸蛋                      3          quick, vegetarian
tomato-egg           Tomato and egg stir-fry   2          quick, home-style
tomato-egg-noodles   Tomato and egg noodles    2          quick, staple
water                Boiled water              1

10 recipes.
```

```text
ID                   名称         份数   标签
boiled-egg           Boiled egg   1
choy-sum             清炒菜心     2      快手、素
cola-wings           可乐鸡翅     2      家常
mapo-tofu            麻婆豆腐     2      辣、家常
red-braised-pork     红烧肉       2      家常
rice                 米饭         2      主食
steamed-egg          蒸蛋         3      快手、素
tomato-egg           番茄炒蛋     2      快手、家常
tomato-egg-noodles   番茄鸡蛋面   2      快手、主食
water                白开水       1

共 10 个菜谱。
```

`LONG` 和 `LONG_ZH` 是在带长名称的一份新的示例副本上运行 `list` 的输出，对每个 S 都相同。第 2 和 3 行是 `a-long` 那一行的两行，第 4 行是 `rice` 的行：

```text
ID       Name                Servings   Tags
a-long   A long first line   2          quick
         end
rice     Steamed rice        2          staple

2 recipes.
```

```text
ID       名称           份数   标签
a-long   长长的第一行   2      快手
         尾
rice     米饭           2      主食

共 2 个菜谱。
```

`LONG_STAPLE` 是 `LONG` 的第 1 和 4 行、一个空行和 `1 recipe has the tag "staple".`。`LONG_QUICK` 是 `LONG` 的第 1 到 3 行、一个空行和 `1 recipe has the tag "quick".`。`LONG_STAPLE_ZH` 是 `LONG_ZH` 的第 1 和 4 行、一个空行和 `共 1 个菜谱带有标签“主食”。`。`LONG_QUICK_ZH` 是 `LONG_ZH` 的第 1 到 3 行、一个空行和 `共 1 个菜谱带有标签“快手”。`。

`S04_LIST`、`CUCUMBER` 和 `CUCUMBER_ZH` 是 v0.1-S04 第 5 步的输出，以及同一个 `show` 的中文输出：

```text
ID               Name                      Servings   Tags
cucumber-salad   Smashed cucumber          2          quick, vegetarian
tomato-egg       Tomato and egg stir-fry   2          quick, home-style

2 recipes.
```

```text
Smashed cucumber  拍黄瓜
Servings: 2   Tags: quick, vegetarian

Ingredients
  Cucumber   2 pieces
  Garlic     2 cloves

Steps
  1. Smash the cucumbers and toss them with the garlic.
```

```text
拍黄瓜  Smashed cucumber
份数：2   标签：快手、素

食材
  黄瓜   2 个
  大蒜   2 瓣

步骤
  1. 黄瓜拍碎，加蒜末拌匀。
```

`browse` 的消息的文字就是设计 2.2 和 2.4 各表里的文字，`cli` 的用法错误的文字就是 F05 设计 2.10 里的文字。用例把它们连同值一起写出。用例里读取函数的消息如下：

| 消息 | 英文 | 中文 |
| --- | --- | --- |
| `FILE_MISSING` | `The file is missing.` | `文件不存在。` |
| `FILE_IS_FOLDER` | `The file cannot be read: it is a folder.` | `无法读取文件：它是一个文件夹。` |
| `MISSING_BRACE` | `The file cannot be read: a closing "}" is missing. A table in braces must be on one line.` | `无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。` |
| `FOLDER_MISSING` | `The folder is missing.` | `文件夹不存在。` |
| `FOLDER_IS_FILE` | `The folder cannot be read: it is a file.` | `无法读取文件夹：它是一个文件。` |
| 列出时的 `NOT_A_RECIPE_ID` | `This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Rename the file.` | `这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。请给文件改名。` |
| `TOML_ENDING_NOT_SMALL` | `The file name must end with ".toml" in small letters. Rename the file.` | `文件名必须以小写的“.toml”结尾。请给文件改名。` |
| 菜谱的 `UNKNOWN_INGREDIENT(name="N")` | `Unknown ingredient "N". Add it to the catalog, or use its name in the catalog.` | `未知食材“N”。请把它加入目录，或改用目录里的名称。` |
| 菜谱的 `UNKNOWN_TAG(tag="T")` | `Unknown tag "T". Add it to the catalog's tags.` | `未知标签“T”。请把它加入目录里的标签。` |
| `SERVINGS_TOO_FEW(servings=0)` | `Servings must be a whole number of 1 or more, not 0.` | `份数必须是不小于 1 的整数，不能是 0。` |
| 设置的 `UNKNOWN_MEAL(meal="supper")` | `Unknown meal "supper". The meals are breakfast, lunch, and dinner.` | `未知餐次“supper”。可用的餐次：breakfast、lunch 和 dinner。` |

F03 设计 2.3 给出 `FILE_MISSING`、`FILE_IS_FOLDER` 和 `MISSING_BRACE`。F04 设计 3.1 给出列出时的消息，F04 设计 2.5 和 2.6 给出菜谱的其他消息。F05 设计 2.3 给出 `UNKNOWN_MEAL`。用到的位置是 `line 11`（`第 11 行`）、`ingredient 1` 和 `ingredient 3`（`食材 1` 和 `食材 3`）、`tags`（`标签`）、`servings`（`份数`）和 `meals`（`餐次`）。

用例分在下面这些文件里，使每个文件不超过 R06 的 500 行：

| 文件 | 用例 |
| --- | --- |
| `tests/test_f09_commands.py` | F09-T01 到 F09-T03 |
| `tests/test_f09_list.py` | F09-T04 到 F09-T08 |
| `tests/test_f09_list_widths.py` | F09-T09 到 F09-T11 |
| `tests/test_f09_show.py` | F09-T12 到 F09-T15 |
| `tests/test_f09_show_errors.py` | F09-T16 到 F09-T18 |
| `tests/test_f09_cli_and_reads.py` | F09-T19 和 F09-T20 |
| `tests/test_f09_integration.py` | F09-T21 到 F09-T26 |
| `tests/test_f09_random.py` | F09-T27 |
| `tests/test_f09_performance.py` | F09-T28 和 F09-T29 |
| `tests/f09_support.py` | 没有测试。有名字的改动、额外的菜谱、长名称，以及随机文件夹的辅助函数。它复用 `tests/f05_support.py` 和 `tests/f05_texts.py` 的 `make_home`、`copy_example`、`run_module` 和 `no_data_folder`，`tests/f07_support.py` 的 `call` 和 `snapshot`，`tests/f07_changes.py` 的 `make_init`、`edit` 和各个有名字的改动，`tests/f08_support.py` 的 `faults`，以及 `tests/f03_support.py` 的 `write`。 |
| `tests/f09_texts.py` | 没有测试。上面的预期文本和用例里的消息，写成字面量，每个文件都用 `Path` 构造。它复用 `tests/f08_texts.py` 的 `HELP` 和 `HELP_ZH`，以及 `tests/f05_texts.py` 的 `stopped`。 |
| `tests/pt01_support.py` | 没有测试。它新增通用的计时运行，以及 PT01 文件夹上 `list` 和 `show` 的预期输出（第 3 节）。它为 F07-T25 提供的函数保持原来的名字和行为。 |
| `tests/test_f04_example_recipes.py` | F04-T38 数 4 个中文步骤，不再是 3 个（A 点）。 |
| `tests/data/example/recipes/red-braised-pork.toml` | A 点的四个中文步骤。 |
| `tests/conftest.py` | 不变。F09 使用它的 fixture `example_folder` 和 `default_int_limit`，以及 pytest 的 `tmp_path` 和 `monkeypatch`。 |

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F09-T01 | 单元 | `LIST_COMMAND`、`LIST_COMMAND.run`、`main` | 2.1 的示例。`LIST_COMMAND` 的词是 `list`，两种语言的用法都是 `list`，帮助行是 F05 原型里的那一行，没有参数，选项是 `--tag`，并且是 `FolderUse.READ`。它的 `run` 用 `context.lang` 把列表写到 `context.out` 并给出 0，或者把错误的三行写到 `context.err` 并给出 1。它既不用 `context.settings`，也不用 `context.today`。帮助在 `check` 之后列出 `list` 和 `show ID`，第二列从第 18 列之后开始（2.1，选择 1）。 | 示例的各行，其中 `folder` 是 `example`，`home` 是 `home`。在 `help_lines` 里，对 `main` 的调用还传入 `commands=(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND)`，因为那 17 行只在 `COMMANDS` 里只有这四个命令时成立，F10 到 F13 会加入它们的命令。然后每次都用新的流：1. 用 `Context(Lang.EN, example, Settings(Lang.ZH, (Meal.BREAKFAST,), 5), out, err, date(2030, 1, 1))` 和 `Arguments()` 调用 `run`。2. 同样的上下文和 `Arguments((), (("--tag", "素"),))`。3. 在 `example` 里做麻婆错误，用示例的上下文和 `Arguments()` 调用 `run`。4. `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部内容。5. 通过 `call`，用真正的 `COMMANDS` 运行 `--help` 和 `--help --lang zh`。 | 示例的每条断言都成立。1. 0，out 为 `LIST`，err 为空。2. 0，out 为 `VEG`，err 为空。3. 1，out 为空，err 为 `STOP_ZH(recipes/mapo-tofu.toml，食材 3, 菜谱的 UNKNOWN_INGREDIENT(name="豆瓣酱"))`。4. `HELP` 和 `HELP_ZH`。5. 退出码 0，err 为空。在 out 里，以 `  check ` 开头的那一行的下一行以 `  list ` 开头、以 `List the recipes.` 或 `列出菜谱。` 结尾，再下一行以 `  show ID ` 开头、以 `Show one recipe.` 或 `查看一个菜谱。` 结尾。这两行的第二列都从以 `  --lang en\|zh` 开头的那一行的第二列所在的下标开始。无论 F10 到 F13 在 `show` 之后加入什么命令，这些规则都成立。 |
| F09-T02 | 单元 | `SHOW_COMMAND`、`SHOW_COMMAND.run` | 2.3 的示例。`SHOW_COMMAND` 的词是 `show`，两种语言的用法都是 `show ID`，帮助行是 F05 原型里的那一行，参数 `ID` 必填且不重复，选项是 `--servings`，并且是 `FolderUse.READ`。它的 `run` 用 `context.lang` 写出菜谱，用菜谱自己的份数，从不用 `context.settings` 的份数。对没有文件的 ID，它把 `UNKNOWN_ID` 写到 `context.err` 并给出 1，它在写任何东西之前抛出 `UsageError`（2.3）。 | 示例的各行，其中 `folder` 是 `example`。两行 `# raises` 各自用新的流在 `pytest.raises(UsageError)` 里运行。然后每次都用新的流和 `Context(Lang.ZH, example, Settings(Lang.EN, (Meal.BREAKFAST,), 5), out, err, date(2030, 1, 1))`：1. 用 `Arguments(("tomato-egg",))` 调用 `run`。2. 用 `Arguments(("tomato-egg",), (("--servings", "4"),))` 调用 `run`。3. 用 `Arguments(("mapo",))` 调用 `run`。 | 示例的每条断言都成立，每行 `# raises` 都抛出 `UsageError`，之后它的两个流都为空。1. 0，out 为 `TOMATO_ZH`，err 为空。2. 0，out 为 `FOUR_ZH`，err 为空。3. 1，out 为空，err 为 `MAPO_ZH` 加一个换行。 |
| F09-T03 | 单元 | `SHOW_COMMAND.run` | `--servings` 或 `ID` 的值不对时，`run` 在读任何文件、写任何输出之前抛出 `UsageError`，并且先检查 `--servings`。这个错误没有提示行，它保存你输入的文字原样，所以 5,000 位的值在 Python 默认的 4,300 位上限下也给出它的消息。正确的值通过检查（2.3，2.4 第 1 和 2 步，选择 7 到 9）。 | 使用 fixture `default_int_limit`。每次调用都用新的流和 `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`，在 `faults(tmp_path)` 里进行。输入 1 到 3 在 `pytest.raises(UsageError)` 里运行。1. 对 `Mapo`、`../rice`、`""`、`con`、`tomato\u2010egg`（U+2010 HYPHEN）、`Tomato-Egg`、`tomato egg`、`tomato_egg`、`-tomato`、`rice.`、`a:b`、`nul`、`lpt9`、`番茄炒蛋`、`tomato-egg\u200b`（U+200B ZERO WIDTH SPACE）和 `\uff54omato-egg`（U+FF54 FULLWIDTH LATIN SMALL LETTER T）中的每个 I，用 `Arguments((I,))`。2. 对 `0`、`101`、`04`、`+4`、`4.0`、` 4`、`4 `、`-1`、`1_0`、`\uff14`（FULLWIDTH DIGIT FOUR）、`\u0664`（ARABIC-INDIC DIGIT FOUR）、`\u00b2`（SUPERSCRIPT TWO）、`1000` 和 `"9" * 5000` 中的每个 V，用 `Arguments(("rice",), (("--servings", V),))`。3. `Arguments(("Mapo",), (("--servings", "0"),))`。4. 对 `1`、`9`、`10` 和 `100` 中的每个 V，用 `Arguments(("rice",), (("--servings", V),))`，以及 `Arguments(("9" * 5000,))`。 | 1. 每个错误的 `text(Lang.EN)` 是 `"I" is not a recipe ID. Run "recipe-menu list" to see the IDs.`，`text(Lang.ZH)` 是 `“I”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。`，`hint` 是 `None`，`values` 是 `(("id", I),)`。2. 每个错误的 `text(Lang.EN)` 是 `--servings must be a whole number from 1 to 100, not "V".`，`text(Lang.ZH)` 是 `--servings 必须是 1 到 100 之间的整数，不能是“V”。`，`hint` 是 `None`，`values` 是 `(("servings", V),)`。3. 输入 2 里 `0` 的错误。在 1 到 3 里，每次调用之后两个流都为空，故障工具的记录和列出记录都为空。4. 没有调用抛出异常。每次都给出 1，out 为空，err 为 `STOP(catalog.toml, FILE_MISSING)`，因为文件夹不存在。 |
| F09-T04 | 功能 | `recipe-menu list`、`main` | 2.2 的示例，按顺序，用真正的命令：原型的两个列表，用任一种语言、带空格和大写字母的 `--tag`，两种语言的未知标签，设置里的语言，没有菜谱带有的标签，没有标签的目录（`list` 在读菜谱之前报告它），`mapo-tofu` 里的错误，`list` 后面多一个词，以及没有菜谱文件的文件夹（2.2，选择 4 到 6）。 | 示例的各行，其中 `folder` 是 `example`，`home` 是 `home`，示例的 `run` 调用 `main` 时不传 `commands`。 | 示例的每条断言都成立。 |
| F09-T05 | 功能 | `recipe-menu list` | 在 `main` 上运行 v0.1-S09 和 v0.1-S10，以及 F09 原型“List the recipes”和“List the recipes with one tag”的完整输出。各行按 ID 的顺序排列，一行里的标签按菜谱里的顺序排列，两种语言里各列都按显示宽度对齐。`--tag` 按任一名称找到标签，与 `Catalog.find_tag` 的匹配方法相同：两端的空白不算，大小写只对字母 A 到 Z 不计（2.2，选择 4）。 | 在 `example` 里：1. `list`，然后 `list --lang zh`。2. `list --tag 快手`、`list --tag quick --lang zh` 和 `list --tag breakfast`。3. 对 `quick`、`QUICK`、`Quick`、` quick `、`\u00a0quick\u3000`（两边是 U+00A0 NO-BREAK SPACE 和 U+3000 IDEOGRAPHIC SPACE）、`快手 ` 和 `\t快手` 中的每个 T，运行 `list --tag T`。4. `list --tag quick\u200b`（末尾是 U+200B ZERO WIDTH SPACE），以及 `list --tag "home style"`。 | 1. `(0, out LIST)` 和 `(0, out LIST_ZH)`：v0.1-S09 期望的输出。2. `(0, out QUICK)`、`(0, out QUICK_ZH)` 和 `(1, err [BREAKFAST])`：v0.1-S10 期望的输出和退出码。3. 每个都给出 `(0, out QUICK)`。4. `(1, err ['Unknown tag "quick\u200b". The tags are quick, home-style, vegetarian, spicy, and staple.'])`，因为 U+200B 不是空白（F03 设计 2.6），把 `quick\u200b` 换成 `home style` 时也一样。 |
| F09-T06 | 功能 | `recipe-menu list` | 计数行。`RECIPE_COUNT` 和 `RECIPES_WITH_TAG` 在 1 个菜谱时用表示一个的形式，在 2 个或更多菜谱时用表示多个的形式，每段中文文字对任何个数都相同。`RECIPES_WITH_TAG` 的 `tag` 是输出语言里的标签名称，无论 `--tag` 给的是哪个名称（2.2）。 | 1. 在 `example` 里：`list --tag home-style`、`list --tag 家常 --lang zh`、`list --tag spicy`、`list --tag 辣` 和 `list --tag staple --lang zh`。2. 在 `tmp_path / "init"` 处的 init 文件夹里：`list` 和 `list --lang zh`。 | 1. 每一行都给出 `(0, out L)`。对 `home-style`，L 是 `LIST` 的第 1、3、4、5 和 7 行，一个空行，以及 `4 recipes have the tag "home-style".`。对 `家常`，L 是 `LIST_ZH` 的同样几行，一个空行，以及 `共 4 个菜谱带有标签“家常”。`。对 `spicy` 和 `辣`，L 是 `LIST` 的第 1 和 4 行，一个空行，以及 `1 recipe has the tag "spicy".`。对 `staple`，L 是 `LIST_ZH` 的第 1、6 和 8 行，一个空行，以及 `共 2 个菜谱带有标签“主食”。`。2. `(0, out INIT_LIST)` 和 `(0, out INIT_LIST_ZH)`。 |
| F09-T07 | 功能 | `recipe-menu list` | 未知标签。`UNKNOWN_TAG` 按目录里标签的个数选用表示一个或多个的形式，目录里没有标签时用 `NO_TAGS`。消息写出你输入的值原样，以及按目录顺序排列的目录标签，用输出的语言。`list` 把它写到错误流，输出流里什么都不写，并给出退出码 1。它在读完目录之后、读菜谱之前查找标签，所以菜谱文件或列出时的错误不改变结果，而目录的错误先出现（2.2 第 1 和 2 步，选择 4）。 | 使用 fixture `default_int_limit`。1. 在 `example` 里：`list --tag " Breakfast "`，以及 `list --tag X`，其中 X 是 `"9" * 5000`。2. 在做了麻婆错误和 Rice Bowl 的一份新的示例副本里：`list --tag breakfast` 和 `list --tag breakfast --lang zh`。3. 分别在一个标签、两个标签和没有标签的一份新的示例副本里：`list --tag breakfast`、`list --tag breakfast --lang zh` 和 `list`。4. 在没有目录的一份新的示例副本里：`list --tag breakfast`。 | 1. `(1, err ['Unknown tag " Breakfast ". The tags are quick, home-style, vegetarian, spicy, and staple.'])`，把 ` Breakfast ` 换成 X 时也一样。2. `(1, err [BREAKFAST])` 和 `(1, err [BREAKFAST_ZH])`。3. 一个标签：`(1, err ['Unknown tag "breakfast". The only tag is quick.'])`、`(1, err ["未知标签“breakfast”。现有标签：快手。"])` 和 `(1, err STOP(recipes/choy-sum.toml, tags, 菜谱的 UNKNOWN_TAG(tag="素")))`。两个标签：`(1, err ['Unknown tag "breakfast". The tags are quick and home-style.'])`、`(1, err ["未知标签“breakfast”。现有标签：快手和家常。"])`，以及与一个标签时相同的 `STOP`。没有标签：`(1, err ['Unknown tag "breakfast". The catalog has no tags.'])`、`(1, err ["未知标签“breakfast”。目录里没有标签。"])` 和 `(1, err STOP(recipes/choy-sum.toml, tags, 菜谱的 UNKNOWN_TAG(tag="快手")))`。4. `(1, err STOP(catalog.toml, FILE_MISSING))`。 |
| F09-T08 | 功能 | `recipe-menu list` | 一个菜谱都没有的列表是输出流上的一行，退出码 0，没有表格：不带 `--tag` 时是 `NO_RECIPES`，带它时是 `NO_RECIPE_WITH_TAG`，后者用输出的语言写出标签名称（选择 6）。 | 1. 在空的菜谱文件夹的一份新的示例副本里：`list`、`list --lang zh`、`list --tag quick` 和 `list --tag 快手 --lang zh`。2. 在不是菜谱的一份新的示例副本里：`list`。3. 在加了汤的一份新的示例副本里：`list --tag 汤` 和 `list --tag soup --lang zh`。4. 在删掉 `recipes/choy-sum.toml` 的一份新的示例副本里：`list --tag vegetarian` 和 `list --tag 素 --lang zh`。 | 1. `(0, out ["No recipes."])`、`(0, out ["没有菜谱。"])`、`(0, out ['No recipe has the tag "quick".'])` 和 `(0, out ["没有菜谱带有标签“快手”。"])`。2. `(0, out ["No recipes."])`，因为两个条目都不是菜谱文件。3. `(0, out ['No recipe has the tag "soup".'])` 和 `(0, out ["没有菜谱带有标签“汤”。"])`。4. `(0, out ['No recipe has the tag "vegetarian".'])` 和 `(0, out ["没有菜谱带有标签“素”。"])`。 |
| F09-T09 | 功能 | `recipe-menu list` | 选择 5。`list --tag` 的表格在两种语言里都保持整个列表的列宽，ID 列也一样。`min_widths` 的每个宽度是一格里各行中最大的 `display_width`，每格像 `format_table` 那样用 `str.splitlines` 拆成各行。所以两行的名称不会让整个列表变宽，无论它用的是哪种换行（2.2，选择 5，F02 设计 2.9）。 | 对 `\n`、`\r\n` 和 `\u2028` 中的每个 S，一份带 S 的长名称的新的示例副本。在其中：`list`、`list --tag staple`、`list --tag quick`、`list --lang zh`、`list --tag 主食 --lang zh` 和 `list --tag 快手 --lang zh`。 | 对每个 S，这六行依次对 `LONG`、`LONG_STAPLE`、`LONG_QUICK`、`LONG_ZH`、`LONG_STAPLE_ZH` 和 `LONG_QUICK_ZH` 中的每个 L 给出 `(0, out L)`，对每个 S 的文字都相同。所以 `a-long` 的名称占两行，没有输出含有 U+000D 或 U+2028。在每个表格里，包括只有一个菜谱的表格，Name 列从第 9 列之后开始，Servings 列在英文里从第 29 列之后开始，在中文里从第 24 列之后开始。如果宽度取自整个格子，或者取自只在 U+000A 处拆开的各行，Name 列就会变宽。 |
| F09-T10 | 功能 | `recipe-menu list` | 缺少一种语言，以及没有标签的菜谱。名称缺少输出语言时显示另一种语言，宽度按表格显示的名称计算。没有标签的菜谱最后一格为空，所以它那一行在份数之后结束。这些菜谱的警告不会写出，也不改变退出码（2.2，选择 3 和 5）。 | 在带额外菜谱的一份新的示例副本里：1. `list`。2. `list --lang zh`。3. `list --tag vegetarian`。 | 1. `(0, out EXTRA)`。2. `(0, out EXTRA_ZH)`。3. `(0, out L)`，其中 L 是 `EXTRA` 的第 1、3 和 8 行，一个空行，以及 `2 recipes have the tag "vegetarian".`。 |
| F09-T11 | 功能 | `recipe-menu list`、`recipe-menu check` | 错误让 `list` 停在第一个错误上，用输出的语言写出 `stop_at_error` 的三行，退出码 1，输出流里什么都没有。目录在前，然后是 `recipes/` 的列出，然后是按 ID 顺序的各个菜谱。`check` 用同样的读取函数读同样的文件，所以让 `list` 停下的错误在 `check` 的错误之中（2.2 第 1 和 3 步，选择 2）。 | 每个输入都在一份新的示例副本里，运行 `list`、`list --lang zh`、`check` 和 `check --lang zh`。1. 没有目录。2. 目录花括号错误。3. 没有菜谱文件夹。4. 菜谱是文件。5. Rice Bowl。6. 大写的 rice。7. 文件夹 x。8. 麻婆错误。9. 麻婆错误和米饭 0 份。10. 麻婆错误和 Rice Bowl。 | `list` 给出 `(1, err STOP(W, M))`，`list --lang zh` 给出 `(1, err STOP_ZH(W, M))`，W 和 M 是：1. `catalog.toml` 和 `FILE_MISSING`。2. `catalog.toml, line 11` 和 `MISSING_BRACE`。3. `recipes` 和 `FOLDER_MISSING`。4. `recipes` 和 `FOLDER_IS_FILE`。5. `recipes/Rice Bowl.toml` 和列出时的 `NOT_A_RECIPE_ID`。6. `recipes/rice.TOML` 和 `TOML_ENDING_NOT_SMALL`。7. `recipes/x.toml` 和 `FILE_IS_FOLDER`。8 和 9. `recipes/mapo-tofu.toml, ingredient 3` 和菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`，即第一个有错误的 ID。10. 输入 5 的 W 和 M，因为 `read_recipes` 先给出列出时的问题。在每个输入里，这个错误在两种语言的 `check` 的错误之中。 |
| F09-T12 | 功能 | `recipe-menu show`、`main` | 2.4 的示例，按顺序，用真正的命令：原型的输出，`--servings` 等于菜谱自己的份数，换算到 3 份，来自文件的 `red-braised-pork` 的步骤，没有中文名称、备注和步骤的菜谱，两种语言的未知 ID，五个错误的 ID，`--servings` 的十一个错误值，没有 ID 的一行，只让 `show mapo-tofu` 停下的 `mapo-tofu` 里的错误，以及让每个 `show` 都停下的不是 ID 的文件名（2.4，选择 3、7 和 8）。 | 示例的各行，其中 `folder` 是 `example`，`home` 是 `home`，示例的 `run` 调用 `main` 时不传 `commands`。使用 fixture `default_int_limit`。 | 示例的每条断言都成立。它的 `pork["steps"]["zh"]` 是 A 点的四个步骤。 |
| F09-T13 | 功能 | `recipe-menu show` | 在 `main` 上运行 v0.1-S12，以及 F09 原型里 `show` 的四节完整输出，每节也用另一种语言运行：名称行，份数行，缩进 2 的食材表格，带编号的步骤，另一种语言的步骤标题，以及 `UNKNOWN_ID`（2.4，选择 3 和 8）。 | 在 `example` 里：1. `show tomato-egg`、`show tomato-egg --servings 4 --lang zh`、`show red-braised-pork` 和 `show mapo`。2. `show tomato-egg --lang zh`、`show tomato-egg --servings 4`、`show red-braised-pork --lang zh` 和 `show mapo --lang zh`。 | 1. `(0, out TOMATO)`、`(0, out FOUR_ZH)`、`(0, out PORK)` 和 `(1, err [MAPO])`：v0.1-S12 期望的输出和退出码，`PORK` 里是 A 点的四个步骤。2. `(0, out TOMATO_ZH)`、`(0, out FOUR)`、`(0, out PORK_ZH)` 和 `(1, err [MAPO_ZH])`。 |
| F09-T14 | 功能 | `recipe-menu show` | 缺少一种语言或某个部分的菜谱。第一行写出菜谱有的每个名称，选定的语言在前，中间隔两个空格，两个名称是同一段文字时也是这样。没有标签的菜谱用 `SERVINGS_ONLY`。备注缺少选定的语言时显示另一种语言。没有食材的菜谱没有食材标题、没有表格，后面也没有空行。步骤缺少选定的语言时，用 `STEPS_IN_OTHER_LANGUAGE` 作标题，两种语言都一样。不写任何警告，退出码保持 0（2.4，选择 3）。 | 在带额外菜谱的一份新的示例副本里：1. `show boiled-egg` 和 `show boiled-egg --lang zh`。2. `show steamed-egg` 和 `show steamed-egg --lang zh`。3. `show water` 和 `show water --lang zh`。4. 两个名称是同一段文字的菜谱：用 `name = { zh = "Pizza", en = "Pizza" }`、`servings = 2`、`tags = []`、`ingredients = []`、`[steps]`、`zh = ["烤 12 分钟。"]` 和 `en = ["Bake for 12 minutes."]` 这几行写出 `recipes/pizza.toml`，然后运行 `show pizza` 和 `show pizza --lang zh`。 | 1. `(0, out BOILED)` 和 `(0, out BOILED_ZH)`。2. `(0, out STEAMED)` 和 `(0, out STEAMED_ZH)`。3. `(0, out WATER)` 和 `(0, out WATER_ZH)`。4. `(0, out ["Pizza  Pizza", "Servings: 2", "", "Steps", "  1. Bake for 12 minutes."])` 和 `(0, out ["Pizza  Pizza", "份数：2", "", "步骤", "  1. 烤 12 分钟。"])`。菜谱在每种语言里都有名称，所以第一行写出两个名称，尽管它们是同一段文字（第 5 节，第 1 轮）。 |
| F09-T15 | 功能 | `recipe-menu show` | 选择 8。`--servings` 用 `Quantity.scale` 把每个数量乘以 `Fraction(servings, recipe.servings)`，再用 `Quantity.to_text` 写出：用菜谱的单位，所以是 `1050 g` 而不是 `1.05 kg`，向上取整到最多两位小数，只有写出的数是 `1` 时才用单数，适量的数量仍是适量。份数行显示 `SCALED_SERVINGS`，没有标签的菜谱也一样，`--servings` 等于菜谱的份数时写出的行与不带这个选项时相同。步骤保持原样，食材表格按换算后的文字取宽度（2.4，选择 8，F01 设计 2.9 和 2.11）。 | 1. 在 `example` 里：对 `1`、`2`、`3`、`7` 和 `100` 中的每个 N 运行 `show tomato-egg --servings N`，然后 `show red-braised-pork --servings 4` 和 `show red-braised-pork --servings 4 --lang zh`。2. 在带额外菜谱的一份新的示例副本里：`show steamed-egg --servings 1`、`show steamed-egg --servings 2 --lang zh`、`show steamed-egg --servings 3`、`show boiled-egg --servings 100`、`show boiled-egg --servings 3 --lang zh` 和 `show water --servings 2 --lang zh`。3. 在米饭 3 份的一份新的示例副本里：`show rice --servings 1` 和 `show rice --servings 2`。 | 每一行都给出退出码 0、空的 err，以及 out 上的下列各行。1. 对 1：`TOMATO`，但第 2 行是 `Servings: 1 (the recipe makes 2)   Tags: quick, home-style`，第 5 到 10 行是 `  Tomato        150 g        cut into wedges`、`  Egg           1.5 pieces`、`  Scallion      0.5 stalks   chopped`、`  Salt          to taste`、`  Sugar         0.5 tsp` 和 `  Cooking oil   1 tbsp`。对 2：`TOMATO`。对 3：`TOMATO`，但第 2 行和第 5 到 10 行是设计 2.4 示例里的那些行。对 7：`TOMATO`，但第 2 行是 `Servings: 7 (the recipe makes 2)   Tags: quick, home-style`，第 5 到 10 行是 `  Tomato        1050 g        cut into wedges`、`  Egg           10.5 pieces`、`  Scallion      3.5 stalks    chopped`、`  Salt          to taste`、`  Sugar         3.5 tsp` 和 `  Cooking oil   7 tbsp`。对 100：`TOMATO`，但第 2 行是 `Servings: 100 (the recipe makes 2)   Tags: quick, home-style`，第 5 到 10 行是 `  Tomato        15000 g      cut into wedges`、`  Egg           150 pieces`、`  Scallion      50 stalks    chopped`、`  Salt          to taste`、`  Sugar         50 tsp` 和 `  Cooking oil   100 tbsp`。然后是 `PORK`，但第 2 行是 `Servings: 4 (the recipe makes 2)   Tags: home-style`，第 5 到 9 行是 `  Pork belly   2 jin      cut into 3 cm cubes`、`  Rock sugar   60 g`、`  Soy sauce    4 tbsp`、`  Ginger       6 slices` 和 `  Scallion     4 stalks`。然后是 `PORK_ZH`，但第 2 行是 `份数：4（菜谱按 2 份写）   标签：家常`，第 5 到 9 行是 `  五花肉   2 斤     切成 3 厘米见方的块`、`  冰糖     60 g`、`  生抽     4 汤匙`、`  姜       6 片` 和 `  葱       4 根`。2. `STEAMED`，但第 2 行是 `Servings: 1 (the recipe makes 3)   Tags: quick, vegetarian`，第 5 和 6 行是 `  Egg        0.67 pieces   打散` 和 `  Scallion   0.34 stalks   切葱花`。`STEAMED_ZH`，但第 2 行是 `份数：2（菜谱按 3 份写）   标签：快手、素`，第 5 和 6 行是 `  鸡蛋   1.34 个   打散` 和 `  葱     0.67 根   切葱花`。`STEAMED`。`BOILED`，但第 2 行是 `Servings: 100 (the recipe makes 1)`，第 5 行是 `  Egg    200 pieces   at room temperature`。设计 2.4 示例里 `boiled_zh` 的 9 行。`WATER_ZH`，但第 2 行是 `份数：2（菜谱按 1 份写）`。3. `RICE`，但第 2 行是 `Servings: 1 (the recipe makes 3)   Tags: staple`，第 5 行是 `  Rice   53.34 g`，然后是 `RICE`，但第 2 行是 `Servings: 2 (the recipe makes 3)   Tags: staple`，第 5 行是 `  Rice   106.67 g`。53.34 是 160 / 3 向上取整的结果，四舍五入会得到 53.33。 |
| F09-T16 | 功能 | `recipe-menu show` | 选择 7。不符合 `is_recipe_id` 的 `ID` 值给出 `NOT_A_RECIPE_ID`，退出码 2，错误流上一行，没有提示行，输出流里什么都没有。`show` 在读文件之前检查它，所以没有目录的文件夹给出相同的结果。符合规则但没有菜谱文件的 ID 给出 `UNKNOWN_ID`，退出码 1，在读完目录和列出之后，所以这两者的错误先出现。`show` 精确比较 ID，所以 Windows 和 Linux 给出相同的结果（2.4 第 2 到 5 步，选择 7）。 | 使用 fixture `default_int_limit`。1. 在 `example` 里：对 F09-T03 输入 1 的每个 I 运行 `show I`，然后 `show Mapo --lang zh`。2. 在 `example` 里：对 `mapo`、`com10`、`console`、`2-minute-noodles`、`a` 和 `"9" * 5000` 中的每个 I 运行 `show I`，然后 `show mapo --lang zh`。3. 在没有目录的一份新的示例副本里：`show Mapo`，然后 `show mapo`。4. 在没有菜谱文件夹的一份新的示例副本里：`show mapo`。5. 在 Rice Bowl 的一份新的示例副本里：`show mapo`。 | 1. 每个 I 都给出 `(2, err ['"I" is not a recipe ID. Run "recipe-menu list" to see the IDs.'])`，最后一行给出 `(2, err ["“Mapo”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。"])`。2. 每个 I 都给出 `(1, err ['No recipe has the ID "I". Run "recipe-menu search I" to find it.'])`，最后一行给出 `(1, err [MAPO_ZH])`。3. `(2, err ['"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.'])`，然后是 `(1, err STOP(catalog.toml, FILE_MISSING))`。4. `(1, err STOP(recipes, FOLDER_MISSING))`。5. `(1, err STOP(recipes/Rice Bowl.toml, 列出时的 NOT_A_RECIPE_ID))`。 |
| F09-T17 | 功能 | `recipe-menu show` | 选择 8。`--servings` 的值如果不是用 ASCII 数字写的、1 到 100 之间、没有前导 `0`、没有符号、没有其他字符的整数，就给出带你输入的值原样的 `SERVINGS_NOT_1_TO_100`，退出码 2，错误流上一行，没有提示行，输出流里什么都没有。`show` 在检查 `ID` 和读文件之前检查 `--servings`（2.4 第 1 步，选择 8）。 | 使用 fixture `default_int_limit`。1. 在 `example` 里：对 F09-T03 输入 2 的每个 V 运行 `show tomato-egg --servings V`。2. 在 `example` 里：`show tomato-egg --servings 0 --lang zh`。3. 在 `example` 里：`show Mapo --servings 0` 和 `show mapo --servings 101`。4. 在没有目录的一份新的示例副本里：`show tomato-egg --servings 04`。 | 1. 每个 V 都给出 `(2, err ['--servings must be a whole number from 1 to 100, not "V".'])`。2. `(2, err ["--servings 必须是 1 到 100 之间的整数，不能是“0”。"])`。3. 输入 1 里 `0` 的消息，然后是 `101` 的消息。4. 输入 1 里 `04` 的消息。 |
| F09-T18 | 功能 | `recipe-menu show`、`recipe-menu check` | 错误让 `show` 停在目录、`recipes/` 的列出或菜谱自己的文件的第一个错误上，写出 `stop_at_error` 的三行，退出码 1，输出流里什么都没有。列出时的错误即使指的是另一个文件也让 `show` 停下，`recipes/rice.TOML` 不留下 ID `rice`。另一个菜谱文件里的错误不让 `show` 停下，因为 `show` 不解析那个文件，菜谱的警告也不改变任何东西。让 `show` 停下的错误在 `check` 的错误之中（2.4 第 3 到 6 步，选择 2）。 | 每个输入都在一份新的示例副本里。1. 没有目录：`show tomato-egg` 和 `show tomato-egg --lang zh`。2. 目录花括号错误：`show rice --lang zh`。3. 菜谱是文件：`show rice`。4. Rice Bowl：`show tomato-egg`。5. 大写的 rice：`show rice` 和 `show tomato-egg --lang zh`。6. 文件夹 x：`show x`，然后 `show rice`。7. 麻婆错误和米饭 0 份：`show mapo-tofu`、`show mapo-tofu --lang zh`、`show rice`、`show tomato-egg --servings 4 --lang zh` 和 `show red-braised-pork`。然后在每个文件夹里运行 `check` 和 `check --lang zh`。 | 1. `(1, err STOP(catalog.toml, FILE_MISSING))` 和 `(1, err STOP_ZH(catalog.toml, FILE_MISSING))`。2. `(1, err STOP_ZH(catalog.toml，第 11 行, MISSING_BRACE))`。3. `(1, err STOP(recipes, FOLDER_IS_FILE))`。4. `(1, err STOP(recipes/Rice Bowl.toml, 列出时的 NOT_A_RECIPE_ID))`。5. `(1, err STOP(recipes/rice.TOML, TOML_ENDING_NOT_SMALL))`，而不是 `UNKNOWN_ID`，然后是 `(1, err STOP_ZH(recipes/rice.TOML, TOML_ENDING_NOT_SMALL))`。6. `(1, err STOP(recipes/x.toml, FILE_IS_FOLDER))`，然后是 `(0, out RICE)`。7. `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, 菜谱的 UNKNOWN_INGREDIENT(name="豆瓣酱")))`，用 `STOP_ZH` 和 `recipes/mapo-tofu.toml，食材 3` 的同样结果，`(1, err STOP(recipes/rice.toml, servings, SERVINGS_TOO_FEW(servings=0)))`，`(0, out FOUR_ZH)`，以及 `(0, out PORK)`。上面的每个错误都在它那种语言的 `check` 的错误之中。 |
| F09-T19 | 功能 | `recipe-menu list`、`recipe-menu show`、`main` | `cli` 在运行 `list` 或 `show` 之前报告命令行上的错误、缺少的数据文件夹和损坏的设置，对每个命令声明的选项和参数使用 F05 的消息和退出码。`list --help` 和 `show --help` 显示帮助，什么都不运行。同样的文件夹之后给出两个命令的输出（2.2 和 2.4 的错误，F05 设计 2.10）。 | 1. 在 `example` 里：`list extra`、`list extra --lang zh`、`list --tags x`、`list --tags x --lang zh`、`list --tag`、`list --tag --lang zh` 和 `list --tag a --tag b`。2. 在 `example` 里：`show`、`show --lang zh`、`show rice tomato-egg`、`show rice --tag quick`、`show rice --tag quick --lang zh`、`show rice --servings`、`show rice --servings ""`、`show rice --servings 2 --servings 3` 和 `show rice --servings --lang zh`。3. M 是 `tmp_path / "missing"`：在 M 里 `list`、在 M 里 `list --lang zh`、在 M 里 `show Mapo`，以及在 M 里 `show rice --servings 0`。4. 在损坏的设置的一份新的示例副本里：`list`、`show Mapo` 和 `show tomato-egg`。5. 在做了麻婆错误的一份新的示例副本里：`list --help`、`show mapo-tofu --help --lang zh` 和 `show Mapo --help`。6. 在 `example` 里：`list` 和 `show tomato-egg`。 | 1. `(2, err ['Unexpected argument "extra". Write "recipe-menu list".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["多余的参数“extra”。请写成“recipe-menu list”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['"list" has no option "--tags". Its own option is "--tag".', 'Run "recipe-menu --help" to see the options.'])`、`(2, err ["“list”没有选项“--tags”。它自己的选项是“--tag”。", "运行“recipe-menu --help”查看选项。"])`、`(2, err ["--tag needs a value."])`、`(2, err ["--tag 后面要写一个值。"])` 和 `(2, err ["--tag is given twice."])`。2. `(2, err ['An argument is missing. Write "recipe-menu show ID".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["缺少参数。请写成“recipe-menu show ID”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['Unexpected argument "tomato-egg". Write "recipe-menu show ID".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ['"show" has no option "--tag". Its own option is "--servings".', 'Run "recipe-menu --help" to see the options.'])`、`(2, err ["“show”没有选项“--tag”。它自己的选项是“--servings”。", "运行“recipe-menu --help”查看选项。"])`、两次 `(2, err ["--servings needs a value."])`、`(2, err ["--servings is given twice."])` 和 `(2, err ["--servings 后面要写一个值。"])`。3. `no_data_folder(M)`、`no_data_folder(M, ZH)`、`no_data_folder(M)` 和 `no_data_folder(M)`：`cli` 在 `run` 检查这些值之前检查数据文件夹。4. 每一行都给出 `(1, err STOP(settings.toml, meals, 设置的 UNKNOWN_MEAL(meal="supper")))`。5. 每一行都给出退出码 0、空的 err，out 与不指定文件夹的 `--help` 相同，第二行与 `--help --lang zh` 相同。6. `(0, out LIST)` 和 `(0, out TOMATO)`。 |
| F09-T20 | 功能 | `recipe-menu list`、`recipe-menu show`、`main` | 每个命令读哪些文件。`list` 把目录读一次，把 `recipes/` 列出一次，并按 ID 的顺序把每个菜谱文件读一次。遇到未知标签时，它不列出任何东西，也不读任何菜谱文件。`show` 读目录，把 `recipes/` 列出一次，只读它指名的那个菜谱。值不对时，它什么都不读。两者都不读常备清单或菜单，所以那里的错误不改变任何东西（2.2 和 2.4 的副作用，选择 2，架构第 8 节）。 | 第 1 到 7 行都在 `example` 里，各自在一个新的 `faults(example.root)` 里运行：1. `list`。2. `list --tag 快手 --lang zh`。3. `list --tag breakfast`。4. `show tomato-egg`。5. `show mapo`。6. `show Mapo`。7. `show rice --servings 0`。然后在 `example` 里做删逗号和错字，并用 `[[[\n` 写出 `menus/2026-W48.toml`。8. 不用故障工具：`list`、`list --tag quick --lang zh`、`show tomato-egg` 和 `show red-braised-pork --lang zh`。 | 记录、列出记录和结果：1. `read settings.toml`、`read catalog.toml`，以及按 `LIST` 的顺序对它的每个 ID 的 `read recipes/<ID>.toml`，列出记录 `recipes`，以及 `(0, out LIST)`。2. 同样的记录和列出记录，以及 `(0, out QUICK_ZH)`。3. `read settings.toml` 和 `read catalog.toml`，没有列出记录，以及 `(1, err [BREAKFAST])`。4. `read settings.toml`、`read catalog.toml` 和 `read recipes/tomato-egg.toml`，列出记录 `recipes`，以及 `(0, out TOMATO)`。5. `read settings.toml` 和 `read catalog.toml`，列出记录 `recipes`，以及 `(1, err [MAPO])`。6 和 7. 只有 `read settings.toml`，没有列出记录，以及带 `Mapo` 或 `0` 的消息的退出码 2。8. `(0, out LIST)`、`(0, out QUICK_ZH)`、`(0, out TOMATO)` 和 `(0, out PORK_ZH)`。 |
| F09-T21 | 集成 | `recipe-menu list`、`recipe-menu show`、`recipe-menu check`、`main` | 在 `main` 上、在 init 文件夹上运行 v0.1-S04。指名目录里没有的食材的菜谱，用 `check` 报告的错误让 `list` 和 `show` 停下。改正之后，两个命令都能列出和显示这个菜谱（2.2，2.4，选择 2）。 | `home / "recipe-menu"` 处的 init 文件夹，每一行都不指定文件夹。1. 按 F07-T20 输入 3 的写法，用 v0.1-S04 的菜谱写出 `recipes/cucumber-salad.toml`。然后 `list`、`show cucumber-salad` 和 `show tomato-egg`。2. 在目录的食材末尾加上 `  { zh = "黄瓜", en = "Cucumber", category = "produce" },`。然后 `list`、`show cucumber-salad` 和 `show cucumber-salad --lang zh`。 | 1. `list` 和 `show cucumber-salad` 都给出 `(1, err STOP(recipes/cucumber-salad.toml, ingredient 1, 菜谱的 UNKNOWN_INGREDIENT(name="黄瓜")))`，即 F07-T20 输入 3 的报告里的那个错误，`show tomato-egg` 给出 `(0, out TOMATO)`。2. `(0, out S04_LIST)`、`(0, out CUCUMBER)` 和 `(0, out CUCUMBER_ZH)`。所以 `list` 先列出 cucumber-salad，再列出 tomato-egg，以 `2 recipes.` 结尾，`show` 给出 Cucumber 2 pieces 和 Garlic 2 cloves，正如 v0.1-S04 所期望的。 |
| F09-T22 | 集成 | `recipe-menu list`、`recipe-menu show`、`main` | 在 `main` 上运行 v0.1-S08。带字节顺序标记和 CRLF 换行的数据文件给出相同的输出（2.2，2.4，F03 设计 2.3）。 | `home / "recipe-menu"` 处的一份新的示例副本。其中每个文件都重新写成 `b"\xef\xbb\xbf"` 加上它原来的字节，并把每个 `b"\n"` 换成 `b"\r\n"`。每一行都不指定文件夹：`show tomato-egg`、`list`、`list --tag 快手`、`show red-braised-pork --lang zh` 和 `show tomato-egg --servings 4 --lang zh`。 | `(0, out TOMATO)`，即 v0.1-S08 第 2 步期望的输出，然后是 `(0, out LIST)`、`(0, out QUICK)`、`(0, out PORK_ZH)` 和 `(0, out FOUR_ZH)`。 |
| F09-T23 | 集成 | `recipe-menu list`、`recipe-menu show`、`main` | 在 `main` 上运行 v0.1-S20。`list` 和 `show` 读取 `cli` 选出的数据文件夹：`--data`，其次 `RECIPE_MENU_DATA`，再次 `~/recipe-menu`。缺少数据文件夹时给出 F05 原型“No data folder yet”的两行（2.2 和 2.4 的参数，F05 设计 2.10）。 | B 是 `tmp_path / "One Drive" / "菜谱"` 处的一份新的示例副本，C 是 `tmp_path / "c"` 处的 init 文件夹。E 是 `{"RECIPE_MENU_DATA": str(C)}`。1. 在 B 里 `list`。2. 不指定文件夹、`environ` 为 E 的 `list`。3. 在 B 里、`environ` 为 E 的 `list`。4. 都不指定文件夹的 `list` 和 `list --lang zh`。5. `environ` 为 E 时：都不指定文件夹的 `show tomato-egg --servings 4 --lang zh` 和 `show rice`，以及在 B 里 `show rice`。 | 1. `(0, out LIST)`。2. `(0, out INIT_LIST)`，它只列出 tomato-egg，以 `1 recipe.` 结尾。3. `(0, out LIST)`。4. `no_data_folder(home / "recipe-menu")` 和 `no_data_folder(home / "recipe-menu", ZH)`，即带这个文件夹的 F05 原型的各行。5. `(0, out FOUR_ZH)`、`(1, err ['No recipe has the ID "rice". Run "recipe-menu search rice" to find it.'])` 和 `(0, out RICE)`。 |
| F09-T24 | 集成 | `recipe-menu list`、`recipe-menu show`、`main` | 在 `main` 上运行 v0.1-S21 和 v0.1-S22。不带 `--lang` 时，两个命令都用设置里的语言，`run` 抛出的用法错误也一样，`--lang en` 把一行切换成英文。没有 `language` 的设置给出英文。损坏的设置用 F05 原型“A broken settings file”的两行让两个命令停下（2.2，2.4，F05 设计 2.10）。 | `home / "recipe-menu"` 处的一份新的示例副本，每一行都不指定文件夹。1. 把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`。然后 `list --tag 素`、`list --tag 素 --lang en`、`show tomato-egg --servings 4`、`show mapo` 和 `show Mapo`。2. 删掉 `settings.toml` 里以 `language = ` 开头的那一行。然后 `list --tag 素` 和 `show tomato-egg`。3. 损坏的设置。然后 `list` 和 `show tomato-egg`。 | 1. `(0, out VEG_ZH)` 和 `(0, out VEG)`，即 v0.1-S21 第 1 和 2 步期望的输出，然后是 `(0, out FOUR_ZH)`、`(1, err [MAPO_ZH])` 和 `(2, err ["“Mapo”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。"])`。2. `(0, out VEG)`，即 v0.1-S21 第 3 步期望的输出，以及 `(0, out TOMATO)`。3. 每一行都给出 `(1, err STOP(settings.toml, meals, 设置的 UNKNOWN_MEAL(meal="supper")))`，它的前两行就是 F05 原型的那两行，正如 v0.1-S22 所期望的。 |
| F09-T25 | 集成 | `recipe-menu list`、`recipe-menu show`、`main` | 在 `main` 上为 `list` 和 `show` 运行 v0.1-S23。无论报告什么，两个命令都不写文件。`home` 和当前文件夹下的每个文件和文件夹都保持它的字节和修改时间，也不新增任何条目（2.2 和 2.4 的副作用）。 | `home / "recipe-menu"` 处的一份新的示例副本，带空的 `shopping/`，当前文件夹是用 `monkeypatch.chdir` 进入的空文件夹 `tmp_path / "cwd"`。在这些行之前和之后，用 `tests/f07_support.py` 的 `snapshot` 记录 `home` 和当前文件夹。这些行都不指定文件夹：`list`、`list --tag 快手`、`list --tag breakfast`、`show tomato-egg --servings 4`、`show mapo`、`show Mapo`、`show tomato-egg --servings 0`、`list extra` 和 `show --help`。然后做麻婆错误，记录新的快照，再运行 `list` 和 `show mapo-tofu`。 | 结果依次是：`(0, out LIST)`、`(0, out QUICK)`、`(1, err [BREAKFAST])`、`(0, out FOUR)`、`(1, err [MAPO])`、带 `Mapo` 的消息的退出码 2、带 `0` 的消息的退出码 2、带 `list extra` 的两行的退出码 2，以及带帮助的退出码 0。做了麻婆错误之后，两者都给出 `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, 菜谱的 UNKNOWN_INGREDIENT(name="豆瓣酱")))`。每次运行之后的快照都等于运行之前的快照。 |
| F09-T26 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令运行 `list` 和 `show`。无论 Python 给流设了什么编码，它都用 UTF-8 把输出写到 stdout，把退出码 1 或 2 的消息写到 stderr（2.2，2.4，F05 设计 2.9）。 | 像 F05-T48 那样使用 `tests/f05_support.py` 的 `run_module`，它把 `HOME` 和 `USERPROFILE` 设成 `tmp_path / "home"`，把 `PYTHONIOENCODING` 设成 `ascii`。用 `example`：1. `list --lang zh --data <example>`。2. `show tomato-egg --servings 4 --lang zh --data <example>`。3. `show mapo --lang zh --data <example>`。4. `show Mapo --data <example>`。5. 带 `data=example.root` 的 `list --tag 快手`，它设置 `RECIPE_MENU_DATA`。 | 1. 退出码 0，stdout 上是 `LIST_ZH` 的各行，stderr 为空。2. 退出码 0，stdout 上是 `FOUR_ZH` 的各行，stderr 为空。3. 退出码 1，stdout 为空，stderr 上是 `MAPO_ZH` 这一行。4. 退出码 2，stdout 为空，stderr 上是 `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.` 这一行。5. 退出码 0，stdout 上是 `QUICK` 的各行，stderr 为空。 |
| F09-T27 | 集成 | `recipe-menu list`、`recipe-menu show`、`main` | 随机文件夹。对 ID、一行或两行的名称、缺少的语言、份数、标签、数量、备注和步骤的任意组合，`list` 和 `show` 在两种语言里、带或不带 `--tag` 和 `--servings`，都给出 2.2 和 2.4 的规则给出的各行。随机组合会遇到其他用例没有列出的宽度、顺序和取整（2.2，2.4，选择 3、5 和 8）。 | `random.Random(20261113)` 构造 100 个文件夹，每个都是删掉七个菜谱文件的一份新的示例副本。每个文件夹有 1 到 6 个菜谱，ID 不重复地取自 `a`、`a-b`、`a0`、`ab`、`b-1`、`0`、`0-a`、`9`、`rice`、`tomato-egg`、`tomato-egg-noodles` 和 `z`。下面每个选择的机会都相同，除非另有说明。名称有英文文字、中文文字或两者都有。英文文字是取自 `Tomato`、`egg`、`stir-fry`、`A`、`long`、`pork` 和 `Mapo` 的 1 到 3 个词，用空格连接，中文文字是取自 番、茄、炒、蛋、红、烧、肉 和 面 的 1 到 5 个字。文字有 1/4 的机会带转义 `\n` 和同类的第二部分。份数是 1、2、3、4、7 或 100。标签是目录里 0 到 3 个不同的标签，顺序随机，各自用中文或英文名称写出。食材是目录里 0 到 4 种不同的食材，各自用中文或英文名称写出，数量是 `适量`、`to taste`、1 到 999 的整数加单位、0.1 到 99.9 之间带一位小数的数加单位，或者对有默认单位的食材，只写 1 到 999 的整数。单位是 `g`、`kg`、`斤`、`两`、`ml`、`L`、`tsp`、`汤匙`、`个`、`stalks`、`瓣`、`slice`、`块`、`bunch`、`罐` 和 `pack` 之一。每种食材没有备注、有英文备注、有中文备注或两者都有，每个备注是它那种语言的一个词。步骤是英文、中文或两者都有，每种语言 1 到 3 步。然后，每一行都用 `--lang` 随机选一种语言：1. `list`，或者对目录里的一个标签用它的某个名称运行 `list --tag T`，英文名称的大小写随机，有 1/2 的机会两端各带一个空格，或者 `list --tag breakfast`。2. 对文件夹里随机的一个 ID I 运行 `show I`，或有 1/6 的机会对 `zz` 运行，不带 `--servings`、`--servings` 等于菜谱的份数，或者是 1 到 100 之间的随机数。 | 每一行都给出退出码 0 和空的 err，只有 `list --tag breakfast` 给出 `(1, err [BREAKFAST])` 或 `(1, err [BREAKFAST_ZH])`，`show zz` 给出带 ID `zz` 的 `(1, err [UNKNOWN_ID])`。每一行的 out 等于测试按 2.2 和 2.4 的规则从它写出的菜谱构造的各行。这包括按 ID 的码位顺序排列的行，对每个菜谱计算的选择 5 的宽度，每个名称、备注和步骤的回退，另一种语言的步骤标题，名称按文件里的样子写出、中间隔两个空格的名称行，`SERVINGS_LINE`、`SERVINGS_ONLY` 和 `SCALED_SERVINGS`，以及每个数量：用食材的默认单位由 `parse_quantity` 读出，乘以 `Fraction(servings, recipe servings)`，再用 `to_text` 写出。测试用 F01 的 `parse_quantity`、`Quantity.scale` 和 `Quantity.to_text`，以及 F02 的 `format_table`、`display_width` 和 `comma_list` 构造这些行，不用 F09 的任何代码。需要知道某个数量是不是适量时，它用 `is_to_taste` 或 `==` 判断，从不用 `is`，因为 F01 只保证给出一个等于 `TO_TASTE` 的值（选择 8）。 |
| F09-T28 | 性能 | `recipe-menu list`、`python -m recipe_menu` | PT01 和 v0.1-S28：`list` 在 1 秒内打印 PT01 数据文件夹的全部 1,000 个菜谱，按从启动到退出的 5 次运行的中位数计（需求 7.1，2.2，选择 10）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"` 里。按第 3 节所说，先不计时运行一次，再计时运行 5 次 `python -m recipe_menu list --data <pt01>`。 | 每次运行都以 0 退出，在 stdout 上写出第 3 节 PT01 列表的 1,003 行，stderr 上什么都不写。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。 |
| F09-T29 | 性能 | `recipe-menu show`、`python -m recipe_menu` | PT01 和 v0.1-S29：`show` 在 1 秒内打印 PT01 数据文件夹的一个菜谱及其 12 种食材，按从启动到退出的 5 次运行的中位数计（需求 7.1，2.4，选择 10）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"` 里。按第 3 节所说，先不计时运行一次，再计时运行 5 次 `python -m recipe_menu show recipe-0500 --data <pt01>`。 | 每次运行都以 0 退出，在 stdout 上写出第 3 节 PT01 菜谱的 24 行，stderr 上什么都不写。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。 |

## 3. 性能用例

PT01 列出的命令里有 `list` 和 `show`（需求 7.1），所以它们各有一个用例，F09 的其他接口都没有（R14）。

| 编号 | 指标 | 机器 | 余量 | 基线 |
| --- | --- | --- | --- | --- |
| F09-T28 | PT01：在有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`recipe-menu list` 在 1 秒内完成。按从启动到退出的 5 次运行的中位数计。 | Troy 的电脑：Windows 11，使用 `recipe-menu` 环境的 Python 3.13。这个用例也在 CI 上、在 `.github/workflows/troy-mode.yml` 的 `ubuntu-24.04` 运行器上运行，那不是一台固定的机器（架构第 10 节）。 | Windows 上没有余量：中位数必须小于 1 秒，因为超出 PT01 的余量会放过达不到指标的命令（v0.1 测试方案第 3 节）。Linux 上是 3 秒，与 F07-T25 相同，使这个用例在速度未知的运行器上成立，同时仍能抓住慢了几倍的情况。 | 首次运行。架构师的模型在 Troy 的电脑上两轮的中位数是 0.806 秒和 0.803 秒，同时 `check` 是 0.835 秒和 0.843 秒（设计第 4 节）。模型不是实现，所以由 F09 的实现 PR 记录第一个基线。 |
| F09-T29 | PT01：用同一个数据文件夹，`recipe-menu show` 在 1 秒内完成。按从启动到退出的 5 次运行的中位数计。 | 与 F09-T28 相同。 | 与 F09-T28 相同。 | 首次运行。架构师的模型的中位数是 0.165 秒和 0.160 秒，同时 `--version` 是 0.147 秒和 0.144 秒（设计第 4 节）。由 F09 的实现 PR 记录第一个基线。 |

**哪个系统是 Troy 的电脑。** CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。所以每个用例都用 `tests/pt01_support.py` 的 `time_limit` 的上限：`sys.platform == "win32"` 时为 1 秒，否则为 3 秒，与 F07-T25 相同。在 Windows 上增加 CI 任务，会先改动这份方案。

**PT01 数据文件夹。** 由 `tests/pt01_support.py` 的 `make_pt01` 写出，与 F07-T25 相同，形状就是 v0.1 测试方案给出的那样（F07 测试方案第 3 节）。F09 不改动这个生成器。对 1 到 1,000 中的每个 k，菜谱 k 的名称是 `Recipe NNNN` 和 `菜谱NNNN`，份数是 `1 + k % 4`，标签是 quick、home-style、vegetarian、spicy 和 staple 中从 0 数起的第 `k % 5` 个和第 `(k + 1) % 5` 个，有 12 种带备注“cut into pieces”的食材，每种语言 6 个步骤。

**通用的计时运行。** `tests/pt01_support.py` 新增一个函数，它通过 `tests/f05_support.py` 的 `run_module` 用给定的参数启动 `python -m recipe_menu`，后面跟着 `--data` 和 PT01 文件夹。它用 `time.perf_counter()` 为整个调用计时，检查结果等于给定的 `(code, stdout, stderr)`，并给出时间。第二个函数做给定次数的这种运行，并给出它们的时间。`median_and_range` 和 `time_limit` 供每个命令使用。`check_run`、`timed_runs` 和 `check_after_mistakes` 保持原来的名字和行为，所以 F07-T25 不变，它们可以调用新函数。

**预期输出。** `tests/pt01_support.py` 按生成器的规则用 f-string 构造它们，不用 F02 的 `format_table`：

- PT01 列表：1,003 行。第 1 行是 `ID            Name          Servings   Tags`。对每个 k，第 k + 1 行是 ID `recipe-NNNN`、三个空格、名称 `Recipe NNNN`、三个空格、用空格补足到 8 列的份数、三个空格，以及用 `, ` 连接的两个标签的英文名称。然后是一个空行和 `1000 recipes.`。所以菜谱 1 和菜谱 1,000 的行是 `recipe-0001   Recipe 0001   2          home-style, vegetarian` 和 `recipe-1000   Recipe 1000   1          quick, home-style`。
- PT01 菜谱，即 `recipe-0500`：24 行。`Recipe 0500  菜谱0500`、`Servings: 1   Tags: quick, home-style`、一个空行、`Ingredients`、12 行食材、一个空行、`Steps`，以及对 1 到 6 中的每个 n 的 `  n. Step n: Wash and cut the ingredients, and stir-fry them for two minutes.` 这一行。每行食材是两个空格、`Ingredient NNN`、三个空格、用空格补足到 8 列的数量、三个空格和 `cut into pieces`。第一行是 `  Ingredient 001   1 tsp      cut into pieces`。对 0 到 10 中的每个 j，下一行是第 `2 + (11 * 500 + j) % 299` 种食材，即 120 到 130，`j % 4` 为 0、1、2 或 3 时数量分别是 `200 g`、`15 ml`、`2 pieces` 或 `to taste`。

**每个用例的步骤。**

1. 生成文件夹。
2. 不计时启动一次命令，像第 3 步那样检查它的结果。Windows 第一次读这 1,053 个新文件时很慢（F07 测试方案第 3 节），而 Troy 自己的数据文件夹不会每次运行都付出这个代价。
3. 用通用的计时运行把同一个命令启动 5 次，每次都是新进程：`sys.executable -m recipe_menu`，在 `tmp_path` 里运行，`HOME` 和 `USERPROFILE` 设成一个空的主文件夹，没有 `RECIPE_MENU_DATA`。每次运行都必须以 0 退出，stdout 正好是预期的输出，stderr 为空。不满足这些的运行会让用例失败，无论它用了多少时间。
4. 取 5 次时间的中位数，与这个系统的上限比较。
5. 用 `record_property` 记录 5 次时间、中位数和范围，使 JUnit 报告保存它们，供下次比较。

**它们怎样在 Troy 的电脑上运行。** 这两个用例在 `tests/` 里，所以每次在 Troy 的电脑上完整运行测试时都会运行，主会话为每个 PR 用 `recipe-menu` 环境的 Python 启动这样的运行。在 F09 的实现 PR 里，主会话还在没有其他测试运行、构建或安装进行时，用 `python -m pytest tests/test_f09_performance.py --junitxml=reports/pt01-f09.xml` 单独运行它们。PR 描述报告每个中位数和范围，那次运行就是基线。如果 `list` 接近上限，设计选择 10 给出第一步：在实现 PR 之前，用一个 `[refactor]` PR 让 `Message.render` 只解析每个模板一次。发布测试在同一台机器上运行 v0.1-S28 和 v0.1-S29。

**基准测试检查表。** 这两个用例这样回答 `benchmark-checklist` 的问题：

- 限制因素：设计选择 10 和第 4 节给出了它。`list` 读 `check` 读的文件，但不读常备清单和 52 个菜单，所以读 1,000 个菜谱文件限制它的速度，和 `check` 一样（F07 设计第 4 节）。它的表格另有大约 40,000 个字符，每个字符最多用 `display_width` 量三次。`show` 只读一个菜谱，所以 Python 的启动和导入限制它的速度：模型的 `show` 只比它的 `--version` 多用约 0.02 秒。这两个用例不做性能剖析，因为剖析会拖慢运行。`[refactor]` PR 会做剖析。
- 调优：每次运行都是一个新的 Python 进程，用已安装的包及其编译文件，没有覆盖率工具和调试器，与 Troy 的运行方式相同。第 2 步的不计时运行已经把文件读过一次。coverage.py 只测量测试进程，所以 CI 里的 `coverage run -m pytest` 不会拖慢计时的进程。
- 极限：`list` 通过管道写出大约 60 KB，1,053 个文件大约 2 MB，磁盘几毫秒就能读完。所以测得的时间是 Python 的工作。
- 错误：第 2 和 3 步检查每次运行的退出码、完整的 stdout 和空的 stderr。
- 可重复性：5 次计时运行，记录中位数和范围。与基线的差距小于基线各次运行的范围时，就不算可测量的变化。
- 相关性：每个用例为从启动到退出的整个命令计时，这正是 Troy 等待的时间。不带 `--tag` 的 `list` 是 `list` 工作最多的情况：`--tag` 读同样的文件，写出的行更少，模型的 `list --tag quick` 的中位数与 `list` 的相差不到 0.02 秒（设计第 4 节）。
- 工作确实发生了：`list` 的 1,000 行和计数行表明它读了每个菜谱，`recipe-0500` 的 12 行食材表明 `show` 读了那个菜谱。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 单独的 `LIST_COMMAND` 和 `SHOW_COMMAND` 字段，`recipe_menu.commands.browse` 的 `__all__` 列出的名称，以及作为 `browse/messages.py` 里常量的消息。 | mock 完整地声明了它们，所以只测它们的测试会在 mock 上通过（R09）。F09-T01 和 F09-T02 在一次运行旁边检查这些字段，各用例通过输出检查每段文字。文字放在哪里由代码审查检查。 |
| `browse` 只导入 `app`、`lang`、`units`、`text`、`datafile`、`catalog` 和 `recipes`。 | R07。CI 里的依赖检查器把每个导入与架构第 3 节的表格比较。 |
| 每个命令在读完最后一个文件之后一次写出它的输出，并且不保存状态。 | 没有接口能显示文字何时到达流。每个期望退出码 1 或 2 的用例都检查输出流为空，F09-T20 检查每个文件读了几次，F09-T01 和 F09-T02 把每个 `run` 运行了多次。其余由代码审查检查。 |
| 用超出 2.1 和 2.3 约束的 `Arguments` 调用 `run`：给 `list` 的值，给 `show` 的零个或两个值，命令没有声明的选项，或者为空或以 `--` 开头的值。 | `cli` 从不传入它们（F05 设计 2.10）。F09-T19 检查 `cli` 拒绝每一行这样的命令。 |
| `show` 输出里含有换行的备注或步骤。 | 设计按文件里的样子写出它们，没有给 `show` 规定它们的排版。选择 5 给出了 `list` 格子里换行的规则，F09-T09 测试它。 |
| 以 Windows 设备名命名的菜谱文件，比如 `recipes/con.toml`。 | Windows 拒绝创建它，F04-T12 只在 Linux 上检查 `RESERVED_RECIPE_ID`。F09-T11 和 F09-T18 用列出时的 `NOT_A_RECIPE_ID` 让命令停下，走的是同一条路径。 |
| 系统拒绝读取的列出或文件。 | 读取函数把这些错误变成问题，F04-T36 和 F07-T13 测试它们。F09-T11 和 F09-T18 检查每个读取函数的第一个错误让命令停下，无论是什么错误。 |
| `list` 或 `show` 运行期间的 Ctrl+C。 | `cli` 对每个命令都给出退出码 130（F05 设计 2.10），F05-T41 测试它。两个命令都不写文件，所以 Ctrl+C 不留下任何东西。 |
| `Message.render` 每次调用都解析它的占位符，以及选择 10 的 `[refactor]` PR。 | 这是 `text` 的内部改动，由架构师决定。F09-T28 为 `list` 计时，能显示这个改动。 |
| v0.1 的八个命令都在时的帮助。 | F05-T45 用替身命令检查那些行，v0.1-S19 用真正的命令检查它们。F09-T01 检查 `list` 和 `show` 的两行，所用的形式在 F10 到 F13 加入它们的命令之后仍然成立。 |
| Windows Terminal 里的中文输出。 | CI 机器没有 Windows 控制台（架构第 10 节），所以 v0.1-S25 让 Troy 检查。F09-T26 检查 `python -m recipe_menu` 用 UTF-8 写出中文输出。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的中文字符。 |
| 设计第 2 节为 F10 做的规划：`search` 共用 `browse` 的格子或宽度，以及 `UNKNOWN_ID` 的提示里的 `recipe-menu search`。 | 由 F10 的设计和测试方案覆盖。F09-T13 和 F09-T16 检查提示的文字。 |
| 发布测试里的 v0.1-S28 和 v0.1-S29。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 加入（TE5）。F09-T28 和 F09-T29 在每次测试运行中，在同一类文件夹上为同样的命令计时。 |

## 5. 与接口设计师的对齐记录

| 轮次 | 问题 | 回答 |
| --- | --- | --- |
| 1 | 两个名称是同一段文字的菜谱，比如 `name = { zh = "Pizza", en = "Pizza" }`。2.4 输出的第 1 步写出“the recipe's name in `context.lang`, then two spaces and its name in the other language, from `recipe.name.exact`”，只省略“a name that the recipe lacks”。选择 3 说“the line never repeats a name”。`show pizza` 写出哪一个第一行？方案 A：两种语言里都是 `Pizza  Pizza`。按第 1 步所说，写出菜谱有的每种语言，“never repeats a name”的意思是 `BiText.get` 的回退从不把一种语言显示两次。方案 B：`Pizza`。当 `recipe.name.exact` 对两种语言给出同一段文字时，这一行只写一次。测试经理推荐方案 A。它按第 1 步的写法执行，设计不需要修改，而且两个名称相同的情况很少，因为 Troy 用中文写中文名称。F09-T14 的输入 4 按回答确定。 | 选项 A，来自设计 1.0，行为不变。`show pizza` 在两种语言里的第一行都是 `Pizza  Pizza`。2.4 输出的第 1 步只在 `recipe.name.exact` 对某种语言给出 `None` 时，才省去这种语言的名称。对 `name = { zh = "Pizza", en = "Pizza" }`，它对两种语言都给出 `"Pizza"`，所以菜谱两个名称都不缺，设计里也没有任何地方比较这两段文字。选择 3 说：“`show` 的第一行写出菜谱有的每个名称，所选语言在前。所以没有英文名称的菜谱只显示它的中文名称，这一行也从不把一个名称写两遍。”这个“所以”让“从不把一个名称写两遍”来自“写出菜谱有的每个名称”：`BiText.get` 的回退从不把一种语言的名称第二次写到这一行上。F09 原型“Show one recipe”先给出所选语言的名称，再给出另一种语言的名称。这个输入是有效的数据：F04 设计 2.3 只要求有值的每种语言不只有空白字符，F03 设计 2.8 允许同一项的两个名称相互匹配。选项 B 需要比较两段文字，而设计没有描述这种比较。接口设计师确认了 F09-T14 输入 4 的两个预期输出。`tags = []` 用 `SERVINGS_ONLY`，对 `ingredients = []`，2.4 输出的第 4 步不写食材的行，`recipe.steps.exact` 在每种语言里都给出步骤，所以用 `STEPS_HEADING`。测试经理也在 Troy 的电脑上用第 2 节说的模型得到了这两个输出。接口设计师还记下了只供下一次设计修订使用的措辞：选择 3 的最后一句可以说明，两个名称是同一段文字时两个都写出。行为不变，所以 F09-T14 的输入 4 保持初稿的写法。 |

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-13 | 初稿。 |
| 0.2 | 2026-11-13 | 记录接口设计师对第 1 轮的回答，来自设计 1.0：选项 A，行为不变。两个名称是同一段文字的菜谱在第一行写出两个名称。F09-T14 在它测试的行为里写明这一点，输入 4 保持初稿的预期输出，接口设计师确认了这些输出。 |
| 1.0 | 2026-11-13 | Troy 批准。 |
