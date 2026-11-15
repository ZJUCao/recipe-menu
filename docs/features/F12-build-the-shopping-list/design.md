---
troy-doc: "F12-design"
lang: "en"
version: "1.0"
updated: "2026-11-15"
status: "Approved by Troy on 2026-11-15"
mirror: "design.zh-CN.md"
---

# F12 Build the shopping list: interface design

## 1. Feature

- ID and name: F12 Build the shopping list
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: F01, F03, F04, F06

## 2. Interfaces

F12 builds the domain module `shopping` in `src/recipe_menu/shopping/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.shopping` exports four names: the values `ShoppingLine` (2.1), with its method `amount_text` (2.2), `ShoppingGroup` (2.3), and `ShoppingList` (2.4), and the function `build_shopping_list` (2.5). Its `__init__.py` lists them in `__all__`. The other files behind them are the Developer's choice. F12 has no command and no message, so `shopping` has no `messages.py` (architecture 8). F13's `shop` calls `build_shopping_list`, and writes the list in the terminal and in the Markdown checklist. The F13 prototype `docs/prototypes/F13-shop.md` shows that list, and its table "How the example adds up" gives the source of each line.

The table maps each part of the requirement to the interfaces that meet it. The numbered rules are those of [requirements 3](../../requirements.md#3-how-users-interact-with-it), "The shopping list".

| The requirement says | F12 gives |
| --- | --- |
| F12 turns a week menu into the shopping list by the rules of section 3: scale, merge, add up, leave out the pantry, group, and round ([requirements 4](../../requirements.md#4-features)). | `build_shopping_list` (2.5). It takes the `WeekMenu`, its recipes, the `Catalog`, and the `Pantry`, and gives a `ShoppingList` (2.4). |
| 1. It scales each dish's ingredients by the dish's servings divided by the recipe's servings. | Step 3 of 2.5: `Quantity.scale` with `Fraction(dish.servings, recipe.servings)` (F01 design 2.9). |
| 2. It merges the lines of each catalog ingredient from all dishes into one line. | One `ShoppingLine` (2.1) for each ingredient that the menu uses. Ingredients are compared by equality (choice 3). |
| 3. It adds up mass in grams, volume in millilitres, and each count unit on its own. | `ShoppingLine.amounts`, the sums that F01's `add_quantities` gives (F01 design 2.10). |
| 4. It shows quantities that cannot be added side by side on one line. | `amounts` holds one sum for each kind, in the order of choice 4, and `amount_text` joins them with ` + ` (2.2). |
| 5. It shows "to taste" for an ingredient that has no quantity in any dish. | An empty `amounts`, for which `amount_text` gives `to taste` or `适量` (choice 5). |
| 6. It leaves out the pantry's ingredients, and names the ones that the menu uses in one line at the end. | No line for a pantry ingredient, and `ShoppingList.pantry_used` (choice 6). |
| 7. It groups the lines by category in the catalog's order. Within a category, the lines follow the catalog's order of ingredients. | `ShoppingList.groups`, a tuple of `ShoppingGroup` values (2.3, choice 7). |
| 8 and 9. It rounds counts, grams, and millilitres up to whole numbers, and shows 1000 g or more in kg and 1000 ml or more in L, with at most two decimals. | `ShoppingLine.amount_text` (2.2), which writes each sum with F01's `Quantity.to_rounded_text` (choice 8). |
| A `ShoppingList` holds the week, the number of meals and of dishes, the lines grouped by category in catalog order, and the pantry ingredients that the menu uses ([architecture 5.2](../../architecture.md#52-values)). | The five fields of 2.4: `week`, `meal_count`, `dish_count`, `groups`, and `pantry_used` (choices 1 and 9). |

These rules hold for every interface below:

- `shopping` imports only `lang`, `units`, `catalog`, `recipes`, and `menus` from the package ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)). It does not import `settings`, so it never names a `Meal`. It walks `WeekMenu.slots`, which already come in the order of the meals.
- `shopping` reads no file, writes no file, prints nothing, reads nothing of the outside world, and keeps no state (architecture 4 and 8). It turns values that other modules read into the list, so its tests need no files.
- Every value is a frozen dataclass with `slots=True`, and its collections are tuples (architecture 8). Every amount stays an exact `Fraction` (ADR-0007).
- `build_shopping_list` never raises for values that the readers gave with no error. The exceptions in the Errors tables below come from wrong calls, which are bugs ([architecture 6](../../architecture.md#6-error-handling)).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. A doc comment names the Chinese "to taste" by its code points, U+9002 U+91CF, as the code of `units` does.
- No F12 interface has a performance target. PT01 times F13's `shop`, which calls `build_shopping_list` once (choice 11). `build_shopping_list` calls single-purpose internal functions (R04).

The design makes these choices. 2.1 to 2.5 give their rules.

1. **Three values, grouped in the value.** `ShoppingList.groups` is a tuple of `ShoppingGroup` values, one for each category that has a line, in the catalog's order of categories. A `ShoppingGroup` holds its `Category` and its `ShoppingLine` values, in the catalog's order of ingredients. So F13 writes the headings and the lines in the order of the tuples, and sorts nothing. Architecture 5.2 names `ShoppingList` and `ShoppingLine`. `ShoppingGroup` is a helper value, as `MealSlot` is for `WeekMenu`. Each constructor checks its fields (2.1, 2.3, and 2.4), so a value that F13 or a test builds by hand keeps the rules that `build_shopping_list` keeps.
2. **The inputs.** `build_shopping_list(menu, recipes, catalog, pantry)` takes the `WeekMenu` (F06 design 2.6), a mapping from each recipe ID that a dish names to its `Recipe` (F04 design 2.3), the `Catalog`, and the `Pantry` (F03 design 2.5 and 2.7). F11's `menu show` reads each recipe that the menu names once into a dictionary (F11 design, choice 7), and F13 can pass the same dictionary. The mapping may hold more recipes, which F12 does not look at. Architecture 8 makes the collections of values tuples or frozensets. The mapping is an argument, not a value: F12 only reads it, and the list keeps nothing of it, as `add_quantities` takes any iterable (F01 design 2.10). F13 stops at the first error of each reader (architecture 6), so F12 gets only values that were read with no error. A wrong call raises `ValueError`: a dish names an ID that the mapping lacks, the mapping holds a recipe under another ID, or a recipe or the pantry holds an ingredient that is not in `catalog.ingredients` (2.5).
3. **Equality, not identity.** F12 compares ingredients and categories with `==` and their hashes, never with `is`. Recipes and the pantry refer to the catalog's `Ingredient` values (architecture 5.2), and one catalog holds no two equal ingredients, so two equal ingredients of one catalog are the same object (F03 design 2.4). So for the values that F13 passes, equality merges exactly what identity would merge. Categories differ: `Catalog` checks by equality that each ingredient's `category` is in `categories`, so it accepts an equal `Category` that is a separate object, as the Code Reviewer noted on F03's mock. Grouping by identity would put such an ingredient in no group. Equality puts it in the group of its category. A test that builds equal values in code then gets the same list as a test that reads the files.
4. **The order of the sums.** `add_quantities` gives its sums in the order in which their kinds first appear (F01 design 2.10). F12 feeds it each ingredient's scaled quantities in this order: the slots of `menu.slots`, which run Monday to Sunday and, within a day, in the order of `Meal`; the dishes of each slot, in the file's order; and the ingredient lines of each dish's recipe, in the file's order. A recipe that two dishes name gives its quantities twice, each scaled by its own dish. An ingredient that one recipe names twice gives both quantities. This order gives the lines of the prototype "Quantities that cannot be added" and of v0.1-S18. In v0.1-S18, Monday's `red-braised-pork` gives 葱 2 根 and 生抽 2 tbsp, before Friday's `scallion-noodles` gives 葱 1 把 and 生抽 10 g. So the scallion line holds 5 stalks and then 1 bunch, written `5 stalks + 1 bunch`. The soy sauce line holds 30 ml and then 10 g, written `30 ml + 10 g` (the example of 2.5).
5. **To taste.** An ingredient that no dish gives a quantity, such as 白胡椒粉 in the example week, gets a line with an empty `amounts`. `amount_text` writes it as `to taste` or `适量` (2.2). When some dishes give an ingredient a quantity and others use it to taste, the line holds only the sums of the quantities, because to taste adds nothing (F01 design 2.10). Its text then shows no "to taste", as rule 5 has it: "to taste" is for an ingredient that has no quantity in any dish. So the line does not say that another dish also uses the ingredient to taste.
6. **The pantry.** An ingredient of `pantry.ingredients` gets no line, whatever its quantities. When the menu uses it, it goes into `pantry_used`. A dish uses an ingredient when its recipe has a line for it, with a quantity or to taste. So 盐, which the example week uses only to taste, is in `pantry_used`, as the prototype's pantry line and v0.1-S16 show. A `Pantry` is a set with no order (F03 design 2.7), so F12 gives `pantry_used` the order of choice 7: by category in the catalog's order, and then in the catalog's order of ingredients. The example catalog gives 食用油, 盐, 糖, 生抽, and 花椒, the order of the prototype's line. A pantry ingredient that the menu does not use is not in `pantry_used`.
7. **The groups.** The groups follow `catalog.categories`, and the lines of a group follow `catalog.ingredients`. The catalog file may list the ingredients of one category in several places. F12 still gathers them under their category, in their order in the file. A category with no line has no group. That is a category that the menu does not use, or a category whose used ingredients are all in the pantry. So v0.1-S16 lists Vegetables and fruit and then Eggs, dairy, and tofu, and no other heading.
8. **Rounding.** `amounts` holds the exact sums that `add_quantities` gives, which are not rounded (F01 design 2.10, ADR-0007). The F12 row of the requirements says that F12 rounds. `ShoppingLine.amount_text(lang)` meets that. It writes each sum with F01's `Quantity.to_rounded_text` (F01 design 2.12), which rounds grams, millilitres, and counts up to whole numbers, and writes 1000 g or more in kg and 1000 ml or more in L, with at most two decimals. It joins the sums with ` + `. The texts come from `units`, whose unit labels are plain data (ADR-0004), and ` + ` is a symbol that belongs to no language (architecture 8). So `shopping` needs no `Message` and no `text`. F01's design planned that F13 writes each sum with `to_rounded_text`. With this choice, F13 writes each line's amounts with `amount_text`, which calls it. The rounding rules stay in one place, `units`, and F12's tests check them on the list. A sum is rounded once, after the whole week is added: two dishes that each need 1.5 stalks of scallion give 3 stalks, not 4. No requirement changes. F12 meets its row, and F01 still meets its own row, which says that F01 "writes a quantity in each language with the rounding rules of section 3". F13 owns every other text of the list.
9. **The counts.** `meal_count` is the number of slots of `menu.slots` that hold at least one dish, and `dish_count` is the number of dishes in all the slots. That is the count of F11's `menu show` (F11 design, choice 9) and of F06 design section 2, so `shop` and `menu show` count a week alike: 4 meals and 9 dishes in the example week, and 1 meal and 1 dish in v0.1-S16. `shopping` may not import `menu` (architecture 3), so it counts from `menu.slots` itself. A menu with no dish gives `ShoppingList(menu.week, 0, 0, (), ())`, and `recipes` may then be empty. F13 shows the prototype's line `The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.` when `dish_count` is 0. A menu whose dishes use only pantry ingredients, or only recipes with no ingredients, gives a list with dishes and no group. F13's design decides what `shop` shows and saves then.
10. **Numbers.** A recipe's amount has at most 15 digits (F01 design 2.7), so it is less than 10^15, and its denominator divides 10^14. `in_base_unit` multiplies it by at most 1000, for kg and L. The servings factor is at most 100, because a dish has at most 100 servings and a recipe at least 1 (F04 design, choice 2). So each scaled quantity is less than 10^20, and a sum of n quantities is less than n times 10^20. `to_rounded_text` raises `ValueError` only above 4,300 digits (F01 design 2.12). A sum of that size would need about 10^4279 recipe lines in one week, so `amount_text` never raises for a line that `build_shopping_list` gave. The denominators stay small too. Each scaled quantity's denominator divides 10^14 times a recipe's servings, so every sum's denominator divides 10^14 times the least common multiple of 1 to 100, a number of 55 digits.
11. **Speed.** PT01 asks that `shop` build and save the list of one PT01 week within 1 second on Troy's PC, the median of 5 runs (v0.1-S32). The week holds 63 dishes from 63 different recipes. A PT01 recipe has 12 ingredient lines (v0.1-S29), so F12 scales and adds 756 quantities and orders at most 300 ingredients. Each quantity costs two `Fraction` multiplications, one for the servings and one in `in_base_unit`, one addition, and two dictionary lookups by ingredient. That is some microseconds each in CPython. The order costs one pass over the catalog's 300 ingredients. So `build_shopping_list` should take about 0.01 s, and `amount_text` for at most 300 lines a few milliseconds more. `shop` reads what `menu show` reads, plus the pantry, and `menu show` of the same week takes a median of 0.187 s on Troy's PC (F11's PT01 baseline). So `shop` should stay near 0.2 s, with F13's own output and file still to add. These are estimates, not measurements. F13's test plan can time `shop` on a PT01 folder. `build_shopping_list` keeps its dictionaries for one call only, and no module keeps a cache (architecture 8).

The v0.1 scenarios that reach F12 through `shop` hold with these choices:

- The prototype's table "How the example adds up": every line of the example week 2026-W47 and its pantry line, with 4 meals and 9 dishes (the example of 2.5). 菜心 is 1 斤 on Monday and 2 斤 on Sunday, so its sum is 1500 g, written `1.5 kg`. 郫县豆瓣酱 is 1 tbsp, so its sum is 15 ml. 白胡椒粉 has no quantity, so it is `适量`.
- v0.1-S14: a menu with no dish gives a list whose `dish_count` is 0, for which `shop` prints its line and saves no file (choice 9).
- v0.1-S16: 3 servings of the 2-serving `tomato-egg` give Tomato 450 g, Scallion 3/2 stalks, written `2 stalks`, and Egg 9/2 pieces, written `5 pieces`, in two groups. The list has 1 meal and 1 dish, and the pantry ingredients 食用油, 盐, and 糖 (choices 6 to 9).
- v0.1-S17 and v0.1-S26: the 14 lines of the example week in six groups, and the pantry line.
- v0.1-S18: `5 stalks + 1 bunch` and `30 ml + 10 g`, and `5 根 + 1 把` in Chinese (choice 4).
- v0.1-S32: PT01 (choice 11).

This design leaves no point for Troy to decide. The pantry line's text, the headings, the count line, and the Markdown file are F13's, and F13's design brings their open points to Troy.

These later features are meant to build on F12. Their own designs decide the details.

- F13's `shop` reads its files as `menu show` does (F11 design, choice 7), reads the pantry with `read_pantry(context.folder, catalog)` after the catalog, and stops at the first error of each reader. It keeps each recipe that the menu names in a dictionary for one run, and calls `build_shopping_list(menu, recipes, catalog, pantry)`.
- F13 shows its line for a week with no dish when `dish_count` is 0. It decides what `shop` shows and saves for a list with dishes and no group (choice 9).
- F13 writes each group's heading with `group.category.name.get(lang)`, each line with `line.ingredient.name.get(lang)` and `line.amount_text(lang)`, and the counts with `meal_count` and `dish_count`. It writes the same values in the terminal and in the Markdown checklist.
- F13 settles the text of the pantry line from `pantry_used`. The F03 design notes that the English pantry line of the prototype writes "cooking oil" where the catalog writes "Cooking oil", and that F13's design must settle that line (F03 design section 2).
- The Architect suggested in the F02 review that F13 can lay out the list as one `format_table` table, with the category headings between the lines. The Code Reviewer of F11's implementation noted that reading the catalog and stopping at the first error repeat in `browse`, `search`, and `menu`, and that F13's design may share them. Both are F13's to decide.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/shopping/__init__.py`, which imports the four names and lists them in `__all__`, and two internal files, such as `_model.py` for the three values and `_build.py` for `build_shopping_list`. It defines the three values with their fields and doc comments, without the checks of their constructors. Its `amount_text` and its `build_shopping_list` raise `NotImplementedError`. So a new test fails against the mock (R09) when it calls `build_shopping_list` or `amount_text`, also when it expects a `ValueError` or the empty list of a menu with no dish. A test also fails against the mock when it expects a constructor to raise. A test of a wrong call must expect `ValueError` or `TypeError`, not any exception, because the mock raises `NotImplementedError`. These tests pass against the mock and break R09: a test that checks only the module's names, or only the fields and the equality of a valid value, such as `ShoppingList(week, 0, 0, (), ())`. Each such test must also check something that the mock gets wrong. By estimate, the mock changes 3 files in about 200 lines, within R03. The implementation (PR 5) adds the checks and `amount_text` to `_model.py`, and `build_shopping_list` with its internal functions to `_build.py`, or to one more internal file. By estimate, it changes 2 or 3 files in about 300 lines, within R03 too. So neither PR needs a soft-limit reason.

### 2.1 `ShoppingLine`

- Module: shopping
- Purpose: One line of the shopping list: a catalog ingredient and its sums for the week ([architecture 5.2](../../architecture.md#52-values)). `amounts` holds one sum for each kind that cannot be added to another: grams, millilitres, and each count unit. An empty `amounts` means "to taste".

Signature:

```python
@dataclass(frozen=True, slots=True)
class ShoppingLine:
    ingredient: Ingredient
    amounts: tuple[Quantity, ...]

    # Method: amount_text (2.2).
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `ingredient` | `Ingredient` | The catalog ingredient, such as Scallion and 葱. | None |
| `amounts` | A tuple of `Quantity` values | The exact sums of the week, as `add_quantities` gives them, such as 5 stalks and 1 bunch. | Each quantity has an amount, so none is to taste. Each unit is `Unit.G`, `Unit.ML`, or a count unit, and no two quantities have the same unit. Empty for to taste. |

- Return value: A `ShoppingLine`. Two lines are equal when their two fields are equal, and a `ShoppingLine` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `ingredient` is not an `Ingredient`, or `amounts` is not a tuple or holds an item that is not a `Quantity`. |
| `ValueError` | A quantity of `amounts` is to taste, has a unit other than `Unit.G`, `Unit.ML`, and the count units, such as `Unit.KG` or `Unit.TBSP`, or has the same unit as another quantity of `amounts`. |

- Side effects: None
- Performance target: None

Example:

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

- Module: shopping, a method of `ShoppingLine` (2.1)
- Purpose: Writes the line's amounts by the rules of the shopping list: side by side (rule 4), "to taste" (rule 5), rounded up (rule 8), and in kg or L from 1000 g or 1000 ml (rule 9). F13 writes the text after the ingredient's name, in the terminal and in the Markdown checklist (choice 8).

Signature:

```python
def amount_text(self, lang: Lang) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language to write in. | None |

- Return value: The text, by these rules:
  - An empty `amounts` gives `TO_TASTE.to_rounded_text(lang)`, which is `to taste` in English and `适量` in Chinese.
  - Otherwise, `amount_text` writes each quantity of `amounts`, in its order, with `to_rounded_text(lang)` (F01 design 2.12), and joins the texts with ` + `: a space, U+002B PLUS SIGN, and a space. So 5 stalks and 1 bunch give `5 stalks + 1 bunch` and `5 根 + 1 把`. 1500 g gives `1.5 kg`, 1001 g gives `1.01 kg`, and 3/2 stalks give `2 stalks`.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | A rounded amount has more than 4,300 digits before the point (F01 design 2.12). Only a line built by hand can hold such an amount. A line that `build_shopping_list` gave cannot (choice 10). |

- Side effects: None
- Performance target: None

Example:

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

- Module: shopping
- Purpose: The lines of one category, in the catalog's order of ingredients (rule 7). `ShoppingList.groups` holds one group for each category that has a line (choice 1).

Signature:

```python
@dataclass(frozen=True, slots=True)
class ShoppingGroup:
    category: Category
    lines: tuple[ShoppingLine, ...]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `category` | `Category` | The category, such as Vegetables and fruit and 蔬菜水果. | None |
| `lines` | A tuple of `ShoppingLine` values | The lines of the category, in the catalog's order of ingredients. | At least one line. The `category` of each line's ingredient equals `category`. No two lines have equal ingredients. |

- Return value: A `ShoppingGroup`. Two groups are equal when their two fields are equal, and a `ShoppingGroup` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `category` is not a `Category`, or `lines` is not a tuple or holds an item that is not a `ShoppingLine`. |
| `ValueError` | `lines` is empty, the category of a line's ingredient does not equal `category`, or two lines have equal ingredients. |

- Side effects: None
- Performance target: None

Example:

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

- Module: shopping
- Purpose: The shopping list of one week ([architecture 5.2](../../architecture.md#52-values)): the week, the number of meals and of dishes, the lines grouped by category in the catalog's order, and the pantry ingredients that the menu uses. `build_shopping_list` gives it, and F13 writes it.

Signature:

```python
@dataclass(frozen=True, slots=True)
class ShoppingList:
    week: IsoWeek
    meal_count: int
    dish_count: int
    groups: tuple[ShoppingGroup, ...]
    pantry_used: tuple[Ingredient, ...]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `week` | `IsoWeek` | The week of the menu, such as `2026-W47`. | None |
| `meal_count` | `int` | The number of meals of the week that hold at least one dish (choice 9). | 0 or more, and at most `dish_count`. 0 only when `dish_count` is 0. Not a `bool`. |
| `dish_count` | `int` | The number of dishes of the week. | 0 or more. Not a `bool`. |
| `groups` | A tuple of `ShoppingGroup` values | One group for each category that has a line, in the catalog's order of categories (choice 7). | No two groups have equal categories. Empty when `dish_count` is 0. |
| `pantry_used` | A tuple of `Ingredient` values | The pantry's ingredients that the menu uses, in the order of choice 6. | Empty when `dish_count` is 0. No ingredient appears twice in `pantry_used` and the lines of `groups` together. |

- Return value: A `ShoppingList`. Two lists are equal when their five fields are equal, and a `ShoppingList` is hashable. A `ShoppingList` holds no catalog, so it cannot check the order of `groups` and `pantry_used`. `build_shopping_list` gives that order.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `week` is not an `IsoWeek`, `meal_count` or `dish_count` is not an `int` or is a `bool`, `groups` is not a tuple of `ShoppingGroup` values, or `pantry_used` is not a tuple of `Ingredient` values. |
| `ValueError` | `meal_count` or `dish_count` is less than 0, `meal_count` is more than `dish_count`, or `meal_count` is 0 and `dish_count` is not. |
| `ValueError` | `dish_count` is 0, and `groups` or `pantry_used` is not empty. |
| `ValueError` | Two groups have equal categories, or an ingredient appears twice in `pantry_used` and the lines of `groups` together. |

- Side effects: None
- Performance target: None

Example:

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

- Module: shopping
- Purpose: Turns a week menu into its shopping list by the rules of [requirements 3](../../requirements.md#3-how-users-interact-with-it), "The shopping list": scale, merge, add up, leave out the pantry, and group ([requirements 4](../../requirements.md#4-features), F12). The `amount_text` of each line rounds (2.2).

Signature:

```python
def build_shopping_list(
    menu: WeekMenu,
    recipes: Mapping[str, Recipe],
    catalog: Catalog,
    pantry: Pantry,
) -> ShoppingList: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `menu` | `WeekMenu` | The week menu, as `read_week_menu` gave it with no error (F06 design 2.9). | None |
| `recipes` | A `Mapping` from `str` to `Recipe` | The recipe of each ID that a dish of `menu` names, as `read_recipe` gave it with no error (F04 design 2.6). | Holds each ID that a dish names, and `recipes[recipe_id].id` is `recipe_id`. May hold other recipes, which F12 does not look at. May be empty when `menu` holds no dish. |
| `catalog` | `Catalog` | The catalog that the recipes and the pantry were read with (F03 design 2.8). | Holds every ingredient of the recipes that the dishes name, and every ingredient of `pantry`. |
| `pantry` | `Pantry` | The pantry, as `read_pantry` gave it with `catalog` (F03 design 2.9). | Only the constraint on `catalog`. |

- Return value: A `ShoppingList` (2.4), built in these steps. "Equal" means equal by `==` (choice 3).

1. It checks that every ingredient of `pantry.ingredients` is in `catalog.ingredients`.
2. It counts `meal_count`, the slots of `menu.slots` that hold at least one dish, and `dish_count`, the dishes of all the slots (choice 9).
3. It goes through the slots of `menu.slots` in their order, the dishes of each slot in their order, and the ingredient lines of each dish's recipe in their order (choice 4). For each dish, it takes `recipe = recipes[dish.recipe_id]` and `factor = Fraction(dish.servings, recipe.servings)`. For each `RecipeIngredient` of `recipe.ingredients`, it checks that its `ingredient` is in `catalog.ingredients`. It then keeps the line's `quantity.scale(factor)` for that ingredient, after the quantities that it kept before for an equal ingredient.
4. For each ingredient that it kept quantities for, `add_quantities` of those quantities, in their order, gives the line's `amounts` (F01 design 2.10).
5. It orders those ingredients by the position of their category in `catalog.categories`, and then by their position in `catalog.ingredients` (choice 7).
6. In that order, each ingredient that is in `pantry.ingredients` goes into `pantry_used`, and each other ingredient becomes a `ShoppingLine` with its `amounts` (choice 6).
7. It puts the lines of each category into one `ShoppingGroup`, in that order, and gives `ShoppingList(menu.week, meal_count, dish_count, groups, pantry_used)`.

A menu with no dish gives `ShoppingList(menu.week, 0, 0, (), ())` (choice 9).

Errors:

`build_shopping_list` checks its arguments in the order of the steps, and raises at the first wrong one. F13 passes values that the readers gave with no error, from one catalog, so it never gets these errors.

| Error | When |
| --- | --- |
| `ValueError` | An ingredient of `pantry.ingredients` is not in `catalog.ingredients` (step 1). |
| `ValueError` | A dish of `menu` names an ID that `recipes` does not hold, or `recipes[dish.recipe_id].id` is not `dish.recipe_id` (step 3). |
| `ValueError` | An ingredient of a recipe that a dish names is not in `catalog.ingredients` (step 3). |

- Side effects: None. It reads no file and changes none of its arguments.
- Performance target: None. PT01 times F13's `shop`, which calls it once (choice 11).

Example:

The example builds in code the example data of `docs/prototypes/example-data.md`, which `tests/data/example/` holds: the catalog, the pantry, the ingredient lines of the seven recipes, and the menu of 2026-W47. It adds the recipe `scallion-noodles` of v0.1-S18. Each recipe has 2 servings, as every example recipe has, and a short name and steps, which F12 does not read. `written` stands in for F13: it writes each heading and each line in one language. The example then builds the weeks of v0.1-S16 and v0.1-S18, a week with no dish, and four wrong calls.

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

## 3. Changes to existing interfaces

None. No interface that F01 to F11 implemented changes. F12 adds the module `shopping` and changes no file of another module.

F12 uses these interfaces as their designs give them, and changes none of them:

- F01's `Quantity`, `Quantity.scale`, `Quantity.to_rounded_text`, `TO_TASTE`, `Unit`, `UnitKind`, and `add_quantities` in `units` (F01 design 2.2 to 2.4, 2.9, 2.10, and 2.12), and `Lang` in `lang` (F01 design 2.1).
- F03's `Catalog`, `Category`, `Ingredient`, and `Pantry` in `catalog` (F03 design 2.4, 2.5, and 2.7).
- F04's `Recipe` and `RecipeIngredient` in `recipes` (F04 design 2.1 and 2.3).
- F06's `Dish`, `IsoWeek`, `MealSlot`, and `WeekMenu` in `menus` (F06 design 2.1 and 2.4 to 2.6).

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `shopping` is the domain module of architecture 3: the folder `src/recipe_menu/shopping/`, whose `__init__.py` lists the four names in `__all__`, with no `messages.py` because it has no `Message` (architecture 8). The Architect's model of section 2 imports only `lang`, `units`, `catalog`, `recipes`, and `menus`, the five modules that its row allows, and mypy in strict mode accepts it. It never imports `settings`. Only the example imports `Meal`, to build a `WeekMenu`. It reads no file, prints nothing, and keeps no state (architecture 4 and 8). The four inputs are those of architecture 5.3. The five fields of `ShoppingList` and the two of `ShoppingLine` are those of 5.2, with an empty `amounts` for to taste. Every value is a frozen dataclass with `slots=True` and tuple fields, and every amount stays a `Fraction` (ADR-0007). Point 2(a) of the brief: choice 3 is within the architecture as written. The note of 5.2 gives the reason why merging works: recipes and the pantry refer to the catalog's own `Ingredient` values. A catalog holds no two equal ingredients, so for the values that the readers give, `==` and `is` merge exactly the same ingredients. The model built the example week once from the files and once from the code of 2.5, and the two lists are equal. Equality also groups the case that identity would lose, an ingredient whose category is an equal but separate `Category`, which `Catalog` accepts. So no architecture change is needed. The next time the architecture changes, the Architect will reword the note of 5.2 to say that the list merges equal ingredients, which for the readers' values are the same object. The new wording changes no rule. Point 2(b): `ShoppingGroup` needs no architecture change. 5.2 lists the values that cross modules and leaves the exact names and signatures to the designs, and `ShoppingGroup` is the shape of 5.2's "the lines grouped by category in catalog order". It is a helper value, like `Severity`, `Steps`, `FolderUse`, `Day`, `MealSlot`, `Creation`, and `FileCreation`, which 5.2 does not list either. Choice 2's `Mapping` argument fits architecture 8, whose rule on tuples and frozensets is for the collections of values. F12 only reads the mapping and keeps nothing of it, as `datafile`'s `read_text` reads a `Mapping` table and `add_quantities` reads any iterable. |
| Follows the error handling and naming conventions | Pass | `shopping` reads no file, so it has no `Problem`. `build_shopping_list` raises `ValueError` only for a wrong call, and each constructor raises `TypeError` or `ValueError` only for wrong fields, as the values of F01 to F06 do. A wrong call is a bug, which architecture 6 leaves to Python's traceback, and the design catches nothing. In the model, each of the 22 `# raises` lines raises the error that it names. 3,000 random menus on random catalogs raised nothing in `build_shopping_list` or `amount_text`, with random pantries, quantities of up to 15 digits in every unit, servings from 1 to 100, and categories that are equal but separate objects. So the readers' values never reach these errors. Choice 10's bound holds: each scaled quantity is less than 10^20, and the denominator of every sum divides 10^14 times the least common multiple of 1 to 100, a number of 55 digits. Point 2(c): choice 8 fits architecture 3, 4, and 8 and ADR-0004. `amount_text` uses only `units` and `lang`, which the row of `shopping` allows. It gives a string and prints nothing, as `Quantity.to_rounded_text` and `Meal.label` do. ADR-0004 keeps the names of units beside their type, as plain data in `units`, and F01's design put the to-taste text there too. ` + ` is a symbol that belongs to no language, and the F13 prototype writes it in both languages. So `shopping` needs no `Message`, and it builds no English plural and no list by hand. The F12 row of the requirements is met with no requirement change. F12's own method writes the rounded text, the exact amounts follow ADR-0007, and the F01 row still holds, because `to_rounded_text` keeps the rounding rules. F01's line "F13 writes each sum with `Quantity.to_rounded_text`" is a plan, not an interface, so moving that call into F12 changes no implemented interface. Names follow PEP 8 and the names of 5.2, and doc comments name the Chinese "to taste" by its code points. Note 1, not blocking (choice 2, and 2.5: the constraint on `recipes` and the second row of Errors): "`recipes[recipe_id].id` is `recipe_id`" and "is not `dish.recipe_id`" can be read as Python's `is`. Two equal IDs can be separate `str` objects, so the design can say "equals" and "does not equal", as choice 3 does for ingredients. Choice 2's "the mapping holds a recipe under another ID" can also say "a recipe that a dish names", because 2.5 checks only those. Note 2, not blocking (choice 10): a count of more than 4,300 digits needs a sum of at least 10^4300, so about 10^4280 recipe lines, not 10^4279. For grams and millilitres it needs about 10^4283, because kg and L divide by 1,000. The conclusion holds. |
| Does not duplicate an existing interface | Pass | F12 scales with `Quantity.scale`, converts and adds with `add_quantities`, and rounds and writes with `Quantity.to_rounded_text`, and builds none of them again. `amount_text` joins the texts that `to_rounded_text` gives, so the rounding rules stay in `units`, and F13 writes each line's amounts through one method, in the terminal and in the Markdown checklist. The meal and dish counts repeat two lines of the internal count of F11's `menu`, because `shopping` may not import `menu` (architecture 3), and F06 design section 2 plans the same count for both. The checks of the constructors are internal to `shopping`. The pantry rule of choice 6 uses `Pantry.ingredients` and the catalog's order, and adds no lookup to `catalog`. |
| Depends only on features earlier in the order | Pass | F12 uses `Lang` and `units` from F01, `BiText` from F02 through the catalog's names, `catalog` from F03, `recipes` from F04, and `menus` from F06, whose `MealSlot` holds F05's `Meal`. All of these features come before F12 and pass their tests on main. F01, F03, F04, and F06 are the soft dependencies of the F12 row. The plans for F13 in section 2 leave the details to F13's design, so they bind no later design. F12 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. F13 must pass values that the readers gave with no error, from one catalog, and the three `ValueError` rows of 2.5 catch any other call (choice 2). The order of the sums rests on the order of `WeekMenu.slots`, which the constructor of `WeekMenu` enforces (choice 4). F13 writes each line's amounts with `amount_text` and every other text itself: the pantry line from `pantry_used`, the headings, the counts, and what `shop` shows for a week with no dish or for a list with no group (choices 8 and 9). The bound of choice 10 rests on the 15 digits of `parse_quantity` and the 100 servings of a recipe and a dish, and the design names both. `build_shopping_list` keeps its dictionaries for one call, and no module keeps a cache. Point 1 of the brief: choices 1 to 11 hold on the model. Choice 1: the constructors reject the 18 wrong values of 2.1, 2.3, and 2.4, and never a value that `build_shopping_list` gives. Choice 4: v0.1-S18 gives `5 stalks + 1 bunch` and `30 ml + 10 g`. Choices 5 and 6: 白胡椒粉 gives `to taste` and `适量`, and 盐, which the example week uses only to taste, is in `pantry_used`. Choice 7: a catalog that lists the ingredients of one category in several places still gives one group for each category, in the catalog's order. Choice 9: a week with no dish gives `ShoppingList(IsoWeek(2026, 46), 0, 0, (), ())`. Choice 11: on a PT01 folder from `tests/pt01_support.py`, the week 2026-W26 gave 63 dishes from 63 recipes, 756 ingredient lines, 21 meals, 6 groups, 290 lines, and 10 pantry ingredients. `build_shopping_list` took a median of 5.1 ms over 200 calls, and `amount_text` took 1.9 ms for all 290 lines in both languages. A stand-in for `shop` reads what `menu show` reads plus the pantry, builds the list, prints it, and writes a Markdown file. In the same set of runs on Troy's PC, 5 runs of it gave a median of 0.222 s, and 5 runs of `menu show 2026-W26` gave 0.209 s. So choice 11's estimates of about 0.01 s and about 0.2 s hold. For the Developer: one dictionary of the catalog's positions serves steps 1, 3, and 5. A membership test on the tuple `catalog.ingredients` compares by `==` and adds about 13 ms on a PT01 week. |
| Changes an implemented interface only through the change flow | Pass | Section 3 rightly says None. The PR adds only the two design files, and `src/recipe_menu/shopping/` does not exist on main. Every name that F12 uses exists on main with the signature that section 3 names, and the model ran on main's code with no change to another module. F01's plan for F13 and the note of architecture 5.2 on identity are not interfaces, and the doc comment of `RecipeIngredient` stays true for the readers' values. Point 5 of the brief: the split is right. The mock's 3 files, `__init__.py`, `_model.py`, and `_build.py`, define the values without their checks, and `amount_text` and `build_shopping_list` raise `NotImplementedError`. So every test that calls either one, expects a constructor to raise, or expects the empty list fails against the mock (R09). `NotImplementedError` is a `RuntimeError`, so a test of a wrong call that names `ValueError` or `TypeError` fails too. The tests that pass against the mock are those that check only the four names, or only the fields, the equality, the hash, or the frozenness of a valid value, such as `ShoppingList(week, 1, 1, (), (oil,))`. The design names the first two kinds, and the Test Manager can add the hash and the frozenness. The model has 3 files and about 270 lines with short doc comments. With full Google-style doc comments, a mock of about 200 lines in 3 files and an implementation that changes 2 or 3 files in about 300 lines both fit R03, so neither PR needs a soft-limit reason. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | Each point of the summary matches the design: no command and no file (section 2), scaling with 450 g of tomato (v0.1-S16), merging with the scallion line (choice 4), to taste and only the amount (choice 5), the pantry line in catalog order with salt (choice 6), the order and no empty category (choice 7), rounding once on the week's total, with kg and L (choice 8), the 6 categories, 14 items, 4 meals, and 9 dishes, the empty list (choice 9), and the two risks (choices 5 and 11). The model confirms each number. Neither language holds an internal ID, and each is within 2,000 characters, with 658 in Chinese and 1,750 in English. Point 4 of the brief: no point needs to go to Troy. Choice 5 follows rule 5 as Troy approved it, "to taste" for an ingredient that has no quantity in any dish, and F01's `add_quantities`, in which to taste adds nothing. Showing "to taste" next to an amount would change the requirements, which Troy can ask for after reading the risk. The Architect recommends keeping choice 5. Choice 8 changes nothing that Troy types or sees, and the terminal, the file, and the rounding stay as the prototype shows them, so it is not Troy's to decide. The Architect recommends keeping it. Note 3, optional (summary, the first risk): "slightly" and "略" judge how much too little Troy may buy, which the design does not say. The summary can drop the word, or choice 5 can say the consequence. Note 4, optional (summary, the second risk): the summary can add the Architect's measurements in this section, about 0.005 s for this part and about 0.22 s for a stand-in for `shop`, which is still not the real command. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 11 choices against the requirements, the architecture, ADR-0004 and ADR-0007, the designs of F01, F03, F04, F06, and F11, the F13 prototype, and v0.1-S14, v0.1-S16 to v0.1-S18, and v0.1-S32. Each file has 10 code blocks, all `python`, each equal to its mirror, and the two files have the same 11 headings and 73 table rows. `ruff format --check` with ruff 0.17.4 and the project's settings reports both files formatted. On main's code, with Python 3.13.18 on Windows, the Architect built a model of section 2 in a copy of `src/` and ran the 5 examples: all 35 assertions and all 22 `# raises` hold. The model also read fresh copies of `tests/data/example/` with main's readers. The week 2026-W47 gives every line of both outputs of the F13 prototype, in English and in Chinese, with 6 categories, 14 items, 4 meals, 9 dishes, and the pantry ingredients 食用油, 盐, 糖, 生抽, and 花椒, and its list equals the one that the example of 2.5 builds in code. The files of v0.1-S16 give Tomato 450 g, Scallion 2 stalks, Egg 5 pieces, 1 meal, 1 dish, and Cooking oil, Salt, and Sugar. The files of v0.1-S18 give `5 stalks + 1 bunch`, `5 根 + 1 把`, and `30 ml + 10 g`, and a week with no dish gives the empty list. No test ran, because the PR changes no code. Notes 1 to 4 do not block. | Approved. The Interface Designer can settle notes 1 to 4 in a revision, or leave them. Troy approves the design (R18, with `troy_approves_first = 16`). The Architect rewords the note on identity in architecture 5.2 the next time the architecture changes. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-15 | First draft. |
| 1.0 | 2026-11-15 | Approved by Troy. |
