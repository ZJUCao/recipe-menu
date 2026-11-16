---
troy-doc: "F13-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-15"
status: "Approved by Troy on 2026-11-15"
mirror: "test-plan.zh-CN.md"
---

# F13 Shopping list command: test plan

## 1. Feature

- ID and name: F13 Shopping list command
- Design: [design.md](design.md), version 1.0

## 2. Cases

The tests call `SHOP_COMMAND` of `recipe_menu.commands.shop`, `replace_file`, `FileCreation`, and `FileOutcome` of `recipe_menu.datafile`, `main` of `recipe_menu.cli`, and `python -m recipe_menu`. A unit case calls `SHOP_COMMAND.run` or `replace_file` with values that it builds. A functional case runs `main` with a command line, as you type `recipe-menu shop`. It passes no `commands`, so `main` uses the real `COMMANDS`, which holds `SHOP_COMMAND` after `MENU_SHOW_COMMAND` from the mock PR on (design choice 1). An integration case runs a v0.1 scenario at `main`, starts `python -m recipe_menu`, or builds random weeks. The performance case times `python -m recipe_menu shop` (section 3). Each case names the part of the design that it comes from, such as (choice 4). The design's three examples and their four `# raises` lines are in F13-T01 (2.1), F13-T11 (2.2), and F13-T03 (3.1).

**Points A to C.** Troy approved design 1.0 on 2026-11-15 with the recommendation of each point: the 11 new texts of 2.2 and 3.1 as written (A), the English pantry line with the catalog's names as written (B), and `replace_file` creating a missing `shopping` folder (C). The requirement change of point B (PR #86) changed the English pantry line of the F13 prototype to `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper` and the line of v0.1-S16 to `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`. So the outputs of the prototype "In English" and of v0.1-S16 follow the design exactly, and no case treats the English pantry line as an exception. The design's choice 8, point B, and its two clauses "apart from the English pantry line" record the decision. The cases check each new text of point A in both languages:

- The top of the English file, `# Shopping list for 2026-W47` and `16 to 22 November 2026: 4 meals, 9 dishes.`: F13-T01, F13-T12, F13-T13, F13-T14, and F13-T15.
- The Chinese line for a week with no dish: F13-T11, F13-T14, and F13-T24.
- `There is nothing to buy.` and `没有要买的东西。`: F13-T14.
- `No file was saved.` and `没有保存文件。`: F13-T11, F13-T19, and F13-T21.
- The line when the temporary file stays, in both languages: F13-T19.
- `The file cannot be written: "shopping" is not a folder.` and its Chinese text: F13-T03, F13-T06, F13-T11, and F13-T21.

Point C is in F13-T05, F13-T09, F13-T12, F13-T16, and F13-T21: nothing at `shopping` gives a new folder, which stays after a later failure, and something other than a folder gives the failure lines.

**Tests of earlier features.** Design section 3 says that every test of the real help stays true when `shop` joins `COMMANDS`. The Test Manager checked it on Troy's PC with Python 3.13.18: with a model of `SHOP_COMMAND` placed in the real `COMMANDS` of `cli`, the whole suite of main gave 553 passed and 4 skipped, the 4 skips being main's cases that run only on Linux. So no test of an earlier feature changes, and F13's tests PR changes none. `HELP` and `HELP_ZH` of `tests/f11_texts.py` stay as they are, because F11-T01 passes `main` its own seven commands. F13 changes no file of `tests/data/example/`, and no function of `tests/f08_support.py`, `tests/f11_support.py`, `tests/f12_support.py`, or `tests/pt01_support.py`.

**R09.** The mock defines every message and `SHOP_COMMAND` with all its fields, adds the entry to `COMMANDS`, and adds `replace_file` and `PARENT_NOT_A_FOLDER` to `datafile`. Its `replace_file` touches nothing and gives `FileCreation(FileOutcome.CREATED)`, and its `run` reads no file, writes nothing, raises nothing, and gives 0 (design section 2). So a test passes against the mock when it checks only the fields of `SHOP_COMMAND`, the help, a message, exit code 0, an empty error stream, or that `replace_file` gives `CREATED`. The same holds for what `cli` does before it runs `shop`: a missing data folder, broken settings, `shop 2026-W47 2026-W48`, `shop --tag x`, and `shop next --help`. It also holds for a check that `shop` changes no file, that `shopping\` stays empty, that a failed save keeps the old file, or that no `.tmp` file is left (Architect note 4). Each case that checks such a thing also checks something that the mock gets wrong: the output of `shop`, exit code 1, 2, or 130, a `UsageError` from `run`, the bytes of the saved file, a new `shopping\`, the outcome or the problem of `replace_file`, an error that `replace_file` raises, or the calls that the harness records. F13-T01, F13-T02, F13-T05, F13-T08, F13-T12, F13-T14, F13-T16, F13-T18, F13-T19, F13-T21, F13-T22, F13-T24, and F13-T27 check such things only beside a result that the mock gets wrong. Every case that expects exit code 0 from `shop` checks the whole output, which is never empty. Every case that expects `CREATED` checks the bytes of the file or the record. `tests/f13_support.py`, `tests/f13_texts.py`, and `tests/f13_blocks.py` call no interface of F13 when they are imported.

**Both systems.** Every case runs on Linux and on Windows, and no case is skipped on either. CI runs only on Linux, and only Troy's PC runs the tests on Windows. A problem names its file with the system's separator. So in an expected line, `menus/2026-W47.toml` stands for `str(Path("menus", "2026-W47.toml"))`, and a path that starts with a folder of the case, such as `X/shopping/2026-W47.md`, stands for `str` of that full path under `tmp_path`. The outputs of `shop` hold no path except in their last line, so their columns have the same widths on both systems. In the Chinese outputs, each Chinese character takes two columns. The inputs that touch what the systems do differently each give a result that the case states for each system:

- A move onto a folder (F13-T09 and F13-T21). The real `os.replace` of a file onto a folder fails on both systems: with `PermissionError` on Windows, which gives `FILE_WRITE_DENIED`, and with `IsADirectoryError` on Linux, which gives `FILE_WRITE_ERROR` with `Is a directory`. The case takes the message from the system with `move_message` of `tests/f13_support.py` (below), as F08-T07 takes the message of a failed `mkdir` from `system_message`.
- A list file that another program holds open (F13-T21). Windows refuses the move, and the run gives the failure lines with `FILE_WRITE_DENIED` and keeps the old bytes. Linux replaces the file, and the run gives the list. The Test Manager made that move on Troy's PC with Python 3.13.18: `os.replace` onto a file that `open(path, "rb")` held open raised `PermissionError` with `Access is denied`.
- A creation of a folder that the system cannot make (F13-T07): `mkdir` under a missing data folder, and a name that the system cannot look at, `a?b` on Windows and 256 times `a` on Linux, as `unreadable_name` of `tests/f05_support.py` gives them. The case takes the message from the system with `system_message("folder", path)` of `tests/f08_support.py`, which makes the same `mkdir` before the call.
- A dangling link (F13-T06 and F13-T21), made with `dangling_link` of `tests/f08_support.py`, and a link that leads to a folder (F13-T05), made with `folder_link` of `tests/f13_support.py`: a junction on Windows and a symbolic link on Linux. A junction needs no right that a user lacks.
- The data folder `One Drive/菜谱` of F13-T23 holds a space and Chinese characters, and it is a valid path on both systems.

**Access that is denied.** No case denies access through the file system, with `os.chmod`, an access list, or `listing_denied` of `tests/f04_support.py`. The root user on Linux ignores the mode bits, so a test that relies on them fails as root, as the F04 tests note. Every `PermissionError` in the cases comes from the fault harness, which raises it the same way for every user, or from a refusal that holds for every user: a move onto a folder, and on Windows a move onto a file that is open. So every case passes as root on Linux and as an administrator on Windows.

**How a case makes the disk fail.** The cases use `shop_faults(base, *rules)` of `tests/f13_support.py`. It is the fault harness of `tests/f08_support.py` with three additions, so it replaces `os.mkdir`, `os.rmdir`, `os.unlink`, `os.remove`, `os.scandir`, `os.listdir`, `io.open`, and `builtins.open`, and also `os.replace`, which `Path.replace` calls in Python 3.13. While it is open, it records each call on a path under `base` and applies its rules. A rule is written as a kind, a path, and an effect, such as `open T: DENIED`. The rules of F08 hold as the F08 and F11 test plans give them:

- `mkdir P: E` raises E in place of the creation of the folder P. `mkdir P: race` first creates P, as another program would, and then makes the call, which raises the system's `FileExistsError`.
- `open P: E` raises E in place of the open of P in mode `x`, so the system creates nothing. `open P: race` first creates P with `b"mine\n"` and then makes the open, which raises the system's `FileExistsError`. `open P: after E` makes the open, closes the file, and then raises E, so P exists but the call never got it.
- `write P: E` writes the first half of the text of the first write to the file that the open of P gave, `text[: len(text) // 2]`, flushes it, and raises E.
- `unlink P: E` raises E in place of each removal of P.

F13 adds these:

- The record of a move is `move A B`, with the source A and the target B relative to `base`. `move P: E` raises E in place of the move whose source is P, and moves nothing.
- `close P: E` closes the file that the open of P in mode `x` gave, for real, and then raises E. It acts at the file's `close` and at the end of its `with` block, unless another exception is already on its way.
- `unlink P: later E` lets the first removal of P run, and raises E in place of each later removal of P. So step 3 of 3.1 runs, and the removal after a failure fails.

The effects are those of the F08 test plan: `DENIED` is `PermissionError(errno.EACCES, "Permission denied")`, `IO` is `OSError(errno.EIO, "Input/output error")`, `NO_SPACE` is `OSError(errno.ENOSPC, "No space left on device")`, `CTRL_C` is `KeyboardInterrupt()`, `BUG` is `RuntimeError("bug")`, and `EMPTY_IO` is `OSError(errno.EIO, "")`. `TimeoutError()` and `OSError()` have the `strerror` `None`. F13 adds `EXISTS`, `FileExistsError(errno.EEXIST, "File exists")`, which pins the rows of `FileExistsError` in the table of 3.1 (Architect note 1). A case that raises `KeyboardInterrupt` gets it back through `pytest.raises`, or as exit code 130 from `main` through `call_main` of `tests/f08_support.py`, which turns a `KeyboardInterrupt` that leaves `main` into a failure.

`ShopFaults` in `tests/f13_support.py` subclasses `Faults` of `tests/f08_support.py`. It adds the method `replace`, a wrapper of the file for the rule `close`, and the count of the rule `later`, and `shop_faults` patches what `faults` patches and `os.replace`. `tests/f08_support.py` stays at its 463 lines, within the 500 of R06, and F08 and F11 keep their harness as it is.

The note for the Developer: the cases hold only when `replace_file` reaches the disk through the calls that design 3.1 names. Besides the probes `os.path.isdir` and `os.path.lexists`, which the harness does not record, it creates the folder with `Path.mkdir()`, removes `temp` with `Path.unlink(missing_ok=True)` in step 3 and with `Path.unlink` after a failure, opens `temp` with `Path.open` or `open` in mode `"x"`, writes the whole text with one call of `write` on the file object that the open gave, also when the text is empty, and moves `temp` with `os.replace` or `Path.replace`. In Python 3.13.18 on Troy's PC, `Path.mkdir` calls `os.mkdir`, `Path.unlink` calls `os.unlink`, `Path.open` calls `io.open`, and `Path.replace` calls `os.replace`. A call that 3.1 does not name, such as `os.open`, `os.rename`, `Path.write_text`, `Path.touch`, `tempfile`, or `shutil`, escapes the rules of the harness or gives another record, so the cases fail. So the record of a call that works always holds `unlink T`, also when nothing is at `T`.

**The record of the reads.** F13-T14, F13-T15, and F13-T16 record which files `shop` opens and which folders it lists, with `shop_faults(F.root)`, as F11-T27 does. The harness records each open of a path under the data folder as `read`, or as `open` for mode `x`, with the path relative to the folder and `/`. It records each listing by `os.scandir` or `os.listdir` in "the listings". `cli` reads `settings.toml` before it runs a command, so every record starts with `read settings.toml`. A recipe that several dishes name is parsed once, so its file appears once in the record.

The Test Manager computed the expected texts below on Troy's PC, with Python 3.13.18, the readers and `build_shopping_list` of main, the fault harness with the additions above, and a model of `shop` and `replace_file` that follows the design. The model gave the two outputs and the saved file of the F13 prototype byte for byte and the whole help of the F05 prototype, and blocks A to H are its outputs.

These rules hold for the test data, as in the F11 test plan:

- `EXAMPLE` is the folder `tests/data/example/` of the repository (architecture 10). It has no `shopping/`. The fixture `example_folder` of `tests/conftest.py` copies it to `tmp_path / "recipe-menu"` with LF line ends and gives a `DataFolder` on the copy. In a case, `example` is that `DataFolder`. "A new example at P" is a further copy, made with `copy_example` of `tests/f05_support.py`. "A new example" with no P is at a path of its own under `tmp_path`.
- "An empty-menus example" is a new example with every entry of `menus/` deleted.
- "The init folder at P" is made with `make_init` of `tests/f07_changes.py`: a new example with no recipe other than `tomato-egg`, no menu, and the empty folders `menus/` and `shopping/`. "The S16 folder" is the folder that `s16_folder(example, tmp_path / "init")` of `tests/f12_support.py` gives: the init folder, with breakfast, lunch, and dinner and 3 servings in `settings.toml`, and `menus/2026-W48.toml` with `tomato-egg` in Monday breakfast.
- `home` is `tmp_path / "home"`, an empty folder that `make_home` of `tests/f05_support.py` makes. It is outside `example`, so a line with no `--data` finds no data folder unless the case puts one at `home / "recipe-menu"`.
- The tests write every file with `write` of `tests/f03_support.py`, which writes UTF-8 with LF line ends and makes its folders first, or as bytes with `put_bytes`. "X replaced by Y in F" replaces the first X in the file F with `edit` of `tests/f07_changes.py`, which checks that F holds X.
- No test changes the repository, touches `~/recipe-menu`, or reads the clock. Every call of `main` passes `home`, `environ`, and `today`. F13-T28 and F13-T30 start `python -m recipe_menu` with `HOME` and `USERPROFILE` set to a folder in `tmp_path`. A case changes the current folder only with pytest's `monkeypatch.chdir`.

These named changes make the folders of the cases. Each applies to the data folder of its case:

- From the F09 and F11 test plans: no catalog, the catalog brace, no recipes folder, recipes as a file, Rice Bowl, capital rice, folder x, the mapo mistake, rice at 0, broken settings, the extra recipes, no menus folder, menus as a file, and week B. The helpers of `tests/f07_changes.py`, `tests/f09_support.py`, and `tests/f11_support.py` make them. The extra recipes are `boiled-egg`, `steamed-egg`, and `water`, whose `ingredients` is empty. Week B is `menus/2026-W48.toml`: Monday's dinner, listed before its lunch, names `rice` twice, Monday's lunch names `mapo-tofu`, Friday's lunch names `choy-sum` with 10 servings, and Sunday's dinner names `red-braised-pork`, which has a warning.
- From the F10 test plan: Chinese settings, which replaces `language = "en"` by `language = "zh"` in `settings.toml`, and BOM and CRLF, which writes each file of the folder again as `b"\xef\xbb\xbf"` followed by its bytes with each `b"\n"` replaced by `b"\r\n"`.
- From F06's helpers in `tests/f06_support.py`: the menu typo, which is `typo`, and the menu mistakes of v0.1-S07, which is `mistakes`. The menu typo makes Monday's dinner of `menus/2026-W47.toml` name `tomato-eggs`.
- From `tests/f07_changes.py`: the pantry mistake, which is `pantry_sesame` and replaces `"糖"` by `"sesame oil"` in `pantry.toml`, and the pantry item, which is `pantry_not_text` and replaces `"糖"` by `3`. No pantry: `pantry.toml` deleted.
- The rice week W: `menus/W.toml` written with `menu_text(W, [lunch, dinner])` of `tests/f11_support.py`, with its first `dinner = []` replaced by `dinner = ["rice"]`.
- The water week: the extra recipes, and `menus/2026-W50.toml` written as `week = "2026-W50"\n\n[monday]\nlunch = ["water"]\n`.
- The egg week: the extra recipes, `"花椒"]` replaced by `"花椒", "鸡蛋"]` in `pantry.toml`, and `menus/2026-W51.toml` written as `week = "2026-W51"\n\n[tuesday]\ndinner = ["water", "boiled-egg"]\n`.
- The chicken break S: `en = "Chicken wings"` replaced by `en = "Chicken{S}wings"` in `catalog.toml`, where S is one of the TOML escapes `\n`, `\r\n`, and `\u2028`, so that the English name takes two lines.
- The meat break: `en = "Meat and seafood"` replaced by `en = "Meat\nand seafood"` in `catalog.toml`, with the TOML escape `\n`.
- The missing name: `{ zh = "可乐", en = "Cola", category = "other", unit = "罐" }` replaced by `{ zh = "可乐", category = "other", unit = "罐" }` in `catalog.toml`.
- Shopping as a file: `shopping` written with `b"x\n"`. An empty shopping: the empty folder `shopping/`.
- A ticked list: `shopping/2026-W47.md` written with `"# 2026-W47 购物清单\n\n- [x] 番茄 600 g\n"`. An old list: `shopping/2026-W47.md` written with `b"old\n"`. An old temporary file: `shopping/2026-W47.md.tmp` written with `b"half\n"`.

These conventions hold for the calls of `main`:

- A line such as `shop 2026-W47 --lang zh` in F stands for `at(home, F, "shop", "2026-W47", "--lang", "zh")` of `tests/f09_support.py`. It adds `--data` and F, and runs `main` through `call` of `tests/f07_support.py`, with `home`, `environ`, `today=date(2026, 11, 10)`, two new `io.StringIO` streams, and no `commands`. A line "on D" runs in the same way with `today=D`, through `on(home, F, D, *argv)` of `tests/f11_support.py`. A line "with no folder" has no `--data`. A line that a rule can stop with `CTRL_C` runs through `call_main` of `tests/f08_support.py`. `environ` is `{}` unless the case gives it.
- A word in quotation marks is one word, written as a Python string with its escapes, such as `""` or `" this"`. Each `\uXXXX` in a word stands for that one character.
- The result is `(code, out, err)`. `(c, out L)` stands for `(c, out, "")`, where out is the lines of L, each followed by `"\n"`, and nothing more. `(c, err L)` stands for `(c, "", err)` in the same way. `(130, "", "")` is an exit with nothing written. The tests compare the whole texts, never `splitlines()` of them, because `splitlines()` also splits at U+000D and U+2028, which F13-T13 must not find in an output.
- In a case, P is the full path of the list file of its week in the data folder of the case, `F.shopping_file(week)`, and T is P with `.tmp` added, such as `X/shopping/2026-W47.md.tmp`.
- `STOP(W, M)` and `STOP_ZH(W, M)` are the three lines of `stop_at_error` in English and in Chinese, as the F09 test plan defines them, and `stop` of `tests/f09_texts.py` builds the result. W is a file, such as `catalog.toml`, or a file and a place, such as `menus/2026-W47.toml, Monday dinner`, which is `menus/2026-W47.toml，周一晚餐` in Chinese.
- "Among the errors of `check`" has the meaning of the F09 test plan, and `assert_among_check` of `tests/f09_support.py` checks it.

These conventions hold for the direct calls of `replace_file`:

- `base` is an empty folder of its own under `tmp_path` for each call. `F` is `DataFolder(base / "recipe-menu")`, and `F.root` exists unless the input says otherwise. Q is `F.shopping_file("2026-W47")`, and T is `F.shopping / "2026-W47.md.tmp"`. In a record, S stands for `recipe-menu/shopping`, and Q and T stand for those paths relative to `base`, such as `recipe-menu/shopping/2026-W47.md.tmp`.
- A problem is written as its file and its message, such as `shopping/2026-W47.md: FILE_WRITE_DENIED`. Every problem of `replace_file` is an error with no place. The test checks the result with `assert_failed` of `tests/f11_support.py`: `outcome is FileOutcome.FAILED`, `severity is Severity.ERROR`, `str(problem.file)`, `place is None`, `text(Lang.EN)`, `text(Lang.ZH)`, `left` as a tuple of `str` of its paths, and `existing is None`.
- "The tree of X" and "the full record of X" are those of the F08 test plan, which `tree` and `full_record` of `tests/f08_support.py` give.

The expected texts are these. The tests write each one out as a literal in `tests/f13_texts.py` or `tests/f13_blocks.py`. They import no message and never read a prototype file, because the messages of `shop` and of `datafile` are internal (design section 2, architecture 8).

- `SHOP_47(P)` and `SHOP_47_ZH(P)` are the outputs of the F13 prototype "In English" and "In Chinese", 26 lines each, with P in place of `C:\Users\Troy\recipe-menu\shopping\2026-W47.md` in the last line.
- `PROTOTYPE_FILE` is the `markdown` block of the F13 prototype "The saved file" as bytes: its 37 lines, each ended by LF, the last one included, in UTF-8.
- `FILE_47` is the file of an English run of the example week, the block below as bytes in the same way.
- `NO_DISHES(W)` is `The menu for W has no dishes, so there is nothing to buy. No file was saved.`, and `NO_DISHES_ZH(W)` is `W 的菜单没有菜，所以没有要买的东西。没有保存文件。`.
- `FAIL(P, M)` is the three lines of a failure: P, then two spaces and the English text of M, then `No file was saved.`. `FAIL_ZH(P, M)` has the Chinese text of M and `没有保存文件。`. `LEFT(P, M, T)` has `No file was saved, but shop could not remove T. Delete it.` as its third line, and `LEFT_ZH(P, M, T)` has `没有保存文件，但 shop 没能删除 T。请删除它。`. P and T are full paths.
- `NO_MENU(W)`, `NO_MENU_ZH(W)`, `NOT_A_WEEK(V)`, and `NOT_A_WEEK_ZH(V)` are those of the F11 test plan, which `no_menu`, `no_menu_zh`, `not_a_week`, and `not_a_week_zh` of `tests/f11_texts.py` give.
- `PARENT(D)` is the message `The file cannot be written: "D" is not a folder.` and `无法写入文件：“D”不是文件夹。`, where D is `str` of a folder relative to the data folder.
- `HELP_EN_LINES` and `HELP_ZH_LINES` of `tests/f05_texts.py` are the two helps of the F05 prototype in full, 21 lines each.

`FILE_47`:

```text
# Shopping list for 2026-W47

16 to 22 November 2026: 4 meals, 9 dishes.

## Vegetables and fruit

- [ ] Tomato 600 g
- [ ] Choy sum 1.5 kg
- [ ] Scallion 5 stalks
- [ ] Ginger 6 slices
- [ ] Garlic 11 cloves

## Meat and seafood

- [ ] Minced pork 100 g
- [ ] Chicken wings 1 kg

## Eggs, dairy, and tofu

- [ ] Egg 5 pieces
- [ ] Tofu 1 block

## Rice, flour, and oil

- [ ] Rice 640 g
- [ ] Noodles 200 g

## Seasonings

- [ ] Doubanjiang 15 ml
- [ ] White pepper to taste

## Other

- [ ] Cola 2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper
```

The messages of `cli` in the cases have the texts of F05 design 2.10 with `shop`. The messages of the readers in the cases are those of section 2 of the F09 and F11 test plans: `FILE_MISSING`, `FILE_IS_FOLDER`, `MISSING_BRACE`, `FOLDER_MISSING`, `FOLDER_IS_FILE`, `NOT_A_RECIPE_ID` of a listing, `TOML_ENDING_NOT_SMALL`, `NOT_A_WEEK_NAME`, `UNKNOWN_RECIPE(recipe="tomato-eggs")`, `WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`, `UNKNOWN_MEAL(meal="M", meals="S")` of a menu, `UNKNOWN_INGREDIENT(name="豆瓣酱")` of a recipe, `SERVINGS_TOO_FEW(servings=0)`, `UNKNOWN_MEAL(meal="supper")` of the settings, `FILE_WRITE_DENIED`, and `FILE_WRITE_ERROR(reason="X")`. These others come from F03 design 2.9 and 2.10 and F08 design 3.2. `tests/f07_texts.py` and `tests/f08_texts.py` already hold them:

| Message | English | Chinese |
| --- | --- | --- |
| `PANTRY_INGREDIENT(name="sesame oil")` | `Unknown ingredient "sesame oil".` | `未知食材“sesame oil”。` |
| `ITEM_NOT_A_TEXT` | `This item must be a text in quotation marks.` | `这一项必须是放在引号里的文字。` |
| `MISSING_KEY(key="en")` | `The key "en" is missing.` | `缺少键“en”。` |
| `FOLDER_CREATE_DENIED` | `The folder cannot be created: access is denied.` | `无法创建文件夹：没有访问权限。` |
| `FOLDER_CREATE_ERROR(reason="X")` | `The folder cannot be created. The system says: X` | `无法创建文件夹。系统提示：X` |

The places in the cases are `line 11` (`第 11 行`), `item 3` (`第 3 项`), `ingredient 3` (`食材 3`), `ingredient 22` (`食材 22`), `servings` (`份数`), and `meals` (`餐次`), and for a menu `week` (`周次`), `Monday dinner` (`周一晚餐`), and `Saturday lunch` (`周六午餐`).

The cases use two builders of `tests/f13_support.py`, which follow design 2.2 and use no code of F13. `shop_list(F, week)` reads the week with `read_week` of `tests/f12_support.py`, which gathers the warnings in a list and checks that no reader gives an error, and gives `build_shopping_list` of its values. `shop_lines(S, L, P)` gives the lines of the output of 2.2 for the list S in the language L with the list file P. They are the heading, an empty line, the groups, then an empty line and the pantry line when `pantry_used` is not empty, then an empty line and `Saved P` or `已保存 P`. The heading is `Shopping list for W, D: M, N` or `W 购物清单，D：M，N`. D is F06's `date_range` of the week in L. M is `n meal` or `n meals`, or `n 餐`, and N is `n dish` or `n dishes`, or `n 道菜`. The groups are, for each group, its category's name in L and the lines of F02's `format_table(rows, indent=2, min_widths=(width,))`. `width` is the largest `display_width` of a line of a name of the whole list, each name split by `str.splitlines`. A list with no group has `There is nothing to buy.` or `没有要买的东西。` in place of the groups. The pantry line is `Not on the list, because they are in the pantry: X` or `常备，不用买：X`, with X as F02's `comma_list` of the names in L. `shop_file(S, L)` gives the bytes of the file of 2.2 in the same way, each line ended by LF. The builders hold their templates as literals. F13-T12, F13-T13, and F13-T14 check first that the builders give `SHOP_47`, `SHOP_47_ZH`, `FILE_47`, `PROTOTYPE_FILE`, and blocks B to H, so the builders agree with the prototype and with the design before F13-T29 and F13-T30 use them.

**Which case compares with the prototype.** F13-T12 compares the outputs of a run with `SHOP_47` and `SHOP_47_ZH`, and the file of the Chinese run with `PROTOTYPE_FILE`, byte for byte, as v0.1-S17 does. F13-T11 runs the design's example, which compares the Chinese file with the prototype's lines. The file of an English run has no prototype, so `FILE_47` is the block above, which the Test Manager built from the rules of design 2.2 and the design's example of 2.1 and checked with the model. The files of blocks E, F, and H are literals in the same way. The other cases build the expected bytes from the design with `shop_file`.

Blocks A to H hold the outputs of `shop` that the cases name and that no prototype shows. Each `PS>` line gives the command line without `--data`, as the prototypes do, and runs with `--data` and the folder of its block. The output of a `PS>` line is the lines that follow it, up to and including its last line. An empty line separates it from the next `PS>` line. Each output comes with exit code 0 and an empty err. The last line of each output names P, the full path of the list file in the folder of its case.

Block A is the output of input 1 of F13-T01, a direct call of `run` in English on `example`, with the settings of all three meals and 3 servings and `Arguments(("2026-W47",))`:

```text
Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes

Vegetables and fruit
  Tomato          900 g
  Choy sum        1.75 kg
  Scallion        7 stalks
  Ginger          6 slices
  Garlic          14 cloves
Meat and seafood
  Minced pork     150 g
  Chicken wings   1 kg
Eggs, dairy, and tofu
  Egg             8 pieces
  Tofu            2 blocks
Rice, flour, and oil
  Rice            800 g
  Noodles         300 g
Seasonings
  Doubanjiang     23 ml
  White pepper    to taste
Other
  Cola            2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper

Saved P
```

Block B, week B in a new example:

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 4 meals, 5 dishes

Vegetables and fruit
  Choy sum      2.5 kg
  Scallion      3 stalks
  Ginger        3 slices
  Garlic        17 cloves
Meat and seafood
  Pork belly    500 g
  Minced pork   100 g
Eggs, dairy, and tofu
  Tofu          1 block
Rice, flour, and oil
  Rice          320 g
Seasonings
  Rock sugar    30 g
  Doubanjiang   15 ml

Not on the list, because they are in the pantry: Cooking oil, Salt, Soy sauce, Sichuan pepper

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：4 餐，5 道菜

蔬菜水果
  菜心         2.5 kg
  葱           3 根
  姜           3 片
  大蒜         17 瓣
肉类水产
  五花肉       500 g
  猪肉末       100 g
蛋奶豆制品
  豆腐         1 块
米面粮油
  大米         320 g
调味品
  冰糖         30 g
  郫县豆瓣酱   15 ml

常备，不用买：食用油、盐、生抽、花椒

已保存 P
```

Block C, v0.1-S16 in the S16 folder:

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish

Vegetables and fruit
  Tomato     450 g
  Scallion   2 stalks
Eggs, dairy, and tofu
  Egg        5 pieces

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：1 餐，1 道菜

蔬菜水果
  番茄   450 g
  葱     2 根
蛋奶豆制品
  鸡蛋   5 个

常备，不用买：食用油、盐、糖

已保存 P
```

Block D, the chicken break S in a new example, the same for each S:

```text
PS> recipe-menu shop 2026-W47
Shopping list for 2026-W47, 16 to 22 November 2026: 4 meals, 9 dishes

Vegetables and fruit
  Tomato         600 g
  Choy sum       1.5 kg
  Scallion       5 stalks
  Ginger         6 slices
  Garlic         11 cloves
Meat and seafood
  Minced pork    100 g
  Chicken        1 kg
  wings
Eggs, dairy, and tofu
  Egg            5 pieces
  Tofu           1 block
Rice, flour, and oil
  Rice           640 g
  Noodles        200 g
Seasonings
  Doubanjiang    15 ml
  White pepper   to taste
Other
  Cola           2 cans

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar, Soy sauce, Sichuan pepper

Saved P
```

Block E, the water week in a new example. `FILE_E` and `FILE_E_ZH` are the file after each run:

```text
PS> recipe-menu shop 2026-W50
Shopping list for 2026-W50, 7 to 13 December 2026: 1 meal, 1 dish

There is nothing to buy.

Saved P

PS> recipe-menu shop 2026-W50 --lang zh
2026-W50 购物清单，2026年12月7日至13日：1 餐，1 道菜

没有要买的东西。

已保存 P
```

```text
# Shopping list for 2026-W50

7 to 13 December 2026: 1 meal, 1 dish.

There is nothing to buy.
```

```text
# 2026-W50 购物清单

2026年12月7日至13日：1 餐，1 道菜。

没有要买的东西。
```

Block F, the egg week in a new example. `FILE_F` and `FILE_F_ZH` are the file after each run:

```text
PS> recipe-menu shop 2026-W51
Shopping list for 2026-W51, 14 to 20 December 2026: 1 meal, 2 dishes

There is nothing to buy.

Not on the list, because they are in the pantry: Egg, Salt

Saved P

PS> recipe-menu shop 2026-W51 --lang zh
2026-W51 购物清单，2026年12月14日至20日：1 餐，2 道菜

没有要买的东西。

常备，不用买：鸡蛋、盐

已保存 P
```

```text
# Shopping list for 2026-W51

14 to 20 December 2026: 1 meal, 2 dishes.

There is nothing to buy.

Not on the list, because they are in the pantry: Egg, Salt
```

```text
# 2026-W51 购物清单

2026年12月14日至20日：1 餐，2 道菜。

没有要买的东西。

常备，不用买：鸡蛋、盐
```

Block G, v0.1-S18 in a new example with the changes of `s18_changes` of `tests/f12_support.py`:

```text
PS> recipe-menu shop 2026-W48
Shopping list for 2026-W48, 23 to 29 November 2026: 5 meals, 5 dishes

Vegetables and fruit
  Tomato         900 g
  Scallion       5 stalks + 1 bunch
  Ginger         3 slices
Meat and seafood
  Pork belly     500 g
Eggs, dairy, and tofu
  Egg            8 pieces
Rice, flour, and oil
  Noodles        400 g
Seasonings
  Soy sauce      30 ml + 10 g
  Rock sugar     30 g
  White pepper   to taste

Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar

Saved P

PS> recipe-menu shop 2026-W48 --lang zh
2026-W48 购物清单，2026年11月23日至29日：5 餐，5 道菜

蔬菜水果
  番茄       900 g
  葱         5 根 + 1 把
  姜         3 片
肉类水产
  五花肉     500 g
蛋奶豆制品
  鸡蛋       8 个
米面粮油
  面条       400 g
调味品
  生抽       30 ml + 10 g
  冰糖       30 g
  白胡椒粉   适量

常备，不用买：食用油、盐、糖

已保存 P
```

Block H, the rice week 2026-W49 in a new example. `FILE_H` and `FILE_H_ZH` are the file after each run. `H(W, D)`, `H_ZH(W, D)`, `FILE_H(W, D)`, and `FILE_H_ZH(W, D)` are these texts with the week W in place of `2026-W49` and the dates D, in the language of the text, in place of the dates of 2026-W49:

```text
PS> recipe-menu shop 2026-W49
Shopping list for 2026-W49, 30 November to 6 December 2026: 1 meal, 1 dish

Rice, flour, and oil
  Rice   160 g

Saved P

PS> recipe-menu shop 2026-W49 --lang zh
2026-W49 购物清单，2026年11月30日至12月6日：1 餐，1 道菜

米面粮油
  大米   160 g

已保存 P
```

```text
# Shopping list for 2026-W49

30 November to 6 December 2026: 1 meal, 1 dish.

## Rice, flour, and oil

- [ ] Rice 160 g
```

```text
# 2026-W49 购物清单

2026年11月30日至12月6日：1 餐，1 道菜。

## 米面粮油

- [ ] 大米 160 g
```

The dates of the weeks in the cases are these, in English and in Chinese: 2026-W01 `29 December 2025 to 4 January 2026` and `2025年12月29日至2026年1月4日`, 2026-W23 `1 to 7 June 2026` and `2026年6月1日至7日`, 2026-W47 `16 to 22 November 2026` and `2026年11月16日至22日`, 2026-W48 `23 to 29 November 2026` and `2026年11月23日至29日`, 2026-W49 `30 November to 6 December 2026` and `2026年11月30日至12月6日`, 2026-W53 `28 December 2026 to 3 January 2027` and `2026年12月28日至2027年1月3日`, and 2027-W01 `4 to 10 January 2027` and `2027年1月4日至10日`.

The cases split into these files, so that each file stays within the 500 lines of R06:

| File | Cases |
| --- | --- |
| `tests/test_f13_command.py` | F13-T01 and F13-T02 |
| `tests/test_f13_replace.py` | F13-T03 to F13-T06 |
| `tests/test_f13_replace_errors.py` | F13-T07 to F13-T10 |
| `tests/test_f13_shop.py` | F13-T11 to F13-T14 |
| `tests/test_f13_weeks_and_reads.py` | F13-T15 and F13-T16 |
| `tests/test_f13_stops.py` | F13-T17 and F13-T18 |
| `tests/test_f13_failures.py` | F13-T19 to F13-T21 |
| `tests/test_f13_cli.py` | F13-T22 |
| `tests/test_f13_integration.py` | F13-T23 to F13-T28 |
| `tests/test_f13_random.py` | F13-T29, with its generator |
| `tests/test_f13_performance.py` | F13-T30 |
| `tests/f13_support.py` | No tests. `EXISTS`, `ShopFaults`, and `shop_faults` (above). `folder_link`, which makes a junction on Windows and a symbolic link on Linux. `move_message(base)`, which moves a file of its own onto an empty folder of its own in `base`, takes the message of the row of 3.1 that the system's error gives, and removes both. `shop_list`, `shop_lines`, and `shop_file` (above). `pt01_shop` (section 3). The named changes of F13: the rice week, the water week, the egg week, the chicken break, the meat break, the missing name, shopping as a file, the ticked list, the old list, and the old temporary file. `held_open(path)`, a context manager that holds a file open with `open(path, "rb")`. It reuses `Faults`, `Rule`, `rule`, the effects, `call_main`, `system_message`, `dangling_link`, `tree`, and `full_record` of `tests/f08_support.py`, `read_week` and `s16_folder` of `tests/f12_support.py`, `menu_text`, `assert_failed`, and the named changes of `tests/f11_support.py`, and the helpers of `tests/f03_support.py`, `tests/f05_support.py`, `tests/f07_support.py`, `tests/f07_changes.py`, `tests/f09_support.py`, and `tests/f10_support.py` that the conventions name. `tests/f12_support.py` has 500 lines, the limit of R06, so the helpers of F13 go here. By the Test Manager's estimate, this file has about 400 lines, within the 500 of R06. |
| `tests/f13_texts.py` | No tests. `SHOP_47`, `SHOP_47_ZH`, `PROTOTYPE_FILE`, `FILE_47`, `NO_DISHES`, `FAIL`, `LEFT`, `PARENT`, and their Chinese forms, as literals. It reuses `HELP_EN_LINES` and `HELP_ZH_LINES` of `tests/f05_texts.py`, the messages of `tests/f07_texts.py`, `tests/f08_texts.py`, and `tests/f09_texts.py`, `stop`, `out`, and `err` of `tests/f09_texts.py`, and `no_menu`, `not_a_week`, and their Chinese forms of `tests/f11_texts.py`. |
| `tests/f13_blocks.py` | No tests. Blocks A to H and their files, as literals, and `H`, `H_ZH`, `FILE_H`, and `FILE_H_ZH`. They are a file of their own because, with them, `tests/f13_texts.py` would pass the 500 lines of R06. |
| `tests/conftest.py` | Unchanged. F13 uses its fixture `example_folder`, and pytest's `tmp_path`, `monkeypatch`, and `record_property`. |

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F13-T01 | unit | `SHOP_COMMAND`, `SHOP_COMMAND.run`, `main` | The example of 2.1. `SHOP_COMMAND` has the word `shop`, the usage `shop [WEEK]` and `shop [周]`, the help line of the F05 prototype, the optional argument `WEEK` that does not repeat, no options, and `FolderUse.READ`. Its `run` takes the week from the argument and `context.today`, reads the menu with the meals and the servings of `context.settings`, writes in `context.lang` and never in the language of `context.settings`, and keeps no state from one call to the next. The whole help of the real `COMMANDS` is the two helps of the F05 prototype in full, with 21 lines and the second column after 21 columns (2.1, choices 1 to 5). | The example's lines, with `folder` as `example` and `home` as `home`. The `# raises` line runs inside `pytest.raises(UsageError)` with a new `Context` of the same values and new streams. Then, each with new streams: 1. `run` with `Context(Lang.EN, example, Settings(Lang.ZH, tuple(Meal), 3), out, err, date(2030, 1, 1))` and `Arguments(("2026-W47",))`. 2. `run` with `Context(Lang.ZH, example, Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2), out, err, date(2026, 11, 17))` and `Arguments(())`. 3. `run` with `Context(Lang.EN, example, Settings(Lang.EN, (Meal.DINNER,), 5), out, err, date(2026, 11, 17))` and `Arguments(())`. 4. The example's run with `Arguments(("next",))`, twice more. 5. `--help` and `--help --lang zh` through `call`, with the real `COMMANDS`. | Every assertion of the example holds, and the `# raises` line raises `UsageError`, after which both of its streams are empty and `shopping/` holds only `2026-W47.md`, with the bytes that the example's run wrote. 1. 0, out the lines of block A with P as `example/shopping/2026-W47.md`, and an empty err. Each dish that gives no servings counts 3, so the list has `Tomato 900 g`, `Choy sum 1.75 kg`, `Tofu 2 blocks`, and `Doubanjiang 23 ml`. The file starts with `# Shopping list for 2026-W47\n` and holds the line `- [ ] Tomato 900 g`. 2. 0, out `SHOP_47_ZH(P)`, an empty err, and the file holds `PROTOTYPE_FILE`: the week of 2026-11-17 is 2026-W47. 3. 1, an empty out, and err `STOP(menus/2026-W47.toml, Saturday lunch, UNKNOWN_MEAL(meal="lunch", meals="dinner") of a menu)`. The file keeps the bytes of 2. 4. Each run gives 0, out `SHOP_47(P)`, and an empty err, and the file holds `FILE_47` after each. 5. Exit code 0, an empty err, and out the lines of `HELP_EN_LINES` and of `HELP_ZH_LINES`: 21 lines each, with `  shop [WEEK]        Make the shopping list of a week menu.` and `  shop [周]          生成一个周菜单的购物清单。` right after the line of `menu show`. |
| F13-T02 | unit | `SHOP_COMMAND.run` | Step 1 of 2.2. `run` turns the value of `WEEK` into a week with `week_from_argument` before it touches the disk or writes any output. A value that is not a week raises `UsageError(NOT_A_WEEK, None, week=value)`, which has no hint. `this`, `next`, an ISO week, and no value pass (2.1 Errors, choice 2). | 1 and 2 each call with new streams and `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`, inside `shop_faults(tmp_path)`. 1. Inside `pytest.raises(UsageError)`: `Arguments((V,))` for each V of `"2026-W99"`, `"Next"`, `"THIS"`, `""`, `" 2026-W47"`, `"2026-W47\n"`, `"2026-w47"`, `"2026-W7"`, `"2025-W53"`, `"2026-W00"`, `"this week"`, and `"\uff12\uff10\uff12\uff16-W47"`, which writes 2026 in full-width digits. 2. `Arguments(V)` for each V of `()`, `("this",)`, `("next",)`, `("2026-W47",)`, `("2026-W53",)`, and `("0001-W01",)`. 3. The calls of 1 with a context on `example` with an old list, inside `shop_faults(example.root)`. | 1. Each error's `text(Lang.EN)` is `NOT_A_WEEK(V)`, its `text(Lang.ZH)` is `NOT_A_WEEK_ZH(V)`, and its `hint` is `None`. Both streams are empty after each call, and the record and the listings of the harness are empty. 2. No call raises. Each gives 1, an empty out, and err `STOP(catalog.toml, FILE_MISSING)`, and `tmp_path / "missing"` still does not exist. 3. The errors of 1, with empty streams, an empty record, and no listing. The old list keeps `b"old\n"`. |
| F13-T03 | unit | `replace_file` | The example of 3.1: a new `shopping/` and a new file, a file replaced, a folder at the file's path that both systems refuse to replace, `shopping` as a file, and three wrong calls (3.1). | The example's lines, with `tmp` as the empty folder `tmp_path / "tmp"`. Each `# raises` line runs inside `pytest.raises` with the error that it names. | Every assertion of the example holds, and each of its three `# raises` lines raises its error. Afterwards, the tree of `tmp` holds only `recipe-menu`, `recipe-menu/shopping`, `recipe-menu/shopping/2026-W47.md` with `"# 2\n番茄 600 g\n".encode("utf-8")`, the empty folder `recipe-menu/shopping/2026-W48.md`, `other`, and the empty file `other/shopping`. No entry ends with `.tmp`. |
| F13-T04 | unit | `replace_file` | Step 1. A wrong call raises before the call touches the disk: a path outside the root, the root itself, a relative path, and a text that UTF-8 cannot encode, also when the file's folder is missing (3.1 step 1 and Errors). | `F` with no `F.shopping`, and each call inside `shop_faults(base)`: 1. `replace_file(F, base / "elsewhere.md", "")`. 2. `replace_file(F, F.root, "")`. 3. `replace_file(F, Path("shopping", "2026-W47.md"), "")`. 4. `replace_file(F, Q, "\udc80")`. 5. `replace_file(F, Q, "ok\n\ud800")`. 6. `replace_file(F, F.root / "a" / "b.md", "\udc80")`. | 1 to 3 raise `ValueError`, and 4 to 6 raise `UnicodeEncodeError`. After every call, the record and the listings are empty, and the tree of `base` is the same as before it: neither `F.shopping` nor `F.root / "a"` exists. |
| F13-T05 | unit | `replace_file` | Steps 2 to 5 for a call that works. Nothing at the file's folder gives that one folder, made with no parents. An entry at `temp` is removed first, and a missing one is no error. The call opens `temp` once in mode `x`, writes the UTF-8 bytes of the text with no byte order mark and with the line ends of the text, also an empty text, and moves `temp` over the file, which creates or replaces it. It reads and lists nothing and gives `CREATED`. Any folder inside the root works, and so does a link that leads to a folder (3.1 steps 2 to 5, point C). | `F` and the text `"# 1\n"` unless the input says otherwise, each input with its own `base`, and each call inside `shop_faults(base)`: 1. An empty `F.shopping`, and Q. 2. No `F.shopping`, and Q. 3. `F.shopping` holds Q with `b"old\n"`, and the text `"# 2\n番茄 600 g\n"`. 4. `F.shopping` holds Q with `b"old\n"` and T with `b"half\n"`. 5. An empty `F.shopping`, and the text `""`. 6. An empty `F.shopping`, and the text `"a\r\nb\n"`. 7. `F.menus` holds `2026-W47.toml` with `b'week = "2026-W47"\n'`, the path `F.menu_file("2026-W47")`, and the text `'week = "2026-W47"\n\n[monday]\n'`, as F14's `menu suggest` will replace a menu. 8. The path `F.root / "notes.md"`. 9. `F.shopping` is a link to the empty folder `base / "synced"`, made with `folder_link`, and Q. 10. `F.shopping` holds `2026-W48.md` with `b"other\n"` and `notes.txt` with `b"x\n"`, and Q. | Each call gives a result equal to `FileCreation(FileOutcome.CREATED)`. The record of 1, 3 to 6, 9, and 10 is `unlink T`, `open T`, and `move T Q`, and the listings are empty. 2. `mkdir S` and then the record of 1, and `F.shopping` is a folder that holds only Q. 7. `unlink recipe-menu/menus/2026-W47.toml.tmp`, `open recipe-menu/menus/2026-W47.toml.tmp`, and `move recipe-menu/menus/2026-W47.toml.tmp recipe-menu/menus/2026-W47.toml`. 8. The same with `recipe-menu/notes.md.tmp` and `recipe-menu/notes.md`. No record holds `read`. The file of the call then holds: 1, 2, 4, and 8 to 10. `b"# 1\n"`. 3. `"# 2\n番茄 600 g\n".encode("utf-8")`, with no `b"\xef\xbb\xbf"`. 5. `b""`. 6. `b"a\r\nb\n"`. 7. `b'week = "2026-W47"\n\n[monday]\n'`. In 4, T is gone. In 9, `base / "synced"` holds only `2026-W47.md`, and `F.shopping` is still a link. In 10, the two other entries keep their bytes and their modification times. In every input, no entry under `base` ends with `.tmp`. |
| F13-T06 | unit | `replace_file` | Step 2 when something other than a folder is at the file's folder: a file, a dangling link, or a file higher up. The call gives `FAILED` with `PARENT_NOT_A_FOLDER`, whose `folder` is `str(folder.relative(parent))`, and with the file to write as the problem's file. It touches nothing (3.1 step 2, point C). | Each input with its own `base`, and each call inside `shop_faults(base)` with the text `"x"`: 1. `F.shopping` is a file with `b"x\n"`, and Q. 2. A dangling link at `F.shopping`, and Q. 3. `F.root / "notes.md"` is a file with `b"x\n"`, and the path `F.root / "notes.md" / "2026-W47.md"`. 4. `F.root / "a"` is a folder that holds the empty file `b`, and the path `F.root / "a" / "b" / "c.md"`. | Each call gives `FAILED`, with an empty `left` and this problem: 1. `shopping/2026-W47.md: PARENT(shopping)`. 2. The same. 3. `notes.md/2026-W47.md: PARENT(notes.md)`. 4. `a/b/c.md: PARENT(a/b)`, where `a/b` is `str(Path("a", "b"))`, so `a\b` on Windows. The record is empty, and the full record of `base` is the same after the call as before it. |
| F13-T07 | unit | `replace_file` | Step 2 when the creation of the folder fails. The first two rows of the table of 3.1 give the result: `PermissionError` gives `FOLDER_CREATE_DENIED`, and any other `OSError`, `FileExistsError` included, gives `FOLDER_CREATE_ERROR` with the error's `strerror`, or the name of its class when `strerror` is `None` or empty. The problem names the file to write, not its folder. A probe that fails counts as false. Ctrl+C goes on, with nothing to remove (3.1 step 2 and its error table, Architect note 1). | `F` with no `F.shopping`, Q, and the text `"x"` unless the input says otherwise, each input with its own `base`, and each call inside `shop_faults(base, *rules)`: 1. `mkdir F.shopping: DENIED`. 2. `mkdir F.shopping: IO`. 3. `mkdir F.shopping: EXISTS`. 4. `mkdir F.shopping: OSError()`. 5. `mkdir F.shopping: TimeoutError()`. 6. `mkdir F.shopping: EMPTY_IO`. 7. No rule, and no `F.root`. 8. No rule, and the path `F.root / U / "x.md"`, where U is `a?b` on Windows and 256 times `a` on Linux. 9. `mkdir F.shopping: CTRL_C`, inside `pytest.raises(KeyboardInterrupt)`. | 1 to 8 give `FAILED`, with an empty `left` and this problem: 1. `shopping/2026-W47.md: FOLDER_CREATE_DENIED`. 2. `shopping/2026-W47.md: FOLDER_CREATE_ERROR(reason="Input/output error")`. 3. The same with `reason="File exists"`, not `FOLDER_EXISTS`. 4. The same with `reason="OSError"`. 5. The same with `reason="TimeoutError"`. 6. The same with `reason="OSError"`. 7. `shopping/2026-W47.md` and `system_message("folder", F.shopping)`, taken before the call, which is `FOLDER_CREATE_ERROR` with the system's reason for a missing folder above. 8. `U/x.md` and `system_message("folder", F.root / U)`, taken before the call. 9. The call raises `KeyboardInterrupt`. The record of 1 to 7 and 9 is `mkdir S` alone, and that of 8 is `mkdir recipe-menu/U` alone. The tree of `base` is the same after each call as before it. |
| F13-T08 | unit | `replace_file` | Steps 3 and 4 before `temp` exists. The rows of steps 3 to 5 give the result: `PermissionError` gives `FILE_WRITE_DENIED`, and any other `OSError`, `FileExistsError` included, gives `FILE_WRITE_ERROR` with its reason, never `EXISTS` or `FILE_EXISTS`. A failed removal of an old `temp` and a failed open created nothing, so the call removes nothing, and a `temp` that another program created stays. The old file keeps its bytes (3.1 steps 3 and 4, its error table, Architect note 1). | `F` whose `F.shopping` holds Q with `b"old\n"`, and in 1 and 2 also T with `b"half\n"`. The text `"new\n"`. Each input with its own `base`, and each call inside `shop_faults(base, *rules)`: 1. `unlink T: DENIED`. 2. `unlink T: IO`. 3. `open T: DENIED`. 4. `open T: IO`. 5. `open T: EXISTS`. 6. `open T: race`. 7. `open T: TimeoutError()`. 8. `open T: EMPTY_IO`. | Each call gives `FAILED`, with an empty `left` and this problem: 1. `shopping/2026-W47.md: FILE_WRITE_DENIED`. 2. `shopping/2026-W47.md: FILE_WRITE_ERROR(reason="Input/output error")`. 3. `FILE_WRITE_DENIED`. 4. `FILE_WRITE_ERROR(reason="Input/output error")`. 5. `FILE_WRITE_ERROR(reason="File exists")`. 6. `FILE_WRITE_ERROR(reason="File exists")`: both systems give that `strerror` for an exclusive open of a file that is there. The Test Manager checked it on Troy's PC, and Linux gives the C library's text for `EEXIST`, the same words. 7. `FILE_WRITE_ERROR(reason="TimeoutError")`. 8. `FILE_WRITE_ERROR(reason="OSError")`. The record of 1 and 2 is `unlink T` alone, and T keeps `b"half\n"`. The record of 3 to 8 is `unlink T` and `open T`, with no second `unlink`. T does not exist in 3 to 5, 7, and 8, and in 6 it holds the other program's `b"mine\n"`. In every input, Q keeps `b"old\n"`, and `F.shopping` holds no entry other than Q and, in 1, 2, and 6, T. |
| F13-T09 | unit | `replace_file` | After the open. `temp` counts as created from the moment that its open succeeds. A write, a close, or a move that fails gives `FAILED`, and the call removes `temp` first. A removal that fails puts the full path of `temp` in `left`. The call writes with one `write`, also an empty text. The old file changes only through the move, so it keeps its bytes. A folder that the call created stays when a later step fails (3.1 steps 4 and 5, the paragraph after its error table, point C). | `F` whose `F.shopping` holds Q with `b"old\n"`, and the text `"0123456789\n"`, unless the input says otherwise. Each input with its own `base`, and each call inside `shop_faults(base, *rules)`: 1. `write T: NO_SPACE`. 2. `write T: DENIED`. 3. `write T: IO` and `unlink T: later DENIED`. 4. `write T: NO_SPACE`, with the text `""`. 5. `close T: NO_SPACE`. 6. `close T: DENIED` and `unlink T: later IO`. 7. `move T: DENIED`. 8. `move T: IO`. 9. `move T: OSError()`. 10. `move T: DENIED` and `unlink T: later DENIED`. 11. No rule, and `F.shopping` holds the empty folder `2026-W47.md` in place of Q. 12. No `F.shopping`, and `write T: NO_SPACE`. 13. No `F.shopping`, and `move T: DENIED`. | Each call gives `FAILED`, with this problem and `left`: 1. `shopping/2026-W47.md: FILE_WRITE_ERROR(reason="No space left on device")`, and `()`. 2. `FILE_WRITE_DENIED`, and `()`. 3. `FILE_WRITE_ERROR(reason="Input/output error")`, and `(T,)` as a full path. 4. The result of 1. 5. The result of 1. 6. `FILE_WRITE_DENIED`, and `(T,)`. 7. `FILE_WRITE_DENIED`, and `()`. 8. `FILE_WRITE_ERROR(reason="Input/output error")`, and `()`. 9. `FILE_WRITE_ERROR(reason="OSError")`, and `()`. 10. `FILE_WRITE_DENIED`, and `(T,)`. 11. `shopping/2026-W47.md` and `move_message(base)`, taken before the call: `FILE_WRITE_DENIED` on Windows and `FILE_WRITE_ERROR(reason="Is a directory")` on Linux, and `()`. 12. The result of 1. 13. The result of 7. The record of 1, 2, 4, and 5 is `unlink T`, `open T`, and `unlink T`, and T is gone. The record of 3 and 6 is the same: T holds `b"01234"` in 3 and `b"0123456789\n"` in 6. The record of 7 to 9 and 11 is `unlink T`, `open T`, `move T Q`, and `unlink T`, and T is gone. The record of 10 is the same, and T holds `b"0123456789\n"`. The record of 12 and 13 is `mkdir S` and then the record of 1 or of 7, and `F.shopping` stays, an empty folder. In 1 to 10, Q keeps `b"old\n"`, and in 11 it stays an empty folder. On Windows, the system removes or moves T only after the call has closed it, so 1, 2, 4, 5, 7 to 9, and 11 also check that the call closes the file. |
| F13-T10 | unit | `replace_file` | An interruption or a bug. Any exception after the open that is not an `OSError`, such as `KeyboardInterrupt` for Ctrl+C or the exception of a bug, runs the same removal in a `finally` block and goes on, so the call gives no result. A Ctrl+C inside `open`, after the system created `temp` but before the call got it, leaves an empty `temp`, and the next call removes it in step 3. A Ctrl+C before the open goes on with nothing to remove. The old file keeps its bytes (3.1, the paragraph after its error table, choice 6). | `F` whose `F.shopping` holds Q with `b"old\n"`, and the text `"0123456789\n"`. Each input with its own `base`, and each call inside `shop_faults(base, *rules)`, inside `pytest.raises` with the exception of its rule: 1. `write T: BUG`. 2. `write T: CTRL_C`. 3. `close T: CTRL_C`. 4. `move T: CTRL_C`. 5. `write T: CTRL_C` and `unlink T: later DENIED`. 6. `write T: CTRL_C` and `unlink T: later CTRL_C`. 7. `open T: after CTRL_C`. 8. After 7, with the same `F` and no rule: `replace_file(F, Q, "# 1\n")`, not inside `pytest.raises`. 9. T with `b"half\n"`, and `unlink T: CTRL_C`. | 1 to 7 and 9 raise the exception of their rule. The record of 1 to 3 is `unlink T`, `open T`, and `unlink T`, and that of 4 is `unlink T`, `open T`, `move T Q`, and `unlink T`, and T is gone. 5 and 6 have the record of 1, and T holds `b"01234"`. 7. The record is `unlink T` and `open T`, with no second `unlink`, and T is an empty file. 8. `FileCreation(FileOutcome.CREATED)`, the record `unlink T`, `open T`, and `move T Q`, T is gone, and Q holds `b"# 1\n"`. 9. The record is `unlink T` alone, and T keeps `b"half\n"`. In 1 to 7 and 9, Q keeps `b"old\n"`. |
| F13-T11 | functional | `recipe-menu shop`, `main` | The example of 2.2, in order, with the real commands: the English list that creates `shopping/`, the Chinese output and file of the prototype, "No menu, or an empty menu" in both languages, a wrong week, "A menu with a mistake", which keeps the file, and `shopping` as a file (2.2, choices 2 to 7). | The example's lines, with `folder` as `example` and `home` as `home`, and the example's `run`, which calls `main` with no `commands`. | Every assertion of the example holds. |
| F13-T12 | functional | `recipe-menu shop`, `main` | v0.1-S17 at `main`, and the F13 prototype "In English", "In Chinese", and "The saved file" in full. A run saves the list in its language and replaces the week's file, so a ticked list loses its ticks, and an old temporary file is gone after a run. `shopping\` then holds only the week's file. The amounts of every group start at one column, by display width, in both languages (v0.1-S25). The prototype's `shop next` and Chinese settings give the same (choices 4 to 6, point C). | X is a new example with no `shopping/`. 1. `shop 2026-W47` in X. 2. `shop 2026-W47 --lang zh` in X. 3. The ticked list and the old temporary file in X, then `shop next` in X. 4. `shop next --lang zh` in X. 5. Chinese settings and an empty shopping in a new example Y: `shop 2026-W47`, then `shop 2026-W47 --lang en`. 6. The builders: `shop_lines` and `shop_file` of `shop_list(X, IsoWeek(2026, 47))` in EN and in ZH, with P of X. | 1. `(0, out SHOP_47(P))`. `X/shopping` is a new folder that holds only `2026-W47.md`, with `FILE_47`: UTF-8 with no byte order mark, LF line ends, and 14 lines that start with `- [ ] `. 2. `(0, out SHOP_47_ZH(P))`, and the file holds `PROTOTYPE_FILE`, byte for byte. `X/shopping` holds only that file. In the English output, the `display_width` of what comes before each amount is 18, and in the Chinese output it is 15: 2 for the indent, 13 or 10 for the widest name, `Chicken wings` or `郫县豆瓣酱`, and 3. 3. `(0, out SHOP_47(P))`. The file holds `FILE_47`, with no `- [x]`, T is gone, and `X/shopping` holds only `2026-W47.md`. 4. `(0, out SHOP_47_ZH(P))`, and the file holds `PROTOTYPE_FILE`. 5. `(0, out SHOP_47_ZH(P))` with P of Y, and the file holds `PROTOTYPE_FILE`. Then `(0, out SHOP_47(P))`, and the file holds `FILE_47`. 6. The lines of `SHOP_47(P)` and `SHOP_47_ZH(P)`, and the bytes of `FILE_47` and `PROTOTYPE_FILE`. |
| F13-T13 | functional | `recipe-menu shop` | Choice 4 for other weeks. A group heading has no indent. Each line is two spaces, the name padded to the widest name of the whole list, three spaces, and the amounts, so each week gets the width of its own names. The groups and their lines follow the catalog's order. A name with a line break takes two lines, the amount follows its first line, and every heading stays in its place. A category name with a line break gives a heading of two lines. No warning is written. The pantry line follows `pantry_used`, and a menu that uses no pantry ingredient gives no pantry line, in the terminal or in the file (choices 4, 5, and 8). | 1. Week B in a new example: the two lines of block B. 2. The S16 folder: the two lines of block C. 3. For each S, the chicken break S in a new example: the line of block D. 4. The meat break in a new example: `shop 2026-W47`. 5. The rice week 2026-W49 in a new example: the two lines of block H. 6. The builders with the lists of 1, 2, 3, and 5, through `shop_list`. | 1 to 3 and 5. Each line gives its output in block B, C, D, or H, with exit code 0 and an empty err. 1. The amounts start 14 columns after the indent in English, after `Doubanjiang`, and 13 in Chinese, after `郫县豆瓣酱`. `Pork belly` comes before `Minced pork`. The warning of `red-braised-pork` is not written. After the English line, the file starts with `# Shopping list for 2026-W48\n\n23 to 29 November 2026: 4 meals, 5 dishes.\n`, and after each line the file holds `shop_file` of the list in the language of the line. 2. The amounts start 11 and 7 columns after the indent, after `Scallion` and `番茄`, and the counts are `1 meal, 1 dish` and `1 餐，1 道菜`. Each file holds `shop_file` of the list in its language. 3. The same output for each S, with no U+000D and no U+2028 in it, and the line `  wings` has no space at its end. The file holds `shop_file` of the list in English, so for S as `\n` it holds the lines `- [ ] Chicken` and `wings 1 kg` where `FILE_47` holds `- [ ] Chicken wings 1 kg`. 4. `(0, out L)`, where L is `SHOP_47(P)` with the line `Meat and seafood` replaced by the two lines `Meat` and `and seafood`. The file holds `FILE_47` with the line `## Meat and seafood` replaced by the lines `## Meat` and `and seafood`. 5. Neither output nor file holds a pantry line, and the files are `FILE_H` and `FILE_H_ZH`. 6. The lines of blocks B, C, D, and H, and the files of 1, 2, 3, and 5. |
| F13-T14 | functional | `recipe-menu shop`, `main` | Choice 7. A menu with no dish gives `NO_DISHES` on the output stream with exit code 0. `shop` calls no `replace_file`, so it creates no folder and writes no file, and the old file of the week stays (v0.1-S14). A menu whose dishes use only recipes with no ingredients, or only pantry ingredients, gives the heading, `NOTHING_TO_BUY` in place of the groups, the pantry line when the menu uses a pantry ingredient, and `SAVED`, and saves a file with `NOTHING_TO_BUY` in place of the groups (choice 7, point A). | 1. An empty-menus example X with `menus/2026-W46.toml` holding `menu_text(2026-W46, [lunch, dinner])`: `shop`, then `shop this --lang zh`, each inside `shop_faults(X.root)`. 2. The same two lines in a new example Y with that menu file, an empty shopping, and `shopping/2026-W46.md` with `b"old\n"`. 3. A new example with `menus/2026-W52.toml` written as `week = "2026-W52"\n`: `shop 2026-W52`. 4. The water week in a new example: the two lines of block E. 5. The egg week in a new example: the two lines of block F. | 1. `(0, out [NO_DISHES(2026-W46)])`, then `(0, out [NO_DISHES_ZH(2026-W46)])`. The record of each is `read settings.toml`, `read catalog.toml`, `read pantry.toml`, and `read menus/2026-W46.toml`, with no `mkdir`, `unlink`, `open`, or `move`, and the listings are `recipes` and then `menus`. X has no `shopping`. 2. The same two results. `Y/shopping` holds only `2026-W46.md`, which keeps its bytes and its modification time. 3. `(0, out [NO_DISHES(2026-W52)])`, and the folder has no `shopping`. 4. The two outputs of block E, and the file holds `FILE_E` after the first line and `FILE_E_ZH` after the second. 5. The two outputs of block F, and the file holds `FILE_F`, then `FILE_F_ZH`. The builders give the outputs and the files of 4 and 5. |
| F13-T15 | functional | `recipe-menu shop`, `main` | Choice 2. `shop` gets its week from `context.today`: no value and `this` give the week of today, and `next` gives the week of the date 7 days later, also across a year. Every line names the week as `str(week)`. A week inside one month, across two months, and across two years works, and so does a week 1 that crosses a year. A value of `WEEK` that is not a week gives `NOT_A_WEEK` alone on the error stream, with exit code 2, no hint, and the language of the output, before any file is touched (2.1 and 2.2 Errors, choice 2). | F is a new example with the rice week W for each W of `2026-W01`, `2026-W23`, `2026-W49`, `2026-W53`, and `2027-W01`. 1. In F: `shop W` and `shop W --lang zh` for each of these W. 2. In F, on each date D below: `shop`, `shop this`, and `shop next --lang zh`. The dates with the week T of D and the week N 7 days later are: 2026-11-10 with `2026-W46` and `2026-W47`, 2026-11-22 with `2026-W47` and `2026-W48`, 2026-12-27 with `2026-W52` and `2026-W53`, 2026-12-30 with `2026-W53` and `2027-W01`, 2027-01-03 with `2026-W53` and `2027-W01`, and 2025-12-29 with `2026-W01` and `2026-W02`. 3. In `example` with an old list, each line inside a new `shop_faults(example.root)`: `shop V` for each V of `"2026-W99"`, `"Next"`, `""`, `"2026-w47"`, `"2025-W53"`, and `" this"`. 4. In `example`: `shop 2026-W99 --lang zh` and `shop Next --lang zh`. 5. Each in a new example: the catalog brace and `shop 2026-W99`, the pantry mistake and `shop Next`, and shopping as a file and `shop ""`. 6. Chinese settings in a new example: `shop 2026-W99`, then `shop 2026-W99 --lang en`. | 1. `(0, out H(W, D))` and `(0, out H_ZH(W, D))`, with the dates D of W. The file holds `FILE_H(W, D)` after the first line and `FILE_H_ZH(W, D)` after the second, such as `# Shopping list for 2026-W53` and `28 December 2026 to 3 January 2027: 1 meal, 1 dish.` at the top. 2. `shop` and `shop this` each give the result of `shop T` in F, and `shop next --lang zh` gives the result of `shop N --lang zh`. For a week with a menu in F, that is the result of 1, or `(0, out SHOP_47(P))` and `(0, out SHOP_47_ZH(P))` for 2026-W47. For a week with no menu, it is `(1, err [NO_MENU(T)])` or `(1, err [NO_MENU_ZH(N)])`, such as `NO_MENU(2026-W46)` and `NO_MENU_ZH(2026-W48)`. 3. Each line gives `(2, err [NOT_A_WEEK(V)])`. The record is `read settings.toml` alone, there is no listing, and the full record of the example is the same after the lines as before them. 4. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` and `(2, err [NOT_A_WEEK_ZH("Next")])`. 5. `(2, err [NOT_A_WEEK(V)])` for the V of each line, and the file `shopping` keeps its bytes. 6. `(2, err [NOT_A_WEEK_ZH("2026-W99")])` and `(2, err [NOT_A_WEEK("2026-W99")])`. |
| F13-T16 | functional | `recipe-menu shop`, `main` | The files that `shop` reads and writes (choice 3, 2.2 side effects). It reads the catalog, then the pantry, lists `recipes/` once and `menus/` once, reads the week's file once, and reads each recipe that a dish names once, in the order of the first dish that names it: Monday to Sunday, the meals in the order of the settings, and the dishes in the file's order. Then it writes through `replace_file`. It reads no recipe that the menu does not name, no other menu, and no file in `shopping/`. After an error or a week with no menu it reads nothing more and writes nothing, and after a wrong week it reads no file. | Each line of 1 to 6 inside a new `shop_faults(F.root)`, for the folder F of the line. 1. In `example`: `shop 2026-W47`, then `shop 2026-W47 --lang zh`. 2. Week B in a new example: `shop 2026-W48`. 3. In `example`: `shop 2026-W48`. 4. In `example`: `shop 2026-W99`, then `shop 2026-W47 --help`. 5. Each in a new example, with `shop 2026-W47`: the catalog brace, the pantry mistake, Rice Bowl, `menus/2026-w48.toml` written empty, the menu typo, and the mapo mistake. 6. A new example whose `shopping/` holds the old list, `2026-W48.md` with `b"other\n"`, and `notes.txt` with `b"x\n"`: `shop 2026-W47`. | R47 is `read settings.toml`, `read catalog.toml`, `read pantry.toml`, `read menus/2026-W47.toml`, and `read recipes/ID.toml` for each ID of `tomato-egg`, `choy-sum`, `rice`, `mapo-tofu`, `tomato-egg-noodles`, and `cola-wings`, in this order. W47 is `unlink shopping/2026-W47.md.tmp`, `open shopping/2026-W47.md.tmp`, and `move shopping/2026-W47.md.tmp shopping/2026-W47.md`. 1. R47, `mkdir shopping`, and W47, the listings `recipes` and then `menus`, and `(0, out SHOP_47(P))`. Then R47 and W47 with no `mkdir`, the same listings, and `(0, out SHOP_47_ZH(P))`. `choy-sum` and `rice` are read once, although 2 and 3 dishes name them, and neither `recipes/red-braised-pork.toml` nor another menu is read. 2. `read settings.toml`, `read catalog.toml`, `read pantry.toml`, `read menus/2026-W48.toml`, and the recipes `mapo-tofu`, `rice`, `choy-sum`, and `red-braised-pork`, in this order, then `mkdir shopping` and the three calls of W47 for `2026-W48`, the same listings, and the first output of block B. The file lists Monday's dinner before its lunch, and the reads follow the settings. 3. `read settings.toml`, `read catalog.toml`, and `read pantry.toml`, the same listings, and `(1, err [NO_MENU(2026-W48)])`. 4. `read settings.toml` alone, no listing, and `(2, err [NOT_A_WEEK("2026-W99")])`. Then the same record, and exit code 0, an empty err, and on out the same text as `--help` with no folder. 5. In order: `read settings.toml` and `read catalog.toml` with no listing; the same and `read pantry.toml` with no listing; those three reads with the listing `recipes` alone; those three reads with both listings; those three reads and `read menus/2026-W47.toml` with both listings; and R47 up to `read recipes/mapo-tofu.toml`, with both listings. No record holds `mkdir`, `unlink`, `open`, or `move`, and each result is the result of its folder in F13-T17. 6. R47 and W47, with no `read shopping/...`, and `(0, out SHOP_47(P))`. `2026-W48.md` and `notes.txt` keep their bytes and their modification times. |
| F13-T17 | functional | `recipe-menu shop`, `recipe-menu check` | Choice 3. The first error of each reader stops `shop`, with the three lines of `stop_at_error` in the language of the output, exit code 1, nothing on the output stream, and no file written. The catalog comes first, then the pantry, whatever the week, then the listing of `recipes/`, then the listing of `menus/`, also for another file, then the week's file, and then the recipes in the order of the first dish. An error in a recipe that the menu does not name changes nothing, and so does another menu. An ingredient whose name lacks a language is an error of the catalog. The error that stopped `shop` is among the errors of `check` (2.2 steps 2 to 8, choice 3). | Each input of 1 to 27 in a new example, with `shop 2026-W47`, `shop 2026-W47 --lang zh`, `check`, and `check --lang zh`: 1. No catalog. 2. The catalog brace. 3. The missing name. 4. The pantry mistake. 5. The pantry item. 6. No pantry. 7. No recipes folder. 8. Recipes as a file. 9. Rice Bowl. 10. Capital rice. 11. No menus folder. 12. Menus as a file. 13. `menus/2026-w48.toml` written empty. 14. `menus/plan.toml` written empty. 15. `menus/2026-W48.TOML` written empty. 16. The menu typo. 17. The menu mistakes of v0.1-S07. 18. The mapo mistake. 19. Rice at 0. 20. The mapo mistake and rice at 0. 21. The catalog brace and the pantry mistake. 22. The pantry mistake and Rice Bowl. 23. The pantry mistake and no menus folder. 24. Rice Bowl and `menus/2026-w48.toml` written empty. 25. `menus/2026-w48.toml` written empty, and the menu typo. 26. The menu typo and the mapo mistake. 27. Folder x, and `[wednesday]\nlunch = []\ndinner = []` replaced by `[wednesday]\nlunch = []\ndinner = ["x"]` in `menus/2026-W47.toml`. Then, each in a new example, with `shop 2026-W47` alone: 28. Folder x. 29. `servings = 2` replaced by `servings = 0` in `recipes/red-braised-pork.toml`. 30. `menus/2026-W48.toml` written with `[[[\n`. Then, each in a new example, with `shop 2026-W48` alone: 31. `menus/2026-w48.toml` written empty. 32. The pantry mistake. | 1 to 27. `shop 2026-W47` gives `(1, err STOP(W, M))`, and `shop 2026-W47 --lang zh` gives `(1, err STOP_ZH(W, M))`, with W and M: 1. `catalog.toml` and `FILE_MISSING`. 2. `catalog.toml, line 11` and `MISSING_BRACE`. 3. `catalog.toml, ingredient 22` and `MISSING_KEY(key="en")`. 4. `pantry.toml, item 3` and `PANTRY_INGREDIENT(name="sesame oil")`. 5. `pantry.toml, item 3` and `ITEM_NOT_A_TEXT`. 6. `pantry.toml` and `FILE_MISSING`. 7. `recipes` and `FOLDER_MISSING`. 8. `recipes` and `FOLDER_IS_FILE`. 9. `recipes/Rice Bowl.toml` and `NOT_A_RECIPE_ID` of a listing. 10. `recipes/rice.TOML` and `TOML_ENDING_NOT_SMALL`. 11. `menus` and `FOLDER_MISSING`. 12. `menus` and `FOLDER_IS_FILE`. 13. `menus/2026-w48.toml` and `NOT_A_WEEK_NAME`. 14. `menus/plan.toml` and `NOT_A_WEEK_NAME`. 15. `menus/2026-W48.TOML` and `TOML_ENDING_NOT_SMALL`. 16. `menus/2026-W47.toml, Monday dinner` and `UNKNOWN_RECIPE(recipe="tomato-eggs")`, the lines of the F11 prototype "A menu with a mistake". 17. `menus/2026-W47.toml, week` and `WEEK_NOT_FILE_NAME(name="2026-W47", week="2026-W48")`. 18. `recipes/mapo-tofu.toml, ingredient 3` and `UNKNOWN_INGREDIENT(name="豆瓣酱")` of a recipe. 19. `recipes/rice.toml, servings` and `SERVINGS_TOO_FEW(servings=0)`. 20. W and M of 19, because Monday's dinner names `rice` before Tuesday's dinner names `mapo-tofu`. 21. W and M of 2. 22. W and M of 4, because the pantry comes before the listing of `recipes/`. 23. W and M of 4. 24. W and M of 9. 25. W and M of 13. 26. W and M of 16. 27. `recipes/x.toml` and `FILE_IS_FOLDER`. In each, the error is among the errors of `check` in both languages, and the folder has no `shopping` after the lines. 28 to 30. `(0, out SHOP_47(P))`, because no dish names `x` or `red-braised-pork`, and `2026-W48` is not read. 31. `(1, err STOP(menus/2026-w48.toml, NOT_A_WEEK_NAME))`, on both systems: the listing stops `shop` before it looks for the week. 32. `(1, err STOP(pantry.toml, item 3, PANTRY_INGREDIENT(name="sesame oil")))`, not `NO_MENU`: the pantry stops `shop` whatever the week. |
| F13-T18 | functional | `recipe-menu shop`, `main` | Choice 3, step 6, and v0.1-S15 at `main`. A week that the listing lacks gives `NO_MENU` with `str(week)`, one line on the error stream, exit code 1, nothing on the output stream, and no file written. An entry that is not a menu file does not count. The catalog, the pantry, and both listings come first. Step 5 of v0.1-S15 gives the same three lines as `menu show` (2.2 step 6, choice 3). | 1. v0.1-S15 in `example` with an empty shopping: `menu show 2026-W48`, `menu show 2026-W99`, `shop 2026-W48`, then the menu typo, `menu show 2026-W47`, and `shop 2026-W47`. Then the same `shop` lines with `--lang zh`. 2. In `example`: `shop`, then `shop this --lang zh`, then on 2026-11-17 `shop next`. 3. A new example whose `menus/` also holds `2026-W48.toml.bak`, with the bytes of `2026-W47.toml`, the empty folder `2026-W48`, and `notes.txt`: `shop 2026-W48`. 4. An empty-menus example: `shop 2026-W47`. 5. Each in a new example, with `shop 2026-W48`: the catalog brace, no recipes folder, and Rice Bowl. | 1. `(1, err [NO_MENU(2026-W48)])` for `menu show 2026-W48` and for `shop 2026-W48`, which is the first output of the F13 prototype "No menu, or an empty menu", and `(2, err [NOT_A_WEEK("2026-W99")])`. Then `menu show 2026-W47` and `shop 2026-W47` each give `(1, err STOP(menus/2026-W47.toml, Monday dinner, UNKNOWN_RECIPE(recipe="tomato-eggs")))`. Then `(1, err [NO_MENU_ZH(2026-W48)])` and `(1, err STOP_ZH(menus/2026-W47.toml，周一晚餐, UNKNOWN_RECIPE(recipe="tomato-eggs")))`. `shopping\` stays empty. 2. `(1, err [NO_MENU(2026-W46)])`, `(1, err [NO_MENU_ZH(2026-W46)])`, and `(1, err [NO_MENU(2026-W48)])`. 3. `(1, err [NO_MENU(2026-W48)])`. 4. `(1, err [NO_MENU(2026-W47)])`. 5. `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`, `(1, err STOP(recipes, FOLDER_MISSING))`, and `(1, err STOP(recipes/Rice Bowl.toml, NOT_A_RECIPE_ID of a listing))`. In 2 to 5, the folder has no `shopping` after the lines. |
| F13-T19 | functional | `recipe-menu shop`, `main` | Choice 6. A failed save is three lines on the error stream with exit code 1: the full path of the list file, `str(context.folder.root / problem.file)`, also when the folder failed, then two spaces and the problem's text in the language of the output, then `NO_FILE_SAVED`, or `LEFT_BEHIND` with the full path of `temp` when the call could not remove it. Nothing goes to the output stream. The old file keeps its bytes. A folder that `shop` created stays. The next run, with no fault, saves the list (2.2 step 12, choice 6, point A). | R is the data folder of each input, a new example, with P and T of 2026-W47. The first line of each input runs inside `shop_faults(R, *rules)`. 1. `mkdir R/shopping: DENIED`: `shop 2026-W47`, then `shop 2026-W47 --lang zh`. 2. `mkdir R/shopping: IO`: `shop 2026-W47`. 3. The old list, and `open T: DENIED`: `shop 2026-W47`, then `shop 2026-W47 --lang zh`. 4. The old list, and `open T: IO`: `shop 2026-W47`. 5. The old list, and `write T: NO_SPACE`: `shop 2026-W47`. 6. The old list, `write T: NO_SPACE`, and `unlink T: later DENIED`: `shop next`. Then, with no rule, `shop next`. 7. As 6, with the line `shop 2026-W47 --lang zh`, and nothing after it. 8. The old list, and `close T: IO`: `shop 2026-W47`. 9. The old list, and `move T: DENIED`: `shop 2026-W47`, then `shop 2026-W47 --lang zh`. 10. No shopping, and `write T: NO_SPACE`: `shop 2026-W47`. Then, with no rule, `shop 2026-W47`. | 1. `(1, err FAIL(P, FOLDER_CREATE_DENIED))` and `(1, err FAIL_ZH(P, FOLDER_CREATE_DENIED))`: the first line names the list file, not its folder. R has no `shopping`. 2. `(1, err FAIL(P, FOLDER_CREATE_ERROR(reason="Input/output error")))`. 3. `(1, err FAIL(P, FILE_WRITE_DENIED))` and `(1, err FAIL_ZH(P, FILE_WRITE_DENIED))`. 4. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="Input/output error")))`. 5. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="No space left on device")))`, and the record ends with `unlink shopping/2026-W47.md.tmp`, `open shopping/2026-W47.md.tmp`, and `unlink shopping/2026-W47.md.tmp`. 6. `(1, err LEFT(P, FILE_WRITE_ERROR(reason="No space left on device"), T))`, and T holds `first_half(FILE_47)` of `tests/f11_support.py`, as the harness wrote it, because `FILE_47` is ASCII. Then `(0, out SHOP_47(P))`: step 3 removed T, the file holds `FILE_47`, and `R/shopping` holds only `2026-W47.md`. 7. `(1, err LEFT_ZH(P, FILE_WRITE_ERROR(reason="No space left on device"), T))`: the line names T, `2026-W47.md.tmp`, for `next` too. 8. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="Input/output error")))`. 9. `(1, err FAIL(P, FILE_WRITE_DENIED))`, which are the lines of the design's example of a failure in 2.2, and `(1, err FAIL_ZH(P, FILE_WRITE_DENIED))`. The record ends with `move shopping/2026-W47.md.tmp shopping/2026-W47.md` and `unlink shopping/2026-W47.md.tmp`. 10. `(1, err FAIL(P, FILE_WRITE_ERROR(reason="No space left on device")))`, and `R/shopping` stays, an empty folder. Then `(0, out SHOP_47(P))`, and the file holds `FILE_47`. In 3 to 9, P keeps `b"old\n"` after each failure, and in 1 to 5 and 8 to 10 no entry ends with `.tmp` afterwards. |
| F13-T20 | functional | `recipe-menu shop`, `main` | Ctrl+C during the save. `cli` exits with 130 and writes nothing, and `replace_file` has removed `temp`, so the old file stays whole. After a Ctrl+C inside `open`, after the system created `temp`, the empty `temp` stays, and the next run removes it and saves the list (2.2 Errors, choice 6, F05 design 2.10). | R, P, and T as in F13-T19, each input in a new example at R with the old list. The first line of each input runs inside `shop_faults(R, *rules)`, through `call_main`. 1. `write T: CTRL_C`: `shop 2026-W47`. 2. `move T: CTRL_C`: `shop 2026-W47`. 3. `open T: after CTRL_C`: `shop 2026-W47`. Then, with no rule, `shop 2026-W47`, inside `shop_faults(R)`. 4. `write T: CTRL_C` and `unlink T: later DENIED`: `shop 2026-W47 --lang zh`. Then, with no rule, `shop 2026-W47 --lang zh`. | The first line of each input gives `(130, "", "")`, and P keeps `b"old\n"`. 1. The record ends with `unlink shopping/2026-W47.md.tmp`, `open shopping/2026-W47.md.tmp`, and `unlink shopping/2026-W47.md.tmp`, and T does not exist. 2. The record ends with `open shopping/2026-W47.md.tmp`, `move shopping/2026-W47.md.tmp shopping/2026-W47.md`, and `unlink shopping/2026-W47.md.tmp`, and T does not exist. 3. The record ends with `unlink shopping/2026-W47.md.tmp` and `open shopping/2026-W47.md.tmp`, and T is an empty file. Then `(0, out SHOP_47(P))`, the record ends with W47 of F13-T16, T is gone, and the file holds `FILE_47`. 4. T holds the UTF-8 bytes of `text[: len(text) // 2]`, where `text` is the text of `PROTOTYPE_FILE`, as the harness wrote them. Then `(0, out SHOP_47_ZH(P))`, T is gone, and the file holds `PROTOTYPE_FILE`. |
| F13-T21 | functional | `recipe-menu shop`, `main` | Choice 6 and point C with real failures of the file system, with no harness. Something other than a folder at `shopping` gives `PARENT_NOT_A_FOLDER`. A folder at the list file's path makes the move fail on both systems. On Windows, another program that holds the old file open makes the move fail with `FILE_WRITE_DENIED`, and the old file keeps its bytes, and on Linux the move replaces the file. No `.tmp` file is left, and the next run after the fix saves the list (choice 6, point C). | R, P, and T as in F13-T19, each input in a new example at R. 1. Shopping as a file: `shop 2026-W47`, then `shop 2026-W47 --lang zh`. Then `R/shopping` deleted, and `shop 2026-W47`. 2. A dangling link at `R/shopping`: `shop 2026-W47`. 3. An empty shopping that holds the empty folder `2026-W47.md`: `shop 2026-W47`. Then that folder deleted, and `shop 2026-W47`. 4. The old list, held open with `held_open(P)` during `shop 2026-W47`. Then, after the file is closed, `shop 2026-W47`. | 1. `(1, err FAIL(P, PARENT(shopping)))`, which is the last run of the design's example of 2.2, and `(1, err FAIL_ZH(P, PARENT(shopping)))`. The file `shopping` keeps `b"x\n"`. After the deletion, `(0, out SHOP_47(P))`, and `R/shopping` is a new folder that holds only `2026-W47.md`, with `FILE_47`. 2. `(1, err FAIL(P, PARENT(shopping)))`, and the link is still there. 3. `(1, err FAIL(P, M))`, where M is `move_message` of a folder of the case, taken before the line: `FILE_WRITE_DENIED` on Windows and `FILE_WRITE_ERROR(reason="Is a directory")` on Linux. The folder `2026-W47.md` is still there, and T does not exist. After the deletion, `(0, out SHOP_47(P))`, and the file holds `FILE_47`. 4. On Windows: `(1, err FAIL(P, FILE_WRITE_DENIED))`, P keeps `b"old\n"`, and T does not exist. On Linux: `(0, out SHOP_47(P))`, and P holds `FILE_47`. Then, on both systems, `(0, out SHOP_47(P))`, P holds `FILE_47`, and `R/shopping` holds only `2026-W47.md`. |
| F13-T22 | functional | `recipe-menu shop`, `main` | `cli` reports the mistakes on the command line, a missing data folder, and broken settings before it runs `shop`, with the messages and exit codes of F05: two weeks and an option. `--help` shows the help and runs nothing. The same folders then give the output of `shop` (2.2 Errors, choice 1, F05 design 2.10). | 1. In `example`: `shop 2026-W47 2026-W48`, `shop 2026-W47 2026-W48 --lang zh`, `shop --tag x`, and `shop --tag x --lang zh`. 2. In `example`: `shop next --help` and `shop 2026-W99 --help --lang zh`. 3. M is `tmp_path / "missing"`: `shop` in M, and `shop next --lang zh` in M. 4. Broken settings in a new example: `shop 2026-W47`. 5. In `example`: `shop 2026-W47`. | 1. `(2, err ['Unexpected argument "2026-W48". Write "recipe-menu shop [WEEK]".', 'Run "recipe-menu --help" to see the commands.'])`, `(2, err ["多余的参数“2026-W48”。请写成“recipe-menu shop [周]”。", "运行“recipe-menu --help”查看命令。"])`, `(2, err ['"shop" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`, and `(2, err ["“shop”没有选项“--tag”。它没有自己的选项。", "运行“recipe-menu --help”查看选项。"])`. 2. Each gives exit code 0, an empty err, and on out the same text as `--help`, or as `--help --lang zh` for the second line, with no folder. 3. `no_data_folder(M)` and `no_data_folder(M, ZH)` of `tests/f05_texts.py`, and M still does not exist. 4. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`, and the folder has no `shopping`. 5. `(0, out SHOP_47(P))`. Before 5, `example` has no `shopping`. |
| F13-T23 | integration | `recipe-menu shop`, `main` | `shop` uses the data folder that `cli` picks and the language that `cli` picks: `--data`, else `RECIPE_MENU_DATA`, else `~/recipe-menu`, and `--lang`, else the language of the settings, else English. The last line names the full path of the saved file. Data files with a byte order mark and CRLF line ends read the same, as v0.1-S08 expects, and the saved file still has no byte order mark and LF line ends (2.2 parameters, choice 5, F05 design 2.10). | B is a new example at `tmp_path / "One Drive" / "菜谱"`, and E is `{"RECIPE_MENU_DATA": str(B)}`. 1. `shop 2026-W47` with no folder and `environ` E. 2. `shop 2026-W47` with no folder. Then a new example at `home / "recipe-menu"`, and `shop 2026-W47` with no folder. 3. `main` with the arguments `shop 2026-W47 --data rel`, after `monkeypatch.chdir` to `tmp_path / "cwd"`, which holds a new example at `rel`. 4. `main` with the arguments `shop 2026-W47 --data ~/other`, with a new example at `home / "other"`. 5. Chinese settings in a new example C: `shop 2026-W47`, then `shop 2026-W47 --lang en`. 6. BOM and CRLF in a new example D: `shop 2026-W47`. | 1. `(0, out SHOP_47(B/shopping/2026-W47.md))`. 2. `no_data_folder(home / "recipe-menu")`, then `(0, out SHOP_47(home/recipe-menu/shopping/2026-W47.md))`. 3. `(0, out SHOP_47(Path.cwd() / "rel" / "shopping" / "2026-W47.md"))`, a full path. 4. `(0, out SHOP_47(home/other/shopping/2026-W47.md))`. 5. `(0, out SHOP_47_ZH(P))`, and the file holds `PROTOTYPE_FILE`. Then `(0, out SHOP_47(P))`, and the file holds `FILE_47`. 6. `(0, out SHOP_47(P))`, which is step 4 of v0.1-S08. In 1 to 4 and 6, the saved file holds `FILE_47`, with no `b"\xef\xbb\xbf"` and no `b"\r"`. |
| F13-T24 | integration | `recipe-menu menu new`, `recipe-menu shop`, `main` | v0.1-S14 at `main`. `shop` and `shop next` read the two empty menus that `menu new` created, print `NO_DISHES` with the week of today and the week 7 days later, and exit with 0. `shopping\` stays empty (choices 2 and 7). | For each date D of 2026-11-10, 2026-12-30, and 2027-01-03, with the weeks T and N of F13-T15, an empty-menus example F with an empty shopping, and each line on D in F: 1. `menu new`. 2. `menu new next`. 3. `shop`. 4. `shop next`. 5. `shop this --lang zh`. | 1 and 2 each give exit code 0, and `menus/` holds `T.toml` and `N.toml`. 3. `(0, out [NO_DISHES(T)])`. 4. `(0, out [NO_DISHES(N)])`. 5. `(0, out [NO_DISHES_ZH(T)])`. `F/shopping` is still an empty folder after the lines. |
| F13-T25 | integration | `recipe-menu menu new`, `recipe-menu menu show`, `recipe-menu shop`, `main` | v0.1-S16 at `main`. The settings name the meals of the new menu and the servings of a dish that gives none, and `shop` scales `tomato-egg` from 2 to 3 servings. The list starts with the line of v0.1-S16, lists Tomato 450 g and Scallion 2 stalks under Vegetables and fruit and then Egg 5 pieces under Eggs, dairy, and tofu, and has the pantry line of v0.1-S16 (choices 4, 7, and 8). | The init folder at R, with `meals = ["lunch", "dinner"]` replaced by `meals = ["breakfast", "lunch", "dinner"]` and `servings = 2 ` replaced by `servings = 3 ` in `settings.toml`. 1. `menu new 2026-W48`. 2. `[monday]\nbreakfast = []` replaced by `[monday]\nbreakfast = ["tomato-egg"]` in `menus/2026-W48.toml`. 3. `menu show 2026-W48`. 4. `shop 2026-W48`, then `shop 2026-W48 --lang zh`. | 1 and 3 each give exit code 0. 4. The two outputs of block C, each with exit code 0 and an empty err. The first line is `Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish`, and the pantry line is `Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar`. |
| F13-T26 | integration | `recipe-menu shop`, `main` | v0.1-S18 at `main`. Quantities that cannot be added share one line: `5 stalks + 1 bunch` and `30 ml + 10 g`, and `5 根 + 1 把` and `30 ml + 10 g` in Chinese, as `amount_text` writes them. The saved file holds the same amounts (choices 4 and 5). | A new example with the changes of `s18_changes` of `tests/f12_support.py`: the two lines of block G. | The two outputs of block G, each with exit code 0 and an empty err. The English output has the line `  Scallion       5 stalks + 1 bunch` and the line `  Soy sauce      30 ml + 10 g`, and the Chinese output the lines `  葱         5 根 + 1 把` and `  生抽       30 ml + 10 g`. After each line, the file holds `shop_file` of the list in its language, with `- [ ] Scallion 5 stalks + 1 bunch` or `- [ ] 葱 5 根 + 1 把`. |
| F13-T27 | integration | `recipe-menu shop`, `main` | v0.1-S23 at `main` for `shop`. Two runs for one week change only `shopping\2026-W47.md`, and `shopping\` holds no other file. Every other file and folder under `home` and under the current folder keeps its bytes and its modification time. The lines of `shop` that save nothing change nothing (2.2 side effects, choice 6). | A new example at `home / "recipe-menu"` with an empty shopping, and the empty current folder `tmp_path / "cwd"`, entered with `monkeypatch.chdir`. `snapshot` of `tests/f07_support.py` of `home` and of the current folder before the lines, after the first group, and after each run of the second group. 1. With no folder: `shop 2026-W48`, `shop 2026-W99`, `shop --help`, and `shop --tag x`. 2. With no folder: `shop 2026-W47`, twice. | 1. `(1, err [NO_MENU(2026-W48)])`, `(2, err [NOT_A_WEEK("2026-W99")])`, exit code 0 with the help, and exit code 2 with the two lines of `shop --tag x` of F13-T22. The snapshots after 1 equal the snapshots before it. 2. Each run gives `(0, out SHOP_47(home/recipe-menu/shopping/2026-W47.md))`. After each run, the snapshot of `home` equals the snapshot before the run, except for `recipe-menu/shopping`, whose modification time may change, and `recipe-menu/shopping/2026-W47.md`, which holds `FILE_47`. `recipe-menu/shopping` holds only `2026-W47.md`, and the snapshot of the current folder is unchanged. |
| F13-T28 | integration | `python -m recipe_menu` | The real entry point runs `shop` with the real commands. It writes the output as UTF-8 to stdout, whatever encoding Python gave the streams, the saved file as UTF-8, and the message of exit code 1 or 2 to stderr (2.2, F05 design 2.9). | `run_module` of `tests/f05_support.py`, which sets `HOME` and `USERPROFILE` to `tmp_path / "home"` and `PYTHONIOENCODING` to `ascii`. With `example`: 1. `shop 2026-W47 --lang zh --data <example>`. 2. `shop 2026-W47 --data <example>`. 3. `shop 2026-W99 --lang zh --data <example>`. 4. `shop 2026-W48` with `data=example.root`, which sets `RECIPE_MENU_DATA`. 5. In a new example X with shopping as a file: `shop 2026-W47 --data <X>`. No line uses `this`, `next`, or no week, because the new process reads the clock. | 1. Exit code 0, the lines of `SHOP_47_ZH(P)` on stdout, and an empty stderr, and the file holds `PROTOTYPE_FILE`. 2. Exit code 0, the lines of `SHOP_47(P)` on stdout, and an empty stderr, and the file holds `FILE_47`. 3. Exit code 2, an empty stdout, and the line `NOT_A_WEEK_ZH("2026-W99")` on stderr. 4. Exit code 1, an empty stdout, and the line `NO_MENU(2026-W48)` on stderr. 5. Exit code 1, an empty stdout, and the lines of `FAIL(P, PARENT(shopping))` on stderr. |
| F13-T29 | integration | `recipe-menu shop`, `main` | Random weeks. For any catalog names of any width, with a line break or not, any pantry, any set of meals and default servings, any week of the list below, and any mix of days, meals, dishes, and servings, `shop` gives the output and the file that the rules of 2.2 give in both languages, or `NO_DISHES` for a menu with no dish, and a second run replaces the file. Random mixes reach widths, groups, and pantry lines that the other cases do not list (2.2, choices 2, 4, 5, 7, and 8). | `random.Random(20261116)` builds 100 folders, each a new example with the extra recipe `water`. Each choice below has equal chances unless it says otherwise. The catalog: the test writes `catalog.toml` again, with the six categories and the 22 ingredients of the example in its order, with their keys, categories, and units, the five tags of the example, and new names. A new English name is `C` or `I` and the item's number, in two digits for an ingredient, then 0 to 3 words, each after one space. A new Chinese name is `类` or `食` and the number, then 0 to 3 words with no space. A word has 1 to 6 characters in English and 1 to 4 in Chinese, from the letters `a` to `z` and `A` to `Z`, `\u00e9`, and the characters `番茄鸡蛋豆腐葱姜蒜米面油`. 1 time in 10, an English name of an ingredient with a word has the TOML escape `\n` in place of the space before its last word. The test replaces each `item = "<old Chinese name>"` of the recipes by the new Chinese name, and writes `pantry.toml` with the new Chinese names of the ingredients, each 1 time in 3. The settings: `meals` with a non-empty set of the three meals in a random order, and `servings` from 1 to 5. The week W: one of `2026-W01`, `2026-W23`, `2026-W47`, `2026-W49`, `2026-W53`, and `2027-W01`. The test writes `menus/W.toml`: each day is left out with a chance of 1 in 4, and a day lists the meals of the settings in a random order, each with 0 to 3 dishes, and 1 time in 10 no meal holds a dish. Each dish is one of the seven recipes of the example or `water`, written as `"ID"`, as `{ recipe = "ID" }`, or as `{ recipe = "ID", servings = k }`, with k from 1 to 12. Then `shop V --lang L` on a date D, with L `en` or `zh`: V is W, `this`, or no value, with D one of the seven dates of W, or V is `next`, with D one of the seven dates of the week before W. Then `shop W --lang L2`, with L2 `en` or `zh`. | With S as `shop_list(folder, W)`: when the menu has no dish, each line gives `(0, out [NO_DISHES(W)])` or `(0, out [NO_DISHES_ZH(W)])`, and the folder has no `shopping`. Otherwise each line gives `(0, out shop_lines(S, L, P))` with the language of its line, the file holds `shop_file(S, L)` after it, and `shopping/` holds only `W.md`. |
| F13-T30 | performance | `recipe-menu shop`, `python -m recipe_menu` | PT01 and v0.1-S32: `shop` builds and saves the list of one PT01 week of 63 dishes from 63 different recipes within 1 second, as the median of 5 runs from start to exit (requirements 7.1, 2.2, choice 10). | The PT01 data folder of section 3, in `tmp_path / "pt01"`, with no `shopping/`. One untimed run, then 5 timed runs of `python -m recipe_menu shop 2026-W26 --data <pt01>`, as section 3 says. | Each run exits with 0, writes the result of `pt01_shop` on stdout, 302 lines, and writes nothing on stderr. Afterwards, `shopping/` holds only `2026-W26.md`, with `shop_file` of the list in English, 10,345 bytes. The median of the 5 timed runs is under 1 second on Windows and under 3 seconds on Linux. |

## 3. Performance cases

PT01 names `shop` among its commands (requirements 7.1), so `recipe-menu shop` gets one case. No other interface of F13 gets one: `SHOP_COMMAND` and `replace_file` have no target of their own, and PT01 times them through the command (R14).

| ID | Target | Machine | Margin | Baseline |
| --- | --- | --- | --- | --- |
| F13-T30 | PT01: `recipe-menu shop` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus. The median of 5 runs from start to exit counts. | Troy's PC: Windows 11, with Python 3.13 of the `recipe-menu` environment. The case also runs in CI, on the `ubuntu-24.04` runner of `.github/workflows/troy-mode.yml`, which is not a fixed machine (architecture 10). | On Windows, none: the median must be under 1 second, because a margin above PT01 would pass a command that misses it (v0.1 test plan, section 3). On Linux, 3 seconds, as F07-T25, F09-T28, F10-T21, and F11-T38 have, so that the case holds on a runner of unknown speed and still fails a slowdown of several times. | First run. The Architect's model took medians of 0.226 s and 0.228 s for `shop 2026-W26` on Troy's PC in two sets of 5 runs, beside 0.216 s for `menu show 2026-W26` in the same sets (design section 4). F11's `menu show 2026-W26` takes 0.187 s on Troy's PC, and F12's `build_shopping_list` takes a median of 5.19 ms on that week. A model is not the implementation, so the F13 implementation PR records the first baseline. |

**Which system is Troy's PC.** CI runs only on Linux, and only Troy's PC runs the tests on Windows. So the case applies the limit of `time_limit` of `tests/pt01_support.py`: 1 second when `sys.platform == "win32"`, and 3 seconds otherwise, as F11-T38 does. A CI job on Windows would change this plan first.

**The PT01 data folder.** `make_pt01` of `tests/pt01_support.py` writes it, as for F11-T38. F13 does not change the generator. Its settings name breakfast, lunch, and dinner, with 2 servings, and its pantry holds the last 10 of the 300 ingredients. `2026-W26`, from 22 to 28 June 2026, names the 63 different recipes `recipe-0576` to `recipe-0638`, three in each of its 21 meals, and the first dish of each dinner has 4 servings. The folder has no `shopping/`, so the untimed run creates it, and the timed runs replace the file. The Architect's model and this plan use the same week.

**The timed run.** The case uses the general timed run of F09 in `tests/pt01_support.py`: `command_run`, `command_runs`, `record_times`, and `time_limit`, which keep their names and their behavior.

**The expected output.** `pt01_shop(root)` of `tests/f13_support.py` gives `(0, out, "")`, where out is the lines of `shop_lines(shop_list(DataFolder(root), IsoWeek(2026, 26)), Lang.EN, P)`, each followed by `"\n"`, with P as `root / "shopping" / "2026-W26.md"`. The case computes it once, before the first run. It checks these facts of the result too, which the Test Manager took from the model on a PT01 folder: the first line is `Shopping list for 2026-W26, 22 to 28 June 2026: 21 meals, 63 dishes`, the output has 302 lines, the six group headings are the six categories of the example in their order, 290 lines start with two spaces, and the pantry line names the 10 pantry ingredients. The saved file has 10,345 bytes on both systems, as the design's section 4 found.

**The steps of the case.**

1. Generate the folder, and compute the expected result.
2. Start the command once, untimed, and check its result as in step 3. Windows reads the 1,053 new files slowly the first time (F07 test plan, section 3), and Troy's own data folder does not pay that cost on each run. This run creates `shopping/`.
3. Start the same command 5 times, each as a new process, with `command_runs`: `sys.executable -m recipe_menu`, in `tmp_path`, with `HOME` and `USERPROFILE` set to an empty home folder and without `RECIPE_MENU_DATA`. Each run must exit with 0, give exactly the expected stdout, and give an empty stderr. A run that does not fails the case, whatever its time.
4. Check that `shopping/` holds only `2026-W26.md`, with the expected bytes.
5. Take the median of the 5 times, and compare it with the limit of the system.
6. Record the 5 times, the median, and the range with `record_property`, so that the JUnit report holds them for the next comparison.

**How it runs on Troy's PC.** The case lives in `tests/`, so it runs in every full test run on Troy's PC, which the main session starts with the Python of the `recipe-menu` environment for each PR. In the F13 implementation PR, the main session also runs it alone, with `python -m pytest tests/test_f13_performance.py --junitxml=reports/pt01-f13.xml`, while no other test run, build, or install is going on. The PR description reports the median and the range, and that run is the baseline. The release test runs v0.1-S32 on the same machine.

**The benchmark checklist.** The case answers the questions of `benchmark-checklist` in these ways:

- The limiter: design choice 10 and section 4 name it. `shop` reads what `menu show` reads, plus the pantry of 10 items, so the start of Python, the imports, the catalog of 300 ingredients, the listing of 1,000 recipe files, and the 63 recipe files limit it, as they limit `menu show`. `build_shopping_list` adds about 5 ms, `amount_text` about 1 ms, and the save one probe, one removal, one open, one write of 10 KB, one close, and one move. The Architect's model took about 0.01 s more than `menu show` in the same sets. The case does not profile, because a profiler slows the run. A `[refactor]` PR profiles.
- Tuning: each run is a new Python process with the installed package and its compiled files, with no coverage and no debugger, as Troy runs it. The untimed run of step 2 has read the files once. coverage.py measures only the test process, so `coverage run -m pytest` in CI does not slow the timed processes.
- Limits: `shop` writes about 10 KB through a pipe and 10 KB to the disk, and reads 63 recipe files, one menu file, the catalog, the pantry, and the settings, about 170 KB, which a disk reads and writes in milliseconds. So the time measures the work of Python.
- Errors: steps 2 and 3 check the exit code, the whole stdout, and the empty stderr of each run, and step 4 checks the saved file.
- Repeatability: 5 timed runs, with the median and the range recorded. A difference from the baseline that is smaller than the range of the baseline's runs is no measurable change.
- Relevance: the case times the whole command from start to exit, which is what Troy waits for. A week with three dishes in each meal of three meals, from 63 different recipes, is the most that a PT01 week holds, so `shop` reads the most recipe files and merges the most lines that it can for one PT01 week.
- The work happened: the count `21 meals, 63 dishes`, the 290 lines in 6 groups from 63 recipes, and the saved file of 10,345 bytes, which each run replaces, show that `shop` read the menu and every recipe that it names, built the list, and saved it.

## 4. Not tested

| What | Why |
| --- | --- |
| The fields of `SHOP_COMMAND` on their own, the names that `__all__` lists in `recipe_menu.commands.shop` and `recipe_menu.datafile`, and the messages as constants in `shop/messages.py` and `datafile/messages.py`. | The mock declares them in full, so a test of them alone would pass against the mock (R09). F13-T01 checks the fields beside a run, and the cases check every text through the output, the file, or a problem. Code review checks where the texts live and that `shop` exports only its command (choice 11). |
| `shop` imports only `app`, `lang`, `text`, `datafile`, `catalog`, `recipes`, `menus`, and `shopping`. | R07. The dependency checker in CI compares each import with the table in architecture 3. |
| `shop` reaches the disk only through the readers and `replace_file`, writes its output once, after the file, and keeps no state or cache. | No interface shows which module makes a call or when the text reaches the stream. F13-T14 to F13-T16 record every call that `shop` makes on the disk, every case that expects exit code 1 or 2 checks that the output stream is empty, and F13-T01 runs `run` several times on one folder. Code review checks the rest. |
| `run` with `Arguments` outside the constraints of 2.1: two values, or an option. | `cli` never passes them (F05 design 2.10). F13-T22 checks that `cli` rejects each such command line. |
| A name of the catalog that lacks the chosen language, which `shop` would show in the other language through `BiText.get` (choice 4). | `read_catalog` gives an error for an ingredient or a category without one of its names (F03 design 2.10), so `shop` stops at that error and never shows such a name. F13-T17 input 3 checks that stop. |
| `replace_file` with a path that holds `..`, such as `folder.root / ".." / "x.md"`, and with a text that is not a `str`. | `DataFolder.relative` compares the parts of two paths and does not resolve `..` (F03 design 2.1), and `shop` passes the path that `shopping_file` gives. A text that is not a `str` breaks the type in the signature, which mypy checks. |
| A process that is killed, and a PC that loses power, during the save. | The removal cannot run then, and no test can stop a process at a chosen step. F13-T05 input 4 and F13-T12 input 3 check that a `temp` that a stopped run left is removed by the next run, and F13-T10 and F13-T20 check Ctrl+C. The design calls no `fsync`, and architecture 6 asks for none. |
| A real Ctrl+C from a console, access that the file system denies, and a real second program that creates `temp` or holds it open. | No CI machine has a console, the root user on Linux ignores mode bits, and no test can time a second program to a step. The fault harness raises `KeyboardInterrupt`, which is what Python raises for Ctrl+C, as F05-T41 does, and raises `PermissionError` or makes the race at the step that each case picks. F13-T21 holds the old file open with the test's own handle, which Windows treats as another program. |
| `shop` on a date near the last date of `datetime.date`. | F06-T22 tests `week_from_argument` there, and the PC's clock gives no such date (F06 design 2.7). |
| Chinese output in Windows Terminal, v0.1-S25. | No CI machine has a Windows console (architecture 10), so Troy checks it. F13-T12 checks that the amounts of the Chinese list start at one display column, and F13-T28 checks that `python -m recipe_menu` writes the Chinese output as UTF-8. |
| The saved list on Troy's phone, v0.1-S26. | It needs Troy's phone and Troy's sync. F13-T12 checks that the Chinese file is the prototype's file, byte for byte, in UTF-8 with no byte order mark. |
| Doc comments are in English only. | R05. troy-check rejects Chinese characters in doc comments. |
| The plans for later features in design section 2: F14's `menu suggest` with `replace_file`, and F15's `add` with `create_file`. | The design and the test plan of each later feature cover them. F13-T05 input 7 checks that `replace_file` replaces a menu file. |
| v0.1-S08, v0.1-S14 to v0.1-S18, v0.1-S23, and v0.1-S32 in the release test. | They are version tests in `version-tests/`, which the version tests PR adds (TE5). F13-T12, F13-T18, and F13-T23 to F13-T27 run the same steps at `main`, and F13-T30 times the same command on the same kind of folder, in every test run. |

## 5. Alignment with the Interface Designer

None.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-15 | First draft. |
| 1.0 | 2026-11-15 | Approved by Troy. |
