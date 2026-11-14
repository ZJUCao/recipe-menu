---
troy-doc: "F10-test-plan"
lang: "en"
version: "1.0"
updated: "2026-11-14"
status: "Approved by Troy on 2026-11-14"
mirror: "test-plan.zh-CN.md"
---

# F10 Search recipes: test plan

## 1. Feature

- ID and name: F10 Search recipes
- Design: [design.md](design.md), version 1.0

## 2. Cases

The tests call `SEARCH_COMMAND` of `recipe_menu.commands.search`, `matching_form` of `recipe_menu.catalog`, `main` of `recipe_menu.cli`, and `python -m recipe_menu`. A unit case calls `SEARCH_COMMAND.run` with a `Context` that it builds. A functional case runs `main` with a command line, as you type `recipe-menu search`. It passes no `commands`, so `main` uses the real `COMMANDS`, which holds `INIT_COMMAND`, `CHECK_COMMAND`, `LIST_COMMAND`, `SHOW_COMMAND`, and `SEARCH_COMMAND` from the mock PR on (design choice 1). An integration case runs a v0.1 scenario at `main`, runs `show` and then `search`, starts `python -m recipe_menu`, or builds random folders. The performance case times `python -m recipe_menu search` (section 3). Each case names the section of the design that it comes from, such as (2.2). The design's three examples and the `# raises` line of 2.1 are in F10-T01 (2.1), F10-T03 (2.2), and F10-T07 (3.1).

**Points A and B.** Troy approved design 1.0 on 2026-11-13 with the recommendation of each point: the new texts of 2.2 as written (A), and `UsageError(EMPTY_WORD, None)` with exit code 2 for a word whose matching form is empty (B, option 1). The cases check each new text of point A in both languages. The English line for two or more words is in F10-T04, F10-T08, and F10-T10, and the Chinese line for one word is in F10-T04. The line for one recipe is in F10-T10 and F10-T12, and the Chinese line for three words is in F10-T03 and F10-T10. The place `tag` is in F10-T05, the place `名称` is in F10-T04, and `EMPTY_WORD` is in F10-T02 and F10-T11.

**Tests of earlier features.** Design section 3 says that the tests of the real help stay true when `search` joins `COMMANDS` and the second column of the help moves from 18 to 19 columns: F05-T48, F05-T49, F07-T17, F08-T14, F09-T01, F09-T19, and F09-T25. The Architect ran the whole test suite of main on a model with `SEARCH_COMMAND` in `COMMANDS` and `matching_form` exported. 462 tests passed, and the 3 cases that run only on Linux were skipped (design section 4). F10 changes no test of an earlier feature and no file of `tests/data/example/`. F10-T01 checks the line of `search` in the help of the real `COMMANDS` in a form that holds as F11 to F13 add their commands.

**R09.** The mock defines every message and `SEARCH_COMMAND` with all its fields, adds the command to `COMMANDS`, and exports `matching_form` from `catalog`. Its `run` reads no file, writes nothing, raises nothing, and gives 0 (design section 2). So a test passes against the mock when it checks only the fields of the command, a message, the help, exit code 0, or that no file changed. The same holds for what `cli` does before it runs the command, such as a missing data folder, broken settings, `search` with no word, `search 番茄 --tag quick`, and `search 番茄 --help`, and for `matching_form` on its own, which is F03's working function. Each case that checks such a thing also checks something that the mock gets wrong: the output of `search`, exit code 1 or 2 from `run`, a `UsageError` from `run`, or the reads that the harness records. F10-T01, F10-T07, F10-T11, F10-T15, and F10-T16 check such things only beside a result that the mock gets wrong. Every case that expects exit code 0 from `search` also checks the whole output, which is never empty. `tests/f10_support.py` and `tests/f10_texts.py` call no interface of F10 when they are imported.

**Both systems.** Every case runs on Linux and on Windows, and no case is skipped on either. CI runs only on Linux, and R09 counts a skipped test as a test that does not fail. A problem names its file with the system's separator. So in an expected line, `recipes/mapo-tofu.toml` stands for `str(Path("recipes", "mapo-tofu.toml"))`: `recipes\mapo-tofu.toml` on Windows and `recipes/mapo-tofu.toml` on Linux. A file at the root, such as `catalog.toml`, and the folder `recipes` read the same on both systems. The tables of `search` hold no path, so their columns have the same widths on both systems. In the Chinese tables, each Chinese character takes two columns, as in the F10 prototype. The inputs that touch what the systems do differently are those of F09, and each gives the same result on both:

- `recipes/rice.TOML` (F10-T13) is made with `Path.rename`, which works on both systems, as in F09-T11.
- The data folder `One Drive/菜谱` of F10-T18 holds a space and Chinese characters, and it is a valid path on both systems.
- F10-T19 passes words with Chinese characters and an empty word to a new `python -m recipe_menu` process, as F09-T26 passes `list --tag 快手`. Both systems hand such words to Python unchanged. No case passes a word with a line break or an invisible character to a new process. F10-T07, F10-T10, and F10-T11 pass such words to `main`.

The Test Manager computed the expected texts below on Troy's PC, with Python 3.13.18, the readers of main, and two models of `search` that follow the design: the Test Manager's own model and the Architect's model of design section 4. The two models gave the same result for every line of the cases, and for 300 random lines from a generator that follows F10-T20.

**The record of the reads.** F10-T14 records which files `search` opens and which folders it lists. It uses the fault harness `faults(base)` of `tests/f08_support.py` with no rules, as F09-T20 does. The harness records each open of a path under `base` as `read` and the path relative to `base`, with `/`, and each listing by `os.scandir` or `os.listdir` in "the listings" (F08 test plan, section 2). `search` reaches the disk only through the readers of F03 and F04 (design section 2). So the record depends on which readers `search` calls, and on no other code of F10. `cli` reads `settings.toml` before it runs a command, so every record starts with `read settings.toml`.

These rules hold for the test data, as in the F09 test plan:

- `EXAMPLE` is the folder `tests/data/example/` of the repository (architecture 10). The fixture `example_folder` of `tests/conftest.py` copies it to `tmp_path / "recipe-menu"` with LF line ends and gives a `DataFolder` on the copy. In a case, `example` is that `DataFolder`. "A new example at P" is a further copy, made with `copy_example` of `tests/f05_support.py`. "A new example" with no P is at a path of its own under `tmp_path`.
- "The init folder at P" is made with `make_init` of `tests/f07_changes.py`: a new example with no recipe other than `tomato-egg`, no menu, and the empty folders `menus/` and `shopping/`.
- `home` is `tmp_path / "home"`, an empty folder that `make_home` of `tests/f05_support.py` makes. It is outside `example`, so a line with no `--data` finds no data folder unless the case puts one at `home / "recipe-menu"`.
- The tests write every file with `write` of `tests/f03_support.py`, which writes UTF-8 with LF line ends and makes its folders first, or as bytes. "X replaced by Y in F" replaces the first X in the file F with `edit` of `tests/f07_changes.py`, which checks that F holds X.
- No test changes the repository, touches `~/recipe-menu`, or reads the clock. Every call of `main` passes `home`, `environ`, and `today`. F10-T19 and F10-T21 start `python -m recipe_menu` with `HOME` and `USERPROFILE` set to a folder in `tmp_path`. A case changes the current folder only with pytest's `monkeypatch.chdir`.

These named changes make the folders of the cases. Each applies to the data folder of its case. Section 2 of the F09 test plan defines the first group, and the helpers of `tests/f07_changes.py` and `tests/f09_support.py` make them:

- From F09: the mapo mistake, rice at 0, the comma, the typo, broken settings, the catalog brace, no catalog, no recipes folder, recipes as a file, empty recipes, not recipes, Rice Bowl, capital rice, folder x, soup, the extra recipes, and the long name with S. The mapo mistake makes ingredient 3 of `recipes/mapo-tofu.toml` name 豆瓣酱, which the catalog lacks. The extra recipes are `boiled-egg`, which has no Chinese name, `steamed-egg`, which has no English name, and `water`. The long name with S keeps only `rice` and adds `a-long`, whose names hold the TOML escape S, which is `\n`, `\r\n`, or `\u2028`, so that each name takes two lines. Soup adds the tag `汤` and `soup`, which no recipe has.
- Chinese settings: `language = "en"` replaced by `language = "zh"` in `settings.toml`.
- Egg in English: `{ item = "鸡蛋", amount = "3" }` replaced by `{ item = "EGG", amount = "3" }` in `recipes/tomato-egg.toml`. F04 finds the catalog's 鸡蛋 for it, and `check` reports the same as on the example: no error, and the warning of `red-braised-pork`.
- Eggplant: the line `  { zh = "茄子", en = "Eggplant", category = "produce" },` added after the line of 番茄 in the ingredients of `catalog.toml`, and `recipes/aubergine.toml` written with the first text below. `check` then reports 8 recipes, no error, and the warning of `red-braised-pork`.
- Crème: `recipes/creme.toml` written with the second text below. `check` then reports 8 recipes, no error, and the warning of `red-braised-pork`.
- BOM and CRLF: each file of the folder written again as `b"\xef\xbb\xbf"` followed by its bytes with each `b"\n"` replaced by `b"\r\n"`, as in F09-T22.

```toml
name = { zh = "烧茄子", en = "Braised aubergine" }
servings = 2
tags = ["素"]
ingredients = [
  { item = "茄子", amount = "2 个" },
  { item = "大蒜", amount = "3 瓣" },
]
[steps]
zh = ["茄子切条，和蒜一起烧软。"]
en = ["Cut the eggplant into strips, and braise it with the garlic."]
```

```toml
name = { zh = "焦糖布丁", en = "Crème caramel" }
servings = 4
tags = []
ingredients = [
  { item = "鸡蛋", amount = "3" },
  { item = "糖", amount = "100 g" },
]
[steps]
zh = ["烤 40 分钟。"]
en = ["Bake for 40 minutes."]
```

These conventions hold for the calls of `main`:

- A line such as `search 葱 quick --lang zh` in F stands for `at(home, F, "search", "葱", "quick", "--lang", "zh")` of `tests/f09_support.py`. It adds `--data` and F, and runs `main` through `call` of `tests/f07_support.py` with `home`, `environ`, `today=date(2026, 11, 10)`, two new `io.StringIO` streams, and no `commands`, so `main` uses the real `COMMANDS`. F is a folder or a `DataFolder`. A line "with no folder" has no `--data`. `environ` is `{}` unless the case gives it.
- A word in quotation marks is one word, written as a Python string with its escapes, such as `"and egg"`, `""`, `'say "hi"'`, or `"\u3000番茄"`. Each `\uXXXX` in a word stands for that one character.
- The result is `(code, out, err)`. `(c, out L)` stands for `(c, out, "")`, where out is the lines of L, each followed by `"\n"`, and nothing more. `(c, err L)` stands for `(c, "", err)`, where err is the lines of L, each followed by `"\n"`. The tests compare the whole texts, never `splitlines()` of them, because `splitlines()` also splits at U+000D and U+2028, which F10-T12 must not find in an output.
- `FOUND(T, C)` stands for `(0, out [*T, "", C])`: the lines of the table T, an empty line, and the count line C. `NONE(C)` stands for `(0, out [C])`. When a word holds a line break, the count line holds it too, and the text of out still ends each item of L with `"\n"`.
- `STOP(W, M)` and `STOP_ZH(W, M)` are the three lines of `stop_at_error` in English and in Chinese, as the F09 test plan defines them. `stop` of `tests/f09_texts.py` builds the result. W is a file, such as `catalog.toml`, or a file and a place, such as `recipes/mapo-tofu.toml, ingredient 3`, which is `recipes/mapo-tofu.toml，食材 3` in Chinese.
- "Among the errors of `check`" has the meaning of the F09 test plan, and `assert_among_check` of `tests/f09_support.py` checks it.

The expected texts are these. The tests write each one out as a literal in `tests/f10_texts.py`. They import no message and never read a prototype file, because the messages of `search` and of the readers are internal (design section 2, architecture 8).

- `TOMATO_TABLE` is the three table lines of the F10 prototype "One word": `ID                   Name                      Matched in`, `tomato-egg           Tomato and egg stir-fry   name, ingredient`, and `tomato-egg-noodles   Tomato and egg noodles    name, ingredient`. `TOMATO_TABLE_ZH` is `ID                   名称         匹配于`, `tomato-egg           番茄炒蛋     名称、食材`, and `tomato-egg-noodles   番茄鸡蛋面   名称、食材`.
- `SCALLION_QUICK_TABLE_ZH` is the three table lines of the F10 prototype "Two words, in Chinese". `SCALLION_QUICK_TABLE` is `TOMATO_TABLE` with `ingredient, tag` in place of `name, ingredient` in both rows. "The output of the prototype "Two words, in Chinese"" is `FOUND(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“葱”和“quick”。")`.
- `ALL_THREE_TABLE` is `TOMATO_TABLE` with `name, ingredient, tag` in both rows. `ALL_THREE_TABLE_ZH` is `TOMATO_TABLE_ZH` with `名称、食材、标签` in both rows.
- `EMPTY` is `A word is empty. Look for a name, such as "recipe-menu search tomato".`, and `EMPTY_ZH` is `有一个词是空的。请写要找的名称，比如“recipe-menu search 番茄”。`.
- `HELP` is the 18 lines of the help in English while `COMMANDS` holds only `init`, `check`, `list`, `show`, and `search`: lines 1 to 4 of `HELP` of the F09 test plan, the 12 lines of the English block of design 2.1 from `Commands:` to `  --help           Show this help.`, an empty line, and the last line of F09's `HELP`. `HELP_ZH` is the same in Chinese, with F09's `HELP_ZH` and the Chinese block of design 2.1. Each line of the two tables has its text after 19 columns.

Blocks A to F hold the outputs of `search` in the cases that have a table and are not built from the tables above. Each `PS>` line gives the command line without `--data`, as the prototypes do, and each line runs with `--data` and the folder of its block. The output of a `PS>` line is the lines that follow it, up to and including its count line. An empty line separates it from the next `PS>` line. Each output comes with exit code 0 and an empty err.

Block A, in `example`:

```text
PS> recipe-menu search 炒蛋
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name

1 recipe matches "炒蛋".

PS> recipe-menu search 鸡蛋
ID                   Name                      Matched in
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

2 recipes match "鸡蛋".

PS> recipe-menu search 鸡蛋 --lang zh
ID                   名称         匹配于
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

2 个菜谱匹配“鸡蛋”。

PS> recipe-menu search scallion
ID                   Name                      Matched in
cola-wings           Cola chicken wings        ingredient
mapo-tofu            Mapo tofu                 ingredient
red-braised-pork     Red-braised pork belly    ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    ingredient

5 recipes match "scallion".

PS> recipe-menu search scallion --lang zh
ID                   名称         匹配于
cola-wings           可乐鸡翅     食材
mapo-tofu            麻婆豆腐     食材
red-braised-pork     红烧肉       食材
tomato-egg           番茄炒蛋     食材
tomato-egg-noodles   番茄鸡蛋面   食材

5 个菜谱匹配“scallion”。

PS> recipe-menu search home
ID                 Name                      Matched in
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    tag
tomato-egg         Tomato and egg stir-fry   tag

4 recipes match "home".

PS> recipe-menu search 家常 --lang zh
ID                 名称       匹配于
cola-wings         可乐鸡翅   标签
mapo-tofu          麻婆豆腐   标签
red-braised-pork   红烧肉     标签
tomato-egg         番茄炒蛋   标签

4 个菜谱匹配“家常”。

PS> recipe-menu search 素
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   tag

1 recipe matches "素".

PS> recipe-menu search vegetarian --lang zh
ID         名称       匹配于
choy-sum   清炒菜心   标签

1 个菜谱匹配“vegetarian”。

PS> recipe-menu search staple
ID                   Name                     Matched in
rice                 Steamed rice             tag
tomato-egg-noodles   Tomato and egg noodles   tag

2 recipes match "staple".

PS> recipe-menu search 主食 --lang zh
ID                   名称         匹配于
rice                 米饭         标签
tomato-egg-noodles   番茄鸡蛋面   标签

2 个菜谱匹配“主食”。

PS> recipe-menu search 豆瓣
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient

1 recipe matches "豆瓣".

PS> recipe-menu search red-braised
ID                 Name                     Matched in
red-braised-pork   Red-braised pork belly   name

1 recipe matches "red-braised".

PS> recipe-menu search "choy sum"
ID         Name                  Matched in
choy-sum   Stir-fried choy sum   name, ingredient

1 recipe matches "choy sum".

PS> recipe-menu search 鸡
ID                   Name                      Matched in
cola-wings           Cola chicken wings        name, ingredient
tomato-egg           Tomato and egg stir-fry   ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "鸡".

PS> recipe-menu search -fr
ID           Name                      Matched in
choy-sum     Stir-fried choy sum       name
tomato-egg   Tomato and egg stir-fry   name

2 recipes match "-fr".

PS> recipe-menu search -
ID                 Name                      Matched in
choy-sum           Stir-fried choy sum       name
cola-wings         Cola chicken wings        tag
mapo-tofu          Mapo tofu                 tag
red-braised-pork   Red-braised pork belly    name, tag
tomato-egg         Tomato and egg stir-fry   name, tag

5 recipes match "-".

PS> recipe-menu search MAPO --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“MAPO”。

PS> recipe-menu search egg noodle
ID                   Name                     Matched in
tomato-egg-noodles   Tomato and egg noodles   name, ingredient

1 recipe matches "egg" and "noodle".

PS> recipe-menu search egg noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材

1 个菜谱同时匹配“egg”和“noodle”。

PS> recipe-menu search 番茄 家常
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient, tag

1 recipe matches "番茄" and "家常".

PS> recipe-menu search pork spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   ingredient, tag

1 recipe matches "pork" and "spicy".

PS> recipe-menu search home 葱
ID                 Name                      Matched in
cola-wings         Cola chicken wings        ingredient, tag
mapo-tofu          Mapo tofu                 ingredient, tag
red-braised-pork   Red-braised pork belly    ingredient, tag
tomato-egg         Tomato and egg stir-fry   ingredient, tag

4 recipes match "home" and "葱".

PS> recipe-menu search 米饭 主食
ID     Name           Matched in
rice   Steamed rice   name, tag

1 recipe matches "米饭" and "主食".

PS> recipe-menu search 米饭 主食 --lang zh
ID     名称   匹配于
rice   米饭   名称、标签

1 个菜谱同时匹配“米饭”和“主食”。

PS> recipe-menu search spicy
ID          Name        Matched in
mapo-tofu   Mapo tofu   tag

1 recipe matches "spicy".

PS> recipe-menu search 辣 --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   标签

1 个菜谱匹配“辣”。

PS> recipe-menu search rice
ID     Name           Matched in
rice   Steamed rice   name, ingredient

1 recipe matches "rice".

PS> recipe-menu search 米 --lang zh
ID     名称   匹配于
rice   米饭   名称、食材

1 个菜谱匹配“米”。

PS> recipe-menu search scallion QUICK noodle --lang zh
ID                   名称         匹配于
tomato-egg-noodles   番茄鸡蛋面   名称、食材、标签

1 个菜谱同时匹配“scallion”、“QUICK”和“noodle”。

PS> recipe-menu search mapo --lang zh
ID          名称       匹配于
mapo-tofu   麻婆豆腐   名称

1 个菜谱匹配“mapo”。

PS> recipe-menu search cola
ID           Name                 Matched in
cola-wings   Cola chicken wings   name, ingredient

1 recipe matches "cola".

PS> recipe-menu search cola --lang zh
ID           名称       匹配于
cola-wings   可乐鸡翅   名称、食材

1 个菜谱匹配“cola”。
```

Block B, in a new example with the extra recipes:

```text
PS> recipe-menu search boiled
ID           Name           Matched in
boiled-egg   Boiled egg     name
water        Boiled water   name

2 recipes match "boiled".

PS> recipe-menu search boiled --lang zh
ID           名称         匹配于
boiled-egg   Boiled egg   名称
water        白开水       名称

2 个菜谱匹配“boiled”。

PS> recipe-menu search 蒸
ID            Name   Matched in
steamed-egg   蒸蛋   name

1 recipe matches "蒸".

PS> recipe-menu search 蒸 --lang zh
ID            名称   匹配于
steamed-egg   蒸蛋   名称

1 个菜谱匹配“蒸”。

PS> recipe-menu search egg
ID                   Name                      Matched in
boiled-egg           Boiled egg                name, ingredient
steamed-egg          蒸蛋                      ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

4 recipes match "egg".

PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
boiled-egg           Boiled egg   名称、食材
steamed-egg          蒸蛋         食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

4 个菜谱匹配“egg”。
```

Block C, in a new example with Eggplant:

```text
PS> recipe-menu search egg
ID                   Name                      Matched in
aubergine            Braised aubergine         ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "egg".

PS> recipe-menu search egg --lang zh
ID                   名称         匹配于
aubergine            烧茄子       食材
tomato-egg           番茄炒蛋     名称、食材
tomato-egg-noodles   番茄鸡蛋面   名称、食材

3 个菜谱匹配“egg”。

PS> recipe-menu search 茄
ID                   Name                      Matched in
aubergine            Braised aubergine         name, ingredient
tomato-egg           Tomato and egg stir-fry   name, ingredient
tomato-egg-noodles   Tomato and egg noodles    name, ingredient

3 recipes match "茄".

PS> recipe-menu search plant
ID          Name                Matched in
aubergine   Braised aubergine   ingredient

1 recipe matches "plant".
```

Block D, in a new example with Crème:

```text
PS> recipe-menu search crème
ID      Name            Matched in
creme   Crème caramel   name

1 recipe matches "crème".

PS> recipe-menu search Crème --lang zh
ID      名称       匹配于
creme   焦糖布丁   名称

1 个菜谱匹配“Crème”。

PS> recipe-menu search CARAMEL
ID      Name            Matched in
creme   Crème caramel   name

1 recipe matches "CARAMEL".
```

Block E, in a new example with the long name with S, the same for each S:

```text
PS> recipe-menu search long
ID       Name                Matched in
a-long   A long first line   name
         end

1 recipe matches "long".

PS> recipe-menu search long --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“long”。

PS> recipe-menu search 尾 --lang zh
ID       名称           匹配于
a-long   长长的第一行   名称
         尾

1 个菜谱匹配“尾”。

PS> recipe-menu search 大米
ID       Name                Matched in
a-long   A long first line   ingredient
         end
rice     Steamed rice        ingredient

2 recipes match "大米".

PS> recipe-menu search 大米 --lang zh
ID       名称           匹配于
a-long   长长的第一行   食材
         尾
rice     米饭           食材

2 个菜谱匹配“大米”。

PS> recipe-menu search steamed
ID     Name           Matched in
rice   Steamed rice   name

1 recipe matches "steamed".
```

Block F, in the init folder:

```text
PS> recipe-menu search 番茄
ID           Name                      Matched in
tomato-egg   Tomato and egg stir-fry   name, ingredient

1 recipe matches "番茄".

PS> recipe-menu search 番茄 --lang zh
ID           名称       匹配于
tomato-egg   番茄炒蛋   名称、食材

1 个菜谱匹配“番茄”。
```

The messages of `cli` in the cases have the texts of F05 design 2.10 with `search`: `TOO_FEW_ARGUMENTS` is `An argument is missing. Write "recipe-menu search WORD...".` and `缺少参数。请写成“recipe-menu search 词...”。`, and `UNKNOWN_OPTION` in its form for no options is `"search" has no option "--tag". It has no options of its own.` and `“search”没有选项“--tag”。它没有自己的选项。`. `RUN_HELP_COMMANDS` and `RUN_HELP_OPTIONS` of `tests/f09_texts.py` give the lines that follow them. The messages of the readers in the cases are those of section 2 of the F09 test plan: `FILE_MISSING`, `FOLDER_MISSING`, `FOLDER_IS_FILE`, `FILE_IS_FOLDER`, `MISSING_BRACE`, `NOT_A_RECIPE_ID` of a listing, `TOML_ENDING_NOT_SMALL`, `UNKNOWN_INGREDIENT(name="豆瓣酱")` of a recipe, and `UNKNOWN_MEAL(meal="supper")` of the settings, with the places `line 11` (`第 11 行`), `ingredient 3` (`食材 3`), and `meals` (`餐次`). `tests/f09_texts.py` writes each of them out.

The cases split into these files, so that each file stays within the 500 lines of R06:

| File | Cases |
| --- | --- |
| `tests/test_f10_command.py` | F10-T01 and F10-T02 |
| `tests/test_f10_search.py` | F10-T03 and F10-T04 |
| `tests/test_f10_places.py` | F10-T05 and F10-T06 |
| `tests/test_f10_words.py` | F10-T07 to F10-T09 |
| `tests/test_f10_count_line.py` | F10-T10 and F10-T11 |
| `tests/test_f10_widths_and_errors.py` | F10-T12 and F10-T13 |
| `tests/test_f10_cli_and_reads.py` | F10-T14 and F10-T15 |
| `tests/test_f10_integration.py` | F10-T16 to F10-T19 |
| `tests/test_f10_random.py` | F10-T20, with its generator of folders and words |
| `tests/test_f10_performance.py` | F10-T21 |
| `tests/f10_support.py` | No tests. The new named changes and the two texts of `aubergine` and `creme`. It reuses `make_home`, `copy_example`, and `run_module` of `tests/f05_support.py`, `no_data_folder` of `tests/f05_texts.py`, `call` and `snapshot` of `tests/f07_support.py`, `make_init`, `edit`, and the named changes of `tests/f07_changes.py`, `faults` of `tests/f08_support.py`, `at`, `made`, `new_context`, `run_command`, `assert_among_check`, the named changes, and the extra recipes of `tests/f09_support.py`, and `write` of `tests/f03_support.py`. |
| `tests/f10_texts.py` | No tests. The expected texts above and blocks A to F, as literals. It writes the 12 lines of the two tables of `HELP` and `HELP_ZH` out, and takes their other 6 lines from `HELP` and `HELP_ZH` of `tests/f09_texts.py`. It reuses `out`, `err`, `stop`, the problems and the messages of the readers, `MAPO`, `MAPO_ZH`, `unknown_id`, `RUN_HELP_COMMANDS`, and `RUN_HELP_OPTIONS` of `tests/f09_texts.py`. |
| `tests/pt01_support.py` | No tests. It gains `pt01_search`, the expected output of `search 食材001` on the PT01 folder (section 3). Its other functions keep their names and their behavior. |
| `tests/conftest.py` | Unchanged. F10 uses its fixtures `example_folder` and `default_int_limit`, and pytest's `tmp_path`, `monkeypatch`, and `record_property`. |

| ID | Level | Interface | What it tests | Setup and input | Expected result |
| --- | --- | --- | --- | --- | --- |
| F10-T01 | unit | `SEARCH_COMMAND`, `SEARCH_COMMAND.run`, `main` | The example of 2.1. `SEARCH_COMMAND` has the word `search`, the usage `search WORD...` and `search 词...`, the help line of the F05 prototype, the required argument `WORD` that repeats, no options, and `FolderUse.READ`. Its `run` writes the result in `context.lang` to `context.out` and gives 0, or writes the three lines of an error to `context.err` and gives 1. It uses neither `context.settings` nor `context.today`. The help lists `search WORD...` after `show ID`, with the second column of both tables after 19 columns, and has 18 lines (2.1, choice 1). | The example's lines, with `folder` as `example` and `home` as `home`. The `# raises` line runs inside `pytest.raises(UsageError)` with a new `Context` of the same values and new streams. In `help_lines`, the call of `main` also passes `commands=(INIT_COMMAND, CHECK_COMMAND, LIST_COMMAND, SHOW_COMMAND, SEARCH_COMMAND)`, because the 18 lines hold only while these five commands are alone in `COMMANDS`, and F11 to F13 add theirs. Then, each with new streams and `Context(Lang.EN, example, Settings(Lang.ZH, (Meal.BREAKFAST,), 5), out, err, date(2030, 1, 1))`: 1. `run` with `Arguments(("番茄",))`. 2. `run` with `Arguments(("葱", "quick"))`. 3. `run` with `Arguments(("lamb",))`. 4. The mapo mistake in `example`, and `run` with `Context(Lang.ZH, example, Settings(), out, err, date(2026, 11, 10))` and `Arguments(("lamb",))`. 5. The whole of `help_lines("--help")` and of `help_lines("--help", "--lang", "zh")`. 6. `--help` and `--help --lang zh` through `call`, with the real `COMMANDS`. | Every assertion of the example holds, and the `# raises` line raises `UsageError`, after which both of its streams are empty. 1. 0, out `[*TOMATO_TABLE, "", '2 recipes match "番茄".']`, and an empty err. 2. 0, out `[*SCALLION_QUICK_TABLE, "", '2 recipes match "葱" and "quick".']`, and an empty err. 3. 0, out `['No recipe matches "lamb".']`, and an empty err. 4. 1, an empty out, and err `STOP_ZH(recipes/mapo-tofu.toml，食材 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe)`, although `lamb` matches no recipe. 5. `HELP` and `HELP_ZH`. 6. Exit code 0 and an empty err. In out, the line after the line that starts with `  show ID ` starts with `  search WORD... ` and ends with `Find recipes by name, ingredient, or tag.`, or starts with `  search 词... ` and ends with `按名称、食材或标签找菜谱。`. Its text starts at the same display column as the text of the line that starts with `  --lang en\|zh`: the `display_width` of what comes before each text is the same. These rules hold whatever commands F11 to F13 add after `search`. |
| F10-T02 | unit | `SEARCH_COMMAND.run` | Step 1 of 2.2. `run` checks every word before it reads a file or writes any output. It raises `UsageError(EMPTY_WORD, None)` when the matching form of a word is empty: the empty text, or only whitespace as `str.strip()` removes it, U+00A0, U+3000, and U+2028 included, also when another word is fine. The error has no hint and no values. Any other word passes the check: U+200B ZERO WIDTH SPACE and U+FEFF ZERO WIDTH NO-BREAK SPACE, which are not whitespace, a word that starts with `-`, and a word of 5,000 digits, which stays a `str` (2.1 Errors, 2.2 step 1, choices 4 and 9). | With the fixture `default_int_limit`. Each call with new streams and `Context(Lang.EN, DataFolder(tmp_path / "missing"), Settings(), out, err, date(2026, 11, 10))`, inside `faults(tmp_path)`. 1. Inside `pytest.raises(UsageError)`: `Arguments(V)` for each V of `("",)`, `(" ",)`, `("\t",)`, `("\n",)`, `("\u00a0",)` (NO-BREAK SPACE), `("\u3000",)` (IDEOGRAPHIC SPACE), `("\u2028",)` (LINE SEPARATOR), `(" \u3000\t",)`, `("番茄", "")`, `("", "番茄")`, `(" ", "lamb")`, `("番茄", "\u3000")`, and `("番茄", "quick", "\t")`. 2. `Arguments(V)` for each V of `("\u200b",)`, `("\ufeff",)`, `("-x",)`, `("a",)`, `(" a ",)`, `("\u3000番茄",)`, `("9" * 5000,)`, and `("番茄", "\u200b")`. | 1. Each error's `text(Lang.EN)` is `EMPTY`, its `text(Lang.ZH)` is `EMPTY_ZH`, its `hint` is `None`, and its `values` are `()`. Both streams are empty after each call, and the record and the listings of the harness are empty. 2. No call raises. Each gives 1, an empty out, and err `STOP(catalog.toml, FILE_MISSING)`, because the folder is missing. |
| F10-T03 | functional | `recipe-menu search`, `main` | The example of 2.2, in order, with the real commands: the five outputs of the prototype, the place `名称`, a narrow table, a word that is part of longer names, whitespace inside a word, three words in both languages, a repeated word and a word that differs only in case, U+3000 at the start of a word, five things that do not count, a look-alike letter and a no-break space inside a word, empty words in both languages, a line with no word, an option that `search` lacks, a mistake in `mapo-tofu` that stops `search 番茄` but not `search ""`, and a folder with no recipe file (2.2, choices 3 to 8). | The example's lines, with `folder` as `example` and `home` as `home`, and the example's `run`, which calls `main` with no `commands`. | Every assertion of the example holds. |
| F10-T04 | functional | `recipe-menu search` | v0.1-S11 at `main`, and the F10 prototype in full, each output also in the other language. The other language uses new texts of point A: the English line for two words, the Chinese line for one word, and the place `名称` (2.2, choices 5 and 6). | In `example`: 1. `search 番茄`, `search TOMATO`, `search 葱 quick --lang zh`, `search lamb`, and `search 豆腐 quick --lang zh`. 2. `search 番茄 --lang zh`, `search TOMATO --lang zh`, `search 葱 quick`, `search lamb --lang zh`, and `search 豆腐 quick`. | 1. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`, `FOUND(TOMATO_TABLE, '2 recipes match "TOMATO".')`, the output of the prototype "Two words, in Chinese", `NONE('No recipe matches "lamb".')`, and `NONE("没有菜谱同时匹配“豆腐”和“quick”。")`: the five outputs of the prototype, each with exit code 0, as v0.1-S11 expects. 2. `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“番茄”。")`, `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“TOMATO”。")`, `FOUND(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')`, `NONE("没有菜谱匹配“lamb”。")`, and `NONE('No recipe matches "豆腐" and "quick".')`. |
| F10-T05 | functional | `recipe-menu search` | Choice 3. A word appears in a place when it appears in one of the place's texts in either language: the recipe's names, both names of the catalog's ingredient of each line, and both names of each tag. A line refers to the catalog's ingredient whatever name the file writes. So `search scallion` finds every recipe whose file writes `葱`, and a file that writes `EGG` for 鸡蛋 changes nothing. A name that lacks one language has only the other text, and the Name cell shows that text in both languages. The places of a row come from the words, so a row of `search 鸡蛋` holds `ingredient` without `name` when only an ingredient holds the word (2.2 table of places, choice 3). | 1. In `example`: the lines of block A from `search 炒蛋` to `search red-braised`. 2. Egg in English in a new example: `search 鸡蛋` and `search 鸡蛋 --lang zh`. 3. The extra recipes in a new example: the six lines of block B. | 1 and 3. Each line gives the output of its line in block A or B. 2. The outputs of the same two lines of block A. So `search home` gives `tag` for four recipes, and `search scallion` gives `ingredient` for five. `search 蒸` finds `steamed-egg` by its Chinese name and shows `蒸蛋` in the English table. `search egg` finds `steamed-egg` by the English name `Egg` of the ingredient that its file writes as `鸡蛋`. The warnings of `red-braised-pork` and of the extra recipes are not written. |
| F10-T06 | functional | `recipe-menu search` | Choice 3. Nothing else counts: no note, step, ID, servings, quantity, amount, unit, or category, and no name of a catalog ingredient or tag that no recipe of the folder uses. Each such word gives the one line of no match, with exit code 0 (2.2, choices 3 and 6). | 1. In `example`: `search W` for each W of `wedges` and `切块` (notes of `tomato-egg`), `crushed` (a note of `choy-sum`), `scramble` and `热锅` (steps of `tomato-egg`), `dairy` and `蛋奶` (the category of eggs), `produce` (a category key), `mapo-tofu` and `cola-wings` (IDs), `2` (servings), `300` (a quantity), `tbsp` (a unit), `适量` (an amount), `片` (the default unit of 姜), and `broccoli` and `西兰花` (an ingredient of the catalog that no recipe uses). Then `search 切块 --lang zh` and `search dairy --lang zh`. 2. The extra recipes in a new example: `search room` (an English note), `search 打散` (a Chinese note), and `search 烧开` (a Chinese step). 3. Eggplant in a new example: `search strips` (an English step). 4. Soup in a new example: `search soup` and `search 汤 --lang zh`. | 1. Each W gives `NONE('No recipe matches "W".')`. The last two lines give `NONE("没有菜谱匹配“切块”。")` and `NONE("没有菜谱匹配“dairy”。")`. 2 and 3. Each gives `NONE('No recipe matches "W".')` for its word W. 4. `NONE('No recipe matches "soup".')` and `NONE("没有菜谱匹配“汤”。")`. |
| F10-T07 | functional | `matching_form`, `recipe-menu search` | The example of 3.1 and choice 4. A word appears in a text when its matching form is part of the text's matching form. A word can be part of a longer name, in English and in Chinese. Case counts only for the letters A to Z, so `È` and `è` differ. Whitespace at both ends of a word does not count, U+00A0 and U+3000 included. Whitespace inside a word counts as written, U+00A0 included. Look-alike letters stay as they are, no text is normalized, and U+200B and U+FEFF are characters of the word. A word that starts with one `-` is a word, and a word that starts with `--` is an option for `cli`. The count line shows each word as typed (3.1, choice 4). | 1. The example of 3.1. 2. In `example`: `search W` for each W of `tomato`, `Tomato`, `tOmAtO`, `" tomato "`, `"\u00a0番茄\t"`, and `"\u3000TOMATO\u3000"`. 3. In `example`: the lines of block A from `search "choy sum"` to `search MAPO --lang zh`. 4. In `example`: `search W` for each W of `"and  egg"` (two spaces), `"choy\u00a0sum"`, `"stir fry"`, `"番\u200b茄"`, `"\u200b"`, `"\ufeff番茄"`, `"T\u043emato"` (U+043E CYRILLIC SMALL LETTER O), `"R\u0130CE"` (U+0130 LATIN CAPITAL LETTER I WITH DOT ABOVE), and `-x`. Then `search --x`. 5. Eggplant in a new example: the four lines of block C. 6. Crème in a new example: the three lines of block D, then `search CRÈME`, `search CRÈME --lang zh`, `search creme`, and `search "Cre\u0300me"`, whose e is followed by U+0300 COMBINING GRAVE ACCENT. | 1. Every assertion of the example holds. 2. Each W gives `FOUND(TOMATO_TABLE, '2 recipes match "W".')`, with W as typed. 3 and 5. Each line gives the output of its line in block A or C. So `-fr` and `-` are words, `鸡` is part of `可乐鸡翅`, `鸡翅中`, `鸡蛋`, and `番茄鸡蛋面`, and `egg` is part of `Eggplant`. 4. Each W gives `NONE('No recipe matches "W".')`, and `search --x` gives `(2, err ['"search" has no option "--x". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`. 6. The outputs of block D, then `NONE('No recipe matches "CRÈME".')`, `NONE("没有菜谱匹配“CRÈME”。")`, `NONE('No recipe matches "creme".')`, and `NONE('No recipe matches "Cre\u0300me".')`, because the file writes è as one character. |
| F10-T08 | functional | `recipe-menu search` | Choice 4. A recipe matches only when every word appears in at least one of its places, and two words may appear in different places. The order of the words changes neither the recipes nor their places, only the order of the words in the count line. A word that no recipe holds leaves no match, whatever the other words find (2.2 step 4, choice 4). | In `example`: 1. `search quick 葱` and `search quick 葱 --lang zh`. 2. `search tomato egg`. 3. The lines of block A from `search egg noodle` to `search home 葱`. 4. `search tomato egg quick 葱` and `search tomato egg quick 葱 --lang zh`. 5. `search egg spicy`, `search egg spicy --lang zh`, `search 葱 quick lamb`, and `search 葱 quick lamb --lang zh`. | 1. `FOUND(SCALLION_QUICK_TABLE, '2 recipes match "quick" and "葱".')` and `FOUND(SCALLION_QUICK_TABLE_ZH, "2 个菜谱同时匹配“quick”和“葱”。")`: the rows and the places of the prototype's `search 葱 quick`. 2. `FOUND(TOMATO_TABLE, '2 recipes match "tomato" and "egg".')`. 3. The outputs of their lines in block A. 4. `FOUND(ALL_THREE_TABLE, '2 recipes match "tomato", "egg", "quick", and "葱".')` and `FOUND(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“tomato”、“egg”、“quick”和“葱”。")`. 5. `NONE('No recipe matches "egg" and "spicy".')`, `NONE("没有菜谱同时匹配“egg”和“spicy”。")`, `NONE('No recipe matches "葱", "quick", and "lamb".')`, and `NONE("没有菜谱同时匹配“葱”、“quick”和“lamb”。")`. |
| F10-T09 | functional | `recipe-menu search` | Choice 5. The `Matched in` cell names each place where at least one word appears, in the order name, ingredient, tag, and each place once, whatever the order of the words. `comma_list` joins the places with `, ` in English and with `、` in Chinese (2.2 rows, choice 5). | In `example`: 1. `search quick 番茄`, `search 番茄 tomato`, and `search 番茄 快手 --lang zh`. 2. The lines of block A from `search 米饭 主食` to `search scallion QUICK noodle --lang zh`. | 1. `FOUND(ALL_THREE_TABLE, '2 recipes match "quick" and "番茄".')`, `FOUND(TOMATO_TABLE, '2 recipes match "番茄" and "tomato".')`, and `FOUND(ALL_THREE_TABLE_ZH, "2 个菜谱同时匹配“番茄”和“快手”。")`. 2. The outputs of their lines in block A. With F10-T04, F10-T05, and F10-T07, each of the seven cells `name`, `ingredient`, `tag`, `name, ingredient`, `name, tag`, `ingredient, tag`, and `name, ingredient, tag` appears in English, and each of `名称`, `食材`, `标签`, `名称、食材`, `名称、标签`, `食材、标签`, and `名称、食材、标签` in Chinese. |
| F10-T10 | functional | `recipe-menu search` | Choice 6 and the new texts of point A. The count line uses `RECIPES_MATCH` for one word and `RECIPES_MATCH_ALL` for two or more, counted after each word that equals an earlier word exactly is left out. Each is a `Plural` by the number of recipes, and only the Chinese text of `RECIPES_MATCH_ALL` holds 同时. No match gives `NO_RECIPE_MATCHES` or `NO_RECIPE_MATCHES_ALL` by the same count of words. `{words}` is `and_list` of the quoted words. Each word is written as typed: its case, its spaces, a `"`, braces, a line break, and 5,000 digits stay as they are (2.2 messages, choices 6 and 9). | With the fixture `default_int_limit`. In `example`: 1. `search scallion QUICK noodle`, `search mapo --lang zh`, and `search 葱 quick 面 --lang zh`. 2. `search egg egg`, `search egg egg --lang zh`, `search egg EGG`, `search egg EGG --lang zh`, `search egg " egg"`, `search 葱 quick 葱`, and `search 葱 quick 葱 --lang zh`. 3. `search lamb lamb`, `search lamb lamb --lang zh`, `search quick 1`, `search quick 1 --lang zh`, `search lamb beef fish`, and `search lamb beef fish --lang zh`. 4. `search 'say "hi"'`, `search 'say "hi"' --lang zh`, `search "{words}"`, `search "{count}" --lang zh`, `search "to\nmato"`, `search "番茄\n"`, and `search X`, where X is `"9" * 5000`. | 1. The output that the design's example of 2.2 gives for `search scallion QUICK noodle`, which ends with `1 recipe matches "scallion", "QUICK", and "noodle".`. Then the output of `search mapo --lang zh` in block A, which ends with `1 个菜谱匹配“mapo”。`, and the output that the design's example gives for `search 葱 quick 面 --lang zh`, which ends with `1 个菜谱同时匹配“葱”、“quick”和“面”。`. 2. `FOUND(TOMATO_TABLE, '2 recipes match "egg".')`, `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“egg”。")`, `FOUND(TOMATO_TABLE, '2 recipes match "egg" and "EGG".')`, `FOUND(TOMATO_TABLE_ZH, "2 个菜谱同时匹配“egg”和“EGG”。")`, `FOUND(TOMATO_TABLE, '2 recipes match "egg" and " egg".')`, `FOUND(SCALLION_QUICK_TABLE, '2 recipes match "葱" and "quick".')`, and the output of the prototype "Two words, in Chinese". 3. `NONE('No recipe matches "lamb".')`, `NONE("没有菜谱匹配“lamb”。")`, `NONE('No recipe matches "quick" and "1".')`, `NONE("没有菜谱同时匹配“quick”和“1”。")`, `NONE('No recipe matches "lamb", "beef", and "fish".')`, and `NONE("没有菜谱同时匹配“lamb”、“beef”和“fish”。")`. 4. `NONE('No recipe matches "say "hi"".')`, `NONE("没有菜谱匹配“say "hi"”。")`, `NONE('No recipe matches "{words}".')`, `NONE("没有菜谱匹配“{count}”。")`, `NONE('No recipe matches "to\nmato".')`, `FOUND(TOMATO_TABLE, '2 recipes match "番茄\n".')`, and `NONE(f'No recipe matches "{X}".')`. In `to\nmato` and `番茄\n`, the line break of the word breaks the count line on out. |
| F10-T11 | functional | `recipe-menu search`, `main` | Choice 4 and point B. A word whose matching form is empty gives `EMPTY_WORD` with exit code 2, one line on the error stream with no hint, and nothing on the output stream. The line is in the language of the output, which can come from the settings. `run` checks the words before it reads a file, so a folder with an error in the catalog, the listing, or a recipe gives the same result. `cli` checks the data folder, the settings, `--help`, and the options before it runs `search`, so each of them comes first (2.2 step 1 and Errors, choice 8). | 1. In `example`: `search` with the words W for each W of `[""]`, `[" "]`, `["\t"]`, `["\u00a0"]`, `["\u3000"]`, `["\u2028"]`, `["番茄", ""]`, `["", "番茄"]`, `[" ", "lamb"]`, `["番茄", "\u3000"]`, and `["", ""]`. Then `search "" --lang zh` and `search 番茄 " " --lang zh`. 2. Chinese settings in a new example: `search ""` and `search "" --lang en`. 3. Each in a new example: no catalog and `search ""`, the catalog brace and `search " " --lang zh`, no recipes folder and `search "\u3000"`, Rice Bowl and `search ""`, and the mapo mistake and `search "" 番茄`. Then `search 番茄` in each of these five folders. 4. M is `tmp_path / "missing"`: `search ""` in M and `search "" --lang zh` in M. 5. Broken settings in a new example: `search ""`. 6. In `example`: `search "" --help` and `search "" --tag x`. | 1. Each W gives `(2, err [EMPTY])`, and the last two lines give `(2, err [EMPTY_ZH])`. 2. `(2, err [EMPTY_ZH])` and `(2, err [EMPTY])`. 3. `(2, err [EMPTY])`, `(2, err [EMPTY_ZH])`, `(2, err [EMPTY])`, `(2, err [EMPTY])`, and `(2, err [EMPTY])`. Then `search 番茄` gives, in order, `(1, err STOP(catalog.toml, FILE_MISSING))`, `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`, `(1, err STOP(recipes, FOLDER_MISSING))`, `(1, err STOP(recipes/Rice Bowl.toml, NOT_A_RECIPE_ID of a listing))`, and `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe))`. 4. `no_data_folder(M)` and `no_data_folder(M, ZH)`. 5. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`. 6. Exit code 0, an empty err, and on out the same text as `--help` with no folder, then `(2, err ['"search" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`. |
| F10-T12 | functional | `recipe-menu search` | Choice 7. `search` passes `format_table` no `min_widths`, so each column is as wide as the widest line of its own cells, the heading included, and the table of a narrow result stays narrow. `search` measures no recipe that it does not show. A name of two lines takes two lines, and its width is that of its longer line, whichever line break the name holds (2.2 output, choice 7, F02 design 2.9). | 1. In `example`: `search mapo`, `search mapo --lang zh`, `search rice`, `search rice --lang zh`, `search spicy`, `search cola`, and `search cola --lang zh`. 2. For each S of `\n`, `\r\n`, and `\u2028`, a new example with the long name with S. In it: the six lines of block E. | 1. `search mapo` gives the output that the design's example of 2.2 gives for it, and each other line gives the output of its line in block A. In `search mapo`, the Name column starts after 12 columns, where the widest ID of the folder, `tomato-egg-noodles`, would put it after 21. In `search rice --lang zh`, the Name column is as wide as its heading `名称`. 2. For each S, the six lines give the outputs of block E, with the same texts for each S. So no output holds U+000D or U+2028, the Name cell of `a-long` takes two lines, and `search steamed` gives a table with the widths of `rice` alone. A width taken from a whole cell, or from its lines split only at U+000A, would make the Name column wider. |
| F10-T13 | functional | `recipe-menu search`, `recipe-menu check` | Choice 8. An error stops `search` at the first error, with the three lines of `stop_at_error` in the language of the output, exit code 1, and nothing on the output stream. The catalog comes first, then the listing of `recipes/`, then the recipes in the order of the IDs. `search` parses every recipe before it matches one, so an error in any recipe file stops it, also when the words match nothing in that recipe. A missing `recipes/` stops it, and a `recipes/` with no recipe file gives the one line of no match with exit code 0. Warnings are not written and change nothing. The error that stopped `search` is among the errors of `check` (2.2 steps 2 and 3, choice 8). | Each input of 1 to 11 in a new example, with `search 番茄`, `search 番茄 --lang zh`, `search lamb`, `check`, and `check --lang zh`: 1. No catalog. 2. The catalog brace. 3. No recipes folder. 4. Recipes as a file. 5. Rice Bowl. 6. Capital rice. 7. Folder x. 8. The mapo mistake. 9. The mapo mistake and rice at 0. 10. The mapo mistake and Rice Bowl. 11. The catalog brace and the mapo mistake. Then, each in a new example: 12. Empty recipes: `search 番茄`, `search 番茄 --lang zh`, and `search 番茄 quick`. 13. Not recipes: `search 番茄`. 14. In `example`: `search pork`. | 1 to 11. `search 番茄` and `search lamb` give `(1, err STOP(W, M))`, and `search 番茄 --lang zh` gives `(1, err STOP_ZH(W, M))`, with W and M: 1. `catalog.toml` and `FILE_MISSING`. 2. `catalog.toml, line 11` and `MISSING_BRACE`. 3. `recipes` and `FOLDER_MISSING`. 4. `recipes` and `FOLDER_IS_FILE`. 5. `recipes/Rice Bowl.toml` and `NOT_A_RECIPE_ID` of a listing. 6. `recipes/rice.TOML` and `TOML_ENDING_NOT_SMALL`. 7. `recipes/x.toml` and `FILE_IS_FOLDER`. 8 and 9. `recipes/mapo-tofu.toml, ingredient 3` and `UNKNOWN_INGREDIENT(name="豆瓣酱")` of a recipe, the first ID with an error. 10. W and M of 5, because `read_recipes` gives the problems of the listing first. 11. W and M of 2. In each input, the error is among the errors of `check` in both languages. 12. `NONE('No recipe matches "番茄".')`, `NONE("没有菜谱匹配“番茄”。")`, and `NONE('No recipe matches "番茄" and "quick".')`. 13. `NONE('No recipe matches "番茄".')`, because neither entry is a recipe file. 14. The output that the design's example of 2.2 gives for `search pork`, with an empty err, although `red-braised-pork` has a warning. |
| F10-T14 | functional | `recipe-menu search`, `main` | The files that `search` reads. It reads the catalog once, lists `recipes/` once, and reads each recipe file once, in the order of the IDs, also when no recipe matches. After an empty word, for `--help`, and for a line with no word, it reads nothing, and after an error in the catalog it lists nothing. It reads neither the pantry nor a menu, so mistakes there change nothing (2.2 side effects, choice 8, architecture 8). | Lines 1 to 5 and 7 run in `example`, each inside a new `faults(example.root)`: 1. `search 番茄`. 2. `search 葱 quick --lang zh`. 3. `search lamb`. 4. `search ""`. 5. `search 番茄 ""`. 6. The catalog brace in a new example, and `search 番茄` inside `faults` of its root. 7. `search 番茄 --help`, and `search`. Then the comma, the typo, and `menus/2026-W48.toml` written with `[[[\n`, in `example`. 8. Without the harness: `search 番茄` and `search 葱 quick --lang zh`. | The record, the listings, and the result: 1. `read settings.toml`, `read catalog.toml`, and `read recipes/<ID>.toml` for each of the seven IDs of the example in the order of the IDs, from `choy-sum` to `tomato-egg-noodles`, the listing `recipes`, and `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`. 2. The same record and listing, and the output of the prototype "Two words, in Chinese". 3. The same record and listing, and `NONE('No recipe matches "lamb".')`. 4 and 5. `read settings.toml` alone, no listing, and `(2, err [EMPTY])`. 6. `read settings.toml` and `read catalog.toml`, no listing, and `(1, err STOP(catalog.toml, line 11, MISSING_BRACE))`. 7. For each line, `read settings.toml` alone and no listing, with exit code 0 and the help, then with exit code 2 and the two lines of `TOO_FEW_ARGUMENTS`. 8. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')` and the output of the prototype "Two words, in Chinese". |
| F10-T15 | functional | `recipe-menu search`, `main` | `cli` reports the mistakes on the command line, a missing data folder, and broken settings before it runs `search`, with the messages and exit codes of F05: no word, and an option that `search` lacks, in both languages. `search --help` shows the help and runs nothing. The same folders then give the output of `search` (2.2 Errors, F05 design 2.10). | 1. In `example`: `search`, `search --lang zh`, `search 番茄 --tag quick`, `search 番茄 --tag quick --lang zh`, and `search --tag`. 2. M is `tmp_path / "missing"`: `search 番茄` in M and `search 番茄 --lang zh` in M. 3. Broken settings in a new example: `search 番茄`. 4. The mapo mistake in a new example: `search 番茄 --help`, `search --help --lang zh`, and `search lamb --help`. 5. In `example`: `search 番茄`. | 1. `(2, err ['An argument is missing. Write "recipe-menu search WORD...".', 'Run "recipe-menu --help" to see the commands.'])`, `(2, err ["缺少参数。请写成“recipe-menu search 词...”。", "运行“recipe-menu --help”查看命令。"])`, `(2, err ['"search" has no option "--tag". It has no options of its own.', 'Run "recipe-menu --help" to see the options.'])`, `(2, err ["“search”没有选项“--tag”。它没有自己的选项。", "运行“recipe-menu --help”查看选项。"])`, and for `search --tag` the same as the third, because `cli` checks the options before the number of words. 2. `no_data_folder(M)` and `no_data_folder(M, ZH)`. 3. `(1, err STOP(settings.toml, meals, UNKNOWN_MEAL(meal="supper") of the settings))`. 4. Each gives exit code 0, an empty err, and on out the same text as `--help`, or as `--help --lang zh` for the second line, with no folder. 5. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`. |
| F10-T16 | integration | `recipe-menu search`, `main` | v0.1-S23 at `main` for `search`. `search` writes no file, whatever it reports. Every file and folder under `home` and under the current folder keeps its bytes and its modification time, and no entry is added (2.2 side effects). | A new example at `home / "recipe-menu"`, with an empty `shopping/`, and the empty current folder `tmp_path / "cwd"`, entered with `monkeypatch.chdir`. `snapshot` of `tests/f07_support.py` of `home` and of the current folder, before the lines and after them. The lines, each with no folder: `search 番茄`, `search 葱 quick --lang zh`, `search lamb`, `search ""`, `search`, `search 番茄 --tag quick`, and `search 番茄 --help`. Then the mapo mistake, new snapshots, and `search 番茄` and `search lamb`. | The results, in order: `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`, which is the line that v0.1-S23 runs, the output of the prototype "Two words, in Chinese", `NONE('No recipe matches "lamb".')`, `(2, err [EMPTY])`, exit code 2 with the two lines of `search` of F10-T15, exit code 2 with the two lines of `search 番茄 --tag quick` of F10-T15, and exit code 0 with the help. After the mapo mistake, both give `(1, err STOP(recipes/mapo-tofu.toml, ingredient 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe))`. Each snapshot after the lines equals the snapshot before them. |
| F10-T17 | integration | `recipe-menu show`, `recipe-menu search`, `main` | The hint of F09's `UNKNOWN_ID` names `recipe-menu search ID`, and that search runs. It finds a recipe by a word of its name, such as `mapo` for `mapo-tofu`, and finds nothing for a typo of an ID, because an ID is not a place (choice 3, F09 design 2.4). | In `example`: 1. `show mapo`, then `search mapo`. 2. `show mapo --lang zh`, then `search mapo --lang zh`. 3. `show pork`, then `search pork`. 4. `show tomato-eggs`, then `search tomato-eggs`. | 1. `(1, err [MAPO])`, with `MAPO` of `tests/f09_texts.py`, whose hint names `recipe-menu search mapo`. Then the output that the design's example of 2.2 gives for `search mapo`. 2. `(1, err [MAPO_ZH])`, then the output of `search mapo --lang zh` in block A. 3. `(1, err ['No recipe has the ID "pork". Run "recipe-menu search pork" to find it.'])`, then the output that the design's example gives for `search pork`. 4. `(1, err ['No recipe has the ID "tomato-eggs". Run "recipe-menu search tomato-eggs" to find it.'])`, then `NONE('No recipe matches "tomato-eggs".')`. |
| F10-T18 | integration | `recipe-menu search`, `main` | `search` reads the data folder that `cli` picks and writes in the language that `cli` picks: `--data`, else `RECIPE_MENU_DATA`, else `~/recipe-menu`, and `--lang`, else the language of the settings, else English. Data files with a byte order mark and CRLF line ends give the same output, as v0.1-S08 expects of the other commands (2.2 parameters, F05 design 2.10). | B is a new example at `tmp_path / "One Drive" / "菜谱"`, and C is the init folder at `tmp_path / "c"`. E is `{"RECIPE_MENU_DATA": str(C)}`. 1. `search 番茄` in B. 2. `search 番茄` and `search 番茄 --lang zh`, each with no folder and `environ` E. 3. `search 番茄` in B with `environ` E. 4. `search 番茄` with no folder. 5. Chinese settings in a new example at `home / "recipe-menu"`: `search 番茄`, `search 番茄 --lang en`, and `search 葱 quick`, each with no folder. 6. BOM and CRLF in a new example: `search 番茄` and `search 葱 quick --lang zh`. | 1. `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')`. 2. The two outputs of block F, which find only `tomato-egg`. 3. The output of 1. 4. `no_data_folder(home / "recipe-menu")`. 5. `FOUND(TOMATO_TABLE_ZH, "2 个菜谱匹配“番茄”。")`, the output of 1, and the output of the prototype "Two words, in Chinese". 6. The output of 1, and the output of the prototype "Two words, in Chinese". |
| F10-T19 | integration | `python -m recipe_menu` | The real entry point runs `search` with the real commands. It writes the output as UTF-8 to stdout, whatever encoding Python gave the streams, and the message of exit code 1 or 2 to stderr (2.2, F05 design 2.9). | `run_module` of `tests/f05_support.py`, as in F09-T26, which sets `HOME` and `USERPROFILE` to `tmp_path / "home"` and `PYTHONIOENCODING` to `ascii`. With `example`: 1. `search 葱 quick --lang zh --data <example>`. 2. `search lamb --lang zh --data <example>`. 3. `search "" --data <example>`. 4. `search 番茄` with `data=example.root`, which sets `RECIPE_MENU_DATA`. 5. The mapo mistake in `example`, then `search 番茄 --lang zh --data <example>`. | 1. Exit code 0, the lines of the output of the prototype "Two words, in Chinese" on stdout, and an empty stderr. 2. Exit code 0, the line `没有菜谱匹配“lamb”。` on stdout, and an empty stderr. 3. Exit code 2, an empty stdout, and the line `EMPTY` on stderr. 4. Exit code 0, the lines of `FOUND(TOMATO_TABLE, '2 recipes match "番茄".')` on stdout, and an empty stderr. 5. Exit code 1, an empty stdout, and the three lines of `STOP_ZH(recipes/mapo-tofu.toml，食材 3, UNKNOWN_INGREDIENT(name="豆瓣酱") of a recipe)` on stderr. |
| F10-T20 | integration | `recipe-menu search`, `main` | Random folders and words. For any mix of recipes, of names in one or two languages, of ingredients and tags written by either name, and of words that are parts of those names in random case, with whitespace at their ends, repeated, empty, or found nowhere, `search` gives the lines that the rules of 2.2 give, in both languages. Random mixes reach places, orders, widths, and count lines that the other cases do not list (2.2, choices 3 to 7). | `random.Random(20261113)` builds 100 folders, each a new example with its seven recipe files deleted. Each choice below has equal chances unless it says otherwise. Each folder gets 1 to 6 recipes, with IDs drawn without repeats from `a`, `a-b`, `b`, `egg`, `rice`, `tomato-egg`, `tomato-egg-noodles`, and `z`. A name has an English text, a Chinese text, or both. An English text is 1 to 3 words from `Tomato`, `egg`, `stir-fry`, `Pork`, `belly`, `Mapo`, `tofu`, `rice`, and `Noodles`, joined by spaces. A Chinese text is 1 to 4 characters from 番, 茄, 炒, 蛋, 红, 烧, 肉, 面, 葱, and 米. A recipe has 0 to 3 different tags and 0 to 4 different ingredients of the catalog, each in a random order and each written by its Chinese or its English name. Each ingredient has the amount `适量`. Each recipe makes 2 servings and has one step in each language. Then each folder gets 3 lines `search W... --lang L`, with L picked at random and 1 to 3 words. A word is one of these, with these chances: a run (13 in 20), a word that no name holds (2 in 20), an earlier word of the same line again (4 in 20, or a run for the first word), and an empty word, `""`, `" "`, or `"\u3000"` (1 in 20). A run is 1 to 4 characters from a random place of a random text of the folder, or the whole text when it is shorter. The texts are the names of the folder's recipes and both names of each ingredient and each tag that one of its recipes uses. Each ASCII letter of a run is then a capital or a small letter. A word that no name holds is `lamb`, `dairy`, `-x`, `"\u200b"`, or `"\uff34omato"`. A run and a word that no name holds then get, with a chance of 1 in 4, whitespace at both ends, each end one of a space, a tab, U+00A0, and U+3000. | Each line gives the result that the test builds from the recipes that it wrote, by the rules of 2.2. When the matching form of a word is empty, that is `(2, err [EMPTY])` or `(2, err [EMPTY_ZH])`. Otherwise it is exit code 0, an empty err, and on out either the table and the count line of the recipes that match, or the one line of no match. The test builds the matching form of a word and of a name with its own code, as `str.strip()` and then each A to Z changed to a to z. It does not call `matching_form`, so the case checks the rule and not a copy of it. A row holds the ID, the name in L with the fallback of `BiText.get`, and the places in the order name, ingredient, tag. The rows come in code point order of the IDs. The test lays out the table with F02's `format_table` and no `min_widths`, joins the places with `comma_list`, and joins the quoted words of the count line with `and_list`. It writes the texts of the headings, of the places, and of the count lines as literals, and it uses no code of F10. |
| F10-T21 | performance | `recipe-menu search`, `python -m recipe_menu` | PT01 and v0.1-S30: `search` looks for the name of the ingredient that every recipe uses, and prints all 1,000 recipes of the PT01 data folder within 1 second, as the median of 5 runs from start to exit (requirements 7.1, 2.2, choice 10). | The PT01 data folder of section 3, in `tmp_path / "pt01"`. One untimed run, then 5 timed runs of `python -m recipe_menu search 食材001 --data <pt01>`, as section 3 says. | Each run exits with 0, writes the 1,003 lines of the PT01 search of section 3 on stdout, and writes nothing on stderr. The median of the 5 timed runs is under 1 second on Windows and under 3 seconds on Linux. |

## 3. Performance cases

PT01 names `search` among its commands (requirements 7.1), so `recipe-menu search` gets one case, and no other interface of F10 gets one (R14).

| ID | Target | Machine | Margin | Baseline |
| --- | --- | --- | --- | --- |
| F10-T21 | PT01: `recipe-menu search` finishes within 1 second with 1,000 recipes, 300 catalog ingredients, and 52 week menus. The median of 5 runs from start to exit counts. | Troy's PC: Windows 11, with Python 3.13 of the `recipe-menu` environment. The case also runs in CI, on the `ubuntu-24.04` runner of `.github/workflows/troy-mode.yml`, which is not a fixed machine (architecture 10). | On Windows, none: the median must be under 1 second, because a margin above PT01 would pass a command that misses it (v0.1 test plan, section 3). On Linux, 3 seconds, as F07-T25 and F09-T28 have, so that the case holds on a runner of unknown speed and still fails a slowdown of several times. | First run. The Architect's model took a median of 0.789 s (0.785 to 0.802 s) for `search 食材001` on Troy's PC, beside 0.794 s (0.791 to 0.794 s) for `list` in the same session (design section 4). F09's implementation PR recorded a median of 0.789 s for `list`. A model is not the implementation, so the F10 implementation PR records the first baseline. |

**Which system is Troy's PC.** CI runs only on Linux, and only Troy's PC runs the tests on Windows. So the case applies the limit of `time_limit` of `tests/pt01_support.py`: 1 second when `sys.platform == "win32"`, and 3 seconds otherwise, as F07-T25 and F09-T28 do. A CI job on Windows would change this plan first.

**The PT01 data folder.** `make_pt01` of `tests/pt01_support.py` writes it, as for F07-T25 and F09-T28, with the shape that the v0.1 test plan gives it. F10 does not change the generator. The first ingredient line of each recipe names `食材001`, the Chinese name of `Ingredient 001`. No other name in the folder holds `食材001`: the other ingredients are `食材002` to `食材300`, the recipes are `Recipe 0001` to `Recipe 1000` and `菜谱0001` to `菜谱1000`, and the tags are those of the example. So `search 食材001` matches every recipe, and in `ingredient` only.

**The timed run.** The case uses the general timed run of F09 in `tests/pt01_support.py`: `command_run`, `command_runs`, `record_times`, and `time_limit`, which keep their names and their behavior.

**The expected output.** `tests/pt01_support.py` gains `pt01_search`, which builds the result with f-strings from the rules of the generator, and not with F02's `format_table`. The PT01 search is 1,003 lines. Line 1 is `ID            Name          Matched in`. For each k from 1 to 1,000, line k + 1 is the ID `recipe-NNNN`, three spaces, the name `Recipe NNNN`, three spaces, and `ingredient`, so the row of recipe 1 is `recipe-0001   Recipe 0001   ingredient`. Then an empty line and `1000 recipes match "食材001".`.

**The steps of the case.**

1. Generate the folder.
2. Start the command once, untimed, and check its result as in step 3. Windows reads the 1,053 new files slowly the first time (F07 test plan, section 3), and Troy's own data folder does not pay that cost on each run.
3. Start the same command 5 times, each as a new process, with `command_runs`: `sys.executable -m recipe_menu`, in `tmp_path`, with `HOME` and `USERPROFILE` set to an empty home folder and without `RECIPE_MENU_DATA`. Each run must exit with 0, give exactly the expected stdout, and give an empty stderr. A run that does not fails the case, whatever its time.
4. Take the median of the 5 times, and compare it with the limit of the system.
5. Record the 5 times, the median, and the range with `record_property`, so that the JUnit report holds them for the next comparison.

**How it runs on Troy's PC.** The case lives in `tests/`, so it runs in every full test run on Troy's PC, which the main session starts with the Python of the `recipe-menu` environment for each PR. In the F10 implementation PR, the main session also runs it alone, with `python -m pytest tests/test_f10_performance.py --junitxml=reports/pt01-f10.xml`, while no other test run, build, or install is going on. The PR description reports the median and the range, and that run is the baseline. If `search` comes close to the limit, design choice 10 names the first step: a `[refactor]` PR that makes `Message.render` parse each template once, before the implementation PR. The release test runs v0.1-S30 on the same machine.

**The benchmark checklist.** The case answers the questions of `benchmark-checklist` in these ways:

- The limiter: design choice 10 and section 4 name it. `search` reads what `list` reads, so reading the 1,000 recipe files limits it, as it limits `list` and `check`. The matching adds about 2,600 matching forms, 2,600 tests with `in`, and 14,000 lookups for one word, and the table holds about 32,000 characters. The Architect's model took about the same time for `search` as for `list`. The case does not profile, because a profiler slows the run. A `[refactor]` PR profiles.
- Tuning: each run is a new Python process with the installed package and its compiled files, with no coverage and no debugger, as Troy runs it. The untimed run of step 2 has read the files once. coverage.py measures only the test process, so `coverage run -m pytest` in CI does not slow the timed processes.
- Limits: `search` writes about 40 KB through a pipe, and the 1,053 files hold about 2 MB, which a disk reads in milliseconds. So the time measures the work of Python.
- Errors: steps 2 and 3 check the exit code, the whole stdout, and the empty stderr of each run.
- Repeatability: 5 timed runs, with the median and the range recorded. A difference from the baseline that is smaller than the range of the baseline's runs is no measurable change.
- Relevance: the case times the whole command from start to exit, which is what Troy waits for. A word that every recipe holds makes `search` write a row for each of the 1,000 recipes, which is the most that `search` can write. Each further word adds about 2,600 tests with `in` (design choice 10), a small part of the time of reading the files.
- The work happened: the 1,000 rows, each matched in `ingredient`, and the count line show that `search` read and matched every recipe.

## 4. Not tested

| What | Why |
| --- | --- |
| The fields of `SEARCH_COMMAND` on their own, the name that `__all__` lists in `recipe_menu.commands.search`, the messages as constants in `search/messages.py`, and `matching_form` on its own. | The mock declares them in full and exports F03's working function, so a test of them alone would pass against the mock (R09). F10-T01 checks the fields beside a run, F10-T07 checks `matching_form` beside the searches that use it, and the cases check every text through the output. Code review checks where the texts live. |
| `search` imports only `app`, `lang`, `text`, `datafile`, `catalog`, and `recipes`, and nothing from `browse`. | R07. The dependency checker in CI compares each import with the table in architecture 3. That table allows `search` more modules than it uses, so code review checks the shorter list of design section 2 and choice 2. |
| `search` writes its output once, after the last file, keeps no state, and builds the matching forms of the catalog's names once per run. | No interface shows when the text reaches the stream or how often a form is built. Every case that expects exit code 1 or 2 checks that the output stream is empty, F10-T14 checks how often each file is read, F10-T01 runs `run` several times on one folder, and F10-T21 times the whole command. Code review checks the rest. |
| `run` with `Arguments` outside the constraints of 2.1: no value, an option, or a value that starts with `--`. | `cli` never passes them (F05 design 2.10). F10-T15 checks that `cli` rejects each such command line. |
| A recipe file named after a Windows device, and a listing or a file that the system refuses to read. | Windows refuses to create the first, and F04-T12 checks it on Linux only. The readers turn the second into problems, which F04-T36 and F07-T13 test. F10-T13 checks that the first error of each reader stops `search`, whatever the error. |
| A word with a line break or an invisible character in the command line of a new process. | Each system's rules for the command line of a new process decide how such a word arrives, and `main` gets the word as it arrives. F10-T07, F10-T10, and F10-T11 pass such words to `main`. |
| A search that also matches IDs. | The design does not make the ID a place, and the Architect's note in design section 4 says that a fourth place needs the requirement change flow. F10-T06 and F10-T17 check that an ID does not count. |
| Ctrl+C during `search`. | `cli` gives exit code 130 for every command (F05 design 2.10), and F05-T41 tests it. `search` writes no file, so Ctrl+C leaves nothing behind. |
| `Message.render` parsing its placeholders on every call, and the `[refactor]` PR of choice 10. | An internal change to `text` that the Architect decides on. F10-T21 times `search`, which would show the change. |
| The help with the eight commands of v0.1. | F05-T45 checks those lines with the stand-ins, and v0.1-S19 checks them with the real commands. F10-T01 checks the line of `search` in a form that holds as F11 to F13 add their commands. |
| Chinese output in Windows Terminal. | No CI machine has a Windows console (architecture 10), so v0.1-S25 has Troy check it. F10-T19 checks that `python -m recipe_menu` writes the Chinese output as UTF-8. |
| Doc comments are in English only. | R05. troy-check rejects Chinese characters in doc comments. |
| v0.1-S11, v0.1-S23, and v0.1-S30 in the release test. | They are version tests in `version-tests/`, which the version tests PR adds (TE5). F10-T04 and F10-T16 run the same steps at `main`, and F10-T21 times the same command on the same kind of folder, in every test run. |

## 5. Alignment with the Interface Designer

None.

## 6. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-13 | First draft. |
| 1.0 | 2026-11-14 | Approved by Troy. |
