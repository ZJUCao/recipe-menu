---
troy-doc: "v0.1-test-plan"
lang: "zh-CN"
version: "0.2"
updated: "2026-11-15"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.1 版本测试方案

## 1. 版本

- 版本：v0.1
- 功能：F01、F02、F03、F04、F05、F06、F07、F08、F09、F10、F11、F12、F13
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

这些场景沿用[需求 3](../../requirements.zh-CN.md#3-用户如何使用)的四个主要流程和 `docs/prototypes/` 里的原型。Claude 把场景作为 `version-tests/` 里的版本测试来运行。发布测试在 Troy 的电脑上运行这些版本测试，从不在 CI 里运行。Claude 的每个场景都这样运行：

- 每个 `recipe-menu` 步骤都作为一个新进程运行：由运行测试的那个 Python 执行 `python -m recipe_menu`，带上该步骤的参数。进程的当前文件夹是一个空的临时文件夹。
- 进程通过 `USERPROFILE` 得到一个临时的主文件夹 `<home>`。除非步骤设置了 `RECIPE_MENU_DATA`，进程里没有这个环境变量。所以没有场景会读取或修改 `C:\Users\Troy\recipe-menu`。
- “示例文件夹”是 `tests/data/example/` 的一份新副本，放在 `<home>\recipe-menu`，带一个空的 `shopping\` 文件夹。`tests/data/example/` 存放 `docs/prototypes/example-data.md` 的数据。“init 文件夹”是 `recipe-menu init` 在 `<home>\recipe-menu` 创建的文件夹。每个场景步骤开头的“起始”写明它从哪个文件夹开始。
- 测试按 UTF-8 读取 stdout 和 stderr，把 CRLF 和 LF 当作同一种换行符。
- 原型的一节，比如 F09 的“List the recipes”，指该功能原型文件里的那一节，这里是 `docs/prototypes/F09-list-show.md`。原型各节的标题照英文原文引用。一节里某个命令的输出，是它那行 `PS>` 之后、下一行 `PS>` 之前的各行，去掉末尾的空行。步骤“打印某节的输出”，指它的输出与这些行逐字符相同，只是用 `<home>\recipe-menu` 代替 `C:\Users\Troy\recipe-menu`。一节里有几个命令时，各步骤按顺序对应它们的输出。
- 以退出码 1 或 2 结束命令的提示在 stderr 上，其他输出都在 stdout 上。`check` 的报告无论退出码是什么都在 stdout 上（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。
- `this` 和 `next` 取决于运行当天电脑上的日期。所以凡是要和原型比较输出的步骤，都写明 ISO 周，比如 `2026-W47`。

| 编号 | 场景 | 由谁运行 | 步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| v0.1-S01 | 创建英文数据文件夹，然后检查它。 | Claude | 起始：没有数据文件夹。1. 运行 `recipe-menu init`。2. 运行 `recipe-menu check`。 | 步骤 1 打印 F08“In English”一节的第一个输出，退出码为 0。它创建 `<home>\recipe-menu`，其中的 `settings.toml`、`catalog.toml`、`pantry.toml` 和 `recipes\tomato-egg.toml` 与 `example-data.md` 所示逐字节相同，为不带字节顺序标记的 UTF-8，换行符为 LF。它还创建空文件夹 `menus\` 和 `shopping\`。步骤 2 打印 F08“In English”一节的第二个输出，退出码为 0。 |
| v0.1-S02 | 创建中文数据文件夹。 | Claude | 起始：没有数据文件夹。1. 运行 `recipe-menu init --lang zh`。2. 不带 `--lang` 运行 `recipe-menu check`。 | 步骤 1 打印 F08“In Chinese”一节的输出，退出码为 0。文件与 v0.1-S01 的相同，只是 `settings.toml` 的 `language` 一行写的是 "zh" 而不是 "en"。步骤 2 用中文报告，以“已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。”开头。它报告没有错误、没有警告，退出码为 0。 |
| v0.1-S03 | `init` 拒绝已有文件的文件夹。 | Claude | 起始：`<home>\recipe-menu` 里只有文件 `notes.txt`。1. 运行 `recipe-menu init`。2. 运行 `recipe-menu init --data <other>`，其中 `<other>` 是一个还不存在的临时文件夹。 | 步骤 1 打印 `<home>\recipe-menu already holds files. init changed nothing.`，退出码为 1。文件夹里仍然只有 `notes.txt`，字节和修改时间都不变。步骤 2 打印 F08“In English”一节的第一个输出，用 `<other>` 代替数据文件夹，退出码为 0。之后 `<other>` 里有 v0.1-S01 的文件和文件夹。 |
| v0.1-S04 | 添加一个需要新食材的菜谱。 | Claude | 起始：init 文件夹。1. 添加 `recipes\cucumber-salad.toml`：名称为 拍黄瓜 和 Smashed cucumber，2 份，标签为 快手 和 素，食材为 黄瓜 `2 个` 和 大蒜 `2 瓣`，两种语言各一个步骤。2. 运行 `recipe-menu check`。3. 在目录的食材末尾加上 `{ zh = "黄瓜", en = "Cucumber", category = "produce" }`。4. 运行 `recipe-menu check`。5. 运行 `recipe-menu list`，再运行 `recipe-menu show cucumber-salad`。 | 步骤 2 报告 1 个错误，位置是 `recipes\cucumber-salad.toml, ingredient 1`，提示为 `Unknown ingredient "黄瓜". Add it to the catalog, or use its name in the catalog.`，退出码为 1。步骤 4 打印 `Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus.` 和 `No errors. No warnings.`，退出码为 0。在步骤 5 里，`list` 先列出 cucumber-salad，再列出 tomato-egg，最后一行是 `2 recipes.`。`show` 给出食材 Cucumber 2 pieces 和 Garlic 2 cloves。两个命令的退出码都是 0。 |
| v0.1-S05 | 改正 `check` 报告的错误。 | Claude | 起始：示例文件夹，带 F07 原型里的两处错误：`mapo-tofu` 的食材 3 写成了 豆瓣酱，`2026-W47` 的周一晚餐写成了 `tomato-eggs`。1. 运行 `recipe-menu check`。2. 运行 `recipe-menu check --lang zh`。3. 把 豆瓣酱 改回 郫县豆瓣酱，把 `tomato-eggs` 改回 `tomato-egg`。4. 运行 `recipe-menu check`。 | 步骤 1 打印 F07“Errors and a warning, in English”一节的输出，退出码为 1。步骤 2 打印 F07“The same check in Chinese”一节的输出，退出码为 1。步骤 4 打印 F07“After the fixes”一节的输出，退出码为 0。 |
| v0.1-S06 | 语法错误会写明行号。 | Claude | 起始：init 文件夹。1. 在 `pantry.toml` 的第 2 行，删掉 "盐" 和 "糖" 之间的逗号。2. 运行 `recipe-menu check`。 | 步骤 2 打印 F07“A syntax mistake”一节的输出，只是第一行为 `Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.`。退出码为 1。 |
| v0.1-S07 | 一次 `check` 列出所有问题。 | Claude | 起始：示例文件夹，带 9 处错误。在 `catalog.toml` 的食材末尾加两种食材：食材 23 为 `{ zh = "芥兰", en = "Broccoli", category = "produce" }`，食材 24 为 `{ zh = "香菜", en = "Coriander", category = "meats" }`。`pantry.toml` 的第 3 项为 "sesame oil"。`recipes\rice.toml` 的份数为 0，食材 1 的数量为 `1 cups`，标签为 `["breakfast"]`。`menus\2026-W47.toml` 的周写成 "2026-W48"，周五有 `supper = []`，周日晚餐第 1 道菜的份数为 0。1. 运行 `recipe-menu check`。 | 报告写着 `9 errors:`，列出 F07“Other problems that check reports”一节表格里的 9 个位置和提示，顺序不限，但有两处不同。重名在 `catalog.toml, ingredient 23`，提示为 `The English name "Broccoli" is also ingredient 3's name. Names must be unique.`。未知分类在 `catalog.toml, ingredient 24`。报告还列出 F07“After the fixes”一节里的警告。命令的退出码为 1。 |
| v0.1-S08 | 带字节顺序标记和 CRLF 换行符的数据文件读起来一样。 | Claude | 起始：示例文件夹，每个文件都重新保存为带字节顺序标记的 UTF-8，换行符为 CRLF。1. 运行 `recipe-menu check`。2. 运行 `recipe-menu show tomato-egg`。3. 运行 `recipe-menu menu show 2026-W47`。4. 运行 `recipe-menu shop 2026-W47`。 | 四个步骤依次打印 F07“After the fixes”一节的输出、F09“Show one recipe”一节的输出、F11“Show the week after you fill it”一节的第一个输出，以及 F13“In English”一节的输出。每个步骤的退出码都是 0。`shopping\2026-W47.md` 为不带字节顺序标记的 UTF-8，换行符为 LF。 |
| v0.1-S09 | 用两种语言列出菜谱。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu list`。2. 运行 `recipe-menu list --lang zh`。 | 步骤 1 和 2 打印 F09“List the recipes”一节的两个输出，退出码为 0。 |
| v0.1-S10 | 按一个标签列出菜谱，标签用哪种语言写都可以。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu list --tag 快手`。2. 运行 `recipe-menu list --tag quick --lang zh`。3. 运行 `recipe-menu list --tag breakfast`。 | 三个步骤打印 F09“List the recipes with one tag”一节的三个输出。步骤 1 和 2 的退出码为 0，步骤 3 的退出码为 1。 |
| v0.1-S11 | 用两种语言搜索菜谱。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu search 番茄`。2. 运行 `recipe-menu search TOMATO`。3. 运行 `recipe-menu search 葱 quick --lang zh`。4. 运行 `recipe-menu search lamb`。5. 运行 `recipe-menu search 豆腐 quick --lang zh`。 | 五个步骤依次打印 F10“One word”一节的两个输出、F10“Two words, in Chinese”一节的输出，以及 F10“No match”一节的两个输出。每个步骤的退出码都是 0。 |
| v0.1-S12 | 查看菜谱：换算份数，以及缺一种语言。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu show tomato-egg`。2. 运行 `recipe-menu show tomato-egg --servings 4 --lang zh`。3. 运行 `recipe-menu show red-braised-pork`。4. 运行 `recipe-menu show mapo`。 | 四个步骤打印 F09 里“Show one recipe”“Show one recipe for 4 servings, in Chinese”“A missing language”和“An unknown ID”各节的输出。步骤 1 到 3 的退出码为 0，步骤 4 的退出码为 1。 |
| v0.1-S13 | 排一周的菜单并查看。 | Claude | 起始：示例文件夹，`menus\` 为空。1. 运行 `recipe-menu menu new 2026-W47`。2. 运行 `recipe-menu menu new 2026-W47 --lang zh`。3. 像 Troy 填写菜单那样，用 `example-data.md` 里的 `menus\2026-W47.toml` 替换新文件。4. 运行 `recipe-menu check`。5. 运行 `recipe-menu menu show 2026-W47`。6. 运行 `recipe-menu menu show 2026-W47 --lang zh`。 | 步骤 1 打印 F11“Create next week's menu”一节的第一个输出，退出码为 0。它创建 `menus\2026-W47.toml`，与那一节所示的文件逐字节相同，为不带字节顺序标记的 UTF-8，换行符为 LF。步骤 2 打印那一节的第二个输出，退出码为 1，文件的字节和修改时间不变。步骤 4 打印 F07“After the fixes”一节的输出，退出码为 0。步骤 5 和 6 打印 F11“Show the week after you fill it”一节的两个输出，退出码为 0。 |
| v0.1-S14 | `this` 和 `next` 跟随电脑上的日期。 | Claude | 起始：示例文件夹，`menus\` 为空。`<T>` 是电脑当天日期所在的 ISO 周，`<N>` 是 7 天后那天所在的 ISO 周。1. 运行 `recipe-menu menu new`。2. 运行 `recipe-menu menu new next`。3. 运行 `recipe-menu menu show this`。4. 运行 `recipe-menu shop`。5. 运行 `recipe-menu shop next`。 | 步骤 1 创建 `menus\<T>.toml`，步骤 2 创建 `menus\<N>.toml`。每个文件的 `week` 一行写着它的周。步骤 3 以 `Menu for <T>,` 开头，每一餐都显示 `—`。步骤 4 打印 `The menu for <T> has no dishes, so there is nothing to buy. No file was saved.`，步骤 5 打印同样的提示，只是周为 `<N>`。每个步骤的退出码都是 0，`shopping\` 一直为空。 |
| v0.1-S15 | 没有菜单、周写错，以及菜单里有错误。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu menu show 2026-W48`。2. 运行 `recipe-menu menu show 2026-W99`。3. 运行 `recipe-menu shop 2026-W48`。4. 在 `menus\2026-W47.toml` 里，把周一晚餐的 `tomato-egg` 改成 `tomato-eggs`，然后运行 `recipe-menu menu show 2026-W47`。5. 运行 `recipe-menu shop 2026-W47`。 | 步骤 1 和 2 打印 F11“A week without a menu”一节的两个输出，退出码分别为 1 和 2。步骤 3 打印 F13“No menu, or an empty menu”一节的第一个输出，退出码为 1。步骤 4 打印 F11“A menu with a mistake”一节的输出，退出码为 1。步骤 5 打印与步骤 4 相同的各行，退出码为 1。`shopping\` 一直为空。 |
| v0.1-S16 | 设置决定有哪几餐和默认份数。 | Claude | 起始：init 文件夹，`settings.toml` 里写着 `meals = ["breakfast", "lunch", "dinner"]` 和 `servings = 3`。1. 运行 `recipe-menu menu new 2026-W48`。2. 在新文件里，把 `"tomato-egg"` 放进周一早餐。3. 运行 `recipe-menu menu show 2026-W48`。4. 运行 `recipe-menu shop 2026-W48`。 | 步骤 1 的第二行是 `7 days with breakfast, lunch, and dinner, all empty.`，文件里每天都按这个顺序有早餐、午餐和晚餐。步骤 3 有 Day、Breakfast、Lunch 和 Dinner 四列，在 Mon 23 Nov 的早餐显示 `Tomato and egg stir-fry ×3`，最后一行是 `1 meal, 1 dish. ×n: servings.`。步骤 4 以 `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish` 开头。它在 Vegetables and fruit 下列出 Tomato 450 g 和 Scallion 2 stalks，再在 Eggs, dairy, and tofu 下列出 Egg 5 pieces。它的常备行是 `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`。每个步骤的退出码都是 0。 |
| v0.1-S17 | 用英文和中文生成这一周的购物清单。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu shop 2026-W47`。2. 运行 `recipe-menu shop 2026-W47 --lang zh`。 | 步骤 1 打印 F13“In English”一节的输出，退出码为 0。它把同一份清单用英文保存为 `shopping\2026-W47.md`，这是一份 Markdown 勾选清单，每一项一行 `- [ ]`。步骤 2 打印 F13“In Chinese”一节的输出，退出码为 0。它用 F13“The saved file”一节的文字替换这个文件，逐字节相同，为不带字节顺序标记的 UTF-8，换行符为 LF。之后 `shopping\` 里只有这一个文件。 |
| v0.1-S18 | 不能相加的数量并列在同一行。 | Claude | 起始：示例文件夹，有三处改动。从 `pantry.toml` 里去掉 生抽。添加 `recipes\scallion-noodles.toml`：葱油拌面，Scallion oil noodles，2 份，标签为 快手 和 主食，食材为 面条 `200 g`、葱 `1 把` 和 生抽 `10 g`，两种语言各一个步骤。`menus\2026-W48.toml` 从周一到周五的晚餐依次是 red-braised-pork、tomato-egg、tomato-egg、tomato-egg-noodles 和 scallion-noodles，其他各餐都为空。1. 运行 `recipe-menu shop 2026-W48`。2. 运行 `recipe-menu shop 2026-W48 --lang zh`。 | 像 F13“Quantities that cannot be added”一节那样，步骤 1 有一行 Scallion，数量为 `5 stalks + 1 bunch`，还有一行 Soy sauce，数量为 `30 ml + 10 g`。步骤 2 有一行 葱，数量为 `5 根 + 1 把`，还有一行 生抽，数量为 `30 ml + 10 g`。两个步骤的退出码都是 0。 |
| v0.1-S19 | 帮助、版本和命令行错误。 | Claude | 起始：步骤 1 到 3 没有数据文件夹，步骤 4 和 5 用示例文件夹。1. 运行 `recipe-menu --help`。2. 运行 `recipe-menu --help --lang zh`。3. 运行 `recipe-menu --version`。4. 运行 `recipe-menu list --lang fr`。5. 运行 `recipe-menu cook`。 | 步骤 1 打印 F05“Help in English”一节的第一个输出，步骤 2 打印 F05“Help in Chinese”一节的输出，步骤 3 打印 `recipe-menu 0.1.0`。步骤 1 到 3 的退出码为 0。步骤 4 和 5 打印 F05“Mistakes on the command line”一节的两个输出，退出码为 2。 |
| v0.1-S20 | 选择数据文件夹。 | Claude | 起始：没有数据文件夹。`<B>` 是示例文件夹的一份副本，所在路径里有空格和汉字，比如 `<temp>\One Drive\菜谱`。`<C>` 是由 `recipe-menu init --data <C>` 创建的文件夹。1. 运行 `recipe-menu list --data <B>`。2. 把 `RECIPE_MENU_DATA` 设为 `<C>`，运行 `recipe-menu list`。3. 把 `RECIPE_MENU_DATA` 设为 `<C>`，运行 `recipe-menu list --data <B>`。4. 运行 `recipe-menu list`。5. 运行 `recipe-menu list --lang zh`。 | 步骤 1 和 3 打印 F09“List the recipes”一节的第一个输出。步骤 2 只列出 tomato-egg，最后一行是 `1 recipe.`。步骤 1 到 3 的退出码为 0。步骤 4 和 5 打印 F05“No data folder yet”一节的两个输出，退出码为 1。 |
| v0.1-S21 | 语言取自设置。 | Claude | 起始：示例文件夹，`settings.toml` 里写着 `language = "zh"`。1. 运行 `recipe-menu list --tag 素`。2. 运行 `recipe-menu list --tag 素 --lang en`。3. 删掉 `settings.toml` 里的 `language` 一行，然后运行 `recipe-menu list --tag 素`。 | 步骤 1 和 2 打印 F05“The language from the settings”一节的两个输出。步骤 3 打印与步骤 2 相同的输出。每个步骤的退出码都是 0。 |
| v0.1-S22 | 设置文件有错时命令停下。 | Claude | 起始：示例文件夹，`settings.toml` 里写着 `meals = ["lunch", "supper"]`。1. 运行 `recipe-menu list`。 | 提示以 F05“A broken settings file”一节的两行开头，命令的退出码为 1。 |
| v0.1-S23 | 你写的文件保持原样。 | Claude | 起始：示例文件夹。测试记下 `<home>` 和当前文件夹下每个文件和文件夹的字节和修改时间。1. 逐个运行这些命令：`recipe-menu check`、`recipe-menu list`、`recipe-menu list --tag 快手`、`recipe-menu search 番茄`、`recipe-menu show tomato-egg --servings 4`、`recipe-menu menu show 2026-W47`、`recipe-menu show mapo`、`recipe-menu menu show 2026-W48` 和 `recipe-menu --help`。2. 运行 `recipe-menu shop 2026-W47` 两次。 | 步骤 1 之后，每个文件和文件夹的字节和修改时间都不变，也没有新增文件或文件夹。步骤 2 之后，唯一新增或改变的文件是 `shopping\2026-W47.md`，`shopping\` 里没有别的文件。 |
| v0.1-S24 | 安装这个版本，在两种 shell 里从任何文件夹运行它。 | Troy | 在你的电脑上：1. 在一个能用 uv 的 PowerShell 里，比如激活了 `recipe-menu` 环境的 PowerShell，运行 `uv tool install --managed-python --python 3.13 --force "git+ssh://git@github.com/ZJUCao/recipe-menu.git@<commit>"`，其中的提交用发布测试给出的那个。然后运行 `uv tool update-shell`。2. 在 Windows Terminal 里打开一个新的 Windows PowerShell 5.1 标签页。运行 `cd $HOME`，再运行 `recipe-menu --version`。3. 在一个新的 PowerShell 7 标签页里再做一遍步骤 2。 | 两个标签页都打印 `recipe-menu 0.1.0`。 |
| v0.1-S25 | Windows Terminal 里正确显示中文。 | Troy | 在你的电脑上，使用 v0.1-S24 的两个标签页：1. 在第一个标签页里运行 `Copy-Item -Recurse D:\Troy\Projects\recipe-menu\tests\data\example $env:TEMP\recipe-menu-v0.1`，再运行 `New-Item -ItemType Directory -Force $env:TEMP\recipe-menu-v0.1\shopping`。2. 在每个标签页里运行 `$env:RECIPE_MENU_DATA = "$env:TEMP\recipe-menu-v0.1"`。然后运行 `recipe-menu list --lang zh`、`recipe-menu show tomato-egg --servings 4 --lang zh`、`recipe-menu menu show 2026-W47 --lang zh`、`recipe-menu shop 2026-W47 --lang zh` 和 `recipe-menu --help --lang zh`。3. 在每个标签页里运行 `chcp 437`，然后再运行一次 `recipe-menu list --lang zh`。 | 每个汉字都正常显示，没有问号、方框或乱码。每个表格的列都像 F05、F09、F11 和 F13 的原型那样对齐。运行 `chcp 437` 之后，`list` 的显示和之前一样。你没有修改任何 Windows 设置。 |
| v0.1-S26 | 在手机上勾选购物清单。 | Troy | 1. 在你的电脑上，像 v0.1-S25 的步骤 1 那样复制示例文件夹，但复制到你的同步工具会同步到手机的文件夹，比如 `D:\OneDrive\recipe-menu-v0.1`。2. 运行 `recipe-menu shop 2026-W47 --lang zh --data D:\OneDrive\recipe-menu-v0.1`。3. 在手机上，用你平时打开 Markdown 文件的应用，打开那个文件夹里的 `shopping/2026-W47.md`。4. 勾选两项。 | 手机显示 F13“The saved file”一节的清单：标题、六个分类、14 项和常备行，每个汉字都显示正确。每一项都是一个勾选框，你勾选的两项显示为已勾选。 |

**为什么有三个场景由 Troy 运行。** 凡是脚本能通过 `recipe-menu` 命令运行的场景，都由 Claude 运行。v0.1-S24 把工具安装进 Troy 自己的 uv 工具文件夹，并修改 Troy 的 PATH，测试不能这样做。只有新开的 PowerShell 标签页才能说明 PATH 生效了（[ADR-0006](../../adr/ADR-0006-install-with-uv-tool.zh-CN.md)）。v0.1-S25 需要 Troy 亲眼看。测试通过管道读取输出，看不到 Windows Terminal 里的字体和列（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。v0.1-S26 需要 Troy 的手机和 Troy 的同步工具。

**本方案不包括的内容。**

- Linux。CI 在 Linux 上运行每个 PR 的测试（[需求 7](../../requirements.zh-CN.md#7-非功能需求)）。Claude 的场景只在 Troy 电脑上的发布测试里运行，所以没有一个在 Linux 上运行。
- 网络。工具从不使用网络（[需求 7](../../requirements.zh-CN.md#7-非功能需求)）。架构禁止代码引入网络模块（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。版本测试无法证明一个进程从没用过网络，所以没有场景检查这一点。
- `menu suggest`、`add` 和 `edit`。它们属于 v0.2，即 F14、F15 和 F16。

**每个流程由哪些场景覆盖。**

| 需求里的流程或规则 | 场景 |
| --- | --- |
| 流程 1：开始 | v0.1-S01 到 v0.1-S08 |
| 流程 2：找菜谱 | v0.1-S09 到 v0.1-S12 |
| 流程 3：排一周的菜单 | v0.1-S13 到 v0.1-S16 |
| 流程 4：购物 | v0.1-S16 到 v0.1-S18，以及 v0.1-S26 |
| 购物清单的规则 | v0.1-S16 到 v0.1-S18 |
| 语言 | v0.1-S02、v0.1-S21、v0.1-S25，以及每个带 `--lang` 的步骤 |
| 数据文件夹 | v0.1-S01、v0.1-S20 和 v0.1-S26 |
| 错误和退出码 | v0.1-S05 到 v0.1-S07、v0.1-S15、v0.1-S19、v0.1-S20 和 v0.1-S22 |
| 你写的文件保持原样 | v0.1-S03、v0.1-S13、v0.1-S17 和 v0.1-S23 |
| 需求 7 里的安装和中文文字 | v0.1-S08、v0.1-S24 和 v0.1-S25 |
| 需求 7 里的规模，以及 PT01 | v0.1-S27 到 v0.1-S32 |

## 3. 性能和压力用例

PT01 是唯一的性能指标（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。它列出的每个命令各有一个用例，其他命令都没有（R14）。

| 编号 | 指标 | 负载 | 持续时间 | 机器 | 由谁运行 |
| --- | --- | --- | --- | --- | --- |
| v0.1-S27 | PT01：`recipe-menu check` 在 1 秒内结束。 | PT01 数据文件夹。`check` 读取其中每个文件。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |
| v0.1-S28 | PT01：`recipe-menu list` 在 1 秒内结束。 | PT01 数据文件夹。`list` 打印全部 1,000 个菜谱。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |
| v0.1-S29 | PT01：`recipe-menu show` 在 1 秒内结束。 | PT01 数据文件夹。`show` 打印一个菜谱及其 12 种食材。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |
| v0.1-S30 | PT01：`recipe-menu search` 在 1 秒内结束。 | PT01 数据文件夹。`search` 查找每个菜谱都用到的那种食材的名称，所以打印全部 1,000 个菜谱。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |
| v0.1-S31 | PT01：`recipe-menu menu show` 在 1 秒内结束。 | PT01 数据文件夹。`menu show` 打印一周的 63 道菜。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |
| v0.1-S32 | PT01：`recipe-menu shop` 在 1 秒内结束。 | PT01 数据文件夹。`shop` 生成并保存一周 63 道菜的清单，这些菜来自 63 个不同的菜谱。 | 运行 5 次，每次从启动到退出。取中位数。 | Troy 的电脑，Windows 11，在发布测试里 | Claude |

**PT01 数据文件夹。** 测试在开始计时之前，先在一个临时文件夹里生成它：

- `settings.toml`：英文，早餐、午餐和晚餐，2 份。
- `catalog.toml`：示例里的六个分类和五个标签，以及分布在各分类里的 300 种食材，每种都有中文名和英文名。
- `pantry.toml`：其中 10 种食材。
- `recipes\`：1,000 个菜谱。每个菜谱都有两种语言的名称和 6 个步骤、2 个标签，以及 12 种带两种语言备注的食材。数量用质量、体积和计数单位，也有“适量”。每个菜谱都用到同一种食材，`search` 查找的就是它的名称。
- `menus\`：52 个周菜单，从 `2026-W01` 到 `2026-W52`。每一餐有 3 道菜，所以一周有 63 道菜，来自 63 个不同的菜谱。`menu show` 和 `shop` 使用其中一周。

**用例何时通过。**

- 每次运行都是一个新进程：`python -m recipe_menu`，带上用例的参数，并用 `--data` 指定 PT01 数据文件夹。测试从启动到退出计时，不计生成文件夹的时间。
- 只有退出码为 0、并打印出这项工作应有结果的运行才算数。`check` 对 1,000 个菜谱和 52 个周菜单报告没有错误、没有警告。`list` 和 `search` 打印 1,000 个菜谱。`show` 打印 12 种食材。`menu show` 打印 63 道菜。`shop` 打印清单并保存文件。这样就能确认计时的工作确实做了，也说明工具能处理需求 7 要求的规模。
- 5 次运行的中位数低于 1 秒时，用例通过。指标在 1 秒之上不留余量，因为这样的余量会让没达到 PT01 的命令通过。v0.1 是第一个版本，所以没有更早的基线可以比较。
- 测试把每个用例 5 次运行的中位数和范围记在发布测试的 JUnit 报告里，以便以后的版本和它们比较。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，Windows Terminal 里的 Windows PowerShell 5.1 和 PowerShell 7 | Troy |
| Troy 的电脑 | Windows 11，`recipe-menu` 环境里的 Python 3.13，在发布测试里 | Claude |
| Troy 的手机 | 需求里没有写明。Troy 报告 v0.1-S26 时写明。 | Troy |

## 5. 验收记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-10 | 初稿。 |
| 0.2 | 2026-11-15 | v0.1-S16 要求的英文常备行按目录的写法写出名称，即 `Cooking oil, Salt, Sugar`，因为 Troy 在 F13 设计里选了这样的一行。 |
