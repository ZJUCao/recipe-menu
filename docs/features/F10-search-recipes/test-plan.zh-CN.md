---
troy-doc: "F10-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-14"
status: "Troy 已于 2026-11-14 批准"
mirror-of: "test-plan.md"
---

# F10 搜索菜谱：测试方案

## 1. 功能

- 编号和名称：F10 搜索菜谱
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.0

## 2. 用例

测试调用 `recipe_menu.commands.search` 的 `SEARCH_COMMAND`、`recipe_menu.catalog` 的 `matching_form`、`recipe_menu.cli` 的 `main`，以及 `python -m recipe_menu`。单元用例用它自己构造的 `Context` 调用 `SEARCH_COMMAND.run`。功能用例像你输入 `recipe-menu search` 那样，用一行命令运行 `main`。它不传 `commands`，所以 `main` 使用真正的 `COMMANDS`，从 mock PR 起 `COMMANDS` 里是 `INIT_COMMAND`、`CHECK_COMMAND`、`LIST_COMMAND`、`SHOW_COMMAND` 和 `SEARCH_COMMAND`（设计选择 1）。集成用例在 `main` 上运行 v0.1 场景，先运行 `show` 再运行 `search`，启动 `python -m recipe_menu`，或者构造随机文件夹。性能用例为 `python -m recipe_menu search` 计时（第 3 节）。每个用例在括号里注明它来自设计的哪一节，比如（2.2）。设计的三个示例和 2.1 的那一行 `# raises` 分别在 F10-T01（2.1）、F10-T03（2.2）和 F10-T07（3.1）里。

**A 点和 B 点。** Troy 于 2026-11-13 批准了设计 1.0，两点都按建议：按 2.2 的写法接受新的文字（A），匹配形式为空的词给出 `UsageError(EMPTY_WORD, None)` 和退出码 2（B，方案 1）。用例用两种语言检查 A 点的每一段新文字。两个及以上的词的英文那一行在 F10-T04、F10-T08 和 F10-T10 里，一个词的中文那一行在 F10-T04 里。一个菜谱的那一行在 F10-T10 和 F10-T12 里，三个词的中文那一行在 F10-T03 和 F10-T10 里。位置 `tag` 在 F10-T05 里，位置 `名称` 在 F10-T04 里，`EMPTY_WORD` 在 F10-T02 和 F10-T11 里。

**之前功能的测试。** 设计第 3 节说，`search` 加进 `COMMANDS`、帮助的第二列从 18 列移到 19 列之后，检查真正帮助的测试仍然成立：F05-T48、F05-T49、F07-T17、F08-T14、F09-T01、F09-T19 和 F09-T25。架构师在一个 `COMMANDS` 里有 `SEARCH_COMMAND`、并导出了 `matching_form` 的模型上运行了 main 的全部测试。462 个测试通过，只在 Linux 上运行的 3 个用例被跳过（设计第 4 节）。F10 不改动之前功能的任何测试，也不改动 `tests/data/example/` 里的任何文件。F10-T01 检查真正 `COMMANDS` 的帮助里 `search` 的那一行，所用的形式在 F11 到 F13 加入它们的命令之后仍然成立。

**R09。** mock 定义了每条消息和带全部字段的 `SEARCH_COMMAND`，把这个命令加进 `COMMANDS`，并让 `catalog` 导出 `matching_form`。它的 `run` 不读文件，什么都不写，什么都不抛，并给出 0（设计第 2 节）。所以只检查命令的字段、某条消息、帮助、退出码 0，或者只检查没有文件被修改的测试，会在 mock 上通过。只检查 `cli` 在运行命令之前所做的事情的测试也一样，比如缺少数据文件夹、损坏的设置、没有词的 `search`、`search 番茄 --tag quick` 和 `search 番茄 --help`；单独检查 `matching_form` 的测试也一样，因为它是 F03 已经能用的函数。每个检查这类内容的用例，也检查 mock 弄错的东西：`search` 的输出，`run` 给出的退出码 1 或 2，`run` 抛出的 `UsageError`，或者故障工具记录的读取。F10-T01、F10-T07、F10-T11、F10-T15 和 F10-T16 只在一个 mock 会弄错的结果旁边检查这类内容。每个期望 `search` 给出退出码 0 的用例也检查完整的输出，这个输出从不为空。`tests/f10_support.py` 和 `tests/f10_texts.py` 在被导入时不调用 F10 的任何接口。

**两个系统。** 每个用例都在 Linux 和 Windows 上运行，在哪个系统上都不跳过。CI 只在 Linux 上运行，而 R09 把跳过的测试算作没有失败的测试。问题用系统的路径分隔符写出它的文件。所以在预期的一行里，`recipes/mapo-tofu.toml` 代表 `str(Path("recipes", "mapo-tofu.toml"))`：在 Windows 上是 `recipes\mapo-tofu.toml`，在 Linux 上是 `recipes/mapo-tofu.toml`。根目录下的文件，比如 `catalog.toml`，以及文件夹 `recipes`，在两个系统上写法相同。`search` 的表格里没有路径，所以它们的各列在两个系统上宽度相同。中文表格里每个汉字占两列，和 F10 原型一样。涉及两个系统不同之处的输入就是 F09 的那些，每个在两个系统上给出相同的结果：

- `recipes/rice.TOML`（F10-T13）用 `Path.rename` 得到，这在两个系统上都可行，与 F09-T11 相同。
- F10-T18 的数据文件夹 `One Drive/菜谱` 里有空格和汉字，在两个系统上都是合法路径。
- F10-T19 把带汉字的词和一个空词传给新的 `python -m recipe_menu` 进程，就像 F09-T26 传入 `list --tag 快手`。两个系统都把这样的词原样交给 Python。没有用例把带换行或不可见字符的词传给新进程。F10-T07、F10-T10 和 F10-T11 把这样的词传给 `main`。

测试经理在 Troy 的电脑上用 Python 3.13.18、main 上的读取函数和两个按设计实现 `search` 的模型算出了下面的预期文本：测试经理自己的模型，以及设计第 4 节里架构师的模型。对用例的每一行，以及按 F10-T20 生成的 300 行随机命令，两个模型给出的结果都相同。

**读取记录。** F10-T14 记录 `search` 打开了哪些文件、列出了哪些文件夹。它使用 `tests/f08_support.py` 的故障工具 `faults(base)`，不带规则，与 F09-T20 相同。故障工具把对 `base` 下每个路径的打开记为 `read` 加上相对于 `base`、用 `/` 写的路径，把每次 `os.scandir` 或 `os.listdir` 的列出记进“列出记录”（F08 测试方案第 2 节）。`search` 只通过 F03 和 F04 的读取函数访问磁盘（设计第 2 节）。所以记录取决于 `search` 调用哪些读取函数，不取决于 F10 的其他代码。`cli` 在运行命令之前读取 `settings.toml`，所以每份记录都以 `read settings.toml` 开头。

测试数据遵守这些规则，与 F09 测试方案相同：

- `EXAMPLE` 是代码仓库里的 `tests/data/example/` 文件夹（架构第 10 节）。`tests/conftest.py` 的 fixture `example_folder` 把它以 LF 换行复制到 `tmp_path / "recipe-menu"`，并给出这份副本上的 `DataFolder`。用例里的 `example` 就是这个 `DataFolder`。“P 处的一份新的示例副本”是用 `tests/f05_support.py` 的 `copy_example` 复制的又一份副本。不带 P 的“一份新的示例副本”在 `tmp_path` 下它自己的路径上。
- “P 处的 init 文件夹”由 `tests/f07_changes.py` 的 `make_init` 创建：一份新的示例副本，除 `tomato-egg` 外没有菜谱，没有菜单，带有空文件夹 `menus/` 和 `shopping/`。
- `home` 是 `tmp_path / "home"`，由 `tests/f05_support.py` 的 `make_home` 创建的空文件夹。它在 `example` 之外，所以不带 `--data` 的一行找不到数据文件夹，除非用例在 `home / "recipe-menu"` 放了一个。
- 测试用 `tests/f03_support.py` 的 `write` 写出每个文件，它以 UTF-8 和 LF 换行写文件，并先创建所在的文件夹，或者直接写字节。“把 F 里的 X 换成 Y”用 `tests/f07_changes.py` 的 `edit` 替换文件 F 里的第一个 X，`edit` 会检查 F 里有 X。
- 测试不改动代码仓库，不碰 `~/recipe-menu`，也不读时钟。每次调用 `main` 都传入 `home`、`environ` 和 `today`。F10-T19 和 F10-T21 启动 `python -m recipe_menu` 时把 `HOME` 和 `USERPROFILE` 设成 `tmp_path` 里的一个文件夹。用例只用 pytest 的 `monkeypatch.chdir` 改变当前文件夹。

下面这些有名字的改动构造用例的文件夹。每个改动作用于它所在用例的数据文件夹。第一组由 F09 测试方案第 2 节定义，由 `tests/f07_changes.py` 和 `tests/f09_support.py` 的辅助函数完成：

- 来自 F09：麻婆错误、米饭 0 份、删逗号、错字、损坏的设置、目录花括号错误、没有目录、没有菜谱文件夹、菜谱是文件、空的菜谱文件夹、不是菜谱、Rice Bowl、大写的 rice、文件夹 x、汤、额外的菜谱，以及带 S 的长名称。麻婆错误让 `recipes/mapo-tofu.toml` 的食材 3 写成目录里没有的 豆瓣酱。额外的菜谱是没有中文名称的 `boiled-egg`、没有英文名称的 `steamed-egg`，以及 `water`。带 S 的长名称只保留 `rice`，并加上 `a-long`，它的名称里有 TOML 转义 S，即 `\n`、`\r\n` 或 `\u2028`，所以每个名称占两行。汤加上标签 `汤` 和 `soup`，没有菜谱带有这个标签。
- 中文设置：把 `settings.toml` 里的 `language = "en"` 换成 `language = "zh"`。
- 英文写的鸡蛋：把 `recipes/tomato-egg.toml` 里的 `{ item = "鸡蛋", amount = "3" }` 换成 `{ item = "EGG", amount = "3" }`。F04 为它找到目录里的 鸡蛋，`check` 的报告与在示例上相同：没有错误，只有 `red-braised-pork` 的警告。
- 茄子：在 `catalog.toml` 的食材里 番茄 那一行后面加上 `  { zh = "茄子", en = "Eggplant", category = "produce" },` 这一行，并用下面第一段文字写出 `recipes/aubergine.toml`。`check` 于是报告 8 个菜谱、没有错误，以及 `red-braised-pork` 的警告。
- Crème：用下面第二段文字写出 `recipes/creme.toml`。`check` 于是报告 8 个菜谱、没有错误，以及 `red-braised-pork` 的警告。
- BOM 和 CRLF：把文件夹里的每个文件重新写成 `b"\xef\xbb\xbf"` 加上它的字节，并把其中每个 `b"\n"` 换成 `b"\r\n"`，与 F09-T22 相同。

```toml
name = { zh = "烧茄子", en = "Braised aubergine" }
servings = 2
tags = ["素"]
ingredients = [
  { item = "茄子", amount = "2 个" },
  { item = "大蒜", amount = "3 瓣" },
]
[steps]
zh = ["茄子切条，和蒜一起烧软。"]
en = ["Cut the eggplant into strips, and braise it with the garlic."]
```

```toml
name = { zh = "焦糖布丁", en = "Crème caramel" }
servings = 4
tags = []
ingredients = [
  { item = "鸡蛋", amount = "3" },
  { item = "糖", amount = "100 g" },
]
[steps]
zh = ["烤 40 分钟。"]
en = ["Bake for 40 minutes."]
```

调用 `main` 遵守这些约定：

- 像“在 F 里 `search 葱 quick --lang zh`”这样的一行，代表 `tests/f09_support.py` 的 `at(home, F, "search", "葱", "quick", "--lang", "zh")`。它加上 `--data` 和 F，通过 `tests/f07_support.py` 的 `call` 运行 `main`，传入 `home`、`environ`、`today=date(2026, 11, 10)` 和两个新的 `io.StringIO` 流，不传 `commands`，所以 `main` 使用真正的 `COMMANDS`。F 是一个文件夹或一个 `DataFolder`。“不指定文件夹”的一行没有 `--data`。除非用例给出，`environ` 是 `{}`。
- 引号里的词是一个词，按 Python 字符串的写法带着转义，比如 `"and egg"`、`""`、`'say "hi"'` 或 `"\u3000番茄"`。词里的每个 `\uXXXX` 代表那一个字符。
- 结果是 `(code, out, err)`。`(c, out L)` 代表 `(c, out, "")`，其中 out 是 L 的各行，每行后面跟着 `"\n"`，此外没有别的。`(c, err L)` 代表 `(c, "", err)`，其中 err 是 L 的各行，每行后面跟着 `"\n"`。测试比较完整的文字，从不比较它们的 `splitlines()`，因为 `splitlines()` 也在 U+000D 和 U+2028 处拆分，而 F10-T12 必须确认输出里没有它们。
- `FOUND(T, C)` 代表 `(0, out [*T, "", C])`：表格 T 的各行、一个空行和计数行 C。`NONE(C)` 代表 `(0, out [C])`。词里有换行时，计数行里也有它，out 的文字仍然在 L 的每一项后面加上 `"\n"`。
- `STOP(W, M)` 和 `STOP_ZH(W, M)` 是 `stop_at_error` 的英文三行和中文三行，与 F09 测试方案的定义相同。`tests/f09_texts.py` 的 `stop` 构造这个结果。W 是一个文件，比如 `catalog.toml`，或者一个文件加一个位置，比如 `recipes/mapo-tofu.toml, ingredient 3`，中文是 `recipes/mapo-tofu.toml，食材 3`。
- “在 `check` 的错误之中”的意思与 F09 测试方案相同，由 `tests/f09_support.py` 的 `assert_among_check` 检查。

预期文本如下。测试在 `tests/f10_texts.py` 里把每一段都写成字面量。它们不引用任何消息，也从不读原型文件，因为 `search` 和各读取函数的消息都是内部的（设计第 2 节，架构第 8 节）。

- `TOMATO_TABLE` 是 F10 原型“One word”表格的三行：`ID                   Name                      Matched in`、`tomato-egg           Tomato and egg stir-fry   name, ingredient` 和 `tomato-egg-noodles   Tomato and egg noodles    name, ingredient`。`TOMATO_TABLE_ZH` 是 `ID                   名称         匹配于`、`tomato-egg           番茄炒蛋     名称、食材` 和 `tomato-egg-noodles   番茄鸡蛋面   名称、食材`。
- `SCALLION_QUICK_TABLE_ZH` 是 F10 原型“Two words, in Chinese”表格的三行。`SCALLION_QUICK_TABLE` 是 `TOMATO_TABLE`，但两行里的 `name, ingredient` 都换成 `ingredient, tag`。“原型“Two words, in Chinese”的输出”是 `FOUND(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“葱”和“quick”。")`。
- `ALL_THREE_TABLE` 是 `TOMATO_TABLE`，但两行里都是 `name, ingredient, tag`。`ALL_THREE_TABLE_ZH` 是 `TOMATO_TABLE_ZH`，但两行里都是 `名称、食材、标签`。
- `EMPTY` 是 `A word is empty. Look for a name, such as "recipe-menu search tomato".`，`EMPTY_ZH` 是 `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。`。
- `HELP` 是 `COMMANDS` 里只有 `init`、`check`、`list`、`show` 和 `search` 时的英文帮助，共 18 行：F09 测试方案里 `HELP` 的第 1 到 4 行，设计 2.1 英文代码块里从 `Commands:` 到 `  --help           Show this help.` 的 12 行，一个空行，以及 F09 的 `HELP` 的最后一行。`HELP_ZH` 是同样的中文帮助，用 F09 的 `HELP_ZH` 和设计 2.1 的中文代码块。两张表格里每一行的文字都在 19 列之后开始。

A 到 F 块写出用例里那些带表格、又不由上面的表格构成的 `search` 输出。每个 `PS>` 行像原型那样给出不带 `--data` 的命令行，每一行都带着 `--data` 和它所在块的文件夹运行。一个 `PS>` 行的输出是它后面的各行，直到并包括它的计数行。一个空行把它和下一个 `PS>` 行隔开。每段输出的退出码都是 0，err 为空。

A 块，在 `example` 里：

```text
PS> recipe-menu search 炒蛋
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name

1 recipe matches "炒蛋".

PS> recipe-menu search 鸡蛋
ID                   Name                      Matched in
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

2 recipes match "鸡蛋".

PS> recipe-menu search 鸡蛋 --lang zh
ID                   名称         匹配于
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

2 个菜谱匹配“鸡蛋”。

PS> recipe-menu search scallion
ID                   Name                      Matched in
cola-wings           Cola chicken wings        ingredient
mapo-tofu            Mapo tofu                 ingredient
red-braised-pork     Red-braised pork belly    ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    ingredient

5 recipes match "scallion".

PS> recipe-menu search scallion --lang zh
ID                   名称         匹配于
cola-wings           可乐鸡翅     食材
mapo-tofu            麻婆豆腐     食材
red-braised-pork     红烧肉       食材
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   食材

5 个菜谱匹配“scallion”。

PS> recipe-menu search home
ID                 Name                      Matched in
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    tag
tomato-egg         Tomato and egg stir-fry   tag

4 recipes match "home".

PS> recipe-menu search 家常 --lang zh
ID                 名称       匹配于
cola-wings         可乐鸡翅   标签
mapo-tofu          麻婆豆腐   标签
red-braised-pork   红烧肉     标签
tomato-egg         番茄炒蛋   标签

4 个菜谱匹配“家常”。

PS> recipe-menu search 素
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   tag

1 recipe matches "素".

PS> recipe-menu search vegetarian --lang zh
ID         名称       匹配于
choy-sum   清炒菜心   标签

1 个菜谱匹配“vegetarian”。

PS> recipe-menu search staple
ID                   Name                     Matched in
rice                 Steamed rice             tag
tomato-egg-noodles   Tomato and egg noodles   tag

2 recipes match "staple".

PS> recipe-menu search 主食 --lang zh
ID                   名称         匹配于
rice                 米饭         标签
tomato-egg-noodles   番茄鸡蛋面   标签

2 个菜谱匹配“主食”。

PS> recipe-menu search 豆瓣
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient

1 recipe matches "豆瓣".

PS> recipe-menu search red-braised
ID                 Name                     Matched in
red-braised-pork   Red-braised pork belly   name

1 recipe matches "red-braised".

PS> recipe-menu search "choy sum"
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   name, ingredient

1 recipe matches "choy sum".

PS> recipe-menu search 鸡
ID                   Name                      Matched in
cola-wings           Cola chicken wings        name, ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "鸡".

PS> recipe-menu search -fr
ID           Name                      Matched in
choy-sum     Stir-fried choy sum       name
tomato-egg   Tomato and egg stir-fry   name

2 recipes match "-fr".

PS> recipe-menu search -
ID                 Name                      Matched in
choy-sum           Stir-fried choy sum       name
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    name, tag
tomato-egg         Tomato and egg stir-fry   name, tag

5 recipes match "-".

PS> recipe-menu search MAPO --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“MAPO”。

PS> recipe-menu search egg noodle
ID                   Name                     Matched in
tomato-egg-noodles   Tomato and egg noodles   name, ingredient

1 recipe matches "egg" and "noodle".

PS> recipe-menu search egg noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材

1 个菜谱同时匹配“egg”和“noodle”。

PS> recipe-menu search 番茄 家常
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient, tag

1 recipe matches "番茄" and "家常".

PS> recipe-menu search pork spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient, tag

1 recipe matches "pork" and "spicy".

PS> recipe-menu search home 葱
ID                 Name                      Matched in
cola-wings         Cola chicken wings        ingredient, tag
mapo-tofu          Mapo tofu                 ingredient, tag
red-braised-pork   Red-braised pork belly    ingredient, tag
tomato-egg         Tomato and egg stir-fry   ingredient, tag

4 recipes match "home" and "葱".

PS> recipe-menu search 米饭 主食
ID     Name           Matched in
rice   Steamed rice   name, tag

1 recipe matches "米饭" and "主食".

PS> recipe-menu search 米饭 主食 --lang zh
ID     名称   匹配于
rice   米饭   名称、标签

1 个菜谱同时匹配“米饭”和“主食”。

PS> recipe-menu search spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   tag

1 recipe matches "spicy".

PS> recipe-menu search 辣 --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   标签

1 个菜谱匹配“辣”。

PS> recipe-menu search rice
ID     Name           Matched in
rice   Steamed rice   name, ingredient

1 recipe matches "rice".

PS> recipe-menu search 米 --lang zh
ID     名称   匹配于
rice   米饭   名称、食材

1 个菜谱匹配“米”。

PS> recipe-menu search scallion QUICK noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签

1 个菜谱同时匹配“scallion”、“QUICK”和“noodle”。

PS> recipe-menu search mapo --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“mapo”。

PS> recipe-menu search cola
ID           Name                 Matched in
cola-wings   Cola chicken wings   name, ingredient

1 recipe matches "cola".

PS> recipe-menu search cola --lang zh
ID           名称       匹配于
cola-wings   可乐鸡翅   名称、食材

1 个菜谱匹配“cola”。
```

B 块，在一份带有额外的菜谱的新示例副本里：

```text
PS> recipe-menu search boiled
ID           Name           Matched in
boiled-egg   Boiled egg     name
water        Boiled water   name

2 recipes match "boiled".

PS> recipe-menu search boiled --lang zh
ID           名称         匹配于
boiled-egg   Boiled egg   名称
water        白开水       名称

2 个菜谱匹配“boiled”。

PS> recipe-menu search 蒸
ID            Name   Matched in
steamed-egg   蒸蛋   name

1 recipe matches "蒸".

PS> recipe-menu search 蒸 --lang zh
ID            名称   匹配于
steamed-egg   蒸蛋   名称

1 个菜谱匹配“蒸”。

PS> recipe-menu search egg
ID                   Name                      Matched in
boiled-egg           Boiled egg                name, ingredient
steamed-egg          蒸蛋                      ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

4 recipes match "egg".

PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
boiled-egg           Boiled egg   名称、食材
steamed-egg          蒸蛋         食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

4 个菜谱匹配“egg”。
```

C 块，在一份带有茄子的新示例副本里：

```text
PS> recipe-menu search egg
ID                   Name                      Matched in
aubergine            Braised aubergine         ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "egg".

PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
aubergine            烧茄子       食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

3 个菜谱匹配“egg”。

PS> recipe-menu search 茄
ID                   Name                      Matched in
aubergine            Braised aubergine         name, ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "茄".

PS> recipe-menu search plant
ID          Name                Matched in
aubergine   Braised aubergine   ingredient

1 recipe matches "plant".
```

D 块，在一份带有 Crème 的新示例副本里：

```text
PS> recipe-menu search crème
ID      Name            Matched in
creme   Crème caramel   name

1 recipe matches "crème".

PS> recipe-menu search Crème --lang zh
ID      名称       匹配于
creme   焦糖布丁   名称

1 个菜谱匹配“Crème”。

PS> recipe-menu search CARAMEL
ID      Name            Matched in
creme   Crème caramel   name

1 recipe matches "CARAMEL".
```

E 块，在一份带 S 的长名称的新示例副本里，每个 S 都相同：

```text
PS> recipe-menu search long
ID       Name                Matched in
a-long   A long first line   name
         end

1 recipe matches "long".

PS> recipe-menu search long --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“long”。

PS> recipe-menu search 尾 --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“尾”。

PS> recipe-menu search 大米
ID       Name                Matched in
a-long   A long first line   ingredient
         end
rice     Steamed rice        ingredient

2 recipes match "大米".

PS> recipe-menu search 大米 --lang zh
ID       名称           匹配于
a-long   长长的第一行   食材
         尾
rice     米饭           食材

2 个菜谱匹配“大米”。

PS> recipe-menu search steamed
ID     Name           Matched in
rice   Steamed rice   name

1 recipe matches "steamed".
```

F 块，在 init 文件夹里：

```text
PS> recipe-menu search 番茄
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient

1 recipe matches "番茄".

PS> recipe-menu search 番茄 --lang zh
ID           名称       匹配于
tomato-egg   番茄炒蛋   名称、食材

1 个菜谱匹配“番茄”。
```

用例里 `cli` 的消息是 F05 设计 2.10 里的文字，命令换成 `search`：`TOO_FEW_ARGUMENTS` 是 `An argument is missing. Write "recipe-menu search WORD...".` 和 `缺少参数。请写成“recipe-menu search 词...”。`，`UNKNOWN_OPTION` 在没有选项时的形式是 `"search" has no option "--tag". It has no options of its own.` 和 `“search”没有选项“--tag”。它没有自己的选项。`。`tests/f09_texts.py` 的 `RUN_HELP_COMMANDS` 和 `RUN_HELP_OPTIONS` 给出它们后面的那一行。用例里读取函数的消息是 F09 测试方案第 2 节的那些：`FILE_MISSING`、`FOLDER_MISSING`、`FOLDER_IS_FILE`、`FILE_IS_FOLDER`、`MISSING_BRACE`、列出时的 `NOT_A_RECIPE_ID`、`TOML_ENDING_NOT_SMALL`、菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`，以及设置的 `UNKNOWN_MEAL(meal="supper")`，位置是 `line 11`（`第 11 行`）、`ingredient 3`（`食材 3`）和 `meals`（`餐次`）。`tests/f09_texts.py` 把它们每一条都写了出来。

用例分在下面这些文件里，使每个文件不超过 R06 的 500 行：

| 文件 | 用例 |
| --- | --- |
| `tests/test_f10_command.py` | F10-T01 和 F10-T02 |
| `tests/test_f10_search.py` | F10-T03 和 F10-T04 |
| `tests/test_f10_places.py` | F10-T05 和 F10-T06 |
| `tests/test_f10_words.py` | F10-T07 到 F10-T09 |
| `tests/test_f10_count_line.py` | F10-T10 和 F10-T11 |
| `tests/test_f10_widths_and_errors.py` | F10-T12 和 F10-T13 |
| `tests/test_f10_cli_and_reads.py` | F10-T14 和 F10-T15 |
| `tests/test_f10_integration.py` | F10-T16 到 F10-T19 |
| `tests/test_f10_random.py` | F10-T20，连同它生成文件夹和词的代码 |
| `tests/test_f10_performance.py` | F10-T21 |
| `tests/f10_support.py` | 没有测试。新的有名字的改动，以及 `aubergine` 和 `creme` 的两段文字。它复用 `tests/f05_support.py` 的 `make_home`、`copy_example` 和 `run_module`，`tests/f05_texts.py` 的 `no_data_folder`，`tests/f07_support.py` 的 `call` 和 `snapshot`，`tests/f07_changes.py` 的 `make_init`、`edit` 和各个有名字的改动，`tests/f08_support.py` 的 `faults`，`tests/f09_support.py` 的 `at`、`made`、`new_context`、`run_command`、`assert_among_check`、各个有名字的改动和额外的菜谱，以及 `tests/f03_support.py` 的 `write`。 |
| `tests/f10_texts.py` | 没有测试。上面的预期文本和 A 到 F 块，写成字面量。它写出 `HELP` 和 `HELP_ZH` 两张表格的 12 行，另外 6 行取自 `tests/f09_texts.py` 的 `HELP` 和 `HELP_ZH`。它复用 `tests/f09_texts.py` 的 `out`、`err`、`stop`、读取函数的问题和消息、`MAPO`、`MAPO_ZH`、`unknown_id`、`RUN_HELP_COMMANDS` 和 `RUN_HELP_OPTIONS`。 |
| `tests/pt01_support.py` | 没有测试。它新增 `pt01_search`，即 PT01 文件夹上 `search 食材001` 的预期输出（第 3 节）。它的其他函数保持原来的名字和行为。 |
| `tests/conftest.py` | 不变。F10 使用它的 fixture `example_folder` 和 `default_int_limit`，以及 pytest 的 `tmp_path`、`monkeypatch` 和 `record_property`。 |

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F10-T01 | 单元 | `SEARCH_COMMAND`、`SEARCH_COMMAND.run`、`main` | 2.1 的示例。`SEARCH_COMMAND` 的词是 `search`，用法是 `search WORD...` 和 `search 词...`，帮助行是 F05 原型里的那一行，参数 `WORD` 必须写、可以重复，没有选项，并且是 `FolderUse.READ`。它的 `run` 用 `context.lang` 把结果写到 `context.out` 并给出 0，或者把错误的三行写到 `context.err` 并给出 1。它既不用 `context.settings`，也不用 `context.today`。帮助在 `show ID` 后面列出 `search WORD...`，两张表格的第二列都在 19 列之后开始，帮助共 18 行（2.1，选择 1）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`。那一行 `# raises` 在 `pytest.raises(UsageError)` 里运行，用一个值相同的新 `Context` 和新的流。在 `help_lines` 里，对 `main` 的调用还传入 `commands=(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND)`，因为这 18 行只在 `COMMANDS` 里只有这五个命令时成立，F11 到 F13 会加入它们的命令。然后，每次都用新的流和 `Context(Lang.EN, example, Settings(Lang.ZH, (Meal.BREAKFAST,), 5), out, err, date(2030, 1, 1))`：1. 用 `Arguments(("番茄",))` 调用 `run`。2. 用 `Arguments(("葱", "quick"))` 调用 `run`。3. 用 `Arguments(("lamb",))` 调用 `run`。4. 在 `example` 里做麻婆错误，用 `Context(Lang.ZH, example, Settings(), out, err, date(2026, 11, 10))` 和 `Arguments(("lamb",))` 调用 `run`。5. `help_lines("--help")` 和 `help_lines("--help", "--lang", "zh")` 的全部内容。6. 通过 `call`、用真正的 `COMMANDS` 运行 `--help` 和 `--help --lang zh`。 | 示例的每条断言都成立，那一行 `# raises` 抛出 `UsageError`，之后它的两个流都为空。1. 0，out 是 `[*TOMATO_TABLE, "", '2 recipes match "番茄".']`，err 为空。2. 0，out 是 `[*SCALLION_QUICK_TABLE, "", '2 recipes match "葱" and "quick".']`，err 为空。3. 0，out 是 `['No recipe matches "lamb".']`，err 为空。4. 1，out 为空，err 是 `STOP_ZH(recipes/mapo-tofu.toml，食材 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe)`，尽管 `lamb` 不匹配任何菜谱。5. `HELP` 和 `HELP_ZH`。6. 退出码 0，err 为空。在 out 里，以 `  show ID ` 开头的那一行的下一行以 `  search WORD... ` 开头、以 `Find recipes by name, ingredient, or tag.` 结尾，或者以 `  search 词... ` 开头、以 `按名称、食材或标签找菜谱。` 结尾。它的文字与以 `  --lang en\|zh` 开头的那一行的文字从同一个显示列开始：两段文字前面部分的 `display_width` 相同。无论 F11 到 F13 在 `search` 后面加入什么命令，这些规则都成立。 |
| F10-T02 | 单元 | `SEARCH_COMMAND.run` | 2.2 的第 1 步。`run` 在读任何文件、写任何输出之前检查每个词。词的匹配形式为空时，它抛出 `UsageError(EMPTY_WORD, None)`：空的文字，或者只有 `str.strip()` 会去掉的空白，包括 U+00A0、U+3000 和 U+2028，别的词没问题时也一样。这个错误没有提示，也没有值。其他的词都能通过检查：不是空白的 U+200B ZERO WIDTH SPACE 和 U+FEFF ZERO WIDTH NO-BREAK SPACE，以 `-` 开头的词，以及仍然是 `str` 的 5,000 位数字的词（2.1 错误，2.2 第 1 步，选择 4 和 9）。 | 使用 fixture `default_int_limit`。每次调用都用新的流和 `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`，在 `faults(tmp_path)` 里运行。1. 在 `pytest.raises(UsageError)` 里：对 `("",)`、`(" ",)`、`("\t",)`、`("\n",)`、`("\u00a0",)`（NO-BREAK SPACE）、`("\u3000",)`（IDEOGRAPHIC SPACE）、`("\u2028",)`（LINE SEPARATOR）、`(" \u3000\t",)`、`("番茄", "")`、`("", "番茄")`、`(" ", "lamb")`、`("番茄", "\u3000")` 和 `("番茄", "quick", "\t")` 中的每个 V 调用 `Arguments(V)`。2. 对 `("\u200b",)`、`("\ufeff",)`、`("-x",)`、`("a",)`、`(" a ",)`、`("\u3000番茄",)`、`("9" * 5000,)` 和 `("番茄", "\u200b")` 中的每个 V 调用 `Arguments(V)`。 | 1. 每个错误的 `text(Lang.EN)` 是 `EMPTY`，`text(Lang.ZH)` 是 `EMPTY_ZH`，`hint` 是 `None`，`values` 是 `()`。每次调用后两个流都为空，故障工具的记录和列出记录也都为空。2. 没有调用抛出异常。每次都给出 1，out 为空，err 是 `STOP(catalog.toml, FILE_MISSING)`，因为文件夹不存在。 |
| F10-T03 | 功能 | `recipe-menu search`、`main` | 按顺序运行 2.2 的示例，用真正的命令：原型的五段输出，位置 `名称`，窄的表格，作为较长名称一部分的词，词里的空白，两种语言里的三个词，重复的词和只有大小写不同的词，开头是 U+3000 的词，五样不算数的东西，词里的形近字母和不换行空格，两种语言里的空词，没有词的一行，`search` 没有的选项，让 `search 番茄` 停下、但不让 `search ""` 停下的 `mapo-tofu` 错误，以及没有菜谱文件的文件夹（2.2，选择 3 到 8）。 | 示例的各行，`folder` 是 `example`，`home` 是 `home`，示例的 `run` 调用 `main` 时不传 `commands`。 | 示例的每条断言都成立。 |
| F10-T04 | 功能 | `recipe-menu search` | 在 `main` 上运行 v0.1-S11，完整运行 F10 原型，每段输出也用另一种语言运行。另一种语言用到 A 点的新文字：两个词的英文那一行，一个词的中文那一行，以及位置 `名称`（2.2，选择 5 和 6）。 | 在 `example` 里：1. `search 番茄`、`search TOMATO`、`search 葱 quick --lang zh`、`search lamb` 和 `search 豆腐 quick --lang zh`。2. `search 番茄 --lang zh`、`search TOMATO --lang zh`、`search 葱 quick`、`search lamb --lang zh` 和 `search 豆腐 quick`。 | 1. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`、`FOUND(TOMATO_TABLE, '2 recipes match "TOMATO".')`、原型“Two words, in Chinese”的输出、`NONE('No recipe matches "lamb".')` 和 `NONE("没有菜谱同时匹配“豆腐”和“quick”。")`：原型的五段输出，每段的退出码都是 0，正是 v0.1-S11 所期望的。2. `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“番茄”。")`、`FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“TOMATO”。")`、`FOUND(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')`、`NONE("没有菜谱匹配“lamb”。")` 和 `NONE('No recipe matches "豆腐" and "quick".')`。 |
| F10-T05 | 功能 | `recipe-menu search` | 选择 3。词出现在某个位置的任一种语言的文字里时，就出现在这个位置：菜谱的名称，每行食材所对应目录食材的两个名称，以及每个标签的两个名称。无论文件写的是哪个名称，一行食材都指向目录里的食材。所以 `search scallion` 找到文件里写 `葱` 的每个菜谱，文件把 鸡蛋 写成 `EGG` 也什么都不改变。缺少一种语言的名称只有另一种语言的文字，名称格子在两种语言里都显示这段文字。一行的位置只来自这些词，所以只有食材含有这个词时，`search 鸡蛋` 的一行里有 `ingredient` 而没有 `name`（2.2 的位置表，选择 3）。 | 1. 在 `example` 里：A 块里从 `search 炒蛋` 到 `search red-braised` 的各行。2. 在一份带有英文写的鸡蛋的新示例副本里：`search 鸡蛋` 和 `search 鸡蛋 --lang zh`。3. 在一份带有额外的菜谱的新示例副本里：B 块的六行。 | 1 和 3. 每一行给出 A 块或 B 块里它那一行的输出。2. A 块里同样两行的输出。所以 `search home` 给四个菜谱写出 `tag`，`search scallion` 给五个菜谱写出 `ingredient`。`search 蒸` 按中文名称找到 `steamed-egg`，并在英文表格里显示 `蒸蛋`。`search egg` 按食材的英文名称 `Egg` 找到 `steamed-egg`，而它的文件把这种食材写成 `鸡蛋`。`red-braised-pork` 和额外的菜谱的警告都不写出。 |
| F10-T06 | 功能 | `recipe-menu search` | 选择 3。别的都不算数：备注、步骤、ID、份数、数量、用量、单位和分类都不算，文件夹里没有菜谱用到的目录食材或标签的名称也不算。每个这样的词都给出没有匹配的那一行，退出码是 0（2.2，选择 3 和 6）。 | 1. 在 `example` 里：对下面每个 W 运行 `search W`：`wedges` 和 `切块`（`tomato-egg` 的备注），`crushed`（`choy-sum` 的备注），`scramble` 和 `热锅`（`tomato-egg` 的步骤），`dairy` 和 `蛋奶`（鸡蛋的分类），`produce`（分类的 key），`mapo-tofu` 和 `cola-wings`（ID），`2`（份数），`300`（数量），`tbsp`（单位），`适量`（用量），`片`（姜 的默认单位），以及 `broccoli` 和 `西兰花`（没有菜谱用到的目录食材）。然后是 `search 切块 --lang zh` 和 `search dairy --lang zh`。2. 在一份带有额外的菜谱的新示例副本里：`search room`（英文备注）、`search 打散`（中文备注）和 `search 烧开`（中文步骤）。3. 在一份带有茄子的新示例副本里：`search strips`（英文步骤）。4. 在一份带有汤的新示例副本里：`search soup` 和 `search 汤 --lang zh`。 | 1. 每个 W 给出 `NONE('No recipe matches "W".')`。最后两行给出 `NONE("没有菜谱匹配“切块”。")` 和 `NONE("没有菜谱匹配“dairy”。")`。2 和 3. 每一行对它的词 W 给出 `NONE('No recipe matches "W".')`。4. `NONE('No recipe matches "soup".')` 和 `NONE("没有菜谱匹配“汤”。")`。 |
| F10-T07 | 功能 | `matching_form`、`recipe-menu search` | 3.1 的示例和选择 4。词的匹配形式是文字的匹配形式的一部分时，词就出现在这段文字里。词可以是较长名称的一部分，英文和中文都一样。大小写只对字母 A 到 Z 有区别，所以 `È` 和 `è` 不同。词两端的空白不算数，包括 U+00A0 和 U+3000。词里面的空白按写的样子算数，包括 U+00A0。形近字母保持原样，文字不做规范化，U+200B 和 U+FEFF 是词里的字符。以一个 `-` 开头的词是词，以 `--` 开头的词是 `cli` 的选项。计数行按输入的样子写出每个词（3.1，选择 4）。 | 1. 3.1 的示例。2. 在 `example` 里：对 `tomato`、`Tomato`、`tOmAtO`、`" tomato "`、`"\u00a0番茄\t"` 和 `"\u3000TOMATO\u3000"` 中的每个 W 运行 `search W`。3. 在 `example` 里：A 块里从 `search "choy sum"` 到 `search MAPO --lang zh` 的各行。4. 在 `example` 里：对 `"and  egg"`（两个空格）、`"choy\u00a0sum"`、`"stir fry"`、`"番\u200b茄"`、`"\u200b"`、`"\ufeff番茄"`、`"T\u043emato"`（U+043E CYRILLIC SMALL LETTER O）、`"R\u0130CE"`（U+0130 LATIN CAPITAL LETTER I WITH DOT ABOVE）和 `-x` 中的每个 W 运行 `search W`。然后是 `search --x`。5. 在一份带有茄子的新示例副本里：C 块的四行。6. 在一份带有 Crème 的新示例副本里：D 块的三行，然后是 `search CRÈME`、`search CRÈME --lang zh`、`search creme` 和 `search "Cre\u0300me"`，最后这个词的 e 后面跟着 U+0300 COMBINING GRAVE ACCENT。 | 1. 示例的每条断言都成立。2. 每个 W 给出 `FOUND(TOMATO_TABLE, '2 recipes match "W".')`，W 按输入的样子写出。3 和 5. 每一行给出 A 块或 C 块里它那一行的输出。所以 `-fr` 和 `-` 是词，`鸡` 是 `可乐鸡翅`、`鸡翅中`、`鸡蛋` 和 `番茄鸡蛋面` 的一部分，`egg` 是 `Eggplant` 的一部分。4. 每个 W 给出 `NONE('No recipe matches "W".')`，`search --x` 给出 `(2, err ['"search" has no option "--x". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`。6. D 块的各段输出，然后是 `NONE('No recipe matches "CRÈME".')`、`NONE("没有菜谱匹配“CRÈME”。")`、`NONE('No recipe matches "creme".')` 和 `NONE('No recipe matches "Cre\u0300me".')`，因为文件把 è 写成一个字符。 |
| F10-T08 | 功能 | `recipe-menu search` | 选择 4。只有每个词都至少出现在菜谱的一个位置时，菜谱才匹配，两个词可以出现在不同的位置。词的顺序既不改变菜谱，也不改变它们的位置，只改变计数行里词的顺序。没有菜谱含有的词让结果没有匹配，无论其他词找到什么（2.2 第 4 步，选择 4）。 | 在 `example` 里：1. `search quick 葱` 和 `search quick 葱 --lang zh`。2. `search tomato egg`。3. A 块里从 `search egg noodle` 到 `search home 葱` 的各行。4. `search tomato egg quick 葱` 和 `search tomato egg quick 葱 --lang zh`。5. `search egg spicy`、`search egg spicy --lang zh`、`search 葱 quick lamb` 和 `search 葱 quick lamb --lang zh`。 | 1. `FOUND(SCALLION_QUICK_TABLE, '2 recipes match "quick" and "葱".')` 和 `FOUND(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“quick”和“葱”。")`：原型里 `search 葱 quick` 的行和位置。2. `FOUND(TOMATO_TABLE, '2 recipes match "tomato" and "egg".')`。3. A 块里它们各行的输出。4. `FOUND(ALL_THREE_TABLE, '2 recipes match "tomato", "egg", "quick", and "葱".')` 和 `FOUND(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“tomato”、“egg”、“quick”和“葱”。")`。5. `NONE('No recipe matches "egg" and "spicy".')`、`NONE("没有菜谱同时匹配“egg”和“spicy”。")`、`NONE('No recipe matches "葱", "quick", and "lamb".')` 和 `NONE("没有菜谱同时匹配“葱”、“quick”和“lamb”。")`。 |
| F10-T09 | 功能 | `recipe-menu search` | 选择 5。`Matched in` 格子写出至少有一个词出现的每个位置，按名称、食材、标签的顺序，每个位置只写一次，无论词的顺序如何。`comma_list` 在英文里用 `, ` 连接这些位置，在中文里用 `、` 连接（2.2 的行，选择 5）。 | 在 `example` 里：1. `search quick 番茄`、`search 番茄 tomato` 和 `search 番茄 快手 --lang zh`。2. A 块里从 `search 米饭 主食` 到 `search scallion QUICK noodle --lang zh` 的各行。 | 1. `FOUND(ALL_THREE_TABLE, '2 recipes match "quick" and "番茄".')`、`FOUND(TOMATO_TABLE, '2 recipes match "番茄" and "tomato".')` 和 `FOUND(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“番茄”和“快手”。")`。2. A 块里它们各行的输出。加上 F10-T04、F10-T05 和 F10-T07，七种格子 `name`、`ingredient`、`tag`、`name, ingredient`、`name, tag`、`ingredient, tag` 和 `name, ingredient, tag` 都在英文里出现，`名称`、`食材`、`标签`、`名称、食材`、`名称、标签`、`食材、标签` 和 `名称、食材、标签` 都在中文里出现。 |
| F10-T10 | 功能 | `recipe-menu search` | 选择 6 和 A 点的新文字。去掉与前面某个词完全相同的词之后数词：一个词时计数行用 `RECIPES_MATCH`，两个及以上时用 `RECIPES_MATCH_ALL`。两者都是按菜谱数选择的 `Plural`，只有 `RECIPES_MATCH_ALL` 的中文里有 同时。没有匹配时，按同样的词数给出 `NO_RECIPE_MATCHES` 或 `NO_RECIPE_MATCHES_ALL`。`{words}` 是加了引号的词的 `and_list`。每个词按输入的样子写出：它的大小写、空格、`"`、花括号、换行和 5,000 位数字都保持原样（2.2 的消息，选择 6 和 9）。 | 使用 fixture `default_int_limit`。在 `example` 里：1. `search scallion QUICK noodle`、`search mapo --lang zh` 和 `search 葱 quick 面 --lang zh`。2. `search egg egg`、`search egg egg --lang zh`、`search egg EGG`、`search egg EGG --lang zh`、`search egg " egg"`、`search 葱 quick 葱` 和 `search 葱 quick 葱 --lang zh`。3. `search lamb lamb`、`search lamb lamb --lang zh`、`search quick 1`、`search quick 1 --lang zh`、`search lamb beef fish` 和 `search lamb beef fish --lang zh`。4. `search 'say "hi"'`、`search 'say "hi"' --lang zh`、`search "{words}"`、`search "{count}" --lang zh`、`search "to\nmato"`、`search "番茄\n"` 和 `search X`，其中 X 是 `"9" * 5000`。 | 1. 设计 2.2 的示例为 `search scallion QUICK noodle` 给出的输出，它以 `1 recipe matches "scallion", "QUICK", and "noodle".` 结尾。然后是 A 块里 `search mapo --lang zh` 的输出，它以 `1 个菜谱匹配“mapo”。` 结尾，以及设计的示例为 `search 葱 quick 面 --lang zh` 给出的输出，它以 `1 个菜谱同时匹配“葱”、“quick”和“面”。` 结尾。2. `FOUND(TOMATO_TABLE, '2 recipes match "egg".')`、`FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“egg”。")`、`FOUND(TOMATO_TABLE, '2 recipes match "egg" and "EGG".')`、`FOUND(TOMATO_TABLE_ZH, "2 个菜谱同时匹配“egg”和“EGG”。")`、`FOUND(TOMATO_TABLE, '2 recipes match "egg" and " egg".')`、`FOUND(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')`，以及原型“Two words, in Chinese”的输出。3. `NONE('No recipe matches "lamb".')`、`NONE("没有菜谱匹配“lamb”。")`、`NONE('No recipe matches "quick" and "1".')`、`NONE("没有菜谱同时匹配“quick”和“1”。")`、`NONE('No recipe matches "lamb", "beef", and "fish".')` 和 `NONE("没有菜谱同时匹配“lamb”、“beef”和“fish”。")`。4. `NONE('No recipe matches "say "hi"".')`、`NONE("没有菜谱匹配“say "hi"”。")`、`NONE('No recipe matches "{words}".')`、`NONE("没有菜谱匹配“{count}”。")`、`NONE('No recipe matches "to\nmato".')`、`FOUND(TOMATO_TABLE, '2 recipes match "番茄\n".')` 和 `NONE(f'No recipe matches "{X}".')`。在 `to\nmato` 和 `番茄\n` 里，词里的换行让 out 上的计数行断开。 |
| F10-T11 | 功能 | `recipe-menu search`、`main` | 选择 4 和 B 点。匹配形式为空的词给出 `EMPTY_WORD` 和退出码 2，错误流上一行、没有提示，输出流上什么都没有。这一行用输出的语言，这个语言可以来自设置。`run` 在读任何文件之前检查这些词，所以目录、列出或某个菜谱有错误的文件夹给出相同的结果。`cli` 在运行 `search` 之前检查数据文件夹、设置、`--help` 和选项，所以它们每一个都排在前面（2.2 第 1 步和错误，选择 8）。 | 1. 在 `example` 里：对 `[""]`、`[" "]`、`["\t"]`、`["\u00a0"]`、`["\u3000"]`、`["\u2028"]`、`["番茄", ""]`、`["", "番茄"]`、`[" ", "lamb"]`、`["番茄", "\u3000"]` 和 `["", ""]` 中的每个 W，带着词 W 运行 `search`。然后是 `search "" --lang zh` 和 `search 番茄 " " --lang zh`。2. 在一份带有中文设置的新示例副本里：`search ""` 和 `search "" --lang en`。3. 每个都在一份新的示例副本里：没有目录时 `search ""`，目录花括号错误时 `search " " --lang zh`，没有菜谱文件夹时 `search "\u3000"`，Rice Bowl 时 `search ""`，麻婆错误时 `search "" 番茄`。然后在这五个文件夹里各运行 `search 番茄`。4. M 是 `tmp_path / "missing"`：在 M 里 `search ""` 和在 M 里 `search "" --lang zh`。5. 在一份带有损坏的设置的新示例副本里：`search ""`。6. 在 `example` 里：`search "" --help` 和 `search "" --tag x`。 | 1. 每个 W 给出 `(2, err [EMPTY])`，最后两行给出 `(2, err [EMPTY_ZH])`。2. `(2, err [EMPTY_ZH])` 和 `(2, err [EMPTY])`。3. `(2, err [EMPTY])`、`(2, err [EMPTY_ZH])`、`(2, err [EMPTY])`、`(2, err [EMPTY])` 和 `(2, err [EMPTY])`。然后 `search 番茄` 依次给出 `(1, err STOP(catalog.toml, FILE_MISSING))`、`(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`、`(1, err STOP(recipes, FOLDER_MISSING))`、`(1, err STOP(recipes/Rice Bowl.toml, NOT_A_RECIPE_ID of a listing))` 和 `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe))`。4. `no_data_folder(M)` 和 `no_data_folder(M, ZH)`。5. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`。6. 退出码 0，err 为空，out 上的文字与不指定文件夹的 `--help` 相同，然后是 `(2, err ['"search" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`。 |
| F10-T12 | 功能 | `recipe-menu search` | 选择 7。`search` 不给 `format_table` 传 `min_widths`，所以每一列与它自己格子里最宽的一行一样宽，标题也算在内，窄的结果的表格保持窄。`search` 不量它不显示的菜谱。两行的名称占两行，它的宽度是较长那一行的宽度，无论名称里是哪种换行（2.2 的输出，选择 7，F02 设计 2.9）。 | 1. 在 `example` 里：`search mapo`、`search mapo --lang zh`、`search rice`、`search rice --lang zh`、`search spicy`、`search cola` 和 `search cola --lang zh`。2. 对 `\n`、`\r\n` 和 `\u2028` 中的每个 S，一份带 S 的长名称的新示例副本。在里面运行：E 块的六行。 | 1. `search mapo` 给出设计 2.2 的示例为它给出的输出，其他每一行给出 A 块里它那一行的输出。在 `search mapo` 里，名称列在 12 列之后开始，而文件夹里最宽的 ID `tomato-egg-noodles` 会让它在 21 列之后开始。在 `search rice --lang zh` 里，名称列与它的标题 `名称` 一样宽。2. 对每个 S，这六行给出 E 块的输出，每个 S 的文字都相同。所以没有输出含有 U+000D 或 U+2028，`a-long` 的名称格子占两行，`search steamed` 给出的表格只有 `rice` 的宽度。按整个格子取宽度，或者只在 U+000A 处拆分格子的行再取宽度，都会让名称列更宽。 |
| F10-T13 | 功能 | `recipe-menu search`、`recipe-menu check` | 选择 8。错误让 `search` 在第一个错误处停下，用输出的语言写出 `stop_at_error` 的三行，退出码 1，输出流上什么都没有。先是目录，然后是 `recipes/` 的列出，然后按 ID 的顺序是各个菜谱。`search` 在匹配任何菜谱之前解析每个菜谱，所以任何菜谱文件里的错误都让它停下，这些词在那个菜谱里什么都不匹配时也一样。缺少 `recipes/` 让它停下，没有菜谱文件的 `recipes/` 给出没有匹配的那一行和退出码 0。警告不写出，也不改变任何东西。让 `search` 停下的错误在 `check` 的错误之中（2.2 第 2 和 3 步，选择 8）。 | 1 到 11 的每个输入在一份新的示例副本里，运行 `search 番茄`、`search 番茄 --lang zh`、`search lamb`、`check` 和 `check --lang zh`：1. 没有目录。2. 目录花括号错误。3. 没有菜谱文件夹。4. 菜谱是文件。5. Rice Bowl。6. 大写的 rice。7. 文件夹 x。8. 麻婆错误。9. 麻婆错误和米饭 0 份。10. 麻婆错误和 Rice Bowl。11. 目录花括号错误和麻婆错误。然后，每个都在一份新的示例副本里：12. 空的菜谱文件夹：`search 番茄`、`search 番茄 --lang zh` 和 `search 番茄 quick`。13. 不是菜谱：`search 番茄`。14. 在 `example` 里：`search pork`。 | 1 到 11. `search 番茄` 和 `search lamb` 给出 `(1, err STOP(W, M))`，`search 番茄 --lang zh` 给出 `(1, err STOP_ZH(W, M))`，W 和 M 是：1. `catalog.toml` 和 `FILE_MISSING`。2. `catalog.toml, line 11` 和 `MISSING_BRACE`。3. `recipes` 和 `FOLDER_MISSING`。4. `recipes` 和 `FOLDER_IS_FILE`。5. `recipes/Rice Bowl.toml` 和列出时的 `NOT_A_RECIPE_ID`。6. `recipes/rice.TOML` 和 `TOML_ENDING_NOT_SMALL`。7. `recipes/x.toml` 和 `FILE_IS_FOLDER`。8 和 9. `recipes/mapo-tofu.toml, ingredient 3` 和菜谱的 `UNKNOWN_INGREDIENT(name="豆瓣酱")`，即第一个有错误的 ID。10. 5 的 W 和 M，因为 `read_recipes` 先给出列出时的问题。11. 2 的 W 和 M。在每个输入里，这个错误都在两种语言的 `check` 的错误之中。12. `NONE('No recipe matches "番茄".')`、`NONE("没有菜谱匹配“番茄”。")` 和 `NONE('No recipe matches "番茄" and "quick".')`。13. `NONE('No recipe matches "番茄".')`，因为两个条目都不是菜谱文件。14. 设计 2.2 的示例为 `search pork` 给出的输出，err 为空，尽管 `red-braised-pork` 有警告。 |
| F10-T14 | 功能 | `recipe-menu search`、`main` | `search` 读的文件。它读一次目录，列出一次 `recipes/`，按 ID 的顺序把每个菜谱文件读一次，没有菜谱匹配时也一样。遇到空词、`--help` 和没有词的一行时，它什么都不读；目录有错误时，它不列出任何文件夹。它既不读常备清单，也不读菜单，所以那里的错误什么都不改变（2.2 的副作用，选择 8，架构第 8 节）。 | 第 1 到 5 行和第 7 行在 `example` 里运行，每行都在一个新的 `faults(example.root)` 里：1. `search 番茄`。2. `search 葱 quick --lang zh`。3. `search lamb`。4. `search ""`。5. `search 番茄 ""`。6. 在一份带有目录花括号错误的新示例副本里，在它的根目录的 `faults` 里运行 `search 番茄`。7. `search 番茄 --help` 和 `search`。然后在 `example` 里做删逗号和错字，并用 `[[[\n` 写出 `menus/2026-W48.toml`。8. 不用故障工具：`search 番茄` 和 `search 葱 quick --lang zh`。 | 记录、列出记录和结果：1. `read settings.toml`、`read catalog.toml`，以及按 ID 的顺序对示例七个 ID 中的每一个的 `read recipes/<ID>.toml`，从 `choy-sum` 到 `tomato-egg-noodles`；列出记录 `recipes`；结果 `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`。2. 同样的记录和列出记录，以及原型“Two words, in Chinese”的输出。3. 同样的记录和列出记录，以及 `NONE('No recipe matches "lamb".')`。4 和 5. 只有 `read settings.toml`，没有列出记录，结果 `(2, err [EMPTY])`。6. `read settings.toml` 和 `read catalog.toml`，没有列出记录，结果 `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`。7. 每一行都只有 `read settings.toml`，没有列出记录；第一行是退出码 0 和帮助，第二行是退出码 2 和 `TOO_FEW_ARGUMENTS` 的两行。8. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')` 和原型“Two words, in Chinese”的输出。 |
| F10-T15 | 功能 | `recipe-menu search`、`main` | `cli` 在运行 `search` 之前报告命令行上的错误、缺少的数据文件夹和损坏的设置，用 F05 的消息和退出码：没有词，以及 `search` 没有的选项，两种语言都检查。`search --help` 显示帮助，什么都不运行。同样的文件夹随后给出 `search` 的输出（2.2 错误，F05 设计 2.10）。 | 1. 在 `example` 里：`search`、`search --lang zh`、`search 番茄 --tag quick`、`search 番茄 --tag quick --lang zh` 和 `search --tag`。2. M 是 `tmp_path / "missing"`：在 M 里 `search 番茄` 和在 M 里 `search 番茄 --lang zh`。3. 在一份带有损坏的设置的新示例副本里：`search 番茄`。4. 在一份带有麻婆错误的新示例副本里：`search 番茄 --help`、`search --help --lang zh` 和 `search lamb --help`。5. 在 `example` 里：`search 番茄`。 | 1. `(2, err ['An argument is missing. Write "recipe-menu search WORD...".', 'Run "recipe-menu --help" to see the commands.'])`、`(2, err ["缺少参数。请写成“recipe-menu search 词...”。", "运行“recipe-menu --help”查看命令。"])`、`(2, err ['"search" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`、`(2, err ["“search”没有选项“--tag”。它没有自己的选项。", "运行“recipe-menu --help”查看选项。"])`，`search --tag` 给出与第三行相同的结果，因为 `cli` 先检查选项，再检查词的个数。2. `no_data_folder(M)` 和 `no_data_folder(M, ZH)`。3. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`。4. 每一行都给出退出码 0，err 为空，out 上的文字与不指定文件夹的 `--help` 相同，第二行则与 `--help --lang zh` 相同。5. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`。 |
| F10-T16 | 集成 | `recipe-menu search`、`main` | 在 `main` 上为 `search` 运行 v0.1-S23。无论报告什么，`search` 都不写文件。`home` 和当前文件夹下的每个文件和文件夹都保持原有的字节和修改时间，也没有新增条目（2.2 的副作用）。 | 在 `home / "recipe-menu"` 放一份新的示例副本，带有空的 `shopping/`，空的当前文件夹 `tmp_path / "cwd"` 用 `monkeypatch.chdir` 进入。在这些命令之前和之后，用 `tests/f07_support.py` 的 `snapshot` 给 `home` 和当前文件夹拍快照。这些命令都不指定文件夹：`search 番茄`、`search 葱 quick --lang zh`、`search lamb`、`search ""`、`search`、`search 番茄 --tag quick` 和 `search 番茄 --help`。然后做麻婆错误，拍新的快照，运行 `search 番茄` 和 `search lamb`。 | 结果依次是：`FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`，它就是 v0.1-S23 运行的那一行；原型“Two words, in Chinese”的输出；`NONE('No recipe matches "lamb".')`；`(2, err [EMPTY])`；退出码 2 和 F10-T15 里 `search` 的两行；退出码 2 和 F10-T15 里 `search 番茄 --tag quick` 的两行；退出码 0 和帮助。做了麻婆错误之后，两行都给出 `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe))`。命令之后的每个快照都等于命令之前的快照。 |
| F10-T17 | 集成 | `recipe-menu show`、`recipe-menu search`、`main` | F09 的 `UNKNOWN_ID` 的提示写出 `recipe-menu search ID`，这个搜索能够运行。它按名称里的一个词找到菜谱，比如用 `mapo` 找到 `mapo-tofu`；对 ID 的笔误它什么都找不到，因为 ID 不是一个位置（选择 3，F09 设计 2.4）。 | 在 `example` 里：1. `show mapo`，然后 `search mapo`。2. `show mapo --lang zh`，然后 `search mapo --lang zh`。3. `show pork`，然后 `search pork`。4. `show tomato-eggs`，然后 `search tomato-eggs`。 | 1. `(1, err [MAPO])`，其中 `MAPO` 来自 `tests/f09_texts.py`，它的提示写出 `recipe-menu search mapo`。然后是设计 2.2 的示例为 `search mapo` 给出的输出。2. `(1, err [MAPO_ZH])`，然后是 A 块里 `search mapo --lang zh` 的输出。3. `(1, err ['No recipe has the ID "pork". Run "recipe-menu search pork" to find it.'])`，然后是设计的示例为 `search pork` 给出的输出。4. `(1, err ['No recipe has the ID "tomato-eggs". Run "recipe-menu search tomato-eggs" to find it.'])`，然后是 `NONE('No recipe matches "tomato-eggs".')`。 |
| F10-T18 | 集成 | `recipe-menu search`、`main` | `search` 读 `cli` 选出的数据文件夹，用 `cli` 选出的语言写出：先是 `--data`，否则 `RECIPE_MENU_DATA`，否则 `~/recipe-menu`；先是 `--lang`，否则设置里的语言，否则英文。带字节顺序标记和 CRLF 换行的数据文件给出相同的输出，就像 v0.1-S08 对其他命令所期望的那样（2.2 的参数，F05 设计 2.10）。 | B 是 `tmp_path / "One Drive" / "菜谱"` 处的一份新的示例副本，C 是 `tmp_path / "c"` 处的 init 文件夹。E 是 `{"RECIPE_MENU_DATA": str(C)}`。1. 在 B 里 `search 番茄`。2. `search 番茄` 和 `search 番茄 --lang zh`，都不指定文件夹，`environ` 是 E。3. 在 B 里 `search 番茄`，`environ` 是 E。4. 不指定文件夹的 `search 番茄`。5. 在 `home / "recipe-menu"` 处一份带有中文设置的新示例副本里：`search 番茄`、`search 番茄 --lang en` 和 `search 葱 quick`，都不指定文件夹。6. 在一份带有 BOM 和 CRLF 的新示例副本里：`search 番茄` 和 `search 葱 quick --lang zh`。 | 1. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`。2. F 块的两段输出，只找到 `tomato-egg`。3. 1 的输出。4. `no_data_folder(home / "recipe-menu")`。5. `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“番茄”。")`、1 的输出，以及原型“Two words, in Chinese”的输出。6. 1 的输出，以及原型“Two words, in Chinese”的输出。 |
| F10-T19 | 集成 | `python -m recipe_menu` | 真正的入口用真正的命令运行 `search`。无论 Python 给流的是什么编码，它都以 UTF-8 把输出写到 stdout，把退出码 1 或 2 的消息写到 stderr（2.2，F05 设计 2.9）。 | `tests/f05_support.py` 的 `run_module`，与 F09-T26 相同，它把 `HOME` 和 `USERPROFILE` 设成 `tmp_path / "home"`，把 `PYTHONIOENCODING` 设成 `ascii`。用 `example`：1. `search 葱 quick --lang zh --data <example>`。2. `search lamb --lang zh --data <example>`。3. `search "" --data <example>`。4. `search 番茄`，带 `data=example.root`，这会设置 `RECIPE_MENU_DATA`。5. 在 `example` 里做麻婆错误，然后 `search 番茄 --lang zh --data <example>`。 | 1. 退出码 0，stdout 上是原型“Two words, in Chinese”的输出的各行，stderr 为空。2. 退出码 0，stdout 上是 `没有菜谱匹配“lamb”。` 这一行，stderr 为空。3. 退出码 2，stdout 为空，stderr 上是 `EMPTY` 这一行。4. 退出码 0，stdout 上是 `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')` 的各行，stderr 为空。5. 退出码 1，stdout 为空，stderr 上是 `STOP_ZH(recipes/mapo-tofu.toml，食材 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe)` 的三行。 |
| F10-T20 | 集成 | `recipe-menu search`、`main` | 随机的文件夹和词。对任意组合的菜谱、一种或两种语言的名称、按任一名称写出的食材和标签，以及由这些名称的片段组成、大小写随机、两端带空白、重复、为空或哪里都找不到的词，`search` 给出 2.2 的规则给出的各行，两种语言都一样。随机组合能覆盖其他用例没有列出的位置、顺序、宽度和计数行（2.2，选择 3 到 7）。 | `random.Random(20261113)` 构造 100 个文件夹，每个都是一份删掉了七个菜谱文件的新示例副本。除非另有说明，下面每个选择的各个选项机会相等。每个文件夹有 1 到 6 个菜谱，ID 从 `a`、`a-b`、`b`、`egg`、`rice`、`tomato-egg`、`tomato-egg-noodles` 和 `z` 中不重复地抽取。名称有英文文字、中文文字，或者两者都有。英文文字是从 `Tomato`、`egg`、`stir-fry`、`Pork`、`belly`、`Mapo`、`tofu`、`rice` 和 `Noodles` 中取 1 到 3 个词，用空格连接。中文文字是从 番、茄、炒、蛋、红、烧、肉、面、葱 和 米 中取 1 到 4 个字。菜谱有 0 到 3 个不同的目录标签和 0 到 4 种不同的目录食材，各自顺序随机，各自用中文名称或英文名称写出。每种食材的用量是 `适量`。每个菜谱做 2 份，每种语言有一个步骤。然后每个文件夹运行 3 行 `search W... --lang L`，L 随机选出，每行有 1 到 3 个词。每个词是下面之一，机会如下：一个片段（20 分之 13），一个没有名称含有的词（20 分之 2），同一行里前面的某个词（20 分之 4，第一个词则取一个片段），以及一个空词 `""`、`" "` 或 `"\u3000"`（20 分之 1）。片段是从文件夹里一段随机文字的随机位置取出的 1 到 4 个字符，文字更短时就是整段文字。这些文字是文件夹里各菜谱的名称，以及它的菜谱用到的每种食材和每个标签的两个名称。片段里的每个 ASCII 字母再随机成为大写或小写。没有名称含有的词是 `lamb`、`dairy`、`-x`、`"\u200b"` 或 `"\uff34omato"`。片段和没有名称含有的词再以 4 分之 1 的机会在两端加上空白，每一端是空格、制表符、U+00A0 和 U+3000 之一。 | 每一行给出测试按 2.2 的规则从它写出的菜谱构造的结果。某个词的匹配形式为空时，结果是 `(2, err [EMPTY])` 或 `(2, err [EMPTY_ZH])`。否则是退出码 0，err 为空，out 上要么是匹配的菜谱的表格和计数行，要么是没有匹配的那一行。测试用自己的代码构造词和名称的匹配形式：先 `str.strip()`，再把每个 A 到 Z 换成 a 到 z。它不调用 `matching_form`，所以这个用例检查的是规则，而不是规则的一份副本。一行里是 ID、带 `BiText.get` 回退的 L 语言的名称，以及按名称、食材、标签顺序的位置。各行按 ID 的码位顺序排列。测试用 F02 的 `format_table`、不带 `min_widths` 排出表格，用 `comma_list` 连接位置，用 `and_list` 连接计数行里加了引号的词。它把标题、位置和计数行的文字写成字面量，不使用 F10 的任何代码。 |
| F10-T21 | 性能 | `recipe-menu search`、`python -m recipe_menu` | PT01 和 v0.1-S30：`search` 查找每个菜谱都用到的那种食材的名称，在 1 秒内打印出 PT01 数据文件夹的全部 1,000 个菜谱，按从启动到退出的 5 次运行的中位数计（需求 7.1，2.2，选择 10）。 | 第 3 节的 PT01 数据文件夹，在 `tmp_path / "pt01"` 里。先不计时运行一次，再按第 3 节所说计时运行 5 次 `python -m recipe_menu search 食材001 --data <pt01>`。 | 每次运行都以 0 退出，在 stdout 上写出第 3 节 PT01 搜索的 1,003 行，stderr 上什么都不写。5 次计时运行的中位数在 Windows 上小于 1 秒，在 Linux 上小于 3 秒。 |

## 3. 性能用例

PT01 列出的命令里有 `search`（需求 7.1），所以 `recipe-menu search` 有一个用例，F10 的其他接口都没有（R14）。

| 编号 | 指标 | 机器 | 余量 | 基线 |
| --- | --- | --- | --- | --- |
| F10-T21 | PT01：在有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`recipe-menu search` 在 1 秒内完成。按从启动到退出的 5 次运行的中位数计。 | Troy 的电脑：Windows 11，使用 `recipe-menu` 环境的 Python 3.13。这个用例也在 CI 上、在 `.github/workflows/troy-mode.yml` 的 `ubuntu-24.04` 运行器上运行，那不是一台固定的机器（架构第 10 节）。 | Windows 上没有余量：中位数必须小于 1 秒，因为超出 PT01 的余量会放过达不到指标的命令（v0.1 测试方案第 3 节）。Linux 上是 3 秒，与 F07-T25 和 F09-T28 相同，使这个用例在速度未知的运行器上也成立，同时仍然能抓到慢了几倍的情况。 | 首次运行。在 Troy 的电脑上，架构师的模型运行 `search 食材001` 的中位数是 0.789 秒（0.785 到 0.802 秒），同一轮里 `list` 是 0.794 秒（0.791 到 0.794 秒）（设计第 4 节）。F09 的实现 PR 记录的 `list` 中位数是 0.789 秒。模型不是实现，所以由 F10 的实现 PR 记录第一个基线。 |

**哪个系统是 Troy 的电脑。** CI 只在 Linux 上运行，只有 Troy 的电脑在 Windows 上运行测试。所以这个用例用 `tests/pt01_support.py` 的 `time_limit` 的上限：`sys.platform == "win32"` 时为 1 秒，否则为 3 秒，与 F07-T25 和 F09-T28 相同。在 Windows 上增加 CI 任务，会先改动这份方案。

**PT01 数据文件夹。** 由 `tests/pt01_support.py` 的 `make_pt01` 写出，与 F07-T25 和 F09-T28 相同，形状就是 v0.1 测试方案给出的那样。F10 不改动这个生成器。每个菜谱的第一行食材写的是 `食材001`，即 `Ingredient 001` 的中文名称。文件夹里没有别的名称含有 `食材001`：其他食材是 `食材002` 到 `食材300`，菜谱是 `Recipe 0001` 到 `Recipe 1000` 和 `菜谱0001` 到 `菜谱1000`，标签就是示例的那些。所以 `search 食材001` 匹配每个菜谱，而且只在 `ingredient` 里匹配。

**计时运行。** 这个用例使用 F09 在 `tests/pt01_support.py` 里加入的通用计时运行：`command_run`、`command_runs`、`record_times` 和 `time_limit`，它们保持原来的名字和行为。

**预期输出。** `tests/pt01_support.py` 新增 `pt01_search`，它按生成器的规则用 f-string 构造结果，不用 F02 的 `format_table`。PT01 搜索有 1,003 行。第 1 行是 `ID            Name          Matched in`。对 1 到 1,000 中的每个 k，第 k + 1 行是 ID `recipe-NNNN`、三个空格、名称 `Recipe NNNN`、三个空格和 `ingredient`，所以菜谱 1 的行是 `recipe-0001   Recipe 0001   ingredient`。然后是一个空行和 `1000 recipes match "食材001".`。

**用例的步骤。**

1. 生成文件夹。
2. 不计时启动一次命令，像第 3 步那样检查它的结果。Windows 第一次读这 1,053 个新文件时很慢（F07 测试方案第 3 节），而 Troy 自己的数据文件夹不会每次运行都付出这个代价。
3. 用 `command_runs` 把同一个命令启动 5 次，每次都是新进程：`sys.executable -m recipe_menu`，在 `tmp_path` 里运行，`HOME` 和 `USERPROFILE` 设成一个空的主文件夹，没有 `RECIPE_MENU_DATA`。每次运行都必须以 0 退出，stdout 正好是预期的输出，stderr 为空。不满足这些的运行会让用例失败，无论它用了多少时间。
4. 取 5 次时间的中位数，与这个系统的上限比较。
5. 用 `record_property` 记录 5 次时间、中位数和范围，使 JUnit 报告保存它们，供下次比较。

**它怎样在 Troy 的电脑上运行。** 这个用例在 `tests/` 里，所以每次在 Troy 的电脑上完整运行测试时都会运行，主会话为每个 PR 用 `recipe-menu` 环境的 Python 启动这样的运行。在 F10 的实现 PR 里，主会话还在没有其他测试运行、构建或安装进行时，用 `python -m pytest tests/test_f10_performance.py --junitxml=reports/pt01-f10.xml` 单独运行它。PR 描述报告中位数和范围，那次运行就是基线。如果 `search` 接近上限，设计选择 10 给出第一步：在实现 PR 之前，用一个 `[refactor]` PR 让 `Message.render` 只解析每个模板一次。发布测试在同一台机器上运行 v0.1-S30。

**基准测试检查表。** 这个用例这样回答 `benchmark-checklist` 的问题：

- 限制因素：设计选择 10 和第 4 节给出了它。`search` 读 `list` 读的文件，所以读 1,000 个菜谱文件限制它的速度，和 `list`、`check` 一样。对一个词，匹配另外要构造约 2,600 个匹配形式，做约 2,600 次 `in` 检查和 14,000 次查找，表格约有 32,000 个字符。架构师的模型里 `search` 和 `list` 用的时间差不多。这个用例不做性能剖析，因为剖析会拖慢运行。`[refactor]` PR 会做剖析。
- 调优：每次运行都是一个新的 Python 进程，用已安装的包及其编译文件，没有覆盖率工具和调试器，与 Troy 的运行方式相同。第 2 步的不计时运行已经把文件读过一次。coverage.py 只测量测试进程，所以 CI 里的 `coverage run -m pytest` 不会拖慢计时的进程。
- 极限：`search` 通过管道写出大约 40 KB，1,053 个文件大约 2 MB，磁盘几毫秒就能读完。所以测得的时间是 Python 的工作。
- 错误：第 2 和 3 步检查每次运行的退出码、完整的 stdout 和空的 stderr。
- 可重复性：5 次计时运行，记录中位数和范围。与基线的差距小于基线各次运行的范围时，就不算可测量的变化。
- 相关性：这个用例为从启动到退出的整个命令计时，这正是 Troy 等待的时间。每个菜谱都含有的词让 `search` 给 1,000 个菜谱各写一行，这是 `search` 能写出的最多的行。每多一个词，大约多 2,600 次 `in` 检查（设计选择 10），只占读文件时间的一小部分。
- 工作确实发生了：1,000 行都匹配在 `ingredient`，加上计数行，表明 `search` 读了并匹配了每个菜谱。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| 单独的 `SEARCH_COMMAND` 字段，`recipe_menu.commands.search` 的 `__all__` 列出的名称，作为 `search/messages.py` 里常量的消息，以及单独的 `matching_form`。 | mock 完整地声明了它们，并导出了 F03 已经能用的函数，所以只测它们的测试会在 mock 上通过（R09）。F10-T01 在一次运行旁边检查这些字段，F10-T07 在用到 `matching_form` 的搜索旁边检查它，各用例通过输出检查每段文字。文字放在哪里由代码审查检查。 |
| `search` 只导入 `app`、`lang`、`text`、`datafile`、`catalog` 和 `recipes`，不从 `browse` 导入任何东西。 | R07。CI 里的依赖检查器把每个导入与架构第 3 节的表格比较。那张表格允许 `search` 导入的模块比它用到的多，所以设计第 2 节和选择 2 里更短的列表由代码审查检查。 |
| `search` 在读完最后一个文件之后一次写出它的输出，不保存状态，每次运行只构造一次目录名称的匹配形式。 | 没有接口能显示文字何时到达流，也不能显示一个匹配形式构造了几次。每个期望退出码 1 或 2 的用例都检查输出流为空，F10-T14 检查每个文件读了几次，F10-T01 在同一个文件夹上把 `run` 运行了多次，F10-T21 为整个命令计时。其余由代码审查检查。 |
| 用超出 2.1 约束的 `Arguments` 调用 `run`：没有值、有选项，或者有以 `--` 开头的值。 | `cli` 从不传入它们（F05 设计 2.10）。F10-T15 检查 `cli` 拒绝每一行这样的命令。 |
| 以 Windows 设备名命名的菜谱文件，以及系统拒绝读取的列出或文件。 | Windows 拒绝创建前者，F04-T12 只在 Linux 上检查它。读取函数把后者变成问题，F04-T36 和 F07-T13 测试它们。F10-T13 检查每个读取函数的第一个错误让 `search` 停下，无论是什么错误。 |
| 新进程的命令行里带换行或不可见字符的词。 | 这样的词怎样到达，由每个系统给新进程命令行定的规则决定，`main` 收到的就是到达时的样子。F10-T07、F10-T10 和 F10-T11 把这样的词传给 `main`。 |
| 也匹配 ID 的搜索。 | 设计没有把 ID 作为一个位置，设计第 4 节里架构师的备注说，第四个位置需要走需求变更流程。F10-T06 和 F10-T17 检查 ID 不算数。 |
| `search` 运行期间的 Ctrl+C。 | `cli` 对每个命令都给出退出码 130（F05 设计 2.10），F05-T41 测试它。`search` 不写文件，所以 Ctrl+C 不留下任何东西。 |
| `Message.render` 每次调用都解析它的占位符，以及选择 10 的 `[refactor]` PR。 | 这是 `text` 的内部改动，由架构师决定。F10-T21 为 `search` 计时，能显示这个改动。 |
| v0.1 的八个命令都在时的帮助。 | F05-T45 用替身命令检查那些行，v0.1-S19 用真正的命令检查它们。F10-T01 检查 `search` 的那一行，所用的形式在 F11 到 F13 加入它们的命令之后仍然成立。 |
| Windows Terminal 里的中文输出。 | CI 机器没有 Windows 控制台（架构第 10 节），所以 v0.1-S25 让 Troy 检查。F10-T19 检查 `python -m recipe_menu` 用 UTF-8 写出中文输出。 |
| 文档注释只用英文。 | R05。troy-check 拒绝文档注释里的中文字符。 |
| 发布测试里的 v0.1-S11、v0.1-S23 和 v0.1-S30。 | 它们是 `version-tests/` 里的版本测试，由版本测试 PR 加入（TE5）。F10-T04 和 F10-T16 在 `main` 上运行同样的步骤，F10-T21 在同一类文件夹上为同样的命令计时，每次测试运行都这样。 |

## 5. 与接口设计师的对齐记录

无。

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-13 | 初稿。 |
| 1.0 | 2026-11-14 | Troy 批准。 |
