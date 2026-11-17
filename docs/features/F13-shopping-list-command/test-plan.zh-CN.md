---
troy-doc: "F13-test-plan"
lang: "zh-CN"
version: "1.1"
updated: "2026-11-17"
status: "Troy 已于 2026-11-15 批准"
mirror-of: "test-plan.md"
---

# F13 购物清单命令：测试方案

## 1. 功能

- 编号和名称：F13 购物清单命令
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.shop` 的 `SHOP_COMMAND`、`recipe_menu.datafile` 的 `replace_file`、`FileCreation` 和 `FileOutcome`、`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的值调用 `SHOP_COMMAND.run` 或 `replace_file`。功能用例像你输入 `recipe-menu shop` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 在 `MENU_SHOW_COMMAND` 之后有 `SHOP_COMMAND`（设计选择 1）。集成用例在 `main` 上运行 v0.1 场景，启动 `python -m recipe_menu`，或者构造随机的星期。性能用例为 `python -m recipe_menu shop` 计时（第 3 节）。每个用例在括号里注明它来自设计的哪一部分，比如（选择 4）。设计的三个示例和其中四行 `# raises` 分别在 F13-T01（2.1）、F13-T11（2.2）和 F13-T03（3.1）里。

**A 点到 C 点。** Troy 于 2026-11-15 批准了设计 1.0，每一点都按建议：按 2.2 和 3.1 的写法接受 11 段新文字（A）；英文的常备行按目录的写法写名称（B）；`replace_file` 创建不存在的 `shopping` 文件夹（C）。B 点的需求变更（PR #86）把 F13 原型的英文常备行改成了 `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper`，把 v0.1-S16 的那一行改成了 `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`。所以原型“In English”和 v0.1-S16 的输出与设计完全一致，没有用例把英文常备行当作例外。设计的选择 8、B 点和其中两处“英文常备行除外”记录的是当时的决定。用例用两种语言检查 A 点的每一段新文字：

- 英文文件的开头，`# Shopping list for 2026-W47` 和 `16 to 22 November 2026: 4 meals, 9 dishes.`：F13-T01、F13-T12、F13-T13、F13-T14 和 F13-T15。
- 一周没有菜时的中文那一行：F13-T11、F13-T14 和 F13-T24。
- `There is nothing to buy.` 和 `没有要买的东西。`：F13-T14。
- `No file was saved.` 和 `没有保存文件。`：F13-T11、F13-T19 和 F13-T21。
- 临时文件留下时的那一行，两种语言：F13-T19。
- `The file cannot be written: "shopping" is not a folder.` 和它的中文：F13-T03、F13-T06、F13-T11 和 F13-T21。

C 点在 F13-T05、F13-T09、F13-T12、F13-T16 和 F13-T21 里：`shopping` 处什么都没有时会得到一个新文件夹，之后某一步失败时它仍然留着；那里是文件夹以外的东西时会得到失败的几行。

**之前功能的测试。** 设计第 3 节说，`shop` 加进 `COMMANDS` 之后，检查真正帮助的每个测试仍然成立。测试经理在 Troy 的电脑上用 Python 3.13.18 检查了这一点：把 `SHOP_COMMAND` 的一个模型放进 `cli` 真正的 `COMMANDS` 后，main 的全部测试给出 553 个通过、4 个跳过，跳过的 4 个是 main 上只在 Linux 上运行的用例。所以之前功能的测试一个都不变，F13 的测试 PR 也不改动任何一个。`tests/f11_texts.py` 的 `HELP` 和 `HELP_ZH` 保持不变，因为 F11-T01 给 `main` 传的是它自己的七个命令。F13 不改动 `tests/data/example/` 里的任何文件，也不改动 `tests/f08_support.py`、`tests/f11_support.py`、`tests/f12_support.py` 或 `tests/pt01_support.py` 里的任何函数。

**R09。** mock 定义了每条消息和带全部字段的 `SHOP_COMMAND`，把这一项加进 `COMMANDS`，并把 `replace_file` 和 `PARENT_NOT_A_FOLDER` 加进 `datafile`。它的 `replace_file` 什么都不碰，给出 `FileCreation(FileOutcome.CREATED)`，它的 `run` 不读文件，什么都不写，什么都不抛，并给出 0（设计第 2 节）。所以只检查 `SHOP_COMMAND` 的字段、帮助、某条消息、退出码 0、空的错误流，或者 `replace_file` 给出 `CREATED` 的测试，会在 mock 上通过。只检查 `cli` 在运行 `shop` 之前所做的事情的测试也一样：缺少数据文件夹、损坏的设置、`shop 2026-W47 2026-W48`、`shop --tag x` 和 `shop next --help`。只检查 `shop` 没有改动文件、`shopping\` 仍然为空、保存失败后旧文件还在，或者没有留下 `.tmp` 文件的测试也一样（架构师说明 4）。每个检查这类内容的用例，也检查 mock 弄错的东西：`shop` 的输出，退出码 1、2 或 130，`run` 抛出的 `UsageError`，保存的文件的字节，新的 `shopping\`，`replace_file` 的结果或问题，`replace_file` 抛出的错误，或者故障工具记录的调用。F13-T01、F13-T02、F13-T05、F13-T08、F13-T12、F13-T14、F13-T16、F13-T18、F13-T19、F13-T21、F13-T22、F13-T24 和 F13-T27 只在一个 mock 会弄错的结果旁边检查这类内容。每个期望 `shop` 给出退出码 0 的用例都检查完整的输出，这个输出从不为空。每个期望 `CREATED` 的用例都检查文件的字节或者调用记录。`tests/f13_support.py`、`tests/f13_texts.py` 和 `tests/f13_blocks.py` 在被导入时不调用 F13 的任何接口。

**两个系统。** 每个用例都在 Linux 和 Windows 上运行，没有用例在任何一个系统上跳过。CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。问题用系统的路径分隔符写出它的文件。所以在预期的一行里，`menus/2026-W47.toml` 代表 `str(Path("menus", "2026-W47.toml"))`，以用例的某个文件夹开头的路径，比如 `X/shopping/2026-W47.md`，代表 `tmp_path` 下这个完整路径的 `str`。`shop` 的输出只在最后一行里有路径，所以它们的各列在两个系统上宽度相同。中文输出里每个汉字占两列。涉及两个系统不同之处的输入，由用例写出每个系统给出的结果：

- 移到一个文件夹上（F13-T09 和 F13-T21）。把一个文件用真正的 `os.replace` 移到一个文件夹上，在两个系统上都会失败：Windows 上是 `PermissionError`，得到 `FILE_WRITE_DENIED`；Linux 上是 `IsADirectoryError`，得到带 `Is a directory` 的 `FILE_WRITE_ERROR`。用例用 `tests/f13_support.py` 的 `move_message`（见下文）从系统取得消息，就像 F08-T07 用 `system_message` 取得失败的 `mkdir` 的消息。
- 别的程序正打开着的清单文件（F13-T21）。Windows 拒绝移动，这次运行给出带 `FILE_WRITE_DENIED` 的失败的几行，保留旧的字节。Linux 替换这个文件，这次运行给出清单。测试经理在 Troy 的电脑上用 Python 3.13.18 做了这次移动：移到一个被 `open(path, "rb")` 打开着的文件上时，`os.replace` 抛出了带 `Access is denied` 的 `PermissionError`。
- 系统无法创建的文件夹（F13-T07）：在不存在的数据文件夹下 `mkdir`，以及系统无法查看的名称，在 Windows 上是 `a?b`，在 Linux 上是 256 个 `a`，与 `tests/f05_support.py` 的 `unreadable_name` 给出的相同。用例用 `tests/f08_support.py` 的 `system_message("folder", path)` 从系统取得消息，它在调用之前做同样的 `mkdir`。
- 悬空链接（F13-T06 和 F13-T21），用 `tests/f08_support.py` 的 `dangling_link` 创建；以及指向一个文件夹的链接（F13-T05），用 `tests/f13_support.py` 的 `folder_link` 创建：在 Windows 上是目录联接，在 Linux 上是符号链接。目录联接不需要普通用户没有的权限。
- F13-T23 的数据文件夹 `One Drive/菜谱` 里有空格和汉字，在两个系统上都是合法路径。

**被拒绝的访问。** 没有用例通过文件系统拒绝访问，无论是用 `os.chmod`、访问控制列表，还是用 `tests/f04_support.py` 的 `listing_denied`。Linux 上的 root 用户无视权限位，所以依赖权限位的测试以 root 运行时会失败，F04 的测试说明里写过这一点。用例里的每个 `PermissionError` 都来自故障工具，它对每个用户都以同样的方式抛出；或者来自对每个用户都成立的拒绝：移到一个文件夹上，以及在 Windows 上移到一个打开着的文件上。所以每个用例在 Linux 上以 root 运行、在 Windows 上以管理员运行时都能通过。

**用例怎样让磁盘出错。** 用例使用 `tests/f13_support.py` 的 `shop_faults(base, *rules)`。它就是 `tests/f08_support.py` 的故障工具加上三处补充，所以它替换 `os.mkdir`、`os.rmdir`、`os.unlink`、`os.remove`、`os.scandir`、`os.listdir`、`io.open` 和 `builtins.open`，还替换 `os.replace`，Python 3.13 的 `Path.replace` 调用的就是它。它打开期间，记录对 `base` 下路径的每次调用，并应用它的规则。规则写成种类、路径和效果，比如 `open T: DENIED`。F08 的规则按 F08 和 F11 测试方案给出的那样成立：

- `mkdir P: E` 抛出 E，代替创建文件夹 P。`mkdir P: race` 先像别的程序那样创建 P，然后调用，这次调用抛出系统的 `FileExistsError`。
- `open P: E` 抛出 E，代替以 `x` 模式打开 P，所以系统什么都不创建。`open P: race` 先创建内容为 `b"mine\n"` 的 P，然后打开，这次打开抛出系统的 `FileExistsError`。`open P: after E` 打开、关闭文件，然后抛出 E，所以 P 存在，但调用从没拿到它。
- `write P: E` 在打开 P 得到的文件上，写入第一次写入的文字的前一半，即 `text[: len(text) // 2]`，刷新，然后抛出 E。
- `unlink P: E` 抛出 E，代替每一次删除 P。

F13 补充这些：

- 一次移动的记录是 `move A B`，源 A 和目标 B 都相对于 `base`。`move P: E` 抛出 E，代替源为 P 的那次移动，什么都不移动。
- `close P: E` 真的关闭以 `x` 模式打开 P 得到的文件，然后抛出 E。它在这个文件的 `close` 和它的 `with` 块结束时起作用，除非另一个异常已经在传递中。
- `unlink P: later E` 让第一次删除 P 照常进行，并抛出 E，代替之后的每一次删除 P。所以 3.1 的第 3 步照常运行，而失败之后的删除会失败。

效果就是 F08 测试方案里的那些：`DENIED` 是 `PermissionError(errno.EACCES, "Permission denied")`，`IO` 是 `OSError(errno.EIO, "Input/output error")`，`NO_SPACE` 是 `OSError(errno.ENOSPC, "No space left on device")`，`CTRL_C` 是 `KeyboardInterrupt()`，`BUG` 是 `RuntimeError("bug")`，`EMPTY_IO` 是 `OSError(errno.EIO, "")`。`TimeoutError()` 和 `OSError()` 的 `strerror` 是 `None`。F13 补充 `EXISTS`，即 `FileExistsError(errno.EEXIST, "File exists")`，用来钉住 3.1 表格里 `FileExistsError` 的那几行（架构师说明 1）。抛出 `KeyboardInterrupt` 的用例通过 `pytest.raises` 拿回它，或者通过 `tests/f08_support.py` 的 `call_main` 从 `main` 得到退出码 130，`call_main` 把离开 `main` 的 `KeyboardInterrupt` 变成一次失败。

`tests/f13_support.py` 里的 `ShopFaults` 是 `tests/f08_support.py` 的 `Faults` 的子类。它加上 `replace` 方法、用于 `close` 规则的文件包装，以及 `later` 规则的计数，`shop_faults` 替换 `faults` 替换的那些函数，再加上 `os.replace`。`tests/f08_support.py` 保持 463 行，在 R06 的 500 行之内，F08 和 F11 的故障工具保持原样。

给开发者的说明：只有当 `replace_file` 通过设计 3.1 列出的调用访问磁盘时，这些用例才成立。除了故障工具不记录的探查 `os.path.isdir` 和 `os.path.lexists`，它用 `Path.mkdir()` 创建文件夹，在第 3 步用 `Path.unlink(missing_ok=True)`、在失败之后用 `Path.unlink` 删除 `temp`，用 `Path.open` 或 `open` 以 `"x"` 模式打开 `temp`，在打开得到的文件对象上用一次 `write` 调用写入全部文字，文字为空时也一样，并用 `os.replace` 或 `Path.replace` 移动 `temp`。在 Troy 电脑上的 Python 3.13.18 里，`Path.mkdir` 调用 `os.mkdir`，`Path.unlink` 调用 `os.unlink`，`Path.open` 调用 `io.open`，`Path.replace` 调用 `os.replace`。3.1 没有列出的调用，比如 `os.open`、`os.rename`、`Path.write_text`、`Path.touch`、`tempfile` 或 `shutil`，会避开故障工具的规则，或者给出另一份记录，所以用例会失败。所以一次成功的调用的记录里总有 `unlink T`，`T` 处什么都没有时也一样。

**读取记录。** F13-T14、F13-T15 和 F13-T16 用 `shop_faults(F.root)` 记录 `shop` 打开了哪些文件、列出了哪些文件夹，与 F11-T27 相同。故障工具把对数据文件夹下每个路径的打开记为 `read`，以 `x` 模式打开时记为 `open`，后面是相对于这个文件夹、用 `/` 写的路径。它把每次 `os.scandir` 或 `os.listdir` 的列出记进“列出记录”。`cli` 在运行命令之前读取 `settings.toml`，所以每份记录都以 `read settings.toml` 开头。被几道菜用到的菜谱只解析一次，所以它的文件在记录里只出现一次。

测试经理在 Troy 的电脑上用 Python 3.13.18、main 上的读取函数和 `build_shopping_list`、加上上述补充的故障工具，以及一个按设计实现 `shop` 和 `replace_file` 的模型算出了下面的预期文本。这个模型逐字节给出了 F13 原型的两段输出和保存的文件，以及 F05 原型的完整帮助，A 到 H 块都是它的输出。

测试数据遵守这些规则，与 F11 测试方案相同：

- `EXAMPLE` 是代码仓库里的 `tests/data/example/` 文件夹（架构第 10 节）。它没有 `shopping/`。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这份副本上的 `DataFolder`。用例里的 `example` 就是这个 `DataFolder`。“P 处的一份新的示例副本”是用 `tests/f05_support.py` 的 `copy_example` 复制的又一份副本。不带 P 的“一份新的示例副本”在 `tmp_path` 下它自己的路径上。
- “一份菜单为空的示例副本”是删掉了 `menus/` 里每个条目的一份新的示例副本。
- “P 处的 init 文件夹”由 `tests/f07_changes.py` 的 `make_init` 创建：一份新的示例副本，除 `tomato-egg` 外没有菜谱，没有菜单，带有空文件夹 `menus/` 和 `shopping/`。“S16 文件夹”是 `tests/f12_support.py` 的 `s16_folder(example, tmp_path / "init")` 给出的文件夹：init 文件夹，`settings.toml` 里是早餐、午餐和晚餐以及 3 份，`menus/2026-W48.toml` 的周一早餐是 `tomato-egg`。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。它在 `example` 之外，所以不带 `--data` 的一行找不到数据文件夹，除非用例在 `home / "recipe-menu"` 放一个。
- 测试用 `tests/f03_support.py` 的 `write` 写每个文件，它以 UTF-8 和 LF 换行写入，并先创建所需的文件夹；或者用 `put_bytes` 按字节写入。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 替换文件 F 里的第一个 X，它会检查 F 里有 X。
- 没有测试改动代码仓库、碰 `~/recipe-menu` 或读取时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`。F13-T28 和 F13-T30 启动 `python -m recipe_menu` 时，把 `HOME` 和 `USERPROFILE` 设成 `tmp_path` 里的一个文件夹。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

这些命名的改动构造用例的文件夹。每个改动作用于它所在用例的数据文件夹：

- 来自 F09 和 F11 测试方案：没有目录、目录花括号、没有 recipes 文件夹、recipes 是文件、Rice Bowl、大写的 rice、文件夹 x、麻婆的错误、rice 为 0、损坏的设置、额外的菜谱、没有 menus 文件夹、menus 是文件，以及 B 周。`tests/f07_changes.py`、`tests/f09_support.py` 和 `tests/f11_support.py` 的辅助函数创建它们。额外的菜谱是 `boiled-egg`、`steamed-egg` 和 `water`，`water` 的 `ingredients` 为空。B 周是 `menus/2026-W48.toml`：周一晚餐写在午餐之前，用了两次 `rice`；周一午餐是 `mapo-tofu`；周五午餐是 10 份的 `choy-sum`；周日晚餐是 `red-braised-pork`，它有一条警告。
- 来自 F10 测试方案：中文设置，把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`；BOM 和 CRLF，把文件夹里的每个文件重新写成 `b"\xef\xbb\xbf"` 加上它的字节，其中每个 `b"\n"` 换成 `b"\r\n"`。
- 来自 `tests/f06_support.py` 里 F06 的辅助函数：菜单笔误，即 `typo`；v0.1-S07 的菜单错误，即 `mistakes`。菜单笔误让 `menus/2026-W47.toml` 的周一晚餐写成 `tomato-eggs`。
- 来自 `tests/f07_changes.py`：常备清单的错误，即 `pantry_sesame`，把 `pantry.toml` 里的 `"糖"` 换成 `"sesame oil"`；常备清单的条目，即 `pantry_not_text`，把 `"糖"` 换成 `3`。没有常备清单：删除 `pantry.toml`。
- 米饭周 W：用 `tests/f11_support.py` 的 `menu_text(W, [lunch, dinner])` 写出 `menus/W.toml`，并把其中第一个 `dinner = []` 换成 `dinner = ["rice"]`。
- 白开水周：额外的菜谱，并把 `menus/2026-W50.toml` 写成 `week = "2026-W50"\n\n[monday]\nlunch = ["water"]\n`。
- 鸡蛋周：额外的菜谱，把 `pantry.toml` 里的 `"花椒"]` 换成 `"花椒", "鸡蛋"]`，并把 `menus/2026-W51.toml` 写成 `week = "2026-W51"\n\n[tuesday]\ndinner = ["water", "boiled-egg"]\n`。
- 鸡翅换行 S：把 `catalog.toml` 里的 `en = "Chicken wings"` 换成 `en = "Chicken{S}wings"`，S 是 TOML 转义 `\n`、`\r\n` 和 `\u2028` 之一，所以这个英文名称占两行。
- 肉类换行：把 `catalog.toml` 里的 `en = "Meat and seafood"` 换成 `en = "Meat\nand seafood"`，用 TOML 转义 `\n`。
- 缺少的名称：把 `catalog.toml` 里的 `{ zh = "可乐", en = "Cola", category = "other", unit = "罐" }` 换成 `{ zh = "可乐", category = "other", unit = "罐" }`。
- shopping 是文件：把 `shopping` 写成 `b"x\n"`。空的 shopping：空文件夹 `shopping/`。
- 打过勾的清单：把 `shopping/2026-W47.md` 写成 `"# 2026-W47 购物清单\n\n- [x] 番茄 600 g\n"`。旧清单：把 `shopping/2026-W47.md` 写成 `b"old\n"`。旧的临时文件：把 `shopping/2026-W47.md.tmp` 写成 `b"half\n"`。

调用 `main` 遵守这些约定：

- F 里的 `shop 2026-W47 --lang zh` 这样一行代表 `tests/f09_support.py` 的 `at(home, F, "shop", "2026-W47", "--lang", "zh")`。它加上 `--data` 和 F，通过 `tests/f07_support.py` 的 `call` 运行 `main`，带 `home`、`environ`、`today=date(2026, 11, 10)`、两个新的 `io.StringIO` 流，不传 `commands`。“在 D 日”的一行以同样方式运行，但 `today=D`，通过 `tests/f11_support.py` 的 `on(home, F, D, *argv)`。“不带文件夹”的一行没有 `--data`。规则可能用 `CTRL_C` 中断的一行通过 `tests/f08_support.py` 的 `call_main` 运行。除非用例给出，`environ` 是 `{}`。
- 引号里的一个词是一个词，写成带转义的 Python 字符串，比如 `""` 或 `" this"`。词里的每个 `\uXXXX` 代表那一个字符。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟 `"\n"`，没有别的。`(c, err L)` 同样代表 `(c, "", err)`。`(130, "", "")` 是什么都没写的退出。测试比较完整的文本，从不比较它们的 `splitlines()`，因为 `splitlines()` 也在 U+000D 和 U+2028 处断开，而 F13-T13 必须确认输出里没有它们。
- 在一个用例里，P 是这个用例的数据文件夹里它那一周清单文件的完整路径，即 `F.shopping_file(week)`，T 是 P 加上 `.tmp`，比如 `X/shopping/2026-W47.md.tmp`。
- `STOP(W, M)` 和 `STOP_ZH(W, M)` 是英文和中文的 `stop_at_error` 的三行，按 F09 测试方案的定义，由 `tests/f09_texts.py` 的 `stop` 构造结果。W 是一个文件，比如 `catalog.toml`，或者一个文件加一个位置，比如 `menus/2026-W47.toml, Monday dinner`，中文是 `menus/2026-W47.toml，周一晚餐`。
- “在 `check` 的错误之中”的意思与 F09 测试方案相同，由 `tests/f09_support.py` 的 `assert_among_check` 检查。

直接调用 `replace_file` 遵守这些约定：

- 每次调用都有它自己的空文件夹 `base`，在 `tmp_path` 下。`F` 是 `DataFolder(base / "recipe-menu")`，除非输入另有说明，`F.root` 存在。Q 是 `F.shopping_file("2026-W47")`，T 是 `F.shopping / "2026-W47.md.tmp"`。在记录里，S 代表 `recipe-menu/shopping`，Q 和 T 代表这两个路径相对于 `base` 的写法，比如 `recipe-menu/shopping/2026-W47.md.tmp`。
- 问题写成它的文件和它的消息，比如 `shopping/2026-W47.md: FILE_WRITE_DENIED`。`replace_file` 的每个问题都是没有位置的错误。测试用 `tests/f11_support.py` 的 `assert_failed` 检查结果：`outcome is FileOutcome.FAILED`、`severity is Severity.ERROR`、`str(problem.file)`、`place is None`、`text(Lang.EN)`、`text(Lang.ZH)`、作为其路径 `str` 元组的 `left`，以及 `existing is None`。
- “X 的树”和“X 的完整记录”是 F08 测试方案里的那些，由 `tests/f08_support.py` 的 `tree` 和 `full_record` 给出。

预期文本如下。测试把每一段都作为字面量写在 `tests/f13_texts.py` 或 `tests/f13_blocks.py` 里。它们不导入任何消息，也从不读取原型文件，因为 `shop` 和 `datafile` 的消息是内部的（设计第 2 节，架构第 8 节）。

- `SHOP_47(P)` 和 `SHOP_47_ZH(P)` 是 F13 原型“In English”和“In Chinese”的输出，各 26 行，最后一行里用 P 代替 `C:\Users\Troy\recipe-menu\shopping\2026-W47.md`。
- `PROTOTYPE_FILE` 是 F13 原型“The saved file”的 `markdown` 块的字节：它的 37 行，每行以 LF 结尾，最后一行也是，用 UTF-8。
- `FILE_47` 是示例那一周用英文运行得到的文件，即下面的块，同样按字节计。
- `NO_DISHES(W)` 是 `The menu for W has no dishes, so there is nothing to buy. No file was saved.`，`NO_DISHES_ZH(W)` 是 `W 的菜单没有菜，所以没有要买的东西。没有保存文件。`。
- `FAIL(P, M)` 是失败的三行：P，然后是两个空格加 M 的英文，然后是 `No file was saved.`。`FAIL_ZH(P, M)` 用 M 的中文和 `没有保存文件。`。`LEFT(P, M, T)` 的第三行是 `No file was saved, but shop could not remove T. Delete it.`，`LEFT_ZH(P, M, T)` 的第三行是 `没有保存文件，但 shop 没能删除 T。请删除它。`。P 和 T 是完整路径。
- `NO_MENU(W)`、`NO_MENU_ZH(W)`、`NOT_A_WEEK(V)` 和 `NOT_A_WEEK_ZH(V)` 是 F11 测试方案里的那些，由 `tests/f11_texts.py` 的 `no_menu`、`no_menu_zh`、`not_a_week` 和 `not_a_week_zh` 给出。
- `PARENT(D)` 是消息 `The file cannot be written: "D" is not a folder.` 和 `无法写入文件：“D”不是文件夹。`，D 是一个相对于数据文件夹的文件夹的 `str`。
- `tests/f05_texts.py` 的 `HELP_EN_LINES` 和 `HELP_ZH_LINES` 是 F05 原型完整的两份帮助，各 21 行。

`FILE_47`：

```text
# Shopping list for 2026-W47

16 to 22 November 2026: 4 meals, 9 dishes.

## Vegetables and fruit

- [ ] Tomato 600 g
- [ ] Choy sum 1.5 kg
- [ ] Scallion 5 stalks
- [ ] Ginger 6 slices
- [ ] Garlic 11 cloves

## Meat and seafood

- [ ] Minced pork 100 g
- [ ] Chicken wings 1 kg

## Eggs, dairy, and tofu

- [ ] Egg 5 pieces
- [ ] Tofu 1 block

## Rice, flour, and oil

- [ ] Rice 640 g
- [ ] Noodles 200 g

## Seasonings

- [ ] Doubanjiang 15 ml
- [ ] White pepper to taste

## Other

- [ ] Cola 2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper
```

用例里 `cli` 的消息是 F05 设计 2.10 里带 `shop` 的文字。用例里读取函数的消息是 F09 和 F11 测试方案第 2 节里的那些：`FILE_MISSING`、`FILE_IS_FOLDER`、`MISSING_BRACE`、`FOLDER_MISSING`、`FOLDER_IS_FILE`、列出的 `NOT_A_RECIPE_ID`、`TOML_ENDING_NOT_SMALL`、`NOT_A_WEEK_NAME`、`UNKNOWN_RECIPE(recipe="tomato-eggs")`、`WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`、菜单的 `UNKNOWN_MEAL(meal="M", meals="S")`、菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`、`SERVINGS_TOO_FEW(servings=0)`、设置的 `UNKNOWN_MEAL(meal="supper")`、`FILE_WRITE_DENIED` 和 `FILE_WRITE_ERROR(reason="X")`。下面这些来自 F03 设计 2.9 和 2.10 以及 F08 设计 3.2。`tests/f07_texts.py` 和 `tests/f08_texts.py` 里已经有它们：

| 消息 | 英文 | 中文 |
| --- | --- | --- |
| `PANTRY_INGREDIENT(name="sesame oil")` | `Unknown ingredient "sesame oil".` | `未知食材“sesame oil”。` |
| `ITEM_NOT_A_TEXT` | `This item must be a text in quotation marks.` | `这一项必须是放在引号里的文字。` |
| `MISSING_KEY(key="en")` | `The key "en" is missing.` | `缺少键“en”。` |
| `FOLDER_CREATE_DENIED` | `The folder cannot be created: access is denied.` | `无法创建文件夹：没有访问权限。` |
| `FOLDER_CREATE_ERROR(reason="X")` | `The folder cannot be created. The system says: X` | `无法创建文件夹。系统提示：X` |

用例里的位置是 `line 11`（`第 11 行`）、`item 3`（`第 3 项`）、`ingredient 3`（`食材 3`）、`ingredient 22`（`食材 22`）、`servings`（`份数`）和 `meals`（`餐次`），菜单的位置是 `week`（`周次`）、`Monday dinner`（`周一晚餐`）和 `Saturday lunch`（`周六午餐`）。

用例使用 `tests/f13_support.py` 的两个构造函数，它们按设计 2.2 写成，不用 F13 的任何代码。`shop_list(F, week)` 用 `tests/f12_support.py` 的 `read_week` 读取这一周，`read_week` 把警告收集到一个列表里，并检查没有读取函数给出错误；然后给出用这些值调用 `build_shopping_list` 的结果。`shop_lines(S, L, P)` 给出清单 S 在语言 L 里、清单文件为 P 时 2.2 的输出的各行。它们是标题行、一个空行、各组，然后在 `pantry_used` 不为空时是一个空行和常备行，然后是一个空行和 `Saved P` 或 `已保存 P`。标题行是 `Shopping list for W, D: M, N` 或 `W 购物清单，D：M，N`。D 是 F06 用 L 写出的这一周的 `date_range`。M 是 `n meal` 或 `n meals`，或者 `n 餐`；N 是 `n dish` 或 `n dishes`，或者 `n 道菜`。各组是：每一组的分类名称（用 L），以及 F02 的 `format_table(rows, indent=2, min_widths=(width,))` 的各行。`width` 是整张清单里名称的一行的最大 `display_width`，每个名称用 `str.splitlines` 拆开。没有组的清单用 `There is nothing to buy.` 或 `没有要买的东西。` 代替各组。常备行是 `Not on the list, because they are in the pantry: X` 或 `常备，不用买：X`，X 是 F02 用 L 写出的名称的 `comma_list`。`shop_file(S, L)` 以同样方式给出 2.2 的文件的字节，每行以 LF 结尾。这两个构造函数把它们的模板作为字面量保存。F13-T12、F13-T13 和 F13-T14 先检查构造函数给出 `SHOP_47`、`SHOP_47_ZH`、`FILE_47`、`PROTOTYPE_FILE` 以及 B 到 H 块，所以在 F13-T29 和 F13-T30 使用它们之前，构造函数与原型和设计一致。

**哪个用例和原型比较。** F13-T12 把一次运行的输出与 `SHOP_47` 和 `SHOP_47_ZH` 比较，把中文运行的文件与 `PROTOTYPE_FILE` 逐字节比较，与 v0.1-S17 相同。F13-T11 运行设计的示例，它把中文文件与原型的各行比较。英文运行的文件没有原型，所以 `FILE_47` 是上面的块，测试经理按设计 2.2 的规则和设计 2.1 的示例构造它，并用模型检查过。E、F 和 H 块的文件同样是字面量。其他用例用 `shop_file` 从设计构造预期的字节。

A 到 H 块是用例提到、但没有原型显示的 `shop` 的输出。每个 `PS>` 行像原型那样给出不带 `--data` 的命令行，运行时带上 `--data` 和它所在块的文件夹。一个 `PS>` 行的输出是它后面的各行，直到并包括它的最后一行。一个空行把它和下一个 `PS>` 行隔开。每段输出都带退出码 0 和空的 err。每段输出的最后一行写出 P，即它所在用例的文件夹里清单文件的完整路径。

A 块是 F13-T01 输入 1 的输出，即在 `example` 上用英文直接调用 `run`，设置是全部三餐和 3 份，参数是 `Arguments(("2026-W47",))`：

```text
Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes

Vegetables and fruit
  Tomato          900 g
  Choy sum        1.75 kg
  Scallion        7 stalks
  Ginger          6 slices
  Garlic          14 cloves
Meat and seafood
  Minced pork     150 g
  Chicken wings   1 kg
Eggs, dairy, and tofu
  Egg             8 pieces
  Tofu            2 blocks
Rice, flour, and oil
  Rice            800 g
  Noodles         300 g
Seasonings
  Doubanjiang     23 ml
  White pepper    to taste
Other
  Cola            2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper

Saved P
```

B 块，一份新的示例副本里的 B 周：

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 4 meals, 5 dishes

Vegetables and fruit
  Choy sum      2.5 kg
  Scallion      3 stalks
  Ginger        3 slices
  Garlic        17 cloves
Meat and seafood
  Pork belly    500 g
  Minced pork   100 g
Eggs, dairy, and tofu
  Tofu          1 block
Rice, flour, and oil
  Rice          320 g
Seasonings
  Rock sugar    30 g
  Doubanjiang   15 ml

Not on the list, because they are in the pantry: Cooking oil, Salt, Soy sauce, Sichuan pepper

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：4 餐，5 道菜

蔬菜水果
  菜心         2.5 kg
  葱           3 根
  姜           3 片
  大蒜         17 瓣
肉类水产
  五花肉       500 g
  猪肉末       100 g
蛋奶豆制品
  豆腐         1 块
米面粮油
  大米         320 g
调味品
  冰糖         30 g
  郫县豆瓣酱   15 ml

常备，不用买：食用油、盐、生抽、花椒

已保存 P
```

C 块，S16 文件夹里的 v0.1-S16：

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish

Vegetables and fruit
  Tomato     450 g
  Scallion   2 stalks
Eggs, dairy, and tofu
  Egg        5 pieces

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：1 餐，1 道菜

蔬菜水果
  番茄   450 g
  葱     2 根
蛋奶豆制品
  鸡蛋   5 个

常备，不用买：食用油、盐、糖

已保存 P
```

D 块，一份新的示例副本里的鸡翅换行 S，每个 S 都一样：

```text
PS> recipe-menu shop 2026-W47
Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes

Vegetables and fruit
  Tomato         600 g
  Choy sum       1.5 kg
  Scallion       5 stalks
  Ginger         6 slices
  Garlic         11 cloves
Meat and seafood
  Minced pork    100 g
  Chicken        1 kg
  wings
Eggs, dairy, and tofu
  Egg            5 pieces
  Tofu           1 block
Rice, flour, and oil
  Rice           640 g
  Noodles        200 g
Seasonings
  Doubanjiang    15 ml
  White pepper   to taste
Other
  Cola           2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper

Saved P
```

E 块，一份新的示例副本里的白开水周。`FILE_E` 和 `FILE_E_ZH` 是每次运行之后的文件：

```text
PS> recipe-menu shop 2026-W50
Shopping list for 2026-W50, 7 to 13 December 2026: 1 meal, 1 dish

There is nothing to buy.

Saved P

PS> recipe-menu shop 2026-W50 --lang zh
2026-W50 购物清单，2026年12月7日至13日：1 餐，1 道菜

没有要买的东西。

已保存 P
```

```text
# Shopping list for 2026-W50

7 to 13 December 2026: 1 meal, 1 dish.

There is nothing to buy.
```

```text
# 2026-W50 购物清单

2026年12月7日至13日：1 餐，1 道菜。

没有要买的东西。
```

F 块，一份新的示例副本里的鸡蛋周。`FILE_F` 和 `FILE_F_ZH` 是每次运行之后的文件：

```text
PS> recipe-menu shop 2026-W51
Shopping list for 2026-W51, 14 to 20 December 2026: 1 meal, 2 dishes

There is nothing to buy.

Not on the list, because they are in the pantry: Egg, Salt

Saved P

PS> recipe-menu shop 2026-W51 --lang zh
2026-W51 购物清单，2026年12月14日至20日：1 餐，2 道菜

没有要买的东西。

常备，不用买：鸡蛋、盐

已保存 P
```

```text
# Shopping list for 2026-W51

14 to 20 December 2026: 1 meal, 2 dishes.

There is nothing to buy.

Not on the list, because they are in the pantry: Egg, Salt
```

```text
# 2026-W51 购物清单

2026年12月14日至20日：1 餐，2 道菜。

没有要买的东西。

常备，不用买：鸡蛋、盐
```

G 块，一份带有 `tests/f12_support.py` 的 `s18_changes` 改动的新示例副本里的 v0.1-S18：

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 5 meals, 5 dishes

Vegetables and fruit
  Tomato         900 g
  Scallion       5 stalks + 1 bunch
  Ginger         3 slices
Meat and seafood
  Pork belly     500 g
Eggs, dairy, and tofu
  Egg            8 pieces
Rice, flour, and oil
  Noodles        400 g
Seasonings
  Soy sauce      30 ml + 10 g
  Rock sugar     30 g
  White pepper   to taste

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：5 餐，5 道菜

蔬菜水果
  番茄       900 g
  葱         5 根 + 1 把
  姜         3 片
肉类水产
  五花肉     500 g
蛋奶豆制品
  鸡蛋       8 个
米面粮油
  面条       400 g
调味品
  生抽       30 ml + 10 g
  冰糖       30 g
  白胡椒粉   适量

常备，不用买：食用油、盐、糖

已保存 P
```

H 块，一份新的示例副本里的米饭周 2026-W49。`FILE_H` 和 `FILE_H_ZH` 是每次运行之后的文件。`H(W, D)`、`H_ZH(W, D)`、`FILE_H(W, D)` 和 `FILE_H_ZH(W, D)` 是这些文本，其中用周 W 代替 `2026-W49`，用该文本语言的日期 D 代替 2026-W49 的日期：

```text
PS> recipe-menu shop 2026-W49
Shopping list for 2026-W49, 30 November to 6 December 2026: 1 meal, 1 dish

Rice, flour, and oil
  Rice   160 g

Saved P

PS> recipe-menu shop 2026-W49 --lang zh
2026-W49 购物清单，2026年11月30日至12月6日：1 餐，1 道菜

米面粮油
  大米   160 g

已保存 P
```

```text
# Shopping list for 2026-W49

30 November to 6 December 2026: 1 meal, 1 dish.

## Rice, flour, and oil

- [ ] Rice 160 g
```

```text
# 2026-W49 购物清单

2026年11月30日至12月6日：1 餐，1 道菜。

## 米面粮油

- [ ] 大米 160 g
```

用例里各周的日期如下，先英文后中文：2026-W01 是 `29 December 2025 to 4 January 2026` 和 `2025年12月29日至2026年1月4日`，2026-W23 是 `1 to 7 June 2026` 和 `2026年6月1日至7日`，2026-W47 是 `16 to 22 November 2026` 和 `2026年11月16日至22日`，2026-W48 是 `23 to 29 November 2026` 和 `2026年11月23日至29日`，2026-W49 是 `30 November to 6 December 2026` 和 `2026年11月30日至12月6日`，2026-W53 是 `28 December 2026 to 3 January 2027` 和 `2026年12月28日至2027年1月3日`，2027-W01 是 `4 to 10 January 2027` 和 `2027年1月4日至10日`。

用例分在这些文件里，让每个文件都在 R06 的 500 行之内：

| 文件 | 用例 |
| --- | --- |
| `tests/test_f13_command.py` | F13-T01 和 F13-T02 |
| `tests/test_f13_replace.py` | F13-T03 到 F13-T06 |
| `tests/test_f13_replace_errors.py` | F13-T07 到 F13-T10 |
| `tests/test_f13_shop.py` | F13-T11 到 F13-T14 |
| `tests/test_f13_weeks_and_reads.py` | F13-T15 和 F13-T16 |
| `tests/test_f13_stops.py` | F13-T17 和 F13-T18 |
| `tests/test_f13_failures.py` | F13-T19 到 F13-T21 |
| `tests/test_f13_cli.py` | F13-T22 |
| `tests/test_f13_integration.py` | F13-T23 到 F13-T28 |
| `tests/test_f13_random.py` | F13-T29，带它的生成器 |
| `tests/test_f13_performance.py` | F13-T30 |
| `tests/f13_support.py` | 没有测试。`EXISTS`、`ShopFaults` 和 `shop_faults`（见上文）。`folder_link`，在 Windows 上创建目录联接，在 Linux 上创建符号链接。`move_message(base)`，它在 `base` 里把自己的一个文件移到自己的一个空文件夹上，取得系统的错误对应的 3.1 那一行的消息，再把两者删掉。`shop_list`、`shop_lines` 和 `shop_file`（见上文）。`pt01_shop`（第 3 节）。F13 的命名改动：米饭周、白开水周、鸡蛋周、鸡翅换行、肉类换行、缺少的名称、shopping 是文件、打过勾的清单、旧清单和旧的临时文件。`held_open(path)`，一个用 `open(path, "rb")` 让文件保持打开的上下文管理器。它复用 `tests/f08_support.py` 的 `Faults`、`Rule`、`rule`、各个效果、`call_main`、`system_message`、`dangling_link`、`tree` 和 `full_record`，`tests/f12_support.py` 的 `read_week` 和 `s16_folder`，`tests/f11_support.py` 的 `menu_text`、`assert_failed` 和命名的改动，以及约定里提到的 `tests/f03_support.py`、`tests/f05_support.py`、`tests/f07_support.py`、`tests/f07_changes.py`、`tests/f09_support.py` 和 `tests/f10_support.py` 的辅助函数。`tests/f12_support.py` 有 500 行，正是 R06 的上限，所以 F13 的辅助函数放在这里。按测试经理的估计，这个文件约有 400 行，在 R06 的 500 行之内。 |
| `tests/f13_texts.py` | 没有测试。`SHOP_47`、`SHOP_47_ZH`、`PROTOTYPE_FILE`、`FILE_47`、`NO_DISHES`、`FAIL`、`LEFT`、`PARENT` 以及它们的中文形式，都是字面量。它复用 `tests/f05_texts.py` 的 `HELP_EN_LINES` 和 `HELP_ZH_LINES`，`tests/f07_texts.py`、`tests/f08_texts.py` 和 `tests/f09_texts.py` 的消息，`tests/f09_texts.py` 的 `stop`、`out` 和 `err`，以及 `tests/f11_texts.py` 的 `no_menu`、`not_a_week` 和它们的中文形式。 |
| `tests/f13_blocks.py` | 没有测试。A 到 H 块和它们的文件，都是字面量，以及 `H`、`H_ZH`、`FILE_H` 和 `FILE_H_ZH`。它们单独成一个文件，因为加上它们，`tests/f13_texts.py` 会超过 R06 的 500 行。 |
| `tests/conftest.py` | 不变。F13 使用它的 fixture `example_folder`，以及 pytest 的 `tmp_path`、`monkeypatch` 和 `record_property`。 |

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F13-T01 | 单元 | `SHOP_COMMAND`、`SHOP_COMMAND.run`、`main` | 2.1 的示例。`SHOP_COMMAND` 的词是 `shop`，用法是 `shop [WEEK]` 和 `shop [周]`，帮助行是 F05 原型里的那一行，有不重复的可选参数 `WEEK`，没有选项，用 `FolderUse.READ`。它的 `run` 从参数和 `context.today` 取得周，用 `context.settings` 的餐次和份数读取菜单，用 `context.lang` 写出，从不用 `context.settings` 的语言，两次调用之间不保留状态。`main` 通过 `commands=` 得到的 v0.1 八个命令的帮助，就是 F05 原型完整的两份帮助，有 21 行，第二列从第 21 列之后开始。在真正 `COMMANDS` 的帮助里，不管之后的功能加上什么行，`shop` 那一行的文字都从 `--lang en\|zh` 的文字所在的那一列开始（2.1，选择 1 到 5）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`。在 `help_lines` 里，调用 `main` 时还用 `commands=` 传入 v0.1 的八个命令，按帮助里的顺序，从 `INIT_COMMAND` 到 `MENU_SHOW_COMMAND`，然后是 `SHOP_COMMAND`，因为这 21 行只在 `COMMANDS` 里只有这八个命令时成立，而 F14 加上 `menu suggest`。`# raises` 那一行在 `pytest.raises(UsageError)` 里运行，用相同值的新 `Context` 和新的流。然后各用新的流：1. 用 `Context(Lang.EN, example, Settings(Lang.ZH, tuple(Meal), 3), out, err, date(2030, 1, 1))` 和 `Arguments(("2026-W47",))` 调用 `run`。2. 用 `Context(Lang.ZH, example, Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2), out, err, date(2026, 11, 17))` 和 `Arguments(())` 调用 `run`。3. 用 `Context(Lang.EN, example, Settings(Lang.EN, (Meal.DINNER,), 5), out, err, date(2026, 11, 17))` 和 `Arguments(())` 调用 `run`。4. 示例里带 `Arguments(("next",))` 的那次运行，再运行两次。5. 通过 `call`、像 `help_lines` 那样用 `commands=` 传入 v0.1 的八个命令，运行 `--help` 和 `--help --lang zh`。6. 通过 `call`、用真正的 `COMMANDS` 运行 `--help` 和 `--help --lang zh`。 | 示例的每个断言都成立，`# raises` 那一行抛出 `UsageError`，之后它的两个流都为空，`shopping/` 里只有 `2026-W47.md`，内容是示例那次运行写下的字节。1. 0，out 是 A 块的各行，P 为 `example/shopping/2026-W47.md`，err 为空。每道没写份数的菜按 3 份算，所以清单里有 `Tomato 900 g`、`Choy sum 1.75 kg`、`Tofu 2 blocks` 和 `Doubanjiang 23 ml`。文件以 `# Shopping list for 2026-W47\n` 开头，并有 `- [ ] Tomato 900 g` 这一行。2. 0，out 是 `SHOP_47_ZH(P)`，err 为空，文件是 `PROTOTYPE_FILE`：2026-11-17 所在的周是 2026-W47。3. 1，out 为空，err 是 `STOP(menus/2026-W47.toml, Saturday lunch, 菜单的 UNKNOWN_MEAL(meal="lunch", meals="dinner"))`。文件保留 2 的字节。4. 每次运行都给出 0、out `SHOP_47(P)` 和空的 err，每次之后文件都是 `FILE_47`。5. 退出码 0，err 为空，out 是 `HELP_EN_LINES` 和 `HELP_ZH_LINES` 的各行：各 21 行，`menu show` 那一行之后紧跟着 `  shop [WEEK]        Make the shopping list of a week menu.` 和 `  shop [周]          生成一个周菜单的购物清单。`。6. 退出码 0，err 为空。out 里有一行以 `  shop [WEEK] ` 开头、以 `Make the shopping list of a week menu.` 结尾，中文里有一行以 `  shop [周] ` 开头、以 `生成一个周菜单的购物清单。` 结尾。它的文字与以 `  --lang en\|zh` 开头的那一行的文字从同一个显示列开始。 |
| F13-T02 | 单元 | `SHOP_COMMAND.run` | 2.2 的第 1 步。`run` 在碰磁盘或写任何输出之前，用 `week_from_argument` 把 `WEEK` 的值变成一个周。不是周的值抛出 `UsageError(NOT_A_WEEK, None, week=value)`，它没有提示。`this`、`next`、ISO 周和没有值都能通过（2.1 的错误，选择 2）。 | 1 和 2 的每次调用都用新的流和 `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`，在 `shop_faults(tmp_path)` 里。1. 在 `pytest.raises(UsageError)` 里：对 `"2026-W99"`、`"Next"`、`"THIS"`、`""`、`" 2026-W47"`、`"2026-W47\n"`、`"2026-w47"`、`"2026-W7"`、`"2025-W53"`、`"2026-W00"`、`"this week"` 和用全角数字写 2026 的 `"\uff12\uff10\uff12\uff16-W47"` 中的每个 V，用 `Arguments((V,))`。2. 对 `()`、`("this",)`、`("next",)`、`("2026-W47",)`、`("2026-W53",)` 和 `("0001-W01",)` 中的每个 V，用 `Arguments(V)`。3. 1 的各次调用，但 context 在带旧清单的 `example` 上，在 `shop_faults(example.root)` 里。 | 1. 每个错误的 `text(Lang.EN)` 是 `NOT_A_WEEK(V)`，`text(Lang.ZH)` 是 `NOT_A_WEEK_ZH(V)`，`hint` 是 `None`。每次调用之后两个流都为空，故障工具的记录和列出记录都为空。2. 没有调用抛出异常。每次都给出 1、空的 out 和 err `STOP(catalog.toml, FILE_MISSING)`，`tmp_path / "missing"` 仍然不存在。3. 1 的那些错误，流为空，记录为空，没有列出。旧清单保留 `b"old\n"`。 |
| F13-T03 | 单元 | `replace_file` | 3.1 的示例：新的 `shopping/` 和新文件、被替换的文件、文件路径上有一个两个系统都拒绝替换的文件夹、`shopping` 是文件，以及三次错误的调用（3.1）。 | 示例的各行，`tmp` 是空文件夹 `tmp_path / "tmp"`。每行 `# raises` 在 `pytest.raises` 里运行，带它写出的错误。 | 示例的每个断言都成立，三行 `# raises` 各自抛出它的错误。之后，`tmp` 的树里只有 `recipe-menu`、`recipe-menu/shopping`、内容为 `"# 2\n番茄 600 g\n".encode("utf-8")` 的 `recipe-menu/shopping/2026-W47.md`、空文件夹 `recipe-menu/shopping/2026-W48.md`、`other` 和空文件 `other/shopping`。没有条目以 `.tmp` 结尾。 |
| F13-T04 | 单元 | `replace_file` | 第 1 步。错误的调用在碰磁盘之前抛出：根之外的路径、根本身、相对路径，以及 UTF-8 无法编码的文字，文件所在的文件夹不存在时也一样（3.1 第 1 步和错误）。 | 没有 `F.shopping` 的 `F`，每次调用都在 `shop_faults(base)` 里：1. `replace_file(F, base / "elsewhere.md", "")`。2. `replace_file(F, F.root, "")`。3. `replace_file(F, Path("shopping", "2026-W47.md"), "")`。4. `replace_file(F, Q, "\udc80")`。5. `replace_file(F, Q, "ok\n\ud800")`。6. `replace_file(F, F.root / "a" / "b.md", "\udc80")`。 | 1 到 3 抛出 `ValueError`，4 到 6 抛出 `UnicodeEncodeError`。每次调用之后，记录和列出记录都为空，`base` 的树和调用之前相同：`F.shopping` 和 `F.root / "a"` 都不存在。 |
| F13-T05 | 单元 | `replace_file` | 一次成功调用的第 2 到第 5 步。文件所在的文件夹处什么都没有时，得到那一个文件夹，不创建上级。先删除 `temp` 处的条目，不存在也不算错误。调用以 `x` 模式打开 `temp` 一次，写入文字的 UTF-8 字节，没有字节顺序标记，保留文字的换行，空文字也一样，再把 `temp` 移到文件上，从而创建或替换它。它什么都不读、不列出，给出 `CREATED`。根里的任何文件夹都可以，指向文件夹的链接也可以（3.1 第 2 到 5 步，C 点）。 | `F` 和文字 `"# 1\n"`，除非输入另有说明，每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base)` 里：1. 空的 `F.shopping`，Q。2. 没有 `F.shopping`，Q。3. `F.shopping` 里有内容为 `b"old\n"` 的 Q，文字是 `"# 2\n番茄 600 g\n"`。4. `F.shopping` 里有内容为 `b"old\n"` 的 Q 和内容为 `b"half\n"` 的 T。5. 空的 `F.shopping`，文字是 `""`。6. 空的 `F.shopping`，文字是 `"a\r\nb\n"`。7. `F.menus` 里有内容为 `b'week = "2026-W47"\n'` 的 `2026-W47.toml`，路径是 `F.menu_file("2026-W47")`，文字是 `'week = "2026-W47"\n\n[monday]\n'`，就像 F14 的 `menu suggest` 将要替换菜单那样。8. 路径 `F.root / "notes.md"`。9. `F.shopping` 是指向空文件夹 `base / "synced"` 的链接，用 `folder_link` 创建，Q。10. `F.shopping` 里有内容为 `b"other\n"` 的 `2026-W48.md` 和内容为 `b"x\n"` 的 `notes.txt`，Q。 | 每次调用给出的结果都等于 `FileCreation(FileOutcome.CREATED)`。1、3 到 6、9 和 10 的记录是 `unlink T`、`open T` 和 `move T Q`，列出记录为空。2. `mkdir S` 然后是 1 的记录，`F.shopping` 是只有 Q 的文件夹。7. `unlink recipe-menu/menus/2026-W47.toml.tmp`、`open recipe-menu/menus/2026-W47.toml.tmp` 和 `move recipe-menu/menus/2026-W47.toml.tmp recipe-menu/menus/2026-W47.toml`。8. 同样，换成 `recipe-menu/notes.md.tmp` 和 `recipe-menu/notes.md`。没有记录里有 `read`。之后调用的文件内容是：1、2、4 以及 8 到 10 为 `b"# 1\n"`。3 为 `"# 2\n番茄 600 g\n".encode("utf-8")`，没有 `b"\xef\xbb\xbf"`。5 为 `b""`。6 为 `b"a\r\nb\n"`。7 为 `b'week = "2026-W47"\n\n[monday]\n'`。4 里 T 不在了。9 里 `base / "synced"` 只有 `2026-W47.md`，`F.shopping` 仍然是链接。10 里另外两个条目保留它们的字节和修改时间。每个输入里，`base` 下都没有以 `.tmp` 结尾的条目。 |
| F13-T06 | 单元 | `replace_file` | 文件所在的文件夹处是文件夹以外的东西时的第 2 步：文件、悬空链接，或者更上层的文件。调用给出带 `PARENT_NOT_A_FOLDER` 的 `FAILED`，其中 `folder` 是 `str(folder.relative(parent))`，问题的文件是要写的文件。它什么都不碰（3.1 第 2 步，C 点）。 | 每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base)` 里，文字是 `"x"`：1. `F.shopping` 是内容为 `b"x\n"` 的文件，Q。2. `F.shopping` 处是悬空链接，Q。3. `F.root / "notes.md"` 是内容为 `b"x\n"` 的文件，路径是 `F.root / "notes.md" / "2026-W47.md"`。4. `F.root / "a"` 是有空文件 `b` 的文件夹，路径是 `F.root / "a" / "b" / "c.md"`。 | 每次调用都给出 `FAILED`，`left` 为空，问题是：1. `shopping/2026-W47.md: PARENT(shopping)`。2. 同上。3. `notes.md/2026-W47.md: PARENT(notes.md)`。4. `a/b/c.md: PARENT(a/b)`，其中 `a/b` 是 `str(Path("a", "b"))`，所以在 Windows 上是 `a\b`。记录为空，`base` 的完整记录在调用前后相同。 |
| F13-T07 | 单元 | `replace_file` | 创建文件夹失败时的第 2 步。3.1 表格的前两行给出结果：`PermissionError` 给出 `FOLDER_CREATE_DENIED`，其他 `OSError`（包括 `FileExistsError`）给出带错误的 `strerror` 的 `FOLDER_CREATE_ERROR`，`strerror` 为 `None` 或空时用错误类的名称。问题写出要写的文件，而不是它的文件夹。失败的探查算作假。Ctrl+C 继续传递，没有要删除的东西（3.1 第 2 步和它的错误表，架构师说明 1）。 | 没有 `F.shopping` 的 `F`、Q 和文字 `"x"`，除非输入另有说明，每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base, *rules)` 里：1. `mkdir F.shopping: DENIED`。2. `mkdir F.shopping: IO`。3. `mkdir F.shopping: EXISTS`。4. `mkdir F.shopping: OSError()`。5. `mkdir F.shopping: TimeoutError()`。6. `mkdir F.shopping: EMPTY_IO`。7. 没有规则，也没有 `F.root`。8. 没有规则，路径是 `F.root / U / "x.md"`，U 在 Windows 上是 `a?b`，在 Linux 上是 256 个 `a`。9. `mkdir F.shopping: CTRL_C`，在 `pytest.raises(KeyboardInterrupt)` 里。 | 1 到 8 给出 `FAILED`，`left` 为空，问题是：1. `shopping/2026-W47.md: FOLDER_CREATE_DENIED`。2. `shopping/2026-W47.md: FOLDER_CREATE_ERROR(reason="Input/output error")`。3. 同样，`reason="File exists"`，不是 `FOLDER_EXISTS`。4. 同样，`reason="OSError"`。5. 同样，`reason="TimeoutError"`。6. 同样，`reason="OSError"`。7. `shopping/2026-W47.md` 和调用之前取得的 `system_message("folder", F.shopping)`，即带系统对上层文件夹不存在给出的原因的 `FOLDER_CREATE_ERROR`。8. `U/x.md` 和调用之前取得的 `system_message("folder", F.root / U)`。9. 调用抛出 `KeyboardInterrupt`。1 到 7 和 9 的记录只有 `mkdir S`，8 的记录只有 `mkdir recipe-menu/U`。每次调用前后 `base` 的树相同。 |
| F13-T08 | 单元 | `replace_file` | `temp` 存在之前的第 3 步和第 4 步。第 3 到 5 步的那几行给出结果：`PermissionError` 给出 `FILE_WRITE_DENIED`，其他 `OSError`（包括 `FileExistsError`）给出带原因的 `FILE_WRITE_ERROR`，从不给出 `EXISTS` 或 `FILE_EXISTS`。删除旧 `temp` 失败和打开失败都没有创建任何东西，所以调用什么都不删除，别的程序创建的 `temp` 留着。旧文件保留它的字节（3.1 第 3 步和第 4 步、它的错误表，架构师说明 1）。 | `F` 的 `F.shopping` 里有内容为 `b"old\n"` 的 Q，1 和 2 里还有内容为 `b"half\n"` 的 T。文字是 `"new\n"`。每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base, *rules)` 里：1. `unlink T: DENIED`。2. `unlink T: IO`。3. `open T: DENIED`。4. `open T: IO`。5. `open T: EXISTS`。6. `open T: race`。7. `open T: TimeoutError()`。8. `open T: EMPTY_IO`。 | 每次调用都给出 `FAILED`，`left` 为空，问题是：1. `shopping/2026-W47.md: FILE_WRITE_DENIED`。2. `shopping/2026-W47.md: FILE_WRITE_ERROR(reason="Input/output error")`。3. `FILE_WRITE_DENIED`。4. `FILE_WRITE_ERROR(reason="Input/output error")`。5. `FILE_WRITE_ERROR(reason="File exists")`。6. `FILE_WRITE_ERROR(reason="File exists")`：独占打开一个已有的文件时，两个系统都给出这个 `strerror`。测试经理在 Troy 的电脑上检查过，Linux 给出 C 库对 `EEXIST` 的文字，是同样的词。7. `FILE_WRITE_ERROR(reason="TimeoutError")`。8. `FILE_WRITE_ERROR(reason="OSError")`。1 和 2 的记录只有 `unlink T`，T 保留 `b"half\n"`。3 到 8 的记录是 `unlink T` 和 `open T`，没有第二次 `unlink`。3 到 5、7 和 8 里 T 不存在，6 里它是别的程序写的 `b"mine\n"`。每个输入里 Q 都保留 `b"old\n"`，`F.shopping` 里除了 Q 以及 1、2 和 6 里的 T 之外没有别的条目。 |
| F13-T09 | 单元 | `replace_file` | 打开之后。`temp` 从打开成功的那一刻起算作已创建。写入、关闭或移动失败时给出 `FAILED`，调用先删除 `temp`。删除失败时把 `temp` 的完整路径放进 `left`。调用用一次 `write` 写入，空文字也一样。旧文件只通过移动改变，所以它保留自己的字节。调用创建的文件夹在之后某一步失败时留着（3.1 第 4 步和第 5 步、它的错误表之后的那一段，C 点）。 | `F` 的 `F.shopping` 里有内容为 `b"old\n"` 的 Q，文字是 `"0123456789\n"`，除非输入另有说明。每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base, *rules)` 里：1. `write T: NO_SPACE`。2. `write T: DENIED`。3. `write T: IO` 和 `unlink T: later DENIED`。4. `write T: NO_SPACE`，文字是 `""`。5. `close T: NO_SPACE`。6. `close T: DENIED` 和 `unlink T: later IO`。7. `move T: DENIED`。8. `move T: IO`。9. `move T: OSError()`。10. `move T: DENIED` 和 `unlink T: later DENIED`。11. 没有规则，`F.shopping` 里用空文件夹 `2026-W47.md` 代替 Q。12. 没有 `F.shopping`，`write T: NO_SPACE`。13. 没有 `F.shopping`，`move T: DENIED`。 | 每次调用都给出 `FAILED`，问题和 `left` 是：1. `shopping/2026-W47.md: FILE_WRITE_ERROR(reason="No space left on device")` 和 `()`。2. `FILE_WRITE_DENIED` 和 `()`。3. `FILE_WRITE_ERROR(reason="Input/output error")` 和 `(T,)`，T 为完整路径。4. 1 的结果。5. 1 的结果。6. `FILE_WRITE_DENIED` 和 `(T,)`。7. `FILE_WRITE_DENIED` 和 `()`。8. `FILE_WRITE_ERROR(reason="Input/output error")` 和 `()`。9. `FILE_WRITE_ERROR(reason="OSError")` 和 `()`。10. `FILE_WRITE_DENIED` 和 `(T,)`。11. `shopping/2026-W47.md` 和调用之前取得的 `move_message(base)`：在 Windows 上是 `FILE_WRITE_DENIED`，在 Linux 上是 `FILE_WRITE_ERROR(reason="Is a directory")`，以及 `()`。12. 1 的结果。13. 7 的结果。1、2、4 和 5 的记录是 `unlink T`、`open T` 和 `unlink T`，T 不在了。3 和 6 的记录相同：3 里 T 是 `b"01234"`，6 里是 `b"0123456789\n"`。7 到 9 和 11 的记录是 `unlink T`、`open T`、`move T Q` 和 `unlink T`，T 不在了。10 的记录相同，T 是 `b"0123456789\n"`。12 和 13 的记录是 `mkdir S` 然后是 1 或 7 的记录，`F.shopping` 留着，是一个空文件夹。1 到 10 里 Q 保留 `b"old\n"`，11 里它仍然是一个空文件夹。在 Windows 上，只有调用关闭了 T 之后系统才能删除或移动它，所以 1、2、4、5、7 到 9 和 11 也检查了调用会关闭文件。 |
| F13-T10 | 单元 | `replace_file` | 中断或缺陷。打开之后任何不是 `OSError` 的异常，比如 Ctrl+C 的 `KeyboardInterrupt` 或缺陷的异常，都在 `finally` 块里做同样的删除，然后继续传递，所以调用不给出结果。在 `open` 里面、系统已创建 `temp` 但调用还没拿到它时按下 Ctrl+C，会留下一个空的 `temp`，下一次调用在第 3 步删除它。打开之前的 Ctrl+C 继续传递，没有要删除的东西。旧文件保留它的字节（3.1、它的错误表之后的那一段，选择 6）。 | `F` 的 `F.shopping` 里有内容为 `b"old\n"` 的 Q，文字是 `"0123456789\n"`。每个输入都有它自己的 `base`，每次调用都在 `shop_faults(base, *rules)` 里，并在带它的规则的异常的 `pytest.raises` 里：1. `write T: BUG`。2. `write T: CTRL_C`。3. `close T: CTRL_C`。4. `move T: CTRL_C`。5. `write T: CTRL_C` 和 `unlink T: later DENIED`。6. `write T: CTRL_C` 和 `unlink T: later CTRL_C`。7. `open T: after CTRL_C`。8. 7 之后，用同一个 `F`、不带规则：`replace_file(F, Q, "# 1\n")`，不在 `pytest.raises` 里。9. 内容为 `b"half\n"` 的 T，`unlink T: CTRL_C`。 | 1 到 7 和 9 抛出它的规则的异常。1 到 3 的记录是 `unlink T`、`open T` 和 `unlink T`，4 的记录是 `unlink T`、`open T`、`move T Q` 和 `unlink T`，T 不在了。5 和 6 的记录与 1 相同，T 是 `b"01234"`。7. 记录是 `unlink T` 和 `open T`，没有第二次 `unlink`，T 是一个空文件。8. `FileCreation(FileOutcome.CREATED)`，记录是 `unlink T`、`open T` 和 `move T Q`，T 不在了，Q 是 `b"# 1\n"`。9. 记录只有 `unlink T`，T 保留 `b"half\n"`。1 到 7 和 9 里 Q 保留 `b"old\n"`。 |
| F13-T11 | 功能 | `recipe-menu shop`、`main` | 按顺序、用真正的命令运行 2.2 的示例：创建 `shopping/` 的英文清单、原型的中文输出和文件、两种语言的“No menu, or an empty menu”、错误的周、保留文件的“A menu with a mistake”，以及 `shopping` 是文件（2.2，选择 2 到 7）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`，以及示例的 `run`，它调用 `main` 时不传 `commands`。 | 示例的每个断言都成立。 |
| F13-T12 | 功能 | `recipe-menu shop`、`main` | 在 `main` 上运行 v0.1-S17，以及完整的 F13 原型“In English”、“In Chinese”和“The saved file”。一次运行用它的语言保存清单，并替换这一周的文件，所以打过勾的清单会丢掉勾，旧的临时文件在一次运行之后不在了。之后 `shopping\` 里只有这一周的文件。按显示宽度算，两种语言里每一组的数量都从同一列开始（v0.1-S25）。原型里的 `shop next` 和中文设置给出同样的结果（选择 4 到 6，C 点）。 | X 是一份没有 `shopping/` 的新示例副本。1. 在 X 里 `shop 2026-W47`。2. 在 X 里 `shop 2026-W47 --lang zh`。3. 在 X 里放打过勾的清单和旧的临时文件，然后在 X 里 `shop next`。4. 在 X 里 `shop next --lang zh`。5. 在一份带中文设置和空的 shopping 的新示例副本 Y 里：`shop 2026-W47`，然后 `shop 2026-W47 --lang en`。6. 构造函数：用 EN 和 ZH、X 的 P，对 `shop_list(X, IsoWeek(2026, 47))` 调用 `shop_lines` 和 `shop_file`。 | 1. `(0, out SHOP_47(P))`。`X/shopping` 是一个新文件夹，只有 `2026-W47.md`，内容是 `FILE_47`：UTF-8，没有字节顺序标记，LF 换行，有 14 行以 `- [ ] ` 开头。2. `(0, out SHOP_47_ZH(P))`，文件逐字节是 `PROTOTYPE_FILE`。`X/shopping` 只有这个文件。英文输出里每个数量之前的部分的 `display_width` 是 18，中文输出里是 15：缩进 2，最宽的名称 `Chicken wings` 或 `郫县豆瓣酱` 是 13 或 10，再加 3。3. `(0, out SHOP_47(P))`。文件是 `FILE_47`，没有 `- [x]`，T 不在了，`X/shopping` 只有 `2026-W47.md`。4. `(0, out SHOP_47_ZH(P))`，文件是 `PROTOTYPE_FILE`。5. `(0, out SHOP_47_ZH(P))`，P 为 Y 里的路径，文件是 `PROTOTYPE_FILE`。然后 `(0, out SHOP_47(P))`，文件是 `FILE_47`。6. `SHOP_47(P)` 和 `SHOP_47_ZH(P)` 的各行，以及 `FILE_47` 和 `PROTOTYPE_FILE` 的字节。 |
| F13-T13 | 功能 | `recipe-menu shop` | 其他周的选择 4。组标题没有缩进。每一行是两个空格、补齐到整张清单最宽名称的名称、三个空格和数量，所以每一周得到它自己名称的宽度。各组和各行按目录的顺序。有换行的名称占两行，数量跟在它的第一行之后，每个标题都留在原位。有换行的分类名称给出两行的标题。不写任何警告。常备行按 `pantry_used`，菜单没用到常备食材时，终端和文件里都没有常备行（选择 4、5 和 8）。 | 1. 一份新的示例副本里的 B 周：B 块的两行。2. S16 文件夹：C 块的两行。3. 对每个 S，一份新的示例副本里的鸡翅换行 S：D 块的那一行。4. 一份新的示例副本里的肉类换行：`shop 2026-W47`。5. 一份新的示例副本里的米饭周 2026-W49：H 块的两行。6. 用 `shop_list` 得到 1、2、3 和 5 的清单，调用构造函数。 | 1 到 3 和 5。每一行给出它在 B、C、D 或 H 块里的输出，退出码 0，err 为空。1. 英文里数量从缩进之后第 14 列开始，跟在 `Doubanjiang` 之后；中文里从第 13 列开始，跟在 `郫县豆瓣酱` 之后。`Pork belly` 在 `Minced pork` 之前。不写出 `red-braised-pork` 的警告。英文那一行之后，文件以 `# Shopping list for 2026-W48\n\n23 to 29 November 2026: 4 meals, 5 dishes.\n` 开头；每一行之后，文件都是这张清单用那一行的语言的 `shop_file`。2. 数量从缩进之后第 11 列和第 7 列开始，跟在 `Scallion` 和 `番茄` 之后，计数是 `1 meal, 1 dish` 和 `1 餐，1 道菜`。每个文件都是这张清单用它的语言的 `shop_file`。3. 每个 S 的输出都相同，其中没有 U+000D 也没有 U+2028，`  wings` 这一行末尾没有空格。文件是这张清单用英文的 `shop_file`，所以 S 为 `\n` 时，`FILE_47` 里 `- [ ] Chicken wings 1 kg` 的位置变成 `- [ ] Chicken` 和 `wings 1 kg` 两行。4. `(0, out L)`，L 是把 `SHOP_47(P)` 里的 `Meat and seafood` 一行换成 `Meat` 和 `and seafood` 两行。文件是把 `FILE_47` 里的 `## Meat and seafood` 一行换成 `## Meat` 和 `and seafood` 两行。5. 输出和文件里都没有常备行，文件是 `FILE_H` 和 `FILE_H_ZH`。6. B、C、D 和 H 块的各行，以及 1、2、3 和 5 的文件。 |
| F13-T14 | 功能 | `recipe-menu shop`、`main` | 选择 7。没有菜的菜单在输出流上给出 `NO_DISHES`，退出码 0。`shop` 不调用 `replace_file`，所以它不创建文件夹，不写文件，这一周的旧文件留着（v0.1-S14）。菜单里的菜只用了没有食材的菜谱，或者只用了常备食材时，给出标题行、代替各组的 `NOTHING_TO_BUY`、用到常备食材时的常备行，以及 `SAVED`，并保存一个用 `NOTHING_TO_BUY` 代替各组的文件（选择 7，A 点）。 | 1. 一份菜单为空的示例副本 X，`menus/2026-W46.toml` 是 `menu_text(2026-W46, [lunch, dinner])`：`shop`，然后 `shop this --lang zh`，每一行都在 `shop_faults(X.root)` 里。2. 在一份新的示例副本 Y 里运行同样两行，Y 有这个菜单文件、空的 shopping，以及内容为 `b"old\n"` 的 `shopping/2026-W46.md`。3. 一份新的示例副本，`menus/2026-W52.toml` 写成 `week = "2026-W52"\n`：`shop 2026-W52`。4. 一份新的示例副本里的白开水周：E 块的两行。5. 一份新的示例副本里的鸡蛋周：F 块的两行。 | 1. `(0, out [NO_DISHES(2026-W46)])`，然后 `(0, out [NO_DISHES_ZH(2026-W46)])`。每一行的记录是 `read settings.toml`、`read catalog.toml`、`read pantry.toml` 和 `read menus/2026-W46.toml`，没有 `mkdir`、`unlink`、`open` 或 `move`，列出记录先是 `recipes` 然后是 `menus`。X 没有 `shopping`。2. 同样的两个结果。`Y/shopping` 只有 `2026-W46.md`，它保留自己的字节和修改时间。3. `(0, out [NO_DISHES(2026-W52)])`，文件夹没有 `shopping`。4. E 块的两段输出，第一行之后文件是 `FILE_E`，第二行之后是 `FILE_E_ZH`。5. F 块的两段输出，文件先是 `FILE_F`，然后是 `FILE_F_ZH`。构造函数给出 4 和 5 的输出和文件。 |
| F13-T15 | 功能 | `recipe-menu shop`、`main` | 选择 2。`shop` 从 `context.today` 取得周：没有值和 `this` 给出今天所在的周，`next` 给出 7 天之后那天所在的周，跨年也一样。每一行都用 `str(week)` 写出周。一周在同一个月里、跨两个月、跨两年都可以，跨年的第 1 周也可以。不是周的 `WEEK` 值在错误流上单独给出 `NOT_A_WEEK`，退出码 2，没有提示，用输出的语言，并在碰任何文件之前（2.1 和 2.2 的错误，选择 2）。 | F 是一份新的示例副本，对 `2026-W01`、`2026-W23`、`2026-W49`、`2026-W53` 和 `2027-W01` 中的每个 W 都有米饭周 W。1. 在 F 里：对这些 W 中的每一个运行 `shop W` 和 `shop W --lang zh`。2. 在 F 里，在下面每个日期 D：`shop`、`shop this` 和 `shop next --lang zh`。各日期和 D 所在的周 T、7 天之后的周 N 是：2026-11-10 对应 `2026-W46` 和 `2026-W47`，2026-11-22 对应 `2026-W47` 和 `2026-W48`，2026-12-27 对应 `2026-W52` 和 `2026-W53`，2026-12-30 对应 `2026-W53` 和 `2027-W01`，2027-01-03 对应 `2026-W53` 和 `2027-W01`，2025-12-29 对应 `2026-W01` 和 `2026-W02`。3. 在带旧清单的 `example` 里，每一行都在一个新的 `shop_faults(example.root)` 里：对 `"2026-W99"`、`"Next"`、`""`、`"2026-w47"`、`"2025-W53"` 和 `" this"` 中的每个 V 运行 `shop V`。4. 在 `example` 里：`shop 2026-W99 --lang zh` 和 `shop Next --lang zh`。5. 各在一份新的示例副本里：目录花括号和 `shop 2026-W99`，常备清单的错误和 `shop Next`，shopping 是文件和 `shop ""`。6. 一份带中文设置的新示例副本：`shop 2026-W99`，然后 `shop 2026-W99 --lang en`。 | 1. `(0, out H(W, D))` 和 `(0, out H_ZH(W, D))`，D 是 W 的日期。第一行之后文件是 `FILE_H(W, D)`，第二行之后是 `FILE_H_ZH(W, D)`，比如开头是 `# Shopping list for 2026-W53` 和 `28 December 2026 to 3 January 2027: 1 meal, 1 dish.`。2. `shop` 和 `shop this` 都给出 F 里 `shop T` 的结果，`shop next --lang zh` 给出 `shop N --lang zh` 的结果。F 里有菜单的周，结果就是 1 的结果，2026-W47 则是 `(0, out SHOP_47(P))` 和 `(0, out SHOP_47_ZH(P))`。没有菜单的周，结果是 `(1, err [NO_MENU(T)])` 或 `(1, err [NO_MENU_ZH(N)])`，比如 `NO_MENU(2026-W46)` 和 `NO_MENU_ZH(2026-W48)`。3. 每一行都给出 `(2, err [NOT_A_WEEK(V)])`。记录只有 `read settings.toml`，没有列出，示例副本的完整记录在这些行前后相同。4. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(2, err [NOT_A_WEEK_ZH("Next")])`。5. 每一行给出它的 V 的 `(2, err [NOT_A_WEEK(V)])`，文件 `shopping` 保留它的字节。6. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(2, err [NOT_A_WEEK("2026-W99")])`。 |
| F13-T16 | 功能 | `recipe-menu shop`、`main` | `shop` 读写的文件（选择 3，2.2 的副作用）。它读取目录，然后读取常备清单，列出 `recipes/` 一次、`menus/` 一次，读取这一周的文件一次，并按第一道用到它的菜的顺序，把菜用到的每个菜谱读取一次：周一到周日，各餐按设置的顺序，各道菜按文件里的顺序。然后它通过 `replace_file` 写入。它不读菜单没用到的菜谱、别的菜单，也不读 `shopping/` 里的任何文件。遇到错误或这一周没有菜单之后，它不再读取任何东西，也不写入；遇到错误的周之后，它不读任何文件。 | 1 到 6 的每一行都在一个新的 `shop_faults(F.root)` 里，F 是那一行的文件夹。1. 在 `example` 里：`shop 2026-W47`，然后 `shop 2026-W47 --lang zh`。2. 一份新的示例副本里的 B 周：`shop 2026-W48`。3. 在 `example` 里：`shop 2026-W48`。4. 在 `example` 里：`shop 2026-W99`，然后 `shop 2026-W47 --help`。5. 各在一份新的示例副本里运行 `shop 2026-W47`：目录花括号、常备清单的错误、Rice Bowl、写成空文件的 `menus/2026-w48.toml`、菜单笔误，以及麻婆的错误。6. 一份新的示例副本，它的 `shopping/` 里有旧清单、内容为 `b"other\n"` 的 `2026-W48.md` 和内容为 `b"x\n"` 的 `notes.txt`：`shop 2026-W47`。 | R47 是 `read settings.toml`、`read catalog.toml`、`read pantry.toml`、`read menus/2026-W47.toml`，以及按 `tomato-egg`、`choy-sum`、`rice`、`mapo-tofu`、`tomato-egg-noodles` 和 `cola-wings` 这个顺序对每个 ID 的 `read recipes/ID.toml`。W47 是 `unlink shopping/2026-W47.md.tmp`、`open shopping/2026-W47.md.tmp` 和 `move shopping/2026-W47.md.tmp shopping/2026-W47.md`。1. R47、`mkdir shopping` 和 W47，列出记录先是 `recipes` 然后是 `menus`，`(0, out SHOP_47(P))`。然后是 R47 和 W47，没有 `mkdir`，同样的列出记录，`(0, out SHOP_47_ZH(P))`。`choy-sum` 和 `rice` 只读一次，虽然分别有 2 道和 3 道菜用到它们；`recipes/red-braised-pork.toml` 和别的菜单都没有被读取。2. `read settings.toml`、`read catalog.toml`、`read pantry.toml`、`read menus/2026-W48.toml`，以及按这个顺序的菜谱 `mapo-tofu`、`rice`、`choy-sum` 和 `red-braised-pork`，然后是 `mkdir shopping` 和 `2026-W48` 的 W47 那三次调用，同样的列出记录，以及 B 块的第一段输出。文件把周一晚餐写在午餐之前，而读取顺序按设置。3. `read settings.toml`、`read catalog.toml` 和 `read pantry.toml`，同样的列出记录，`(1, err [NO_MENU(2026-W48)])`。4. 只有 `read settings.toml`，没有列出，`(2, err [NOT_A_WEEK("2026-W99")])`。然后是同样的记录，退出码 0，err 为空，out 与不带文件夹的 `--help` 文本相同。5. 依次为：`read settings.toml` 和 `read catalog.toml`，没有列出；这两次再加 `read pantry.toml`，没有列出；这三次读取，列出记录只有 `recipes`；这三次读取，两个列出都有；这三次读取和 `read menus/2026-W47.toml`，两个列出都有；R47 直到 `read recipes/mapo-tofu.toml`，两个列出都有。没有记录里有 `mkdir`、`unlink`、`open` 或 `move`，每个结果都是它的文件夹在 F13-T17 里的结果。6. R47 和 W47，没有 `read shopping/...`，`(0, out SHOP_47(P))`。`2026-W48.md` 和 `notes.txt` 保留它们的字节和修改时间。 |
| F13-T17 | 功能 | `recipe-menu shop`、`recipe-menu check` | 选择 3。每个读取函数的第一个错误让 `shop` 停下，用输出的语言给出 `stop_at_error` 的三行，退出码 1，输出流上什么都没有，不写任何文件。先是目录，然后是常备清单（不管哪一周），然后是 `recipes/` 的列出，然后是 `menus/` 的列出（别的文件也算），然后是这一周的文件，然后按第一道菜的顺序读菜谱。菜单没用到的菜谱里的错误不改变任何东西，别的菜单也一样。名称缺少一种语言的食材是目录的错误。让 `shop` 停下的错误在 `check` 的错误之中（2.2 第 2 到 8 步，选择 3）。 | 1 到 27 的每个输入各在一份新的示例副本里，运行 `shop 2026-W47`、`shop 2026-W47 --lang zh`、`check` 和 `check --lang zh`：1. 没有目录。2. 目录花括号。3. 缺少的名称。4. 常备清单的错误。5. 常备清单的条目。6. 没有常备清单。7. 没有 recipes 文件夹。8. recipes 是文件。9. Rice Bowl。10. 大写的 rice。11. 没有 menus 文件夹。12. menus 是文件。13. 写成空文件的 `menus/2026-w48.toml`。14. 写成空文件的 `menus/plan.toml`。15. 写成空文件的 `menus/2026-W48.TOML`。16. 菜单笔误。17. v0.1-S07 的菜单错误。18. 麻婆的错误。19. rice 为 0。20. 麻婆的错误和 rice 为 0。21. 目录花括号和常备清单的错误。22. 常备清单的错误和 Rice Bowl。23. 常备清单的错误和没有 menus 文件夹。24. Rice Bowl 和写成空文件的 `menus/2026-w48.toml`。25. 写成空文件的 `menus/2026-w48.toml` 和菜单笔误。26. 菜单笔误和麻婆的错误。27. 文件夹 x，并把 `menus/2026-W47.toml` 里的 `[wednesday]\nlunch = []\ndinner = []` 换成 `[wednesday]\nlunch = []\ndinner = ["x"]`。然后，各在一份新的示例副本里，只运行 `shop 2026-W47`：28. 文件夹 x。29. 把 `recipes/red-braised-pork.toml` 里的 `servings = 2` 换成 `servings = 0`。30. 把 `menus/2026-W48.toml` 写成 `[[[\n`。然后，各在一份新的示例副本里，只运行 `shop 2026-W48`：31. 写成空文件的 `menus/2026-w48.toml`。32. 常备清单的错误。 | 1 到 27。`shop 2026-W47` 给出 `(1, err STOP(W, M))`，`shop 2026-W47 --lang zh` 给出 `(1, err STOP_ZH(W, M))`，W 和 M 是：1. `catalog.toml` 和 `FILE_MISSING`。2. `catalog.toml, line 11` 和 `MISSING_BRACE`。3. `catalog.toml, ingredient 22` 和 `MISSING_KEY(key="en")`。4. `pantry.toml, item 3` 和 `PANTRY_INGREDIENT(name="sesame oil")`。5. `pantry.toml, item 3` 和 `ITEM_NOT_A_TEXT`。6. `pantry.toml` 和 `FILE_MISSING`。7. `recipes` 和 `FOLDER_MISSING`。8. `recipes` 和 `FOLDER_IS_FILE`。9. `recipes/Rice Bowl.toml` 和列出的 `NOT_A_RECIPE_ID`。10. `recipes/rice.TOML` 和 `TOML_ENDING_NOT_SMALL`。11. `menus` 和 `FOLDER_MISSING`。12. `menus` 和 `FOLDER_IS_FILE`。13. `menus/2026-w48.toml` 和 `NOT_A_WEEK_NAME`。14. `menus/plan.toml` 和 `NOT_A_WEEK_NAME`。15. `menus/2026-W48.TOML` 和 `TOML_ENDING_NOT_SMALL`。16. `menus/2026-W47.toml, Monday dinner` 和 `UNKNOWN_RECIPE(recipe="tomato-eggs")`，即 F11 原型“A menu with a mistake”的各行。17. `menus/2026-W47.toml, week` 和 `WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`。18. `recipes/mapo-tofu.toml, ingredient 3` 和菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`。19. `recipes/rice.toml, servings` 和 `SERVINGS_TOO_FEW(servings=0)`。20. 19 的 W 和 M，因为周一晚餐用到 `rice` 在周二晚餐用到 `mapo-tofu` 之前。21. 2 的 W 和 M。22. 4 的 W 和 M，因为常备清单在 `recipes/` 的列出之前。23. 4 的 W 和 M。24. 9 的 W 和 M。25. 13 的 W 和 M。26. 16 的 W 和 M。27. `recipes/x.toml` 和 `FILE_IS_FOLDER`。每个输入里，这个错误都在两种语言的 `check` 的错误之中，这些行之后文件夹没有 `shopping`。28 到 30。`(0, out SHOP_47(P))`，因为没有菜用到 `x` 或 `red-braised-pork`，也不读 `2026-W48`。31. `(1, err STOP(menus/2026-w48.toml, NOT_A_WEEK_NAME))`，两个系统上都是：列出在找这一周之前就让 `shop` 停下了。32. `(1, err STOP(pantry.toml, item 3, PANTRY_INGREDIENT(name="sesame oil")))`，不是 `NO_MENU`：不管哪一周，常备清单都让 `shop` 停下。 |
| F13-T18 | 功能 | `recipe-menu shop`、`main` | 选择 3 的第 6 步，以及在 `main` 上运行 v0.1-S15。列出里没有的周给出带 `str(week)` 的 `NO_MENU`，错误流上一行，退出码 1，输出流上什么都没有，不写文件。不是菜单文件的条目不算。目录、常备清单和两个列出在前。v0.1-S15 的第 5 步给出与 `menu show` 相同的三行（2.2 第 6 步，选择 3）。 | 1. 在带空的 shopping 的 `example` 里运行 v0.1-S15：`menu show 2026-W48`、`menu show 2026-W99`、`shop 2026-W48`，然后菜单笔误、`menu show 2026-W47` 和 `shop 2026-W47`。然后用 `--lang zh` 运行同样的 `shop` 各行。2. 在 `example` 里：`shop`，然后 `shop this --lang zh`，然后在 2026-11-17 日 `shop next`。3. 一份新的示例副本，它的 `menus/` 里还有内容与 `2026-W47.toml` 相同的 `2026-W48.toml.bak`、空文件夹 `2026-W48` 和 `notes.txt`：`shop 2026-W48`。4. 一份菜单为空的示例副本：`shop 2026-W47`。5. 各在一份新的示例副本里运行 `shop 2026-W48`：目录花括号、没有 recipes 文件夹，以及 Rice Bowl。 | 1. `menu show 2026-W48` 和 `shop 2026-W48` 都给出 `(1, err [NO_MENU(2026-W48)])`，后者是 F13 原型“No menu, or an empty menu”的第一段输出；`(2, err [NOT_A_WEEK("2026-W99")])`。然后 `menu show 2026-W47` 和 `shop 2026-W47` 都给出 `(1, err STOP(menus/2026-W47.toml, Monday dinner, UNKNOWN_RECIPE(recipe="tomato-eggs")))`。然后是 `(1, err [NO_MENU_ZH(2026-W48)])` 和 `(1, err STOP_ZH(menus/2026-W47.toml，周一晚餐, UNKNOWN_RECIPE(recipe="tomato-eggs")))`。`shopping\` 仍然为空。2. `(1, err [NO_MENU(2026-W46)])`、`(1, err [NO_MENU_ZH(2026-W46)])` 和 `(1, err [NO_MENU(2026-W48)])`。3. `(1, err [NO_MENU(2026-W48)])`。4. `(1, err [NO_MENU(2026-W47)])`。5. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`、`(1, err STOP(recipes, FOLDER_MISSING))` 和 `(1, err STOP(recipes/Rice Bowl.toml, 列出的 NOT_A_RECIPE_ID))`。2 到 5 里，这些行之后文件夹没有 `shopping`。 |
| F13-T19 | 功能 | `recipe-menu shop`、`main` | 选择 6。保存失败是错误流上的三行，退出码 1：清单文件的完整路径 `str(context.folder.root / problem.file)`（文件夹失败时也是），然后是两个空格和用输出语言写的问题文字，然后是 `NO_FILE_SAVED`，或者调用没能删除 `temp` 时带 `temp` 完整路径的 `LEFT_BEHIND`。输出流上什么都没有。旧文件保留它的字节。`shop` 创建的文件夹留着。下一次没有故障的运行会保存清单（2.2 第 12 步，选择 6，A 点）。 | R 是每个输入的数据文件夹，一份新的示例副本，P 和 T 属于 2026-W47。每个输入的第一行都在 `shop_faults(R, *rules)` 里运行。1. `mkdir R/shopping: DENIED`：`shop 2026-W47`，然后 `shop 2026-W47 --lang zh`。2. `mkdir R/shopping: IO`：`shop 2026-W47`。3. 旧清单，`open T: DENIED`：`shop 2026-W47`，然后 `shop 2026-W47 --lang zh`。4. 旧清单，`open T: IO`：`shop 2026-W47`。5. 旧清单，`write T: NO_SPACE`：`shop 2026-W47`。6. 旧清单，`write T: NO_SPACE` 和 `unlink T: later DENIED`：`shop next`。然后不带规则 `shop next`。7. 同 6，但那一行是 `shop 2026-W47 --lang zh`，之后没有别的。8. 旧清单，`close T: IO`：`shop 2026-W47`。9. 旧清单，`move T: DENIED`：`shop 2026-W47`，然后 `shop 2026-W47 --lang zh`。10. 没有 shopping，`write T: NO_SPACE`：`shop 2026-W47`。然后不带规则 `shop 2026-W47`。 | 1. `(1, err FAIL(P, FOLDER_CREATE_DENIED))` 和 `(1, err FAIL_ZH(P, FOLDER_CREATE_DENIED))`：第一行写出的是清单文件，不是它的文件夹。R 没有 `shopping`。2. `(1, err FAIL(P, FOLDER_CREATE_ERROR(reason="Input/output error")))`。3. `(1, err FAIL(P, FILE_WRITE_DENIED))` 和 `(1, err FAIL_ZH(P, FILE_WRITE_DENIED))`。4. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="Input/output error")))`。5. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="No space left on device")))`，记录以 `unlink shopping/2026-W47.md.tmp`、`open shopping/2026-W47.md.tmp` 和 `unlink shopping/2026-W47.md.tmp` 结尾。6. `(1, err LEFT(P, FILE_WRITE_ERROR(reason="No space left on device"), T))`，T 是故障工具写下的 `tests/f11_support.py` 的 `first_half(FILE_47)`，因为 `FILE_47` 是 ASCII。然后 `(0, out SHOP_47(P))`：第 3 步删除了 T，文件是 `FILE_47`，`R/shopping` 只有 `2026-W47.md`。7. `(1, err LEFT_ZH(P, FILE_WRITE_ERROR(reason="No space left on device"), T))`：对 `next` 也一样，这一行写出的是 T，即 `2026-W47.md.tmp`。8. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="Input/output error")))`。9. `(1, err FAIL(P, FILE_WRITE_DENIED))`，这就是设计 2.2 里失败示例的各行，以及 `(1, err FAIL_ZH(P, FILE_WRITE_DENIED))`。记录以 `move shopping/2026-W47.md.tmp shopping/2026-W47.md` 和 `unlink shopping/2026-W47.md.tmp` 结尾。10. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="No space left on device")))`，`R/shopping` 留着，是一个空文件夹。然后 `(0, out SHOP_47(P))`，文件是 `FILE_47`。3 到 9 里，每次失败之后 P 都保留 `b"old\n"`；1 到 5 和 8 到 10 之后，没有条目以 `.tmp` 结尾。 |
| F13-T20 | 功能 | `recipe-menu shop`、`main` | 保存时按下 Ctrl+C。`cli` 以 130 退出，什么都不写，`replace_file` 已经删除了 `temp`，所以旧文件完整留着。在 `open` 里面、系统已创建 `temp` 之后按下 Ctrl+C，空的 `temp` 留着，下一次运行删除它并保存清单（2.2 的错误，选择 6，F05 设计 2.10）。 | R、P 和 T 同 F13-T19，每个输入各在 R 处一份带旧清单的新示例副本里。每个输入的第一行都在 `shop_faults(R, *rules)` 里、通过 `call_main` 运行。1. `write T: CTRL_C`：`shop 2026-W47`。2. `move T: CTRL_C`：`shop 2026-W47`。3. `open T: after CTRL_C`：`shop 2026-W47`。然后不带规则、在 `shop_faults(R)` 里 `shop 2026-W47`。4. `write T: CTRL_C` 和 `unlink T: later DENIED`：`shop 2026-W47 --lang zh`。然后不带规则 `shop 2026-W47 --lang zh`。 | 每个输入的第一行都给出 `(130, "", "")`，P 保留 `b"old\n"`。1. 记录以 `unlink shopping/2026-W47.md.tmp`、`open shopping/2026-W47.md.tmp` 和 `unlink shopping/2026-W47.md.tmp` 结尾，T 不存在。2. 记录以 `open shopping/2026-W47.md.tmp`、`move shopping/2026-W47.md.tmp shopping/2026-W47.md` 和 `unlink shopping/2026-W47.md.tmp` 结尾，T 不存在。3. 记录以 `unlink shopping/2026-W47.md.tmp` 和 `open shopping/2026-W47.md.tmp` 结尾，T 是一个空文件。然后 `(0, out SHOP_47(P))`，记录以 F13-T16 的 W47 结尾，T 不在了，文件是 `FILE_47`。4. T 是故障工具写下的 `text[: len(text) // 2]` 的 UTF-8 字节，`text` 是 `PROTOTYPE_FILE` 的文字。然后 `(0, out SHOP_47_ZH(P))`，T 不在了，文件是 `PROTOTYPE_FILE`。 |
| F13-T21 | 功能 | `recipe-menu shop`、`main` | 不用故障工具、文件系统真实失败时的选择 6 和 C 点。`shopping` 处是文件夹以外的东西时给出 `PARENT_NOT_A_FOLDER`。清单文件路径上的文件夹让移动在两个系统上都失败。在 Windows 上，别的程序打开着旧文件时，移动以 `FILE_WRITE_DENIED` 失败，旧文件保留它的字节；在 Linux 上，移动替换这个文件。不留下 `.tmp` 文件，修正之后的下一次运行会保存清单（选择 6，C 点）。 | R、P 和 T 同 F13-T19，每个输入各在 R 处一份新的示例副本里。1. shopping 是文件：`shop 2026-W47`，然后 `shop 2026-W47 --lang zh`。然后删除 `R/shopping`，再 `shop 2026-W47`。2. `R/shopping` 处是悬空链接：`shop 2026-W47`。3. 空的 shopping 里有空文件夹 `2026-W47.md`：`shop 2026-W47`。然后删除这个文件夹，再 `shop 2026-W47`。4. 旧清单，在 `shop 2026-W47` 期间用 `held_open(P)` 让它保持打开。然后在文件关闭之后 `shop 2026-W47`。 | 1. `(1, err FAIL(P, PARENT(shopping)))`，这就是设计 2.2 示例的最后一次运行，以及 `(1, err FAIL_ZH(P, PARENT(shopping)))`。文件 `shopping` 保留 `b"x\n"`。删除之后，`(0, out SHOP_47(P))`，`R/shopping` 是一个新文件夹，只有内容为 `FILE_47` 的 `2026-W47.md`。2. `(1, err FAIL(P, PARENT(shopping)))`，链接仍然在。3. `(1, err FAIL(P, M))`，M 是在这一行之前对用例的一个文件夹取得的 `move_message`：在 Windows 上是 `FILE_WRITE_DENIED`，在 Linux 上是 `FILE_WRITE_ERROR(reason="Is a directory")`。文件夹 `2026-W47.md` 仍然在，T 不存在。删除之后，`(0, out SHOP_47(P))`，文件是 `FILE_47`。4. 在 Windows 上：`(1, err FAIL(P, FILE_WRITE_DENIED))`，P 保留 `b"old\n"`，T 不存在。在 Linux 上：`(0, out SHOP_47(P))`，P 是 `FILE_47`。然后在两个系统上都是：`(0, out SHOP_47(P))`，P 是 `FILE_47`，`R/shopping` 只有 `2026-W47.md`。 |
| F13-T22 | 功能 | `recipe-menu shop`、`main` | `cli` 在运行 `shop` 之前，用 F05 的消息和退出码报告命令行上的错误、缺少的数据文件夹和损坏的设置：两个周和一个选项。`--help` 显示帮助，什么都不运行。之后同样的文件夹给出 `shop` 的输出（2.2 的错误，选择 1，F05 设计 2.10）。 | 1. 在 `example` 里：`shop 2026-W47 2026-W48`、`shop 2026-W47 2026-W48 --lang zh`、`shop --tag x` 和 `shop --tag x --lang zh`。2. 在 `example` 里：`shop next --help` 和 `shop 2026-W99 --help --lang zh`。3. M 是 `tmp_path / "missing"`：在 M 里 `shop`，在 M 里 `shop next --lang zh`。4. 一份带损坏设置的新示例副本：`shop 2026-W47`。5. 在 `example` 里：`shop 2026-W47`。 | 1. `(2, err ['Unexpected argument "2026-W48". Write "recipe-menu shop [WEEK]".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["多余的参数“2026-W48”。请写成“recipe-menu shop [周]”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['"shop" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])` 和 `(2, err ["“shop”没有选项“--tag”。它没有自己的选项。", "运行“recipe-menu --help”查看选项。"])`。2. 每一行都给出退出码 0、空的 err，out 与用真正的 `COMMANDS`、不带文件夹运行 `--help` 得到的文本相同，第二行则与 `--help --lang zh` 相同。3. `tests/f05_texts.py` 的 `no_data_folder(M)` 和 `no_data_folder(M, ZH)`，M 仍然不存在。4. `(1, err STOP(settings.toml, meals, 设置的 UNKNOWN_MEAL(meal="supper")))`，文件夹没有 `shopping`。5. `(0, out SHOP_47(P))`。5 之前，`example` 没有 `shopping`。 |
| F13-T23 | 集成 | `recipe-menu shop`、`main` | `shop` 使用 `cli` 选出的数据文件夹和语言：`--data`，否则 `RECIPE_MENU_DATA`，否则 `~/recipe-menu`；`--lang`，否则设置里的语言，否则英文。最后一行写出保存的文件的完整路径。带字节顺序标记和 CRLF 换行的数据文件读出来一样，与 v0.1-S08 的期望相同，保存的文件仍然没有字节顺序标记、用 LF 换行（2.2 的参数，选择 5，F05 设计 2.10）。 | B 是 `tmp_path / "One Drive" / "菜谱"` 处的一份新示例副本，E 是 `{"RECIPE_MENU_DATA": str(B)}`。1. 不带文件夹、`environ` 为 E，运行 `shop 2026-W47`。2. 不带文件夹 `shop 2026-W47`。然后在 `home / "recipe-menu"` 处放一份新的示例副本，再不带文件夹 `shop 2026-W47`。3. 用 `monkeypatch.chdir` 进入 `tmp_path / "cwd"` 之后，以参数 `shop 2026-W47 --data rel` 调用 `main`，`tmp_path / "cwd"` 里的 `rel` 处有一份新的示例副本。4. 以参数 `shop 2026-W47 --data ~/other` 调用 `main`，`home / "other"` 处有一份新的示例副本。5. 一份带中文设置的新示例副本 C：`shop 2026-W47`，然后 `shop 2026-W47 --lang en`。6. 一份带 BOM 和 CRLF 的新示例副本 D：`shop 2026-W47`。 | 1. `(0, out SHOP_47(B/shopping/2026-W47.md))`。2. `no_data_folder(home / "recipe-menu")`，然后 `(0, out SHOP_47(home/recipe-menu/shopping/2026-W47.md))`。3. `(0, out SHOP_47(Path.cwd() / "rel" / "shopping" / "2026-W47.md"))`，一个完整路径。4. `(0, out SHOP_47(home/other/shopping/2026-W47.md))`。5. `(0, out SHOP_47_ZH(P))`，文件是 `PROTOTYPE_FILE`。然后 `(0, out SHOP_47(P))`，文件是 `FILE_47`。6. `(0, out SHOP_47(P))`，这就是 v0.1-S08 的第 4 步。1 到 4 和 6 里，保存的文件是 `FILE_47`，没有 `b"\xef\xbb\xbf"`，也没有 `b"\r"`。 |
| F13-T24 | 集成 | `recipe-menu menu new`、`recipe-menu shop`、`main` | 在 `main` 上运行 v0.1-S14。`shop` 和 `shop next` 读取 `menu new` 创建的两个空菜单，打印带今天所在的周和 7 天之后那一周的 `NO_DISHES`，以 0 退出。`shopping\` 仍然为空（选择 2 和 7）。 | 对 2026-11-10、2026-12-30 和 2027-01-03 中的每个日期 D，以及 F13-T15 里的周 T 和 N，用一份带空的 shopping、菜单为空的示例副本 F，并在 D 日于 F 里运行每一行：1. `menu new`。2. `menu new next`。3. `shop`。4. `shop next`。5. `shop this --lang zh`。 | 1 和 2 都给出退出码 0，`menus/` 里有 `T.toml` 和 `N.toml`。3. `(0, out [NO_DISHES(T)])`。4. `(0, out [NO_DISHES(N)])`。5. `(0, out [NO_DISHES_ZH(T)])`。这些行之后，`F/shopping` 仍然是一个空文件夹。 |
| F13-T25 | 集成 | `recipe-menu menu new`、`recipe-menu menu show`、`recipe-menu shop`、`main` | 在 `main` 上运行 v0.1-S16。设置决定新菜单的餐次，以及没写份数的菜的份数，`shop` 把 `tomato-egg` 从 2 份换算成 3 份。清单以 v0.1-S16 的那一行开头，在 Vegetables and fruit 下列出 Tomato 450 g 和 Scallion 2 stalks，然后在 Eggs, dairy, and tofu 下列出 Egg 5 pieces，常备行与 v0.1-S16 相同（选择 4、7 和 8）。 | R 处的 init 文件夹，把 `settings.toml` 里的 `meals = ["lunch", "dinner"]` 换成 `meals = ["breakfast", "lunch", "dinner"]`，把 `servings = 2 ` 换成 `servings = 3 `。1. `menu new 2026-W48`。2. 把 `menus/2026-W48.toml` 里的 `[monday]\nbreakfast = []` 换成 `[monday]\nbreakfast = ["tomato-egg"]`。3. `menu show 2026-W48`。4. `shop 2026-W48`，然后 `shop 2026-W48 --lang zh`。 | 1 和 3 都给出退出码 0。4. C 块的两段输出，各带退出码 0 和空的 err。第一行是 `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish`，常备行是 `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`。 |
| F13-T26 | 集成 | `recipe-menu shop`、`main` | 在 `main` 上运行 v0.1-S18。不能相加的数量共用一行：`5 stalks + 1 bunch` 和 `30 ml + 10 g`，中文是 `5 根 + 1 把` 和 `30 ml + 10 g`，就是 `amount_text` 写出的样子。保存的文件里是同样的数量（选择 4 和 5）。 | 一份带有 `tests/f12_support.py` 的 `s18_changes` 改动的新示例副本：G 块的两行。 | G 块的两段输出，各带退出码 0 和空的 err。英文输出里有 `  Scallion       5 stalks + 1 bunch` 和 `  Soy sauce      30 ml + 10 g` 两行，中文输出里有 `  葱         5 根 + 1 把` 和 `  生抽       30 ml + 10 g` 两行。每一行之后，文件是这张清单用它的语言的 `shop_file`，其中有 `- [ ] Scallion 5 stalks + 1 bunch` 或 `- [ ] 葱 5 根 + 1 把`。 |
| F13-T27 | 集成 | `recipe-menu shop`、`main` | 在 `main` 上为 `shop` 运行 v0.1-S23。同一周运行两次只改变 `shopping\2026-W47.md`，`shopping\` 里没有别的文件。`home` 下和当前文件夹下的其他每个文件和文件夹都保留它的字节和修改时间。不保存任何东西的 `shop` 各行什么都不改变（2.2 的副作用，选择 6）。 | `home / "recipe-menu"` 处一份带空的 shopping 的新示例副本，以及用 `monkeypatch.chdir` 进入的空的当前文件夹 `tmp_path / "cwd"`。在这些行之前、第一组之后、第二组的每次运行之后，用 `tests/f07_support.py` 的 `snapshot` 给 `home` 和当前文件夹拍快照。1. 不带文件夹：`shop 2026-W48`、`shop 2026-W99`、`shop --help` 和 `shop --tag x`。2. 不带文件夹：`shop 2026-W47`，运行两次。 | 1. `(1, err [NO_MENU(2026-W48)])`、`(2, err [NOT_A_WEEK("2026-W99")])`、带用真正的 `COMMANDS`、不带文件夹运行 `--help` 得到的文本的退出码 0，以及带 F13-T22 里 `shop --tag x` 那两行的退出码 2。1 之后的快照等于它之前的快照。2. 每次运行都给出 `(0, out SHOP_47(home/recipe-menu/shopping/2026-W47.md))`。每次运行之后，`home` 的快照等于这次运行之前的快照，只有 `recipe-menu/shopping`（修改时间可能改变）和 `recipe-menu/shopping/2026-W47.md`（内容是 `FILE_47`）除外。`recipe-menu/shopping` 只有 `2026-W47.md`，当前文件夹的快照不变。 |
| F13-T28 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令运行 `shop`。不管 Python 给流的编码是什么，它都把输出以 UTF-8 写到 stdout，把保存的文件写成 UTF-8，把退出码 1 或 2 的消息写到 stderr（2.2，F05 设计 2.9）。 | `tests/f05_support.py` 的 `run_module`，它把 `HOME` 和 `USERPROFILE` 设成 `tmp_path / "home"`，把 `PYTHONIOENCODING` 设成 `ascii`。用 `example`：1. `shop 2026-W47 --lang zh --data <example>`。2. `shop 2026-W47 --data <example>`。3. `shop 2026-W99 --lang zh --data <example>`。4. 用 `data=example.root`（它设置 `RECIPE_MENU_DATA`）运行 `shop 2026-W48`。5. 在一份 shopping 是文件的新示例副本 X 里：`shop 2026-W47 --data <X>`。没有一行用 `this`、`next` 或不写周，因为新进程会读取时钟。 | 1. 退出码 0，stdout 是 `SHOP_47_ZH(P)` 的各行，stderr 为空，文件是 `PROTOTYPE_FILE`。2. 退出码 0，stdout 是 `SHOP_47(P)` 的各行，stderr 为空，文件是 `FILE_47`。3. 退出码 2，stdout 为空，stderr 是 `NOT_A_WEEK_ZH("2026-W99")` 那一行。4. 退出码 1，stdout 为空，stderr 是 `NO_MENU(2026-W48)` 那一行。5. 退出码 1，stdout 为空，stderr 是 `FAIL(P, PARENT(shopping))` 的各行。 |
| F13-T29 | 集成 | `recipe-menu shop`、`main` | 随机的星期。对于任意宽度、带不带换行的目录名称，任意常备清单，任意餐次组合和默认份数，下面列出的任意一周，以及日、餐、菜和份数的任意组合，`shop` 都给出 2.2 的规则在两种语言里给出的输出和文件，没有菜的菜单则给出 `NO_DISHES`，第二次运行替换文件。随机组合能覆盖其他用例没有列出的宽度、组和常备行（2.2，选择 2、4、5、7 和 8）。 | `random.Random(20261116)` 构造 100 个文件夹，每个都是一份带额外菜谱 `water` 的新示例副本。除非另有说明，下面的每个选择机会均等。目录：测试重新写出 `catalog.toml`，有示例的六个分类和 22 种食材，按示例的顺序，保留它们的键、分类和单位，有示例的五个标签，名称都是新的。新的英文名称是 `C` 或 `I` 加上这一项的编号（食材用两位数字），然后是 0 到 3 个词，每个词前面一个空格。新的中文名称是 `类` 或 `食` 加上编号，然后是 0 到 3 个词，中间没有空格。一个词在英文里有 1 到 6 个字符，在中文里有 1 到 4 个字符，取自字母 `a` 到 `z` 和 `A` 到 `Z`、`\u00e9`，以及汉字 `番茄鸡蛋豆腐葱姜蒜米面油`。有 1/10 的机会，带词的食材英文名称用 TOML 转义 `\n` 代替它最后一个词前面的空格。测试把菜谱里的每个 `item = "<旧中文名称>"` 换成新的中文名称，并把 `pantry.toml` 写成食材的新中文名称，每种食材有 1/3 的机会。设置：`meals` 是三餐的一个非空组合，顺序随机，`servings` 从 1 到 5。周 W：`2026-W01`、`2026-W23`、`2026-W47`、`2026-W49`、`2026-W53` 和 `2027-W01` 之一。测试写出 `menus/W.toml`：每一天有 1/4 的机会被省略，一天按随机顺序列出设置的各餐，每餐 0 到 3 道菜，并有 1/10 的机会所有餐都没有菜。每道菜是示例的七个菜谱之一或 `water`，写成 `"ID"`、`{ recipe = "ID" }` 或 `{ recipe = "ID", servings = k }`，k 从 1 到 12。然后在日期 D 运行 `shop V --lang L`，L 是 `en` 或 `zh`：V 是 W、`this` 或没有值，D 是 W 的七天之一；或者 V 是 `next`，D 是 W 前一周的七天之一。然后运行 `shop W --lang L2`，L2 是 `en` 或 `zh`。 | 设 S 为 `shop_list(folder, W)`：菜单没有菜时，每一行都给出 `(0, out [NO_DISHES(W)])` 或 `(0, out [NO_DISHES_ZH(W)])`，文件夹没有 `shopping`。否则每一行都给出用它那一行语言的 `(0, out shop_lines(S, L, P))`，之后文件是 `shop_file(S, L)`，`shopping/` 只有 `W.md`。 |
| F13-T30 | 性能 | `recipe-menu shop`、`python -m recipe_menu` | PT01 和 v0.1-S32：`shop` 在 1 秒内为 PT01 的一周生成并保存清单，这一周有来自 63 个不同菜谱的 63 道菜，按从启动到退出的 5 次运行的中位数计（需求 7.1，2.2，选择 10）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"`，没有 `shopping/`。按第 3 节的说明，先不计时运行一次，然后计时运行 5 次 `python -m recipe_menu shop 2026-W26 --data <pt01>`。 | 每次运行都以 0 退出，在 stdout 上写出 `pt01_shop` 的结果，共 302 行，stderr 上什么都不写。之后 `shopping/` 只有 `2026-W26.md`，内容是这张清单用英文的 `shop_file`，共 10,345 字节。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。 |

## 3. 性能用例

PT01 把 `shop` 列在它的命令里（需求 7.1），所以 `recipe-menu shop` 有一个用例。F13 的其他接口都没有：`SHOP_COMMAND` 和 `replace_file` 没有自己的指标，PT01 通过这个命令为它们计时（R14）。

| 编号 | 指标 | 机器 | 余量 | 基线 |
| --- | --- | --- | --- | --- |
| F13-T30 | PT01：在有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`recipe-menu shop` 在 1 秒内完成。按从启动到退出的 5 次运行的中位数计。 | Troy 的电脑：Windows 11，用 `recipe-menu` 环境的 Python 3.13。这个用例也在 CI 里运行，在 `.github/workflows/troy-mode.yml` 的 `ubuntu-24.04` 运行器上，它不是固定的机器（架构第 10 节）。 | 在 Windows 上没有余量：中位数必须小于 1 秒，因为高于 PT01 的余量会放过达不到它的命令（v0.1 测试方案第 3 节）。在 Linux 上是 3 秒，与 F07-T25、F09-T28、F10-T21 和 F11-T38 相同，所以这个用例在速度未知的运行器上能成立，同时仍能抓住慢了好几倍的情况。 | 首次运行。架构师的模型在 Troy 的电脑上分两组、每组 5 次运行 `shop 2026-W26`，中位数是 0.226 秒和 0.228 秒，同一组里 `menu show 2026-W26` 是 0.216 秒（设计第 4 节）。F11 的 `menu show 2026-W26` 在 Troy 的电脑上用时 0.187 秒，F12 的 `build_shopping_list` 在这一周的中位数是 5.19 毫秒。模型不是实现，所以 F13 的实现 PR 记录第一个基线。 |

**哪个系统是 Troy 的电脑。** CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。所以这个用例用 `tests/pt01_support.py` 的 `time_limit` 的上限：`sys.platform == "win32"` 时为 1 秒，否则为 3 秒，与 F11-T38 相同。如果有了 Windows 上的 CI 任务，要先改这份方案。

**PT01 数据文件夹。** 由 `tests/pt01_support.py` 的 `make_pt01` 写出，与 F11-T38 相同。F13 不改动这个生成器。它的设置是早餐、午餐和晚餐，2 份，它的常备清单是 300 种食材里的最后 10 种。`2026-W26` 从 2026 年 6 月 22 日到 28 日，用到 63 个不同的菜谱 `recipe-0576` 到 `recipe-0638`，21 餐每餐三个，每顿晚餐的第一道菜是 4 份。这个文件夹没有 `shopping/`，所以不计时的那次运行会创建它，计时的各次运行替换文件。架构师的模型和这份方案用的是同一周。

**计时运行。** 这个用例使用 F09 在 `tests/pt01_support.py` 里加入的通用计时运行：`command_run`、`command_runs`、`record_times` 和 `time_limit`，它们保持原来的名称和行为。

**预期输出。** `tests/f13_support.py` 的 `pt01_shop(root)` 给出 `(0, out, "")`，out 是 `shop_lines(shop_list(DataFolder(root), IsoWeek(2026, 26)), Lang.EN, P)` 的各行，每行后面跟 `"\n"`，P 是 `root / "shopping" / "2026-W26.md"`。用例在第一次运行之前算一次。它还检查结果的这些事实，测试经理在一个 PT01 文件夹上从模型取得了它们：第一行是 `Shopping list for 2026-W26, 22 to 28 June 2026: 21 meals, 63 dishes`，输出共 302 行，六个组标题是示例的六个分类、按它们的顺序，有 290 行以两个空格开头，常备行写出 10 种常备食材。保存的文件在两个系统上都是 10,345 字节，与设计第 4 节的结果相同。

**用例的步骤。**

1. 生成文件夹，并算出预期结果。
2. 不计时地启动一次命令，按第 3 步检查它的结果。Windows 第一次读取这 1,053 个新文件时很慢（F07 测试方案第 3 节），而 Troy 自己的数据文件夹不会每次运行都付这个代价。这次运行创建 `shopping/`。
3. 用 `command_runs` 把同一命令启动 5 次，每次都是新进程：`sys.executable -m recipe_menu`，在 `tmp_path` 里，`HOME` 和 `USERPROFILE` 设成一个空的 home 文件夹，没有 `RECIPE_MENU_DATA`。每次运行都必须以 0 退出，给出完全等于预期的 stdout，给出空的 stderr。不满足的运行让用例失败，不管它用时多少。
4. 检查 `shopping/` 只有 `2026-W26.md`，内容是预期的字节。
5. 取 5 次时间的中位数，与这个系统的上限比较。
6. 用 `record_property` 记录 5 次时间、中位数和范围，让 JUnit 报告保存它们供下次比较。

**它怎样在 Troy 的电脑上运行。** 这个用例在 `tests/` 里，所以每次在 Troy 的电脑上完整运行测试时都会运行，主会话为每个 PR 用 `recipe-menu` 环境的 Python 启动完整运行。在 F13 的实现 PR 里，主会话还会在没有别的测试、构建或安装进行时单独运行它：`python -m pytest tests/test_f13_performance.py --junitxml=reports/pt01-f13.xml`。PR 描述报告中位数和范围，那次运行就是基线。发布测试在同一台机器上运行 v0.1-S32。

**基准测试检查表。** 这个用例这样回答 `benchmark-checklist` 的问题：

- 瓶颈：设计选择 10 和第 4 节写明了它。`shop` 读取 `menu show` 读取的东西，再加上 10 项的常备清单，所以 Python 的启动、导入、300 种食材的目录、1,000 个菜谱文件的列出和 63 个菜谱文件限制了它，与限制 `menu show` 的相同。`build_shopping_list` 增加约 5 毫秒，`amount_text` 约 1 毫秒，保存是一次探查、一次删除、一次打开、一次 10 KB 的写入、一次关闭和一次移动。在同一组里，架构师的模型比 `menu show` 多用约 0.01 秒。这个用例不做性能剖析，因为剖析器会拖慢运行。剖析由 `[refactor]` PR 做。
- 调优：每次运行都是一个新的 Python 进程，用安装好的包和它编译好的文件，没有覆盖率统计，也没有调试器，与 Troy 的运行方式相同。第 2 步不计时的那次运行已经把文件读过一次。coverage.py 只统计测试进程，所以 CI 里的 `coverage run -m pytest` 不会拖慢计时的进程。
- 极限：`shop` 通过管道写约 10 KB，向磁盘写 10 KB，并读取 63 个菜谱文件、一个菜单文件、目录、常备清单和设置，约 170 KB，磁盘在几毫秒内就能读写完。所以这个时间衡量的是 Python 的工作。
- 错误：第 2 步和第 3 步检查每次运行的退出码、完整的 stdout 和空的 stderr，第 4 步检查保存的文件。
- 可重复：5 次计时运行，记录中位数和范围。与基线的差别如果小于基线各次运行的范围，就不算可测量的变化。
- 相关性：这个用例为整个命令从启动到退出计时，这正是 Troy 等待的时间。三餐每餐三道菜、来自 63 个不同菜谱的一周，是 PT01 一周最多的内容，所以 `shop` 读取了它能为 PT01 一周读取的最多菜谱文件，合并了最多的行。
- 工作确实发生了：计数 `21 meals, 63 dishes`、来自 63 个菜谱的 6 组 290 行，以及每次运行都会替换的 10,345 字节的保存文件，表明 `shop` 读取了菜单和它用到的每个菜谱，生成了清单，并保存了它。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 单独的 `SHOP_COMMAND` 字段、`recipe_menu.commands.shop` 和 `recipe_menu.datafile` 的 `__all__` 列出的名称，以及作为常量的 `shop/messages.py` 和 `datafile/messages.py` 里的消息。 | mock 完整声明了它们，所以只测它们的测试会在 mock 上通过（R09）。F13-T01 在一次运行旁边检查这些字段，用例通过输出、文件或问题检查每一段文字。代码审查检查文字放在哪里，以及 `shop` 只导出它的命令（选择 11）。 |
| `shop` 只导入 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`menus` 和 `shopping`。 | R07。CI 里的依赖检查器把每个导入与架构第 3 节的表格比较。 |
| `shop` 只通过读取函数和 `replace_file` 访问磁盘，在文件之后只写一次输出，不保留状态或缓存。 | 没有接口能显示是哪个模块发起了调用，或者文字什么时候到达流。F13-T14 到 F13-T16 记录 `shop` 在磁盘上的每次调用，每个期望退出码 1 或 2 的用例都检查输出流为空，F13-T01 在一个文件夹上多次运行 `run`。其余由代码审查检查。 |
| 用超出 2.1 约束的 `Arguments` 调用 `run`：两个值，或者一个选项。 | `cli` 从不传入它们（F05 设计 2.10）。F13-T22 检查 `cli` 拒绝每一种这样的命令行。 |
| 目录里缺少所选语言的名称，`shop` 本会通过 `BiText.get` 用另一种语言显示它（选择 4）。 | `read_catalog` 对缺少某个名称的食材或分类给出错误（F03 设计 2.10），所以 `shop` 在这个错误处停下，从不显示这样的名称。F13-T17 的输入 3 检查这次停下。 |
| 路径里有 `..` 的 `replace_file`，比如 `folder.root / ".." / "x.md"`，以及文字不是 `str` 的情况。 | `DataFolder.relative` 比较两个路径的各部分，不解析 `..`（F03 设计 2.1），而 `shop` 传入的是 `shopping_file` 给出的路径。不是 `str` 的文字违反签名里的类型，由 mypy 检查。 |
| 保存期间进程被杀死，或者电脑断电。 | 那时删除无法运行，也没有测试能让进程停在选定的一步。F13-T05 的输入 4 和 F13-T12 的输入 3 检查下一次运行会删除中断的运行留下的 `temp`，F13-T10 和 F13-T20 检查 Ctrl+C。设计不调用 `fsync`，架构第 6 节也不要求。 |
| 来自控制台的真正 Ctrl+C、文件系统拒绝的访问，以及真正有第二个程序创建或打开着 `temp`。 | CI 机器没有控制台，Linux 上的 root 用户无视权限位，也没有测试能把第二个程序卡在某一步。故障工具抛出 `KeyboardInterrupt`，这正是 Python 对 Ctrl+C 抛出的异常，与 F05-T41 相同；它还在每个用例选定的那一步抛出 `PermissionError` 或制造竞争。F13-T21 用测试自己的句柄让旧文件保持打开，Windows 把它当作另一个程序。 |
| 在 `datetime.date` 最后日期附近的日子运行 `shop`。 | F06-T22 在那里测试了 `week_from_argument`，而电脑的时钟不会给出这样的日期（F06 设计 2.7）。 |
| Windows Terminal 里的中文输出，即 v0.1-S25。 | CI 机器没有 Windows 控制台（架构第 10 节），所以由 Troy 检查。F13-T12 检查中文清单的数量从同一个显示列开始，F13-T28 检查 `python -m recipe_menu` 把中文输出写成 UTF-8。 |
| Troy 手机上保存的清单，即 v0.1-S26。 | 它需要 Troy 的手机和 Troy 的同步工具。F13-T12 检查中文文件逐字节就是原型的文件，用 UTF-8，没有字节顺序标记。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的汉字。 |
| 设计第 2 节里对之后功能的计划：F14 用 `replace_file` 的 `menu suggest`，以及 F15 用 `create_file` 的 `add`。 | 每个之后功能的设计和测试方案会覆盖它们。F13-T05 的输入 7 检查 `replace_file` 能替换菜单文件。 |
| 发布测试里的 v0.1-S08、v0.1-S14 到 v0.1-S18、v0.1-S23 和 v0.1-S32。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 加入（TE5）。F13-T12、F13-T18 以及 F13-T23 到 F13-T27 在 `main` 上运行同样的步骤，F13-T30 在每次测试运行时在同类文件夹上为同一命令计时。 |

## 5. 与接口设计师的对齐记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-15 | 初稿。 |
| 1.0 | 2026-11-15 | Troy 批准。 |
| 1.1 | 2026-11-17 | 来自 F14 测试方案，对应 Troy 于 2026-11-17 批准的 F14 设计。F13-T01 拿 `main` 通过 `commands=` 得到的 v0.1 八个命令的帮助和 F05 原型的帮助比较，并按列检查真正 `COMMANDS` 的帮助里 `shop` 那一行。F13-T22 和 F13-T27 拿 `shop --help` 的帮助和运行 `--help` 的结果比较。所以 F14 加上 `menu suggest` 之后这三个用例仍然成立。`[F14 test-fix]` PR 修改这三个测试。 |
