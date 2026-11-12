---
troy-doc: "F05-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-12"
status: "Troy 已于 2026-11-12 批准"
mirror-of: "design.md"
---

# F05 命令行和设置：接口设计

## 1. 功能

- 编号和名称：F05 命令行和设置
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：F02

## 2. 接口

F05 构建三个模块（[架构 3](../../architecture.zh-CN.md#3-模块)）。领域层模块 `settings` 读取设置文件。应用层模块 `app` 存放连接 `cli` 和各个命令的值。入口模块 `cli` 运行 `recipe-menu` 命令：它解析命令行，显示帮助和版本，找到数据文件夹，选定语言，运行一个命令，并以这个命令的退出码退出。各模块导出下面这些名称，每个模块的 `__init__.py` 在 `__all__` 里列出它们：

- `recipe_menu.settings`：`Meal`、`Settings` 和 `read_settings`（2.1 到 2.3）。
- `recipe_menu.app`：`Argument`、`Arguments`、`Command`、`Context`、`FolderUse`、`UsageError`、`first_error`、`problem_lines` 和 `stop_at_error`（2.4 到 2.8）。
- `recipe_menu.cli`：`main`（2.9），它运行 2.10 的命令行。
- `recipe_menu`：`__version__`（2.11），放在 `src/recipe_menu/__init__.py` 里；架构 3 把这个文件交给 `cli`。

每个模块把自己的提示放在自己的 `messages.py` 里，只在模块内部使用（架构 8）。其他文件由开发工程师决定，只有后续功能要依赖的三个文件除外。命令列表是 `src/recipe_menu/cli/_commands.py` 里的 `COMMANDS`（2.9）。`src/recipe_menu/__main__.py` 为 `python -m recipe_menu` 运行 `main`。`src/recipe_menu/commands/__init__.py` 只有它的文档注释，所以引入一个命令模块时不会引入别的命令模块。F05 还给 `datafile` 加入 `read_servings`、`MIN_SERVINGS` 和 `MAX_SERVINGS`，`recipes` 改用它们读取份数（第 3 节）。F05 原型 `docs/prototypes/F05-command-line.md` 展示了帮助、语言、数据文件夹和各种错误。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F05 提供的接口 |
| --- | --- |
| 提供 `recipe-menu` 命令及其子命令。 | `main`（2.9）和命令行（2.10）。每个命令模块用 `Command`（2.5）描述自己的命令，并把它们加进 `COMMANDS`。控制台脚本 `recipe-menu` 和 `python -m recipe_menu` 都调用 `main`。 |
| 提供选项 `--lang`、`--data`、`--help` 和 `--version`。 | 2.10 的全局选项、两种语言的帮助，以及 `__version__`（2.11）。 |
| 找到数据文件夹。 | 2.10 的规则 4：先看 `--data`，再看 `RECIPE_MENU_DATA`，最后用 `~/recipe-menu`（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)、Q15）。 |
| 读取设置：语言、餐次和默认份数。 | `read_settings`（2.3），它给出一个带有 `Meal` 值（2.1）的 `Settings`（2.2）。 |
| 命令先用 `--lang`，没有时用设置里的语言，再没有时用英文（需求 3）。 | 2.10 的第 3 步，用 F02 的 `choose_lang`。`Context.lang`（2.4）把语言带给命令。 |
| 每个命令都以第 3 节的退出码结束：成功为 0，数据有错或缺少文件为 1，命令行写错为 2。 | 2.10 的退出码，退出码 2 用的 `UsageError`（2.7），以及数据文件出错时用的 `stop_at_error`（2.8）。 |

下面每个接口都遵守这些规则：

- `settings` 在包内只引用 `lang`、`text` 和 `datafile`。`app` 只引用 `lang`、`text`、`datafile` 和 `settings`。`cli` 引用 `lang`、`text`、`datafile`、`settings`、`app` 和各个命令模块（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- 只有 `cli` 接触外部世界：命令行参数、环境变量、主文件夹、当前文件夹、今天的日期和控制台的流（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。`settings` 只通过 `read_toml` 读取它的文件。`app` 只写入它拿到的 `Context` 里的流。没有接口保存状态。
- `read_settings` 遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。下面各个“错误”表里的异常都来自错误的调用，也就是 bug。`UsageError` 是唯一一个有意跨越模块的异常（[架构 5.2](../../architecture.zh-CN.md#52-值)）。
- 每个值都是带 `slots=True` 的冻结 dataclass 或者枚举，其中的集合用元组（架构 8）。`UsageError` 是异常，所以它是一个单独的类（2.7）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F05 的接口都没有性能指标。PT01 计时的每个命令都要付出 F05 的启动时间：Python 自己的启动、各模块的引入、对参数的一次扫描、对数据文件夹的一次查看，以及读取一个只有几行的设置文件（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。所以 `cli` 启动时只引入 `settings`、`app` 和各个命令模块，以及它们引入的模块。它不引入 `argparse`，也不引入 `importlib.metadata`（选择 12）。`main` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。每条后面括号里的小节给出它的规则。

1. **设置文件。** 每个键都可以不写，不写时用[架构 5.2](../../architecture.zh-CN.md#52-值) 的默认值：没有语言、午餐和晚餐、2 份（2.3）。文件本身必须存在，和每个数据文件一样。缺少 `settings.toml` 时得到 `read_toml` 的错误 `FILE_MISSING`，它让命令以退出码 1 停下，这符合需求 3 对缺少文件的规定。`init` 会写出这个文件（F08）。未知的键是错误，和其他数据文件一样。
2. **餐次。** `meals` 用文件里的词写餐次：`breakfast`、`lunch` 和 `dinner`，它们也是菜单文件里的键（架构 8）。不管文件按什么顺序列出，`read_settings` 都按一天里的顺序保存它们，并且每个只保存一次，和 `read_recipe` 对标签只保存一次一样（2.3）。空列表是错误，因为菜单至少需要一个餐次。
3. **份数。** 数据文件里的每个份数都遵守同一条规则：1 到 100 之间的整数，只有不超过 15 位时才在提示里显示（F04 设计，选择 2）。这条规则放在 `datafile` 里，就是 `read_servings`、`MIN_SERVINGS` 和 `MAX_SERVINGS`（3.1），因为 `recipes`、`settings` 和 `menus` 都要读取份数，而 `settings` 和 `menus` 不能引用 `recipes`（架构 3）。三条份数提示随它一起从 `recipes` 移过来，文字不变。换一种做法，`settings` 会复制这三条提示，F06 又要复制或引用它们，这个范围就会出现在四个地方。
4. **出错的设置文件。** 文件有错误时，`read_settings` 不给出 `Settings`，和 `read_recipe` 不给出菜谱一样（2.3）。所以出错文件里的语言不算数，命令使用 `--lang` 的语言，没有时用英文。
5. **先读设置，再报告命令行的错误。** `cli` 在报告用法错误之前读取设置，所以在写了 `language = "zh"` 的数据文件夹里，`recipe-menu cook` 用中文报告错误（2.10）。代价是多读一个很小的文件。
6. **启动时的数据文件夹和设置。** 每个 `Command` 用它的 `FolderUse` 说明 `cli` 在运行它之前检查什么（2.5）。对大多数命令，数据文件夹不存在或设置有错误时，命令在运行前就停下。`check` 自己报告设置的问题，所以这些问题不让它停下。`init` 会创建文件夹，所以两者都不让它停下。这样需要数据文件夹的各个命令共用一次检查和一条提示。架构 6 说由命令检查数据文件夹是否存在，所以它的这一行要改（决定 B）。
7. **`Context.settings` 总是一个 `Settings`**（2.4）。`FolderUse.READ` 的命令拿到文件里的设置。文件夹或其中的设置读不了时，`check` 和 `init` 拿到 `Settings()`。所以没有命令需要为缺少设置写一个测试走不到的分支。架构 5.2 写的是“数据文件夹有设置时，就是这些设置”；没有设置时，由默认值代替。
8. **遇到错误停下的命令**先写出问题，再写 `RUN_CHECK`，和架构 6 以及 F11 原型“A menu with a mistake”一样（2.8）。在产品经理加上第三行之前，F05 原型“A broken settings file”只展示前两行（决定 D）。v0.1-S22 期望提示“以”这两行“开头”，所以加上第三行后它仍然成立。
9. **用法错误自己指定提示行。** `UsageError` 带着跟在提示后面的那一行，比如 `RUN_HELP_FOR_OPTIONS`，或者 `None`（2.7）。解析器的大多数错误都指定 F02 两条 `--help` 提示行中的一条。提示本身已经说明了该怎么写的错误指定 `None`。例子有命令自己的选项的 `--tag needs a value.`（帮助不列出这些选项，见 2.10），以及 F11 原型里的 `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".`。Troy 接受了对架构 6 的这处修改（决定 A）。
10. **解析器**遵守 ADR-0005（2.10）。选项可以出现在命令行的任何位置。`--help` 和 `--version` 是开关，其他每个选项都把下一个参数当作它的值。不接受 `--lang=zh` 和 `-l zh` 这样的写法，也不接受缩写。一个命令最多有一个参数，这个参数可以是可选的，也可以重复，因为原型里的每个命令最多有一个参数。带值的选项写两次是错误，因为两个值可能不同。空值算作没有值。开关可以重复，因为第二个 `--help` 或 `--version` 不改变任何东西。只有第一个有值的 `--lang` 和第一个有值的 `--data` 决定语言和数据文件夹。所以 `recipe-menu list --lang --lang zh` 用中文报告缺少的值。
11. **帮助**先按 `COMMANDS` 的顺序列出命令，再列出四个全局选项，和原型一样（2.10）。它的第一列在两种语言里宽度相同：取两种语言里最宽的命令或选项的宽度。所以英文帮助和中文帮助在同一列对齐（F02 设计 2.9）。帮助不列出命令自己的选项，比如 `--tag`，因为原型没有列出。所以 `UNKNOWN_OPTION` 写出命令自己的选项，命令自己的选项的其他错误不指定提示行（2.10）。
12. **版本**是 `recipe_menu.__version__`，一个测试保证它等于 `pyproject.toml` 里的版本（2.11）。如果用 `importlib.metadata` 读取已安装包的版本，每次启动都要引入很多模块。
13. **数据文件夹**是第一个有值的 `--data` 指定的文件夹；没有时，如果设置了 `RECIPE_MENU_DATA` 而且它不为空，就是它指定的文件夹；否则是主文件夹里的 `recipe-menu`（2.10）。`cli` 把这两个值开头的 `~` 换成主文件夹。Windows PowerShell 5.1 把 `~` 原样传给外部命令，所以不做这个替换的话，`recipe-menu init --data ~\OneDrive\recipe-menu` 会在当前文件夹里创建一个名为 `~` 的文件夹。`cli` 不展开其他写法，比如 `~troy` 或变量。它从当前文件夹出发把相对路径变成绝对路径，所以每条提示都用完整路径写出文件夹（架构 6）。

Troy 在 2026-11-12 对以下四项作出决定，每一项都接受了推荐。这个 PR 不改动 `docs/architecture.md`，也不改动任何原型。架构师之后用一个 `[docs]` PR 落实 A 到 C，产品经理用一个文档 PR 落实 D。

- **A. 用法错误的提示行。** Troy 选择了方案 1。架构 6 说退出码为 2 的错误显示“提示，然后一行指向 `recipe-menu --help`”。F11 原型“A week without a menu”显示的 `"2026-W99" is not a week. ...` 后面没有这一行，v0.1-S15 期望的也是这个输出。所以 `UsageError` 自己指定提示行，提示本身已经说明怎么写时指定 `None`，和 2.7 一样。F11 原型和 v0.1-S15 保持不变。理由：提示已经说明了怎么写，后面再加一行就是重复。而且这处修改只改架构里的一行，不改任何需求。架构师的 `[docs]` PR 修改架构 6 的这一行和架构 5.2 的 `UsageError` 一行。
- **B. 由谁检查数据文件夹是否存在。** Troy 接受了推荐。只要命令的 `FolderUse` 要求，就由 `cli` 检查数据文件夹是否存在（选择 6），提示和退出码和架构 6 一样。理由：`cli` 启动时已经要查看文件夹来读取设置（选择 5），所以需要数据文件夹的各个命令共用一次检查和一条提示。架构 6 的“缺数据文件夹、菜单或菜谱”一行写的是“由谁捕获：命令自己”。同一个 `[docs]` PR 把它改为数据文件夹由 `cli` 检查，菜单或菜谱由命令自己检查。
- **C. 语法错误对应的异常**，这是 F03 设计审查时留下的问题。Troy 接受了推荐。架构 6 的“语法错误，或者文件不是 UTF-8”一行和 ADR-0002 写的是 `tomllib.TOMLDecodeError` 和 `UnicodeDecodeError`。对这样的文件，`tomllib` 还会抛出普通的 `ValueError` 和 `RecursionError`，`read_toml` 也捕获它们（F03 设计 2.3）。同一个 `[docs]` PR 在两份文档里写上这两个异常。理由：这样两份文档就写出了 `read_toml` 捕获的每个异常，而且这处修改只改措辞。
- **D. F05 原型“A broken settings file”。** Troy 接受了推荐。原型加上第三行 `Run "recipe-menu check" to see every problem.`，让它展示完整的提示（选择 8）。无论加不加，v0.1-S22 都成立。由产品经理在一个文档 PR 里修改。

以下后续功能打算调用 F05 的接口。具体细节由它们自己的设计决定。

- F07 到 F16 的每个命令模块为它的每个命令导出一个 `Command`，比如 `browse` 导出的 `LIST_COMMAND` 和 `SHOW_COMMAND`。它的 mock PR 把每个命令加进 `COMMANDS`，放在帮助里的顺序位置上：init、check、list、show、search、menu new、menu show 和 shop（架构 4）。menu suggest、add 和 edit 的位置由 F14 到 F16 选定。
- 命令的 `run` 拿到 `Context` 和 `Arguments`。它把输出写到 `context.out`，把以退出码 1 结束它的提示写到 `context.err`，并返回 0 或 1。参数值写错时，它在写出任何输出之前抛出 `UsageError`，`cli` 以 2 退出。它用 `first_error` 和 `stop_at_error` 在数据文件的第一个错误处停下。它从不打印、不退出，也不读环境变量（架构 8）。
- F06 从 `Settings` 读取餐次和默认份数。它用 `Meal.label` 在位置里写出餐次，比如“Monday dinner”和“周一晚餐”。它用 `key in Meal` 检查菜单文件里的餐次键，用 `Meal(key)` 得到餐次。它用 `read_servings` 读取一道菜的份数。
- F07 的 `check` 使用 `FolderUse.CHECK`。它自己调用 `read_settings` 来报告设置的问题，并用 `problem_lines` 按 F07 原型的缩进写出每个问题。设置有错误时，F07 决定怎样读取周菜单，比如用这时存放着 `Settings()` 的 `context.settings`。
- F08 的 `init` 使用 `FolderUse.CREATE`。它把 `context.lang` 的语言写进设置。它可以用 `Settings()`、`Meal.label` 和 `and_list` 描述它写出的设置，比如“English, lunch and dinner, 2 servings per dish”。
- F09 的 `list` 声明选项 `--tag`，它的 `show` 声明参数 `ID` 和选项 `--servings`。`show` 用 `MIN_SERVINGS` 和 `MAX_SERVINGS` 检查 `--servings` 的值，它的 `UsageError` 把这个值按你输入的文字显示，从不显示成 `int`，所以没有值会碰到 F02 的 4,300 位限制。在 F05 原型“The language from the settings”里，`list --tag 素` 的两个表格保持整个列表的列宽，而 `format_table` 只有在给了 `min_widths` 时才会这样。F09 的设计决定怎样得到这些列宽。
- F10 的 `search` 用 `repeats=True` 声明参数 `WORD`，所以没有写词的 search 由 `cli` 报告。
- F11 的 `menu new` 和 `menu show` 以及 F13 的 `shop` 声明可选参数 `WEEK`，并用 `context.today` 把 `this` 和 `next` 换算成周。F11 用 `Meal.heading` 写出各列顶部的餐次。按决定 A，F11 对写错的周不指定提示行。
- 在 v0.2 里，F14 给 `Context` 和 `main` 加入随机数生成器，F15 加入输入流（架构 5.2）。F14 和 F16 给 `Settings` 和 `read_settings` 加入它们的键（架构 5.1）。

troy-mode 的流程每个阶段一个 PR，每个 PR 在自己的分支上，比如 `troy-mode/f05-3-mock`。所以 F05 有一个 mock PR 和一个实现 PR。每个 PR 改动的文件都超过 R03 的 5 个，所以每个 PR 的说明都要写明软限制的理由（R03）：测试通过 `main` 用到 `settings`、`app` 和 `cli`，所以每个阶段要一次带上这三个模块。F04 的 mock PR 和实现 PR 也写了同类的理由。

- mock（PR 3）包含 `settings` 和 `datafile` 新增的部分、`app`，以及 `cli` 和 `__main__.py`、`commands/__init__.py`、`__version__`。mock 定义每个常量，比如 `Meal` 的成员、`Settings` 的默认值和每条提示，这样各模块都能引入。在实现之前，`recipes` 保留它自己的份数检查。所以 F04 的测试一直通过，而 F05 的每个新测试都能在 mock 上失败（R09）。
- 测试（PR 4）通过 `main` 的参数 `commands` 传入它们自己的命令，因为 F07 之前没有真正的命令。
- 实现（PR 5）包含 `read_servings` 和改用它的 `recipes`、`settings`、`app`，`cli` 的解析器、帮助和 `main`，入口文件，以及控制台脚本。
- 实现 PR 按架构 2 的写法，把控制台脚本 `recipe-menu = "recipe_menu.cli:main"` 加进 `pyproject.toml` 的 `[project.scripts]`，这样安装出来的命令从它的第一次提交起就运行能用的代码。`pyproject.toml` 是依赖文件，所以 troy-check 在那个 PR 里按 R16 发出警告。这个脚本不加入第三方依赖。所以架构师确认 `pyproject.toml` 只多了 `[project.scripts]` 下的 `recipe-menu = "recipe_menu.cli:main"` 之后，批准这个警告。没有测试需要这个脚本：测试调用 `main`，计时测试和版本测试运行 `python -m recipe_menu`。

### 2.1 `Meal`

- 模块：settings
- 功能：一天里的餐次，按一天里的顺序排列，带有两种语言的名称（[架构 5.2](../../architecture.zh-CN.md#52-值)、ADR-0004）。每个成员的值就是设置和菜单文件里用的那个词。

签名：

```python
class Meal(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

    @property
    def label(self) -> BiText: ...

    @property
    def heading(self) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `value` | `str` | 文件里的词，供 `Meal(value)` 使用。 | `breakfast`、`lunch` 或 `dinner`，写法与这里完全相同。 |

- 返回值：一个 `Meal`。
  - `list(Meal)` 按一天里的顺序给出成员：`BREAKFAST`、`LUNCH` 和 `DINNER`。
  - `label` 给出用在句子或位置里的餐次名称，`heading` 给出用在列顶部的餐次名称。下表列出它们。
  - `Meal(value)` 给出值为 `value` 的成员。`value in Meal` 判断一个词是不是餐次，不会抛异常（Python 3.12 及以后）。
  - `Meal` 是 `str`，所以 `sorted` 按词排序餐次，这不是一天里的顺序。要用 `key=list(Meal).index` 排序。
  - F02 的 `Message.render` 拒绝把枚举成员当作值（F02 设计 2.3），所以提示通过 `label` 或 `heading` 显示餐次。

| 成员 | 值 | `label`，英文 | `label`，中文 | `heading`，英文 | `heading`，中文 |
| --- | --- | --- | --- | --- | --- |
| `BREAKFAST` | `breakfast` | `breakfast` | `早餐` | `Breakfast` | `早餐` |
| `LUNCH` | `lunch` | `lunch` | `午餐` | `Lunch` | `午餐` |
| `DINNER` | `dinner` | `dinner` | `晚餐` | `Dinner` | `晚餐` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `Meal(value)` 拿到的词不是任何成员的值，比如 `supper` 或 `Lunch`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import BiText
from recipe_menu.settings import Meal
from recipe_menu.text import and_list

assert list(Meal) == [Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER]
assert Meal("lunch") is Meal.LUNCH
assert "dinner" in Meal
assert "supper" not in Meal
assert Meal.DINNER.label == BiText("dinner", "晚餐")
assert Meal.DINNER.heading == BiText("Dinner", "晚餐")
meals = and_list(meal.label for meal in (Meal.LUNCH, Meal.DINNER))
assert meals == BiText("lunch and dinner", "午餐和晚餐")
assert sorted(Meal) == [Meal.BREAKFAST, Meal.DINNER, Meal.LUNCH]
day_order = sorted([Meal.DINNER, Meal.BREAKFAST], key=list(Meal).index)
assert day_order == [Meal.BREAKFAST, Meal.DINNER]

Meal("supper")  # raises ValueError
Meal("Lunch")  # raises ValueError
```

### 2.2 `Settings`

- 模块：settings
- 功能：一个数据文件夹的设置：语言、每天的餐次，以及没写份数的菜所用的份数（[架构 5.2](../../architecture.zh-CN.md#52-值)）。`Settings()` 给出默认值。在 v0.2 里，F14 和 F16 会加入字段。

签名：

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `language` | `Lang` 或 `None` | 命令行没有 `--lang` 时命令使用的语言。 | 设置没有写语言时为 `None`。这时命令使用英文。 |
| `meals` | `Meal` 值的元组 | 周菜单里每天的餐次。 | 1 到 3 个餐次，按 `Meal` 的顺序排列，每个只出现一次。 |
| `servings` | `int` | 没写份数的菜所用的份数（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)、Q17）。 | 从 `MIN_SERVINGS` 到 `MAX_SERVINGS`，也就是 1 到 100（3.1）。不能是 `bool`。 |

- 返回值：一个 `Settings`。三个字段都相等时，两个设置相等。`Settings` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `language` 既不是 `Lang` 也不是 `None`，比如文字 `"zh"`。 |
| `TypeError` | `meals` 不是元组，或者其中有一项不是 `Meal`。 |
| `ValueError` | `meals` 为空，有一个餐次出现两次，或者没有按 `Meal` 的顺序排列。 |
| `TypeError` | `servings` 不是 `int`，或者是 `bool`。 |
| `ValueError` | `servings` 小于 1 或大于 100。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.language is None
assert defaults.meals == (Meal.LUNCH, Meal.DINNER)
assert defaults.servings == 2
every_meal = Settings(Lang.ZH, tuple(Meal), 3)
assert every_meal.meals == (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER)
assert Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2) == Settings(Lang.EN)

Settings(meals=())  # raises ValueError
Settings(meals=(Meal.DINNER, Meal.LUNCH))  # raises ValueError
Settings(meals=(Meal.LUNCH, Meal.LUNCH))  # raises ValueError
Settings(servings=0)  # raises ValueError
Settings(servings=101)  # raises ValueError
Settings(servings=True)  # raises TypeError
Settings(language="zh")  # raises TypeError
Settings(meals=[Meal.LUNCH])  # raises TypeError
```

### 2.3 `read_settings`

- 模块：settings
- 功能：把 `settings.toml` 读成一个 `Settings`，并报告每个问题及其位置（[需求 4](../../requirements.zh-CN.md#4-功能点)，F05）。`cli` 在启动时调用它（2.10），`check` 调用它来报告设置的问题（F07）。

签名：

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：一个二元组 `(settings, problems)`。
  - `problems` 里有错误时，`settings` 为 `None`。否则它是一个 `Settings`，文件里没写的每个键都取默认值。
  - 文件不存在、读不了、不是 UTF-8 或不是有效的 TOML 时，`problems` 只包含 `read_toml` 给出的那个问题（F03 设计 2.3）。否则它按顺序包含下面各项检查的问题。每个问题的文件都是 `settings.toml`。

文件的格式就是 `docs/prototypes/example-data.md` 里的格式：

```toml
# recipe-menu settings
language = "en"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
```

每个键都可以不写：

| 键 | 值 | 没写这个键时的默认值 |
| --- | --- | --- |
| `language` | `"en"` 或 `"zh"`。 | 没有语言，所以除非命令行有 `--lang`，命令使用英文。 |
| `meals` | 由 `"breakfast"`、`"lunch"` 和 `"dinner"` 组成的列表，顺序不限。 | 午餐和晚餐。 |
| `servings` | 1 到 100 之间的整数。 | 2。 |

问题的位置如下。N 从 1 开始数 `meals` 的各项，跳过的项也算在内。

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| `language` | `language` | `语言` |
| `meals` | `meals` | `餐次` |
| `meals` 的第 N 项 | `meal N` | `餐次 N` |
| `servings` | `servings` | `份数` |

`read_settings` 做以下检查。没写的键不产生问题，也没有检查给出警告。

| 部分 | 检查 | 问题 | 位置 | 类型 |
| --- | --- | --- | --- | --- |
| `language` | 值不是文字。 | `NOT_A_TEXT` | `language` | 错误 |
| `language` | 文字为空或只有空白字符。 | `EMPTY_TEXT` | `language` | 错误 |
| `language` | 去掉两端的空白后，文字既不是 `en` 也不是 `zh`，比如 `fr` 或 `EN`。 | `LANGUAGE_NOT_EN_OR_ZH` | `language` | 错误 |
| `meals` | 值不是列表。 | `NOT_A_LIST` | `meals` | 错误 |
| `meals` 的一项 | 这一项不是文字。 | `ITEM_NOT_A_TEXT` | `meal N` | 错误 |
| `meals` 的一项 | 这一项为空或只有空白字符。 | `EMPTY_ITEM` | `meal N` | 错误 |
| `meals` 的一项 | 去掉两端的空白后，这一项不是任何 `Meal` 的值，比如 `supper` 或 `Lunch`。 | `UNKNOWN_MEAL` | `meals` | 错误 |
| `meals` 的一项 | 它写的餐次前面已经写过。 | 无。设置只保存这个餐次一次。 | 无 | 无 |
| `meals` | 值是空列表 `[]`。 | `NO_MEALS` | `meals` | 错误 |
| `servings` | 值不符合 `read_servings` 的规则（3.1）。 | `SERVINGS_NOT_A_NUMBER`、`SERVINGS_TOO_FEW` 或 `SERVINGS_TOO_MANY` | `servings` | 错误 |
| 文件顶层 | `language`、`meals` 和 `servings` 以外的键。 | `UNKNOWN_KEY` | 无 | 错误 |

问题按这个顺序排列：先是 `language` 的问题，然后是 `meals` 的问题，然后是 `servings` 的问题，最后按文件里的顺序排列未知的键。在 `meals` 里，列表本身的问题在前，然后按顺序是各项的问题，最后是 `NO_MEALS`。`UNKNOWN_MEAL` 的位置是 `meals`，和 F05 原型一样，因为提示里已经写出了这个餐次。不管文件按什么顺序列出餐次，设置都按 `Meal` 的顺序保存它们。

`read_settings` 用 `datafile` 的提示报告文件结构的问题（F03 设计 2.10）。`UNKNOWN_KEY` 使用三个键的形式。下面是 `settings` 的提示，2.1 的餐次名称也和它们放在一起：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `LANGUAGE`、`MEALS`、`MEAL_N` 和 `SERVINGS` | 位置表里的位置，N 写成 `{number}`。 | 位置表里的位置，N 写成 `{number}`。 |
| `LANGUAGE_NOT_EN_OR_ZH` | `The language must be "en" or "zh", not "{language}".` | `语言必须是“en”或“zh”，不能是“{language}”。` |
| `UNKNOWN_MEAL` | `Unknown meal "{meal}". The meals are {meals}.` | `未知餐次“{meal}”。可用的餐次：{meals}。` |
| `NO_MEALS` | `"meals" must name at least one meal. The meals are {meals}.` | `“meals”至少要写上一个餐次。可用的餐次：{meals}。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `key` | 在 `NOT_A_TEXT` 和 `EMPTY_TEXT` 里是 `language`，在 `NOT_A_LIST` 里是 `meals`，在 `UNKNOWN_KEY` 里是那个未知的键。 |
| `keys` | `and_list(["language", "meals", "servings"])`：“language, meals, and servings”和“language、meals 和 servings”。 |
| `language` | 去掉两端空白后的 `language` 文字。 |
| `meal` | 去掉两端空白后的这一项。 |
| `meals` | 按顺序对 `Meal` 的各个值做 `and_list`：“breakfast, lunch, and dinner”和“breakfast、lunch 和 dinner”。中文也列出英文词，因为文件里要写这些词。 |
| `servings` | `servings` 的值，由 `read_servings` 给出（3.1）。 |
| `number` | N，也就是这一项的序号。 |

F05 原型“A broken settings file”和 v0.1-S22 展示了 `UNKNOWN_MEAL`。写 `meals = ["lunch", "supper"]` 时，问题位于 `settings.toml, meals`，提示是 `Unknown meal "supper". The meals are breakfast, lunch, and dinner.`。

错误：无。`read_settings` 遇到坏数据从不抛异常。

- 副作用：通过 `read_toml` 读取 `settings.toml`。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings, read_settings

settings, problems = read_settings(folder)
assert settings == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2)
assert problems == ()

folder.settings.write_text('meals = ["dinner", "breakfast", "dinner"]\n', encoding="utf-8")
assert read_settings(folder) == (Settings(None, (Meal.BREAKFAST, Meal.DINNER), 2), ())
folder.settings.write_text("", encoding="utf-8")
assert read_settings(folder) == (Settings(), ())

folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [BiText("meals", "餐次")]
english = problems[0].text(Lang.EN)
assert english == 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
chinese = problems[0].text(Lang.ZH)
assert chinese == "未知餐次“supper”。可用的餐次：breakfast、lunch 和 dinner。"

lines = ['language = "fr"', 'meals = ["lunch", 3]', "servings = 0x" + "f" * 5000, "editor = 1"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [
    BiText("language", "语言"),
    BiText("meal 2", "餐次 2"),
    BiText("servings", "份数"),
    None,
]
assert problems[0].text(Lang.EN) == 'The language must be "en" or "zh", not "fr".'
assert problems[1].text(Lang.EN) == "This item must be a text in quotation marks."
assert problems[2].text(Lang.EN) == "Servings must be a whole number from 1 to 100, such as 2."
assert problems[3].text(Lang.EN).startswith('Unknown key "editor". The keys are language,')

folder.settings.write_text("meals = []\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert problems[0].text(Lang.EN).startswith('"meals" must name at least one meal.')

folder.settings.unlink()
settings, problems = read_settings(folder)
assert settings is None
assert [problem.text(Lang.EN) for problem in problems] == ["The file is missing."]
```

### 2.4 `Context`

- 模块：app
- 功能：命令通过 `cli` 从外部世界得到的东西：语言、数据文件夹、设置、输出流和错误流，以及今天的日期（[架构 5.2](../../architecture.zh-CN.md#52-值) 和 [8](../../architecture.zh-CN.md#8-命名和编码规范)）。`cli` 构造它（2.10），测试可以用固定的值构造一个。

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
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | `cli` 选定的语言（2.10）。 | 无 |
| `folder` | `DataFolder` | 数据文件夹。 | 由 `cli` 构造时，它的 `root` 是绝对路径。对 `FolderUse.CREATE` 的命令，这个文件夹可以不存在。 |
| `settings` | `Settings` | 数据文件夹的设置。 | 对 `FolderUse.READ` 的命令，是 `read_settings` 给出的设置。对 `FolderUse.CHECK` 和 `FolderUse.CREATE`，是这些设置；文件夹不存在或设置有错误时，是 `Settings()`（选择 7）。 |
| `out` | `TextIO` | 命令写输出的地方。 | 已打开。 |
| `err` | `TextIO` | 命令写以退出码 1 结束它的提示的地方（架构 6）。 | 已打开。 |
| `today` | `date` | 电脑上今天的日期，F11 和 F13 由它得出 `this` 和 `next`。 | 无 |

- 返回值：一个 `Context`。六个字段都相等时，两个上下文相等，流按对象比较。`Context` 可以求哈希。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert context.settings.servings == 2
assert context.today.isocalendar().week == 46
context.out.write("共 7 个菜谱。\n")
assert out.getvalue() == "共 7 个菜谱。\n"
```

### 2.5 `Command`、`Argument` 和 `FolderUse`

- 模块：app
- 功能：对一个命令的描述：它的词、它的帮助行、运行它的函数、它的参数、它的选项，以及 `cli` 在运行它之前检查什么（[架构 5.2](../../architecture.zh-CN.md#52-值)、ADR-0005）。每个命令模块定义自己的命令，`cli` 根据它们读取命令行并写出帮助（2.10）。

签名：

```python
class FolderUse(Enum):
    READ = "read"
    CHECK = "check"
    CREATE = "create"


@dataclass(frozen=True, slots=True)
class Argument:
    name: Message
    required: bool = True
    repeats: bool = False


@dataclass(frozen=True, slots=True)
class Command:
    words: tuple[str, ...]
    help_line: Message
    run: Callable[[Context, Arguments], int]
    argument: Argument | None = None
    options: tuple[str, ...] = ()
    folder: FolderUse = FolderUse.READ

    @property
    def usage(self) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | 命令的词，比如 `("list",)` 或 `("menu", "show")`。 | 1 个或 2 个词。每个词只由小写字母 `a` 到 `z` 组成。 |
| `help_line` | `Message` | 命令在帮助里的那一行，比如“Show a week menu.”和“查看一个周菜单。”。 | 没有占位符。 |
| `run` | 接受一个 `Context` 和 `Arguments`（2.6）、给出 `int` 的可调用对象 | 运行命令并给出它的退出码。 | 给出 0 或 1。参数值写错时，在写出任何输出之前抛出 `UsageError`。 |
| `argument` | `Argument` 或 `None` | 命令的参数，跟在命令的词后面。 | 没有参数的命令为 `None`。 |
| `options` | `str` 的元组 | 命令的选项，每个都带一个值，比如 `("--tag",)`。 | 每个都是 `--` 后面跟一个小写字母，再跟小写字母和 `-`。不能是 `--lang`、`--data`、`--help` 或 `--version`。每个只出现一次。 |
| `folder` | `FolderUse` | `cli` 在运行命令之前检查什么，见下表。 | 无 |
| `name` | `Message` | 参数在帮助里的名称，比如 `ID`、`WORD` 和 `词`，或者 `WEEK` 和 `周`。 | 没有占位符。 |
| `required` | `bool` | 命令行是否必须给出这个参数。 | 无 |
| `repeats` | `bool` | 命令行能否多次给出这个参数。 | 无 |

`cli` 在运行命令之前做什么，取决于命令的 `FolderUse`：

| 成员 | 数据文件夹不存在 | 设置有错误 | `context.settings` | 用于 |
| --- | --- | --- | --- | --- |
| `READ` | `cli` 写出 `NO_DATA_FOLDER` 和 `RUN_INIT`，以 1 退出。 | `cli` 用 `stop_at_error` 在第一个错误处停下，以 1 退出。 | 文件里的设置。 | `list`、`show`、`search`、`menu new`、`menu show` 和 `shop` |
| `CHECK` | `cli` 写出 `NO_DATA_FOLDER` 和 `RUN_INIT`，以 1 退出。 | `cli` 运行命令，由命令报告这些问题。 | 文件里的设置；出错时为 `Settings()`。 | `check` |
| `CREATE` | `cli` 运行命令。 | `cli` 运行命令。 | 文件里的设置；文件夹不存在或设置有错误时为 `Settings()`。 | `init` |

参数的字段决定命令行可以给它几个值，以及帮助怎样写出它：

| `required` | `repeats` | 值的个数 | 帮助里的写法 | 例子 |
| --- | --- | --- | --- | --- |
| `True` | `False` | 正好 1 个 | `NAME` | `show ID` |
| `False` | `False` | 0 个或 1 个 | `[NAME]` | `menu new [WEEK]` |
| `True` | `True` | 1 个或更多 | `NAME...` | `search WORD...` |
| `False` | `True` | 0 个或更多 | `[NAME...]` | v0.1 里没有 |

- 返回值：一个 `Command`、一个 `Argument` 或一个 `FolderUse` 成员。
  - `usage` 给出命令的词，用空格连接，然后在每种语言里接一个空格和参数的写法，比如 `show ID`、`search WORD...` 和 `search 词...`，或者 `menu show [WEEK]` 和 `menu show [周]`。没有参数的命令只给出它的词。帮助显示 `usage`，2.10 的用法错误也引用它。
  - 六个字段都相等时，两个命令相等；三个字段都相等时，两个参数相等。两者都可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `words` 为空、多于 2 个词，或者有一个词含有 `a` 到 `z` 以外的字符。 |
| `ValueError` | `help_line` 或参数的 `name` 有占位符。 |
| `ValueError` | 某个选项不符合参数表里的规则，是全局选项，或者出现两次。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.app import Argument, Arguments, Command, Context, FolderUse
from recipe_menu.lang import BiText
from recipe_menu.text import Message


def run(context: Context, arguments: Arguments) -> int:
    context.out.write(" ".join(arguments.values) + "\n")
    return 0


WEEK = Argument(Message("WEEK", "周"), required=False)
WORD = Argument(Message("WORD", "词"), repeats=True)
MENU_SHOW = Command(
    ("menu", "show"),
    Message("Show a week menu.", "查看一个周菜单。"),
    run,
    WEEK,
)
SEARCH = Command(
    ("search",),
    Message("Find recipes by name, ingredient, or tag.", "按名称、食材或标签找菜谱。"),
    run,
    WORD,
)
INIT = Command(
    ("init",),
    Message("Create the data folder with example data.", "创建数据文件夹和示例数据。"),
    run,
    folder=FolderUse.CREATE,
)
assert MENU_SHOW.usage == BiText("menu show [WEEK]", "menu show [周]")
assert SEARCH.usage == BiText("search WORD...", "search 词...")
assert INIT.usage == BiText("init", "init")
assert MENU_SHOW.folder is FolderUse.READ

HELP = Message("Show one recipe.", "查看一个菜谱。")
Command(("Show",), HELP, run)  # raises ValueError
Command(("menu", "show", "all"), HELP, run)  # raises ValueError
Command(("show",), HELP, run, options=("--lang",))  # raises ValueError
Command(("show",), HELP, run, options=("-s",))  # raises ValueError
Command(("show",), Message("Show {id}.", "查看 {id}。"), run)  # raises ValueError
```

### 2.6 `Arguments`

- 模块：app
- 功能：命令行给一个命令的东西：它的参数的值和它的选项的值。`cli` 构造它（2.10），命令的 `run` 拿到它。

签名：

```python
@dataclass(frozen=True, slots=True)
class Arguments:
    values: tuple[str, ...] = ()
    options: tuple[tuple[str, str], ...] = ()

    def option(self, name: str) -> str | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `values` | `str` 的元组 | 参数的值，按命令行里的顺序，比如 `("番茄", "quick")`。 | 个数在参数允许的范围内（2.5）。 |
| `options` | （名称，值）二元组的元组 | 命令行给出的命令选项，比如 `(("--tag", "素"),)`。全局选项不在这里。 | 每个名称只出现一次。`Arguments` 按名称给这些二元组排序，所以它们的顺序无关紧要。 |
| `name` | `str` | 选项的名称，供 `option` 使用。 | 无 |

- 返回值：一个 `Arguments`。
  - `option(name)` 给出选项 `name` 的值；命令行没有给出这个选项时给出 `None`。
  - 由 `cli` 构造时，选项的值都不为空，也不以 `--` 开头（2.10）。
  - 两个字段都相等时，两个 `Arguments` 相等。`Arguments` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 某个名称在 `options` 里出现两次。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.app import Arguments

arguments = Arguments(("番茄", "quick"), (("--tag", "素"),))
assert arguments.values == ("番茄", "quick")
assert arguments.option("--tag") == "素"
assert arguments.option("--servings") is None
both = Arguments((), (("--tag", "素"), ("--servings", "4")))
assert both.options == (("--servings", "4"), ("--tag", "素"))
assert Arguments() == Arguments((), ())

Arguments((), (("--tag", "a"), ("--tag", "b")))  # raises ValueError
```

### 2.7 `UsageError`

- 模块：app
- 功能：写错的命令行或参数值，带有它的提示、提示的值，以及跟在提示后面的那一行（[架构 5.2](../../architecture.zh-CN.md#52-值) 和 [6](../../architecture.zh-CN.md#6-错误处理)）。解析器抛出它，命令遇到写错的参数值时也抛出它。`cli` 把它变成退出码 2。

签名：

```python
class UsageError(Exception):
    message: Message
    hint: Message | None
    values: tuple[tuple[str, MessageValue], ...]

    def __init__(
        self,
        message: Message,
        hint: Message | None,
        /,
        **values: MessageValue,
    ) -> None: ...

    def text(self, lang: Lang) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `message` | `Message` | 哪里写错了。 | 只能按位置传入。 |
| `hint` | `Message` 或 `None` | 跟在提示后面的那一行，比如 `RUN_HELP_FOR_OPTIONS`；提示本身已经说明怎么写时为 `None`（选择 9）。 | 没有占位符。只能按位置传入，所以提示可以有名为 `message` 或 `hint` 的占位符。 |
| `values` | `MessageValue` 关键字参数 | `message` 每个占位符的值。 | 每个占位符一个，不多不少。`UsageError` 把它们按名称排序，存成二元组。 |
| `lang` | `Lang` | `text` 使用的语言。 | 无 |

- 返回值：一个 `UsageError`。
  - `text(lang)` 给出 `message.render(lang, **values)`。`cli` 把它写到错误流，`hint` 不为 `None` 时再写 `hint.render(lang)`，各占一行（2.10）。
  - `str(error)` 给出英文文字，所以万一有 bug 让这个错误漏出去，回溯信息也会写明错误。
  - `__init__` 只设置一次 `message`、`hint` 和 `values`，没有代码再改动它们。异常不能是冻结的 dataclass，因为 Python 会在异常上设置 `__traceback__` 之类的属性，所以 `UsageError` 是一个普通的类。

错误：

和 `Problem` 一样（F03 设计 2.2），创建 `UsageError` 时会用两种语言各渲染一次提示，所以错误的值在构造错误的地方就会失败。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `values` 的名称和 `message` 的占位符不完全相同。 |
| `TypeError` | 某个值不是 `str`、`int` 或 `BiText`，或者是 `bool` 或 `enum.Enum` 成员（F02 设计 2.3）。 |
| `ValueError` | 某个 `int` 值超过 4,300 位（F02 设计 2.3）。 |
| `ValueError` | `hint` 有占位符。 |

- 副作用：无
- 性能指标：无

示例：

`NOT_A_WEEK` 代表 F11 的设计会给出的那类提示。

```python
from recipe_menu.app import UsageError
from recipe_menu.lang import Lang
from recipe_menu.text import RUN_HELP_FOR_OPTIONS, Message

LANG_NOT_EN_OR_ZH = Message(
    '--lang must be en or zh, not "{lang}".',
    "--lang 必须是 en 或 zh，不能是“{lang}”。",
)
NOT_A_WEEK = Message('"{week}" is not a week.', "“{week}”不是一个周。")

error = UsageError(LANG_NOT_EN_OR_ZH, RUN_HELP_FOR_OPTIONS, lang="fr")
assert error.text(Lang.EN) == '--lang must be en or zh, not "fr".'
assert error.text(Lang.ZH) == "--lang 必须是 en 或 zh，不能是“fr”。"
assert error.hint is RUN_HELP_FOR_OPTIONS
assert str(error) == '--lang must be en or zh, not "fr".'
week = UsageError(NOT_A_WEEK, None, week="2026-W99")
assert week.hint is None
assert week.values == (("week", "2026-W99"),)

UsageError(NOT_A_WEEK, None)  # raises ValueError
UsageError(NOT_A_WEEK, None, week=None)  # raises TypeError
UsageError(NOT_A_WEEK, NOT_A_WEEK, week="2026-W99")  # raises ValueError
```

### 2.8 `problem_lines`、`first_error` 和 `stop_at_error`

- 模块：app
- 功能：按原型的格式显示数据文件的问题：一行写文件和位置，下一行写提示（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。`stop_at_error` 在数据文件的第一个错误处结束命令，`check` 以外的每个命令都这样做。`cli` 对设置使用它，F09 到 F16 的命令对它们的文件使用它。F07 用 `problem_lines` 写出每个问题，并使用自己的缩进。

签名：

```python
def problem_lines(problem: Problem, lang: Lang) -> tuple[str, str]: ...


def first_error(problems: Iterable[Problem]) -> Problem | None: ...


def stop_at_error(context: Context, error: Problem) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `problem` | `Problem` | 要显示的问题。 | 无 |
| `lang` | `Lang` | 这两行的语言。 | 无 |
| `problems` | `Problem` 值的可迭代对象 | 读取函数给出的问题，按它的顺序。 | 无 |
| `context` | `Context` | 语言和错误流。 | 无 |
| `error` | `Problem` | 让命令停下的错误。 | `Severity.ERROR`。 |

- 返回值：
  - `problem_lines` 给出二元组 `(where, what)`，不带缩进。问题没有位置时，`where` 是 `str(problem.file)`；否则是带有文件和位置的 `FILE_AT_PLACE`，比如 Windows 上的 `recipes\mapo-tofu.toml, ingredient 3` 和 `recipes\mapo-tofu.toml，食材 3`。`what` 是 `problem.text(lang)`。
  - `first_error` 给出第一个 `Severity.ERROR` 的问题；没有时给出 `None`。
  - `stop_at_error` 给出 1，也就是数据文件出错而停下的命令的退出码。它向 `context.err` 写三行：`where`，然后是两个空格加 `what`，最后是 `RUN_CHECK`，都用 `context.lang`。F11 原型“A menu with a mistake”展示了这个格式。

`app` 的提示如下。`{file}` 是 `str(problem.file)`，`{place}` 是问题的位置，类型是 `BiText`。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `FILE_AT_PLACE` | `{file}, {place}` | `{file}，{place}` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `stop_at_error` 拿到一个 `Severity.WARNING` 的问题。 |

- 副作用：`stop_at_error` 写入 `context.err`。另外两个函数没有副作用。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本。

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Context, first_error, problem_lines, stop_at_error
from recipe_menu.datafile import Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings
from recipe_menu.text import Message

UNKNOWN = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
FILE_MISSING = Message("The file is missing.", "文件不存在。")
mapo = Path("recipes", "mapo-tofu.toml")
problem = Problem.error(mapo, BiText("ingredient 3", "食材 3"), UNKNOWN, name="豆瓣酱")
assert problem_lines(problem, Lang.ZH) == (f"{mapo}，食材 3", "未知食材“豆瓣酱”。")
missing = Problem.error(Path("settings.toml"), None, FILE_MISSING)
assert problem_lines(missing, Lang.EN) == ("settings.toml", "The file is missing.")
warning = Problem.warning(mapo, None, FILE_MISSING)
assert first_error([warning, missing, problem]) is missing
assert first_error([warning]) is None

folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
_, problems = read_settings(folder)
error = first_error(problems)
assert error is not None
err = io.StringIO()
context = Context(Lang.EN, folder, Settings(), io.StringIO(), err, date(2026, 11, 10))
assert stop_at_error(context, error) == 1
assert err.getvalue().splitlines() == [
    "settings.toml, meals",
    '  Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
    'Run "recipe-menu check" to see every problem.',
]

stop_at_error(context, warning)  # raises ValueError
```

### 2.9 `main`

- 模块：cli
- 功能：`recipe-menu` 命令和 `python -m recipe_menu` 的入口（[架构 2](../../architecture.zh-CN.md#2-技术栈) 和 [10](../../architecture.zh-CN.md#10-测试配置)）。它读取外部世界，运行 2.10 的命令行，并给出退出码。测试用固定的值调用它。

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
) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `argv` | `str` 的序列，或 `None` | 程序名后面的参数。 | `None` 时用 `sys.argv[1:]`。 |
| `environ` | 从 `str` 到 `str` 的映射，或 `None` | 环境变量。`main` 只读取 `RECIPE_MENU_DATA`。 | `None` 时用 `os.environ`。 |
| `home` | `Path` 或 `None` | 主文件夹，用于默认的数据文件夹和开头的 `~`（2.10）。 | `None` 时用 `Path.home()`，它在 Windows 上跟随 `USERPROFILE`，在 Linux 上跟随 `HOME`。 |
| `today` | `date` 或 `None` | 今天的日期。 | `None` 时用电脑时钟的本地日期。 |
| `stdout` | `TextIO` 或 `None` | 输出流。 | `None` 时用经过 F02 的 `use_utf8` 处理的 `sys.stdout`。 |
| `stderr` | `TextIO` 或 `None` | 错误流。 | `None` 时用经过 `use_utf8` 处理的 `sys.stderr`。 |
| `commands` | `Command` 值的序列，或 `None` | 各个命令，按帮助里的顺序。 | `None` 时用 `COMMANDS`。没有两个命令的词相同，也没有一个单词命令的词是某个两词命令的第一个词。 |

- 返回值：2.10 的退出码。`uv tool install` 写出的控制台脚本把它传给 `sys.exit`；Python 把 `src/recipe_menu/__main__.py` 当作主模块运行时，这个文件执行 `raise SystemExit(main())`。

`COMMANDS` 是 `src/recipe_menu/cli/_commands.py` 里由 `Command` 值组成的元组。在 F05 里它是空的。每个命令功能在它的 mock PR 里，在这里引入它的命令模块的 `Command` 值并加进去；这是命令功能对 `cli` 的唯一改动（架构 4）。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `commands` 不符合它的约束。`main` 在读取参数之前检查它。这只来自错误的调用。 |

命令抛出的其他任何异常都是 bug，会继续交给 Python，由它显示回溯信息（架构 6）。`main` 只把 `UsageError` 变成退出码 2，把 `KeyboardInterrupt` 变成 130。它不捕获控制台流的错误，因为架构 6 没有对应的行。

- 副作用：每个为 `None` 的参数都读取外部世界里对应的部分，`use_utf8` 会改动 `sys.stdout` 和 `sys.stderr`。`main` 按 2.10 的说明查看数据文件夹是不是文件夹、读取设置并运行命令。它自己不写任何文件。
- 性能指标：无

示例：

在这个示例里，`home` 是一个空的临时文件夹，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，位于 `home` 之外。`LIST` 代表 F09 的 `list` 命令。`environ` 是 `run` 传给 `main` 的环境变量，最后一种情况在其中设置 `RECIPE_MENU_DATA`。

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run_list(context: Context, arguments: Arguments) -> int:
    tag = arguments.option("--tag")
    context.out.write(f"{context.lang.value} {tag}\n")
    return 0


LIST = Command(
    ("list",),
    Message("List the recipes.", "列出菜谱。"),
    run_list,
    options=("--tag",),
)
environ: dict[str, str] = {}


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ=environ,
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        commands=[LIST],
    )
    return code, out.getvalue(), err.getvalue()


data = str(folder.root)
assert run("list", "--tag", "素", "--data", data) == (0, "en 素\n", "")
assert run("--lang", "zh", "--data", data, "list") == (0, "zh None\n", "")
assert run("--version") == (0, "recipe-menu 0.1.0\n", "")

code, out, err = run("cook", "--data", data)
assert (code, out) == (2, "")
assert err.splitlines() == [
    'Unknown command "cook".',
    'Run "recipe-menu --help" to see the commands.',
]
code, _, err = run("list", "--tags", "素", "--data", data)
assert err.splitlines() == [
    '"list" has no option "--tags". Its own option is "--tag".',
    'Run "recipe-menu --help" to see the options.',
]
assert run("list", "--tag", "--data", data) == (2, "", "--tag needs a value.\n")
code, _, err = run("list", "--lang", "--lang", "zh", "--data", data)
assert err.splitlines() == ["--lang 后面要写一个值。", "运行“recipe-menu --help”查看选项。"]

folder.settings.write_text('language = "zh"\n', encoding="utf-8")
code, _, err = run("cook", "--data", data)
assert err.splitlines() == ["未知命令“cook”。", "运行“recipe-menu --help”查看命令。"]
assert run("list", "--data", data) == (0, "zh None\n", "")

code, _, err = run("list")
assert code == 1
default = home / "recipe-menu"
assert err.splitlines() == [
    f"There is no data folder at {default}.",
    'Run "recipe-menu init" to create it, or name another folder with --data.',
]
assert run("list", "--data", "~/recipe-menu") == (1, "", err)

environ["RECIPE_MENU_DATA"] = data
code, _, err = run("list", "--data")
assert err.splitlines() == ["--data 后面要写一个值。", "运行“recipe-menu --help”查看选项。"]
```

### 2.10 `recipe-menu`

- 模块：cli
- 功能：你输入的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 和 [4](../../requirements.zh-CN.md#4-功能点)）。它运行一个命令和它的参数，选定数据文件夹和语言，显示帮助和版本，报告命令行的错误，并以需求 3 的退出码退出。F05 原型展示了它。

签名：

```text
recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]
recipe-menu --help [--lang en|zh] [--data FOLDER]
recipe-menu --version
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `COMMAND` | 一个或两个词 | 命令，比如 `list` 或 `menu show`。 | `commands` 里的一个命令（2.9）。 |
| `ARGUMENTS` | 词和选项 | 命令参数的值，以及命令的选项和它们的值，比如 `tomato-egg --servings 4`。 | 按命令的声明（2.5）。 |
| `--lang` | `en` 或 `zh` | 每条提示的语言，帮助也包括在内。 | 正好是 `en` 或 `zh`。 |
| `--data` | 一个文件夹 | 数据文件夹。 | 不为空。开头的 `~` 从主文件夹算起，相对路径从当前文件夹算起。 |
| `--help` | 开关 | 显示帮助。 | 无 |
| `--version` | 开关 | 显示版本。 | 无 |

`cli` 按这些规则读取参数：

1. 以 `--` 开头的参数是选项。`--help` 和 `--version` 是开关。其他每个选项都把下一个参数当作它的值。下一个参数不存在、为空或以 `--` 开头时，它不是值。这时这个选项没有值，`cli` 单独读取下一个参数。
2. 其他每个参数都是词。前一个或两个词是命令的词，其余按顺序是它的参数的值。所以选项和词可以按任意顺序出现，比如 `recipe-menu --lang zh list --tag 素`。
3. `--lang`、`--data`、`--help` 和 `--version` 是全局选项。`cli` 为每个命令接受它们，没有命令声明它们。其他每个选项都属于命令。
4. 数据文件夹是第一个有值的 `--data` 的值构成的 `Path(value)`。没有值的 `--data` 在这里算作没写，由第 4 步报告它。没有这样的 `--data` 时，如果设置了 `RECIPE_MENU_DATA` 而且它不为空，就是它的值构成的 `Path(value)`。两者都没有时，是 `home / "recipe-menu"`。`Path(value).parts[0]` 是 `~` 时，`cli` 把这一部分换成 `home`，所以 `~`、`~/OneDrive` 以及 Windows 上的 `~\OneDrive` 都从主文件夹算起。然后 `cli` 用 `Path.absolute()` 从当前文件夹出发把相对路径变成绝对路径。它不展开其他写法的 `~`，不展开变量，也不解析链接。所以 `--data` 优先于 `RECIPE_MENU_DATA`，和 v0.1-S20 的期望一样。

然后 `main` 按顺序执行这些步骤：

1. 它按规则 1 到 3 读取参数，按规则 4 找到数据文件夹。
2. `os.path.isdir(folder.root)` 为真时，它用 `read_settings` 读取设置。`os.path.isdir` 从不抛异常，所以查看失败时按假处理，和 `datafile` 一样。在 Python 3.13 里 `Path.is_dir` 可能抛异常，所以 `cli` 不用它。
3. 它用 `choose_lang(option, setting)` 选定语言（F02 设计 2.7）。第一个有值的 `--lang` 的值是 `en` 或 `zh` 时，`option` 是这个值，否则是 `None`。没有值的 `--lang` 在这里算作没写，由第 4 步报告它。第 2 步给出 `Settings` 时，`setting` 是设置里的 `language`，否则是 `None`。从这里开始的每条提示都用这种语言，用法错误也一样。
4. 它按命令行里的顺序检查每个 `--lang` 和每个 `--data`。对每一个，下面三条规则中第一条适用的规则给出它的错误。没有值的选项给出 `OPTION_NEEDS_VALUE`。第二个 `--lang` 或第二个 `--data` 给出 `OPTION_TWICE`。`--lang` 的值不是 `en` 或 `zh` 时给出 `LANG_NOT_EN_OR_ZH`。`--help` 和 `--version` 可以重复（选择 10）。
5. 命令行里有 `--help` 时，它写出帮助并以 0 退出。否则，命令行里有 `--version` 时，它写出版本并以 0 退出。两者都不看命令行的其余部分。
6. 它在词里找出命令。没有词时给出 `NO_COMMAND`。第一个词不是任何命令的开头时给出 `UNKNOWN_COMMAND`。第一个词是两词命令的开头时，需要第二个词：没有第二个词时给出 `INCOMPLETE_COMMAND`，第二个词组不成命令时给出带两个词的 `UNKNOWN_COMMAND`。
7. 它按命令行里的顺序检查命令的选项。命令没有声明的选项给出 `UNKNOWN_OPTION`。没有值的选项给出 `OPTION_NEEDS_VALUE`。同一选项的第二次给出 `OPTION_TWICE`。
8. 它检查参数的值的个数（2.5）。太少时给出 `TOO_FEW_ARGUMENTS`。太多时给出 `TOO_MANY_ARGUMENTS`，它写出第一个多余的值。
9. 它按命令的 `FolderUse` 检查数据文件夹和设置（2.5）。数据文件夹不存在时，向错误流写出 `NO_DATA_FOLDER` 和 `RUN_INIT`，退出码为 1。设置有错误时，用第一个错误调用 `stop_at_error`（2.8），退出码为 1。
10. 它构造 `Context`（2.4）和 `Arguments`（2.6），运行命令，并以 `run` 给出的退出码退出。

对第 4 步、第 6 到 8 步或 `run` 里的 `UsageError`，`cli` 向错误流写出 `error.text(lang)`，有提示行时再写出提示行，各占一行，然后以 2 退出。在任何一步按 Ctrl+C 都以 130 退出，`cli` 不再写出任何内容（架构 6）。

- 返回值：退出码，每种情况的输出写在对应的流上（[架构 6](../../architecture.zh-CN.md#6-错误处理)）：

| 退出码 | 何时 | 流 |
| --- | --- | --- |
| 0 | 帮助、版本，或者命令成功。 | 输出流。 |
| 1 | 数据文件夹不存在、设置有错误，或者命令给出 1。 | `cli` 的提示写到错误流。命令按架构 6 的规定，把输出写到输出流，把结束它的提示写到错误流。 |
| 2 | `UsageError`。 | 错误流：先是提示，有提示行时再写它的提示行。 |
| 130 | Ctrl+C。 | 不再写出任何内容。 |

帮助由下面这些行按顺序组成，每行以换行结束，写到输出流：

1. 用法行。
2. 一个空行。
3. 简介。
4. 一个空行。
5. 命令的标题。
6. 命令表：对 `commands` 里的每个命令，按它们的顺序，写 `usage.get(lang)` 和 `help_line.render(lang)`。
7. 一个空行。
8. 选项的标题。
9. 选项表：`--lang`、`--data`、`--version` 和 `--help`，按这个顺序。
10. 一个空行。
11. 关于周的说明。

两个表都是 `format_table(rows, indent=2, min_widths=(width,))`，使用默认的间距 3（F02 设计 2.9）。`width` 是两个表里所有第一格在两种语言里的最大 `display_width`。所以第二列在两个表里、在两种语言里都从同一个位置开始。有 v0.1 的八个命令时，最宽的第一格是 `menu show [WEEK]`，宽 16 列，帮助正好给出 F05 原型的两份帮助输出。F02 的审查已经用 `min_widths=(16,)` 检查过这些行。

帮助和版本的文字如下：

| 行 | 英文 | 中文 |
| --- | --- | --- |
| 用法行 | `Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en\|zh] [--data FOLDER]` | `用法：recipe-menu 命令 [参数] [--lang en\|zh] [--data 文件夹]` |
| 简介 | `Keep your recipes, plan a week's menu, and make its shopping list.` | `保存菜谱，排一周的菜单，并生成它的购物清单。` |
| 命令的标题 | `Commands:` | `命令：` |
| 选项的标题 | `Options:` | `选项：` |
| 关于周的说明 | `WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.` | `“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。` |
| 版本 | `recipe-menu {version}`，值为 `__version__`（2.11） | `recipe-menu {version}`，值为 `__version__`（2.11） |

| 选项 | 第一格，英文 | 第一格，中文 | 第二格，英文 | 第二格，中文 |
| --- | --- | --- | --- | --- |
| `--lang` | `--lang en\|zh` | `--lang en\|zh` | `The language of the output. Default: the settings, else English.` | `输出语言。默认：设置里的语言，否则英文。` |
| `--data` | `--data FOLDER` | `--data 文件夹` | `The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.` | `数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。` |
| `--version` | `--version` | `--version` | `Show the version.` | `显示版本。` |
| `--help` | `--help` | `--help` | `Show this help.` | `显示这份帮助。` |

错误：

解析器的每个 `UsageError` 都指定 F02 两条指向 `--help` 的提示行中的一条，只有命令自己的选项的 `OPTION_NEEDS_VALUE` 和 `OPTION_TWICE` 除外。帮助不列出命令自己的选项（选择 11），而这两条提示本身已经说明了要改什么，所以它们不指定提示行（决定 A）。`UNKNOWN_OPTION` 写出命令自己的选项，它的提示行指向列出全局选项的帮助，以防你本来想写的是其中一个。它有三种形式，按命令自己的选项个数选择，就像 `UNKNOWN_KEY` 有两种形式（F03 设计 2.10）。`INCOMPLETE_COMMAND` 是一个 `Plural`（F02 设计 2.4），按以 `word` 开头的命令个数选择。`LANG_NOT_EN_OR_ZH` 和 `UNKNOWN_COMMAND` 的英文文字及其提示行，就是 F05 原型“Mistakes on the command line”里的各行。

| 名称 | 何时 | 英文 | 中文 | 提示行 |
| --- | --- | --- | --- | --- |
| `OPTION_NEEDS_VALUE` | 选项没有值（第 4 步和第 7 步）。 | `{option} needs a value.` | `{option} 后面要写一个值。` | `--lang` 和 `--data` 为 `RUN_HELP_FOR_OPTIONS`。命令自己的选项为无。 |
| `OPTION_TWICE` | 带值的选项出现两次（第 4 步和第 7 步）。 | `{option} is given twice.` | `{option} 写了两次。` | `--lang` 和 `--data` 为 `RUN_HELP_FOR_OPTIONS`。命令自己的选项为无。 |
| `LANG_NOT_EN_OR_ZH` | `--lang` 的值既不是 `en` 也不是 `zh`（第 4 步）。 | `--lang must be en or zh, not "{lang}".` | `--lang 必须是 en 或 zh，不能是“{lang}”。` | `RUN_HELP_FOR_OPTIONS` |
| `NO_COMMAND` | 命令行里没有词（第 6 步）。 | `Name a command, such as "recipe-menu list".` | `请写上一个命令，比如“recipe-menu list”。` | `RUN_HELP_FOR_COMMANDS` |
| `UNKNOWN_COMMAND` | 这些词组不成命令（第 6 步）。 | `Unknown command "{command}".` | `未知命令“{command}”。` | `RUN_HELP_FOR_COMMANDS` |
| `INCOMPLETE_COMMAND`，一个命令时 | 唯一的词正好是一个两词命令的开头（第 6 步）。只有测试自己的 `commands` 才有这样的词。 | `The only command that starts with "{word}" is {commands}.` | `以“{word}”开头的命令只有{commands}。` | `RUN_HELP_FOR_COMMANDS` |
| `INCOMPLETE_COMMAND`，多个命令时 | 唯一的词是两个或更多两词命令的开头，比如 `menu`（第 6 步）。 | `The commands that start with "{word}" are {commands}.` | `以“{word}”开头的命令有{commands}。` | `RUN_HELP_FOR_COMMANDS` |
| `UNKNOWN_OPTION`，没有选项时 | 命令没有声明任何选项（第 7 步）。 | `"{command}" has no option "{option}". It has no options of its own.` | `“{command}”没有选项“{option}”。它没有自己的选项。` | `RUN_HELP_FOR_OPTIONS` |
| `UNKNOWN_OPTION`，一个选项时 | 命令声明了一个选项，但不是这一个（第 7 步）。 | `"{command}" has no option "{option}". Its own option is {options}.` | `“{command}”没有选项“{option}”。它自己的选项是{options}。` | `RUN_HELP_FOR_OPTIONS` |
| `UNKNOWN_OPTION`，多个选项时 | 命令声明了两个或更多选项，但没有这一个（第 7 步）。 | `"{command}" has no option "{option}". Its own options are {options}.` | `“{command}”没有选项“{option}”。它自己的选项有{options}。` | `RUN_HELP_FOR_OPTIONS` |
| `TOO_FEW_ARGUMENTS` | 参数的值太少（第 8 步）。 | `An argument is missing. Write "recipe-menu {usage}".` | `缺少参数。请写成“recipe-menu {usage}”。` | `RUN_HELP_FOR_COMMANDS` |
| `TOO_MANY_ARGUMENTS` | 参数的值太多（第 8 步）。 | `Unexpected argument "{argument}". Write "recipe-menu {usage}".` | `多余的参数“{argument}”。请写成“recipe-menu {usage}”。` | `RUN_HELP_FOR_COMMANDS` |

下面这些提示以退出码 1 结束命令（第 9 步）。它们的文字就是 F05 原型“No data folder yet”里的各行。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NO_DATA_FOLDER` | `There is no data folder at {folder}.` | `{folder} 没有数据文件夹。` |
| `RUN_INIT` | `Run "recipe-menu init" to create it, or name another folder with --data.` | `运行“recipe-menu init”创建它，或用 --data 指定别的文件夹。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `option` | 命令行里写的选项，比如 `--data` 或 `--lang=zh`。 |
| `lang` | 命令行里写的 `--lang` 的值。 |
| `command` | 命令的词，或者组不成命令的那些词，用空格连接，比如 `menu cook`。 |
| `word` | 第一个词，比如 `menu`。 |
| `commands` | 对以 `word` 开头的每个命令，按 `commands` 的顺序，把加了引号的命令词做 `and_list`：`"menu new" and "menu show"` 和 `“menu new”和“menu show”`。 |
| `options` | 对命令自己的每个选项加上引号，按 `options` 的顺序（2.5）做 `and_list`：`"--tag"`，或者 `"--servings" and "--tag"` 和 `“--servings”和“--tag”`。 |
| `usage` | 命令的 `usage`（2.5），比如 `show ID`，或者 `menu new [WEEK]` 和 `menu new [周]`。 |
| `argument` | 第一个多余的值，按命令行里的写法。 |
| `folder` | `str(folder.root)`，数据文件夹的完整路径。 |
| `version` | `__version__`（2.11）。 |

- 副作用：查看数据文件夹是不是文件夹；是文件夹时，通过 `read_settings` 读取 `settings.toml`。`cli` 不写任何文件。它运行的命令读写什么，由那个功能的设计规定。
- 性能指标：无。PT01 的各个命令都包括这段启动时间（见第 2 节开头的规则）。

示例：

在这个示例里，`home` 是一个空的临时文件夹。`SHOW` 和 `MENU_SHOW` 代表 F09 和 F11 的两个命令。第 5 行和第 6 行是 F05 原型“Help in Chinese”里的行，它的第一列宽 16 列，因为英文里有 `menu show [WEEK]`。

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run(context: Context, arguments: Arguments) -> int:
    return 0


SHOW = Command(
    ("show",),
    Message("Show one recipe.", "查看一个菜谱。"),
    run,
    Argument(Message("ID", "ID")),
    ("--servings",),
)
MENU_SHOW = Command(
    ("menu", "show"),
    Message("Show a week menu.", "查看一个周菜单。"),
    run,
    Argument(Message("WEEK", "周"), required=False),
)


def help_lines(*argv: str) -> list[str]:
    out = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=io.StringIO(),
        commands=[SHOW, MENU_SHOW],
    )
    assert code == 0
    return out.getvalue().splitlines()


lines = help_lines("--help", "--lang", "zh")
assert len(lines) == 15
assert lines[0] == "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]"
assert lines[4] == "命令："
assert lines[5] == "  show ID            查看一个菜谱。"
assert lines[6] == "  menu show [周]     查看一个周菜单。"
assert lines[10].startswith("  --data 文件夹      数据文件夹。")
english = help_lines("show", "x", "--help")
assert english[6] == "  menu show [WEEK]   Show a week menu."
assert english[9].startswith("  --lang en|zh       The language of the output.")
assert help_lines("--help", "--help") == english
```

v0.1-S19 到 v0.1-S22 用真正的命令运行 F05 原型里的其他情况。

### 2.11 `__version__`

- 模块：cli，放在 `src/recipe_menu/__init__.py` 里
- 功能：`--version` 显示的版本（2.10）。架构 3 把 `src/recipe_menu/__init__.py` 交给 `cli`。F01 创建了它，只放了文档注释，因为 mypy 需要这个文件；F05 只加入这一个名称（选择 12）。

签名：

```python
__version__ = "0.1.0"
```

参数：无

- 返回值：无。`__version__` 是一个 `str`，等于 `pyproject.toml` 里 `[project]` 的 `version`。F05 的一个测试保证两者相等，所以提高版本的发布要同时修改这两行。

错误：无

- 副作用：无
- 性能指标：无

示例：

这个示例在仓库的根目录下运行。

```python
import tomllib
from pathlib import Path

import recipe_menu

project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
assert recipe_menu.__version__ == project["version"] == "0.1.0"
```

## 3. 对已有接口的修改

无。F01 到 F04 已实现的接口都没有改变。每个导出的名称都保持原来的签名和行为，F01 到 F04 的测试不加改动就能通过。F05 和 F04 一样，给 `datafile` 的接口加入名称，并改动 `recipes` 的内部文件。

1. `datafile` 导出 `read_servings`、`MIN_SERVINGS` 和 `MAX_SERVINGS`（3.1）。提示 `SERVINGS_NOT_A_NUMBER`、`SERVINGS_TOO_FEW` 和 `SERVINGS_TOO_MANY` 从 `recipes/messages.py` 移到 `datafile/messages.py`，文字不变，仍然只在模块内部使用。`read_recipe` 仍然自己报告缺少的 `servings` 键，并用 `read_servings` 读取它的值，所以它按同样的顺序给出同样的问题（F04 设计 2.6）。`Recipe` 可以用 `MIN_SERVINGS` 和 `MAX_SERVINGS` 检查它的范围。
2. `src/recipe_menu/__init__.py` 加入 `__version__`（2.11）。
3. F05 使用 F02 的 `BiText`、`Lang`、`Message`、`MessageValue`、`RUN_CHECK`、`RUN_HELP_FOR_COMMANDS`、`RUN_HELP_FOR_OPTIONS`、`and_list`、`choose_lang`、`display_width`、`format_table` 和 `use_utf8`。它使用 `DataFolder`、`Problem`、`Severity`、`read_toml` 和 F03 设计 2.10 的提示，以及 F04 设计 3.2 的 `Report`、`read_list`、`read_text` 和 `report_unknown_keys`。它按这些设计的规定使用它们，一个也不改动。

### 3.1 `read_servings`、`MIN_SERVINGS` 和 `MAX_SERVINGS`

- 模块：datafile
- 功能：数据文件里份数的唯一规则：1 到 100 之间的整数，只有不超过 15 位时才在提示里显示（[F04 设计](../F04-recipe-files/design.zh-CN.md)，选择 2）。`read_recipe`（F04）、`read_settings`（2.3）和 F06 读取周菜单的函数都用它检查份数。F09 用 `MIN_SERVINGS` 和 `MAX_SERVINGS` 检查 `show --servings`。

签名：

```python
MIN_SERVINGS: Final[int] = 1
MAX_SERVINGS: Final[int] = 100


def read_servings(value: object, place: BiText, report: Report) -> int | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `value` | `object` | `read_toml` 给出的份数值，比如 `2` 或 `"2"`。 | 无。调用者已经找到了这个键。 |
| `place` | `BiText` | 这个值的位置，比如“servings”和“份数”。 | 无 |
| `report` | `Report` | 问题写到哪里（F04 设计 3.2）。 | 无 |

- 返回值：`value` 是 `int`、不是 `bool`，并且在 `MIN_SERVINGS` 到 `MAX_SERVINGS` 之间时，给出 `value`。否则 `read_servings` 按下表在 `place` 加一个错误，然后给出 `None`：

| 值 | 提示 |
| --- | --- |
| 不是整数，比如 `"2"`、`2.5` 或 `true`，或者是 16 位以上的整数，比如 `0x` 后面跟 5,000 位数字 | `SERVINGS_NOT_A_NUMBER` |
| -999,999,999,999,999 到 0 之间的整数 | `SERVINGS_TOO_FEW`，`servings` 设为这个值 |
| 101 到 999,999,999,999,999 之间的整数 | `SERVINGS_TOO_MANY`，`servings` 设为这个值 |

所以值 `servings` 不超过 15 位，`Problem` 永远碰不到 F02 的 4,300 位限制。这些提示保持 F04 设计 2.6 里的文字：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `SERVINGS_NOT_A_NUMBER` | `Servings must be a whole number from 1 to 100, such as 2.` | `份数必须是 1 到 100 之间的整数，比如 2。` |
| `SERVINGS_TOO_FEW` | `Servings must be a whole number of 1 or more, not {servings}.` | `份数必须是不小于 1 的整数，不能是 {servings}。` |
| `SERVINGS_TOO_MANY` | `Servings must be a whole number of 100 or less, not {servings}.` | `份数必须是不大于 100 的整数，不能是 {servings}。` |

错误：无。`read_servings` 遇到坏数据从不抛异常。

- 副作用：最多向 `report.problems` 追加一个问题。
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS, Report, read_servings
from recipe_menu.lang import BiText, Lang

report = Report(Path("settings.toml"))
place = BiText("servings", "份数")
assert read_servings(4, place, report) == 4
assert read_servings(MIN_SERVINGS, place, report) == 1
assert read_servings(MAX_SERVINGS, place, report) == 100
assert report.problems == []
assert read_servings(0, place, report) is None
assert read_servings(True, place, report) is None
assert read_servings(10**15, place, report) is None
assert read_servings(101, place, report) is None
assert [problem.text(Lang.EN) for problem in report.problems] == [
    "Servings must be a whole number of 1 or more, not 0.",
    "Servings must be a whole number from 1 to 100, such as 2.",
    "Servings must be a whole number from 1 to 100, such as 2.",
    "Servings must be a whole number of 100 or less, not 101.",
]
assert report.problems[0].place == place
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `settings`、`app` 和 `cli` 拥有架构 3 交给它们的内容，每个模块只引用架构 3 和 4 允许的模块。`Meal`、`Settings`、`Context`、`Command` 和 `UsageError` 持有架构 5.2 列出的内容，`Command.folder` 和 `UsageError.hint` 补上选择 6 和 9 需要的部分。`Argument`、`Arguments` 和 `FolderUse` 是辅助值，就像 F03 增加了 `Severity`，F04 增加了 `Steps`。`problem_lines`、`first_error` 和 `stop_at_error` 应当放在 `app` 里，`read_servings` 应当放在 `datafile` 里，它是 `recipes`、`settings` 和 `menus` 都能引用的唯一模块。0.2 版没有改动这些，所以第 1 轮的理由仍然成立。发现 6 已解决。2.10 第 2 步和 `datafile` 一样用 `os.path.isdir` 查看文件夹，因为 Python 3.13.18 的 `Path.is_dir` 会抛出 `PermissionError`。发现 7 已解决，而且不需要修改需求或架构。需求 3 和 Q15 说 `--data` 或 `RECIPE_MENU_DATA` 指定另一个文件夹，架构 1 写的也是这三个来源。它们都没有规定 `cli` 怎样读这个名称，所以由设计决定。没有原型或场景在值里写 `~`，v0.1-S20 用的是完整路径。规则 4 从 `main` 的 `home` 取得主文件夹，而不用自己读取 `USERPROFILE` 或 `HOME` 的 `Path.expanduser`。所以测试能给出固定的主文件夹，符合架构 8 的要求。在 Windows PowerShell 5.1 里，外部命令收到的 `~\OneDrive\recipe-menu` 原样不变，和选择 13 说的一样。发现 9，不阻塞：规则 4 检查 `Path(value).parts[0]`，而 `pathlib` 会去掉开头的 `.`。所以 `--data ./~/recipe-menu`，以及 Windows 上的 `.\~\recipe-menu`，也从主文件夹算起，而 shell 会保留 `./~` 原样。选择 13 把这条规则叫作“开头的 `~`”，并说 `cli` 不展开其他写法。接口设计师可以写明 `./~` 也算，或者改为检查值的文字：值是 `~`，或者以 `~/` 开头，或者在 Windows 上以 `~\` 开头。 |
| 遵守错误处理和命名约定 | Pass | Troy 在 2026-11-12 按推荐决定了 A 到 D，第 2 节记下了每项决定、它的理由和落实它的 PR。设计遵守这些决定修改后的架构。2.10 里的每个提示行都是 `Message` 或无（决定 A），第 9 步在 `cli` 里检查数据文件夹（决定 B），选择 8 在问题后面写出 `RUN_CHECK`（决定 D）。发现 1 已解决。规则 4 和第 3 步取第一个有值的 `--data` 和第一个有值的 `--lang`。第 4 步按命令行里的顺序检查每一个：先看有没有值，再看是不是第二个，最后看 `--lang` 的值是不是 `en` 或 `zh`。在模型里，`list --lang --lang zh` 用中文报告 `--lang 后面要写一个值。`，`list --lang zh --lang fr` 报告 `--lang 写了两次。`，`list --lang fr --lang zh` 用设置里的语言报告“fr”。设置了 `RECIPE_MENU_DATA` 时，`list --data` 读取那个文件夹的设置，并用其中的语言报告缺少的值。发现 2 已解决。选择 10 和第 4 步允许开关重复，所以 `--help --help` 和 `--version --version` 以 0 退出。发现 3 已解决。`UNKNOWN_OPTION` 用三种形式写出命令自己的选项，并保留 `RUN_HELP_FOR_OPTIONS`。对命令自己的选项，`OPTION_NEEDS_VALUE` 和 `OPTION_TWICE` 不指定提示行，因为帮助不列出这些选项。`INCOMPLETE_COMMAND` 是一个 `Plural`，只有一个命令时写“The only command that starts with”。模型在两种语言里给出了每种形式。发现 8，不阻塞：选择 9 说“提示本身已经说明了该怎么写的错误指定 `None`”。但 `INCOMPLETE_COMMAND`、`UNKNOWN_OPTION`、`TOO_FEW_ARGUMENTS` 和 `TOO_MANY_ARGUMENTS` 都说明了该怎么写，却保留提示行，因为帮助列出了命令、它们的用法和全局选项。2.10 的表格和它上面的那段话给出了确切的规则，所以开发者和测试设计师得到的答案是同一个。架构师的 `[docs]` PR 把架构 6 写成“提示本身已经说明了该怎么写的错误，比如写错的周，可以不指定这一行”，这和表格相符。选择 9 可以相应地写成“可以指定 `None`”。发现 10，不阻塞：`UNKNOWN_OPTION` 没有选项时的形式没有 `{options}`，而 `Plural` 的两种形式必须有相同的占位符（F02 设计 2.4）。所以这三种形式是一个 `Message` 加一个 `Plural`，由开发者在 `cli/messages.py` 里命名，而不是一个 `Plural`。第 1 轮的其他理由仍然成立。选择 4、5 和 10 分别遵守 `read_recipe`、需求 3 和 ADR-0005。`main` 只捕获 `UsageError` 和 `KeyboardInterrupt`，每个名称都遵守 PEP 8（架构 8）。 |
| 不和已有接口重复 | Pass | 第 1 轮的理由仍然成立。`read_servings` 把份数规则放在一个地方，三条份数提示连同文字一起移过去。F05 调用 F02 到 F04 共用的函数和提示，不重写其中任何一个。0.2 版用 `and_list` 写出 `UNKNOWN_OPTION` 的列表，和 `INCOMPLETE_COMMAND` 写出它的列表一样。开头的 `~` 用的是 `main` 已经接受的 `home`。第 2 步对文件夹的查看只是一次 `os.path.isdir` 调用。`datafile` 的查看是内部的，所以 `cli` 没有复制任何对外接口。 |
| 只依赖排序在前面的功能 | Pass | F05 使用 F01 的 `Lang`、F02 的 `text`、F03 的 `datafile`，以及 F04 加进 `datafile` 的辅助函数，并修改 F04 的 `recipes` 的内部文件。这四个功能都排在 F05 之前，并且在 main 上通过了测试。0.2 版没有增加对任何功能或包的依赖。发现 5 已解决。第 2 节写明控制台脚本不加入第三方依赖。它还写明，架构师在实现 PR 里确认 `pyproject.toml` 只多了 `[project.scripts]` 下的 `recipe-menu = "recipe_menu.cli:main"` 之后，批准 R16 警告。`docs/rules.md` 没有交给架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | 模块之间的每个假设都写在设计里。`FolderUse` 把 `cli` 要检查的内容变成每个 `Command` 的一部分，`COMMANDS` 的顺序就是帮助的顺序。`UNKNOWN_OPTION` 只读取每个命令自己声明的 `Command.options`，所以 `cli` 仍然不按名称认识任何命令。发现 4 已解决。第 2 节安排一个 mock PR 和一个实现 PR，各自按 R03 写明软限制的理由，符合 troy-mode 每个阶段一个 PR 的做法。第 1 轮给 F06 和 F07 的两点留给它们的设计。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节和 0.1 版相同。F01 到 F04 导出的名称都没有改变，`datafile` 加入三个名称，份数提示在内部文件之间移动。在架构师按 0.2 版建的模型里，分支上的测试结果是 269 个通过、2 个跳过，与分支上的代码相同。所以第 3 节写“无”是对的。第 1 轮给 PR 2 的一点仍然有效：只检查 mock 已经定义的常量的测试，在 mock 上就会通过，违反 R09。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求和架构检查了 13 项选择和决定 A 到 D。决定 A、B 和 C 修改架构 6，C 还修改 ADR-0002，所以由 Troy 决定。决定 D 修改 F05 原型，所以由 Troy 决定。决定 A 的方案 2 会修改 F11 原型和 v0.1-S15。其他选择都不修改架构、原型或需求。每个文件有 25 个代码块，每个都与另一种语言的版本相同，23 个 `python` 代码块都能解析。架构师在分支上 F01 到 F04 的代码之上，按第 2 节和第 3 节建了模型，在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 运行了 12 个示例，每个断言和全部 20 个 `# raises` 都成立。用 v0.1 的八个命令和原型里的帮助行，模型的帮助与“Help in English”的 21 行和“Help in Chinese”的 21 行完全相同，第一列宽 16。模型还给出 `recipe-menu 0.1.0`，以及两种语言下“Mistakes on the command line”和“No data folder yet”的各行。对“A broken settings file”，它的前两行就是原型的两行，后面跟着 `RUN_CHECK`。分支上的测试在模型上通过，269 个通过、2 个跳过。发现 1 到 7 不阻塞。 | 批准。Troy 批准这份设计时（R18），主会话把决定 A 到 D 交给 Troy。Troy 决定 A 到 C 之后，架构师在 F05 的 mock PR 之前，用一个文档 PR 写出架构的修改和一份 ADR。接口设计师对发现 1 到 3、6 和 7 作出决定，并在下一次修订里改正 PR 安排（发现 4）和关于控制台脚本的那句话（发现 5）。 |
| 2 | 没有阻塞问题。0.2 版解决了第 1 轮的发现 1 到 7，并记下 Troy 在 2026-11-12 对决定 A 到 D 的决定。发现 7 带来的开头的 `~` 不需要修改需求或架构。每个文件仍然有 25 个代码块，每个都与另一种语言的版本相同，23 个 `python` 代码块都能解析。架构师把模型更新到 0.2 版，在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 运行了 12 个示例，每个断言和全部 20 个 `# raises` 都成立。在第 1 轮的模型上，2.9 的示例会失败，所以它新增的断言检查的是新规则。用 v0.1 的八个命令，帮助仍然与“Help in English”和“Help in Chinese”的 21 行完全相同。模型给出的 F05 原型其他各行和第 1 轮一样，分支上的测试在模型上通过，269 个通过、2 个跳过。发现 8 到 10 不阻塞。 | 批准。接口设计师可以在合并前的一次修订里处理发现 8 到 10，也可以不改。在 F05 的 mock PR 之前，架构师用一个 `[docs]` PR 写出决定 A 到 C，采用发现 8 的措辞。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-12 | 初稿。 |
| 0.2 | 2026-11-12 | 回应架构师审查第 1 轮，并记下 Troy 在 2026-11-12 的决定。Troy 对决定 A 到 D 都接受了推荐，第 2 节写明落实它们的 PR。2.7 去掉决定 A 的方案 2。第一个有值的 `--data` 和第一个有值的 `--lang` 决定数据文件夹和语言，没有值的由第 4 步报告。开关可以重复（选择 10 和 2.10）。`UNKNOWN_OPTION` 写出命令自己的选项，命令自己的选项的 `OPTION_NEEDS_VALUE` 和 `OPTION_TWICE` 不指定提示行，`INCOMPLETE_COMMAND` 有了一个命令时的形式（选择 9 和 11，以及 2.10）。`cli` 把开头的 `~` 换成主文件夹（选择 13 和 2.10）。2.10 的第 2 步用 `os.path.isdir` 查看文件夹。第 2 节安排一个 mock PR 和一个实现 PR，各自写明 R03 软限制的理由，并由架构师批准控制台脚本的 R16 警告。需求对照表在语言一项指向 2.10 的第 3 步。2.9 和 2.10 的示例覆盖了新的情况。 |
| 1.0 | 2026-11-12 | Troy 批准。 |
