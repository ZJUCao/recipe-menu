---
troy-doc: "v0.2-test-plan"
lang: "zh-CN"
version: "0.1"
updated: "2026-11-16"
status: "草稿。"
mirror-of: "test-plan.md"
---

# v0.2 版本测试方案

## 1. 版本

- 版本：v0.2
- 功能：F14、F15、F16
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#6-版本计划)

## 2. 端到端场景

这些场景沿用[需求 3](../../requirements.zh-CN.md#3-用户如何使用)里 v0.2 的流程：`menu suggest` 填满一周里的空餐，`add` 逐行询问一个新菜谱，`edit` 用你的编辑器打开一个菜谱，并在你关闭编辑器后检查它。它们也沿用[需求 4](../../requirements.zh-CN.md#4-功能点)里 F14、F15 和 F16 这三行，以及原型 `docs/prototypes/F14-suggest.md`、`docs/prototypes/F15-add.md` 和 `docs/prototypes/F16-edit.md`。

Claude 把场景作为 `version-tests/` 里的版本测试来运行。发布测试在 Troy 的电脑上运行这些版本测试，从不在 CI 里运行。[v0.1 测试方案第 2 节](../v0.1/test-plan.zh-CN.md#2-端到端场景)的这些规则对 Claude 的每个场景同样适用：

- 每个 `recipe-menu` 步骤都把项目环境里的 `recipe-menu` 命令作为一个新进程运行，当前文件夹是一个空的临时文件夹，主文件夹是一个临时的 `<home>`。没有场景会读取或修改 `C:\Users\Troy\recipe-menu`。
- “示例文件夹”是 `tests/data/example/` 的一份新副本，放在 `<home>\recipe-menu`，带一个空的 `shopping\` 文件夹。每个场景步骤开头的“起始”写明它从哪个文件夹开始。
- 测试按 UTF-8 读取 stdout 和 stderr，把 CRLF 和 LF 当作同一种换行符。
- 原型的一节，比如 F14 的“Fill an empty week”，以及其中某个命令的输出，含义与 v0.1 方案里相同。原型各节的标题照英文原文引用。步骤“打印某节的输出”，指它的输出与那些行逐字符相同，只是用 `<home>\recipe-menu` 代替 `C:\Users\Troy\recipe-menu`。
- 以退出码 1 或 2 结束命令的提示在 stderr 上，其他输出都在 stdout 上。

v0.2 增加这些规则：

- **推荐文件夹。** F14 原型假定有 40 个菜谱，其中 16 个带标签 快手。推荐文件夹是示例文件夹再加 33 个菜谱：13 个带标签 快手，2 个带标签 辣，18 个带标签 家常，每个只带一个标签。这样共有 16 个菜谱带 快手，3 个带 辣。每个新菜谱都是 2 份，名称和步骤都有两种语言，只用目录里的食材，所以 `check` 在其中找不到问题。设置与示例相同：午餐和晚餐，没有规定每餐菜数的设置。所以一周有 14 餐，每餐 1 道菜。
- **随机选择。** `menu suggest` 随机选菜谱。所以步骤检查的是每种选法都必须满足的条件：每餐的菜数、标签，以及同一周里没有菜谱出现两次。它不检查命令选了哪些菜谱。只有 v0.2-S02 比较两次选择。正确的随机选择把两周填成同样的 14 个菜谱、放在同样的餐里，概率是 16! 分之 2，约为 10^13 分之 1。
- **文件的其余部分。** 步骤说菜单文件的其余部分保持原样时，指 `menu suggest` 所填各餐的列表之外，每一行都保持原来的文字和位置，包括注释和空行。
- **回答 `add` 的问题。** 步骤在 stdin 上给出回答，每行一个，用 UTF-8，在最后一个回答之后关闭 stdin。空回答是一个空行。通过管道时，控制台不会回显回答。所以步骤检查 stdout 是否按该节所示的顺序显示该节的提问和提示，以及它的最后一行是否就是该节的最后一行。它们之间的空格和换行由 F15 的设计给出。
- **替身编辑器。** Claude 的场景都不打开记事本。`edit` 的步骤在 `settings.toml` 里指定一个替身编辑器，写法与 F16 原型指定 VS Code 的写法相同：`editor = "stand-in-editor --wait"`。测试把替身所在的文件夹放进进程的 PATH。在那里，这个名称指向批处理文件 `stand-in-editor.cmd`，就像在 VS Code 的安装里 `code` 指向 `code.cmd`。替身在 `<home>` 和当前文件夹之外记下它运行过，以及它收到的是哪个文件。它等 1 秒，对那个文件做该步骤的修改，然后退出。所以，如果 `edit` 在编辑器退出之前就检查菜谱，它检查的是旧文件，这个步骤就会失败。
- **`add` 和 `edit` 的报告。** 结束 `add` 或 `edit` 的那次检查的报告是它们的输出。所以无论退出码是什么，它都在 stdout 上，与 `check` 的报告一样（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。
- **原型没有给出输出时。** 预期结果写明输出必须包含什么，确切的文字由该功能的设计给出。Troy 批准的设计与本方案不同时，测试经理在版本测试 PR 之前更新本方案，使两者一致。

| 编号 | 场景 | 由谁运行 | 步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| v0.2-S01 | 用快手菜填满空的一周。 | Claude | 起始：推荐文件夹。1. 运行 `recipe-menu menu new 2026-W48`。2. 运行 `recipe-menu menu suggest 2026-W48 --tag quick`。3. 运行 `recipe-menu menu show 2026-W48`。4. 运行 `recipe-menu check`。 | 步骤 1 和 2 打印 F14“Fill an empty week”一节的两个输出，退出码为 0。步骤 2 之后，`menus\2026-W48.toml` 的 14 餐每餐有 1 道菜。每道菜都是带标签 快手 的菜谱，没有菜谱出现两次。文件的其余部分保持 `menu new` 写出的样子。步骤 3 每餐都显示一道菜，最后一行是 `14 meals, 14 dishes. ×n: servings.`。步骤 4 打印 F07“After the fixes”一节的输出，用 `40 recipes, and 2 week menus` 代替 `7 recipes, and 1 week menu`。步骤 3 和 4 的退出码为 0。 |
| v0.2-S02 | 选择是随机的，`--tag` 接受标签的任一种语言的名称。 | Claude | 起始：两个推荐文件夹 A 和 B，各在自己的主文件夹里。1. 在 A 里运行 `recipe-menu menu new 2026-W48`，再运行 `recipe-menu menu suggest 2026-W48 --tag quick`。2. 在 B 里运行同样的两个命令，用 `--tag 快手` 代替 `--tag quick`。 | 步骤 2 的 `menu suggest` 打印的输出与步骤 1 的相同：F14“Fill an empty week”一节的第二个输出。在两个文件夹里，每餐都有 1 个带标签 快手 的菜谱，没有菜谱出现两次。两个菜单文件至少有一餐不同。每个命令的退出码都是 0。 |
| v0.2-S03 | 换一道菜。 | Claude | 起始：做完 v0.2-S01 步骤 1 和 2 之后的推荐文件夹。1. 在 `menus\2026-W48.toml` 里，把周三晚餐的列表换成 `[]`。2. 运行 `recipe-menu menu suggest 2026-W48 --lang zh`。3. 运行 `recipe-menu menu suggest 2026-W48`。 | 步骤 2 打印 F14“Swap one dish”一节的输出，退出码为 0。之后周三晚餐有 1 道菜：一个这一周别的餐里都没有的菜谱。没有 `--tag` 时，它可以是 40 个菜谱里任何一个这样的菜谱。其他 13 餐保留它们的菜，文件的其余部分保持原样。步骤 3 时没有空餐。命令用 F14 设计里的文字说明这一点，退出码为 0。文件的字节和修改时间都不变。 |
| v0.2-S04 | 带这个标签的菜谱太少。 | Claude | 起始：推荐文件夹。1. 运行 `recipe-menu menu new 2026-W49`。2. 运行 `recipe-menu menu suggest 2026-W49 --tag spicy`。 | 步骤 2 打印 F14“Not enough recipes”一节的输出，退出码为 0。`menus\2026-W49.toml` 里恰好有 3 餐有菜：带标签 辣 的 3 个菜谱各一个。其他 11 餐保持空着，文件的其余部分保持 `menu new` 写出的样子。 |
| v0.2-S05 | 你填了一部分的一周保留你的菜，也不会有菜谱出现两次。 | Claude | 起始：示例文件夹。它的 `menus\2026-W47.toml` 在 4 餐里有 9 道菜，另有 10 个空餐。这一周用到 7 个菜谱里的 6 个，只有 `red-braised-pork` 没用到。1. 运行 `recipe-menu menu suggest 2026-W47`。2. 运行 `recipe-menu menu show 2026-W47`。 | 步骤 1 用 `red-braised-pork` 填上 1 个空餐，其他 9 个空餐保持空着。它用 F14 设计里的文字说明填了 10 个空餐里的 1 个、还有 9 餐空着，退出码为 0。你填好的 4 餐保留你写的菜，包括出现两次的 `choy-sum`、出现三次的 `rice` 和周日晚餐的份数。文件的其余部分保持原样。步骤 2 在步骤 1 填上的那一餐显示 `Red-braised pork belly ×2`，最后一行是 `5 meals, 10 dishes. ×n: servings.`，退出码为 0。 |
| v0.2-S06 | 设置规定每餐的菜数，推荐出的一周能生成购物清单。 | Claude | 起始：推荐文件夹，`settings.toml` 里写着 `meals = ["breakfast", "lunch", "dinner"]`，还有 F14 设计里让晚餐有 2 道菜的设置。早餐和午餐没有这样的设置。1. 运行 `recipe-menu menu new 2026-W48`。2. 运行 `recipe-menu menu suggest 2026-W48`。3. 运行 `recipe-menu menu show 2026-W48`。4. 运行 `recipe-menu check`。5. 运行 `recipe-menu shop 2026-W48`。 | 步骤 2 填满全部 21 餐：每顿早餐和每顿午餐 1 道菜，每顿晚餐 2 道菜，来自 28 个不同的菜谱。步骤 3 有 Day、Breakfast、Lunch 和 Dinner 四列，最后一行是 `21 meals, 28 dishes. ×n: servings.`。步骤 4 打印 F07“After the fixes”一节的输出，用 `40 recipes, and 2 week menus` 代替 `7 recipes, and 1 week menu`。步骤 5 以 `Shopping list for 2026-W48, 23 to 29 November 2026: 21 meals, 28 dishes` 开头，并保存 `shopping\2026-W48.md`。每个步骤的退出码都是 0。 |
| v0.2-S07 | `this` 和 `next` 跟随电脑上的日期。 | Claude | 起始：示例文件夹，`menus\` 为空。`<T>` 是电脑当天日期所在的 ISO 周，`<N>` 是 7 天后那天所在的 ISO 周。1. 运行 `recipe-menu menu new next`。2. 运行 `recipe-menu menu suggest next`。3. 运行 `recipe-menu menu suggest`。 | 步骤 2 填上 `menus\<N>.toml` 的 14 餐里的 7 餐，7 个菜谱各用一次。它说明还有 7 餐空着，退出码为 0。步骤 3 打印 F11“A week without a menu”一节的第一个输出，用 `<T>` 代替 `2026-W48`，退出码为 1。之后 `menus\` 里只有 `<N>.toml`。 |
| v0.2-S08 | 出错时 `menu suggest` 停下，不修改任何文件。 | Claude | 起始：示例文件夹。测试记下 `<home>` 下每个文件的字节和修改时间。1. 运行 `recipe-menu menu suggest 2026-W99`。2. 运行 `recipe-menu menu suggest 2026-W48`。3. 运行 `recipe-menu menu suggest 2026-W47 --tag breakfast`。4. 在 `menus\2026-W47.toml` 里，把周一晚餐的 `tomato-egg` 改成 `tomato-eggs`。然后运行 `recipe-menu menu suggest 2026-W47`。 | 步骤 1 打印 F11“A week without a menu”一节的第二个输出，退出码为 2。步骤 2 打印该节的第一个输出，退出码为 1。步骤 3 打印 F09“List the recipes with one tag”一节的第三个输出，退出码为 1。步骤 4 打印 F11“A menu with a mistake”一节的输出，退出码为 1。没有步骤添加文件。除了步骤 4 里的修改，每个文件的字节和修改时间都不变。 |
| v0.2-S09 | 用中文添加一个菜谱，其中有一个错误回答。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu add --lang zh`，给出 F15“In Chinese, with one wrong answer”一节里的回答：`garlic-broccoli`、`蒜蓉西兰花`、`Garlic broccoli`，份数用一个空行，`快手, 素`，从 `西兰花 300 g` 到 `盐 适量` 的五行食材（第三行是 `橄榄油 1 tbsp`），一个空行，三个中文步骤，一个空行，三个英文步骤，再一个空行。2. 运行 `recipe-menu show garlic-broccoli`。3. 运行 `recipe-menu show garlic-broccoli --lang zh`。4. 运行 `recipe-menu list`。5. 运行 `recipe-menu check`。 | 步骤 1 按顺序显示该节的提问和提示，最后一行是 `已保存 <home>\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。`。它的退出码为 0。它创建 `recipes\garlic-broccoli.toml`，为不带字节顺序标记的 UTF-8，换行符为 LF，不修改其他文件。步骤 2 以 `Garlic broccoli  蒜蓉西兰花` 和 `Servings: 2   Tags: quick, vegetarian` 两行开头。它依次列出食材 Broccoli 300 g、Garlic 4 cloves、Cooking oil 1 tbsp 和 Salt to taste，没有备注，然后按顺序列出三个英文步骤。步骤 3 按顺序显示三个中文步骤。步骤 4 把 `garlic-broccoli` 紧接着列在 `cola-wings` 之后，最后一行是 `8 recipes.`。步骤 5 打印 F07“After the fixes”一节的输出，用 `8 recipes` 代替 `7 recipes`。步骤 2 到 5 的退出码为 0。 |
| v0.2-S10 | 每个错误回答之后，`add` 都再问一次，用英文。 | Claude | 起始：示例文件夹。1. 运行 `recipe-menu add`，回答如下：`egg-fried-rice`、`蛋炒饭` 和 `Egg fried rice`。然后份数依次回答 `0`、`two` 和 `3`，标签依次回答 `breakfast` 和 `quick, staple`。然后食材依次是 `Rice 1 cups`、`Rice 300 g`、`Egg 3`、`Peanut 30 g`、`Scallion 1 stalk`、`Salt to taste` 和 `Cooking oil 2 tbsp`，再一个空行。然后两个中文步骤，一个空行，两个英文步骤，再一个空行。2. 运行 `recipe-menu show egg-fried-rice`。 | 在步骤 1 里，5 个错误回答各得到一条说明错在哪里的提示，文字由 F15 的设计给出：`0`、`two`、`breakfast`、`Rice 1 cups` 和 `Peanut 30 g`。在 `0` 和 `two` 之后，`add` 都再问份数。在 `breakfast` 之后它再问标签，在每个错误的食材之后它询问下一行食材。它保存 `recipes\egg-fried-rice.toml`，报告没有问题，退出码为 0。步骤 2 以 `Egg fried rice  蛋炒饭` 和 `Servings: 3   Tags: quick, staple` 开头。它依次列出 Rice 300 g、Egg 3 pieces、Scallion 1 stalk、Salt to taste 和 Cooking oil 2 tbsp，退出码为 0。 |
| v0.2-S11 | 已有的 ID，以及空的第一个回答。 | Claude | 起始：示例文件夹。测试记下 `<home>` 下每个文件的字节和修改时间。1. 运行 `recipe-menu add`，回答 `tomato-egg` 和一个空行。2. 运行 `recipe-menu add --lang zh`，回答一个空行。 | 步骤 1 按顺序显示 F15“An ID that exists”一节的提问、提示和再次提问。之后空回答结束 `add`。在步骤 2 里，空回答立即结束 `add`。每个步骤的退出码都是 0。每个文件的字节和修改时间都不变，也没有添加文件。 |
| v0.2-S12 | 一次留下错误的编辑，然后一次用中文、没有错误的编辑。 | Claude | 起始：示例文件夹，`settings.toml` 里写着 `editor = "stand-in-editor --wait"`。1. 运行 `recipe-menu edit mapo-tofu`。替身把食材 3 里的 郫县豆瓣酱 改成 豆瓣酱。2. 运行 `recipe-menu edit mapo-tofu --lang zh`。替身把 豆瓣酱 改回 郫县豆瓣酱。3. 运行 `recipe-menu check`。 | 在步骤 1 和 2 里，替身各运行一次，收到的是数据文件夹里的 `recipes\mapo-tofu.toml`。每个步骤的第一行说明 `edit` 已用设置里的编辑器打开 `recipes\mapo-tofu.toml`，文字由 F16 的设计给出。在这一行之后，步骤 1 打印 F16“An edit that leaves a mistake”一节输出里第一行之后的各行，退出码为 1。替身在退出前一刻才写入 豆瓣酱，所以这份报告说明 `edit` 等了编辑器。在第一行之后，步骤 2 打印 F16“A clean edit, in Chinese”一节输出里第一行之后的各行，退出码为 0。步骤 3 打印 F07“After the fixes”一节的输出，退出码为 0。 |
| v0.2-S13 | 未知的 ID、缺少的 ID，以及弄坏文件的一次编辑。 | Claude | 起始：示例文件夹，`settings.toml` 里像 v0.2-S12 那样指定替身编辑器。1. 运行 `recipe-menu edit mapo`。2. 运行 `recipe-menu edit`。3. 运行 `recipe-menu edit tomato-egg`。替身删掉第 3 行里 "快手" 和 "家常" 之间的逗号。 | 步骤 1 打印 F16“An unknown ID”一节的输出，退出码为 1。步骤 2 在 stderr 上打印一条用法提示，文字由 F16 的设计给出，退出码为 2。在步骤 1 和 2 里，替身没有运行，也没有文件被修改。在第一行之后，步骤 3 打印一个空行和 `Checked tomato-egg: 1 error.`。然后它打印位置 `recipes\tomato-egg.toml, line 3` 和提示 `The file cannot be read: a closing "]" is missing.`，缩进与 F16“An edit that leaves a mistake”一节相同。它以 `Run "recipe-menu edit tomato-egg" to fix it.` 结束，退出码为 1。 |
| v0.2-S14 | 帮助、版本，以及没有数据文件夹。 | Claude | 起始：没有数据文件夹。1. 运行 `recipe-menu --help`。2. 运行 `recipe-menu --help --lang zh`。3. 运行 `recipe-menu --version`。4. 运行 `recipe-menu menu suggest 2026-W48`。5. 运行 `recipe-menu add`。6. 运行 `recipe-menu edit tomato-egg`。 | 步骤 1 打印 F05“Help in English”一节的输出，并在 `Commands:` 下多出三行，`menu suggest`、`add` 和 `edit` 各一行。F14、F15 和 F16 的设计给出每一行及它在列表里的位置。步骤 2 打印 F05“Help in Chinese”一节的输出，并多出同样三行的中文。步骤 3 打印 `recipe-menu 0.2.0`。步骤 1 到 3 的退出码为 0。步骤 4 到 6 各打印 F05“No data folder yet”一节的第一个输出，退出码为 1。它们不创建文件夹。 |
| v0.2-S15 | 每个 v0.2 命令只修改它自己的文件。 | Claude | 起始：示例文件夹，`settings.toml` 里像 v0.2-S12 那样指定替身编辑器，还有 `recipe-menu menu new 2026-W48` 创建的空的 `menus\2026-W48.toml`。每个步骤之前，测试记下 `<home>` 下和当前文件夹下每个文件和文件夹的字节和修改时间。1. 运行 `recipe-menu menu suggest 2026-W48`。2. 运行 `recipe-menu add --lang zh`，给出 v0.2-S09 的那些回答。3. 运行 `recipe-menu edit tomato-egg`。替身不做修改就退出。 | 步骤 1 之后，`menus\2026-W48.toml` 是唯一字节或时间有变化的文件。步骤 2 之后，`recipes\garlic-broccoli.toml` 是唯一的新文件，其他文件都没有变化。步骤 3 之后，每个文件和文件夹的字节和修改时间都不变。没有步骤留下别的文件或文件夹，比如临时文件或备份。 |
| v0.2-S16 | `menu suggest`、`add` 和 `edit` 能处理 1,000 个菜谱。 | Claude | 起始：[v0.1 测试方案第 3 节](../v0.1/test-plan.zh-CN.md#3-性能和压力用例)的 PT01 数据文件夹，生成在 `<home>\recipe-menu`，设置里像 v0.2-S12 那样指定替身编辑器。1. 运行 `recipe-menu menu new 2026-W53`，再运行 `recipe-menu menu suggest 2026-W53`。2. 运行 `recipe-menu add`，给出一个菜谱 `size-check` 的回答：名称为 规模检查 和 Size check，默认份数，标签 `quick`，食材 `食材300 100 g` 和 `食材150 适量`，两种语言各一个步骤。3. 运行 `recipe-menu edit recipe-1000`。替身不做修改就退出。4. 运行 `recipe-menu check`。 | 步骤 1 用 21 个不同的菜谱填满 `menus\2026-W53.toml` 的全部 21 餐，每餐 1 道菜。步骤 2 保存 `recipes\size-check.toml`，报告没有问题。步骤 3 报告 `recipe-1000` 没有错误。步骤 4 打印 `Checked the settings, the catalog, the pantry, 1001 recipes, and 53 week menus.`、一个空行和 `No errors. No warnings.`。每个步骤的退出码都是 0。没有步骤计时，因为 v0.2 的命令都没有性能指标（第 3 节）。 |
| v0.2-S17 | 安装这个版本，在两种 shell 里从任何文件夹运行它。 | Troy | 在你的电脑上：1. 在一个能用 uv 的 PowerShell 里，比如激活了 `recipe-menu` 环境的 PowerShell，运行 `uv tool install --managed-python --python 3.13 --force "git+ssh://git@github.com/ZJUCao/recipe-menu.git@<commit>"`，其中的提交用发布测试给出的那个。然后运行 `uv tool update-shell`。2. 在 Windows Terminal 里打开一个新的 Windows PowerShell 5.1 标签页。运行 `cd $HOME`，再运行 `recipe-menu --version`。3. 在一个新的 PowerShell 7 标签页里再做一遍步骤 2。 | 两个标签页都打印 `recipe-menu 0.2.0`。 |
| v0.2-S18 | 在 Windows Terminal 里输入一个新菜谱。 | Troy | 在你的电脑上，使用 v0.2-S17 的两个标签页：1. 在第一个标签页里运行 `Copy-Item -Recurse D:\Troy\Projects\recipe-menu\tests\data\example $env:TEMP\recipe-menu-v0.2`。2. 在每个标签页里运行 `$env:RECIPE_MENU_DATA = "$env:TEMP\recipe-menu-v0.2"`。3. 在第一个标签页里运行 `recipe-menu add --lang zh`。用你的中文输入法输入 F15“In Chinese, with one wrong answer”一节里的回答。输入中文名时，先打一个错字，用 Backspace 删掉，再打对的字。然后运行 `recipe-menu show garlic-broccoli --lang zh`。4. 在第二个标签页里运行 `chcp 437`，再运行 `Remove-Item $env:RECIPE_MENU_DATA\recipes\garlic-broccoli.toml`。然后在这个标签页里再做一遍步骤 3。5. 在第二个标签页里运行 `recipe-menu add`。第一个问题回答 `test-cancel`，在第二个问题处按 Ctrl+C。然后运行 `Test-Path $env:RECIPE_MENU_DATA\recipes\test-cancel.toml`。 | 在两个标签页里，`add` 的样子都与 F15“In Chinese, with one wrong answer”一节所示相同。提问、提示和你的回答里的每个汉字都正常显示，没有问号、方框或乱码。在 橄榄油 之后，`add` 询问另一种食材。`show` 给出的名称 蒜蓉西兰花 里没有那个错字，四种食材和三个中文步骤也都与你输入的相同。在步骤 5 里，`add` 立即结束，没有报错文字，`Test-Path` 打印 `False`。 |
| v0.2-S19 | 用记事本编辑一个菜谱。 | Troy | 在你的电脑上，使用 v0.2-S18 的第一个标签页。它的数据文件夹没有指定编辑器，所以 `edit` 用记事本。1. 关闭所有记事本窗口。运行 `recipe-menu edit mapo-tofu`。在记事本里把食材 3 的 郫县豆瓣酱 改成 豆瓣酱，保存，然后关闭记事本。再运行 `$LASTEXITCODE`。2. 运行 `recipe-menu edit mapo-tofu --lang zh`。把 豆瓣酱 改回 郫县豆瓣酱，保存，然后关闭记事本。3. 在记事本里打开一个你自己的文本文件，让它的窗口开着。运行 `recipe-menu edit tomato-egg`。等 10 秒。然后不做修改，关闭记事本里这个菜谱的标签页或窗口。 | 步骤 1 显示 F16“An edit that leaves a mistake”一节的内容，`$LASTEXITCODE` 打印 `1`。步骤 2 显示 F16“A clean edit, in Chinese”一节的内容，每个汉字都正确。在每个步骤里，你关闭菜谱之前，`edit` 只显示它的第一行，之后才显示检查结果。在步骤 3 里，你自己的文件开在另一个记事本窗口里时也是这样。然后 `edit` 报告 tomato-egg 没有错误。 |

**为什么有三个场景由 Troy 运行。** 凡是脚本能通过 `recipe-menu` 命令运行的场景，都由 Claude 运行。v0.2-S17 把工具安装进 Troy 自己的 uv 工具文件夹，并修改 Troy 的 PATH，测试不能这样做。只有新开的 PowerShell 标签页才能说明 PATH 生效了（[ADR-0006](../../adr/ADR-0006-install-with-uv-tool.zh-CN.md)）。v0.2-S18 需要 Troy 的键盘和中文输入法。Claude 的 `add` 场景通过管道给出回答，所以它们从不在控制台里打字，从不用输入法，也不能在提问处按 Ctrl+C。v0.2-S19 需要记事本，这个窗口只能由人来关闭。Windows 11 的记事本可能把文件作为一个已经打开的窗口里的标签页打开，所以步骤 3 检查 `edit` 是否仍然会等。

**本方案不包括的内容。**

- Linux。CI 在 Linux 上运行每个 PR 的测试（[需求 7](../../requirements.zh-CN.md#7-非功能需求)）。Claude 的场景只在 Troy 电脑上的发布测试里运行，所以没有一个在 Linux 上运行。
- 网络。和 v0.1 一样，版本测试无法证明一个进程从没用过网络，所以没有场景检查这一点。
- VS Code。F16 原型以 `editor = "code --wait"` 为例。v0.2-S12、v0.2-S13、v0.2-S15 和 v0.2-S16 的替身编辑器用同样的方式指定，而且和 `code` 一样是一个批处理文件。需求没有说 Troy 的电脑上装有 VS Code，所以没有场景需要它。

**本方案在等设计的地方。** F14、F15 和 F16 都还没有设计。场景里的下面这些点来自设计。如果 Troy 批准的设计用别的方式定下它们，本方案会随之修改：

- F14：规定每餐菜数的设置（v0.2-S06）。不带 `--tag`、填完后仍有空餐时的文字（v0.2-S05 和 v0.2-S07），以及一周没有空餐时的文字（v0.2-S03）。本方案预期这两种情况的退出码都是 0，因为两者都不是数据里的错误。对于错误的周、缺少的菜单和未知的标签，本方案预期的提示和退出码与 `menu show` 和 `list --tag` 的相同（v0.2-S07 和 v0.2-S08）。需求只禁止同一个菜谱在一周里出现两次，所以在 v0.2-S03 里，你清空的那道菜可能又被选回来。只剩 1 个菜谱时一顿要 2 道菜的餐怎么填，以及文件里漏写的一餐怎么处理，由 F14 的设计和它的测试方案决定。
- F15：英文的提问、保存后的英文那一行，以及错误回答的提示（v0.2-S10）。空的第一个回答之后的退出码，本方案预期为 0（v0.2-S11）。`add` 怎样把 `Cooking oil 2 tbsp` 和 `Salt to taste` 分成名称和数量，因为两者都含有空格（v0.2-S10）。`add` 按 UTF-8 读取管道，就像重定向的输出是 UTF-8 一样（[ADR-0004](../../adr/ADR-0004-bilingual-text.zh-CN.md)）。
- F16：设置指定了编辑器时的第一行（v0.2-S12），没有 ID 时的用法提示（v0.2-S13），以及 `editor` 的值怎样分成程序和它的参数。还有，记事本把菜谱作为已经打开的窗口里的标签页打开时，`edit` 怎样等待（v0.2-S19）。

**v0.2 改变的 v0.1 场景。**

- v0.1-S19 的步骤 1 到 3 预期 v0.1 的帮助和 `recipe-menu 0.1.0`。在 v0.2 里，帮助还列出 `menu suggest`、`add` 和 `edit`，正如 F05 原型所说，版本也变成 0.2.0。所以，除非 v0.1-S19 的测试把这几步交给 v0.2-S14，它会在 v0.2 的发布测试里失败。v0.1 方案和这个测试需要在 v0.2 的发布测试之前做相应的修改。
- 如果某个 v0.2 设计改变了 `init` 或 `menu new` 写出的文件，比如在 `settings.toml` 里加一个新键，v0.1-S01、v0.1-S02 和 v0.1-S13 也随之改变。
- v0.1 的 PT01 用例在 v0.2 里再运行一次（第 3 节）。

**每个流程由哪些场景覆盖。**

| 需求里的流程、规则或原型 | 场景 |
| --- | --- |
| `menu suggest` 填满一周里的空餐 | v0.2-S01 到 v0.2-S08，以及 v0.2-S15 |
| 设置规定每餐的菜数，以及推荐出的一周的购物清单 | v0.2-S06 |
| `add` 逐行询问一个新菜谱 | v0.2-S09 到 v0.2-S11，以及 v0.2-S18 |
| `edit` 用你的编辑器打开一个菜谱，并在你关闭编辑器后检查它 | v0.2-S12、v0.2-S13 和 v0.2-S19 |
| F14 原型：“Fill an empty week”、“Swap one dish”和“Not enough recipes” | v0.2-S01 到 v0.2-S04 |
| F15 原型：“In Chinese, with one wrong answer”和“An ID that exists” | v0.2-S09、v0.2-S11 和 v0.2-S18 |
| F16 原型：“An edit that leaves a mistake”、“A clean edit, in Chinese”和“An unknown ID” | v0.2-S12、v0.2-S13 和 v0.2-S19 |
| 语言 | v0.2-S02、v0.2-S03、v0.2-S09、v0.2-S12、v0.2-S14、v0.2-S18 和 v0.2-S19 |
| 数据文件夹 | v0.2-S14 |
| 错误和退出码 | v0.2-S08、v0.2-S10、v0.2-S11、v0.2-S13 和 v0.2-S14 |
| 你写的文件保持原样 | v0.2-S03、v0.2-S05、v0.2-S08、v0.2-S11 和 v0.2-S15 |
| 需求 7 里的规模 | v0.2-S16 |
| 需求 7 里的安装和中文文字 | v0.2-S17 到 v0.2-S19 |
| PT01 | 第 3 节 |

## 3. 性能和压力用例

无。PT01 是唯一的性能指标（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。它列出 `check`、`list`、`show`、`search`、`menu show` 和 `shop`，这些都不是 v0.2 新加的。所以 `menu suggest`、`add` 和 `edit` 没有性能用例（R14）。v0.2-S16 在 PT01 数据文件夹上运行它们，不计时，以检查需求 7 要求的规模。

**PT01 在 v0.2 里仍然成立。** v0.1 的六个 PT01 用例 v0.1-S27 到 v0.1-S32 留在 `version-tests/` 里，在 v0.2 的发布测试里再运行一次。它们的规则不变：5 次运行的中位数低于 1 秒时，用例通过。v0.2 修改了它们计时的代码。F14 和 F16 在每个命令都读取的设置里加键。F14 在每个命令都拿到的上下文里加一个随机数生成器，F15 加一个输入流。F15 和 F16 复用 `check`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [5](../../architecture.zh-CN.md#5-数据模型)）。

基线是 2026-11-16 在 Troy 的电脑上进行的 v0.1.0 发布测试，以它的 JUnit 报告记下的数字为准：

| 用例 | 命令 | 中位数 | 5 次运行的范围 |
| --- | --- | --- | --- |
| v0.1-S27 | `check` | 0.841 秒 | 0.832 到 3.080 秒 |
| v0.1-S28 | `list` | 0.782 秒 | 0.777 到 0.789 秒 |
| v0.1-S29 | `show` | 0.164 秒 | 0.161 到 0.174 秒 |
| v0.1-S30 | `search` | 0.779 秒 | 0.772 到 0.789 秒 |
| v0.1-S31 | `menu show` | 0.201 秒 | 0.199 到 0.202 秒 |
| v0.1-S32 | `shop` | 0.215 秒 | 0.213 到 0.219 秒 |

`check` 用掉了它那 1 秒的 84%，`list` 和 `search` 用掉了 78%。所以修改 `check` 或读取菜谱的代码时，余地很小。v0.2 的发布测试把每个中位数和它的基线记在一起。比基线高出 20% 以上的中位数，只要低于 1 秒，仍然通过。发布测试的总结会写出它，让 Troy 在它达不到 PT01 之前就看到变慢。

## 4. 设备

| 设备 | 操作系统 | 由谁运行 |
| --- | --- | --- |
| Troy 的电脑 | Windows 11，Windows Terminal 里的 Windows PowerShell 5.1 和 PowerShell 7，记事本，以及中文输入法 | Troy |
| Troy 的电脑 | Windows 11，`recipe-menu` 环境里的 Python 3.13，在发布测试里 | Claude |

## 5. 验收记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-16 | 初稿。 |
