---
troy-doc: "F08-design"
lang: "en"
version: "1.0"
updated: "2026-11-13"
status: "Approved by Troy on 2026-11-13"
mirror: "design.zh-CN.md"
---

# F08 Start a data folder: interface design

## 1. Feature

- ID and name: F08 Start a data folder
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: F05
- Soft dependencies: F03, F04, F07

## 2. Interfaces

F08 builds the command module `init` in `src/recipe_menu/commands/init/` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.commands.init` exports one name, `INIT_COMMAND` (2.1), and its `__init__.py` lists it in `__all__`. The command that you type is `recipe-menu init` (2.2). Its messages live in `src/recipe_menu/commands/init/messages.py`, and the texts of the example files live in `src/recipe_menu/commands/init/_example.py`. Both files are internal to the module (architecture 8). The other files behind it are the Developer's choice. F08 also adds the first write to `datafile`: `create_data_folder` and its result, a `Creation` with a `CreationOutcome` (section 3). In its mock PR, F08 adds `INIT_COMMAND` to `COMMANDS` in `src/recipe_menu/cli/_commands.py`, before `CHECK_COMMAND`. That entry is the only change that a command feature makes in `cli` (architecture 4, F05 design 2.9). The F08 prototype `docs/prototypes/F08-init.md` shows the command.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F08 gives |
| --- | --- |
| `recipe-menu init` creates the data folder with the settings, the catalog and the pantry of the example data, the example recipe `tomato-egg`, and the empty folders `menus/` and `shopping/`. | `recipe-menu init` (2.2). Its `run` in `INIT_COMMAND` (2.1) passes the folders `recipes/`, `menus/`, and `shopping/` and the four texts of choice 2 to `create_data_folder` (3.2). |
| The settings get the language that `init` runs in. | The `language` line of `settings.toml` holds `context.lang` (choice 6). |
| It refuses when the folder already holds files. | `CreationOutcome.HOLDS_FILES` and `CreationOutcome.NOT_A_FOLDER` (3.1), by the rules of choice 4. `init` writes `ALREADY_HOLDS_FILES` or `IS_A_FILE` and exits with code 1 (2.2). |
| `check` reports no errors on what it creates. | The files are those of the example data, which `tests/data/example/` also holds (choice 2). On them, `check` reports `No errors. No warnings.` with 1 recipe and 0 week menus (F07 design section 2, v0.1-S01). |
| `init` creates a file only where none exists, and refuses otherwise ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | `create_data_folder` writes only into a data folder that is missing or empty, and it opens each file in exclusive mode (3.2, [architecture 6](../../architecture.md#6-error-handling)). |
| No file is left half written after Ctrl+C (architecture 6). | After a failure or an interruption, `create_data_folder` removes what it created (choice 5). |

These rules hold for every interface below:

- `init` imports only `app`, `lang`, `text`, `datafile`, and `settings` from the package. Its row of architecture 3 allows them, and it needs none of the others. The additions to `datafile` import only `lang` and `text` (architecture 3 and [4](../../architecture.md#4-dependency-rules)).
- `init` reaches the disk only through `create_data_folder`, the one interface of F08 that lists, creates, or removes anything. Only `datafile` opens data files ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). `init` reads no data file. `cli` reads `settings.toml` at start when the data folder is a folder (F05 design 2.10). `init` writes only to `context.out` and `context.err`. It reads nothing of the outside world itself, and it keeps no state.
- A refusal or a failure on the disk is a value, never an exception. `create_data_folder` turns each `OSError` into a `Problem` in its result (architecture 6). The exceptions in the Errors tables below come from wrong calls, which are bugs.
- `INIT_COMMAND` is a frozen `Command` (F05 design 2.5). `Creation` is a frozen dataclass with `slots=True`, and `CreationOutcome` is an enum (architecture 8). They are helper values, as F03 added `Severity` and F05 added `FolderUse`.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F08 interface has a performance target. PT01 does not time `init` ([requirements 7.1](../../requirements.md#71-performance-targets)). `init` creates at most the data folder, the missing folders above it, three folders, and four files. `run` and `create_data_folder` call single-purpose internal functions (R04).

The design makes these choices. 2.2 and 3.2 give their rules.

1. **`init` comes first in the help.** `COMMANDS` holds `INIT_COMMAND` and then `CHECK_COMMAND`, in the order of F05 design section 2: init, check, list, show, search, menu new, menu show, and shop. The widest first cell is still `--data FOLDER` or `--data 文件夹`, of 13 columns, so the second column starts after 18 columns, as in F07 design choice 1. The help gets one more line, 15 in all. With the eight commands of v0.1, it gives the two help outputs of the F05 prototype (v0.1-S19). These are the commands of `recipe-menu --help` and of `recipe-menu --help --lang zh`:

   ```text
   Commands:
     init            Create the data folder with example data.
     check           Check every data file for mistakes.
   ```

   ```text
   命令：
     init            创建数据文件夹和示例数据。
     check           检查每个数据文件有没有错误。
   ```

2. **The example files are texts in the code.** `_example.py` holds four string constants. Each is the text of one code block of `docs/prototypes/example-data.md`, with a line break at the end of each line: `settings.toml`, `catalog.toml`, `pantry.toml`, and `recipes\tomato-egg.toml`. The text of the settings is a template for its `language` line (choice 6). `init` writes the texts through `datafile`, as architecture 2 plans: "Text that the code builds from templates, written through `datafile`." The texts do not ship as data files in the package. Such files would need `importlib.resources`, a read at run time that can fail, and an entry in `pyproject.toml` that is easy to miss. So `pyproject.toml` does not change, and R16 has nothing to flag. The texts hold no backslash, so a Python string holds each one as it is written. `tests/data/example/` holds the same four texts, beside six more recipes and a menu (architecture 10). The two copies are on purpose. The example folder is test data, which the Developer never edits (R08), and the tests of F03 to F07 read it. The texts of `init` are source, which the Developer owns. A test of F08 runs `init` and compares each file that it wrote, byte for byte, with the same file of `tests/data/example/`, read as UTF-8 with LF line ends (2.2, example). v0.1-S01 compares the files with `example-data.md` itself. So a change to one copy alone fails a test.
3. **`datafile` writes the files.** Architecture 3 gives writing a file to `datafile`, and architecture 8 lets only `datafile` open data files. F08 is the first feature that writes, so it adds `create_data_folder` (3.2). It is all that `init` needs from the disk: it looks at the data folder, creates the folders and the files, and removes them again after a failure. `init` passes the paths that `DataFolder` gives, and the texts. So `datafile` knows no example data, and `init` knows no file name (architecture 5.2). `create_data_folder` takes the folders and the files as arguments, so a test can make it fail at any step, such as with a file name that no system accepts (3.2, example).
4. **What "holds files" means.** `create_data_folder` looks at the data folder before it creates anything (3.2). The first case that applies decides:
   - The data folder is a folder. `init` lists it, and a listing that fails, such as when access is denied, is a failure (choice 5). An entry of any kind makes `init` refuse with `ALREADY_HOLDS_FILES`: a file, a folder, an empty folder such as `menus\` alone, a link, or a hidden or system file such as `.keep` or `desktop.ini`. So `init` never mixes its files with yours, and it never has to decide which entry to keep (open question B). With no entry, `init` writes into the folder, so you can make the folder in Explorer first.
   - Something other than a folder is at the path, such as a file, or a link that leads to no folder. `init` refuses with `IS_A_FILE`.
   - Nothing is at the path. `init` creates the data folder and each missing folder above it, from the top down. So `init --data D:\OneDrive\Food\recipe-menu` creates `Food` and `recipe-menu` when only `D:\OneDrive` exists (open question C).
5. **All or nothing.** `create_data_folder` creates the data folder when it is missing, then `recipes\`, `menus\`, and `shopping\`, and then `settings.toml`, `catalog.toml`, `pantry.toml`, and `recipes\tomato-egg.toml`. It opens each file in exclusive mode, so it never overwrites a file (architecture 6). The first `OSError` stops it. It then removes what it created, the last first, and `init` reports the error and `init changed nothing.` with exit code 1. A file counts as created from the moment that it is opened, so a file that is half written is removed too. Nothing that existed before is removed: a data folder that was empty stays, and so do the folders above it. Ctrl+C runs the same removal, and then `cli` exits with 130 and writes nothing more (F05 design 2.10). A removal can fail too, such as when another program holds a new file open. `init` then writes `LEFT_BEHIND`, which asks you to empty the data folder and run `init` again. The removal cannot run when the process is killed, as when you close the terminal window, or when the PC loses power. Two cases of Ctrl+C act like a killed process. A Ctrl+C after the system has created a folder or a file, but before the call has recorded it, such as inside `open`, leaves that entry. A second Ctrl+C during the removal stops the removal. `cli` still exits with 130 in both cases and writes nothing more. After any of these cases, the data folder can keep what `init` created. `init` refuses such a folder when it holds an entry, and `check` names the files that it lacks, so you delete the folder and run `init` again.
6. **The settings and their line.** `settings.toml` is the example's text, with the value of `context.lang` in its `language` line: `language = "en"` or `language = "zh"`, followed by the same spaces and comment. For that file, `read_settings` gives `Settings(context.lang)`: the language of `init`, lunch and dinner, and 2 servings. The line of `settings.toml` in the output describes that value, as F05 design section 2 plans: the name of the language, `and_list` of the `Meal.label` of its meals, and its servings. The language that the line names is always the language of the output, because `init` writes the language that it runs in. `context.lang` comes from `--lang`, else English, because a missing or empty data folder has no settings (F05 design 2.10, step 3).
7. **The counts.** The lines of the catalog and the pantry show the counts of the example texts: 6 categories, 22 ingredients, and 5 tags, and 5 ingredients in the pantry. They are constants beside the texts in `_example.py`, so `init` reads none of the files that it wrote. Reading them back would give `run` a branch for a file with an error, which no test can reach. A test of F08 reads the new folder with `read_catalog` and `read_pantry` and compares their counts with the output (2.2, example). The counts use `Plural` messages, so a later change of the example data keeps the English right.
8. **Streams, codes, and paths.** The output for a new folder goes to `context.out` with exit code 0. A refusal or a failure goes to `context.err` with exit code 1 (architecture 6). The first line and the refusals name the data folder by its full path, `str(context.folder.root)`, as F05's `NO_DATA_FOLDER` does. The table of the output names each file and folder relative to the data folder, with the system's separator, and a folder ends with the separator: `menus\` on Windows and `menus/` on Linux. A failure names the file or the folder that failed by its full path, `str(context.folder.root / problem.file)`. That departs from this rule of architecture 6: "A problem names its file relative to the data folder, with the system's separator." The rule fits a data folder that you use every day, but not one that you just named on the command line. A failure at the data folder itself, or at a folder above it, also has the file `Path(".")`, which would show as `.`. The `Problem` still holds its file relative to the data folder (3.2), and only the line that `init` writes gives the full path. Troy decides the departure as open question D. After Troy approves it, the Architect adds the case to architecture 6 in a `[docs]` PR.
9. **A folder name that ends with spaces or dots, other than a single dot.** On Windows, the system drops every trailing space and dot from the last part of a path when it opens or creates the path. From a part in the middle, it drops one trailing dot and keeps trailing spaces (F05 review, PR #38). So `--data "D:\x\recipe-menu "` names the folder `D:\x\recipe-menu`, but `root / "recipes"` keeps the space in a part in the middle, so it names a folder whose parent does not exist. The same holds for two spaces, `..`, ` .`, and `. `. A single dot works: with `--data "D:\x\recipe-menu."`, `init` creates `D:\x\recipe-menu` with every file and exits with 0, its first line names `D:\x\recipe-menu.`, and every later command with that value uses the same folder. F08 needs no change to F05 to keep the other values safe, because choice 5 leaves every folder as it was:
   - When `D:\x\recipe-menu` is missing, Windows creates it for the data folder. The next step creates `recipes`, whose path keeps the space, and fails. `init` removes the new folder and each folder above it that it created. It reports `D:\x\recipe-menu \recipes` with `FOLDER_CREATE_ERROR`, whose reason is the system's, such as "The system cannot find the path specified", and exits with 1.
   - When `D:\x\recipe-menu` exists, its listing works, because the listing uses the data folder's own path, whose last part loses its space. A folder with an entry gives `ALREADY_HOLDS_FILES`, which names the folder with its space. An empty folder fails at `recipes`, as in the first bullet, and the failure ends with `init changed nothing.` Both exit with 1.

   These messages are hard to understand. `init` cannot create `recipes` in a folder that you see in Explorer, or it refuses a folder whose trailing space you cannot see. Open question A proposes a change to F05 under which such a value names the folder that Windows uses. `init` then creates that folder as for any other value.
10. **No home folder is out of scope.** On Windows with none of `USERPROFILE`, `HOMEDRIVE`, and `HOMEPATH`, `Path.home()` raises `RuntimeError`, which no message covers. `cli` calls it by rule 4 of F05 design 2.10 before it runs any command, so `init` with the default data folder ends with Python's traceback. F08 leaves it out of scope: the error comes from F05's `cli`, it hits every command alike, and F05's next design revision covers it. `init --data FOLDER` and `RECIPE_MENU_DATA` need no home folder, because `cli` asks for it only when rule 4 needs it.

The folder that `init` creates has no warning, so v0.1-S06 holds with the texts of F07 (F07 design section 2). The F07 prototype "A syntax mistake" lacks the warning that the example folder gives. That is a separate question for Troy, and it does not change F08.

Troy decides these four open questions when Troy approves this design (R18). None of them changes a requirement. Question A changes F05's design, and question D adds a case to architecture 6.

- **A. A folder name that ends with spaces or dots, on Windows.** The Architect raised it in the F05 review (PR #38). A single trailing dot already works (choice 9), so the question matters only for a trailing space, for two or more dots, and for a mix of spaces and dots. The options:
  1. `cli` applies `os.path.abspath` to the data folder on Windows. It drops the trailing spaces and dots of the last part, as Windows does, so every command uses the folder that Windows uses. It also collapses `..`, so F05's test of `x/../y` changes on Windows. A narrower form drops only the trailing spaces and dots of the last part.
  2. `cli` looks at `os.path.join(root, "")`, which keeps the space. Every command other than `init` then reports such a folder as missing, and `init` fails as choice 9 says.
  3. No change. Choice 9 stays as it is.

  Options 1 and 2 change rule 4 or step 2 of F05 design 2.10, an implemented interface. So either one goes through the change flow: a revision of F05's design, its tests, and its code. Recommendation: option 1, as the Architect prefers, in F05's next revision, which also covers choice 10. F08's own PRs need no change either way.
- **B. "Holds files" counts every entry.** Requirement F08 says that `init` "refuses when the folder already holds files". Choice 4 counts every entry, also an empty folder such as `menus\` and a hidden file. The options:
  1. Every entry counts. A data folder is either empty or refused, and `init` mixes nothing.
  2. Only files count, anywhere in the folder. `init` would then reuse the empty folders that it finds. It would also have to say what happens with an entry named like one of its files, such as an empty folder named `settings.toml`.

  Recommendation: option 1.
- **C. Missing folders above the data folder.** The options:
  1. `init` creates them, and removes them again after a failure (choice 5). You can name a new folder deep in OneDrive in one step.
  2. `init` refuses, and says that the folder above is missing. A typo above the data folder, such as `D:\OneDirve\recipe-menu`, then gives an error rather than a new tree of folders.

  Recommendation: option 1. The first line of the output names the full path, so you see where `init` created the folder.
- **D. A failure names its file by its full path.** Architecture 6 says that a problem names its file relative to the data folder, and that other messages name a file or a folder by its full path. The first line of a failure is the file of a `Problem`, and 2.2 writes it as a full path (choice 8). The options:
  1. The full path, as 2.2 gives it. You see where `init` failed, and a failure at the data folder itself shows the folder. After Troy approves it, the Architect adds the case to architecture 6 in a `[docs]` PR.
  2. The path relative to the data folder, as architecture 6 says now. A failure at `recipes` shows `recipes`, and a failure at the data folder or at a folder above it shows `.`. The first line of a failure and its example in 2.2 change.

  Recommendation: option 1, which the Architect agrees with.

Troy also approves the new Chinese texts of 2.2 and 3.2 with this design (R18).

These later features are meant to build on F08. Their own designs decide the details.

- F11's `menu new` and F13's `shop` add their own writes to `datafile` (architecture 3). `menu new` creates one file in exclusive mode, and `shop` replaces one file through a temporary file in the same folder (architecture 6). They can share the internals of `create_data_folder` that write a file, and its messages for a failure (3.2). The F11 prototype names an existing menu file by its full path, as `init` names its data folder.
- F15's `add` writes a new recipe file in exclusive mode, as `menu new` does.
- The scenarios v0.1-S01 to v0.1-S04, v0.1-S06, v0.1-S16, and v0.1-S20 start with the folder that `init` creates.

troy-mode's flow has one mock PR and one implementation PR. The mock (PR 3) holds `src/recipe_menu/commands/init/__init__.py`, `messages.py`, and an internal file for `run`, and the entry in `src/recipe_menu/cli/_commands.py`. In `datafile`, it holds the new exports in `__init__.py`, an internal file for `CreationOutcome`, `Creation`, and `create_data_folder`, and the six messages in `messages.py`. It defines every message, `INIT_COMMAND` with all its fields, and `CreationOutcome` with its members. Its `Creation` has the three fields without the checks of 3.1. Its `create_data_folder` touches nothing and gives `Creation(CreationOutcome.CREATED)`, and its `run` writes nothing and gives 0. So a new test of the output, the files, a refusal, or a failure fails against the mock (R09). Some tests pass against the mock and so break R09: a test that checks only that a refused folder keeps its entries, only that a failure leaves nothing, or only the help. So does a test that checks only the fields of `INIT_COMMAND`, the values of `CreationOutcome`, the defaults or the equality of a valid `Creation`, or `init extra` or `init --tag`, the last two of which `cli` rejects before it runs `init`. Each such test must also check something that the mock gets wrong, such as the output, the outcome, or a check of 3.1. The mock changes 7 files, more than R03's 5, so its description gives a soft-limit reason: the tests reach `create_data_folder` both directly and through `init`, so both modules come in one stage, as in F05's mock. The implementation (PR 5) holds the texts in `_example.py`, `run`, and `create_data_folder`, in 3 files.

### 2.1 `INIT_COMMAND`

- Module: init
- Purpose: The description of the `init` command. `cli` reads it to parse the command line, write the help, decide what it checks before the command runs, and run the command (F05 design 2.5 and 2.9). Its `run` creates the data folder and writes the output of 2.2.

Signature:

```python
INIT_COMMAND: Final[Command]

# Its fields, as F05 design 2.5 defines them:
#   words = ("init",)
#   help_line = INIT_HELP
#   run: Callable[[Context, Arguments], int]
#   argument = None
#   options = ()
#   folder = FolderUse.CREATE
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `words` | A tuple of `str` | `("init",)`. | None |
| `help_line` | `Message` | `INIT_HELP`: "Create the data folder with example data." and "创建数据文件夹和示例数据。", the line of the F05 prototype's help. | No placeholders. |
| `run` | A callable that takes a `Context` and the `Arguments` and gives an `int` | Creates the data folder and writes the output of 2.2. | Gives 0 or 1. |
| `argument` | `None` | `init` takes no argument. | None |
| `options` | An empty tuple | `init` has no options of its own. | None |
| `folder` | `FolderUse` | `FolderUse.CREATE`: `cli` runs `init` whether or not the data folder exists, and whether or not its settings have an error (F05 design 2.5). | None |
| `context` | `Context` | What `run` gets from `cli` (F05 design 2.4). | `run` uses only `context.lang`, `context.folder`, `context.out`, and `context.err`. It uses neither `context.settings` nor `context.today`. |
| `arguments` | `Arguments` | What the command line gives `init` (F05 design 2.6). | Empty, because `init` declares no argument and no option, so `cli` lets no value through. `run` does not read it. |

- Return value: `INIT_COMMAND`, a `Command`.
  - `INIT_COMMAND.usage` is `init` in both languages, so the help shows `init`, and a usage error quotes `recipe-menu init`.
  - `INIT_COMMAND.run(context, arguments)` calls `create_data_folder` once, writes the output of 2.2 in `context.lang`, and gives 0 when it created the data folder, and 1 otherwise.

Errors: None. `run` never raises for a refusal or a failure on the disk. It raises no `UsageError`, because `init` takes no argument value. An exception that interrupts it, such as `KeyboardInterrupt`, goes on to `cli` after `create_data_folder` removed what it created (choice 5).

- Side effects: Those of 2.2.
- Performance target: None

Example:

In this example, `home` is an empty temporary folder ([architecture 10](../../architecture.md#10-test-setup)). The context holds settings in English, and `run` writes the settings in the language of the context. The help comes from `COMMANDS`, which holds `INIT_COMMAND` and `CHECK_COMMAND` after F08.

```python
import io
from datetime import date

from recipe_menu.app import Arguments, Context, FolderUse
from recipe_menu.cli import main
from recipe_menu.commands.init import INIT_COMMAND
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings

assert INIT_COMMAND.words == ("init",)
assert INIT_COMMAND.usage == BiText("init", "init")
assert INIT_COMMAND.help_line.render(Lang.EN) == "Create the data folder with example data."
assert INIT_COMMAND.help_line.render(Lang.ZH) == "创建数据文件夹和示例数据。"
assert (INIT_COMMAND.argument, INIT_COMMAND.options) == (None, ())
assert INIT_COMMAND.folder is FolderUse.CREATE

out, err = io.StringIO(), io.StringIO()
folder = DataFolder(home / "direct")
context = Context(Lang.ZH, folder, Settings(Lang.EN), out, err, date(2026, 11, 10))
assert INIT_COMMAND.run(context, Arguments()) == 0
assert err.getvalue() == ""
assert out.getvalue().splitlines()[0] == f"已创建数据文件夹 {folder.root}："
assert read_settings(folder) == (Settings(Lang.ZH), ())


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
assert len(english) == 15
assert english[4:7] == [
    "Commands:",
    "  init            Create the data folder with example data.",
    "  check           Check every data file for mistakes.",
]
chinese = help_lines("--help", "--lang", "zh")
assert chinese[5:7] == [
    "  init            创建数据文件夹和示例数据。",
    "  check           检查每个数据文件有没有错误。",
]
```

### 2.2 `recipe-menu init`

- Module: init
- Purpose: The command that starts a data folder ([requirements 3](../../requirements.md#3-how-users-interact-with-it), flow 1, and [4](../../requirements.md#4-features)). It creates the data folder with the settings in its language, the catalog, the pantry, the example recipe `tomato-egg`, and the empty folders `menus/` and `shopping/`. It refuses a folder that already holds files. The F08 prototype shows it.

Signature:

```text
recipe-menu init [--lang en|zh] [--data FOLDER]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `--lang` | `en` or `zh` | The language of the output and of the new settings. | As F05 design 2.10 gives it. Without the option, English, because a missing or empty data folder has no settings. A refusal speaks the language of the folder's settings when they name one. |
| `--data` | A folder | The data folder to create. | As F05 design 2.10 gives it. Without the option, `RECIPE_MENU_DATA`, else `~/recipe-menu`. The folder may be missing, and so may the folders above it. |
| `--help` | A flag | Shows the help (choice 1) and does not run `init`. | None |

`init` makes one call, `create_data_folder(folder, folders, files)`, with `folder = context.folder` and these folders and files, in this order:

| Kind | Path | Text |
| --- | --- | --- |
| Folder | `folder.recipes` | None |
| Folder | `folder.menus` | None |
| Folder | `folder.shopping` | None |
| File | `folder.settings` | The block `settings.toml` of `example-data.md`, with the value of `context.lang` in place of `en` in its `language` line. |
| File | `folder.catalog` | The block `catalog.toml` of `example-data.md`. |
| File | `folder.pantry` | The block `pantry.toml` of `example-data.md`. |
| File | `folder.recipe_file("tomato-egg")` | The block `recipes\tomato-egg.toml` of `example-data.md`. |

Each text is the lines of its block, each ended by LF. So `recipe-menu init --lang zh` writes this `settings.toml`:

```toml
# recipe-menu settings
language = "zh"              # "en" or "zh"
meals = ["lunch", "dinner"]  # from "breakfast", "lunch", and "dinner", in this order
servings = 2                 # the servings of a dish that gives none
```

- Return value: The exit code, and the output on its stream:

| Exit code | When | Stream |
| --- | --- | --- |
| 0 | `create_data_folder` gave `CREATED`. | The output stream: the lines of a new folder. |
| 1 | It gave `HOLDS_FILES`, `NOT_A_FOLDER`, or `FAILED`. | The error stream: the refusal or the failure. Nothing goes to the output stream. |

A new folder gives these lines, each ended by a line break:

1. `CREATED`, with `folder`.
2. The six rows of the table below, as `format_table(rows, indent=2, gap=4)` lays them out (F02 design 2.9). The first column is 23 columns wide, the width of `recipes\tomato-egg.toml`, so the second column starts after 29 columns in both languages, as the F08 prototype shows.
3. An empty line.
4. `NEXT_STEP`, with `recipes`.

| First cell | Second cell |
| --- | --- |
| `settings.toml` | `SETTINGS_LINE`, with `language`, `meals`, and `servings` |
| `catalog.toml` | `CATALOG_LINE`, with `categories`, `ingredients`, and `tags` |
| `pantry.toml` | `INGREDIENT_COUNT`, picked by 5, with `count` set to 5 |
| `recipes\tomato-egg.toml` | `EXAMPLE_RECIPE` |
| `menus\` | `EMPTY_FOLDER` |
| `shopping\` | `EMPTY_FOLDER` |

Each first cell is `str(folder.relative(path))` for its path in the table of the call, and a folder gets `os.sep` at its end. So Linux shows `recipes/tomato-egg.toml` and `menus/`.

A refusal is one line: `ALREADY_HOLDS_FILES` for `HOLDS_FILES`, or `IS_A_FILE` for `NOT_A_FOLDER`, each with `folder`.

A failure is three lines. In this case on Windows, you may read the folder `D:\Shared\recipe-menu`, but not create anything in it:

```text
PS> recipe-menu init --data D:\Shared\recipe-menu
D:\Shared\recipe-menu\recipes
  The folder cannot be created: access is denied.
init changed nothing.
PS> $LASTEXITCODE
1
```

The first line is the full path of the problem's file, `str(context.folder.root / problem.file)`. For the file `Path(".")`, that is the data folder itself. Architecture 6 names the file of a problem relative to the data folder, so this line departs from it (choice 8 and open question D). The second line is two spaces and `problem.text(context.lang)`. The third line is `CHANGED_NOTHING` when the result's `left` is empty, and `LEFT_BEHIND` with `folder` otherwise.

The messages of `init` are these. `SERVINGS_PER_DISH`, `CATEGORY_COUNT`, `INGREDIENT_COUNT`, and `TAG_COUNT` are `Plural` values (F02 design 2.4), each picked by its `count`. Their form "for more" is the form for every count other than 1.

| Name | English | Chinese |
| --- | --- | --- |
| `INIT_HELP` | `Create the data folder with example data.` | `创建数据文件夹和示例数据。` |
| `CREATED` | `Created the data folder {folder}:` | `已创建数据文件夹 {folder}：` |
| `SETTINGS_LINE` | `{language}, {meals}, {servings}` | `{language}，{meals}，{servings}` |
| `ENGLISH` | `English` | `英文` |
| `CHINESE` | `Chinese` | `中文` |
| `SERVINGS_PER_DISH`, for one | `{count} serving per dish` | `每道菜 {count} 份` |
| `SERVINGS_PER_DISH`, for more | `{count} servings per dish` | `每道菜 {count} 份` |
| `CATALOG_LINE` | `{categories}, {ingredients}, {tags}` | `{categories}，{ingredients}，{tags}` |
| `CATEGORY_COUNT`, for one | `{count} category` | `{count} 个分类` |
| `CATEGORY_COUNT`, for more | `{count} categories` | `{count} 个分类` |
| `INGREDIENT_COUNT`, for one | `{count} ingredient` | `{count} 种食材` |
| `INGREDIENT_COUNT`, for more | `{count} ingredients` | `{count} 种食材` |
| `TAG_COUNT`, for one | `{count} tag` | `{count} 个标签` |
| `TAG_COUNT`, for more | `{count} tags` | `{count} 个标签` |
| `EXAMPLE_RECIPE` | `an example recipe in both languages` | `一个中英双语的示例菜谱` |
| `EMPTY_FOLDER` | `empty` | `空` |
| `NEXT_STEP` | `Next: add your recipes to {recipes}, then run "recipe-menu check".` | `下一步：把你的菜谱加进 {recipes}，然后运行“recipe-menu check”。` |
| `ALREADY_HOLDS_FILES` | `{folder} already holds files. init changed nothing.` | `{folder} 里已经有文件。init 没有做任何修改。` |
| `IS_A_FILE` | `{folder} is a file, not a folder. init changed nothing.` | `{folder} 是一个文件，不是文件夹。init 没有做任何修改。` |
| `CHANGED_NOTHING` | `init changed nothing.` | `init 没有做任何修改。` |
| `LEFT_BEHIND` | `init could not remove all that it created. Empty {folder}, then run "recipe-menu init" again.` | `init 没能删除它创建的全部内容。请清空 {folder}，然后再运行“recipe-menu init”。` |

The values of the placeholders are these. `settings` is `Settings(context.lang)`, the value that `read_settings` gives for the new file (choice 6).

| Placeholder | Value |
| --- | --- |
| `folder` | `str(context.folder.root)`, the data folder's full path. |
| `language` | `ENGLISH` for `Lang.EN` and `CHINESE` for `Lang.ZH`, picked by `settings.language` and given as a `BiText`. |
| `meals` | `and_list` of the `Meal.label` of each meal of `settings.meals`: "lunch and dinner" and "午餐和晚餐". |
| `servings` | `SERVINGS_PER_DISH`, picked by `settings.servings`, with `count` set to it, as a `BiText`: "2 servings per dish" and "每道菜 2 份". |
| `categories`, `ingredients`, and `tags` | `CATEGORY_COUNT`, `INGREDIENT_COUNT`, and `TAG_COUNT`, picked by 6, 22, and 5, each with `count` set to its number, as a `BiText` (choice 7). |
| `count` | The number of each `Plural`. |
| `recipes` | `str(folder.relative(folder.recipes))` and `os.sep`: `recipes\` on Windows and `recipes/` on Linux. |

With these messages, the lines of the F08 prototype follow in both languages, such as `6 categories, 22 ingredients, 5 tags` and `6 个分类，22 种食材，5 个标签`.

Errors:

| Error | When |
| --- | --- |
| Exit code 1, with `ALREADY_HOLDS_FILES` on the error stream | The data folder is a folder with an entry (choice 4). Every entry keeps its bytes and modification time (v0.1-S03). |
| Exit code 1, with `IS_A_FILE` on the error stream | Something other than a folder is at the data folder's path (choice 4). |
| Exit code 1, with the three lines of a failure on the error stream | An `OSError` stopped `create_data_folder` (3.2). |
| Exit code 2, with `TOO_MANY_ARGUMENTS` and then `RUN_HELP_FOR_COMMANDS`, such as `Unexpected argument "extra". Write "recipe-menu init".` | A word follows `init`. `cli` reports it before it runs `init` (F05 design 2.10). |
| Exit code 2, with `UNKNOWN_OPTION` in its form for no options and then `RUN_HELP_FOR_OPTIONS`, such as `"init" has no option "--tag". It has no options of its own.` | An option other than the four global options. |
| Exit code 2, with the errors of `--lang` and `--data` of F05 design 2.10 | A global option breaks its rule. |
| Exit code 130 | Ctrl+C. `create_data_folder` removes what it created, and `cli` writes nothing more (choice 5). |

- Side effects: `cli` looks at the data folder, and it reads `settings.toml` when the data folder is a folder (F05 design 2.10). `init` then calls `create_data_folder` once. That call lists the data folder, creates the folders and the files of the table of the call, and removes them again after a failure (3.2). `init` writes its lines to the output stream or the error stream. A refusal creates and changes nothing.
- Performance target: None

Example:

In this example, `home` is an empty temporary folder, and `example` is the folder `tests/data/example/` of the repository ([architecture 10](../../architecture.md#10-test-setup)). The first run creates the default data folder. The next runs check it, refuse it, create a data folder in Chinese, and try the cases of choice 4 and a mistake on the command line.

```python
import io
import os
from datetime import date
from pathlib import Path

from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Settings, read_settings


def run(*argv: str) -> tuple[int, list[str], list[str]]:
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ={},
        home=home,
        today=date(2026, 11, 10),
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue().splitlines(), err.getvalue().splitlines()


def same_text(made: Path, source: Path) -> bool:
    return made.read_bytes() == source.read_text(encoding="utf-8").encode("utf-8")


folder = DataFolder(home / "recipe-menu")
recipe = str(Path("recipes", "tomato-egg.toml"))
menus, shopping = "menus" + os.sep, "shopping" + os.sep
assert run("init") == (
    0,
    [
        f"Created the data folder {folder.root}:",
        "  settings.toml              English, lunch and dinner, 2 servings per dish",
        "  catalog.toml               6 categories, 22 ingredients, 5 tags",
        "  pantry.toml                5 ingredients",
        f"  {recipe}    an example recipe in both languages",
        f"  {menus}                     empty",
        f"  {shopping}                  empty",
        "",
        f'Next: add your recipes to recipes{os.sep}, then run "recipe-menu check".',
    ],
    [],
)
assert sorted(entry.name for entry in folder.root.iterdir()) == [
    "catalog.toml",
    "menus",
    "pantry.toml",
    "recipes",
    "settings.toml",
    "shopping",
]
assert [entry.name for entry in folder.recipes.iterdir()] == ["tomato-egg.toml"]
assert list(folder.menus.iterdir()) == list(folder.shopping.iterdir()) == []
for name in ("settings.toml", "catalog.toml", "pantry.toml"):
    assert same_text(folder.root / name, example / name)
assert same_text(folder.recipe_file("tomato-egg"), example / "recipes" / "tomato-egg.toml")
assert read_settings(folder) == (Settings(Lang.EN), ())
catalog, problems = read_catalog(folder)
assert catalog is not None and problems == ()
assert (len(catalog.categories), len(catalog.ingredients), len(catalog.tags)) == (6, 22, 5)
pantry, problems = read_pantry(folder, catalog)
assert pantry is not None and problems == () and len(pantry.ingredients) == 5

assert run("check") == (
    0,
    [
        "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
        "",
        "No errors. No warnings.",
    ],
    [],
)
assert run("init") == (1, [], [f"{folder.root} already holds files. init changed nothing."])

other = home / "zh"
code, lines, err = run("init", "--lang", "zh", "--data", str(other))
assert (code, err) == (0, [])
assert lines[0] == f"已创建数据文件夹 {other}："
assert lines[1:4] == [
    "  settings.toml              中文，午餐和晚餐，每道菜 2 份",
    "  catalog.toml               6 个分类，22 种食材，5 个标签",
    "  pantry.toml                5 种食材",
]
assert lines[-1] == f"下一步：把你的菜谱加进 recipes{os.sep}，然后运行“recipe-menu check”。"
english_settings = folder.settings.read_bytes()
chinese_settings = (other / "settings.toml").read_bytes()
assert chinese_settings == english_settings.replace(b'language = "en"', b'language = "zh"')
assert run("check", "--data", str(other)) == (
    0,
    ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"],
    [],
)

empty = home / "empty"
empty.mkdir()
assert run("init", "--data", str(empty))[0] == 0
only_menus = home / "only-menus"
(only_menus / "menus").mkdir(parents=True)
hidden = home / "hidden"
hidden.mkdir()
(hidden / ".keep").write_text("", encoding="utf-8")
for full in (only_menus, hidden):
    refusal = f"{full} already holds files. init changed nothing."
    assert run("init", "--data", str(full)) == (1, [], [refusal])
assert [entry.name for entry in only_menus.iterdir()] == ["menus"]
notes = home / "notes.txt"
notes.write_text("Ideas\n", encoding="utf-8")
assert run("init", "--data", str(notes)) == (
    1,
    [],
    [f"{notes} is a file, not a folder. init changed nothing."],
)
deep = home / "a" / "b" / "recipe-menu"
code, lines, _ = run("init", "--data", str(deep))
assert (code, lines[0]) == (0, f"Created the data folder {deep}:")
assert run("init", "extra") == (
    2,
    [],
    [
        'Unexpected argument "extra". Write "recipe-menu init".',
        'Run "recipe-menu --help" to see the commands.',
    ],
)
```

## 3. Changes to existing interfaces

None. No interface that F01 to F07 implemented changes. Each exported name keeps its signature and its behavior, and the tests of F01 to F07 pass unchanged. F08 adds the module `init`. Like F04 and F05, it adds names to the interface of `datafile`:

1. `datafile` exports `CreationOutcome` and `Creation` (3.1) and `create_data_folder` (3.2), and `datafile/messages.py` gains six internal messages (3.2). Architecture 3 plans these writes: "Later features add the writes and the shared checks that they need."
2. `COMMANDS` in `src/recipe_menu/cli/_commands.py` gets `INIT_COMMAND` before `CHECK_COMMAND`. `COMMANDS` is internal to `cli`, and architecture 4 gives each command feature this entry. With it, the help of the real `recipe-menu` lists `init` (choice 1). The tests that run the real `COMMANDS` are F05-T48, F05-T49, and F07-T17. They check an unknown command, a line with no command, the first and last lines of the help, and the line of `check` wherever it is, which the entry does not change.

F08 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, `Plural`, `and_list`, and `format_table`.
- F03's `DataFolder`, `Problem`, and `Severity`, and the conditions of `SYSTEM_ERROR` for the value `reason` (F03 design 2.3).
- F04's table of listing problems of `list_toml_files` and its four messages, which stay internal to `datafile` (F04 design 3.1).
- F05's `Arguments`, `Command`, `Context`, and `FolderUse` in `app`, `Settings` and `Meal.label` in `settings`, and `COMMANDS` in `cli`.

The examples above also use F03's `read_catalog` and `read_pantry`, F05's `read_settings`, and F07's `check` on the folder that `init` creates.

### 3.1 `CreationOutcome` and `Creation`

- Module: datafile
- Purpose: The result of `create_data_folder` (3.2): what it found at the data folder, or what stopped it, and what it could not remove after a failure. `init` picks its output by the outcome (2.2).

Signature:

```python
class CreationOutcome(Enum):
    CREATED = "created"
    HOLDS_FILES = "holds files"
    NOT_A_FOLDER = "not a folder"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Creation:
    outcome: CreationOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `outcome` | `CreationOutcome` | What happened, by the table below. | None |
| `problem` | `Problem` or `None` | The `OSError` that stopped the call, as a problem. | A `Problem` with `Severity.ERROR` for `FAILED`, and `None` for the other outcomes. |
| `left` | A tuple of `Path` | What the call created and could not remove after the failure, as full paths, in the order of the removal. | Empty for every outcome other than `FAILED`. |

| Member | When | `problem` | `left` |
| --- | --- | --- | --- |
| `CREATED` | The call created every folder and file. | `None` | Empty |
| `HOLDS_FILES` | The data folder is a folder with an entry. The call created nothing. | `None` | Empty |
| `NOT_A_FOLDER` | Something other than a folder is at the data folder's path. The call created nothing. | `None` | Empty |
| `FAILED` | An `OSError` stopped the call, and the call removed what it created. | The error | What the removal could not remove, often nothing |

- Return value: A `CreationOutcome` member, or a `Creation`. Two creations are equal when their three fields are equal, and a `Creation` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `outcome` is `FAILED` and `problem` is `None`, or `outcome` is another member and `problem` is not `None`. |
| `ValueError` | `problem` has `Severity.WARNING`. |
| `ValueError` | `left` is not empty, and `outcome` is not `FAILED`. |

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import Creation, CreationOutcome, Problem
from recipe_menu.text import Message

DENIED = Message(
    "The folder cannot be created: access is denied.", "无法创建文件夹：没有访问权限。"
)
values = [outcome.value for outcome in CreationOutcome]
assert values == ["created", "holds files", "not a folder", "failed"]
created = Creation(CreationOutcome.CREATED)
assert (created.problem, created.left) == (None, ())
problem = Problem.error(Path("recipes"), None, DENIED)
left = (Path.cwd() / "recipe-menu" / "recipes",)
failed = Creation(CreationOutcome.FAILED, problem, left)
assert (failed.problem, failed.left) == (problem, left)
assert failed == Creation(CreationOutcome.FAILED, problem, left)

Creation(CreationOutcome.FAILED)  # raises ValueError
Creation(CreationOutcome.HOLDS_FILES, problem)  # raises ValueError
Creation(CreationOutcome.CREATED, None, left)  # raises ValueError
warning = Problem.warning(Path("recipes"), None, DENIED)
Creation(CreationOutcome.FAILED, warning)  # raises ValueError
```

### 3.2 `create_data_folder`

- Module: datafile
- Purpose: Creates a data folder with its folders and files, all or nothing (choices 4 and 5). It writes only into a data folder that is missing or empty, opens each file in exclusive mode, and removes what it created after a failure or an interruption ([architecture 6](../../architecture.md#6-error-handling)). It is the first write of `datafile` (architecture 3). `init` calls it (2.2).

Signature:

```python
def create_data_folder(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> Creation: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder to create. | None. Its root and the folders above it may be missing. |
| `folders` | A sequence of `Path` | The folders to create in it, in order, such as `folder.recipes`. | Each is inside `folder.root` and is not `folder.root`. Each appears once. Its parent is `folder.root` or an earlier item of `folders`. |
| `files` | A sequence of (path, text) pairs | The files to create, in order, each with its text. | Each path is inside `folder.root`, is not `folder.root`, appears once, and is not an item of `folders`. Its parent is `folder.root` or an item of `folders`. Each text is a `str` that UTF-8 can encode. |

- Return value: A `Creation` (3.1).

`create_data_folder` works in these steps:

1. It checks the arguments by their constraints, and it encodes each text as UTF-8, before it touches the disk. A wrong argument raises an error of the Errors table.
2. It looks at `folder.root`. The first row of this table that applies decides:

   | Condition | What follows |
   | --- | --- |
   | `os.path.isdir(folder.root)` is true. | It lists the folder. A listing that fails with an `OSError` gives `FAILED`. Its problem has the file `Path(".")`, no place, and the message of the table of listing problems of `list_toml_files` (F04 design 3.1). An entry of any kind, hidden ones included, gives `HOLDS_FILES`. With no entry, the call goes on with step 3. |
   | `os.path.lexists(folder.root)` is true. | `NOT_A_FOLDER`. |
   | Neither. | It creates `folder.root` and each missing folder above it, from the top down, one at a time. Then it goes on with step 3. |

3. It creates each folder of `folders`, in order, with `Path.mkdir`, with no parents, and with an existing folder as an error.
4. It creates each file of `files`, in order. It opens the file in exclusive mode, `"x"`, with `encoding="utf-8"` and `newline="\n"` (architecture 8), writes the text, and closes the file. So the file holds the UTF-8 bytes of the text, with no byte order mark and with the line ends of the text.
5. It gives `Creation(CreationOutcome.CREATED)`.

`os.path.isdir` and `os.path.lexists` never raise, and a probe that fails counts as false. The first `OSError` that a creation raises in steps 2 to 4 stops the call. The call then removes what it created, as described below, and gives `FAILED` with a problem by the first row of this table that applies:

| Error | Creating a folder | Creating a file |
| --- | --- | --- |
| `FileExistsError` | `FOLDER_EXISTS` | `FILE_EXISTS` |
| `PermissionError` | `FOLDER_CREATE_DENIED` | `FILE_WRITE_DENIED` |
| Any other `OSError` | `FOLDER_CREATE_ERROR` | `FILE_WRITE_ERROR` |

The value `reason` is the error's `strerror`, or the name of the error's class, such as `OSError`, when `strerror` is `None` or empty, as for `SYSTEM_ERROR` (F03 design 2.3). The problem has no place. Its file is `folder.relative(path)` for an item of `folders` or `files`. For `folder.root` and the folders above it, its file is `Path(".")`, because you named the data folder.

The removal works in these steps:

1. It removes each folder and file that the call created, in the reverse order of their creation. It removes a file with `Path.unlink` and a folder with `Path.rmdir`, which removes only an empty folder. A file counts as created from the moment that its open succeeds, so a file that is half written is removed too.
2. It never removes anything that existed before the call. So a data folder that was empty stays, and so do the folders above it.
3. A removal that fails with an `OSError` is skipped, and the next removal follows. Its path goes into `left`, as a full path, in the order of the removal. A folder that still holds a skipped file fails its `rmdir`, so it goes into `left` too.

Any other exception that interrupts steps 2 to 4, such as `KeyboardInterrupt` for Ctrl+C or the exception of a bug, runs the same removal, and then goes on. The call then gives no result. The removal runs in a `finally` block, so no `except` clause catches more than `OSError` (architecture 6 and 8).

These messages join the internal messages of `datafile`, beside those of F03 design 2.3 and F04 design 3.1:

| Name | English | Chinese |
| --- | --- | --- |
| `FILE_EXISTS` | `The file already exists.` | `文件已存在。` |
| `FILE_WRITE_DENIED` | `The file cannot be written: access is denied.` | `无法写入文件：没有访问权限。` |
| `FILE_WRITE_ERROR` | `The file cannot be written. The system says: {reason}` | `无法写入文件。系统提示：{reason}` |
| `FOLDER_EXISTS` | `The folder already exists.` | `文件夹已存在。` |
| `FOLDER_CREATE_DENIED` | `The folder cannot be created: access is denied.` | `无法创建文件夹：没有访问权限。` |
| `FOLDER_CREATE_ERROR` | `The folder cannot be created. The system says: {reason}` | `无法创建文件夹。系统提示：{reason}` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | A path of `folders` or `files` is not inside `folder.root`, is `folder.root`, appears twice, or has a parent that is neither `folder.root` nor an item of `folders` that comes before it. The check runs before the call touches the disk. |
| `UnicodeEncodeError` | A text holds a character that UTF-8 cannot encode, such as a lone surrogate. The check runs before the call touches the disk. |

- Side effects: Lists `folder.root` when it is a folder. Creates `folder.root` and the folders above it when `folder.root` is missing, and then the folders and the files. After a failure or an interruption, removes what it created. It reads no file.
- Performance target: None

Example:

In this example, `tmp` is an empty temporary folder. The second call finds the folder that the first call created. The failure uses a file name of 300 characters, which both systems reject, after the call has created the settings.

```python
from pathlib import Path

from recipe_menu.datafile import CreationOutcome, DataFolder, create_data_folder
from recipe_menu.lang import Lang

folder = DataFolder(tmp / "a" / "recipe-menu")
folders = (folder.recipes, folder.menus)
files = ((folder.settings, 'language = "en"\n'), (folder.recipe_file("rice"), "servings = 2\n"))
creation = create_data_folder(folder, folders, files)
assert creation.outcome is CreationOutcome.CREATED
assert (creation.problem, creation.left) == (None, ())
assert folder.settings.read_bytes() == b'language = "en"\n'
assert sorted(entry.name for entry in folder.root.iterdir()) == [
    "menus",
    "recipes",
    "settings.toml",
]
assert [entry.name for entry in folder.recipes.iterdir()] == ["rice.toml"]

assert create_data_folder(folder, folders, files).outcome is CreationOutcome.HOLDS_FILES
assert folder.settings.read_bytes() == b'language = "en"\n'
not_a_folder = create_data_folder(DataFolder(folder.settings), (), ())
assert not_a_folder.outcome is CreationOutcome.NOT_A_FOLDER

other = DataFolder(tmp / "b" / "recipe-menu")
name = "x" * 300 + ".toml"
failed = create_data_folder(
    other, (other.recipes,), ((other.settings, "\n"), (other.root / name, "\n"))
)
assert failed.outcome is CreationOutcome.FAILED
assert failed.problem is not None
assert (failed.problem.file, failed.problem.place) == (Path(name), None)
assert failed.problem.text(Lang.EN).startswith("The file cannot be written. The system says: ")
assert failed.left == ()
assert not (tmp / "b").exists()

fresh = DataFolder(tmp / "c")
create_data_folder(fresh, (), ((tmp / "elsewhere.toml", ""),))  # raises ValueError
create_data_folder(fresh, (), ((fresh.recipe_file("rice"), ""),))  # raises ValueError
create_data_folder(fresh, (fresh.menus, fresh.menus), ())  # raises ValueError
create_data_folder(fresh, (), ((fresh.settings, "\udc80"),))  # raises UnicodeEncodeError
```

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `init` is the command module of architecture 3, in `src/recipe_menu/commands/init/`, and exports only `INIT_COMMAND`. It imports `app`, `lang`, `text`, `datafile`, and `settings`, which its row allows. Its row owns "the example files that it writes", so the four texts belong in `_example.py`, and `init` writes them through `datafile`, as architecture 2 and 8 ask (choice 2). `create_data_folder` is the first write that architecture 3 plans for `datafile`, and it uses only the files of `datafile`. `Creation` is a frozen dataclass with `slots=True` whose collection is a tuple, and `CreationOutcome` is an enum (architecture 8). A `Problem` keeps its file relative to the data folder, with `Path(".")` for the folder itself (architecture 5.3). The four files are those of architecture 5.1 that name `init` as their writer. The Architect built a model of sections 2 and 3 on the code of the branch, and choices 1 to 3, 6, and 7 hold on it. With `INIT_COMMAND` before `CHECK_COMMAND`, the help has 15 lines in each language, and its second column starts after 18 columns. The texts that the model takes from the code blocks of `example-data.md` hold no backslash and equal `tests/data/example/` byte for byte. For them, `read_catalog` and `read_pantry` give 6 categories, 22 ingredients, 5 tags, and 5 pantry ingredients. The Chinese `settings.toml` differs from the English one only in its `language` value, and `read_settings` gives `Settings(Lang.ZH)` for it. `pyproject.toml` does not change, so R16 has nothing to review. Version 0.2 changes none of this, so the reasons of round 1 hold. |
| Follows the error handling and naming conventions | Pass | The reasons of round 1 hold. A refusal and a failure on the disk are values. `create_data_folder` turns each `OSError` into a `Problem`, names no exception other than `OSError`, and removes in a `finally` block (architecture 6 and 8). Each file opens in mode `"x"` with `utf-8` and `newline="\n"`, so `init` never overwrites a file (architecture 6). The exit codes and the streams follow architecture 6. Every message is an UPPER_SNAKE constant in the `messages.py` of its module. The counts are `Plural` values with the same placeholder in both forms. The six new `datafile` messages follow the read messages of F03 design 2.3 and F04 design 3.1 in both languages. On the model, with Python 3.13.18 on this Windows 11 PC, choices 4, 5, and 10 and the example of 3.2 still hold as round 1 found. Finding 1 is resolved. The Architect ran choice 9 again with the six values of round 1, `x\recipe-menu` followed by a space, two spaces, `.`, `..`, ` .`, and `. `, each in the four states of round 1. Version 0.2 states each result. With every value but the single dot, `init` fails at `recipes` with `FOLDER_CREATE_ERROR` and the reason "The system cannot find the path specified", and it removes each folder that it created. The one exception is a folder that holds an entry, which gives `ALREADY_HOLDS_FILES` with the name as typed. Each of these runs exits with 1, and the failure in an empty folder ends with `init changed nothing.` With the single dot, `init` creates `recipe-menu` with every file and exits with 0, and its first line shows the dot. `check` with the same value then gives "No errors. No warnings.", and a second `init` refuses the folder. Finding 2 is resolved. Choice 8 quotes the rule of architecture 6 that the first line of a failure departs from, says why, and puts the departure to Troy as open question D. 2.2 points to both. The quote ends before the example of the rule, which leaves the rule as it is. A `Problem` keeps its file relative to the data folder, so only the line that `init` writes departs. Finding 3 is resolved. The Architect ran the two cases that choice 5 adds. A Ctrl+C just after `open` created `pantry.toml` left that file, the data folder, and the folders above it. A second Ctrl+C at the removal of `settings.toml` stopped the removal. Both gave exit code 130 and no output, and the next `init` refused the folder, as choice 5 says. Finding 4 is resolved. With ruff 0.17.4, `ruff format --config pyproject.toml --diff` finds the 7 `python` blocks already formatted, and none of their lines is wider than 100 columns. The `# raises ValueError` of the warning in 3.1 is on the line of its call. |
| Does not duplicate an existing interface | Pass | No interface created a folder or a file before `create_data_folder`. A listing that fails reuses the messages of `list_toml_files` (F04 design 3.1), and its value `reason` follows `SYSTEM_ERROR` (F03 design 2.3). The six new messages say what no read message says. `init` writes a failure in the layout of `stop_at_error` (F05 design 2.8) and does not call it, because the first line is a full path (choice 8 and open question D) and the last line is `CHANGED_NOTHING` or `LEFT_BEHIND`, not `RUN_CHECK`. No module had a message for the names of the two languages, so `ENGLISH` and `CHINESE` duplicate nothing. The settings line uses `Meal.label`, `and_list`, and `Plural`, so no list or plural is built by hand (architecture 8). The two copies of the example texts are on purpose (choice 2). One is test data that the Developer never edits (R08), and an F08 test keeps the two equal byte for byte. Version 0.2 adds no interface. |
| Depends only on features earlier in the order | Pass | F08 uses `lang` from F01 and F02, `text` from F02, `datafile` from F03 and F04, and `app`, `settings`, and `cli` from F05. The examples also use `catalog` from F03 and `check` from F07, which reads through `recipes` from F04 and `menus` from F06. All of them come before F08 and pass their tests on main. F05 is the hard dependency of the F08 row, and F03, F04, and F07 are its soft dependencies. The plans for F11, F13, and F15 say what each feature is meant to do and bind no later design. F08 needs only the standard library, and version 0.2 adds no dependency on a feature or a package. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | `datafile` knows no example data, and `init` knows no file name (choice 3). `init` passes the paths that `DataFolder` gives, with its texts, and it names each row of its table with `folder.relative`. The counts sit beside the texts in `_example.py`, and an F08 test reads the counts back with `read_catalog` and `read_pantry` (choice 7). `init` uses neither `context.settings` nor `context.today`. A refusal speaks the language that `cli` picked from the folder's settings, as F05 design 2.10 gives it. The tie between `init` and `check`, "No errors. No warnings." on a new folder, is a test and v0.1-S01, not an import. On the model, `check` on the new folder gives the second output of the F08 prototype "In English" exactly. Version 0.2 changes none of this. |
| Changes an implemented interface only through the change flow | Pass | Section 3 rightly says None. `datafile` gains three names and six internal messages, as F04 and F05 added names to it. The entry in `COMMANDS` is the change that architecture 4 gives each command feature. Version 0.2 changes no interface, so the model and the test run of round 1 stand. With the model in place, the branch's tests give 405 passed and 3 skipped, which are the 408 tests that it collects, F05-T48, F05-T49, and F07-T17 included. So no test of F01 to F07 changes. The PR adds only the two design files. Open question A changes rule 4 or step 2 of F05 design 2.10, and the design sends it through the change flow. On this PC, `os.path.abspath` drops a trailing space or dot from the last part, keeps a trailing space in a middle part, and turns `C:\x\..\y` into `C:\y`. So under option 1, F05's case `x/../y` in `tests/test_f05_data_folder.py` changes on Windows, as the design says. Open question D changes architecture 6, not an implemented interface, and Troy decides it with this design. The split into a mock and an implementation is right. The tests reach `create_data_folder` both directly and through `init`, so both modules must import in the mock, and the reason for the soft limit is the one of F05's mock. Moving the six `datafile` messages to PR 5 would still leave 6 files in the mock, so it gains nothing. Finding 5 is resolved. Section 2 now names the further tests that pass against the mock, such as tests of the fields of `INIT_COMMAND`, of the values of `CreationOutcome`, of a valid `Creation`, and of `init extra` or `init --tag`. It asks each such test to also check something that the mock gets wrong (R09). |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | Findings 1 and 2 block. The Architect checked choices 1 to 10 and the five notes of the brief against the requirements, the architecture, the F05, F07, and F08 prototypes, `example-data.md`, and v0.1-S01 to v0.1-S03. Each file has 12 code blocks, each equal to its mirror, and the 707 lines of the two files match heading for heading, row for row, and item for item. The 7 `python` blocks parse. On the code of the branch, the Architect built a model of sections 2 and 3 with `INIT_COMMAND` in `COMMANDS`. It ran the four examples with Python 3.13.18 on Windows, and every assertion and all 8 `# raises` hold. The model gives the three outputs of the F08 prototype exactly, in both languages, and the branch's tests pass on it, 405 passed and 3 skipped. The Architect ran choice 9 and the failure of 3.2 on this PC, as the Interface Designer asked. No test ran on the PR itself, because it changes no code. | Changes requested. The Interface Designer corrects choice 9 (finding 1) and states the full path of a failure as a point for Troy (finding 2), in both files, and raises the version. Findings 3 to 5 do not block. For the approval, the Architect agrees with the recommendations of open questions A, B, and C. After finding 1, option 1 of question A matters for a trailing space and for two or more dots, because a single dot already works. The Architect also agrees with the new Chinese texts of 2.2 and 3.2. The six `datafile` texts follow the read messages, and the texts of `init` match the F08 prototype where it shows them. |
| 2 | No blocking issue. Version 0.2 resolves findings 1 and 2 as asked and takes in findings 3 to 5. Besides the version and the change log, only choices 5, 8, and 9, open questions A and D, the sentence that counts the open questions, the paragraph on the mock, the paragraph of 2.2 on a failure, and four lines of the examples of 3.1 and 3.2 change. Section 4 is as round 1 left it. The 722 lines of the two files still match heading for heading, row for row, and item for item, and the 12 code blocks of each file equal those of its mirror. The 7 `python` blocks parse, and `ruff format` finds them formatted. On the model of round 1, the four examples hold again, with every assertion and all 8 `# raises`. So do the three outputs of the F08 prototype, v0.1-S03, Ctrl+C, and `LEFT_BEHIND`. The Architect also ran the 24 cases of choice 9, `check` on the folder of the single dot, and the two new cases of Ctrl+C. The example of 3.2 ran in the scratchpad only, not in `D:\` as in round 1. The tests on the branch did not run again, because version 0.2 changes no interface and the PR changes no code. | Approved. The main session puts open questions A to D and the new Chinese texts of 2.2 and 3.2 to Troy when Troy approves this design (R18). The Architect agrees with the recommendation of each question. Once Troy approves option 1 of question D, the Architect adds the case to architecture 6 in a `[docs]` PR, before the F08 mock PR. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-13 | First draft. |
| 0.2 | 2026-11-13 | Answers round 1 of the Architect review. Choice 9 says that the listing of an existing folder works, so an empty folder fails at `recipes` and a folder with an entry is refused. It also says that a single trailing dot works, because Windows drops one trailing dot from a part in the middle. Open question A says that a single dot already works. Choice 8 and 2.2 name the rule of architecture 6 from which the full path of a failure departs, and open question D puts it to Troy. Choice 5 says that a Ctrl+C before the call records an entry, or a second Ctrl+C during the removal, acts like a killed process. Section 2 names more tests that would pass against the mock. Four lines of the examples of 3.1 and 3.2 now fit in 100 columns. Three are wrapped as `ruff format` wraps them, and the warning of the last call of 3.1 moves to a variable, so its `# raises` comment stays on the line of the call. |
| 1.0 | 2026-11-13 | Approved by Troy. |
