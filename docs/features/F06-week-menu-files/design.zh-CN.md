---
troy-doc: "F06-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-12"
status: "Troy 已于 2026-11-12 批准"
mirror-of: "design.md"
---

# F06 周菜单文件：接口设计

## 1. 功能

- 编号和名称：F06 周菜单文件
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：F04、F05

## 2. 接口

F06 构建领域层模块 `menus`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.menus` 导出 `Day`、`Dish`、`IsoWeek`、`MealSlot`、`NOT_A_WEEK`、`WeekMenu`、`list_menu_weeks`、`read_week_menu`、`short_date` 和 `week_from_argument`，它的 `__init__.py` 在 `__all__` 里列出这些名称。它的提示放在 `menus/messages.py` 里。`NOT_A_WEEK` 导出给各个命令使用（2.7），其他提示都只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。菜单文件的格式就是 `docs/prototypes/example-data.md` 里 `menus/2026-W47.toml` 的格式。F11 原型展示了 `menu new` 写出的文件，F07 原型展示了 `check` 怎样报告菜单的问题。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F06 提供的接口 |
| --- | --- |
| 读取一个周菜单文件：它的 ISO 周。 | `read_week_menu`（2.9），它读取一个 `IsoWeek`（2.1）的文件，并对照文件名检查文件里的 `week`。`list_menu_weeks`（2.8）给出有文件的各个周。 |
| 读取各天、设置里的几餐，以及每道菜和它的份数。 | `read_week_menu` 给出的 `WeekMenu`（2.6）。它保存 `Settings` 里的餐次，并为每个 `Day`（2.3）的每一餐保存一个 `MealSlot`（2.5）。每个餐位保存它的 `Dish` 值（2.4），份数来自文件或设置。 |
| 把 `this` 和 `next` 换成 ISO 周。需要指定周的命令接受 ISO 周、`this` 或 `next`；不指定时使用本周（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | `week_from_argument` 和 `NOT_A_WEEK`（2.7），以及 `IsoWeek.of`（2.1）。 |
| 报告未知的菜谱 ID、未知的餐和错误的份数及其位置。 | `list_menu_weeks` 和 `read_week_menu` 返回的 `Problem` 值，每个都带有它的文件和 2.9 的位置。 |
| `menus` 负责 ISO 周、本周和下周，以及两种语言的日期和星期名称（架构 3）。 | `IsoWeek`（2.1），`IsoWeek.date_range` 和 `short_date`（2.2），以及 `Day.label`（2.3）。 |

下面每个接口都遵守这些规则：

- `menus` 在包内只引用 `lang`、`text`、`datafile`、`settings` 和 `recipes`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。它从 `recipes` 只用 `is_recipe_id`。
- `menus` 只通过 `datafile` 访问磁盘：它用 `list_toml_files` 列出 `menus/`，用 `read_toml` 读取每个文件。没有接口写文件、打印、读环境变量或今天的日期，也没有接口保存状态。今天的日期由调用方传进来（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。它检查整个文件，为每处错误记下一个 `Problem`，然后继续，所以运行一次 `check` 就能列出所有问题。下面各个“错误”表里的异常都来自错误的调用，也就是 bug。
- 每个值都是带 `slots=True` 的冻结 dataclass 或枚举，其中的集合用元组或 frozenset（架构 8）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F06 的接口都没有性能指标。PT01 计时的命令里，`check` 读取 52 个周菜单，`menu show` 和 `shop` 读取一个有 63 道菜的周（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)）。所以 `list_menu_weeks` 只列一次 `menus/`。`read_week_menu` 只把一个文件读一次，耗时与文件的大小成正比，并在 `frozenset` 里查找每道菜的 ID。

这两个读取函数像 F04 的读取函数那样分工（架构 8）：

- `list_menu_weeks` 不读任何文件。它从 `menus/` 里的文件名得出各个周，所以 F07 能数出菜单的个数，F11、F13 和 F14 能区分没有菜单的周和出错的文件，都不用解析任何菜单。
- `read_week_menu` 只读一个周的文件，不列出任何文件夹。调用方传入 `list_menu_weeks` 给出的周，以及 `list_recipe_ids` 给出的菜谱 ID。

这份设计做了以下选择。每条后面括号里的小节给出它的规则。

1. **周只有一种写法。** 周写成四位数字的 ISO 年份、`-W` 和两位数字的周数，比如 `2026-W47`（2.1）。`IsoWeek.parse` 只读取与 `str` 写出的文字完全相同的文字，无论是在文件名里、键 `week` 里还是在命令行上。所以 `2026-w47`、`2026-W7` 和 `2026-W99` 都不是周。`2025-W53` 也不是周，因为 2025 年只有 52 周。在 Windows 上，`menus/2026-w47.toml` 会被当作周 `2026-W47` 的文件打开，而在 Linux 上不会，所以严格比较名称让两个系统的结果一致（F04 设计第 4 节）。只有一种写法也与帮助里关于周的说明（F05 设计 2.10）和提示 `NOT_A_WEEK` 一致。
2. **文件名给出各个周。** `list_menu_weeks` 为 `menus/` 里每个是周的名称给出那个周（2.8）。它传递 `list_toml_files` 的问题，并为其他每个 `.toml` 名称给出一个错误，和 `list_recipe_ids` 对 `recipes/` 的做法相同。缺少 `menus/` 文件夹是错误，因为 `init` 会创建它。
3. **读取函数接收设置，或者没有设置。** `read_week_menu` 接收菜单要用的餐次和份数所在的 `Settings`；设置读不了时，接收 `None`（2.9）。传入 `None` 时，它做所有不依赖设置的检查。它接受全部三种餐次，用 `UNKNOWN_KEY` 报告根本不是餐次的日表键，并且不给出菜单，就像 `read_recipe` 没有目录时不给出菜谱一样。所以 F07 不会报告只因 `Settings()` 的默认餐次而产生的问题；设置文件出错后，`context.settings` 保存的正是这些默认值（F05 设计 2.4）。
4. **菜谱 ID 由调用方传入。** `read_week_menu` 以 `frozenset` 的形式接收 `list_recipe_ids` 的 ID。一道菜的 ID 不符合 `is_recipe_id` 的规则，或者不在这个集合里时，它写的就是未知菜谱。F06 从不用一道菜拼出路径。它只用 `IsoWeek` 拼出菜单的路径，所以 `DataFolder.menu_file` 永远不会收到错误的名称（F03 设计 2.1）。F07 为它的所有菜单只建一次这个集合，所以 52 个菜单只需要列一次 `recipes/`。
5. **文件可以不写某些天和某些餐。** 键 `week` 必须写，而且它写的周必须与文件名一致。文件里没写的一天没有菜，某天里没写的设置中的一餐也没有菜。这样不会丢失任何东西；你在设置里加上一餐之前写的菜单也依然正确。日表里的键如果不是设置中的任何一餐，就是错误，因为 `menu show` 和 `shop` 会漏掉它的菜。唯一的例外是 `breakfast = []` 这样没有菜的一餐。所以你在设置里去掉一餐之前写的菜单也依然正确（2.9）。
6. **菜和它的份数。** 一道菜是放在引号里的菜谱 ID，或者是带有 `recipe` 和可选的 `servings` 的表，和 `example-data.md` 里一样。没写份数的菜使用 `settings.servings`（[架构 5.2](../../architecture.zh-CN.md#52-值)）。`read_week_menu` 用 `read_servings` 在这道菜的位置读取份数，所以 1 到 100 的范围和它的三条提示都只在一个地方（F05 设计选择 3）。提示只通过 `read_servings` 显示文件里的数字，而 `read_servings` 把它限制在 15 位以内（F04 设计选择 2）。`week` 的文字作为文字放进提示。所以没有提示会碰到 F02 的 4,300 位限制。
7. **菜单要么完整，要么没有。** 文件有错误时，`read_week_menu` 不给出菜单，就像 `read_recipe` 不给出菜谱一样（2.9）。`check` 以外的每个命令遇到第一个错误就停下（架构 6），所以没有命令会用到有错误的菜单。对菜单的检查都不给出警告。
8. **两种语言的日期和名称。** `menus` 给出星期名称（2.3），并把一天的日期和一周的日期写成文字（2.2），这是架构 3 分配给它的。所以 F11 和 F13 写出相同的文字。`menus` 还导出 `NOT_A_WEEK`，也就是命令行上周写错时的提示（2.7）。F11、F13 和 F14 都显示它，而 `shop` 不能引用 `menu`（架构 3），所以它唯一的一份放在这里。这条提示已经说明要写什么，所以它的 `UsageError` 不带提示行，与 ADR-0008（决定 A）、F11 原型“A week without a menu”和 v0.1-S15 一致。

以下后续功能打算调用这些接口：

- F07 调用一次 `list_menu_weeks`，用它的周数写出“1 个周菜单”，并报告它的问题。它用 `read_week_menu` 读取每个周。它传入 `read_settings` 给出的设置，出错后就是 `None`，而不是 `context.settings`，因为那时它保存的是 `Settings()`（选择 3）。它传入由 `list_recipe_ids` 的 ID 组成的 `frozenset`，只为所有菜单建一次。
- F08 创建空文件夹 `menus/`，`list_menu_weeks` 对它不给出任何周，也不给出问题。
- F11 的 `menu new` 和 `menu show` 用 `week_from_argument(value, context.today)` 得到它们的周，其中 `value` 是参数 `WEEK` 的值，命令行没写时为 `None`。它给出 `None` 时，它们抛出 `UsageError(NOT_A_WEEK, None, week=value)`。`menu show` 在 `list_menu_weeks` 的周里查找这个周，用 `read_week_menu` 和 `context.settings` 读取它，并用 `first_error` 和 `stop_at_error` 在第一个错误处停下，和 F11 原型“A menu with a mistake”一样。它用 `str(week)` 和 `date_range` 写出这个周，用 `short_date` 写出每天那一行，用 `Meal.heading` 写出每一餐那一列，并用 `WeekMenu.dishes` 得到每个格子里的菜。`menu new` 写出的文件，`read_week_menu` 读它时不给出任何问题，并且每个餐位都是空的。在 Windows 上，文件 `2026-w47.toml` 会让 `datafile` 无法创建 `2026-W47.toml`，而 `list_menu_weeks` 会报告这个文件，所以由 F11 的设计决定 `menu new` 这时说什么。
- F12 从 `WeekMenu.slots` 取得各道菜，并按 `Fraction(dish.servings, recipe.servings)` 换算每个菜谱。F11 和 F12 只在餐位有菜时才把这一餐计入。F11 和 F13 原型里的“4 餐，9 道菜”就是这样数出来的。
- F13 的 `shop` 像 F11 那样得到它的周，并在标题里显示 `date_range`。对于没有菜单文件的周，F11 和 F13 显示同一行文字，而 `shop` 不能引用 `menu`。所以由它们的设计决定 `menus` 是否也导出这条提示。
- F14 把没有菜的餐位当作空的一餐，并在写文件之前用 `read_week_menu` 检查菜单。

troy-mode 的流程有一个模拟实现 PR 和一个正式实现 PR。`menus` 可以放进 R03 的五个文件里：`__init__.py`、`messages.py` 和三个内部文件。模拟实现定义所有常量，比如 `Day` 的成员和每条提示，这样模块能被导入。只检查常量的测试，比如只检查 `NOT_A_WEEK` 的文字，在模拟实现上也会通过，从而违反 R09，架构师在 F05 中已经指出过这一点。

### 2.1 `IsoWeek`

- 模块：menus
- 功能：一个 ISO 周，比如 `2026-W47`，即 2026 年 11 月 16 日（周一）至 11 月 22 日（周日）（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，[架构 5.2](../../architecture.zh-CN.md#52-值)）。它按文件名的写法写出和读取周，给出它的七个日期，并给出一个日期所在的周，所以调用方能从今天的日期得出本周。

签名：

```python
@dataclass(frozen=True, slots=True, order=True)
class IsoWeek:
    year: int
    week: int

    @classmethod
    def of(cls, day: date) -> IsoWeek: ...

    @classmethod
    def parse(cls, text: str) -> IsoWeek | None: ...

    @property
    def dates(self) -> tuple[date, ...]: ...

    # Property: date_range (2.2).

    def __str__(self) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `year` | `int` | ISO 年份。在新年前后，它可能与这一周里某个日期的公历年份不同。 | 1 到 9999。不能是 `bool`。 |
| `week` | `int` | ISO 年份里的第几周。 | 1 到 `year` 的周数。`year` 年 12 月 28 日落在第 53 周时，周数是 53，否则是 52。不能是 `bool`。这一周的周日不晚于 9999 年 12 月 31 日，也就是 `datetime.date` 的最后一天，所以周日本应是 10000 年 1 月 2 日的 `9999-W52` 不是周。 |
| `day` | `date` | 一个日期，供 `of` 使用。 | 不能是 9999 年 12 月 27 日到 31 日，这几天落在 `9999-W52`。 |
| `text` | `str` | 要读取的文字，供 `parse` 使用，比如去掉 `.toml` 的文件名。 | 任意字符串。 |

- 返回值：一个 `IsoWeek`。
  - `str(week)` 给出 `f"{year:04d}-W{week:02d}"`，比如 `2026-W47`、`2027-W01` 或 `0001-W01`。文件名、键 `week` 和每条提示都这样写周。
  - `IsoWeek.of(day)` 给出包含 `day` 的周，年份和周数来自 `day.isocalendar()`。所以 2026 年 11 月 10 日在 `2026-W46`，2027 年 1 月 1 日在 `2026-W53`，2024 年 12 月 30 日在 `2025-W01`。
  - `IsoWeek.parse(text)` 给出 `str` 等于 `text` 的那个周；没有这样的周时给出 `None`。所以 `text` 由四个 ASCII 数字、`-W` 和两个 ASCII 数字组成，前后没有别的字符，并且按上面的约束写的是一个周。对任何 `str`，`parse` 都不会抛异常。
  - `dates` 给出这一周的七个日期，从周一到周日，顺序与 `Day`（2.3）相同。
  - 年份和周数都相等时，两个周相等。周先按年份比较，再按周数比较，所以 `sorted` 给出时间顺序，这也是它们的 `str` 的顺序。`IsoWeek` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `year` 或 `week` 不是 `int`，或者是 `bool`。 |
| `ValueError` | `year` 和 `week` 不符合上面的约束，比如 `IsoWeek(2025, 53)`、`IsoWeek(2026, 0)` 或 `IsoWeek(9999, 52)`。 |
| `ValueError` | `of` 收到 9999 年 12 月 27 日到 31 日之间的日期。 |

- 副作用：无
- 性能指标：无

示例：

```python
from datetime import date

from recipe_menu.menus import IsoWeek

week = IsoWeek(2026, 47)
assert str(week) == "2026-W47"
assert IsoWeek.parse("2026-W47") == week
assert str(IsoWeek(2027, 1)) == "2027-W01"
assert IsoWeek.parse("0001-W01") == IsoWeek(1, 1)
assert IsoWeek.of(date(2026, 11, 10)) == IsoWeek(2026, 46)
assert IsoWeek.of(date(2027, 1, 1)) == IsoWeek(2026, 53)
assert IsoWeek.of(date(2024, 12, 30)) == IsoWeek(2025, 1)
assert week.dates == tuple(date(2026, 11, day) for day in range(16, 23))
assert IsoWeek(2026, 53).dates[-1] == date(2027, 1, 3)
assert IsoWeek.parse("2026-W53") == IsoWeek(2026, 53)
assert IsoWeek(2026, 53) < IsoWeek(2027, 1)
wrong = ["2025-W53", "2026-W99", "2026-W00", "2026-w47", "2026-W7", " 2026-W47", "2026-W47\n"]
assert [IsoWeek.parse(text) for text in wrong] == [None] * 7
fullwidth = "".join(chr(0xFF10 + int(digit)) for digit in "2026")
assert IsoWeek.parse(fullwidth + "-W47") is None

IsoWeek(2025, 53)  # raises ValueError
IsoWeek(2026, 0)  # raises ValueError
IsoWeek(9999, 52)  # raises ValueError
IsoWeek(2026, True)  # raises TypeError
IsoWeek.of(date(9999, 12, 31))  # raises ValueError
```

### 2.2 `IsoWeek.date_range` 和 `short_date`

- 模块：menus。`date_range` 是 `IsoWeek`（2.1）的属性。
- 功能：把一周的日期和一天的日期写成两种语言的文字（[架构 3](../../architecture.zh-CN.md#3-模块)，ADR-0004）。F11 和 F13 在周的后面显示 `date_range`，比如“2026-W47 菜单，2026年11月16日至22日”；F11 在每天那一行的开头显示 `short_date`，比如“周一 11月16日”。

签名：

```python
@property
def date_range(self) -> BiText: ...


def short_date(day: date) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `day` | `date` | 要写出的日期。 | 无 |

- 返回值：一个两种语言都有值的 `BiText`。
  - `date_range` 按下面第一张表里第一个适用的行写出这一周的周一和周日。`first` 和 `last` 是周一和周日在当月的日期。
  - `short_date(day)` 的英文写成 `{weekday} {day} {month}`，中文写成 `{weekday} {month}月{day}日`。`weekday` 在英文里是星期的简称，在中文里是这一天的 `label`（2.3），比如 `Mon` 和 `周一`。所以 2026 年 11 月 16 日给出 `Mon 16 Nov` 和 `周一 11月16日`，也就是 F11 原型“Show the week after you fill it”里的第一列格子。

| 情况 | 英文 | 中文 | 示例 |
| --- | --- | --- | --- |
| 周一和周日在同一个月。 | `{first} to {last} {month} {year}` | `{year}年{month}月{first}日至{last}日` | `2026-W47`：`16 to 22 November 2026` 和 `2026年11月16日至22日` |
| 周一和周日在同一年的两个月。 | `{first} {first_month} to {last} {last_month} {year}` | `{year}年{first_month}月{first}日至{last_month}月{last}日` | `2026-W49`：`30 November to 6 December 2026` 和 `2026年11月30日至12月6日` |
| 周一和周日在两个年份。 | `{first} {first_month} {first_year} to {last} {last_month} {last_year}` | `{first_year}年{first_month}月{first}日至{last_year}年{last_month}月{last}日` | `2026-W53`：`28 December 2026 to 3 January 2027` 和 `2026年12月28日至2027年1月3日` |

这三个模板和 `short_date` 的模板都是 `menus/messages.py` 里的提示。日和年份是不带前导零的 `int` 值。月份在英文里是它的名称，在中文里是它的数字：

| 月份 | `date_range` 里的英文 | `short_date` 里的英文 | 中文 |
| --- | --- | --- | --- |
| 1 | `January` | `Jan` | `1` |
| 2 | `February` | `Feb` | `2` |
| 3 | `March` | `Mar` | `3` |
| 4 | `April` | `Apr` | `4` |
| 5 | `May` | `May` | `5` |
| 6 | `June` | `Jun` | `6` |
| 7 | `July` | `Jul` | `7` |
| 8 | `August` | `Aug` | `8` |
| 9 | `September` | `Sep` | `9` |
| 10 | `October` | `Oct` | `10` |
| 11 | `November` | `Nov` | `11` |
| 12 | `December` | `Dec` | `12` |

错误：无。对任何 `IsoWeek` 和 `date`，`date_range` 和 `short_date` 都不会抛异常。

- 副作用：无
- 性能指标：无

示例：

```python
from datetime import date

from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek, short_date

november = BiText("16 to 22 November 2026", "2026年11月16日至22日")
assert IsoWeek(2026, 47).date_range == november
december = BiText("30 November to 6 December 2026", "2026年11月30日至12月6日")
assert IsoWeek(2026, 49).date_range == december
new_year = BiText("28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日")
assert IsoWeek(2026, 53).date_range == new_year
assert short_date(date(2026, 11, 16)) == BiText("Mon 16 Nov", "周一 11月16日")
assert short_date(date(2026, 11, 22)) == BiText("Sun 22 Nov", "周日 11月22日")
assert short_date(date(2026, 12, 1)) == BiText("Tue 1 Dec", "周二 12月1日")
```

### 2.3 `Day`

- 模块：menus
- 功能：一周的七天，从周一到周日，带有两种语言的名称（架构 3，ADR-0004）。每个成员的值就是菜单文件里这一天的表的键。

签名：

```python
class Day(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @property
    def label(self) -> BiText: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `value` | `str` | 文件里的键，供 `Day(value)` 使用。 | 下表里的一个值，写法与表里完全相同。 |

- 返回值：一个 `Day`。
  - `list(Day)` 按一周的顺序给出各个成员，从周一到周日。`IsoWeek.dates[i]` 是 `list(Day)[i]` 那一天的日期。
  - `label` 给出这一天的名称，用在“Monday dinner”和“周一晚餐”这样的位置里。下表列出它，以及 `short_date` 使用的英文简称（2.2）。在中文里，`short_date` 使用 `label`。
  - `Day(value)` 给出值为 `value` 的成员；`value in Day` 判断一个词是不是星期，不会抛异常。
  - `Day` 是 `str`，所以 `sorted` 按词排序，这不是一周的顺序。要按一周的顺序排，请用 `key=list(Day).index`，和 `Meal` 一样（F05 设计 2.1）。

| 成员 | 值 | `label`，英文 | `label`，中文 | `short_date` 里的简称，英文 |
| --- | --- | --- | --- | --- |
| `MONDAY` | `monday` | `Monday` | `周一` | `Mon` |
| `TUESDAY` | `tuesday` | `Tuesday` | `周二` | `Tue` |
| `WEDNESDAY` | `wednesday` | `Wednesday` | `周三` | `Wed` |
| `THURSDAY` | `thursday` | `Thursday` | `周四` | `Thu` |
| `FRIDAY` | `friday` | `Friday` | `周五` | `Fri` |
| `SATURDAY` | `saturday` | `Saturday` | `周六` | `Sat` |
| `SUNDAY` | `sunday` | `Sunday` | `周日` | `Sun` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `Day(value)` 收到的词不是任何成员的值，比如 `funday` 或 `Monday`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import BiText
from recipe_menu.menus import Day

assert len(Day) == 7
assert list(Day)[0] is Day.MONDAY
assert list(Day)[-1] is Day.SUNDAY
assert Day("sunday") is Day.SUNDAY
assert "friday" in Day
assert "Friday" not in Day
assert Day.MONDAY.label == BiText("Monday", "周一")
assert Day.SUNDAY.label == BiText("Sunday", "周日")
assert sorted(Day)[0] is Day.FRIDAY

Day("funday")  # raises ValueError
Day("Monday")  # raises ValueError
```

### 2.4 `Dish`

- 模块：menus
- 功能：一餐里的一道菜：它的菜谱 ID 和份数（[架构 5.2](../../architecture.zh-CN.md#52-值)）。文件没写份数时，`read_week_menu` 填上设置里的份数，所以后面的模块处理一道菜时从不需要设置。

签名：

```python
@dataclass(frozen=True, slots=True)
class Dish:
    recipe_id: str
    servings: int
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `recipe_id` | `str` | 菜谱的 ID，比如 `cola-wings`。 | `is_recipe_id(recipe_id)` 为真（F04 设计 2.4）。`read_week_menu` 只给出 `list_recipe_ids` 给出过的 ID。 |
| `servings` | `int` | 这道菜的份数。 | 从 `MIN_SERVINGS` 到 `MAX_SERVINGS`，即 1 到 100（F05 设计 3.1）。不能是 `bool`。 |

- 返回值：一个 `Dish`。两个字段都相等时，两道菜相等。`Dish` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `recipe_id` 不是 `str`。 |
| `ValueError` | `is_recipe_id(recipe_id)` 为假。 |
| `TypeError` | `servings` 不是 `int`，或者是 `bool`。 |
| `ValueError` | `servings` 小于 1 或大于 100。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.menus import Dish

dish = Dish("cola-wings", 4)
assert dish.recipe_id == "cola-wings"
assert dish.servings == 4
assert dish == Dish("cola-wings", 4)

Dish(3, 4)  # raises TypeError
Dish("Cola-Wings", 4)  # raises ValueError
Dish("cola-wings", 0)  # raises ValueError
Dish("cola-wings", 101)  # raises ValueError
Dish("cola-wings", True)  # raises TypeError
```

### 2.5 `MealSlot`

- 模块：menus
- 功能：某一天的一餐，比如周一晚餐，以及按文件顺序排列的菜。本文把它叫作餐位。每餐可以有零道或多道菜（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，Q16）。F14 往没有菜的餐位里填菜。

签名：

```python
@dataclass(frozen=True, slots=True)
class MealSlot:
    day: Day
    meal: Meal
    dishes: tuple[Dish, ...] = ()
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `day` | `Day` | 这一天。 | 无 |
| `meal` | `Meal` | 这一餐（F05 设计 2.1）。 | 无 |
| `dishes` | 由 `Dish` 值组成的元组 | 各道菜，按文件里的顺序。 | 可以为空。同一道菜可以出现多次。 |

- 返回值：一个 `MealSlot`。三个字段都相等时，两个餐位相等。`MealSlot` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `day` 不是 `Day`，`meal` 不是 `Meal`，或者 `dishes` 不是元组或其中有一项不是 `Dish`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.menus import Day, Dish, MealSlot
from recipe_menu.settings import Meal

slot = MealSlot(Day.TUESDAY, Meal.DINNER, (Dish("mapo-tofu", 2), Dish("rice", 2)))
assert [dish.recipe_id for dish in slot.dishes] == ["mapo-tofu", "rice"]
assert MealSlot(Day.WEDNESDAY, Meal.LUNCH).dishes == ()

MealSlot(Day.TUESDAY, Meal.DINNER, [Dish("rice", 2)])  # raises TypeError
MealSlot("tuesday", Meal.DINNER)  # raises TypeError
```

### 2.6 `WeekMenu`

- 模块：menus
- 功能：一周的菜单：它的 ISO 周、每天的几餐，以及从周一到周日每天每一餐的一个餐位（[架构 5.2](../../architecture.zh-CN.md#52-值)）。它保存设置里列出的几餐。它只通过 ID 引用菜谱，命令自己读取它需要的菜谱（架构 5.3）。

签名：

```python
@dataclass(frozen=True, slots=True)
class WeekMenu:
    week: IsoWeek
    meals: tuple[Meal, ...]
    slots: tuple[MealSlot, ...]

    def dishes(self, day: Day, meal: Meal) -> tuple[Dish, ...]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `week` | `IsoWeek` | 这一周。 | 无 |
| `meals` | 由 `Meal` 值组成的元组 | 每天的几餐，来自设置。 | 1 到 3 餐，按 `Meal` 的顺序，每餐一次，和 `Settings.meals` 相同（F05 设计 2.2）。 |
| `slots` | 由 `MealSlot` 值组成的元组 | 这一周的各餐和它们的菜。 | 每天的每一个 `meals` 中的餐次正好一个餐位：从周一到周日，同一天里按 `meals` 的顺序。所以它有 `7 * len(meals)` 个餐位。 |
| `day` 和 `meal` | `Day` 和 `Meal` | `dishes` 给出的那个餐位。 | `meal` 在 `meals` 里。 |

- 返回值：一个 `WeekMenu`。
  - `dishes(day, meal)` 给出 `day` 和 `meal` 那个餐位的菜。F11 用它填写表格的每个格子。
  - 三个字段都相等时，两个菜单相等。`WeekMenu` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `week` 不是 `IsoWeek`，`meals` 不是由 `Meal` 值组成的元组，或者 `slots` 不是由 `MealSlot` 值组成的元组。 |
| `ValueError` | `meals` 为空，有重复的餐次，或者不是按 `Meal` 的顺序。 |
| `ValueError` | `slots` 没有按约束里的顺序，为每天的每一个 `meals` 中的餐次正好保存一个餐位。 |
| `ValueError` | `dishes` 收到的餐次不在 `meals` 里。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.menus import Day, Dish, IsoWeek, MealSlot, WeekMenu
from recipe_menu.settings import Meal

meals = (Meal.LUNCH, Meal.DINNER)
friday_dinner = (Dish("rice", 2),)
slots = tuple(
    MealSlot(day, meal, friday_dinner if day is Day.FRIDAY and meal is Meal.DINNER else ())
    for day in Day
    for meal in meals
)
menu = WeekMenu(IsoWeek(2026, 48), meals, slots)
assert len(menu.slots) == 14
assert menu.slots[0] == MealSlot(Day.MONDAY, Meal.LUNCH)
assert menu.dishes(Day.FRIDAY, Meal.DINNER) == friday_dinner
assert menu.dishes(Day.MONDAY, Meal.LUNCH) == ()
assert sum(1 for slot in menu.slots if slot.dishes) == 1

WeekMenu(IsoWeek(2026, 48), meals, slots[:-1])  # raises ValueError
WeekMenu(IsoWeek(2026, 48), (Meal.DINNER, Meal.LUNCH), slots)  # raises ValueError
menu.dishes(Day.MONDAY, Meal.BREAKFAST)  # raises ValueError
```

### 2.7 `week_from_argument` 和 `NOT_A_WEEK`

- 模块：menus
- 功能：把命令的参数 `WEEK` 换成 ISO 周：ISO 周、`this`、`next`，或者不写参数表示本周（[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 和 [4](../../requirements.zh-CN.md#4-功能点)）。F11 的 `menu new` 和 `menu show`、F13 的 `shop` 以及 F14 的 `menu suggest` 用 `Context.today` 调用它。对其他任何文字，它们的 `UsageError` 使用提示 `NOT_A_WEEK`。

签名：

```python
NOT_A_WEEK: Final[Message]


def week_from_argument(text: str | None, today: date) -> IsoWeek | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` 或 `None` | 你输入的参数值；命令行没写时为 `None`。 | 任意字符串。 |
| `today` | `date` | 今天的日期，来自 `Context.today`（F05 设计 2.4）。 | 无 |

- 返回值：按下表第一个适用的行给出的周，或者 `None`。

| `text` | 周 |
| --- | --- |
| `None` | `IsoWeek.of(today)`，也就是本周。 |
| `this` | `IsoWeek.of(today)`。 |
| `next` | `IsoWeek.of(today + timedelta(days=7))`，也就是本周的下一周。 |
| `IsoWeek.parse` 能读取的文字，比如 `2026-W47` | 那个周。 |
| 其他任何文字，比如 `2026-W99`、`This`、`2026-w47` 或空文字 | `None`。调用方抛出 `UsageError(NOT_A_WEEK, None, week=text)`。 |

`this` 和 `next` 必须完全一致，只用这些小写字母，就像 `IsoWeek.parse` 要求完全一致一样（选择 1）。帮助里关于周的说明列出的也是这三种写法（F05 设计 2.10）。`NOT_A_WEEK` 是下面这条提示。它的英文就是 F11 原型“A week without a menu”里的那一行。`{week}` 是你输入的文字。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NOT_A_WEEK` | `"{week}" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `“{week}”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。` |

这条提示已经说明要写什么，所以它的 `UsageError` 不带提示行，`cli` 只写出这条提示（ADR-0008，决定 A）。F11 原型和 v0.1-S15 都是这样显示的。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `IsoWeek.of` 收到 9999 年 12 月 27 日到 31 日之间的日期（2.1）。对 `None` 和 `this`，就是 `today` 在这几天里。对 `next`，就是 `today` 在 9999 年 12 月 20 日到 24 日之间。 |
| `OverflowError` | `text` 是 `next`，而 `today` 在 9999 年 12 月 25 日或之后，所以 `today + timedelta(days=7)` 超出了 `datetime.date` 的最后一天。 |

电脑的时钟不会给出这样的日期，所以只有错误的调用会遇到这些错误。

- 副作用：无
- 性能指标：无

示例：

```python
from datetime import date

from recipe_menu.app import UsageError
from recipe_menu.lang import Lang
from recipe_menu.menus import NOT_A_WEEK, IsoWeek, week_from_argument

today = date(2026, 11, 10)
assert week_from_argument(None, today) == IsoWeek(2026, 46)
assert week_from_argument("this", today) == IsoWeek(2026, 46)
assert week_from_argument("next", today) == IsoWeek(2026, 47)
assert week_from_argument("2026-W47", today) == IsoWeek(2026, 47)
assert week_from_argument("2026-W53", today) == IsoWeek(2026, 53)
assert week_from_argument("next", date(2026, 12, 30)) == IsoWeek(2027, 1)
assert week_from_argument("2026-W99", today) is None
assert week_from_argument("Next", today) is None
assert week_from_argument("", today) is None

error = UsageError(NOT_A_WEEK, None, week="2026-W99")
assert error.text(Lang.EN) == (
    '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
)
chinese = error.text(Lang.ZH)
assert chinese == "“2026-W99”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。"

week_from_argument("next", date(9999, 12, 20))  # raises ValueError
```

### 2.8 `list_menu_weeks`

- 模块：menus
- 功能：根据文件名列出 `menus/` 里有菜单文件的各个周，不读任何文件（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。F07 数出并读取这些周的菜单，F11、F13 和 F14 在其中查找一个周。

签名：

```python
def list_menu_weeks(folder: DataFolder) -> tuple[tuple[IsoWeek, ...], tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：一个二元组 `(weeks, problems)`。
  - 菜单文件是 `menus/` 里名称以小写的 `.toml` 结尾的条目，由 `list_toml_files` 给出（F04 设计 3.1）。其他条目，比如 `notes.txt` 或 `2026-W47.toml.bak`，都不是菜单文件，也不产生问题。`2026-W48.TOML` 这样 `.toml` 结尾里有大写字母的条目也不是菜单文件，`list_toml_files` 会为它给出一个错误。
  - `weeks` 保存每个菜单文件的周，只要这个文件去掉 `.toml` 后的名称能被 `IsoWeek.parse` 读取（2.1）。它们按时间顺序排列，这也是名称的顺序。
  - `problems` 先保存 `list_toml_files` 给出的问题，再按名称的顺序，为其他每个菜单文件保存一个错误 `NOT_A_WEEK_NAME`。这样的文件有 `2026-w47.toml`、`2026-W99.toml` 或 `plan.toml`。每个问题的文件就是它的条目，比如 Windows 上的 `menus\2026-w47.toml`，没有位置。有问题的名称不在 `weeks` 里，所以没有读取函数会读它的文件。
  - `menus/` 不存在、是一个文件或读不了时，`list_toml_files` 不给出名称，只给出一个问题，文件是 `menus`，没有位置。所以 `weeks` 为空，`problems` 只有这一个问题。

`list_menu_weeks` 的提示如下。它不显示名称，因为问题的文件在提示上面那一行已经写出了名称，和 F04 的 `NOT_A_RECIPE_ID` 一样。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NOT_A_WEEK_NAME` | `This file name is not an ISO week such as 2026-W47. Rename the file.` | `这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。` |

错误：无。`list_menu_weeks` 遇到坏数据从不抛异常。

- 副作用：通过 `list_toml_files` 列出 `menus/`。它不读任何文件，也不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。

```python
import shutil
from pathlib import Path

from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, list_menu_weeks

assert list_menu_weeks(folder) == ((IsoWeek(2026, 47),), ())

for name in ["2026-W53.toml", "2027-W01.toml", "2026-w48.toml", "2026-W99.toml", "2026-W49.TOML"]:
    (folder.menus / name).write_text("", encoding="utf-8")
(folder.menus / "notes.txt").write_text("Ideas\n", encoding="utf-8")
weeks, problems = list_menu_weeks(folder)
assert weeks == (IsoWeek(2026, 47), IsoWeek(2026, 53), IsoWeek(2027, 1))
names = [problem.file.name for problem in problems]
assert names == ["2026-W49.TOML", "2026-W99.toml", "2026-w48.toml"]
assert all(problem.place is None for problem in problems)
assert problems[2].text(Lang.ZH) == "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。"

shutil.rmtree(folder.menus)
weeks, problems = list_menu_weeks(folder)
assert weeks == ()
assert [problem.file for problem in problems] == [Path("menus")]
assert problems[0].text(Lang.EN) == "The folder is missing."
```

### 2.9 `read_week_menu`

- 模块：menus
- 功能：把一个周的菜单文件读成一个 `WeekMenu`，并报告每个问题及其位置（[需求 4](../../requirements.zh-CN.md#4-功能点)，F06）。`menu show`、`shop` 和 `menu suggest` 为它们的周调用它，`check` 为 `list_menu_weeks` 的每个周调用它。`check` 显示所有问题（F07）。其他每个命令遇到第一个错误就停下（架构 6）。

签名：

```python
def read_week_menu(
    folder: DataFolder,
    week: IsoWeek,
    settings: Settings | None,
    recipe_ids: frozenset[str],
) -> tuple[WeekMenu | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `week` | `IsoWeek` | 文件的周，比如 `2026-W47`。 | `list_menu_weeks` 给出的周。`read_week_menu` 读取 `folder.menu_file(str(week))`，不列出文件夹。在 Windows 上，名为 `2026-w47.toml` 的文件也会被当作 `2026-W47` 的文件打开。从严格比较名称的 `list_menu_weeks` 取得周，能让 Windows 和 Linux 的结果一致。 |
| `settings` | `Settings` 或 `None` | 每天的几餐，以及没写份数的菜所用的份数（F05 设计 2.2）。 | 设置读不了时为 `None`。这时 `read_week_menu` 只检查不依赖设置的部分（选择 3）。 |
| `recipe_ids` | 由 `str` 组成的 `frozenset` | 一道菜可以写的菜谱 ID。 | `list_recipe_ids` 给出的 ID（F04 设计 2.5）。 |

- 返回值：一个二元组 `(menu, problems)`。
  - `settings` 为 `None`，或者 `problems` 里有错误时，`menu` 为 `None`。否则它是一个 `WeekMenu`，周是 `week`，餐次是 `settings.meals`，并为每天的每一个这样的餐次保存一个餐位。餐位保存这一餐的列表里的菜，按文件里的顺序；文件没写这一天或这一餐时，餐位没有菜。每道菜的 ID 去掉了两端的空白，份数来自它的 `servings`，没写时用 `settings.servings`。设置里没有列出的 `breakfast = []` 这样的一餐不在菜单里。
  - 文件不存在、读不了、不是 UTF-8 或不是有效的 TOML 时，`problems` 只包含 `read_toml` 给出的那个问题（F03 设计 2.3）。否则它按顺序包含下面各项检查的问题。每个问题的文件都是 `menus/<week>.toml`，比如 Windows 上的 `menus\2026-W47.toml`。周来自 `list_menu_weeks` 时，只有在那之后被删除或改名的文件才会给出 `FILE_MISSING`。每个问题都是错误。

文件的格式就是 `docs/prototypes/example-data.md` 里的格式。这里省略了周二到周六：

```toml
# 2026-W47: 16 to 22 November 2026
week = "2026-W47"

[monday]
lunch = []
dinner = ["tomato-egg", "choy-sum", "rice"]

[sunday]
lunch = []
dinner = [
  { recipe = "cola-wings", servings = 4 },
  { recipe = "choy-sum", servings = 4 },
  { recipe = "rice", servings = 4 },
]
```

启用的餐次就是 `settings.meals`；`settings` 为 `None` 时，是 `Meal` 的全部三种餐次。文件里的每张表有这些键，按这个顺序：

| 表 | 键 | 必须写的 |
| --- | --- | --- |
| 文件顶层 | `week`，然后是各天 `monday`、`tuesday`、`wednesday`、`thursday`、`friday`、`saturday` 和 `sunday`，也就是 `Day` 的各个值 | `week`。文件没写的一天没有菜。 |
| 一天 | 启用的餐次，用 `Meal` 的值作键。每个都是一个菜的列表。 | 无。这一天没写的启用餐次没有菜。 |
| 放在花括号里的一道菜 | `recipe` 和 `servings` | `recipe`。没写 `servings` 时，这道菜使用 `settings.servings`。 |

一餐的列表里的每一项都是一道菜：放在引号里的菜谱 ID，或者放在花括号里的表。问题的位置如下。N 从 1 开始数一餐里的菜，跳过的项也算在内，所以它就是你在文件里数出的序号。

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| `week` | `week` | `周次` |
| 一天 | 这一天的 `label`，比如 `Monday` | `周一` |
| 一天里值为某个 `Meal` 的键 | 这一天的 `label` 和这一餐的 `label`，比如 `Monday dinner` | `周一晚餐` |
| 一天里的其他键 | 这一天的 `label` 和文件里写的键，比如 `Friday supper` | `周五 supper` |
| 一餐里的第 N 道菜 | 这一天的这一餐和 N，比如 `Sunday dinner, dish 1` | `周日晚餐，菜品 1` |

下文的“这一天的这一餐”指第三行，“这一天的键”指第三行或第四行。

`read_week_menu` 做以下检查。如果某个部分的值类型不对，比如一天不是表，那么这项检查就是这个部分唯一的检查。其他部分照样检查，所以运行一次就能报告文件的所有问题。一餐和它的菜的检查适用于一天里写的是启用餐次的每个键。得到 `UNKNOWN_MEAL` 或 `UNKNOWN_KEY` 的键不再做进一步检查。

| 部分 | 检查 | 问题 | 位置 | 类型 |
| --- | --- | --- | --- | --- |
| `week` | 没写这个键。 | `MISSING_KEY` | 无 | 错误 |
| `week` | 值不是文字。 | `NOT_A_TEXT` | `week` | 错误 |
| `week` | 文字为空或只有空白字符。 | `EMPTY_TEXT` | `week` | 错误 |
| `week` | 去掉两端的空白后，`IsoWeek.parse` 对这段文字给出 `None`，比如 `2026-w47` 或 `next`。 | `WEEK_NOT_ISO` | `week` | 错误 |
| `week` | 文字写的周与文件名的周不同，比如 `2026-W47.toml` 里写了 `2026-W48`。 | `WEEK_NOT_FILE_NAME` | `week` | 错误 |
| 一天 | 值不是表，比如 `monday = []`。 | `NOT_A_DAY_TABLE` | 这一天 | 错误 |
| 一天里的键 | `settings` 不为 `None`，而且这个键不是 `settings.meals` 中的任何一餐，比如 `supper`、`Dinner`，或者设置只列出午餐和晚餐时的 `breakfast`。值为某个 `Meal` 且保存空列表 `[]` 的键不产生问题。 | `UNKNOWN_MEAL` | 这一天的键 | 错误 |
| 一天里的键 | `settings` 为 `None`，而且这个键不是任何 `Meal` 的值，比如 `supper` 或 `Dinner`。 | `UNKNOWN_KEY` | 这一天的键 | 错误 |
| 一餐 | 值不是列表。 | `NOT_A_LIST` | 这一天的这一餐 | 错误 |
| 一道菜 | 这一项既不是文字也不是表。 | `NOT_A_DISH` | 第 N 道菜 | 错误 |
| 一道菜 | 这一项是文字，但为空或只有空白字符。 | `EMPTY_ITEM` | 第 N 道菜 | 错误 |
| 一道菜 | 这一项是表，而 `recipe` 没写、不是文字，或为空或只有空白字符。 | `MISSING_KEY`、`NOT_A_TEXT` 或 `EMPTY_TEXT` | 第 N 道菜 | 错误 |
| 一道菜 | 菜谱 ID 不符合 `is_recipe_id` 的规则，比如 `Rice`，或者 `recipe_ids` 里没有它。ID 就是去掉两端空白后的文字，或 `recipe` 的文字。 | `UNKNOWN_RECIPE` | 这一天的这一餐 | 错误 |
| 一道菜 | 这一项是带有 `servings` 的表，而这个值不符合 `read_servings` 的规则（F05 设计 3.1）。 | `SERVINGS_NOT_A_NUMBER`、`SERVINGS_TOO_FEW` 或 `SERVINGS_TOO_MANY` | 第 N 道菜 | 错误 |
| 一道菜 | 这一项是表，带有 `recipe` 和 `servings` 以外的键。 | `UNKNOWN_KEY` | 第 N 道菜 | 错误 |
| 文件顶层 | 键表里八个键以外的键。 | `UNKNOWN_KEY` | 无 | 错误 |

`UNKNOWN_RECIPE` 的位置是这一天的这一餐，和 F07 原型一样，因为提示里已经写出了菜谱。一道菜的其他问题都在第 N 道菜。

问题按这个顺序排列：

1. `week` 的问题。
2. 各天，按周一到周日的顺序。一天给出它自己的问题，或者按文件里的顺序给出它的各个键的问题。一餐给出它的列表本身的问题，或者按顺序给出每道菜的问题。一道菜先给出它自己的问题或它的菜谱 ID 的问题，然后是 `servings` 的问题，最后按文件里的顺序给出它的未知键。
3. 文件顶层的其他键，按文件里的顺序。

`read_week_menu` 用 `datafile` 的提示报告文件结构的问题（F03 设计 2.10），用 `read_servings` 的提示报告份数的问题。它按键的个数选择 `UNKNOWN_KEY` 的形式：文件顶层是八个，`settings` 为 `None` 时的一天是三个，一道菜是两个。下面是 `menus` 的提示。占位符是放在花括号里的名称，比如 `{week}`。`NOT_A_DISH` 里 `{ ... }` 的花括号是文字的一部分，所以它的模板把每个花括号写两次（F02 设计 2.2）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `WEEK` | `week` | `周次` |
| `DAY_MEAL` | `{day} {meal}` | `{day}{meal}` |
| `DAY_KEY` | `{day} {key}` | `{day} {key}` |
| `DISH_N` | `{place}, dish {number}` | `{place}，菜品 {number}` |
| `WEEK_NOT_ISO` | `"week" must be an ISO week such as 2026-W47, not "{week}".` | `“week”必须是 2026-W47 这样的 ISO 周，不能是“{week}”。` |
| `WEEK_NOT_FILE_NAME` | `The file name says {name}, but the file says {week}.` | `文件名是 {name}，但文件里写的是 {week}。` |
| `NOT_A_DAY_TABLE` | `"{key}" must be a table. Write the line [{key}], and below it a list of dishes for each meal, such as dinner = ["tomato-egg"].` | `“{key}”必须是表。请写一行 [{key}]，在它下面为每一餐写一个菜的列表，比如 dinner = ["tomato-egg"]。` |
| `UNKNOWN_MEAL` | `Unknown meal "{meal}". The settings name {meals}.` | `未知餐次“{meal}”。设置里的餐次：{meals}。` |
| `NOT_A_DISH` | `A dish must be a recipe ID in quotation marks, such as "tomato-egg", or a table in braces, such as { recipe = "tomato-egg", servings = 4 }.` | `一道菜必须是放在引号里的菜谱 ID，比如 "tomato-egg"，或者是放在花括号里的表，比如 { recipe = "tomato-egg", servings = 4 }。` |
| `UNKNOWN_RECIPE` | `Unknown recipe "{recipe}".` | `未知菜谱“{recipe}”。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `day` | 这一天的 `label`（2.3），用在 `DAY_MEAL` 和 `DAY_KEY` 里。 |
| `meal` | 在 `DAY_MEAL` 里是这一餐的 `label`（F05 设计 2.1）。在 `UNKNOWN_MEAL` 里是文件里写的键。 |
| `place` | 这一天的这一餐，来自 `DAY_MEAL`。 |
| `number` | N，也就是这道菜的序号。 |
| `key` | 文件里写的键。在 `DAY_KEY` 里是一天里的其他键。在 `MISSING_KEY`、`NOT_A_TEXT` 和 `EMPTY_TEXT` 里是 `week` 或 `recipe`。在 `NOT_A_DAY_TABLE` 里是这一天。在 `NOT_A_LIST` 里是这一餐。在 `UNKNOWN_KEY` 里是那个未知的键。 |
| `keys` | 按键表的顺序，对这张表可以有的键做 `and_list`。文件顶层是“week, monday, tuesday, wednesday, thursday, friday, saturday, and sunday”。`settings` 为 `None` 时的一天是“breakfast, lunch, and dinner”。一道菜是“recipe and servings”和“recipe 和 servings”。 |
| `week` | 去掉两端空白后的 `week` 文字。在 `WEEK_NOT_FILE_NAME` 里，它是一个 ISO 周。 |
| `name` | 参数 `week` 的 `str(week)`，也就是文件名的周。 |
| `meals` | 按顺序对 `settings.meals` 的各个值做 `and_list`，比如“lunch and dinner”和“lunch 和 dinner”。中文也列出英文词，因为文件里要写这些词，和 F05 的 `UNKNOWN_MEAL` 一样。 |
| `recipe` | 去掉两端空白后的菜谱 ID。 |
| `servings` | `servings` 的值，由 `read_servings` 给出（F05 设计 3.1）。 |

F07 原型以及场景 v0.1-S05 和 v0.1-S07 展示了其中四个问题。`menus\2026-W47.toml, Monday dinner` 得到 `Unknown recipe "tomato-eggs".`。按 v0.1-S07 的错误，`menus\2026-W47.toml, week` 得到 `The file name says 2026-W47, but the file says 2026-W48.`，`menus\2026-W47.toml, Friday supper` 得到 `Unknown meal "supper". The settings name lunch and dinner.`，`menus\2026-W47.toml, Sunday dinner, dish 1` 得到 `Servings must be a whole number of 1 or more, not 0.`。

错误：无。`read_week_menu` 遇到坏数据从不抛异常。`str(week)` 总是有效的名称，所以 `DataFolder.menu_file` 从不抛异常。

- 副作用：通过 `read_toml` 读取 `menus/<week>.toml`。它不列出任何文件夹，也不写任何东西。
- 性能指标：无

示例：

在这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。第三次读取让周一晚餐写成 `tomato-eggs`，和 F07 原型一样。第四次读取从示例文件重新开始，做出 v0.1-S07 里菜单的三处错误。然后 `lines` 的文件几乎每个部分都有一处错误。

```python
from pathlib import Path

from recipe_menu.datafile import Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, Settings, read_settings

settings, _ = read_settings(folder)
ids, _ = list_recipe_ids(folder)
recipe_ids = frozenset(ids)
week = IsoWeek(2026, 47)
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert problems == ()
assert menu is not None
assert menu.week == week
assert menu.meals == (Meal.LUNCH, Meal.DINNER)
assert len(menu.slots) == 14
monday = (Dish("tomato-egg", 2), Dish("choy-sum", 2), Dish("rice", 2))
assert menu.dishes(Day.MONDAY, Meal.DINNER) == monday
assert menu.dishes(Day.SUNDAY, Meal.DINNER)[0] == Dish("cola-wings", 4)
assert sum(1 for slot in menu.slots if slot.dishes) == 4
assert sum(len(slot.dishes) for slot in menu.slots) == 9

every_meal = Settings(Lang.EN, tuple(Meal), 3)
menu, problems = read_week_menu(folder, week, every_meal, recipe_ids)
assert problems == ()
assert menu is not None
assert menu.dishes(Day.MONDAY, Meal.BREAKFAST) == ()
assert menu.dishes(Day.MONDAY, Meal.DINNER)[0] == Dish("tomato-egg", 3)
assert read_week_menu(folder, week, None, recipe_ids) == (None, ())

file = folder.menu_file("2026-W47")
text = file.read_text(encoding="utf-8")
file.write_text(text.replace('"tomato-egg"', '"tomato-eggs"'), encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert [problem.file for problem in problems] == [Path("menus", "2026-W47.toml")]
assert problems[0].place == BiText("Monday dinner", "周一晚餐")
assert problems[0].text(Lang.EN) == 'Unknown recipe "tomato-eggs".'
assert problems[0].text(Lang.ZH) == "未知菜谱“tomato-eggs”。"

text = text.replace('week = "2026-W47"', 'week = "2026-W48"')
text = text.replace("[friday]\n", "[friday]\nsupper = []\n")
text = text.replace('"cola-wings", servings = 4', '"cola-wings", servings = 0')
file.write_text(text, encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert [problem.place for problem in problems] == [
    BiText("week", "周次"),
    BiText("Friday supper", "周五 supper"),
    BiText("Sunday dinner, dish 1", "周日晚餐，菜品 1"),
]
assert problems[0].text(Lang.EN) == "The file name says 2026-W47, but the file says 2026-W48."
assert problems[1].text(Lang.EN) == 'Unknown meal "supper". The settings name lunch and dinner.'
assert problems[1].text(Lang.ZH) == "未知餐次“supper”。设置里的餐次：lunch 和 dinner。"
assert problems[2].text(Lang.EN) == "Servings must be a whole number of 1 or more, not 0."
menu, problems = read_week_menu(folder, week, None, recipe_ids)
assert len(problems) == 3
english = problems[1].text(Lang.EN)
assert english == 'Unknown key "supper". The keys are breakfast, lunch, and dinner.'

lines = [
    "week = 2026",
    "wednesday = []",
    "[monday]",
    'lunch = "rice"',
    'dinner = ["Rice", 3, " ", { recipe = "rice", servings = 0x' + "f" * 5000 + ", note = 1 }]",
    "breakfast = []",
    "[tuesday]",
    'breakfast = ["rice"]',
    "[funday]",
]
file.write_text("\n".join(lines) + "\n", encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert all(problem.severity is Severity.ERROR for problem in problems)
assert [problem.place for problem in problems] == [
    BiText("week", "周次"),
    BiText("Monday lunch", "周一午餐"),
    BiText("Monday dinner", "周一晚餐"),
    BiText("Monday dinner, dish 2", "周一晚餐，菜品 2"),
    BiText("Monday dinner, dish 3", "周一晚餐，菜品 3"),
    BiText("Monday dinner, dish 4", "周一晚餐，菜品 4"),
    BiText("Monday dinner, dish 4", "周一晚餐，菜品 4"),
    BiText("Tuesday breakfast", "周二早餐"),
    BiText("Wednesday", "周三"),
    None,
]
assert problems[0].text(Lang.EN) == '"week" must be a text in quotation marks.'
assert problems[1].text(Lang.EN) == '"lunch" must be a list in square brackets, [ ... ].'
assert problems[2].text(Lang.EN) == 'Unknown recipe "Rice".'
assert problems[3].text(Lang.EN).startswith("A dish must be a recipe ID in quotation marks,")
assert problems[4].text(Lang.EN) == "This item is empty."
assert problems[5].text(Lang.EN) == "Servings must be a whole number from 1 to 100, such as 2."
assert problems[6].text(Lang.EN) == 'Unknown key "note". The keys are recipe and servings.'
assert problems[7].text(Lang.EN).startswith('Unknown meal "breakfast". The settings name')
assert problems[8].text(Lang.EN).startswith('"wednesday" must be a table.')
assert problems[9].text(Lang.EN).startswith('Unknown key "funday". The keys are week, monday,')
_, problems = read_week_menu(folder, week, None, recipe_ids)
assert len(problems) == 9

file.write_text('week = " 2026-W47 "\n', encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert problems == ()
assert menu is not None
assert all(slot.dishes == () for slot in menu.slots)
file.write_text('week = "2026-w47"\n', encoding="utf-8")
_, problems = read_week_menu(folder, week, settings, recipe_ids)
english = problems[0].text(Lang.EN)
assert english == '"week" must be an ISO week such as 2026-W47, not "2026-w47".'
file.write_text("[monday]\ndinner = []\n", encoding="utf-8")
_, problems = read_week_menu(folder, week, settings, recipe_ids)
assert [problem.place for problem in problems] == [None]
assert problems[0].text(Lang.EN) == 'The key "week" is missing.'
menu, problems = read_week_menu(folder, IsoWeek(2026, 48), settings, recipe_ids)
assert menu is None
assert [problem.text(Lang.EN) for problem in problems] == ["The file is missing."]
```

## 3. 对已有接口的修改

无。F01 到 F05 实现的接口都没有修改。每个导出的名称都保持它的签名和行为，F01 到 F05 的测试不改也能通过。F06 新增模块 `menus`，不修改其他模块的任何文件。

F06 按各自设计的规定使用下面这些接口，不修改其中任何一个：

- F02 的 `BiText`、`Lang`、`Message` 和 `and_list`。
- F03 的 `DataFolder`、`Problem`、`read_toml`，以及 F03 设计 2.10 的提示 `EMPTY_ITEM`、`EMPTY_TEXT`、`MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TEXT` 和 `UNKNOWN_KEY`。
- F04 加入 `datafile` 的 `list_toml_files`、`Report`、`read_text` 和 `report_unknown_keys`（F04 设计 3.1 和 3.2），以及 `recipes` 里的 `is_recipe_id`（F04 设计 2.4）。
- F05 在 `settings` 里的 `Meal` 和 `Settings`（F05 设计 2.1 和 2.2），以及加入 `datafile` 的 `read_servings`、`MIN_SERVINGS` 和 `MAX_SERVINGS`（F05 设计 3.1）。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `menus` 是架构 3 里的领域层模块。它只引用 `lang`、`text`、`datafile`、`settings` 和 `recipes`，也就是它那一行允许的五个模块；它从 `recipes` 只用 `is_recipe_id`，并且只通过 `list_toml_files` 和 `read_toml` 访问磁盘（架构 4 和 8）。它负责它那一行列出的内容：ISO 周、本周和下周（`IsoWeek` 和 `week_from_argument`），两种语言的日期和星期名称（`date_range`、`short_date` 和 `Day.label`），以及读取周菜单文件并报告它们的问题。`IsoWeek`、`Dish` 和 `WeekMenu` 持有架构 5.2 的字段。文件没写份数时，`Dish` 得到设置里的份数；`WeekMenu` 保存设置里的餐次，只通过 ID 引用菜谱（5.3）。`Day` 和 `MealSlot` 是辅助值，就像 `Severity`、`Steps` 和 `FolderUse` 一样。文件的格式就是 5.1 和 `example-data.md` 的格式，键是小写的英文词（架构 8）。`read_week_menu` 接收 `Settings` 或 `None`，就像 `read_recipe` 接收 `Catalog` 或 `None`；架构 8 也允许由 ID 组成的 `frozenset` 跨模块传递。`NOT_A_WEEK` 应当放在 `menus` 里（选择 8）。它的文字说明的是 `week_from_argument` 能读取的写法；`app` 在更高的一层，所以 `menus` 不能抛出 `UsageError`；而 `shop` 不能引用 `menu`。`datafile` 和 `text` 已经导出了提示。选择 5 符合需求 3：每个 `WeekMenu` 都有七天和设置里的几餐，只有文件可以不写没有菜的部分。注 1，不阻塞：架构 8 规定用户看到的每段文字都是 `Message`，而 2.2 只把四个模板列为提示。星期名称、英文的星期简称和月份名称也是这样的文字，所以它们也放在 `menus/messages.py` 里，就像 `Meal` 的名称放在 `settings/messages.py` 里一样。注 2，不阻塞：第 2 节关于性能的规则说“有 63 道菜的周”，但需求 7.1 没有给出菜的数量。这里可以写“一个周菜单”。 |
| 遵守错误处理和命名约定 | Pass | 读取函数返回它们的问题，遇到坏数据从不抛异常（架构 6）。异常只来自错误的调用：2.1 以及 2.3 到 2.6 的构造函数、`WeekMenu.dishes`，以及在 `datetime.date` 最后一天附近的 `week_from_argument`。`read_week_menu` 只用 `str(week)` 拼出路径，而 `DataFolder.menu_file` 总是接受它，所以菜永远不会进入路径（F03 设计 2.1）。每个问题都写出相对于数据文件夹的 `menus/<week>.toml`，并以 `Monday dinner` 这样的字段作为位置，和 F07 原型一样。语法错误只给出 `read_toml` 的那个问题和它的行号。命令行上写错的周是命令抛出的 `UsageError`，不带提示行，与 ADR-0008（决定 A）、F11 原型和 v0.1-S15 一致。没有提示会碰到 F02 的 4,300 位限制：份数经过有 15 位限制的 `read_servings`，`week` 的文字作为文字放进提示，N、日和年份都很小。每条提示都是 `menus/messages.py` 里带两种语言的 UPPER_SNAKE 常量，名称遵守 PEP 8（架构 8）。每个占位符的值都是 `str`、`int` 或 `BiText`。设计传入的是 `Day.label`、`Meal.label`，以及对每个餐次的值做的 `and_list`，从不传入枚举成员，因为 `Message.render` 和 `and_list` 会拒绝它。架构师权衡了接口设计师提出的三点。(a) 选择 5 成立。没写的一天或一餐没有菜，所以你在加上一餐之前写的菜单依然正确。设置里没有列出的一餐写成 `breakfast = []` 时不产生问题，所以你在去掉一餐之前写的菜单也依然正确。设置里没有列出、却写了菜的一餐仍然是错误，因为 `menu show` 和 `shop` 会漏掉它的菜。(b) 没有设置时使用 `UNKNOWN_KEY` 是可以接受的。它只在 `settings.toml` 有错误时出现，而 F07 也会报告那个错误；它的文字也是对的。复制 `settings` 里 `UNKNOWN_MEAL` 的文字能保留“餐次”这个词，代价是多一条提示。(c) 三个新的中文位置遵循项目的写法。`周次` 是一个键的名称，和 `餐次`、`份数` 一样。`周五 supper` 在中文和拉丁文字之间加一个空格，和 `食材 3` 一样。`周日晚餐，菜品 1` 对应 `Sunday dinner, dish 1`。注 3，可选：`周日晚餐第 1 道菜` 会用上原型里的“道菜”，比如 `9 道菜` 和 `每道菜`，也能避免在文件后面的那个“，”之后再出现一个“，”。Troy 批准这份设计时会看到这些文字（R18，`troy_approves_first = 16`）。给开发工程师：没有设置时，一天里的每个未知键有它自己的位置，所以读取函数通过 `Report.add` 加入 `UNKNOWN_KEY.pick(3)`，因为 `report_unknown_keys` 给所有键同一个位置。 |
| 不和已有接口重复 | Pass | `menus` 是新模块，不重写任何已有的东西。它用 `list_toml_files` 列出 `menus/` 并传递它的问题，和 `list_recipe_ids` 一样，所以 `TOML_ENDING_NOT_SMALL` 仍然只在 `datafile` 里（F04 设计 3.1）。它用 `read_toml` 读取文件，用 `read_text` 读取文字，用 `read_servings` 读取份数，所以 1 到 100 的范围和它的三条提示都只在一个地方（F05 设计选择 3）。它用 `is_recipe_id` 检查 ID，用 F03 设计 2.10 的提示报告文件结构的问题。它的新提示说出了共用提示说不出的内容。一天是一行 `[table]`，所以 `NOT_A_DAY_TABLE` 代替要求花括号的 `NOT_A_TABLE`。一道菜可以是文字或表，所以 `NOT_A_DISH` 代替 `ITEM_NOT_A_TEXT`。`UNKNOWN_MEAL` 与 `settings` 内部的一个名称相同，但用的是 F07 原型里不同的文字。架构 8 让每个模块保存自己的提示，F04 的 `UNKNOWN_INGREDIENT` 也是这样。对 `WeekMenu.meals` 的检查重复了 `settings` 内部的 `_check_meals`。它只有几行，复制一份比让已实现的模块新增导出更好。注 4，不阻塞：`There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` 这一行在 F11 和 F13 原型里完全相同，而 `shop` 不能引用 `menu`。这正是选择 8 为 `NOT_A_WEEK` 给出的理由。如果 `menus` 现在不导出这一行，F11 的设计就必须把它加进架构 3 只交给 F06 的 `menus`，否则 `menu` 和 `shop` 各自要保存一份。架构师建议 `menus` 现在就导出它，比如命名为带 `{week}` 的 `NO_MENU`，中文文字由 Troy 随这份设计一起批准。 |
| 只依赖排序在前面的功能 | Pass | F06 使用 F02 的 `lang` 和 `text`、F03 的 `datafile` 以及 F04 和 F05 加进它的内容、F04 的 `is_recipe_id`，以及 F05 的 `Meal`、`Settings` 和 `read_servings`。这四个功能都排在 F06 之前，并且在 main 上通过了测试。F04 和 F05 是 F06 那一行的软依赖，F02 和 F03 则通过 F04 和 F05 也在用的共用模块进来。第 2 节给 F07、F08 和 F11 到 F14 的安排只说明每个后续功能打算调用什么，其余的留给它自己的设计，所以不约束任何后续设计。这些接口只需要标准库，所以 R16 没有新的依赖要审查。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | 模块之间的每个假设都写在设计里。`read_week_menu` 只打开一个文件，不列出任何文件夹。所以调用方传入 `list_menu_weeks` 给出的周，它严格比较名称，让 Windows 和 Linux 的结果一致；调用方还传入 `list_recipe_ids` 给出的 ID（选择 1 和 4，以及 2.9 的参数）。F07 传入 `read_settings` 给出的设置，而不是 `context.settings`（选择 3）。F11 的 `menu new` 写出的文件，`read_week_menu` 读它时必须不给出任何问题，并且每个餐位都是空的。`NOT_A_WEEK`、`week_from_argument` 和 F05 帮助里关于周的说明列出同样的三种写法，2.7 写明了这一点，所以改动这些写法就要同时改动这三处。`list_toml_files` 对名称排序，所以 `weeks` 和问题都不依赖文件系统给出的顺序。注 5，不阻塞，给 F14：`WeekMenu` 不说明文件里有没有一个空餐位的键或它那一天的表（选择 5）。F14 往空的一餐里填菜，并保持文件的其余部分不变，所以它必须补上缺少的餐次键或日表。由 F14 的设计决定怎么做。 |
| 修改已实现的接口时走了变更流程 | Pass | 第 3 节写“无”是对的。这个 PR 只加入两个设计文件，`src/recipe_menu/menus/` 还不存在。F06 用到的每个名称都已经在分支上，签名与设计给出的相同：`recipe_menu.datafile` 里的 `list_toml_files`、`Report`、`read_text`、`report_unknown_keys`、`read_servings` 和文件结构的提示，`recipes` 里的 `is_recipe_id`，`settings` 里的 `Meal` 和 `Settings`，以及 `text` 里的 `Message`、`Plural` 和 `and_list`。所以 F01 到 F05 导出的名称都没有改变，它们的测试也不受影响。给后续阶段的几点：mock 定义所有常量，所以只检查常量的测试，比如只检查 `NOT_A_WEEK` 的文字或某个 `Day` 的名称，在 mock 上就会通过，违反 R09，第 2 节已经指出这一点。加上文档注释后，mock PR 在五个文件里修改的行数可能超过 R03 的 500 行，所以主会话要像 F04 和 F05 那样准备软限制的理由。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0008、F07 和 F11 原型，以及 v0.1-S05、v0.1-S07 和 v0.1-S15，检查了八项选择。选择 1 到 4、6 和 8 解决了任务说明里的七条审查意见。选择 5 和三个新的中文位置不需要修改需求、架构或原型。每个文件有 19 个代码块，每个都与另一种语言的版本相同，两个文件的标题和表格行逐行对应。18 个 `python` 代码块都能解析，用 ruff 0.17.4 和项目的设置运行 `ruff format --check`，结果是都已格式化。架构师在分支上 F01 到 F05 的代码之上，按第 2 节建了模型，在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 运行了 9 个示例，每个断言和全部 18 个 `# raises` 都成立。模型分别用示例设置、不用设置、用全部三餐和只用晚餐，读取了 3,000 个随机生成的菜单文件，没有抛出任何异常。这个 PR 没有修改代码，所以没有运行测试。注 1 到 5 都不阻塞。 | 批准。接口设计师可以在修订版里处理注 1 到 5，也可以不处理。Troy 连同新的中文文字一起批准这份设计（R18，`troy_approves_first = 16`）。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-12 | 初稿。 |
| 1.0 | 2026-11-12 | Troy 批准。 |
