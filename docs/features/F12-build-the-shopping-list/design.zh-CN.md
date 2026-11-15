---
troy-doc: "F12-design"
lang: "zh-CN"
version: "1.0"
updated: "2026-11-15"
status: "Troy 已于 2026-11-15 批准"
mirror-of: "design.md"
---

# F12 生成购物清单：接口设计

## 1. 功能

- 编号和名称：F12 生成购物清单
- 需求：[docs/requirements.zh-CN.md](../../requirements.zh-CN.md#4-功能点)
- 硬依赖：无
- 软依赖：F01、F03、F04、F06

## 2. 接口

F12 在 `src/recipe_menu/shopping/` 里构建领域层模块 `shopping`（[架构 3](../../architecture.zh-CN.md#3-模块)）。`recipe_menu.shopping` 导出四个名称：值 `ShoppingLine`（2.1，带方法 `amount_text`，2.2）、`ShoppingGroup`（2.3）和 `ShoppingList`（2.4），以及函数 `build_shopping_list`（2.5）。它的 `__init__.py` 在 `__all__` 里列出这些名称。背后的其他文件由开发工程师决定。F12 没有命令，也没有提示，所以 `shopping` 没有 `messages.py`（架构 8）。F13 的 `shop` 调用 `build_shopping_list`，并把清单写到终端和 Markdown 勾选清单里。F13 原型 `docs/prototypes/F13-shop.md` 展示了这份清单，它的表格“How the example adds up”给出了每一行的来源。

下表把需求的每一部分对应到满足它的接口。编号的规则是[需求 3](../../requirements.zh-CN.md#3-用户如何使用)“购物清单”里的规则。

| 需求的说法 | F12 提供的接口 |
| --- | --- |
| F12 按第 3 节的规则把一个周菜单变成购物清单：换算、合并、相加、去掉常备食材、分组、取整（[需求 4](../../requirements.zh-CN.md#4-功能点)）。 | `build_shopping_list`（2.5）。它接收 `WeekMenu`、菜单的菜谱、`Catalog` 和 `Pantry`，给出 `ShoppingList`（2.4）。 |
| 1. 把每道菜的食材按这道菜的份数除以菜谱的份数换算。 | 2.5 的第 3 步：用 `Fraction(dish.servings, recipe.servings)` 调用 `Quantity.scale`（F01 设计 2.9）。 |
| 2. 把所有菜里同一种目录食材的各行合并成一行。 | 菜单用到的每种食材一个 `ShoppingLine`（2.1）。食材按相等性比较（选择 3）。 |
| 3. 质量按克相加，体积按毫升相加，每种计数单位各自相加。 | `ShoppingLine.amounts`，也就是 F01 的 `add_quantities` 给出的和（F01 设计 2.10）。 |
| 4. 不能相加的数量在同一行里并列显示。 | `amounts` 按选择 4 的顺序为每一类保存一个和，`amount_text` 用 ` + ` 把它们连起来（2.2）。 |
| 5. 某种食材在所有菜里都没有数量时，显示“适量”。 | 空的 `amounts`，`amount_text` 对它给出 `to taste` 或 `适量`（选择 5）。 |
| 6. 去掉常备清单里的食材，并在末尾用一行列出菜单用到的那些常备食材。 | 常备食材没有行，另有 `ShoppingList.pantry_used`（选择 6）。 |
| 7. 按目录里的分类顺序分组。同一分类里，各行按目录里的食材顺序排列。 | `ShoppingList.groups`，一个由 `ShoppingGroup` 值组成的元组（2.3，选择 7）。 |
| 8 和 9. 计数、克数和毫升数都向上取整；1000 g 及以上用 kg 显示，1000 ml 及以上用 L 显示，最多保留两位小数。 | `ShoppingLine.amount_text`（2.2），它用 F01 的 `Quantity.to_rounded_text` 写出每个和（选择 8）。 |
| `ShoppingList` 保存周、餐数和菜数、按目录顺序分好类的各行，以及菜单用到的常备食材（[架构 5.2](../../architecture.zh-CN.md#52-值)）。 | 2.4 的五个字段：`week`、`meal_count`、`dish_count`、`groups` 和 `pantry_used`（选择 1 和 9）。 |

下面每个接口都遵守这些规则：

- `shopping` 在包内只引用 `lang`、`units`、`catalog`、`recipes` 和 `menus`（[架构 3](../../architecture.zh-CN.md#3-模块) 和 [4](../../architecture.zh-CN.md#4-依赖规则)）。它不引用 `settings`，所以从不提到 `Meal`。它遍历 `WeekMenu.slots`，这些餐位本来就按餐次的顺序排列。
- `shopping` 不读文件、不写文件、不打印，不读取外部世界的任何东西，也不保存状态（架构 4 和 8）。它把其他模块读出的值变成清单，所以它的测试不需要文件。
- 每个值都是带 `slots=True` 的冻结 dataclass，其中的集合用元组（架构 8）。每个数量都保持为精确的 `Fraction`（ADR-0007）。
- 对读取函数没有报错时给出的值，`build_shopping_list` 从不抛异常。下面各个“错误”表里的异常都来自错误的调用，也就是 bug（[架构 6](../../architecture.zh-CN.md#6-错误处理)）。
- 文档注释只用英文（R05），troy-check 会拒绝其中的汉字。文档注释用码位 U+9002 U+91CF 指称中文的“适量”，和 `units` 的代码一样。
- F12 的接口都没有性能指标。PT01 计时的是 F13 的 `shop`，它调用一次 `build_shopping_list`（选择 11）。`build_shopping_list` 调用单一用途的内部函数（R04）。

这份设计做了以下选择。2.1 到 2.5 给出它们的规则。

1. **三个值，分组放在值里。** `ShoppingList.groups` 是由 `ShoppingGroup` 值组成的元组，每个有行的分类一个，按目录里的分类顺序排列。一个 `ShoppingGroup` 保存它的 `Category` 和它的 `ShoppingLine` 值，按目录里的食材顺序排列。所以 F13 按元组的顺序写出各个标题和各行，不用排序。架构 5.2 给出了 `ShoppingList` 和 `ShoppingLine`。`ShoppingGroup` 是辅助值，就像 `MealSlot` 之于 `WeekMenu`。每个构造函数都检查它的字段（2.1、2.3 和 2.4），所以 F13 或测试手工构建的值也遵守 `build_shopping_list` 遵守的规则。
2. **输入。** `build_shopping_list(menu, recipes, catalog, pantry)` 接收 `WeekMenu`（F06 设计 2.6）、一个从菜用到的每个菜谱 ID 到它的 `Recipe` 的映射（F04 设计 2.3）、`Catalog` 和 `Pantry`（F03 设计 2.5 和 2.7）。F11 的 `menu show` 把菜单用到的每个菜谱读一次，放进一个字典（F11 设计选择 7），F13 可以传入同样的字典。映射里可以有更多菜谱，F12 不看它们。架构 8 要求值里的集合用元组或 frozenset。这个映射是参数，不是值：F12 只读它，清单里不保留它的任何部分，就像 `add_quantities` 接收任意可迭代对象一样（F01 设计 2.10）。F13 遇到每个读取函数的第一个错误就停下（架构 6），所以 F12 只会收到读取时没有错误的值。错误的调用会抛出 `ValueError`：某道菜用到的 ID 不在映射里，映射把一个菜谱放在了别的 ID 下，或者某个菜谱或常备清单里有不在 `catalog.ingredients` 里的食材（2.5）。
3. **按相等性比较，不按同一对象比较。** F12 用 `==` 和哈希比较食材和分类，从不用 `is`。菜谱和常备清单引用的是目录里的 `Ingredient` 值（架构 5.2），一个目录里没有两个相等的食材，所以同一目录里两个相等的食材就是同一个对象（F03 设计 2.4）。因此对 F13 传入的值，按相等性合并的结果和按同一对象合并完全一样。分类不同：`Catalog` 按相等性检查每个食材的 `category` 是否在 `categories` 里，所以它接受一个相等但属于另一个对象的 `Category`，代码审查员在 F03 的 mock 上指出过这一点。按同一对象分组时，这样的食材不会进入任何分组。按相等性分组时，它进入它所属分类的分组。这样，用代码构建相等值的测试和读取文件的测试得到同一份清单。
4. **各个和的顺序。** `add_quantities` 按各类数量第一次出现的顺序给出它们的和（F01 设计 2.10）。F12 按这个顺序把每种食材换算后的数量交给它：`menu.slots` 里的各个餐位，从周一到周日，同一天里按 `Meal` 的顺序；每个餐位里的菜，按文件里的顺序；每道菜的菜谱里的食材行，按文件里的顺序。两道菜用到的同一个菜谱会给出两次数量，各自按自己那道菜换算。一个菜谱里写了两次的食材会给出两个数量。这个顺序给出原型“Quantities that cannot be added”和 v0.1-S18 里的那两行。在 v0.1-S18 里，周一的 `red-braised-pork` 先给出 葱 2 根 和 生抽 2 tbsp，周五的 `scallion-noodles` 后给出 葱 1 把 和 生抽 10 g。所以葱这一行先是 5 根、后是 1 把，写成 `5 stalks + 1 bunch`。生抽这一行先是 30 ml、后是 10 g，写成 `30 ml + 10 g`（2.5 的示例）。
5. **适量。** 没有一道菜给出数量的食材，比如示例那一周的白胡椒粉，得到一行 `amounts` 为空的行。`amount_text` 把它写成 `to taste` 或 `适量`（2.2）。一种食材在有的菜里有数量、在有的菜里是适量时，这一行只保存那些数量的和，因为适量不加任何东西（F01 设计 2.10）。这时它的文字里没有“适量”，这符合规则 5：“适量”只给在所有菜里都没有数量的食材。所以这一行不会提示另一道菜也适量地用到了这种食材。
6. **常备清单。** `pantry.ingredients` 里的食材没有行，不管它有多少数量。菜单用到它时，它进入 `pantry_used`。菜谱里有某种食材的一行时，不论有数量还是适量，这道菜就算用到了它。所以示例那一周只适量地用到的盐也在 `pantry_used` 里，与原型的常备行和 v0.1-S16 一致。`Pantry` 是没有顺序的集合（F03 设计 2.7），所以 F12 给 `pantry_used` 选择 7 的顺序：先按目录里的分类顺序，再按目录里的食材顺序。示例目录给出 食用油、盐、糖、生抽、花椒，正是原型那一行的顺序。菜单没有用到的常备食材不在 `pantry_used` 里。
7. **分组。** 各个分组按 `catalog.categories` 排列，分组里的各行按 `catalog.ingredients` 排列。目录文件可以把同一分类的食材写在几个地方。F12 照样把它们归到它们的分类下，按它们在文件里的顺序排列。没有行的分类没有分组。这样的分类是菜单没有用到的分类，或者用到的食材都在常备清单里的分类。所以 v0.1-S16 先列出 Vegetables and fruit，再列出 Eggs, dairy, and tofu，没有别的标题。
8. **取整。** `amounts` 保存 `add_quantities` 给出的精确的和，它们没有取整（F01 设计 2.10，ADR-0007）。需求里 F12 那一行说 F12 要取整。`ShoppingLine.amount_text(lang)` 满足这一点。它用 F01 的 `Quantity.to_rounded_text` 写出每个和（F01 设计 2.12），这个方法把克数、毫升数和计数向上取整，并把 1000 g 及以上写成 kg、1000 ml 及以上写成 L，最多保留两位小数。它用 ` + ` 把各个和连起来。这些文字来自 `units`，它的单位名称是普通数据（ADR-0004），而 ` + ` 是不属于任何语言的符号（架构 8）。所以 `shopping` 不需要 `Message`，也不需要 `text`。F01 的设计原本计划由 F13 用 `to_rounded_text` 写出每个和。按这个选择，F13 用 `amount_text` 写出每一行的数量，由 `amount_text` 调用 `to_rounded_text`。取整规则仍然只在一个地方，也就是 `units`，F12 的测试在清单上检查它们。一个和只在整周加完之后取整一次：两道菜各要 1.5 根葱，合起来是 3 根，不是 4 根。这不需要修改需求。F12 满足它自己那一行，F01 也仍然满足它那一行，那一行说 F01“按第 3 节的取整规则用两种语言写出数量”。清单的其他文字都归 F13。
9. **计数。** `meal_count` 是 `menu.slots` 里至少有一道菜的餐位数，`dish_count` 是所有餐位里的菜数。这和 F11 的 `menu show` 的计数（F11 设计选择 9）以及 F06 设计第 2 节的计数相同，所以 `shop` 和 `menu show` 对一周的计数一致：示例那一周是 4 餐、9 道菜，v0.1-S16 是 1 餐、1 道菜。`shopping` 不能引用 `menu`（架构 3），所以它自己从 `menu.slots` 数。一道菜都没有的菜单给出 `ShoppingList(menu.week, 0, 0, (), ())`，这时 `recipes` 可以是空的。`dish_count` 为 0 时，F13 显示原型里的那一行 `The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.`。菜单里的菜只用到常备食材，或者只用到没有食材的菜谱时，得到的清单有菜但没有分组。这时 `shop` 显示和保存什么，由 F13 的设计决定。
10. **数字。** 菜谱里的数量最多 15 位数字（F01 设计 2.7），所以它小于 10^15，它的分母整除 10^14。`in_base_unit` 最多把它乘以 1000（kg 和 L）。份数比例最多是 100，因为一道菜最多 100 份，一个菜谱至少 1 份（F04 设计选择 2）。所以每个换算后的数量小于 10^20，n 个数量的和小于 n 乘以 10^20。`to_rounded_text` 只在超过 4,300 位时抛出 `ValueError`（F01 设计 2.12）。要达到这么大的和，一周里需要约 10^4279 行菜谱，所以对 `build_shopping_list` 给出的行，`amount_text` 从不抛异常。分母也一直很小。每个换算后的数量的分母整除 10^14 乘以一个菜谱的份数，所以每个和的分母整除 10^14 乘以 1 到 100 的最小公倍数，这是一个 55 位的数。
11. **速度。** PT01 要求 `shop` 在 Troy 的电脑上生成并保存一个 PT01 周的清单，在 1 秒内完成，取 5 次运行的中位数（v0.1-S32）。这一周有 63 道菜，来自 63 个不同的菜谱。一个 PT01 菜谱有 12 行食材（v0.1-S29），所以 F12 要换算并相加 756 个数量，并给最多 300 种食材排序。每个数量要做两次 `Fraction` 乘法（一次换算份数，一次在 `in_base_unit` 里）、一次加法和两次按食材查字典，在 CPython 里每样几微秒。排序要把目录的 300 种食材过一遍。所以 `build_shopping_list` 应该约 0.01 秒，`amount_text` 写最多 300 行再多几毫秒。`shop` 读取的是 `menu show` 读取的文件再加上常备清单，而 `menu show` 对同一周在 Troy 的电脑上的中位数是 0.187 秒（F11 的 PT01 基准）。所以 `shop` 应该在 0.2 秒左右，F13 自己的输出和文件还要另算。这些是估计，不是实测。F13 的测试计划可以在 PT01 文件夹上给 `shop` 计时。`build_shopping_list` 只在一次调用里保留它的字典，没有模块保存缓存（架构 8）。

通过 `shop` 用到 F12 的 v0.1 场景在这些选择下成立：

- 原型的表格“How the example adds up”：示例周 2026-W47 的每一行和它的常备行，以及 4 餐、9 道菜（2.5 的示例）。菜心周一 1 斤、周日 2 斤，所以它的和是 1500 g，写成 `1.5 kg`。郫县豆瓣酱是 1 tbsp，所以它的和是 15 ml。白胡椒粉没有数量，所以是 `适量`。
- v0.1-S14：一道菜都没有的菜单给出 `dish_count` 为 0 的清单，`shop` 对它显示那一行，不保存文件（选择 9）。
- v0.1-S16：2 份的 `tomato-egg` 做 3 份，得到 Tomato 450 g、Scallion 3/2 根（写成 `2 stalks`）和 Egg 9/2 个（写成 `5 pieces`），分在两个分组里。清单是 1 餐、1 道菜，常备食材是 食用油、盐、糖（选择 6 到 9）。
- v0.1-S17 和 v0.1-S26：示例周的 14 行，分在六个分组里，以及常备行。
- v0.1-S18：`5 stalks + 1 bunch` 和 `30 ml + 10 g`，中文是 `5 根 + 1 把`（选择 4）。
- v0.1-S32：PT01（选择 11）。

这份设计没有留给 Troy 决定的事。常备行的文字、各个标题、计数行和 Markdown 文件都归 F13，由 F13 的设计把其中待定的事交给 Troy。

以下后续功能打算在 F12 的基础上构建。细节由它们自己的设计决定。

- F13 的 `shop` 像 `menu show` 那样读取它的文件（F11 设计选择 7），在目录之后用 `read_pantry(context.folder, catalog)` 读取常备清单，并在每个读取函数的第一个错误处停下。它在一次运行里把菜单用到的每个菜谱保存在字典里，然后调用 `build_shopping_list(menu, recipes, catalog, pantry)`。
- `dish_count` 为 0 时，F13 显示它给没有菜的周准备的那一行。对有菜但没有分组的清单，`shop` 显示和保存什么由 F13 决定（选择 9）。
- F13 用 `group.category.name.get(lang)` 写出每个分组的标题，用 `line.ingredient.name.get(lang)` 和 `line.amount_text(lang)` 写出每一行，用 `meal_count` 和 `dish_count` 写出计数。它在终端和 Markdown 勾选清单里写出同样的值。
- F13 根据 `pantry_used` 确定常备行的文字。F03 的设计指出，原型的英文常备行写的是“cooking oil”，而目录里写的是“Cooking oil”，这一行要由 F13 的设计来确定（F03 设计第 2 节）。
- 架构师在 F02 的审查里建议，F13 可以把清单排成一张 `format_table` 表格，把分类标题放在各行之间。F11 实现的代码审查员指出，读取目录并在第一个错误处停下的代码在 `browse`、`search` 和 `menu` 里重复，F13 的设计可以把它们共用起来。这两件事都由 F13 决定。

troy-mode 的流程有一个 mock PR 和一个实现 PR。mock（PR 3）包含 `src/recipe_menu/shopping/__init__.py`，它导入这四个名称并在 `__all__` 里列出它们，以及两个内部文件，比如放三个值的 `_model.py` 和放 `build_shopping_list` 的 `_build.py`。它定义三个值的字段和文档注释，但不做构造函数的检查。它的 `amount_text` 和 `build_shopping_list` 抛出 `NotImplementedError`。所以新测试调用 `build_shopping_list` 或 `amount_text` 时在 mock 上会失败（R09），期望得到 `ValueError` 或期望一道菜都没有的菜单得到空清单时也会失败。期望构造函数抛异常的测试在 mock 上也会失败。测试错误调用时要期望 `ValueError` 或 `TypeError`，不能接受任意异常，因为 mock 抛的是 `NotImplementedError`。下面这些测试在 mock 上会通过，从而违反 R09：只检查模块的名称的测试，或者只检查一个合法值的字段和相等性的测试，比如 `ShoppingList(week, 0, 0, (), ())`。每个这样的测试都还要检查 mock 做错的内容。按估计，mock 改动 3 个文件，约 200 行，在 R03 以内。实现（PR 5）把检查和 `amount_text` 加到 `_model.py`，把 `build_shopping_list` 和它的内部函数加到 `_build.py`，或者再加一个内部文件。按估计，它改动 2 到 3 个文件，约 300 行，也在 R03 以内。所以两个 PR 都不需要写软限制的理由。

### 2.1 `ShoppingLine`

- 模块：shopping
- 功能：购物清单的一行：一种目录食材和它这一周的各个和（[架构 5.2](../../architecture.zh-CN.md#52-值)）。`amounts` 为每一类不能互相相加的数量保存一个和：克、毫升和每种计数单位。`amounts` 为空表示“适量”。

签名：

```python
@dataclass(frozen=True, slots=True)
class ShoppingLine:
    ingredient: Ingredient
    amounts: tuple[Quantity, ...]

    # Method: amount_text (2.2).
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `ingredient` | `Ingredient` | 目录里的食材，比如 Scallion 和 葱。 | 无 |
| `amounts` | 由 `Quantity` 值组成的元组 | 这一周的精确的和，就是 `add_quantities` 给出的那些，比如 5 根和 1 把。 | 每个数量都有数值，所以没有适量。每个单位是 `Unit.G`、`Unit.ML` 或一种计数单位，没有两个数量的单位相同。适量时为空。 |

- 返回值：一个 `ShoppingLine`。两个字段都相等时，两行相等。`ShoppingLine` 可哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `ingredient` 不是 `Ingredient`，或者 `amounts` 不是元组，或者其中有不是 `Quantity` 的项。 |
| `ValueError` | `amounts` 里有一个数量是适量，或者它的单位不是 `Unit.G`、`Unit.ML` 和计数单位，比如 `Unit.KG` 或 `Unit.TBSP`，或者它和 `amounts` 里另一个数量的单位相同。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.shopping import ShoppingLine
from recipe_menu.units import TO_TASTE, Quantity, Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
soy_sauce = Ingredient(BiText("Soy sauce", "生抽"), seasonings)
white_pepper = Ingredient(BiText("White pepper", "白胡椒粉"), seasonings)
stalks = Quantity(Fraction(5), Unit.STALK)
bunch = Quantity(Fraction(1), Unit.BUNCH)
grams = Quantity(Fraction(10), Unit.G)

line = ShoppingLine(scallion, (stalks, bunch))
assert line.ingredient is scallion
assert line.amounts == (stalks, bunch)
assert line == ShoppingLine(scallion, (stalks, bunch))
assert ShoppingLine(white_pepper, ()).amounts == ()
soy = ShoppingLine(soy_sauce, (Quantity(Fraction(30), Unit.ML), grams))
assert soy.amounts[1].unit is Unit.G

ShoppingLine(soy_sauce, (Quantity(Fraction(2), Unit.TBSP),))  # raises ValueError
ShoppingLine(soy_sauce, (grams, grams))  # raises ValueError
ShoppingLine(white_pepper, (TO_TASTE,))  # raises ValueError
ShoppingLine(scallion, [stalks, bunch])  # raises TypeError
ShoppingLine("Scallion", (stalks,))  # raises TypeError
```

### 2.2 `ShoppingLine.amount_text`

- 模块：shopping，`ShoppingLine` 的方法（2.1）
- 功能：按购物清单的规则写出这一行的数量：并列显示（规则 4）、“适量”（规则 5）、向上取整（规则 8），以及从 1000 g 或 1000 ml 起用 kg 或 L（规则 9）。F13 把这段文字写在食材名称后面，终端和 Markdown 勾选清单里都是这样（选择 8）。

签名：

```python
def amount_text(self, lang: Lang) -> str: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `lang` | `Lang` | 用哪种语言写。 | 无 |

- 返回值：按这些规则写出的文字：
  - `amounts` 为空时给出 `TO_TASTE.to_rounded_text(lang)`，英文是 `to taste`，中文是 `适量`。
  - 否则，`amount_text` 按顺序用 `to_rounded_text(lang)` 写出 `amounts` 里的每个数量（F01 设计 2.12），再用 ` + ` 把这些文字连起来，也就是一个空格、U+002B PLUS SIGN 和一个空格。所以 5 根和 1 把给出 `5 stalks + 1 bunch` 和 `5 根 + 1 把`。1500 g 给出 `1.5 kg`，1001 g 给出 `1.01 kg`，3/2 根给出 `2 stalks`。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | 某个取整后的数值在小数点前超过 4,300 位（F01 设计 2.12）。只有手工构建的行才可能有这样的数值。`build_shopping_list` 给出的行不会有（选择 10）。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText, Lang
from recipe_menu.shopping import ShoppingLine
from recipe_menu.units import Quantity, Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
choy_sum = Ingredient(BiText("Choy sum", "菜心"), produce)
soy_sauce = Ingredient(BiText("Soy sauce", "生抽"), seasonings)
white_pepper = Ingredient(BiText("White pepper", "白胡椒粉"), seasonings)
five = Quantity(Fraction(5), Unit.STALK)
bunch = Quantity(Fraction(1), Unit.BUNCH)
half = Quantity(Fraction(3, 2), Unit.STALK)
kilo = Quantity(Fraction(1500), Unit.G)
grams = Quantity(Fraction(1001), Unit.G)
ml = Quantity(Fraction(30), Unit.ML)
soy_grams = Quantity(Fraction(10), Unit.G)

scallion_line = ShoppingLine(scallion, (five, bunch))
assert scallion_line.amount_text(Lang.EN) == "5 stalks + 1 bunch"
assert scallion_line.amount_text(Lang.ZH) == "5 根 + 1 把"
assert ShoppingLine(scallion, (half,)).amount_text(Lang.EN) == "2 stalks"
assert ShoppingLine(choy_sum, (kilo,)).amount_text(Lang.ZH) == "1.5 kg"
assert ShoppingLine(choy_sum, (grams,)).amount_text(Lang.EN) == "1.01 kg"
assert ShoppingLine(soy_sauce, (ml, soy_grams)).amount_text(Lang.ZH) == "30 ml + 10 g"
assert ShoppingLine(white_pepper, ()).amount_text(Lang.EN) == "to taste"
assert ShoppingLine(white_pepper, ()).amount_text(Lang.ZH) == "适量"
```

### 2.3 `ShoppingGroup`

- 模块：shopping
- 功能：一个分类的各行，按目录里的食材顺序排列（规则 7）。`ShoppingList.groups` 为每个有行的分类保存一个分组（选择 1）。

签名：

```python
@dataclass(frozen=True, slots=True)
class ShoppingGroup:
    category: Category
    lines: tuple[ShoppingLine, ...]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `category` | `Category` | 分类，比如 Vegetables and fruit 和 蔬菜水果。 | 无 |
| `lines` | 由 `ShoppingLine` 值组成的元组 | 这个分类的各行，按目录里的食材顺序排列。 | 至少一行。每一行的食材的 `category` 等于 `category`。没有两行的食材相等。 |

- 返回值：一个 `ShoppingGroup`。两个字段都相等时，两个分组相等。`ShoppingGroup` 可哈希。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `category` 不是 `Category`，或者 `lines` 不是元组，或者其中有不是 `ShoppingLine` 的项。 |
| `ValueError` | `lines` 为空，某一行的食材的分类不等于 `category`，或者两行的食材相等。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.shopping import ShoppingGroup, ShoppingLine
from recipe_menu.units import Quantity, Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
pork = Ingredient(BiText("Minced pork", "猪肉末"), meat)
tomatoes = ShoppingLine(tomato, (Quantity(Fraction(600), Unit.G),))
minced_pork = ShoppingLine(pork, (Quantity(Fraction(100), Unit.G),))

group = ShoppingGroup(produce, (tomatoes,))
assert group.category is produce
assert group.lines == (tomatoes,)
same_produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
assert ShoppingGroup(same_produce, (tomatoes,)) == group

ShoppingGroup(produce, ())  # raises ValueError
ShoppingGroup(produce, (tomatoes, minced_pork))  # raises ValueError
ShoppingGroup(produce, (tomatoes, tomatoes))  # raises ValueError
ShoppingGroup(produce, [tomatoes])  # raises TypeError
```

### 2.4 `ShoppingList`

- 模块：shopping
- 功能：一周的购物清单（[架构 5.2](../../architecture.zh-CN.md#52-值)）：周、餐数和菜数、按目录顺序分好类的各行，以及菜单用到的常备食材。它由 `build_shopping_list` 给出，由 F13 写出。

签名：

```python
@dataclass(frozen=True, slots=True)
class ShoppingList:
    week: IsoWeek
    meal_count: int
    dish_count: int
    groups: tuple[ShoppingGroup, ...]
    pantry_used: tuple[Ingredient, ...]
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `week` | `IsoWeek` | 菜单的周，比如 `2026-W47`。 | 无 |
| `meal_count` | `int` | 这一周里至少有一道菜的餐数（选择 9）。 | 0 或更多，最多等于 `dish_count`。只有 `dish_count` 为 0 时才为 0。不是 `bool`。 |
| `dish_count` | `int` | 这一周的菜数。 | 0 或更多。不是 `bool`。 |
| `groups` | 由 `ShoppingGroup` 值组成的元组 | 每个有行的分类一个分组，按目录里的分类顺序排列（选择 7）。 | 没有两个分组的分类相等。`dish_count` 为 0 时为空。 |
| `pantry_used` | 由 `Ingredient` 值组成的元组 | 菜单用到的常备食材，按选择 6 的顺序排列。 | `dish_count` 为 0 时为空。在 `pantry_used` 和 `groups` 的各行里合起来，没有食材出现两次。 |

- 返回值：一个 `ShoppingList`。五个字段都相等时，两份清单相等。`ShoppingList` 可哈希。`ShoppingList` 不保存目录，所以它无法检查 `groups` 和 `pantry_used` 的顺序。这个顺序由 `build_shopping_list` 给出。

错误：

| 错误 | 何时发生 |
| --- | --- |
| `TypeError` | `week` 不是 `IsoWeek`，`meal_count` 或 `dish_count` 不是 `int` 或者是 `bool`，`groups` 不是由 `ShoppingGroup` 值组成的元组，或者 `pantry_used` 不是由 `Ingredient` 值组成的元组。 |
| `ValueError` | `meal_count` 或 `dish_count` 小于 0，`meal_count` 大于 `dish_count`，或者 `meal_count` 为 0 而 `dish_count` 不为 0。 |
| `ValueError` | `dish_count` 为 0，而 `groups` 或 `pantry_used` 不为空。 |
| `ValueError` | 两个分组的分类相等，或者在 `pantry_used` 和 `groups` 的各行里合起来有食材出现两次。 |

- 副作用：无
- 性能指标：无

示例：

```python
from fractions import Fraction

from recipe_menu.catalog import Category, Ingredient
from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek
from recipe_menu.shopping import ShoppingGroup, ShoppingLine, ShoppingList
from recipe_menu.units import Quantity, Unit

staples = Category("staples", BiText("Rice, flour, and oil", "米面粮油"))
rice = Ingredient(BiText("Rice", "大米"), staples)
oil = Ingredient(BiText("Cooking oil", "食用油"), staples)
rice_line = ShoppingLine(rice, (Quantity(Fraction(640), Unit.G),))
group = ShoppingGroup(staples, (rice_line,))
week = IsoWeek(2026, 47)

shopping = ShoppingList(week, 4, 9, (group,), (oil,))
assert shopping.groups[0].lines[0] is rice_line
assert shopping.pantry_used == (oil,)
assert shopping == ShoppingList(week, 4, 9, (group,), (oil,))
empty = ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())
assert (empty.meal_count, empty.dish_count, empty.groups) == (0, 0, ())
assert ShoppingList(week, 1, 1, (), (oil,)).groups == ()

ShoppingList(week, 4, True, (group,), ())  # raises TypeError
ShoppingList(week, 4, 9, [group], ())  # raises TypeError
ShoppingList(week, -1, 9, (group,), ())  # raises ValueError
ShoppingList(week, 10, 9, (group,), ())  # raises ValueError
ShoppingList(week, 0, 9, (group,), ())  # raises ValueError
ShoppingList(week, 0, 0, (group,), ())  # raises ValueError
ShoppingList(week, 4, 9, (group, group), ())  # raises ValueError
ShoppingList(week, 4, 9, (group,), (rice,))  # raises ValueError
ShoppingList(week, 4, 9, (group,), (oil, oil))  # raises ValueError
```

### 2.5 `build_shopping_list`

- 模块：shopping
- 功能：按[需求 3](../../requirements.zh-CN.md#3-用户如何使用)“购物清单”的规则把一个周菜单变成它的购物清单：换算、合并、相加、去掉常备食材、分组（[需求 4](../../requirements.zh-CN.md#4-功能点)，F12）。取整由每一行的 `amount_text` 完成（2.2）。

签名：

```python
def build_shopping_list(
    menu: WeekMenu,
    recipes: Mapping[str, Recipe],
    catalog: Catalog,
    pantry: Pantry,
) -> ShoppingList: ...
```

参数：

| 名称 | 类型 | 含义 | 约束 |
| --- | --- | --- | --- |
| `menu` | `WeekMenu` | 周菜单，就是 `read_week_menu` 没有报错时给出的那个（F06 设计 2.9）。 | 无 |
| `recipes` | 从 `str` 到 `Recipe` 的 `Mapping` | `menu` 里的菜用到的每个 ID 的菜谱，就是 `read_recipe` 没有报错时给出的那些（F04 设计 2.6）。 | 包含菜用到的每个 ID，并且 `recipes[recipe_id].id` 就是 `recipe_id`。可以包含别的菜谱，F12 不看它们。`menu` 里一道菜都没有时可以为空。 |
| `catalog` | `Catalog` | 读取菜谱和常备清单时用的目录（F03 设计 2.8）。 | 包含菜用到的菜谱里的每种食材，以及 `pantry` 里的每种食材。 |
| `pantry` | `Pantry` | 常备清单，就是 `read_pantry` 用 `catalog` 给出的那个（F03 设计 2.9）。 | 只有对 `catalog` 的那条约束。 |

- 返回值：一个 `ShoppingList`（2.4），按这些步骤构建。“相等”指用 `==` 比较相等（选择 3）。

1. 检查 `pantry.ingredients` 里的每种食材都在 `catalog.ingredients` 里。
2. 数出 `meal_count`，也就是 `menu.slots` 里至少有一道菜的餐位数，以及 `dish_count`，也就是所有餐位里的菜数（选择 9）。
3. 按顺序遍历 `menu.slots` 里的餐位，按顺序遍历每个餐位里的菜，再按顺序遍历每道菜的菜谱里的食材行（选择 4）。对每道菜，取 `recipe = recipes[dish.recipe_id]` 和 `factor = Fraction(dish.servings, recipe.servings)`。对 `recipe.ingredients` 里的每个 `RecipeIngredient`，检查它的 `ingredient` 在 `catalog.ingredients` 里。然后把这一行的 `quantity.scale(factor)` 记到这种食材名下，排在之前为相等的食材记下的数量后面。
4. 对每种记了数量的食材，按顺序把这些数量交给 `add_quantities`，得到这一行的 `amounts`（F01 设计 2.10）。
5. 把这些食材先按它们的分类在 `catalog.categories` 里的位置排序，再按它们在 `catalog.ingredients` 里的位置排序（选择 7）。
6. 按这个顺序，在 `pantry.ingredients` 里的食材进入 `pantry_used`，其他每种食材成为带有它的 `amounts` 的 `ShoppingLine`（选择 6）。
7. 按这个顺序，把每个分类的各行放进一个 `ShoppingGroup`，然后给出 `ShoppingList(menu.week, meal_count, dish_count, groups, pantry_used)`。

一道菜都没有的菜单给出 `ShoppingList(menu.week, 0, 0, (), ())`（选择 9）。

错误：

`build_shopping_list` 按步骤的顺序检查它的参数，在第一个错误处抛异常。F13 传入的是读取函数没有报错时给出的、来自同一个目录的值，所以它不会遇到这些错误。

| 错误 | 何时发生 |
| --- | --- |
| `ValueError` | `pantry.ingredients` 里有不在 `catalog.ingredients` 里的食材（第 1 步）。 |
| `ValueError` | `menu` 里某道菜用到的 ID 不在 `recipes` 里，或者 `recipes[dish.recipe_id].id` 不是 `dish.recipe_id`（第 3 步）。 |
| `ValueError` | 菜用到的某个菜谱里有不在 `catalog.ingredients` 里的食材（第 3 步）。 |

- 副作用：无。它不读文件，也不修改它的任何参数。
- 性能指标：无。PT01 计时的是 F13 的 `shop`，它调用一次这个函数（选择 11）。

示例：

这个示例用代码构建 `docs/prototypes/example-data.md` 里的示例数据，也就是 `tests/data/example/` 里的数据：目录、常备清单、七个菜谱的食材行，以及 2026-W47 的菜单。它还加上 v0.1-S18 的菜谱 `scallion-noodles`。每个菜谱都是 2 份，和每个示例菜谱一样；名称和步骤都很简短，F12 不读它们。`written` 代替 F13：它用一种语言写出每个标题和每一行。示例接着构建 v0.1-S16 和 v0.1-S18 的周、一个没有菜的周，以及四个错误的调用。

```python
from fractions import Fraction

from recipe_menu.catalog import Catalog, Category, Ingredient, Pantry
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, MealSlot, WeekMenu
from recipe_menu.recipes import Recipe, RecipeIngredient, Steps
from recipe_menu.settings import Meal
from recipe_menu.shopping import ShoppingList, build_shopping_list
from recipe_menu.units import Quantity, Unit, parse_quantity

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
eggs = Category("eggs", BiText("Eggs, dairy, and tofu", "蛋奶豆制品"))
staples = Category("staples", BiText("Rice, flour, and oil", "米面粮油"))
seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
other = Category("other", BiText("Other", "其他"))
rows = [
    (produce, "番茄", "Tomato", None),
    (produce, "菜心", "Choy sum", None),
    (produce, "西兰花", "Broccoli", None),
    (produce, "葱", "Scallion", Unit.STALK),
    (produce, "姜", "Ginger", Unit.SLICE),
    (produce, "大蒜", "Garlic", Unit.CLOVE),
    (meat, "五花肉", "Pork belly", None),
    (meat, "猪肉末", "Minced pork", None),
    (meat, "鸡翅中", "Chicken wings", None),
    (eggs, "鸡蛋", "Egg", Unit.PIECE),
    (eggs, "豆腐", "Tofu", Unit.BLOCK),
    (staples, "大米", "Rice", None),
    (staples, "面条", "Noodles", None),
    (staples, "食用油", "Cooking oil", None),
    (seasonings, "盐", "Salt", None),
    (seasonings, "糖", "Sugar", None),
    (seasonings, "生抽", "Soy sauce", None),
    (seasonings, "冰糖", "Rock sugar", None),
    (seasonings, "郫县豆瓣酱", "Doubanjiang", None),
    (seasonings, "花椒", "Sichuan pepper", None),
    (seasonings, "白胡椒粉", "White pepper", None),
    (other, "可乐", "Cola", Unit.CAN),
]
ingredients = tuple(Ingredient(BiText(en, zh), cat, unit) for cat, zh, en, unit in rows)
catalog = Catalog((produce, meat, eggs, staples, seasonings, other), ingredients, ())
pantry_names = ["食用油", "盐", "糖", "生抽", "花椒"]
pantry = Pantry(frozenset(catalog.find_ingredient(name) for name in pantry_names))
recipe_lines = {
    "tomato-egg": ("番茄 300 g", "鸡蛋 3", "葱 1 根", "盐 适量", "糖 1 tsp", "食用油 2 tbsp"),
    "choy-sum": ("菜心 1 斤", "大蒜 3 瓣", "盐 适量", "食用油 1 tbsp"),
    "rice": ("大米 160 g",),
    "mapo-tofu": (
        "豆腐 1 块",
        "猪肉末 100 g",
        "郫县豆瓣酱 1 tbsp",
        "花椒 1 tsp",
        "大蒜 2 瓣",
        "葱 1 根",
        "生抽 1 tbsp",
        "食用油 2 tbsp",
    ),
    "cola-wings": ("鸡翅中 500 g", "可乐 1 罐", "姜 3 片", "葱 1 根", "生抽 2 tbsp"),
    "tomato-egg-noodles": (
        "面条 200 g",
        "番茄 300 g",
        "鸡蛋 2",
        "葱 1 根",
        "盐 适量",
        "白胡椒粉 适量",
    ),
    "red-braised-pork": ("五花肉 1 斤", "冰糖 30 g", "生抽 2 tbsp", "姜 3 片", "葱 2 根"),
    "scallion-noodles": ("面条 200 g", "葱 1 把", "生抽 10 g"),
}


def recipe(recipe_id: str, lines: tuple[str, ...]) -> Recipe:
    items = []
    for line in lines:
        name, amount = line.split(" ", 1)
        ingredient = catalog.find_ingredient(name)
        items.append(RecipeIngredient(ingredient, parse_quantity(amount, ingredient.unit)))
    return Recipe(recipe_id, BiText(recipe_id), 2, (), tuple(items), Steps(("Cook.",)))


recipes = {recipe_id: recipe(recipe_id, lines) for recipe_id, lines in recipe_lines.items()}


def week_menu(week: IsoWeek, meals: tuple[Meal, ...], cells: dict) -> WeekMenu:
    slots = [MealSlot(day, meal, cells.get((day, meal), ())) for day in Day for meal in meals]
    return WeekMenu(week, meals, tuple(slots))


def written(shopping: ShoppingList, lang: Lang) -> list[str]:
    texts = []
    for group in shopping.groups:
        texts.append(group.category.name.get(lang))
        for line in group.lines:
            texts.append(f"- {line.ingredient.name.get(lang)} {line.amount_text(lang)}")
    return texts


cells = {
    (Day.MONDAY, Meal.DINNER): (Dish("tomato-egg", 2), Dish("choy-sum", 2), Dish("rice", 2)),
    (Day.TUESDAY, Meal.DINNER): (Dish("mapo-tofu", 2), Dish("rice", 2)),
    (Day.SATURDAY, Meal.LUNCH): (Dish("tomato-egg-noodles", 2),),
    (Day.SUNDAY, Meal.DINNER): (Dish("cola-wings", 4), Dish("choy-sum", 4), Dish("rice", 4)),
}
w47 = week_menu(IsoWeek(2026, 47), (Meal.LUNCH, Meal.DINNER), cells)
shopping = build_shopping_list(w47, recipes, catalog, pantry)
assert (shopping.week, shopping.meal_count, shopping.dish_count) == (IsoWeek(2026, 47), 4, 9)
assert written(shopping, Lang.ZH) == [
    "蔬菜水果",
    "- 番茄 600 g",
    "- 菜心 1.5 kg",
    "- 葱 5 根",
    "- 姜 6 片",
    "- 大蒜 11 瓣",
    "肉类水产",
    "- 猪肉末 100 g",
    "- 鸡翅中 1 kg",
    "蛋奶豆制品",
    "- 鸡蛋 5 个",
    "- 豆腐 1 块",
    "米面粮油",
    "- 大米 640 g",
    "- 面条 200 g",
    "调味品",
    "- 郫县豆瓣酱 15 ml",
    "- 白胡椒粉 适量",
    "其他",
    "- 可乐 2 罐",
]
pantry_line = [ingredient.name.zh for ingredient in shopping.pantry_used]
assert pantry_line == ["食用油", "盐", "糖", "生抽", "花椒"]
english = [line.amount_text(Lang.EN) for group in shopping.groups for line in group.lines]
assert english[:5] == ["600 g", "1.5 kg", "5 stalks", "6 slices", "11 cloves"]
assert english[-3:] == ["15 ml", "to taste", "2 cans"]
assert shopping.groups[0].lines[1].amounts == (Quantity(Fraction(1500), Unit.G),)

breakfast = {(Day.MONDAY, Meal.BREAKFAST): (Dish("tomato-egg", 3),)}
w48 = week_menu(IsoWeek(2026, 48), tuple(Meal), breakfast)
s16 = build_shopping_list(w48, {"tomato-egg": recipes["tomato-egg"]}, catalog, pantry)
assert (s16.meal_count, s16.dish_count) == (1, 1)
assert written(s16, Lang.EN) == [
    "Vegetables and fruit",
    "- Tomato 450 g",
    "- Scallion 2 stalks",
    "Eggs, dairy, and tofu",
    "- Egg 5 pieces",
]
assert s16.groups[1].lines[0].amounts == (Quantity(Fraction(9, 2), Unit.PIECE),)
s16_pantry = [ingredient.name.en for ingredient in s16.pantry_used]
assert s16_pantry == ["Cooking oil", "Salt", "Sugar"]

dinners = {
    (Day.MONDAY, Meal.DINNER): (Dish("red-braised-pork", 2),),
    (Day.TUESDAY, Meal.DINNER): (Dish("tomato-egg", 2),),
    (Day.WEDNESDAY, Meal.DINNER): (Dish("tomato-egg", 2),),
    (Day.THURSDAY, Meal.DINNER): (Dish("tomato-egg-noodles", 2),),
    (Day.FRIDAY, Meal.DINNER): (Dish("scallion-noodles", 2),),
}
s18_week = week_menu(IsoWeek(2026, 48), (Meal.LUNCH, Meal.DINNER), dinners)
no_soy_sauce = Pantry(pantry.ingredients - {catalog.find_ingredient("生抽")})
s18 = build_shopping_list(s18_week, recipes, catalog, no_soy_sauce)
by_name = {line.ingredient.name.en: line for group in s18.groups for line in group.lines}
assert by_name["Scallion"].amount_text(Lang.EN) == "5 stalks + 1 bunch"
assert by_name["Scallion"].amount_text(Lang.ZH) == "5 根 + 1 把"
assert by_name["Soy sauce"].amount_text(Lang.EN) == "30 ml + 10 g"

nothing = week_menu(IsoWeek(2026, 46), (Meal.LUNCH, Meal.DINNER), {})
empty = build_shopping_list(nothing, {}, catalog, pantry)
assert empty == ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())

wrong_id = {**recipes, "rice": recipes["choy-sum"]}
no_cola = Catalog(catalog.categories, ingredients[:-1], ())
lard = Pantry(frozenset({Ingredient(BiText("Lard", "猪油"), staples)}))
build_shopping_list(w47, {}, catalog, pantry)  # raises ValueError
build_shopping_list(w47, wrong_id, catalog, pantry)  # raises ValueError
build_shopping_list(w47, recipes, no_cola, pantry)  # raises ValueError
build_shopping_list(w47, recipes, catalog, lard)  # raises ValueError
```

## 3. 对已有接口的修改

无。F01 到 F11 实现的接口都没有改变。F12 添加模块 `shopping`，不改动其他模块的文件。

F12 按设计里给出的样子使用这些接口，一个都不修改：

- `units` 里 F01 的 `Quantity`、`Quantity.scale`、`Quantity.to_rounded_text`、`TO_TASTE`、`Unit`、`UnitKind` 和 `add_quantities`（F01 设计 2.2 到 2.4、2.9、2.10 和 2.12），以及 `lang` 里的 `Lang`（F01 设计 2.1）。
- `catalog` 里 F03 的 `Catalog`、`Category`、`Ingredient` 和 `Pantry`（F03 设计 2.4、2.5 和 2.7）。
- `recipes` 里 F04 的 `Recipe` 和 `RecipeIngredient`（F04 设计 2.1 和 2.3）。
- `menus` 里 F06 的 `Dish`、`IsoWeek`、`MealSlot` 和 `WeekMenu`（F06 设计 2.1 和 2.4 到 2.6）。

## 4. 架构师审查

| 项目 | 结果 | 备注 |
| --- | --- | --- |
| 符合模块划分和数据模型 | 通过 | `shopping` 是架构 3 里的领域模块：文件夹 `src/recipe_menu/shopping/`，它的 `__init__.py` 在 `__all__` 里列出四个名字。它没有 `Message`，所以没有 `messages.py`（架构 8）。架构师按第 2 节建的模型只引用 `lang`、`units`、`catalog`、`recipes` 和 `menus`，正是它那一行允许的五个模块，mypy 的严格模式也接受它。它从不引用 `settings`。只有示例引用 `Meal`，用来构造 `WeekMenu`。它不读文件，不打印，也不保存状态（架构 4 和 8）。四个输入就是架构 5.3 的那四个。`ShoppingList` 的五个字段和 `ShoppingLine` 的两个字段就是 5.2 的那些，`amounts` 为空表示适量。每个值都是带 `slots=True` 的冻结 dataclass，字段用元组，每个数量都保持为 `Fraction`（ADR-0007）。简报的 2(a) 点：选择 3 在现有架构之内。5.2 的说明给出合并能成立的原因：菜谱和常备清单引用的是目录自己的 `Ingredient` 值。一个目录里没有两个相等的食材，所以对读取器给出的值，`==` 和 `is` 合并的食材完全相同。模型把示例那一周从文件构造一次、按 2.5 的代码构造一次，两份清单相等。相等还能归好按同一性会漏掉的情况：食材的分类是一个相等但不同的 `Category` 对象，而 `Catalog` 接受这种情况。所以不需要修改架构。下次修改架构时，架构师会把 5.2 的说明改写为：清单合并相等的食材，对读取器给出的值来说它们就是同一个对象。新的说法不改变任何规则。2(b) 点：`ShoppingGroup` 不需要修改架构。5.2 列出跨模块的值，确切的名字和签名留给各设计，而 `ShoppingGroup` 正是 5.2 里“按目录顺序按分类分组的各行”的形状。它是辅助值，和 `Severity`、`Steps`、`FolderUse`、`Day`、`MealSlot`、`Creation`、`FileCreation` 一样，5.2 也没有列出它们。选择 2 的 `Mapping` 参数符合架构 8，那条关于元组和 frozenset 的规则针对的是值里的集合。F12 只读取这个映射，不保留其中任何东西，就像 `datafile` 的 `read_text` 读取一个 `Mapping` 表、`add_quantities` 读取任何可迭代对象那样。 |
| 遵守错误处理和命名约定 | 通过 | `shopping` 不读文件，所以没有 `Problem`。`build_shopping_list` 只在调用错误时抛出 `ValueError`，各构造函数只在字段错误时抛出 `TypeError` 或 `ValueError`，和 F01 到 F06 的值一样。错误的调用是 bug，架构 6 把它交给 Python 的回溯，设计不捕获任何异常。在模型里，22 个 `# raises` 行各自抛出它写明的错误。3,000 个随机目录上的随机菜单没有让 `build_shopping_list` 或 `amount_text` 抛出任何异常，其中有随机的常备清单、每种单位下最多 15 位数字的数量、1 到 100 的份数，以及相等但不同的分类对象。所以读取器给出的值永远碰不到这些错误。选择 10 的界限成立：每个换算后的数量都小于 10^20，每个和的分母都整除 10^14 乘以 1 到 100 的最小公倍数，那是一个 55 位的数。2(c) 点：选择 8 符合架构 3、4、8 和 ADR-0004。`amount_text` 只用到 `units` 和 `lang`，`shopping` 那一行允许它们。它返回字符串，不打印任何东西，和 `Quantity.to_rounded_text`、`Meal.label` 一样。ADR-0004 把单位的名称放在它的类型旁边，作为 `units` 里的普通数据，F01 的设计也把适量的文字放在那里。` + ` 是不属于任何语言的符号，F13 原型在两种语言里都这样写。所以 `shopping` 不需要 `Message`，也没有手工拼英文复数或列表。需求里 F12 那一行不用修改需求就能满足。F12 自己的方法写出取整后的文字，精确的数量遵循 ADR-0007，F01 那一行也仍然成立，因为取整规则仍在 `to_rounded_text` 里。F01 里“F13 用 `Quantity.to_rounded_text` 写出每个和”这一句是计划，不是接口，所以把这个调用移到 F12 不改变任何已实现的接口。名字遵循 PEP 8 和 5.2 的名字，文档注释用码位写出中文的适量。备注 1，不阻塞（选择 2，以及 2.5 里对 `recipes` 的约束和“错误”表的第二行）：“`recipes[recipe_id].id` 就是 `recipe_id`”和“不是 `dish.recipe_id`”可能被读成 Python 的 `is`。两个相等的 ID 可以是不同的 `str` 对象，所以设计可以写“等于”和“不等于”，就像选择 3 对食材那样。选择 2 的“映射把一个菜谱放在了别的 ID 下”也可以写明是“某道菜用到的菜谱”，因为 2.5 只检查这些菜谱。备注 2，不阻塞（选择 10）：一个超过 4,300 位的计数需要和至少为 10^4300，所以大约需要 10^4280 行菜谱食材，而不是 10^4279。克和毫升大约需要 10^4283，因为 kg 和 L 要除以 1,000。结论不变。 |
| 不和已有接口重复 | 通过 | F12 用 `Quantity.scale` 换算份数，用 `add_quantities` 换算单位并相加，用 `Quantity.to_rounded_text` 取整并写出，没有重写其中任何一个。`amount_text` 把 `to_rounded_text` 给出的文字连起来，所以取整规则留在 `units` 里，F13 在终端和 Markdown 清单里都通过同一个方法写出每一行的数量。餐数和菜数重复了 F11 的 `menu` 内部计数的两行，因为 `shopping` 不能引用 `menu`（架构 3），而 F06 设计第 2 节为两者计划了同样的计数。构造函数的检查是 `shopping` 内部的。选择 6 的常备规则用到 `Pantry.ingredients` 和目录的顺序，没有给 `catalog` 增加查找。 |
| 只依赖排序在前面的功能 | 通过 | F12 使用 F01 的 `Lang` 和 `units`，通过目录的名字使用 F02 的 `BiText`，使用 F03 的 `catalog`、F04 的 `recipes` 和 F06 的 `menus`，`menus` 的 `MealSlot` 里有 F05 的 `Meal`。这些功能都排在 F12 前面，并且在 main 上通过测试。F01、F03、F04 和 F06 是 F12 那一行的软依赖。第 2 节对 F13 的计划把细节留给 F13 的设计，所以不约束后面的设计。F12 只需要标准库，所以 R16 没有要审查的东西。`docs/rules.md` 里没有由架构师检查的 Review 类 P 规则。 |
| 不在模块之间增加隐性耦合 | 通过 | 设计写下了模块之间的每个假设。F13 必须传入读取器无错误给出的、来自同一个目录的值，2.5 的三行 `ValueError` 会拦下任何别的调用（选择 2）。各个和的顺序依赖 `WeekMenu.slots` 的顺序，而 `WeekMenu` 的构造函数保证这个顺序（选择 4）。F13 用 `amount_text` 写出每一行的数量，其他文字都由它自己写：根据 `pantry_used` 写的常备那一行、各标题、计数，以及没有菜的一周或没有分组的清单时 `shop` 显示什么（选择 8 和 9）。选择 10 的界限依赖 `parse_quantity` 的 15 位数字，以及菜谱和菜的 100 份上限，设计写明了这两点。`build_shopping_list` 只在一次调用里保留它的字典，没有模块保存缓存。简报第 1 点：选择 1 到 11 在模型上都成立。选择 1：构造函数拒绝 2.1、2.3 和 2.4 的 18 个错误值，从不拒绝 `build_shopping_list` 给出的值。选择 4：v0.1-S18 得到 `5 stalks + 1 bunch` 和 `30 ml + 10 g`。选择 5 和 6：白胡椒粉得到 `to taste` 和 `适量`，示例那一周只用了适量的盐在 `pantry_used` 里。选择 7：一个分类的食材在目录里分几处列出时，每个分类仍然只有一组，按目录的顺序。选择 9：没有菜的一周得到 `ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())`。选择 11：在 `tests/pt01_support.py` 生成的 PT01 文件夹上，2026-W26 这一周有来自 63 个菜谱的 63 道菜、756 行食材、21 餐、6 组、290 行和 10 种常备食材。`build_shopping_list` 调用 200 次的中位数是 5.1 毫秒，`amount_text` 用两种语言写出全部 290 行用了 1.9 毫秒。一个代替 `shop` 的脚本读取 `menu show` 读取的文件再加上常备清单，生成清单，打印出来，并写一个 Markdown 文件。在 Troy 的电脑上的同一组运行里，它 5 次运行的中位数是 0.222 秒，`menu show 2026-W26` 5 次运行是 0.209 秒。所以选择 11 估计的约 0.01 秒和约 0.2 秒成立。给开发者：一个记录目录中位置的字典就能满足第 1、3、5 步。在元组 `catalog.ingredients` 上做成员测试会按 `==` 比较，在一个 PT01 周上多用约 13 毫秒。 |
| 修改已实现的接口时走了变更流程 | 通过 | 第 3 节说“无”是对的。这个 PR 只添加两个设计文件，main 上还没有 `src/recipe_menu/shopping/`。F12 用到的每个名字都以第 3 节写出的签名存在于 main 上，模型在 main 的代码上运行，没有修改别的模块。F01 对 F13 的计划和架构 5.2 关于同一性的说明都不是接口，`RecipeIngredient` 的文档注释对读取器给出的值仍然成立。简报第 5 点：这样拆分是对的。mock 的 3 个文件 `__init__.py`、`_model.py` 和 `_build.py` 定义了不带检查的值，`amount_text` 和 `build_shopping_list` 抛出 `NotImplementedError`。所以调用两者之一、期望构造函数抛出异常或期望得到空清单的测试，对 mock 都会失败（R09）。`NotImplementedError` 是 `RuntimeError`，所以写明 `ValueError` 或 `TypeError` 的错误调用测试也会失败。对 mock 能通过的测试，是只检查四个名字，或者只检查有效值的字段、相等、哈希或不可变性的测试，比如 `ShoppingList(week, 1, 1, (), (oil,))`。设计写出了前两类，测试经理可以补上哈希和不可变性。模型有 3 个文件，文档注释写得简短，约 270 行。写上完整的 Google 风格文档注释后，3 个文件约 200 行的 mock，以及修改 2 到 3 个文件约 300 行的实现，都在 R03 之内，所以两个 PR 都不需要软限制的理由。 |
| 给 Troy 的摘要和设计说的一致，并列出了需要 Troy 决定的每一件事 | 通过 | 摘要的每一点都和设计一致：不加命令、不改文件（第 2 节），以 450 g 番茄为例的份数换算（v0.1-S16），以葱那一行为例的合并（选择 4），适量和只显示数量（选择 5），按目录顺序、包括盐的常备那一行（选择 6），顺序和不出现空分类（选择 7），对一周的总数取整一次以及 kg 和 L（选择 8），6 个分类、14 样东西、4 餐、9 道菜和空清单（选择 9），以及两条风险（选择 5 和 11）。模型证实了每个数字。两种语言都没有内部编号，都在 2,000 字符以内，中文 658 个，英文 1,750 个。简报第 4 点：没有需要交给 Troy 决定的点。选择 5 遵循 Troy 批准的规则 5，即没有一道菜写数量的食材显示适量，也遵循 F01 的 `add_quantities`，其中适量不增加任何量。在数量旁边再写适量会修改需求，Troy 看了这条风险后可以提出。架构师推荐保留选择 5。选择 8 不改变 Troy 输入或看到的任何东西，终端、文件和取整都和原型一样，所以不由 Troy 决定。架构师推荐保留它。备注 3，可选（摘要的第一条风险）：“略”和“slightly”判断了 Troy 可能少买多少，设计没有这样说。摘要可以去掉这个词，或者由选择 5 写出后果。备注 4，可选（摘要的第二条风险）：摘要可以加上本节里架构师的测量结果，这一部分约 0.005 秒，代替 `shop` 的脚本约 0.22 秒，它仍然不是真正的命令。 |

| 轮次 | 问题 | 解决方式 |
| --- | --- | --- |
| 1 | 没有阻塞问题。架构师对照需求、架构、ADR-0004 和 ADR-0007、F01、F03、F04、F06 和 F11 的设计、F13 原型，以及 v0.1-S14、v0.1-S16 到 v0.1-S18 和 v0.1-S32，检查了 11 个选择。每个文件有 10 个代码块，都是 `python`，每个都和镜像里的相同，两个文件有同样的 11 个标题和 73 个表格行。用 ruff 0.17.4 和项目的设置运行 `ruff format --check`，报告两个文件都已格式化。架构师在 Windows 上用 Python 3.13.18，基于 main 的代码，在 `src/` 的一份副本里按第 2 节建了模型，运行了 5 个示例：全部 35 个断言和全部 22 个 `# raises` 都成立。模型还用 main 的读取器读取了 `tests/data/example/` 的新副本。2026-W47 这一周得到 F13 原型英文和中文两份输出的每一行，有 6 个分类、14 样东西、4 餐、9 道菜，常备食材是食用油、盐、糖、生抽和花椒，它的清单也等于 2.5 的示例在代码里构造的清单。v0.1-S16 的文件得到 Tomato 450 g、Scallion 2 stalks、Egg 5 pieces、1 餐、1 道菜，以及 Cooking oil、Salt 和 Sugar。v0.1-S18 的文件得到 `5 stalks + 1 bunch`、`5 根 + 1 把` 和 `30 ml + 10 g`，没有菜的一周得到空清单。没有运行测试，因为这个 PR 不改代码。备注 1 到 4 不阻塞。 | 批准。接口设计师可以在修订中处理备注 1 到 4，也可以不处理。由 Troy 批准这份设计（R18，`troy_approves_first = 16`）。架构师在下次修改架构时改写架构 5.2 里关于同一性的说明。 |

## 5. 修改记录

| 版本 | 日期 | 修改 |
| --- | --- | --- |
| 0.1 | 2026-11-15 | 初稿。 |
| 1.0 | 2026-11-15 | Troy 批准。 |
