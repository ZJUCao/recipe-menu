---
troy-doc: "F09-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-13"
status: "Troy 已于 2026-11-13 批准"
mirror-of: "design.md"
---

# F09 列出和查看菜谱：接口设计

## 1. 功能

- 编号和名称：F09 列出和查看菜谱
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F01、F02、F04

## 2. 接口

F09 在 `src/recipe_menu/commands/browse/` 里构建命令模块 `browse`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.browse` 导出两个名称：`LIST_COMMAND`（2.1）和 `SHOW_COMMAND`（2.3），它的 `__init__.py` 在 `__all__` 里列出它们。你输入的命令是 `recipe-menu list`（2.2）和 `recipe-menu show`（2.4）。它们的提示放在 `src/recipe_menu/commands/browse/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F09 在它的 mock PR 里把这两个命令加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `CHECK_COMMAND` 之后。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F09 原型 `docs/prototypes/F09-list-show.md` 展示了这两个命令，F05 原型“The language from the settings”展示了按设置里的语言运行的 `list --tag`。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F09 提供的接口 |
| --- | --- |
| `recipe-menu list` 打印一张按 ID 排序的菜谱表。 | `recipe-menu list`（2.2）。它为 `read_recipes` 给出的每个菜谱写一行，按 ID 的顺序，也就是 `list_recipe_ids` 的顺序（F04 设计 2.5）。 |
| `--tag` 只保留带这个标签的菜谱。 | `LIST_COMMAND`（2.1）的选项 `--tag`。它接受任一种语言的标签名称，并用 `Catalog.find_tag` 找到这个标签（选择 4）。 |
| `recipe-menu show ID` 打印一个菜谱：名称、份数、标签、带备注的食材和步骤。 | `recipe-menu show`（2.4），以及 `SHOW_COMMAND`（2.3）的参数 `ID`。 |
| `--servings N` 换算数量。 | `SHOW_COMMAND` 的选项 `--servings`，从 1 到 100。`show` 用 F01 的 `Quantity.scale` 换算每个数量（选择 8）。 |
| `show` 按菜谱里用的单位显示数量（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | `Quantity.to_text`（F01 设计 2.11），它保留菜谱的单位。 |
| 名称、备注或步骤可以缺一种语言，这时命令会改为显示另一种语言（需求 3）。 | `BiText` 和 `Steps` 的回退，以及另一种语言的步骤的标题（选择 3）。 |
| 数据文件夹里有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`list` 和 `show` 都在 1 秒内完成（PT01，[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。 | 2.2 和 2.4 的性能指标，以及选择 10。 |

下面每个接口都遵守这些规则：

- `browse` 在包内只引用 `app`、`lang`、`units`、`text`、`datafile`、`catalog` 和 `recipes`。架构 3 里它那一行允许这些模块，它不需要 `settings`、`menus` 和 `shopping`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `browse` 只通过 F03 和 F04 的读取函数访问磁盘，这些函数又通过 `datafile` 读取（架构 8）。它不写任何文件（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 1](../../architecture.zh-CN.md#1-背景和约束)）。它只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西，也不保存状态。
- 两个命令都不用 `context.settings` 和 `context.today`。没有 `--servings` 时，`show` 显示菜谱自己的份数。设置里的份数属于菜单里没写份数的菜品（需求 3）。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。每个命令在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。`run` 只为命令行上的错误值抛出 `UsageError`，而且在读取任何文件、写出任何输出之前抛出（F05 设计第 2 节）。传到 `cli` 的任何其他异常都是 bug。
- `LIST_COMMAND` 和 `SHOW_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。F09 不增加值类型。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- `recipe-menu list` 和 `recipe-menu show` 有性能指标 PT01（选择 10）。每个命令把它需要的每个文件只读一次，并在读完最后一个文件后一次写出输出。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和 2.4 给出它们的规则。

1. **一个模块里的两个命令，在帮助里排在 `check` 之后。** 架构 8 把 `list` 和 `show` 放进模块 `browse`。F09 把 `LIST_COMMAND` 和 `SHOW_COMMAND` 加在 `COMMANDS` 里 `CHECK_COMMAND` 的后面，所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND)`，符合 F05 设计第 2 节的帮助顺序。两个命令都有 `FolderUse.READ`。所以数据文件夹不存在或设置有错误时，`cli` 不运行它们（F05 设计 2.5），和 v0.1-S20 与 v0.1-S22 的预期一致。`list` 声明选项 `--tag`。`show` 声明参数 `ID` 和选项 `--servings`。帮助保持 F05 的格式。有这四个命令时，最宽的第一格仍是 `--data FOLDER` 或 `--data 文件夹`，占 13 列，所以第二列从第 18 列之后开始，和 F07、F08 之后一样。2.1 给出各命令的那几行。有 v0.1 的八个命令时，帮助给出 F05 原型的两段输出。
2. **每个命令读什么，在哪里停下。** 每个命令只读它需要的文件（架构 8），顺序与 `check` 的步骤相同（F07 设计 2.2）：先是目录，然后是 `recipes/` 的列表，然后是菜谱。两个命令都不读常备清单和菜单。每个命令在每个读取函数的第一个错误处用 `stop_at_error` 停下，它写出这个问题和 `RUN_CHECK`，并给出 1。`check` 用相同的读取函数、相同的参数读这些文件，所以让命令停下的错误一定在 `check` 的错误里（F07 设计，选择 8）。
   - `list` 先读目录，然后在目录里找 `--tag` 的标签，再用 `read_recipes` 读每个菜谱（2.2）。它不再另外调用 `list_recipe_ids`，因为 `read_recipes` 会先返回列表的问题，再返回各文件的问题（F04 设计 2.7）。所以 `list` 对列表的每个问题只报告一次。未知标签让 `list` 在读任何菜谱之前停下，所以 `list --tag breakfast` 不解析任何菜谱文件。
   - `show` 先检查命令行上的值。然后它读目录，用 `list_recipe_ids` 列出 `recipes/`，在这些 ID 里找这个 ID，并用 `read_recipe` 只读这一个菜谱（2.4）。列表的错误会让 `show` 停下，即使它说的是另一个文件，比如 `recipes\Rice Bowl.toml`。架构 6 不允许 `check` 以外的命令在错误之后继续。有错误的列表也可能缺少你要的 ID：`recipes\rice.TOML` 给出一个错误，却不给出 ID `rice`（F04 设计 2.5）。另一个菜谱文件里的错误不会让 `show` 停下，因为 `show` 不解析那个文件。
3. **警告和缺少的语言。** 两个命令都不写出警告，警告也从不改变退出码（架构 6）。警告由 `check` 报告。缺少所选语言的文字显示另一种语言，这是需求 3 的要求：名称和备注通过 `BiText.get`，步骤通过 `Steps.get`。`Steps.exact` 对所选语言给出 `None` 时，`show` 用 `STEPS_IN_OTHER_LANGUAGE` 作为步骤的标题：英文是 `Steps (no English steps, so these are the Chinese steps)`，和 F09 原型“A missing language”一样，中文是 `步骤（没有中文步骤，所以这里是英文步骤）`。`show` 的第一行写出菜谱有的每个名称，所选语言在前。所以没有英文名称的菜谱只显示它的中文名称，这一行也从不把一个名称写两遍。名称和备注没有别的标记。在 `list` 的表格里，缺少所选语言的名称也显示另一种语言。
4. **`--tag` 的标签。** `list` 用 `Catalog.find_tag` 找标签（F03 设计 2.6）。所以这个值按 F03 的规则与任一种语言的标签名称匹配：两端的空白不算，大小写只对字母 A 到 Z 不区分。`list --tag 快手`、`list --tag quick` 和 `list --tag " QUICK "` 保留相同的菜谱。菜谱的 `tags` 里有这个标签时，`list` 保留这个菜谱。`find_tag` 找不到标签时，`list` 把 `UNKNOWN_TAG`（目录里没有标签时是 `NO_TAGS`）写到错误流，并以 1 退出，和原型一样。提示按你输入的样子写出这个值，并按目录的顺序列出目录里的标签，就像原型列出的“quick, home-style, vegetarian, spicy, and staple”。在表格的一行里，标签按菜谱的顺序排列，也就是它文件里的顺序（F04 设计 2.3）。所以 `mapo-tofu` 显示“spicy, home-style”，和原型一样，虽然目录把 home-style 排在前面。
5. **带标签的列表的列宽。** `list --tag` 的表格保持整个列表的列宽，F05 原型“The language from the settings”和 F09 原型“List the recipes with one tag”都是这样，v0.1-S10 和 v0.1-S21 也这样预期。所以 `list` 给 `format_table` 传入参数 `min_widths`，其中有三个宽度，分别对应 ID、所选语言的名称和份数。每个宽度是在 `read_recipes` 给出的每个菜谱上，这一格各行中最大的 `display_width`（F02 设计 2.8）。每一格按 `format_table` 的规则 1 拆成各行，即 `cell.splitlines()`（F02 设计 2.9）。`format_table` 按格子的每一行来量，而名称里可以有换行，因为 F04 只去掉文字两端的空白（F04 设计 2.6）。表头的宽度由 `format_table` 自己算进去。标签是最后一列，`format_table` 不给它补空格。所以带标签的列表和不带标签的列表对齐，与标签无关。没有 `--tag` 时，这三个宽度等于 `format_table` 按它的规则 2 自己算出的宽度，所以不改变任何东西，名称有两行时也是这样。
6. **没有菜谱的列表。** `list` 一个菜谱也不保留时，它只写一行，不写表格，并以 0 退出。文件夹里没有菜谱时，这一行是 `NO_RECIPES`，即 `No recipes.`。没有菜谱带 `--tag` 的标签时，这一行是 `NO_RECIPE_WITH_TAG`，比如 `No recipe has the tag "soup".`。空列表不是错误，就像 F10 原型“No match”里没有匹配不是错误一样，这两行也沿用了它的措辞。只有表头、没有行的表格不会多说什么。`init` 会写一个菜谱，所以只有在你删除每个菜谱文件之后，`recipes/` 里才没有菜谱。
7. **不可能是菜谱 ID 的值，以及没有菜谱的 ID。** `show` 在读任何文件之前用 `is_recipe_id` 检查 `ID`（F04 设计 2.4）。违反这条规则的值是错误的参数值，比如 `Mapo`、`../rice`、`""`、`con`，或带 U+2010 HYPHEN 的 `tomato\u2010egg`。对这样的值，`show` 抛出 `UsageError(NOT_A_RECIPE_ID, None, id=value)`，`cli` 以 2 退出（架构 6，F05 设计 2.7）。提示已经说了该运行什么，所以不带下一行（ADR-0008）：`"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.`。F06 的 `NOT_A_WEEK` 对不可能存在的周，比如 `2026-W99`，也是这样处理，F11 原型显示它以 2 退出。这条提示不说原因，这样一段文字就适用于 `is_recipe_id` 的每条规则，包括规则 4 的 Windows 设备名。符合规则、但不在 `list_recipe_ids` 给出的 ID 里的 ID 没有菜谱文件。对这样的 ID，`show` 把 `UNKNOWN_ID`，也就是 F09 原型“An unknown ID”的那一行，写到错误流，并以 1 退出，这是需求 3 对文件不存在的要求。`UNKNOWN_ID` 的后半句用这个 ID 运行 `search`，这时 ID 只有小写字母、数字和 `-`，所以它总是一条正确的命令行。所以 `show` 从不把 `DataFolder.recipe_file` 或 `read_recipe` 会拒绝的值传给它们（F03 设计 2.1，F04 设计 2.6）。`show` 把这个 ID 与列表里的 ID 逐字比较，所以 Windows 和 Linux 给出相同的结果。这个选择由 Troy 决定（下面的 C 点）。
8. **`--servings`。** 这个值是从 `datafile` 的 `MIN_SERVINGS` 到 `MAX_SERVINGS`，即 1 到 100 的整数，也就是 Troy 在 F04 里为所有份数接受的范围（F04 设计，选择 2，以及 F05 设计 3.1）。它用 ASCII 数字 `0` 到 `9` 写成，不以 `0` 开头，不带正负号，也没有其他字符，比如 `4` 或 `100`。其他任何值都给出 `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)`。提示按你输入的文字显示这个值，从不把它当作 `int`，所以没有值会碰到 F02 的 4,300 位限制。5,000 位的值给出这条提示，而不是 Python 的 `ValueError`（F05 设计第 2 节）。这条规则看的是文字，因为 Python 的 `int` 也能读 `+4`、` 4`、`1_0`、`\uff14`（FULLWIDTH DIGIT FOUR）和 `\u0664`（ARABIC-INDIC DIGIT FOUR）。提示已经说了该写什么，所以不带下一行（ADR-0008），和 F05 里命令自身选项的其他错误一样。`show` 用 `Quantity.scale` 把每个数量乘以 `Fraction(servings, recipe.servings)`，再用 `Quantity.to_text` 写出。`to_text` 保留菜谱的单位，并向上取整到最多两位小数（F01 设计 2.9 和 2.11）。所以 2 份的菜谱做 3 份时，3 个鸡蛋是 `4.5 pieces`。“适量”的数量仍是适量。F01 设计 2.9 只承诺 `Quantity.scale` 给出一个等于 `TO_TASTE` 的值，它的示例也用 `==` 检查。所以检查它的代码用 `is_to_taste` 或 `==`，从不用 `is`。步骤保持原样，和原型说的一样。份数这一行写出份数，并在括号里写出菜谱自己的份数：`Servings: 4 (the recipe makes 2)` 和 `份数：4（菜谱按 2 份写）`。`--servings` 等于菜谱的份数时，什么都不换算，`show` 写出的行和不带这个选项时相同，比如 `Servings: 2   Tags: quick, home-style`。
9. **提示里的数字。** `browse` 的提示显示菜谱的份数、在 1 到 100 之间时的 `--servings` 的值，以及 `list` 保留的菜谱数。菜谱的份数在 1 到 100 之间（F04 设计 2.3），菜谱数是一个元组的长度。`--servings` 的错误值以文字放进提示。文件里的问题只通过 `stop_at_error` 写到错误流，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `browse` 的提示不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。
10. **速度。** PT01 要求有 1,000 个菜谱时的 `list` 和 `show` 在 Troy 的电脑上各在 1 秒内完成，取 5 次运行的中位数（v0.1-S28 和 v0.1-S29）。`list` 读的比 `check` 少：`cli` 里的设置、目录、`recipes/` 的一次列表，以及每个菜谱文件各一次，不读常备清单和 52 个菜单。自 F07 的读取加速（PR #50）以来，`check` 在 Troy 的电脑上处理 PT01 文件夹的中位数约为 0.82 秒，在 F07 的审查里，菜单约占 `check` 耗时中的 0.08 秒。`list` 在此之上加上它的表格，表格的耗时随字符数增长：PT01 文件夹上约 40,000 个字符，每个字符最多用 `display_width` 量三次，一次为 `min_widths`，两次在 `format_table` 里。每一行都不运行 `Message.render`，因为标签来自 `comma_list`，份数来自 `str`。所以 `list` 的耗时应该与 `check` 差不多，或者更少。这是根据上述耗时的估计，不是测量结果。`show` 读设置、300 种食材的目录、一次列表和一个菜谱，所以它的耗时接近工具的启动时间。F09 在 mock 之前不需要 `[refactor]` 旁支 PR。测试计划可以在 PT01 文件夹上为这两个命令计时，就像 F07-T25 为 `check` 计时一样。如果 `list` 接近上限，第一步是代码审查员在 PR #50 上指出的修改：`Message.render` 每次调用都解析模板的占位符，在 PT01 文件夹上约耗 0.06 秒。每条提示只解析一次是 `text` 的内部修改，由架构师判断它是否改变 F02 的接口。它会作为 `[refactor]` PR，在 F09 的实现 PR 之前合入。

这三点由 Troy 决定。设计采用了每一点的建议。

- **A. `red-braised-pork` 的步骤**（架构师，F04 审查）。F09 原型“A missing language”为 `red-braised-pork` 显示四个中文步骤：`五花肉冷水下锅，焯水后捞出。`、`小火把冰糖炒成焦糖色，下五花肉翻炒上色。`、`加生抽、姜片和热水，没过肉，小火炖 1 小时。` 和 `大火收汁，撒上葱段。`。示例文件 `tests/data/example/recipes/red-braised-pork.toml` 里是另外三个步骤。v0.1-S12 第 3 步预期原型的输出，所以两者必须改一个。
  - 方案 1，推荐：改测试数据。一个测试 PR 把文件的三个步骤逐字换成原型的四个步骤。只有 F04-T38（`tests/test_f04_example_recipes.py` 里的 `test_f04_t38_the_other_six_example_recipes`）依赖它们。它断言文件里有 3 个中文步骤，并把菜谱与它从文件读出的步骤比较。所以它的数量在同一个 PR 里从 3 改成 4，main 上的测试保持通过。没有别的测试读这个文件的步骤。F07 的测试往这个文件里追加英文步骤，`tests/f04_support.py` 里的两个中文步骤来自 F04 设计 2.2 的示例，而不是这个文件。没有文档需要修改，因为 `docs/prototypes/example-data.md` 只说这些步骤是中文的。
  - 方案 2：改需求。产品经理在 Troy 批准的 `[docs]` PR 里，把文件的三个步骤写进原型的“A missing language”一节。这样 v0.1-S12 按现在的写法成立，不需要修改测试。
  - 推荐方案 1 的理由：原型是已经批准、由 v0.1-S12 检查的文字，而示例数据文件夹是跟随原型的测试数据（架构 10）。方案 1 只改一个测试里的一个数，不改需求。
- **B. 新的文字。** 没有原型展示这些文字。每一段都沿用已有提示的措辞。建议按 2.2 和 2.4 的写法接受它们。
  - 换算后菜谱的英文份数行 `Servings: 4 (the recipe makes 2)   Tags: quick, home-style`，对应中文原型的 `份数：4（菜谱按 2 份写）   标签：快手、家常`。
  - 英文步骤的中文标题 `步骤（没有中文步骤，所以这里是英文步骤）`，对应原型的 `Steps (no English steps, so these are the Chinese steps)`。
  - 原型里两个错误的中文文字。`未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。` 沿用 F03 的 `UNKNOWN_CATEGORY`，`没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。` 沿用 `RUN_CHECK`。
  - 两种语言都新增的：`NO_RECIPES`、`NO_RECIPE_WITH_TAG`、`UNKNOWN_TAG` 只有一个标签时的形式、`NO_TAGS`、`NOT_A_RECIPE_ID`、`SERVINGS_NOT_1_TO_100`，以及 `SERVINGS_ONLY`，即没有标签的菜谱的份数行。
- **C. 不可能是菜谱 ID 的值**（选择 7）。
  - 方案 1，推荐：用法错误，退出码 2，`"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.`。
  - 方案 2：对列表里没有的每个值，都给出“An unknown ID”的输出，退出码 1。它的后半句 `Run "recipe-menu search Mapo" to find it.` 对 `Mapo` 有帮助。但对 `""` 这样的值，后半句给出的是一条错误的命令行，所以这种情况无论如何都需要另一条提示。
  - 推荐方案 1 的理由：需求 3 把退出码 2 给了错误的命令行，F06 和 F11 原型对不可能存在的周也是这样处理。

这些后续功能会在 F09 的基础上构建。细节由它们自己的设计决定。

- F10 的 `search` 用带 ID 和名称两列的表格列出菜谱，和 `list` 一样。F10 原型“No match”只写一行、不写表格，和 `list` 一个菜谱也不保留时一样（选择 6）。架构 4 允许 `search` 引用 `browse`。F09 只导出它的两个命令，这样在有功能使用某个名称之前，不导出它。F10 的设计把两个命令共用的东西加进 `browse`，比如菜谱一行的各格或选择 5 的列宽，或者自己另写一份。
- `UNKNOWN_ID` 的后半句运行 `recipe-menu search`，这个命令由 F10 添加。在 F10 的 mock PR 之前，这条命令行给出 `Unknown command "search".`。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/browse/__init__.py` 和 `messages.py`，可能还有一个内部文件，以及 `src/recipe_menu/cli/_commands.py` 里的那几项。它定义每条提示和字段齐全的两个命令，所以帮助会列出 `list` 和 `show`，两个命令也都能运行。它的 `run` 函数不读任何文件，也不抛任何异常。比如，每个都什么也不写并给出 0。所以输出、退出码 1 或 `run` 抛出的 `UsageError` 的新测试在 mock 上会失败（R09）。只检查命令的字段、帮助、某条提示或退出码 0 的测试，在 mock 上会通过，从而违反 R09。检查 `cli` 在运行命令之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、`list extra`，或者 `--tag` 没有值。实现（PR 5）读取文件并写出输出。每个 PR 都在 R03 的 5 个文件以内。如果 A 点选方案 1，示例文件的修改和 F04-T38 一起放在一个测试 PR 里。

### 2.1 `LIST_COMMAND`

- 模块：browse
- 功能：对 `list` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 写出 2.2 的列表。

签名：

```python
LIST_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("list",)
#   help_line = LIST_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ("--tag",)
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("list",)`。 | 无 |
| `help_line` | `Message` | `LIST_HELP`：“List the recipes.”和“列出菜谱。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 读取目录和每个菜谱，并写出 2.2 的列表。 | 给出 0 或 1。遇到坏数据不抛异常。 |
| `argument` | `None` | `list` 不接受参数。 | 无 |
| `options` | `str` 的元组 | `("--tag",)`，要保留的菜谱的标签（2.2）。 | 只有值不为空、也不以 `--` 开头时，`cli` 才传入它（F05 设计 2.10）。 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `list`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、`context.folder`、`context.out` 和 `context.err`。它不用 `context.settings`，也不用 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `list` 的东西（F05 设计 2.6）。 | 没有参数值。`arguments.option("--tag")` 是 `--tag` 的值，或者 `None`。 |

- 返回值：`LIST_COMMAND`，一个 `Command`。
  - `LIST_COMMAND.usage` 在两种语言里都是 `list`，所以帮助显示 `list`，用法错误引用 `recipe-menu list`。
  - `LIST_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出输出，并给出 0 或 1。

F09 之后，帮助列出这些命令，第二列从第 18 列之后开始（选择 1）。英文：

```text
Commands:
  init            Create the data folder with example data.
  check           Check every data file for mistakes.
  list            List the recipes.
  show ID         Show one recipe.
```

中文：

```text
命令：
  init            创建数据文件夹和示例数据。
  check           检查每个数据文件有没有错误。
  list            列出菜谱。
  show ID         查看一个菜谱。
```

错误：无。`run` 遇到坏数据从不抛异常。它也不抛 `UsageError`，因为 `--tag` 的每个值都是一个要查找的名称。目录里没有的名称给出退出码 1（2.2）。

- 副作用：与 2.2 相同。`run` 通过 F03 和 F04 的读取函数读取目录和菜谱文件，写入 `context.out` 或 `context.err`，不写任何文件。
- 性能指标：无。PT01 从启动到退出为 `recipe-menu list`（2.2）计时，而它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里是默认设置，输出跟随 `context.lang`。帮助来自 `COMMANDS`，F09 之后它有 `init`、`check`、`list` 和 `show`。

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.browse import LIST_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings

assert LIST_COMMAND.words == ("list",)
assert LIST_COMMAND.usage == BiText("list", "list")
assert LIST_COMMAND.help_line.render(Lang.EN) == "List the recipes."
assert LIST_COMMAND.help_line.render(Lang.ZH) == "列出菜谱。"
assert (LIST_COMMAND.argument, LIST_COMMAND.options) == (None, ("--tag",))
assert LIST_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert LIST_COMMAND.run(context, Arguments((), (("--tag", "quick"),))) == 0
assert out.getvalue().splitlines() == [
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "",
    "共 3 个菜谱带有标签“快手”。",
]
assert err.getvalue() == ""


def help_lines(*argv: str) -> list[str]:
    out = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=io.StringIO(),
    )
    assert code == 0
    return out.getvalue().splitlines()


english = help_lines("--help")
assert len(english) == 17
assert english[4:9] == [
    "Commands:",
    "  init            Create the data folder with example data.",
    "  check           Check every data file for mistakes.",
    "  list            List the recipes.",
    "  show ID         Show one recipe.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[7:9] == ["  list            列出菜谱。", "  show ID         查看一个菜谱。"]
```

### 2.2 `recipe-menu list`

- 模块：browse
- 功能：列出菜谱的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 2，以及 [4](../../requirements.zh-CN.md#4-功能点)）。它打印一张按 ID 排序的菜谱表，`--tag` 只保留带这个标签的菜谱。F09 原型“List the recipes”和“List the recipes with one tag”展示了它。

签名：

```text
recipe-menu list [--tag TAG] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--tag` | 标签名称 | 只保留带这个标签的菜谱。 | 目录里某个标签的名称，任一种语言都可以，按 `Catalog.find_tag` 的方式匹配（选择 4）。不为空，最多写一次（F05 设计 2.10）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。 | 按 F05 设计 2.10。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `list`。 | 无 |

`list` 按顺序执行这些步骤。每个读文件的步骤都用前面步骤给出的东西。

1. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`list` 对第一个错误给出 `stop_at_error(context, error)`。
2. 有 `--tag` 时，`catalog.find_tag(value)` 给出 `tag`。它给出 `None` 时，`list` 把 `UNKNOWN_TAG`（按目录里标签的个数选择形式），或者目录里没有标签时的 `NO_TAGS`，写到错误流，并给出 1。
3. `read_recipes(context.folder, catalog)` 给出 `recipes` 和它们的问题（F04 设计 2.7）。问题里有错误时，`list` 用 `stop_at_error` 在第一个错误处停下。
4. `list` 保留 `tags` 里有 `tag` 的每个菜谱，没有 `--tag` 时保留每个菜谱，顺序与 `recipes` 相同，也就是 ID 的顺序。
5. 它把下面的输出写到输出流，并给出 0。

第 1 步和第 3 步的警告不改变任何东西（选择 3）。

- 返回值：退出码，以及写在对应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `list` 写出了它的列表，包括空列表。 | 输出流：表格和计数行，或者 `list` 一个菜谱也不保留时的一行。 |
| 1 | 某个文件有错误，或者目录里没有名称为 `--tag` 的标签。 | 错误流：`stop_at_error` 的三行，或者 `UNKNOWN_TAG` 或 `NO_TAGS` 的一行。输出流上什么也没有。 |

`list` 保留一个或多个菜谱时，它的输出是这些行，按这个顺序，每行以换行结束：

1. `format_table(rows, min_widths=widths)` 的各行，没有缩进，用默认间距 3（F02 设计 2.9）。
2. 一个空行。
3. 计数行：没有 `--tag` 时是 `RECIPE_COUNT`，有 `--tag` 时是 `RECIPES_WITH_TAG`，都按 `list` 保留的菜谱数选择形式。

`rows` 是表头行，然后是 `list` 保留的每个菜谱的一行：

| 列 | 表头 | 单元格 |
| --- | --- | --- |
| ID | `ID_HEADING` | `recipe.id` |
| 名称 | `NAME_HEADING` | `recipe.name.get(context.lang)` |
| 份数 | `SERVINGS_HEADING` | `str(recipe.servings)` |
| 标签 | `TAGS_HEADING` | `comma_list(tag.name for tag in recipe.tags).get(context.lang)`，按菜谱的顺序。没有标签的菜谱是空文字。 |

`widths` 是前三列各自的格子里各行中最大的 `display_width`，在第 3 步的每个菜谱上计算，不管保留与否，每一格按 `format_table` 的规则 1 拆成各行（选择 5）。`list` 按文件里的样子写出每段文字，所以 `format_table` 的规则对它适用，比如带换行的名称会占两行。

`list` 一个菜谱也不保留时，它的输出只有一行：没有 `--tag` 时是 `NO_RECIPES`，有 `--tag` 时是 `NO_RECIPE_WITH_TAG`（选择 6）。

`list` 的提示如下。`RECIPE_COUNT`、`RECIPES_WITH_TAG` 和 `UNKNOWN_TAG` 是 `Plural` 值（F02 设计 2.4）。`RECIPE_COUNT` 和 `RECIPES_WITH_TAG` 按 `count` 选择，`UNKNOWN_TAG` 按目录里标签的个数选择。`NO_TAGS` 是一条单独的 `Message`，用于没有标签的目录，因为它没有 `{tags}`，而 `Plural` 的两条提示需要相同的占位符。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `LIST_HELP` | `List the recipes.` | `列出菜谱。` |
| `ID_HEADING` | `ID` | `ID` |
| `NAME_HEADING` | `Name` | `名称` |
| `SERVINGS_HEADING` | `Servings` | `份数` |
| `TAGS_HEADING` | `Tags` | `标签` |
| `RECIPE_COUNT`，一个时 | `{count} recipe.` | `共 {count} 个菜谱。` |
| `RECIPE_COUNT`，多个时 | `{count} recipes.` | `共 {count} 个菜谱。` |
| `RECIPES_WITH_TAG`，一个时 | `{count} recipe has the tag "{tag}".` | `共 {count} 个菜谱带有标签“{tag}”。` |
| `RECIPES_WITH_TAG`，多个时 | `{count} recipes have the tag "{tag}".` | `共 {count} 个菜谱带有标签“{tag}”。` |
| `NO_RECIPES` | `No recipes.` | `没有菜谱。` |
| `NO_RECIPE_WITH_TAG` | `No recipe has the tag "{tag}".` | `没有菜谱带有标签“{tag}”。` |
| `UNKNOWN_TAG`，一个标签时 | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`，多个标签时 | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `count` | `list` 保留的菜谱数，即一个元组的长度（选择 9）。 |
| `tag` | `find_tag` 给出的标签的名称，作为它的 `BiText`，所以每种语言显示它自己的名称：`--tag 快手` 时是 `quick` 和 `快手`。 |
| `value` | 你输入的 `--tag` 的值。 |
| `tags` | 目录里各标签名称的 `and_list`，每个名称作为它的 `BiText`，按目录的顺序：“quick, home-style, vegetarian, spicy, and staple”和“快手、家常、素、辣和主食”。 |

错误：

`cli` 在运行 `list` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 1，错误流上是 `stop_at_error` 的三行 | 目录、`recipes/` 的列表或某个菜谱文件有错误（第 1 步和第 3 步）。 |
| 退出码 1，错误流上是 `UNKNOWN_TAG` 或 `NO_TAGS` | 目录里没有名称为 `--tag` 的标签（第 2 步）。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `list` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "extra". Write "recipe-menu list".` | `list` 后面跟了一个词。 |
| 退出码 2，先是只有一个选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"list" has no option "--tags". Its own option is "--tag".` | 除 `--tag` 和四个全局选项以外的选项。 |
| 退出码 2，`OPTION_NEEDS_VALUE` 或 `OPTION_TWICE`，不带下一行，比如 `--tag needs a value.` | `--tag` 没有值，或者写了两次。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。不再写出任何东西（F05 设计 2.10）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `list` 把 `catalog.toml` 读一次，把 `recipes/` 列一次，把每个菜谱文件读一次，都通过 F03 和 F04 的读取函数。遇到未知标签时，它不读任何菜谱文件。它不读 `pantry.toml`，也不读菜单。它写入输出流或错误流。它不写任何文件，所以每个文件和文件夹都保持原来的字节和修改时间（v0.1-S23）。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。这些运行先给出 F09 原型的输出，然后给出 F05 原型“The language from the settings”的输出。接着目录加上一个没有菜谱用的标签，然后去掉所有标签，这也说明 `list` 在读任何菜谱之前查找标签。`mapo-tofu` 里的一个错误让 `list` 停下，没有菜谱文件的文件夹给出一行。

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def run(data: Path, *argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(data)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


ENGLISH = [
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "cola-wings           Cola chicken wings        2          home-style",
    "mapo-tofu            Mapo tofu                 2          spicy, home-style",
    "red-braised-pork     Red-braised pork belly    2          home-style",
    "rice                 Steamed rice              2          staple",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
    "",
    "7 recipes.",
]
CHINESE = [
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣、家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "",
    "共 7 个菜谱。",
]
assert run(folder.root, "list") == (0, ENGLISH, [])
assert run(folder.root, "list", "--lang", "zh") == (0, CHINESE, [])

quick = [ENGLISH[0], ENGLISH[1], ENGLISH[6], ENGLISH[7], "", '3 recipes have the tag "quick".']
assert run(folder.root, "list", "--tag", "快手") == (0, quick, [])
assert run(folder.root, "list", "--tag", " QUICK ") == (0, quick, [])
quick_zh = [CHINESE[0], CHINESE[1], CHINESE[6], CHINESE[7], "", "共 3 个菜谱带有标签“快手”。"]
assert run(folder.root, "list", "--tag", "quick", "--lang", "zh") == (0, quick_zh, [])
tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
breakfast = [f'Unknown tag "breakfast". {tags}']
assert run(folder.root, "list", "--tag", "breakfast") == (1, [], breakfast)
breakfast_zh = ["未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。"]
assert run(folder.root, "list", "--tag", "breakfast", "--lang", "zh") == (1, [], breakfast_zh)

settings_text = folder.settings.read_text(encoding="utf-8")
zh_settings = settings_text.replace('language = "en"', 'language = "zh"')
folder.settings.write_text(zh_settings, encoding="utf-8")
vegetarian_zh = [CHINESE[0], CHINESE[1], "", "共 1 个菜谱带有标签“素”。"]
assert run(folder.root, "list", "--tag", "素") == (0, vegetarian_zh, [])
vegetarian = [ENGLISH[0], ENGLISH[1], "", '1 recipe has the tag "vegetarian".']
assert run(folder.root, "list", "--tag", "素", "--lang", "en") == (0, vegetarian, [])
folder.settings.write_text(settings_text, encoding="utf-8")

catalog_text = folder.catalog.read_text(encoding="utf-8")
staple = '{ zh = "主食", en = "staple" },'
soup = catalog_text.replace(staple, staple + '\n  { zh = "汤", en = "soup" },')
folder.catalog.write_text(soup, encoding="utf-8")
assert run(folder.root, "list", "--tag", "汤") == (0, ['No recipe has the tag "soup".'], [])
assert run(folder.root, "list", "--tag", "soup", "--lang", "zh") == (
    0,
    ["没有菜谱带有标签“汤”。"],
    [],
)
no_tags = catalog_text[: catalog_text.index("tags = [")] + "tags = []\n"
folder.catalog.write_text(no_tags, encoding="utf-8")
no_quick = ['Unknown tag "quick". The catalog has no tags.']
assert run(folder.root, "list", "--tag", "quick") == (1, [], no_quick)
choy = Path("recipes", "choy-sum.toml")
assert run(folder.root, "list") == (
    1,
    [],
    [
        f"{choy}, tags",
        '  Unknown tag "快手". Add it to the catalog\'s tags.',
        'Run "recipe-menu check" to see every problem.',
    ],
)
folder.catalog.write_text(catalog_text, encoding="utf-8")

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "list") == (1, [], stopped)
assert run(folder.root, "list", "--tag", "breakfast") == (1, [], breakfast)
code, out, err = run(folder.root, "list", "extra")
assert (code, out) == (2, [])
assert err == [
    'Unexpected argument "extra". Write "recipe-menu list".',
    'Run "recipe-menu --help" to see the commands.',
]

for path in folder.recipes.iterdir():
    path.unlink()
assert run(folder.root, "list") == (0, ["No recipes."], [])
assert run(folder.root, "list", "--lang", "zh") == (0, ["没有菜谱。"], [])
assert run(folder.root, "list", "--tag", "quick") == (0, ['No recipe has the tag "quick".'], [])
```

### 2.3 `SHOW_COMMAND`

- 模块：browse
- 功能：对 `show` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 写出 2.4 的菜谱。

签名：

```python
SHOW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("show",)
#   help_line = SHOW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(ID_ARGUMENT)
#   options = ("--servings",)
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("show",)`。 | 无 |
| `help_line` | `Message` | `SHOW_HELP`：“Show one recipe.”和“查看一个菜谱。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 检查命令行上的值，读取目录、`recipes/` 的列表和这个菜谱，并写出 2.4 的菜谱。 | 给出 0 或 1。`ID` 或 `--servings` 的值错误时抛出 `UsageError`，而且在读取任何文件、写出任何输出之前抛出。 |
| `argument` | `Argument` | `Argument(ID_ARGUMENT)`，必填，不重复。`ID_ARGUMENT` 在两种语言里都是 `ID`，即 F05 原型帮助里的名称。 | 所以 `cli` 正好传入一个值（F05 设计 2.5）。 |
| `options` | `str` 的元组 | `("--servings",)`，要换算到的份数（2.4）。 | 只有值不为空、也不以 `--` 开头时，`cli` 才传入它（F05 设计 2.10）。 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `show`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、`context.folder`、`context.out` 和 `context.err`。它不用 `context.settings`，也不用 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `show` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `(ID,)`。`arguments.option("--servings")` 是 `--servings` 的值，或者 `None`。 |

- 返回值：`SHOW_COMMAND`，一个 `Command`。
  - `SHOW_COMMAND.usage` 在两种语言里都是 `show ID`，所以帮助显示 `show ID`，用法错误引用 `recipe-menu show ID`。
  - `SHOW_COMMAND.run(context, arguments)` 按 2.4 的步骤执行，用 `context.lang` 写出输出，并给出 0 或 1。

错误：

`run` 先检查 `--servings`，再检查 `ID`，就像 `cli` 先检查选项、再检查参数一样（F05 设计 2.10，第 7 步和第 8 步）。两项检查都不读文件。

| 错误 | 何时发生 |
| --- | --- |
| `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)` | `--servings` 的值违反选择 8 的规则。 |
| `UsageError(NOT_A_RECIPE_ID, None, id=value)` | 对 `ID` 的值，`is_recipe_id(value)` 为假（选择 7）。 |

- 副作用：与 2.4 相同。`run` 通过 F03 和 F04 的读取函数读取目录、`recipes/` 的列表和一个菜谱文件，写入 `context.out` 或 `context.err`，不写任何文件。
- 性能指标：无。PT01 从启动到退出为 `recipe-menu show`（2.4）计时，而它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本。第一个上下文里的设置是 4 份，`show` 不用它。两个抛出异常的调用都不往任何流里写一行。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.commands.browse import SHOW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SHOW_COMMAND.words == ("show",)
assert SHOW_COMMAND.usage == BiText("show ID", "show ID")
assert SHOW_COMMAND.help_line.render(Lang.EN) == "Show one recipe."
assert SHOW_COMMAND.help_line.render(Lang.ZH) == "查看一个菜谱。"
assert SHOW_COMMAND.argument == Argument(Message("ID", "ID"))
assert SHOW_COMMAND.options == ("--servings",)
assert SHOW_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
four = Context(Lang.EN, folder, Settings(servings=4), out, err, date(2026, 11, 10))
assert SHOW_COMMAND.run(four, Arguments(("rice",))) == 0
assert out.getvalue().splitlines()[1] == "Servings: 2   Tags: staple"

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert SHOW_COMMAND.run(context, Arguments(("rice",), (("--servings", "3"),))) == 0
assert out.getvalue().splitlines() == [
    "Steamed rice  米饭",
    "Servings: 3 (the recipe makes 2)   Tags: staple",
    "",
    "Ingredients",
    "  Rice   240 g",
    "",
    "Steps",
    "  1. Rinse the rice, add water, and soak it for 20 minutes.",
    "  2. Cook it in a rice cooker, and let it rest for 10 minutes.",
]
assert err.getvalue() == ""

SHOW_COMMAND.run(context, Arguments(("Mapo",)))  # raises UsageError
SHOW_COMMAND.run(context, Arguments(("rice",), (("--servings", "0"),)))  # raises UsageError
```

### 2.4 `recipe-menu show`

- 模块：browse
- 功能：查看一个菜谱的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 2，以及 [4](../../requirements.zh-CN.md#4-功能点)）。它打印菜谱的名称、份数、标签、带备注的食材和步骤，`--servings` 换算数量。F09 原型“Show one recipe”、“Show one recipe for 4 servings, in Chinese”、“A missing language”和“An unknown ID”展示了它。

签名：

```text
recipe-menu show ID [--servings N] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `ID` | 菜谱 ID | 要查看的菜谱，比如 `tomato-egg`。 | 正好一个值。`is_recipe_id(ID)` 为真（选择 7）。 |
| `--servings` | 整数 | 数量要换算到的份数。 | 从 1 到 100，按选择 8 的写法。没有这个选项时，用菜谱自己的份数。最多写一次（F05 设计 2.10）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。 | 按 F05 设计 2.10。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `show`。 | 无 |

`show` 按顺序执行这些步骤。第 1 步和第 2 步不读文件。

1. 有 `--servings` 时，它按选择 8 检查这个值，值错误时抛出 `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)`。
2. 它用 `is_recipe_id` 检查 `ID`，结果为假时抛出 `UsageError(NOT_A_RECIPE_ID, None, id=ID)`。
3. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`show` 对第一个错误给出 `stop_at_error(context, error)`。
4. `list_recipe_ids(context.folder)` 给出 ID 和它们的问题（F04 设计 2.5）。问题里有错误时，`show` 用 `stop_at_error` 在第一个错误处停下。
5. `ID` 不在这些 ID 里时，`show` 把 `UNKNOWN_ID` 写到错误流，并给出 1。
6. `read_recipe(context.folder, catalog, ID)` 给出菜谱和它的问题（F04 设计 2.6）。问题里有错误时，`show` 用 `stop_at_error` 在第一个错误处停下。它的警告不改变任何东西（选择 3）。
7. 它按下面的样子把菜谱写到输出流，并给出 0。

- 返回值：退出码，以及写在对应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `show` 写出了菜谱。 | 输出流：下面的各行。 |
| 1 | 某个文件有错误，或者没有菜谱用这个 ID。 | 错误流：`stop_at_error` 的三行，或者 `UNKNOWN_ID` 的一行。输出流上什么也没有。 |
| 2 | `ID` 或 `--servings` 的值错误。 | 错误流：由 `cli` 写出的提示，不带下一行。输出流上什么也没有。 |

输出是这些行，按这个顺序，每行以换行结束：

1. 名称：菜谱在 `context.lang` 里的名称，然后是两个空格和它在另一种语言里的名称，都来自 `recipe.name.exact`。菜谱缺少的名称连同它前面的两个空格一起省去（选择 3）。两个空格在两种语言里相同，所以这一行不是 `Message`（架构 8）。
2. 份数行：`SERVINGS_LINE`，没有标签的菜谱用 `SERVINGS_ONLY`。它的 `servings` 是菜谱的份数。`--servings` 与菜谱的份数不同时，它是由 `--servings` 的值和菜谱的份数组成的 `SCALED_SERVINGS`，作为 `to_bitext` 给出的 `BiText`（选择 8）。
3. 一个空行。
4. 有食材的菜谱：`INGREDIENTS_HEADING`，然后是 `format_table(rows, indent=2)` 的各行，用默认间距 3，然后是一个空行。没有食材的菜谱没有这些行。
5. 步骤的标题：`recipe.steps.exact(context.lang)` 给出步骤时是 `STEPS_HEADING`，给出 `None` 时是 `STEPS_IN_OTHER_LANGUAGE`（选择 3）。
6. `recipe.steps.get(context.lang)` 的每个步骤一行，按顺序：两个空格、从 1 开始的步骤序号、一个句点、一个空格，以及文件里写的步骤，比如 `  1. Cut the tomatoes into wedges.`。序号和句点在两种语言里相同，所以这一行不是 `Message`。

`rows` 为菜谱的每个食材行各有一行，按文件的顺序，没有表头行：

| 列 | 单元格 |
| --- | --- |
| 食材 | `line.ingredient.name.get(context.lang)` |
| 数量 | `line.quantity.scale(factor).to_text(context.lang)`，有 `--servings` 时 `factor` 是用它的值算出的 `Fraction(servings, recipe.servings)`，没有时是 1（选择 8）。 |
| 备注 | `line.note.get(context.lang)`，这一行没有备注时是空文字。 |

`show` 的提示如下。只有缺少英文步骤时，`STEPS_IN_OTHER_LANGUAGE` 才用英文写出；只有缺少中文步骤时，才用中文写出。所以每个模板说的都是缺少的那种语言。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `SHOW_HELP` | `Show one recipe.` | `查看一个菜谱。` |
| `ID_ARGUMENT` | `ID` | `ID` |
| `SERVINGS_LINE` | `Servings: {servings}   Tags: {tags}` | `份数：{servings}   标签：{tags}` |
| `SERVINGS_ONLY` | `Servings: {servings}` | `份数：{servings}` |
| `SCALED_SERVINGS` | `{servings} (the recipe makes {recipe_servings})` | `{servings}（菜谱按 {recipe_servings} 份写）` |
| `INGREDIENTS_HEADING` | `Ingredients` | `食材` |
| `STEPS_HEADING` | `Steps` | `步骤` |
| `STEPS_IN_OTHER_LANGUAGE` | `Steps (no English steps, so these are the Chinese steps)` | `步骤（没有中文步骤，所以这里是英文步骤）` |
| `UNKNOWN_ID` | `No recipe has the ID "{id}". Run "recipe-menu search {id}" to find it.` | `没有 ID 为“{id}”的菜谱。运行“recipe-menu search {id}”查找它。` |
| `NOT_A_RECIPE_ID` | `"{id}" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `“{id}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。` |
| `SERVINGS_NOT_1_TO_100` | `--servings must be a whole number from 1 to 100, not "{servings}".` | `--servings 必须是 1 到 100 之间的整数，不能是“{servings}”。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `servings` | 在 `SERVINGS_LINE` 和 `SERVINGS_ONLY` 里：菜谱的份数，是一个 `int`，或者是 `SCALED_SERVINGS` 的 `BiText`。在 `SCALED_SERVINGS` 里：`--servings` 的值，是 1 到 100 之间的 `int`。在 `SERVINGS_NOT_1_TO_100` 里：你输入的 `--servings` 的值，是一个 `str`（选择 9）。 |
| `recipe_servings` | 菜谱的份数，是 1 到 100 之间的 `int`。 |
| `tags` | `recipe.tags` 各名称的 `comma_list`，每个名称作为它的 `BiText`，按菜谱的顺序：“quick, home-style”和“快手、家常”。 |
| `id` | 你输入的 `ID` 的值。在 `UNKNOWN_ID` 里，它符合 `is_recipe_id`，所以后半句的命令行是正确的（选择 7）。 |

按这些规则，可以得出 F09 原型的各行：比如 `份数：4（菜谱按 2 份写）   标签：快手、家常` 和 `  食用油   4 汤匙`。

错误：

`cli` 在运行 `show` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，`SERVINGS_NOT_1_TO_100`，不带下一行，比如 `--servings must be a whole number from 1 to 100, not "0".` | `--servings` 的值违反选择 8 的规则（第 1 步）。 |
| 退出码 2，`NOT_A_RECIPE_ID`，不带下一行，比如 `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `ID` 的值违反 `is_recipe_id` 的规则（第 2 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行 | 目录、`recipes/` 的列表或这个菜谱的文件有错误（第 3、4、6 步）。 |
| 退出码 1，错误流上是 `UNKNOWN_ID`，比如 `No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.` | `recipes/` 里没有这个 ID 的菜谱文件（第 5 步）。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `show` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_FEW_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`An argument is missing. Write "recipe-menu show ID".` | 命令行没有写 ID。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "rice". Write "recipe-menu show ID".` | 命令行写了两个或更多 ID。 |
| 退出码 2，先是只有一个选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"show" has no option "--tag". Its own option is "--servings".` | 除 `--servings` 和四个全局选项以外的选项。 |
| 退出码 2，`OPTION_NEEDS_VALUE` 或 `OPTION_TWICE`，不带下一行，比如 `--servings needs a value.` | `--servings` 没有值，或者写了两次。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。不再写出任何东西（F05 设计 2.10）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `show` 把 `catalog.toml` 读一次，把 `recipes/` 列一次，把 `recipes/<ID>.toml` 读一次，都通过 F03 和 F04 的读取函数。它不读别的菜谱文件，不读 `pantry.toml`，也不读菜单（架构 8）。命令行上的值错误时，它什么文件也不读。它写入输出流或错误流。它不写任何文件，所以每个文件和文件夹都保持原来的字节和修改时间（v0.1-S23）。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。这些运行给出 F09 原型的输出。`red-braised-pork` 的步骤与文件比较，因为它们由 A 点决定。新菜谱 `boiled-egg` 缺少中文名称、中文备注和中文步骤。`mapo-tofu` 里的一个错误只让 `show mapo-tofu` 停下，而一个不是 ID 的文件名会让每个 `show` 停下。

```python
import io
import tomllib
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def run(data: Path, *argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(data)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


TOMATO_EGG = [
    "Tomato and egg stir-fry  番茄炒蛋",
    "Servings: 2   Tags: quick, home-style",
    "",
    "Ingredients",
    "  Tomato        300 g      cut into wedges",
    "  Egg           3 pieces",
    "  Scallion      1 stalk    chopped",
    "  Salt          to taste",
    "  Sugar         1 tsp",
    "  Cooking oil   2 tbsp",
    "",
    "Steps",
    "  1. Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.",
    "  2. Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.",
    "  3. Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.",
    "  4. Return the eggs, season with salt, and scatter the scallion on top.",
]
FOUR_ZH = [
    "番茄炒蛋  Tomato and egg stir-fry",
    "份数：4（菜谱按 2 份写）   标签：快手、家常",
    "",
    "食材",
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  葱       2 根     切葱花",
    "  盐       适量",
    "  糖       2 茶匙",
    "  食用油   4 汤匙",
    "",
    "步骤",
    "  1. 番茄切块。鸡蛋加少许盐打散。",
    "  2. 热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。",
    "  3. 下剩下的油，炒番茄至软，加糖。",
    "  4. 倒回鸡蛋，加盐调味，撒上葱花。",
]
assert run(folder.root, "show", "tomato-egg") == (0, TOMATO_EGG, [])
assert run(folder.root, "show", "tomato-egg", "--servings", "2") == (0, TOMATO_EGG, [])
assert run(folder.root, "show", "tomato-egg", "--servings", "4", "--lang", "zh") == (0, FOUR_ZH, [])
code, out, err = run(folder.root, "show", "tomato-egg", "--servings", "3")
assert (code, err) == (0, [])
assert out[1] == "Servings: 3 (the recipe makes 2)   Tags: quick, home-style"
assert out[4:10] == [
    "  Tomato        450 g        cut into wedges",
    "  Egg           4.5 pieces",
    "  Scallion      1.5 stalks   chopped",
    "  Salt          to taste",
    "  Sugar         1.5 tsp",
    "  Cooking oil   3 tbsp",
]
assert out[10:] == TOMATO_EGG[10:]

code, out, err = run(folder.root, "show", "red-braised-pork")
assert (code, err) == (0, [])
assert out[:11] == [
    "Red-braised pork belly  红烧肉",
    "Servings: 2   Tags: home-style",
    "",
    "Ingredients",
    "  Pork belly   1 jin      cut into 3 cm cubes",
    "  Rock sugar   30 g",
    "  Soy sauce    2 tbsp",
    "  Ginger       3 slices",
    "  Scallion     2 stalks",
    "",
    "Steps (no English steps, so these are the Chinese steps)",
]
pork = tomllib.loads(folder.recipe_file("red-braised-pork").read_text(encoding="utf-8"))
assert out[11:] == [f"  {n}. {step}" for n, step in enumerate(pork["steps"]["zh"], 1)]

egg = [
    'name = { en = "Boiled egg" }',
    "servings = 1",
    "tags = []",
    "ingredients = [",
    '  { item = "鸡蛋", amount = "2", note = { en = "at room temperature" } },',
    '  { item = "盐", amount = "适量" },',
    "]",
    "[steps]",
    'en = ["Boil the eggs for 8 minutes."]',
]
folder.recipe_file("boiled-egg").write_text("\n".join(egg) + "\n", encoding="utf-8")
boiled = [
    "Boiled egg",
    "Servings: 1",
    "",
    "Ingredients",
    "  Egg    2 pieces   at room temperature",
    "  Salt   to taste",
    "",
    "Steps",
    "  1. Boil the eggs for 8 minutes.",
]
assert run(folder.root, "show", "boiled-egg") == (0, boiled, [])
boiled_zh = [
    "Boiled egg",
    "份数：3（菜谱按 1 份写）",
    "",
    "食材",
    "  鸡蛋   6 个   at room temperature",
    "  盐     适量",
    "",
    "步骤（没有中文步骤，所以这里是英文步骤）",
    "  1. Boil the eggs for 8 minutes.",
]
assert run(folder.root, "show", "boiled-egg", "--servings", "3", "--lang", "zh") == (
    0,
    boiled_zh,
    [],
)

unknown = 'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.'
assert run(folder.root, "show", "mapo") == (1, [], [unknown])
unknown_zh = "没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。"
assert run(folder.root, "show", "mapo", "--lang", "zh") == (1, [], [unknown_zh])
for wrong in ("Mapo", "../rice", "", "con", "tomato\u2010egg"):
    message = f'"{wrong}" is not a recipe ID. Run "recipe-menu list" to see the IDs.'
    assert run(folder.root, "show", wrong) == (2, [], [message])
not_an_id_zh = "“Mapo”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。"
assert run(folder.root, "show", "Mapo", "--lang", "zh") == (2, [], [not_an_id_zh])
for wrong in ("0", "101", "04", "+4", "4.0", " 4", "-1", "1_0", "\uff14", "\u0664", "9" * 5000):
    message = f'--servings must be a whole number from 1 to 100, not "{wrong}".'
    assert run(folder.root, "show", "tomato-egg", "--servings", wrong) == (2, [], [message])
zero = '--servings must be a whole number from 1 to 100, not "0".'
assert run(folder.root, "show", "Mapo", "--servings", "0") == (2, [], [zero])
assert run(folder.root, "show", "tomato-egg", "--servings", "100")[0] == 0
code, out, err = run(folder.root, "show")
assert (code, out) == (2, [])
assert err == [
    'An argument is missing. Write "recipe-menu show ID".',
    'Run "recipe-menu --help" to see the commands.',
]

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "show", "mapo-tofu") == (1, [], stopped)
assert run(folder.root, "show", "tomato-egg") == (0, TOMATO_EGG, [])

(folder.recipes / "Rice Bowl.toml").write_text("", encoding="utf-8")
code, out, err = run(folder.root, "show", "tomato-egg")
assert (code, out) == (1, [])
assert err[0] == str(Path("recipes", "Rice Bowl.toml"))
assert err[1].startswith("  This file name is not a recipe ID.")
assert err[2:] == ['Run "recipe-menu check" to see every problem.']
```

## 3. 对已有接口的修改

无。F01 到 F08 实现的接口都不改变。每个导出的名称都保持它的签名和行为。F09 增加模块 `browse`。它还在 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS` 里增加两项，这个文件是 `cli` 的内部文件，架构 4 允许每个命令功能这样做。有了这两项，真正的 `recipe-menu` 的帮助会列出 `list` 和 `show`（选择 1）。运行真正的 `COMMANDS` 的测试检查的都是这两项不会改变的行：未知命令、没有命令的命令行、帮助的第一行和最后一行（F05-T48 和 F05-T49），`check` 那一行和它的列（F07-T17），以及 `init` 那一行后面紧跟 `check` 那一行（F08-T14）。其他每个测试都给 `main` 传入自己的命令，或者只运行 `init` 和 `check`。A 点的方案 1 改的是测试数据和一个测试，不是接口。

F09 按这些接口的设计使用它们，不修改其中任何一个：

- F01 的 `Quantity.scale`、`Quantity.to_text` 和 `Quantity.is_to_taste`。
- F02 的 `BiText`、`Lang`、`Message`、`Plural`、`and_list`、`comma_list`、`display_width` 和 `format_table`。
- F03 的 `DataFolder`、`Problem`、`Catalog`、`Catalog.find_tag` 和 `read_catalog`。
- F04 的 `Recipe`、`RecipeIngredient`、`Steps`、`is_recipe_id`、`list_recipe_ids`、`read_recipe` 和 `read_recipes`。
- F05 的：`app` 里的 `Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error` 和 `stop_at_error`，`datafile` 里的 `MIN_SERVINGS` 和 `MAX_SERVINGS`，以及 `cli` 里的 `COMMANDS`。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `browse` 是架构 3 和 8 给 `list` 和 `show` 的命令模块，位于 `src/recipe_menu/commands/browse/`，只导出 `LIST_COMMAND` 和 `SHOW_COMMAND`。它引用 `app`、`lang`、`units`、`text`、`datafile`、`catalog` 和 `recipes`，都是它那一行允许的模块，它不需要 `settings`、`menus`、`shopping` 和 `check` 中的任何一个。它的提示放在它自己的 `messages.py` 里。`list` 解析每个菜谱。`show` 先列出文件夹内容，不打开任何文件，然后只解析它指定的那个菜谱，符合架构 8 的要求。两个命令都不写文件（架构 1）。F09 不增加值类型，按架构 5.2 的规定使用 `Recipe`、`Steps`、`Tag`、`Catalog`、`Quantity` 和 `Context`。不是 `Message` 的两种行，即用两个空格连起来的名称和带编号的步骤，只含数据、空格、数字和句点，它们不属于任何语言（架构 8）。架构师在分支的代码之上按 2.1 到 2.4 建了模型，并把两个命令放进 `COMMANDS`。用这台 Windows 11 电脑上的 Python 3.13.18，四个示例都成立，包括每个断言和两个 `# raises`。F09 原型的九个命令准确给出原型的各行和退出码，其中 `show red-braised-pork` 使用 A 点方案 1 的示例文件。两种语言的帮助都是 17 行，第二列从第 18 列之后开始（选择 1）。在 0.2 版里，每个文件的 6 个 `python` 代码块与 0.1 版的语法树相同，示例里也没有带换行的名称，所以四个示例和第 1 轮一样成立。 |
| 遵守错误处理和命名约定 | Pass | 读取函数的问题都是值，每个命令用 `first_error` 和 `stop_at_error` 在第一个错误处停下，这是架构 6 对 `check` 以外每个命令的要求。退出码和输出流符合架构 6 和需求 3。退出码 0 写到 stdout，空列表也是如此（选择 6）。文件里有错误、ID 没有对应的文件，或目录里没有某个标签时，退出码 1 写到 stderr，和原型、v0.1-S10 与 v0.1-S12 的预期一致。架构 6 没有专门为“命令行上的名称在数据里不存在”写一行。`--tag breakfast` 的退出码 1 沿用它对菜谱不存在的那一行，所以架构不需要修改。退出码 2 来自 `run` 对 `ID` 或 `--servings` 的错误值抛出的 `UsageError`，它在读任何文件、写任何输出之前抛出（F05 设计第 2 节）。`NOT_A_RECIPE_ID` 和 `SERVINGS_NOT_1_TO_100` 已经说了该运行什么或写什么，所以不带下一行（ADR-0008）。每条提示都是 UPPER_SNAKE 的 `Message` 或 `Plural`，复数和列表都来自 `text`。在模型上，2.4 示例里的 5 个错误 ID 和 11 个 `--servings` 错误值，每个都给出退出码 2 和一行提示。5,000 位的值给出这条提示，而不是 `ValueError`（选择 7 到 9）。`to_text` 碰不到 F02 的 4,300 位限制，因为文件里的数量最多 15 位，倍数最多是 100。 |
| 不和已有接口重复 | Pass | F09 调用 `is_recipe_id`、`list_recipe_ids`、`read_recipe`、`read_recipes`、`Catalog.find_tag`、`first_error`、`stop_at_error`、`format_table`、`display_width`、`and_list`、`comma_list`、`Quantity.scale`、`Quantity.to_text`、`BiText.get`、`Steps.get`、`MIN_SERVINGS` 和 `MAX_SERVINGS`，没有重新实现其中任何一个。以前没有接口从命令行读取整数。`read_servings` 检查的是 `tomllib` 给出的值，所以选择 8 对 `--servings` 文字的规则是新的，它留在 `browse` 内部，`browse` 是它唯一的使用者。`browse` 不能引用 `check`（架构 3），两个模块的 `RECIPE_COUNT` 各有自己的文字，所以这两条内部提示不是同一个接口写了两次。F09 只导出它的两个命令。`search` 与 `browse` 共用什么由 F10 的设计决定，架构 4 允许这样做。 |
| 只依赖排序在前面的功能 | Pass | F09 使用 F01 的 `units`、F01 和 F02 的 `lang` 与 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`，以及 F05 的 `app`、`cli`、`MIN_SERVINGS` 和 `MAX_SERVINGS`。它们都排在 F09 之前，并且在 main 上通过了测试。F05 是 F09 那一行的硬依赖，F01、F02 和 F04 是它的软依赖。F03 不在那一行里，但它排在 F04 之前，F04 通过它读取目录。`UNKNOWN_ID` 的后半句只以文字提到 F10 的 `search`，这段文字来自已批准的原型，设计也说明了在 F10 的 mock 之前这条命令行会给出什么。给 F10 的安排不约束任何后续设计。F09 只需要标准库，所以 R16 没有要审查的内容。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | `browse` 只通过 F03 和 F04 的读取函数访问磁盘，只写 `context.out` 和 `context.err`，既不用 `context.settings`，也不用 `context.today`。它只把它的两个 `Command` 值交给 `cli`。选择 2 说，让命令停下的错误一定在 `check` 的错误里。这来自两个模块用相同参数调用的读取函数，而不是它们之间的引用。选择 5 的列宽只取决于 `list` 读到的菜谱。自 0.2 版起，它们按格子的每一行来量，和 `format_table` 的规则 1 与规则 2 一样（F02 设计 2.9），所以没有 `--tag` 时不改变任何东西。选择 8 只依赖 F01 设计 2.9 承诺的内容，即一个等于 `TO_TASTE` 的值，而不依赖 `scale` 给出的是哪个对象。`show` 把 ID 与列表逐字比较，所以它不依赖 Windows 如何匹配文件名的大小写（架构 5.2）。A 点改的是测试数据，不是模块。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节写“无”是对的。模型没有改动 F01 到 F08 的任何模块，`COMMANDS` 里的两项是架构 4 给每个命令功能的改动。放进模型后，分支上的测试结果是 433 个通过、3 个跳过，也就是分支收集到的 436 个测试，包括 F05-T48、F05-T49、F07-T17 和 F08-T14。所以第 3 节关于这些测试的说法成立。A 点的方案 1 只改测试数据和一个测试。示例文件换成原型的四个步骤后，只有 F04-T38 失败，把它的数量改成 4 后，所有测试再次通过。把工作分成 mock 和实现是对的。mock 的 3 或 4 个文件在 R03 以内。它的 `run` 函数什么也不写、给出 0，也不抛异常，所以输出、退出码 1 或 `UsageError` 的每个测试在 mock 上都会失败（R09）。设计列出了会在 mock 上通过的测试，所以测试经理可以给每个这样的测试配上一个会失败的检查。实现在 `browse` 的内部文件里就能满足 R03，开发者可以把它拆成每个命令一个文件。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、F05 和 F09 原型、`example-data.md`，以及 v0.1-S10、v0.1-S12、v0.1-S20 到 v0.1-S23、v0.1-S28 和 v0.1-S29，检查了选择 1 到 10、A 到 C 三点，以及任务说明里的备注。两个文件的 828 行在标题、表格行和列表项上逐一对应，每个文件的 6 个 `python` 代码块都与另一种语言的版本相同。在模型上，示例、原型和分支上的测试都像第 1、2 和 6 项说的那样成立。架构师还用 `tests/pt01_support.py` 生成的 PT01 文件夹为模型计时，每个命令运行 5 次 `python -m recipe_menu`，在这台电脑上做了两轮。中位数是：`check` 0.835 秒和 0.843 秒，`list` 0.806 秒和 0.803 秒，`list --tag quick` 0.792 秒和 0.807 秒，`show recipe-0500` 0.165 秒和 0.160 秒，`--version` 0.147 秒和 0.144 秒。所以选择 10 的估计成立，不需要先做 `[refactor]` PR。`list` 大约还有 0.2 秒的余量，所以它的计时用例保持 F07-T25 在 Windows 上 1 秒的上限。有三个不阻塞的发现。发现 1：选择 5 和 2.2 取整个格子的 `display_width`。但名称里可以有换行，而 `format_table` 按格子的每一行来量。在模型上，一个由 `A long first line` 和 `end` 两行组成的名称，让名称列比 `format_table` 自己算的宽 4 列，所以“不改变任何东西”对它不成立。要求的修改：取每个格子各行中最大的 `display_width`，各行按 `format_table` 的规则 1 拆分。发现 2：选择 8 说 `Quantity.scale` 给出一个等于 `TO_TASTE` 的值，“而不是这个对象本身”。F01 设计 2.9 给出的是 `TO_TASTE`，代码给出数量本身，对 `parse_quantity` 读出的数量来说，它就是 `TO_TASTE`。要求的修改：说明 F01 承诺的是一个等于 `TO_TASTE` 的值，所以代码用 `is_to_taste` 或 `==` 检查它。发现 3：按项目的设置，`ruff format` 会改动 2.2 的第 385 行和第 396 行，以及 2.4 的第 755 行。其中两行超过 100 列（一个汉字算两列），另一行有转义的引号。这个 PR 本身没有运行测试，因为它不改代码。 | 批准。Troy 批准这份设计时，主会话把 A 到 C 三点交给 Troy（R18）。架构师同意每一点的建议。如果 A 点选方案 1，示例文件和 F04-T38 在 F09 的测试 PR，也就是 PR 4 里修改，测试计划写明这项修改。测试数据和已验收功能的测试属于测试阶段（R02、R08）。之后 F04-T38 通过，符合 R10 对已验收功能的要求，F09 的新测试在 mock 上仍然失败（R09）。架构师同意 B 点的新文字。对 C 点，退出码 2 正是架构 6 给错误参数值的退出码。F03 审查的备注只要求 `show` 从不把这样的值传给 `DataFolder.recipe_file`，选择 7 做到了这一点。接口设计师可以在 Troy 批准之前，把发现 1 到 3 放进这个 PR。否则，测试计划按发现 1 的规则写。 |
| 2 | 没有阻塞问题。架构师比较了两个文件的 0.2 版和 0.1 版。它们只在选择 5、2.2 里关于 `widths` 的那句话、选择 8、2.2 和 2.4 示例里的三行、版本号和修改记录的一行上不同，第 4 节和第 1 轮留下的一样。发现 1 已解决：`min_widths` 的每个宽度是格子各行中最大的 `display_width`，各行按 `format_table` 的规则 1 拆分，即 `cell.splitlines()`（F02 设计 2.9）。架构师用 F02 的 `format_table` 在四个菜谱上检查了这条规则，其中一个名称由 `A long first line` 和 `end` 两行组成。用这些宽度，完整的表格不变，只含其中一个菜谱的每个表格也保持完整表格的列。0.1 版的宽度会让完整的表格变宽。发现 2 已解决：选择 8 现在说的是 F01 设计 2.9 承诺的内容，那份设计的示例检查的是 `TO_TASTE.scale(Fraction(2)) == TO_TASTE`。发现 3 已解决：每个文件的 6 个 `python` 代码块与 0.1 版的语法树相同，所以没有示例改变含义，两个文件的代码块也仍然相同。`ruff format --check` 在这两个文件和它在仓库里检查的 238 个文件上都通过，这个 PR 的两个 CI 任务也都通过。加上这一行，两个文件各有 838 行，在标题、表格行和列表项上仍然逐一对应。 | 批准。每一项都通过。Troy 批准这份设计时，A 到 C 三点仍交给 Troy（R18），第 1 轮对它们的意见仍然成立。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-13 | 初稿。 |
| 0.2 | 2026-11-13 | 采纳架构师审查第 1 轮的三个发现。选择 5 和 2.2 按格子的各行取 `min_widths` 的每个宽度，各行按 `format_table` 的规则 1 拆分，所以没有 `--tag` 时，即使名称里有换行，这些宽度也不改变任何东西。选择 8 说明 F01 只承诺 `Quantity.scale` 给出一个等于 `TO_TASTE` 的值，所以代码用 `is_to_taste` 或 `==` 检查它，从不用 `is`。2.2 和 2.4 示例里的三行按 `ruff format` 的写法写出：两行折行，一行改用单引号。示例的含义都没有改变。 |
| 1.0 | 2026-11-13 | Troy 批准。 |
