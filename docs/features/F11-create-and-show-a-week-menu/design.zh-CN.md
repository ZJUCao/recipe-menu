---
troy-doc: "F11-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-14"
status: "Troy 已于 2026-11-14 批准"
mirror-of: "design.md"
---

# F11 创建和查看周菜单：接口设计

## 1. 功能

- 编号和名称：F11 创建和查看周菜单
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F02、F06

## 2. 接口

F11 在 `src/recipe_menu/commands/menu/` 里构建命令模块 `menu`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.menu` 导出两个名称 `MENU_NEW_COMMAND`（2.1）和 `MENU_SHOW_COMMAND`（2.3），它的 `__init__.py` 在 `__all__` 里列出它们。你输入的命令是 `recipe-menu menu new`（2.2）和 `recipe-menu menu show`（2.4）。它们的提示放在 `src/recipe_menu/commands/menu/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F11 在它的 mock PR 里把这两个命令加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `SEARCH_COMMAND` 之后。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F11 还给两个已实现的模块增加名称（第 3 节）。`menus` 把一周没有菜单时的那一行导出为 `NO_MENU`（3.1）。`datafile` 得到写一个新文件的功能 `create_file`，以及它的结果 `FileCreation` 和 `FileOutcome`（3.2 和 3.3）。F11 原型 `docs/prototypes/F11-menu.md` 展示了这两个命令，F05 原型展示了它们在帮助里的那两行。

在这份设计里，`\u00d7` 代表 U+00D7 MULTIPLICATION SIGN，它写在一道菜的份数前面；`\u2014` 代表 U+2014 EM DASH，它表示空的一餐。两者都按 Python 的写法写出。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F11 提供的接口 |
| --- | --- |
| `recipe-menu menu new [WEEK]` 创建这一周的菜单文件，每天每餐都是空的。 | `recipe-menu menu new`（2.2），以及 `MENU_NEW_COMMAND`（2.1）。它通过 `create_file`（3.3）写出选择 3 的文件。 |
| 文件已存在时拒绝执行。 | `create_file` 的结果 `EXISTS`（3.2），`menu new` 用 `ALREADY_EXISTS` 和退出码 1 报告它（选择 4）。 |
| `recipe-menu menu show [WEEK]` 把这一周打印成一张按天和餐排列的表，写出每道菜和它的份数。 | `recipe-menu menu show`（2.4），以及 `MENU_SHOW_COMMAND`（2.3），还有选择 8 的表格。 |
| 接受周的命令接受 ISO 周、`this` 或 `next`。不写周时，用本周（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | F06 的 `week_from_argument` 和 `NOT_A_WEEK`（选择 2）。 |
| `init` 和 `menu new` 只在没有文件的地方创建文件，否则拒绝执行（需求 3）。 | `create_file` 拒绝已经存在的条目，并用独占模式打开新文件（3.3，[架构 6](../../architecture.zh-CN.md#6-错误处理)）。 |
| 数据文件夹里有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`menu show` 在 1 秒内结束（PT01，[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。 | 2.4 的性能指标，以及选择 11。 |

下面每个接口都遵守这些规则：

- `menu` 在包内只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`。架构 3 里它那一行允许这些模块。它既不需要 `units`，也不需要 `shopping`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `menu` 只通过 F03、F04 和 F06 的读取函数以及 `create_file` 访问磁盘，这些函数都通过 `datafile` 工作（架构 8）。`menu new` 只写这一周的菜单文件（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 1](../../architecture.zh-CN.md#1-背景和约束)），`menu show` 不写任何文件。两者都只写入 `context.out` 和 `context.err`。它们自己不读取外部世界的任何东西，也不保存状态。`menu show` 读到的菜谱只在一次运行里存在，所以没有模块保存缓存（架构 8）。
- 读取函数遇到坏数据从不抛异常，`create_file` 把每个 `OSError` 变成一个值（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。每个命令在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。`run` 只为不是周的 `WEEK` 值抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出（F05 设计第 2 节）。传到 `cli` 的任何其他异常都是 bug。
- `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。`FileCreation` 是带 `slots=True` 的冻结数据类，`FileOutcome` 是枚举（架构 8）。它们是辅助值，就像 F08 增加的 `Creation` 和 `CreationOutcome`。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- `recipe-menu menu show` 有性能指标 PT01（选择 11）。它把需要的每个文件只读一次，并在读完最后一个文件后一次写出输出。`recipe-menu menu new` 没有性能指标，因为 PT01 不为它计时。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2、2.4 和 3.3 给出它们的规则。

1. **两个命令在一个模块里，在帮助里排在 `search` 之后。** 架构 8 把 `menu new` 和 `menu show` 放进模块 `menu`。F11 把 `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND` 加在 `COMMANDS` 里 `SEARCH_COMMAND` 的后面。所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND)`，符合 F05 设计第 2 节的帮助顺序。两个命令都有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它们（F05 设计 2.5）。按 F05 设计的计划，每个命令都声明可选参数 `WEEK`。所以帮助写成 `menu new [WEEK]` 和 `menu show [WEEK]`，中文写成 `menu new [周]` 和 `menu show [周]`。两个命令都不声明选项。有这七个命令时，帮助里最宽的第一格是 `menu show [WEEK]`，占 16 列，比 `search WORD...` 多两列。所以两种语言里，两张表的第二列都从第 21 列之后开始，而不是像 F10 之后那样从第 19 列之后开始，帮助共 20 行。这时的帮助就是 F05 原型的两段帮助去掉 `shop` 那一行（2.1）。只写 `recipe-menu menu` 时，给出 F05 的 `INCOMPLETE_COMMAND`，`The commands that start with "menu" are "menu new" and "menu show".`，后面是 `RUN_HELP_FOR_COMMANDS`，退出码 2。这就是 F05 设计 2.10 的文字，F05-T23 用按 v0.1 顺序排列的替身命令检查它，它仍然成立。第 3 节列出检查真正帮助的测试，它们都仍然成立。
2. **周。** 每个命令用 `week_from_argument(value, context.today)` 得到它的周（F06 设计 2.7）。`value` 是 `WEEK` 的值，命令行没有给出时是 `None`。所以 `2026-W47` 这样的 ISO 周、`this`、`next`，以及表示本周的不写值，在两个命令里都能用，这是需求 3 的要求。其他文字，比如 `2026-W99`、`Next` 或空文字，给出 `UsageError(NOT_A_WEEK, None, week=value)`，`cli` 只写出这条提示，并以 2 退出。提示已经说了该写什么，所以不带下一行（ADR-0008，决定 A），和 F11 原型“A week without a menu”以及 v0.1-S15 显示的一样。`run` 在访问磁盘、写出任何输出之前抛出它。之后的每一行都用 `str(week)` 写出周，比如 `next` 写成 `2026-W47`，所以每一行写出的都是你能找到的文件。
3. **`menu new` 写出的文件。** 它就是 F11 原型“Create next week's menu”里的文件：三行注释、键 `week`，以及从周一到周日每天一张表，表里按 `Meal` 的顺序为 `context.settings.meals` 的每一餐写一个空列表（2.2）。第一行注释是这一周和它的英文 `date_range`，比如 `# 2026-W47: 16 to 22 November 2026`，和 `example-data.md` 里菜单的开头一样。另外两行注释展示 `read_week_menu` 能读的两种菜的写法（F06 设计 2.9）。文件是 UTF-8，没有字节顺序标记，用 LF 换行（架构 5.1），而且只有 ASCII 字符。它的字节在两种语言里都相同。`--lang zh` 或设置里的 `language = "zh"` 改变的是输出的各行，而不是文件，就像 `init` 写出的文件在两种语言里都保留英文注释（F08 设计，选择 6）。这一点由 Troy 决定（下面的 B 点）。`read_week_menu` 用同样的设置读这个文件，给出一个每格都是空的菜单，没有问题。所以 `check` 对它什么也不报告，`menu show` 对每一餐都显示 `\u2014`（v0.1-S14）。以后设置里的餐次变少时，其他餐次的空列表仍然不会带来问题（F06 设计，选择 5）。
4. **`menu new` 怎样写文件，以及它读什么。** 每个文件都由 `datafile` 写（架构 2、3 和 8），所以 F11 按 F08 设计第 2 节的计划，给它加上 `create_file`（3.3）。`create_file` 只写一个新文件，别的什么都不写。它列出文件所在的文件夹，那里已经有条目时拒绝执行。否则它用独占模式、`encoding="utf-8"` 和 `newline="\n"` 打开文件，用一次 `write` 写入文字，然后关闭文件。它和 F08 的 `create_data_folder` 共用写文件的方式和失败时的提示（F08 设计 3.2）。`menu new` 按它的结果处理：
   - **文件已存在。** `create_file` 给出 `EXISTS`。`menu new` 写出 `ALREADY_EXISTS`，带上已经存在的那个条目的完整路径，比如 F11 原型里的 `C:\Users\Troy\recipe-menu\menus\2026-W47.toml 已存在。没有做任何修改。`，并以 1 退出。`create_file` 从不打开那个条目，所以文件保持原来的字节和修改时间（v0.1-S13）。`menu new` 不读任何菜单文件，所以这一周有错误的文件，或者空文件，也得到同样的拒绝。`check` 和 `menu show` 会报告它的错误。
   - **只有大小写不同的名称。** 在 Windows 上，文件系统分不清 `2026-w47.toml` 和 `2026-W47.toml`，所以那个文件会让任何程序都无法创建 `2026-W47.toml`（F06 设计第 2 节）。Linux 会创建第二个文件。`create_file` 让两个系统表现一致：把 A 到 Z 的字母换成小写后与新名称相同的条目，也算已经存在（3.3）。所以在两个系统上，`menu new 2026-W47` 都写出带 `...\menus\2026-w47.toml` 的 `ALREADY_EXISTS`，并以 1 退出。然后 `menu show 2026-W47` 和 `check` 用 F06 的 `NOT_A_WEEK_NAME` 报告那个文件，提示你给它改名。同一条规则也拒绝 `2026-W47.TOML`。
   - **`menus\` 不存在，或者是一个文件。** 这个文件夹由 `init` 创建，`menu new` 只创建菜单文件（需求 3）。所以列出文件夹会失败，`create_file` 给出 `FAILED`，带上 `list_menu_weeks` 和 `check` 对这个文件夹报告的问题：`The folder is missing.` 或 `The folder cannot be read: it is a file.`（F04 设计 3.1）。`menu new` 写出失败时的三行，并以 1 退出。按 C 点的做法 1（见下文），第一行用完整路径写出这个文件夹，比如 `C:\Users\Troy\recipe-menu\menus`。你创建这个文件夹，再运行一次 `menu new`。
   - **其他 `OSError`。** 以别的方式失败的列出，或者失败的打开、写入或关闭，比如没有访问权限或磁盘已满，都给出 `FAILED`。它的问题带有列出文件夹时的提示、F08 的 `FILE_WRITE_DENIED`，或者 F08 的 `FILE_WRITE_ERROR`。`menu new` 写出三行：文件或文件夹的完整路径 `str(context.folder.root / problem.file)`，然后是两个空格加上这个问题，然后是 `CHANGED_NOTHING`。架构 6 允许 `menu new` 用完整路径写出它没能写成的文件（ADR-0009）。它没有涵盖 `menu new` 没能列出的文件夹 `menus\`，而 ADR-0009 第 5 节有意保持这个范围。所以用完整路径写出这个文件夹，也就是 C 点的做法 1，需要修改架构 6，由 Troy 决定。Troy 决定之后，架构师在 F11 的 mock PR 之前，用一个 `[docs]` PR 把决定记进架构 6 和一份 ADR，就像 ADR-0009 记下 F08 设计的待定问题 D 那样。这份设计采用推荐的做法 1。打开已经成功时，`create_file` 先删除写了一半的文件。这次删除也失败时，比如另一个程序正打开着这个文件，第三行是 `LEFT_BEHIND`，它请你删除这个文件，再运行一次命令。
   - **Ctrl+C。** `create_file` 在 `finally` 块里删除写了一半的文件，`cli` 以 130 退出，不再写出任何东西（F05 设计 2.10）。文件关闭之后按 Ctrl+C，留下的是完整的文件。和 `init` 一样，在 `open` 内部、系统已经创建了文件但调用还没记下它的时候按 Ctrl+C，可能留下一个空文件（F08 设计，选择 5）。这时 `menu show` 和 `check` 报告它缺少 `week`，`menu new` 拒绝它，你把它删掉。

   `menu new` 自己不读任何数据文件。`cli` 在运行命令之前读取设置，并在设置的第一个错误处停下（F05 设计 2.10 第 9 步），`menu new` 从 `context.settings` 取得餐次。它不读目录、菜谱或菜单，也不检查 `menus\` 里的其他名称。所以别的文件里的错误不会让它停下。
5. **`menu new` 的输出。** 新菜单在输出流上给出原型里的三行，退出码 0（2.2）。它们是带新文件完整路径和这一周 `date_range` 的 `CREATED`，然后是带各餐的 `EMPTY_DAYS`，然后是 `NEXT_STEP`。各餐是 `context.settings.meals` 里每一餐的 `Meal.label` 的 `and_list`（F02 设计 2.6）。这在原型里给出 `lunch and dinner` 和 `午餐和晚餐`，在 v0.1-S16 里给出 `breakfast, lunch, and dinner`，只有一餐时给出 `dinner` 和 `晚餐`，比如 `7 days with dinner, all empty.`。一周总是七天，所以这一行直接写数字 7，不需要 `Plural`。拒绝执行和失败写到错误流，退出码 1（架构 6）。输出跟随 `context.lang`。没有原型展示的文字由 Troy 决定（下面的 A 点）。
6. **一周没有菜单时的那一行。** 对一周没有菜单文件的情况，`menu show` 和 F13 的 `shop` 写出同一行，`There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.`，F11 和 F13 的原型都是这样显示的。`shop` 不能引用 `menu`（架构 3）。所以 F11 把这一行加进 `menus`，命名为 `NO_MENU`（3.1），这是架构师在 F06 审查里的建议（备注 4）。`menus` 已经因为同样的理由导出了 `NOT_A_WEEK`（F06 设计，选择 8），而且这一行讲的周菜单正归它管。换一种做法，`menu` 和 `shop` 就要各存一份，改这一行时要改两处。`{week}` 是 `str(week)`。这一行写到错误流，退出码 1。没有菜单就是缺少文件，由命令检查（架构 6，“缺少数据文件夹、菜单或菜谱”，ADR-0008）。它的中文是新的，由 Troy 决定（A 点）。
7. **`menu show` 读什么，在哪里停下。** `menu show` 只读它需要的文件：`cli` 里的设置、目录、菜单，以及只有菜单写到的那些菜谱（架构 8）。它按 `show` 的顺序读这些文件（F09 设计，选择 2）：先是目录和各个列表，然后是你要的那一周，然后只读这一周需要的东西（2.4）。
   - 它用 `read_catalog` 读目录，因为没有目录时 `read_recipe` 给不出菜谱（F04 设计 2.6）。
   - 它用 `list_recipe_ids` 把 `recipes/` 列一次，并把这些 ID 作为 `frozenset` 传给 `read_week_menu`（F06 设计，选择 4）。它不调用 `read_recipes`，那样会再列一次文件夹并解析每个菜谱。所以列表的问题它只报告一次。
   - 它用 `list_menu_weeks` 把 `menus/` 列一次，在它给出的周里查找这一周（F06 设计 2.8）。这次列出的错误会让 `menu show` 停下，即使错误写的是另一个文件，就像 `recipes/` 列表的错误会让 `show` 停下一样。`menus\` 不存在时给出 `menus` 和 `The folder is missing.`。在两个系统上，`2026-w48.toml` 都会给出 `menus\2026-w48.toml` 和 `NOT_A_WEEK_NAME`，提示你给文件改名，这发生在 `menu show 2026-W48` 查找这一周之前。列表里没有的周给出 `NO_MENU` 和退出码 1（选择 6）。
   - 它用 `read_week_menu` 和 `context.settings` 读这一周（F06 设计 2.9）。因为 `menu show` 有 `FolderUse.READ`，这就是文件里的设置。
   - 它用 `read_recipe` 读每道菜写到的每个菜谱，每个只读一次，按第一道写到它的菜的顺序：周一到周日，各餐按设置的顺序，菜按文件里的顺序。几道菜写到的同一个菜谱只解析一次，这次运行为其他几道菜保留它。菜单没写到的菜谱不解析，所以它里面的错误不会让 `menu show` 停下。

   每个读取函数的第一个错误都会让 `menu show` 用 `first_error` 和 `stop_at_error` 停下，它们写出这个问题和 `RUN_CHECK`，并给出 1（F05 设计 2.8），和 F11 原型“A menu with a mistake”显示的一样。`check` 用相同的读取函数、相同的参数读这些文件，所以让 `menu show` 停下的错误一定在 `check` 的错误里（F07 设计，选择 8）。`menu show` 不写出警告，警告也从不改变退出码，与 F09 选择 3 相同（架构 6）。缺少所选语言的名称通过 `BiText.get` 显示另一种语言，就像 F09 原型“A missing language”里 `show` 显示的那样。
8. **`menu show` 的表格。** 表格有一列是日期，菜单的每一餐各一列，也就是设置里的餐次。最上面是 `DAY_HEADING` 和每一餐的 `Meal.heading`（F05 设计 2.1）。每天一行，从周一到周日。第一格是这一天日期的 `short_date`，比如 `Mon 16 Nov` 和 `周一 11月16日`（F06 设计 2.2）。一餐的格子里，`WeekMenu.dishes` 的每道菜占一行，按文件里的顺序：所选语言 `context.lang` 的菜谱名、一个空格、`\u00d7` 和份数，比如 `Mapo tofu \u00d72`。一餐里写了两次的同一道菜给出两行这样的文字，两道都计数（选择 9）。空的一餐显示 `\u2014`。`format_table` 把一格里的各行上下排列，所以一行占的行数与它最满的那一餐相同（F02 设计 2.9）。名称按菜谱文件里的样子写出，所以 `format_table` 的规则对它适用，比如带换行的名称会占两行，和 `search` 里一样（F10 设计 2.2）。`\u00d7` 和 `\u2014` 不属于任何语言，所以它们是代码里的符号，不是提示，这些格子在两种语言里都相同（架构 8）。每一列与这一周表格里它最宽的一行一样宽，表头也算在内，最后一列不补空格（F02 设计 2.9）。`menu show` 不传 `min_widths`，因为没有别的表格要和这张表对齐。所以原型的英文表格两列宽 10 列和 25 列，来自 `Mon 16 Nov` 和 `Tomato and egg noodles \u00d72`。中文表格两列都宽 13 列，来自 `周一 11月16日` 和 `番茄鸡蛋面 \u00d72`。别的周用它自己格子的宽度，和 `search` 一样（F10 设计，选择 7）。
9. **计数行。** 表格下面那一行数出至少有一道菜的餐数和全部菜数，这是 F06 设计第 2 节为 F11 和 F12 计划的计数方式。按这种计数，原型里是 `4 meals, 9 dishes.` 和 `4 餐，9 道菜。`，v0.1-S16 里是 `1 meal, 1 dish.`。这一行接着解释 `\u00d7n`，和原型一样。`MEAL_COUNT` 和 `DISH_COUNT` 是 `Plural` 值（F02 设计 2.4），所以一餐和一道菜时英文也是对的。一道菜也没有的周，比如 v0.1-S14 里的新菜单，显示每一餐都是 `\u2014` 的表格，然后用 `NO_DISHES`，`The menu has no dishes yet.`，代替计数行。这时没有格子显示 `\u00d7n`，所以这一行不解释它。没有原型展示这些行，所以由 Troy 决定（A 点）。
10. **提示里的数字。** `menu` 的提示显示餐数和菜数，即菜单各格的计数，以及一周的日期，它们来自 `IsoWeek`。一道菜的份数来自 `read_week_menu`，它用 `read_servings` 读取份数，范围是 1 到 100（F05 设计 3.1）。份数通过 `str` 放进格子，不经过提示。命令行上错误的周作为文字放进 `NOT_A_WEEK`。文件里的问题只通过 `stop_at_error` 或 `menu new` 失败时的各行写到错误流，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `menu` 的提示不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。
11. **速度。** PT01 要求一个 PT01 周的 `menu show` 在 Troy 的电脑上在 1 秒内完成，取 5 次运行的中位数（v0.1-S31）。这一周有来自 63 个不同菜谱的 63 道菜，早餐、午餐和晚餐每餐 3 道。`menu show` 读的是 `show` 读的东西，再加上 `menus/` 的一次列表（52 个名称）、一个菜单文件和另外 62 个菜谱文件。F09 在 Troy 的电脑上的 PT01 基线是：`show` 的中位数 0.153 秒，`list` 0.789 秒；F10 的 `search` 是 0.780 秒。`show` 读设置、300 种食材的目录、`recipes/` 的一次列表和一个菜谱。`list` 多读 999 个菜谱，所以一个菜谱约耗 0.64 毫秒，多 62 个约耗 0.04 秒。在 F07 的审查里，52 个菜单约占 `check` 0.08 秒，所以一个菜单约耗 2 毫秒。表格有 7 行、3 个餐次列，约 2,000 个字符，`format_table` 每个量两次，计数行只渲染几次。所以 `menu show` 应该约耗 0.2 秒。这是根据上述耗时的估计，不是测量结果。测试计划可以在 PT01 文件夹上为它计时，就像 F09-T28 为 `list` 计时一样。`menu show` 把读到的菜谱放在一个只在一次运行里存在的字典里，所以几道菜写到的同一个菜谱只解析一次，没有模块保存缓存（架构 8）。`menu new` 不在 PT01 里。
12. **只导出两个命令。** `menu` 导出 `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND`，别的什么都不导出。在 v0.2 里，F14 的 `suggest` 可以引用 `menu`（架构 3）。F14 的设计把两个模块共用的东西加进 `menu`，比如选择 3 的文件格式或一道菜的格子，或者自己另存一份，就像 F09 把共用部分留给 F10 一样。所以在有功能使用之前，不导出任何名称。

运行 `menu new` 或 `menu show` 的 v0.1 场景，在这些选择下都成立：

- v0.1-S08：带字节顺序标记、用 CRLF 换行的文件读起来一样（F03 设计 2.3），所以 `menu show 2026-W47` 打印“Show the week after you fill it”的第一段输出。
- v0.1-S13：第 1 步打印“Create next week's menu”的三行，并逐字节写出原型里的文件（选择 3 和 5）。第 2 步打印中文的拒绝，并以 1 退出，文件保持原来的字节和修改时间（选择 4）。第 5 步和第 6 步打印“Show the week after you fill it”的两张表格（选择 8 和 9）。
- v0.1-S14：`menu new` 和 `menu new next` 创建本周和下周的文件，每个文件都有自己的 `week` 行（选择 2 和 3）。`menu show this` 以 `Menu for <T>,` 开头，每一餐都显示 `\u2014`，最后是 `NO_DISHES`（选择 9）。第 1 到 3 步都以 0 退出。
- v0.1-S15：第 1、2 和 4 步分别打印 `NO_MENU` 并以 1 退出，打印 `NOT_A_WEEK` 并以 2 退出，打印“A menu with a mistake”的三行并以 1 退出（选择 2、6 和 7）。
- v0.1-S16：`menu new 2026-W48` 打印 `7 days with breakfast, lunch, and dinner, all empty.`，并为每天写出三餐。`menu show 2026-W48` 有 Day、Breakfast、Lunch 和 Dinner 四列，在 Mon 23 Nov 的早餐显示 `Tomato and egg stir-fry \u00d73`，份数 3 来自设置，最后是 `1 meal, 1 dish. \u00d7n: servings.`。
- v0.1-S23：`menu show 2026-W47` 和 `menu show 2026-W48` 不写任何文件。
- v0.1-S25：中文表格是对齐的，因为 `format_table` 按显示宽度测量（F02 设计 2.8）。
- v0.1-S31：PT01（选择 11）。`menu show` 在 21 个格子里打印 63 道菜。

这三点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 没有原型展示这些文字。每一段都沿用某个原型里文字的措辞。建议按 2.2、2.4 和 3.1 的写法接受它们。
  - `menu new` 的英文拒绝，对应原型里的中文那一行：`C:\Users\Troy\recipe-menu\menus\2026-W47.toml already exists. Nothing was changed.`。
  - 新菜单的中文各行：`已创建 C:\Users\Troy\recipe-menu\menus\2026-W47.toml，日期为 2026年11月16日至22日：`、`共 7 天，每天有午餐和晚餐，都还是空的。` 和 `在各餐里填上菜谱 ID，然后运行“recipe-menu check”。`。
  - 一周没有菜单时的中文那一行：`2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。`。
  - 一餐、一道菜时的中文计数行：`1 餐，1 道菜。\u00d7n：份数。`。英文那一行就是 v0.1-S16 要求的那一行。
  - 一道菜也没有的周的那一行：`The menu has no dishes yet.` 和 `这个菜单还没有菜。`。
  - `menu new` 失败时的最后一行：`Nothing was changed.` 和 `没有做任何修改。`，也就是原型里拒绝那一行的后半句，或者两种语言的 `LEFT_BEHIND`。
- **B. 新菜单文件的语言**（选择 3）。
  - 做法 1，推荐：两种语言里文件都用英文注释，`--lang` 只改变输出。
  - 做法 2：注释跟随命令的语言，比如 `# 2026-W47：2026年11月16日至22日`，以及两行展示菜怎样写的中文。
  - 推荐做法 1 的理由：两种语言里文件的键都是英文单词，`init` 也已经在两种语言里写出相同的注释（F08 设计，选择 6）。只用一种文字，无论文件怎样创建，它都相同，v0.1-S13 也按原型检查它。
- **C. `menu new` 没能列出的文件夹的完整路径**（选择 4 和 2.2）。架构 6 允许 `menu new` 用完整路径写出它没能写成的文件（ADR-0009），但不包括列出失败时的文件夹 `menus\`，而 ADR-0009 第 5 节有意保持这个范围。所以用完整路径写出这个文件夹会修改架构 6，这要由 Troy 批准。
  - 做法 1，推荐：`menu new` 每次失败的第一行都用完整路径 `str(context.folder.root / problem.file)` 写出它的文件或文件夹，比如在 `  The folder is missing.` 上面写出 `C:\Users\Troy\recipe-menu\menus`。这样架构 6 在 `menu new` 没能写成的文件旁边，也写明它没能列出的文件夹。
  - 做法 2：列出失败时，像 `check` 和 `list_menu_weeks` 那样把文件夹写成 `menus`，只有打开、写入或关闭失败时才用完整路径写出文件，比如 `C:\Users\Troy\recipe-menu\menus\2026-W47.toml`。架构 6 保持不变。选择 4、2.2 里失败时的各行，以及 2.2 示例的最后一次运行，在 mock PR 之前修改。
  - 推荐做法 1 的理由：ADR-0009 的理由在这里同样成立。这一行必须说明写入在磁盘上的哪里失败，而 `menu new` 的其他各行都写出完整路径。用做法 2 时，失败的第一行会因为一种原因是相对路径，因为另一种原因是完整路径。
  - Troy 选定做法 1 之后，架构师在 F11 的 mock PR 之前，用一个 `[docs]` PR 把它记进架构 6 和一份 ADR，就像 ADR-0009 记下 F08 设计的待定问题 D 那样。

这些后续功能会在 F11 的基础上构建。细节由它们自己的设计决定。

- F13 的 `shop` 像 F11 一样得到它的周（选择 2），对没有菜单文件的周写出 `menus` 的 `NO_MENU`（选择 6）。它可以按 `menu show` 的顺序读它的文件（选择 7），常备清单放在目录之后。
- F14 的 `menu suggest` 可以引用 `menu`，而 `menu` 只导出它的两个命令（选择 12）。
- F15 的 `add` 可以照原样用 `create_file` 写出新的菜谱文件；有 `rice.TOML` 或 `Rice.toml` 时，`create_file` 在两个系统上都拒绝创建 `rice.toml`（3.3）。`add` 失败时，要先对架构 6 做它自己的修改，才能用完整路径写出它的文件（ADR-0009，第 5 节）。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/menu/__init__.py`、`messages.py`、放两个 `run` 函数的一个内部文件，以及 `src/recipe_menu/cli/_commands.py` 里的那两项。它把 `NO_MENU` 加进 `src/recipe_menu/menus/messages.py` 和 `src/recipe_menu/menus/__init__.py`。它把 `FileOutcome`、`FileCreation` 和 `create_file` 加进 `datafile` 的一个新的内部文件，比如 `_new_file.py`，以及 `src/recipe_menu/datafile/__init__.py`。它定义每条提示、字段齐全的两个命令，以及带有各个成员的 `FileOutcome`。它的 `FileCreation` 有四个字段，但没有 3.2 的检查。它的 `create_file` 什么都不碰，给出 `FileCreation(FileOutcome.CREATED)`，每个 `run` 不读文件、不写任何东西、不抛异常，并给出 0。所以检查输出、退出码 1、带退出码 2 的 `NOT_A_WEEK`、新文件的字节、拒绝执行或失败，或者 `create_file` 的结果或检查的新测试，在 mock 上都会失败（R09）。这些测试在 mock 上会通过，从而违反 R09：只检查某个命令的字段、帮助、某条提示（比如 `NO_MENU`）或退出码 0 的测试。检查 `cli` 在运行命令之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、`menu new 2026-W47 2026-W48`、`menu show --tag quick`、`menu show next --help` 或 `recipe-menu menu`。只检查命令不改变任何文件（比如 v0.1-S23 对 `menu show` 的检查）、被拒绝的 `menu new` 保留了文件，或者失败后什么都没留下的测试也是如此。检查 `FileOutcome` 的值，或者合法 `FileCreation` 的默认值和相等性的测试也是如此。每个这样的测试都还要检查 mock 做错的内容，比如输出、文件或结果。按估计，mock 改动 8 个文件，约 350 行，文件数超过 R03 的 5 个，所以它的说明要写明软限制的理由。理由是测试既直接用到 `create_file` 和 `NO_MENU`，也通过命令用到它们，所以 `menu`、`datafile` 和 `menus` 要在同一个阶段一起带上，和 F08 的 mock 一样。实现（PR 5）把两个命令放在 `menu` 的内部文件里，比如 `_run.py`、`_new.py` 和 `_show.py`，并把带 `FileCreation` 检查的 `create_file` 放在 `datafile` 的那个内部文件里。按估计，它改动 4 个文件，约 450 行，在 R03 以内，但接近它的 500 行。`create_file` 可以像 `_creation.py` 那样引用 `datafile` 的内部辅助函数，并在文档注释里指向 `create_data_folder` 的规则，让注释保持简短。改动 `_creation.py` 来共用它删除文件的代码，会让 PR 5 多出第五个文件，还会动到 F08 的代码。如果文档注释让它超过 500 行，它的说明要写明软限制的理由，所以开发工程师要早一点运行 troy-check。

### 2.1 `MENU_NEW_COMMAND`

- 模块：menu
- 功能：对 `menu new` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 创建这一周的菜单文件，并写出 2.2 的输出。

签名：

```python
MENU_NEW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "new")
#   help_line = MENU_NEW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("menu", "new")`。 | 无 |
| `help_line` | `Message` | `MENU_NEW_HELP`：“Create an empty week menu.”和“创建一个空的周菜单。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 把参数变成周，通过 `create_file` 创建这一周的菜单文件，并写出 2.2 的输出。 | 给出 0 或 1。为不是周的值抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出。遇到坏数据或磁盘上的失败时不抛异常。 |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`，它是可选的，不能重复。`WEEK_ARGUMENT` 是 `WEEK` 和 `周`，也就是 F05 原型帮助里的名称。 | 所以 `cli` 不传值或传入一个值（F05 设计 2.5）。 |
| `options` | `str` 的元组 | `()`。`menu new` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `menu new`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、用来取餐次的 `context.settings`、`context.folder`、`context.out`、`context.err` 和 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `menu new` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `()` 或只有一个值，比如 `("next",)`。它没有选项。 |

- 返回值：`MENU_NEW_COMMAND`，一个 `Command`。
  - `MENU_NEW_COMMAND.usage` 英文是 `menu new [WEEK]`，中文是 `menu new [周]`。所以帮助显示它们，用法错误引用 `recipe-menu menu new [WEEK]` 或 `recipe-menu menu new [周]`。
  - `MENU_NEW_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出各行，并给出 0 或 1。

F11 之后，帮助列出这些命令和选项，第二列从第 21 列之后开始（选择 1）。它们就是 F05 原型帮助里的各行，去掉 `shop` 那一行。英文：

```text
Commands:
  init               Create the data folder with example data.
  check              Check every data file for mistakes.
  list               List the recipes.
  show ID            Show one recipe.
  search WORD...     Find recipes by name, ingredient, or tag.
  menu new [WEEK]    Create an empty week menu.
  menu show [WEEK]   Show a week menu.

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

- 副作用：与 2.2 相同。`run` 通过 `create_file` 列出 `menus/` 并创建一个文件，写入 `context.out` 或 `context.err`。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，里面有 `menus/2026-W47.toml`，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。第一次运行用上下文的语言，并写出上下文设置里的餐次。帮助来自 `COMMANDS`，F11 之后它有七个命令。抛出异常的那次调用不碰任何文件，也不向任何流写出一行。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.menu import MENU_NEW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

assert MENU_NEW_COMMAND.words == ("menu", "new")
assert MENU_NEW_COMMAND.usage == BiText("menu new [WEEK]", "menu new [周]")
assert MENU_NEW_COMMAND.help_line.render(Lang.EN) == "Create an empty week menu."
assert MENU_NEW_COMMAND.help_line.render(Lang.ZH) == "创建一个空的周菜单。"
assert MENU_NEW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_NEW_COMMAND.options == ()
assert MENU_NEW_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
dinner_only = Settings(Lang.EN, (Meal.DINNER,), 2)
context = Context(Lang.ZH, folder, dinner_only, out, err, date(2026, 11, 17))
assert MENU_NEW_COMMAND.run(context, Arguments(("next",))) == 0
file = folder.menu_file("2026-W48")
assert out.getvalue().splitlines() == [
    f"已创建 {file}，日期为 2026年11月23日至29日：",
    "共 7 天，每天有晚餐，都还是空的。",
    "在各餐里填上菜谱 ID，然后运行“recipe-menu check”。",
]
assert err.getvalue() == ""
lines = [
    "# 2026-W48: 23 to 29 November 2026",
    '# A dish is a recipe ID, such as "tomato-egg",',
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
    'week = "2026-W48"',
]
for day in Day:
    lines += ["", f"[{day.value}]", "dinner = []"]
assert file.read_bytes() == "".join(f"{line}\n" for line in lines).encode("utf-8")

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
existing = folder.menu_file("2026-W47")
assert MENU_NEW_COMMAND.run(context, Arguments(("2026-W47",))) == 1
refusal = f"{existing} already exists. Nothing was changed.\n"
assert (out.getvalue(), err.getvalue()) == ("", refusal)


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
assert len(english) == 20
assert english[9:12] == [
    "  search WORD...     Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]    Create an empty week menu.",
    "  menu show [WEEK]   Show a week menu.",
]
assert english[14].startswith("  --lang en|zh       The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[10:12] == [
    "  menu new [周]      创建一个空的周菜单。",
    "  menu show [周]     查看一个周菜单。",
]
assert chinese[15].startswith("  --data 文件夹      数据文件夹。")

MENU_NEW_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu menu new`

- 模块：menu
- 功能：创建一周菜单文件的命令，文件里每天每餐都是空的，文件已存在时拒绝执行（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 3，以及 [4](../../requirements.zh-CN.md#4-功能点)）。F11 原型“Create next week's menu”展示了它。

签名：

```text
recipe-menu menu new [WEEK] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `WEEK` | 文字 | 菜单的周：`2026-W47` 这样的 ISO 周、`this` 或 `next`。 | 可选。不写时用本周。其他文字是用法错误（选择 2）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。它不改变文件（选择 3）。 | 按 F05 设计 2.10。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `menu new`。 | 无 |

`menu new` 按顺序执行这些步骤：

1. 它用 `week_from_argument(value, context.today)` 把 `WEEK` 的值变成周。`value` 是参数的值，命令行没有给出时是 `None`。结果为 `None` 时，它抛出 `UsageError(NOT_A_WEEK, None, week=value)`（选择 2）。
2. 它用这一周和 `context.settings.meals` 构建文件的文字（选择 3）。
3. 它调用一次 `create_file(context.folder, path, text)`，其中 `path = context.folder.menu_file(str(week))`（3.3）。
4. 它把结果对应的各行写到对应的流，并给出下表的退出码。

文件的文字是这些行，每行以 LF 结束：

1. `# {week}: {dates}`，用 `str(week)` 和 `week.date_range.get(Lang.EN)`，比如 `# 2026-W53: 28 December 2026 to 3 January 2027`。
2. `# A dish is a recipe ID, such as "tomato-egg",`
3. `# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.`
4. `week = "{week}"`，用 `str(week)`。
5. 对 `Day` 的每一天，从周一到周日：一个空行，然后是带这一天的值的 `[{day}]`，然后对 `context.settings.meals` 的每一餐按顺序写一行带这一餐的值的 `{meal} = []`。

所以用示例的设置，在 2026 年 11 月 10 日星期二运行 `recipe-menu menu new next`，会写出 F11 原型里的文件 `menus/2026-W47.toml`，两种语言里字节都相同：

```toml
# 2026-W47: 16 to 22 November 2026
# A dish is a recipe ID, such as "tomato-egg",
# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.
week = "2026-W47"

[monday]
lunch = []
dinner = []

[tuesday]
lunch = []
dinner = []

[wednesday]
lunch = []
dinner = []

[thursday]
lunch = []
dinner = []

[friday]
lunch = []
dinner = []

[saturday]
lunch = []
dinner = []

[sunday]
lunch = []
dinner = []
```

- 返回值：退出码，以及写在对应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `create_file` 给出 `CREATED`。 | 输出流：新菜单的三行。 |
| 1 | 它给出 `EXISTS`。 | 错误流：`ALREADY_EXISTS`。输出流上什么也没有。 |
| 1 | 它给出 `FAILED`。 | 错误流：失败时的三行。输出流上什么也没有。 |
| 2 | `WEEK` 的值不是周。 | 错误流：`cli` 写出的 `NOT_A_WEEK`，不带下一行。输出流上什么也没有。 |

新菜单给出这些行，每行以换行结束：

1. `CREATED`，带 `file` 和 `dates`。
2. `EMPTY_DAYS`，带 `meals`。
3. `NEXT_STEP`。

拒绝执行只有一行：`ALREADY_EXISTS`，其中 `file` 是已经存在的那个条目（选择 4）。

失败时有三行。第一行是问题所在文件的完整路径 `str(context.folder.root / problem.file)`。列出失败时，那就是文件夹，比如 `C:\Users\Troy\recipe-menu\menus`。这采用的是 C 点的做法 1，由 Troy 决定（选择 4）。用做法 2 时，列出失败给出 `str(problem.file)`，比如 `menus`，只有打开、写入或关闭失败才给出完整路径。第二行是两个空格加上 `problem.text(context.lang)`。结果的 `left` 为空时，第三行是 `CHANGED_NOTHING`，否则是带 `week` 的 `LEFT_BEHIND`。在下面这个 Windows 上的例子里，你可以读 `menus\`，但不能在里面创建文件：

```text
PS> recipe-menu menu new next
C:\Users\Troy\recipe-menu\menus\2026-W47.toml
  The file cannot be written: access is denied.
Nothing was changed.
PS> $LASTEXITCODE
1
```

`menu new` 的提示如下：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `MENU_NEW_HELP` | `Create an empty week menu.` | `创建一个空的周菜单。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `CREATED` | `Created {file} for {dates}:` | `已创建 {file}，日期为 {dates}：` |
| `EMPTY_DAYS` | `7 days with {meals}, all empty.` | `共 7 天，每天有{meals}，都还是空的。` |
| `NEXT_STEP` | `Add recipe IDs to the meals, then run "recipe-menu check".` | `在各餐里填上菜谱 ID，然后运行“recipe-menu check”。` |
| `ALREADY_EXISTS` | `{file} already exists. Nothing was changed.` | `{file} 已存在。没有做任何修改。` |
| `CHANGED_NOTHING` | `Nothing was changed.` | `没有做任何修改。` |
| `LEFT_BEHIND` | `menu new could not remove the file that it created. Delete it, then run "recipe-menu menu new {week}" again.` | `menu new 没能删除它创建的文件。请删除这个文件，然后再运行“recipe-menu menu new {week}”。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `file` | 完整路径。在 `CREATED` 里是 `str(path)`，即新文件。在 `ALREADY_EXISTS` 里是 `str(creation.existing)`，即已经存在的那个条目。`context.folder.root` 是绝对路径（F05 设计 2.4）。 |
| `dates` | `week.date_range`，作为 `BiText`：`16 to 22 November 2026` 和 `2026年11月16日至22日`。 |
| `meals` | `context.settings.meals` 里每一餐的 `Meal.label` 的 `and_list`：`lunch and dinner` 和 `午餐和晚餐`。 |
| `week` | `str(week)`，比如 `2026-W47`。 |

按这些提示，可以得出 F11 原型里的各行，比如 `7 days with lunch and dinner, all empty.` 和 `C:\Users\Troy\recipe-menu\menus\2026-W47.toml 已存在。没有做任何修改。`。

错误：

`cli` 在运行 `menu new` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，`NOT_A_WEEK`，不带下一行：`"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `WEEK` 的值不是周（第 1 步）。 |
| 退出码 1，错误流上是 `ALREADY_EXISTS` | `menus/` 里有一个条目，名称与文件名相同，或者只在 A 到 Z 的大小写上不同（选择 4）。每个条目都保持原来的字节和修改时间。 |
| 退出码 1，错误流上是失败时的三行 | 列出 `menus/` 失败，或者一个 `OSError` 让文件没能写成（选择 4）。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `menu new` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`Unexpected argument "2026-W48". Write "recipe-menu menu new [WEEK]".` | 命令行写了两个周。 |
| 退出码 2，先是没有选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"menu new" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。`create_file` 删除写了一半的文件，`cli` 不再写出任何东西（选择 4）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。周写错时，`menu new` 什么都不碰。否则它调用一次 `create_file`。这次调用列出 `menus/` 并创建菜单文件；拒绝执行或列出失败时什么都不创建；失败之后删除写了一半的文件（3.3）。`menu new` 不读任何数据文件。它把各行写到输出流或错误流。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。示例先清空 `menus/`，和 F11 原型一样，所以前两次运行给出“Create next week's menu”的两段输出，和 v0.1-S13 的运行一样。后面的运行展示 v0.1-S16 和选择 4 的几种情况。最后一次运行时没有 `menus\`，它按 C 点的做法 1 用完整路径写出这个文件夹。

```python
import io
import shutil
from datetime import date

from recipe_menu.cli import main
from recipe_menu.menus import Day


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


def menu_text(week: str, dates: str, meals: list[str]) -> bytes:
    lines = [
        f"# {week}: {dates}",
        '# A dish is a recipe ID, such as "tomato-egg",',
        '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
        f'week = "{week}"',
    ]
    for day in Day:
        lines += ["", f"[{day.value}]", *(f"{meal} = []" for meal in meals)]
    return "".join(f"{line}\n" for line in lines).encode("utf-8")


for path in folder.menus.iterdir():
    path.unlink()
file = folder.menu_file("2026-W47")
assert run("menu", "new", "next") == (
    0,
    [
        f"Created {file} for 16 to 22 November 2026:",
        "7 days with lunch and dinner, all empty.",
        'Add recipe IDs to the meals, then run "recipe-menu check".',
    ],
    [],
)
assert file.read_bytes() == menu_text("2026-W47", "16 to 22 November 2026", ["lunch", "dinner"])
made = file.stat().st_mtime_ns
exists = [f"{file} 已存在。没有做任何修改。"]
assert run("menu", "new", "next", "--lang", "zh") == (1, [], exists)
assert file.stat().st_mtime_ns == made

folder.settings.write_text('meals = ["breakfast", "lunch", "dinner"]\n', encoding="utf-8")
code, out, err = run("menu", "new", "2026-W48")
assert (code, out[1], err) == (0, "7 days with breakfast, lunch, and dinner, all empty.", [])
every_meal = ["breakfast", "lunch", "dinner"]
week48 = menu_text("2026-W48", "23 to 29 November 2026", every_meal)
assert folder.menu_file("2026-W48").read_bytes() == week48

wrong_case = folder.menus / "2026-w49.toml"
wrong_case.write_text("", encoding="utf-8")
refusal = f"{wrong_case} already exists. Nothing was changed."
assert run("menu", "new", "2026-W49") == (1, [], [refusal])
assert sorted(path.name for path in folder.menus.iterdir()) == [
    "2026-W47.toml",
    "2026-W48.toml",
    "2026-w49.toml",
]

week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "new", "2026-W99") == (2, [], [week_error])

shutil.rmtree(folder.menus)
missing = [str(folder.menus), "  The folder is missing.", "Nothing was changed."]
assert run("menu", "new", "2026-W50") == (1, [], missing)
assert not folder.menus.exists()
```

### 2.3 `MENU_SHOW_COMMAND`

- 模块：menu
- 功能：对 `menu show` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 写出 2.4 的这一周。

签名：

```python
MENU_SHOW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "show")
#   help_line = MENU_SHOW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("menu", "show")`。 | 无 |
| `help_line` | `Message` | `MENU_SHOW_HELP`：“Show a week menu.”和“查看一个周菜单。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 把参数变成周，读取目录、各个列表、这一周的菜单和它写到的菜谱，并写出 2.4 的这一周。 | 给出 0 或 1。为不是周的值抛出 `UsageError`，而且在读取任何文件、写出任何输出之前抛出。遇到坏数据不抛异常。 |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`，用 2.2 的 `WEEK_ARGUMENT`。 | 所以 `cli` 不传值或传入一个值（F05 设计 2.5）。 |
| `options` | `str` 的元组 | `()`。`menu show` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `menu show`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、`context.folder`、给 `read_week_menu` 用的 `context.settings`、`context.out`、`context.err` 和 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `menu show` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `()` 或只有一个值，比如 `("2026-W47",)`。它没有选项。 |

- 返回值：`MENU_SHOW_COMMAND`，一个 `Command`。
  - `MENU_SHOW_COMMAND.usage` 英文是 `menu show [WEEK]`，中文是 `menu show [周]`。所以帮助显示它们，用法错误引用 `recipe-menu menu show [WEEK]` 或 `recipe-menu menu show [周]`。
  - `MENU_SHOW_COMMAND.run(context, arguments)` 按 2.4 的步骤执行，用 `context.lang` 写出输出，并给出 0 或 1。

错误：

`run` 在读任何文件之前把参数变成周。

| 错误 | 何时发生 |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | 对 `WEEK` 的值，`week_from_argument` 给出 `None`（选择 2）。 |

- 副作用：与 2.4 相同。`run` 通过 F03、F04 和 F06 的读取函数读取目录、两个列表、一个菜单文件和菜单写到的菜谱，写入 `context.out` 或 `context.err`，不写任何文件。
- 性能指标：无。PT01 从启动到退出为 `recipe-menu menu show`（2.4）计时，而它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本。上下文里是默认设置，也就是示例的设置，输出跟随 `context.lang`。这次运行给出 F11 原型“Show the week after you fill it”的第一段输出。`row` 写出表格的一行，表格两列宽 10 列和 25 列（选择 8）。英文表格里每个字符都占一列，所以用 `str` 补空格得到的各行与 `format_table` 的相同。抛出异常的那次调用不读任何文件，也不向任何流写出一行。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.commands.menu import MENU_SHOW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert MENU_SHOW_COMMAND.words == ("menu", "show")
assert MENU_SHOW_COMMAND.usage == BiText("menu show [WEEK]", "menu show [周]")
assert MENU_SHOW_COMMAND.help_line.render(Lang.EN) == "Show a week menu."
assert MENU_SHOW_COMMAND.help_line.render(Lang.ZH) == "查看一个周菜单。"
assert MENU_SHOW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_SHOW_COMMAND.options == ()
assert MENU_SHOW_COMMAND.folder is FolderUse.READ

DASH, TIMES = "\u2014", "\u00d7"


def row(day: str, lunch: str, dinner: str) -> str:
    return f"{day:10}   {lunch:25}   {dinner}".rstrip()


out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert MENU_SHOW_COMMAND.run(context, Arguments(("next",))) == 0
assert out.getvalue().splitlines() == [
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    row("Day", "Lunch", "Dinner"),
    row("Mon 16 Nov", DASH, f"Tomato and egg stir-fry {TIMES}2"),
    row("", "", f"Stir-fried choy sum {TIMES}2"),
    row("", "", f"Steamed rice {TIMES}2"),
    row("Tue 17 Nov", DASH, f"Mapo tofu {TIMES}2"),
    row("", "", f"Steamed rice {TIMES}2"),
    row("Wed 18 Nov", DASH, DASH),
    row("Thu 19 Nov", DASH, DASH),
    row("Fri 20 Nov", DASH, DASH),
    row("Sat 21 Nov", f"Tomato and egg noodles {TIMES}2", DASH),
    row("Sun 22 Nov", DASH, f"Cola chicken wings {TIMES}4"),
    row("", "", f"Stir-fried choy sum {TIMES}4"),
    row("", "", f"Steamed rice {TIMES}4"),
    "",
    f"4 meals, 9 dishes. {TIMES}n: servings.",
]
assert err.getvalue() == ""

MENU_SHOW_COMMAND.run(context, Arguments(("this week",)))  # raises UsageError
```

### 2.4 `recipe-menu menu show`

- 模块：menu
- 功能：把一周菜单打印成按天和餐排列的表格的命令，写出每道菜和它的份数（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 3，以及 [4](../../requirements.zh-CN.md#4-功能点)）。F11 原型的“Show the week after you fill it”、“A week without a menu”和“A menu with a mistake”展示了它。

签名：

```text
recipe-menu menu show [WEEK] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `WEEK` | 文字 | 要查看的周：`2026-W47` 这样的 ISO 周、`this` 或 `next`。 | 可选。不写时用本周。其他文字是用法错误（选择 2）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。 | 按 F05 设计 2.10。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `menu show`。 | 无 |

`menu show` 按顺序执行这些步骤。第 1 步不读文件。每个读文件的步骤都用前面步骤给出的东西，每个发现错误的步骤都让命令停下（选择 7）。

1. 它用 `week_from_argument(value, context.today)` 把 `WEEK` 的值变成周。结果为 `None` 时，它抛出 `UsageError(NOT_A_WEEK, None, week=value)`（选择 2）。
2. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`menu show` 对第一个错误给出 `stop_at_error(context, error)`。
3. `list_recipe_ids(context.folder)` 给出 `ids` 和它们的问题（F04 设计 2.5）。问题里有错误时，`menu show` 用 `stop_at_error` 在第一个错误处停下。
4. `list_menu_weeks(context.folder)` 给出 `weeks` 和它们的问题（F06 设计 2.8）。问题里有错误时，`menu show` 用 `stop_at_error` 在第一个错误处停下。
5. `weeks` 里没有这一周时，`menu show` 把带 `week=str(week)` 的 `NO_MENU` 写到错误流，并给出 1（选择 6）。
6. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` 给出 `menu` 和它的问题（F06 设计 2.9）。问题里有错误时，`menu show` 用 `stop_at_error` 在第一个错误处停下。
7. 对 `menu` 里的菜写到的每个菜谱 ID，每个只取一次，按第一道写到它的菜的顺序，`read_recipe(context.folder, catalog, recipe_id)` 给出这个菜谱和它的问题（F04 设计 2.6）。菜的顺序是周一到周日，各餐按 `menu.meals` 的顺序，菜按文件里的顺序。问题里有错误时，`menu show` 用 `stop_at_error` 在第一个错误处停下。
8. 它把下面的输出写到输出流，并给出 0。

第 2、3 和 7 步的警告不改变任何东西（选择 7）。

- 返回值：退出码，以及写在对应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `menu show` 写出了这一周，包括一道菜也没有的周。 | 输出流：标题、表格和计数行。 |
| 1 | 这一周没有菜单文件。 | 错误流：`NO_MENU`。输出流上什么也没有。 |
| 1 | 某个文件有错误。 | 错误流：`stop_at_error` 的三行。输出流上什么也没有。 |
| 2 | `WEEK` 的值不是周。 | 错误流：`cli` 写出的 `NOT_A_WEEK`，不带下一行。输出流上什么也没有。 |

输出是这些行，按这个顺序，每行以换行结束：

1. `MENU_HEADING`，带 `week` 和 `dates`。
2. 一个空行。
3. `format_table(rows)` 的各行，没有缩进，用默认间距 3，不带 `min_widths`（F02 设计 2.9，选择 8）。
4. 一个空行。
5. `menu` 有一格里有菜时，是带 `meals` 和 `dishes` 的 `COUNT_LINE`。一格都没有时，是 `NO_DISHES`（选择 9）。

`rows` 是表头行，然后是 `Day` 的每一天各一行，从周一到周日。`day_date` 是这一天的日期，对 `list(Day)[i]` 这一天是 `week.dates[i]`（F06 设计 2.1）。

| 列 | 表头 | 单元格 |
| --- | --- | --- |
| 日期 | `DAY_HEADING` | `short_date(day_date).get(context.lang)`，比如 `Mon 16 Nov` 和 `周一 11月16日`。 |
| `menu.meals` 的每一餐各一列，按它们的顺序 | `meal.heading.get(context.lang)`，比如 `Lunch` 和 `午餐` | `menu.dishes(day, meal)` 为空时是 `\u2014`。否则 `menu.dishes(day, meal)` 的每道菜占一行，按它们的顺序，用 `\n` 连接。一道菜的那一行是 `f"{name} \u00d7{dish.servings}"`，其中 `name` 是第 7 步为 `dish.recipe_id` 读到的菜谱的 `recipe.name.get(context.lang)`。 |

`menu show` 的提示如下。`MEAL_COUNT` 和 `DISH_COUNT` 是 `Plural` 值（F02 设计 2.4），各按自己的 `count` 选择。它们“多个时”的形式用于 1 以外的每个数。`menu show` 还用 2.2 的 `WEEK_ARGUMENT` 和 `menus` 的 `NO_MENU`（3.1）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `MENU_SHOW_HELP` | `Show a week menu.` | `查看一个周菜单。` |
| `MENU_HEADING` | `Menu for {week}, {dates}` | `{week} 菜单，{dates}` |
| `DAY_HEADING` | `Day` | `日期` |
| `MEAL_COUNT`，一个时 | `{count} meal` | `{count} 餐` |
| `MEAL_COUNT`，多个时 | `{count} meals` | `{count} 餐` |
| `DISH_COUNT`，一个时 | `{count} dish` | `{count} 道菜` |
| `DISH_COUNT`，多个时 | `{count} dishes` | `{count} 道菜` |
| `COUNT_LINE` | `{meals}, {dishes}. \u00d7n: servings.` | `{meals}，{dishes}。\u00d7n：份数。` |
| `NO_DISHES` | `The menu has no dishes yet.` | `这个菜单还没有菜。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `week` | `str(week)`，比如 `2026-W47`。 |
| `dates` | `week.date_range`，作为 `BiText`。 |
| `meals` | `MEAL_COUNT`，按 `menu` 里至少有一道菜的格数选择，`count` 设为这个数，作为 `BiText`。 |
| `dishes` | `DISH_COUNT`，按 `menu` 所有格子里的菜数选择，`count` 设为这个数，作为 `BiText`。 |
| `count` | 每个 `Plural` 的数。 |

按这些提示，可以得出 F11 原型里两种语言的各行，比如 `Menu for 2026-W47, 16 to 22 November 2026`、`2026-W47 菜单，2026年11月16日至22日` 和 `4 餐，9 道菜。\u00d7n：份数。`。

错误：

`cli` 在运行 `menu show` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，`NOT_A_WEEK`，不带下一行：`"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `WEEK` 的值不是周（第 1 步）。 |
| 退出码 1，错误流上是 `NO_MENU`：`There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | `menus/` 的列表里没有这一周的文件（第 5 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行，比如 `menus\2026-W47.toml, Monday dinner`、`  Unknown recipe "tomato-eggs".` 和 `RUN_CHECK` | 目录、`recipes/` 的列表、`menus/` 的列表、这一周的菜单文件，或者菜单写到的某个菜谱文件有错误（第 2 到 4 步、第 6 步和第 7 步）。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `menu show` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`Unexpected argument "2026-W48". Write "recipe-menu menu show [WEEK]".` | 命令行写了两个周。 |
| 退出码 2，先是没有选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"menu show" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。不再写出任何东西（F05 设计 2.10）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `menu show` 把 `catalog.toml` 读一次，把 `recipes/` 列一次，把 `menus/` 列一次，把这一周的菜单文件读一次，把菜写到的每个菜谱文件各读一次，都通过 F03、F04 和 F06 的读取函数。周写错时，它不读任何文件。遇到错误或没有菜单的周之后，它不再读任何东西。它不读 `pantry.toml`、别的菜单或菜单没写到的菜谱。它写入输出流或错误流。它不写任何文件，所以每个文件和文件夹都保持原来的字节和修改时间（v0.1-S23）。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。第一次运行给出 F11 原型“Show the week after you fill it”的第二段输出，示例检查其中几行。接下来的运行给出“A week without a menu”。然后，菜单没写到的菜谱里的错误不改变任何东西，缺少的英文名称显示为中文名称。菜单写到的菜谱里的错误让 `menu show` 停下，“A menu with a mistake”里的错误也让它停下，而且这个文件先被读到。新菜单的每一餐都显示 `\u2014`，`menus\` 不存在时 `menu show` 停下。

```python
import io
import shutil
from datetime import date
from pathlib import Path

from recipe_menu.cli import main
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, short_date


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


code, out, err = run("menu", "show", "2026-W47", "--lang", "zh")
assert (code, err) == (0, [])
assert out[:5] == [
    "2026-W47 菜单，2026年11月16日至22日",
    "",
    "日期            午餐            晚餐",
    "周一 11月16日   \u2014               番茄炒蛋 \u00d72",
    " " * 32 + "清炒菜心 \u00d72",
]
assert out[11] == "周六 11月21日   番茄鸡蛋面 \u00d72   \u2014"
assert out[-2:] == ["", "4 餐，9 道菜。\u00d7n：份数。"]

no_menu = ['There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.']
assert run("menu", "show", "2026-W48") == (1, [], no_menu)
no_menu_zh = ["2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。"]
assert run("menu", "show", "2026-W48", "--lang", "zh") == (1, [], no_menu_zh)
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "show", "2026-W99") == (2, [], [week_error])

edit(folder.recipe_file("red-braised-pork"), "servings = 2", "servings = 0")
edit(folder.recipe_file("rice"), ', en = "Steamed rice"', "")
code, out, err = run("menu", "show", "2026-W47")
assert (code, err) == (0, [])
assert out[5] == " " * 41 + "米饭 \u00d72"
assert out[-1] == "4 meals, 9 dishes. \u00d7n: servings."

edit(folder.recipe_file("mapo-tofu"), "郫县", "")
mapo = Path("recipes", "mapo-tofu.toml")
assert run("menu", "show", "2026-W47") == (
    1,
    [],
    [
        f"{mapo}, ingredient 3",
        '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
        'Run "recipe-menu check" to see every problem.',
    ],
)
edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
week47 = Path("menus", "2026-W47.toml")
assert run("menu", "show", "next") == (
    1,
    [],
    [
        f"{week47}, Monday dinner",
        '  Unknown recipe "tomato-eggs".',
        'Run "recipe-menu check" to see every problem.',
    ],
)

assert run("menu", "new", "2026-W48")[0] == 0
days = [short_date(day).get(Lang.EN) for day in IsoWeek(2026, 48).dates]
assert run("menu", "show", "2026-W48") == (
    0,
    [
        "Menu for 2026-W48, 23 to 29 November 2026",
        "",
        "Day          Lunch   Dinner",
        *(f"{day}   \u2014       \u2014" for day in days),
        "",
        "The menu has no dishes yet.",
    ],
    [],
)

shutil.rmtree(folder.menus)
assert run("menu", "show", "2026-W48") == (
    1,
    [],
    ["menus", "  The folder is missing.", 'Run "recipe-menu check" to see every problem.'],
)
```

## 3. 对已有接口的修改

F11 给两个已实现模块的接口增加名称。F06 的 `menus` 导出提示 `NO_MENU`（3.1）。`datafile` 由 F03 创建，F08 给了它第一个写文件的功能；它导出 `FileOutcome` 和 `FileCreation`（3.2）以及 `create_file`（3.3），也就是架构 3 和 F08 设计第 2 节为 `menu new` 计划的写文件功能。F01 到 F10 导出的名称都不改变签名或行为，所以它们的测试不用修改也能通过。需求不改变，所以没有 `[docs]` PR 批准这些增加。架构师在这份设计里审查它们，就像审查 F10 的 `matching_form`，以及 F04、F05 和 F08 在它们的第 3 节里给 `datafile` 增加的名称一样。

F11 还在 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS` 里增加两项，这个文件是 `cli` 的内部文件，架构 4 允许每个命令功能这样做。有了这两项，真正的 `recipe-menu` 的帮助会列出 `menu new` 和 `menu show`，两张表的第二列从第 21 列之后开始，而不是第 19 列之后（选择 1）。运行真正的 `COMMANDS` 的测试只检查仍然成立的行和列：

- F05-T48 检查中文帮助的第一行和最后一行，F05-T49 不检查帮助的任何一行。
- F07-T17 检查 `check` 那一行以它的文字结尾，而且这段文字的起始列与 `--lang en|zh` 的文字的起始列相同。
- F08-T14 对 `init` 那一行做同样的检查，并检查它后面紧跟 `check` 那一行。
- F09-T01 检查 `list` 和 `show` 两行紧跟在 `check` 那一行后面，而且它们的文字从同一列开始。F09-T19 和 F09-T25 检查 `list --help` 和 `show ... --help` 给出与 `--help` 相同的帮助。
- F10-T01 检查 `search` 那一行紧跟在 `show ID` 那一行后面，以 `  search WORD... ` 开头，而且它的文字从同一列开始。F10-T11、F10-T15 和 F10-T16 检查带 `--help` 的 `search` 给出与 `--help` 相同的帮助，并且其中有 `search` 那一行。

列从 19 移到 21、`search` 那一行后面多出两行时，这些检查都成立。F07-T01、F08-T14、F09-T01 和 F10-T01 也比较一整段帮助，但每个都给 `main` 传入自己的命令，F11 不改变那些命令。没有测试用真正的 `COMMANDS` 运行 `menu`。F05 和 F06 中运行 `menu new`、`menu show` 或只运行 `menu` 的测试都给 `main` 传入自己的命令。所以 `recipe-menu menu` 从 `Unknown command "menu".` 变成 F05 的 `INCOMPLETE_COMMAND`（选择 1），没有测试需要修改。

F11 按这些接口的设计使用它们，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural`、`and_list` 和 `format_table`。
- F03 的 `DataFolder`、`Problem`、`Severity`、`Catalog` 和 `read_catalog`，以及 `SYSTEM_ERROR` 对 `reason` 这个值的规定（F03 设计 2.3）。
- F04 的 `list_toml_files` 列出问题表和它的四条提示，它们仍只在 `datafile` 内部使用（F04 设计 3.1），以及 `recipes` 里的 `Recipe`、`list_recipe_ids` 和 `read_recipe`。
- F05 的：`app` 里的 `Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error` 和 `stop_at_error`，`settings` 里带 `label` 和 `heading` 的 `Meal` 以及 `Settings`，还有 `cli` 里的 `COMMANDS`。
- F06 的 `Day`、带 `dates` 和 `date_range` 的 `IsoWeek`、`NOT_A_WEEK`、`WeekMenu`、`list_menu_weeks`、`read_week_menu`、`short_date` 和 `week_from_argument`。
- F08 的提示 `FILE_WRITE_DENIED` 和 `FILE_WRITE_ERROR`，它们仍只在 `datafile` 内部使用，以及 `create_data_folder` 写文件和删除文件的方式（F08 设计 3.2）。`create_file` 可以共用那段代码，`create_data_folder` 保持它的行为。

### 3.1 `NO_MENU`

- 模块：menus
- 功能：一周没有菜单文件时的那一行，`menu show` 写出它，F13 的 `shop` 以后也会写出它（选择 6）。`src/recipe_menu/menus/messages.py` 在 `NOT_A_WEEK` 旁边定义它，`src/recipe_menu/menus/__init__.py` 引入它，并在 `__all__` 里列出它。`menus` 的其他每条提示仍只在内部使用，`messages.py` 的模块文档注释写明这两条导出的提示。

签名：

```python
NO_MENU: Final[Message]
```

参数：无

- 返回值：无。`NO_MENU` 是下面这条 `Message`，只有一个占位符 `week`，即按 `str(IsoWeek)` 写出的 ISO 周。它的英文是 F11 和 F13 原型里的那一行。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NO_MENU` | `There is no menu for {week}. Run "recipe-menu menu new {week}" to create it.` | `{week} 没有菜单。运行“recipe-menu menu new {week}”创建它。` |

这条提示说了下一步该运行什么，这是架构 6 对缺少菜单的要求，所以它只有一行。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.menus import NO_MENU

assert NO_MENU.placeholders == frozenset({"week"})
text = NO_MENU.render(Lang.EN, week="2026-W48")
assert text == 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
chinese = NO_MENU.render(Lang.ZH, week="2026-W48")
assert chinese == "2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。"
```

### 3.2 `FileOutcome` 和 `FileCreation`

- 模块：datafile
- 功能：`create_file`（3.3）的结果：它创建了文件、发现那里已经有一个条目，还是失败了，以及失败后它没能删除什么。`menu new` 按结果选择它的输出（2.2）。F08 的 `CreationOutcome` 和 `Creation` 描述整个数据文件夹，这两个描述一个文件。

签名：

```python
class FileOutcome(Enum):
    CREATED = "created"
    EXISTS = "exists"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class FileCreation:
    outcome: FileOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
    existing: Path | None = None
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `outcome` | `FileOutcome` | 发生了什么，见下表。 | 无 |
| `problem` | `Problem` 或 `None` | 让调用停下的原因，作为一个问题。 | `FAILED` 时是 `Severity.ERROR` 的 `Problem`，其他结果时是 `None`。 |
| `left` | `Path` 的元组 | 调用创建了这个文件、但失败后没能删除它时，以完整路径给出这个文件。 | `FAILED` 时为空或只有一个路径。其他结果时为空。 |
| `existing` | `Path` 或 `None` | 已经存在的那个条目，以完整路径给出，比如 `C:\Users\Troy\recipe-menu\menus\2026-w47.toml`。 | `EXISTS` 时是一个 `Path`，其他结果时是 `None`。 |

| 成员 | 何时 | `problem` | `left` | `existing` |
| --- | --- | --- | --- | --- |
| `CREATED` | 调用创建了文件，并写入了它的文字。 | `None` | 空 | `None` |
| `EXISTS` | 文件所在的文件夹里有一个条目，名称与文件名相同，或者只在 A 到 Z 的大小写上不同。调用什么都没创建。 | `None` | 空 | 那个条目 |
| `FAILED` | 列出文件夹失败，或者一个 `OSError` 让文件没能写成。调用创建了文件时，已经删除了它。 | 这个错误 | 没能删除时是这个文件，否则为空 | `None` |

- 返回值：一个 `FileOutcome` 成员，或者一个 `FileCreation`。两个 `FileCreation` 的四个字段都相等时它们相等，`FileCreation` 可以哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `outcome` 是 `FAILED` 而 `problem` 是 `None`，或者 `outcome` 是其他成员而 `problem` 不是 `None`。 |
| `ValueError` | `problem` 是 `Severity.WARNING`。 |
| `ValueError` | `left` 有一个以上的路径，或者它不为空而 `outcome` 不是 `FAILED`。 |
| `ValueError` | `outcome` 是 `EXISTS` 而 `existing` 是 `None`，或者 `outcome` 是其他成员而 `existing` 不是 `None`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import FileCreation, FileOutcome, Problem
from recipe_menu.text import Message

DENIED = Message("Access is denied.", "没有访问权限。")
assert [outcome.value for outcome in FileOutcome] == ["created", "exists", "failed"]
created = FileCreation(FileOutcome.CREATED)
assert (created.problem, created.left, created.existing) == (None, (), None)
entry = Path.cwd() / "menus" / "2026-w47.toml"
assert FileCreation(FileOutcome.EXISTS, existing=entry).existing == entry
problem = Problem.error(Path("menus", "2026-W47.toml"), None, DENIED)
left = (Path.cwd() / "menus" / "2026-W47.toml",)
failed = FileCreation(FileOutcome.FAILED, problem, left)
assert failed == FileCreation(FileOutcome.FAILED, problem, left)

FileCreation(FileOutcome.FAILED)  # raises ValueError
FileCreation(FileOutcome.EXISTS)  # raises ValueError
FileCreation(FileOutcome.CREATED, problem)  # raises ValueError
FileCreation(FileOutcome.CREATED, left=left)  # raises ValueError
FileCreation(FileOutcome.FAILED, problem, left + left)  # raises ValueError
warning = Problem.warning(problem.file, None, DENIED)
FileCreation(FileOutcome.FAILED, warning)  # raises ValueError
```

### 3.3 `create_file`

- 模块：datafile
- 功能：创建一个新文件并写入它的文字，从不覆盖任何条目（选择 4，[架构 6](../../architecture.zh-CN.md#6-错误处理)）。文件所在的文件夹里已经有与文件同名的条目时，它拒绝执行；只在 A 到 Z 的大小写上不同的条目也算，所以 Windows 和 Linux 给出相同的结果。它用独占模式打开文件，失败或被打断之后删除它。`menu new` 调用它（2.2），F15 的 `add` 也可以调用它。

签名：

```python
def create_file(folder: DataFolder, path: Path, text: str) -> FileCreation: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `path` | `Path` | 要创建的文件，比如 `folder.menu_file("2026-W47")`。 | 在 `folder.root` 里面，而且不是 `folder.root`。 |
| `text` | `str` | 文件的文字。 | UTF-8 能编码它。 |

- 返回值：一个 `FileCreation`（3.2）。

`create_file` 按这些步骤工作：

1. 它在访问磁盘之前用 `folder.relative(path)` 检查 `path`，并把 `text` 编码为 UTF-8。错误的参数抛出错误表里的错误。
2. 它用 `Path.iterdir` 列出 `path.parent`。以 `OSError` 失败的列出给出 `FAILED`。它的问题的文件是 `folder.relative(path.parent)`，比如 `menus`，没有位置，提示是 `list_toml_files` 列出问题表里的提示（F04 设计 3.1）：`FOLDER_IS_FILE`、`FOLDER_MISSING`、`FOLDER_ACCESS_DENIED` 或 `FOLDER_SYSTEM_ERROR`。所以调用报告不存在的 `menus\` 的方式与 `list_menu_weeks` 相同。
3. 把两个名称里 A 到 Z 的每个 ASCII 大写字母都换成小写后，名称与 `path.name` 相同的条目给出 `EXISTS`。它的 `existing` 是 `path.parent` 加上这个条目的名称。有几个条目都相同时，比如在 Linux 上，以名称完全相同的那个为准，否则取 `sorted` 顺序里的第一个。任何种类的条目都算：文件、文件夹或链接。调用不打开任何条目，所以每个条目都保持原来的字节和修改时间。
4. 它用独占模式 `"x"`、`encoding="utf-8"` 和 `newline="\n"` 打开 `path`（架构 8）。它在打开得到的文件上用一次 `write` 调用写入文字，文字为空时也是如此，然后关闭文件。所以文件里是这段文字的 UTF-8 字节，没有字节顺序标记，换行就是文字里的换行。然后调用给出 `FileCreation(FileOutcome.CREATED)`。

打开、写入和关闭都可能抛出 `OSError`。下表第一条适用的规则给出结果。`relative` 是 `folder.relative(path)`。`reason` 是这个错误的 `strerror`；`strerror` 为 `None` 或空时，是这个错误的类名，与 `SYSTEM_ERROR` 相同（F03 设计 2.3）。

| 错误 | 结果 |
| --- | --- |
| 打开时的 `FileExistsError` | `EXISTS`，`existing` 设为 `path`。列出之后又出现了一个条目，调用什么都没创建。 |
| `PermissionError` | `FAILED`，`FILE_WRITE_DENIED` 在 `relative`，没有位置。 |
| 其他任何 `OSError` | `FAILED`，带 `reason` 的 `FILE_WRITE_ERROR` 在 `relative`，没有位置。 |

文件从打开成功的那一刻起就算已创建。写入或关闭时出现 `OSError` 后，调用先用 `Path.unlink` 删除这个文件，再给出 `FAILED`。以 `OSError` 失败的删除把这个文件的完整路径放进 `left`。打开之后的其他任何异常，比如 Ctrl+C 带来的 `KeyboardInterrupt` 或 bug 的异常，都在 `finally` 块里执行同样的删除，然后继续传出，所以调用不给出结果。没有 `except` 子句捕获 `OSError` 以外的东西（架构 6 和 8）。调用只通过 `Path.iterdir`、模式 `"x"` 的 `open` 和 `Path.unlink` 访问磁盘，和 `create_data_folder` 一样，它也可以和 `create_data_folder` 共用那段代码（F08 设计 3.2）。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `path` 不在 `folder.root` 里面，或者它就是 `folder.root`。这项检查在调用访问磁盘之前进行。 |
| `UnicodeEncodeError` | `text` 里有 UTF-8 无法编码的字符，比如单独的代理项。这项检查在调用访问磁盘之前进行。 |

- 副作用：把 `path.parent` 列一次。创建 `path` 并写入它的文字；`EXISTS` 时和列出失败后什么都不创建。失败或被打断之后，删除它创建的文件。它不读任何文件。
- 性能指标：无

示例：

在这个示例里，`tmp` 是一个空临时文件夹。数据文件夹有 `menus/`，但没有 `recipes/`。失败的情况用一个 300 个字符的文件名，两个系统都拒绝它。

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder, FileOutcome, create_file
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "recipe-menu")
folder.menus.mkdir(parents=True)
file = folder.menu_file("2026-W47")
created = create_file(folder, file, 'week = "2026-W47"\n')
assert created.outcome is FileOutcome.CREATED
assert file.read_bytes() == b'week = "2026-W47"\n'

again = create_file(folder, file, "")
assert (again.outcome, again.existing) == (FileOutcome.EXISTS, file)
assert file.read_bytes() == b'week = "2026-W47"\n'
wrong_case = folder.menus / "2026-w48.toml"
wrong_case.write_text("", encoding="utf-8")
taken = create_file(folder, folder.menu_file("2026-W48"), "")
assert (taken.outcome, taken.existing) == (FileOutcome.EXISTS, wrong_case)

missing = create_file(folder, folder.recipe_file("rice"), "servings = 2\n")
assert missing.outcome is FileOutcome.FAILED
assert missing.problem is not None
assert (missing.problem.file, missing.problem.place) == (Path("recipes"), None)
assert missing.problem.text(Lang.EN) == "The folder is missing."
assert missing.left == ()

name = "x" * 300 + ".toml"
failed = create_file(folder, folder.menus / name, "\n")
assert failed.outcome is FileOutcome.FAILED
assert failed.problem is not None
assert failed.problem.file == Path("menus", name)
assert failed.problem.text(Lang.EN).startswith("The file cannot be written. The system says: ")
assert failed.left == ()
names = sorted(entry.name for entry in folder.menus.iterdir())
assert names == ["2026-W47.toml", "2026-w48.toml"]

create_file(folder, tmp / "elsewhere.toml", "")  # raises ValueError
create_file(folder, folder.root, "")  # raises ValueError
create_file(folder, file, "\udc80")  # raises UnicodeEncodeError
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `menu` 是架构 3 里的那个模块：文件夹 `src/recipe_menu/commands/menu/`，它的 `__init__.py` 在 `__all__` 里只列出 `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND`，提示放在它自己的 `messages.py` 里（架构 8，选择 1 和 12）。它引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`，它那一行允许这些模块，架构师按第 2 节和第 3 节建的模型也不需要别的模块。`cli` 里唯一的修改是 `COMMANDS` 中 `SEARCH_COMMAND` 之后的两项（架构 4）。第 3 节的新增是共享这些内容的正确方式。架构 2、3 和 6 把写文件交给 `datafile`，所以 `create_file` 应该放在那里。`create_data_folder` 做不了这件事，因为数据文件夹里有任何条目时它都会拒绝。新建一个内部文件，能让已有 393 行的 `_creation.py` 保持在 R06 之内。`menus` 负责周菜单，并且已经为各命令导出 `NOT_A_WEEK`，所以 `NO_MENU` 应该放在它旁边。F13 的 `shop` 不能引用 `menu`，但能从这里拿到它。放进 `text` 或 `app` 的话，这行关于周菜单的话就落在一个对周菜单一无所知的模块里。`FileOutcome` 是枚举，`FileCreation` 是带 `slots=True` 和元组字段的冻结 dataclass（架构 8）。它们是辅助值，和 F08 的 `CreationOutcome`、`Creation` 一样，架构 5.2 也没有列出那两个。新文件遵守架构 5.1：`example-data.md` 的键、不带字节顺序标记的 UTF-8，以及 LF 换行。`menu show` 只读架构 8 允许的内容：`cli` 里的设置、目录、两次列表、一个菜单，以及菜单提到的每个菜谱各一次（选择 7）。`menu new` 不读任何数据文件（选择 4）。两个命令都不在一次运行之外保留状态。 |
| 遵守错误处理和命名约定 | 通过 | 第 1 轮的发现 1 已解决。C 点把列出 `menus\` 失败的情况交给 Troy，写明两种做法、推荐做法 1 的理由，以及每种做法要改什么：做法 1 修改架构 6，做法 2 在 mock PR 之前修改选择 4、2.2 里失败时的各行和它示例的最后一次运行。选择 4 不再说架构 6 涵盖这个文件夹。它说做法 1 需要修改架构 6，由 Troy 决定，并说架构师在 F11 的 mock PR 之前，用一个 `[docs]` PR 把决定记进架构 6 和一份 ADR，就像 ADR-0009 记下 F08 设计的待定问题 D 那样。`menus\` 不存在的那一条和 2.2 里失败时的各行都指向做法 1，2.2 示例前的文字也说明它的最后一次运行采用做法 1。设计对架构 6 和 ADR-0009 的描述和它们一致：架构 6 只允许 `menu new` 用完整路径写出它没能写成的文件，ADR-0009 第 5 节要求其他情况另外修改架构 6。架构师推荐做法 1，理由就是 C 点给出的那个。备注 1，不阻塞（选择 4）：“Troy 决定之后，架构师……把决定记进架构 6 和一份 ADR”这句只对做法 1 成立，因为做法 2 让架构 6 保持不变。C 点写的是“Troy 选定做法 1 之后”，设计记下 Troy 的决定时，选择 4 可以照 C 点的说法写。本项其余部分和第 1 轮一样通过。退出码遵守架构 1 和 6。`menu new` 新建菜单时给出 0，拒绝或失败时给出 1。`menu show` 写出一周时给出 0，没有菜的一周也是；遇到 `NO_MENU`，或通过 `first_error` 和 `stop_at_error` 遇到某个读取函数的第一个错误时，给出 1。两个命令都在接触磁盘之前抛出 `UsageError(NOT_A_WEEK, None, week=value)`，`cli` 把它变成不带提示的 2（ADR-0008，决定 A）。`create_file` 把每个 `OSError` 变成一个值，不捕获更宽的异常，以独占模式打开文件，并在 `finally` 块里删除写了一半的文件。所以 Ctrl+C 不会留下写了一半的文件，只有 F08 设计选择 5 已经指出的 `open` 内部那一刻例外。输出写到 `context.out`，每个拒绝、失败和错误写到 `context.err`。命名遵守架构 8：UPPER_SNAKE 的 `Message` 和 `Plural` 常量，列举用 `and_list`，复数用 `Plural`，表格用 `format_table`。选择 10 成立。A 点：架构师同意推荐。每段新文字都是两种语言的 `Message` 或 `Plural`，并且都沿用某个原型里一行文字的措辞。B 点：架构师同意选项 1。只有一种文字，文件无论怎样创建都一样；它和英文的键以及 `init` 写出的文件一致（F08 设计，选择 6）；v0.1-S13 逐字节检查它。 |
| 不和已有接口重复 | 通过 | `menu` 调用 `week_from_argument`、`NOT_A_WEEK`、`list_menu_weeks`、`read_week_menu`、`short_date`、`IsoWeek.date_range`、`read_catalog`、`list_recipe_ids`、`read_recipe`、`first_error`、`stop_at_error`、`and_list`、`Plural.pick` 和 `format_table`，没有重写其中任何一个。在 `datafile` 内部，`create_file` 复用 F04 的列表问题，以及 F08 的 `FILE_WRITE_DENIED` 和 `FILE_WRITE_ERROR`。所以缺少 `menus\` 时，`menu new`、`menu show` 和 `check` 的说法相同。它没有重复 `create_data_folder`，后者创建整个数据文件夹，要么全部创建，要么什么都不留。`menus` 里的 `NO_MENU` 让 `menu show` 和 F13 的 `shop` 共用这一行的唯一一份，这是 F06 审查备注 4 的要求。`CHANGED_NOTHING` 和 `LEFT_BEHIND` 沿用了 `init` 两条内部提示的名字，文字不同。架构 8 让每个模块把提示放在自己的 `messages.py` 里，而且 `menu` 不能引用 `init`。失败的三行重复了 `init` 的几行代码。`app` 的 `problem_lines` 写的是相对路径，所以复制这几行比从 `app` 新导出一个名字代价更小。 |
| 只依赖排序在前面的功能 | 通过 | F11 使用 F01 和 F02 的 `lang` 和 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`、F05 的 `app`、`settings` 和 `cli`，以及 F06 的 `menus`。在 `datafile` 内部，它使用 F08 的写入提示和 F08 删除文件的方式。这些功能都排在 F11 前面，都在 main 上通过了测试。F05 是 F11 那一行的硬依赖，F02 和 F06 是它的软依赖。F08 不在那一行里，但它只通过共享模块 `datafile` 影响 F11，架构 4 允许共享模块这样做。对 F13、F14 和 F15 的计划把细节留给它们自己的设计，所以不约束以后的设计。F11 只需要标准库，所以 R16 没有要审查的。`docs/rules.md` 里没有类型为 Review、由架构师执行的 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写明了模块之间的每个假设。`menu new` 写出的文件，`read_week_menu` 必须读得没有问题，并且每个餐位都为空（F06 设计第 2 节）。模型对全部七种餐次组合检查了这一点，分别用这些设置、默认设置和不带设置来读。`create_file` 通过和 `list_toml_files` 相同的内部函数报告列表失败，所以它的问题和 `list_menu_weeks`、`check` 的相同。加入两个命令会让帮助的第二列从第 19 列之后移到第 21 列之后，第 3 节写明了这一点，测试运行也证实真正帮助的每个测试仍然成立。`NO_MENU` 只在文字里提到 `menu new`，就像 `text` 里的 `RUN_CHECK` 提到 `check`。选择 7 让 `menu show` 在 `menus/` 列表的第一个错误处停下，错误针对别的文件时也是。这和 `show` 一致，`show` 会在 `recipes/` 列表的错误处停下（F09 设计）。这样也让 Windows 和 Linux 一致：在 Windows 上，文件夹里有 `2026-w48.toml` 时读 `2026-W48` 会打开那个文件，而列表的错误让 `menu show` 先停下。简报第 2(b) 点：`create_file` 的顺序是对的。列表让两个系统给出相同的拒绝，并写出已有的那个条目。独占模式的打开才保证不会覆盖任何条目。通过它的 `FileExistsError` 那一行，它还能拦住列表之后才出现的条目，以及文件系统按比 A 到 Z 更宽的规则不分大小写的名字。顺序反过来的话，`create_file` 在 Linux 上会先创建文件，之后才发现另一个名字，只好再删掉文件。A 到 Z 的规则适合两个调用者，因为 ISO 周和菜谱 ID 只含 ASCII 字符（`is_recipe_id`）。按这个规则列一次表，在 Troy 的电脑上 52 个条目用 0.43 ms，1,000 个条目用 5.3 ms，和进程启动相比很小。第 1 轮的备注 1 和 2 已采纳：3.3 不再提到 `folder.relative`，关于 F15 的那一条写明，`add` 失败时要先对架构 6 做它自己的修改，才能用完整路径写出它的文件（ADR-0009，第 5 节）。 |
| 修改已实现的接口时走了变更流程 | 通过 | 第 3 节给 `menus` 加上 `NO_MENU`，给 `datafile` 加上 `FileOutcome`、`FileCreation` 和 `create_file`。F01 到 F10 的名字没有一个改变签名或行为，需求也不改变，所以不需要 `[docs]` PR。架构师在这里审查这些新增，就像审查 F10 的 `matching_form`，以及 F04、F05 和 F08 加到 `datafile` 里的名字那样。第 1 轮把模型放进分支的一份副本后，整个测试套件得到 483 个通过、3 个跳过，这 3 个是 main 上只在 Linux 运行的用例。所以 F05-T48、F05-T49、F07-T17、F08-T14、F09-T01、F09-T19、F09-T25、F10-T01、F10-T11、F10-T15、F10-T16 和其他每个测试都仍然成立，和第 3 节说的一样。模拟和实现的拆分是对的。模拟修改 8 个文件：`menu` 的三个文件、`cli/_commands.py`、`menus/messages.py`、`menus/__init__.py`、`datafile` 新的内部文件，以及 `datafile/__init__.py`。它超出软限制的理由成立，和 F08 的模拟一样：测试既直接调用 `create_file` 和 `NO_MENU`，也通过命令调用它们，所以三个模块都必须在模拟里能引用。模拟的桩让每个检查输出、文件、结果或 3.2 的检查的新测试都失败（R09），设计也写出了哪些测试会在模拟上通过。实现只修改 `menu` 和 `datafile` 的内部文件，所以它的 4 个文件符合 R03。第 1 轮的备注 3 已写进 mock 计划，它现在说明 PR 5 怎样保持在 R03 以内。C 点的做法 1 修改架构 6，但不改变任何已实现的接口：`Problem` 仍然保存相对于数据文件夹的文件，`problem_lines`、`stop_at_error` 和每个读取函数仍然用相对路径，和 ADR-0009 第 5 节对 `init` 说的一样。它的 `[docs]` PR 就是架构的变更流程（troy-mode 需求 5.7）。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 发现 1，属于“遵守错误处理和命名约定”：选择 4 用完整路径写出 `menus` 文件夹，架构 6 和 ADR-0009 都没有涵盖这种情况，所以要由 Troy 决定。备注 1 到 3 不阻塞。每个文件的 18 个代码块都和镜像里的相同，用 ruff 0.17.4 和项目的设置运行 `ruff format --check`，报告每个文件的 12 个 `python` 块都已格式化。架构师在分支的一份副本里按第 2 节和第 3 节建了模型，在 Windows 上用 Python 3.13.18，在 `tests/data/example/` 的新副本上运行了 7 个示例。每个断言和全部 11 个 `# raises` 都成立，抛出异常的调用都没有接触文件，也没有写任何流。模型的其他运行完全符合这些输出：两种语言各 20 行的帮助，第二列在第 21 列之后，等于 F05 原型的帮助去掉 `shop` 那一行；新菜单的三行，新文件的字节等于原型里的文件和 2.2 的 `toml` 块；中文的拒绝，之后文件保持原来的字节和修改时间；“Show the week after you fill it”的两张表，列宽为 10 和 25，以及 13 和 13；“A week without a menu”；以及“A menu with a mistake”。它们还符合带字节顺序标记和 CRLF 换行的 v0.1-S08；2026 年 12 月 30 日的 v0.1-S14，带 `# 2026-W53: 28 December 2026 to 3 January 2027` 和两种语言的 `NO_DISHES`；带 `1 meal, 1 dish.` 及其中文行的 v0.1-S16；以及 v0.1-S23。`menu show` 按选择 7 的顺序读文件，每个菜谱只读一次。模型还给出了打开被拒时的三行，在写入失败后删除了文件，在删除失败后写出 `LEFT_BEHIND`，在写入时按下 Ctrl+C 后以 130 退出，并且不留下文件。在用 `tests/pt01_support.py` 生成的 PT01 文件夹上，`menu show 2026-W26` 在 21 个单元格里写出 63 道菜，以及 `21 meals, 63 dishes.`。两组各 5 次运行中，`menu show` 的中位数为 0.262 s 和 0.247 s，同组里 `show recipe-0500` 为 0.231 s 和 0.203 s。当时电脑上还有别的测试在运行，`list` 用了约 1.0 s，而它的基线是 0.789 s。所以选择 11 约 0.2 s 的估计成立，远低于 1 秒。 | 要求修改。接口设计者按发现 1 的要求加上 C 点并修改选择 4。备注 1 到 3 可做可不做。架构师同意 A 点和 B 点的推荐，Troy 在批准这份设计时决定这两点。 |
| 2 | 0.2 版解决了“遵守错误处理和命名约定”下的发现 1：C 点把列出 `menus\` 失败的情况交给 Troy，选择 4、2.2 里失败时的各行和它示例前的文字都指向做法 1，和发现 1 的要求一致。第 1 轮的备注 1 到 3 已采纳。本轮的备注 1 不阻塞。`git diff 5caabb4 HEAD` 在每个文件里改动同样的 10 处，没有改动任何代码块，也没有改动第 4 节：文件头里的版本、选择 4 的两条、交给 Troy 决定的点数、C 点、关于 F15 的那一条、mock 计划、2.2 里失败时的各行、它示例前的文字、3.3，以及修改记录。每个文件的 18 个代码块都和第 1 轮的相同，也和镜像里的相同，每个文件仍然有同样的 36 个 Unicode 转义，两个文件的标题和表格也相同。用 ruff 0.17.4 和项目的设置运行 `ruff format --check`，报告两个文件以及每个文件的 12 个 `python` 块都已格式化。代码块和输出的各行都没有改变，所以架构师的模型在第 1 轮的运行结果仍然成立。 | 批准。Troy 在批准这份设计时决定 A、B、C 三点，架构师同意每一点的推荐。Troy 选定 C 点的做法 1 之后，架构师在 F11 的 mock PR 之前，用一个 `[docs]` PR 写下对架构 6 的修改和它的 ADR，就像 `[docs] Change the architecture for F08` 在 F08 的 PR 1 和 PR 2 之间合并那样。如果 Troy 选定做法 2，接口设计者在 mock PR 之前修改选择 4 和 2.2，架构 6 保持不变。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-14 | 初稿。 |
| 0.2 | 2026-11-14 | 回应架构师审查第 1 轮。C 点把列出 `menus\` 失败的情况交给 Troy：推荐的做法 1 让 `menu new` 的每次失败都用完整路径写出，这需要在 F11 的 mock PR 之前修改架构 6 并写一份 ADR；做法 2 把文件夹写成 `menus`。选择 4、2.2 里失败时的各行和它示例前的文字写明这一点，并采用做法 1。3.3 不再暗示 `folder.relative` 会访问磁盘。F15 那一条写明，`add` 失败时要先对架构 6 做它自己的修改，才能用完整路径写出它的文件。mock 计划写明 PR 5 怎样保持在 R03 以内。输出的各行和代码块都没有改变。 |
| 1.0 | 2026-11-14 | Troy 批准。 |
