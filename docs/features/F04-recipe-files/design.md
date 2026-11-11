---
troy-doc: "F04-design"
lang: "en"
version: "1.0"
updated: "2026-11-11"
status: "Approved by Troy on 2026-11-11"
mirror: "design.zh-CN.md"
---

# F04 Recipe files: interface design

## 1. Feature

- ID and name: F04 Recipe files
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: F01, F02, F03

## 2. Interfaces

F04 builds the domain module `recipes` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.recipes` exports `Recipe`, `RecipeIngredient`, `Steps`, `is_recipe_id`, `list_recipe_ids`, `read_recipe`, and `read_recipes`, and its `__init__.py` lists them in `__all__`. Its messages live in `recipes/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. F04 also adds `list_toml_files` to `datafile`, and moves F03's helpers for the shape of a file from `catalog` into `datafile` (section 3). A recipe file has the layout of `recipes/tomato-egg.toml` in `docs/prototypes/example-data.md`, and the F07 prototype shows how `check` reports its problems.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F04 gives |
| --- | --- |
| A recipe has an ID, which is its file name without the extension, such as `tomato-egg` ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | The ID rule of `is_recipe_id` (2.4), and `list_recipe_ids` (2.5), which gives the IDs from the file names. |
| It reads every file in `recipes/` into recipes with the parts of section 3: the names, the servings, the tags, the ingredients with their quantities and notes, and the steps. | `read_recipes` (2.7) and `read_recipe` (2.6). They give `Recipe` values (2.3), which hold `RecipeIngredient` (2.1) and `Steps` (2.2) values. |
| A quantity without a unit uses the ingredient's default unit from the catalog (requirements 3, [architecture 5.2](../../architecture.md#52-values)). | `read_recipe` reads each amount with F01's `parse_quantity` and the default unit of the ingredient (2.6). |
| It reports each problem with its file and place: a syntax mistake, a missing part, an unknown ingredient or tag, or a wrong quantity or unit. | The `Problem` values that `list_recipe_ids`, `read_recipe`, and `read_recipes` return, each with its file and the places of 2.6. |
| A missing language is a warning. | The warnings of 2.6 for a name, a note, or steps that lack one language. |
| `recipes` lists the recipe IDs from the file names in `recipes/` without parsing the files ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). | `list_recipe_ids` (2.5), through `datafile`'s `list_toml_files` (3.1). |

These rules hold for every interface below:

- `recipes` imports only `lang`, `units`, `text`, `datafile`, and `catalog` from the package ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `recipes` reaches the disk only through `datafile`: it lists `recipes/` with `list_toml_files` and reads each file with `read_toml`. No interface writes a file, prints, reads the environment, or keeps state.
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). It checks the whole file, records a `Problem` for each mistake, and goes on, so one `check` run lists every problem. The exceptions in the Errors tables below come from wrong calls, which are bugs.
- Every value is a frozen dataclass with `slots=True`, and its collections are tuples (architecture 8).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F04 interface has a performance target. `check`, `list`, and `search` read 1,000 recipes within PT01's 1 second ([requirements 7.1](../../requirements.md#71-performance-targets), architecture 8, ADR-0002). So `read_recipes` lists `recipes/` once and reads each file once, and its time grows in proportion to the size of the files. Each lookup in the catalog takes time in proportion to the length of the name (F03 design 2.6).

A reader of one recipe and a reader of every recipe differ in what they list (architecture 8):

- `list_recipe_ids` reads no file. It gives the IDs from the file names in `recipes/`, so F06 can report an unknown recipe ID, and F09 can tell an unknown ID from a broken file, without parsing any recipe.
- `read_recipe` reads one file and does not list `recipes/`. `show`, `menu show`, and `shop` call it only for the recipes that they name, with IDs that `list_recipe_ids` gave, directly or through a week menu that F06 checked against them.
- `read_recipes` lists `recipes/` once with `list_recipe_ids` and reads each file with `read_recipe`. `list`, `search`, and `check` call it.

The design makes these choices. The subsection in parentheses after each choice gives its rules.

1. A recipe ID has only the small letters `a` to `z`, the digits, and `-`, starts with a letter or a digit, and is not a Windows device name (2.4). Troy decided to keep this rule rather than also allow Chinese characters (section 4, finding 1). A file name needs less on Windows and Linux: no separator, no `:`, no U+0000, not `.` or `..`, none of the other characters that Windows forbids, no dot or space at the end, no device name, and no two names that differ only in case ([architecture 1](../../architecture.md#1-context-and-constraints), F03 design 2.1). The rule asks more for four reasons. Every ID in the prototypes and the example data is lowercase ASCII. You type IDs on the command line and in menu files. The rule keeps look-alike and invisible characters out of IDs. Its letters have one case, so no two IDs differ only in case. No ID looks like an option such as `-x` either. A file such as `红烧肉.toml` gets an error that asks you to rename it (2.5).
2. A recipe makes from 1 to 100 servings (2.3 and 2.6). Troy decided to keep this range, and to use it for the settings, a dish, and `show --servings` too (section 4, finding 2). The bound keeps small every servings number that F09 shows and that F12 divides by. A message shows a number from the file only when it has at most 15 digits, as F01 limits an amount, so `Problem` never meets F02's limit of 4,300 digits.
3. In the name and a note, a blank text counts as a missing language. In the steps, an empty list does (2.6). The steps hold only lists, so a text in the steps, even `""`, is an error. One missing language gives a warning when the other language is usable. A name or steps with neither language give an error, and a note with neither language is no note.
4. `read_recipe` gives no recipe when the file has an error, and gives the recipe with its warnings otherwise (2.6). No later reader checks anything against a recipe, and every command other than `check` stops at the first error (architecture 6), so no command uses a recipe with an error. So every `Recipe` is complete.
5. The steps are a `Steps` value with an English and a Chinese tuple and the fallback of `BiText` (2.2), so F09 shows them as it shows a name.
6. `datafile` lists a folder and turns the `OSError` of a missing or unreadable folder into a `Problem`, because architecture 6 gives it every `OSError` (3.1). A missing `recipes/` folder is an error, because `init` creates it. `datafile` also reports a name whose `.toml` ending has a capital letter, such as `rice.TOML`, because Windows opens that file for `rice.toml` and Linux does not.
7. The helpers for the shape of a file move from `catalog` into `datafile`, so that `settings` and `menus` can use them too (3.2).

These later features are meant to call them:

- F06 gets the IDs from `list_recipe_ids`, and reports a dish whose ID is not among them as an unknown recipe. It never builds a path from an ID that a menu file gives.
- F07 calls `read_recipes` with the catalog that `read_catalog` gave, or with `None` when the catalog could not be read, and prints the errors and the warnings apart. It can count the recipes with `list_recipe_ids`.
- F08 writes `recipes/tomato-egg.toml`, on which `read_recipe` gives no problem.
- F09's `list` calls `read_recipes`. Its `show ID` looks for the ID among those of `list_recipe_ids`, shows its "unknown ID" output when the ID is not there, and calls `read_recipe` when it is. It shows the steps with `Steps.get`, and adds its note on the other language when `Steps.exact` gives `None`.
- F10 matches each word against `Recipe.name`, the names of each `RecipeIngredient.ingredient`, and the names of `Recipe.tags`.
- F12 scales each `RecipeIngredient.quantity` by `Fraction(dish.servings, recipe.servings)`, and merges the lines by `RecipeIngredient.ingredient`.
- F14 picks recipes from `read_recipes` by their tags.
- F15 checks the ID that you type with `is_recipe_id`, and checks that `list_recipe_ids` does not list it yet.
- F16 checks the recipe that you edited with `read_recipe`.
- F05, F06, and F09 bound the servings of the settings, of a dish, and of `show --servings` to the range 1 to 100, as Troy decided (choice 2), so that every servings number stays in one range.

### 2.1 `RecipeIngredient`

- Module: recipes
- Purpose: One ingredient line of a recipe: the catalog's ingredient, its quantity, and its optional note in two languages ([architecture 5.2](../../architecture.md#52-values)). It refers to the same `Ingredient` object as the catalog, so the shopping list merges ingredients by identity.

Signature:

```python
@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    ingredient: Ingredient
    quantity: Quantity
    note: BiText | None = None
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `ingredient` | `Ingredient` | The ingredient, such as Tomato and 番茄. | An ingredient of the catalog that the recipe was read with. |
| `quantity` | `Quantity` | The amount with its unit, or to taste (F01 design 2.4). `read_recipe` gives an amount without a unit the default unit of the ingredient. | None |
| `note` | `BiText` or `None` | The note, such as "cut into wedges" and "切块". | `None` when the line has no note. Each language that is set holds more than whitespace. One language may be missing. |

- Return value: A `RecipeIngredient`. Two of them are equal when their three fields are equal, and a `RecipeIngredient` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | A language of `note` that is set is empty or holds only whitespace. |

- Side effects: None
- Performance target: None

Example:

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

- Module: recipes
- Purpose: The steps of a recipe, as a tuple of texts for each language, with at least one language ([architecture 5.2](../../architecture.md#52-values)). Like `BiText`, it gives the asked language, or the other language when the asked one is missing. So `show` shows the Chinese steps of a recipe that has no English steps, as in the F09 prototype "A missing language".

Signature:

```python
@dataclass(frozen=True, slots=True)
class Steps:
    en: tuple[str, ...] | None = None
    zh: tuple[str, ...] | None = None

    def get(self, lang: Lang) -> tuple[str, ...]: ...

    def exact(self, lang: Lang) -> tuple[str, ...] | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `en` | A tuple of `str`, or `None` | The English steps, in order. | `None` when the recipe has no English steps. Otherwise 1 or more steps, and each holds more than whitespace. |
| `zh` | A tuple of `str`, or `None` | The Chinese steps, in order. | As for `en`. `en` and `zh` are not both `None`. |
| `lang` | `Lang` | The language that `get` or `exact` gives. | None |

- Return value: A `Steps`.
  - `get(lang)` gives the steps in `lang`, or the steps in the other language when the ones in `lang` are `None`. It never gives `None`.
  - `exact(lang)` gives the steps in `lang`, or `None` when they are missing. F09 uses it to say that it shows the steps in the other language.
  - Two `Steps` values are equal when their `en` and their `zh` are equal, and a `Steps` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `en` and `zh` are both `None`. |
| `ValueError` | `en` or `zh` is the empty tuple, or holds a step that is empty or holds only whitespace. |
| `TypeError` | `en` or `zh` is neither a tuple nor `None`, such as a list, or holds a step that is not a `str`. |

- Side effects: None
- Performance target: None

Example:

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

- Module: recipes
- Purpose: One recipe with the parts of [requirements 3](../../requirements.md#3-how-users-interact-with-it): its ID, its names, its servings, its tags, its ingredients, and its steps ([architecture 5.2](../../architecture.md#52-values)). The ID is the file name without `.toml`, and IDs compare exactly as written. The tags and the ingredients are values of the catalog. Tests and F12 can build a recipe in code, with no file.

Signature:

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

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `id` | `str` | The ID, such as `tomato-egg`. | `is_recipe_id(id)` is true (2.4). |
| `name` | `BiText` | The names, such as "Tomato and egg stir-fry" and "番茄炒蛋". | Each language that is set holds more than whitespace. One language may be missing. |
| `servings` | `int` | The servings that the recipe makes. | From 1 to 100. Not a `bool`. |
| `tags` | A tuple of `Tag` values | The tags, in the file's order. | Tags of the catalog. `read_recipe` gives each tag once. May be empty. |
| `ingredients` | A tuple of `RecipeIngredient` values | The ingredient lines, in the file's order. | May be empty. |
| `steps` | `Steps` | The steps. | None |

- Return value: A `Recipe`. Two recipes are equal when their six fields are equal, and a `Recipe` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `is_recipe_id(id)` is false. |
| `TypeError` | `servings` is not an `int`, or it is a `bool`. |
| `ValueError` | `servings` is less than 1 or more than 100. |
| `ValueError` | A language of `name` that is set is empty or holds only whitespace. |

- Side effects: None
- Performance target: None

Example:

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

- Module: recipes
- Purpose: The rule for a recipe ID ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). A file in `recipes/` is a recipe only when its name without `.toml` follows the rule (2.5). `read_recipe` and `Recipe` check it before they build a path or a value, so `DataFolder.recipe_file` never gets a wrong name (F03 design 2.1). F09 and F15 can check an ID from the command line or from your answer with it.

Signature:

```python
def is_recipe_id(text: str) -> bool: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | A name to check, such as a file name without `.toml` or an ID that you typed. | Any string. |

- Return value: `True` when `text` follows all of these rules, and `False` otherwise. The rules are the same on Windows and Linux.
  1. It has at least one character.
  2. Its first character is a small letter from `a` to `z` or a digit from `0` to `9`.
  3. Each other character is a small letter from `a` to `z`, a digit from `0` to `9`, or `-`, which is U+002D HYPHEN-MINUS.
  4. It is not a Windows device name: `con`, `prn`, `aux`, `nul`, `com0` to `com9`, or `lpt0` to `lpt9`.

The rule rejects every name that `DataFolder.recipe_file` rejects, and more. The table gives the reasons.

| Rejected, for example | Why |
| --- | --- |
| `""` | An ID names a file. |
| `.`, `..`, `rice.`, and `nul.v2` | A dot is not allowed. `.` and `..` name folders. Windows treats a name that starts with a device name and a dot, such as `nul.v2.toml`, as the device. |
| `a/b`, `a\b`, `a:b`, and `a` followed by U+0000 | A separator, a drive, an NTFS stream, or the null character could give the path of another file. Linux allows the file `recipes/a:b.toml`. |
| `a*b`, `a?b`, and `a<b` | Windows does not allow these characters in a file name, nor the others in the list below. |
| `Tomato-Egg` | Windows compares file names without case, so `Tomato-Egg.toml` and `tomato-egg.toml` would be one file on Windows and two files on Linux. |
| `tomato egg` and `tomato_egg` | Only `-` joins words. Windows drops spaces at the end of a name, and an ID with a space needs quotation marks on the command line. |
| `-tomato` | On the command line, it would look like an option. |
| `番茄炒蛋`, `"tomato\u2010egg"`, `"\uff54omato-egg"`, and `"tomato-egg\u200b"` | Only ASCII is allowed. U+2010 HYPHEN, U+FF54 FULLWIDTH LATIN SMALL LETTER T, and U+200B ZERO WIDTH SPACE look like `tomato-egg` or like nothing, so two IDs could look the same. Windows also compares letters outside ASCII without case. |
| `con`, `nul`, `com1`, and `lpt9` | Windows keeps these names for devices, so `nul.toml` names no file there. |

The characters that Windows does not allow in a file name are `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`, and the control characters U+0000 to U+001F. Rules 2 and 3 reject all of them, and also every name that ends with a dot or a space.

Errors: None. `is_recipe_id` never raises.

- Side effects: None
- Performance target: None

Example:

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

- Module: recipes
- Purpose: Lists the recipe IDs from the file names in `recipes/`, without reading any file ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). F06 checks the dishes of a menu against them, F09's `show` looks for an ID among them, and `read_recipes` reads the file of each.

Signature:

```python
def list_recipe_ids(folder: DataFolder) -> tuple[tuple[str, ...], tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: A pair `(ids, problems)`.
  - A recipe file is an entry of `recipes/` whose name ends with `.toml`, in these small letters, as `list_toml_files` gives it (3.1). Its ID is its name without `.toml`. Every other entry, such as `notes.txt` or `rice.toml.bak`, is not a recipe file and gives no problem. An entry such as `rice.TOML`, whose `.toml` ending has a capital letter, is not a recipe file either, and `list_toml_files` gives an error for it.
  - `ids` holds the ID of each recipe file whose name without `.toml` follows the rule of 2.4, sorted by code point, as `sorted` sorts strings. With that rule, `-` sorts before the digits and the digits before the letters. So the example data gives `choy-sum` first, and `tomato-egg` before `tomato-egg-noodles`, in the order of `list` in the F09 prototype.
  - `problems` holds the problems that `list_toml_files` gives, and then one error for each recipe file whose name without `.toml` breaks the rule of 2.4, in the order of the names: `RESERVED_RECIPE_ID` for a Windows device name of rule 4, and `NOT_A_RECIPE_ID` for every other name. Each problem's file is its entry, such as `recipes\pancakes.TOML` or `recipes\Rice Bowl.toml` on Windows, and it has no place. A name with a problem is not in `ids`, so no reader reads its file.
  - When `recipes/` is missing, is a file, or cannot be read, `list_toml_files` gives no names and one problem, with the file `recipes` and no place. So `ids` is empty, and `problems` holds only that problem.

The messages of `list_recipe_ids` are these:

| Name | English | Chinese |
| --- | --- | --- |
| `NOT_A_RECIPE_ID` | `This file name is not a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Rename the file.` | `这个文件名不是菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。请给文件改名。` |
| `RESERVED_RECIPE_ID` | `This file name cannot be a recipe ID, because Windows keeps it for a device. Rename the file.` | `这个文件名不能用作菜谱 ID，因为 Windows 把它留给设备使用。请给文件改名。` |

Neither message shows the name. The problem's file names it, on the line above the message in the layout of the F07 prototype. So a name with a control character, or with a character that no font shows, changes no message.

Errors: None. `list_recipe_ids` never raises for bad data.

- Side effects: Lists `recipes/` through `list_toml_files`. It reads no file and writes nothing. Windows may refuse to create a file such as `con.toml`, so a test of `RESERVED_RECIPE_ID` with a real file may run on Linux only.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` ([architecture 10](../../architecture.md#10-test-setup)).

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

- Module: recipes
- Purpose: Reads one recipe file into a `Recipe`, and reports each problem with its place ([requirements 4](../../requirements.md#4-features), F04). `show`, `menu show`, `shop`, and F16's check of one recipe call it, and `read_recipes` calls it for every ID. `check` shows every problem (F07). Every other command stops at the first error (architecture 6).

Signature:

```python
def read_recipe(
    folder: DataFolder,
    catalog: Catalog | None,
    recipe_id: str,
) -> tuple[Recipe | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `catalog` | `Catalog` or `None` | The catalog that the names of the ingredients and the tags come from. | `None` when the catalog could not be read. Then `read_recipe` checks only the form of the file. |
| `recipe_id` | `str` | The ID of the recipe, such as `tomato-egg`. | `is_recipe_id(recipe_id)` is true. An ID that `list_recipe_ids` gave, directly or through a week menu that F06 checked. `read_recipe` reads `folder.recipe_file(recipe_id)` and does not list the folder. On Windows, a file named `Tomato-Egg.toml` would also open for `tomato-egg`, so taking the ID from `list_recipe_ids`, which compares names exactly, keeps Windows and Linux alike. |

- Return value: A pair `(recipe, problems)`.
  - `recipe` is `None` when `catalog` is `None`, or when `problems` holds an error. Otherwise it is a `Recipe` with the ID `recipe_id`, even when `problems` holds warnings. Each text in it is stored without whitespace at both ends. It holds each tag once, in the order of the first item that names it, and each ingredient line in the file's order. A note with neither language is `None`, and a language that is missing is `None` in the name, a note, or the steps.
  - `problems` holds the problem of `read_toml` alone, when the file is missing, cannot be read, is not UTF-8, or is not valid TOML (F03 design 2.3). Otherwise it holds the problems of the checks below, in their order. Each problem has the file `recipes/<id>.toml`, such as `recipes\mapo-tofu.toml` on Windows. When `list_recipe_ids` gave the ID, only a file that was deleted or renamed since then gives `FILE_MISSING`.

The file has the layout of `docs/prototypes/example-data.md`:

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

`[steps]` comes last, because every key after it belongs to `steps`. `item` names an ingredient of the catalog in either language, and each item of `tags` names a tag in either language. `read_recipe` finds them with `Catalog.find_ingredient` and `Catalog.find_tag` (F03 design 2.6). `amount` is the quantity as F01's `parse_quantity` reads it, such as `300 g`, `1.5 kg`, `3`, or `适量` (F01 design 2.7).

Each table of the file has these keys, in this order:

| Table | Keys | Required |
| --- | --- | --- |
| The top of the file | `name`, `servings`, `tags`, `ingredients`, and `steps` | All five. `tags` and `ingredients` may be empty lists. |
| `name` | `zh` and `en` | At least one language. |
| An item of `ingredients` | `item`, `amount`, and `note` | `item` and `amount`. |
| `note` | `zh` and `en` | None. A note with neither language is no note. |
| `steps` | `zh` and `en`, each a list of texts | At least one language. |

The places of the problems are these. N counts the items of a list from 1, skipped items included, so it is the number that you count in the file.

| Place | English | Chinese |
| --- | --- | --- |
| `name` | `name` | `名称` |
| `servings` | `servings` | `份数` |
| The list `tags` | `tags` | `标签` |
| Item N of `tags` | `tag N` | `标签 N` |
| The list `ingredients` | `ingredients` | `食材` |
| Item N of `ingredients`, with its note | `ingredient N` | `食材 N` |
| `steps` | `steps` | `步骤` |
| Item N of `zh` in `steps` | `Chinese step N` | `中文步骤 N` |
| Item N of `en` in `steps` | `English step N` | `英文步骤 N` |

Each language of the name, of a note, and of the steps is in one of three states:

- Missing: its key is missing. In the name or a note, it is also missing when it holds a text that is empty or holds only whitespace. In the steps, it is also missing when it holds the empty list `[]`.
- Usable: in the name or a note, it holds a text with more than whitespace. In the steps, it holds a list that holds at least one text with more than whitespace.
- Wrong: it holds anything else, such as a number where a text belongs, or a text where a list of steps belongs, even a blank text such as `zh = ""`. So the steps hold only lists. Its check below gives an error.

The two languages of the name, of a note, and of the steps then follow these rules:

1. When one language is usable and the other is missing, the missing one gets a warning. So the language that a warning says commands show instead is always usable.
2. When both languages are missing, the name gets `NO_NAME` and the steps get `NO_STEPS`. A note with both languages missing is no note, and gets no problem.
3. Otherwise the languages get no further problem. A wrong language has its own error.

`read_recipe` makes these checks. A check whose part has a value of the wrong kind, such as a `name` that is not a table, is the only check of that part. Every other part is still checked, so one run reports every problem of the file.

| Part | Check | Problem | Place | Kind |
| --- | --- | --- | --- | --- |
| `name` | The key is missing. | `MISSING_KEY` | None | Error |
| `name` | The value is not a table. | `NOT_A_ZH_EN_TABLE` | `name` | Error |
| `name` | `zh` or `en` is wrong: it is there, but it is not a text. | `NOT_A_TEXT` | `name` | Error |
| `name` | The table has a key other than `zh` and `en`. | `UNKNOWN_KEY` | `name` | Error |
| `name` | Both languages are missing. | `NO_NAME` | `name` | Error |
| `name` | `zh` is missing, and `en` is usable. | `NO_ZH_NAME` | `name` | Warning |
| `name` | `en` is missing, and `zh` is usable. | `NO_EN_NAME` | `name` | Warning |
| `servings` | The key is missing. | `MISSING_KEY` | None | Error |
| `servings` | The value is not an integer, such as `"2"`, `2.5`, or `true`, or it is an integer of 16 or more digits, such as `0x` followed by 5,000 digits. | `SERVINGS_NOT_A_NUMBER` | `servings` | Error |
| `servings` | The value is an integer from -999,999,999,999,999 to 0. | `SERVINGS_TOO_FEW` | `servings` | Error |
| `servings` | The value is an integer from 101 to 999,999,999,999,999. | `SERVINGS_TOO_MANY` | `servings` | Error |
| `tags` | The key is missing. | `MISSING_KEY` | None | Error |
| `tags` | The value is not a list. | `NOT_A_LIST` | `tags` | Error |
| An item of `tags` | The item is not a text. | `ITEM_NOT_A_TEXT` | `tag N` | Error |
| An item of `tags` | The item is empty or holds only whitespace. | `EMPTY_ITEM` | `tag N` | Error |
| An item of `tags` | `catalog` is not `None`, and `find_tag` finds no tag for the item. | `UNKNOWN_TAG` | `tags` | Error |
| An item of `tags` | It names a tag that an earlier item named, such as `快手` after `quick`. | None. The recipe holds the tag once. | None | None |
| `ingredients` | The key is missing. | `MISSING_KEY` | None | Error |
| `ingredients` | The value is not a list. | `NOT_A_LIST` | `ingredients` | Error |
| An ingredient | The item is not a table. | `NOT_A_TABLE` | `ingredient N` | Error |
| An ingredient | `item` is missing, is not a text, or is empty or holds only whitespace. | `MISSING_KEY`, `NOT_A_TEXT`, or `EMPTY_TEXT` | `ingredient N` | Error |
| An ingredient | `catalog` is not `None`, and `find_ingredient` finds no ingredient for `item`. | `UNKNOWN_INGREDIENT` | `ingredient N` | Error |
| An ingredient | `amount` is missing, is not a text, or is empty or holds only whitespace. | `MISSING_KEY`, `NOT_A_TEXT`, or `EMPTY_TEXT` | `ingredient N` | Error |
| An ingredient | `parse_quantity` cannot read `amount`. | The message for its reason, by the table below | `ingredient N` | Error |
| An ingredient | `note` is there, but it is not a table. | `NOT_A_ZH_EN_TABLE` | `ingredient N` | Error |
| An ingredient | `zh` or `en` of `note` is wrong: it is there, but it is not a text. | `NOT_A_TEXT` | `ingredient N` | Error |
| An ingredient | `note` has a key other than `zh` and `en`. | `UNKNOWN_KEY` | `ingredient N` | Error |
| An ingredient | One language of `note` is missing, and the other is usable. | `NO_ZH_NOTE` or `NO_EN_NOTE` | `ingredient N` | Warning |
| An ingredient | The item has a key other than `item`, `amount`, and `note`. | `UNKNOWN_KEY` | `ingredient N` | Error |
| `steps` | The key is missing. | `MISSING_KEY` | None | Error |
| `steps` | The value is not a table. | `NOT_A_STEPS_TABLE` | `steps` | Error |
| `steps` | `zh` or `en` is wrong: it is there, but it is not a list, such as `zh = ""`. | `NOT_A_LIST` | `steps` | Error |
| A step | The item is not a text. | `ITEM_NOT_A_TEXT` | `Chinese step N` or `English step N` | Error |
| A step | The item is empty or holds only whitespace. | `EMPTY_ITEM` | `Chinese step N` or `English step N` | Error |
| `steps` | The table has a key other than `zh` and `en`. | `UNKNOWN_KEY` | `steps` | Error |
| `steps` | Both languages are missing. | `NO_STEPS` | `steps` | Error |
| `steps` | One language is missing, and the other is usable. | `NO_ZH_STEPS` or `NO_EN_STEPS` | `steps` | Warning |
| The top of the file | A key other than the five of the table of keys. | `UNKNOWN_KEY` | None | Error |

When `catalog` is `None`, `read_recipe` makes every check except `UNKNOWN_TAG`, `UNKNOWN_INGREDIENT`, and `AMOUNT_NO_UNIT`. The place of `UNKNOWN_TAG` is the list `tags`, as the F07 prototype shows, because the message names the tag. The other problems of an item of `tags` are at `tag N`.

The problems come in this order:

1. The parts come in the order `name`, `servings`, `tags`, `ingredients`, `steps`, and then the other keys at the top of the file, in the file's order.
2. Within a part, the problems come in the order of the rows above. A list's own problem comes first, and then the problems of each item, in order.
3. An ingredient's problems come key by key: `item`, then `amount`, then `note`, and then its unknown keys in the file's order.
4. A name, a note, or the steps give the problems of `zh`, then those of `en`, then their unknown keys in the file's order, and then `NO_NAME`, `NO_STEPS`, or the warning for the missing language.

`read_recipe` reads `amount` with `parse_quantity(amount, unit)`, where `unit` is the default unit of the ingredient that `item` names (F03 design 2.4). So `3` for 鸡蛋, whose default unit is 个, gives 3 pieces. When `item` has a problem, or `catalog` is `None`, it reads `amount` with no default unit, and reports every reason except `NO_UNIT`, because only the ingredient's default unit decides whether the amount needs a unit. A reason gives the message in this table:

| Reason of `WrongQuantity` (F01 design 2.5) | Message | An amount that gives it |
| --- | --- | --- |
| `NOT_A_NUMBER` | `AMOUNT_NOT_A_NUMBER` | `a few`, `1/2 tsp`, `-1 g`, or `1234567890123456 g`, whose number has 16 digits. |
| `UNKNOWN_UNIT` | `AMOUNT_UNKNOWN_UNIT` | `1 cups`. |
| `NO_UNIT` | `AMOUNT_NO_UNIT`, only when `item` names an ingredient of the catalog | `3` for 番茄, which has no default unit. |
| `ZERO` | `AMOUNT_ZERO` | `0 g`. |
| `EMPTY` | None. `EMPTY_TEXT` reports a blank `amount` first. | None |

`read_recipe` uses the messages of `datafile` for the shape of a file (F03 design 2.10): `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TABLE`, `NOT_A_TEXT`, `EMPTY_TEXT`, `ITEM_NOT_A_TEXT`, `EMPTY_ITEM`, and `UNKNOWN_KEY`. It picks the form of `UNKNOWN_KEY` by the number of keys of the table: five at the top of the file, three in an ingredient, and two in `name`, `note`, and `steps`. These are the messages of `recipes`. A placeholder is a name in braces, such as `{amount}`. The braces of `{ ... }` are part of the text, so the templates of `NOT_A_ZH_EN_TABLE` write each brace twice (F02 design 2.2).

| Name | English | Chinese |
| --- | --- | --- |
| `NAME`, `SERVINGS`, `TAGS`, `TAG_N`, `INGREDIENTS`, `INGREDIENT_N`, `STEPS`, `ZH_STEP_N`, and `EN_STEP_N` | The places in the table of places, with `{number}` for N. | The places in the table of places, with `{number}` for N. |
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

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `key` | The key as the file writes it. `name` or `note` in `NOT_A_ZH_EN_TABLE`. `zh`, `en`, `item`, `amount`, `tags`, `ingredients`, or a key of the top of the file in the messages of `datafile`. The unknown key in `UNKNOWN_KEY`. |
| `keys` | `and_list` of the keys of the table, in the order of the table of keys, such as "item, amount, and note" and "item、amount 和 note". |
| `servings` | The servings from the file, as an `int`. Only a number from -999,999,999,999,999 to 999,999,999,999,999 gets here, so the text has at most 15 digits. |
| `tag` | The item of `tags` without whitespace at both ends. |
| `name` | `item` without whitespace at both ends. |
| `amount` | The `text` of the `WrongQuantity`: `amount` without whitespace at both ends. |
| `unit` | The `unit` of the `WrongQuantity`, such as `cups`. |
| `ingredient` | The name of the ingredient, as its `BiText`, so each language shows its own name. |
| `number` | N, the number of the item. |

The F07 prototype and scenarios v0.1-S04 and v0.1-S07 show five of these problems. `recipes\mapo-tofu.toml, ingredient 3` gets `Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.`, and `recipes\red-braised-pork.toml, steps` gets `No English steps. Commands show the Chinese steps instead.`. `recipes\rice.toml` gets `Servings must be a whole number of 1 or more, not 0.` at `servings`, `Unknown unit "cups" in "1 cups".` at `ingredient 1`, and `Unknown tag "breakfast". Add it to the catalog's tags.` at `tags`.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `is_recipe_id(recipe_id)` is false. `read_recipe` checks this before it reads, so `DataFolder.recipe_file` never gets a wrong name. |

- Side effects: Reads `recipes/<id>.toml` through `read_toml`. It lists no folder and writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10). The second file has the mistakes of scenario v0.1-S07 in `rice.toml`. The third file has a missing English name, a hexadecimal servings number of 5,000 digits, an amount without a unit for an ingredient that has no default unit, an amount of 16 digits, and a note and steps in English only. The last change adds `en = ""` to the steps of `red-braised-pork.toml`, which turns its warning into an error, because the steps hold only lists.

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

- Module: recipes
- Purpose: Reads every recipe file in `recipes/`, and reports every problem of the folder and of the files ([requirements 4](../../requirements.md#4-features), F04). `list`, `search`, and `check` call it, and so does F14's `menu suggest` (architecture 8).

Signature:

```python
def read_recipes(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[tuple[Recipe, ...], tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `catalog` | `Catalog` or `None` | The catalog, as for `read_recipe` (2.6). | `None` when the catalog could not be read. |

- Return value: A pair `(recipes, problems)`.
  - `read_recipes` calls `list_recipe_ids` once, and then `read_recipe` once for each ID, in the order of the IDs.
  - `recipes` holds each recipe that `read_recipe` gives, in the order of the IDs. A file with an error gives no recipe. `recipes` is empty when `catalog` is `None`.
  - `problems` holds the problems of `list_recipe_ids`, and then the problems that `read_recipe` gives for each ID, in the order of the IDs.

Errors: None. `read_recipes` never raises for bad data.

- Side effects: Lists `recipes/` once through `list_toml_files`, and reads each recipe file once through `read_toml`. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10). The second run adds a file whose name is not an ID, and makes `rice.toml` hold only `servings = 0`, which gives five errors.

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

## 3. Changes to existing interfaces

None. No interface that F01 to F03 implemented changes. Each exported name keeps its signature and its behavior, and F03's tests pass unchanged. F04 adds names to the interface of `datafile`, as F02 added `BiText` to F01's `lang`, and it changes internal files of `catalog`.

1. `datafile` exports `list_toml_files` (3.1). Architecture 6 gives every `OSError` of a data file to `datafile`, and architecture 8 lets only `datafile` open data files, so `recipes` lists `recipes/` through it. F06 can list `menus/` with it.
2. `datafile` exports `Report`, `read_list`, `read_table`, `read_text`, and `report_unknown_keys` (3.2). They move from `src/recipe_menu/catalog/_shape.py`, where they are internal to `catalog`. `recipes` may import `catalog`, but `settings` and `menus` may not (architecture 3), so helpers kept in `catalog` would be copied into F05 and F06. `Report` gains the method `warn`. `read_catalog` and `read_pantry` import the helpers from `recipe_menu.datafile`, and `catalog/_shape.py` is deleted. The interface of `catalog` does not change, and `read_catalog` and `read_pantry` give the same problems in the same order.
3. F04 uses F01's `Quantity`, `TO_TASTE`, `Unit`, `WrongQuantity`, `WrongQuantityReason`, and `parse_quantity`, F02's `BiText`, `Lang`, `Message`, `MessageValue`, `Plural`, and `and_list`, and F03's `DataFolder`, `Problem`, `Severity`, `read_toml`, the messages of F03 design 2.10, `Catalog`, `Ingredient`, and `Tag`, as their designs give them, and changes none of them.

### 3.1 `list_toml_files`

- Module: datafile
- Purpose: Lists the TOML files of one folder of the data folder. It turns an `OSError` into a `Problem` ([architecture 6](../../architecture.md#6-error-handling)), and reports a name whose `.toml` ending has a capital letter. `list_recipe_ids` lists `recipes/` with it (2.5), and F06 can list `menus/`. It reads no file, so a command can learn the names without parsing the files (architecture 8).

Signature:

```python
def list_toml_files(
    folder: DataFolder,
    path: Path,
) -> tuple[tuple[str, ...], tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `path` | `Path` | The folder to list, such as `folder.recipes`. | Inside `folder.root`. |

- Return value: A pair `(names, problems)`.
  - `names` holds the name of each entry of `path` whose name ends with `.toml`, in these small letters, without that ending, sorted by code point. Every kind of entry counts, a folder named `x.toml` too, so `list_toml_files` need not look at each entry, and `read_toml` later reports such a folder as `FILE_IS_FOLDER`. A folder with no such entry gives the empty tuple.
  - `problems` holds the error `TOML_ENDING_NOT_SMALL` for each entry whose `.toml` ending has a capital letter, such as `rice.TOML` or `rice.Toml`, sorted by code point. Such a name ends with `.` followed by `t` or `T`, `o` or `O`, `m` or `M`, and `l` or `L`, and does not end with `.toml`. The problem's file is the entry, relative to the data folder, such as `Path("menus", "2026-W48.TOML")`, and it has no place. Windows opens `rice.TOML` when a reader asks for `rice.toml`, and Linux does not, so the name is not in `names`, and the error asks you to rename the file.
  - When listing `path` fails with an `OSError`, `names` is empty, and `problems` holds only one problem. It has `Severity.ERROR`, the file `folder.relative(path)`, and no place. Its message comes from the first row of this table that applies:

| Condition | Message |
| --- | --- |
| `path.is_file()` is true. The probe never raises, and a probe that fails counts as false. | `FOLDER_IS_FILE` |
| The error is a `FileNotFoundError`, or a `NotADirectoryError` because a folder above `path` is a file. | `FOLDER_MISSING` |
| The error is a `PermissionError`. | `FOLDER_ACCESS_DENIED` |
| Any other `OSError`. | `FOLDER_SYSTEM_ERROR`. Its value `reason` is the error's `strerror`, or the name of the error's class, such as `OSError`, when `strerror` is `None` or empty. |

These messages join the internal messages of `datafile`, beside `FILE_MISSING` and the others of F03 design 2.3:

| Name | English | Chinese |
| --- | --- | --- |
| `FOLDER_MISSING` | `The folder is missing.` | `文件夹不存在。` |
| `FOLDER_IS_FILE` | `The folder cannot be read: it is a file.` | `无法读取文件夹：它是一个文件。` |
| `FOLDER_ACCESS_DENIED` | `The folder cannot be read: access is denied.` | `无法读取文件夹：没有访问权限。` |
| `FOLDER_SYSTEM_ERROR` | `The folder cannot be read. The system says: {reason}` | `无法读取文件夹。系统提示：{reason}` |
| `TOML_ENDING_NOT_SMALL` | `The file name must end with ".toml" in small letters. Rename the file.` | `文件名必须以小写的“.toml”结尾。请给文件改名。` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `path` is not inside `folder.root`, as `DataFolder.relative` finds. `list_toml_files` checks this before it lists. |

- Side effects: Lists the folder at `path`. It reads no file and writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10).

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

### 3.2 `Report`, `read_list`, `read_table`, `read_text`, and `report_unknown_keys`

- Module: datafile
- Purpose: The helpers with which a reader checks the shape of its file and reports it with the messages of F03 design 2.10. A reader starts a `Report` for its file, passes it to each helper, adds its own problems with `add` and `warn`, and returns `tuple(report.problems)`. They move from `src/recipe_menu/catalog/_shape.py` as they are. Only `warn` is new, because F04 gives warnings and F03 gives none.

Signature:

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

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `file` | `Path` | The file of every problem of the report, relative to the data folder, such as `Path("recipes", "rice.toml")`. | As the `file` of a `Problem` (F03 design 2.2). |
| `place` | `BiText` or `None` | The place of the problem, of the list, of the item, or of the table. | `None` only where the signature allows it, for a problem of the whole file. |
| `message` and `values` | `Message`, and `MessageValue` keyword arguments | What is wrong, and the value of each placeholder. | As for `Problem.error` (F03 design 2.2). |
| `table` | A mapping of `str` to `object` | A table of the file, as `read_toml` gives it. | None |
| `key` | `str` | The key of the list or the text. | None |
| `item` | `object` | An item of a list, as the file gives it. | None |
| `known` | A sequence of `str` | The keys that the table may have, in the order that the reader's design gives. | None |
| `report` | `Report` | Where the problems go. | None |

- Return value:
  - `Report(file)` gives an empty report. `problems` lists the problems added so far, in order. `add` appends `Problem.error(file, place, message, **values)`, and `warn` appends `Problem.warning(file, place, message, **values)`.
  - `read_list` gives the list at `key`. When the key is missing, it adds `MISSING_KEY` with no place and gives `[]`. When the value is not a list, it adds `NOT_A_LIST` at `place` and gives `[]`.
  - `read_table` gives `item` when it is a table. Otherwise it adds `NOT_A_TABLE` at `place` and gives `None`.
  - `read_text` gives the text at `key` without whitespace at both ends. It adds `MISSING_KEY` when the key is missing, `NOT_A_TEXT` when the value is not a text, and `EMPTY_TEXT` when the text holds only whitespace, each at `place`, and then gives `None`.
  - `report_unknown_keys` gives nothing. For each key of `table` that is not in `known`, in the table's order, it adds `UNKNOWN_KEY` at `place`, in its form for `len(known)` keys, with the value `keys` set to `and_list(known)`.

`Report` is not a value of the data model. It is a collector that a reader creates and drops within one call. No reader returns one or keeps one in a value, and every reader returns its problems as a tuple. So every value that crosses modules is still frozen, as architecture 8 asks.

Errors:

| Error | When |
| --- | --- |
| The errors of `Problem.error` and `Problem.warning` (F03 design 2.2) | `add` or `warn` gets a message and values that do not fit, or a `file` that is absolute. The other helpers pass only messages and values that fit. |

- Side effects: `add`, `warn`, and the four functions append to `report.problems`. Nothing else changes.
- Performance target: None

Example:

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

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `recipes` is a domain module that imports only `lang`, `units`, `text`, `datafile`, and `catalog`, and it reaches the disk only through `datafile`, as architecture 3, 4, and 8 allow. `Recipe` and `RecipeIngredient` have the fields of architecture 5.2, and a `RecipeIngredient` holds the catalog's own `Ingredient` object, so F12 can merge by identity. Choice 5 fits 5.2: `Steps` holds "the steps as a tuple of strings for each language" in one value with the fallback of `BiText`. A design may add such a helper value, as F01 added `WrongQuantity` and F03 added `Severity`. Choice 7 fits architecture 3 and 6. Architecture 6 gives every `OSError` of a data file to `datafile`, and architecture 3 gives it the paths of the data folder's files and problems with their places, so `list_toml_files`, its five messages, and the shape helpers belong there. The check of the `.toml` ending in 3.1 belongs there too, because architecture 5.2 makes `DataFolder` the only place that knows the file names, and F06 can share the check for `menus/`. `Report` fits architecture 8 as designed. It is not a value of the data model. It is a collector that one reader call creates, passes to the helpers, and drops, and every reader returns `tuple(report.problems)`. Choice 4 fits architecture 6. The reader still checks the whole file and records every problem, and no command other than `check` uses a recipe with an error. Choice 6 fits architecture 6 and requirements 3: `init` creates `recipes/`, and a missing part of the data folder exits with 1. Finding 1, resolved. Choice 1 narrows requirements 3 and the F04 row, so Troy decided it, and Troy kept the rule in chat (option A). Choice 1 now lists what a file name needs, as architecture 1 and F03 design 2.1 give it, and gives the reasons for asking more, without the overstated reason of version 0.1. `TOML_ENDING_NOT_SMALL` follows from the same decision. It reports a file such as `rice.TOML`, which version 0.1 skipped with no problem. So every entry of `recipes/` that Windows can open as a recipe file now gives an ID or an error, and the error works like `NOT_A_RECIPE_ID`. Troy sees it when Troy approves this design (R18, with `troy_approves_first = 16`). Finding 2, resolved. Troy accepted the range 1 to 100 in chat, for a recipe, the settings, a dish, and `show --servings`. It needs no architecture change. The "(1 or more)" of 5.2 is the lower bound that every reader keeps, and 5.2 leaves exact constraints to the designs. The designs of F05, F06, and F09 follow choice 2. The 15-digit rule for a number in a message is still needed. `tomllib` reads a hexadecimal integer of 5,000 digits, and `Problem` would otherwise raise F02's 4,300-digit `ValueError` for bad data (F03 review). Finding 6, optional, not blocking. Choice 1 says "for four reasons" and then gives five, because the sentence about `-x` is a fifth. A later revision can say "five reasons". |
| Follows the error handling and naming conventions | Pass | Every reader returns its problems and never raises for bad data (architecture 6). The only exceptions come from wrong calls: an ID that breaks the rule in `read_recipe`, a path outside the data folder in `list_toml_files`, and wrong values in the constructors of 2.1 to 2.3. `list_toml_files` turns each `OSError` into a `Problem`, with its conditions in the order that `read_toml` uses, so its `except` clause names `OSError` at the place that makes the `Problem` (architecture 6 and 8). It now returns the pair `(names, problems)`, as `list_recipe_ids`, `read_recipe`, and `read_catalog` do, so no caller tests the type of the result. A folder error gives empty `names` and one problem. `TOML_ENDING_NOT_SMALL` is an error with the entry as its file, relative to the data folder, and no place. Its message does not show the name, because the file line above it does, as for `NOT_A_RECIPE_ID`. The rule of 3.1 catches every ending that Windows opens as `.toml`. Unicode maps no character outside ASCII to `t`, `o`, `m`, `l`, or their capitals by a one-to-one case mapping, and on Windows the Architect checked that `a.toml` opens the file `a.TOML`. Each problem names its file relative to the data folder and its place as a field, such as `ingredient 3`, or no place for the whole file (architecture 1 and 6). A missing language is a warning, which never changes the exit code. Finding 3, resolved. 2.6 now gives each language of the steps one state. Missing is a missing key or `[]`, and any text, even `zh = ""`, is Wrong and gets `NOT_A_LIST` at `steps`. Choice 3, the three states, the row of the table, and the new example agree. In the Architect's model, `zh = ""`, `zh = " "`, and `zh = 3` give `NOT_A_LIST` at `steps`, `zh = []` gives the warning `NO_ZH_STEPS`, and `zh = [" "]` gives `EMPTY_ITEM` at `Chinese step 1`. With `zh = ""` and `en = []`, `zh` is wrong, so rule 3 adds no `NO_STEPS`, and the file still has its error. A blank text in the name or a note stays a missing language. The F02 review leaves that choice to each reader, and it agrees with F03's `EMPTY_TEXT`. A message shows a number from the file only when the number has at most 15 digits, and `AMOUNT_NOT_A_NUMBER` names F01's limit, as the F01 review asked. The five problems that the F07 prototype and scenarios v0.1-S04 and v0.1-S07 show still follow from the rules, as 2.6 lists them. Names follow PEP 8, and the messages are UPPER_SNAKE constants in `recipes/messages.py` and `datafile/messages.py` (architecture 8). |
| Does not duplicate an existing interface | Pass | `recipes` is new. It reads amounts with F01's `parse_quantity`, finds names with F03's `find_ingredient` and `find_tag`, reads files with `read_toml`, and reports shape mistakes with the eight messages of F03 design 2.10, so it writes none of them again. `list_recipe_ids` passes on the problems of `list_toml_files` and does not check the `.toml` ending again. `TOML_ENDING_NOT_SMALL` stays internal to `datafile`, so F06 gets the same check for `menus/` with no copy. `is_recipe_id` rejects every name that `DataFolder.recipe_file` rejects, and more (2.4), and `recipe_file` keeps its own check as the last guard. `Steps` repeats the fallback of `BiText` for tuples of steps. `BiText` takes only texts (F02 design 2.1), and making it generic would change an implemented interface, so a second small value is the better choice. The move in 3.2 prevents a copy. Without it, `settings` and `menus`, which may not import `catalog`, would each copy the helpers. The places `tags`, `tag N`, `ingredients`, and `ingredient N` repeat texts that `catalog` keeps internal. Architecture 8 has each module keep its own messages, so the copies are acceptable. `UNKNOWN_INGREDIENT` and `AMOUNT_UNKNOWN_UNIT` differ from the catalog's `UNKNOWN_INGREDIENT` and `UNKNOWN_UNIT`, as the F07 prototype shows. |
| Depends only on features earlier in the order | Pass | F04 uses F01, F02, and F03, which come before it and pass their tests on main, and section 3 names each interface that it uses. The additions to `datafile` use only `lang` and `text`, which architecture 3 allows `datafile`. F04 depends on no later feature. The plans for later features in section 2 bind no later design, except Troy's decision on servings (choice 2), which F05, F06, and F09 follow. Those features come after F04, so they may rely on it, and each of their designs gets its own review. The interfaces need only the standard library, so R16 has no new dependency to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | Each assumption between modules is written in the design. `read_recipe` opens `recipes/<id>.toml` without listing the folder, so a caller passes an ID that `list_recipe_ids` gave, and section 2 says so for F06 and F09. F06 checks dish IDs against `list_recipe_ids` and never builds a path from a menu file. `Report` reaches `datafile` only as an argument within one call. `AMOUNT_NOT_A_NUMBER` names F01's 15-digit limit (F01 design 2.7), so a change to that limit changes this message too. `list_toml_files` sorts its names and its problems, so no caller depends on the order of the file system. Finding 4, resolved. `list_toml_files` reports a name such as `rice.TOML`, and `list_recipe_ids` passes the problem on before its own errors, so such a file no longer goes unnoticed on either system. Finding 7, not blocking. 3.1 sorts the problems of `TOML_ENDING_NOT_SMALL` "by code point", but it does not say which text it sorts. The two choices give different orders: `a-b.TOML` comes before `a.TOML` by the whole entry name, and after it by the name without its ending. The Architect recommends the whole entry name, which its model uses. The Interface Designer can name the text in a later revision, or the Test Manager settles it in PR 2. These notes go to later designs and do not block. F05, F06, and F09: use the range 1 to 100 for servings, as Troy decided. The F07 prototype gives a dish with 0 servings the text of `SERVINGS_TOO_FEW`, and the servings messages are internal to `recipes`, so F06 either asks `recipes` to export them or defines its own with the same text. F06: pass on the problems that `list_toml_files` gives for `menus/`, as `list_recipe_ids` does, and check each name against the week format exactly. On Windows, `menu_file("2026-W47")` opens `2026-w47.toml`, which `list_toml_files` lists as `2026-w47`. F07: `read_recipes` already returns the problems of `list_recipe_ids`, `TOML_ENDING_NOT_SMALL` included, so when F07 also counts the recipes with `list_recipe_ids`, it reports those problems once. With `recipes/` missing, `list_recipe_ids` gives one error and no IDs. F09: the F09 prototype "A missing language" shows four Chinese steps for `red-braised-pork`, and `tests/data/example/recipes/red-braised-pork.toml` has three different steps. v0.1-S12 step 3 expects the prototype's output, so the F09 design settles which one changes. F15 and F16: check an ID that you type with `is_recipe_id` and then against `list_recipe_ids`, before `read_recipe` or a new file. On Windows, `Tomato-Egg.toml` opens for `tomato-egg`, and a file named `rice.TOML` stops `datafile` from creating `rice.toml`. |
| Changes an implemented interface only through the change flow | Pass | `datafile` and `catalog` are implemented (F03). Section 3 now starts with "None", as F02's section 3 does, so finding 5 is resolved. F04 changes no exported name of F01 to F03. Each one keeps its signature and its behavior, and `recipe_menu.catalog` still exports the same seven names. F04 adds `list_toml_files`, `Report`, `read_list`, `read_table`, `read_text`, and `report_unknown_keys` to `recipe_menu.datafile`, and it changes only internal files of `catalog`: two imports, and `_shape.py` moves to `datafile`. An addition that leaves every existing contract as it was needs no requirement change (troy-mode requirements 5.4), as when F02 added `BiText` to F01's `lang`. Architecture 3 plans later features that add to `datafile`, and the helpers fit its responsibilities (first row). The Code Reviewer of PR #24 asked for this move for F04 to F06. `list_toml_files` is new in F04 and not yet implemented, so the change of its result from version 0.1 to 0.2 changes no implemented interface. All 213 tests of F01 to F03 pass against the Architect's model of version 0.2, so "F03's tests pass unchanged" holds. Notes for the next stages: the moved helpers keep their bodies in F04's mock PR, because F03's code calls them and the mock PR keeps the existing tests passing. A new test of a moved helper would then pass against the mock and break R09, so the test plan adds cases only for `Report.warn` and `list_toml_files` and leaves the moved helpers to F03's tests. The move changes three F03 files, so the main session plans the PRs for R03. On Windows, `Path` compares paths without case, so `Path("recipes", "pancakes.TOML") == Path("recipes", "pancakes.toml")` is true there. So the examples of 2.5 and 3.1 do not check the case of a problem's file on Windows, and a test that must check it compares `problem.file.name` or `str(problem.file)`. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the seven choices of section 2 against the requirements and the architecture. Choices 1 and 2 narrow what the requirements allow, so Troy decides them (findings 1 and 2). Each file has 19 code blocks, each block equals its mirror, and the 18 `python` blocks parse. The Architect built a model of sections 2 and 3 on the F01 to F03 code of main, and ran the 9 examples on fresh copies of `tests/data/example/`, in Python 3.13.18 and 3.14.3 on Windows. Every assertion and all 13 `# raises` hold. The expected values follow from the design's rules, from `docs/prototypes/example-data.md`, and from the recipe lines of the F07 prototype. The model read 3,000 random recipe files with and without a catalog, and it raised no exception. All 213 tests of F01 to F03 pass with the helpers moved. `ruff format --check` with ruff 0.17.4 reports both files formatted. Findings 3 to 5 do not block. | Approved. Troy decides findings 1 and 2 when Troy approves this design (R18). The Interface Designer decides findings 3 to 5. |
| 2 | No blocking issue. Version 0.2 records Troy's decisions on findings 1 and 2, and resolves findings 3, 4, and 5. `list_toml_files` now gives `(names, problems)` and the error `TOML_ENDING_NOT_SMALL`, and `list_recipe_ids` passes those problems on (3.1 and 2.5). The Architect updated its round 1 model to version 0.2, and ran the 9 examples on fresh copies of `tests/data/example/`, in Python 3.13.18 and 3.14.3 on Windows. Every assertion and all 13 `# raises` hold. The changed examples of 2.5, 2.6, and 3.1 fail against the round 1 model, so they test the changes. The 26 message rows of the design equal the model's messages. Each file still has 19 code blocks, each block equals its mirror, and the 18 `python` blocks parse. The headings, table rows, and list items of the two files match. The model read 3,000 random recipe files with and without a catalog and raised no exception, and all 213 tests of F01 to F03 pass against it. The Architect did not rerun `ruff format --check` or troy-check, which the project manager ran on version 0.2. Findings 6 and 7 do not block. | Approved. Troy approves this design (R18). The Interface Designer decides findings 6 and 7, or the Test Manager settles finding 7 in PR 2. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-11 | First draft. |
| 0.2 | 2026-11-11 | Answers round 1 of the Architect review and records Troy's decisions. Troy kept the rule for recipe IDs (choice 1), and the range 1 to 100 for the servings of a recipe, the settings, a dish, and `show --servings` (choice 2). Choice 1 gives the real reasons for the ID rule. A text in the steps, even `zh = ""`, is wrong and gets `NOT_A_LIST`, so the steps hold only lists (choice 3 and 2.6). Section 3 starts with "None". `list_toml_files` gives a pair of names and problems, and gives `TOML_ENDING_NOT_SMALL` for a name such as `rice.TOML`, which `list_recipe_ids` passes on (choice 6, 2.5, and 3.1). The examples of 2.5, 2.6, and 3.1 cover the new cases. |
| 1.0 | 2026-11-11 | Approved by Troy. |
