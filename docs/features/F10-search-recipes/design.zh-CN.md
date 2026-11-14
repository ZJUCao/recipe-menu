---
troy-doc: "F10-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-13"
status: "Troy 已于 2026-11-13 批准"
mirror-of: "design.md"
---

# F10 搜索菜谱：接口设计

## 1. 功能

- 编号和名称：F10 搜索菜谱
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F03、F04、F09

## 2. 接口

F10 在 `src/recipe_menu/commands/search/` 里构建命令模块 `search`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.search` 导出一个名称 `SEARCH_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出它。你输入的命令是 `recipe-menu search`（2.2）。它的提示放在 `src/recipe_menu/commands/search/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F10 在它的 mock PR 里把这个命令加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `SHOW_COMMAND` 之后。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F10 还让 `catalog` 把它的匹配形式导出为 `matching_form`，这样 `search` 就按 F03 的大小写规则比较词和名称（3.1 节）。F10 原型 `docs/prototypes/F10-search.md` 展示了这个命令，F05 原型展示了它在帮助里的那一行。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F10 提供的接口 |
| --- | --- |
| `recipe-menu search WORD...` 列出匹配每个词的菜谱。 | `recipe-menu search`（2.2），以及 `SEARCH_COMMAND`（2.1）的参数 `WORD`，它接受一个或多个词。每个词都出现在菜谱的至少一个位置里时，这个菜谱就匹配（选择 4）。 |
| 词在菜谱名、食材名或标签名里匹配，中英文都算。 | 选择 3 的三个位置：菜谱的名称、它的食材在目录里的名称，以及它的标签在目录里的名称，每个都包括两种语言。 |
| 英文匹配不区分大小写。 | F03 的匹配形式，`catalog` 把它导出为 `matching_form`（选择 4，3.1 节）。 |
| 每条结果写明匹配在哪里。 | `Matched in` 这一列（选择 5）。 |
| 数据文件夹里有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`search` 在 1 秒内完成（PT01，[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。 | 2.2 的性能指标，以及选择 10。 |

下面每个接口都遵守这些规则：

- `search` 在包内只引用 `app`、`lang`、`text`、`datafile`、`catalog` 和 `recipes`。架构 3 里它那一行允许这些模块。它不需要 `units`、`settings`、`menus`、`shopping` 和 `browse`（选择 2，[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `search` 只通过 F03 和 F04 的读取函数访问磁盘，这些函数又通过 `datafile` 读取（架构 8）。它不写任何文件（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 1](../../architecture.zh-CN.md#1-背景和约束)）。它只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西，也不保存状态。它为匹配这些词而构建的东西，比如目录里各名称的匹配形式，只在一次运行里存在，所以没有模块保存缓存（架构 8）。
- `search` 不用 `context.settings`，也不用 `context.today`。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`search` 在数据文件的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。`run` 只为空的词抛出 `UsageError`，而且在读取任何文件、写出任何输出之前抛出（F05 设计第 2 节）。传到 `cli` 的任何其他异常都是 bug。
- `SEARCH_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。F10 不增加值类型。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- `recipe-menu search` 有性能指标 PT01（选择 10）。它把需要的每个文件只读一次，并在读完最后一个文件后一次写出输出。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 给出它们的规则。

1. **一个命令有自己的模块，在帮助里排在 `show` 之后。** 架构 3 给这个命令一个自己的模块 `search`。F10 把 `SEARCH_COMMAND` 加在 `COMMANDS` 里 `SHOW_COMMAND` 的后面，所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND)`，符合 F05 设计第 2 节的帮助顺序。`search` 有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它（F05 设计 2.5）。它按 F05 设计的计划，用 `repeats=True` 声明参数 `WORD`。所以这个参数是必需的，`cli` 会报告没有词的搜索，帮助写成 `search WORD...` 和 `search 词...`（F05 设计 2.5）。`search` 不声明选项。有这五个命令时，帮助里最宽的第一格是 `search WORD...`，占 14 列，比 `--data FOLDER` 和 `--data 文件夹` 多一列。所以两种语言里，两张表的第二列都从第 19 列之后开始，而不是像 F09 之后那样从第 18 列之后开始。两张表的每一行都保持原来的文字，整体右移一列，帮助共 18 行。2.1 给出这两张表。有 v0.1 的八个命令时，最宽的第一格是 `menu show [WEEK]`，占 16 列，帮助仍然给出 F05 原型的两段输出。第 3 节列出检查真正帮助的测试，它们都仍然成立。
2. **不和 `browse` 共用任何东西。** 架构 4 允许 `search` 引用 `browse`，F09 的设计把这个选择留给了 F10。`search` 不从 `browse` 引用任何东西，`browse` 保持它的两个导出。两个命令共同的东西很少。ID 这一格是 `recipe.id`，名称这一格是 `recipe.name.get(context.lang)`，各是一个基于 F04 和 F02 接口的表达式。F09 选择 5 的列宽不适用于 `search`（选择 7）。表头 `ID` 和 `Name` 是两条提示，而架构 8 让每个模块把自己的提示放在自己的 `messages.py` 里。所以 `search` 定义自己的 `ID_HEADING` 和 `NAME_HEADING`，文字与 `browse` 的相同，也就是 F10 原型显示的文字。从 `browse` 导出它们，会为两段短文字给 F09 的接口增加两个名称。代价是改其中一个表头时，两个模块都要改。
3. **词可以出现在哪里。** 菜谱有需求里的三个位置，每个位置都有两种语言的文字：
   - 名称：`recipe.name.en` 和 `recipe.name.zh`。缺少一种语言的名称在这里只有另一种语言的文字。`BiText.get` 的回退只会再给出同一段文字，所以不会改变任何结果。
   - 食材：每一行食材上目录里那个 `Ingredient` 的两个名称，`line.ingredient.name.en` 和 `line.ingredient.name.zh`。菜谱文件用任一种语言写食材，比如 `item = "鸡蛋"`，F04 用 `Catalog.find_ingredient` 找到它（F04 设计 2.6）。所以每一行都指向目录里的那个食材本身，它总有两个名称（F03 设计 2.4），`search egg` 能找到文件里写 `鸡蛋` 的菜谱。文件在 `item` 后面写的文字不增加任何东西，因为它的匹配形式等于那两个名称之一的匹配形式。
   - 标签：`recipe.tags` 里每个 `Tag` 的两个名称，它们也来自目录。

   其他都不算，这是需求的说法：备注、步骤、ID、份数、数量、单位和食材的分类都不算。所以 `search wedges` 和 `search 切块` 找不到备注，`search scramble` 找不到步骤，`search dairy` 找不到分类，比如 `Eggs, dairy, and tofu`。因为 ID 不算，F09 的后半句 `Run "recipe-menu search mapo" to find it.` 靠英文名称 `Mapo tofu` 找到 `mapo-tofu`（2.2）。对 `show tomato-eggs` 这样的拼写错误，后半句里的搜索什么也找不到，因为没有名称含有 `tomato-eggs`。
4. **词怎样比较。** `matching_form(word)` 是 `matching_form(text)` 的一部分时，词就出现在这段文字里，也就是 Python 的 `in` 检查的那样。`matching_form` 是 F03 的匹配形式（F03 设计 2.6），`catalog` 为 F10 导出它（3.1 节）。所以 `search` 的大小写规则与 `find_ingredient` 和 `find_tag` 相同，也没有模块另写一份，这是架构师在 F03 审查里的要求。对词来说，由此得出这些规则：
   - 词可以是一个更长名称的一部分，就像原型里 `番茄炒蛋` 中的 `番茄` 和 `Tomato and egg stir-fry` 中的 `TOMATO`。中文的词之间不写空格，所以搜索 `番茄` 必须在 `番茄炒蛋` 里面找，英文也按同一条规则。所以 `search egg` 也会找到含有 `Eggplant` 的菜谱，`search pork` 会找到 `Pork belly` 和 `Minced pork`。
   - 只有 A 到 Z 的字母不分大小写，所以 `TOMATO`、`tomato` 和 `Tomato` 找到相同的菜谱。这条规则在两种语言的文字里都改变 A 到 Z，汉字按原样比较。
   - 词两端的空白不算，按 `str.strip()` 的方式去掉，包括 U+3000 IDEOGRAPHIC SPACE。所以 `search "\u3000番茄"` 找到的与 `search 番茄` 相同。U+200B ZERO WIDTH SPACE 不是空白（F03 设计 2.6，规则 1），所以 `"\u200b"` 是只有一个字符的词，示例文件夹里没有名称含有它。
   - 词中间的空白按原样计算。`search "and egg"` 找到名称含有 `and egg` 的两个菜谱，带 U+00A0 NO-BREAK SPACE 的 `search "tomato\u00a0and"` 什么也找不到。
   - 形似的字母保持原样，文字也不做规范化。带 U+FF34 FULLWIDTH LATIN CAPITAL LETTER T 的 `search "\uff34omato"` 什么也找不到。
   - 匹配形式为空的词，比如 `""`、`" "` 或 `"\u3000"`，是命令行上的错误值。每段文字都含有空文字，所以不检查的话，这样的词会匹配每个菜谱。`run` 在读任何文件之前检查每个词，对第一个这样的词抛出 `UsageError(EMPTY_WORD, None)`，`cli` 以 2 退出（架构 6，F05 设计 2.7）。提示已经说了该写什么，所以不带下一行（ADR-0008）。这个选择由 Troy 决定（下面的 B 点）。
   - 每个词都出现在菜谱的至少一个位置里时，这个菜谱就匹配。两个词可以出现在不同的位置，比如 `葱` 在食材里，`quick` 在标签里。词的顺序既不改变找到的菜谱，也不改变它们的位置。
   - 写了两次的词，比如 `search egg egg` 里的词，找到的与写一次相同（选择 6）。
   - 以 `--` 开头的词对 `cli` 来说是选项（F05 设计 2.10），所以 `search` 不能查找它。以一个 `-` 开头的词，比如 `-x`，是词。
5. **每条结果匹配在哪里。** 最后一列 `Matched in` 和 `匹配于` 写出至少有一个词出现的每个位置，按名称、食材、标签的顺序，每个位置只写一次。所以几个词的位置会合并。在 `search 葱 quick` 里，`葱` 出现在食材里，`quick` 出现在标签里，所以这一格是 `食材、标签`，和原型一样。出现在两个位置的词，比如 `番茄` 既在名称里又在食材里，会给出两个位置。这一格是各位置提示的 `comma_list`，这是 F02 设计 2.6 为格子里的短列表计划的用法：`name, ingredient` 和 `食材、标签`。
6. **表格下面的那一行。** 它数出菜谱，并重复这些词。`{words}` 是这些词的 `and_list`，每个词用 `QUOTED_WORD` 加上引号：`"葱" and "quick"` 和 `“葱”和“quick”`，和 F02 设计 2.6 里的一样。每个词按你输入的样子写出，所以 `TOMATO` 保持大写，`" tomato "` 保留它的空格。与前面某个词完全相同的词不写进这个列表。所以 `search egg egg` 只写一次 `"egg"`，`search egg EGG` 两个都写。词原样显示，不做转义：词里的 `"` 显示为 `"`，词里的换行会把这一行断开。原型的中文这一行对两个词说“同时”，对一个词就读起来不对。所以这一行对一个词有一条提示，对两个或更多词有另一条提示，词数在去掉重复的词之后计算，每条提示都是按菜谱数选择形式的 `Plural`。两条提示的英文文字相同，因为 `and_list` 已经写出了每个词。没有菜谱匹配时，`search` 只写出 `NO_RECIPE_MATCHES` 或 `NO_RECIPE_MATCHES_ALL` 这一行，不写表格，并以 0 退出。没有匹配不是错误，这是原型“No match”的说法。没有原型展示的文字由 Troy 决定（下面的 A 点）。
7. **列宽来自结果里的行。** `search` 不给 `format_table` 传 `min_widths`，所以每一列与它自己的格子一样宽（F02 设计 2.9）。在示例文件夹里，对原型里的几次搜索，用整个文件夹的列宽也会得到相同的表格，因为匹配的行里有最长的 ID `tomato-egg-noodles` 和最长的名称 `Tomato and egg stir-fry` 与 `番茄鸡蛋面`。所以无论哪种做法，原型和 v0.1-S11 都成立。F09 选择 5 让 `list --tag` 用整个列表的列宽，因为 F05 和 F09 的原型把带标签的列表显示为行数更少的整个列表。搜索没有这样一张要对齐的表格：它的最后一列是另一列，每次搜索问的是一个新问题。所以结果窄的表格保持窄，比如 2.2 里的 `search mapo`，`search` 也不量它不显示的菜谱。
8. **`search` 读什么，在哪里停下。** `search` 只读它需要的文件（架构 8），顺序与 `check` 的步骤相同（F07 设计 2.2）：先是目录，然后用 `read_recipes` 读每个菜谱。它不再另外调用 `list_recipe_ids`，因为 `read_recipes` 会先返回列表的问题，再返回各文件的问题（F04 设计 2.7）。所以 `search` 对列表的每个问题只报告一次，和 `list` 一样。它不读常备清单，也不读菜单。它在每个读取函数的第一个错误处用 `stop_at_error` 停下，`stop_at_error` 写出这个问题和 `RUN_CHECK`，并给出 1（架构 6）。它在匹配任何菜谱之前解析每个菜谱，所以任何菜谱文件里的错误都会让它停下，即使那个菜谱本来不会匹配，就像错误会让 `list` 停下一样。`check` 用相同的读取函数、相同的参数读这些文件，所以让 `search` 停下的错误一定在 `check` 的错误里（F07 设计，选择 8）。`search` 不写出警告，警告也从不改变退出码，与 F09 选择 3 相同（架构 6）。各行按 `read_recipes` 的顺序排列，也就是 ID 的顺序，和 `list` 一样（F04 设计 2.5）。`recipes/` 文件夹里没有菜谱文件时没有匹配，所以 `search` 写出选择 6 的那一行，并以 0 退出。`recipes/` 文件夹不存在是列表的错误（F04 设计，选择 6），所以它让 `search` 以退出码 1 停下。`cli` 在运行 `search` 之前检查词的个数、数据文件夹和设置（F05 设计 2.10）。所以数据文件夹不存在时，`search ""` 给出 `NO_DATA_FOLDER` 和退出码 1，和 `show Mapo` 一样。
9. **提示里的数字。** `search` 的提示只显示匹配的菜谱数，即一个元组的长度，以及这些词，即命令行上的文字。5,000 位数字的词是一个 `str`，所以它不会碰到 F02 的 4,300 位限制（F02 设计 2.3）。文件里的问题只通过 `stop_at_error` 写到错误流，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计，选择 2）。所以 `search` 的提示不会碰到这个限制。
10. **速度。** PT01 要求有 1,000 个菜谱时的 `search` 在 Troy 的电脑上在 1 秒内完成，取 5 次运行的中位数（v0.1-S30）。这个用例查找每个菜谱都用到的那种食材的名称，所以 `search` 打印全部 1,000 个菜谱。在 `tests/pt01_support.py` 的 PT01 文件夹里，这就是 `search 食材001`，每一行都匹配于 `ingredient`。`search` 读的与 `list` 相同：`cli` 里的设置、目录、`recipes/` 的一次列表，以及每个菜谱文件各一次。F09 在 Troy 的电脑上的 PT01 基线是：`list` 的中位数 0.789 秒，`show` 的中位数 0.153 秒。在读取之外，`search` 加上匹配和一张更小的表格：
    - 目录里 600 个食材名称和 10 个标签名称的匹配形式每次运行只构建一次，每个词在每个名称里只查找一次。所以对每个词，`search` 在查看任何菜谱之前就知道目录里哪些食材和标签含有它。菜谱的各行和各标签指向目录里的这些值（架构 5.2），所以它们不需要新的匹配形式：菜谱的 12 行食材和 2 个标签各是一次查找。每个菜谱的 2 个名称各构建一次匹配形式。对一个词，一次运行大约构建 2,600 个匹配形式，做 2,600 次 `in` 检查和 14,000 次查找，最多花几百分之一秒。
    - 表格约有 32,000 个字符，每个字符在 `format_table` 里用 `display_width` 量两次。`list` 的表格约有 40,000 个字符，每个量三次。每一行都不运行 `Message.render`：各位置的提示每次运行只渲染一次，每一格是它们的 `comma_list`。

    所以 `search` 的耗时应该与 `list` 差不多。这是根据上述耗时的估计，不是测量结果。F10 在 mock 之前不需要 `[refactor]` 旁支 PR。测试计划可以在 PT01 文件夹上为 `search` 计时，就像 F09-T28 为 `list` 计时一样。如果 `search` 接近上限，第一步是代码审查员在 PR #50 上指出的修改：`Message.render` 每次调用都解析模板的占位符，在 PT01 文件夹上约耗 0.06 秒。这个修改会作为 `[refactor]` PR，在 F10 的实现 PR 之前合入，由架构师判断它是否改变 F02 的接口。

这两点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 没有原型展示这些文字。每一段都沿用某个原型里文字的措辞。建议按 2.2 的写法接受它们。
  - 两个或更多词时的英文这一行，用 `and_list`：`2 recipes match "葱" and "quick".`、`No recipe matches "豆腐" and "quick".` 和 `1 recipe matches "scallion", "QUICK", and "noodle".`。它读起来与原型里一个词的那一行一样。用“both”或“all of”的写法，需要为三个或更多词再加第三条提示。
  - 一个词时的中文这一行，不带“同时”：`2 个菜谱匹配“番茄”。` 和 `没有菜谱匹配“lamb”。`。
  - 一个菜谱时的这一行：`1 recipe matches "mapo".` 和 `1 个菜谱匹配“mapo”。`。
  - 三个词时的中文这一行：`1 个菜谱同时匹配“葱”、“quick”和“面”。`。
  - 英文的位置 `tag` 和中文的位置 `名称`。原型显示了 `name`、`ingredient`、`食材` 和 `标签`。
  - `EMPTY_WORD`：`A word is empty. Look for a name, such as "recipe-menu search tomato".` 和 `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。`。
- **B. 里面什么也没有的词**（选择 4）。
  - 方案 1，推荐：用法错误，退出码 2，`EMPTY_WORD`，在 `search` 读任何文件之前给出。
  - 方案 2：没有匹配，退出码 0，比如 `No recipe matches "".`。F03 设计 2.6 的规则 7 说，匹配形式为空的文字不匹配任何名称。
  - 推荐方案 1 的理由：需求 3 把退出码 2 给了错误的命令行，工具也已经把命令行上的空文字当作错误。`cli` 把选项的空值当作没有值（F05 设计 2.10），`show ""` 是用法错误（F09 选择 7）。按方案 2，`search ""` 会报告没有菜谱匹配，把输入错误藏起来。

没有后续功能在 F10 的基础上构建。F09 的 `UNKNOWN_ID` 的后半句运行 `recipe-menu search`，从 F10 的 mock PR 起这条命令就能运行，从 F10 的实现 PR 起它给出 2.2 的输出。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/search/__init__.py` 和 `messages.py`，可能还有一个内部文件，`src/recipe_menu/cli/_commands.py` 里的那一项，以及 `src/recipe_menu/catalog/__init__.py` 里 `matching_form` 的导出（3.1 节），所以它最多改 5 个文件。它定义每条提示和字段齐全的命令，所以帮助会列出 `search`，命令也能运行。它的 `run` 不读任何文件，也不抛任何异常。比如，它什么也不写并给出 0。所以输出、退出码 1 或带退出码 2 的 `EMPTY_WORD` 的新测试在 mock 上会失败（R09）。这些测试在 mock 上会通过，从而违反 R09：只检查 `SEARCH_COMMAND` 的字段、帮助、某条提示或退出码 0 的测试。只检查 `search` 不改变任何文件的测试也是如此，比如 v0.1-S23 对 `search 番茄` 的检查。检查 `cli` 在运行命令之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、没有词的 `search`、`search --tag quick` 或 `search 番茄 --help`。单独检查 `matching_form` 的测试也会通过，因为 mock 导出的是 F03 已经能用的函数，所以 F10 的测试通过 `search` 用到它。实现（PR 5）在 `search` 的内部文件里读取文件、匹配这些词并写出输出，它在 R03 的 5 个文件以内。

### 2.1 `SEARCH_COMMAND`

- 模块：search
- 功能：对 `search` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 写出 2.2 的结果。

签名：

```python
SEARCH_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("search",)
#   help_line = SEARCH_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WORD_ARGUMENT, repeats=True)
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("search",)`。 | 无 |
| `help_line` | `Message` | `SEARCH_HELP`：“Find recipes by name, ingredient, or tag.”和“按名称、食材或标签找菜谱。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 检查这些词，读取目录和每个菜谱，并写出 2.2 的结果。 | 给出 0 或 1。为空的词抛出 `UsageError`，而且在读取任何文件、写出任何输出之前抛出。遇到坏数据不抛异常。 |
| `argument` | `Argument` | `Argument(WORD_ARGUMENT, repeats=True)`，它是必需的，可以重复。`WORD_ARGUMENT` 是 `WORD` 和 `词`，也就是 F05 原型帮助里的名称。 | 所以 `cli` 传入一个或多个值（F05 设计 2.5）。 |
| `options` | `str` 的元组 | `()`。`search` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `search`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 用 `context.lang`、`context.folder`、`context.out` 和 `context.err`。它不用 `context.settings`，也不用 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `search` 的东西（F05 设计 2.6）。 | `arguments.values` 按命令行的顺序保存这些词，比如 `("葱", "quick")`。它没有选项。 |

- 返回值：`SEARCH_COMMAND`，一个 `Command`。
  - `SEARCH_COMMAND.usage` 英文是 `search WORD...`，中文是 `search 词...`，所以帮助显示它们，用法错误引用 `recipe-menu search WORD...` 或 `recipe-menu search 词...`。
  - `SEARCH_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出输出，并给出 0 或 1。

F10 之后，帮助列出这些命令和选项，第二列从第 19 列之后开始（选择 1）。英文：

```text
Commands:
  init             Create the data folder with example data.
  check            Check every data file for mistakes.
  list             List the recipes.
  show ID          Show one recipe.
  search WORD...   Find recipes by name, ingredient, or tag.

Options:
  --lang en|zh     The language of the output. Default: the settings, else English.
  --data FOLDER    The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version        Show the version.
  --help           Show this help.
```

中文：

```text
命令：
  init             创建数据文件夹和示例数据。
  check            检查每个数据文件有没有错误。
  list             列出菜谱。
  show ID          查看一个菜谱。
  search 词...     按名称、食材或标签找菜谱。

选项：
  --lang en|zh     输出语言。默认：设置里的语言，否则英文。
  --data 文件夹    数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version        显示版本。
  --help           显示这份帮助。
```

错误：

`run` 在读任何文件之前检查这些词。

| 错误 | 何时发生 |
| --- | --- |
| `UsageError(EMPTY_WORD, None)` | 对 `arguments.values` 里的某个词，`matching_form(word)` 为空（选择 4）。 |

- 副作用：与 2.2 相同。`run` 通过 F03 和 F04 的读取函数读取目录和菜谱文件，写入 `context.out` 或 `context.err`，不写任何文件。
- 性能指标：无。PT01 从启动到退出为 `recipe-menu search`（2.2）计时，而它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里是默认设置，输出跟随 `context.lang`。帮助来自 `COMMANDS`，F10 之后它有 `init`、`check`、`list`、`show` 和 `search`。抛出异常的那次调用不向任何流写出一行。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SEARCH_COMMAND.words == ("search",)
assert SEARCH_COMMAND.usage == BiText("search WORD...", "search 词...")
assert SEARCH_COMMAND.help_line.render(Lang.EN) == "Find recipes by name, ingredient, or tag."
assert SEARCH_COMMAND.help_line.render(Lang.ZH) == "按名称、食材或标签找菜谱。"
assert SEARCH_COMMAND.argument == Argument(Message("WORD", "词"), repeats=True)
assert SEARCH_COMMAND.options == ()
assert SEARCH_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert SEARCH_COMMAND.run(context, Arguments(("葱", "quick"))) == 0
assert out.getvalue().splitlines() == [
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     食材、标签",
    "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
    "",
    "2 个菜谱同时匹配“葱”和“quick”。",
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
assert len(english) == 18
assert english[4:10] == [
    "Commands:",
    "  init             Create the data folder with example data.",
    "  check            Check every data file for mistakes.",
    "  list             List the recipes.",
    "  show ID          Show one recipe.",
    "  search WORD...   Find recipes by name, ingredient, or tag.",
]
assert english[12].startswith("  --lang en|zh     The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[9] == "  search 词...     按名称、食材或标签找菜谱。"
assert chinese[13].startswith("  --data 文件夹    数据文件夹。")

SEARCH_COMMAND.run(context, Arguments(("番茄", "\u3000")))  # raises UsageError
```

### 2.2 `recipe-menu search`

- 模块：search
- 功能：查找菜谱的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 2，以及 [4](../../requirements.zh-CN.md#4-功能点)）。它列出每个词都能在菜谱名、食材名或标签名里匹配上的菜谱，中英文都算，并写明每个菜谱匹配在哪里。F10 原型展示了它。

签名：

```text
recipe-menu search WORD... [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `WORD` | 文字 | 要查找的词，比如 `番茄`、`TOMATO` 或 `quick`。 | 一个或多个词（F05 设计 2.5）。每个词的匹配形式不为空（选择 4）。以 `--` 开头的词是选项（F05 设计 2.10）。 |
| `--lang` | `en` 或 `zh` | 输出和每条提示的语言。 | 按 F05 设计 2.10。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 文件夹 | 数据文件夹。 | 按 F05 设计 2.10。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `search`。 | 无 |

`search` 按顺序执行这些步骤。第 1 步不读文件，每个读文件的步骤都用前面步骤给出的东西。

1. 它按顺序检查这些词，对第一个 `matching_form` 为空的词抛出 `UsageError(EMPTY_WORD, None)`。
2. `read_catalog(context.folder)` 给出 `catalog` 和它的问题（F03 设计 2.8）。问题里有错误时，`search` 对第一个错误给出 `stop_at_error(context, error)`。
3. `read_recipes(context.folder, catalog)` 给出 `recipes` 和它们的问题（F04 设计 2.7）。问题里有错误时，`search` 用 `stop_at_error` 在第一个错误处停下。
4. 对 `recipes` 里的每个菜谱，按它们的顺序，`search` 按下表找出每个词的位置。每个词都至少有一个位置时，它保留这个菜谱。
5. 它把下面的输出写到输出流，并给出 0。

第 2 步和第 3 步的警告不改变任何东西（选择 8）。

`matching_form(word) in matching_form(text)` 为真时，词出现在这段文字里（选择 4）。词在菜谱里的位置如下，按这个顺序：

| 位置 | 提示 | 词出现在这些文字之一里 |
| --- | --- | --- |
| 名称 | `NAME_PLACE` | `recipe.name.en` 和 `recipe.name.zh`，各自不为 `None` 时。 |
| 食材 | `INGREDIENT_PLACE` | `recipe.ingredients` 里每个 `line` 的 `line.ingredient.name.en` 和 `line.ingredient.name.zh`。 |
| 标签 | `TAG_PLACE` | `recipe.tags` 里每个 `tag` 的 `tag.name.en` 和 `tag.name.zh`。 |

计数行里的词是命令行上的词，按它们的顺序，去掉每个与前面某个词完全相同的词（选择 6）。下面的“一个词”和“两个或更多词”数的就是这些词。

- 返回值：退出码，以及写在对应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | `search` 写出了它的结果，包括没有菜谱匹配时。 | 输出流：表格和计数行，或者没有菜谱匹配时的一行。 |
| 1 | 某个文件有错误。 | 错误流：`stop_at_error` 的三行。输出流上什么也没有。 |
| 2 | 某个词是空的。 | 错误流：`cli` 写出的提示，不带下一行。输出流上什么也没有。 |

有一个或多个菜谱匹配时，输出是这些行，按这个顺序，每行以换行结束：

1. `format_table(rows)` 的各行，没有缩进，用默认间距 3，不带 `min_widths`（F02 设计 2.9，选择 7）。
2. 一个空行。
3. 计数行：一个词时是 `RECIPES_MATCH`，两个或更多词时是 `RECIPES_MATCH_ALL`，都按匹配的菜谱数选择形式。

`rows` 是表头行，然后是每个匹配的菜谱的一行：

| 列 | 表头 | 单元格 |
| --- | --- | --- |
| ID | `ID_HEADING` | `recipe.id` |
| 名称 | `NAME_HEADING` | `recipe.name.get(context.lang)` |
| 匹配于 | `MATCHED_IN_HEADING` | 菜谱各位置提示的 `comma_list`，每条提示作为它的 `BiText`，按位置表的顺序，再取 `.get(context.lang)`：`name, ingredient` 和 `食材、标签`（选择 5）。 |

`search` 按文件里的样子写出每个名称，所以 `format_table` 的规则对它适用，比如带换行的名称会占两行。

没有菜谱匹配时，输出只有一行：一个词时是 `NO_RECIPE_MATCHES`，两个或更多词时是 `NO_RECIPE_MATCHES_ALL`（选择 6）。

`search` 的提示如下。`RECIPES_MATCH` 和 `RECIPES_MATCH_ALL` 是 `Plural` 值（F02 设计 2.4），按 `count` 选择。`NAME_PLACE`、`INGREDIENT_PLACE` 和 `TAG_PLACE` 每次运行用 `to_bitext` 渲染一次（选择 10）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `SEARCH_HELP` | `Find recipes by name, ingredient, or tag.` | `按名称、食材或标签找菜谱。` |
| `WORD_ARGUMENT` | `WORD` | `词` |
| `ID_HEADING` | `ID` | `ID` |
| `NAME_HEADING` | `Name` | `名称` |
| `MATCHED_IN_HEADING` | `Matched in` | `匹配于` |
| `NAME_PLACE` | `name` | `名称` |
| `INGREDIENT_PLACE` | `ingredient` | `食材` |
| `TAG_PLACE` | `tag` | `标签` |
| `QUOTED_WORD` | `"{word}"` | `“{word}”` |
| `RECIPES_MATCH`，一个时 | `{count} recipe matches {words}.` | `{count} 个菜谱匹配{words}。` |
| `RECIPES_MATCH`，多个时 | `{count} recipes match {words}.` | `{count} 个菜谱匹配{words}。` |
| `RECIPES_MATCH_ALL`，一个时 | `{count} recipe matches {words}.` | `{count} 个菜谱同时匹配{words}。` |
| `RECIPES_MATCH_ALL`，多个时 | `{count} recipes match {words}.` | `{count} 个菜谱同时匹配{words}。` |
| `NO_RECIPE_MATCHES` | `No recipe matches {words}.` | `没有菜谱匹配{words}。` |
| `NO_RECIPE_MATCHES_ALL` | `No recipe matches {words}.` | `没有菜谱同时匹配{words}。` |
| `EMPTY_WORD` | `A word is empty. Look for a name, such as "recipe-menu search tomato".` | `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `count` | 匹配的菜谱数，即一个元组的长度（选择 9）。 |
| `words` | 对计数行里的每个词，按顺序取 `QUOTED_WORD.to_bitext(word=word)`，再取它们的 `and_list`：`"葱" and "quick"` 和 `“葱”和“quick”`。 |
| `word` | 一个词，按你输入的样子。 |

按这些规则，可以得出 F10 原型里的各行，比如 `2 recipes match "TOMATO".` 和 `没有菜谱同时匹配“豆腐”和“quick”。`。

错误：

`cli` 在运行 `search` 之前报告命令行上的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 2，`EMPTY_WORD`，不带下一行：`A word is empty. Look for a name, such as "recipe-menu search tomato".` | 某个词的匹配形式为空（第 1 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行 | 目录、`recipes/` 的列表或某个菜谱文件有错误（第 2 步和第 3 步）。 |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT`，或者是设置的第一个错误和 `RUN_CHECK` | 数据文件夹不是文件夹，或者设置有错误。因为 `search` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查这两点。 |
| 退出码 2，先是 `TOO_FEW_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`An argument is missing. Write "recipe-menu search WORD...".` | 命令行上没有词。 |
| 退出码 2，先是没有选项时的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"search" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。不再写出任何东西（F05 设计 2.10）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `search` 把 `catalog.toml` 读一次，把 `recipes/` 列一次，把每个菜谱文件读一次，都通过 F03 和 F04 的读取函数。遇到空的词时，它不读任何文件。它不读 `pantry.toml`，也不读菜单。它写入输出流或错误流。它不写任何文件，所以每个文件和文件夹都保持原来的字节和修改时间（v0.1-S23）。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹。前五次运行给出 F10 原型的五段输出，和 v0.1-S11 的运行一样。后面的运行展示选择 3 到 8 的规则。`mapo-tofu` 里的一个错误让 `search` 停下，没有菜谱文件的文件夹给出一行。

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


TOMATO = [
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
    "",
]
assert run(folder.root, "search", "番茄") == (0, [*TOMATO, '2 recipes match "番茄".'], [])
assert run(folder.root, "search", "TOMATO") == (0, [*TOMATO, '2 recipes match "TOMATO".'], [])
assert run(folder.root, "search", "葱", "quick", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg           番茄炒蛋     食材、标签",
        "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
        "",
        "2 个菜谱同时匹配“葱”和“quick”。",
    ],
    [],
)
assert run(folder.root, "search", "lamb") == (0, ['No recipe matches "lamb".'], [])
assert run(folder.root, "search", "豆腐", "quick", "--lang", "zh") == (
    0,
    ["没有菜谱同时匹配“豆腐”和“quick”。"],
    [],
)

assert run(folder.root, "search", "番茄", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg           番茄炒蛋     名称、食材",
        "tomato-egg-noodles   番茄鸡蛋面   名称、食材",
        "",
        "2 个菜谱匹配“番茄”。",
    ],
    [],
)
assert run(folder.root, "search", "mapo") == (
    0,
    [
        "ID          Name        Matched in",
        "mapo-tofu   Mapo tofu   name",
        "",
        '1 recipe matches "mapo".',
    ],
    [],
)
assert run(folder.root, "search", "pork") == (
    0,
    [
        "ID                 Name                     Matched in",
        "mapo-tofu          Mapo tofu                ingredient",
        "red-braised-pork   Red-braised pork belly   name, ingredient",
        "",
        '2 recipes match "pork".',
    ],
    [],
)
assert run(folder.root, "search", "and egg") == (
    0,
    [
        TOMATO[0],
        "tomato-egg           Tomato and egg stir-fry   name",
        "tomato-egg-noodles   Tomato and egg noodles    name",
        "",
        '2 recipes match "and egg".',
    ],
    [],
)
assert run(folder.root, "search", "scallion", "QUICK", "noodle") == (
    0,
    [
        "ID                   Name                     Matched in",
        "tomato-egg-noodles   Tomato and egg noodles   name, ingredient, tag",
        "",
        '1 recipe matches "scallion", "QUICK", and "noodle".',
    ],
    [],
)
assert run(folder.root, "search", "葱", "quick", "面", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签",
        "",
        "1 个菜谱同时匹配“葱”、“quick”和“面”。",
    ],
    [],
)
assert run(folder.root, "search", "egg", "egg") == (0, [*TOMATO, '2 recipes match "egg".'], [])
both = [*TOMATO, '2 recipes match "egg" and "EGG".']
assert run(folder.root, "search", "egg", "EGG") == (0, both, [])
spaced = [*TOMATO, '2 recipes match "\u3000番茄".']
assert run(folder.root, "search", "\u3000番茄") == (0, spaced, [])

# A note, a step, a category, and an ID do not count.
for word in ("wedges", "切块", "scramble", "dairy", "tomato-egg"):
    assert run(folder.root, "search", word) == (0, [f'No recipe matches "{word}".'], [])
# A fullwidth letter and a no-break space inside a word count as written.
for word in ("\uff34omato", "tomato\u00a0and"):
    assert run(folder.root, "search", word) == (0, [f'No recipe matches "{word}".'], [])

empty = ['A word is empty. Look for a name, such as "recipe-menu search tomato".']
for words in ([""], ["番茄", "\u3000"], [" ", "lamb"]):
    assert run(folder.root, "search", *words) == (2, [], empty)
empty_zh = ["有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。"]
assert run(folder.root, "search", "", "--lang", "zh") == (2, [], empty_zh)
code, out, err = run(folder.root, "search")
assert (code, out) == (2, [])
assert err == [
    'An argument is missing. Write "recipe-menu search WORD...".',
    'Run "recipe-menu --help" to see the commands.',
]
code, out, err = run(folder.root, "search", "番茄", "--tag", "quick")
assert (code, out) == (2, [])
assert err == [
    '"search" has no option "--tag". It has no options of its own.',
    'Run "recipe-menu --help" to see the options.',
]

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "search", "番茄") == (1, [], stopped)
assert run(folder.root, "search", "") == (2, [], empty)

for path in folder.recipes.iterdir():
    path.unlink()
assert run(folder.root, "search", "番茄") == (0, ['No recipe matches "番茄".'], [])
```

## 3. 对已有接口的修改

F10 给 F03 的 `catalog` 的接口增加一个名称（3.1）。这个名称是 `catalog` 已经在用的函数，所以 F03 实现的东西都不改变签名或行为，F03 的测试不用修改也能通过。F01、F02、F04、F05 和 F09 的接口都不改变。`browse` 保持它的两个导出（选择 2）。需求不改变，所以没有 `[docs]` PR 批准这项修改。架构师在这份设计里审查它，就像 F04 和 F05 在它们的第 3 节里给 `datafile` 增加名称时一样。

F10 还在 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS` 里增加一项，这个文件是 `cli` 的内部文件，架构 4 允许每个命令功能这样做。有了这一项，真正的 `recipe-menu` 的帮助会列出 `search`，两张表的第二列从第 19 列之后开始，而不是第 18 列之后（选择 1）。运行真正的 `COMMANDS` 的测试只检查仍然成立的行和列：

- F05-T48 检查中文帮助的第一行和最后一行，F05-T49 不检查帮助的任何一行。
- F07-T17 检查 `check` 那一行以它的文字结尾，而且这段文字的起始列与 `--lang en|zh` 的文字的起始列相同。
- F08-T14 对 `init` 那一行做同样的检查，并检查它后面紧跟 `check` 那一行。
- F09-T01 检查 `list` 和 `show` 两行紧跟在 `check` 那一行后面，而且它们的文字从同一列开始。F09-T19 和 F09-T25 检查 `list --help` 和 `show ... --help` 给出与 `--help` 相同的帮助。

列从 18 移到 19 时，这些检查都成立。F07-T01、F08-T14 和 F09-T01 也比较一整段帮助，但每个都给 `main` 传入自己的命令，F10 不改变那些命令。

F10 按这些接口的设计使用它们，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural`、`and_list`、`comma_list` 和 `format_table`。
- F03 的 `DataFolder`、`Problem`、`Catalog`、`Ingredient`、`Tag` 和 `read_catalog`。
- F04 的 `Recipe`、`RecipeIngredient` 和 `read_recipes`。
- F05 的：`app` 里的 `Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error` 和 `stop_at_error`，以及 `cli` 里的 `COMMANDS`。

### 3.1 `matching_form`

- 模块：catalog
- 功能：F03 设计 2.6 的匹配形式，`Catalog`、`read_catalog` 和 `read_pantry` 已经用它比较名称。`catalog` 导出它，让 `search` 按同一条大小写规则比较词和名称，也没有模块另写一份，这是架构师在 F03 审查里的要求。`src/recipe_menu/catalog/__init__.py` 从 `src/recipe_menu/catalog/_matching.py` 引入它，并在 `__all__` 里列出它。这个函数和它的文档注释保持原样，`is_blank` 仍只在模块内部使用。

签名：

```python
def matching_form(text: str) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 按原样写的文字，比如名称或命令行上的词。 | 任何字符串。 |

- 返回值：`text` 的匹配形式：按 `str.strip()` 的方式去掉两端空白的文字，其中每个 A 到 Z 的 ASCII 大写字母换成对应的小写字母。按 F03 设计 2.6 的规则 1 到 6，其他都不改变：文字中间的空白按原样计算，形似的字母保持原样，文字不做规范化，汉字保持原样。两段文字的匹配形式相等时，它们相互匹配。词的匹配形式是一段文字的匹配形式的一部分时，词出现在这段文字里（选择 4）。

错误：无

- 副作用：无
- 性能指标：无。`search` 在一次运行里对目录的每个名称、菜谱的每个名称和每个词各调用它一次（选择 10）。

示例：

```python
from recipe_menu.catalog import matching_form

assert matching_form(" TOMATO\t") == "tomato"
assert matching_form("\u3000番茄") == "番茄"
assert matching_form("Choy  Sum") == "choy  sum"
assert matching_form("\u212aale") == "\u212aale"  # U+212A KELVIN SIGN
assert matching_form("\uff34omato") == "\uff34omato"  # U+FF34 FULLWIDTH LATIN CAPITAL LETTER T
assert matching_form("\u3000") == ""
assert matching_form("egg") in matching_form("Eggplant")
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `search` 是架构 3 里的那个模块：文件夹 `src/recipe_menu/commands/search/`，它的 `__init__.py` 在 `__all__` 里只列出 `SEARCH_COMMAND`，提示放在它自己的 `messages.py` 里（架构 8）。它引用 `app`、`lang`、`text`、`datafile`、`catalog` 和 `recipes`，它那一行允许这些模块，架构师按第 2 节建的模型也不需要别的模块。选择 2 让架构 4 里从 `search` 到 `browse` 的箭头不被使用，规则允许这样，所以架构不需要修改。`cli` 里唯一的改动是 `COMMANDS` 里 `SHOW_COMMAND` 后面的那一项（架构 4），`cli` 可以引用 `search`。选择 3 按架构 5.2 和 5.3 使用数据模型：每个 `RecipeIngredient` 都指向目录里的那个 `Ingredient` 本身，它有两个名称；菜谱的每个标签都是目录里的一个 `Tag`。所以选择 10 为每个词建立的目录食材和标签集合，给出的位置与逐行检查名称的结果相同。`search` 不增加值类型，不在模块级保存状态，它的匹配形式只在一次运行里存在（架构 8）。它读的正是架构 8 给 `search` 的文件：`cli` 里的设置、目录和每个菜谱，不读常备清单，也不读菜单（选择 8）。从 `catalog` 导出 `matching_form`（3.1 节）是共用 F03 大小写规则的正确做法。这条规则属于按名称查找食材和标签，架构 3 把这件事给了 `catalog`，而 `search` 可以引用 `catalog`。把这个函数移到 `text` 或 `lang`，会为一条只有名称才用的规则修改 F02 的基础模块。在 `Catalog` 上加一个给出含有某个词的名称的方法，会把 `search` 的一部分移进 `catalog`，而且它管不到菜谱名，因为菜谱名不在 `catalog` 里。F03 的审查要的就是这个导出。 |
| 遵守错误处理和命名约定 | 通过 | 退出码遵守架构 1 和 6。`search` 写出结果时给出 0，没有匹配时也是，和原型“No match”显示的一样。目录、`recipes/` 的列表或某个菜谱文件有错误时，它通过 `first_error` 和 `stop_at_error` 给出 1。对空的词，`run` 在读任何文件、写出任何输出之前抛出 `UsageError(EMPTY_WORD, None)`，这是 `Command.run` 的要求（F05 设计 2.5），`cli` 把它变成 2。`EMPTY_WORD` 已经说了该写什么，所以不带下一行（ADR-0008）。警告不改变任何东西（架构 6）。结果写到 `context.out`，错误写到 `context.err`（架构 6 和 8）。命名遵守架构 8：模块用命令的名称，提示是 `messages.py` 里 UPPER_SNAKE 的 `Message` 和 `Plural` 常量。列表来自 `and_list` 和 `comma_list`，复数来自 `Plural`，表格来自 `format_table`，没有模块自己拼。选择 9 成立：提示里唯一的数字是菜谱数，词是 `str`，所以 F02 的 4,300 位限制用不上。模型写出 5,000 位数字的词时没有出错。B 点：架构师同意方案 1。空的词是错误的参数值，需求 3 和架构 6 给它退出码 2，就像 F09 对 `show ""` 的处理。F03 的规则 7 讲的是相等的名称。按 `in` 比较时，空文字出现在每段文字里，所以方案 2 需要自己的特例，还会把输入错误藏起来。A 点不涉及架构，架构师同意它的建议：每段新文字都是两种语言的 `Message` 或 `Plural`，其中的列表来自 `and_list`。 |
| 不和已有接口重复 | 通过 | `search` 调用 `matching_form`、`read_catalog`、`read_recipes`、`first_error`、`stop_at_error`、`format_table`、`and_list`、`comma_list`、`Plural.pick`、`Message.to_bitext` 和 `BiText.get`，没有重写其中任何一个。导出 `matching_form` 让工具里的名称只有一条大小写规则，这是 F03 审查的要求。选择 2 重复了 `browse` 两条提示的文字，`ID_HEADING` 和 `NAME_HEADING`。它们是内部提示，不是接口，架构 8 让每个模块把自己的提示放在自己的 `messages.py` 里。导出它们会为两段短文字给 F09 已实现的接口增加两个名称，所以架构师同意选择 2 和它写明的代价。`search` 还会重复 `browse` 内部 `read_catalog_or_stop` 的几行代码。这几行调用 F05 共用的 `first_error` 和 `stop_at_error`，所以 `search` 没有重复任何接口。`search` 不增加读取函数。 |
| 只依赖排序在前面的功能 | 通过 | F10 使用 F01 和 F02 的 `lang` 和 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`，以及 F05 的 `app` 和 `cli`。它们都排在 F10 前面，都在 main 上通过了测试。F05 是 F10 那一行的硬依赖，F03 和 F04 是软依赖。第三个软依赖 F09 只提供 `UNKNOWN_ID` 后半句的文字，F10 不从 `browse` 引用任何东西。F02 不在那一行里，但它排在使用它的 F03 前面。没有后续功能在 F10 的基础上构建。F10 只需要标准库，所以 R16 没有要审查的东西。`docs/rules.md` 里没有类型为 Review、由架构师执行的 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写明了模块之间的每个假设。加入 `SEARCH_COMMAND` 会让帮助的第二列从第 18 列之后移到第 19 列之后，因为 `cli` 按 `COMMANDS` 确定帮助的宽度（F05 设计 2.9），第 3 节列出了检查真正帮助的测试。架构师运行测试检查了这个说法。把模型放进仓库的一份副本后，main 的全部测试在 Troy 的电脑上是 462 个通过、3 个跳过，这 3 个就是 main 上只在 Windows 跳过的用例。所以 F05-T48、F05-T49、F07-T17、F08-T14、F09-T01、F09-T19、F09-T25 和其他每个测试都仍然成立。选择 10 的查找依据架构 5.2：菜谱指向目录里的 `Ingredient` 值本身，所以 `recipes` 和 `search` 之间没有出现新的约定。F09 的 `UNKNOWN_ID` 后半句只以文字的形式提到 `search`。按选择 3，这句提示靠名称里的一个词找到菜谱，比如 `mapo`，对 `tomato-eggs` 这样的拼写错误什么也找不到，选择 3 写明了这一点。给 Troy 的一点说明，不阻塞：如果搜索也要匹配 ID，ID 就成了第四个位置，这需要走需求变更流程。架构师不建议在 v0.1 里这样做。 |
| 修改已实现的接口时走了变更流程 | 通过 | 对已实现接口的唯一修改，是 F03 的 `catalog` 新导出的 `matching_form`（3.1 节）。这个函数、它的签名、行为和文档注释都保持原样，所以 F03 的测试不用修改也能通过，模型的测试运行证实了这一点。需求不改变，所以不需要 `[docs]` PR，架构师在这里审查这项增加，就像审查 F04 和 F05 在它们的第 3 节里给 `datafile` 增加的名称一样。`browse` 和其他每个接口都保持原样，`COMMANDS` 里的那一项是 `cli` 的内部内容，架构 4 允许每个命令功能这样做。mock 计划是对的。mock 包含 `search/__init__.py`、`search/messages.py`、最多一个带 `run` 的内部文件（这个 `run` 什么也不写并给出 0）、`cli/_commands.py` 里的那一项，以及 `catalog/__init__.py` 里的导出。这最多是 5 个文件，远少于 500 行（R03）。导出和那一项应当放在 mock 里，这样测试能引用 `matching_form`，并通过 `main` 运行 `search`。匹配和输出应当放在实现里，实现只改 `search` 的内部文件，所以也在 R03 以内。这样，输出、退出码 1 或 `EMPTY_WORD` 的每个新测试在 mock 上都会失败（R09），设计也列出了会在 mock 上通过的测试。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞的问题。架构师检查了每个文件里的 5 个 `python` 代码块：每个都能解析，并且与镜像相同。它在仓库的一份副本里按第 2 节建了模型，把 `SEARCH_COMMAND` 放进 `COMMANDS` 并导出 `matching_form`，然后在 Python 3.13.18 里、在 `tests/data/example/` 的一份新副本上运行 2.1、2.2 和 3.1 的示例。每个断言和 `# raises` 都成立。其中包括第二列从第 19 列之后开始的帮助行、`search pork`、`search mapo`、`search scallion QUICK noodle`、把 `mapo-tofu.toml` 里的 `郫县` 删掉之后的三行，以及之后 `search ""` 的退出码 2。其他运行证实了选择 4、6 和 8 的文字。`search -x` 和由 U+200B 组成的词什么也找不到，并以 0 退出。带 `"` 和换行的词按输入的样子写出。数据文件夹不存在时，`search ""` 给出 `NO_DATA_FOLDER` 和退出码 1。`recipes/` 不存在时 `search` 以退出码 1 停下，`search 番茄 --help` 写出 18 行帮助。在 `tests/pt01_support.py` 生成的 PT01 文件夹上，`search 食材001` 写出 1,000 行、每行都匹配于 `ingredient`，以及 `1000 recipes match "食材001".` 这一行。在 Troy 的电脑上用 `python -m recipe_menu` 轮流把两个命令各运行 5 次，`search` 的中位数是 0.789 秒（0.785 到 0.802 秒），`list` 是 0.794 秒（0.791 到 0.794 秒）。所以选择 10 的估计成立，比上限少约 0.2 秒，不需要先做 `[refactor]` 旁支 PR。 | 通过。架构师同意 A 点和 B 点的建议，这两点由 Troy 在批准这份设计时决定。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-13 | 初稿。 |
| 1.0 | 2026-11-13 | Troy 批准。 |
