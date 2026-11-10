---
troy-doc: "F01-design"
lang: "en"
version: "1.1"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "design.zh-CN.md"
---

# F01 Quantities and units: interface design

## 1. Feature

- ID and name: F01 Quantities and units
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: None

## 2. Interfaces

F01 builds two base modules ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.lang` exports `Lang`. `recipe_menu.units` exports `UnitKind`, `Unit`, `Quantity`, `TO_TASTE`, `WrongQuantity`, `WrongQuantityReason`, `parse_unit`, `parse_quantity`, and `add_quantities`. Each module's `__init__.py` lists these names in `__all__`. The files behind it are the Developer's choice.

These rules hold for every interface below:

- Every amount is an exact `fractions.Fraction`, and no `float` holds one (ADR-0007). Amounts compare exactly, with no tolerance.
- `units` never raises for bad data. A wrong amount text gives a `WrongQuantity` value, and `recipes` turns it into a `Problem` with its own message ([architecture 4](../../architecture.md#4-dependency-rules) and [6](../../architecture.md#6-error-handling)). The exceptions that `units` raises below come from wrong calls, which are bugs. `Lang(value)` raises `ValueError` for an unknown code, as every enum does, and its caller turns that into a `Problem` or a `UsageError`.
- `units` imports only `lang` from the package. It holds no `Message`, and the names of its units are plain data (ADR-0004).
- No interface prints, reads a file, or keeps state.

These later features are meant to call them:

- F03 reads an ingredient's default unit with `parse_unit`.
- F04 reads each ingredient's amount with `parse_quantity` and the ingredient's default unit.
- F09 scales a recipe with `Quantity.scale` and writes each quantity with `Quantity.to_text`.
- F12 scales each dish with `Quantity.scale` and adds up each ingredient with `add_quantities`.
- F13 writes each sum with `Quantity.to_rounded_text`.

### 2.1 `Lang`

- Module: lang
- Purpose: The two languages of the tool. Every interface that writes text for the user takes a `Lang`. Its values are the values that `--lang` and the settings' `language` take.

Signature:

```python
class Lang(StrEnum):
    EN = "en"
    ZH = "zh"
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `value` | `str` | The language code that `Lang(value)` looks up. | `"en"` or `"zh"`, exactly as written. |

- Return value: `Lang(value)` gives the member with that value. A member is a `str` equal to its value, so `str(Lang.ZH)` is `"zh"`. The members come in the order `EN`, `ZH`.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `Lang(value)` gets any other string, such as `"fr"` or `"EN"`. The caller turns it into its own message. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang

assert Lang("zh") is Lang.ZH
assert str(Lang.EN) == "en"
assert list(Lang) == [Lang.EN, Lang.ZH]
Lang("fr")  # raises ValueError
```

### 2.2 `UnitKind`

- Module: units
- Purpose: The kind of a unit: mass, volume, or count. Mass converts to grams and volume to millilitres. A count unit converts to nothing else, and no kind converts to another kind.

Signature:

```python
class UnitKind(Enum):
    MASS = "mass"
    VOLUME = "volume"
    COUNT = "count"
```

Parameters: None

- Return value: None. `Unit.kind` (2.3) gives a member.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.units import Unit, UnitKind

assert Unit.TBSP.kind is UnitKind.VOLUME
assert Unit.JIN.kind is UnitKind.MASS
assert Unit.BUNCH.kind is UnitKind.COUNT
```

### 2.3 `Unit`

- Module: units
- Purpose: One member for each unit of [requirements 3](../../requirements.md#3-how-users-interact-with-it), with its kind, its size in grams or millilitres, and its labels in both languages. The labels, including the English plural of each count unit, are plain data in `units`, because `units` comes before `text` (ADR-0004).

Signature:

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

Each member's value is its English label. Code finds a unit by its spelling with `parse_unit` (2.6), not by its value. The table gives each member and what its properties return.

| Member | `kind` | `size` | English label | English plural | Chinese label | Spellings that `parse_unit` reads |
| --- | --- | --- | --- | --- | --- | --- |
| `G` | `MASS` | 1 | g | g | g | `g`, `克` |
| `KG` | `MASS` | 1000 | kg | kg | kg | `kg`, `千克`, `公斤` |
| `JIN` | `MASS` | 500 | jin | jin | 斤 | `jin`, `斤` |
| `LIANG` | `MASS` | 50 | liang | liang | 两 | `liang`, `两` |
| `ML` | `VOLUME` | 1 | ml | ml | ml | `ml`, `毫升` |
| `L` | `VOLUME` | 1000 | L | L | L | `L`, `升` |
| `TSP` | `VOLUME` | 5 | tsp | tsp | 茶匙 | `tsp`, `茶匙` |
| `TBSP` | `VOLUME` | 15 | tbsp | tbsp | 汤匙 | `tbsp`, `汤匙` |
| `PIECE` | `COUNT` | `None` | piece | pieces | 个 | `piece`, `pieces`, `个` |
| `STALK` | `COUNT` | `None` | stalk | stalks | 根 | `stalk`, `stalks`, `根` |
| `CLOVE` | `COUNT` | `None` | clove | cloves | 瓣 | `clove`, `cloves`, `瓣` |
| `SLICE` | `COUNT` | `None` | slice | slices | 片 | `slice`, `slices`, `片` |
| `BLOCK` | `COUNT` | `None` | block | blocks | 块 | `block`, `blocks`, `块` |
| `BUNCH` | `COUNT` | `None` | bunch | bunches | 把 | `bunch`, `bunches`, `把` |
| `CAN` | `COUNT` | `None` | can | cans | 罐 | `can`, `cans`, `罐` |
| `PACK` | `COUNT` | `None` | pack | packs | 包 | `pack`, `packs`, `包` |

English spellings match in any case, so `L`, `l`, `ML`, and `Tbsp` all match. The Chinese label of `G`, `KG`, `ML`, and `L` is the symbol, because the shopping list writes g, kg, ml, and L in both languages, and the F09 and F13 prototypes show `600 g` in Chinese. The labels jin and liang have no English plural.

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language of the label that `label` returns. | None |
| `plural` | `bool` | Whether the label follows an amount other than 1. | Changes English count labels only. Chinese labels ignore it. |

- Return value: `kind` gives the unit's `UnitKind`. `size` gives the grams in one mass unit or the millilitres in one volume unit, as an exact `Fraction`, and `None` for a count unit. `label` gives the label from the table.

Errors: None

- Side effects: None
- Performance target: None

Example:

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

### 2.4 `Quantity` and `TO_TASTE`

- Module: units
- Purpose: An exact amount in a unit, or "to taste". A recipe's ingredient holds one (`RecipeIngredient.quantity`, [architecture 5.2](../../architecture.md#52-values)), and so does each sum on a shopping line. `TO_TASTE` is the "to taste" value.

Signature:

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

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `amount` | `Fraction` or `None` | The exact amount, counted in `unit`. | Greater than 0. `None` only for to taste. |
| `unit` | `Unit` or `None` | The unit of `amount`. | `None` only for to taste. `amount` and `unit` are both set or both `None`. |

- Return value: A `Quantity`. `is_to_taste` is `True` when `amount` and `unit` are `None`. Two quantities are equal when their amounts are equal and their units are equal, so 1 kg and 1000 g are not equal. To compare sizes, compare the results of `in_base_unit`. A `Quantity` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `amount` is neither a `Fraction` nor `None`, such as a `float` or an `int`. |
| `ValueError` | One of `amount` and `unit` is `None` and the other is not. |
| `ValueError` | `amount` is 0 or less. |

- Side effects: None
- Performance target: None

Example:

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

### 2.5 `WrongQuantity` and `WrongQuantityReason`

- Module: units
- Purpose: What is wrong with an amount text that `parse_quantity` cannot read. `units` has no messages, so `recipes` turns this value into a `Problem` with a message in both languages, such as `Unknown unit "cups" in "1 cups".` in the F07 prototype ([architecture 4](../../architecture.md#4-dependency-rules)).

Signature:

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

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `reason` | `WrongQuantityReason` | What is wrong. The errors of 2.7 give the condition of each member. | None |
| `text` | `str` | The amount text, without whitespace at either end. | None |
| `unit` | `str` or `None` | The unknown unit as written, such as `"cups"`. | Set for `UNKNOWN_UNIT` only. `None` for every other reason. |

- Return value: A `WrongQuantity`. Two of them are equal when all three fields are equal.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.units import WrongQuantity, WrongQuantityReason, parse_quantity

assert parse_quantity(" 1 cups ") == WrongQuantity(WrongQuantityReason.UNKNOWN_UNIT, "1 cups", "cups")
assert parse_quantity("a few") == WrongQuantity(WrongQuantityReason.NOT_A_NUMBER, "a few")
```

### 2.6 `parse_unit`

- Module: units
- Purpose: Finds the unit that a word names, in either language. `catalog` reads an ingredient's default unit with it, and `parse_quantity` reads the unit after the number with it.

Signature:

```python
def parse_unit(text: str) -> Unit | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | A unit as written, such as `"g"`, `"公斤"`, or `"cloves"`. | Any string. |

- Return value: The `Unit` that has `text` among its spellings in 2.3, after `parse_unit` removes whitespace at both ends of `text`. English spellings match in any case. `None` when no unit has that spelling, which includes the empty string, `"to taste"`, and `"适量"`.

Errors: None. `parse_unit` never raises.

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.units import Unit, parse_unit

assert parse_unit("公斤") is Unit.KG
assert parse_unit(" Tbsp ") is Unit.TBSP
assert parse_unit("cloves") is Unit.CLOVE
assert parse_unit("cups") is None
assert parse_unit("适量") is None
```

### 2.7 `parse_quantity`

- Module: units
- Purpose: Reads an amount as a recipe writes it: a number with or without a unit, or "to taste" ([requirements 3](../../requirements.md#3-how-users-interact-with-it), "Units").

Signature:

```python
def parse_quantity(text: str, default_unit: Unit | None = None) -> Quantity | WrongQuantity: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | The amount as written, such as `"300 g"`, `"1.5 kg"`, `"300克"`, `"3"`, or `"适量"`. | Any string. |
| `default_unit` | `Unit` or `None` | The unit of an amount that names none: the ingredient's default unit from the catalog. | `None` when the ingredient has no default unit. A unit in `text` always wins over it. |

- Return value: A `Quantity`, or a `WrongQuantity` when `text` cannot be read.

`parse_quantity` reads `text` in these steps:

1. It removes whitespace at both ends, including the ideographic space U+3000.
2. `to taste` in any case, with one or more whitespace characters between the two words, gives `TO_TASTE`. So does `适量`.
3. The number is the text before the first letter or whitespace character. A letter is a character for which `str.isalpha` is true, which includes Chinese characters. The number is one or more ASCII digits, optionally followed by `.` and one or more ASCII digits, such as `3`, `300`, `1.5`, or `0.25`. It has at most 15 digits. The point does not count, and every digit counts, leading and trailing zeros included, so `12345678901234.5` is read and `0.000000000000001` is not. The limit keeps the number far below the 4,300 digits that Python's `int` and `Fraction` read from a string. The number becomes an exact `Fraction`, so `1.5` is 3/2.
4. The rest of the text, without whitespace at either end, is the unit, read with `parse_unit`. The space before the unit is optional, so `300 g`, `300g`, and `300克` all work.
5. An amount with no unit gets `default_unit`.

Errors:

`parse_quantity` never raises. It returns a `WrongQuantity` with the first reason in this table that applies.

| Error | When |
| --- | --- |
| `EMPTY` | `text` is empty or holds only whitespace. |
| `NOT_A_NUMBER` | The number is missing, is not a decimal number of ASCII digits, or has more than 15 digits, as in `a few`, `g`, `1/2 tsp`, `1,5 g`, `-1 g`, `½ tsp`, `３ 个` with a fullwidth digit, or `1234567890123456 g`. This row comes before `UNKNOWN_UNIT` and `ZERO`, so `1234567890123456 cups` and `0000000000000000 g` give `NOT_A_NUMBER` too. |
| `UNKNOWN_UNIT` | The unit is not a spelling in 2.3, as in `1 cups` or `1 适量`. The field `unit` holds it. |
| `NO_UNIT` | The text has no unit, and `default_unit` is `None`. |
| `ZERO` | The number is 0, as in `0 g` or `0.00 个`. |

- Side effects: None
- Performance target: None

Example:

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

- Module: units, a method of `Quantity` (2.4)
- Purpose: Converts mass to grams and volume to millilitres, exactly. A count unit converts to nothing else, so a count and to taste stay as they are.

Signature:

```python
def in_base_unit(self) -> Quantity: ...
```

Parameters: None

- Return value: For a mass unit, `Quantity(amount * unit.size, Unit.G)`. For a volume unit, `Quantity(amount * unit.size, Unit.ML)`. For a count unit or to taste, the same quantity.

Errors: None

- Side effects: None
- Performance target: None

Example:

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

- Module: units, a method of `Quantity` (2.4)
- Purpose: Multiplies the amount by a factor, such as a dish's servings divided by the recipe's servings. The unit stays, so `show` can write a scaled amount in the recipe's unit.

Signature:

```python
def scale(self, factor: Fraction) -> Quantity: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `factor` | `Fraction` | The number to multiply by, such as `Fraction(4, 2)` for 4 servings of a 2-serving recipe. | Greater than 0. |

- Return value: `Quantity(amount * factor, unit)`, exact. `TO_TASTE` for to taste.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `factor` is not a `Fraction`, such as a `float` or an `int`. |
| `ValueError` | `factor` is 0 or less. This holds for to taste too. |

- Side effects: None
- Performance target: None

Example:

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

- Module: units
- Purpose: Adds up quantities of the same kind: mass in grams, volume in millilitres, and each count unit on its own. It never converts mass to volume, or either one to a count ([requirements 3](../../requirements.md#3-how-users-interact-with-it), shopping list rule 3).

Signature:

```python
def add_quantities(quantities: Iterable[Quantity]) -> tuple[Quantity, ...]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `quantities` | `Iterable[Quantity]` | The quantities to add, such as one ingredient's scaled quantities from every dish of a week. | Any units, to taste included. May be empty. |

- Return value: One exact sum for each group: all mass as one `Quantity` in `Unit.G`, all volume as one in `Unit.ML`, and each count unit as one in that unit. The sums come in the order in which their groups first appear in `quantities`. To taste adds nothing, so the tuple is empty when no quantity has an amount. The sums are not rounded. `to_rounded_text` rounds a sum when it writes it.

Errors: None

- Side effects: None
- Performance target: None

Example:

The first three cases are lines of the F13 prototype.

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

- Module: units, a method of `Quantity` (2.4)
- Purpose: Writes the quantity in its own unit. `show` uses it, because `show` "writes a quantity in the unit that the recipe uses" ([requirements 3](../../requirements.md#3-how-users-interact-with-it)).

Signature:

```python
def to_text(self, lang: Lang) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language to write in. | None |

- Return value: The text, by these rules:
  - To taste is `to taste` in English and `适量` in Chinese.
  - Any other quantity is its amount, a space, and the label of its unit (2.3).
  - The amount is rounded up to at most two decimals. It is written with `.` as the decimal point, without trailing zeros, and without a thousands separator, such as `2`, `4.5`, `1.34`, or `1500`.
  - In English, the label is plural unless the written amount is `1`.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | The rounded amount has more than 4,300 digits before the point, Python's limit on writing an `int` (`sys.int_info.default_max_str_digits`). This error comes only from a wrong call. No amount that `parse_quantity` reads comes near that size, even scaled by servings. |

- Side effects: None
- Performance target: None

Example:

The first five cases are lines of the F09 prototype.

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

- Module: units, a method of `Quantity` (2.4)
- Purpose: Writes the quantity by the rounding rules of [requirements 3](../../requirements.md#3-how-users-interact-with-it): grams, millilitres, and counts rounded up to whole numbers (shopping list rule 8, Q18), and 1000 g or more in kg and 1000 ml or more in L, with at most two decimals (rule 9). The shopping list writes each sum with it.

Signature:

```python
def to_rounded_text(self, lang: Lang) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language to write in. | None |

- Return value: The text.

`to_rounded_text` builds the text in these steps:

1. To taste is `to taste` in English and `适量` in Chinese.
2. It converts the quantity with `in_base_unit`.
3. It rounds the amount up to a whole number.
4. It writes 1000 g or more in kg, and 1000 ml or more in L. The amount in kg or L is rounded up to at most two decimals and written as in 2.11: 1500 g is `1.5 kg`, 1000 g is `1 kg`, and 1001 g is `1.01 kg`.
5. It writes any other amount as the whole number, a space, and the label of its unit, such as `600 g`, `15 ml`, `5 stalks`, or `1 block`. In English, the label is plural unless the number is 1.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | The rounded amount that `to_rounded_text` writes has more than 4,300 digits before the point, Python's limit on writing an `int` (`sys.int_info.default_max_str_digits`). This error comes only from a wrong call. No amount that `parse_quantity` reads comes near that size, even scaled by servings. |

- Side effects: None
- Performance target: None

Example:

The cases come from the F13 prototype and from scenario v0.1-S16 of the version test plan.

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

## 3. Changes to existing interfaces

None

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `lang` and `units` are base modules, and `units` imports only `lang` (architecture 3 and 4). `Unit` has one member for each unit of requirements 3, with the kind, size, and names of architecture 5.2. One `Quantity` with `amount` and `unit` both `None` for to taste fits 5.2, because `RecipeIngredient.quantity` is a `Quantity` and must hold 适量. Rounding up to two decimals follows ADR-0007, which writes at most two decimals and rounds up with `math.ceil`. Rounding kg and L up also follows Q18: 1001 g written as 1 kg would buy too little. `add_quantities` fits `ShoppingLine` in 5.2: to taste alone gives the empty tuple, and the order of first appearance gives `30 ml + 10 g` and `5 stalks + 1 bunch`, as the F13 prototype and v0.1-S18 expect. Unrounded sums keep rounding in one place, when the list is written. Version 1.1 keeps this. The 15-digit limit changes only which texts `parse_quantity` reads, and every amount that it reads is still an exact `Fraction` (ADR-0007). |
| Follows the error handling and naming conventions | Pass | Bad data gives a `WrongQuantity` value, and only wrong calls raise (architecture 4 and 6). `parse_quantity` keeps that rule: it never raises, its reasons have a fixed order, and `UNKNOWN_UNIT` carries the unit that the F07 message `Unknown unit "cups" in "1 cups".` needs. Its number format is a product choice that the requirements leave open, and `check` reports every text that it rejects. The plural labels follow ADR-0004, which keeps unit names in `units` as plain data because `units` cannot import `text`. A plural label is one of those names, stored and not built, so the rule of architecture 8 on English plurals covers message text from `text`, not unit labels. The `TypeError` for an `int` makes "every amount is a `Fraction`" (architecture 8) hold at run time. mypy in strict mode already rejects an `int` there. Names follow PEP 8, and both dataclasses are frozen with `slots=True`. Version 1.1 keeps both parts of the rule. Step 3 of 2.7 limits the number to 15 digits before the number becomes a `Fraction`, so a longer number gives `NOT_A_NUMBER` and never reaches the `ValueError` that `int` and `Fraction` raise above 4,300 digits. 15 digits is also below 640, the lowest limit that `sys.set_int_max_str_digits` accepts, so `parse_quantity` never raises under any setting. The examples of step 3 fall on each side of the limit: `12345678901234.5` has 15 digits, and `0.000000000000001` has 16. Step 2 now makes clear that `totaste`, with no whitespace, is not `to taste` and gives `NOT_A_NUMBER`. The `ValueError` rows of 2.11 and 2.12 describe wrong calls, which architecture 6 treats as bugs. 2.12 counts the digits of the amount that it writes, after step 4 changes g to kg or ml to L. `sys.int_info.default_max_str_digits` names the default limit. The limit in force is `sys.get_int_max_str_digits()`, which `PYTHONINTMAXSTRDIGITS` can change, so the 4,300 in both rows holds for the default, which the tests use. Not blocking: the F04 message for `NOT_A_NUMBER` must also fit `1234567890123456 g`, for example by naming the 15-digit limit. |
| Does not duplicate an existing interface | Pass | F01 is the first feature, and `src/` holds no code yet. `to_text` writes a quantity in the recipe's unit for `show`, and `to_rounded_text` applies the rules of the shopping list, so the two do not overlap. The English plurals that F02 gives message text are a separate interface from these unit labels. |
| Depends only on features earlier in the order | Pass | F01 has no feature dependencies. `units` depends only on `lang`, which F01 also builds. Both use only the standard library, so no new dependency needs review under R16. Version 1.1 adds no dependency. The `sys.int_info` that its new error rows name is part of the standard library. |
| Adds no hidden coupling between modules | Pass | Later modules use only the names that section 2 exports. `catalog` and `recipes` read `WrongQuantity` and its reasons. 2.3 has code find a unit with `parse_unit`, never by its value. `units` keeps no state, reads no file, and prints nothing. Version 1.1 states one assumption about callers in 2.11 and 2.12: no amount that `parse_quantity` reads comes near 4,300 digits, even scaled by servings. That assumption holds only while servings stay small. `tomllib` reads a whole number of up to 4,300 digits, far past the 64 bits of TOML 1.0, and Python's `int` reads as many from a command line. So the F05 design must give the settings' `servings` an upper bound, the F06 design must give a dish's servings one, and the F09 design must give `show --servings` one. Without these bounds, the settings, a menu file, or a command line could make `to_text` or `to_rounded_text` raise for bad data, which architecture 6 forbids. Recipe servings only divide an amount, so F04 needs no bound for this. Not blocking, because each bound belongs to a feature that reads servings, and the Architect checks it when it reviews that feature's design. |
| Changes an implemented interface only through the change flow | Pass | No interface is implemented yet, and section 3 says None. Version 1.1 changes 2.7, 2.11, and 2.12 before any code exists. `src/` does not exist yet, so no implemented interface changes, and section 3 still says None. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the six choices that the Interface Designer named against the requirements and the architecture. Only the plural labels seemed to conflict with architecture 8, and ADR-0004 settles them as unit names that `units` holds. | Approved with no change. |
| 1 (version 1.1) | No blocking issue. The Architect reviewed the change from version 1.0 to 1.1. In 2.7, it checked the 15-digit limit with its examples and its reason, the `to taste` wording, and the new `NOT_A_NUMBER` condition. It also checked the `ValueError` rows of 2.11 and 2.12. It tested the digit limits of `int`, `Fraction`, and `tomllib` in Python 3.14.3, which has the same limits as Python 3.13. Two points go to later designs: upper bounds on servings in F05, F06, and F09, and an F04 message for `NOT_A_NUMBER` that fits a 16-digit number. | Approved with no change. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-10 | First draft. |
| 1.0 | 2026-11-10 | Approved by Troy. |
| 1.1 | 2026-11-10 | Limits the number that `parse_quantity` reads to 15 digits, and makes clear that `to taste` takes one or more whitespace characters between its words (2.7). Adds a `ValueError` to `to_text` (2.11) and `to_rounded_text` (2.12) for a rounded amount with more than 4,300 digits before the point. |
