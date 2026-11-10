---
troy-doc: "F02-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "design.md"
---

# F02 双语终端输出：接口设计

## 1. 功能

- 编号和名称：F02 双语终端输出
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：无

## 2. 接口

F02 给基础层模块 `lang` 加入一个值，并构建基础层模块 `text`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.lang` 在 F01 的 `Lang` 旁边导出 `BiText`。`recipe_menu.text` 导出 `Message`、`MessageValue`、`Plural`、`RUN_CHECK`、`RUN_HELP_FOR_COMMANDS`、`RUN_HELP_FOR_OPTIONS`、`and_list`、`choose_lang`、`comma_list`、`display_width`、`format_table` 和 `use_utf8`。每个模块的 `__init__.py` 在 `__all__` 里列出自己的名称。三条公用提示放在 `text/messages.py` 里（架构 8）。每个模块背后的其他文件由开发工程师决定。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F02 提供的接口 |
| --- | --- |
| 保存工具所有提示的英文和中文。 | 不可能只有一种语言的 `Message`（2.2 和 2.3），以及 `text` 公用的提示（2.5）。其他每条提示都是一个 `Message` 常量，放在显示它的模块的 `messages.py` 里（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)，ADR-0004）。 |
| 选择语言：先看 `--lang`，再看设置，最后用英文。 | `choose_lang`（2.7）。 |
| 对于有两种语言的文字，显示所选语言，缺失时改用另一种语言。 | `BiText`（2.1）。`Message.render`（2.3）和 2.6 的列举对它们的 `BiText` 值也这样改用另一种语言。 |
| 英文复数，以及“a, b, and c”和“a、b、c”这样的列举，由 `text` 提供（架构 8）。 | `Plural`（2.4）、`and_list` 和 `comma_list`（2.6）。 |
| 打印对齐的表格，其中一个汉字占两列。 | `display_width`（2.8）和 `format_table`（2.9）。 |
| 不论控制台代码页是什么，都能在 PowerShell 里正确显示中文。 | `use_utf8`（2.10）。 |

下面每个接口都遵守这些规则：

- `lang` 不引用包里的任何模块，`text` 只引用 `lang`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- 没有接口打印、读文件、读环境变量或保存状态。`format_table` 返回各行，由调用方写到 `Context` 里的流（架构 8）。`use_utf8` 只改变传给它的那个流。
- 下文的异常都来自错误的调用，也就是 bug（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。读取函数先检查文件里的值，再用它们构造 `BiText`，并把错误的值报告为 `Problem`。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F02 的接口都没有性能指标。PT01 计时的命令通过 `format_table` 打印，比如有 1,000 个菜谱时的 `list`。所以 `format_table` 和 `display_width` 的耗时与它们收到的字符数成正比。

以下后续功能打算调用这些接口：

- F03 在 `datafile` 里用一个 `Message` 和它的 `MessageValue` 值构造 `Problem`，位置是 `Message.to_bitext` 给出的 `BiText`。`catalog` 把每个名称存为 `BiText`，并用 `and_list` 在提示里列出分类。
- F04 把菜谱名和备注存为 `BiText` 值，并用 `BiText.exact` 找出缺少的语言。
- F05 用 `choose_lang` 选择语言，用 `use_utf8` 把 stdout 和 stderr 设为 UTF-8，用 `format_table` 排版帮助，并用 `RUN_HELP_FOR_OPTIONS` 或 `RUN_HELP_FOR_COMMANDS` 结束用法错误。
- F07 用 `Plural` 数错误和警告，用 `and_list` 列出它检查了什么。
- F09、F10、F11 和 F13 用 `format_table` 打印表格，用 `comma_list` 连接标签和其他短列举，用 `Plural` 计数。数据文件里的错误让它们停下时，它们加上 `RUN_CHECK`。

### 2.1 `BiText`

- 模块：lang
- 功能：有两种语言、至少有其中一种的文字，比如菜谱名或食材的备注。它给出要求的语言；缺这种语言时给出另一种（[架构 5.2](../../architecture.zh-CN.md#52-值)）。`Message.to_bitext`（2.3）和 2.6 的列举也给出 `BiText`，所以写好的文字可以作为另一条提示的值，或者作为 `Problem` 的位置。

签名：

```python
@dataclass(frozen=True, slots=True)
class BiText:
    en: str | None = None
    zh: str | None = None

    def get(self, lang: Lang) -> str: ...

    def exact(self, lang: Lang) -> str | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `en` | `str` 或 `None` | 英文文字。 | 没有英文时为 `None`。 |
| `zh` | `str` 或 `None` | 中文文字。 | 没有中文时为 `None`。`en` 和 `zh` 不能都是 `None`。 |
| `lang` | `Lang` | `get` 或 `exact` 给出的语言。 | 无 |

- 返回值：一个 `BiText`。
  - `get(lang)` 给出 `lang` 的文字；`lang` 的文字为 `None` 时，给出另一种语言的文字。它从不给出 `None`。
  - `exact(lang)` 给出 `lang` 的文字；这种文字缺失时给出 `None`。读取函数用它对缺少的语言发出警告。
  - 空字符串也算一种文字，所以 `get` 直接给出它，不改用另一种语言。读取函数如果把文件里的空名称当作缺失，就为它传入 `None`。
  - 两个 `BiText` 的 `en` 相等、`zh` 也相等时，它们相等。`BiText` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `en` 和 `zh` 都是 `None`。 |
| `TypeError` | `en` 或 `zh` 既不是 `str` 也不是 `None`，比如从 TOML 文件读到的数字。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import BiText, Lang

name = BiText("Tomato and egg stir-fry", "番茄炒蛋")
assert name.get(Lang.ZH) == "番茄炒蛋"
assert name.exact(Lang.EN) == "Tomato and egg stir-fry"
pork = BiText(zh="红烧肉")
assert pork.get(Lang.EN) == "红烧肉"
assert pork.exact(Lang.EN) is None
assert BiText("", "盐").get(Lang.EN) == ""
assert BiText("Salt", "盐") == BiText(en="Salt", zh="盐")
BiText()  # raises ValueError
BiText(en=3)  # raises TypeError
```

### 2.2 `Message` 和 `MessageValue`

- 模块：text
- 功能：工具显示的一段文字，有一个英文模板和一个中文模板，两者的 `{name}` 占位符相同（[架构 5.2](../../architecture.zh-CN.md#52-值)）。创建时缺一种语言或占位符不同，会立即失败。所以任何引入定义该提示的模块的测试都能发现这个错误（ADR-0004）。`MessageValue` 是占位符的值的类型。

签名：

```python
type MessageValue = str | int | BiText


@dataclass(frozen=True, slots=True)
class Message:
    en: str
    zh: str

    @property
    def placeholders(self) -> frozenset[str]: ...

    # Methods: render and to_bitext (2.3).
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `en` | `str` | 英文模板。 | 不能只有空白。 |
| `zh` | `str` | 中文模板。 | 不能只有空白，占位符名称与 `en` 相同。 |

模板遵守这些规则：

1. 占位符是花括号里的一个名称，比如 `{name}`。名称由小写 ASCII 字母、数字和 `_` 组成，以字母开头。
2. 两个模板含有相同的一组名称。一个名称可以出现多次，两个模板里名称的顺序可以不同。
3. 占位符不带转换符，也不带格式说明，`{count:}` 这样空的格式说明也不行。`string.Formatter().parse` 把 `{count:}` 读得与 `{count}` 相同，所以检查要看花括号之间的字符。值本身就是文字，或者是由 `render` 变成文字的 `int` 或 `BiText`（2.3）。
4. 要显示花括号本身，模板把它连写两次，与 `str.format` 相同。

- 返回值：一个 `Message`。`placeholders` 给出它的模板里的名称集合；没有占位符的提示给出空集合。两条提示的两个模板都相等时，它们相等。`Message` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `en` 或 `zh` 不是 `str`。 |
| `ValueError` | `en` 或 `zh` 为空，或者只有空白。 |
| `ValueError` | 模板不是合法的格式字符串，比如含有单独的 `{` 或单独的 `}`。 |
| `ValueError` | 占位符不符合上面的名称规则，比如 `{}`、`{0}`、`{Name}`、`{ name }`、`{tag.en}` 或 `{items[0]}`。 |
| `ValueError` | 占位符带有转换符或格式说明（空的格式说明也算），比如 `{count!r}`、`{count:>3}` 或 `{count:}`。 |
| `ValueError` | 两个模板含有的名称集合不同。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.text import Message

UNKNOWN_RECIPE = Message('Unknown recipe "{recipe}".', "未知菜谱“{recipe}”。")
assert UNKNOWN_RECIPE.placeholders == frozenset({"recipe"})
assert Message("No errors.", "没有错误。").placeholders == frozenset()
Message("{count} recipes.", "共 {total} 个菜谱。")  # raises ValueError
Message("Saved {path}.", " ")  # raises ValueError
Message("Saved {0}.", "已保存 {0}。")  # raises ValueError
Message("{count:>3} recipes.", "{count:>3} 个菜谱。")  # raises ValueError
Message("{count:} recipes.", "{count:} 个菜谱。")  # raises ValueError
```

### 2.3 `Message.render` 和 `Message.to_bitext`

- 模块：text，`Message`（2.2）的方法
- 功能：`render` 用值写出一种语言的提示。`to_bitext` 用值写出两种语言的提示，用于稍后才显示或放进另一条提示里的文字，比如 `Problem` 的位置或列举的一项。

签名：

```python
def render(self, lang: Lang, /, **values: MessageValue) -> str: ...


def to_bitext(self, /, **values: MessageValue) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | `render` 写出的语言。 | 只能按位置传入，所以模板也可以有名为 `lang` 的占位符。 |
| `values` | `MessageValue` 关键字参数 | 按名称给出每个占位符的值。 | 每个占位符一个，没有多余的。 |

- 返回值：
  - `render` 给出 `lang` 的模板，并把每个占位符换成它的值。`str` 原样放入，`int` 写成十进制数字，不加千位分隔符。`BiText` 放入它的 `get(lang)`，所以缺 `lang` 的值会改用它的另一种语言。
  - 值原样放入，所以值里的花括号从不被当作占位符。
  - `to_bitext` 给出 `BiText(self.render(Lang.EN, **values), self.render(Lang.ZH, **values))`。

错误：

两个方法都先检查值的名称，再检查值的类型。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `values` 的名称与占位符不完全一致：有占位符没有值，或者有值没有对应的占位符。 |
| `TypeError` | 值不是 `str`、`int` 或 `BiText`，比如 `float` 或 `None`。`bool` 和 `enum.Enum` 成员也不行，虽然 `bool` 是 `int`，`StrEnum` 成员（比如 `Lang.ZH` 或架构 5.2 的 `Meal`）是 `str`。`StrEnum` 成员会在中文里显示它的英文值。 |
| `ValueError` | `int` 值超过 4300 位，这是 Python 写出 `int` 的上限（`sys.int_info.default_max_str_digits`）。这个错误只来自错误的调用。计数远远达不到这个上限，F05、F06 和 F09 也会给份数定上限（F01 设计第 4 节）。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN_RECIPE = Message('Unknown recipe "{recipe}".', "未知菜谱“{recipe}”。")
assert UNKNOWN_RECIPE.render(Lang.ZH, recipe="tomato-eggs") == "未知菜谱“tomato-eggs”。"
assert UNKNOWN_RECIPE.render(Lang.EN, recipe="{x}") == 'Unknown recipe "{x}".'
both = UNKNOWN_RECIPE.to_bitext(recipe="tomato-eggs")
assert both == BiText('Unknown recipe "tomato-eggs".', "未知菜谱“tomato-eggs”。")

SERVINGS = Message("Servings: {count}   Tags: {tags}", "份数：{count}   标签：{tags}")
tags = BiText("quick, home-style", "快手、家常")
assert SERVINGS.render(Lang.EN, count=2, tags=tags) == "Servings: 2   Tags: quick, home-style"
assert SERVINGS.render(Lang.ZH, count=2, tags=tags) == "份数：2   标签：快手、家常"

NO_OTHER = Message('No other recipe has the tag "{tag}".', "没有别的菜谱带有标签“{tag}”。")
assert NO_OTHER.render(Lang.EN, tag=BiText(zh="素")) == 'No other recipe has the tag "素".'

UNKNOWN_RECIPE.render(Lang.EN)  # raises ValueError
UNKNOWN_RECIPE.render(Lang.EN, recipe="rice", meal="dinner")  # raises ValueError
UNKNOWN_RECIPE.render(Lang.EN, recipe=None)  # raises TypeError
SERVINGS.render(Lang.EN, count=True, tags=tags)  # raises TypeError
UNKNOWN_RECIPE.render(Lang.ZH, recipe=Lang.ZH)  # raises TypeError
```

### 2.4 `Plural`

- 模块：text
- 功能：英文复数：数量为 1 时用一条提示，其他数量用另一条，比如“1 recipe”和“7 recipes”。中文没有复数，所以两条提示的中文模板通常相同。

签名：

```python
@dataclass(frozen=True, slots=True)
class Plural:
    one: Message
    other: Message

    def pick(self, count: int) -> Message: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `one` | `Message` | 数量为 1 时的提示。 | 占位符名称与 `other` 相同。 |
| `other` | `Message` | 其他数量（包括 0）时的提示。 | 占位符名称与 `one` 相同。 |
| `count` | `int` | `pick` 据以选择的数量。 | 任何 `int`。 |

- 返回值：一个 `Plural`。`count` 为 1 时，`pick(count)` 给出 `one`；其他数量（比如 0、2 或 7）给出 `other`。调用方再用值写出这条提示，值里通常包括这个数量。两个 `Plural` 的两条提示都相等时，它们相等。`Plural` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `one` 和 `other` 的占位符名称不同。 |

- 副作用：无
- 性能指标：无

示例：

第二和第三个例子是 F09 原型“List the recipes with one tag”里的行。

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural

WITH_TAG = Plural(
    Message('{count} recipe has the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
    Message('{count} recipes have the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
)
quick = BiText("quick", "快手")
assert WITH_TAG.pick(1).render(Lang.EN, count=1, tag=quick) == '1 recipe has the tag "quick".'
assert WITH_TAG.pick(3).render(Lang.EN, count=3, tag=quick) == '3 recipes have the tag "quick".'
assert WITH_TAG.pick(3).render(Lang.ZH, count=3, tag=quick) == "共 3 个菜谱带有标签“快手”。"
assert WITH_TAG.pick(0) is WITH_TAG.other

ONE_ERROR = Message("{count} error", "{count} 个错误")
Plural(ONE_ERROR, Message("errors", "错误"))  # raises ValueError
```

### 2.5 `RUN_CHECK`、`RUN_HELP_FOR_OPTIONS` 和 `RUN_HELP_FOR_COMMANDS`

- 模块：text
- 功能：架构 3 和 ADR-0004 交给 `text` 的公用提示：数据文件里的错误让命令停下时的最后一行，以及两条指向 `--help` 的提示。其他每条提示都放在显示它的模块的 `messages.py` 里（架构 8）。

签名：

```python
RUN_CHECK: Final[Message] = Message(
    'Run "recipe-menu check" to see every problem.',
    "运行“recipe-menu check”查看所有问题。",
)
RUN_HELP_FOR_OPTIONS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the options.',
    "运行“recipe-menu --help”查看选项。",
)
RUN_HELP_FOR_COMMANDS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the commands.',
    "运行“recipe-menu --help”查看命令。",
)
```

下表说明每条提示的来源，以及命令何时显示它。

| 常量 | 来源 | 何时显示 |
| --- | --- | --- |
| `RUN_CHECK` | 英文见 [`architecture.md` 第 6 节](../../architecture.md#6-error-handling)和 F11 原型“A menu with a mistake”。中文见[架构 6](../../architecture.zh-CN.md#6-错误处理)。 | 数据文件里的第一个错误让 `check` 以外的命令停下之后。 |
| `RUN_HELP_FOR_OPTIONS` | 英文见 F05 原型“Mistakes on the command line”。没有原型显示中文。 | 选项或选项的值写错之后，比如 `--lang fr`。 |
| `RUN_HELP_FOR_COMMANDS` | 英文见 F05 原型“Mistakes on the command line”。没有原型显示中文。 | 命令未知之后，比如 `cook`。 |

参数：无

- 返回值：无。每个常量都是没有占位符的 `Message`，所以 `render` 只接受语言。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.text import RUN_CHECK, RUN_HELP_FOR_COMMANDS

assert RUN_CHECK.render(Lang.EN) == 'Run "recipe-menu check" to see every problem.'
assert RUN_CHECK.render(Lang.ZH) == "运行“recipe-menu check”查看所有问题。"
assert RUN_HELP_FOR_COMMANDS.placeholders == frozenset()
```

### 2.6 `and_list` 和 `comma_list`

- 模块：text
- 功能：把几段文字连成两种语言的一个列举（架构 8）。`and_list` 写出句子里的列举，比如“breakfast, lunch, and dinner”和“早餐、午餐和晚餐”。`comma_list` 写出简单的列举，比如表格单元格里的标签“quick, vegetarian”和“快手、素”。

签名：

```python
def and_list(items: Iterable[str | BiText]) -> BiText: ...


def comma_list(items: Iterable[str | BiText]) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `items` | 由 `str` 或 `BiText` 项组成的可迭代对象 | 要连接的文字，按顺序排列。`str` 项在两种语言里相同，比如菜谱 ID 或分类的键。 | 任意多项，也可以没有。不能是单个 `str`。 |

- 返回值：两种语言都有的 `BiText`。英文连接每项的 `get(Lang.EN)`，中文连接每项的 `get(Lang.ZH)`。所以缺一种语言的项会各自改用另一种语言。下表以 `a`、`b`、`c` 和 `d` 为项，给出各种项数时的文字。

| 项 | `and_list`，英文 | `and_list`，中文 | `comma_list`，英文 | `comma_list`，中文 |
| --- | --- | --- | --- | --- |
| 没有项 | 空字符串 | 空字符串 | 空字符串 | 空字符串 |
| a | `a` | `a` | `a` | `a` |
| a, b | `a and b` | `a 和 b` | `a, b` | `a、b` |
| a, b, c | `a, b, and c` | `a、b 和 c` | `a, b, c` | `a、b、c` |
| a, b, c, d | `a, b, c, and d` | `a、b、c 和 d` | `a, b, c, d` | `a、b、c、d` |

更多的项照最后一行类推。在英文里，`and_list` 用“ and ”连接两项。有三项或更多时，它在项与项之间放“, ”，在最后一项前放“and ”。在中文里，它在项与项之间放“、”，在最后一项前放“和”。两个函数在中文里按这些规则加空格：

1. “、”旁边不加空格，`and_list` 和 `comma_list` 都是这样。
2. 某一项紧挨“和”的字符是 ASCII 字母或数字（`A` 到 `Z`、`a` 到 `z` 或 `0` 到 `9`）时，在这一项和“和”之间加一个空格。这个字符是“和”前面那一项的最后一个字符，或者“和”后面那一项的第一个字符。
3. 空的项没有紧挨“和”的字符，所以它和“和”之间不加空格。
4. 这些规则看每一项的 `get(Lang.ZH)`，所以对没有中文的项，它们看的是这一项的英文文字。

所以 `a`、`b` 和 `c` 这三项得到 `a、b 和 c`。F07 的两项 `7 个菜谱` 和 `1 个周菜单` 得到 `7 个菜谱和 1 个周菜单`。F10 的两项 `“葱”` 和 `“quick”` 得到 `“葱”和“quick”`，因为中文引号不是 ASCII 字母或数字。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `items` 是 `str`。`str` 是由各个字符组成的可迭代对象，不检查的话，`and_list("abc")` 会列出 `a`、`b` 和 `c`。 |
| `TypeError` | 某一项既不是 `str` 也不是 `BiText`，比如 `None`。`enum.Enum` 成员也不行，虽然 `StrEnum` 成员（比如 `Lang.ZH`）是 `str`。它会在中文里显示它的英文值，与 2.3 相同。 |

- 副作用：无
- 性能指标：无

示例：

用 `QUOTED` 的例子给出 F10 原型“Two words, in Chinese”里的两个词。用 `CHECKED` 的例子给出 F07 原型两种语言的第一行。

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural, and_list, comma_list

meals = [BiText("breakfast", "早餐"), BiText("lunch", "午餐"), BiText("dinner", "晚餐")]
assert and_list(meals) == BiText("breakfast, lunch, and dinner", "早餐、午餐和晚餐")
assert and_list(meals[1:]) == BiText("lunch and dinner", "午餐和晚餐")
assert and_list(meals[2:]) == BiText("dinner", "晚餐")
assert and_list([]) == BiText("", "")
assert and_list(["a", "b", "c", "d"]) == BiText("a, b, c, and d", "a、b、c 和 d")
assert and_list(["produce", "meat", "eggs"]).get(Lang.EN) == "produce, meat, and eggs"
assert and_list([BiText("tofu", "豆腐"), BiText(en="quick")]).get(Lang.ZH) == "豆腐和 quick"
tags = [BiText("quick", "快手"), BiText(zh="素")]
assert comma_list(tags) == BiText("quick, 素", "快手、素")

QUOTED = Message('"{word}"', "“{word}”")
words = [QUOTED.to_bitext(word="葱"), QUOTED.to_bitext(word="quick")]
assert and_list(words) == BiText('"葱" and "quick"', "“葱”和“quick”")

SETTINGS = Message("the settings", "设置")
CATALOG = Message("the catalog", "目录")
PANTRY = Message("the pantry", "常备清单")
RECIPES = Plural(
    Message("{count} recipe", "{count} 个菜谱"),
    Message("{count} recipes", "{count} 个菜谱"),
)
WEEK_MENUS = Plural(
    Message("{count} week menu", "{count} 个周菜单"),
    Message("{count} week menus", "{count} 个周菜单"),
)
CHECKED = Message("Checked {files}.", "已检查{files}。")
parts = [
    SETTINGS.to_bitext(),
    CATALOG.to_bitext(),
    PANTRY.to_bitext(),
    RECIPES.pick(7).to_bitext(count=7),
    WEEK_MENUS.pick(1).to_bitext(count=1),
]
files = and_list(parts)
english = CHECKED.render(Lang.EN, files=files)
assert english == "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
chinese = CHECKED.render(Lang.ZH, files=files)
assert chinese == "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。"

and_list("abc")  # raises TypeError
comma_list([Lang.ZH])  # raises TypeError
```

### 2.7 `choose_lang`

- 模块：text
- 功能：按[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 选择命令的语言：先看 `--lang`，再看设置，最后用英文。`cli` 在启动时调用它（F05）。

签名：

```python
def choose_lang(option: Lang | None, setting: Lang | None) -> Lang: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `option` | `Lang` 或 `None` | `--lang` 指定的语言。 | 命令行没有 `--lang` 时为 `None`。 |
| `setting` | `Lang` 或 `None` | 设置里的 `language`。 | 设置没有指定语言，或者没有设置时为 `None`。 |

- 返回值：`option` 不是 `None` 时给出 `option`；否则 `setting` 不是 `None` 时给出 `setting`；否则给出 `Lang.EN`。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.text import choose_lang

assert choose_lang(Lang.EN, Lang.ZH) is Lang.EN
assert choose_lang(None, Lang.ZH) is Lang.ZH
assert choose_lang(None, None) is Lang.EN
```

### 2.8 `display_width`

- 模块：text
- 功能：一段文字在 Windows Terminal 里占的列数，按 ADR-0004 的规则计算。只有 `text` 计算宽度（ADR-0004），`format_table` 用它对齐各列。

签名：

```python
def display_width(text: str) -> int: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 要测量的文字，比如表格单元格的一行。 | 任何字符串。换行符和其他字符一样算一列，所以一次只测量一行。 |

- 返回值：`text` 里各字符所占列数之和，空字符串为 0。`display_width` 用当前 Python 的 `unicodedata` 模块，按下面第一条适用的规则给出每个字符的列数：
  1. 组合用的附加符号占 0 列。附加符号是通用类别为 `Mn`（非间距符号）或 `Me`（包围符号）的字符。
  2. East Asian Width 为 `W`（宽）或 `F`（全角）的字符占 2 列。
  3. 其他字符都占 1 列。这包括 `“`、`—` 和 `×` 这类宽度不定的字符（Windows Terminal 把它们画成一列宽），以及类别为 `Mc` 的间距符号。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.text import display_width

assert display_width("Tomato") == 6
assert display_width("番茄鸡蛋面") == 10
assert display_width("周一 11月16日") == 13
assert display_width("，、：") == 6
assert display_width("—×“”") == 4
assert display_width("e\N{COMBINING ACUTE ACCENT}") == 1
assert display_width("") == 0
```

### 2.9 `format_table`

- 模块：text
- 功能：按显示宽度把各行排成对齐的列。它给出原型里的表格：`list` 和 `search`（F09 和 F10）、`show` 的食材（F09）、`menu show`（F11）、购物清单（F13）、帮助（F05），以及 `init` 写出的文件列表（F08）。每一列都左对齐，与所有原型一样。

签名：

```python
def format_table(
    rows: Sequence[Sequence[str]],
    *,
    indent: int = 0,
    gap: int = 3,
    min_widths: Sequence[int] = (),
) -> tuple[str, ...]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `rows` | 行的序列，每行是 `str` 单元格的序列 | 各行；表格有表头时，表头在最前面。 | 不能是 `str`，每行也不能是 `str`。每行的单元格数相同，至少 1 个。可以没有行。 |
| `indent` | `int` | 每行前面的空格数，比如 `show` 的食材是 2。 | 0 或更多。 |
| `gap` | `int` | 两列之间的空格数。所有原型都用 3，只有 `init` 的文件列表用 4。 | 1 或更多。 |
| `min_widths` | `int` 的序列 | 从左起每列的最小宽度，以列为单位，不含间隔。F05 需要它，因为帮助在两种语言里的列宽相同。 | 每项为 0 或更多。项数不超过一行的单元格数。最后一项之后的列没有最小宽度。 |

- 返回值：表格的各行，不带换行符，按这些规则：
  1. 单元格的行是 `cell.splitlines()`；结果为空时（比如 `""`），是一个空行。一行表格占的行数等于其中行数最多的单元格。行数较少的单元格在后面的行里为空。
  2. 一列的宽度是它各单元格里各行的最大 `display_width`；这一列在 `min_widths` 里的项更大时，取那一项。
  3. 每行以 `indent` 个空格开头，后面依次是每列的这一行，左对齐。最后一列以外的列用空格补足到列宽，后面再跟 `gap` 个空格。最后一列不补空格，所以它在 `min_widths` 里的项不起作用。
  4. 删除每行末尾的空格（U+0020）。所以行末的空单元格不加任何内容，各单元格都为空的行是空字符串。
  5. 各行按表格行的顺序排列。没有行时，`format_table` 给出空元组。
  6. 单元格从不被截断或折行。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `rows` 或其中某一行是 `str`。`str` 是由各个字符组成的序列，不检查的话，`format_table(["ab", "cd"])` 会让每个字母占一个单元格。`format_table` 先检查这个错误，再检查其他错误。 |
| `ValueError` | 各行的单元格数不全相同，或者行没有单元格。 |
| `ValueError` | `indent` 小于 0、`gap` 小于 1，或者 `min_widths` 有一项小于 0。没有行时也检查这些。 |
| `ValueError` | `min_widths` 的项数超过一行的单元格数。 |

- 副作用：无
- 性能指标：无

示例：

每个预期的行都是其上方注释所指原型里的一行。

```python
from recipe_menu.text import format_table

# F09 "List the recipes", in Chinese.
recipes = [
    ("ID", "名称", "份数", "标签"),
    ("choy-sum", "清炒菜心", "2", "快手、素"),
    ("tomato-egg-noodles", "番茄鸡蛋面", "2", "快手、主食"),
]
assert format_table(recipes) == (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
)

# F11 "Show the week after you fill it": a cell with two lines.
week = [
    ("Day", "Lunch", "Dinner"),
    ("Mon 16 Nov", "—", "Tomato and egg stir-fry ×2\nStir-fried choy sum ×2"),
    ("Sat 21 Nov", "Tomato and egg noodles ×2", "—"),
]
assert format_table(week) == (
    "Day          Lunch                       Dinner",
    "Mon 16 Nov   —                           Tomato and egg stir-fry ×2",
    "                                         Stir-fried choy sum ×2",
    "Sat 21 Nov   Tomato and egg noodles ×2   —",
)

# F09 "Show one recipe for 4 servings, in Chinese": an indent and empty last cells.
ingredients = [
    ("番茄", "600 g", "切块"),
    ("鸡蛋", "6 个", ""),
    ("食用油", "4 汤匙", ""),
]
assert format_table(ingredients, indent=2) == (
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  食用油   4 汤匙",
)

# F08 "In English": a gap of 4.
listing = [
    ("catalog.toml", "6 categories, 22 ingredients, 5 tags"),
    ("recipes\\tomato-egg.toml", "an example recipe in both languages"),
]
assert format_table(listing, indent=2, gap=4) == (
    "  catalog.toml               6 categories, 22 ingredients, 5 tags",
    "  recipes\\tomato-egg.toml    an example recipe in both languages",
)

# F05 "Help in Chinese": the width of "menu show [WEEK]" in the English help.
commands = [
    ("init", "创建数据文件夹和示例数据。"),
    ("menu show [周]", "查看一个周菜单。"),
]
assert format_table(commands, indent=2, min_widths=(16,)) == (
    "  init               创建数据文件夹和示例数据。",
    "  menu show [周]     查看一个周菜单。",
)

assert format_table([]) == ()
format_table([("a", "b"), ("c",)])  # raises ValueError
format_table(recipes, gap=0)  # raises ValueError
format_table(recipes, min_widths=(1, 1, 1, 1, 1))  # raises ValueError
format_table(["ab", "cd"])  # raises TypeError
```

### 2.10 `use_utf8`

- 模块：text
- 功能：让控制台输出流写 UTF-8，所以不论控制台代码页是什么，中文都能正确显示（ADR-0004）。启动时，`cli` 对 `sys.stdout` 和 `sys.stderr` 调用它，再通过 `Context` 把这两个流传下去（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。

签名：

```python
def use_utf8(stream: TextIO) -> None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `stream` | `TextIO` | 一个输出流，比如 `sys.stdout`。 | 已打开。 |

- 返回值：无

错误：无

- 副作用：
  - `stream` 是 `io.TextIOWrapper` 时（`sys.stdout` 和 `sys.stderr` 就是），`use_utf8` 以 `encoding="utf-8"` 和 `errors="backslashreplace"` 调用它的 `reconfigure`。`reconfigure` 先把流里已有的内容写出去。此后这个流写出 UTF-8。单独的代理码元是 UTF-8 唯一不能编码的一类码位，流把它写成 `\udcff` 这样的转义，从不因此抛异常。
  - 其他流（比如测试里的 `io.StringIO`）保持原样。
  - 在 Windows 控制台上，Python 通过控制台的 Unicode 接口写入，所以代码页在那里不起作用。调用之后，PowerShell 重定向或用管道传递的输出是 UTF-8（ADR-0004 第 5 节）。
- 性能指标：无

示例：

```python
import io

from recipe_menu.text import use_utf8

raw = io.BytesIO()
stream = io.TextIOWrapper(raw, encoding="cp1252")
use_utf8(stream)
assert stream.encoding == "utf-8"
stream.write("番茄 \udcff")
stream.flush()
assert raw.getvalue() == "番茄 \\udcff".encode()
use_utf8(io.StringIO())  # changes nothing
```

## 3. 对已有接口的修改

无。F02 把 `BiText` 加入 `recipe_menu.lang` 和它的 `__all__`。`Lang` 保持 F01 设计 2.1 给出的样子，架构 3 把 `lang` 同时交给 F01 和 F02。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `BiText` 与 `Lang` 一起放在 `lang` 里，架构 3 把这个模块交给 F01 和 F02。它的字段和改用另一种语言的规则与架构 5.2 一致。`text` 得到的正是架构 3 列给它的内容，并且只引用 `lang`。`BiText`、`Message` 和 `Plural` 都是带 `slots=True` 的冻结数据类，接口返回的集合是元组和 frozenset（架构 8）。以 `BiText` 表示的位置和 `MessageValue` 类型的值，符合架构 5.2 的 `Problem` 和 `UsageError`。`format_table` 返回各行，`use_utf8` 以参数接收流，所以只有 `cli` 接触控制台，输出写到 `Context` 里的流（架构 8）。架构师在 Python 3.13.18 里按 2.9 的规则建了一个模型，用它重建了原型里的每个表格。每一行都与原型完全一致：两种语言的 F05 命令和选项（`min_widths=(16,)`）、F08 的文件列表（`gap=4`）、F09 的菜谱列表和食材、F10 的结果、F11 含多行单元格的一周，以及 F13 的清单。选择 5 也由此通过。第 2 轮里，模型改按 0.2 版，每个表格仍与原型完全一致，因为 2.9 新增的 `TypeError` 不改变任何排版。有两点留给后续设计，不阻塞。F05 的英文帮助也需要 `min_widths`，因为选项一列沿用命令一列的宽度。F13 可以把所有分类的清单排成一个表格，再把每个分类的标题插到各行之间，因为这个表格没有含换行符的单元格。 |
| 遵守错误处理和命名约定 | Pass | 第 1 轮的发现 1 已经解决。2.6 的规则 1 到 4 只在某一项紧挨“和”的字符是 ASCII 字母或数字时，才在这一项和“和”之间加一个空格。项目的中文模板也这样在中文和 ASCII 文字之间加空格，比如 `共 {count} 个菜谱`。所以 `and_list` 能写出原型里的每个中文列举：F07 的 `7 个菜谱和 1 个周菜单`、F08 的餐次 `午餐和晚餐`，以及 F10 的 `“葱”和“quick”` 和 `“豆腐”和“quick”`。没有命令需要手工拼接列举（架构 8）。ASCII 以外的字母旁边不加空格，比如 `café和茶`，原型里没有这种情况。接口设计师采纳了发现 2 到 5。每个新增的错误都来自错误的调用（架构 6）：类型不对的值引发 `TypeError`，模板 `{count:}` 引发 `ValueError`。拒绝所有 `enum.Enum` 成员，使 `Meal` 这样的 `StrEnum` 的英文值不会出现在中文里，调用方要传入这一餐的双语名称，即一个 `BiText`。`format_table` 先检查 `str`，再检查其他错误，所以以 `str` 作为一行时，总是得到说明这个错误的 `TypeError`。有一点不阻塞。`format_table` 不检查单元格的类型，所以 `StrEnum` 单元格会在中文表格里显示它的英文值。逐行比较中文表格和原型的测试能发现这个问题。接口设计师在第 1 轮列出的选择仍然通过。选择 1：空字符串也算文字，使 `and_list([])` 仍是合法的 `BiText`；`BiText` 的 `TypeError` 能发现跳过了文件值检查的读取函数（架构 6）。选择 2：占位符不带转换符和格式说明，模板就无法补齐值。`str.format` 按码位补齐，所以这样能让宽度只由 `text` 计算（ADR-0004）。`render` 的错误都来自错误的调用（架构 6），拒绝 `bool` 让 `True` 不会出现在文字里。选择 3：`RUN_HELP_FOR_OPTIONS` 和 `RUN_HELP_FOR_COMMANDS` 的中文沿用架构 6 里 `RUN_CHECK` 和各中文原型的句式，比如 `运行“recipe-menu init”创建它`。Troy 批准这个 PR 时会读到这两段文字（R18）。选择 4：ADR-0004 没有定义组合用的附加符号。常见的 `wcwidth` 规则让 `Mn` 和 `Me` 不占列，间距符号（`Mc`）只出现在工具不显示的文字里，所以 ADR 不需要修改。选择 6：`errors="backslashreplace"` 把单独的代理码元写成转义。文件名可能含有单独的代理码元，菜谱 ID 也就可能含有，所以坏数据在这里从不引起回溯信息（架构 6）。名称遵守 PEP 8。 |
| 不和已有接口重复 | Pass | F01 导出 `Lang` 和 `units` 的名称。它的单位名称是 `Unit.label` 和 `Quantity.to_text` 背后的普通数据（ADR-0004），F01 也没有保存两种语言文字的类型，所以 `BiText` 不重复任何接口。`Plural` 在两条提示中选一条，`Unit.label(plural=True)` 给出单位名称，F01 的审查已经记录了这一点。`and_list` 写出句子里的列举，`comma_list` 写出简单的列举。这正是原型里的两种列举。一个 `format_table` 排出原型里的所有表格。 |
| 只依赖排序在前面的功能 | Pass | F02 没有功能依赖。它使用 F01 创建的 `lang`，与架构 4 列出的一致。它的接口只需要标准库，比如 `enum`、`unicodedata` 和 `io`，所以没有新依赖需要按 R16 审查。第 2 节列出的后续功能调用 F02，F02 不调用其中任何一个。`docs/rules.md` 没有交给架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | `text` 只引用 `lang`，不保存状态，不读取任何东西，也不打印。`use_utf8` 只改变传给它的流。每个调用方通过 `indent`、`gap` 和 `min_widths` 把自己的排版交给 `format_table`，所以没有命令依赖只有 `text` 知道的宽度。2.6 的空格规则只看各项的文字，所以调用方不需要知道这些规则，F07 和 F10 的那几行也出自同一个函数。第 2 节对 F03 到 F13 的计划不约束后续设计，每个设计都会单独审查。有两点留给后续设计。F03 和 F04：空字符串也算文字，所以每个读取函数自己决定文件里空的或只有空白的名称是否算缺失，并为缺失的名称传入 `None`。否则 `list` 会显示空名称，`check` 也不会警告。F05 和 F11：架构 6 规定退出码为 2 的错误以一行指向 `recipe-menu --help` 的提示结束，但 F11 原型显示 `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".`，后面没有这一行。无论怎样，F02 的接口都不变，因为 `UsageError` 后面跟哪条提示由 `app` 和 `cli` 决定。架构师建议 F05 的设计让 `UsageError` 指定它的提示，或者不带提示。这样架构 6 就可以对已经说明该怎么写的提示免除这一行。对架构 6 的这项修改由 Troy 在 F05 设计时决定。 |
| 修改已实现的接口时走了变更流程 | Pass | F01 的 `lang` 已经实现。F02 把 `BiText` 加入 `recipe_menu.lang` 和它的 `__all__`，`Lang` 保持 F01 设计 2.1 给出的样子，与架构 3 的安排一致。F01 的测试都不检查 `lang` 导出的名称，所以这次加入不会让任何测试失败。第 3 节写“无”，是对的。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 一个阻塞问题，即发现 1。在中文里，`and_list` 在“和”两边不加空格（2.6），所以写不出 F07 原型的 `7 个菜谱和 1 个周菜单`，2.6 的最后一个例子也不成立。架构师在 Python 3.13.18 里按设计的规则建了模型，运行了第 2 节的每个例子。每个代码块都能解析，并与英文版相同，其余每个预期值都符合设计的规则。发现 2 到 5 不阻塞。`StrEnum` 值，比如 `Lang.ZH` 或架构 5.2 的 `Meal`，会作为 `str` 通过 `render`，在中文里显示它的英文值（2.3）。2.2 没有说明格式说明为空的 `{count:}` 算不算错。把单个 `str` 传给 `and_list`、`comma_list` 或 `format_table` 能通过类型检查，结果是由它的各个字母组成的列举（2.6 和 2.9）。2.8 的 `é` 是 `e` 后跟 U+0301，以后修改时可能变成 U+00E9，从而不再测试规则 1。 | 要求修改。接口设计师按发现 1 修改 2.6，并决定如何处理发现 2 到 5。 |
| 2 | 没有阻塞问题。架构师用 `git diff f55f9de HEAD` 检查了第 1 轮以后的每处修改，把模型改按 0.2 版，并在 Python 3.13.18 里重新运行了第 2 节的每个例子。每个代码块都能解析，并与英文版相同，每个断言和每个 `# raises` 都成立。模型重建的每个原型表格仍与原型完全一致。探测脚本确认 2.6 的规则对两个和三个带引号的词、空的项以及改用英文的项都成立。它们还确认 `string.Formatter().parse` 对 `{count:}` 和 `{count}` 给出相同的结果，与 2.2 的说法一致。有一点不阻塞：`format_table` 不检查单元格的类型（遵守错误处理和命名约定）。 | 批准。2.6 的规则 1 到 4 解决了发现 1，接口设计师采纳了发现 2 到 5。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-10 | 初稿。 |
| 0.2 | 2026-11-10 | 回应架构师审查第 1 轮。在中文里，某一项紧挨“和”的字符是 ASCII 字母或数字时，`and_list` 在这一项和“和”之间加一个空格，所以能写出 F07 的那一行，F10 的那一行也不变（2.6）。模板拒绝 `{count:}` 这样空的格式说明（2.2）。`render` 拒绝 `enum.Enum` 成员（2.3）。`and_list` 和 `comma_list` 拒绝以单个 `str` 作为 `items`，也拒绝既不是 `str` 也不是 `BiText` 的项和 `enum.Enum` 成员（2.6）。`format_table` 拒绝以 `str` 作为 `rows` 或其中的一行（2.9）。2.8 中组合用附加符号的例子用转义写出 U+0301。 |
| 1.0 | 2026-11-10 | Troy 批准。 |
