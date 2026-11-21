---
troy-doc: "F16-design"
lang: "en"
version: "1.0"
updated: "2026-11-21"
status: "Approved by Troy on 2026-11-21"
mirror: "design.zh-CN.md"
---

# F16 Edit a recipe: interface design

## 1. Feature

- ID and name: F16 Edit a recipe
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F07

## 2. Interfaces

F16 builds the command module `edit` in `src/recipe_menu/commands/edit/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.edit` exports one name, `EDIT_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu edit ID` (2.2). Its messages live in `src/recipe_menu/commands/edit/messages.py` and are internal to the module (architecture 8). The other files behind it are the Developer's choice. In its mock PR, F16 adds `EDIT_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, after `ADD_COMMAND` (choice 1). That entry is the only change that a command feature makes to the list of commands (architecture 4, F05 design 2.9). F16 also adds the setting `editor` to `settings`, as architecture 5.1 plans: the field `Settings.editor` (3.1) and the key `editor` of `read_settings` (3.2). It changes no other implemented interface. `edit` uses F15's `Context.input`, `check_recipe`, and `problem_block`, and F14's `read_file_text`, as their designs give them, and it adds no field to `Context` and no parameter to `main` (choice 10). The F16 prototype `docs/prototypes/F16-edit.md` shows the command. The plans of F07 and F15 for F16 hold: `edit` checks the recipe with `check_recipe`, and writes its problems with `problem_block`, whose indents are those of the prototype (F07 design section 2, F15 design section 2).

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F16 gives |
| --- | --- |
| `recipe-menu edit ID` opens the recipe's file in the editor that the settings name, Notepad by default ([requirements 4](../../requirements.md#4-features)). | `recipe-menu edit` (2.2), with `EDIT_COMMAND` (2.1). The setting `editor` names the program and its options, and it is `notepad` when the settings name none (choice 3, 3.1, 3.2). `edit` finds the program and starts it with the full path of `recipes/<id>.toml` as its last argument (choice 4). |
| It waits until you close the editor. | `edit` waits until the program that it started ends (choice 5). When that program ends at once and the recipe has not changed, as Notepad does when it opens the file in a window that is already open, `edit` waits for Enter (choice 6, point D). |
| Then it checks that recipe. | A second listing of `recipes/`, then `check_recipe`, and the report of the prototype: an empty line, the count line, the blocks of `problem_block`, and a closing line after an error (choice 7). |
| `add` and `edit` reuse `check` to check one recipe ([architecture 3](../../architecture.md#3-modules)). | `check_recipe` and `problem_block` of F15 (F15 design 3.4 and 3.5). |
| In v0.2, F16 adds the editor to `settings.toml` ([architecture 5.1](../../architecture.md#51-data-files)). | `Settings.editor` and the key `editor` (3.1 and 3.2). |

These rules hold for every interface below:

- `edit` imports only `app`, `lang`, `text`, `datafile`, `recipes`, and `check` from the package. Its row of architecture 3 allows them, and `edit --> check` is an arrow of architecture 4. It needs neither `units`, `catalog`, `settings`, `menus`, nor `shopping`: it reads the editor as `context.settings.editor` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `edit` reaches the data folder only through `list_recipe_ids`, `read_file_text`, and `check_recipe`, all of which work through `datafile` (architecture 8). It writes no file: the editor changes the recipe, and `edit` only reads it. It writes only to `context.out` and `context.err`, and reads `context.input` only at the prompt of choice 6. It starts one program, the editor, with `subprocess.Popen`, and finds it with `shutil.which` (choice 4). Point C asks for the rule of the architecture that allows it. It keeps no state.
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). `edit` stops at the first error of a listing with `first_error` and `stop_at_error` (F05 design 2.8). An editor that cannot be found, cannot start, or ends with an error is not an error in the data: `edit` writes one line to the error stream and gives 1. `run` raises `UsageError` only for an ID that breaks the rule of `is_recipe_id`, before it reads a file (choice 2). `KeyboardInterrupt` from Ctrl+C goes on to `cli`, which gives 130 (choice 5). `edit` catches only the `OSError` of `Popen` and the `subprocess.TimeoutExpired` of its steps of waiting. Any other exception that reaches `cli` is a bug.
- `EDIT_COMMAND` is a frozen `Command` value (F05 design 2.5). F16 adds no value type. `Settings.editor` is a tuple of `str` (3.1).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F16 interface has a performance target. PT01 does not time `edit` ([requirements 7.1](../../requirements.md#71-performance-targets)). Choice 12 says what F16 adds to the start of every other command. `run` calls single-purpose internal functions (R04).

The design makes these choices. 2.2 and section 3 give their rules.

1. **One command, right after `add` in the help.** F16 adds `EDIT_COMMAND` to `COMMANDS` after `ADD_COMMAND`, as F15 design section 2 planned. So `COMMANDS` becomes `(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND, ADD_COMMAND, EDIT_COMMAND, MENU_NEW_COMMAND, MENU_SHOW_COMMAND, MENU_SUGGEST_COMMAND, SHOP_COMMAND)`. The commands that work on recipes stand together: `list`, `show`, `search`, `add`, and `edit`. `edit` has `FolderUse.READ`, so `cli` stops it when the data folder is missing or the settings have an error (F05 design 2.5), as v0.2-S14 step 6 expects. It declares the required argument `ID`, named `ID` in both languages as for `show`, and no option. So its usage is `edit ID` in both languages, 7 columns wide. `menu suggest [WEEK]`, of 19 columns, stays the widest first cell, so the second column of both tables still starts after 24 columns in both languages. The line of `edit` moves the lines below it down by one, and no other line of the help changes. The help has 24 lines (2.1). No test of an accepted feature depends on the line that follows `add` (section 3).
2. **The ID, and what `edit` reads before it starts the editor.**
   - `edit` checks `ID` with `is_recipe_id` before it reads a file (F04 design 2.4). A value that breaks the rule, such as `Mapo`, `../rice`, `""`, or `con`, gives `UsageError(NOT_A_RECIPE_ID, None, id=value)`, and `cli` exits with 2, as for `show` (F09 design, choice 7). The message says what to run, so it names no hint (ADR-0008).
   - Then `edit` lists `recipes/` with `list_recipe_ids`. The first error of the listing stops `edit` with `stop_at_error`, as it stops `show` and `add` (F09 design, choice 2). So an entry such as `recipes\Rice Bowl.toml` stops `edit` too. When the listing lacks the ID, `edit` writes `UNKNOWN_ID` to the error stream and gives 1. That is the line of the prototype "An unknown ID", which is the line of `show` for an unknown ID (F09 design 2.4). `edit` compares the ID exactly with the IDs of the listing, so Windows and Linux give the same result. So `edit` never opens `Tomato-Egg.toml` for `tomato-egg`, which `read_recipe` would do on Windows (F15 design 3.4).
   - `edit` keeps its own copies of `NOT_A_RECIPE_ID` and `UNKNOWN_ID`, with the texts of `show`, because architecture 3 does not let `edit` import `browse`, which keeps them internal (choice 13).
   - Before the editor starts, `edit` reads only the listing and the text of the recipe's file, the latter with `read_file_text` for choice 6. It reads neither the catalog, the pantry, a menu, nor another recipe. `cli` has read the settings (F05 design 2.10), and `edit` takes the editor from `context.settings`. The catalog is read once, after the editor, by `check_recipe`. You may change the catalog while the editor is open, and an error in it should not keep you from opening the recipe. So a catalog with an error stops nothing before the editor, and the check after it names the error (choice 7).
3. **The setting `editor`** (3.1 and 3.2).
   - `settings.toml` may hold the key `editor`, a text that names a program and its options, such as `editor = "code --wait"`. Without the key, the editor is `notepad`, on every system. So `Settings.editor` is `("notepad",)` by default, and a file with `editor = "notepad"` gives the same settings.
   - The text splits into words by one rule, the same on Windows and on Linux. Whitespace outside double quotation marks separates words. A double quotation mark starts or ends a quoted part and is not part of the word, so a path with spaces goes in double quotation marks. A word may join quoted and plain parts, such as `--file="a b"`, and `""` alone is an empty word. Every other character stands for itself, `\` and `'` included, so a Windows path needs no escape inside the value. No character escapes a double quotation mark, so a word cannot hold one, and no path on Windows can. Whitespace is what `str.isspace` names, as `str.strip` removes it. The first word is the program, and the other words are its options.

     | The line in `settings.toml` | `Settings.editor` |
     | --- | --- |
     | No key `editor` | `("notepad",)` |
     | `editor = "notepad"` | `("notepad",)` |
     | `editor = "code --wait"` | `("code", "--wait")` |
     | `editor = "  code   --wait  "` | `("code", "--wait")` |
     | `editor = '"C:\Program Files\Notepad++\notepad++.exe" -multiInst -nosession'` | `("C:\Program Files\Notepad++\notepad++.exe", "-multiInst", "-nosession")` |
     | `editor = 'code --file="a b"'` | `("code", "--file=a b")` |
     | `editor = 'code ""'` | `("code", "")` |

   - TOML reads `\` in a text in double quotation marks as an escape, so `editor = "C:\Program Files\..."` is a syntax mistake, which `read_toml` reports with its line (F03 design 2.3). That message already says to put the text in single quotation marks. In single quotation marks, a TOML text keeps every `\`, as the fifth row of the table shows.
   - A wrong value is an error at the place `editor`, as for the other keys. A value that is not a text gives `NOT_A_TEXT`, and a text that is empty or holds only whitespace gives `EMPTY_TEXT`, both of `datafile` (F03 design 2.10), as `read_text` gives them (F04 design 3.2). A text that ends inside a quoted part, whose first word is empty, such as `'"" --wait'`, or one of whose words holds U+0000 gives `EDITOR_NOT_A_COMMAND`. The last case keeps `subprocess` from raising `ValueError` for a null character.
   - An error in the settings stops every command but `check` and `init` (F05 design 2.5). So a wrong `editor` stops `list` and `show` too, as a wrong `dishes` does (F14 design 3.2), and `check` reports it.
   - The keys of the top of the file are `language`, `meals`, `servings`, `dishes`, and `editor`, in this order, so `UNKNOWN_KEY` names the five keys.
   - `init` writes its settings file without the key, as it writes it without `dishes` (F14 design, choice 5). So F16 changes no file that `init` writes, and v0.1-S01, v0.1-S02, and v0.1-S13 hold, as the v0.2 test plan expects.
4. **How `edit` finds and starts the editor** (point C).
   - `program` is the first word of `context.settings.editor`, and the other words are its options. `edit` finds the program with `shutil.which(program)`. A program with a folder part, such as `C:\Tools\ed.exe` or `./ed`, is looked up at that path, and a relative path counts from the current folder. A program without one is looked up in the folders of the `PATH`. On Windows, `shutil.which` looks in the current folder first, as `cmd.exe` does, and tries each extension of `PATHEXT`, so `code` finds `code.cmd`, and `stand-in-editor` finds `stand-in-editor.cmd`. On Linux, it finds a file that you may run, a script with `#!` included. When it finds nothing, `edit` writes `EDITOR_NOT_FOUND` to the error stream and gives 1.
   - The default `notepad` finds `C:\Windows\System32\notepad.exe` on Windows. Linux has no `notepad`, so there `edit` without the key gives `EDITOR_NOT_FOUND`, whose message says how to name an editor. CI runs on Linux, and no test needs Notepad (choice 10).
   - `edit` starts the list `[found, *options, str(path)]` with `subprocess.Popen`, where `found` is what `shutil.which` gave, and `path` is `context.folder.recipe_file(recipe_id)`, the full path of the recipe's file. The file is always the last argument, and one argument, whatever spaces its folders hold. `Popen` gets no `shell`, no `env`, no `cwd`, and no streams. So the editor gets the environment, the current folder, and the console of `recipe-menu`, as when you type its name in PowerShell. An editor with a window of its own, such as Notepad or VS Code, does not use the console.
   - On Windows, `Popen` passes the command line to `CreateProcess`, which runs a `.cmd` or `.bat` file through `cmd.exe` by itself when it gets the file's full path. So `code.cmd` and the plan's `stand-in-editor.cmd` start without `shell=True`. `cmd.exe` reads the arguments of a batch file by its own rules and expands `%NAME%` in them, so a batch editor gets the path of a data folder that holds `%` changed. An `.exe` editor gets every argument as written.
   - When `Popen` raises `OSError`, such as for access denied or a file that Windows cannot run, `edit` writes `EDITOR_NOT_STARTED` to the error stream with the system's reason, as `datafile` gives it (`error.strerror`, else the name of the exception's type), and gives 1.
   - Once the editor has started, `edit` writes the first line and calls `context.out.flush()`, so the line shows while the editor is open. The line is `OPENED_IN_NOTEPAD`, the line of the prototype, when `context.settings.editor` is `("notepad",)`, and otherwise `OPENED_IN_EDITOR` with the program as the settings write it, such as `Opened recipes\mapo-tofu.toml in "code". Close the editor when you are done.`. `edit` writes it after the start, so it never says that it opened a file that it could not open. An editor that runs in the console may draw over the line.
   - `edit` imports `subprocess` and `shutil` inside the internal function that starts the editor (choice 12), and calls them as `subprocess.Popen` and `shutil.which`, so a test can replace either through pytest's `monkeypatch` (choice 10). ruff flags the call of `Popen` (`S603`) and an import inside a function (`PLC0415`), so each of those lines carries a `noqa` comment with its reason, as the code does for `S311`.
5. **Waiting for the editor, and Ctrl+C.**
   - `edit` waits until the program that it started ends. It waits with `Popen.wait(timeout=0.5)` in a loop, which returns as soon as the program ends. On Windows, Python's wait for a process does not wake for Ctrl+C, and a wait in steps of half a second lets Ctrl+C through on both systems.
   - Ctrl+C while `edit` waits raises `KeyboardInterrupt`, which `edit` does not catch. `cli` gives 130 and writes nothing more (architecture 6, F05 design 2.10). `edit` does not stop the editor: `Popen.wait` gives the editor a quarter of a second to end, as Python does after Ctrl+C, and then leaves it running. So the editor stays open with what you typed, what you saved stays saved, and no check runs. A batch editor in the console, such as `code.cmd`, gets the Ctrl+C too, and `cmd.exe` may then ask whether to end the batch job.
   - When the program ends with an exit code other than 0, `edit` writes `EDITOR_FAILED` with the code to the error stream, checks nothing, and gives 1. Such a code means that the editor did not run as the settings meant, for example with a wrong option. Notepad and `code --wait` end with 0.
6. **An editor that ends at once** (point D). On Windows 11, Notepad can open a file as a tab of a window that is already open. The `notepad.exe` that `edit` started then hands the file over and ends at once, before you have changed anything. `code` without `--wait` does the same.
   - When the program ends with exit code 0 less than 2 seconds after `edit` started it, and `read_file_text` then gives the same result as before the start (choice 2), `edit` takes it for such a hand-over. It writes the prompt `QUICK_EXIT`, which ends with no line break, calls `context.out.flush()`, and reads one line from `context.input`, as `add` reads an answer (F15 design, choice 4). When `context.input.isatty()` is false, `edit` then writes the line that it read, without the LF at its end, and a line break, or only a line break at the end of the input. Whatever the line holds, and also at the end of the input, `edit` goes on to the check.
   - So you see the first line and then the prompt. You save the recipe in Notepad, close its tab if you like, and press Enter. Then `edit` checks the recipe.
   - An editor that changed the file, such as the stand-in of v0.2-S12, or that ends 2 seconds or more after its start, takes the plain way, and `edit` checks at once. You close Notepad within 2 seconds of its start without a change only when you meant no change, and then one Enter goes on to the check.
   - `edit` measures the 2 seconds with `time.monotonic()`, from just before `Popen` to the end of the wait. It is a duration, not today's date, so architecture 8 does not give it to `cli`. A test reaches each side of the rule with a stand-in that ends at once with or without a change, or that waits 2 seconds or more.
   - Ctrl+C at the prompt gives 130, as at a question of `add`.
7. **The check after the editor.**
   - `edit` lists `recipes/` again with `list_recipe_ids`, because the editor or you may have deleted or renamed the file. The first error of this listing stops `edit` with `stop_at_error`, as before the editor. So on Windows, a file renamed to `Mapo-Tofu.toml` stops `edit` with the error of that name. When the listing no longer holds the ID, `edit` writes `GONE` to the error stream and gives 1. So `check_recipe` gets an ID of a listing made after the editor ended, as F15 design 3.4 requires.
   - Then `check_recipe(context.folder, recipe_id)` gives the problems: the errors of the catalog, then the problems of the recipe (F15 design 3.4). `edit` writes the report to the output stream with either exit code, because it is the report of a check, as the rule "The report of `add` and `edit`" of the v0.2 test plan says (architecture 6).
   - The report is an empty line, the count line, `problem_block` of the errors, then `problem_block` of the warnings (F15 design 3.5), and, with an error, the closing line. The count line is `CHECKED_CLEAN` with no problem, `CHECKED_WARNINGS` with warnings alone, and `CHECKED_PROBLEMS` with an error. The closing line is `EDIT_AGAIN` when every error is in the recipe's file, as in the prototype. It is `FIX_AND_CHECK` when an error is in another file, such as a catalog that cannot be read, because a change to the recipe does not fix that.
   - `edit` gives 1 when a problem is an error, and 0 otherwise, because a warning never changes the exit code (architecture 6).
   - `edit` itself never writes the recipe or any other file. Only the editor changes the file, so v0.2-S15 and v0.2-S16 see only the editor's change.
8. **How the lines name the file** (point B). The first line names the recipe's file relative to the data folder, `str(context.folder.relative(path))`, such as `recipes\mapo-tofu.toml` on Windows and `recipes/mapo-tofu.toml` on Linux, as the prototype writes it. The lines of the report and of `stop_at_error` are problems, which name their files the same way (architecture 6). No other line of `edit` names a file: `UNKNOWN_ID`, `GONE`, `EDIT_AGAIN`, and the count lines name the ID, and the lines about the editor name the program as the settings write it. Architecture 6 names the file of a message that is not a problem by its full path, and ADR-0009 asks every other case for its own change to architecture 6. So the first line needs one, as the swap line of `menu suggest` did (ADR-0011). The editor gets the full path in either case.
9. **Starting a program, and the architecture** (point C). Architecture 4 says that only `cli` touches the outside world, and architecture 8 lists what only `cli` reads, the environment variables among them. Neither names starting another program. `edit` starts the editor. `shutil.which` reads `PATH`, and on Windows `PATHEXT`, from the environment of the process, and the editor gets that environment, the current folder, and the console. The requirement asks for this program. Under option 1 of point C, architecture 8 gains one rule: `edit` starts the editor that the settings name and waits for it, and no other module starts a program. The Architect records the rule in architecture 4 and 8 and in an ADR, in a `[docs]` PR before the F16 mock PR. The rule "No network" stays true: the tool never uses the network, and the editor is a program of your own choice, such as VS Code, which may.
10. **Tests, and the editor on CI.** No test starts Notepad, VS Code, or any other real editor, and no test needs a console.
    - A test names a stand-in editor in `settings.toml` by full paths: the test's Python, `sys.executable`, and a script that changes the file as the test asks and ends. It opens no window and reads no console, so it runs on CI, where no console exists. It gets the streams that pytest captures.
    - A test of the default, with no key `editor`, sets `PATH` through `monkeypatch`: to an empty folder, for `EDITOR_NOT_FOUND`, or to a folder that holds a stand-in named `notepad`, which is `notepad.cmd` on Windows and an executable script on Linux. It also changes to a temporary current folder through `monkeypatch.chdir`, because `shutil.which` looks there first on Windows.
    - A test that needs `Popen` to raise `OSError`, or a wait to raise `KeyboardInterrupt`, replaces `subprocess.Popen` through `monkeypatch` (choice 4).
    - So `edit` needs no new field of `Context` and no new parameter of `main`. F15-T03, which compares the names of the fields of `Context` exactly, holds. The version tests put `stand-in-editor.cmd` on the `PATH` of the process, as the v0.2 test plan's rule "The stand-in editor" says.
11. **Numbers in messages.** The messages of `edit` show the ID, which follows `is_recipe_id`, counts of problems, and the exit code of the editor. An exit code is a number that the system gives: at most 10 digits on Windows, and a small negative number for a signal on Linux. A problem in a file reaches the output only through `stop_at_error` and `problem_block`, and the readers limit a number from a file to 15 digits or show the file's text (F04 design, choice 2). So no message of `edit` meets F02's limit of 4,300 digits (F02 design 2.3).
12. **Speed.** No performance target names `edit`. On a PT01 data folder it lists 1,000 entries twice, and reads the catalog of 300 ingredients and one recipe, so its own reading takes about as long as `show`, 0.164 s in the release test of v0.1.0 (v0.2 test plan, section 3). The rest is your time in the editor. v0.2-S16 runs `edit` on a PT01 folder without timing it. The start of every other command changes little. `cli` imports the few small files of `edit` at start, a few milliseconds, as for F15 (F15 design, choice 14). `read_settings` reads one more key. `edit` imports `subprocess` and `shutil`, with the modules that they import, such as `threading`, only inside the function that starts the editor (choice 4), so no other command loads them. `time` is built into Python. `check` takes about 0.86 s under PT01 on Troy's PC after F15, so it keeps about 140 ms. These times were not measured for F16, and the PT01 cases of v0.1 run again in v0.2's release test.
13. **Only the command is exported.** `edit` exports `EDIT_COMMAND` and nothing else. Only `cli` may import `edit` (architecture 3), so no other name would have a user. `edit` keeps its own copies, with the same texts, of `ID_ARGUMENT`, `NOT_A_RECIPE_ID`, and `UNKNOWN_ID` of `browse`, and of `ERROR_COUNT`, `WARNING_COUNT`, and `FIX_AND_CHECK` of `add`, because those modules keep them internal (architecture 8). A later `[refactor]` PR can share them.

The v0.2 scenarios that run `edit` hold with these choices:

- v0.2-S12: step 1 starts `stand-in-editor.cmd` once with the full path of `recipes\mapo-tofu.toml` as its last argument (choice 4). Its first line is `Opened recipes\mapo-tofu.toml in "stand-in-editor". Close the editor when you are done.`. The stand-in changes the file, so `edit` checks the recipe when the stand-in ends (choice 6) and prints the lines of the prototype that follow its first line, with exit code 1. Step 2 prints `已用“stand-in-editor”打开 recipes\mapo-tofu.toml。改完后关闭编辑器。`, an empty line, and `已检查 mapo-tofu：没有错误。`, with exit code 0. Step 3 prints the output of F07 "After the fixes".
- v0.2-S13: step 1 prints the line of the prototype "An unknown ID" with exit code 1, and step 2 prints `An argument is missing. Write "recipe-menu edit ID".` and `Run "recipe-menu --help" to see the commands.` on stderr with exit code 2 (F05 design 2.10). In both, the stand-in does not run (choice 2). In step 3, the error is in the recipe's file, so the closing line is `Run "recipe-menu edit tomato-egg" to fix it.`, and the exit code is 1.
- v0.2-S14: the help gets the line of `edit` right after the line of `add`, and the second column stays after 24 columns (2.1). Step 6 prints `NO_DATA_FOLDER` and `RUN_INIT` from `cli` and exits with 1, before `edit` lists anything (choice 1).
- v0.2-S15: step 3 changes no file and no folder. `edit` writes nothing, and it only reads the listing, the recipe, and the catalog. A stand-in that ends without a change within 2 seconds gets the prompt of choice 6, and `edit` goes on at the end of the input. So the Test Manager gives step 3 an empty standard input and expects the prompt, or makes the stand-in of that step wait 2 seconds or more.
- v0.2-S16: step 3 ends with `Checked recipe-1000: no errors.` when the recipe has no warning, and the rule of choice 6 holds as in v0.2-S15.
- v0.2-S19: in steps 1 and 2, no Notepad window is open, so the `notepad.exe` that `edit` started is the window, and `edit` waits until you close it. In step 3, when Notepad opens the recipe as a tab of your window, `edit` shows the prompt of choice 6 after its first line and checks the recipe after you press Enter. When Notepad opens a window of its own, `edit` waits until you close it, as in step 1. Either way, `edit` then prints an empty line and `Checked tomato-egg: no errors.`. So the Test Manager adds "then press Enter, if `edit` asks for it" to step 3, and both cases to its expected result.
- v0.1-S01, v0.1-S02, and v0.1-S13: F16 changes no file that `init` or `menu new` writes, and `init` writes no key `editor` (choice 3).

Troy decides these four points. The design follows the recommendation of each.

- **A. New texts.** The prototype gives the line for Notepad in both languages, the English count line with one error and the English closing line, and the Chinese count line with no error. The other texts follow the wording of the prototype or of an existing message. `edit` has 18 messages, listed in 2.2, and `settings` gains 2, listed in 3.2. Six of the 20 are copies of existing messages, and one, `OPENED_IN_NOTEPAD`, comes whole from the prototype. The recommendation is to accept the other 13 as 2.2 and 3.2 give them:
  - The line of the help: `Edit a recipe in your editor, then check it.` and `在编辑器里修改一个菜谱，然后检查它。`.
  - The first line with an editor of the settings: `Opened {file} in "{editor}". Close the editor when you are done.` and `已用“{editor}”打开 {file}。改完后关闭编辑器。`.
  - The count lines that the prototype does not show: `Checked {id}: no errors.`, `Checked {id}: no errors, 1 warning.`, `已检查 {id}：没有错误，有 1 个警告。`, and `已检查 {id}：有 1 个错误和 2 个警告。`. The Chinese closing line: `运行“recipe-menu edit {id}”改正它。`.
  - The prompt of an editor that ends at once (point D): `The editor closed at once, maybe because it opened the recipe in a window that was already open. When you have saved the recipe there, press Enter: `.
  - The lines of an editor that cannot be found, cannot start, or ends with an error, and of a recipe that is gone, such as `Cannot start the editor "code": no program of that name was found. Name your editor in settings.toml, such as editor = "code --wait".`.
  - The place `editor` and `编辑器`, and the problem of a value that does not split: `"editor" must name a program and then its options, such as editor = "code --wait". Put a path with spaces in double quotation marks, and close each one.`.
- **B. How the first line names the file** (choice 8).
  - Option 1, recommended: relative to the data folder, as the prototype writes it: `Opened recipes\mapo-tofu.toml in Notepad. Close Notepad when you are done.`. Architecture 6 gains one case for this line. The Architect records it in architecture 6 and an ADR, in a `[docs]` PR before the F16 mock PR, as ADR-0011 recorded point D of the F14 design.
  - Option 2: by its full path, such as `Opened C:\Users\Troy\recipe-menu\recipes\mapo-tofu.toml in Notepad. …`, as architecture 6 gives a message that is not a problem. The first lines of both sections of the F16 prototype change through the requirement change flow before the F16 test plan, and choice 8, 2.2, and the examples change before the mock PR.
  - The reason for option 1: it keeps the line of the prototype that Troy approved, and the line then names the file as the lines of the check below it do.
- **C. How `edit` starts the editor** (choices 4, 9, and 10).
  - Option 1, recommended: `edit` starts the editor itself with `subprocess.Popen`, after `shutil.which` finds it on the `PATH`, and the editor gets the environment, the current folder, and the console of `recipe-menu`. Architecture 4 and 8 gain the rule of choice 9, which the Architect records with an ADR in a `[docs]` PR before the F16 mock PR. Tests name a stand-in editor in the settings.
  - Option 2: `cli` starts programs for the commands. `Context` gets a new field, a function that starts a program and waits for it, which `main` fills, and a test replaces with a stand-in in the process. `edit` calls it. F15-T03, which compares the names of the fields of `Context`, changes in a test-fix PR before the mock PR, and the `Context` row of architecture 5.2 changes. Choices 4, 5, 9, and 10, section 3, and the examples change before the mock PR.
  - The reason for option 1: only `edit` starts a program, and the requirement names that program, so one rule covers it. Option 2 adds a field that one command uses to the context of every command, and its tests would still need a stand-in for the real start.
- **D. An editor that ends at once** (choice 6).
  - Option 1, recommended: when the editor ends with exit code 0 within 2 seconds and the recipe has not changed, `edit` writes the prompt of choice 6 and waits for Enter before it checks.
  - Option 2: `edit` checks as soon as the program that it started ends. With a Notepad window already open, the check then comes at once, before you change anything. You would close every Notepad window first, or set Notepad to open files in a new window. Choice 6 and the examples change before the mock PR, and the Test Manager changes the expected result of v0.2-S19 step 3 to a check at once.
  - The reason for option 1: the check then still comes after your change, whichever way Notepad opens the file, and also with an editor such as `code` without `--wait`.

No later feature builds on F16. It is the last feature of the order and of v0.2.

troy-mode's flow has one mock PR and one implementation PR. No test of an accepted feature breaks with the entry in `COMMANDS`, the field `editor`, or the key `editor` (section 3), so no test-fix PR comes before the mock PR.

The mock (PR 3) holds `src/recipe_menu/commands/edit/__init__.py`, `messages.py`, and one internal file for `run`, such as `_run.py`, and the entry in `src/recipe_menu/cli/_commands.py`. It adds the field `editor` with its default to `Settings`, without the checks of 3.1, and the two messages of 3.2 to `src/recipe_menu/settings/messages.py`. It leaves `read_settings` as it is, so `editor` is still an unknown key there. It defines every message and `EDIT_COMMAND` with all its fields. Its `run` checks nothing, reads no file, starts nothing, writes nothing, and gives 0. So a new test fails against the mock (R09) when it checks an output line, exit code 1 or 2 from `edit`, a line on the error stream, the arguments that the stand-in got, the change that it made, a problem of the key `editor`, the text of `UNKNOWN_KEY` with five keys, or a check of `Settings.editor`. These tests pass against the mock and break R09: a test that checks only the fields of `EDIT_COMMAND`, the help, a message, exit code 0, an empty error stream, the default of `Settings.editor`, or the equality of settings. So does a test of what `cli` does before it runs `edit`, such as a missing data folder, broken settings, no ID, two IDs, an unknown option, or `edit --help`. So does a test that checks only that a run writes no file or starts no stand-in. Each such test must also check something that the mock gets wrong, such as the output. The mock changes 6 files, more than R03's 5, in about 200 lines by estimate, so its description gives a soft-limit reason: the tests reach the settings and `edit` both directly and through `main`, so they come in one stage, as in the mocks of F14 and F15.

The implementation (PR 5) holds `run` with its checks of the ID, its listings, the finding and starting of the editor, the wait, the prompt, and the report, in internal files of `edit`, such as `_run.py`, `_editor.py`, and `_report.py`. It also holds the checks of `Settings.editor`, and the reading and splitting of the key `editor` in `settings`, such as in `_settings.py`, `_read.py`, and `_read_parts.py`. By estimate, it changes about 7 files in about 450 lines, more than R03's 5 files, so its description gives a soft-limit reason too: the tests of `edit` need all these parts at once. The Developer runs troy-check early.

### 2.1 `EDIT_COMMAND`

- Module: edit
- Purpose: The description of the `edit` command. `cli` reads it to parse the command line, write the help, check the data folder and the settings, and run the command (F05 design 2.5 and 2.9). Its `run` starts the editor of the settings on the recipe's file, waits for it, and checks the recipe, as 2.2 says.

Signature:

```python
EDIT_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("edit",)
#   help_line = EDIT_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = Argument(ID_ARGUMENT)
#   options = ()
#   folder = FolderUse.READ
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("edit",)`. | None |
| `help_line` | `Message` | `EDIT_HELP`: "Edit a recipe in your editor, then check it." and "在编辑器里修改一个菜谱，然后检查它。". | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Checks the ID, lists `recipes/`, starts the editor, waits for it, and checks the recipe, as 2.2 says. | Gives 0 or 1. Raises `UsageError` only for an ID that breaks the rule of `is_recipe_id`, before it reads a file. Raises nothing for bad data, an editor that cannot start, or an editor that fails. Lets `KeyboardInterrupt` go on to `cli`. |
| `argument` | `Argument` | `Argument(ID_ARGUMENT)`, required and not repeated, with the name `ID` in both languages. | None |
| `options` | An empty tuple | `edit` has no options of its own. | None |
| `folder` | `FolderUse` | `FolderUse.READ`: `cli` stops `edit` when the data folder is missing or the settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4, F15 design 3.1). | `run` uses `context.lang`, `context.folder`, `context.settings.editor`, `context.out`, `context.err`, and `context.input`. It uses neither `context.today` nor `context.random`. |
| `arguments` | `Arguments` | What the command line gives `edit` (F05 design 2.6). | `arguments.values` is `(ID,)`, because `cli` checks the number of values. It has no options. |

- Return value: `EDIT_COMMAND`, a `Command`.
  - `EDIT_COMMAND.usage` is `edit ID` in both languages. So the help shows `edit ID`, and a usage error quotes `recipe-menu edit ID`.
  - `EDIT_COMMAND.run(context, arguments)` takes the steps of 2.2, writes its lines in `context.lang`, and gives 0 or 1.

After F16, the help lists these commands and options, with the second column after 24 columns, as after F14 and F15 (choice 1). The other lines of the help are those of the F05 prototype. In English:

```text
Commands:
  init                  Create the data folder with example data.
  check                 Check every data file for mistakes.
  list                  List the recipes.
  show ID               Show one recipe.
  search WORD...        Find recipes by name, ingredient, or tag.
  add                   Add a recipe by answering questions.
  edit ID               Edit a recipe in your editor, then check it.
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
  edit ID               在编辑器里修改一个菜谱，然后检查它。
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

Errors: `run` raises `UsageError(NOT_A_RECIPE_ID, None, id=value)` when `is_recipe_id(value)` is false for the value of `ID` (choice 2). It raises nothing else on purpose.

- Side effects: Those of 2.2. `run` lists `recipes/` twice, reads the recipe's file through `read_file_text`, starts the editor and waits for it, may read one line from `context.input`, reads the catalog and the recipe through `check_recipe`, and writes to `context.out` or `context.err`. It writes no file.
- Performance target: None

Example:

In this example, `home` is an empty temporary folder ([architecture 10](../../architecture.md#10-test-setup)). The help comes from `COMMANDS`, which holds eleven commands after F16.

```python
import io
from datetime import date

from recipe_menu.app import Argument, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.edit import EDIT_COMMAND
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

assert EDIT_COMMAND.words == ("edit",)
assert EDIT_COMMAND.usage == BiText("edit ID", "edit ID")
assert EDIT_COMMAND.help_line.render(Lang.EN) == "Edit a recipe in your editor, then check it."
assert EDIT_COMMAND.help_line.render(Lang.ZH) == "在编辑器里修改一个菜谱，然后检查它。"
assert EDIT_COMMAND.argument == Argument(Message("ID", "ID"))
assert EDIT_COMMAND.options == ()
assert EDIT_COMMAND.folder is FolderUse.READ


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
assert len(english) == 24
assert english[10:13] == [
    "  add                   Add a recipe by answering questions.",
    "  edit ID               Edit a recipe in your editor, then check it.",
    "  menu new [WEEK]       Create an empty week menu.",
]
assert english[18].startswith("  --lang en|zh          The language of the output.")
chinese = help_lines("--help", "--lang", "zh")
assert chinese[11] == "  edit ID               在编辑器里修改一个菜谱，然后检查它。"
```

### 2.2 `recipe-menu edit`

- Module: edit
- Purpose: The command that opens a recipe's file in the editor that the settings name, Notepad by default, waits until you close the editor, and then checks that recipe ([requirements 3](../../requirements.md#3-how-users-interact-with-it) and [4](../../requirements.md#4-features)). The F16 prototype shows it.

Signature:

```text
recipe-menu edit ID [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `ID` | A recipe ID | The recipe to edit, such as `mapo-tofu`. | Exactly one value. It follows the rule of `is_recipe_id`, and `recipes/` holds its file. |
| `--lang` | `en` or `zh` | The language of every line. It does not change the file or the editor. | As F05 design 2.10 gives it. Without the option, the language of the settings, else English. |
| `--data` | A folder | The data folder. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. |
| `--help` | A flag | Shows the help (2.1) and does not run `edit`. | None |
| The setting `editor` | A text in `settings.toml` | The program and its options (choice 3). | `notepad` without the key. |
| The standard input | Lines of text | Read only at the prompt of choice 6. | Any text. The end of the input goes on to the check. |

`edit` takes these steps, in order. `recipe_id` is the value of `ID`, `path` is `context.folder.recipe_file(recipe_id)`, and `program` is `context.settings.editor[0]`.

1. When `is_recipe_id(recipe_id)` is false, `edit` raises `UsageError(NOT_A_RECIPE_ID, None, id=recipe_id)` before it reads a file, and `cli` exits with 2 (choice 2).
2. `list_recipe_ids(context.folder)` gives `ids` and their problems (F04 design 2.5). With an error among the problems, `edit` gives `stop_at_error(context, error)` for the first one.
3. When `ids` lacks `recipe_id`, `edit` writes `UNKNOWN_ID` to the error stream and gives 1.
4. `shutil.which(program)` gives `found`. When it gives `None`, `edit` writes `EDITOR_NOT_FOUND` to the error stream and gives 1 (choice 4).
5. `read_file_text(context.folder, path)` gives `before`, the text of the file or a `Problem` (F14 design 3.5).
6. `subprocess.Popen([found, *context.settings.editor[1:], str(path)])` starts the editor. When it raises `OSError`, `edit` writes `EDITOR_NOT_STARTED` to the error stream and gives 1 (choice 4).
7. `edit` writes the first line, `OPENED_IN_NOTEPAD` or `OPENED_IN_EDITOR`, and flushes `context.out` (choice 4).
8. `edit` waits until the editor ends, in steps of half a second (choice 5).
9. When the editor's exit code is not 0, `edit` writes `EDITOR_FAILED` to the error stream and gives 1 (choice 5).
10. When the editor ended less than 2 seconds after step 6, and `read_file_text(context.folder, path)` equals `before`, `edit` writes `QUICK_EXIT`, flushes `context.out`, and reads one line from `context.input` (choice 6).
11. `list_recipe_ids(context.folder)` gives the IDs and problems again. With an error among the problems, `edit` gives `stop_at_error(context, error)` for the first one. When the IDs lack `recipe_id`, `edit` writes `GONE` to the error stream and gives 1 (choice 7).
12. `check_recipe(context.folder, recipe_id)` gives the problems (F15 design 3.4). `edit` writes the report to the output stream, and gives 1 when a problem is an error and 0 otherwise (choice 7).

Ctrl+C in steps 8 and 10 raises `KeyboardInterrupt`, which `edit` lets go on to `cli`. The warnings of the listings change nothing.

- Return value: The exit code, with the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | The check found no error. It may have found warnings. | The output stream: the first line, the prompt of choice 6 when `edit` wrote it, and the report. |
| 1 | A listing has an error, `recipes/` holds no file of the ID, the editor cannot be found, cannot start, or ends with an exit code other than 0, the recipe is gone after the editor, or the check found an error. | The error stream holds the three lines of `stop_at_error`, or one of `UNKNOWN_ID`, `EDITOR_NOT_FOUND`, `EDITOR_NOT_STARTED`, `EDITOR_FAILED`, and `GONE`. The output stream holds the first line when the editor started. After a check that found an error, the report goes to the output stream, and nothing goes to the error stream. |
| 2 | A `UsageError` of `cli`, or `NOT_A_RECIPE_ID` of step 1. | The error stream: the message, then its hint when it has one. |
| 130 | Ctrl+C. | Nothing more, as `cli` gives it (F05 design 2.10). |

The output is these lines, each ended by a line break, except the prompt of choice 6, which has none of its own:

| Case | What `edit` writes to the output stream |
| --- | --- |
| The editor started | `OPENED_IN_NOTEPAD` when `context.settings.editor` is `("notepad",)`, else `OPENED_IN_EDITOR`. |
| The editor ended at once, and the file did not change (choice 6) | `QUICK_EXIT`. Then, when the input is not a terminal, the line that `edit` read without the LF at its end, and a line break, or only a line break at the end of the input. |
| The check found no problem | An empty line and `CHECKED_CLEAN`. |
| The check found warnings and no error | An empty line, `CHECKED_WARNINGS`, and `problem_block` of the warnings. |
| The check found an error | An empty line, `CHECKED_PROBLEMS`, `problem_block` of the errors, `problem_block` of the warnings, and the closing line: `EDIT_AGAIN` when every error is in the recipe's file, else `FIX_AND_CHECK`. |

The messages of `edit` are these. `ERROR_COUNT` and `WARNING_COUNT` are `Plural` values (F02 design 2.4), each picked by its `count`. Their form "for more" is the form for every count other than 1, and their Chinese text is the same in both forms. `QUICK_EXIT` ends with a space in English, and with `：` and no space in Chinese.

| Name | English | Chinese |
| --- | --- | --- |
| `EDIT_HELP` | `Edit a recipe in your editor, then check it.` | `在编辑器里修改一个菜谱，然后检查它。` |
| `ID_ARGUMENT` | `ID` | `ID` |
| `NOT_A_RECIPE_ID` | `"{id}" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | `“{id}”不是菜谱 ID。运行“recipe-menu list”查看菜谱 ID。` |
| `UNKNOWN_ID` | `No recipe has the ID "{id}". Run "recipe-menu search {id}" to find it.` | `没有 ID 为“{id}”的菜谱。运行“recipe-menu search {id}”查找它。` |
| `OPENED_IN_NOTEPAD` | `Opened {file} in Notepad. Close Notepad when you are done.` | `已用记事本打开 {file}。改完后关闭记事本。` |
| `OPENED_IN_EDITOR` | `Opened {file} in "{editor}". Close the editor when you are done.` | `已用“{editor}”打开 {file}。改完后关闭编辑器。` |
| `EDITOR_NOT_FOUND` | `Cannot start the editor "{editor}": no program of that name was found. Name your editor in settings.toml, such as editor = "code --wait".` | `无法启动编辑器“{editor}”：找不到这个名称的程序。请在 settings.toml 里写上你的编辑器，比如 editor = "code --wait"。` |
| `EDITOR_NOT_STARTED` | `Cannot start the editor "{editor}". The system says: {reason}` | `无法启动编辑器“{editor}”。系统提示：{reason}` |
| `EDITOR_FAILED` | `The editor "{editor}" ended with exit code {code}, so the recipe was not checked. Run "recipe-menu check" to check it.` | `编辑器“{editor}”以退出码 {code} 结束，所以没有检查这个菜谱。运行“recipe-menu check”检查它。` |
| `QUICK_EXIT` | `The editor closed at once, maybe because it opened the recipe in a window that was already open. When you have saved the recipe there, press Enter: ` | `编辑器马上就关闭了，可能是因为它在已经打开的窗口里打开了这个菜谱。在那里改完并保存后，按 Enter：` |
| `GONE` | `The recipe {id} is gone: its file was deleted or renamed while the editor was open.` | `菜谱 {id} 不见了：编辑器打开期间，它的文件被删除或改了名。` |
| `CHECKED_CLEAN` | `Checked {id}: no errors.` | `已检查 {id}：没有错误。` |
| `CHECKED_WARNINGS` | `Checked {id}: no errors, {warnings}.` | `已检查 {id}：没有错误，有 {warnings}。` |
| `CHECKED_PROBLEMS` | `Checked {id}: {problems}.` | `已检查 {id}：有 {problems}。` |
| `ERROR_COUNT`, for one | `{count} error` | `{count} 个错误` |
| `ERROR_COUNT`, for more | `{count} errors` | `{count} 个错误` |
| `WARNING_COUNT`, for one | `{count} warning` | `{count} 个警告` |
| `WARNING_COUNT`, for more | `{count} warnings` | `{count} 个警告` |
| `EDIT_AGAIN` | `Run "recipe-menu edit {id}" to fix it.` | `运行“recipe-menu edit {id}”改正它。` |
| `FIX_AND_CHECK` | `Fix the errors, then run "recipe-menu check".` | `改正错误后，运行“recipe-menu check”。` |

`ID_ARGUMENT`, `NOT_A_RECIPE_ID`, and `UNKNOWN_ID` have the texts of `show` (F09 design 2.4). `ERROR_COUNT`, `WARNING_COUNT`, and `FIX_AND_CHECK` have the texts of `add` (F15 design 2.2). Both texts of `OPENED_IN_NOTEPAD`, the English `CHECKED_PROBLEMS` with one error, the English `EDIT_AGAIN`, and the Chinese `CHECKED_CLEAN` are the lines of the prototype.

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `id` | The value of `ID` as you typed it. Except in `NOT_A_RECIPE_ID`, it follows the rule of `is_recipe_id`, so the command lines of `UNKNOWN_ID` and `EDIT_AGAIN` are valid. |
| `file` | `str(context.folder.relative(path))`, such as `recipes\mapo-tofu.toml` on Windows (choice 8). |
| `editor` | `context.settings.editor[0]`, the program as the settings write it, without its quotation marks, such as `code` or `C:\Program Files\Notepad++\notepad++.exe`. |
| `reason` | `error.strerror` of the `OSError`, or the name of its type when it has none, as `datafile` gives a system's reason. |
| `code` | The exit code of the editor, an `int`, as `Popen` gives it. |
| `warnings` | `WARNING_COUNT` with the number of warnings, as a `BiText`: `1 warning` and `1 个警告`. |
| `problems` | `and_list` of `ERROR_COUNT` with the number of errors and `WARNING_COUNT` with the number of warnings, each as a `BiText`, leaving out a count of 0: `1 error and 2 warnings` and `1 个错误和 2 个警告`. |
| `count` | The number of errors in `ERROR_COUNT`, and of warnings in `WARNING_COUNT`. |

Errors:

`cli` reports the mistakes on the command line, a missing data folder, and an error in the settings before it runs `edit` (F05 design 2.10).

| Error | When |
| --- | --- |
| Exit code 1, with `NO_DATA_FOLDER` and `RUN_INIT` on the error stream | The data folder is not a folder. `cli` checks it in step 9 of F05 design 2.10, because `edit` has `FolderUse.READ`. |
| Exit code 1, with the first error of the settings and `RUN_CHECK` on the error stream | The settings have an error, a wrong `editor` included (choice 3). |
| Exit code 2, with `TOO_FEW_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`: `An argument is missing. Write "recipe-menu edit ID".` | No ID follows `edit`. |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "rice". Write "recipe-menu edit ID".` | Two or more IDs follow `edit`. |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"edit" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 2, with `NOT_A_RECIPE_ID` and no hint, such as `"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.` | The value of `ID` breaks the rule of `is_recipe_id` (step 1). |
| Exit code 1, with the three lines of `stop_at_error` on the error stream, such as `recipes\Rice Bowl.toml`, its message, and `RUN_CHECK` | A listing of `recipes/` has an error, before or after the editor (steps 2 and 11). |
| Exit code 1, with `UNKNOWN_ID` on the error stream, such as `No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.` | `recipes/` holds no file of the ID (step 3). |
| Exit code 1, with `EDITOR_NOT_FOUND` on the error stream | `shutil.which` finds no program (step 4). Nothing starts. |
| Exit code 1, with `EDITOR_NOT_STARTED` on the error stream | `Popen` raises `OSError` (step 6). |
| Exit code 1, with the first line on the output stream and `EDITOR_FAILED` on the error stream | The editor ends with an exit code other than 0 (step 9). Nothing is checked. |
| Exit code 1, with the first line on the output stream and `GONE` on the error stream | After the editor, `recipes/` no longer holds the file of the ID (step 11). |
| Exit code 1, with the report on the output stream | The check found an error (step 12). |
| Exit code 130 | Ctrl+C while `edit` waits for the editor or at the prompt of choice 6. The editor stays open, and nothing is checked (choice 5). |

- Side effects: `cli` looks at the data folder and reads `settings.toml` (F05 design 2.10). `edit` then lists `recipes/`, reads the recipe's file once through `read_file_text`, starts the editor as a new process, and waits until it ends. After an editor that ended at once, it reads the recipe's file once more, and may read one line of the standard input. Then it lists `recipes/` again, and reads `catalog.toml` and the recipe's file once each through `check_recipe`. It writes to the output stream and the error stream. It writes no file. What the editor changes is the editor's doing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`, `home` is an empty temporary folder outside it, and `stand_in` is the path of a new file in a temporary folder of its own ([architecture 10](../../architecture.md#10-test-setup)). The paths hold no `'`. The stand-in is a Python script that the settings name with the test's Python, so it needs no `PATH` and no console. It replaces the first `old` with `new` in the file that it gets last, and changes nothing when the two are equal. The first two runs are the two sections of the prototype "An edit that leaves a mistake" and "A clean edit, in Chinese", with the stand-in in place of Notepad. The third run leaves `red-braised-pork` as it is, so the stand-in ends at once without a change, and `edit` writes the prompt of choice 6. The other runs give an unknown ID, an ID that breaks the rule, no ID, a program that does not exist, an editor that ends with exit code 3, and an editor that deletes the file.

```python
import io
import sys
from datetime import date
from pathlib import Path

from recipe_menu.cli import main

stand_in.write_text(
    "import sys\n"
    "from pathlib import Path\n"
    "old, new, file = sys.argv[1], sys.argv[2], Path(sys.argv[3])\n"
    "if old != new:\n"
    "    data = file.read_bytes()\n"
    "    file.write_bytes(data.replace(old.encode(), new.encode(), 1))\n",
    encoding="utf-8",
)
settings_text = folder.settings.read_text(encoding="utf-8")


def use_editor(*words: str) -> None:
    editor = " ".join(f'"{word}"' for word in words)
    folder.settings.write_text(settings_text + f"editor = '{editor}'\n", encoding="utf-8")


def edit(*argv: str, stdin: str = "") -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["edit", "--data", str(folder.root), *argv],
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
        stdin=io.StringIO(stdin),
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


python = sys.executable
mapo = Path("recipes", "mapo-tofu.toml")
use_editor(python, str(stand_in), "郫县豆瓣酱", "豆瓣酱")
assert edit("mapo-tofu") == (
    1,
    [
        f'Opened {mapo} in "{python}". Close the editor when you are done.',
        "",
        "Checked mapo-tofu: 1 error.",
        f"  {mapo}, ingredient 3",
        '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
        'Run "recipe-menu edit mapo-tofu" to fix it.',
    ],
    [],
)
use_editor(python, str(stand_in), "豆瓣酱", "郫县豆瓣酱")
assert edit("mapo-tofu", "--lang", "zh") == (
    0,
    [f"已用“{python}”打开 {mapo}。改完后关闭编辑器。", "", "已检查 mapo-tofu：没有错误。"],
    [],
)

pork = Path("recipes", "red-braised-pork.toml")
quick = (
    "The editor closed at once, maybe because it opened the recipe in a window that "
    "was already open. When you have saved the recipe there, press Enter: "
)
use_editor(python, str(stand_in), "x", "x")
assert edit("red-braised-pork") == (
    0,
    [
        f'Opened {pork} in "{python}". Close the editor when you are done.',
        quick,
        "",
        "Checked red-braised-pork: no errors, 1 warning.",
        f"  {pork}, steps",
        "    No English steps. Commands show the Chinese steps instead.",
    ],
    [],
)

unknown = 'No recipe has the ID "mapo". Run "recipe-menu search mapo" to find it.'
assert edit("mapo") == (1, [], [unknown])
not_an_id = '"Mapo" is not a recipe ID. Run "recipe-menu list" to see the IDs.'
assert edit("Mapo") == (2, [], [not_an_id])
assert edit() == (
    2,
    [],
    [
        'An argument is missing. Write "recipe-menu edit ID".',
        'Run "recipe-menu --help" to see the commands.',
    ],
)

use_editor("no-such-editor-f16")
not_found = (
    'Cannot start the editor "no-such-editor-f16": no program of that name was found. '
    'Name your editor in settings.toml, such as editor = "code --wait".'
)
assert edit("tomato-egg") == (1, [], [not_found])

rice = Path("recipes", "rice.toml")
opened_rice = f'Opened {rice} in "{python}". Close the editor when you are done.'
use_editor(python, "-c", "raise SystemExit(3)")
failed = (
    f'The editor "{python}" ended with exit code 3, so the recipe was not checked. '
    'Run "recipe-menu check" to check it.'
)
assert edit("rice") == (1, [opened_rice], [failed])
use_editor(python, "-c", "import os, sys; os.remove(sys.argv[1])")
gone = "The recipe rice is gone: its file was deleted or renamed while the editor was open."
assert edit("rice") == (1, [opened_rice], [gone])
```

## 3. Changes to existing interfaces

F16 adds to one implemented module what architecture 5.1 plans for it: "F16 adds the editor" to `settings.toml`, which F05 design section 2 and F14 design section 2 plan as a key of `Settings` and `read_settings`. No call of an exported name of F01 to F15 breaks. The new field comes last, with a default, so `Settings(Lang.EN, (Meal.DINNER,), 5)` of F15-T02, and every call that gives three or four values by position, keep their meaning. `read_settings` keeps its signature. The requirements already name the setting (requirements 4, F16), so no `[docs]` PR approves these additions. The Architect reviews them in this design, as it reviewed F14's `dishes`. Points B and C change architecture 4, 6, and 8, and the Architect writes them with an ADR in a `[docs]` PR before the F16 mock PR, once Troy decides them.

1. `settings`: `Settings` gets the field `editor` (3.1), and `read_settings` reads the key `editor` (3.2). Two settings are now equal when their five fields are equal. The key `editor` gave `UNKNOWN_KEY` before, and the text of `UNKNOWN_KEY` for the settings now lists five keys.
2. `cli`: `COMMANDS` gets `EDIT_COMMAND` after `ADD_COMMAND` (choice 1).

These changes follow at F16's acceptance, outside the design:

- The Product Manager adds the line of `edit ID` after the line of `add` to the two help blocks of the F05 prototype, "Help in English" and "Help in Chinese", as 2.1 gives them. The note at the top of that prototype then says that the help lists `edit` too, and no longer that F16 adds it. The Test Manager ruled at F14's acceptance that those two blocks show the help of the accepted features.
- The Test Manager updates the v0.2 test plan, as its section 2 provides: the help of v0.2-S14 with the line of `edit`, the first lines of v0.2-S12, steps 1 to 3 of v0.2-S13, step 3 of v0.2-S15 and v0.2-S16 (choice 6), step 3 of v0.2-S19, and the F16 point of "Where the plan waits for the designs".
- The Architect can add the editor to the `Settings` row of architecture 5.2, as version 4.1 added the dishes.

No test of an accepted feature changes. These tests stay true:

- F07-T17 and F13-T01 find their line by its start and compare its text column with that of `--lang en|zh`. `edit ID` is 7 columns wide, so the second column stays after 24 columns.
- F08-T14 checks that `check` follows `init`, F09-T01 that `list` and `show` follow `check`, F10-T01 that `search` follows `show ID`, F11-T01 that `menu new` comes after `search` and that `menu show` follows it, F14-T01 that `menu suggest` follows `menu show`, and F15-T01 that `add` comes after `search`, at the column of `--lang en|zh`. The line of `edit` comes between none of these pairs. F11-T01 finds the line of `menu new` by its start since the F15 test fix, so a line between `add` and `menu new` does not matter. F15-T01 compares the whole help only for its own ten commands, and F14-T01 only for its own nine.
- F09-T19, F11-T27, F11-T32, F11-T35, F13-T22, F13-T27, F14-T21, F14-T31, and F15-T24 compare one help of the real `COMMANDS` with another. `edit` is one word, so `recipe-menu menu` still lists only the three `menu` commands, as F11-T32 and F14-T21 expect.
- F15-T03 compares the names of the fields of `Context`, and F16 adds no field. Its item 5 runs `list`, `check`, `show tomato-egg`, `menu show 2026-W47`, and `--help` with a watched standard input. None of them runs `edit`, and the help equals itself.
- F05-T10 and F05-T11 check that the key list of `UNKNOWN_KEY` for the settings starts with `language`, `meals`, and `servings`, through `KEYS_START` of `tests/f05_texts.py`. F14-T23 also checks, through `assert_settings_problems` of `tests/f14_support.py`, that its fourth key is `dishes`. `editor` comes fifth, so all three hold.
- F05-T02, F05-T03, F14-T22, F15-T02, and the other tests that build settings give at most four values, so `editor` gets its default on both sides of each comparison.
- F03-T30 writes `editor = "C:\Program Files\notepad.exe"`, a syntax mistake that `read_toml` reports before any key is read.
- No test runs `edit`, which gives `Unknown command "edit".` before the mock, and no test expects that line. F15's `ID_EXISTS` names `recipe-menu edit` only as text.
- The example of F05 design 2.3 writes `editor = 1` and expects `UNKNOWN_KEY`. After F16, that line gives `NOT_A_TEXT` at the place `editor`. No test runs that line, because F05-T11 uses `colour = 1`. The approved F05 design keeps its text, and 3.2 gives the rule after F16.

F16 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, and `and_list`.
- F03's `DataFolder` with `recipe_file` and `relative`, `Problem`, `Severity`, and `read_toml`, and the messages `NOT_A_TEXT`, `EMPTY_TEXT`, and `UNKNOWN_KEY` of `datafile` (F03 design 2.10).
- F04's `read_text` and `report_unknown_keys` of `datafile` (F04 design 3.2), `is_recipe_id` and `list_recipe_ids`, and `read_recipe` through `check_recipe`.
- F05's `Argument`, `Arguments`, `Command`, `Context`, `FolderUse`, `UsageError`, `first_error`, and `stop_at_error` in `app`, `Settings` and `read_settings` in `settings`, with the additions of 3.1 and 3.2, and `COMMANDS` and `main` in `cli`.
- F14's `read_file_text` in `datafile`.
- F15's `Context.input`, and `check_recipe` and `problem_block` in `check`.

### 3.1 `Settings.editor`

- Module: settings
- Purpose: The program that `edit` opens a recipe in, and its options ([requirements 4](../../requirements.md#4-features), architecture 5.1). `read_settings` fills it from the key `editor` (3.2), and `edit` starts it (choice 4).

Signature:

```python
@dataclass(frozen=True, slots=True)
class Settings:
    language: Lang | None = None
    meals: tuple[Meal, ...] = (Meal.LUNCH, Meal.DINNER)
    servings: int = 2
    dishes: tuple[int, int, int] = (1, 1, 1)
    editor: tuple[str, ...] = ("notepad",)

    def dishes_for(self, meal: Meal) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `editor` | A tuple of `str` | The program, then its options, as the words of choice 3. `edit` adds the recipe's file after them. | At least one item. The first item is not empty. No item holds U+0000. The other items may be empty. |

The other fields keep their meanings and constraints (F05 design 2.2, F14 design 3.1).

- Return value: A `Settings`. Two settings are equal when their five fields are equal, and a `Settings` is hashable. `Settings()` and every call that F01 to F15 make keep `editor` at `("notepad",)`.

Errors:

The errors of F05 design 2.2 and F14 design 3.1 stay, and these come with `editor`:

| Error | When |
| --- | --- |
| `TypeError` | `editor` is not a tuple, or it holds an item that is not a `str`. |
| `ValueError` | `editor` is empty, its first item is empty, or an item holds U+0000. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

defaults = Settings()
assert defaults.editor == ("notepad",)
code = Settings(editor=("code", "--wait"))
assert code.editor == ("code", "--wait")
assert code != defaults
whole = Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2, (1, 1, 1), ("notepad",))
assert whole == Settings(Lang.EN)
assert hash(whole) == hash(Settings(Lang.EN))
assert Settings(editor=("code", "")).editor == ("code", "")

Settings(editor=())  # raises ValueError
Settings(editor=("", "--wait"))  # raises ValueError
Settings(editor=("vi", "a\x00b"))  # raises ValueError
Settings(editor="notepad")  # raises TypeError
Settings(editor=["notepad"])  # raises TypeError
Settings(editor=("code", 1))  # raises TypeError
```

### 3.2 `read_settings`: the key `editor`

- Module: settings
- Purpose: Reads the optional key `editor` of `settings.toml` into `Settings.editor`, and reports its problems with their places, as for the other keys (F05 design 2.3, choice 3). `cli` and `check` call `read_settings` as before.

Signature:

```python
def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: The pair `(settings, problems)` of F05 design 2.3 and F14 design 3.2, with these additions.
  - The file may hold the key `editor`, a text that splits into the words of choice 3, such as `editor = "code --wait"`. Without the key, `settings.editor` is `("notepad",)`.
  - `settings.editor` holds the words of the text, in their order, without the quotation marks that group them.
  - The keys of the top of the file are `language`, `meals`, `servings`, `dishes`, and `editor`, in this order. So `UNKNOWN_KEY` names "language, meals, servings, dishes, and editor" and "language、meals、servings、dishes 和 editor", in its form for more keys.

The place of the new problems is this:

| Place | English | Chinese |
| --- | --- | --- |
| `editor` | `editor` | `编辑器` |

`read_settings` makes these checks of `editor`. A missing key gives no problem.

| Part | Check | Problem | Place | Kind |
| --- | --- | --- | --- | --- |
| `editor` | The value is not a text, such as `editor = 1` or `editor = ["code"]`. | `NOT_A_TEXT` of `datafile`, with `key` set to `editor` | `editor` | Error |
| `editor` | The text is empty or holds only whitespace. | `EMPTY_TEXT` of `datafile`, with `key` set to `editor` | `editor` | Error |
| `editor` | The text ends inside a quoted part, its first word is empty, or a word holds U+0000. | `EDITOR_NOT_A_COMMAND` | `editor` | Error |

Each value gives at most one problem, the first of the table that applies. The problem of `editor` comes after those of `dishes` and before the unknown keys of the top of the file.

These are the new messages of `settings`:

| Name | English | Chinese |
| --- | --- | --- |
| `EDITOR` | `editor` | `编辑器` |
| `EDITOR_NOT_A_COMMAND` | `"editor" must name a program and then its options, such as editor = "code --wait". Put a path with spaces in double quotation marks, and close each one.` | `“editor”必须先写程序，再写它的选项，比如 editor = "code --wait"。带空格的路径要放在英文双引号里，每个引号都要配对。` |

Errors: None. `read_settings` never raises for bad data.

- Side effects: Reads `settings.toml` through `read_toml`, as before. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/`.

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings


def settings_of(*lines: str) -> tuple[Settings | None, list[str]]:
    folder.settings.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    settings, problems = read_settings(folder)
    return settings, [problem.text(Lang.EN) for problem in problems]


assert settings_of('editor = "code --wait"') == (Settings(editor=("code", "--wait")), [])
assert settings_of('editor = "  notepad  "') == (Settings(), [])
notepad_pp = r"""editor = '"C:\Program Files\Notepad++\notepad++.exe" -multiInst -nosession'"""
program = r"C:\Program Files\Notepad++\notepad++.exe"
assert settings_of(notepad_pp)[0] == Settings(editor=(program, "-multiInst", "-nosession"))
assert settings_of("editor = 'code --file=\"a b\"'")[0] == Settings(editor=("code", "--file=a b"))

not_a_command = (
    '"editor" must name a program and then its options, such as editor = "code --wait". '
    "Put a path with spaces in double quotation marks, and close each one."
)
assert settings_of(r"""editor = '"C:\Program Files\x.exe --wait'""") == (None, [not_a_command])
assert settings_of("""editor = '"" --wait'""") == (None, [not_a_command])
assert settings_of('editor = "vi \\u0000"') == (None, [not_a_command])
assert settings_of("editor = 1") == (None, ['"editor" must be a text in quotation marks.'])
assert settings_of('editor = "   "') == (None, ['"editor" is empty.'])
settings, texts = settings_of("dishes = 2", "editor = []", "colour = 1")
assert settings is None
assert texts[1:] == [
    '"editor" must be a text in quotation marks.',
    'Unknown key "colour". The keys are language, meals, servings, dishes, and editor.',
]

folder.settings.write_text("editor = 1\ncolour = 1\n", encoding="utf-8")
_, problems = read_settings(folder)
assert [problem.place for problem in problems] == [BiText("editor", "编辑器"), None]
keys_zh = "未知键“colour”。可用的键：language、meals、servings、dishes 和 editor。"
assert problems[1].text(Lang.ZH) == keys_zh
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `edit` is the command module that architecture 3 gives F16, in `src/recipe_menu/commands/edit/`, and it exports only `EDIT_COMMAND`. It imports only `app`, `lang`, `text`, `datafile`, `recipes`, and `check`. All of them are in its row, and `edit --> check` is an arrow of architecture 4. It reads the editor as `context.settings.editor`, so it needs neither `settings` nor `units`, `catalog`, `menus`, or `shopping`. Section 3 adds what architecture 3 and 5.1 plan for F16: the key `editor` of `settings.toml`, and `Settings.editor`, a tuple of `str` with a default in a frozen dataclass with `slots=True`, so the value rules of architecture 8 hold. The split of the key lives in `settings`, which reads the file, and each new file belongs to one module. `edit` writes no file, so architecture 1 "Your files stay as you wrote them" holds: only the editor changes the recipe. Point 1 of the brief, point C: under option 1, `edit` touches the outside world in three ways that architecture 4 and 8 keep for `cli`. `shutil.which` reads `PATH`, `PATHEXT`, and `NoDefaultCurrentDirectoryInExePath` from the environment of the process, and the editor gets that environment, the current folder, and the console. So `main(environ={})` no longer keeps `edit` away from the PATH of the process, as choice 9 says. The rule that the Architect writes under option 1 names all three, not only the start of a program. Note 1, not blocking: point C describes option 2 fairly, but leaves out what it gains. Under option 2, the rule of architecture 8 stays whole: `main` would search the PATH of its `environ`, and the tests of `edit` would start no process, only the test of the starter in `cli` would. "Its tests would still need a stand-in for the real start" holds only for that test. The Architect still recommends option 1: one command starts one program that the requirement names, and option 2 adds a start-and-wait interface to `app` and a field to every context for it. The summary rightly says "the same for you", because Troy sees no difference. Point C can add this gain in a revision. Section 3's sentence "Points B and C change architecture 4, 6, and 8" holds for option 1 of each. Option 2 of point B changes the prototype and no architecture. Option 2 of point C changes the `Context` row of architecture 5.2, and architecture 8 then names the start of the editor among what `cli` does. Point 4 of the brief, speed: on an unchanged copy of main and on the model, `import recipe_menu.cli` loads neither `subprocess`, `shutil`, nor `threading`, and it already loads `time`. The five new files of the model, four of `edit` and one of `settings`, took 3.2 to 3.3 ms of self time under `python -X importtime` in 9 warm runs. Imported at the top, `subprocess` would add 5.0 to 8.7 ms and `shutil` 6.3 to 6.9 ms, so the imports inside the function keep about 11 to 15 ms out of the start of every command. Choice 12's "a few milliseconds" holds, and `check`'s 0.858 s under PT01 would become about 0.861 s. These times come from the review's sandbox on Troy's PC, not from v0.2's release test. |
| Follows the error handling and naming conventions | Pass | `run` raises `UsageError` only for an ID that breaks `is_recipe_id`, with no hint, as `show` does (ADR-0008). The first error of a listing stops `edit` through `first_error` and `stop_at_error`, before and after the editor. `UNKNOWN_ID`, `EDITOR_NOT_FOUND`, `EDITOR_NOT_STARTED`, `EDITOR_FAILED`, and `GONE` end `edit` with 1 on the error stream. The report goes to the output stream with either code, as architecture 6 says for `check` and the v0.2 test plan says for `add` and `edit`. Exit code 1 for an editor that cannot start or fails fits architecture 1, because the command did not work, as F15's early end of the input does. `edit` catches only the `OSError` of `Popen` and the `subprocess.TimeoutExpired` of its steps, both by name, and lets `KeyboardInterrupt` go on to `cli`. The names follow architecture 8. The module has its command's name. The 18 messages of `edit` and the 2 of `settings` are UPPER_SNAKE constants in each module's `messages.py`. The counts are `Plural` values, the list of counts comes from `and_list`, and the key `editor` is a lowercase English word. Point 1 of the brief, point B: option 1 changes architecture 6, as choice 8 says. Architecture 6 names the file of a message that is not a problem by its full path, and ADR-0009 and ADR-0011 ask every other case for its own change. The first line of `edit` is not a problem, so option 1 needs one case, as the swap line of `menu suggest` did (ADR-0011). Option 2 needs no change to the architecture, but changes the prototype through the requirement change flow, as point B says. Architecture 6 also has no row for a program that a command starts. Under either option of point C, the Architect's `[docs]` PR adds one: the editor cannot be found, cannot start, or ends with an exit code other than 0, `edit` catches it, the exit code is 1, and one line goes to the error stream. ruff 0.17.4 with the project's `pyproject.toml`, run on the model, flags exactly `PLC0415` for each import inside a function and `S603` for the call of `Popen`. With the `noqa` comments of choice 4, it flags nothing more in that code. Note 2, not blocking: the reason of `EDITOR_NOT_STARTED` is the text of Windows, in the language of Windows, and it can hold a literal `%1`. On the model, a `.py` file that `PATHEXT` found gave `The system says: %1 is not a valid Win32 application`, also in Chinese. A text file named `bogus.exe` gave `This version of %1 is not compatible with …`. `datafile` passes on the reasons of Windows the same way, so choice 4 can name the case and leave it. Note 3, not blocking: choice 5 says that `Popen.wait` gives the editor a quarter of a second after Ctrl+C. CPython 3.13 waits `min(0.25, remaining)` seconds, where `remaining` is what is left of the timeout. On Windows, the interrupt comes only when a half-second step ends, so the grace is often none. The editor is not stopped either way, so only the words change: "at most a quarter of a second". |
| Does not duplicate an existing interface | Pass | `edit` checks the ID with `is_recipe_id` and the listing of `list_recipe_ids`, and reads the file with `read_file_text`. It checks the recipe with `check_recipe`, writes the problems with `problem_block`, and stops with `stop_at_error`. `settings` reads the key with `read_text` and the messages `NOT_A_TEXT` and `EMPTY_TEXT` of `datafile`. Neither builds any of these again. The split rule of choice 3 is new, and the standard library has no fit. In POSIX mode, `shlex.split` takes `\` outside quotation marks as an escape, so `C:\Tools\ed.exe` loses its separators. In the other mode, it keeps the quotation marks in the word. The copies of `ID_ARGUMENT`, `NOT_A_RECIPE_ID`, `UNKNOWN_ID`, `ERROR_COUNT`, `WARNING_COUNT`, and `FIX_AND_CHECK` are internal messages, which architecture 8 keeps in each module, as the reviews of F13 to F15 accepted. Note 4, not blocking: `edit` also repeats internal code of `add`, the counts of the problems and the read of the listing that stops at the first error. The later `[refactor]` PR of the earlier reviews can share both, for example through `check`, which both commands import. |
| Depends only on features earlier in the order | Pass | F16 uses F02's `text`, F03's and F14's `datafile`, F04's `recipes`, F05's `app`, `settings`, and `cli`, F07's and F15's `check`, and F15's `Context.input`. It copies texts of F09 and F15. Each of these features comes before F16 and is accepted on main, F15 in commit 902ed65. F05 is the hard dependency of the F16 row, and F07 the soft one. F14 and F15 reach F16 through the shared modules `datafile`, `app`, and `check`, which point to earlier features, as architecture 4 allows. No later feature builds on F16. `subprocess`, `shutil`, and `time` are standard modules (ADR-0001), so R16 has nothing to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | The design writes down each assumption. `check_recipe` gets an ID of a listing made after the editor ended, as F15 design 3.4 requires. `edit` compares the ID exactly, so on Windows it never opens `Tomato-Egg.toml` for `tomato-egg`. The first line depends on `context.settings.editor == ("notepad",)`, and the prompt of point D only on the exit code, a duration of `time.monotonic()`, and two results of `read_file_text`. The editor gets the console, not `context.out`. Choices 4 and 6 say each of these. Point 2 of the brief, run on Windows 11 with Python 3.13.18 on a model of sections 2 and 3, with stand-in editors that open no window: (a) `shutil.which` with `PATHEXT` found `code.CMD` and `stand-in-editor.CMD` in a folder named `Microsoft VS Code\bin`. `Popen` without a shell ran that `.cmd` with `--wait` and the full path of a data folder named `数据 文件夹` as one argument. The outputs of v0.2-S12 steps 1 to 3 and v0.2-S13 steps 1 to 3 equal the lines that the design gives. The stand-in ran once in each S12 step and not at all in S13 steps 1 and 2. (b) Ctrl+C, sent in a console with no window while `edit` waited for a 6-second stand-in with no console, gave 130 after 0.24 s, with only the first line written. The stand-in ran on and finished. A plain `Popen.wait()` with no timeout woke only when the stand-in ended, 4.1 s after Ctrl+C, so the half-second steps of choice 5 are needed. (c) A stand-in that waited 1 s with no change got the prompt and then the check, at the end of the input. One that waited 2.2 s took the plain way. (d) All 7 rows of the table of choice 3 hold. `\` stays as written, a tab and U+3000 separate words, `a"b c"d` gives `ab cd`, `'""'` gives `EDITOR_NOT_A_COMMAND`, and a path in double quotation marks gives the escape message of TOML, which points to single ones. The 4 examples hold: 40 assertions and the 6 `# raises`. (e) With `NoDefaultCurrentDirectoryInExePath` unset, as on Troy's PC, a `stand-in-editor.cmd` in the current folder ran before the one on the PATH, which is the fourth risk. This Claude session sets that variable, so `shutil.which` skips the current folder here. Not run: Notepad, VS Code, and Ctrl+C at the prompt in a real console, because a harness cannot press a key in a console. The check in the process gives 130 for `KeyboardInterrupt` at the prompt, as for `add`. Windows 11 Notepad: on this PC, `shutil.which("notepad")` gives `C:\WINDOWS\system32\notepad.EXE`, and an image-file redirect starts the Store app Notepad 11.2609 in its place. Microsoft's Windows Insider blog of 2023-01-19 says only that a setting decides whether files open in new tabs or a new window. It does not say what the started process does when it hands a file over, or whether it is the window when none is open. Point 5 of the brief: in WSL Ubuntu 22.04 with Python 3.10.12, `shutil.which("notepad")` gives `None` on the PATH of a CI runner, so `edit` there gives `EDITOR_NOT_FOUND` and starts nothing. A test on CI cannot start the default. A stand-in with `#!` and the x bit was found and got a path with spaces and Chinese characters as one argument, and a file without the x bit was not found. A user on Linux without the key gets `EDITOR_NOT_FOUND`, whose message says how to name an editor. Note 5, not blocking: the item of v0.2-S19 says as a fact that in steps 1 and 2 the started `notepad.exe` is the window. It can say that this was not verified. If Notepad ends at once there too, option 1 of point D still checks after your edit, with the prompt as an extra line. Note 6, not blocking: choice 4 names only `%NAME%`. On the model, a data folder path with `&` and no space cut the path of a batch editor, and cmd.exe ran the rest of the path as a command. It also dropped `^`. In a path with a space, `&` and `^` stayed, and `%PATH%` was expanded. The ID never holds these characters, and the data folder is Troy's own choice, so this is not a security gap. Choice 4 can name `&`, `\|`, `<`, `>`, and `^` in a path with no space, and `%` in any path. Note 7, for the Test Manager: on Troy's PC the default finds the real Notepad. A test that runs `edit` without the key and without a PATH of its own would start Notepad and wait until someone closes it. Choice 10 has each test of the default set the PATH. The test plan can make that hold for every test that runs `edit`, for example with a fixture that sets the PATH to an empty folder, so a test that forgets the key gets `EDITOR_NOT_FOUND` on Windows too. A test of the current folder sets or deletes `NoDefaultCurrentDirectoryInExePath` itself, because Claude's sessions set it and Troy's terminal does not. |
| Changes an implemented interface only through the change flow | Pass | The PR adds only the two design files. Section 3 adds to `settings` what architecture 5.1 and the designs of F05 and F14 plan: a fifth field with a default, last, and one more key. `COMMANDS` gets its entry, which architecture 4 gives a command feature as its one change in `cli`. The requirements already name the setting, so no requirement changes, and the Architect reviews the additions here, as it reviewed F14's `dishes`. Point 3 of the brief: on Windows with Python 3.13.18, the whole suite, run alone on the model with `EDIT_COMMAND` after `ADD_COMMAND`, gave 646 passed and 4 skipped. An unchanged copy of main gave the same, and the 4 skips are main's cases for Linux only. F05-T10, F05-T11, F14-T23, F15-T02, F15-T03, F05-T02, F05-T03, F14-T22, F03-T30, and each help test that section 3 names pass. So do F07-T25 and F10-T21, the PT01 cases in `tests/`, on both copies. The help has 24 lines in both languages, with `edit ID` on line 12 and the second column after 24 columns. So no test-fix PR comes before the mock. Note 8, not blocking: the example of F05 design 2.3 writes `editor = 1` and expects `UNKNOWN_KEY`, which section 3 says stops holding after F16. A later `[docs]` PR of the Interface Designer can write `colour = 1` there, as F05-T11 does, so that every example of an approved design stays true. |
| The summary for Troy says what the design says, and lists every point Troy decides | Pass | The summary at the top of PR #123, at commit a0c239c, is the one in the brief, and it says what the design says. "What changes for you" gives Notepad by default, the key `editor` and how to quote a path, that `init` does not write the key, that `edit` never writes the recipe, and the line of the help. Items 1 to 4 are points A to D, each with its options and a recommendation with its reason. The count of point A holds: 2.2 and 3.2 have 20 messages, 6 of them copies and 1 whole from the prototype, which leaves 13. The four risks are those of choices 3 to 6. The first leaves out `init`, which only refuses when the data folder exists, so it says what Troy sees. The fourth holds on Troy's PC, which does not set `NoDefaultCurrentDirectoryInExePath`. The Architect found no other point for Troy to decide: notes 1 to 8 change nothing that Troy sees or chooses. The checks of troy-check's `summary.py`, run on the description, all pass. The Chinese part has 864 characters and the English part 1,836, within R22's 2,000. Both have the three parts in order and a recommendation in each of their 4 items, and neither holds an internal ID. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the 13 choices, section 3, and points A to D against the requirements, the architecture, ADR-0001, ADR-0008, ADR-0009, and ADR-0011, the designs of F05, F07, F14, and F15, the F16 prototype, the v0.2 test plan, and the six points of the brief. The two files have the same 17 headings and 124 table lines with the same cells, and 10 code blocks, each equal to its mirror, with no control or invisible character. The 7 `python` blocks parse. On a copy of main's `src/` outside the repository, with Python 3.13.18 on Windows, the Architect built a model of sections 2 and 3 and ran the 4 examples on fresh copies of `tests/data/example/`: all 40 assertions and the 6 `# raises` hold. Items 1, 5, and 6 give the runs, the start time, and the whole suite. Not run: Notepad, VS Code, a real console with keys, the model on Linux, and the PT01 version test. Notes 1 to 8 do not block. | Approved. The main session puts points A to D to Troy when Troy approves this design (R18). Under option 1 of point B and option 1 of point C, the Architect's `[docs]` PR comes before the F16 mock PR. It records point B in architecture 6 with an ADR. It records point C in architecture 4 and 8 with an ADR, naming the start of the editor and the reading of `PATH`, `PATHEXT`, and `NoDefaultCurrentDirectoryInExePath` by `shutil.which`. It also adds to architecture 6 the row of an editor that cannot be found, cannot start, or fails (item 2), and the editor to the `Settings` row of architecture 5.2. Option 2 of point B changes the prototype through the requirement change flow and needs no ADR. Option 2 of point C still needs an ADR, for architecture 5.2 and 8. The Interface Designer can take notes 1, 2, 3, 5, and 6 in a revision, or leave them. Note 4 waits for the later `[refactor]` PR, and note 8 for a later `[docs]` PR. For the Test Manager's brief (point 6 of the brief): the design settles the F16 points of "Where the plan waits for the designs". The model gives the first lines of v0.2-S12, the usage message of v0.2-S13 step 2, and the split of `editor` that the design gives. The list of section 3 is complete: v0.2-S12 to v0.2-S16, v0.2-S19 step 3, and the F16 point. As for F14 and F15, the update can come with the F16 test plan, before the version tests PR. Steps 3 of v0.2-S15 and v0.2-S16 give an empty standard input and expect the prompt, because the 1-second stand-in that changes nothing gets it. Note 7 goes to the same brief. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-21 | First draft. |
| 1.0 | 2026-11-21 | Approved by Troy. |
