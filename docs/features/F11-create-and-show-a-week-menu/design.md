---
troy-doc: "F11-design"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "design.zh-CN.md"
---

# F11 Create and show a week menu: interface design

## 1. Feature

- ID and name: F11 Create and show a week menu
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F02, F06

## 2. Interfaces

F11 builds the command module `menu` in `src/recipe_menu/commands/menu/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.menu` exports two names, `MENU_NEW_COMMAND` (2.1) and `MENU_SHOW_COMMAND` (2.3), and its `__init__.py` lists them in `__all__`. The commands that you type are `recipe-menu menu new` (2.2) and `recipe-menu menu show` (2.4). Their messages live in `src/recipe_menu/commands/menu/messages.py` and are internal to the module (architecture 8). The other files behind them are the Developer's choice. In its mock PR, F11 adds both commands to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `SEARCH_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). F11 also adds names to two implemented modules (section 3). `menus` exports the line for a week with no menu as `NO_MENU` (3.1). `datafile` gets the write of one new file, `create_file`, with its result `FileCreation` and `FileOutcome` (3.2 and 3.3). The F11 prototype `docs/prototypes/F11-menu.md` shows both commands, and the F05 prototype shows their lines in the help.

In this design, `\u00d7` stands for U+00D7 MULTIPLICATION SIGN, which comes before the servings of a dish, and `\u2014` stands for U+2014 EM DASH, which marks an empty meal. Both are written as Python writes them.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F11 gives |
| --- | --- |
| `recipe-menu menu new [WEEK]` creates the week's menu file with every day and meal empty. | `recipe-menu menu new` (2.2), with `MENU_NEW_COMMAND` (2.1). It writes the file of choice 3 through `create_file` (3.3). |
| It refuses when the file exists. | The outcome `EXISTS` of `create_file` (3.2), which `menu new` reports with `ALREADY_EXISTS` and exit code 1 (choice 4). |
| `recipe-menu menu show [WEEK]` prints the week as a table of days and meals, with each dish and its servings. | `recipe-menu menu show` (2.4), with `MENU_SHOW_COMMAND` (2.3), and the table of choice 8. |
| A command that takes a week accepts an ISO week, `this`, or `next`. Without a week, it uses this week ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | F06's `week_from_argument` and `NOT_A_WEEK` (choice 2). |
| `init` and `menu new` create a file only where none exists, and refuse otherwise (requirements 3). | `create_file` refuses an entry that is already there, and opens the new file in exclusive mode (3.3, [architecture 6](../../architecture.md#6-error-handling)). |
| `menu show` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus (PT01, [requirements 7.1](../../requirements.md#71-performance-targets)). | The performance target of 2.4, and choice 11. |

These rules hold for every interface below:

- `menu` imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus` from the package. Its row of architecture 3 allows them. It needs neither `units` nor `shopping` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `menu` reaches the disk only through the readers of F03, F04, and F06 and through `create_file`, all of which work through `datafile` (architecture 8). `menu new` writes only the week's menu file ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 1](../../architecture.md#1-context-and-constraints)), and `menu show` writes no file. Both write only to `context.out` and `context.err`. They read nothing of the outside world themselves, and they keep no state. The recipes that `menu show` reads live for one run only, so no module keeps a cache (architecture 8).
- A reader never raises for bad data, and `create_file` turns each `OSError` into a value ([architecture 6](../../architecture.md#6-error-handling)). Each command stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). `run` raises a `UsageError` only for a value of `WEEK` that is not a week, before it touches the disk or writes any output (F05 design, section 2). Any other exception that reaches `cli` is a bug.
- `MENU_NEW_COMMAND` and `MENU_SHOW_COMMAND` are frozen `Command` values (F05 design 2.5). `FileCreation` is a frozen dataclass with `slots=True`, and `FileOutcome` is an enum (architecture 8). They are helper values, as F08 added `Creation` and `CreationOutcome`.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- `recipe-menu menu show` has the performance target PT01 (choice 11). It reads each file that it needs once, and writes its output once, after the last file. `recipe-menu menu new` has none, because PT01 does not time it. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2, 2.4, and 3.3 give their rules.

1. **Two commands in one module, after `search` in the help.** Architecture 8 gives `menu new` and `menu show` the module `menu`. F11 adds `MENU_NEW_COMMAND` and `MENU_SHOW_COMMAND` to `COMMANDS` after `SEARCH_COMMAND`. So `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND)`, in the help's order of F05 design section 2. Both commands have `FolderUse.READ`, so `cli` stops them when the data folder is missing or the settings have an error (F05 design 2.5). Each declares the optional argument `WEEK`, as F05's design planned. So the help writes `menu new [WEEK]` and `menu show [WEEK]`, and `menu new [周]` and `menu show [周]` in Chinese. Neither declares an option. With these seven commands, the widest first cell of the help is `menu show [WEEK]`, of 16 columns, two more than `search WORD...`. So the second column of both tables starts after 21 columns in both languages, not after 19 as after F10, and the help has 20 lines. The help is then the two helps of the F05 prototype without the line of `shop` (2.1). `recipe-menu menu` alone gives F05's `INCOMPLETE_COMMAND`, `The commands that start with "menu" are "menu new" and "menu show".`, with `RUN_HELP_FOR_COMMANDS` and exit code 2. That is the text of F05 design 2.10, which F05-T23 checks with stand-in commands in the order of v0.1, and it stays true. Section 3 lists the tests of the real help, which all stay true.
2. **The week.** Each command gets its week with `week_from_argument(value, context.today)` (F06 design 2.7). `value` is the value of `WEEK`, or `None` when the line gives none. So an ISO week such as `2026-W47`, `this`, `next`, and no value for this week work in both commands, as requirements 3 asks. Any other text, such as `2026-W99`, `Next`, or the empty text, gives `UsageError(NOT_A_WEEK, None, week=value)`, and `cli` writes the message alone and exits with 2. The message says what to write, so it names no hint (ADR-0008, decision A), as the F11 prototype "A week without a menu" and v0.1-S15 show. `run` raises it before it touches the disk or writes any output. Every later line names the week as `str(week)`, such as `2026-W47` for `next`, so a line always names a file that you can find.
3. **The file that `menu new` writes.** It is the file of the F11 prototype "Create next week's menu": three comment lines, the key `week`, and one table for each day, Monday to Sunday, with an empty list for each meal of `context.settings.meals`, in the order of `Meal` (2.2). The first comment is the week and its `date_range` in English, such as `# 2026-W47: 16 to 22 November 2026`, as the menu of `example-data.md` starts. The other two comments show the two forms of a dish that `read_week_menu` reads (F06 design 2.9). The file is UTF-8 with no byte order mark and with LF line ends (architecture 5.1), and it holds only ASCII characters. Its bytes are the same in both languages. `--lang zh`, or `language = "zh"` in the settings, changes the lines of the output and not the file, as the files that `init` writes keep their English comments in both languages (F08 design, choice 6). Troy decides this point (point B below). `read_week_menu` reads the file with the same settings and gives a menu with every slot empty and no problem. So `check` reports nothing for it, and `menu show` shows `\u2014` for every meal (v0.1-S14). When the settings later name fewer meals, the empty lists of the other meals still give no problem (F06 design, choice 5).
4. **How `menu new` writes the file, and what it reads.** `datafile` writes every file (architecture 2, 3, and 8), so F11 adds `create_file` to it (3.3), as F08 design section 2 plans. `create_file` writes one new file and nothing else. It lists the file's folder and refuses when an entry is already there. Otherwise it opens the file in exclusive mode with `encoding="utf-8"` and `newline="\n"`, writes the text with one `write`, and closes it. It shares the way of writing and the failure messages of F08's `create_data_folder` (F08 design 3.2). `menu new` acts on its outcome:
   - **The file exists.** `create_file` gives `EXISTS`. `menu new` writes `ALREADY_EXISTS` with the full path of the entry that is there, such as `C:\Users\Troy\recipe-menu\menus\2026-W47.toml 已存在。没有做任何修改。` in the F11 prototype, and exits with 1. `create_file` never opens that entry, so the file keeps its bytes and its modification time (v0.1-S13). `menu new` reads no menu file, so a file for the week with an error, or an empty file, gets the same refusal. `check` and `menu show` report its error.
   - **A name that differs only in case.** On Windows, the file system does not tell `2026-w47.toml` from `2026-W47.toml`, so that file keeps any program from creating `2026-W47.toml` (F06 design section 2). Linux would create the second file. `create_file` treats both systems alike: an entry whose name equals the new name when the letters A to Z are changed to small letters counts as there (3.3). So on both systems, `menu new 2026-W47` writes `ALREADY_EXISTS` with `...\menus\2026-w47.toml` and exits with 1. `menu show 2026-W47` and `check` then report that file with F06's `NOT_A_WEEK_NAME`, which asks you to rename it. The same rule refuses `2026-W47.TOML`.
   - **`menus\` is missing, or is a file.** `init` creates the folder, and `menu new` creates only the menu file (requirements 3). So the listing fails, and `create_file` gives `FAILED` with the problem that `list_menu_weeks` and `check` report for the folder: `The folder is missing.` or `The folder cannot be read: it is a file.` (F04 design 3.1). `menu new` writes the three lines of a failure and exits with 1. Their first line names the folder by its full path, such as `C:\Users\Troy\recipe-menu\menus`, as option 1 of point C has it (below). You create the folder and run `menu new` again.
   - **Another `OSError`.** A listing that fails in another way, or an open, a write, or a close that fails, such as when access is denied or the disk is full, gives `FAILED`. Its problem has a listing message, F08's `FILE_WRITE_DENIED`, or F08's `FILE_WRITE_ERROR`. `menu new` writes three lines: the full path of the file or the folder, `str(context.folder.root / problem.file)`, then two spaces and the problem, then `CHANGED_NOTHING`. Architecture 6 lets `menu new` name a file that it could not write by its full path (ADR-0009). It does not cover the folder `menus\` that `menu new` could not list, and ADR-0009 section 5 keeps that scope on purpose. So naming the folder by its full path, option 1 of point C, needs a change to architecture 6, which Troy decides. After Troy decides, the Architect records the decision in architecture 6 and an ADR, in a `[docs]` PR before the F11 mock PR, as ADR-0009 recorded open question D of the F08 design. This design follows option 1, the recommendation. When the open had succeeded, `create_file` removes the half-written file first. When that removal fails too, such as when another program holds the file open, the third line is `LEFT_BEHIND`, which asks you to delete the file and run the command again.
   - **Ctrl+C.** `create_file` removes a half-written file in a `finally` block, and `cli` exits with 130 and writes nothing more (F05 design 2.10). A Ctrl+C after the file is closed leaves the whole file. As for `init`, a Ctrl+C inside `open`, after the system has created the file but before the call has recorded it, can leave an empty file (F08 design, choice 5). `menu show` and `check` then report its missing `week`, `menu new` refuses it, and you delete it.

   `menu new` reads no data file itself. `cli` reads the settings before it runs the command and stops at their first error (F05 design 2.10, step 9), and `menu new` takes the meals from `context.settings`. It reads neither the catalog, the recipes, nor a menu, and it does not check the other names in `menus\`. So a mistake in another file does not stop it.
5. **The output of `menu new`.** A new menu gives the three lines of the prototype on the output stream, with exit code 0 (2.2). They are `CREATED` with the full path of the new file and the week's `date_range`, then `EMPTY_DAYS` with the meals, then `NEXT_STEP`. The meals are `and_list` of the `Meal.label` of each meal of `context.settings.meals` (F02 design 2.6). That gives `lunch and dinner` and `午餐和晚餐` in the prototype, `breakfast, lunch, and dinner` in v0.1-S16, and `dinner` and `晚餐` for one meal, as in `7 days with dinner, all empty.`. A week always has seven days, so the line holds the number 7 and needs no `Plural`. A refusal and a failure go to the error stream with exit code 1 (architecture 6). The output follows `context.lang`. Troy decides the texts that no prototype shows (point A below).
6. **The line for a week with no menu.** `menu show` and F13's `shop` write the same line for a week with no menu file, `There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.`, as the F11 and F13 prototypes show. `shop` may not import `menu` (architecture 3). So F11 adds the line to `menus` as `NO_MENU` (3.1), as the Architect recommended in the F06 review (note 4). `menus` already exports `NOT_A_WEEK` for the same reason (F06 design, choice 8), and it owns the week menus that the line is about. The other way, `menu` and `shop` would each keep a copy, and a change to the line would have to be made twice. `{week}` is `str(week)`. The line goes to the error stream with exit code 1. A missing menu is a missing file, which the command checks (architecture 6, "A missing data folder, menu, or recipe", ADR-0008). Its Chinese text is new, for Troy (point A).
7. **What `menu show` reads, and where it stops.** `menu show` reads only the files that it needs: the settings in `cli`, the catalog, the menu, and only the recipes that the menu names (architecture 8). It reads them in the order of `show` (F09 design, choice 2): first the catalog and the listings, then the week that you asked for, then only what that week needs (2.4).
   - It reads the catalog with `read_catalog`, because `read_recipe` gives no recipe without one (F04 design 2.6).
   - It lists `recipes/` once with `list_recipe_ids` and passes the IDs to `read_week_menu` as a `frozenset` (F06 design, choice 4). It does not call `read_recipes`, which would list the folder again and parse every recipe. So it reports a problem of the listing once.
   - It lists `menus/` once with `list_menu_weeks` and looks for the week among the weeks that it gives (F06 design 2.8). An error of that listing stops `menu show`, also when it names another file, as an error of the listing of `recipes/` stops `show`. A missing `menus\` gives `menus` and `The folder is missing.`. On either system, `2026-w48.toml` gives `menus\2026-w48.toml` and `NOT_A_WEEK_NAME`, which asks you to rename the file, before `menu show 2026-W48` looks for the week. A week that the listing lacks gives `NO_MENU` and exit code 1 (choice 6).
   - It reads the week with `read_week_menu` and `context.settings` (F06 design 2.9). Because `menu show` has `FolderUse.READ`, those are the settings of the file.
   - It reads each recipe that a dish names with `read_recipe`, once, in the order of the first dish that names it: Monday to Sunday, the meals in the order of the settings, and the dishes in the file's order. A recipe that several dishes name is parsed once, and the run keeps it for its other dishes. A recipe that the menu does not name is not parsed, so an error in it does not stop `menu show`.

   The first error of each reader stops `menu show` with `first_error` and `stop_at_error`, which write the problem and `RUN_CHECK` and give 1 (F05 design 2.8), as the F11 prototype "A menu with a mistake" shows. `check` reads the same files with the same readers and arguments, so the error that stopped `menu show` is among the errors of `check` (F07 design, choice 8). `menu show` writes no warning, and a warning never changes the exit code, as F09 choice 3 has it (architecture 6). A name that lacks the chosen language shows the other language through `BiText.get`, as the F09 prototype "A missing language" shows for `show`.
8. **The table of `menu show`.** The table has a column for the day and one column for each meal of the menu, which are the meals of the settings. `DAY_HEADING` and each meal's `Meal.heading` are at the top (F05 design 2.1). Each day has one row, Monday to Sunday. Its first cell is `short_date` of the day's date, such as `Mon 16 Nov` and `周一 11月16日` (F06 design 2.2). A meal's cell holds one line for each dish of `WeekMenu.dishes`, in the file's order: the recipe's name in `context.lang`, a space, `\u00d7`, and the servings, such as `Mapo tofu \u00d72`. The same dish twice in one meal gives two such lines, and both count (choice 9). An empty meal shows `\u2014`. `format_table` puts the lines of a cell under each other, so a row takes as many lines as its fullest meal (F02 design 2.9). A name is written as the recipe file holds it, so the rules of `format_table` apply to it, such as a name with a line break, which takes two lines, as in `search` (F10 design 2.2). `\u00d7` and `\u2014` belong to no language, so they are symbols in the code, not messages, and these cells are the same in both languages (architecture 8). Each column is as wide as its widest line in the week's table, heading included, and the last column is not padded (F02 design 2.9). `menu show` passes no `min_widths`, because no other table has to line up with this one. So the prototype's English table has columns of 10 and 25 columns, from `Mon 16 Nov` and `Tomato and egg noodles \u00d72`. Its Chinese table has columns of 13 and 13, from `周一 11月16日` and `番茄鸡蛋面 \u00d72`. Another week gets the widths of its own cells, as in `search` (F10 design, choice 7).
9. **The count line.** The line under the table counts the meals that hold at least one dish, and all the dishes, as F06 design section 2 plans for F11 and F12. That count gives `4 meals, 9 dishes.` and `4 餐，9 道菜。` in the prototype, and `1 meal, 1 dish.` in v0.1-S16. The line then explains `\u00d7n`, as the prototype does. `MEAL_COUNT` and `DISH_COUNT` are `Plural` values (F02 design 2.4), so the English is right for one meal and one dish. A week with no dish, such as a new menu in v0.1-S14, shows the table with `\u2014` in every meal and then `NO_DISHES`, `The menu has no dishes yet.`, in place of the count line. No cell shows `\u00d7n` then, so the line does not explain it. No prototype shows these lines, so Troy decides them (point A).
10. **Numbers in messages.** The messages of `menu` show the number of meals and of dishes, which are counts of a menu's slots, and the dates of a week, which come from `IsoWeek`. The servings of a dish come from `read_week_menu`, which reads them with `read_servings` and its range of 1 to 100 (F05 design 3.1). They go into a cell through `str`, not through a message. A wrong week on the command line goes into `NOT_A_WEEK` as text. A problem in a file reaches the error stream only through `stop_at_error` or the failure lines of `menu new`, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `menu` meets F02's limit of 4,300 digits (F02 design 2.3).
11. **Speed.** PT01 asks that `menu show` of one PT01 week finish within 1 second on Troy's PC, the median of 5 runs (v0.1-S31). The week holds 63 dishes from 63 different recipes, three in each of breakfast, lunch, and dinner. `menu show` reads what `show` reads, plus one listing of `menus/` with 52 names, one menu file, and 62 more recipe files. F09's PT01 baselines on Troy's PC are a median of 0.153 s for `show` and 0.789 s for `list`, and F10's is 0.780 s for `search`. `show` reads the settings, a catalog of 300 ingredients, one listing of `recipes/`, and one recipe. `list` reads 999 more recipes, so one recipe costs about 0.64 ms, and 62 more cost about 0.04 s. In the F07 review, the 52 menus took about 0.08 s of `check`, so one menu costs about 2 ms. The table has 7 rows and 3 meal columns, about 2,000 characters, which `format_table` measures twice, and the count line is a few renders. So `menu show` should take about 0.2 s. This is an estimate from those times, not a measurement. The test plan can time it on a PT01 folder, as F09-T28 times `list`. `menu show` keeps the recipes that it read in a dictionary for one run, so a recipe that several dishes name is parsed once, and no module keeps a cache (architecture 8). `menu new` is not in PT01.
12. **Only the two commands are exported.** `menu` exports `MENU_NEW_COMMAND` and `MENU_SHOW_COMMAND` and nothing else. In v0.2, F14's `suggest` may import `menu` (architecture 3). F14's design adds to `menu` what the two modules share, such as the layout of the file of choice 3 or the cell of a dish, or keeps its own, as F09 left its shared parts to F10. So no name is exported before a feature uses it.

The v0.1 scenarios that run `menu new` or `menu show` hold with these choices:

- v0.1-S08: files with a byte order mark and CRLF line ends read the same (F03 design 2.3), so `menu show 2026-W47` prints the first output of "Show the week after you fill it".
- v0.1-S13: step 1 prints the three lines of "Create next week's menu" and writes the prototype's file byte for byte (choices 3 and 5). Step 2 prints the Chinese refusal and exits with 1, and the file keeps its bytes and modification time (choice 4). Steps 5 and 6 print the two tables of "Show the week after you fill it" (choices 8 and 9).
- v0.1-S14: `menu new` and `menu new next` create the files of this week and of next week, each with its own `week` line (choices 2 and 3). `menu show this` starts with `Menu for <T>,`, shows `\u2014` for every meal, and ends with `NO_DISHES` (choice 9). Steps 1 to 3 exit with 0.
- v0.1-S15: steps 1, 2, and 4 print `NO_MENU` with exit code 1, `NOT_A_WEEK` with exit code 2, and the three lines of "A menu with a mistake" with exit code 1 (choices 2, 6, and 7).
- v0.1-S16: `menu new 2026-W48` prints `7 days with breakfast, lunch, and dinner, all empty.` and writes the three meals for each day. `menu show 2026-W48` has the columns Day, Breakfast, Lunch, and Dinner, shows `Tomato and egg stir-fry \u00d73` at breakfast on Mon 23 Nov, with the 3 servings of the settings, and ends with `1 meal, 1 dish. \u00d7n: servings.`.
- v0.1-S23: `menu show 2026-W47` and `menu show 2026-W48` write no file.
- v0.1-S25: the Chinese table lines up, because `format_table` measures display width (F02 design 2.8).
- v0.1-S31: PT01 (choice 11). `menu show` prints 63 dishes in 21 cells.

Troy decides these three points. The design follows the recommendation of each.

- **A. New texts.** No prototype shows these texts. Each follows the wording of a text that a prototype shows. The recommendation is to accept them as 2.2, 2.4, and 3.1 give them.
  - The English refusal of `menu new`, for the prototype's Chinese line: `C:\Users\Troy\recipe-menu\menus\2026-W47.toml already exists. Nothing was changed.`.
  - The Chinese lines of a new menu: `已创建 C:\Users\Troy\recipe-menu\menus\2026-W47.toml，日期为 2026年11月16日至22日：`, `共 7 天，每天有午餐和晚餐，都还是空的。`, and `在各餐里填上菜谱 ID，然后运行“recipe-menu check”。`.
  - The Chinese line for a week with no menu: `2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。`.
  - The Chinese count line for one meal and one dish: `1 餐，1 道菜。\u00d7n：份数。`. The English line is the one that v0.1-S16 expects.
  - The line for a week with no dish: `The menu has no dishes yet.` and `这个菜单还没有菜。`.
  - The last line of a failure of `menu new`: `Nothing was changed.` and `没有做任何修改。`, the end of the prototype's refusal, or `LEFT_BEHIND` in both languages.
- **B. The language of a new menu file** (choice 3).
  - Option 1, recommended: the file has English comments in both languages, and `--lang` changes only the output.
  - Option 2: the comments follow the language of the command, such as `# 2026-W47：2026年11月16日至22日` and two Chinese lines that show how to write a dish.
  - The reason for option 1: the file's keys are English words in both languages, and `init` already writes the same comments in both languages (F08 design, choice 6). One text keeps the file the same however you made it, and v0.1-S13 checks it against the prototype.
- **C. The full path of a folder that `menu new` could not list** (choice 4 and 2.2). Architecture 6 lets `menu new` name a file that it could not write by its full path (ADR-0009), but not the folder `menus\` when its listing fails, and ADR-0009 section 5 keeps that scope on purpose. So naming the folder by its full path changes architecture 6, which Troy approves.
  - Option 1, recommended: the first line of every failure of `menu new` names its file or folder by its full path, `str(context.folder.root / problem.file)`, such as `C:\Users\Troy\recipe-menu\menus` above `  The folder is missing.`. Architecture 6 then names the folder that `menu new` could not list beside the file that it could not write.
  - Option 2: a failed listing names the folder as `menus`, as `check` and `list_menu_weeks` do, and only a failed open, write, or close names the file by its full path, such as `C:\Users\Troy\recipe-menu\menus\2026-W47.toml`. Architecture 6 stays as it is. Choice 4, the failure lines of 2.2, and the last run of the example of 2.2 change before the mock PR.
  - The reason for option 1: the reason of ADR-0009 holds here too. The line must say where on the disk the write failed, and every other line of `menu new` names a full path. With option 2, the first line of a failure would be a relative path for one cause and a full path for another.
  - After Troy picks option 1, the Architect records it in architecture 6 and an ADR, in a `[docs]` PR before the F11 mock PR, as ADR-0009 recorded open question D of the F08 design.

These later features are meant to build on F11. Their own designs decide the details.

- F13's `shop` gets its week as F11 does (choice 2), and writes `NO_MENU` of `menus` for a week with no menu file (choice 6). It can read its files in the order of `menu show` (choice 7), with the pantry after the catalog.
- F14's `menu suggest` may import `menu`, which exports only its two commands (choice 12).
- F15's `add` can write its new recipe with `create_file` as it is, which refuses `rice.toml` on both systems when `rice.TOML` or `Rice.toml` is there (3.3). A failure of `add` can name its file by its full path only after its own change to architecture 6 (ADR-0009, section 5).

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/menu/__init__.py`, `messages.py`, and one internal file for the two `run` functions, and the entries in `src/recipe_menu/cli/_commands.py`. It adds `NO_MENU` to `src/recipe_menu/menus/messages.py` and `src/recipe_menu/menus/__init__.py`. It adds `FileOutcome`, `FileCreation`, and `create_file` to a new internal file of `datafile`, such as `_new_file.py`, and to `src/recipe_menu/datafile/__init__.py`. It defines every message, both commands with all their fields, and `FileOutcome` with its members. Its `FileCreation` has the four fields without the checks of 3.2. Its `create_file` touches nothing and gives `FileCreation(FileOutcome.CREATED)`, and each `run` reads no file, writes nothing, raises nothing, and gives 0. So a new test fails against the mock (R09) when it checks an output, exit code 1, `NOT_A_WEEK` with exit code 2, the new file's bytes, a refusal or a failure, or an outcome or a check of `create_file`. These tests pass against the mock and break R09: a test that checks only the fields of a command, the help, a message such as `NO_MENU`, or exit code 0. So does a test of what `cli` does before it runs a command, such as a missing data folder, broken settings, `menu new 2026-W47 2026-W48`, `menu show --tag quick`, `menu show next --help`, or `recipe-menu menu`. So does a test that checks only that a command changes no file, as v0.1-S23 does for `menu show`, that a refused `menu new` keeps the file, or that a failure leaves nothing. So does a test of the values of `FileOutcome`, or of the defaults and the equality of a valid `FileCreation`. Each such test must also check something that the mock gets wrong, such as the output, the file, or the outcome. The mock changes 8 files, more than R03's 5, in about 350 lines by estimate, so its description gives a soft-limit reason. The reason is that the tests reach `create_file` and `NO_MENU` both directly and through the commands, so `menu`, `datafile`, and `menus` come in one stage, as in F08's mock. The implementation (PR 5) holds the two commands in internal files of `menu`, such as `_run.py`, `_new.py`, and `_show.py`, and `create_file` with the checks of `FileCreation` in the internal file of `datafile`. By estimate, it changes 4 files in about 450 lines, within R03 but close to its 500. `create_file` can import the internal helpers of `datafile`, as `_creation.py` does, and keep its doc comment short by pointing to the rules of `create_data_folder`. Changing `_creation.py` to share its removal code would add a fifth file to PR 5 and touch F08's code. If its doc comments take it past 500 lines, its description gives a soft-limit reason, so the Developer runs troy-check early.

### 2.1 `MENU_NEW_COMMAND`

- Module: menu
- Purpose: The description of the `menu new` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` creates the week's menu file and writes the output of 2.2.

Signature:

```python
MENU_NEW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "new")
#   help_line = MENU_NEW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("menu", "new")`. | None |
| `help_line` | `Message` | `MENU_NEW_HELP`: "Create an empty week menu." and "创建一个空的周菜单。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Turns the argument into a week, creates the week's menu file through `create_file`, and writes the output of 2.2. | Gives 0 or 1. Raises `UsageError` for a value that is not a week, before it touches the disk or writes any output. Raises nothing for bad data or for a failure on the disk. |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`, which is optional and does not repeat. `WEEK_ARGUMENT` is `WEEK` and `周`, the names in the F05 prototype's help. | So `cli` passes no value or one value (F05 design 2.5). |
| `options` | A tuple of `str` | `()`. `menu new` has no option of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `menu new` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.settings` for the meals, `context.out`, `context.err`, and `context.today`. |
| `arguments` | `Arguments` | What the command line gives `menu new` (F05 design 2.6). | `arguments.values` is `()` or holds one value, such as `("next",)`. It has no options. |

- Return value: `MENU_NEW_COMMAND`, a `Command`.
  - `MENU_NEW_COMMAND.usage` is `menu new [WEEK]` in English and `menu new [周]` in Chinese. So the help shows them, and a usage error quotes `recipe-menu menu new [WEEK]` or `recipe-menu menu new [周]`.
  - `MENU_NEW_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its lines in `context.lang`, and gives 0 or 1.

After F11, the help lists these commands and options, with the second column after 21 columns (choice 1). They are the lines of the F05 prototype's helps without the line of `shop`. In English:

```text
Commands:
  init               Create the data folder with example data.
  check              Check every data file for mistakes.
  list               List the recipes.
  show ID            Show one recipe.
  search WORD...     Find recipes by name, ingredient, or tag.
  menu new [WEEK]    Create an empty week menu.
  menu show [WEEK]   Show a week menu.

Options:
  --lang en|zh       The language of the output. Default: the settings, else English.
  --data FOLDER      The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version          Show the version.
  --help             Show this help.
```

In Chinese:

```text
命令：
  init               创建数据文件夹和示例数据。
  check              检查每个数据文件有没有错误。
  list               列出菜谱。
  show ID            查看一个菜谱。
  search 词...       按名称、食材或标签找菜谱。
  menu new [周]      创建一个空的周菜单。
  menu show [周]     查看一个周菜单。

选项：
  --lang en|zh       输出语言。默认：设置里的语言，否则英文。
  --data 文件夹      数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version          显示版本。
  --help             显示这份帮助。
```

Errors:

`run` turns the argument into a week before it touches the disk.

| Error | When |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | `week_from_argument` gives `None` for the value of `WEEK` (choice 2). |

- Side effects: Those of 2.2. `run` lists `menus/` and creates one file through `create_file`, and writes to `context.out` or `context.err`.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, which holds `menus/2026-W47.toml`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The first run speaks the language of the context and writes the meals of the context's settings. The help comes from `COMMANDS`, which holds the seven commands after F11. The call that raises touches no file and writes no line to either stream.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.menu import MENU_NEW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

assert MENU_NEW_COMMAND.words == ("menu", "new")
assert MENU_NEW_COMMAND.usage == BiText("menu new [WEEK]", "menu new [周]")
assert MENU_NEW_COMMAND.help_line.render(Lang.EN) == "Create an empty week menu."
assert MENU_NEW_COMMAND.help_line.render(Lang.ZH) == "创建一个空的周菜单。"
assert MENU_NEW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_NEW_COMMAND.options == ()
assert MENU_NEW_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
dinner_only = Settings(Lang.EN, (Meal.DINNER,), 2)
context = Context(Lang.ZH, folder, dinner_only, out, err, date(2026, 11, 17))
assert MENU_NEW_COMMAND.run(context, Arguments(("next",))) == 0
file = folder.menu_file("2026-W48")
assert out.getvalue().splitlines() == [
    f"已创建 {file}，日期为 2026年11月23日至29日：",
    "共 7 天，每天有晚餐，都还是空的。",
    "在各餐里填上菜谱 ID，然后运行“recipe-menu check”。",
]
assert err.getvalue() == ""
lines = [
    "# 2026-W48: 23 to 29 November 2026",
    '# A dish is a recipe ID, such as "tomato-egg",',
    '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
    'week = "2026-W48"',
]
for day in Day:
    lines += ["", f"[{day.value}]", "dinner = []"]
assert file.read_bytes() == "".join(f"{line}\n" for line in lines).encode("utf-8")

out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
existing = folder.menu_file("2026-W47")
assert MENU_NEW_COMMAND.run(context, Arguments(("2026-W47",))) == 1
refusal = f"{existing} already exists. Nothing was changed.\n"
assert (out.getvalue(), err.getvalue()) == ("", refusal)


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
assert len(english) == 20
assert english[9:12] == [
    "  search WORD...     Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]    Create an empty week menu.",
    "  menu show [WEEK]   Show a week menu.",
]
assert english[14].startswith("  --lang en|zh       The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[10:12] == [
    "  menu new [周]      创建一个空的周菜单。",
    "  menu show [周]     查看一个周菜单。",
]
assert chinese[15].startswith("  --data 文件夹      数据文件夹。")

MENU_NEW_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu menu new`

- Module: menu
- Purpose: The command that creates a week's menu file with every day and meal empty, and refuses when the file exists ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 3, and [4](../../requirements.md#4-features)). The F11 prototype "Create next week's menu" shows it.

Signature:

```text
recipe-menu menu new [WEEK] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `WEEK` | A text | The week of the menu: an ISO week such as `2026-W47`, `this`, or `next`. | Optional. Without it, this week. Any other text is a usage error (choice 2). |
| `--lang` | `en` or `zh` | The language of the output and of every message. It does not change the file (choice 3). | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `menu new`. | None |

`menu new` takes these steps, in order:

1. It turns the value of `WEEK` into a week with `week_from_argument(value, context.today)`. `value` is the value of the argument, or `None` when the line gives none. For a result of `None`, it raises `UsageError(NOT_A_WEEK, None, week=value)` (choice 2).
2. It builds the text of the file from the week and `context.settings.meals` (choice 3).
3. It calls `create_file(context.folder, path, text)` once, with `path = context.folder.menu_file(str(week))` (3.3).
4. It writes the lines of the outcome to their stream, and gives the exit code of the table below.

The text of the file is these lines, each ended by LF:

1. `# {week}: {dates}`, with `str(week)` and `week.date_range.get(Lang.EN)`, such as `# 2026-W53: 28 December 2026 to 3 January 2027`.
2. `# A dish is a recipe ID, such as "tomato-egg",`
3. `# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.`
4. `week = "{week}"`, with `str(week)`.
5. For each day of `Day`, Monday to Sunday: an empty line, then `[{day}]` with the day's value, then `{meal} = []` for each meal of `context.settings.meals`, in their order, with the meal's value.

So with the example settings, `recipe-menu menu new next` on Tuesday 10 November 2026 writes the file of the F11 prototype, `menus/2026-W47.toml`, in the same bytes in both languages:

```toml
# 2026-W47: 16 to 22 November 2026
# A dish is a recipe ID, such as "tomato-egg",
# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.
week = "2026-W47"

[monday]
lunch = []
dinner = []

[tuesday]
lunch = []
dinner = []

[wednesday]
lunch = []
dinner = []

[thursday]
lunch = []
dinner = []

[friday]
lunch = []
dinner = []

[saturday]
lunch = []
dinner = []

[sunday]
lunch = []
dinner = []
```

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `create_file` gave `CREATED`. | The output stream: the three lines of a new menu. |
| 1 | It gave `EXISTS`. | The error stream: `ALREADY_EXISTS`. Nothing goes to the output stream. |
| 1 | It gave `FAILED`. | The error stream: the three lines of a failure. Nothing goes to the output stream. |
| 2 | The value of `WEEK` is not a week. | The error stream: `NOT_A_WEEK`, which `cli` writes, with no hint. Nothing goes to the output stream. |

A new menu gives these lines, each ended by a line break:

1. `CREATED`, with `file` and `dates`.
2. `EMPTY_DAYS`, with `meals`.
3. `NEXT_STEP`.

A refusal is one line: `ALREADY_EXISTS`, with `file` set to the entry that is there (choice 4).

A failure is three lines. The first line is the full path of the problem's file, `str(context.folder.root / problem.file)`. For a failed listing, that is the folder, such as `C:\Users\Troy\recipe-menu\menus`. This follows option 1 of point C, which Troy decides (choice 4). Under option 2, a failed listing gives `str(problem.file)`, such as `menus`, and only a failed open, write, or close gives the full path. The second line is two spaces and `problem.text(context.lang)`. The third line is `CHANGED_NOTHING` when the result's `left` is empty, and `LEFT_BEHIND` with `week` otherwise. In this case on Windows, you may read `menus\`, but not create a file in it:

```text
PS> recipe-menu menu new next
C:\Users\Troy\recipe-menu\menus\2026-W47.toml
  The file cannot be written: access is denied.
Nothing was changed.
PS> $LASTEXITCODE
1
```

The messages of `menu new` are these:

| Name | English | Chinese |
| --- | --- | --- |
| `MENU_NEW_HELP` | `Create an empty week menu.` | `创建一个空的周菜单。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `CREATED` | `Created {file} for {dates}:` | `已创建 {file}，日期为 {dates}：` |
| `EMPTY_DAYS` | `7 days with {meals}, all empty.` | `共 7 天，每天有{meals}，都还是空的。` |
| `NEXT_STEP` | `Add recipe IDs to the meals, then run "recipe-menu check".` | `在各餐里填上菜谱 ID，然后运行“recipe-menu check”。` |
| `ALREADY_EXISTS` | `{file} already exists. Nothing was changed.` | `{file} 已存在。没有做任何修改。` |
| `CHANGED_NOTHING` | `Nothing was changed.` | `没有做任何修改。` |
| `LEFT_BEHIND` | `menu new could not remove the file that it created. Delete it, then run "recipe-menu menu new {week}" again.` | `menu new 没能删除它创建的文件。请删除这个文件，然后再运行“recipe-menu menu new {week}”。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `file` | A full path. In `CREATED`, `str(path)`, the new file. In `ALREADY_EXISTS`, `str(creation.existing)`, the entry that is there. `context.folder.root` is absolute (F05 design 2.4). |
| `dates` | `week.date_range`, as a `BiText`: `16 to 22 November 2026` and `2026年11月16日至22日`. |
| `meals` | `and_list` of the `Meal.label` of each meal of `context.settings.meals`: `lunch and dinner` and `午餐和晚餐`. |
| `week` | `str(week)`, such as `2026-W47`. |

With these messages, the lines of the F11 prototype follow, such as `7 days with lunch and dinner, all empty.` and `C:\Users\Troy\recipe-menu\menus\2026-W47.toml 已存在。没有做任何修改。`.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `menu new` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `NOT_A_WEEK` and no hint: `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | The value of `WEEK` is not a week (step 1). |
| Exit code 1, with `ALREADY_EXISTS` on the error stream | An entry with the file's name, or with a name that differs from it only in the case of A to Z, is in `menus/` (choice 4). Every entry keeps its bytes and modification time. |
| Exit code 1, with the three lines of a failure on the error stream | The listing of `menus/` failed, or an `OSError` stopped the file (choice 4). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `menu new` has `FolderUse.READ`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `Unexpected argument "2026-W48". Write "recipe-menu menu new [WEEK]".` | The line names two weeks. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"menu new" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. `create_file` removes a half-written file, and `cli` writes nothing more (choice 4). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). After a wrong week, `menu new` touches nothing. Otherwise it calls `create_file` once. That call lists `menus/` and creates the menu file, or creates nothing for a refusal or a failed listing, and removes a half-written file after a failure (3.3). `menu new` reads no data file. It writes its lines to the output stream or the error stream.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. The example first empties `menus/`, as the F11 prototype does, so the first two runs give the two outputs of "Create next week's menu", as v0.1-S13 runs them. The later runs show v0.1-S16 and the cases of choice 4. The last run, with no `menus\`, names the folder by its full path, as option 1 of point C has it.

```python
import io
import shutil
from datetime import date

from recipe_menu.cli import main
from recipe_menu.menus import Day


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


def menu_text(week: str, dates: str, meals: list[str]) -> bytes:
    lines = [
        f"# {week}: {dates}",
        '# A dish is a recipe ID, such as "tomato-egg",',
        '# or a recipe ID with servings, such as { recipe = "tomato-egg", servings = 4 }.',
        f'week = "{week}"',
    ]
    for day in Day:
        lines += ["", f"[{day.value}]", *(f"{meal} = []" for meal in meals)]
    return "".join(f"{line}\n" for line in lines).encode("utf-8")


for path in folder.menus.iterdir():
    path.unlink()
file = folder.menu_file("2026-W47")
assert run("menu", "new", "next") == (
    0,
    [
        f"Created {file} for 16 to 22 November 2026:",
        "7 days with lunch and dinner, all empty.",
        'Add recipe IDs to the meals, then run "recipe-menu check".',
    ],
    [],
)
assert file.read_bytes() == menu_text("2026-W47", "16 to 22 November 2026", ["lunch", "dinner"])
made = file.stat().st_mtime_ns
exists = [f"{file} 已存在。没有做任何修改。"]
assert run("menu", "new", "next", "--lang", "zh") == (1, [], exists)
assert file.stat().st_mtime_ns == made

folder.settings.write_text('meals = ["breakfast", "lunch", "dinner"]\n', encoding="utf-8")
code, out, err = run("menu", "new", "2026-W48")
assert (code, out[1], err) == (0, "7 days with breakfast, lunch, and dinner, all empty.", [])
every_meal = ["breakfast", "lunch", "dinner"]
week48 = menu_text("2026-W48", "23 to 29 November 2026", every_meal)
assert folder.menu_file("2026-W48").read_bytes() == week48

wrong_case = folder.menus / "2026-w49.toml"
wrong_case.write_text("", encoding="utf-8")
refusal = f"{wrong_case} already exists. Nothing was changed."
assert run("menu", "new", "2026-W49") == (1, [], [refusal])
assert sorted(path.name for path in folder.menus.iterdir()) == [
    "2026-W47.toml",
    "2026-W48.toml",
    "2026-w49.toml",
]

week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "new", "2026-W99") == (2, [], [week_error])

shutil.rmtree(folder.menus)
missing = [str(folder.menus), "  The folder is missing.", "Nothing was changed."]
assert run("menu", "new", "2026-W50") == (1, [], missing)
assert not folder.menus.exists()
```

### 2.3 `MENU_SHOW_COMMAND`

- Module: menu
- Purpose: The description of the `menu show` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` writes the week of 2.4.

Signature:

```python
MENU_SHOW_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "show")
#   help_line = MENU_SHOW_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("menu", "show")`. | None |
| `help_line` | `Message` | `MENU_SHOW_HELP`: "Show a week menu." and "查看一个周菜单。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Turns the argument into a week, reads the catalog, the listings, the week's menu, and the recipes that it names, and writes the week of 2.4. | Gives 0 or 1. Raises `UsageError` for a value that is not a week, before it reads a file or writes any output. Raises nothing for bad data. |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`, with the `WEEK_ARGUMENT` of 2.2. | So `cli` passes no value or one value (F05 design 2.5). |
| `options` | A tuple of `str` | `()`. `menu show` has no option of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `menu show` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.settings` for `read_week_menu`, `context.out`, `context.err`, and `context.today`. |
| `arguments` | `Arguments` | What the command line gives `menu show` (F05 design 2.6). | `arguments.values` is `()` or holds one value, such as `("2026-W47",)`. It has no options. |

- Return value: `MENU_SHOW_COMMAND`, a `Command`.
  - `MENU_SHOW_COMMAND.usage` is `menu show [WEEK]` in English and `menu show [周]` in Chinese. So the help shows them, and a usage error quotes `recipe-menu menu show [WEEK]` or `recipe-menu menu show [周]`.
  - `MENU_SHOW_COMMAND.run(context, arguments)` takes the steps of 2.4, writes its output in `context.lang`, and gives 0 or 1.

Errors:

`run` turns the argument into a week before it reads a file.

| Error | When |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | `week_from_argument` gives `None` for the value of `WEEK` (choice 2). |

- Side effects: Those of 2.4. `run` reads the catalog, two listings, one menu file, and the recipes that the menu names through the readers of F03, F04, and F06, writes to `context.out` or `context.err`, and writes no file.
- Performance target: None. PT01 times `recipe-menu menu show` (2.4) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`. The context holds the default settings, which are the settings of the example, and the output follows `context.lang`. The run gives the first output of the F11 prototype "Show the week after you fill it". `row` writes one line of its table, whose columns are 10 and 25 columns wide (choice 8). Every character of the English table takes one column, so `str` padding gives the same lines as `format_table`. The call that raises reads no file and writes no line to either stream.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.commands.menu import MENU_SHOW_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert MENU_SHOW_COMMAND.words == ("menu", "show")
assert MENU_SHOW_COMMAND.usage == BiText("menu show [WEEK]", "menu show [周]")
assert MENU_SHOW_COMMAND.help_line.render(Lang.EN) == "Show a week menu."
assert MENU_SHOW_COMMAND.help_line.render(Lang.ZH) == "查看一个周菜单。"
assert MENU_SHOW_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_SHOW_COMMAND.options == ()
assert MENU_SHOW_COMMAND.folder is FolderUse.READ

DASH, TIMES = "\u2014", "\u00d7"


def row(day: str, lunch: str, dinner: str) -> str:
    return f"{day:10}   {lunch:25}   {dinner}".rstrip()


out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert MENU_SHOW_COMMAND.run(context, Arguments(("next",))) == 0
assert out.getvalue().splitlines() == [
    "Menu for 2026-W47, 16 to 22 November 2026",
    "",
    row("Day", "Lunch", "Dinner"),
    row("Mon 16 Nov", DASH, f"Tomato and egg stir-fry {TIMES}2"),
    row("", "", f"Stir-fried choy sum {TIMES}2"),
    row("", "", f"Steamed rice {TIMES}2"),
    row("Tue 17 Nov", DASH, f"Mapo tofu {TIMES}2"),
    row("", "", f"Steamed rice {TIMES}2"),
    row("Wed 18 Nov", DASH, DASH),
    row("Thu 19 Nov", DASH, DASH),
    row("Fri 20 Nov", DASH, DASH),
    row("Sat 21 Nov", f"Tomato and egg noodles {TIMES}2", DASH),
    row("Sun 22 Nov", DASH, f"Cola chicken wings {TIMES}4"),
    row("", "", f"Stir-fried choy sum {TIMES}4"),
    row("", "", f"Steamed rice {TIMES}4"),
    "",
    f"4 meals, 9 dishes. {TIMES}n: servings.",
]
assert err.getvalue() == ""

MENU_SHOW_COMMAND.run(context, Arguments(("this week",)))  # raises UsageError
```

### 2.4 `recipe-menu menu show`

- Module: menu
- Purpose: The command that prints a week menu as a table of days and meals, with each dish and its servings ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 3, and [4](../../requirements.md#4-features)). The F11 prototype "Show the week after you fill it", "A week without a menu", and "A menu with a mistake" show it.

Signature:

```text
recipe-menu menu show [WEEK] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `WEEK` | A text | The week to show: an ISO week such as `2026-W47`, `this`, or `next`. | Optional. Without it, this week. Any other text is a usage error (choice 2). |
| `--lang` | `en` or `zh` | The language of the output and of every message. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `menu show`. | None |

`menu show` takes these steps, in order. Step 1 reads no file. Each step that reads a file uses what the earlier steps gave, and each one that finds an error stops the command (choice 7).

1. It turns the value of `WEEK` into a week with `week_from_argument(value, context.today)`. For a result of `None`, it raises `UsageError(NOT_A_WEEK, None, week=value)` (choice 2).
2. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `menu show` gives `stop_at_error(context, error)` for the first one.
3. `list_recipe_ids(context.folder)` gives `ids` and their problems (F04 design 2.5). With an error among the problems, `menu show` stops at the first one with `stop_at_error`.
4. `list_menu_weeks(context.folder)` gives `weeks` and their problems (F06 design 2.8). With an error among the problems, `menu show` stops at the first one with `stop_at_error`.
5. When `weeks` does not hold the week, `menu show` writes `NO_MENU` with `week=str(week)` to the error stream and gives 1 (choice 6).
6. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` gives `menu` and its problems (F06 design 2.9). With an error among the problems, `menu show` stops at the first one with `stop_at_error`.
7. For each recipe ID that a dish of `menu` names, once, in the order of the first dish that names it, `read_recipe(context.folder, catalog, recipe_id)` gives the recipe and its problems (F04 design 2.6). The order of the dishes is Monday to Sunday, the meals in the order of `menu.meals`, and the dishes in the file's order. With an error among the problems, `menu show` stops at the first one with `stop_at_error`.
8. It writes the output below to the output stream and gives 0.

The warnings of steps 2, 3, and 7 change nothing (choice 7).

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `menu show` wrote the week, also a week with no dish. | The output stream: the heading, the table, and the count line. |
| 1 | The week has no menu file. | The error stream: `NO_MENU`. Nothing goes to the output stream. |
| 1 | A file has an error. | The error stream: the three lines of `stop_at_error`. Nothing goes to the output stream. |
| 2 | The value of `WEEK` is not a week. | The error stream: `NOT_A_WEEK`, which `cli` writes, with no hint. Nothing goes to the output stream. |

The output is these lines, in this order, each ended by a line break:

1. `MENU_HEADING`, with `week` and `dates`.
2. An empty line.
3. The lines of `format_table(rows)`, with no indent, the default gap of 3, and no `min_widths` (F02 design 2.9, choice 8).
4. An empty line.
5. `COUNT_LINE`, with `meals` and `dishes`, when a slot of `menu` holds a dish. `NO_DISHES` when none does (choice 9).

`rows` is the heading row, and then one row for each day of `Day`, Monday to Sunday. `day_date` is the date of the day, `week.dates[i]` for the day `list(Day)[i]` (F06 design 2.1).

| Column | Heading | Cell |
| --- | --- | --- |
| Day | `DAY_HEADING` | `short_date(day_date).get(context.lang)`, such as `Mon 16 Nov` and `周一 11月16日`. |
| One for each meal of `menu.meals`, in their order | `meal.heading.get(context.lang)`, such as `Lunch` and `午餐` | `\u2014` when `menu.dishes(day, meal)` is empty. Otherwise one line for each dish of `menu.dishes(day, meal)`, in their order, joined by `\n`. A dish's line is `f"{name} \u00d7{dish.servings}"`, where `name` is `recipe.name.get(context.lang)` of the recipe that step 7 read for `dish.recipe_id`. |

The messages of `menu show` are these. `MEAL_COUNT` and `DISH_COUNT` are `Plural` values (F02 design 2.4), each picked by its `count`. Their form "for more" is the form for every count other than 1. `menu show` also uses `WEEK_ARGUMENT` of 2.2, and `NO_MENU` of `menus` (3.1).

| Name | English | Chinese |
| --- | --- | --- |
| `MENU_SHOW_HELP` | `Show a week menu.` | `查看一个周菜单。` |
| `MENU_HEADING` | `Menu for {week}, {dates}` | `{week} 菜单，{dates}` |
| `DAY_HEADING` | `Day` | `日期` |
| `MEAL_COUNT`, for one | `{count} meal` | `{count} 餐` |
| `MEAL_COUNT`, for more | `{count} meals` | `{count} 餐` |
| `DISH_COUNT`, for one | `{count} dish` | `{count} 道菜` |
| `DISH_COUNT`, for more | `{count} dishes` | `{count} 道菜` |
| `COUNT_LINE` | `{meals}, {dishes}. \u00d7n: servings.` | `{meals}，{dishes}。\u00d7n：份数。` |
| `NO_DISHES` | `The menu has no dishes yet.` | `这个菜单还没有菜。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `week` | `str(week)`, such as `2026-W47`. |
| `dates` | `week.date_range`, as a `BiText`. |
| `meals` | `MEAL_COUNT`, picked by the number of slots of `menu` that hold at least one dish, with `count` set to it, as a `BiText`. |
| `dishes` | `DISH_COUNT`, picked by the number of dishes in all the slots of `menu`, with `count` set to it, as a `BiText`. |
| `count` | The number of each `Plural`. |

With these messages, the lines of the F11 prototype follow in both languages, such as `Menu for 2026-W47, 16 to 22 November 2026`, `2026-W47 菜单，2026年11月16日至22日`, and `4 餐，9 道菜。\u00d7n：份数。`.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `menu show` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `NOT_A_WEEK` and no hint: `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | The value of `WEEK` is not a week (step 1). |
| Exit code 1, with `NO_MENU` on the error stream: `There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | The listing of `menus/` holds no file for the week (step 5). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream, such as `menus\2026-W47.toml, Monday dinner`, `  Unknown recipe "tomato-eggs".`, and `RUN_CHECK` | The catalog, the listing of `recipes/`, the listing of `menus/`, the week's menu file, or a recipe file that the menu names has an error (steps 2 to 4, 6, and 7). |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `menu show` has `FolderUse.READ`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `Unexpected argument "2026-W48". Write "recipe-menu menu show [WEEK]".` | The line names two weeks. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"menu show" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. Nothing more is written (F05 design 2.10). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `menu show` then reads `catalog.toml` once, lists `recipes/` once, lists `menus/` once, reads the week's menu file once, and reads each recipe file that a dish names once, all through the readers of F03, F04, and F06. After a wrong week, it reads no file. After an error or a week with no menu, it reads nothing more. It reads neither `pantry.toml`, another menu, nor a recipe that the menu does not name. It writes to the output stream or the error stream. It writes no file, so every file and folder keeps its bytes and modification time (v0.1-S23).
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. The first run gives the second output of the F11 prototype "Show the week after you fill it", of which the example checks some lines. The next runs give "A week without a menu". Then an error in a recipe that the menu does not name changes nothing, and a missing English name shows the Chinese one. An error in a recipe that the menu names stops `menu show`, and so does the mistake of "A menu with a mistake", whose file comes first. A new menu shows `\u2014` in every meal, and a missing `menus\` stops `menu show`.

```python
import io
import shutil
from datetime import date
from pathlib import Path

from recipe_menu.cli import main
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, short_date


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


def edit(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


code, out, err = run("menu", "show", "2026-W47", "--lang", "zh")
assert (code, err) == (0, [])
assert out[:5] == [
    "2026-W47 菜单，2026年11月16日至22日",
    "",
    "日期            午餐            晚餐",
    "周一 11月16日   \u2014               番茄炒蛋 \u00d72",
    " " * 32 + "清炒菜心 \u00d72",
]
assert out[11] == "周六 11月21日   番茄鸡蛋面 \u00d72   \u2014"
assert out[-2:] == ["", "4 餐，9 道菜。\u00d7n：份数。"]

no_menu = ['There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.']
assert run("menu", "show", "2026-W48") == (1, [], no_menu)
no_menu_zh = ["2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。"]
assert run("menu", "show", "2026-W48", "--lang", "zh") == (1, [], no_menu_zh)
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "show", "2026-W99") == (2, [], [week_error])

edit(folder.recipe_file("red-braised-pork"), "servings = 2", "servings = 0")
edit(folder.recipe_file("rice"), ', en = "Steamed rice"', "")
code, out, err = run("menu", "show", "2026-W47")
assert (code, err) == (0, [])
assert out[5] == " " * 41 + "米饭 \u00d72"
assert out[-1] == "4 meals, 9 dishes. \u00d7n: servings."

edit(folder.recipe_file("mapo-tofu"), "郫县", "")
mapo = Path("recipes", "mapo-tofu.toml")
assert run("menu", "show", "2026-W47") == (
    1,
    [],
    [
        f"{mapo}, ingredient 3",
        '  Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
        'Run "recipe-menu check" to see every problem.',
    ],
)
edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
week47 = Path("menus", "2026-W47.toml")
assert run("menu", "show", "next") == (
    1,
    [],
    [
        f"{week47}, Monday dinner",
        '  Unknown recipe "tomato-eggs".',
        'Run "recipe-menu check" to see every problem.',
    ],
)

assert run("menu", "new", "2026-W48")[0] == 0
days = [short_date(day).get(Lang.EN) for day in IsoWeek(2026, 48).dates]
assert run("menu", "show", "2026-W48") == (
    0,
    [
        "Menu for 2026-W48, 23 to 29 November 2026",
        "",
        "Day          Lunch   Dinner",
        *(f"{day}   \u2014       \u2014" for day in days),
        "",
        "The menu has no dishes yet.",
    ],
    [],
)

shutil.rmtree(folder.menus)
assert run("menu", "show", "2026-W48") == (
    1,
    [],
    ["menus", "  The folder is missing.", 'Run "recipe-menu check" to see every problem.'],
)
```

## 3. Changes to existing interfaces

F11 adds names to the interfaces of two implemented modules. F06's `menus` exports the message `NO_MENU` (3.1). `datafile`, which F03 created and F08 gave its first write, exports `FileOutcome` and `FileCreation` (3.2) and `create_file` (3.3), the write that architecture 3 and F08 design section 2 plan for `menu new`. No exported name of F01 to F10 changes its signature or its behavior, so their tests pass unchanged. The requirements do not change, so no `[docs]` PR approves these additions. The Architect reviews them in this design, as it reviewed F10's `matching_form` and the names that F04, F05, and F08 added to `datafile` in their section 3.

F11 also adds two entries to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is internal to `cli` and which architecture 4 gives each command feature. With them, the help of the real `recipe-menu` lists `menu new` and `menu show`, and the second column of its tables starts after 21 columns instead of 19 (choice 1). The tests that run the real `COMMANDS` check only lines and columns that stay true:

- F05-T48 checks the first and the last line of the Chinese help, and F05-T49 checks no line of the help.
- F07-T17 checks that the line of `check` ends with its text, and that the text starts at the column where the text of `--lang en|zh` starts.
- F08-T14 checks the same of the line of `init`, and that the line of `check` follows it.
- F09-T01 checks that the lines of `list` and `show` follow the line of `check`, and that their texts start at that same column. F09-T19 and F09-T25 check that `list --help` and `show ... --help` give the same help as `--help`.
- F10-T01 checks that the line of `search` follows the line of `show ID`, starts with `  search WORD... `, and has its text at that same column. F10-T11, F10-T15, and F10-T16 check that `search` with `--help` gives the same help as `--help`, and that it holds the line of `search`.

Each of these holds when the column moves from 19 to 21 and two lines follow the line of `search`. F07-T01, F08-T14, F09-T01, and F10-T01 also compare a whole help, but each passes `main` its own commands, which F11 does not change. No test runs `menu` with the real `COMMANDS`. The tests of F05 and F06 that run `menu new`, `menu show`, or `menu` alone pass `main` their own commands. So `recipe-menu menu` changes from `Unknown command "menu".` to F05's `INCOMPLETE_COMMAND` (choice 1), and no test changes.

F11 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, `and_list`, and `format_table`.
- F03's `DataFolder`, `Problem`, `Severity`, `Catalog`, and `read_catalog`, and the conditions of `SYSTEM_ERROR` for the value `reason` (F03 design 2.3).
- F04's table of listing problems of `list_toml_files` and its four messages, which stay internal to `datafile` (F04 design 3.1), and `Recipe`, `list_recipe_ids`, and `read_recipe` in `recipes`.
- F05's `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, and `stop_at_error` in `app`, `Meal` with `label` and `heading` and `Settings` in `settings`, and `COMMANDS` in `cli`.
- F06's `Day`, `IsoWeek` with `dates` and `date_range`, `NOT_A_WEEK`, `WeekMenu`, `list_menu_weeks`, `read_week_menu`, `short_date`, and `week_from_argument`.
- F08's messages `FILE_WRITE_DENIED` and `FILE_WRITE_ERROR`, which stay internal to `datafile`, and the way `create_data_folder` writes and removes a file (F08 design 3.2). `create_file` may share that code, and `create_data_folder` keeps its behavior.

### 3.1 `NO_MENU`

- Module: menus
- Purpose: The line for a week that has no menu file, which `menu show` writes and F13's `shop` will write too (choice 6). `src/recipe_menu/menus/messages.py` defines it beside `NOT_A_WEEK`, and `src/recipe_menu/menus/__init__.py` imports it and lists it in `__all__`. Every other message of `menus` stays internal, and the module doc comment of `messages.py` names both exported messages.

Signature:

```python
NO_MENU: Final[Message]
```

Parameters: None

- Return value: None. `NO_MENU` is this `Message`, with the one placeholder `week`, an ISO week as `str(IsoWeek)` writes it. Its English text is the line of the F11 and F13 prototypes.

| Name | English | Chinese |
| --- | --- | --- |
| `NO_MENU` | `There is no menu for {week}. Run "recipe-menu menu new {week}" to create it.` | `{week} 没有菜单。运行“recipe-menu menu new {week}”创建它。` |

The message says what to run next, as architecture 6 asks for a missing menu, so it is one line.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.menus import NO_MENU

assert NO_MENU.placeholders == frozenset({"week"})
text = NO_MENU.render(Lang.EN, week="2026-W48")
assert text == 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
chinese = NO_MENU.render(Lang.ZH, week="2026-W48")
assert chinese == "2026-W48 没有菜单。运行“recipe-menu menu new 2026-W48”创建它。"
```

### 3.2 `FileOutcome` and `FileCreation`

- Module: datafile
- Purpose: The result of `create_file` (3.3): whether it created the file, found an entry already there, or failed, and what it could not remove after a failure. `menu new` picks its output by the outcome (2.2). F08's `CreationOutcome` and `Creation` describe a whole data folder, and these two describe one file.

Signature:

```python
class FileOutcome(Enum):
    CREATED = "created"
    EXISTS = "exists"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class FileCreation:
    outcome: FileOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
    existing: Path | None = None
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `outcome` | `FileOutcome` | What happened, by the table below. | None |
| `problem` | `Problem` or `None` | What stopped the call, as a problem. | A `Problem` with `Severity.ERROR` for `FAILED`, and `None` for the other outcomes. |
| `left` | A tuple of `Path` | The file, as a full path, when the call created it and could not remove it after the failure. | Empty or one path for `FAILED`. Empty for the other outcomes. |
| `existing` | `Path` or `None` | The entry that is already there, as a full path, such as `C:\Users\Troy\recipe-menu\menus\2026-w47.toml`. | A `Path` for `EXISTS`, and `None` for the other outcomes. |

| Member | When | `problem` | `left` | `existing` |
| --- | --- | --- | --- | --- |
| `CREATED` | The call created the file and wrote its text. | `None` | Empty | `None` |
| `EXISTS` | An entry with the file's name, or with a name that differs from it only in the case of A to Z, is in the file's folder. The call created nothing. | `None` | Empty | The entry |
| `FAILED` | The listing of the folder failed, or an `OSError` stopped the file. The call removed the file when it had created it. | The error | The file when it could not be removed, else empty | `None` |

- Return value: A `FileOutcome` member, or a `FileCreation`. Two values of `FileCreation` are equal when their four fields are equal, and a `FileCreation` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `outcome` is `FAILED` and `problem` is `None`, or `outcome` is another member and `problem` is not `None`. |
| `ValueError` | `problem` has `Severity.WARNING`. |
| `ValueError` | `left` holds more than one path, or it is not empty and `outcome` is not `FAILED`. |
| `ValueError` | `outcome` is `EXISTS` and `existing` is `None`, or `outcome` is another member and `existing` is not `None`. |

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import FileCreation, FileOutcome, Problem
from recipe_menu.text import Message

DENIED = Message("Access is denied.", "没有访问权限。")
assert [outcome.value for outcome in FileOutcome] == ["created", "exists", "failed"]
created = FileCreation(FileOutcome.CREATED)
assert (created.problem, created.left, created.existing) == (None, (), None)
entry = Path.cwd() / "menus" / "2026-w47.toml"
assert FileCreation(FileOutcome.EXISTS, existing=entry).existing == entry
problem = Problem.error(Path("menus", "2026-W47.toml"), None, DENIED)
left = (Path.cwd() / "menus" / "2026-W47.toml",)
failed = FileCreation(FileOutcome.FAILED, problem, left)
assert failed == FileCreation(FileOutcome.FAILED, problem, left)

FileCreation(FileOutcome.FAILED)  # raises ValueError
FileCreation(FileOutcome.EXISTS)  # raises ValueError
FileCreation(FileOutcome.CREATED, problem)  # raises ValueError
FileCreation(FileOutcome.CREATED, left=left)  # raises ValueError
FileCreation(FileOutcome.FAILED, problem, left + left)  # raises ValueError
warning = Problem.warning(problem.file, None, DENIED)
FileCreation(FileOutcome.FAILED, warning)  # raises ValueError
```

### 3.3 `create_file`

- Module: datafile
- Purpose: Creates one new file with its text, and never overwrites an entry (choice 4, [architecture 6](../../architecture.md#6-error-handling)). It refuses when the file's folder already holds an entry with the file's name, also one that differs only in the case of A to Z, so Windows and Linux give the same result. It opens the file in exclusive mode, and removes it after a failure or an interruption. `menu new` calls it (2.2), and F15's `add` can call it.

Signature:

```python
def create_file(folder: DataFolder, path: Path, text: str) -> FileCreation: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `path` | `Path` | The file to create, such as `folder.menu_file("2026-W47")`. | Inside `folder.root`, and not `folder.root`. |
| `text` | `str` | The text of the file. | UTF-8 can encode it. |

- Return value: A `FileCreation` (3.2).

`create_file` works in these steps:

1. It checks `path` with `folder.relative(path)` and encodes `text` as UTF-8, before it touches the disk. A wrong argument raises an error of the Errors table.
2. It lists `path.parent` with `Path.iterdir`. A listing that fails with an `OSError` gives `FAILED`. Its problem has the file `folder.relative(path.parent)`, such as `menus`, no place, and the message of the table of listing problems of `list_toml_files` (F04 design 3.1): `FOLDER_IS_FILE`, `FOLDER_MISSING`, `FOLDER_ACCESS_DENIED`, or `FOLDER_SYSTEM_ERROR`. So the call reports a missing `menus\` as `list_menu_weeks` does.
3. An entry whose name equals `path.name`, when each ASCII capital letter from A to Z in both names is changed to its small letter, gives `EXISTS`. Its `existing` is `path.parent` joined with the entry's name. When several entries match, as on Linux, the entry with exactly the name counts, and otherwise the first match in the order of `sorted`. An entry of any kind counts: a file, a folder, or a link. The call opens no entry, so each one keeps its bytes and its modification time.
4. It opens `path` in exclusive mode, `"x"`, with `encoding="utf-8"` and `newline="\n"` (architecture 8). It writes the text with one `write` call on the file that the open gave, also when the text is empty, and closes the file. So the file holds the UTF-8 bytes of the text, with no byte order mark and with the line ends of the text. Then the call gives `FileCreation(FileOutcome.CREATED)`.

The open, the write, and the close can raise an `OSError`. The first row of this table that applies gives the result. `relative` is `folder.relative(path)`. `reason` is the error's `strerror`, or the name of the error's class when `strerror` is `None` or empty, as for `SYSTEM_ERROR` (F03 design 2.3).

| Error | Result |
| --- | --- |
| `FileExistsError` from the open | `EXISTS`, with `existing` set to `path`. An entry appeared after the listing, and the call created nothing. |
| `PermissionError` | `FAILED`, with `FILE_WRITE_DENIED` at `relative` and no place. |
| Any other `OSError` | `FAILED`, with `FILE_WRITE_ERROR` and `reason` at `relative` and no place. |

A file counts as created from the moment that its open succeeds. After an `OSError` from the write or the close, the call removes the file with `Path.unlink` before it gives `FAILED`. A removal that fails with an `OSError` puts the full path of the file in `left`. Any other exception after the open, such as `KeyboardInterrupt` for Ctrl+C or the exception of a bug, runs the same removal in a `finally` block and then goes on, so the call gives no result. No `except` clause catches more than `OSError` (architecture 6 and 8). The call reaches the disk only through `Path.iterdir`, `open` in mode `"x"`, and `Path.unlink`, as `create_data_folder` does, and it may share that code with `create_data_folder` (F08 design 3.2).

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `path` is not inside `folder.root`, or it is `folder.root`. The check runs before the call touches the disk. |
| `UnicodeEncodeError` | `text` holds a character that UTF-8 cannot encode, such as a lone surrogate. The check runs before the call touches the disk. |

- Side effects: Lists `path.parent` once. Creates `path` and writes its text, or creates nothing for `EXISTS` and after a failed listing. After a failure or an interruption, removes the file that it created. It reads no file.
- Performance target: None

Example:

In this example, `tmp` is an empty temporary folder. The data folder has `menus/` but no `recipes/`. The failure uses a file name of 300 characters, which both systems reject.

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder, FileOutcome, create_file
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "recipe-menu")
folder.menus.mkdir(parents=True)
file = folder.menu_file("2026-W47")
created = create_file(folder, file, 'week = "2026-W47"\n')
assert created.outcome is FileOutcome.CREATED
assert file.read_bytes() == b'week = "2026-W47"\n'

again = create_file(folder, file, "")
assert (again.outcome, again.existing) == (FileOutcome.EXISTS, file)
assert file.read_bytes() == b'week = "2026-W47"\n'
wrong_case = folder.menus / "2026-w48.toml"
wrong_case.write_text("", encoding="utf-8")
taken = create_file(folder, folder.menu_file("2026-W48"), "")
assert (taken.outcome, taken.existing) == (FileOutcome.EXISTS, wrong_case)

missing = create_file(folder, folder.recipe_file("rice"), "servings = 2\n")
assert missing.outcome is FileOutcome.FAILED
assert missing.problem is not None
assert (missing.problem.file, missing.problem.place) == (Path("recipes"), None)
assert missing.problem.text(Lang.EN) == "The folder is missing."
assert missing.left == ()

name = "x" * 300 + ".toml"
failed = create_file(folder, folder.menus / name, "\n")
assert failed.outcome is FileOutcome.FAILED
assert failed.problem is not None
assert failed.problem.file == Path("menus", name)
assert failed.problem.text(Lang.EN).startswith("The file cannot be written. The system says: ")
assert failed.left == ()
names = sorted(entry.name for entry in folder.menus.iterdir())
assert names == ["2026-W47.toml", "2026-w48.toml"]

create_file(folder, tmp / "elsewhere.toml", "")  # raises ValueError
create_file(folder, folder.root, "")  # raises ValueError
create_file(folder, file, "\udc80")  # raises UnicodeEncodeError
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `menu` is the module of architecture 3: the folder `src/recipe_menu/commands/menu/`, whose `__init__.py` lists only `MENU_NEW_COMMAND` and `MENU_SHOW_COMMAND` in `__all__`, with its messages in its own `messages.py` (architecture 8, choices 1 and 12). It imports `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus`, which its row allows, and the Architect's model of sections 2 and 3 needed no other module. The only change in `cli` is the two entries after `SEARCH_COMMAND` in `COMMANDS` (architecture 4). The additions of section 3 are the right way to share what they hold. Architecture 2, 3, and 6 give the writing of files to `datafile`, so `create_file` belongs there. `create_data_folder` cannot do the job, because it refuses a data folder that holds an entry. A new internal file keeps `_creation.py`, which has 393 lines, within R06. `menus` owns the week menus and already exports `NOT_A_WEEK` for the commands, so `NO_MENU` belongs beside it, where F13's `shop`, which may not import `menu`, can reach it. In `text` or `app`, the line about a week menu would sit in a module that knows nothing of week menus. `FileOutcome` is an enum, and `FileCreation` is a frozen dataclass with `slots=True` and a tuple field (architecture 8). They are helper values, as F08's `CreationOutcome` and `Creation` are, which architecture 5.2 does not list either. The new file follows architecture 5.1: the keys of `example-data.md`, UTF-8 with no byte order mark, and LF line ends. `menu show` reads what architecture 8 allows: the settings in `cli`, the catalog, two listings, one menu, and each recipe that the menu names, once (choice 7). `menu new` reads no data file (choice 4). Neither command keeps state beyond one run. |
| Follows the error handling and naming conventions | Pass | Finding 1 of round 1 is settled. Point C gives Troy the case of a failed listing of `menus\`, with the two options, the reason for option 1, and what each option changes: option 1 changes architecture 6, and option 2 changes choice 4, the failure lines of 2.2, and the last run of its example before the mock PR. Choice 4 no longer says that architecture 6 covers the folder. It says that option 1 needs a change to architecture 6, which Troy decides, and that the Architect records the decision in architecture 6 and an ADR, in a `[docs]` PR before the F11 mock PR, as ADR-0009 recorded open question D of the F08 design. The bullet for a missing `menus\` and the failure lines of 2.2 point to option 1, and the text before the example of 2.2 says that its last run follows it. What the design says of architecture 6 and ADR-0009 matches them: architecture 6 lets `menu new` name only a file that it could not write by its full path, and ADR-0009 section 5 asks any other case for its own change to architecture 6. The Architect recommends option 1, for the reason that point C gives. Note 1, not blocking (choice 4): the sentence "After Troy decides, the Architect records the decision in architecture 6 and an ADR" holds only for option 1, because option 2 leaves architecture 6 as it is. Point C says "After Troy picks option 1", and choice 4 can say the same when the design records Troy's decisions. The rest of the item passes as in round 1. Exit codes follow architecture 1 and 6. `menu new` gives 0 for a new menu, and 1 for a refusal or a failure. `menu show` gives 0 for a week, also one with no dish, and 1 for `NO_MENU` or for the first error of a reader, through `first_error` and `stop_at_error`. Both raise `UsageError(NOT_A_WEEK, None, week=value)` before they touch the disk, and `cli` turns it into 2 with no hint (ADR-0008, decision A). `create_file` turns each `OSError` into a value, catches nothing wider, opens in exclusive mode, and removes a half-written file in a `finally` block. So a Ctrl+C leaves no half-written file, apart from the moment inside `open` that F08 design choice 5 already names. The output goes to `context.out`, and every refusal, failure, and error goes to `context.err`. Names follow architecture 8: UPPER_SNAKE `Message` and `Plural` constants, lists from `and_list`, plurals from `Plural`, and the table from `format_table`. Choice 10 holds. Point A: the Architect agrees with the recommendation. Each new text is a `Message` or a `Plural` in both languages, and each follows the wording of a line that a prototype shows. Point B: the Architect agrees with option 1. One text keeps the file the same however you made it, it matches the English keys and the files that `init` writes (F08 design, choice 6), and v0.1-S13 checks it byte for byte. |
| Does not duplicate an existing interface | Pass | `menu` calls `week_from_argument`, `NOT_A_WEEK`, `list_menu_weeks`, `read_week_menu`, `short_date`, `IsoWeek.date_range`, `read_catalog`, `list_recipe_ids`, `read_recipe`, `first_error`, `stop_at_error`, `and_list`, `Plural.pick`, and `format_table`, and builds none of them again. Inside `datafile`, `create_file` reuses F04's listing problems and F08's `FILE_WRITE_DENIED` and `FILE_WRITE_ERROR`. So a missing `menus\` reads the same in `menu new`, `menu show`, and `check`. It does not repeat `create_data_folder`, which creates a whole data folder, all or nothing. `NO_MENU` in `menus` keeps one copy of the line for `menu show` and F13's `shop`, as note 4 of the F06 review asked. `CHANGED_NOTHING` and `LEFT_BEHIND` reuse the names of two internal messages of `init` with other texts. Architecture 8 keeps each module's messages in its own `messages.py`, and `menu` may not import `init`. The three failure lines repeat a few lines of `init`. `problem_lines` of `app` writes the relative path, so a copy of those few lines costs less than a new export from `app`. |
| Depends only on features earlier in the order | Pass | F11 uses `lang` and `text` from F01 and F02, `datafile` and `catalog` from F03, `recipes` from F04, `app`, `settings`, and `cli` from F05, and `menus` from F06. Inside `datafile`, it uses F08's write messages and the way F08 removes a file. All of these features come before F11 and pass their tests on main. F05 is the hard dependency of the F11 row, and F02 and F06 are its soft ones. F08 is not in the row, but it reaches F11 only through the shared module `datafile`, as architecture 4 allows for shared modules. The plans for F13, F14, and F15 leave the details to their designs, so they bind no later design. F11 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. `menu new` must write a file that `read_week_menu` reads with no problem and with every slot empty (F06 design, section 2). The model checked that for all seven sets of meals, read with those settings, with the default settings, and with no settings. `create_file` reports a failed listing through the same internal function as `list_toml_files`, so its problem equals that of `list_menu_weeks` and `check`. Adding the two commands moves the help's second column from 19 to 21 columns, which section 3 names, and the test run confirms that every test of the real help stays true. `NO_MENU` names `menu new` only as text, as `RUN_CHECK` in `text` names `check`. Choice 7 stops `menu show` at the first error of the listing of `menus/`, also for another file. That matches `show`, which stops at an error of the listing of `recipes/` (F09 design), and it keeps Windows and Linux alike: on Windows, reading `2026-W48` with `2026-w48.toml` in the folder would open that file, and the listing error stops `menu show` first. Point 2(b) of the brief: the order of `create_file` is right. The listing gives the same refusal on both systems and names the entry that is there. The exclusive open is what guarantees that no entry is overwritten. Through its `FileExistsError` row, it also catches an entry that appears after the listing, and a name that the file system folds more widely than A to Z. In the other order, `create_file` would create the file on Linux, find the other name only afterwards, and have to remove the file. The rule for A to Z fits both callers, because ISO weeks and recipe IDs hold only ASCII characters (`is_recipe_id`). One listing with that rule took 0.43 ms for 52 entries and 5.3 ms for 1,000 entries on Troy's PC, which is small next to the start of the process. Notes 1 and 2 of round 1 are taken: 3.3 no longer names `folder.relative`, and the bullet for F15 says that a failure of `add` can name its file by its full path only after its own change to architecture 6 (ADR-0009, section 5). |
| Changes an implemented interface only through the change flow | Pass | Section 3 adds `NO_MENU` to `menus`, and `FileOutcome`, `FileCreation`, and `create_file` to `datafile`. No name of F01 to F10 changes its signature or its behavior, and the requirements do not change, so no `[docs]` PR is needed. The Architect reviews the additions here, as it did for F10's `matching_form` and the names that F04, F05, and F08 added to `datafile`. In round 1, with the model in a copy of the branch, the whole test suite gives 483 passed and 3 skipped, the 3 skips being the Linux-only cases of main. So F05-T48, F05-T49, F07-T17, F08-T14, F09-T01, F09-T19, F09-T25, F10-T01, F10-T11, F10-T15, F10-T16, and every other test stay true, as section 3 says. The split into a mock and an implementation is right. The mock changes 8 files: the three files of `menu`, `cli/_commands.py`, `menus/messages.py`, `menus/__init__.py`, the new internal file of `datafile`, and `datafile/__init__.py`. Its reason for the soft limit holds, as it did for F08's mock: the tests reach `create_file` and `NO_MENU` both directly and through the commands, so all three modules must import in the mock. The mock's stubs make every new test of an output, a file, an outcome, or a check of 3.2 fail (R09), and the design names the tests that would pass against the mock. The implementation changes only internal files of `menu` and `datafile`, so its 4 files fit R03. Note 3 of round 1 is taken into the mock plan, which now says how PR 5 can stay within R03. Option 1 of point C changes architecture 6 but no implemented interface: the `Problem` keeps its file relative to the data folder, and `problem_lines`, `stop_at_error`, and every reader keep the relative path, as ADR-0009 section 5 says for `init`. Its `[docs]` PR is the change flow for the architecture (troy-mode requirements 5.7). |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | Finding 1, under "Follows the error handling and naming conventions": choice 4 names the `menus` folder by its full path, which architecture 6 and ADR-0009 do not cover, so Troy must decide the case. Notes 1 to 3 do not block. The 18 code blocks of each file equal those of its mirror, and `ruff format --check` with ruff 0.17.4 and the project's settings reports the 12 `python` blocks of each file formatted. The Architect built a model of sections 2 and 3 in a copy of the branch and ran the 7 examples on fresh copies of `tests/data/example/`, with Python 3.13.18 on Windows. Every assertion and all 11 `# raises` hold, and no call that raises touches a file or writes to a stream. Further runs of the model matched these outputs in full: the help of 20 lines in both languages, with the second column after 21 columns, equal to the helps of the F05 prototype without the line of `shop`; the three lines of a new menu, with the bytes of the new file equal to the prototype's file and to the `toml` block of 2.2; the Chinese refusal, after which the file keeps its bytes and modification time; both tables of "Show the week after you fill it", with columns of 10 and 25 and of 13 and 13; "A week without a menu"; and "A menu with a mistake". They also matched v0.1-S08 with a byte order mark and CRLF line ends; v0.1-S14 on 30 December 2026, with `# 2026-W53: 28 December 2026 to 3 January 2027` and `NO_DISHES` in both languages; v0.1-S16, with `1 meal, 1 dish.` and its Chinese line; and v0.1-S23. `menu show` read the files in the order of choice 7, each recipe once. The model also gave the three lines of a denied open, removed the file after a failed write, wrote `LEFT_BEHIND` after a failed removal, and exited with 130 after a Ctrl+C during the write, with no file left. On a PT01 folder from `tests/pt01_support.py`, `menu show 2026-W26` printed 63 dishes in 21 cells and `21 meals, 63 dishes.`. Two sets of 5 runs gave medians of 0.262 s and 0.247 s for `menu show`, against 0.231 s and 0.203 s for `show recipe-0500` in the same sets. Other test runs loaded the PC at the time, and `list` took about 1.0 s against its baseline of 0.789 s. So choice 11's estimate of about 0.2 s holds, far below 1 second. | Changes requested. The Interface Designer adds point C and changes choice 4, as finding 1 asks. Notes 1 to 3 are optional. The Architect agrees with the recommendations of points A and B, which Troy decides when Troy approves this design. |
| 2 | Version 0.2 settles finding 1 under "Follows the error handling and naming conventions": point C gives Troy the case of a failed listing of `menus\`, and choice 4, the failure lines of 2.2, and the text before its example point to option 1, as finding 1 asked. Notes 1 to 3 of round 1 are taken. Note 1 of this round does not block. `git diff 5caabb4 HEAD` changes the same 10 places in each file and nothing in a code block or in section 4: the version in the header, two bullets of choice 4, the count of the points that Troy decides, point C, the bullet for F15, the mock plan, the failure lines of 2.2, the text before its example, 3.3, and the change log. The 18 code blocks of each file equal those of round 1 and those of its mirror, each file still holds the same 36 Unicode escapes, and the two files have the same headings and tables. `ruff format --check` with ruff 0.17.4 and the project's settings reports both files and the 12 `python` blocks of each formatted. No code block or output line changed, so the runs of the Architect's model in round 1 still hold. | Approved. Troy decides points A, B, and C when Troy approves this design, and the Architect agrees with the recommendation of each. After Troy picks option 1 of point C, the Architect writes the change to architecture 6 and its ADR in a `[docs]` PR before the F11 mock PR, as `[docs] Change the architecture for F08` landed between F08's PR 1 and PR 2. If Troy picks option 2, the Interface Designer changes choice 4 and 2.2 before the mock PR, and architecture 6 stays as it is. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-14 | First draft. |
| 0.2 | 2026-11-14 | Answers round 1 of the Architect's review. Point C gives Troy the case of a failed listing of `menus\`: option 1, recommended, names every failure of `menu new` by its full path, which needs a change to architecture 6 and an ADR before the F11 mock PR, and option 2 names the folder as `menus`. Choice 4, the failure lines of 2.2, and the text before its example say so, and follow option 1. 3.3 no longer suggests that `folder.relative` reaches the disk. The bullet for F15 says that a failure of `add` needs its own change to architecture 6 to name its file by its full path. The mock plan says how PR 5 can stay within R03. No output line or code block changes. |
| 1.0 | 2026-11-14 | Approved by Troy. |
