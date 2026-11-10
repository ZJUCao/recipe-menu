---
troy-doc: "F01-design"
lang: "zh-CN"
version: "1.1"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "design.md"
---

# F01 数量和单位：接口设计

## 1. 功能

- 编号和名称：F01 数量和单位
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：无

## 2. 接口

F01 构建两个基础层模块（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.lang` 导出 `Lang`。`recipe_menu.units` 导出 `UnitKind`、`Unit`、`Quantity`、`TO_TASTE`、`WrongQuantity`、`WrongQuantityReason`、`parse_unit`、`parse_quantity` 和 `add_quantities`。每个模块的 `__init__.py` 在 `__all__` 里列出这些名称。背后的文件由开发工程师决定。

下面每个接口都遵守这些规则：

- 每个数量都是精确的 `fractions.Fraction`，没有 `float` 存放数量（ADR-0007）。数量按精确值比较，不留容差。
- `units` 遇到坏数据从不抛异常。写错的数量文字得到一个 `WrongQuantity` 值，由 `recipes` 把它变成带自己提示的 `Problem`（[架构 4](../../architecture.zh-CN.md#4-依赖规则) 和 [6](../../architecture.zh-CN.md#6-错误处理)）。下文 `units` 抛出的异常都来自错误的调用，也就是 bug。`Lang(value)` 遇到未知的语言代码时，会像所有枚举一样抛出 `ValueError`，由调用方把它变成 `Problem` 或 `UsageError`。
- `units` 在包内只引用 `lang`。它没有 `Message`，单位的名称是普通数据（ADR-0004）。
- 没有接口打印、读文件或保存状态。

以下后续功能打算调用这些接口：

- F03 用 `parse_unit` 读取食材的默认单位。
- F04 用 `parse_quantity` 和食材的默认单位读取每样食材的数量。
- F09 用 `Quantity.scale` 换算菜谱，用 `Quantity.to_text` 写出每个数量。
- F12 用 `Quantity.scale` 换算每道菜，用 `add_quantities` 把每种食材的数量相加。
- F13 用 `Quantity.to_rounded_text` 写出每个总量。

### 2.1 `Lang`

- 模块：lang
- 功能：工具的两种语言。每个为用户写出文字的接口都接受一个 `Lang`。它的值就是 `--lang` 和设置里 `language` 接受的值。

签名：

```python
class Lang(StrEnum):
    EN = "en"
    ZH = "zh"
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `value` | `str` | `Lang(value)` 查找的语言代码。 | `"en"` 或 `"zh"`，写法完全一致。 |

- 返回值：`Lang(value)` 给出值为 `value` 的成员。成员是一个等于其值的 `str`，所以 `str(Lang.ZH)` 是 `"zh"`。成员的顺序是 `EN`、`ZH`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `Lang(value)` 收到其他字符串，比如 `"fr"` 或 `"EN"`。调用方把它变成自己的提示。 |

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.lang import Lang

assert Lang("zh") is Lang.ZH
assert str(Lang.EN) == "en"
assert list(Lang) == [Lang.EN, Lang.ZH]
Lang("fr")  # raises ValueError
```

### 2.2 `UnitKind`

- 模块：units
- 功能：单位的种类：质量、体积或计数。质量换算成克，体积换算成毫升。计数单位不换算成任何别的单位，不同种类之间也从不换算。

签名：

```python
class UnitKind(Enum):
    MASS = "mass"
    VOLUME = "volume"
    COUNT = "count"
```

参数：无

- 返回值：无。`Unit.kind`（2.3）给出一个成员。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.units import Unit, UnitKind

assert Unit.TBSP.kind is UnitKind.VOLUME
assert Unit.JIN.kind is UnitKind.MASS
assert Unit.BUNCH.kind is UnitKind.COUNT
```

### 2.3 `Unit`

- 模块：units
- 功能：[需求 3](../../requirements.zh-CN.md#3-用户如何使用) 里的每个单位各一个成员，带种类、换算成克或毫升的大小，以及两种语言的名称。这些名称，包括每个计数单位的英文复数，都是 `units` 里的普通数据，因为 `units` 排在 `text` 前面（ADR-0004）。

签名：

```python
class Unit(Enum):
    G = "g"
    KG = "kg"
    JIN = "jin"
    LIANG = "liang"
    ML = "ml"
    L = "L"
    TSP = "tsp"
    TBSP = "tbsp"
    PIECE = "piece"
    STALK = "stalk"
    CLOVE = "clove"
    SLICE = "slice"
    BLOCK = "block"
    BUNCH = "bunch"
    CAN = "can"
    PACK = "pack"

    @property
    def kind(self) -> UnitKind: ...

    @property
    def size(self) -> Fraction | None: ...

    def label(self, lang: Lang, *, plural: bool = False) -> str: ...
```

每个成员的值是它的英文名称。代码用 `parse_unit`（2.6）按写法查找单位，而不是按值查找。下表列出每个成员及其属性的返回值。

| 成员 | `kind` | `size` | 英文名称 | 英文复数 | 中文名称 | `parse_unit` 认得的写法 |
| --- | --- | --- | --- | --- | --- | --- |
| `G` | `MASS` | 1 | g | g | g | `g`、`克` |
| `KG` | `MASS` | 1000 | kg | kg | kg | `kg`、`千克`、`公斤` |
| `JIN` | `MASS` | 500 | jin | jin | 斤 | `jin`、`斤` |
| `LIANG` | `MASS` | 50 | liang | liang | 两 | `liang`、`两` |
| `ML` | `VOLUME` | 1 | ml | ml | ml | `ml`、`毫升` |
| `L` | `VOLUME` | 1000 | L | L | L | `L`、`升` |
| `TSP` | `VOLUME` | 5 | tsp | tsp | 茶匙 | `tsp`、`茶匙` |
| `TBSP` | `VOLUME` | 15 | tbsp | tbsp | 汤匙 | `tbsp`、`汤匙` |
| `PIECE` | `COUNT` | `None` | piece | pieces | 个 | `piece`、`pieces`、`个` |
| `STALK` | `COUNT` | `None` | stalk | stalks | 根 | `stalk`、`stalks`、`根` |
| `CLOVE` | `COUNT` | `None` | clove | cloves | 瓣 | `clove`、`cloves`、`瓣` |
| `SLICE` | `COUNT` | `None` | slice | slices | 片 | `slice`、`slices`、`片` |
| `BLOCK` | `COUNT` | `None` | block | blocks | 块 | `block`、`blocks`、`块` |
| `BUNCH` | `COUNT` | `None` | bunch | bunches | 把 | `bunch`、`bunches`、`把` |
| `CAN` | `COUNT` | `None` | can | cans | 罐 | `can`、`cans`、`罐` |
| `PACK` | `COUNT` | `None` | pack | packs | 包 | `pack`、`packs`、`包` |

英文写法不区分大小写，所以 `L`、`l`、`ML` 和 `Tbsp` 都能匹配。`G`、`KG`、`ML` 和 `L` 的中文名称就是符号，因为购物清单在两种语言下都写 g、kg、ml 和 L，F09 和 F13 原型的中文输出里也写 `600 g`。jin 和 liang 这两个名称没有英文复数。

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | `label` 返回的名称所用的语言。 | 无 |
| `plural` | `bool` | 名称是否跟在不等于 1 的数量后面。 | 只影响英文的计数单位名称。中文名称不受它影响。 |

- 返回值：`kind` 给出单位的 `UnitKind`。`size` 以精确的 `Fraction` 给出一个质量单位合多少克、一个体积单位合多少毫升，计数单位给出 `None`。`label` 给出表中的名称。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.lang import Lang
from recipe_menu.units import Unit, UnitKind

assert Unit.JIN.size == Fraction(500)
assert Unit.TBSP.size == Fraction(15)
assert Unit.CLOVE.kind is UnitKind.COUNT
assert Unit.CLOVE.size is None
assert Unit.STALK.label(Lang.EN) == "stalk"
assert Unit.STALK.label(Lang.EN, plural=True) == "stalks"
assert Unit.JIN.label(Lang.EN, plural=True) == "jin"
assert Unit.TSP.label(Lang.ZH, plural=True) == "茶匙"
```

### 2.4 `Quantity` 和 `TO_TASTE`

- 模块：units
- 功能：某个单位下的精确数量，或者“适量”。菜谱里的每样食材有一个（[架构 5.2](../../architecture.zh-CN.md#52-值) 的 `RecipeIngredient.quantity`），购物清单每一行里的每个总量也是一个。`TO_TASTE` 就是表示“适量”的值。

签名：

```python
@dataclass(frozen=True, slots=True)
class Quantity:
    amount: Fraction | None
    unit: Unit | None

    @property
    def is_to_taste(self) -> bool: ...

    # Methods: in_base_unit (2.8), scale (2.9), to_text (2.11), and to_rounded_text (2.12).


TO_TASTE: Final[Quantity] = Quantity(None, None)
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `amount` | `Fraction` 或 `None` | 精确的数值，以 `unit` 计。 | 大于 0。只有“适量”时为 `None`。 |
| `unit` | `Unit` 或 `None` | `amount` 的单位。 | 只有“适量”时为 `None`。`amount` 和 `unit` 要么都有值，要么都是 `None`。 |

- 返回值：一个 `Quantity`。`amount` 和 `unit` 都是 `None` 时，`is_to_taste` 为 `True`。两个数量的数值相等、单位也相等时才相等，所以 1 kg 和 1000 g 不相等。要比较大小，就比较 `in_base_unit` 的结果。`Quantity` 可以做哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `amount` 既不是 `Fraction` 也不是 `None`，比如 `float` 或 `int`。 |
| `ValueError` | `amount` 和 `unit` 一个是 `None`，另一个不是。 |
| `ValueError` | `amount` 小于或等于 0。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.units import TO_TASTE, Quantity, Unit

tomato = Quantity(Fraction(300), Unit.G)
assert not tomato.is_to_taste
assert TO_TASTE.is_to_taste
assert TO_TASTE == Quantity(None, None)
assert Quantity(Fraction(1), Unit.KG) != Quantity(Fraction(1000), Unit.G)
Quantity(300.0, Unit.G)  # raises TypeError
Quantity(Fraction(0), Unit.G)  # raises ValueError
```

### 2.5 `WrongQuantity` 和 `WrongQuantityReason`

- 模块：units
- 功能：说明 `parse_quantity` 读不了的数量文字错在哪里。`units` 没有提示，所以由 `recipes` 把这个值变成带两种语言提示的 `Problem`，比如 F07 原型里的 `Unknown unit "cups" in "1 cups".`（[架构 4](../../architecture.zh-CN.md#4-依赖规则)）。

签名：

```python
class WrongQuantityReason(Enum):
    EMPTY = "empty"
    NOT_A_NUMBER = "not-a-number"
    UNKNOWN_UNIT = "unknown-unit"
    NO_UNIT = "no-unit"
    ZERO = "zero"


@dataclass(frozen=True, slots=True)
class WrongQuantity:
    reason: WrongQuantityReason
    text: str
    unit: str | None = None
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `reason` | `WrongQuantityReason` | 错在哪里。2.7 的错误表给出每个成员的条件。 | 无 |
| `text` | `str` | 去掉两端空白后的数量文字。 | 无 |
| `unit` | `str` 或 `None` | 原样写出的未知单位，比如 `"cups"`。 | 只有 `UNKNOWN_UNIT` 时有值。其他原因都是 `None`。 |

- 返回值：一个 `WrongQuantity`。三个字段都相等时，两个值相等。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.units import WrongQuantity, WrongQuantityReason, parse_quantity

assert parse_quantity(" 1 cups ") == WrongQuantity(WrongQuantityReason.UNKNOWN_UNIT, "1 cups", "cups")
assert parse_quantity("a few") == WrongQuantity(WrongQuantityReason.NOT_A_NUMBER, "a few")
```

### 2.6 `parse_unit`

- 模块：units
- 功能：用任一语言找出一个词表示的单位。`catalog` 用它读取食材的默认单位，`parse_quantity` 用它读取数字后面的单位。

签名：

```python
def parse_unit(text: str) -> Unit | None: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 原样写出的单位，比如 `"g"`、`"公斤"` 或 `"cloves"`。 | 任意字符串。 |

- 返回值：`parse_unit` 去掉 `text` 两端的空白后，返回 2.3 的写法里包含 `text` 的那个 `Unit`。英文写法不区分大小写。没有单位用这个写法时返回 `None`，空字符串、`"to taste"` 和 `"适量"` 都是这样。

错误：无。`parse_unit` 从不抛异常。

- 副作用：无
- 性能指标：无

示例：

```python
from recipe_menu.units import Unit, parse_unit

assert parse_unit("公斤") is Unit.KG
assert parse_unit(" Tbsp ") is Unit.TBSP
assert parse_unit("cloves") is Unit.CLOVE
assert parse_unit("cups") is None
assert parse_unit("适量") is None
```

### 2.7 `parse_quantity`

- 模块：units
- 功能：按菜谱的写法读取数量：带单位或不带单位的数字，或者“适量”（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，“单位”）。

签名：

```python
def parse_quantity(text: str, default_unit: Unit | None = None) -> Quantity | WrongQuantity: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `text` | `str` | 原样写出的数量，比如 `"300 g"`、`"1.5 kg"`、`"300克"`、`"3"` 或 `"适量"`。 | 任意字符串。 |
| `default_unit` | `Unit` 或 `None` | 没写单位的数量所用的单位，也就是目录里该食材的默认单位。 | 食材没有默认单位时为 `None`。`text` 里写了单位时，总是以 `text` 为准。 |

- 返回值：一个 `Quantity`。读不了 `text` 时返回一个 `WrongQuantity`。

`parse_quantity` 按以下步骤读取 `text`：

1. 去掉两端的空白，包括全角空格 U+3000。
2. `to taste` 得到 `TO_TASTE`，不区分大小写，两个词之间是一个或多个空白字符。`适量` 也得到 `TO_TASTE`。
3. 数字是第一个字母或空白字符之前的文字。字母指 `str.isalpha` 为真的字符，汉字也算。数字是一个或多个 ASCII 数字，后面可以跟 `.` 和一个或多个 ASCII 数字，比如 `3`、`300`、`1.5` 或 `0.25`。数字最多 15 位。小数点不算，每一位数字都算，开头和末尾的 0 也算，所以 `12345678901234.5` 能读，`0.000000000000001` 不能读。这个上限让数字远低于 Python 的 `int` 和 `Fraction` 从字符串读取时允许的 4300 位。数字被读成精确的 `Fraction`，所以 `1.5` 就是 3/2。
4. 其余的文字去掉两端空白后就是单位，用 `parse_unit` 读取。单位前的空格可有可无，所以 `300 g`、`300g` 和 `300克` 都可以。
5. 没写单位的数量使用 `default_unit`。

错误：

`parse_quantity` 从不抛异常。它返回一个 `WrongQuantity`，原因是下表中第一条符合的。

| 错误 | 何时发生 |
| --- | --- |
| `EMPTY` | `text` 为空，或者只有空白。 |
| `NOT_A_NUMBER` | 缺少数字，数字不是由 ASCII 数字组成的十进制数，或者数字超过 15 位，比如 `a few`、`g`、`1/2 tsp`、`1,5 g`、`-1 g`、`½ tsp`、带全角数字的 `３ 个`，或者 `1234567890123456 g`。这一行排在 `UNKNOWN_UNIT` 和 `ZERO` 前面，所以 `1234567890123456 cups` 和 `0000000000000000 g` 也得到 `NOT_A_NUMBER`。 |
| `UNKNOWN_UNIT` | 单位不是 2.3 里的任何写法，比如 `1 cups` 或 `1 适量`。字段 `unit` 存放这个单位。 |
| `NO_UNIT` | 文字里没有单位，`default_unit` 也是 `None`。 |
| `ZERO` | 数字是 0，比如 `0 g` 或 `0.00 个`。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.units import TO_TASTE, Quantity, Unit, WrongQuantity, WrongQuantityReason, parse_quantity

assert parse_quantity("300 g") == Quantity(Fraction(300), Unit.G)
assert parse_quantity("1.5kg") == Quantity(Fraction(3, 2), Unit.KG)
assert parse_quantity("1 斤") == Quantity(Fraction(1), Unit.JIN)
assert parse_quantity("3", Unit.PIECE) == Quantity(Fraction(3), Unit.PIECE)
assert parse_quantity("2 tbsp", Unit.PIECE) == Quantity(Fraction(2), Unit.TBSP)
assert parse_quantity("适量") == TO_TASTE
assert parse_quantity("To  taste") == TO_TASTE
assert parse_quantity("3") == WrongQuantity(WrongQuantityReason.NO_UNIT, "3")
assert parse_quantity("0 g") == WrongQuantity(WrongQuantityReason.ZERO, "0 g")
```

### 2.8 `Quantity.in_base_unit`

- 模块：units，`Quantity`（2.4）的方法
- 功能：把质量精确地换算成克，把体积精确地换算成毫升。计数单位不换算成任何别的单位，所以计数和“适量”保持原样。

签名：

```python
def in_base_unit(self) -> Quantity: ...
```

参数：无

- 返回值：质量单位返回 `Quantity(amount * unit.size, Unit.G)`。体积单位返回 `Quantity(amount * unit.size, Unit.ML)`。计数单位和“适量”返回原来的数量。

错误：无

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.units import TO_TASTE, Quantity, Unit

assert Quantity(Fraction(1), Unit.JIN).in_base_unit() == Quantity(Fraction(500), Unit.G)
assert Quantity(Fraction(3, 2), Unit.KG).in_base_unit() == Quantity(Fraction(1500), Unit.G)
assert Quantity(Fraction(2), Unit.TBSP).in_base_unit() == Quantity(Fraction(30), Unit.ML)
assert Quantity(Fraction(3), Unit.CLOVE).in_base_unit() == Quantity(Fraction(3), Unit.CLOVE)
assert TO_TASTE.in_base_unit() == TO_TASTE
```

### 2.9 `Quantity.scale`

- 模块：units，`Quantity`（2.4）的方法
- 功能：把数值乘以一个系数，比如这道菜的份数除以菜谱的份数。单位保持不变，所以 `show` 能用菜谱里的单位写出换算后的数量。

签名：

```python
def scale(self, factor: Fraction) -> Quantity: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `factor` | `Fraction` | 要乘的数，比如 2 份的菜谱做 4 份时为 `Fraction(4, 2)`。 | 大于 0。 |

- 返回值：精确的 `Quantity(amount * factor, unit)`。“适量”返回 `TO_TASTE`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `factor` 不是 `Fraction`，比如 `float` 或 `int`。 |
| `ValueError` | `factor` 小于或等于 0。对“适量”也是这样。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.units import TO_TASTE, Quantity, Unit

oil = Quantity(Fraction(2), Unit.TBSP)
assert oil.scale(Fraction(4, 2)) == Quantity(Fraction(4), Unit.TBSP)
egg = Quantity(Fraction(3), Unit.PIECE)
assert egg.scale(Fraction(3, 2)) == Quantity(Fraction(9, 2), Unit.PIECE)
assert TO_TASTE.scale(Fraction(2)) == TO_TASTE
oil.scale(Fraction(0))  # raises ValueError
```

### 2.10 `add_quantities`

- 模块：units
- 功能：把同类数量相加：质量按克相加，体积按毫升相加，每种计数单位各自相加。它从不把质量换算成体积，也不把两者换算成计数（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)，购物清单规则 3）。

签名：

```python
def add_quantities(quantities: Iterable[Quantity]) -> tuple[Quantity, ...]: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `quantities` | `Iterable[Quantity]` | 要相加的数量，比如一种食材在一周每道菜里换算后的数量。 | 任意单位，可以包括“适量”。可以为空。 |

- 返回值：每组一个精确的总量：所有质量合成一个 `Unit.G` 的 `Quantity`，所有体积合成一个 `Unit.ML` 的 `Quantity`，每种计数单位各合成一个该单位的 `Quantity`。各总量按其组在 `quantities` 里第一次出现的顺序排列。“适量”不加任何东西，所以没有一个数量带数值时，返回空元组。总量不取整。`to_rounded_text` 写出总量时才取整。

错误：无

- 副作用：无
- 性能指标：无

示例：

前三个例子是 F13 原型里的几行。

```python
from fractions import Fraction

from recipe_menu.units import TO_TASTE, Quantity, Unit, add_quantities

choy_sum = Quantity(Fraction(1), Unit.JIN)
assert add_quantities([choy_sum, choy_sum.scale(Fraction(4, 2))]) == (Quantity(Fraction(1500), Unit.G),)

stalk = Quantity(Fraction(1), Unit.STALK)
scallion = [stalk.scale(Fraction(2)), stalk, stalk, stalk, Quantity(Fraction(1), Unit.BUNCH)]
assert add_quantities(scallion) == (Quantity(Fraction(5), Unit.STALK), Quantity(Fraction(1), Unit.BUNCH))

soy_sauce = [Quantity(Fraction(2), Unit.TBSP), TO_TASTE, Quantity(Fraction(10), Unit.G)]
assert add_quantities(soy_sauce) == (Quantity(Fraction(30), Unit.ML), Quantity(Fraction(10), Unit.G))

assert add_quantities([TO_TASTE, TO_TASTE]) == ()
assert add_quantities([]) == ()
```

### 2.11 `Quantity.to_text`

- 模块：units，`Quantity`（2.4）的方法
- 功能：用数量自己的单位写出它。`show` 用它，因为 `show`“按菜谱里用的单位显示数量”（[需求 3](../../requirements.zh-CN.md#3-用户如何使用)）。

签名：

```python
def to_text(self, lang: Lang) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | 写出时用的语言。 | 无 |

- 返回值：按以下规则写出的文字：
  - “适量”在英文里是 `to taste`，在中文里是 `适量`。
  - 其他数量写成数值、一个空格和单位的名称（2.3）。
  - 数值向上取整到最多两位小数，用 `.` 作小数点，不写末尾的 0，也不写千位分隔符，比如 `2`、`4.5`、`1.34` 或 `1500`。
  - 英文里，除非写出的数值是 `1`，名称都用复数。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 取整后的数值在小数点前超过 4300 位，这是 Python 写出 `int` 的上限（`sys.int_info.default_max_str_digits`）。这个错误只来自错误的调用。`parse_quantity` 读出的数量即使按份数换算，也远远达不到这个位数。 |

- 副作用：无
- 性能指标：无

示例：

前五个例子是 F09 原型里的几行。

```python
from fractions import Fraction

from recipe_menu.lang import Lang
from recipe_menu.units import TO_TASTE, Quantity, Unit

assert Quantity(Fraction(1), Unit.STALK).to_text(Lang.EN) == "1 stalk"
assert Quantity(Fraction(3), Unit.PIECE).to_text(Lang.EN) == "3 pieces"
assert Quantity(Fraction(1), Unit.JIN).to_text(Lang.EN) == "1 jin"
assert Quantity(Fraction(2), Unit.TSP).to_text(Lang.ZH) == "2 茶匙"
assert Quantity(Fraction(600), Unit.G).to_text(Lang.ZH) == "600 g"
assert Quantity(Fraction(9, 2), Unit.PIECE).to_text(Lang.EN) == "4.5 pieces"
assert Quantity(Fraction(4, 3), Unit.TBSP).to_text(Lang.EN) == "1.34 tbsp"
assert TO_TASTE.to_text(Lang.ZH) == "适量"
```

### 2.12 `Quantity.to_rounded_text`

- 模块：units，`Quantity`（2.4）的方法
- 功能：按 [需求 3](../../requirements.zh-CN.md#3-用户如何使用) 的取整规则写出数量：克数、毫升数和计数都向上取整到整数（购物清单规则 8，Q18）。1000 g 及以上用 kg 显示，1000 ml 及以上用 L 显示，最多保留两位小数（规则 9）。购物清单用它写出每个总量。

签名：

```python
def to_rounded_text(self, lang: Lang) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | 写出时用的语言。 | 无 |

- 返回值：写出的文字。

`to_rounded_text` 按以下步骤生成文字：

1. “适量”在英文里是 `to taste`，在中文里是 `适量`。
2. 用 `in_base_unit` 换算数量。
3. 把数值向上取整到整数。
4. 1000 g 及以上用 kg 写出，1000 ml 及以上用 L 写出。kg 或 L 的数值向上取整到最多两位小数，写法同 2.11：1500 g 写成 `1.5 kg`，1000 g 写成 `1 kg`，1001 g 写成 `1.01 kg`。
5. 其他数值写成整数、一个空格和单位的名称，比如 `600 g`、`15 ml`、`5 stalks` 或 `1 block`。英文里，除非数值是 1，名称都用复数。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `to_rounded_text` 写出的取整后的数值在小数点前超过 4300 位，这是 Python 写出 `int` 的上限（`sys.int_info.default_max_str_digits`）。这个错误只来自错误的调用。`parse_quantity` 读出的数量即使按份数换算，也远远达不到这个位数。 |

- 副作用：无
- 性能指标：无

示例：

这些例子来自 F13 原型和版本测试计划的场景 v0.1-S16。

```python
from fractions import Fraction

from recipe_menu.lang import Lang
from recipe_menu.units import TO_TASTE, Quantity, Unit

assert Quantity(Fraction(1500), Unit.G).to_rounded_text(Lang.EN) == "1.5 kg"
assert Quantity(Fraction(1000), Unit.G).to_rounded_text(Lang.ZH) == "1 kg"
assert Quantity(Fraction(1001), Unit.G).to_rounded_text(Lang.EN) == "1.01 kg"
assert Quantity(Fraction(1), Unit.JIN).to_rounded_text(Lang.EN) == "500 g"
assert Quantity(Fraction(1), Unit.TBSP).to_rounded_text(Lang.ZH) == "15 ml"
assert Quantity(Fraction(3, 2), Unit.STALK).to_rounded_text(Lang.EN) == "2 stalks"
assert Quantity(Fraction(9, 2), Unit.PIECE).to_rounded_text(Lang.EN) == "5 pieces"
assert Quantity(Fraction(1), Unit.BLOCK).to_rounded_text(Lang.EN) == "1 block"
assert Quantity(Fraction(5), Unit.STALK).to_rounded_text(Lang.ZH) == "5 根"
assert TO_TASTE.to_rounded_text(Lang.EN) == "to taste"
```

## 3. 对已有接口的修改

无

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | Pass | `lang` 和 `units` 是基础层模块，`units` 只引用 `lang`（架构 3 和 4）。`Unit` 为需求 3 的每个单位各设一个成员，带架构 5.2 列出的种类、大小和名称。用一个 `Quantity`、在“适量”时让 `amount` 和 `unit` 都为 `None`，符合 5.2，因为 `RecipeIngredient.quantity` 是 `Quantity`，必须能存放“适量”。向上取整到两位小数遵守 ADR-0007：写出时最多两位小数，并用 `math.ceil` 向上取整。kg 和 L 也向上取整，这符合 Q18：把 1001 g 写成 1 kg 会买得不够。`add_quantities` 符合 5.2 的 `ShoppingLine`：只有“适量”时得到空元组，按首次出现的顺序排列则得到 `30 ml + 10 g` 和 `5 stalks + 1 bunch`，与 F13 原型和 v0.1-S18 的预期一致。总量不取整，取整就只在写出清单时做一次。版本 1.1 仍然符合。15 位的上限只改变 `parse_quantity` 能读哪些文字，它读出的每个数量仍是精确的 `Fraction`（ADR-0007）。 |
| 遵守错误处理和命名约定 | Pass | 坏数据得到一个 `WrongQuantity` 值，只有错误的调用才抛异常（架构 4 和 6）。`parse_quantity` 遵守这一点：它从不抛异常，原因有固定的先后顺序，`UNKNOWN_UNIT` 带着 F07 提示 `Unknown unit "cups" in "1 cups".` 需要的单位。它接受的数字写法是需求没有规定的产品选择，`check` 会报告它拒绝的每一段文字。复数名称遵守 ADR-0004：单位名作为普通数据放在 `units` 里，因为 `units` 不能引用 `text`。复数名称也是这些名称之一，是存下来的，不是拼出来的，所以架构 8 关于英文复数的规则管的是 `text` 提供的提示文字，不管单位名称。遇到 `int` 抛出 `TypeError`，让“每个数量都是 `Fraction`”（架构 8）在运行时也成立。严格模式的 mypy 本来就拒绝在这里传 `int`。名称遵守 PEP 8，两个数据类都是带 `slots=True` 的冻结数据类。版本 1.1 两方面都仍然遵守。2.7 第 3 步在数字变成 `Fraction` 之前就把它限制在 15 位，所以更长的数字得到 `NOT_A_NUMBER`，碰不到 `int` 和 `Fraction` 超过 4300 位时抛出的 `ValueError`。15 位也低于 `sys.set_int_max_str_digits` 接受的最低上限 640，所以无论怎样设置，`parse_quantity` 都不会抛异常。第 3 步的例子正好落在上限两侧：`12345678901234.5` 有 15 位，`0.000000000000001` 有 16 位。第 2 步现在说清楚了：没有空白的 `totaste` 不算 `to taste`，得到 `NOT_A_NUMBER`。2.11 和 2.12 的 `ValueError` 行描述的是错误的调用，架构 6 把它们当作缺陷。2.12 数的是它写出的数值的位数，也就是第 4 步把 g 换成 kg、把 ml 换成 L 之后的数值。`sys.int_info.default_max_str_digits` 是默认上限。实际生效的上限是 `sys.get_int_max_str_digits()`，`PYTHONINTMAXSTRDIGITS` 可以改变它，所以两行里的 4300 对默认设置成立，测试用的也是默认设置。不阻塞：F04 给 `NOT_A_NUMBER` 的提示也要适用于 `1234567890123456 g`，比如写出 15 位的上限。 |
| 不和已有接口重复 | Pass | F01 是第一个功能，`src/` 里还没有代码。`to_text` 为 `show` 按菜谱的单位写出数量，`to_rounded_text` 执行购物清单的规则，两者不重叠。F02 为提示文字提供的英文复数，是和这些单位名称分开的接口。 |
| 只依赖排序在前面的功能 | Pass | F01 没有功能依赖。`units` 只依赖同样由 F01 构建的 `lang`。两者都只用标准库，所以没有新依赖需要按 R16 审查。版本 1.1 没有增加依赖。新的错误行提到的 `sys.int_info` 属于标准库。 |
| 不在模块之间增加隐性耦合 | Pass | 后续模块只使用第 2 节导出的名称。`catalog` 和 `recipes` 读取 `WrongQuantity` 及其原因。2.3 规定代码用 `parse_unit` 查找单位，从不按值查找。`units` 不保存状态、不读文件、不打印。版本 1.1 在 2.11 和 2.12 里写明了一个对调用方的假设：`parse_quantity` 读出的数量即使按份数换算，也远远达不到 4300 位。这个假设只在份数不大时成立。`tomllib` 能读最多 4300 位的整数，远超 TOML 1.0 的 64 位，Python 的 `int` 从命令行也能读这么多位。所以 F05 的设计要给设置里的 `servings` 定上限，F06 的设计要给菜品的份数定上限，F09 的设计要给 `show --servings` 定上限。没有这些上限，设置、菜单文件或命令行就可能让 `to_text` 或 `to_rounded_text` 因坏数据抛异常，而架构 6 不允许这样。菜谱的份数只做除数，所以 F04 不需要为此定上限。不阻塞，因为每个上限都属于读取份数的功能，架构师审查那个功能的设计时会检查。 |
| 修改已实现的接口时走了变更流程 | Pass | 还没有已实现的接口，第 3 节写的是“无”。版本 1.1 在还没有代码时修改了 2.7、2.11 和 2.12。`src/` 还不存在，所以没有修改已实现的接口，第 3 节仍然是“无”。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求和架构，检查了接口设计师列出的六项选择。只有复数名称看起来和架构 8 冲突，而 ADR-0004 已经把它们定为 `units` 保存的单位名称。 | 批准，无需修改。 |
| 1（版本 1.1） | 没有阻塞问题。架构师审查了从版本 1.0 到 1.1 的修改。在 2.7 里，架构师检查了 15 位的上限及其例子和理由、`to taste` 的写法，以及新的 `NOT_A_NUMBER` 条件。架构师还检查了 2.11 和 2.12 的 `ValueError` 行。架构师在 Python 3.14.3 里测试了 `int`、`Fraction` 和 `tomllib` 的位数上限，这些上限与 Python 3.13 相同。有两点留给后续设计：F05、F06 和 F09 给份数定上限，F04 给 `NOT_A_NUMBER` 写一条也适用于 16 位数字的提示。 | 批准，无需修改。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-10 | 初稿。 |
| 1.0 | 2026-11-10 | Troy 批准。 |
| 1.1 | 2026-11-10 | `parse_quantity` 读取的数字限制为最多 15 位，并说明 `to taste` 两个词之间是一个或多个空白字符（2.7）。`to_text`（2.11）和 `to_rounded_text`（2.12）增加 `ValueError`：取整后的数值在小数点前超过 4300 位时抛出。 |
