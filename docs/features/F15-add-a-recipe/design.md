---
troy-doc: "F15-design"
lang: "en"
version: "1.0"
updated: "2026-11-20"
status: "Approved by Troy on 2026-11-20"
mirror: "design.zh-CN.md"
---

# F15 Add a recipe: interface design

## 1. Feature

- ID and name: F15 Add a recipe
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F03, F04, F07

## 2. Interfaces

F15 builds the command module `add` in `src/recipe_menu/commands/add/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.add` exports one name, `ADD_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu add` (2.2). Its messages live in `src/recipe_menu/commands/add/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F15 adds `ADD_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `SEARCH_COMMAND` (choice 1, point C). That entry is the only change that a command feature makes to the list of commands (architecture 4, F05 design 2.9). F15 also adds to four implemented modules what it needs (section 3): the input stream to `Context` in `app` (3.1) and to `main` in `cli` (3.2), as architecture 5.2 plans; `use_utf8_input` to `text`, which owns the console streams (3.3); and `check_recipe` and `problem_block` to `check`, which architecture 3 says `add` reuses to check one recipe (3.4 and 3.5). The F15 prototype `docs/prototypes/F15-add.md` shows the command. The plans of F03 and F04 for F15 hold: `add` checks each ingredient with `find_ingredient` (F03 design, section 2), and checks the ID with `is_recipe_id` and the listing of `list_recipe_ids` (F04 design, section 2).

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F15 gives |
| --- | --- |
| `recipe-menu add` asks for the ID, the names, the servings, the tags, the ingredients, and the steps, one line at a time ([requirements 4](../../requirements.md#4-features)). | `recipe-menu add` (2.2), with `ADD_COMMAND` (2.1). It asks the eight questions of choice 3, in the same order in both languages, and reads each answer as one line of `Context.input` (3.1, choice 4). |
| It checks each answer against the catalog. | The tags with `Catalog.find_tag` (choice 8), and each ingredient line with `Catalog.find_ingredient` and `parse_quantity` (choice 9). The ID with `is_recipe_id` and the listing of `recipes/` (choice 5), and the servings against the range 1 to 100 (choice 7). |
| It asks again after a wrong answer. | Each wrong answer gets one message that says what is wrong. Then `add` asks the same question again, or for a wrong ingredient line the next line of the list (choice 3). |
| It writes a new recipe file. | `create_file` writes `recipes/<id>.toml` in the layout of the example data, and never overwrites an entry (choices 10 and 11). |
| A name or the steps may lack one language. Commands then show the other language, and `check` warns about the gap ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | Point B: either language of the name and of the steps may stay empty when the other language has text (choice 6). The check after saving shows the warning (choice 12). |
| `add` and `edit` reuse `check` to check one recipe ([architecture 3](../../architecture.md#3-modules)). | `check_recipe` and `problem_block` (3.4 and 3.5), and the lines after saving (choice 12). |

These rules hold for every interface below:

- `add` imports only `app`, `lang`, `units`, `text`, `datafile`, `catalog`, `recipes`, and `check` from the package. Its row of architecture 3 allows them. It needs neither `settings`, `menus`, nor `shopping`: it reads the default servings as `context.settings.servings` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `add` reaches the disk only through `read_catalog`, `list_recipe_ids`, `create_file`, and `check_recipe`, all of which work through `datafile` (architecture 8). It writes only the new file `recipes/<id>.toml` ([architecture 5.1](../../architecture.md#51-data-files)). It reads the answers only from `context.input`, and writes only to `context.out` and `context.err`. It reads nothing of the outside world itself: `cli` passes the input stream in the context (3.1 and 3.2). It keeps no state.
- A reader never raises for bad data, and `create_file` turns each `OSError` into a value ([architecture 6](../../architecture.md#6-error-handling)). `add` stops at the first error in a data file with `first_error` and `stop_at_error` (F05 design 2.8). A wrong answer is not an error in the data: it gets a message and the question again. `run` raises no `UsageError`, because `add` takes no argument value. `KeyboardInterrupt` from Ctrl+C goes on to `cli`, which gives 130 (choice 4). Any other exception that reaches `cli` is a bug.
- `ADD_COMMAND` is a frozen `Command` value (F05 design 2.5). F15 adds no value type. `Context.input` is a `TextIO` (3.1).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F15 interface has a performance target. PT01 does not time `add` ([requirements 7.1](../../requirements.md#71-performance-targets)). Choice 14 says what F15 adds to the start of every other command. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 and section 3 give their rules.

1. **One command, after `search` in the help** (point C). F15 adds `ADD_COMMAND` to `COMMANDS` after `SEARCH_COMMAND`. So `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, ADD_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`. The commands that work on recipes stay together, and F16 can put `edit ID` right after `add`. `add` has `FolderUse.READ`, so `cli` stops it when the data folder is missing or the settings have an error (F05 design 2.5), as v0.2-S14 expects. It declares no argument and no option, so its usage is `add` in both languages. `add` is 3 columns wide, so `menu suggest [WEEK]` stays the widest first cell, and the second column of both tables still starts after 24 columns in both languages. The line of `add` moves the lines below it down by one, and no other line of the help changes. The help has 23 lines (2.1). Section 3 names the test that this place breaks.
2. **What `add` reads before it asks, and where it stops.** Before the first question, `add` reads the catalog with `read_catalog` and lists `recipes/` with `list_recipe_ids`, in this order (2.2, steps 1 and 2). It needs the catalog for the tags and the ingredients, and the listing for the ID. The first error of either stops `add` with `first_error` and `stop_at_error`, before you type anything, as `list` and `menu suggest` stop at them (F05 design 2.8). So an entry such as `recipes\Rice Bowl.toml`, whose name is not a recipe ID, stops `add` too. With no error in the listing, every entry of `recipes/` whose name ends with `.toml` is a recipe ID that the listing gives. So the listing holds every name that `create_file` would refuse (choice 11). A warning changes nothing. `add` reads no recipe file, no menu, and not the pantry. After it saves the file, `check_recipe` reads the catalog again and the new file (choice 12).
3. **The eight questions.** `add` asks them in this order in both languages, as v0.2-S09 and v0.2-S10 give the answers. The prompts are the messages of 2.2, and "empty" means an answer that is empty without whitespace at both ends (choice 4).

   | Question | Prompt | An answer | An empty answer | After a wrong answer |
   | --- | --- | --- | --- | --- |
   | 1. The ID | `ID_PROMPT` | A recipe ID that `recipes/` does not hold (choice 5). | Ends `add` with exit code 0, and writes no file. | `NOT_AN_ID` or `ID_EXISTS`, then question 1 again. |
   | 2. The Chinese name | `ZH_NAME_PROMPT` | Any text. | No Chinese name (choice 6). | None. Every answer is right. |
   | 3. The English name | `EN_NAME_PROMPT` | Any text. | No English name, when question 2 got a name. | `NAME_NEEDED` when questions 2 and 3 both got an empty answer, then question 3 again. |
   | 4. The servings | `SERVINGS_PROMPT` | A whole number from 1 to 100 (choice 7). | The servings of the settings, which the prompt shows. | `SERVINGS_WRONG`, then question 4 again. |
   | 5. The tags | `TAGS_PROMPT` | Names of the catalog's tags, separated by commas (choice 8). | No tags. | `UNKNOWN_TAG` or `NO_TAGS`, then question 5 again. |
   | 6. The ingredients | `INGREDIENTS_PROMPT`, then two spaces before each line | One ingredient line, a name and a quantity, such as `西兰花 300 g` (choice 9). | Ends the list. | `NAME_AND_QUANTITY`, `UNKNOWN_INGREDIENT`, or the message of the amount, after two spaces. Then the next line of the list. |
   | 7. The Chinese steps | `ZH_STEPS_PROMPT`, then two spaces before each line | One step. | Ends the list. | None. Every answer is right. |
   | 8. The English steps | `EN_STEPS_OPTIONAL_PROMPT` when question 7 got a step, else `EN_STEPS_PROMPT`, then two spaces before each line | One step. | Ends the list. | `STEPS_NEEDED` when both lists of steps are empty, then question 8 again. |

   Each wrong answer gets exactly one message. A message after an answer to questions 1 to 5 and 8 is a line of its own with no indent. A message after an ingredient line starts with two spaces, as the prototype shows. `add` asks for no notes, as the prototype says. You add a note in the file.
4. **How `add` reads an answer.**
   - `add` writes the prompt to `context.out`, calls `context.out.flush()`, and reads one line with `context.input.readline()`. Python buffers a console stream by line, so without the flush a prompt with no line break would not show before the answer. The prompts of questions 1 to 5 end with no line break, so you type the answer on the line of the prompt. The prompt of a list ends with a line break, and each line of a list has the prompt of two spaces.
   - The answer is the line without its line break and without whitespace at both ends, as `str.strip()` removes it, so an ideographic space U+3000 at an end does not count.
   - When `context.input.isatty()` is false, `add` writes the line that it read, without its line break, and then a line break to `context.out`, right after the prompt. So the output through a pipe and in a test reads like the session in the console: every prompt with its answer on one line, as the prototype shows. In a console, the console shows what you type, and `add` writes nothing more. `isatty()` is a call on the stream that `cli` passed in the context, as `readline()` is, so `add` reads no console itself (architecture 8).
   - `readline()` gives the empty text at the end of the input: a pipe that ended, or Ctrl+Z and Enter in a Windows console. At question 1, the end of the input counts as an empty answer, so `add` ends with exit code 0 and writes no file. At any later question, `add` writes `INPUT_ENDED` to the error stream, writes no file, and gives 1, so a pipe that ends early says so, and a script sees the exit code. When `context.input.isatty()` is false, `add` first writes a line break after the prompt.
   - Ctrl+C at a question makes `readline()` raise `KeyboardInterrupt`, which `add` does not catch. `cli` gives 130 and writes nothing more (architecture 6, F05 design 2.10). `add` writes the file only after the last answer, so no file is left. On Windows, Python's console reader turns Ctrl+C at a prompt into `KeyboardInterrupt`, not into the end of the input. v0.2-S18 step 5 checks it in Windows Terminal.
   - A test passes the answers as a stream: `main(..., stdin=io.StringIO("garlic-broccoli\n蒜蓉西兰花\n..."))` (3.2), or `Context(..., input=io.StringIO(...))` (3.1). A version test writes the answers as UTF-8 bytes to the standard input of `recipe-menu add` and closes it.
   - The installed command reads `sys.stdin`. At start, `cli` calls `use_utf8_input(sys.stdin)` (3.3), which makes the stream decode UTF-8, with or without a byte order mark, and turn a byte that is not UTF-8 into U+FFFD. So `add` reads a pipe as UTF-8, as redirected output is UTF-8 (ADR-0004), whatever the code page and `PYTHONIOENCODING` are. In a Windows console, Python reads the console through its Unicode interface, so an answer that you type with a Chinese input method arrives as you typed it, also after `chcp 437`, as v0.2-S18 checks. The console edits the line, so Backspace works, and `add` gets the line after you press Enter.
   - Windows PowerShell 5.1 sends a pipe to a program in `$OutputEncoding`, which is ASCII unless you change it, so Chinese answers piped from Windows PowerShell 5.1 arrive as `?`. You type the answers in the console, so no flow of the requirements needs such a pipe.
5. **The ID.** An empty answer ends `add`, as the prototype says. When `is_recipe_id(answer)` is false (F04 design 2.4), `add` writes `NOT_AN_ID`. When the listing of step 2 holds the answer, it writes `ID_EXISTS`, the line of the prototype "An ID that exists". After either message, it asks question 1 again. `create_file` checks the name again when it writes (choice 11).
6. **The names and the steps** (point B). Either language of the name, and either list of steps, may stay empty when the other language has text, as requirements 3 allows.
   - An empty Chinese name is no Chinese name. An empty English name is no English name when the Chinese name has text. When both names are empty, `add` writes `NAME_NEEDED` and asks question 3 again.
   - An empty list of Chinese steps is no Chinese steps. The prompt of the English steps is `EN_STEPS_OPTIONAL_PROMPT`, which says "optional", when there is a Chinese step, and `EN_STEPS_PROMPT` otherwise. When both lists are empty, `add` writes `STEPS_NEEDED` and asks question 8 again, with `EN_STEPS_PROMPT`.
   - The file leaves out a language that is empty, such as `name = { zh = "葱花蛋" }`, or a `[steps]` table with `zh` alone (choice 10). `read_recipe` then gives `NO_EN_NAME` or `NO_EN_STEPS`, or the Chinese ones, each a warning (F04 design 2.6), and the lines after saving show it (choice 12).
7. **The servings.** A right answer is one or more of the ASCII digits 0 to 9 and nothing else, with a value from `MIN_SERVINGS` to `MAX_SERVINGS`, 1 to 100 (F05 design 3.1). So `3` and `03` give 3. `0`, `101`, `two`, `2.5`, `-1`, `+3`, `3 份`, and `３` with a fullwidth digit each give `SERVINGS_WRONG`, which has the text of `SERVINGS_NOT_A_NUMBER` of `datafile`. An answer of thousands of digits gives the message too, and never meets Python's limit on turning a text into an `int`. An empty answer gives `context.settings.servings`, which the prompt shows in brackets, such as `[2]` for the example data. The settings give those servings to a dish that names none (requirements 3), so a recipe with the default needs no scaling for such a dish.
8. **The tags.** `add` splits the answer at `,`, at `，` (U+FF0C FULLWIDTH COMMA), and at `、` (U+3001 IDEOGRAPHIC COMMA), so `快手, 素`, `快手，素`, and `快手、素` give the same tags. Each part counts without whitespace at both ends, and an empty part, such as the one after a comma at the end, is skipped. `Catalog.find_tag` finds each part, so a part matches a tag's name in either language, as `list --tag` matches it (F03 design 2.6). The first part that names no tag makes the whole answer wrong: `add` writes `UNKNOWN_TAG`, picked by the number of the catalog's tags, or `NO_TAGS` for a catalog with no tags, and asks question 5 again. A tag that two parts name, such as `快手, quick`, counts once, as `read_recipe` holds it once (F04 design 2.6).
9. **An ingredient line.** The words of a line are the pieces between whitespace characters, as `str.split()` gives them, so an ideographic space U+3000 separates words too.
   - The quantity: when the last word is `适量`, or the last two words are `to` and `taste` in any case of the letters A to Z, the quantity is that word or those two words. Otherwise the quantity starts at the last word whose first character is an ASCII digit from 0 to 9, and runs to the end of the line.
   - The name is the text before the quantity, without whitespace at both ends.
   - A line with no quantity, or with an empty name, gives `NAME_AND_QUANTITY`. So a space must come between the name and the quantity, as the prompt `“名称 数量”` asks: `盐适量` and `西兰花300g` give the message, and `西兰花 300g` works.
   - A name may hold digits, such as `食材300` of the PT01 data folder (v0.2-S16), so the first digit of the line does not start the quantity. A quantity of F01 is a number with an optional unit, or "to taste", so it is at most two words when a space comes before its unit.

   | Line | Name | Quantity |
   | --- | --- | --- |
   | `西兰花 300 g` | `西兰花` | `300 g` |
   | `Cooking oil 2 tbsp` | `Cooking oil` | `2 tbsp` |
   | `Salt to taste` | `Salt` | `to taste` |
   | `盐 适量` | `盐` | `适量` |
   | `食材300 100 g` | `食材300` | `100 g` |
   | `Egg 3` | `Egg` | `3` |
   | `7-Up 1 can` | `7-Up` | `1 can` |
   | `Peanut`, `300 g`, or `盐适量` | None | None. The line gives `NAME_AND_QUANTITY`. |

   - Then `catalog.find_ingredient(name)` finds the ingredient, by the rules of F03 design 2.6: a name in either language, whitespace at both ends does not count, case counts only for the letters A to Z, and whitespace inside the name counts as written. When it finds none, the line gives `UNKNOWN_INGREDIENT`, the line of the prototype after `橄榄油 1 tbsp`.
   - Then `parse_quantity(quantity, ingredient.unit)` reads the quantity, as `read_recipe` reads `amount` (F04 design 2.6), so `Egg 3` gives 3 pieces. A `WrongQuantity` gives the message of its reason, with the texts of `read_recipe`: `AMOUNT_NOT_A_NUMBER`, `AMOUNT_UNKNOWN_UNIT`, `AMOUNT_NO_UNIT`, or `AMOUNT_ZERO`. The reason `EMPTY` cannot come, because the quantity is never empty.
   - A wrong line gets the message of the first of these three checks that fails, and `add` does not keep the line. A right line is kept. An ingredient may come twice, and the list may be empty, as `read_recipe` allows both (F04 design 2.6). So `read_recipe` reads each kept line of the file with the same name and amount, and finds the same ingredient and the same quantity.
10. **The file.** It has the layout of the example data's recipes, such as `recipes/choy-sum.toml`, with no notes and no comments:

    ```toml
    name = { zh = "<Chinese name>", en = "<English name>" }
    servings = <servings>
    tags = ["<tag>", "<tag>"]

    ingredients = [
      { item = "<name>", amount = "<quantity>" },
      { item = "<name>", amount = "<quantity>" },
    ]

    [steps]
    zh = [
      "<Chinese step>",
    ]
    en = [
      "<English step>",
    ]
    ```

    - The name leaves out a language that is empty (choice 6).
    - `tags` holds each tag once, as you first typed it, in the order of your answer. With no tags it is `tags = []`.
    - `ingredients` holds one line for each kept ingredient line, in the order that you typed them. With none it is `ingredients = []` on one line.
    - `[steps]` holds `zh` and then `en`, each with one line for each step, and leaves out a language with no step.
    - Every text is your answer as you typed it, without whitespace at both ends: the name of an ingredient and of a tag in the language that you typed, not the catalog's spelling, because `read_recipe` finds a name in either language. The quantity keeps your words too, such as `to taste` or `300g`.
    - Each text is a TOML basic string in double quotation marks. `\` becomes `\\`, `"` becomes `\"`, and each control character from U+0000 to U+001F and U+007F becomes `\u` and its four hexadecimal digits, such as `\u0009` for a tab. Every other character stays as it is. So `read_recipe` reads back exactly your text.
    - Every line ends with LF, the last line too. `create_file` writes UTF-8 with no byte order mark ([architecture 5.1](../../architecture.md#51-data-files)).

    So `check`, `list`, `show`, `search`, `menu suggest`, and `shop` read the file with `read_recipe` as any recipe, and F16's `edit` opens it as any recipe file.
11. **How `add` saves the file.** After the last answer, `add` calls `create_file(context.folder, context.folder.recipe_file(recipe_id), text)` once (F11 design 3.3). `is_recipe_id` gave the ID, so `recipe_file` gets a safe name (F03 design 2.1). `create_file` refuses an entry of the file's name, also one that differs only in the case of A to Z, and opens the file in exclusive mode, so `add` never overwrites a file ([architecture 6](../../architecture.md#6-error-handling)). It writes the text with one `write`, and it removes the file after an `OSError` or Ctrl+C during the write. `add` acts on the result:
    - **`CREATED`.** It checks the file (choice 12).
    - **`EXISTS`.** An entry of that name appeared after step 2 listed `recipes/`, for example a file that you saved in another window while `add` waited for an answer. `add` writes `APPEARED` with the full path of the entry to the error stream and gives 1. It created nothing.
    - **`FAILED`.** `add` writes three lines to the error stream and gives 1. The first line is `where` of `problem_lines` (F05 design 2.8): the file as the problem holds it, relative to the data folder, such as `recipes\garlic-broccoli.toml`, or `recipes` when the folder cannot be listed. The second line is two spaces and `what`, such as `The file cannot be written: access is denied.`. The third line is `NOTHING_SAVED`, or `LEFT_BEHIND` with the full path of the file when `create_file` could not remove it.

    Architecture 6 names the file of a problem relative to the data folder, and every other file by its full path. The line after saving, `APPEARED`, and `LEFT_BEHIND` are not problems, so they name the file by its full path, as the prototype's line `已保存 C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml。…` does. The first line of a failure and the lines of the check are problems, so they name the file relative to the data folder. No case needs a change to architecture 6. Your answers live only in memory until `create_file` writes them, so `EXISTS` and `FAILED` lose them.
12. **The check after saving.** After `CREATED`, `add` calls `check_recipe(context.folder, recipe_id)` (3.4). It gives the errors of `read_catalog`, then the problems of `read_recipe` with that catalog: the check that `check` makes of one recipe (F07 design 2.2, steps 2 and 5). The lines go to the output stream with either exit code, because they are the report of a check, as the report of `check` is (architecture 6). The v0.2 test plan says the same in "The report of add and edit".
    - With no problem, `add` writes one line, `SAVED`, such as `已保存 C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。`, the last line of the prototype, and gives 0.
    - With problems, it writes `SAVED_WITH_PROBLEMS` with their counts, then `problem_block` of the errors and then of the warnings, each in the order that `check_recipe` gives (3.5). With an error, `FIX_AND_CHECK` follows, and `add` gives 1. With warnings alone, it gives 0, because a warning never changes the exit code (architecture 6).

    The file stays saved in every case. `add` checked the answers against the catalog of step 1, so an error comes only when the catalog or the file changed after that, for example when you edited the catalog while `add` waited for an answer. A warning comes when you leave out a language (choice 6).
13. **Numbers in messages.** The messages of `add` show counts of problems, the servings of the settings, which are from 1 to 100, and your answers as text. `SERVINGS_WRONG` shows no number. A problem in a file reaches the output only through `stop_at_error`, `problem_lines`, and `problem_block`, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `add` meets F02's limit of 4,300 digits (F02 design 2.3).
14. **Speed.** No performance target names `add`. It reads the catalog and lists `recipes/` before it asks, and after the save it reads the catalog and one recipe, so on a PT01 data folder its own reading takes about as long as `show`, 0.164 s in the release test of v0.1.0 (v0.2 test plan, section 3). The rest is your typing. v0.2-S16 runs `add` on a PT01 folder without timing it. The start of every other command changes little. `cli` imports the few small files of `add` at start, and `add` needs no module that `cli` does not import already through the other commands. `cli` also calls `use_utf8_input(sys.stdin)` once, which reconfigures a stream that nothing has read. By estimate, both take about 1 ms on Troy's PC, far below the 172 ms that `check` has left under PT01's 1 second (0.828 s after F14). This is an estimate, not a measurement. The PT01 cases of v0.1 run again in v0.2's release test.
15. **Only the command is exported.** `add` exports `ADD_COMMAND` and nothing else. Only `cli` may import `add` (architecture 3), so no other name would have a user. `add` keeps its own copies, with the same texts, of `UNKNOWN_TAG` and `NO_TAGS` of `browse`, as `suggest` keeps them (F14 design, choice 4), of the four amount messages of `recipes`, and of the servings message of `datafile`, because those modules keep them internal (architecture 8). A later `[refactor]` PR can share them.

The v0.2 scenarios that run `add` hold with these choices:

- v0.2-S09: step 1 prints the prototype section "In Chinese, with one wrong answer", with the answers on the lines of their prompts (choice 4), and ends with `已保存 <home>\recipe-menu\recipes\garlic-broccoli.toml。检查没有发现问题。`. The file is the 22 lines of the example of 2.2, in UTF-8 with no byte order mark and with LF line ends (choice 10). The ingredient line `橄榄油 1 tbsp` gets `UNKNOWN_INGREDIENT`, and `add` asks for the next line (choice 9).
- v0.2-S10: each of the 5 wrong answers gets one message (choices 3, 7, 8, and 9): `Servings must be a whole number from 1 to 100, such as 2.` after `0` and after `two`, `Unknown tag "breakfast". The tags are quick, home-style, vegetarian, spicy, and staple.`, `  Unknown unit "cups" in "1 cups".`, and `  The catalog has no "Peanut". Enter a name from the catalog, or add it to the catalog first and then run add again.`. Step 1 ends with `Saved <home>\recipe-menu\recipes\egg-fried-rice.toml. The check found no problems.` and exits with 0.
- v0.2-S11: step 1 prints `Recipe ID (also the file name): tomato-egg`, the line of `ID_EXISTS`, and the prompt again, and the empty answer ends `add` with 0 (choice 5). Step 2 prints `菜谱 ID（也是文件名）：` and exits with 0. Neither step writes a file, because `add` writes only after the last answer.
- v0.2-S14: step 5 prints `NO_DATA_FOLDER` and `RUN_INIT` from `cli` and exits with 1, before `add` asks anything (choice 1). The help of steps 1 and 2 gets the line of `add` right after the line of `search`, and the second column stays after 24 columns (2.1). So the Test Manager updates the expected help of v0.2-S14, as section 2 of the v0.2 test plan provides.
- v0.2-S15: step 2 creates only `recipes\garlic-broccoli.toml`. `create_file` writes it in place, with no temporary file (choice 11). The new entry gives the folder `recipes\` a new modification time, as the move of `menu suggest` gives `menus\` one in step 1. So "no other file changed" of step 2 counts files, not folders.
- v0.2-S16: `食材300 100 g` and `食材150 适量` split as choice 9 gives. The check reads the catalog of 300 ingredients and the one new recipe, and finds no problem.
- v0.2-S18: the console reads the Chinese answers of the input method as typed, Backspace edits the line, and `chcp 437` changes nothing (choice 4). Ctrl+C at the second question gives exit code 130 with no further text, and no file.
- Through a pipe, `add` writes each answer after its prompt (choice 4), so the output of v0.2-S09 to v0.2-S11 has the lines of the prototype sections. A line of a Markdown prototype shows no space at its end. In the output, an English prompt keeps its space after the colon also when the answer is empty, such as `Recipe ID (also the file name): `, and the line of an empty answer in a list is two spaces. So the Test Manager compares the lines as the examples of 2.2 give them, and updates the rule "Answers to `add`" of the v0.2 test plan to say that each answer follows its prompt.
- v0.1-S01, v0.1-S02, and v0.1-S13: F15 changes no file that `init` or `menu new` writes. `add` writes only `recipes/<id>.toml`, and F15 adds no key to `settings.toml`. So the three scenarios hold, as the v0.2 test plan expects.

Troy decides these three points. The design follows the recommendation of each.

- **A. New texts.** The prototype gives the Chinese prompts, the Chinese message for an unknown ingredient, the Chinese line after saving, and the English prompt and message for an ID that exists. The other texts follow the wording of the prototype or of an existing message. `add` has 32 messages, listed in 2.2. Seven are copies of existing messages, and one comes whole from the prototype. The recommendation is to accept the other 24 as 2.2 gives them:
  - The English prompts, such as `Chinese name: `, `Servings [2]: `, `Tags, separated by commas: `, `Ingredients, one per line, as "name quantity". An empty line ends the list:`, and `English steps, one per line. An empty line ends the list (optional):`.
  - The English lines for the prototype's Chinese lines: `The catalog has no "{name}". Enter a name from the catalog, or add it to the catalog first and then run add again.` and `Saved {file}. The check found no problems.`.
  - The Chinese line for the prototype's English line: `菜谱 {id} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {id}”。`.
  - The messages for a wrong ID, a missing name or missing steps, and an ingredient line with no space before the quantity: `NOT_AN_ID`, `NAME_NEEDED`, `STEPS_NEEDED`, and `NAME_AND_QUANTITY`, such as `Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".` and `请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。`.
  - The lines after saving with problems, such as `Saved {file}. The check found 1 error and 2 warnings:` and `已保存 {file}。检查发现了 1 个错误和 2 个警告：`, and `FIX_AND_CHECK`.
  - The lines of an early end and of a failed save: `INPUT_ENDED`, `APPEARED`, `NOTHING_SAVED`, and `LEFT_BEHIND`.
  - The line of the help: `Add a recipe by answering questions.` and `回答问题，添加一个菜谱。`.
- **B. The answers that may stay empty** (choice 6).
  - Option 1, recommended: either language of the name, and either list of steps, may stay empty when the other language has text. The prompts stay as the prototype shows them, except that the English steps say "optional" only when there is a Chinese step. The check after saving warns about each language that you left out.
  - Option 2: only the English steps may stay empty, as the prototype marks them. An empty Chinese name, English name, or list of Chinese steps gets a message and the question again. Choices 3 and 6, the messages of 2.2, and the examples change before the mock PR.
  - The reason for option 1: requirements 3 lets a name or the steps lack one language, so `add` can write every recipe that the requirements allow, except for notes, also one in English only.
- **C. The place of `add` in the help** (choice 1).
  - Option 1, recommended: right after `search`. The test-fix PR of section 3 changes F11-T01 before the mock PR.
  - Option 2: last, after `shop`. No test changes. Choice 1, 2.1, and the help of v0.2-S14 change before the mock PR.
  - The reason for option 1: `list`, `show`, `search`, `add`, and later `edit` then stand together, and the help reads by what each command works on: the data folder, the recipes, the week menus, and the shopping list.

These later features are meant to build on F15. Their own designs decide the details.

- F16's `edit` can check the recipe with `check_recipe` after the editor closes, and show its problems with `problem_block`, whose indents are those of the F16 prototype "An edit that leaves a mistake". F16 can put `edit ID` right after `add` in the help. After the test-fix PR of section 3, no test of an accepted feature depends on the line that follows `search`.
- `add` takes nothing from `suggest`, and F16 needs nothing from `add`.

troy-mode's flow has one mock PR and one implementation PR. The entry in `COMMANDS` after `SEARCH_COMMAND` breaks F11-T01, which takes the two lines after the line of `search` as the lines of `menu new` and `menu show` (section 3). The Developer never edits a test (R08), and every test of an accepted feature must pass (R10). So a test-fix PR before the F15 mock PR changes F11-T01, so that it finds the line of `menu new` by its start and holds with and without a line after `search`. The test plan names the test and the PR. Under option 2 of point C, no test-fix PR is needed.

The mock (PR 3) holds `src/recipe_menu/commands/add/__init__.py`, `messages.py`, and one internal file for `run`, such as `_run.py`, and the entry in `src/recipe_menu/cli/_commands.py`. It adds the field `input` with its default to `Context`, and the parameter `stdin` to `main`, which the mock does not pass on, so the context gets its default. It adds `use_utf8_input` to `text`, which changes nothing in the mock. It adds `check_recipe` and `problem_block` to `check` in a new internal file, which give `()` in the mock, and leaves the report of `check` as it is, so F07's tests keep passing. It defines every message and `ADD_COMMAND` with all its fields. Its `run` reads no file, reads no answer, writes nothing, and gives 0. So a new test fails against the mock (R09) when it checks a prompt, a message, an output line, exit code 1, the bytes of the new file, a failure and its lines, the stream that `main` passes on, the encoding that `use_utf8_input` sets, or the problems and lines of `check_recipe` and `problem_block`. These tests pass against the mock and break R09: a test that checks only the fields of `ADD_COMMAND`, the help, a message, exit code 0, or the default of `Context.input`. So does a test of what `cli` does before it runs `add`, such as a missing data folder, broken settings, an extra argument, or an unknown option. So does a test that checks only that a run writes no file, as for an empty first answer, and a test of `check_recipe` that expects `()` alone. Each such test must also check something that the mock gets wrong, such as the output. The mock changes about 10 files, more than R03's 5, in about 400 lines by estimate, so its description gives a soft-limit reason. The reason is that the tests reach the context, `main`, `text`, and `check` both directly and through `add`, so they come in one stage, as in the mocks of F08, F11, F13, and F14.

The implementation (PR 5) holds `run` with its questions, its reading of answers, the splitting of an ingredient line, the text of the file, and the lines after saving, in internal files of `add`, such as `_run.py`, `_ask.py`, `_ingredient.py`, `_file.py`, and `_report.py`. It also holds `check_recipe` and `problem_block`, with the report of `check` written through `problem_block`, the stream in `main`, and `use_utf8_input`. By estimate, it changes about 10 files in about 650 lines, more than R03's limits, so its description gives a soft-limit reason too: the tests of `add` need all these parts at once. The Developer runs troy-check early.

### 2.1 `ADD_COMMAND`

- Module: add
- Purpose: The description of the `add` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` asks the questions of 2.2, writes the new recipe file, and checks it.

Signature:

```python
ADD_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("add",)
#   help_line = ADD_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("add",)`. | None |
| `help_line` | `Message` | `ADD_HELP`: "Add a recipe by answering questions." and "回答问题，添加一个菜谱。". | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Reads the catalog and the listing of `recipes/`, asks the questions, writes the file through `create_file`, checks it, and writes the lines of 2.2. | Gives 0 or 1. Raises nothing for bad data, a wrong answer, or a failure on the disk. Lets `KeyboardInterrupt` go on to `cli`. |
| `argument` | `None` | `add` takes no argument. | None |
| `options` | An empty tuple | `add` has no options of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `add` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4), with the field `input` of 3.1. | `run` uses `context.lang`, `context.folder`, `context.settings.servings`, `context.out`, `context.err`, and `context.input`. It uses neither `context.today` nor `context.random`. |
| `arguments` | `Arguments` | What the command line gives `add` (F05 design 2.6). | Empty, because `add` declares no argument and no option. `run` does not read it. |

- Return value: `ADD_COMMAND`, a `Command`.
  - `ADD_COMMAND.usage` is `add` in both languages. So the help shows `add`, and a usage error quotes `recipe-menu add`.
  - `ADD_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its lines in `context.lang`, and gives 0 or 1.

After F15, the help lists these commands and options, with the second column after 24 columns, as after F14 (choice 1). The other lines of the help are those of the F05 prototype. In English:

```text
Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  add                   Add a recipe by answering questions.
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
  add                   回答问题，添加一个菜谱。
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

Errors: None. `run` raises no `UsageError`, because `add` takes no argument value.

- Side effects: Those of 2.2. `run` reads the catalog and lists `recipes/`, reads the answers from `context.input`, creates `recipes/<id>.toml` through `create_file`, reads the catalog and the new file again through `check_recipe`, and writes to `context.out` or `context.err`.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, with its seven recipes, and `home` is an empty temporary folder outside it ([architecture 10](../../architecture.md#10-test-setup)). The context holds the answers `tomato-egg` and an empty line, so `run` writes the lines of the prototype "An ID that exists" and ends. The help comes from `COMMANDS`, which holds ten commands after F15.

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.add import ADD_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings

assert ADD_COMMAND.words == ("add",)
assert ADD_COMMAND.usage == BiText("add", "add")
assert ADD_COMMAND.help_line.render(Lang.EN) == "Add a recipe by answering questions."
assert ADD_COMMAND.help_line.render(Lang.ZH) == "回答问题，添加一个菜谱。"
assert (ADD_COMMAND.argument, ADD_COMMAND.options) == (None, ())
assert ADD_COMMAND.folder is FolderUse.READ

out, err = io.StringIO(), io.StringIO()
answers = io.StringIO("tomato-egg\n\n")
context = Context(Lang.EN, folder, Settings(), out, err, date(2026, 11, 10), input=answers)
assert ADD_COMMAND.run(context, Arguments()) == 0
exists = "The recipe tomato-egg already exists. Enter another ID, "
assert out.getvalue().splitlines() == [
    "Recipe ID (also the file name): tomato-egg",
    exists + 'or run "recipe-menu edit tomato-egg".',
    "Recipe ID (also the file name): ",
]
assert err.getvalue() == ""
assert len(list(folder.recipes.iterdir())) == 7


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
assert len(english) == 23
assert english[9:12] == [
    "  search WORD...        Find recipes by name, ingredient, or tag.",
    "  add                   Add a recipe by answering questions.",
    "  menu new [WEEK]       Create an empty week menu.",
]
assert english[17].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[10] == "  add                   回答问题，添加一个菜谱。"
```

### 2.2 `recipe-menu add`

- Module: add
- Purpose: The command that asks for a new recipe one line at a time, checks each answer against the catalog, asks again after a wrong answer, and writes a new recipe file ([requirements 3](../../requirements.md#3-how-users-interact-with-it) and [4](../../requirements.md#4-features)). The F15 prototype "In Chinese, with one wrong answer" and "An ID that exists" shows it.

Signature:

```text
recipe-menu add [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--lang` | `en` or `zh` | The language of the prompts and of every message. It does not change the file. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `add`. | None |
| The standard input | Lines of text | The answers, one per line (choice 4). | UTF-8 through a pipe. Any text in a console. |

`add` takes these steps, in order. `path` is `context.folder.recipe_file(recipe_id)`. A question that gets a wrong answer is asked again, as choice 3 gives it, before the next step.

1. `read_catalog(context.folder)` gives `catalog` and its problems (F03 design 2.8). With an error among the problems, `add` gives `stop_at_error(context, error)` for the first one.
2. `list_recipe_ids(context.folder)` gives `ids` and their problems (F04 design 2.5). With an error among the problems, `add` stops at the first one with `stop_at_error`.
3. Question 1 gives `recipe_id` (choice 5). An empty answer, or the end of the input, makes `add` give 0 here.
4. Questions 2 and 3 give the names (choice 6).
5. Question 4 gives the servings (choice 7).
6. Question 5 gives the tags (choice 8).
7. Question 6 gives the ingredient lines (choice 9).
8. Questions 7 and 8 give the steps (choice 6).
9. `add` builds the text of the file (choice 10) and calls `create_file(context.folder, path, text)` once (F11 design 3.3). For `EXISTS`, it writes `APPEARED` to the error stream and gives 1. For `FAILED`, it writes the three lines of a failure to the error stream and gives 1 (choice 11).
10. `check_recipe(context.folder, recipe_id)` gives the problems (3.4). `add` writes the lines after saving to the output stream and gives 1 when a problem is an error, and 0 otherwise (choice 12).

The end of the input in steps 4 to 8 makes `add` write `INPUT_ENDED` to the error stream and give 1 (choice 4). The warnings of steps 1 and 2 change nothing.

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | Question 1 got an empty answer or the end of the input, or the file was saved and its check found no error. | The output stream: the prompts, your answers when the input is not a terminal, the messages after wrong answers, and the lines after saving. |
| 1 | The catalog or the listing of `recipes/` has an error, the input ended after question 1, `create_file` gave `EXISTS` or `FAILED`, or the check after saving found an error. | The output stream holds the session up to there. The error stream holds the three lines of `stop_at_error`, `INPUT_ENDED`, `APPEARED`, or the three lines of a failure. After a check that found an error, the lines after saving go to the output stream, and nothing goes to the error stream. |
| 130 | Ctrl+C. | Nothing more, as `cli` gives it (F05 design 2.10). |

The output is these lines, each ended by a line break, except that a prompt of questions 1 to 5 has no line break of its own:

| Case | What `add` writes to the output stream |
| --- | --- |
| A question | The prompt. Then, when the input is not a terminal, your answer as you typed it and a line break. |
| A list (questions 6 to 8) | The prompt of the list and a line break. Then for each line of the list: two spaces, then, when the input is not a terminal, your line and a line break. |
| A wrong answer | The message and a line break. After an ingredient line, two spaces come before the message. |
| The end of the input | When the input is not a terminal, a line break after the prompt. |
| The file was saved, and the check found no problem | `SAVED`. |
| The file was saved, and the check found problems | `SAVED_WITH_PROBLEMS`. Then `problem_block` of the errors, then `problem_block` of the warnings (3.5). Then, with an error, `FIX_AND_CHECK`. |

A failure of the save is three lines on the error stream: `where` of `problem_lines(creation.problem, context.lang)`, then two spaces and `what`, and then `NOTHING_SAVED`, or `LEFT_BEHIND` when `creation.left` holds the file (choice 11).

The messages of `add` are these. `UNKNOWN_TAG` is a `Plural` (F02 design 2.4), picked by the number of the catalog's tags. `ERROR_COUNT` and `WARNING_COUNT` are `Plural` values, each picked by its `count`. Their form "for more" is the form for every count other than 1, and their Chinese text is the same in both forms. The prompts of questions 1 to 5 end with a space in English, and with `：` and no space in Chinese.

| Name | English | Chinese |
| --- | --- | --- |
| `ADD_HELP` | `Add a recipe by answering questions.` | `回答问题，添加一个菜谱。` |
| `ID_PROMPT` | `Recipe ID (also the file name): ` | `菜谱 ID（也是文件名）：` |
| `ZH_NAME_PROMPT` | `Chinese name: ` | `中文名：` |
| `EN_NAME_PROMPT` | `English name: ` | `英文名：` |
| `SERVINGS_PROMPT` | `Servings [{servings}]: ` | `份数 [{servings}]：` |
| `TAGS_PROMPT` | `Tags, separated by commas: ` | `标签，用逗号分隔：` |
| `INGREDIENTS_PROMPT` | `Ingredients, one per line, as "name quantity". An empty line ends the list:` | `食材，每行一个，写“名称 数量”，空行结束：` |
| `ZH_STEPS_PROMPT` | `Chinese steps, one per line. An empty line ends the list:` | `中文步骤，每行一步，空行结束：` |
| `EN_STEPS_PROMPT` | `English steps, one per line. An empty line ends the list:` | `英文步骤，每行一步，空行结束：` |
| `EN_STEPS_OPTIONAL_PROMPT` | `English steps, one per line. An empty line ends the list (optional):` | `英文步骤，每行一步，空行结束（可以不写）：` |
| `NOT_AN_ID` | `"{id}" cannot be a recipe ID. An ID has only the small letters a to z, digits, and "-", and starts with a letter or a digit, such as "tomato-egg". Windows device names, such as "con", are not IDs.` | `“{id}”不能用作菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，并以字母或数字开头，比如“tomato-egg”。“con”这样的 Windows 设备名不能用作 ID。` |
| `ID_EXISTS` | `The recipe {id} already exists. Enter another ID, or run "recipe-menu edit {id}".` | `菜谱 {id} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {id}”。` |
| `NAME_NEEDED` | `A recipe needs a name in at least one language. Enter its English name.` | `菜谱至少要有一种语言的名称。请输入它的英文名。` |
| `SERVINGS_WRONG` | `Servings must be a whole number from 1 to 100, such as 2.` | `份数必须是 1 到 100 之间的整数，比如 2。` |
| `UNKNOWN_TAG`, for one tag | `Unknown tag "{value}". The only tag is {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `UNKNOWN_TAG`, for more tags | `Unknown tag "{value}". The tags are {tags}.` | `未知标签“{value}”。现有标签：{tags}。` |
| `NO_TAGS` | `Unknown tag "{value}". The catalog has no tags.` | `未知标签“{value}”。目录里没有标签。` |
| `NAME_AND_QUANTITY` | `Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".` | `请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。` |
| `UNKNOWN_INGREDIENT` | `The catalog has no "{name}". Enter a name from the catalog, or add it to the catalog first and then run add again.` | `目录里没有“{name}”。请输入目录里的名称，或先把它加入目录后再运行 add。` |
| `AMOUNT_NOT_A_NUMBER` | `The amount "{amount}" must start with a number of at most 15 digits, such as 300 or 1.5, or be "适量" or "to taste".` | `数量“{amount}”必须以不超过 15 位的数字开头，比如 300 或 1.5，或者写成“适量”或“to taste”。` |
| `AMOUNT_UNKNOWN_UNIT` | `Unknown unit "{unit}" in "{amount}".` | `数量“{amount}”里有未知单位“{unit}”。` |
| `AMOUNT_NO_UNIT` | `The amount "{amount}" has no unit, and the catalog gives "{ingredient}" no default unit. Write a unit after the number, such as "300 g".` | `数量“{amount}”没有单位，目录也没有给“{ingredient}”默认单位。请在数字后面写上单位，比如“300 g”。` |
| `AMOUNT_ZERO` | `The amount "{amount}" is 0. Write a number of more than 0, or "适量" or "to taste".` | `数量“{amount}”是 0。请写大于 0 的数，或者写成“适量”或“to taste”。` |
| `STEPS_NEEDED` | `A recipe needs steps in at least one language. Enter at least one English step.` | `菜谱至少要有一种语言的步骤。请至少输入一步英文步骤。` |
| `SAVED` | `Saved {file}. The check found no problems.` | `已保存 {file}。检查没有发现问题。` |
| `SAVED_WITH_PROBLEMS` | `Saved {file}. The check found {problems}:` | `已保存 {file}。检查发现了 {problems}：` |
| `ERROR_COUNT`, for one | `{count} error` | `{count} 个错误` |
| `ERROR_COUNT`, for more | `{count} errors` | `{count} 个错误` |
| `WARNING_COUNT`, for one | `{count} warning` | `{count} 个警告` |
| `WARNING_COUNT`, for more | `{count} warnings` | `{count} 个警告` |
| `FIX_AND_CHECK` | `Fix the errors, then run "recipe-menu check".` | `改正错误后，运行“recipe-menu check”。` |
| `INPUT_ENDED` | `The answers ended before the recipe was complete. Nothing was saved.` | `回答在菜谱完成之前就结束了。没有保存任何东西。` |
| `APPEARED` | `Nothing was saved: {file} appeared while you answered. Run "recipe-menu add" again with another ID.` | `没有保存任何东西：你回答问题时出现了 {file}。请换一个 ID，再运行“recipe-menu add”。` |
| `NOTHING_SAVED` | `Nothing was saved.` | `没有保存任何东西。` |
| `LEFT_BEHIND` | `Nothing was saved, but add could not remove {file}. Delete it.` | `没有保存任何东西，但 add 没能删除 {file}。请删除它。` |

`SERVINGS_WRONG` has the text of `SERVINGS_NOT_A_NUMBER` of `datafile` (F05 design 3.1). `UNKNOWN_TAG` and `NO_TAGS` have the texts of `list` (F09 design 2.2). The four amount messages have the texts of `read_recipe` (F04 design 2.6). The Chinese prompts, the Chinese `UNKNOWN_INGREDIENT` and `SAVED`, and the English `ID_PROMPT` and `ID_EXISTS` are the lines of the prototype.

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `id` | The answer to question 1, without whitespace at both ends. |
| `servings` | `context.settings.servings`, an `int` from 1 to 100. |
| `value` | The first part of the answer to question 5 that names no tag, without whitespace at both ends. |
| `tags` | `and_list` of the names of the catalog's tags, each as its `BiText`, in the catalog's order, as for `list` (F09 design 2.2). |
| `name` | The name of the ingredient line (choice 9). |
| `amount` | The `text` of the `WrongQuantity`: the quantity of the line. |
| `unit` | The `unit` of the `WrongQuantity`, such as `cups`. |
| `ingredient` | The name of the ingredient, as its `BiText`, so each language shows its own name. |
| `file` | In `SAVED` and `SAVED_WITH_PROBLEMS`, `str(path)`, the full path, such as `C:\Users\Troy\recipe-menu\recipes\garlic-broccoli.toml`. In `APPEARED`, `str(creation.existing)`. In `LEFT_BEHIND`, `str(creation.left[0])`. |
| `problems` | `and_list` of `ERROR_COUNT` with the number of errors and `WARNING_COUNT` with the number of warnings, each as a `BiText`, and leaving out a count of 0: `1 error and 2 warnings` and `1 个错误和 2 个警告`. |
| `count` | The number of errors in `ERROR_COUNT`, and of warnings in `WARNING_COUNT`. |

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `add` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT` on the error stream | The data folder is not a folder. `cli` checks it in step 9 of F05 design 2.10, because `add` has `FolderUse.READ`. |
| Exit code 1, with the first error of the settings and `RUN_CHECK` on the error stream | The settings have an error. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "garlic-broccoli". Write "recipe-menu add".` | A word follows `add`. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"add" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 1, with the three lines of `stop_at_error` on the error stream, such as `catalog.toml, line 2`, `  The file cannot be read: a closing "]" is missing.`, and `RUN_CHECK` | The catalog or the listing of `recipes/` has an error (steps 1 and 2). `add` asks nothing. |
| Exit code 1, with `INPUT_ENDED` on the error stream | The input ended after question 1 (choice 4). No file. |
| Exit code 1, with `APPEARED` on the error stream | `create_file` gave `EXISTS` (choice 11). No file. |
| Exit code 1, with the three lines of a failure on the error stream | `create_file` gave `FAILED` (choice 11). No file, or the file of `LEFT_BEHIND`. |
| Exit code 1, with the lines after saving on the output stream | The check after saving found an error (choice 12). The file stays saved. |
| Exit code 130 | Ctrl+C. `add` writes no file before the last answer, and `create_file` removes a file that it was writing (choice 4). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `add` then reads `catalog.toml` once and lists `recipes/` once, reads the answers from the input stream, and writes to the output stream. After the last answer, it creates `recipes/<id>.toml` through `create_file` (choice 11), and reads `catalog.toml` and the new file once each through `check_recipe` (choice 12). It changes no other file and leaves no temporary file. After an error, an empty first answer, the end of the input, or Ctrl+C before the save, it writes no file.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. `add` runs `main` with the answers on a stream, each followed by a line break. The first run is v0.2-S09, and the file that it writes follows. The second run gives a wrong answer of each kind of v0.2-S10. The third leaves out the English name and the English steps, so its check finds two warnings. The last runs end with the input after question 2, with an empty first answer, and with no answer at all.

```python
import io
from datetime import date
from pathlib import Path

from recipe_menu.cli import main


def add(answers: list[str], *extra: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["add", "--data", str(folder.root), *extra],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        stdin=io.StringIO("".join(f"{answer}\n" for answer in answers)),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


chinese = [
    "garlic-broccoli",
    "蒜蓉西兰花",
    "Garlic broccoli",
    "",
    "快手, 素",
    "西兰花 300 g",
    "大蒜 4 瓣",
    "橄榄油 1 tbsp",
    "食用油 1 tbsp",
    "盐 适量",
    "",
    "西兰花切小朵，焯水 1 分钟，捞出沥干。",
    "大蒜切末，热油爆香。",
    "倒入西兰花翻炒，加盐调味。",
    "",
    "Cut the broccoli into florets. Blanch them for 1 minute and drain.",
    "Mince the garlic, and fry it in the hot oil until fragrant.",
    "Add the broccoli, stir-fry it, and season with salt.",
    "",
]
broccoli = folder.recipe_file("garlic-broccoli")
assert add(chinese, "--lang", "zh") == (
    0,
    [
        "菜谱 ID（也是文件名）：garlic-broccoli",
        "中文名：蒜蓉西兰花",
        "英文名：Garlic broccoli",
        "份数 [2]：",
        "标签，用逗号分隔：快手, 素",
        "食材，每行一个，写“名称 数量”，空行结束：",
        "  西兰花 300 g",
        "  大蒜 4 瓣",
        "  橄榄油 1 tbsp",
        "  目录里没有“橄榄油”。请输入目录里的名称，或先把它加入目录后再运行 add。",
        "  食用油 1 tbsp",
        "  盐 适量",
        "  ",
        "中文步骤，每行一步，空行结束：",
        "  西兰花切小朵，焯水 1 分钟，捞出沥干。",
        "  大蒜切末，热油爆香。",
        "  倒入西兰花翻炒，加盐调味。",
        "  ",
        "英文步骤，每行一步，空行结束（可以不写）：",
        "  Cut the broccoli into florets. Blanch them for 1 minute and drain.",
        "  Mince the garlic, and fry it in the hot oil until fragrant.",
        "  Add the broccoli, stir-fry it, and season with salt.",
        "  ",
        f"已保存 {broccoli}。检查没有发现问题。",
    ],
    [],
)
assert broccoli.read_bytes() == "\n".join(
    [
        'name = { zh = "蒜蓉西兰花", en = "Garlic broccoli" }',
        "servings = 2",
        'tags = ["快手", "素"]',
        "",
        "ingredients = [",
        '  { item = "西兰花", amount = "300 g" },',
        '  { item = "大蒜", amount = "4 瓣" },',
        '  { item = "食用油", amount = "1 tbsp" },',
        '  { item = "盐", amount = "适量" },',
        "]",
        "",
        "[steps]",
        "zh = [",
        '  "西兰花切小朵，焯水 1 分钟，捞出沥干。",',
        '  "大蒜切末，热油爆香。",',
        '  "倒入西兰花翻炒，加盐调味。",',
        "]",
        "en = [",
        '  "Cut the broccoli into florets. Blanch them for 1 minute and drain.",',
        '  "Mince the garlic, and fry it in the hot oil until fragrant.",',
        '  "Add the broccoli, stir-fry it, and season with salt.",',
        "]",
        "",
    ]
).encode("utf-8")

english = [
    "egg-fried-rice",
    "蛋炒饭",
    "Egg fried rice",
    "0",
    "two",
    "3",
    "breakfast",
    "quick, staple",
    "Rice 1 cups",
    "Rice 300 g",
    "Egg 3",
    "Peanut 30 g",
    "Scallion 1 stalk",
    "Salt to taste",
    "Cooking oil 2 tbsp",
    "",
    "鸡蛋打散。",
    "热油炒蛋，加米饭和葱花翻炒。",
    "",
    "Beat the eggs.",
    "Scramble the eggs, then stir-fry them with the rice and scallion.",
    "",
]
servings = "Servings must be a whole number from 1 to 100, such as 2."
tags = "The tags are quick, home-style, vegetarian, spicy, and staple."
peanut = 'The catalog has no "Peanut". Enter a name from the catalog, '
peanut += "or add it to the catalog first and then run add again."
rice = folder.recipe_file("egg-fried-rice")
code, lines, errors = add(english)
assert (code, errors) == (0, [])
assert lines[3:16] == [
    "Servings [2]: 0",
    servings,
    "Servings [2]: two",
    servings,
    "Servings [2]: 3",
    "Tags, separated by commas: breakfast",
    f'Unknown tag "breakfast". {tags}',
    "Tags, separated by commas: quick, staple",
    'Ingredients, one per line, as "name quantity". An empty line ends the list:',
    "  Rice 1 cups",
    '  Unknown unit "cups" in "1 cups".',
    "  Rice 300 g",
    "  Egg 3",
]
assert lines[16:18] == ["  Peanut 30 g", f"  {peanut}"]
assert lines[-5] == "English steps, one per line. An empty line ends the list (optional):"
assert lines[-1] == f"Saved {rice}. The check found no problems."
assert rice.read_text(encoding="utf-8").splitlines()[:7] == [
    'name = { zh = "蛋炒饭", en = "Egg fried rice" }',
    "servings = 3",
    'tags = ["quick", "staple"]',
    "",
    "ingredients = [",
    '  { item = "Rice", amount = "300 g" },',
    '  { item = "Egg", amount = "3" },',
]

partly = ["scallion-egg", "葱花蛋", "", "", "快手，quick", "鸡蛋 3", "葱 2", ""]
partly += ["鸡蛋打散，加葱花煎熟。", "", ""]
egg = folder.recipe_file("scallion-egg")
relative = Path("recipes", "scallion-egg.toml")
code, lines, errors = add(partly)
assert (code, errors) == (0, [])
assert lines[-5:] == [
    f"Saved {egg}. The check found 2 warnings:",
    f"  {relative}, name",
    "    No English name. Commands show the Chinese name instead.",
    f"  {relative}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
]
assert egg.read_text(encoding="utf-8").splitlines() == [
    'name = { zh = "葱花蛋" }',
    "servings = 2",
    'tags = ["快手"]',
    "",
    "ingredients = [",
    '  { item = "鸡蛋", amount = "3" },',
    '  { item = "葱", amount = "2" },',
    "]",
    "",
    "[steps]",
    "zh = [",
    '  "鸡蛋打散，加葱花煎熟。",',
    "]",
]

ended = "The answers ended before the recipe was complete. Nothing was saved."
assert add(["new-dish", "新菜"]) == (
    1,
    ["Recipe ID (also the file name): new-dish", "Chinese name: 新菜", "English name: "],
    [ended],
)
assert not folder.recipe_file("new-dish").exists()
assert add([""], "--lang", "zh") == (0, ["菜谱 ID（也是文件名）："], [])
assert add([]) == (0, ["Recipe ID (also the file name): "], [])
assert len(list(folder.recipes.iterdir())) == 10
```

## 3. Changes to existing interfaces

F15 adds to four implemented modules. Architecture 5.2 plans the input stream: "In v0.2, F15 adds the input stream" to `Context`, and F05 design section 2 and F14 design section 2 plan it for `main`. Architecture 3 plans that `add` reuses `check` to check one recipe, and F07 design section 2 leaves to F15 the names that it needs. `use_utf8_input` is the input side of F02's `use_utf8`, in `text`, which owns the console streams. No call of an exported name of F01 to F14 breaks: the new field has a default, the new parameter of `main` is optional, and `text` and `check` gain names. The requirements already name `add`, so no `[docs]` PR approves these additions. The Architect reviews them in this design, as it reviewed F14's additions. ADR-0004 says that `cli` asks `text` to set stdout and stderr to UTF-8. The Architect decides whether ADR-0004 gains a sentence for stdin.

1. `app`: `Context` gets the field `input` (3.1). Two contexts are now equal when their eight fields are equal, and the streams and the generator compare as objects.
2. `cli`: `main` gets the parameter `stdin` (3.2), and `COMMANDS` gets `ADD_COMMAND` after `SEARCH_COMMAND` (choice 1).
3. `text`: `use_utf8_input` (3.3).
4. `check`: `check_recipe` (3.4) and `problem_block` (3.5). The report of `check` writes each of its two blocks with `problem_block`, so its output does not change, and F07's tests hold.

These changes follow at F15's acceptance, outside the design:

- The Product Manager adds the line of `add` after the line of `search` to the two help blocks of the F05 prototype, "Help in English" and "Help in Chinese", and changes their note to say that the help lists `add` too and that F16 adds `edit`. The Test Manager ruled at F14's acceptance that those two blocks show the help of the accepted features.
- The Test Manager updates the expected help of v0.2-S14, and the rule "Answers to `add`" of the v0.2 test plan (section 2).

This test of an accepted feature changes, and section 2 says in which PR:

- F11-T01 (`test_f11_t01_the_menu_new_command_creates_the_file_and_the_help_lists_it`) takes the two lines after the line of `search` in the help of the real `COMMANDS` as the lines of `menu new` and `menu show`. With the entry of the mock, the line after `search` is the line of `add`. A test-fix PR before the mock PR makes it find the line of `menu new` by its start. Under option 2 of point C, F11-T01 holds and no test changes.

These tests stay true. The first cell of `add` is 3 columns wide, so the second column of both tables stays after 24 columns. F07-T17 and F13-T01 find their line by its start and compare its text column with that of `--lang en|zh`. F08-T14 checks that `check` follows `init`, F09-T01 that `list` and `show` follow `check`, F10-T01 that `search` follows `show ID`, and F14-T01 that `menu suggest` follows `menu show`, and the line of `add` comes between none of them. F09-T19, F11-T27, F11-T32, F11-T35, F13-T22, F13-T27, F14-T21, and F14-T31 compare one help of the real `COMMANDS` with another. `add` is one word, so `recipe-menu menu` still lists only the three `menu` commands, as F11-T32 with the commands of v0.1 and F14-T21 expect. F05-T10 and F05-T11 compare the keys of the settings, and F15 adds no key. The tests of F05 to F14 run their own commands, build contexts with six or seven values, and compare no two contexts that would be equal but for the new field. A test that calls `main` with no `stdin` gets `sys.stdin`, which pytest replaces with an object that is not an `io.TextIOWrapper`, so `use_utf8_input` leaves it as it is, and no command but `add` reads it. `run_module` of the tests sets `PYTHONIOENCODING` to `ascii`, and `use_utf8_input` still makes `python -m recipe_menu add` read a pipe as UTF-8. No test runs `add`, which gives `Unknown command "add".` before the mock.

F15 uses these interfaces as their designs give them, and changes none of them:

- F01's `Quantity`, `Unit`, `WrongQuantity`, `WrongQuantityReason`, and `parse_quantity`.
- F02's `BiText`, `Lang`, `Message`, `Plural`, and `and_list`.
- F03's `DataFolder` with `recipe_file` and `relative`, `Problem`, `Severity`, `Catalog` with `find_ingredient` and `find_tag`, and `read_catalog`.
- F04's `is_recipe_id`, `list_recipe_ids`, and `read_recipe`, the last through `check_recipe`.
- F05's `Arguments`, `Command`, `Context`, `FolderUse`, `first_error`, `problem_lines`, and `stop_at_error` in `app`, `MIN_SERVINGS` and `MAX_SERVINGS` in `datafile`, `Settings` in `settings`, and `COMMANDS` and `main` in `cli`, with the additions of 3.1 and 3.2.
- F07's `CHECK_COMMAND`, with the additions of 3.4 and 3.5.
- F11's `FileOutcome`, `FileCreation`, and `create_file` in `datafile`.

### 3.1 `Context.input`

- Module: app
- Purpose: The input stream of a command ([architecture 5.2](../../architecture.md#52-values) and [8](../../architecture.md#8-naming-and-coding-rules)). `cli` passes the standard input (3.2), and a test passes a stream of answers. `add` reads its answers from it (choice 4).

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
    input: TextIO = field(default_factory=io.StringIO)
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `input` | `TextIO` | The stream that a command reads lines from. | Open. When `cli` builds the context, the stream that `main` got, else `sys.stdin` (3.2). Without it, a new empty `io.StringIO` for each context, so a command that reads finds the end of the input at once. The text that it gives can be encoded as UTF-8. |

The other fields keep their meanings and constraints (F05 design 2.4, F14 design 3.3). `io` is the standard module, and `field` is `dataclasses.field`.

- Return value: A `Context`. Two contexts are equal when their eight fields are equal, and the streams and the generator compare as objects. So two contexts that each made their own default stream are not equal. A `Context` is hashable.

Errors: None

- Side effects: None. Building a context with the default makes an empty `io.StringIO`, which reads nothing of the outside world.
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
today = date(2026, 11, 10)
answers = io.StringIO("garlic-broccoli\n")
context = Context(Lang.EN, folder, Settings(), out, err, today, input=answers)
assert context.input is answers
assert context.input.readline() == "garlic-broccoli\n"
first = Context(Lang.EN, folder, Settings(), out, err, today)
second = Context(Lang.EN, folder, Settings(), out, err, today)
assert first.input is not second.input
assert first.input.readline() == second.input.readline() == ""
assert first != second
```

### 3.2 `main`: the parameter `stdin`

- Module: cli
- Purpose: Lets a test pass the answers of a command ([architecture 8](../../architecture.md#8-naming-and-coding-rules): only `cli` reads the console streams). `main` passes the stream to the command in `Context.input` (3.1).

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
    stdin: TextIO | None = None,
) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `stdin` | `TextIO` or `None` | The input stream of the command. | `None` gives `sys.stdin`, after `use_utf8_input` (3.3), as `None` gives `sys.stdout` after `use_utf8` for `stdout`. |

The other parameters keep their meanings and constraints (F05 design 2.9, F14 design 3.4). The mock adds the parameter and does not pass it on (section 2), so that is the implementation.

- Return value: The exit code of F05 design 2.10, as before. In step 10 of F05 design 2.10, the `Context` holds the input stream.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `commands` breaks its constraint, as before (F05 design 2.9). |

- Side effects: Those of F05 design 2.9. When `stdin` is `None`, `main` calls `use_utf8_input(sys.stdin)` once at start, which reads nothing from the stream. `main` itself never reads the stream.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, and `home` is an empty temporary folder outside it. `ECHO` stands in for a command that reads a line.

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Command, Context
from recipe_menu.cli import main
from recipe_menu.text import Message


def run_echo(context: Context, arguments: Arguments) -> int:
    context.out.write(context.input.readline().upper())
    return 0


ECHO = Command(("echo",), Message("Repeat a line.", "重复一行。"), run_echo)
out = io.StringIO()
code = main(
    ["echo", "--data", str(folder.root)],
    environ={},
    home=home,
    today=date(2026, 11, 10),
    stdout=out,
    stderr=io.StringIO(),
    commands=[ECHO],
    stdin=io.StringIO("salt to taste\n"),
)
assert (code, out.getvalue()) == (0, "SALT TO TASTE\n")
```

### 3.3 `use_utf8_input`

- Module: text
- Purpose: Makes a console input stream read UTF-8, so `add` reads a pipe of Chinese answers whatever the code page is (ADR-0004, choice 4). At start, `cli` calls it on `sys.stdin`, as it calls `use_utf8` on `sys.stdout` and `sys.stderr` (F02 design 2.10).

Signature:

```python
def use_utf8_input(stream: TextIO) -> None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `stream` | `TextIO` | An input stream, such as `sys.stdin`. | Open, and nothing has been read from it yet. |

- Return value: None

Errors: None

- Side effects:
  - When `stream` is an `io.TextIOWrapper`, as `sys.stdin` is, `use_utf8_input` calls its `reconfigure` with `encoding="utf-8-sig"` and `errors="replace"`. From then on, the stream decodes UTF-8, drops a byte order mark at the start, and turns each byte that is not UTF-8 into U+FFFD REPLACEMENT CHARACTER, so a read never raises for the bytes. Its line ends stay universal, so CR LF and LF both end a line.
  - Any other stream, such as the `io.StringIO` of a test, stays as it is.
  - On a Windows console, Python reads through the console's Unicode interface and gives UTF-8 bytes, so the code page does not matter there. A pipe or a redirected file is read as UTF-8 after this call.
- Performance target: None

Example:

```python
import io

from recipe_menu.text import use_utf8_input

data = b"\xef\xbb\xbf" + "蒜蓉西兰花\r\n".encode() + b"\xffx\n"
stream = io.TextIOWrapper(io.BytesIO(data), encoding="cp1252")
use_utf8_input(stream)
assert (stream.encoding, stream.errors) == ("utf-8-sig", "replace")
assert stream.readline() == "蒜蓉西兰花\n"
assert stream.readline() == "\ufffdx\n"
answers = io.StringIO("西兰花 300 g\n")
use_utf8_input(answers)  # changes nothing
assert answers.readline() == "西兰花 300 g\n"
```

### 3.4 `check_recipe`

- Module: check
- Purpose: Checks one recipe as `check` checks it: with the catalog that `read_catalog` gives, through `read_recipe` (F07 design 2.2, steps 2 and 5). `add` checks the file that it saved with it (choice 12), and F16's `edit` can check the recipe that you edited.

Signature:

```python
def check_recipe(folder: DataFolder, recipe_id: str) -> tuple[Problem, ...]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `recipe_id` | `str` | The ID of the recipe, such as `garlic-broccoli`. | `is_recipe_id(recipe_id)` is true (F04 design 2.4). |

- Return value: The problems of the recipe, in this order: the errors of `read_catalog(folder)` (F03 design 2.8), then the problems of `read_recipe(folder, catalog, recipe_id)` with the catalog that `read_catalog` gave, or `None` when it gave none (F04 design 2.6). A catalog with an error keeps `read_recipe` from finding the ingredients and the tags, so the check names that error and does not report a clean recipe. The empty tuple means that the recipe has no problem.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `is_recipe_id(recipe_id)` is false. `check_recipe` checks this before it reads any file. |

- Side effects: Reads `catalog.toml` and `recipes/<id>.toml` once each through `read_catalog` and `read_recipe`. It lists no folder and writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`.

```python
from pathlib import Path

from recipe_menu.commands.check import check_recipe
from recipe_menu.lang import BiText, Lang

assert check_recipe(folder, "tomato-egg") == ()
problems = check_recipe(folder, "red-braised-pork")
assert [problem.place for problem in problems] == [BiText("steps", "步骤")]
mapo = folder.recipe_file("mapo-tofu")
mapo.write_text(mapo.read_text(encoding="utf-8").replace("郫县", ""), encoding="utf-8")
problems = check_recipe(folder, "mapo-tofu")
assert [problem.file for problem in problems] == [Path("recipes", "mapo-tofu.toml")]
assert problems[0].text(Lang.ZH) == "未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。"
folder.catalog.write_text("categories = [\n", encoding="utf-8")
problems = check_recipe(folder, "tomato-egg")
assert [problem.file for problem in problems] == [Path("catalog.toml")]

check_recipe(folder, "Tomato-Egg")  # raises ValueError
```

### 3.5 `problem_block`

- Module: check
- Purpose: The lines that show problems with the indents of the report of `check`: the file and the place after two spaces, and the message after four (F07 design 2.2). The report of `check` writes its blocks with it, `add` writes the problems of its check with it (choice 12), and F16's `edit` can write the lines of its prototype with it.

Signature:

```python
def problem_block(problems: Iterable[Problem], lang: Lang) -> tuple[str, ...]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `problems` | An iterable of `Problem` values | The problems to show, in their order. | Any number, none included. |
| `lang` | `Lang` | The language of the lines. | None |

- Return value: Two lines for each problem, in the order of `problems`, with no line break: two spaces and `where`, then four spaces and `what`, from `problem_lines(problem, lang)` (F05 design 2.8). No problems give the empty tuple.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.commands.check import problem_block
from recipe_menu.datafile import Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
MISSING = Message("The file is missing.", "文件不存在。")
mapo = Path("recipes", "mapo-tofu.toml")
problem = Problem.error(mapo, BiText("ingredient 3", "食材 3"), UNKNOWN, name="豆瓣酱")
missing = Problem.error(Path("catalog.toml"), None, MISSING)
assert problem_block([problem, missing], Lang.ZH) == (
    f"  {mapo}，食材 3",
    "    未知食材“豆瓣酱”。",
    "  catalog.toml",
    "    文件不存在。",
)
assert problem_block([], Lang.EN) == ()
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `add` is the command module that architecture 3 gives F15, in `src/recipe_menu/commands/add/`, and it exports only `ADD_COMMAND`. It imports only `app`, `lang`, `units`, `text`, `datafile`, `catalog`, `recipes`, and `check`. All of them are in its row, and `add --> check` is an arrow of architecture 4. It reads the default servings from `context.settings`, so it needs neither `settings`, `menus`, nor `shopping`. Point 4 of the brief: section 3 adds what architecture 3 and 5.2 plan for F15. `Context` gets the input stream, which only `cli` fills (architecture 8). `text`, which owns the console streams, gets `use_utf8_input`. `check` gets `check_recipe` and `problem_block`, because architecture 3 says that `add` and `edit` reuse `check`, and F07 design section 2 left these names to F15. The two names live in a new internal file of `check` and go into its `__all__`, so every new file belongs to one module. `Context` stays a frozen dataclass with `slots=True`, and `input` is a `TextIO` with a default, like `out` and `err`, so the value rules of architecture 8 hold. The file that `add` writes is the `recipes/<id>.toml` of architecture 5.1, in the layout of `recipes/choy-sum.toml`, in UTF-8 with no byte order mark and with LF line ends. It goes through `create_file`, the write that architecture 6 gives a new file. Its text comes from a template with an escape for TOML basic strings, as architecture 2 allows, so no TOML writer is needed. `use_utf8_input` sets `utf-8-sig`, the encoding that architecture 8 gives for reading. Point 2 of the brief: `add` may call `context.input.isatty()`. It is a call on the stream that `cli` passed, as `readline()` is, so `add` reads no console itself (architecture 8). A test controls both branches: `io.StringIO` gives false, and a stream whose `isatty` gives true takes the other branch. Point 5 of the brief, speed: in the model, `cli` imports no new standard module. The four new files, three of `add` and one of `check`, take 0.7 to 0.9 ms of self time each under `python -X importtime`, about 3 ms in all, and reconfiguring stdin takes 14 µs. The start of `import recipe_menu.cli` in a new process showed no difference beyond noise: a minimum of 163 to 170 ms for the model and 165 to 172 ms for an unchanged copy, in 3 rounds of 21 runs in the same folder. Note 1, not blocking: choice 14's "about 1 ms" is low. The seven files that section 2 plans for `add` may take a few milliseconds, still far below the 172 ms that `check` has left. Choice 14 can say "a few milliseconds". |
| Follows the error handling and naming conventions | Pass | The first error of `read_catalog` or `list_recipe_ids` stops `add` through `first_error` and `stop_at_error`, before any question, as `list` and `menu suggest` stop. A wrong answer is not an error in the data: it gets one message on the output stream and the question again. `INPUT_ENDED`, `APPEARED`, and the three lines of a failed save end `add` with 1 on the error stream. The lines after saving go to the output stream with either exit code, because they are the report of a check. Architecture 6 says so for `check`, and the rule "The report of `add` and `edit`" of the v0.2 test plan reads it the same way. The first line of a failed save names the file as its problem holds it, relative to the data folder, and `SAVED`, `APPEARED`, and `LEFT_BEHIND` name a file by its full path, as architecture 6 gives both rules. So F15 needs no change to architecture 6 and no ADR, unlike `init` (ADR-0009) and `menu new` (ADR-0010), and it names a failed save as `menu suggest` does (ADR-0011). Ctrl+C goes on to `cli` as `KeyboardInterrupt`, which gives 130, and `create_file` removes a file that it was writing, so no file is left half written (architecture 6). Exit code 1 after an early end of the input fits architecture 1, because the command did not work, and a script sees it. `run` catches no exception, so the rule on `except` clauses holds. The names follow architecture 8. The module `add` has its command's name. The 32 messages are UPPER_SNAKE `Message` and `Plural` constants in `add/messages.py`, counts use `Plural`, and lists use `and_list`. `input`, `stdin`, and `use_utf8_input` match `out`, `stdout`, and `use_utf8`. ruff 0.17.4 with the project's settings reports nothing about the field `input` of the model's `Context`. Point 1 of the brief: ADR-0004 needs no new sentence. Its decision on the console says that `cli` asks `text` to set stdout and stderr to UTF-8, and it says nothing about the input. `use_utf8_input` applies the same decision to the one stream that only `add` reads, and choice 4 and 3.3 record the reason and the case of Windows PowerShell 5.1. The architecture does not change, so Troy has no further point to decide. |
| Does not duplicate an existing interface | Pass | `add` checks the ID with `is_recipe_id` and the listing of `list_recipe_ids`, the tags with `Catalog.find_tag`, each ingredient with `Catalog.find_ingredient` and `parse_quantity`, and the servings with `MIN_SERVINGS` and `MAX_SERVINGS`, as the F03, F04, and F05 designs planned. It writes through `create_file` and stops through `stop_at_error`. It builds none of them again. `read_servings` takes a TOML value and a `Report`, not a typed answer, so `add` checks the answer itself, with the shared range. `problem_block` takes the two indented lines out of the report of `check`, which then writes its blocks with it, so the indents live in one place. `check_recipe` is new: no interface checks one recipe. The TOML escape is new too, because no other module writes text that you typed into a TOML file. If a later feature needs it, it can move to `datafile`. The copies of `SERVINGS_WRONG`, `UNKNOWN_TAG`, `NO_TAGS`, and the four amount messages are internal messages, which architecture 8 keeps in each module, as the F13 and F14 reviews accepted. Note 2, not blocking: `add` makes the third copy of `UNKNOWN_TAG` and `NO_TAGS`, after `browse` and `suggest`, and the sixth copy of the read of the catalog that stops at the first error. The later `[refactor]` PR that the F13 and F14 reviews named can share them. |
| Depends only on features earlier in the order | Pass | F15 uses F01's `parse_quantity` and `WrongQuantity`, F02's `text`, F03's `datafile` and `catalog`, F04's `recipes`, F05's `app`, `cli`, and servings range, F07's `check`, F11's `create_file`, `FileOutcome`, and `FileCreation`, and F14's form of `Context` and `main`. It copies texts of F04, F05, and F09. Each of these features comes before F15 and is accepted on main, and so is F05, the hard dependency. F03, F04, and F07 are the soft dependencies of the F15 row. F01, F02, F11, and F14 reach F15 through the shared modules `units`, `text`, `datafile`, `app`, and `cli`, which point to earlier features, as architecture 4 allows. `ID_EXISTS` names F16's `recipe-menu edit` only as text, as the F15 prototype that Troy approved shows it, so it adds no dependency on F16. Until F16 is accepted, that command gives `Unknown command "edit".`, and v0.2 ships both. The plans for F16 bind no later design. F15 needs only the standard library, so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption between modules. The file must read back through `read_recipe` as you typed it, and the model confirms it. Texts with `"`, `\`, a tab, U+007F, U+3000, and U+2028 come back exactly through `tomllib`. A run of `add` with quotation marks, a backslash, and a tab in its answers gives a file that `read_recipe` reads with the same texts and only the expected warning. `add` checks each ingredient line with the same `find_ingredient` and `parse_quantity` as `read_recipe`, so a kept line never gives a problem after saving, `Salt TO taste` included. Choice 2 is right: `list_toml_files` counts every kind of entry, so a listing with no error holds every name that `create_file` would refuse, also on Windows. `create_file` lists `recipes/` again, so an entry that appears while you answer gives `EXISTS` and `APPEARED`. A folder that appears between that listing and the open gives `FAILED` with access denied on Windows, as the code review of PR #76 found, and the failure lines then say that nothing was saved, which is right. The echo depends only on `context.input.isatty()`. `cli` calls `use_utf8_input` only when `main` got no `stdin`, and pytest's `sys.stdin` is not an `io.TextIOWrapper`, so the tests change no stream. The Architect checked both. Through a pipe with `PYTHONIOENCODING=ascii`, `python -m recipe_menu add --lang zh` on the model read UTF-8 answers with a byte order mark and CR LF line ends as typed, and turned a byte that is not UTF-8 into U+FFFD. Note 3, not blocking: the constraint of 3.4 says only that `is_recipe_id(recipe_id)` is true. `read_recipe` also needs an ID that `list_recipe_ids` gave, because on Windows it opens `Tomato-Egg.toml` for `tomato-egg`. `add` meets that need, because `create_file` has just created the file with exactly that name and refused every other case of it. 3.4 can add that the ID is one that `list_recipe_ids` gave, or the ID of a file that the caller has just created with `create_file`, so that F16 and later callers keep to it. |
| Changes an implemented interface only through the change flow | Pass | The PR adds only the two design files. Section 3 adds only what architecture 3 and 5.2, F05 design section 2, F07 design section 2, and F14 design section 2 plan for F15: a field with a default in `Context`, an optional keyword parameter of `main`, and the new names `use_utf8_input`, `check_recipe`, and `problem_block`. No call of an exported name of F01 to F14 breaks. Architecture 4 says that the entry in `COMMANDS` is the only change that a command feature makes in `cli`. The parameter `stdin` is the `cli` side of the input stream that architecture 5.2 plans, as F14's `random` was, so it needs no change to the architecture. The requirements already name `add`, so no requirement changes, and the Architect reviews the additions here, as it reviewed F14's. Point 3 of the brief: with the model of section 3 and `ADD_COMMAND` after `SEARCH_COMMAND`, the whole suite gave 614 passed, 1 failed, and 4 skipped on Windows, with F07-T25 and F10-T21 left out. The one failure is F11-T01, which section 3 names, and the 4 skips are main's cases for Linux only. The other tests that the brief lists pass: F07-T17, F08-T14, F09-T01, F10-T01, F11-T27, F11-T35, F14-T01, F14-T21, and F14-T31, and the six tests that PR #105 changed, F05-T10, F05-T11, F11-T32, F13-T01, F13-T22, and F13-T27. F07's tests of the report pass with the report written through `problem_block`. The model's help has the 23 lines of 2.1, with the second column after 24 columns in both languages. F07-T25 and F10-T21 time `check` and `search` on a PT01 folder. They failed on an unchanged copy too in the review's sandbox, with medians of 1.08 s and 1.09 s, so this sandbox cannot time PT01. The release test of v0.2 runs PT01 on Troy's PC. So the plan of section 2 holds: a test-fix PR before the mock changes F11-T01, and the mock's 10 files and the implementation's about 650 lines need the soft-limit reasons that section 2 gives, as F14's did. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary at the top of PR #113, at commit 4d9b1e2, is the one in the brief, and it says what the design says. "What changes for you" gives the eight questions in the order of choice 3, the default servings, the tags in either language, the ingredient line as a name, a space, and a quantity, and the empty line that ends a list. It gives the message and the question again after a wrong answer, the wrong ingredient line that is dropped, and the empty first answer that saves nothing (choices 3 to 9). It says that the file has the layout of the other recipe files, holds the answers as typed and no notes, and never replaces a file, and that `add` then checks it (choices 10 to 12). Items 1 to 3 are points A, B, and C, each with its options and a recommendation with its reason. The counts of point A hold: 2.2 has 32 messages, 7 of them copies, 1 whole from the prototype (`ID_PROMPT`), and 24 others. The three risks are those of choices 4 and 11. The Architect found no other point for Troy to decide. Notes 1 to 4 need no decision from Troy, and the answers to points 1 and 2 of the brief change no architecture. The checks of troy-check's `summary.py`, run on the description, all pass. The Chinese part has 850 characters and the English part 1,961, within R22's 2,000. Both have the three parts in order and a recommendation in each of their 3 items, and neither holds an internal ID. Note 4, not blocking: "or the warnings" ("或者发现的警告") leaves out the error that choice 12 allows when the catalog changed while `add` waited. The file then stays saved, and `add` gives 1. "or the problems it found" ("或者发现的问题") covers it. The English part has 39 characters left. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 15 choices, section 3, and points A to C against the requirements, the architecture, ADR-0004 and ADR-0009 to ADR-0011, the designs of F03, F04, F05, F07, F11, and F14, the F15 prototype, the v0.2 test plan, and the six points of the brief. The two files have the same 13 headings and 158 table lines, and 17 code blocks, each equal to its mirror, with no control or invisible character. The 13 `python` blocks parse. With Python 3.13.18 on Windows, the Architect built a model of sections 2 and 3 in a copy of main's `src/` and ran the 7 examples on fresh copies of `tests/data/example/`. All 48 assertions and the one `# raises` hold. The model's help equals both help blocks of 2.1 line for line. Items 1, 5, and 6 give the runs through a pipe, the round trips, the start time, and the whole suite. The Linux results, the Windows console (typing with an input method, Backspace, `chcp 437`, and Ctrl+C at a prompt), and PT01 were not run. Notes 1 to 4 do not block. | Approved. The main session puts points A to C to Troy when Troy approves this design (R18). No point changes the architecture, so no `[docs]` PR of the Architect follows. The Interface Designer can take notes 1, 3, and 4 in a revision, or leave them. Note 2 waits for the later `[refactor]` PR. For the Test Manager's brief (point 6 of the brief): the design settles the F15 points of "Where the plan waits for the designs" in the v0.2 test plan. The model confirms the English lines of v0.2-S10, exit code 0 in v0.2-S11, the split of `Cooking oil 2 tbsp` and `Salt to taste`, and the pipe read as UTF-8. The Test Manager updates the help of v0.2-S14, the rule "Answers to `add`", and step 2 of v0.2-S15, as the design says. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-19 | First draft. |
| 1.0 | 2026-11-20 | Approved by Troy. |
