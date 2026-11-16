---
troy-doc: "v0.1-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-16"
status: "Accepted by Troy on 2026-11-16"
mirror: "test-plan.zh-CN.md"
---

# v0.1 version test plan

## 1. Version

- Version: v0.1
- Features: F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13
- Requirements: [docs/requirements.md](../../requirements.md#6-version-plan)

## 2. End-to-end scenarios

The scenarios follow the four main flows of [requirements 3](../../requirements.md#3-how-users-interact-with-it) and the prototypes in `docs/prototypes/`. Claude runs a scenario as a version test in `version-tests/`. The release test runs the version tests on Troy's PC, never in CI. Each of Claude's scenarios works this way:

- Each `recipe-menu` step runs as a new process: the `recipe-menu` command of the project's environment, as Troy types it, with the step's arguments. The test finds the command in the scripts folder of the environment whose Python runs the test. The current folder of the process is an empty temporary folder.
- The process gets a temporary home folder, `<home>`, through `USERPROFILE`. It gets no `RECIPE_MENU_DATA` unless the steps set it. So no scenario reads or changes `C:\Users\Troy\recipe-menu`.
- "The example folder" is a fresh copy of `tests/data/example/` at `<home>\recipe-menu`, with an empty `shopping\` folder. `tests/data/example/` holds the data of `docs/prototypes/example-data.md`. "The init folder" is the folder that `recipe-menu init` creates at `<home>\recipe-menu`. The Start of each scenario's steps says which folder it begins with.
- The test reads stdout and stderr as UTF-8, and counts CRLF and LF as the same line end.
- A prototype section, such as F09 "List the recipes", is a section of the prototype file of that feature, here `docs/prototypes/F09-list-show.md`. The output of a command in a section is the lines after its `PS>` line, up to the next `PS>` line, without blank lines at the end. When a step "prints the output" of a section, its output equals those lines, character for character, with `<home>\recipe-menu` in place of `C:\Users\Troy\recipe-menu`. When a section shows several commands, the steps take their outputs in order.
- A message that ends a command with exit code 1 or 2 is on stderr, and any other output is on stdout. The report of `check` is on stdout with every exit code ([architecture 6](../../architecture.md#6-error-handling)).
- `this` and `next` depend on the PC's date on the day of the run. So every step that compares its output with a prototype names an ISO week, such as `2026-W47`.

| ID | Scenario | Run by | Steps | Expected result |
| --- | --- | --- | --- | --- |
| v0.1-S01 | Start a data folder in English, then check it. | Claude | Start: no data folder. 1. Run `recipe-menu init`. 2. Run `recipe-menu check`. | Step 1 prints the first output of F08 "In English" and exits with 0. It creates `<home>\recipe-menu` with `settings.toml`, `catalog.toml`, `pantry.toml`, and `recipes\tomato-egg.toml`, byte for byte as `example-data.md` shows them, in UTF-8 without a byte order mark and with LF line ends. It also creates the empty folders `menus\` and `shopping\`. Step 2 prints the second output of F08 "In English" and exits with 0. |
| v0.1-S02 | Start a data folder in Chinese. | Claude | Start: no data folder. 1. Run `recipe-menu init --lang zh`. 2. Run `recipe-menu check`, without `--lang`. | Step 1 prints the output of F08 "In Chinese" and exits with 0. The files are those of v0.1-S01, except that the `language` line of `settings.toml` says "zh" in place of "en". Step 2 reports in Chinese, starting with "已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。". It reports no errors and no warnings, and exits with 0. |
| v0.1-S03 | `init` refuses a folder that holds files. | Claude | Start: `<home>\recipe-menu` holds only the file `notes.txt`. 1. Run `recipe-menu init`. 2. Run `recipe-menu init --data <other>`, where `<other>` is a temporary folder that does not exist yet. | Step 1 prints `<home>\recipe-menu already holds files. init changed nothing.` and exits with 1. The folder still holds only `notes.txt`, with the same bytes and modification time. Step 2 prints the first output of F08 "In English", with `<other>` in place of the data folder, and exits with 0. `<other>` then holds the files and folders of v0.1-S01. |
| v0.1-S04 | Add a recipe that needs a new ingredient. | Claude | Start: the init folder. 1. Add `recipes\cucumber-salad.toml`, with the names 拍黄瓜 and Smashed cucumber, 2 servings, the tags 快手 and 素, the ingredients 黄瓜 `2 个` and 大蒜 `2 瓣`, and one step in each language. 2. Run `recipe-menu check`. 3. Add `{ zh = "黄瓜", en = "Cucumber", category = "produce" }` at the end of the catalog's ingredients. 4. Run `recipe-menu check`. 5. Run `recipe-menu list`, then `recipe-menu show cucumber-salad`. | Step 2 reports 1 error, at `recipes\cucumber-salad.toml, ingredient 1`, with the message `Unknown ingredient "黄瓜". Add it to the catalog, or use its name in the catalog.`, and exits with 1. Step 4 prints `Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus.` and `No errors. No warnings.`, and exits with 0. In step 5, `list` lists cucumber-salad, then tomato-egg, and ends with `2 recipes.`. `show` gives the ingredients Cucumber 2 pieces and Garlic 2 cloves. Both commands exit with 0. |
| v0.1-S05 | Fix the mistakes that `check` reports. | Claude | Start: the example folder, with the two mistakes of the F07 prototype: ingredient 3 of `mapo-tofu` says 豆瓣酱, and Monday dinner of `2026-W47` says `tomato-eggs`. 1. Run `recipe-menu check`. 2. Run `recipe-menu check --lang zh`. 3. Change 豆瓣酱 back to 郫县豆瓣酱, and `tomato-eggs` back to `tomato-egg`. 4. Run `recipe-menu check`. | Step 1 prints the output of F07 "Errors and a warning, in English" and exits with 1. Step 2 prints the output of F07 "The same check in Chinese" and exits with 1. Step 4 prints the output of F07 "After the fixes" and exits with 0. |
| v0.1-S06 | A syntax mistake names its line. | Claude | Start: the example folder. 1. In line 2 of `pantry.toml`, delete the comma between "盐" and "糖". 2. Run `recipe-menu check`. | Step 2 prints the output of F07 "A syntax mistake" and exits with 1. |
| v0.1-S07 | One `check` run lists every problem. | Claude | Start: the example folder, with 9 mistakes. In `catalog.toml`, two ingredients are added at the end: ingredient 23 is `{ zh = "芥兰", en = "Broccoli", category = "produce" }`, and ingredient 24 is `{ zh = "香菜", en = "Coriander", category = "meats" }`. In `pantry.toml`, item 3 is "sesame oil". In `recipes\rice.toml`, the servings are 0, ingredient 1 has the amount `1 cups`, and the tags are `["breakfast"]`. In `menus\2026-W47.toml`, the week is "2026-W48", Friday has `supper = []`, and Sunday dinner's dish 1 has servings 0. 1. Run `recipe-menu check`. | The report says `9 errors:` and lists the 9 places and messages of F07 "Other problems that check reports", in any order, with two changes. The duplicate name is at `catalog.toml, ingredient 23`, with the message `The English name "Broccoli" is also ingredient 3's name. Names must be unique.`. The unknown category is at `catalog.toml, ingredient 24`. The report also lists the warning of F07 "After the fixes". The command exits with 1. |
| v0.1-S08 | Data files with a byte order mark and CRLF line ends read the same. | Claude | Start: the example folder, with every file saved again in UTF-8 with a byte order mark and with CRLF line ends. 1. Run `recipe-menu check`. 2. Run `recipe-menu show tomato-egg`. 3. Run `recipe-menu menu show 2026-W47`. 4. Run `recipe-menu shop 2026-W47`. | The four steps print the output of F07 "After the fixes", the output of F09 "Show one recipe", the first output of F11 "Show the week after you fill it", and the output of F13 "In English". Each step exits with 0. `shopping\2026-W47.md` is in UTF-8 without a byte order mark, with LF line ends. |
| v0.1-S09 | List the recipes in both languages. | Claude | Start: the example folder. 1. Run `recipe-menu list`. 2. Run `recipe-menu list --lang zh`. | Steps 1 and 2 print the two outputs of F09 "List the recipes" and exit with 0. |
| v0.1-S10 | List the recipes with one tag, named in either language. | Claude | Start: the example folder. 1. Run `recipe-menu list --tag 快手`. 2. Run `recipe-menu list --tag quick --lang zh`. 3. Run `recipe-menu list --tag breakfast`. | The three steps print the three outputs of F09 "List the recipes with one tag". Steps 1 and 2 exit with 0, and step 3 exits with 1. |
| v0.1-S11 | Search recipes in either language. | Claude | Start: the example folder. 1. Run `recipe-menu search 番茄`. 2. Run `recipe-menu search TOMATO`. 3. Run `recipe-menu search 葱 quick --lang zh`. 4. Run `recipe-menu search lamb`. 5. Run `recipe-menu search 豆腐 quick --lang zh`. | The five steps print, in order, the two outputs of F10 "One word", the output of F10 "Two words, in Chinese", and the two outputs of F10 "No match". Every step exits with 0. |
| v0.1-S12 | Show a recipe, scaled and with a missing language. | Claude | Start: the example folder. 1. Run `recipe-menu show tomato-egg`. 2. Run `recipe-menu show tomato-egg --servings 4 --lang zh`. 3. Run `recipe-menu show red-braised-pork`. 4. Run `recipe-menu show mapo`. | The four steps print the outputs of the F09 sections "Show one recipe", "Show one recipe for 4 servings, in Chinese", "A missing language", and "An unknown ID". Steps 1 to 3 exit with 0, and step 4 exits with 1. |
| v0.1-S13 | Plan a week and show it. | Claude | Start: the example folder, with an empty `menus\`. 1. Run `recipe-menu menu new 2026-W47`. 2. Run `recipe-menu menu new 2026-W47 --lang zh`. 3. Replace the new file with the `menus\2026-W47.toml` of `example-data.md`, as Troy fills it in. 4. Run `recipe-menu check`. 5. Run `recipe-menu menu show 2026-W47`. 6. Run `recipe-menu menu show 2026-W47 --lang zh`. | Step 1 prints the first output of F11 "Create next week's menu" and exits with 0. It creates `menus\2026-W47.toml` byte for byte as that section shows the file, in UTF-8 without a byte order mark and with LF line ends. Step 2 prints the second output of that section and exits with 1, and the file keeps its bytes and modification time. Step 4 prints the output of F07 "After the fixes" and exits with 0. Steps 5 and 6 print the two outputs of F11 "Show the week after you fill it" and exit with 0. |
| v0.1-S14 | `this` and `next` follow the PC's date. | Claude | Start: the example folder, with an empty `menus\`. `<T>` is the ISO week of the PC's date, and `<N>` is the ISO week of the date 7 days later. 1. Run `recipe-menu menu new`. 2. Run `recipe-menu menu new next`. 3. Run `recipe-menu menu show this`. 4. Run `recipe-menu shop`. 5. Run `recipe-menu shop next`. | Step 1 creates `menus\<T>.toml`, and step 2 creates `menus\<N>.toml`. The `week` line of each file names its week. Step 3 starts with `Menu for <T>,` and shows `—` for every meal. Step 4 prints `The menu for <T> has no dishes, so there is nothing to buy. No file was saved.`, and step 5 prints the same message with `<N>`. Every step exits with 0, and `shopping\` stays empty. |
| v0.1-S15 | A missing menu, a wrong week, and a menu with a mistake. | Claude | Start: the example folder. 1. Run `recipe-menu menu show 2026-W48`. 2. Run `recipe-menu menu show 2026-W99`. 3. Run `recipe-menu shop 2026-W48`. 4. In `menus\2026-W47.toml`, change Monday dinner's `tomato-egg` to `tomato-eggs`, then run `recipe-menu menu show 2026-W47`. 5. Run `recipe-menu shop 2026-W47`. | Steps 1 and 2 print the two outputs of F11 "A week without a menu", and exit with 1 and 2. Step 3 prints the first output of F13 "No menu, or an empty menu" and exits with 1. Step 4 prints the output of F11 "A menu with a mistake" and exits with 1. Step 5 prints the same lines as step 4 and exits with 1. `shopping\` stays empty. |
| v0.1-S16 | The settings name the meals and the default servings. | Claude | Start: the init folder, with `meals = ["breakfast", "lunch", "dinner"]` and `servings = 3` in `settings.toml`. 1. Run `recipe-menu menu new 2026-W48`. 2. In the new file, put `"tomato-egg"` in Monday breakfast. 3. Run `recipe-menu menu show 2026-W48`. 4. Run `recipe-menu shop 2026-W48`. | The second line of step 1 is `7 days with breakfast, lunch, and dinner, all empty.`, and the file has breakfast, lunch, and dinner, in that order, for each day. Step 3 has the columns Day, Breakfast, Lunch, and Dinner. It shows `Tomato and egg stir-fry ×3` at breakfast on Mon 23 Nov, and ends with `1 meal, 1 dish. ×n: servings.`. Step 4 starts with `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish`. It lists Tomato 450 g and Scallion 2 stalks under Vegetables and fruit, then Egg 5 pieces under Eggs, dairy, and tofu. Its pantry line is `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`. Every step exits with 0. |
| v0.1-S17 | Make the week's shopping list in English and in Chinese. | Claude | Start: the example folder. 1. Run `recipe-menu shop 2026-W47`. 2. Run `recipe-menu shop 2026-W47 --lang zh`. | Step 1 prints the output of F13 "In English" and exits with 0. It saves `shopping\2026-W47.md` with the same list in English, as a Markdown checklist with one `- [ ]` line for each item. Step 2 prints the output of F13 "In Chinese" and exits with 0. It replaces the file with the text of F13 "The saved file", byte for byte, in UTF-8 without a byte order mark and with LF line ends. `shopping\` then holds only that file. |
| v0.1-S18 | Quantities that cannot be added share one line. | Claude | Start: the example folder, with three changes. 生抽 is removed from `pantry.toml`. `recipes\scallion-noodles.toml` is added: 葱油拌面, Scallion oil noodles, 2 servings, the tags 快手 and 主食, the ingredients 面条 `200 g`, 葱 `1 把`, and 生抽 `10 g`, and one step in each language. `menus\2026-W48.toml` has these dinners from Monday to Friday: red-braised-pork, tomato-egg, tomato-egg, tomato-egg-noodles, and scallion-noodles, and every other meal is empty. 1. Run `recipe-menu shop 2026-W48`. 2. Run `recipe-menu shop 2026-W48 --lang zh`. | Step 1 has a Scallion line with the amounts `5 stalks + 1 bunch` and a Soy sauce line with `30 ml + 10 g`, as in F13 "Quantities that cannot be added". Step 2 has a 葱 line with `5 根 + 1 把` and a 生抽 line with `30 ml + 10 g`. Both steps exit with 0. |
| v0.1-S19 | Help, version, and mistakes on the command line. | Claude | Start: no data folder for steps 1 to 3, and the example folder for steps 4 and 5. 1. Run `recipe-menu --help`. 2. Run `recipe-menu --help --lang zh`. 3. Run `recipe-menu --version`. 4. Run `recipe-menu list --lang fr`. 5. Run `recipe-menu cook`. | Step 1 prints the first output of F05 "Help in English", step 2 prints the output of F05 "Help in Chinese", and step 3 prints `recipe-menu 0.1.0`. Steps 1 to 3 exit with 0. Steps 4 and 5 print the two outputs of F05 "Mistakes on the command line" and exit with 2. |
| v0.1-S20 | Choose the data folder. | Claude | Start: no data folder. `<B>` is a copy of the example folder at a path that holds a space and Chinese characters, such as `<temp>\One Drive\菜谱`. `<C>` is a folder that `recipe-menu init --data <C>` created. 1. Run `recipe-menu list --data <B>`. 2. With `RECIPE_MENU_DATA` set to `<C>`, run `recipe-menu list`. 3. With `RECIPE_MENU_DATA` set to `<C>`, run `recipe-menu list --data <B>`. 4. Run `recipe-menu list`. 5. Run `recipe-menu list --lang zh`. | Steps 1 and 3 print the first output of F09 "List the recipes". Step 2 lists only tomato-egg and ends with `1 recipe.`. Steps 1 to 3 exit with 0. Steps 4 and 5 print the two outputs of F05 "No data folder yet" and exit with 1. |
| v0.1-S21 | The language comes from the settings. | Claude | Start: the example folder, with `language = "zh"` in `settings.toml`. 1. Run `recipe-menu list --tag 素`. 2. Run `recipe-menu list --tag 素 --lang en`. 3. Delete the `language` line from `settings.toml`, then run `recipe-menu list --tag 素`. | Steps 1 and 2 print the two outputs of F05 "The language from the settings". Step 3 prints the same output as step 2. Every step exits with 0. |
| v0.1-S22 | A broken settings file stops a command. | Claude | Start: the example folder, with `meals = ["lunch", "supper"]` in `settings.toml`. 1. Run `recipe-menu list`. | The message starts with the two lines of F05 "A broken settings file", and the command exits with 1. |
| v0.1-S23 | Your files stay as you wrote them. | Claude | Start: the example folder. The test records the bytes and the modification time of every file and folder under `<home>` and under the current folder. 1. Run each of these commands: `recipe-menu check`, `recipe-menu list`, `recipe-menu list --tag 快手`, `recipe-menu search 番茄`, `recipe-menu show tomato-egg --servings 4`, `recipe-menu menu show 2026-W47`, `recipe-menu show mapo`, `recipe-menu menu show 2026-W48`, and `recipe-menu --help`. 2. Run `recipe-menu shop 2026-W47` twice. | After step 1, every file and folder keeps its bytes and modification time, and no file or folder is added. After step 2, the only new or changed file is `shopping\2026-W47.md`, and `shopping\` holds no other file. |
| v0.1-S24 | Install the release and run it from any folder, in both shells. | Troy | On your PC: 1. In a PowerShell where uv is available, such as the activated `recipe-menu` environment, run `uv tool install --managed-python --python 3.13 --force "git+ssh://git@github.com/ZJUCao/recipe-menu.git@<commit>"`, with the commit that the release test names. Then run `uv tool update-shell`. 2. Open a new Windows PowerShell 5.1 tab in Windows Terminal. Run `cd $HOME`, then `recipe-menu --version`. 3. Do step 2 again in a new PowerShell 7 tab. | Both tabs print `recipe-menu 0.1.0`. |
| v0.1-S25 | Chinese shows correctly in Windows Terminal. | Troy | On your PC, in the two tabs of v0.1-S24: 1. In the first tab, run `Copy-Item -Recurse D:\Troy\Projects\recipe-menu\tests\data\example $env:TEMP\recipe-menu-v0.1`, then `New-Item -ItemType Directory -Force $env:TEMP\recipe-menu-v0.1\shopping`. 2. In each tab, run `$env:RECIPE_MENU_DATA = "$env:TEMP\recipe-menu-v0.1"`. Then run `recipe-menu list --lang zh`, `recipe-menu show tomato-egg --servings 4 --lang zh`, `recipe-menu menu show 2026-W47 --lang zh`, `recipe-menu shop 2026-W47 --lang zh`, and `recipe-menu --help --lang zh`. 3. In each tab, run `chcp 437`, then `recipe-menu list --lang zh` again. | Every Chinese character shows as itself, with no question marks, boxes, or garbled text. The columns of each table line up as in the F05, F09, F11, and F13 prototypes. After `chcp 437`, `list` shows the same as before. You change no Windows setting. |
| v0.1-S26 | Tick off the shopping list on your phone. | Troy | 1. On your PC, copy the example folder as in step 1 of v0.1-S25, but to a folder that your sync carries to your phone, such as `D:\OneDrive\recipe-menu-v0.1`. 2. Run `recipe-menu shop 2026-W47 --lang zh --data D:\OneDrive\recipe-menu-v0.1`. 3. On your phone, open `shopping/2026-W47.md` in that folder with the app you use for Markdown files. 4. Tick two items. | The phone shows the list of F13 "The saved file": the title, the six categories, 14 items, and the pantry line, with every Chinese character correct. Each item is a checkbox, and the two items you ticked show as ticked. |

**Why Troy runs three scenarios.** Claude runs every scenario that a script can run through the `recipe-menu` command. v0.1-S24 installs the tool into Troy's own uv tool folder and changes Troy's PATH, which a test must not do. Only a new PowerShell tab shows that the PATH works ([ADR-0006](../../adr/ADR-0006-install-with-uv-tool.md)). v0.1-S25 needs Troy's eyes. A test reads the output through a pipe, so it sees neither the font nor the columns in Windows Terminal ([architecture 10](../../architecture.md#10-test-setup)). v0.1-S26 needs Troy's phone and Troy's sync.

**What the plan leaves out.**

- Linux. CI runs the per-PR tests on Linux ([requirements 7](../../requirements.md#7-non-functional-requirements)). Claude's scenarios run only in the release test on Troy's PC, so none of them runs on Linux.
- The network. The tool never uses the network ([requirements 7](../../requirements.md#7-non-functional-requirements)). The architecture bans network modules from the code ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). A version test cannot show that a process never used the network, so no scenario checks it.
- `menu suggest`, `add`, and `edit`. They belong to v0.2, in F14, F15, and F16.

**Which scenarios cover each flow.**

| Flow or rule in the requirements | Scenarios |
| --- | --- |
| Flow 1: start | v0.1-S01 to v0.1-S08 |
| Flow 2: find a recipe | v0.1-S09 to v0.1-S12 |
| Flow 3: plan the week | v0.1-S13 to v0.1-S16 |
| Flow 4: shop | v0.1-S16 to v0.1-S18, and v0.1-S26 |
| The shopping list's rules | v0.1-S16 to v0.1-S18 |
| The language | v0.1-S02, v0.1-S21, v0.1-S25, and every step with `--lang` |
| The data folder | v0.1-S01, v0.1-S20, and v0.1-S26 |
| Errors and exit codes | v0.1-S05 to v0.1-S07, v0.1-S15, v0.1-S19, v0.1-S20, and v0.1-S22 |
| Your files stay as you wrote them | v0.1-S03, v0.1-S13, v0.1-S17, and v0.1-S23 |
| Installation and Chinese text, in requirements 7 | v0.1-S08, v0.1-S24, and v0.1-S25 |
| Size, in requirements 7, and PT01 | v0.1-S27 to v0.1-S32 |

## 3. Performance and stress cases

PT01 is the only performance target ([requirements 7.1](../../requirements.md#71-performance-targets)). Each command that it names gets one case, and no other command gets one (R14).

| ID | Target | Load | Duration | Machine | Run by |
| --- | --- | --- | --- | --- | --- |
| v0.1-S27 | PT01: `recipe-menu check` finishes within 1 second. | The PT01 data folder. `check` reads every file in it. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |
| v0.1-S28 | PT01: `recipe-menu list` finishes within 1 second. | The PT01 data folder. `list` prints all 1,000 recipes. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |
| v0.1-S29 | PT01: `recipe-menu show` finishes within 1 second. | The PT01 data folder. `show` prints one recipe with its 12 ingredients. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |
| v0.1-S30 | PT01: `recipe-menu search` finishes within 1 second. | The PT01 data folder. `search` looks for the name of the ingredient that every recipe uses, so it prints all 1,000 recipes. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |
| v0.1-S31 | PT01: `recipe-menu menu show` finishes within 1 second. | The PT01 data folder. `menu show` prints one week of 63 dishes. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |
| v0.1-S32 | PT01: `recipe-menu shop` finishes within 1 second. | The PT01 data folder. `shop` builds and saves the list of one week of 63 dishes, from 63 different recipes. | 5 runs, each from start to exit. The median counts. | Troy's PC, Windows 11, in the release test | Claude |

**The PT01 data folder.** The test generates it in a temporary folder before it times anything:

- `settings.toml`: English, breakfast, lunch, and dinner, and 2 servings.
- `catalog.toml`: the six categories and the five tags of the example, and 300 ingredients spread over the categories, each with a Chinese and an English name.
- `pantry.toml`: 10 of those ingredients.
- `recipes\`: 1,000 recipes. Each recipe has its names and 6 steps in both languages, 2 tags, and 12 ingredients with notes in both languages. The quantities use mass, volume, and count units, and "to taste". Every recipe uses one shared ingredient, whose name `search` looks for.
- `menus\`: 52 week menus, `2026-W01` to `2026-W52`. Each meal holds 3 dishes, so a week has 63 dishes, from 63 different recipes. `menu show` and `shop` use one of these weeks.

**When a case passes.**

- Each run is a new process, `python -m recipe_menu` with the case's arguments and `--data` naming the PT01 data folder. The test times it from start to exit. It does not time the generation of the folder.
- A run counts only when it exits with 0 and prints what the work gives. `check` reports no errors and no warnings for 1,000 recipes and 52 week menus. `list` and `search` print 1,000 recipes. `show` prints 12 ingredients. `menu show` prints 63 dishes. `shop` prints the list and saves its file. So the timed work did happen, and the tool handles the size that requirements 7 asks for.
- A case passes when the median of its 5 runs is under 1 second. The target gets no margin above 1 second, because such a margin would pass a command that misses PT01. v0.1 is the first version, so no earlier baseline exists to compare with.
- The test records the median and the range of each case's 5 runs in the JUnit report of the release test, so that a later version can compare with them.

## 4. Devices

| Device | Operating system | Run by |
| --- | --- | --- |
| Troy's PC | Windows 11, with Windows PowerShell 5.1 and PowerShell 7 in Windows Terminal | Troy |
| Troy's PC | Windows 11, with Python 3.13 in the `recipe-menu` environment, in the release test | Claude |
| Troy's phone | Not named in the requirements. Troy names it when reporting v0.1-S26. | Troy |

## 5. Acceptance record

| Date | Result | Troy's notes |
| --- | --- | --- |
| 2026-11-16 | Accepted as v0.1.0 | Troy ran v0.1-S24, v0.1-S25, and v0.1-S26 on Troy's devices and replied: "All accepted". No bug was deferred. |

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-10 | First draft. |
| 0.2 | 2026-11-15 | v0.1-S16 expects the English pantry line with the catalog's names as written, `Cooking oil, Salt, Sugar`, because Troy chose that line in the F13 design. |
| 0.3 | 2026-11-16 | v0.1-S06 starts from the example folder and expects the output of F07 "A syntax mistake" unchanged, because that section now also shows the warning that the example folder gives. The steps of v0.1-S01 to v0.1-S23 run the `recipe-menu` command of the project's environment in place of `python -m recipe_menu`. |
| 1.0 | 2026-11-16 | Accepted by Troy as v0.1.0. |
