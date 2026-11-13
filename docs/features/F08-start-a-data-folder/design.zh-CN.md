---
troy-doc: "F08-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-13"
status: "Troy 已于 2026-11-13 批准"
mirror-of: "design.md"
---

# F08 创建数据文件夹：接口设计

## 1. 功能

- 编号和名称：F08 创建数据文件夹
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F03、F04、F07

## 2. 接口

F08 在 `src/recipe_menu/commands/init/` 里构建命令模块 `init`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.init` 只导出一个名称 `INIT_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出这个名称。你输入的命令是 `recipe-menu init`（2.2）。它的提示放在 `src/recipe_menu/commands/init/messages.py` 里，示例文件的文字放在 `src/recipe_menu/commands/init/_example.py` 里。这两个文件都只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F08 还给 `datafile` 加入第一个写文件的接口：`create_data_folder` 和它的结果，即带有一个 `CreationOutcome` 的 `Creation`（第 3 节）。F08 在它的 mock PR 里把 `INIT_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `CHECK_COMMAND` 前面。这一项是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F08 原型 `docs/prototypes/F08-init.md` 展示了这个命令。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F08 提供的接口 |
| --- | --- |
| `recipe-menu init` 创建数据文件夹，里面有设置、示例数据里的目录和常备清单、示例菜谱 `tomato-egg`，以及空文件夹 `menus/` 和 `shopping/`。 | `recipe-menu init`（2.2）。`INIT_COMMAND`（2.1）里的 `run` 把文件夹 `recipes/`、`menus/` 和 `shopping/` 以及选择 2 的四段文字交给 `create_data_folder`（3.2）。 |
| 设置里的语言就是运行 `init` 时用的语言。 | `settings.toml` 的 `language` 一行写的是 `context.lang`（选择 6）。 |
| 文件夹里已有文件时，它拒绝执行。 | 按选择 4 的规则给出的 `CreationOutcome.HOLDS_FILES` 和 `CreationOutcome.NOT_A_FOLDER`（3.1）。`init` 写出 `ALREADY_HOLDS_FILES` 或 `IS_A_FILE`，并以退出码 1 退出（2.2）。 |
| `check` 对它创建的内容不报告任何错误。 | 这些文件就是示例数据的文件，`tests/data/example/` 里也有它们（选择 2）。`check` 对它们报告 `No errors. No warnings.`，有 1 个菜谱和 0 个周菜单（F07 设计第 2 节，v0.1-S01）。 |
| `init` 只在没有文件的地方创建文件，否则拒绝执行（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | `create_data_folder` 只往不存在或空的数据文件夹里写，并用独占模式打开每个文件（3.2，[架构 6](../../architecture.zh-CN.md#6-错误处理)）。 |
| 按 Ctrl+C 之后不留下写了一半的文件（架构 6）。 | 失败或被打断之后，`create_data_folder` 删除它创建的东西（选择 5）。 |

下面每个接口都遵守这些规则：

- `init` 在包内只引用 `app`、`lang`、`text`、`datafile` 和 `settings`。架构 3 里它那一行允许这些模块，其他模块它都不需要。`datafile` 新增的部分只引用 `lang` 和 `text`（架构 3 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `init` 只通过 `create_data_folder` 访问磁盘，它是 F08 里唯一会列出、创建或删除东西的接口。只有 `datafile` 打开数据文件（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。`init` 不读任何数据文件。数据文件夹是文件夹时，`cli` 在启动时读取 `settings.toml`（F05 设计 2.10）。`init` 只写入 `context.out` 和 `context.err`。它自己不读取外部世界的任何东西，也不保存状态。
- 拒绝执行和磁盘上的失败都是值，从来不是异常。`create_data_folder` 把每个 `OSError` 变成结果里的一个 `Problem`（架构 6）。下面“错误”表里的异常来自错误的调用，都是 bug。
- `INIT_COMMAND` 是一个冻结的 `Command`（F05 设计 2.5）。`Creation` 是带 `slots=True` 的冻结 dataclass，`CreationOutcome` 是枚举（架构 8）。它们是辅助值，就像 F03 加入的 `Severity` 和 F05 加入的 `FolderUse`。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F08 的接口都没有性能指标。PT01 不给 `init` 计时（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。`init` 最多创建数据文件夹、它上面缺少的文件夹、三个文件夹和四个文件。`run` 和 `create_data_folder` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和 3.2 给出它们的规则。

1. **`init` 在帮助里排第一。** `COMMANDS` 里先是 `INIT_COMMAND`，然后是 `CHECK_COMMAND`，按 F05 设计第 2 节的顺序：init、check、list、show、search、menu new、menu show 和 shop。最宽的第一格仍然是 `--data FOLDER` 或 `--data 文件夹`，占 13 列，所以第二列从第 18 列之后开始，和 F07 设计选择 1 一样。帮助多了一行，一共 15 行。有 v0.1 的八个命令时，帮助给出 F05 原型的两段帮助输出（v0.1-S19）。`recipe-menu --help` 和 `recipe-menu --help --lang zh` 里的命令是这些行：

   ```text
   Commands:
     init            Create the data folder with example data.
     check           Check every data file for mistakes.
   ```

   ```text
   命令：
     init            创建数据文件夹和示例数据。
     check           检查每个数据文件有没有错误。
   ```

2. **示例文件是代码里的文字。** `_example.py` 保存四个字符串常量。每个常量都是 `docs/prototypes/example-data.md` 里一个代码块的文字，每行末尾有一个换行：`settings.toml`、`catalog.toml`、`pantry.toml` 和 `recipes\tomato-egg.toml`。设置的文字是一个模板，用来填写它的 `language` 一行（选择 6）。`init` 通过 `datafile` 写出这些文字，这正是架构 2 的安排：“代码按模板生成文本，经 `datafile` 写出。”这些文字不作为包里的数据文件发布。那样的文件需要 `importlib.resources`、一次在运行时可能失败的读取，以及 `pyproject.toml` 里一项容易漏掉的配置。所以 `pyproject.toml` 不变，R16 也没有要标记的东西。这些文字里没有反斜杠，所以 Python 字符串能按原样保存每一段。`tests/data/example/` 里有同样的四段文字，旁边还有另外六个菜谱和一个菜单（架构 10）。两份副本是有意的。示例文件夹是测试数据，开发工程师从不修改它（R08），F03 到 F07 的测试都读它。`init` 的文字是源代码，归开发工程师所有。F08 的一个测试运行 `init`，把它写出的每个文件和 `tests/data/example/` 里的同一个文件逐字节比较，后者按 UTF-8 读取，换行统一为 LF（2.2 的示例）。v0.1-S01 把这些文件和 `example-data.md` 本身比较。所以只改一份副本会让测试失败。
3. **由 `datafile` 写出文件。** 架构 3 把写文件交给 `datafile`，架构 8 也只允许 `datafile` 打开数据文件。F08 是第一个写文件的功能，所以它加入 `create_data_folder`（3.2）。`init` 需要磁盘做的事都由它完成：它查看数据文件夹，创建文件夹和文件，失败后再把它们删除。`init` 传入 `DataFolder` 给出的路径和各段文字。所以 `datafile` 不知道任何示例数据，`init` 也不知道任何文件名（架构 5.2）。`create_data_folder` 把文件夹和文件作为参数，所以测试可以让它在任何一步失败，比如用一个两种系统都不接受的文件名（3.2 的示例）。
4. **“已有文件”的意思。** `create_data_folder` 在创建任何东西之前先查看数据文件夹（3.2）。第一个符合的情况决定结果：
   - 数据文件夹是一个文件夹。`init` 列出它的内容，列不出来时，比如没有访问权限，就是一次失败（选择 5）。只要有任何一种条目，`init` 就用 `ALREADY_HOLDS_FILES` 拒绝执行：文件、文件夹、只有一个空的 `menus\` 这样的空文件夹、链接，或者 `.keep`、`desktop.ini` 这样的隐藏文件或系统文件。所以 `init` 从不把它的文件和你的文件混在一起，也从不需要决定保留哪个条目（待定问题 B）。没有任何条目时，`init` 往这个文件夹里写，所以你可以先在资源管理器里建好文件夹。
   - 这个路径上有一个不是文件夹的东西，比如一个文件，或者一个不指向任何文件夹的链接。`init` 用 `IS_A_FILE` 拒绝执行。
   - 这个路径上什么都没有。`init` 从上往下创建数据文件夹和它上面每个缺少的文件夹。所以只有 `D:\OneDrive` 存在时，`init --data D:\OneDrive\Food\recipe-menu` 会创建 `Food` 和 `recipe-menu`（待定问题 C）。
5. **要么全部完成，要么什么都不留下。** 数据文件夹不存在时，`create_data_folder` 先创建它，然后创建 `recipes\`、`menus\` 和 `shopping\`，再创建 `settings.toml`、`catalog.toml`、`pantry.toml` 和 `recipes\tomato-egg.toml`。它用独占模式打开每个文件，所以从不覆盖文件（架构 6）。第一个 `OSError` 让它停下。然后它从最后创建的开始，删除它创建的东西，`init` 报告这个错误和 `init changed nothing.`，并以退出码 1 退出。文件从打开的那一刻起就算已创建，所以写了一半的文件也会被删除。调用之前就有的东西都不删除：原来就空着的数据文件夹会留下，它上面的文件夹也会留下。Ctrl+C 会执行同样的删除，然后 `cli` 以 130 退出，不再写出任何内容（F05 设计 2.10）。删除也可能失败，比如另一个程序正打开着一个新文件。这时 `init` 写出 `LEFT_BEHIND`，请你清空数据文件夹，然后再运行 `init`。进程被结束时，比如你关掉了终端窗口，或者电脑断电时，删除无法执行。有两种 Ctrl+C 的情况和进程被结束一样。如果 Ctrl+C 发生在系统已经创建了文件夹或文件、但调用还没记下它的时候，比如在 `open` 内部，这个条目会留下来。删除过程中再按一次 Ctrl+C，会让删除停下。这两种情况下 `cli` 仍以 130 退出，不再写出任何内容。在这些情况之后，数据文件夹里可能留下 `init` 创建的东西。这样的文件夹里有条目时，`init` 会拒绝它，`check` 会写出缺少的文件，所以你删除这个文件夹，再运行 `init`。
6. **设置和描述它的那一行。** `settings.toml` 是示例的文字，只是 `language` 一行写的是 `context.lang` 的值：`language = "en"` 或 `language = "zh"`，后面的空格和注释不变。`read_settings` 读这个文件，给出 `Settings(context.lang)`：`init` 的语言、午餐和晚餐，以及 2 份。输出里 `settings.toml` 那一行描述的就是这个值，这正是 F05 设计第 2 节的安排：语言的名称、它的各个餐次的 `Meal.label` 组成的 `and_list`，以及它的份数。这一行写出的语言总是输出的语言，因为 `init` 写入的就是它运行时用的语言。`context.lang` 来自 `--lang`，否则是英文，因为不存在或空的数据文件夹没有设置（F05 设计 2.10 的步骤 3）。
7. **各个数量。** 目录和常备清单那两行写出示例文字里的数量：6 个分类、22 种食材和 5 个标签，以及常备清单里的 5 种食材。它们是 `_example.py` 里和各段文字放在一起的常量，所以 `init` 不读它刚写出的任何文件。如果把文件读回来，`run` 就会多一个处理文件出错的分支，而没有测试能走到那个分支。F08 的一个测试用 `read_catalog` 和 `read_pantry` 读取新的文件夹，把它们的数量和输出比较（2.2 的示例）。这些数量用 `Plural` 提示，所以以后修改示例数据时，英文仍然正确。
8. **输出流、退出码和路径。** 新建文件夹的输出写到 `context.out`，退出码为 0。拒绝执行或失败写到 `context.err`，退出码为 1（架构 6）。第一行和拒绝执行的提示用完整路径 `str(context.folder.root)` 写出数据文件夹，和 F05 的 `NO_DATA_FOLDER` 一样。输出里的表格用相对于数据文件夹的路径写出每个文件和文件夹，使用系统的分隔符，文件夹以分隔符结尾：Windows 上是 `menus\`，Linux 上是 `menus/`。失败时用完整路径 `str(context.folder.root / problem.file)` 写出出错的文件或文件夹。这偏离了架构 6 的这条规则：“问题里的文件路径相对于数据文件夹，使用系统的分隔符。”这条规则适合你每天都在用的数据文件夹，但不适合你刚在命令行里指定的文件夹。在数据文件夹本身或它上面的文件夹处失败时，问题的文件还是 `Path(".")`，会显示成 `.`。`Problem` 本身仍然保存相对于数据文件夹的文件（3.2），只有 `init` 写出的那一行给出完整路径。Troy 把这处偏离作为待定问题 D 来决定。Troy 批准后，架构师在一个 `[docs]` PR 里把这种情况加进架构 6。
9. **以空格或点结尾的文件夹名称，只有一个点的除外。** 在 Windows 上，系统打开或创建路径时，会去掉路径最后一部分末尾所有的空格和点。对中间的某一部分，它只去掉末尾的一个点，并保留末尾的空格（F05 审查，PR #38）。所以 `--data "D:\x\recipe-menu "` 指向文件夹 `D:\x\recipe-menu`，但 `root / "recipes"` 在中间那一部分保留了空格，所以它指向的文件夹的上一级不存在。两个空格、`..`、` .` 和 `. ` 也是这样。只有一个点时能正常使用：用 `--data "D:\x\recipe-menu."` 时，`init` 创建带有全部文件的 `D:\x\recipe-menu`，以 0 退出，第一行写的是 `D:\x\recipe-menu.`，之后用同一个值的每个命令也都使用这个文件夹。F08 不需要修改 F05 就能保证其他的值安全，因为选择 5 让每个文件夹保持原样：
   - `D:\x\recipe-menu` 不存在时，Windows 为数据文件夹创建它。下一步创建 `recipes`，它的路径保留了空格，所以失败。`init` 删除新建的文件夹，以及它在上面创建的每个文件夹。它用 `FOLDER_CREATE_ERROR` 报告 `D:\x\recipe-menu \recipes`，原因由系统给出，比如“The system cannot find the path specified”，并以 1 退出。
   - `D:\x\recipe-menu` 存在时，列出它的内容能成功，因为列出时用的是数据文件夹自己的路径，它的最后一部分会去掉空格。有条目的文件夹给出 `ALREADY_HOLDS_FILES`，提示里的文件夹名带着空格。空文件夹在 `recipes` 处失败，和第一条一样，失败提示以 `init changed nothing.` 结束。两者都以 1 退出。

   这些提示都不好懂。`init` 无法在一个你在资源管理器里能看到的文件夹里创建 `recipes`，或者拒绝一个你看不见末尾空格的文件夹。待定问题 A 提议修改 F05，让这样的值指向 Windows 实际使用的文件夹。这时 `init` 就像对待其他值一样创建那个文件夹。
10. **没有主文件夹的情况不在范围内。** 在 Windows 上，如果 `USERPROFILE`、`HOMEDRIVE` 和 `HOMEPATH` 都没有，`Path.home()` 会抛出 `RuntimeError`，没有提示覆盖这种情况。`cli` 在运行任何命令之前，按 F05 设计 2.10 的规则 4 调用它，所以用默认数据文件夹的 `init` 会以 Python 的回溯信息结束。F08 不处理这种情况：这个错误来自 F05 的 `cli`，对每个命令的影响都一样，F05 的下一次设计修订会处理它。`init --data FOLDER` 和 `RECIPE_MENU_DATA` 不需要主文件夹，因为 `cli` 只在规则 4 需要时才去取主文件夹。

`init` 创建的文件夹没有警告，所以 v0.1-S06 按 F07 的文字成立（F07 设计第 2 节）。F07 原型“A syntax mistake”缺少示例文件夹会给出的那个警告。那是另一个要由 Troy 决定的问题，它不改变 F08。

Troy 批准这份设计时决定下面四个待定问题（R18）。它们都不修改需求。问题 A 修改 F05 的设计，问题 D 给架构 6 加入一种情况。

- **A. Windows 上以空格或点结尾的文件夹名称。** 架构师在 F05 审查中提出了这个问题（PR #38）。末尾只有一个点时已经能正常使用（选择 9），所以这个问题只对末尾的空格、两个以上的点，以及空格和点混在一起的情况有意义。可选的做法：
  1. 在 Windows 上，`cli` 对数据文件夹调用 `os.path.abspath`。它像 Windows 一样去掉最后一部分末尾的空格和点，所以每个命令都使用 Windows 实际使用的文件夹。它还会把 `..` 合并掉，所以 F05 对 `x/../y` 的测试在 Windows 上要修改。更窄的一种做法只去掉最后一部分末尾的空格和点。
  2. `cli` 查看 `os.path.join(root, "")`，它保留这个空格。这时 `init` 以外的每个命令都把这样的文件夹报告为不存在，而 `init` 按选择 9 的说法失败。
  3. 不修改。选择 9 保持原样。

  做法 1 和 2 修改 F05 设计 2.10 的规则 4 或步骤 2，这是已经实现的接口。所以两者都要走变更流程：修订 F05 的设计、测试和代码。建议：按架构师的倾向选做法 1，放在 F05 的下一次修订里，那次修订也处理选择 10。无论选哪种，F08 自己的 PR 都不需要修改。
- **B. “已有文件”计入每一种条目。** 需求 F08 说，“文件夹里已有文件时，它拒绝执行”。选择 4 计入每一种条目，也包括 `menus\` 这样的空文件夹和隐藏文件。可选的做法：
  1. 每一种条目都计入。数据文件夹要么是空的，要么被拒绝，`init` 不和任何东西混在一起。
  2. 只计入文件，不管它在文件夹的哪一层。这时 `init` 会重用它找到的空文件夹。它还得说明，名称和它的某个文件相同的条目怎么处理，比如一个名为 `settings.toml` 的空文件夹。

  建议：做法 1。
- **C. 数据文件夹上面缺少的文件夹。** 可选的做法：
  1. `init` 创建它们，失败后再把它们删除（选择 5）。你可以一步在 OneDrive 深处建好一个新文件夹。
  2. `init` 拒绝执行，并说明上面的文件夹不存在。这样，数据文件夹上面的一个拼写错误，比如 `D:\OneDirve\recipe-menu`，会得到一个错误，而不是一串新建的文件夹。

  建议：做法 1。输出的第一行写出完整路径，所以你能看到 `init` 把文件夹建在了哪里。
- **D. 失败时用完整路径写出问题的文件。** 架构 6 说，问题用相对于数据文件夹的路径写出它的文件，其他提示用完整路径写出文件或文件夹。失败时的第一行是一个 `Problem` 的文件，而 2.2 用完整路径写出它（选择 8）。可选的做法：
  1. 按 2.2 的写法用完整路径。你能看到 `init` 在哪里失败，在数据文件夹本身处失败时也显示这个文件夹。Troy 批准后，架构师在一个 `[docs]` PR 里把这种情况加进架构 6。
  2. 按架构 6 现在的说法，用相对于数据文件夹的路径。在 `recipes` 处失败时显示 `recipes`，在数据文件夹本身或它上面的文件夹处失败时显示 `.`。2.2 里失败时的第一行和它的示例都要修改。

  建议：做法 1，架构师也同意这个做法。

Troy 批准这份设计时，也一并批准 2.2 和 3.2 里新的中文文字（R18）。

以下后续功能打算以 F08 为基础。它们自己的设计决定细节。

- F11 的 `menu new` 和 F13 的 `shop` 给 `datafile` 加入它们自己的写文件功能（架构 3）。`menu new` 用独占模式创建一个文件，`shop` 先写到同一文件夹里的一个临时文件，再用它替换原文件（架构 6）。它们可以共用 `create_data_folder` 里写文件的内部部分，以及它在失败时用的提示（3.2）。F11 原型用完整路径写出已经存在的菜单文件，和 `init` 写出它的数据文件夹的方式一样。
- F15 的 `add` 像 `menu new` 一样，用独占模式写出一个新的菜谱文件。
- 场景 v0.1-S01 到 v0.1-S04、v0.1-S06、v0.1-S16 和 v0.1-S20 都从 `init` 创建的文件夹开始。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/init/__init__.py`、`messages.py`、放 `run` 的一个内部文件，以及 `src/recipe_menu/cli/_commands.py` 里的那一项。在 `datafile` 里，它包含 `__init__.py` 里新的导出、放 `CreationOutcome`、`Creation` 和 `create_data_folder` 的一个内部文件，以及 `messages.py` 里的六条提示。它定义每条提示、字段齐全的 `INIT_COMMAND`，以及带有各个成员的 `CreationOutcome`。它的 `Creation` 有三个字段，但没有 3.1 的检查。它的 `create_data_folder` 什么都不碰，给出 `Creation(CreationOutcome.CREATED)`，它的 `run` 什么都不写，给出 0。所以检查输出、文件、拒绝执行或失败的新测试在 mock 上都会失败（R09）。有些测试在 mock 上会通过，从而违反 R09：只检查被拒绝的文件夹保留了它的条目、只检查失败后什么都没留下，或者只检查帮助的测试。只检查 `INIT_COMMAND` 的字段、`CreationOutcome` 的值、合法 `Creation` 的默认值或相等性，或者只检查 `init extra` 或 `init --tag` 的测试也是这样，后两者在 `cli` 运行 `init` 之前就被拒绝。每个这样的测试都还要检查 mock 做错的内容，比如输出、结果，或者 3.1 的某项检查。mock 改动 7 个文件，超过 R03 的 5 个，所以它的说明要写明软限制的理由：测试既直接用到 `create_data_folder`，也通过 `init` 用到它，所以两个模块要在同一个阶段一起带上，和 F05 的 mock 一样。实现（PR 5）包含 `_example.py` 里的文字、`run` 和 `create_data_folder`，共 3 个文件。

### 2.1 `INIT_COMMAND`

- 模块：init
- 功能：对 `init` 命令的描述。`cli` 读取它来解析命令行、写出帮助、决定运行命令之前检查什么，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 创建数据文件夹，并写出 2.2 的输出。

签名：

```python
INIT_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("init",)
#   help_line = INIT_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.CREATE
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("init",)`。 | 无 |
| `help_line` | `Message` | `INIT_HELP`：“Create the data folder with example data.”和“创建数据文件夹和示例数据。”，即 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接受一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 创建数据文件夹，并写出 2.2 的输出。 | 给出 0 或 1。 |
| `argument` | `None` | `init` 不接受参数。 | 无 |
| `options` | 空元组 | `init` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.CREATE`：无论数据文件夹是否存在，也无论它的设置有没有错误，`cli` 都运行 `init`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4）。 | `run` 只使用 `context.lang`、`context.folder`、`context.out` 和 `context.err`。它既不使用 `context.settings`，也不使用 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `init` 的东西（F05 设计 2.6）。 | 是空的，因为 `init` 不声明参数和选项，所以 `cli` 不放过任何值。`run` 不读取它。 |

- 返回值：`INIT_COMMAND`，一个 `Command`。
  - `INIT_COMMAND.usage` 在两种语言里都是 `init`，所以帮助显示 `init`，用法错误引用 `recipe-menu init`。
  - `INIT_COMMAND.run(context, arguments)` 调用一次 `create_data_folder`，用 `context.lang` 写出 2.2 的输出。它创建了数据文件夹时给出 0，否则给出 1。

错误：无。`run` 遇到拒绝执行或磁盘上的失败从不抛异常。它不抛 `UsageError`，因为 `init` 不接受参数值。打断它的异常，比如 `KeyboardInterrupt`，在 `create_data_folder` 删除它创建的东西之后继续传给 `cli`（选择 5）。

- 副作用：见 2.2。
- 性能指标：无

示例：

在这个示例里，`home` 是一个空的临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里的设置是英文的，而 `run` 用上下文的语言写出设置。帮助来自 `COMMANDS`，F08 之后它包含 `INIT_COMMAND` 和 `CHECK_COMMAND`。

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings

assert INIT_COMMAND.words == ("init",)
assert INIT_COMMAND.usage == BiText("init", "init")
assert INIT_COMMAND.help_line.render(Lang.EN) == "Create the data folder with example data."
assert INIT_COMMAND.help_line.render(Lang.ZH) == "创建数据文件夹和示例数据。"
assert (INIT_COMMAND.argument, INIT_COMMAND.options) == (None, ())
assert INIT_COMMAND.folder is FolderUse.CREATE

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(home / "direct")
context = Context(Lang.ZH, folder, Settings(Lang.EN), out, err, date(2026, 11, 10))
assert INIT_COMMAND.run(context, Arguments()) == 0
assert err.getvalue() == ""
assert out.getvalue().splitlines()[0] == f"已创建数据文件夹 {folder.root}："
assert read_settings(folder) == (Settings(Lang.ZH), ())


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
assert len(english) == 15
assert english[4:7] == [
    "Commands:",
    "  init            Create the data folder with example data.",
    "  check           Check every data file for mistakes.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[5:7] == [
    "  init            创建数据文件夹和示例数据。",
    "  check           检查每个数据文件有没有错误。",
]
```

### 2.2 `recipe-menu init`

- 模块：init
- 功能：创建数据文件夹的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 的流程 1，以及 [4](../../requirements.zh-CN.md#4-功能点)）。它创建数据文件夹，里面有用它的语言写的设置、目录、常备清单、示例菜谱 `tomato-egg`，以及空文件夹 `menus/` 和 `shopping/`。文件夹里已有文件时，它拒绝执行。F08 原型展示了它。

签名：

```text
recipe-menu init [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--lang` | `en` 或 `zh` | 输出的语言，也是新设置的语言。 | 按 F05 设计 2.10 的规则。不写这个选项时用英文，因为不存在或空的数据文件夹没有设置。文件夹的设置写了语言时，拒绝执行的提示用那种语言。 |
| `--data` | 一个文件夹 | 要创建的数据文件夹。 | 按 F05 设计 2.10 的规则。不写这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。这个文件夹可以不存在，它上面的文件夹也可以不存在。 |
| `--help` | 开关 | 显示帮助（选择 1），不运行 `init`。 | 无 |

`init` 只调用一次 `create_data_folder(folder, folders, files)`，其中 `folder = context.folder`，文件夹和文件按以下顺序：

| 种类 | 路径 | 文字 |
| --- | --- | --- |
| 文件夹 | `folder.recipes` | 无 |
| 文件夹 | `folder.menus` | 无 |
| 文件夹 | `folder.shopping` | 无 |
| 文件 | `folder.settings` | `example-data.md` 里的代码块 `settings.toml`，`language` 一行里的 `en` 换成 `context.lang` 的值。 |
| 文件 | `folder.catalog` | `example-data.md` 里的代码块 `catalog.toml`。 |
| 文件 | `folder.pantry` | `example-data.md` 里的代码块 `pantry.toml`。 |
| 文件 | `folder.recipe_file("tomato-egg")` | `example-data.md` 里的代码块 `recipes\tomato-egg.toml`。 |

每段文字就是它的代码块里的各行，每行以 LF 结束。所以 `recipe-menu init --lang zh` 写出这样的 `settings.toml`：

```toml
# recipe-menu settings
language = "zh"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
```

- 返回值：退出码，以及写到对应流上的输出：

| 退出码 | 何时 | 输出流 |
| --- | --- | --- |
| 0 | `create_data_folder` 给出 `CREATED`。 | 输出流：新建文件夹的各行。 |
| 1 | 它给出 `HOLDS_FILES`、`NOT_A_FOLDER` 或 `FAILED`。 | 错误流：拒绝执行或失败的提示。输出流里什么也不写。 |

新建的文件夹给出这些行，每行以换行结束：

1. `CREATED`，带 `folder`。
2. 下表的六行，按 `format_table(rows, indent=2, gap=4)` 排版（F02 设计 2.9）。第一列宽 23 列，即 `recipes\tomato-egg.toml` 的宽度，所以在两种语言里第二列都从第 29 列之后开始，和 F08 原型一样。
3. 一个空行。
4. `NEXT_STEP`，带 `recipes`。

| 第一格 | 第二格 |
| --- | --- |
| `settings.toml` | `SETTINGS_LINE`，带 `language`、`meals` 和 `servings` |
| `catalog.toml` | `CATALOG_LINE`，带 `categories`、`ingredients` 和 `tags` |
| `pantry.toml` | `INGREDIENT_COUNT`，按 5 选择，`count` 为 5 |
| `recipes\tomato-egg.toml` | `EXAMPLE_RECIPE` |
| `menus\` | `EMPTY_FOLDER` |
| `shopping\` | `EMPTY_FOLDER` |

每个第一格都是调用表里对应路径的 `str(folder.relative(path))`，文件夹末尾再加上 `os.sep`。所以 Linux 上显示 `recipes/tomato-egg.toml` 和 `menus/`。

拒绝执行时只有一行：`HOLDS_FILES` 对应 `ALREADY_HOLDS_FILES`，`NOT_A_FOLDER` 对应 `IS_A_FILE`，都带 `folder`。

失败时有三行。在下面这个 Windows 上的例子里，你能读取文件夹 `D:\Shared\recipe-menu`，但不能在里面创建任何东西：

```text
PS> recipe-menu init --data D:\Shared\recipe-menu
D:\Shared\recipe-menu\recipes
  The folder cannot be created: access is denied.
init changed nothing.
PS> $LASTEXITCODE
1
```

第一行是问题所在文件的完整路径 `str(context.folder.root / problem.file)`。文件为 `Path(".")` 时，它就是数据文件夹本身。架构 6 用相对于数据文件夹的路径写出问题的文件，所以这一行偏离了它（选择 8 和待定问题 D）。第二行是两个空格加上 `problem.text(context.lang)`。结果的 `left` 为空时，第三行是 `CHANGED_NOTHING`，否则是带 `folder` 的 `LEFT_BEHIND`。

`init` 的提示如下。`SERVINGS_PER_DISH`、`CATEGORY_COUNT`、`INGREDIENT_COUNT` 和 `TAG_COUNT` 是 `Plural` 值（F02 设计 2.4），各自按它的 `count` 选择。它们“多个”的形式用于 1 以外的每个数。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `INIT_HELP` | `Create the data folder with example data.` | `创建数据文件夹和示例数据。` |
| `CREATED` | `Created the data folder {folder}:` | `已创建数据文件夹 {folder}：` |
| `SETTINGS_LINE` | `{language}, {meals}, {servings}` | `{language}，{meals}，{servings}` |
| `ENGLISH` | `English` | `英文` |
| `CHINESE` | `Chinese` | `中文` |
| `SERVINGS_PER_DISH`，一个 | `{count} serving per dish` | `每道菜 {count} 份` |
| `SERVINGS_PER_DISH`，多个 | `{count} servings per dish` | `每道菜 {count} 份` |
| `CATALOG_LINE` | `{categories}, {ingredients}, {tags}` | `{categories}，{ingredients}，{tags}` |
| `CATEGORY_COUNT`，一个 | `{count} category` | `{count} 个分类` |
| `CATEGORY_COUNT`，多个 | `{count} categories` | `{count} 个分类` |
| `INGREDIENT_COUNT`，一个 | `{count} ingredient` | `{count} 种食材` |
| `INGREDIENT_COUNT`，多个 | `{count} ingredients` | `{count} 种食材` |
| `TAG_COUNT`，一个 | `{count} tag` | `{count} 个标签` |
| `TAG_COUNT`，多个 | `{count} tags` | `{count} 个标签` |
| `EXAMPLE_RECIPE` | `an example recipe in both languages` | `一个中英双语的示例菜谱` |
| `EMPTY_FOLDER` | `empty` | `空` |
| `NEXT_STEP` | `Next: add your recipes to {recipes}, then run "recipe-menu check".` | `下一步：把你的菜谱加进 {recipes}，然后运行“recipe-menu check”。` |
| `ALREADY_HOLDS_FILES` | `{folder} already holds files. init changed nothing.` | `{folder} 里已经有文件。init 没有做任何修改。` |
| `IS_A_FILE` | `{folder} is a file, not a folder. init changed nothing.` | `{folder} 是一个文件，不是文件夹。init 没有做任何修改。` |
| `CHANGED_NOTHING` | `init changed nothing.` | `init 没有做任何修改。` |
| `LEFT_BEHIND` | `init could not remove all that it created. Empty {folder}, then run "recipe-menu init" again.` | `init 没能删除它创建的全部内容。请清空 {folder}，然后再运行“recipe-menu init”。` |

占位符的值如下。`settings` 是 `Settings(context.lang)`，即 `read_settings` 读新文件时给出的值（选择 6）。

| 占位符 | 值 |
| --- | --- |
| `folder` | `str(context.folder.root)`，数据文件夹的完整路径。 |
| `language` | `Lang.EN` 对应 `ENGLISH`，`Lang.ZH` 对应 `CHINESE`，按 `settings.language` 选择，以 `BiText` 给出。 |
| `meals` | `settings.meals` 里每个餐次的 `Meal.label` 组成的 `and_list`：“lunch and dinner”和“午餐和晚餐”。 |
| `servings` | 按 `settings.servings` 选出的 `SERVINGS_PER_DISH`，`count` 为这个数，以 `BiText` 给出：“2 servings per dish”和“每道菜 2 份”。 |
| `categories`、`ingredients` 和 `tags` | 分别按 6、22 和 5 选出的 `CATEGORY_COUNT`、`INGREDIENT_COUNT` 和 `TAG_COUNT`，`count` 为各自的数，以 `BiText` 给出（选择 7）。 |
| `count` | 每个 `Plural` 的数。 |
| `recipes` | `str(folder.relative(folder.recipes))` 加上 `os.sep`：Windows 上是 `recipes\`，Linux 上是 `recipes/`。 |

用这些提示，两种语言都能得到 F08 原型里的各行，比如 `6 categories, 22 ingredients, 5 tags` 和 `6 个分类，22 种食材，5 个标签`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| 退出码 1，错误流上是 `ALREADY_HOLDS_FILES` | 数据文件夹是一个有条目的文件夹（选择 4）。每个条目都保持原来的字节和修改时间（v0.1-S03）。 |
| 退出码 1，错误流上是 `IS_A_FILE` | 数据文件夹的路径上有一个不是文件夹的东西（选择 4）。 |
| 退出码 1，错误流上是失败时的三行 | 一个 `OSError` 让 `create_data_folder` 停下（3.2）。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "extra". Write "recipe-menu init".` | `init` 后面跟着一个词。`cli` 在运行 `init` 之前报告它（F05 设计 2.10）。 |
| 退出码 2，先是没有选项那种形式的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"init" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 全局选项违反了它的规则。 |
| 退出码 130 | Ctrl+C。`create_data_folder` 删除它创建的东西，`cli` 不再写出任何内容（选择 5）。 |

- 副作用：`cli` 查看数据文件夹，数据文件夹是文件夹时还读取 `settings.toml`（F05 设计 2.10）。然后 `init` 调用一次 `create_data_folder`。这次调用列出数据文件夹的内容，创建调用表里的文件夹和文件，失败后再把它们删除（3.2）。`init` 把它的各行写到输出流或错误流。拒绝执行时什么都不创建，也什么都不修改。
- 性能指标：无

示例：

在这个示例里，`home` 是一个空的临时文件夹，`example` 是仓库里的文件夹 `tests/data/example/`（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。第一次运行创建默认的数据文件夹。之后的几次运行检查它、拒绝它、创建一个中文的数据文件夹，并试一试选择 4 的各种情况和一个命令行错误。

```python
import io
import os
from datetime import date
from pathlib import Path

from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings, read_settings


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


def same_text(made: Path, source: Path) -> bool:
    return made.read_bytes() == source.read_text(encoding="utf-8").encode("utf-8")


folder = DataFolder(home / "recipe-menu")
recipe = str(Path("recipes", "tomato-egg.toml"))
menus, shopping = "menus" + os.sep, "shopping" + os.sep
assert run("init") == (
    0,
    [
        f"Created the data folder {folder.root}:",
        "  settings.toml              English, lunch and dinner, 2 servings per dish",
        "  catalog.toml               6 categories, 22 ingredients, 5 tags",
        "  pantry.toml                5 ingredients",
        f"  {recipe}    an example recipe in both languages",
        f"  {menus}                     empty",
        f"  {shopping}                  empty",
        "",
        f'Next: add your recipes to recipes{os.sep}, then run "recipe-menu check".',
    ],
    [],
)
assert sorted(entry.name for entry in folder.root.iterdir()) == [
    "catalog.toml",
    "menus",
    "pantry.toml",
    "recipes",
    "settings.toml",
    "shopping",
]
assert [entry.name for entry in folder.recipes.iterdir()] == ["tomato-egg.toml"]
assert list(folder.menus.iterdir()) == list(folder.shopping.iterdir()) == []
for name in ("settings.toml", "catalog.toml", "pantry.toml"):
    assert same_text(folder.root / name, example / name)
assert same_text(folder.recipe_file("tomato-egg"), example / "recipes" / "tomato-egg.toml")
assert read_settings(folder) == (Settings(Lang.EN), ())
catalog, problems = read_catalog(folder)
assert catalog is not None and problems == ()
assert (len(catalog.categories), len(catalog.ingredients), len(catalog.tags)) == (6, 22, 5)
pantry, problems = read_pantry(folder, catalog)
assert pantry is not None and problems == () and len(pantry.ingredients) == 5

assert run("check") == (
    0,
    [
        "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
        "",
        "No errors. No warnings.",
    ],
    [],
)
assert run("init") == (1, [], [f"{folder.root} already holds files. init changed nothing."])

other = home / "zh"
code, lines, err = run("init", "--lang", "zh", "--data", str(other))
assert (code, err) == (0, [])
assert lines[0] == f"已创建数据文件夹 {other}："
assert lines[1:4] == [
    "  settings.toml              中文，午餐和晚餐，每道菜 2 份",
    "  catalog.toml               6 个分类，22 种食材，5 个标签",
    "  pantry.toml                5 种食材",
]
assert lines[-1] == f"下一步：把你的菜谱加进 recipes{os.sep}，然后运行“recipe-menu check”。"
english_settings = folder.settings.read_bytes()
chinese_settings = (other / "settings.toml").read_bytes()
assert chinese_settings == english_settings.replace(b'language = "en"', b'language = "zh"')
assert run("check", "--data", str(other)) == (
    0,
    ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"],
    [],
)

empty = home / "empty"
empty.mkdir()
assert run("init", "--data", str(empty))[0] == 0
only_menus = home / "only-menus"
(only_menus / "menus").mkdir(parents=True)
hidden = home / "hidden"
hidden.mkdir()
(hidden / ".keep").write_text("", encoding="utf-8")
for full in (only_menus, hidden):
    refusal = f"{full} already holds files. init changed nothing."
    assert run("init", "--data", str(full)) == (1, [], [refusal])
assert [entry.name for entry in only_menus.iterdir()] == ["menus"]
notes = home / "notes.txt"
notes.write_text("Ideas\n", encoding="utf-8")
assert run("init", "--data", str(notes)) == (
    1,
    [],
    [f"{notes} is a file, not a folder. init changed nothing."],
)
deep = home / "a" / "b" / "recipe-menu"
code, lines, _ = run("init", "--data", str(deep))
assert (code, lines[0]) == (0, f"Created the data folder {deep}:")
assert run("init", "extra") == (
    2,
    [],
    [
        'Unexpected argument "extra". Write "recipe-menu init".',
        'Run "recipe-menu --help" to see the commands.',
    ],
)
```

## 3. 对已有接口的修改

无。F01 到 F07 已经实现的接口都不改变。每个导出的名称都保持它的签名和行为，F01 到 F07 的测试不用修改就能通过。F08 增加模块 `init`。和 F04、F05 一样，它给 `datafile` 的接口加入名称：

1. `datafile` 导出 `CreationOutcome`、`Creation`（3.1）和 `create_data_folder`（3.2），`datafile/messages.py` 多了六条内部提示（3.2）。架构 3 安排了这些写文件的部分：“之后的功能按需加入写文件的部分和公用的检查。”
2. `src/recipe_menu/cli/_commands.py` 的 `COMMANDS` 在 `CHECK_COMMAND` 前面加入 `INIT_COMMAND`。`COMMANDS` 只在 `cli` 内部使用，架构 4 让每个命令功能加入这样一项。加入这一项后，真正的 `recipe-menu` 的帮助会列出 `init`（选择 1）。运行真正的 `COMMANDS` 的测试是 F05-T48、F05-T49 和 F07-T17。它们检查未知命令、没有命令的命令行、帮助的第一行和最后一行，以及不管排在哪里的 `check` 那一行，这一项都不改变这些内容。

F08 按这些接口的设计使用它们，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural`、`and_list` 和 `format_table`。
- F03 的 `DataFolder`、`Problem` 和 `Severity`，以及 `SYSTEM_ERROR` 确定值 `reason` 的条件（F03 设计 2.3）。
- F04 里 `list_toml_files` 的列出问题表和它的四条提示，它们仍然只在 `datafile` 内部使用（F04 设计 3.1）。
- F05 在 `app` 里的 `Arguments`、`Command`、`Context` 和 `FolderUse`，在 `settings` 里的 `Settings` 和 `Meal.label`，以及 `cli` 里的 `COMMANDS`。

上面的示例还用到 F03 的 `read_catalog` 和 `read_pantry`、F05 的 `read_settings`，以及在 `init` 创建的文件夹上运行的 F07 的 `check`。

### 3.1 `CreationOutcome` 和 `Creation`

- 模块：datafile
- 功能：`create_data_folder`（3.2）的结果：它在数据文件夹那里发现了什么，或者什么让它停下，以及失败后它没能删除的东西。`init` 按结果选择它的输出（2.2）。

签名：

```python
class CreationOutcome(Enum):
    CREATED = "created"
    HOLDS_FILES = "holds files"
    NOT_A_FOLDER = "not a folder"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Creation:
    outcome: CreationOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `outcome` | `CreationOutcome` | 发生了什么，见下表。 | 无 |
| `problem` | `Problem` 或 `None` | 让调用停下的 `OSError`，以问题的形式给出。 | `FAILED` 时是一个 `Severity.ERROR` 的 `Problem`，其他结果时是 `None`。 |
| `left` | `Path` 的元组 | 调用创建了、但失败后没能删除的东西，以完整路径给出，按删除的顺序排列。 | `FAILED` 以外的结果都是空的。 |

| 成员 | 何时 | `problem` | `left` |
| --- | --- | --- | --- |
| `CREATED` | 调用创建了每个文件夹和文件。 | `None` | 空 |
| `HOLDS_FILES` | 数据文件夹是一个有条目的文件夹。调用什么都没创建。 | `None` | 空 |
| `NOT_A_FOLDER` | 数据文件夹的路径上有一个不是文件夹的东西。调用什么都没创建。 | `None` | 空 |
| `FAILED` | 一个 `OSError` 让调用停下，调用删除了它创建的东西。 | 这个错误 | 删除时没能删除的东西，通常什么都没有 |

- 返回值：一个 `CreationOutcome` 成员，或一个 `Creation`。两个结果的三个字段都相等时，它们相等，`Creation` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `outcome` 是 `FAILED` 而 `problem` 是 `None`，或者 `outcome` 是其他成员而 `problem` 不是 `None`。 |
| `ValueError` | `problem` 是 `Severity.WARNING`。 |
| `ValueError` | `left` 不是空的，而 `outcome` 不是 `FAILED`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import Creation, CreationOutcome, Problem
from recipe_menu.text import Message

DENIED = Message(
    "The folder cannot be created: access is denied.", "无法创建文件夹：没有访问权限。"
)
values = [outcome.value for outcome in CreationOutcome]
assert values == ["created", "holds files", "not a folder", "failed"]
created = Creation(CreationOutcome.CREATED)
assert (created.problem, created.left) == (None, ())
problem = Problem.error(Path("recipes"), None, DENIED)
left = (Path.cwd() / "recipe-menu" / "recipes",)
failed = Creation(CreationOutcome.FAILED, problem, left)
assert (failed.problem, failed.left) == (problem, left)
assert failed == Creation(CreationOutcome.FAILED, problem, left)

Creation(CreationOutcome.FAILED)  # raises ValueError
Creation(CreationOutcome.HOLDS_FILES, problem)  # raises ValueError
Creation(CreationOutcome.CREATED, None, left)  # raises ValueError
warning = Problem.warning(Path("recipes"), None, DENIED)
Creation(CreationOutcome.FAILED, warning)  # raises ValueError
```

### 3.2 `create_data_folder`

- 模块：datafile
- 功能：创建一个数据文件夹和它的文件夹、文件，要么全部完成，要么什么都不留下（选择 4 和 5）。它只往不存在或空的数据文件夹里写，用独占模式打开每个文件，失败或被打断之后删除它创建的东西（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。它是 `datafile` 第一个写文件的接口（架构 3）。`init` 调用它（2.2）。

签名：

```python
def create_data_folder(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> Creation: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 要创建的数据文件夹。 | 无。它的根和它上面的文件夹都可以不存在。 |
| `folders` | `Path` 的序列 | 要在里面创建的文件夹，按顺序，比如 `folder.recipes`。 | 每个都在 `folder.root` 里面，而且不是 `folder.root`。每个只出现一次。它的上一级是 `folder.root`，或者 `folders` 里排在它前面的一项。 |
| `files` | （路径，文字）对的序列 | 要创建的文件，按顺序，每个都带着它的文字。 | 每个路径都在 `folder.root` 里面，不是 `folder.root`，只出现一次，也不是 `folders` 里的一项。它的上一级是 `folder.root` 或 `folders` 里的一项。每段文字都是 UTF-8 能编码的 `str`。 |

- 返回值：一个 `Creation`（3.1）。

`create_data_folder` 按以下步骤工作：

1. 在碰磁盘之前，它按约束检查参数，并把每段文字编码成 UTF-8。参数不对时，抛出“错误”表里的一个错误。
2. 它查看 `folder.root`。下表第一个符合的行决定结果：

   | 条件 | 接下来 |
   | --- | --- |
   | `os.path.isdir(folder.root)` 为真。 | 它列出这个文件夹的内容。列出时遇到 `OSError` 失败，就给出 `FAILED`。这个问题的文件是 `Path(".")`，没有位置，提示来自 `list_toml_files` 的列出问题表（F04 设计 3.1）。只要有任何一种条目，包括隐藏的条目，就给出 `HOLDS_FILES`。没有条目时，调用继续执行步骤 3。 |
   | `os.path.lexists(folder.root)` 为真。 | `NOT_A_FOLDER`。 |
   | 两者都不是。 | 它从上往下逐个创建 `folder.root` 和它上面每个缺少的文件夹，然后继续执行步骤 3。 |

3. 它按顺序创建 `folders` 里的每个文件夹，用 `Path.mkdir`，不创建上级，已经存在的文件夹算作错误。
4. 它按顺序创建 `files` 里的每个文件。它用独占模式 `"x"`、`encoding="utf-8"` 和 `newline="\n"` 打开文件（架构 8），写入文字，然后关闭文件。所以文件里是这段文字的 UTF-8 字节，没有字节顺序标记，换行就是文字里的换行。
5. 它给出 `Creation(CreationOutcome.CREATED)`。

`os.path.isdir` 和 `os.path.lexists` 从不抛异常，查看失败时算作假。步骤 2 到 4 里创建东西时抛出的第一个 `OSError` 让调用停下。然后调用按下面的说法删除它创建的东西，并给出 `FAILED`，问题按下表第一个符合的行确定：

| 错误 | 创建文件夹时 | 创建文件时 |
| --- | --- | --- |
| `FileExistsError` | `FOLDER_EXISTS` | `FILE_EXISTS` |
| `PermissionError` | `FOLDER_CREATE_DENIED` | `FILE_WRITE_DENIED` |
| 其他任何 `OSError` | `FOLDER_CREATE_ERROR` | `FILE_WRITE_ERROR` |

值 `reason` 是这个错误的 `strerror`。`strerror` 为 `None` 或空时，它是错误类的名称，比如 `OSError`，和 `SYSTEM_ERROR` 一样（F03 设计 2.3）。这个问题没有位置。对 `folders` 或 `files` 里的一项，它的文件是 `folder.relative(path)`。对 `folder.root` 和它上面的文件夹，它的文件是 `Path(".")`，因为你指定的是数据文件夹。

删除按以下步骤进行：

1. 它按创建的相反顺序，删除调用创建的每个文件夹和文件。它用 `Path.unlink` 删除文件，用 `Path.rmdir` 删除文件夹，后者只删除空文件夹。文件从成功打开的那一刻起就算已创建，所以写了一半的文件也会被删除。
2. 它从不删除调用之前就有的东西。所以原来就空着的数据文件夹会留下，它上面的文件夹也会留下。
3. 删除时遇到 `OSError` 失败的那一项被跳过，接着删除下一项。它的路径以完整路径的形式进入 `left`，按删除的顺序排列。还装着被跳过的文件的文件夹在 `rmdir` 时会失败，所以它也进入 `left`。

在步骤 2 到 4 里打断调用的其他任何异常，比如 Ctrl+C 引起的 `KeyboardInterrupt` 或者 bug 引起的异常，都会执行同样的删除，然后继续传出去。这时调用不给出结果。删除在 `finally` 块里执行，所以没有 `except` 子句捕获 `OSError` 以外的异常（架构 6 和 8）。

这些提示加入 `datafile` 的内部提示，和 F03 设计 2.3 以及 F04 设计 3.1 的提示放在一起：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `FILE_EXISTS` | `The file already exists.` | `文件已存在。` |
| `FILE_WRITE_DENIED` | `The file cannot be written: access is denied.` | `无法写入文件：没有访问权限。` |
| `FILE_WRITE_ERROR` | `The file cannot be written. The system says: {reason}` | `无法写入文件。系统提示：{reason}` |
| `FOLDER_EXISTS` | `The folder already exists.` | `文件夹已存在。` |
| `FOLDER_CREATE_DENIED` | `The folder cannot be created: access is denied.` | `无法创建文件夹：没有访问权限。` |
| `FOLDER_CREATE_ERROR` | `The folder cannot be created. The system says: {reason}` | `无法创建文件夹。系统提示：{reason}` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `folders` 或 `files` 里的某个路径不在 `folder.root` 里面、就是 `folder.root`、出现了两次，或者它的上一级既不是 `folder.root`，也不是 `folders` 里排在它前面的一项。这个检查在调用碰磁盘之前进行。 |
| `UnicodeEncodeError` | 某段文字里有 UTF-8 无法编码的字符，比如单独的代理项。这个检查在调用碰磁盘之前进行。 |

- 副作用：`folder.root` 是文件夹时，列出它的内容。`folder.root` 不存在时，创建 `folder.root` 和它上面的文件夹，然后创建各个文件夹和文件。失败或被打断之后，删除它创建的东西。它不读任何文件。
- 性能指标：无

示例：

在这个示例里，`tmp` 是一个空的临时文件夹。第二次调用遇到第一次调用创建的文件夹。失败的情况用一个 300 个字符的文件名，两种系统都不接受它，这时调用已经创建了设置文件。

```python
from pathlib import Path

from recipe_menu.datafile import CreationOutcome, DataFolder, create_data_folder
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "a" / "recipe-menu")
folders = (folder.recipes, folder.menus)
files = ((folder.settings, 'language = "en"\n'), (folder.recipe_file("rice"), "servings = 2\n"))
creation = create_data_folder(folder, folders, files)
assert creation.outcome is CreationOutcome.CREATED
assert (creation.problem, creation.left) == (None, ())
assert folder.settings.read_bytes() == b'language = "en"\n'
assert sorted(entry.name for entry in folder.root.iterdir()) == [
    "menus",
    "recipes",
    "settings.toml",
]
assert [entry.name for entry in folder.recipes.iterdir()] == ["rice.toml"]

assert create_data_folder(folder, folders, files).outcome is CreationOutcome.HOLDS_FILES
assert folder.settings.read_bytes() == b'language = "en"\n'
not_a_folder = create_data_folder(DataFolder(folder.settings), (), ())
assert not_a_folder.outcome is CreationOutcome.NOT_A_FOLDER

other = DataFolder(tmp / "b" / "recipe-menu")
name = "x" * 300 + ".toml"
failed = create_data_folder(
    other, (other.recipes,), ((other.settings, "\n"), (other.root / name, "\n"))
)
assert failed.outcome is CreationOutcome.FAILED
assert failed.problem is not None
assert (failed.problem.file, failed.problem.place) == (Path(name), None)
assert failed.problem.text(Lang.EN).startswith("The file cannot be written. The system says: ")
assert failed.left == ()
assert not (tmp / "b").exists()

fresh = DataFolder(tmp / "c")
create_data_folder(fresh, (), ((tmp / "elsewhere.toml", ""),))  # raises ValueError
create_data_folder(fresh, (), ((fresh.recipe_file("rice"), ""),))  # raises ValueError
create_data_folder(fresh, (fresh.menus, fresh.menus), ())  # raises ValueError
create_data_folder(fresh, (), ((fresh.settings, "\udc80"),))  # raises UnicodeEncodeError
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `init` 是架构 3 里的命令模块，位于 `src/recipe_menu/commands/init/`，只导出 `INIT_COMMAND`。它引用 `app`、`lang`、`text`、`datafile` 和 `settings`，都是它那一行允许的模块。它那一行拥有“它写出的示例文件”，所以四段文字应当放在 `_example.py` 里，`init` 通过 `datafile` 写出它们，符合架构 2 和 8 的要求（选择 2）。`create_data_folder` 是架构 3 为 `datafile` 安排的第一个写入，它只用 `datafile` 自己的文件。`Creation` 是带 `slots=True` 的冻结 dataclass，其中的集合是元组，`CreationOutcome` 是枚举（架构 8）。`Problem` 的文件仍然相对于数据文件夹，数据文件夹本身是 `Path(".")`（架构 5.3）。这四个文件正是架构 5.1 里写明由 `init` 写出的文件。架构师在分支的代码之上按第 2 节和第 3 节建了模型，选择 1 到 3、6 和 7 在模型上都成立。`INIT_COMMAND` 排在 `CHECK_COMMAND` 前面时，两种语言的帮助都是 15 行，第二列从第 18 列之后开始。模型从 `example-data.md` 的代码块取出的文字不含反斜杠，与 `tests/data/example/` 逐字节相同。对这些文字，`read_catalog` 和 `read_pantry` 给出 6 个分类、22 种食材、5 个标签和 5 种常备食材。中文的 `settings.toml` 与英文的只在 `language` 的值上不同，`read_settings` 对它给出 `Settings(Lang.ZH)`。`pyproject.toml` 不变，所以 R16 没有要审查的内容。第 0.2 版没有改动这些内容，所以第 1 轮的理由仍然成立。 |
| 遵守错误处理和命名约定 | Pass | 第 1 轮的理由仍然成立。拒绝执行和磁盘上的失败都是值。`create_data_folder` 把每个 `OSError` 变成一个 `Problem`，除了 `OSError` 不写别的异常，并在 `finally` 块里删除（架构 6 和 8）。每个文件都以 `"x"` 模式、`utf-8` 和 `newline="\n"` 打开，所以 `init` 从不覆盖文件（架构 6）。退出码和输出流符合架构 6。每条提示都是所在模块 `messages.py` 里的 UPPER_SNAKE 常量。各个计数是 `Plural` 值，两种形式有相同的占位符。`datafile` 的六条新提示在两种语言里都沿用 F03 设计 2.3 和 F04 设计 3.1 的读取提示。在模型上，用这台 Windows 11 电脑上的 Python 3.13.18，选择 4、5 和 10 以及 3.2 的示例仍然和第 1 轮发现的一样成立。发现 1 已解决。架构师用第 1 轮的六个值再次运行了选择 9：`x\recipe-menu` 后面加一个空格、两个空格、`.`、`..`、` .` 和 `. `，每个值都在第 1 轮的四种情况下运行。第 0.2 版写出了每个结果。除了只有一个点的值，`init` 对每个值都在 `recipes` 处失败，给出 `FOLDER_CREATE_ERROR` 和原因“The system cannot find the path specified”，并删除它创建的每个文件夹。唯一的例外是有条目的文件夹，它给出 `ALREADY_HOLDS_FILES`，提示里的名称和输入的一样。这些运行都以 1 退出，在空文件夹里的失败以 `init changed nothing.` 结束。只有一个点时，`init` 创建带有全部文件的 `recipe-menu`，以 0 退出，第一行带着这个点。之后用同一个值运行 `check` 给出“No errors. No warnings.”，再运行一次 `init` 会拒绝这个文件夹。发现 2 已解决。选择 8 引用了失败的第一行所偏离的架构 6 的规则，说明了原因，并把这处偏离作为待定问题 D 交给 Troy。2.2 指向这两处。引文在规则的示例之前结束，这不改变规则。`Problem` 仍然保存相对于数据文件夹的文件，所以只有 `init` 写出的那一行偏离了规则。发现 3 已解决。架构师运行了选择 5 新增的两种情况。在 `open` 刚创建 `pantry.toml` 之后按 Ctrl+C，会留下这个文件、数据文件夹和它上面的文件夹。在删除 `settings.toml` 时再按一次 Ctrl+C，会让删除停下。两者都给出退出码 130，没有输出，之后的 `init` 拒绝这个文件夹，和选择 5 说的一样。发现 4 已解决。用 ruff 0.17.4 运行 `ruff format --config pyproject.toml --diff`，7 个 `python` 代码块都已经格式化好，其中没有一行超过 100 列。3.1 里警告的 `# raises ValueError` 在那次调用的那一行。 |
| 不和已有接口重复 | Pass | 在 `create_data_folder` 之前，没有接口创建文件夹或文件。列出内容失败时沿用 `list_toml_files` 的提示（F04 设计 3.1），它的值 `reason` 沿用 `SYSTEM_ERROR` 的规则（F03 设计 2.3）。六条新提示说的是读取提示说不出的内容。`init` 按 `stop_at_error` 的格式写出失败（F05 设计 2.8），但不调用它，因为第一行是完整路径（选择 8 和待定问题 D），最后一行是 `CHANGED_NOTHING` 或 `LEFT_BEHIND`，而不是 `RUN_CHECK`。以前没有模块为两种语言的名称准备提示，所以 `ENGLISH` 和 `CHINESE` 不重复任何内容。设置那一行使用 `Meal.label`、`and_list` 和 `Plural`，所以没有手工拼出的列表或复数（架构 8）。示例文字有两份是有意的（选择 2）。一份是开发者从不修改的测试数据（R08），F08 的一个测试让两份逐字节相同。第 0.2 版没有增加接口。 |
| 只依赖排序在前面的功能 | Pass | F08 使用 F01 和 F02 的 `lang`、F02 的 `text`、F03 和 F04 的 `datafile`，以及 F05 的 `app`、`settings` 和 `cli`。示例还用到 F03 的 `catalog` 和 F07 的 `check`，`check` 通过 F04 的 `recipes` 和 F06 的 `menus` 读取。它们都排在 F08 之前，并且在 main 上通过了测试。F05 是 F08 那一行的硬依赖，F03、F04 和 F07 是它的软依赖。给 F11、F13 和 F15 的安排只说明每个功能打算做什么，不约束任何后续设计。F08 只需要标准库，第 0.2 版也没有增加对功能或包的依赖。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | `datafile` 不知道任何示例数据，`init` 不知道任何文件名（选择 3）。`init` 传入 `DataFolder` 给出的路径和它的文字，并用 `folder.relative` 写出表格的每一行。各个计数和文字一起放在 `_example.py` 里，F08 的一个测试用 `read_catalog` 和 `read_pantry` 读回这些计数（选择 7）。`init` 既不用 `context.settings`，也不用 `context.today`。拒绝执行的提示使用 `cli` 按文件夹的设置选出的语言，和 F05 设计 2.10 给出的一样。`init` 和 `check` 之间的关联，即新文件夹上的“No errors. No warnings.”，是一个测试和 v0.1-S01，而不是一次引用。在模型上，对新文件夹运行 `check` 准确给出 F08 原型“In English”的第二段输出。第 0.2 版没有改动这些内容。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节写“无”是对的。`datafile` 增加三个名称和六条内部提示，和 F04、F05 给它增加名称一样。`COMMANDS` 里的那一项是架构 4 给每个命令功能的改动。第 0.2 版没有改动任何接口，所以第 1 轮的模型和测试结果仍然有效。放进模型后，分支上的测试结果是 405 个通过、3 个跳过，也就是分支收集到的 408 个测试，包括 F05-T48、F05-T49 和 F07-T17。所以 F01 到 F07 的测试都不用修改。这个 PR 只加入两个设计文件。待定问题 A 修改 F05 设计 2.10 的规则 4 或步骤 2，设计让它走变更流程。在这台电脑上，`os.path.abspath` 去掉最后一部分末尾的空格或点，保留中间某一部分末尾的空格，并把 `C:\x\..\y` 变成 `C:\y`。所以在选项 1 下，`tests/test_f05_data_folder.py` 里 F05 的 `x/../y` 用例在 Windows 上会改变，和设计说的一样。待定问题 D 修改的是架构 6，不是已实现的接口，Troy 在批准这份设计时决定它。把工作分成 mock 和实现是对的。测试既直接调用 `create_data_folder`，也通过 `init` 调用它，所以两个模块都必须在 mock 里能被引用，软限制的理由和 F05 的 mock 相同。把 `datafile` 的六条提示移到 PR 5，mock 里仍有 6 个文件，所以没有好处。发现 5 已解决。第 2 节现在列出了更多会在 mock 上通过的测试，比如只检查 `INIT_COMMAND` 的字段、`CreationOutcome` 的值、合法的 `Creation`，或者 `init extra` 和 `init --tag` 的测试。它要求每个这样的测试还要检查 mock 做错的内容（R09）。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 发现 1 和 2 是阻塞问题。架构师对照需求、架构、F05、F07 和 F08 原型、`example-data.md`，以及 v0.1-S01 到 v0.1-S03，检查了选择 1 到 10 和任务说明里的五点备注。每个文件有 12 个代码块，每个都与另一种语言的版本相同，两个文件的 707 行在标题、表格行和列表项上逐一对应。7 个 `python` 代码块都能解析。架构师在分支的代码之上按第 2 节和第 3 节建了模型，并把 `INIT_COMMAND` 放进 `COMMANDS`。模型用 Windows 上的 Python 3.13.18 运行了四个示例，每个断言和全部 8 个 `# raises` 都成立。模型准确给出 F08 原型的三段输出，两种语言都是，分支上的测试在模型上通过，405 个通过、3 个跳过。架构师按接口设计师的要求，在这台电脑上运行了选择 9 和 3.2 的失败。这个 PR 本身没有运行测试，因为它不改代码。 | 要求修改。接口设计师在两个文件里改正选择 9（发现 1），把失败时的完整路径写成交给 Troy 的一点（发现 2），并提高版本号。发现 3 到 5 不阻塞。对批准时的决定，架构师同意待定问题 A、B 和 C 的建议。按发现 1，问题 A 的选项 1 只对末尾的空格和两个以上的点有意义，因为一个点已经能正常使用。架构师也同意 2.2 和 3.2 里新的中文文字。`datafile` 的六段文字沿用读取提示，`init` 的文字在 F08 原型有的地方与原型相同。 |
| 2 | 没有阻塞问题。第 0.2 版按要求解决了发现 1 和 2，也采纳了发现 3 到 5。除了版本号和修改记录，只有选择 5、8 和 9，待定问题 A 和 D，说明待定问题个数的那一句，关于 mock 的那一段，2.2 里关于失败的那一段，以及 3.1 和 3.2 示例里的四行有改动。第 4 节保持第 1 轮留下的样子。两个文件的 722 行仍然在标题、表格行和列表项上逐一对应，每个文件的 12 个代码块都与另一种语言的版本相同。7 个 `python` 代码块都能解析，`ruff format` 认为它们已经格式化好。在第 1 轮的模型上，四个示例再次成立，每个断言和全部 8 个 `# raises` 都成立。F08 原型的三段输出、v0.1-S03、Ctrl+C 和 `LEFT_BEHIND` 也都成立。架构师还运行了选择 9 的 24 种情况、对只有一个点的文件夹运行的 `check`，以及 Ctrl+C 的两种新情况。3.2 的示例只在 scratchpad 里运行，没有像第 1 轮那样在 `D:\` 里运行。分支上的测试没有再运行，因为第 0.2 版没有改动接口，这个 PR 也不改代码。 | 批准。Troy 批准这份设计时，主会话把待定问题 A 到 D 和 2.2、3.2 里新的中文文字交给 Troy（R18）。架构师同意每个问题的建议。Troy 批准问题 D 的做法 1 后，架构师在 F08 的 mock PR 之前，用一个 `[docs]` PR 把这种情况加进架构 6。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-13 | 初稿。 |
| 0.2 | 2026-11-13 | 回应架构师审查第 1 轮。选择 9 写明，列出已有文件夹的内容能成功，所以空文件夹在 `recipes` 处失败，有条目的文件夹被拒绝。它还写明末尾只有一个点时能正常使用，因为 Windows 会去掉中间某一部分末尾的一个点。待定问题 A 写明一个点已经能正常使用。选择 8 和 2.2 写明失败时的完整路径偏离了架构 6 的哪条规则，待定问题 D 把它交给 Troy。选择 5 写明，在调用记下条目之前按的 Ctrl+C，以及删除过程中再按的一次 Ctrl+C，和进程被结束一样。第 2 节列出更多会在 mock 上通过的测试。3.1 和 3.2 的示例里有四行现在不超过 100 列。其中三行按 `ruff format` 的方式折行，3.1 最后一次调用里的警告移到一个变量里，所以它的 `# raises` 注释仍在那次调用的那一行。 |
| 1.0 | 2026-11-13 | Troy 批准。 |
