---
troy-doc: "F15-design"
lang: "zh-CN"
version: "1.1"
updated: "2026-11-20"
status: "Troy 已于 2026-11-20 批准"
mirror-of: "design.md"
---

# F15 添加菜谱：接口设计

## 1. 功能

- 编号和名称：F15 添加菜谱
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F03、F04、F07

## 2. 接口

F15 在 `src/recipe_menu/commands/add/` 里构建命令模块 `add`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.add` 导出一个名称 `ADD_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出它。你输入的命令是 `recipe-menu add`（2.2）。它的提示放在 `src/recipe_menu/commands/add/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F15 在它的 mock PR 里把 `ADD_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `SEARCH_COMMAND` 之后（选择 1，C 点）。这一项是命令功能对命令列表唯一的改动（架构 4，F05 设计 2.9）。F15 还给四个已实现的模块加上它需要的东西（第 3 节）：按架构 5.2 的计划，给 `app` 里的 `Context`（3.1）和 `cli` 里的 `main`（3.2）加上输入流；给负责控制台流的 `text` 加上 `use_utf8_input`（3.3）；给 `check` 加上 `check_recipe` 和 `problem_block`，架构 3 说 `add` 会复用 `check` 来检查一个菜谱（3.4 和 3.5）。F15 原型 `docs/prototypes/F15-add.md` 展示了这个命令。F03 和 F04 为 F15 做的计划仍然成立：`add` 用 `find_ingredient` 检查每种食材（F03 设计第 2 节），用 `is_recipe_id` 和 `list_recipe_ids` 的列表检查 ID（F04 设计第 2 节）。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F15 提供的接口 |
| --- | --- |
| `recipe-menu add` 逐行询问 ID、名称、份数、标签、食材和步骤（[需求 4](../../requirements.zh-CN.md#4-功能点)）。 | `recipe-menu add`（2.2），以及 `ADD_COMMAND`（2.1）。它按选择 3 问八个问题，两种语言的顺序相同，并把每个回答当作 `Context.input` 的一行来读（3.1，选择 4）。 |
| 它对照目录检查每个回答。 | 用 `Catalog.find_tag` 检查标签（选择 8），用 `Catalog.find_ingredient` 和 `parse_quantity` 检查每一行食材（选择 9）。用 `is_recipe_id` 和 `recipes/` 的列表检查 ID（选择 5），按 1 到 100 的范围检查份数（选择 7）。 |
| 回答有误时再问一次。 | 每个错误的回答得到一条说明错在哪里的提示。然后 `add` 再问同一个问题；错误的食材行则接着问列表的下一行（选择 3）。 |
| 最后写出一个新的菜谱文件。 | `create_file` 按示例数据的格式写出 `recipes/<id>.toml`，从不覆盖已有的条目（选择 10 和 11）。 |
| 名称或步骤可以缺一种语言。这时命令改为显示另一种语言，`check` 会对缺的部分给出警告（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | B 点：名称的任一种语言、步骤的任一种语言，只要另一种语言有文字，就可以留空（选择 6）。保存后的检查会显示这个警告（选择 12）。 |
| `add` 和 `edit` 复用 `check` 来检查一个菜谱（[架构 3](../../architecture.zh-CN.md#3-模块)）。 | `check_recipe` 和 `problem_block`（3.4 和 3.5），以及保存后的那几行（选择 12）。 |

下面每个接口都遵守这些规则：

- `add` 在包内只引用 `app`、`lang`、`units`、`text`、`datafile`、`catalog`、`recipes` 和 `check`。架构 3 里它那一行允许这些模块。它既不需要 `settings`、`menus`，也不需要 `shopping`：它通过 `context.settings.servings` 读取默认份数（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `add` 只通过 `read_catalog`、`list_recipe_ids`、`create_file` 和 `check_recipe` 访问磁盘，这些函数都通过 `datafile` 工作（架构 8）。它只写新文件 `recipes/<id>.toml`（[架构 5.1](../../architecture.zh-CN.md#51-数据文件)）。它只从 `context.input` 读回答，只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西：`cli` 把输入流放在上下文里传给它（3.1 和 3.2）。它不保存状态。
- 读取函数遇到坏数据从不抛异常，`create_file` 把每个 `OSError` 变成一个值（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`add` 在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。错误的回答不是数据里的错误：它得到一条提示，问题再问一次。`run` 不抛出 `UsageError`，因为 `add` 不接受参数值。Ctrl+C 产生的 `KeyboardInterrupt` 继续传给 `cli`，`cli` 给出 130（选择 4）。传到 `cli` 的任何其他异常都是 bug。
- `ADD_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。F15 不增加值类型。`Context.input` 是一个 `TextIO`（3.1）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F15 的接口都没有性能指标。PT01 不为 `add` 计时（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。选择 14 说明 F15 给其他每个命令的启动增加了什么。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和第 3 节给出它们的规则。

1. **一个命令，在帮助里排在 `search` 之后**（C 点）。F15 把 `ADD_COMMAND` 加在 `COMMANDS` 里 `SEARCH_COMMAND` 的后面。所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, ADD_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`。处理菜谱的几个命令放在一起，F16 可以把 `edit ID` 紧接着放在 `add` 后面。`add` 有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它（F05 设计 2.5），这是 v0.2-S14 的要求。它不声明参数，也不声明选项，所以两种语言里它的用法都是 `add`。`add` 占 3 列，所以 `menu suggest [WEEK]` 仍是最宽的第一格，两种语言里两张表的第二列仍从第 24 列之后开始。`add` 那一行让它下面的各行往下移一行，帮助的其他行都不变。帮助共 23 行（2.1）。第 3 节列出这个位置会让哪个测试失败。
2. **`add` 提问之前读什么，在哪里停下。** 第一个问题之前，`add` 用 `read_catalog` 读目录，用 `list_recipe_ids` 列出 `recipes/`，按这个顺序（2.2，第 1 和 2 步）。标签和食材需要目录，ID 需要这个列表。两者中任一个的第一个错误都会让 `add` 用 `first_error` 和 `stop_at_error` 停下，这发生在你输入任何东西之前，就像 `list` 和 `menu suggest` 在这些错误处停下一样（F05 设计 2.8）。所以像 `recipes\Rice Bowl.toml` 这样名称不是菜谱 ID 的条目，也会让 `add` 停下。列表没有错误时，`recipes/` 里每个名称以 `.toml` 结尾的条目都是列表给出的菜谱 ID。所以 `create_file` 会拒绝的每个名称都在这个列表里（选择 11）。警告不改变任何东西。`add` 不读任何菜谱文件、菜单，也不读常备清单。保存文件之后，`check_recipe` 再读一次目录，并读这个新文件（选择 12）。
3. **八个问题。** 两种语言里 `add` 都按这个顺序提问，这是 v0.2-S09 和 v0.2-S10 给出回答的顺序。提示是 2.2 的那些提示；“空回答”是指去掉两端空白后为空的回答（选择 4）。

   | 问题 | 提示 | 回答 | 空回答 | 回答错误之后 |
   | --- | --- | --- | --- | --- |
   | 1. ID | `ID_PROMPT` | `recipes/` 里还没有的菜谱 ID（选择 5）。 | 结束 `add`，退出码 0，不写文件。 | `NOT_AN_ID` 或 `ID_EXISTS`，然后再问问题 1。 |
   | 2. 中文名 | `ZH_NAME_PROMPT` | 任何文字。 | 没有中文名（选择 6）。 | 无。每个回答都对。 |
   | 3. 英文名 | `EN_NAME_PROMPT` | 任何文字。 | 问题 2 有名称时，表示没有英文名。 | 问题 2 和 3 都是空回答时给出 `NAME_NEEDED`，然后再问问题 3。 |
   | 4. 份数 | `SERVINGS_PROMPT` | 1 到 100 之间的整数（选择 7）。 | 设置里的份数，提示里显示的就是它。 | `SERVINGS_WRONG`，然后再问问题 4。 |
   | 5. 标签 | `TAGS_PROMPT` | 目录里标签的名称，用逗号分隔（选择 8）。 | 没有标签。 | `UNKNOWN_TAG` 或 `NO_TAGS`，然后再问问题 5。 |
   | 6. 食材 | `INGREDIENTS_PROMPT`，然后每行前面两个空格 | 一行食材，名称和数量，比如 `西兰花 300 g`（选择 9）。 | 结束这个列表。 | 两个空格之后的 `NAME_AND_QUANTITY`、`UNKNOWN_INGREDIENT` 或数量的提示。然后问列表的下一行。 |
   | 7. 中文步骤 | `ZH_STEPS_PROMPT`，然后每行前面两个空格 | 一步。 | 结束这个列表。 | 无。每个回答都对。 |
   | 8. 英文步骤 | 问题 7 有步骤时是 `EN_STEPS_OPTIONAL_PROMPT`，否则是 `EN_STEPS_PROMPT`，然后每行前面两个空格 | 一步。 | 结束这个列表。 | 两个步骤列表都是空的时给出 `STEPS_NEEDED`，然后再问问题 8。 |

   每个错误的回答只得到一条提示。问题 1 到 5 和问题 8 的回答之后的提示单独占一行，不缩进。食材行之后的提示以两个空格开头，就像原型显示的那样。和原型说的一样，`add` 不问备注。备注你在文件里加。
4. **`add` 怎样读一个回答。**
   - `add` 把提示写到 `context.out`，调用 `context.out.flush()`，再用 `context.input.readline()` 读一行。Python 按行缓冲控制台流，所以不调用 flush 的话，没有换行的提示不会在回答之前显示出来。问题 1 到 5 的提示末尾没有换行，所以你在提示的那一行上输入回答。列表的提示以换行结束，列表的每一行都以两个空格作为提示。
   - 回答是这一行去掉换行符、再按 `str.strip()` 去掉两端空白后的文字，所以两端的全角空格 U+3000 不算。
   - `context.input.isatty()` 为假时，`add` 紧接着提示，把读到的那一行（末尾有 LF 时去掉这个 LF）和一个换行写到 `context.out`。`add` 只去掉这个 LF，这一行的其他部分都不动。调用 `use_utf8_input` 之后，标准输入的每一行都只以 LF 结束，管道里用 CR LF 或单独的 CR 结束的行也一样（3.3），所以在任何系统上回显里都没有 CR。所以通过管道和在测试里，输出读起来和控制台里的会话一样：每个提示和它的回答在同一行，就像原型显示的那样。在控制台里，控制台会显示你输入的东西，`add` 不再多写。`isatty()` 和 `readline()` 一样，是对 `cli` 放在上下文里传来的流的调用，所以 `add` 自己不读取任何控制台（架构 8）。
   - 输入结束时，`readline()` 给出空文字：管道结束了，或者在 Windows 控制台里按了 Ctrl+Z 再按回车。在问题 1，输入结束算作空回答，所以 `add` 以退出码 0 结束，不写文件。在之后的任何问题，`add` 把 `INPUT_ENDED` 写到错误流，不写文件，并给出 1，所以提前结束的管道会说明这一点，脚本也能看到退出码。`context.input.isatty()` 为假时，`add` 先在提示后面写一个换行。
   - 在某个问题处按 Ctrl+C，会让 `readline()` 抛出 `KeyboardInterrupt`，`add` 不捕获它。`cli` 给出 130，不再写出任何东西（架构 6，F05 设计 2.10）。`add` 只在最后一个回答之后才写文件，所以不会留下文件。在 Windows 上，Python 的控制台读取会把提示处的 Ctrl+C 变成 `KeyboardInterrupt`，而不是输入结束。v0.2-S18 第 5 步在 Windows Terminal 里检查这一点。
   - 测试把回答作为一个流传进去：`main(..., stdin=io.StringIO("garlic-broccoli\n蒜蓉西兰花\n..."))`（3.2），或者 `Context(..., input=io.StringIO(...))`（3.1）。版本测试把回答作为 UTF-8 字节写到 `recipe-menu add` 的标准输入，然后关闭它。
   - 安装好的命令读 `sys.stdin`。启动时，`cli` 调用 `use_utf8_input(sys.stdin)`（3.3），让这个流按 UTF-8 解码（带不带字节顺序标记都行），把不是 UTF-8 的字节变成 U+FFFD，并在每个系统上都让每一行以 LF 结束。所以 `add` 按 UTF-8 读管道，就像重定向的输出是 UTF-8 一样（ADR-0004），不管代码页和 `PYTHONIOENCODING` 是什么。在 Windows 控制台里，Python 通过控制台的 Unicode 接口读取，所以你用中文输入法输入的回答原样到达，执行 `chcp 437` 之后也一样，v0.2-S18 会检查这一点。控制台负责编辑这一行，所以退格键有效，`add` 在你按回车之后才得到这一行。
   - Windows PowerShell 5.1 用 `$OutputEncoding` 把管道发给程序，除非你改过，它是 ASCII，所以从 Windows PowerShell 5.1 用管道传来的中文回答会变成 `?`。你在控制台里输入回答，所以需求里没有哪个流程需要这样的管道。
5. **ID。** 空回答结束 `add`，和原型说的一样。`is_recipe_id(answer)` 为假时（F04 设计 2.4），`add` 写出 `NOT_AN_ID`。第 2 步的列表里已经有这个回答时，它写出 `ID_EXISTS`，也就是原型“An ID that exists”里的那一行。两种提示之后，它都再问问题 1。`create_file` 写文件时会再检查一次这个名称（选择 11）。
6. **名称和步骤**（B 点）。名称的任一种语言、任一个步骤列表，只要另一种语言有文字，就可以留空，这是需求 3 允许的。
   - 空的中文名表示没有中文名。中文名有文字时，空的英文名表示没有英文名。两个名称都是空的时，`add` 写出 `NAME_NEEDED`，再问问题 3。
   - 空的中文步骤列表表示没有中文步骤。有中文步骤时，英文步骤的提示是写着“可以不写”的 `EN_STEPS_OPTIONAL_PROMPT`，否则是 `EN_STEPS_PROMPT`。两个列表都是空的时，`add` 写出 `STEPS_NEEDED`，再用 `EN_STEPS_PROMPT` 问问题 8。
   - 文件里不写空着的那种语言，比如 `name = { zh = "葱花蛋" }`，或者只有 `zh` 的 `[steps]` 表（选择 10）。这时 `read_recipe` 给出 `NO_EN_NAME` 或 `NO_EN_STEPS`，或者对应的中文那条，都是警告（F04 设计 2.6），保存后的那几行会显示它（选择 12）。
7. **份数。** 对的回答由一个或多个 ASCII 数字 0 到 9 组成，没有别的字符，值在 `MIN_SERVINGS` 和 `MAX_SERVINGS` 之间，也就是 1 到 100（F05 设计 3.1）。所以 `3` 和 `03` 都得到 3。`0`、`101`、`two`、`2.5`、`-1`、`+3`、`3 份` 和全角数字的 `３` 都得到 `SERVINGS_WRONG`，它的文字和 `datafile` 的 `SERVINGS_NOT_A_NUMBER` 相同。几千位数字的回答也得到这条提示，从不碰到 Python 把文字转成 `int` 时的限制。空回答得到 `context.settings.servings`，提示在方括号里显示它，示例数据是 `[2]`。设置把这个份数给没写份数的菜（需求 3），所以用默认值的菜谱用在这样的菜上时不需要换算。
8. **标签。** `add` 在 `,`、`，`（U+FF0C 全角逗号）和 `、`（U+3001 顿号）处拆开回答，所以 `快手, 素`、`快手，素` 和 `快手、素` 得到相同的标签。每一部分去掉两端空白后再算，空的部分（比如末尾逗号后面的那部分）跳过。`Catalog.find_tag` 查找每一部分，所以一部分按两种语言匹配标签的名称，和 `list --tag` 的匹配方式一样（F03 设计 2.6）。第一个找不到标签的部分让整个回答都算错：`add` 写出按目录标签数选择写法的 `UNKNOWN_TAG`（目录里没有标签时是 `NO_TAGS`），再问问题 5。两个部分写的是同一个标签时，比如 `快手, quick`，只算一次，就像 `read_recipe` 只保存一次一样（F04 设计 2.6）。
9. **一行食材。** 一行的词是空白字符之间的片段，和 `str.split()` 给出的一样，所以全角空格 U+3000 也分隔词。
   - 数量：最后一个词是 `适量`，或者最后两个词是 `to` 和 `taste`（字母 A 到 Z 不分大小写）时，数量就是这个词或这两个词。否则，数量从第一个字符是 ASCII 数字 0 到 9 的最后一个词开始，一直到这一行的末尾。
   - 名称是数量前面的文字，去掉两端空白。
   - 没有数量、或者名称为空的一行，给出 `NAME_AND_QUANTITY`。所以名称和数量之间必须有空格，这正是提示 `“名称 数量”` 的要求：`盐适量` 和 `西兰花300g` 得到这条提示，`西兰花 300g` 可以。
   - 名称可以含有数字，比如 PT01 数据文件夹里的 `食材300`（v0.2-S16），所以这一行的第一个数字不一定是数量的开头。F01 的数量是一个数字加上可有可无的单位，或者“适量”，所以单位前面有空格时，数量最多两个词。

   | 一行 | 名称 | 数量 |
   | --- | --- | --- |
   | `西兰花 300 g` | `西兰花` | `300 g` |
   | `Cooking oil 2 tbsp` | `Cooking oil` | `2 tbsp` |
   | `Salt to taste` | `Salt` | `to taste` |
   | `盐 适量` | `盐` | `适量` |
   | `食材300 100 g` | `食材300` | `100 g` |
   | `Egg 3` | `Egg` | `3` |
   | `7-Up 1 can` | `7-Up` | `1 can` |
   | `Peanut`、`300 g` 或 `盐适量` | 无 | 无。这一行给出 `NAME_AND_QUANTITY`。 |

   - 然后 `catalog.find_ingredient(name)` 按 F03 设计 2.6 的规则查找食材：名称可以是两种语言之一，两端的空白不算，只有字母 A 到 Z 区分大小写，名称中间的空白照写的算。找不到时，这一行给出 `UNKNOWN_INGREDIENT`，也就是原型里 `橄榄油 1 tbsp` 之后的那一行。
   - 然后 `parse_quantity(quantity, ingredient.unit)` 读数量，和 `read_recipe` 读 `amount` 的方式一样（F04 设计 2.6），所以 `Egg 3` 得到 3 个。`WrongQuantity` 按它的原因给出提示，文字和 `read_recipe` 的相同：`AMOUNT_NOT_A_NUMBER`、`AMOUNT_UNKNOWN_UNIT`、`AMOUNT_NO_UNIT` 或 `AMOUNT_ZERO`。原因 `EMPTY` 不会出现，因为数量从不为空。
   - 错误的一行得到这三项检查里第一个不通过的那条提示，`add` 不保留这一行。对的一行被保留。同一种食材可以出现两次，列表也可以是空的，`read_recipe` 两者都允许（F04 设计 2.6）。所以 `read_recipe` 读文件里保留的每一行时，名称和数量都相同，找到的食材和数量也相同。
10. **文件。** 它的格式和示例数据里的菜谱一样，比如 `recipes/choy-sum.toml`，没有备注，也没有注释：

    ```toml
    name = { zh = "<Chinese name>", en = "<English name>" }
    servings = <servings>
    tags = ["<tag>", "<tag>"]

    ingredients = [
      { item = "<name>", amount = "<quantity>" },
      { item = "<name>", amount = "<quantity>" },
    ]

    [steps]
    zh = [
      "<Chinese step>",
    ]
    en = [
      "<English step>",
    ]
    ```

    - 名称里不写空着的那种语言（选择 6）。
    - `tags` 里每个标签只写一次，写成你第一次输入的样子，按你回答里的顺序。没有标签时是 `tags = []`。
    - `ingredients` 里每个保留的食材行写一行，按你输入的顺序。没有时是写在一行里的 `ingredients = []`。
    - `[steps]` 里先写 `zh`，再写 `en`，每一步写一行，没有步骤的那种语言不写。
    - 每段文字都是你输入的回答，去掉两端空白：食材和标签的名称用你输入的那种语言，而不是目录里的写法，因为 `read_recipe` 按两种语言都能找到名称。数量也保留你的写法，比如 `to taste` 或 `300g`。
    - 每段文字是放在双引号里的 TOML 基本字符串。`\` 变成 `\\`，`"` 变成 `\"`，U+0000 到 U+001F 和 U+007F 的每个控制字符变成 `\u` 加上它的四位十六进制数字，比如制表符写成 `\u0009`。其他字符都保持原样。所以 `read_recipe` 读回来的正好是你的文字。
    - 每一行都以 LF 结束，最后一行也是。`create_file` 写出没有字节顺序标记的 UTF-8（[架构 5.1](../../architecture.zh-CN.md#51-数据文件)）。

    所以 `check`、`list`、`show`、`search`、`menu suggest` 和 `shop` 像读任何菜谱一样用 `read_recipe` 读这个文件，F16 的 `edit` 也像打开任何菜谱文件一样打开它。
11. **`add` 怎样保存文件。** 最后一个回答之后，`add` 调用一次 `create_file(context.folder, context.folder.recipe_file(recipe_id), text)`（F11 设计 3.3）。ID 来自 `is_recipe_id`，所以 `recipe_file` 得到的是安全的名称（F03 设计 2.1）。`create_file` 拒绝和文件同名的条目（只有 A 到 Z 大小写不同的也算），并以独占模式打开文件，所以 `add` 从不覆盖文件（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。它用一次 `write` 写出文字，写的时候遇到 `OSError` 或 Ctrl+C 会删除这个文件。`add` 按结果处理：
    - **`CREATED`。** 它检查这个文件（选择 12）。
    - **`EXISTS`。** 第 2 步列出 `recipes/` 之后出现了同名的条目，比如 `add` 等你回答时，你在另一个窗口里保存了一个这个名字的文件。`add` 把带这个条目完整路径的 `APPEARED` 写到错误流，并给出 1。它什么也没创建。
    - **`FAILED`。** `add` 在错误流上写出三行，并给出 1。第一行是 `problem_lines` 的 `where`（F05 设计 2.8）：按问题里的样子写出文件，也就是相对于数据文件夹的路径，比如 `recipes\garlic-broccoli.toml`；文件夹无法列出时是 `recipes`。第二行是两个空格加上 `what`，比如 `The file cannot be written: access is denied.`。第三行是 `NOTHING_SAVED`；`create_file` 没能删除这个文件时，第三行是带这个文件完整路径的 `LEFT_BEHIND`。

    架构 6 规定问题用相对于数据文件夹的路径写出它的文件，其他提示用完整路径写出文件。保存后的那一行、`APPEARED` 和 `LEFT_BEHIND` 不是问题，所以用完整路径写出文件，就像原型里 `已保存 C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml。…` 那一行一样。失败时的第一行和检查的那几行是问题，所以用相对于数据文件夹的路径写出文件。没有哪种情况需要修改架构 6。在 `create_file` 写出之前，你的回答只存在内存里，所以 `EXISTS` 和 `FAILED` 会让它们丢失。
12. **保存后的检查。** `CREATED` 之后，`add` 调用 `check_recipe(context.folder, recipe_id)`（3.4）。它给出 `read_catalog` 的错误，然后是用那个目录调用 `read_recipe` 得到的问题：这就是 `check` 对一个菜谱做的检查（F07 设计 2.2，第 2 和 5 步）。不管退出码是什么，这几行都写到输出流，因为它们是一次检查的报告，就像 `check` 的报告一样（架构 6）。v0.2 测试计划在“The report of add and edit”里也这样说。
    - 没有问题时，`add` 写出一行 `SAVED`，比如 `已保存 C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。`，也就是原型的最后一行，并给出 0。
    - 有问题时，它写出带问题个数的 `SAVED_WITH_PROBLEMS`，然后是错误的 `problem_block`，再是警告的 `problem_block`，各自按 `check_recipe` 给出的顺序（3.5）。有错误时，后面接 `FIX_AND_CHECK`，`add` 给出 1。只有警告时，它给出 0，因为警告从不改变退出码（架构 6）。

    不管哪种情况，文件都已经保存。`add` 是对照第 1 步的目录检查回答的，所以只有目录或文件在那之后改变时才会出现错误，比如 `add` 等你回答时你修改了目录。你留空一种语言时会出现警告（选择 6）。
13. **提示里的数字。** `add` 的提示显示问题的个数、设置里的份数（1 到 100），以及作为文字的你的回答。`SERVINGS_WRONG` 不显示数字。文件里的问题只通过 `stop_at_error`、`problem_lines` 和 `problem_block` 写到输出，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `add` 的提示不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。
14. **速度。** 没有性能指标写到 `add`。它在提问之前读目录、列出 `recipes/`，保存之后读目录和一个菜谱，所以在 PT01 数据文件夹上，它自己的读取所花的时间和 `show` 差不多，`show` 在 v0.1.0 的发布测试里是 0.164 秒（v0.2 测试计划第 3 节）。其余的时间是你在输入。v0.2-S16 在 PT01 文件夹上运行 `add`，但不计时。其他每个命令的启动变化很小。`cli` 在启动时引用 `add` 的几个小文件，而 `add` 需要的模块，`cli` 已经通过其他命令全都引用过了。`cli` 还调用一次 `use_utf8_input(sys.stdin)`，它重新配置一个还没读过的流。这两者共花几毫秒：架构师在 `python -X importtime` 下测得它的模型里新文件的自身时间约 3 毫秒，mock 的新文件花了 2 到 3 毫秒，重新配置这个流只需微秒级的时间。这远低于 `check` 在 PT01 的 1 秒之内剩下的 172 毫秒（F14 之后是 0.828 秒）。这些时间不是在 Troy 的电脑上测的，v0.1 的 PT01 用例会在 v0.2 的发布测试里在那台电脑上再运行一次。
15. **只导出这个命令。** `add` 导出 `ADD_COMMAND`，别的什么都不导出。只有 `cli` 能引用 `add`（架构 3），所以别的名称不会有使用者。`add` 自己保存几条提示的副本，文字相同：`browse` 的 `UNKNOWN_TAG` 和 `NO_TAGS`（`suggest` 也这样保存，F14 设计，选择 4）、`recipes` 的四条数量提示，以及 `datafile` 的份数提示，因为这些模块把它们留在内部（架构 8）。以后的 `[refactor]` PR 可以让它们共用。

运行 `add` 的 v0.2 场景，在这些选择下都成立：

- v0.2-S09：第 1 步打印原型“In Chinese, with one wrong answer”那一段，回答写在各自提示的那一行上（选择 4），最后一行是 `已保存 <home>\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。`。文件就是 2.2 示例里的 22 行，UTF-8，没有字节顺序标记，用 LF 换行（选择 10）。食材行 `橄榄油 1 tbsp` 得到 `UNKNOWN_INGREDIENT`，`add` 接着问下一行（选择 9）。
- v0.2-S10：5 个错误的回答各得到一条提示（选择 3、7、8 和 9）：`0` 和 `two` 之后是 `Servings must be a whole number from 1 to 100, such as 2.`，然后是 `Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.`、`  Unknown unit "cups" in "1 cups".` 和 `  The catalog has no "Peanut". Enter a name from the catalog, or add it to the catalog first and then run add again.`。第 1 步最后一行是 `Saved <home>\recipe-menu\recipes\egg-fried-rice.toml. The check found no problems.`，以 0 退出。
- v0.2-S11：第 1 步打印 `Recipe ID (also the file name): tomato-egg`、`ID_EXISTS` 那一行，再打印一次提示，空回答让 `add` 以 0 结束（选择 5）。第 2 步打印 `菜谱 ID（也是文件名）：`，以 0 退出。两步都不写文件，因为 `add` 只在最后一个回答之后才写。
- v0.2-S14：第 5 步打印 `cli` 的 `NO_DATA_FOLDER` 和 `RUN_INIT`，以 1 退出，这发生在 `add` 提问之前（选择 1）。第 1 步和第 2 步的帮助在 `search` 那一行后面紧跟着多了 `add` 那一行，第二列仍在第 24 列之后（2.1）。所以测试经理按 v0.2 测试计划第 2 节的规定，更新 v0.2-S14 要求的帮助。
- v0.2-S15：第 2 步只创建 `recipes\garlic-broccoli.toml`。`create_file` 直接写出它，没有临时文件（选择 11）。新条目会让文件夹 `recipes\` 得到新的修改时间，就像第 1 步里 `menu suggest` 的移动让 `menus\` 得到新的修改时间一样。所以第 2 步的“没有别的文件改变”只算文件，不算文件夹。
- v0.2-S16：`食材300 100 g` 和 `食材150 适量` 按选择 9 拆开。检查读取有 300 种食材的目录和这一个新菜谱，没有发现问题。
- v0.2-S18：控制台原样读到输入法输入的中文回答，退格键编辑这一行，`chcp 437` 不改变任何东西（选择 4）。在第二个问题处按 Ctrl+C 得到退出码 130，不再有任何文字，也没有文件。
- 通过管道时，`add` 把每个回答写在它的提示后面（选择 4），所以 v0.2-S09 到 v0.2-S11 的输出就是原型各段的那些行。Markdown 原型里的一行末尾不显示空格。在输出里，英文提示在冒号后面保留它的空格，回答为空时也一样，比如 `Recipe ID (also the file name): `；列表里空回答的那一行是两个空格。所以测试经理按 2.2 示例给出的样子比较各行，并把 v0.2 测试计划的规则“Answers to `add`”改为：每个回答跟在它的提示后面。
- v0.1-S01、v0.1-S02 和 v0.1-S13：F15 不改动 `init` 或 `menu new` 写的任何文件。`add` 只写 `recipes/<id>.toml`，F15 也不给 `settings.toml` 加键。所以这三个场景都成立，和 v0.2 测试计划预期的一样。

这三点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 原型给出了中文的各个提示、食材未知时的中文提示、保存后的中文那一行，以及 ID 已存在时的英文提示和英文提示语。其他文字都沿用原型或某条已有提示的措辞。`add` 有 32 条提示，列在 2.2 里。其中 7 条是已有提示的副本，1 条完全来自原型。建议按 2.2 的写法接受其余 24 条：
  - 英文的各个提示，比如 `Chinese name: `、`Servings [2]: `、`Tags, separated by commas: `、`Ingredients, one per line, as "name quantity". An empty line ends the list:` 和 `English steps, one per line. An empty line ends the list (optional):`。
  - 原型里中文各行对应的英文：`The catalog has no "{name}". Enter a name from the catalog, or add it to the catalog first and then run add again.` 和 `Saved {file}. The check found no problems.`。
  - 原型里英文那一行对应的中文：`菜谱 {id} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {id}”。`。
  - 错误的 ID、缺名称或缺步骤，以及数量前面没有空格的食材行的提示：`NOT_AN_ID`、`NAME_NEEDED`、`STEPS_NEEDED` 和 `NAME_AND_QUANTITY`，比如 `Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".` 和 `请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。`。
  - 保存后有问题时的那几行，比如 `Saved {file}. The check found 1 error and 2 warnings:` 和 `已保存 {file}。检查发现了 1 个错误和 2 个警告：`，以及 `FIX_AND_CHECK`。
  - 提前结束和保存失败时的那几行：`INPUT_ENDED`、`APPEARED`、`NOTHING_SAVED` 和 `LEFT_BEHIND`。
  - 帮助里的那一行：`Add a recipe by answering questions.` 和 `回答问题，添加一个菜谱。`。
- **B. 可以留空的回答**（选择 6）。
  - 做法 1，推荐：名称的任一种语言、任一个步骤列表，只要另一种语言有文字，就可以留空。提示保持原型的样子，只是英文步骤只有在有中文步骤时才写“可以不写”。保存后的检查对你留空的每种语言给出警告。
  - 做法 2：只有英文步骤可以留空，就像原型标出的那样。空的中文名、英文名或中文步骤列表得到一条提示，问题再问一次。选择 3 和 6、2.2 的提示和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：需求 3 允许名称或步骤缺一种语言，所以 `add` 能写出需求允许的每一种菜谱（备注除外），只有英文的菜谱也可以。
- **C. `add` 在帮助里的位置**（选择 1）。
  - 做法 1，推荐：紧接在 `search` 之后。第 3 节的修测试 PR 在 mock PR 之前修改 F11-T01。
  - 做法 2：放在最后，在 `shop` 之后。不修改任何测试。选择 1、2.1 和 v0.2-S14 的帮助在 mock PR 之前修改。
  - 推荐做法 1 的理由：这样 `list`、`show`、`search`、`add` 和以后的 `edit` 放在一起，帮助按每个命令处理的对象排列：数据文件夹、菜谱、周菜单和购物清单。

这些后续功能会在 F15 的基础上构建。细节由它们自己的设计决定。

- F16 的 `edit` 可以在编辑器关闭后用 `check_recipe` 检查菜谱，用 `problem_block` 显示它的问题，`problem_block` 的缩进就是 F16 原型“An edit that leaves a mistake”里的缩进。F16 可以把 `edit ID` 紧接着放在帮助里 `add` 的后面。第 3 节的修测试 PR 之后，已验收功能的测试都不再依赖 `search` 后面的那一行。
- `add` 不从 `suggest` 取任何东西，F16 也不需要 `add` 的任何东西。

troy-mode 的流程有一个 mock PR 和一个实现 PR。`COMMANDS` 里放在 `SEARCH_COMMAND` 之后的这一项会让 F11-T01 失败，它把 `search` 那一行后面的两行当作 `menu new` 和 `menu show` 的两行（第 3 节）。开发工程师从不修改测试（R08），已验收功能的每个测试都必须通过（R10）。所以在 F15 的 mock PR 之前，一个修测试的 PR 修改 F11-T01，让它按开头找到 `menu new` 那一行，`search` 后面有没有别的行都成立。测试计划列出这个测试和修改它的 PR。按 C 点的做法 2，就不需要修测试的 PR。

mock（PR 3）包含 `src/recipe_menu/commands/add/__init__.py`、`messages.py`、放 `run` 的一个内部文件（比如 `_run.py`），以及 `src/recipe_menu/cli/_commands.py` 里的那一项。它给 `Context` 加上带默认值的字段 `input`，给 `main` 加上参数 `stdin`，但 mock 不把它传下去，所以上下文得到默认值。它给 `text` 加上 `use_utf8_input`，mock 里它什么也不改。它在一个新的内部文件里给 `check` 加上 `check_recipe` 和 `problem_block`，mock 里两者都给出 `()`，`check` 的报告保持原样，所以 F07 的测试仍然通过。它定义每条提示和字段齐全的 `ADD_COMMAND`。它的 `run` 不读文件、不读回答、不写任何东西，并给出 0。所以检查以下内容的新测试在 mock 上会失败（R09）：某个提示、某条提示语、输出的某一行、退出码 1、新文件的字节、失败及其各行、`main` 传下去的流、`use_utf8_input` 设置的编码，或者 `check_recipe` 和 `problem_block` 给出的问题和各行。这些测试在 mock 上会通过，从而违反 R09：只检查 `ADD_COMMAND` 的字段、帮助、某条提示、退出码 0，或者 `Context.input` 的默认值的测试。检查 `cli` 在运行 `add` 之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、多余的参数或未知选项。只检查一次运行没有写文件的测试也是如此，比如第一个回答为空时；只期望 `check_recipe` 给出 `()` 的测试也是如此。每个这样的测试都还要检查 mock 做错的内容，比如输出。按估计，mock 改动约 10 个文件，约 400 行，文件数超过 R03 的 5 个，所以它的说明要写明软限制的理由。理由是测试既直接用到上下文、`main`、`text` 和 `check`，也通过 `add` 用到它们，所以它们要在同一个阶段一起带上，和 F08、F11、F13 和 F14 的 mock 一样。

实现（PR 5）把 `run` 放在 `add` 的内部文件里，包括它的提问、读回答、拆分食材行、文件的文字和保存后的那几行，比如 `_run.py`、`_ask.py`、`_ingredient.py`、`_file.py` 和 `_report.py`。它还包含 `check_recipe` 和 `problem_block`（`check` 的报告改用 `problem_block` 写出）、`main` 里的流，以及 `use_utf8_input`。按估计，它改动约 10 个文件，约 650 行，超过 R03 的限制，所以它的说明也要写明软限制的理由：`add` 的测试同时需要这些部分。开发工程师要早一点运行 troy-check。

### 2.1 `ADD_COMMAND`

- 模块：add
- 功能：对 `add` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 问 2.2 的那些问题，写出新的菜谱文件，并检查它。

签名：

```python
ADD_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("add",)
#   help_line = ADD_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 组成的元组 | `("add",)`。 | 无 |
| `help_line` | `Message` | `ADD_HELP`：“Add a recipe by answering questions.”和“回答问题，添加一个菜谱。”。 | 没有占位符。 |
| `run` | 接受一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 读目录和 `recipes/` 的列表，提问，通过 `create_file` 写出文件，检查它，并写出 2.2 的那几行。 | 给出 0 或 1。遇到坏数据、错误的回答或磁盘上的失败都不抛异常。让 `KeyboardInterrupt` 继续传给 `cli`。 |
| `argument` | `None` | `add` 不接受参数。 | 无 |
| `options` | 空元组 | `add` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `add`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4），带 3.1 的字段 `input`。 | `run` 用到 `context.lang`、`context.folder`、`context.settings.servings`、`context.out`、`context.err` 和 `context.input`。它既不用 `context.today`，也不用 `context.random`。 |
| `arguments` | `Arguments` | 命令行给 `add` 的东西（F05 设计 2.6）。 | 空的，因为 `add` 不声明参数和选项。`run` 不读它。 |

- 返回值：`ADD_COMMAND`，一个 `Command`。
  - 两种语言里 `ADD_COMMAND.usage` 都是 `add`。所以帮助显示 `add`，用法错误引用 `recipe-menu add`。
  - `ADD_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出各行，并给出 0 或 1。

F15 之后，帮助列出这些命令和选项，第二列和 F14 之后一样，在第 24 列之后（选择 1）。帮助的其他行是 F05 原型里的那些行。英文：

```text
Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  add                   Add a recipe by answering questions.
  menu new [WEEK]       Create an empty week menu.
  menu show [WEEK]      Show a week menu.
  menu suggest [WEEK]   Fill the empty meals of a week menu.
  shop [WEEK]           Make the shopping list of a week menu.

Options:
  --lang en|zh          The language of the output. Default: the settings, else English.
  --data FOLDER         The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version             Show the version.
  --help                Show this help.
```

中文：

```text
命令：
  init                  创建数据文件夹和示例数据。
  check                 检查每个数据文件有没有错误。
  list                  列出菜谱。
  show ID               查看一个菜谱。
  search 词...          按名称、食材或标签找菜谱。
  add                   回答问题，添加一个菜谱。
  menu new [周]         创建一个空的周菜单。
  menu show [周]        查看一个周菜单。
  menu suggest [周]     给一个周菜单的空餐填上菜。
  shop [周]             生成一个周菜单的购物清单。

选项：
  --lang en|zh          输出语言。默认：设置里的语言，否则英文。
  --data 文件夹         数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version             显示版本。
  --help                显示这份帮助。
```

错误：无。`run` 不抛出 `UsageError`，因为 `add` 不接受参数值。

- 副作用：2.2 的那些副作用。`run` 读目录并列出 `recipes/`，从 `context.input` 读回答，通过 `create_file` 创建 `recipes/<id>.toml`，通过 `check_recipe` 再读一次目录和新文件，并写入 `context.out` 或 `context.err`。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`，有七个菜谱；`home` 是它外面的一个空的临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里的回答是 `tomato-egg` 和一个空行，所以 `run` 写出原型“An ID that exists”的那几行后结束。帮助来自 `COMMANDS`，F15 之后它有十个命令。

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.add import ADD_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings

assert ADD_COMMAND.words == ("add",)
assert ADD_COMMAND.usage == BiText("add", "add")
assert ADD_COMMAND.help_line.render(Lang.EN) == "Add a recipe by answering questions."
assert ADD_COMMAND.help_line.render(Lang.ZH) == "回答问题，添加一个菜谱。"
assert (ADD_COMMAND.argument, ADD_COMMAND.options) == (None, ())
assert ADD_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
answers = io.StringIO("tomato-egg\n\n")
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10), input=answers)
assert ADD_COMMAND.run(context, Arguments()) == 0
exists = "The recipe tomato-egg already exists. Enter another ID, "
assert out.getvalue().splitlines() == [
    "Recipe ID (also the file name): tomato-egg",
    exists + 'or run "recipe-menu edit tomato-egg".',
    "Recipe ID (also the file name): ",
]
assert err.getvalue() == ""
assert len(list(folder.recipes.iterdir())) == 7


def help_lines(*argv: str) -> list[str]:
    output = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=output,
        stderr=io.StringIO(),
    )
    assert code == 0
    return output.getvalue().splitlines()


english = help_lines("--help")
assert len(english) == 23
assert english[9:12] == [
    "  search WORD...        Find recipes by name, ingredient, or tag.",
    "  add                   Add a recipe by answering questions.",
    "  menu new [WEEK]       Create an empty week menu.",
]
assert english[17].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[10] == "  add                   回答问题，添加一个菜谱。"
```

### 2.2 `recipe-menu add`

- 模块：add
- 功能：逐行询问一个新菜谱、对照目录检查每个回答、回答有误时再问一次，最后写出一个新菜谱文件的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 和 [4](../../requirements.zh-CN.md#4-功能点)）。F15 原型“In Chinese, with one wrong answer”和“An ID that exists”展示了它。

签名：

```text
recipe-menu add [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--lang` | `en` 或 `zh` | 提示和每条提示语的语言。它不改变文件。 | 按 F05 设计 2.10 的规定。不写这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 一个文件夹 | 数据文件夹。 | 按 F05 设计 2.10 的规定。不写这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `add`。 | 无 |
| 标准输入 | 几行文字 | 回答，每行一个（选择 4）。 | 通过管道时是 UTF-8。在控制台里可以是任何文字。 |

`add` 按顺序执行这些步骤。`path` 是 `context.folder.recipe_file(recipe_id)`。回答错误的问题按选择 3 的规定再问一次，然后才进入下一步。

1. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`add` 对第一个错误给出 `stop_at_error(context, error)`。
2. `list_recipe_ids(context.folder)` 给出 `ids` 和它们的问题（F04 设计 2.5）。问题里有错误时，`add` 用 `stop_at_error` 在第一个错误处停下。
3. 问题 1 给出 `recipe_id`（选择 5）。空回答或输入结束让 `add` 在这里给出 0。
4. 问题 2 和 3 给出名称（选择 6）。
5. 问题 4 给出份数（选择 7）。
6. 问题 5 给出标签（选择 8）。
7. 问题 6 给出食材行（选择 9）。
8. 问题 7 和 8 给出步骤（选择 6）。
9. `add` 拼出文件的文字（选择 10），调用一次 `create_file(context.folder, path, text)`（F11 设计 3.3）。结果是 `EXISTS` 时，它把 `APPEARED` 写到错误流，并给出 1。结果是 `FAILED` 时，它把失败时的三行写到错误流，并给出 1（选择 11）。
10. `check_recipe(context.folder, recipe_id)` 给出问题（3.4）。`add` 把保存后的那几行写到输出流，有问题是错误时给出 1，否则给出 0（选择 12）。

在第 4 到 8 步输入结束时，`add` 把 `INPUT_ENDED` 写到错误流，并给出 1（选择 4）。第 1 和 2 步的警告不改变任何东西。

- 返回值：退出码，以及写在相应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | 问题 1 得到空回答或输入结束，或者文件已保存，而且它的检查没有发现错误。 | 输出流：各个提示、输入不是终端时你的回答、回答错误之后的提示，以及保存后的那几行。 |
| 1 | 目录或 `recipes/` 的列表有错误，问题 1 之后输入结束，`create_file` 给出 `EXISTS` 或 `FAILED`，或者保存后的检查发现了错误。 | 输出流上是到那时为止的会话。错误流上是 `stop_at_error` 的三行、`INPUT_ENDED`、`APPEARED`，或者失败时的三行。检查发现错误之后，保存后的那几行写到输出流，错误流上什么也没有。 |
| 130 | Ctrl+C。 | 不再写出任何东西，这是 `cli` 的规定（F05 设计 2.10）。 |

输出是下面这些行，每行以换行结束，只是问题 1 到 5 的提示本身不带换行：

| 情况 | `add` 写到输出流的内容 |
| --- | --- |
| 一个问题 | 提示。然后，输入不是终端时，是你回答的那一行（去掉末尾的 LF）和一个换行（选择 4）。 |
| 一个列表（问题 6 到 8） | 列表的提示和一个换行。然后对列表的每一行：两个空格，然后，输入不是终端时，是你的这一行（去掉末尾的 LF）和一个换行。 |
| 错误的回答 | 提示语和一个换行。食材行之后，提示语前面有两个空格。 |
| 输入结束 | 输入不是终端时，在提示后面写一个换行。 |
| 文件已保存，检查没有发现问题 | `SAVED`。 |
| 文件已保存，检查发现了问题 | `SAVED_WITH_PROBLEMS`。然后是错误的 `problem_block`，再是警告的 `problem_block`（3.5）。然后，有错误时是 `FIX_AND_CHECK`。 |

保存失败时，错误流上是三行：`problem_lines(creation.problem, context.lang)` 的 `where`，然后是两个空格加上 `what`，然后是 `NOTHING_SAVED`；`creation.left` 里有这个文件时，第三行是 `LEFT_BEHIND`（选择 11）。

`add` 的提示如下。`UNKNOWN_TAG` 是一个 `Plural`（F02 设计 2.4），按目录里标签的个数选择写法。`ERROR_COUNT` 和 `WARNING_COUNT` 是 `Plural` 值，各自按它的 `count` 选择写法。它们“多个”的写法用于 1 以外的每个数，两种写法的中文相同。问题 1 到 5 的提示，英文以一个空格结束，中文以 `：` 结束，后面没有空格。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `ADD_HELP` | `Add a recipe by answering questions.` | `回答问题，添加一个菜谱。` |
| `ID_PROMPT` | `Recipe ID (also the file name): ` | `菜谱 ID（也是文件名）：` |
| `ZH_NAME_PROMPT` | `Chinese name: ` | `中文名：` |
| `EN_NAME_PROMPT` | `English name: ` | `英文名：` |
| `SERVINGS_PROMPT` | `Servings [{servings}]: ` | `份数 [{servings}]：` |
| `TAGS_PROMPT` | `Tags, separated by commas: ` | `标签，用逗号分隔：` |
| `INGREDIENTS_PROMPT` | `Ingredients, one per line, as "name quantity". An empty line ends the list:` | `食材，每行一个，写“名称 数量”，空行结束：` |
| `ZH_STEPS_PROMPT` | `Chinese steps, one per line. An empty line ends the list:` | `中文步骤，每行一步，空行结束：` |
| `EN_STEPS_PROMPT` | `English steps, one per line. An empty line ends the list:` | `英文步骤，每行一步，空行结束：` |
| `EN_STEPS_OPTIONAL_PROMPT` | `English steps, one per line. An empty line ends the list (optional):` | `英文步骤，每行一步，空行结束（可以不写）：` |
| `NOT_AN_ID` | `"{id}" cannot be a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Windows device names, such as "con", are not IDs.` | `“{id}”不能用作菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。“con”这样的 Windows 设备名不能用作 ID。` |
| `ID_EXISTS` | `The recipe {id} already exists. Enter another ID, or run "recipe-menu edit {id}".` | `菜谱 {id} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {id}”。` |
| `NAME_NEEDED` | `A recipe needs a name in at least one language. Enter its English name.` | `菜谱至少要有一种语言的名称。请输入它的英文名。` |
| `SERVINGS_WRONG` | `Servings must be a whole number from 1 to 100, such as 2.` | `份数必须是 1 到 100 之间的整数，比如 2。` |
| `UNKNOWN_TAG`，一个标签时 | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`，多个标签时 | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |
| `NAME_AND_QUANTITY` | `Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".` | `请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。` |
| `UNKNOWN_INGREDIENT` | `The catalog has no "{name}". Enter a name from the catalog, or add it to the catalog first and then run add again.` | `目录里没有“{name}”。请输入目录里的名称，或先把它加入目录后再运行 add。` |
| `AMOUNT_NOT_A_NUMBER` | `The amount "{amount}" must start with a number of at most 15 digits, such as 300 or 1.5, or be "适量" or "to taste".` | `数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，或者写成“适量”或“to taste”。` |
| `AMOUNT_UNKNOWN_UNIT` | `Unknown unit "{unit}" in "{amount}".` | `数量“{amount}”里有未知单位“{unit}”。` |
| `AMOUNT_NO_UNIT` | `The amount "{amount}" has no unit, and the catalog gives "{ingredient}" no default unit. Write a unit after the number, such as "300 g".` | `数量“{amount}”没有单位，目录也没有给“{ingredient}”默认单位。请在数字后面写上单位，比如“300 g”。` |
| `AMOUNT_ZERO` | `The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".` | `数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。` |
| `STEPS_NEEDED` | `A recipe needs steps in at least one language. Enter at least one English step.` | `菜谱至少要有一种语言的步骤。请至少输入一步英文步骤。` |
| `SAVED` | `Saved {file}. The check found no problems.` | `已保存 {file}。检查没有发现问题。` |
| `SAVED_WITH_PROBLEMS` | `Saved {file}. The check found {problems}:` | `已保存 {file}。检查发现了 {problems}：` |
| `ERROR_COUNT`，一个时 | `{count} error` | `{count} 个错误` |
| `ERROR_COUNT`，多个时 | `{count} errors` | `{count} 个错误` |
| `WARNING_COUNT`，一个时 | `{count} warning` | `{count} 个警告` |
| `WARNING_COUNT`，多个时 | `{count} warnings` | `{count} 个警告` |
| `FIX_AND_CHECK` | `Fix the errors, then run "recipe-menu check".` | `改正错误后，运行“recipe-menu check”。` |
| `INPUT_ENDED` | `The answers ended before the recipe was complete. Nothing was saved.` | `回答在菜谱完成之前就结束了。没有保存任何东西。` |
| `APPEARED` | `Nothing was saved: {file} appeared while you answered. Run "recipe-menu add" again with another ID.` | `没有保存任何东西：你回答问题时出现了 {file}。请换一个 ID，再运行“recipe-menu add”。` |
| `NOTHING_SAVED` | `Nothing was saved.` | `没有保存任何东西。` |
| `LEFT_BEHIND` | `Nothing was saved, but add could not remove {file}. Delete it.` | `没有保存任何东西，但 add 没能删除 {file}。请删除它。` |

`SERVINGS_WRONG` 的文字和 `datafile` 的 `SERVINGS_NOT_A_NUMBER` 相同（F05 设计 3.1）。`UNKNOWN_TAG` 和 `NO_TAGS` 的文字和 `list` 的相同（F09 设计 2.2）。四条数量提示的文字和 `read_recipe` 的相同（F04 设计 2.6）。中文的各个提示、中文的 `UNKNOWN_INGREDIENT` 和 `SAVED`，以及英文的 `ID_PROMPT` 和 `ID_EXISTS`，都是原型里的行。

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `id` | 问题 1 的回答，去掉两端空白。 |
| `servings` | `context.settings.servings`，1 到 100 之间的 `int`。 |
| `value` | 问题 5 的回答里第一个找不到标签的部分，去掉两端空白。 |
| `tags` | 目录里各个标签的名称（各自作为 `BiText`，按目录的顺序）的 `and_list`，和 `list` 的一样（F09 设计 2.2）。 |
| `name` | 这一行食材的名称（选择 9）。 |
| `amount` | `WrongQuantity` 的 `text`：这一行的数量。 |
| `unit` | `WrongQuantity` 的 `unit`，比如 `cups`。 |
| `ingredient` | 这种食材的名称，作为它的 `BiText`，所以每种语言显示自己的名称。 |
| `file` | 在 `SAVED` 和 `SAVED_WITH_PROBLEMS` 里，是 `str(path)`，完整路径，比如 `C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml`。在 `APPEARED` 里，是 `str(creation.existing)`。在 `LEFT_BEHIND` 里，是 `str(creation.left[0])`。 |
| `problems` | 带错误个数的 `ERROR_COUNT` 和带警告个数的 `WARNING_COUNT`（各自作为 `BiText`，个数为 0 的不写）的 `and_list`：`1 error and 2 warnings` 和 `1 个错误和 2 个警告`。 |
| `count` | 在 `ERROR_COUNT` 里是错误的个数，在 `WARNING_COUNT` 里是警告的个数。 |

错误：

`cli` 在运行 `add` 之前报告命令行的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT` | 数据文件夹不是文件夹。因为 `add` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查它。 |
| 退出码 1，错误流上是设置的第一个错误和 `RUN_CHECK` | 设置有错误。 |
| 退出码 2，带 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "garlic-broccoli". Write "recipe-menu add".` | `add` 后面跟了一个词。 |
| 退出码 2，带没有选项时那种写法的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"add" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，带 F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行，比如 `catalog.toml, line 2`、`  The file cannot be read: a closing "]" is missing.` 和 `RUN_CHECK` | 目录或 `recipes/` 的列表有错误（第 1 和 2 步）。`add` 什么也不问。 |
| 退出码 1，错误流上是 `INPUT_ENDED` | 问题 1 之后输入结束（选择 4）。没有文件。 |
| 退出码 1，错误流上是 `APPEARED` | `create_file` 给出 `EXISTS`（选择 11）。没有文件。 |
| 退出码 1，错误流上是失败时的三行 | `create_file` 给出 `FAILED`（选择 11）。没有文件，或者只有 `LEFT_BEHIND` 写出的那个文件。 |
| 退出码 1，输出流上是保存后的那几行 | 保存后的检查发现了错误（选择 12）。文件仍然已保存。 |
| 退出码 130 | Ctrl+C。`add` 在最后一个回答之前不写文件，`create_file` 会删除它正在写的文件（选择 4）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `add` 读一次 `catalog.toml`，列一次 `recipes/`，从输入流读回答，并写入输出流。最后一个回答之后，它通过 `create_file` 创建 `recipes/<id>.toml`（选择 11），再通过 `check_recipe` 把 `catalog.toml` 和新文件各读一次（选择 12）。它不改动别的文件，也不留下临时文件。在保存之前遇到错误、第一个回答为空、输入结束或按了 Ctrl+C 时，它不写文件。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`，`home` 是它外面的一个空的临时文件夹。`add` 运行 `main`，回答放在一个流里，每个后面跟一个换行。第一次运行是 v0.2-S09，接着检查它写出的文件。第二次运行给出 v0.2-S10 里每种错误的回答。第三次运行不写英文名和英文步骤，所以它的检查发现两个警告。最后几次运行分别在问题 2 之后输入结束、第一个回答为空，以及完全没有回答。

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def add(answers: list[str], *extra: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["add", "--data", str(folder.root), *extra],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        stdin=io.StringIO("".join(f"{answer}\n" for answer in answers)),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


chinese = [
    "garlic-broccoli",
    "蒜蓉西兰花",
    "Garlic broccoli",
    "",
    "快手, 素",
    "西兰花 300 g",
    "大蒜 4 瓣",
    "橄榄油 1 tbsp",
    "食用油 1 tbsp",
    "盐 适量",
    "",
    "西兰花切小朵，焯水 1 分钟，捞出沥干。",
    "大蒜切末，热油爆香。",
    "倒入西兰花翻炒，加盐调味。",
    "",
    "Cut the broccoli into florets. Blanch them for 1 minute and drain.",
    "Mince the garlic, and fry it in the hot oil until fragrant.",
    "Add the broccoli, stir-fry it, and season with salt.",
    "",
]
broccoli = folder.recipe_file("garlic-broccoli")
assert add(chinese, "--lang", "zh") == (
    0,
    [
        "菜谱 ID（也是文件名）：garlic-broccoli",
        "中文名：蒜蓉西兰花",
        "英文名：Garlic broccoli",
        "份数 [2]：",
        "标签，用逗号分隔：快手, 素",
        "食材，每行一个，写“名称 数量”，空行结束：",
        "  西兰花 300 g",
        "  大蒜 4 瓣",
        "  橄榄油 1 tbsp",
        "  目录里没有“橄榄油”。请输入目录里的名称，或先把它加入目录后再运行 add。",
        "  食用油 1 tbsp",
        "  盐 适量",
        "  ",
        "中文步骤，每行一步，空行结束：",
        "  西兰花切小朵，焯水 1 分钟，捞出沥干。",
        "  大蒜切末，热油爆香。",
        "  倒入西兰花翻炒，加盐调味。",
        "  ",
        "英文步骤，每行一步，空行结束（可以不写）：",
        "  Cut the broccoli into florets. Blanch them for 1 minute and drain.",
        "  Mince the garlic, and fry it in the hot oil until fragrant.",
        "  Add the broccoli, stir-fry it, and season with salt.",
        "  ",
        f"已保存 {broccoli}。检查没有发现问题。",
    ],
    [],
)
assert broccoli.read_bytes() == "\n".join(
    [
        'name = { zh = "蒜蓉西兰花", en = "Garlic broccoli" }',
        "servings = 2",
        'tags = ["快手", "素"]',
        "",
        "ingredients = [",
        '  { item = "西兰花", amount = "300 g" },',
        '  { item = "大蒜", amount = "4 瓣" },',
        '  { item = "食用油", amount = "1 tbsp" },',
        '  { item = "盐", amount = "适量" },',
        "]",
        "",
        "[steps]",
        "zh = [",
        '  "西兰花切小朵，焯水 1 分钟，捞出沥干。",',
        '  "大蒜切末，热油爆香。",',
        '  "倒入西兰花翻炒，加盐调味。",',
        "]",
        "en = [",
        '  "Cut the broccoli into florets. Blanch them for 1 minute and drain.",',
        '  "Mince the garlic, and fry it in the hot oil until fragrant.",',
        '  "Add the broccoli, stir-fry it, and season with salt.",',
        "]",
        "",
    ]
).encode("utf-8")

english = [
    "egg-fried-rice",
    "蛋炒饭",
    "Egg fried rice",
    "0",
    "two",
    "3",
    "breakfast",
    "quick, staple",
    "Rice 1 cups",
    "Rice 300 g",
    "Egg 3",
    "Peanut 30 g",
    "Scallion 1 stalk",
    "Salt to taste",
    "Cooking oil 2 tbsp",
    "",
    "鸡蛋打散。",
    "热油炒蛋，加米饭和葱花翻炒。",
    "",
    "Beat the eggs.",
    "Scramble the eggs, then stir-fry them with the rice and scallion.",
    "",
]
servings = "Servings must be a whole number from 1 to 100, such as 2."
tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
peanut = 'The catalog has no "Peanut". Enter a name from the catalog, '
peanut += "or add it to the catalog first and then run add again."
rice = folder.recipe_file("egg-fried-rice")
code, lines, errors = add(english)
assert (code, errors) == (0, [])
assert lines[3:16] == [
    "Servings [2]: 0",
    servings,
    "Servings [2]: two",
    servings,
    "Servings [2]: 3",
    "Tags, separated by commas: breakfast",
    f'Unknown tag "breakfast". {tags}',
    "Tags, separated by commas: quick, staple",
    'Ingredients, one per line, as "name quantity". An empty line ends the list:',
    "  Rice 1 cups",
    '  Unknown unit "cups" in "1 cups".',
    "  Rice 300 g",
    "  Egg 3",
]
assert lines[16:18] == ["  Peanut 30 g", f"  {peanut}"]
assert lines[-5] == "English steps, one per line. An empty line ends the list (optional):"
assert lines[-1] == f"Saved {rice}. The check found no problems."
assert rice.read_text(encoding="utf-8").splitlines()[:7] == [
    'name = { zh = "蛋炒饭", en = "Egg fried rice" }',
    "servings = 3",
    'tags = ["quick", "staple"]',
    "",
    "ingredients = [",
    '  { item = "Rice", amount = "300 g" },',
    '  { item = "Egg", amount = "3" },',
]

partly = ["scallion-egg", "葱花蛋", "", "", "快手，quick", "鸡蛋 3", "葱 2", ""]
partly += ["鸡蛋打散，加葱花煎熟。", "", ""]
egg = folder.recipe_file("scallion-egg")
relative = Path("recipes", "scallion-egg.toml")
code, lines, errors = add(partly)
assert (code, errors) == (0, [])
assert lines[-5:] == [
    f"Saved {egg}. The check found 2 warnings:",
    f"  {relative}, name",
    "    No English name. Commands show the Chinese name instead.",
    f"  {relative}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
]
assert egg.read_text(encoding="utf-8").splitlines() == [
    'name = { zh = "葱花蛋" }',
    "servings = 2",
    'tags = ["快手"]',
    "",
    "ingredients = [",
    '  { item = "鸡蛋", amount = "3" },',
    '  { item = "葱", amount = "2" },',
    "]",
    "",
    "[steps]",
    "zh = [",
    '  "鸡蛋打散，加葱花煎熟。",',
    "]",
]

ended = "The answers ended before the recipe was complete. Nothing was saved."
assert add(["new-dish", "新菜"]) == (
    1,
    ["Recipe ID (also the file name): new-dish", "Chinese name: 新菜", "English name: "],
    [ended],
)
assert not folder.recipe_file("new-dish").exists()
assert add([""], "--lang", "zh") == (0, ["菜谱 ID（也是文件名）："], [])
assert add([]) == (0, ["Recipe ID (also the file name): "], [])
assert len(list(folder.recipes.iterdir())) == 10
```

## 3. 对已有接口的修改

F15 给四个已实现的模块加东西。架构 5.2 计划了输入流：“在 v0.2，F15 加上输入流”到 `Context`，F05 设计第 2 节和 F14 设计第 2 节也为 `main` 计划了它。架构 3 计划 `add` 复用 `check` 来检查一个菜谱，F07 设计第 2 节把它需要的名称留给 F15 决定。`use_utf8_input` 是 F02 的 `use_utf8` 在输入一侧的对应函数，放在负责控制台流的 `text` 里。F01 到 F14 导出的名称，没有哪个调用会失效：新字段有默认值，`main` 的新参数是可选的，`text` 和 `check` 只是多了名称。需求已经写到 `add`，所以不需要 `[docs]` PR 来批准这些添加。架构师在这份设计里审查它们，就像审查 F14 的添加一样。ADR-0004 说 `cli` 请 `text` 把 stdout 和 stderr 设成 UTF-8。是否给 ADR-0004 为 stdin 加一句话，由架构师决定。

1. `app`：`Context` 多了字段 `input`（3.1）。现在两个上下文的八个字段都相等时才相等，流和生成器按对象比较。
2. `cli`：`main` 多了参数 `stdin`（3.2），`COMMANDS` 在 `SEARCH_COMMAND` 之后多了 `ADD_COMMAND`（选择 1）。
3. `text`：`use_utf8_input`（3.3）。
4. `check`：`check_recipe`（3.4）和 `problem_block`（3.5）。`check` 的报告用 `problem_block` 写出它的两块，所以它的输出不变，F07 的测试仍然成立。

F15 验收时，设计之外还有这些修改：

- 产品经理在 F05 原型的两段帮助“Help in English”和“Help in Chinese”里，在 `search` 那一行后面加上 `add` 那一行，并修改它们的说明，写明帮助也列出 `add`，F16 加上 `edit`。测试经理在 F14 验收时裁定，这两段显示已验收功能的帮助。
- 测试经理更新 v0.2-S14 要求的帮助，以及 v0.2 测试计划里的规则“Answers to `add`”（第 2 节）。

已验收功能的这个测试要改，第 2 节说明在哪个 PR 里改：

- F11-T01（`test_f11_t01_the_menu_new_command_creates_the_file_and_the_help_lists_it`）把真实 `COMMANDS` 的帮助里 `search` 那一行后面的两行当作 `menu new` 和 `menu show` 的两行。有了 mock 的这一项，`search` 后面那一行是 `add` 的。mock PR 之前的一个修测试的 PR 让它按开头找到 `menu new` 那一行。按 C 点的做法 2，F11-T01 成立，不修改任何测试。

这些测试仍然成立。`add` 的第一格占 3 列，所以两张表的第二列仍在第 24 列之后。F07-T17 和 F13-T01 按开头找到它们的那一行，把它的文字所在的列和 `--lang en|zh` 的比较。F08-T14 检查 `check` 跟在 `init` 后面，F09-T01 检查 `list` 和 `show` 跟在 `check` 后面，F10-T01 检查 `search` 跟在 `show ID` 后面，F14-T01 检查 `menu suggest` 跟在 `menu show` 后面，`add` 那一行都不在它们之间。F09-T19、F11-T27、F11-T32、F11-T35、F13-T22、F13-T27、F14-T21 和 F14-T31 拿真实 `COMMANDS` 的一份帮助和另一份比较。`add` 是一个词，所以 `recipe-menu menu` 仍然只列出三个 `menu` 命令，这是 F11-T32（用 v0.1 的命令）和 F14-T21 的要求。F05-T10 和 F05-T11 比较设置的键，F15 不加键。F05 到 F14 的测试运行它们自己的命令，用六个或七个值创建上下文，也不比较除了新字段以外都相等的两个上下文。不带 `stdin` 调用 `main` 的测试得到 `sys.stdin`，pytest 把它换成了一个不是 `io.TextIOWrapper` 的对象，所以 `use_utf8_input` 不改动它，除了 `add` 也没有命令读它。测试的 `run_module` 把 `PYTHONIOENCODING` 设成 `ascii`，`use_utf8_input` 仍然让 `python -m recipe_menu add` 按 UTF-8 读管道。没有测试运行 `add`，在 mock 之前它给出 `Unknown command "add".`。

F15 按各自设计的规定使用这些接口，不修改其中任何一个：

- F01 的 `Quantity`、`Unit`、`WrongQuantity`、`WrongQuantityReason` 和 `parse_quantity`。
- F02 的 `BiText`、`Lang`、`Message`、`Plural` 和 `and_list`。
- F03 的 `DataFolder`（以及 `recipe_file` 和 `relative`）、`Problem`、`Severity`、`Catalog`（以及 `find_ingredient` 和 `find_tag`），以及 `read_catalog`。
- F04 的 `is_recipe_id`、`list_recipe_ids` 和 `read_recipe`，最后一个通过 `check_recipe` 使用。
- F05 在 `app` 里的 `Arguments`、`Command`、`Context`、`FolderUse`、`first_error`、`problem_lines` 和 `stop_at_error`，在 `datafile` 里的 `MIN_SERVINGS` 和 `MAX_SERVINGS`，在 `settings` 里的 `Settings`，以及在 `cli` 里的 `COMMANDS` 和 `main`，加上 3.1 和 3.2 的添加。
- F07 的 `CHECK_COMMAND`，加上 3.4 和 3.5 的添加。
- F11 在 `datafile` 里的 `FileOutcome`、`FileCreation` 和 `create_file`。

### 3.1 `Context.input`

- 模块：app
- 功能：命令的输入流（[架构 5.2](../../architecture.zh-CN.md#52-值) 和 [8](../../architecture.zh-CN.md#8-命名和编码规范)）。`cli` 传入标准输入（3.2），测试传入一个装着回答的流。`add` 从它读回答（选择 4）。

签名：

```python
@dataclass(frozen=True, slots=True)
class Context:
    lang: Lang
    folder: DataFolder
    settings: Settings
    out: TextIO
    err: TextIO
    today: date
    random: Random = field(default_factory=lambda: Random(0))
    input: TextIO = field(default_factory=io.StringIO)
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `input` | `TextIO` | 命令从中读行的流。 | 打开的。`cli` 创建上下文时，是 `main` 得到的流，否则是 `sys.stdin`（3.2）。不传时，每个上下文得到一个新的空 `io.StringIO`，所以读取的命令马上读到输入结束。它给出的文字可以编码成 UTF-8。 |

其他字段保持它们的含义和约束（F05 设计 2.4，F14 设计 3.3）。`io` 是标准模块，`field` 是 `dataclasses.field`。

- 返回值：一个 `Context`。两个上下文的八个字段都相等时才相等，流和生成器按对象比较。所以各自创建了默认流的两个上下文不相等。`Context` 可以求哈希。

错误：无

- 副作用：无。用默认值创建上下文时会创建一个空的 `io.StringIO`，它不读取外部世界的任何东西。
- 性能指标：无

示例：

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
today = date(2026, 11, 10)
answers = io.StringIO("garlic-broccoli\n")
context = Context(Lang.EN, folder, Settings(), out, err, today, input=answers)
assert context.input is answers
assert context.input.readline() == "garlic-broccoli\n"
first = Context(Lang.EN, folder, Settings(), out, err, today)
second = Context(Lang.EN, folder, Settings(), out, err, today)
assert first.input is not second.input
assert first.input.readline() == second.input.readline() == ""
assert first != second
```

### 3.2 `main`：参数 `stdin`

- 模块：cli
- 功能：让测试传入命令的回答（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)：只有 `cli` 读控制台流）。`main` 把这个流放在 `Context.input` 里传给命令（3.1）。

签名：

```python
def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    today: date | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    commands: Sequence[Command] | None = None,
    random: Random | None = None,
    stdin: TextIO | None = None,
) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `stdin` | `TextIO` 或 `None` | 命令的输入流。 | `None` 给出调用过 `use_utf8_input`（3.3）之后的 `sys.stdin`，就像 `stdout` 为 `None` 时给出调用过 `use_utf8` 之后的 `sys.stdout`。 |

其他参数保持它们的含义和约束（F05 设计 2.9，F14 设计 3.4）。mock 加上这个参数，但不把它传下去（第 2 节），所以传下去的是实现。

- 返回值：F05 设计 2.10 的退出码，和以前一样。在 F05 设计 2.10 的第 10 步，`Context` 带着这个输入流。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `commands` 违反它的约束，和以前一样（F05 设计 2.9）。 |

- 副作用：F05 设计 2.9 的那些副作用。`stdin` 为 `None` 时，`main` 在启动时调用一次 `use_utf8_input(sys.stdin)`，它不从流里读任何东西。`main` 自己从不读这个流。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`，`home` 是它外面的一个空的临时文件夹。`ECHO` 代表一个读一行的命令。

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run_echo(context: Context, arguments: Arguments) -> int:
    context.out.write(context.input.readline().upper())
    return 0


ECHO = Command(("echo",), Message("Repeat a line.", "重复一行。"), run_echo)
out = io.StringIO()
code = main(
    ["echo", "--data", str(folder.root)],
    environ={},
    home=home,
    today=date(2026, 11, 10),
    stdout=out,
    stderr=io.StringIO(),
    commands=[ECHO],
    stdin=io.StringIO("salt to taste\n"),
)
assert (code, out.getvalue()) == (0, "SALT TO TASTE\n")
```

### 3.3 `use_utf8_input`

- 模块：text
- 功能：让控制台输入流按 UTF-8 读取，这样不管代码页是什么，`add` 都能读通过管道传来的中文回答（ADR-0004，选择 4）。启动时，`cli` 对 `sys.stdin` 调用它，就像对 `sys.stdout` 和 `sys.stderr` 调用 `use_utf8` 一样（F02 设计 2.10）。

签名：

```python
def use_utf8_input(stream: TextIO) -> None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `stream` | `TextIO` | 一个输入流，比如 `sys.stdin`。 | 打开的，而且还没有从中读过任何东西。第一次读取之后，`reconfigure` 既不能设置编码，也不能设置换行方式，会抛出 `io.UnsupportedOperation`。 |

- 返回值：无

错误：无

- 副作用：
  - `stream` 是 `io.TextIOWrapper` 时（`sys.stdin` 就是），`use_utf8_input` 调用 `stream.reconfigure(encoding="utf-8-sig", errors="replace", newline=None)`。从此这个流按 UTF-8 解码，去掉开头的字节顺序标记，把每个不是 UTF-8 的字节变成 U+FFFD REPLACEMENT CHARACTER，所以读取从不因为字节而抛异常。在每个系统上，它的换行都变成通用换行：CR LF、单独的 CR 和 LF 都结束一行，这个流给出的每一行都以 LF 结束。
  - Python 只在 Windows 上用通用换行构建 `sys.stdin`。在 Linux 和 macOS 上，它只在 LF 处结束一行，并保留每个 CR；不带 `newline` 的 `reconfigure` 会保留这个设置，所以管道里以 CR LF 结束的一行会以 `"...\r\n"` 到达。所以在 Windows 上 `newline=None` 什么都不改，在 Linux 和 macOS 上它给出和 Windows 上一样的行。
  - 其他流，比如测试里的 `io.StringIO`，保持原样。
  - 在 Windows 控制台里，Python 通过控制台的 Unicode 接口读取，给出 UTF-8 字节，所以那里的代码页不起作用。调用之后，管道或重定向的文件按 UTF-8 读取。
- 性能指标：无

示例：

示例用 `newline="\n"` 构建这个包装流，和 Python 在 Linux 和 macOS 上构建 `sys.stdin` 的方式一样，所以第一行的 CR LF 显示出这个改动：不设置 `newline=None` 的话，那一行会以 `"\r\n"` 结束。

```python
import io

from recipe_menu.text import use_utf8_input

data = b"\xef\xbb\xbf" + "蒜蓉西兰花\r\n".encode() + b"\xffx\n"
stream = io.TextIOWrapper(io.BytesIO(data), encoding="cp1252", newline="\n")
use_utf8_input(stream)
assert (stream.encoding, stream.errors) == ("utf-8-sig", "replace")
assert stream.readline() == "蒜蓉西兰花\n"
assert stream.readline() == "\ufffdx\n"
answers = io.StringIO("西兰花 300 g\n")
use_utf8_input(answers)  # changes nothing
assert answers.readline() == "西兰花 300 g\n"
```

### 3.4 `check_recipe`

- 模块：check
- 功能：像 `check` 那样检查一个菜谱：用 `read_catalog` 给出的目录，通过 `read_recipe` 检查（F07 设计 2.2，第 2 和 5 步）。`add` 用它检查自己保存的文件（选择 12），F16 的 `edit` 可以用它检查你编辑过的菜谱。

签名：

```python
def check_recipe(folder: DataFolder, recipe_id: str) -> tuple[Problem, ...]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `recipe_id` | `str` | 菜谱的 ID，比如 `garlic-broccoli`。 | `is_recipe_id(recipe_id)` 为真（F04 设计 2.4）。它是 `list_recipe_ids` 给出的 ID（F04 设计 2.5），或者是调用者刚用 `create_file` 创建的文件的 ID（F11 设计 3.3）。`read_recipe` 读 `folder.recipe_file(recipe_id)` 时不列出文件夹，所以在 Windows 上它对 `tomato-egg` 也会打开 `Tomato-Egg.toml`（F04 设计 2.6）。`add` 满足这一点：它传入的是 `create_file` 刚创建的文件的 ID，而 `create_file` 拒绝了名称和它只有大小写不同的每个条目（选择 11）。 |

- 返回值：这个菜谱的问题，按这个顺序：`read_catalog(folder)` 的错误（F03 设计 2.8），然后是用 `read_catalog` 给出的目录（没有目录时用 `None`）调用 `read_recipe(folder, catalog, recipe_id)` 得到的问题（F04 设计 2.6）。目录有错误时，`read_recipe` 找不到食材和标签，所以检查写出这个错误，而不是报告菜谱没有问题。空元组表示这个菜谱没有问题。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `is_recipe_id(recipe_id)` 为假。`check_recipe` 在读任何文件之前检查这一点。 |

- 副作用：通过 `read_catalog` 和 `read_recipe` 把 `catalog.toml` 和 `recipes/<id>.toml` 各读一次。它不列出文件夹，也不写任何东西。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`。

```python
from pathlib import Path

from recipe_menu.commands.check import check_recipe
from recipe_menu.lang import BiText, Lang

assert check_recipe(folder, "tomato-egg") == ()
problems = check_recipe(folder, "red-braised-pork")
assert [problem.place for problem in problems] == [BiText("steps", "步骤")]
mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
problems = check_recipe(folder, "mapo-tofu")
assert [problem.file for problem in problems] == [Path("recipes", "mapo-tofu.toml")]
assert problems[0].text(Lang.ZH) == "未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。"
folder.catalog.write_text("categories = [\n", encoding="utf-8")
problems = check_recipe(folder, "tomato-egg")
assert [problem.file for problem in problems] == [Path("catalog.toml")]

check_recipe(folder, "Tomato-Egg")  # raises ValueError
```

### 3.5 `problem_block`

- 模块：check
- 功能：用 `check` 报告的缩进显示问题的那些行：两个空格之后是文件和位置，四个空格之后是提示（F07 设计 2.2）。`check` 的报告用它写出各块，`add` 用它写出检查发现的问题（选择 12），F16 的 `edit` 可以用它写出原型里的那几行。

签名：

```python
def problem_block(problems: Iterable[Problem], lang: Lang) -> tuple[str, ...]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `problems` | `Problem` 值的可迭代对象 | 要显示的问题，按它们的顺序。 | 任意个，包括零个。 |
| `lang` | `Lang` | 各行的语言。 | 无 |

- 返回值：每个问题两行，按 `problems` 的顺序，不带换行：两个空格加上 `where`，然后四个空格加上 `what`，两者来自 `problem_lines(problem, lang)`（F05 设计 2.8）。没有问题时给出空元组。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.commands.check import problem_block
from recipe_menu.datafile import Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
MISSING = Message("The file is missing.", "文件不存在。")
mapo = Path("recipes", "mapo-tofu.toml")
problem = Problem.error(mapo, BiText("ingredient 3", "食材 3"), UNKNOWN, name="豆瓣酱")
missing = Problem.error(Path("catalog.toml"), None, MISSING)
assert problem_block([problem, missing], Lang.ZH) == (
    f"  {mapo}，食材 3",
    "    未知食材“豆瓣酱”。",
    "  catalog.toml",
    "    文件不存在。",
)
assert problem_block([], Lang.EN) == ()
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `add` 是架构 3 交给 F15 的命令模块，位于 `src/recipe_menu/commands/add/`，只导出 `ADD_COMMAND`。它只引用 `app`、`lang`、`units`、`text`、`datafile`、`catalog`、`recipes` 和 `check`。这些都在它那一行里，`add --> check` 也是架构 4 里的一个箭头。它从 `context.settings` 读默认份数，所以既不需要 `settings`、`menus`，也不需要 `shopping`。任务说明的第 4 点：第 3 节增加的正是架构 3 和 5.2 为 F15 规划的内容。`Context` 得到输入流，只由 `cli` 填入（架构 8）。掌管控制台流的 `text` 得到 `use_utf8_input`。`check` 得到 `check_recipe` 和 `problem_block`，因为架构 3 说 `add` 和 `edit` 复用 `check`，F07 设计第 2 节也把这两个名称留给了 F15。这两个名称放在 `check` 的一个新的内部文件里，并加入它的 `__all__`，所以每个新文件都只属于一个模块。`Context` 仍是带 `slots=True` 的冻结 dataclass，`input` 是带默认值的 `TextIO`，和 `out`、`err` 一样，所以符合架构 8 对值的规定。`add` 写的文件就是架构 5.1 的 `recipes/<id>.toml`，格式和 `recipes/choy-sum.toml` 相同，用 UTF-8、不带字节顺序标记、以 LF 换行。它通过 `create_file` 写入，这正是架构 6 给新文件规定的写法。文件的文本来自模板，加上对 TOML 基本字符串的转义，这是架构 2 允许的，所以不需要 TOML 写入器。`use_utf8_input` 设置的 `utf-8-sig`，正是架构 8 规定的读取编码。任务说明的第 2 点：`add` 可以调用 `context.input.isatty()`。这是对 `cli` 传进来的流的调用，和 `readline()` 一样，所以 `add` 自己不读控制台（架构 8）。测试能控制两个分支：`io.StringIO` 给出 false，`isatty` 给出 true 的流走另一个分支。任务说明的第 5 点，速度：在模型里，`cli` 没有引用新的标准模块。四个新文件（`add` 的三个和 `check` 的一个）在 `python -X importtime` 下各自用时 0.7 到 0.9 毫秒，合计约 3 毫秒；重新配置 stdin 用时 14 微秒。在新进程里运行 `import recipe_menu.cli` 的启动时间，差别没有超出噪声：在同一个文件夹里各跑 3 轮、每轮 21 次，模型的最小值是 163 到 170 毫秒，未改动的副本是 165 到 172 毫秒。备注 1，不阻塞：选择 14 的“约 1 毫秒”偏低。第 2 节为 `add` 规划的七个文件可能要几毫秒，仍然远低于 `check` 剩下的 172 毫秒。选择 14 可以改成“几毫秒”。版本 1.1 保持这些。它不改任何模块、文件、引用或值：`use_utf8_input` 仍在 `text` 里，只多了一个关键字参数，`add` 自己去掉 LF。备注 1 已采纳，选择 14 现在写的是“几毫秒”。在本次审查的沙箱里，在带 mock 的 main 上，`add` 的三个新文件在 `python -X importtime` 下 9 次运行的自身时间是 2.1 到 2.5 毫秒，加上 `check/_recipe.py` 的四个新文件是 3.0 到 4.5 毫秒。用 `newline=None` 对通过管道传入的 stdin 调用 `reconfigure` 用时 14 微秒。备注 5，不阻塞：“mock 的新文件花了 2 到 3 毫秒”对 `add` 的文件成立，对全部四个文件不成立。审查用的沙箱就运行在 Troy 的电脑上，所以“在审查用的沙箱里测得，不是在 v0.2 的发布测试里”比“不是在 Troy 的电脑上测的”更准确。这两点都不改变“几毫秒”这个结论。 |
| 遵守错误处理和命名约定 | 通过 | `read_catalog` 或 `list_recipe_ids` 的第一个错误通过 `first_error` 和 `stop_at_error` 让 `add` 停下，停在提任何问题之前，和 `list`、`menu suggest` 停下的方式一样。错误的回答不是数据里的错误：它在输出流上得到一条提示，然后再问一次。`INPUT_ENDED`、`APPEARED` 和保存失败时的三行写到错误流，`add` 以 1 结束。保存后的那些行无论退出码是什么都写到输出流，因为它们是一次检查的报告。架构 6 对 `check` 就是这样规定的，v0.2 测试计划的规则“`add` 和 `edit` 的报告”也这样理解。保存失败时的第一行按问题保存的方式给出文件，即相对于数据文件夹的路径；`SAVED`、`APPEARED` 和 `LEFT_BEHIND` 用完整路径给出文件。这两条规则都是架构 6 给的。所以 F15 和 `init`（ADR-0009）、`menu new`（ADR-0010）不同，不需要修改架构 6，也不需要 ADR；它给出保存失败的文件的方式和 `menu suggest` 相同（ADR-0011）。Ctrl+C 以 `KeyboardInterrupt` 传给 `cli`，得到 130；`create_file` 会删掉正在写的文件，所以不会留下写了一半的文件（架构 6）。输入提前结束后的退出码 1 符合架构 1，因为命令没有完成，脚本也能看出来。`run` 不捕获任何异常，所以符合对 `except` 子句的规定。名称符合架构 8。模块 `add` 用的是它的命令名。32 条提示是 `add/messages.py` 里 UPPER_SNAKE 命名的 `Message` 和 `Plural` 常量，数量用 `Plural`，列表用 `and_list`。`input`、`stdin` 和 `use_utf8_input` 分别对应 `out`、`stdout` 和 `use_utf8`。用 ruff 0.17.4 和项目的设置检查模型的 `Context`，字段 `input` 没有报出任何问题。任务说明的第 1 点：ADR-0004 不需要加一句话。它关于控制台的决定说的是 `cli` 请 `text` 把 stdout 和 stderr 设成 UTF-8，没有提到输入。`use_utf8_input` 把同一个决定用在只有 `add` 读取的那一个流上，选择 4 和 3.3 写明了理由，也写明了 Windows PowerShell 5.1 的情况。架构不变，所以 Troy 没有额外要决定的事。版本 1.1 保持这些。`newline=None` 是 `io.TextIOWrapper.reconfigure` 的参数，没有名称改变。3.3 的约束里新加的那句话成立。在 Windows 上用 Python 3.13.18、在 Linux 上用 3.10.12，在一次 `readline` 或 `read(1)` 之后，设置编码或 `newline` 的 `reconfigure` 会抛出 `io.UnsupportedOperation`。“错误：无”仍然正确：约束排除了这种调用，而 `cli` 在任何读取之前调用它，就像 `use_utf8` 的约束“已打开。”也不带错误一样（F02 设计 2.10）。备注 6，不阻塞：CPython 只在流里还留有解码过的文字时才抛出。读完整个流的 `read()` 之后，或者 `readline` 给出空文字之后，这个调用什么也不抛，所以测试不能指望每次读取之后都会抛出。 |
| 不和已有接口重复 | 通过 | `add` 用 `is_recipe_id` 和 `list_recipe_ids` 的列表检查 ID，用 `Catalog.find_tag` 检查标签，用 `Catalog.find_ingredient` 和 `parse_quantity` 检查每种食材，用 `MIN_SERVINGS` 和 `MAX_SERVINGS` 检查份数，和 F03、F04、F05 的设计规划的一样。它通过 `create_file` 写入，通过 `stop_at_error` 停下。这些它都没有重写。`read_servings` 接收的是 TOML 值和 `Report`，不是输入的回答，所以 `add` 自己检查回答，但用的是共用的范围。`problem_block` 把带缩进的两行从 `check` 的报告里提出来，`check` 的报告再用它写出各块，所以缩进只在一个地方定义。`check_recipe` 是新的：没有接口检查单个菜谱。TOML 转义也是新的，因为没有别的模块把你输入的文字写进 TOML 文件。以后的功能需要它时，可以把它移到 `datafile`。`SERVINGS_WRONG`、`UNKNOWN_TAG`、`NO_TAGS` 和四条数量提示的副本都是内部提示，架构 8 让每个模块各自保存，F13 和 F14 的审查也接受了这种做法。备注 2，不阻塞：`add` 带来了 `UNKNOWN_TAG` 和 `NO_TAGS` 的第三份副本（前两份在 `browse` 和 `suggest`），以及“读取目录、在第一个错误处停下”的第六份副本。F13 和 F14 的审查提到的那个后续 `[refactor]` PR 可以把它们共用起来。版本 1.1 不增加接口。`use_utf8_input` 设置换行方式，`add` 只去掉 LF，所以没有哪个模块自己处理 CR。 |
| 只依赖排序在前面的功能 | 通过 | F15 使用 F01 的 `parse_quantity` 和 `WrongQuantity`、F02 的 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`、F05 的 `app`、`cli` 和份数范围、F07 的 `check`、F11 的 `create_file`、`FileOutcome` 和 `FileCreation`，以及 F14 定下的 `Context` 和 `main` 的形式。它复制了 F04、F05 和 F09 的文字。这些功能都排在 F15 前面，都已在 main 上验收，硬依赖 F05 也已验收。F03、F04 和 F07 是 F15 那一行的软依赖。F01、F02、F11 和 F14 通过共享模块 `units`、`text`、`datafile`、`app` 和 `cli` 进入 F15，这些模块指向更早的功能，这是架构 4 允许的。`ID_EXISTS` 只是以文字形式提到 F16 的 `recipe-menu edit`，和 Troy 批准的 F15 原型一样，所以不增加对 F16 的依赖。F16 验收之前，这个命令会给出 `未知命令“edit”。`，而 v0.2 会同时发布两者。给 F16 的规划不约束后面的设计。F15 只需要标准库，所以 R16 没有要审查的。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。版本 1.1 不增加依赖：`newline` 是标准模块 `io` 的参数。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写下了模块之间的每个假设。文件必须能通过 `read_recipe` 按你输入的样子读回来，模型证实了这一点。含有 `"`、`\`、制表符、U+007F、U+3000 和 U+2028 的文字通过 `tomllib` 原样读回。回答里有引号、反斜杠和制表符的一次 `add` 运行，写出的文件被 `read_recipe` 读成同样的文字，只有预期的那条警告。`add` 检查每个食材行时用的 `find_ingredient` 和 `parse_quantity` 和 `read_recipe` 用的相同，所以保留下来的行在保存后不会出问题，`Salt TO taste` 也一样。选择 2 是对的：`list_toml_files` 统计所有种类的条目，所以没有错误的列表包含 `create_file` 会拒绝的每个名称，在 Windows 上也是如此。`create_file` 会再列一次 `recipes/`，所以你回答问题时出现的条目会得到 `EXISTS` 和 `APPEARED`。在 Windows 上，在那次列出和打开文件之间出现的文件夹会得到 `FAILED` 和“拒绝访问”，这是 PR #76 的代码审查发现的；这时失败的几行说什么也没有保存，这是对的。回显只取决于 `context.input.isatty()`。`cli` 只在 `main` 没有得到 `stdin` 时调用 `use_utf8_input`，而 pytest 的 `sys.stdin` 不是 `io.TextIOWrapper`，所以测试不会改动任何流。架构师核实了这两点。在模型上，设置 `PYTHONIOENCODING=ascii` 后通过管道运行 `python -m recipe_menu add --lang zh`，带字节顺序标记、以 CR LF 换行的 UTF-8 回答按输入的样子读入，不是 UTF-8 的字节变成了 U+FFFD。备注 3，不阻塞：3.4 的约束只说 `is_recipe_id(recipe_id)` 为真。`read_recipe` 还要求 ID 是 `list_recipe_ids` 给出的，因为在 Windows 上它会为 `tomato-egg` 打开 `Tomato-Egg.toml`。`add` 满足这个要求，因为 `create_file` 刚刚用正好这个名称创建了文件，并且拒绝了这个名称的其他大小写形式。3.4 可以加上：ID 是 `list_recipe_ids` 给出的，或者是调用方刚用 `create_file` 创建的文件的 ID，这样 F16 和以后的调用方也会遵守。版本 1.1 去掉了一处耦合。在 1.0 下，`add` 在 Linux 和 macOS 上读到的行取决于 Python 在那里怎样构建 `sys.stdin`：通过管道传来的 CR LF 行保留着 CR，只是 `add` 去掉换行符的方式让 CR 不出现在回显里。现在 `use_utf8_input` 在每个系统上设置换行方式，`add` 只去掉 LF，这正是架构师的 AR5 回答所推荐的。架构师核实了 3.3 新加的那一条。在 CPython 3.13 里，`create_stdio` 在 Windows 上用 `newline=None` 构建 `sys.stdin`，在其他每个系统上用 `newline="\n"`。在 Linux 上（WSL Ubuntu 22.04，Python 3.10.12），通过管道传入的字节 `a\r\nb\rc\nd` 在不调用 `reconfigure` 和用 1.0 的调用时，都只在 LF 处结束一行，并保留每个 CR，比如 `"b\rc\n"`。用 1.1 的调用时，它们给出 `"a\n"`、`"b\n"`、`"c\n"` 和 `"d"`。在 Windows 上用 Python 3.13.18，三种情况都和 1.1 的调用一样分行、结束每一行。所以 Windows 上什么都不变，Linux 和 macOS 现在读到和 Windows 一样的行，回显在任何系统上都没有 CR。备注 3 已采纳：3.4 给出 F04 设计 2.6 的约束，并加上 `create_file` 刚创建的文件。这个文件的名称正好是 `<id>.toml`，这正是 F04 的约束所保护的。 |
| 修改已实现的接口时走了变更流程 | 通过 | 这个 PR 只添加两个设计文件。第 3 节增加的只有架构 3 和 5.2、F05 设计第 2 节、F07 设计第 2 节以及 F14 设计第 2 节为 F15 规划的内容：`Context` 里一个带默认值的字段，`main` 的一个可选关键字参数，以及新名称 `use_utf8_input`、`check_recipe` 和 `problem_block`。F01 到 F14 导出名称的调用都不会出错。架构 4 说 `COMMANDS` 里的那一项是命令功能对 `cli` 做的唯一修改。参数 `stdin` 是架构 5.2 规划的输入流在 `cli` 这一侧的部分，和 F14 的 `random` 一样，所以不需要修改架构。需求已经写明了 `add`，所以需求不变，由架构师在这里审查这些增加，就像审查 F14 的增加那样。任务说明的第 3 点：用第 3 节的模型并把 `ADD_COMMAND` 放在 `SEARCH_COMMAND` 后面，在 Windows 上不运行 F07-T25 和 F10-T21，整个测试集的结果是 614 个通过、1 个失败、4 个跳过。唯一的失败是第 3 节列出的 F11-T01，4 个跳过是 main 上只在 Linux 运行的用例。任务说明列出的其他测试都通过：F07-T17、F08-T14、F09-T01、F10-T01、F11-T27、F11-T35、F14-T01、F14-T21 和 F14-T31，以及 PR #105 修改过的六个测试 F05-T10、F05-T11、F11-T32、F13-T01、F13-T22 和 F13-T27。报告改由 `problem_block` 写出后，F07 对报告的测试仍然通过。模型的帮助有 2.1 的 23 行，两种语言的第二列都从第 24 列之后开始。F07-T25 和 F10-T21 在 PT01 数据文件夹上给 `check` 和 `search` 计时。在审查用的沙箱里，它们在未改动的副本上也失败了，中位数是 1.08 秒和 1.09 秒，所以这个沙箱无法给 PT01 计时。v0.2 的发布测试会在 Troy 的电脑上运行 PT01。所以第 2 节的计划成立：在 mock 之前用一个 test-fix PR 修改 F11-T01；mock 的 10 个文件和实现的约 650 行需要第 2 节给出的软限制理由，和 F14 一样。版本 1.1 只修改 F15 自己的接口（main 上是它们的 mock），不修改 F01 到 F14 的任何接口。PR 4 的测试都和它不冲突：这些测试通过 `io.StringIO` 给 `add` 以 LF 结束的行，或者通过包装流、或通过管道给出 CR LF，而管道的输出要先把 CR LF 变成 LF 再比较。F15-T04 用 1.1 调用的模型能通过，用 1.0 的也能通过，所以它分不出两者。它的包装流和 F15-T03 的包装流都用 `io.TextIOWrapper` 默认的 `newline`，这个默认值在每个系统上都是 `None`，不只是在 CI 上。F15-T27 通过管道传入 CR LF，但 `pipe_module` 把输出里的 `"\r\n"` 变成 `"\n"`，所以在 Linux 上它也会掩盖回显保留下来的 CR。用 `newline="\n"` 构建这些包装流的 test-fix，能在每个系统上发现漏掉的 `newline=None`。备注 7，不阻塞：3.4 的新约束不包括 F15-T05 的调用 `check_recipe(second, "garlic-broccoli")`，因为没有哪次列出给出过这个 ID，也没有这个 ID 的文件。结果仍然是确定的：对缺失的文件，`read_recipe` 在每个系统上都给出 `FILE_MISSING`（F04 设计 2.6），所以这个测试成立。测试方案的更新可以说明，这个用例代表列出之后被删除的文件，F04 设计 2.6 包括了这种情况。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | PR #113 开头的摘要（提交 4d9b1e2）就是任务说明里的那一份，它和设计说的一致。“对你有什么变化”按选择 3 的顺序给出八个问题，写了默认份数、两种语言都可以的标签、写成名称、空格和数量的食材行，以及结束一个列表的空行。它写了错误回答之后的提示和再问一次、被丢掉的错误食材行，以及第一个问题直接回车时什么也不保存（选择 3 到 9）。它说文件和其他菜谱文件格式相同，内容是输入的回答，不带备注，从不覆盖文件，然后 `add` 会检查它（选择 10 到 12）。第 1 到 3 条就是要点 A、B 和 C，每一条都有方案和带理由的推荐。要点 A 的数目成立：2.2 有 32 条提示，其中 7 条是副本，1 条整条来自原型（`ID_PROMPT`），其余 24 条。三条风险就是选择 4 和 11 里的风险。架构师没有发现别的需要 Troy 决定的事。备注 1 到 4 都不需要 Troy 决定，对任务说明第 1 和第 2 点的回答也不修改架构。在 PR 描述上运行 troy-check 的 `summary.py` 里的检查，全部通过。中文部分有 850 个字符，英文部分有 1,961 个，都在 R22 的 2,000 以内。两部分都按顺序有三个部分，3 条里每一条都有推荐，也都不含内部编号。备注 4，不阻塞：“或者发现的警告”（“or the warnings”）漏掉了选择 12 允许的错误，即 `add` 等待回答时目录被改了的情况。这时文件仍然保存着，`add` 给出 1。改成“或者发现的问题”（“or the problems it found”）就能包括它。英文部分还剩 39 个字符。版本 1.1 不改变 Troy 看到的或要决定的任何东西。在 Windows 上，标准输入的行、回显、控制台和文件都和以前一样。选择 14 改正了一个估计，3.4 写明了 `add` 本来就满足的约束。所以 PR #118 不需要给 Troy 的摘要，要点 A 到 C 仍按 Troy 批准的那样。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0004 和 ADR-0009 到 ADR-0011、F03、F04、F05、F07、F11 和 F14 的设计、F15 原型、v0.2 测试计划，以及任务说明的六点，检查了 15 个选择、第 3 节和要点 A 到 C。两个文件有同样的 13 个标题和 158 个表格行，以及 17 个代码块，每个都和镜像里的相同，没有控制字符或不可见字符。13 个 `python` 代码块都能解析。架构师在 Windows 上用 Python 3.13.18，在 main 的 `src/` 的一份副本里按第 2 节和第 3 节建了模型，在 `tests/data/example/` 的新副本上运行了 7 个示例。全部 48 个断言和那一个 `# raises` 都成立。模型的帮助和 2.1 的两份帮助逐行相同。第一项、第五项和第六项给出了管道运行、往返读写、启动时间和整个测试集的结果。没有运行 Linux 上的结果、Windows 控制台（用输入法输入、退格、`chcp 437` 和在提示处按 Ctrl+C）以及 PT01。备注 1 到 4 不阻塞。 | 通过。Troy 批准这份设计时，主会话把要点 A 到 C 交给 Troy 决定（R18）。没有哪个要点修改架构，所以之后没有架构师的 `[docs]` PR。接口设计师可以在修订时采纳备注 1、3 和 4，也可以不改。备注 2 留给后续的 `[refactor]` PR。给测试经理的任务说明（任务说明的第 6 点）：设计解决了 v0.2 测试计划“本方案在等设计的地方”里 F15 的各点。模型证实了 v0.2-S10 的英文行、v0.2-S11 的退出码 0、`Cooking oil 2 tbsp` 和 `Salt to taste` 的拆分，以及按 UTF-8 读取管道。测试经理按设计所说，更新 v0.2-S14 的帮助、规则“回答 `add` 的问题”和 v0.2-S15 的第 2 步。 |
| 1（版本 1.1） | 没有阻塞问题。架构师用 `git diff origin/main...HEAD` 审查了 PR #118 里从版本 1.0 到 1.1 的修改。在两个文件里，它只修改了选择 4、选择 14、2.2 里回显的两行、3.3、3.4、版本和修改记录。每处修改都和架构师的 AR5 回答或备注 1 和 3 一致。状态仍保留 Troy 的批准，和 F01 设计的修订一样。两个文件仍然有同样的 13 个标题、同样的表格行（每行的单元格数也相同），以及 17 个代码块，每个都和镜像里的相同，没有控制字符或不可见字符。13 个 `python` 代码块都能解析。架构师用 1.1 调用的模型，在 Windows 上用 Python 3.13.18、在 Linux 上用 Python 3.10.12 运行了 3.3 的示例。用 `newline="\n"`、`newline=None` 和默认值构建的包装流，示例的四个断言都成立。用 1.0 的调用和 `newline="\n"` 时，第一行是 `"蒜蓉西兰花\r\n"`，和示例前面那句话说的一样。设计的其他部分都没有再说换行仍是通用换行。说回答“原样”或“按你输入的样子”的地方，现在只指控制台读到的内容和文件里的文字，和回显不冲突。没有在 macOS 和 Linux 控制台上运行，也没有运行实现。备注 5 到 7 不阻塞。 | 通过。主会话合并 PR #118。之后是主会话计划的测试方案更新和 test-fix。它们包括 F15-T04 里的单独 CR，以及 F15-T03、F15-T04 和 `tests/test_f15_values.py` 里 `_wrapped` 用 `newline="\n"` 构建的包装流。更新可以写明，选择 4 现在解决了测试方案第 4 节里“保留换行的流上以 CR LF 结束的回答行”那一行：回显保留 CR，回答不保留。它还可以让测试方案第 3 节和第 4 节里的“约 1 毫秒”和选择 14 一致，并采纳备注 7。开发者的实现 PR 让 `src/recipe_menu/text/_utf8.py` 里 `use_utf8_input` 的文档注释和 3.3 一致。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-19 | 初稿。 |
| 1.0 | 2026-11-20 | Troy 批准。 |
| 1.1 | 2026-11-20 | `use_utf8_input` 还设置 `newline=None`，让标准输入在每个系统上都以 LF 结束每一行，就像 Python 在 Windows 上已经做的那样。读取之后再设置会抛出 `io.UnsupportedOperation`，回答的回显只去掉末尾的 LF（3.3、选择 4、2.2）。选择 14 按测量结果说明 F15 给每个命令的启动增加几毫秒。`check_recipe` 的约束补充：ID 来自 `list_recipe_ids`，或者是调用者刚用 `create_file` 创建的文件的 ID（3.4）。在 Windows 上什么都不变。 |
