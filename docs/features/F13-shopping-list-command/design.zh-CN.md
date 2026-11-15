---
troy-doc: "F13-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-15"
status: "Troy 已于 2026-11-15 批准"
mirror-of: "design.md"
---

# F13 购物清单命令：接口设计

## 1. 功能

- 编号和名称：F13 购物清单命令
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F02、F12

## 2. 接口

F13 在 `src/recipe_menu/commands/shop/` 里构建命令模块 `shop`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.shop` 导出一个名称 `SHOP_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出它。你输入的命令是 `recipe-menu shop`（2.2）。它的提示放在 `src/recipe_menu/commands/shop/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F13 在它的 mock PR 里把 `SHOP_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `MENU_SHOW_COMMAND` 之后。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F13 还给 `datafile` 加上替换文件的写入功能 `replace_file`，以及一条内部提示（第 3 节）。F13 原型 `docs/prototypes/F13-shop.md` 展示了这个命令，F05 原型展示了它在帮助里的那一行。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F13 提供的接口 |
| --- | --- |
| `recipe-menu shop [WEEK]` 用所选语言打印购物清单（[需求 4](../../requirements.zh-CN.md#4-功能点)）。 | `recipe-menu shop`（2.2），以及 `SHOP_COMMAND`（2.1）。它用 F12 的 `build_shopping_list` 生成清单，并按选择 4 的版式写出。 |
| 它把清单保存为 Markdown 勾选清单 `shopping/<week>.md`（需求 4）。 | 选择 5 的文件，通过 `replace_file`（3.1）写出。 |
| `shop` 只在 `shopping/` 里写它自己的文件，并替换同一周的文件。v0.1 不改动任何其他文件（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | `replace_file` 在 `shopping/` 里写一个临时文件，再把它移到这一周的文件上，`shop` 不写别的任何东西（选择 6，[架构 6](../../architecture.zh-CN.md#6-错误处理)）。 |
| 接受周的命令接受 ISO 周、`this` 或 `next`。不写周时，用本周（需求 3）。 | F06 的 `week_from_argument` 和 `NOT_A_WEEK`（选择 2）。 |
| 每条提示都跟随所选语言（需求 3）。 | 每段文字都来自 `shop/messages.py`、目录里的名称和 `amount_text`，用 `context.lang` 写出（选择 4、5 和 8）。 |
| 命令成功时以 0 退出，数据有错误或缺少文件时以 1 退出，命令行写错时以 2 退出（需求 3）。 | 2.2 的退出码表。 |
| 数据文件夹里有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`shop` 在 1 秒内结束（PT01，[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。 | 2.2 的性能指标，以及选择 10。 |

下面每个接口都遵守这些规则：

- `shop` 在包内只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`menus` 和 `shopping`。架构 3 里它那一行允许这些模块。它既不需要 `units`，也不需要 `settings`，而且从不引用 `menu`、`browse` 或其他命令模块（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `shop` 只通过 F03、F04 和 F06 的读取函数以及 `replace_file` 访问磁盘，这些函数都通过 `datafile` 工作（架构 8）。它只写这一周的清单文件、写这个文件时 3.1 的临时文件，以及在那个路径上什么都没有时的文件夹 `shopping/`（C 点）（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 1](../../architecture.zh-CN.md#1-背景和约束)）。它只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西，也不保存状态。它读到的菜谱和生成的清单只在一次运行里存在，所以没有模块保存缓存（架构 8）。
- 读取函数遇到坏数据从不抛异常，`replace_file` 把每个 `OSError` 变成一个值（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`shop` 在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。`run` 只为不是周的 `WEEK` 值抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出（F05 设计第 2 节）。传到 `cli` 的任何其他异常都是 bug。
- `SHOP_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。`replace_file` 给出 F11 的 `FileCreation`（F11 设计 3.2），所以 F13 不增加值类型。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- `recipe-menu shop` 有性能指标 PT01（选择 10）。它把需要的每个文件只读一次，把清单文件只写一次，并在写完文件之后一次写出输出。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和 3.1 给出它们的规则。

1. **一个命令，在帮助里排在 `menu show` 之后。** F13 把 `SHOP_COMMAND` 加在 `COMMANDS` 里 `MENU_SHOW_COMMAND` 的后面，也就是 F05 设计第 2 节帮助顺序里的最后一位。所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, SHOP_COMMAND)`。`shop` 有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它（F05 设计 2.5）。按 F05 设计的计划，它声明可选参数 `WEEK`，不声明选项。所以帮助写成 `shop [WEEK]` 和 `shop [周]`，分别占 11 列和 9 列。最宽的第一格仍然是 `menu show [WEEK]`，占 16 列，所以两种语言里，两张表的第二列仍然从第 21 列之后开始。帮助多出一行，共 21 行，这时它就是 F05 原型完整的两段帮助（2.1）。第 3 节列出检查真正帮助的测试，它们都仍然成立。
2. **周。** `shop` 像 F11 的命令那样得到它的周（F11 设计，选择 2）：`week_from_argument(value, context.today)`（F06 设计 2.7），其中 `value` 是 `WEEK` 的值，命令行没有给出时是 `None`。ISO 周、`this` 和 `next` 以外的文字，比如 `2026-W99`，给出 `UsageError(NOT_A_WEEK, None, week=value)`，`cli` 只写出这条提示，并以 2 退出（ADR-0008，决定 A）。`run` 在访问磁盘、写出任何输出之前抛出它。之后的每一行都用 `str(week)` 写出周，比如 `next` 写成 `2026-W47`。`shop` 只在 `week_from_argument` 给出周之后，才用 `context.folder.shopping_file(str(week))` 生成文件路径，所以这个名称总能通过 `shopping_file` 的检查；名称不对时，`shopping_file` 抛出 `ValueError`（F03 设计 2.1）。
3. **`shop` 读什么，在哪里停下。** `shop` 只读它需要的文件：`cli` 里的设置、目录、常备清单、菜单，以及只有菜单写到的那些菜谱（架构 8）。它按 `menu show` 的顺序读这些文件（F11 设计，选择 7），常备清单放在目录之后，这是 F11 和 F12 的设计为 F13 计划的做法（2.2）：
   - 它用 `read_catalog` 读目录，因为 `read_pantry` 和 `read_recipe` 需要目录（F03 设计 2.9，F04 设计 2.6）。
   - 它用 `read_pantry(context.folder, catalog)` 读常备清单。所以无论你要哪一周，常备清单里的错误都会让 `shop` 停下，就像目录里的错误那样。
   - 它用 `list_recipe_ids` 把 `recipes/` 列一次，并把这些 ID 作为 `frozenset` 传给 `read_week_menu`（F06 设计，选择 4）。
   - 它用 `list_menu_weeks` 把 `menus/` 列一次，在它给出的周里查找这一周（F06 设计 2.8）。这次列出的错误会让 `shop` 停下，即使错误写的是另一个文件，就像它会让 `menu show` 停下一样。列表里没有的周在错误流上给出 `menus` 的 `NO_MENU`（F11 设计 3.1），退出码 1。
   - 它用 `read_week_menu` 和 `context.settings` 读这一周（F06 设计 2.9）。
   - 它用 `read_recipe` 读每道菜写到的每个菜谱，每个只读一次，按第一道写到它的菜的顺序：周一到周日，各餐按 `menu.meals` 的顺序，菜按文件里的顺序。它把这些菜谱放在一个只在一次运行里存在的字典里，并把这个字典传给 `build_shopping_list`（F12 设计，选择 2）。菜单没写到的菜谱不解析，所以它里面的错误不会让 `shop` 停下。

   每个读取函数的第一个错误都会让 `shop` 用 `first_error` 和 `stop_at_error` 停下，它们写出这个问题和 `RUN_CHECK`，并给出 1（F05 设计 2.8）。`check` 用相同的读取函数、相同的参数读这些文件，所以让 `shop` 停下的错误一定在 `check` 的错误里（F07 设计，选择 8）。`shop` 不写出警告，警告也从不改变退出码（架构 6）。所以 `shop` 传给 `build_shopping_list` 的只有读取函数没有报错时给出的、来自同一个目录的值，它永远碰不到 F12 设计 2.5 的 `ValueError`。遇到错误或 `NO_MENU` 之后，`shop` 不再读任何东西，也不写任何文件。它从不读这一周的清单文件，也不读 `shopping/` 里的其他文件。

   `shop` 自己保留读取目录、并在读取函数的第一个错误处停下的那几行代码。正如 F11 实现的代码审查员指出的，同样的几行在 `browse`、`search` 和 `menu` 里重复。`shop` 不能引用这些模块（架构 3）。所以要共用这几行，就需要在四个模块都能引用的模块里，比如 `app`，新导出一个辅助函数；要去掉那些副本，还要改动 `browse`、`search` 和 `menu`，这是三个已经实现、而且不由 F13 构建的模块。即使不做这件事，F13 的 mock 和实现也已经接近 R03 的限制（第 2 节最后一段）。所以 F13 保留它自己的副本，以后可以用一个 `[refactor]` PR 加上这个辅助函数，并在四个命令里都使用它。出于同样的理由，`shop` 自己定义 `WEEK_ARGUMENT`、`MEAL_COUNT` 和 `DISH_COUNT`，文字与 `menu` 的内部提示相同（F11 设计 2.2 和 2.4）。
4. **终端里的清单。** 保存成功时的输出有四块，两块之间隔一个空行：标题行、各个分组、常备食材那一行，以及写出已保存文件的那一行（2.2）。
   - 标题行是 `LIST_HEADING`，带有这一周、它的 `date_range`（F06 设计 2.1），以及清单的计数 `meal_count` 和 `dish_count`（F12 设计，选择 9），计数用 `MEAL_COUNT` 和 `DISH_COUNT` 写出。它们是 `Plural` 值（F02 设计 2.4），所以一餐和一道菜时英文也是对的，和 F11 的计数行一样。
   - 各个分组按 `shopping.groups` 的顺序排列（F12 设计，选择 1）。每个分组先写它所属分类的名称 `group.category.name.get(context.lang)`，不缩进。然后分组里的每个 `ShoppingLine` 占一行：两个空格、食材名称 `line.ingredient.name.get(context.lang)`（补齐到整份清单里最宽名称的宽度）、三个空格，以及 `line.amount_text(context.lang)`（F12 设计 2.2）。
   - 每个分组的各行是 `format_table(rows, indent=2, min_widths=(width,))`（F02 设计 2.9），其中 `width` 是整份清单里名称的最大 `display_width`。所以所有分组的数量都从同一列开始，就像帮助的两张表一样（F05 设计 2.10）。架构师在 F02 的审查里建议，所有分组用一张表，把标题放在各行之间；只要没有格子带换行，这样就行得通。目录里的名称可能带换行，这时 `format_table` 让这一行占两行，所以每个分组一张表、用同一个宽度，能让每个标题都在它的位置上，其他情况下给出的各行完全相同。
   - 原型里最宽的名称是 `Chicken wings`（13 列）和 `郫县豆瓣酱`（10 列）。所以数量从缩进之后的第 16 列和第 13 列之后开始，和原型显示的一样。别的周用它自己名称的宽度，和 `menu show`、`search` 一样（F11 设计，选择 8）。
   - 名称按目录里的样子写出，就像 `menu show` 写出菜谱名称那样。缺少所选语言的名称通过 `BiText.get` 显示另一种语言。
5. **保存的文件。** 文件就是 F13 原型“The saved file”里的 Markdown 勾选清单，用运行时的语言写出：“A run in English writes the same list in English.”它的文字由下面几块组成，两块之间隔一个空行，每行以 LF 结尾（2.2）：
   - 标题，`# ` 加上 `FILE_TITLE`，比如 `# 2026-W47 购物清单`；
   - 日期和计数那一行 `FILE_DATES`，比如 `2026年11月16日至22日：4 餐，9 道菜。`；
   - 每个分组先是标题 `## ` 加上分类名称，然后是一块文字，每个 `ShoppingLine` 一行：`- [ ] `、食材名称、一个空格和 `amount_text`，比如 `- [ ] 番茄 600 g`；
   - 菜单用到常备食材时，选择 8 的常备食材那一行。

   文件是 UTF-8，没有字节顺序标记，用 LF 换行（架构 5.1）。所以示例那一周用中文运行之后，文件的字节就是原型里的文件；用英文运行时，文件开头是 `# Shopping list for 2026-W47` 和 `16 to 22 November 2026: 4 meals, 9 dishes.`（A 点）。`# `、`## ` 和 `- [ ] ` 是不属于任何语言的 Markdown 符号，所以它们写在代码里，不是提示，名称也不做 Markdown 转义（架构 8）。每次运行都替换这一周的文件，所以你在手机上勾选过的清单，在你为这一周再运行一次 `shop` 时会失去勾选，这正是需求 3 的说法：`shop`“替换同一周的文件”。
6. **`shop` 怎样保存文件。** 每个文件都由 `datafile` 写（架构 2、3 和 8）。`create_file` 拒绝已经存在的条目，所以 `shop` 不能用它（ADR-0010）。于是 F13 给 `datafile` 加上 `replace_file(folder, path, text)`（3.1），也就是架构 6 给要替换的文件规定的写法：在同一个文件夹里写一个临时文件，再把它移到旧文件上。`shop` 调用它一次，`path = context.folder.shopping_file(str(week))`，文字是选择 5 的文字。`replace_file` 按这些步骤执行：
   1. 它确保文件所在的文件夹存在。`shopping` 那里什么都没有时，它只创建这一个文件夹（C 点）。那里有个不是文件夹的东西时，它给出 `FAILED`。
   2. 之前的运行留下了临时文件 `shopping/2026-W47.md.tmp` 时，比如停电之后，它删除这个文件。
   3. 它用独占模式创建临时文件，用一次 `write` 写入全部文字，然后关闭它。
   4. 它用 `os.replace` 把临时文件移到 `shopping/2026-W47.md` 上，这一步一次替换掉旧文件。

   `shop` 按结果处理：
   - **`CREATED`。** `shop` 把选择 4 的输出写到输出流，并给出 0。最后一行是带文件完整路径 `str(path)` 的 `SAVED`，和原型显示的一样。
   - **`FAILED`。** `shop` 向错误流写出三行，并给出 1，输出流上什么都没有。第一行是清单文件的完整路径 `str(context.folder.root / problem.file)`，因为 `replace_file` 的每个问题写的都是它没能写成的文件。架构 6 和 ADR-0009 第 3 节允许 `shop` 用完整路径写出它没能写成的文件，这份设计采用这种情况，并按 ADR-0009 第 5 节的要求写明这一点。第二行是两个空格加上 `problem.text(context.lang)`，比如 F08 的 `FILE_WRITE_DENIED`，`The file cannot be written: access is denied.`。第三行是 `NO_FILE_SAVED`，`No file was saved.`；`replace_file` 没能删除临时文件时，第三行是带临时文件完整路径的 `LEFT_BEHIND`（A 点）。输出流上没有清单：屏幕上的每份清单都以写明文件位置的那一行结尾。
   - **旧文件保持不变。** 只有移动这一步会改变这一周的文件，所以只要 `replace_file` 给出 `FAILED`，旧文件就保持原来的字节，读这个文件的人看到的要么是旧文字，要么是新文字，绝不会是一部分。另一个程序，比如同步工具或编辑器，正打开着这个文件时，Windows 可能拒绝移动。这时 `shop` 报告 `The file cannot be written: access is denied.`，你再运行一次 `shop`。
   - **Ctrl+C。** `replace_file` 在 `finally` 块里删除临时文件，`cli` 以 130 退出，不再写出任何东西（F05 设计 2.10）。所以按 Ctrl+C 之后，留下的要么是完整的旧文件，要么是完整的新文件。和 `init`、`menu new` 一样，在 `open` 内部、系统已经创建了临时文件但调用还没记下它的时候按 Ctrl+C，可能留下这个文件（F08 设计，选择 5）。下次为这一周运行 `shop` 时，它会在写入之前删除这个文件（3.1 第 3 步）。
7. **一道菜也没有的周，以及没有要买的东西的清单。** 一道菜也没有的菜单给出 `dish_count` 为 0 的清单（F12 设计，选择 9）。这时 `shop` 把原型里的那一行 `NO_DISHES`，`The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.`，写到输出流，并给出 0。它不调用 `replace_file`，所以不创建文件夹，也不写文件，这一周原有的文件（如果有）保持不变（v0.1-S14）。各道菜只用到常备食材，或者只用到没有食材的菜谱时，菜单给出有菜但没有分组的清单。这时 `shop` 写出标题行，用 `NOTHING_TO_BUY`，`There is nothing to buy.`，代替各个分组，菜单用到常备食材时写出常备食材那一行，最后写出 `SAVED`。它保存文件，文件里同样用 `NOTHING_TO_BUY` 代替各个分组。这一周有菜，所以它的文件要跟随它的菜单：如果不保存，这一周按旧菜单生成的清单会留着菜单已经不需要的东西。`There is nothing to buy.` 这一行是新的，由 Troy 决定（A 点）。
8. **常备食材那一行。** 这一行写出菜单用到的常备食材，按 `shopping.pantry_used` 的顺序（F12 设计，选择 6）：`PANTRY_LINE`，带上这些名称的 `comma_list`（F02 设计 2.6）。中文那一行就是原型里的 `常备，不用买：食用油、盐、糖、生抽、花椒`。原型的英文那一行写的是 `cooking oil, salt, sugar, soy sauce, Sichuan pepper`，v0.1-S16 要求的是 `cooking oil, salt, sugar`。目录写的是 `Cooking oil`、`Salt`、`Sugar`、`Soy sauce` 和 `Sichuan pepper`，没有哪条规则能把这些名称变成原型里的那一行（F03 设计第 2 节）。这一行由 Troy 决定（B 点）。这份设计采用推荐的做法 1：按目录的写法写出名称，`Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper`。菜单没有用到常备食材时，终端和文件里都没有常备食材那一行。
9. **提示里的数字。** `shop` 的提示显示餐数和菜数，它们是 F12 在内存里数出来的，以及一周的日期，它们来自 `IsoWeek`。数量通过 `amount_text` 放进一行，不经过提示；对 `build_shopping_list` 给出的行，`amount_text` 从不抛异常（F12 设计，选择 10）。错误的周作为文字放进 `NOT_A_WEEK`。文件里的问题只通过 `stop_at_error` 或选择 6 的失败各行写到错误流，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `shop` 的提示不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。
10. **速度。** PT01 要求 `shop` 为一个 PT01 周生成并保存清单，在 Troy 的电脑上在 1 秒内完成，取 5 次运行的中位数（v0.1-S32）。这一周有来自 63 个不同菜谱的 63 道菜。`shop` 读的是 `menu show` 读的东西，再加上 10 项的常备清单，而 `menu show 2026-W26` 在 Troy 的电脑上的中位数是 0.187 秒（F11 的 PT01 基线）。`build_shopping_list` 在这一周上的中位数是 5.19 毫秒（F12 的实现），给出 6 个分组里约 290 行。`amount_text` 用一种语言写这些行约耗 1 毫秒，F12 的审查测得两种语言共 1.9 毫秒。`format_table` 把约 290 行、每行两个短格子量一次，Markdown 文字把同样的行再写一次。`replace_file` 做一次探测、一次删除不存在的文件、一次打开、一次约 10 KB 的 `write`、一次关闭和一次移动，共耗几毫秒。在 F12 的设计审查里，一个替身 `shop` 读这些文件、生成清单、打印清单并写出一个 Markdown 文件，在 Troy 的电脑上的中位数是 0.222 秒，同一批运行里 `menu show` 是 0.209 秒。所以 `shop` 应该约耗 0.2 秒，远低于 1 秒。这是估计，不是测量结果。测试计划可以在 PT01 文件夹上为 `shop` 计时，就像 F11-T38 为 `menu show` 计时一样。`tests/pt01_support.py` 的 PT01 文件夹没有 `shopping/`，所以第一次运行会创建它（选择 6），之后的运行替换文件。
11. **只导出这个命令。** `shop` 导出 `SHOP_COMMAND`，别的什么都不导出。只有 `cli` 可以引用 `shop`（架构 3），所以其他名称不会有使用者。

运行 `shop` 的 v0.1 场景在这些选择下都成立，只有英文的常备食材那一行除外，B 点把它交给 Troy：

- v0.1-S08：带字节顺序标记、用 CRLF 换行的文件读起来一样（F03 设计 2.3），所以 `shop 2026-W47` 打印 F13“In English”的输出，并以 0 退出。保存的文件是 UTF-8，没有字节顺序标记，用 LF 换行（选择 5）。
- v0.1-S14：`shop` 和 `shop next` 读 `menu new` 创建的两个空菜单，打印带 `<T>` 和 `<N>` 的 `NO_DISHES`，并以 0 退出。`shopping\` 保持为空（选择 7）。
- v0.1-S15：第 3 步为 2026-W48 打印 `NO_MENU`，并以 1 退出。第 5 步打印和 `menu show` 对 `tomato-eggs` 相同的三行，并以 1 退出，因为在读到菜单之前，`shop` 读的文件和 `menu show` 相同，而在它们之前读的常备清单没有错误（选择 3）。`shopping\` 保持为空。
- v0.1-S16：`shop 2026-W48` 以 `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish` 开头，在 Vegetables and fruit 下列出 Tomato 450 g 和 Scallion 2 stalks，然后在 Eggs, dairy, and tofu 下列出 Egg 5 pieces，并以 0 退出。它的常备食材那一行按 B 点处理。按做法 1，这一行以 `Cooking oil, Salt, Sugar` 结尾，场景要求的那一行随原型一起修改。
- v0.1-S17：第 1 步打印 F13“In English”的输出，并保存英文清单，每项一行 `- [ ]`。第 2 步打印 F13“In Chinese”的输出，并把文件逐字节替换成原型里的文件。之后 `shopping\` 里只有这个文件，因为移动不留下临时文件（选择 4 到 6）。
- v0.1-S18：Scallion 和 Soy sauce 两行显示 `5 stalks + 1 bunch` 和 `30 ml + 10 g`，中文运行显示 `5 根 + 1 把`，这些都由 `amount_text` 写出（F12 设计，选择 4）。
- v0.1-S23：两次运行 `shop 2026-W47` 只改变 `shopping\2026-W47.md`，`shopping\` 里没有别的文件。文件夹 `shopping\` 得到新的修改时间，就像文件夹里有文件被添加或替换时一样。
- v0.1-S25：中文清单在 Windows Terminal 里是对齐的，因为 `format_table` 按显示宽度测量（F02 设计 2.8）。
- v0.1-S26：保存的中文文件就是原型里的勾选清单，有标题、六个分类、14 项和常备食材那一行，用 UTF-8 编码。
- v0.1-S32：PT01（选择 10）。这次运行打印清单并保存它的文件。

这三点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 没有原型展示这些文字。每一段都沿用某个原型里文字的措辞。建议按 2.2 和 3.1 的写法接受它们。共 11 段文字：
  - 英文文件的开头，对应原型里的中文文件：`# Shopping list for 2026-W47` 和 `16 to 22 November 2026: 4 meals, 9 dishes.`。
  - 一道菜也没有的周的中文那一行：`2026-W46 的菜单没有菜，所以没有要买的东西。没有保存文件。`。
  - 没有要买的东西时清单里的那一行（选择 7）：`There is nothing to buy.` 和 `没有要买的东西。`。
  - 保存失败时的最后一行（选择 6）：`No file was saved.` 和 `没有保存文件。`，也就是原型里一道菜也没有的周那一行的后半句。没能删除临时文件时：`No file was saved, but shop could not remove C:\Users\Troy\recipe-menu\shopping\2026-W47.md.tmp. Delete it.` 和 `没有保存文件，但 shop 没能删除 C:\Users\Troy\recipe-menu\shopping\2026-W47.md.tmp。请删除它。`。
  - `shopping` 不是文件夹时的问题（3.1）：`The file cannot be written: "shopping" is not a folder.` 和 `无法写入文件：“shopping”不是文件夹。`。
- **B. 英文的常备食材那一行**（选择 8）。原型的英文那一行把四个目录名称写成小写开头，却保留了 `Sichuan pepper`，v0.1-S16 要求的是 `cooking oil, salt, sugar`。原型和场景归 Troy 所有，所以修改它们要走 Troy 批准的需求变更流程。
  - 做法 1，推荐：按目录的写法写出名称：`Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper`。F13 原型的英文常备食材那一行，以及 v0.1-S16 要求的那一行 `Cooking oil, Salt, Sugar`，都要修改。v0.1-S08 和 v0.1-S17 与原型比较，所以随原型变化。产品经理在 F13 测试计划之前，用一个 Troy 批准的 `[docs]` PR 做这个修改。目录和 F03 的代码保持不变。
  - 做法 2：目录给食材加第二个英文名，专用于句子里，比如 `cooking oil`，目录给出它时，这一行就用它。F13 原型和场景保持不变。`example-data.md` 里的目录要加上这些名称，`init` 写出的和测试复制的都是这个目录；`Ingredient`、`read_catalog`（F03）和它们的测试也要修改，这些都在 F13 的 mock PR 之前走变更流程。然后这份设计修改选择 8。
  - 做法 3：这一行里每个英文名称都改成小写开头：`cooking oil, salt, sugar, soy sauce, sichuan pepper`。v0.1-S16 保持不变，原型里最后一个名称通过变更流程改成 `sichuan pepper`。这样，目录里的专有名词或缩写在这一行里会写错。
  - 推荐做法 1 的理由：这一行按你在目录里的写法写出每个名称，就像清单的标题和各行那样，所以永远不会写错名称，也不需要改动任何文件或读取函数。架构师在 F03 的审查里推荐过这个做法。
- **C. 缺少 `shopping` 文件夹**（选择 6），这是从需求阶段就待定的问题。`shopping\` 由 `init` 创建，你也可以删掉它。Git 不保留空文件夹，测试的示例数据和测试用的 PT01 文件夹里都没有 `shopping\`。
  - 做法 1，推荐：文件所在的路径上什么都没有时，`replace_file` 用一次不带上级目录的 `Path.mkdir` 创建这个文件夹。后面的步骤失败时，它创建的文件夹保留下来。那里有个不是文件夹的东西时，`shop` 写出失败的各行和 `The file cannot be written: "shopping" is not a folder.` 后停下。
  - 做法 2：`replace_file` 不创建文件夹。`shopping` 那里什么都没有时，给出 `FAILED`，带 F04 的 `FOLDER_MISSING`，`The folder is missing.`，写在清单文件的完整路径下面。你创建这个文件夹，再运行一次 `shop`。选择 6、3.1 和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：只有 `shop` 往 `shopping\` 里写（需求 3），也没有命令读它，所以创建这个文件夹不会改动你写的任何东西。丢了空 `shopping\` 的数据文件夹，比如一份副本或放在 git 里的文件夹，照样能得到清单。两种做法都不修改需求：需求 3 说的是 `shop` 写和替换的文件，而文件夹不是文件。

这些后续功能会在 F13 的基础上构建。细节由它们自己的设计决定。

- F14 的 `menu suggest`（v0.2）填满已有菜单文件里的空餐次，所以它要替换这个文件。它可以照原样用 `replace_file` 写这个文件。`suggest` 不能引用 `shop`（架构 3），而 `shop` 只导出它的命令，所以 F14 不从 F13 拿别的东西。
- F15 的 `add` 用从不覆盖的 `create_file` 写新菜谱，F16 的 `edit` 不写文件。两者都不从 F13 拿任何东西。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/shop/__init__.py`、`messages.py`、放 `run` 的一个内部文件（比如 `_run.py`），以及 `src/recipe_menu/cli/_commands.py` 里的那一项。它把 `replace_file` 加进 `datafile` 的一个新的内部文件（比如 `_replace.py`）和 `src/recipe_menu/datafile/__init__.py`，把 `PARENT_NOT_A_FOLDER` 加进 `src/recipe_menu/datafile/messages.py`。它修改 `src/recipe_menu/datafile/_new_file.py` 里 `FileOutcome` 和 `FileCreation` 的文档注释，让它们也写到 `replace_file`。它定义每条提示和字段齐全的 `SHOP_COMMAND`。它的 `replace_file` 什么都不碰，给出 `FileCreation(FileOutcome.CREATED)`，它的 `run` 不读文件、不写任何东西、不抛异常，并给出 0。所以检查输出的某一行、退出码 1、带退出码 2 的 `NOT_A_WEEK`、保存的文件的字节、新建的 `shopping\`、失败及其各行、`FAILED` 结果或 `replace_file` 的问题，或者 `replace_file` 抛出的错误的新测试，在 mock 上都会失败（R09）。这些测试在 mock 上会通过，从而违反 R09：只检查 `SHOP_COMMAND` 的字段、帮助、某条提示或退出码 0 的测试。检查 `cli` 在运行 `shop` 之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、`shop 2026-W47 2026-W48`、`shop --tag x` 或 `shop next --help`。只检查 `shop` 不改变任何文件（比如一道菜也没有的周、`NO_MENU` 或错误时），或者只检查 `shopping\` 保持为空（比如 v0.1-S14 和 v0.1-S15 那样）的测试也是如此。只检查保存失败时保留了旧文件，或者只检查 `replace_file` 给出 `CREATED` 的测试也是如此。每个这样的测试都还要检查 mock 做错的内容，比如输出、文件或结果。按估计，mock 改动 8 个文件，约 280 行，文件数超过 R03 的 5 个，所以它的说明要写明软限制的理由。理由是测试既直接用到 `replace_file`，也通过 `shop` 用到它，所以 `shop` 和 `datafile` 要在同一个阶段一起带上，和 F08、F11 的 mock 一样。实现（PR 5）把带读取和输出的 `run` 放在 `shop` 的内部文件里，比如 `_run.py`、`_read.py` 和 `_output.py`，并把 `replace_file` 放在 `_replace.py` 里。按估计，它改动 4 个文件，约 450 行，在 R03 以内，但接近它的 500 行。`_replace.py` 可以像 `_new_file.py` 那样从 `_creation.py` 引用 `_remove_all`，不需要改动 `_creation.py`。如果文档注释让它超过 500 行，它的说明要写明软限制的理由，所以开发工程师要早一点运行 troy-check。

### 2.1 `SHOP_COMMAND`

- 模块：shop
- 功能：对 `shop` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 生成 2.2 的清单并保存它。

签名：

```python
SHOP_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("shop",)
#   help_line = SHOP_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("shop",)`。 | 无 |
| `help_line` | `Message` | `SHOP_HELP`：“Make the shopping list of a week menu.”和“生成一个周菜单的购物清单。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 把参数变成周，读选择 3 的文件，生成清单，通过 `replace_file` 保存它，并写出 2.2 的输出。 | 给出 0 或 1。为不是周的值抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出。遇到坏数据或磁盘上的失败时不抛异常。 |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`，它是可选的，不能重复。`WEEK_ARGUMENT` 是 `WEEK` 和 `周`，也就是 F05 原型帮助里的名称。 | 所以 `cli` 不传值或传入一个值（F05 设计 2.5）。 |
| `options` | `str` 的元组 | `()`。`shop` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `shop`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、`context.folder`、给 `read_week_menu` 用的 `context.settings`、`context.out`、`context.err` 和 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `shop` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `()` 或只有一个值，比如 `("next",)`。它没有选项。 |

- 返回值：`SHOP_COMMAND`，一个 `Command`。
  - `SHOP_COMMAND.usage` 英文是 `shop [WEEK]`，中文是 `shop [周]`。所以帮助显示它们，用法错误引用 `recipe-menu shop [WEEK]` 或 `recipe-menu shop [周]`。
  - `SHOP_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出各行，并给出 0 或 1。

F13 之后，帮助列出这些命令和选项，第二列从第 21 列之后开始（选择 1）。它们就是 F05 原型帮助里的各行。英文：

```text
Commands:
  init               Create the data folder with example data.
  check              Check every data file for mistakes.
  list               List the recipes.
  show ID            Show one recipe.
  search WORD...     Find recipes by name, ingredient, or tag.
  menu new [WEEK]    Create an empty week menu.
  menu show [WEEK]   Show a week menu.
  shop [WEEK]        Make the shopping list of a week menu.

Options:
  --lang en|zh       The language of the output. Default: the settings, else English.
  --data FOLDER      The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version          Show the version.
  --help             Show this help.
```

中文：

```text
命令：
  init               创建数据文件夹和示例数据。
  check              检查每个数据文件有没有错误。
  list               列出菜谱。
  show ID            查看一个菜谱。
  search 词...       按名称、食材或标签找菜谱。
  menu new [周]      创建一个空的周菜单。
  menu show [周]     查看一个周菜单。
  shop [周]          生成一个周菜单的购物清单。

选项：
  --lang en|zh       输出语言。默认：设置里的语言，否则英文。
  --data 文件夹      数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version          显示版本。
  --help             显示这份帮助。
```

错误：

`run` 在访问磁盘之前把参数变成周。

| 错误 | 何时发生 |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | 对 `WEEK` 的值，`week_from_argument` 给出 `None`（选择 2）。 |

- 副作用：与 2.2 相同。`run` 通过 F03、F04 和 F06 的读取函数读目录、常备清单、两个列表、一个菜单文件和菜单写到的菜谱，通过 `replace_file` 保存清单，并写入 `context.out` 或 `context.err`。
- 性能指标：无。PT01 为 `recipe-menu shop`（2.2）从启动到退出计时，它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，里面没有 `shopping/`，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里是默认设置，也就是示例的设置，输出跟随 `context.lang`。这次运行给出 F13 原型“In English”的输出，常备食材那一行按 B 点的做法 1，并创建 `shopping/`（C 点的做法 1）。`row` 写出分组里的一行，名称宽 13 列（选择 4）。英文清单里每个字符都占一列，所以用 `str` 补空格得到的各行和 `format_table` 相同。帮助来自 `COMMANDS`，F13 之后它有八个命令。抛出异常的那次调用不碰任何文件，也不向任何流写出一行。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.shop import SHOP_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SHOP_COMMAND.words == ("shop",)
assert SHOP_COMMAND.usage == BiText("shop [WEEK]", "shop [周]")
assert SHOP_COMMAND.help_line.render(Lang.EN) == "Make the shopping list of a week menu."
assert SHOP_COMMAND.help_line.render(Lang.ZH) == "生成一个周菜单的购物清单。"
assert SHOP_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert SHOP_COMMAND.options == ()
assert SHOP_COMMAND.folder is FolderUse.READ


def row(name: str, amount: str) -> str:
    return f"  {name:13}   {amount}"


out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert SHOP_COMMAND.run(context, Arguments(("next",))) == 0
file = folder.shopping_file("2026-W47")
pantry = "Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper"
assert out.getvalue().splitlines() == [
    "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes",
    "",
    "Vegetables and fruit",
    row("Tomato", "600 g"),
    row("Choy sum", "1.5 kg"),
    row("Scallion", "5 stalks"),
    row("Ginger", "6 slices"),
    row("Garlic", "11 cloves"),
    "Meat and seafood",
    row("Minced pork", "100 g"),
    row("Chicken wings", "1 kg"),
    "Eggs, dairy, and tofu",
    row("Egg", "5 pieces"),
    row("Tofu", "1 block"),
    "Rice, flour, and oil",
    row("Rice", "640 g"),
    row("Noodles", "200 g"),
    "Seasonings",
    row("Doubanjiang", "15 ml"),
    row("White pepper", "to taste"),
    "Other",
    row("Cola", "2 cans"),
    "",
    f"Not on the list, because they are in the pantry: {pantry}",
    "",
    f"Saved {file}",
]
assert err.getvalue() == ""
text = file.read_bytes().decode("utf-8")
assert text.splitlines()[:7] == [
    "# Shopping list for 2026-W47",
    "",
    "16 to 22 November 2026: 4 meals, 9 dishes.",
    "",
    "## Vegetables and fruit",
    "",
    "- [ ] Tomato 600 g",
]
last = f"- [ ] Cola 2 cans\n\nNot on the list, because they are in the pantry: {pantry}\n"
assert text.endswith(last)
assert "\r" not in text
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]


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
assert len(english) == 21
assert english[11:13] == [
    "  menu show [WEEK]   Show a week menu.",
    "  shop [WEEK]        Make the shopping list of a week menu.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[11:13] == [
    "  menu show [周]     查看一个周菜单。",
    "  shop [周]          生成一个周菜单的购物清单。",
]

SHOP_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu shop`

- 模块：shop
- 功能：用所选语言打印一个周菜单的购物清单，并把它保存为 Markdown 勾选清单 `shopping/<week>.md` 的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 的流程 4，以及 [4](../../requirements.zh-CN.md#4-功能点)）。F13 原型展示了它。

签名：

```text
recipe-menu shop [WEEK] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `WEEK` | 文字 | 菜单所属的周：`2026-W47` 这样的 ISO 周、`this` 或 `next`。 | 可选。不写时为本周。其他文字都是用法错误（选择 2）。 |
| `--lang` | `en` 或 `zh` | 输出、保存的文件和每条提示的语言。 | 按 F05 设计 2.10 的规定。不写这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10 的规定。不写这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `shop`。 | 无 |

`shop` 按顺序执行这些步骤。第 1 步不读文件。每个读文件的步骤都使用前面步骤给出的东西，发现错误的步骤会让命令停下（选择 3）。

1. 它用 `week_from_argument(value, context.today)` 把 `WEEK` 的值变成周。结果是 `None` 时，它抛出 `UsageError(NOT_A_WEEK, None, week=value)`（选择 2）。
2. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`shop` 对第一个错误给出 `stop_at_error(context, error)`。
3. `read_pantry(context.folder, catalog)` 给出 `pantry` 和它的问题（F03 设计 2.9）。问题里有错误时，`shop` 用 `stop_at_error` 在第一个错误处停下。
4. `list_recipe_ids(context.folder)` 给出 `ids` 和它们的问题（F04 设计 2.5）。问题里有错误时，`shop` 用 `stop_at_error` 在第一个错误处停下。
5. `list_menu_weeks(context.folder)` 给出 `weeks` 和它们的问题（F06 设计 2.8）。问题里有错误时，`shop` 用 `stop_at_error` 在第一个错误处停下。
6. `weeks` 里没有这一周时，`shop` 把带 `week=str(week)` 的 `NO_MENU` 写到错误流，并给出 1（F11 设计 3.1）。
7. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` 给出 `menu` 和它的问题（F06 设计 2.9）。问题里有错误时，`shop` 用 `stop_at_error` 在第一个错误处停下。
8. 对 `menu` 里的菜写到的每个菜谱 ID，每个一次，按第一道写到它的菜的顺序，`read_recipe(context.folder, catalog, recipe_id)` 给出菜谱和它的问题（F04 设计 2.6）。问题里有错误时，`shop` 用 `stop_at_error` 在第一个错误处停下。
9. `build_shopping_list(menu, recipes, catalog, pantry)` 给出 `shopping`，其中 `recipes` 把第 8 步的每个 ID 对应到它的菜谱（F12 设计 2.5）。
10. `shopping.dish_count` 为 0 时，`shop` 把带 `week=str(week)` 的 `NO_DISHES` 写到输出流，并给出 0（选择 7）。
11. 它生成文件的文字（见下文），并调用一次 `replace_file(context.folder, path, text)`，其中 `path = context.folder.shopping_file(str(week))`（3.1）。
12. 对 `CREATED`，它把下面的输出写到输出流，并给出 0。对 `FAILED`，它把失败时的三行写到错误流，并给出 1（选择 6）。

第 2 到 5 步、第 7 步和第 8 步的警告不改变任何东西（选择 3）。

- 返回值：退出码，输出写在它对应的流上：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `replace_file` 给出 `CREATED`。 | 输出流：清单、有常备食材时的那一行，以及 `SAVED`。 |
| 0 | 这一周的菜单一道菜也没有。 | 输出流：`NO_DISHES`。不写任何文件。 |
| 1 | 这一周没有菜单文件。 | 错误流：`NO_MENU`。输出流上什么都没有。 |
| 1 | 某个文件有错误。 | 错误流：`stop_at_error` 的三行。输出流上什么都没有。 |
| 1 | `replace_file` 给出 `FAILED`。 | 错误流：失败时的三行。输出流上什么都没有。 |
| 2 | `WEEK` 的值不是周。 | 错误流：`cli` 写出的 `NOT_A_WEEK`，不带下一行。输出流上什么都没有。 |

`lang` 是 `context.lang`。`width` 是清单里名称各行的最大 `display_width`，名称指每个分组每一行的 `line.ingredient.name.get(lang)`，每个名称用 `str.splitlines` 分行。保存成功时的输出由下面几块按顺序组成，两块之间隔一个空行，每行以换行结尾：

1. `LIST_HEADING`，带 `week`、`dates`、`meals` 和 `dishes`。
2. `shopping.groups` 不为空时，按顺序对每个分组：先是 `group.category.name.get(lang)` 那一行，然后是 `format_table(rows, indent=2, min_widths=(width,))` 的各行，其中 `rows` 按顺序为分组的每一行放一个 `(line.ingredient.name.get(lang), line.amount_text(lang))`。`shopping.groups` 为空时，是 `NOTHING_TO_BUY`。
3. `PANTRY_LINE`，带 `items`，只在 `shopping.pantry_used` 不为空时出现。
4. `SAVED`，带 `file`。

文件的文字由下面几块按顺序组成，两块之间隔一个空行，每行以 LF 结尾：

1. `# ` 加上带 `week` 的 `FILE_TITLE`。
2. `FILE_DATES`，带 `dates`、`meals` 和 `dishes`。
3. `shopping.groups` 不为空时，按顺序对每个分组：先是 `## ` 加上 `group.category.name.get(lang)` 那一行，然后是它的各行组成的一块，分组的每一行按顺序占一行：`- [ ] `、`line.ingredient.name.get(lang)`、一个空格和 `line.amount_text(lang)`。`shopping.groups` 为空时，是 `NOTHING_TO_BUY`。
4. `PANTRY_LINE`，带 `items`，只在 `shopping.pantry_used` 不为空时出现。

所以示例那一周用中文运行之后，文件就是 F13 原型“The saved file”里的那一块文字，每一行都以 LF 结尾，最后一行也是。失败时是三行：`str(context.folder.root / problem.file)`，也就是 `str(path)`，然后是两个空格加上 `problem.text(lang)`，然后是：结果的 `left` 为空时是 `NO_FILE_SAVED`，否则是带 `file` 的 `LEFT_BEHIND`。在下面这个 Windows 上的例子里，另一个程序正打开着旧文件：

```text
PS> recipe-menu shop next
C:\Users\Troy\recipe-menu\shopping\2026-W47.md
  The file cannot be written: access is denied.
No file was saved.
PS> $LASTEXITCODE
1
```

`shop` 的提示如下。`MEAL_COUNT` 和 `DISH_COUNT` 是 `Plural` 值（F02 设计 2.4），各自按它的 `count` 选择。它们“更多”的形式用于 1 以外的每个计数。`shop` 还使用 `menus` 的 `NO_MENU`（F11 设计 3.1），以及读取函数和 `replace_file` 给出的问题。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `SHOP_HELP` | `Make the shopping list of a week menu.` | `生成一个周菜单的购物清单。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `LIST_HEADING` | `Shopping list for {week}, {dates}: {meals}, {dishes}` | `{week} 购物清单，{dates}：{meals}，{dishes}` |
| `MEAL_COUNT`，一个时 | `{count} meal` | `{count} 餐` |
| `MEAL_COUNT`，更多时 | `{count} meals` | `{count} 餐` |
| `DISH_COUNT`，一个时 | `{count} dish` | `{count} 道菜` |
| `DISH_COUNT`，更多时 | `{count} dishes` | `{count} 道菜` |
| `NOTHING_TO_BUY` | `There is nothing to buy.` | `没有要买的东西。` |
| `PANTRY_LINE` | `Not on the list, because they are in the pantry: {items}` | `常备，不用买：{items}` |
| `SAVED` | `Saved {file}` | `已保存 {file}` |
| `NO_DISHES` | `The menu for {week} has no dishes, so there is nothing to buy. No file was saved.` | `{week} 的菜单没有菜，所以没有要买的东西。没有保存文件。` |
| `FILE_TITLE` | `Shopping list for {week}` | `{week} 购物清单` |
| `FILE_DATES` | `{dates}: {meals}, {dishes}.` | `{dates}：{meals}，{dishes}。` |
| `NO_FILE_SAVED` | `No file was saved.` | `没有保存文件。` |
| `LEFT_BEHIND` | `No file was saved, but shop could not remove {file}. Delete it.` | `没有保存文件，但 shop 没能删除 {file}。请删除它。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `week` | `str(week)`，比如 `2026-W47`。 |
| `dates` | `week.date_range`，一个 `BiText`：`16 to 22 November 2026` 和 `2026年11月16日至22日`。 |
| `meals` | `MEAL_COUNT.pick(n).to_bitext(count=n)`，`n` 设为 `shopping.meal_count`。 |
| `dishes` | `DISH_COUNT.pick(n).to_bitext(count=n)`，`n` 设为 `shopping.dish_count`。 |
| `count` | 每个 `Plural` 的数字。 |
| `items` | `comma_list(ingredient.name for ingredient in shopping.pantry_used)`（F02 设计 2.6）：`Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper` 和 `食用油、盐、糖、生抽、花椒`。 |
| `file` | 完整路径。在 `SAVED` 里是清单文件 `str(path)`。在 `LEFT_BEHIND` 里是临时文件 `str(creation.left[0])`。`context.folder.root` 是绝对路径（F05 设计 2.4）。 |

用这些提示，两种语言里 F13 原型的各行都能得出，比如 `Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes`、`2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜` 和 `已保存 C:\Users\Troy\recipe-menu\shopping\2026-W47.md`，只有 B 点的英文常备食材那一行除外。

错误：

`cli` 在运行 `shop` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，`NOT_A_WEEK`，不带下一行：`"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `WEEK` 的值不是周（第 1 步）。 |
| 退出码 1，错误流上是 `NO_MENU`：`There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | `menus/` 的列表里没有这一周的文件（第 6 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行，比如 `menus\2026-W47.toml, Monday dinner`、`  Unknown recipe "tomato-eggs".` 和 `RUN_CHECK` | 目录、常备清单、`recipes/` 的列表、`menus/` 的列表、这一周的菜单文件，或者菜单写到的某个菜谱文件有错误（第 2 到 5 步、第 7 步和第 8 步）。 |
| 退出码 1，错误流上是失败时的三行 | `replace_file` 给出 `FAILED`：`shopping` 不是文件夹、它没能创建，或者一个 `OSError` 让临时文件或移动没能完成（选择 6，3.1）。旧文件保持原来的字节。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `shop` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`Unexpected argument "2026-W48". Write "recipe-menu shop [WEEK]".` | 命令行写了两个周。 |
| 退出码 2，先是没有选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"shop" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。`replace_file` 删除临时文件，`cli` 不再写出任何东西（选择 6）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `shop` 把 `catalog.toml` 和 `pantry.toml` 各读一次，把 `recipes/` 列一次，把 `menus/` 列一次，把这一周的菜单文件读一次，并把菜写到的每个菜谱文件读一次，全都通过 F03、F04 和 F06 的读取函数。周写错时，它不读任何文件。遇到错误或没有菜单的周之后，它不再读任何东西。对菜单里有菜的周，它调用一次 `replace_file`，这次调用可能创建 `shopping/`，写入并删除临时文件，并创建或替换这一周的清单文件（3.1）。它不写其他文件，所以其他每个文件都保持原来的字节和修改时间（v0.1-S23）。它写入输出流或错误流。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，里面没有 `shopping/`，`home` 是它外面的一个空临时文件夹。第一次运行保存英文清单，并创建 `shopping/`。第二次运行给出 F13 原型“In Chinese”的输出，并把文件替换成原型里的文件。接下来几次运行给出“No menu, or an empty menu”的第一段输出、周写错时的错误，以及 F11 原型“A menu with a mistake”的各行，这些运行都保留文件。然后为本周新建一个菜单，给出“No menu, or an empty menu”的第二段输出，两种语言都有。最后一次运行遇到一个名为 `shopping` 的文件。

```python
import io
import shutil
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


def edit(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


file = folder.shopping_file("2026-W47")
assert not folder.shopping.exists()
code, out, err = run("shop", "2026-W47")
assert (code, err) == (0, [])
assert out[0] == "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes"
assert out[-1] == f"Saved {file}"

code, out, err = run("shop", "2026-W47", "--lang", "zh")
assert (code, err) == (0, [])
assert out == [
    "2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜",
    "",
    "蔬菜水果",
    "  番茄         600 g",
    "  菜心         1.5 kg",
    "  葱           5 根",
    "  姜           6 片",
    "  大蒜         11 瓣",
    "肉类水产",
    "  猪肉末       100 g",
    "  鸡翅中       1 kg",
    "蛋奶豆制品",
    "  鸡蛋         5 个",
    "  豆腐         1 块",
    "米面粮油",
    "  大米         640 g",
    "  面条         200 g",
    "调味品",
    "  郫县豆瓣酱   15 ml",
    "  白胡椒粉     适量",
    "其他",
    "  可乐         2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
    "",
    f"已保存 {file}",
]
saved = [
    "# 2026-W47 购物清单",
    "",
    "2026年11月16日至22日：4 餐，9 道菜。",
    "",
    "## 蔬菜水果",
    "",
    "- [ ] 番茄 600 g",
    "- [ ] 菜心 1.5 kg",
    "- [ ] 葱 5 根",
    "- [ ] 姜 6 片",
    "- [ ] 大蒜 11 瓣",
    "",
    "## 肉类水产",
    "",
    "- [ ] 猪肉末 100 g",
    "- [ ] 鸡翅中 1 kg",
    "",
    "## 蛋奶豆制品",
    "",
    "- [ ] 鸡蛋 5 个",
    "- [ ] 豆腐 1 块",
    "",
    "## 米面粮油",
    "",
    "- [ ] 大米 640 g",
    "- [ ] 面条 200 g",
    "",
    "## 调味品",
    "",
    "- [ ] 郫县豆瓣酱 15 ml",
    "- [ ] 白胡椒粉 适量",
    "",
    "## 其他",
    "",
    "- [ ] 可乐 2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
]
chinese_file = "".join(f"{line}\n" for line in saved).encode("utf-8")
assert file.read_bytes() == chinese_file
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

no_menu = 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
assert run("shop", "2026-W48") == (1, [], [no_menu])
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("shop", "2026-W99") == (2, [], [week_error])

edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
week47 = Path("menus", "2026-W47.toml")
assert run("shop", "next") == (
    1,
    [],
    [
        f"{week47}, Monday dinner",
        '  Unknown recipe "tomato-eggs".',
        'Run "recipe-menu check" to see every problem.',
    ],
)
assert file.read_bytes() == chinese_file

assert run("menu", "new", "this")[0] == 0
nothing = "The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved."
assert run("shop") == (0, [nothing], [])
nothing_zh = "2026-W46 的菜单没有菜，所以没有要买的东西。没有保存文件。"
assert run("shop", "this", "--lang", "zh") == (0, [nothing_zh], [])
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

edit(folder.menu_file("2026-W47"), '"tomato-eggs"', '"tomato-egg"')
shutil.rmtree(folder.shopping)
folder.shopping.write_text("", encoding="utf-8")
not_a_folder = '  The file cannot be written: "shopping" is not a folder.'
assert run("shop", "2026-W47") == (1, [], [str(file), not_a_folder, "No file was saved."])
assert folder.shopping.read_bytes() == b""
```

## 3. 对已有接口的修改

F13 给一个已实现模块的接口增加一个名称。`datafile` 由 F03 创建，F08 和 F11 给它加上了各自的写入功能；现在它导出 `replace_file`（3.1），这是架构 3 和 6 为 `shop` 计划的写入功能。它还在 `src/recipe_menu/datafile/messages.py` 里得到提示 `PARENT_NOT_A_FOLDER`，这条提示只在 `datafile` 内部使用。`replace_file` 给出 F11 的 `FileCreation`，结果只有 `CREATED` 和 `FAILED`。`FileOutcome` 和 `FileCreation` 保持它们的成员、字段和检查，`create_file` 保持它的行为。它们的文档注释现在讲的是 `create_file` 的结果，以后也写到 `replace_file`。F01 到 F12 导出的名称都不改变签名或行为，所以它们的测试原样通过。这些增加不改变需求，所以不需要 `[docs]` PR 批准。架构师在这份设计里审查它们，就像审查 F11 的 `create_file` 和 `NO_MENU` 那样。B 点做法 1 对一个原型和一个场景的修改单独走需求变更流程，它不改变任何接口。

F13 还把 `SHOP_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`；这个文件只在 `cli` 内部使用，架构 4 把它交给每个命令功能。加上之后，真正的 `recipe-menu` 的帮助在 `menu show` 之后列出 `shop`，共 21 行，两张表的第二列仍然从第 21 列之后开始（选择 1）。运行真正 `COMMANDS` 的测试只检查仍然成立的行和列：

- F05-T48 检查中文帮助的第一行和最后一行，F05-T49 不检查帮助的任何一行。
- F07-T17 检查 `check` 那一行以它的文字结尾，并且文字开始的列与 `--lang en|zh` 的文字开始的列相同。
- F08-T14 对 `init` 那一行做同样的检查，并检查 `check` 那一行跟在它后面。
- F09-T01 检查 `list` 和 `show` 两行跟在 `check` 那一行后面，并且它们的文字从同一列开始。F09-T19 和 F09-T25 检查 `list --help` 和 `show ... --help` 给出与 `--help` 相同的帮助。
- F10-T01 检查 `search` 那一行跟在 `show ID` 那一行后面，以 `  search WORD... ` 开头，文字也在同一列。F10-T11、F10-T15 和 F10-T16 检查带 `--help` 的 `search` 给出与 `--help` 相同的帮助，并且其中有 `search` 那一行。
- F11-T01 检查 `menu new` 和 `menu show` 两行跟在 `search` 那一行后面，并且它们的文字从同一列开始。F11-T27、F11-T32 和 F11-T35 检查带 `--help` 的 `menu` 给出与 `--help` 相同的帮助，F11-T32 还检查其中有 `Commands:` 和 `命令：`。

列仍然在第 21 列、`menu show` 那一行后面多出一行时，这些检查都仍然成立。`tests/f11_texts.py` 的 `HELP` 和 `HELP_ZH` 是 F05 原型的帮助去掉以 `  shop ` 开头的那一行，如果有测试拿它们和真正的帮助比较，就会失败。但没有测试这样做：F11-T01 只拿它们和 F11 自己的七个命令的帮助比较，它把这些命令作为 `commands=SEVEN` 传给 `main`，而 F13 不改变这个列表。F07-T01、F08-T14、F09-T01 和 F10-T01 也比较整段帮助，但每个都给 `main` 传入它自己的命令。没有测试用真正的 `COMMANDS` 运行 `shop`，所以 `recipe-menu shop` 从 `Unknown command "shop".` 变成真正的命令，不会让任何测试改变。所以加上这一项的 mock PR 让 F01 到 F12 的每个测试都继续通过，不需要修复测试的 PR。F13 自己的测试拿整段真正的帮助和 `tests/f05_texts.py` 的 `HELP_EN_LINES`、`HELP_ZH_LINES`，也就是 F05 原型完整的帮助比较。如果测试经理仍然发现某个检查真正帮助的测试会改变，就在 F13 的测试计划里写明它，由 F13 的测试 PR 修改它，因为开发工程师从不修改测试（R08）。

F13 按各自设计的规定使用这些接口，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural`、`comma_list`、`display_width` 和 `format_table`。
- F03 的 `DataFolder`（带 `shopping_file` 和 `relative`）、`Problem`、`Catalog`、`Pantry`、`read_catalog` 和 `read_pantry`。
- F04 的 `Recipe`、`list_recipe_ids` 和 `read_recipe`。
- F05 在 `app` 里的 `Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error` 和 `stop_at_error`，通过 `Context.settings` 使用的 `Settings`，以及 `cli` 里的 `COMMANDS`。
- F06 的 `IsoWeek`（带 `date_range`）、`NOT_A_WEEK`、`WeekMenu`、`list_menu_weeks`、`read_week_menu` 和 `week_from_argument`。
- F08 的提示 `FILE_WRITE_DENIED`、`FILE_WRITE_ERROR`、`FOLDER_CREATE_DENIED` 和 `FOLDER_CREATE_ERROR`，它们只在 `datafile` 内部使用，以及 `create_data_folder` 删除它所创建文件的方式（F08 设计 3.2）。`replace_file` 可以共用这段代码，`create_data_folder` 保持它的行为。
- F11 在 `menus` 里的 `NO_MENU`，以及在 `datafile` 里的 `FileOutcome` 和 `FileCreation`。
- F12 在 `shopping` 里的 `ShoppingList`、`ShoppingGroup`、带 `amount_text` 的 `ShoppingLine` 和 `build_shopping_list`。

### 3.1 `replace_file`

- 模块：datafile
- 功能：写一个文件和它的文字，并替换那里已有的文件：先在同一个文件夹里写一个临时文件，再把它移到旧文件上（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。所以文件里要么是旧文字，要么是新文字，绝不会是一部分，`OSError` 或中断都会让旧文件保持原样。文件所在的路径上什么都没有时，它创建这个文件夹（C 点）。`shop` 调用它（2.2），F14 的 `menu suggest` 也可以调用它。

签名：

```python
def replace_file(folder: DataFolder, path: Path, text: str) -> FileCreation: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `path` | `Path` | 要写的文件，比如 `folder.shopping_file("2026-W47")`。 | 在 `folder.root` 里面，而且不是 `folder.root`。 |
| `text` | `str` | 文件的文字。 | UTF-8 能够编码它。 |

- 返回值：一个 `FileCreation`（F11 设计 3.2）。`path` 上的文件已经是这段文字时，给出 `FileCreation(FileOutcome.CREATED)`，无论它是否替换了文件。某一步失败时，给出 `FileCreation(FileOutcome.FAILED, problem, left)`。`replace_file` 从不给出 `EXISTS`。

`replace_file` 按这些步骤工作。`parent` 是 `path.parent`，`temp` 是 `parent / (path.name + ".tmp")`，比如 `shopping/2026-W47.md.tmp`。

1. 在访问磁盘之前，它用 `folder.relative(path)` 检查 `path`，检查它不是 `folder.root`，并把 `text` 编码为 UTF-8。参数不对时，抛出错误表里的错误。
2. `os.path.isdir(parent)` 为真时，它继续。否则，`os.path.lexists(parent)` 为真时，那里有个不是文件夹的东西，比如一个文件，或者一个不指向文件夹的链接，调用给出带 `PARENT_NOT_A_FOLDER` 的 `FAILED`。否则那里什么都没有，它用 `Path.mkdir()` 创建 `parent`，不带上级目录，已有条目时算作错误。两次探测从不抛异常，失败的探测算作假。后面的步骤失败时，调用创建的文件夹保留下来。
3. 它用 `Path.unlink(missing_ok=True)` 删除 `temp` 上的条目。没有完成清理就停下的调用，比如停电之后，可能留下这个文件。条目不存在不算错误。
4. 它用独占模式 `"x"`、`encoding="utf-8"` 和 `newline="\n"` 打开 `temp`（架构 8）。它在打开得到的文件上用一次 `write` 调用写入文字，文字为空时也是这样，然后关闭文件。所以文件里是这段文字的 UTF-8 字节，没有字节顺序标记，换行就是文字里的换行。
5. 它用 `os.replace(temp, path)` 把 `temp` 移到 `path` 上，可以直接调用，也可以通过会调用它的 `Path.replace`。在 Windows 和 Linux 上，这次移动都一步替换掉 `path` 上的文件，那里什么都没有时就创建 `path`。然后调用给出 `FileCreation(FileOutcome.CREATED)`。

调用的每个问题都写文件 `folder.relative(path)`，也就是要写的文件，而不是它的文件夹或 `temp`，并且没有位置。所以调用者可以用完整路径 `str(folder.root / problem.file)` 写出它没能写成的文件，架构 6 允许 `shop` 这样做（ADR-0009）。`OSError` 给出下表里第一条适用的一行的问题。`reason` 是这个错误的 `strerror`；`strerror` 为 `None` 或空时，是这个错误的类名，与 `SYSTEM_ERROR` 相同（F03 设计 2.3）。

| 步骤 | 错误 | 结果 |
| --- | --- | --- |
| 2 | 创建 `parent` 时的 `PermissionError` | `FAILED`，带 `FOLDER_CREATE_DENIED`。 |
| 2 | 创建 `parent` 时的其他任何 `OSError`，包括 `FileExistsError` | `FAILED`，带 `FOLDER_CREATE_ERROR` 和 `reason`。 |
| 3 到 5 | `PermissionError` | `FAILED`，带 `FILE_WRITE_DENIED`。 |
| 3 到 5 | 其他任何 `OSError`，包括 `FileExistsError` | `FAILED`，带 `FILE_WRITE_ERROR` 和 `reason`。 |

`temp` 从打开成功的那一刻起就算已经创建。写入、关闭或移动抛出 `OSError` 之后，调用先用 `Path.unlink` 删除 `temp`，再给出 `FAILED`。删除也因 `OSError` 失败时，`temp` 的完整路径放进 `left`。打开之后的任何其他异常，比如 Ctrl+C 的 `KeyboardInterrupt` 或 bug 引起的异常，都在 `finally` 块里执行同样的删除，然后继续传出，所以调用不给出结果。移动之后什么都不删除。没有 `except` 子句捕获比 `OSError` 更宽的异常（架构 6 和 8）。`path` 上的文件只通过移动改变。所以只要调用给出 `FAILED` 或抛出异常，它就保持原来的字节，读 `path` 的人看到的要么是旧文字，要么是新文字，绝不会是一部分。

打开是独占的，所以失败之后的删除只删除调用自己创建的文件。第 3 步删除之前的调用留在 `temp` 上的文件，所以那个文件永远不会挡住打开。`temp` 在 `path` 所在的文件夹里，所以移动只发生在一个文件夹里，移动的文件绝不会跨越磁盘。除了探测 `os.path.isdir` 和 `os.path.lexists`，调用只通过 `Path.mkdir`、`Path.unlink`、用 `"x"` 模式的 `Path.open` 或 `open`、文件对象上的一次 `write`，以及 `os.replace` 访问磁盘。它从不使用 `os.open`、`os.rename`、`Path.write_text`、`Path.touch`、`tempfile` 或 `shutil`。F08 测试在 `tests/f08_support.py` 里的故障注入工具替换 `os.mkdir`、`os.rmdir`、`os.unlink`、`os.remove`、`os.scandir`、`os.listdir`、`io.open` 和 `builtins.open`，并把它对打开和写入的规则用在以 `"x"` 打开的文件上。所以除了移动，它覆盖了 `replace_file` 的每一次调用。F13 的测试计划为 `os.replace` 加一个替身，放在一个新的辅助文件里或 `tests/f08_support.py` 里，`Path.replace` 也会经过它。

`datafile` 的提示如下。`{folder}` 是 `str(folder.relative(parent))`，比如 `shopping`。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `PARENT_NOT_A_FOLDER` | `The file cannot be written: "{folder}" is not a folder.` | `无法写入文件：“{folder}”不是文件夹。` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `path` 不在 `folder.root` 里面，或者就是 `folder.root`。这项检查在调用访问磁盘之前进行。 |
| `UnicodeEncodeError` | `text` 里有 UTF-8 无法编码的字符，比如单独的代理项。这项检查在调用访问磁盘之前进行。 |

- 副作用：`parent` 所在的路径上什么都没有时，创建它。删除留在 `temp` 上的条目。创建 `temp`，写入它的文字，并把它移到 `path` 上，从而创建或替换 `path`。失败或中断之后，删除 `temp`。它不读任何文件。
- 性能指标：无。PT01 为 `recipe-menu shop`（2.2）计时，它调用一次 `replace_file`。

示例：

在这个示例里，`tmp` 是一个空临时文件夹。第一次调用创建 `shopping/`。移动失败的情况用文件路径上的一个文件夹，两个系统都拒绝替换它：Windows 给出 `PermissionError`，Linux 给出 `IsADirectoryError`。

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder, FileCreation, FileOutcome, replace_file
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "recipe-menu")
folder.root.mkdir()
file = folder.shopping_file("2026-W47")
assert replace_file(folder, file, "# 1\n") == FileCreation(FileOutcome.CREATED)
assert file.read_bytes() == b"# 1\n"
assert replace_file(folder, file, "# 2\n番茄 600 g\n").outcome is FileOutcome.CREATED
assert file.read_bytes() == "# 2\n番茄 600 g\n".encode()
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

week48 = folder.shopping_file("2026-W48")
week48.mkdir()
blocked = replace_file(folder, week48, "# 3\n")
assert blocked.outcome is FileOutcome.FAILED
assert blocked.problem is not None
assert (blocked.problem.file, blocked.problem.place) == (Path("shopping", "2026-W48.md"), None)
assert blocked.problem.text(Lang.EN).startswith("The file cannot be written")
assert blocked.left == ()
names = sorted(path.name for path in folder.shopping.iterdir())
assert names == ["2026-W47.md", "2026-W48.md"]

other = DataFolder(tmp / "other")
other.root.mkdir()
other.shopping.write_text("", encoding="utf-8")
failed = replace_file(other, other.shopping_file("2026-W47"), "# 1\n")
assert failed.outcome is FileOutcome.FAILED
assert failed.problem is not None
assert failed.problem.text(Lang.EN) == 'The file cannot be written: "shopping" is not a folder.'
assert other.shopping.read_bytes() == b""

replace_file(folder, tmp / "elsewhere.md", "")  # raises ValueError
replace_file(folder, folder.root, "")  # raises ValueError
replace_file(folder, file, "\udc80")  # raises UnicodeEncodeError
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `shop` 是架构 3 交给 F13 的命令模块，位于 `src/recipe_menu/commands/shop/`。它只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`menus` 和 `shopping`，都在它那一行里。它既不需要 `units` 也不需要 `settings`，也不引用别的命令模块，所以没有给架构 4 增加箭头。`SHOP_COMMAND` 是一个 `Command`（架构 5.2），它在 `COMMANDS` 里的那一项就是架构 4 允许命令功能在 `cli` 里做的唯一修改。`replace_file` 应该放在 `datafile` 里：它那一行负责写文件，而且只有它打开数据文件（架构 8）。它给出 F11 的 `FileCreation`，所以 F13 不增加值类型。保存的文件就是架构 5.1 里的 `shopping/<week>.md`，UTF-8 编码，没有字节顺序标记，换行是 LF。选择 3 只读取架构 8 为 `shop` 列出的文件。简报第 1 点：架构师在 main 的 `src/` 的一份副本里按第 2 节和 3.1 建了模型，选择 1 到 11 在模型上都成立。帮助和 F05 原型的两份帮助完全相同，也就是 `tests/f05_texts.py` 里的 `HELP_EN_LINES` 和 `HELP_ZH_LINES`，共 21 行，第二列从第 21 列之后开始。`shop 2026-W99` 只给出 `NOT_A_WEEK`，退出码为 2，什么都不写，也不碰任何文件。英文和中文的数量分别在缩进之后 16 列和 13 列处开始。目录名称和分类名称里有换行时，每个标题仍在原位。保存的文件跟随运行时的语言。一周里唯一的菜只用到常备食材时，给出 `There is nothing to buy.`、常备那一行和 `Saved`，并保存文件。一个 PT01 的周给出 6 个分组里的 290 行，文件有 10,345 字节。 |
| 遵守错误处理和命名约定 | 通过 | 数据文件里的错误通过 F05 的 `first_error` 和 `stop_at_error` 让 `shop` 停下。`NO_MENU` 和失败时的各行写到 stderr，退出码为 1；错误的周是唯一的 `UsageError`，不带提示（架构 6，ADR-0008）。`replace_file` 把每个 `OSError` 变成带 F08 提示的 `Problem`，捕获的范围不超过 `OSError`，并在 `finally` 块里删除临时文件。简报第 2(a) 点：3.1 就是架构 6 说的那种写法。`<name>.tmp` 和文件在同一个文件夹里，所以 `os.replace` 不会跨驱动器，在两个系统上都一步替换旧文件。先删除旧的 `.tmp`，可以避免停电留下的文件挡住独占打开，而且只有 `shop` 往 `shopping/` 里写（需求 3）。独占打开是架构 6 对新文件的规定。设计没有调用 `fsync`，架构 6 也不要求：按 Ctrl+C 后，旧文件或新文件都是完整的；停电弄坏的清单，下一次运行会重写。在 Windows 上，模型把临时文件移到被另一个句柄打开着的文件上，以及移到只读文件上，都抛出了 `PermissionError`。这时 `shop` 写出清单文件的完整路径、`The file cannot be written: access is denied.` 和 `No file was saved.`，旧文件的字节不变，也没有留下 `.tmp`，和选择 6 以及摘要的第一条风险说的一样。简报第 2(b) 点：C 点的做法 1 在需求 3 之内：需求 3 的表格把 `shopping/` 交给 `shop`，它的规定限制的是文件，不是文件夹。它也在架构 1 和 6 之内，两者都没有禁止。`replace_file` 的每个问题都写清单文件，从不写它的文件夹（3.1），所以失败时的第一行写的是 `shop` 没能写成的文件。这正是 ADR-0009 第 3 节里、架构 6 给 `shop` 的那种情况。所以和 F11 的 C 点不同，它不需要修改架构 6，也不需要新的 ADR；选择 6 也按 ADR-0009 第 5 节的要求说明了它用到这种情况。`PARENT_NOT_A_FOLDER` 里相对的 `"shopping"` 属于一个问题，问题按相对数据文件夹的路径写，而它上面那一行给出完整路径。各个名字遵守架构 8。备注 1，不阻塞（3.1，`OSError` 结果的表格）：F08 的 `_creation_problem` 把 `FileExistsError` 映射为 `FILE_EXISTS` 和 `FOLDER_EXISTS`，而表格给的是 `FILE_WRITE_ERROR` 和 `FOLDER_CREATE_ERROR`。开发者不能让 `FileExistsError` 原样经过它，main 上的 `create_file` 对写入时出现的 `FileExistsError` 就是这样处理的。测试计划可以在创建文件夹时和打开时各注入一个，把表格固定下来。 |
| 不和已有接口重复 | 通过 | `shop` 用 F12 的 `build_shopping_list` 生成清单，用 `amount_text` 写出每个数量，用 `format_table` 和 `display_width` 对齐，用 `comma_list` 连接常备食材的名称，用 `week_from_argument` 得到周。这些它都没有重写。`replace_file` 是第一个替换文件的写法：`create_file` 拒绝已有的条目，`create_data_folder` 创建一整个文件夹。它复用 `_remove_all`、F08 的四个写入提示和 `FileCreation`，只增加一个提示。简报第 2(d) 点：读取目录和在第一个错误处停下的这份副本是内部代码，不是接口，它调用的是共享接口 `first_error` 和 `stop_at_error`。`WEEK_ARGUMENT`、`MEAL_COUNT` 和 `DISH_COUNT` 的副本也一样，架构 8 让每个模块把提示放在自己的 `messages.py` 里。选择 3 的理由成立：再多共享就要修改 F13 不负责的三个已实现模块，而相关 PR 已经接近 R03 的上限。备注 2，不阻塞（选择 3 的最后一段）：`shop` 不能引用 `menu`，`app` 也不能引用 `catalog`、`recipes` 或 `menus`（架构 3）。所以后续的 `[refactor]` PR 不改架构就能加的辅助函数，是 `app` 里一个根据读取器的问题停下的函数，它给出退出码或 `None`，各命令保留自己的读取。要共享 `menu show` 的读取顺序本身，需要一个架构 3 里没有的箭头。这一段可以把“比如 `app`”改成“`app` 里一个接收读取器问题的辅助函数”。 |
| 只依赖排序在前面的功能 | 通过 | F13 使用 F02 的 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`、F05 的 `app` 和 `COMMANDS`、F06 的 `menus`、`datafile` 内部 F08 的提示和 `_remove_all`、F11 的 `NO_MENU`、`FileOutcome` 和 `FileCreation`，以及 F12 的 `shopping`。这些功能都排在 F13 前面，并且在 main 上通过测试，硬依赖 F05 已经验收。对 F14 的计划不约束后面的设计。F13 只需要标准库，所以 R16 没有要审查的东西。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写下了模块之间的每个假设。`replace_file` 的每个问题都写要写的那个文件，不带位置，所以 `shop` 写出 `str(context.folder.root / problem.file)`（3.1）。`replace_file` 只给出 `CREATED` 和 `FAILED`，它的 `left` 最多只有临时文件。`shop` 只把读取器无错误给出的、来自同一个目录的值传给 `build_shopping_list`，所以不会遇到 F12 的 `ValueError`（选择 3）。`shopping_file` 只在 `week_from_argument` 给出周之后才拿到名字（选择 2）。F08 的故障注入工具没有 `os.replace`，3.1 说明由测试计划加上。没有模块读 `shopping/`，所以 `.tmp` 这个名字不会碰到读取方。在模型里，v0.1-S15 的第 5 步给出 `menu show` 的那三行，因为常备清单没有错误；运行前就有的 `2026-W47.md.tmp` 在运行后不见了。 |
| 修改已实现的接口时走了变更流程 | 通过 | 这个 PR 只添加两个设计文件。第 3 节给 `datafile` 增加 `replace_file` 和内部的 `PARENT_NOT_A_FOLDER`，并扩展 `FileOutcome` 和 `FileCreation` 的文档注释，让它们也提到 `replace_file`。F01 到 F12 导出的名字没有一个改变签名、字段、检查或行为，`replace_file` 的每个结果都能通过 `FileCreation` 现有的检查。这些新增不改变需求，所以由架构师在这里审查，就像审查 F11 的 `create_file` 和 `NO_MENU` 那样。把模型的 `SHOP_COMMAND` 放进 `COMMANDS`、把新名字放进 `datafile` 后，整个测试套件在 Windows 上 553 个通过、4 个跳过，跳过的 4 个是 main 上只在 Linux 上运行的用例。所以 F05-T48、F05-T49、F07-T17、F08-T14、F09-T01、F10-T01、F11-T01 和其他每个测试都仍然成立，和第 3 节说的一样，也不需要修正测试的 PR。简报第 2(c) 点：B 点的做法 1 修改一个原型和一个场景，它们归 Troy 所有，所以要走需求变更流程。顺序是对的：在 Troy 于这个 PR 里做出决定之后、PR 2 之前，因为 PR 2 的用例要和 F13 原型以及 v0.1-S16 比较。它不改任何接口，所以变更影响分析不会找到要改的接口。简报第 5 点：mock 的 8 个文件超过 R03 的 5 个，它给出的软限制理由是对的。troy-mode 只有一个 mock PR，测试既直接调用 `replace_file`，也通过 `shop` 调用它，和 F08、F11 的 mock 一样。实现的 4 个文件在 R03 之内，行数接近 500，和设计提醒的一样。备注 3，不阻塞（B 点做法 1）：v0.1-S16 在 `docs/versions/v0.1/test-plan.md` 里，由测试经理而不是产品经理来写。产品经理修改原型，测试经理修改 v0.1-S16，都在 PR 2 之前。备注 4，不阻塞（第 2 节最后一段）：只检查错误流为空的测试，或者只检查没有留下 `.tmp` 文件的测试，在 mock 上也会通过。测试经理要给每个这样的测试加上一项 mock 做错的检查。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | PR #85 开头的摘要和设计说的一致。有什么变化：按分类的清单、常备那一行和带路径的 `Saved`（选择 4）；按运行时语言保存的清单，它替换这一周的文件和其中的勾选（选择 5）；不改别的文件（需求 3）；`There is nothing to buy.`，文件照样保存（选择 7）；保存失败时说明原因，旧文件不变（选择 6）。需要 Troy 决定的：A、B、C 三点，各有做法，B 点写了做法 1 和 2 的代价以及做法 3 的结果，每点都有推荐和理由，没有别的点。A 点的 11 段文字就是没有原型展示的全部新文字。风险：Windows 拒绝保存，模型重现了这种情况；以及速度，设计给的是估计。在这台电脑上，对 `tests/pt01_support.py` 生成的 PT01 文件夹运行 `shop 2026-W26`，从启动到退出计时，两组各 5 次，中位数是 0.226 秒和 0.228 秒，同一组里 `menu show 2026-W26` 是 0.216 秒，所以“约 0.2 秒”成立。中文部分约 920 个字符，英文部分约 1,870 个，都在 R22 的 2,000 以内，都没有内部编号。架构师没有发现别的需要 Troy 决定的点。架构师的推荐：A，接受这 11 段文字，它们沿用了 `NO_DISHES`、F08 的写入提示和 `menu new` 的 `LEFT_BEHIND`；B，做法 1，因为这样这一行按目录的写法写出每个名称，和清单自己的各行一样，而做法 2 要改目录的格式和读取它的代码，做法 3 会把 Sichuan 这样的专有名词写错；C，做法 1，因为它在需求 3、架构 6 和 ADR-0009 之内，三者都不用改，复制出来的数据文件夹也照样能得到清单。备注 5，可选（摘要的“对你有什么变化”和第 2 点）：摘要可以说明保存失败时不显示清单，比如“你会看到原因，清单不显示，旧文件保持不变”，和选择 6 一致。还可以说明做法 3 也要修改原型里最后一个名称，需要 Troy 批准。两处加上后都不超过 2,000 个字符。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0008 到 ADR-0010、F02、F05、F11 和 F12 的设计、F05 和 F13 原型，以及 v0.1-S08、v0.1-S14 到 v0.1-S18、v0.1-S23、v0.1-S26 和 v0.1-S32，检查了 11 个选择和第 3 节。两个文件有同样的 9 个标题和 106 个表格行，9 个代码块各自和镜像里的相同，没有不可见字符。用 ruff 0.17.4 运行 `ruff format --check`，报告两个文件都已格式化。架构师在 Windows 上用 Python 3.13.18，在 main 的 `src/` 的一份副本里按第 2 节和 3.1 建了模型，运行了每个文件的 3 个示例：全部 51 个断言和全部 4 个 `# raises` 都成立。在 `tests/data/example/` 的新副本上，中文运行给出的输出和保存的文件与 F13 原型逐字节相同，英文运行和原型只差 B 点的常备那一行，“No menu, or an empty menu”的两个输出也一致。v0.1-S08、v0.1-S14、v0.1-S15、v0.1-S17、v0.1-S18 和 v0.1-S23 成立，v0.1-S16 除了 B 点的常备那一行也成立。在 v0.1-S14 里，`shop` 和 `shop next` 给出一道菜也没有的周那一行，退出码为 0，`shopping\` 保持为空，和设计对简报的更正一致。在 v0.1-S23 里，只有 `shopping\2026-W47.md` 和 `shopping\` 的修改时间变了。3.1 在 Linux 上的结果没有运行。备注 1 到 5 不阻塞。 | 批准。接口设计师可以在修订中处理备注 1 到 5，也可以不处理。由 Troy 批准这份设计并决定 A 到 C 点（R18）。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-15 | 初稿。 |
| 1.0 | 2026-11-15 | Troy 批准。 |
