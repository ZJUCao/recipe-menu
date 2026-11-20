---
troy-doc: "F15-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-20"
status: "Troy 已于 2026-11-20 批准"
mirror-of: "test-plan.md"
---

# F15 添加菜谱：测试方案

## 1. 功能

- 编号和名称：F15 添加菜谱
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.add` 的 `ADD_COMMAND`、`recipe_menu.commands.check` 的 `check_recipe` 和 `problem_block`、`recipe_menu.app` 的 `Context`、`recipe_menu.text` 的 `use_utf8_input`、`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的值调用 `ADD_COMMAND.run`、`Context`、带替身命令的 `main`、`use_utf8_input`、`check_recipe` 或 `problem_block`。功能用例像你输入 `recipe-menu add` 并回答它的问题那样，用一行命令和一个回答流运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 在 `SEARCH_COMMAND` 之后有 `ADD_COMMAND`（设计选择 1）。集成用例在 `main` 上运行一个 v0.2 场景，通过管道给出回答来启动 `python -m recipe_menu add`，构造随机的回答，或者在 PT01 数据文件夹上运行。为了知道保存的文件读回来应该是什么，用例还按各自的设计调用 `recipe_menu.catalog` 的 `read_catalog`、`Catalog.find_ingredient` 和 `Catalog.find_tag`，`recipe_menu.recipes` 的 `read_recipe`，以及 `recipe_menu.units` 的 `parse_quantity`。没有用例是性能用例（第 3 节）。每个用例写明它来自设计的哪一部分，比如（选择 9）。设计的七个示例和其中唯一的一行 `# raises` 分布在 F15-T01（2.1）、F15-T03（3.1 和 3.2）、F15-T04（3.3）、F15-T05（3.4）、F15-T06（3.5）和 F15-T07（2.2）里。

**A 点到 C 点。** Troy 于 2026-11-20 批准了设计 1.0，每一点都按建议：按 2.2 的写法接受 32 条消息（A）；名称的任一种语言、任一种语言的步骤，在另一种语言有文字时都可以留空，保存后的检查会对缺的语言给出警告（B）；帮助里 `add` 那一行紧接在 `search` 那一行之后（C）。用例用两种语言检查 A 点的每一条消息：

- `ADD_HELP`：F15-T01。
- 问题 1 到 7 的提问和 `EN_STEPS_OPTIONAL_PROMPT`：中文在 F15-T07 和 F15-T08，英文在 F15-T07 和 F15-T25。`EN_STEPS_PROMPT`：F15-T15，两种语言。份数不是 2 时的 `SERVINGS_PROMPT`：F15-T02。
- `NOT_AN_ID`：F15-T10。`ID_EXISTS`：F15-T09。`NAME_NEEDED`：F15-T11。`SERVINGS_WRONG`：F15-T12。两种形式的 `UNKNOWN_TAG` 和 `NO_TAGS`：F15-T13。`NAME_AND_QUANTITY`、`UNKNOWN_INGREDIENT` 和四条数量消息：F15-T14。`STEPS_NEEDED`：F15-T15。每条都用两种语言。
- `SAVED`：中文在 F15-T08，英文在 F15-T25。`SAVED_WITH_PROBLEMS`、两种形式的 `ERROR_COUNT` 和 `WARNING_COUNT`，以及 `FIX_AND_CHECK`：F15-T11、F15-T15 和 F15-T23，两种语言。
- `INPUT_ENDED`：F15-T17。`APPEARED`：F15-T21。`NOTHING_SAVED` 和 `LEFT_BEHIND`：F15-T22。每条都用两种语言。

B 点在 F15-T07、F15-T11、F15-T15、F15-T23 和 F15-T28 里。C 点在 F15-T01 里，也在下面对 F11-T01 的修改里。

**之前功能的测试。** 设计第 3 节指出 F15 会让一个已验收功能的测试失败。`tests/test_f11_commands.py` 里的 F11-T01 把真正 `COMMANDS` 的帮助里 `search` 那一行之后的两行当作 `menu new` 和 `menu show` 那两行。从 mock PR 起，`search` 之后的那一行是 `add` 那一行。在架构师的模型上，`ADD_COMMAND` 放在 `SEARCH_COMMAND` 之后，整套测试在 Windows 上 614 个通过、1 个失败、4 个跳过。唯一的失败是 F11-T01，4 个跳过是只在 Linux 上运行的用例。F07-T25 和 F10-T21 没有运行，因为评审用的沙盒无法给 PT01 计时（设计第 4 节）。开发者从不修改测试（R08），每个已验收功能的测试都必须通过（R10）。所以测试工程师在本方案之后、F15 的 mock PR 之前，用一个测试修正 PR 修改 F11-T01（TE3）。修改后，这个测试按开头找到 `menu new` 那一行，检查它在 `search` 那一行之后，并检查紧接其后的是 `menu show` 那一行，两种语言都这样检查。所以它在 F15 的 mock PR 之前和之后都成立，F16 在 `add` 之后加上 `edit ID` 时也成立。本 PR 让 F11 测试方案与这一修改一致（F11 测试方案版本 1.2）。这个测试修正 PR 不修改别的测试，也不修改任何辅助模块。

这些测试仍然成立，正如设计第 3 节所说。F07-T17 和 F13-T01 按开头找到它们那一行，并把它的文字列和 `--lang en|zh` 的文字列比较；`add` 的第一格宽 3 列，所以第二列仍从第 24 列之后开始。F08-T14、F09-T01、F10-T01 和 F14-T01 检查帮助里某一行跟在另一行后面，`add` 那一行不在其中任何一对之间。F09-T19、F11-T27、F11-T32、F11-T35、F13-T22、F13-T27、F14-T21 和 F14-T31 拿真正 `COMMANDS` 的一份帮助和另一份比较。`add` 是一个词，所以 `recipe-menu menu` 仍然只列出三个 `menu` 命令。F05-T10 和 F05-T11 比较设置的键，F15 不加键。F05 到 F14 的测试用六个或七个值构造上下文，没有比较两个只因新字段而不同的上下文。不传 `stdin` 调用 `main` 的测试得到 pytest 的 `sys.stdin`，它不是 `io.TextIOWrapper`，所以 `use_utf8_input` 不改变它，除了 `add` 也没有命令读取它。`check` 的报告通过 `problem_block` 写出它的各块时，F07 对这份报告的测试仍然成立。F05 测试方案的 `HELP_EN` 和 `HELP_ZH`、F05-T45、F02-T57 和 F13-T01 拿 v0.1 的帮助和字面量或 v0.1 的八个命令比较，所以 `add` 那一行不会让它们的步骤或预期结果出错。`init` 和 `menu new` 写出的文件和以前一样，所以 v0.1-S01、v0.1-S02 和 v0.1-S13 仍然成立。F15 的测试 PR 不修改之前功能的测试，不修改 `tests/data/example/` 里的文件，也不修改之前辅助模块里的函数。

**R09。** mock 定义了每条消息和带全部字段的 `ADD_COMMAND`，并把这一项加进 `COMMANDS`。它给 `Context` 加上带默认值的字段 `input`，给 `main` 加上参数 `stdin`，但不把它传下去。它的 `use_utf8_input` 什么也不改，它的 `check_recipe` 和 `problem_block` 给出 `()`，它的 `run` 不读文件、不读回答、什么也不写，给出 0（设计第 2 节）。所以，只检查 `ADD_COMMAND` 的字段、帮助、某条消息、退出码 0、空的错误流、`Context.input` 的默认值、上下文的相等、一个干净菜谱的 `check_recipe`、没有问题时的 `problem_block`，或者只检查一次运行没有写文件或没有读回答的测试，在 mock 上会通过。`cli` 在运行 `add` 之前做的事也是这样：缺少数据文件夹、设置有错、多出一个词、未知选项、全局选项写错，以及 `add --help`。检查这类内容的每个用例，还检查 mock 做错的某样东西：`add` 的输出（它总是以一个提问开头）、它给出的退出码 1 或 130、新文件的字节、停下或失败时的那几行、`main` 传下去的流、`use_utf8_input` 设置的编码，或者 `check_recipe` 和 `problem_block` 给出的问题和行。F15-T01、F15-T03、F15-T05、F15-T06、F15-T09、F15-T19 和 F15-T24 只在 mock 做错的结果旁边检查这类内容。每个预期 `add` 给出退出码 0 的用例都检查它的全部输出，而输出从不为空。`tests/f15_support.py` 和 `tests/f15_texts.py` 在被导入时不调用 F15 的任何接口。

**两个系统。** 每个用例都在 Linux 和 Windows 上运行，没有用例在任何一个系统上跳过。CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。问题用相对于数据文件夹的路径写出它的文件，用系统的分隔符。所以在预期的行里，`recipes/new-dish.toml` 代表 `str(Path("recipes", "new-dish.toml"))`：在 Windows 上是 `recipes\new-dish.toml`，和 F15 原型里路径的写法一样；在 Linux 上是 `recipes/new-dish.toml`。`SAVED`、`SAVED_WITH_PROBLEMS`、`APPEARED` 和 `LEFT_BEHIND` 用完整路径写出文件（选择 11）。以用例的文件夹开头的路径，比如 `F/recipes/new-dish.toml`，代表那个完整路径的 `str`。`add` 在两个系统上都写 UTF-8，换行符为 LF（选择 10）。没有用例需要某个系统做不出的条目。和 ID 只有大小写不同的名称（比如 `New-Dish.toml`），以及不是菜谱 ID 的名称（比如 `Rice Bowl.toml`），在两个系统上都是合法的文件名，也没有用例创建以 Windows 设备名命名的文件。所以 F15 没有用例加入只在 Linux 上运行的 F04-T12、F04-T51、F06-T28 和 F11-T11。

**被拒绝的访问。** 没有用例通过文件系统拒绝访问，不用 `os.chmod`、访问控制列表，也不用 `tests/f04_support.py` 的 `listing_denied`。Linux 上的 root 用户无视权限位，所以依赖它们的测试在 root 下会失败。用例里的每个 `PermissionError` 都来自故障工具，它对每个用户都以同样的方式抛出。所以每个用例在 Linux 上以 root 运行、在 Windows 上以管理员运行时都能通过。

**用例怎样让磁盘出错。** 用例使用 `tests/f13_support.py` 的 `shop_faults(base, *rules)`，规则和效果与 F13 和 F14 测试方案相同：用于以 `x` 模式打开 P 的 `open P: E` 和 `open P: race`，以及 `write P: E`、`close P: E`、`unlink P: E`、`read P: E` 和 `read P: later E`，效果有 `DENIED`、`IO`、`NO_SPACE` 和 `CTRL_C`。所以 `open recipes/new-dish.toml: race` 就在 `create_file` 打开文件之前用 `b"mine\n"` 创建这个文件，就像另一个程序那样。`read catalog.toml: later DENIED` 让 2.2 的第 1 步读到目录，并让 `check_recipe` 的那次读取失败。抛出 `KeyboardInterrupt` 的用例通过 `tests/f15_support.py` 的 `add` 从 `main` 得到退出码 130。这个辅助函数把离开 `main` 的 `KeyboardInterrupt` 变成一次失败，和 `tests/f08_support.py` 的 `call_main` 一样。

给开发者的说明：只有当 `add` 通过 `read_catalog`、`list_recipe_ids`、`create_file` 和 `check_recipe` 访问磁盘（设计第 2 节），并且它们保持 F11 和 F14 测试方案写明的那些调用时，这些用例才成立。绕过 `io.open`、`os.scandir`、`os.listdir` 或 `os.unlink` 的调用，比如 `os.open` 或 `Path.write_text`，会逃过故障工具，F15-T18、F15-T20、F15-T22 和 F15-T23 就会失败。

**读取的记录。** F15-T05 和 F15-T20 用不带规则的 `shop_faults(F.root)` 记录一次调用打开和删除了哪些文件、列出了哪些文件夹，和 F14-T14 一样。故障工具把数据文件夹下某个路径的每次打开记为 `read`，以 `x` 模式打开时记为 `open`，每次删除记为 `unlink`，每次移动记为 `move A B`，路径相对于该文件夹，用 `/` 分隔。它把每次用 `os.scandir` 或 `os.listdir` 的列举记在“列举记录”里。`cli` 在运行命令之前读取 `settings.toml`，所以 `main` 每次运行的记录都以 `read settings.toml` 开头。

**回答流。** `tests/f15_support.py` 给出这些输入流。每个流都装着它的回答 A 的各行，每行后面跟着 `"\n"`：

- A 的普通流是一个 `io.StringIO`，它的 `isatty()` 给出假。
- A 的终端流和普通流一样，但它的 `isatty()` 给出真，就像控制台那样。
- 受监视的流没有回答，一旦有东西用 `read`、`readline`、`readlines` 或迭代读取它，用例就失败。它的 `isatty()` 给出假。
- 在第 k 个回答处做修改 C 的 A 的钩子流，在给出 A 的第 k 行（从 1 数起）之前，对数据文件夹做修改 C，就像你在 `add` 等待时在另一个窗口里做的那样。“在它的最后一个回答处”指 A 的最后一行。
- 在第 k 个回答处停下的 A 的停止流，在第 k 行的位置抛出 `KeyboardInterrupt`，就像 Python 的控制台读取在提问处按下 Ctrl+C 时那样。
- 刷新记录是一个在每次 `flush()` 时记下自己全部文字的输出流，加上一个在每次 `readline()` 时记下那个输出流的文字的 A 的输入流。

这些规则适用于测试数据，和 F11、F13、F14 测试方案一样：

- `EXAMPLE` 是仓库里的文件夹 `tests/data/example/`（架构 10）。`tests/conftest.py` 的夹具 `example_folder` 把它复制到 `tmp_path / "recipe-menu"`，换行符为 LF，并给出这份副本上的 `DataFolder`。在用例里，`example` 就是这个 `DataFolder`。它的七个菜谱按 ID 顺序是 `choy-sum`、`cola-wings`、`mapo-tofu`、`red-braised-pork`、`rice`、`tomato-egg` 和 `tomato-egg-noodles`。“P 处的新示例”是用 `tests/f05_support.py` 的 `copy_example` 再做的一份副本。不带 P 的“新示例”在 `tmp_path` 下它自己的路径上。用例里的“一份副本”是带同样修改的新示例。
- `home` 是 `tmp_path / "home"`，一个由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。
- 测试用 `tests/f03_support.py` 的 `write` 写每个文件，它写 UTF-8，换行符为 LF，并先创建所需的文件夹；或者用 `put_bytes` 写字节。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 替换文件 F 里的第一个 X，它会检查 F 里有 X。
- 没有测试修改仓库、碰 `~/recipe-menu` 或读取时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`。F15-T27 通过 `tests/f15_support.py` 的 `pipe_module` 启动 `python -m recipe_menu`。它和 `tests/f05_support.py` 的 `run_module` 一样运行，环境也相同，所以 `HOME` 和 `USERPROFILE` 指向 `tmp_path` 里的一个文件夹，`PYTHONIOENCODING` 是 `ascii`；它还把用例的字节写到进程的标准输入，然后关闭它。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

这些有名字的修改构成用例的文件夹。每个修改作用于它所在用例的数据文件夹：

- 来自 F09、F11 和 F13 测试方案：没有目录、目录花括号、没有菜谱文件夹、菜谱是文件、Rice Bowl、大写的 rice、文件夹 x、麻婆错误、设置有错、只有一个标签、没有标签，以及没有菜单文件夹。`tests/f07_changes.py`、`tests/f09_support.py` 和 `tests/f11_support.py` 的辅助函数做这些修改。来自 F10 测试方案：中文设置。来自 F06 的辅助函数：菜单拼写错误。常备清单错误是 `tests/f07_changes.py` 的 `pantry_not_text` 做的修改。
- 条目 `recipes/N` 是写成 `b"mine\n"` 的文件 `recipes/N`，比如条目 `recipes/Garlic-Broccoli.toml`。
- 没有番茄，是把 `catalog.toml` 里的 `  { zh = "番茄", en = "Tomato", category = "produce" },\n` 换成 `""`，这样目录里没有 番茄，也仍然没有错误。

这些约定适用于对 `main` 的调用：

- 像“在 F 里用 A 运行 `add --lang zh`”这样的一行代表 `tests/f15_support.py` 的 `add(home, F, A, "--lang", "zh")`。它用 `["add", "--data", str(F.root), "--lang", "zh"]`、`home`、`environ={}`、`today=date(2026, 11, 10)`、两个新的 `io.StringIO` 流运行 `main`，不传 `commands`，`stdin` 设为 A 的普通流，或用例指明的流。“不指定文件夹”的一行没有 `--data`。
- 其他命令的一行，比如 `show garlic-broccoli` 或 `check`，通过 `tests/f09_support.py` 的 `at` 运行。`--help` 的行通过 `tests/f07_support.py` 的 `call` 运行。
- 反引号里的回答就是所显示的文字，比如 `快手, 素` 或 `a\b`。引号里的回答是带转义的 Python 字符串，比如 `""`、`" rice\t"` 或 `"\u3000"`，其中每个 `\uXXXX` 或 `\xXX` 代表那一个字符。“没有回答”是一个空流。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟着 `"\n"`。`(c, out L, err M)` 用同样的方式给出两个流，`(c, err M)` 的 out 为空。用例把 out 写成一段文字时，那段文字就是 out 的全部。测试比较完整的文字。
- 用例里的“这个文件”是它的回答中那个 ID 的 `F.recipe_file(ID)`。“`recipes/` 的列表”是它的条目名称按排序列出的结果，和 `os.listdir` 给出的一样，所以每个名称都和系统保存的完全相同。
- `STOP(W, M)` 和 `STOP_ZH(W, M)` 是 `stop_at_error` 的英文和中文三行，按 F09 测试方案的定义，由 `tests/f09_texts.py` 的 `stop` 构造结果。W 是一个文件，或者一个文件和一个位置，比如 `catalog.toml, line 11`。
- “在 `check` 的错误之中”的含义和 F09 测试方案相同，由 `tests/f09_support.py` 的 `assert_among_check` 检查。

用例的回答如下：

- `S09` 是设计 2.2 的示例里 `chinese` 的 19 个回答，也就是 v0.2-S09 的回答。`S10` 是那里 `english` 的 22 个回答，也就是 v0.2-S10 的回答。`PARTLY` 是 `partly` 的 11 个回答。
- `BASE(ID)` 是这 11 个回答：`ID`、`新菜`、`New dish`、`""`、`quick`、`番茄 300 g`、`""`、`番茄切块。`、`""`、`Cut the tomatoes.` 和 `""`。`BASE` 是 `BASE(new-dish)`。所以回答 1 到 5 回答问题 1 到 5。回答 6 是唯一的一行食材，回答 7 结束这个列表；回答 8 是那一步中文步骤，回答 9 结束这个列表；回答 10 是那一步英文步骤，回答 11 结束这个列表。
- “BASE，其中 Q：X1, ..., Xn”是把问题 Q 的回答换成 X1 到 Xn 的 BASE，比如“BASE，其中份数：`0`、`3`”。这些问题是 ID、中文名、英文名、份数、标签、食材、中文步骤和英文步骤。对一个列表，X1 到 Xn 替换列表的各行，结束列表的空回答跟在它们后面。“BASE，没有中文步骤”让这个列表只有它的空回答，食材和英文步骤也一样。
- `ESCAPES` 是这 12 个回答：`odd-text`、`老"家"\菜`、`"Home\tstyle \x00\x01\x10 \"best\""`、`""`、`素`、`番茄 300 g`、`""`、`"第一行\u2028第二行"`、`"加 1 勺\"糖\"\u3000和盐。"`、`""`、`Use C:\path and "x".` 和 `""`。
- `PT01_ANSWERS` 是这 12 个回答：`size-check`、`规模检查`、`Size check`、`""`、`quick`、`食材300 100 g`、`食材150 适量`、`""`、`把食材洗净切好。`、`""`、`Wash and cut the ingredients.` 和 `""`，也就是 v0.2-S16 第 2 步的回答。

预期的文字如下。测试在 `tests/f15_texts.py` 里把每一段写成字面量，或者在那里用字面量模板构造出来。它们不引用 `add`、`check`、`app` 或 `text` 的任何消息，也从不读取原型文件，因为这些消息都是内部的（设计第 2 节，架构 8）。

- `add` 的 32 条消息是设计 2.2 里的消息，用它表格里的名称，带上占位符的值，比如 `NOT_AN_ID(id="Tomato-Egg")` 或 `SAVED(file=F/recipes/new-dish.toml)`。`X_ZH` 是 X 的中文文字，比如 `NOT_AN_ID_ZH(id="Tomato-Egg")`。`SAVED_WITH_PROBLEMS(P, e, w)` 写出文件 P，并在 `problems` 里按 2.2 的构造方式给出 e 个错误和 w 个警告的数目，比如 `Saved F/recipes/new-dish.toml. The check found 1 error and 2 warnings:`。
- 问题 Q 的回答 a 那一行，是 Q 的提问后面跟着照原样输入的 a，比如 `Servings [2]: 0`；回答为空时是带着那个空格的 `Servings [2]: `。列表里回答 a 那一行是两个空格后面跟着 a，所以空回答那一行是两个空格。
- `TAGS(V)`、`TAGS_ZH(V)`、`ONE_TAG(V)`、`ONE_TAG_ZH(V)`、`NO_TAGS(V)` 和 `NO_TAGS_ZH(V)` 和 F14 测试方案里的相同：示例的目录、只有一个标签的目录和没有标签的目录下 `UNKNOWN_TAG` 和 `NO_TAGS` 的文字。
- `HELP_15` 是十个命令的帮助的 23 行：F05 原型“Help in English”一节的第 1 到 4 行，设计 2.1 英文代码块从 `Commands:` 到 `  --help                Show this help.` 的 17 行，一个空行，以及 `WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.` 这一行。`HELP_15_ZH` 用同样的方式由“Help in Chinese”一节和设计 2.1 的中文代码块构成。
- `S09_OUT(F)` 是设计 2.2 里 `add` 的第一次运行给出的 24 行，从 `菜谱 ID（也是文件名）：garlic-broccoli` 到 `已保存 F/recipes/garlic-broccoli.toml。检查没有发现问题。`。`S09_FILE` 是它那个文件的 22 行，作为字节。
- `BLOCK(P1, ..., Pn)` 是问题 P1 到 Pn 用输出语言写出的 `problem_block` 的各行：每个问题先是两个空格和它的文件及位置，写法同 `problem_lines`，然后是四个空格和它的文字。一个问题写成它的文件、位置和消息，比如 `recipes/new-dish.toml at name with NO_ZH_NAME`。
- 用例里读取器的消息是 F04、F09 和 F14 测试方案里的消息，由 `tests/f03_support.py`、`tests/f04_support.py` 和 `tests/f09_texts.py` 保存：`NO_ZH_NAME`、`NO_EN_NAME`、`NO_ZH_STEPS`、`NO_EN_STEPS`、菜谱的 `UNKNOWN_INGREDIENT(name="番茄")`、`FILE_MISSING`、`FOLDER_MISSING`、`FOLDER_IS_FILE`、`MISSING_BRACE`、`ACCESS_DENIED`、列举的 `NOT_A_RECIPE_ID`、`TOML_ENDING_NOT_SMALL`，以及设置的 `UNKNOWN_MEAL(meal="supper")`，位置有 `name`、`steps`、`ingredient N`、`line 11` 和 `meals`。`FILE_WRITE_DENIED` 和 `FILE_WRITE_ERROR(reason="X")` 是 `tests/f08_texts.py` 里的消息。`cli` 的消息是 F05 设计 2.10 里的文字，命令为 `add`。
- `BASE_OUT(F)`、`BASE_OUT_ZH(F)`、`BASE_FILE`、`S10_OUT(F)`、`S10_FILE`、`TEXT_G`、`PT01_OUT(F)` 和 `PT01_FILE` 是下面的代码块。

在下面的代码块里，每一行都以 LF 结尾，最后一行也是。`<SP>` 代表一个空格 U+0020，代码块只在行末显示它。`<U+XXXX>` 代表那一个字符。F 代表数据文件夹的完整路径。

`BASE_OUT(F)`，BASE 的输出：

```text
Recipe ID (also the file name): new-dish
Chinese name: 新菜
English name: New dish
Servings [2]:<SP>
Tags, separated by commas: quick
Ingredients, one per line, as "name quantity". An empty line ends the list:
  番茄 300 g
<SP><SP>
Chinese steps, one per line. An empty line ends the list:
  番茄切块。
<SP><SP>
English steps, one per line. An empty line ends the list (optional):
  Cut the tomatoes.
<SP><SP>
Saved F/recipes/new-dish.toml. The check found no problems.
```

`BASE_OUT_ZH(F)`，带 `--lang zh` 时 BASE 的输出：

```text
菜谱 ID（也是文件名）：new-dish
中文名：新菜
英文名：New dish
份数 [2]：
标签，用逗号分隔：quick
食材，每行一个，写“名称 数量”，空行结束：
  番茄 300 g
<SP><SP>
中文步骤，每行一步，空行结束：
  番茄切块。
<SP><SP>
英文步骤，每行一步，空行结束（可以不写）：
  Cut the tomatoes.
<SP><SP>
已保存 F/recipes/new-dish.toml。检查没有发现问题。
```

`BASE_FILE`，BASE 的文件：

```toml
name = { zh = "新菜", en = "New dish" }
servings = 2
tags = ["quick"]

ingredients = [
  { item = "番茄", amount = "300 g" },
]

[steps]
zh = [
  "番茄切块。",
]
en = [
  "Cut the tomatoes.",
]
```

`S10_OUT(F)`，S10 的输出：

```text
Recipe ID (also the file name): egg-fried-rice
Chinese name: 蛋炒饭
English name: Egg fried rice
Servings [2]: 0
Servings must be a whole number from 1 to 100, such as 2.
Servings [2]: two
Servings must be a whole number from 1 to 100, such as 2.
Servings [2]: 3
Tags, separated by commas: breakfast
Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.
Tags, separated by commas: quick, staple
Ingredients, one per line, as "name quantity". An empty line ends the list:
  Rice 1 cups
  Unknown unit "cups" in "1 cups".
  Rice 300 g
  Egg 3
  Peanut 30 g
  The catalog has no "Peanut". Enter a name from the catalog, or add it to the catalog first and then run add again.
  Scallion 1 stalk
  Salt to taste
  Cooking oil 2 tbsp
<SP><SP>
Chinese steps, one per line. An empty line ends the list:
  鸡蛋打散。
  热油炒蛋，加米饭和葱花翻炒。
<SP><SP>
English steps, one per line. An empty line ends the list (optional):
  Beat the eggs.
  Scramble the eggs, then stir-fry them with the rice and scallion.
<SP><SP>
Saved F/recipes/egg-fried-rice.toml. The check found no problems.
```

`S10_FILE`，S10 的文件：

```toml
name = { zh = "蛋炒饭", en = "Egg fried rice" }
servings = 3
tags = ["quick", "staple"]

ingredients = [
  { item = "Rice", amount = "300 g" },
  { item = "Egg", amount = "3" },
  { item = "Scallion", amount = "1 stalk" },
  { item = "Salt", amount = "to taste" },
  { item = "Cooking oil", amount = "2 tbsp" },
]

[steps]
zh = [
  "鸡蛋打散。",
  "热油炒蛋，加米饭和葱花翻炒。",
]
en = [
  "Beat the eggs.",
  "Scramble the eggs, then stir-fry them with the rice and scallion.",
]
```

`TEXT_G`，ESCAPES 的文件。其中每个 `\` 都是文件里的一个反斜杠字符：

```toml
name = { zh = "老\"家\"\\菜", en = "Home\u0009style \u0000\u0001\u0010 \"best\"" }
servings = 2
tags = ["素"]

ingredients = [
  { item = "番茄", amount = "300 g" },
]

[steps]
zh = [
  "第一行<U+2028>第二行",
  "加 1 勺\"糖\"<U+3000>和盐。",
]
en = [
  "Use C:\\path and \"x\".",
]
```

`PT01_OUT(F)`，PT01_ANSWERS 的输出：

```text
Recipe ID (also the file name): size-check
Chinese name: 规模检查
English name: Size check
Servings [2]:<SP>
Tags, separated by commas: quick
Ingredients, one per line, as "name quantity". An empty line ends the list:
  食材300 100 g
  食材150 适量
<SP><SP>
Chinese steps, one per line. An empty line ends the list:
  把食材洗净切好。
<SP><SP>
English steps, one per line. An empty line ends the list (optional):
  Wash and cut the ingredients.
<SP><SP>
Saved F/recipes/size-check.toml. The check found no problems.
```

`PT01_FILE`，PT01_ANSWERS 的文件：

```toml
name = { zh = "规模检查", en = "Size check" }
servings = 2
tags = ["quick"]

ingredients = [
  { item = "食材300", amount = "100 g" },
  { item = "食材150", amount = "适量" },
]

[steps]
zh = [
  "把食材洗净切好。",
]
en = [
  "Wash and cut the ingredients.",
]
```

用例分在这些文件里，使每个文件不超过 R06 的 500 行：

| 文件 | 内容 |
| --- | --- |
| `tests/test_f15_command.py` | F15-T01 和 F15-T02。 |
| `tests/test_f15_values.py` | F15-T03 到 F15-T06。 |
| `tests/test_f15_session.py` | F15-T07 到 F15-T09。 |
| `tests/test_f15_answers.py` | F15-T10 到 F15-T13。 |
| `tests/test_f15_lists.py` | F15-T14 和 F15-T15。 |
| `tests/test_f15_file.py` | F15-T16。 |
| `tests/test_f15_input.py` | F15-T17 和 F15-T18。 |
| `tests/test_f15_reads.py` | F15-T19 和 F15-T20。 |
| `tests/test_f15_save.py` | F15-T21 和 F15-T22。 |
| `tests/test_f15_after_save.py` | F15-T23。 |
| `tests/test_f15_cli.py` | F15-T24。 |
| `tests/test_f15_integration.py` | F15-T25 到 F15-T27。 |
| `tests/test_f15_random.py` | F15-T28。 |
| `tests/test_f15_size.py` | F15-T29。 |
| `tests/f15_support.py` | 没有测试。带回答调用 `main`、各种回答流、在标准输入上带字节运行 `python -m recipe_menu`、按帮助顺序排列的 F15 的十个命令、各组回答，以及文件夹的修改。它的文档注释遵循 P01。 |
| `tests/f15_texts.py` | 没有测试。上面的预期文字和代码块，写成字面量，以及输出各行的构造函数。它的文档注释遵循 P01。 |
| `tests/conftest.py` | 不变。F15 使用它的夹具 `example_folder` 和 `default_int_limit`，以及 pytest 的 `tmp_path` 和 `monkeypatch`。 |

某个文件超过 500 行时，测试工程师可以把它再拆开。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F15-T01 | 单元 | `ADD_COMMAND`、`ADD_COMMAND.run`、`main` | 2.1 的示例。`ADD_COMMAND` 的词是 `add`，两种语言的用法都是 `add`，帮助行是 A 点的那一行，没有参数，没有选项，`FolderUse.READ`。对一个已有的 ID 和一个空回答，它的 `run` 写出 F15 原型“An ID that exists”一节的各行，给出 0。十个命令的帮助有 23 行，`add` 那一行紧接在 `search` 那一行之后，两种语言的第二列都从第 24 列之后开始。在真正 `COMMANDS` 的帮助里，`add` 那一行在 `search` 那一行之后，它的文字和 `--lang en\|zh` 的文字在同一列（2.1，选择 1，C 点）。 | 示例的各行，`folder` 为 `example`，`home` 为 `home`。在 `help_lines` 里，对 `main` 的调用还传入 `commands=` 按帮助顺序排列的 F15 的十个命令：`tests/v01_commands.py` 的 `V01_COMMANDS`，在 `SEARCH_COMMAND` 之后加上 `ADD_COMMAND`，在 `MENU_SHOW_COMMAND` 之后加上 `MENU_SUGGEST_COMMAND`，因为这 23 行只在 F16 加入 `edit` 之前成立。然后：1. `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部。2. 用真正的 `COMMANDS`，通过 `call` 运行 `--help` 和 `--help --lang zh`。 | 示例的每个断言都成立。1. `HELP_15` 和 `HELP_15_ZH`。2. 退出码 0，err 为空。在 out 里，一个以 `  add ` 开头、以 `Add a recipe by answering questions.` 结尾的行在以 `  search WORD... ` 开头的那一行之后。中文里，一个以 `  add ` 开头、以 `回答问题，添加一个菜谱。` 结尾的行在以 `  search 词... ` 开头的那一行之后。每一行的文字和以 `  --lang en\|zh` 开头的那一行的文字从同一个显示列开始，量法同 F11-T01。F16 加入 `edit ID` 之后，这些规则仍然成立。 |
| F15-T02 | 单元 | `ADD_COMMAND.run` | `run` 用 `context.lang` 写出它的各行，从不用 `context.settings` 的语言。它在问题 4 的提问里显示 `context.settings.servings`，并把它给空回答。它从 `context.input` 读取回答，只写到 `context.out` 和 `context.err`，不从 `context.random` 取任何东西，不依赖 `context.today`，也不在两次调用之间保留状态（2.1，2.2，选择 4 和 7）。 | 每一行用新的流、一个新示例 F、BASE 的普通流 I 和 `tests/f14_support.py` 的一个新的前取来源 R 调用 `ADD_COMMAND.run(Context(L, F, S, out, err, D, random=R, input=I), Arguments())`；R 的任何抽取都会让用例失败，它的 `sample` 会记下调用。1. L 为 `Lang.ZH`，S 为 `Settings(Lang.EN, (Meal.DINNER,), 5)`，D 为 `date(2030, 1, 1)`。2. L 为 `Lang.EN`，S 为 `Settings(Lang.ZH, tuple(Meal), 1)`，D 为 `date(2026, 11, 10)`。3. L 为 `Lang.EN`，S 为 `Settings(servings=100)`，D 为 `date(2026, 11, 10)`。4. 在第二个新示例 G 里再运行第 2 行。 | 1. `(0, out L1)`，其中 L1 是把 `份数 [2]：` 换成 `份数 [5]：` 的 `BASE_OUT_ZH(F)`，这个文件是带 `servings = 5` 的 `BASE_FILE`。2. `(0, out L2)`，其中 L2 是把 `Servings [2]: ` 换成 `Servings [1]: ` 的 `BASE_OUT(F)`，这个文件是带 `servings = 1` 的 `BASE_FILE`。3. 同样，带 `Servings [100]: ` 和 `servings = 100`。4. 第 2 行的结果，用 G 代替 F，文件相同。每一行里 R 都没有记下调用。 |
| F15-T03 | 单元 | `Context`、`main` | 3.1 和 3.2 的示例。`Context` 得到字段 `input`，在字段顺序里排第八，不带它构造的每个上下文都得到一个新的空 `io.StringIO`。两个上下文的八个字段都相等时它们相等，流和生成器按对象比较，`Context` 可以求哈希，并且不可修改。`main` 把它作为 `stdin` 得到的流放进 `Context.input` 传给命令。没有 `stdin` 时，它在 `use_utf8_input` 之后传入 `sys.stdin`。`main` 不从这个流读取任何东西，除了 `add` 也没有命令读取它（3.1，3.2，设计第 3 节）。 | 3.1 的示例。3.2 的示例，`folder` 为 `example`，`home` 为 `home`。然后：1. `dataclasses.fields(Context)` 的名称。2. 用同样八个值构造的两个上下文，以及第三个用另一个 `io.StringIO` 作为 `input` 的上下文。3. 在 3.1 示例的上下文上执行 `context.input = io.StringIO()`。4. 用 `monkeypatch.setattr` 把 `sys.stdin` 设为 W，即 `encoding="cp1252"`、建在 `io.BytesIO(b"\xef\xbb\xbf" + "salt 适量\r\n".encode())` 上的 `io.TextIOWrapper`：不带 `stdin` 进行 3.2 示例里对 `main` 的调用。5. 把 `sys.stdin` 设为一个受监视的流：在 `example` 里不带 `stdin` 运行 `list`、`check`、`show tomato-egg`、`menu show 2026-W47` 和 `--help`。 | 两个示例的每个断言都成立。1. `lang`、`folder`、`settings`、`out`、`err`、`today`、`random` 和 `input`。2. 前两个相等，哈希相同，第三个和它们都不相等。3. 抛出 `dataclasses.FrozenInstanceError`。4. `(0, out ["SALT 适量"])`，之后 `(W.encoding, W.errors)` 是 `("utf-8-sig", "replace")`。5. 退出码 0，输出分别是 F09 和 F07 测试方案的 `LIST`、`AFTER` 和 `TOMATO`，F11 测试方案的 `SHOW_47`，以及没有受监视的流时 `--help` 的 out。受监视的流没有记下读取。 |
| F15-T04 | 单元 | `use_utf8_input` | 3.3 的示例。对 `io.TextIOWrapper`，`use_utf8_input` 设置编码 `utf-8-sig` 和错误处理 `replace`。之后这个流丢掉开头的字节顺序标记，保留别处的标记，把每个不是 UTF-8 的字节变成 U+FFFD，并且在 CR LF 和 LF 处都结束一行。别的流保持原样（3.3）。 | 示例的各行。然后对每个建在字节 B 的 `io.BytesIO` 上的 `io.TextIOWrapper`，在 `use_utf8_input` 之后用 `readline` 读，直到它给出 `""`：1. B 为 `b"a\n\xef\xbb\xbfb\n"`，`encoding="ascii"`。2. B 为 `"西兰花 300 g\r\n盐 适量\n".encode("utf-8")`，`encoding="gbk"`。3. B 为 `b"\x80\xfe\n\xe8\xa5"`，`encoding="latin-1"`。4. 对 `Rice 300 g` 的终端流和 `io.StringIO("x\r\ny\n")` 调用 `use_utf8_input`。 | 示例的每个断言都成立。1. `"a\n"` 和 `"\ufeffb\n"`。2. `"西兰花 300 g\n"` 和 `"盐 适量\n"`。3. `"\ufffd\ufffd\n"` 和 `"\ufffd"`。4. 终端流仍然给出 `"Rice 300 g\n"`，它的 `isatty()` 给出真。`io.StringIO` 给出 `"x\r\n"` 和 `"y\n"`，所以它的换行符保持原样。 |
| F15-T05 | 单元 | `check_recipe` | 3.4 的示例。`check_recipe` 先给出 `read_catalog` 的错误，再给出用那个目录（目录有错误时用 `None`）的 `read_recipe` 的问题，每个都带严重程度、文件、位置和文字。它在读取任何文件之前检查 ID，`catalog.toml` 和菜谱文件各读一次，不列举文件夹，什么也不写（3.4）。 | 示例的各行，`folder` 为 `example`，它的 `# raises` 那一行放在 `pytest.raises(ValueError)` 里。然后，每一行在一个新示例 F 里、在 `shop_faults(F.root)` 之内：1. `check_recipe(F, "tomato-egg")`。2. F 带目录花括号：`check_recipe(F, "red-braised-pork")`。3. `check_recipe(F, "garlic-broccoli")`，它没有文件。4. 在 `pytest.raises(ValueError)` 里，对 `""`、`"con"`、`"tomato egg"` 和 `"rice.toml"` 中的每个 V 调用 `check_recipe(F, V)`。5. 在第 1 到 4 行之前和之后对 F 做 `tests/f07_support.py` 的 `snapshot`。 | 示例的每个断言都成立。1. `()`，记录为 `read catalog.toml` 和 `read recipes/tomato-egg.toml`，没有列举。2. 按这个顺序的两个问题：`catalog.toml` 在 `line 11` 的错误 `MISSING_BRACE`，然后是 `recipes/red-braised-pork.toml` 在 `steps` 的警告 `NO_EN_STEPS`，每个都带它的英文和中文文字。3. `recipes/garlic-broccoli.toml` 的一个错误，没有位置，`FILE_MISSING`。4. 每次调用都抛出，记录保持为空。5. 两次快照相同。 |
| F15-T06 | 单元 | `problem_block` | 3.5 的示例。`problem_block` 按参数的顺序给每个问题两行：两个空格和 `problem_lines` 的 `where`，然后四个空格和 `what`，用它得到的语言，没有换行。它接受任何可迭代对象，生成器也可以，没有问题时给出 `()`（3.5）。 | 示例的各行。然后，用示例的 `problem` 和 `missing`：1. `problem_block([problem, missing], Lang.EN)`。2. `problem_block(iter([missing, problem]), Lang.ZH)`。3. `problem_block((item for item in [warning]), Lang.EN)`，其中 `warning` 是 `Problem.warning(rice, BiText("steps", "步骤"), Message("No English steps.", "没有英文步骤。"))`，`rice` 是 `Path("recipes", "rice.toml")`。 | 示例的每个断言都成立。1. `(f"  {mapo}, ingredient 3", '    Unknown ingredient "豆瓣酱".', "  catalog.toml", "    The file is missing.")`。2. `("  catalog.toml", "    文件不存在。", f"  {mapo}，食材 3", "    未知食材“豆瓣酱”。")`。3. `(f"  {rice}, steps", "    No English steps.")`。没有一行含有 `"\n"`。 |
| F15-T07 | 功能 | `recipe-menu add`、`main` | 2.2 的示例，按顺序：v0.2-S09，v0.2-S10 每种错误回答各一个，一个没有英文名、没有英文步骤、检查发现两个警告的菜谱，在问题 2 之后结束的回答，空的第一个回答，以及完全没有回答（2.2，选择 3 到 12，B 点）。 | 示例的各行，`folder` 为 `example`，`home` 为 `home`。它的 `add` 是 `tests/f15_support.py` 的 `add`，对 `main` 的调用相同。 | 示例的每个断言都成立。 |
| F15-T08 | 功能 | `recipe-menu add`、`recipe-menu show`、`recipe-menu list`、`recipe-menu check`、`main` | F15 原型“In Chinese, with one wrong answer”一节，以及 `main` 上的 v0.2-S09。每个提问和它的回答显示在同一行，`橄榄油 1 tbsp` 在两个空格之后得到 `UNKNOWN_INGREDIENT`，`add` 询问下一行，最后一行用完整路径写出新文件。这个文件的格式和示例的菜谱相同，`show`、`list` 和 `check` 像读任何菜谱一样读它（选择 3、4、9、10 和 12，A 点）。 | 1. 在 `example` 里用 S09 运行 `add --lang zh`。2. 然后在 `example` 里运行 `show garlic-broccoli`、`show garlic-broccoli --lang zh`、`list` 和 `check`。3. 在一个用 `put_bytes` 把 `S09_FILE` 写成 `recipes/garlic-broccoli.toml` 的新示例 G 里运行第 2 步的四行。 | 1. `(0, out S09_OUT(example))`。这个文件是 `S09_FILE`，`recipes/` 的列表是示例的 7 个名称和 `garlic-broccoli.toml`，示例的 7 个菜谱保持它们的字节。2. 每一行给出 G 里同一行的结果。`show garlic-broccoli` 以 `Garlic broccoli  蒜蓉西兰花` 和 `Servings: 2   Tags: quick, vegetarian` 两行开头。`list` 里 `garlic-broccoli` 那一行紧接在 `cola-wings` 那一行之后，最后一行是 `8 recipes.`。`check` 给出把 `7 recipes` 换成 `8 recipes` 的 `(0, out AFTER)`。 |
| F15-T09 | 功能 | `recipe-menu add`、`main` | F15 原型“An ID that exists”一节，以及 `main` 上的 v0.2-S11。`recipes/` 的列举里已有的 ID 得到 `ID_EXISTS`，它写出这个 ID 和 `recipe-menu edit`，然后再问问题 1。问题 1 处的空回答、只有空白的回答或输入结束，都以退出码 0 结束 `add`，不写文件。回答那一行照原样显示回答，消息写出去掉两端空白的回答（选择 4 和 5，A 点）。 | R 处的一个新示例 F，在第 1 行之前和每一行之后对 R 做 `tests/f07_support.py` 的 `snapshot`。1. 用 `tomato-egg` 和 `""` 运行 `add`。2. 用 `tomato-egg` 和 `""` 运行 `add --lang zh`。3. 用 `""` 运行 `add --lang zh`。4. 不给回答运行 `add`。5. 用 `"   "` 运行 `add`。6. 用 `" rice\t"`、`tomato-egg-noodles`、`choy-sum` 和 `""` 运行 `add`。 | 1. `(0, out [ID_PROMPT + "tomato-egg", ID_EXISTS(id="tomato-egg"), ID_PROMPT])`，其中 `ID_PROMPT` 以它的空格结尾。2. `(0, out [ID_PROMPT_ZH + "tomato-egg", ID_EXISTS_ZH(id="tomato-egg"), ID_PROMPT_ZH])`。3. `(0, out [ID_PROMPT_ZH])`。4. `(0, out [ID_PROMPT])`。5. `(0, out [ID_PROMPT + "   "])`。6. `(0, out L)`，其中 L 是 `ID_PROMPT + " rice\t"`、`ID_EXISTS(id="rice")`、`ID_PROMPT + "tomato-egg-noodles"`、`ID_EXISTS(id="tomato-egg-noodles")`、`ID_PROMPT + "choy-sum"`、`ID_EXISTS(id="choy-sum")` 和 `ID_PROMPT`。每次快照都等于第一次：没有文件或文件夹变化，也没有添加条目。 |
| F15-T10 | 功能 | `recipe-menu add`、`main` | ID。违反菜谱 ID 规则的回答得到带着去掉两端空白的回答的 `NOT_AN_ID`，然后再问问题 1。和文件夹里某个菜谱只有大小写不同的 ID 不是 ID。`recipes/` 里任何种类的条目都给出 `ID_EXISTS`，文件夹也一样。正确的 ID 进入问题 2（选择 5，F04 设计 2.4）。 | 每一行在一个新示例 F 里。1. 用 `Tomato-Egg`、`TOMATO-EGG`、`tomato egg`、`tomato_egg`、`-tomato`、`rice.`、`a/b`、`a\b`、`a:b`、`番茄炒蛋`、`"\uff54omato-egg"`、`con`、`nul` 和 `lpt9`，再加 `""` 运行 `add`。2. 用 `Tomato-Egg` 和 `""` 运行 `add --lang zh`。3. 文件夹 x：用 `x` 和 `""` 运行 `add`。4. 用 `Tomato-Egg`，然后用 BASE(`tomato-egg-2`) 的回答运行 `add`。 | 1. 退出码 0，err 为空。out 是对每个回答 a 的 `ID_PROMPT + a` 和 `NOT_AN_ID(id=a)`，最后是 `ID_PROMPT`。`recipes/` 的列表保持为示例的列表。2. `(0, out [ID_PROMPT_ZH + "Tomato-Egg", NOT_AN_ID_ZH(id="Tomato-Egg"), ID_PROMPT_ZH])`。3. `(0, out [ID_PROMPT + "x", ID_EXISTS(id="x"), ID_PROMPT])`，`recipes/x.toml` 仍然是一个空文件夹。4. `(0, out L)`，其中 L 是 `ID_PROMPT + "Tomato-Egg"`、`NOT_AN_ID(id="Tomato-Egg")`，以及把 `new-dish` 换成 `tomato-egg-2` 的 `BASE_OUT(F)` 的各行。文件 `recipes/tomato-egg-2.toml` 是 `BASE_FILE`，`recipes/tomato-egg.toml` 保持它的字节。 |
| F15-T11 | 功能 | `recipe-menu add`、`main` | 名称（B 点）。另一个名称有文字时，任一个名称都可以留空。两者都为空时，`add` 写出 `NAME_NEEDED` 并再问问题 3，中文名仍然为空。只有空白的回答算空，名称里面的空白照原样算。文件省去为空的语言，保存后的检查对它给出警告，退出码为 0（选择 3、6、10 和 12）。 | 每一行在一个新示例 F 里。1. 用 BASE，其中中文名：`""`，运行 `add`。2. 用 BASE，其中英文名：`""`，运行 `add`。3. 用 BASE，其中中文名：`""`，英文名：`""`、`"\u3000"`、`New dish`，运行 `add`。4. 第 3 行带 `--lang zh`。5. 用 BASE，其中中文名：`"\u3000新菜 "`，英文名：`" New  dish\t"`，运行 `add`。 | 1. `(0, out L1)`，其中 L1 是把 `Chinese name: 新菜` 换成 `Chinese name: `、并把最后一行换成 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 0, 1)` 和 `BLOCK(recipes/new-dish.toml at name with NO_ZH_NAME)` 的 `BASE_OUT(F)`。这个文件是第一行为 `name = { en = "New dish" }` 的 `BASE_FILE`。2. 同样，带 `English name: `、`NO_EN_NAME` 和 `name = { zh = "新菜" }`。3. 把 `English name: New dish` 那一行换成 `English name: `、`NAME_NEEDED`、`English name: \u3000`、`NAME_NEEDED` 和 `English name: New dish` 的 L1，文件和第 1 行相同。4. 第 3 行的中文各行：`中文名：`、`英文名：`、`NAME_NEEDED_ZH`、`英文名：\u3000`、`NAME_NEEDED_ZH` 和 `英文名：New dish`，最后是 `SAVED_WITH_PROBLEMS_ZH(F/recipes/new-dish.toml, 0, 1)`、`  recipes/new-dish.toml，名称` 和 `    没有中文名称。命令会改为显示英文名称。`。5. `(0, out L)`，其中 L 是带 `Chinese name: \u3000新菜 ` 和 `English name:  New  dish\t` 的 `BASE_OUT(F)`，这个文件是第一行为 `name = { zh = "新菜", en = "New  dish" }` 的 `BASE_FILE`。 |
| F15-T12 | 功能 | `recipe-menu add`、`main` | 份数。正确的回答是一个或多个 ASCII 数字、没有别的，值在 1 到 100 之间，所以前导零也算。其他每个回答都得到 `SERVINGS_WRONG`，然后再问问题 4：全角数字或其他文字的数字、正负号、小数、下划线、指数，以及几千位数字，都从不抛出。两端的空白不算，空回答给出设置里的份数（选择 7）。 | 带夹具 `default_int_limit`，它保持 Python 对 `int` 位数的默认限制。1. 在一个新示例 F 里，用 BASE，其中份数：`0`、`00`、`101`、`two`、`2.5`、`-1`、`+3`、`3 份`、`"\uff13"`、`"\u0663"`、`1_0`、`1e2`、5,000 个 `1` 组成的文字，以及 `03`，运行 `add`。2. 在一个新示例 F 里，用 BASE，其中份数：`two`、`""`，运行 `add --lang zh`。3. 在一个新示例 F 里，用 BASE(`d-1`)，其中份数：`1`，运行 `add`，然后是 BASE(`d-100`)，其中份数：`100`，BASE(`d-0100`)，其中份数：`0100`，以及 BASE(`d-7`)，其中份数：`" 7\t"`。 | 1. `(0, out L)`，其中 L 是把 `Servings [2]: ` 那一行换成每个错误回答 a 的 `Servings [2]: ` + a 和 `SERVINGS_WRONG`、再加 `Servings [2]: 03` 的 `BASE_OUT(F)`。这个文件是带 `servings = 3` 的 `BASE_FILE`。2. `(0, out L)`，其中 L 是把 `份数 [2]：` 那一行换成 `份数 [2]：two`、`SERVINGS_WRONG_ZH` 和 `份数 [2]：` 的 `BASE_OUT_ZH(F)`。这个文件是 `BASE_FILE`。3. 每一行给出退出码 0，最后一行是 `SAVED`，各文件依次有 `servings = 1`、`servings = 100`、`servings = 100` 和 `servings = 7`。 |
| F15-T13 | 功能 | `recipe-menu add`、`main` | 标签。`add` 在 `,`、`，` 和 `、` 处切分回答，每一部分去掉两端空白，跳过空的部分，并用标签的任一个名称找到每一部分，大小写只对 A 到 Z 有意义。文件里每个标签只出现一次，按第一次输入的样子，按回答的顺序，或者是 `tags = []`。第一个找不到标签的部分让整个回答出错：按目录标签个数选择形式的 `UNKNOWN_TAG`，或者 `NO_TAGS`，然后再问问题 5（选择 8，A 点）。 | 除非另有说明，每一行在一个新示例 F 里。1. 在 F 里，用 BASE(`t-1`)，其中标签：`快手, 素`，运行 `add`，以及 BASE(`t-2`)，其中标签：`快手，素`，和 BASE(`t-3`)，其中标签：`快手、素`。2. 用 BASE，其中标签：`" quick ,vegetarian, "`，运行 `add`。3. 用 BASE，其中标签：`QUICK, 快手, quick, Vegetarian`，运行 `add`。4. 在 F 里，用 BASE(`t-4`)，其中标签：`""`，以及 BASE(`t-5`)，其中标签：`" , ，、"`，运行 `add`。5. 用 BASE，其中标签：`breakfast`、`quick, breakfast, lunch`、`快手; 素`、`home style` 和 `quick`，运行 `add`。6. 用 BASE，其中标签：`breakfast`、`素`，运行 `add --lang zh`。7. 只有一个标签：用 BASE，其中标签：`素`、`quick`，运行 `add`，并在一份副本里用同样的回答运行 `add --lang zh`。8. 没有标签：用 BASE，其中标签：`quick`、`""`，运行 `add`，并在一份副本里用同样的回答运行 `add --lang zh`。 | 每一行给出退出码 0，err 为空，最后一行是 `SAVED`。它的 out 是 `BASE_OUT(F)`（带 `--lang zh` 时是 `BASE_OUT_ZH(F)`），其中 `Tags, separated by commas: quick` 或 `标签，用逗号分隔：quick` 那一行换成问题 5 的每个回答那一行，每个错误回答后面跟着它的消息。每个文件都是带这里给出的 `tags` 那一行的 `BASE_FILE`。1. 每个文件都有 `tags = ["快手", "素"]`。2. `tags = ["quick", "vegetarian"]`。3. `tags = ["QUICK", "Vegetarian"]`。4. 两个文件都有 `tags = []`。5. 消息 `TAGS(breakfast)`、`TAGS(breakfast)`、`TAGS(快手; 素)` 和 `TAGS(home style)`，以及 `tags = ["quick"]`。6. `TAGS_ZH(breakfast)`，以及 `tags = ["素"]`。7. `ONE_TAG(素)` 和 `ONE_TAG_ZH(素)`，以及 `tags = ["quick"]`。8. `NO_TAGS(quick)` 和 `NO_TAGS_ZH(quick)`，以及 `tags = []`。 |
| F15-T14 | 功能 | `recipe-menu add`、`main` | 一行食材。数量是行末的 `适量`，或 A 到 Z 任意大小写的“to taste”；否则它从最后一个以 ASCII 数字开头的词一直到行末，名称是它前面的文字。空白（包括 U+3000）分隔词，名称里面的空白照原样算。没有数量或没有名称的行得到 `NAME_AND_QUANTITY`，未知的名称得到 `UNKNOWN_INGREDIENT`，错误的数量得到它的 `WrongQuantity` 的消息，按这个检查顺序，每条都在两个空格之后，然后 `add` 询问下一行。正确的行按输入的名称和数量保留，同一种食材可以出现两次，列表可以为空（选择 9，A 点）。 | 每一行在一个新示例 F 里。1. 用 BASE，其中食材：`西兰花 300 g`、`Cooking oil 2 tbsp`、`Salt to taste`、`盐 适量`、`Egg 3`、`西兰花 300g`、`Salt TO taste`、`broccoli 1 kg`、`"大蒜\u30004 瓣"`、`Egg 2` 和 `Scallion 1 stalk`，运行 `add`。2. 用 BASE，其中食材：`Peanut`、`300 g`、`盐适量`、`西兰花300g`、`to taste`、`适量`、`Peanut 30 g`、`7-Up 1 can`、`"Choy  sum 1 斤"`、`Peanut 1 cups`、`Rice 1 cups`、`Rice 300`、`Rice 0 g`、`Rice 1234567890123456 g` 和 `番茄 300 g`，运行 `add`。3. 用 BASE，其中食材：`盐适量`、`Peanut 30 g`、`Rice 1 cups`、`Rice 300`、`Rice 0 g`、`Rice 1234567890123456 g` 和 `番茄 300 g`，运行 `add --lang zh`。4. 用 BASE，没有食材，运行 `add`。 | 1. `(0, out L)`，其中 L 是把 `  番茄 300 g` 换成这 11 个回答那几行的 `BASE_OUT(F)`。这个文件是把唯一的食材那一行换成下面 11 行的 `BASE_FILE`，每行在两个空格之后，后面跟着 `,`：`{ item = "西兰花", amount = "300 g" }`、`{ item = "Cooking oil", amount = "2 tbsp" }`、`{ item = "Salt", amount = "to taste" }`、`{ item = "盐", amount = "适量" }`、`{ item = "Egg", amount = "3" }`、`{ item = "西兰花", amount = "300g" }`、`{ item = "Salt", amount = "TO taste" }`、`{ item = "broccoli", amount = "1 kg" }`、`{ item = "大蒜", amount = "4 瓣" }`、`{ item = "Egg", amount = "2" }` 和 `{ item = "Scallion", amount = "1 stalk" }`。2. `(0, out L)`，其中 L 有每个回答那一行，每个错误回答后面跟着两个空格和它的消息：前六个各是 `NAME_AND_QUANTITY`，然后是 `UNKNOWN_INGREDIENT(name="Peanut")`、`UNKNOWN_INGREDIENT(name="7-Up")`、`UNKNOWN_INGREDIENT(name="Choy  sum")`、`UNKNOWN_INGREDIENT(name="Peanut")`、`AMOUNT_UNKNOWN_UNIT(unit="cups", amount="1 cups")`、`AMOUNT_NO_UNIT(amount="300", ingredient=Rice)`、`AMOUNT_ZERO(amount="0 g")` 和 `AMOUNT_NOT_A_NUMBER(amount="1234567890123456 g")`。这个文件是 `BASE_FILE`。3. 同样各行的中文消息：`NAME_AND_QUANTITY_ZH`、`UNKNOWN_INGREDIENT_ZH(name="Peanut")`、`AMOUNT_UNKNOWN_UNIT_ZH(unit="cups", amount="1 cups")`、`AMOUNT_NO_UNIT_ZH(amount="300", ingredient=大米)`（虽然那一行写的是 `Rice`，它用中文名写出这种食材）、`AMOUNT_ZERO_ZH(amount="0 g")` 和 `AMOUNT_NOT_A_NUMBER_ZH(amount="1234567890123456 g")`。4. `(0, out L)`，其中 L 是去掉 `  番茄 300 g` 那一行的 `BASE_OUT(F)`，这个文件是把从 `ingredients = [` 到 `]` 的三行换成一行 `ingredients = []` 的 `BASE_FILE`。 |
| F15-T15 | 功能 | `recipe-menu add`、`main` | 步骤（B 点）。有中文步骤时，英文步骤的提问是 `EN_STEPS_OPTIONAL_PROMPT`，英文步骤可以留空。没有中文步骤时，提问是 `EN_STEPS_PROMPT`。两个列表都为空时，`add` 写出 `STEPS_NEEDED`，并用 `EN_STEPS_PROMPT` 再问问题 8。只有空白的一行结束列表。文件按输入的顺序保留步骤，省去没有步骤的语言，保存后的检查对它给出警告（选择 3、6、10 和 12）。 | 每一行在一个新示例 F 里。1. 用 BASE，没有中文步骤，运行 `add`。2. 用 BASE，没有英文步骤，运行 `add`。3. 用 BASE 的回答 1 到 7，然后是 `""`、`""`、`""`、`Cut the tomatoes.` 和 `""`，运行 `add`。4. 第 3 行带 `--lang zh`。5. 用 BASE 的回答 1 到 7，然后是 `第一步。`、`第二步。`、`"\u3000 "`、`Step one.` 和 `"\t"`，运行 `add`。 | 1. `(0, out L1)`，其中 L1 是去掉 `  番茄切块。` 那一行、把 `EN_STEPS_OPTIONAL_PROMPT` 换成 `EN_STEPS_PROMPT`、并把最后一行换成 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 0, 1)` 和 `BLOCK(recipes/new-dish.toml at steps with NO_ZH_STEPS)` 的 `BASE_OUT(F)`。这个文件是去掉从 `zh = [` 到 `]` 三行的 `BASE_FILE`。2. `(0, out L2)`，其中 L2 是去掉 `  Cut the tomatoes.` 那一行、并把最后一行换成 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 0, 1)` 和 `BLOCK(recipes/new-dish.toml at steps with NO_EN_STEPS)` 的 `BASE_OUT(F)`。这个文件是去掉从 `en = [` 到 `]` 三行的 `BASE_FILE`。3. `(0, out L)`，其中 L 是 `BASE_OUT(F)` 的前 8 行，然后是 `ZH_STEPS_PROMPT`、`  `、`EN_STEPS_PROMPT`、`  `、`STEPS_NEEDED`、`EN_STEPS_PROMPT`、`  `、`STEPS_NEEDED`、`EN_STEPS_PROMPT`、`  Cut the tomatoes.`、`  `，以及 L1 的最后三行。这个文件和第 1 行相同。4. 第 3 行的中文各行，带 `EN_STEPS_PROMPT_ZH`、`STEPS_NEEDED_ZH`、`SAVED_WITH_PROBLEMS_ZH(F/recipes/new-dish.toml, 0, 1)`、`  recipes/new-dish.toml，步骤` 和 `    没有中文步骤。命令会改为显示英文步骤。`。5. `(0, out L)`，其中 L 是 `BASE_OUT(F)` 的前 9 行，然后是 `  第一步。`、`  第二步。`、`  \u3000 `、`EN_STEPS_OPTIONAL_PROMPT`、`  Step one.`、`  \t` 和 `SAVED(file=F/recipes/new-dish.toml)`。这个文件是中文步骤为 `第一步。` 和 `第二步。`、英文步骤为 `Step one.` 的 `BASE_FILE`。 |
| F15-T16 | 功能 | `recipe-menu add`、`read_recipe`、`main` | 文件的文字。每段文字是去掉两端空白的回答，写在 TOML 基本字符串里：`\` 变成 `\\`，`"` 变成 `\"`，从 U+0000 到 U+001F 的每个控制字符和 U+007F 变成 `\u` 加四位十六进制数字，其他每个字符都保持原样，包括 U+3000、U+2028 和基本多文种平面之外的字符。文件是不带字节顺序标记的 UTF-8，换行符为 LF，最后一行也是，`read_recipe` 读回来的正好是这些回答（选择 10）。 | 每一行在一个新示例 F 里。1. 用 `ESCAPES` 运行 `add`。2. 然后 `read_recipe(F, catalog, "odd-text")`，其中 `catalog` 是 `read_catalog(F)` 给出的目录。3. 用 BASE(`ctrl-text`)，其中中文名：`"中\x1b文"`，英文名：`"E\x7fN"`，运行 `add`，然后用同样的方式对 `ctrl-text` 调用 `read_recipe`。4. 用 BASE，其中英文步骤：`"Rice bowl \U0001F35A"`，运行 `add`。 | 1. 退出码 0，err 为空，out 的最后一行是 `SAVED(file=F/recipes/odd-text.toml)`。out 的第二行和第三行是 `ZH_NAME_PROMPT` 和 `EN_NAME_PROMPT`，各自后面跟着照原样输入的回答。这个文件是 `TEXT_G`，不含 `b"\r"`，也不以 `b"\xef\xbb\xbf"` 开头。2. 没有问题，得到一个菜谱，它的中文名和英文名是回答 2 和 3，它的步骤中文是回答 8 和 9，英文是回答 11。3. out 的最后一行是 `SAVED(file=F/recipes/ctrl-text.toml)`。文件的第一行是 `name = { zh = "中\u001b文", en = "E\u007fN" }`，其中字母 `b` 和 `f` 大小写都可以。`read_recipe` 没有给出问题，名称为 `"中\x1b文"` 和 `"E\x7fN"`。4. 这个文件是把 `  "Cut the tomatoes.",` 换成 `  "Rice bowl 🍚",` 一行的 `BASE_FILE`，用 UTF-8。 |
| F15-T17 | 功能 | `ADD_COMMAND.run`、`recipe-menu add`、`main` | `add` 怎样读取回答。它写出每个提问，刷新输出流，然后读一行。输入不是终端时，它在提问后面写出读到的那一行和一个换行；`isatty()` 给出真时，两样都不写。问题 1 处的输入结束以 0 结束 `add`。在后面的任何问题处，它向错误流写出 `INPUT_ENDED`，给出 1，不写文件；输入不是终端时，在这之前先写一个换行（选择 4，2.2 输出的表格）。 | 每一行在一个新示例 F 里。1. 对 1 到 10 的每个 k：用 BASE 的前 k 个回答运行 `add`。2. 用 BASE 的前 4 个回答运行 `add --lang zh`。3. 用 BASE 的终端流运行 `add`。4. 用 `tomato-egg` 和 `""` 的终端流运行 `add`。5. 用 BASE 前 2 个回答的终端流运行 `add`。6. 用没有回答的终端流运行 `add`。7. `ADD_COMMAND.run(Context(Lang.EN, F, Settings(), out, err, date(2026, 11, 10), input=I), Arguments())`，其中 out 和 I 是 BASE 的一个刷新记录的两个流，err 是一个新的流。 | 1. `(1, out L, err [INPUT_ENDED])`，其中 L 是 `BASE_OUT(F)` 直到回答 k + 1 那一行的各行，那一行只有它的提问，在列表里是两个空格。所以 k = 1 以 `Chinese name: ` 结束，k = 5 以 `Ingredients, one per line, as "name quantity". An empty line ends the list:` 和 `  ` 结束，k = 10 以 `  Cut the tomatoes.` 和 `  ` 结束。没有一行写文件，`recipes/` 的列表保持为示例的列表。2. `(1, out L, err [INPUT_ENDED_ZH])`，其中 L 是 `BASE_OUT_ZH(F)` 的前 4 行和 `标签，用逗号分隔：`。3. 退出码 0，err 为空，out 是文字 `ID_PROMPT + ZH_NAME_PROMPT + EN_NAME_PROMPT + SERVINGS_PROMPT(servings=2) + TAGS_PROMPT + INGREDIENTS_PROMPT + "\n" + "    " + ZH_STEPS_PROMPT + "\n" + "    " + EN_STEPS_OPTIONAL_PROMPT + "\n" + "    " + SAVED(file=F/recipes/new-dish.toml) + "\n"`。这个文件是 `BASE_FILE`。4. `(0, ID_PROMPT + ID_EXISTS(id="tomato-egg") + "\n" + ID_PROMPT, "")`。5. `(1, ID_PROMPT + ZH_NAME_PROMPT + EN_NAME_PROMPT, INPUT_ENDED + "\n")`。6. `(0, ID_PROMPT, "")`。7. 0，这个文件是 `BASE_FILE`。在 11 次读取的每一次，输出流的文字都等于它最后一次刷新时的文字，并以这次读取给出的回答的提问结尾：问题 1 到 5 的提问，以及列表每一行的两个空格。 |
| F15-T18 | 功能 | `ADD_COMMAND.run`、`recipe-menu add`、`main` | Ctrl+C。读取回答时的 `KeyboardInterrupt` 经过 `run` 传到 `cli`，`cli` 给出 130，不再写任何东西，也不写文件，因为 `add` 只在最后一个回答之后才写。写文件时按下 Ctrl+C 不留下文件（选择 4 和 11）。 | 每一行在一个新示例 F 里。1. 对 1、2、6、8 和 11 中的每个 k：用在回答 k 处停下的 BASE 的停止流运行 `add`。2. 用 `Lang.EN`、F 和新的流构成的 `Context` 调用 `ADD_COMMAND.run`，它的输入是在回答 3 处停下的 BASE 的停止流。3. 在 `shop_faults(F.root, write recipes/new-dish.toml: CTRL_C)` 之内用 BASE 运行 `add`。4. 在 `shop_faults(F.root, close recipes/new-dish.toml: CTRL_C)` 之内用 BASE 运行 `add`。 | 1. 退出码 130，err 为空，out 是 `BASE_OUT(F)` 直到回答 k 那一行的文字，那一行只有它的提问，后面没有换行。所以 k = 1 时 out 是 `ID_PROMPT`，k = 2 时是 `ID_PROMPT + "new-dish\n" + ZH_NAME_PROMPT`。没有一行写文件，`recipes/` 的列表保持为示例的列表。2. `run` 抛出 `KeyboardInterrupt`。3 和 4. `(130, out L, "")`，其中 L 是去掉最后一行的 `BASE_OUT(F)`。记录里有 `unlink recipes/new-dish.toml`，`recipes/` 的列表是示例的列表。 |
| F15-T19 | 功能 | `recipe-menu add`、`recipe-menu check`、`main` | 2.2 的第 1 步和第 2 步。目录的第一个错误，然后是 `recipes/` 列举的第一个错误，让 `add` 停下：`stop_at_error` 的三行，退出码 1，输出流上什么也没有，也不读任何回答。名称不是菜谱 ID 的条目会让它停下，和某个 ID 只有大小写不同的名称也一样，比如 `Garlic-Broccoli.toml` 或 `garlic-broccoli.TOML`。`check` 读取同样的文件，所以这个错误在 `check` 的错误之中（选择 2）。 | 每一行在一个新示例里用受监视的流运行 `add`。1. 没有目录。2. 目录花括号。3. 没有菜谱文件夹。4. 菜谱是文件。5. Rice Bowl。6. 大写的 rice。7. 条目 `recipes/Garlic-Broccoli.toml`。8. 条目 `recipes/garlic-broccoli.TOML`。9. 没有目录，也没有菜谱文件夹。10. 目录花括号和 Rice Bowl。11. 第 2 行和第 7 行带 `--lang zh`。 | 1. `(1, err STOP(catalog.toml, FILE_MISSING))`。2. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`。3. `(1, err STOP(recipes, FOLDER_MISSING))`。4. `(1, err STOP(recipes, FOLDER_IS_FILE))`。5. `(1, err STOP(recipes/Rice Bowl.toml, NOT_A_RECIPE_ID of a listing))`。6. `(1, err STOP(recipes/rice.TOML, TOML_ENDING_NOT_SMALL))`。7. `(1, err STOP(recipes/Garlic-Broccoli.toml, NOT_A_RECIPE_ID of a listing))`。8. `(1, err STOP(recipes/garlic-broccoli.TOML, TOML_ENDING_NOT_SMALL))`。9. 第 1 行的结果。10. 第 2 行的结果。11. 第 2 行和第 7 行的 `STOP_ZH` 结果。每一行里，受监视的流都没有记下读取，没有添加条目，这个错误在同一文件夹里 `check` 的错误之中。 |
| F15-T20 | 功能 | `recipe-menu add`、`main` | `add` 读写什么。在第一个问题之前，它读取 `catalog.toml` 并列举 `recipes/`，各一次。在最后一个回答之后，它以 `x` 模式打开一次来创建新文件，然后读取 `catalog.toml` 和新文件各一次。它不读别的菜谱、不读菜单，也不读常备清单，所以它们里面的错误不会改变什么，它也不留下别的条目（选择 2 和 11，2.2 的副作用）。 | 每一行在一个新示例 F 里、在 `shop_faults(F.root)` 之内。1. 用 BASE 运行 `add`。2. 带麻婆错误、菜单拼写错误和常备清单错误：用 BASE 运行 `add`。3. 没有菜单文件夹：用 BASE 运行 `add`。4. 用 `tomato-egg` 和 `""` 运行 `add`。 | 1. `(0, out BASE_OUT(F))`。记录为 `read settings.toml`、`read catalog.toml`、`open recipes/new-dish.toml`、`read catalog.toml` 和 `read recipes/new-dish.toml`，列举记录为 `recipes` 和 `recipes`。`recipes/` 的列表是示例的列表和 `new-dish.toml`。2 和 3. 第 1 行的结果和记录。4. `(0, out [ID_PROMPT + "tomato-egg", ID_EXISTS(id="tomato-egg"), ID_PROMPT])`，记录为 `read settings.toml` 和 `read catalog.toml`，列举记录只有一个 `recipes`。 |
| F15-T21 | 功能 | `recipe-menu add`、`main` | 在第 2 步列举 `recipes/` 之后出现了与这个文件同名的条目。`create_file` 拒绝它，名称只有大小写不同或它是文件夹时也一样。`add` 向错误流写出带这个条目完整路径的 `APPEARED`，给出 1。输出流里有整个会话，没有保存后的那几行，这个条目保持它的字节（选择 11，F11 设计 3.3）。 | 每一行在一个新示例 F 里。1. 在 `shop_faults(F.root, open recipes/new-dish.toml: race)` 之内用 BASE 运行 `add`。2. 第 1 行带 `--lang zh`。3. 用在最后一个回答处写出条目 `recipes/New-Dish.toml` 的 BASE 的钩子流运行 `add`。4. 同样，修改改为创建空文件夹 `recipes/new-dish.toml`。5. 同样，修改改为写出条目 `recipes/new-dish.TOML`。 | 1. `(1, out L, err [APPEARED(file=F/recipes/new-dish.toml)])`，其中 L 是去掉最后一行的 `BASE_OUT(F)`，这个文件里是 `b"mine\n"`。2. `(1, out L′, err [APPEARED_ZH(file=F/recipes/new-dish.toml)])`，其中 L′ 是去掉最后一行的 `BASE_OUT_ZH(F)`。3. `(1, out L, err [APPEARED(file=F/recipes/New-Dish.toml)])`。`recipes/` 的列表是示例的列表和 `New-Dish.toml`，没有名称正好是 `new-dish.toml` 的条目，`New-Dish.toml` 里是 `b"mine\n"`。4. `(1, out L, err [APPEARED(file=F/recipes/new-dish.toml)])`，这个文件夹仍然是空的。5. `(1, out L, err [APPEARED(file=F/recipes/new-dish.TOML)])`，`recipes/` 的列表是示例的列表和 `new-dish.TOML`。 |
| F15-T22 | 功能 | `recipe-menu add`、`main` | 保存失败。`create_file` 给出 `FAILED`，`add` 向错误流写出三行并给出 1：相对于数据文件夹的文件（文件夹无法列举时是 `recipes`），然后是两个空格和用输出语言写的问题文字，然后是 `NOTHING_SAVED`；`create_file` 无法删除文件时，第三行是带文件完整路径的 `LEFT_BEHIND`。输出流里有整个会话，没有保存后的那几行（选择 11，F11 设计 3.3）。 | 每一行在一个新示例 F 里、在带所列规则的 `shop_faults(F.root, ...)` 之内用 BASE 运行 `add`。1. `open recipes/new-dish.toml: DENIED`。2. `write recipes/new-dish.toml: IO`。3. 带 `write recipes/new-dish.toml: NO_SPACE` 运行 `add --lang zh`。4. `close recipes/new-dish.toml: IO`。5. `write recipes/new-dish.toml: IO` 和 `unlink recipes/new-dish.toml: DENIED`。6. 第 5 行带 `--lang zh`。7. 没有规则，用在最后一个回答处删除 `recipes/` 及其中一切的 BASE 的钩子流。 | 每一行的退出码都是 1，out 是去掉最后一行的 `BASE_OUT(F)`，带 `--lang zh` 时是去掉最后一行的 `BASE_OUT_ZH(F)`。1. err 为 `recipes/new-dish.toml`、`  ` 后跟 `FILE_WRITE_DENIED`，以及 `NOTHING_SAVED`，没有文件。2. err 为 `recipes/new-dish.toml`、`  ` 后跟 `FILE_WRITE_ERROR(reason="Input/output error")`，以及 `NOTHING_SAVED`。没有留下文件，记录里有 `unlink recipes/new-dish.toml`。3. 中文各行：`recipes/new-dish.toml`、`  ` 后跟中文的 `FILE_WRITE_ERROR(reason="No space left on device")`，以及 `NOTHING_SAVED_ZH`。4. 第 2 行的各行和记录。5. err 为 `recipes/new-dish.toml`、`  ` 后跟 `FILE_WRITE_ERROR(reason="Input/output error")`，以及 `LEFT_BEHIND(file=F/recipes/new-dish.toml)`。这个文件里是 `BASE_FILE` 文字前一半 `text[: len(text) // 2]` 的 UTF-8 字节。6. 第 5 行的中文各行，带 `LEFT_BEHIND_ZH(file=F/recipes/new-dish.toml)`。7. err 为 `recipes`、`  ` 后跟 `FOLDER_MISSING`，以及 `NOTHING_SAVED`，`recipes/` 不存在。 |
| F15-T23 | 功能 | `recipe-menu add`、`main` | 保存后的检查。没有问题时，`add` 写出 `SAVED`，给出 0。有问题时，它写出带数目的 `SAVED_WITH_PROBLEMS`，先是错误的 `problem_block`，再是警告的，有错误时再写 `FIX_AND_CHECK`，全部写到输出流；有错误时给出 1，只有警告时给出 0。每个数目为 1 时用单数形式，其他时候用复数形式，为 0 的数目省去，中文文字对每个数目都相同。只有目录或文件在第 1 步之后变了才会有错误，文件保持已保存（选择 12，A 点）。 | 每一行在一个新示例 F 里。1. 用 BASE，其中中文名：`""`，且没有英文步骤，运行 `add`。2. 用在最后一个回答处做“没有番茄”修改的 BASE 的钩子流运行 `add`。3. 同样，用 BASE，其中食材：`番茄 300 g`、`番茄 1 kg`。4. 和第 2 行相同，用 BASE，其中中文名：`""`。5. 用在最后一个回答处做“没有番茄”修改的钩子流运行 `add --lang zh`，回答是 BASE，其中中文名：`""`，食材：`番茄 300 g`、`番茄 1 kg`，且没有英文步骤。6. 用在最后一个回答处做目录花括号修改的 BASE 的钩子流运行 `add`。7. 在 `shop_faults(F.root, read recipes/new-dish.toml: DENIED)` 之内用 BASE 运行 `add`。8. 在 `shop_faults(F.root, read catalog.toml: later DENIED)` 之内用 BASE 运行 `add`。 | 每一行里 err 都为空，这个文件是它的回答给出的文件。1. `(0, out L)`，其中 L 是带 `Chinese name: `、去掉 `  Cut the tomatoes.` 那一行、并把最后一行换成 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 0, 2)` 和 `BLOCK(recipes/new-dish.toml at name with NO_ZH_NAME, recipes/new-dish.toml at steps with NO_EN_STEPS)` 的 `BASE_OUT(F)`。2. `(1, out L)`，其中 L 是把最后一行换成 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 1, 0)`、`BLOCK(recipes/new-dish.toml at ingredient 1 with UNKNOWN_INGREDIENT(name="番茄") of a recipe)` 和 `FIX_AND_CHECK` 的 `BASE_OUT(F)`。这个文件是 `BASE_FILE`。3. 退出码 1，最后几行是 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 2, 0)`、`ingredient 1` 和 `ingredient 2` 处同一个错误的块，以及 `FIX_AND_CHECK`。4. 退出码 1，最后几行是 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 1, 1)`、第 2 行那个错误的块、`name` 处 `NO_ZH_NAME` 警告的块，以及 `FIX_AND_CHECK`。5. 退出码 1，最后几行是 `已保存 F/recipes/new-dish.toml。检查发现了 2 个错误和 2 个警告：`、第 3 行两个错误的中文块、`name` 和 `steps` 处警告的中文块，以及 `FIX_AND_CHECK_ZH`。6. 退出码 1，最后几行是 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 1, 0)`、`BLOCK(catalog.toml at line 11 with MISSING_BRACE)` 和 `FIX_AND_CHECK`。7. 退出码 1，最后几行是 `SAVED_WITH_PROBLEMS(F/recipes/new-dish.toml, 1, 0)`、`BLOCK(recipes/new-dish.toml with no place and ACCESS_DENIED)` 和 `FIX_AND_CHECK`。8. 和第 7 行相同，块换成 `BLOCK(catalog.toml with no place and ACCESS_DENIED)`。 |
| F15-T24 | 功能 | `recipe-menu add`、`main` | `cli` 在运行 `add` 之前用 F05 的消息和退出码报告命令行上的错误、缺少的数据文件夹和有错的设置，`add` 不读任何回答。`--help` 显示帮助。没有 `--lang` 时，设置里的语言决定 `add` 的语言。没有 `--data` 时，`add` 使用 `cli` 选定的数据文件夹。之后同样的文件夹给出 `add` 的输出（2.2 的错误，选择 1，F05 设计 2.10）。 | 除非给出回答，每一行都用受监视的流。1. 在 `example` 里：`add garlic-broccoli`、`add garlic-broccoli --lang zh`、`add --tag quick`、`add --tag quick --lang zh`、`add --lang fr` 和 `add --lang`。2. 在 `example` 里：`add --help` 和 `add garlic-broccoli --help --lang zh`。3. M 是 `tmp_path / "missing"`：在 M 里运行 `add`，以及在 M 里运行 `add --lang zh`。4. 在设置有错的新示例里：`add`。5. 在带中文设置的新示例 G 里：用 BASE 运行 `add`，然后用 BASE(`new-dish-2`) 运行 `add --lang en`。6. 在 `home / "recipe-menu"` 处的新示例里：不指定文件夹，用 BASE 运行 `add`。7. 在 `example` 里，在第 1 和 2 行之后：用 BASE 运行 `add`。 | 1. `(2, err ['Unexpected argument "garlic-broccoli". Write "recipe-menu add".', RUN_HELP_COMMANDS])`、`(2, err ["多余的参数“garlic-broccoli”。请写成“recipe-menu add”。", RUN_HELP_COMMANDS_ZH])`、`(2, err ['"add" has no option "--tag". It has no options of its own.', RUN_HELP_OPTIONS])` 和 `(2, err ["“add”没有选项“--tag”。它没有自己的选项。", RUN_HELP_OPTIONS_ZH])`。`add --lang fr` 和 `add --lang` 给出把 `add` 换成 `list` 的同一行的结果。2. 退出码 0，err 为空，out 是不指定文件夹时 `--help` 或 `--help --lang zh` 的 out。3. `tests/f05_texts.py` 的 `no_data_folder(M)` 和 `no_data_folder(M, ZH)`，out 为空，M 仍然不存在。4. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`。5. `(0, out BASE_OUT_ZH(G))`，然后是把 `new-dish` 换成 `new-dish-2` 的 `(0, out BASE_OUT(G))`。6. `(0, out BASE_OUT(home/recipe-menu))`。7. `(0, out BASE_OUT(example))`。在第 1 到 4 行里，受监视的流没有记下读取，也没有添加条目。 |
| F15-T25 | 集成 | `recipe-menu add`、`recipe-menu show`、`main` | `main` 上的 v0.2-S10。5 个错误回答各得到它的那一条消息，`add` 再问同一个问题或询问下一行食材，`Cooking oil 2 tbsp` 和 `Salt to taste` 分成各自的名称和数量，这个菜谱能通过 `show` 读回来（选择 3、7、8、9 和 10，A 点）。 | 1. 在 `example` 里用 S10 运行 `add`。2. 然后在 `example` 里运行 `show egg-fried-rice`。3. 在一个用 `put_bytes` 把 `S10_FILE` 写成 `recipes/egg-fried-rice.toml` 的新示例 G 里运行 `show egg-fried-rice`。 | 1. `(0, out S10_OUT(example))`，这个文件是 `S10_FILE`。2. 第 3 行的结果，它的退出码为 0，以 `Egg fried rice  蛋炒饭` 和 `Servings: 3   Tags: quick, staple` 两行开头。 |
| F15-T26 | 集成 | `recipe-menu add`、`main` | `main` 上的 v0.2-S15 第 2 步。`add` 只直接创建新的菜谱文件，不用临时文件。新的条目可能让文件夹 `recipes/` 得到新的修改时间，`home` 和当前文件夹下的其他每个文件和文件夹都保持它们的字节和时间（2.2 的副作用，选择 11）。 | `home / "recipe-menu"` 处的一个新示例，带空的 `shopping/`，以及用 `monkeypatch.chdir` 进入的空的当前文件夹 `tmp_path / "cwd"`。在这一行之前和之后对 `home` 和当前文件夹做 `tests/f07_support.py` 的 `snapshot`。这一行是不指定文件夹、用 S09 运行 `add --lang zh`。 | `(0, out S09_OUT(home/recipe-menu))`。这一行之后 `home` 的快照比之前多一个条目 `recipe-menu/recipes/garlic-broccoli.toml`，里面是 `S09_FILE`。其他每个条目都保持它的字节和时间，只是 `recipe-menu/recipes` 可以有新的时间。当前文件夹的快照不变。 |
| F15-T27 | 集成 | `python -m recipe_menu` | 真正的入口在管道上带着回答运行 `add`。`cli` 对 stdin 调用 `use_utf8_input`，所以 `add` 读取 UTF-8，有没有字节顺序标记、用 CR LF 还是 LF 都一样，把不是 UTF-8 的字节变成 U+FFFD，并且不依赖 `PYTHONIOENCODING`。它把输出以 UTF-8 写到 stdout，把 `INPUT_ENDED` 或用法错误写到 stderr（3.2，3.3，选择 4）。 | `tests/f15_support.py` 的 `pipe_module`，它把 `PYTHONIOENCODING` 设为 `ascii`。每一行在它自己的新示例 F 里运行。1. `add --lang zh --data <F>`，字节为 `b"\xef\xbb\xbf"`，然后是 UTF-8 的 S09 的回答，每个后面跟着 `b"\r\n"`。2. `add --data <F>`，字节为 UTF-8 的 BASE 的回答，每个后面跟着 `b"\n"`，只是中文名是字节 `b"\xff"` 后跟 UTF-8 的 `新菜`。3. `add --data <F>`，字节为 BASE 的前 2 个回答，每个后面跟着 `b"\n"`。4. `add --data <F>`，没有字节。5. `add garlic-broccoli --data <F>`，没有字节。 | 1. `(0, out S09_OUT(F))`，这个文件是 `S09_FILE`。2. `(0, out L)`，其中 L 是 `Chinese name: ` 那一行后跟 U+FFFD 和 `新菜` 的 `BASE_OUT(F)`，这个文件是第一行为 `name = { zh = "<U+FFFD>新菜", en = "New dish" }` 的 `BASE_FILE`，用 UTF-8。3. `(1, out [ID_PROMPT + "new-dish", ZH_NAME_PROMPT + "新菜", EN_NAME_PROMPT], err [INPUT_ENDED])`。4. `(0, out [ID_PROMPT])`。5. `(2, err ['Unexpected argument "garlic-broccoli". Write "recipe-menu add".', RUN_HELP_COMMANDS])`。 |
| F15-T28 | 集成 | `recipe-menu add`、`read_recipe`、`main` | 随机的回答，以及对任何回答都成立的性质。对 `add` 接受的任何名称、份数、标签、食材行和步骤，文件通过 `read_recipe` 读回来的正好是去掉两端空白的回答：名称、份数、目录找到的标签和食材、`parse_quantity` 给出的数量，以及按顺序的步骤。保存后的检查没有发现错误，每个警告都是回答里省去的一种语言（选择 6 到 12，B 点）。 | 一个新示例 F，对 0 到 199 的每个 n，用 `Random(n)` 构造的回答运行一行 `add`，ID 是 `random-` 加三位数的 n。名称和步骤列表各自可以在一种语言里为空，绝不在两种语言里都为空。一段文字是 1 到 12 个字符，取自 ASCII 字母和数字、汉字、`"`、`\`、`'`、`#`、`=`、`[`、`]`、`{`、`}`、`🍚`，以及只在文字内部出现的空格、制表符、U+0000、U+007F、U+00A0、U+2028 和 U+3000。它至少有一个不是空白的字符，两端有空格、制表符或 U+3000。份数是 1 到 100 的整数，最多带两个前导零，或者是空回答。标签是目录里最多三个标签，每个用任一种语言的名称、A 到 Z 随机大小写写出，用带空格的 `,`、`，` 或 `、` 连接。食材是 0 到 5 行，每行是目录里一种食材的任一种语言的名称（A 到 Z 随机大小写）、一个空格和一个数量：`适量`、`to taste` 或 `TO taste`；对有默认单位的食材，可以是 1 到 999 的整数；对没有默认单位的食材，可以是整数或 `1.5` 后跟 ` g`、`g`、` kg` 或 ` ml`。 | 对每个 n：退出码 0，err 为空。out 的最后一行是 `SAVED`，或者 out 以没有错误的 `SAVED_WITH_PROBLEMS` 和省去的语言的警告块结尾，按 name、steps 的顺序。`read_recipe(F, catalog, ID)` 给出一个菜谱，并且只有那些警告。它的名称和步骤等于去掉两端空白的回答。它的份数等于回答，空回答时为 2。它的标签是 `find_tag` 为各部分找到的标签，每个一次，按顺序。每一行食材是 `find_ingredient` 找到的食材和 `parse_quantity(quantity, ingredient.unit)` 给出的数量。文件是不带字节顺序标记、不含 `b"\r"` 的 UTF-8，以 `b"\n"` 结尾。 |
| F15-T29 | 集成 | `recipe-menu add`、`recipe-menu check`、`main` | `main` 上的 v0.2-S16 第 2 步，以及需求 7 的规模。有 1,000 个菜谱和 300 种食材时，`add` 在列举里找到一个已有的 ID，拆分名称里带数字的 `食材300 100 g` 和 `食材150 适量`，保存文件，并且没有发现问题。没有性能指标提到 `add`，所以这个用例不计时（第 3 节）。 | 用 `tests/pt01_support.py` 的 `make_pt01` 在 P（`tmp_path / "pt01"`）处做出的 PT01 数据文件夹。1. 用 `recipe-0001`，然后用 `PT01_ANSWERS` 运行 `add`。2. `check`。 | 1. `(0, out L)`，其中 L 是 `ID_PROMPT + "recipe-0001"`、`ID_EXISTS(id="recipe-0001")` 和 `PT01_OUT(P)`。文件 `recipes/size-check.toml` 是 `PT01_FILE`。2. 把 `1000 recipes` 换成 `1001 recipes` 的 `tests/pt01_support.py` 的 `(0, out PT01_LINES)`。 |

## 3. 性能用例

无。F15 的接口都没有性能指标。PT01 提到的是 `check`、`list`、`show`、`search`、`menu show` 和 `shop`，没有 `add`（需求 7.1，设计第 2 节）。所以 `add` 没有计时的用例（R14）。F15-T29 在 PT01 数据文件夹上运行它而不计时，和 v0.2-S16 一样；`add` 其余的时间是你打字的时间（选择 14）。

F15 还给每个命令的启动加了一点东西：`cli` 导入 `add` 的文件，并从实现 PR 起调用一次 `use_utf8_input(sys.stdin)`。选择 14 估计约 1 毫秒。架构师用 `python -X importtime` 测得模型的 4 个新文件自身约 3 毫秒，这次调用 14 微秒，`import recipe_menu.cli` 的启动时间没有超出噪声的差别（设计第 4 节，说明 1）。在 Troy 的电脑上，`check` 在 PT01 的 1 秒之内还剩 172 毫秒，F14 之后的中位数是 0.828 秒。F07、F09、F10、F11 和 F13 的 PT01 用例在每个 PR 里给它们命令的启动计时，v0.1-S27 到 v0.1-S32 也在 v0.2 的发布测试里再运行一次。所以启动变慢会在 PT01 提到的命令里显示出来，F15 不需要为此加自己的计时用例。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| `add` 要多长时间，以及 F15 给每个命令启动加的时间。 | 没有性能指标提到 `add`（R14）。选择 14 估计启动约 1 毫秒，架构师测得几毫秒（设计第 4 节，说明 1）。F07、F09、F10、F11 和 F13 的 PT01 用例在每个 PR 里给它们命令的启动计时（第 3 节）。F15-T29 在 PT01 数据文件夹上运行 `add` 而不计时。 |
| Windows 控制台：用输入法输入的中文回答、退格键、`chcp 437`、在提问处真正按下的 Ctrl+C，以及 Windows Terminal 里的中文输出。 | 没有 CI 机器有控制台（架构 10），v0.2-S18 让 Troy 手动检查这些。F15-T17 用一个 `isatty()` 给出真的流走终端的分支。F15-T18 在一次读取时抛出 `KeyboardInterrupt`，这正是 Python 的控制台读取在提问处按下 Ctrl+C 时抛出的（选择 4）。 |
| 从 Windows PowerShell 5.1 通过管道送来的中文回答，它们会变成 `?`。 | 选择 4 说需求里没有流程需要这样的管道，因为你在控制台里输入回答。F15-T27 通过管道送 UTF-8 字节。 |
| `ID_EXISTS` 提到的 `recipe-menu edit tomato-egg` 能打开这个菜谱。 | F16 加入 `edit`。在 F16 验收之前，这个命令给出 `Unknown command "edit".`（设计第 4 节）。F15-T09 只检查 `ID_EXISTS` 的文字。 |
| 用一个文件和它只有大小写不同的 ID 调用 `check_recipe`，比如 `recipes/` 里只有 `Rice.toml` 时用 `rice`。 | 设计 3.4 只要求 `is_recipe_id(recipe_id)` 为真。这时在 Windows 上 `read_recipe` 会打开 `Rice.toml`，在 Linux 上找不到文件，所以结果随系统而不同。架构师的说明 3 补充说，这个 ID 必须是 `list_recipe_ids` 给出的，或者是调用者刚用 `create_file` 创建的文件的 ID，而 `add` 总是这样调用 `check_recipe`。对 `add` 来说，`recipes/` 里有这样的文件时，它在第一个问题之前就停下（F15-T19）；`add` 等待时出现这样的文件，会给出 `APPEARED`（F15-T21）。F16 的测试方案覆盖 `edit` 的调用。 |
| 含有 UTF-8 无法编码的字符（比如单独的代理项）的回答。 | 设计 3.1 要求输入流只给出 UTF-8 能编码的文字。`use_utf8_input` 之后，标准输入把每个不是 UTF-8 的字节变成 U+FFFD（F15-T04 和 F15-T27）。 |
| 在保留换行符的流上以 CR LF 结尾的回答那一行，比如 `io.StringIO("new-dish\r\n")`。 | 选择 4 取去掉两端空白的回答，所以 CR 不算在回答里，但它没有说回答那一行是否显示 CR。`use_utf8_input` 之后，标准输入把 CR LF 变成 LF（3.3），F15-T27 通过管道送 CR LF。 |
| 调用者作为 `stdin` 传入的流，`main` 会不会改变它。 | 设计 3.2 说明了 `stdin` 为 `None` 时 `main` 做什么（F15-T03），对调用者传入的流什么也没说。 |
| 第一个问题之前 `read_catalog` 或 `list_recipe_ids` 的警告。 | 选择 2 说警告不改变什么，但这两个读取器都不给警告。目录的问题和列举的问题都是错误（F03 设计 2.8，F04 设计 2.5 和 3.1）。 |
| `\u007F` 这样的转义里字母的大小写。 | 选择 10 给出 `\u` 加四位十六进制数字，它唯一的例子 `\u0009` 里没有字母。F15-T16 对 U+001B 和 U+007F 接受两种大小写，并检查 `read_recipe` 能读回文字。 |
| `add` 遇不到的 `create_file` 的情况，比如数据文件夹之外的路径，或 UTF-8 无法编码的文字。 | `add` 用 `recipe_file`、从 `is_recipe_id` 接受的 ID 构造路径（选择 11）。F11 的测试方案测试 `create_file` 本身。 |
| `add` 等待时，真正的另一个程序创建这个文件或修改目录。 | 没有测试能让另一个程序卡准某一步。钩子流和规则 `open P: race` 在每个用例选定的回答或步骤处做修改（F15-T21 到 F15-T23）。 |
| 发布测试里的 v0.2-S09 到 v0.2-S11 和 v0.2-S14 到 v0.2-S16。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 添加（TE5）。F15-T08、F15-T09、F15-T24 到 F15-T26 和 F15-T29 在 `main` 上运行它们的步骤。v0.2-S18 由 Troy 运行。 |
| mock PR 之后真实运行里 F05 原型的两份帮助。 | 从 mock PR 起，真正的帮助有 `add` 那一行。产品经理在 F15 验收时把这一行加进 F05 原型的两个帮助代码块（设计第 3 节）。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的中文字符。 |
| F16 的计划：帮助里 `add` 之后的 `edit ID`，以及它对 `check_recipe` 和 `problem_block` 的使用。 | F16 的设计和测试方案会覆盖它们。 |

## 5. 与接口设计师的对齐记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-20 | 初稿。 |
| 1.0 | 2026-11-20 | Troy 批准。 |
