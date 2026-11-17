---
troy-doc: "F14-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-17"
status: "Troy 已于 2026-11-17 批准"
mirror-of: "test-plan.md"
---

# F14 推荐一周菜单：测试方案

## 1. 功能

- 编号和名称：F14 推荐一周菜单
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.suggest` 的 `MENU_SUGGEST_COMMAND`、`recipe_menu.settings` 的 `Settings` 和 `read_settings`、`recipe_menu.app` 的 `Context`、`recipe_menu.datafile` 的 `read_file_text` 和 `parse_toml`、`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的值调用 `MENU_SUGGEST_COMMAND.run`、`Settings`、`read_settings`、`Context`、`read_file_text` 或 `parse_toml`。功能用例像你输入 `recipe-menu menu suggest` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 在 `MENU_SHOW_COMMAND` 之后有 `MENU_SUGGEST_COMMAND`（设计选择 1）。它把一个生成器作为 `random` 传入，设计 3.4 允许测试这样做。集成用例在 `main` 上运行 v0.2 场景，启动 `python -m recipe_menu`，构造随机的星期，或者在 PT01 数据文件夹上运行。没有用例是性能用例（第 3 节）。每个用例在括号里注明它来自设计的哪一部分，比如（选择 7）。设计的八个示例和其中九行 `# raises` 分别在 F14-T01（2.1）、F14-T03（2.2）、F14-T22（3.1）、F14-T23（3.2）、F14-T25（3.3 和 3.4）、F14-T26（3.5）和 F14-T27（3.6）里。

**A 点到 D 点。** Troy 于 2026-11-17 批准了设计 1.0，每一点都按建议：按 2.2 和 3.2 的写法接受 19 段新文字（A）；一个键 `dishes`，它是一张表，给每顿需要的餐写一个 1 到 10 的数（B）；一顿餐需要的菜比剩下的多时保持空着，后面需要的菜不多于剩下的餐仍然得到它们的菜（C）；换菜那一行和保存失败的第一行用相对于数据文件夹的路径写出菜单文件，比如 `menus\2026-W48.toml`（D）。架构 6 在 mock PR 之前的一个 `[docs]` PR 里记录 D 点。用例按设计的文字写。用例用两种语言检查 A 点的每一段新文字：

- F14 原型里英文行对应的中文行：带标签的第一行和 `NO_TWICE` 在 F14-T04 和 F14-T08 里，换菜那一行在 F14-T04、F14-T05、F14-T08 和 F14-T09 里，“Not enough recipes”的两行都在 F14-T06 里。
- “Swap one dish”里中文那一行对应的英文行：F14-T05。
- 不带 `--tag`、填完后仍有空餐的情况：F14-T02、F14-T03、F14-T07、F14-T08 和 F14-T29，两种语言。
- `TOO_FEW` 和 `TOO_FEW_WITH_TAG`：F14-T02、F14-T03、F14-T08 和 F14-T17，两种语言。
- 一周没有空餐：F14-T05 和 F14-T09，两种语言。
- `CANNOT_FILL`：F14-T15 和 F14-T19，两种语言。`LEFT_BEHIND`：F14-T20，两种语言。
- 帮助里的那一行：F14-T01。
- 设置 `dishes` 的位置和问题：F14-T21、F14-T23 和 F14-T24，两种语言。
- 只有一餐时的英文形式：F14-T08 和 F14-T17。

B 点在 F14-T02、F14-T03、F14-T08、F14-T17、F14-T21 到 F14-T24、F14-T28 和 F14-T33 里。C 点在 F14-T02、F14-T03、F14-T08、F14-T17 和 F14-T33 里。D 点在 F14-T04、F14-T05、F14-T08、F14-T09、F14-T19 和 F14-T20 里。

**之前功能的测试。** 设计第 3 节列出了 F14 会打破的六个已验收功能的测试：`COMMANDS` 里的 `MENU_SUGGEST_COMMAND` 这一项改变了帮助和 `recipe-menu menu` 那一行，键 `dishes` 改变了设置的 `UNKNOWN_KEY` 的文字。在架构师的模型上，全部测试在 Windows 上给出 577 个通过、6 个失败、4 个跳过，失败的 6 个正好是这些测试（设计第 4 节）。开发者从不修改测试（R08），每个已验收功能的测试都必须通过（R10）。所以测试工程师在本方案之后、F14 的 mock PR 之前，用一个 `[F14 test-fix]` PR 修改这全部六个测试（TE3）。每处修改都让它的测试在 F14 之前和之后都成立，在 F15 和 F16 加上它们的命令、F16 加上它的键之后也成立，这样 F15 和 F16 就不需要为它们再修一次测试（架构师备注 5）：

- F05-T10 和 F05-T11，在 `tests/test_f05_read_settings_errors.py` 里，用到 `tests/f05_texts.py` 的 `unknown_key` 和 `KEYS_EN`。它们拿设置的 `UNKNOWN_KEY` 和“language, meals, and servings”比较。现在每个用例检查每个 `UNKNOWN_KEY` 的文字是 `Unknown key "K". The keys are L.` 和 `未知键“K”。可用的键：L′。`，其中 L 和 L′ 是同一列键用 F02 的 `and_list` 写成的英文和中文，并检查这列键以 `language`、`meals` 和 `servings` 开头，按这个顺序。每个问题的其他部分，以及其他每个问题，都和以前一样比较。所以这两个用例在 F14 实现之前有三个键时成立，在 `read_settings` 读取 `dishes` 之后 `dishes` 排在它们后面时成立（3.2），在 F16 加上它的键时也成立。
- F11-T32，在 `tests/test_f11_cli.py` 里。它用真正的 `COMMANDS` 运行 `recipe-menu menu` 和 `recipe-menu menu --lang zh`，预期两个命令。现在这两行运行 `main` 时用 `commands=` 传入 v0.1 的八个命令，按帮助里的顺序：`INIT_COMMAND`、`CHECK_COMMAND`、`LIST_COMMAND`、`SHOW_COMMAND`、`SEARCH_COMMAND`、`MENU_NEW_COMMAND`、`MENU_SHOW_COMMAND` 和 `SHOP_COMMAND`，就像 F11-T01 传入它的七个命令一样。它们预期的几行不变。F14-T21 用真正的 `COMMANDS` 检查有三个命令的那一行。
- F13-T01，在 `tests/test_f13_command.py` 里。它的示例和输入 5 拿真正的 `COMMANDS` 的帮助和 `tests/f05_texts.py` 的 `HELP_EN` 和 `HELP_ZH` 比较。现在示例的 `help_lines` 和输入 5 用 `commands=` 传入 v0.1 的八个命令，所以 F05 原型的 21 行仍是预期的帮助。新的输入 6 在真正的 `COMMANDS` 的帮助里检查 `shop` 那一行有它的用法和帮助行，它的文字从 `--lang en|zh` 的文字所在的那一列开始，就像 F11-T01 检查它的几行一样。
- F13-T22，在 `tests/test_f13_cli.py` 里，和 F13-T27，在 `tests/test_f13_integration.py` 里。它们拿 `shop next --help`、`shop 2026-W99 --help --lang zh` 和 `shop --help` 的输出和 `HELP_EN`、`HELP_ZH` 比较。现在每个都改为和用真正的 `COMMANDS`、不带文件夹运行 `--help` 或 `--help --lang zh` 的输出比较，就像 F11-T32 那样。

本 PR 让 F05、F11 和 F13 的测试方案与这些修改一致：F05-T10、F05-T11，以及第 2 节关于 `UNKNOWN_KEY` 的约定（F05 测试方案版本 1.1），F11-T32（F11 测试方案版本 1.1），以及 F13-T01、F13-T22 和 F13-T27（F13 测试方案版本 1.1）。测试修复 PR 的一个支持模块按帮助里的顺序给出 v0.1 的八个命令，F14-T01 在其中的 `MENU_SHOW_COMMAND` 之后加上 `MENU_SUGGEST_COMMAND`。测试修复 PR 修改的每个支持模块，比如 `tests/f05_texts.py`，都让它的文档注释符合 P01。

这些测试仍然成立，正如设计第 3 节所说。F07-T17、F08-T14、F09-T01、F10-T01 和 F11-T01 检查真正的帮助里某一行跟在另一行后面，并且它的文字从 `--lang en|zh` 的文字所在的那一列开始。两者都成立，因为 `menu suggest` 那一行在 `menu show` 那一行之后，而每一行都移动同样的 3 列。F11-T27 和 F11-T35 拿真正的 `COMMANDS` 的一份帮助和另一份比较。F05 的测试运行它们自己的命令。`init` 和 `menu new` 写出的文件和以前相同，所以 v0.1-S01、v0.1-S02 和 v0.1-S13 成立。F14 的测试 PR 不改动之前功能的任何测试，不改动 `tests/data/example/` 的任何文件，也不改动 `tests/f08_support.py` 或 `tests/f13_support.py` 的任何函数。

**R09。** mock 定义了每条消息和带全部字段的 `MENU_SUGGEST_COMMAND`，并把这一项加进 `COMMANDS`。它给 `Settings` 加上带默认值的字段 `dishes` 和给出 1 的 `dishes_for`，不带 3.1 的检查；它让 `read_settings` 保持原样，所以 `dishes` 仍是未知键。它给 `Context` 加上带默认值的字段 `random`，给 `main` 加上参数 `random`，但不把它传下去。它的 `read_file_text` 给出空文字，`parse_toml` 给出 `None`，`run` 不读文件，什么都不写，什么都不抛，并给出 0（设计第 2 节）。所以只检查 `MENU_SUGGEST_COMMAND` 的字段、帮助、`recipe-menu menu` 那一行、某条消息、退出码 0、空的错误流、`Settings` 和 `Context` 的默认值和相等、`Context` 的默认生成器、只有 1 道菜的餐的 `dishes_for`、没有 `dishes` 的文件的 `read_settings`，或者不是 TOML 的文字的 `parse_toml` 的测试，会在 mock 上通过。只检查 `cli` 在运行 `menu suggest` 之前所做的事情的测试也一样：数据文件夹不存在、设置损坏、两个星期、未知选项、`--tag` 没有值或写了两次，以及 `menu suggest next --help`。只检查一次运行没有修改文件的测试也一样，比如一周没有空餐、`NO_MENU`、未知标签、错误或拒绝时，或者只检查没有留下 `.tmp` 文件的测试。检查这类内容的每个用例，同时也检查 mock 做错的东西：`menu suggest` 的输出，它给出的退出码 1、2 或 130，`run` 抛出的 `UsageError`，填好的文件的字节，来源或工具记录的调用，有更多道菜的餐的 `dishes_for`，`Settings` 抛出的错误，`read_settings` 给出的带 `dishes` 的 `Settings` 或 `dishes` 的问题，`main` 传下去的生成器，或者 `read_file_text` 给出的文字和问题、`parse_toml` 给出的表。F14-T01、F14-T09、F14-T12、F14-T19、F14-T21 到 F14-T25、F14-T27、F14-T30 和 F14-T31 只在 mock 做错的结果旁边检查这类内容。预期 `menu suggest` 给出退出码 0 的每个用例都检查它的全部输出，而这个输出从不为空。`tests/f14_support.py` 和 `tests/f14_texts.py` 在被导入时不调用 F14 的任何接口。

**两个系统。** 每个用例都在 Linux 和 Windows 上运行，没有用例在任何一个系统上跳过。CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。问题、换菜那一行和保存失败的第一行用相对于数据文件夹的路径、用系统的路径分隔符写出菜单文件（D 点）。所以在预期的一行里，`menus/2026-W48.toml` 代表 `str(Path("menus", "2026-W48.toml"))`：在 Windows 上是 `menus\2026-W48.toml`，正如 F14 原型所示，在 Linux 上是 `menus/2026-W48.toml`。以用例的某个文件夹开头的路径，比如 `X/menus/2026-W47.toml.tmp`，代表 `tmp_path` 下这个完整路径的 `str`。`menu suggest` 在两个系统上都写出 UTF-8、LF 换行的文件（选择 7）。有一个输入在两个系统上结果不同，它的用例写明两者：别的程序正打开着的菜单文件（F14-T20）。Windows 拒绝替换它，`menu suggest` 给出保存失败的几行，保留旧的字节。Linux 替换它，这次运行填好这一周，就像 F13-T21 那样。F14-T20 的数据文件夹 `One Drive/菜谱` 含有空格和中文字符，在两个系统上都是有效的路径。

**被拒绝的访问。** 没有用例通过文件系统拒绝访问，不用 `os.chmod`、访问控制列表，也不用 `tests/f04_support.py` 的 `listing_denied`。Linux 上的 root 用户无视权限位，所以依赖它们的测试在 root 下会失败。用例里的每个 `PermissionError` 都来自故障工具，它对每个用户都以同样的方式抛出，或者来自 Windows 拒绝替换一个被打开着的文件。所以每个用例在 Linux 上以 root 运行、在 Windows 上以管理员运行时都能通过。

**用例怎样让磁盘出错。** 用例使用 `tests/f13_support.py` 的 `shop_faults(base, *rules)`，规则和效果与 F13 测试方案相同：`open P: E`、`write P: E`、`close P: E`、`move P: E`、`unlink P: E` 和 `unlink P: later E`，以及效果 `DENIED`、`IO`、`NO_SPACE` 和 `CTRL_C`。F14 还用到 `read` 这一类。F08 的工具把每次不是 `x` 模式的打开记录为 `read`，规则可以指定它：`read P: E` 在每次读 P 时抛出 E 来代替读取，`read P: later E` 让第一次读 P 照常进行，之后每次读 P 时抛出 E。所以 `read menus/2026-W47.toml: later DENIED` 让 `read_week_menu` 读到这个文件，而让 2.2 第 8 步的读取失败。抛出 `KeyboardInterrupt` 的用例通过 `tests/f08_support.py` 的 `call_main` 从 `main` 得到退出码 130；`KeyboardInterrupt` 离开 `main` 时，`call_main` 把它变成一次失败。

给开发者的说明：只有当 `read_file_text` 通过 `io.open` 读取文件时，这些用例才成立；在 Troy 电脑上的 Python 3.13.18 里，`Path.read_bytes` 和 `open(path, "rb")` 都是这样，所以工具能记录这次读取，也能让它失败。绕过 `io.open` 的调用，比如 `os.open`，会逃过工具，F14-T14 和 F14-T26 会失败。`menu suggest` 只通过 `replace_file` 写文件，它的调用由 F13 测试方案列出。

**读取的记录。** F14-T09、F14-T10、F14-T11、F14-T12、F14-T14、F14-T19 和 F14-T26 用 `shop_faults(F.root)` 记录 `menu suggest` 打开、删除和移动了哪些文件，列出了哪些文件夹，除非用例给出规则，否则不带规则，就像 F13-T14 那样。工具把数据文件夹下某个路径的每次打开记录为 `read`，`x` 模式的记录为 `open`，每次删除记录为 `unlink`，每次移动记录为 `move A B`，路径都相对于这个文件夹、用 `/` 分隔。它把每次用 `os.scandir` 或 `os.listdir` 的列出记录在“列出记录”里。`cli` 在运行命令之前读 `settings.toml`，所以每次运行 `main` 的记录都以 `read settings.toml` 开头。

**随机选择的来源。** `menu suggest` 调用一次 `context.random.sample(C, k)`，不从生成器取别的东西（选择 6）。C 是按 ID 顺序排列的候选：这一周没有哪道菜用到的 ID，它的菜谱读取时没有错误，并且给出 `--tag` 时带有这个标签。k 是 `min(need, len(C))`，其中 `need` 是各个空餐的菜数之和。用例用三种来源，这样没有用例依赖某个 Python 版本的 `random.Random` 对某个种子给出的序列：

- `Random(n)` 是 `random.Random(n)`。“`Random(n)` 选出的菜谱”是 `Random(n).sample(C, k)`，测试用它这次运行的 C 和 k 算出它，正如选择 6 所说。没有用例把某个种子选出的菜谱写成字面量。
- 前取来源是 `tests/f14_support.py` 里 `random.Random` 的一个子类。它的 `sample(population, k)` 把这次调用记录为 `(list(population), k)`，并给出 population 的前 k 项。从它取任何别的东西，比如 `random()`、`getrandbits`、`randrange`、`choice`、`choices` 或 `shuffle`，都会让用例失败。
- 后取来源与此相同，但给出 population 的最后 k 项，最后一项排在最前。

除非用例指定别的来源，`menu suggest` 的每一行都用一个新的前取来源运行。用前取来源时，新菜就是按 ID 顺序排列的候选，所以预期的文件都是字面量。

测试数据遵守这些规则，与 F11 和 F13 测试方案相同：

- `EXAMPLE` 是仓库里的文件夹 `tests/data/example/`（架构 10）。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这个副本上的 `DataFolder`。在用例里，`example` 就是这个 `DataFolder`。它的七个菜谱按 ID 顺序是 `choy-sum`、`cola-wings`、`mapo-tofu`、`red-braised-pork`、`rice`、`tomato-egg` 和 `tomato-egg-noodles`。“P 处的新示例”是用 `tests/f05_support.py` 的 `copy_example` 做的又一个副本。不带 P 的“新示例”在 `tmp_path` 下它自己的路径上。用例里的“副本”是做了同样修改的新示例。
- P 处的推荐文件夹是 P 处的一个新示例，再加 33 个菜谱，与 v0.2 测试方案的描述相同：带标签 快手 的 `quick-01` 到 `quick-13`，带标签 辣 的 `spicy-01` 和 `spicy-02`，以及带标签 家常 的 `home-01` 到 `home-18`。每个新菜谱只带一个标签，2 份，有中文名和英文名，有一个目录里的食材，比如 `{ item = "番茄", amount = "300 g" }`，每种语言一个步骤，所以 `check` 在其中找不到问题。`tests/f14_support.py` 的 `suggest_folder` 做出它。这样共有 16 个菜谱带标签 快手，3 个带标签 辣，它的 40 个 ID 按 ID 顺序是 `choy-sum`、`cola-wings`、`home-01` 到 `home-18`、`mapo-tofu`、`quick-01` 到 `quick-13`、`red-braised-pork`、`rice`、`spicy-01`、`spicy-02`、`tomato-egg` 和 `tomato-egg-noodles`。
- “menus 为空的示例”是删掉 `menus/` 里每一项的新示例。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 做出的空文件夹。
- 测试用 `tests/f03_support.py` 的 `write` 写每个文件，它写 UTF-8、LF 换行，并先建好文件夹；或者用 `put_bytes` 按字节写。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 把文件 F 里的第一个 X 换掉，它会检查 F 里有 X。
- 没有测试修改仓库、碰 `~/recipe-menu` 或读时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`。F14-T32 通过 `tests/f05_support.py` 的 `run_module` 启动 `python -m recipe_menu`，它把 `HOME` 和 `USERPROFILE` 设为 `tmp_path` 里的一个文件夹。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

这些有名字的修改做出用例的文件夹。每个都作用于它所在用例的数据文件夹：

- 来自 F09、F11 和 F13 测试方案：没有目录、目录的花括号、没有 recipes 文件夹、recipes 是文件、Rice Bowl、大写的 rice、文件夹 x、麻婆的错误、rice 为 0、损坏的设置、一个标签、没有标签、空的 recipes、没有 menus 文件夹，以及 menus 是文件。`tests/f07_changes.py`、`tests/f09_support.py` 和 `tests/f11_support.py` 的辅助函数做出它们。麻婆的错误让 `recipes/mapo-tofu.toml` 的食材 3 写成目录里没有的 豆瓣酱。rice 为 0 让 `recipes/rice.toml` 是 0 份；red-braised-pork 为 0 用 `servings_zero` 同样做出，让 `recipes/red-braised-pork.toml` 是 0 份。
- 来自 F10 测试方案：中文设置，把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`；BOM 和 CRLF，把文件夹里的每个文件重写为 `b"\xef\xbb\xbf"` 加上它的字节，其中每个 `b"\n"` 换成 `b"\r\n"`。
- 来自 `tests/f06_support.py` 里 F06 的辅助函数：菜单的笔误，让 `menus/2026-W47.toml` 的周一晚餐写成 `tomato-eggs`；以及 v0.1-S07 的菜单错误。
- 小写的星期：`menus/2026-w48.toml` 写成空文件，与 `tests/f13_support.py` 的 `empty_menu_file` 写的相同。
- 餐次 M：`settings.toml` 写成一行 `meals = [...]`，餐次 M 按 `Meal` 的顺序，与 `tests/f11_support.py` 的 `settings_meals` 写的相同。所以设置不指定语言，份数是 2。
- 菜数 T：用 `tests/f07_changes.py` 的 `append` 在 `settings.toml` 末尾加上一行 `dishes = T`，比如 `dishes = { dinner = 2 }`。
- `NEW(W, M)` 是 `menu new` 为星期 W 和餐次 M 写出的文件：`tests/f11_support.py` 的 `menu_text(W, M)` 的字节。“W 写成 `NEW(W, M)`”用它们写出 `menus/W.toml`。
- `DINNERS(W; L1, ..., L7)` 是只有晚餐的星期 W 的文字：一行 `week = "W"`，然后从周一到周日，每天一个空行、一行 `[day]` 和一行 `dinner = Li`，其中 Li 是一个 TOML 列表，比如 `["rice"]` 或 `[]`。每一行都以 LF 结尾。
- 文字 A 到 D 和 R1 到 R6 是下面的代码块和各行，按用例所说写成 `menus/2026-W48.toml`、`menus/2026-W47.toml` 或 `menus/2026-W49.toml`。

调用 `main` 遵守这些约定：

- 像“在 F 里用 S 运行 `menu suggest 2026-W48 --tag quick`”这样的一行，代表 `tests/f14_support.py` 的 `suggest(home, F, "menu", "suggest", "2026-W48", "--tag", "quick", random=S)`。它加上 `--data` 和 F，用 `home`、`environ={}`、`today=date(2026, 11, 10)`、两个新的 `io.StringIO` 流、不传 `commands`，以及 `random=S` 运行 `main`。“在 D 这天”的一行传入 `today=D`。“不带文件夹”的一行没有 `--data`。可能被规则用 `CTRL_C` 打断的一行通过 `tests/f08_support.py` 的 `call_main` 运行，它不传生成器。
- 其他命令的一行，比如 `menu new 2026-W48` 或 `check`，通过 `tests/f09_support.py` 的 `at` 运行，“在 D 这天”的一行通过 `tests/f11_support.py` 的 `on` 运行，都不传生成器。`--help` 的几行通过 `tests/f07_support.py` 的 `call` 运行。
- 引号里的一个词是一个参数，写成带转义的 Python 字符串，比如 `""` 或 `" quick "`。词里的每个 `\uXXXX` 代表那一个字符。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟 `"\n"`，没有别的东西。`(c, err L)` 同样代表 `(c, "", err)`。`(130, "", "")` 是什么都没写就退出。测试比较完整的文字。
- 用例里的“这个文件”是它那一行所指星期的菜单文件。“这个文件保留它的字节和时间”指这一行之后它的字节和 `st_mtime_ns` 与之前相同。
- `STOP(W, M)` 和 `STOP_ZH(W, M)` 是 `stop_at_error` 的英文和中文三行，与 F09 测试方案的定义相同，由 `tests/f09_texts.py` 的 `stop` 构造结果。W 是一个文件，或者一个文件加一个位置，比如 `menus/2026-W47.toml, Monday dinner`。
- “在 `check` 的错误之中”的含义与 F09 测试方案相同，由 `tests/f09_support.py` 的 `assert_among_check` 检查。

预期的文字如下。测试在 `tests/f14_texts.py` 里把每一段写成字面量，或者在那里用字面量模板构造出来。它们不引用 `suggest`、`settings` 或 `menus` 的任何消息，也从不读取原型文件，因为这些消息都是内部的（设计第 2 节，架构 8）。在每一段里，W 是一个星期，比如 `2026-W48`，T 是标签在输出语言里的名称，数为 1 时用单数形式：`meal`、`has` 和 `stays`，代替 `meals`、`have` 和 `stay`。

- `FIRST(W, n)` 和 `FIRST(W, n, T)` 是第一次填满的四行：`Filled n empty meals of W.`，带 T 时是 `Filled n empty meals of W with recipes that have the tag "T".`，然后是 `No recipe appears twice in the week.`、`Run "recipe-menu menu show W" to see the week.`，以及换菜那一行 `To swap a dish, empty its meal in menus/W.toml, then run "recipe-menu menu suggest W" again.`。`FIRST_ZH(W, n)` 和 `FIRST_ZH(W, n, T)` 是 `已为 W 填好 n 个空餐。`，带 T 时是 `已为 W 填好 n 个空餐，用的都是带有标签“T”的菜谱。`，然后是 `这一周里没有重复的菜谱。`、`运行“recipe-menu menu show W”查看这一周。` 和 `要换掉一道菜，就在 menus/W.toml 里清空它那一餐，然后再运行“recipe-menu menu suggest W”。`。
- `REFILL(W, n, k)` 和 `REFILL(W, n, k, T)` 是有 k 餐已经有菜、所有空餐都填满时的两行：`FIRST` 的第一行、一个空格和 `Kept the k meals that already have dishes.`，然后是 `Run "recipe-menu menu show W" to see the week.`。`REFILL_ZH` 是 `FIRST_ZH` 的第一行后面跟 `保留了已经有菜的 k 餐。`，然后是 `运行“recipe-menu menu show W”查看这一周。`。
- `SOME(W, f, e, k, why)` 和 `SOME(W, f, e, k, why, T)` 是有 k 餐已经有菜、e 个空餐里填了 f 个时的两行。第一行是 `Filled f of e empty meals of W`，带 T 时接着 ` with recipes that have the tag "T"`，然后是 `.`，k 大于 0 时再接一个空格和 `Kept the k meals that already have dishes.`。`meals` 的形式随 e。第二行里 c = e − f，why 为 `left` 时是 `c meals stay empty: no other recipe is left.`，带 T 时是 `c meals stay empty: no other recipe has the tag "T".`；why 为 `few` 时是 `c meals stay empty: too few other recipes are left.`，带 T 时是 `c meals stay empty: too few other recipes have the tag "T".`。`SOME_ZH` 的第一行是 `已为 W 填好 e 个空餐中的 f 个`，带 T 时接着 `，用的都是带有标签“T”的菜谱`，然后是 `。`，k 大于 0 时再接 `保留了已经有菜的 k 餐。`。它的第二行是 `c 餐仍是空的：没有别的菜谱可选了。`、`c 餐仍是空的：没有别的菜谱带有标签“T”。`、`c 餐仍是空的：剩下的菜谱不够了。` 或 `c 餐仍是空的：带有标签“T”的别的菜谱不够了。`。
- `FULL(W)` 是 `W has no empty meal. Nothing was changed.` 和换菜那一行。`FULL_ZH(W)` 是 `W 没有空餐。没有做任何修改。` 和中文的换菜那一行。
- `CANNOT(W)` 是三行 `menus/W.toml`、`  menu suggest cannot fill this file: write each day as a line such as [monday], and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.` 和 `Nothing was changed.`。`CANNOT_ZH(W)` 是 `menus/W.toml`、`  menu suggest 无法填写这个文件：请把每一天写成 [monday] 这样的一行，把每个空餐写成 dinner = [] 这样的一行，和“recipe-menu menu new”写的一样。` 和 `没有做任何修改。`。
- `FAIL(W, M)` 是保存失败的三行：`menus/W.toml`，两个空格加 M 的英文，以及 `Nothing was changed.`。`FAIL_ZH(W, M)` 用 M 的中文和 `没有做任何修改。`。`LEFT(W, M, P)` 的第三行是 `Nothing was changed, but menu suggest could not remove P. Delete it.`，`LEFT_ZH(W, M, P)` 的是 `没有做任何修改，但 menu suggest 没能删除 P。请删除它。`。P 是完整路径。
- `TAGS(V)` 是 `Unknown tag "V". The tags are quick, home-style, vegetarian, spicy, and staple.`，`TAGS_ZH(V)` 是 `未知标签“V”。现有标签：快手、家常、素、辣和主食。`。`ONE_TAG(V)` 是 `Unknown tag "V". The only tag is quick.`，`ONE_TAG_ZH(V)` 是 `未知标签“V”。现有标签：快手。`。`NO_TAGS(V)` 是 `Unknown tag "V". The catalog has no tags.`，`NO_TAGS_ZH(V)` 是 `未知标签“V”。目录里没有标签。`。V 是输入时的 `--tag` 的值。
- `NO_MENU(W)`、`NO_MENU_ZH(W)`、`NOT_A_WEEK(V)` 和 `NOT_A_WEEK_ZH(V)` 与 F11 测试方案相同，由 `tests/f11_texts.py` 的 `no_menu`、`no_menu_zh`、`not_a_week` 和 `not_a_week_zh` 给出。
- `HELP_14` 是九个命令的帮助的 22 行：F05 原型“Help in English”的第 1 到 4 行，设计 2.1 英文代码块里从 `Commands:` 到 `  --help                Show this help.` 的 16 行，一个空行，以及原型帮助的最后一行 `WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.`。`HELP_14_ZH` 用同样的方法由“Help in Chinese”和设计 2.1 的中文代码块构造。
- 3.2 的设置消息：`DISHES_NOT_A_TABLE` 是 `"dishes" must be a table in braces, such as dishes = { dinner = 2 }.` 和 `“dishes”必须是放在花括号里的表，比如 dishes = { dinner = 2 }。`。`DISHES_NOT_1_TO_10` 是 `The number of dishes must be a whole number from 1 to 10, such as 2.` 和 `菜数必须是 1 到 10 之间的整数，比如 2。`。位置 `dishes` 是 `BiText("dishes", "菜数")`，位置 `dishes of M` 是 `BiText("dishes of breakfast", "早餐的菜数")`、`BiText("dishes of lunch", "午餐的菜数")` 或 `BiText("dishes of dinner", "晚餐的菜数")`。设置的 `UNKNOWN_MEAL(meal="M")` 是 `Unknown meal "M". The meals are breakfast, lunch, and dinner.` 和 `未知餐次“M”。可用的餐次：breakfast、lunch 和 dinner。`。设置的其他消息与 F05 测试方案相同。

用例里 `cli` 的消息是 F05 设计 2.10 的文字，用 `menu suggest` 代入。用例里读取器的消息与 F09、F11 和 F13 测试方案相同：`FILE_MISSING`、`FILE_IS_FOLDER`、`MISSING_BRACE`、`FOLDER_MISSING`、`FOLDER_IS_FILE`、列出时的 `NOT_A_RECIPE_ID`、`TOML_ENDING_NOT_SMALL`、`NOT_A_WEEK_NAME`、`UNKNOWN_RECIPE(recipe="tomato-eggs")`、`WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`、`UNKNOWN_INGREDIENT(name="豆瓣酱")`、`SERVINGS_TOO_FEW(servings=0)`，以及设置的 `UNKNOWN_MEAL(meal="supper")`。`FILE_WRITE_DENIED` 和 `FILE_WRITE_ERROR(reason="X")` 是 `tests/f08_texts.py` 里的那些。`ACCESS_DENIED` 是 `The file cannot be read: access is denied.` 和 `无法读取文件：没有访问权限。`，`NOT_UTF8` 是 `The file cannot be read: it is not UTF-8 text. Save it as UTF-8.` 和它的中文，`SYSTEM_ERROR(reason="X")` 是 `The file cannot be read. The system says: X` 和 `无法读取文件。系统提示：X`，与 `tests/f03_support.py` 里的相同。

在下面的代码块里，除非代码块另有说明，每一行都以 LF 结尾，最后一行也是。`<TAB>` 代表一个制表符 U+0009。代码块按文件里的样子显示每个字符。

文字 A，用默认设置，午餐和晚餐：

```text
week = "2026-W48"

[monday]
lunch=[]
dinner = [ ]  # nothing yet

[ 'tuesday' ]  # guests
"lunch" = []
<TAB>'dinner'<TAB>=<TAB>[<TAB>]
```

用前取来源运行之后的文字 A：

```text
week = "2026-W48"

[monday]
lunch=["choy-sum"]
dinner = ["cola-wings"]  # nothing yet

[ 'tuesday' ]  # guests
"lunch" = ["mapo-tofu"]
<TAB>'dinner'<TAB>=<TAB>["red-braised-pork"]

[wednesday]
lunch = ["rice"]
dinner = ["tomato-egg"]

[thursday]
lunch = ["tomato-egg-noodles"]
```

文字 B，餐次为早餐、午餐和晚餐：

```text
week = "2026-W48"

[monday]  # busy
# plan below
lunch = []
```

用前取来源运行之后的文字 B：

```text
week = "2026-W48"

[monday]  # busy
breakfast = ["choy-sum"]
dinner = ["mapo-tofu"]
# plan below
lunch = ["cola-wings"]

[tuesday]
breakfast = ["red-braised-pork"]
lunch = ["rice"]
dinner = ["tomato-egg"]

[wednesday]
breakfast = ["tomato-egg-noodles"]
```

文字 C，餐次为晚餐。它的最后一行没有 LF：

```text
week = "2026-W48"
[sunday]
dinner = []
[monday]
dinner = ["rice"]
```

用前取来源运行之后的文字 C：

```text
week = "2026-W48"
[sunday]
dinner = ["tomato-egg-noodles"]
[monday]
dinner = ["rice"]

[tuesday]
dinner = ["choy-sum"]

[wednesday]
dinner = ["cola-wings"]

[thursday]
dinner = ["mapo-tofu"]

[friday]
dinner = ["red-braised-pork"]

[saturday]
dinner = ["tomato-egg"]
```

文字 D，餐次为晚餐，是没有 LF 的一行 `week = "2026-W48"`。文字 D′ 是带 LF 的同一行。用前取来源运行之后的文字 D：

```text
week = "2026-W48"

[monday]
dinner = ["choy-sum"]

[tuesday]
dinner = ["cola-wings"]

[wednesday]
dinner = ["mapo-tofu"]

[thursday]
dinner = ["red-braised-pork"]

[friday]
dinner = ["rice"]

[saturday]
dinner = ["tomato-egg"]

[sunday]
dinner = ["tomato-egg-noodles"]
```

拒绝的文字，用默认设置：

- R1 是示例的 `menus/2026-W47.toml`，删掉周日晚餐那三道菜的三行，于是 `dinner = [` 和 `]` 留在两行上，正如选择 7 所描述的。这时这一周不再有 `cola-wings`。
- R2 是 R1 把周日的 `dinner = [` 换成 `dinner = [  # later`。
- R3 到 R6 是下面的代码块，写成 `menus/2026-W49.toml`。在 R5 和 R6 里，`\u006e` 和 `\u0064` 是 TOML 转义的六个字符。

R3，设计里写在花括号里的一天：

```text
week = "2026-W49"
monday = { lunch = [], dinner = [] }
```

R4，用点号键写的一天：

```text
week = "2026-W49"
monday.dinner = []
```

R5，带转义的键：

```text
week = "2026-W49"

[monday]
lunch = []
"din\u006eer" = []
```

R6，带转义的表头：

```text
week = "2026-W49"

["mon\u0064ay"]
dinner = []
```

用例分在这些文件里，这样每个文件都不超过 R06 的 500 行：

| 文件 | 内容 |
| --- | --- |
| `tests/test_f14_command.py` | F14-T01 和 F14-T02。 |
| `tests/test_f14_fill.py` | F14-T03 到 F14-T09。 |
| `tests/test_f14_weeks_and_tags.py` | F14-T10 到 F14-T12。 |
| `tests/test_f14_stops.py` | F14-T13 到 F14-T15。 |
| `tests/test_f14_text.py` | F14-T16 到 F14-T19。 |
| `tests/test_f14_failures.py` | F14-T20。 |
| `tests/test_f14_cli.py` | F14-T21。 |
| `tests/test_f14_settings.py` | F14-T22 到 F14-T24。 |
| `tests/test_f14_values.py` | F14-T25 到 F14-T27。 |
| `tests/test_f14_integration.py` | F14-T28 到 F14-T32。 |
| `tests/test_f14_random.py` | F14-T33。 |
| `tests/test_f14_size.py` | F14-T34。 |
| `tests/f14_support.py` | 没有测试。前取来源和后取来源、带来源调用 `main`、推荐文件夹、`DINNERS`，以及设置的修改。它的文档注释遵守 P01。 |
| `tests/f14_texts.py` | 没有测试。上面预期的文字和文字 A 到 D、R3 到 R6，写成字面量，以及输出各行的构造函数。它的文档注释遵守 P01。 |
| `tests/conftest.py` | 不变。F14 用到它的 fixture `example_folder`、`folder` 和 `default_int_limit`，以及 pytest 的 `tmp_path` 和 `monkeypatch`。 |

某个文件超过 500 行时，测试工程师可以把它再拆分。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F14-T01 | 单元 | `MENU_SUGGEST_COMMAND`、`MENU_SUGGEST_COMMAND.run`、`main` | 2.1 的示例。`MENU_SUGGEST_COMMAND` 有词 `menu suggest`、用法 `menu suggest [WEEK]` 和 `menu suggest [周]`、A 点的帮助行、可选且不重复的参数 `WEEK`、选项 `--tag`，以及 `FolderUse.READ`。它的 `run` 按 `Random(7)` 选出的顺序填好新的一周的七顿晚餐。九个命令的帮助有 22 行，`menu suggest` 那一行在 `menu show` 那一行之后，第二列从第 24 列之后开始。在真正的 `COMMANDS` 的帮助里，`menu suggest` 那一行跟在 `menu show` 那一行后面，它的文字从 `--lang en\|zh` 的文字所在的那一列开始（2.1，选择 1 和 6）。 | 示例的各行，`folder` 为 `example`，`home` 为 `home`。在 `help_lines` 里，调用 `main` 时还用 `commands=` 传入 v0.1 的八个命令，并在 `MENU_SHOW_COMMAND` 之后加上 `MENU_SUGGEST_COMMAND`，因为这 22 行只在 F15 和 F16 加上它们的命令之前成立。`# raises` 那一行在 `pytest.raises(UsageError)` 里运行，用值相同的新 `Context` 和新的流。然后：1. `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部。2. 用真正的 `COMMANDS` 运行 `--help` 和 `--help --lang zh`。 | 示例的每个断言都成立。`# raises` 那一行抛出 `UsageError`，它的英文是 `NOT_A_WEEK("2026-W99")`，提示是 `None`。之后它的两个流都为空，`menus/2026-W48.toml` 保留示例那次运行写出的字节。1. `HELP_14` 和 `HELP_14_ZH`。2. 退出码 0，err 为空。在 out 里，以 `  menu show [WEEK] ` 开头的那一行之后的一行以 `  menu suggest [WEEK] ` 开头，以 `Fill the empty meals of a week menu.` 结尾。在中文里，以 `  menu show [周] ` 开头的那一行之后的一行以 `  menu suggest [周] ` 开头，以 `给一个周菜单的空餐填上菜。` 结尾。它们的文字都与以 `  --lang en\|zh` 开头的那一行的文字从同一个显示列开始。F15 和 F16 加上它们的行之后，这些规则仍然成立，除非之后的设计在 `menu show` 和 `menu suggest` 之间放了一行。 |
| F14-T02 | 单元 | `MENU_SUGGEST_COMMAND.run` | `run` 从参数和 `context.today` 得到星期，从 `context.settings` 得到餐次、份数和每餐的菜数。它用 `context.lang` 写它的各行，从不用 `context.settings` 的语言。它每次运行从 `context.random` 取一次，或者从不带生成器构造的 `Context` 的默认生成器取，并且两次调用之间不保留状态。不是星期的值在 `run` 碰磁盘或写任何一行之前就抛出（2.1，2.2 第 1 步和第 10 步，选择 2、5 和 6，C 点，3.3）。 | S 和 S2 是新的前取来源，每次调用都用新的流。1. 在 `example` 里，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：用 `Context(Lang.ZH, example, Settings(Lang.EN, (Meal.DINNER,), 3, (1, 1, 2)), out, err, date(2026, 11, 24), S)` 和 `Arguments(())` 调用 `run`。2. 在新示例 F 里：用 `Context(Lang.EN, F, Settings(Lang.ZH), out, err, date(2026, 11, 10), S2)` 和 `Arguments(("next",))` 调用 `run`。3. 用同一个 S2 再做一次 2 的调用。4. 在新示例 G 里，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：用不带生成器的 `Context(Lang.EN, G, Settings(Lang.EN, (Meal.DINNER,), 2), out, err, date(2026, 11, 10))` 和 `Arguments(("2026-W48",))` 调用 `run`。5. 在 `shop_faults(F.root)` 里：用与 2 的值相同、带新的流和 S2 的新 `Context` 和 `Arguments(("2026-W99",))` 调用 `run`。 | 1. 0，out 为 `SOME_ZH(2026-W48, 3, 7, 0, few)`，err 为空：2026-11-24 所在的星期是 2026-W48。S 记录了一次调用，带按 ID 顺序的七个 ID 和 7。这个文件是 `NEW(2026-W48, [dinner])`，其中前三个 `dinner = []` 换成 `dinner = ["choy-sum", "cola-wings"]`、`dinner = ["mapo-tofu", "red-braised-pork"]` 和 `dinner = ["rice", "tomato-egg"]`，其他四个保留：周四需要 2 道菜，只剩 1 个。2. 0，out 为 `SOME(2026-W47, 1, 10, 4, left)`，err 为空：2026-11-10 的下一周是 2026-W47。S2 记录了 `(["red-braised-pork"], 1)`。这个文件是示例的文件，其中第一个 `lunch = []`，也就是周一的那个，换成 `lunch = ["red-braised-pork"]`。3. 0，out 为 `SOME(2026-W47, 0, 9, 5, left)`，err 为空。S2 记录了第二次调用 `([], 0)`，这个文件保留它的字节和时间。4. 0，out 为 `FIRST(2026-W48, 7)`，err 为空。这个文件是 `NEW(2026-W48, [dinner])`，其中七个 `dinner = []` 依次换成 `dinner = ["p"]`，p 是 `Random(0)` 选出的每个菜谱，因为 context 的默认生成器是一个新的 `Random(0)`。5. `UsageError`，它的英文是 `NOT_A_WEEK("2026-W99")`，提示是 `None`。两个流都为空，工具没有记录任何调用和列出，S2 没有再记录调用。 |
| F14-T03 | 功能 | `recipe-menu menu suggest`、`main` | 2.2 的示例，按顺序，用真正的命令：v0.2-S05，一次没有填任何餐、也不写文件的运行，未知标签，没有菜单的星期，错误的星期，一个漏写一餐和六天的文件，一个把一天写在花括号里的文件，以及设置 `dishes`，剩下一个菜谱时一顿晚餐保持空着（2.2，选择 2 到 9，B 点和 C 点）。 | 示例的各行，`folder` 为 `example`，`home` 为 `home`，以及示例的 `run`，它调用 `main` 时不传 `commands`，并传入一个新的 `Random(3)`。 | 示例的每个断言都成立。 |
| F14-T04 | 功能 | `recipe-menu menu suggest`、`recipe-menu menu new`、`recipe-menu menu show`、`recipe-menu check`、`main` | F14 原型“Fill an empty week”，以及 `main` 上的 v0.2-S01 和 v0.2-S02。带 `--tag` 第一次填满 14 餐，给出第一次填满的四行，标签名用输出的语言，不管 `--tag` 给的是哪个名称。每餐得到一个带这个标签的菜谱，按选出的顺序，没有菜谱出现两次，只有每餐的 `[]` 改变。两次运行用同样的种子和同样的文件，会选出同样的菜谱（2.2，选择 4、6、7 和 9，A 点和 D 点）。 | R 处的推荐文件夹。在 R 里：1. `menu new 2026-W48`。2. 用 `Random(5)` 运行 `menu suggest 2026-W48 --tag quick`。3. `menu show 2026-W48`。4. `check`。然后在 R2 处的推荐文件夹里：`menu new 2026-W48`，然后用 `Random(5)` 运行 `menu suggest 2026-W48 --tag 快手`。然后在 R3 处的推荐文件夹里：`menu new 2026-W48`，然后用 `Random(6)` 运行 `menu suggest 2026-W48 --tag quick --lang zh`。 | 1. `(0, out L)`，其中 L 是原型这一节的第一个输出，用 `R/menus/2026-W48.toml` 代替 `C:\Users\Troy\recipe-menu\menus\2026-W48.toml`。2. `(0, out FIRST(2026-W48, 14, quick))`，也就是这一节的第二个输出。这个文件是 `NEW(2026-W48, [lunch, dinner])`，其中 14 个 `[]` 依次换成 `["p"]`，p 是 `Random(5)` 从按 ID 顺序排列的 16 个带标签 快手 的 ID 里选出的每个菜谱：`choy-sum`、`quick-01` 到 `quick-13`、`tomato-egg` 和 `tomato-egg-noodles`。3. 退出码 0，err 为空，out 的最后一行是 `14 meals, 14 dishes. ×n: servings.`。4. `(0, out A)`，其中 A 是 `tests/f07_support.py` 的 `AFTER`，用 `40 recipes, and 2 week menus` 代替 `7 recipes, and 1 week menu`。在 R2 里，`(0, out FIRST(2026-W48, 14, quick))`，这个文件的字节与 R 的文件相同。在 R3 里，`(0, out FIRST_ZH(2026-W48, 14, 快手))`，这个文件用同样的方法写着 `Random(6)` 选出的菜谱。 |
| F14-T05 | 功能 | `recipe-menu menu suggest`、`main` | F14 原型“Swap one dish”，以及 `main` 上的 v0.2-S03。填你清空的那一餐，给出带 `KEPT` 的第一行，然后是 `RUN_SHOW`，没有 `NO_TWICE`，也没有换菜那一行。候选是另外 13 餐没有用到的菜谱，其中包括你去掉的那个，所以它可能又被选回来。然后，一周没有空餐时给出 `NO_EMPTY_MEAL` 和换菜那一行，退出码 0，不写文件（2.2 第 7 步和第 9 步，选择 6、8 和 9，A 点和 D 点）。 | R 处的推荐文件夹，先运行 `menu new 2026-W48`，再用 `Random(5)` 运行 `menu suggest 2026-W48 --tag quick`。X 是周三晚餐，也就是第六餐，选出的菜谱。在 R 里把 `dinner = ["X"]` 换成 `dinner = []`，然后在 R2 处做一个 R 的副本。在 R 里，用前取来源 S：1. `menu suggest 2026-W48 --lang zh`。2. `menu suggest 2026-W48`，然后 `menu suggest 2026-W48 --lang zh`。在 R2 里：3. `menu suggest 2026-W48`。 | 1. `(0, out ["已为 2026-W48 填好 1 个空餐。保留了已经有菜的 13 餐。", "运行“recipe-menu menu show 2026-W48”查看这一周。"])`，也就是原型这一节的输出。S 记录了一次调用，数为 1，带另外 13 餐没有用到的 27 个 ID，按 ID 顺序，其中有 X。这个文件与运行之前相同，只是周三晚餐那一行是 `dinner = ["P"]`，P 是这 27 个 ID 里的第一个。2. `(0, out FULL(2026-W48))` 和 `(0, out FULL_ZH(2026-W48))`。两个来源都没有记录调用，这个文件保留它的字节和时间。3. `(0, out REFILL(2026-W48, 1, 13))`，也就是 `Filled 1 empty meal of 2026-W48. Kept the 13 meals that already have dishes.` 和 `Run "recipe-menu menu show 2026-W48" to see the week.`。 |
| F14-T06 | 功能 | `recipe-menu menu suggest`、`main` | F14 原型“Not enough recipes”，以及 `main` 上的 v0.2-S04。每个候选都放进了某一餐时，这一周最前面的几餐得到 3 个带标签 辣 的菜谱，说明 11 餐仍是空的那一行写出这个标签（2.2，选择 6、7 和 9，A 点）。 | R 处的推荐文件夹：`menu new 2026-W49`，然后用 `Random(8)` 运行 `menu suggest 2026-W49 --tag spicy`。R2 处的推荐文件夹：`menu new 2026-W49`，然后用 `Random(8)` 运行 `menu suggest 2026-W49 --tag 辣 --lang zh`。 | 在 R 里，`(0, out SOME(2026-W49, 3, 14, 0, left, spicy))`，也就是原型这一节的输出。这个文件是 `NEW(2026-W49, [lunch, dinner])`，其中周一午餐、周一晚餐和周二午餐的 `[]` 依次换成 `["p"]`，p 是 `Random(8)` 从 `mapo-tofu`、`spicy-01` 和 `spicy-02` 里以数 3 选出的每个菜谱，其他 11 个 `[]` 保留。在 R2 里，`(0, out SOME_ZH(2026-W49, 3, 14, 0, left, 辣))`，这个文件的字节与 R 的文件相同。 |
| F14-T07 | 功能 | `recipe-menu menu suggest`、`recipe-menu menu show`、`main` | `main` 上的 v0.2-S05。在你填了一部分的一周里，这一周没有用到的那一个菜谱填上第一个空餐。填好的四餐保留它们的行，包括出现两次的 `choy-sum`、出现三次的 `rice` 和周日晚餐的份数，其他每一行都保留它的文字。第二次运行找不到候选，以退出码 0 说明这一点，不写文件。设置的语言决定输出的语言（选择 3、6、7 和 9，A 点）。 | 1. 在 `example` 里：用 `Random(3)` 运行 `menu suggest 2026-W47`。2. `menu suggest 2026-W47 --lang zh`。3. `menu show 2026-W47`。4. 在新示例里：`menu suggest 2026-W47 --lang zh`。5. 新示例里的中文设置：`menu suggest 2026-W47`，然后 `menu suggest 2026-W47 --lang en`。 | 1. `(0, out SOME(2026-W47, 1, 10, 4, left))`，也就是 `Filled 1 of 10 empty meals of 2026-W47. Kept the 4 meals that already have dishes.` 和 `9 meals stay empty: no other recipe is left.`。这个文件是示例的文件，其中第一个 `lunch = []`，也就是周一的那个，换成 `lunch = ["red-braised-pork"]`，其他每一行保持原样。2. `(0, out SOME_ZH(2026-W47, 0, 9, 5, left))`，这个文件保留它的字节和时间。3. `(0, out L)`，其中 L 是 `tests/f11_texts.py` 的 `SHOW_47`，第四行换成 `Mon 16 Nov   Red-braised pork belly ×2   Tomato and egg stir-fry ×2`，最后一行换成 `5 meals, 10 dishes. ×n: servings.`。4. `(0, out SOME_ZH(2026-W47, 1, 10, 4, left))`，也就是 `已为 2026-W47 填好 10 个空餐中的 1 个。保留了已经有菜的 4 餐。` 和 `9 餐仍是空的：没有别的菜谱可选了。`。5. `(0, out SOME_ZH(2026-W47, 1, 10, 4, left))`，然后 `(0, out SOME(2026-W47, 0, 9, 5, left))`。 |
| F14-T08 | 功能 | `recipe-menu menu suggest`、`main` | 输出的各种形式（2.2，输出的表）。每个 `Plural` 数为 1 时用单数形式，其他任何数，包括 0，都用复数形式，每段中文对每个数都相同。`FILLED_SOME` 随空餐数，`KEPT` 随保留的餐数，原因随仍是空的餐数。每个候选都放进了某一餐时，原因是 `STAY_EMPTY`；还剩候选时，原因是 `TOO_FEW`；给出 `--tag` 时各自带标签。一顿餐需要的菜比剩下的多时保持空着，后面需要得少的餐仍然得到它的菜。各餐按来源给出的顺序取选出的菜谱，而不是按 ID 顺序（选择 5、6 和 9，A 点到 D 点）。 | 每个输入都是一个新示例，带它指定的设置和星期。1. 餐次晚餐，以及 `DINNERS(2026-W48; ["choy-sum"], ["cola-wings"], ["mapo-tofu"], ["red-braised-pork"], ["rice"], ["tomato-egg"], [])`：`menu suggest 2026-W48`。在一个副本里 `menu suggest 2026-W48 --tag staple`，在另一个副本里 `menu suggest 2026-W48 --tag staple --lang zh`。2. 餐次晚餐，以及 `DINNERS(2026-W48; ["rice"], [], [], [], [], [], [])`：`menu suggest 2026-W48`，在一个副本里 `menu suggest 2026-W48 --lang zh`。3. 餐次晚餐，以及 `DINNERS(2026-W48; ["choy-sum", "cola-wings"], ["mapo-tofu"], ["red-braised-pork"], ["rice"], ["tomato-egg"], ["tomato-egg-noodles"], [])`：`menu suggest 2026-W48`、`menu suggest 2026-W48 --tag vegetarian` 和 `menu suggest 2026-W48 --lang zh`。4. 餐次晚餐，菜数 `{ dinner = 2 }`，以及 `DINNERS(2026-W48; ["choy-sum", "cola-wings"], ["mapo-tofu", "red-braised-pork"], ["rice", "tomato-egg"], ["rice"], ["rice"], ["rice"], [])`：`menu suggest 2026-W48`、`menu suggest 2026-W48 --tag staple`、`menu suggest 2026-W48 --lang zh` 和 `menu suggest 2026-W48 --tag staple --lang zh`。5. 餐次晚餐，菜数 `{ dinner = 2 }`，`menus/2026-W50.toml` 写成 `NEW(2026-W50, [dinner])`：`menu suggest 2026-W50 --tag quick`。在副本里 `menu suggest 2026-W50 --tag 快手 --lang zh` 和 `menu suggest 2026-W50 --tag home-style`。6. 餐次早餐、午餐和晚餐，菜数 `{ dinner = 2 }`，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [breakfast, lunch, dinner])`：`menu suggest 2026-W48`。在一个副本里，用后取来源运行同一行。7. 餐次晚餐，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：`menu suggest 2026-W48 --lang zh`。 | 1. `(0, out REFILL(2026-W48, 1, 6))`，周日那一行是 `dinner = ["tomato-egg-noodles"]`。带 `--tag staple` 时，`(0, out REFILL(2026-W48, 1, 6, staple))`，文件相同，来源记录了 `(["tomato-egg-noodles"], 1)`，因为 `rice` 在这一周里。带 `--lang zh` 时，`(0, out REFILL_ZH(2026-W48, 1, 6, 主食))`。2. `(0, out REFILL(2026-W48, 6, 1))` 和 `(0, out REFILL_ZH(2026-W48, 6, 1))`，周二到周日得到 `["choy-sum"]`、`["cola-wings"]`、`["mapo-tofu"]`、`["red-braised-pork"]`、`["tomato-egg"]` 和 `["tomato-egg-noodles"]`。3. `(0, out SOME(2026-W48, 0, 1, 6, left))`、`(0, out SOME(2026-W48, 0, 1, 6, left, vegetarian))` 和 `(0, out SOME_ZH(2026-W48, 0, 1, 6, left))`。每个来源都记录了 `([], 0)`，这个文件保留它的字节和时间。4. `(0, out SOME(2026-W48, 0, 1, 6, few))`、`(0, out SOME(2026-W48, 0, 1, 6, few, staple))`、`(0, out SOME_ZH(2026-W48, 0, 1, 6, few))` 和 `(0, out SOME_ZH(2026-W48, 0, 1, 6, few, 主食))`。每个来源都记录了 `(["tomato-egg-noodles"], 1)`：周日需要 2 道菜，只剩 1 个。这个文件保留它的字节和时间。5. `(0, out SOME(2026-W50, 1, 7, 0, few, quick))`，第一个 `dinner = []` 是 `dinner = ["choy-sum", "tomato-egg"]`，其他六个保留。在副本里，`(0, out SOME_ZH(2026-W50, 1, 7, 0, few, 快手))`，以及 `(0, out SOME(2026-W50, 2, 7, 0, left, home-style))`，前两个 `dinner = []` 是 `dinner = ["cola-wings", "mapo-tofu"]` 和 `dinner = ["red-braised-pork", "tomato-egg"]`。6. 两行都是 `(0, out SOME(2026-W48, 6, 21, 0, left))`。用前取来源时，周一有 `breakfast = ["choy-sum"]`、`lunch = ["cola-wings"]` 和 `dinner = ["mapo-tofu", "red-braised-pork"]`，周二有 `breakfast = ["rice"]`、`lunch = ["tomato-egg"]` 和 `dinner = []`，周三有 `breakfast = ["tomato-egg-noodles"]`。其他每餐保留 `[]`。用后取来源时，同样这六餐得到 `["tomato-egg-noodles"]`、`["tomato-egg"]`、`["rice", "red-braised-pork"]`、`["mapo-tofu"]`、`["cola-wings"]` 和 `["choy-sum"]`。两者都是周二晚餐保持空着，周三早餐得到它的菜。7. `(0, out FIRST_ZH(2026-W48, 7))`，七顿晚餐按 ID 顺序得到七个 ID。 |
| F14-T09 | 功能 | `recipe-menu menu suggest`、`main` | 没有空餐的一周。`menu suggest` 读完这一周就停下，不读文件的文字，也不读任何菜谱，所以这一周没有用到的菜谱里的错误什么都不改变。不管 `--tag` 指定什么，它都写出 `NO_EMPTY_MEAL` 和换菜那一行，退出码 0，不写文件（2.2 第 7 步，选择 3、8 和 9，D 点）。 | 新示例 F，餐次晚餐，带麻婆的错误，以及 `DINNERS(2026-W48; ["choy-sum"], ["cola-wings"], ["red-braised-pork"], ["rice"], ["tomato-egg"], ["tomato-egg-noodles"], ["rice"])`。在 F 里：1. `menu suggest 2026-W48`。2. `menu suggest 2026-W48 --lang zh`。3. `menu suggest 2026-W48 --tag spicy`。4. 在 `shop_faults(F.root)` 里：`menu suggest 2026-W48`。 | 1. `(0, out FULL(2026-W48))`。2. `(0, out FULL_ZH(2026-W48))`。3. `(0, out FULL(2026-W48))`。4. `(0, out FULL(2026-W48))`，记录是 `read settings.toml`、`read catalog.toml` 和一次 `read menus/2026-W48.toml`，列出记录是 `recipes` 和 `menus`。没有来源记录调用，每一行之后这个文件都保留它的字节和时间。 |
| F14-T10 | 功能 | `recipe-menu menu suggest`、`main` | 星期。不带 `WEEK` 和带 `this` 时，`menu suggest` 取 `context.today` 所在的星期，带 `next` 时取它的下一周。其他任何文字都是用法错误，只有 `NOT_A_WEEK`，退出码 2，由 `run` 在碰磁盘之前抛出（2.2 第 1 步，选择 2，F06 设计 2.7）。 | 1. 在 `example` 里：`menu suggest` 和 `menu suggest this`，然后 `menu suggest next`。2. 在新示例里，在 2026-11-17 这天：`menu suggest`。3. 在新示例里，`menus/2026-W53.toml` 写成 `NEW(2026-W53, [lunch, dinner])`，在 2026-12-30 这天：`menu suggest next`，然后 `menu suggest`。4. 在 `example` 里：对 `2026-W99`、`Next`、`THIS`、`""`、`" 2026-W47"`、`"2026-W47\n"`、`2026-w47`、`2026-W7`、`2025-W53`、`2026-W00`、`"this week"` 和 `"\uff12\uff10\uff12\uff16-W47"` 里的每个 V 运行 `menu suggest V`，与 F13-T01 相同。然后 `menu suggest 2026-W99 --lang zh` 和 `menu suggest Next --lang zh`。5. 在 `shop_faults(example.root)` 里：`menu suggest 2026-W99`。 | 1. 两次 `(1, err [NO_MENU(2026-W46)])`，因为 2026-11-10 在 2026-W46 里。然后 `(0, out SOME(2026-W47, 1, 10, 4, left))`。2. `(0, out SOME(2026-W47, 1, 10, 4, left))`。3. `(1, err [NO_MENU(2027-W01)])`，因为 2026-12-30 的下一周是 2027-W01。然后 `(0, out SOME(2026-W53, 7, 14, 0, left))`。4. 每个 V 给出 `(2, err [NOT_A_WEEK(V)])`，然后是 `(2, err [NOT_A_WEEK_ZH("2026-W99")])` 和 `(2, err [NOT_A_WEEK_ZH("Next")])`。2026-W47 的文件保留 1 里那一行 `menu suggest next` 写出的字节。5. `(2, err [NOT_A_WEEK("2026-W99")])`。记录只有 `read settings.toml`，没有列出，来源没有记录调用。 |
| F14-T11 | 功能 | `recipe-menu menu suggest`、`main` | 标签。`--tag` 用任何一个名称找到标签，与 `Catalog.find_tag` 的匹配相同：两端的空白不算，大小写只对字母 A 到 Z 不算。输出用输出的语言写出标签名。未知标签给出单数或复数形式的 `UNKNOWN_TAG`，或者 `NO_TAGS`，带输入时的值，退出码 1，在目录之后、任何列出之前。没有候选带有的标签不填任何餐。`menu suggest` 仍然读取这一周没有用到的每个菜谱，所以一个不带这个标签的菜谱里的错误也会让它停下（2.2 第 2、3 和 9 步，选择 3、4 和 9）。 | 1. 一个餐次为晚餐的新示例，每一行之前把 `menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：对 `quick`、`QUICK`、`Quick`、`" quick "`、`"\u00a0quick\u3000"`、`"快手 "` 和 `"\t快手"` 里的每个 T 运行 `menu suggest 2026-W48 --tag T`。然后 `menu suggest 2026-W48 --tag 快手 --lang zh` 和 `menu suggest 2026-W48 --tag quick --lang zh`。2. 在 `example` 里：`menu suggest 2026-W47 --tag breakfast`、`menu suggest 2026-W47 --tag breakfast --lang zh`、`menu suggest 2026-W47 --tag " Breakfast "`、`menu suggest 2026-W47 --tag "quick\u200b"` 和 `menu suggest 2026-W47 --tag "home style"`。3. 新示例里的一个标签：`menu suggest 2026-W47 --tag breakfast` 和 `menu suggest 2026-W47 --tag breakfast --lang zh`。4. 新示例里没有标签：`menu suggest 2026-W47 --tag quick` 和 `menu suggest 2026-W47 --tag quick --lang zh`。5. 在 `shop_faults(example.root)` 里：`menu suggest 2026-W47 --tag breakfast`。6. 在 `example` 里：`menu suggest 2026-W47 --tag vegetarian`。7. 新示例里的麻婆的错误，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [lunch, dinner])`：`menu suggest 2026-W48 --tag quick`。 | 1. 每个带 T 的行都给出 `(0, out SOME(2026-W48, 3, 7, 0, left, quick))`，这个文件是 `NEW(2026-W48, [dinner])`，其中前三个 `dinner = []` 换成 `dinner = ["choy-sum"]`、`dinner = ["tomato-egg"]` 和 `dinner = ["tomato-egg-noodles"]`。两行中文都给出 `(0, out SOME_ZH(2026-W48, 3, 7, 0, left, 快手))`。2. `(1, err [TAGS("breakfast")])`、`(1, err [TAGS_ZH("breakfast")])`、`(1, err [TAGS(" Breakfast ")])`、`(1, err [TAGS("quick\u200b")])` 和 `(1, err [TAGS("home style")])`。3. `(1, err [ONE_TAG("breakfast")])` 和 `(1, err [ONE_TAG_ZH("breakfast")])`。4. `(1, err [NO_TAGS("quick")])` 和 `(1, err [NO_TAGS_ZH("quick")])`。5. `(1, err [TAGS("breakfast")])`。记录是 `read settings.toml` 和 `read catalog.toml`，没有列出，来源没有记录调用。6. `(0, out SOME(2026-W47, 0, 10, 4, left, vegetarian))`，来源记录了 `([], 0)`：这一周没有用到的那一个菜谱 `red-braised-pork` 只带标签 家常。7. `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱")))`，尽管 `mapo-tofu` 不带标签 快手。在 2 到 7 里，文件夹里的每个文件都保留它的字节和时间。 |
| F14-T12 | 功能 | `recipe-menu menu suggest`、`main` | 没有菜单文件的星期。读完目录和两次列出之后，`menu suggest` 写出 `NO_MENU`，退出码 1，在读任何菜单或菜谱之前停下。文件名与星期名只有大小写不同的文件不是那一周的菜单，它是列出时的错误（2.2 第 5 步，选择 3，F11 设计 3.1）。 | 1. 在 `example` 里：`menu suggest 2026-W48` 和 `menu suggest 2026-W48 --lang zh`。2. 新示例 F 里的麻婆的错误：在 `shop_faults(F.root)` 里运行 `menu suggest 2026-W48`。3. 新示例里的小写的星期：`menu suggest 2026-W48`，然后 `menu suggest 2026-W47`。 | 1. `(1, err [NO_MENU(2026-W48)])` 和 `(1, err [NO_MENU_ZH(2026-W48)])`，`menus/` 里只有 `2026-W47.toml`。2. `(1, err [NO_MENU(2026-W48)])`。记录是 `read settings.toml` 和 `read catalog.toml`，列出记录是 `recipes` 和 `menus`，来源没有记录调用。3. 两行都是 `(1, err STOP(menus/2026-w48.toml, NOT_A_WEEK_NAME))`：`menus/` 的列出在找这一周之前就让 `menu suggest` 停下。 |
| F14-T13 | 功能 | `recipe-menu menu suggest`、`recipe-menu check`、`main` | 错误让 `menu suggest` 停在第一个错误上，用输出的语言写出 `stop_at_error` 的三行，退出码 1，输出流上什么都没有，不写文件。先是目录，然后是 `recipes/` 的列出、`menus/` 的列出、这一周的菜单，以及这一周没有用到的菜谱，按 ID 顺序。这一周用到的菜谱不读。`check` 用同样的读取器读同样的文件，所以让 `menu suggest` 停下的错误在 `check` 的错误之中（2.2 第 2 步、第 4 到 6 步和第 9 步，选择 3）。 | 每个输入都是一个新示例。W 是 `2026-W48`，在输入做修改之前把 `menus/2026-W48.toml` 写成 `NEW(2026-W48, [lunch, dinner])`，除非输入指定 `2026-W47`。输入 1 到 13 各运行 `menu suggest W`、`menu suggest W --lang zh`、`check` 和 `check --lang zh`。1. 没有目录。2. 目录的花括号。3. 没有 recipes 文件夹。4. recipes 是文件。5. Rice Bowl。6. 大写的 rice。7. 没有 menus 文件夹。8. menus 是文件。9. 菜单的笔误，W 为 `2026-W47`。10. v0.1-S07 的菜单错误，W 为 `2026-W47`。11. 文件夹 x。12. 麻婆的错误。13. 麻婆的错误和 rice 为 0。然后只运行 `menu suggest 2026-W47`：14. rice 为 0。15. 麻婆的错误。 | `menu suggest W` 给出 `(1, err STOP(P, M))`，`menu suggest W --lang zh` 给出 `(1, err STOP_ZH(P, M))`，P 和 M 是：1. `catalog.toml`，`FILE_MISSING`。2. `catalog.toml, line 11`，`MISSING_BRACE`。3. `recipes`，`FOLDER_MISSING`。4. `recipes`，`FOLDER_IS_FILE`。5. `recipes/Rice Bowl.toml`，列出时的 `NOT_A_RECIPE_ID`。6. `recipes/rice.TOML`，`TOML_ENDING_NOT_SMALL`。7. `menus`，`FOLDER_MISSING`。8. `menus`，`FOLDER_IS_FILE`。9. `menus/2026-W47.toml, Monday dinner`，`UNKNOWN_RECIPE(recipe="tomato-eggs")`，也就是 F11 原型“A menu with a mistake”的几行。10. `menus/2026-W47.toml, week`，`WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`。11. `recipes/x.toml`，`FILE_IS_FOLDER`。12 和 13. `recipes/mapo-tofu.toml, ingredient 3`，`UNKNOWN_INGREDIENT(name="豆瓣酱")`，因为 `mapo-tofu` 排在 `rice` 前面。在 1 到 13 里，这个错误在 `check` 和 `check --lang zh` 的错误之中，文件夹里的每个文件都保留它的字节。14 和 15. `(0, out SOME(2026-W47, 1, 10, 4, left))`：`rice` 和 `mapo-tofu` 在这一周里，所以不读它们的文件。 |
| F14-T14 | 功能 | `recipe-menu menu suggest`、`main` | 读取。`menu suggest` 读一次目录，依次各列出一次 `recipes/` 和 `menus/`，读两次这一周的菜单文件，按 ID 顺序把这一周没有用到的每个菜谱读一次，然后通过 `replace_file` 写文件。它不读 `pantry.toml`、别的菜单，也不读这一周用到的菜谱。菜谱的错误让读取停下，第 8 步读取文字时也可能单独失败（2.2 第 2 到 13 步，副作用，选择 3）。 | 每一行都在新示例 F 里、在 `shop_faults(F.root)` 里运行。1. `menu suggest 2026-W47`。2. `menus/2026-W48.toml` 写成 `NEW(2026-W48, [lunch, dinner])`，`menus/2026-W49.toml` 写成 `NEW(2026-W49, [lunch, dinner])`：`menu suggest 2026-W48`。3. 麻婆的错误，`menus/2026-W48.toml` 同 2：`menu suggest 2026-W48`。4. 规则 `read F/menus/2026-W47.toml: later DENIED`：`menu suggest 2026-W47`。 | 1. `(0, out SOME(2026-W47, 1, 10, 4, left))`。记录是 `read settings.toml`、`read catalog.toml`、两次 `read menus/2026-W47.toml`、`read recipes/red-braised-pork.toml`、`unlink menus/2026-W47.toml.tmp`、`open menus/2026-W47.toml.tmp` 和 `move menus/2026-W47.toml.tmp menus/2026-W47.toml`，列出记录依次是 `recipes` 和 `menus`。2. `(0, out SOME(2026-W48, 7, 14, 0, left))`。记录是 `read settings.toml`、`read catalog.toml`、两次 `read menus/2026-W48.toml`、按 ID 顺序读七个菜谱文件，从 `read recipes/choy-sum.toml` 到 `read recipes/tomato-egg-noodles.toml`，以及写 `menus/2026-W48.toml` 的三次调用。3. `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱")))`。记录以 `read recipes/choy-sum.toml`、`read recipes/cola-wings.toml` 和 `read recipes/mapo-tofu.toml` 结尾，没有 `unlink`、`open` 或 `move`。4. `(1, err STOP(menus/2026-W47.toml, ACCESS_DENIED))`。记录是 `read settings.toml`、`read catalog.toml` 和两次 `read menus/2026-W47.toml`，这个文件保留它的字节。 |
| F14-T15 | 功能 | `recipe-menu menu suggest`、`main` | 停下的顺序。第一个发现问题的步骤给出结果：目录先于标签，标签先于列出，`recipes/` 的列出先于 `menus/` 的列出，这一周的菜单先于任何菜谱，第 8 步的拒绝先于任何菜谱，菜谱的错误先于第 12 步对新文字的检查（2.2 第 1 到 12 步，选择 3）。 | 每个输入都是一个新示例。1. 没有目录：`menu suggest 2026-W47 --tag breakfast`。2. 没有 recipes 文件夹：`menu suggest 2026-W47 --tag breakfast`。3. 没有 recipes 文件夹，也没有 menus 文件夹：`menu suggest 2026-W47`。4. 目录的花括号和菜单的笔误：`menu suggest 2026-W47`。5. Rice Bowl 和菜单的笔误：`menu suggest 2026-W47`。6. R1 写成 `menus/2026-W47.toml`，以及 red-braised-pork 为 0：`menu suggest 2026-W47` 和 `menu suggest 2026-W47 --lang zh`。7. R3 和麻婆的错误：`menu suggest 2026-W49`。 | 1. `(1, err STOP(catalog.toml, FILE_MISSING))`。2. `(1, err [TAGS("breakfast")])`。3. `(1, err STOP(recipes, FOLDER_MISSING))`。4. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`。5. `(1, err STOP(recipes/Rice Bowl.toml, NOT_A_RECIPE_ID of a listing))`。6. `(1, err CANNOT(2026-W47))` 和 `(1, err CANNOT_ZH(2026-W47))`，尽管候选 `red-braised-pork` 有错误。7. `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱")))`，尽管 R3 无法填写。在每个输入里，文件夹里的每个文件都保留它的字节。 |
| F14-T16 | 功能 | `recipe-menu menu suggest`、`main` | 文字怎样原地改变。一餐的空行用它的列表代替 `[`、`]` 和它们之间的空格和制表符，保留 `[` 之前和 `]` 之后的文字，包括注释。模式能读出不带引号或带引号的一天和一餐，中间可以有任意多个空格和制表符，也可以没有。文件漏写的一天在末尾得到它的表，没有一餐得到菜的一天不得到表（2.2，“文字怎样改变”，选择 7）。 | 一个新示例，文字 A 写成 `menus/2026-W48.toml`：`menu suggest 2026-W48`。然后 `menu show 2026-W48`。 | `(0, out SOME(2026-W48, 7, 14, 0, left))`，这个文件写着运行之后的文字 A。周四晚餐和周五到周日保持空着，不得到行。`menu show 2026-W48` 给出退出码 0，err 为空。 |
| F14-T17 | 功能 | `recipe-menu menu suggest`、`main` | 新的行和新的表。某天的表里漏写的一餐，在那天的表头之后紧接着得到新的一行；同一天的新行按设置里餐次的顺序紧跟在表头后面，在原有的行之前。文件漏写的一天在文字末尾得到它的表，新的表按一周的顺序排列，文字不以 LF 结尾时先加一个 LF。有不止一道菜的餐按选出的顺序得到各个 ID，每个放在双引号里，用 `, ` 分开（2.2，“文字怎样改变”，选择 7，C 点）。 | 每个输入都是一个新示例。1. 餐次早餐、午餐和晚餐，文字 B 写成 `menus/2026-W48.toml`：`menu suggest 2026-W48`。2. 餐次晚餐，文字 C 写成 `menus/2026-W48.toml`：`menu suggest 2026-W48`。3. 餐次晚餐，文字 D 写成 `menus/2026-W48.toml`：`menu suggest 2026-W48`。在一个副本里，用文字 D′ 做同样的事。4. 餐次晚餐，菜数 `{ dinner = 3 }`，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：`menu suggest 2026-W48`。 | 1. `(0, out SOME(2026-W48, 7, 21, 0, left))`，这个文件写着运行之后的文字 B。2. `(0, out REFILL(2026-W48, 6, 1))`，也就是 `Filled 6 empty meals of 2026-W48. Kept the 1 meal that already has dishes.` 和 `RUN_SHOW` 那一行，这个文件写着运行之后的文字 C。3. `(0, out FIRST(2026-W48, 7))`，对文字 D 和文字 D′，这个文件都写着运行之后的文字 D。4. `(0, out SOME(2026-W48, 2, 7, 0, few))`，这个文件是 `NEW(2026-W48, [dinner])`，其中前两个 `dinner = []` 换成 `dinner = ["choy-sum", "cola-wings", "mapo-tofu"]` 和 `dinner = ["red-braised-pork", "rice", "tomato-egg"]`。 |
| F14-T18 | 功能 | `recipe-menu menu suggest`、`recipe-menu menu show`、`main` | 换行和字节顺序标记。以 CR LF 换行、带字节顺序标记或两者都有的菜单文件，保留每一行的文字，新的文件是 UTF-8、LF 换行、没有标记。别的文件都不变（选择 7，3.5，架构 5.1）。 | 每个输入都是一个新示例。1. BOM 和 CRLF：`menu suggest 2026-W47`，然后 `menu show 2026-W47`。2. `menus/2026-W47.toml` 重写为 `b"\xef\xbb\xbf"` 加上它的字节：`menu suggest 2026-W47`。3. `menus/2026-W47.toml` 重写，每个 `b"\n"` 换成 `b"\r\n"`：`menu suggest 2026-W47`。 | 每次 `menu suggest` 都给出 `(0, out SOME(2026-W47, 1, 10, 4, left))`，这个文件写着示例文件的字节，LF 换行，没有字节顺序标记，其中第一个 `lunch = []` 换成 `lunch = ["red-braised-pork"]`。在 1 里，`menu show 2026-W47` 给出 F14-T07 的输出 L，文件夹里其他每个文件都保留它的字节，包括 CR LF 换行和标记。 |
| F14-T19 | 功能 | `recipe-menu menu suggest`、`main` | `menu suggest` 无法填写的文件。文字里没有位置的空餐让它在第 8 步停下，在读任何菜谱之前。读出来不是旧表加上新菜的新文字让它在第 12 步停下，在读完菜谱之后。两者都给出 `CANNOT_FILL` 的三行，带相对于数据文件夹的文件和 `CHANGED_NOTHING`，退出码 1，不写文件。没有填任何餐的运行到不了第 12 步（2.2 第 8、11 和 12 步，选择 7，A 点）。 | 每个输入都是一个新示例 F。1. R1 写成 `menus/2026-W47.toml`：`menu suggest 2026-W47` 和 `menu suggest 2026-W47 --lang zh`，然后在 `shop_faults(F.root)` 里运行 `menu suggest 2026-W47`。2. R2 写成 `menus/2026-W47.toml`：`menu suggest 2026-W47`。3. R3：`menu suggest 2026-W49`，然后在 `shop_faults(F.root)` 里运行 `menu suggest 2026-W49`。4. R4：`menu suggest 2026-W49`。5. R5：`menu suggest 2026-W49`。6. R6：`menu suggest 2026-W49` 和 `menu suggest 2026-W49 --lang zh`。7. R3 和空的 recipes：`menu suggest 2026-W49`。 | 1. `(1, err CANNOT(2026-W47))` 和 `(1, err CANNOT_ZH(2026-W47))`。记录是 `read settings.toml`、`read catalog.toml` 和两次 `read menus/2026-W47.toml`，没有读任何菜谱，也没有 `unlink`、`open` 或 `move`。2. `(1, err CANNOT(2026-W47))`。3. `(1, err CANNOT(2026-W49))`，记录里有七个菜谱文件的读取，没有 `unlink`、`open` 或 `move`。4 和 5. `(1, err CANNOT(2026-W49))`。6. `(1, err CANNOT(2026-W49))` 和 `(1, err CANNOT_ZH(2026-W49))`。7. `(0, out SOME(2026-W49, 0, 14, 0, left))`。在每个输入里，这个文件都保留它的字节和时间，`menus/` 里没有 `.tmp` 文件。 |
| F14-T20 | 功能 | `recipe-menu menu suggest`、`main` | 保存失败。`replace_file` 给出 `FAILED`，`menu suggest` 向错误流写三行，退出码 1，输出流上什么都不写：问题里写着的、相对于数据文件夹的文件，然后两个空格加问题在输出语言里的文字，然后是 `CHANGED_NOTHING`，或者 `replace_file` 没能删掉临时文件时带临时文件完整路径的 `LEFT_BEHIND`。菜单文件保留它的字节。在读取或移动时按 Ctrl+C，留下旧文件，不留临时文件。下一次没有故障的运行填好这一周（2.2 第 13 步，选择 8，A 点和 D 点）。 | X 是每个输入的数据文件夹，一个新示例，P 是 `X/menus/2026-W47.toml`，T 是 `X/menus/2026-W47.toml.tmp`。N 是示例文件的字节，其中第一个 `lunch = []` 换成 `lunch = ["red-braised-pork"]`。每个输入的第一行在 `shop_faults(X, *rules)` 里运行。1. `open T: DENIED`：`menu suggest 2026-W47`，然后 `menu suggest 2026-W47 --lang zh`。2. `open T: IO`：`menu suggest 2026-W47`。3. `write T: NO_SPACE`：`menu suggest 2026-W47`。4. X 在 `tmp_path / "One Drive" / "菜谱"`，带 `write T: NO_SPACE` 和 `unlink T: later DENIED`：`menu suggest next`。然后不带规则运行 `menu suggest 2026-W47`。5. 同 4，但这一行是 `menu suggest 2026-W47 --lang zh`，之后没有别的行。6. `close T: IO`：`menu suggest 2026-W47`。7. `move T: DENIED`：`menu suggest 2026-W47`。8. `move T: CTRL_C`：`menu suggest 2026-W47`。9. `read X/recipes/red-braised-pork.toml: CTRL_C`：`menu suggest 2026-W47`。10. 不用工具，`tests/f13_support.py` 的 `held_open` 打开着 P 时：`menu suggest 2026-W47`。11. 不用工具，`menus/2026-W47.toml.tmp` 写成 `b"half\n"`：`menu suggest 2026-W47`。 | 1. `(1, err FAIL(2026-W47, FILE_WRITE_DENIED))` 和 `(1, err FAIL_ZH(2026-W47, FILE_WRITE_DENIED))`。2. `(1, err FAIL(2026-W47, FILE_WRITE_ERROR(reason="Input/output error")))`。3. `(1, err FAIL(2026-W47, FILE_WRITE_ERROR(reason="No space left on device")))`，记录以 `unlink menus/2026-W47.toml.tmp`、`open menus/2026-W47.toml.tmp` 和 `unlink menus/2026-W47.toml.tmp` 结尾。4. `(1, err LEFT(2026-W47, FILE_WRITE_ERROR(reason="No space left on device"), T))`，T 里是工具写下的 `tests/f11_support.py` 的 `first_half(N)`，因为 N 是 ASCII。然后 `(0, out SOME(2026-W47, 1, 10, 4, left))`：`replace_file` 的第 3 步删掉了 T，这个文件写着 N，`menus/` 里只有 `2026-W47.toml`。5. `(1, err LEFT_ZH(2026-W47, FILE_WRITE_ERROR(reason="No space left on device"), T))`。6. `(1, err FAIL(2026-W47, FILE_WRITE_ERROR(reason="Input/output error")))`。7. `(1, err FAIL(2026-W47, FILE_WRITE_DENIED))`，记录以 `move menus/2026-W47.toml.tmp menus/2026-W47.toml` 和 `unlink menus/2026-W47.toml.tmp` 结尾。8 和 9. 通过 `call_main` 得到 `(130, "", "")`，没有 T。10. 在 Windows 上，`(1, err FAIL(2026-W47, FILE_WRITE_DENIED))`，没有 T。在 Linux 上，`(0, out SOME(2026-W47, 1, 10, 4, left))`，这个文件写着 N。11. `(0, out SOME(2026-W47, 1, 10, 4, left))`，这个文件写着 N，`menus/` 里只有 `2026-W47.toml`。在 1 到 9 里，以及 Windows 上的 10 里，这个文件保留示例的字节；除 4 和 5 之外的每个输入，这一行之后 `menus/` 里都没有 `.tmp` 文件。 |
| F14-T21 | 功能 | `recipe-menu menu suggest`、`recipe-menu menu`、`main` | `cli` 在运行 `menu suggest` 之前报告命令行上的错误、不存在的数据文件夹和损坏的设置，用 F05 的消息和退出码：两个星期、未知选项、`--tag` 没有值或写了两次、只写 `menu` 时列出三个菜单命令，以及错误的 `dishes` 值。`--help` 显示帮助，不运行任何东西。之后同一个文件夹给出 `menu suggest` 的输出（2.2 的错误，选择 1，3.2，F05 设计 2.10）。 | 1. 在 `example` 里：`menu suggest 2026-W47 2026-W48`、`menu suggest 2026-W47 2026-W48 --lang zh`、`menu suggest --tags quick`、`menu suggest --tags quick --lang zh`、`menu suggest --tag`、`menu suggest --tag ""`、`menu suggest --tag --lang zh`、`menu suggest --tag a --tag b` 和 `menu suggest --tag a --tag b --lang zh`。2. 在 `example` 里：`menu`、`menu --lang zh` 和 `menu suggestion`。3. 在 `example` 里：`menu suggest next --help` 和 `menu suggest 2026-W99 --help --lang zh`。4. M 是 `tmp_path / "missing"`：在 M 里运行 `menu suggest`，在 M 里运行 `menu suggest next --lang zh`。然后不带文件夹运行 `menu suggest 2026-W48`。5. 新示例里的损坏的设置：`menu suggest 2026-W47`。6. 新示例里的菜数 `{ dinner = 0 }`：`menu suggest 2026-W47` 和 `menu suggest 2026-W47 --lang zh`。7. 在 `example` 里：`menu suggest 2026-W47`。 | 1. `(2, err ['Unexpected argument "2026-W48". Write "recipe-menu menu suggest [WEEK]".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["多余的参数“2026-W48”。请写成“recipe-menu menu suggest [周]”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['"menu suggest" has no option "--tags". Its own option is "--tag".', 'Run "recipe-menu --help" to see the options.'])`、`(2, err ["“menu suggest”没有选项“--tags”。它自己的选项是“--tag”。", "运行“recipe-menu --help”查看选项。"])`、两次 `(2, err ["--tag needs a value."])`、`(2, err ["--tag 后面要写一个值。"])`、`(2, err ["--tag is given twice."])` 和 `(2, err ["--tag 写了两次。"])`。2. `(2, err ['The commands that start with "menu" are "menu new", "menu show", and "menu suggest".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["以“menu”开头的命令有“menu new”、“menu show”和“menu suggest”。", "运行“recipe-menu --help”查看命令。"])` 和 `(2, err ['Unknown command "menu suggestion".', 'Run "recipe-menu --help" to see the commands.'])`。3. 每个都给出退出码 0，err 为空，out 上的文字与不带文件夹的 `--help` 相同，第二行则与 `--help --lang zh` 相同。4. `tests/f05_texts.py` 的 `no_data_folder(M)` 和 `no_data_folder(M, ZH)`，M 仍然不存在。然后是 `no_data_folder(home/recipe-menu)`，也就是 F05 原型“No data folder yet”对这个文件夹的第一个输出，正如 v0.2-S14 第 4 步所预期的。5. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`。6. `(1, err STOP(settings.toml, dishes of dinner, DISHES_NOT_1_TO_10))` 和 `(1, err STOP_ZH(settings.toml, dishes of dinner, DISHES_NOT_1_TO_10))`。7. `(0, out SOME(2026-W47, 1, 10, 4, left))`。在 7 之前，`example` 的 `menus/2026-W47.toml` 写着示例的字节，`menus/` 里没有别的东西。 |
| F14-T22 | 单元 | `Settings`、`Settings.dishes_for` | 3.1 的示例。`Settings` 得到字段 `dishes`，在字段顺序里排第四，默认是 `(1, 1, 1)`；`dishes_for` 按 `Meal` 的顺序给出某一餐的数，对 `meals` 没有指定的餐也一样。两个设置的四个字段都相等时，它们相等，散列值也相同。`dishes` 必须是三个 1 到 10 的 `int` 组成的元组，其中没有 `bool`（3.1）。 | 示例的各行。然后：1. `Settings(dishes=(3, 5, 7))`。2. `Settings(Lang.EN, (Meal.LUNCH,), 2, (4, 1, 1))`。3. `Settings(dishes=(1, 1, 10))` 和 `Settings(dishes=(10, 10, 10))`。4. `Settings()`、`Settings(dishes=(1, 1, 1))` 和 `Settings(dishes=(1, 1, 2))`。5. 对 `(0, 1, 1)`、`(1, 1, 1, 1)`、`()` 和 `(1, -1, 1)` 里的每个 D 调用 `Settings(dishes=D)`。6. 对 `None`、`(1, "2", 1)`、`(1, 1, None)` 和 `(False, 1, 1)` 里的每个 D 调用 `Settings(dishes=D)`。 | 示例的每个断言都成立，每行 `# raises` 都抛出它的错误。1. `dishes_for` 对 `Meal.BREAKFAST`、`Meal.LUNCH` 和 `Meal.DINNER` 给出 3、5 和 7。2. `dishes_for(Meal.BREAKFAST)` 是 4，`dishes_for(Meal.LUNCH)` 是 1。3. 每个都能构造出来，它的 `dishes` 就是给出的元组。4. 前两个相等，散列值相同，三个组成的集合有两项，第三个与第一个不同。5. 每个都抛出 `ValueError`。6. 每个都抛出 `TypeError`。 |
| F14-T23 | 单元 | `read_settings` | 3.2 的示例。可选的键 `dishes` 是一张表，写在花括号里，或者写成 `[dishes]` 和 `dinner = 2` 这样的几行，给每顿需要的餐写一个 1 到 10 的整数。它没有写到的餐得到 1，`meals` 没有指定的餐也可以有一个数。它的问题排在 `servings` 的问题之后、未知键之前，按文件里的顺序：值不是表时，在 `dishes` 处只有 `DISHES_NOT_A_TABLE`；键不是餐次时，在 `dishes` 处是设置的 `UNKNOWN_MEAL`，这个键不再继续检查；在这一餐的数处是 `DISHES_NOT_1_TO_10`。没有消息显示这个数。`UNKNOWN_KEY` 列出的键里 `dishes` 排在 `servings` 之后（3.2，选择 5 和 10，B 点）。 | 示例的各行，`folder` 为 `example`。然后，带 fixture `default_int_limit`，fixture `folder` 的 `folder.settings` 依次写成：1. `dishes = {}`。2. `dishes = { breakfast = 10, lunch = 1 }`。3. `meals = ["lunch"]` 和 `dishes = { breakfast = 3 }` 两行。4. 对 `0x2`、`+3` 和 `1_0` 里的每个 V 写 `dishes = { dinner = V }`。5. 对 `0`、`11`、`-1`、`2.5`、`2.0`、`"2"`、`true`、`[2]`、`{ n = 2 }`、`2026-11-12`、`inf`、`nan`，以及 `0x` 后面跟 5,000 个 `f` 里的每个 V 写 `dishes = { dinner = V }`。6. 对 `2`、`[]`、`"dinner"`、`[{ dinner = 2 }]` 和 `true` 里的每个 V 写 `dishes = V`。7. `dishes = { supper = 2 }`、`dishes = { Dinner = 2 }` 和 `dishes = { supper = 0 }`。8. `[dishes]`、`lunch = 0` 和 `breakfast = "x"` 几行。9. `colour = 1`、`dishes = { dinner = 11 }`、`servings = 0`、`meals = 3` 和 `language = "fr"` 几行，按这个顺序。 | 示例的每个断言都成立，只是它的 `UNKNOWN_KEY` 文字按 F05-T10 的方法检查：这列键以 `language`、`meals`、`servings` 和 `dishes` 开头，按这个顺序，这样 F16 加上它的键时这个用例仍然成立。1. `(Settings(), ())`。2. `(Settings(dishes=(10, 1, 1)), ())`。3. `(Settings(None, (Meal.LUNCH,), 2, (3, 1, 1)), ())`。4. `(Settings(dishes=(1, 1, N)), ())`，N 为 2、3 和 10。5. 每个都不给出设置，只有一个问题 `dishes of dinner`：`DISHES_NOT_1_TO_10`。6. 每个都不给出设置，只有一个问题 `dishes`：`DISHES_NOT_A_TABLE`。7. 每个都不给出设置，只有一个问题 `dishes`：`UNKNOWN_MEAL(meal="supper")`、`UNKNOWN_MEAL(meal="Dinner")` 和 `UNKNOWN_MEAL(meal="supper")`。8. 不给出设置，`dishes of lunch`：`DISHES_NOT_1_TO_10`，然后是 `dishes of breakfast`：`DISHES_NOT_1_TO_10`，按文件里的顺序。9. 不给出设置，依次是 `language`：`LANGUAGE_NOT_EN_OR_ZH(language="fr")`，`meals`：`NOT_A_LIST(key="meals")`，`servings`：`SERVINGS_TOO_FEW(servings=0)`，`dishes of dinner`：`DISHES_NOT_1_TO_10`，以及没有位置的 `UNKNOWN_KEY(key="colour")`。每个问题都是文件为 `settings.toml` 的错误，测试比较它的位置和两种文字。 |
| F14-T24 | 功能 | `recipe-menu check`、`recipe-menu list`、`recipe-menu menu show`、`recipe-menu shop`、`recipe-menu menu new`、`recipe-menu menu suggest`、`main` | 每个命令都读取带 `dishes` 的设置。正确的值不改变 v0.1 命令的任何输出；错误的值是设置的错误，`check` 把它和其他问题一起报告，它让其他每个命令停下（3.2，选择 5，F05 设计 2.10）。 | 1. 新示例 F 里的菜数 `{ dinner = 2 }`：`check`、`list`、`menu show 2026-W47` 和 `shop 2026-W47`。2. 新示例 G 里的菜数 `{ dinner = 0 }`：`check`、`check --lang zh`、`list`、`menu new 2026-W48`、`menu suggest 2026-W47` 和 `menu suggest 2026-W47 --lang zh`。3. 新示例里的菜数 `[]`：`check`。 | 1. `tests/f07_support.py` 的 `(0, out AFTER)`、`tests/f09_texts.py` 的 `(0, out LIST)`、`(0, out SHOW_47)`，以及 F13 测试方案的 `(0, out SHOP_47(F/shopping/2026-W47.md))`。2. `tests/f07_support.py` 的 `rep(1, 7, 1, E, W)`，英文和中文，其中 E 是问题 `settings.toml`、`dishes of dinner`、`DISHES_NOT_1_TO_10`，W 是 `AFTER` 里 `red-braised-pork` 的警告。然后 `list`、`menu new` 和 `menu suggest` 给出 `(1, err STOP(settings.toml, dishes of dinner, DISHES_NOT_1_TO_10))`，最后一行给出同样内容的 `STOP_ZH`。G 没有 `menus/2026-W48.toml`，它的 `menus/2026-W47.toml` 保留它的字节。3. `rep(1, 7, 1, E, W)`，其中 E 是问题 `settings.toml`、`dishes`、`DISHES_NOT_A_TABLE`。 |
| F14-T25 | 单元 | `Context`、`main` | 3.3 和 3.4 的示例。`Context` 得到字段 `random`，在字段顺序里排第七，不带生成器构造的每个 context 都得到一个新的 `Random(0)`。两个 context 的七个字段都相等时它们相等，流和生成器按对象比较，`Context` 可以求散列值。`main` 把它得到的生成器放在 `Context.random` 里传给命令；没有得到生成器时，它每次调用都新建一个 `Random()`（3.3，3.4）。 | 3.3 的示例。3.4 的示例，`folder` 为 `example`，`home` 为 `home`。然后：1. 3.3 示例的 `hash(context)`。2. 在 3.4 的示例之后再调用一次 `pick(None)`。 | 两个示例的每个断言都成立。1. 这次调用给出一个 `int`。2. 0。`seen[2]` 是一个 `Random`，既不是 `seeded` 也不是 `seen[1]`，并且 `seen[1].getstate() != seen[2].getstate()`。 |
| F14-T26 | 单元 | `read_file_text` | 3.5 的示例。`read_file_text` 给出一个数据文件的文字，按带或不带字节顺序标记的 UTF-8 解码，换行保持原样，不做解析。或者它给出一个 `Problem`，带 `Severity.ERROR`、相对于数据文件夹的文件，以及 `read_toml` 的消息和位置。数据文件夹之外的路径在任何读取之前抛出 `ValueError`（3.5）。 | 示例的各行，`folder` 为 `example`。然后，F 是一个新示例：1. `menus/2026-W49.toml` 依次写成 `b""`、`b"\xef\xbb\xbf"`、`b"a\r\nb\rc\n"` 和 `b'dinner = ["rice"\n'`，每次之后调用 `read_file_text(F, F.menu_file("2026-W49"))`。2. `menus/2026-W49.toml` 写成 `b"week = 1\nx = 2\n\xe4\xb8\n"`，然后写成 `b"\xff\xfew\x00"`，每次之后做同样的调用。3. 把 `menus/2026-W49.toml` 建成一个文件夹，做同样的调用。4. 在 `shop_faults(F.root, read F/menus/2026-W47.toml: DENIED)` 里调用 `read_file_text(F, F.menu_file("2026-W47"))`，然后用 `IO` 代替 `DENIED` 再做一次。5. `F.root.parent / "elsewhere.toml"` 写成 `b"x\n"`，在 `shop_faults(F.root.parent)` 里调用 `read_file_text(F, F.root.parent / "elsewhere.toml")`。 | 示例的每个断言都成立，它的 `# raises` 那一行抛出 `ValueError`。1. `""`、`""`、`"a\r\nb\rc\n"` 和 `'dinner = ["rice"\n'`。2. 位置为 `line 3` 的 `Problem`，然后是位置为 `line 1` 的 `Problem`，都是 `NOT_UTF8`。3. 没有位置、带 `FILE_IS_FOLDER` 的 `Problem`。4. 没有位置、带 `ACCESS_DENIED` 的 `Problem`，然后是没有位置、带 `SYSTEM_ERROR(reason="Input/output error")` 的 `Problem`。5. `ValueError`，记录里没有读取。每个 `Problem` 都是一个错误，文件为 `menus/2026-W49.toml` 或 `menus/2026-W47.toml`，测试按 `str` 比较，并比较它的两种文字。 |
| F14-T27 | 单元 | `parse_toml` | 3.6 的示例。`parse_toml` 给出一段 TOML 文字的表；对 `tomllib` 拒绝的文字、位数太多的数或嵌套太深的文字，给出 `None`。对 `str` 它从不抛出（3.6）。 | 示例的各行，带 fixture `default_int_limit`。然后对下面的文字调用 `parse_toml`：1. `"a = 1\r\n"`。2. `"[monday]\ndinner = [\n]\n"`。3. `"\x00"`、`"\ufeffa = 1\n"`、`"a = 1\rb = 2\n"`，以及 R3 的文字后面跟 `"\n[monday]\nlunch = [\"rice\"]\n"`。 | 示例的每个断言都成立。1. `{"a": 1}`。2. `{"monday": {"dinner": []}}`。3. 每个都是 `None`。 |
| F14-T28 | 集成 | `recipe-menu menu suggest`、`recipe-menu menu new`、`recipe-menu menu show`、`recipe-menu check`、`recipe-menu shop`、`main` | `main` 上的 v0.2-S06。有早餐、午餐和晚餐，以及一行 `dishes = { dinner = 2 }` 时，第一次填满在每顿早餐和每顿午餐放 1 道菜，每顿晚餐放 2 道菜，共 28 个不同的菜谱。这一周能读回来，`check` 不报告错误，`shop` 生成它的清单（选择 5 和 6，B 点）。 | R 处的推荐文件夹，把 `settings.toml` 里的 `meals = ["lunch", "dinner"]` 换成 `meals = ["breakfast", "lunch", "dinner"]`，并加上菜数 `{ dinner = 2 }`。1. `menu new 2026-W48`。2. 用 `Random(11)` 运行 `menu suggest 2026-W48`。3. `menu show 2026-W48`。4. `check`。5. `shop 2026-W48`。 | 1. 退出码 0，这个文件是 `NEW(2026-W48, [breakfast, lunch, dinner])`。2. `(0, out FIRST(2026-W48, 21))`。选出的菜谱是 `Random(11)` 从按 ID 顺序排列的 40 个 ID 里以数 28 选出的。这个文件是 `NEW(2026-W48, [breakfast, lunch, dinner])`，其中 21 个 `[]` 依次换掉：每顿早餐和每顿午餐换成 `["p"]`，p 是下一个选出的菜谱；每顿晚餐换成 `["p", "q"]`，用接下来的两个。3. 退出码 0，err 为空。out 的前几行是 `Menu for 2026-W48, 23 to 29 November 2026`、一个空行，以及以 `Day` 开头、依次含有 `Breakfast`、`Lunch` 和 `Dinner` 的一行，最后一行是 `21 meals, 28 dishes. ×n: servings.`。4. `(0, out A)`，其中 A 是 `AFTER`，用 `40 recipes, and 2 week menus` 代替 `7 recipes, and 1 week menu`。5. 退出码 0，err 为空。out 的第一行是 `Shopping list for 2026-W48, 23 to 29 November 2026: 21 meals, 28 dishes`，最后一行是 `Saved R/shopping/2026-W48.md`，这个文件存在。 |
| F14-T29 | 集成 | `recipe-menu menu suggest`、`recipe-menu menu new`、`main` | `main` 上的 v0.2-S07。`this` 和 `next` 跟随 `main` 得到的今天的日期。有 7 个菜谱时，第一次填一个有 14 餐的新星期，填满前 7 餐，也就是周一午餐到周四午餐，每个菜谱各一餐，说明 7 餐仍是空的，退出码 0（选择 2、6 和 9）。 | 一个 menus 为空的示例，在 2026-12-30 这天：1. `menu new next`。2. `menu suggest next`。3. `menu suggest`。 | 1. 退出码 0，`menus/2027-W01.toml` 是 `NEW(2027-W01, [lunch, dinner])`。2. `(0, out SOME(2027-W01, 7, 14, 0, left))`。这个文件是 `NEW(2027-W01, [lunch, dinner])`，其中前七个 `[]` 依次换成 `["choy-sum"]`、`["cola-wings"]`、`["mapo-tofu"]`、`["red-braised-pork"]`、`["rice"]`、`["tomato-egg"]` 和 `["tomato-egg-noodles"]`。3. `(1, err [NO_MENU(2026-W53)])`。之后 `menus/` 里只有 `2027-W01.toml`。 |
| F14-T30 | 集成 | `recipe-menu menu suggest`、`main` | `main` 上的 v0.2-S08。错误的星期、缺少的菜单、未知的标签和这一周里的错误让 `menu suggest` 停下，用 `menu show` 和 `list --tag` 的消息。除了用例自己做的修改，没有哪一行添加或修改文件（选择 2 到 4，架构 6）。 | `home / "recipe-menu"` 处的一个新示例，带空的 `shopping/`，以及空的当前文件夹 `tmp_path / "cwd"`，用 `monkeypatch.chdir` 进入。每一行之前用 `tests/f07_support.py` 的 `snapshot` 给 `home` 和当前文件夹拍快照。不带文件夹：1. `menu suggest 2026-W99`。2. `menu suggest 2026-W48`。3. `menu suggest 2026-W47 --tag breakfast`。4. 菜单的笔误，然后 `menu suggest 2026-W47`。 | 1. `(2, err [NOT_A_WEEK("2026-W99")])`，也就是 F11 原型“A week without a menu”的第二个输出。2. `(1, err [NO_MENU(2026-W48)])`，它的第一个输出。3. `(1, err [TAGS("breakfast")])`，也就是 F09 原型“List the recipes with one tag”的第三个输出。4. `(1, err STOP(menus/2026-W47.toml, Monday dinner, UNKNOWN_RECIPE(recipe="tomato-eggs")))`，也就是 F11 原型“A menu with a mistake”的输出。每一行之后，两个快照都等于这一行之前的快照，第 4 行之前的快照在笔误之后拍。 |
| F14-T31 | 集成 | `recipe-menu menu suggest`、`main` | `main` 上的 v0.2-S15 第 1 步。一次填写只改变这一周的菜单文件，`menus/` 里没有别的新东西，比如 `2026-W48.toml.tmp`。`replace_file` 的移动可能让 `menus/` 得到新的修改时间。`home` 下和当前文件夹下其他每个文件和文件夹都保留它的字节和时间。什么都不写的那几行什么都不改变（2.2 副作用，选择 8）。 | `home / "recipe-menu"` 处的一个新示例，带空的 `shopping/`，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [lunch, dinner])`，以及空的当前文件夹 `tmp_path / "cwd"`，用 `monkeypatch.chdir` 进入。每一行之前给 `home` 和当前文件夹拍快照。不带文件夹：1. `menu suggest 2026-W48`。2. `menu suggest 2026-W48`、`menu suggest --help`、`menu suggest 2026-W99` 和 `menu suggest 2026-W48 --tag x`。 | 1. `(0, out SOME(2026-W48, 7, 14, 0, left))`。`home` 的快照等于这一行之前的快照，只有 `recipe-menu/menus` 的时间可能改变，`recipe-menu/menus/2026-W48.toml` 写着填好的文字。`recipe-menu/menus` 里只有 `2026-W47.toml` 和 `2026-W48.toml`，当前文件夹的快照不变。2. `(0, out SOME(2026-W48, 0, 7, 7, left))`、带 `--help` 文字的退出码 0、`(2, err [NOT_A_WEEK("2026-W99")])` 和 `(1, err [TAGS("x")])`。每一行之后，两个快照都等于这一行之前的快照。 |
| F14-T32 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令和一个从系统取种子的生成器运行 `menu suggest`。不管 Python 给流设了什么编码，它都把输出按 UTF-8 写到 stdout，把退出码 1 或 2 的消息写到 stderr（2.2，3.4，F05 设计 2.9）。 | `tests/f05_support.py` 的 `run_module`，与 F13-T28 相同，它把 `PYTHONIOENCODING` 设为 `ascii`。1. `menu suggest 2026-W47 --lang zh --data <example>`。2. `menu suggest 2026-W47 --data <example>`。3. `menu suggest 2026-W99 --lang zh --data <example>`。4. `menu suggest 2026-W48 --data <example>`。5. 新示例 F，餐次晚餐，`menus/2026-W48.toml` 写成 `NEW(2026-W48, [dinner])`：`menu suggest 2026-W48 --data <F>`。 | 1. `(0, out SOME_ZH(2026-W47, 1, 10, 4, left))`，这个文件与 F14-T07 输入 1 的文件相同。2. `(0, out SOME(2026-W47, 0, 9, 5, left))`。3. `(2, err [NOT_A_WEEK_ZH("2026-W99")])`。4. `(1, err [NO_MENU(2026-W48)])`。5. `(0, out FIRST(2026-W48, 7))`。七顿晚餐每顿有一道菜，这七道菜是 F 的七个菜谱，各一次，顺序是生成器选的任意顺序。 |
| F14-T33 | 集成 | `recipe-menu menu suggest`、`main` | 随机的星期，以及对任何来源都成立的性质。对任何餐次和菜数的设置、2.2 的规则接受的任何写法、任何已填的餐和空餐、任何标签或不带标签，以及任何来源，一次填写都保留每个保留的餐和它不改变的每一行。它在它填的每餐放上这一餐的菜数，从这一周没有用到的菜谱里各取一次新菜谱，给出 `--tag` 时都带这个标签。它填的餐遵守 C 点，输出是输出的表按这次的数给出的几行。用 `Random(s)` 时，新菜谱就是 `Random(s)` 选出的菜谱。随机组合能达到别的用例没有列出的数和写法（2.2，选择 5 到 9，C 点）。 | `random.Random(20261117)` 构造 100 个文件夹，每个是一个新示例，每四个里有一个是推荐文件夹。下面每个选择都由构造器做出。设置：按顺序的 1 到 3 个 `Meal` 餐次，以及不带 `dishes`，或者在花括号里给部分餐次写 1 到 3 的数的 `dishes`。星期 `2026-W48`：每一天要么没有表，要么有它的表头，带或不带引号；对设置里的每个餐次，要么没有行，要么是文字 A 的某种写法的一餐的空行，要么是文件夹里 1 到 3 个菜谱 ID 的列表，可以重复；其中夹着注释行、空行和行尾注释。`menu suggest 2026-W48` 这一行，不带 `--tag`，或者用目录里某个标签的某个名称，在同一个文件上运行两次：一次用构造器给的种子 s 的 `Random(s)`，一次用后取来源。 | 每次运行都给出退出码 0，err 为空。用这次运行的 C、k 和空餐：1. 运行之后文件的 `read_week_menu` 没有问题，每个保留的餐都有它原来的菜。2. 每个空餐要么没有菜，要么正好有它那一餐的 `dishes_for` 道菜，每道菜的份数都是设置的份数。带着 k 个选出的菜谱依次走过各个空餐，一顿餐恰好在它的数不超过剩下的选出的菜谱时有菜，并从最前面取。3. 新的 ID 各不相同，没有一个在旧的一周里，每个都在 C 里，带 `--tag` 时每个菜谱都有这个标签。4. 用 `Random(s)` 时，按各餐顺序的新 ID 是 `Random(s).sample(C, k)` 的前几项；用后取来源时，是倒过来的 C 的前几项。5. out 是输出的表按这次运行的数给出的几行，由 `tests/f14_texts.py` 的构造函数给出。6. 没有一餐得到菜时，这个文件保留它的字节和时间。否则，新文件去掉 2.2 的规则加上的行之后的各行，就是旧文件的各行，其中每顿得到菜的餐的 `[ ]` 换成了它的列表。 |
| F14-T34 | 集成 | `recipe-menu menu suggest`、`recipe-menu check`、`main` | `main` 上的 v0.2-S16 第 1 步，以及需求 7 的规模：有 1,000 个菜谱时，`menu suggest` 读取每个菜谱，用 21 个不同的菜谱填满新的一周的 21 餐。没有性能指标提到它，所以这个用例不计时（第 3 节）。 | 用 `tests/pt01_support.py` 的 `make_pt01` 在 `tmp_path / "pt01"` 做出的 PT01 数据文件夹，`menus/2026-W53.toml` 写成 `NEW(2026-W53, [breakfast, lunch, dinner])`。1. 用 `Random(53)` 运行 `menu suggest 2026-W53`。2. `check`。 | 1. `(0, out FIRST(2026-W53, 21))`，这个文件是 `NEW(2026-W53, [breakfast, lunch, dinner])`，其中 21 个 `[]` 依次换成 `["p"]`，p 是 `Random(53)` 从按 ID 顺序排列的 1,000 个 ID 里以数 21 选出的每个菜谱。2. `(0, out L)`，其中 L 是 `tests/pt01_support.py` 的 `PT01_LINES`，用 `53 week menus` 代替 `52 week menus`。 |

## 3. 性能用例

无。F14 的接口都没有性能指标。PT01 提到的是 `check`、`list`、`show`、`search`、`menu show` 和 `shop`，没有 `menu suggest`（需求 7.1，设计第 2 节）。所以 `menu suggest` 没有计时的用例（R14）。F14-T34 在 PT01 数据文件夹上运行它而不计时，就像 v0.2-S16 那样。F07、F09、F10、F11 和 F13 的 PT01 用例仍在每个 PR 里运行。它们给各自命令的启动计时，而从 F14 实现起，启动时会导入 `random` 并新建一个 `Random()`（设计选择 11）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| `menu suggest` 要多长时间。 | 没有性能指标提到它（R14）。设计估计大约与 `list` 相当，在 v0.1.0 的发布测试里 `list` 在 Troy 的电脑上用了 0.782 秒，这是估计，不是测量（选择 11）。F14-T34 在 PT01 数据文件夹上运行它而不计时。 |
| 某一天的表头是文字的最后一行、后面没有 LF 时，新的一餐那一行的行尾。 | 设计 2.2 没有说这新的一行是否以 LF 结尾。两种文字读出来是同一张表，所以对新文字的检查都能通过。没有用例写这样的文件。 |
| 两端有空白的 `dishes` 的键，比如 `" dinner " = 2`。 | 设计 3.2 没有说两端的空白算不算，而 F05 设计 2.3 对 `meals` 的各项说了。没有用例写这样的键。 |
| `main` 没有得到生成器时 `Random()` 选出哪些菜谱。 | 它从系统取种子，所以没有一次运行能预期它选出的菜谱。F14-T25 检查每次调用都得到一个新的生成器，F14-T32 只检查每种选法都必须满足的条件。 |
| `random.Random` 对某个种子给出的序列。 | 用例在运行它们的 Python 里用 `Random(n).sample` 算出 `Random(n)` 选出的菜谱，正如选择 6 所说，所以它们对任何 Python 版本都成立。没有用例把某个种子选出的菜谱写成字面量。 |
| `menu suggest` 遇不到的 `replace_file` 的情况，比如写文件时 `menus` 文件夹不存在。 | `menu suggest` 只在 `list_menu_weeks` 列出 `menus/` 之后才写（选择 8）。F13-T03 到 F13-T10 测试 `replace_file` 本身。 |
| `root/menus/../../x.toml` 这样的路径。 | `menu suggest` 只用 `menu_file`、从 `list_menu_weeks` 给出的星期构造它的路径（选择 8）。 |
| 架构 6 里关于换菜那一行的句子（D 点）。 | 架构师在 mock PR 之前的一个 `[docs]` PR 里记录它。用例按设计的文字写，在换菜那一行和保存失败的第一行里用相对于数据文件夹的路径写出文件。 |
| mock PR 之后真实运行里 F05 原型的两份帮助。 | 从 mock 起，真正的帮助有 `menu suggest` 那一行。产品经理在 F14 验收时决定真实运行怎样处理这两节（设计第 3 节）。 |
| 从控制台真正按下的 Ctrl+C，以及在每一步按 Ctrl+C。 | 没有 CI 机器有控制台。F14-T20 在一次读取和移动时抛出 `KeyboardInterrupt`，F13 的用例在 `replace_file` 的每一步抛出它。 |
| Windows Terminal 里的中文输出，以及发布测试里的 v0.2-S01 到 v0.2-S08、v0.2-S14 到 v0.2-S16。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 添加（TE5）。F14-T04 到 F14-T07、F14-T10、F14-T21、F14-T28 到 F14-T31 和 F14-T34 在 `main` 上运行它们的步骤。没有 CI 机器有 Windows 控制台（架构 10）。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的中文字符。 |
| 之后功能的计划：F15 在 `Context` 和 `main` 里的输入流，以及 F16 的键 `editor`。 | 之后每个功能的设计和测试方案会覆盖它们。 |

## 5. 与接口设计师的对齐记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-17 | 初稿。 |
| 1.0 | 2026-11-17 | Troy 批准。 |
