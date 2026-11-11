---
troy-doc: "F03-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "design.md"
---

# F03 目录和常备清单：接口设计

## 1. 功能

- 编号和名称：F03 目录和常备清单
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：F01、F02

## 2. 接口

F03 创建基础层模块 `datafile`，并构建领域层模块 `catalog`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.datafile` 导出 `DataFolder`、`Problem`、`Severity`、`read_toml`，以及关于文件结构的提示（2.10）：`EMPTY_ITEM`、`EMPTY_TEXT`、`ITEM_NOT_A_TEXT`、`MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TABLE`、`NOT_A_TEXT` 和 `UNKNOWN_KEY`。`recipe_menu.catalog` 导出 `Catalog`、`Category`、`Ingredient`、`Pantry`、`Tag`、`read_catalog` 和 `read_pantry`。每个模块的 `__init__.py` 在 `__all__` 里列出自己的名称。每个模块把自己的提示放在自己的 `messages.py` 里（架构 8）。每个模块背后的其他文件由开发工程师决定。文件就是 `docs/prototypes/example-data.md` 里的那些文件，F07 原型展示了 `check` 怎样报告它们的问题。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F03 提供的接口 |
| --- | --- |
| 读取目录：按顺序排列的购物分类；食材及其中文名、英文名、分类和默认单位；标签及其中文名和英文名。 | `read_catalog`（2.8）。它给出一个 `Catalog`（2.5），里面是按文件顺序排列的 `Category`、`Ingredient` 和 `Tag` 值（2.4）。 |
| 按任一语言的名称查找食材或标签。 | `Catalog.find_ingredient` 和 `Catalog.find_tag`，使用 2.6 的匹配规则。 |
| 读取常备清单。 | `read_pantry`（2.9）。它给出一个 `Pantry`（2.7）。 |
| 报告重复的名称、未知的分类、未知的单位和常备清单里未知的食材。 | `read_catalog` 和 `read_pantry` 返回的 `Problem` 值（2.2），每个都带有它的文件和位置。 |
| `datafile` 负责数据文件夹里各文件的路径、读取 TOML 文件，以及带位置的问题（架构 3）。 | `DataFolder`（2.1）、`Severity` 和 `Problem`（2.2）、`read_toml`（2.3），以及关于文件结构的提示（2.10）。 |

下面每个接口都遵守这些规则：

- `datafile` 在包内只引用 `lang` 和 `text`。`catalog` 只引用 `lang`、`units`、`text` 和 `datafile`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `read_toml` 是唯一打开文件的接口，`read_catalog` 和 `read_pantry` 都通过它读取自己的文件。没有接口写文件、打印、读环境变量或保存状态。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。它跳过出错的部分，记下一个 `Problem`，然后继续，所以运行一次 `check` 就能列出所有问题。下面各个“错误”表里的异常都来自错误的调用，也就是 bug。
- 每个值都是带 `slots=True` 的冻结 dataclass 或者枚举，其中的集合用元组或 frozenset（架构 8）。唯一的例外是 `read_toml` 给出的表。它就是 `tomllib` 给出的结果，只交给请求它的读取函数，由读取函数把它变成值。原始的 TOML 表不会再往外传（架构 5）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F03 的接口都没有性能指标。`check`、`show` 和 `shop` 要在 PT01 的 1 秒内读完有 300 种食材的目录。所以 `read_catalog` 和 `read_pantry` 的耗时与文件大小成正比。每次按名称查找的耗时与名称的长度成正比，与目录的大小无关。

以下后续功能打算调用这些接口：

- F04 用 `read_toml` 读取每个菜谱文件，并用 2.10 的提示报告结构不对的地方。它用 `find_ingredient` 和 `find_tag` 查找菜谱的食材和标签，并把每个问题报告为一个 `Problem`。
- F05 用 `read_toml` 读取设置，并用 2.10 的提示报告结构不对的地方。`cli` 构造 `DataFolder`。
- F06 用 `read_toml` 从 `DataFolder.menu_file` 读取周菜单，并用 2.10 的提示报告结构不对的地方。
- F07 调用 `read_catalog`，再用得到的目录调用 `read_pantry`；目录读不了时，传入 `None`。它打印每个问题的文件、位置和文字。
- F08、F11 和 F13 给 `datafile` 加入它们需要的写文件功能（架构 3）。F08 显示分类、食材和标签的数量，以及常备清单里食材的数量。
- F09 用 `find_tag` 查找 `list --tag` 的标签。
- F12 按 `Catalog.categories` 和 `Catalog.ingredients` 排列购物清单，并去掉 `Pantry.ingredients`。
- F13 把清单保存到 `DataFolder.shopping_file`。F13 原型的英文常备食材一行写的是“cooking oil”和“Sichuan pepper”，而目录里写的是“Cooking oil”和“Sichuan pepper”。没有规则能把目录里的名称变成这一行，而目录按原样保存每个名称，所以要由 F13 的设计决定这一行。
- F15 用 `find_ingredient` 检查你输入的每样食材。

### 2.1 `DataFolder`

- 模块：datafile
- 功能：数据文件夹，以及其中每个文件的路径（[架构 5.1](../../architecture.zh-CN.md#51-数据文件)）。它是唯一知道各文件名称的地方（架构 5.2）。`cli` 根据 `--data`、`RECIPE_MENU_DATA` 或 `~/recipe-menu` 构造它（F05），并通过 `Context` 传下去。

签名：

```python
@dataclass(frozen=True, slots=True)
class DataFolder:
    root: Path

    @property
    def settings(self) -> Path: ...

    @property
    def catalog(self) -> Path: ...

    @property
    def pantry(self) -> Path: ...

    @property
    def recipes(self) -> Path: ...

    @property
    def menus(self) -> Path: ...

    @property
    def shopping(self) -> Path: ...

    def recipe_file(self, recipe_id: str) -> Path: ...

    def menu_file(self, week: str) -> Path: ...

    def shopping_file(self, week: str) -> Path: ...

    def relative(self, path: Path) -> Path: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `root` | `Path` | 数据文件夹，比如 `C:\Users\Troy\recipe-menu`。 | 无。`DataFolder` 不检查文件夹是否存在。 |
| `recipe_id` | `str` | 菜谱 ID，比如 `tomato-egg`。 | 符合 F04 规则的 ID。`recipe_file` 只检查“错误”表里的规则。 |
| `week` | `str` | 文件名里写的 ISO 周，比如 `2026-W47`。 | F06 写出的周。`menu_file` 和 `shopping_file` 只检查“错误”表里的规则。 |
| `path` | `Path` | `root` 里面的一个路径，比如 `folder.catalog`。 | 在 `root` 里面。 |

- 返回值：每个属性和方法都按下表给出一个 `Path`。它从 `root` 拼出路径，不查看磁盘上的任何东西。

| 接口 | 路径 |
| --- | --- |
| `settings` | `root / "settings.toml"` |
| `catalog` | `root / "catalog.toml"` |
| `pantry` | `root / "pantry.toml"` |
| `recipes` | `root / "recipes"` |
| `menus` | `root / "menus"` |
| `shopping` | `root / "shopping"` |
| `recipe_file(recipe_id)` | `root / "recipes" / f"{recipe_id}.toml"` |
| `menu_file(week)` | `root / "menus" / f"{week}.toml"` |
| `shopping_file(week)` | `root / "shopping" / f"{week}.md"` |
| `relative(path)` | `path.relative_to(root)`，比如 `Path("recipes", "mapo-tofu.toml")`。`Problem` 用它写出自己的文件（架构 5.3）。 |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `recipe_file`、`menu_file` 或 `shopping_file` 收到的名称为空，是 `.` 或 `..`，或者含有 `/`、`\`、`:` 或空字符 U+0000。这样的名称可能给出另一个文件的路径。`../catalog` 给出目录文件。在 Windows 上，`pathlib` 把 `C:catalog.toml` 读作 C 盘上的文件 `catalog.toml`。数据文件夹在 C 盘上时，`recipe_file("C:catalog")` 给出 `recipes` 里的 `catalog.toml`。数据文件夹在别的盘上时，它给出 C 盘当前文件夹里的 `catalog.toml`，在数据文件夹之外。这条规则在 Windows 和 Linux 上相同。 |
| `ValueError` | `relative` 收到的路径不在 `root` 里面。 |

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder

folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
assert folder.catalog == folder.root / "catalog.toml"
assert folder.recipes == folder.root / "recipes"
assert folder.recipe_file("tomato-egg") == folder.recipes / "tomato-egg.toml"
assert folder.menu_file("2026-W47") == folder.root / "menus" / "2026-W47.toml"
assert folder.shopping_file("2026-W47") == folder.shopping / "2026-W47.md"
assert folder.relative(folder.recipe_file("mapo-tofu")) == Path("recipes", "mapo-tofu.toml")
folder.recipe_file("../catalog")  # raises ValueError
folder.recipe_file("C:catalog")  # raises ValueError
folder.relative(Path("D:/other/catalog.toml"))  # raises ValueError
```

### 2.2 `Severity` 和 `Problem`

- 模块：datafile
- 功能：数据文件里的一个问题，带有它的严重程度、文件、位置、提示和提示的值（[架构 5.2](../../architecture.zh-CN.md#52-值)）。读取函数返回问题，从不把问题当异常抛出。`Severity` 说明问题是错误还是警告：错误让命令以 1 退出，警告从不改变退出码（架构 6）。

签名：

```python
class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Problem:
    severity: Severity
    file: Path
    place: BiText | None
    message: Message
    values: tuple[tuple[str, MessageValue], ...] = ()

    @classmethod
    def error(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem: ...

    @classmethod
    def warning(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem: ...

    def text(self, lang: Lang) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `severity` | `Severity` | 错误或警告。 | 无 |
| `file` | `Path` | 相对于数据文件夹的文件路径，来自 `DataFolder.relative`。 | 不是绝对路径。 |
| `place` | `BiText` 或 `None` | 文件里的位置，两种语言都有，比如“line 2”和“第 2 行”，或“ingredient 3”和“食材 3”。 | 问题属于整个文件、没有行号或字段时为 `None`，比如文件不存在，或者文件顶层有未知的键。 |
| `message` | `Message` | 哪里有错，以及该怎么办。 | 无 |
| `values` | （名称，`MessageValue`）对组成的元组 | `message` 每个占位符的值。 | 每个占位符一对，不多不少。`Problem` 按名称给这些对排序，所以它们的顺序无关紧要。 |
| `error` 和 `warning` 的 `values` | `MessageValue` 关键字参数 | 同样的值，按名称给出。 | 与字段 `values` 相同。 |
| `lang` | `Lang` | `text` 写出的语言。 | 无 |

- 返回值：一个 `Problem`。
  - `Problem.error(file, place, message, **values)` 给出 `Severity.ERROR` 的问题，`Problem.warning` 给出 `Severity.WARNING` 的问题。它们的前三个参数只能按位置传入，所以提示也可以有名为 `file`、`place` 或 `message` 的占位符。
  - `text(lang)` 给出 `message.render(lang, **values)`。F07 可以在文件后面显示 `place.get(lang)`，在它们下面显示 `text(lang)`。
  - `str(problem.file)` 用系统的分隔符写出路径，比如 Windows 上的 `recipes\mapo-tofu.toml`（架构 6）。
  - 两个问题的五个字段都相等时，它们相等。`Problem` 可以求哈希。

错误：

创建 `Problem` 时会用两种语言把它的提示写出一次，所以错误的值会立即失败。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `file` 是绝对路径。 |
| `ValueError` | `values` 里的名称与 `message` 的占位符不完全一致，或者某个名称在 `values` 里出现了两次。 |
| `TypeError` | 某个值不是 `str`、`int` 或 `BiText`，或者是 `bool` 或 `enum.Enum` 成员，`Message.render` 会拒绝它（F02 设计 2.3）。 |
| `ValueError` | 某个 `int` 值超过 4,300 位（F02 设计 2.3）。 |

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN_TAG = Message('Unknown tag "{tag}".', "未知标签“{tag}”。")
NO_ENGLISH_STEPS = Message("No English steps.", "没有英文步骤。")
rice = Path("recipes", "rice.toml")
tags = BiText("tags", "标签")

problem = Problem.error(rice, tags, UNKNOWN_TAG, tag="breakfast")
assert problem.severity is Severity.ERROR
assert problem.values == (("tag", "breakfast"),)
assert problem.text(Lang.EN) == 'Unknown tag "breakfast".'
assert problem.text(Lang.ZH) == "未知标签“breakfast”。"
assert problem == Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG, (("tag", "breakfast"),))

warning = Problem.warning(rice, BiText("steps", "步骤"), NO_ENGLISH_STEPS)
assert warning.severity is Severity.WARNING
assert warning.values == ()

Problem.error(rice, tags, UNKNOWN_TAG)  # raises ValueError
Problem.error(Path.cwd() / "rice.toml", None, NO_ENGLISH_STEPS)  # raises ValueError
Problem.error(rice, tags, UNKNOWN_TAG, tag=None)  # raises TypeError
```

### 2.3 `read_toml`

- 模块：datafile
- 功能：按 TOML 1.0 读取一个数据文件（ADR-0002）。它给出文件的表，或者给出一个说明文件为什么读不了的 `Problem`。F03 到 F06 的读取函数都用它读取每个文件，所以每种语法错误都得到相同的提示。

签名：

```python
def read_toml(folder: DataFolder, path: Path) -> dict[str, object] | Problem: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `path` | `Path` | 要读取的文件，比如 `folder.catalog`。 | 在 `folder.root` 里面。 |

- 返回值：文件的表，类型为 `dict[str, object]`；或者一个 `Problem`，严重程度为 `Severity.ERROR`，文件为 `folder.relative(path)`。调用方把表变成值，从不把表再传出去（架构 5）。

`read_toml` 按这些步骤工作：

1. 它读取文件的字节。读取因 `OSError` 失败时，问题没有位置。它的提示取自下表第一个符合的行：

   | 条件 | 提示 |
   | --- | --- |
   | `path.is_dir()` 为真。在 Windows 上，读取文件夹会因 `PermissionError` 失败，所以 `read_toml` 先检查这一行，再检查其他行。 | `FILE_IS_FOLDER` |
   | 错误是 `FileNotFoundError`，或者因为路径里的某个文件夹其实是文件而出现的 `NotADirectoryError`。 | `FILE_MISSING` |
   | 错误是 `PermissionError`。 | `ACCESS_DENIED` |
   | 其他任何 `OSError`。 | `SYSTEM_ERROR`。它的值 `reason` 是错误的 `strerror`；`strerror` 为 `None` 或空时，是错误的类名，比如 `OSError`。 |

2. 它用 `bytes.decode` 和 `utf-8-sig` 编解码器一次解码全部字节，出错时严格报错（架构 8）。文件带不带字节顺序标记，这个编解码器都能读取。`UnicodeDecodeError` 给出 `NOT_UTF8`，位置是第一个不属于 UTF-8 的字节所在的行。这一行的行号等于 `error.object[:error.start]` 里 LF 字节的个数加一。文件以字节顺序标记开头时，`error.object` 是标记之后的字节，`error.start` 也从那里算起。所以字节 `EF BB BF 61 0A FF`，也就是字节顺序标记、`a`、一个换行和字节 FF，给出第 2 行。如果在文件本身的字节里数到 `error.start` 为止，就会得到第 1 行。
3. 它用 `tomllib.loads` 解析文字。`tomllib.TOMLDecodeError` 给出一个问题，位置是解析器停下的那一行，提示按下表取自解析器给出的原因。另外还有两种异常，来自 TOML 1.0 或解析器不接受的文件：
   - 超过 4,300 位的十进制整数会抛出普通的 `ValueError`，因为 Python 不把这样的字符串转成 `int`（`sys.get_int_max_str_digits()`）。TOML 1.0 要求解析器拒绝放不进 64 位的整数，所以这样的数字是文件里的错误。`read_toml` 给出 `NUMBER_TOO_LONG`。
   - 嵌套几百层的列表或表会抛出 `RecursionError`。在限制键的部分个数的 Python 上，点号分隔的部分超过 1,000 个的键也会抛出它：Python 3.13.18 和 3.14.10 有这个限制，3.14.3 能解析这样的键。`read_toml` 给出 `NESTED_TOO_DEEPLY`。只有嵌套在每个版本上都会抛出这个异常，所以测试 `NESTED_TOO_DEEPLY` 时用嵌套。

   架构 6 为语法错误列出的是 `TOMLDecodeError` 和 `UnicodeDecodeError`。这两种异常是同一类错误，所以 `read_toml` 在同一个地方捕获它们，没有数据文件会导致回溯信息。`except` 子句依次写明 `tomllib.TOMLDecodeError`、`ValueError` 和 `RecursionError`。`TOMLDecodeError` 是 `ValueError` 的子类，所以它的子句在前。

`read_toml` 这样找出 `TOMLDecodeError` 的原因和行号（ADR-0002）：

- 原因是错误的文字去掉 `tomllib` 加上的结尾 ` (at line N, column M)` 或 ` (at end of document)` 之后的部分。在 Python 3.14 上，原因等于错误的 `msg` 属性。
- Python 有 `lineno` 属性时（3.14），行号就是错误的 `lineno`。在 Python 3.13 上，行号是结尾 ` (at line N, column M)` 里的 N。结尾是 ` (at end of document)` 时，行号等于文字里换行的个数加一，这也是 Python 3.14 在这种情况下给出的 `lineno`。
- 错误既没有 `lineno`、也没有这样的结尾时，问题没有位置。只有不是由 `tomllib` 抛出的 `TOMLDecodeError` 才可能两者都没有。

`ValueError` 和 `RecursionError` 不带位置，所以 `read_toml` 自己找出行号。行号是满足下面条件的第一行 N：只解析第 1 行到第 N 行（每行带上它的换行）时，再次抛出同一种异常，也就是不是 `TOMLDecodeError` 的 `ValueError`，或者 `RecursionError`。对于位数太多的数字，这就是数字所在的行，因为解析器按顺序读取文字，在数字之前结束的文字永远读不到这个数字。用二分查找找出 N，大约需要再解析行数的 log2 次。只有带这种错误的文件才付出这些代价。

`read_toml` 认识下表里的原因。Python 3.13 和 3.14 给出的原因相同，它们的 `tomllib` 源码可以证明（已在 Python 3.13.18 和 3.14.10 中核对）。其他任何原因，以及以后的 Python 新加的原因，都给出 `NOT_TOML`。最后一列给出导致每个原因的一种错误写法。

| `tomllib` 给出的原因 | 提示 | 导致它的一种错误写法 |
| --- | --- | --- |
| `Unclosed array`、`Expected ']' at the end of a table declaration` 和 `Expected ']]' at the end of an array declaration` | `MISSING_BRACKET` | `pantry = ["盐" "糖"]`，两项之间少了逗号，和 F07 原型“A syntax mistake”一样。`[monday` 少了 `]`。 |
| `Unclosed inline table` | `MISSING_BRACE` | `{ zh = "番茄" en = "Tomato" }`，两个键之间少了逗号。花括号里的表在 `}` 之前就换了行。 |
| `Unterminated string`、`Illegal character '\n'`、`Found invalid character '\n'`、`Expected "'"` 和 `Expected "'''"` | `MISSING_QUOTE` | `zh = "番茄`，少了结尾的 `"`。在两个带 `'\n'` 的原因里，`\n` 是 `\` 和 `n` 两个字符，这是 `repr` 写出换行的方式。 |
| `Invalid value` | `BAD_VALUE` | `zh = 番茄` 没加引号，`zh = “番茄”` 用了中文引号，或者 `zh =` 后面没有值。 |
| `Expected '=' after a key in a key/value pair` | `MISSING_EQUALS` | `zh "番茄"` 或 `zh: "番茄"`。 |
| `Invalid initial character for a key part` | `BAD_KEY` | `{ zh = "番茄", }`，以逗号结尾。花括号里的表在逗号之后换了行。`{ 中文 = "番茄" }`。 |
| `Expected newline or end of document after a statement` | `EXTRA_TEXT` | `servings = 2 份`，或者一行写了两个键。 |
| `Invalid statement` | `BAD_LINE` | 以 `番茄` 或 `“` 开头的一行。 |
| `Cannot overwrite a value`，以及以 `Cannot declare `、`Duplicate inline table key `、`Cannot mutate immutable namespace ` 或 `Cannot redefine namespace ` 开头的原因 | `DEFINED_TWICE` | `servings = 2` 写了两次，`[monday]` 写了两次，或者 `{ zh = "葱", zh = "大葱" }`。 |
| `Unescaped '\' in a string`、`Invalid hex value` 和 `Escaped character is not a Unicode scalar value` | `BAD_ESCAPE` | `editor = "C:\Program Files\notepad.exe"`，其中 `\P` 不是转义。`"C:\users"` 给出 `Invalid hex value`，因为 `\u` 开始了一个转义。 |
| 其他以 `Illegal character ` 或 `Found invalid character ` 开头的原因 | `CONTROL_CHARACTER` | 含有控制字符的文字或注释，比如 U+0000，或者后面没有 U+000A 的 U+000D。 |
| 其他任何原因，比如 `Invalid date or datetime` | `NOT_TOML` | `day = 2026-11-31`。 |

`datafile` 的提示如下。`LINE` 是每个带行号的问题的位置。`MISSING_BRACE` 的模板里，花括号 `}` 写两次（F02 设计 2.2）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `LINE` | `line {line}` | `第 {line} 行` |
| `FILE_MISSING` | `The file is missing.` | `文件不存在。` |
| `FILE_IS_FOLDER` | `The file cannot be read: it is a folder.` | `无法读取文件：它是一个文件夹。` |
| `ACCESS_DENIED` | `The file cannot be read: access is denied.` | `无法读取文件：没有访问权限。` |
| `SYSTEM_ERROR` | `The file cannot be read. The system says: {reason}` | `无法读取文件。系统提示：{reason}` |
| `NOT_UTF8` | `The file cannot be read: it is not UTF-8 text. Save it as UTF-8.` | `无法读取文件：它不是 UTF-8 文本。请把它另存为 UTF-8。` |
| `MISSING_BRACKET` | `The file cannot be read: a closing "]" is missing.` | `无法读取文件：缺少右方括号“]”。` |
| `MISSING_BRACE` | `The file cannot be read: a closing "}" is missing. A table in braces must be on one line.` | `无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。` |
| `MISSING_QUOTE` | `The file cannot be read: a closing quotation mark is missing.` | `无法读取文件：缺少结尾的引号。` |
| `BAD_VALUE` | `The file cannot be read: a value is missing or not valid. Write a text in straight quotation marks, such as "Tomato".` | `无法读取文件：缺少值，或者值写得不对。文字要放在英文双引号里，比如 "番茄"。` |
| `MISSING_EQUALS` | `The file cannot be read: an "=" is missing after a key.` | `无法读取文件：键后面缺少“=”。` |
| `BAD_KEY` | `The file cannot be read: a key is missing or not valid. A table in braces must be on one line, and it cannot end with a comma.` | `无法读取文件：缺少键，或者键写得不对。花括号里的表必须写在一行里，而且不能以逗号结尾。` |
| `EXTRA_TEXT` | `The file cannot be read: something follows the value on this line. Write one key and its value on each line.` | `无法读取文件：这一行的值后面还有别的内容。每行只写一个键和它的值。` |
| `BAD_LINE` | `The file cannot be read: this line does not start with a key, "[", or "#".` | `无法读取文件：这一行的开头不是键、“[”或“#”。` |
| `DEFINED_TWICE` | `The file cannot be read: a key or a table is defined twice.` | `无法读取文件：同一个键或表定义了两次。` |
| `BAD_ESCAPE` | `The file cannot be read: a "\" in a text does not start a valid escape. Write "\\" for one "\", or put the text in single quotation marks.` | `无法读取文件：文字里的“\”没有构成有效的转义。一个“\”要写成“\\”，或者把文字放在单引号里。` |
| `CONTROL_CHARACTER` | `The file cannot be read: this line holds a control character, which TOML does not allow.` | `无法读取文件：这一行有 TOML 不允许的控制字符。` |
| `NOT_TOML` | `The file cannot be read: this line is not valid TOML.` | `无法读取文件：这一行不是有效的 TOML。` |
| `NUMBER_TOO_LONG` | `The file cannot be read: a number has too many digits.` | `无法读取文件：有一个数字的位数太多。` |
| `NESTED_TOO_DEEPLY` | `The file cannot be read: lists or tables are nested too deeply.` | `无法读取文件：列表或表嵌套得太深。` |

`MISSING_BRACKET` 的英文就是 F07 原型“A syntax mistake”里的那一行。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `path` 不在 `folder.root` 里面，由 `DataFolder.relative` 发现。`read_toml` 在读取之前检查这一点。 |

- 副作用：读取 `path` 处的文件。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。

```python
from pathlib import Path

from recipe_menu.datafile import Problem, read_toml
from recipe_menu.lang import BiText, Lang

assert read_toml(folder, folder.pantry) == {"pantry": ["食用油", "盐", "糖", "生抽", "花椒"]}

folder.pantry.write_text('# The pantry.\npantry = ["食用油", "盐" "糖"]\n', encoding="utf-8")
problem = read_toml(folder, folder.pantry)
assert isinstance(problem, Problem)
assert problem.file == Path("pantry.toml")
assert problem.place == BiText("line 2", "第 2 行")
assert problem.text(Lang.EN) == 'The file cannot be read: a closing "]" is missing.'
assert problem.text(Lang.ZH) == "无法读取文件：缺少右方括号“]”。"

folder.settings.unlink()
missing = read_toml(folder, folder.settings)
assert isinstance(missing, Problem)
assert missing.place is None
assert missing.text(Lang.EN) == "The file is missing."

digits = "servings = " + "1" * 5000 + "\n"
folder.settings.write_text('language = "en"\n' + digits, encoding="utf-8")
too_long = read_toml(folder, folder.settings)
assert isinstance(too_long, Problem)
assert too_long.place == BiText("line 2", "第 2 行")
assert too_long.text(Lang.EN) == "The file cannot be read: a number has too many digits."

folder.catalog.write_bytes(b"tags = []\n# caf\xe9\n")
not_utf8 = read_toml(folder, folder.catalog)
assert isinstance(not_utf8, Problem)
assert not_utf8.place == BiText("line 2", "第 2 行")

folder.catalog.write_bytes(b"\xef\xbb\xbftags = []\n\xff\n")
with_mark = read_toml(folder, folder.catalog)
assert isinstance(with_mark, Problem)
assert with_mark.place == BiText("line 2", "第 2 行")

read_toml(folder, Path("D:/other/catalog.toml"))  # raises ValueError
```

### 2.4 `Category`、`Ingredient` 和 `Tag`

- 模块：catalog
- 功能：目录的组成部分（[架构 5.2](../../architecture.zh-CN.md#52-值)）。`Category` 是一个购物分类，目录里分类的顺序就是购物顺序。`Ingredient` 带有它两种语言的名称、分类和默认单位。`Tag` 带有它两种语言的名称。菜谱和常备清单引用同一个 `Ingredient` 值，所以购物清单按同一对象合并食材。

签名：

```python
@dataclass(frozen=True, slots=True)
class Category:
    key: str
    name: BiText


@dataclass(frozen=True, slots=True)
class Ingredient:
    name: BiText
    category: Category
    unit: Unit | None = None


@dataclass(frozen=True, slots=True)
class Tag:
    name: BiText
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `key` | `str` | 分类的键，食材的 `category` 用它指明分类，比如 `produce`。 | 不只是空白字符。 |
| `Category` 的 `name` | `BiText` | 分类的名称，比如“Vegetables and fruit”和“蔬菜水果”。 | 已设置的每种语言都不只是空白字符。可以缺一种语言，因为分类的另一个名称写错时，`read_catalog` 仍保留这个分类，让它的食材还能找到它（2.8）。 |
| `Ingredient` 或 `Tag` 的 `name` | `BiText` | 英文名和中文名，比如“Scallion”和“葱”。 | 两种语言都已设置，而且都不只是空白字符。 |
| `category` | `Category` | 食材的购物分类。 | 目录里的一个分类（2.5）。 |
| `unit` | `Unit` 或 `None` | 没写单位的数量使用的默认单位（F01 设计 2.7）。 | 食材没有默认单位时为 `None`。 |

- 返回值：一个 `Category`、`Ingredient` 或 `Tag`。所有字段都相等时，两个值相等；每个值都可以求哈希。`Catalog` 里没有名称相互匹配的两种食材或两个标签（2.5），所以同一个目录里两个相等的食材就是同一个对象。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `Category`：`key` 为空或只有空白字符，或者 `name` 里已设置的某种语言为空或只有空白字符。 |
| `ValueError` | `Ingredient` 或 `Tag`：`name` 的某种语言为 `None`、为空，或者只有空白字符。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.catalog import Category, Ingredient, Tag
from recipe_menu.lang import BiText, Lang
from recipe_menu.units import Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
assert scallion.category is produce
assert scallion.unit is Unit.STALK
assert Ingredient(BiText("Tomato", "番茄"), produce).unit is None
assert Category("other", BiText(zh="其他")).name.get(Lang.EN) == "其他"
assert Tag(BiText("quick", "快手")) == Tag(BiText("quick", "快手"))

Ingredient(BiText(zh="葱"), produce)  # raises ValueError
Tag(BiText("quick", " "))  # raises ValueError
Category(" ", BiText("Other", "其他"))  # raises ValueError
```

### 2.5 `Catalog`

- 模块：catalog
- 功能：按文件顺序排列的分类、食材和标签（[架构 5.2](../../architecture.zh-CN.md#52-值)）。它按任一语言的名称找到食材或标签（2.6）。测试和 F12 可以不用文件，直接在代码里构造一个目录。

签名：

```python
@dataclass(frozen=True, slots=True)
class Catalog:
    categories: tuple[Category, ...]
    ingredients: tuple[Ingredient, ...]
    tags: tuple[Tag, ...]

    # Methods: find_ingredient and find_tag (2.6).
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `categories` | `Category` 值组成的元组 | 按购物顺序排列的分类。 | 按 2.6 的规则，没有两个键相互匹配。两个分类可以同名，因为没有接口按名称查找分类。`read_catalog` 会报告同名的分类（2.8）。 |
| `ingredients` | `Ingredient` 值组成的元组 | 按目录顺序排列的食材，购物清单上同一分类的各行按这个顺序排列。 | 每种食材的 `category` 都在 `categories` 里。没有两种食材的名称相互匹配。 |
| `tags` | `Tag` 值组成的元组 | 按文件顺序排列的标签。 | 没有两个标签的名称相互匹配。 |

- 返回值：一个 `Catalog`。它在创建时为名称建立索引，所以 2.6 的每次查找耗时都与目录的大小无关。三个元组都相等时，两个目录相等。`Catalog` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 按 2.6 的规则，两个分类的键相互匹配。 |
| `ValueError` | 某种食材的 `category` 不在 `categories` 里。 |
| `ValueError` | 按 2.6 的规则，两种食材的名称相互匹配，或者两个标签的名称相互匹配，不论是同一种语言还是不同语言。同一种食材或同一个标签的两个名称可以相互匹配。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.lang import BiText

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
pork = Ingredient(BiText("Pork belly", "五花肉"), meat)
quick = Tag(BiText("quick", "快手"))
catalog = Catalog((produce, meat), (tomato, pork), (quick,))
assert catalog.categories == (produce, meat)
assert catalog.find_ingredient("五花肉") is pork
assert catalog == Catalog((produce, meat), (tomato, pork), (quick,))
greens = Category("greens", BiText("Vegetables and fruit", "青菜"))
assert Catalog((produce, greens), (), ()).categories == (produce, greens)

fruit = Category("Produce", BiText("Fruit", "水果"))
tomato_again = Ingredient(BiText("tomato", "西红柿"), produce)
Catalog((produce,), (tomato, pork), ())  # raises ValueError
Catalog((produce, fruit), (), ())  # raises ValueError
Catalog((produce, meat), (tomato, tomato_again), ())  # raises ValueError
```

### 2.6 `Catalog.find_ingredient` 和 `Catalog.find_tag`

- 模块：catalog，`Catalog`（2.5）的方法
- 功能：按任一语言的名称查找食材或标签。F04 用它们查找菜谱的食材和标签，F09 查找 `list --tag` 的标签，`read_pantry` 查找常备清单的每一项。

签名：

```python
def find_ingredient(self, name: str) -> Ingredient | None: ...


def find_tag(self, name: str) -> Tag | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `name` | `str` | 写下的名称，比如 `葱`、`Scallion` 或 ` scallion `。 | 任何字符串。 |

- 返回值：有一个名称（任一语言）按下面的规则与 `name` 匹配的食材或标签；没有名称匹配时为 `None`。目录里没有两个相互匹配的名称（2.5），所以最多只有一项匹配。食材和标签分开查找：`find_ingredient` 从不给出标签，`find_tag` 从不给出食材。

两段文字的匹配形式相等时，它们相互匹配。一段文字的匹配形式是：按 `str.strip()` 的方式去掉两端的空白字符，再把其中每个 A 到 Z 的 ASCII 大写字母换成对应的小写字母。`Catalog`、`read_catalog` 和 `read_pantry` 都用这种方式比较每个名称、每个分类键，以及常备清单给出的每个名称。由此得出这些规则：

1. 两端的空白字符不算。`str.strip()` 去掉每个 `str.isspace()` 为真的字符，比如空格、制表符、U+00A0 NO-BREAK SPACE 和 U+3000 IDEOGRAPHIC SPACE。它保留 U+200B ZERO WIDTH SPACE 和 U+FEFF ZERO WIDTH NO-BREAK SPACE，因为它们不是空白字符。所以 `葱\u200B` 不匹配 `葱`。
2. 文字中间的空白字符按原样计算。中间有两个空格的 `Choy  sum` 不匹配 `Choy sum`。
3. 只有 A 到 Z 的字母不分大小写，两种语言的文字都是这样。`SCALLION` 匹配 `Scallion`，`jalapeño` 匹配 `Jalapeño`。`JALAPEÑO` 不匹配它，因为 `Ñ` 不是 A 到 Z 之间的字母。
4. 形似的字母保持原样。带 U+212A KELVIN SIGN 的 `\u212Aale` 不匹配 `Kale`，尽管 `str.lower()` 会把 U+212A 变成 `k`。带 U+017F LATIN SMALL LETTER LONG S 的 `\u017Fcallion` 不匹配 `Scallion`，尽管 `str.casefold()` 会把 U+017F 变成 `s`。全角字母，比如 U+FF33 FULLWIDTH LATIN CAPITAL LETTER S，不匹配对应的 ASCII 字母。所以代码既不用 `str.lower()`，也不用 `str.casefold()`。
5. 文字不做规范化。`e` 后面跟 U+0301 COMBINING ACUTE ACCENT，不匹配单个字符 U+00E9 `é`。
6. 汉字按原样比较。`番茄` 和 `西红柿` 是两个名称。
7. 匹配形式为空的文字，比如 `""` 或 `"\u3000"`，不匹配任何名称。

F01 的 `parse_unit` 让英文写法不分大小写（F01 设计 2.3 和 2.6）。它的代码只在整段文字都是 ASCII 时才改变大小写（`src/recipe_menu/units/_ops.py` 里的 `_fold`）。在单位的写法上，两条规则的结果一致，因为单位的每个英文写法都是 ASCII，也没有哪个写法把 ASCII 字母和别的字符混在一起。F03 还会改变含有其他字符的名称里的 A 到 Z，所以 `jalapeño` 匹配 `Jalapeño`。

错误：无。两个方法都不抛异常。

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.lang import BiText

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
kale = Ingredient(BiText("Kale", "羽衣甘蓝"), produce)
scallion = Ingredient(BiText("Scallion", "葱"), produce)
quick = Tag(BiText("quick", "快手"))
catalog = Catalog((produce,), (kale, scallion), (quick,))
assert catalog.find_ingredient("葱") is scallion
assert catalog.find_ingredient(" SCALLION\t") is scallion
assert catalog.find_ingredient("\u3000葱") is scallion  # U+3000 IDEOGRAPHIC SPACE
assert catalog.find_ingredient("kale") is kale
assert catalog.find_ingredient("\u212aale") is None  # U+212A KELVIN SIGN
assert catalog.find_ingredient("\u017fcallion") is None  # U+017F LATIN SMALL LETTER LONG S
assert catalog.find_ingredient("葱\u200b") is None  # U+200B ZERO WIDTH SPACE
assert catalog.find_ingredient("Scal lion") is None
assert catalog.find_ingredient("") is None
assert catalog.find_tag("QUICK") is quick
assert catalog.find_tag("葱") is None
```

### 2.7 `Pantry`

- 模块：catalog
- 功能：家里常备的食材（[架构 5.2](../../architecture.zh-CN.md#52-值)）。购物清单去掉这些食材，并在末尾用一行列出菜单用到的那些（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，购物清单第 6 条规则）。

签名：

```python
@dataclass(frozen=True, slots=True)
class Pantry:
    ingredients: frozenset[Ingredient]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `ingredients` | `Ingredient` 值组成的 frozenset | 常备清单里的食材。 | 来自 `read_pantry` 拿到的目录。 |

- 返回值：一个 `Pantry`。两个集合相等时，两个常备清单相等。`Pantry` 可以求哈希。集合没有顺序，所以由 F12 给常备食材那一行定顺序，比如目录里的顺序。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.catalog import Category, Ingredient, Pantry
from recipe_menu.lang import BiText

seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
salt = Ingredient(BiText("Salt", "盐"), seasonings)
sugar = Ingredient(BiText("Sugar", "糖"), seasonings)
pantry = Pantry(frozenset({salt}))
assert salt in pantry.ingredients
assert sugar not in pantry.ingredients
assert pantry == Pantry(frozenset({salt}))
```

### 2.8 `read_catalog`

- 模块：catalog
- 功能：把 `catalog.toml` 读成一个 `Catalog`，并报告每个问题及其位置（[需求 4](../../requirements.zh-CN.md#4-功能点)，F03）。`check` 显示所有问题（F07）。其他命令遇到第一个错误就停下（架构 6）。

签名：

```python
def read_catalog(folder: DataFolder) -> tuple[Catalog | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：一对值 `(catalog, problems)`。
  - `read_toml` 给出问题时，`catalog` 为 `None`：文件不存在、读不了、不是 UTF-8，或者不是有效的 TOML。这时 `problems` 只含这一个问题。
  - 否则 `catalog` 是一个 `Catalog`，按文件顺序包含没有被下面任何检查跳过的每个分类、食材和标签，即使 `problems` 不为空也是如此。每个名称和每个键保存时都去掉了两端的空白字符。每种食材的 `category` 与 `catalog.categories` 里的 `Category` 是同一个对象。
  - `problems` 是 `Problem` 值组成的元组，每个的严重程度都是 `Severity.ERROR`，文件都是 `catalog.toml`。F03 不给出警告。

文件的格式就是 `docs/prototypes/example-data.md` 里的格式：

```toml
categories = [
  { key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" },
]

ingredients = [
  { zh = "葱", en = "Scallion", category = "produce", unit = "根" },
]

tags = [
  { zh = "快手", en = "quick" },
]
```

目录问题的位置如下。N 从 1 开始数列表里的项，被跳过的项也算在内，所以它就是你在文件里数出来的序号。TOML 的 `[[ingredients]]` 写法里的每个表也是列表的一项。

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| 列表 `categories`、`ingredients` 或 `tags` | `categories`、`ingredients` 或 `tags` | `分类`、`食材` 或 `标签` |
| `categories` 的第 N 项 | `category N` | `分类 N` |
| `ingredients` 的第 N 项 | `ingredient N` | `食材 N` |
| `tags` 的第 N 项 | `tag N` | `标签 N` |

`read_catalog` 依次读取 `categories`、`ingredients` 和 `tags`，然后读取文件顶层的其他键。它按顺序读取每个列表的项。对于每一项，它检查每个字段和每个未知的键，并报告每个问题。这些检查都没有跳过这一项时，它再检查这一项是否重复。没有检查跳过这一项时，它保留这一项。问题也按同样的顺序给出：先是列表本身的问题，然后是每一项的问题。一项的问题先按下面它的键的顺序逐个字段给出，然后按文件顺序给出它的未知键，最后给出它的重复：分类先是键，然后是中文名和英文名。

每类项有这些键，顺序如下：

| 类别 | 键 | 必填文字 |
| --- | --- | --- |
| 分类 | `key`、`zh` 和 `en` | 三个都是 |
| 食材 | `zh`、`en`、`category` 和 `unit` | `zh`、`en` 和 `category` |
| 标签 | `zh` 和 `en` | 两个都是 |
| 文件顶层 | `categories`、`ingredients` 和 `tags` | 无。它们是列表。 |

必填文字在这些情况下有问题：

| 情况 | 问题 |
| --- | --- |
| 缺少这个键。 | `MISSING_KEY` |
| 值不是文字，比如 `3`、`true` 或一个列表。 | `NOT_A_TEXT` |
| 文字为空或只有空白字符：`str.strip()` 给出 `""`。 | `EMPTY_TEXT` |

`read_catalog` 做这些检查。最后一列说明每项检查对这一项怎么做。一项检查保留的项，如果另一项检查跳过它，仍然会被跳过。

| 部分 | 检查 | 问题和位置 | `read_catalog` 怎么做 |
| --- | --- | --- | --- |
| `categories`、`ingredients` 或 `tags` | 缺少这个键。 | `MISSING_KEY`，没有位置 | 把这个列表当作空列表。 |
| `categories`、`ingredients` 或 `tags` | 值不是列表。 | `NOT_A_LIST`，位置是这个列表 | 把这个列表当作空列表。 |
| 任何一项 | 这一项不是表。 | `NOT_A_TABLE`，位置是这一项 | 跳过这一项。 |
| 任何一项 | 这一项有它这一类没有的键。 | `UNKNOWN_KEY`，位置是这一项 | 忽略这个键。 |
| 分类 | `key`、`zh` 或 `en` 作为必填文字有问题。 | 这个问题，位置是这个分类 | `key` 有问题，或者 `zh` 和 `en` 都有问题时，跳过这个分类。否则保留这个分类和它可用的名称。 |
| 分类 | 它的键与之前保留的某个分类的键匹配。 | `DUPLICATE_KEY`，位置是这个分类 | 跳过这个分类。 |
| 分类 | 它的中文名、然后是英文名，与之前保留的某个分类的任一语言名称匹配。 | `DUPLICATE_ZH_NAME` 或 `DUPLICATE_EN_NAME`，位置是这个分类 | 保留这个分类，让它的食材还能找到它。 |
| 食材 | `zh`、`en` 或 `category` 作为必填文字有问题。 | 这个问题，位置是这种食材 | 跳过这种食材。 |
| 食材 | `category` 不匹配任何已保留分类的键。 | `UNKNOWN_CATEGORY`；没有保留任何分类时为 `NO_CATEGORIES`。位置是这种食材 | 跳过这种食材。 |
| 食材 | 有 `unit`，但它不是文字。 | `NOT_A_TEXT`，位置是这种食材 | 保留这种食材，不设默认单位。 |
| 食材 | `unit` 是 `parse_unit` 不认识的文字（F01 设计 2.6），比如 `cups` 或 `适量`。 | `UNKNOWN_UNIT`，位置是这种食材 | 保留这种食材，不设默认单位。 |
| 食材 | 缺少 `unit`，或者它为空或只有空白字符。 | 无 | 这种食材没有默认单位。 |
| 食材 | 它的中文名、然后是英文名，与之前保留的某种食材的任一语言名称匹配。 | `DUPLICATE_ZH_NAME` 或 `DUPLICATE_EN_NAME`，位置是这种食材 | 跳过这种食材。 |
| 标签 | `zh` 或 `en` 作为必填文字有问题。 | 这个问题，位置是这个标签 | 跳过这个标签。 |
| 标签 | 它的中文名、然后是英文名，与之前保留的某个标签的任一语言名称匹配。 | `DUPLICATE_ZH_NAME` 或 `DUPLICATE_EN_NAME`，位置是这个标签 | 跳过这个标签。 |
| 文件顶层 | `categories`、`ingredients` 和 `tags` 以外的键。 | `UNKNOWN_KEY`，没有位置 | 忽略这个键。 |

重复的键和名称遵守这些规则：

- 只要没有其他检查跳过一项，`read_catalog` 就检查它是否重复。保留这一项、只记下问题的检查不会跳过它：未知的键，不是文字或 `parse_unit` 不认识的 `unit`，以及另一个名称仍可用的分类写错的 `zh` 或 `en`。所以一种食材写了 `unit = "cups"`，中文名又与更早的一种食材的某个名称匹配时，它得到 `UNKNOWN_UNIT`，然后是 `DUPLICATE_ZH_NAME`，并被跳过。一个分类写了 `en = ""`，中文名是新的，键又与更早的一个分类相同时，它得到 `EMPTY_TEXT`，然后是 `DUPLICATE_KEY`，并被跳过。
- 它只把这一项与已保留的同类项比较，所以被跳过的项不占用键和名称。分类只比较可用的名称。
- 一项的每个名称，以及分类的键，都可以各自给出一个问题。每个问题都指出拥有这个键或名称的第一个更早的项。
- 同一项的两个名称可以相互匹配。
- 匹配遵守 2.6 的规则，所以 `rice` 与 `Rice` 重复。
- 两个分类不能同名，因为购物清单把每个分类的名称显示为标题。一个分类的名称与更早的某个分类的名称匹配时，它得到 `DUPLICATE_ZH_NAME` 或 `DUPLICATE_EN_NAME`，但 `read_catalog` 保留它。食材通过键指明分类，所以这个分类的食材仍能找到它，`check` 也不会再把这些食材逐个报告为 `UNKNOWN_CATEGORY`。所以 `Catalog` 不比较分类的名称（2.5）。

`read_catalog` 用 `datafile` 的提示（2.10）报告文件结构的问题：`MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TABLE`、`NOT_A_TEXT`、`EMPTY_TEXT` 和 `UNKNOWN_KEY`。它按这一类的键的个数选择 `UNKNOWN_KEY` 的形式。下面是 `catalog` 的提示。占位符是花括号里的名称，比如 `{category}`。`UNKNOWN_CATEGORY` 是 `Plural` 值（F02 设计 2.4），按 `read_catalog` 保留的分类的个数选择。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `CATEGORIES`、`INGREDIENTS`、`TAGS`、`CATEGORY_N`、`INGREDIENT_N` 和 `TAG_N` | 位置表里的位置，N 写作 `{number}`。 | 位置表里的位置，N 写作 `{number}`。 |
| `UNKNOWN_CATEGORY`，只有一个分类时 | `Unknown category "{category}". The only category is {categories}.` | `未知分类“{category}”。现有分类：{categories}。` |
| `UNKNOWN_CATEGORY`，有多个分类时 | `Unknown category "{category}". The categories are {categories}.` | `未知分类“{category}”。现有分类：{categories}。` |
| `NO_CATEGORIES` | `Unknown category "{category}". The catalog has no categories.` | `未知分类“{category}”。目录里没有分类。` |
| `UNKNOWN_UNIT` | `Unknown unit "{unit}".` | `未知单位“{unit}”。` |
| `DUPLICATE_KEY` | `The key "{key}" is also {other}'s key. Keys must be unique.` | `键“{key}”也是{other} 的键。键不能重复。` |
| `DUPLICATE_ZH_NAME` | `The Chinese name "{name}" is also {other}'s name. Names must be unique.` | `中文名称“{name}”也是{other} 的名称。名称不能重复。` |
| `DUPLICATE_EN_NAME` | `The English name "{name}" is also {other}'s name. Names must be unique.` | `英文名称“{name}”也是{other} 的名称。名称不能重复。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `key` | 文件里写的键，比如 `en`、`categories` 或一个未知的键。在 `DUPLICATE_KEY` 里，是去掉两端空白字符的分类键。 |
| `keys` | 这一类的键按键表顺序经 `and_list` 列出，比如“zh, en, category, and unit”和“zh、en、category 和 unit”。 |
| `category` | 食材的 `category`，去掉两端的空白字符。 |
| `categories` | `read_catalog` 保留的分类的键按顺序经 `and_list` 列出。示例目录给出“produce, meat, eggs, staples, seasonings, and other”，和 F07 原型一样。 |
| `unit` | 食材的 `unit`，去掉两端的空白字符。 |
| `name` | 后面那一项的名称，去掉两端的空白字符。 |
| `other` | 拥有这个键或名称的第一个更早的项的位置，比如“ingredient 3”和“食材 3”。 |
| `number` | N，项的序号。 |

F07 原型展示了其中两个问题。`catalog.toml, ingredient 12` 对应 `The English name "Rice" is also ingredient 4's name. Names must be unique.`，`catalog.toml, ingredient 7` 对应 `Unknown category "meats". The categories are produce, meat, eggs, staples, seasonings, and other.`。

错误：无。`read_catalog` 遇到坏数据从不抛异常。

- 副作用：通过 `read_toml` 读取 `catalog.toml`。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。第二个目录在一个较短的文件里带有场景 v0.1-S07 的错误，外加两个未知的单位。食材 5 还重复了食材 4 的中文名，所以它得到两个问题，并被跳过。

```python
from recipe_menu.catalog import read_catalog
from recipe_menu.lang import BiText, Lang
from recipe_menu.units import Unit

catalog, problems = read_catalog(folder)
assert problems == ()
assert catalog is not None
assert [category.key for category in catalog.categories[:3]] == ["produce", "meat", "eggs"]
assert (len(catalog.categories), len(catalog.ingredients), len(catalog.tags)) == (6, 22, 5)
scallion = catalog.ingredients[3]
assert scallion.name == BiText("Scallion", "葱")
assert scallion.category is catalog.categories[0]
assert scallion.unit is Unit.STALK

lines = [
    'categories = [{ key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" }]',
    "ingredients = [",
    '  { zh = "西兰花", en = "Broccoli", category = "produce" },',
    '  { zh = "芥兰", en = "broccoli", category = "produce" },',
    '  { zh = "香菜", en = "Coriander", category = "meats" },',
    '  { zh = "葱", en = "Scallion", category = "produce", unit = "cups" },',
    '  { zh = "葱", en = "Green onion", category = "produce", unit = "cups" },',
    "]",
    "tags = []",
]
folder.catalog.write_text("\n".join(lines) + "\n", encoding="utf-8")
catalog, problems = read_catalog(folder)
assert catalog is not None
assert [ingredient.name.en for ingredient in catalog.ingredients] == ["Broccoli", "Scallion"]
assert catalog.ingredients[1].unit is None
assert [problem.place for problem in problems] == [
    BiText("ingredient 2", "食材 2"),
    BiText("ingredient 3", "食材 3"),
    BiText("ingredient 4", "食材 4"),
    BiText("ingredient 5", "食材 5"),
    BiText("ingredient 5", "食材 5"),
]
assert problems[0].text(Lang.ZH) == "英文名称“broccoli”也是食材 1 的名称。名称不能重复。"
assert problems[1].text(Lang.EN) == 'Unknown category "meats". The only category is produce.'
assert problems[2].text(Lang.EN) == 'Unknown unit "cups".'
assert problems[3].text(Lang.EN) == 'Unknown unit "cups".'
assert problems[4].text(Lang.ZH) == "中文名称“葱”也是食材 4 的名称。名称不能重复。"

folder.catalog.unlink()
catalog, problems = read_catalog(folder)
assert catalog is None
assert problems[0].text(Lang.EN) == "The file is missing."
```

### 2.9 `read_pantry`

- 模块：catalog
- 功能：把 `pantry.toml` 读成一个 `Pantry`，并报告每个问题及其位置（[需求 4](../../requirements.zh-CN.md#4-功能点)，F03）。目录读不了时，它接受 `None` 作为目录，这样 `check` 仍能报告常备清单自己的错误。

签名：

```python
def read_pantry(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[Pantry | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `catalog` | `Catalog` 或 `None` | 常备清单里的名称所来自的目录。 | 目录读不了时为 `None`。这时 `read_pantry` 只检查文件的格式。 |

- 返回值：一对值 `(pantry, problems)`。
  - `read_toml` 给出问题，或者 `catalog` 为 `None` 时，`pantry` 为 `None`。否则它是一个 `Pantry`，含有每个指明了食材的项所指的食材，即使 `problems` 不为空也是如此。两项指明同一种食材时，比如 `盐` 和 `Salt`，这种食材在集合里只出现一次，也不产生问题。
  - `problems` 要么只含 `read_toml` 的问题，要么是下面各项检查的问题。每个问题的严重程度都是 `Severity.ERROR`，文件都是 `pantry.toml`。

文件的格式就是示例里的格式：`pantry = ["食用油", "盐", "糖", "生抽", "花椒"]`。每一项用任一语言指明目录里的一种食材，`read_pantry` 用 `Catalog.find_ingredient`（2.6）找到它。

常备清单问题的位置如下。N 从 1 开始数各项，被跳过的项也算在内。

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| 列表 `pantry` | `pantry` | `常备清单` |
| `pantry` 的第 N 项 | `item N` | `第 N 项` |

`read_pantry` 按这个顺序做这些检查：先检查列表，再按顺序检查每一项，然后检查文件顶层的其他键。

| 部分 | 检查 | 问题和位置 | `read_pantry` 怎么做 |
| --- | --- | --- | --- |
| `pantry` | 缺少这个键。 | `MISSING_KEY`，没有位置 | 把这个列表当作空列表。 |
| `pantry` | 值不是列表。 | `NOT_A_LIST`，位置是 `pantry` | 把这个列表当作空列表。 |
| 一项 | 这一项不是文字。 | `ITEM_NOT_A_TEXT`，位置是这一项 | 跳过这一项。 |
| 一项 | 这一项为空或只有空白字符。 | `EMPTY_ITEM`，位置是这一项 | 跳过这一项。 |
| 一项 | `catalog` 不是 `None`，而且 `find_ingredient` 找不到这一项的食材。 | `UNKNOWN_INGREDIENT`，位置是这一项 | 跳过这一项。 |
| 文件顶层 | `pantry` 以外的键。 | `UNKNOWN_KEY`，没有位置，使用只有一个键时的形式 | 忽略这个键。 |

`read_pantry` 使用 `datafile`（2.10）的 `MISSING_KEY`、`NOT_A_LIST`、`ITEM_NOT_A_TEXT`、`EMPTY_ITEM` 和 `UNKNOWN_KEY`。`MISSING_KEY` 和 `NOT_A_LIST` 的值 `key` 是 `pantry`。`UNKNOWN_KEY` 的 `key` 是文件里写的未知键，`keys` 是 `and_list(["pantry"])`，也就是“pantry”。它还使用 `catalog` 的这些提示：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `PANTRY` 和 `ITEM_N` | 位置表里的位置，N 写作 `{number}`。 | 位置表里的位置，N 写作 `{number}`。 |
| `UNKNOWN_INGREDIENT` | `Unknown ingredient "{name}".` | `未知食材“{name}”。` |

值 `name` 是去掉两端空白字符的这一项。F07 原型展示了 `pantry.toml, item 3` 和 `Unknown ingredient "sesame oil".`。

错误：无。`read_pantry` 遇到坏数据从不抛异常。

- 副作用：通过 `read_toml` 读取 `pantry.toml`。它不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。

```python
from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.lang import BiText, Lang

catalog, _ = read_catalog(folder)
assert catalog is not None
pantry, problems = read_pantry(folder, catalog)
assert problems == ()
assert pantry is not None
assert len(pantry.ingredients) == 5
assert catalog.find_ingredient("Salt") in pantry.ingredients

text = 'pantry = ["食用油", "Salt", "sesame oil", 3, " "]\n'
folder.pantry.write_text(text, encoding="utf-8")
pantry, problems = read_pantry(folder, catalog)
assert pantry is not None
assert len(pantry.ingredients) == 2
assert [problem.place for problem in problems] == [
    BiText("item 3", "第 3 项"),
    BiText("item 4", "第 4 项"),
    BiText("item 5", "第 5 项"),
]
assert problems[0].text(Lang.EN) == 'Unknown ingredient "sesame oil".'
assert problems[1].text(Lang.ZH) == "这一项必须是放在引号里的文字。"
assert problems[2].text(Lang.EN) == "This item is empty."

pantry, problems = read_pantry(folder, None)
assert pantry is None
assert len(problems) == 2
```

### 2.10 `MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TABLE`、`NOT_A_TEXT`、`EMPTY_TEXT`、`ITEM_NOT_A_TEXT`、`EMPTY_ITEM` 和 `UNKNOWN_KEY`

- 模块：datafile
- 功能：数据文件结构不对时的提示：缺少键；值不是列表、表或文字；文字或列表项为空；表里有它不能有的键。每个数据文件都可能有这些错误，所以由 `datafile` 保存这些提示，F03 到 F06 的读取函数对同一种错误给出同一种说法。`settings` 和 `menus` 不能引用 `catalog`（架构 3），所以放在 `catalog` 里的提示就得被复制。这些提示放在 `datafile/messages.py` 里，由 `recipe_menu.datafile` 导出。

签名：

```python
MISSING_KEY: Final[Message]
NOT_A_LIST: Final[Message]
NOT_A_TABLE: Final[Message]
NOT_A_TEXT: Final[Message]
EMPTY_TEXT: Final[Message]
ITEM_NOT_A_TEXT: Final[Message]
EMPTY_ITEM: Final[Message]
UNKNOWN_KEY: Final[Plural]
```

这些提示如下。占位符是花括号里的名称，比如 `{key}`。`{ ... }` 和 `[ ... ]` 里的括号是文字的一部分，所以 `NOT_A_TABLE` 的模板把每个花括号写两次（F02 设计 2.2）。`UNKNOWN_KEY` 是 `Plural` 值（F02 设计 2.4）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `MISSING_KEY` | `The key "{key}" is missing.` | `缺少键“{key}”。` |
| `NOT_A_LIST` | `"{key}" must be a list in square brackets, [ ... ].` | `“{key}”必须是放在方括号 [ ... ] 里的列表。` |
| `NOT_A_TABLE` | `This item must be a table in braces, { ... }.` | `这一项必须是放在花括号 { ... } 里的表。` |
| `NOT_A_TEXT` | `"{key}" must be a text in quotation marks.` | `“{key}”必须是放在引号里的文字。` |
| `EMPTY_TEXT` | `"{key}" is empty.` | `“{key}”是空的。` |
| `ITEM_NOT_A_TEXT` | `This item must be a text in quotation marks.` | `这一项必须是放在引号里的文字。` |
| `EMPTY_ITEM` | `This item is empty.` | `这一项是空的。` |
| `UNKNOWN_KEY`，只有一个键时 | `Unknown key "{key}". The only key is {keys}.` | `未知键“{key}”。可用的键：{keys}。` |
| `UNKNOWN_KEY`，有多个键时 | `Unknown key "{key}". The keys are {keys}.` | `未知键“{key}”。可用的键：{keys}。` |

下表说明读取函数在什么时候使用每个提示。

| 常量 | 错误 |
| --- | --- |
| `MISSING_KEY` | 缺少文件或表需要的键。 |
| `NOT_A_LIST` | 键的值不是列表。 |
| `NOT_A_TABLE` | 由表组成的列表里，某一项不是表。 |
| `NOT_A_TEXT` | 键的值不是文字，比如 `3`、`true` 或一个列表。 |
| `EMPTY_TEXT` | 键的值是文字，但为空或只有空白字符。 |
| `ITEM_NOT_A_TEXT` | 由文字组成的列表里，某一项不是文字。 |
| `EMPTY_ITEM` | 由文字组成的列表里，某一项为空或只有空白字符。 |
| `UNKNOWN_KEY` | 表或文件顶层有它不能有的键。读取函数按这个表能有的键的个数选择形式。 |

参数：

占位符的值，由调用方传给 `Problem.error`（2.2）。

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `key` | `str` | 出错的键，比如 `en` 或 `categories`。对于 `UNKNOWN_KEY`，是文件里写的未知键。 | 只用于 `MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TEXT`、`EMPTY_TEXT` 和 `UNKNOWN_KEY`。 |
| `keys` | `BiText` | 这个表能有的键按读取函数的设计给出的顺序经 `and_list` 列出，比如“zh, en, category, and unit”和“zh、en、category 和 unit”。 | 只用于 `UNKNOWN_KEY`。 |

- 返回值：无。每个常量都是一个 `Message`，`UNKNOWN_KEY` 是由两个提示组成的 `Plural`。`NOT_A_TABLE`、`ITEM_NOT_A_TEXT` 和 `EMPTY_ITEM` 没有占位符，因为问题的位置已经指明了这一项。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import EMPTY_TEXT, MISSING_KEY, UNKNOWN_KEY, Problem
from recipe_menu.lang import Lang
from recipe_menu.text import and_list

missing = Problem.error(Path("catalog.toml"), None, MISSING_KEY, key="tags")
assert missing.text(Lang.EN) == 'The key "tags" is missing.'
assert EMPTY_TEXT.render(Lang.ZH, key="en") == "“en”是空的。"

only = UNKNOWN_KEY.pick(1).render(Lang.EN, key="items", keys=and_list(["pantry"]))
assert only == 'Unknown key "items". The only key is pantry.'
keys = and_list(["zh", "en", "category", "unit"])
chinese = UNKNOWN_KEY.pick(4).render(Lang.ZH, key="units", keys=keys)
assert chinese == "未知键“units”。可用的键：zh、en、category 和 unit。"
```

## 3. 对已有接口的修改

无。F03 加入模块 `datafile` 和 `catalog`。它按 F01 和 F02 的设计使用 F01 的 `Unit` 和 `parse_unit`，以及 F02 的 `BiText`、`Lang`、`Message`、`MessageValue`、`Plural` 和 `and_list`，不修改其中任何一个。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `datafile` 是基础层模块，只引用 `lang` 和 `text`；`catalog` 是领域层模块，只引用 `lang`、`units`、`text` 和 `datafile`，与架构 3 和 4 允许的一致。每个值都有架构 5.2 列出的字段。`DataFolder` 是唯一知道各文件名称的地方。`Problem` 带有严重程度、相对于数据文件夹的文件、两种语言的位置，以及提示和提示的值。`Ingredient` 和 `Tag` 需要两个名称，`Category` 需要一个。选择 7 符合架构 5.2 和 8。排好序的值对让 `Problem` 保持为集合都是元组的冻结值，相等比较不受关键字参数顺序的影响；创建时用两种语言写出提示，能让错误的值在构造它的读取函数里立即失败。`read_toml` 给出的表只交给读取这个文件的读取函数。这正是架构 5 里“原始的 TOML 表从不离开读取该文件的模块”的意思，因为架构 3 把读取 TOML 文件交给 `datafile`，把读取目录交给 `catalog`。`menu_file` 和 `shopping_file` 以文字接收周，因为 `datafile` 不能引用 `menus`。`Catalog` 建立的索引是内部的，所以开发工程师让它不参与比较、哈希和打印，`Catalog` 仍是由三个元组组成的值。选择 5 符合架构 6 和 F07 原型。`read_catalog` 返回没有被任何检查跳过的每一项，所以运行一次 `check` 就能列出所有问题；`read_pantry` 收到 `None` 时，仍会报告常备清单自己的错误。第 1 轮的发现 7 已解决。2.8 规定两个分类不能同名，把同名报告为错误，并保留这个分类。这与发现 1 和架构 6 一致。读取函数不抛异常，这个错误让命令以 1 退出。`check` 以外的命令遇到第一个错误就停止，所以没有购物清单会显示两个同名的标题。被保留的分类的食材仍能通过键找到它，所以 `check` 不会给这些食材报告错误的 `UNKNOWN_CATEGORY`。架构 5.2 对分类的名称没有规定，所以不比较分类名称的 `Catalog` 符合数据模型，2.5 的示例就是这样。2.10 把关于文件结构的提示放在 `datafile` 里。这符合把带位置的问题交给 `datafile` 的架构 3，也符合把模块的提示放在它的 `messages.py` 里的架构 8。`recipes`、`settings` 和 `menus` 都能引用 `datafile`，而 `settings` 和 `menus` 不能引用 `catalog`。有一处措辞不阻塞，合并前不需要修改。2.5 的约束一列说“两个分类可以同名”，说的是 `Catalog` 值；2.8 说“两个分类不能同名”，说的是文件。以后修改 2.5 时，可以写成“一个 `Catalog` 可以包含两个同名的分类”。第 2 节关于 F13 的说明不影响按现在设计的 F03 接口，它作为第 1 轮的发现 9 留给 Troy。F13 原型的英文常备食材一行“cooking oil, salt, sugar, soy sauce, Sichuan pepper”把目录里的四个名称写成小写字母，却保留“Sichuan pepper”；v0.1-S16 期望的是“cooking oil, salt, sugar”。名称按原样保存，没有规则能得出这一行。要么 F13 按目录的写法显示名称，这要通过需求变更流程修改原型、v0.1-S16 和 v0.1-S17；要么目录增加一个键，存放名称在句子中间的写法，这要通过变更流程修改 `Ingredient` 和 `read_catalog`。架构师推荐第一种，把这一点记给 F12 和 F13 的设计，并建议 Troy 在批准这份设计时（R18）、F03 实现之前做出决定。 |
| 遵守错误处理和命名约定 | Pass | 第 1 轮的发现 1 已解决。2.8 现在规定，目录包含没有被任何检查跳过的每一项；只要没有其他检查跳过一项，这一项就要做重复检查。它列出了保留一项、只记下问题的检查，并给出两种情况的结果。架构师按设计 0.2 更新的模型对第 1 轮的三个文件各给出两个问题，不抛异常：`UNKNOWN_UNIT` 然后是 `DUPLICATE_ZH_NAME`，`UNKNOWN_KEY` 然后是 `DUPLICATE_EN_NAME`，`EMPTY_TEXT` 然后是 `DUPLICATE_KEY`。三项都被跳过。在混合了 2.8 每项检查的 3,000 个随机目录上，`read_catalog` 在 Python 3.13.18 和 3.14.3 里都没有抛出异常。一个分类的键和中文名都与更早的一个分类相同时，它得到 `DUPLICATE_KEY`，然后是 `DUPLICATE_ZH_NAME`，并被跳过。三个分类的英文名相同时，第二个和第三个都指出分类 1，与 2.8 的“第一个更早的项”一致。测试计划可以使用这些情况。发现 4 到 6 已解决，架构师在这台电脑上重新核对了每一点。发现 4：点号分隔的部分有 1,001 个的键在 3.13.18 里抛出 `RecursionError`，在 3.14.3 里能解析；嵌套 600 层的列表或表在两个版本里都抛出这个异常。所以 2.3 用嵌套测试 `NESTED_TOO_DEEPLY` 是对的。发现 5：对字节 `EF BB BF 61 0A FF` 和 2.3 的新示例，在 `error.object[:error.start]` 里计数，两个版本都给出第 2 行。在文件本身的字节里数到 `error.start` 为止，给出第 1 行，所以这个示例能区分两种计数。发现 6：接在 `C:\Users\Troy\recipe-menu\recipes` 后面时，`PureWindowsPath` 把 `C:catalog.toml` 变成这个文件夹里的 `catalog.toml`。接在 `D:\data\recipes` 后面时，它给出 `C:catalog.toml`，也就是 C 盘当前文件夹里的一个文件。2.1 现在写出了这两种结果。第 1 轮的各项选择仍然通过。选择 1：超过 4,300 位的十进制整数和嵌套太深都是文件里的错误，不是 bug。架构 6 说读取函数遇到坏数据从不抛异常，出现回溯信息就一定是 bug，所以 `datafile` 捕获这两种异常。`except` 子句在生成 `Problem` 的地方写明它们（架构 6 和 8）。选择 2：第 1 轮的 36 种错误写法在两个版本里仍然给出 2.3 指定的提示，带行号的 `NOT_TOML` 就是架构 6 的一般提示。选择 3 遵守 F02 的审查意见：`catalog` 在构造 `BiText` 之前就认定空白的名称为缺失。选择 6：可能指向文件夹之外的名称属于错误的调用，所以这个 `ValueError` 符合架构 6；两个系统用同一条规则，符合架构 1。名称遵守 PEP 8，提示都是放在各模块 `messages.py` 里的 UPPER_SNAKE 常量（架构 8）。第 1 轮的发现 8 留给 Troy。`read_toml` 捕获 `ValueError` 和 `RecursionError`，按现在的设计可以接受。架构师建议 Troy 让架构 6 的“语法错误”一行和 ADR-0002 的决定写明这两种异常。这只改措辞，由 Troy 批准。 |
| 不和已有接口重复 | Pass | `datafile` 和 `catalog` 是新模块，F01 和 F02 没有接口读取文件、保存路径或查找名称。`catalog` 用 F01 的 `parse_unit` 读取单位，用 F02 的 `and_list` 写列举、用 `Plural` 写复数，用 `Message.to_bitext` 构造位置，所以这些都不重写。`Problem.text` 调用 `Message.render`。第 1 轮的发现 2 已解决。`datafile` 导出 2.10 的八个提示，所以 F04 到 F06 的读取函数使用它们，不复制它们。这八个提示都不与 F02 的提示重复，因为 `text` 只导出 `RUN_CHECK`、`RUN_HELP_FOR_OPTIONS` 和 `RUN_HELP_FOR_COMMANDS`。2.10 的签名把每个常量声明为 `Final[Message]` 或 `Final[Plural]`，与 `src/recipe_menu/text/messages.py` 声明 F02 提示的方式相同。发现 3 已解决。2.6 引用 F01 设计 2.3 和 2.6 来说明“英文写法不分大小写”，这两节都这样写。它引用 `src/recipe_menu/units/_ops.py` 里的 `_fold` 来说明 ASCII 规则，这个函数只在文字是 ASCII 时才改变大小写。选择 4：2.6 的匹配形式是 `parse_unit` 之外的第二条大小写规则，用于名称，不用于单位。两条规则在都能适用的地方结果一致。每个英文单位写法都是 ASCII，没有哪个中文写法含有 ASCII 字母，所以只改 A 到 Z，对每个写法都得到 `parse_unit` 的结果。形似的字母保持原样、不做规范化，让规则保持精确；2.6 写出了每种情况，所以测试计划能覆盖 F01 的测试计划没有覆盖的部分。关于 F10：匹配形式是 `catalog` 内部的。如果搜索需要同一条大小写规则，F10 的设计应该请求导出它，而不是再写一条。 |
| 只依赖排序在前面的功能 | Pass | F03 使用 F01 的 `Unit` 和 `parse_unit`，以及 F02 的 `BiText`、`Lang`、`Message`、`MessageValue`、`Plural` 和 `and_list`。这两个功能都排在 F03 之前，并且在 main 上通过了测试。2.10 的提示只需要 F02 的 `Message` 和 `Plural`。F03 不依赖任何后续功能。第 2 节列出的后续功能调用 F03，它们的设计各自接受审查。这些接口只需要标准库，比如 `tomllib`、`pathlib`、`dataclasses`、`enum` 和 `typing`，所以没有新依赖需要按 R16 审查。`docs/rules.md` 没有交给架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | 模块之间的每个假设都写在设计里。读取函数只从 `read_toml` 得到表，名称只能通过 `Catalog` 查找，所以菜谱和常备清单共用目录里的 `Ingredient` 对象（架构 5.2）。`read_toml` 依赖 `tomllib` 的英文原因文字。2.3 写出了这些文字和核对过的版本，其他任何文字都给出 `NOT_TOML`，所以以后的 Python 可能改变一条提示，但不会改变退出码。2.10 写出了占位符 `key` 和 `keys`，以及每个提示报告的错误，所以 F04 到 F06 按写明的约定使用这些提示。F03 不在提示里显示来自文件的数字。有两点留给后续设计。关于 F04、F06 和 F09：给 `recipe_file`、`menu_file` 或 `shopping_file` 传入错误的名称属于错误的调用，所以每个调用方先检查 ID 或周。F04 的 ID 规则至少要拒绝 2.1“错误”表里的名称，因为 Linux 允许 `recipes/a:b.toml` 这样的文件。F06 在拼出路径之前就报告未知的菜谱 ID，F09 的 `show ID` 把错误的 ID 变成它的“未知 ID”输出。关于 F04 到 F06：`tomllib` 能读取任意长度的十六进制、八进制或二进制整数，5,000 位的 `0x` 数字也能解析。`Problem` 在创建时就写出它的值，所以显示文件里数字的提示必须先限制这个数字的范围，或者显示文件里的文字。否则 `Problem` 会因为坏数据抛出 F02 设计 2.3 的 `ValueError`。 |
| 修改已实现的接口时走了变更流程 | Pass | F01 的 `lang` 和 `units`，以及 F02 的 `lang` 和 `text` 都已实现。F03 按它们的设计使用它们，不给它们增加任何东西。它创建架构 3 交给 F03 的 `datafile`，并构建 `catalog`。2.10 的提示放在新的 `datafile` 里，而不是 F02 的 `text` 里，所以没有已实现的模块被修改。第 3 节写“无”，是对的。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 一个阻塞问题，即发现 1：2.8 让检查保留下来、但带有问题的项跳过重复检查，接着 `Catalog` 因为坏数据抛出异常。架构师检查了每个文件里的 18 个 `python` 代码块。每个都能解析，并与另一种语言的版本相同。架构师按第 2 节建了模型，在 `docs/prototypes/example-data.md` 示例数据的副本上，用 Python 3.13.18 和 3.14.3 运行了 9 个示例。每个断言和每个 `# raises` 都成立，包括数量 6、22 和 5，以及 `catalog.ingredients[3]` 就是葱。ruff 0.17.4 的 `ruff format --check` 报告两个文件都已格式化。发现 2 到 7 不阻塞。 | 要求修改。接口设计师为发现 1 修改 2.8，并对发现 2 到 7 作出决定。 |
| 2 | 没有阻塞问题。第 1 轮的发现 1 到 7 已解决，发现 8 和 9 留给 Troy。架构师检查了每个文件里的 20 个 `python` 代码块。每个都能解析，并与另一种语言的版本相同。架构师把模型更新到设计 0.2，在 `docs/prototypes/example-data.md` 示例数据的副本上，用 Python 3.13.18 和 3.14.3 运行了 10 个示例。每个断言和每个 `# raises` 都成立，包括 2.3 的字节顺序标记、2.5 的同名分类和 2.8 的食材 5。ruff 0.17.4 的 `ruff format --check` 报告两个文件都已格式化。2.5 有一处措辞不阻塞。 | 批准。Troy 在批准这份设计时（R18）决定发现 8 和 9。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-10 | 初稿。 |
| 0.2 | 2026-11-10 | 回应架构师审查第 1 轮。`read_catalog` 保留没有被任何检查跳过的每一项；只要没有其他检查跳过一项，就检查它是否重复，所以检查保留下来、但带有问题的项也要做重复检查（2.8）。分类的名称与更早的某个分类的名称匹配时，得到 `DUPLICATE_ZH_NAME` 或 `DUPLICATE_EN_NAME`，但仍被保留；`Catalog` 不比较分类的名称（2.5 和 2.8）。关于文件结构的提示从 `catalog` 移到 `datafile`，由它导出，并加入 `ITEM_NOT_A_TEXT` 和 `EMPTY_ITEM`（2.10）。`NOT_UTF8` 在 `error.object[:error.start]` 里数行号，所以字节顺序标记不改变行号（2.3）。键的部分个数限制取决于 Python 的版本，所以只用嵌套测试 `NESTED_TOO_DEEPLY`（2.3）。改正了带盘符的名称这条规则的理由（2.1）。`parse_unit` 的 ASCII 规则改为引用 F01 的代码（2.6）。2.3、2.5 和 2.8 的示例覆盖了新的情况。 |
| 1.0 | 2026-11-10 | Troy 批准。 |
