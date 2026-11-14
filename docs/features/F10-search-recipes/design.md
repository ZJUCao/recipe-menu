---
troy-doc: "F10-design"
lang: "en"
version: "1.0"
updated: "2026-11-13"
status: "Approved by Troy on 2026-11-13"
mirror: "design.zh-CN.md"
---

# F10 Search recipes: interface design

## 1. Feature

- ID and name: F10 Search recipes
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F03, F04, F09

## 2. Interfaces

F10 builds the command module `search` in `src/recipe_menu/commands/search/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.search` exports one name, `SEARCH_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu search` (2.2). Its messages live in `src/recipe_menu/commands/search/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F10 adds the command to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `SHOW_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). F10 also has `catalog` export its matching form as `matching_form`, so that `search` compares a word with a name by F03's case rule (section 3.1). The F10 prototype `docs/prototypes/F10-search.md` shows the command, and the F05 prototype shows its line in the help.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F10 gives |
| --- | --- |
| `recipe-menu search WORD...` lists the recipes that match every word. | `recipe-menu search` (2.2), with the argument `WORD` of `SEARCH_COMMAND` (2.1), which takes one or more words. A recipe matches when each word appears in at least one of its places (choice 4). |
| A word matches in a recipe name, an ingredient name, or a tag name, in either language. | The three places of choice 3: the recipe's names, the catalog's names of its ingredients, and the catalog's names of its tags, each in both languages. |
| A match in English ignores case. | F03's matching form, which `catalog` exports as `matching_form` (choice 4, section 3.1). |
| Each result says where it matched. | The column `Matched in` (choice 5). |
| `search` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus (PT01, [requirements 7.1](../../requirements.md#71-performance-targets)). | The performance target of 2.2, and choice 10. |

These rules hold for every interface below:

- `search` imports only `app`, `lang`, `text`, `datafile`, `catalog`, and `recipes` from the package. Its row of architecture 3 allows them. It needs neither `units`, `settings`, `menus`, `shopping`, nor `browse` (choice 2, [architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `search` reaches the disk only through the readers of F03 and F04, which read through `datafile` (architecture 8). It writes no file ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 1](../../architecture.md#1-context-and-constraints)). It writes only to `context.out` and `context.err`. It reads nothing of the outside world itself, and it keeps no state. What it builds to match the words, such as the matching forms of the catalog's names, lives for one run only, so no module keeps a cache (architecture 8).
- `search` uses neither `context.settings` nor `context.today`.
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). `search` stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). `run` raises a `UsageError` only for an empty word, before it reads a file or writes any output (F05 design, section 2). Any other exception that reaches `cli` is a bug.
- `SEARCH_COMMAND` is a frozen `Command` value (F05 design 2.5). F10 adds no value type.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- `recipe-menu search` has the performance target PT01 (choice 10). It reads each file that it needs once, and writes its output once, after the last file. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 gives their rules.

1. **One command in its own module, after `show` in the help.** Architecture 3 gives the command its own module, `search`. F10 adds `SEARCH_COMMAND` to `COMMANDS` after `SHOW_COMMAND`, so `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND)`, in the help's order of F05 design section 2. `search` has `FolderUse.READ`, so `cli` stops it when the data folder is missing or the settings have an error (F05 design 2.5). It declares the argument `WORD` with `repeats=True`, as F05's design planned. So the argument is required, `cli` reports a search with no word, and the help writes `search WORD...` and `search 词...` (F05 design 2.5). `search` declares no option. With these five commands, the widest first cell of the help is `search WORD...`, of 14 columns, one more than `--data FOLDER` and `--data 文件夹`. So the second column of both tables starts after 19 columns in both languages, not after 18 as after F09. Every line of the two tables keeps its text and moves one column to the right, and the help has 18 lines. 2.1 gives the tables. With the eight commands of v0.1, the widest first cell is `menu show [WEEK]`, of 16 columns, and the help still gives the two outputs of the F05 prototype. Section 3 lists the tests of the real help, which all stay true.
2. **Nothing shared with `browse`.** Architecture 4 lets `search` import `browse`, and F09's design left the choice to F10. `search` imports nothing from `browse`, and `browse` keeps its two exports. The two commands have little in common. The ID cell is `recipe.id`, and the name cell is `recipe.name.get(context.lang)`, each one expression on interfaces of F04 and F02. The widths of F09 choice 5 do not apply to `search` (choice 7). The headings `ID` and `Name` are two messages, and architecture 8 keeps each module's messages in its own `messages.py`. So `search` defines its own `ID_HEADING` and `NAME_HEADING`, with the texts of `browse`, which the F10 prototype shows. Exporting them from `browse` would add two names to F09's interface for two short texts. The cost is that a change to one of these headings must be made in both modules.
3. **Where a word can appear.** A recipe has the three places of the requirement, and each place holds texts in both languages:
   - Name: `recipe.name.en` and `recipe.name.zh`. A name that lacks one language has only the other text here. The fallback of `BiText.get` would give that same text again, so it would change no result.
   - Ingredient: both names of the catalog's `Ingredient` on each ingredient line, `line.ingredient.name.en` and `line.ingredient.name.zh`. A recipe file names an ingredient in either language, such as `item = "鸡蛋"`, and F04 finds it with `Catalog.find_ingredient` (F04 design 2.6). So each line refers to the catalog's own ingredient, which always has both names (F03 design 2.4), and `search egg` finds a recipe whose file writes `鸡蛋`. The text that the file writes after `item` adds nothing, because its matching form equals the matching form of one of the two names.
   - Tag: both names of each `Tag` of `recipe.tags`, which also come from the catalog.

   Nothing else counts, as the requirement says: no note, step, ID, servings, quantity, unit, or category of an ingredient. So `search wedges` and `search 切块` find no note, `search scramble` finds no step, and `search dairy` finds no category, such as `Eggs, dairy, and tofu`. Because the ID does not count, F09's hint `Run "recipe-menu search mapo" to find it.` finds `mapo-tofu` by its English name `Mapo tofu` (2.2). For a typo such as `show tomato-eggs`, the hint's search finds nothing, because no name holds `tomato-eggs`.
4. **How a word is compared.** A word appears in a text when `matching_form(word)` is part of `matching_form(text)`, as Python's `in` tests it. `matching_form` is F03's matching form (F03 design 2.6), which `catalog` exports for F10 (section 3.1). So `search` has the case rule of `find_ingredient` and `find_tag`, and no module holds a second one, as the Architect asked in the F03 review. These rules follow for a word:
   - A word can be part of a longer name, as the prototype shows with `番茄` in `番茄炒蛋` and `TOMATO` in `Tomato and egg stir-fry`. Chinese writes no spaces between words, so a search for `番茄` must look inside `番茄炒蛋`, and English follows the same rule. So `search egg` also finds a recipe with `Eggplant`, and `search pork` finds `Pork belly` and `Minced pork`.
   - Case counts only for the letters A to Z, so `TOMATO`, `tomato`, and `Tomato` find the same recipes. The rule changes A to Z in a text of either language, and Chinese characters compare exactly.
   - Whitespace at both ends of a word does not count, as `str.strip()` removes it, U+3000 IDEOGRAPHIC SPACE included. So `search "\u3000番茄"` finds what `search 番茄` finds. U+200B ZERO WIDTH SPACE is not whitespace (F03 design 2.6, rule 1), so `"\u200b"` is a word of one character, which no name in the example folder holds.
   - Whitespace inside a word counts as written. `search "and egg"` finds the two recipes whose names hold `and egg`, and `search "tomato\u00a0and"`, with U+00A0 NO-BREAK SPACE, finds none.
   - Look-alike letters stay as they are, and no text is normalized. `search "\uff34omato"`, with U+FF34 FULLWIDTH LATIN CAPITAL LETTER T, finds nothing.
   - A word whose matching form is empty, such as `""`, `" "`, or `"\u3000"`, is a wrong value on the command line. Every text holds the empty text, so such a word would otherwise match every recipe. `run` checks every word before it reads a file, and raises `UsageError(EMPTY_WORD, None)` for the first such word, and `cli` exits with 2 (architecture 6, F05 design 2.7). The message says what to write, so it names no hint (ADR-0008). Troy decides this choice (point B below).
   - A recipe matches when every word appears in at least one of its places. Two words may appear in different places, such as `葱` in an ingredient and `quick` in a tag. The order of the words changes neither the recipes nor their places.
   - A word that comes twice, as in `search egg egg`, finds what it finds once (choice 6).
   - A word that starts with `--` is an option for `cli` (F05 design 2.10), so `search` cannot look for it. A word that starts with one `-`, such as `-x`, is a word.
5. **Where each result matched.** The last column, `Matched in` and `匹配于`, names each place where at least one word appears, in the order name, ingredient, tag, and each place once. So the places of several words combine. In `search 葱 quick`, `葱` appears in an ingredient and `quick` in a tag, so the cell is `食材、标签`, as the prototype shows. A word that appears in two places, such as `番茄` in the name and in an ingredient, gives both. The cell is `comma_list` of the places' messages, as F02 design 2.6 plans for a short list in a cell: `name, ingredient` and `食材、标签`.
6. **The line under the table.** It counts the recipes and repeats the words. `{words}` is `and_list` of the words, each in quotation marks with `QUOTED_WORD`: `"葱" and "quick"` and `“葱”和“quick”`, as F02 design 2.6 shows. Each word is written as you typed it, so `TOMATO` stays in capitals and `" tomato "` keeps its spaces. A word that equals an earlier word exactly is left out of the list. So `search egg egg` writes `"egg"` once, and `search egg EGG` writes both. A word is shown with no escape: a `"` in it shows as `"`, and a line break in it breaks the line. The prototype's Chinese line says 同时 (at the same time) for two words, which reads wrong for one word. So the line has one message for one word and one for two or more words, counted after the repeated words are left out, and each message is a `Plural` picked by the number of recipes. The English texts of the two messages are the same, because `and_list` already names every word. When no recipe matches, `search` writes only the line `NO_RECIPE_MATCHES` or `NO_RECIPE_MATCHES_ALL`, with no table, and exits with 0. No match is not an error, as the prototype "No match" says. Troy decides the texts that no prototype shows (point A below).
7. **The column widths come from the rows of the result.** `search` passes `format_table` no `min_widths`, so each column is as wide as its own cells (F02 design 2.9). In the example folder, the widths of the whole folder would give the same tables for the prototype's searches, because the matched rows hold the longest ID `tomato-egg-noodles` and the longest names `Tomato and egg stir-fry` and `番茄鸡蛋面`. So the prototype and v0.1-S11 hold either way. F09 choice 5 gives `list --tag` the widths of the whole list, because the F05 and F09 prototypes show a list with a tag as the whole list with fewer rows. A search has no such table to line up with: its last column is another column, and each search asks a new question. So the table of a narrow result stays narrow, as for `search mapo` in 2.2, and `search` measures no recipe that it does not show.
8. **What `search` reads, and where it stops.** `search` reads only the files that it needs (architecture 8), in the order of the steps of `check` (F07 design 2.2): the catalog, then every recipe with `read_recipes`. It does not also call `list_recipe_ids`, because `read_recipes` returns the problems of the listing before those of the files (F04 design 2.7). So `search` reports each problem of the listing once, as `list` does. It reads neither the pantry nor a menu. It stops at the first error of each reader with `stop_at_error`, which writes the problem and `RUN_CHECK` and gives 1 (architecture 6). It parses every recipe before it matches one, so an error in any recipe file stops it, also when that recipe would not match, as an error stops `list`. `check` reads the same files with the same readers and the same arguments, so the error that stopped `search` is among the errors of `check` (F07 design, choice 8). `search` writes no warning, and a warning never changes the exit code, as for F09 choice 3 (architecture 6). The rows come in the order of `read_recipes`, which is the order of the IDs, as in `list` (F04 design 2.5). A `recipes/` folder with no recipe file gives no match, so `search` writes the line of choice 6 and exits with 0. A missing `recipes/` folder is an error of the listing (F04 design, choice 6), so it stops `search` with exit code 1. `cli` checks the number of words, the data folder, and the settings before it runs `search` (F05 design 2.10). So `search ""` with a missing data folder gives `NO_DATA_FOLDER` and exit code 1, as `show Mapo` does.
9. **Numbers in messages.** The messages of `search` show only the number of recipes that match, which is the length of a tuple, and the words, which are text from the command line. A word of 5,000 digits is a `str`, so it never meets F02's limit of 4,300 digits (F02 design 2.3). A problem in a file reaches the error stream only through `stop_at_error`, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `search` meets that limit.
10. **Speed.** PT01 asks that `search` with 1,000 recipes finish within 1 second on Troy's PC, the median of 5 runs (v0.1-S30). The case looks for the name of the ingredient that every recipe uses, so `search` prints all 1,000 recipes. In the PT01 folder of `tests/pt01_support.py`, that is `search 食材001`, and every row is matched in `ingredient`. `search` reads what `list` reads: the settings in `cli`, the catalog, one listing of `recipes/`, and each recipe file once. F09's PT01 baseline on Troy's PC is a median of 0.789 s for `list` and 0.153 s for `show`. To the reading, `search` adds the matching and a smaller table:
    - The matching forms of the catalog's 600 ingredient names and 10 tag names are built once per run, and each word is looked for in each of them once. So for each word, `search` knows which ingredients and tags of the catalog hold it before it looks at a recipe. A recipe's lines and tags refer to those same catalog values (architecture 5.2), so they need no new matching form: each of a recipe's 12 lines and 2 tags is one lookup. Each recipe's 2 names get their matching forms once. For one word, a run makes about 2,600 matching forms, 2,600 tests with `in`, and 14,000 lookups, which take a few hundredths of a second at most.
    - The table holds about 32,000 characters, each measured twice with `display_width` inside `format_table`. The table of `list` holds about 40,000, each measured three times. No `Message.render` runs for a row: the messages of the places are rendered once per run, and each cell is `comma_list` of them.

    So `search` should take about as long as `list`. This is an estimate from those times, not a measurement. F10 needs no `[refactor]` side PR before its mock. The test plan can time `search` on a PT01 folder, as F09-T28 times `list`. If `search` comes close to the limit, the first step is the change that the Code Reviewer named on PR #50: `Message.render` parses its template's placeholders on every call, which costs about 0.06 s on a PT01 folder. That change would land as a `[refactor]` PR before F10's implementation PR, and the Architect decides whether it changes F02's interface.

Troy decides these two points. The design follows the recommendation of each.

- **A. New texts.** No prototype shows these texts. Each follows the wording of a text that a prototype shows. The recommendation is to accept them as 2.2 gives them.
  - The English line for two or more words, with `and_list`: `2 recipes match "葱" and "quick".`, `No recipe matches "豆腐" and "quick".`, and `1 recipe matches "scallion", "QUICK", and "noodle".`. It reads as the prototype's line for one word. A form with "both" or "all of" would need a third message for three or more words.
  - The Chinese line for one word, without 同时: `2 个菜谱匹配“番茄”。` and `没有菜谱匹配“lamb”。`.
  - The line for one recipe: `1 recipe matches "mapo".` and `1 个菜谱匹配“mapo”。`.
  - The Chinese line for three words: `1 个菜谱同时匹配“葱”、“quick”和“面”。`.
  - The place `tag` in English and the place `名称` in Chinese. The prototype shows `name`, `ingredient`, `食材`, and `标签`.
  - `EMPTY_WORD`: `A word is empty. Look for a name, such as "recipe-menu search tomato".` and `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。`.
- **B. A word with nothing in it** (choice 4).
  - Option 1, recommended: a usage error with exit code 2, `EMPTY_WORD`, before `search` reads a file.
  - Option 2: no match with exit code 0, such as `No recipe matches "".`. F03 design 2.6, rule 7, says that a text whose matching form is empty matches nothing.
  - The reason for option 1: requirements 3 give exit code 2 to a wrong command line, and the tool already treats empty text on the command line as a mistake. `cli` treats an empty value of an option as no value (F05 design 2.10), and `show ""` is a usage error (F09 choice 7). Under option 2, `search ""` would report that no recipe matches, which hides the typing mistake.

No later feature builds on F10. The hint of F09's `UNKNOWN_ID` runs `recipe-menu search`, which runs from F10's mock PR on and gives the output of 2.2 from F10's implementation PR on.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/search/__init__.py` and `messages.py`, maybe one internal file, the entry in `src/recipe_menu/cli/_commands.py`, and the export of `matching_form` in `src/recipe_menu/catalog/__init__.py` (section 3.1), so it changes at most 5 files. It defines every message and the command with all its fields, so the help lists `search` and the command runs. Its `run` reads no file and raises nothing. For example, it writes nothing and gives 0. So a new test of the output, of exit code 1, or of `EMPTY_WORD` with exit code 2 fails against the mock (R09). These tests pass against the mock and break R09: a test that checks only the fields of `SEARCH_COMMAND`, the help, a message, or exit code 0. So does a test that checks only that `search` changes no file, as v0.1-S23 does for `search 番茄`, or a test of what `cli` does before it runs the command, such as a missing data folder, broken settings, `search` with no word, `search --tag quick`, or `search 番茄 --help`. A test of `matching_form` on its own passes too, because the mock exports F03's working function, so F10's tests reach it through `search`. The implementation (PR 5) reads the files, matches the words, and writes the output in the internal files of `search`, and it fits R03's 5 files.

### 2.1 `SEARCH_COMMAND`

- Module: search
- Purpose: The description of the `search` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` writes the result of 2.2.

Signature:

```python
SEARCH_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("search",)
#   help_line = SEARCH_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WORD_ARGUMENT, repeats=True)
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("search",)`. | None |
| `help_line` | `Message` | `SEARCH_HELP`: "Find recipes by name, ingredient, or tag." and "按名称、食材或标签找菜谱。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Checks the words, reads the catalog and every recipe, and writes the result of 2.2. | Gives 0 or 1. Raises `UsageError` for an empty word, before it reads a file or writes any output. Raises nothing for bad data. |
| `argument` | `Argument` | `Argument(WORD_ARGUMENT, repeats=True)`, which is required and repeats. `WORD_ARGUMENT` is `WORD` and `词`, the names in the F05 prototype's help. | So `cli` passes one or more values (F05 design 2.5). |
| `options` | A tuple of `str` | `()`. `search` has no option of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `search` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.out`, and `context.err`. It uses neither `context.settings` nor `context.today`. |
| `arguments` | `Arguments` | What the command line gives `search` (F05 design 2.6). | `arguments.values` holds the words in the order of the command line, such as `("葱", "quick")`. It has no options. |

- Return value: `SEARCH_COMMAND`, a `Command`.
  - `SEARCH_COMMAND.usage` is `search WORD...` in English and `search 词...` in Chinese, so the help shows them, and a usage error quotes `recipe-menu search WORD...` or `recipe-menu search 词...`.
  - `SEARCH_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its output in `context.lang`, and gives 0 or 1.

After F10, the help lists these commands and options, with the second column after 19 columns (choice 1). In English:

```text
Commands:
  init             Create the data folder with example data.
  check            Check every data file for mistakes.
  list             List the recipes.
  show ID          Show one recipe.
  search WORD...   Find recipes by name, ingredient, or tag.

Options:
  --lang en|zh     The language of the output. Default: the settings, else English.
  --data FOLDER    The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version        Show the version.
  --help           Show this help.
```

In Chinese:

```text
命令：
  init             创建数据文件夹和示例数据。
  check            检查每个数据文件有没有错误。
  list             列出菜谱。
  show ID          查看一个菜谱。
  search 词...     按名称、食材或标签找菜谱。

选项：
  --lang en|zh     输出语言。默认：设置里的语言，否则英文。
  --data 文件夹    数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version        显示版本。
  --help           显示这份帮助。
```

Errors:

`run` checks the words before it reads a file.

| Error | When |
| --- | --- |
| `UsageError(EMPTY_WORD, None)` | `matching_form(word)` is empty for a word of `arguments.values` (choice 4). |

- Side effects: Those of 2.2. `run` reads the catalog and the recipe files through the readers of F03 and F04, writes to `context.out` or `context.err`, and writes no file.
- Performance target: None. PT01 times `recipe-menu search` (2.2) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context holds the default settings, and the output follows `context.lang`. The help comes from `COMMANDS`, which holds `init`, `check`, `list`, `show`, and `search` after F10. The call that raises writes no line to either stream.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.search import SEARCH_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SEARCH_COMMAND.words == ("search",)
assert SEARCH_COMMAND.usage == BiText("search WORD...", "search 词...")
assert SEARCH_COMMAND.help_line.render(Lang.EN) == "Find recipes by name, ingredient, or tag."
assert SEARCH_COMMAND.help_line.render(Lang.ZH) == "按名称、食材或标签找菜谱。"
assert SEARCH_COMMAND.argument == Argument(Message("WORD", "词"), repeats=True)
assert SEARCH_COMMAND.options == ()
assert SEARCH_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.ZH, folder, Settings(), out, err, date(2026, 11, 10))
assert SEARCH_COMMAND.run(context, Arguments(("葱", "quick"))) == 0
assert out.getvalue().splitlines() == [
    "ID                   名称         匹配于",
    "tomato-egg           番茄炒蛋     食材、标签",
    "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
    "",
    "2 个菜谱同时匹配“葱”和“quick”。",
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
assert len(english) == 18
assert english[4:10] == [
    "Commands:",
    "  init             Create the data folder with example data.",
    "  check            Check every data file for mistakes.",
    "  list             List the recipes.",
    "  show ID          Show one recipe.",
    "  search WORD...   Find recipes by name, ingredient, or tag.",
]
assert english[12].startswith("  --lang en|zh     The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[9] == "  search 词...     按名称、食材或标签找菜谱。"
assert chinese[13].startswith("  --data 文件夹    数据文件夹。")

SEARCH_COMMAND.run(context, Arguments(("番茄", "\u3000")))  # raises UsageError
```

### 2.2 `recipe-menu search`

- Module: search
- Purpose: The command that finds recipes ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 2, and [4](../../requirements.md#4-features)). It lists the recipes that match every word in a recipe name, an ingredient name, or a tag name, in either language, and says where each one matched. The F10 prototype shows it.

Signature:

```text
recipe-menu search WORD... [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `WORD` | A text | A word to look for, such as `番茄`, `TOMATO`, or `quick`. | One or more words (F05 design 2.5). The matching form of each word is not empty (choice 4). A word that starts with `--` is an option (F05 design 2.10). |
| `--lang` | `en` or `zh` | The language of the output and of every message. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `search`. | None |

`search` takes these steps, in order. Step 1 reads no file, and each step that reads a file uses what the earlier steps gave.

1. It checks the words in order, and raises `UsageError(EMPTY_WORD, None)` for the first word whose `matching_form` is empty.
2. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `search` gives `stop_at_error(context, error)` for the first one.
3. `read_recipes(context.folder, catalog)` gives `recipes` and their problems (F04 design 2.7). With an error among the problems, `search` stops at the first one with `stop_at_error`.
4. For each recipe of `recipes`, in their order, `search` finds the places of each word by the table below. It keeps the recipe when every word has at least one place.
5. It writes the output below to the output stream and gives 0.

The warnings of steps 2 and 3 change nothing (choice 8).

A word appears in a text when `matching_form(word) in matching_form(text)` is true (choice 4). The places of a word in a recipe are these, in this order:

| Place | Message | The word appears in one of these texts |
| --- | --- | --- |
| Name | `NAME_PLACE` | `recipe.name.en` and `recipe.name.zh`, each when it is not `None`. |
| Ingredient | `INGREDIENT_PLACE` | `line.ingredient.name.en` and `line.ingredient.name.zh`, for each `line` of `recipe.ingredients`. |
| Tag | `TAG_PLACE` | `tag.name.en` and `tag.name.zh`, for each `tag` of `recipe.tags`. |

The words of the count line are the words of the command line in their order, without each word that equals an earlier word exactly (choice 6). "One word" and "two or more words" below count those words.

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `search` wrote its result, also when no recipe matches. | The output stream: the table and the count line, or one line when no recipe matches. |
| 1 | A file has an error. | The error stream: the three lines of `stop_at_error`. Nothing goes to the output stream. |
| 2 | A word is empty. | The error stream: the message, which `cli` writes, with no hint. Nothing goes to the output stream. |

When one or more recipes match, the output is these lines, in this order, each ended by a line break:

1. The lines of `format_table(rows)`, with no indent, the default gap of 3, and no `min_widths` (F02 design 2.9, choice 7).
2. An empty line.
3. The count line: `RECIPES_MATCH` for one word, and `RECIPES_MATCH_ALL` for two or more words, each picked by the number of recipes that match.

`rows` is the heading row, and then one row for each recipe that matches:

| Column | Heading | Cell |
| --- | --- | --- |
| ID | `ID_HEADING` | `recipe.id` |
| Name | `NAME_HEADING` | `recipe.name.get(context.lang)` |
| Matched in | `MATCHED_IN_HEADING` | `comma_list` of the messages of the recipe's places, each as its `BiText`, in the order of the table of places, then `.get(context.lang)`: `name, ingredient` and `食材、标签` (choice 5). |

`search` writes each name as the file holds it, so the rules of `format_table` apply to it, such as a name with a line break, which takes two lines.

When no recipe matches, the output is one line: `NO_RECIPE_MATCHES` for one word, and `NO_RECIPE_MATCHES_ALL` for two or more words (choice 6).

The messages of `search` are these. `RECIPES_MATCH` and `RECIPES_MATCH_ALL` are `Plural` values (F02 design 2.4), picked by `count`. `NAME_PLACE`, `INGREDIENT_PLACE`, and `TAG_PLACE` are rendered once per run with `to_bitext` (choice 10).

| Name | English | Chinese |
| --- | --- | --- |
| `SEARCH_HELP` | `Find recipes by name, ingredient, or tag.` | `按名称、食材或标签找菜谱。` |
| `WORD_ARGUMENT` | `WORD` | `词` |
| `ID_HEADING` | `ID` | `ID` |
| `NAME_HEADING` | `Name` | `名称` |
| `MATCHED_IN_HEADING` | `Matched in` | `匹配于` |
| `NAME_PLACE` | `name` | `名称` |
| `INGREDIENT_PLACE` | `ingredient` | `食材` |
| `TAG_PLACE` | `tag` | `标签` |
| `QUOTED_WORD` | `"{word}"` | `“{word}”` |
| `RECIPES_MATCH`, for one | `{count} recipe matches {words}.` | `{count} 个菜谱匹配{words}。` |
| `RECIPES_MATCH`, for more | `{count} recipes match {words}.` | `{count} 个菜谱匹配{words}。` |
| `RECIPES_MATCH_ALL`, for one | `{count} recipe matches {words}.` | `{count} 个菜谱同时匹配{words}。` |
| `RECIPES_MATCH_ALL`, for more | `{count} recipes match {words}.` | `{count} 个菜谱同时匹配{words}。` |
| `NO_RECIPE_MATCHES` | `No recipe matches {words}.` | `没有菜谱匹配{words}。` |
| `NO_RECIPE_MATCHES_ALL` | `No recipe matches {words}.` | `没有菜谱同时匹配{words}。` |
| `EMPTY_WORD` | `A word is empty. Look for a name, such as "recipe-menu search tomato".` | `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `count` | The number of recipes that match, the length of a tuple (choice 9). |
| `words` | `and_list` of `QUOTED_WORD.to_bitext(word=word)` for each word of the count line, in order: `"葱" and "quick"` and `“葱”和“quick”`. |
| `word` | One word, as you typed it. |

With these rules, the lines of the F10 prototype follow: for example, `2 recipes match "TOMATO".` and `没有菜谱同时匹配“豆腐”和“quick”。`.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `search` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `EMPTY_WORD` and no hint: `A word is empty. Look for a name, such as "recipe-menu search tomato".` | The matching form of a word is empty (step 1). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream | The catalog, the listing of `recipes/`, or a recipe file has an error (steps 2 and 3). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `search` has `FolderUse.READ`. |
| Exit code 2, with `TOO_FEW_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `An argument is missing. Write "recipe-menu search WORD...".` | The line names no word. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"search" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. Nothing more is written (F05 design 2.10). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `search` then reads `catalog.toml` once, lists `recipes/` once, and reads each recipe file once, all through the readers of F03 and F04. After an empty word, it reads no file. It reads neither `pantry.toml` nor a menu. It writes to the output stream or the error stream. It writes no file, so every file and folder keeps its bytes and modification time (v0.1-S23).
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. The first five runs give the five outputs of the F10 prototype, as v0.1-S11 runs them. The later runs show the rules of choices 3 to 8. A mistake in `mapo-tofu` stops `search`, and a folder with no recipe file gives one line.

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


TOMATO = [
    "ID                   Name                      Matched in",
    "tomato-egg           Tomato and egg stir-fry   name, ingredient",
    "tomato-egg-noodles   Tomato and egg noodles    name, ingredient",
    "",
]
assert run(folder.root, "search", "番茄") == (0, [*TOMATO, '2 recipes match "番茄".'], [])
assert run(folder.root, "search", "TOMATO") == (0, [*TOMATO, '2 recipes match "TOMATO".'], [])
assert run(folder.root, "search", "葱", "quick", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg           番茄炒蛋     食材、标签",
        "tomato-egg-noodles   番茄鸡蛋面   食材、标签",
        "",
        "2 个菜谱同时匹配“葱”和“quick”。",
    ],
    [],
)
assert run(folder.root, "search", "lamb") == (0, ['No recipe matches "lamb".'], [])
assert run(folder.root, "search", "豆腐", "quick", "--lang", "zh") == (
    0,
    ["没有菜谱同时匹配“豆腐”和“quick”。"],
    [],
)

assert run(folder.root, "search", "番茄", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg           番茄炒蛋     名称、食材",
        "tomato-egg-noodles   番茄鸡蛋面   名称、食材",
        "",
        "2 个菜谱匹配“番茄”。",
    ],
    [],
)
assert run(folder.root, "search", "mapo") == (
    0,
    [
        "ID          Name        Matched in",
        "mapo-tofu   Mapo tofu   name",
        "",
        '1 recipe matches "mapo".',
    ],
    [],
)
assert run(folder.root, "search", "pork") == (
    0,
    [
        "ID                 Name                     Matched in",
        "mapo-tofu          Mapo tofu                ingredient",
        "red-braised-pork   Red-braised pork belly   name, ingredient",
        "",
        '2 recipes match "pork".',
    ],
    [],
)
assert run(folder.root, "search", "and egg") == (
    0,
    [
        TOMATO[0],
        "tomato-egg           Tomato and egg stir-fry   name",
        "tomato-egg-noodles   Tomato and egg noodles    name",
        "",
        '2 recipes match "and egg".',
    ],
    [],
)
assert run(folder.root, "search", "scallion", "QUICK", "noodle") == (
    0,
    [
        "ID                   Name                     Matched in",
        "tomato-egg-noodles   Tomato and egg noodles   name, ingredient, tag",
        "",
        '1 recipe matches "scallion", "QUICK", and "noodle".',
    ],
    [],
)
assert run(folder.root, "search", "葱", "quick", "面", "--lang", "zh") == (
    0,
    [
        "ID                   名称         匹配于",
        "tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签",
        "",
        "1 个菜谱同时匹配“葱”、“quick”和“面”。",
    ],
    [],
)
assert run(folder.root, "search", "egg", "egg") == (0, [*TOMATO, '2 recipes match "egg".'], [])
both = [*TOMATO, '2 recipes match "egg" and "EGG".']
assert run(folder.root, "search", "egg", "EGG") == (0, both, [])
spaced = [*TOMATO, '2 recipes match "\u3000番茄".']
assert run(folder.root, "search", "\u3000番茄") == (0, spaced, [])

# A note, a step, a category, and an ID do not count.
for word in ("wedges", "切块", "scramble", "dairy", "tomato-egg"):
    assert run(folder.root, "search", word) == (0, [f'No recipe matches "{word}".'], [])
# A fullwidth letter and a no-break space inside a word count as written.
for word in ("\uff34omato", "tomato\u00a0and"):
    assert run(folder.root, "search", word) == (0, [f'No recipe matches "{word}".'], [])

empty = ['A word is empty. Look for a name, such as "recipe-menu search tomato".']
for words in ([""], ["番茄", "\u3000"], [" ", "lamb"]):
    assert run(folder.root, "search", *words) == (2, [], empty)
empty_zh = ["有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。"]
assert run(folder.root, "search", "", "--lang", "zh") == (2, [], empty_zh)
code, out, err = run(folder.root, "search")
assert (code, out) == (2, [])
assert err == [
    'An argument is missing. Write "recipe-menu search WORD...".',
    'Run "recipe-menu --help" to see the commands.',
]
code, out, err = run(folder.root, "search", "番茄", "--tag", "quick")
assert (code, out) == (2, [])
assert err == [
    '"search" has no option "--tag". It has no options of its own.',
    'Run "recipe-menu --help" to see the options.',
]

mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
stopped = [
    f"{Path('recipes', 'mapo-tofu.toml')}, ingredient 3",
    '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    'Run "recipe-menu check" to see every problem.',
]
assert run(folder.root, "search", "番茄") == (1, [], stopped)
assert run(folder.root, "search", "") == (2, [], empty)

for path in folder.recipes.iterdir():
    path.unlink()
assert run(folder.root, "search", "番茄") == (0, ['No recipe matches "番茄".'], [])
```

## 3. Changes to existing interfaces

F10 adds one name to the interface of F03's `catalog` (3.1). The name is the function that `catalog` already uses, so nothing that F03 implemented changes its signature or its behavior, and the tests of F03 pass unchanged. No interface of F01, F02, F04, F05, or F09 changes. `browse` keeps its two exports (choice 2). The requirements do not change, so no `[docs]` PR approves this change. The Architect reviews it in this design, as F04 and F05 added names to `datafile` in their section 3.

F10 also adds one entry to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is internal to `cli` and which architecture 4 gives each command feature. With it, the help of the real `recipe-menu` lists `search`, and the second column of its tables starts after 19 columns instead of 18 (choice 1). The tests that run the real `COMMANDS` check only lines and columns that stay true:

- F05-T48 checks the first and the last line of the Chinese help, and F05-T49 checks no line of the help.
- F07-T17 checks that the line of `check` ends with its text, and that the text starts at the column where the text of `--lang en|zh` starts.
- F08-T14 checks the same of the line of `init`, and that the line of `check` follows it.
- F09-T01 checks that the lines of `list` and `show` follow the line of `check`, and that their texts start at that same column. F09-T19 and F09-T25 check that `list --help` and `show ... --help` give the same help as `--help`.

Each of these holds when the column moves from 18 to 19. F07-T01, F08-T14, and F09-T01 also compare a whole help, but each passes `main` its own commands, which F10 does not change.

F10 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, `and_list`, `comma_list`, and `format_table`.
- F03's `DataFolder`, `Problem`, `Catalog`, `Ingredient`, `Tag`, and `read_catalog`.
- F04's `Recipe`, `RecipeIngredient`, and `read_recipes`.
- F05's `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, and `stop_at_error` in `app`, and `COMMANDS` in `cli`.

### 3.1 `matching_form`

- Module: catalog
- Purpose: The matching form of F03 design 2.6, which `Catalog`, `read_catalog`, and `read_pantry` already use to compare names. `catalog` exports it so that `search` compares a word with a name by the same case rule, and no module writes a second one, as the Architect asked in the F03 review. `src/recipe_menu/catalog/__init__.py` imports it from `src/recipe_menu/catalog/_matching.py` and lists it in `__all__`. The function and its doc comment stay as they are, and `is_blank` stays internal.

Signature:

```python
def matching_form(text: str) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | A text as written, such as a name or a word from the command line. | Any string. |

- Return value: The matching form of `text`: the text without whitespace at both ends, as `str.strip()` removes it, with each ASCII capital letter from A to Z changed to its small letter. Nothing else changes, by rules 1 to 6 of F03 design 2.6: whitespace inside the text counts as written, look-alike letters stay as they are, no text is normalized, and Chinese characters stay as they are. Two texts match when their matching forms are equal, and a word appears in a text when its matching form is part of the text's matching form (choice 4).

Errors: None

- Side effects: None
- Performance target: None. `search` calls it once for each name of the catalog, each name of a recipe, and each word in a run (choice 10).

Example:

```python
from recipe_menu.catalog import matching_form

assert matching_form(" TOMATO\t") == "tomato"
assert matching_form("\u3000番茄") == "番茄"
assert matching_form("Choy  Sum") == "choy  sum"
assert matching_form("\u212aale") == "\u212aale"  # U+212A KELVIN SIGN
assert matching_form("\uff34omato") == "\uff34omato"  # U+FF34 FULLWIDTH LATIN CAPITAL LETTER T
assert matching_form("\u3000") == ""
assert matching_form("egg") in matching_form("Eggplant")
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `search` is the module of architecture 3: the folder `src/recipe_menu/commands/search/`, whose `__init__.py` lists only `SEARCH_COMMAND` in `__all__`, with its messages in its own `messages.py` (architecture 8). It imports `app`, `lang`, `text`, `datafile`, `catalog`, and `recipes`, which its row allows, and the Architect's model of section 2 needs no other module. Choice 2 leaves the arrow from `search` to `browse` in architecture 4 unused, which the rules allow, so the architecture needs no change. The only change in `cli` is the entry after `SHOW_COMMAND` in `COMMANDS` (architecture 4), and `cli` may import `search`. Choice 3 reads the data model as architecture 5.2 and 5.3 give it: each `RecipeIngredient` refers to the catalog's own `Ingredient`, which has both names, and each tag of a recipe is a `Tag` of the catalog. So the sets of catalog ingredients and tags that choice 10 builds for each word give the same places as a test of each line's names. `search` adds no value type, keeps no state at module level, and keeps its matching forms for one run only (architecture 8). It reads what architecture 8 gives `search`: the settings in `cli`, the catalog, and every recipe, and neither the pantry nor a menu (choice 8). Exporting `matching_form` from `catalog` (section 3.1) is the right way to share F03's case rule. The rule is part of finding ingredients and tags by name, which architecture 3 gives `catalog`, and `search` may import `catalog`. Moving the function to `text` or `lang` would change a base module of F02 for a rule that only names use. A method on `Catalog` that gives the names that hold a word would move part of `search` into `catalog`, and it would not cover recipe names, which `catalog` does not hold. The F03 review asked for this export. |
| Follows the error handling and naming conventions | Pass | Exit codes follow architecture 1 and 6. `search` gives 0 for a result, also with no match, as the prototype "No match" shows. It gives 1 through `first_error` and `stop_at_error` for an error in the catalog, the listing of `recipes/`, or a recipe file. `run` raises `UsageError(EMPTY_WORD, None)` for an empty word before it reads a file or writes output, as `Command.run` requires (F05 design 2.5), and `cli` turns it into 2. `EMPTY_WORD` says what to write, so it names no hint (ADR-0008). Warnings change nothing (architecture 6). The result goes to `context.out` and the errors to `context.err` (architecture 6 and 8). Names follow architecture 8: the module has the command's name, and the messages are UPPER_SNAKE `Message` and `Plural` constants in `messages.py`. Lists come from `and_list` and `comma_list`, plurals from `Plural`, and the table from `format_table`, so no module builds them by hand. Choice 9 holds: the only number in a message is the count, and a word is a `str`, so F02's limit of 4,300 digits never applies. The model wrote a word of 5,000 digits with no error. Point B: the Architect agrees with option 1. An empty word is a wrong argument value, to which requirements 3 and architecture 6 give exit code 2, as F09 does for `show ""`. F03's rule 7 is about equal names. Under `in`, the empty text appears in every text, so option 2 would need its own special case, and it would hide the typing mistake. Point A does not touch the architecture, and the Architect agrees with its recommendation: each new text is a `Message` or a `Plural` in both languages, and its lists come from `and_list`. |
| Does not duplicate an existing interface | Pass | `search` calls `matching_form`, `read_catalog`, `read_recipes`, `first_error`, `stop_at_error`, `format_table`, `and_list`, `comma_list`, `Plural.pick`, `Message.to_bitext`, and `BiText.get`, and builds none of them again. Exporting `matching_form` keeps one case rule for names in the tool, as the F03 review asked. Choice 2 repeats the texts of two messages of `browse`, `ID_HEADING` and `NAME_HEADING`. These are internal messages, not interfaces, and architecture 8 keeps each module's messages in its own `messages.py`. Exporting them would add two names to F09's implemented interface for two short texts, so the Architect agrees with choice 2 and the cost that it states. `search` also repeats the few lines of the internal `read_catalog_or_stop` of `browse`. Those lines call F05's shared `first_error` and `stop_at_error`, so `search` repeats no interface. `search` adds no reader. |
| Depends only on features earlier in the order | Pass | F10 uses `lang` and `text` from F01 and F02, `datafile` and `catalog` from F03, `recipes` from F04, and `app` and `cli` from F05. All of them come before F10 and pass their tests on main. F05 is the hard dependency of the F10 row, and F03 and F04 are soft ones. F09, the third soft one, gives only the text of the `UNKNOWN_ID` hint, and F10 imports nothing from `browse`. F02 is not in the row, but it comes before F03, which uses it. No later feature builds on F10. F10 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. Adding `SEARCH_COMMAND` moves the second column of the help from 18 to 19 columns, because `cli` sizes the help from `COMMANDS` (F05 design 2.9), and section 3 names the tests of the real help. The Architect checked that claim by running the tests. With the model in a copy of the repository, the whole test suite of main gives 462 passed and 3 skipped on Troy's PC, the 3 skips being the Windows-only cases of main. So F05-T48, F05-T49, F07-T17, F08-T14, F09-T01, F09-T19, F09-T25, and every other test stay true. Choice 10's lookups rest on architecture 5.2, which says that recipes refer to the catalog's own `Ingredient` values, so no new contract appears between `recipes` and `search`. The `UNKNOWN_ID` hint of F09 names `search` only as text. Under choice 3, the hint finds a recipe by a word of its name, such as `mapo`, and finds nothing for a typo such as `tomato-eggs`, as choice 3 says. A note for Troy that does not block: a search that also matches IDs would make the ID a fourth place, which needs the requirement change flow. The Architect does not recommend it for v0.1. |
| Changes an implemented interface only through the change flow | Pass | The one change to an implemented interface is the new export `matching_form` of F03's `catalog` (section 3.1). The function, its signature, its behavior, and its doc comment stay as they are, so F03's tests pass unchanged, as the model's test run confirms. The requirements do not change, so no `[docs]` PR is needed, and the Architect reviews the addition here, as it did for the names that F04 and F05 added to `datafile` in their section 3. `browse` and every other interface stay as they are, and the entry in `COMMANDS` is internal to `cli`, which architecture 4 gives each command feature. The mock plan is right. The mock holds `search/__init__.py`, `search/messages.py`, at most one internal file with a `run` that writes nothing and gives 0, the entry in `cli/_commands.py`, and the export in `catalog/__init__.py`. That is at most 5 files and well under 500 lines (R03). The export and the entry belong in the mock, so that the tests can import `matching_form` and run `search` through `main`. The matching and the output belong in the implementation, which changes only internal files of `search` and so also fits R03. Every new test of the output, of exit code 1, or of `EMPTY_WORD` then fails against the mock (R09), and the design names the tests that would pass against it. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 5 `python` blocks of each file: each one parses and equals its mirror. It built a model of section 2 in a copy of the repository, with `SEARCH_COMMAND` in `COMMANDS` and `matching_form` exported, and ran the examples of 2.1, 2.2, and 3.1 on a fresh copy of `tests/data/example/` in Python 3.13.18. Every assertion and the `# raises` hold. These include the help lines with the second column after 19 columns, `search pork`, `search mapo`, `search scallion QUICK noodle`, the three lines after the `郫县` change to `mapo-tofu.toml`, and `search ""` with exit code 2 after that change. More runs confirm the prose of choices 4, 6, and 8. `search -x` and a word of U+200B find nothing and exit with 0. A word with `"` and a line break is written as typed. `search ""` with a missing data folder gives `NO_DATA_FOLDER` and exit code 1. A missing `recipes/` stops `search` with exit code 1, and `search 番茄 --help` writes the 18 lines of the help. On a PT01 folder from `tests/pt01_support.py`, `search 食材001` writes 1,000 rows matched in `ingredient` and the line `1000 recipes match "食材001".`. Five runs of each command with `python -m recipe_menu` on Troy's PC, taken in turn, gave a median of 0.789 s for `search` (0.785 to 0.802 s) and 0.794 s for `list` (0.791 to 0.794 s). So choice 10's estimate holds, about 0.2 s under the limit, and no `[refactor]` side PR needs to come first. | Approved. The Architect agrees with the recommendation of points A and B, which Troy decides when Troy approves this design. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-13 | First draft. |
| 1.0 | 2026-11-13 | Approved by Troy. |
