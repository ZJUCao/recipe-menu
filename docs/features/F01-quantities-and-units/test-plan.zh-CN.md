---
troy-doc: "F01-test-plan"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-10"
status: "Troy 已于 2026-11-10 批准"
mirror-of: "test-plan.md"
---

# F01 数量和单位：测试方案

## 1. 功能

- 编号和名称：F01 数量和单位
- 设计：[design.zh-CN.md](design.zh-CN.md)，版本 1.1

## 2. 用例

测试直接调用 `recipe_menu.lang` 和 `recipe_menu.units` 的接口，不读任何文件。F01 没有命令，所以方案里没有功能用例。集成用例让 F09 和 F13 原型里的数量依次经过几个接口。

每个用例都依赖 mock 里没有的代码：方法或函数的函数体，或者 `Quantity` 的检查。所以每个测试对着 mock 都失败（R09）。第 4 节列出 mock 完整声明的内容。

以下约定适用于每个用例：

- 双引号里的字符串是 Python 字面量，所以 `"　"` 是全角空格 U+3000，`"\t"` 是制表符。
- `300 G` 代表 `Quantity(Fraction(300), Unit.G)`，`3/2 KG` 代表 `Quantity(Fraction(3, 2), Unit.KG)`。
- `NOT_A_NUMBER("a few")` 代表 `WrongQuantity(WrongQuantityReason.NOT_A_NUMBER, "a few")`，`UNKNOWN_UNIT("1 cups", "cups")` 代表 `WrongQuantity(WrongQuantityReason.UNKNOWN_UNIT, "1 cups", "cups")`。其他原因照此写法。
- 结果里的每个数值都是 `Fraction`。测试既检查它的值，也检查它的类型，因为数值是 `int` 300 时，`Fraction(300) == 300` 同样成立。
- 空白指 `str.isspace` 为真的每个字符，包括 U+3000，与设计 2.7 第 1 步一致。
- “按 2 份”指乘以 `Fraction(2, 2)`，即 2 份的菜谱做 2 份。“按 4 份”指乘以 `Fraction(4, 2)`。
- 长文字和大数值写成 Python 表达式，比如 `"0" * 15 + "1 g"` 或 `Quantity(Fraction(10**4300), Unit.G)`。
- Python 限制它从字符串读取、或写成字符串的 `int` 的位数。F01-T24 和 F01-T54 到 F01-T57 用 `sys.set_int_max_str_digits(4300)` 把这个上限设为默认的 4,300 位，测试结束后恢复原来的上限。所以 `PYTHONINTMAXSTRDIGITS` 改变不了它们的结果。

| 编号 | 层级 | 接口 | 测什么 | 准备和输入 | 预期结果 |
| --- | --- | --- | --- | --- | --- |
| F01-T01 | 单元 | `Unit`、`Unit.kind`、`Unit.size`、`UnitKind` | 每个单位的种类和大小与设计 2.3 的表一致。 | `Unit` 的每个成员。 | `Unit` 恰好有 16 个成员：`G`、`KG`、`JIN`、`LIANG`、`ML`、`L`、`TSP`、`TBSP`、`PIECE`、`STALK`、`CLOVE`、`SLICE`、`BLOCK`、`BUNCH`、`CAN` 和 `PACK`，每个成员的值是它的英文名称。`UnitKind` 恰好有 `MASS`、`VOLUME` 和 `COUNT`，值依次是 `"mass"`、`"volume"` 和 `"count"`。`G`、`KG`、`JIN` 和 `LIANG` 的 `kind` 是 `MASS`，`ML`、`L`、`TSP` 和 `TBSP` 的是 `VOLUME`，其余八个是 `COUNT`。前八个成员的 `size` 依次是 `Fraction` 1、1000、500、50、1、1000、5 和 15，每个计数单位的 `size` 是 `None`。 |
| F01-T02 | 单元 | `Unit.label` | 每个单位的名称与设计 2.3 一致，只有英文的计数单位名称有复数。 | 每个成员分别用 `Lang.EN` 和 `Lang.ZH`，每种各调用三次：不传 `plural`、`plural=False` 和 `plural=True`。 | 英文里，`label` 依次给出 `g`、`kg`、`jin`、`liang`、`ml`、`L`、`tsp`、`tbsp`、`piece`、`stalk`、`clove`、`slice`、`block`、`bunch`、`can` 和 `pack`。用 `plural=True` 时，八个计数单位给出 `pieces`、`stalks`、`cloves`、`slices`、`blocks`、`bunches`、`cans` 和 `packs`，其余八个单位给出与不用它时相同的名称。中文里，无论 `plural` 是什么，`label` 都依次给出 `g`、`kg`、`斤`、`两`、`ml`、`L`、`茶匙`、`汤匙`、`个`、`根`、`瓣`、`片`、`块`、`把`、`罐` 和 `包`。不传 `plural` 时，每个名称都与 `plural=False` 时相同。 |
| F01-T03 | 单元 | `Quantity`、`Quantity.is_to_taste`、`TO_TASTE` | 数量保留它的数值和单位，只有“适量”才是适量。 | `300 G`、`1/2 PIECE`、`Quantity(None, None)` 和 `TO_TASTE`。 | `300 G` 的数值是 `Fraction(300)`，单位是 `Unit.G`，`is_to_taste` 是 `False`。`1/2 PIECE` 依次是 `Fraction(1, 2)`、`Unit.PIECE` 和 `False`。`Quantity(None, None)` 和 `TO_TASTE` 的数值都是 `None`，单位都是 `None`，`is_to_taste` 都是 `True`。 |
| F01-T04 | 单元 | `Quantity` | 数值既不是 `Fraction` 也不是 `None`，属于错误的调用。 | `Quantity(a, Unit.G)`，`a` 依次取 `300.0`、`300`、`"300"` 和 `Decimal("300")`。 | 每次调用都抛出 `TypeError`。 |
| F01-T05 | 单元 | `Quantity` | 数值和单位要么同时有，要么都没有。 | `Quantity(None, Unit.G)` 和 `Quantity(Fraction(1), None)`。 | 每次调用都抛出 `ValueError`。 |
| F01-T06 | 单元 | `Quantity` | 数值大于 0。 | `Quantity(a, u)`，`a` 依次取 `Fraction(0)`、`Fraction(-1)` 和 `Fraction(-1, 2)`，`u` 依次取 `Unit.G` 和 `Unit.PIECE`。 | 每次调用都抛出 `ValueError`。 |
| F01-T07 | 单元 | `parse_unit` | 设计 2.3 表格最后一列的每种写法都指向它的单位。 | 全部 41 种写法，比如 `"g"`、`"克"`、`"kg"`、`"千克"`、`"公斤"`、`"tbsp"`、`"汤匙"`、`"cloves"` 和 `"瓣"`。 | 写法所在行的单位，比如 `"公斤"` 得到 `Unit.KG`，`"cloves"` 和 `"瓣"` 都得到 `Unit.CLOVE`。 |
| F01-T08 | 单元 | `parse_unit` | 英文写法不区分大小写。 | `"G"`、`"KG"`、`"Kg"`、`"kG"`、`"JIN"`、`"Liang"`、`"ML"`、`"Ml"`、`"l"`、`"TSP"`、`"Tbsp"`、`"PIECE"`、`"Pieces"`、`"STALKS"`、`"Clove"`、`"SLICES"`、`"Block"`、`"BUNCHES"`、`"Can"` 和 `"PACKS"`。 | 依次得到：`Unit.G`，三次 `Unit.KG`，`Unit.JIN`，`Unit.LIANG`，两次 `Unit.ML`，`Unit.L`，`Unit.TSP`，`Unit.TBSP`，两次 `Unit.PIECE`，`Unit.STALK`，`Unit.CLOVE`，`Unit.SLICE`，`Unit.BLOCK`，`Unit.BUNCH`，`Unit.CAN` 和 `Unit.PACK`。 |
| F01-T09 | 单元 | `parse_unit` | 两端的空白不影响结果。 | `" Tbsp "`、`"\t公斤\n"`、`"　个　"` 和 `"  l"`。 | `Unit.TBSP`、`Unit.KG`、`Unit.PIECE` 和 `Unit.L`。 |
| F01-T10 | 单元 | `parse_unit` | 不是任何写法的文字不指向任何单位。 | `""`、`"   "`、`"cups"`、`"cup"`、`"kgs"`、`"gs"`、`"jins"`、`"liangs"`、`"to taste"`、`"适量"`、`"茶 匙"`、`"g."`、`"克克"`，以及全角的 `"ｋｇ"`。 | 每个都得到 `None`，不抛异常。 |
| F01-T11 | 单元 | `parse_quantity` | 数字加单位，单位用哪种语言都行，中间有没有空格都行。 | `"300 g"`、`"300g"`、`"300克"`、`"1.5kg"`、`"1.5 公斤"`、`"1 斤"`、`"2 两"`、`"1 L"`、`"500 毫升"`、`"1 tsp"`、`"2汤匙"`、`"3 个"`、`"1 根"`、`"3 cloves"` 和 `"1 罐"`，不传 `default_unit`。 | 三次 `300 G`，两次 `3/2 KG`，然后是 `1 JIN`、`2 LIANG`、`1 L`、`500 ML`、`1 TSP`、`2 TBSP`、`3 PIECE`、`1 STALK`、`3 CLOVE` 和 `1 CAN`。 |
| F01-T12 | 单元 | `parse_quantity` | 小数被读成精确的分数。 | `"0.25 tsp"`、`"0.1 g"`、`"1.50 kg"`、`"1.005 kg"`、`"10.0 ml"` 和 `"0.5 个"`。 | `1/4 TSP`、`1/10 G`、`3/2 KG`、`201/200 KG`、`10 ML` 和 `1/2 PIECE`。`"0.1 g"` 的数值等于 `Fraction(1, 10)`，不等于 `Fraction(0.1)`。 |
| F01-T13 | 单元 | `parse_quantity` | 两端和单位前面的空白不影响结果。 | `" 300 g "`、`"　300 g　"`、`"300   g"`、`"300\tg"`、`"3　个"` 和 `"\n1 斤\n"`。 | 四次 `300 G`，然后是 `3 PIECE` 和 `1 JIN`。 |
| F01-T14 | 单元 | `parse_quantity` | 两种语言的“适量”。 | `"适量"`、`" 适量 "`、`"　适量"`、`"to taste"`、`"To taste"`、`"TO TASTE"`、`"tO tAsTe"`、`"To  taste"`、`"to\ttaste"`、`"to　taste"` 和 `" to taste "`，每个都分别不传 `default_unit` 和传 `Unit.PIECE`。 | 每个都得到 `TO_TASTE`。 |
| F01-T15 | 单元 | `parse_quantity` | 没写单位的数字使用默认单位。 | `"3"` 配 `Unit.PIECE`，`"300"` 配 `Unit.G`，`"1.5"` 配 `Unit.KG`，`"0.5"` 配 `Unit.PIECE`。 | `3 PIECE`、`300 G`、`3/2 KG` 和 `1/2 PIECE`。 |
| F01-T16 | 单元 | `parse_quantity` | 文字里的单位优先于默认单位，并且保持原样。 | `"2 tbsp"` 配 `Unit.PIECE`，`"300 g"` 配 `Unit.PIECE`，`"1 斤"` 配 `Unit.G`，`"3 瓣"` 配 `Unit.STALK`。 | `2 TBSP`、`300 G`、`1 JIN` 和 `3 CLOVE`。 |
| F01-T17 | 单元 | `parse_quantity` | 为空或只有空白的文字是 `EMPTY`。 | `""`、`" "`、`"\t\n"`、`"　"` 和 `"　 　"`，每个都分别不传 `default_unit` 和传 `Unit.PIECE`。 | 每个都得到 `EMPTY("")`。 |
| F01-T18 | 单元 | `parse_quantity` | 缺少数字，或者数字不是由 ASCII 数字组成的十进制数，是 `NOT_A_NUMBER`。 | `"a few"`、`"g"`、`"1/2 tsp"`、`"1,5 g"`、`"-1 g"`、`"+1 g"`、`"½ tsp"`、带全角数字的 `"３ 个"`、带阿拉伯-印度数字 U+0663 的 `"٣ g"`、`"三 个"`、`".5 g"`、`"1. g"`、`"1.2.3 g"`、`"1_000 g"`、`"1-2 个"`、`"to tastes"` 和 `"to-taste"`，不传 `default_unit`。另有 `" a few "` 配 `Unit.PIECE`。 | 以输入本身为文字的 `NOT_A_NUMBER`，比如 `NOT_A_NUMBER("1/2 tsp")`。`" a few "` 得到 `NOT_A_NUMBER("a few")`。 |
| F01-T19 | 单元 | `parse_quantity` | 不是任何写法的单位是 `UNKNOWN_UNIT`，结果里存放原样写出的单位。 | `"1 cups"`、`" 1 cups "`、`"2 Cups"`、`"1   cup"`、`"300 gs"`、`"1 适量"`、`"1 to taste"` 和 `"2 茶 匙"`，不传 `default_unit`。另有 `"1 cups"` 配 `Unit.PIECE`。 | `UNKNOWN_UNIT("1 cups", "cups")`、`UNKNOWN_UNIT("1 cups", "cups")`、`UNKNOWN_UNIT("2 Cups", "Cups")`、`UNKNOWN_UNIT("1   cup", "cup")`、`UNKNOWN_UNIT("300 gs", "gs")`、`UNKNOWN_UNIT("1 适量", "适量")`、`UNKNOWN_UNIT("1 to taste", "to taste")`、`UNKNOWN_UNIT("2 茶 匙", "茶 匙")` 和 `UNKNOWN_UNIT("1 cups", "cups")`。 |
| F01-T20 | 单元 | `parse_quantity` | 数字没有单位，也没有默认单位，是 `NO_UNIT`。 | `"3"`、`"1.5"`、`" 3 "` 和 `"　3"`，不传 `default_unit`。 | `NO_UNIT("3")`、`NO_UNIT("1.5")`、`NO_UNIT("3")` 和 `NO_UNIT("3")`。 |
| F01-T21 | 单元 | `parse_quantity` | 等于 0 的数字是 `ZERO`。 | `"0 g"`、`"0.00 个"`、`"00 kg"` 和 `"0.0kg"`，不传 `default_unit`。另有 `"0"` 配 `Unit.PIECE`。 | `ZERO("0 g")`、`ZERO("0.00 个")`、`ZERO("00 kg")`、`ZERO("0.0kg")` 和 `ZERO("0")`。 |
| F01-T22 | 单元 | `parse_quantity` | 同时符合几条原因时，以设计 2.7 表中靠前的一条为准。 | `"0 cups"` 分别不传 `default_unit` 和传 `Unit.PIECE`，`"0"` 不传 `default_unit`，以及 `"-0 g"` 和 `"a cups"`。另有数字为 16 位的 `"1234567890123456 cups"`、不传 `default_unit` 的 `"1234567890123456"`，以及 `"0" * 16 + " g"`。 | 两次 `UNKNOWN_UNIT("0 cups", "cups")`，然后是 `NO_UNIT("0")`、`NOT_A_NUMBER("-0 g")` 和 `NOT_A_NUMBER("a cups")`。三个带 16 位数字的文字都得到以输入本身为文字的 `NOT_A_NUMBER`，而不是 `UNKNOWN_UNIT`、`NO_UNIT` 或 `ZERO`。 |
| F01-T23 | 单元 | `parse_quantity` | “to taste”的两个词之间至少要有一个空白字符。 | `"totaste"` 和 `"TOTASTE"`，每个都分别不传 `default_unit` 和传 `Unit.PIECE`。 | 无论传不传默认单位，都得到 `NOT_A_NUMBER("totaste")` 和 `NOT_A_NUMBER("TOTASTE")`。 |
| F01-T24 | 单元 | `parse_quantity` | 数字最多 15 位。小数点不算，每一位数字都算，开头和末尾的 0 也算。更长的数字是 `NOT_A_NUMBER`，即使长到 Python 的 `int` 读不了也是这样，而且没有调用抛异常。 | 不传 `default_unit`：数字为 15 位的 `"123456789012345 g"`、`"12345678901234.5 g"`、`"0" * 14 + "1 g"`、`"1." + "0" * 14 + " g"` 和 `"0." + "0" * 13 + "1 g"`，数字为 16 位的 `"1234567890123456 g"`、`"0" * 15 + "1 g"`、`"1." + "0" * 15 + " g"` 和 `"0.000000000000001 g"`，以及 `"1" * 5000 + " g"`。传 `Unit.PIECE`：`"123456789012345"` 和 `"1234567890123456"`。 | `123456789012345 G`、`24691357802469/2 G`、`1 G`、`1 G` 和 `Quantity(Fraction(1, 10**14), Unit.G)`。不传 `default_unit` 的另外五个文字都得到以输入本身为文字的 `NOT_A_NUMBER`，比如 `NOT_A_NUMBER("1234567890123456 g")`。传 `Unit.PIECE` 时得到 `123456789012345 PIECE` 和 `NOT_A_NUMBER("1234567890123456")`。每次调用都不抛异常。 |
| F01-T25 | 单元 | `Quantity.in_base_unit` | 质量精确地换算成克，体积精确地换算成毫升。 | `2 KG`、`1 JIN`、`3 LIANG`、`7 G`、`3/2 KG`、`1/3 KG`、`2 L`、`3 TSP`、`2 TBSP`、`7 ML` 和 `1/3 TSP`。 | `2000 G`、`500 G`、`150 G`、`7 G`、`1500 G`、`1000/3 G`、`2000 ML`、`15 ML`、`30 ML`、`7 ML` 和 `5/3 ML`。 |
| F01-T26 | 单元 | `Quantity.in_base_unit` | 计数和“适量”保持原样。 | `3 CLOVE`、`1/2 PIECE`、`1 PACK` 和 `TO_TASTE`。 | `3 CLOVE`、`1/2 PIECE`、`1 PACK` 和 `TO_TASTE`。 |
| F01-T27 | 单元 | `Quantity`、`Quantity.in_base_unit` | 单位不同的数量不相等，用 `in_base_unit` 比较它们的大小。 | 三对数量：`1 KG` 和 `1000 G`，`1 JIN` 和 `10 LIANG`，`1 TBSP` 和 `3 TSP`。 | 每对的两个数量不相等，它们 `in_base_unit` 的结果相等。 |
| F01-T28 | 单元 | `Quantity.scale` | 换算精确地乘以数值，单位保持不变。 | `2 TBSP` 乘以 `Fraction(4, 2)`，`3 PIECE` 乘以 `Fraction(3, 2)`，`1 JIN` 乘以 `Fraction(2)`，`300 G` 乘以 `Fraction(3, 2)`，`300 G` 乘以 `Fraction(1, 2)`，`1 PIECE` 乘以 `Fraction(1, 3)`，`3/2 KG` 乘以 `Fraction(2, 3)`。 | `4 TBSP`、`9/2 PIECE`、`2 JIN`、`450 G`、`150 G`、`1/3 PIECE` 和 `1 KG`。 |
| F01-T29 | 单元 | `Quantity.scale` | “适量”换算后仍是“适量”。 | `TO_TASTE` 分别乘以 `Fraction(2)` 和 `Fraction(1, 2)`。 | 两次都得到 `TO_TASTE`。 |
| F01-T30 | 单元 | `Quantity.scale` | 系数不是 `Fraction`，属于错误的调用。 | `2 TBSP` 和 `TO_TASTE`，各自乘以 `2`、`2.0`、`"2"` 和 `Decimal("2")`。 | 每次调用都抛出 `TypeError`。 |
| F01-T31 | 单元 | `Quantity.scale` | 系数小于或等于 0，属于错误的调用，对“适量”也是这样。 | `2 TBSP` 和 `TO_TASTE`，各自乘以 `Fraction(0)`、`Fraction(-1)` 和 `Fraction(-1, 2)`。 | 每次调用都抛出 `ValueError`。 |
| F01-T32 | 单元 | `add_quantities` | 无论用哪个单位，质量都按克相加，体积都按毫升相加。 | `[1 KG, 1 JIN, 1 LIANG, 1 G]`、`[1 L, 1 TSP, 1 TBSP, 1 ML]`、`[1 KG]` 和 `[1 TBSP]`。 | `(1551 G,)`、`(1021 ML,)`、`(1000 G,)` 和 `(15 ML,)`。 |
| F01-T33 | 单元 | `add_quantities` | 每种计数单位各自相加，不与质量、体积或其他计数单位合并。 | `[2 STALK, 1 STALK, 1 BUNCH, 3 PIECE, 2 PIECE]` 和 `[2 PIECE, 100 G, 1 TBSP]`。 | `(3 STALK, 1 BUNCH, 5 PIECE)` 和 `(2 PIECE, 100 G, 15 ML)`。 |
| F01-T34 | 单元 | `add_quantities` | 各总量按其组第一次出现的顺序排列。 | `[2 TBSP, 10 G]`、`[10 G, 2 TBSP]` 和 `[1 BUNCH, 10 G, 2 TBSP, 1 STALK, 5 G, 1 ML, 1 BUNCH]`。 | `(30 ML, 10 G)`、`(10 G, 30 ML)` 和 `(2 BUNCH, 15 G, 31 ML, 1 STALK)`。 |
| F01-T35 | 单元 | `add_quantities` | “适量”不加任何东西，没有数值就没有总量。 | `[TO_TASTE, 2 TBSP, TO_TASTE]`、`[TO_TASTE, TO_TASTE]`、`[TO_TASTE]` 和 `[]`。 | `(30 ML,)`、`()`、`()` 和 `()`。 |
| F01-T36 | 单元 | `add_quantities` | 总量精确，不取整。 | `[1/3 G, 1/3 G]`、`[1/10 KG, 1/10 KG, 1/10 KG]`、`[1/2 PIECE, 1/3 PIECE]` 和 `[1/3 TSP, 1/3 TSP]`。 | `(2/3 G,)`、`(300 G,)`、`(5/6 PIECE,)` 和 `(10/3 ML,)`。 |
| F01-T37 | 单元 | `add_quantities` | 任何可迭代对象都行，包括生成器。 | 依次产出 `1 JIN` 和 `2 JIN` 的生成器，以及元组 `(1 JIN, 2 JIN)`。 | 都得到 `(1500 G,)`。 |
| F01-T38 | 单元 | `Quantity.to_text` | 数量用它自己的单位写成数值、一个空格和单位的名称。 | 英文：`1 STALK`、`3 PIECE`、`1 JIN`、`2 JIN`、`2 LIANG`、`1500 G`、`2 TBSP` 和 `1 L`。中文：`2 TSP`、`600 G`、`3 PIECE`、`1 JIN`、`2 LIANG` 和 `1 L`。 | `"1 stalk"`、`"3 pieces"`、`"1 jin"`、`"2 jin"`、`"2 liang"`、`"1500 g"`、`"2 tbsp"` 和 `"1 L"`。然后是 `"2 茶匙"`、`"600 g"`、`"3 个"`、`"1 斤"`、`"2 两"` 和 `"1 L"`。 |
| F01-T39 | 单元 | `Quantity.to_text` | 数值向上取整到最多两位小数，不写末尾的 0，也不写千位分隔符。 | 英文：`4/3 TBSP`、`1/3 G`、`2/3 G`、`9/2 PIECE`、`5/2 G`、`21/10 G`、`201/100 G`、`1/1000 G`、`1/200 G` 和 `12345 G`。中文：`9/2 PIECE`。 | `"1.34 tbsp"`、`"0.34 g"`、`"0.67 g"`、`"4.5 pieces"`、`"2.5 g"`、`"2.1 g"`、`"2.01 g"`、`"0.01 g"`、`"0.01 g"` 和 `"12345 g"`。然后是 `"4.5 个"`。 |
| F01-T40 | 单元 | `Quantity.to_text` | 在 `float` 运算会多进一位的地方，向上取整依然精确（ADR-0007）。 | 英文：`7/100 G`、`7/50 G` 和 `11/10 KG`。 | `"0.07 g"`、`"0.14 g"` 和 `"1.1 kg"`。用 `float` 算，0.07 × 100 是 7.000000000000001，向上取整就成了 0.08。 |
| F01-T41 | 单元 | `Quantity.to_text` | 英文里，除非写出的数值是 `1`，名称都用复数。 | 英文：`1 PIECE`、`999/1000 PIECE`、`1001/1000 PIECE`、`1/2 PIECE` 和 `2 PIECE`。中文：`2 PIECE`。 | `"1 piece"`、`"1 piece"`、`"1.01 pieces"`、`"0.5 pieces"` 和 `"2 pieces"`。然后是 `"2 个"`。 |
| F01-T42 | 单元 | `Quantity.to_text` | 两种语言的“适量”。 | `TO_TASTE`，分别用英文和中文。 | `"to taste"` 和 `"适量"`。 |
| F01-T43 | 单元 | `Quantity.to_rounded_text` | 两种语言的“适量”。 | `TO_TASTE`，分别用英文和中文。 | `"to taste"` 和 `"适量"`。 |
| F01-T44 | 单元 | `Quantity.to_rounded_text` | 不到 1000 时，质量用克写出，体积用毫升写出，向上取整到整数。 | 英文：`1 JIN`、`2 LIANG`、`1/3 TSP`、`1/10 G`、`2/3 KG`、`999 G` 和 `999 ML`。中文：`1 TBSP` 和 `600 G`。 | `"500 g"`、`"100 g"`、`"2 ml"`、`"1 g"`、`"667 g"`、`"999 g"` 和 `"999 ml"`。然后是 `"15 ml"` 和 `"600 g"`。 |
| F01-T45 | 单元 | `Quantity.to_rounded_text` | 1000 g 及以上用 kg 写出，1000 ml 及以上用 L 写出，向上取整到最多两位小数。克数和毫升数先向上取整，再和 1000 比较。 | 英文：`1500 G`、`1001 G`、`1999 G`、`1999/2 G`、`2 JIN`、`12345 G`、`1234567 G`、`1 L`、`67 TBSP` 和 `3/2 L`。中文：`1000 G` 和 `1500 ML`。 | `"1.5 kg"`、`"1.01 kg"`、`"2 kg"`、`"1 kg"`、`"1 kg"`、`"12.35 kg"`、`"1234.57 kg"`、`"1 L"`、`"1.01 L"` 和 `"1.5 L"`。然后是 `"1 kg"` 和 `"1.5 L"`。 |
| F01-T46 | 单元 | `Quantity.to_rounded_text` | 计数向上取整到整数，单位保持不变。英文里，除非数字是 1，名称都用复数。 | 英文：`3/2 STALK`、`9/2 PIECE`、`1/3 PIECE`、`1 BLOCK` 和 `1000 PIECE`。中文：`5 STALK` 和 `2 CAN`。 | `"2 stalks"`、`"5 pieces"`、`"1 piece"`、`"1 block"` 和 `"1000 pieces"`。然后是 `"5 根"` 和 `"2 罐"`。 |
| F01-T47 | 单元 | `Quantity.to_rounded_text` | 在 `float` 运算会多进一位的地方，向上取整依然精确（ADR-0007）。 | 英文：`1100 G`、`1090 G`、`11/10 KG` 和 `403/100 KG`。 | `"1.1 kg"`、`"1.09 kg"`、`"1.1 kg"` 和 `"4.03 kg"`。用 `float` 算，1100 / 1000 × 100 是 110.00000000000001，向上取整就成了 1.11 kg。 |
| F01-T48 | 集成 | `parse_quantity`、`Quantity.to_text` | F09“Show one recipe”和“A missing language”两节的菜谱用英文读取并写出数量。 | `tomato-egg`：`"300 g"`、`"3"` 配 `Unit.PIECE`、`"1 根"`、`"适量"`、`"1 tsp"` 和 `"2 tbsp"`。`red-braised-pork`：`"1 斤"`、`"30 g"`、`"2 tbsp"`、`"3 片"` 和 `"2 根"`。每个都用 `parse_quantity` 读取，用 `to_text(Lang.EN)` 写出。 | `"300 g"`、`"3 pieces"`、`"1 stalk"`、`"to taste"`、`"1 tsp"` 和 `"2 tbsp"`。然后是 `"1 jin"`、`"30 g"`、`"2 tbsp"`、`"3 slices"` 和 `"2 stalks"`。 |
| F01-T49 | 集成 | `parse_quantity`、`Quantity.scale`、`Quantity.to_text` | F09“Show one recipe for 4 servings, in Chinese”一节把 `tomato-egg` 换算后，用菜谱自己的单位写出。 | F01-T48 里 `tomato-egg` 的六个数量，每个都读取，按 4 份换算，再用 `to_text(Lang.ZH)` 写出。 | `"600 g"`、`"6 个"`、`"2 根"`、`"适量"`、`"2 茶匙"` 和 `"4 汤匙"`。 |
| F01-T50 | 集成 | `parse_quantity`、`Quantity.scale`、`add_quantities`、`Quantity.to_rounded_text` | `2026-W47` 这一周加起来，得到 F13“In English”和“In Chinese”两节里的各行。 | F13“How the example adds up”一节里的数量，每个都读取、换算，再按食材相加。番茄：两次 `"300 g"`，按 2 份。菜心：`"1 斤"` 按 2 份和按 4 份各一次。葱：`"1 根"` 按 2 份三次，按 4 份一次。姜：`"3 片"` 按 4 份。大蒜：`"3 瓣"` 按 2 份和按 4 份各一次，`"2 瓣"` 按 2 份。猪肉末：`"100 g"` 按 2 份。鸡翅中：`"500 g"` 按 4 份。鸡蛋：`"3"` 和 `"2"` 配 `Unit.PIECE`，按 2 份。豆腐：`"1 块"` 按 2 份。大米：`"160 g"` 按 2 份两次，按 4 份一次。面条：`"200 g"` 按 2 份。郫县豆瓣酱：`"1 tbsp"` 按 2 份。白胡椒粉：`"适量"` 按 2 份。可乐：`"1 罐"` 按 4 份。每个总量都用 `to_rounded_text` 分别以英文和中文写出。 | 每种食材都有一个总量，只有白胡椒粉的 `add_quantities` 结果是 `()`。英文按上面的顺序依次是 `"600 g"`、`"1.5 kg"`、`"5 stalks"`、`"6 slices"`、`"11 cloves"`、`"100 g"`、`"1 kg"`、`"5 pieces"`、`"1 block"`、`"640 g"`、`"200 g"`、`"15 ml"` 和 `"2 cans"`。中文依次是 `"600 g"`、`"1.5 kg"`、`"5 根"`、`"6 片"`、`"11 瓣"`、`"100 g"`、`"1 kg"`、`"5 个"`、`"1 块"`、`"640 g"`、`"200 g"`、`"15 ml"` 和 `"2 罐"`。 |
| F01-T51 | 集成 | `parse_quantity`、`Quantity.scale`、`add_quantities`、`Quantity.to_rounded_text` | 不能相加的数量并列在一起，与 F13“Quantities that cannot be added”一节和 v0.1-S18 一致。 | v0.1-S18 里 `2026-W48` 的各顿晚餐，全部按 2 份。葱：先是 `"2 根"`，然后三次 `"1 根"`，最后是 `"1 把"`。生抽：先是 `"2 tbsp"`，然后是 `"10 g"`。 | 葱加起来是 `(5 STALK, 1 BUNCH)`，英文写成 `"5 stalks"` 和 `"1 bunch"`，中文写成 `"5 根"` 和 `"1 把"`。生抽加起来是 `(30 ML, 10 G)`，两种语言都写成 `"30 ml"` 和 `"10 g"`。 |
| F01-T52 | 集成 | `parse_quantity`、`Quantity.scale`、`add_quantities`、`Quantity.to_rounded_text` | 2 份的菜谱做 3 份，与 v0.1-S16 一致，向上取整到要买的量。 | `tomato-egg` 的 `"300 g"`、`"3"` 配 `Unit.PIECE` 和 `"1 根"`，每个都读取，乘以 `Fraction(3, 2)`，单独相加，再用英文写出。 | `"450 g"`、`"5 pieces"` 和 `"2 stalks"`。 |
| F01-T53 | 集成 | `parse_quantity`、`add_quantities`、`Quantity.to_rounded_text` | 从文字到写出的总量，数值始终精确（ADR-0007）。 | 三次 `"0.1 kg"`，读取、相加，再用英文写出。另有 `"1.1 kg"`，读取后用英文写出。 | `(300 G,)`，写成 `"300 g"`。用 `float` 算，0.1 + 0.1 + 0.1 kg 是 300.00000000000006 g，向上取整就成了 301 g。`"1.1 kg"` 写成 `"1.1 kg"`。 |
| F01-T54 | 单元 | `Quantity.to_text` | 小数点前有 4,300 位的数值会完整写出，小数部分不算进上限。 | 英文：`Quantity(Fraction(10**4300 - 1), Unit.G)` 和 `Quantity(Fraction(2 * 10**4300 - 1, 2), Unit.G)`。 | `"9" * 4300 + " g"` 和 `"9" * 4300 + ".5 g"`。两次调用都不抛异常。 |
| F01-T55 | 单元 | `Quantity.to_text` | 取整后的数值在小数点前超过 4,300 位，属于错误的调用。 | 有 4,301 位的 `Quantity(Fraction(10**4300), Unit.G)`，以及有 4,300 位、但向上取整后变成 `10**4300` 的 `Quantity(Fraction(10**4303 - 1, 1000), Unit.G)`，每个都分别用英文和中文。 | 每次调用都抛出 `ValueError`。 |
| F01-T56 | 单元 | `Quantity.to_rounded_text` | 上限数的是 `to_rounded_text` 写出的数值的位数，也就是把 g 换成 kg、把 ml 换成 L 之后的数值。小数点前有 4,300 位的数值会完整写出。 | 英文：`Quantity(Fraction(10**4300), Unit.G)`、`Quantity(Fraction(10**4303 - 500), Unit.G)`、`Quantity(Fraction(10**4303 - 1000), Unit.ML)` 和 `Quantity(Fraction(10**4300 - 1), Unit.PIECE)`。 | `"1" + "0" * 4297 + " kg"`、`"9" * 4300 + ".5 kg"`、`"9" * 4300 + " L"` 和 `"9" * 4300 + " pieces"`。每次调用都不抛异常，尽管 `to_text` 对第一个数量会抛异常（F01-T55）。 |
| F01-T57 | 单元 | `Quantity.to_rounded_text` | `to_rounded_text` 要写出的数值在小数点前超过 4,300 位，属于错误的调用。 | `Quantity(Fraction(10**4303), Unit.G)`、`Quantity(Fraction(10**4303 - 1), Unit.G)`、`Quantity(Fraction(10**4303), Unit.ML)`、`Quantity(Fraction(10**4300), Unit.PIECE)` 和 `Quantity(Fraction(2 * 10**4300 - 1, 2), Unit.PIECE)`，每个都分别用英文和中文。 | 每次调用都抛出 `ValueError`。前三个换成 kg 或 L 并向上取整后是 `10**4300`，两个计数向上取整后也是 `10**4300`。 |

## 3. 性能用例

无。设计里没有接口带性能指标（R14）。

## 4. 不测的内容

| 内容 | 原因 |
| --- | --- |
| `Lang`：`Lang(value)`、它的两个成员、成员的顺序，以及 `"fr"` 或 `"EN"` 这类代码引发的 `ValueError`。 | `Lang` 是没有自己代码的 `StrEnum`，mock 会完整声明它，所以测它的测试对着 mock 会通过，而 R09 不允许这样。F01-T02 和 F01-T38 到 F01-T57 把 `Lang.EN` 和 `Lang.ZH` 传给需要语言的接口。v0.1-S19 运行 `recipe-menu list --lang fr`，预期退出码为 2。 |
| `WrongQuantity` 的字段、`unit` 的默认值、相等比较和不可变性，以及 `WrongQuantityReason` 的值。 | mock 以冻结的 dataclass 和枚举完整声明它们，所以单独测它们的测试对着 mock 会通过（R09）。F01-T17 到 F01-T22 把 `parse_quantity` 的每个结果和完整的 `WrongQuantity` 比较，字段或相等比较出错都会让它们失败。 |
| `Quantity` 的相等比较、哈希和不可变性。 | 设计签名里的 `@dataclass(frozen=True, slots=True)` 提供了这些，mock 也声明了它，所以单独测它们的测试对着 mock 会通过（R09）。大多数用例用 `==` 比较完整的数量，F01-T27 检查 `1 KG` 和 `1000 G` 不相等。 |
| `recipe_menu.lang` 和 `recipe_menu.units` 的 `__all__` 列出的名称。 | mock 完整声明 `__all__`，所以测它的测试对着 mock 会通过（R09）。F03 和 F04 引用这些名称后，严格模式的 mypy 会检查这些导出（架构 8）。每个测试都从这两个模块引用它用的名称。 |
| `units` 在包内只引用 `lang`。 | R07。CI 里的依赖检查器把每个引用和架构 3 的表比较。 |
| 没有接口打印、读文件或保存状态。 | ruff 的 `T20` 规则禁止 `print()`，只有 `datafile` 打开数据文件（架构 8），代码评审检查模块级的状态。测试只能说明它做的那些调用没有打印。 |
| `int` 位数的上限不是默认的 4,300 位时，比如由 `PYTHONINTMAXSTRDIGITS` 设置时，`parse_quantity`、`to_text` 和 `to_rounded_text` 的行为。 | 设计 2.11 和 2.12 给出的是默认设置下的上限，架构师的评审也说明测试用默认设置，所以这些用例会设置它（第 2 节）。只有错误的调用才会让 `to_text` 或 `to_rounded_text` 碰到上限。`parse_quantity` 最多读 15 位，低于 `sys.set_int_max_str_digits` 接受的最低上限 640，所以无论怎样设置，它的结果都不变。 |

## 5. 与接口设计师的对齐记录

| 轮次 | 问题 | 回答 |
| --- | --- | --- |
| 1 | 问题 1，对应 F01-T23。设计 2.7 第 2 步接受 `to taste`，“两个词之间可以是任意空白”。“任意空白”是否包括没有空白，使 `"totaste"` 得到 `TO_TASTE`？(a) 不包括。两个词之间至少要有一个空白字符，所以 `"totaste"` 以字母开头，是 `NOT_A_NUMBER`。(b) 包括。`"totaste"` 得到 `TO_TASTE`。本方案推荐 (a)：这一步说的是两个词，而且没有别的不带空格的文字会成为“适量”。 | (a)。“任意空白”指一个或多个任意种类的空白字符，至少要有一个，因为这一步说的是两个词。`"totaste"` 和 `"TOTASTE"` 以空的数字进入第 3 步，得到 `NOT_A_NUMBER("totaste")` 和 `NOT_A_NUMBER("TOTASTE")`。设计不需要为此修改。版本 1.1 把第 2 步改写为“两个词之间是一个或多个空白字符”，让意思更清楚。F01-T23 按这个回答确定。 |
| 1 | 问题 2，对应 F01-T24。设计 2.7 说 `parse_quantity` 从不抛异常，数字是一个或多个 ASCII 数字，没有上限。Python 的 `int` 和 `Fraction` 读取超过 4,300 位的数字时会抛出 `ValueError`，这是 CPython 的默认上限。`str` 写出这样的整数时也抛出同样的错误。`parse_quantity` 遇到 5,000 位的数字返回什么？(a) 带精确数值的 `Quantity`，即设计现在的写法。这样 `to_text` 和 `to_rounded_text` 也要写出每一位，不抛异常。(b) 超过 15 位（不算小数点）的数字是 `NOT_A_NUMBER`。这样 `parse_quantity` 返回的每个数值都能换算、相加和写出。这要修改设计 2.7。(c) 不设用例，因为没有菜谱会写这样的数字。这样一个 5,000 位的数量可能让 `check` 以 traceback 结束。本方案推荐 (b)：这么长的数字是输入错误，应该由 `check` 报告，而这个上限让后面每一步都远离 Python 的上限。 | (b)。版本 1.0 的写法本意是 (a)。但 (a) 会让 `parse_quantity`、`to_text` 和 `to_rounded_text` 绕开 Python 的上限，只为接受一个只可能是输入错误的数量，(c) 则违反“从不抛异常”和架构 6。所以设计做了修改：PR #7“[docs] Limit amounts to 15 digits in the F01 design”合并了设计版本 1.1，架构师审查并批准了它。2.7 第 3 步把数字限制在最多 15 个 ASCII 数字。小数点不算，每一位数字都算，开头和末尾的 0 也算。`NOT_A_NUMBER` 一行增加了“或者数字超过 15 位”，并且排在 `UNKNOWN_UNIT` 和 `ZERO` 前面。2.11 和 2.12 各增加一个 `ValueError`：取整后的数值在小数点前超过 4,300 位时抛出，只有错误的调用才会碰到。4,300 是实际生效的上限 `sys.get_int_max_str_digits()` 的默认值，测试用的也是默认值。F01-T22 和 F01-T24 按这个回答确定，F01-T54 到 F01-T57 测试新增的 `ValueError` 行。 |

## 6. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-10 | 初稿。 |
| 0.2 | 2026-11-10 | 记录接口设计师对第 1 轮的回答，跟随设计版本 1.1。F01-T23 和 F01-T24 按回答确定，F01-T22 增加 16 位的数字，F01-T54 到 F01-T57 测试 `to_text` 和 `to_rounded_text` 新增的 `ValueError`。 |
| 1.0 | 2026-11-10 | Troy 批准。 |
