---
troy-doc: "F11-test-plan"
lang: "zh-CN"
version: "1.1"
updated: "2026-11-17"
status: "Troy 已于 2026-11-15 批准"
mirror-of: "test-plan.md"
---

# F11 创建和查看周菜单：测试方案

## 1. 功能

- 编号和名称：F11 创建和查看周菜单
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.menu` 的 `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND`、`recipe_menu.menus` 的 `NO_MENU`、`recipe_menu.datafile` 的 `FileOutcome`、`FileCreation` 和 `create_file`、`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的值调用 `FileCreation`、`create_file` 或某个命令的 `run`。功能用例像你输入 `recipe-menu menu new` 或 `recipe-menu menu show` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 里是 `INIT_COMMAND`、`CHECK_COMMAND`、`LIST_COMMAND`、`SHOW_COMMAND`、`SEARCH_COMMAND`、`MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND`（设计选择 1）。集成用例在 `main` 上运行 v0.1 场景，启动 `python -m recipe_menu`，或者构造随机菜单。性能用例为 `python -m recipe_menu menu show` 计时（第 3 节）。每个用例在括号里注明它来自设计的哪一节，比如（2.2）。设计的七个示例和其中 11 行 `# raises` 分别在 F11-T01（2.1）、F11-T02（2.3）、F11-T04（3.1）、F11-T05（3.2）、F11-T07（3.3）、F11-T15（2.2）和 F11-T26（2.4）里。

**A 点到 C 点。** Troy 于 2026-11-14 批准了设计 1.0，每一点都按建议：按 2.2、2.4 和 3.1 的写法接受新的文字（A）；新菜单文件在两种语言里都用英文注释，所以 `--lang zh` 和 `language = "zh"` 只改变输出（B）；C 点用做法 1：`menu new` 每次失败的第一行都用完整路径写出它的文件或文件夹，包括它没能列出的文件夹 `menus\`。架构 4.0 和 ADR-0010 记录了 C 点。用例用两种语言检查 A 点的每一段新文字。英文的拒绝在 F11-T01、F11-T15、F11-T22 和 F11-T35 里。新菜单的中文各行在 F11-T01、F11-T17 和 F11-T18 里。中文的 `NO_MENU` 在 F11-T04 和 F11-T29 里。一餐一道菜的中文计数行在 F11-T34 里。两种语言的 `NO_DISHES` 在 F11-T19、F11-T20 和 F11-T31 里。两种语言的 `CHANGED_NOTHING` 和 `LEFT_BEHIND` 在 F11-T23 里。F11-T18 检查 B 点，F11-T23 对不存在的 `menus\`、是文件的 `menus` 和列出失败检查 C 点。

**之前功能的测试。** 设计第 3 节说，`menu new` 和 `menu show` 加进 `COMMANDS`、帮助的第二列从 19 列移到 21 列之后，检查真正帮助的测试仍然成立：F05-T48、F05-T49、F07-T17、F08-T14、F09-T01、F09-T19、F09-T25、F10-T01、F10-T11、F10-T15 和 F10-T16。F05-T23 给 `main` 传它自己的命令，所以它的 `INCOMPLETE_COMMAND` 仍然成立。在架构师的模型上，main 的全部测试都通过了：483 个测试，只在 Linux 上运行的 3 个用例在 Windows 上被跳过（设计第 4 节）。F11 不改动之前功能的任何测试，也不改动 `tests/data/example/` 里的任何文件。F11-T01 检查真正 `COMMANDS` 的帮助里 `menu new` 和 `menu show` 的那两行，所用的形式在 F13 加入 `shop` 之后仍然成立。加上 F11-T11，只在 Linux 上运行的用例变成 4 个。

**R09。** mock 定义了每条消息、带全部字段的两个命令、带全部成员的 `FileOutcome`，以及 `menus` 里的 `NO_MENU`，并把两个命令加进 `COMMANDS`。它的 `FileCreation` 有四个字段，但没有 3.2 的检查。它的 `create_file` 什么都不碰，给出 `FileCreation(FileOutcome.CREATED)`，每个 `run` 都不读文件，什么都不写，什么都不抛，并给出 0（设计第 2 节）。所以只检查命令的字段、帮助、`NO_MENU` 这样的消息、退出码 0、`FileOutcome` 的值，或者有效 `FileCreation` 的默认值和相等性的测试，会在 mock 上通过。只检查 `cli` 在运行命令之前所做的事情的测试也一样，比如缺少数据文件夹、损坏的设置、`menu new 2026-W47 2026-W48`、`menu show --tag quick`、`menu show next --help` 和 `recipe-menu menu`。只检查命令没有改动文件、被拒绝的 `menu new` 保留了文件，或者失败没有留下任何东西的测试也一样。每个检查这类内容的用例，也检查 mock 弄错的东西：命令的输出，`run` 给出的退出码 1 或 2，`run` 抛出的 `UsageError`，新文件的字节，`FileCreation` 的结果、问题、`left` 或 `existing`，`FileCreation` 或 `create_file` 抛出的错误，或者故障工具记录的调用。F11-T01、F11-T02、F11-T04、F11-T05、F11-T06、F11-T22、F11-T32 和 F11-T35 只在一个 mock 会弄错的结果旁边检查这类内容。每个期望 `menu show` 给出退出码 0 的用例都检查完整的输出，这个输出从不为空。每个期望 `menu new` 给出退出码 0 的用例都检查它的三行和新文件的字节。`tests/f11_support.py` 和 `tests/f11_texts.py` 在被导入时不调用 F11 的任何接口。

**两个系统。** 除了只在 Linux 上运行的 F11-T11，每个用例都在 Linux 和 Windows 上运行。CI 只在 Linux 上运行，所以 CI 运行每个用例，而 R09 把跳过的测试算作没有失败的测试。问题用系统的路径分隔符写出它的文件。所以在预期的一行里，`menus/2026-W47.toml` 代表 `str(Path("menus", "2026-W47.toml"))`：在 Windows 上是 `menus\2026-W47.toml`，和原型显示的一样，在 Linux 上是 `menus/2026-W47.toml`。以用例的某个文件夹开头的路径，比如 `example/menus/2026-W48.toml` 或 `R/menus`，代表那个文件夹下这个路径的 `str`：`tmp_path` 里的一个完整路径，用系统的路径分隔符。`menu show` 的表格里没有路径，所以它们的各列在两个系统上宽度相同。中文表格里每个汉字占两列，和 F11 原型一样。涉及两个系统不同之处的输入，要么在两个系统上给出相同的结果，要么由用例写出每个系统给出什么：

- 一个和文件名只有大小写不同的名称，比如 `2026-w47.toml`（F11-T10、F11-T22、F11-T25 和 F11-T28）。两个系统都能有这样的名称，而 `create_file` 和 `list_menu_weeks` 比较的是列出给出的名称，所以两个系统给出相同的结果。`WindowsPath` 比较时不分大小写，所以检查路径的用例比较两个路径的 `str`。
- 一个文件夹里两个只有大小写不同的名称（F11-T11）。只有 Linux 能有这样的名称，所以这个用例只在 Linux 上运行，与 F04-T12、F04-T51 和 F06-T28 相同。
- 文件系统在 A 到 Z 之外也不分大小写的名称（F11-T13 的输入 7）。NTFS 把 `\u00c4.toml` 和 `\u00e4.toml` 当作同一个名称，所以独占打开在 Windows 上抛出 `FileExistsError`，而 Linux 把两个名称分开。用例期望每个系统各自的结果。测试经理在 Troy 的电脑上用 Python 3.13.18 做了这次打开，它抛出了 `FileExistsError`。
- 300 个字符的文件名（F11-T13 的输入 6）。两个系统都拒绝它，在 Troy 的电脑上是 errno 22，在 Linux 上是 `ENAMETOOLONG`。用例从系统取得消息，与 F08-T07 相同。
- 悬空链接（F11-T10 和 F11-T22）。`tests/f08_support.py` 的 `dangling_link` 在 Linux 上创建符号链接，在 Windows 上创建目录联接，与 F08-T05 相同。
- F11-T33 的数据文件夹 `One Drive/菜谱` 里有空格和汉字，在两个系统上都是合法路径。

**被拒绝的访问。** 没有用例通过文件系统拒绝访问，无论是用 `os.chmod`、访问控制列表，还是用 `tests/f04_support.py` 的 `listing_denied`。Linux 上的 root 用户无视权限位，所以依赖权限位的测试以 root 运行时会失败，F04 的测试说明里写过这一点。用例里的每个 `PermissionError` 都来自故障工具，它对每个用户都以同样的方式抛出。所以每个用例在 Linux 上以 root 运行、在 Windows 上以管理员运行时都能通过。

**用例怎样让磁盘出错。** 用例使用 `tests/f08_support.py` 的故障工具 `faults(base, *rules)`，与 F08 相同（F08 测试方案第 2 节）。它打开期间，替换 `os.mkdir`、`os.rmdir`、`os.unlink`、`os.remove`、`os.scandir`、`os.listdir`、`io.open` 和 `builtins.open`，记录对 `base` 下路径的每次调用，并应用它的规则。规则写成种类、路径和效果，比如 `open P: DENIED`：

- `list P: E` 抛出 E，代替列出文件夹 P。
- `open P: E` 抛出 E，代替以 `x` 模式打开 P，所以系统什么都不创建。
- `open P: race` 先像别的程序那样创建内容为 `b"mine\n"` 的 P，然后打开，这次打开抛出系统的 `FileExistsError`。
- `open P: after E` 打开、关闭文件，然后抛出 E。所以 P 存在，但调用从没拿到它。
- `write P: E` 在打开 P 得到的文件上，写入第一次写入的文字的前一半，即 `text[: len(text) // 2]`，刷新，然后抛出 E。
- `unlink P: E` 抛出 E，代替删除 P。
- 效果就是 F08 测试方案里的那些：`DENIED` 是 `PermissionError(errno.EACCES, "Permission denied")`，`IO` 是 `OSError(errno.EIO, "Input/output error")`，`NO_SPACE` 是 `OSError(errno.ENOSPC, "No space left on device")`，`CTRL_C` 是 `KeyboardInterrupt()`，`BUG` 是 `RuntimeError("bug")`。`OSError(errno.EIO, "")` 的 `strerror` 是 `""`，`TimeoutError()` 和 `OSError()` 的 `strerror` 是 `None`。

抛出 `KeyboardInterrupt` 的用例通过 `pytest.raises` 拿回它，或者通过 `tests/f08_support.py` 的 `call_main` 从 `main` 得到退出码 130。`KeyboardInterrupt` 离开 `main` 时，`call_main` 把它变成一次失败，所以错误的实现会让用例失败，而不会中断整个测试运行。

给开发者的说明：只有当 `create_file` 通过设计 3.3 列出的调用访问磁盘时，这些用例才成立。它用 `Path.iterdir`、`os.scandir` 或 `os.listdir` 列出 `path.parent`。它用 `Path.open` 或 `open` 以 `"x"` 模式打开文件，并在打开得到的文件对象上用一次 `write` 调用写入全部文字，文字为空时也一样。它用 `Path.unlink` 删除文件。在 Troy 电脑上的 Python 3.13.18 里，`Path.iterdir` 调用 `os.scandir`，`Path.open` 调用 `io.open`，`Path.unlink` 调用 `os.unlink`。设计 3.3 没有列出的调用，比如 `os.open`、`Path.write_text`、`Path.touch`、`os.replace` 或 `shutil`，会避开故障工具的规则，或者给出另一份记录，所以用例会失败。

**读取记录。** F11-T21、F11-T25 和 F11-T27 记录命令打开了哪些文件、列出了哪些文件夹，用不带规则的 `faults(F.root)`，与 F09-T20 和 F10-T14 相同。故障工具把对数据文件夹下每个路径的打开记为 `read`，以 `x` 模式打开时记为 `open`，后面是相对于这个文件夹、用 `/` 写的路径。它把每次 `os.scandir` 或 `os.listdir` 的列出记进“列出记录”。`menu show` 只通过 F03、F04 和 F06 的读取函数访问磁盘，`menu new` 只通过 `create_file` 访问磁盘（设计第 2 节）。`cli` 在运行命令之前读取 `settings.toml`，所以每份记录都以 `read settings.toml` 开头。

测试经理在 Troy 的电脑上用 Python 3.13.18、main 上的读取函数、故障工具，以及一个按设计实现两个命令和 `create_file` 的模型算出了下面的预期文本。这个模型给出了 F11 原型的每一段输出，A 到 F 块和第 3 节的 PT01 周都是它的输出。

测试数据遵守这些规则，与 F09 和 F10 测试方案相同：

- `EXAMPLE` 是代码仓库里的 `tests/data/example/` 文件夹（架构第 10 节）。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这份副本上的 `DataFolder`。用例里的 `example` 就是这个 `DataFolder`。“P 处的一份新的示例副本”是用 `tests/f05_support.py` 的 `copy_example` 复制的又一份副本。不带 P 的“一份新的示例副本”在 `tmp_path` 下它自己的路径上。
- “一份菜单为空的示例副本”是删掉了 `menus/` 里每个条目的一份新的示例副本，这就是 F11 原型、v0.1-S13 和 v0.1-S14 开始时的样子。
- “P 处的 init 文件夹”由 `tests/f07_changes.py` 的 `make_init` 创建：一份新的示例副本，除 `tomato-egg` 外没有菜谱，没有菜单，带有空文件夹 `menus/` 和 `shopping/`。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。它在 `example` 之外，所以不带 `--data` 的一行找不到数据文件夹，除非用例在 `home / "recipe-menu"` 放了一个。
- 测试用 `tests/f03_support.py` 的 `write` 写出每个文件，它以 UTF-8 和 LF 换行写文件，并先创建所在的文件夹，或者直接写字节。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 替换文件 F 里的第一个 X，`edit` 会检查 F 里有 X。
- 测试不改动代码仓库，不碰 `~/recipe-menu`，也不读时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`。F11-T36 和 F11-T38 启动 `python -m recipe_menu` 时把 `HOME` 和 `USERPROFILE` 设成 `tmp_path` 里的一个文件夹。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

下面这些有名字的改动构造用例的文件夹。每个改动作用于它所在用例的数据文件夹：

- 来自 F09 测试方案：麻婆错误、米饭 0 份、目录花括号错误、损坏的设置、没有目录、没有菜谱文件夹、菜谱是文件、Rice Bowl、大写的 rice、文件夹 x、额外的菜谱，以及带 S 的长名称。`tests/f07_changes.py` 和 `tests/f09_support.py` 的辅助函数完成这些改动。额外的菜谱是没有中文名称的 `boiled-egg`、没有英文名称的 `steamed-egg`，以及 `water`。带 S 的长名称只保留 `rice`，并加上 `a-long`，它的名称里有 TOML 转义 S，即 `\n`、`\r\n` 或 `\u2028`，所以每个名称占两行。
- 来自 F10 测试方案：中文设置，即把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`；BOM 和 CRLF，即把文件夹里的每个文件重新写成 `b"\xef\xbb\xbf"` 加上它的字节，并把其中每个 `b"\n"` 换成 `b"\r\n"`。
- 来自 `tests/f06_support.py` 里 F06 的辅助函数：菜单错字，即 `typo`；v0.1-S07 的菜单错误，即 `mistakes`。菜单错字让 `menus/2026-W47.toml` 里周一的晚餐写成 `tomato-eggs`，和 F11 原型“A menu with a mistake”一样。
- 没有菜单文件夹：删掉 `menus/` 和其中的一切。菜单文件夹是文件：同样删掉，然后在 `menus` 的路径上写一个空文件。
- 周 B、周 C 和周 D：按顺序用下面三段文字写出 `menus/2026-W48.toml`、`menus/2026-W49.toml` 和 `menus/2026-W50.toml`。周 C 和额外的菜谱一起用，周 D 和带 S 的长名称一起用。周 B 把周一的晚餐写在午餐之前，在一餐里写了两次 `rice`，给一道菜 10 份，并写了带警告的 `red-braised-pork`。

```toml
week = "2026-W48"

[monday]
dinner = ["rice", "rice"]
lunch = ["mapo-tofu"]

[friday]
lunch = [{ recipe = "choy-sum", servings = 10 }]

[sunday]
dinner = ["red-braised-pork"]
```

```toml
week = "2026-W49"

[tuesday]
breakfast = ["boiled-egg", { recipe = "steamed-egg", servings = 1 }]

[sunday]
breakfast = ["water"]
```

```toml
week = "2026-W50"

[monday]
lunch = ["a-long", "rice"]
```

调用 `main` 遵守这些约定：

- 像“在 F 里 `menu show 2026-W47 --lang zh`”这样的一行，代表 `tests/f09_support.py` 的 `at(home, F, "menu", "show", "2026-W47", "--lang", "zh")`。它加上 `--data` 和 F，通过 `tests/f07_support.py` 的 `call` 运行 `main`，传入 `home`、`environ`、`today=date(2026, 11, 10)` 和两个新的 `io.StringIO` 流，不传 `commands`，所以 `main` 使用真正的 `COMMANDS`。“在 D 这天”的一行以同样的方式运行，但 `today=D`，通过 `tests/f11_support.py` 的 `on(home, F, D, *argv)` 完成。“不指定文件夹”的一行没有 `--data`。除非用例给出，`environ` 是 `{}`。
- 引号里的词是一个词，按 Python 字符串的写法带着转义，比如 `""`、`" this"` 或 `"2026-W47\n"`。词里的每个 `\uXXXX` 代表那一个字符。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟着 `"\n"`，此外没有别的。`(c, err L)` 代表 `(c, "", err)`，其中 err 是 L 的各行，每行后面跟着 `"\n"`。`(130, "", "")` 是什么都没写就退出。测试比较完整的文字，从不比较它们的 `splitlines()`，因为 `splitlines()` 也在 U+000D 和 U+2028 处拆分，而 F11-T30 必须确认输出里没有它们。
- `STOP(W, M)` 和 `STOP_ZH(W, M)` 是 `stop_at_error` 的英文三行和中文三行，与 F09 测试方案的定义相同，由 `tests/f09_texts.py` 的 `stop` 构造结果。W 是一个文件，比如 `catalog.toml`，或者一个文件加一个位置，比如 `menus/2026-W47.toml, Monday dinner`，中文是 `menus/2026-W47.toml，周一晚餐`。
- “在 `check` 的错误之中”的意思与 F09 测试方案相同，由 `tests/f09_support.py` 的 `assert_among_check` 检查。

直接调用 `create_file` 遵守这些约定：

- `base` 是 `tmp_path` 下每次调用自己的一个空文件夹。`F` 是 `DataFolder(base / "recipe-menu")`，Q 是 `F.menu_file("2026-W47")`。在规则或记录里，`F.menus` 代表那个文件夹的路径，记录用相对于 `base` 的路径写出，比如 `open recipe-menu/menus/2026-W47.toml`。
- 问题写成它的文件和它的消息，比如 `menus: FOLDER_MISSING`，文件 `Path(".")` 写成 `.: FOLDER_MISSING`。`create_file` 的每个问题都是没有位置的错误。测试检查 `severity is Severity.ERROR`、`str(problem.file)`、`place is None`、`text(Lang.EN)` 和 `text(Lang.ZH)`。它把 `left` 作为由各路径的 `str` 组成的元组比较，把 `existing` 作为 `str` 比较。
- “X 的树”和“X 的完整记录”就是 F08 测试方案里的那些，由 `tests/f08_support.py` 的 `tree` 和 `full_record` 给出：X 下的每个条目，带它的种类和每个文件的字节，后者还带每个条目的 `st_mtime_ns`。

预期文本如下。测试在 `tests/f11_texts.py` 里把每一段都写成字面量。它们不引用任何消息，也从不读原型文件，因为 `menu` 和各读取函数的消息都是内部的（设计第 2 节，架构第 8 节）。`menu_text` 和 `EMPTY` 由测试构造。

- `SHOW_47` 和 `SHOW_47_ZH` 是 F11 原型“Show the week after you fill it”的两段输出，各 17 行。
- `PROTOTYPE_FILE` 是 F11 原型“Create next week's menu”的 `toml` 代码块的字节：它的 32 行，每行以 LF 结尾，用 UTF-8 编码。它和设计 2.2 的 `toml` 代码块是同一段文字。
- `menu_text(W, S)` 是周 W、餐次 S 的 2.2 文件，由测试按 2.2 的规则构造，与设计 2.2 的示例相同：`# W: ` 加上 F06 给出的 W 的英文 `date_range`，两行讲菜的注释，`week = "W"`，然后对 `Day` 的每一天写一个空行、`[day]`，并按 `Meal` 的顺序为 S 的每一餐写 `meal = []`。每行以 LF 结尾，文字用 UTF-8 编码。S 写成列表，比如 `[lunch, dinner]`。
- `NEW(P, D, M)` 是新菜单的英文三行：`Created P for D:`、`7 days with M, all empty.` 和 `Add recipe IDs to the meals, then run "recipe-menu check".`。`NEW_ZH(P, D, M)` 是 `已创建 P，日期为 D：`、`共 7 天，每天有M，都还是空的。` 和 `在各餐里填上菜谱 ID，然后运行“recipe-menu check”。`。P 是文件的完整路径，D 是这一行语言里的日期，M 是这一行显示的各餐，比如 `lunch and dinner` 和 `午餐和晚餐`。
- `EXISTS(P)` 是 `P already exists. Nothing was changed.`，`EXISTS_ZH(P)` 是 `P 已存在。没有做任何修改。`。
- `FAIL(Q, M)` 是失败的三行：Q，然后是两个空格加上 M 的英文文字，然后是 `Nothing was changed.`。`FAIL_ZH(Q, M)` 用 M 的中文文字和 `没有做任何修改。`。`LEFT(Q, M, W)` 的第三行是 `menu new could not remove the file that it created. Delete it, then run "recipe-menu menu new W" again.`，`LEFT_ZH(Q, M, W)` 的第三行是 `menu new 没能删除它创建的文件。请删除这个文件，然后再运行“recipe-menu menu new W”。`。Q 是完整路径。这些不是 `init` 的文字，所以 `tests/f11_texts.py` 自己定义它们，不用 `tests/f08_texts.py` 的 `fail`。
- `NO_MENU(W)` 是 `There is no menu for W. Run "recipe-menu menu new W" to create it.`，`NO_MENU_ZH(W)` 是 `W 没有菜单。运行“recipe-menu menu new W”创建它。`。
- `NOT_A_WEEK(V)` 是 `"V" is not a week. Write an ISO week such as 2026-W47, "this", or "next".`，`NOT_A_WEEK_ZH(V)` 是 `“V”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。`，V 按输入的原样写出。
- `EMPTY(W, L, S)` 是 `menu show` 对没有菜的周 W、用语言 L、餐次 S 的输出：`Menu for W, D` 或 `W 菜单，D`，一个空行，表格的各行，一个空行，以及 `The menu has no dishes yet.` 或 `这个菜单还没有菜。`。测试用 F02 的 `format_table` 排出表格，不传 `min_widths`。表格的行是标题行，即 `Day` 或 `日期`，加上 S 每一餐的标题 `Breakfast` 或 `早餐`、`Lunch` 或 `午餐`、`Dinner` 或 `晚餐`，然后 W 的每个日期一行，用 F06 的 `short_date`，每一餐写 `\u2014`。D 来自 F06 的 `date_range`。测试先检查 `EMPTY` 给出 F 块的六段输出。
- `HELP` 是 `tests/f05_texts.py` 的 `HELP_EN_LINES` 的 21 行去掉以 `  shop ` 开头的那一行，共 20 行。`HELP_ZH` 是 `HELP_ZH_LINES` 去掉以 `  shop ` 开头的那一行。这就是 `COMMANDS` 里只有 F11 的七个命令时设计 2.1 的帮助。两张表格里每一行的文字都在 21 列之后开始。

A 到 F 块写出用例提到、而原型没有显示的 `menu show` 输出。每个 `PS>` 行像原型那样给出不带 `--data` 的命令行，并带着 `--data` 和它所在块的文件夹运行。一个 `PS>` 行的输出是它后面的各行，直到并包括它的最后一行。一个空行把它和下一个 `PS>` 行隔开。每段输出的退出码都是 0，err 为空。块里的一行是一个 Python 字符串的内容：`\u00d7` 和 `\u2014` 各代表一个字符，和设计的写法一样，所以各列在输出里对齐，而不是在这份文档里对齐。

A 块，在一份新的示例副本里写入周 B：

```text
PS> recipe-menu menu show 2026-W48
Menu for 2026-W48, 23 to 29 November 2026

Day          Lunch                     Dinner
Mon 23 Nov   Mapo tofu \u00d72              Steamed rice \u00d72
                                       Steamed rice \u00d72
Tue 24 Nov   \u2014                         \u2014
Wed 25 Nov   \u2014                         \u2014
Thu 26 Nov   \u2014                         \u2014
Fri 27 Nov   Stir-fried choy sum \u00d710   \u2014
Sat 28 Nov   \u2014                         \u2014
Sun 29 Nov   \u2014                         Red-braised pork belly \u00d72

4 meals, 5 dishes. \u00d7n: servings.

PS> recipe-menu menu show 2026-W48 --lang zh
2026-W48 菜单，2026年11月23日至29日

日期            午餐           晚餐
周一 11月23日   麻婆豆腐 \u00d72    米饭 \u00d72
                               米饭 \u00d72
周二 11月24日   \u2014              \u2014
周三 11月25日   \u2014              \u2014
周四 11月26日   \u2014              \u2014
周五 11月27日   清炒菜心 \u00d710   \u2014
周六 11月28日   \u2014              \u2014
周日 11月29日   \u2014              红烧肉 \u00d72

4 餐，5 道菜。\u00d7n：份数。
```

B 块，在一份带额外菜谱、`settings.toml` 写成 `meals = ["breakfast"]` 的新示例副本里写入周 C：

```text
PS> recipe-menu menu show 2026-W49
Menu for 2026-W49, 30 November to 6 December 2026

Day          Breakfast
Mon 30 Nov   \u2014
Tue 1 Dec    Boiled egg \u00d72
             蒸蛋 \u00d71
Wed 2 Dec    \u2014
Thu 3 Dec    \u2014
Fri 4 Dec    \u2014
Sat 5 Dec    \u2014
Sun 6 Dec    Boiled water \u00d72

2 meals, 3 dishes. \u00d7n: servings.

PS> recipe-menu menu show 2026-W49 --lang zh
2026-W49 菜单，2026年11月30日至12月6日

日期            早餐
周一 11月30日   \u2014
周二 12月1日    Boiled egg \u00d72
                蒸蛋 \u00d71
周三 12月2日    \u2014
周四 12月3日    \u2014
周五 12月4日    \u2014
周六 12月5日    \u2014
周日 12月6日    白开水 \u00d72

2 餐，3 道菜。\u00d7n：份数。
```

C 块，在一份带 S 的长名称的新示例副本里写入周 D，每个 S 都相同：

```text
PS> recipe-menu menu show 2026-W50
Menu for 2026-W50, 7 to 13 December 2026

Day          Lunch               Dinner
Mon 7 Dec    A long first line   \u2014
             end \u00d72
             Steamed rice \u00d72
Tue 8 Dec    \u2014                   \u2014
Wed 9 Dec    \u2014                   \u2014
Thu 10 Dec   \u2014                   \u2014
Fri 11 Dec   \u2014                   \u2014
Sat 12 Dec   \u2014                   \u2014
Sun 13 Dec   \u2014                   \u2014

1 meal, 2 dishes. \u00d7n: servings.

PS> recipe-menu menu show 2026-W50 --lang zh
2026-W50 菜单，2026年12月7日至13日

日期            午餐           晚餐
周一 12月7日    长长的第一行   \u2014
                尾 \u00d72
                米饭 \u00d72
周二 12月8日    \u2014              \u2014
周三 12月9日    \u2014              \u2014
周四 12月10日   \u2014              \u2014
周五 12月11日   \u2014              \u2014
周六 12月12日   \u2014              \u2014
周日 12月13日   \u2014              \u2014

1 餐，2 道菜。\u00d7n：份数。
```

D 块是 F11-T02 输入 1 的输出，即在 `example` 上用三餐、3 份的设置以英文直接调用 `run`：

```text
Menu for 2026-W47, 16 to 22 November 2026

Day          Breakfast   Lunch                       Dinner
Mon 16 Nov   \u2014           \u2014                           Tomato and egg stir-fry \u00d73
                                                     Stir-fried choy sum \u00d73
                                                     Steamed rice \u00d73
Tue 17 Nov   \u2014           \u2014                           Mapo tofu \u00d73
                                                     Steamed rice \u00d73
Wed 18 Nov   \u2014           \u2014                           \u2014
Thu 19 Nov   \u2014           \u2014                           \u2014
Fri 20 Nov   \u2014           \u2014                           \u2014
Sat 21 Nov   \u2014           Tomato and egg noodles \u00d73   \u2014
Sun 22 Nov   \u2014           \u2014                           Cola chicken wings \u00d74
                                                     Stir-fried choy sum \u00d74
                                                     Steamed rice \u00d74

4 meals, 9 dishes. \u00d7n: servings.
```

E 块，F11-T34 的 init 文件夹里的 v0.1-S16，在它的第 1 步和第 2 步之后：

```text
PS> recipe-menu menu show 2026-W48
Menu for 2026-W48, 23 to 29 November 2026

Day          Breakfast                    Lunch   Dinner
Mon 23 Nov   Tomato and egg stir-fry \u00d73   \u2014       \u2014
Tue 24 Nov   \u2014                            \u2014       \u2014
Wed 25 Nov   \u2014                            \u2014       \u2014
Thu 26 Nov   \u2014                            \u2014       \u2014
Fri 27 Nov   \u2014                            \u2014       \u2014
Sat 28 Nov   \u2014                            \u2014       \u2014
Sun 29 Nov   \u2014                            \u2014       \u2014

1 meal, 1 dish. \u00d7n: servings.

PS> recipe-menu menu show 2026-W48 --lang zh
2026-W48 菜单，2026年11月23日至29日

日期            早餐          午餐   晚餐
周一 11月23日   番茄炒蛋 \u00d73   \u2014      \u2014
周二 11月24日   \u2014             \u2014      \u2014
周三 11月25日   \u2014             \u2014      \u2014
周四 11月26日   \u2014             \u2014      \u2014
周五 11月27日   \u2014             \u2014      \u2014
周六 11月28日   \u2014             \u2014      \u2014
周日 11月29日   \u2014             \u2014      \u2014

1 餐，1 道菜。\u00d7n：份数。
```

F 块，在一份菜单为空的示例副本里，运行 `menu new 2026-W47`、`menu new 2026-W53` 和 `menu new 2026-W23` 之后：

```text
PS> recipe-menu menu show 2026-W47
Menu for 2026-W47, 16 to 22 November 2026

Day          Lunch   Dinner
Mon 16 Nov   \u2014       \u2014
Tue 17 Nov   \u2014       \u2014
Wed 18 Nov   \u2014       \u2014
Thu 19 Nov   \u2014       \u2014
Fri 20 Nov   \u2014       \u2014
Sat 21 Nov   \u2014       \u2014
Sun 22 Nov   \u2014       \u2014

The menu has no dishes yet.

PS> recipe-menu menu show 2026-W47 --lang zh
2026-W47 菜单，2026年11月16日至22日

日期            午餐   晚餐
周一 11月16日   \u2014      \u2014
周二 11月17日   \u2014      \u2014
周三 11月18日   \u2014      \u2014
周四 11月19日   \u2014      \u2014
周五 11月20日   \u2014      \u2014
周六 11月21日   \u2014      \u2014
周日 11月22日   \u2014      \u2014

这个菜单还没有菜。

PS> recipe-menu menu show 2026-W53
Menu for 2026-W53, 28 December 2026 to 3 January 2027

Day          Lunch   Dinner
Mon 28 Dec   \u2014       \u2014
Tue 29 Dec   \u2014       \u2014
Wed 30 Dec   \u2014       \u2014
Thu 31 Dec   \u2014       \u2014
Fri 1 Jan    \u2014       \u2014
Sat 2 Jan    \u2014       \u2014
Sun 3 Jan    \u2014       \u2014

The menu has no dishes yet.

PS> recipe-menu menu show 2026-W53 --lang zh
2026-W53 菜单，2026年12月28日至2027年1月3日

日期            午餐   晚餐
周一 12月28日   \u2014      \u2014
周二 12月29日   \u2014      \u2014
周三 12月30日   \u2014      \u2014
周四 12月31日   \u2014      \u2014
周五 1月1日     \u2014      \u2014
周六 1月2日     \u2014      \u2014
周日 1月3日     \u2014      \u2014

这个菜单还没有菜。

PS> recipe-menu menu show 2026-W23
Menu for 2026-W23, 1 to 7 June 2026

Day         Lunch   Dinner
Mon 1 Jun   \u2014       \u2014
Tue 2 Jun   \u2014       \u2014
Wed 3 Jun   \u2014       \u2014
Thu 4 Jun   \u2014       \u2014
Fri 5 Jun   \u2014       \u2014
Sat 6 Jun   \u2014       \u2014
Sun 7 Jun   \u2014       \u2014

The menu has no dishes yet.

PS> recipe-menu menu show 2026-W23 --lang zh
2026-W23 菜单，2026年6月1日至7日

日期          午餐   晚餐
周一 6月1日   \u2014      \u2014
周二 6月2日   \u2014      \u2014
周三 6月3日   \u2014      \u2014
周四 6月4日   \u2014      \u2014
周五 6月5日   \u2014      \u2014
周六 6月6日   \u2014      \u2014
周日 6月7日   \u2014      \u2014

这个菜单还没有菜。
```

用例里 `cli` 的消息是 F05 设计 2.10 里带 `menu new` 和 `menu show` 的文字。`tests/f09_texts.py` 的 `RUN_HELP_COMMANDS` 和 `RUN_HELP_OPTIONS` 给出跟在它们后面的那一行。用例里各读取函数的消息就是 F09 测试方案第 2 节的那些：`FILE_MISSING`、`FILE_IS_FOLDER`、`MISSING_BRACE`、`FOLDER_MISSING`、`FOLDER_IS_FILE`、列出时的 `NOT_A_RECIPE_ID`、`TOML_ENDING_NOT_SMALL`、菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`、`SERVINGS_TOO_FEW(servings=0)`，以及设置的 `UNKNOWN_MEAL(meal="supper")`。下面这些来自 F06 设计 2.8 和 2.9、F04 设计 3.1、F03 设计 2.10，以及 F08 设计 3.2：

| 消息 | 英文 | 中文 |
| --- | --- | --- |
| `NOT_A_WEEK_NAME` | `This file name is not an ISO week such as 2026-W47. Rename the file.` | `这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。` |
| `UNKNOWN_RECIPE(recipe="R")` | `Unknown recipe "R".` | `未知菜谱“R”。` |
| `WEEK_NOT_FILE_NAME(name="N", week="W")` | `The file name says N, but the file says W.` | `文件名是 N，但文件里写的是 W。` |
| 菜单的 `UNKNOWN_MEAL(meal="M", meals="S")` | `Unknown meal "M". The settings name S.` | `未知餐次“M”。设置里的餐次：S。` |
| `MISSING_KEY(key="week")` | `The key "week" is missing.` | `缺少键“week”。` |
| `FOLDER_ACCESS_DENIED` | `The folder cannot be read: access is denied.` | `无法读取文件夹：没有访问权限。` |
| `FOLDER_SYSTEM_ERROR(reason="X")` | `The folder cannot be read. The system says: X` | `无法读取文件夹。系统提示：X` |
| `FILE_WRITE_DENIED` | `The file cannot be written: access is denied.` | `无法写入文件：没有访问权限。` |
| `FILE_WRITE_ERROR(reason="X")` | `The file cannot be written. The system says: X` | `无法写入文件。系统提示：X` |

用例里的位置是 `line 11`（`第 11 行`）、`ingredient 3`（`食材 3`）、`servings`（`份数`）和 `meals`（`餐次`），菜单的位置是 `week`（`周次`）、`Monday dinner`（`周一晚餐`）和 `Saturday lunch`（`周六午餐`）。

用例分成下面这些文件，使每个文件都在 R06 的 500 行之内：

| 文件 | 用例 |
| --- | --- |
| `tests/test_f11_commands.py` | F11-T01 到 F11-T04 |
| `tests/test_f11_file_creation.py` | F11-T05 和 F11-T06 |
| `tests/test_f11_create_file.py` | F11-T07 到 F11-T11 |
| `tests/test_f11_create_file_errors.py` | F11-T12 到 F11-T14 |
| `tests/test_f11_menu_new.py` | F11-T15 到 F11-T19 |
| `tests/test_f11_weeks.py` | F11-T20 和 F11-T21 |
| `tests/test_f11_menu_new_errors.py` | F11-T22 到 F11-T25 |
| `tests/test_f11_menu_show.py` | F11-T26 和 F11-T27 |
| `tests/test_f11_menu_show_errors.py` | F11-T28 和 F11-T29 |
| `tests/test_f11_table.py` | F11-T30 和 F11-T31 |
| `tests/test_f11_cli.py` | F11-T32 |
| `tests/test_f11_integration.py` | F11-T33 到 F11-T36 |
| `tests/test_f11_random.py` | F11-T37，以及它的菜单生成器 |
| `tests/test_f11_performance.py` | F11-T38 |
| `tests/f11_support.py` | 没有测试。`on`、菜单为空的示例副本、没有菜单文件夹、菜单文件夹是文件、周 B 到周 D、`menu_text`，以及检查一个 `FileCreation` 及其问题、`left` 和 `existing` 的函数。它复用 `tests/f05_support.py` 的 `make_home`、`copy_example` 和 `run_module`，`tests/f05_texts.py` 的 `no_data_folder`，`tests/f06_support.py` 的 `typo` 和 `mistakes`，`tests/f07_support.py` 的 `call` 和 `snapshot`，`tests/f07_changes.py` 的 `make_init`、`edit` 和有名字的改动，`tests/f08_support.py` 的 `faults`、`rule`、各个效果、`call_main`、`system_message`、`dangling_link`、`tree` 和 `full_record`，`tests/f09_support.py` 的 `at`、`made`、`new_context`、`run_command`、`assert_among_check` 和有名字的改动，`tests/f10_support.py` 的 `chinese_settings` 和 `bom_and_crlf`，以及 `tests/f03_support.py` 的 `write` 和 `put_bytes`。 |
| `tests/f11_texts.py` | 没有测试。上面的预期文本和 A 到 F 块，写成字面量，以及 `EMPTY`。它从 `tests/f05_texts.py` 的 `HELP_EN_LINES` 和 `HELP_ZH_LINES` 得到 `HELP` 和 `HELP_ZH`，复用 `tests/f07_support.py` 的 `AFTER` 和 `AFTER_ZH`，以及 `tests/f09_texts.py` 的 `out`、`err`、`stop`、`Prob`、各读取函数的消息、`RUN_HELP_COMMANDS` 和 `RUN_HELP_OPTIONS`。 |
| `tests/pt01_support.py` | 没有测试。它新增 `pt01_menu_show`，即在 PT01 文件夹上运行 `menu show 2026-W26` 的预期输出（第 3 节）。它的其他函数保持原来的名字和行为。 |
| `tests/conftest.py` | 不变。F11 使用它的 fixture `example_folder`，以及 pytest 的 `tmp_path`、`monkeypatch` 和 `record_property`。 |

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F11-T01 | 单元 | `MENU_NEW_COMMAND`、`MENU_NEW_COMMAND.run`、`main` | 2.1 的示例。`MENU_NEW_COMMAND` 的词是 `menu new`，用法是 `menu new [WEEK]` 和 `menu new [周]`，帮助行是 F05 原型里的那一行，参数 `WEEK` 可以不写、不能重复，没有选项，并且是 `FolderUse.READ`。它的 `run` 从参数和 `context.today` 得到周，把 `context.settings` 的各餐写进文件，用 `context.lang` 写出它的各行，从不用 `context.settings` 的语言，并给出 0；或者把拒绝写到 `context.err` 并给出 1。帮助在 `search WORD...` 后面列出 `menu new [WEEK]` 和 `menu show [WEEK]`，共 20 行，两张表格的第二列都在 21 列之后开始（2.1，选择 1 到 5）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`。那一行 `# raises` 在 `pytest.raises(UsageError)` 里运行，用一个值相同的新 `Context` 和新的流。在 `help_lines` 里，对 `main` 的调用还传入 `commands=(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND)`，因为只有这七个命令单独在 `COMMANDS` 里时那 20 行才成立，而 F13 会加入 `shop`。然后，每次都用新的流：1. `run`，用 `Context(Lang.EN, example, Settings(Lang.ZH, tuple(Meal), 5), out, err, date(2030, 1, 1))` 和 `Arguments(("2026-W49",))`。2. `run`，用 `Context(Lang.EN, example, Settings(), out, err, date(2026, 12, 30))` 和 `Arguments(())`。3. 再做一次 2 的调用。4. `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部内容。5. 通过 `call` 用真正的 `COMMANDS` 运行 `--help` 和 `--help --lang zh`。 | 示例的每条断言都成立，那一行 `# raises` 抛出 `UsageError`，之后它的两个流都为空，`menus/` 里只有 `2026-W47.toml` 和 `2026-W48.toml`。1. 0，out 是 `NEW(example/menus/2026-W49.toml, 30 November to 6 December 2026, breakfast, lunch, and dinner)`，err 为空，文件内容是 `menu_text(2026-W49, [breakfast, lunch, dinner])`。2. 0，out 是 `NEW(example/menus/2026-W53.toml, 28 December 2026 to 3 January 2027, lunch and dinner)`，err 为空，文件内容是 `menu_text(2026-W53, [lunch, dinner])`。3. 1，out 为空，err 是 `EXISTS(example/menus/2026-W53.toml)` 加一个换行。4. `HELP` 和 `HELP_ZH`。5. 退出码 0，err 为空。在 out 里，以 `  search WORD... ` 开头的那一行后面的两行，分别以 `  menu new [WEEK] ` 和 `  menu show [WEEK] ` 开头，以 `Create an empty week menu.` 和 `Show a week menu.` 结尾。中文里，以 `  search 词... ` 开头的那一行后面的两行，分别以 `  menu new [周] ` 和 `  menu show [周] ` 开头，以 `创建一个空的周菜单。` 和 `查看一个周菜单。` 结尾。它们的文字和以 `  --lang en\|zh` 开头的那一行的文字从同一个显示列开始：每段文字前面部分的 `display_width` 相同。F13 在它们后面加入 `shop` 之后，这些规则仍然成立。 |
| F11-T02 | 单元 | `MENU_SHOW_COMMAND`、`MENU_SHOW_COMMAND.run` | 2.3 的示例。`MENU_SHOW_COMMAND` 的词是 `menu show`，用法是 `menu show [WEEK]` 和 `menu show [周]`，帮助行是 F05 原型里的那一行，参数 `WEEK` 可以不写，没有选项，并且是 `FolderUse.READ`。它的 `run` 用 `context.settings` 的餐次和份数读取这一周，从 `context.today` 得到周，用 `context.lang` 写出，两次调用之间不保留状态（2.3，2.4 第 6 步）。 | 示例的各行，`folder` 是 `example`。那一行 `# raises` 在 `pytest.raises(UsageError)` 里运行，用一个值相同的新 `Context` 和新的流。然后，每次都用新的流：1. `run`，用 `Context(Lang.EN, example, Settings(Lang.ZH, tuple(Meal), 3), out, err, date(2030, 1, 1))` 和 `Arguments(("2026-W47",))`。2. `run`，用 `Context(Lang.ZH, example, Settings(Lang.EN, (Meal.DINNER,), 5), out, err, date(2026, 11, 17))` 和 `Arguments(())`。3. `run`，用示例的 context 的值和 `Arguments(("2026-W48",))`。4. 用 `Arguments(("next",))` 再运行示例的那次调用两次。 | 示例的每条断言都成立，那一行 `# raises` 抛出 `UsageError`，之后它的两个流都为空。1. 0，out 是 D 块的各行，err 为空：三餐各有一列，没有写份数的菜都是 `\u00d73`，周日的菜是 `\u00d74`。2. 1，out 为空，err 是 `STOP_ZH(menus/2026-W47.toml，周六午餐, 菜单的 UNKNOWN_MEAL(meal="lunch", meals="dinner"))`：只有晚餐时，周六的 `lunch = ["tomato-egg-noodles"]` 是错误，而午餐的空列表不是。3. 1，out 为空，err 是 `NO_MENU(2026-W48)`。4. 每次运行都再次给出示例那次运行的输出。 |
| F11-T03 | 单元 | `MENU_NEW_COMMAND.run`、`MENU_SHOW_COMMAND.run` | 2.2 和 2.4 的第 1 步。每个 `run` 在访问磁盘、写出任何输出之前，用 `week_from_argument` 把 `WEEK` 的值变成周。不是周的值抛出 `UsageError(NOT_A_WEEK, None, week=value)`，它没有提示。`this`、`next`、ISO 周和不写值都能通过（2.1 和 2.3 的错误，选择 2）。 | 对两个命令中的每一个，每次调用都用新的流和 `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`，在 `faults(tmp_path)` 里运行。1. 在 `pytest.raises(UsageError)` 里：对 `"2026-W99"`、`"Next"`、`"THIS"`、`""`、`" 2026-W47"`、`"2026-W47\n"`、`"2026-w47"`、`"2026-W7"`、`"2025-W53"`、`"2026-W00"`、`"this week"`，以及用全角数字写 2026 的 `"\uff12\uff10\uff12\uff16-W47"` 中的每个 V，用 `Arguments((V,))`。2. 对 `()`、`("this",)`、`("next",)`、`("2026-W47",)`、`("2026-W53",)` 和 `("0001-W01",)` 中的每个 V，用 `Arguments(V)`。 | 1. 每个错误的 `text(Lang.EN)` 是 `NOT_A_WEEK(V)`，`text(Lang.ZH)` 是 `NOT_A_WEEK_ZH(V)`，`hint` 是 `None`。每次调用之后两个流都为空，故障工具的记录和列出记录都为空。2. 没有调用抛出。对 `menu new`，每次调用给出 1，out 为空，err 是 `FAIL(tmp_path/missing/menus, FOLDER_MISSING)`。对 `menu show`，每次调用给出 1，out 为空，err 是 `STOP(catalog.toml, FILE_MISSING)`。`tmp_path / "missing"` 仍然不存在。 |
| F11-T04 | 单元 | `NO_MENU`、`recipe-menu menu show` | 3.1 的示例。`menus` 导出只有一个占位符 `week` 的 `NO_MENU`，对没有菜单文件的周，`menu show` 在错误流上正好写出这条消息，共一行（3.1，选择 6）。 | 示例的各行。然后在 `example` 里：对 `2026-W48` 和 `2027-W01` 中的每个 W，`menu show W` 和 `menu show W --lang zh`。 | 示例的每条断言都成立。每一行给出退出码 1，out 为空，err 是 `NO_MENU.render(Lang.EN, week=W) + "\n"` 或 `NO_MENU.render(Lang.ZH, week=W) + "\n"`，也就是 `NO_MENU(W)` 和 `NO_MENU_ZH(W)` 这两行。 |
| F11-T05 | 单元 | `FileOutcome`、`FileCreation` | 3.2 的示例：成员的值，带默认值和字段的有效结果，相等和哈希，以及六个错误的调用（3.2）。 | 示例的各行。然后 `hash(created)` 和 `hash(failed)`。 | 示例的每条断言都成立，它的六行 `# raises` 都抛出 `ValueError`。`hash` 对两个结果都给出 `int`，`failed` 和一个新的 `FileCreation(FileOutcome.FAILED, problem, left)` 的哈希相同。 |
| F11-T06 | 单元 | `FileCreation` | 四个字段的每种组合都遵守 3.2 的表格和它的错误表。`FAILED` 需要一个错误，`left` 里可以有一个路径。`EXISTS` 需要 `existing`。其他成员不带问题，`left` 为空，没有 `existing`。警告从不是这个问题（3.2）。 | `M = Message("The file cannot be written: access is denied.", "无法写入文件：没有访问权限。")`，`E = Problem.error(Path("menus", "2026-W47.toml"), None, M)`，`W = Problem.warning(Path("menus", "2026-W47.toml"), None, M)`，`P = tmp_path / "recipe-menu" / "menus" / "2026-W47.toml"`，`L = (P,)`。对每个成员 o、`None`、E 和 W 中的每个 p、`()`、L 和 `L + L` 中的每个 l，以及 `None` 和 P 中的每个 x，调用 `FileCreation(o, p, l, x)`：共 54 次。 | 正好 4 次调用给出 `FileCreation`：`CREATED` 带 `None`、`()` 和 `None`，`EXISTS` 带 `None`、`()` 和 P，以及 `FAILED` 带 E、x 为 `None`、l 为 `()` 或 L。每个都原样给回它的四个字段。其他 50 次调用抛出 `ValueError`。 |
| F11-T07 | 单元 | `create_file` | 3.3 的示例：一个新文件，找到它的第二次调用，只有大小写不同的名称，不存在的文件夹，两个系统都拒绝的 300 个字符的名称，以及三个错误的调用（3.3）。 | 示例的各行，`tmp` 是空文件夹 `tmp_path / "tmp"`。 | 示例的每条断言都成立，它的三行 `# raises` 都抛出各自的错误。之后，`tmp` 的树里只有 `recipe-menu`、`recipe-menu/menus`、内容为 `b'week = "2026-W47"\n'` 的 `recipe-menu/menus/2026-W47.toml`，以及空的 `recipe-menu/menus/2026-w48.toml`。 |
| F11-T08 | 单元 | `create_file` | 第 1 步。错误的调用在访问磁盘之前抛出：根之外的路径、根本身、相对路径，以及 UTF-8 无法编码的文字（3.3 第 1 步和错误）。 | `F` 带一个空的 `F.menus`，每次调用都在 `faults(base)` 里运行：1. `create_file(F, base / "elsewhere.toml", "")`。2. `create_file(F, F.root, "")`。3. `create_file(F, Path("menus", "2026-W47.toml"), "")`。4. `create_file(F, Q, "\udc80")`。5. `create_file(F, Q, "ok\n\ud800")`。 | 1 到 3 抛出 `ValueError`，4 和 5 抛出 `UnicodeEncodeError`。每次调用之后，记录和列出记录都为空，`F.menus` 仍然是空的。 |
| F11-T09 | 单元 | `create_file` | 第 2 步和第 4 步。成功的调用列出文件所在的文件夹一次，以 `x` 模式打开文件一次，写入文字的 UTF-8 字节，没有字节顺序标记，换行就是文字里的换行。它不读任何文件，给出 `FileCreation(FileOutcome.CREATED)`。空文字给出空文件。根里的任何文件夹都可以，根本身也可以（3.3）。 | `F` 带空文件夹 `F.menus` 和 `F.recipes`，每次调用都在 `faults(base)` 里运行：1. `create_file(F, Q, 'week = "2026-W47"\n')`。2. `create_file(F, F.menu_file("2026-W48"), "a\r\nb\n")`。3. `create_file(F, F.menu_file("2026-W49"), "番茄\n")`。4. `create_file(F, F.menu_file("2026-W50"), "")`。5. `create_file(F, F.recipe_file("rice"), "servings = 2\n")`。6. `create_file(F, F.root / "notes.toml", "x")`。 | 每次调用给出的结果都等于 `FileCreation(FileOutcome.CREATED)`。每次调用的记录只有它的文件的 `open`，比如 `open recipe-menu/menus/2026-W47.toml`，它的列出记录只有它的文件夹：1 到 4 是 `recipe-menu/menus`，5 是 `recipe-menu/recipes`，6 是 `recipe-menu`。没有记录含有 `read`。各文件的内容是 `b'week = "2026-W47"\n'`、`b"a\r\nb\n"`、`"番茄\n".encode("utf-8")`、`b""`、`b"servings = 2\n"` 和 `b"x"`，没有加入别的条目。 |
| F11-T10 | 单元 | `create_file` | 第 3 步。把两个名称里的 A 到 Z 都换成小写后与文件名相同的条目给出 `EXISTS`，`existing` 是那个条目的完整路径，无论条目是哪一种。调用什么都不打开，所以每个条目都保持原来的字节和修改时间。以别的方式不同的名称不算已经存在，调用会创建文件（3.3 第 3 步，选择 4）。 | `F` 和文字 `"new\n"`，每个输入用自己的 `base`，每次调用都在 `faults(base)` 里运行。路径是 Q，`F.menus` 里有：1. 内容为 `b"old\n"` 的 `2026-W47.toml`。2. 空的 `2026-w47.toml`。3. 空的 `2026-W47.TOML`。4. 空的 `2026-W47.Toml`。5. 空的 `2026-w47.TOML`。6. 空文件夹 `2026-W47.toml`。7. 位于 `2026-W47.toml` 的悬空链接。8. 内容为 `b"[[[\n"` 的 `2026-W47.toml`。然后路径是 `F.recipe_file("rice")`，`F.recipes` 里有：9. 空的 `Rice.toml`。10. 空的 `RICE.TOML`。11. 路径是 Q，`F.menus` 里有空文件 `2026-W47.toml.bak`、`2026-W47`、`2026-W470.toml`、`x2026-W47.toml` 和 `2026-W47.tom`。 | 1 到 10 给出 `EXISTS`，没有问题，`left` 为空，`str(existing)` 等于输入里那个条目的 `str`，比如 2 里的 `str(F.menus / "2026-w47.toml")` 和 9 里的 `str(F.recipes / "Rice.toml")`。记录为空，列出记录只有文件所在的文件夹，调用之后 `base` 的完整记录和调用之前相同。11. `CREATED`。Q 的内容是 `b"new\n"`，另外五个文件保持原来的字节和修改时间。 |
| F11-T11 | 单元 | `create_file` | Linux 上的第 3 步，那里一个文件夹可以有只有大小写不同的名称。几个条目都匹配时，名称和文件名完全相同的那个算数，否则按 `sorted` 的顺序取第一个匹配（3.3 第 3 步）。这个用例只在 Linux 上运行，由 CI 检查，与 F04-T12、F04-T51 和 F06-T28 相同，因为 Windows 的一个文件夹不能有两个这样的名称。 | `F`、路径 Q 和文字 `"new\n"`，每个输入用自己的 `base`，每次调用都在 `faults(base)` 里运行。`F.menus` 里有这些空文件：1. `2026-w47.toml` 和 `2026-W47.TOML`。2. `2026-w47.toml`、`2026-W47.toml` 和 `2026-W47.TOML`。3. `2026-w47.toml`、`2026-W47.Toml` 和 `2026-W47.TOML`。 | 每次调用都给出 `EXISTS`，`str(existing)` 等于 `str(F.menus / N)`，N 是：1. `2026-W47.TOML`。2. `2026-W47.toml`。3. `2026-W47.TOML`。记录为空，每个文件都保持原来的字节和修改时间。 |
| F11-T12 | 单元 | `create_file` | 第 2 步。列出文件所在的文件夹失败时给出 `FAILED`，问题的文件是相对于数据文件夹的那个文件夹，没有位置，消息来自 `list_toml_files` 的列出问题表，调用什么都不创建。不存在的 `menus\` 给出 `menus` 和 `FOLDER_MISSING`，与 `list_menu_weeks` 相同（3.3 第 2 步，F04 设计 3.1）。 | `F`、路径 Q 和文字 `"new\n"`，输入另有说明的除外，每个输入用自己的 `base`，每次调用都在 `faults(base, *rules)` 里运行：1. `F.menus` 不存在。2. `F.menus` 是内容为 `b"x\n"` 的文件。3. `list F.menus: DENIED`。4. `list F.menus: IO`。5. `list F.menus: OSError()`。6. `list F.menus: TimeoutError()`。7. 路径 `F.root / "a" / "b.toml"`，`a` 不存在。8. `F.root` 不存在，路径是 `F.root / "notes.toml"`。 | 每次调用都给出 `FAILED`，`left` 为空，没有 `existing`，问题是：1. `menus: FOLDER_MISSING`。2. `menus: FOLDER_IS_FILE`。3. `menus: FOLDER_ACCESS_DENIED`。4. `menus: FOLDER_SYSTEM_ERROR(reason="Input/output error")`。5. `menus: FOLDER_SYSTEM_ERROR(reason="OSError")`。6. `menus: FOLDER_SYSTEM_ERROR(reason="TimeoutError")`。7. `a: FOLDER_MISSING`。8. `.: FOLDER_MISSING`。记录为空，调用之后 `base` 的树和调用之前相同。 |
| F11-T13 | 单元 | `create_file` | 打开。3.3 错误表里第一个适用的行给出结果。打开时的 `FileExistsError` 给出 `EXISTS`，`existing` 是这个路径，因为列出之后出现了一个条目。`PermissionError` 给出 `FILE_WRITE_DENIED`，其他 `OSError` 给出带错误的 `strerror` 的 `FILE_WRITE_ERROR`，`strerror` 为 `None` 或空时用错误类的名字。失败的打开什么都没创建，所以调用什么都不删除。文件系统在 A 到 Z 之外也不分大小写的名称走到 `FileExistsError` 那一行（3.3 第 4 步和它的错误表）。 | `F` 带一个空的 `F.menus`，路径 Q 和文字 `"new\n"`，输入另有说明的除外，每个输入用自己的 `base`，每次调用都在 `faults(base, *rules)` 里运行：1. `open Q: race`。2. `open Q: DENIED`。3. `open Q: IO`。4. `open Q: TimeoutError()`。5. `open Q: OSError(errno.EIO, "")`。6. 没有规则，路径是 `F.menus / N`，N 是 `"x" * 300 + ".toml"`。7. 没有规则，`F.menus` 里有内容为 `b"x\n"` 的 `\u00c4.toml`（U+00C4 LATIN CAPITAL LETTER A WITH DIAERESIS），路径是 `F.menus / "\u00e4.toml"`（U+00E4，它的小写字母）。 | 1. `EXISTS`，`str(existing)` 等于 `str(Q)`，Q 的内容是别的程序写的 `b"mine\n"`。2 到 6 给出 `FAILED`，`left` 为空，问题是：2. `menus/2026-W47.toml: FILE_WRITE_DENIED`。3. `menus/2026-W47.toml: FILE_WRITE_ERROR(reason="Input/output error")`。4. 同样，但 `reason="TimeoutError"`。5. 同样，但 `reason="OSError"`。6. `menus/N` 和系统对 `open(F.menus / N, "x")` 给出的消息，在两个系统上都是 `FILE_WRITE_ERROR`。在 1 到 6 里，记录只有这个路径的 `open`，没有 `unlink`，`F.menus` 里没有别的新条目。7. 在 Windows 上：`EXISTS`，`str(existing)` 等于 `str(F.menus / "\u00e4.toml")`，记录是那个路径的 `open`，`F.menus` 里只有内容为 `b"x\n"` 的 `\u00c4.toml`。在 Linux 上：`CREATED`，`F.menus` 里有两个文件。 |
| F11-T14 | 单元 | `create_file` | 打开之后。文件从打开成功的那一刻起就算已创建。写入失败时给出 `FAILED`，调用先删除写了一半的文件。删除失败时，文件的完整路径进入 `left`。打开之后的其他异常，比如程序缺陷或 Ctrl+C，执行同样的删除然后继续抛出，没有结果。调用用一次 `write` 写入文字，文字为空时也一样（3.3 第 4 步和它的错误表后面的那一段）。 | `F` 带一个空的 `F.menus`，路径 Q 和文字 T，T 是 `"0123456789\n"`，输入另有说明的除外。每个输入用自己的 `base`，每次调用 `create_file(F, Q, T)` 都在 `faults(base, *rules)` 里运行：1. `write Q: NO_SPACE`。2. `write Q: DENIED`。3. `write Q: IO` 和 `unlink Q: DENIED`。4. `write Q: NO_SPACE`，文字是 `""`。5. `write Q: BUG`，在 `pytest.raises(RuntimeError)` 里。6. `write Q: CTRL_C`，在 `pytest.raises(KeyboardInterrupt)` 里。7. `write Q: CTRL_C` 和 `unlink Q: DENIED`，在 `pytest.raises(KeyboardInterrupt)` 里。8. `write Q: CTRL_C` 和 `unlink Q: CTRL_C`，在 `pytest.raises(KeyboardInterrupt)` 里。9. `open Q: after CTRL_C`，在 `pytest.raises(KeyboardInterrupt)` 里。 | 1. `FAILED`，带 `menus/2026-W47.toml: FILE_WRITE_ERROR(reason="No space left on device")`，`left` 为空。2. `FAILED`，带 `menus/2026-W47.toml: FILE_WRITE_DENIED`，`left` 为空。3. `FAILED`，带 `menus/2026-W47.toml: FILE_WRITE_ERROR(reason="Input/output error")`，`left` 是 `(Q,)`。4. 1 的结果。5 到 8. 调用抛出它的 `write` 规则的异常。在 1、2 和 4 到 6 里，记录是 Q 的 `open`，然后是 Q 的 `unlink`，之后 Q 不存在。在 3、7 和 8 里，记录相同，Q 的内容是 `b"01234"`，即故障工具写入的 T 的一半。9. 记录只有 Q 的 `open`，没有 `unlink`，Q 是一个空文件：系统创建了它，但调用从没拿到它，与设计选择 4 对 `open` 内部的 Ctrl+C 的说法相同。在 Windows 上，只有调用关闭了 Q 之后才能删除它，所以 1、2 和 4 到 6 也检查调用关闭了文件。 |
| F11-T15 | 功能 | `recipe-menu menu new`、`main` | 按顺序运行 2.2 的示例，用真正的命令：原型“Create next week's menu”的两段输出和它的文件，保留文件的拒绝，设置里的三餐，名称只有大小写不同的文件，错误的周，以及用完整路径写出的不存在的 `menus\`（2.2，选择 2 到 5，C 点）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`，示例的 `run` 调用 `main` 时不传 `commands`。 | 示例的每条断言都成立。 |
| F11-T16 | 功能 | `recipe-menu menu new`、`recipe-menu check`、`recipe-menu menu show` | 在 `main` 上运行 v0.1-S13，并完整运行 F11 原型“Create next week's menu”和“Show the week after you fill it”。新文件和原型的文件逐字节相同。拒绝保留文件的字节和修改时间。Troy 填好文件之后，`check` 报告没有错误，两张表格都和原型相同（选择 3 到 5、8 和 9）。 | X 是一份菜单为空的示例副本。1. 在 X 里 `menu new 2026-W47`。2. 在 X 里 `menu new 2026-W47 --lang zh`。3. 像 Troy 填写的那样，用 `EXAMPLE / "menus" / "2026-W47.toml"` 的文字写出 X 的 `menus/2026-W47.toml`。4. 在 X 里 `check`。5. 在 X 里 `menu show 2026-W47`。6. 在 X 里 `menu show 2026-W47 --lang zh`。7. 在第二份菜单为空的示例副本 Y 里：`menu new next`，然后 `menu new next --lang zh`。 | 1. `(0, out NEW(X/menus/2026-W47.toml, 16 to 22 November 2026, lunch and dinner))`，即原型“Create next week's menu”的第一段输出。文件内容是 `PROTOTYPE_FILE`，逐字节相同：UTF-8，没有字节顺序标记，LF 换行，只有 ASCII 字符。2. `(1, err [EXISTS_ZH(X/menus/2026-W47.toml)])`，即那一节的第二段输出，文件保持原来的字节和 `st_mtime_ns`。4. `(0, out AFTER)`，即 F07 原型“After the fixes”的输出。5. `(0, out SHOW_47)`。6. `(0, out SHOW_47_ZH)`。7. 把 X 换成 Y 后 1 和 2 的结果，Y 的文件内容是 `PROTOTYPE_FILE`。 |
| F11-T17 | 功能 | `recipe-menu menu new` | 选择 3 和 5。文件有 2.2 的各行：带这一周和它的英文 `date_range` 的第一行注释，两行讲菜的注释，`week`，以及从周一到周日每天一张表，表里为设置的每一餐写一个空列表，按 `Meal` 的顺序，无论设置按什么顺序列出它们。输出写出文件的完整路径、这一周在输出语言里的 `date_range`，以及各餐标签的 `and_list`。一个月之内、跨两个月和跨两年的周都可以，跨年的第 1 周也可以（2.2，选择 3 和 5）。 | 1. 对七组餐次中的每一组 S，一份菜单为空的示例副本，`settings.toml` 用下面的一行写出：`meals = ["breakfast"]`、`meals = ["lunch"]`、`meals = ["dinner"]`、`meals = ["lunch", "breakfast"]`、`meals = ["dinner", "breakfast"]`、`meals = ["dinner", "lunch"]` 和 `meals = ["dinner", "lunch", "breakfast"]`。在每份副本里：`menu new 2026-W47`，然后 `menu new 2026-W48 --lang zh`。2. 在一份菜单为空的示例副本 A 里：对 `2026-W49`、`2026-W53`、`2026-W01`、`2027-W01`、`2026-W23` 和 `2020-W53` 中的每个 W，`menu new W`。在一份菜单为空的示例副本 B 里：对同样的周，`menu new W --lang zh`。3. `menu_text(2026-W47, [lunch, dinner])`。 | 1. 对每一组的文件夹 F：`(0, out NEW(F/menus/2026-W47.toml, 16 to 22 November 2026, M))` 和 `(0, out NEW_ZH(F/menus/2026-W48.toml, 2026年11月23日至29日, M_ZH))`。按七组的顺序，M 和 M_ZH 是：`breakfast` 和 `早餐`，`lunch` 和 `午餐`，`dinner` 和 `晚餐`，`breakfast and lunch` 和 `早餐和午餐`，`breakfast and dinner` 和 `早餐和晚餐`，`lunch and dinner` 和 `午餐和晚餐`，以及 `breakfast, lunch, and dinner` 和 `早餐、午餐和晚餐`。所以只有晚餐的那一组给出 `7 days with dinner, all empty.`。每个文件的内容是它那一周和按 `Meal` 顺序排列的 S 的 `menu_text`，所以最后一组的每一天依次是 `breakfast = []`、`lunch = []` 和 `dinner = []`。2. 每一行给出退出码 0，A 里是它的文件和 `lunch and dinner` 的 `NEW`，B 里是它的文件和 `午餐和晚餐` 的 `NEW_ZH`。按六个周的顺序，英文和中文的日期是：`30 November to 6 December 2026` 和 `2026年11月30日至12月6日`，`28 December 2026 to 3 January 2027` 和 `2026年12月28日至2027年1月3日`，`29 December 2025 to 4 January 2026` 和 `2025年12月29日至2026年1月4日`，`4 to 10 January 2027` 和 `2027年1月4日至10日`，`1 to 7 June 2026` 和 `2026年6月1日至7日`，以及 `28 December 2020 to 3 January 2021` 和 `2020年12月28日至2021年1月3日`。A 和 B 里每个文件的内容都是 `menu_text(W, [lunch, dinner])`，所以它的第一行是 `# W: ` 加上英文日期，比如 `# 2026-W53: 28 December 2026 to 3 January 2027`。3. 它等于 `PROTOTYPE_FILE`，所以测试的构造函数和原型一致。 |
| F11-T18 | 功能 | `recipe-menu menu new` | B 点和选择 3。`--lang zh` 和 `language = "zh"` 改变输出的各行，不改变文件，文件在两种语言里都有同样的英文注释和同样的字节。新菜单的中文各行是 A 点的新文字（选择 3 和 5，A 点和 B 点）。 | 1. 一份菜单为空的示例副本 X：`menu new 2026-W47 --lang zh`。2. 一份带中文设置、菜单为空的示例副本 Y：`menu new 2026-W47`，然后 `menu new 2026-W48 --lang en`，然后 `menu new 2026-W47 --lang en`，然后 `menu new 2026-W48`。 | 1. `(0, out NEW_ZH(X/menus/2026-W47.toml, 2026年11月16日至22日, 午餐和晚餐))`，文件内容是 `PROTOTYPE_FILE`。2. `(0, out NEW_ZH(Y/menus/2026-W47.toml, 2026年11月16日至22日, 午餐和晚餐))`，文件内容是 `PROTOTYPE_FILE`。然后 `(0, out NEW(Y/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`，文件内容是 `menu_text(2026-W48, [lunch, dinner])`。然后 `(1, err [EXISTS(Y/menus/2026-W47.toml)])` 和 `(1, err [EXISTS_ZH(Y/menus/2026-W48.toml)])`。 |
| F11-T19 | 功能 | `recipe-menu menu new`、`read_week_menu`、`recipe-menu check`、`recipe-menu menu show` | 选择 3。`read_week_menu` 用创建它的设置、默认设置和不带设置读新文件，都没有问题，每个格子都为空。所以 `check` 对它什么都不报告，`menu show` 对每一餐显示 `\u2014`，并以 `NO_DISHES` 结尾（选择 3 和 9，v0.1-S14）。 | 1. 对 F11-T17 的每一组 S，它的文件夹 F 在 F11-T17 输入 1 的两行之后。对 `Settings(Lang.EN, S, 2)`（S 写成按 `Meal` 顺序排列的元组）、`Settings()` 和 `None` 中的每个 s，`read_week_menu(F, IsoWeek(2026, 47), s, frozenset(list_recipe_ids(F)[0]))`。然后在 F 里 `check`、`menu show 2026-W47` 和 `menu show 2026-W48 --lang zh`。2. 在 `example` 里：`menu new 2026-W48`，然后 `check` 和 `check --lang zh`。 | 1. 用 `Settings(Lang.EN, S, 2)` 和 `Settings()` 时，结果是一个菜单，它的 `meals` 就是设置的餐次，7 天里每天为每一餐都有一个空格子，没有问题。用 `None` 时，结果是 `(None, ())`。`check` 给出 `(0, out AFTER)`。`menu show 2026-W47` 给出 `(0, out EMPTY(2026-W47, EN, S))`，`menu show 2026-W48 --lang zh` 给出 `(0, out EMPTY(2026-W48, ZH, S))`。2. `(0, out NEW(example/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`。然后是把 `1 week menu` 换成 `2 week menus` 的 `(0, out AFTER)`，以及把 `1 个周菜单` 换成 `2 个周菜单` 的 `(0, out AFTER_ZH)`。 |
| F11-T20 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 选择 2，以及在 `main` 上运行 v0.1-S14。两个命令都从 `context.today` 得到它们的周：不写值和 `this` 给出今天所在的周，`next` 给出 7 天后的日期所在的周，跨年也一样。每一行都用 `str(week)` 写出这一周，从不写成 `this` 或 `next`（选择 2）。 | 对下面每个日期 D 及其周 T 和 N，一份菜单为空的示例副本 F，在 F 里、在 D 这天运行每一行：1. `menu new`。2. `menu new next`。3. `menu new this --lang zh`。4. `menu new N`。5. `menu show this`。6. `menu show`。7. `menu show next --lang zh`。8. `menu show T`。日期及其 T 和 N 是：2026-11-10，星期二，`2026-W46` 和 `2026-W47`。2026-11-22，星期日，`2026-W47` 和 `2026-W48`。2026-12-27，星期日，`2026-W52` 和 `2026-W53`。2026-12-30，星期三，`2026-W53` 和 `2027-W01`。2027-01-03，星期日，`2026-W53` 和 `2027-W01`。2025-12-29，星期一，`2026-W01` 和 `2026-W02`。 | 1. `(0, out NEW(F/menus/T.toml, T 的日期, lunch and dinner))`，文件内容是 `menu_text(T, [lunch, dinner])`。2. 对 N 同样。3. `(1, err [EXISTS_ZH(F/menus/T.toml)])`。4. `(1, err [EXISTS(F/menus/N.toml)])`。5 和 6. `(0, out EMPTY(T, EN, [lunch, dinner]))`。7. `(0, out EMPTY(N, ZH, [lunch, dinner]))`。8. 5 的结果。之后，F 的 `menus/` 里正好是 `T.toml` 和 `N.toml`。各周的日期就是 F11-T17 里的那些，加上 `2026-W46`、`2026-W47`、`2026-W48`、`2026-W52` 和 `2026-W02` 的 `9 to 15 November 2026`、`16 to 22 November 2026`、`23 to 29 November 2026`、`21 to 27 December 2026` 和 `5 to 11 January 2026`。在 2026-12-30 这天，第 1、2 和 5 行就是 v0.1-S14 的第 1 到 3 步：文件 `2026-W53.toml` 和 `2027-W01.toml` 各有自己的 `week` 行，`menu show 2026-W53` 的输出就是 F 块里的那一段，每一步的退出码都是 0。 |
| F11-T21 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 选择 2。不是周的 `WEEK` 值只在错误流上给出 `NOT_A_WEEK`，退出码 2，没有提示，用输出的语言。命令在碰任何文件之前抛出它，所以有错误的文件夹、不存在的 `menus\`，或者名称像这一周的文件，都给出同样的结果（2.2 和 2.4 的错误，选择 2）。 | 1. 在 `example` 里，每一行都在一个新的 `faults(example.root)` 里运行：对 `"2026-W99"`、`"Next"`、`""`、`"2026-w47"`、`"2025-W53"` 和 `" this"` 中的每个 V，`menu new V` 和 `menu show V`。2. 在 `example` 里：`menu new 2026-W99 --lang zh` 和 `menu show Next --lang zh`。3. 各在一份新的示例副本里：没有菜单文件夹时 `menu new 2026-W99`，目录花括号错误时 `menu show 2026-W99`，菜单错字时 `menu show ""`。4. 一份带中文设置的新示例副本：`menu show 2026-W99`，然后 `menu show 2026-W99 --lang en`。 | 1. 每一行给出 `(2, err [NOT_A_WEEK(V)])`。记录只有 `read settings.toml`，没有列出，这些行之后示例的完整记录和之前相同。2. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(2, err [NOT_A_WEEK_ZH("Next")])`。3. 每一行给出它的 V 的 `(2, err [NOT_A_WEEK(V)])`，第一行之后 `menus/` 仍然不存在。4. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(2, err [NOT_A_WEEK("2026-W99")])`。 |
| F11-T22 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`recipe-menu check` | 选择 4：拒绝。名称和文件名相同，或者只在 A 到 Z 的大小写上不同的条目，给出带已经存在的那个条目的完整路径的 `ALREADY_EXISTS`，退出码 1，错误流上一行，输出流上什么都没有，两个系统上都一样。每个条目都保持原来的字节和修改时间，有错误的文件和空文件也一样。然后 `menu show` 和 `check` 报告这样的条目（选择 4，2.2）。 | 1. 在 `example` 里：`menu new 2026-W47`，然后 `menu new next --lang zh`。2 到 8 各在一份菜单为空的示例副本 X 里，它的 `menus/` 里有：2. 内容为 `b"[[[\n"` 的 `2026-W47.toml`。3. 空的 `2026-W47.toml`。4. 空的 `2026-w47.toml`。5. 空的 `2026-W47.TOML`。6. 空的 `2026-W47.Toml`。7. 空文件夹 `2026-W47.toml`。8. 位于 `2026-W47.toml` 的悬空链接。在每份副本里：`menu new 2026-W47`，然后 `menu new 2026-W47 --lang zh`。在 3 到 5 和 7 里，然后还有 `menu show 2026-W47` 和 `check`。9. 一份菜单为空的示例副本 X，在 `faults(X.root, open X/menus/2026-W47.toml: race)` 里 `menu new 2026-W47`。 | 1. `(1, err [EXISTS(example/menus/2026-W47.toml)])` 和 `(1, err [EXISTS_ZH(example/menus/2026-W47.toml)])`。2 到 8. `(1, err [EXISTS(E)])` 和 `(1, err [EXISTS_ZH(E)])`，E 是 `X/menus/` 加上输入里那个条目的名称：4 里是 `2026-w47.toml`，5 里是 `2026-W47.TOML`，6 里是 `2026-W47.Toml`，其他的是 `2026-W47.toml`，两个系统上都一样。然后 `menu show 2026-W47` 给出 `(1, err STOP(W, M))`，W 和 M 是：3. `menus/2026-W47.toml` 和 `MISSING_KEY(key="week")`。4. `menus/2026-w47.toml` 和 `NOT_A_WEEK_NAME`。5. `menus/2026-W47.TOML` 和 `TOML_ENDING_NOT_SMALL`。7. `menus/2026-W47.toml` 和 `FILE_IS_FOLDER`。每个这样的错误都在 `check` 的错误之中。在 1 到 8 里，这些行之后数据文件夹的完整记录和之前相同。9. `(1, err [EXISTS(X/menus/2026-W47.toml)])`，因为这个条目在列出之后出现。记录是 `read settings.toml` 和 `open menus/2026-W47.toml`，没有 `unlink`，文件的内容是别的程序写的 `b"mine\n"`。 |
| F11-T23 | 功能 | `recipe-menu menu new`、`main` | 选择 4 和 C 点。失败是错误流上的三行，退出码 1：文件或文件夹的完整路径 `str(context.folder.root / problem.file)`，然后是两个空格加上问题的文字，然后是 `CHANGED_NOTHING`，或者在写了一半的文件留下时，是带这一周的 `LEFT_BEHIND`。列出失败时用完整路径写出文件夹 `menus\`，与 ADR-0010 相同。输出流上什么都没有（2.2，选择 4）。 | R 是每个输入的数据文件夹，一份新的示例副本，P 是 `R / "menus" / "2026-W48.toml"`。3 到 10 的各行在 `faults(R, *rules)` 里运行。1. 没有菜单文件夹：`menu new 2026-W48`，然后 `menu new 2026-W48 --lang zh`。2. 菜单文件夹是文件：同样两行。3. `list R/menus: DENIED`：同样两行。4. `list R/menus: IO`：`menu new 2026-W48`。5. `open P: DENIED`：`menu new 2026-W48`，然后 `menu new 2026-W48 --lang zh`。6. `open P: IO`：`menu new 2026-W48`。7. `write P: NO_SPACE`：`menu new 2026-W48`。8. `write P: NO_SPACE` 和 `unlink P: DENIED`：`menu new 2026-W48`。然后不带规则 `menu new 2026-W48`，再删掉 P，然后 `menu new 2026-W48`。9. 和 8 一样，但那一行是 `menu new 2026-W48 --lang zh`，后面没有别的行。10. R 是一份菜单为空的示例副本，带 `write R/menus/2026-W47.toml: NO_SPACE` 和 `unlink R/menus/2026-W47.toml: DENIED`：`menu new next`。 | 1. `(1, err FAIL(R/menus, FOLDER_MISSING))`，即设计 2.2 示例的最后一次运行，以及 `(1, err FAIL_ZH(R/menus, FOLDER_MISSING))`。`R / "menus"` 仍然不存在。2. 同样，但是 `FOLDER_IS_FILE`，那个文件保持原来的字节。3. 同样，但是 `FOLDER_ACCESS_DENIED`。4. `(1, err FAIL(R/menus, FOLDER_SYSTEM_ERROR(reason="Input/output error")))`。5. `(1, err FAIL(P, FILE_WRITE_DENIED))`，即设计 2.2 里失败示例的各行，以及 `(1, err FAIL_ZH(P, FILE_WRITE_DENIED))`。6. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="Input/output error")))`。7. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="No space left on device")))`。记录是 `read settings.toml`、`open menus/2026-W48.toml` 和 `unlink menus/2026-W48.toml`，P 不存在。8. `(1, err LEFT(P, FILE_WRITE_ERROR(reason="No space left on device"), 2026-W48))`，P 的内容是故障工具写入的 `menu_text(2026-W48, [lunch, dinner])` 的前一半。然后 `(1, err [EXISTS(P)])`，删掉之后 `(0, out NEW(P, 23 to 29 November 2026, lunch and dinner))`。9. `(1, err LEFT_ZH(P, FILE_WRITE_ERROR(reason="No space left on device"), 2026-W48))`。10. `(1, err LEFT(R/menus/2026-W47.toml, FILE_WRITE_ERROR(reason="No space left on device"), 2026-W47))`：这一行写的是 `2026-W47`，不是 `next`。在 1 到 7 里，这些行之后 R 的树和之前相同。 |
| F11-T24 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`recipe-menu check`、`main` | `menu new` 期间按 Ctrl+C。`cli` 以 130 退出，什么都不写，`create_file` 已经删掉了写了一半的文件。在 `open` 内部、系统创建了文件之后按 Ctrl+C，空文件会留下：`menu new` 拒绝它，`menu show` 和 `check` 报告它缺少 `week`（2.2 的错误，选择 4，F05 设计 2.10）。 | R 和 P 与 F11-T23 相同，每个输入在 R 处的一份新示例副本里。每个输入的第一行在 `faults(R, *rules)` 里、通过 `tests/f08_support.py` 的 `call_main` 运行。1. `write P: CTRL_C`：`menu new 2026-W48`。2. `open P: after CTRL_C`：`menu new 2026-W48`。然后不带规则：`menu new 2026-W48`、`menu show 2026-W48` 和 `check`。3. `write P: CTRL_C` 和 `unlink P: DENIED`：`menu new 2026-W48 --lang zh`。然后不带规则 `menu new 2026-W48 --lang zh`。 | 每个输入的第一行给出 `(130, "", "")`。1. 记录是 `read settings.toml`、`open menus/2026-W48.toml` 和 `unlink menus/2026-W48.toml`，P 不存在。2. 记录是 `read settings.toml` 和 `open menus/2026-W48.toml`，P 是一个空文件。然后 `(1, err [EXISTS(P)])`，然后 `(1, err STOP(menus/2026-W48.toml, MISSING_KEY(key="week")))`，这个错误在 `check` 的错误之中。3. P 的内容是 `menu_text(2026-W48, [lunch, dinner])` 的前一半。然后 `(1, err [EXISTS_ZH(P)])`。 |
| F11-T25 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 选择 4。`menu new` 不读任何数据文件，只有 `cli` 读取设置。损坏的目录、菜谱、常备清单或其他菜单，或者 `menus\` 里不是周的名称，都不会让它停下。它不读它那一周的文件，所以有错误的文件得到拒绝（选择 4）。 | B 是一份新的示例副本，带目录花括号错误、麻婆错误和菜单错字，`pantry.toml` 和 `menus/2026-W48.toml` 写成 `[[[\n`，`menus/plan.toml` 和 `menus/2026-w49.toml` 写成空文件。1. 在 B 里、在 `faults(B)` 里 `menu new 2026-W50`。2. 在 B 里 `menu new 2026-W47 --lang zh`、`menu new 2026-W48` 和 `menu new 2026-W49`。3. 在 B 里 `menu show 2026-W50`。 | 1. `(0, out NEW(B/menus/2026-W50.toml, 7 to 13 December 2026, lunch and dinner))`，文件内容是 `menu_text(2026-W50, [lunch, dinner])`。记录是 `read settings.toml` 和 `open menus/2026-W50.toml`，列出记录只有 `menus`。2. `(1, err [EXISTS_ZH(B/menus/2026-W47.toml)])`、`(1, err [EXISTS(B/menus/2026-W48.toml)])` 和 `(1, err [EXISTS(B/menus/2026-w49.toml)])`。3. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`：`menu show` 先读目录，而 `menu new` 没有读它。 |
| F11-T26 | 功能 | `recipe-menu menu show`、`main` | 按顺序运行 2.4 的示例，用真正的命令：原型“Show the week after you fill it”的中文输出，两种语言的“A week without a menu”，菜单没有写到的菜谱里的错误，缺少的英文名称，菜单写到的菜谱里的错误，“A menu with a mistake”，新菜单，以及不存在的 `menus\`（2.4，选择 6 到 9）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`，示例的 `run` 调用 `main` 时不传 `commands`。 | 示例的每条断言都成立。 |
| F11-T27 | 功能 | `recipe-menu menu show`、`recipe-menu menu new`、`main` | 每个命令读取的文件（选择 4 和 7，2.4 的副作用）。`menu show` 读目录一次，列出 `recipes/` 一次、`menus/` 一次，读这一周的文件一次，并按第一道写到它的菜的顺序，把菜写到的每个菜谱读一次：周一到周日，各餐按设置的顺序，各道菜按文件里的顺序。它不读菜单没有写到的菜谱，不读别的菜单，也不读常备清单。遇到错误或没有菜单的周之后，它什么都不再读；遇到错误的周之后，它不读任何文件。`menu new` 不读任何文件，列出 `menus/` 一次。 | 1 到 6 的每一行都在一个新的 `faults(F.root)` 里运行，F 是这一行的文件夹。1. 在 `example` 里：`menu show 2026-W47`，然后 `menu show 2026-W47 --lang zh`。2. 在一份写入周 B 的新示例副本里：`menu show 2026-W48`。3. 在 `example` 里：`menu show 2026-W48`。4. 在 `example` 里：`menu show 2026-W99`，然后 `menu show 2026-W47 --help`。5. 各在一份新的示例副本里，运行 `menu show 2026-W47`：目录花括号错误，Rice Bowl，写成空文件的 `menus/2026-w48.toml`，菜单错字，以及麻婆错误。6. 在 `example` 里：`menu new 2026-W48`，然后 `menu new 2026-W47`，然后 `menu new 2026-W99`。7. 不用故障工具，在 `example` 里：`menu show 2026-W47`。 | 记录、列出记录和结果。R47 是 `read settings.toml`、`read catalog.toml`、`read menus/2026-W47.toml`，然后按 `tomato-egg`、`choy-sum`、`rice`、`mapo-tofu`、`tomato-egg-noodles` 和 `cola-wings` 的顺序，每个 ID 一行 `read recipes/ID.toml`。1. R47，列出记录先是 `recipes` 再是 `menus`，以及 `(0, out SHOW_47)`；然后是同样的记录和列出记录，以及 `(0, out SHOW_47_ZH)`。虽然有 2 道和 3 道菜写到 `choy-sum` 和 `rice`，它们都只读一次，`recipes/red-braised-pork.toml` 和 `pantry.toml` 都没有被读。2. `read settings.toml`、`read catalog.toml`、`read menus/2026-W48.toml`，然后依次是菜谱 `mapo-tofu`、`rice`、`choy-sum` 和 `red-braised-pork`，同样的列出记录，以及 A 块的第一段输出。文件把周一的晚餐写在午餐之前，而读取按设置的顺序。`menus/2026-W47.toml` 没有被读。3. `read settings.toml` 和 `read catalog.toml`，同样的列出记录，以及 `(1, err [NO_MENU(2026-W48)])`。4. 只有 `read settings.toml`，没有列出，以及 `(2, err [NOT_A_WEEK("2026-W99")])`。然后是同样的记录，退出码 0，err 为空，out 上是和不指定文件夹的 `--help` 相同的文字。5. 依次是：`read settings.toml` 和 `read catalog.toml`，没有列出；同样两次读取，列出记录只有 `recipes`；同样两次读取，两个列出都有；这两次读取加 `read menus/2026-W47.toml`，两个列出都有；R47 直到 `read recipes/mapo-tofu.toml`，两个列出都有。每个结果都是 F11-T28 里它那个文件夹的结果。6. `read settings.toml` 和 `open menus/2026-W48.toml`，列出记录只有 `menus`，以及 `(0, out NEW(example/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`。然后是 `read settings.toml`，列出记录 `menus`，以及 `(1, err [EXISTS(example/menus/2026-W47.toml)])`。然后是 `read settings.toml`，没有列出，以及 `(2, err [NOT_A_WEEK("2026-W99")])`。7. `(0, out SHOW_47)`。 |
| F11-T28 | 功能 | `recipe-menu menu show`、`recipe-menu check` | 选择 7。每个读取函数的第一个错误让 `menu show` 停下，用输出的语言写出 `stop_at_error` 的三行，退出码 1，输出流上什么都没有。先是目录，然后是 `recipes/` 的列出，然后是 `menus/` 的列出（问题是别的文件时也一样），然后是这一周的文件，最后是按第一道菜的顺序排列的菜谱。菜单没有写到的菜谱里的错误不改变任何东西，常备清单和别的菜单也一样。让 `menu show` 停下的错误在 `check` 的错误之中（2.4 第 2 到 7 步，选择 7）。 | 1 到 21 的每个输入各在一份新的示例副本里，运行 `menu show 2026-W47`、`menu show 2026-W47 --lang zh`、`check` 和 `check --lang zh`：1. 没有目录。2. 目录花括号错误。3. 没有菜谱文件夹。4. 菜谱是文件。5. Rice Bowl。6. 大写的 rice。7. 没有菜单文件夹。8. 菜单文件夹是文件。9. 写成空文件的 `menus/2026-w48.toml`。10. 写成空文件的 `menus/plan.toml`。11. 写成空文件的 `menus/2026-W48.TOML`。12. 菜单错字。13. v0.1-S07 的菜单错误。14. 麻婆错误。15. 米饭 0 份。16. 麻婆错误和米饭 0 份。17. 目录花括号错误和菜单错字。18. Rice Bowl 和写成空文件的 `menus/2026-w48.toml`。19. 写成空文件的 `menus/2026-w48.toml` 和菜单错字。20. 菜单错字和麻婆错误。21. 文件夹 x，并在周三的晚餐里加上 `"x"`：把 `menus/2026-W47.toml` 里的 `[wednesday]\nlunch = []\ndinner = []` 换成 `[wednesday]\nlunch = []\ndinner = ["x"]`。然后各在一份新的示例副本里，只运行 `menu show 2026-W47`：22. 文件夹 x。23. 把米饭 0 份用在 `red-braised-pork` 上而不是 `rice` 上：把 `recipes/red-braised-pork.toml` 里的 `servings = 2` 换成 `servings = 0`。24. `pantry.toml` 和 `menus/2026-W48.toml` 写成 `[[[\n`。25. 写成空文件的 `menus/2026-w48.toml`，运行 `menu show 2026-W48` 而不是 `menu show 2026-W47`。 | 1 到 21. `menu show 2026-W47` 给出 `(1, err STOP(W, M))`，`menu show 2026-W47 --lang zh` 给出 `(1, err STOP_ZH(W, M))`，W 和 M 是：1. `catalog.toml` 和 `FILE_MISSING`。2. `catalog.toml, line 11` 和 `MISSING_BRACE`。3. `recipes` 和 `FOLDER_MISSING`。4. `recipes` 和 `FOLDER_IS_FILE`。5. `recipes/Rice Bowl.toml` 和列出时的 `NOT_A_RECIPE_ID`。6. `recipes/rice.TOML` 和 `TOML_ENDING_NOT_SMALL`。7. `menus` 和 `FOLDER_MISSING`。8. `menus` 和 `FOLDER_IS_FILE`。9. `menus/2026-w48.toml` 和 `NOT_A_WEEK_NAME`。10. `menus/plan.toml` 和 `NOT_A_WEEK_NAME`。11. `menus/2026-W48.TOML` 和 `TOML_ENDING_NOT_SMALL`。12. `menus/2026-W47.toml, Monday dinner` 和 `UNKNOWN_RECIPE(recipe="tomato-eggs")`，即原型“A menu with a mistake”的各行。13. `menus/2026-W47.toml, week` 和 `WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`。14. `recipes/mapo-tofu.toml, ingredient 3` 和菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`。15. `recipes/rice.toml, servings` 和 `SERVINGS_TOO_FEW(servings=0)`。16. 15 的 W 和 M，因为周一的晚餐写到 `rice`，在周二的晚餐写到 `mapo-tofu` 之前，虽然按 ID 的顺序 `mapo-tofu` 在前。17. 2 的 W 和 M。18. 5 的 W 和 M。19. 9 的 W 和 M。20. 12 的 W 和 M。21. `recipes/x.toml` 和 `FILE_IS_FOLDER`。在每个输入里，这个错误在两种语言的 `check` 的错误之中。22 到 24. `(0, out SHOW_47)`，因为没有菜写到 `x` 或 `red-braised-pork`，常备清单和 `2026-W48` 都没有被读。25. `(1, err STOP(menus/2026-w48.toml, NOT_A_WEEK_NAME))`，两个系统上都一样：列出在 `menu show` 查找这一周之前就让它停下。 |
| F11-T29 | 功能 | `recipe-menu menu show`、`main` | 选择 6，以及在 `main` 上运行 v0.1-S15。列出里没有的周给出带 `str(week)` 的 `NO_MENU`，错误流上一行，退出码 1，输出流上什么都没有。不是菜单文件的条目不算数。目录和两个列出在它之前（2.4 第 5 步，选择 6）。 | 1. 在 `example` 里运行 v0.1-S15：`menu show 2026-W48`，`menu show 2026-W99`，然后是菜单错字和 `menu show 2026-W47`。然后带 `--lang zh` 运行同样三行。2. 在 `example` 里：`menu show`，然后 `menu show this --lang zh`，然后在 2026-11-17 这天 `menu show next`。3. 一份新的示例副本，它的 `menus/` 里还有内容为 `2026-W47.toml` 的字节的 `2026-W48.toml.bak`、空文件夹 `2026-W48` 和 `notes.txt`：`menu show 2026-W48`。4. 一份菜单为空的示例副本：`menu show 2026-W47`。5. 各在一份新的示例副本里，运行 `menu show 2026-W48`：目录花括号错误、没有菜谱文件夹和 Rice Bowl。 | 1. `(1, err [NO_MENU(2026-W48)])`、`(2, err [NOT_A_WEEK("2026-W99")])` 和 `(1, err STOP(menus/2026-W47.toml, Monday dinner, UNKNOWN_RECIPE(recipe="tomato-eggs")))`：v0.1-S15 的第 1、2 和 4 步，即原型“A week without a menu”和“A menu with a mistake”的输出。然后 `(1, err [NO_MENU_ZH(2026-W48)])`、`(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(1, err STOP_ZH(menus/2026-W47.toml，周一晚餐, UNKNOWN_RECIPE(recipe="tomato-eggs")))`。2. `(1, err [NO_MENU(2026-W46)])`、`(1, err [NO_MENU_ZH(2026-W46)])` 和 `(1, err [NO_MENU(2026-W48)])`。3. `(1, err [NO_MENU(2026-W48)])`。4. `(1, err [NO_MENU(2026-W47)])`。5. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`、`(1, err STOP(recipes, FOLDER_MISSING))` 和 `(1, err STOP(recipes/Rice Bowl.toml, 列出时的 NOT_A_RECIPE_ID))`。 |
| F11-T30 | 功能 | `recipe-menu menu show` | 有菜的周的选择 8 和 9。表格从周一到周日每天一行，用 `short_date`，设置的每一餐一列，带它的标题。格子里每道菜一行，即 `<名称> \u00d7<份数>`，按文件里的顺序，空的一餐写 `\u2014`。一餐里同一道菜写两次给出两行，两行都算数。带换行的名称占两行，缺少输出语言的名称显示另一种语言。每一列都和它在这一周表格里最宽的一行一样宽，标题也算在内，不传 `min_widths`，最后一列不补空格。计数行数出有菜的餐和所有的菜，用英文的复数形式。不写出警告（2.4 的输出，选择 7 到 9）。 | 1. 在 `example` 里：`menu show 2026-W47`，然后 `menu show 2026-W47 --lang zh`。2. 在一份写入周 B 的新示例副本里：A 块的两行。3. 在一份带额外菜谱、`settings.toml` 写成 `meals = ["breakfast"]`、写入周 C 的新示例副本里：B 块的两行。4. 对 `\n`、`\r\n` 和 `\u2028` 中的每个 S，在一份带 S 的长名称、写入周 D 的新示例副本里：C 块的两行。 | 1. `(0, out SHOW_47)` 和 `(0, out SHOW_47_ZH)`。日期列在英文里宽 10 列，中文里宽 13 列，午餐列宽 25 列和 13 列，来自 `Tomato and egg noodles \u00d72` 和 `番茄鸡蛋面 \u00d72`（v0.1-S25）。2 到 4. 每一行给出它在 A、B 或 C 块里那一行的输出，退出码 0，err 为空，每个 S 都相同。在 A 块里，午餐列在英文里宽 23 列，来自 `Stir-fried choy sum \u00d710`，在中文里宽 12 列，来自 `清炒菜心 \u00d710`。周一的晚餐显示两次 `Steamed rice \u00d72`，计数行数出 4 餐 5 道菜。`red-braised-pork` 的警告没有写出。在 B 块里，早餐那一列是最后一列，`Boiled egg` 和 `蒸蛋` 在两张表格里都显示，周二的格子占两行。在 C 块里，`a-long` 的名称占两行，`\u00d72` 跟在它的第二行后面，没有输出含有 U+000D 或 U+2028。计数行是 `4 meals, 9 dishes.`、`4 meals, 5 dishes.`、`2 meals, 3 dishes.` 和 `1 meal, 2 dishes.`，每个后面跟着 ` \u00d7n: servings.`，以及 `4 餐，9 道菜。`、`4 餐，5 道菜。`、`2 餐，3 道菜。` 和 `1 餐，2 道菜。`，每个后面跟着 `\u00d7n：份数。`。 |
| F11-T31 | 功能 | `recipe-menu menu show`、`recipe-menu menu new` | 没有菜的周的选择 9。表格在每一餐显示 `\u2014`，`NO_DISHES` 代替计数行，没有讲 `\u00d7n` 的一行。每天都只有一位数日期的周，日期列更窄。某一天写了设置没有的一餐的空列表不改变任何东西，只写了 `week` 的文件也一样（选择 8 和 9，A 点）。 | 1. 一份菜单为空的示例副本：`menu new 2026-W47`、`menu new 2026-W53` 和 `menu new 2026-W23`，然后是 F 块的六行。2. 一份新的示例副本，`menus/2026-W51.toml` 写成 `week = "2026-W51"\n\n[monday]\nbreakfast = []\n`，`menus/2026-W52.toml` 写成 `week = "2026-W52"\n`：`menu show 2026-W51`、`menu show 2026-W51 --lang zh` 和 `menu show 2026-W52`。 | 1. `menu new` 的每一行给出退出码 0，F 块的每一行给出它的输出，退出码 0，err 为空。在 `2026-W23` 的输出里，日期列在英文里宽 9 列，在中文里宽 11 列，来自 `Mon 1 Jun` 和 `周一 6月1日`。2. `(0, out EMPTY(2026-W51, EN, [lunch, dinner]))`、`(0, out EMPTY(2026-W51, ZH, [lunch, dinner]))` 和 `(0, out EMPTY(2026-W52, EN, [lunch, dinner]))`。 |
| F11-T32 | 功能 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | `cli` 在运行任一命令之前，用 F05 的消息和退出码报告命令行上的错误、缺少的数据文件夹和损坏的设置：两个周、一个选项、单独的 `menu`，以及不构成任何命令的第二个词。`--help` 显示帮助，什么都不运行。然后同样的文件夹给出命令的输出（2.2 和 2.4 的错误，选择 1，F05 设计 2.10）。 | 1. 在 `example` 里：`menu new 2026-W47 2026-W48`、`menu new 2026-W47 2026-W48 --lang zh`、`menu show 2026-W47 2026-W48`、`menu new --tag quick`、`menu show --tag quick` 和 `menu show --tag quick --lang zh`。2. 在 `example` 里：`menu`、`menu --lang zh`、`menu cook` 和 `menu --help`。`menu` 和 `menu --lang zh` 运行 `main` 时用 `commands=` 传入 v0.1 的八个命令，按帮助里的顺序，从 `INIT_COMMAND` 到 `MENU_SHOW_COMMAND`，然后是 `SHOP_COMMAND`，就像 F11-T01 传入它的七个命令一样，这样不管之后的功能加上什么菜单命令，它们那一行都写出 F11 的两个命令。F14-T21 检查带 `menu suggest` 的那一行。3. 在 `example` 里：`menu new 2026-W48 --help`、`menu show next --help` 和 `menu new 2026-W99 --help --lang zh`。4. M 是 `tmp_path / "missing"`：在 M 里 `menu new`，在 M 里 `menu show next --lang zh`。5. 一份带损坏设置的新示例副本：`menu new 2026-W48`，然后 `menu show 2026-W47`。6. 在 `example` 里：`menu new 2026-W48`，然后 `menu show 2026-W47`。 | 1. `(2, err ['Unexpected argument "2026-W48". Write "recipe-menu menu new [WEEK]".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["多余的参数“2026-W48”。请写成“recipe-menu menu new [周]”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['Unexpected argument "2026-W48". Write "recipe-menu menu show [WEEK]".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ['"menu new" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`、`(2, err ['"menu show" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])` 和 `(2, err ["“menu show”没有选项“--tag”。它没有自己的选项。", "运行“recipe-menu --help”查看选项。"])`。2. `(2, err ['The commands that start with "menu" are "menu new" and "menu show".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["以“menu”开头的命令有“menu new”和“menu show”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['Unknown command "menu cook".', 'Run "recipe-menu --help" to see the commands.'])`，以及退出码 0 和 3 里的帮助。3. 每一行给出退出码 0，err 为空，out 上是和不指定文件夹的 `--help` 相同的文字，第三行则和 `--help --lang zh` 相同。4. `no_data_folder(M)` 和 `no_data_folder(M, ZH)`，M 仍然不存在。5. 两行都给出 `(1, err STOP(settings.toml, meals, 设置的 UNKNOWN_MEAL(meal="supper")))`，`menus/` 里只有 `2026-W47.toml`。6. `(0, out NEW(example/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))` 和 `(0, out SHOW_47)`。在 6 之前，示例的 `menus/` 里只有 `2026-W47.toml`。 |
| F11-T33 | 集成 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 两个命令都使用 `cli` 选的数据文件夹和 `cli` 选的语言：`--data`，否则 `RECIPE_MENU_DATA`，否则 `~/recipe-menu`；`--lang`，否则设置里的语言，否则英文。`menu new` 的第一行写出新文件的完整路径。带字节顺序标记和 CRLF 换行的数据文件读起来相同，这是 v0.1-S08 的期望，新文件仍然是 LF 换行（2.2 和 2.4 的参数，F05 设计 2.10）。 | B 是 `tmp_path / "One Drive" / "菜谱"` 处的一份新示例副本，E 是 `{"RECIPE_MENU_DATA": str(B)}`。1. `menu show 2026-W47` 和 `menu new 2026-W48`，都不指定文件夹，`environ` 是 E。2. 不指定文件夹 `menu show 2026-W47`。然后在 `home / "recipe-menu"` 放一份新的示例副本，不指定文件夹 `menu new 2026-W48`。3. `monkeypatch.chdir` 到 `tmp_path / "cwd"` 之后，用参数 `menu new 2026-W49 --data rel` 运行 `main`，`rel` 处有一份新的示例副本。4. 用参数 `menu new 2026-W50 --data ~/other` 运行 `main`，`home / "other"` 处有一份新的示例副本。5. 一份带中文设置的新示例副本 C：`menu show 2026-W47`、`menu show 2026-W47 --lang en` 和 `menu new 2026-W48`。6. 一份带 BOM 和 CRLF 的新示例副本 D：`menu show 2026-W47`，然后 `menu new 2026-W48`。 | 1. `(0, out SHOW_47)` 和 `(0, out NEW(B/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`。2. `no_data_folder(home / "recipe-menu")`，然后 `(0, out NEW(home/recipe-menu/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`。3. `(0, out NEW(Path.cwd() / "rel" / "menus" / "2026-W49.toml", 30 November to 6 December 2026, lunch and dinner))`，一个完整路径。4. `(0, out NEW(home/other/menus/2026-W50.toml, 7 to 13 December 2026, lunch and dinner))`。5. `(0, out SHOW_47_ZH)`、`(0, out SHOW_47)` 和 `(0, out NEW_ZH(C/menus/2026-W48.toml, 2026年11月23日至29日, 午餐和晚餐))`。6. `(0, out SHOW_47)`，即 v0.1-S08 的第 3 步，以及 `(0, out NEW(D/menus/2026-W48.toml, 23 to 29 November 2026, lunch and dinner))`。在 1 到 6 里，每个新文件的内容都是它那一周和 `[lunch, dinner]` 的 `menu_text`，没有字节顺序标记，也没有 `b"\r"`。 |
| F11-T34 | 集成 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 在 `main` 上运行 v0.1-S16。设置决定新文件和表格里的餐次，以及没有写份数的菜的份数。一餐一道菜的计数行是 v0.1-S16 的英文那一行和 A 点的新中文那一行（选择 3、5、8 和 9）。 | R 处的 init 文件夹，把 `settings.toml` 里的 `meals = ["lunch", "dinner"]` 换成 `meals = ["breakfast", "lunch", "dinner"]`，把 `servings = 2 ` 换成 `servings = 3 `。1. `menu new 2026-W48`。2. 把 `menus/2026-W48.toml` 里的 `[monday]\nbreakfast = []` 换成 `[monday]\nbreakfast = ["tomato-egg"]`。3. `menu show 2026-W48`，然后 `menu show 2026-W48 --lang zh`。 | 1. `(0, out NEW(R/menus/2026-W48.toml, 23 to 29 November 2026, breakfast, lunch, and dinner))`，它的第二行是 `7 days with breakfast, lunch, and dinner, all empty.`，文件内容是 `menu_text(2026-W48, [breakfast, lunch, dinner])`。3. E 块的两段输出，退出码都是 0，err 为空：列是 Day、Breakfast、Lunch 和 Dinner，Mon 23 Nov 的早餐是 `Tomato and egg stir-fry \u00d73`，计数行是 `1 meal, 1 dish. \u00d7n: servings.` 和 `1 餐，1 道菜。\u00d7n：份数。`。 |
| F11-T35 | 集成 | `recipe-menu menu show`、`recipe-menu menu new`、`main` | 在 `main` 上对 `menu show` 运行 v0.1-S23，并对 `menu new` 那些什么都不创建的行做同样的检查。无论命令报告什么，`home` 和当前文件夹下的每个文件和文件夹都保持原来的字节和修改时间，也没有加入任何条目（2.4 的副作用，选择 4）。 | `home / "recipe-menu"` 处的一份新示例副本，带一个空的 `shopping/`，以及空的当前文件夹 `tmp_path / "cwd"`，用 `monkeypatch.chdir` 进入。在这些行之前和之后，用 `tests/f07_support.py` 的 `snapshot` 记录 `home` 和当前文件夹。这些行都不指定文件夹：`menu show 2026-W47`、`menu show 2026-W48`、`menu show 2026-W99`、`menu show`、`menu show --tag x`、`menu show --help`、`menu new 2026-W47`、`menu new 2026-W99` 和 `menu new 2026-W47 2026-W48`。然后是菜单错字、新的快照，以及 `menu show 2026-W47` 和 `menu new 2026-W47`。 | 结果依次是：`(0, out SHOW_47)` 和 `(1, err [NO_MENU(2026-W48)])`，即 v0.1-S23 运行的两行 `menu show`，`(2, err [NOT_A_WEEK("2026-W99")])`，`(1, err [NO_MENU(2026-W46)])`，退出码 2 和把 `quick` 换成 `x` 后 F11-T32 里 `menu show --tag quick` 的两行，退出码 0 和帮助，`(1, err [EXISTS(home/recipe-menu/menus/2026-W47.toml)])`，`(2, err [NOT_A_WEEK("2026-W99")])`，以及退出码 2 和 F11-T32 里 `menu new 2026-W47 2026-W48` 的两行。菜单错字之后：`(1, err STOP(menus/2026-W47.toml, Monday dinner, UNKNOWN_RECIPE(recipe="tomato-eggs")))`，以及再一次的拒绝。这些行之后的每个快照都和之前的快照相同。 |
| F11-T36 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令运行两个命令。无论 Python 给流的是什么编码，它都把输出以 UTF-8 写到 stdout，把退出码 1 或 2 的消息写到 stderr（2.2，2.4，F05 设计 2.9）。 | `tests/f05_support.py` 的 `run_module`，与 F10-T19 相同，它把 `HOME` 和 `USERPROFILE` 设成 `tmp_path / "home"`，把 `PYTHONIOENCODING` 设成 `ascii`。用 `example`：1. `menu show 2026-W47 --lang zh --data <example>`。2. `menu new 2026-W48 --lang zh --data <example>`。3. `menu new 2026-W48 --data <example>`。4. `menu show 2026-W99 --lang zh --data <example>`。5. `menu show 2026-W49`，带 `data=example.root`，它设置 `RECIPE_MENU_DATA`。没有一行用 `this`、`next` 或不写周，因为新进程会读时钟。 | 1. 退出码 0，stdout 上是 `SHOW_47_ZH` 的各行，stderr 为空。2. 退出码 0，stdout 上是 `NEW_ZH(example/menus/2026-W48.toml, 2026年11月23日至29日, 午餐和晚餐)` 的各行，stderr 为空，文件内容是 `menu_text(2026-W48, [lunch, dinner])`。3. 退出码 1，stdout 为空，stderr 上是 `EXISTS(example/menus/2026-W48.toml)` 这一行。4. 退出码 2，stdout 为空，stderr 上是 `NOT_A_WEEK_ZH("2026-W99")` 这一行。5. 退出码 1，stdout 为空，stderr 上是 `NO_MENU(2026-W49)` 这一行。 |
| F11-T37 | 集成 | `recipe-menu menu new`、`recipe-menu menu show`、`main` | 随机菜单。对设置里任意顺序的任意一组餐次、任意默认份数、下面列出的任意一周，以及天、餐、菜和份数的任意组合，`menu new` 写出 2.2 的文件和它的三行，`menu show` 用两种语言给出 2.4 的规则给出的各行。随机组合覆盖其他用例没有列出的宽度、格子和计数行（2.2，2.4，选择 2、3 和 7 到 9）。 | `random.Random(20261114)` 构造 100 个文件夹，每个都是一份菜单为空的示例副本。下面每个选择的机会都相等，另有说明的除外。设置：`settings.toml` 写出 `meals = [...]`，按随机顺序列出 F11-T17 的七组之一，以及 `servings = n`，n 从 1 到 5。周 W：`2026-W01`、`2026-W23`、`2026-W47`、`2026-W49`、`2026-W53` 和 `2027-W01` 之一。然后在日期 D 这天运行 `menu new V --lang L`，L 是 `en` 或 `zh`：V 是 W 本身、`this` 或不写值，D 是 W 的七个日期之一；或者 V 是 `next`，D 是 W 前一周的七个日期之一。然后测试带着菜重新写出 W 的文件。`Day` 的每一天有 1/4 的机会被省略。没有被省略的一天按随机顺序列出设置的各餐，每一餐有 0 到 3 道菜。每道菜是示例的七个菜谱 ID 之一，写成 `"ID"`、`{ recipe = "ID" }` 或 `{ recipe = "ID", servings = k }`，k 从 1 到 12。然后运行 `menu show W --lang L2`，L2 是 `en` 或 `zh`。 | `menu new` 给出退出码 0，以及 W 的文件、W 的日期和各餐标签的 `NEW` 或 `NEW_ZH`，文件内容是 `menu_text(W, S)`，S 是按 `Meal` 顺序排列的设置的餐次。`menu show` 给出退出码 0，err 为空，以及测试按 2.4 的规则、从它写入的菜构造出的输出。测试把标题、计数行和 `NO_DISHES` 的模板、各列的标题，以及七个菜谱的两种语言的名称都写成字面量。它从 F06 的 `date_range` 和 `short_date` 取得日期，用 F02 的 `format_table` 不传 `min_widths` 排出表格，不用 F11 的任何代码。没有写份数的菜得到 n。 |
| F11-T38 | 性能 | `recipe-menu menu show`、`python -m recipe_menu` | PT01 和 v0.1-S31：`menu show` 在 1 秒内打印 PT01 的一周，21 个格子里共 63 道菜，按从启动到退出的 5 次运行的中位数计（需求 7.1，2.4，选择 11）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"` 里。不计时运行一次，然后按第 3 节的说明计时运行 `python -m recipe_menu menu show 2026-W26 --data <pt01>` 5 次。 | 每次运行都以 0 退出，在 stdout 上写出第 3 节的 PT01 周的 26 行，stderr 上什么都不写。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。 |

## 3. 性能用例

PT01 列出的命令里有 `menu show`（需求 7.1），所以 `recipe-menu menu show` 有一个用例。F11 的其他接口都没有，PT01 也不为 `menu new` 计时（R14）。

| 编号 | 指标 | 机器 | 余量 | 基线 |
| --- | --- | --- | --- | --- |
| F11-T38 | PT01：在有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`recipe-menu menu show` 在 1 秒内完成。按从启动到退出的 5 次运行的中位数计。 | Troy 的电脑：Windows 11，使用 `recipe-menu` 环境的 Python 3.13。这个用例也在 CI 上、在 `.github/workflows/troy-mode.yml` 的 `ubuntu-24.04` 运行器上运行，那不是一台固定的机器（架构第 10 节）。 | Windows 上没有余量：中位数必须小于 1 秒，因为超出 PT01 的余量会放过达不到指标的命令（v0.1 测试方案第 3 节）。Linux 上是 3 秒，与 F07-T25、F09-T28 和 F10-T21 相同，使这个用例在速度未知的运行器上也成立，同时仍然能抓到慢了几倍的情况。 | 首次运行。在 Troy 的电脑上，架构师的模型在两组各 5 次的运行里，`menu show 2026-W26` 的中位数是 0.262 秒和 0.247 秒，同一组里 `show recipe-0500` 是 0.231 秒和 0.203 秒，当时其他测试运行占用着电脑（设计第 4 节）。F09 的实现 PR 记录的 `show` 中位数是 0.153 秒。模型不是实现，所以由 F11 的实现 PR 记录第一个基线。 |

**哪个系统是 Troy 的电脑。** CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。所以这个用例用 `tests/pt01_support.py` 的 `time_limit` 的上限：`sys.platform == "win32"` 时为 1 秒，否则为 3 秒，与 F07-T25、F09-T28 和 F10-T21 相同。在 Windows 上增加 CI 任务，会先改动这份方案。

**PT01 数据文件夹。** 由 `tests/pt01_support.py` 的 `make_pt01` 写出，与 F07-T25、F09-T28 和 F10-T21 相同，形状就是 v0.1 测试方案给出的那样。F11 不改动这个生成器。它的设置写的是早餐、午餐和晚餐，每道菜 2 份。2026 年第 k 周的菜单给第 d 天第 m 餐的第 s 道菜的菜谱编号是 `((k - 1) * 63 + 9 * d + 3 * m + s) % 1000 + 1`，d、m 和 s 都从 0 数起，每顿晚餐的第一道菜是 4 份。所以从 2026 年 6 月 22 日到 28 日的 `2026-W26` 写到 63 个不同的菜谱 `recipe-0576` 到 `recipe-0638`，它的 21 餐每餐 3 道。文件夹里的任何一周都可以，这一周是架构师的模型用的那一周。

**计时运行。** 这个用例使用 F09 在 `tests/pt01_support.py` 里加入的通用计时运行：`command_run`、`command_runs`、`record_times` 和 `time_limit`，它们保持原来的名字和行为。

**预期输出。** `tests/pt01_support.py` 新增 `pt01_menu_show`，它按生成器的规则用 f-string 构造结果，不用 F02 的 `format_table`。PT01 周共 26 行。第 1 行是 `Menu for 2026-W26, 22 to 28 June 2026`，第 2 行为空，第 3 行是补到 10 列的 `Day`、三个空格、补到 14 列的 `Breakfast`、三个空格、补到 14 列的 `Lunch`、三个空格和 `Dinner`。然后对 0 到 6 的每一天 d 和 0 到 2 的每一行 s 写一行：补到 10 列的这一天的格子，三个空格，早餐和午餐的格子，各补到 14 列，后面各跟三个空格，然后是晚餐的格子。s 为 0 时这一天的格子是 `Mon 22 Jun` 到 `Sun 28 Jun`，其他行为空。第 m 餐的格子是 `Recipe NNNN \u00d7n`，NNNN 是四位数的编号 `576 + 9 * d + 3 * m + s`，晚餐的第一道菜 n 是 4，其他是 2。所以第 4 行是 `Mon 22 Jun   Recipe 0576 \u00d72   Recipe 0579 \u00d72   Recipe 0582 \u00d74`。然后是一个空行和 `21 meals, 63 dishes. \u00d7n: servings.`。测试经理在一个 PT01 文件夹上把这条规则和模型的输出逐行比较过。

**用例的步骤。**

1. 生成文件夹。
2. 不计时启动一次命令，像第 3 步那样检查它的结果。Windows 第一次读这 1,053 个新文件时很慢（F07 测试方案第 3 节），而 Troy 自己的数据文件夹不会每次运行都付出这个代价。
3. 用 `command_runs` 把同一个命令启动 5 次，每次都是新进程：`sys.executable -m recipe_menu`，在 `tmp_path` 里运行，`HOME` 和 `USERPROFILE` 设成一个空的主文件夹，没有 `RECIPE_MENU_DATA`。每次运行都必须以 0 退出，stdout 正好是预期的输出，stderr 为空。不满足这些的运行会让用例失败，无论它用了多少时间。
4. 取 5 次时间的中位数，与这个系统的上限比较。
5. 用 `record_property` 记录 5 次时间、中位数和范围，使 JUnit 报告保存它们，供下次比较。

**它怎样在 Troy 的电脑上运行。** 这个用例在 `tests/` 里，所以每次在 Troy 的电脑上完整运行测试时都会运行，主会话为每个 PR 用 `recipe-menu` 环境的 Python 启动这样的运行。在 F11 的实现 PR 里，主会话还在没有其他测试运行、构建或安装进行时，用 `python -m pytest tests/test_f11_performance.py --junitxml=reports/pt01-f11.xml` 单独运行它。PR 描述报告中位数和范围，那次运行就是基线。发布测试在同一台机器上运行 v0.1-S31。

**基准测试检查表。** 这个用例这样回答 `benchmark-checklist` 的问题：

- 限制因素：设计选择 11 和第 4 节给出了它。`menu show` 读 `show` 读的文件，再加上对有 52 个名称的 `menus/` 的一次列出、一个菜单文件和另外 62 个菜谱文件。所以 Python 的启动、导入、有 300 种食材的目录，以及对 1,000 个菜谱文件的列出限制它的速度，和 `show` 一样。在同一组运行里，架构师的模型比 `show` 多用 0.03 到 0.04 秒。这个用例不做性能剖析，因为剖析会拖慢运行。`[refactor]` PR 会做剖析。
- 调优：每次运行都是一个新的 Python 进程，用已安装的包及其编译文件，没有覆盖率工具和调试器，与 Troy 的运行方式相同。第 2 步的不计时运行已经把文件读过一次。coverage.py 只测量测试进程，所以 CI 里的 `coverage run -m pytest` 不会拖慢计时的进程。
- 极限：`menu show` 通过管道写出约 1.5 KB，读 63 个菜谱文件、一个菜单文件、目录和设置，约 160 KB，磁盘几毫秒就能读完。所以计时测量的是 Python 的工作。
- 错误：第 2 步和第 3 步检查每次运行的退出码、完整的 stdout 和为空的 stderr。
- 可重复性：5 次计时运行，记录中位数和范围。和基线的差别如果小于基线各次运行的范围，就不算可测量的变化。
- 相关性：这个用例为从启动到退出的整个命令计时，这正是 Troy 要等的时间。三餐每餐三道菜、来自 63 个不同菜谱的一周，是 PT01 的一周所能有的最多的菜，所以 `menu show` 读了它对 PT01 的一周所能读的最多的菜谱文件。
- 工作确实发生了：63 个格子里 63 个不同菜谱的名称，以及计数行 `21 meals, 63 dishes.`，说明 `menu show` 读了菜单和它写到的每个菜谱。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 单独的 `MENU_NEW_COMMAND` 和 `MENU_SHOW_COMMAND` 的字段，`recipe_menu.commands.menu`、`recipe_menu.menus` 和 `recipe_menu.datafile` 的 `__all__` 列出的名字，以及作为 `menu/messages.py` 和 `menus/messages.py` 里常量的消息。 | mock 完整声明了它们，所以单独测它们的测试会在 mock 上通过（R09）。F11-T01、F11-T02 和 F11-T04 在一次运行旁边检查它们，用例通过输出检查每段文字。代码评审检查文字放在哪里，以及 `menu` 只导出它的两个命令（选择 12）。 |
| `menu` 只导入 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`。 | R07。CI 里的依赖检查器把每个导入和架构第 3 节的表格比较，那张表正好允许这些模块。 |
| `menu new` 只通过 `create_file` 访问磁盘，`menu show` 在最后一个文件之后一次写出输出，两个命令都不保留状态，也没有缓存。 | 没有接口显示是哪个模块发出调用，或者文字什么时候到达流。F11-T25 和 F11-T27 记录两个命令对磁盘的每次调用，每个期望退出码 1 或 2 的用例都检查输出流为空，F11-T02 在一个文件夹上多次运行 `run`。代码评审检查其余部分。 |
| 用 2.1 和 2.3 的约束之外的 `Arguments` 调用 `run`：两个值，或者一个选项。 | `cli` 从不传入它们（F05 设计 2.10）。F11-T32 检查 `cli` 拒绝每个这样的命令行。 |
| `create_file` 里失败的关闭。 | 故障工具没有针对关闭的规则。设计 3.3 给失败的关闭和失败的写入同一行错误表和同样的删除，F11-T14 和 F11-T23 测试失败的写入。 |
| 用含有 `..` 的路径调用 `create_file`，比如 `folder.root / ".." / "x.toml"`，以及用不是 `str` 的文字调用它。 | `DataFolder.relative` 比较两个路径的各部分，不解析 `..`（F03 设计 2.1），每个调用者传入的都是 `DataFolder` 给出的路径。不是 `str` 的文字违反签名里的类型，由 mypy 检查。 |
| `menu new` 期间进程被杀掉，或者电脑断电。 | 这时删除无法执行，测试也无法让进程停在选定的一步。F11-T14 和 F11-T24 检查像进程被杀掉那样的 Ctrl+C 情况。 |
| 来自控制台的真正 Ctrl+C、文件系统拒绝的访问，以及真正创建这个文件或打开着它的第二个程序。 | 没有 CI 机器有控制台，Linux 上的 root 用户无视权限位，测试也无法让第二个程序正好在某一步动作。故障工具抛出 Python 对 Ctrl+C 抛出的 `KeyboardInterrupt`，与 F05-T41 相同。它还在每个用例选定的那一步抛出 `PermissionError`，并制造竞争（第 2 节）。 |
| `menu show` 期间按 Ctrl+C。 | `cli` 对每个命令都给出退出码 130（F05 设计 2.10），F05-T41 测试了它。`menu show` 不写文件，所以 Ctrl+C 什么都不会留下。 |
| 在接近 `datetime.date` 最后一天的日期运行 `menu new` 和 `menu show`。 | F06-T22 在那里测试 `week_from_argument`，而电脑的时钟不会给出这样的日期（F06 设计 2.7）。 |
| 带 v0.1 全部八个命令、包括 `shop` 的帮助。 | F05-T45 用替身检查那些行，v0.1-S19 用真正的命令检查它们。F11-T01 检查 `menu new` 和 `menu show` 那两行，所用的形式在 F13 加入 `shop` 之后仍然成立。 |
| Windows Terminal 里的中文输出。 | 没有 CI 机器有 Windows 控制台（架构第 10 节），所以 v0.1-S25 由 Troy 检查。F11-T30 检查中文表格按显示宽度对齐，F11-T36 检查 `python -m recipe_menu` 以 UTF-8 写出中文输出。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的汉字。 |
| 设计第 2 节里给后续功能的计划：带 `NO_MENU` 的 F13 `shop`，F14 的 `menu suggest`，以及使用 `create_file` 的 F15 `add`。 | 每个后续功能的设计和测试方案覆盖它们。F11-T04 通过 `menus` 检查 `NO_MENU`，F11-T10 检查 F15 的情况提到的名称 `Rice.toml`。 |
| 发布测试里的 v0.1-S08、v0.1-S13 到 v0.1-S16、v0.1-S23 和 v0.1-S31。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 加入（TE5）。F11-T16、F11-T20、F11-T29、F11-T33、F11-T34 和 F11-T35 在 `main` 上运行同样的步骤，F11-T38 在每次测试运行时在同样的文件夹上为同一个命令计时。 |

## 5. 与接口设计师的对齐记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-14 | 初稿。 |
| 1.0 | 2026-11-15 | Troy 批准。 |
| 1.1 | 2026-11-17 | 来自 F14 测试方案，对应 Troy 于 2026-11-17 批准的 F14 设计。F11-T32 用 `commands=` 传入 v0.1 的八个命令来运行 `menu` 和 `menu --lang zh`，这样 F14 加上 `menu suggest` 之后，它那一行仍然写出 F11 的两个命令。`[F14 test-fix]` PR 修改这个测试。 |
