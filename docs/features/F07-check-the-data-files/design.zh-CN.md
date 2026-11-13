---
troy-doc: "F07-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-12"
status: "Troy 已于 2026-11-12 批准"
mirror-of: "design.md"
---

# F07 检查数据文件：接口设计

## 1. 功能

- 编号和名称：F07 检查数据文件
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：F05
- 软依赖：F03、F04、F06

## 2. 接口

F07 在 `src/recipe_menu/commands/check/` 里构建命令模块 `check`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.commands.check` 只导出一个名称 `CHECK_COMMAND`（2.1），它的 `__init__.py` 在 `__all__` 里列出这个名称。你输入的命令是 `recipe-menu check`（2.2）。它的提示放在 `src/recipe_menu/commands/check/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F07 在它的 mock PR 里把 `CHECK_COMMAND` 加进 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS`，这是命令功能在 `cli` 里唯一的改动（架构 4，F05 设计 2.9）。F07 原型 `docs/prototypes/F07-check.md` 展示了报告，F08 原型“In English”的第二段输出展示了没有问题的报告。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F07 提供的接口 |
| --- | --- |
| `recipe-menu check` 读取设置、目录、常备清单、每个菜谱和每个周菜单。 | `recipe-menu check`（2.2）。`CHECK_COMMAND`（2.1）里的 `run` 按 2.2 的七个步骤调用 F03 到 F06 的读取函数。 |
| 列出错误和警告及其位置。 | 2.2 的报告：先是计数行，然后是错误列表和警告列表。每个问题在一行里写出文件和位置，在下一行写出提示，和 F07 原型一样。 |
| 有错误时以退出码 1 退出。 | 2.2 的退出码：报告里有错误时为 1，否则为 0，有警告时也是 0（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。 |
| 运行 `check`，改正它报告的问题，再运行它，直到它不再报告错误（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，流程 1）。 | 有错误时的结尾行 `FIX_AND_CHECK_AGAIN`，以及没有错误时的 `NO_ERRORS` 或 `NO_ERRORS_OR_WARNINGS`（2.2）。 |
| 数据文件夹里有 1,000 个菜谱、300 种目录食材和 52 个周菜单时，`check` 在 1 秒内完成（PT01，[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。 | 2.2 的性能指标，以及下面关于耗时的规则。 |

下面每个接口都遵守这些规则：

- `check` 在包内只引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`。架构 3 里它那一行允许这些模块，它既不需要 `units`，也不需要 `shopping`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `check` 只通过 F03 到 F06 的读取函数访问磁盘，这些函数又通过 `datafile` 读取（架构 8）。它不写任何文件（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 1](../../architecture.zh-CN.md#1-背景和约束)）。它只写入 `context.out`。它自己不读取外部世界的任何东西：不读参数、环境变量、日期，也不读控制台流（架构 8）。它不保存状态。
- 读取函数遇到坏数据从不抛异常，`check` 也不抛（架构 6）。它显示读取函数返回的每个问题，不在任何问题处停下。传到 `cli` 的任何异常都是 bug。
- `CHECK_COMMAND` 是一个冻结的 `Command`（F05 设计 2.5）。F07 不增加值类型。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- `recipe-menu check` 有性能指标 PT01（2.2）。它把每个数据文件只读一次，只有 `settings.toml` 例外，因为 `cli` 启动时也读它（F05 设计 2.10）。它把 `recipes/` 和 `menus/` 各列一次，为所有菜单只建一次菜谱 ID 的集合，并在读完最后一个文件后一次写出报告。所以它的耗时与文件的大小成正比。`run` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.2 给出选择 2 到 7 的规则。

1. **帮助里的第一个命令。** `check` 是第一个真正的命令，所以 F07 之后 `COMMANDS` 里只有 `CHECK_COMMAND`（2.1）。之后的每个命令功能把自己的 `Command` 加在帮助顺序里它的位置上：F08 把 `init` 放在 `check` 前面，F09、F10、F11 和 F13 把它们的命令放在 `check` 后面（F05 设计第 2 节）。帮助保持 F05 的格式（F05 设计 2.10）。只有 `check` 时，最宽的第一格是 `--data FOLDER` 或 `--data 文件夹`，占 13 列，所以第二列从第 18 列之后开始。帮助按 F05 的写法以关于周的说明结尾，虽然在 F11 之前没有命令接受周。有 v0.1 的八个命令时，帮助给出 F05 原型的两段帮助输出，由 v0.1-S19 检查。只有 `check` 时，`recipe-menu --help` 给出这些行：

   ```text
   Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]

   Keep your recipes, plan a week's menu, and make its shopping list.

   Commands:
     check           Check every data file for mistakes.

   Options:
     --lang en|zh    The language of the output. Default: the settings, else English.
     --data FOLDER   The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
     --version       Show the version.
     --help          Show this help.

   WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.
   ```

   `recipe-menu --help --lang zh` 给出这些行：

   ```text
   用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]

   保存菜谱，排一周的菜单，并生成它的购物清单。

   命令：
     check           检查每个数据文件有没有错误。

   选项：
     --lang en|zh    输出语言。默认：设置里的语言，否则英文。
     --data 文件夹   数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
     --version       显示版本。
     --help          显示这份帮助。

   “周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。
   ```

2. **`check` 自己读取设置，从不使用 `context.settings`。** `cli` 启动时读取设置，但 `Context` 不带设置的问题，而且 `FolderUse.CHECK` 让设置里的错误通过（F05 设计选择 6）。所以 `check` 自己调用 `read_settings`（2.2 步骤 1）。它把 `read_settings` 给出的 `Settings` 或 `None` 传给 `read_week_menu`。设置出错后，`context.settings` 保存的是 `Settings()`，它的默认餐次会给出文件里并不存在的菜单问题。传入 `None` 时，`read_week_menu` 只做不依赖设置的检查（F06 设计选择 3）。设置没有错误时，这两个值相等。所以 `run` 从不读取 `context.settings`，2.1 的示例展示了这一点。再读一次设置只多读一个只有几行的文件。
3. **`recipes/` 只列一次。** `check` 调用一次 `list_recipe_ids`，然后为每个 ID 调用 `read_recipe`（2.2 步骤 4 和 5）。这两步给出的问题和顺序都与 `read_recipes` 相同（F04 设计 2.7），所以 `check` 只报告一次 `list_recipe_ids` 的问题。它不调用 `read_recipes`，因为 `read_recipes` 不给出 ID，而 `check` 计数和读取菜单都需要 ID。如果用 `read_recipes`，`check` 就要把 `recipes/` 列两次，并丢掉第二次列出的问题，而这些问题只有在两次之间没有文件变化时才与第一次相同。只列一次就让计数、`check` 读取的菜谱和菜单用同一组 ID。`recipes/` 不存在或列不出来时，`list_recipe_ids` 给出一个错误，不给出 ID（F04 设计 2.5）。这时 ID 的集合是空的，所以每个菜单的每道菜都得到 `UNKNOWN_RECIPE`。这些错误是真实的，因为没有命令能找到这些菜谱。它们排在这个文件夹本身的错误后面，文件夹恢复后它们就消失了。`read_week_menu` 不能跳过对 ID 的检查，而增加一个跳过它的选项会修改 F06 已经实现的接口。
4. **问题的顺序。** 问题按 2.2 的七个步骤排列：设置、目录、常备清单、列出 `recipes/`、按 ID 顺序的每个菜谱、列出 `menus/`，以及按时间顺序的每个周菜单。在一个步骤之内，问题按它的读取函数给出的顺序排列。这也是计数行的顺序，而且改正前面的文件可能消除后面文件里的问题，比如目录里缺少的食材。错误列表和警告列表都保持这个顺序。所以 F07 原型把 `recipes\mapo-tofu.toml` 列在 `menus\2026-W47.toml` 前面，而 v0.1-S07 接受任何顺序。
5. **计数行写出 `check` 查看过的东西。** 它总是写出设置、目录和常备清单，文件不存在或读不了时也写。错误列表再说明出了什么问题。它的菜谱数是 `list_recipe_ids` 给出的 ID 的个数，不管这些文件有没有问题。它的周菜单数是 `list_menu_weeks` 给出的周的个数。名称不是菜谱 ID 或周的文件不计入，因为 `check` 不读它，它的错误会写出它的名称。不存在或列不出来的文件夹计为 0，并给出它的错误。F07 原型“A syntax mistake”写出了 `check` 读不了的常备清单，F07 原型也把有错误的 `mapo-tofu` 算在 7 个菜谱里。空的数据文件夹给出 `Checked the settings, the catalog, the pantry, 0 recipes, and 0 week menus.` 和五个错误，2.2 的示例展示了这种情况。
6. **报告和退出码。** 无论退出码是多少，报告都写到输出流，错误流里什么也不写（架构 6）。报告依次是计数行、错误、警告，有错误时最后是结尾行（2.2）。一个问题占两行：前面空两格的文件和位置，以及前面空四格的提示。`check` 原样写出 `problem_lines` 的文字（F05 设计 2.8）。有警告而没有错误时，报告在警告前面写 `No errors.`。两者都没有时，它写 `No errors. No warnings.`。F07 原型“After the fixes”和 F08 原型展示了这两行。报告里有错误时退出码为 1，否则为 0。警告从不改变退出码（架构 6）。`check` 读完最后一个文件后才写出报告，因为前几行需要各个计数。
7. **提示里的数字。** `check` 的提示只显示计数：菜谱 ID、周、错误和警告的个数。每个计数都是内存里一个元组的长度，所以远低于 F02 的 4,300 位限制（F02 设计 2.3）。文件里的值只通过 F03 到 F06 的读取函数进入提示，而这些函数把文件里的数字限制在 15 位以内，或者显示文件里的文字（F04 设计选择 2，F05 设计 3.1，F06 设计选择 6）。所以报告里没有提示会碰到这个限制。
8. **让你去运行 `check` 的命令。** 其他每个命令都用 `stop_at_error` 在数据文件的第一个错误处停下，它的最后一行 `RUN_CHECK` 写的是 `Run "recipe-menu check" to see every problem.`（F05 设计 2.8，架构 6）。F11 的“A menu with a mistake”展示了这一行。这些命令读取的每个文件，`check` 都用同样的读取函数读取。所以只要命令传入同样的参数，就像下面的计划所说，让命令停下的错误就在 `check` 的错误之中。

F07 原型“A syntax mistake”展示的是示例文件夹的计数行，却没有展示它的警告。在示例数据上，报告还包含 `recipes\red-braised-pork.toml` 的警告，2.2 的示例展示了这一点。v0.1-S06 在 init 文件夹上运行这种情况，那里没有警告，所以按 2.2 的规则这个场景成立。产品经理可以给那一节加上警告，也可以保持原样。

以下后续功能打算以 F07 为基础。它们自己的设计决定细节。

- F08 的 `init` 写出的文件，`check` 对它们报告 `No errors. No warnings.`，有 1 个菜谱和 0 个周菜单（v0.1-S01）。所以 `init` 还要创建空文件夹 `menus/`，和需求 F08 说的一样。没有它，`check` 会报告 `menus` 和 `The folder is missing.`。在帮助里，`init` 排在 `check` 前面。
- F09、F10、F11、F13 和 F14 的命令用 `first_error` 和 `stop_at_error` 在第一个错误处停下（F05 设计 2.8）。为了让使它们停下的错误出现在 `check` 的错误之中，它们用 `check` 所用的读取函数读取每个文件，并传入同样的参数：文件里的设置、`read_catalog` 给出的目录，以及 `list_recipe_ids` 的 ID 组成的 `frozenset`。对 `FolderUse.READ` 的命令，`context.settings` 保存文件里的设置，所以 `menu show` 和 `shop` 可以传入它（F06 设计第 2 节）。
- F15 和 F16 复用 `check` 来检查一个菜谱（架构 3）。F16 原型用 `check` 的缩进展示一个问题。它们的设计给 `check` 的接口加上它们需要的东西，比如一个问题的两行缩进文字。F07 让这些函数只在内部使用，这样在有功能使用某个名称之前，不导出它。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/commands/check/__init__.py` 和 `messages.py`，可能还有一个内部文件，以及 `src/recipe_menu/cli/_commands.py` 里的那一项。它定义每条提示和字段齐全的 `CHECK_COMMAND`，所以帮助会列出 `check`，`recipe-menu check` 也能运行。它的 `run` 还不读任何文件。比如，它什么也不写并给出 0，这样报告或退出码 1 的新测试在 mock 上会失败（R09）。只检查 `CHECK_COMMAND` 的字段、帮助、某条提示，或者 `cli` 在运行 `check` 之前做的事的测试，在 mock 上也会通过，从而违反 R09，架构师在 F05 和 F06 中已经指出过这一点。最后一类的例子有数据文件夹不存在和 `recipe-menu check extra`。实现（PR 5）读取文件并写出报告。每个 PR 都在 R03 的 5 个文件以内。

### 2.1 `CHECK_COMMAND`

- 模块：check
- 功能：对 `check` 命令的描述。`cli` 读取它来解析命令行、写出帮助、检查数据文件夹并运行命令（F05 设计 2.5 和 2.9）。它的 `run` 读取每个数据文件，并写出 2.2 的报告。

签名：

```python
CHECK_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("check",)
#   help_line = CHECK_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.CHECK
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `words` | `str` 的元组 | `("check",)`。 | 无 |
| `help_line` | `Message` | `CHECK_HELP`：“Check every data file for mistakes.”和“检查每个数据文件有没有错误。”，也就是 F05 原型帮助里的那一行。 | 没有占位符。 |
| `run` | 接收一个 `Context` 和 `Arguments`、给出一个 `int` 的可调用对象 | 读取每个数据文件，并写出 2.2 的报告。 | 给出 0 或 1。 |
| `argument` | `None` | `check` 不接受参数。 | 无 |
| `options` | 空元组 | `check` 没有自己的选项。 | 无 |
| `folder` | `FolderUse` | `FolderUse.CHECK`：数据文件夹不存在时，`cli` 不运行 `check`；设置有错误时，`cli` 照样运行它（F05 设计 2.5）。 | 无 |
| `context` | `Context` | `run` 从 `cli` 得到的东西：语言、数据文件夹和输出流（F05 设计 2.4）。 | `run` 只用 `context.lang`、`context.folder` 和 `context.out`。它不用 `context.settings`（选择 2），也不用 `context.err` 和 `context.today`。 |
| `arguments` | `Arguments` | 命令行给 `check` 的东西（F05 设计 2.6）。 | 空的，因为 `check` 不声明参数和选项，所以 `cli` 不让任何值通过。`run` 不读取它。 |

- 返回值：`CHECK_COMMAND`，一个 `Command`。
  - `CHECK_COMMAND.usage` 在两种语言里都是 `check`，所以帮助显示 `check`，用法错误引用 `recipe-menu check`。
  - `CHECK_COMMAND.run(context, arguments)` 按 2.2 的七个步骤读取文件，用 `context.lang` 把 2.2 的报告写到 `context.out`，报告里有错误时给出 1，否则给出 0。

错误：无。`run` 遇到坏数据从不抛异常。数据文件夹不存在时，每个文件和文件夹各给出一个错误，和空文件夹一样（2.2）。`run` 不抛 `UsageError`，因为 `check` 不接受参数值。

- 副作用：与 2.2 相同。`run` 通过 F03 到 F06 的读取函数读取数据文件，写入 `context.out`，不写任何文件。
- 性能指标：无。PT01 从启动到退出为 `recipe-menu check`（2.2）计时，而它运行的就是这个 `run`。

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。上下文里的设置只有晚餐，而菜单在周六有午餐，所以如果 `run` 用了 `context.settings`，就会把这顿午餐报告为未知餐次。帮助来自 `COMMANDS`，F07 之后它只有 `CHECK_COMMAND`。

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings

assert CHECK_COMMAND.words == ("check",)
assert CHECK_COMMAND.usage == BiText("check", "check")
assert CHECK_COMMAND.help_line.render(Lang.EN) == "Check every data file for mistakes."
assert CHECK_COMMAND.help_line.render(Lang.ZH) == "检查每个数据文件有没有错误。"
assert (CHECK_COMMAND.argument, CHECK_COMMAND.options) == (None, ())
assert CHECK_COMMAND.folder is FolderUse.CHECK

out, err = io.StringIO(), io.StringIO()
dinner_only = Settings(Lang.ZH, (Meal.DINNER,), 3)
context = Context(Lang.EN, folder, dinner_only, out, err, date(2026, 11, 10))
assert CHECK_COMMAND.run(context, Arguments()) == 0
pork = Path("recipes", "red-braised-pork.toml")
assert out.getvalue().splitlines() == [
    "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
    "",
    "No errors.",
    "",
    "1 warning:",
    f"  {pork}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
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
assert len(english) == 14
assert english[4:6] == ["Commands:", "  check           Check every data file for mistakes."]
assert english[9].startswith("  --data FOLDER   The data folder.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[5] == "  check           检查每个数据文件有没有错误。"
assert chinese[9].startswith("  --data 文件夹   数据文件夹。")
```

### 2.2 `recipe-menu check`

- 模块：check
- 功能：检查数据文件夹的命令（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 的流程 1 和 3，以及 [4](../../requirements.zh-CN.md#4-功能点)）。它读取设置、目录、常备清单、每个菜谱和每个周菜单。它列出每个错误和每个警告及其文件和位置，有错误时以退出码 1 退出。F07 原型展示了它。

签名：

```text
recipe-menu check [--lang en|zh] [--data FOLDER]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `--lang` | `en` 或 `zh` | 报告的语言。 | 按 F05 设计 2.10 的规则。不写这个选项时，用设置里的语言；设置没写语言或有错误时，用英文（F05 设计选择 4）。 |
| `--data` | 一个文件夹 | 数据文件夹。 | 按 F05 设计 2.10 的规则。不写这个选项时，用 `RECIPE_MENU_DATA`，否则用 `~/recipe-menu`。 |
| `--help` | 开关 | 显示帮助（选择 1），不运行 `check`。 | 无 |

`check` 按以下步骤依次读取数据文件夹 `context.folder`。步骤 3、5 和 7 使用前面步骤给出的东西。

1. `read_settings(folder)` 给出 `settings`，是一个 `Settings` 或 `None`（F05 设计 2.3）。
2. `read_catalog(folder)` 给出 `catalog`，是一个 `Catalog` 或 `None`（F03 设计 2.8）。
3. `read_pantry(folder, catalog)` 读取常备清单（F03 设计 2.9）。传入 `None` 时，它只检查文件的格式。
4. `list_recipe_ids(folder)` 给出 `ids`（F04 设计 2.5）。
5. `read_recipe(folder, catalog, recipe_id)` 按顺序读取 `ids` 的每个 ID（F04 设计 2.6）。目录为 `None` 时，它只检查文件的格式。
6. `list_menu_weeks(folder)` 给出 `weeks`（F06 设计 2.8）。
7. `read_week_menu(folder, week, settings, recipe_ids)` 按顺序读取 `weeks` 的每个周（F06 设计 2.9）。`recipe_ids` 是 `frozenset(ids)`，为所有周只建一次。设置为 `None` 时，它只检查不依赖设置的部分。

报告里的问题就是这七个步骤的问题，按步骤的顺序排列，每个步骤的问题按它的读取函数给出的顺序排列（选择 4）。`check` 只把目录和设置用作后面步骤的参数，不使用读取函数给出的任何 `Pantry`、`Recipe` 或 `WeekMenu`。它不读其他文件：不读 `shop` 写的 `shopping/`，也不读 `recipes/` 或 `menus/` 里不是 `.toml` 文件的条目（F04 设计 2.5，F06 设计 2.8）。

- 返回值：退出码，以及输出流上的报告：

| 退出码 | 何时 | 输出流 |
| --- | --- | --- |
| 0 | 报告里没有错误。可以有警告。 | 输出流：报告。 |
| 1 | 报告里有错误。 | 输出流：报告。错误流里什么也不写。 |

报告依次是下面这些行，每行以换行结束：

1. 计数行：`CHECKED`，带有选择 5 的各个部分。
2. 一个空行。
3. 有错误时：按错误的个数选出的标题 `ERRORS_HEADING`，然后是每个错误的两行。没有错误时：有警告就写 `NO_ERRORS`，没有警告就写 `NO_ERRORS_OR_WARNINGS`。既没有错误也没有警告时，报告到这里结束。
4. 有警告时：一个空行，按警告的个数选出的标题 `WARNINGS_HEADING`，然后是每个警告的两行。
5. 有错误时：一个空行，然后是 `FIX_AND_CHECK_AGAIN`。

一个问题的两行就是 `problem_lines(problem, context.lang)` 的 `where` 和 `what`（F05 设计 2.8）：两个空格加上 `where`，以及四个空格加上 `what`。问题没有位置时，`where` 是文件，比如 `settings.toml`；否则是文件和位置，比如 Windows 上的 `recipes\mapo-tofu.toml, ingredient 3`。标题和其他行都不缩进。`Severity.ERROR` 的问题是错误，`Severity.WARNING` 的问题是警告。

下表给出四种报告。每种都以计数行和一个空行开头。

| 错误 | 警告 | 后面的行 | 退出码 | 原型 |
| --- | --- | --- | --- | --- |
| 没有 | 没有 | `No errors. No warnings.` | 0 | F08“In English”的第二段输出 |
| 没有 | 一个或多个 | `No errors.`、一个空行，以及各个警告 | 0 | F07“After the fixes” |
| 一个或多个 | 没有 | 各个错误、一个空行，以及结尾行 | 1 | F07“A syntax mistake”，在 init 文件夹上（v0.1-S06） |
| 一个或多个 | 一个或多个 | 各个错误、一个空行、各个警告、一个空行，以及结尾行 | 1 | F07“Errors and a warning, in English” |

`check` 的提示如下。`RECIPE_COUNT`、`WEEK_MENU_COUNT`、`ERRORS_HEADING` 和 `WARNINGS_HEADING` 是 `Plural` 值（F02 设计 2.4），各自按它的 `count` 选择。它们“多个”的形式用于 1 以外的每个计数，包括 0。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `CHECK_HELP` | `Check every data file for mistakes.` | `检查每个数据文件有没有错误。` |
| `CHECKED` | `Checked {files}.` | `已检查{files}。` |
| `THE_SETTINGS` | `the settings` | `设置` |
| `THE_CATALOG` | `the catalog` | `目录` |
| `THE_PANTRY` | `the pantry` | `常备清单` |
| `RECIPE_COUNT`，一个 | `{count} recipe` | `{count} 个菜谱` |
| `RECIPE_COUNT`，多个 | `{count} recipes` | `{count} 个菜谱` |
| `WEEK_MENU_COUNT`，一个 | `{count} week menu` | `{count} 个周菜单` |
| `WEEK_MENU_COUNT`，多个 | `{count} week menus` | `{count} 个周菜单` |
| `ERRORS_HEADING`，一个 | `{count} error:` | `{count} 个错误：` |
| `ERRORS_HEADING`，多个 | `{count} errors:` | `{count} 个错误：` |
| `WARNINGS_HEADING`，一个 | `{count} warning:` | `{count} 个警告：` |
| `WARNINGS_HEADING`，多个 | `{count} warnings:` | `{count} 个警告：` |
| `NO_ERRORS` | `No errors.` | `没有错误。` |
| `NO_ERRORS_OR_WARNINGS` | `No errors. No warnings.` | `没有错误，也没有警告。` |
| `FIX_AND_CHECK_AGAIN` | `Fix the errors and run "recipe-menu check" again.` | `改正错误后，再运行“recipe-menu check”。` |

各占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `files` | 五个部分的 `and_list`，每个部分是一个 `BiText`，顺序是：`THE_SETTINGS`、`THE_CATALOG`、`THE_PANTRY`、`RECIPE_COUNT` 和 `WEEK_MENU_COUNT`。示例数据给出“the settings, the catalog, the pantry, 7 recipes, and 1 week menu”和“设置、目录、常备清单、7 个菜谱和 1 个周菜单”。`and_list` 在“和”与数字之间加空格（F02 设计 2.6）。 |
| `count` | `RECIPE_COUNT` 里是 `list_recipe_ids` 给出的 ID 的个数，`WEEK_MENU_COUNT` 里是 `list_menu_weeks` 给出的周的个数。`ERRORS_HEADING` 里是错误的个数，`WARNINGS_HEADING` 里是警告的个数。每个都是一个元组的长度（选择 7）。 |

用这些提示，就得到 F07 原型以及 v0.1-S01、v0.1-S02、v0.1-S04 和 v0.1-S06 里的各行，比如 `Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.` 和 `已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。`。

错误：

`cli` 在运行 `check` 之前报告命令行上的错误和不存在的数据文件夹（F05 设计 2.10）。

| 错误 | 何时发生 |
| --- | --- |
| 退出码 1，报告在输出流上 | 报告里有错误（选择 6）。 |
| 退出码 1，`NO_DATA_FOLDER` 和 `RUN_INIT` 在错误流上，输出流上什么也没有 | 数据文件夹不是文件夹。因为 `check` 是 `FolderUse.CHECK`，`cli` 在 F05 设计 2.10 的步骤 9 里检查它。 |
| 退出码 2，先是 `TOO_MANY_ARGUMENTS`，然后是 `RUN_HELP_FOR_COMMANDS`，比如 `Unexpected argument "extra". Write "recipe-menu check".` | `check` 后面跟着一个词。 |
| 退出码 2，先是 `UNKNOWN_OPTION` 用于没有选项的形式，然后是 `RUN_HELP_FOR_OPTIONS`，比如 `"check" has no option "--tag". It has no options of its own.` | 四个全局选项以外的选项。 |
| 退出码 2，F05 设计 2.10 里 `--lang` 和 `--data` 的错误 | 全局选项不符合它的规则。 |
| 退出码 130 | 按下 Ctrl+C。不再写任何东西（F05 设计 2.10）；`check` 还没读完每个文件时，不写出报告。 |

- 副作用：`cli` 查看数据文件夹并读取 `settings.toml`（F05 设计 2.10）。然后 `check` 把 `settings.toml`、`catalog.toml` 和 `pantry.toml` 各读一次，把 `recipes/` 和 `menus/` 各列一次，把每个菜谱文件和每个菜单文件各读一次，全都通过 F03 到 F06 的读取函数。它把报告写到输出流。它不写任何文件，所以每个文件和文件夹都保持原来的字节和修改时间（v0.1-S23）。
- 性能指标：PT01

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本，`home` 是它外面的一个空临时文件夹（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。第一次运行做出 F07 原型的两处错误。后面几次运行先撤销它们，再各做一处别的错误：F07 原型的语法错误，然后是 F05 原型的错误设置，再加上周一的早餐。设置里没有早餐，但 `read_week_menu` 拿到的设置是 `None`，所以接受早餐（选择 2）。再下一次运行给 `red-braised-pork` 加上英文步骤，警告就消失了。最后几次运行检查空的数据文件夹、不存在的数据文件夹，以及命令行上的两处错误。

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def check(data: Path, *argv: str) -> tuple[int, list[str], str]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["check", "--data", str(data), *argv],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue()


COUNTS = "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
FIX = 'Fix the errors and run "recipe-menu check" again.'
mapo_file = Path("recipes", "mapo-tofu.toml")
pork_file = Path("recipes", "red-braised-pork.toml")
week_file = Path("menus", "2026-W47.toml")
pork_warning = [
    "1 warning:",
    f"  {pork_file}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
]

mapo, menu = folder.recipe_file("mapo-tofu"), folder.menu_file("2026-W47")
mapo_text, week_text = mapo.read_text(encoding="utf-8"), menu.read_text(encoding="utf-8")
mapo.write_text(mapo_text.replace("郫县", ""), encoding="utf-8")
menu.write_text(week_text.replace('"tomato-egg"', '"tomato-eggs"'), encoding="utf-8")
code, lines, err = check(folder.root)
assert (code, err) == (1, "")
assert lines == [
    COUNTS,
    "",
    "2 errors:",
    f"  {mapo_file}, ingredient 3",
    '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    f"  {week_file}, Monday dinner",
    '    Unknown recipe "tomato-eggs".',
    "",
    *pork_warning,
    "",
    FIX,
]
code, lines, _ = check(folder.root, "--lang", "zh")
assert code == 1
assert lines[0] == "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。"
assert lines[2:4] == ["2 个错误：", f"  {mapo_file}，食材 3"]
assert lines[8:10] == ["1 个警告：", f"  {pork_file}，步骤"]
assert lines[-1] == "改正错误后，再运行“recipe-menu check”。"

mapo.write_text(mapo_text, encoding="utf-8")
menu.write_text(week_text, encoding="utf-8")
pantry_text = folder.pantry.read_text(encoding="utf-8")
folder.pantry.write_text('# The pantry.\npantry = ["食用油", "盐" "糖"]\n', encoding="utf-8")
code, lines, _ = check(folder.root)
assert code == 1
assert lines == [
    COUNTS,
    "",
    "1 error:",
    "  pantry.toml, line 2",
    '    The file cannot be read: a closing "]" is missing.',
    "",
    *pork_warning,
    "",
    FIX,
]

folder.pantry.write_text(pantry_text, encoding="utf-8")
settings_text = folder.settings.read_text(encoding="utf-8")
folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
breakfast = week_text.replace("[monday]\n", '[monday]\nbreakfast = ["rice"]\n')
menu.write_text(breakfast, encoding="utf-8")
code, lines, _ = check(folder.root)
assert code == 1
assert lines[2:5] == [
    "1 error:",
    "  settings.toml, meals",
    '    Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
]

folder.settings.write_text(settings_text, encoding="utf-8")
menu.write_text(week_text, encoding="utf-8")
pork = folder.recipe_file("red-braised-pork")
steps = pork.read_text(encoding="utf-8") + 'en = ["Braise the pork."]\n'
pork.write_text(steps, encoding="utf-8")
assert check(folder.root) == (0, [COUNTS, "", "No errors. No warnings."], "")

empty = home / "empty"
empty.mkdir()
code, lines, _ = check(empty)
assert code == 1
assert lines == [
    "Checked the settings, the catalog, the pantry, 0 recipes, and 0 week menus.",
    "",
    "5 errors:",
    "  settings.toml",
    "    The file is missing.",
    "  catalog.toml",
    "    The file is missing.",
    "  pantry.toml",
    "    The file is missing.",
    "  recipes",
    "    The folder is missing.",
    "  menus",
    "    The folder is missing.",
    "",
    FIX,
]

missing = home / "missing"
code, lines, err = check(missing)
assert (code, lines) == (1, [])
assert err.splitlines() == [
    f"There is no data folder at {missing}.",
    'Run "recipe-menu init" to create it, or name another folder with --data.',
]
code, lines, err = check(folder.root, "extra")
assert (code, lines) == (2, [])
assert err.splitlines() == [
    'Unexpected argument "extra". Write "recipe-menu check".',
    'Run "recipe-menu --help" to see the commands.',
]
code, _, err = check(folder.root, "--tag", "素")
assert code == 2
assert err.splitlines() == [
    '"check" has no option "--tag". It has no options of its own.',
    'Run "recipe-menu --help" to see the options.',
]
```

## 3. 对已有接口的修改

无。F01 到 F06 已经实现的接口都不改变。每个导出的名称都保持它的签名和行为，F01 到 F06 的测试不用修改就能通过。F07 增加模块 `check`。它还在 `src/recipe_menu/cli/_commands.py` 的 `COMMANDS` 里加入一项；`COMMANDS` 只在 `cli` 内部使用，架构 4 让每个命令功能加入这样一项。加入这一项后，真正的 `recipe-menu` 的帮助会列出 `check`（选择 1）。只有 F05-T48 和 F05-T49 运行真正的 `COMMANDS`。它们检查未知命令、没有命令的命令行，以及帮助的第一行和最后一行，这一项不改变这些内容。其他每个测试都把自己的命令传给 `main`。

F07 按这些接口的设计使用它们，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message`、`Plural` 和 `and_list`。
- F03 的 `DataFolder`、`Problem`、`Severity`、`Catalog`、`read_catalog` 和 `read_pantry`。
- F04 的 `list_recipe_ids` 和 `read_recipe`。
- F05 在 `app` 里的 `Arguments`、`Command`、`Context`、`FolderUse` 和 `problem_lines`，在 `settings` 里的 `Settings` 和 `read_settings`，以及 `cli` 里的 `COMMANDS`。
- F06 的 `IsoWeek`、`list_menu_weeks` 和 `read_week_menu`。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `check` 是架构 3 里的命令模块，位于 `src/recipe_menu/commands/check/`，只导出 `CHECK_COMMAND`。它引用 `app`、`lang`、`text`、`datafile`、`catalog`、`recipes`、`settings` 和 `menus`，都是它那一行允许的模块。`cli` 在 `_commands.py` 里引用它，这是架构 4 允许命令功能在 `cli` 里做的唯一改动。`CHECK_COMMAND` 是架构 5.2 的 `Command`，F07 不增加值类型，菜谱 ID 以 `frozenset` 的形式传给 `menus`（架构 8）。`check` 只通过 F03 到 F06 的读取函数读取，按架构 8 的说法解析每个菜谱，并且不写任何文件（架构 1）。选择 1 成立。把 `CHECK_COMMAND` 放进 `COMMANDS` 后，架构师的模型准确给出选择 1 里每段帮助的 14 行，两种语言都是，第二列从第 18 列之后开始。发现 1，不阻塞：PT01 的余量很小。架构师按 v0.1 测试计划为 v0.1-S27 描述的方式生成了一个数据文件夹：1,000 个菜谱、300 种食材，以及 52 个各有 63 道菜的周菜单。在这次会话里、在 Troy 的电脑上，对模型运行 `python -m recipe_menu check`，5 次运行的中位数是 1.006 秒，其中第一次是冷启动，用了 5.3 秒；再运行 5 次，中位数是 1.017 秒。在进程内，`read_recipe` 读 1,000 个菜谱用了 0.77 秒，单是 `read_toml` 读同样这些文件就用了 0.27 秒。52 个菜单用了 0.08 秒，其他文件和两次列出用了 0.02 秒，启动加上各个引用用了 0.14 秒。设计已经只读最少的内容：每个文件读一次，每个文件夹列一次，所以修改 F07 的接口不会让 `check` 更快。性能分析显示，F04 的读取函数在文件没有问题时也构建位置文字和键的列表：读 1,000 个没有问题的菜谱，调用了 31,000 次 `Message.to_bitext` 和 27,000 次 `report_unknown_keys`。在性能分析下，单是 `Message.to_bitext` 就占了 `read_recipe` 1.93 秒中的 0.55 秒。只在有问题需要时才构建这些文字，是 `recipes` 和 `datafile` 内部的改动，不改变任何接口。F09 的 `list` 和 F10 的 `search` 读取同样的 1,000 个菜谱，所以它们有同样的风险。架构师建议在 F07 的实现 PR 之前，为这些读取函数做一个 `[refactor]` PR，并在 PT01 数据文件夹上计时。 |
| 遵守错误处理和命名约定 | Pass | 读取函数遇到坏数据从不抛异常，`run` 既不抛异常，也不在任何问题处停下（架构 6）。报告里有错误时退出码为 1，否则为 0，警告从不改变退出码。无论退出码是多少，报告都写到输出流，和架构 6 对 `check` 的说法一致，所以选择 6 成立。用法错误和不存在的数据文件夹仍由 `cli` 处理，和 F05 设计 2.10 以及 ADR-0008 给出的一样。每条提示都是 `check/messages.py` 里的 UPPER_SNAKE 常量，带有两种语言（架构 8）。四个 `Plural` 值的两种形式有相同的占位符（F02 设计 2.4），`files` 来自 `and_list`，所以没有手工拼出的列表或复数。选择 7 成立，因为 `check` 加进去的每个数字都是一个元组的长度。模型证实了选择 2、4 和 5。两个示例在模型上都成立，而 `run` 把 `context.settings` 传给 `read_week_menu` 的模型让两个示例都失败。模型准确给出 v0.1-S05 的三段输出、F08“In English”的第二段输出（v0.1-S01）、v0.1-S02 的中文计数行，以及 v0.1-S04 的各行。它按选择 4 的顺序给出 v0.1-S07 的 9 个错误和那个警告。对不存在的文件夹运行 `run`，给出空文件夹的 5 个错误，和 2.1 的“错误”一行说的一样。发现 2，不阻塞，请 Troy 决定：`没有错误。` 是 F16 原型“A clean edit, in Chinese”里 `已检查 mapo-tofu：没有错误。` 的说法，`没有错误，也没有警告。` 是它的延伸。架构师认为两段文字都不需要修改。Troy 在批准这份设计时一并批准它们（R18，`troy_approves_first = 16`）。 |
| 不和已有接口重复 | Pass | `check` 调用 F03 到 F06 的读取函数和 F05 的 `problem_lines`，不重写其中任何一个。选择 3 成立。先调用 `list_recipe_ids`，再为每个 ID 调用 `read_recipe`，给出的问题和顺序都与 `read_recipes` 相同（F04 设计 2.7）。这个循环重复了 `read_recipes` 里面的几行，这是保留 ID 的代价，因为 `read_recipes` 不给出 ID。两个都调用就要把 `recipes/` 列两次。新的提示说出了共用提示说不出的内容。`RUN_CHECK` 让别的命令把你引向 `check`，而 `FIX_AND_CHECK_AGAIN` 是 `check` 报告的结尾。发现 3，不阻塞：F04 设计第 2 节说 F07 调用 `read_recipes`，并且可以用 `list_recipe_ids` 计算菜谱数，F04 设计 2.7 的“功能”也把 `check` 列为调用方。选择 3 给出了理由，却没有提到这个安排。选择 3 可以补一句，说它取代了 F04 的安排。已批准的 F04 设计保持原文，因为没有接口改变。 |
| 只依赖排序在前面的功能 | Pass | F07 使用 F01 和 F02 的 `lang`、F02 的 `text`、F03 的 `datafile` 和 `catalog`、F04 的 `recipes`、F05 的 `app`、`settings` 和 `cli`，以及 F06 的 `menus`。这五个功能都排在 F07 之前，并且在 main 上通过了测试。F05 是 F07 那一行的硬依赖，F03、F04 和 F06 是它的软依赖。F01 和 F02 通过每个命令都在用的 `lang` 和 `text` 进来。给 F08 到 F16 的安排只说明每个功能打算做什么，细节留给它自己的设计，所以不约束任何后续设计。F07 只需要标准库，所以 R16 没有依赖要审查。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | 模块之间的每个假设都写在设计里。各个计数来自 `list_recipe_ids` 和 `list_menu_weeks` 的同一次调用，报告显示的也正是这两次调用的问题（选择 3 和 5）。`check` 传入 `read_settings` 给出的 `Settings` 或 `None`，而不是 `context.settings`，这正是 F05 设计第 2 节给 F07 的安排和 F06 设计选择 3 的要求（选择 2）。`check` 不知道任何读取函数的提示。它只按 `Severity` 给问题分类，并通过 `problem_lines` 写出它们。选择 8 成立。它是写给 F09 到 F14 的明确安排，不是隐性的规则。对 `FolderUse.READ` 的命令，`context.settings` 等于 `read_settings` 给出的设置，所以 `menu show` 和 `shop` 传入的设置与 `check` 相同。发现 4，不阻塞，请 Troy 决定：对于 `recipes/` 不存在的情况，架构师同意选择 3。在模型上，没有 `recipes/` 的示例文件夹给出 10 个错误：先是这个文件夹的错误，然后是 `2026-W47` 的 9 道菜各一个 `UNKNOWN_RECIPE`。每个错误都是真实的，而且它们排在文件夹的错误后面，那个错误说明了要改什么。要省掉它们，`check` 就得认出 `menus` 内部的 `UNKNOWN_RECIPE`，这就是隐性耦合。另一种做法是给 `read_week_menu` 加一个跳过 ID 检查的选项，这要通过变更流程修改 F06 已经实现的接口。列不出文件夹时跳过菜单，也会把菜单的其他问题藏起来，比如写错的周。`init` 会创建 `recipes/`，所以这种情况很少见。架构师建议 Troy 接受选择 3 描述的这些错误。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节写“无”是对的。这个 PR 只加入两个设计文件。F07 用到的每个名称都已经在分支上，签名与它的设计给出的相同。`COMMANDS` 里的那一项是架构 4 给每个命令功能的改动。在模型上，把 `CHECK_COMMAND` 放进 `COMMANDS` 后，分支上的测试结果是 380 个通过、3 个跳过，也就是分支收集到的 383 个测试，包括 F05-T48 和 F05-T49。所以 F01 到 F06 的测试都不用修改。发现 5，不阻塞，请 Troy 和产品经理决定：在示例文件夹上，模型在 F07 原型“A syntax mistake”的错误后面给出 `recipes\red-braised-pork.toml` 的警告。所以在原型所说的文件夹上，那一节与 2.2 不一致。v0.1-S06 在 init 文件夹上运行，它成立，因为模型给出那一节的各行，只是计数行换成 init 文件夹的。第 2 节建议给那一节加上警告。只做这个改动会让 v0.1-S06 不成立，因为它期望第一行之后的各行与那一节相同，所以产品经理还得修改 v0.1-S06。把那一节的计数行改成 `Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.`，并说明那一节在 init 文件夹上运行，就能让 v0.1-S06 按原文成立。修改原型由 Troy 决定，和 F05 的决定 D 一样。给后续阶段的一点：只检查退出码 0 或只检查帮助的测试，在第 2 节的 mock 上会通过，因为 mock 的 `run` 什么也不写并给出 0，所以这样的测试违反 R09。`run` 的每个新测试还要检查报告的各行。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0008、F05、F07、F08 和 F16 原型，以及 v0.1-S01、v0.1-S02、v0.1-S04 到 v0.1-S07 和 v0.1-S27，检查了选择 1 到 8 以及接口设计师提出的三点。每个文件有 6 个代码块，每个都与另一种语言的版本相同，两个文件的 480 行在标题、表格行和列表项上逐一对应。3 个 `python` 代码块都能解析。架构师在分支上 F01 到 F06 的代码之上，按第 2 节建了模型，并把 `CHECK_COMMAND` 放进 `COMMANDS`。模型在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 运行了 2.1 和 2.2 的示例，每个断言都成立。模型给出选择 1 的帮助，以及第 1 项和第 2 项的备注里列出的原型和场景的输出。分支上的测试在模型上通过，380 个通过、3 个跳过。这个 PR 本身没有运行测试，因为它不改代码。发现 1 到 5 都不阻塞。 | 批准。Troy 批准这份设计和它的两段新中文文字（发现 2，R18，`troy_approves_first = 16`），并决定发现 4 和 5。架构师建议在 F07 的实现 PR 之前做发现 1 的 `[refactor]` PR。接口设计师可以在修订版里处理发现 3，也可以不处理。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-12 | 初稿。 |
| 1.0 | 2026-11-12 | Troy 批准。 |
