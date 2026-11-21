---
troy-doc: "F16-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-21"
status: "Troy 已于 2026-11-21 批准"
mirror-of: "design.md"
---

# F16 修改菜谱：接口设计

## 1. 功能

- 编号和名称：F16 修改菜谱
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F07

## 2. 接口

F16 在 `src/recipe_menu/commands/edit/` 里构建命令模块 `edit`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.edit` 导出一个名称 `EDIT_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出它。你输入的命令是 `recipe-menu edit ID`（2.2）。它的提示放在 `src/recipe_menu/commands/edit/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F16 在它的 mock PR 里把 `EDIT_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，放在 `ADD_COMMAND` 之后（选择 1）。这一项是命令功能对命令列表唯一的改动（架构 4，F05 设计 2.9）。F16 还按架构 5.1 的计划，给 `settings` 加上设置 `editor`：字段 `Settings.editor`（3.1）和 `read_settings` 的键 `editor`（3.2）。它不改动其他已实现的接口。`edit` 按各自设计的规定使用 F15 的 `Context.input`、`check_recipe` 和 `problem_block`，以及 F14 的 `read_file_text`；它不给 `Context` 加字段，也不给 `main` 加参数（选择 10）。F16 原型 `docs/prototypes/F16-edit.md` 展示了这个命令。F07 和 F15 为 F16 做的计划仍然成立：`edit` 用 `check_recipe` 检查菜谱，用 `problem_block` 写出它的问题，`problem_block` 的缩进就是原型里的缩进（F07 设计第 2 节，F15 设计第 2 节）。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F16 提供的接口 |
| --- | --- |
| `recipe-menu edit ID` 用设置里指定的编辑器打开这个菜谱的文件，默认用记事本（[需求 4](../../requirements.zh-CN.md#4-功能点)）。 | `recipe-menu edit`（2.2），以及 `EDIT_COMMAND`（2.1）。设置 `editor` 写出程序和它的选项，设置里没写时是 `notepad`（选择 3，3.1，3.2）。`edit` 找到这个程序，并把 `recipes/<id>.toml` 的完整路径作为最后一个参数启动它（选择 4）。 |
| 它等到你关闭编辑器。 | `edit` 等到它启动的程序结束（选择 5）。那个程序马上就结束、菜谱也没有变时，比如记事本在已经打开的窗口里打开这个文件时，`edit` 等你按 Enter（选择 6，D 点）。 |
| 然后检查这个菜谱。 | 再列一次 `recipes/`，然后是 `check_recipe`，以及原型里的报告：一个空行、计数行、`problem_block` 的各块，有错误时再加一行结尾（选择 7）。 |
| `add` 和 `edit` 复用 `check` 来检查一个菜谱（[架构 3](../../architecture.zh-CN.md#3-模块)）。 | F15 的 `check_recipe` 和 `problem_block`（F15 设计 3.4 和 3.5）。 |
| 在 v0.2，F16 给 `settings.toml` 加上编辑器（[架构 5.1](../../architecture.zh-CN.md#51-数据文件)）。 | `Settings.editor` 和键 `editor`（3.1 和 3.2）。 |

下面每个接口都遵守这些规则：

- `edit` 在包内只引用 `app`、`lang`、`text`、`datafile`、`recipes` 和 `check`。架构 3 里它那一行允许这些模块，`edit --> check` 是架构 4 里的一个箭头。它既不需要 `units`、`catalog`、`settings`、`menus`，也不需要 `shopping`：它通过 `context.settings.editor` 读取编辑器（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `edit` 只通过 `list_recipe_ids`、`read_file_text` 和 `check_recipe` 访问数据文件夹，这些函数都通过 `datafile` 工作（架构 8）。它不写任何文件：修改菜谱的是编辑器，`edit` 只读它。它只写入 `context.out` 和 `context.err`，只在选择 6 的提示处读 `context.input`。它启动一个程序，也就是编辑器，用 `subprocess.Popen` 启动，用 `shutil.which` 找到它（选择 4）。C 点要求架构给出允许这样做的规则。它不保存状态。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`edit` 在列表的第一个错误处用 `first_error` 和 `stop_at_error` 停下（F05 设计 2.8）。找不到编辑器、无法启动编辑器或编辑器出错结束，都不是数据里的错误：`edit` 往错误流写一行，并给出 1。只有 ID 违反 `is_recipe_id` 的规则时，`run` 才抛出 `UsageError`，这发生在它读任何文件之前（选择 2）。Ctrl+C 产生的 `KeyboardInterrupt` 继续传给 `cli`，`cli` 给出 130（选择 5）。`edit` 只捕获 `Popen` 的 `OSError`，以及它分段等待时的 `subprocess.TimeoutExpired`。传到 `cli` 的任何其他异常都是 bug。
- `EDIT_COMMAND` 是冻结的 `Command` 值（F05 设计 2.5）。F16 不增加值类型。`Settings.editor` 是 `str` 组成的元组（3.1）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F16 的接口都没有性能指标。PT01 不为 `edit` 计时（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。选择 12 说明 F16 给其他每个命令的启动增加了什么。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 和第 3 节给出它们的规则。

1. **一个命令，在帮助里紧接在 `add` 之后。** 按 F15 设计第 2 节的计划，F16 把 `EDIT_COMMAND` 加在 `COMMANDS` 里 `ADD_COMMAND` 的后面。所以 `COMMANDS` 变成 `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, ADD_COMMAND, EDIT_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`。处理菜谱的几个命令放在一起：`list`、`show`、`search`、`add` 和 `edit`。`edit` 有 `FolderUse.READ`，所以数据文件夹不存在或设置有错误时，`cli` 不运行它（F05 设计 2.5），这是 v0.2-S14 第 6 步的要求。它声明必需的参数 `ID`，和 `show` 一样，两种语言里都叫 `ID`，不声明选项。所以两种语言里它的用法都是 `edit ID`，占 7 列。`menu suggest [WEEK]` 占 19 列，仍是最宽的第一格，所以两种语言里两张表的第二列仍从第 24 列之后开始。`edit` 那一行让它下面的各行往下移一行，帮助的其他行都不变。帮助共 24 行（2.1）。已验收功能的测试都不依赖 `add` 后面的那一行（第 3 节）。
2. **ID，以及 `edit` 启动编辑器之前读什么。**
   - `edit` 在读任何文件之前用 `is_recipe_id` 检查 `ID`（F04 设计 2.4）。违反规则的值，比如 `Mapo`、`../rice`、`""` 或 `con`，给出 `UsageError(NOT_A_RECIPE_ID, None, id=value)`，`cli` 以 2 退出，和 `show` 一样（F09 设计，选择 7）。这条提示已经说了该运行什么，所以它不带提示行（ADR-0008）。
   - 然后 `edit` 用 `list_recipe_ids` 列出 `recipes/`。列表的第一个错误会让 `edit` 用 `stop_at_error` 停下，就像它让 `show` 和 `add` 停下一样（F09 设计，选择 2）。所以像 `recipes\Rice Bowl.toml` 这样的条目也会让 `edit` 停下。列表里没有这个 ID 时，`edit` 往错误流写 `UNKNOWN_ID`，并给出 1。这就是原型“An unknown ID”里的那一行，也是 `show` 遇到未知 ID 时的那一行（F09 设计 2.4）。`edit` 拿 ID 和列表里的 ID 逐字比较，所以 Windows 和 Linux 的结果相同。所以 `edit` 从不为 `tomato-egg` 打开 `Tomato-Egg.toml`，而 `read_recipe` 在 Windows 上会这样做（F15 设计 3.4）。
   - `edit` 自己保留一份 `NOT_A_RECIPE_ID` 和 `UNKNOWN_ID`，文字和 `show` 的相同，因为架构 3 不允许 `edit` 引用 `browse`，而 `browse` 把它们留在内部（选择 13）。
   - 编辑器启动之前，`edit` 只读列表和这个菜谱文件的文字，后者用 `read_file_text` 读，供选择 6 使用。它不读目录、常备清单、菜单，也不读别的菜谱。`cli` 已经读了设置（F05 设计 2.10），`edit` 从 `context.settings` 取编辑器。目录只在编辑器之后由 `check_recipe` 读一次。编辑器开着的时候你可能修改目录，而且目录里的错误不应该让你打不开菜谱。所以目录有错误时，编辑器之前什么也不会停下，编辑器之后的检查会写出这个错误（选择 7）。
3. **设置 `editor`**（3.1 和 3.2）。
   - `settings.toml` 可以有键 `editor`，它的文字写出一个程序和它的选项，比如 `editor = "code --wait"`。没有这个键时，编辑器在每个系统上都是 `notepad`。所以 `Settings.editor` 默认是 `("notepad",)`，文件里写 `editor = "notepad"` 得到的设置也一样。
   - 这段文字按一条规则拆成词，Windows 和 Linux 上相同。英文双引号以外的空白把词分开。一个英文双引号开始或结束一个带引号的部分，它本身不属于词，所以带空格的路径放在英文双引号里。一个词可以把带引号的部分和普通部分连在一起，比如 `--file="a b"`；单独的 `""` 是一个空词。其他每个字符都代表它自己，包括 `\` 和 `'`，所以 Windows 路径在值里不需要转义。没有字符能转义英文双引号，所以词里不能有它，Windows 上的路径也不会有它。空白指 `str.isspace` 认为是空白的字符，和 `str.strip` 去掉的一样。第一个词是程序，其他词是它的选项。

     | `settings.toml` 里的那一行 | `Settings.editor` |
     | --- | --- |
     | 没有键 `editor` | `("notepad",)` |
     | `editor = "notepad"` | `("notepad",)` |
     | `editor = "code --wait"` | `("code", "--wait")` |
     | `editor = "  code   --wait  "` | `("code", "--wait")` |
     | `editor = '"C:\Program Files\Notepad++\notepad++.exe" -multiInst -nosession'` | `("C:\Program Files\Notepad++\notepad++.exe", "-multiInst", "-nosession")` |
     | `editor = 'code --file="a b"'` | `("code", "--file=a b")` |
     | `editor = 'code ""'` | `("code", "")` |

   - TOML 把英文双引号里文字中的 `\` 当作转义，所以 `editor = "C:\Program Files\..."` 是语法错误，`read_toml` 会连同它所在的行一起报告（F03 设计 2.3）。那条提示已经说了要把文字放在单引号里。TOML 文字放在单引号里时，每个 `\` 都保持原样，就像上表第五行那样。
   - 错误的值是 `editor` 这个位置上的错误，和其他键一样。不是文字的值给出 `NOT_A_TEXT`，空的或只有空白的文字给出 `EMPTY_TEXT`，两者都是 `datafile` 的提示（F03 设计 2.10），由 `read_text` 给出（F04 设计 3.2）。文字在带引号的部分里结束、第一个词是空的（比如 `'"" --wait'`），或者某个词里有 U+0000 时，给出 `EDITOR_NOT_A_COMMAND`。最后一种情况让 `subprocess` 不会因为空字符抛出 `ValueError`。
   - 设置里有错误时，除了 `check` 和 `init`，每个命令都会停下（F05 设计 2.5）。所以错误的 `editor` 也会让 `list` 和 `show` 停下，就像错误的 `dishes` 一样（F14 设计 3.2），`check` 会报告它。
   - 文件顶层的键是 `language`、`meals`、`servings`、`dishes` 和 `editor`，按这个顺序，所以 `UNKNOWN_KEY` 列出这五个键。
   - `init` 写设置文件时不写这个键，就像它不写 `dishes` 一样（F14 设计，选择 5）。所以 F16 不改动 `init` 写的任何文件，v0.1-S01、v0.1-S02 和 v0.1-S13 都成立，和 v0.2 测试计划预期的一样。
4. **`edit` 怎样找到并启动编辑器**（C 点）。
   - `program` 是 `context.settings.editor` 的第一个词，其他词是它的选项。`edit` 用 `shutil.which(program)` 找这个程序。带文件夹部分的程序，比如 `C:\Tools\ed.exe` 或 `./ed`，就在那个路径上找，相对路径从当前文件夹算起。不带文件夹部分的程序在 `PATH` 的各个文件夹里找。在 Windows 上，`shutil.which` 先找当前文件夹，和 `cmd.exe` 一样，并逐个尝试 `PATHEXT` 里的扩展名，所以 `code` 能找到 `code.cmd`，`stand-in-editor` 能找到 `stand-in-editor.cmd`。在 Linux 上，它找你有权运行的文件，包括以 `#!` 开头的脚本。什么也没找到时，`edit` 往错误流写 `EDITOR_NOT_FOUND`，并给出 1。
   - 默认的 `notepad` 在 Windows 上找到 `C:\Windows\System32\notepad.exe`。Linux 上没有 `notepad`，所以在那里没有这个键时 `edit` 给出 `EDITOR_NOT_FOUND`，这条提示会说怎样写出一个编辑器。CI 在 Linux 上运行，没有测试需要记事本（选择 10）。
   - `edit` 用 `subprocess.Popen` 启动列表 `[found, *options, str(path)]`，其中 `found` 是 `shutil.which` 给出的结果，`path` 是 `context.folder.recipe_file(recipe_id)`，也就是这个菜谱文件的完整路径。无论它的文件夹里有什么空格，这个文件总是最后一个参数，而且是一个参数。`Popen` 不带 `shell`、`env`、`cwd`，也不带流。所以编辑器得到 `recipe-menu` 的环境、当前文件夹和控制台，就像你在 PowerShell 里输入它的名字一样。有自己窗口的编辑器，比如记事本或 VS Code，不使用控制台。
   - 在 Windows 上，`Popen` 把命令行交给 `CreateProcess`；它拿到 `.cmd` 或 `.bat` 文件的完整路径时，会自己通过 `cmd.exe` 运行这个文件。所以 `code.cmd` 和测试计划里的 `stand-in-editor.cmd` 不用 `shell=True` 也能启动。`cmd.exe` 按它自己的规则读批处理文件的参数，并展开其中的 `%NAME%`，所以数据文件夹的路径里有 `%` 时，批处理编辑器得到的路径会变。`.exe` 编辑器得到的每个参数都和写的一样。
   - `Popen` 抛出 `OSError` 时，比如没有访问权限，或者文件不是 Windows 能运行的程序，`edit` 往错误流写 `EDITOR_NOT_STARTED`，带上系统给出的原因（和 `datafile` 一样，是 `error.strerror`，没有时是异常类型的名称），并给出 1。
   - 编辑器启动之后，`edit` 写出第一行，并调用 `context.out.flush()`，让这一行在编辑器开着的时候就显示出来。`context.settings.editor` 是 `("notepad",)` 时，这一行是原型里的 `OPENED_IN_NOTEPAD`；否则是 `OPENED_IN_EDITOR`，带上设置里写的程序，比如 `Opened recipes\mapo-tofu.toml in "code". Close the editor when you are done.`。`edit` 在启动之后才写这一行，所以它从不说自己打开了一个没能打开的文件。在控制台里运行的编辑器可能会盖住这一行。
   - `edit` 在启动编辑器的那个内部函数里引用 `subprocess` 和 `shutil`（选择 12），并以 `subprocess.Popen` 和 `shutil.which` 的形式调用它们，所以测试可以用 pytest 的 `monkeypatch` 替换其中任何一个（选择 10）。ruff 会标出 `Popen` 的调用（`S603`）和函数里的引用（`PLC0415`），所以这几行各带一条写明理由的 `noqa` 注释，就像代码对 `S311` 做的那样。
5. **等待编辑器，以及 Ctrl+C。**
   - `edit` 等到它启动的程序结束。它在循环里用 `Popen.wait(timeout=0.5)` 等待，程序一结束这个调用就返回。在 Windows 上，Python 等待进程时不会因为 Ctrl+C 醒来；每次等半秒，就能让 Ctrl+C 在两个系统上都生效。
   - `edit` 等待时按 Ctrl+C 会抛出 `KeyboardInterrupt`，`edit` 不捕获它。`cli` 给出 130，不再写出任何东西（架构 6，F05 设计 2.10）。`edit` 不会关掉编辑器：`Popen.wait` 像 Python 在 Ctrl+C 之后做的那样，给编辑器四分之一秒结束，然后让它继续运行。所以编辑器连同你输入的内容一直开着，你保存过的仍然保存着，也不运行检查。在控制台里运行的批处理编辑器，比如 `code.cmd`，也会收到 Ctrl+C，`cmd.exe` 这时可能会问是否终止批处理作业。
   - 程序结束时的退出码不是 0 时，`edit` 往错误流写 `EDITOR_FAILED`，带上这个退出码，不做检查，并给出 1。这样的退出码说明编辑器没有按设置的意思运行，比如选项写错了。记事本和 `code --wait` 都以 0 结束。
6. **马上就结束的编辑器**（D 点）。在 Windows 11 上，记事本可能把文件作为已经打开的窗口里的一个标签页打开。这时 `edit` 启动的 `notepad.exe` 把文件交出去后马上就结束，你还什么都没改。不带 `--wait` 的 `code` 也一样。
   - 程序在 `edit` 启动它之后不到 2 秒就以退出码 0 结束，而且 `read_file_text` 这时给出的结果和启动之前一样（选择 2）时，`edit` 认为这是这样一次交接。它写出提示 `QUICK_EXIT`（结尾不换行），调用 `context.out.flush()`，然后从 `context.input` 读一行，和 `add` 读回答的方式一样（F15 设计，选择 4）。`context.input.isatty()` 为假时，`edit` 接着写出读到的那一行（去掉末尾的 LF）和一个换行；输入结束时只写一个换行。不管这一行是什么，输入结束时也一样，`edit` 都接着做检查。
   - 所以你先看到第一行，然后是这个提示。你在记事本里保存这个菜谱，愿意的话关掉它的标签页，然后按 Enter。接着 `edit` 检查这个菜谱。
   - 改过文件的编辑器，比如 v0.2-S12 里的替身，或者启动 2 秒以后才结束的编辑器，走普通的路，`edit` 马上做检查。只有你本来就不想改、在记事本启动后 2 秒内没改就关掉它时，才会看到这个提示，这时按一次 Enter 就接着做检查。
   - `edit` 用 `time.monotonic()` 计这 2 秒，从 `Popen` 之前一刻算到等待结束。这是一段时长，不是今天的日期，所以架构 8 没有把它交给 `cli`。测试可以用一个马上结束（改或不改文件）或者等 2 秒以上的替身，分别走到这条规则的两边。
   - 在提示处按 Ctrl+C 给出 130，和在 `add` 的问题处一样。
7. **编辑器之后的检查。**
   - `edit` 再用 `list_recipe_ids` 列一次 `recipes/`，因为编辑器或者你可能删除了文件，或给它改了名。这次列表的第一个错误会让 `edit` 用 `stop_at_error` 停下，和编辑器之前一样。所以在 Windows 上，文件改名成 `Mapo-Tofu.toml` 时，`edit` 会带着这个名称的错误停下。列表里不再有这个 ID 时，`edit` 往错误流写 `GONE`，并给出 1。所以 `check_recipe` 得到的是编辑器结束之后那次列表里的 ID，这是 F15 设计 3.4 的要求。
   - 然后 `check_recipe(context.folder, recipe_id)` 给出问题：先是目录的错误，再是这个菜谱的问题（F15 设计 3.4）。无论退出码是几，`edit` 都把报告写到输出流，因为它是一次检查的报告，这是 v0.2 测试计划的规则“The report of `add` and `edit`”说的（架构 6）。
   - 报告是一个空行、计数行、错误的 `problem_block`、然后是警告的 `problem_block`（F15 设计 3.5），有错误时再加结尾一行。没有问题时计数行是 `CHECKED_CLEAN`，只有警告时是 `CHECKED_WARNINGS`，有错误时是 `CHECKED_PROBLEMS`。每个错误都在这个菜谱的文件里时，结尾一行是 `EDIT_AGAIN`，和原型一样。有错误在别的文件里时，比如目录读不出来，结尾一行是 `FIX_AND_CHECK`，因为修改菜谱改正不了它。
   - 有问题是错误时，`edit` 给出 1，否则给出 0，因为警告从不改变退出码（架构 6）。
   - `edit` 自己从不写这个菜谱，也不写别的任何文件。只有编辑器修改文件，所以 v0.2-S15 和 v0.2-S16 看到的只是编辑器做的修改。
8. **各行怎样写出文件名**（B 点）。第一行写出这个菜谱文件相对于数据文件夹的路径，也就是 `str(context.folder.relative(path))`，比如 Windows 上的 `recipes\mapo-tofu.toml` 和 Linux 上的 `recipes/mapo-tofu.toml`，和原型的写法一样。报告和 `stop_at_error` 的各行是问题，它们也这样写出各自的文件（架构 6）。`edit` 的其他行都不写文件名：`UNKNOWN_ID`、`GONE`、`EDIT_AGAIN` 和各个计数行写的是 ID，关于编辑器的各行写的是设置里的程序。架构 6 规定，不是问题的提示用完整路径写出文件，ADR-0009 要求其他每种情况各自修改架构 6。所以第一行需要一次这样的修改，就像 `menu suggest` 的换菜那一行一样（ADR-0011）。两种做法下，编辑器得到的都是完整路径。
9. **启动程序，以及架构**（C 点）。架构 4 说只有 `cli` 接触外部世界，架构 8 列出只有 `cli` 读取的东西，其中包括环境变量。两处都没有说到启动另一个程序。`edit` 启动编辑器。`shutil.which` 从进程的环境里读取 `PATH`，在 Windows 上还读取 `PATHEXT`；编辑器得到这个环境、当前文件夹和控制台。需求要的正是这个程序。按 C 点的做法 1，架构 8 增加一条规则：`edit` 启动设置里指定的编辑器并等它结束，其他模块都不启动程序。架构师在 F16 的 mock PR 之前，用一个 `[docs]` PR 把这条规则写进架构 4 和 8，并写一份 ADR。“不联网”这条规则仍然成立：这个工具从不使用网络，编辑器是你自己选的程序，比如 VS Code，它可能会联网。
10. **测试，以及 CI 上的编辑器。** 没有测试启动记事本、VS Code 或任何其他真正的编辑器，也没有测试需要控制台。
    - 测试在 `settings.toml` 里用完整路径写出一个替身编辑器：测试自己的 Python，即 `sys.executable`，以及一个按测试要求修改文件后就结束的脚本。它不打开窗口，也不读控制台，所以能在没有控制台的 CI 上运行。它得到 pytest 捕获的那些流。
    - 测试默认情况（没有键 `editor`）时，用 `monkeypatch` 设置 `PATH`：设成一个空文件夹，测 `EDITOR_NOT_FOUND`；或者设成一个放着名为 `notepad` 的替身的文件夹，替身在 Windows 上是 `notepad.cmd`，在 Linux 上是一个可执行脚本。它还用 `monkeypatch.chdir` 换到一个临时的当前文件夹，因为在 Windows 上 `shutil.which` 先找那里。
    - 需要 `Popen` 抛出 `OSError`，或者需要等待时抛出 `KeyboardInterrupt` 的测试，用 `monkeypatch` 替换 `subprocess.Popen`（选择 4）。
    - 所以 `edit` 不需要 `Context` 的新字段，也不需要 `main` 的新参数。逐字比较 `Context` 各字段名称的 F15-T03 仍然成立。版本测试按 v0.2 测试计划的规则“The stand-in editor”，把 `stand-in-editor.cmd` 放到进程的 `PATH` 上。
11. **提示里的数字。** `edit` 的提示显示 ID（它符合 `is_recipe_id`）、问题的个数，以及编辑器的退出码。退出码是系统给出的数：在 Windows 上最多 10 位，在 Linux 上因信号结束时是一个小的负数。文件里的问题只通过 `stop_at_error` 和 `problem_block` 进入输出，而读取函数把文件里的数字限制在 15 位以内，或者显示文件里的原文（F04 设计，选择 2）。所以 `edit` 的提示都碰不到 F02 的 4,300 位限制（F02 设计 2.3）。
12. **速度。** 没有性能指标提到 `edit`。在 PT01 的数据文件夹上，它列两次 1,000 个条目，读 300 种食材的目录和一个菜谱，所以它自己读取的时间和 `show` 差不多，v0.1.0 发布测试里 `show` 是 0.164 秒（v0.2 测试计划第 3 节）。其余是你在编辑器里的时间。v0.2-S16 在 PT01 文件夹上运行 `edit`，不计时。其他命令的启动变化很小。`cli` 启动时引用 `edit` 的几个小文件，花几毫秒，和 F15 一样（F15 设计，选择 14）。`read_settings` 多读一个键。`edit` 只在启动编辑器的那个函数里引用 `subprocess` 和 `shutil`，以及它们引用的模块，比如 `threading`（选择 4），所以其他命令都不加载它们。`time` 是 Python 内置的。F15 之后，在 Troy 的电脑上 `check` 在 PT01 下约用 0.86 秒，所以它还剩约 140 毫秒。这些时间没有为 F16 测量过，v0.1 的 PT01 用例会在 v0.2 的发布测试里再运行一次。
13. **只导出命令。** `edit` 只导出 `EDIT_COMMAND`。只有 `cli` 可以引用 `edit`（架构 3），所以别的名称不会有使用者。`edit` 自己保留几份文字相同的副本：`browse` 的 `ID_ARGUMENT`、`NOT_A_RECIPE_ID` 和 `UNKNOWN_ID`，以及 `add` 的 `ERROR_COUNT`、`WARNING_COUNT` 和 `FIX_AND_CHECK`，因为这些模块把它们留在内部（架构 8）。以后的 `[refactor]` PR 可以让它们共用。

用到 `edit` 的 v0.2 场景在这些选择下都成立：

- v0.2-S12：第 1 步启动 `stand-in-editor.cmd` 一次，把 `recipes\mapo-tofu.toml` 的完整路径作为它的最后一个参数（选择 4）。它的第一行是 `Opened recipes\mapo-tofu.toml in "stand-in-editor". Close the editor when you are done.`。替身改了文件，所以替身结束时 `edit` 就检查这个菜谱（选择 6），并打印原型里第一行之后的那几行，退出码 1。第 2 步打印 `已用“stand-in-editor”打开 recipes\mapo-tofu.toml。改完后关闭编辑器。`、一个空行和 `已检查 mapo-tofu：没有错误。`，退出码 0。第 3 步打印 F07 “After the fixes”的输出。
- v0.2-S13：第 1 步打印原型“An unknown ID”的那一行，退出码 1；第 2 步在 stderr 上打印 `An argument is missing. Write "recipe-menu edit ID".` 和 `Run "recipe-menu --help" to see the commands.`，退出码 2（F05 设计 2.10）。这两步里替身都不运行（选择 2）。第 3 步的错误在这个菜谱的文件里，所以结尾一行是 `Run "recipe-menu edit tomato-egg" to fix it.`，退出码 1。
- v0.2-S14：帮助在 `add` 那一行后面紧跟着多了 `edit` 那一行，第二列仍在第 24 列之后（2.1）。第 6 步打印 `cli` 的 `NO_DATA_FOLDER` 和 `RUN_INIT`，以 1 退出，这发生在 `edit` 列出任何东西之前（选择 1）。
- v0.2-S15：第 3 步不改动任何文件或文件夹。`edit` 什么也不写，它只读列表、这个菜谱和目录。没有改文件、2 秒内就结束的替身会得到选择 6 的提示，`edit` 在输入结束时接着做检查。所以测试经理要么给第 3 步一个空的标准输入并要求出现这个提示，要么让这一步的替身等 2 秒以上。
- v0.2-S16：这个菜谱没有警告时，第 3 步以 `Checked recipe-1000: no errors.` 结束；选择 6 的规则和 v0.2-S15 一样适用。
- v0.2-S19：第 1 步和第 2 步里没有打开的记事本窗口，所以 `edit` 启动的 `notepad.exe` 就是那个窗口，`edit` 一直等到你关闭它。第 3 步里，记事本把菜谱作为你那个窗口的一个标签页打开时，`edit` 在第一行之后显示选择 6 的提示，你按 Enter 之后它检查这个菜谱。记事本打开自己的窗口时，`edit` 一直等到你关闭它，和第 1 步一样。不管哪种情况，`edit` 接着都打印一个空行和 `Checked tomato-egg: no errors.`。所以测试经理在第 3 步里加上“`edit` 要求时再按 Enter”，并在预期结果里写上这两种情况。
- v0.1-S01、v0.1-S02 和 v0.1-S13：F16 不改动 `init` 或 `menu new` 写的任何文件，`init` 也不写键 `editor`（选择 3）。

这四点由 Troy 决定。设计采用了每一点的建议。

- **A. 新的文字。** 原型给出了两种语言里记事本的那一行、一个错误时的英文计数行和英文结尾一行，以及没有错误时的中文计数行。其他文字都沿用原型或某条已有提示的措辞。`edit` 有 18 条提示，列在 2.2 里；`settings` 多了 2 条，列在 3.2 里。这 20 条里有 6 条是已有提示的副本，1 条 `OPENED_IN_NOTEPAD` 完全来自原型。建议按 2.2 和 3.2 的写法接受其余 13 条：
  - 帮助里的那一行：`Edit a recipe in your editor, then check it.` 和 `在编辑器里修改一个菜谱，然后检查它。`。
  - 设置里写了编辑器时的第一行：`Opened {file} in "{editor}". Close the editor when you are done.` 和 `已用“{editor}”打开 {file}。改完后关闭编辑器。`。
  - 原型没有显示的计数行：`Checked {id}: no errors.`、`Checked {id}: no errors, 1 warning.`、`已检查 {id}：没有错误，有 1 个警告。` 和 `已检查 {id}：有 1 个错误和 2 个警告。`。中文的结尾一行：`运行“recipe-menu edit {id}”改正它。`。
  - 编辑器马上就结束时的提示（D 点）：`The editor closed at once, maybe because it opened the recipe in a window that was already open. When you have saved the recipe there, press Enter: `。
  - 找不到编辑器、无法启动编辑器或编辑器出错结束时的各行，以及菜谱不见了时的那一行，比如 `Cannot start the editor "code": no program of that name was found. Name your editor in settings.toml, such as editor = "code --wait".`。
  - 位置 `editor` 和 `编辑器`，以及值拆不开时的问题：`"editor" must name a program and then its options, such as editor = "code --wait". Put a path with spaces in double quotation marks, and close each one.`。
- **B. 第一行怎样写出文件名**（选择 8）。
  - 做法 1，推荐：写相对于数据文件夹的路径，和原型的写法一样：`Opened recipes\mapo-tofu.toml in Notepad. Close Notepad when you are done.`。架构 6 为这一行增加一种情况。架构师在 F16 的 mock PR 之前，用一个 `[docs]` PR 把它写进架构 6，并写一份 ADR，就像 ADR-0011 记录 F14 设计的 D 点那样。
  - 做法 2：写完整路径，比如 `Opened C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml in Notepad. …`，这是架构 6 对不是问题的提示的规定。F16 原型两段的第一行在 F16 测试计划之前走需求变更流程修改，选择 8、2.2 和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：它保留了 Troy 批准的原型里的那一行，而且这一行写出文件名的方式和它下面检查的各行一样。
- **C. `edit` 怎样启动编辑器**（选择 4、9 和 10）。
  - 做法 1，推荐：`edit` 在 `shutil.which` 从 `PATH` 上找到编辑器之后，自己用 `subprocess.Popen` 启动它，编辑器得到 `recipe-menu` 的环境、当前文件夹和控制台。架构 4 和 8 增加选择 9 的规则，架构师在 F16 的 mock PR 之前用一个 `[docs]` PR 把它连同一份 ADR 写下来。测试在设置里写出一个替身编辑器。
  - 做法 2：由 `cli` 替命令启动程序。`Context` 多一个新字段，它是一个启动程序并等它结束的函数，由 `main` 填入，测试在进程里用替身替换它。`edit` 调用它。逐字比较 `Context` 各字段名称的 F15-T03 要在 mock PR 之前由一个修测试的 PR 修改，架构 5.2 里 `Context` 那一行也要改。选择 4、5、9 和 10、第 3 节和各个示例在 mock PR 之前修改。
  - 推荐做法 1 的理由：只有 `edit` 启动程序，而且需求点名了这个程序，所以一条规则就够了。做法 2 给每个命令的上下文都加了一个只有一个命令用的字段，而且它的测试仍然需要一个替身来测真正的启动。
- **D. 马上就结束的编辑器**（选择 6）。
  - 做法 1，推荐：编辑器在 2 秒内以退出码 0 结束、菜谱也没有变时，`edit` 写出选择 6 的提示，等你按 Enter 之后再检查。
  - 做法 2：`edit` 启动的程序一结束，`edit` 就做检查。已经有记事本窗口开着时，检查会马上进行，在你修改任何东西之前。你需要先关掉所有记事本窗口，或者把记事本设成在新窗口里打开文件。选择 6 和各个示例在 mock PR 之前修改，测试经理把 v0.2-S19 第 3 步的预期结果改成马上检查。
  - 推荐做法 1 的理由：不管记事本怎样打开文件，检查都仍然在你修改之后进行；用不带 `--wait` 的 `code` 这样的编辑器时也一样。

没有后续功能在 F16 的基础上构建。它是排序里的最后一个功能，也是 v0.2 的最后一个功能。

troy-mode 的流程有一个 mock PR 和一个实现 PR。`COMMANDS` 里的这一项、字段 `editor` 和键 `editor` 都不会让已验收功能的测试失败（第 3 节），所以 mock PR 之前不需要修测试的 PR。

mock（PR 3）包含 `src/recipe_menu/commands/edit/__init__.py`、`messages.py`、放 `run` 的一个内部文件（比如 `_run.py`），以及 `src/recipe_menu/cli/_commands.py` 里的那一项。它给 `Settings` 加上带默认值的字段 `editor`，不带 3.1 的检查，并把 3.2 的两条提示加进 `src/recipe_menu/settings/messages.py`。它让 `read_settings` 保持原样，所以在那里 `editor` 仍是未知键。它定义每条提示和字段齐全的 `EDIT_COMMAND`。它的 `run` 什么也不检查、不读文件、不启动任何东西、不写任何东西，并给出 0。所以检查以下内容的新测试在 mock 上会失败（R09）：输出的某一行、`edit` 给出的退出码 1 或 2、错误流上的某一行、替身得到的参数、替身做的修改、键 `editor` 的某个问题、列出五个键的 `UNKNOWN_KEY` 文字，或者对 `Settings.editor` 的检查。这些测试在 mock 上会通过，从而违反 R09：只检查 `EDIT_COMMAND` 的字段、帮助、某条提示、退出码 0、空的错误流、`Settings.editor` 的默认值，或者设置是否相等的测试。检查 `cli` 在运行 `edit` 之前做的事的测试也是如此，比如数据文件夹不存在、设置损坏、没有 ID、两个 ID、未知选项或 `edit --help`。只检查一次运行没有写文件或没有启动替身的测试也是如此。每个这样的测试都还要检查 mock 做错的内容，比如输出。按估计，mock 改动 6 个文件，约 200 行，文件数超过 R03 的 5 个，所以它的说明要写明软限制的理由：测试既直接用到设置和 `edit`，也通过 `main` 用到它们，所以它们要在同一个阶段一起带上，和 F14 与 F15 的 mock 一样。

实现（PR 5）把 `run` 放在 `edit` 的内部文件里，包括对 ID 的检查、两次列表、找到并启动编辑器、等待、提示和报告，比如 `_run.py`、`_editor.py` 和 `_report.py`。它还包括 `Settings.editor` 的检查，以及 `settings` 里读取和拆分键 `editor` 的代码，比如在 `_settings.py`、`_read.py` 和 `_read_parts.py` 里。按估计，它改动约 7 个文件，约 450 行，文件数超过 R03 的 5 个，所以它的说明也要写明软限制的理由：`edit` 的测试同时需要这些部分。开发工程师要早一点运行 troy-check。

### 2.1 `EDIT_COMMAND`

- 模块：edit
- 功能：对 `edit` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹和设置，并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 按 2.2 的规定，用设置里的编辑器打开这个菜谱的文件，等它结束，然后检查这个菜谱。

签名：

```python
EDIT_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("edit",)
#   help_line = EDIT_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(ID_ARGUMENT)
#   options = ()
#   folder = FolderUse.READ
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 组成的元组 | `("edit",)`。 | 无 |
| `help_line` | `Message` | `EDIT_HELP`：“Edit a recipe in your editor, then check it.”和“在编辑器里修改一个菜谱，然后检查它。”。 | 没有占位符。 |
| `run` | 接受一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 按 2.2 的规定检查 ID、列出 `recipes/`、启动编辑器、等它结束，并检查这个菜谱。 | 给出 0 或 1。只有 ID 违反 `is_recipe_id` 的规则时才抛出 `UsageError`，这发生在它读任何文件之前。遇到坏数据、无法启动的编辑器或出错的编辑器都不抛异常。让 `KeyboardInterrupt` 继续传给 `cli`。 |
| `argument` | `Argument` | `Argument(ID_ARGUMENT)`，必需、不重复，两种语言里都叫 `ID`。 | 无 |
| `options` | 空元组 | `edit` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.READ`：数据文件夹不存在或设置有错误时，`cli` 不运行 `edit`（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西（F05 设计 2.4，F15 设计 3.1）。 | `run` 用到 `context.lang`、`context.folder`、`context.settings.editor`、`context.out`、`context.err` 和 `context.input`。它既不用 `context.today`，也不用 `context.random`。 |
| `arguments` | `Arguments` | 命令行给 `edit` 的东西（F05 设计 2.6）。 | `arguments.values` 是 `(ID,)`，因为 `cli` 检查值的个数。它没有选项。 |

- 返回值：`EDIT_COMMAND`，一个 `Command`。
  - 两种语言里 `EDIT_COMMAND.usage` 都是 `edit ID`。所以帮助显示 `edit ID`，用法错误引用 `recipe-menu edit ID`。
  - `EDIT_COMMAND.run(context, arguments)` 按 2.2 的步骤执行，用 `context.lang` 写出各行，并给出 0 或 1。

F16 之后，帮助列出这些命令和选项，第二列和 F14、F15 之后一样，在第 24 列之后（选择 1）。帮助的其他行是 F05 原型里的那些行。英文：

```text
Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  add                   Add a recipe by answering questions.
  edit ID               Edit a recipe in your editor, then check it.
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
  edit ID               在编辑器里修改一个菜谱，然后检查它。
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

错误：`ID` 的值 `value` 让 `is_recipe_id(value)` 为假时，`run` 抛出 `UsageError(NOT_A_RECIPE_ID, None, id=value)`（选择 2）。它不会有意抛出别的异常。

- 副作用：2.2 的那些副作用。`run` 列两次 `recipes/`，通过 `read_file_text` 读这个菜谱的文件，启动编辑器并等它结束，可能从 `context.input` 读一行，通过 `check_recipe` 读目录和这个菜谱，并写入 `context.out` 或 `context.err`。它不写任何文件。
- 性能指标：无

示例：

这个示例里，`home` 是一个空的临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。帮助来自 `COMMANDS`，F16 之后它有十一个命令。

```python
import io
from datetime import date

from recipe_menu.app import Argument, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.edit import EDIT_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

assert EDIT_COMMAND.words == ("edit",)
assert EDIT_COMMAND.usage == BiText("edit ID", "edit ID")
assert EDIT_COMMAND.help_line.render(Lang.EN) == "Edit a recipe in your editor, then check it."
assert EDIT_COMMAND.help_line.render(Lang.ZH) == "在编辑器里修改一个菜谱，然后检查它。"
assert EDIT_COMMAND.argument == Argument(Message("ID", "ID"))
assert EDIT_COMMAND.options == ()
assert EDIT_COMMAND.folder is FolderUse.READ


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
assert len(english) == 24
assert english[10:13] == [
    "  add                   Add a recipe by answering questions.",
    "  edit ID               Edit a recipe in your editor, then check it.",
    "  menu new [WEEK]       Create an empty week menu.",
]
assert english[18].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[11] == "  edit ID               在编辑器里修改一个菜谱，然后检查它。"
```

### 2.2 `recipe-menu edit`

- 模块：edit
- 功能：用设置里指定的编辑器（默认是记事本）打开一个菜谱的文件，等到你关闭编辑器，然后检查这个菜谱的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 和 [4](../../requirements.zh-CN.md#4-功能点)）。F16 原型展示了它。

签名：

```text
recipe-menu edit ID [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `ID` | 一个菜谱 ID | 要修改的菜谱，比如 `mapo-tofu`。 | 正好一个值。它符合 `is_recipe_id` 的规则，`recipes/` 里有它的文件。 |
| `--lang` | `en` 或 `zh` | 每一行的语言。它不改变文件，也不改变编辑器。 | 按 F05 设计 2.10 的规定。没有这个选项时，用设置里的语言，否则用英文。 |
| `--data` | 一个文件夹 | 数据文件夹。 | 按 F05 设计 2.10 的规定。没有这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（2.1），不运行 `edit`。 | 无 |
| 设置 `editor` | `settings.toml` 里的一段文字 | 程序和它的选项（选择 3）。 | 没有这个键时是 `notepad`。 |
| 标准输入 | 若干行文字 | 只在选择 6 的提示处读。 | 任何文字。输入结束时接着做检查。 |

`edit` 按顺序执行这些步骤。`recipe_id` 是 `ID` 的值，`path` 是 `context.folder.recipe_file(recipe_id)`，`program` 是 `context.settings.editor[0]`。

1. `is_recipe_id(recipe_id)` 为假时，`edit` 在读任何文件之前抛出 `UsageError(NOT_A_RECIPE_ID, None, id=recipe_id)`，`cli` 以 2 退出（选择 2）。
2. `list_recipe_ids(context.folder)` 给出 `ids` 和它们的问题（F04 设计 2.5）。问题里有错误时，`edit` 对第一个错误给出 `stop_at_error(context, error)`。
3. `ids` 里没有 `recipe_id` 时，`edit` 往错误流写 `UNKNOWN_ID`，并给出 1。
4. `shutil.which(program)` 给出 `found`。它给出 `None` 时，`edit` 往错误流写 `EDITOR_NOT_FOUND`，并给出 1（选择 4）。
5. `read_file_text(context.folder, path)` 给出 `before`，也就是文件的文字或一个 `Problem`（F14 设计 3.5）。
6. `subprocess.Popen([found, *context.settings.editor[1:], str(path)])` 启动编辑器。它抛出 `OSError` 时，`edit` 往错误流写 `EDITOR_NOT_STARTED`，并给出 1（选择 4）。
7. `edit` 写出第一行 `OPENED_IN_NOTEPAD` 或 `OPENED_IN_EDITOR`，并刷新 `context.out`（选择 4）。
8. `edit` 每次等半秒，一直等到编辑器结束（选择 5）。
9. 编辑器的退出码不是 0 时，`edit` 往错误流写 `EDITOR_FAILED`，并给出 1（选择 5）。
10. 编辑器在第 6 步之后不到 2 秒就结束，而且 `read_file_text(context.folder, path)` 等于 `before` 时，`edit` 写出 `QUICK_EXIT`，刷新 `context.out`，并从 `context.input` 读一行（选择 6）。
11. `list_recipe_ids(context.folder)` 再给出一次 ID 和问题。问题里有错误时，`edit` 对第一个错误给出 `stop_at_error(context, error)`。ID 里没有 `recipe_id` 时，`edit` 往错误流写 `GONE`，并给出 1（选择 7）。
12. `check_recipe(context.folder, recipe_id)` 给出问题（F15 设计 3.4）。`edit` 把报告写到输出流；有问题是错误时给出 1，否则给出 0（选择 7）。

在第 8 步和第 10 步按 Ctrl+C 会抛出 `KeyboardInterrupt`，`edit` 让它继续传给 `cli`。列表里的警告不改变任何东西。

- 返回值：退出码，以及写在相应流上的输出：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | 检查没有发现错误。它可能发现了警告。 | 输出流：第一行、`edit` 写出过的选择 6 的提示，以及报告。 |
| 1 | 某次列表有错误，`recipes/` 里没有这个 ID 的文件，找不到编辑器、无法启动编辑器或编辑器的退出码不是 0，编辑器之后菜谱不见了，或者检查发现了错误。 | 错误流上是 `stop_at_error` 的三行，或者 `UNKNOWN_ID`、`EDITOR_NOT_FOUND`、`EDITOR_NOT_STARTED`、`EDITOR_FAILED` 和 `GONE` 中的一条。编辑器启动过时，输出流上有第一行。检查发现错误之后，报告写到输出流，错误流上什么也没有。 |
| 2 | `cli` 的 `UsageError`，或者第 1 步的 `NOT_A_RECIPE_ID`。 | 错误流：提示，有提示行时再加上提示行。 |
| 130 | Ctrl+C。 | 不再写出任何东西，这是 `cli` 的规定（F05 设计 2.10）。 |

输出是下面这些行，每行以换行结束，只是选择 6 的提示本身不带换行：

| 情况 | `edit` 写到输出流的内容 |
| --- | --- |
| 编辑器启动了 | `context.settings.editor` 是 `("notepad",)` 时是 `OPENED_IN_NOTEPAD`，否则是 `OPENED_IN_EDITOR`。 |
| 编辑器马上就结束，文件也没有变（选择 6） | `QUICK_EXIT`。然后，输入不是终端时，是 `edit` 读到的那一行（去掉末尾的 LF）和一个换行；输入结束时只有一个换行。 |
| 检查没有发现问题 | 一个空行和 `CHECKED_CLEAN`。 |
| 检查发现了警告，没有错误 | 一个空行、`CHECKED_WARNINGS`，以及警告的 `problem_block`。 |
| 检查发现了错误 | 一个空行、`CHECKED_PROBLEMS`、错误的 `problem_block`、警告的 `problem_block`，以及结尾一行：每个错误都在这个菜谱的文件里时是 `EDIT_AGAIN`，否则是 `FIX_AND_CHECK`。 |

`edit` 的提示如下。`ERROR_COUNT` 和 `WARNING_COUNT` 是 `Plural` 值（F02 设计 2.4），各自按它的 `count` 选择写法。它们“多个”的写法用于 1 以外的每个数，两种写法的中文相同。`QUICK_EXIT` 的英文以一个空格结束，中文以 `：` 结束，后面没有空格。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `EDIT_HELP` | `Edit a recipe in your editor, then check it.` | `在编辑器里修改一个菜谱，然后检查它。` |
| `ID_ARGUMENT` | `ID` | `ID` |
| `NOT_A_RECIPE_ID` | `"{id}" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `“{id}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。` |
| `UNKNOWN_ID` | `No recipe has the ID "{id}". Run "recipe-menu search {id}" to find it.` | `没有 ID 为“{id}”的菜谱。运行“recipe-menu search {id}”查找它。` |
| `OPENED_IN_NOTEPAD` | `Opened {file} in Notepad. Close Notepad when you are done.` | `已用记事本打开 {file}。改完后关闭记事本。` |
| `OPENED_IN_EDITOR` | `Opened {file} in "{editor}". Close the editor when you are done.` | `已用“{editor}”打开 {file}。改完后关闭编辑器。` |
| `EDITOR_NOT_FOUND` | `Cannot start the editor "{editor}": no program of that name was found. Name your editor in settings.toml, such as editor = "code --wait".` | `无法启动编辑器“{editor}”：找不到这个名称的程序。请在 settings.toml 里写上你的编辑器，比如 editor = "code --wait"。` |
| `EDITOR_NOT_STARTED` | `Cannot start the editor "{editor}". The system says: {reason}` | `无法启动编辑器“{editor}”。系统提示：{reason}` |
| `EDITOR_FAILED` | `The editor "{editor}" ended with exit code {code}, so the recipe was not checked. Run "recipe-menu check" to check it.` | `编辑器“{editor}”以退出码 {code} 结束，所以没有检查这个菜谱。运行“recipe-menu check”检查它。` |
| `QUICK_EXIT` | `The editor closed at once, maybe because it opened the recipe in a window that was already open. When you have saved the recipe there, press Enter: ` | `编辑器马上就关闭了，可能是因为它在已经打开的窗口里打开了这个菜谱。在那里改完并保存后，按 Enter：` |
| `GONE` | `The recipe {id} is gone: its file was deleted or renamed while the editor was open.` | `菜谱 {id} 不见了：编辑器打开期间，它的文件被删除或改了名。` |
| `CHECKED_CLEAN` | `Checked {id}: no errors.` | `已检查 {id}：没有错误。` |
| `CHECKED_WARNINGS` | `Checked {id}: no errors, {warnings}.` | `已检查 {id}：没有错误，有 {warnings}。` |
| `CHECKED_PROBLEMS` | `Checked {id}: {problems}.` | `已检查 {id}：有 {problems}。` |
| `ERROR_COUNT`，一个时 | `{count} error` | `{count} 个错误` |
| `ERROR_COUNT`，多个时 | `{count} errors` | `{count} 个错误` |
| `WARNING_COUNT`，一个时 | `{count} warning` | `{count} 个警告` |
| `WARNING_COUNT`，多个时 | `{count} warnings` | `{count} 个警告` |
| `EDIT_AGAIN` | `Run "recipe-menu edit {id}" to fix it.` | `运行“recipe-menu edit {id}”改正它。` |
| `FIX_AND_CHECK` | `Fix the errors, then run "recipe-menu check".` | `改正错误后，运行“recipe-menu check”。` |

`ID_ARGUMENT`、`NOT_A_RECIPE_ID` 和 `UNKNOWN_ID` 的文字和 `show` 的相同（F09 设计 2.4）。`ERROR_COUNT`、`WARNING_COUNT` 和 `FIX_AND_CHECK` 的文字和 `add` 的相同（F15 设计 2.2）。`OPENED_IN_NOTEPAD` 的两种文字、一个错误时英文的 `CHECKED_PROBLEMS`、英文的 `EDIT_AGAIN` 和中文的 `CHECKED_CLEAN`，都是原型里的行。

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `id` | 你输入的 `ID` 的值。除了在 `NOT_A_RECIPE_ID` 里，它都符合 `is_recipe_id` 的规则，所以 `UNKNOWN_ID` 和 `EDIT_AGAIN` 里的命令行都是有效的。 |
| `file` | `str(context.folder.relative(path))`，比如 Windows 上的 `recipes\mapo-tofu.toml`（选择 8）。 |
| `editor` | `context.settings.editor[0]`，即设置里写的程序，不带包住它的引号，比如 `code` 或 `C:\Program Files\Notepad++\notepad++.exe`。 |
| `reason` | `OSError` 的 `error.strerror`，没有时是它的类型名称，和 `datafile` 给出系统原因的方式一样。 |
| `code` | 编辑器的退出码，一个 `int`，就是 `Popen` 给出的那个。 |
| `warnings` | 带警告个数的 `WARNING_COUNT`，作为 `BiText`：`1 warning` 和 `1 个警告`。 |
| `problems` | 带错误个数的 `ERROR_COUNT` 和带警告个数的 `WARNING_COUNT`（各自作为 `BiText`，个数为 0 的不写）的 `and_list`：`1 error and 2 warnings` 和 `1 个错误和 2 个警告`。 |
| `count` | 在 `ERROR_COUNT` 里是错误的个数，在 `WARNING_COUNT` 里是警告的个数。 |

错误：

`cli` 在运行 `edit` 之前报告命令行的错误、不存在的数据文件夹和设置里的错误（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 1，错误流上是 `NO_DATA_FOLDER` 和 `RUN_INIT` | 数据文件夹不是文件夹。因为 `edit` 有 `FolderUse.READ`，`cli` 在 F05 设计 2.10 的第 9 步检查它。 |
| 退出码 1，错误流上是设置的第一个错误和 `RUN_CHECK` | 设置有错误，包括错误的 `editor`（选择 3）。 |
| 退出码 2，带 `TOO_FEW_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`：`An argument is missing. Write "recipe-menu edit ID".` | `edit` 后面没有 ID。 |
| 退出码 2，带 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "rice". Write "recipe-menu edit ID".` | `edit` 后面有两个或更多 ID。 |
| 退出码 2，带没有选项时那种写法的 `UNKNOWN_OPTION`，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"edit" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，带 F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 某个全局选项违反了它的规则。 |
| 退出码 2，带 `NOT_A_RECIPE_ID`，没有提示行，比如 `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `ID` 的值违反 `is_recipe_id` 的规则（第 1 步）。 |
| 退出码 1，错误流上是 `stop_at_error` 的三行，比如 `recipes\Rice Bowl.toml`、它的提示和 `RUN_CHECK` | 编辑器之前或之后，`recipes/` 的某次列表有错误（第 2 和 11 步）。 |
| 退出码 1，错误流上是 `UNKNOWN_ID`，比如 `No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.` | `recipes/` 里没有这个 ID 的文件（第 3 步）。 |
| 退出码 1，错误流上是 `EDITOR_NOT_FOUND` | `shutil.which` 没有找到程序（第 4 步）。什么也不启动。 |
| 退出码 1，错误流上是 `EDITOR_NOT_STARTED` | `Popen` 抛出 `OSError`（第 6 步）。 |
| 退出码 1，输出流上是第一行，错误流上是 `EDITOR_FAILED` | 编辑器的退出码不是 0（第 9 步）。不做检查。 |
| 退出码 1，输出流上是第一行，错误流上是 `GONE` | 编辑器之后，`recipes/` 里不再有这个 ID 的文件（第 11 步）。 |
| 退出码 1，输出流上是报告 | 检查发现了错误（第 12 步）。 |
| 退出码 130 | `edit` 等编辑器时或在选择 6 的提示处按了 Ctrl+C。编辑器一直开着，不做检查（选择 5）。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `edit` 列出 `recipes/`，通过 `read_file_text` 读一次这个菜谱的文件，把编辑器作为一个新进程启动，并等它结束。编辑器马上就结束时，它再读一次这个菜谱的文件，并可能读标准输入的一行。然后它再列一次 `recipes/`，并通过 `check_recipe` 把 `catalog.toml` 和这个菜谱的文件各读一次。它写入输出流和错误流。它不写任何文件。编辑器改了什么，是编辑器做的事。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`，`home` 是它外面的一个空的临时文件夹，`stand_in` 是另一个临时文件夹里一个新文件的路径（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。这些路径里没有 `'`。替身是一个 Python 脚本，设置里用测试自己的 Python 写出它，所以它不需要 `PATH`，也不需要控制台。它在最后拿到的那个文件里把第一个 `old` 换成 `new`，两者相同时什么也不改。前两次运行就是原型的两段“An edit that leaves a mistake”和“A clean edit, in Chinese”，只是用替身代替了记事本。第三次运行让 `red-braised-pork` 保持原样，所以替身没改文件就马上结束，`edit` 写出选择 6 的提示。其余几次运行分别给出未知的 ID、违反规则的 ID、没有 ID、不存在的程序、以退出码 3 结束的编辑器，以及删除了文件的编辑器。

```python
import io
import sys
from datetime import date
from pathlib import Path

from recipe_menu.cli import main

stand_in.write_text(
    "import sys\n"
    "from pathlib import Path\n"
    "old, new, file = sys.argv[1], sys.argv[2], Path(sys.argv[3])\n"
    "if old != new:\n"
    "    data = file.read_bytes()\n"
    "    file.write_bytes(data.replace(old.encode(), new.encode(), 1))\n",
    encoding="utf-8",
)
settings_text = folder.settings.read_text(encoding="utf-8")


def use_editor(*words: str) -> None:
    editor = " ".join(f'"{word}"' for word in words)
    folder.settings.write_text(settings_text + f"editor = '{editor}'\n", encoding="utf-8")


def edit(*argv: str, stdin: str = "") -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["edit", "--data", str(folder.root), *argv],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        stdin=io.StringIO(stdin),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


python = sys.executable
mapo = Path("recipes", "mapo-tofu.toml")
use_editor(python, str(stand_in), "郫县豆瓣酱", "豆瓣酱")
assert edit("mapo-tofu") == (
    1,
    [
        f'Opened {mapo} in "{python}". Close the editor when you are done.',
        "",
        "Checked mapo-tofu: 1 error.",
        f"  {mapo}, ingredient 3",
        '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
        'Run "recipe-menu edit mapo-tofu" to fix it.',
    ],
    [],
)
use_editor(python, str(stand_in), "豆瓣酱", "郫县豆瓣酱")
assert edit("mapo-tofu", "--lang", "zh") == (
    0,
    [f"已用“{python}”打开 {mapo}。改完后关闭编辑器。", "", "已检查 mapo-tofu：没有错误。"],
    [],
)

pork = Path("recipes", "red-braised-pork.toml")
quick = (
    "The editor closed at once, maybe because it opened the recipe in a window that "
    "was already open. When you have saved the recipe there, press Enter: "
)
use_editor(python, str(stand_in), "x", "x")
assert edit("red-braised-pork") == (
    0,
    [
        f'Opened {pork} in "{python}". Close the editor when you are done.',
        quick,
        "",
        "Checked red-braised-pork: no errors, 1 warning.",
        f"  {pork}, steps",
        "    No English steps. Commands show the Chinese steps instead.",
    ],
    [],
)

unknown = 'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.'
assert edit("mapo") == (1, [], [unknown])
not_an_id = '"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.'
assert edit("Mapo") == (2, [], [not_an_id])
assert edit() == (
    2,
    [],
    [
        'An argument is missing. Write "recipe-menu edit ID".',
        'Run "recipe-menu --help" to see the commands.',
    ],
)

use_editor("no-such-editor-f16")
not_found = (
    'Cannot start the editor "no-such-editor-f16": no program of that name was found. '
    'Name your editor in settings.toml, such as editor = "code --wait".'
)
assert edit("tomato-egg") == (1, [], [not_found])

rice = Path("recipes", "rice.toml")
opened_rice = f'Opened {rice} in "{python}". Close the editor when you are done.'
use_editor(python, "-c", "raise SystemExit(3)")
failed = (
    f'The editor "{python}" ended with exit code 3, so the recipe was not checked. '
    'Run "recipe-menu check" to check it.'
)
assert edit("rice") == (1, [opened_rice], [failed])
use_editor(python, "-c", "import os, sys; os.remove(sys.argv[1])")
gone = "The recipe rice is gone: its file was deleted or renamed while the editor was open."
assert edit("rice") == (1, [opened_rice], [gone])
```

## 3. 对已有接口的修改

F16 给一个已实现的模块加上架构 5.1 为它计划的东西：给 `settings.toml`“F16 加上编辑器”，F05 设计第 2 节和 F14 设计第 2 节把它计划为 `Settings` 和 `read_settings` 的一个键。F01 到 F15 导出的名称，没有哪个调用会失效。新字段放在最后，带默认值，所以 F15-T02 的 `Settings(Lang.EN, (Meal.DINNER,), 5)`，以及每个按位置给出三个或四个值的调用，意思都不变。`read_settings` 的签名不变。需求已经写到这个设置（需求 4，F16），所以不需要 `[docs]` PR 来批准这些添加。架构师在这份设计里审查它们，就像审查 F14 的 `dishes` 一样。B 点和 C 点修改架构 4、6 和 8，Troy 决定之后，架构师在 F16 的 mock PR 之前用一个 `[docs]` PR 把它们连同一份 ADR 写下来。

1. `settings`：`Settings` 多了字段 `editor`（3.1），`read_settings` 读取键 `editor`（3.2）。现在两个设置的五个字段都相等时才相等。键 `editor` 以前给出 `UNKNOWN_KEY`，现在设置的 `UNKNOWN_KEY` 文字列出五个键。
2. `cli`：`COMMANDS` 在 `ADD_COMMAND` 之后多了 `EDIT_COMMAND`（选择 1）。

F16 验收时，设计之外还有这些修改：

- 产品经理在 F05 原型的两段帮助“Help in English”和“Help in Chinese”里，按 2.1 的样子在 `add` 那一行后面加上 `edit ID` 那一行。那个原型开头的说明随后写明帮助也列出 `edit`，不再说 F16 加上它。测试经理在 F14 验收时裁定，这两段显示已验收功能的帮助。
- 测试经理按 v0.2 测试计划第 2 节的规定更新它：v0.2-S14 带 `edit` 那一行的帮助、v0.2-S12 的第一行、v0.2-S13 的第 1 到 3 步、v0.2-S15 和 v0.2-S16 的第 3 步（选择 6）、v0.2-S19 的第 3 步，以及“Where the plan waits for the designs”里 F16 的那一点。
- 架构师可以在架构 5.2 的 `Settings` 那一行写上编辑器，就像 4.1 版写上菜数一样。

已验收功能的测试都不用改。这些测试仍然成立：

- F07-T17 和 F13-T01 按开头找到它们的那一行，把它的文字所在的列和 `--lang en|zh` 的比较。`edit ID` 占 7 列，所以第二列仍在第 24 列之后。
- F08-T14 检查 `check` 跟在 `init` 后面，F09-T01 检查 `list` 和 `show` 跟在 `check` 后面，F10-T01 检查 `search` 跟在 `show ID` 后面，F11-T01 检查 `menu new` 在 `search` 之后、`menu show` 跟在它后面，F14-T01 检查 `menu suggest` 跟在 `menu show` 后面，F15-T01 检查 `add` 在 `search` 之后、文字在 `--lang en|zh` 的那一列。`edit` 那一行都不在这些成对的行之间。F15 的修测试之后，F11-T01 按开头找到 `menu new` 那一行，所以 `add` 和 `menu new` 之间多一行没有关系。F15-T01 只对它自己的十个命令比较整份帮助，F14-T01 只对它自己的九个命令比较。
- F09-T19、F11-T27、F11-T32、F11-T35、F13-T22、F13-T27、F14-T21、F14-T31 和 F15-T24 拿真实 `COMMANDS` 的一份帮助和另一份比较。`edit` 是一个词，所以 `recipe-menu menu` 仍然只列出三个 `menu` 命令，这是 F11-T32 和 F14-T21 的要求。
- F15-T03 比较 `Context` 各字段的名称，F16 不加字段。它的第 5 项在被监视的标准输入下运行 `list`、`check`、`show tomato-egg`、`menu show 2026-W47` 和 `--help`。它们都不运行 `edit`，帮助也和它自己相等。
- F05-T10 和 F05-T11 通过 `tests/f05_texts.py` 的 `KEYS_START`，检查设置的 `UNKNOWN_KEY` 的键列表以 `language`、`meals` 和 `servings` 开头。F14-T23 还通过 `tests/f14_support.py` 的 `assert_settings_problems` 检查它的第四个键是 `dishes`。`editor` 是第五个，所以这三个测试都成立。
- F05-T02、F05-T03、F14-T22、F15-T02 和其他创建设置的测试最多给出四个值，所以每次比较的两边 `editor` 都得到它的默认值。
- F03-T30 写的 `editor = "C:\Program Files\notepad.exe"` 是语法错误，`read_toml` 在读任何键之前就报告它。
- 没有测试运行 `edit`，在 mock 之前它给出 `Unknown command "edit".`，也没有测试要求这一行。F15 的 `ID_EXISTS` 只是在文字里写到 `recipe-menu edit`。
- F05 设计 2.3 的示例写了 `editor = 1`，要求得到 `UNKNOWN_KEY`。F16 之后，这一行在位置 `editor` 上给出 `NOT_A_TEXT`。没有测试运行这一行，因为 F05-T11 用的是 `colour = 1`。已批准的 F05 设计保持原文，3.2 给出 F16 之后的规则。

F16 按各自设计的规定使用这些接口，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural` 和 `and_list`。
- F03 的 `DataFolder`（以及 `recipe_file` 和 `relative`）、`Problem`、`Severity` 和 `read_toml`，以及 `datafile` 的提示 `NOT_A_TEXT`、`EMPTY_TEXT` 和 `UNKNOWN_KEY`（F03 设计 2.10）。
- F04 在 `datafile` 里的 `read_text` 和 `report_unknown_keys`（F04 设计 3.2）、`is_recipe_id` 和 `list_recipe_ids`，以及通过 `check_recipe` 使用的 `read_recipe`。
- F05 在 `app` 里的 `Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error` 和 `stop_at_error`，在 `settings` 里的 `Settings` 和 `read_settings`（加上 3.1 和 3.2 的添加），以及在 `cli` 里的 `COMMANDS` 和 `main`。
- F14 在 `datafile` 里的 `read_file_text`。
- F15 的 `Context.input`，以及 `check` 里的 `check_recipe` 和 `problem_block`。

### 3.1 `Settings.editor`

- 模块：settings
- 功能：`edit` 用来打开菜谱的程序，以及它的选项（[需求 4](../../requirements.zh-CN.md#4-功能点)，架构 5.1）。`read_settings` 从键 `editor` 填入它（3.2），`edit` 启动它（选择 4）。

签名：

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
    dishes: tuple[int, int, int] = (1, 1, 1)
    editor: tuple[str, ...] = ("notepad",)

    def dishes_for(self, meal: Meal) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `editor` | `str` 组成的元组 | 程序，然后是它的选项，也就是选择 3 拆出的词。`edit` 在它们后面加上菜谱的文件。 | 至少一项。第一项不为空。每一项都没有 U+0000。其他项可以为空。 |

其他字段保持它们的含义和约束（F05 设计 2.2，F14 设计 3.1）。

- 返回值：一个 `Settings`。两个设置的五个字段都相等时才相等，`Settings` 可以求哈希。`Settings()` 以及 F01 到 F15 的每个调用，`editor` 都保持 `("notepad",)`。

错误：

F05 设计 2.2 和 F14 设计 3.1 的错误仍然有效，`editor` 带来这些错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `editor` 不是元组，或者里面有一项不是 `str`。 |
| `ValueError` | `editor` 是空的，它的第一项是空的，或者某一项里有 U+0000。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.editor == ("notepad",)
code = Settings(editor=("code", "--wait"))
assert code.editor == ("code", "--wait")
assert code != defaults
whole = Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2, (1, 1, 1), ("notepad",))
assert whole == Settings(Lang.EN)
assert hash(whole) == hash(Settings(Lang.EN))
assert Settings(editor=("code", "")).editor == ("code", "")

Settings(editor=())  # raises ValueError
Settings(editor=("", "--wait"))  # raises ValueError
Settings(editor=("vi", "a\x00b"))  # raises ValueError
Settings(editor="notepad")  # raises TypeError
Settings(editor=["notepad"])  # raises TypeError
Settings(editor=("code", 1))  # raises TypeError
```

### 3.2 `read_settings`：键 `editor`

- 模块：settings
- 功能：把 `settings.toml` 里可选的键 `editor` 读进 `Settings.editor`，并和其他键一样报告它的问题和位置（F05 设计 2.3，选择 3）。`cli` 和 `check` 和以前一样调用 `read_settings`。

签名：

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：F05 设计 2.3 和 F14 设计 3.2 的 `(settings, problems)` 这一对，加上下面这些内容。
  - 文件可以有键 `editor`，它的文字按选择 3 拆成词，比如 `editor = "code --wait"`。没有这个键时，`settings.editor` 是 `("notepad",)`。
  - `settings.editor` 按顺序放着这段文字拆出的词，不带把它们括在一起的引号。
  - 文件顶层的键是 `language`、`meals`、`servings`、`dishes` 和 `editor`，按这个顺序。所以 `UNKNOWN_KEY` 用“多个键”的写法列出“language, meals, servings, dishes, and editor”和“language、meals、servings、dishes 和 editor”。

新问题的位置如下：

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| `editor` | `editor` | `编辑器` |

`read_settings` 对 `editor` 做这些检查。没有这个键不产生问题。

| 部分 | 检查 | 问题 | 位置 | 类型 |
| --- | --- | --- | --- | --- |
| `editor` | 值不是文字，比如 `editor = 1` 或 `editor = ["code"]`。 | `datafile` 的 `NOT_A_TEXT`，`key` 设为 `editor` | `editor` | 错误 |
| `editor` | 文字是空的，或者只有空白。 | `datafile` 的 `EMPTY_TEXT`，`key` 设为 `editor` | `editor` | 错误 |
| `editor` | 文字在带引号的部分里结束，第一个词是空的，或者某个词里有 U+0000。 | `EDITOR_NOT_A_COMMAND` | `editor` | 错误 |

每个值最多产生一个问题，就是表中第一个适用的那个。`editor` 的问题排在 `dishes` 的问题之后、文件顶层的未知键之前。

这些是 `settings` 的新提示：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `EDITOR` | `editor` | `编辑器` |
| `EDITOR_NOT_A_COMMAND` | `"editor" must name a program and then its options, such as editor = "code --wait". Put a path with spaces in double quotation marks, and close each one.` | `“editor”必须先写程序，再写它的选项，比如 editor = "code --wait"。带空格的路径要放在英文双引号里，每个引号都要配对。` |

错误：无。`read_settings` 遇到坏数据从不抛异常。

- 副作用：和以前一样，通过 `read_toml` 读取 `settings.toml`。它不写任何东西。
- 性能指标：无

示例：

这个示例里，`folder` 是示例数据文件夹 `tests/data/example/` 的一份新副本上的 `DataFolder`。

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings


def settings_of(*lines: str) -> tuple[Settings | None, list[str]]:
    folder.settings.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    settings, problems = read_settings(folder)
    return settings, [problem.text(Lang.EN) for problem in problems]


assert settings_of('editor = "code --wait"') == (Settings(editor=("code", "--wait")), [])
assert settings_of('editor = "  notepad  "') == (Settings(), [])
notepad_pp = r"""editor = '"C:\Program Files\Notepad++\notepad++.exe" -multiInst -nosession'"""
program = r"C:\Program Files\Notepad++\notepad++.exe"
assert settings_of(notepad_pp)[0] == Settings(editor=(program, "-multiInst", "-nosession"))
assert settings_of("editor = 'code --file=\"a b\"'")[0] == Settings(editor=("code", "--file=a b"))

not_a_command = (
    '"editor" must name a program and then its options, such as editor = "code --wait". '
    "Put a path with spaces in double quotation marks, and close each one."
)
assert settings_of(r"""editor = '"C:\Program Files\x.exe --wait'""") == (None, [not_a_command])
assert settings_of("""editor = '"" --wait'""") == (None, [not_a_command])
assert settings_of('editor = "vi \\u0000"') == (None, [not_a_command])
assert settings_of("editor = 1") == (None, ['"editor" must be a text in quotation marks.'])
assert settings_of('editor = "   "') == (None, ['"editor" is empty.'])
settings, texts = settings_of("dishes = 2", "editor = []", "colour = 1")
assert settings is None
assert texts[1:] == [
    '"editor" must be a text in quotation marks.',
    'Unknown key "colour". The keys are language, meals, servings, dishes, and editor.',
]

folder.settings.write_text("editor = 1\ncolour = 1\n", encoding="utf-8")
_, problems = read_settings(folder)
assert [problem.place for problem in problems] == [BiText("editor", "编辑器"), None]
keys_zh = "未知键“colour”。可用的键：language、meals、servings、dishes 和 editor。"
assert problems[1].text(Lang.ZH) == keys_zh
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `edit` 是架构 3 交给 F16 的命令模块，位于 `src/recipe_menu/commands/edit/`，只导出 `EDIT_COMMAND`。它只引用 `app`、`lang`、`text`、`datafile`、`recipes` 和 `check`。这些都在它那一行里，`edit --> check` 也是架构 4 里的一个箭头。它从 `context.settings.editor` 读编辑器，所以既不需要 `settings`，也不需要 `units`、`catalog`、`menus` 或 `shopping`。第 3 节加上的正是架构 3 和 5.1 为 F16 计划的东西：`settings.toml` 的键 `editor`，以及 `Settings.editor`。它是一个 `str` 元组，在带 `slots=True` 的冻结数据类里有默认值，所以架构 8 的值规则成立。拆分这个键的代码放在读这个文件的 `settings` 里，每个新文件都只属于一个模块。`edit` 不写任何文件，所以架构 1 的“你的文件保持你写的样子”成立：只有编辑器修改菜谱。任务说明第 1 点，要点 C：在做法 1 下，`edit` 用三种方式接触外部世界，而架构 4 和 8 把这些留给 `cli`。`shutil.which` 从进程的环境里读 `PATH`、`PATHEXT` 和 `NoDefaultCurrentDirectoryInExePath`，编辑器得到这个环境、当前文件夹和控制台。所以 `main(environ={})` 不再能让 `edit` 不碰进程的 PATH，选择 9 也这样说。架构师在做法 1 下写的规则要写明这三点，而不只是启动一个程序。备注 1，不阻塞：要点 C 对做法 2 的描述是公正的，但漏了它的好处。在做法 2 下，架构 8 的规则保持完整：`main` 会在它的 `environ` 的 PATH 里查找，`edit` 的测试不启动任何进程，只有 `cli` 里启动函数的测试会启动。“它的测试仍然需要一个替身来真正启动”只对那一个测试成立。架构师仍然推荐做法 1：只有一个命令启动一个程序，而且需求点名了这个程序；做法 2 为此给 `app` 加一个启动并等待的接口，给每个上下文加一个字段。摘要说“对你来说一样”是对的，因为 Troy 看不出区别。要点 C 可以在修订时加上这个好处。第 3 节那句“要点 B 和 C 修改架构 4、6 和 8”只对各自的做法 1 成立。要点 B 的做法 2 修改原型，不改架构。要点 C 的做法 2 修改架构 5.2 的 `Context` 一行，架构 8 也要在 `cli` 做的事里写上启动编辑器。任务说明第 4 点，速度：在 main 未改动的副本和模型上，`import recipe_menu.cli` 都不加载 `subprocess`、`shutil` 或 `threading`，而 `time` 已经加载。模型的五个新文件，`edit` 的四个和 `settings` 的一个，在 9 次预热后的 `python -X importtime` 里自身耗时 3.2 到 3.3 毫秒。如果在顶部引用，`subprocess` 会增加 5.0 到 8.7 毫秒，`shutil` 会增加 6.3 到 6.9 毫秒，所以在函数里引用让每个命令启动时少花大约 11 到 15 毫秒。选择 12 的“几毫秒”成立，`check` 在 PT01 下的 0.858 秒会变成大约 0.861 秒。这些时间来自审查在 Troy 电脑上的沙箱，不是 v0.2 的发布测试。 |
| 遵守错误处理和命名约定 | 通过 | `run` 只在 ID 不符合 `is_recipe_id` 时抛出 `UsageError`，不带提示，和 `show` 一样（ADR-0008）。列目录的第一个错误通过 `first_error` 和 `stop_at_error` 让 `edit` 停下，编辑器之前和之后都是这样。`UNKNOWN_ID`、`EDITOR_NOT_FOUND`、`EDITOR_NOT_STARTED`、`EDITOR_FAILED` 和 `GONE` 在错误流上结束 `edit`，退出码 1。报告不论退出码都写到输出流，正如架构 6 对 `check` 的规定，以及 v0.2 测试计划对 `add` 和 `edit` 的规定。编辑器无法启动或出错时退出码为 1，符合架构 1，因为命令没有成功，和 F15 输入提前结束一样。`edit` 只捕获 `Popen` 的 `OSError` 和分步等待的 `subprocess.TimeoutExpired`，都写明了名字，并让 `KeyboardInterrupt` 传给 `cli`。名称遵守架构 8。模块和它的命令同名。`edit` 的 18 条消息和 `settings` 的 2 条消息是各自模块 `messages.py` 里的 UPPER_SNAKE 常量。计数是 `Plural` 值，计数的列表来自 `and_list`，键 `editor` 是一个小写英文单词。任务说明第 1 点，要点 B：做法 1 修改架构 6，选择 8 也这样说。架构 6 规定，不是问题的消息用完整路径写文件，而 ADR-0009 和 ADR-0011 要求其他每种情况各自修改架构。`edit` 的第一行不是问题，所以做法 1 需要加一种情况，就像 `menu suggest` 的换菜行那样（ADR-0011）。做法 2 不需要修改架构，但要通过需求变更流程修改原型，要点 B 也这样说。架构 6 还没有一行讲命令启动的程序。不论要点 C 选哪种做法，架构师的 `[docs]` PR 都会加上这一行：找不到编辑器、无法启动它，或者它以非 0 的退出码结束时，由 `edit` 捕获，退出码为 1，错误流上写一行。在模型上用 ruff 0.17.4 和项目的 `pyproject.toml` 检查，它只对函数里的每个 import 报 `PLC0415`，对 `Popen` 的调用报 `S603`。加上选择 4 的 `noqa` 注释后，这段代码里它不再报别的。备注 2，不阻塞：`EDITOR_NOT_STARTED` 的原因是 Windows 的文字，用 Windows 的语言，而且可能带一个原样的 `%1`。在模型上，`PATHEXT` 找到的一个 `.py` 文件给出 `The system says: %1 is not a valid Win32 application`，中文时也一样。一个名叫 `bogus.exe` 的文本文件给出 `This version of %1 is not compatible with …`。`datafile` 也这样转述 Windows 的原因，所以选择 4 可以写明这种情况，保持不变。备注 3，不阻塞：选择 5 说按 Ctrl+C 后 `Popen.wait` 给编辑器四分之一秒。CPython 3.13 等待的是 `min(0.25, remaining)` 秒，`remaining` 是超时剩下的时间。在 Windows 上，中断要到半秒的一步结束时才到，所以常常一点也不等。不论哪种情况，编辑器都不会被停止，所以只需要改措辞：“最多四分之一秒”。 |
| 不和已有接口重复 | 通过 | `edit` 用 `is_recipe_id` 和 `list_recipe_ids` 的列表检查 ID，用 `read_file_text` 读文件。它用 `check_recipe` 检查菜谱，用 `problem_block` 写问题，用 `stop_at_error` 停下。`settings` 用 `read_text` 以及 `datafile` 的消息 `NOT_A_TEXT` 和 `EMPTY_TEXT` 读这个键。两者都没有重新造这些东西。选择 3 的拆分规则是新的，标准库里没有合适的。在 POSIX 模式下，`shlex.split` 把引号外的 `\` 当作转义，所以 `C:\Tools\ed.exe` 会丢掉分隔符。在另一种模式下，它把引号留在词里。`ID_ARGUMENT`、`NOT_A_RECIPE_ID`、`UNKNOWN_ID`、`ERROR_COUNT`、`WARNING_COUNT` 和 `FIX_AND_CHECK` 的副本是内部消息，架构 8 把它们留在各自模块里，F13 到 F15 的审查也接受了这种做法。备注 4，不阻塞：`edit` 还重复了 `add` 的内部代码，即问题的计数，以及读列表并在第一个错误处停下。前几次审查提到的后续 `[refactor]` PR 可以让两者共用，比如通过两个命令都引用的 `check`。 |
| 只依赖排序在前面的功能 | 通过 | F16 用到 F02 的 `text`、F03 和 F14 的 `datafile`、F04 的 `recipes`、F05 的 `app`、`settings` 和 `cli`、F07 和 F15 的 `check`，以及 F15 的 `Context.input`。它复制了 F09 和 F15 的文字。这些功能都排在 F16 前面，并已在 main 上验收，F15 在提交 902ed65 中验收。F05 是 F16 那一行的硬依赖，F07 是软依赖。F14 和 F15 通过共享模块 `datafile`、`app` 和 `check` 进入 F16，这些模块指向更早的功能，正如架构 4 所允许的。没有后续功能建立在 F16 之上。`subprocess`、`shutil` 和 `time` 是标准模块（ADR-0001），所以 R16 没有要审查的。`docs/rules.md` 里没有类型为 Review、由架构师执行的 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写下了每个假设。`check_recipe` 得到的是编辑器结束后列出的 ID，正如 F15 设计 3.4 的要求。`edit` 精确比较 ID，所以在 Windows 上它不会为 `tomato-egg` 打开 `Tomato-Egg.toml`。第一行取决于 `context.settings.editor == ("notepad",)`，要点 D 的提示只取决于退出码、`time.monotonic()` 量出的时长，以及 `read_file_text` 的两次结果。编辑器得到的是控制台，而不是 `context.out`。选择 4 和 6 写明了这些。任务说明第 2 点，在 Windows 11 上用 Python 3.13.18 在第 2、3 节的模型上运行，替身编辑器都不打开窗口：(a) `shutil.which` 借助 `PATHEXT` 在名为 `Microsoft VS Code\bin` 的文件夹里找到了 `code.CMD` 和 `stand-in-editor.CMD`。`Popen` 不经过 shell 运行了这个 `.cmd`，参数是 `--wait` 和数据文件夹 `数据 文件夹` 的完整路径，路径是一个参数。v0.2-S12 第 1 到 3 步和 v0.2-S13 第 1 到 3 步的输出与设计给出的各行一致。替身在 S12 的每一步各运行一次，在 S13 第 1、2 步里没有运行。(b) 在一个没有窗口的控制台里，`edit` 等待一个运行 6 秒、没有控制台的替身时发出 Ctrl+C，0.24 秒后得到 130，只写出了第一行。替身继续运行并结束。不带超时的普通 `Popen.wait()` 直到替身结束才醒来，即 Ctrl+C 后 4.1 秒，所以选择 5 的半秒分步是必要的。(c) 等 1 秒、不做修改的替身得到了提示，然后在输入结束时进行检查。等 2.2 秒的替身走普通路径。(d) 选择 3 表里的 7 行都成立。`\` 保持原样，制表符和 U+3000 分隔词，`a"b c"d` 给出 `ab cd`，`'""'` 给出 `EDITOR_NOT_A_COMMAND`，放在双引号里的路径给出 TOML 的转义消息，它会指向单引号。4 个示例成立：40 个断言和 6 个 `# raises`。(e) 在不设 `NoDefaultCurrentDirectoryInExePath` 时，也就是 Troy 电脑上的情况，当前文件夹里的 `stand-in-editor.cmd` 比 PATH 上的那个先运行，这就是第四条风险。这个 Claude 会话设置了这个变量，所以在这里 `shutil.which` 跳过当前文件夹。没有运行的：记事本、VS Code，以及在真正的控制台里在提示处按 Ctrl+C，因为测试程序无法在控制台里按键。进程内的检查对提示处的 `KeyboardInterrupt` 给出 130，和 `add` 一样。Windows 11 记事本：在这台电脑上，`shutil.which("notepad")` 给出 `C:\WINDOWS\system32\notepad.EXE`，一个映像文件重定向会改为启动应用商店版记事本 11.2609。微软 2023-01-19 的 Windows Insider 博客只说有一个设置决定文件在新标签页还是新窗口里打开。它没有说被启动的进程交出文件后会做什么，也没有说在没有窗口打开时它是不是那个窗口。任务说明第 5 点：在 WSL Ubuntu 22.04 上用 Python 3.10.12，在 CI 运行器的 PATH 上 `shutil.which("notepad")` 给出 `None`，所以 `edit` 在那里给出 `EDITOR_NOT_FOUND`，什么都不启动。CI 上的测试不会启动默认编辑器。带 `#!` 和可执行位的替身能被找到，并把含空格和中文的路径作为一个参数收到；没有可执行位的文件找不到。Linux 上没有这个键的用户得到 `EDITOR_NOT_FOUND`，它的消息说明怎样写编辑器。备注 5，不阻塞：v0.2-S19 那一项把“第 1、2 步里被启动的 `notepad.exe` 就是那个窗口”当作事实。它可以说明这一点没有验证过。如果记事本在那里也马上结束，要点 D 的做法 1 仍然在你修改之后检查，只是多出提示这一行。备注 6，不阻塞：选择 4 只提到 `%NAME%`。在模型上，含 `&`、不含空格的数据文件夹路径让批处理编辑器收到的路径被截断，cmd.exe 把路径的其余部分当作命令运行。它还丢掉了 `^`。在含空格的路径里，`&` 和 `^` 保留，`%PATH%` 被展开。ID 里从不会有这些字符，数据文件夹是 Troy 自己选的，所以这不是安全漏洞。选择 4 可以写明不含空格的路径里的 `&`、`\|`、`<`、`>` 和 `^`，以及任何路径里的 `%`。备注 7，给测试经理：在 Troy 的电脑上，默认值会找到真正的记事本。一个运行 `edit` 的测试如果既没有这个键，也没有自己的 PATH，就会启动记事本并一直等到有人关闭它。选择 10 让每个测试默认值的测试设置 PATH。测试计划可以让每个运行 `edit` 的测试都这样做，比如用一个把 PATH 设为空文件夹的 fixture，这样忘了写键的测试在 Windows 上也会得到 `EDITOR_NOT_FOUND`。测试当前文件夹的测试要自己设置或删除 `NoDefaultCurrentDirectoryInExePath`，因为 Claude 的会话设置了它，而 Troy 的终端没有。 |
| 修改已实现的接口时走了变更流程 | 通过 | 这个 PR 只加了两个设计文件。第 3 节给 `settings` 加上的正是架构 5.1 以及 F05 和 F14 的设计所计划的：最后一个带默认值的第五个字段，再加一个键。`COMMANDS` 加上它的一项，这是架构 4 允许命令功能在 `cli` 里做的唯一修改。需求已经写了这个设置，所以需求不变，由架构师在这里审查这些新增内容，就像审查 F14 的 `dishes` 一样。任务说明第 3 点：在 Windows 上用 Python 3.13.18，在 `EDIT_COMMAND` 排在 `ADD_COMMAND` 后面的模型上单独运行整个测试集，结果是 646 个通过、4 个跳过。main 未改动的副本结果相同，4 个跳过是 main 里只在 Linux 上运行的用例。F05-T10、F05-T11、F14-T23、F15-T02、F15-T03、F05-T02、F05-T03、F14-T22、F03-T30，以及第 3 节点名的每个帮助测试都通过。`tests/` 里的 PT01 用例 F07-T25 和 F10-T21 在两个副本上也都通过。帮助在两种语言里都有 24 行，`edit ID` 在第 12 行，第二列从第 24 列之后开始。所以在模拟 PR 之前不需要修复测试的 PR。备注 8，不阻塞：F05 设计 2.3 的示例写了 `editor = 1` 并期望 `UNKNOWN_KEY`，第 3 节说 F16 之后它不再成立。接口设计师以后可以在一个 `[docs]` PR 里把那里改成 `colour = 1`，和 F05-T11 一样，让已批准设计的每个示例都保持正确。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | PR #123 在提交 a0c239c 时顶部的摘要就是任务说明里的那份，它和设计说的一致。“对你有什么变化”写了默认用记事本、键 `editor` 以及怎样给路径加引号、`init` 不写这个键、`edit` 从不写菜谱，以及帮助里的那一行。第 1 到 4 项是要点 A 到 D，每项都有做法和带理由的推荐。要点 A 的数目成立：2.2 和 3.2 共有 20 条消息，其中 6 条是副本，1 条整条来自原型，剩下 13 条。四条风险来自选择 3 到 6。第一条漏了 `init`，而数据文件夹存在时 `init` 只会拒绝，所以它说的就是 Troy 看到的。第四条在 Troy 的电脑上成立，因为那里没有设置 `NoDefaultCurrentDirectoryInExePath`。架构师没有找到需要 Troy 决定的其他事：备注 1 到 8 都不改变 Troy 看到或选择的东西。在描述上运行 troy-check 的 `summary.py` 检查，全部通过。中文部分 864 个字符，英文部分 1,836 个字符，都在 R22 的 2,000 以内。两部分都按顺序有三个小节，各自 4 项里每项都有推荐，都不含内部编号。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0001、ADR-0008、ADR-0009 和 ADR-0011、F05、F07、F14 和 F15 的设计、F16 原型、v0.2 测试计划，以及任务说明的六点，检查了 13 个选择、第 3 节和要点 A 到 D。两个文件有同样的 17 个标题和 124 行表格，单元格相同，还有 10 个代码块，每个都和镜像相同，没有控制字符或不可见字符。7 个 `python` 代码块都能解析。架构师在仓库之外 main 的 `src/` 副本上，用 Windows 上的 Python 3.13.18 搭了第 2、3 节的模型，在 `tests/data/example/` 的新副本上运行了 4 个示例：40 个断言和 6 个 `# raises` 全部成立。第 1、5、6 项给出了各次运行、启动时间和整个测试集。没有运行的：记事本、VS Code、按键的真实控制台、Linux 上的模型，以及 PT01 的版本测试。备注 1 到 8 都不阻塞。 | 批准。Troy 批准这份设计时，主会话把要点 A 到 D 交给 Troy（R18）。在要点 B 的做法 1 和要点 C 的做法 1 下，架构师的 `[docs]` PR 排在 F16 模拟 PR 之前。它用一个 ADR 把要点 B 记进架构 6。它用一个 ADR 把要点 C 记进架构 4 和 8，写明启动编辑器，以及 `shutil.which` 读取 `PATH`、`PATHEXT` 和 `NoDefaultCurrentDirectoryInExePath`。它还给架构 6 加上找不到、无法启动或出错的编辑器那一行（第 2 项），并在架构 5.2 的 `Settings` 一行加上编辑器。要点 B 的做法 2 通过需求变更流程修改原型，不需要 ADR。要点 C 的做法 2 仍然需要一个 ADR，用于架构 5.2 和 8。接口设计师可以在修订时采纳备注 1、2、3、5 和 6，也可以不采纳。备注 4 等后续的 `[refactor]` PR，备注 8 等以后的 `[docs]` PR。给测试经理的任务说明（任务说明第 6 点）：设计解决了“计划在哪里等设计”里 F16 的各点。模型给出了 v0.2-S12 的第一行、v0.2-S13 第 2 步的用法消息，以及设计给出的 `editor` 的拆分方式。第 3 节的列表是完整的：v0.2-S12 到 v0.2-S16、v0.2-S19 第 3 步，以及 F16 那一点。和 F14、F15 一样，更新可以随 F16 测试计划一起做，在版本测试 PR 之前。v0.2-S15 和 v0.2-S16 的第 3 步给一个空的标准输入，并期望出现提示，因为什么都不改的 1 秒替身会得到提示。备注 7 也交给同一份任务说明。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-21 | 初稿。 |
| 1.0 | 2026-11-21 | Troy 批准。 |
