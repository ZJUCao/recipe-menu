---
troy-doc: "F13-design"
lang: "en"
version: "1.0"
updated: "2026-11-15"
status: "Approved by Troy on 2026-11-15"
mirror: "design.zh-CN.md"
---

# F13 Shopping list command: interface design

## 1. Feature

- ID and name: F13 Shopping list command
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F02, F12

## 2. Interfaces

F13 builds the command module `shop` in `src/recipe_menu/commands/shop/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.shop` exports one name, `SHOP_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu shop` (2.2). Its messages live in `src/recipe_menu/commands/shop/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F13 adds `SHOP_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `MENU_SHOW_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). F13 also adds to `datafile` the write that replaces a file, `replace_file`, with one internal message (section 3). The F13 prototype `docs/prototypes/F13-shop.md` shows the command, and the F05 prototype shows its line in the help.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F13 gives |
| --- | --- |
| `recipe-menu shop [WEEK]` prints the shopping list in the chosen language ([requirements 4](../../requirements.md#4-features)). | `recipe-menu shop` (2.2), with `SHOP_COMMAND` (2.1). It builds the list with F12's `build_shopping_list` and writes it in the layout of choice 4. |
| It saves the list as the Markdown checklist `shopping/<week>.md` (requirements 4). | The file of choice 5, written through `replace_file` (3.1). |
| `shop` writes only its own file in `shopping/`, and replaces the file of the same week. v0.1 changes no other file ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | `replace_file` writes a temporary file in `shopping/` and moves it over the week's file, and `shop` writes nothing else (choice 6, [architecture 6](../../architecture.md#6-error-handling)). |
| A command that takes a week accepts an ISO week, `this`, or `next`. Without a week, it uses this week (requirements 3). | F06's `week_from_argument` and `NOT_A_WEEK` (choice 2). |
| Every message follows the language (requirements 3). | Every text comes from `shop/messages.py`, the catalog's names, and `amount_text`, in `context.lang` (choices 4, 5, and 8). |
| A command exits with 0 when it worked, 1 when the data has an error or a file is missing, and 2 when the command line is wrong (requirements 3). | The table of exit codes in 2.2. |
| `shop` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus (PT01, [requirements 7.1](../../requirements.md#71-performance-targets)). | The performance target of 2.2, and choice 10. |

These rules hold for every interface below:

- `shop` imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `menus`, and `shopping` from the package. Its row of architecture 3 allows them. It needs neither `units` nor `settings`, and it never imports `menu`, `browse`, or another command module ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `shop` reaches the disk only through the readers of F03, F04, and F06 and through `replace_file`, all of which work through `datafile` (architecture 8). It writes only the week's list file, the temporary file of 3.1 while it writes that file, and the folder `shopping/` when nothing is at that path (point C) ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 1](../../architecture.md#1-context-and-constraints)). It writes only to `context.out` and `context.err`. It reads nothing of the outside world itself, and it keeps no state. The recipes and the list that it builds live for one run only, so no module keeps a cache (architecture 8).
- A reader never raises for bad data, and `replace_file` turns each `OSError` into a value ([architecture 6](../../architecture.md#6-error-handling)). `shop` stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). `run` raises a `UsageError` only for a value of `WEEK` that is not a week, before it touches the disk or writes any output (F05 design, section 2). Any other exception that reaches `cli` is a bug.
- `SHOP_COMMAND` is a frozen `Command` value (F05 design 2.5). `replace_file` gives F11's `FileCreation` (F11 design 3.2), so F13 adds no value type.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- `recipe-menu shop` has the performance target PT01 (choice 10). It reads each file that it needs once, writes the list file once, and writes its output once, after the file. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 and 3.1 give their rules.

1. **One command, after `menu show` in the help.** F13 adds `SHOP_COMMAND` to `COMMANDS` after `MENU_SHOW_COMMAND`, the last place of the help's order of F05 design section 2. So `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, SHOP_COMMAND)`. `shop` has `FolderUse.READ`, so `cli` stops it when the data folder is missing or the settings have an error (F05 design 2.5). It declares the optional argument `WEEK`, as F05's design planned, and no option. So the help writes `shop [WEEK]` and `shop [周]`, of 11 and 9 columns. The widest first cell stays `menu show [WEEK]`, of 16 columns, so the second column of both tables still starts after 21 columns in both languages. The help gets one line more, 21 in all, and it is then the two helps of the F05 prototype in full (2.1). Section 3 lists the tests of the real help, which all stay true.
2. **The week.** `shop` gets its week as F11's commands do (F11 design, choice 2): `week_from_argument(value, context.today)` (F06 design 2.7), where `value` is the value of `WEEK`, or `None` when the line gives none. Any other text than an ISO week, `this`, or `next`, such as `2026-W99`, gives `UsageError(NOT_A_WEEK, None, week=value)`, and `cli` writes the message alone and exits with 2 (ADR-0008, decision A). `run` raises it before it touches the disk or writes any output. Every later line names the week as `str(week)`, such as `2026-W47` for `next`. `shop` builds the file's path with `context.folder.shopping_file(str(week))` only after `week_from_argument` gave a week, so the name always passes the check of `shopping_file`, which raises `ValueError` for a wrong name (F03 design 2.1).
3. **What `shop` reads, and where it stops.** `shop` reads only the files that it needs: the settings in `cli`, the catalog, the pantry, the menu, and only the recipes that the menu names (architecture 8). It reads them in the order of `menu show` (F11 design, choice 7), with the pantry after the catalog, as the F11 and F12 designs plan for F13 (2.2):
   - It reads the catalog with `read_catalog`, because `read_pantry` and `read_recipe` need it (F03 design 2.9, F04 design 2.6).
   - It reads the pantry with `read_pantry(context.folder, catalog)`. So a mistake in the pantry stops `shop` whatever week you ask for, as a mistake in the catalog does.
   - It lists `recipes/` once with `list_recipe_ids`, and passes the IDs to `read_week_menu` as a `frozenset` (F06 design, choice 4).
   - It lists `menus/` once with `list_menu_weeks` and looks for the week among the weeks that it gives (F06 design 2.8). An error of that listing stops `shop`, also when it names another file, as it stops `menu show`. A week that the listing lacks gives `NO_MENU` of `menus` (F11 design 3.1) on the error stream and exit code 1.
   - It reads the week with `read_week_menu` and `context.settings` (F06 design 2.9).
   - It reads each recipe that a dish names with `read_recipe`, once, in the order of the first dish that names it: Monday to Sunday, the meals in the order of `menu.meals`, and the dishes in the file's order. It keeps them in a dictionary for one run and passes that dictionary to `build_shopping_list` (F12 design, choice 2). A recipe that the menu does not name is not parsed, so an error in it does not stop `shop`.

   The first error of each reader stops `shop` with `first_error` and `stop_at_error`, which write the problem and `RUN_CHECK` and give 1 (F05 design 2.8). `check` reads the same files with the same readers and arguments, so the error that stopped `shop` is among the errors of `check` (F07 design, choice 8). `shop` writes no warning, and a warning never changes the exit code (architecture 6). So `shop` passes `build_shopping_list` only values that the readers gave with no error, from one catalog, and it never meets the `ValueError` of F12 design 2.5. After an error or `NO_MENU`, `shop` reads nothing more and writes no file. It never reads the list file of the week or another file in `shopping/`.

   `shop` keeps its own few lines that read the catalog and stop at the first error of a reader. The same lines repeat in `browse`, `search`, and `menu`, as the Code Reviewer of F11's implementation noted. `shop` may not import those modules (architecture 3). So sharing the lines needs a new exported helper in a module that all four may import, such as `app`, and taking out the copies changes `browse`, `search`, and `menu`, three implemented modules that F13 does not build. F13's mock and implementation are already near R03's limits without that (the last paragraph of section 2). So F13 keeps its copy, and a later `[refactor]` PR can add the helper and use it in all four commands. For the same reason, `shop` defines its own `WEEK_ARGUMENT`, `MEAL_COUNT`, and `DISH_COUNT`, with the texts of the internal messages of `menu` (F11 design 2.2 and 2.4).
4. **The list in the terminal.** The output of a saved list has four blocks, with one empty line between two blocks: the heading, the groups, the pantry line, and the line that names the saved file (2.2).
   - The heading is `LIST_HEADING`, with the week, its `date_range` (F06 design 2.1), and the counts `meal_count` and `dish_count` of the list (F12 design, choice 9) as `MEAL_COUNT` and `DISH_COUNT`. These are `Plural` values (F02 design 2.4), so the English is right for one meal and one dish, as in F11's count line.
   - The groups follow `shopping.groups`, in their order (F12 design, choice 1). Each group starts with its category's name, `group.category.name.get(context.lang)`, with no indent. One line follows for each `ShoppingLine` of the group: two spaces, the ingredient's name `line.ingredient.name.get(context.lang)`, padded to the width of the widest name of the whole list, three spaces, and `line.amount_text(context.lang)` (F12 design 2.2).
   - The lines of each group are `format_table(rows, indent=2, min_widths=(width,))` (F02 design 2.9), where `width` is the largest `display_width` of a name in the whole list. So the amounts of every group start at one column, as the two tables of the help do (F05 design 2.10). The Architect suggested in the F02 review one table for all groups, with the headings between its lines, which works while no cell has a line break. A catalog name may hold one, and `format_table` then gives its row two lines, so one table for each group, with one width, keeps every heading in its place and gives the same lines otherwise.
   - The widest names of the prototype are `Chicken wings`, of 13 columns, and `郫县豆瓣酱`, of 10 columns. So the amounts start 16 and 13 columns after the indent, as the prototype shows. Another week gets the width of its own names, as `menu show` and `search` do (F11 design, choice 8).
   - A name is written as the catalog holds it, as `menu show` writes a recipe name. A name that lacks the chosen language shows the other one through `BiText.get`.
5. **The saved file.** The file is the Markdown checklist of the F13 prototype "The saved file", in the language of the run: "A run in English writes the same list in English." Its text is these blocks, with one empty line between two blocks, and each line ended by LF (2.2):
   - the title, `# ` and `FILE_TITLE`, such as `# 2026-W47 购物清单`;
   - the line of the dates and the counts, `FILE_DATES`, such as `2026年11月16日至22日：4 餐，9 道菜。`;
   - for each group, the heading `## ` and the category's name, and then a block of one line for each `ShoppingLine`: `- [ ] `, the ingredient's name, a space, and `amount_text`, such as `- [ ] 番茄 600 g`;
   - the pantry line of choice 8, when the menu uses a pantry ingredient.

   The file is UTF-8 with no byte order mark and with LF line ends (architecture 5.1). So after the Chinese run of the example week, its bytes are those of the prototype's file, and the English run gives `# Shopping list for 2026-W47` and `16 to 22 November 2026: 4 meals, 9 dishes.` at its top (point A). `# `, `## `, and `- [ ] ` are Markdown signs that belong to no language, so they are in the code, not in the messages, and a name is written with no Markdown escape (architecture 8). Each run replaces the file of its week, so a list that you ticked on your phone loses its ticks when you run `shop` for that week again, as requirements 3 has it: `shop` "replaces the file of the same week".
6. **How `shop` saves the file.** `datafile` writes every file (architecture 2, 3, and 8). `create_file` refuses an entry that is already there, so `shop` cannot use it (ADR-0010). So F13 adds `replace_file(folder, path, text)` to `datafile` (3.1), the write that architecture 6 gives a file that is replaced: a temporary file in the same folder, moved over the old file. `shop` calls it once, with `path = context.folder.shopping_file(str(week))` and the text of choice 5. `replace_file` takes these steps:
   1. It makes sure that the file's folder is there. When nothing is at `shopping`, it creates that one folder (point C). When something other than a folder is there, it gives `FAILED`.
   2. It removes the temporary file `shopping/2026-W47.md.tmp` when an earlier run left it, such as after a power cut.
   3. It creates the temporary file in exclusive mode, writes the whole text with one `write`, and closes it.
   4. It moves the temporary file over `shopping/2026-W47.md` with `os.replace`, which replaces an old file in one step.

   `shop` acts on the result:
   - **`CREATED`.** `shop` writes the output of choice 4 to the output stream and gives 0. The last line is `SAVED` with the file's full path, `str(path)`, as the prototype shows.
   - **`FAILED`.** `shop` writes three lines to the error stream and gives 1, and nothing goes to the output stream. The first line is the full path of the list file, `str(context.folder.root / problem.file)`, because every problem of `replace_file` names the file that it could not write. Architecture 6 and section 3 of ADR-0009 let `shop` name a file that it could not write by its full path, and this design uses that case, as section 5 of ADR-0009 asks a design to say. The second line is two spaces and `problem.text(context.lang)`, such as `The file cannot be written: access is denied.`, F08's `FILE_WRITE_DENIED`. The third line is `NO_FILE_SAVED`, `No file was saved.`, or `LEFT_BEHIND` with the temporary file's full path when `replace_file` could not remove it (point A). The output stream gets no list: every list on the screen ends with the line that says where the file is.
   - **The old file stays.** Only the move changes the file of the week, so the old file keeps its bytes whenever `replace_file` gives `FAILED`, and a reader of the file sees the old text or the new text, never a part. When another program, such as a sync tool or an editor, holds the file open, Windows can refuse the move. `shop` then reports `The file cannot be written: access is denied.`, and you run `shop` again.
   - **Ctrl+C.** `replace_file` removes the temporary file in a `finally` block, and `cli` exits with 130 and writes nothing more (F05 design 2.10). So a Ctrl+C leaves the old file or the new file, whole. As for `init` and `menu new`, a Ctrl+C inside `open`, after the system created the temporary file but before the call recorded it, can leave that file (F08 design, choice 5). The next run of `shop` for that week removes it before it writes (step 3 of 3.1).
7. **A week with no dish, and a list with nothing to buy.** A menu with no dish gives a list whose `dish_count` is 0 (F12 design, choice 9). `shop` then writes `NO_DISHES`, the prototype's line `The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved.`, to the output stream, and gives 0. It calls no `replace_file`, so it creates no folder and writes no file, and the old file of the week, if any, stays (v0.1-S14). A menu whose dishes use only pantry ingredients, or only recipes with no ingredients, gives a list with dishes and no group. `shop` then writes the heading, `NOTHING_TO_BUY`, `There is nothing to buy.`, in place of the groups, the pantry line when the menu uses a pantry ingredient, and `SAVED`. It saves the file, whose text has `NOTHING_TO_BUY` in place of the groups. The week has dishes, so its file follows its menu: without the save, a list from an older menu of the week would keep items that the menu no longer needs. The line `There is nothing to buy.` is new, for Troy (point A).
8. **The pantry line.** The line names the pantry ingredients that the menu uses, in the order of `shopping.pantry_used` (F12 design, choice 6): `PANTRY_LINE` with `comma_list` of their names (F02 design 2.6). The Chinese line is the prototype's, `常备，不用买：食用油、盐、糖、生抽、花椒`. The prototype's English line writes `cooking oil, salt, sugar, soy sauce, Sichuan pepper`, and v0.1-S16 expects `cooking oil, salt, sugar`. The catalog writes `Cooking oil`, `Salt`, `Sugar`, `Soy sauce`, and `Sichuan pepper`, and no rule turns those names into the prototype's line (F03 design, section 2). Troy decides the line (point B). This design follows option 1, the recommendation: the names as the catalog writes them, `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper`. A menu that uses no pantry ingredient gives no pantry line, in the terminal or in the file.
9. **Numbers in messages.** The messages of `shop` show the number of meals and of dishes, which F12 counts in memory, and the dates of a week, which come from `IsoWeek`. An amount goes into a line through `amount_text`, which never raises for a line that `build_shopping_list` gave (F12 design, choice 10), and not through a message. A wrong week goes into `NOT_A_WEEK` as text. A problem in a file reaches the error stream only through `stop_at_error` or the failure lines of choice 6, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `shop` meets F02's limit of 4,300 digits (F02 design 2.3).
10. **Speed.** PT01 asks that `shop` build and save the list of one PT01 week within 1 second on Troy's PC, the median of 5 runs (v0.1-S32). The week holds 63 dishes from 63 different recipes. `shop` reads what `menu show` reads, plus the pantry of 10 items, and `menu show 2026-W26` takes a median of 0.187 s on Troy's PC (F11's PT01 baseline). `build_shopping_list` takes a median of 5.19 ms on that week (F12's implementation), and gives about 290 lines in 6 groups. `amount_text` takes about 1 ms for those lines in one language, and the F12 review measured 1.9 ms for both. `format_table` measures about 290 rows of two short cells once, and the Markdown text holds the same lines once more. `replace_file` makes one probe, one removal of a missing file, one open, one `write` of about 10 KB, one close, and one move, which take some milliseconds. In the F12 design review, a stand-in for `shop` that read these files, built the list, printed it, and wrote a Markdown file took a median of 0.222 s on Troy's PC, against 0.209 s for `menu show` in the same runs. So `shop` should take about 0.2 s, far below 1 second. This is an estimate, not a measurement. The test plan can time `shop` on a PT01 folder, as F11-T38 times `menu show`. The PT01 folder of `tests/pt01_support.py` has no `shopping/`, so the first run creates it (choice 6), and later runs replace the file.
11. **Only the command is exported.** `shop` exports `SHOP_COMMAND` and nothing else. Only `cli` may import `shop` (architecture 3), so no other name would have a user.

The v0.1 scenarios that run `shop` hold with these choices, apart from the English pantry line, which point B sends to Troy:

- v0.1-S08: files with a byte order mark and CRLF line ends read the same (F03 design 2.3), so `shop 2026-W47` prints the output of F13 "In English" and exits with 0. The saved file is UTF-8 with no byte order mark and with LF line ends (choice 5).
- v0.1-S14: `shop` and `shop next` read the two empty menus that `menu new` created, print `NO_DISHES` with `<T>` and `<N>`, and exit with 0. `shopping\` stays empty (choice 7).
- v0.1-S15: step 3 prints `NO_MENU` for 2026-W48 and exits with 1. Step 5 prints the same three lines as `menu show` for `tomato-eggs` and exits with 1, because `shop` reads the same files as `menu show` up to the menu, and the pantry before them has no error (choice 3). `shopping\` stays empty.
- v0.1-S16: `shop 2026-W48` starts with `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish`, lists Tomato 450 g and Scallion 2 stalks under Vegetables and fruit, then Egg 5 pieces under Eggs, dairy, and tofu, and exits with 0. Its pantry line follows point B. Under option 1, the line ends with `Cooking oil, Salt, Sugar`, and the scenario's expected line changes with the prototype.
- v0.1-S17: step 1 prints the output of F13 "In English" and saves the English list, with one `- [ ]` line for each item. Step 2 prints the output of F13 "In Chinese" and replaces the file with the prototype's file, byte for byte. `shopping\` then holds only that file, because the move leaves no temporary file (choices 4 to 6).
- v0.1-S18: the Scallion and Soy sauce lines show `5 stalks + 1 bunch` and `30 ml + 10 g`, and the Chinese run shows `5 根 + 1 把`, as `amount_text` writes them (F12 design, choice 4).
- v0.1-S23: two runs of `shop 2026-W47` change only `shopping\2026-W47.md`, and `shopping\` holds no other file. The folder `shopping\` gets a new modification time, as a folder does when a file in it is added or replaced.
- v0.1-S25: the Chinese list lines up in Windows Terminal, because `format_table` measures display width (F02 design 2.8).
- v0.1-S26: the saved Chinese file is the prototype's checklist, with the title, six categories, 14 items, and the pantry line, in UTF-8.
- v0.1-S32: PT01 (choice 10). The run prints the list and saves its file.

Troy decides these three points. The design follows the recommendation of each.

- **A. New texts.** No prototype shows these texts. Each follows the wording of a text that a prototype shows. The recommendation is to accept them as 2.2 and 3.1 give them. They are 11 texts:
  - The top of the English file, for the prototype's Chinese file: `# Shopping list for 2026-W47` and `16 to 22 November 2026: 4 meals, 9 dishes.`.
  - The Chinese line for a week with no dish: `2026-W46 的菜单没有菜，所以没有要买的东西。没有保存文件。`.
  - The line for a list with nothing to buy (choice 7): `There is nothing to buy.` and `没有要买的东西。`.
  - The last line of a failed save (choice 6): `No file was saved.` and `没有保存文件。`, the end of the prototype's line for a week with no dish. When the temporary file could not be removed: `No file was saved, but shop could not remove C:\Users\Troy\recipe-menu\shopping\2026-W47.md.tmp. Delete it.` and `没有保存文件，但 shop 没能删除 C:\Users\Troy\recipe-menu\shopping\2026-W47.md.tmp。请删除它。`.
  - The problem when `shopping` is not a folder (3.1): `The file cannot be written: "shopping" is not a folder.` and `无法写入文件：“shopping”不是文件夹。`.
- **B. The English pantry line** (choice 8). The prototype's English line writes four catalog names with a small first letter and keeps `Sichuan pepper`, and v0.1-S16 expects `cooking oil, salt, sugar`. The prototypes and the scenarios are Troy's, so changing them goes through the requirement change flow, which Troy approves.
  - Option 1, recommended: the names as the catalog writes them: `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper`. The English pantry line of the F13 prototype and the expected line of v0.1-S16, `Cooking oil, Salt, Sugar`, change. v0.1-S08 and v0.1-S17 compare with the prototype, so they follow it. The Product Manager makes the change in a `[docs]` PR, which Troy approves, before the F13 test plan. The catalog and the code of F03 stay as they are.
  - Option 2: the catalog gets a second English name for an ingredient inside a sentence, such as `cooking oil`, and the line uses it when the catalog gives it. The F13 prototype and the scenarios stay. The catalog of `example-data.md`, which `init` writes and the tests copy, gets those names, and `Ingredient`, `read_catalog` (F03), and their tests change, all through the change flow before F13's mock PR. This design then changes choice 8.
  - Option 3: every English name of the line starts with a small letter: `cooking oil, salt, sugar, soy sauce, sichuan pepper`. v0.1-S16 stays, and the prototype's last name changes to `sichuan pepper` through the change flow. A proper name or an abbreviation in the catalog then comes out wrong in that line.
  - The reason for option 1: the line then writes each name as you wrote it in the catalog, as the headings and the lines of the list do, so it never gets a name wrong, and no file or reader changes. The Architect recommended it at F03's review.
- **C. A missing `shopping` folder** (choice 6), open since the requirements. `init` creates `shopping\`, and you can delete it. Git keeps no empty folder, and neither the example data of the tests nor their PT01 folder has a `shopping\`.
  - Option 1, recommended: `replace_file` creates the file's folder when nothing is at that path, with one `Path.mkdir` and no parents. A folder that it created stays when a later step fails. When something other than a folder is there, `shop` stops with the failure lines and `The file cannot be written: "shopping" is not a folder.`.
  - Option 2: `replace_file` creates no folder. Nothing at `shopping` gives `FAILED` with F04's `FOLDER_MISSING`, `The folder is missing.`, under the list file's full path. You create the folder and run `shop` again. Choice 6, 3.1, and the examples change before the mock PR.
  - The reason for option 1: only `shop` writes in `shopping\` (requirements 3), and no command reads it, so creating the folder changes nothing that you wrote. A data folder that lost its empty `shopping\`, such as a copy or a folder kept in git, still gets its list. Neither option changes a requirement: requirements 3 names the files that `shop` writes and replaces, and a folder is not a file.

These later features are meant to build on F13. Their own designs decide the details.

- F14's `menu suggest` (v0.2) fills the empty meals of an existing menu file, so it replaces that file. It can write the file with `replace_file` as it is. `suggest` may not import `shop` (architecture 3), and `shop` exports only its command, so F14 takes nothing else from F13.
- F15's `add` writes a new recipe with `create_file`, which never overwrites, and F16's `edit` writes no file. Neither takes anything from F13.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/shop/__init__.py`, `messages.py`, and one internal file for `run`, such as `_run.py`, and the entry in `src/recipe_menu/cli/_commands.py`. It adds `replace_file` to a new internal file of `datafile`, such as `_replace.py`, and to `src/recipe_menu/datafile/__init__.py`, and `PARENT_NOT_A_FOLDER` to `src/recipe_menu/datafile/messages.py`. It changes the doc comments of `FileOutcome` and `FileCreation` in `src/recipe_menu/datafile/_new_file.py` so that they name `replace_file` too. It defines every message and `SHOP_COMMAND` with all its fields. Its `replace_file` touches nothing and gives `FileCreation(FileOutcome.CREATED)`, and its `run` reads no file, writes nothing, raises nothing, and gives 0. So a new test fails against the mock (R09) when it checks an output line, exit code 1, `NOT_A_WEEK` with exit code 2, the bytes of the saved file, a new `shopping\`, a failure and its lines, a `FAILED` result or the problem of `replace_file`, or an error that `replace_file` raises. These tests pass against the mock and break R09: a test that checks only the fields of `SHOP_COMMAND`, the help, a message, or exit code 0. So does a test of what `cli` does before it runs `shop`, such as a missing data folder, broken settings, `shop 2026-W47 2026-W48`, `shop --tag x`, or `shop next --help`. So does a test that checks only that `shop` changes no file, as for a week with no dish, `NO_MENU`, or an error, or that `shopping\` stays empty, as v0.1-S14 and v0.1-S15 do. So does a test that checks only that a failed save keeps the old file, or only that `replace_file` gives `CREATED`. Each such test must also check something that the mock gets wrong, such as the output, the file, or the result. The mock changes 8 files, more than R03's 5, in about 280 lines by estimate, so its description gives a soft-limit reason. The reason is that the tests reach `replace_file` both directly and through `shop`, so `shop` and `datafile` come in one stage, as in F08's and F11's mocks. The implementation (PR 5) holds `run` with its reads and its output in internal files of `shop`, such as `_run.py`, `_read.py`, and `_output.py`, and `replace_file` in `_replace.py`. By estimate, it changes 4 files in about 450 lines, within R03 but close to its 500. `_replace.py` can import `_remove_all` from `_creation.py`, as `_new_file.py` does, with no change to `_creation.py`. If its doc comments take it past 500 lines, its description gives a soft-limit reason, so the Developer runs troy-check early.

### 2.1 `SHOP_COMMAND`

- Module: shop
- Purpose: The description of the `shop` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` makes the list of 2.2 and saves it.

Signature:

```python
SHOP_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("shop",)
#   help_line = SHOP_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(WEEK_ARGUMENT, required=False)
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("shop",)`. | None |
| `help_line` | `Message` | `SHOP_HELP`: "Make the shopping list of a week menu." and "生成一个周菜单的购物清单。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Turns the argument into a week, reads the files of choice 3, builds the list, saves it through `replace_file`, and writes the output of 2.2. | Gives 0 or 1. Raises `UsageError` for a value that is not a week, before it touches the disk or writes any output. Raises nothing for bad data or for a failure on the disk. |
| `argument` | `Argument` | `Argument(WEEK_ARGUMENT, required=False)`, which is optional and does not repeat. `WEEK_ARGUMENT` is `WEEK` and `周`, the names in the F05 prototype's help. | So `cli` passes no value or one value (F05 design 2.5). |
| `options` | A tuple of `str` | `()`. `shop` has no option of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `shop` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses `context.lang`, `context.folder`, `context.settings` for `read_week_menu`, `context.out`, `context.err`, and `context.today`. |
| `arguments` | `Arguments` | What the command line gives `shop` (F05 design 2.6). | `arguments.values` is `()` or holds one value, such as `("next",)`. It has no options. |

- Return value: `SHOP_COMMAND`, a `Command`.
  - `SHOP_COMMAND.usage` is `shop [WEEK]` in English and `shop [周]` in Chinese. So the help shows them, and a usage error quotes `recipe-menu shop [WEEK]` or `recipe-menu shop [周]`.
  - `SHOP_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its lines in `context.lang`, and gives 0 or 1.

After F13, the help lists these commands and options, with the second column after 21 columns (choice 1). They are the lines of the F05 prototype's helps. In English:

```text
Commands:
  init               Create the data folder with example data.
  check              Check every data file for mistakes.
  list               List the recipes.
  show ID            Show one recipe.
  search WORD...     Find recipes by name, ingredient, or tag.
  menu new [WEEK]    Create an empty week menu.
  menu show [WEEK]   Show a week menu.
  shop [WEEK]        Make the shopping list of a week menu.

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
  shop [周]          生成一个周菜单的购物清单。

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

- Side effects: Those of 2.2. `run` reads the catalog, the pantry, two listings, one menu file, and the recipes that the menu names through the readers of F03, F04, and F06, saves the list through `replace_file`, and writes to `context.out` or `context.err`.
- Performance target: None. PT01 times `recipe-menu shop` (2.2) from start to exit, which runs this `run`.

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, which has no `shopping/`, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context holds the default settings, which are the settings of the example, and the output follows `context.lang`. The run gives the output of the F13 prototype "In English", with the pantry line of option 1 of point B, and creates `shopping/` (option 1 of point C). `row` writes one line of a group, whose names are 13 columns wide (choice 4). Every character of the English list takes one column, so `str` padding gives the same lines as `format_table`. The help comes from `COMMANDS`, which holds the eight commands after F13. The call that raises touches no file and writes no line to either stream.

```python
import io
from datetime import date

from recipe_menu.app import Argument, Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.shop import SHOP_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import Message

assert SHOP_COMMAND.words == ("shop",)
assert SHOP_COMMAND.usage == BiText("shop [WEEK]", "shop [周]")
assert SHOP_COMMAND.help_line.render(Lang.EN) == "Make the shopping list of a week menu."
assert SHOP_COMMAND.help_line.render(Lang.ZH) == "生成一个周菜单的购物清单。"
assert SHOP_COMMAND.argument == Argument(Message("WEEK", "周"), required=False)
assert SHOP_COMMAND.options == ()
assert SHOP_COMMAND.folder is FolderUse.READ


def row(name: str, amount: str) -> str:
    return f"  {name:13}   {amount}"


out, err = io.StringIO(), io.StringIO()
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10))
assert SHOP_COMMAND.run(context, Arguments(("next",))) == 0
file = folder.shopping_file("2026-W47")
pantry = "Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper"
assert out.getvalue().splitlines() == [
    "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes",
    "",
    "Vegetables and fruit",
    row("Tomato", "600 g"),
    row("Choy sum", "1.5 kg"),
    row("Scallion", "5 stalks"),
    row("Ginger", "6 slices"),
    row("Garlic", "11 cloves"),
    "Meat and seafood",
    row("Minced pork", "100 g"),
    row("Chicken wings", "1 kg"),
    "Eggs, dairy, and tofu",
    row("Egg", "5 pieces"),
    row("Tofu", "1 block"),
    "Rice, flour, and oil",
    row("Rice", "640 g"),
    row("Noodles", "200 g"),
    "Seasonings",
    row("Doubanjiang", "15 ml"),
    row("White pepper", "to taste"),
    "Other",
    row("Cola", "2 cans"),
    "",
    f"Not on the list, because they are in the pantry: {pantry}",
    "",
    f"Saved {file}",
]
assert err.getvalue() == ""
text = file.read_bytes().decode("utf-8")
assert text.splitlines()[:7] == [
    "# Shopping list for 2026-W47",
    "",
    "16 to 22 November 2026: 4 meals, 9 dishes.",
    "",
    "## Vegetables and fruit",
    "",
    "- [ ] Tomato 600 g",
]
last = f"- [ ] Cola 2 cans\n\nNot on the list, because they are in the pantry: {pantry}\n"
assert text.endswith(last)
assert "\r" not in text
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]


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
assert len(english) == 21
assert english[11:13] == [
    "  menu show [WEEK]   Show a week menu.",
    "  shop [WEEK]        Make the shopping list of a week menu.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[11:13] == [
    "  menu show [周]     查看一个周菜单。",
    "  shop [周]          生成一个周菜单的购物清单。",
]

SHOP_COMMAND.run(context, Arguments(("2026-W99",)))  # raises UsageError
```

### 2.2 `recipe-menu shop`

- Module: shop
- Purpose: The command that prints the shopping list of a week menu in the chosen language and saves it as the Markdown checklist `shopping/<week>.md` ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 4, and [4](../../requirements.md#4-features)). The F13 prototype shows it.

Signature:

```text
recipe-menu shop [WEEK] [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `WEEK` | A text | The week of the menu: an ISO week such as `2026-W47`, `this`, or `next`. | Optional. Without it, this week. Any other text is a usage error (choice 2). |
| `--lang` | `en` or `zh` | The language of the output, of the saved file, and of every message. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `shop`. | None |

`shop` takes these steps, in order. Step 1 reads no file. Each step that reads a file uses what the earlier steps gave, and each one that finds an error stops the command (choice 3).

1. It turns the value of `WEEK` into a week with `week_from_argument(value, context.today)`. For a result of `None`, it raises `UsageError(NOT_A_WEEK, None, week=value)` (choice 2).
2. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `shop` gives `stop_at_error(context, error)` for the first one.
3. `read_pantry(context.folder, catalog)` gives `pantry` and its problems (F03 design 2.9). With an error among the problems, `shop` stops at the first one with `stop_at_error`.
4. `list_recipe_ids(context.folder)` gives `ids` and their problems (F04 design 2.5). With an error among the problems, `shop` stops at the first one with `stop_at_error`.
5. `list_menu_weeks(context.folder)` gives `weeks` and their problems (F06 design 2.8). With an error among the problems, `shop` stops at the first one with `stop_at_error`.
6. When `weeks` does not hold the week, `shop` writes `NO_MENU` with `week=str(week)` to the error stream and gives 1 (F11 design 3.1).
7. `read_week_menu(context.folder, week, context.settings, frozenset(ids))` gives `menu` and its problems (F06 design 2.9). With an error among the problems, `shop` stops at the first one with `stop_at_error`.
8. For each recipe ID that a dish of `menu` names, once, in the order of the first dish that names it, `read_recipe(context.folder, catalog, recipe_id)` gives the recipe and its problems (F04 design 2.6). With an error among the problems, `shop` stops at the first one with `stop_at_error`.
9. `build_shopping_list(menu, recipes, catalog, pantry)` gives `shopping`, where `recipes` maps each ID of step 8 to its recipe (F12 design 2.5).
10. When `shopping.dish_count` is 0, `shop` writes `NO_DISHES` with `week=str(week)` to the output stream and gives 0 (choice 7).
11. It builds the text of the file (below) and calls `replace_file(context.folder, path, text)` once, with `path = context.folder.shopping_file(str(week))` (3.1).
12. For `CREATED`, it writes the output below to the output stream and gives 0. For `FAILED`, it writes the three lines of a failure to the error stream and gives 1 (choice 6).

The warnings of steps 2 to 5, 7, and 8 change nothing (choice 3).

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `replace_file` gave `CREATED`. | The output stream: the list, the pantry line when there is one, and `SAVED`. |
| 0 | The menu of the week has no dish. | The output stream: `NO_DISHES`. No file is written. |
| 1 | The week has no menu file. | The error stream: `NO_MENU`. Nothing goes to the output stream. |
| 1 | A file has an error. | The error stream: the three lines of `stop_at_error`. Nothing goes to the output stream. |
| 1 | `replace_file` gave `FAILED`. | The error stream: the three lines of a failure. Nothing goes to the output stream. |
| 2 | The value of `WEEK` is not a week. | The error stream: `NOT_A_WEEK`, which `cli` writes, with no hint. Nothing goes to the output stream. |

`lang` is `context.lang`. `width` is the largest `display_width` of a line of a name of the list, `line.ingredient.name.get(lang)` for each line of each group, each name split by `str.splitlines`. The output of a saved list is these blocks, in this order, with one empty line between two blocks, each line ended by a line break:

1. `LIST_HEADING`, with `week`, `dates`, `meals`, and `dishes`.
2. When `shopping.groups` is not empty, for each group in its order: the line `group.category.name.get(lang)`, and then the lines of `format_table(rows, indent=2, min_widths=(width,))`, where `rows` holds `(line.ingredient.name.get(lang), line.amount_text(lang))` for each line of the group, in its order. When `shopping.groups` is empty, `NOTHING_TO_BUY`.
3. `PANTRY_LINE`, with `items`, only when `shopping.pantry_used` is not empty.
4. `SAVED`, with `file`.

The text of the file is these blocks, in this order, with one empty line between two blocks, each line ended by LF:

1. `# ` and `FILE_TITLE`, with `week`.
2. `FILE_DATES`, with `dates`, `meals`, and `dishes`.
3. When `shopping.groups` is not empty, for each group in its order: the line `## ` and `group.category.name.get(lang)`, and then the block of its lines, one for each line of the group, in its order: `- [ ] `, `line.ingredient.name.get(lang)`, a space, and `line.amount_text(lang)`. When `shopping.groups` is empty, `NOTHING_TO_BUY`.
4. `PANTRY_LINE`, with `items`, only when `shopping.pantry_used` is not empty.

So after the Chinese run of the example week, the file is the block of the F13 prototype "The saved file", each of its lines ended by LF, the last one included. A failure is three lines: `str(context.folder.root / problem.file)`, which is `str(path)`, then two spaces and `problem.text(lang)`, then `NO_FILE_SAVED` when the result's `left` is empty and `LEFT_BEHIND` with `file` otherwise. In this case on Windows, another program holds the old file open:

```text
PS> recipe-menu shop next
C:\Users\Troy\recipe-menu\shopping\2026-W47.md
  The file cannot be written: access is denied.
No file was saved.
PS> $LASTEXITCODE
1
```

The messages of `shop` are these. `MEAL_COUNT` and `DISH_COUNT` are `Plural` values (F02 design 2.4), each picked by its `count`. Their form "for more" is the form for every count other than 1. `shop` also uses `NO_MENU` of `menus` (F11 design 3.1), and the problems that the readers and `replace_file` give.

| Name | English | Chinese |
| --- | --- | --- |
| `SHOP_HELP` | `Make the shopping list of a week menu.` | `生成一个周菜单的购物清单。` |
| `WEEK_ARGUMENT` | `WEEK` | `周` |
| `LIST_HEADING` | `Shopping list for {week}, {dates}: {meals}, {dishes}` | `{week} 购物清单，{dates}：{meals}，{dishes}` |
| `MEAL_COUNT`, for one | `{count} meal` | `{count} 餐` |
| `MEAL_COUNT`, for more | `{count} meals` | `{count} 餐` |
| `DISH_COUNT`, for one | `{count} dish` | `{count} 道菜` |
| `DISH_COUNT`, for more | `{count} dishes` | `{count} 道菜` |
| `NOTHING_TO_BUY` | `There is nothing to buy.` | `没有要买的东西。` |
| `PANTRY_LINE` | `Not on the list, because they are in the pantry: {items}` | `常备，不用买：{items}` |
| `SAVED` | `Saved {file}` | `已保存 {file}` |
| `NO_DISHES` | `The menu for {week} has no dishes, so there is nothing to buy. No file was saved.` | `{week} 的菜单没有菜，所以没有要买的东西。没有保存文件。` |
| `FILE_TITLE` | `Shopping list for {week}` | `{week} 购物清单` |
| `FILE_DATES` | `{dates}: {meals}, {dishes}.` | `{dates}：{meals}，{dishes}。` |
| `NO_FILE_SAVED` | `No file was saved.` | `没有保存文件。` |
| `LEFT_BEHIND` | `No file was saved, but shop could not remove {file}. Delete it.` | `没有保存文件，但 shop 没能删除 {file}。请删除它。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `week` | `str(week)`, such as `2026-W47`. |
| `dates` | `week.date_range`, as a `BiText`: `16 to 22 November 2026` and `2026年11月16日至22日`. |
| `meals` | `MEAL_COUNT.pick(n).to_bitext(count=n)`, with `n` set to `shopping.meal_count`. |
| `dishes` | `DISH_COUNT.pick(n).to_bitext(count=n)`, with `n` set to `shopping.dish_count`. |
| `count` | The number of each `Plural`. |
| `items` | `comma_list(ingredient.name for ingredient in shopping.pantry_used)` (F02 design 2.6): `Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper` and `食用油、盐、糖、生抽、花椒`. |
| `file` | A full path. In `SAVED`, `str(path)`, the list file. In `LEFT_BEHIND`, `str(creation.left[0])`, the temporary file. `context.folder.root` is absolute (F05 design 2.4). |

With these messages, the lines of the F13 prototype follow in both languages, such as `Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes`, `2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜`, and `已保存 C:\Users\Troy\recipe-menu\shopping\2026-W47.md`, apart from the English pantry line of point B.

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `shop` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 2, with `NOT_A_WEEK` and no hint: `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | The value of `WEEK` is not a week (step 1). |
| Exit code 1, with `NO_MENU` on the error stream: `There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` | The listing of `menus/` holds no file for the week (step 6). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream, such as `menus\2026-W47.toml, Monday dinner`, `  Unknown recipe "tomato-eggs".`, and `RUN_CHECK` | The catalog, the pantry, the listing of `recipes/`, the listing of `menus/`, the week's menu file, or a recipe file that the menu names has an error (steps 2 to 5, 7, and 8). |
| Exit code 1, with the three lines of a failure on the error stream | `replace_file` gave `FAILED`: `shopping` is not a folder, it could not be created, or an `OSError` stopped the temporary file or the move (choice 6, 3.1). The old file keeps its bytes. |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT`, or with the first error of the settings and `RUN_CHECK`, on the error stream | The data folder is not a folder, or the settings have an error. `cli` checks both in step 9 of F05 design 2.10, because `shop` has `FolderUse.READ`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `Unexpected argument "2026-W48". Write "recipe-menu shop [WEEK]".` | The line names two weeks. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"shop" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. `replace_file` removes the temporary file, and `cli` writes nothing more (choice 6). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `shop` then reads `catalog.toml` and `pantry.toml` once, lists `recipes/` once, lists `menus/` once, reads the week's menu file once, and reads each recipe file that a dish names once, all through the readers of F03, F04, and F06. After a wrong week, it reads no file. After an error or a week with no menu, it reads nothing more. For a week whose menu has a dish, it calls `replace_file` once, which may create `shopping/`, writes and removes the temporary file, and creates or replaces the week's list file (3.1). It writes no other file, so every other file keeps its bytes and its modification time (v0.1-S23). It writes to the output stream or the error stream.
- Performance target: PT01

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, which has no `shopping/`, and `home` is an empty temporary folder outside it. The first run saves the English list and creates `shopping/`. The second run gives the output of the F13 prototype "In Chinese" and replaces the file with the prototype's file. The next runs give the first output of "No menu, or an empty menu", the error of a wrong week, and the lines of the F11 prototype "A menu with a mistake", which keep the file. A new menu for this week then gives the second output of "No menu, or an empty menu", in both languages. The last run meets a file named `shopping`.

```python
import io
import shutil
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


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


file = folder.shopping_file("2026-W47")
assert not folder.shopping.exists()
code, out, err = run("shop", "2026-W47")
assert (code, err) == (0, [])
assert out[0] == "Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes"
assert out[-1] == f"Saved {file}"

code, out, err = run("shop", "2026-W47", "--lang", "zh")
assert (code, err) == (0, [])
assert out == [
    "2026-W47 购物清单，2026年11月16日至22日：4 餐，9 道菜",
    "",
    "蔬菜水果",
    "  番茄         600 g",
    "  菜心         1.5 kg",
    "  葱           5 根",
    "  姜           6 片",
    "  大蒜         11 瓣",
    "肉类水产",
    "  猪肉末       100 g",
    "  鸡翅中       1 kg",
    "蛋奶豆制品",
    "  鸡蛋         5 个",
    "  豆腐         1 块",
    "米面粮油",
    "  大米         640 g",
    "  面条         200 g",
    "调味品",
    "  郫县豆瓣酱   15 ml",
    "  白胡椒粉     适量",
    "其他",
    "  可乐         2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
    "",
    f"已保存 {file}",
]
saved = [
    "# 2026-W47 购物清单",
    "",
    "2026年11月16日至22日：4 餐，9 道菜。",
    "",
    "## 蔬菜水果",
    "",
    "- [ ] 番茄 600 g",
    "- [ ] 菜心 1.5 kg",
    "- [ ] 葱 5 根",
    "- [ ] 姜 6 片",
    "- [ ] 大蒜 11 瓣",
    "",
    "## 肉类水产",
    "",
    "- [ ] 猪肉末 100 g",
    "- [ ] 鸡翅中 1 kg",
    "",
    "## 蛋奶豆制品",
    "",
    "- [ ] 鸡蛋 5 个",
    "- [ ] 豆腐 1 块",
    "",
    "## 米面粮油",
    "",
    "- [ ] 大米 640 g",
    "- [ ] 面条 200 g",
    "",
    "## 调味品",
    "",
    "- [ ] 郫县豆瓣酱 15 ml",
    "- [ ] 白胡椒粉 适量",
    "",
    "## 其他",
    "",
    "- [ ] 可乐 2 罐",
    "",
    "常备，不用买：食用油、盐、糖、生抽、花椒",
]
chinese_file = "".join(f"{line}\n" for line in saved).encode("utf-8")
assert file.read_bytes() == chinese_file
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

no_menu = 'There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.'
assert run("shop", "2026-W48") == (1, [], [no_menu])
week_error = '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
assert run("shop", "2026-W99") == (2, [], [week_error])

edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
week47 = Path("menus", "2026-W47.toml")
assert run("shop", "next") == (
    1,
    [],
    [
        f"{week47}, Monday dinner",
        '  Unknown recipe "tomato-eggs".',
        'Run "recipe-menu check" to see every problem.',
    ],
)
assert file.read_bytes() == chinese_file

assert run("menu", "new", "this")[0] == 0
nothing = "The menu for 2026-W46 has no dishes, so there is nothing to buy. No file was saved."
assert run("shop") == (0, [nothing], [])
nothing_zh = "2026-W46 的菜单没有菜，所以没有要买的东西。没有保存文件。"
assert run("shop", "this", "--lang", "zh") == (0, [nothing_zh], [])
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

edit(folder.menu_file("2026-W47"), '"tomato-eggs"', '"tomato-egg"')
shutil.rmtree(folder.shopping)
folder.shopping.write_text("", encoding="utf-8")
not_a_folder = '  The file cannot be written: "shopping" is not a folder.'
assert run("shop", "2026-W47") == (1, [], [str(file), not_a_folder, "No file was saved."])
assert folder.shopping.read_bytes() == b""
```

## 3. Changes to existing interfaces

F13 adds a name to the interface of one implemented module. `datafile`, which F03 created and F08 and F11 gave their writes, exports `replace_file` (3.1), the write that architecture 3 and 6 plan for `shop`. It also gets the message `PARENT_NOT_A_FOLDER` in `src/recipe_menu/datafile/messages.py`, which stays internal to `datafile`. `replace_file` gives F11's `FileCreation`, with the outcomes `CREATED` and `FAILED` only. `FileOutcome` and `FileCreation` keep their members, fields, and checks, and `create_file` keeps its behavior. Their doc comments, which now speak of the result of `create_file`, name `replace_file` too. No exported name of F01 to F12 changes its signature or its behavior, so their tests pass unchanged. The requirements do not change for these additions, so no `[docs]` PR approves them. The Architect reviews them in this design, as it reviewed F11's `create_file` and `NO_MENU`. The change to a prototype and a scenario under option 1 of point B goes through the requirement change flow on its own, and it changes no interface.

F13 also adds `SHOP_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, which is internal to `cli` and which architecture 4 gives each command feature. With it, the help of the real `recipe-menu` lists `shop` after `menu show`, with 21 lines in all, and the second column of its tables still starts after 21 columns (choice 1). The tests that run the real `COMMANDS` check only lines and columns that stay true:

- F05-T48 checks the first and the last line of the Chinese help, and F05-T49 checks no line of the help.
- F07-T17 checks that the line of `check` ends with its text, and that the text starts at the column where the text of `--lang en|zh` starts.
- F08-T14 checks the same of the line of `init`, and that the line of `check` follows it.
- F09-T01 checks that the lines of `list` and `show` follow the line of `check`, and that their texts start at that same column. F09-T19 and F09-T25 check that `list --help` and `show ... --help` give the same help as `--help`.
- F10-T01 checks that the line of `search` follows the line of `show ID`, starts with `  search WORD... `, and has its text at that same column. F10-T11, F10-T15, and F10-T16 check that `search` with `--help` gives the same help as `--help`, and that it holds the line of `search`.
- F11-T01 checks that the lines of `menu new` and `menu show` follow the line of `search`, and that their texts start at that same column. F11-T27, F11-T32, and F11-T35 check that `menu` with `--help` gives the same help as `--help`, and F11-T32 that it holds `Commands:` and `命令：`.

Each of these holds when the column stays at 21 and one line follows the line of `menu show`. `HELP` and `HELP_ZH` of `tests/f11_texts.py`, the helps of the F05 prototype without the line that starts with `  shop `, would break if a test compared them with the real help. No test does: F11-T01 compares them only with the help of F11's own seven commands, which it passes to `main` as `commands=SEVEN`, and F13 does not change that list. F07-T01, F08-T14, F09-T01, and F10-T01 also compare a whole help, and each passes `main` its own commands. No test runs `shop` with the real `COMMANDS`, so `recipe-menu shop` changes from `Unknown command "shop".` to the command, and no test changes. So the mock PR, which adds the entry, keeps every test of F01 to F12 passing, and no test-fix PR is needed. F13's own tests compare the whole real help with `HELP_EN_LINES` and `HELP_ZH_LINES` of `tests/f05_texts.py`, the helps of the F05 prototype in full. If the Test Manager still finds a test of the real help that changes, the F13 test plan names it, and F13's tests PR changes it, because the Developer never edits a test (R08).

F13 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, `comma_list`, `display_width`, and `format_table`.
- F03's `DataFolder` with `shopping_file` and `relative`, `Problem`, `Catalog`, `Pantry`, `read_catalog`, and `read_pantry`.
- F04's `Recipe`, `list_recipe_ids`, and `read_recipe`.
- F05's `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, and `stop_at_error` in `app`, `Settings` through `Context.settings`, and `COMMANDS` in `cli`.
- F06's `IsoWeek` with `date_range`, `NOT_A_WEEK`, `WeekMenu`, `list_menu_weeks`, `read_week_menu`, and `week_from_argument`.
- F08's messages `FILE_WRITE_DENIED`, `FILE_WRITE_ERROR`, `FOLDER_CREATE_DENIED`, and `FOLDER_CREATE_ERROR`, which stay internal to `datafile`, and the way `create_data_folder` removes a file that it created (F08 design 3.2). `replace_file` may share that code, and `create_data_folder` keeps its behavior.
- F11's `NO_MENU` in `menus`, and `FileOutcome` and `FileCreation` in `datafile`.
- F12's `ShoppingList`, `ShoppingGroup`, `ShoppingLine` with `amount_text`, and `build_shopping_list` in `shopping`.

### 3.1 `replace_file`

- Module: datafile
- Purpose: Writes one file with its text, and replaces the file that is there, through a temporary file in the same folder that it moves over the old file ([architecture 6](../../architecture.md#6-error-handling)). So the file holds its old text or its new text, never a part, and an `OSError` or an interruption leaves the old file as it was. It creates the file's folder when nothing is at that path (point C). `shop` calls it (2.2), and F14's `menu suggest` can call it.

Signature:

```python
def replace_file(folder: DataFolder, path: Path, text: str) -> FileCreation: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `path` | `Path` | The file to write, such as `folder.shopping_file("2026-W47")`. | Inside `folder.root`, and not `folder.root`. |
| `text` | `str` | The text of the file. | UTF-8 can encode it. |

- Return value: A `FileCreation` (F11 design 3.2). `FileCreation(FileOutcome.CREATED)` when the file at `path` holds the text, whether it replaced a file or not. `FileCreation(FileOutcome.FAILED, problem, left)` when a step failed. `replace_file` never gives `EXISTS`.

`replace_file` works in these steps. `parent` is `path.parent`, and `temp` is `parent / (path.name + ".tmp")`, such as `shopping/2026-W47.md.tmp`.

1. It checks `path` with `folder.relative(path)`, checks that it is not `folder.root`, and encodes `text` as UTF-8, before it touches the disk. A wrong argument raises an error of the Errors table.
2. When `os.path.isdir(parent)` is true, it goes on. Otherwise, when `os.path.lexists(parent)` is true, something other than a folder is there, such as a file or a link that leads to no folder, and the call gives `FAILED` with `PARENT_NOT_A_FOLDER`. Otherwise nothing is there, and it creates `parent` with `Path.mkdir()`, with no parents and with an existing entry as an error. The two probes never raise, and a probe that fails counts as false. A folder that the call created stays when a later step fails.
3. It removes an entry at `temp` with `Path.unlink(missing_ok=True)`. A call that stopped without its cleanup, such as after a power cut, can leave that file. A missing entry is no error.
4. It opens `temp` in exclusive mode, `"x"`, with `encoding="utf-8"` and `newline="\n"` (architecture 8). It writes the text with one `write` call on the file that the open gave, also when the text is empty, and closes the file. So the file holds the UTF-8 bytes of the text, with no byte order mark and with the line ends of the text.
5. It moves `temp` over `path` with `os.replace(temp, path)`, called directly or through `Path.replace`, which calls it. The move replaces a file at `path` in one step, on Windows and on Linux, and creates `path` when nothing is there. Then the call gives `FileCreation(FileOutcome.CREATED)`.

Every problem of the call has the file `folder.relative(path)`, the file to write, not its folder or `temp`, and no place. So a caller can name the file that it could not write by its full path, `str(folder.root / problem.file)`, as architecture 6 lets `shop` do (ADR-0009). An `OSError` gives the problem of the first row of this table that applies. `reason` is the error's `strerror`, or the name of the error's class when `strerror` is `None` or empty, as for `SYSTEM_ERROR` (F03 design 2.3).

| Step | Error | Result |
| --- | --- | --- |
| 2 | `PermissionError` from the creation of `parent` | `FAILED`, with `FOLDER_CREATE_DENIED`. |
| 2 | Any other `OSError` from the creation of `parent`, `FileExistsError` included | `FAILED`, with `FOLDER_CREATE_ERROR` and `reason`. |
| 3 to 5 | `PermissionError` | `FAILED`, with `FILE_WRITE_DENIED`. |
| 3 to 5 | Any other `OSError`, `FileExistsError` included | `FAILED`, with `FILE_WRITE_ERROR` and `reason`. |

`temp` counts as created from the moment that its open succeeds. After an `OSError` from the write, the close, or the move, the call removes `temp` with `Path.unlink` before it gives `FAILED`. A removal that fails with an `OSError` puts the full path of `temp` in `left`. Any other exception after the open, such as `KeyboardInterrupt` for Ctrl+C or the exception of a bug, runs the same removal in a `finally` block and then goes on, so the call gives no result. After the move, nothing is removed. No `except` clause catches more than `OSError` (architecture 6 and 8). The file at `path` changes only through the move. So it keeps its bytes whenever the call gives `FAILED` or raises, and a reader of `path` sees the old text or the new text, never a part.

The open is exclusive, so the removal after a failure removes only a file that the call itself created. Step 3 removes a file that an earlier call left at `temp`, so that file never blocks the open. `temp` is in the folder of `path`, so the move stays in one folder, and a moved file never crosses a drive. Besides the probes `os.path.isdir` and `os.path.lexists`, the call reaches the disk only through `Path.mkdir`, `Path.unlink`, `Path.open` or `open` in mode `"x"`, one `write` on the file object, and `os.replace`. It never uses `os.open`, `os.rename`, `Path.write_text`, `Path.touch`, `tempfile`, or `shutil`. The fault harness of F08's tests in `tests/f08_support.py` replaces `os.mkdir`, `os.rmdir`, `os.unlink`, `os.remove`, `os.scandir`, `os.listdir`, `io.open`, and `builtins.open`, and it applies its rules for an open and a write to a file opened with `"x"`. So it covers every call of `replace_file` except the move. F13's test plan adds a stand-in for `os.replace`, in a new support file or in `tests/f08_support.py`, which `Path.replace` goes through too.

The message of `datafile` is this. `{folder}` is `str(folder.relative(parent))`, such as `shopping`.

| Name | English | Chinese |
| --- | --- | --- |
| `PARENT_NOT_A_FOLDER` | `The file cannot be written: "{folder}" is not a folder.` | `无法写入文件：“{folder}”不是文件夹。` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `path` is not inside `folder.root`, or it is `folder.root`. The check runs before the call touches the disk. |
| `UnicodeEncodeError` | `text` holds a character that UTF-8 cannot encode, such as a lone surrogate. The check runs before the call touches the disk. |

- Side effects: Creates `parent` when nothing is at that path. Removes an entry left at `temp`. Creates `temp`, writes its text, and moves it over `path`, which creates or replaces `path`. After a failure or an interruption, removes `temp`. It reads no file.
- Performance target: None. PT01 times `recipe-menu shop` (2.2), which calls it once.

Example:

In this example, `tmp` is an empty temporary folder. The first call creates `shopping/`. The failure of the move uses a folder at the file's path, which both systems refuse to replace: Windows with `PermissionError`, and Linux with `IsADirectoryError`.

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder, FileCreation, FileOutcome, replace_file
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "recipe-menu")
folder.root.mkdir()
file = folder.shopping_file("2026-W47")
assert replace_file(folder, file, "# 1\n") == FileCreation(FileOutcome.CREATED)
assert file.read_bytes() == b"# 1\n"
assert replace_file(folder, file, "# 2\n番茄 600 g\n").outcome is FileOutcome.CREATED
assert file.read_bytes() == "# 2\n番茄 600 g\n".encode()
assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]

week48 = folder.shopping_file("2026-W48")
week48.mkdir()
blocked = replace_file(folder, week48, "# 3\n")
assert blocked.outcome is FileOutcome.FAILED
assert blocked.problem is not None
assert (blocked.problem.file, blocked.problem.place) == (Path("shopping", "2026-W48.md"), None)
assert blocked.problem.text(Lang.EN).startswith("The file cannot be written")
assert blocked.left == ()
names = sorted(path.name for path in folder.shopping.iterdir())
assert names == ["2026-W47.md", "2026-W48.md"]

other = DataFolder(tmp / "other")
other.root.mkdir()
other.shopping.write_text("", encoding="utf-8")
failed = replace_file(other, other.shopping_file("2026-W47"), "# 1\n")
assert failed.outcome is FileOutcome.FAILED
assert failed.problem is not None
assert failed.problem.text(Lang.EN) == 'The file cannot be written: "shopping" is not a folder.'
assert other.shopping.read_bytes() == b""

replace_file(folder, tmp / "elsewhere.md", "")  # raises ValueError
replace_file(folder, folder.root, "")  # raises ValueError
replace_file(folder, file, "\udc80")  # raises UnicodeEncodeError
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `shop` is the command module that architecture 3 gives F13, in `src/recipe_menu/commands/shop/`. It imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `menus`, and `shopping`, all of them in its row. It needs neither `units` nor `settings`, and it imports no other command module, so it adds no arrow to architecture 4. `SHOP_COMMAND` is a `Command` (architecture 5.2), and its entry in `COMMANDS` is the one change in `cli` that architecture 4 gives a command feature. `replace_file` belongs in `datafile`, whose row owns writing a file, and which is the only module that opens data files (architecture 8). It gives F11's `FileCreation`, so F13 adds no value type. The saved file is the `shopping/<week>.md` of architecture 5.1, in UTF-8 with no byte order mark and with LF line ends. Choice 3 reads only what architecture 8 lists for `shop`. Point 1 of the brief: each of choices 1 to 11 holds on the Architect's model of section 2 and 3.1 in a copy of main's `src/`. The help equals the two helps of the F05 prototype in full, `HELP_EN_LINES` and `HELP_ZH_LINES` of `tests/f05_texts.py`, with 21 lines and the second column after 21 columns. `shop 2026-W99` gives `NOT_A_WEEK` alone with exit code 2, writes nothing, and touches no file. The amounts start 16 and 13 columns after the indent. A catalog name and a category name with a line break keep every heading in its place. The saved file follows the language of the run. A week whose only dish uses only pantry items gives `There is nothing to buy.`, the pantry line, and `Saved`, and saves its file. A PT01 week gives 290 lines in 6 groups and a file of 10,345 bytes. |
| Follows the error handling and naming conventions | Pass | An error in a data file stops `shop` through F05's `first_error` and `stop_at_error`. `NO_MENU` and the failure lines go to stderr with exit code 1, and a wrong week is the only `UsageError`, with no hint (architecture 6, ADR-0008). `replace_file` turns each `OSError` into a `Problem` with F08's messages, catches nothing broader than `OSError`, and removes its temporary file in a `finally` block. Point 2(a): 3.1 is the write that architecture 6 names. `<name>.tmp` is in the folder of the file, so `os.replace` never crosses a drive and replaces the old file in one step on both systems. Removing an old `.tmp` first keeps a file that a power cut left from blocking the exclusive open, and only `shop` writes in `shopping/` (requirements 3). The exclusive open is architecture 6's rule for a new file. The design calls no `fsync`, and architecture 6 asks for none: Ctrl+C leaves the old file or the new file whole, and the next run rewrites a list that a power cut spoiled. On Windows, the model's move onto a file that another handle holds open, and onto a read-only file, raised `PermissionError`. `shop` then wrote the list file's full path, `The file cannot be written: access is denied.`, and `No file was saved.`, kept the old bytes, and left no `.tmp`, as choice 6 and the first risk of the summary say. Point 2(b): option 1 of point C is within requirements 3, whose table gives `shopping/` to `shop` and whose rule limits files, not folders. It is within architecture 1 and 6, which forbid neither. Every problem of `replace_file` names the list file, never its folder (3.1), so the first failure line names a file that `shop` could not write. That is the case of ADR-0009 section 3 that architecture 6 gives `shop`. So, unlike F11's point C, it needs no change to architecture 6 and no ADR, and choice 6 says that it uses the case, as ADR-0009 section 5 asks. The relative `"shopping"` inside `PARENT_NOT_A_FOLDER` belongs to a problem, which names paths relative to the data folder, and the line above it gives the full path. The names follow architecture 8. Note 1, not blocking (3.1, the table of `OSError` results): F08's `_creation_problem` maps `FileExistsError` to `FILE_EXISTS` and `FOLDER_EXISTS`, while the table gives `FILE_WRITE_ERROR` and `FOLDER_CREATE_ERROR`. The Developer must not pass a `FileExistsError` through it unchanged, as `create_file` on main does for one from its write. The test plan can inject one at the creation of the folder and at the open to pin the table. |
| Does not duplicate an existing interface | Pass | `shop` builds the list with F12's `build_shopping_list`, writes each amount with `amount_text`, aligns with `format_table` and `display_width`, joins the pantry names with `comma_list`, and gets its week from `week_from_argument`. It builds none of them again. `replace_file` is the first write that replaces a file: `create_file` refuses an entry that is there, and `create_data_folder` creates a whole folder. It reuses `_remove_all`, F08's four write messages, and `FileCreation`, and adds one message. Point 2(d): the copy of the catalog read and of the stop at the first error is internal code, not an interface, and it calls the shared interfaces `first_error` and `stop_at_error`. So are the copies of `WEEK_ARGUMENT`, `MEAL_COUNT`, and `DISH_COUNT`, which architecture 8 keeps in each module's `messages.py`. Choice 3's reason holds: sharing more changes three implemented modules that F13 does not build, in PRs that are near R03's limits. Note 2, not blocking (choice 3, its last paragraph): `shop` may not import `menu`, and `app` may not import `catalog`, `recipes`, or `menus` (architecture 3). So the helper that a later `[refactor]` PR can add without an architecture change is a stop on a reader's problems in `app`, which gives the exit code or `None`, and each command keeps its own reads. Sharing the read order of `menu show` itself would need an arrow that architecture 3 does not have. The paragraph can say "a helper in `app` that takes a reader's problems" in place of "such as `app`". |
| Depends only on features earlier in the order | Pass | F13 uses F02's `text`, F03's `datafile` and `catalog`, F04's `recipes`, F05's `app` and `COMMANDS`, F06's `menus`, F08's messages and `_remove_all` inside `datafile`, F11's `NO_MENU`, `FileOutcome`, and `FileCreation`, and F12's `shopping`. Each of these features comes before F13 and passes its tests on main, and F05, the hard dependency, is accepted. The plan for F14 binds no later design. F13 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. Every problem of `replace_file` names the file to write, with no place, so `shop` writes `str(context.folder.root / problem.file)` (3.1). `replace_file` gives only `CREATED` and `FAILED`, and its `left` holds at most the temporary file. `shop` passes `build_shopping_list` only values that the readers gave with no error, from one catalog, so F12's `ValueError` never comes (choice 3). `shopping_file` gets a name only after `week_from_argument` gave a week (choice 2). F08's fault harness lacks `os.replace`, and 3.1 says that the test plan adds it. No module reads `shopping/`, so the `.tmp` name meets no reader. In the model, step 5 of v0.1-S15 gives the three lines of `menu show`, because the pantry has no error, and a `2026-W47.md.tmp` that is there before a run is gone after it. |
| Changes an implemented interface only through the change flow | Pass | The PR adds only the two design files. Section 3 adds `replace_file` and the internal `PARENT_NOT_A_FOLDER` to `datafile`, and widens the doc comments of `FileOutcome` and `FileCreation` to name `replace_file`. No exported name of F01 to F12 changes its signature, its fields, its checks, or its behavior, and every result of `replace_file` passes the checks of `FileCreation` as they are. The requirements do not change for these additions, so the Architect reviews them here, as it reviewed F11's `create_file` and `NO_MENU`. With the model's `SHOP_COMMAND` in `COMMANDS` and the new names in `datafile`, the whole suite gives 553 passed and 4 skipped on Windows, the 4 skips being main's Linux-only cases. So F05-T48, F05-T49, F07-T17, F08-T14, F09-T01, F10-T01, F11-T01, and every other test stay true, as section 3 says, and no test-fix PR is needed. Point 2(c): option 1 of point B changes a prototype and a scenario, which are Troy's, so it needs the requirement change flow. The order is right: after Troy decides in this PR, and before PR 2, whose cases compare with the F13 prototype and v0.1-S16. It changes no interface, so the change impact will find none. Point 5 of the brief: the mock's 8 files exceed R03's 5, and its soft-limit reason is right. troy-mode has one mock PR, and the tests reach `replace_file` both directly and through `shop`, as in F08's and F11's mocks. The implementation's 4 files fit R03, and its line count is near 500, as the design warns. Note 3, not blocking (point B, option 1): v0.1-S16 is in `docs/versions/v0.1/test-plan.md`, which the Test Manager writes, not the Product Manager. The Product Manager changes the prototype, and the Test Manager changes v0.1-S16, both before PR 2. Note 4, not blocking (section 2, its last paragraph): a test that checks only that the error stream is empty, or only that no `.tmp` file is left, also passes against the mock. The Test Manager gives each such test a check that the mock gets wrong. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary at the top of PR #85 says what the design says. What changes: the list by category, the pantry line, and `Saved` with the path (choice 4); the checklist in the language of the run, which replaces the week's file and its ticks (choice 5); no other file (requirements 3); `There is nothing to buy.` with a saved file (choice 7); and the reason and the old file after a failed save (choice 6). What Troy decides: points A, B, and C, each with its options, the cost of options 1 and 2 of point B and the result of option 3, and a recommendation with its reason, and no other point. The 11 texts of point A are all the new texts that no prototype shows. Risks: the refused save on Windows, which the model reproduced, and the speed, which the design estimates. On this PC, `shop 2026-W26` on a PT01 folder from `tests/pt01_support.py`, timed from start to exit in two sets of 5 runs, took medians of 0.226 s and 0.228 s, against 0.216 s for `menu show 2026-W26` in the same sets, so "about 0.2 seconds" holds. The Chinese part has about 920 characters and the English part about 1,870, within R22's 2,000, and neither holds an internal ID. The Architect found no other point for Troy. Its recommendations: A, accept the 11 texts, which follow `NO_DISHES`, F08's write messages, and the `LEFT_BEHIND` of `menu new`; B, option 1, because the line then writes each name as the catalog holds it, as the list's own lines do, while option 2 changes the catalog's format and its reader, and option 3 writes a proper name such as Sichuan wrongly; C, option 1, because it stays within requirements 3, architecture 6, and ADR-0009 with no change to any of them, and a copied data folder still gets its list. Note 5, optional (the summary, "What changes" and point 2): the summary can say that a failed save shows no list, such as "you see why, the list is not shown, and the old file stays", as choice 6 has it. It can also say that option 3 changes the prototype's last name, which Troy approves. Both fit within 2,000 characters. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 11 choices and section 3 against the requirements, the architecture, ADR-0008 to ADR-0010, the designs of F02, F05, F11, and F12, the F05 and F13 prototypes, and v0.1-S08, v0.1-S14 to v0.1-S18, v0.1-S23, v0.1-S26, and v0.1-S32. The two files have the same 9 headings and 106 table rows, and 9 code blocks, each equal to its mirror, with no invisible character. `ruff format --check` with ruff 0.17.4 reports both files formatted. With Python 3.13.18 on Windows, the Architect built a model of section 2 and 3.1 in a copy of main's `src/` and ran the 3 examples of each file: all 51 assertions and all 4 `# raises` hold. On fresh copies of `tests/data/example/`, the Chinese run gives the output and the saved file of the F13 prototype byte for byte, the English run differs from its prototype only in the pantry line of point B, and both outputs of "No menu, or an empty menu" match. v0.1-S08, v0.1-S14, v0.1-S15, v0.1-S17, v0.1-S18, and v0.1-S23 hold, and v0.1-S16 holds apart from the pantry line of point B. In v0.1-S14, `shop` and `shop next` give the line for a week with no dish with exit code 0, and `shopping\` stays empty, as the design corrects the brief. In v0.1-S23, only `shopping\2026-W47.md` and the modification time of `shopping\` change. The Linux results of 3.1 were not run. Notes 1 to 5 do not block. | Approved. The Interface Designer can take notes 1 to 5 in a revision, or leave them. Troy approves the design and decides points A to C (R18). |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-15 | First draft. |
| 1.0 | 2026-11-15 | Approved by Troy. |
