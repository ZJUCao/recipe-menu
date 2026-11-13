---
troy-doc: "F07-design"
lang: "en"
version: "1.0"
updated: "2026-11-12"
status: "Approved by Troy on 2026-11-12"
mirror: "design.zh-CN.md"
---

# F07 Check the data files: interface design

## 1. Feature

- ID and name: F07 Check the data files
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F03, F04, F06

## 2. Interfaces

F07 builds the command module `check` in `src/recipe_menu/commands/check/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.check` exports one name, `CHECK_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu check` (2.2). Its messages live in `src/recipe_menu/commands/check/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F07 adds `CHECK_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). The F07 prototype `docs/prototypes/F07-check.md` shows the report, and the second output of the F08 prototype "In English" shows a report with no problems.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F07 gives |
| --- | --- |
| `recipe-menu check` reads the settings, the catalog, the pantry, every recipe, and every week menu. | `recipe-menu check` (2.2), whose `run` in `CHECK_COMMAND` (2.1) calls the readers of F03 to F06 in the seven steps of 2.2. |
| It lists the errors and the warnings with their places. | The report of 2.2: the count line, then a block of errors and a block of warnings. Each problem shows its file and place on one line and its message on the next, as the F07 prototype shows. |
| It exits with code 1 when there is an error. | The exit codes of 2.2: 1 when the report has an error, and 0 otherwise, also when it has warnings ([architecture 6](../../architecture.md#6-error-handling)). |
| You run `check`, fix what it reports, and run it again until it reports no errors ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 1). | The closing line `FIX_AND_CHECK_AGAIN` after errors, and `NO_ERRORS` or `NO_ERRORS_OR_WARNINGS` when there are none (2.2). |
| `check` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus (PT01, [requirements 7.1](../../requirements.md#71-performance-targets)). | The performance target of 2.2, and the rule on time below. |

These rules hold for every interface below:

- `check` imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus` from the package. Its row of architecture 3 allows them, and it needs neither `units` nor `shopping` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `check` reaches the disk only through the readers of F03 to F06, which read through `datafile` (architecture 8). It writes no file ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 1](../../architecture.md#1-context-and-constraints)). It writes only to `context.out`. It reads nothing of the outside world itself: no argument, environment variable, date, or console stream (architecture 8). It keeps no state.
- A reader never raises for bad data, and neither does `check` (architecture 6). It shows every problem that the readers return and stops at none. Any exception that reaches `cli` is a bug.
- `CHECK_COMMAND` is a frozen `Command` (F05 design 2.5). F07 adds no value type.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- `recipe-menu check` has the performance target PT01 (2.2). It reads each data file once, except `settings.toml`, which `cli` also reads at start (F05 design 2.10). It lists `recipes/` and `menus/` once each, builds the set of recipe IDs once for every menu, and writes its report once, after the last file. So its time grows in proportion to the size of the files. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 gives the rules of choices 2 to 7.

1. **The first command in the help.** `check` is the first real command, so `COMMANDS` holds only `CHECK_COMMAND` after F07 (2.1). Each later command feature adds its `Command` at its place in the help's order: F08 puts `init` before `check`, and F09, F10, F11, and F13 put theirs after it (F05 design, section 2). The help keeps F05's layout (F05 design 2.10). With `check` alone, the widest first cell is `--data FOLDER` or `--data 文件夹`, of 13 columns, so the second column starts after 18 columns. The help ends with the note on weeks, as F05 writes it, although no command takes a week before F11. With the eight commands of v0.1, the help gives the two help outputs of the F05 prototype, which v0.1-S19 checks. With `check` alone, `recipe-menu --help` gives these lines:

   ```text
   Usage: recipe-menu COMMAND [ARGUMENTS] [--lang en|zh] [--data FOLDER]

   Keep your recipes, plan a week's menu, and make its shopping list.

   Commands:
     check           Check every data file for mistakes.

   Options:
     --lang en|zh    The language of the output. Default: the settings, else English.
     --data FOLDER   The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
     --version       Show the version.
     --help          Show this help.

   WEEK is an ISO week such as 2026-W47, "this", or "next". Default: this.
   ```

   `recipe-menu --help --lang zh` gives these lines:

   ```text
   用法：recipe-menu 命令 [参数] [--lang en|zh] [--data 文件夹]

   保存菜谱，排一周的菜单，并生成它的购物清单。

   命令：
     check           检查每个数据文件有没有错误。

   选项：
     --lang en|zh    输出语言。默认：设置里的语言，否则英文。
     --data 文件夹   数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
     --version       显示版本。
     --help          显示这份帮助。

   “周”是 ISO 周，比如 2026-W47，也可以是 this（本周）或 next（下周）。默认：本周。
   ```

2. **`check` reads the settings itself, and never uses `context.settings`.** `cli` reads the settings at start, but `Context` does not carry their problems, and `FolderUse.CHECK` lets an error in the settings through (F05 design, choice 6). So `check` calls `read_settings` itself (2.2, step 1). It passes the `Settings` or `None` that `read_settings` gives to `read_week_menu`. After an error, `context.settings` holds `Settings()`, whose default meals would give menu problems that the file does not have. With `None`, `read_week_menu` makes only the checks that do not depend on the settings (F06 design, choice 3). Without an error, the two values are equal. So `run` never reads `context.settings`, and the example of 2.1 shows it. Reading the settings again costs one read of a file of a few lines.
3. **One listing of `recipes/`.** `check` calls `list_recipe_ids` once, and then `read_recipe` for each ID (2.2, steps 4 and 5). Those two steps give the same problems in the same order as `read_recipes` (F04 design 2.7), so `check` reports the problems of `list_recipe_ids` once. It does not call `read_recipes`, because `read_recipes` gives no IDs, and `check` needs them for the count and for the menus. With `read_recipes`, `check` would list `recipes/` twice and drop the problems of the second listing, which equal those of the first only when no file changed in between. One listing gives one set of IDs for the count, the recipes that `check` reads, and the menus. When `recipes/` is missing or cannot be listed, `list_recipe_ids` gives one error and no IDs (F04 design 2.5). The set of IDs is then empty, so each dish of each menu gets `UNKNOWN_RECIPE`. Those errors are true, because no command can find those recipes. They come after the folder's own error, and they go when the folder is back. `read_week_menu` cannot skip its check of the IDs, and an option to skip it would change F06's implemented interface.
4. **The order of the problems.** The problems come in the order of the seven steps of 2.2: the settings, the catalog, the pantry, the listing of `recipes/`, each recipe in the order of its ID, the listing of `menus/`, and each week menu in the order of time. Within a step, they come in the order that its reader gives. This is also the order of the count line, and a fix in an earlier file can remove problems in a later one, such as a missing ingredient of the catalog. The block of errors and the block of warnings each keep this order. So the F07 prototype lists `recipes\mapo-tofu.toml` before `menus\2026-W47.toml`, and v0.1-S07 accepts any order.
5. **The count line names what `check` looked at.** It always names the settings, the catalog, and the pantry, also when a file is missing or cannot be read. The block of errors then says what went wrong. Its number of recipes is the number of IDs that `list_recipe_ids` gave, whether or not their files have problems. Its number of week menus is the number of weeks that `list_menu_weeks` gave. A file whose name is not a recipe ID or a week does not count, because `check` does not read it, and its error names it. A folder that is missing or cannot be listed gives 0 and its error. The F07 prototype "A syntax mistake" names the pantry that `check` could not read, and the F07 prototype counts `mapo-tofu` among the 7 recipes, although it has an error. An empty data folder gives `Checked the settings, the catalog, the pantry, 0 recipes, and 0 week menus.` and five errors, as the example of 2.2 shows.
6. **The report and the exit code.** The report goes to the output stream with either exit code, and nothing goes to the error stream (architecture 6). It has the count line, then the errors, then the warnings, and then the closing line when there are errors (2.2). A problem takes two lines: its file and place with two spaces before them, and its message with four. `check` writes the texts of `problem_lines` as they are (F05 design 2.8). With warnings and no errors, the report says `No errors.` before the warnings. With neither, it says `No errors. No warnings.`. The F07 prototype "After the fixes" and the F08 prototype show the two lines. The exit code is 1 when the report has an error and 0 otherwise. A warning never changes it (architecture 6). `check` writes the report after it reads the last file, because the first lines need the counts.
7. **Numbers in messages.** The messages of `check` show only counts: of recipe IDs, of weeks, of errors, and of warnings. Each count is the length of a tuple in memory, so it stays far below F02's limit of 4,300 digits (F02 design 2.3). A value from a file reaches a message only through the readers of F03 to F06, which limit a number from a file to 15 digits or show the file's text (F04 design, choice 2, F05 design 3.1, F06 design, choice 6). So no message of the report meets that limit.
8. **The commands that send you to `check`.** Every other command stops at the first error in a data file with `stop_at_error`, whose last line `RUN_CHECK` says `Run "recipe-menu check" to see every problem.` (F05 design 2.8, architecture 6). F11's "A menu with a mistake" shows that line. `check` reads every file that those commands read, with the same readers. So the error that stopped a command is among the errors of `check`, as long as the command passes the same arguments, as the plans below say.

The F07 prototype "A syntax mistake" shows the count line of the example folder, but not its warning. On the example data, the report also holds the warning of `recipes\red-braised-pork.toml`, as the example of 2.2 shows. v0.1-S06 runs that case on the init folder, which has no warning, so the scenario holds with the rules of 2.2. The Product Manager can add the warning to that section or leave it as it is.

These later features are meant to build on F07. Their own designs decide the details.

- F08's `init` writes files on which `check` reports `No errors. No warnings.` with 1 recipe and 0 week menus (v0.1-S01). So `init` also creates the empty folder `menus/`, as requirement F08 says. Without it, `check` reports `menus` with `The folder is missing.`. In the help, `init` comes before `check`.
- The commands of F09, F10, F11, F13, and F14 stop at the first error with `first_error` and `stop_at_error` (F05 design 2.8). So that the error that stopped them is among the errors of `check`, they read each file with the reader that `check` uses, and with the same arguments: the settings of the file, the catalog that `read_catalog` gave, and the IDs of `list_recipe_ids` as a `frozenset`. For a command with `FolderUse.READ`, `context.settings` holds the settings of the file, so `menu show` and `shop` can pass it (F06 design, section 2).
- F15 and F16 reuse `check` to check one recipe (architecture 3). The F16 prototype shows a problem with the indents of `check`. Their designs add to the interface of `check` what they need, such as the two indented lines of a problem. F07 keeps those functions internal, so that no name is exported before a feature uses it.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/check/__init__.py` and `messages.py`, maybe an internal file, and the entry in `src/recipe_menu/cli/_commands.py`. It defines every message and `CHECK_COMMAND` with all its fields, so the help lists `check` and `recipe-menu check` runs. Its `run` reads no file yet. For example, it writes nothing and gives 0, so a new test of the report or of exit code 1 fails against the mock (R09). A test that checks only the fields of `CHECK_COMMAND`, the help, a message, or what `cli` does before it runs `check` passes against the mock and breaks R09, as the Architect noted for F05 and F06. Examples of the last kind are a missing data folder and `recipe-menu check extra`. The implementation (PR 5) reads the files and writes the report. Each PR fits R03's 5 files.

### 2.1 `CHECK_COMMAND`

- Module: check
- Purpose: The description of the `check` command. `cli` reads it to parse the command line, write the help, check the data folder, and run the command (F05 design 2.5 and 2.9). Its `run` reads every data file and writes the report of 2.2.

Signature:

```python
CHECK_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("check",)
#   help_line = CHECK_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.CHECK
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("check",)`. | None |
| `help_line` | `Message` | `CHECK_HELP`: "Check every data file for mistakes." and "检查每个数据文件有没有错误。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Reads every data file and writes the report of 2.2. | Gives 0 or 1. |
| `argument` | `None` | `check` takes no argument. | None |
| `options` | An empty tuple | `check` has no options of its own. | None |
| `folder` | `FolderUse` | `FolderUse.CHECK`: `cli` stops `check` when the data folder is missing, and runs it when the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli`: the language, the data folder, and the output stream (F05 design 2.4). | `run` uses only `context.lang`, `context.folder`, and `context.out`. It uses neither `context.settings` (choice 2), nor `context.err`, nor `context.today`. |
| `arguments` | `Arguments` | What the command line gives `check` (F05 design 2.6). | Empty, because `check` declares no argument and no option, so `cli` lets no value through. `run` does not read it. |

- Return value: `CHECK_COMMAND`, a `Command`.
  - `CHECK_COMMAND.usage` is `check` in both languages, so the help shows `check`, and a usage error quotes `recipe-menu check`.
  - `CHECK_COMMAND.run(context, arguments)` reads the files in the seven steps of 2.2, writes the report of 2.2 to `context.out` in `context.lang`, and gives 1 when the report has an error, and 0 otherwise.

Errors: None. `run` never raises for bad data. A missing data folder gives one error for each file and folder, as an empty one does (2.2). `run` raises no `UsageError`, because `check` takes no argument value.

- Side effects: Those of 2.2. `run` reads the data files through the readers of F03 to F06, writes to `context.out`, and writes no file.
- Performance target: None. PT01 times `recipe-menu check` (2.2) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context holds settings with dinner alone, and the menu has a lunch on Saturday, so a `run` that used `context.settings` would report that lunch as an unknown meal. The help comes from `COMMANDS`, which holds only `CHECK_COMMAND` after F07.

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.check import CHECK_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings

assert CHECK_COMMAND.words == ("check",)
assert CHECK_COMMAND.usage == BiText("check", "check")
assert CHECK_COMMAND.help_line.render(Lang.EN) == "Check every data file for mistakes."
assert CHECK_COMMAND.help_line.render(Lang.ZH) == "检查每个数据文件有没有错误。"
assert (CHECK_COMMAND.argument, CHECK_COMMAND.options) == (None, ())
assert CHECK_COMMAND.folder is FolderUse.CHECK

out, err = io.StringIO(), io.StringIO()
dinner_only = Settings(Lang.ZH, (Meal.DINNER,), 3)
context = Context(Lang.EN, folder, dinner_only, out, err, date(2026, 11, 10))
assert CHECK_COMMAND.run(context, Arguments()) == 0
pork = Path("recipes", "red-braised-pork.toml")
assert out.getvalue().splitlines() == [
    "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu.",
    "",
    "No errors.",
    "",
    "1 warning:",
    f"  {pork}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
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
assert len(english) == 14
assert english[4:6] == ["Commands:", "  check           Check every data file for mistakes."]
assert english[9].startswith("  --data FOLDER   The data folder.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[5] == "  check           检查每个数据文件有没有错误。"
assert chinese[9].startswith("  --data 文件夹   数据文件夹。")
```

### 2.2 `recipe-menu check`

- Module: check
- Purpose: The command that checks the data folder ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flows 1 and 3, and [4](../../requirements.md#4-features)). It reads the settings, the catalog, the pantry, every recipe, and every week menu. It lists every error and every warning with its file and place, and exits with code 1 when there is an error. The F07 prototype shows it.

Signature:

```text
recipe-menu check [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--lang` | `en` or `zh` | The language of the report. | As F05 design 2.10 gives it. Without the option, the language of the settings, or English when the settings name none or have an error (F05 design, choice 4). |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (choice 1) and does not run `check`. | None |

`check` reads the data folder `context.folder` in these steps, in order. Steps 3, 5, and 7 use what the earlier steps gave.

1. `read_settings(folder)` gives `settings`, a `Settings` or `None` (F05 design 2.3).
2. `read_catalog(folder)` gives `catalog`, a `Catalog` or `None` (F03 design 2.8).
3. `read_pantry(folder, catalog)` reads the pantry (F03 design 2.9). With `None`, it checks only the form of the file.
4. `list_recipe_ids(folder)` gives `ids` (F04 design 2.5).
5. `read_recipe(folder, catalog, recipe_id)` reads each ID of `ids`, in their order (F04 design 2.6). With `None` for the catalog, it checks only the form of the file.
6. `list_menu_weeks(folder)` gives `weeks` (F06 design 2.8).
7. `read_week_menu(folder, week, settings, recipe_ids)` reads each week of `weeks`, in their order (F06 design 2.9). `recipe_ids` is `frozenset(ids)`, made once for every week. With `None` for the settings, it checks only what does not depend on them.

The problems of the report are the problems of the seven steps, in this order, each step's in the order that its reader gives (choice 4). `check` uses the catalog and the settings only as the arguments of later steps, and it uses no `Pantry`, `Recipe`, or `WeekMenu` that the readers give. It reads no other file: not `shopping/`, which `shop` writes, and not an entry of `recipes/` or `menus/` that is not a `.toml` file (F04 design 2.5, F06 design 2.8).

- Return value: The exit code, and the report on the output stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | The report has no error. It may have warnings. | The output stream: the report. |
| 1 | The report has an error. | The output stream: the report. Nothing goes to the error stream. |

The report is these lines, in this order, each ended by a line break:

1. The count line: `CHECKED`, with the parts of choice 5.
2. An empty line.
3. With errors: the heading `ERRORS_HEADING`, picked by the number of errors, and then the two lines of each error. Without errors: `NO_ERRORS` when there are warnings, and `NO_ERRORS_OR_WARNINGS` when there are none. The report ends here when it has neither errors nor warnings.
4. With warnings: an empty line, the heading `WARNINGS_HEADING`, picked by the number of warnings, and then the two lines of each warning.
5. With errors: an empty line, and then `FIX_AND_CHECK_AGAIN`.

The two lines of a problem are `where` and `what` of `problem_lines(problem, context.lang)` (F05 design 2.8): two spaces and then `where`, and four spaces and then `what`. `where` is the file, such as `settings.toml`, when the problem has no place, and the file and the place otherwise, such as `recipes\mapo-tofu.toml, ingredient 3` on Windows. The headings and the other lines have no indent. A problem with `Severity.ERROR` is an error, and one with `Severity.WARNING` is a warning.

The table gives the four kinds of report. Each starts with the count line and an empty line.

| Errors | Warnings | The lines that follow | Exit code | Prototype |
| --- | --- | --- | --- | --- |
| None | None | `No errors. No warnings.` | 0 | F08 "In English", second output |
| None | One or more | `No errors.`, an empty line, and the warnings | 0 | F07 "After the fixes" |
| One or more | None | The errors, an empty line, and the closing line | 1 | F07 "A syntax mistake", on the init folder (v0.1-S06) |
| One or more | One or more | The errors, an empty line, the warnings, an empty line, and the closing line | 1 | F07 "Errors and a warning, in English" |

The messages of `check` are these. `RECIPE_COUNT`, `WEEK_MENU_COUNT`, `ERRORS_HEADING`, and `WARNINGS_HEADING` are `Plural` values (F02 design 2.4), each picked by its `count`. Their form "for more" is the form for every count other than 1, 0 included.

| Name | English | Chinese |
| --- | --- | --- |
| `CHECK_HELP` | `Check every data file for mistakes.` | `检查每个数据文件有没有错误。` |
| `CHECKED` | `Checked {files}.` | `已检查{files}。` |
| `THE_SETTINGS` | `the settings` | `设置` |
| `THE_CATALOG` | `the catalog` | `目录` |
| `THE_PANTRY` | `the pantry` | `常备清单` |
| `RECIPE_COUNT`, for one | `{count} recipe` | `{count} 个菜谱` |
| `RECIPE_COUNT`, for more | `{count} recipes` | `{count} 个菜谱` |
| `WEEK_MENU_COUNT`, for one | `{count} week menu` | `{count} 个周菜单` |
| `WEEK_MENU_COUNT`, for more | `{count} week menus` | `{count} 个周菜单` |
| `ERRORS_HEADING`, for one | `{count} error:` | `{count} 个错误：` |
| `ERRORS_HEADING`, for more | `{count} errors:` | `{count} 个错误：` |
| `WARNINGS_HEADING`, for one | `{count} warning:` | `{count} 个警告：` |
| `WARNINGS_HEADING`, for more | `{count} warnings:` | `{count} 个警告：` |
| `NO_ERRORS` | `No errors.` | `没有错误。` |
| `NO_ERRORS_OR_WARNINGS` | `No errors. No warnings.` | `没有错误，也没有警告。` |
| `FIX_AND_CHECK_AGAIN` | `Fix the errors and run "recipe-menu check" again.` | `改正错误后，再运行“recipe-menu check”。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `files` | `and_list` of five parts, each as a `BiText`, in this order: `THE_SETTINGS`, `THE_CATALOG`, `THE_PANTRY`, `RECIPE_COUNT`, and `WEEK_MENU_COUNT`. The example data gives "the settings, the catalog, the pantry, 7 recipes, and 1 week menu" and "设置、目录、常备清单、7 个菜谱和 1 个周菜单". `and_list` puts the space between 和 and the digit (F02 design 2.6). |
| `count` | The number of IDs that `list_recipe_ids` gave in `RECIPE_COUNT`, and of weeks that `list_menu_weeks` gave in `WEEK_MENU_COUNT`. The number of errors in `ERRORS_HEADING`, and of warnings in `WARNINGS_HEADING`. Each is the length of a tuple (choice 7). |

With these messages, the lines of the F07 prototype and of v0.1-S01, v0.1-S02, v0.1-S04, and v0.1-S06 follow: for example, `Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.` and `已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。`.

Errors:

`cli` reports the mistakes on the command line and a missing data folder before it runs `check` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 1, with the report on the output stream | The report has an error (choice 6). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT` on the error stream and nothing on the output stream | The data folder is not a folder. `cli` checks it in step 9 of F05 design 2.10, because `check` has `FolderUse.CHECK`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "extra". Write "recipe-menu check".` | A word follows `check`. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"check" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. Nothing more is written (F05 design 2.10), and the report is not written when `check` has not read every file. |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `check` then reads `settings.toml`, `catalog.toml`, and `pantry.toml` once each, lists `recipes/` and `menus/` once each, and reads each recipe file and each menu file once, all through the readers of F03 to F06. It writes the report to the output stream. It writes no file, so every file and folder keeps its bytes and modification time (v0.1-S23).
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The first run makes the two mistakes of the F07 prototype. The next runs undo them and make one other mistake each: the syntax mistake of the F07 prototype, and then the broken settings of the F05 prototype together with a breakfast on Monday. The settings name no breakfast, but `read_week_menu` gets `None` for them and accepts it (choice 2). The run after that adds English steps to `red-braised-pork`, which removes the warning. The last runs check an empty data folder, a missing one, and two mistakes on the command line.

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def check(data: Path, *argv: str) -> tuple[int, list[str], str]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["check", "--data", str(data), *argv],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue()


COUNTS = "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
FIX = 'Fix the errors and run "recipe-menu check" again.'
mapo_file = Path("recipes", "mapo-tofu.toml")
pork_file = Path("recipes", "red-braised-pork.toml")
week_file = Path("menus", "2026-W47.toml")
pork_warning = [
    "1 warning:",
    f"  {pork_file}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
]

mapo, menu = folder.recipe_file("mapo-tofu"), folder.menu_file("2026-W47")
mapo_text, week_text = mapo.read_text(encoding="utf-8"), menu.read_text(encoding="utf-8")
mapo.write_text(mapo_text.replace("郫县", ""), encoding="utf-8")
menu.write_text(week_text.replace('"tomato-egg"', '"tomato-eggs"'), encoding="utf-8")
code, lines, err = check(folder.root)
assert (code, err) == (1, "")
assert lines == [
    COUNTS,
    "",
    "2 errors:",
    f"  {mapo_file}, ingredient 3",
    '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
    f"  {week_file}, Monday dinner",
    '    Unknown recipe "tomato-eggs".',
    "",
    *pork_warning,
    "",
    FIX,
]
code, lines, _ = check(folder.root, "--lang", "zh")
assert code == 1
assert lines[0] == "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。"
assert lines[2:4] == ["2 个错误：", f"  {mapo_file}，食材 3"]
assert lines[8:10] == ["1 个警告：", f"  {pork_file}，步骤"]
assert lines[-1] == "改正错误后，再运行“recipe-menu check”。"

mapo.write_text(mapo_text, encoding="utf-8")
menu.write_text(week_text, encoding="utf-8")
pantry_text = folder.pantry.read_text(encoding="utf-8")
folder.pantry.write_text('# The pantry.\npantry = ["食用油", "盐" "糖"]\n', encoding="utf-8")
code, lines, _ = check(folder.root)
assert code == 1
assert lines == [
    COUNTS,
    "",
    "1 error:",
    "  pantry.toml, line 2",
    '    The file cannot be read: a closing "]" is missing.',
    "",
    *pork_warning,
    "",
    FIX,
]

folder.pantry.write_text(pantry_text, encoding="utf-8")
settings_text = folder.settings.read_text(encoding="utf-8")
folder.settings.write_text('meals = ["lunch", "supper"]\n', encoding="utf-8")
breakfast = week_text.replace("[monday]\n", '[monday]\nbreakfast = ["rice"]\n')
menu.write_text(breakfast, encoding="utf-8")
code, lines, _ = check(folder.root)
assert code == 1
assert lines[2:5] == [
    "1 error:",
    "  settings.toml, meals",
    '    Unknown meal "supper". The meals are breakfast, lunch, and dinner.',
]

folder.settings.write_text(settings_text, encoding="utf-8")
menu.write_text(week_text, encoding="utf-8")
pork = folder.recipe_file("red-braised-pork")
steps = pork.read_text(encoding="utf-8") + 'en = ["Braise the pork."]\n'
pork.write_text(steps, encoding="utf-8")
assert check(folder.root) == (0, [COUNTS, "", "No errors. No warnings."], "")

empty = home / "empty"
empty.mkdir()
code, lines, _ = check(empty)
assert code == 1
assert lines == [
    "Checked the settings, the catalog, the pantry, 0 recipes, and 0 week menus.",
    "",
    "5 errors:",
    "  settings.toml",
    "    The file is missing.",
    "  catalog.toml",
    "    The file is missing.",
    "  pantry.toml",
    "    The file is missing.",
    "  recipes",
    "    The folder is missing.",
    "  menus",
    "    The folder is missing.",
    "",
    FIX,
]

missing = home / "missing"
code, lines, err = check(missing)
assert (code, lines) == (1, [])
assert err.splitlines() == [
    f"There is no data folder at {missing}.",
    'Run "recipe-menu init" to create it, or name another folder with --data.',
]
code, lines, err = check(folder.root, "extra")
assert (code, lines) == (2, [])
assert err.splitlines() == [
    'Unexpected argument "extra". Write "recipe-menu check".',
    'Run "recipe-menu --help" to see the commands.',
]
code, _, err = check(folder.root, "--tag", "素")
assert code == 2
assert err.splitlines() == [
    '"check" has no option "--tag". It has no options of its own.',
    'Run "recipe-menu --help" to see the options.',
]
```

## 3. Changes to existing interfaces

None. No interface that F01 to F06 implemented changes. Each exported name keeps its signature and its behavior, and the tests of F01 to F06 pass unchanged. F07 adds the module `check`. It also adds one entry to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is internal to `cli` and which architecture 4 gives each command feature. With that entry, the help of the real `recipe-menu` lists `check` (choice 1). F05-T48 and F05-T49 are the only tests that run the real `COMMANDS`. They check an unknown command, a line with no command, and the first and last lines of the help, which the entry does not change. Every other test passes its own commands to `main`.

F07 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, and `and_list`.
- F03's `DataFolder`, `Problem`, `Severity`, `Catalog`, `read_catalog`, and `read_pantry`.
- F04's `list_recipe_ids` and `read_recipe`.
- F05's `Arguments`, `Command`, `Context`, `FolderUse`, and `problem_lines` in `app`, `Settings` and `read_settings` in `settings`, and `COMMANDS` in `cli`.
- F06's `IsoWeek`, `list_menu_weeks`, and `read_week_menu`.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `check` is the command module of architecture 3, in `src/recipe_menu/commands/check/`, and exports only `CHECK_COMMAND`. It imports `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus`, which its row allows. `cli` imports it in `_commands.py`, the one change in `cli` that architecture 4 gives a command feature. `CHECK_COMMAND` is a `Command` of architecture 5.2, F07 adds no value type, and the IDs reach `menus` as a `frozenset` (architecture 8). `check` reads only through the readers of F03 to F06, parses every recipe as architecture 8 says, and writes no file (architecture 1). Choice 1 holds. With `CHECK_COMMAND` in `COMMANDS`, the Architect's model gives the 14 lines of each help block of choice 1 exactly, in both languages, with the second column after 18 columns. Finding 1, not blocking: PT01 is tight. The Architect generated a data folder as the v0.1 test plan describes it for v0.1-S27: 1,000 recipes, 300 ingredients, and 52 week menus of 63 dishes. In this session on Troy's PC, `python -m recipe_menu check` on the model took a median of 1.006 s over 5 runs, the first of them a cold run of 5.3 s, and 1.017 s over 5 more runs. In the process, `read_recipe` took 0.77 s for the 1,000 recipes, and `read_toml` alone took 0.27 s for the same files. The 52 menus took 0.08 s, the other files and the two listings 0.02 s, and the start with the imports 0.14 s. The design already reads the minimum, each file once and each folder once, so no change to F07's interfaces makes `check` faster. A profile shows that the readers of F04 build place texts and lists of keys for files with no problems: 31,000 calls of `Message.to_bitext` and 27,000 calls of `report_unknown_keys` for 1,000 recipes with no problems. Under the profiler, `Message.to_bitext` alone took 0.55 s of the 1.93 s of `read_recipe`. Building those texts only when a problem needs them is an internal change to `recipes` and `datafile`, and it changes no interface. F09's `list` and F10's `search` read the same 1,000 recipes, so they share the risk. The Architect recommends a `[refactor]` PR for those readers, timed on a PT01 data folder, before the F07 implementation PR. |
| Follows the error handling and naming conventions | Pass | Readers never raise for bad data, and `run` neither raises nor stops at a problem (architecture 6). The exit code is 1 when the report has an error and 0 otherwise, and a warning never changes it. The report goes to the output stream with either code, as architecture 6 says for `check`, so choice 6 holds. `cli` keeps the usage errors and the missing data folder, as F05 design 2.10 and ADR-0008 give them. Every message is an UPPER_SNAKE constant in `check/messages.py`, with both languages (architecture 8). The four `Plural` values have the same placeholder in both forms (F02 design 2.4), and `files` comes from `and_list`, so no list or plural is built by hand. Choice 7 holds, because every number that `check` adds is the length of a tuple. The model confirms choices 2, 4, and 5. Both examples hold on it, and a model whose `run` passes `context.settings` to `read_week_menu` fails both. The model gives the three outputs of v0.1-S05 exactly, the second output of F08 "In English" (v0.1-S01), the Chinese count line of v0.1-S02, and the lines of v0.1-S04. It gives the 9 errors and the warning of v0.1-S07 in the order of choice 4. `run` on a folder that does not exist gives the 5 errors of an empty folder, as the Errors line of 2.1 says. Finding 2, not blocking, for Troy: `没有错误。` is the wording of the F16 prototype "A clean edit, in Chinese", `已检查 mapo-tofu：没有错误。`, and `没有错误，也没有警告。` extends it. The Architect sees no reason to change either text. Troy approves them with this design (R18, with `troy_approves_first = 16`). |
| Does not duplicate an existing interface | Pass | `check` calls the readers of F03 to F06 and `problem_lines` of F05, and rewrites none of them. Choice 3 holds. `list_recipe_ids` and then `read_recipe` for each ID give the problems of `read_recipes` in the same order (F04 design 2.7). The loop repeats the few lines inside `read_recipes`, which is the price of keeping the IDs that `read_recipes` does not give. Calling both would list `recipes/` twice. The new messages say what no shared message says. `RUN_CHECK` sends another command to `check`, and `FIX_AND_CHECK_AGAIN` closes the report of `check`. Finding 3, not blocking: F04 design section 2 says that F07 calls `read_recipes` and can count the recipes with `list_recipe_ids`, and the Purpose of F04 design 2.7 names `check` among its callers. Choice 3 gives its reasons but does not name that plan. Choice 3 can add that it replaces the plan of F04. The approved F04 design keeps its text, because no interface changes. |
| Depends only on features earlier in the order | Pass | F07 uses `lang` from F01 and F02, `text` from F02, `datafile` and `catalog` from F03, `recipes` from F04, `app`, `settings`, and `cli` from F05, and `menus` from F06. All five features come before F07 and pass their tests on main. F05 is the hard dependency of the F07 row, and F03, F04, and F06 are its soft dependencies. F01 and F02 come in through `lang` and `text`, which every command uses. The plans for F08 to F16 say what each feature is meant to do and leave the details to its design, so they bind no later design. F07 needs only the standard library, so R16 has no dependency to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | Each assumption between modules is written in the design. The counts come from the same calls of `list_recipe_ids` and `list_menu_weeks` whose problems the report shows (choices 3 and 5). `check` passes the `Settings` or `None` of `read_settings`, not `context.settings`, as the plan for F07 in F05 design section 2 and F06 design, choice 3, ask (choice 2). `check` knows no message of a reader. It sorts the problems only by `Severity` and writes them through `problem_lines`. Choice 8 holds. It is a written plan for F09 to F14, not a hidden rule. With `FolderUse.READ`, `context.settings` equals what `read_settings` gives, so `menu show` and `shop` pass the same settings as `check`. Finding 4, not blocking, for Troy: the Architect agrees with choice 3 on a missing `recipes/`. On the model, the example folder without `recipes/` gives 10 errors: the error of the folder, and then one `UNKNOWN_RECIPE` for each of the 9 dishes of `2026-W47`. Each error is true, and they come after the error of the folder, which says what to fix. To leave them out, `check` would have to recognize `UNKNOWN_RECIPE`, which is internal to `menus`, and that is hidden coupling. The other way, `read_week_menu` would need an option to skip the IDs, which changes F06's implemented interface through the change flow. Skipping the menus when the listing fails would hide their other problems too, such as a wrong week. `init` creates `recipes/`, so the case is rare. The Architect recommends that Troy accept these errors as choice 3 describes them. |
| Changes an implemented interface only through the change flow | Pass | Section 3 rightly says None. The PR adds only the two design files. Every name that F07 uses exists on the branch with the signature that its design gives. The entry in `COMMANDS` is the change that architecture 4 gives every command feature. On the model, with `CHECK_COMMAND` in `COMMANDS`, the tests on the branch give 380 passed and 3 skipped, which are the 383 tests that the branch collects, F05-T48 and F05-T49 included. So no test of F01 to F06 changes. Finding 5, not blocking, for Troy and the Product Manager: on the example folder, the model gives the warning of `recipes\red-braised-pork.toml` after the error of the F07 prototype "A syntax mistake". So that section does not match 2.2 on the folder that the prototype names. v0.1-S06 runs on the init folder and holds, because the model gives the lines of the section with the count line of the init folder. Section 2 suggests adding the warning to the section. That change alone breaks v0.1-S06, which expects the lines of the section after the first one, so the Product Manager would also have to change v0.1-S06. Changing the count line of the section to `Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.`, and saying that the section runs on the init folder, keeps v0.1-S06 true as written. Troy decides a prototype change, as for F05 decision D. A note for the next stages: a test that checks only exit code 0, or only the help, passes against the mock of section 2, whose `run` writes nothing and gives 0, and so breaks R09. Each new test of `run` also checks the lines of the report. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked choices 1 to 8 and the three points that the Interface Designer raised against the requirements, the architecture, ADR-0008, the F05, F07, F08, and F16 prototypes, and v0.1-S01, v0.1-S02, v0.1-S04 to v0.1-S07, and v0.1-S27. Each file has 6 code blocks, each equal to its mirror, and the 480 lines of the two files match heading for heading, row for row, and item for item. The 3 `python` blocks parse. On the F01 to F06 code of the branch, the Architect built a model of section 2 with `CHECK_COMMAND` in `COMMANDS`. It ran the examples of 2.1 and 2.2 on fresh copies of `tests/data/example/` with Python 3.13.18 on Windows, and every assertion holds. The model gives the help of choice 1 and the outputs of the prototypes and the scenarios that the notes on items 1 and 2 name. The tests on the branch pass on it, 380 passed and 3 skipped. No test ran on the PR itself, because it changes no code. Findings 1 to 5 do not block. | Approved. Troy approves the design with its two new Chinese texts (finding 2, R18, with `troy_approves_first = 16`), and decides findings 4 and 5. The Architect recommends the `[refactor]` PR of finding 1 before the F07 implementation PR. The Interface Designer can settle finding 3 in a revision, or leave it. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-12 | First draft. |
| 1.0 | 2026-11-12 | Approved by Troy. |
