---
troy-doc: "F05-design"
lang: "en"
version: "1.0"
updated: "2026-11-12"
status: "Approved by Troy on 2026-11-12"
mirror: "design.zh-CN.md"
---

# F05 Command line and settings: interface design

## 1. Feature

- ID and name: F05 Command line and settings
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: F02

## 2. Interfaces

F05 builds three modules ([architecture 3](../../architecture.md#3-modules)). The domain module `settings` reads the settings file. The application module `app` holds the values that connect `cli` with the commands. The entry module `cli` runs the `recipe-menu` command: it parses the command line, shows the help and the version, finds the data folder, picks the language, runs a command, and exits with its code. The modules export these names, and each `__init__.py` lists them in `__all__`:

- `recipe_menu.settings`: `Meal`, `Settings`, and `read_settings` (2.1 to 2.3).
- `recipe_menu.app`: `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, `problem_lines`, and `stop_at_error` (2.4 to 2.8).
- `recipe_menu.cli`: `main` (2.9), which runs the command line of 2.10.
- `recipe_menu`: `__version__` (2.11), in `src/recipe_menu/__init__.py`, which architecture 3 gives to `cli`.

Each module keeps its messages in its `messages.py`, internal to the module (architecture 8). The other files are the Developer's choice, except three that later features rely on. The list of commands is `COMMANDS` in `src/recipe_menu/cli/_commands.py` (2.9). `src/recipe_menu/__main__.py` runs `main` for `python -m recipe_menu`. `src/recipe_menu/commands/__init__.py` holds only its doc comment, so importing one command module imports no other. F05 also adds `read_servings`, `MIN_SERVINGS`, and `MAX_SERVINGS` to `datafile`, and `recipes` reads its servings with them (section 3). The F05 prototype `docs/prototypes/F05-command-line.md` shows the help, the language, the data folder, and the mistakes.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F05 gives |
| --- | --- |
| It provides the `recipe-menu` command with its subcommands. | `main` (2.9) and the command line (2.10). Each command module describes its commands with `Command` (2.5) and adds them to `COMMANDS`. The console script `recipe-menu` and `python -m recipe_menu` call `main`. |
| It provides the options `--lang`, `--data`, `--help`, and `--version`. | The global options of 2.10, the help in both languages, and `__version__` (2.11). |
| It finds the data folder. | Rule 4 of 2.10: `--data`, then `RECIPE_MENU_DATA`, then `~/recipe-menu` ([requirements 3](../../requirements.md#3-how-users-interact-with-it), Q15). |
| It reads the settings: the language, the meals, and the default servings. | `read_settings` (2.3), which gives a `Settings` (2.2) with `Meal` values (2.1). |
| A command uses `--lang`, else the language in the settings, else English (requirements 3). | Step 3 of 2.10, with F02's `choose_lang`. `Context.lang` (2.4) carries the language to the command. |
| It ends every command with the exit codes of section 3: 0 when it worked, 1 for an error in the data or a missing file, and 2 for a wrong command line. | The exit codes of 2.10, `UsageError` (2.7) for exit code 2, and `stop_at_error` (2.8) for an error in a data file. |

These rules hold for every interface below:

- `settings` imports only `lang`, `text`, and `datafile` from the package. `app` imports only `lang`, `text`, `datafile`, and `settings`. `cli` imports `lang`, `text`, `datafile`, `settings`, `app`, and the command modules ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- Only `cli` touches the outside world: the arguments, the environment, the home folder, the current folder, today's date, and the console streams ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). `settings` reads its file only through `read_toml`. `app` writes only to the streams of the `Context` that it gets. No interface keeps state.
- `read_settings` never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). The exceptions in the Errors tables below come from wrong calls, which are bugs. `UsageError` is the one exception that crosses modules on purpose ([architecture 5.2](../../architecture.md#52-values)).
- Every value is a frozen dataclass with `slots=True` or an enum, and its collections are tuples (architecture 8). `UsageError` is an exception, so it is a class of its own (2.7).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F05 interface has a performance target. Every command that PT01 times pays for F05's start: Python's own start, the imports, one pass over the arguments, one look at the data folder, and one read of a settings file of a few lines ([requirements 7.1](../../requirements.md#71-performance-targets)). So `cli` imports at start only `settings`, `app`, and the command modules with what they import. It imports neither `argparse` nor `importlib.metadata` (choice 12). `main` calls single-purpose internal functions (R04).

The design makes these choices. The subsection in parentheses after each choice gives its rules.

1. **The settings file.** Every key is optional, with the defaults of architecture 5.2: no language, lunch and dinner, and 2 servings (2.3). The file itself is required, as every data file is. A missing `settings.toml` gives `read_toml`'s error `FILE_MISSING`, which stops a command with exit code 1, as requirements 3 says for a missing file. `init` writes the file (F08). An unknown key is an error, as in every other data file.
2. **The meals.** `meals` names the meals by their words in the files, `breakfast`, `lunch`, and `dinner`, which are also the keys of a menu file (architecture 8). `read_settings` keeps them in the order of a day and holds each once, whatever order the file lists them in, as `read_recipe` holds a tag once (2.3). An empty list is an error, because a menu needs at least one meal.
3. **Servings.** One rule holds for every servings number in a data file: an integer from 1 to 100, shown in a message only when it has at most 15 digits (F04 design, choice 2). It lives in `datafile` as `read_servings`, `MIN_SERVINGS`, and `MAX_SERVINGS` (3.1), because `recipes`, `settings`, and `menus` all read servings, and `settings` and `menus` may not import `recipes` (architecture 3). The three servings messages move from `recipes` with it and keep their texts. The other way, `settings` would copy the three messages and F06 would copy or import them, and the range would live in four places.
4. **A broken settings file.** `read_settings` gives no `Settings` when the file has an error, as `read_recipe` gives no recipe (2.3). So the language of a broken file does not count, and the command speaks the language of `--lang`, else English.
5. **The settings come before the mistakes on the command line.** `cli` reads the settings before it reports a usage error, so `recipe-menu cook` in a data folder with `language = "zh"` reports the mistake in Chinese (2.10). That costs one read of a small file.
6. **The data folder and the settings at start.** Each `Command` says with its `FolderUse` what `cli` checks before it runs the command (2.5). For most commands, a missing data folder or an error in the settings stops the command before it runs. `check` reports the settings' problems itself, so they do not stop it. `init` creates the folder, so neither stops it. So the commands that need the data folder share one check and one message. Architecture 6 says that the command checks a missing data folder, so its row changes (decision B).
7. **`Context.settings` is always a `Settings`** (2.4). A command with `FolderUse.READ` gets the settings of the file. `check` and `init` get `Settings()` when the folder or its settings could not be read. So no command needs a branch for missing settings that no test can reach. Architecture 5.2 lists "the settings when the folder has them", and the defaults stand in when it has none.
8. **A command that stops at an error** writes the problem and then `RUN_CHECK`, as architecture 6 and the F11 prototype "A menu with a mistake" show (2.8). The F05 prototype "A broken settings file" shows only the first two lines until the Product Manager adds the third (decision D). v0.1-S22 expects a message that "starts with" those two lines, so it holds with the third line too.
9. **A usage error names its hint.** A `UsageError` carries the line that follows its message, such as `RUN_HELP_FOR_OPTIONS`, or `None` (2.7). Most errors of the parser name one of F02's two `--help` lines. An error whose message already says what to write names `None`. Examples are `--tag needs a value.` for an option of a command, which the help does not list (2.10), and the F11 prototype's `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".`. Troy accepted this change to architecture 6 (decision A).
10. **The parser** follows ADR-0005 (2.10). Options can come anywhere on the line. `--help` and `--version` are flags, and every other option takes the next argument as its value. Forms such as `--lang=zh` and `-l zh`, and abbreviations, are not accepted. A command has at most one argument, which may be optional or repeat, because every command of the prototypes has at most one. An option with a value is a mistake when it comes twice, because the two values could differ, and an empty value counts as no value. A flag may repeat, because a second `--help` or `--version` changes nothing. Only the first `--lang` and the first `--data` that have a value pick the language and the data folder. So `recipe-menu list --lang --lang zh` reports the missing value in Chinese.
11. **The help** lists the commands in the order of `COMMANDS`, and then the four global options, as the prototype does (2.10). Its first column has the same width in both languages: the width of the widest command or option in either language. So the English and the Chinese help line up at the same column (F02 design 2.9). The help does not list the options of a command, such as `--tag`, because the prototype does not. So `UNKNOWN_OPTION` names the command's own options, and the other errors of a command's option name no hint (2.10).
12. **The version** is `recipe_menu.__version__`, and a test keeps it equal to the version in `pyproject.toml` (2.11). Reading the version of the installed package with `importlib.metadata` would import many modules at every start.
13. **The data folder** is the folder that the first `--data` with a value names, else the folder that `RECIPE_MENU_DATA` names when it is set and not empty, else `recipe-menu` in the home folder (2.10). `cli` replaces a leading `~` in either value with the home folder. Windows PowerShell 5.1 passes `~` unchanged to a native command, so without the replacement, `recipe-menu init --data ~\OneDrive\recipe-menu` would create a folder named `~` in the current folder. `cli` expands no other form, such as `~troy` or a variable. It makes a relative path absolute from the current folder, so every message names the folder by its full path (architecture 6).

Troy decided these four points on 2026-11-12 and accepted each recommendation. This PR changes neither `docs/architecture.md` nor a prototype. A later `[docs]` PR of the Architect carries out A to C, and a docs PR of the Product Manager carries out D.

- **A. The hint of a usage error.** Troy chose option 1. Architecture 6 says that an error with exit code 2 shows "The message, then a line that points to `recipe-menu --help`". The F11 prototype "A week without a menu" shows `"2026-W99" is not a week. ...` with no such line, and v0.1-S15 expects that output. So a `UsageError` names its hint, or `None` for a message that already says what to write, as 2.7 gives it. The F11 prototype and v0.1-S15 stay as they are. The reason: a line after a message that already says what to write repeats it, and the change touches one row of the architecture and no requirement. The Architect's `[docs]` PR changes that row of architecture 6 and the `UsageError` row of architecture 5.2.
- **B. Who checks a missing data folder.** Troy accepted the recommendation. `cli` checks a missing data folder for each command whose `FolderUse` asks for it (choice 6), with the message and the exit code that architecture 6 gives. The reason: `cli` already looks at the folder at start to read the settings (choice 5), so the commands that need the folder share one check and one message. Architecture 6's row "A missing data folder, menu, or recipe" says "Caught by: The command". The same `[docs]` PR changes it to say `cli` for the data folder and the command for a menu or a recipe.
- **C. The exceptions of a syntax mistake**, open since the F03 design review. Troy accepted the recommendation. Architecture 6's row "A syntax mistake, or a file that is not UTF-8" and ADR-0002 name `tomllib.TOMLDecodeError` and `UnicodeDecodeError`. `read_toml` also catches the plain `ValueError` and `RecursionError` that `tomllib` raises for such files (F03 design 2.3). The same `[docs]` PR names the two exceptions in both documents. The reason: the documents then name every exception that `read_toml` catches, and the change is wording only.
- **D. The F05 prototype "A broken settings file".** Troy accepted the recommendation. The prototype gets the third line `Run "recipe-menu check" to see every problem.`, so that it shows the whole message (choice 8). v0.1-S22 holds either way. The Product Manager makes the change in a docs PR.

These later features are meant to call F05's interfaces. Their own designs decide the details.

- Every command module of F07 to F16 exports one `Command` for each of its commands, such as `LIST_COMMAND` and `SHOW_COMMAND` from `browse`. Its mock PR adds each one to `COMMANDS`, at its place in the help's order: init, check, list, show, search, menu new, menu show, and shop (architecture 4). F14 to F16 choose the places of menu suggest, add, and edit.
- A command's `run` gets the `Context` and the `Arguments`. It writes its output to `context.out` and a message that ends it with exit code 1 to `context.err`, and it returns 0 or 1. For a wrong argument value, it raises a `UsageError` before it writes any output, and `cli` exits with 2. It stops at the first error in a data file with `first_error` and `stop_at_error`. It never prints, exits, or reads the environment (architecture 8).
- F06 reads the meals and the default servings from `Settings`. It names a meal in a place, such as "Monday dinner" and "周一晚餐", with `Meal.label`. It tests a meal key of a menu file with `key in Meal` and gets the meal with `Meal(key)`. It reads the servings of a dish with `read_servings`.
- F07's `check` has `FolderUse.CHECK`. It calls `read_settings` itself to report the settings' problems, and it writes each problem with `problem_lines`, indented as the F07 prototype shows. When the settings have an error, F07 decides how it reads the week menus, for example with `context.settings`, which then holds `Settings()`.
- F08's `init` has `FolderUse.CREATE`. It writes the language of `context.lang` into the settings. It can describe the settings that it writes with `Settings()`, `Meal.label`, and `and_list`, as in "English, lunch and dinner, 2 servings per dish".
- F09's `list` declares the option `--tag`, and its `show` declares the argument `ID` and the option `--servings`. `show` checks the value of `--servings` against `MIN_SERVINGS` and `MAX_SERVINGS`, and its `UsageError` shows the value as the text that you typed, never as an `int`, so no value meets F02's limit of 4,300 digits. In the F05 prototype "The language from the settings", the two tables of `list --tag 素` keep the column widths of the whole list, which `format_table` gives only with `min_widths`. F09's design decides how it gets them.
- F10's `search` declares the argument `WORD` with `repeats=True`, so `cli` reports a search with no word.
- F11's `menu new` and `menu show` and F13's `shop` declare the optional argument `WEEK`, and they turn `this` and `next` into weeks with `context.today`. F11 writes the meals at the top of its columns with `Meal.heading`. Under decision A, F11's error for a wrong week names no hint.
- In v0.2, F14 adds a random generator and F15 adds the input stream to `Context` and `main` (architecture 5.2). F14 and F16 add their keys to `Settings` and `read_settings` (architecture 5.1).

troy-mode's flow has one PR for each stage, on its own branch, such as `troy-mode/f05-3-mock`. So F05 has one mock PR and one implementation PR. Each changes more than R03's 5 files, so each PR description gives a soft-limit reason (R03): the tests reach `settings`, `app`, and `cli` through `main`, so each stage brings the three modules at once. F04's mock and implementation PRs gave reasons of the same kind.

- The mock (PR 3) holds `settings` with the addition to `datafile`, `app`, and `cli` with `__main__.py`, `commands/__init__.py`, and `__version__`. The mock defines every constant, such as the members of `Meal`, the defaults of `Settings`, and every message, so the modules import. `recipes` keeps its own check of the servings until the implementation. So F04's tests keep passing, and every new F05 test can fail against the mock (R09).
- The tests (PR 4) call `main` with their own commands through its parameter `commands`, because no real command exists before F07.
- The implementation (PR 5) holds `read_servings` with `recipes` reading through it, `settings`, `app`, the parser, the help, and `main` of `cli`, the entry files, and the console script.
- The implementation PR adds the console script `recipe-menu = "recipe_menu.cli:main"` to `[project.scripts]` in `pyproject.toml`, as architecture 2 names it, so the installed command runs working code from its first commit. `pyproject.toml` is a dependency file, so troy-check warns under R16 in that PR. The script adds no third-party dependency. So the Architect approves the warning after checking that `pyproject.toml` gains only `[project.scripts]` with `recipe-menu = "recipe_menu.cli:main"`. No test needs the script: the tests call `main`, and the timed tests and the version tests run `python -m recipe_menu`.

### 2.1 `Meal`

- Module: settings
- Purpose: The meals of a day, in the order of the day, with their names in both languages ([architecture 5.2](../../architecture.md#52-values), ADR-0004). Each member's value is the word that the settings and the menu files use.

Signature:

```python
class Meal(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

    @property
    def label(self) -> BiText: ...

    @property
    def heading(self) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `value` | `str` | The word of a file, for `Meal(value)`. | `breakfast`, `lunch`, or `dinner`, exactly as written here. |

- Return value: A `Meal`.
  - `list(Meal)` gives the members in the order of a day: `BREAKFAST`, `LUNCH`, and `DINNER`.
  - `label` gives the meal's name inside a sentence or a place, and `heading` gives its name at the top of a column. The table lists them.
  - `Meal(value)` gives the member whose value is `value`. `value in Meal` tells whether a word is a meal, without an exception (Python 3.12 and later).
  - A `Meal` is a `str`, so `sorted` sorts meals by their words, which is not the order of a day. Sort them with `key=list(Meal).index`.
  - F02's `Message.render` rejects an enum member as a value (F02 design 2.3), so a message shows a meal through `label` or `heading`.

| Member | Value | `label`, English | `label`, Chinese | `heading`, English | `heading`, Chinese |
| --- | --- | --- | --- | --- | --- |
| `BREAKFAST` | `breakfast` | `breakfast` | `早餐` | `Breakfast` | `早餐` |
| `LUNCH` | `lunch` | `lunch` | `午餐` | `Lunch` | `午餐` |
| `DINNER` | `dinner` | `dinner` | `晚餐` | `Dinner` | `晚餐` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `Meal(value)` gets a word that is not a member's value, such as `supper` or `Lunch`. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import BiText
from recipe_menu.settings import Meal
from recipe_menu.text import and_list

assert list(Meal) == [Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER]
assert Meal("lunch") is Meal.LUNCH
assert "dinner" in Meal
assert "supper" not in Meal
assert Meal.DINNER.label == BiText("dinner", "晚餐")
assert Meal.DINNER.heading == BiText("Dinner", "晚餐")
meals = and_list(meal.label for meal in (Meal.LUNCH, Meal.DINNER))
assert meals == BiText("lunch and dinner", "午餐和晚餐")
assert sorted(Meal) == [Meal.BREAKFAST, Meal.DINNER, Meal.LUNCH]
day_order = sorted([Meal.DINNER, Meal.BREAKFAST], key=list(Meal).index)
assert day_order == [Meal.BREAKFAST, Meal.DINNER]

Meal("supper")  # raises ValueError
Meal("Lunch")  # raises ValueError
```

### 2.2 `Settings`

- Module: settings
- Purpose: The settings of a data folder: the language, the meals of each day, and the servings of a dish that gives none ([architecture 5.2](../../architecture.md#52-values)). `Settings()` gives the defaults. In v0.2, F14 and F16 add fields.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `language` | `Lang` or `None` | The language of the commands when the command line has no `--lang`. | `None` when the settings name no language. Then the commands speak English. |
| `meals` | A tuple of `Meal` values | The meals of each day of a week menu. | 1 to 3 meals, in the order of `Meal`, each once. |
| `servings` | `int` | The servings of a dish that gives none ([requirements 3](../../requirements.md#3-how-users-interact-with-it), Q17). | From `MIN_SERVINGS` to `MAX_SERVINGS`, which are 1 and 100 (3.1). Not a `bool`. |

- Return value: A `Settings`. Two settings are equal when their three fields are equal, and a `Settings` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `language` is neither a `Lang` nor `None`, such as the text `"zh"`. |
| `TypeError` | `meals` is not a tuple, or it holds an item that is not a `Meal`. |
| `ValueError` | `meals` is empty, holds a meal twice, or is not in the order of `Meal`. |
| `TypeError` | `servings` is not an `int`, or it is a `bool`. |
| `ValueError` | `servings` is less than 1 or more than 100. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.language is None
assert defaults.meals == (Meal.LUNCH, Meal.DINNER)
assert defaults.servings == 2
every_meal = Settings(Lang.ZH, tuple(Meal), 3)
assert every_meal.meals == (Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER)
assert Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2) == Settings(Lang.EN)

Settings(meals=())  # raises ValueError
Settings(meals=(Meal.DINNER, Meal.LUNCH))  # raises ValueError
Settings(meals=(Meal.LUNCH, Meal.LUNCH))  # raises ValueError
Settings(servings=0)  # raises ValueError
Settings(servings=101)  # raises ValueError
Settings(servings=True)  # raises TypeError
Settings(language="zh")  # raises TypeError
Settings(meals=[Meal.LUNCH])  # raises TypeError
```

### 2.3 `read_settings`

- Module: settings
- Purpose: Reads `settings.toml` into a `Settings`, and reports each problem with its place ([requirements 4](../../requirements.md#4-features), F05). `cli` calls it at start (2.10), and `check` calls it to report the settings' problems (F07).

Signature:

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: A pair `(settings, problems)`.
  - `settings` is `None` when `problems` holds an error. Otherwise it is a `Settings`, and each key that the file lacks has its default.
  - `problems` holds the problem of `read_toml` alone, when the file is missing, cannot be read, is not UTF-8, or is not valid TOML (F03 design 2.3). Otherwise it holds the problems of the checks below, in their order. Each problem has the file `settings.toml`.

The file has the layout of `docs/prototypes/example-data.md`:

```toml
# recipe-menu settings
language = "en"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
```

Each key is optional:

| Key | Value | Default when the key is missing |
| --- | --- | --- |
| `language` | `"en"` or `"zh"`. | No language, so a command speaks English unless the command line has `--lang`. |
| `meals` | A list of `"breakfast"`, `"lunch"`, and `"dinner"`, in any order. | Lunch and dinner. |
| `servings` | An integer from 1 to 100. | 2. |

The places of the problems are these. N counts the items of `meals` from 1, skipped items included.

| Place | English | Chinese |
| --- | --- | --- |
| `language` | `language` | `语言` |
| `meals` | `meals` | `餐次` |
| Item N of `meals` | `meal N` | `餐次 N` |
| `servings` | `servings` | `份数` |

`read_settings` makes these checks. A missing key gives no problem, and no check gives a warning.

| Part | Check | Problem | Place | Kind |
| --- | --- | --- | --- | --- |
| `language` | The value is not a text. | `NOT_A_TEXT` | `language` | Error |
| `language` | The text is empty or holds only whitespace. | `EMPTY_TEXT` | `language` | Error |
| `language` | Without whitespace at both ends, the text is neither `en` nor `zh`, such as `fr` or `EN`. | `LANGUAGE_NOT_EN_OR_ZH` | `language` | Error |
| `meals` | The value is not a list. | `NOT_A_LIST` | `meals` | Error |
| An item of `meals` | The item is not a text. | `ITEM_NOT_A_TEXT` | `meal N` | Error |
| An item of `meals` | The item is empty or holds only whitespace. | `EMPTY_ITEM` | `meal N` | Error |
| An item of `meals` | Without whitespace at both ends, the item is not the value of a `Meal`, such as `supper` or `Lunch`. | `UNKNOWN_MEAL` | `meals` | Error |
| An item of `meals` | It names a meal that an earlier item named. | None. The settings hold the meal once. | None | None |
| `meals` | The value is the empty list `[]`. | `NO_MEALS` | `meals` | Error |
| `servings` | The value breaks the rule of `read_servings` (3.1). | `SERVINGS_NOT_A_NUMBER`, `SERVINGS_TOO_FEW`, or `SERVINGS_TOO_MANY` | `servings` | Error |
| The top of the file | A key other than `language`, `meals`, and `servings`. | `UNKNOWN_KEY` | None | Error |

The problems come in this order: those of `language`, then those of `meals`, then those of `servings`, and then the unknown keys in the file's order. Within `meals`, the list's own problem comes first, then the problems of each item in order, and then `NO_MEALS`. The place of `UNKNOWN_MEAL` is `meals`, as the F05 prototype shows, because the message names the meal. The settings hold the meals in the order of `Meal`, whatever order the file lists them in.

`read_settings` uses the messages of `datafile` for the shape of a file (F03 design 2.10). `UNKNOWN_KEY` has its form for three keys. These are the messages of `settings`, together with the names of the meals of 2.1:

| Name | English | Chinese |
| --- | --- | --- |
| `LANGUAGE`, `MEALS`, `MEAL_N`, and `SERVINGS` | The places in the table of places, with `{number}` for N. | The places in the table of places, with `{number}` for N. |
| `LANGUAGE_NOT_EN_OR_ZH` | `The language must be "en" or "zh", not "{language}".` | `语言必须是“en”或“zh”，不能是“{language}”。` |
| `UNKNOWN_MEAL` | `Unknown meal "{meal}". The meals are {meals}.` | `未知餐次“{meal}”。可用的餐次：{meals}。` |
| `NO_MEALS` | `"meals" must name at least one meal. The meals are {meals}.` | `“meals”至少要写上一个餐次。可用的餐次：{meals}。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `key` | `language` in `NOT_A_TEXT` and `EMPTY_TEXT`, `meals` in `NOT_A_LIST`, and the unknown key in `UNKNOWN_KEY`. |
| `keys` | `and_list(["language", "meals", "servings"])`: "language, meals, and servings" and "language、meals 和 servings". |
| `language` | The text of `language` without whitespace at both ends. |
| `meal` | The item without whitespace at both ends. |
| `meals` | `and_list` of the values of `Meal`, in their order: "breakfast, lunch, and dinner" and "breakfast、lunch 和 dinner". The Chinese text lists the English words too, because the file needs them. |
| `servings` | The value of `servings`, as `read_servings` gives it (3.1). |
| `number` | N, the number of the item. |

The F05 prototype "A broken settings file" and v0.1-S22 show `UNKNOWN_MEAL`. With `meals = ["lunch", "supper"]`, the problem is at `settings.toml, meals`, with the message `Unknown meal "supper". The meals are breakfast, lunch, and dinner.`.

Errors: None. `read_settings` never raises for bad data.

- Side effects: Reads `settings.toml` through `read_toml`. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` ([architecture 10](../../architecture.md#10-test-setup)).

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings, read_settings

settings, problems = read_settings(folder)
assert settings == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2)
assert problems == ()

folder.settings.write_text('meals = ["dinner", "breakfast", "dinner"]\n', encoding="utf-8")
assert read_settings(folder) == (Settings(None, (Meal.BREAKFAST, Meal.DINNER), 2), ())
folder.settings.write_text("", encoding="utf-8")
assert read_settings(folder) == (Settings(), ())

folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [BiText("meals", "餐次")]
english = problems[0].text(Lang.EN)
assert english == 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
chinese = problems[0].text(Lang.ZH)
assert chinese == "未知餐次“supper”。可用的餐次：breakfast、lunch 和 dinner。"

lines = ['language = "fr"', 'meals = ["lunch", 3]', "servings = 0x" + "f" * 5000, "editor = 1"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [
    BiText("language", "语言"),
    BiText("meal 2", "餐次 2"),
    BiText("servings", "份数"),
    None,
]
assert problems[0].text(Lang.EN) == 'The language must be "en" or "zh", not "fr".'
assert problems[1].text(Lang.EN) == "This item must be a text in quotation marks."
assert problems[2].text(Lang.EN) == "Servings must be a whole number from 1 to 100, such as 2."
assert problems[3].text(Lang.EN).startswith('Unknown key "editor". The keys are language,')

folder.settings.write_text("meals = []\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert problems[0].text(Lang.EN).startswith('"meals" must name at least one meal.')

folder.settings.unlink()
settings, problems = read_settings(folder)
assert settings is None
assert [problem.text(Lang.EN) for problem in problems] == ["The file is missing."]
```

### 2.4 `Context`

- Module: app
- Purpose: What a command gets from the outside world through `cli`: the language, the data folder, the settings, the output and error streams, and today's date ([architecture 5.2](../../architecture.md#52-values) and [8](../../architecture.md#8-naming-and-coding-rules)). `cli` builds it (2.10), and a test can build one with fixed values.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Context:
    lang: Lang
    folder: DataFolder
    settings: Settings
    out: TextIO
    err: TextIO
    today: date
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language that `cli` picked (2.10). | None |
| `folder` | `DataFolder` | The data folder. | Its `root` is absolute when `cli` builds it. The folder may be missing for a command with `FolderUse.CREATE`. |
| `settings` | `Settings` | The settings of the data folder. | For a command with `FolderUse.READ`, the settings that `read_settings` gave. For `FolderUse.CHECK` and `FolderUse.CREATE`, those settings, or `Settings()` when the folder is missing or the settings have an error (choice 7). |
| `out` | `TextIO` | Where the command writes its output. | Open. |
| `err` | `TextIO` | Where the command writes a message that ends it with exit code 1 (architecture 6). | Open. |
| `today` | `date` | Today's date on the PC, from which F11 and F13 find `this` and `next`. | None |

- Return value: A `Context`. Two contexts are equal when their six fields are equal, and the streams compare as objects. A `Context` is hashable.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert context.settings.servings == 2
assert context.today.isocalendar().week == 46
context.out.write("共 7 个菜谱。\n")
assert out.getvalue() == "共 7 个菜谱。\n"
```

### 2.5 `Command`, `Argument`, and `FolderUse`

- Module: app
- Purpose: The description of one command: its words, its help line, the function that runs it, its argument, its options, and what `cli` checks before it runs the command ([architecture 5.2](../../architecture.md#52-values), ADR-0005). Each command module defines its own, and `cli` reads the command line and writes the help from them (2.10).

Signature:

```python
class FolderUse(Enum):
    READ = "read"
    CHECK = "check"
    CREATE = "create"


@dataclass(frozen=True, slots=True)
class Argument:
    name: Message
    required: bool = True
    repeats: bool = False


@dataclass(frozen=True, slots=True)
class Command:
    words: tuple[str, ...]
    help_line: Message
    run: Callable[[Context, Arguments], int]
    argument: Argument | None = None
    options: tuple[str, ...] = ()
    folder: FolderUse = FolderUse.READ

    @property
    def usage(self) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | The command's words, such as `("list",)` or `("menu", "show")`. | 1 or 2 words. Each word has only the small letters `a` to `z`. |
| `help_line` | `Message` | The command's line in the help, such as "Show a week menu." and "查看一个周菜单。". | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` (2.6) and gives an `int` | Runs the command and gives its exit code. | Gives 0 or 1. Raises `UsageError` for a wrong argument value, before it writes any output. |
| `argument` | `Argument` or `None` | The command's argument, which follows its words. | `None` for a command with no argument. |
| `options` | A tuple of `str` | The options of the command, each with a value, such as `("--tag",)`. | Each is `--` followed by a small letter and then small letters and `-`. None is `--lang`, `--data`, `--help`, or `--version`. Each appears once. |
| `folder` | `FolderUse` | What `cli` checks before it runs the command, by the table below. | None |
| `name` | `Message` | The argument's name in the help, such as `ID`, `WORD` and `词`, or `WEEK` and `周`. | No placeholders. |
| `required` | `bool` | Whether the command line must give the argument. | None |
| `repeats` | `bool` | Whether the command line can give the argument more than once. | None |

What `cli` does before it runs a command depends on the command's `FolderUse`:

| Member | The data folder is missing | The settings have an error | `context.settings` | For |
| --- | --- | --- | --- | --- |
| `READ` | `cli` writes `NO_DATA_FOLDER` and `RUN_INIT` and exits with 1. | `cli` stops at the first error with `stop_at_error` and exits with 1. | The settings of the file. | `list`, `show`, `search`, `menu new`, `menu show`, and `shop` |
| `CHECK` | `cli` writes `NO_DATA_FOLDER` and `RUN_INIT` and exits with 1. | `cli` runs the command, which reports the problems. | The settings of the file, or `Settings()` after an error. | `check` |
| `CREATE` | `cli` runs the command. | `cli` runs the command. | The settings of the file, or `Settings()` when the folder is missing or the settings have an error. | `init` |

The argument's fields give how many values the command line may give it, and how the help writes it:

| `required` | `repeats` | Values | Form in the help | Example |
| --- | --- | --- | --- | --- |
| `True` | `False` | Exactly 1 | `NAME` | `show ID` |
| `False` | `False` | 0 or 1 | `[NAME]` | `menu new [WEEK]` |
| `True` | `True` | 1 or more | `NAME...` | `search WORD...` |
| `False` | `True` | 0 or more | `[NAME...]` | None in v0.1 |

- Return value: A `Command`, an `Argument`, or a `FolderUse` member.
  - `usage` gives the command's words, joined by a space, and then a space and the form of its argument in each language, such as `show ID`, `search WORD...` and `search 词...`, or `menu show [WEEK]` and `menu show [周]`. A command with no argument gives only its words. The help shows `usage`, and the usage errors of 2.10 quote it.
  - Two commands are equal when their six fields are equal, and two arguments when their three fields are equal. Both are hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `words` is empty, has more than 2 words, or has a word with a character other than `a` to `z`. |
| `ValueError` | `help_line` or the argument's `name` has a placeholder. |
| `ValueError` | An option breaks the rule of the parameters table, is a global option, or appears twice. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.app import Argument, Arguments, Command, Context, FolderUse
from recipe_menu.lang import BiText
from recipe_menu.text import Message


def run(context: Context, arguments: Arguments) -> int:
    context.out.write(" ".join(arguments.values) + "\n")
    return 0


WEEK = Argument(Message("WEEK", "周"), required=False)
WORD = Argument(Message("WORD", "词"), repeats=True)
MENU_SHOW = Command(
    ("menu", "show"),
    Message("Show a week menu.", "查看一个周菜单。"),
    run,
    WEEK,
)
SEARCH = Command(
    ("search",),
    Message("Find recipes by name, ingredient, or tag.", "按名称、食材或标签找菜谱。"),
    run,
    WORD,
)
INIT = Command(
    ("init",),
    Message("Create the data folder with example data.", "创建数据文件夹和示例数据。"),
    run,
    folder=FolderUse.CREATE,
)
assert MENU_SHOW.usage == BiText("menu show [WEEK]", "menu show [周]")
assert SEARCH.usage == BiText("search WORD...", "search 词...")
assert INIT.usage == BiText("init", "init")
assert MENU_SHOW.folder is FolderUse.READ

HELP = Message("Show one recipe.", "查看一个菜谱。")
Command(("Show",), HELP, run)  # raises ValueError
Command(("menu", "show", "all"), HELP, run)  # raises ValueError
Command(("show",), HELP, run, options=("--lang",))  # raises ValueError
Command(("show",), HELP, run, options=("-s",))  # raises ValueError
Command(("show",), Message("Show {id}.", "查看 {id}。"), run)  # raises ValueError
```

### 2.6 `Arguments`

- Module: app
- Purpose: What the command line gives a command: the values of its argument and the values of its options. `cli` builds it (2.10), and the command's `run` gets it.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Arguments:
    values: tuple[str, ...] = ()
    options: tuple[tuple[str, str], ...] = ()

    def option(self, name: str) -> str | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `values` | A tuple of `str` | The values of the argument, in the order of the command line, such as `("番茄", "quick")`. | As many as the argument allows (2.5). |
| `options` | A tuple of (name, value) pairs | The options of the command that the command line gives, such as `(("--tag", "素"),)`. The global options are not here. | Each name appears once. `Arguments` sorts the pairs by name, so their order does not matter. |
| `name` | `str` | The name of an option, for `option`. | None |

- Return value: An `Arguments`.
  - `option(name)` gives the value of the option `name`, or `None` when the command line does not give it.
  - When `cli` builds it, no value of an option is empty or starts with `--` (2.10).
  - Two `Arguments` values are equal when their two fields are equal, and an `Arguments` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | A name appears twice in `options`. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.app import Arguments

arguments = Arguments(("番茄", "quick"), (("--tag", "素"),))
assert arguments.values == ("番茄", "quick")
assert arguments.option("--tag") == "素"
assert arguments.option("--servings") is None
both = Arguments((), (("--tag", "素"), ("--servings", "4")))
assert both.options == (("--servings", "4"), ("--tag", "素"))
assert Arguments() == Arguments((), ())

Arguments((), (("--tag", "a"), ("--tag", "b")))  # raises ValueError
```

### 2.7 `UsageError`

- Module: app
- Purpose: A wrong command line or argument value, with its message, the message's values, and the line that follows the message ([architecture 5.2](../../architecture.md#52-values) and [6](../../architecture.md#6-error-handling)). The parser raises it, and so does a command for a wrong argument value. `cli` turns it into exit code 2.

Signature:

```python
class UsageError(Exception):
    message: Message
    hint: Message | None
    values: tuple[tuple[str, MessageValue], ...]

    def __init__(
        self,
        message: Message,
        hint: Message | None,
        /,
        **values: MessageValue,
    ) -> None: ...

    def text(self, lang: Lang) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `message` | `Message` | What is wrong. | Positional only. |
| `hint` | `Message` or `None` | The line that follows the message, such as `RUN_HELP_FOR_OPTIONS`, or `None` when the message already says what to write (choice 9). | No placeholders. Positional only, so a message can have a placeholder named `message` or `hint`. |
| `values` | `MessageValue` keyword arguments | The value of each placeholder of `message`. | One for each placeholder, and no others. `UsageError` keeps them as pairs sorted by name. |
| `lang` | `Lang` | The language that `text` writes. | None |

- Return value: A `UsageError`.
  - `text(lang)` gives `message.render(lang, **values)`. `cli` writes it, and then `hint.render(lang)` when `hint` is not `None`, each on its own line, to the error stream (2.10).
  - `str(error)` gives the English text, so a traceback names the mistake if a bug lets the error escape.
  - `__init__` sets `message`, `hint`, and `values` once, and no code changes them. An exception cannot be a frozen dataclass, because Python sets attributes such as `__traceback__` on it, so `UsageError` is a plain class.

Errors:

Creating a `UsageError` renders its message once in both languages, as `Problem` does (F03 design 2.2), so wrong values fail where the error is made.

| Error | When |
| --- | --- |
| `ValueError` | The names of `values` are not exactly the placeholders of `message`. |
| `TypeError` | A value is not a `str`, an `int`, or a `BiText`, or it is a `bool` or an `enum.Enum` member (F02 design 2.3). |
| `ValueError` | An `int` value has more than 4,300 digits (F02 design 2.3). |
| `ValueError` | `hint` has a placeholder. |

- Side effects: None
- Performance target: None

Example:

`NOT_A_WEEK` stands in for a message such as the one that F11's design gives.

```python
from recipe_menu.app import UsageError
from recipe_menu.lang import Lang
from recipe_menu.text import RUN_HELP_FOR_OPTIONS, Message

LANG_NOT_EN_OR_ZH = Message(
    '--lang must be en or zh, not "{lang}".',
    "--lang 必须是 en 或 zh，不能是“{lang}”。",
)
NOT_A_WEEK = Message('"{week}" is not a week.', "“{week}”不是一个周。")

error = UsageError(LANG_NOT_EN_OR_ZH, RUN_HELP_FOR_OPTIONS, lang="fr")
assert error.text(Lang.EN) == '--lang must be en or zh, not "fr".'
assert error.text(Lang.ZH) == "--lang 必须是 en 或 zh，不能是“fr”。"
assert error.hint is RUN_HELP_FOR_OPTIONS
assert str(error) == '--lang must be en or zh, not "fr".'
week = UsageError(NOT_A_WEEK, None, week="2026-W99")
assert week.hint is None
assert week.values == (("week", "2026-W99"),)

UsageError(NOT_A_WEEK, None)  # raises ValueError
UsageError(NOT_A_WEEK, None, week=None)  # raises TypeError
UsageError(NOT_A_WEEK, NOT_A_WEEK, week="2026-W99")  # raises ValueError
```

### 2.8 `problem_lines`, `first_error`, and `stop_at_error`

- Module: app
- Purpose: Show a problem of a data file in the layout of the prototypes, with the file and the place on one line and the message on the next ([architecture 6](../../architecture.md#6-error-handling)). `stop_at_error` ends a command at the first error in a data file, as every command other than `check` does. `cli` uses it for the settings, and the commands of F09 to F16 use it for their files. F07 writes each problem with `problem_lines`, with its own indents.

Signature:

```python
def problem_lines(problem: Problem, lang: Lang) -> tuple[str, str]: ...


def first_error(problems: Iterable[Problem]) -> Problem | None: ...


def stop_at_error(context: Context, error: Problem) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `problem` | `Problem` | The problem to show. | None |
| `lang` | `Lang` | The language of the lines. | None |
| `problems` | An iterable of `Problem` values | The problems that a reader gave, in its order. | None |
| `context` | `Context` | The language and the error stream. | None |
| `error` | `Problem` | The error that stops the command. | `Severity.ERROR`. |

- Return value:
  - `problem_lines` gives the pair `(where, what)`, with no indent. `where` is `str(problem.file)` when the problem has no place, and `FILE_AT_PLACE` with the file and the place otherwise, such as `recipes\mapo-tofu.toml, ingredient 3` and `recipes\mapo-tofu.toml，食材 3` on Windows. `what` is `problem.text(lang)`.
  - `first_error` gives the first problem with `Severity.ERROR`, or `None` when there is none.
  - `stop_at_error` gives 1, the exit code of a command that an error in a data file stopped. It writes three lines to `context.err`: `where`, then two spaces and `what`, and then `RUN_CHECK`, all in `context.lang`. The F11 prototype "A menu with a mistake" shows this layout.

The message of `app` is this. `{file}` is `str(problem.file)`, and `{place}` is the problem's place as a `BiText`.

| Name | English | Chinese |
| --- | --- | --- |
| `FILE_AT_PLACE` | `{file}, {place}` | `{file}，{place}` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `stop_at_error` gets a problem with `Severity.WARNING`. |

- Side effects: `stop_at_error` writes to `context.err`. The other two functions have none.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`.

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Context, first_error, problem_lines, stop_at_error
from recipe_menu.datafile import Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings
from recipe_menu.text import Message

UNKNOWN = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
FILE_MISSING = Message("The file is missing.", "文件不存在。")
mapo = Path("recipes", "mapo-tofu.toml")
problem = Problem.error(mapo, BiText("ingredient 3", "食材 3"), UNKNOWN, name="豆瓣酱")
assert problem_lines(problem, Lang.ZH) == (f"{mapo}，食材 3", "未知食材“豆瓣酱”。")
missing = Problem.error(Path("settings.toml"), None, FILE_MISSING)
assert problem_lines(missing, Lang.EN) == ("settings.toml", "The file is missing.")
warning = Problem.warning(mapo, None, FILE_MISSING)
assert first_error([warning, missing, problem]) is missing
assert first_error([warning]) is None

folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
_, problems = read_settings(folder)
error = first_error(problems)
assert error is not None
err = io.StringIO()
context = Context(Lang.EN, folder, Settings(), io.StringIO(), err, date(2026, 11, 10))
assert stop_at_error(context, error) == 1
assert err.getvalue().splitlines() == [
    "settings.toml, meals",
    '  Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
    'Run "recipe-menu check" to see every problem.',
]

stop_at_error(context, warning)  # raises ValueError
```

### 2.9 `main`

- Module: cli
- Purpose: The entry point of the `recipe-menu` command and of `python -m recipe_menu` ([architecture 2](../../architecture.md#2-tech-stack) and [10](../../architecture.md#10-test-setup)). It reads the outside world, runs the command line of 2.10, and gives the exit code. Tests call it with fixed values.

Signature:

```python
def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    today: date | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    commands: Sequence[Command] | None = None,
) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `argv` | A sequence of `str`, or `None` | The arguments after the program's name. | `None` gives `sys.argv[1:]`. |
| `environ` | A mapping of `str` to `str`, or `None` | The environment variables. `main` reads only `RECIPE_MENU_DATA`. | `None` gives `os.environ`. |
| `home` | `Path` or `None` | The home folder, for the default data folder and a leading `~` (2.10). | `None` gives `Path.home()`, which follows `USERPROFILE` on Windows and `HOME` on Linux. |
| `today` | `date` or `None` | Today's date. | `None` gives the local date of the PC's clock. |
| `stdout` | `TextIO` or `None` | The output stream. | `None` gives `sys.stdout`, after F02's `use_utf8`. |
| `stderr` | `TextIO` or `None` | The error stream. | `None` gives `sys.stderr`, after `use_utf8`. |
| `commands` | A sequence of `Command` values, or `None` | The commands, in the order of the help. | `None` gives `COMMANDS`. No two commands have the same words, and no one-word command has the first word of a two-word command. |

- Return value: The exit code of 2.10. The console script that `uv tool install` writes passes it to `sys.exit`, and `src/recipe_menu/__main__.py` runs `raise SystemExit(main())` when Python runs it as the main module.

`COMMANDS` is a tuple of `Command` values in `src/recipe_menu/cli/_commands.py`. In F05 it is empty. Each command feature imports its command module's `Command` values there and adds them in its mock PR, which is the only change that a command feature makes in `cli` (architecture 4).

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `commands` breaks its constraint. `main` checks it before it reads the arguments. This comes only from a wrong call. |

Any other exception from a command is a bug and goes on to Python, which shows its traceback (architecture 6). `main` turns only a `UsageError` into exit code 2, and `KeyboardInterrupt` into 130. It catches no error of the console streams, because architecture 6 has no row for them.

- Side effects: Each parameter that is `None` reads its part of the outside world, and `use_utf8` changes `sys.stdout` and `sys.stderr`. `main` looks whether the data folder is a folder, reads the settings, and runs the command, as 2.10 says. It writes no file itself.
- Performance target: None

Example:

In this example, `home` is an empty temporary folder, and `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, outside `home`. `LIST` stands in for the `list` command of F09. `environ` is the environment that `run` passes to `main`, and the last case sets `RECIPE_MENU_DATA` in it.

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run_list(context: Context, arguments: Arguments) -> int:
    tag = arguments.option("--tag")
    context.out.write(f"{context.lang.value} {tag}\n")
    return 0


LIST = Command(
    ("list",),
    Message("List the recipes.", "列出菜谱。"),
    run_list,
    options=("--tag",),
)
environ: dict[str, str] = {}


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ=environ,
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        commands=[LIST],
    )
    return code, out.getvalue(), err.getvalue()


data = str(folder.root)
assert run("list", "--tag", "素", "--data", data) == (0, "en 素\n", "")
assert run("--lang", "zh", "--data", data, "list") == (0, "zh None\n", "")
assert run("--version") == (0, "recipe-menu 0.1.0\n", "")

code, out, err = run("cook", "--data", data)
assert (code, out) == (2, "")
assert err.splitlines() == [
    'Unknown command "cook".',
    'Run "recipe-menu --help" to see the commands.',
]
code, _, err = run("list", "--tags", "素", "--data", data)
assert err.splitlines() == [
    '"list" has no option "--tags". Its own option is "--tag".',
    'Run "recipe-menu --help" to see the options.',
]
assert run("list", "--tag", "--data", data) == (2, "", "--tag needs a value.\n")
code, _, err = run("list", "--lang", "--lang", "zh", "--data", data)
assert err.splitlines() == ["--lang 后面要写一个值。", "运行“recipe-menu --help”查看选项。"]

folder.settings.write_text('language = "zh"\n', encoding="utf-8")
code, _, err = run("cook", "--data", data)
assert err.splitlines() == ["未知命令“cook”。", "运行“recipe-menu --help”查看命令。"]
assert run("list", "--data", data) == (0, "zh None\n", "")

code, _, err = run("list")
assert code == 1
default = home / "recipe-menu"
assert err.splitlines() == [
    f"There is no data folder at {default}.",
    'Run "recipe-menu init" to create it, or name another folder with --data.',
]
assert run("list", "--data", "~/recipe-menu") == (1, "", err)

environ["RECIPE_MENU_DATA"] = data
code, _, err = run("list", "--data")
assert err.splitlines() == ["--data 后面要写一个值。", "运行“recipe-menu --help”查看选项。"]
```

### 2.10 `recipe-menu`

- Module: cli
- Purpose: The command that you type ([requirements 3](../../requirements.md#3-how-users-interact-with-it) and [4](../../requirements.md#4-features)). It runs a command with its arguments, picks the data folder and the language, shows the help and the version, reports the mistakes on the command line, and exits with the codes of requirements 3. The F05 prototype shows it.

Signature:

```text
recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]
recipe-menu --help [--lang en|zh] [--data FOLDER]
recipe-menu --version
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `COMMAND` | One or two words | The command, such as `list` or `menu show`. | A command of `commands` (2.9). |
| `ARGUMENTS` | Words and options | The values of the command's argument, and the command's options with their values, such as `tomato-egg --servings 4`. | As the command declares them (2.5). |
| `--lang` | `en` or `zh` | The language of every message, the help included. | Exactly `en` or `zh`. |
| `--data` | A folder | The data folder. | Not empty. A leading `~` counts from the home folder, and a relative path from the current folder. |
| `--help` | A flag | Shows the help. | None |
| `--version` | A flag | Shows the version. | None |

`cli` reads the arguments by these rules:

1. An argument that starts with `--` is an option. `--help` and `--version` are flags. Every other option takes the next argument as its value. The next argument is no value when it is missing, empty, or starts with `--`. Then the option has no value, and `cli` reads the next argument on its own.
2. Every other argument is a word. The first one or two words are the command's words, and the rest are the values of its argument, in order. So options and words can come in any order, as in `recipe-menu --lang zh list --tag 素`.
3. `--lang`, `--data`, `--help`, and `--version` are global. `cli` takes them for every command, and no command declares them. Every other option belongs to the command.
4. The data folder is `Path(value)` for the value of the first `--data` that has a value. A `--data` with no value counts as absent here, and step 4 reports it. Without such a `--data`, it is `Path(value)` for the value of `RECIPE_MENU_DATA` when that variable is set and not empty. Without either, it is `home / "recipe-menu"`. When `Path(value).parts[0]` is `~`, `cli` replaces that part with `home`, so `~`, `~/OneDrive`, and on Windows `~\OneDrive` count from the home folder. `cli` then makes a relative path absolute with `Path.absolute()`, from the current folder. It expands no other form of `~` and no variable, and it does not resolve links. So `--data` wins over `RECIPE_MENU_DATA`, as v0.1-S20 expects.

`main` then takes these steps, in order:

1. It reads the arguments by rules 1 to 3, and finds the data folder by rule 4.
2. It reads the settings with `read_settings` when `os.path.isdir(folder.root)` is true. `os.path.isdir` never raises, so a look that fails counts as false, as in `datafile`. `Path.is_dir` can raise in Python 3.13, so `cli` does not use it.
3. It picks the language with `choose_lang(option, setting)` (F02 design 2.7). `option` is the value of the first `--lang` that has a value, when that value is `en` or `zh`, else `None`. A `--lang` with no value counts as absent here, and step 4 reports it. `setting` is the `language` of the settings when step 2 gave a `Settings`, else `None`. Every message from here on is in that language, a usage error included.
4. It checks each `--lang` and each `--data` in the order of the line. For each one, the first of these three rules that applies gives its error. An option with no value gives `OPTION_NEEDS_VALUE`. A second `--lang` or a second `--data` gives `OPTION_TWICE`. A value of `--lang` other than `en` and `zh` gives `LANG_NOT_EN_OR_ZH`. `--help` and `--version` may repeat (choice 10).
5. With `--help` on the line, it writes the help and exits with 0. Otherwise, with `--version` on the line, it writes the version and exits with 0. Neither looks at the rest of the line.
6. It finds the command in the words. No word gives `NO_COMMAND`. A first word that starts no command gives `UNKNOWN_COMMAND`. A first word that starts two-word commands needs a second word: no second word gives `INCOMPLETE_COMMAND`, and one that completes no command gives `UNKNOWN_COMMAND` with both words.
7. It checks the command's options in the order of the line. An option that the command does not declare gives `UNKNOWN_OPTION`. An option with no value gives `OPTION_NEEDS_VALUE`. The second of two gives `OPTION_TWICE`.
8. It checks the number of values of the argument (2.5). Too few give `TOO_FEW_ARGUMENTS`. Too many give `TOO_MANY_ARGUMENTS`, which names the first value too many.
9. It checks the data folder and the settings as the command's `FolderUse` says (2.5). A missing data folder gives `NO_DATA_FOLDER` and `RUN_INIT`, written to the error stream, and exit code 1. An error in the settings gives `stop_at_error` with the first error (2.8), and exit code 1.
10. It builds the `Context` (2.4) and the `Arguments` (2.6), runs the command, and exits with the code that `run` gives.

For a `UsageError` from steps 4 and 6 to 8 or from `run`, `cli` writes `error.text(lang)`, and then the hint when there is one, each on its own line, to the error stream, and exits with 2. Ctrl+C at any step exits with 130, and `cli` writes nothing more (architecture 6).

- Return value: The exit code, with the output of each case on its stream ([architecture 6](../../architecture.md#6-error-handling)):

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | The help, the version, or a command that worked. | The output stream. |
| 1 | The data folder is missing, the settings have an error, or the command gave 1. | The error stream for the messages of `cli`. A command writes its output to the output stream and the message that ends it to the error stream, as architecture 6 says. |
| 2 | A `UsageError`. | The error stream: the message, then its hint when it has one. |
| 130 | Ctrl+C. | Nothing more. |

The help is these lines, in this order, each ended by a line break and written to the output stream:

1. The usage line.
2. An empty line.
3. The summary.
4. An empty line.
5. The heading of the commands.
6. The table of the commands: for each command of `commands`, in their order, `usage.get(lang)` and `help_line.render(lang)`.
7. An empty line.
8. The heading of the options.
9. The table of the options: `--lang`, `--data`, `--version`, and `--help`, in this order.
10. An empty line.
11. The note on weeks.

Both tables are `format_table(rows, indent=2, min_widths=(width,))`, with the default gap of 3 (F02 design 2.9). `width` is the largest `display_width` of a first cell of either table, in either language. So the second column starts at the same place in both tables and in both languages. With the eight commands of v0.1, the widest first cell is `menu show [WEEK]`, of 16 columns, and the help gives exactly the two help outputs of the F05 prototype. The F02 review checked those lines with `min_widths=(16,)`.

The texts of the help and of the version are these:

| Line | English | Chinese |
| --- | --- | --- |
| The usage line | `Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en\|zh] [--data FOLDER]` | `用法：recipe-menu 命令 [参数] [--lang en\|zh] [--data 文件夹]` |
| The summary | `Keep your recipes, plan a week's menu, and make its shopping list.` | `保存菜谱，排一周的菜单，并生成它的购物清单。` |
| The heading of the commands | `Commands:` | `命令：` |
| The heading of the options | `Options:` | `选项：` |
| The note on weeks | `WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.` | `“周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。` |
| The version | `recipe-menu {version}`, with `__version__` (2.11) | `recipe-menu {version}`, with `__version__` (2.11) |

| Option | First cell, English | First cell, Chinese | Second cell, English | Second cell, Chinese |
| --- | --- | --- | --- | --- |
| `--lang` | `--lang en\|zh` | `--lang en\|zh` | `The language of the output. Default: the settings, else English.` | `输出语言。默认：设置里的语言，否则英文。` |
| `--data` | `--data FOLDER` | `--data 文件夹` | `The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.` | `数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。` |
| `--version` | `--version` | `--version` | `Show the version.` | `显示版本。` |
| `--help` | `--help` | `--help` | `Show this help.` | `显示这份帮助。` |

Errors:

Each `UsageError` of the parser names one of F02's two lines that point to `--help`, except `OPTION_NEEDS_VALUE` and `OPTION_TWICE` for an option of the command. The help does not list the command's options (choice 11), and each of the two messages already says what to change, so they name no line (decision A). `UNKNOWN_OPTION` names the command's own options, and its hint points to the help for the global options, in case the option was meant as one of them. It has three forms, picked by the number of the command's options, as `UNKNOWN_KEY` has two (F03 design 2.10). `INCOMPLETE_COMMAND` is a `Plural` (F02 design 2.4), picked by the number of commands that start with `word`. The English texts of `LANG_NOT_EN_OR_ZH` and `UNKNOWN_COMMAND`, with their hints, are the lines of the F05 prototype "Mistakes on the command line".

| Name | When | English | Chinese | Hint |
| --- | --- | --- | --- | --- |
| `OPTION_NEEDS_VALUE` | An option has no value (steps 4 and 7). | `{option} needs a value.` | `{option} 后面要写一个值。` | `RUN_HELP_FOR_OPTIONS` for `--lang` and `--data`. None for an option of the command. |
| `OPTION_TWICE` | An option with a value comes twice (steps 4 and 7). | `{option} is given twice.` | `{option} 写了两次。` | `RUN_HELP_FOR_OPTIONS` for `--lang` and `--data`. None for an option of the command. |
| `LANG_NOT_EN_OR_ZH` | The value of `--lang` is neither `en` nor `zh` (step 4). | `--lang must be en or zh, not "{lang}".` | `--lang 必须是 en 或 zh，不能是“{lang}”。` | `RUN_HELP_FOR_OPTIONS` |
| `NO_COMMAND` | The line has no word (step 6). | `Name a command, such as "recipe-menu list".` | `请写上一个命令，比如“recipe-menu list”。` | `RUN_HELP_FOR_COMMANDS` |
| `UNKNOWN_COMMAND` | The words name no command (step 6). | `Unknown command "{command}".` | `未知命令“{command}”。` | `RUN_HELP_FOR_COMMANDS` |
| `INCOMPLETE_COMMAND`, for one command | The only word starts exactly one two-word command (step 6). Only a test's own `commands` have such a word. | `The only command that starts with "{word}" is {commands}.` | `以“{word}”开头的命令只有{commands}。` | `RUN_HELP_FOR_COMMANDS` |
| `INCOMPLETE_COMMAND`, for more commands | The only word starts two or more two-word commands, such as `menu` (step 6). | `The commands that start with "{word}" are {commands}.` | `以“{word}”开头的命令有{commands}。` | `RUN_HELP_FOR_COMMANDS` |
| `UNKNOWN_OPTION`, for no options | The command declares no option (step 7). | `"{command}" has no option "{option}". It has no options of its own.` | `“{command}”没有选项“{option}”。它没有自己的选项。` | `RUN_HELP_FOR_OPTIONS` |
| `UNKNOWN_OPTION`, for one option | The command declares one option, and not this one (step 7). | `"{command}" has no option "{option}". Its own option is {options}.` | `“{command}”没有选项“{option}”。它自己的选项是{options}。` | `RUN_HELP_FOR_OPTIONS` |
| `UNKNOWN_OPTION`, for more options | The command declares two or more options, and not this one (step 7). | `"{command}" has no option "{option}". Its own options are {options}.` | `“{command}”没有选项“{option}”。它自己的选项有{options}。` | `RUN_HELP_FOR_OPTIONS` |
| `TOO_FEW_ARGUMENTS` | The argument has too few values (step 8). | `An argument is missing. Write "recipe-menu {usage}".` | `缺少参数。请写成“recipe-menu {usage}”。` | `RUN_HELP_FOR_COMMANDS` |
| `TOO_MANY_ARGUMENTS` | The argument has too many values (step 8). | `Unexpected argument "{argument}". Write "recipe-menu {usage}".` | `多余的参数“{argument}”。请写成“recipe-menu {usage}”。` | `RUN_HELP_FOR_COMMANDS` |

These messages end a command with exit code 1 (step 9). Their texts are the lines of the F05 prototype "No data folder yet".

| Name | English | Chinese |
| --- | --- | --- |
| `NO_DATA_FOLDER` | `There is no data folder at {folder}.` | `{folder} 没有数据文件夹。` |
| `RUN_INIT` | `Run "recipe-menu init" to create it, or name another folder with --data.` | `运行“recipe-menu init”创建它，或用 --data 指定别的文件夹。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `option` | The option as the line writes it, such as `--data` or `--lang=zh`. |
| `lang` | The value of `--lang` as the line writes it. |
| `command` | The command's words, or the words that name no command, joined by a space, such as `menu cook`. |
| `word` | The first word, such as `menu`. |
| `commands` | `and_list` of the quoted words of each command that starts with `word`, in the order of `commands`: `"menu new" and "menu show"` and `“menu new”和“menu show”`. |
| `options` | `and_list` of the command's options, each in quotation marks, in the order of `options` (2.5): `"--tag"`, or `"--servings" and "--tag"` and `“--servings”和“--tag”`. |
| `usage` | The command's `usage` (2.5), such as `show ID`, or `menu new [WEEK]` and `menu new [周]`. |
| `argument` | The first value too many, as the line writes it. |
| `folder` | `str(folder.root)`, the data folder's full path. |
| `version` | `__version__` (2.11). |

- Side effects: Looks whether the data folder is a folder, and reads `settings.toml` through `read_settings` when it is. `cli` writes no file. The command that it runs reads and writes what its feature's design says.
- Performance target: None. The commands of PT01 include this start (see the rules at the top of section 2).

Example:

In this example, `home` is an empty temporary folder. `SHOW` and `MENU_SHOW` stand in for two commands of F09 and F11. Lines 5 and 6 are lines of the F05 prototype "Help in Chinese", whose first column is 16 columns wide because of `menu show [WEEK]` in English.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run(context: Context, arguments: Arguments) -> int:
    return 0


SHOW = Command(
    ("show",),
    Message("Show one recipe.", "查看一个菜谱。"),
    run,
    Argument(Message("ID", "ID")),
    ("--servings",),
)
MENU_SHOW = Command(
    ("menu", "show"),
    Message("Show a week menu.", "查看一个周菜单。"),
    run,
    Argument(Message("WEEK", "周"), required=False),
)


def help_lines(*argv: str) -> list[str]:
    out = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=io.StringIO(),
        commands=[SHOW, MENU_SHOW],
    )
    assert code == 0
    return out.getvalue().splitlines()


lines = help_lines("--help", "--lang", "zh")
assert len(lines) == 15
assert lines[0] == "用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]"
assert lines[4] == "命令："
assert lines[5] == "  show ID            查看一个菜谱。"
assert lines[6] == "  menu show [周]     查看一个周菜单。"
assert lines[10].startswith("  --data 文件夹      数据文件夹。")
english = help_lines("show", "x", "--help")
assert english[6] == "  menu show [WEEK]   Show a week menu."
assert english[9].startswith("  --lang en|zh       The language of the output.")
assert help_lines("--help", "--help") == english
```

v0.1-S19 to v0.1-S22 run the other cases of the F05 prototype with the real commands.

### 2.11 `__version__`

- Module: cli, in `src/recipe_menu/__init__.py`
- Purpose: The version that `--version` shows (2.10). Architecture 3 gives `src/recipe_menu/__init__.py` to `cli`. F01 created it with only its doc comment, because mypy needs it, and F05 adds this one name (choice 12).

Signature:

```python
__version__ = "0.1.0"
```

Parameters: None

- Return value: None. `__version__` is a `str` that equals the `version` of `[project]` in `pyproject.toml`. A test of F05 keeps the two equal, so a release that raises the version changes both lines.

Errors: None

- Side effects: None
- Performance target: None

Example:

The example runs in the root of the repository.

```python
import tomllib
from pathlib import Path

import recipe_menu

project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
assert recipe_menu.__version__ == project["version"] == "0.1.0"
```

## 3. Changes to existing interfaces

None. No interface that F01 to F04 implemented changes. Each exported name keeps its signature and its behavior, and the tests of F01 to F04 pass unchanged. F05 adds names to the interface of `datafile`, as F04 did, and it changes internal files of `recipes`.

1. `datafile` exports `read_servings`, `MIN_SERVINGS`, and `MAX_SERVINGS` (3.1). The messages `SERVINGS_NOT_A_NUMBER`, `SERVINGS_TOO_FEW`, and `SERVINGS_TOO_MANY` move from `recipes/messages.py` into `datafile/messages.py` with the same texts, and they stay internal. `read_recipe` still reports a missing `servings` key itself, and it reads the value with `read_servings`, so it gives the same problems in the same order (F04 design 2.6). `Recipe` can check its range with `MIN_SERVINGS` and `MAX_SERVINGS`.
2. `src/recipe_menu/__init__.py` gets `__version__` (2.11).
3. F05 uses F02's `BiText`, `Lang`, `Message`, `MessageValue`, `RUN_CHECK`, `RUN_HELP_FOR_COMMANDS`, `RUN_HELP_FOR_OPTIONS`, `and_list`, `choose_lang`, `display_width`, `format_table`, and `use_utf8`. It uses `DataFolder`, `Problem`, `Severity`, `read_toml`, and the messages of F03 design 2.10, and `Report`, `read_list`, `read_text`, and `report_unknown_keys` of F04 design 3.2. It uses them as their designs give them and changes none of them.

### 3.1 `read_servings`, `MIN_SERVINGS`, and `MAX_SERVINGS`

- Module: datafile
- Purpose: The one rule for a servings number in a data file: an integer from 1 to 100, shown in a message only when it has at most 15 digits ([F04 design](../F04-recipe-files/design.md), choice 2). `read_recipe` (F04), `read_settings` (2.3), and F06's reader of week menus check servings with it. F09 checks `show --servings` against `MIN_SERVINGS` and `MAX_SERVINGS`.

Signature:

```python
MIN_SERVINGS: Final[int] = 1
MAX_SERVINGS: Final[int] = 100


def read_servings(value: object, place: BiText, report: Report) -> int | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `value` | `object` | A servings value as `read_toml` gives it, such as `2` or `"2"`. | None. The caller has found the key. |
| `place` | `BiText` | The place of the value, such as "servings" and "份数". | None |
| `report` | `Report` | Where the problem goes (F04 design 3.2). | None |

- Return value: `value` when it is an `int`, not a `bool`, from `MIN_SERVINGS` to `MAX_SERVINGS`. Otherwise `None`, after `read_servings` adds one error at `place` by this table:

| Value | Message |
| --- | --- |
| Not an integer, such as `"2"`, `2.5`, or `true`, or an integer of 16 or more digits, such as `0x` followed by 5,000 digits | `SERVINGS_NOT_A_NUMBER` |
| An integer from -999,999,999,999,999 to 0 | `SERVINGS_TOO_FEW`, with `servings` set to the value |
| An integer from 101 to 999,999,999,999,999 | `SERVINGS_TOO_MANY`, with `servings` set to the value |

So the value `servings` has at most 15 digits, and `Problem` never meets F02's limit of 4,300 digits. The messages keep their texts of F04 design 2.6:

| Name | English | Chinese |
| --- | --- | --- |
| `SERVINGS_NOT_A_NUMBER` | `Servings must be a whole number from 1 to 100, such as 2.` | `份数必须是 1 到 100 之间的整数，比如 2。` |
| `SERVINGS_TOO_FEW` | `Servings must be a whole number of 1 or more, not {servings}.` | `份数必须是不小于 1 的整数，不能是 {servings}。` |
| `SERVINGS_TOO_MANY` | `Servings must be a whole number of 100 or less, not {servings}.` | `份数必须是不大于 100 的整数，不能是 {servings}。` |

Errors: None. `read_servings` never raises for bad data.

- Side effects: Appends at most one problem to `report.problems`.
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import MAX_SERVINGS, MIN_SERVINGS, Report, read_servings
from recipe_menu.lang import BiText, Lang

report = Report(Path("settings.toml"))
place = BiText("servings", "份数")
assert read_servings(4, place, report) == 4
assert read_servings(MIN_SERVINGS, place, report) == 1
assert read_servings(MAX_SERVINGS, place, report) == 100
assert report.problems == []
assert read_servings(0, place, report) is None
assert read_servings(True, place, report) is None
assert read_servings(10**15, place, report) is None
assert read_servings(101, place, report) is None
assert [problem.text(Lang.EN) for problem in report.problems] == [
    "Servings must be a whole number of 1 or more, not 0.",
    "Servings must be a whole number from 1 to 100, such as 2.",
    "Servings must be a whole number from 1 to 100, such as 2.",
    "Servings must be a whole number of 100 or less, not 101.",
]
assert report.problems[0].place == place
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `settings`, `app`, and `cli` own what architecture 3 gives them, and each imports only the modules that architecture 3 and 4 allow. `Meal`, `Settings`, `Context`, `Command`, and `UsageError` hold what architecture 5.2 lists, and `Command.folder` and `UsageError.hint` add what choices 6 and 9 need. `Argument`, `Arguments`, and `FolderUse` are helper values, as F03 added `Severity` and F04 added `Steps`. `problem_lines`, `first_error`, and `stop_at_error` belong in `app`, and `read_servings` belongs in `datafile`, the only module that `recipes`, `settings`, and `menus` can all import. Version 0.2 changes none of this, so the reasons of round 1 hold. Finding 6 is resolved. Step 2 of 2.10 looks at the folder with `os.path.isdir`, as `datafile` does, because `Path.is_dir` in Python 3.13.18 raises `PermissionError`. Finding 7 is resolved, and it needs no change to the requirements or the architecture. Requirements 3 and Q15 say that `--data` or `RECIPE_MENU_DATA` names another folder, and architecture 1 names the same three sources. Neither says how `cli` reads the name, so the design decides it. No prototype or scenario writes `~` in a value, and v0.1-S20 uses full paths. Rule 4 takes the home folder from `main`'s `home`, not from `Path.expanduser`, which reads `USERPROFILE` or `HOME` itself. So tests give a fixed home folder, as architecture 8 requires. In Windows PowerShell 5.1, a native command gets `~\OneDrive\recipe-menu` unchanged, as choice 13 says. Finding 9, not blocking: rule 4 tests `Path(value).parts[0]`, and `pathlib` drops a leading `.`. So `--data ./~/recipe-menu` and, on Windows, `.\~\recipe-menu` also count from the home folder, while a shell leaves `./~` as it is. Choice 13 calls the rule "a leading `~`" and says that `cli` expands no other form. The Interface Designer can say that `./~` counts too, or test the text of the value: it is `~`, or it starts with `~/`, or, on Windows, with `~\`. |
| Follows the error handling and naming conventions | Pass | Troy decided A to D on 2026-11-12 as recommended, and section 2 records each decision with its reason and the PR that carries it out. The design follows the architecture as those decisions change it. Every hint in 2.10 is a `Message` or none (decision A), step 9 checks the data folder in `cli` (decision B), and choice 8 writes `RUN_CHECK` after a problem (decision D). Finding 1 is resolved. Rule 4 and step 3 take the first `--data` and the first `--lang` that have a value. Step 4 checks each one in the order of the line: no value, then a second one, then a value of `--lang` other than `en` and `zh`. In the model, `list --lang --lang zh` reports `--lang 后面要写一个值。` in Chinese, `list --lang zh --lang fr` reports `--lang 写了两次。`, and `list --lang fr --lang zh` reports "fr" in the language of the settings. `list --data` with `RECIPE_MENU_DATA` set reads the settings of that folder and reports the missing value in their language. Finding 2 is resolved. Choice 10 and step 4 let a flag repeat, so `--help --help` and `--version --version` exit with 0. Finding 3 is resolved. `UNKNOWN_OPTION` names the command's own options in three forms and keeps `RUN_HELP_FOR_OPTIONS`. `OPTION_NEEDS_VALUE` and `OPTION_TWICE` name no hint for an option of the command, because the help does not list it. `INCOMPLETE_COMMAND` is a `Plural`, with "The only command that starts with" for one command. The model gives each form in both languages. Finding 8, not blocking: choice 9 says "An error whose message already says what to write names `None`." But `INCOMPLETE_COMMAND`, `UNKNOWN_OPTION`, `TOO_FEW_ARGUMENTS`, and `TOO_MANY_ARGUMENTS` say what to write and keep a hint, because the help lists the commands, their usage, and the global options. The table of 2.10 and the paragraph above it give the exact rule, so the Developer and the Test Designer get one answer. The Architect's `[docs]` PR words architecture 6 as "An error whose message already says what to write, such as a wrong week, can name no line", which fits the table. Choice 9 can say "can name `None`" to match. Finding 10, not blocking: the form of `UNKNOWN_OPTION` for no options has no `{options}`, and both forms of a `Plural` need the same placeholders (F02 design 2.4). So the three forms are a `Message` and a `Plural`, which the Developer names in `cli/messages.py`, and not one `Plural`. The other reasons of round 1 hold. Choices 4, 5, and 10 follow `read_recipe`, requirements 3, and ADR-0005. `main` catches only `UsageError` and `KeyboardInterrupt`, and every name follows PEP 8 (architecture 8). |
| Does not duplicate an existing interface | Pass | The reasons of round 1 hold. `read_servings` keeps the servings rule in one place, and the three servings messages move with their texts. F05 calls the shared functions and messages of F02 to F04 and rewrites none of them. Version 0.2 builds the list of `UNKNOWN_OPTION` with `and_list`, as `INCOMPLETE_COMMAND` builds its list. The leading `~` uses the `home` that `main` already takes. The folder probe of step 2 is one call of `os.path.isdir`. The probe of `datafile` is internal, so `cli` copies no exported interface. |
| Depends only on features earlier in the order | Pass | F05 uses F01's `Lang`, F02's `text`, F03's `datafile`, and the helpers that F04 added to `datafile`, and it changes internal files of F04's `recipes`. All four features come before F05 and pass their tests on main. Version 0.2 adds no dependency on a feature or a package. Finding 5 is resolved. Section 2 says that the console script adds no third-party dependency. It also says that the Architect approves the R16 warning in the implementation PR after checking that `pyproject.toml` gains only `[project.scripts]` with `recipe-menu = "recipe_menu.cli:main"`. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | Each assumption between modules is written in the design. `FolderUse` makes what `cli` checks part of each `Command`, and the order of `COMMANDS` is the order of the help. `UNKNOWN_OPTION` reads only `Command.options`, which each command declares, so `cli` still knows no command by name. Finding 4 is resolved. Section 2 plans one mock PR and one implementation PR, each with a soft-limit reason under R03, which fits troy-mode's one PR for each stage. The notes of round 1 for F06 and F07 stay with those designs. |
| Changes an implemented interface only through the change flow | Pass | Section 3 is the same as in version 0.1. No exported name of F01 to F04 changes, `datafile` gains three names, and the servings messages move between internal files. In the Architect's model of version 0.2, the tests on the branch give 269 passed and 2 skipped, the same as the code on the branch. So section 3 rightly says None. The note of round 1 for PR 2 stands: a test that checks only a constant that the mock defines passes against the mock and breaks R09. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 13 choices and decisions A to D against the requirements and the architecture. Decisions A, B, and C change architecture 6, and C also changes ADR-0002, so Troy decides them. Decision D changes the F05 prototype, so Troy decides it. Option 2 of decision A would change the F11 prototype and v0.1-S15. No other choice changes the architecture, a prototype, or a requirement. Each file has 25 code blocks, each equal to its mirror, and the 23 `python` blocks parse. On top of the F01 to F04 code of the branch, the Architect built a model of sections 2 and 3. It ran the 12 examples on fresh copies of `tests/data/example/` with Python 3.13.18 on Windows, and every assertion and all 20 `# raises` hold. With the eight commands of v0.1 and the help lines of the prototype, the model's help gives the 21 lines of "Help in English" and the 21 lines of "Help in Chinese" exactly, with a first column of 16. The model also gives `recipe-menu 0.1.0` and the lines of "Mistakes on the command line" and "No data folder yet" in both languages. For "A broken settings file", its first two lines are the prototype's, and `RUN_CHECK` follows them. The tests on the branch pass on the model, 269 passed and 2 skipped. Findings 1 to 7 do not block. | Approved. The main session puts decisions A to D to Troy when Troy approves this design (R18). Once Troy decides A to C, the Architect writes the architecture change and an ADR in a docs PR, before the F05 mock PR. The Interface Designer decides findings 1 to 3, 6, and 7, and corrects the PR plan (finding 4) and the sentence on the console script (finding 5) in its next revision. |
| 2 | No blocking issue. Version 0.2 resolves findings 1 to 7 of round 1 and records Troy's decisions A to D of 2026-11-12. The leading `~` of finding 7 needs no change to the requirements or the architecture. Each file still has 25 code blocks, each equal to its mirror, and the 23 `python` blocks parse. The Architect updated its model to version 0.2 and ran the 12 examples on fresh copies of `tests/data/example/` with Python 3.13.18 on Windows. Every assertion and all 20 `# raises` hold. On the model of round 1, the example of 2.9 fails, so its new assertions test the new rules. With the eight commands of v0.1, the help still gives the 21 lines of "Help in English" and of "Help in Chinese" exactly. The model gives the other lines of the F05 prototype as in round 1, and the tests on the branch pass on it, 269 passed and 2 skipped. Findings 8 to 10 do not block. | Approved. The Interface Designer can settle findings 8 to 10 in a revision before the merge, or leave them. Before the F05 mock PR, the Architect writes decisions A to C in a `[docs]` PR, with the wording of finding 8. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-12 | First draft. |
| 0.2 | 2026-11-12 | Answers round 1 of the Architect review and records Troy's decisions of 2026-11-12. Troy accepted the recommendation of each of decisions A to D, and section 2 names the PRs that carry them out. 2.7 drops option 2 of decision A. The first `--data` and the first `--lang` with a value pick the data folder and the language, and step 4 reports one with no value. A flag may repeat (choice 10 and 2.10). `UNKNOWN_OPTION` names the command's own options, `OPTION_NEEDS_VALUE` and `OPTION_TWICE` name no hint for an option of the command, and `INCOMPLETE_COMMAND` has a form for one command (choices 9 and 11, and 2.10). `cli` replaces a leading `~` with the home folder (choice 13 and 2.10). Step 2 of 2.10 looks at the folder with `os.path.isdir`. Section 2 plans one mock PR and one implementation PR with R03 soft-limit reasons, and the Architect approves the R16 warning of the console script. The table of the requirement points to step 3 of 2.10 for the language. The examples of 2.9 and 2.10 cover the new cases. |
| 1.0 | 2026-11-12 | Approved by Troy. |
