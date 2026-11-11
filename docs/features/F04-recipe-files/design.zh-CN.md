---
troy-doc: "F04-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-11"
status: "Troy 已于 2026-11-11 批准"
mirror-of: "design.md"
---

# F04 菜谱文件：接口设计

## 1. 功能

- 编号和名称：F04 菜谱文件
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：F01、F02、F03

## 2. 接口

F04 构建领域层模块 `recipes`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.recipes` 导出 `Recipe`、`RecipeIngredient`、`Steps`、`is_recipe_id`、`list_recipe_ids`、`read_recipe` 和 `read_recipes`，它的 `__init__.py` 在 `__all__` 里列出这些名称。它的提示放在 `recipes/messages.py` 里，只在模块内部使用（架构 8）。模块背后的其他文件由开发工程师决定。F04 还给 `datafile` 加入 `list_toml_files`，并把 F03 检查文件结构的辅助函数从 `catalog` 移到 `datafile`（第 3 节）。菜谱文件的格式就是 `docs/prototypes/example-data.md` 里 `recipes/tomato-egg.toml` 的格式，F07 原型展示了 `check` 怎样报告它的问题。

下表把需求的每一部分对应到满足它的接口。

| 需求的说法 | F04 提供的接口 |
| --- | --- |
| 菜谱有一个 ID，即去掉扩展名的文件名，比如 `tomato-egg`（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。 | `is_recipe_id`（2.4）的 ID 规则，以及从文件名得出 ID 的 `list_recipe_ids`（2.5）。 |
| 把 `recipes/` 里的每个文件读成具有第 3 节各部分的菜谱：名称、份数、标签、带数量和备注的食材，以及步骤。 | `read_recipes`（2.7）和 `read_recipe`（2.6）。它们给出 `Recipe` 值（2.3），其中包含 `RecipeIngredient`（2.1）和 `Steps`（2.2）值。 |
| 没写单位的数量使用目录里这种食材的默认单位（需求 3，[架构 5.2](../../architecture.zh-CN.md#52-值)）。 | `read_recipe` 用 F01 的 `parse_quantity` 和这种食材的默认单位读取每个数量（2.6）。 |
| 报告每个问题及其文件和位置：语法错误、缺少某部分、未知的食材或标签、错误的数量或单位。 | `list_recipe_ids`、`read_recipe` 和 `read_recipes` 返回的 `Problem` 值，每个都带有它的文件和 2.6 的位置。 |
| 缺少一种语言是警告。 | 2.6 中名称、备注或步骤缺少一种语言时的警告。 |
| `recipes` 根据 `recipes/` 里的文件名列出菜谱 ID，不解析文件（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。 | `list_recipe_ids`（2.5），通过 `datafile` 的 `list_toml_files`（3.1）。 |

下面每个接口都遵守这些规则：

- `recipes` 在包内只引用 `lang`、`units`、`text`、`datafile` 和 `catalog`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。
- `recipes` 只通过 `datafile` 访问磁盘：它用 `list_toml_files` 列出 `recipes/`，用 `read_toml` 读取每个文件。没有接口写文件、打印、读环境变量或保存状态。
- 读取函数遇到坏数据从不抛异常（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。它检查整个文件，为每处错误记下一个 `Problem`，然后继续，所以运行一次 `check` 就能列出所有问题。下面各个“错误”表里的异常都来自错误的调用，也就是 bug。
- 每个值都是带 `slots=True` 的冻结 dataclass，其中的集合用元组（架构 8）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。所以文档注释用英文描述提示，从不引用它的中文模板。中文只出现在字符串字面量里。
- F04 的接口都没有性能指标。`check`、`list` 和 `search` 要在 PT01 的 1 秒内读完 1,000 个菜谱（[需求 7.1](../../requirements.zh-CN.md#71-性能指标)、架构 8、ADR-0002）。所以 `read_recipes` 只列一次 `recipes/`，每个文件只读一次，耗时与文件的大小成正比。在目录里的每次查找耗时与名称的长度成正比（F03 设计 2.6）。

读取一个菜谱和读取所有菜谱的区别在于列出什么（架构 8）：

- `list_recipe_ids` 不读任何文件。它从 `recipes/` 里的文件名得出 ID，所以 F06 能报告未知的菜谱 ID，F09 能区分未知的 ID 和出错的文件，都不用解析任何菜谱。
- `read_recipe` 只读一个文件，不列出 `recipes/`。`show`、`menu show` 和 `shop` 只为它们点到的菜谱调用它，所用的 ID 直接来自 `list_recipe_ids`，或者来自 F06 已经对照这些 ID 检查过的周菜单。
- `read_recipes` 用 `list_recipe_ids` 列一次 `recipes/`，再用 `read_recipe` 读取每个文件。`list`、`search` 和 `check` 调用它。

这份设计做了以下选择。每条后面括号里的小节给出它的规则。

1. 菜谱 ID 只能由小写字母 `a` 到 `z`、数字和 `-` 组成，以字母或数字开头，并且不是 Windows 的设备名（2.4）。Troy 决定保留这条规则，而不是另外允许汉字（第 4 节，发现 1）。在 Windows 和 Linux 上，文件名本身的要求更少：没有分隔符，没有 `:`，没有 U+0000，不是 `.` 或 `..`，没有 Windows 禁止的其他字符，末尾没有点号或空格，不是设备名，也没有只差在大小写上的两个名称（[架构 1](../../architecture.zh-CN.md#1-背景和约束)、F03 设计 2.1）。这条规则要求更多，原因有四个。原型和示例数据里的每个 ID 都是小写 ASCII。你要在命令行和菜单文件里输入 ID。这条规则让 ID 里没有形似字符和看不见的字符。ID 的字母只有一种大小写，所以没有两个 ID 只差在大小写上。ID 也不会像 `-x` 这样的选项。`红烧肉.toml` 这样的文件会得到一个错误，提示你给它改名（2.5）。
2. 菜谱做出的份数是 1 到 100（2.3 和 2.6）。Troy 决定保留这个范围，并决定设置、一道菜和 `show --servings` 也用它（第 4 节，发现 2）。这个范围让 F09 显示的、F12 用来做除数的每个份数都不大。提示只在文件里的数字不超过 15 位时才显示它，与 F01 对数量的限制相同，所以 `Problem` 永远碰不到 F02 的 4,300 位限制。
3. 在名称和备注里，空白的文字算作缺少这种语言。在步骤里，空列表算作缺少这种语言（2.6）。步骤里只能放列表，所以步骤里的文字，即使是 `""`，也是错误。缺少一种语言时，如果另一种语言可用，就给出警告。名称或步骤两种语言都没有时给出错误；备注两种语言都没有时就是没有备注。
4. 文件有错误时，`read_recipe` 不给出菜谱；否则给出菜谱和它的警告（2.6）。后续的读取函数不会对照菜谱检查任何东西，而 `check` 以外的每个命令遇到第一个错误就停下（架构 6），所以没有命令会用到有错误的菜谱。因此每个 `Recipe` 都是完整的。
5. 步骤是一个 `Steps` 值，有一个英文元组和一个中文元组，并像 `BiText` 那样回退到另一种语言（2.2），所以 F09 显示步骤的方式与显示名称相同。
6. 由 `datafile` 列出文件夹，并把文件夹不存在或读不了时的 `OSError` 变成 `Problem`，因为架构 6 把所有 `OSError` 都交给它处理（3.1）。缺少 `recipes/` 文件夹是错误，因为 `init` 会创建它。`datafile` 还报告 `.toml` 结尾里有大写字母的名称，比如 `rice.TOML`，因为 Windows 会把这个文件当作 `rice.toml` 打开，而 Linux 不会。
7. 检查文件结构的辅助函数从 `catalog` 移到 `datafile`，这样 `settings` 和 `menus` 也能使用它们（3.2）。

以下后续功能打算调用这些接口：

- F06 从 `list_recipe_ids` 得到 ID，把 ID 不在其中的菜报告为未知菜谱。它从不用菜单文件给出的 ID 拼出路径。
- F07 用 `read_catalog` 给出的目录调用 `read_recipes`；目录读不了时，传入 `None`。它把错误和警告分开打印。它可以用 `list_recipe_ids` 数出菜谱的个数。
- F08 写出 `recipes/tomato-egg.toml`，`read_recipe` 读它时不给出任何问题。
- F09 的 `list` 调用 `read_recipes`。它的 `show ID` 在 `list_recipe_ids` 的 ID 里查找这个 ID：不在其中时显示“未知 ID”的输出，在其中时调用 `read_recipe`。它用 `Steps.get` 显示步骤；`Steps.exact` 给出 `None` 时，加上关于另一种语言的说明。
- F10 把每个词与 `Recipe.name`、每个 `RecipeIngredient.ingredient` 的名称以及 `Recipe.tags` 的名称匹配。
- F12 按 `Fraction(dish.servings, recipe.servings)` 换算每个 `RecipeIngredient.quantity`，并按 `RecipeIngredient.ingredient` 合并各行。
- F14 按标签从 `read_recipes` 的结果里挑选菜谱。
- F15 用 `is_recipe_id` 检查你输入的 ID，并检查 `list_recipe_ids` 还没有列出它。
- F16 用 `read_recipe` 检查你编辑过的菜谱。
- F05、F06 和 F09 按 Troy 的决定（选择 2），把设置里的份数、一道菜的份数和 `show --servings` 限制在 1 到 100 的范围里，让所有份数都在同一个范围里。

### 2.1 `RecipeIngredient`

- 模块：recipes
- 功能：菜谱里的一行食材：目录里的食材、它的数量，以及可选的两种语言的备注（[架构 5.2](../../architecture.zh-CN.md#52-值)）。它引用的是目录里的同一个 `Ingredient` 对象，所以购物清单按同一对象合并食材。

签名：

```python
@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    ingredient: Ingredient
    quantity: Quantity
    note: BiText | None = None
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `ingredient` | `Ingredient` | 食材，比如 Tomato 和 番茄。 | 读取这个菜谱时所用目录里的一种食材。 |
| `quantity` | `Quantity` | 带单位的数量，或者“适量”（F01 设计 2.4）。没写单位的数量由 `read_recipe` 给上这种食材的默认单位。 | 无 |
| `note` | `BiText` 或 `None` | 备注，比如“cut into wedges”和“切块”。 | 这一行没有备注时为 `None`。有值的每种语言都不能只有空白字符。可以缺一种语言。 |

- 返回值：一个 `RecipeIngredient`。三个字段都相等时，两个值相等。`RecipeIngredient` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `note` 中有值的某种语言为空或只有空白字符。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.recipes import RecipeIngredient
from recipe_menu.units import TO_TASTE, Quantity, Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
wedges = BiText("cut into wedges", "切块")
line = RecipeIngredient(tomato, Quantity(Fraction(300), Unit.G), wedges)
assert line.ingredient is tomato
assert line == RecipeIngredient(tomato, Quantity(Fraction(300), Unit.G), wedges)
to_taste = RecipeIngredient(tomato, TO_TASTE)
assert to_taste.quantity.is_to_taste
assert to_taste.note is None
assert RecipeIngredient(tomato, TO_TASTE, BiText(zh="切块")).note == BiText(zh="切块")

RecipeIngredient(tomato, TO_TASTE, BiText("chopped", " "))  # raises ValueError
RecipeIngredient(tomato, TO_TASTE, BiText(en=""))  # raises ValueError
```

### 2.2 `Steps`

- 模块：recipes
- 功能：菜谱的步骤，每种语言一个文字元组，至少有一种语言（[架构 5.2](../../architecture.zh-CN.md#52-值)）。它像 `BiText` 一样给出所要的语言；所要的语言缺失时，给出另一种语言。所以对没有英文步骤的菜谱，`show` 显示中文步骤，和 F09 原型“A missing language”一样。

签名：

```python
@dataclass(frozen=True, slots=True)
class Steps:
    en: tuple[str, ...] | None = None
    zh: tuple[str, ...] | None = None

    def get(self, lang: Lang) -> tuple[str, ...]: ...

    def exact(self, lang: Lang) -> tuple[str, ...] | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `en` | `str` 元组，或 `None` | 英文步骤，按顺序排列。 | 菜谱没有英文步骤时为 `None`。否则有 1 个或更多步骤，每个都不能只有空白字符。 |
| `zh` | `str` 元组，或 `None` | 中文步骤，按顺序排列。 | 同 `en`。`en` 和 `zh` 不能都是 `None`。 |
| `lang` | `Lang` | `get` 或 `exact` 给出的语言。 | 无 |

- 返回值：一个 `Steps`。
  - `get(lang)` 给出 `lang` 的步骤；`lang` 的步骤为 `None` 时，给出另一种语言的步骤。它从不给出 `None`。
  - `exact(lang)` 给出 `lang` 的步骤；缺失时给出 `None`。F09 用它说明自己显示的是另一种语言的步骤。
  - `en` 和 `zh` 都相等时，两个 `Steps` 值相等。`Steps` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `en` 和 `zh` 都是 `None`。 |
| `ValueError` | `en` 或 `zh` 是空元组，或者含有为空或只有空白字符的步骤。 |
| `TypeError` | `en` 或 `zh` 既不是元组也不是 `None`（比如列表），或者含有不是 `str` 的步骤。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang
from recipe_menu.recipes import Steps

chinese = ("五花肉切块，冷水下锅焯水。", "小火炖 60 分钟，再大火收汁。")
steps = Steps(zh=chinese)
assert steps.get(Lang.EN) == chinese
assert steps.exact(Lang.EN) is None
assert steps.exact(Lang.ZH) == chinese
both = Steps(("Cut the tomatoes into wedges.",), ("番茄切块。",))
assert both.get(Lang.EN) == ("Cut the tomatoes into wedges.",)

Steps()  # raises ValueError
Steps(en=())  # raises ValueError
Steps(en=("Stir.", " "))  # raises ValueError
Steps(en=["Stir."])  # raises TypeError
```

### 2.3 `Recipe`

- 模块：recipes
- 功能：一个菜谱，包含[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 的各部分：ID、名称、份数、标签、食材和步骤（[架构 5.2](../../architecture.zh-CN.md#52-值)）。ID 是去掉 `.toml` 的文件名，ID 按写法精确比较。标签和食材都是目录里的值。测试和 F12 可以不用文件，直接在代码里构造菜谱。

签名：

```python
@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    name: BiText
    servings: int
    tags: tuple[Tag, ...]
    ingredients: tuple[RecipeIngredient, ...]
    steps: Steps
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `id` | `str` | ID，比如 `tomato-egg`。 | `is_recipe_id(id)` 为真（2.4）。 |
| `name` | `BiText` | 名称，比如“Tomato and egg stir-fry”和“番茄炒蛋”。 | 有值的每种语言都不能只有空白字符。可以缺一种语言。 |
| `servings` | `int` | 菜谱做出来的份数。 | 1 到 100。不能是 `bool`。 |
| `tags` | `Tag` 值的元组 | 标签，按文件里的顺序。 | 目录里的标签。`read_recipe` 给出的每个标签只出现一次。可以为空。 |
| `ingredients` | `RecipeIngredient` 值的元组 | 各行食材，按文件里的顺序。 | 可以为空。 |
| `steps` | `Steps` | 步骤。 | 无 |

- 返回值：一个 `Recipe`。六个字段都相等时，两个菜谱相等。`Recipe` 可以求哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `is_recipe_id(id)` 为假。 |
| `TypeError` | `servings` 不是 `int`，或者是 `bool`。 |
| `ValueError` | `servings` 小于 1 或大于 100。 |
| `ValueError` | `name` 中有值的某种语言为空或只有空白字符。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient, Tag
from recipe_menu.lang import BiText, Lang
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.units import Quantity, Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
choy_sum = Ingredient(BiText("Choy sum", "菜心"), produce)
quick = Tag(BiText("quick", "快手"))
name = BiText("Stir-fried choy sum", "清炒菜心")
lines = (RecipeIngredient(choy_sum, Quantity(Fraction(1), Unit.JIN)),)
steps = Steps(("Stir-fry the choy sum.",), ("炒菜心。",))
recipe = Recipe("choy-sum", name, 2, (quick,), lines, steps)
assert recipe.name.get(Lang.ZH) == "清炒菜心"
assert recipe.ingredients[0].ingredient is choy_sum
assert recipe == Recipe("choy-sum", name, 2, (quick,), lines, steps)

Recipe("Choy Sum", name, 2, (), lines, steps)  # raises ValueError
Recipe("choy-sum", name, 0, (), lines, steps)  # raises ValueError
Recipe("choy-sum", name, 101, (), lines, steps)  # raises ValueError
Recipe("choy-sum", name, True, (), lines, steps)  # raises TypeError
Recipe("choy-sum", BiText(zh=""), 2, (), lines, steps)  # raises ValueError
```

### 2.4 `is_recipe_id`

- 模块：recipes
- 功能：菜谱 ID 的规则（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。`recipes/` 里的文件只有在去掉 `.toml` 后的名称符合这条规则时，才是菜谱（2.5）。`read_recipe` 和 `Recipe` 在拼出路径或构造值之前检查它，所以 `DataFolder.recipe_file` 永远不会收到错误的名称（F03 设计 2.1）。F09 和 F15 可以用它检查命令行里或你回答的 ID。

签名：

```python
def is_recipe_id(text: str) -> bool: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 要检查的名称，比如去掉 `.toml` 的文件名，或者你输入的 ID。 | 任意字符串。 |

- 返回值：`text` 符合下面所有规则时为 `True`，否则为 `False`。这些规则在 Windows 和 Linux 上相同。
  1. 至少有一个字符。
  2. 第一个字符是 `a` 到 `z` 的小写字母或 `0` 到 `9` 的数字。
  3. 其他每个字符是 `a` 到 `z` 的小写字母、`0` 到 `9` 的数字或 `-`，也就是 U+002D HYPHEN-MINUS。
  4. 不是 Windows 的设备名：`con`、`prn`、`aux`、`nul`、`com0` 到 `com9`，或 `lpt0` 到 `lpt9`。

这条规则拒绝 `DataFolder.recipe_file` 拒绝的每个名称，还拒绝更多。下表给出原因。

| 被拒绝的名称举例 | 原因 |
| --- | --- |
| `""` | ID 要给一个文件命名。 |
| `.`、`..`、`rice.` 和 `nul.v2` | 不允许有点号。`.` 和 `..` 是文件夹。Windows 把以设备名和点号开头的名称（比如 `nul.v2.toml`）当作那个设备。 |
| `a/b`、`a\b`、`a:b`，以及 `a` 后面跟 U+0000 | 分隔符、盘符、NTFS 数据流或空字符都可能给出另一个文件的路径。Linux 允许 `recipes/a:b.toml` 这个文件。 |
| `a*b`、`a?b` 和 `a<b` | Windows 不允许文件名里有这些字符，也不允许下面列出的其他字符。 |
| `Tomato-Egg` | Windows 比较文件名时不分大小写，所以 `Tomato-Egg.toml` 和 `tomato-egg.toml` 在 Windows 上是一个文件，在 Linux 上是两个文件。 |
| `tomato egg` 和 `tomato_egg` | 只有 `-` 能连接单词。Windows 会去掉名称末尾的空格，带空格的 ID 在命令行里还要加引号。 |
| `-tomato` | 在命令行里，它看起来像一个选项。 |
| `番茄炒蛋`、`"tomato\u2010egg"`、`"\uff54omato-egg"` 和 `"tomato-egg\u200b"` | 只允许 ASCII。U+2010 HYPHEN、U+FF54 FULLWIDTH LATIN SMALL LETTER T 和 U+200B ZERO WIDTH SPACE 看起来像 `tomato-egg` 里的字符，或者根本看不见，所以两个 ID 可能看起来一样。Windows 比较 ASCII 以外的字母时也不分大小写。 |
| `con`、`nul`、`com1` 和 `lpt9` | Windows 把这些名称留给设备，所以在 Windows 上 `nul.toml` 不是一个文件。 |

Windows 不允许出现在文件名里的字符是 `<`、`>`、`:`、`"`、`/`、`\`、`|`、`?`、`*`，以及控制字符 U+0000 到 U+001F。规则 2 和 3 拒绝所有这些字符，也拒绝所有以点号或空格结尾的名称。

错误：无。`is_recipe_id` 从不抛异常。

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.recipes import is_recipe_id

assert is_recipe_id("tomato-egg")
assert is_recipe_id("2-minute-noodles")
assert is_recipe_id("com10")
assert is_recipe_id("console")
assert not is_recipe_id("")
assert not is_recipe_id("Tomato-Egg")
assert not is_recipe_id("tomato egg")
assert not is_recipe_id("tomato_egg")
assert not is_recipe_id("-tomato")
assert not is_recipe_id("rice.")
assert not is_recipe_id("a:b")
assert not is_recipe_id("番茄炒蛋")
assert not is_recipe_id("tomato\u2010egg")  # U+2010 HYPHEN
assert not is_recipe_id("nul")
assert not is_recipe_id("lpt0")
```

### 2.5 `list_recipe_ids`

- 模块：recipes
- 功能：根据 `recipes/` 里的文件名列出菜谱 ID，不读任何文件（[架构 8](../../architecture.zh-CN.md#8-命名和编码规范)）。F06 对照它们检查菜单里的菜，F09 的 `show` 在其中查找 ID，`read_recipes` 读取每个 ID 的文件。

签名：

```python
def list_recipe_ids(folder: DataFolder) -> tuple[tuple[str, ...], tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |

- 返回值：一对值 `(ids, problems)`。
  - 菜谱文件是 `recipes/` 里名称以 `.toml`（就是这几个小写字母）结尾的条目，由 `list_toml_files` 给出（3.1）。它的 ID 是去掉 `.toml` 的名称。其他条目，比如 `notes.txt` 或 `rice.toml.bak`，都不是菜谱文件，也不产生问题。`rice.TOML` 这样 `.toml` 结尾里有大写字母的条目也不是菜谱文件，`list_toml_files` 会为它给出一个错误。
  - `ids` 包含去掉 `.toml` 后符合 2.4 规则的每个菜谱文件的 ID，按码位排序，与 `sorted` 对字符串的排序相同。按这条规则，`-` 排在数字前面，数字排在字母前面。所以示例数据里 `choy-sum` 排第一，`tomato-egg` 排在 `tomato-egg-noodles` 前面，与 F09 原型里 `list` 的顺序相同。
  - `problems` 先包含 `list_toml_files` 给出的问题，再为去掉 `.toml` 后不符合 2.4 规则的每个菜谱文件包含一个错误，按名称的顺序排列：名称是规则 4 的 Windows 设备名时为 `RESERVED_RECIPE_ID`，其他名称为 `NOT_A_RECIPE_ID`。每个问题的文件就是它的条目，比如 Windows 上的 `recipes\pancakes.TOML` 或 `recipes\Rice Bowl.toml`，没有位置。有问题的名称不在 `ids` 里，所以没有读取函数会读它的文件。
  - `recipes/` 不存在、是一个文件或读不了时，`list_toml_files` 不给出名称，只给出一个问题，它的文件是 `recipes`，没有位置。所以 `ids` 为空，`problems` 只包含这个问题。

`list_recipe_ids` 的提示如下：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NOT_A_RECIPE_ID` | `This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Rename the file.` | `这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。请给文件改名。` |
| `RESERVED_RECIPE_ID` | `This file name cannot be a recipe ID, because Windows keeps it for a device. Rename the file.` | `这个文件名不能用作菜谱 ID，因为 Windows 把它留给设备使用。请给文件改名。` |

两个提示都不显示名称。问题的文件已经写出了名称，在 F07 原型的格式里就在提示的上一行。所以名称里有控制字符或任何字体都显示不出的字符时，提示也不会变。

错误：无。`list_recipe_ids` 遇到坏数据从不抛异常。

- 副作用：通过 `list_toml_files` 列出 `recipes/`。它不读任何文件，也不写任何东西。Windows 可能拒绝创建 `con.toml` 这样的文件，所以用真实文件测试 `RESERVED_RECIPE_ID` 的用例可能只能在 Linux 上运行。
- 性能指标：无

示例：

这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（[架构 10](../../architecture.zh-CN.md#10-测试配置)）。

```python
import shutil
from pathlib import Path

from recipe_menu.lang import Lang
from recipe_menu.recipes import list_recipe_ids

ids, problems = list_recipe_ids(folder)
assert ids == (
    "choy-sum",
    "cola-wings",
    "mapo-tofu",
    "red-braised-pork",
    "rice",
    "tomato-egg",
    "tomato-egg-noodles",
)
assert problems == ()

(folder.recipes / "notes.txt").write_text("Ideas\n", encoding="utf-8")
(folder.recipes / "pancakes.TOML").write_text("", encoding="utf-8")
(folder.recipes / "Rice Bowl.toml").write_text("", encoding="utf-8")
ids, problems = list_recipe_ids(folder)
assert len(ids) == 7
assert [problem.file for problem in problems] == [
    Path("recipes", "pancakes.TOML"),
    Path("recipes", "Rice Bowl.toml"),
]
assert all(problem.place is None for problem in problems)
assert problems[1].text(Lang.EN).startswith("This file name is not a recipe ID.")

shutil.rmtree(folder.recipes)
ids, problems = list_recipe_ids(folder)
assert ids == ()
assert [problem.file for problem in problems] == [Path("recipes")]
assert problems[0].text(Lang.EN) == "The folder is missing."
```

### 2.6 `read_recipe`

- 模块：recipes
- 功能：把一个菜谱文件读成一个 `Recipe`，并报告每个问题及其位置（[需求 4](../../requirements.zh-CN.md#4-功能点)，F04）。`show`、`menu show`、`shop` 和 F16 对一个菜谱的检查调用它，`read_recipes` 为每个 ID 调用它。`check` 显示所有问题（F07）。其他命令遇到第一个错误就停下（架构 6）。

签名：

```python
def read_recipe(
    folder: DataFolder,
    catalog: Catalog | None,
    recipe_id: str,
) -> tuple[Recipe | None, tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `catalog` | `Catalog` 或 `None` | 食材和标签的名称所来自的目录。 | 目录读不了时为 `None`。这时 `read_recipe` 只检查文件的形式。 |
| `recipe_id` | `str` | 菜谱的 ID，比如 `tomato-egg`。 | `is_recipe_id(recipe_id)` 为真。是 `list_recipe_ids` 直接给出的 ID，或者来自 F06 检查过的周菜单。`read_recipe` 读取 `folder.recipe_file(recipe_id)`，不列出文件夹。在 Windows 上，名为 `Tomato-Egg.toml` 的文件也能用 `tomato-egg` 打开，所以从精确比较名称的 `list_recipe_ids` 取得 ID，才能让 Windows 和 Linux 的结果相同。 |

- 返回值：一对值 `(recipe, problems)`。
  - `catalog` 为 `None`，或者 `problems` 里有错误时，`recipe` 为 `None`。否则它是一个 ID 为 `recipe_id` 的 `Recipe`，即使 `problems` 里有警告也是如此。其中的每段文字都去掉了两端的空白。每个标签只出现一次，按第一次写出它的项的顺序排列；各行食材按文件里的顺序排列。两种语言都没有的备注为 `None`；名称、备注或步骤里缺失的语言为 `None`。
  - 文件不存在、读不了、不是 UTF-8 或不是有效的 TOML 时，`problems` 只包含 `read_toml` 的那个问题（F03 设计 2.3）。否则它包含下面各项检查的问题，按检查的顺序排列。每个问题的文件都是 `recipes/<id>.toml`，比如 Windows 上的 `recipes\mapo-tofu.toml`。ID 来自 `list_recipe_ids` 时，只有在那之后被删除或改名的文件才会给出 `FILE_MISSING`。

文件的格式就是 `docs/prototypes/example-data.md` 的格式：

```toml
name = { zh = "番茄炒蛋", en = "Tomato and egg stir-fry" }
servings = 2
tags = ["快手", "家常"]

ingredients = [
  { item = "番茄", amount = "300 g", note = { zh = "切块", en = "cut into wedges" } },
  { item = "鸡蛋", amount = "3" },
]

[steps]
zh = ["番茄切块。鸡蛋加少许盐打散。"]
en = ["Cut the tomatoes into wedges. Beat the eggs with a pinch of salt."]
```

`[steps]` 写在最后，因为它后面的每个键都属于 `steps`。`item` 用任一语言写出目录里的一种食材，`tags` 的每一项用任一语言写出一个标签。`read_recipe` 用 `Catalog.find_ingredient` 和 `Catalog.find_tag` 查找它们（F03 设计 2.6）。`amount` 是 F01 的 `parse_quantity` 能读的数量，比如 `300 g`、`1.5 kg`、`3` 或 `适量`（F01 设计 2.7）。

文件里的每个表有这些键，按这个顺序：

| 表 | 键 | 必需的 |
| --- | --- | --- |
| 文件顶层 | `name`、`servings`、`tags`、`ingredients` 和 `steps` | 五个都必需。`tags` 和 `ingredients` 可以是空列表。 |
| `name` | `zh` 和 `en` | 至少一种语言。 |
| `ingredients` 的一项 | `item`、`amount` 和 `note` | `item` 和 `amount`。 |
| `note` | `zh` 和 `en` | 无。两种语言都没有的备注就是没有备注。 |
| `steps` | `zh` 和 `en`，每个都是文字列表 | 至少一种语言。 |

问题的位置如下。N 从 1 开始数列表的项，被跳过的项也算在内，所以就是你在文件里数出的编号。

| 位置 | 英文 | 中文 |
| --- | --- | --- |
| `name` | `name` | `名称` |
| `servings` | `servings` | `份数` |
| 列表 `tags` | `tags` | `标签` |
| `tags` 的第 N 项 | `tag N` | `标签 N` |
| 列表 `ingredients` | `ingredients` | `食材` |
| `ingredients` 的第 N 项，连同它的备注 | `ingredient N` | `食材 N` |
| `steps` | `steps` | `步骤` |
| `steps` 里 `zh` 的第 N 项 | `Chinese step N` | `中文步骤 N` |
| `steps` 里 `en` 的第 N 项 | `English step N` | `英文步骤 N` |

名称、备注和步骤的每种语言都处于三种状态之一：

- 缺失：它的键不存在。在名称或备注里，它的文字为空或只有空白字符时也算缺失。在步骤里，它是空列表 `[]` 时也算缺失。
- 可用：在名称或备注里，它是一段不只有空白字符的文字。在步骤里，它是至少含有一段不只有空白字符的文字的列表。
- 错误：其他任何值，比如该写文字的地方写了数字，或者该写步骤列表的地方写了文字，即使是 `zh = ""` 这样空白的文字也算。所以步骤里只能放列表。下面对它的检查给出一个错误。

名称、备注和步骤的两种语言再遵守这些规则：

1. 一种语言可用、另一种缺失时，缺失的那种得到一个警告。所以警告里说命令会改为显示的那种语言总是可用的。
2. 两种语言都缺失时，名称得到 `NO_NAME`，步骤得到 `NO_STEPS`。两种语言都缺失的备注就是没有备注，不产生问题。
3. 其他情况下，这两种语言不再产生问题。错误的语言有它自己的错误。

`read_recipe` 做下面这些检查。某一部分的值类型不对时（比如 `name` 不是表），这项检查就是这一部分唯一的检查。其他每一部分照样检查，所以运行一次就能报告文件里的所有问题。

| 部分 | 检查 | 问题 | 位置 | 类别 |
| --- | --- | --- | --- | --- |
| `name` | 键不存在。 | `MISSING_KEY` | 无 | 错误 |
| `name` | 值不是表。 | `NOT_A_ZH_EN_TABLE` | `name` | 错误 |
| `name` | `zh` 或 `en` 是错误的：有这个键，但值不是文字。 | `NOT_A_TEXT` | `name` | 错误 |
| `name` | 表里有 `zh` 和 `en` 以外的键。 | `UNKNOWN_KEY` | `name` | 错误 |
| `name` | 两种语言都缺失。 | `NO_NAME` | `name` | 错误 |
| `name` | `zh` 缺失，`en` 可用。 | `NO_ZH_NAME` | `name` | 警告 |
| `name` | `en` 缺失，`zh` 可用。 | `NO_EN_NAME` | `name` | 警告 |
| `servings` | 键不存在。 | `MISSING_KEY` | 无 | 错误 |
| `servings` | 值不是整数，比如 `"2"`、`2.5` 或 `true`；或者是 16 位或更多位的整数，比如 `0x` 后面跟 5,000 位数字。 | `SERVINGS_NOT_A_NUMBER` | `servings` | 错误 |
| `servings` | 值是 -999,999,999,999,999 到 0 之间的整数。 | `SERVINGS_TOO_FEW` | `servings` | 错误 |
| `servings` | 值是 101 到 999,999,999,999,999 之间的整数。 | `SERVINGS_TOO_MANY` | `servings` | 错误 |
| `tags` | 键不存在。 | `MISSING_KEY` | 无 | 错误 |
| `tags` | 值不是列表。 | `NOT_A_LIST` | `tags` | 错误 |
| `tags` 的一项 | 这一项不是文字。 | `ITEM_NOT_A_TEXT` | `tag N` | 错误 |
| `tags` 的一项 | 这一项为空或只有空白字符。 | `EMPTY_ITEM` | `tag N` | 错误 |
| `tags` 的一项 | `catalog` 不是 `None`，而 `find_tag` 找不到这一项的标签。 | `UNKNOWN_TAG` | `tags` | 错误 |
| `tags` 的一项 | 它写出的标签已经由前面的某一项写过，比如 `quick` 之后的 `快手`。 | 无。菜谱里这个标签只出现一次。 | 无 | 无 |
| `ingredients` | 键不存在。 | `MISSING_KEY` | 无 | 错误 |
| `ingredients` | 值不是列表。 | `NOT_A_LIST` | `ingredients` | 错误 |
| 一样食材 | 这一项不是表。 | `NOT_A_TABLE` | `ingredient N` | 错误 |
| 一样食材 | `item` 不存在、不是文字，或者为空或只有空白字符。 | `MISSING_KEY`、`NOT_A_TEXT` 或 `EMPTY_TEXT` | `ingredient N` | 错误 |
| 一样食材 | `catalog` 不是 `None`，而 `find_ingredient` 找不到 `item` 的食材。 | `UNKNOWN_INGREDIENT` | `ingredient N` | 错误 |
| 一样食材 | `amount` 不存在、不是文字，或者为空或只有空白字符。 | `MISSING_KEY`、`NOT_A_TEXT` 或 `EMPTY_TEXT` | `ingredient N` | 错误 |
| 一样食材 | `parse_quantity` 读不了 `amount`。 | 按下表，对应它的原因的提示 | `ingredient N` | 错误 |
| 一样食材 | 有 `note`，但它不是表。 | `NOT_A_ZH_EN_TABLE` | `ingredient N` | 错误 |
| 一样食材 | `note` 的 `zh` 或 `en` 是错误的：有这个键，但值不是文字。 | `NOT_A_TEXT` | `ingredient N` | 错误 |
| 一样食材 | `note` 里有 `zh` 和 `en` 以外的键。 | `UNKNOWN_KEY` | `ingredient N` | 错误 |
| 一样食材 | `note` 缺一种语言，另一种可用。 | `NO_ZH_NOTE` 或 `NO_EN_NOTE` | `ingredient N` | 警告 |
| 一样食材 | 这一项有 `item`、`amount` 和 `note` 以外的键。 | `UNKNOWN_KEY` | `ingredient N` | 错误 |
| `steps` | 键不存在。 | `MISSING_KEY` | 无 | 错误 |
| `steps` | 值不是表。 | `NOT_A_STEPS_TABLE` | `steps` | 错误 |
| `steps` | `zh` 或 `en` 是错误的：有这个键，但值不是列表，比如 `zh = ""`。 | `NOT_A_LIST` | `steps` | 错误 |
| 一个步骤 | 这一项不是文字。 | `ITEM_NOT_A_TEXT` | `Chinese step N` 或 `English step N` | 错误 |
| 一个步骤 | 这一项为空或只有空白字符。 | `EMPTY_ITEM` | `Chinese step N` 或 `English step N` | 错误 |
| `steps` | 表里有 `zh` 和 `en` 以外的键。 | `UNKNOWN_KEY` | `steps` | 错误 |
| `steps` | 两种语言都缺失。 | `NO_STEPS` | `steps` | 错误 |
| `steps` | 缺一种语言，另一种可用。 | `NO_ZH_STEPS` 或 `NO_EN_STEPS` | `steps` | 警告 |
| 文件顶层 | 键表里五个键以外的键。 | `UNKNOWN_KEY` | 无 | 错误 |

`catalog` 为 `None` 时，`read_recipe` 做除 `UNKNOWN_TAG`、`UNKNOWN_INGREDIENT` 和 `AMOUNT_NO_UNIT` 以外的所有检查。`UNKNOWN_TAG` 的位置是列表 `tags`，与 F07 原型一致，因为提示已经写出了标签。`tags` 中一项的其他问题位于 `tag N`。

问题按这个顺序排列：

1. 各部分的顺序是 `name`、`servings`、`tags`、`ingredients`、`steps`，然后是文件顶层的其他键，按文件里的顺序。
2. 同一部分里，问题按上表各行的顺序排列。列表自己的问题在前，然后是每一项的问题，按项的顺序。
3. 一样食材的问题按键排列：先 `item`，再 `amount`，再 `note`，然后是它的未知键，按文件里的顺序。
4. 名称、备注或步骤先给出 `zh` 的问题，再给出 `en` 的问题，然后是它们的未知键（按文件里的顺序），最后是 `NO_NAME`、`NO_STEPS` 或缺失语言的警告。

`read_recipe` 用 `parse_quantity(amount, unit)` 读取 `amount`，其中 `unit` 是 `item` 写出的那种食材的默认单位（F03 设计 2.4）。所以鸡蛋的默认单位是 个，`3` 就是 3 个。`item` 有问题，或者 `catalog` 为 `None` 时，它不带默认单位读取 `amount`，并报告除 `NO_UNIT` 以外的所有原因，因为只有食材的默认单位才能决定这个数量是否需要单位。每种原因给出下表里的提示：

| `WrongQuantity` 的原因（F01 设计 2.5） | 提示 | 给出它的数量 |
| --- | --- | --- |
| `NOT_A_NUMBER` | `AMOUNT_NOT_A_NUMBER` | `a few`、`1/2 tsp`、`-1 g` 或 `1234567890123456 g`（数字有 16 位）。 |
| `UNKNOWN_UNIT` | `AMOUNT_UNKNOWN_UNIT` | `1 cups`。 |
| `NO_UNIT` | `AMOUNT_NO_UNIT`，只在 `item` 写出目录里的一种食材时给出 | 番茄的 `3`，番茄没有默认单位。 |
| `ZERO` | `AMOUNT_ZERO` | `0 g`。 |
| `EMPTY` | 无。空白的 `amount` 先由 `EMPTY_TEXT` 报告。 | 无 |

`read_recipe` 使用 `datafile` 关于文件结构的提示（F03 设计 2.10）：`MISSING_KEY`、`NOT_A_LIST`、`NOT_A_TABLE`、`NOT_A_TEXT`、`EMPTY_TEXT`、`ITEM_NOT_A_TEXT`、`EMPTY_ITEM` 和 `UNKNOWN_KEY`。它按表里键的个数选择 `UNKNOWN_KEY` 的形式：文件顶层五个，一样食材三个，`name`、`note` 和 `steps` 两个。下面是 `recipes` 的提示。占位符是花括号里的名称，比如 `{amount}`。`{ ... }` 里的花括号是文字的一部分，所以 `NOT_A_ZH_EN_TABLE` 的模板把每个花括号写两次（F02 设计 2.2）。

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `NAME`、`SERVINGS`、`TAGS`、`TAG_N`、`INGREDIENTS`、`INGREDIENT_N`、`STEPS`、`ZH_STEP_N` 和 `EN_STEP_N` | 位置表里的位置，N 写作 `{number}`。 | 位置表里的位置，N 写作 `{number}`。 |
| `NOT_A_ZH_EN_TABLE` | `"{key}" must be a table in braces with "zh" and "en", such as { zh = "...", en = "..." }.` | `“{key}”必须是放在花括号里、带有“zh”和“en”的表，比如 { zh = "...", en = "..." }。` |
| `NO_NAME` | `The name has no text in either language. Write "zh", "en", or both.` | `名称在两种语言里都没有文字。请写上“zh”、“en”或两者。` |
| `NO_ZH_NAME` | `No Chinese name. Commands show the English name instead.` | `没有中文名称。命令会改为显示英文名称。` |
| `NO_EN_NAME` | `No English name. Commands show the Chinese name instead.` | `没有英文名称。命令会改为显示中文名称。` |
| `SERVINGS_NOT_A_NUMBER` | `Servings must be a whole number from 1 to 100, such as 2.` | `份数必须是 1 到 100 之间的整数，比如 2。` |
| `SERVINGS_TOO_FEW` | `Servings must be a whole number of 1 or more, not {servings}.` | `份数必须是不小于 1 的整数，不能是 {servings}。` |
| `SERVINGS_TOO_MANY` | `Servings must be a whole number of 100 or less, not {servings}.` | `份数必须是不大于 100 的整数，不能是 {servings}。` |
| `UNKNOWN_TAG` | `Unknown tag "{tag}". Add it to the catalog's tags.` | `未知标签“{tag}”。请把它加入目录里的标签。` |
| `UNKNOWN_INGREDIENT` | `Unknown ingredient "{name}". Add it to the catalog, or use its name in the catalog.` | `未知食材“{name}”。请把它加入目录，或改用目录里的名称。` |
| `AMOUNT_NOT_A_NUMBER` | `The amount "{amount}" must start with a number of at most 15 digits, such as 300 or 1.5, or be "适量" or "to taste".` | `数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，或者写成“适量”或“to taste”。` |
| `AMOUNT_UNKNOWN_UNIT` | `Unknown unit "{unit}" in "{amount}".` | `数量“{amount}”里有未知单位“{unit}”。` |
| `AMOUNT_NO_UNIT` | `The amount "{amount}" has no unit, and the catalog gives "{ingredient}" no default unit. Write a unit after the number, such as "300 g".` | `数量“{amount}”没有单位，目录也没有给“{ingredient}”默认单位。请在数字后面写上单位，比如“300 g”。` |
| `AMOUNT_ZERO` | `The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".` | `数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。` |
| `NO_ZH_NOTE` | `No Chinese note. Commands show the English note instead.` | `没有中文备注。命令会改为显示英文备注。` |
| `NO_EN_NOTE` | `No English note. Commands show the Chinese note instead.` | `没有英文备注。命令会改为显示中文备注。` |
| `NOT_A_STEPS_TABLE` | `"steps" must be a table. Write the line [steps] at the end of the file, and below it zh = [ ... ] and en = [ ... ].` | `“steps”必须是表。请在文件末尾写一行 [steps]，在它下面写 zh = [ ... ] 和 en = [ ... ]。` |
| `NO_STEPS` | `The recipe has no steps. Write the steps in "zh", "en", or both.` | `菜谱没有步骤。请在“zh”、“en”或两者里写上步骤。` |
| `NO_ZH_STEPS` | `No Chinese steps. Commands show the English steps instead.` | `没有中文步骤。命令会改为显示英文步骤。` |
| `NO_EN_STEPS` | `No English steps. Commands show the Chinese steps instead.` | `没有英文步骤。命令会改为显示中文步骤。` |

占位符的值如下：

| 占位符 | 值 |
| --- | --- |
| `key` | 文件里写的键。在 `NOT_A_ZH_EN_TABLE` 里是 `name` 或 `note`。在 `datafile` 的提示里是 `zh`、`en`、`item`、`amount`、`tags`、`ingredients` 或文件顶层的某个键。在 `UNKNOWN_KEY` 里是那个未知的键。 |
| `keys` | 这个表的键按键表的顺序经 `and_list` 列出，比如“item, amount, and note”和“item、amount 和 note”。 |
| `servings` | 文件里的份数，类型为 `int`。只有 -999,999,999,999,999 到 999,999,999,999,999 之间的数字才会用到这里，所以文字最多 15 位。 |
| `tag` | `tags` 的这一项去掉两端空白后的文字。 |
| `name` | `item` 去掉两端空白后的文字。 |
| `amount` | `WrongQuantity` 的 `text`：`amount` 去掉两端空白后的文字。 |
| `unit` | `WrongQuantity` 的 `unit`，比如 `cups`。 |
| `ingredient` | 食材的名称，即它的 `BiText`，所以每种语言显示自己的名称。 |
| `number` | N，即这一项的编号。 |

F07 原型和场景 v0.1-S04、v0.1-S07 展示了其中五个问题。`recipes\mapo-tofu.toml, ingredient 3` 得到 `Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.`，`recipes\red-braised-pork.toml, steps` 得到 `No English steps. Commands show the Chinese steps instead.`。`recipes\rice.toml` 在 `servings` 得到 `Servings must be a whole number of 1 or more, not 0.`，在 `ingredient 1` 得到 `Unknown unit "cups" in "1 cups".`，在 `tags` 得到 `Unknown tag "breakfast". Add it to the catalog's tags.`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `is_recipe_id(recipe_id)` 为假。`read_recipe` 在读取之前检查这一点，所以 `DataFolder.recipe_file` 永远不会收到错误的名称。 |

- 副作用：通过 `read_toml` 读取 `recipes/<id>.toml`。它不列出文件夹，也不写任何东西。
- 性能指标：无

示例：

这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。第二个文件在 `rice.toml` 里有场景 v0.1-S07 的错误。第三个文件缺少英文名称，份数是 5,000 位的十六进制数，一种没有默认单位的食材的数量没写单位，一个数量有 16 位，还有一条备注和步骤只有英文。最后一处修改在 `red-braised-pork.toml` 的步骤里加上 `en = ""`，它的警告就变成了错误，因为步骤里只能放列表。

```python
from fractions import Fraction
from pathlib import Path

from recipe_menu.catalog import read_catalog
from recipe_menu.datafile import Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.recipes import read_recipe
from recipe_menu.units import Quantity, Unit

catalog, _ = read_catalog(folder)
assert catalog is not None
recipe, problems = read_recipe(folder, catalog, "tomato-egg")
assert problems == ()
assert recipe is not None
assert recipe.id == "tomato-egg"
assert recipe.name == BiText("Tomato and egg stir-fry", "番茄炒蛋")
assert recipe.servings == 2
assert recipe.tags == (catalog.find_tag("快手"), catalog.find_tag("家常"))
egg = recipe.ingredients[1]
assert egg.ingredient is catalog.find_ingredient("Egg")
assert egg.quantity == Quantity(Fraction(3), Unit.PIECE)
assert recipe.ingredients[0].note == BiText("cut into wedges", "切块")
assert recipe.ingredients[3].quantity.is_to_taste
assert len(recipe.steps.get(Lang.ZH)) == 4

pork, problems = read_recipe(folder, catalog, "red-braised-pork")
assert pork is not None
assert pork.steps.exact(Lang.EN) is None
assert [problem.severity for problem in problems] == [Severity.WARNING]
assert problems[0].file == Path("recipes", "red-braised-pork.toml")
assert problems[0].place == BiText("steps", "步骤")
assert problems[0].text(Lang.EN) == "No English steps. Commands show the Chinese steps instead."

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
tofu, problems = read_recipe(folder, catalog, "mapo-tofu")
assert tofu is None
assert [problem.place for problem in problems] == [BiText("ingredient 3", "食材 3")]
assert problems[0].text(Lang.ZH) == "未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。"

lines = [
    'name = { zh = "米饭", en = "Steamed rice" }',
    "servings = 0",
    'tags = ["breakfast"]',
    'ingredients = [{ item = "大米", amount = "1 cups" }]',
    "[steps]",
    'zh = ["煮饭。"]',
    'en = ["Cook the rice."]',
]
folder.recipe_file("rice").write_text("\n".join(lines) + "\n", encoding="utf-8")
rice, problems = read_recipe(folder, catalog, "rice")
assert rice is None
assert [problem.place for problem in problems] == [
    BiText("servings", "份数"),
    BiText("tags", "标签"),
    BiText("ingredient 1", "食材 1"),
]
assert problems[0].text(Lang.EN) == "Servings must be a whole number of 1 or more, not 0."
assert problems[1].text(Lang.ZH) == "未知标签“breakfast”。请把它加入目录里的标签。"
assert problems[2].text(Lang.EN) == 'Unknown unit "cups" in "1 cups".'

lines = [
    'name = { zh = "番茄", en = " " }',
    "servings = 0x" + "f" * 5000,
    "tags = []",
    "ingredients = [",
    '  { item = "番茄", amount = "3" },',
    '  { item = "葱", amount = "1234567890123456 根", note = { en = "chopped" } },',
    "]",
    "[steps]",
    'en = ["Cook."]',
]
folder.recipe_file("rice").write_text("\n".join(lines) + "\n", encoding="utf-8")
rice, problems = read_recipe(folder, catalog, "rice")
assert rice is None
assert [problem.severity for problem in problems] == [
    Severity.WARNING,
    Severity.ERROR,
    Severity.ERROR,
    Severity.ERROR,
    Severity.WARNING,
    Severity.WARNING,
]
assert problems[0].text(Lang.EN) == "No English name. Commands show the Chinese name instead."
assert problems[1].text(Lang.EN) == "Servings must be a whole number from 1 to 100, such as 2."
assert problems[2].text(Lang.ZH).startswith("数量“3”没有单位，目录也没有给“番茄”默认单位。")
assert problems[3].text(Lang.EN).startswith('The amount "1234567890123456 根" must start')
assert problems[4].place == BiText("ingredient 2", "食材 2")
assert problems[5].text(Lang.ZH) == "没有中文步骤。命令会改为显示英文步骤。"

pork_file = folder.recipe_file("red-braised-pork")
pork_file.write_text(pork_file.read_text(encoding="utf-8") + 'en = ""\n', encoding="utf-8")
pork, problems = read_recipe(folder, catalog, "red-braised-pork")
assert pork is None
assert [problem.severity for problem in problems] == [Severity.ERROR]
assert problems[0].place == BiText("steps", "步骤")
assert problems[0].text(Lang.EN) == '"en" must be a list in square brackets, [ ... ].'

assert read_recipe(folder, None, "tomato-egg") == (None, ())
gone, problems = read_recipe(folder, catalog, "mapo")
assert gone is None
assert problems[0].text(Lang.EN) == "The file is missing."

read_recipe(folder, catalog, "Tomato-Egg")  # raises ValueError
```

### 2.7 `read_recipes`

- 模块：recipes
- 功能：读取 `recipes/` 里的每个菜谱文件，并报告文件夹和各文件的所有问题（[需求 4](../../requirements.zh-CN.md#4-功能点)，F04）。`list`、`search` 和 `check` 调用它，F14 的 `menu suggest` 也调用它（架构 8）。

签名：

```python
def read_recipes(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[tuple[Recipe, ...], tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `catalog` | `Catalog` 或 `None` | 目录，与 `read_recipe` 相同（2.6）。 | 目录读不了时为 `None`。 |

- 返回值：一对值 `(recipes, problems)`。
  - `read_recipes` 调用一次 `list_recipe_ids`，再按 ID 的顺序为每个 ID 调用一次 `read_recipe`。
  - `recipes` 包含 `read_recipe` 给出的每个菜谱，按 ID 的顺序排列。有错误的文件不给出菜谱。`catalog` 为 `None` 时，`recipes` 为空。
  - `problems` 先包含 `list_recipe_ids` 的问题，再包含 `read_recipe` 为每个 ID 给出的问题，按 ID 的顺序排列。

错误：无。`read_recipes` 遇到坏数据从不抛异常。

- 副作用：通过 `list_toml_files` 列一次 `recipes/`，通过 `read_toml` 把每个菜谱文件读一次。它不写任何东西。
- 性能指标：无

示例：

这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。第二次运行加入一个名称不是 ID 的文件，并让 `rice.toml` 只有 `servings = 0`，这会给出五个错误。

```python
from pathlib import Path

from recipe_menu.catalog import read_catalog
from recipe_menu.datafile import Severity
from recipe_menu.recipes import read_recipes

catalog, _ = read_catalog(folder)
recipes, problems = read_recipes(folder, catalog)
assert len(recipes) == 7
assert recipes[0].id == "choy-sum"
assert recipes[-1].id == "tomato-egg-noodles"
assert [problem.file for problem in problems] == [Path("recipes", "red-braised-pork.toml")]
assert problems[0].severity is Severity.WARNING

(folder.recipes / "Rice Bowl.toml").write_text("", encoding="utf-8")
folder.recipe_file("rice").write_text("servings = 0\n", encoding="utf-8")
recipes, problems = read_recipes(folder, catalog)
assert len(recipes) == 6
files = [problem.file for problem in problems]
rice = Path("recipes", "rice.toml")
pork = Path("recipes", "red-braised-pork.toml")
assert files == [Path("recipes", "Rice Bowl.toml"), pork, rice, rice, rice, rice, rice]

recipes, problems = read_recipes(folder, None)
assert recipes == ()
assert len(problems) == 7
```

## 3. 对已有接口的修改

无。F01 到 F03 已实现的接口都不改变。每个导出的名称都保持原有的签名和行为，F03 的测试不用修改就能通过。F04 给 `datafile` 的接口加入名称，就像 F02 给 F01 的 `lang` 加入 `BiText` 一样，它还修改 `catalog` 的内部文件。

1. `datafile` 导出 `list_toml_files`（3.1）。架构 6 把数据文件的每个 `OSError` 交给 `datafile`，架构 8 只让 `datafile` 打开数据文件，所以 `recipes` 通过它列出 `recipes/`。F06 可以用它列出 `menus/`。
2. `datafile` 导出 `Report`、`read_list`、`read_table`、`read_text` 和 `report_unknown_keys`（3.2）。它们从 `src/recipe_menu/catalog/_shape.py` 移过来，在那里它们是 `catalog` 内部的。`recipes` 能引用 `catalog`，但 `settings` 和 `menus` 不能（架构 3），所以留在 `catalog` 里的辅助函数就得被复制到 F05 和 F06 里。`Report` 增加方法 `warn`。`read_catalog` 和 `read_pantry` 从 `recipe_menu.datafile` 引用这些辅助函数，并删除 `catalog/_shape.py`。`catalog` 的接口不变，`read_catalog` 和 `read_pantry` 按相同的顺序给出相同的问题。
3. F04 按各自的设计使用 F01 的 `Quantity`、`TO_TASTE`、`Unit`、`WrongQuantity`、`WrongQuantityReason` 和 `parse_quantity`，F02 的 `BiText`、`Lang`、`Message`、`MessageValue`、`Plural` 和 `and_list`，以及 F03 的 `DataFolder`、`Problem`、`Severity`、`read_toml`、F03 设计 2.10 的提示、`Catalog`、`Ingredient` 和 `Tag`，不修改其中任何一个。

### 3.1 `list_toml_files`

- 模块：datafile
- 功能：列出数据文件夹里某个文件夹中的 TOML 文件。它把 `OSError` 变成 `Problem`（[架构 6](../../architecture.zh-CN.md#6-错误处理)），并报告 `.toml` 结尾里有大写字母的名称。`list_recipe_ids` 用它列出 `recipes/`（2.5），F06 可以用它列出 `menus/`。它不读任何文件，所以命令不用解析文件就能知道文件名（架构 8）。

签名：

```python
def list_toml_files(
    folder: DataFolder,
    path: Path,
) -> tuple[tuple[str, ...], tuple[Problem, ...]]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | 数据文件夹。 | 无 |
| `path` | `Path` | 要列出的文件夹，比如 `folder.recipes`。 | 在 `folder.root` 里面。 |

- 返回值：一对值 `(names, problems)`。
  - `names` 包含 `path` 里名称以 `.toml`（就是这几个小写字母）结尾的每个条目的名称，去掉这个结尾，按码位排序。任何种类的条目都算，名为 `x.toml` 的文件夹也算，所以 `list_toml_files` 不需要查看每个条目；之后 `read_toml` 会把这样的文件夹报告为 `FILE_IS_FOLDER`。没有这样的条目的文件夹给出空元组。
  - `problems` 为 `.toml` 结尾里有大写字母的每个条目包含一个错误 `TOML_ENDING_NOT_SMALL`，比如 `rice.TOML` 或 `rice.Toml`，按码位排序。这样的名称以 `.` 加上 `t` 或 `T`、`o` 或 `O`、`m` 或 `M`、`l` 或 `L` 结尾，但不以 `.toml` 结尾。问题的文件是这个条目相对于数据文件夹的路径，比如 `Path("menus", "2026-W48.TOML")`，没有位置。读取函数要 `rice.toml` 时，Windows 会打开 `rice.TOML`，而 Linux 不会，所以这个名称不在 `names` 里，错误提示你给文件改名。
  - 列出 `path` 时出现 `OSError`，`names` 就为空，`problems` 只包含一个问题。它的严重程度为 `Severity.ERROR`，文件为 `folder.relative(path)`，没有位置。它的提示来自下表第一个适用的行：

| 条件 | 提示 |
| --- | --- |
| `path.is_file()` 为真。这个探测从不抛异常，探测失败时算作假。 | `FOLDER_IS_FILE` |
| 错误是 `FileNotFoundError`，或者是因为 `path` 上层的某个文件夹其实是文件而出现的 `NotADirectoryError`。 | `FOLDER_MISSING` |
| 错误是 `PermissionError`。 | `FOLDER_ACCESS_DENIED` |
| 其他任何 `OSError`。 | `FOLDER_SYSTEM_ERROR`。它的值 `reason` 是错误的 `strerror`；`strerror` 为 `None` 或空时，是错误的类名，比如 `OSError`。 |

这些提示加入 `datafile` 的内部提示，与 F03 设计 2.3 的 `FILE_MISSING` 等提示放在一起：

| 名称 | 英文 | 中文 |
| --- | --- | --- |
| `FOLDER_MISSING` | `The folder is missing.` | `文件夹不存在。` |
| `FOLDER_IS_FILE` | `The folder cannot be read: it is a file.` | `无法读取文件夹：它是一个文件。` |
| `FOLDER_ACCESS_DENIED` | `The folder cannot be read: access is denied.` | `无法读取文件夹：没有访问权限。` |
| `FOLDER_SYSTEM_ERROR` | `The folder cannot be read. The system says: {reason}` | `无法读取文件夹。系统提示：{reason}` |
| `TOML_ENDING_NOT_SMALL` | `The file name must end with ".toml" in small letters. Rename the file.` | `文件名必须以小写的“.toml”结尾。请给文件改名。` |

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `path` 不在 `folder.root` 里面，由 `DataFolder.relative` 判断。`list_toml_files` 在列出之前检查这一点。 |

- 副作用：列出 `path` 处的文件夹。它不读任何文件，也不写任何东西。
- 性能指标：无

示例：

这个示例里，`folder` 是一个 `DataFolder`，指向示例数据文件夹 `tests/data/example/` 的一份新副本（架构 10）。

```python
import shutil
from pathlib import Path

from recipe_menu.datafile import list_toml_files
from recipe_menu.lang import Lang

assert list_toml_files(folder, folder.menus) == (("2026-W47",), ())
(folder.menus / "notes.txt").write_text("Ideas\n", encoding="utf-8")
(folder.menus / "2026-W48.TOML").write_text("", encoding="utf-8")
names, problems = list_toml_files(folder, folder.menus)
assert names == ("2026-W47",)
assert [problem.file for problem in problems] == [Path("menus", "2026-W48.TOML")]
assert problems[0].place is None
assert problems[0].text(Lang.ZH) == "文件名必须以小写的“.toml”结尾。请给文件改名。"

shutil.rmtree(folder.menus)
names, problems = list_toml_files(folder, folder.menus)
assert names == ()
assert [problem.file for problem in problems] == [Path("menus")]
assert problems[0].place is None
assert problems[0].text(Lang.EN) == "The folder is missing."

folder.menus.write_text("", encoding="utf-8")
names, problems = list_toml_files(folder, folder.menus)
assert names == ()
assert problems[0].text(Lang.ZH) == "无法读取文件夹：它是一个文件。"

list_toml_files(folder, Path("D:/other"))  # raises ValueError
```

### 3.2 `Report`、`read_list`、`read_table`、`read_text` 和 `report_unknown_keys`

- 模块：datafile
- 功能：读取函数用这些辅助函数检查文件的结构，并用 F03 设计 2.10 的提示报告出来。读取函数为自己的文件创建一个 `Report`，把它传给每个辅助函数，用 `add` 和 `warn` 加入自己的问题，最后返回 `tuple(report.problems)`。它们原样从 `src/recipe_menu/catalog/_shape.py` 移过来。只有 `warn` 是新的，因为 F04 会给出警告，而 F03 不给出警告。

签名：

```python
class Report:
    file: Path
    problems: list[Problem]

    def __init__(self, file: Path) -> None: ...

    def add(self, place: BiText | None, message: Message, /, **values: MessageValue) -> None: ...

    def warn(self, place: BiText | None, message: Message, /, **values: MessageValue) -> None: ...


def read_list(
    table: Mapping[str, object],
    key: str,
    place: BiText,
    report: Report,
) -> list[object]: ...


def read_table(item: object, place: BiText, report: Report) -> dict[str, object] | None: ...


def read_text(
    table: Mapping[str, object],
    key: str,
    place: BiText,
    report: Report,
) -> str | None: ...


def report_unknown_keys(
    table: Mapping[str, object],
    known: Sequence[str],
    place: BiText | None,
    report: Report,
) -> None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `file` | `Path` | 这个报告里每个问题的文件，相对于数据文件夹，比如 `Path("recipes", "rice.toml")`。 | 与 `Problem` 的 `file` 相同（F03 设计 2.2）。 |
| `place` | `BiText` 或 `None` | 问题、列表、这一项或这个表的位置。 | 只在签名允许的地方为 `None`，用于整个文件的问题。 |
| `message` 和 `values` | `Message`，以及 `MessageValue` 关键字参数 | 错在哪里，以及每个占位符的值。 | 与 `Problem.error` 相同（F03 设计 2.2）。 |
| `table` | `str` 到 `object` 的映射 | 文件里的一个表，就是 `read_toml` 给出的样子。 | 无 |
| `key` | `str` | 列表或文字的键。 | 无 |
| `item` | `object` | 列表的一项，就是文件给出的样子。 | 无 |
| `known` | `str` 的序列 | 这个表可以有的键，按读取函数的设计给出的顺序。 | 无 |
| `report` | `Report` | 问题放到哪里。 | 无 |

- 返回值：
  - `Report(file)` 给出一个空报告。`problems` 按顺序列出到目前为止加入的问题。`add` 追加 `Problem.error(file, place, message, **values)`，`warn` 追加 `Problem.warning(file, place, message, **values)`。
  - `read_list` 给出 `key` 处的列表。键不存在时，它加入没有位置的 `MISSING_KEY`，给出 `[]`。值不是列表时，它在 `place` 加入 `NOT_A_LIST`，给出 `[]`。
  - `read_table` 在 `item` 是表时给出 `item`。否则它在 `place` 加入 `NOT_A_TABLE`，给出 `None`。
  - `read_text` 给出 `key` 处去掉两端空白的文字。键不存在时加入 `MISSING_KEY`，值不是文字时加入 `NOT_A_TEXT`，文字只有空白字符时加入 `EMPTY_TEXT`，都在 `place`，然后给出 `None`。
  - `report_unknown_keys` 不给出任何值。对 `table` 中不在 `known` 里的每个键，按表里的顺序，它在 `place` 加入 `UNKNOWN_KEY`，使用 `len(known)` 个键时的形式，值 `keys` 为 `and_list(known)`。

`Report` 不是数据模型里的值。它是读取函数在一次调用里创建、用完就丢的收集器。没有读取函数返回它或把它保存在某个值里，每个读取函数都以元组返回自己的问题。所以跨模块的每个值仍然是冻结的，符合架构 8 的要求。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `Problem.error` 和 `Problem.warning` 的错误（F03 设计 2.2） | `add` 或 `warn` 收到不匹配的提示和值，或者 `file` 是绝对路径。其他辅助函数只传入匹配的提示和值。 |

- 副作用：`add`、`warn` 和这四个函数向 `report.problems` 追加问题，别的什么都不改变。
- 性能指标：无

示例：

```python
from pathlib import Path

from recipe_menu.datafile import Report, Severity, read_list, read_text, report_unknown_keys
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

report = Report(Path("recipes", "rice.toml"))
table = {"tags": "主食", "ingredients": [{"item": " "}], "note": 3}
assert read_list(table, "tags", BiText("tags", "标签"), report) == []
item = read_text({"item": " "}, "item", BiText("ingredient 1", "食材 1"), report)
assert item is None
report_unknown_keys(table, ("tags", "ingredients"), None, report)
NO_EN = Message("No English steps.", "没有英文步骤。")
report.warn(BiText("steps", "步骤"), NO_EN)
problems = report.problems
assert [problem.severity for problem in problems] == [
    Severity.ERROR,
    Severity.ERROR,
    Severity.ERROR,
    Severity.WARNING,
]
assert problems[0].text(Lang.EN) == '"tags" must be a list in square brackets, [ ... ].'
assert problems[1].text(Lang.EN) == '"item" is empty.'
assert problems[2].text(Lang.EN) == 'Unknown key "note". The keys are tags and ingredients.'
assert problems[3].place == BiText("steps", "步骤")
```

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `recipes` 是领域层模块，只引用 `lang`、`units`、`text`、`datafile` 和 `catalog`，并且只通过 `datafile` 访问磁盘，与架构 3、4 和 8 允许的一致。`Recipe` 和 `RecipeIngredient` 有架构 5.2 列出的字段。`RecipeIngredient` 持有目录自己的 `Ingredient` 对象，所以 F12 能按同一个对象合并。选择 5 符合 5.2：`Steps` 把“每种语言一组字符串元组形式的步骤”放在一个值里，并像 `BiText` 那样回退到另一种语言。设计可以增加这样的辅助值，就像 F01 增加了 `WrongQuantity`，F03 增加了 `Severity`。选择 7 符合架构 3 和 6。架构 6 把数据文件的每个 `OSError` 交给 `datafile`，架构 3 把数据文件夹里各文件的路径和带位置的问题交给它，所以 `list_toml_files`、它的五个提示和检查文件结构的辅助函数都属于那里。3.1 对 `.toml` 结尾的检查也属于那里，因为架构 5.2 让 `DataFolder` 成为唯一知道文件名的地方，F06 也能用这项检查处理 `menus/`。按现在的设计，`Report` 符合架构 8。它不是数据模型里的值。它是一次读取调用创建、交给辅助函数、用完就丢的收集器，每个读取函数都返回 `tuple(report.problems)`。选择 4 符合架构 6。读取函数仍然检查整个文件，记下每个问题，而 `check` 以外的命令都不会用到有错误的菜谱。选择 6 符合架构 6 和需求 3：`init` 会创建 `recipes/`，数据文件夹缺少某部分时以 1 退出。发现 1，已解决。选择 1 收窄了需求 3 和 F04 那一行，所以由 Troy 决定，Troy 在对话里决定保留这条规则（方案 A）。选择 1 现在按架构 1 和 F03 设计 2.1 列出文件名需要满足的条件，并给出要求更多的原因，去掉了 0.1 版里言过其实的理由。`TOML_ENDING_NOT_SMALL` 出自同一个决定。它报告 `rice.TOML` 这样的文件，而 0.1 版跳过这样的文件，不产生问题。所以 `recipes/` 里 Windows 能当作菜谱文件打开的每个条目，现在都会给出一个 ID 或一个错误，这个错误的作用与 `NOT_A_RECIPE_ID` 相同。Troy 批准这份设计时会看到它（R18，`troy_approves_first = 16`）。发现 2，已解决。Troy 在对话里接受了 1 到 100 的范围，用于菜谱、设置、一道菜和 `show --servings`。它不需要修改架构。5.2 的“（1 或更多）”是每个读取函数都要守住的下限，5.2 把确切的约束留给各个设计。F05、F06 和 F09 的设计遵守选择 2。提示里的数字不超过 15 位这条规则仍然必要。`tomllib` 能读出 5,000 位的十六进制整数，没有这条规则，`Problem` 会因为坏数据抛出 F02 的 4,300 位 `ValueError`（F03 的审查）。发现 6，可选，不阻塞。选择 1 说“原因有四个”，接着却给出五个，因为关于 `-x` 的那句是第五个。以后的修订可以改成“原因有五个”。 |
| 遵守错误处理和命名约定 | Pass | 每个读取函数都返回自己的问题，遇到坏数据从不抛异常（架构 6）。异常只来自错误的调用：`read_recipe` 收到不符合规则的 ID，`list_toml_files` 收到数据文件夹之外的路径，以及 2.1 到 2.3 的构造函数收到错误的值。`list_toml_files` 按 `read_toml` 的条件顺序把每个 `OSError` 变成 `Problem`，所以它的 `except` 子句在生成 `Problem` 的地方写明 `OSError`（架构 6 和 8）。它现在返回一对值 `(names, problems)`，与 `list_recipe_ids`、`read_recipe` 和 `read_catalog` 相同，所以调用方不用检查结果的类型。文件夹出错时，`names` 为空，只有一个问题。`TOML_ENDING_NOT_SMALL` 是错误，它的文件是相对于数据文件夹的条目，没有位置。它的提示不显示名称，因为上面那行文件已经显示了，与 `NOT_A_RECIPE_ID` 相同。3.1 的规则能找出 Windows 当作 `.toml` 打开的每种结尾。Unicode 没有按一对一的大小写映射把 ASCII 以外的字符对应到 `t`、`o`、`m`、`l` 或它们的大写，架构师也在 Windows 上确认了 `a.toml` 会打开文件 `a.TOML`。每个问题都写出相对于数据文件夹的文件，并以字段写出位置，比如 `ingredient 3`。整个文件的问题没有位置（架构 1 和 6）。缺少一种语言是警告，从不改变退出码。发现 3，已解决。2.6 现在给步骤的每种语言只定一种状态。缺失是键不存在或 `[]`，任何文字，即使是 `zh = ""`，都是错误，在 `steps` 处得到 `NOT_A_LIST`。选择 3、三种状态、表里的那一行和新示例都一致。在架构师的模型里，`zh = ""`、`zh = " "` 和 `zh = 3` 在 `steps` 处得到 `NOT_A_LIST`，`zh = []` 得到警告 `NO_ZH_STEPS`，`zh = [" "]` 在 `Chinese step 1` 处得到 `EMPTY_ITEM`。`zh = ""` 且 `en = []` 时，`zh` 是错误的，所以规则 3 不再加 `NO_STEPS`，文件仍然有它的错误。名称或备注里空白的文字仍然算作缺少这种语言。F02 的审查把这个选择留给每个读取函数，它也与 F03 的 `EMPTY_TEXT` 一致。提示只在文件里的数字不超过 15 位时才显示它，`AMOUNT_NOT_A_NUMBER` 写出了 F01 的位数限制，这正是 F01 的审查要求的。F07 原型和场景 v0.1-S04、v0.1-S07 展示的五个问题仍然能从规则推出，2.6 列出了它们。名称遵守 PEP 8，提示都是放在 `recipes/messages.py` 和 `datafile/messages.py` 里的 UPPER_SNAKE 常量（架构 8）。 |
| 不和已有接口重复 | Pass | `recipes` 是新模块。它用 F01 的 `parse_quantity` 读取数量，用 F03 的 `find_ingredient` 和 `find_tag` 查找名称，用 `read_toml` 读取文件，用 F03 设计 2.10 的八个提示报告结构错误，所以这些都不重写。`list_recipe_ids` 把 `list_toml_files` 的问题传下去，不再检查一遍 `.toml` 结尾。`TOML_ENDING_NOT_SMALL` 留在 `datafile` 内部，所以 F06 不用复制就能对 `menus/` 做同样的检查。`is_recipe_id` 拒绝 `DataFolder.recipe_file` 拒绝的每个名称，还拒绝更多名称（2.4），`recipe_file` 保留自己的检查，作为最后一道关。`Steps` 为步骤元组重复了 `BiText` 的回退。`BiText` 只接受文字（F02 设计 2.1），把它改成泛型会修改已实现的接口，所以再加一个小的值是更好的选择。3.2 的移动避免了复制。不移动的话，不能引用 `catalog` 的 `settings` 和 `menus` 都得复制这些辅助函数。位置 `tags`、`tag N`、`ingredients` 和 `ingredient N` 重复了 `catalog` 内部的文字。架构 8 让每个模块保留自己的提示，所以这些副本可以接受。`UNKNOWN_INGREDIENT` 和 `AMOUNT_UNKNOWN_UNIT` 与目录的 `UNKNOWN_INGREDIENT` 和 `UNKNOWN_UNIT` 不同，与 F07 原型一致。 |
| 只依赖排序在前面的功能 | Pass | F04 使用 F01、F02 和 F03，它们都排在 F04 之前，并且在 main 上通过了测试。第 3 节写出了它用到的每个接口。`datafile` 新增的内容只用到 `lang` 和 `text`，架构 3 允许 `datafile` 依赖它们。F04 不依赖任何后续功能。第 2 节为后续功能写的安排不约束后续设计，只有 Troy 对份数的决定（选择 2）例外，F05、F06 和 F09 都遵守它。这些功能排在 F04 之后，所以可以依靠它，它们的设计也各自接受审查。这些接口只需要标准库，所以没有新依赖需要按 R16 审查。`docs/rules.md` 没有交给架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | Pass | 模块之间的每个假设都写在设计里。`read_recipe` 打开 `recipes/<id>.toml` 时不列出文件夹，所以调用方传入 `list_recipe_ids` 给出的 ID，第 2 节为 F06 和 F09 写明了这一点。F06 对照 `list_recipe_ids` 检查菜品的 ID，从不用菜单文件里的内容拼出路径。`Report` 只在一次调用里作为参数进入 `datafile`。`AMOUNT_NOT_A_NUMBER` 写出了 F01 的 15 位限制（F01 设计 2.7），所以修改这个限制时也要修改这条提示。`list_toml_files` 对名称和问题都排序，所以调用方不依赖文件系统给出的顺序。发现 4，已解决。`list_toml_files` 报告 `rice.TOML` 这样的名称，`list_recipe_ids` 先把这个问题传下去，再给出自己的错误，所以在两种系统上这样的文件都不会再没人发现。发现 7，不阻塞。3.1 把 `TOML_ENDING_NOT_SMALL` 的问题“按码位排序”，但没有说按哪段文字排序。两种做法的顺序不同：按整个条目名，`a-b.TOML` 排在 `a.TOML` 前面；按去掉结尾的名称，它排在后面。架构师建议按整个条目名，架构师的模型就是这样做的。接口设计师可以在以后的修订里写明按哪段文字，或者由测试经理在 PR 2 里定下来。下面几点留给后续设计，不阻塞。F05、F06 和 F09：按 Troy 的决定，份数都用 1 到 100 的范围。F07 原型给份数为 0 的菜品的文字就是 `SERVINGS_TOO_FEW` 的文字，而份数的提示是 `recipes` 内部的，所以 F06 要么请 `recipes` 导出它们，要么定义文字相同的自己的提示。F06：像 `list_recipe_ids` 那样，把 `list_toml_files` 为 `menus/` 给出的问题传下去，并严格按周的格式检查每个名称。在 Windows 上，`menu_file("2026-W47")` 会打开 `2026-w47.toml`，而 `list_toml_files` 把它列为 `2026-w47`。F07：`read_recipes` 已经返回 `list_recipe_ids` 的问题，包括 `TOML_ENDING_NOT_SMALL`，所以 F07 再用 `list_recipe_ids` 数菜谱时，这些问题只报告一次。缺少 `recipes/` 时，`list_recipe_ids` 给出一个错误，不给出 ID。F09：F09 原型“缺少一种语言”为 `red-braised-pork` 显示四个中文步骤，而 `tests/data/example/recipes/red-braised-pork.toml` 有另外三个步骤。v0.1-S12 第 3 步期望原型的输出，所以由 F09 的设计决定改哪一边。F15 和 F16：你输入的 ID 先用 `is_recipe_id` 检查，再对照 `list_recipe_ids`，然后才调用 `read_recipe` 或创建新文件。在 Windows 上，`Tomato-Egg.toml` 会作为 `tomato-egg` 的文件被打开，名为 `rice.TOML` 的文件也会让 `datafile` 无法创建 `rice.toml`。 |
| 修改已实现的接口时走了变更流程 | Pass | `datafile` 和 `catalog` 已经实现（F03）。第 3 节现在以“无”开头，与 F02 的第 3 节相同，所以发现 5 已解决。F04 不修改 F01 到 F03 导出的任何名称。每个名称都保持原来的签名和行为，`recipe_menu.catalog` 仍然导出同样的七个名称。F04 给 `recipe_menu.datafile` 加入 `list_toml_files`、`Report`、`read_list`、`read_table`、`read_text` 和 `report_unknown_keys`，只修改 `catalog` 的内部文件：两处引用，以及把 `_shape.py` 移到 `datafile`。让每个已有约定保持原样的加入不需要修改需求（troy-mode 需求 5.4），就像 F02 把 `BiText` 加入 F01 的 `lang` 那样。架构 3 安排了后续功能往 `datafile` 里加内容，这些辅助函数也符合它的职责（第一行）。PR #24 的代码审查员为 F04 到 F06 提出了这次移动。`list_toml_files` 是 F04 新加的，还没有实现，所以它的结果从 0.1 版到 0.2 版的变化不修改任何已实现的接口。F01 到 F03 的全部 213 个测试在架构师按 0.2 版建的模型上都通过，所以“F03 的测试不用修改就能通过”成立。留给后续阶段的几点：移过去的辅助函数在 F04 的 mock PR 里保留函数体，因为 F03 的代码调用它们，而 mock PR 要让已有测试继续通过。这样一来，针对某个移过去的辅助函数的新测试会在 mock 上通过，违反 R09，所以测试计划只为 `Report.warn` 和 `list_toml_files` 增加用例，移过去的辅助函数交给 F03 的测试。这次移动修改 F03 的三个文件，所以主会话安排 PR 时要考虑 R03。在 Windows 上，`Path` 比较路径时不分大小写，所以 `Path("recipes", "pancakes.TOML") == Path("recipes", "pancakes.toml")` 在那里为真。因此 2.5 和 3.1 的示例在 Windows 上不检查问题文件的大小写，需要检查大小写的测试要比较 `problem.file.name` 或 `str(problem.file)`。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求和架构检查了第 2 节的七项选择。选择 1 和 2 收窄了需求允许的范围，所以由 Troy 决定（发现 1 和 2）。每个文件有 19 个代码块，每个都与另一种语言的版本相同，18 个 `python` 代码块都能解析。架构师在 main 上 F01 到 F03 的代码之上，按第 2 节和第 3 节建了模型，在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 和 3.14.3 运行了 9 个示例。每个断言和全部 13 个 `# raises` 都成立。期望的值都能从设计的规则、`docs/prototypes/example-data.md` 和 F07 原型里关于菜谱的几行推出。模型带目录和不带目录各读了 3,000 个随机的菜谱文件，没有抛出异常。辅助函数移动以后，F01 到 F03 的全部 213 个测试都通过。ruff 0.17.4 的 `ruff format --check` 报告两个文件都已格式化。发现 3 到 5 不阻塞。 | 批准。Troy 在批准这份设计时（R18）决定发现 1 和 2。接口设计师对发现 3 到 5 作出决定。 |
| 2 | 没有阻塞问题。0.2 版记下了 Troy 对发现 1 和 2 的决定，并解决了发现 3、4 和 5。`list_toml_files` 现在给出 `(names, problems)` 和错误 `TOML_ENDING_NOT_SMALL`，`list_recipe_ids` 把这些问题传下去（3.1 和 2.5）。架构师把第 1 轮的模型更新到 0.2 版，在 `tests/data/example/` 的全新副本上，用 Windows 上的 Python 3.13.18 和 3.14.3 运行了 9 个示例。每个断言和全部 13 个 `# raises` 都成立。2.5、2.6 和 3.1 里改过的示例在第 1 轮的模型上不通过，所以它们检查了这些修改。设计里的 26 行提示与模型的提示相同。每个文件仍然有 19 个代码块，每个都与另一种语言的版本相同，18 个 `python` 代码块都能解析。两个文件的标题、表格行和列表项都对得上。模型带目录和不带目录各读了 3,000 个随机的菜谱文件，没有抛出异常，F01 到 F03 的全部 213 个测试在它上面都通过。架构师没有重新运行 `ruff format --check` 和 troy-check，项目经理已经在 0.2 版上运行过它们。发现 6 和 7 不阻塞。 | 批准。由 Troy 批准这份设计（R18）。接口设计师对发现 6 和 7 作出决定，或者由测试经理在 PR 2 里定下发现 7。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-11 | 初稿。 |
| 0.2 | 2026-11-11 | 回应架构师审查第 1 轮，并记下 Troy 的决定。Troy 保留菜谱 ID 的规则（选择 1），也保留份数的范围 1 到 100，用于菜谱、设置、一道菜和 `show --servings`（选择 2）。选择 1 给出 ID 规则真正的原因。步骤里的文字，即使是 `zh = ""`，也是错误的，得到 `NOT_A_LIST`，所以步骤里只能放列表（选择 3 和 2.6）。第 3 节以“无”开头。`list_toml_files` 给出一对名称和问题，并为 `rice.TOML` 这样的名称给出 `TOML_ENDING_NOT_SMALL`，`list_recipe_ids` 把它传下去（选择 6、2.5 和 3.1）。2.5、2.6 和 3.1 的示例覆盖了新的情况。 |
| 1.0 | 2026-11-11 | Troy 批准。 |
