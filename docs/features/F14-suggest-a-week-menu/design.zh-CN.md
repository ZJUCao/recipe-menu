---
troy-doc: "F14-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-17"
status: "Troy 已于 2026-11-17 批准"
mirror-of: "design.md"
---

# F14 推荐周菜单：接口设计

## 1. 功能

- 编号和名称：F14 推荐周菜单
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F06、F11

## 2. 接口

F14 在 `src/recipe_menu/commands/suggest/` 里构建命令模块 `suggest`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.suggest` 导出一个名称 `MENU_SUGGEST_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出它。你输入的命令是 `recipe-menu menu suggest`（2.2）。它的提示放在 `src/recipe_menu/commands/suggest/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F14 在它的 mock PR 里把 `MENU_SUGGEST_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `MENU_SHOW_COMMAND` 之后。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F14 还给四个已实现的模块加上架构 5.1 和 5.2 为它计划的东西（第 3 节）：给 `settings` 加上设置 `dishes`（3.1 和 3.2），给 `app` 里的 `Context`（3.3）和 `cli` 里的 `main`（3.4）加上随机数生成器，给 `datafile` 加上读取文件文字和解析 TOML 文字的功能（3.5 和 3.6）。F14 原型 `docs/prototypes/F14-suggest.md` 展示了这个命令，F05 原型说明 v0.2 会在帮助里加上它的那一行。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F14 提供的接口 |
| --- | --- |
| `recipe-menu menu suggest [WEEK]` 用随机选出的菜谱填满这一周菜单文件里的每个空餐（[需求 4](../../requirements.zh-CN.md#4-功能点)）。 | `recipe-menu menu suggest`（2.2），以及 `MENU_SUGGEST_COMMAND`（2.1）。它用 `Context.random` 来选（3.3，选择 6），并按选择 7 的规则修改文件。 |
| 每个空餐得到设置里为这一餐规定的菜数，默认 1 道。 | `settings.toml` 的键 `dishes`，由 `read_settings` 读进 `Settings.dishes`（3.1 和 3.2，选择 5，B 点）。 |
| 同一周里不会出现两次同一个菜谱。 | 选择 6：候选菜谱是这一周还没有的菜谱，`random.sample` 每个最多取一次。 |
| `--tag` 只从带这个标签的菜谱里选。 | 选项 `--tag`，由 `Catalog.find_tag` 按两种语言读取，和 `list --tag` 一样（选择 4）。 |
| 没有菜谱可选时，剩下的餐保持空着，命令会说明有几餐。 | 选择 9 的输出，以及针对需要的菜数比剩下的菜谱还多的一餐的 C 点。 |
| 已经填好的餐和文件的其余部分保持原样。 | 选择 7：只有得到菜的每一餐的 `[]` 会变，缺少的某餐那一行或某天的表会被加上。用 CR LF 换行或带字节顺序标记保存的文件，每一行的文字都不变，但会改用 LF 换行，也不再带这个标记。对新文字的检查，以及一步就改好文件的 `replace_file`（选择 8）。 |
| 要换一道菜，就清空它所在的那一餐，再运行一次 `menu suggest`。 | `SWAP_HINT`（选择 9）。你清空的那一餐又是空的了，它原来的菜谱可能再被选中（选择 6）。 |
| 接受周的命令接受 ISO 周、`this` 或 `next`。不写周时，用本周（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | F06 的 `week_from_argument` 和 `NOT_A_WEEK`（选择 2）。 |

下面每个接口都遵守这些规则：

- `suggest` 在包内只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`。架构 3 里它那一行允许这些模块。它既不需要 `units`、`shopping`，也不需要 `menu`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `suggest` 只通过 F03、F04 和 F06 的读取函数、`read_file_text`（3.5）和 `replace_file`（F13 设计 3.1）访问磁盘，这些函数都通过 `datafile` 工作（架构 8）。它只写这一周的菜单文件，以及写这个文件时 `replace_file` 用的临时文件 `menus/<week>.toml.tmp`（[需求 4](../../requirements.zh-CN.md#4-功能点)，[架构 5.1](../../architecture.zh-CN.md#51-数据文件)）。它只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西：它的随机选择来自 `cli` 创建的 `context.random`（3.3 和 3.4）。它不保存状态，读到的菜谱只在一次运行里存在。
- 读取函数遇到坏数据从不抛异常，`replace_file` 把每个 `OSError` 变成一个值（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`menu suggest` 在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。`run` 只为不是周的 `WEEK` 值抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出（F05 设计第 2 节）。传到 `cli` 的任何其他异常都是 bug。
- `MENU_SUGGEST_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。F14 不增加值类型。`Settings.dishes` 是三个 `int` 组成的元组，`Context.random` 是一个 `random.Random`（第 3 节）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F14 的接口都没有性能指标。PT01 不为 `menu suggest` 计时（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。选择 11 说明它要花多长时间，以及 F14 怎样让其他每个命令的启动仍然很快。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和第 3 节给出它们的规则。

1. **一个命令，在帮助里排在 `menu show` 之后。** F14 把 `MENU_SUGGEST_COMMAND` 加在 `COMMANDS` 里 `MENU_SHOW_COMMAND` 的后面。所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`。菜单的几个命令放在一起，v0.1 的命令保持原来的顺序。`menu suggest` 有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它（F05 设计 2.5），这是 v0.2-S14 的要求。它声明可选参数 `WEEK` 和选项 `--tag`。所以帮助写成 `menu suggest [WEEK]` 和 `menu suggest [周]`，分别占 19 列和 17 列。`menu suggest [WEEK]` 成为帮助里最宽的第一格，比 `menu show [WEEK]` 多 3 列。所以两种语言里，两张表的第二列都从第 24 列之后开始，而不是第 21 列之后，两张表的每一行都多 3 个空格。帮助共 22 行（2.1）。只写 `recipe-menu menu` 时，给出 F05 的 `INCOMPLETE_COMMAND`，现在是 `The commands that start with "menu" are "menu new", "menu show", and "menu suggest".`，后面是 `RUN_HELP_FOR_COMMANDS`，退出码 2。第 3 节列出这两处变化会让哪些测试失败。
2. **周。** `menu suggest` 像 F11 的命令和 `shop` 一样得到它的周（F11 设计，选择 2）：`week_from_argument(value, context.today)`（F06 设计 2.7），其中 `value` 是 `WEEK` 的值，命令行没有给出时是 `None`。ISO 周、`this` 或 `next` 以外的文字，比如 `2026-W99`，给出 `UsageError(NOT_A_WEEK, None, week=value)`，`cli` 只写出这条提示，并以 2 退出（ADR-0008，决定 A），这是 v0.2-S08 的要求。`run` 在访问磁盘、写出任何输出之前抛出它。之后的每一行都用 `str(week)` 写出周，比如 `next` 写成 `2026-W48`。
3. **`menu suggest` 读什么，在哪里停下。** 它只读需要的文件，顺序如下（2.2）：`cli` 里的设置、目录、`recipes/` 的列表、`menus/` 的列表、这一周的菜单、菜单文件的文字，然后是这一周还没有的每个菜谱。它既不读常备清单，也不读别的菜单。
   - 它用 `read_catalog` 读目录，因为 `find_tag` 和 `read_recipe` 需要目录（F03 设计 2.6，F04 设计 2.6）。和 `list` 一样，它读完目录就查找 `--tag` 的标签，所以未知的标签会让它在读别的东西之前停下（选择 4）。
   - 它用 `list_recipe_ids` 列出 `recipes/`，用 `list_menu_weeks` 列出 `menus/`，再用 `read_week_menu` 和 `context.settings` 读这一周，顺序和停下的地方都和 `menu show` 相同（F11 设计，选择 7）。列表里没有的周在错误流上给出 `menus` 的 `NO_MENU`（F11 设计 3.1），退出码 1，这是 v0.2-S07 和 v0.2-S08 的要求。
   - 没有空餐的周让它在这里停下，给出 `NO_EMPTY_MEAL`，退出码 0（选择 9）。所以填满的周不再多读任何东西。
   - 它用 `read_file_text`（3.5）读菜单文件的文字，在文字里找到每个空餐的位置（选择 7）。它无法填写的文件让它在这里停下，给出 `CANNOT_FILL`，这发生在读任何菜谱之前。
   - 它用 `read_recipe` 读这一周的菜都没写到的每个菜谱，每个只读一次，按 ID 的顺序，不写 `--tag` 时也这样。所以它只从读起来没有错误的菜谱里选。和 `list` 一样，有错误的菜谱会让 `menu suggest` 停下（F09 设计，选择 2），`check` 会报告它。这一周已经有的菜谱不是候选，所以不读。

   每个读取函数的第一个错误都会让 `menu suggest` 用 `first_error` 和 `stop_at_error` 停下，它们写出这个问题和 `RUN_CHECK`，并给出 1（F05 设计 2.8），和 F11 原型“A menu with a mistake”显示的一样，也是 v0.2-S08 的要求。`check` 用相同的读取函数、相同的参数读这些文件，所以让 `menu suggest` 停下的错误一定在 `check` 的错误里（F07 设计，选择 8）。`menu suggest` 不写出警告，警告也从不改变退出码（架构 6）。遇到错误、`NO_MENU`、未知的标签或 `CANNOT_FILL` 之后，它不写任何文件。
4. **标签。** `menu suggest` 用 `Catalog.find_tag`（F03 设计 2.6）查找 `--tag` 的标签，和 `list` 一样（F09 设计，选择 4）。所以这个值按两种语言匹配标签的名称：两端的空白不算，只有字母 A 到 Z 区分大小写。`find_tag` 找不到标签时，`menu suggest` 把 `UNKNOWN_TAG`（目录里没有标签时是 `NO_TAGS`）写到错误流，并以 1 退出，文字和 `list` 的相同，这是 v0.2-S08 的要求。`suggest` 不能引用 `browse`（架构 3），而 `browse` 只导出它的命令。所以 `suggest` 自己保存这两条提示的一份副本，文字相同，就像 `shop` 保存了 `menu` 一些提示的副本（F13 设计，选择 3）。和 `list` 一样，输出用所选语言里的名称写出标签，所以 `--tag 快手` 和 `--tag quick` 给出相同的输出（v0.2-S02）。
5. **一餐的菜数。** 设置用键 `dishes` 给出每一餐的菜数。它是一张表，为需要的每一餐写一个数，比如 `dishes = { dinner = 2 }`（B 点）。表里没写的一餐得到 1，这是需求 4 的说法。这个数是 1 到 10 之间的整数：一餐很少有更多的菜，而 `20` 这样的笔误会让一周有 140 道菜。`read_settings` 把这个键读进 `Settings.dishes`，`menu suggest` 用 `Settings.dishes_for(meal)` 取得它（3.1 和 3.2）。错误的值是设置的错误，和其他键一样，会让每个命令停下，`check` 也会报告它。`init` 写出的设置文件仍然没有这个键，所以 `init` 写的文件、`example-data.md` 和 v0.1 的场景都保持不变。对 v0.2-S06，让晚餐有 2 道菜的设置就是 `dishes = { dinner = 2 }` 这一行。
6. **随机选择。**
   - 空餐是菜单里没有菜的格子，按 `WeekMenu.slots` 的顺序：周一到周日，每天按设置里各餐的顺序（F06 设计 2.6）。有菜的格子是保留的餐。
   - 候选菜谱是 `list_recipe_ids` 给出的、这一周的菜都没写到的 ID，按 ID 的顺序，其中 `read_recipe` 读起来没有错误，带 `--tag` 时菜谱的 `tags` 还要含有这个标签。
   - `need` 是所有空餐的 `context.settings.dishes_for(slot.meal)` 之和。`menu suggest` 调用一次 `context.random.sample(candidates, min(need, len(candidates)))`，不为别的事用 `context.random`。结果是 `chosen`。所以 `chosen` 里没有重复的菜谱，也没有这一周已经有的菜谱。种子相同、文件相同时，两次运行选出相同的菜谱，所以测试可以用 `main(random=Random(seed))`（3.4）固定选择，`Random(seed).sample` 给出一次运行选中的菜谱。
   - 空餐按顺序取菜，每餐从 `chosen` 剩下部分的最前面取。剩下的菜谱够 `dishes_for(meal)` 道时，这一餐取这么多道。否则它保持空着，后面的餐继续取（C 点）。所以菜谱太少时，这一周前面的空餐先得到菜，后面的保持空着。
   - 新的一道菜只写它的菜谱 ID，不写份数。所以 F06 的读取函数读它时，它得到 `settings.servings`，和你不写份数的菜一样（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。
   - 需求只禁止同一周里出现两次同一个菜谱。你清空的那道菜已经不在这一周里了，所以它又是候选，换菜时可能把它换回来（v0.2-S03）。`menu suggest` 无法知道一个空餐以前有什么菜。
   - 你写的周可能有重复的菜谱，比如示例的那一周有三次 `rice`。`menu suggest` 不改动有菜的餐，所以它保留这样的重复，也不增加新的重复。
7. **`menu suggest` 怎样修改文件。** ADR-0002 给 F14 留了两条路：只改写空餐的那几行，或者用一个能保留文件格式的库，比如 tomlkit。tomlkit 会是运行时的第三方包，违背 ADR-0001，还需要架构师批准（R16）。所以 `menu suggest` 用标准库修改文字的某些行（2.2）：
   - 它用 `read_file_text` 读文字，把每个 CR LF 变成 LF。新文件是 UTF-8，没有字节顺序标记，用 LF 换行，这是架构 5.1 对工具写出的每个文件的规定。所以用 CR LF 换行或带字节顺序标记保存的文件，每一行的文字都不变，只有换行符和这个标记会变。
   - 写在 `dinner = []` 这样一行上的一餐，把 `[]` 换成它的菜，比如 `dinner = ["mapo-tofu", "rice"]`。这一行的其余部分，包括注释，保持不变。
   - 某天的表里没写的一餐，在那天的 `[monday]` 那一行后面紧跟着得到新的一行。
   - 文件里没写的一天，在文件末尾得到它的表：一个空行、`[tuesday]` 那一行，以及这天得到菜的每一餐各一行。
   - 保持空着的一餐不会得到新的一行，一餐菜都没得到的一天也不会。
   - 其他每一行都保持它的文字和顺序，注释和空行也一样。新的一行会让它后面的行往下移。
   - 然后 `menu suggest` 用 `parse_toml`（3.6）检查新文字：它的表必须等于旧文字的表加上各餐的新菜。检查不通过时，`menu suggest` 什么都不写，给出 `CANNOT_FILL` 后停下，这条提示要求使用 `menu new` 写出的格式。所以这些规则改不了的文件，比如把某天写成花括号里的表 `monday = { dinner = [] }` 的文件，会被拒绝，但从不被弄坏。`menu new` 写出的文件和 `example-data.md` 的格式总能通过。你最可能遇到的被拒绝的格式，是你把某一餐的列表写成多行，后来删掉其中的菜把它清空，留下分在两行的 `dinner = [` 和 `]`，示例那一周的周日晚餐就会这样。它让 `menu suggest` 在 2.2 的第 8 步给出 `CANNOT_FILL` 后停下，这条提示要求写成 `dinner = []`。
8. **`menu suggest` 怎样保存文件。** 每个文件都由 `datafile` 写（架构 2、3 和 8）。`create_file` 拒绝已经存在的条目，所以 `menu suggest` 照原样用 `replace_file` 写文件，这是 F13 设计第 2 节为 F14 计划的。`replace_file` 写出 `menus/<week>.toml.tmp`，再一步把它移到菜单文件上。所以文件里要么是旧文字，要么是新文字，从不是一部分；失败或 Ctrl+C 会让旧文件保持原样（F13 设计 3.1）。`list_menu_weeks` 只列出以 `.toml` 结尾的名称，所以临时文件从不算作菜单（F06 设计 2.8）。`menu suggest` 只用 `context.folder.menu_file(str(week))` 拼出路径，而且是在 `list_menu_weeks` 给出这一周之后，所以名称总是 ISO 周（F03 设计 2.1）。`replace_file` 用 `folder.relative(path)` 检查路径，它比较的是路径的文字，所以 `root/menus/../../x.toml` 这样的路径能通过它的检查。`menu suggest` 从不拼出这样的路径。只有某一餐得到菜时，它才写文件。没有空餐的周，或者一餐都没填上的运行，不写文件，文件保持原来的字节和修改时间（v0.2-S03）。`menu suggest` 按结果处理：
   - **`CREATED`。** 它把选择 9 的输出写到输出流，并给出 0。
   - **`FAILED`。** 它在错误流上写出三行，并给出 1，输出流上什么也没有。第一行按问题里的样子写出文件，也就是相对于数据文件夹的路径，比如 `menus\2026-W48.toml`，这是架构 6 对问题的规定（D 点）。第二行是两个空格加上 `problem.text(context.lang)`，比如 `The file cannot be written: access is denied.`。第三行是 `CHANGED_NOTHING`；`replace_file` 没能删除临时文件时，第三行是带临时文件完整路径的 `LEFT_BEHIND`。菜单文件保持原来的字节。
9. **输出。** F14 原型的三段对第一次填、换菜和留下空餐的填写显示不同的行。这份设计让每一行出现在它有用的情况里，使三段原型按原样得出（2.2）：
   - 第一行说明填好了几个空餐，带 `--tag` 时也写出标签。运行之前已经有餐有菜时，这一行接着写 `KEPT`，就像中文原型“Swap one dish”显示的那样。
   - 每个空餐都得到它的菜时，后面接 `RUN_SHOW`。运行之前没有一餐有菜时，还接上 `NO_TWICE` 和 `SWAP_HINT`，就像“Fill an empty week”那样。只有这时 `NO_TWICE` 才一定对：你自己填过的周可能有重复的菜谱。`SWAP_HINT` 在第一次填之后告诉你怎样换菜，而“Swap one dish”这样的再次填写说明你已经知道了。
   - 有空餐保持空着时，第二行说明有几餐、为什么，后面什么也不接，就像“Not enough recipes”那样。每个候选都填进了某一餐时，原因是 `STAY_EMPTY`；还剩下候选、但剩下的每一餐都用不了时，原因是 `TOO_FEW`（C 点）。两者都有带标签的写法。
   - 没有空餐的周给出 `NO_EMPTY_MEAL`，然后是 `SWAP_HINT`，退出码 0，这是 v0.2-S03 的要求。
   - 因为没有候选而一餐都没填上的运行，给出留下空餐时的那两行，第一行是 `Filled 0 of`，退出码 0，不写文件。v0.2-S04、v0.2-S05 和 v0.2-S07 对留下空餐的填写要求退出码 0，因为数据里没有任何错误。
   - 输出写到输出流。拒绝执行和失败写到错误流，退出码 1（架构 6）。
10. **提示里的数字。** `suggest` 的提示显示菜单格子的计数（最多 21），以及用 `str(week)` 写出的周。标签作为它名称的 `BiText` 放进提示，`--tag` 的值作为你输入的文字放进提示。设置里错误的菜数得到一条不显示数字的提示（3.2）。文件里的问题只通过 `stop_at_error` 或选择 8 里失败时的各行写到错误流，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `suggest` 的提示不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。
11. **速度。** 没有性能指标写到 `menu suggest`。它读的是 `menu show` 读到菜单为止的东西，再读一次菜单文件，然后像 `list` 读每个菜谱那样，读这一周还没有的每个菜谱。在 v0.1.0 的发布测试里，`list` 在 PT01 文件夹上、在 Troy 的电脑上的中位数是 0.782 秒（v0.2 测试计划第 3 节）。所以 `menu suggest` 应该花差不多的时间，低于 1 秒。这是估计，不是测量结果。对新文字的检查多解析一段几 KB 的文字。v0.2-S16 在 PT01 文件夹上运行 `menu suggest`，但不计时。其他每个命令的启动变化很小：`cli` 引用 `random`，并创建一个从系统取得种子的 `Random()`。在 Troy 的电脑上，`python -X importtime` 测得在 `recipe_menu.cli` 之后 `import random` 耗时 1.7 到 2.1 毫秒，远低于每个 PT01 用例的余量，而且 v0.1 的 PT01 用例会在 v0.2 的发布测试里再运行一次。
12. **只导出这个命令。** `suggest` 导出 `MENU_SUGGEST_COMMAND`，别的什么都不导出。只有 `cli` 能引用 `suggest`（架构 3），所以别的名称不会有使用者。F14 不从 `menu` 取任何东西，`menu` 只导出它的两个命令（F11 设计，选择 12）。`suggest` 自己保存 `WEEK_ARGUMENT` 和 `CHANGED_NOTHING`，文字和 `menu` 的相同，和 `shop` 的做法一样（F13 设计，选择 3），也自己保存 `UNKNOWN_TAG` 和 `NO_TAGS`，文字和 `list` 的相同（选择 4）。以后的 `[refactor]` PR 可以让它们共用。

运行 `menu suggest` 的 v0.2 场景，在这些选择下都成立：

- v0.2-S01：第 2 步打印 F14“Fill an empty week”的第二段输出：14 餐都得到一道菜，运行之前没有一餐有菜（选择 9）。只有每一餐的 `[]` 会变，所以文件的其余部分保持 `menu new` 写出的样子（选择 7）。第 3 步和第 4 步读这个文件时没有问题。
- v0.2-S02：输出用所选语言写出标签，所以 `--tag 快手` 给出和 `--tag quick` 相同的输出（选择 4）。每次运行都从 `cli` 得到自己的生成器，所以两个文件几乎总是不同。
- v0.2-S03：第 2 步用中文打印 F14“Swap one dish”的输出：填好 1 餐，保留 13 餐。第 3 步打印 `2026-W48 has no empty meal. Nothing was changed.` 和换菜的那一行，以 0 退出，不写文件（选择 8 和 9）。
- v0.2-S04：第 2 步打印 F14“Not enough recipes”的输出：带标签辣的 3 个菜谱填进前 3 餐，11 餐保持空着（选择 6 和 9）。
- v0.2-S05：第 1 步打印 `Filled 1 of 10 empty meals of 2026-W47. Kept the 4 meals that already have dishes.` 和 `9 meals stay empty: no other recipe is left.`，并以 0 退出。`red-braised-pork` 填进第一个空餐，也就是周一午餐。只有那一行会变。
- v0.2-S06：有 `dishes = { dinner = 2 }` 时，第 2 步用 28 道菜填满 21 餐，并打印第一次填时的四行（选择 5 和 9）。
- v0.2-S07：第 2 步打印 `Filled 7 of 14 empty meals of <N>.` 和 `7 meals stay empty: no other recipe is left.`，并以 0 退出。第 3 步打印 `<T>` 的 `NO_MENU`，并以 1 退出。
- v0.2-S08：第 1 到 4 步分别打印带退出码 2 的 `NOT_A_WEEK`、`NO_MENU`、`UNKNOWN_TAG`，以及“A menu with a mistake”的三行，后三者退出码都是 1，都不写文件（选择 2 到 4）。
- v0.2-S14：第 4 步打印 `cli` 的 `NO_DATA_FOLDER` 和 `RUN_INIT`（选择 1）。第 1 步和第 2 步的帮助在 `menu show` 那一行后面多了 `menu suggest` 那一行，两张表的每一行都往右移 3 列（2.1）。所以测试经理按 v0.2 测试计划第 2 节的规定，更新 v0.2-S14 要求的帮助。
- v0.2-S15：第 1 步只改动 `menus\2026-W48.toml`，`replace_file` 不留下临时文件（选择 8）。`replace_file` 的移动还会让文件夹 `menus\` 得到新的修改时间，就像 v0.1-S23 里 `shop` 让 `shopping\` 得到新的修改时间一样。所以第 1 步的“唯一字节或时间有变化的文件”只算文件，不算文件夹。
- v0.2-S16：第 1 步读 1,000 个菜谱，用 21 个不同的菜谱填满 2026-W53 的 21 餐（选择 3 和 6）。

这四点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 没有原型完整展示这些文字。每一段都沿用 F14 原型某一行或某条已有提示的措辞。建议按 2.2 和 3.2 的写法接受它们。共 19 条提示：
  - 原型里英文各行对应的中文：`已为 2026-W48 填好 14 个空餐，用的都是带有标签“快手”的菜谱。`、`这一周里没有重复的菜谱。`、`要换掉一道菜，就在 menus\2026-W48.toml 里清空它那一餐，然后再运行“recipe-menu menu suggest 2026-W48”。`、`已为 2026-W49 填好 14 个空餐中的 3 个，用的都是带有标签“辣”的菜谱。` 和 `11 餐仍是空的：没有别的菜谱带有标签“辣”。`。
  - 原型里中文那一行对应的英文：`Filled 1 empty meal of 2026-W48. Kept the 13 meals that already have dishes.`。
  - 不带 `--tag`、留下空餐的填写：`Filled 1 of 10 empty meals of 2026-W47.` 和 `9 meals stay empty: no other recipe is left.`，以及 `已为 2026-W47 填好 10 个空餐中的 1 个。` 和 `9 餐仍是空的：没有别的菜谱可选了。`。
  - 还剩下候选时保持空着的餐（C 点）：`4 meals stay empty: too few other recipes are left.` 和 `4 餐仍是空的：剩下的菜谱不够了。`，以及带标签的写法，比如 `… too few other recipes have the tag "spicy".` 和 `……带有标签“辣”的别的菜谱不够了。`。
  - 没有空餐的周：`2026-W48 has no empty meal. Nothing was changed.` 和 `2026-W48 没有空餐。没有做任何修改。`，后面是换菜的那一行。
  - `menu suggest` 无法填写的文件 `CANNOT_FILL`，以及保存失败、临时文件留下时的 `LEFT_BEHIND`，两种语言都有。
  - 帮助里的那一行：`Fill the empty meals of a week menu.` 和 `给一个周菜单的空餐填上菜。`。
  - 设置 `dishes` 的位置和问题：`dishes` 和 `菜数`，`dishes of dinner` 和 `晚餐的菜数`，`"dishes" must be a table in braces, such as dishes = { dinner = 2 }.`，以及 `The number of dishes must be a whole number from 1 to 10, such as 2.`，每条都有两种语言。
  - 一餐时的英文写法，比如 `Kept the 1 meal that already has dishes.` 和 `1 meal stays empty: no other recipe is left.`。
- **B. 一餐菜数的设置**（选择 5）。
  - 做法 1，推荐：一个键 `dishes`，它是一张表，为需要的每一餐写一个 1 到 10 之间的数，比如 `dishes = { dinner = 2 }`，或者在文件末尾写 `[dishes]` 和 `dinner = 2` 两行。表里没写的一餐得到 1。`init` 写出的设置文件仍然没有这个键。
  - 做法 2：每一餐一个键，`breakfast_dishes`、`lunch_dishes` 和 `dinner_dishes`，每个都是 1 到 10 之间的数。选择 5、3.1、3.2 和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：这张表用你已经在 `meals` 里写的那些词称呼各餐，设置文件只多一个键，而不是三个。
- **C. 需要的菜数比剩下的菜谱还多的一餐**（选择 6），比如只剩 1 个菜谱时要 2 道菜的晚餐。
  - 做法 1，推荐：这一餐保持空着，后面需要的菜数不超过剩下菜谱数的餐照样得到菜。每个填好的餐都有设置规定的菜数。说明保持空着的餐的那一行写的是剩下的别的菜谱不够了（`TOO_FEW`）。
  - 做法 2：这一餐得到剩下的菜谱，后面的每一餐都保持空着。选择 6、选择 9 和 2.2 的示例在 mock PR 之前修改。这时输出还需要一行写出菜数不够的那一餐，否则在每一餐都得到菜的填写里看不出来。
  - 推荐做法 1 的理由：`menu suggest` 只填空餐。所以它留空的一餐，在你加了菜谱或换了标签之后，能在以后的运行里得到全部的菜；而菜数不够的一餐已经不是空的了，以后的运行不会给它补上。需求里“每个空餐得到设置里规定的菜数”这条规则，也只有在做法 1 下才成立。
- **D. `menu suggest` 怎样写出它的菜单文件**（选择 8 和 9）。原型里的那一行 `To swap a dish, empty its meal in menus\2026-W48.toml, …` 用相对于数据文件夹的路径写出文件。架构 6 规定问题这样写出它的文件，其他提示用完整路径写出文件。ADR-0009 和 ADR-0010 允许 `menu new` 和 `shop` 用完整路径写出它们没能写成的文件，而 ADR-0009 第 5 节要求以后的每一种写入都对架构 6 做它自己的修改。所以换菜的那一行（它不是问题）需要决定，保存失败时的第一行也需要决定。
  - 做法 1，推荐：换菜的那一行像原型那样写出文件 `menus\2026-W48.toml`，用系统的分隔符。保存失败时按问题里的样子同样写出文件，比如在 `  The file cannot be written: access is denied.` 上面写出 `menus\2026-W48.toml`，架构 6 已经允许问题这样写。架构 6 为换菜的那一行加一句话。架构师在 F14 的 mock PR 之前，用一个 `[docs]` PR 把它记进架构 6 和一份 ADR，就像 ADR-0010 记下 F11 设计的 C 点那样。
  - 做法 2：两行都写出完整路径，比如 `C:\Users\Troy\recipe-menu\menus\2026-W48.toml`，就像 `menu new` 和 `shop` 写出它们的文件那样。F14 原型里换菜的那一行通过需求变更流程修改，架构 6 加上 `menu suggest` 保存失败的情况，两者都在 F14 的测试计划之前完成。选择 8 和 9、2.2 和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：它保留了 Troy 批准的原型里的那一行，`menu suggest` 在讲这个文件的每一行里都用同一种写法。数据文件夹是你每天用的那个，这正是架构 6 让问题用相对于它的路径写出文件的原因。
  - 两种做法下，`LEFT_BEHIND` 都用完整路径写出临时文件，这是架构 6 对不是问题的提示的规定，`shop` 也这样做。

这些后续功能会在 F14 的基础上构建。细节由它们自己的设计决定。

- F15 的 `add` 不从 `suggest` 取任何东西。它按 F14 加生成器的方式，给 `Context` 和 `main` 加上输入流：一个带默认值的字段和一个可选参数，所以没有调用会失效（第 3 节）。
- F16 的 `edit` 给 `Settings` 和 `read_settings` 加上键 `editor`。这时设置的 `UNKNOWN_KEY` 的文字列出五个键，所以 F16 的设计要像这里的第 3 节一样，列出比较这段文字的测试。

troy-mode 的流程有一个 mock PR 和一个实现 PR。`COMMANDS` 里的这一项改变了帮助和 `recipe-menu menu` 的那一行，键 `dishes` 改变了设置的 `UNKNOWN_KEY` 的文字。所以 F05、F11 和 F13 的六个测试要改（第 3 节）。开发工程师从不修改测试（R08），已验收功能的每个测试都必须通过（R10）。所以在 F14 的 mock PR 之前，一个修测试的 PR 修改 F11-T32、F13-T01、F13-T22 和 F13-T27（mock 的这一项会让它们失败），让每个测试有没有 `menu suggest` 那一行都成立。F05-T10 和 F05-T11 只有在实现让 `read_settings` 认识键 `dishes` 时才会失败。它们在同一个修测试的 PR 里修改，或者在 F14 的测试 PR 里修改，让它们在两种键列表下都成立。测试计划列出这六个测试，以及修改它们的 PR。

mock（PR 3）包含 `src/recipe_menu/commands/suggest/__init__.py`、`messages.py`、放 `run` 的一个内部文件（比如 `_run.py`），以及 `src/recipe_menu/cli/_commands.py` 里的那一项。它给 `Settings` 加上带默认值的字段 `dishes` 和方法 `dishes_for`，但不带 3.1 的检查，并把 3.2 的提示加进 `src/recipe_menu/settings/messages.py`。它让 `read_settings` 保持原样，所以 `dishes` 仍然是未知的键，F05-T10 和 F05-T11 仍然通过。它给 `Context` 加上带默认值的字段 `random`，给 `main` 加上参数 `random`，但 mock 不把它传下去，所以上下文得到默认值。它把 `read_file_text` 和 `parse_toml` 加进 `datafile` 的 `_toml.py` 或一个新的内部文件，以及 `src/recipe_menu/datafile/__init__.py`。它定义每条提示和字段齐全的 `MENU_SUGGEST_COMMAND`。它的 `run` 不读文件、不写任何东西、不抛异常，并给出 0。它的 `dishes_for` 给出 1，`read_file_text` 给出空文字，`parse_toml` 给出 `None`。所以检查以下内容的新测试在 mock 上会失败（R09）：输出的某一行、退出码 1、带退出码 2 的 `NOT_A_WEEK`、改过的文件的字节、拒绝执行、失败及其各行、多于一道菜的那一餐的 `dishes_for`、键 `dishes` 的问题、`Settings` 的检查、`main` 传下去的生成器，或者 `read_file_text` 和 `parse_toml` 给出的结果。这些测试在 mock 上会通过，从而违反 R09：只检查 `MENU_SUGGEST_COMMAND` 的字段、帮助、某条提示、退出码 0、`Settings` 的默认值和相等性，或者 `Context.random` 的默认值的测试。检查 `cli` 在运行 `menu suggest` 之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、两个周、未知选项，或者 `--tag` 没有值。只检查一次运行没有改动任何文件的测试也是如此，比如没有空餐的周、`NO_MENU`、未知的标签或错误。每个这样的测试都还要检查 mock 做错的内容，比如输出或文件。按估计，mock 改动约 10 个文件，约 350 行，文件数超过 R03 的 5 个，所以它的说明要写明软限制的理由。理由是测试既直接用到设置、上下文和 `datafile` 的两个函数，也通过 `menu suggest` 用到它们，所以它们要在同一个阶段一起带上，和 F08、F11、F13 的 mock 一样。

实现（PR 5）把带读取、选择、文字修改和输出的 `run` 放在 `suggest` 的内部文件里，比如 `_run.py`、`_choose.py`、`_edit.py` 和 `_output.py`。它还包含 `settings` 里对 `dishes` 的读取、`Settings` 的检查、`main` 里的生成器，以及 `datafile` 的两个函数。按估计，它改动约 9 个文件，约 700 行，超过 R03 的限制，所以它的说明也要写明软限制的理由：`menu suggest` 的测试同时需要这些部分。开发工程师要早一点运行 troy-check。

### 2.1 `MENU_SUGGEST_COMMAND`

- 模块：suggest
- 功能：对 `menu suggest` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 填满这一周菜单文件的空餐，并写出 2.2 的输出。

签名：

```python
MENU_SUGGEST_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "suggest")
#   help_line = MENU_SUGGEST_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ("--tag",)
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 组成的元组 | `("menu", "suggest")`。 | 无 |
| `help_line` | `Message` | `MENU_SUGGEST_HELP`：“Fill the empty meals of a week menu.”和“给一个周菜单的空餐填上菜。”。 | 没有占位符。 |
| `run` | 接受一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 把参数变成周，读选择 3 的文件，选出菜谱，通过 `replace_file` 修改菜单文件，并写出 2.2 的输出。 | 给出 0 或 1。值不是周时抛出 `UsageError`，而且在访问磁盘、写出任何输出之前抛出。遇到坏数据或磁盘上的失败时不抛异常。 |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`，可选，不能重复。`WEEK_ARGUMENT` 是 `WEEK` 和 `周`，和 F11、F13 的一样。 | 所以 `cli` 不传值或传一个值（F05 设计 2.5）。 |
| `options` | `str` 组成的元组 | `("--tag",)`，要从中选择的菜谱的标签（选择 4）。 | 只有值不为空、不以 `--` 开头时，`cli` 才传它，而且最多一次（F05 设计 2.10）。 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `menu suggest`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4），加上 3.3 的字段 `random`。 | `run` 使用 `context.lang`、`context.folder`、`context.settings`（用于各餐、每餐的菜数和 `read_week_menu`）、`context.out`、`context.err`、`context.today` 和 `context.random`。 |
| `arguments` | `Arguments` | 命令行给 `menu suggest` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `()`，或者有一个值，比如 `("next",)`。`arguments.option("--tag")` 是 `--tag` 的值，或者 `None`。 |

- 返回值：`MENU_SUGGEST_COMMAND`，一个 `Command`。
  - `MENU_SUGGEST_COMMAND.usage` 的英文是 `menu suggest [WEEK]`，中文是 `menu suggest [周]`。所以帮助显示它们，用法错误引用 `recipe-menu menu suggest [WEEK]` 或 `recipe-menu menu suggest [周]`。
  - `MENU_SUGGEST_COMMAND.run(context, arguments)` 执行 2.2 的步骤，用 `context.lang` 写出各行，并给出 0 或 1。

F14 之后，帮助列出下面这些命令和选项，第二列从第 24 列之后开始（选择 1）。帮助的其他各行就是 F05 原型里的那些行。英文：

```text
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
```

中文：

```text
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
```

错误：

`run` 在访问磁盘之前把参数变成周。

| 错误 | 何时发生 |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | `week_from_argument` 对 `WEEK` 的值给出 `None`（选择 2）。 |

- 副作用：2.2 的那些副作用。`run` 通过 F03、F04 和 F06 的读取函数以及 `read_file_text`，读取目录、两个列表、这一周的菜单文件（读两次）以及这一周还没有的菜谱。某一餐得到菜时，它通过 `replace_file` 修改菜单文件，并写入 `context.out` 或 `context.err`。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，里面有七个菜谱；`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文只把晚餐当作一餐，并带有 `Random(7)`，所以这次运行用这七个菜谱，按 `Random(7).sample` 给出的顺序，填满一个新周的七个晚餐（选择 6）。帮助来自 `COMMANDS`，F14 之后它有九个命令。抛出异常的那次调用不碰任何文件，也不往任何一个流写一行。

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.app import Argument, Arguments, Context, FolderUse, UsageError
from recipe_menu.cli import main
from recipe_menu.commands.suggest import MENU_SUGGEST_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

assert MENU_SUGGEST_COMMAND.words == ("menu", "suggest")
assert MENU_SUGGEST_COMMAND.usage == BiText("menu suggest [WEEK]", "menu suggest [周]")
assert MENU_SUGGEST_COMMAND.help_line.render(Lang.EN) == "Fill the empty meals of a week menu."
assert MENU_SUGGEST_COMMAND.help_line.render(Lang.ZH) == "给一个周菜单的空餐填上菜。"
assert MENU_SUGGEST_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_SUGGEST_COMMAND.options == ("--tag",)
assert MENU_SUGGEST_COMMAND.folder is FolderUse.READ

dinner_only = Settings(Lang.EN, (Meal.DINNER,), 2)
file = folder.menu_file("2026-W48")
text = 'week = "2026-W48"\n' + "".join(f"\n[{day.value}]\ndinner = []\n" for day in Day)
file.write_text(text, encoding="utf-8")
out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, dinner_only, out, err, date(2026, 11, 10), Random(7))
assert MENU_SUGGEST_COMMAND.run(context, Arguments(("2026-W48",))) == 0
relative = Path("menus", "2026-W48.toml")
again = 'then run "recipe-menu menu suggest 2026-W48" again.'
assert out.getvalue().splitlines() == [
    "Filled 7 empty meals of 2026-W48.",
    "No recipe appears twice in the week.",
    'Run "recipe-menu menu show 2026-W48" to see the week.',
    f"To swap a dish, empty its meal in {relative}, {again}",
]
assert err.getvalue() == ""

ids, _ = list_recipe_ids(folder)
picks = Random(7).sample(ids, 7)
menu, problems = read_week_menu(folder, IsoWeek(2026, 48), dinner_only, frozenset(ids))
assert problems == ()
assert menu is not None
assert [slot.dishes for slot in menu.slots] == [(Dish(pick, 2),) for pick in picks]
lines = file.read_text(encoding="utf-8").splitlines()
assert lines[0] == 'week = "2026-W48"'
assert [line for line in lines if line.startswith("dinner")] == [
    f'dinner = ["{pick}"]' for pick in picks
]


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
assert len(english) == 22
assert english[11:14] == [
    "  menu show [WEEK]      Show a week menu.",
    "  menu suggest [WEEK]   Fill the empty meals of a week menu.",
    "  shop [WEEK]           Make the shopping list of a week menu.",
]
assert english[16].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[12] == "  menu suggest [周]     给一个周菜单的空餐填上菜。"

MENU_SUGGEST_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu menu suggest`

- 模块：suggest
- 功能：用随机选出的菜谱填满一周菜单文件里的每个空餐、同一周里不出现两次同一个菜谱，并让已经填好的餐和文件的其余部分保持原样的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 和 [4](../../requirements.zh-CN.md#4-功能点)）。F14 原型“Fill an empty week”“Swap one dish”和“Not enough recipes”展示了它。

签名：

```text
recipe-menu menu suggest [WEEK] [--tag TAG] [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `WEEK` | 文字 | 菜单的周：`2026-W48` 这样的 ISO 周、`this` 或 `next`。 | 可选。不写时为本周。其他文字是用法错误（选择 2）。 |
| `--tag` | 标签的名称 | 只从带这个标签的菜谱里选。 | 目录里某个标签的名称，两种语言都行，按 `Catalog.find_tag` 的方式匹配（选择 4）。不能为空，最多写一次（F05 设计 2.10）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。它不改变文件。 | 按 F05 设计 2.10 的规定。不写这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10 的规定。不写这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `menu suggest`。 | 无 |

`menu suggest` 按顺序执行这些步骤。`path` 是 `context.folder.menu_file(str(week))`。每个读文件的步骤都使用前面步骤给出的东西，每个发现错误的步骤都会让命令停下（选择 3）。

1. 它用 `week_from_argument(value, context.today)` 把 `WEEK` 的值变成周。`value` 是参数的值，命令行没有给出时是 `None`。结果是 `None` 时，它抛出 `UsageError(NOT_A_WEEK, None, week=value)`（选择 2）。
2. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`menu suggest` 对第一个错误给出 `stop_at_error(context, error)`。
3. 带 `--tag` 时，`catalog.find_tag(value)` 给出 `tag`。它给出 `None` 时，`menu suggest` 把按目录里标签个数选出的 `UNKNOWN_TAG`（目录里没有标签时是 `NO_TAGS`）写到错误流，并给出 1（选择 4）。
4. `list_recipe_ids(context.folder)` 给出 `ids` 和它们的问题（F04 设计 2.5）。问题里有错误时，`menu suggest` 用 `stop_at_error` 在第一个错误处停下。
5. `list_menu_weeks(context.folder)` 给出 `weeks` 和它们的问题（F06 设计 2.8）。问题里有错误时，`menu suggest` 用 `stop_at_error` 在第一个错误处停下。`weeks` 里没有这一周时，它把带 `week=str(week)` 的 `NO_MENU` 写到错误流，并给出 1。
6. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` 给出 `menu` 和它的问题（F06 设计 2.9）。问题里有错误时，`menu suggest` 用 `stop_at_error` 在第一个错误处停下。
7. 空餐是 `menu` 里没有菜的格子，其余的是保留的餐（选择 6）。没有空餐时，`menu suggest` 把 `NO_EMPTY_MEAL` 和 `SWAP_HINT` 写到输出流，并给出 0。
8. `read_file_text(context.folder, path)` 给出文字（3.5）。它给出 `Problem` 时，`menu suggest` 给出 `stop_at_error(context, problem)`。它把文字里的每个 CR LF 变成 LF，再按下面的规则找到每个空餐的位置。某个空餐没有位置时，它把 `CANNOT_FILL` 的三行写到错误流，并给出 1。
9. 对 `ids` 里 `menu` 的菜都没写到的每个 ID，按 `ids` 的顺序，`read_recipe(context.folder, catalog, recipe_id)` 给出菜谱和它的问题（F04 设计 2.6）。问题里有错误时，`menu suggest` 用 `stop_at_error` 在第一个错误处停下。
10. 它调用一次 `context.random.sample` 选出菜谱，并按顺序分给各个空餐（选择 6）。
11. 没有一餐得到菜时，它把下面的输出写到输出流，并给出 0。它不写文件。
12. 它按下面的规则拼出新文字，并检查它。检查不通过时，它把 `CANNOT_FILL` 的三行写到错误流，并给出 1。
13. 它调用一次 `replace_file(context.folder, path, new_text)`（F13 设计 3.1）。结果是 `FAILED` 时，它把失败时的三行写到错误流，并给出 1（选择 8）。结果是 `CREATED` 时，它把下面的输出写到输出流，并给出 0。

第 2、4 和 9 步的警告不改变任何东西（选择 3）。

**文字怎样修改。** `text` 是第 8 步给出的文字，其中每个 CR LF 都已变成 LF。一行是 `text` 里两个 LF 之间、第一个 LF 之前或最后一个 LF 之后的一段。下面的 `D` 是一个 `Day` 的值，比如 `monday`，`M` 是一个 `Meal` 的值，比如 `dinner`。在式样里，D 和 M 可以不加引号，也可以放在双引号或单引号里，比如 `"dinner"`。式样里的一个空格代表任意个空格和制表符，也可以没有，式样末尾还可以有一段注释，也就是 `#` 和任意文字。

| 行的种类 | 这一行 | 例子 |
| --- | --- | --- |
| 表头 | 它第一个不是空格或制表符的字符是 `[`。 | `[monday]` |
| 某天 D 的表头 | ` [ D ] ` | `[monday]`、`[ 'sunday' ]  # guests` |
| 某餐 M 的一行 | 它以 ` M =` 开头。 | `dinner = ["rice"]`、`dinner = [` |
| 某餐 M 的空行 | ` M = [ ] ` | `dinner = []`、`dinner = [ ]  # nothing yet` |

某天的表是它的表头后面、到下一个表头或文字末尾为止的那些行。对每个空餐，`menu suggest` 按下表第一个适用的行找到它的位置。它在第 8 步为每个空餐找位置，也包括将会保持空着的那些。

| 文字 | 这一餐的位置 | 这一餐得到菜时 |
| --- | --- | --- |
| 那天的表里正好有一行是这一餐的，而且它是这一餐的空行。 | 那一行。 | `[`、`]` 和它们之间的空格换成菜的列表。`[` 前面和 `]` 后面的文字，包括注释，保持不变。 |
| 文字里有那天的表头，它的表里没有这一餐的行。 | 紧跟在那天的表头后面。 | 新的一行：M、` = ` 和列表。同一天的几行新行按设置里各餐的顺序跟在表头后面。 |
| 文字里没有那天的表头。 | 文字的末尾。 | 那天的表：一个空行、`[D]`，以及那天得到菜的每一餐，按设置里各餐的顺序，各一行 M、` = ` 和列表。几张新表按一周的顺序一张接一张。文字不为空、又不以 LF 结尾时，先加一个 LF。 |
| 其他任何文字，比如那天的表里这一餐的那一行不是空行，像 `dinner = [` 后面一行才是 `]` 那样。 | 无。 | `menu suggest` 在第 8 步给出 `CANNOT_FILL` 后停下。 |

菜的列表是 `[`、按 `chosen` 的顺序放在双引号里、用 `, ` 隔开的这一餐的菜谱 ID，以及 `]`，比如 `["mapo-tofu", "rice"]`。菜谱 ID 只含有小写字母、数字和 `-`（F04 设计 2.4），所以不需要转义。保持空着的一餐不会得到新行，它原来的那一行保持原样；一餐菜都没得到的一天不会得到表。

**对新文字的检查。** `old` 是 `parse_toml(text)`，`new` 是新文字的 `parse_toml`（3.6）。检查通过的条件是：两者都不是 `None`，而且 `new` 等于这样的 `old`：对每个得到菜的餐，那天的表里键 M 的值是它的 ID 列表；`old` 没有那天的表时，那天的表是一张新表。把某天写成花括号里的表 `monday = { dinner = [] }`，或者用点号键写成 `monday.dinner = []` 的文件，那天没有表头。所以它的表会放到文字末尾，这天就定义了两次，检查不通过。式样读不懂的表头或键，比如带转义的，也是如此。所以 `menu suggest` 写出的每个文件读起来都是旧文件加上新菜，规则没改的每一行都保持它的文字和顺序。

- 返回值：退出码，以及写在相应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `replace_file` 给出 `CREATED`，或者没有一餐得到菜，或者这一周没有空餐。 | 输出流：下面的各行。 |
| 1 | 标签未知、这一周没有菜单文件、某个文件有错误、`menu suggest` 无法填写这个文件，或者 `replace_file` 给出 `FAILED`。 | 错误流：`UNKNOWN_TAG` 或 `NO_TAGS`、`NO_MENU`、`stop_at_error` 的三行、`CANNOT_FILL` 的三行，或者失败时的三行。输出流上什么也没有。 |
| 2 | `WEEK` 的值不是周。 | 错误流：`cli` 写出的 `NOT_A_WEEK`，不带下一行。输出流上什么也没有。 |

输出是下面这些行，每行以换行结束。`empty` 是空餐的个数，`filled` 是得到菜的空餐的个数，`kept` 是保留的餐的个数（选择 9）。

| 情况 | 各行，按顺序 |
| --- | --- |
| `filled` 等于 `empty`，`kept` 是 0 | 1. `FILLED`，带 `--tag` 时是 `FILLED_WITH_TAG`，`count` 为 `filled`。2. `NO_TWICE`。3. `RUN_SHOW`。4. `SWAP_HINT`。 |
| `filled` 等于 `empty`，`kept` 大于 0 | 1. `WITH_KEPT`，`first` 为上一种情况的那一行，`kept` 为 `count` 为 `kept` 的 `KEPT`。2. `RUN_SHOW`。 |
| `filled` 小于 `empty`，`kept` 是 0 | 1. `FILLED_SOME`，带 `--tag` 时是 `FILLED_SOME_WITH_TAG`，`count` 为 `empty`。2. 原因，`count` 为 `empty - filled`：每个候选都填进了某一餐时是 `STAY_EMPTY`，还剩下候选时是 `TOO_FEW`，带 `--tag` 时各用带标签的写法。 |
| `filled` 小于 `empty`，`kept` 大于 0 | 1. `WITH_KEPT`，`first` 为上一种情况的那一行，`kept` 为 `KEPT`。2. 原因，同上。 |
| 这一周没有空餐（第 7 步） | 1. `NO_EMPTY_MEAL`。2. `SWAP_HINT`。 |

`CANNOT_FILL` 的拒绝是三行：`Problem.error(context.folder.relative(path), None, CANNOT_FILL)` 的 `problem_lines`（F05 设计 2.8），它的第一行是不带位置的文件，比如 `menus\2026-W49.toml`，然后是两个空格加上提示，然后是 `CHANGED_NOTHING`。保存失败是选择 8 的三行。

`menu suggest` 的提示如下。`FILLED`、`FILLED_WITH_TAG`、`FILLED_SOME`、`FILLED_SOME_WITH_TAG`、`KEPT`、`STAY_EMPTY`、`STAY_EMPTY_WITH_TAG`、`TOO_FEW`、`TOO_FEW_WITH_TAG` 和 `UNKNOWN_TAG` 是 `Plural` 值（F02 设计 2.4），各按自己的 `count` 选择，`UNKNOWN_TAG` 按目录里标签的个数选择。“多个”的写法用于 1 以外的每个计数，两种写法的中文相同。`menu suggest` 还使用 `menus` 的 `NOT_A_WEEK` 和 `NO_MENU`。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `MENU_SUGGEST_HELP` | `Fill the empty meals of a week menu.` | `给一个周菜单的空餐填上菜。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `FILLED`，一个 | `Filled {count} empty meal of {week}.` | `已为 {week} 填好 {count} 个空餐。` |
| `FILLED`，多个 | `Filled {count} empty meals of {week}.` | `已为 {week} 填好 {count} 个空餐。` |
| `FILLED_WITH_TAG`，一个 | `Filled {count} empty meal of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_WITH_TAG`，多个 | `Filled {count} empty meals of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_SOME`，一个 | `Filled {filled} of {count} empty meal of {week}.` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个。` |
| `FILLED_SOME`，多个 | `Filled {filled} of {count} empty meals of {week}.` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个。` |
| `FILLED_SOME_WITH_TAG`，一个 | `Filled {filled} of {count} empty meal of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_SOME_WITH_TAG`，多个 | `Filled {filled} of {count} empty meals of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。` |
| `KEPT`，一个 | `Kept the {count} meal that already has dishes.` | `保留了已经有菜的 {count} 餐。` |
| `KEPT`，多个 | `Kept the {count} meals that already have dishes.` | `保留了已经有菜的 {count} 餐。` |
| `WITH_KEPT` | `{first} {kept}` | `{first}{kept}` |
| `NO_TWICE` | `No recipe appears twice in the week.` | `这一周里没有重复的菜谱。` |
| `RUN_SHOW` | `Run "recipe-menu menu show {week}" to see the week.` | `运行“recipe-menu menu show {week}”查看这一周。` |
| `SWAP_HINT` | `To swap a dish, empty its meal in {file}, then run "recipe-menu menu suggest {week}" again.` | `要换掉一道菜，就在 {file} 里清空它那一餐，然后再运行“recipe-menu menu suggest {week}”。` |
| `STAY_EMPTY`，一个 | `{count} meal stays empty: no other recipe is left.` | `{count} 餐仍是空的：没有别的菜谱可选了。` |
| `STAY_EMPTY`，多个 | `{count} meals stay empty: no other recipe is left.` | `{count} 餐仍是空的：没有别的菜谱可选了。` |
| `STAY_EMPTY_WITH_TAG`，一个 | `{count} meal stays empty: no other recipe has the tag "{tag}".` | `{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。` |
| `STAY_EMPTY_WITH_TAG`，多个 | `{count} meals stay empty: no other recipe has the tag "{tag}".` | `{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。` |
| `TOO_FEW`，一个 | `{count} meal stays empty: too few other recipes are left.` | `{count} 餐仍是空的：剩下的菜谱不够了。` |
| `TOO_FEW`，多个 | `{count} meals stay empty: too few other recipes are left.` | `{count} 餐仍是空的：剩下的菜谱不够了。` |
| `TOO_FEW_WITH_TAG`，一个 | `{count} meal stays empty: too few other recipes have the tag "{tag}".` | `{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。` |
| `TOO_FEW_WITH_TAG`，多个 | `{count} meals stay empty: too few other recipes have the tag "{tag}".` | `{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。` |
| `NO_EMPTY_MEAL` | `{week} has no empty meal. Nothing was changed.` | `{week} 没有空餐。没有做任何修改。` |
| `CANNOT_FILL` | `menu suggest cannot fill this file: write each day as a line such as [monday], and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.` | `menu suggest 无法填写这个文件：请把每一天写成 [monday] 这样的一行，把每个空餐写成 dinner = [] 这样的一行，和“recipe-menu menu new”写的一样。` |
| `CHANGED_NOTHING` | `Nothing was changed.` | `没有做任何修改。` |
| `LEFT_BEHIND` | `Nothing was changed, but menu suggest could not remove {file}. Delete it.` | `没有做任何修改，但 menu suggest 没能删除 {file}。请删除它。` |
| `UNKNOWN_TAG`，一个标签 | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`，多个标签 | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `week` | `str(week)`，比如 `2026-W48`。 |
| `count` | 选择每个 `Plural` 的那个数，按输出那张表的规定。 |
| `filled` | 得到菜的空餐的个数。 |
| `tag` | `find_tag` 给出的标签的名称，作为它的 `BiText`，所以每种语言显示它自己的名称：`--tag 快手` 时是 `quick` 和 `快手`。 |
| `first` | 输出的第一行去掉 `KEPT` 的部分，作为 `BiText`。 |
| `kept` | 按保留的餐的个数选出、`count` 为这个数的 `KEPT`，作为 `BiText`。 |
| `file` | 在 `SWAP_HINT` 里是 `str(context.folder.relative(path))`，在 Windows 上比如 `menus\2026-W48.toml`（D 点）。在 `LEFT_BEHIND` 里是 `str(creation.left[0])`，也就是临时文件的完整路径，比如 `C:\Users\Troy\recipe-menu\menus\2026-W48.toml.tmp`。 |
| `value` | 你输入的 `--tag` 的值。 |
| `tags` | 目录里各个标签名称的 `and_list`，每个作为它的 `BiText`，按目录的顺序，和 `list` 一样（F09 设计 2.2）。 |

用这些提示，就得出 F14 原型里的各行，比如 `Filled 14 empty meals of 2026-W48 with recipes that have the tag "quick".`、`已为 2026-W48 填好 1 个空餐。保留了已经有菜的 13 餐。` 和 `11 meals stay empty: no other recipe has the tag "spicy".`。

错误：

`cli` 在运行 `menu suggest` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，带 `NOT_A_WEEK`，不带下一行：`"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `WEEK` 的值不是周（第 1 步）。 |
| 退出码 1，错误流上是 `UNKNOWN_TAG` 或 `NO_TAGS`，比如 `Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.` | 目录里没有名为 `--tag` 的值的标签（第 3 步）。 |
| 退出码 1，错误流上是 `NO_MENU`：`There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | `menus/` 的列表里没有这一周的文件（第 5 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行，比如 `menus\2026-W47.toml, Monday dinner`、`  Unknown recipe "tomato-eggs".` 和 `RUN_CHECK` | 目录、某个列表、这一周的菜单文件、它的文字，或者这一周还没有的某个菜谱有错误（第 2、4 到 6、8 和 9 步）。 |
| 退出码 1，错误流上是 `CANNOT_FILL` 的三行 | 某个空餐在文字里没有位置，或者新文字没通过检查（第 8 和 12 步）。文件保持原来的字节。 |
| 退出码 1，错误流上是失败时的三行 | `replace_file` 给出 `FAILED`（第 13 步，选择 8）。文件保持原来的字节。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误，比如 `dishes` 的值不对（3.2）。因为 `menu suggest` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两者。 |
| 退出码 2，带 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`Unexpected argument "2026-W49". Write "recipe-menu menu suggest [WEEK]".` | 命令行写了两个周。 |
| 退出码 2，带一个选项时那种写法的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"menu suggest" has no option "--tags". Its own option is "--tag".` | `--tag` 和四个全局选项以外的选项。 |
| 退出码 2，带 `OPTION_NEEDS_VALUE` 或 `OPTION_TWICE`，不带下一行，比如 `--tag needs a value.` | `--tag` 没有值，或者写了两次。 |
| 退出码 2，带 F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。`replace_file` 删除它的临时文件，菜单文件要么保持旧文字，要么是新文字，`cli` 不再写出任何东西（F13 设计 3.1）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `menu suggest` 读一次 `catalog.toml`，列一次 `recipes/`，列一次 `menus/`，读两次这一周的菜单文件（一次通过 `read_week_menu`，一次通过 `read_file_text`），并把这一周还没有的每个菜谱文件各读一次。周不对时，它不读任何文件。遇到错误、未知的标签、`NO_MENU`、没有空餐的周或第 8 步的拒绝之后，它不再读任何东西。它既不读 `pantry.toml`、别的菜单，也不读这一周已经有的菜谱。某一餐得到菜、而且检查通过时，它通过 `replace_file` 修改这一周的菜单文件，`replace_file` 会写出并移动 `menus/<week>.toml.tmp`。它不改动别的文件。它写入输出流或错误流。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。每次运行都给 `main` 一个新的 `Random(3)`，所以 `Random(3).sample` 给出一次运行选中的菜谱（选择 6）。第一次运行就是 v0.2-S05：这一周唯一还没有的菜谱 `red-braised-pork` 填进周一午餐，文件里只有那一行会变。第二次运行找不到候选，不写文件。接着是未知的标签、没有菜单的周和不对的周这几次运行。然后，一个漏写一餐和六天的文件得到一行新行和几张新表，一个把某天写在花括号里的文件被拒绝。最后一次运行用设置 `dishes` 让晚餐有 2 道菜，所以还剩下一个菜谱时，第四个晚餐保持空着（C 点）。

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.cli import main
from recipe_menu.recipes import list_recipe_ids


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        random=Random(3),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


week47 = folder.menu_file("2026-W47")
before = week47.read_text(encoding="utf-8").splitlines()
assert run("menu", "suggest", "2026-W47") == (
    0,
    [
        "Filled 1 of 10 empty meals of 2026-W47. Kept the 4 meals that already have dishes.",
        "9 meals stay empty: no other recipe is left.",
    ],
    [],
)
after = week47.read_text(encoding="utf-8").splitlines()
changed = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
assert changed == [("lunch = []", 'lunch = ["red-braised-pork"]')]
assert after[3:5] == ["[monday]", 'lunch = ["red-braised-pork"]']
made = week47.stat().st_mtime_ns
assert run("menu", "suggest", "2026-W47") == (
    0,
    [
        "Filled 0 of 9 empty meals of 2026-W47. Kept the 5 meals that already have dishes.",
        "9 meals stay empty: no other recipe is left.",
    ],
    [],
)
assert week47.stat().st_mtime_ns == made

tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
unknown = (1, [], [f'Unknown tag "breakfast". {tags}'])
assert run("menu", "suggest", "2026-W47", "--tag", "breakfast") == unknown
no_menu = 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
assert run("menu", "suggest", "2026-W48") == (1, [], [no_menu])
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "suggest", "2026-W99") == (2, [], [week_error])

week48 = folder.menu_file("2026-W48")
week48.write_text('week = "2026-W48"\n\n[monday]\ndinner = []  # leftovers\n', encoding="utf-8")
ids, _ = list_recipe_ids(folder)
a, b, c, d, e, f, g = Random(3).sample(ids, 7)
assert run("menu", "suggest", "2026-W48") == (
    0,
    [
        "Filled 7 of 14 empty meals of 2026-W48.",
        "7 meals stay empty: no other recipe is left.",
    ],
    [],
)
assert week48.read_text(encoding="utf-8").splitlines() == [
    'week = "2026-W48"',
    "",
    "[monday]",
    f'lunch = ["{a}"]',
    f'dinner = ["{b}"]  # leftovers',
    "",
    "[tuesday]",
    f'lunch = ["{c}"]',
    f'dinner = ["{d}"]',
    "",
    "[wednesday]",
    f'lunch = ["{e}"]',
    f'dinner = ["{f}"]',
    "",
    "[thursday]",
    f'lunch = ["{g}"]',
]

week49 = folder.menu_file("2026-W49")
inline = 'week = "2026-W49"\nmonday = { lunch = [], dinner = [] }\n'
week49.write_text(inline, encoding="utf-8")
first = "  menu suggest cannot fill this file: write each day as a line such as [monday], "
second = 'and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.'
assert run("menu", "suggest", "2026-W49") == (
    1,
    [],
    [str(Path("menus", "2026-W49.toml")), first + second, "Nothing was changed."],
)
assert week49.read_text(encoding="utf-8") == inline

settings_text = folder.settings.read_text(encoding="utf-8")
meals = settings_text.replace('["lunch", "dinner"]', '["dinner"]')
folder.settings.write_text(meals + "dishes = { dinner = 2 }\n", encoding="utf-8")
assert run("menu", "new", "2026-W50")[0] == 0
assert run("menu", "suggest", "2026-W50") == (
    0,
    [
        "Filled 3 of 7 empty meals of 2026-W50.",
        "4 meals stay empty: too few other recipes are left.",
    ],
    [],
)
```

## 3. 对已有接口的修改

F14 给四个已实现的模块加上架构 5.1 和 5.2 为它计划的东西：给设置加上“F14 增加每餐的菜数”，给上下文加上“F14 增加一个随机数生成器”。F01 到 F13 导出的名称，没有一个调用会失效：每个新字段都有默认值，`main` 的新参数是可选的，`datafile` 多了两个名称。需求已经写到了这个设置（需求 4，F14），所以不需要 `[docs]` PR 批准这些增加的东西。架构师在这份设计里审查它们，就像审查 F11 的 `create_file` 和 F13 的 `replace_file` 那样。

1. `settings`：`Settings` 得到字段 `dishes` 和方法 `dishes_for`（3.1），`read_settings` 读取键 `dishes`（3.2）。现在两个设置的四个字段都相等时，它们才相等。键 `dishes` 以前给出 `UNKNOWN_KEY`，现在设置的 `UNKNOWN_KEY` 的文字列出四个键。
2. `app`：`Context` 得到字段 `random`（3.3）。现在两个上下文的七个字段都相等时，它们才相等，流和生成器按对象比较。
3. `cli`：`main` 得到参数 `random`（3.4），`COMMANDS` 得到 `MENU_SUGGEST_COMMAND`（选择 1）。
4. `datafile`：`read_file_text`（3.5）和 `parse_toml`（3.6）。

已验收功能的这些测试要改，第 2 节说明在哪个 PR 里改：

- F05-T10 和 F05-T11 把设置的 `UNKNOWN_KEY` 的文字和“language, meals, and servings”比较（`tests/f05_texts.py` 里的 `KEYS_EN` 和 `unknown_key`）。`read_settings` 读取 `dishes` 之后，这段文字列出“language, meals, servings, and dishes”。
- F11-T32 用真正的 `COMMANDS` 把 `recipe-menu menu` 和 `The commands that start with "menu" are "menu new" and "menu show".` 及其中文那一行比较。有了 mock 的这一项，这一行列出三个命令。
- F13-T01、F13-T22 和 F13-T27 把真正的 `COMMANDS` 的帮助和 `tests/f05_texts.py` 的 `HELP_EN`、`HELP_ZH`（F05 原型里的帮助）比较。有了 mock 的这一项，帮助多一行，它的第二列从第 21 列移到第 24 列。

这些测试仍然成立。F07-T17、F08-T14、F09-T01、F10-T01 和 F11-T01 检查真正的帮助里某一行跟在另一行后面，以及它的文字从 `--lang en|zh` 的文字开始的那一列开始。两者都成立，因为 `menu suggest` 那一行在 `menu show` 那一行之后，而且每一行都移动同样的 3 列。F11-T27 和 F11-T35 把真正的 `COMMANDS` 的一段帮助和另一段比较。F05 的测试运行它们自己的命令。没有测试运行 `menu suggest`，在 mock 之前它给出 `Unknown command "menu suggest".`。`init` 和 `menu new` 写出的文件和以前一样，所以 v0.1-S01、v0.1-S02 和 v0.1-S13 成立。F05 原型里的两段帮助显示的是 v0.1 的帮助，它的说明也这样写，所以从 mock 起，真正的帮助就和它们不同了。产品经理在 F14 验收时决定真实运行怎样对待这两段。v0.1-S19 和 v0.2-S14 按 v0.2 测试计划第 2 节的说法修改。

F14 按这些接口的设计使用它们，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural` 和 `and_list`。
- F03 的带 `menu_file` 和 `relative` 的 `DataFolder`、`Problem`、带 `find_tag` 的 `Catalog`，以及 `read_catalog`。
- F04 的 `Recipe`、`list_recipe_ids` 和 `read_recipe`。
- F05 在 `app` 里的 `Argument`、`Arguments`、`Command`、`FolderUse`、`UsageError`、`first_error`、`problem_lines` 和 `stop_at_error`，`settings` 里的 `Meal` 和 `Settings`，以及 `cli` 里的 `COMMANDS`，加上 3.1 到 3.4 增加的东西。
- F06 的 `Day`、`IsoWeek`、`NOT_A_WEEK`、`WeekMenu`、`MealSlot`、`list_menu_weeks`、`read_week_menu` 和 `week_from_argument`。
- F11 在 `menus` 里的 `NO_MENU`，以及 `datafile` 里的 `FileOutcome` 和 `FileCreation`。
- F13 在 `datafile` 里的 `replace_file`。

### 3.1 `Settings.dishes` 和 `Settings.dishes_for`

- 模块：settings
- 功能：`menu suggest` 放进一个空的早餐、午餐和晚餐的菜数，默认 1 道（[需求 4](../../requirements.zh-CN.md#4-功能点)，架构 5.1）。`read_settings` 从键 `dishes` 填写它（3.2），`menu suggest` 用 `dishes_for` 取得它（选择 6）。

签名：

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
    dishes: tuple[int, int, int] = (1, 1, 1)

    def dishes_for(self, meal: Meal) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `dishes` | 三个 `int` 组成的元组 | 早餐、午餐和晚餐的菜数，按 `Meal` 的顺序。 | 正好三项，每项是 1 到 10 之间的整数。不能是 `bool`。 |
| `meal` | `Meal` | `dishes_for` 给出其菜数的那一餐。 | 任何 `Meal`，包括 `meals` 没写到的。 |

其他字段的含义和约束不变（F05 设计 2.2）。

- 返回值：一个 `Settings`。两个设置的四个字段都相等时，它们相等，`Settings` 可以求哈希。`Settings()` 以及 F01 到 F13 的每个调用都让 `dishes` 保持 `(1, 1, 1)`。
  - `dishes_for(meal)` 给出 `dishes[list(Meal).index(meal)]`。

错误：

F05 设计 2.2 的错误保留，`dishes` 带来下面这些：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `dishes` 不是元组，或者有一项不是 `int`，或者是 `bool`。 |
| `ValueError` | `dishes` 不是正好三项，或者有一个数小于 1 或大于 10。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.dishes == (1, 1, 1)
assert [defaults.dishes_for(meal) for meal in Meal] == [1, 1, 1]
two = Settings(Lang.ZH, tuple(Meal), 3, (1, 1, 2))
assert two.dishes_for(Meal.DINNER) == 2
assert two.dishes_for(Meal.BREAKFAST) == 1
assert Settings(Lang.EN) == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2, (1, 1, 1))

Settings(dishes=(1, 1))  # raises ValueError
Settings(dishes=(1, 0, 1))  # raises ValueError
Settings(dishes=(1, 1, 11))  # raises ValueError
Settings(dishes=[1, 1, 2])  # raises TypeError
Settings(dishes=(1, 1, True))  # raises TypeError
Settings(dishes=(1, 1, 2.0))  # raises TypeError
```

### 3.2 `read_settings`：键 `dishes`

- 模块：settings
- 功能：把 `settings.toml` 里可选的键 `dishes` 读进 `Settings.dishes`，并像其他键一样报告它的问题和位置（F05 设计 2.3，选择 5）。`cli` 和 `check` 照旧调用 `read_settings`。

签名：

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：F05 设计 2.3 的那对 `(settings, problems)`，增加以下内容。
  - 文件里可以有键 `dishes`，它是一张表，键是 `Meal` 的值，每个键对应一个 1 到 10 之间的整数，比如 `dishes = { dinner = 2 }`。在文件末尾写 `[dishes]` 和 `dinner = 2` 两行，得到的是同一张表。表里没写的一餐，或者没有 `dishes` 的文件，得到 1。`meals` 没写到的一餐也可以有一个数，你加上这一餐之后它才起作用。
  - `settings.dishes` 按 `Meal` 的顺序存放每一餐的菜数。
  - 文件顶层的键是 `language`、`meals`、`servings` 和 `dishes`，按这个顺序。所以 `UNKNOWN_KEY` 用“多个键”的写法写出“language, meals, servings, and dishes”和“language、meals、servings 和 dishes”。

新问题的位置如下：

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| `dishes` | `dishes` | `菜数` |
| `dishes` 里某餐 M 的数 | `dishes of`、一个空格和这一餐的 `label`，比如 `dishes of dinner` | 这一餐的 `label` 和 `的菜数`，比如 `晚餐的菜数` |

`read_settings` 对 `dishes` 做这些检查。缺少这个键不算问题。

| 部分 | 检查 | 问题 | 位置 | 种类 |
| --- | --- | --- | --- | --- |
| `dishes` | 值不是表，比如 `dishes = 2` 或 `dishes = []`。 | `DISHES_NOT_A_TABLE` | `dishes` | 错误 |
| `dishes` 的一个键 | 这个键不是 `Meal` 的值，比如 `supper` 或 `Dinner`。 | `settings` 的 `UNKNOWN_MEAL`（F05 设计 2.3） | `dishes` | 错误 |
| `dishes` 里是某一餐的键 | 值不是 1 到 10 之间的 `int`，或者是 `bool`，比如 `0`、`11`、`2.5`、`"2"` 或 `true`。 | `DISHES_NOT_1_TO_10` | 这一餐的数 | 错误 |

`dishes` 的问题排在 `servings` 的问题之后、文件顶层未知的键之前。不是表的值只给出它自己的问题。否则表里的各个键按文件里的顺序给出它们的问题。`UNKNOWN_MEAL` 的位置是 `dishes`，因为提示里写了这一餐，和 `meals` 的做法一样（F05 设计 2.3）。

这些是 `settings` 的新提示。在 `DISHES_NOT_A_TABLE` 的模板里，每个花括号都写两次（F02 设计 2.2）。`DISHES_NOT_1_TO_10` 不显示数字，所以几千位的值也不会碰到 F02 的限制。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `DISHES` 和 `DISHES_OF` | 位置表里的那些位置，`{meal}` 代表这一餐的 `label`。 | 位置表里的那些位置，`{meal}` 代表这一餐的 `label`。 |
| `DISHES_NOT_A_TABLE` | `"dishes" must be a table in braces, such as dishes = { dinner = 2 }.` | `“dishes”必须是放在花括号里的表，比如 dishes = { dinner = 2 }。` |
| `DISHES_NOT_1_TO_10` | `The number of dishes must be a whole number from 1 to 10, such as 2.` | `菜数必须是 1 到 10 之间的整数，比如 2。` |

`UNKNOWN_MEAL` 的占位符的值和 F05 设计 2.3 的相同：`meal` 是文件里写的键，`meals` 是 `Meal` 各个值的 `and_list`。

错误：无。`read_settings` 遇到坏数据从不抛异常。

- 副作用：和以前一样，通过 `read_toml` 读取 `settings.toml`。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本。

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings, read_settings

lines = ['meals = ["breakfast", "lunch", "dinner"]', "dishes = { dinner = 2 }"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
assert read_settings(folder) == (Settings(None, tuple(Meal), 2, (1, 1, 2)), ())
folder.settings.write_text("[dishes]\nlunch = 3\n", encoding="utf-8")
assert read_settings(folder) == (Settings(dishes=(1, 3, 1)), ())

lines = ["dishes = { dinner = 0, supper = 2, lunch = true }", "colour = 1"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [
    BiText("dishes of dinner", "晚餐的菜数"),
    BiText("dishes", "菜数"),
    BiText("dishes of lunch", "午餐的菜数"),
    None,
]
english = problems[0].text(Lang.EN)
assert english == "The number of dishes must be a whole number from 1 to 10, such as 2."
assert problems[0].text(Lang.ZH) == "菜数必须是 1 到 10 之间的整数，比如 2。"
unknown = 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
assert problems[1].text(Lang.EN) == unknown
keys = 'Unknown key "colour". The keys are language, meals, servings, and dishes.'
assert problems[3].text(Lang.EN) == keys

folder.settings.write_text("dishes = []\n", encoding="utf-8")
_, problems = read_settings(folder)
not_a_table = '"dishes" must be a table in braces, such as dishes = { dinner = 2 }.'
assert [problem.text(Lang.EN) for problem in problems] == [not_a_table]
```

### 3.3 `Context.random`

- 模块：app
- 功能：命令的随机数生成器（[架构 5.2](../../architecture.zh-CN.md#52-值) 和 [8](../../architecture.zh-CN.md#8-命名和编码规范)）。`cli` 用系统给的种子创建它（3.4），测试传入一个种子固定的生成器。`menu suggest` 用它选菜谱（选择 6）。

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
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `random` | `random.Random` | 命令从中取得随机选择的生成器。 | `cli` 创建上下文时，是 `main` 得到或创建的那个生成器（3.4）。不传时，每个上下文得到一个新的 `Random(0)`，所以创建上下文的测试每次都得到相同的选择。 |

其他字段的含义和约束不变（F05 设计 2.4）。`Random` 是 `random.Random`，`field` 是 `dataclasses.field`。项目检查的 `S` 规则里，ruff 的规则 S311 会标出 `Random(0)`。所以默认值那一行带上 `# noqa: S311` 和理由，写法和测试里的一样，比如 `# noqa: S311 - a fixed seed, no security`，从 mock PR 起就带上，因为 mock 加上了这个字段。

- 返回值：一个 `Context`。两个上下文的七个字段都相等时，它们相等，流和生成器按对象比较。所以各自创建了默认生成器的两个上下文不相等。`Context` 可以求哈希。

错误：无

- 副作用：无。用默认值创建上下文时会创建一个 `Random(0)`，它不读取外部世界的任何东西。
- 性能指标：无

示例：

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.app import Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
today = date(2026, 11, 10)
seeded = Random(5)
context = Context(Lang.EN, folder, Settings(), out, err, today, seeded)
assert context.random is seeded
first = Context(Lang.EN, folder, Settings(), out, err, today)
second = Context(Lang.EN, folder, Settings(), out, err, today)
assert first.random is not second.random
assert first != second
assert first.random.random() == second.random.random() == Random(0).random()
```

### 3.4 `main`：参数 `random`

- 模块：cli
- 功能：让测试固定命令的随机选择（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)：只有 `cli` 读取随机种子）。`main` 把生成器放在 `Context.random` 里传给命令（3.3）。

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
) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `random` | `random.Random` 或 `None` | 命令的生成器。 | `None` 时为 `Random()`，它从系统的随机字节来源取得种子，所以安装好的命令每次运行都重新选择。 |

其他参数的含义和约束不变（F05 设计 2.9）。ruff 的规则 S311 也会标出 `Random()`。所以 `main` 里创建它的那一行带上 `# noqa: S311` 和理由，比如 `# noqa: S311 - a recipe choice, no security`，从第一个写出这一行的 PR 起就带上。mock 不把生成器传下去（第 2 节），所以那是实现 PR。

- 返回值：和以前一样，是 F05 设计 2.10 的退出码。在 F05 设计 2.10 的第 10 步，`Context` 带着这个生成器。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 和以前一样，`commands` 违反它的约束（F05 设计 2.9）。 |

- 副作用：F05 设计 2.9 的那些副作用。`random` 为 `None` 时，`main` 在运行命令之前创建一个 `Random()`。它不读取别的种子。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。`PICK` 代表一个取随机选择的命令。

```python
import io
from datetime import date
from random import Random

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message

seen: list[Random] = []


def run_pick(context: Context, arguments: Arguments) -> int:
    seen.append(context.random)
    return 0


PICK = Command(("pick",), Message("Pick a recipe.", "挑一个菜谱。"), run_pick)


def pick(random: Random | None) -> int:
    return main(
        ["pick", "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        commands=[PICK],
        random=random,
    )


seeded = Random(9)
assert pick(seeded) == 0
assert seen == [seeded]
assert pick(None) == 0
assert isinstance(seen[1], Random)
assert seen[1] is not seeded
```

### 3.5 `read_file_text`

- 模块：datafile
- 功能：把一个数据文件读成 UTF-8 文字；文件读不了或不是 UTF-8 时，给出 `read_toml` 的那些问题（F03 设计 2.3）。`menu suggest` 用它读菜单文件的文字，以便修改空餐的那几行、保留其他每一行（选择 7）。只有 `datafile` 打开数据文件（架构 8）。

签名：

```python
def read_file_text(folder: DataFolder, path: Path) -> str | Problem: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `path` | `Path` | 要读的文件，比如 `folder.menu_file("2026-W47")`。 | 在 `folder.root` 里面。 |

- 返回值：文件的文字；或者一个 `Problem`，严重程度为 `Severity.ERROR`，文件为 `folder.relative(path)`。
  - `read_file_text` 执行 `read_toml` 的第 1 步和第 2 步，带着它们的问题：读出字节，再用 `utf-8-sig` 编解码器和严格的错误处理一次全部解码。`OSError` 给出不带位置的 `FILE_IS_FOLDER`、`FILE_MISSING`、`ACCESS_DENIED` 或 `SYSTEM_ERROR`，`UnicodeDecodeError` 在它所在的行给出 `NOT_UTF8`（F03 设计 2.3）。
  - 文字里没有字节顺序标记，换行符和文件里的一样，所以 CR LF 仍然是 CR LF。它不解析这段文字。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 按 `DataFolder.relative` 的判断，`path` 不在 `folder.root` 里面。这项检查在读文件之前进行。 |

- 副作用：读一个文件的字节。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本。

```python
from pathlib import Path

from recipe_menu.datafile import Problem, read_file_text
from recipe_menu.lang import BiText, Lang

file = folder.menu_file("2026-W47")
text = read_file_text(folder, file)
assert isinstance(text, str)
assert text.splitlines()[:2] == ["# 2026-W47: 16 to 22 November 2026", 'week = "2026-W47"']
file.write_bytes(b'\xef\xbb\xbfweek = "2026-W47"\r\n')
assert read_file_text(folder, file) == 'week = "2026-W47"\r\n'
file.write_bytes(b"week = 1\n\xff\n")
broken = read_file_text(folder, file)
assert isinstance(broken, Problem)
assert broken.place == BiText("line 2", "第 2 行")
not_utf8 = "The file cannot be read: it is not UTF-8 text. Save it as UTF-8."
assert broken.text(Lang.EN) == not_utf8
missing = read_file_text(folder, folder.menu_file("2026-W48"))
assert isinstance(missing, Problem)
assert (missing.file, missing.place) == (Path("menus", "2026-W48.toml"), None)
assert missing.text(Lang.EN) == "The file is missing."

read_file_text(folder, folder.root.parent / "elsewhere.toml")  # raises ValueError
```

### 3.6 `parse_toml`

- 模块：datafile
- 功能：解析一段不是文件的 TOML 文字，比如菜单文件的新文字，让 `menu suggest` 能在写出之前检查它（选择 7）。它让 TOML 的解析留在 `datafile` 里（ADR-0002）。调用方比较这张表，从不把它再传出去（架构 5）。

签名：

```python
def parse_toml(text: str) -> dict[str, object] | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 要解析的文字。 | 任何字符串。 |

- 返回值：`tomllib.loads(text)`；`tomllib` 抛出 `TOMLDecodeError`、数字位数太多时的普通 `ValueError`，或者嵌套太深时的 `RecursionError` 时为 `None`，这正是 `read_toml` 第 3 步捕获的三种异常（F03 设计 2.3）。它不给出原因和行号，因为调用方只需要知道这段文字能不能解析。

错误：无。对于 `str`，`parse_toml` 从不抛异常。

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.datafile import parse_toml

assert parse_toml('week = "2026-W47"\n[monday]\ndinner = ["rice"]\n') == {
    "week": "2026-W47",
    "monday": {"dinner": ["rice"]},
}
assert parse_toml("") == {}
assert parse_toml("[monday]\n[monday]\n") is None
assert parse_toml('dinner = ["rice"') is None
assert parse_toml("servings = " + "1" * 5000) is None
assert parse_toml("x = " + "[" * 5000 + "]" * 5000) is None
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `suggest` 是架构 3 交给 F14 的命令模块，位于 `src/recipe_menu/commands/suggest/`，只导出 `MENU_SUGGEST_COMMAND`。它只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`，都在它那一行里。它既不需要 `units`、`shopping`，也不需要 `menu`，所以不给架构 4 增加箭头。它在 `COMMANDS` 里的那一项，就是架构 4 允许命令功能对 `cli` 做的唯一修改。第 3 节增加的正是架构 3、5.1 和 5.2 为 F14 规划的内容：`settings.toml` 和 `Settings` 里每餐的菜数，`Context` 里只由 `cli` 设定种子的随机数生成器（架构 8），以及 `datafile` 里的两个读取函数，而 `datafile` 是唯一打开数据文件的模块。ADR-0001 已经写明推荐要用 `random`。`Settings.dishes` 是按 `Meal` 顺序排列的三个 `int` 组成的元组，`Context.random` 是 `random.Random`。两者都是冻结 dataclass 里带默认值的字段，所以符合架构 8 对值的规定。`parse_toml` 只把原始表交给 `suggest`，`suggest` 只比较这个表，不往外传，所以符合架构 5 对原始表的规定。`menu suggest` 写的文件就是架构 5.1 的 `menus/<week>.toml`，用 UTF-8、不带字节顺序标记、以 LF 换行，并且通过 `replace_file` 写入，这正是架构 6 给要替换的文件规定的写法。选择 7 只用标准库，符合 ADR-0001 和 ADR-0002，并且没有采用需要走 R16 的 tomlkit。选择 11 现在给出了 `import random` 实测的 1.7 到 2.1 毫秒（第 1 轮的备注 1）。 |
| 遵守错误处理和命名约定 | 通过 | 读取函数的第一个错误通过 F05 的 `first_error` 和 `stop_at_error` 让 `menu suggest` 停下。`NO_MENU`、未知标签、`CANNOT_FILL` 和保存失败都写到 stderr，退出码为 1；错误的周是唯一的 `UsageError`，不带提示（架构 6，ADR-0008）。`CANNOT_FILL` 是一个 `Problem`，文件相对于数据文件夹。`menu suggest` 用 `problem_lines` 写出它，最后一行是 `CHANGED_NOTHING` 而不是 `RUN_CHECK`，因为 `check` 不会报告它，和 `menu new` 结束失败的方式一样（ADR-0010 第 5 节）。`read_file_text` 把每个 `OSError` 和 `UnicodeDecodeError` 变成 `Problem`，和 `read_toml` 一样；`parse_toml` 只捕获 `read_toml` 捕获的那三种异常（架构 6 和 8）。名称符合架构 8：键 `dishes`、放在各模块 `messages.py` 里的提示，以及 `read_file_text` 这个名字，它和 `datafile` 已经导出的 `read_text` 区分开了。要点 D 的做法 1 沿用 ADR-0010 的方式：在 mock PR 之前的一个 `[docs]` PR 里，为换菜那一行给架构 6 加一句话，并配一个 ADR。失败时的第一行和 `CANNOT_FILL` 已经符合架构 6 对问题的规定。3.3 和 3.4 现在给 `Random(0)` 和 `Random()` 写明了带理由的 `# noqa: S311`（第 1 轮的备注 2）。架构师用 ruff 0.17.4 和项目的 `pyproject.toml`，在一个示例文件上核实了这两行。单独的 `Random()` 会得到 S311。带上注释的这两行都能通过 S311、RUF100 和 E501；默认值那一行有 103 列也能通过，因为 ruff 计算 100 列的限制时不算行尾的 `# noqa` 注释。2.1 的示例导入了 `UsageError`（备注 3）。 |
| 不和已有接口重复 | 通过 | `menu suggest` 用 `week_from_argument` 得到周，用 `Catalog.find_tag` 得到标签，用 `read_week_menu` 得到空餐，用 `list_recipe_ids` 和 `read_recipe` 得到候选菜谱，用 `replace_file` 写入。这些它都没有重写。`read_file_text` 和 `parse_toml` 是新的：没有接口给出文件的文本或解析一段文本，两者都可以在 `datafile` 内部共用 `read_toml` 的步骤。`WEEK_ARGUMENT`、`CHANGED_NOTHING`、`UNKNOWN_TAG` 和 `NO_TAGS` 的副本是内部提示，架构 8 让每个模块各自保存。`suggest` 不能引用 `browse`，`menu` 只导出它的命令，所以这些副本的理由和 F13 审查为 `shop` 接受的理由相同。读取目录并在第一个错误处停下的代码是第五份内部代码副本，F13 审查备注 2 说的那个后续 `[refactor]` PR 可以通过 `app` 里的辅助函数共用它。第 2 轮没有改动这里。 |
| 只依赖排序在前面的功能 | 通过 | F14 使用 F02 的 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`、F05 的 `app`、`settings` 和 `cli`、F06 的 `menus`、F11 的 `NO_MENU`、`FileOutcome` 和 `FileCreation`，以及 F13 的 `replace_file`，并复制了 F09 的两条文字。这些功能都排在 F14 前面，都已在 main 上验收，硬依赖 F05 也已验收。需求的依赖图里 F14 那一行没有 F13。F14 通过共享模块 `datafile` 使用它，而 `datafile` 指向更早的功能，这是架构 4 允许的。给 F15 和 F16 的规划不约束后面的设计。F14 只需要标准库，所以 R16 没有要审查的。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写下了模块之间的每个假设。`suggest` 知道 `menus` 读取、`menu new` 写出的菜单文件格式，但它从不只靠自己的行模式。用 `parse_toml` 检查新文本时，结果必须等于旧表加上新菜，所以模式读错的格式会被拒绝，永远不会被写入（2.2）。菜谱 ID 不需要转义（F04 设计 2.4）。临时文件 `<week>.toml.tmp` 不会被任何读取函数读到，因为 `list_menu_weeks` 和 `check` 只统计以 `.toml` 结尾的名称（F06 设计 2.8）。写入的路径只来自 `menu_file`，而且是在 `list_menu_weeks` 给出这一周之后（选择 8）。`dishes_for` 把 `Settings.dishes` 的顺序藏在里面，`Context.random` 默认是一个新的 `Random(0)`，所以自己构建上下文的测试得到固定的选择（3.3）。在模型上，带 CR LF 换行和字节顺序标记的文件，每一行的文字都保留，换行变成 LF，标记被去掉。带引号的表头和键，以及 `[]` 后面的注释，文字都保留。写成 `lunch = [`、下一行才是 `]` 的一餐，在第 8 步就停下，还没有读任何菜谱。用点号键或花括号写的一天得到 `CANNOT_FILL`。末尾没有 LF 的文件，在新表之前先补上一个 LF。只读的菜单文件给出 `menus\2026-W48.toml`、`  The file cannot be written: access is denied.` 和 `Nothing was changed.`，文件字节不变，也不留下 `.tmp` 文件。选择 7 现在写出了 Troy 最可能遇到的被拒绝的格式，这是对的。`tests/data/example/menus/2026-W47.toml` 里周日晚餐的列表分五行写，删掉其中三道菜会留下 `dinner = [` 和 `]`。`read_week_menu` 把这一餐读成空餐，而 2.2 位置表里只有最后一行适用于它那一行，所以第 8 步给出 `CANNOT_FILL` 后停下，还没有读任何菜谱。v0.2-S15 那一项现在写明，移动会让 `menus\` 得到新的修改时间，第 1 步只算文件，不算文件夹，这和 v0.2 测试计划里 v0.2-S15 预期结果的“唯一字节或时间有变化的文件”一致（第 1 轮的备注 4）。 |
| 修改已实现的接口时走了变更流程 | 通过 | 这个 PR 只添加两个设计文件。第 3 节给 `settings`、`app`、`cli` 和 `datafile` 增加的，只有 F05 的设计和架构 5.1、5.2 为 F14 规划的内容：一个带默认值的字段和一个方法，一个带默认值的字段，一个可选参数，以及两个新名称。F01 到 F13 导出名称的调用都不会出错。需求已经写明了这个设置，所以需求不变，由架构师在这里审查这些增加，就像审查 F11 的 `create_file` 和 F13 的 `replace_file` 那样。第 1 轮用第 3 节的模型并把 `MENU_SUGGEST_COMMAND` 放进 `COMMANDS` 后，在 Windows 上整个测试集的结果是 577 个通过、6 个失败、4 个跳过。这 6 个失败正好是第 3 节列出的 F05-T10、F05-T11、F11-T32、F13-T01、F13-T22 和 F13-T27，4 个跳过是 main 上只在 Linux 运行的用例。所以第 2 节的计划成立：在 mock 之前用一个 test-fix PR 修改被那一项弄坏的四个测试；F05-T10 和 F05-T11 在那个 PR 或 F14 的测试 PR 里修改，因为 mock 不改 `read_settings`。mock 的 10 个文件和实现的 9 个文件、约 700 行都超过 R03 的限制，它们的软限制理由是对的：测试既直接、又通过 `menu suggest` 用到设置、上下文和 `datafile`。第 1 轮的备注 5 要求这六个测试不受 F15 和 F16 以后加上的行和键影响，例如像 F11-T01 那样用 `commands=` 传入 v0.1 的八个命令。它交给 F14 测试计划的测试经理任务说明，所以第 3 节保持原样是对的。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | PR #102 开头的摘要（提交 e74d593）和设计说的一致。发现 1 在两种语言里都已修正。“对你有什么变化”现在写明：每一行的文字都不变，只有得到菜的那一餐的 `[]` 会变；漏写的某餐那一行或某一天会被补上；用 Windows 换行符或带字节顺序标记保存的文件会改用 Unix 换行符，也不再带这个标记。这和需求对照表以及选择 7 现在说的一样。备注 6 已采纳：第一条风险写出了示例那一周的周日晚餐清空后剩下的 `dinner = [` 和 `]`，和选择 7 现在写的一样；英文的帮助那一行写成了第二列右移。其余和第 1 轮相同：新命令和 `--tag`、换菜、从周一往后填、新设置和帮助；然后是要点 A 到 D，编为第 1 到 4 条，每一条都有方案和带理由的推荐；然后是三条风险。要点 A 的 19 条文字仍然是原型没有展示的 `suggest` 的 15 条提示和 `settings` 的 4 条。架构师没有发现别的需要 Troy 决定的事。在 PR 描述上运行 troy-check 的 `summary.py` 里的检查，全部通过。中文部分有 1,016 个字符，英文部分有 1,969 个，都在 R22 的 2,000 以内。两部分都按顺序有三个部分，4 条里每一条都有推荐，也都不含内部编号。英文部分只剩 31 个字符，所以以后对它的修改要很短。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 发现 1（第七项）是阻塞问题。“对你有什么变化”里的“文件里只有被填的那一餐的 `[]` 会变”（“Only the `[]` of each filled meal changes”）和选择 7 对用 CR LF 换行或带字节顺序标记保存的文件所说的不一致。这样的文件会改成 LF 换行并去掉标记，因为架构 5.1 规定工具写的每个文件都用不带标记的 UTF-8 和 LF 换行，模型也证实了这一点。需求说文件的其余部分保持不变，所以 Troy 必须在批准之前看到这一点。要求：在两种语言里写明，用 Windows 换行或带字节顺序标记保存的文件会改成 Unix 换行、不带标记，每一行的文字保持不变。英文部分还剩 117 个字符。架构师对照需求、架构、ADR-0001、ADR-0002、ADR-0008 到 ADR-0010、F05、F06、F11 和 F13 的设计、F05 和 F14 原型，以及 v0.2-S01 到 v0.2-S08 和 v0.2-S14 到 v0.2-S16，检查了 12 个选择、第 3 节和要点 A 到 D。两个文件有同样的 14 个标题和 171 个表格行，以及 18 个代码块，每个都和镜像里的相同，没有不可见字符。架构师在 Windows 上用 Python 3.13.18，在 main 的 `src/` 的一份副本里按第 2 节和第 3 节建了模型，运行了每个文件的 8 个示例。在 2.1 的示例导入 `UsageError` 之后（备注 3），全部 72 个断言和全部 8 个 `# raises` 都成立。2.1 的两份帮助和模型的帮助逐行相同，`recipe-menu menu` 给出选择 1 的那一行。第六项和第七项给出整个测试集和 PT01 运行的结果。没有运行 Linux 上的结果。备注 1 到 6 不阻塞。 | 要求修改。接口设计师在摘要的两种语言里修正发现 1，并可以在设计里采纳备注 1 到 6。如果 Troy 选择要点 D 的做法 1，架构师的 `[docs]` PR 还会在架构 5.2 的 `Settings` 那一行加上每餐的菜数。 |
| 2 | 没有阻塞问题。架构师在两个文件里把 0.2 版和第 1 轮审查的那一版做了比较。改动的是需求对照表、选择 7 和 11、v0.2-S15 那一项、3.3、3.4、2.1 示例里的导入、文件头和修改记录，两种语言都相同。需求对照表和选择 7 现在说的，就是发现 1 要求摘要说的内容；设计也采纳了备注 1、2、3、4 和 6。备注 5 交给测试经理的任务说明。两个文件有同样的标题和表格行，以及 18 个代码块，每个代码块都和镜像里的相同，没有不可见字符。代码块里唯一的改动是导入 `UsageError`，所以第 1 轮运行示例的结果仍然成立，模型没有再运行。没有运行 Linux 上的结果。 | 通过。要点 D 无论选哪种做法，架构 6 都要改。所以架构师按要点 D 给出的时间，用一个 `[docs]` PR 把 Troy 的选择记进架构 6 和一个 ADR，同时在架构 5.2 的 `Settings` 那一行加上每餐的菜数。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-17 | 初稿。 |
| 0.2 | 2026-11-17 | 架构师审查第 1 轮。需求对照表和选择 7 说明：用 CR LF 换行或带字节顺序标记保存的文件，每一行的文字都不变，但会改用 LF 换行，也不再带这个标记；选择 7 还写出你最可能遇到的被拒绝的格式。选择 11 给出 `import random` 实测的耗时。v0.2-S15 那一项说明文件夹 `menus\` 会得到新的修改时间。3.3 和 3.4 给出 `Random(0)` 和 `Random()` 的 `# noqa: S311`。2.1 的示例引用了 `UsageError`。 |
| 1.0 | 2026-11-17 | Troy 批准。 |
