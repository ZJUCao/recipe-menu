---
troy-doc: "F09-design"
lang: "en"
version: "1.0"
updated: "2026-11-13"
status: "Approved by Troy on 2026-11-13"
mirror: "design.zh-CN.md"
---

# F09 List and show recipes: interface design

## 1. Feature

- ID and name: F09 List and show recipes
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F01, F02, F04

## 2. Interfaces

F09 builds the command module `browse` in `src/recipe_menu/commands/browse/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.browse` exports two names, `LIST_COMMAND` (2.1) and `SHOW_COMMAND` (2.3), and its `__init__.py` lists them in `__all__`. The commands that you type are `recipe-menu list` (2.2) and `recipe-menu show` (2.4). Their messages live in `src/recipe_menu/commands/browse/messages.py` and are internal to the module (architecture 8). The other files behind them are the Developer's choice. In its mock PR, F09 adds both commands to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `CHECK_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). The F09 prototype `docs/prototypes/F09-list-show.md` shows both commands, and the F05 prototype "The language from the settings" shows `list --tag` in the language of the settings.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F09 gives |
| --- | --- |
| `recipe-menu list` prints a table of the recipes sorted by ID. | `recipe-menu list` (2.2). It writes one row for each recipe that `read_recipes` gives, in the order of the IDs, which is the order of `list_recipe_ids` (F04 design 2.5). |
| `--tag` keeps only the recipes with that tag. | The option `--tag` of `LIST_COMMAND` (2.1). It takes a tag's name in either language and finds the tag with `Catalog.find_tag` (choice 4). |
| `recipe-menu show ID` prints one recipe: its names, servings, tags, ingredients with notes, and steps. | `recipe-menu show` (2.4), with the argument `ID` of `SHOW_COMMAND` (2.3). |
| `--servings N` scales the quantities. | The option `--servings` of `SHOW_COMMAND`, from 1 to 100. `show` scales each quantity with F01's `Quantity.scale` (choice 8). |
| `show` writes a quantity in the unit that the recipe uses ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | `Quantity.to_text` (F01 design 2.11), which keeps the recipe's unit. |
| A name, a note, or the steps may lack one language. Commands then show the other language (requirements 3). | The fallback of `BiText` and `Steps`, and the heading of steps in the other language (choice 3). |
| `list` and `show` each finish within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus (PT01, [requirements 7.1](../../requirements.md#71-performance-targets)). | The performance target of 2.2 and 2.4, and choice 10. |

These rules hold for every interface below:

- `browse` imports only `app`, `lang`, `units`, `text`, `datafile`, `catalog`, and `recipes` from the package. Its row of architecture 3 allows them, and it needs neither `settings`, `menus`, nor `shopping` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `browse` reaches the disk only through the readers of F03 and F04, which read through `datafile` (architecture 8). It writes no file ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 1](../../architecture.md#1-context-and-constraints)). It writes only to `context.out` and `context.err`. It reads nothing of the outside world itself, and it keeps no state.
- Neither command uses `context.settings` or `context.today`. Without `--servings`, `show` shows the recipe's own servings. The servings of the settings belong to a dish of a menu that gives none (requirements 3).
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). Each command stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). `run` raises a `UsageError` only for a wrong value on the command line, before it reads a file or writes any output (F05 design, section 2). Any other exception that reaches `cli` is a bug.
- `LIST_COMMAND` and `SHOW_COMMAND` are frozen `Command` values (F05 design 2.5). F09 adds no value type.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- `recipe-menu list` and `recipe-menu show` have the performance target PT01 (choice 10). Each command reads each file that it needs once, and writes its output once, after the last file. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 and 2.4 give their rules.

1. **Two commands in one module, after `check` in the help.** Architecture 8 gives `list` and `show` the module `browse`. F09 adds `LIST_COMMAND` and `SHOW_COMMAND` to `COMMANDS` after `CHECK_COMMAND`, so `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND)`, in the help's order of F05 design section 2. Both commands have `FolderUse.READ`. So `cli` stops them when the data folder is missing or the settings have an error (F05 design 2.5), as v0.1-S20 and v0.1-S22 expect. `list` declares the option `--tag`. `show` declares the argument `ID` and the option `--servings`. The help keeps F05's layout. With these four commands, the widest first cell is still `--data FOLDER` or `--data 文件夹`, of 13 columns, so the second column starts after 18 columns, as after F07 and F08. 2.1 gives the lines of the commands. With the eight commands of v0.1, the help gives the two outputs of the F05 prototype.
2. **What each command reads, and where it stops.** Each command reads only the files that it needs (architecture 8), in the order of the steps of `check` (F07 design 2.2): the catalog, then the listing of `recipes/`, then the recipes. Neither command reads the pantry or a menu. Each stops at the first error of each reader with `stop_at_error`, which writes the problem and `RUN_CHECK` and gives 1. `check` reads the same files with the same readers and the same arguments, so the error that stopped a command is among the errors of `check` (F07 design, choice 8).
   - `list` reads the catalog, then looks for the tag of `--tag` in it, and then reads every recipe with `read_recipes` (2.2). It does not also call `list_recipe_ids`, because `read_recipes` returns the problems of the listing before those of the files (F04 design 2.7). So `list` reports each problem of the listing once. An unknown tag stops `list` before it reads a recipe, so `list --tag breakfast` parses no recipe file.
   - `show` checks the values of the command line first. It then reads the catalog, lists `recipes/` with `list_recipe_ids`, looks for the ID among the IDs, and reads only that recipe with `read_recipe` (2.4). An error of the listing stops `show`, also when it names another file, such as `recipes\Rice Bowl.toml`. Architecture 6 lets no command other than `check` go on after an error. A listing with an error can also lack the ID that you asked for: `recipes\rice.TOML` gives an error and no ID `rice` (F04 design 2.5). An error in another recipe file does not stop `show`, because `show` does not parse that file.
3. **Warnings and a missing language.** Neither command writes a warning, and a warning never changes the exit code (architecture 6). `check` reports the warnings. A text that lacks the chosen language shows the other language, as requirements 3 asks: a name and a note through `BiText.get`, and the steps through `Steps.get`. When `Steps.exact` gives `None` for the chosen language, `show` writes `STEPS_IN_OTHER_LANGUAGE` as the heading of the steps: `Steps (no English steps, so these are the Chinese steps)` in English, as the F09 prototype "A missing language" shows, and `步骤（没有中文步骤，所以这里是英文步骤）` in Chinese. The first line of `show` holds each name that the recipe has, the chosen language first. So a recipe without an English name shows its Chinese name alone, and the line never repeats a name. A name and a note get no other mark. In the table of `list`, a name without the chosen language also shows the other language.
4. **The tag of `--tag`.** `list` finds the tag with `Catalog.find_tag` (F03 design 2.6). So the value matches a tag's name in either language by F03's rules: whitespace at both ends does not count, and case counts only for the letters A to Z. `list --tag 快手`, `list --tag quick`, and `list --tag " QUICK "` keep the same recipes. `list` keeps a recipe when its `tags` hold that tag. When `find_tag` finds no tag, `list` writes `UNKNOWN_TAG`, or `NO_TAGS` for a catalog with no tags, to the error stream and exits with 1, as the prototype shows. The message names the value as you typed it, and lists the catalog's tags in the catalog's order, as the prototype lists "quick, home-style, vegetarian, spicy, and staple". In a row of the table, the tags come in the recipe's order, which is the order of its file (F04 design 2.3). So `mapo-tofu` shows "spicy, home-style", as the prototype does, although the catalog lists home-style first.
5. **The column widths of a list with a tag.** The tables of `list --tag` keep the column widths of the whole list, as the F05 prototype "The language from the settings" and the F09 prototype "List the recipes with one tag" show, and as v0.1-S10 and v0.1-S21 expect. So `list` passes `format_table` the argument `min_widths` with three widths, for the ID, the name in the chosen language, and the servings. Each width is the largest `display_width` of a line of that cell, over every recipe that `read_recipes` gave (F02 design 2.8). Each cell is split into lines as rule 1 of `format_table` splits it, with `cell.splitlines()` (F02 design 2.9). `format_table` measures each line of a cell, and a name can hold a line break, because F04 removes only the whitespace at both ends of a text (F04 design 2.6). `format_table` adds the heading's width itself. The tags are the last column, which `format_table` does not pad. So a list with a tag lines up with the list without one, whatever the tag. Without `--tag`, the three widths equal the ones that `format_table` finds itself by its rule 2, so they change nothing, also for a name of two lines.
6. **A list with no recipe.** When `list` keeps no recipe, it writes one line and no table, and exits with 0. The line is `NO_RECIPES`, `No recipes.`, when the folder holds no recipe, and `NO_RECIPE_WITH_TAG`, such as `No recipe has the tag "soup".`, when no recipe has the tag of `--tag`. An empty list is not an error, as no match is not an error in the F10 prototype "No match", whose wording these lines follow. A heading with no rows would say nothing more. `init` writes one recipe, so `recipes/` holds none only after you delete every recipe file.
7. **An ID that cannot be a recipe ID, and an ID with no recipe.** `show` checks `ID` with `is_recipe_id` before it reads a file (F04 design 2.4). A value that breaks the rule is a wrong argument value, such as `Mapo`, `../rice`, `""`, `con`, or `tomato\u2010egg` with U+2010 HYPHEN. For it, `show` raises `UsageError(NOT_A_RECIPE_ID, None, id=value)`, and `cli` exits with 2 (architecture 6, F05 design 2.7). The message says what to run, so it names no hint (ADR-0008): `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.`. F06's `NOT_A_WEEK` treats a week that cannot exist, such as `2026-W99`, the same way, and the F11 prototype shows it with exit code 2. The message gives no reason, so that one text holds for every rule of `is_recipe_id`, the Windows device names of rule 4 included. An ID that follows the rule but is not among the IDs of `list_recipe_ids` has no recipe file. For it, `show` writes `UNKNOWN_ID`, the line of the F09 prototype "An unknown ID", to the error stream and exits with 1, as requirements 3 asks for a missing file. The hint of `UNKNOWN_ID` runs `search` with the ID, which then has only small letters, digits, and `-`, so the hint is always a valid command line. So `show` never passes `DataFolder.recipe_file` or `read_recipe` a value that they reject (F03 design 2.1, F04 design 2.6). `show` compares the ID exactly with the IDs of the listing, so Windows and Linux give the same result. Troy decides this choice (point C below).
8. **`--servings`.** The value is a whole number from `MIN_SERVINGS` to `MAX_SERVINGS` of `datafile`, 1 to 100, the range that Troy accepted for every servings number in F04 (F04 design, choice 2, and F05 design 3.1). It is written in the ASCII digits `0` to `9`, with no leading `0`, no sign, and no other character, such as `4` or `100`. Any other value gives `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)`. The message shows the value as the text that you typed, never as an `int`, so no value meets F02's limit of 4,300 digits. A value of 5,000 digits gives the message, not Python's `ValueError` (F05 design, section 2). The rule reads the text, because Python's `int` also reads `+4`, ` 4`, `1_0`, `\uff14` (FULLWIDTH DIGIT FOUR), and `\u0664` (ARABIC-INDIC DIGIT FOUR). The message says what to write, so it names no hint (ADR-0008), as F05's other errors of a command's option do. `show` multiplies each quantity by `Fraction(servings, recipe.servings)` with `Quantity.scale`, and writes it with `Quantity.to_text`. `to_text` keeps the recipe's unit and rounds up to at most two decimals (F01 design 2.9 and 2.11). So 3 eggs for 3 servings of a 2-serving recipe are `4.5 pieces`. A quantity "to taste" stays to taste. F01 design 2.9 promises only that `Quantity.scale` gives a value equal to `TO_TASTE`, and its example checks it with `==`. So code that tests it uses `is_to_taste` or `==`, never `is`. The steps stay as written, as the prototype says. The servings line shows the servings and, in parentheses, the recipe's own servings: `Servings: 4 (the recipe makes 2)` and `份数：4（菜谱按 2 份写）`. When `--servings` equals the recipe's servings, nothing is scaled, and `show` writes the same lines as without the option, such as `Servings: 2   Tags: quick, home-style`.
9. **Numbers in messages.** The messages of `browse` show the servings of a recipe, the value of `--servings` once it is from 1 to 100, and the number of recipes that `list` keeps. A recipe's servings are from 1 to 100 (F04 design 2.3), and the number of recipes is the length of a tuple. A wrong value of `--servings` goes into its message as text. A problem in a file reaches the error stream only through `stop_at_error`, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `browse` meets F02's limit of 4,300 digits (F02 design 2.3).
10. **Speed.** PT01 asks that `list` with 1,000 recipes and `show` each finish within 1 second on Troy's PC, the median of 5 runs (v0.1-S28 and v0.1-S29). `list` reads less than `check`: the settings in `cli`, the catalog, one listing of `recipes/`, and each recipe file once, and neither the pantry nor the 52 menus. `check` takes a median of about 0.82 s on a PT01 folder on Troy's PC since F07's reader speedup (PR #50), and the menus took about 0.08 s of `check`'s time in the F07 review. To that, `list` adds its table, whose time grows with the number of its characters: about 40,000 on a PT01 folder, each measured with `display_width` at most three times, once for `min_widths` and twice inside `format_table`. No `Message.render` runs for a row, because the tags come from `comma_list` and the servings from `str`. So `list` should take about as long as `check`, or less. This is an estimate from those times, not a measurement. `show` reads the settings, a catalog of 300 ingredients, one listing, and one recipe, so its time stays close to the start of the tool. F09 needs no `[refactor]` side PR before its mock. The test plan can time both commands on a PT01 folder, as F07-T25 times `check`. If `list` comes close to the limit, the first step is the change that the Code Reviewer named on PR #50: `Message.render` parses its template's placeholders on every call, which costs about 0.06 s on a PT01 folder. Parsing them once for each message is an internal change to `text`, and the Architect decides whether it changes F02's interface. It would land as a `[refactor]` PR before F09's implementation PR.

Troy decides these three points. The design follows the recommendation of each.

- **A. The steps of `red-braised-pork`** (Architect, F04 review). The F09 prototype "A missing language" shows four Chinese steps for `red-braised-pork`: `五花肉冷水下锅，焯水后捞出。`, `小火把冰糖炒成焦糖色，下五花肉翻炒上色。`, `加生抽、姜片和热水，没过肉，小火炖 1 小时。`, and `大火收汁，撒上葱段。`. The example file `tests/data/example/recipes/red-braised-pork.toml` has three other steps. v0.1-S12 step 3 expects the prototype's output, so one of the two must change.
  - Option 1, recommended: the test data changes. A test PR replaces the three steps of the file with the four steps of the prototype, word for word. Only F04-T38 (`test_f04_t38_the_other_six_example_recipes` in `tests/test_f04_example_recipes.py`) depends on them. It asserts that the file has 3 Chinese steps, and compares the recipe with the steps that it reads from the file. So its count changes from 3 to 4 in the same PR, and the tests on main stay green. No other test reads the steps of that file. The F07 tests append English steps to it, and the two Chinese steps in `tests/f04_support.py` come from the example of F04 design 2.2, not from the file. No document changes, because `docs/prototypes/example-data.md` says only that the steps are in Chinese.
  - Option 2: the requirements change. The Product Manager writes the three steps of the file into the prototype section "A missing language", in a `[docs]` PR that Troy approves. v0.1-S12 then holds as written, and no test changes.
  - The reason for option 1: the prototype is approved text that v0.1-S12 checks, and the example data folder is test data that follows the prototypes (architecture 10). Option 1 changes one count in one test and no requirement.
- **B. New texts.** No prototype shows these texts. Each follows the wording of an existing message. The recommendation is to accept them as 2.2 and 2.4 give them.
  - The English servings line of a scaled recipe, `Servings: 4 (the recipe makes 2)   Tags: quick, home-style`, for the Chinese prototype's `份数：4（菜谱按 2 份写）   标签：快手、家常`.
  - The Chinese heading of English steps, `步骤（没有中文步骤，所以这里是英文步骤）`, for the prototype's `Steps (no English steps, so these are the Chinese steps)`.
  - The Chinese texts of the prototype's two errors. `未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。` follows F03's `UNKNOWN_CATEGORY`, and `没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。` follows `RUN_CHECK`.
  - In both languages: `NO_RECIPES`, `NO_RECIPE_WITH_TAG`, the form of `UNKNOWN_TAG` for one tag, `NO_TAGS`, `NOT_A_RECIPE_ID`, `SERVINGS_NOT_1_TO_100`, and `SERVINGS_ONLY`, the servings line of a recipe with no tags.
- **C. An ID that cannot be a recipe ID** (choice 7).
  - Option 1, recommended: a usage error with exit code 2, `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.`.
  - Option 2: the output of "An unknown ID" with exit code 1 for every value that the listing lacks. Its hint `Run "recipe-menu search Mapo" to find it.` helps with `Mapo`. For a value such as `""`, though, the hint names a wrong command line, so that case needs another message anyway.
  - The reason for option 1: requirements 3 give exit code 2 to a wrong command line, and F06 and the F11 prototype treat a week that cannot exist the same way.

These later features are meant to build on F09. Their own designs decide the details.

- F10's `search` lists recipes in a table with the columns ID and Name, as `list` does. The F10 prototype "No match" writes one line and no table, as `list` does when it keeps no recipe (choice 6). Architecture 4 lets `search` import `browse`. F09 exports only its two commands, so that no name is exported before a feature uses it. F10's design adds to `browse` what the two commands share, such as the cells of a recipe's row or the widths of choice 5, or keeps its own.
- The hint of `UNKNOWN_ID` runs `recipe-menu search`, which F10 adds. Until F10's mock PR, that command line gives `Unknown command "search".`.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/browse/__init__.py` and `messages.py`, maybe one internal file, and the entries in `src/recipe_menu/cli/_commands.py`. It defines every message and both commands with all their fields, so the help lists `list` and `show`, and both commands run. Its `run` functions read no file and raise nothing. For example, each writes nothing and gives 0. So a new test of the output, of exit code 1, or of a `UsageError` that `run` raises fails against the mock (R09). A test that checks only the fields of a command, the help, a message, or exit code 0 passes against the mock and breaks R09. So does a test of what `cli` does before it runs a command, such as a missing data folder, broken settings, `list extra`, or `--tag` with no value. The implementation (PR 5) reads the files and writes the output. Each PR fits R03's 5 files. Under option 1 of point A, the change to the example file lands in a test PR together with F04-T38.

### 2.1 `LIST_COMMAND`

- Module: browse
- Purpose: The description of the `list` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` writes the list of 2.2.

Signature:

```python
LIST_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("list",)
#   help_line = LIST_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ("--tag",)
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("list",)`. | None |
| `help_line` | `Message` | `LIST_HELP`: "List the recipes." and "列出菜谱。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Reads the catalog and every recipe, and writes the list of 2.2. | Gives 0 or 1. Raises nothing for bad data. |
| `argument` | `None` | `list` takes no argument. | None |
| `options` | A tuple of `str` | `("--tag",)`, the tag of the recipes to keep (2.2). | `cli` passes a value only when it is not empty and does not start with `--` (F05 design 2.10). |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `list` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.out`, and `context.err`. It uses neither `context.settings` nor `context.today`. |
| `arguments` | `Arguments` | What the command line gives `list` (F05 design 2.6). | No values. `arguments.option("--tag")` is the value of `--tag`, or `None`. |

- Return value: `LIST_COMMAND`, a `Command`.
  - `LIST_COMMAND.usage` is `list` in both languages, so the help shows `list`, and a usage error quotes `recipe-menu list`.
  - `LIST_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its output in `context.lang`, and gives 0 or 1.

After F09, the help lists these commands, with the second column after 18 columns (choice 1). In English:

```text
Commands:
  init            Create the data folder with example data.
  check           Check every data file for mistakes.
  list            List the recipes.
  show ID         Show one recipe.
```

In Chinese:

```text
命令：
  init            创建数据文件夹和示例数据。
  check           检查每个数据文件有没有错误。
  list            列出菜谱。
  show ID         查看一个菜谱。
```

Errors: None. `run` never raises for bad data. It raises no `UsageError` either, because every value of `--tag` is a name to look for. A name that the catalog lacks gives exit code 1 (2.2).

- Side effects: Those of 2.2. `run` reads the catalog and the recipe files through the readers of F03 and F04, writes to `context.out` or `context.err`, and writes no file.
- Performance target: None. PT01 times `recipe-menu list` (2.2) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context holds the default settings, and the output follows `context.lang`. The help comes from `COMMANDS`, which holds `init`, `check`, `list`, and `show` after F09.

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.browse import LIST_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings

assert LIST_COMMAND.words == ("list",)
assert LIST_COMMAND.usage == BiText("list", "list")
assert LIST_COMMAND.help_line.render(Lang.EN) == "List the recipes."
assert LIST_COMMAND.help_line.render(Lang.ZH) == "列出菜谱。"
assert (LIST_COMMAND.argument, LIST_COMMAND.options) == (None, ("--tag",))
assert LIST_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert LIST_COMMAND.run(context, Arguments((), (("--tag", "quick"),))) == 0
assert out.getvalue().splitlines() == [
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "",
    "共 3 个菜谱带有标签“快手”。",
]
assert err.getvalue() == ""


def help_lines(*argv: str) -> list[str]:
    out = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=io.StringIO(),
    )
    assert code == 0
    return out.getvalue().splitlines()


english = help_lines("--help")
assert len(english) == 17
assert english[4:9] == [
    "Commands:",
    "  init            Create the data folder with example data.",
    "  check           Check every data file for mistakes.",
    "  list            List the recipes.",
    "  show ID         Show one recipe.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[7:9] == ["  list            列出菜谱。", "  show ID         查看一个菜谱。"]
```

### 2.2 `recipe-menu list`

- Module: browse
- Purpose: The command that lists the recipes ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 2, and [4](../../requirements.md#4-features)). It prints a table of the recipes sorted by ID, and `--tag` keeps only the recipes with that tag. The F09 prototype "List the recipes" and "List the recipes with one tag" show it.

Signature:

```text
recipe-menu list [--tag TAG] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--tag` | A tag's name | Keeps only the recipes with that tag. | A name of a tag of the catalog, in either language, as `Catalog.find_tag` matches it (choice 4). Not empty, and given at most once (F05 design 2.10). |
| `--lang` | `en` or `zh` | The language of the output and of every message. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `list`. | None |

`list` takes these steps, in order. Each step that reads a file uses what the earlier steps gave.

1. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `list` gives `stop_at_error(context, error)` for the first one.
2. With `--tag`, `catalog.find_tag(value)` gives `tag`. When it gives `None`, `list` writes `UNKNOWN_TAG`, picked by the number of the catalog's tags, or `NO_TAGS` when the catalog has none, to the error stream, and gives 1.
3. `read_recipes(context.folder, catalog)` gives `recipes` and their problems (F04 design 2.7). With an error among the problems, `list` stops at the first one with `stop_at_error`.
4. `list` keeps each recipe whose `tags` hold `tag`, or every recipe without `--tag`, in the order of `recipes`, which is the order of the IDs.
5. It writes the output below to the output stream and gives 0.

The warnings of steps 1 and 3 change nothing (choice 3).

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `list` wrote its list, also an empty one. | The output stream: the table and the count line, or one line when `list` keeps no recipe. |
| 1 | A file has an error, or the catalog has no tag with the name of `--tag`. | The error stream: the three lines of `stop_at_error`, or the one line of `UNKNOWN_TAG` or `NO_TAGS`. Nothing goes to the output stream. |

When `list` keeps one or more recipes, its output is these lines, in this order, each ended by a line break:

1. The lines of `format_table(rows, min_widths=widths)`, with no indent and the default gap of 3 (F02 design 2.9).
2. An empty line.
3. The count line: `RECIPE_COUNT` without `--tag`, and `RECIPES_WITH_TAG` with it, each picked by the number of recipes that `list` keeps.

`rows` is the heading row, and then one row for each recipe that `list` keeps:

| Column | Heading | Cell |
| --- | --- | --- |
| ID | `ID_HEADING` | `recipe.id` |
| Name | `NAME_HEADING` | `recipe.name.get(context.lang)` |
| Servings | `SERVINGS_HEADING` | `str(recipe.servings)` |
| Tags | `TAGS_HEADING` | `comma_list(tag.name for tag in recipe.tags).get(context.lang)`, in the recipe's order. The empty text for a recipe with no tags. |

`widths` holds, for each of the first three columns, the largest `display_width` of a line of its cells, over every recipe of step 3, kept or not, with each cell split into lines as rule 1 of `format_table` splits it (choice 5). `list` writes each text as the file holds it, so the rules of `format_table` apply to it, such as a name with a line break, which takes two lines.

When `list` keeps no recipe, its output is one line: `NO_RECIPES` without `--tag`, and `NO_RECIPE_WITH_TAG` with it (choice 6).

The messages of `list` are these. `RECIPE_COUNT`, `RECIPES_WITH_TAG`, and `UNKNOWN_TAG` are `Plural` values (F02 design 2.4). `RECIPE_COUNT` and `RECIPES_WITH_TAG` are picked by `count`, and `UNKNOWN_TAG` by the number of the catalog's tags. `NO_TAGS` is a `Message` of its own for a catalog with no tags, because it has no `{tags}`, and both messages of a `Plural` need the same placeholders.

| Name | English | Chinese |
| --- | --- | --- |
| `LIST_HELP` | `List the recipes.` | `列出菜谱。` |
| `ID_HEADING` | `ID` | `ID` |
| `NAME_HEADING` | `Name` | `名称` |
| `SERVINGS_HEADING` | `Servings` | `份数` |
| `TAGS_HEADING` | `Tags` | `标签` |
| `RECIPE_COUNT`, for one | `{count} recipe.` | `共 {count} 个菜谱。` |
| `RECIPE_COUNT`, for more | `{count} recipes.` | `共 {count} 个菜谱。` |
| `RECIPES_WITH_TAG`, for one | `{count} recipe has the tag "{tag}".` | `共 {count} 个菜谱带有标签“{tag}”。` |
| `RECIPES_WITH_TAG`, for more | `{count} recipes have the tag "{tag}".` | `共 {count} 个菜谱带有标签“{tag}”。` |
| `NO_RECIPES` | `No recipes.` | `没有菜谱。` |
| `NO_RECIPE_WITH_TAG` | `No recipe has the tag "{tag}".` | `没有菜谱带有标签“{tag}”。` |
| `UNKNOWN_TAG`, for one tag | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`, for more tags | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `count` | The number of recipes that `list` keeps, the length of a tuple (choice 9). |
| `tag` | The name of the tag that `find_tag` gave, as its `BiText`, so each language shows its own name: `quick` and `快手` for `--tag 快手`. |
| `value` | The value of `--tag` as you typed it. |
| `tags` | `and_list` of the names of the catalog's tags, each as its `BiText`, in the catalog's order: "quick, home-style, vegetarian, spicy, and staple" and "快手、家常、素、辣和主食". |

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `list` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 1, with the three lines of `stop_at_error` on the error stream | The catalog, the listing of `recipes/`, or a recipe file has an error (steps 1 and 3). |
| Exit code 1, with `UNKNOWN_TAG` or `NO_TAGS` on the error stream | The catalog has no tag with the name of `--tag` (step 2). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `list` has `FolderUse.READ`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "extra". Write "recipe-menu list".` | A word follows `list`. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for one option and then `RUN_HELP_FOR_OPTIONS`, such as `"list" has no option "--tags". Its own option is "--tag".` | An option other than `--tag` and the four global options. |
| Exit code 2, with `OPTION_NEEDS_VALUE` or `OPTION_TWICE` and no hint, such as `--tag needs a value.` | `--tag` has no value, or comes twice. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. Nothing more is written (F05 design 2.10). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `list` then reads `catalog.toml` once, lists `recipes/` once, and reads each recipe file once, all through the readers of F03 and F04. With an unknown tag, it reads no recipe file. It reads neither `pantry.toml` nor a menu. It writes to the output stream or the error stream. It writes no file, so every file and folder keeps its bytes and modification time (v0.1-S23).
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. The runs give the outputs of the F09 prototype, then of the F05 prototype "The language from the settings". The catalog then gets a tag that no recipe has, and then no tags, which also shows that `list` looks for the tag before it reads a recipe. A mistake in `mapo-tofu` stops `list`, and a folder with no recipe file gives one line.

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def run(data: Path, *argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(data)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


ENGLISH = [
    "ID                   Name                      Servings   Tags",
    "choy-sum             Stir-fried choy sum       2          quick, vegetarian",
    "cola-wings           Cola chicken wings        2          home-style",
    "mapo-tofu            Mapo tofu                 2          spicy, home-style",
    "red-braised-pork     Red-braised pork belly    2          home-style",
    "rice                 Steamed rice              2          staple",
    "tomato-egg           Tomato and egg stir-fry   2          quick, home-style",
    "tomato-egg-noodles   Tomato and egg noodles    2          quick, staple",
    "",
    "7 recipes.",
]
CHINESE = [
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "cola-wings           可乐鸡翅     2      家常",
    "mapo-tofu            麻婆豆腐     2      辣、家常",
    "red-braised-pork     红烧肉       2      家常",
    "rice                 米饭         2      主食",
    "tomato-egg           番茄炒蛋     2      快手、家常",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
    "",
    "共 7 个菜谱。",
]
assert run(folder.root, "list") == (0, ENGLISH, [])
assert run(folder.root, "list", "--lang", "zh") == (0, CHINESE, [])

quick = [ENGLISH[0], ENGLISH[1], ENGLISH[6], ENGLISH[7], "", '3 recipes have the tag "quick".']
assert run(folder.root, "list", "--tag", "快手") == (0, quick, [])
assert run(folder.root, "list", "--tag", " QUICK ") == (0, quick, [])
quick_zh = [CHINESE[0], CHINESE[1], CHINESE[6], CHINESE[7], "", "共 3 个菜谱带有标签“快手”。"]
assert run(folder.root, "list", "--tag", "quick", "--lang", "zh") == (0, quick_zh, [])
tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
breakfast = [f'Unknown tag "breakfast". {tags}']
assert run(folder.root, "list", "--tag", "breakfast") == (1, [], breakfast)
breakfast_zh = ["未知标签“breakfast”。现有标签：快手、家常、素、辣和主食。"]
assert run(folder.root, "list", "--tag", "breakfast", "--lang", "zh") == (1, [], breakfast_zh)

settings_text = folder.settings.read_text(encoding="utf-8")
zh_settings = settings_text.replace('language = "en"', 'language = "zh"')
folder.settings.write_text(zh_settings, encoding="utf-8")
vegetarian_zh = [CHINESE[0], CHINESE[1], "", "共 1 个菜谱带有标签“素”。"]
assert run(folder.root, "list", "--tag", "素") == (0, vegetarian_zh, [])
vegetarian = [ENGLISH[0], ENGLISH[1], "", '1 recipe has the tag "vegetarian".']
assert run(folder.root, "list", "--tag", "素", "--lang", "en") == (0, vegetarian, [])
folder.settings.write_text(settings_text, encoding="utf-8")

catalog_text = folder.catalog.read_text(encoding="utf-8")
staple = '{ zh = "主食", en = "staple" },'
soup = catalog_text.replace(staple, staple + '\n  { zh = "汤", en = "soup" },')
folder.catalog.write_text(soup, encoding="utf-8")
assert run(folder.root, "list", "--tag", "汤") == (0, ['No recipe has the tag "soup".'], [])
assert run(folder.root, "list", "--tag", "soup", "--lang", "zh") == (
    0,
    ["没有菜谱带有标签“汤”。"],
    [],
)
no_tags = catalog_text[: catalog_text.index("tags = [")] + "tags = []\n"
folder.catalog.write_text(no_tags, encoding="utf-8")
no_quick = ['Unknown tag "quick". The catalog has no tags.']
assert run(folder.root, "list", "--tag", "quick") == (1, [], no_quick)
choy = Path("recipes", "choy-sum.toml")
assert run(folder.root, "list") == (
    1,
    [],
    [
        f"{choy}, tags",
        '  Unknown tag "快手". Add it to the catalog\'s tags.',
        'Run "recipe-menu check" to see every problem.',
    ],
)
folder.catalog.write_text(catalog_text, encoding="utf-8")

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "list") == (1, [], stopped)
assert run(folder.root, "list", "--tag", "breakfast") == (1, [], breakfast)
code, out, err = run(folder.root, "list", "extra")
assert (code, out) == (2, [])
assert err == [
    'Unexpected argument "extra". Write "recipe-menu list".',
    'Run "recipe-menu --help" to see the commands.',
]

for path in folder.recipes.iterdir():
    path.unlink()
assert run(folder.root, "list") == (0, ["No recipes."], [])
assert run(folder.root, "list", "--lang", "zh") == (0, ["没有菜谱。"], [])
assert run(folder.root, "list", "--tag", "quick") == (0, ['No recipe has the tag "quick".'], [])
```

### 2.3 `SHOW_COMMAND`

- Module: browse
- Purpose: The description of the `show` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` writes the recipe of 2.4.

Signature:

```python
SHOW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("show",)
#   help_line = SHOW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(ID_ARGUMENT)
#   options = ("--servings",)
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("show",)`. | None |
| `help_line` | `Message` | `SHOW_HELP`: "Show one recipe." and "查看一个菜谱。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Checks the values of the command line, reads the catalog, the listing of `recipes/`, and the recipe, and writes the recipe of 2.4. | Gives 0 or 1. Raises `UsageError` for a wrong value of `ID` or `--servings`, before it reads a file or writes any output. |
| `argument` | `Argument` | `Argument(ID_ARGUMENT)`, which is required and does not repeat. `ID_ARGUMENT` is `ID` in both languages, the name in the F05 prototype's help. | So `cli` passes exactly one value (F05 design 2.5). |
| `options` | A tuple of `str` | `("--servings",)`, the servings to scale to (2.4). | `cli` passes a value only when it is not empty and does not start with `--` (F05 design 2.10). |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `show` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.out`, and `context.err`. It uses neither `context.settings` nor `context.today`. |
| `arguments` | `Arguments` | What the command line gives `show` (F05 design 2.6). | `arguments.values` is `(ID,)`. `arguments.option("--servings")` is the value of `--servings`, or `None`. |

- Return value: `SHOW_COMMAND`, a `Command`.
  - `SHOW_COMMAND.usage` is `show ID` in both languages, so the help shows `show ID`, and a usage error quotes `recipe-menu show ID`.
  - `SHOW_COMMAND.run(context, arguments)` takes the steps of 2.4, writes its output in `context.lang`, and gives 0 or 1.

Errors:

`run` checks `--servings` first and then `ID`, as `cli` checks the options before the argument (F05 design 2.10, steps 7 and 8). Neither check reads a file.

| Error | When |
| --- | --- |
| `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)` | The value of `--servings` breaks the rule of choice 8. |
| `UsageError(NOT_A_RECIPE_ID, None, id=value)` | `is_recipe_id(value)` is false for the value of `ID` (choice 7). |

- Side effects: Those of 2.4. `run` reads the catalog, the listing of `recipes/`, and one recipe file through the readers of F03 and F04, writes to `context.out` or `context.err`, and writes no file.
- Performance target: None. PT01 times `recipe-menu show` (2.4) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`. The first context holds settings with 4 servings, which `show` does not use. Neither call that raises writes a line to either stream.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.commands.browse import SHOW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SHOW_COMMAND.words == ("show",)
assert SHOW_COMMAND.usage == BiText("show ID", "show ID")
assert SHOW_COMMAND.help_line.render(Lang.EN) == "Show one recipe."
assert SHOW_COMMAND.help_line.render(Lang.ZH) == "查看一个菜谱。"
assert SHOW_COMMAND.argument == Argument(Message("ID", "ID"))
assert SHOW_COMMAND.options == ("--servings",)
assert SHOW_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
four = Context(Lang.EN, folder, Settings(servings=4), out, err, date(2026, 11, 10))
assert SHOW_COMMAND.run(four, Arguments(("rice",))) == 0
assert out.getvalue().splitlines()[1] == "Servings: 2   Tags: staple"

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert SHOW_COMMAND.run(context, Arguments(("rice",), (("--servings", "3"),))) == 0
assert out.getvalue().splitlines() == [
    "Steamed rice  米饭",
    "Servings: 3 (the recipe makes 2)   Tags: staple",
    "",
    "Ingredients",
    "  Rice   240 g",
    "",
    "Steps",
    "  1. Rinse the rice, add water, and soak it for 20 minutes.",
    "  2. Cook it in a rice cooker, and let it rest for 10 minutes.",
]
assert err.getvalue() == ""

SHOW_COMMAND.run(context, Arguments(("Mapo",)))  # raises UsageError
SHOW_COMMAND.run(context, Arguments(("rice",), (("--servings", "0"),)))  # raises UsageError
```

### 2.4 `recipe-menu show`

- Module: browse
- Purpose: The command that shows one recipe ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 2, and [4](../../requirements.md#4-features)). It prints the recipe's names, servings, tags, ingredients with notes, and steps, and `--servings` scales the quantities. The F09 prototype "Show one recipe", "Show one recipe for 4 servings, in Chinese", "A missing language", and "An unknown ID" show it.

Signature:

```text
recipe-menu show ID [--servings N] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `ID` | A recipe ID | The recipe to show, such as `tomato-egg`. | Exactly one value. `is_recipe_id(ID)` is true (choice 7). |
| `--servings` | A whole number | The servings that the quantities are scaled to. | From 1 to 100, written as choice 8 says. Without the option, the recipe's own servings. Given at most once (F05 design 2.10). |
| `--lang` | `en` or `zh` | The language of the output and of every message. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `show`. | None |

`show` takes these steps, in order. Steps 1 and 2 read no file.

1. With `--servings`, it checks the value by choice 8, and raises `UsageError(SERVINGS_NOT_1_TO_100, None, servings=value)` for a wrong one.
2. It checks `ID` with `is_recipe_id`, and raises `UsageError(NOT_A_RECIPE_ID, None, id=ID)` when the check is false.
3. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `show` gives `stop_at_error(context, error)` for the first one.
4. `list_recipe_ids(context.folder)` gives the IDs and their problems (F04 design 2.5). With an error among the problems, `show` stops at the first one with `stop_at_error`.
5. When `ID` is not among the IDs, `show` writes `UNKNOWN_ID` to the error stream and gives 1.
6. `read_recipe(context.folder, catalog, ID)` gives the recipe and its problems (F04 design 2.6). With an error among the problems, `show` stops at the first one with `stop_at_error`. Its warnings change nothing (choice 3).
7. It writes the recipe to the output stream, as below, and gives 0.

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `show` wrote the recipe. | The output stream: the lines below. |
| 1 | A file has an error, or no recipe has the ID. | The error stream: the three lines of `stop_at_error`, or the one line of `UNKNOWN_ID`. Nothing goes to the output stream. |
| 2 | The value of `ID` or of `--servings` is wrong. | The error stream: the message, which `cli` writes, with no hint. Nothing goes to the output stream. |

The output is these lines, in this order, each ended by a line break:

1. The names: the recipe's name in `context.lang`, then two spaces and its name in the other language, from `recipe.name.exact`. A name that the recipe lacks is left out with its two spaces (choice 3). The two spaces are the same in both languages, so the line is not a `Message` (architecture 8).
2. The servings line: `SERVINGS_LINE`, or `SERVINGS_ONLY` for a recipe with no tags. Its `servings` is the recipe's servings. With `--servings` other than the recipe's servings, it is `SCALED_SERVINGS` with the value of `--servings` and the recipe's servings, as the `BiText` of `to_bitext` (choice 8).
3. An empty line.
4. For a recipe with ingredients: `INGREDIENTS_HEADING`, then the lines of `format_table(rows, indent=2)` with the default gap of 3, and then an empty line. A recipe with no ingredients has none of these lines.
5. The heading of the steps: `STEPS_HEADING` when `recipe.steps.exact(context.lang)` gives steps, and `STEPS_IN_OTHER_LANGUAGE` when it gives `None` (choice 3).
6. One line for each step of `recipe.steps.get(context.lang)`, in order: two spaces, the step's number from 1, a period, a space, and the step as the file writes it, such as `  1. Cut the tomatoes into wedges.`. The number and the period are the same in both languages, so the line is not a `Message`.

`rows` holds one row for each ingredient line of the recipe, in the file's order, and no heading row:

| Column | Cell |
| --- | --- |
| Ingredient | `line.ingredient.name.get(context.lang)` |
| Quantity | `line.quantity.scale(factor).to_text(context.lang)`, where `factor` is `Fraction(servings, recipe.servings)` with the value of `--servings`, and 1 without it (choice 8). |
| Note | `line.note.get(context.lang)`, or the empty text when the line has no note. |

The messages of `show` are these. `STEPS_IN_OTHER_LANGUAGE` is rendered in English only when the English steps are missing, and in Chinese only when the Chinese steps are missing, so each template names the language that is missing.

| Name | English | Chinese |
| --- | --- | --- |
| `SHOW_HELP` | `Show one recipe.` | `查看一个菜谱。` |
| `ID_ARGUMENT` | `ID` | `ID` |
| `SERVINGS_LINE` | `Servings: {servings}   Tags: {tags}` | `份数：{servings}   标签：{tags}` |
| `SERVINGS_ONLY` | `Servings: {servings}` | `份数：{servings}` |
| `SCALED_SERVINGS` | `{servings} (the recipe makes {recipe_servings})` | `{servings}（菜谱按 {recipe_servings} 份写）` |
| `INGREDIENTS_HEADING` | `Ingredients` | `食材` |
| `STEPS_HEADING` | `Steps` | `步骤` |
| `STEPS_IN_OTHER_LANGUAGE` | `Steps (no English steps, so these are the Chinese steps)` | `步骤（没有中文步骤，所以这里是英文步骤）` |
| `UNKNOWN_ID` | `No recipe has the ID "{id}". Run "recipe-menu search {id}" to find it.` | `没有 ID 为“{id}”的菜谱。运行“recipe-menu search {id}”查找它。` |
| `NOT_A_RECIPE_ID` | `"{id}" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `“{id}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。` |
| `SERVINGS_NOT_1_TO_100` | `--servings must be a whole number from 1 to 100, not "{servings}".` | `--servings 必须是 1 到 100 之间的整数，不能是“{servings}”。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `servings` | In `SERVINGS_LINE` and `SERVINGS_ONLY`: the recipe's servings as an `int`, or the `BiText` of `SCALED_SERVINGS`. In `SCALED_SERVINGS`: the value of `--servings` as an `int` from 1 to 100. In `SERVINGS_NOT_1_TO_100`: the value of `--servings` as you typed it, a `str` (choice 9). |
| `recipe_servings` | The recipe's servings, an `int` from 1 to 100. |
| `tags` | `comma_list` of the names of `recipe.tags`, each as its `BiText`, in the recipe's order: "quick, home-style" and "快手、家常". |
| `id` | The value of `ID` as you typed it. In `UNKNOWN_ID`, it follows `is_recipe_id`, so the command line of the hint is valid (choice 7). |

With these rules, the lines of the F09 prototype follow: for example, `份数：4（菜谱按 2 份写）   标签：快手、家常` and `  食用油   4 汤匙`.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `show` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `SERVINGS_NOT_1_TO_100` and no hint, such as `--servings must be a whole number from 1 to 100, not "0".` | The value of `--servings` breaks the rule of choice 8 (step 1). |
| Exit code 2, with `NOT_A_RECIPE_ID` and no hint, such as `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | The value of `ID` breaks the rule of `is_recipe_id` (step 2). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream | The catalog, the listing of `recipes/`, or the recipe's file has an error (steps 3, 4, and 6). |
| Exit code 1, with `UNKNOWN_ID` on the error stream, such as `No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.` | `recipes/` holds no recipe file with the ID (step 5). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `show` has `FolderUse.READ`. |
| Exit code 2, with `TOO_FEW_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `An argument is missing. Write "recipe-menu show ID".` | The line names no ID. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "rice". Write "recipe-menu show ID".` | The line names two or more IDs. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for one option and then `RUN_HELP_FOR_OPTIONS`, such as `"show" has no option "--tag". Its own option is "--servings".` | An option other than `--servings` and the four global options. |
| Exit code 2, with `OPTION_NEEDS_VALUE` or `OPTION_TWICE` and no hint, such as `--servings needs a value.` | `--servings` has no value, or comes twice. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. Nothing more is written (F05 design 2.10). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `show` then reads `catalog.toml` once, lists `recipes/` once, and reads `recipes/<ID>.toml` once, all through the readers of F03 and F04. It reads no other recipe file, neither `pantry.toml` nor a menu (architecture 8), and no file at all after a wrong value on the command line. It writes to the output stream or the error stream. It writes no file, so every file and folder keeps its bytes and modification time (v0.1-S23).
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. The runs give the outputs of the F09 prototype. The steps of `red-braised-pork` are compared with the file, because point A decides them. A new recipe `boiled-egg` lacks its Chinese name, note, and steps. A mistake in `mapo-tofu` stops only `show mapo-tofu`, and a file name that is not an ID stops every `show`.

```python
import io
import tomllib
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def run(data: Path, *argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(data)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


TOMATO_EGG = [
    "Tomato and egg stir-fry  番茄炒蛋",
    "Servings: 2   Tags: quick, home-style",
    "",
    "Ingredients",
    "  Tomato        300 g      cut into wedges",
    "  Egg           3 pieces",
    "  Scallion      1 stalk    chopped",
    "  Salt          to taste",
    "  Sugar         1 tsp",
    "  Cooking oil   2 tbsp",
    "",
    "Steps",
    "  1. Cut the tomatoes into wedges. Beat the eggs with a pinch of salt.",
    "  2. Heat 1 tbsp of oil. Scramble the eggs until just set, and take them out.",
    "  3. Heat the rest of the oil. Stir-fry the tomatoes until soft, and add the sugar.",
    "  4. Return the eggs, season with salt, and scatter the scallion on top.",
]
FOUR_ZH = [
    "番茄炒蛋  Tomato and egg stir-fry",
    "份数：4（菜谱按 2 份写）   标签：快手、家常",
    "",
    "食材",
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  葱       2 根     切葱花",
    "  盐       适量",
    "  糖       2 茶匙",
    "  食用油   4 汤匙",
    "",
    "步骤",
    "  1. 番茄切块。鸡蛋加少许盐打散。",
    "  2. 热锅下 1 汤匙油，炒鸡蛋至刚凝固，盛出。",
    "  3. 下剩下的油，炒番茄至软，加糖。",
    "  4. 倒回鸡蛋，加盐调味，撒上葱花。",
]
assert run(folder.root, "show", "tomato-egg") == (0, TOMATO_EGG, [])
assert run(folder.root, "show", "tomato-egg", "--servings", "2") == (0, TOMATO_EGG, [])
assert run(folder.root, "show", "tomato-egg", "--servings", "4", "--lang", "zh") == (0, FOUR_ZH, [])
code, out, err = run(folder.root, "show", "tomato-egg", "--servings", "3")
assert (code, err) == (0, [])
assert out[1] == "Servings: 3 (the recipe makes 2)   Tags: quick, home-style"
assert out[4:10] == [
    "  Tomato        450 g        cut into wedges",
    "  Egg           4.5 pieces",
    "  Scallion      1.5 stalks   chopped",
    "  Salt          to taste",
    "  Sugar         1.5 tsp",
    "  Cooking oil   3 tbsp",
]
assert out[10:] == TOMATO_EGG[10:]

code, out, err = run(folder.root, "show", "red-braised-pork")
assert (code, err) == (0, [])
assert out[:11] == [
    "Red-braised pork belly  红烧肉",
    "Servings: 2   Tags: home-style",
    "",
    "Ingredients",
    "  Pork belly   1 jin      cut into 3 cm cubes",
    "  Rock sugar   30 g",
    "  Soy sauce    2 tbsp",
    "  Ginger       3 slices",
    "  Scallion     2 stalks",
    "",
    "Steps (no English steps, so these are the Chinese steps)",
]
pork = tomllib.loads(folder.recipe_file("red-braised-pork").read_text(encoding="utf-8"))
assert out[11:] == [f"  {n}. {step}" for n, step in enumerate(pork["steps"]["zh"], 1)]

egg = [
    'name = { en = "Boiled egg" }',
    "servings = 1",
    "tags = []",
    "ingredients = [",
    '  { item = "鸡蛋", amount = "2", note = { en = "at room temperature" } },',
    '  { item = "盐", amount = "适量" },',
    "]",
    "[steps]",
    'en = ["Boil the eggs for 8 minutes."]',
]
folder.recipe_file("boiled-egg").write_text("\n".join(egg) + "\n", encoding="utf-8")
boiled = [
    "Boiled egg",
    "Servings: 1",
    "",
    "Ingredients",
    "  Egg    2 pieces   at room temperature",
    "  Salt   to taste",
    "",
    "Steps",
    "  1. Boil the eggs for 8 minutes.",
]
assert run(folder.root, "show", "boiled-egg") == (0, boiled, [])
boiled_zh = [
    "Boiled egg",
    "份数：3（菜谱按 1 份写）",
    "",
    "食材",
    "  鸡蛋   6 个   at room temperature",
    "  盐     适量",
    "",
    "步骤（没有中文步骤，所以这里是英文步骤）",
    "  1. Boil the eggs for 8 minutes.",
]
assert run(folder.root, "show", "boiled-egg", "--servings", "3", "--lang", "zh") == (
    0,
    boiled_zh,
    [],
)

unknown = 'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.'
assert run(folder.root, "show", "mapo") == (1, [], [unknown])
unknown_zh = "没有 ID 为“mapo”的菜谱。运行“recipe-menu search mapo”查找它。"
assert run(folder.root, "show", "mapo", "--lang", "zh") == (1, [], [unknown_zh])
for wrong in ("Mapo", "../rice", "", "con", "tomato\u2010egg"):
    message = f'"{wrong}" is not a recipe ID. Run "recipe-menu list" to see the IDs.'
    assert run(folder.root, "show", wrong) == (2, [], [message])
not_an_id_zh = "“Mapo”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。"
assert run(folder.root, "show", "Mapo", "--lang", "zh") == (2, [], [not_an_id_zh])
for wrong in ("0", "101", "04", "+4", "4.0", " 4", "-1", "1_0", "\uff14", "\u0664", "9" * 5000):
    message = f'--servings must be a whole number from 1 to 100, not "{wrong}".'
    assert run(folder.root, "show", "tomato-egg", "--servings", wrong) == (2, [], [message])
zero = '--servings must be a whole number from 1 to 100, not "0".'
assert run(folder.root, "show", "Mapo", "--servings", "0") == (2, [], [zero])
assert run(folder.root, "show", "tomato-egg", "--servings", "100")[0] == 0
code, out, err = run(folder.root, "show")
assert (code, out) == (2, [])
assert err == [
    'An argument is missing. Write "recipe-menu show ID".',
    'Run "recipe-menu --help" to see the commands.',
]

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "show", "mapo-tofu") == (1, [], stopped)
assert run(folder.root, "show", "tomato-egg") == (0, TOMATO_EGG, [])

(folder.recipes / "Rice Bowl.toml").write_text("", encoding="utf-8")
code, out, err = run(folder.root, "show", "tomato-egg")
assert (code, out) == (1, [])
assert err[0] == str(Path("recipes", "Rice Bowl.toml"))
assert err[1].startswith("  This file name is not a recipe ID.")
assert err[2:] == ['Run "recipe-menu check" to see every problem.']
```

## 3. Changes to existing interfaces

None. No interface that F01 to F08 implemented changes. Each exported name keeps its signature and its behavior. F09 adds the module `browse`. It also adds two entries to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is internal to `cli` and which architecture 4 gives each command feature. With them, the help of the real `recipe-menu` lists `list` and `show` (choice 1). The tests that run the real `COMMANDS` check lines that the entries do not change: an unknown command, a line with no command, the first and last lines of the help (F05-T48 and F05-T49), the line of `check` and its column (F07-T17), and the line of `init` followed by the line of `check` (F08-T14). Every other test passes its own commands to `main`, or runs `init` and `check`. Option 1 of point A changes test data and one test, not an interface.

F09 uses these interfaces as their designs give them, and changes none of them:

- F01's `Quantity.scale`, `Quantity.to_text`, and `Quantity.is_to_taste`.
- F02's `BiText`, `Lang`, `Message`, `Plural`, `and_list`, `comma_list`, `display_width`, and `format_table`.
- F03's `DataFolder`, `Problem`, `Catalog`, `Catalog.find_tag`, and `read_catalog`.
- F04's `Recipe`, `RecipeIngredient`, `Steps`, `is_recipe_id`, `list_recipe_ids`, `read_recipe`, and `read_recipes`.
- F05's `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, and `stop_at_error` in `app`, `MIN_SERVINGS` and `MAX_SERVINGS` in `datafile`, and `COMMANDS` in `cli`.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `browse` is the command module that architecture 3 and 8 give `list` and `show`, in `src/recipe_menu/commands/browse/`, and it exports only `LIST_COMMAND` and `SHOW_COMMAND`. It imports `app`, `lang`, `units`, `text`, `datafile`, `catalog`, and `recipes`, which its row allows, and it needs none of `settings`, `menus`, `shopping`, and `check`. Its messages are in its own `messages.py`. `list` parses every recipe. `show` parses only the recipe that it names, after a listing that opens no file, as architecture 8 asks. Neither command writes a file (architecture 1). F09 adds no value type, and it uses `Recipe`, `Steps`, `Tag`, `Catalog`, `Quantity`, and `Context` as architecture 5.2 gives them. The two kinds of line that are not a `Message`, the names joined by two spaces and the numbered steps, hold only data, spaces, digits, and a period, which belong to no language (architecture 8). The Architect built a model of 2.1 to 2.4 on the code of the branch, with both commands in `COMMANDS`. With Python 3.13.18 on this Windows 11 PC, the four examples hold, every assertion and both `# raises` included. The nine commands of the F09 prototype give its lines and exit codes exactly, `show red-braised-pork` with the example file of option 1 of point A. The help has 17 lines in each language, and its second column starts after 18 columns (choice 1). In version 0.2, the six `python` blocks of each file give the same syntax trees as in version 0.1, and no name in the examples holds a line break, so the four examples hold as in round 1. |
| Follows the error handling and naming conventions | Pass | A reader's problems are values, and each command stops at the first error with `first_error` and `stop_at_error`, as architecture 6 asks of every command but `check`. The exit codes and the streams follow architecture 6 and requirements 3. Exit code 0 writes to stdout, also for an empty list (choice 6). Exit code 1 writes to stderr for an error in a file, an ID with no file, or a tag that the catalog lacks, as the prototype, v0.1-S10, and v0.1-S12 expect. Architecture 6 has no row of its own for a name on the command line that the data lacks. Exit code 1 for `--tag breakfast` follows its row for a missing recipe, so the architecture needs no change. Exit code 2 comes from a `UsageError` that `run` raises for a wrong value of `ID` or `--servings`, before it reads a file or writes any output (F05 design, section 2). `NOT_A_RECIPE_ID` and `SERVINGS_NOT_1_TO_100` say what to run or write, so they name no hint (ADR-0008). Every message is an UPPER_SNAKE `Message` or `Plural`, and the plurals and lists come from `text`. On the model, each of the 5 wrong IDs and the 11 wrong values of `--servings` in the example of 2.4 gives exit code 2 and one line. The value of 5,000 digits gives the message, not a `ValueError` (choices 7 to 9). `to_text` cannot reach F02's limit of 4,300 digits, because an amount from a file has at most 15 digits and the factor is at most 100. |
| Does not duplicate an existing interface | Pass | F09 calls `is_recipe_id`, `list_recipe_ids`, `read_recipe`, `read_recipes`, `Catalog.find_tag`, `first_error`, `stop_at_error`, `format_table`, `display_width`, `and_list`, `comma_list`, `Quantity.scale`, `Quantity.to_text`, `BiText.get`, `Steps.get`, `MIN_SERVINGS`, and `MAX_SERVINGS`, and it builds none of them again. No interface reads a whole number from the command line. `read_servings` checks a value that `tomllib` gave, so the rule of choice 8 for the text of `--servings` is new, and it stays internal to `browse`, its only user. `browse` may not import `check` (architecture 3), and the `RECIPE_COUNT` of each module has its own texts, so the two internal messages are not one interface twice. F09 exports only its two commands. F10's design decides what `search` shares with `browse`, which architecture 4 allows. |
| Depends only on features earlier in the order | Pass | F09 uses `units` from F01, `lang` and `text` from F01 and F02, `datafile` and `catalog` from F03, `recipes` from F04, and `app`, `cli`, `MIN_SERVINGS`, and `MAX_SERVINGS` from F05. All of them come before F09 and pass their tests on main. F05 is the hard dependency of the F09 row, and F01, F02, and F04 are its soft ones. F03 is not in the row, but it comes before F04, which reads the catalog through it. The hint of `UNKNOWN_ID` names F10's `search` only as text, which the approved prototype gives, and the design says what that command line gives until F10's mock. The plans for F10 bind no later design. F09 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | `browse` reaches the disk only through the readers of F03 and F04, writes only to `context.out` and `context.err`, and uses neither `context.settings` nor `context.today`. It gives `cli` only its two `Command` values. Choice 2 says that the error that stops a command is among the errors of `check`. That follows from the readers that both modules call with the same arguments, not from an import between them. The widths of choice 5 depend only on the recipes that `list` read. Since version 0.2, they measure each line of a cell, as rules 1 and 2 of `format_table` do (F02 design 2.9), so they change nothing without `--tag`. Choice 8 relies only on what F01 design 2.9 promises, a value equal to `TO_TASTE`, and not on which object `scale` gives. `show` compares the ID with the listing exactly, so it does not depend on how Windows matches the case of a file name (architecture 5.2). Point A changes test data, not a module. |
| Changes an implemented interface only through the change flow | Pass | Section 3 rightly says None. The model changes no module of F01 to F08, and the two entries in `COMMANDS` are the change that architecture 4 gives each command feature. With the model in place, the branch's tests give 433 passed and 3 skipped, which are the 436 tests that it collects, F05-T48, F05-T49, F07-T17, and F08-T14 included. So section 3's claim about those tests holds. Option 1 of point A changes test data and one test. With the prototype's four steps in the example file, F04-T38 is the only test that fails, and with its count at 4, every test passes again. The split into a mock and an implementation is right. The mock's 3 or 4 files fit R03. Its `run` functions write nothing, give 0, and raise nothing, so every test of the output, of exit code 1, or of a `UsageError` fails against it (R09). The design names the tests that pass against the mock, so the Test Manager can pair each with a check that fails. The implementation fits R03 in the internal files of `browse`, which the Developer may split into one file for each command. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked choices 1 to 10, points A to C, and the notes of the brief against the requirements, the architecture, the F05 and F09 prototypes, `example-data.md`, and v0.1-S10, v0.1-S12, v0.1-S20 to v0.1-S23, v0.1-S28, and v0.1-S29. The 828 lines of the two files match heading for heading, row for row, and item for item, and the 6 `python` blocks of each file equal those of its mirror. On the model, the examples, the prototype, and the branch's tests hold as items 1, 2, and 6 say. The Architect also timed the model on a PT01 folder from `tests/pt01_support.py`, with 5 runs of `python -m recipe_menu` for each command, in two rounds on this PC. The medians were 0.835 s and 0.843 s for `check`, 0.806 s and 0.803 s for `list`, 0.792 s and 0.807 s for `list --tag quick`, 0.165 s and 0.160 s for `show recipe-0500`, and 0.147 s and 0.144 s for `--version`. So choice 10's estimate holds, and no `[refactor]` PR comes first. `list` has about 0.2 s to spare, so its timed case keeps F07-T25's limit of 1 s on Windows. Three findings do not block. Finding 1: choice 5 and 2.2 take the `display_width` of a whole cell. A name can hold a line break, though, and `format_table` measures each line of a cell. On the model, a name with the lines `A long first line` and `end` makes the Name column 4 columns wider than `format_table` would, so "they change nothing" does not hold for it. The change asked: take the largest `display_width` of the lines of each cell, as rule 1 of `format_table` splits them. Finding 2: choice 8 says that `Quantity.scale` gives a value equal to `TO_TASTE`, "not the object itself". F01 design 2.9 gives `TO_TASTE`, and the code gives the quantity itself, which is `TO_TASTE` for a quantity that `parse_quantity` read. The change asked: say that F01 promises a value equal to `TO_TASTE`, so code tests it with `is_to_taste` or `==`. Finding 3: `ruff format` with the project's settings would change lines 385 and 396 of 2.2 and line 755 of 2.4. Two of them are wider than 100 columns, where a Chinese character counts as two, and one has escaped quotation marks. No test ran on the PR itself, because it changes no code. | Approved. The main session puts points A to C to Troy when Troy approves this design (R18). The Architect agrees with each recommendation. Under option 1 of point A, the example file and F04-T38 change in F09's test PR, PR 4, and the test plan names the change. Test data and a test of an accepted feature belong to the tests stage (R02, R08). F04-T38 then passes, as R10 asks of an accepted feature, and the new F09 tests still fail against the mock (R09). The Architect agrees with the new texts of point B. For point C, exit code 2 is what architecture 6 gives a wrong argument value. The note of the F03 review asked only that `show` never pass such a value to `DataFolder.recipe_file`, and choice 7 keeps that. The Interface Designer can take findings 1 to 3 into this PR before Troy approves it. If not, the test plan follows the rule of finding 1. |
| 2 | No blocking issue. The Architect compared version 0.2 with version 0.1 in both files. They differ only in choice 5, the `widths` sentence of 2.2, choice 8, three lines of the examples of 2.2 and 2.4, the version, and a row of the change log, and section 4 was as round 1 left it. Finding 1 is resolved: each width of `min_widths` is the largest `display_width` of a line of a cell, split as rule 1 of `format_table` splits it, with `cell.splitlines()` (F02 design 2.9). The Architect checked the rule with F02's `format_table` on four recipes, one with the name lines `A long first line` and `end`. With these widths, the full table does not change, and each table of one of those recipes keeps the columns of the full table. The widths of version 0.1 made the full table wider. Finding 2 is resolved: choice 8 now says what F01 design 2.9 promises, and that design's example tests `TO_TASTE.scale(Fraction(2)) == TO_TASTE`. Finding 3 is resolved: the six `python` blocks of each file give the same syntax trees as in version 0.1, so no example changes its meaning, and the blocks of the two files are still equal. `ruff format --check` passes on both files and on the 238 files that it checks in the repository, and both CI jobs of the PR pass. With this row, the two files have 838 lines each and still match heading for heading, row for row, and item for item. | Approved. Every item passes. Points A to C still go to Troy when Troy approves this design (R18), and the notes of round 1 on them still hold. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-13 | First draft. |
| 0.2 | 2026-11-13 | Takes the three findings of round 1 of the Architect review. Choice 5 and 2.2 take each width of `min_widths` from the lines of the cells, split as rule 1 of `format_table` splits them, so the widths change nothing without `--tag`, also for a name with a line break. Choice 8 says that F01 promises only that `Quantity.scale` gives a value equal to `TO_TASTE`, so code tests it with `is_to_taste` or `==`, never `is`. Three lines of the examples of 2.2 and 2.4 are written as `ruff format` writes them: two are wrapped, and one takes single quotes. No example changes its meaning. |
| 1.0 | 2026-11-13 | Approved by Troy. |
