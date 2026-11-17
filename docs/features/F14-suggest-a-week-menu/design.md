---
troy-doc: "F14-design"
lang: "en"
version: "1.0"
updated: "2026-11-17"
status: "Approved by Troy on 2026-11-17"
mirror: "design.zh-CN.md"
---

# F14 Suggest a week menu: interface design

## 1. Feature

- ID and name: F14 Suggest a week menu
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F06, F11

## 2. Interfaces

F14 builds the command module `suggest` in `src/recipe_menu/commands/suggest/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.suggest` exports one name, `MENU_SUGGEST_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu menu suggest` (2.2). Its messages live in `src/recipe_menu/commands/suggest/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F14 adds `MENU_SUGGEST_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `MENU_SHOW_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). F14 also adds to four implemented modules what architecture 5.1 and 5.2 plan for it (section 3): the setting `dishes` to `settings` (3.1 and 3.2), the random generator to `Context` in `app` (3.3) and to `main` in `cli` (3.4), and to `datafile` a read of a file's text and a parse of a TOML text (3.5 and 3.6). The F14 prototype `docs/prototypes/F14-suggest.md` shows the command, and the F05 prototype says that v0.2 adds its line to the help.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F14 gives |
| --- | --- |
| `recipe-menu menu suggest [WEEK]` fills each empty meal of the week's menu file with recipes chosen at random ([requirements 4](../../requirements.md#4-features)). | `recipe-menu menu suggest` (2.2), with `MENU_SUGGEST_COMMAND` (2.1). It chooses with `Context.random` (3.3, choice 6) and changes the file by the rules of choice 7. |
| Each empty meal gets the number of dishes that the settings give for that meal, 1 by default. | The key `dishes` of `settings.toml`, which `read_settings` reads into `Settings.dishes` (3.1 and 3.2, choice 5, point B). |
| No recipe appears twice in the week. | Choice 6: the candidates are the recipes that the week does not hold, and `random.sample` takes each of them at most once. |
| `--tag` limits the choice to recipes with that tag. | The option `--tag`, which `Catalog.find_tag` reads in either language, as for `list --tag` (choice 4). |
| When no recipe is left to choose, the remaining meals stay empty, and the command says how many. | The output of choice 9, and point C for a meal that needs more dishes than are left. |
| Filled meals and the rest of the file stay as they are. | Choice 7: only the `[]` of each meal that gets dishes changes, and a missing line of a meal or table of a day is added. A file saved with CR LF line ends or a byte order mark keeps the text of every line, and gets LF line ends and no mark. A check of the new text, and `replace_file`, which changes the file in one step (choice 8). |
| To swap a dish, empty its meal and run `menu suggest` again. | `SWAP_HINT` (choice 9). The meal that you emptied is empty again, and its old recipe can come back (choice 6). |
| A command that takes a week accepts an ISO week, `this`, or `next`. Without a week, it uses this week ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | F06's `week_from_argument` and `NOT_A_WEEK` (choice 2). |

These rules hold for every interface below:

- `suggest` imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus` from the package. Its row of architecture 3 allows them. It needs neither `units`, `shopping`, nor `menu` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `suggest` reaches the disk only through the readers of F03, F04, and F06, through `read_file_text` (3.5), and through `replace_file` (F13 design 3.1), all of which work through `datafile` (architecture 8). It writes only the week's menu file, and the temporary file `menus/<week>.toml.tmp` of `replace_file` while it writes that file ([requirements 4](../../requirements.md#4-features), [architecture 5.1](../../architecture.md#51-data-files)). It writes only to `context.out` and `context.err`. It reads nothing of the outside world itself: its random choice comes from `context.random`, which `cli` makes (3.3 and 3.4). It keeps no state, and the recipes that it reads live for one run only.
- A reader never raises for bad data, and `replace_file` turns each `OSError` into a value ([architecture 6](../../architecture.md#6-error-handling)). `menu suggest` stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). `run` raises a `UsageError` only for a value of `WEEK` that is not a week, before it touches the disk or writes any output (F05 design, section 2). Any other exception that reaches `cli` is a bug.
- `MENU_SUGGEST_COMMAND` is a frozen `Command` value (F05 design 2.5). F14 adds no value type. `Settings.dishes` is a tuple of three `int` values, and `Context.random` is a `random.Random` (section 3).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F14 interface has a performance target. PT01 does not time `menu suggest` ([requirements 7.1](../../requirements.md#71-performance-targets)). Choice 11 says how long it takes, and how F14 keeps the start of every other command fast. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 and section 3 give their rules.

1. **One command, after `menu show` in the help.** F14 adds `MENU_SUGGEST_COMMAND` to `COMMANDS` after `MENU_SHOW_COMMAND`. So `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`. The menu commands stay together, and the commands of v0.1 keep their order. `menu suggest` has `FolderUse.READ`, so `cli` stops it when the data folder is missing or the settings have an error (F05 design 2.5), as v0.2-S14 expects. It declares the optional argument `WEEK` and the option `--tag`. So the help writes `menu suggest [WEEK]` and `menu suggest [周]`, of 19 and 17 columns. `menu suggest [WEEK]` becomes the widest first cell of the help, 3 columns wider than `menu show [WEEK]`. So the second column of both tables starts after 24 columns in both languages, not after 21, and every line of the two tables gets 3 more spaces. The help has 22 lines (2.1). `recipe-menu menu` alone gives F05's `INCOMPLETE_COMMAND`, which now reads `The commands that start with "menu" are "menu new", "menu show", and "menu suggest".`, with `RUN_HELP_FOR_COMMANDS` and exit code 2. Section 3 names the tests that these two changes break.
2. **The week.** `menu suggest` gets its week as F11's commands and `shop` do (F11 design, choice 2): `week_from_argument(value, context.today)` (F06 design 2.7), where `value` is the value of `WEEK`, or `None` when the line gives none. Any other text than an ISO week, `this`, or `next`, such as `2026-W99`, gives `UsageError(NOT_A_WEEK, None, week=value)`, and `cli` writes the message alone and exits with 2 (ADR-0008, decision A), as v0.2-S08 expects. `run` raises it before it touches the disk or writes any output. Every later line names the week as `str(week)`, such as `2026-W48` for `next`.
3. **What `menu suggest` reads, and where it stops.** It reads only the files that it needs, in this order (2.2): the settings in `cli`, the catalog, the listing of `recipes/`, the listing of `menus/`, the week's menu, the text of the menu file, and then each recipe that the week does not hold. It reads neither the pantry nor another menu.
   - It reads the catalog with `read_catalog`, because `find_tag` and `read_recipe` need it (F03 design 2.6, F04 design 2.6). It looks for the tag of `--tag` right after the catalog, as `list` does, so an unknown tag stops it before it reads anything else (choice 4).
   - It lists `recipes/` with `list_recipe_ids` and `menus/` with `list_menu_weeks`, and reads the week with `read_week_menu` and `context.settings`, in the order and with the stops of `menu show` (F11 design, choice 7). A week that the listing lacks gives `NO_MENU` of `menus` (F11 design 3.1) on the error stream and exit code 1, as v0.2-S07 and v0.2-S08 expect.
   - A week with no empty meal stops it there with `NO_EMPTY_MEAL` and exit code 0 (choice 9). So a full week costs no further read.
   - It reads the text of the menu file with `read_file_text` (3.5) and finds the place of each empty meal in it (choice 7). A file that it cannot fill stops it there with `CANNOT_FILL`, before it reads a recipe.
   - It reads each recipe that no dish of the week names with `read_recipe`, once, in the order of the IDs, also without `--tag`. So it chooses only recipes that read with no error. A recipe with an error stops `menu suggest`, as it stops `list` (F09 design, choice 2), and `check` reports it. A recipe that the week holds is no candidate, so it is not read.

   The first error of each reader stops `menu suggest` with `first_error` and `stop_at_error`, which write the problem and `RUN_CHECK` and give 1 (F05 design 2.8), as the F11 prototype "A menu with a mistake" shows and v0.2-S08 expects. `check` reads the same files with the same readers and arguments, so the error that stopped `menu suggest` is among the errors of `check` (F07 design, choice 8). `menu suggest` writes no warning, and a warning never changes the exit code (architecture 6). After an error, `NO_MENU`, an unknown tag, or `CANNOT_FILL`, it writes no file.
4. **The tag.** `menu suggest` finds the tag of `--tag` with `Catalog.find_tag` (F03 design 2.6), as `list` does (F09 design, choice 4). So the value matches a tag's name in either language: whitespace at both ends does not count, and case counts only for the letters A to Z. When `find_tag` finds no tag, `menu suggest` writes `UNKNOWN_TAG`, or `NO_TAGS` for a catalog with no tags, to the error stream and exits with 1, with the texts of `list`, as v0.2-S08 expects. `suggest` may not import `browse` (architecture 3), and `browse` exports only its commands. So `suggest` keeps its own copy of the two messages, with the same texts, as `shop` keeps copies of messages of `menu` (F13 design, choice 3). The output names the tag by its name in the chosen language, as `list` does, so `--tag 快手` and `--tag quick` give the same output (v0.2-S02).
5. **The dishes of a meal.** The settings give the number of dishes of each meal with the key `dishes`, a table with a number for each meal that needs one, such as `dishes = { dinner = 2 }` (point B). A meal that the table leaves out gets 1, as requirements 4 says. A number is a whole number from 1 to 10: a meal rarely has more dishes, and a typing mistake such as `20` would put 140 dishes in a week. `read_settings` reads the key into `Settings.dishes`, and `menu suggest` asks `Settings.dishes_for(meal)` (3.1 and 3.2). A wrong value is an error of the settings, which stops every command and which `check` reports, as for the other keys. `init` keeps writing its settings file without the key, so the files of `init`, `example-data.md`, and the v0.1 scenarios stay as they are. For v0.2-S06, the setting that gives dinner 2 dishes is the line `dishes = { dinner = 2 }`.
6. **The random choice.**
   - The empty meals are the slots of the menu that hold no dish, in the order of `WeekMenu.slots`: Monday to Sunday, and in a day in the order of the settings' meals (F06 design 2.6). The kept meals are the slots that hold a dish.
   - The candidates are the IDs of `list_recipe_ids` that no dish of the week names, in the order of the IDs, whose recipe `read_recipe` read with no error, and, with `--tag`, whose recipe's `tags` hold the tag.
   - `need` is the sum of `context.settings.dishes_for(slot.meal)` over the empty meals. `menu suggest` calls `context.random.sample(candidates, min(need, len(candidates)))` once, and calls `context.random` for nothing else. The result is `chosen`. So no recipe comes twice in `chosen`, and none of them is in the week yet. Two runs with the same seed and the same files choose the same recipes, so a test fixes the choice with `main(random=Random(seed))` (3.4), and `Random(seed).sample` gives the recipes that a run chooses.
   - The empty meals take their dishes in their order, each from the front of what is left of `chosen`. A meal takes `dishes_for(meal)` recipes when that many are left. Otherwise it stays empty, and the next meals go on (point C). So when too few recipes are there, the first empty meals of the week get dishes, and the last ones stay empty.
   - A new dish is its recipe ID alone, with no servings. So it gets `settings.servings` when F06's reader reads it, as a dish that you write without servings does ([requirements 3](../../requirements.md#3-how-users-interact-with-it)).
   - The requirements forbid only a recipe twice in the week. A dish that you emptied is no longer in the week, so it is a candidate again, and a swap can give it back (v0.2-S03). `menu suggest` cannot know what an empty meal held before.
   - A week that you wrote may hold a recipe twice, as the example week holds `rice` three times. `menu suggest` changes no meal that holds a dish, so it keeps such a repeat, and it adds none.
7. **How `menu suggest` changes the file.** ADR-0002 leaves F14 two ways: rewrite only the lines of empty meals, or use a library that keeps a file's layout, such as tomlkit. tomlkit would be a third-party package at run time, against ADR-0001, and it would need the Architect's approval (R16). So `menu suggest` changes lines of the text with the standard library (2.2):
   - It reads the text with `read_file_text` and turns each CR LF into LF. The new file is UTF-8 with no byte order mark and with LF line ends, as architecture 5.1 says for every file that the tool writes. So a file that you saved with CR LF line ends or a byte order mark keeps the text of every line, and only its line ends and its mark change.
   - A meal on a line such as `dinner = []` gets its dishes in place of the `[]`, such as `dinner = ["mapo-tofu", "rice"]`. The rest of the line, a comment included, stays.
   - A meal that the table of its day leaves out gets a new line right after the line `[monday]` of its day.
   - A day that the file leaves out gets its table at the end of the file: an empty line, the line `[tuesday]`, and a line for each meal of the day that gets dishes.
   - A meal that stays empty gets no new line, and neither does a day none of whose meals gets a dish.
   - Every other line keeps its text and its order, comments and blank lines included. A new line moves the lines after it down.
   - Then `menu suggest` checks the new text with `parse_toml` (3.6): its table must equal the table of the old text with the new dishes in their meals. When the check fails, `menu suggest` writes nothing and stops with `CANNOT_FILL`, which asks for the layout that `menu new` writes. So a file that these rules cannot change, such as one that writes a day as a table in braces, `monday = { dinner = [] }`, is refused and never broken. The files that `menu new` writes, and the layout of `example-data.md`, always pass. The refused layout that you are likeliest to meet is a meal whose list you wrote over several lines and then emptied by deleting its dishes, which leaves `dinner = [` and `]` on two lines, as Sunday dinner of the example week would. It stops `menu suggest` in step 8 of 2.2 with `CANNOT_FILL`, which asks for `dinner = []`.
8. **How `menu suggest` saves the file.** `datafile` writes every file (architecture 2, 3, and 8). `create_file` refuses an entry that is there, so `menu suggest` writes with `replace_file` as it is, which F13 design section 2 plans for F14. `replace_file` writes `menus/<week>.toml.tmp` and moves it over the menu file in one step. So the file holds its old text or its new text, never a part, and a failure or Ctrl+C leaves the old file as it was (F13 design 3.1). `list_menu_weeks` lists only names that end with `.toml`, so the temporary file never counts as a menu (F06 design 2.8). `menu suggest` builds the path only as `context.folder.menu_file(str(week))`, after `list_menu_weeks` gave the week, so the name is always an ISO week (F03 design 2.1). `replace_file` checks a path with `folder.relative(path)`, which compares the text of the paths, so a path such as `root/menus/../../x.toml` would pass its check. `menu suggest` never builds such a path. It writes the file only when a meal gets a dish. A week with no empty meal, or a run that fills no meal, writes no file, and the file keeps its bytes and its modification time (v0.2-S03). `menu suggest` acts on the result:
   - **`CREATED`.** It writes the output of choice 9 to the output stream and gives 0.
   - **`FAILED`.** It writes three lines to the error stream and gives 1, and nothing goes to the output stream. The first line names the file as the problem holds it, relative to the data folder, such as `menus\2026-W48.toml`, as architecture 6 says for a problem (point D). The second line is two spaces and `problem.text(context.lang)`, such as `The file cannot be written: access is denied.`. The third line is `CHANGED_NOTHING`, or `LEFT_BEHIND` with the full path of the temporary file when `replace_file` could not remove it. The menu file keeps its bytes.
9. **The output.** The three sections of the F14 prototype show different lines for a first fill, a swap, and a fill that leaves meals empty. The design gives each line the case in which it helps, so that the three sections come out as the prototype shows them (2.2):
   - The first line says how many empty meals were filled, with the tag when `--tag` is given. When some meals held dishes before the run, the line goes on with `KEPT`, as the Chinese prototype "Swap one dish" shows.
   - When every empty meal got its dishes, `RUN_SHOW` follows. When no meal held a dish before the run, `NO_TWICE` and `SWAP_HINT` follow too, as in "Fill an empty week". `NO_TWICE` is true only then: a week that you filled yourself may hold a recipe twice. `SWAP_HINT` tells you how to swap after a first fill, and a refill such as "Swap one dish" shows that you know already.
   - When some empty meals stay empty, the second line says how many and why, and nothing follows, as in "Not enough recipes". The reason is `STAY_EMPTY` when every candidate went into a meal, and `TOO_FEW` when candidates are left that no remaining meal can take (point C). Each has a form with the tag.
   - A week with no empty meal gives `NO_EMPTY_MEAL` and then `SWAP_HINT`, with exit code 0, as v0.2-S03 expects.
   - A run that fills no meal, because no candidate is left, gives the lines of a fill that leaves meals empty, with `Filled 0 of`, and exit code 0, and writes no file. v0.2-S04, v0.2-S05, and v0.2-S07 expect exit code 0 for a fill that leaves meals empty, because nothing in the data is wrong.
   - The output goes to the output stream. A refusal and a failure go to the error stream with exit code 1 (architecture 6).
10. **Numbers in messages.** The messages of `suggest` show counts of the slots of a menu, at most 21, and the week, as `str(week)`. A tag goes into a message as the `BiText` of its name, and the value of `--tag` as the text that you typed. The settings' wrong numbers of dishes get a message that shows no number (3.2). A problem in a file reaches the error stream only through `stop_at_error` or the failure lines of choice 8, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `suggest` meets F02's limit of 4,300 digits (F02 design 2.3).
11. **Speed.** No performance target names `menu suggest`. It reads what `menu show` reads up to the menu, the menu file once more, and then each recipe that the week does not hold, as `list` reads every recipe. On a PT01 folder, `list` took a median of 0.782 s on Troy's PC in the release test of v0.1.0 (v0.2 test plan, section 3). So `menu suggest` should take about as long, below 1 second. This is an estimate, not a measurement. The check of the new text parses one more text of a few kilobytes. v0.2-S16 runs `menu suggest` on a PT01 folder without timing it. The start of every other command changes little: `cli` imports `random` and makes one `Random()`, which seeds itself from the system. On Troy's PC, `python -X importtime` gave 1.7 to 2.1 ms for `import random` after `recipe_menu.cli`, far below the margin of every PT01 case, and the PT01 cases of v0.1 run again in v0.2's release test.
12. **Only the command is exported.** `suggest` exports `MENU_SUGGEST_COMMAND` and nothing else. Only `cli` may import `suggest` (architecture 3), so no other name would have a user. F14 takes nothing from `menu`, which exports only its two commands (F11 design, choice 12). `suggest` keeps its own `WEEK_ARGUMENT` and `CHANGED_NOTHING`, with the texts of `menu`, as `shop` does (F13 design, choice 3), and its own `UNKNOWN_TAG` and `NO_TAGS`, with the texts of `list` (choice 4). A later `[refactor]` PR can share them.

The v0.2 scenarios that run `menu suggest` hold with these choices:

- v0.2-S01: step 2 prints the second output of F14 "Fill an empty week": all 14 meals get a dish, and no meal held one before (choice 9). Only the `[]` of each meal changes, so the rest of the file stays as `menu new` wrote it (choice 7). Steps 3 and 4 read the file with no problem.
- v0.2-S02: the output names the tag in the chosen language, so `--tag 快手` gives the same output as `--tag quick` (choice 4). Each run gets its own generator from `cli`, so the two files almost always differ.
- v0.2-S03: step 2 prints the output of F14 "Swap one dish", in Chinese: 1 meal filled and 13 kept. Step 3 prints `2026-W48 has no empty meal. Nothing was changed.` and the swap line, exits with 0, and writes no file (choices 8 and 9).
- v0.2-S04: step 2 prints the output of F14 "Not enough recipes": the 3 recipes with the tag 辣 fill the first 3 meals, and 11 stay empty (choices 6 and 9).
- v0.2-S05: step 1 prints `Filled 1 of 10 empty meals of 2026-W47. Kept the 4 meals that already have dishes.` and `9 meals stay empty: no other recipe is left.`, and exits with 0. `red-braised-pork` fills Monday lunch, the first empty meal. Only that line changes.
- v0.2-S06: with `dishes = { dinner = 2 }`, step 2 fills 21 meals with 28 dishes and prints the four lines of a first fill (choices 5 and 9).
- v0.2-S07: step 2 prints `Filled 7 of 14 empty meals of <N>.` and `7 meals stay empty: no other recipe is left.`, and exits with 0. Step 3 prints `NO_MENU` for `<T>` and exits with 1.
- v0.2-S08: steps 1 to 4 print `NOT_A_WEEK` with exit code 2, `NO_MENU`, `UNKNOWN_TAG`, and the three lines of "A menu with a mistake", each with exit code 1, and write no file (choices 2 to 4).
- v0.2-S14: step 4 prints `NO_DATA_FOLDER` and `RUN_INIT` from `cli` (choice 1). The help of steps 1 and 2 gets the line of `menu suggest` after the line of `menu show`, and every line of its two tables moves 3 columns to the right (2.1). So the Test Manager updates the expected help of v0.2-S14, as section 2 of the v0.2 test plan provides.
- v0.2-S15: step 1 changes only `menus\2026-W48.toml`, and `replace_file` leaves no temporary file (choice 8). The move of `replace_file` also gives the folder `menus\` a new modification time, as `shop` gives `shopping\` one in v0.1-S23. So "the only file whose bytes or time changed" of step 1 counts files, not folders.
- v0.2-S16: step 1 reads the 1,000 recipes and fills the 21 meals of 2026-W53 with 21 different recipes (choices 3 and 6).

Troy decides these four points. The design follows the recommendation of each.

- **A. New texts.** No prototype shows these texts in full. Each follows the wording of a line of the F14 prototype or of an existing message. The recommendation is to accept them as 2.2 and 3.2 give them. They are 19 messages:
  - The Chinese lines for the prototype's English lines: `已为 2026-W48 填好 14 个空餐，用的都是带有标签“快手”的菜谱。`, `这一周里没有重复的菜谱。`, `要换掉一道菜，就在 menus\2026-W48.toml 里清空它那一餐，然后再运行“recipe-menu menu suggest 2026-W48”。`, `已为 2026-W49 填好 14 个空餐中的 3 个，用的都是带有标签“辣”的菜谱。`, and `11 餐仍是空的：没有别的菜谱带有标签“辣”。`.
  - The English line for the prototype's Chinese line: `Filled 1 empty meal of 2026-W48. Kept the 13 meals that already have dishes.`.
  - A fill without `--tag` that leaves meals empty: `Filled 1 of 10 empty meals of 2026-W47.` and `9 meals stay empty: no other recipe is left.`, and `已为 2026-W47 填好 10 个空餐中的 1 个。` and `9 餐仍是空的：没有别的菜谱可选了。`.
  - Meals that stay empty while candidates are left (point C): `4 meals stay empty: too few other recipes are left.` and `4 餐仍是空的：剩下的菜谱不够了。`, and the forms with a tag, such as `… too few other recipes have the tag "spicy".` and `……带有标签“辣”的别的菜谱不够了。`.
  - A week with no empty meal: `2026-W48 has no empty meal. Nothing was changed.` and `2026-W48 没有空餐。没有做任何修改。`, followed by the swap line.
  - A file that `menu suggest` cannot fill, `CANNOT_FILL`, and a failed save whose temporary file stays, `LEFT_BEHIND`, in both languages.
  - The line of the help: `Fill the empty meals of a week menu.` and `给一个周菜单的空餐填上菜。`.
  - The places and problems of the setting `dishes`: `dishes` and `菜数`, `dishes of dinner` and `晚餐的菜数`, `"dishes" must be a table in braces, such as dishes = { dinner = 2 }.`, and `The number of dishes must be a whole number from 1 to 10, such as 2.`, each in both languages.
  - The English forms for one meal, such as `Kept the 1 meal that already has dishes.` and `1 meal stays empty: no other recipe is left.`.
- **B. The setting for the dishes of a meal** (choice 5).
  - Option 1, recommended: one key, `dishes`, a table that gives a number from 1 to 10 for each meal that needs one, such as `dishes = { dinner = 2 }`, or the lines `[dishes]` and `dinner = 2` at the end of the file. A meal that the table leaves out gets 1. `init` keeps writing its settings file without the key.
  - Option 2: one key for each meal, `breakfast_dishes`, `lunch_dishes`, and `dinner_dishes`, each a number from 1 to 10. Choice 5, 3.1, 3.2, and the examples change before the mock PR.
  - The reason for option 1: the table names the meals by the words that you already write in `meals`, and the settings file gains one key, not three.
- **C. A meal that needs more dishes than are left** (choice 6), such as a dinner of 2 dishes when 1 recipe is left.
  - Option 1, recommended: the meal stays empty, and the later meals that need no more dishes than are left still get theirs. Every filled meal has the number of dishes that the settings give. The line about the meals that stay empty says that too few other recipes are left (`TOO_FEW`).
  - Option 2: the meal gets the recipes that are left, and every later meal stays empty. Choices 6 and 9 and the example of 2.2 change before the mock PR. The output then needs a line that names the meal with too few dishes, because a fill in which every meal got a dish would not show it otherwise.
  - The reason for option 1: `menu suggest` fills only empty meals. So a meal that it leaves empty gets its full number of dishes from a later run, after you add recipes or pick another tag, while a meal with too few dishes is no longer empty, and no later run tops it up. The requirement's rule that each empty meal gets the number of dishes that the settings give also holds only under option 1.
- **D. How `menu suggest` names its menu file** (choices 8 and 9). The prototype's line `To swap a dish, empty its meal in menus\2026-W48.toml, …` names the file relative to the data folder. Architecture 6 says that a problem names its file that way, and that other messages name a file by its full path. ADR-0009 and ADR-0010 let `menu new` and `shop` name a file that they could not write by its full path, and section 5 of ADR-0009 asks every later write for its own change to architecture 6. So the swap line, which is not a problem, needs a decision, and so does the first line of a failed save.
  - Option 1, recommended: the swap line names the file as the prototype does, `menus\2026-W48.toml`, with the system's separator. A failed save names the file the same way, as its problem holds it, such as `menus\2026-W48.toml` above `  The file cannot be written: access is denied.`, which architecture 6 already allows for a problem. Architecture 6 gains one sentence for the swap line. The Architect records it in architecture 6 and an ADR, in a `[docs]` PR before the F14 mock PR, as ADR-0010 recorded point C of the F11 design.
  - Option 2: both lines name the full path, such as `C:\Users\Troy\recipe-menu\menus\2026-W48.toml`, as `menu new` and `shop` name their files. The swap line of the F14 prototype changes through the requirement change flow, and architecture 6 gains the case of a failed save of `menu suggest`, both before the F14 test plan. Choices 8 and 9, 2.2, and the examples change before the mock PR.
  - The reason for option 1: it keeps the line of the prototype that Troy approved, and `menu suggest` then names its file one way in every line about it. The data folder is the one that you use every day, which is why architecture 6 names the file of a problem relative to it.
  - Under both options, `LEFT_BEHIND` names the temporary file by its full path, as architecture 6 says for a message that is not a problem, and as `shop` does.

These later features are meant to build on F14. Their own designs decide the details.

- F15's `add` takes nothing from `suggest`. It adds the input stream to `Context` and to `main` in the way that F14 adds the generator: a field with a default and an optional parameter, so no call breaks (section 3).
- F16's `edit` adds the key `editor` to `Settings` and `read_settings`. The text of `UNKNOWN_KEY` for the settings then lists five keys, so F16's design names the tests that compare it, as section 3 does here.

troy-mode's flow has one mock PR and one implementation PR. The entry in `COMMANDS` changes the help and the line of `recipe-menu menu`, and the key `dishes` changes the text of `UNKNOWN_KEY` for the settings. So six tests of F05, F11, and F13 change (section 3). The Developer never edits a test (R08), and every test of an accepted feature must pass (R10). So a test-fix PR before the F14 mock PR changes F11-T32, F13-T01, F13-T22, and F13-T27, which the mock's entry breaks, so that each holds with and without the line of `menu suggest`. F05-T10 and F05-T11 break only when the implementation teaches `read_settings` the key `dishes`. They change in the same test-fix PR or in F14's tests PR, so that they hold with both lists of keys. The test plan names the six tests and the PR that changes them.

The mock (PR 3) holds `src/recipe_menu/commands/suggest/__init__.py`, `messages.py`, and one internal file for `run`, such as `_run.py`, and the entry in `src/recipe_menu/cli/_commands.py`. It adds the field `dishes` with its default and the method `dishes_for` to `Settings`, without the checks of 3.1, and the messages of 3.2 to `src/recipe_menu/settings/messages.py`. It leaves `read_settings` as it is, so `dishes` is still an unknown key, and F05-T10 and F05-T11 keep passing. It adds the field `random` with its default to `Context`, and the parameter `random` to `main`, which the mock does not pass on, so the context gets its default. It adds `read_file_text` and `parse_toml` to `datafile`, in `_toml.py` or in a new internal file, and to `src/recipe_menu/datafile/__init__.py`. It defines every message and `MENU_SUGGEST_COMMAND` with all its fields. Its `run` reads no file, writes nothing, raises nothing, and gives 0. Its `dishes_for` gives 1, its `read_file_text` gives the empty text, and its `parse_toml` gives `None`. So a new test fails against the mock (R09) when it checks an output line, exit code 1, `NOT_A_WEEK` with exit code 2, the bytes of the changed file, a refusal, a failure and its lines, `dishes_for` of a meal with more than one dish, a problem of the key `dishes`, a check of `Settings`, the generator that `main` passes on, or what `read_file_text` and `parse_toml` give. These tests pass against the mock and break R09: a test that checks only the fields of `MENU_SUGGEST_COMMAND`, the help, a message, exit code 0, the defaults and the equality of `Settings`, or the default of `Context.random`. So does a test of what `cli` does before it runs `menu suggest`, such as a missing data folder, broken settings, two weeks, an unknown option, or `--tag` with no value. So does a test that checks only that a run changes no file, as for a week with no empty meal, `NO_MENU`, an unknown tag, or an error. Each such test must also check something that the mock gets wrong, such as the output or the file. The mock changes about 10 files, more than R03's 5, in about 350 lines by estimate, so its description gives a soft-limit reason. The reason is that the tests reach the settings, the context, and the two functions of `datafile` both directly and through `menu suggest`, so they come in one stage, as in the mocks of F08, F11, and F13.

The implementation (PR 5) holds `run` with its reads, its choice, the change of the text, and its output in internal files of `suggest`, such as `_run.py`, `_choose.py`, `_edit.py`, and `_output.py`. It also holds the reading of `dishes` in `settings`, the checks of `Settings`, the generator in `main`, and the two functions of `datafile`. By estimate, it changes about 9 files in about 700 lines, more than R03's limits, so its description gives a soft-limit reason too: the tests of `menu suggest` need all these parts at once. The Developer runs troy-check early.

### 2.1 `MENU_SUGGEST_COMMAND`

- Module: suggest
- Purpose: The description of the `menu suggest` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` fills the empty meals of the week's menu file and writes the output of 2.2.

Signature:

```python
MENU_SUGGEST_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("menu", "suggest")
#   help_line = MENU_SUGGEST_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ("--tag",)
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("menu", "suggest")`. | None |
| `help_line` | `Message` | `MENU_SUGGEST_HELP`: "Fill the empty meals of a week menu." and "给一个周菜单的空餐填上菜。". | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Turns the argument into a week, reads the files of choice 3, chooses the recipes, changes the menu file through `replace_file`, and writes the output of 2.2. | Gives 0 or 1. Raises `UsageError` for a value that is not a week, before it touches the disk or writes any output. Raises nothing for bad data or for a failure on the disk. |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`, which is optional and does not repeat. `WEEK_ARGUMENT` is `WEEK` and `周`, as in F11 and F13. | So `cli` passes no value or one value (F05 design 2.5). |
| `options` | A tuple of `str` | `("--tag",)`, the tag of the recipes to choose from (choice 4). | `cli` passes a value only when it is not empty and does not start with `--`, and at most once (F05 design 2.10). |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `menu suggest` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4), with the field `random` of 3.3. | `run` uses `context.lang`, `context.folder`, `context.settings` for the meals, the dishes of each meal, and `read_week_menu`, `context.out`, `context.err`, `context.today`, and `context.random`. |
| `arguments` | `Arguments` | What the command line gives `menu suggest` (F05 design 2.6). | `arguments.values` is `()` or holds one value, such as `("next",)`. `arguments.option("--tag")` is the value of `--tag`, or `None`. |

- Return value: `MENU_SUGGEST_COMMAND`, a `Command`.
  - `MENU_SUGGEST_COMMAND.usage` is `menu suggest [WEEK]` in English and `menu suggest [周]` in Chinese. So the help shows them, and a usage error quotes `recipe-menu menu suggest [WEEK]` or `recipe-menu menu suggest [周]`.
  - `MENU_SUGGEST_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its lines in `context.lang`, and gives 0 or 1.

After F14, the help lists these commands and options, with the second column after 24 columns (choice 1). The other lines of the help are those of the F05 prototype. In English:

```text
Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  menu new [WEEK]       Create an empty week menu.
  menu show [WEEK]      Show a week menu.
  menu suggest [WEEK]   Fill the empty meals of a week menu.
  shop [WEEK]           Make the shopping list of a week menu.

Options:
  --lang en|zh          The language of the output. Default: the settings, else English.
  --data FOLDER         The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.
  --version             Show the version.
  --help                Show this help.
```

In Chinese:

```text
命令：
  init                  创建数据文件夹和示例数据。
  check                 检查每个数据文件有没有错误。
  list                  列出菜谱。
  show ID               查看一个菜谱。
  search 词...          按名称、食材或标签找菜谱。
  menu new [周]         创建一个空的周菜单。
  menu show [周]        查看一个周菜单。
  menu suggest [周]     给一个周菜单的空餐填上菜。
  shop [周]             生成一个周菜单的购物清单。

选项：
  --lang en|zh          输出语言。默认：设置里的语言，否则英文。
  --data 文件夹         数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。
  --version             显示版本。
  --help                显示这份帮助。
```

Errors:

`run` turns the argument into a week before it touches the disk.

| Error | When |
| --- | --- |
| `UsageError(NOT_A_WEEK, None, week=value)` | `week_from_argument` gives `None` for the value of `WEEK` (choice 2). |

- Side effects: Those of 2.2. `run` reads the catalog, two listings, the week's menu file twice, and the recipes that the week does not hold, through the readers of F03, F04, and F06 and through `read_file_text`. It changes the menu file through `replace_file` when a meal gets a dish, and writes to `context.out` or `context.err`.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, with its seven recipes, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context names dinner as the only meal and holds `Random(7)`, so the run fills the seven dinners of a new week with the seven recipes, in the order that `Random(7).sample` gives (choice 6). The help comes from `COMMANDS`, which holds nine commands after F14. The call that raises touches no file and writes no line to either stream.

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.app import Argument, Arguments, Context, FolderUse, UsageError
from recipe_menu.cli import main
from recipe_menu.commands.suggest import MENU_SUGGEST_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, Settings
from recipe_menu.text import Message

assert MENU_SUGGEST_COMMAND.words == ("menu", "suggest")
assert MENU_SUGGEST_COMMAND.usage == BiText("menu suggest [WEEK]", "menu suggest [周]")
assert MENU_SUGGEST_COMMAND.help_line.render(Lang.EN) == "Fill the empty meals of a week menu."
assert MENU_SUGGEST_COMMAND.help_line.render(Lang.ZH) == "给一个周菜单的空餐填上菜。"
assert MENU_SUGGEST_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert MENU_SUGGEST_COMMAND.options == ("--tag",)
assert MENU_SUGGEST_COMMAND.folder is FolderUse.READ

dinner_only = Settings(Lang.EN, (Meal.DINNER,), 2)
file = folder.menu_file("2026-W48")
text = 'week = "2026-W48"\n' + "".join(f"\n[{day.value}]\ndinner = []\n" for day in Day)
file.write_text(text, encoding="utf-8")
out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, dinner_only, out, err, date(2026, 11, 10), Random(7))
assert MENU_SUGGEST_COMMAND.run(context, Arguments(("2026-W48",))) == 0
relative = Path("menus", "2026-W48.toml")
again = 'then run "recipe-menu menu suggest 2026-W48" again.'
assert out.getvalue().splitlines() == [
    "Filled 7 empty meals of 2026-W48.",
    "No recipe appears twice in the week.",
    'Run "recipe-menu menu show 2026-W48" to see the week.',
    f"To swap a dish, empty its meal in {relative}, {again}",
]
assert err.getvalue() == ""

ids, _ = list_recipe_ids(folder)
picks = Random(7).sample(ids, 7)
menu, problems = read_week_menu(folder, IsoWeek(2026, 48), dinner_only, frozenset(ids))
assert problems == ()
assert menu is not None
assert [slot.dishes for slot in menu.slots] == [(Dish(pick, 2),) for pick in picks]
lines = file.read_text(encoding="utf-8").splitlines()
assert lines[0] == 'week = "2026-W48"'
assert [line for line in lines if line.startswith("dinner")] == [
    f'dinner = ["{pick}"]' for pick in picks
]


def help_lines(*argv: str) -> list[str]:
    output = io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=output,
        stderr=io.StringIO(),
    )
    assert code == 0
    return output.getvalue().splitlines()


english = help_lines("--help")
assert len(english) == 22
assert english[11:14] == [
    "  menu show [WEEK]      Show a week menu.",
    "  menu suggest [WEEK]   Fill the empty meals of a week menu.",
    "  shop [WEEK]           Make the shopping list of a week menu.",
]
assert english[16].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[12] == "  menu suggest [周]     给一个周菜单的空餐填上菜。"

MENU_SUGGEST_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu menu suggest`

- Module: suggest
- Purpose: The command that fills each empty meal of a week's menu file with recipes chosen at random, with no recipe twice in the week, and keeps the filled meals and the rest of the file as they are ([requirements 3](../../requirements.md#3-how-users-interact-with-it) and [4](../../requirements.md#4-features)). The F14 prototype "Fill an empty week", "Swap one dish", and "Not enough recipes" shows it.

Signature:

```text
recipe-menu menu suggest [WEEK] [--tag TAG] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `WEEK` | A text | The week of the menu: an ISO week such as `2026-W48`, `this`, or `next`. | Optional. Without it, this week. Any other text is a usage error (choice 2). |
| `--tag` | A tag's name | Chooses only recipes with that tag. | A name of a tag of the catalog, in either language, as `Catalog.find_tag` matches it (choice 4). Not empty, and given at most once (F05 design 2.10). |
| `--lang` | `en` or `zh` | The language of the output and of every message. It does not change the file. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `menu suggest`. | None |

`menu suggest` takes these steps, in order. `path` is `context.folder.menu_file(str(week))`. Each step that reads a file uses what the earlier steps gave, and each one that finds an error stops the command (choice 3).

1. It turns the value of `WEEK` into a week with `week_from_argument(value, context.today)`. `value` is the value of the argument, or `None` when the line gives none. For a result of `None`, it raises `UsageError(NOT_A_WEEK, None, week=value)` (choice 2).
2. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `menu suggest` gives `stop_at_error(context, error)` for the first one.
3. With `--tag`, `catalog.find_tag(value)` gives `tag`. When it gives `None`, `menu suggest` writes `UNKNOWN_TAG`, picked by the number of the catalog's tags, or `NO_TAGS` when the catalog has none, to the error stream, and gives 1 (choice 4).
4. `list_recipe_ids(context.folder)` gives `ids` and their problems (F04 design 2.5). With an error among the problems, `menu suggest` stops at the first one with `stop_at_error`.
5. `list_menu_weeks(context.folder)` gives `weeks` and their problems (F06 design 2.8). With an error among the problems, `menu suggest` stops at the first one with `stop_at_error`. When `weeks` does not hold the week, it writes `NO_MENU` with `week=str(week)` to the error stream and gives 1.
6. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` gives `menu` and its problems (F06 design 2.9). With an error among the problems, `menu suggest` stops at the first one with `stop_at_error`.
7. The empty meals are the slots of `menu` that hold no dish, and the kept meals are the others (choice 6). When there is no empty meal, `menu suggest` writes `NO_EMPTY_MEAL` and `SWAP_HINT` to the output stream and gives 0.
8. `read_file_text(context.folder, path)` gives the text (3.5). When it gives a `Problem`, `menu suggest` gives `stop_at_error(context, problem)`. It turns each CR LF of the text into LF, and finds the place of every empty meal by the rules below. When an empty meal has no place, it writes the three lines of `CANNOT_FILL` to the error stream and gives 1.
9. For each ID of `ids` that no dish of `menu` names, in the order of `ids`, `read_recipe(context.folder, catalog, recipe_id)` gives the recipe and its problems (F04 design 2.6). With an error among the problems, `menu suggest` stops at the first one with `stop_at_error`.
10. It chooses the recipes with one call of `context.random.sample` and gives them to the empty meals in their order (choice 6).
11. When no meal gets a dish, it writes the output below to the output stream and gives 0. It writes no file.
12. It builds the new text by the rules below and checks it. When the check fails, it writes the three lines of `CANNOT_FILL` to the error stream and gives 1.
13. It calls `replace_file(context.folder, path, new_text)` once (F13 design 3.1). For `FAILED`, it writes the three lines of a failure to the error stream and gives 1 (choice 8). For `CREATED`, it writes the output below to the output stream and gives 0.

The warnings of steps 2, 4, and 9 change nothing (choice 3).

**How the text changes.** `text` is the text that step 8 gave, with each CR LF turned into LF. A line is a piece of `text` between two LF characters, before the first one, or after the last one. Below, `D` is the value of a `Day`, such as `monday`, and `M` is the value of a `Meal`, such as `dinner`. In a pattern, D and M may be bare, or in double or single quotation marks, such as `"dinner"`. A space in a pattern stands for any number of spaces and tabs, also none, and a pattern may end with a comment, `#` and any text.

| Kind of line | The line | Examples |
| --- | --- | --- |
| A header | Its first character other than a space or a tab is `[`. | `[monday]` |
| The header of the day D | ` [ D ] ` | `[monday]`, `[ 'sunday' ]  # guests` |
| A line of the meal M | It starts with ` M =`. | `dinner = ["rice"]`, `dinner = [` |
| An empty line of the meal M | ` M = [ ] ` | `dinner = []`, `dinner = [ ]  # nothing yet` |

The table of a day is the lines after its header, up to the next header or the end of the text. For each empty meal, `menu suggest` finds its place by the first row of this table that applies. It finds the places in step 8, for every empty meal, also for one that will stay empty.

| The text | The place of the meal | When the meal gets dishes |
| --- | --- | --- |
| The table of the day holds exactly one line of the meal, and it is an empty line of the meal. | That line. | The `[`, the `]`, and the spaces between them become the list of the dishes. The text before `[` and after `]`, a comment included, stays. |
| The text has a header of the day, and its table holds no line of the meal. | Right after the header of the day. | A new line: M, ` = `, and the list. The new lines of one day follow its header in the order of the settings' meals. |
| The text has no header of the day. | The end of the text. | The table of the day: an empty line, `[D]`, and for each meal of the day that gets dishes, in the order of the settings' meals, a line of M, ` = `, and the list. The new tables follow each other in the order of the week. When the text is not empty and does not end with LF, an LF comes first. |
| Any other text, such as a table of the day whose line of the meal is not an empty line, like `dinner = [` with `]` on the next line. | None. | `menu suggest` stops with `CANNOT_FILL` in step 8. |

The list of the dishes is `[`, the recipe IDs of the meal in the order of `chosen`, each in double quotation marks, separated by `, `, and `]`, such as `["mapo-tofu", "rice"]`. A recipe ID holds only small letters, digits, and `-` (F04 design 2.4), so it needs no escape. A meal that stays empty gets no new line and keeps its line as it is, and a day none of whose meals gets a dish gets no table.

**The check of the new text.** `old` is `parse_toml(text)`, and `new` is `parse_toml` of the new text (3.6). The check passes when neither is `None`, and `new` equals `old` in which, for each meal that gets dishes, the table of its day holds the key M with the list of its IDs, and the table of the day is a new table when `old` lacks it. A day that the file writes as a table in braces, `monday = { dinner = [] }`, or with dotted keys, `monday.dinner = []`, has no header. So its table goes to the end of the text, which defines the day twice, and the check fails. So does a header or a key that the patterns do not read, such as one with an escape. So every file that `menu suggest` writes reads as the old file with the new dishes, and every line that the rules do not change keeps its text and its order.

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `replace_file` gave `CREATED`, or no meal got a dish, or the week has no empty meal. | The output stream: the lines below. |
| 1 | The tag is unknown, the week has no menu file, a file has an error, `menu suggest` cannot fill the file, or `replace_file` gave `FAILED`. | The error stream: `UNKNOWN_TAG` or `NO_TAGS`, `NO_MENU`, the three lines of `stop_at_error`, the three lines of `CANNOT_FILL`, or the three lines of a failure. Nothing goes to the output stream. |
| 2 | The value of `WEEK` is not a week. | The error stream: `NOT_A_WEEK`, which `cli` writes, with no hint. Nothing goes to the output stream. |

The output is these lines, each ended by a line break. `empty` is the number of empty meals, `filled` the number of empty meals that got dishes, and `kept` the number of kept meals (choice 9).

| Case | Lines, in order |
| --- | --- |
| `filled` equals `empty`, and `kept` is 0 | 1. `FILLED`, or `FILLED_WITH_TAG` with `--tag`, with `count` set to `filled`. 2. `NO_TWICE`. 3. `RUN_SHOW`. 4. `SWAP_HINT`. |
| `filled` equals `empty`, and `kept` is more than 0 | 1. `WITH_KEPT`, with `first` set to the line of the case above, and `kept` set to `KEPT` with `count` set to `kept`. 2. `RUN_SHOW`. |
| `filled` is less than `empty`, and `kept` is 0 | 1. `FILLED_SOME`, or `FILLED_SOME_WITH_TAG` with `--tag`, with `count` set to `empty`. 2. The reason, with `count` set to `empty - filled`: `STAY_EMPTY` when every candidate went into a meal, and `TOO_FEW` when candidates are left, each in its form with the tag when `--tag` is given. |
| `filled` is less than `empty`, and `kept` is more than 0 | 1. `WITH_KEPT`, with `first` set to the line of the case above, and `kept` set to `KEPT`. 2. The reason, as above. |
| The week has no empty meal (step 7) | 1. `NO_EMPTY_MEAL`. 2. `SWAP_HINT`. |

A refusal of `CANNOT_FILL` is three lines: `problem_lines` of `Problem.error(context.folder.relative(path), None, CANNOT_FILL)` (F05 design 2.8), whose first line is the file with no place, such as `menus\2026-W49.toml`, then the message after two spaces, and then `CHANGED_NOTHING`. A failure of the save is the three lines of choice 8.

The messages of `menu suggest` are these. `FILLED`, `FILLED_WITH_TAG`, `FILLED_SOME`, `FILLED_SOME_WITH_TAG`, `KEPT`, `STAY_EMPTY`, `STAY_EMPTY_WITH_TAG`, `TOO_FEW`, `TOO_FEW_WITH_TAG`, and `UNKNOWN_TAG` are `Plural` values (F02 design 2.4), each picked by its `count`, or `UNKNOWN_TAG` by the number of the catalog's tags. Their form "for more" is the form for every count other than 1, and their Chinese text is the same in both forms. `menu suggest` also uses `NOT_A_WEEK` and `NO_MENU` of `menus`.

| Name | English | Chinese |
| --- | --- | --- |
| `MENU_SUGGEST_HELP` | `Fill the empty meals of a week menu.` | `给一个周菜单的空餐填上菜。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `FILLED`, for one | `Filled {count} empty meal of {week}.` | `已为 {week} 填好 {count} 个空餐。` |
| `FILLED`, for more | `Filled {count} empty meals of {week}.` | `已为 {week} 填好 {count} 个空餐。` |
| `FILLED_WITH_TAG`, for one | `Filled {count} empty meal of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_WITH_TAG`, for more | `Filled {count} empty meals of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_SOME`, for one | `Filled {filled} of {count} empty meal of {week}.` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个。` |
| `FILLED_SOME`, for more | `Filled {filled} of {count} empty meals of {week}.` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个。` |
| `FILLED_SOME_WITH_TAG`, for one | `Filled {filled} of {count} empty meal of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。` |
| `FILLED_SOME_WITH_TAG`, for more | `Filled {filled} of {count} empty meals of {week} with recipes that have the tag "{tag}".` | `已为 {week} 填好 {count} 个空餐中的 {filled} 个，用的都是带有标签“{tag}”的菜谱。` |
| `KEPT`, for one | `Kept the {count} meal that already has dishes.` | `保留了已经有菜的 {count} 餐。` |
| `KEPT`, for more | `Kept the {count} meals that already have dishes.` | `保留了已经有菜的 {count} 餐。` |
| `WITH_KEPT` | `{first} {kept}` | `{first}{kept}` |
| `NO_TWICE` | `No recipe appears twice in the week.` | `这一周里没有重复的菜谱。` |
| `RUN_SHOW` | `Run "recipe-menu menu show {week}" to see the week.` | `运行“recipe-menu menu show {week}”查看这一周。` |
| `SWAP_HINT` | `To swap a dish, empty its meal in {file}, then run "recipe-menu menu suggest {week}" again.` | `要换掉一道菜，就在 {file} 里清空它那一餐，然后再运行“recipe-menu menu suggest {week}”。` |
| `STAY_EMPTY`, for one | `{count} meal stays empty: no other recipe is left.` | `{count} 餐仍是空的：没有别的菜谱可选了。` |
| `STAY_EMPTY`, for more | `{count} meals stay empty: no other recipe is left.` | `{count} 餐仍是空的：没有别的菜谱可选了。` |
| `STAY_EMPTY_WITH_TAG`, for one | `{count} meal stays empty: no other recipe has the tag "{tag}".` | `{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。` |
| `STAY_EMPTY_WITH_TAG`, for more | `{count} meals stay empty: no other recipe has the tag "{tag}".` | `{count} 餐仍是空的：没有别的菜谱带有标签“{tag}”。` |
| `TOO_FEW`, for one | `{count} meal stays empty: too few other recipes are left.` | `{count} 餐仍是空的：剩下的菜谱不够了。` |
| `TOO_FEW`, for more | `{count} meals stay empty: too few other recipes are left.` | `{count} 餐仍是空的：剩下的菜谱不够了。` |
| `TOO_FEW_WITH_TAG`, for one | `{count} meal stays empty: too few other recipes have the tag "{tag}".` | `{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。` |
| `TOO_FEW_WITH_TAG`, for more | `{count} meals stay empty: too few other recipes have the tag "{tag}".` | `{count} 餐仍是空的：带有标签“{tag}”的别的菜谱不够了。` |
| `NO_EMPTY_MEAL` | `{week} has no empty meal. Nothing was changed.` | `{week} 没有空餐。没有做任何修改。` |
| `CANNOT_FILL` | `menu suggest cannot fill this file: write each day as a line such as [monday], and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.` | `menu suggest 无法填写这个文件：请把每一天写成 [monday] 这样的一行，把每个空餐写成 dinner = [] 这样的一行，和“recipe-menu menu new”写的一样。` |
| `CHANGED_NOTHING` | `Nothing was changed.` | `没有做任何修改。` |
| `LEFT_BEHIND` | `Nothing was changed, but menu suggest could not remove {file}. Delete it.` | `没有做任何修改，但 menu suggest 没能删除 {file}。请删除它。` |
| `UNKNOWN_TAG`, for one tag | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`, for more tags | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `week` | `str(week)`, such as `2026-W48`. |
| `count` | The number that picks each `Plural`, as the table of the output gives it. |
| `filled` | The number of empty meals that got dishes. |
| `tag` | The name of the tag that `find_tag` gave, as its `BiText`, so each language shows its own name: `quick` and `快手` for `--tag 快手`. |
| `first` | The first line of the output without `KEPT`, as a `BiText`. |
| `kept` | `KEPT`, picked by the number of kept meals, with `count` set to it, as a `BiText`. |
| `file` | In `SWAP_HINT`, `str(context.folder.relative(path))`, such as `menus\2026-W48.toml` on Windows (point D). In `LEFT_BEHIND`, `str(creation.left[0])`, the full path of the temporary file, such as `C:\Users\Troy\recipe-menu\menus\2026-W48.toml.tmp`. |
| `value` | The value of `--tag` as you typed it. |
| `tags` | `and_list` of the names of the catalog's tags, each as its `BiText`, in the catalog's order, as for `list` (F09 design 2.2). |

With these messages, the lines of the F14 prototype follow, such as `Filled 14 empty meals of 2026-W48 with recipes that have the tag "quick".`, `已为 2026-W48 填好 1 个空餐。保留了已经有菜的 13 餐。`, and `11 meals stay empty: no other recipe has the tag "spicy".`.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `menu suggest` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `NOT_A_WEEK` and no hint: `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | The value of `WEEK` is not a week (step 1). |
| Exit code 1, with `UNKNOWN_TAG` or `NO_TAGS` on the error stream, such as `Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.` | The catalog has no tag with the name of `--tag` (step 3). |
| Exit code 1, with `NO_MENU` on the error stream: `There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | The listing of `menus/` holds no file for the week (step 5). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream, such as `menus\2026-W47.toml, Monday dinner`, `  Unknown recipe "tomato-eggs".`, and `RUN_CHECK` | The catalog, a listing, the week's menu file, its text, or a recipe that the week does not hold has an error (steps 2, 4 to 6, 8, and 9). |
| Exit code 1, with the three lines of `CANNOT_FILL` on the error stream | An empty meal has no place in the text, or the new text fails its check (steps 8 and 12). The file keeps its bytes. |
| Exit code 1, with the three lines of a failure on the error stream | `replace_file` gave `FAILED` (step 13, choice 8). The file keeps its bytes. |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error, such as a wrong value of `dishes` (3.2). `cli` checks both in step 9 of F05 design 2.10, because `menu suggest` has `FolderUse.READ`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `Unexpected argument "2026-W49". Write "recipe-menu menu suggest [WEEK]".` | The line names two weeks. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for one option and then `RUN_HELP_FOR_OPTIONS`, such as `"menu suggest" has no option "--tags". Its own option is "--tag".` | An option other than `--tag` and the four global options. |
| Exit code 2, with `OPTION_NEEDS_VALUE` or `OPTION_TWICE` and no hint, such as `--tag needs a value.` | `--tag` has no value, or comes twice. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. `replace_file` removes its temporary file, the menu file keeps its old text or holds its new text, and `cli` writes nothing more (F13 design 3.1). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `menu suggest` then reads `catalog.toml` once, lists `recipes/` once, lists `menus/` once, reads the week's menu file twice, once through `read_week_menu` and once through `read_file_text`, and reads each recipe file that the week does not hold once. After a wrong week, it reads no file. After an error, an unknown tag, `NO_MENU`, a week with no empty meal, or a refusal in step 8, it reads nothing more. It reads neither `pantry.toml`, another menu, nor a recipe that the week holds. When a meal gets a dish and the check passes, it changes the week's menu file through `replace_file`, which writes and moves `menus/<week>.toml.tmp`. It changes no other file. It writes to the output stream or the error stream.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. Each run passes `main` a new `Random(3)`, so `Random(3).sample` gives the recipes that a run chooses (choice 6). The first run is v0.2-S05: `red-braised-pork`, the one recipe that the week does not hold, fills Monday lunch, and only that line of the file changes. The second run finds no candidate and writes no file. The runs for an unknown tag, a week with no menu, and a wrong week follow. Then a file that leaves out a meal and six days gets a new line and new tables, and a file that writes a day in braces is refused. The last run gives dinner 2 dishes with the setting `dishes`, so the fourth dinner stays empty while one recipe is left (point C).

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.cli import main
from recipe_menu.recipes import list_recipe_ids


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        [*argv, "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        random=Random(3),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


week47 = folder.menu_file("2026-W47")
before = week47.read_text(encoding="utf-8").splitlines()
assert run("menu", "suggest", "2026-W47") == (
    0,
    [
        "Filled 1 of 10 empty meals of 2026-W47. Kept the 4 meals that already have dishes.",
        "9 meals stay empty: no other recipe is left.",
    ],
    [],
)
after = week47.read_text(encoding="utf-8").splitlines()
changed = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
assert changed == [("lunch = []", 'lunch = ["red-braised-pork"]')]
assert after[3:5] == ["[monday]", 'lunch = ["red-braised-pork"]']
made = week47.stat().st_mtime_ns
assert run("menu", "suggest", "2026-W47") == (
    0,
    [
        "Filled 0 of 9 empty meals of 2026-W47. Kept the 5 meals that already have dishes.",
        "9 meals stay empty: no other recipe is left.",
    ],
    [],
)
assert week47.stat().st_mtime_ns == made

tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
unknown = (1, [], [f'Unknown tag "breakfast". {tags}'])
assert run("menu", "suggest", "2026-W47", "--tag", "breakfast") == unknown
no_menu = 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
assert run("menu", "suggest", "2026-W48") == (1, [], [no_menu])
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("menu", "suggest", "2026-W99") == (2, [], [week_error])

week48 = folder.menu_file("2026-W48")
week48.write_text('week = "2026-W48"\n\n[monday]\ndinner = []  # leftovers\n', encoding="utf-8")
ids, _ = list_recipe_ids(folder)
a, b, c, d, e, f, g = Random(3).sample(ids, 7)
assert run("menu", "suggest", "2026-W48") == (
    0,
    [
        "Filled 7 of 14 empty meals of 2026-W48.",
        "7 meals stay empty: no other recipe is left.",
    ],
    [],
)
assert week48.read_text(encoding="utf-8").splitlines() == [
    'week = "2026-W48"',
    "",
    "[monday]",
    f'lunch = ["{a}"]',
    f'dinner = ["{b}"]  # leftovers',
    "",
    "[tuesday]",
    f'lunch = ["{c}"]',
    f'dinner = ["{d}"]',
    "",
    "[wednesday]",
    f'lunch = ["{e}"]',
    f'dinner = ["{f}"]',
    "",
    "[thursday]",
    f'lunch = ["{g}"]',
]

week49 = folder.menu_file("2026-W49")
inline = 'week = "2026-W49"\nmonday = { lunch = [], dinner = [] }\n'
week49.write_text(inline, encoding="utf-8")
first = "  menu suggest cannot fill this file: write each day as a line such as [monday], "
second = 'and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.'
assert run("menu", "suggest", "2026-W49") == (
    1,
    [],
    [str(Path("menus", "2026-W49.toml")), first + second, "Nothing was changed."],
)
assert week49.read_text(encoding="utf-8") == inline

settings_text = folder.settings.read_text(encoding="utf-8")
meals = settings_text.replace('["lunch", "dinner"]', '["dinner"]')
folder.settings.write_text(meals + "dishes = { dinner = 2 }\n", encoding="utf-8")
assert run("menu", "new", "2026-W50")[0] == 0
assert run("menu", "suggest", "2026-W50") == (
    0,
    [
        "Filled 3 of 7 empty meals of 2026-W50.",
        "4 meals stay empty: too few other recipes are left.",
    ],
    [],
)
```

## 3. Changes to existing interfaces

F14 adds to four implemented modules what architecture 5.1 and 5.2 plan for it: "F14 adds the dishes per meal" to the settings, and "F14 adds a random generator" to the context. No call of an exported name of F01 to F13 breaks: each new field has a default, the new parameter of `main` is optional, and `datafile` gains two names. The requirements already name the setting (requirements 4, F14), so no `[docs]` PR approves these additions. The Architect reviews them in this design, as it reviewed F11's `create_file` and F13's `replace_file`.

1. `settings`: `Settings` gets the field `dishes` and the method `dishes_for` (3.1), and `read_settings` reads the key `dishes` (3.2). Two settings are now equal when their four fields are equal. The key `dishes` gave `UNKNOWN_KEY` before, and the text of `UNKNOWN_KEY` for the settings now lists four keys.
2. `app`: `Context` gets the field `random` (3.3). Two contexts are now equal when their seven fields are equal, and the streams and the generator compare as objects.
3. `cli`: `main` gets the parameter `random` (3.4), and `COMMANDS` gets `MENU_SUGGEST_COMMAND` (choice 1).
4. `datafile`: `read_file_text` (3.5) and `parse_toml` (3.6).

These tests of accepted features change, and section 2 says in which PR:

- F05-T10 and F05-T11 compare the text of `UNKNOWN_KEY` for the settings with "language, meals, and servings" (`KEYS_EN` and `unknown_key` in `tests/f05_texts.py`). Once `read_settings` reads `dishes`, the text lists "language, meals, servings, and dishes".
- F11-T32 compares `recipe-menu menu` with the real `COMMANDS` with `The commands that start with "menu" are "menu new" and "menu show".` and its Chinese line. With the entry of the mock, the line lists three commands.
- F13-T01, F13-T22, and F13-T27 compare the help of the real `COMMANDS` with `HELP_EN` and `HELP_ZH` of `tests/f05_texts.py`, the helps of the F05 prototype. With the entry of the mock, the help gets a line, and its second column moves from 21 to 24 columns.

These tests stay true. F07-T17, F08-T14, F09-T01, F10-T01, and F11-T01 check that a line of the real help follows another line, and that its text starts at the column of the text of `--lang en|zh`. Both hold, because the line of `menu suggest` comes after the line of `menu show`, and every line moves by the same 3 columns. F11-T27 and F11-T35 compare one help of the real `COMMANDS` with another. The tests of F05 run their own commands. No test runs `menu suggest`, which gives `Unknown command "menu suggest".` before the mock. `init` and `menu new` write the same files as before, so v0.1-S01, v0.1-S02, and v0.1-S13 hold. The two helps of the F05 prototype show the help of v0.1, as its note says, so from the mock on the real help differs from them. The Product Manager decides at F14's acceptance how the real run treats those two sections. v0.1-S19 and v0.2-S14 change as section 2 of the v0.2 test plan says.

F14 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, and `and_list`.
- F03's `DataFolder` with `menu_file` and `relative`, `Problem`, `Catalog` with `find_tag`, and `read_catalog`.
- F04's `Recipe`, `list_recipe_ids`, and `read_recipe`.
- F05's `Argument`, `Arguments`, `Command`, `FolderUse`, `UsageError`, `first_error`, `problem_lines`, and `stop_at_error` in `app`, `Meal` and `Settings` in `settings`, and `COMMANDS` in `cli`, with the additions of 3.1 to 3.4.
- F06's `Day`, `IsoWeek`, `NOT_A_WEEK`, `WeekMenu`, `MealSlot`, `list_menu_weeks`, `read_week_menu`, and `week_from_argument`.
- F11's `NO_MENU` in `menus`, and `FileOutcome` and `FileCreation` in `datafile`.
- F13's `replace_file` in `datafile`.

### 3.1 `Settings.dishes` and `Settings.dishes_for`

- Module: settings
- Purpose: The number of dishes that `menu suggest` puts in an empty breakfast, lunch, and dinner, 1 by default ([requirements 4](../../requirements.md#4-features), architecture 5.1). `read_settings` fills it from the key `dishes` (3.2), and `menu suggest` asks `dishes_for` (choice 6).

Signature:

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
    dishes: tuple[int, int, int] = (1, 1, 1)

    def dishes_for(self, meal: Meal) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `dishes` | A tuple of three `int` values | The number of dishes of breakfast, lunch, and dinner, in the order of `Meal`. | Exactly three items, each a whole number from 1 to 10. Not a `bool`. |
| `meal` | `Meal` | The meal whose number `dishes_for` gives. | Any `Meal`, also one that `meals` does not name. |

The other fields keep their meanings and constraints (F05 design 2.2).

- Return value: A `Settings`. Two settings are equal when their four fields are equal, and a `Settings` is hashable. `Settings()` and every call that F01 to F13 make keep `dishes` at `(1, 1, 1)`.
  - `dishes_for(meal)` gives `dishes[list(Meal).index(meal)]`.

Errors:

The errors of F05 design 2.2 stay, and these come with `dishes`:

| Error | When |
| --- | --- |
| `TypeError` | `dishes` is not a tuple, or it holds an item that is not an `int`, or that is a `bool`. |
| `ValueError` | `dishes` does not hold exactly three items, or it holds a number less than 1 or more than 10. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.dishes == (1, 1, 1)
assert [defaults.dishes_for(meal) for meal in Meal] == [1, 1, 1]
two = Settings(Lang.ZH, tuple(Meal), 3, (1, 1, 2))
assert two.dishes_for(Meal.DINNER) == 2
assert two.dishes_for(Meal.BREAKFAST) == 1
assert Settings(Lang.EN) == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2, (1, 1, 1))

Settings(dishes=(1, 1))  # raises ValueError
Settings(dishes=(1, 0, 1))  # raises ValueError
Settings(dishes=(1, 1, 11))  # raises ValueError
Settings(dishes=[1, 1, 2])  # raises TypeError
Settings(dishes=(1, 1, True))  # raises TypeError
Settings(dishes=(1, 1, 2.0))  # raises TypeError
```

### 3.2 `read_settings`: the key `dishes`

- Module: settings
- Purpose: Reads the optional key `dishes` of `settings.toml` into `Settings.dishes`, and reports its problems with their places, as for the other keys (F05 design 2.3, choice 5). `cli` and `check` call `read_settings` as before.

Signature:

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: The pair `(settings, problems)` of F05 design 2.3, with these additions.
  - The file may hold the key `dishes`, a table whose keys are values of `Meal`, each with a whole number from 1 to 10, such as `dishes = { dinner = 2 }`. The lines `[dishes]` and `dinner = 2` at the end of the file give the same table. A meal that the table leaves out, or a file with no `dishes`, gets 1. A meal that `meals` does not name may have a number, which counts once you add the meal.
  - `settings.dishes` holds the number of each meal, in the order of `Meal`.
  - The keys of the top of the file are `language`, `meals`, `servings`, and `dishes`, in this order. So `UNKNOWN_KEY` names "language, meals, servings, and dishes" and "language、meals、servings 和 dishes", in its form for more keys.

The places of the new problems are these:

| Place | English | Chinese |
| --- | --- | --- |
| `dishes` | `dishes` | `菜数` |
| The number of the meal M in `dishes` | `dishes of`, a space, and the meal's `label`, such as `dishes of dinner` | The meal's `label` and `的菜数`, such as `晚餐的菜数` |

`read_settings` makes these checks of `dishes`. A missing key gives no problem.

| Part | Check | Problem | Place | Kind |
| --- | --- | --- | --- | --- |
| `dishes` | The value is not a table, such as `dishes = 2` or `dishes = []`. | `DISHES_NOT_A_TABLE` | `dishes` | Error |
| A key of `dishes` | The key is not the value of a `Meal`, such as `supper` or `Dinner`. | `UNKNOWN_MEAL` of `settings` (F05 design 2.3) | `dishes` | Error |
| A key of `dishes` that is a meal | The value is not an `int` from 1 to 10, or it is a `bool`, such as `0`, `11`, `2.5`, `"2"`, or `true`. | `DISHES_NOT_1_TO_10` | The number of the meal | Error |

The problems of `dishes` come after those of `servings` and before the unknown keys of the top of the file. A value that is not a table gives its problem alone. Otherwise the keys of the table give their problems in the file's order. The place of `UNKNOWN_MEAL` is `dishes`, because the message names the meal, as for `meals` (F05 design 2.3).

These are the new messages of `settings`. In the templates of `DISHES_NOT_A_TABLE`, each brace is written twice (F02 design 2.2). `DISHES_NOT_1_TO_10` shows no number, so a value of thousands of digits never reaches F02's limit.

| Name | English | Chinese |
| --- | --- | --- |
| `DISHES` and `DISHES_OF` | The places in the table of places, with `{meal}` for the meal's `label`. | The places in the table of places, with `{meal}` for the meal's `label`. |
| `DISHES_NOT_A_TABLE` | `"dishes" must be a table in braces, such as dishes = { dinner = 2 }.` | `“dishes”必须是放在花括号里的表，比如 dishes = { dinner = 2 }。` |
| `DISHES_NOT_1_TO_10` | `The number of dishes must be a whole number from 1 to 10, such as 2.` | `菜数必须是 1 到 10 之间的整数，比如 2。` |

The values of the placeholders of `UNKNOWN_MEAL` are those of F05 design 2.3: `meal` is the key as the file writes it, and `meals` is `and_list` of the values of `Meal`.

Errors: None. `read_settings` never raises for bad data.

- Side effects: Reads `settings.toml` through `read_toml`, as before. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`.

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Meal, Settings, read_settings

lines = ['meals = ["breakfast", "lunch", "dinner"]', "dishes = { dinner = 2 }"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
assert read_settings(folder) == (Settings(None, tuple(Meal), 2, (1, 1, 2)), ())
folder.settings.write_text("[dishes]\nlunch = 3\n", encoding="utf-8")
assert read_settings(folder) == (Settings(dishes=(1, 3, 1)), ())

lines = ["dishes = { dinner = 0, supper = 2, lunch = true }", "colour = 1"]
folder.settings.write_text("\n".join(lines) + "\n", encoding="utf-8")
settings, problems = read_settings(folder)
assert settings is None
assert [problem.place for problem in problems] == [
    BiText("dishes of dinner", "晚餐的菜数"),
    BiText("dishes", "菜数"),
    BiText("dishes of lunch", "午餐的菜数"),
    None,
]
english = problems[0].text(Lang.EN)
assert english == "The number of dishes must be a whole number from 1 to 10, such as 2."
assert problems[0].text(Lang.ZH) == "菜数必须是 1 到 10 之间的整数，比如 2。"
unknown = 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
assert problems[1].text(Lang.EN) == unknown
keys = 'Unknown key "colour". The keys are language, meals, servings, and dishes.'
assert problems[3].text(Lang.EN) == keys

folder.settings.write_text("dishes = []\n", encoding="utf-8")
_, problems = read_settings(folder)
not_a_table = '"dishes" must be a table in braces, such as dishes = { dinner = 2 }.'
assert [problem.text(Lang.EN) for problem in problems] == [not_a_table]
```

### 3.3 `Context.random`

- Module: app
- Purpose: The random generator of a command ([architecture 5.2](../../architecture.md#52-values) and [8](../../architecture.md#8-naming-and-coding-rules)). `cli` makes it from a seed of the system (3.4), and a test passes one with a fixed seed. `menu suggest` chooses its recipes with it (choice 6).

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
    random: Random = field(default_factory=lambda: Random(0))
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `random` | `random.Random` | The generator that a command draws its random choices from. | When `cli` builds the context, the generator that `main` got or made (3.4). Without it, a new `Random(0)` for each context, so a test that builds a context gets the same choices every time. |

The other fields keep their meanings and constraints (F05 design 2.4). `Random` is `random.Random`, and `field` is `dataclasses.field`. Ruff's rule S311, among the `S` rules that the project checks, flags `Random(0)`. So the line of the default carries `# noqa: S311` with a reason, as the tests write it, such as `# noqa: S311 - a fixed seed, no security`, from the mock PR on, because the mock adds the field.

- Return value: A `Context`. Two contexts are equal when their seven fields are equal, and the streams and the generator compare as objects. So two contexts that each made their own default generator are not equal. A `Context` is hashable.

Errors: None

- Side effects: None. Building a context with the default makes a `Random(0)`, which reads nothing of the outside world.
- Performance target: None

Example:

```python
import io
from datetime import date
from pathlib import Path
from random import Random

from recipe_menu.app import Context
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
today = date(2026, 11, 10)
seeded = Random(5)
context = Context(Lang.EN, folder, Settings(), out, err, today, seeded)
assert context.random is seeded
first = Context(Lang.EN, folder, Settings(), out, err, today)
second = Context(Lang.EN, folder, Settings(), out, err, today)
assert first.random is not second.random
assert first != second
assert first.random.random() == second.random.random() == Random(0).random()
```

### 3.4 `main`: the parameter `random`

- Module: cli
- Purpose: Lets a test fix the random choices of a command ([architecture 8](../../architecture.md#8-naming-and-coding-rules): only `cli` reads a random seed). `main` passes the generator to the command in `Context.random` (3.3).

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
    random: Random | None = None,
) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `random` | `random.Random` or `None` | The generator of the command. | `None` gives `Random()`, which seeds itself from the system's source of random bytes, so each run of the installed command chooses anew. |

The other parameters keep their meanings and constraints (F05 design 2.9). Ruff's rule S311 flags `Random()` too. So the line of `main` that makes it carries `# noqa: S311` with a reason, such as `# noqa: S311 - a recipe choice, no security`, from the first PR that writes that line. The mock passes no generator on (section 2), so that is the implementation.

- Return value: The exit code of F05 design 2.10, as before. In step 10 of F05 design 2.10, the `Context` holds the generator.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `commands` breaks its constraint, as before (F05 design 2.9). |

- Side effects: Those of F05 design 2.9. When `random` is `None`, `main` makes one `Random()` before it runs a command. It reads no other seed.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. `PICK` stands in for a command that draws random choices.

```python
import io
from datetime import date
from random import Random

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message

seen: list[Random] = []


def run_pick(context: Context, arguments: Arguments) -> int:
    seen.append(context.random)
    return 0


PICK = Command(("pick",), Message("Pick a recipe.", "挑一个菜谱。"), run_pick)


def pick(random: Random | None) -> int:
    return main(
        ["pick", "--data", str(folder.root)],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        commands=[PICK],
        random=random,
    )


seeded = Random(9)
assert pick(seeded) == 0
assert seen == [seeded]
assert pick(None) == 0
assert isinstance(seen[1], Random)
assert seen[1] is not seeded
```

### 3.5 `read_file_text`

- Module: datafile
- Purpose: Reads one data file as UTF-8 text, with the problems of `read_toml` for a file that cannot be read or is not UTF-8 (F03 design 2.3). `menu suggest` reads the text of the menu file with it, so that it can change the lines of the empty meals and keep every other line (choice 7). Only `datafile` opens data files (architecture 8).

Signature:

```python
def read_file_text(folder: DataFolder, path: Path) -> str | Problem: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `path` | `Path` | The file to read, such as `folder.menu_file("2026-W47")`. | Inside `folder.root`. |

- Return value: The text of the file, or a `Problem` with `Severity.ERROR` and the file `folder.relative(path)`.
  - `read_file_text` takes steps 1 and 2 of `read_toml`, with their problems: it reads the bytes, and decodes them all at once with the `utf-8-sig` codec and strict errors. An `OSError` gives `FILE_IS_FOLDER`, `FILE_MISSING`, `ACCESS_DENIED`, or `SYSTEM_ERROR` with no place, and a `UnicodeDecodeError` gives `NOT_UTF8` at its line (F03 design 2.3).
  - The text has no byte order mark, and its line ends are those of the file, so a CR LF stays a CR LF. It does not parse the text.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `path` is not inside `folder.root`, as `DataFolder.relative` finds. The check runs before the file is read. |

- Side effects: Reads the bytes of one file. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`.

```python
from pathlib import Path

from recipe_menu.datafile import Problem, read_file_text
from recipe_menu.lang import BiText, Lang

file = folder.menu_file("2026-W47")
text = read_file_text(folder, file)
assert isinstance(text, str)
assert text.splitlines()[:2] == ["# 2026-W47: 16 to 22 November 2026", 'week = "2026-W47"']
file.write_bytes(b'\xef\xbb\xbfweek = "2026-W47"\r\n')
assert read_file_text(folder, file) == 'week = "2026-W47"\r\n'
file.write_bytes(b"week = 1\n\xff\n")
broken = read_file_text(folder, file)
assert isinstance(broken, Problem)
assert broken.place == BiText("line 2", "第 2 行")
not_utf8 = "The file cannot be read: it is not UTF-8 text. Save it as UTF-8."
assert broken.text(Lang.EN) == not_utf8
missing = read_file_text(folder, folder.menu_file("2026-W48"))
assert isinstance(missing, Problem)
assert (missing.file, missing.place) == (Path("menus", "2026-W48.toml"), None)
assert missing.text(Lang.EN) == "The file is missing."

read_file_text(folder, folder.root.parent / "elsewhere.toml")  # raises ValueError
```

### 3.6 `parse_toml`

- Module: datafile
- Purpose: Parses a TOML text that is not a file, such as the new text of a menu file, so that `menu suggest` can check it before it writes it (choice 7). It keeps the parsing of TOML in `datafile` (ADR-0002). Its caller compares the table and never passes it on (architecture 5).

Signature:

```python
def parse_toml(text: str) -> dict[str, object] | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | The text to parse. | Any string. |

- Return value: `tomllib.loads(text)`, or `None` when `tomllib` raises `TOMLDecodeError`, the plain `ValueError` of a number of too many digits, or `RecursionError` for nesting that is too deep, the three exceptions that step 3 of `read_toml` catches (F03 design 2.3). It gives no reason and no line, because its caller only needs to know whether the text parses.

Errors: None. `parse_toml` never raises for a `str`.

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.datafile import parse_toml

assert parse_toml('week = "2026-W47"\n[monday]\ndinner = ["rice"]\n') == {
    "week": "2026-W47",
    "monday": {"dinner": ["rice"]},
}
assert parse_toml("") == {}
assert parse_toml("[monday]\n[monday]\n") is None
assert parse_toml('dinner = ["rice"') is None
assert parse_toml("servings = " + "1" * 5000) is None
assert parse_toml("x = " + "[" * 5000 + "]" * 5000) is None
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `suggest` is the command module that architecture 3 gives F14, in `src/recipe_menu/commands/suggest/`, and it exports only `MENU_SUGGEST_COMMAND`. It imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `settings`, and `menus`, all of them in its row. It needs neither `units`, `shopping`, nor `menu`, so it adds no arrow to architecture 4. Its entry in `COMMANDS` is the one change in `cli` that architecture 4 gives a command feature. Section 3 adds what architecture 3, 5.1, and 5.2 plan for F14: the dishes of each meal in `settings.toml` and `Settings`, a random generator in `Context` that only `cli` seeds (architecture 8), and two reads in `datafile`, the only module that opens data files. ADR-0001 already names `random` for the suggestions. `Settings.dishes` is a tuple of three `int` values in the order of `Meal`, and `Context.random` is a `random.Random`. Both are fields with defaults of frozen dataclasses, so the value rules of architecture 8 hold. `parse_toml` gives its raw table only to `suggest`, which compares the table without passing it on, so the rule of architecture 5 on raw tables holds. The file that `menu suggest` writes is the `menus/<week>.toml` of architecture 5.1, in UTF-8 with no byte order mark and with LF line ends, and it writes the file through `replace_file`, the write that architecture 6 gives a file that is replaced. Choice 7 keeps to ADR-0001 and ADR-0002 with the standard library and turns down tomlkit, which would need R16. Choice 11 now gives the measured 1.7 to 2.1 ms of `import random` (note 1 of round 1). |
| Follows the error handling and naming conventions | Pass | The first error of a reader stops `menu suggest` through F05's `first_error` and `stop_at_error`. `NO_MENU`, an unknown tag, `CANNOT_FILL`, and a failed save go to stderr with exit code 1, and a wrong week is the only `UsageError`, with no hint (architecture 6, ADR-0008). `CANNOT_FILL` is a `Problem` with the file relative to the data folder. `menu suggest` writes it with `problem_lines` and then `CHANGED_NOTHING`, not `RUN_CHECK`, because `check` does not report it, as `menu new` ends its failures (ADR-0010, section 5). `read_file_text` turns each `OSError` and `UnicodeDecodeError` into a `Problem`, as `read_toml` does, and `parse_toml` catches only the three exceptions that `read_toml` catches (architecture 6 and 8). The names follow architecture 8: the key `dishes`, the messages in the `messages.py` of each module, and `read_file_text`, which keeps clear of the `read_text` that `datafile` already exports. Option 1 of point D follows the way of ADR-0010: one sentence in architecture 6 for the swap line, with an ADR, in a `[docs]` PR before the mock. The first failure line and `CANNOT_FILL` already follow the rule of architecture 6 for a problem. 3.3 and 3.4 now give the `# noqa: S311` with a reason for `Random(0)` and `Random()` (note 2 of round 1). The Architect checked both lines on a sample file with ruff 0.17.4 and the project's `pyproject.toml`. `Random()` alone gives S311. The two lines with their comments pass S311, RUF100, and E501, also the line of the default at 103 columns, because ruff does not count a trailing `# noqa` comment against the limit of 100. The example of 2.1 imports `UsageError` (note 3). |
| Does not duplicate an existing interface | Pass | `menu suggest` gets its week from `week_from_argument`, its tag from `Catalog.find_tag`, its empty meals from `read_week_menu`, its candidates from `list_recipe_ids` and `read_recipe`, and its write from `replace_file`. It builds none of them again. `read_file_text` and `parse_toml` are new: no interface gives the text of a file or parses a text, and both can share the steps of `read_toml` inside `datafile`. The copies of `WEEK_ARGUMENT`, `CHANGED_NOTHING`, `UNKNOWN_TAG`, and `NO_TAGS` are internal messages, which architecture 8 keeps in each module. `suggest` may not import `browse`, and `menu` exports only its commands, so the copies have the reason that the F13 review accepted for `shop`. The read of the catalog and the stop at the first error is a fifth copy of internal code, which the later `[refactor]` PR of note 2 of the F13 review can share through a helper in `app`. Round 2 changes nothing here. |
| Depends only on features earlier in the order | Pass | F14 uses F02's `text`, F03's `datafile` and `catalog`, F04's `recipes`, F05's `app`, `settings`, and `cli`, F06's `menus`, F11's `NO_MENU`, `FileOutcome`, and `FileCreation`, and F13's `replace_file`, and it copies two texts of F09. Each of these features comes before F14 and is accepted on main, and so is F05, the hard dependency. F13 is not in the row of F14 in the requirements' graph. F14 uses it through the shared module `datafile`, which points to an earlier feature, as architecture 4 allows. The plans for F15 and F16 bind no later design. F14 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. `suggest` knows the layout of a menu file that `menus` reads and `menu new` writes, and it never trusts its line patterns alone. The check of the new text with `parse_toml` must give the old table with the new dishes, so a layout that the patterns misread is refused and never written (2.2). A recipe ID needs no escape (F04 design 2.4). The temporary file `<week>.toml.tmp` meets no reader, because `list_menu_weeks` and `check` count only names that end with `.toml` (F06 design 2.8). The path of the write comes only from `menu_file`, after `list_menu_weeks` gave the week (choice 8). `dishes_for` hides the order of `Settings.dishes`, and `Context.random` defaults to a new `Random(0)`, so a test that builds a context gets fixed choices (3.3). On the model, a file with CR LF line ends and a byte order mark keeps the text of every line and gets LF line ends and no mark. Quoted headers and keys and a comment after `[]` keep their text. A meal written as `lunch = [` with `]` on the next line stops at step 8, before any recipe is read. A day in dotted keys or in braces gets `CANNOT_FILL`. A file with no LF at its end gets one before a new table. A read-only menu file gives `menus\2026-W48.toml`, `  The file cannot be written: access is denied.`, and `Nothing was changed.`, keeps its bytes, and leaves no `.tmp` file. Choice 7 now names the refused layout that Troy is likeliest to meet, and it is right. Sunday dinner of `tests/data/example/menus/2026-W47.toml` is a list over five lines, and deleting its three dishes leaves `dinner = [` and `]`. `read_week_menu` reads that meal as empty, and only the last row of the table of places in 2.2 fits its line, so step 8 stops with `CANNOT_FILL` before any recipe is read. The v0.2-S15 item now says that the move gives `menus\` a new modification time and that step 1 counts files, not folders, which matches "the only file whose bytes or time changed" in the expected result of v0.2-S15 in the v0.2 test plan (note 4 of round 1). |
| Changes an implemented interface only through the change flow | Pass | The PR adds only the two design files. Section 3 adds to `settings`, `app`, `cli`, and `datafile` only what F05's design and architecture 5.1 and 5.2 plan for F14: a field and a method with defaults, a field with a default, an optional parameter, and two new names. No call of an exported name of F01 to F13 breaks. The requirements already name the setting, so no requirement changes, and the Architect reviews the additions here, as it reviewed F11's `create_file` and F13's `replace_file`. With the model of section 3 and `MENU_SUGGEST_COMMAND` in `COMMANDS`, the whole suite gave 577 passed, 6 failed, and 4 skipped on Windows in round 1. The 6 failures are exactly F05-T10, F05-T11, F11-T32, F13-T01, F13-T22, and F13-T27, which section 3 names, and the 4 skips are main's Linux-only cases. So the plan of section 2 holds: a test-fix PR before the mock changes the four tests that the entry breaks, and F05-T10 and F05-T11 change in that PR or in F14's tests PR, because the mock leaves `read_settings` as it is. The mock's 10 files and the implementation's 9 files and about 700 lines exceed R03's limits, and their soft-limit reason is right: the tests reach the settings, the context, and `datafile` both directly and through `menu suggest`. Note 5 of round 1 asks that the six tests hold whatever lines and keys F15 and F16 add later, for example by passing the eight commands of v0.1 with `commands=`, as F11-T01 does. It goes to the Test Manager's brief for the F14 test plan, so section 3 rightly stays as it is. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary at the top of PR #102, at commit e74d593, says what the design says. Finding 1 is fixed in both languages. What changes for Troy now says that every line keeps its text apart from the `[]` of each meal that gets dishes, that a missing meal line or day is added, and that a file saved with Windows line ends or a byte order mark gets Unix line ends and no mark, as the requirement table and choice 7 now say. Note 6 is taken: the first risk names Sunday dinner of the example week emptied to `dinner = [` and `]`, as choice 7 now does, and the English help line says that the second column moves. The rest is as in round 1: the new command and `--tag`, the swap, the fill from Monday on, the setting, and the help; then points A to D as items 1 to 4, each with its options and a recommendation with its reason; then the three risks. The 19 texts of point A are still the 15 messages of `suggest` and the 4 of `settings` that no prototype shows. The Architect found no other point for Troy to decide. The checks of troy-check's `summary.py`, run on the description, all pass. The Chinese part has 1,016 characters and the English part 1,969, within R22's 2,000. Both have the three parts in order and a recommendation in each of their 4 items, and neither holds an internal ID. The English part has 31 characters left, so a later change to it must stay short. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | Finding 1 (the seventh item) blocks. In "What changes for you", the line "Only the `[]` of each filled meal changes" ("文件里只有被填的那一餐的 `[]` 会变") is not what choice 7 says for a file saved with CR LF line ends or a byte order mark. Such a file gets LF line ends and loses its mark, because architecture 5.1 has every file that the tool writes in UTF-8 with no mark and with LF line ends, and the model showed it. The requirements say that the rest of the file stays as it is, so Troy must see this before approving. Ask: in both languages, say that a file saved with Windows line ends or a byte order mark gets Unix line ends and no mark, and that every line keeps its text. The English part has 117 characters left. The Architect checked the 12 choices, section 3, and points A to D against the requirements, the architecture, ADR-0001, ADR-0002, ADR-0008 to ADR-0010, the designs of F05, F06, F11, and F13, the F05 and F14 prototypes, and v0.2-S01 to v0.2-S08 and v0.2-S14 to v0.2-S16. The two files have the same 14 headings and 171 table rows, and 18 code blocks, each equal to its mirror, with no invisible character. With Python 3.13.18 on Windows, the Architect built a model of section 2 and section 3 in a copy of main's `src/` and ran the 8 examples of each file. All 72 assertions and all 8 `# raises` hold, once the example of 2.1 imports `UsageError` (note 3). The two helps of 2.1 equal the model's help line for line, and `recipe-menu menu` gives the line of choice 1. Items 6 and 7 give the whole suite and the PT01 runs. The Linux results were not run. Notes 1 to 6 do not block. | Changes requested. The Interface Designer fixes finding 1 in both languages of the summary, and can take notes 1 to 6 in the design. If Troy chooses option 1 of point D, the Architect's `[docs]` PR also adds the dishes of each meal to the `Settings` row of architecture 5.2. |
| 2 | No finding blocks. The Architect compared version 0.2 with the version of round 1 in both files. The changes are the requirement table, choices 7 and 11, the v0.2-S15 item, 3.3, 3.4, the import of the example of 2.1, the header, and the change log, each the same in both languages. The requirement table and choice 7 now say what finding 1 asked the summary to say, and the design takes notes 1, 2, 3, 4, and 6. Note 5 goes to the Test Manager's brief. The two files have the same headings and table rows, and 18 code blocks, each equal to its mirror, with no invisible character. The only change in a code block is the import of `UsageError`, so the run of the examples in round 1 still holds, and the model was not run again. The Linux results were not run. | Approved. Under either option of point D, architecture 6 changes. So the Architect's `[docs]` PR records Troy's choice in architecture 6 and an ADR, at the time that point D gives, and also adds the dishes of each meal to the `Settings` row of architecture 5.2. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-17 | First draft. |
| 0.2 | 2026-11-17 | Round 1 of the Architect review. The requirement table and choice 7 say that a file saved with CR LF line ends or a byte order mark keeps the text of every line and gets LF line ends and no mark, and choice 7 names the refused layout that you are likeliest to meet. Choice 11 gives the measured cost of `import random`. The v0.2-S15 item says that the folder `menus\` gets a new modification time. 3.3 and 3.4 give the `# noqa: S311` of `Random(0)` and `Random()`. The example of 2.1 imports `UsageError`. |
| 1.0 | 2026-11-17 | Approved by Troy. |
