---
troy-doc: "F03-design"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "design.zh-CN.md"
---

# F03 Catalog and pantry: interface design

## 1. Feature

- ID and name: F03 Catalog and pantry
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: F01, F02

## 2. Interfaces

F03 creates the base module `datafile` and builds the domain module `catalog` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.datafile` exports `DataFolder`, `Problem`, `Severity`, `read_toml`, and the messages for the shape of a file (2.10): `EMPTY_ITEM`, `EMPTY_TEXT`, `ITEM_NOT_A_TEXT`, `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TABLE`, `NOT_A_TEXT`, and `UNKNOWN_KEY`. `recipe_menu.catalog` exports `Catalog`, `Category`, `Ingredient`, `Pantry`, `Tag`, `read_catalog`, and `read_pantry`. Each module's `__init__.py` lists its names in `__all__`. Each module keeps its messages in its `messages.py` (architecture 8). The other files behind each module are the Developer's choice. The files are those of `docs/prototypes/example-data.md`, and the F07 prototype shows how `check` reports their problems.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F03 gives |
| --- | --- |
| It reads the catalog: the shopping categories in order, the ingredients with their Chinese and English names, category, and default unit, and the tags with their Chinese and English names. | `read_catalog` (2.8). It gives a `Catalog` (2.5) of `Category`, `Ingredient`, and `Tag` values (2.4), in the file's order. |
| It finds an ingredient or a tag by its name in either language. | `Catalog.find_ingredient` and `Catalog.find_tag`, with the matching rules of 2.6. |
| It reads the pantry list. | `read_pantry` (2.9). It gives a `Pantry` (2.7). |
| It reports duplicate names, unknown categories, unknown units, and unknown pantry ingredients. | The `Problem` values (2.2) that `read_catalog` and `read_pantry` return, each with its file and its place. |
| `datafile` holds the paths of the data folder's files, reading a TOML file, and problems with their places (architecture 3). | `DataFolder` (2.1), `Severity` and `Problem` (2.2), `read_toml` (2.3), and the messages for the shape of a file (2.10). |

These rules hold for every interface below:

- `datafile` imports only `lang` and `text` from the package. `catalog` imports only `lang`, `units`, `text`, and `datafile` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- `read_toml` is the only interface that opens a file, and `read_catalog` and `read_pantry` read their files through it. No interface writes a file, prints, reads the environment, or keeps state.
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). It skips the broken part, records a `Problem`, and goes on, so one `check` run lists every problem. The exceptions in the Errors tables below come from wrong calls, which are bugs.
- Every value is a frozen dataclass with `slots=True` or an enum, and its collections are tuples or frozensets (architecture 8). The one exception is the table that `read_toml` gives. It is what `tomllib` gives, and it goes only to the reader that asked for it, which turns it into values. A raw TOML table never goes further (architecture 5).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F03 interface has a performance target. `check`, `show`, and `shop` read a catalog of 300 ingredients within PT01's 1 second. So `read_catalog` and `read_pantry` take time in proportion to the size of their file. Each lookup by name takes time in proportion to the length of the name, whatever the size of the catalog.

These later features are meant to call them:

- F04 reads each recipe file with `read_toml`, and reports a wrong shape with the messages of 2.10. It finds a recipe's ingredients and tags with `find_ingredient` and `find_tag`, and reports each problem as a `Problem`.
- F05 reads the settings with `read_toml`, and reports a wrong shape with the messages of 2.10. `cli` builds the `DataFolder`.
- F06 reads a week menu from `DataFolder.menu_file` with `read_toml`, and reports a wrong shape with the messages of 2.10.
- F07 calls `read_catalog`, and then `read_pantry` with that catalog, or with `None` when the catalog could not be read. It prints each problem's file, place, and text.
- F08, F11, and F13 add to `datafile` the writes that they need (architecture 3). F08 shows the number of categories, ingredients, and tags, and of the pantry's ingredients.
- F09 finds the tag of `list --tag` with `find_tag`.
- F12 orders the shopping list by `Catalog.categories` and `Catalog.ingredients`, and leaves out `Pantry.ingredients`.
- F13 saves the list at `DataFolder.shopping_file`. The English pantry line of the F13 prototype writes "cooking oil" and "Sichuan pepper", where the catalog writes "Cooking oil" and "Sichuan pepper". No rule turns the catalog's names into that line, and the catalog keeps each name as written, so F13's design must settle the line.
- F15 checks each ingredient that you type with `find_ingredient`.

### 2.1 `DataFolder`

- Module: datafile
- Purpose: The data folder and the path of each file in it ([architecture 5.1](../../architecture.md#51-data-files)). It is the only place that knows the file names (architecture 5.2). `cli` builds it from `--data`, `RECIPE_MENU_DATA`, or `~/recipe-menu` (F05), and passes it on in `Context`.

Signature:

```python
@dataclass(frozen=True, slots=True)
class DataFolder:
    root: Path

    @property
    def settings(self) -> Path: ...

    @property
    def catalog(self) -> Path: ...

    @property
    def pantry(self) -> Path: ...

    @property
    def recipes(self) -> Path: ...

    @property
    def menus(self) -> Path: ...

    @property
    def shopping(self) -> Path: ...

    def recipe_file(self, recipe_id: str) -> Path: ...

    def menu_file(self, week: str) -> Path: ...

    def shopping_file(self, week: str) -> Path: ...

    def relative(self, path: Path) -> Path: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `root` | `Path` | The data folder, such as `C:\Users\Troy\recipe-menu`. | None. `DataFolder` does not check that the folder exists. |
| `recipe_id` | `str` | A recipe ID, such as `tomato-egg`. | An ID that F04's rules accept. `recipe_file` checks only the rule in Errors. |
| `week` | `str` | An ISO week as a file name writes it, such as `2026-W47`. | A week that F06 wrote. `menu_file` and `shopping_file` check only the rule in Errors. |
| `path` | `Path` | A path inside `root`, such as `folder.catalog`. | Inside `root`. |

- Return value: Each property and each method gives a `Path`, by this table. It builds the path from `root` and looks at nothing on the disk.

| Interface | Path |
| --- | --- |
| `settings` | `root / "settings.toml"` |
| `catalog` | `root / "catalog.toml"` |
| `pantry` | `root / "pantry.toml"` |
| `recipes` | `root / "recipes"` |
| `menus` | `root / "menus"` |
| `shopping` | `root / "shopping"` |
| `recipe_file(recipe_id)` | `root / "recipes" / f"{recipe_id}.toml"` |
| `menu_file(week)` | `root / "menus" / f"{week}.toml"` |
| `shopping_file(week)` | `root / "shopping" / f"{week}.md"` |
| `relative(path)` | `path.relative_to(root)`, such as `Path("recipes", "mapo-tofu.toml")`. A `Problem` names its file with it (architecture 5.3). |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `recipe_file`, `menu_file`, or `shopping_file` gets a name that is empty, that is `.` or `..`, or that holds `/`, `\`, `:`, or the null character U+0000. Such a name could give the path of another file. `../catalog` gives the catalog. On Windows, `pathlib` reads `C:catalog.toml` as the file `catalog.toml` on drive C. With the data folder on drive C, `recipe_file("C:catalog")` gives `catalog.toml` in `recipes`. With the data folder on another drive, it gives `catalog.toml` in the current folder of drive C, outside the data folder. The rule is the same on Windows and Linux. |
| `ValueError` | `relative` gets a path that is not inside `root`. |

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import DataFolder

folder = DataFolder(Path("C:/Users/Troy/recipe-menu"))
assert folder.catalog == folder.root / "catalog.toml"
assert folder.recipes == folder.root / "recipes"
assert folder.recipe_file("tomato-egg") == folder.recipes / "tomato-egg.toml"
assert folder.menu_file("2026-W47") == folder.root / "menus" / "2026-W47.toml"
assert folder.shopping_file("2026-W47") == folder.shopping / "2026-W47.md"
assert folder.relative(folder.recipe_file("mapo-tofu")) == Path("recipes", "mapo-tofu.toml")
folder.recipe_file("../catalog")  # raises ValueError
folder.recipe_file("C:catalog")  # raises ValueError
folder.relative(Path("D:/other/catalog.toml"))  # raises ValueError
```

### 2.2 `Severity` and `Problem`

- Module: datafile
- Purpose: A problem in a data file, with its severity, its file, its place, and its message with the message's values ([architecture 5.2](../../architecture.md#52-values)). Readers return problems and never raise them. `Severity` says whether a problem is an error, which makes a command exit with 1, or a warning, which never changes the exit code (architecture 6).

Signature:

```python
class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Problem:
    severity: Severity
    file: Path
    place: BiText | None
    message: Message
    values: tuple[tuple[str, MessageValue], ...] = ()

    @classmethod
    def error(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem: ...

    @classmethod
    def warning(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem: ...

    def text(self, lang: Lang) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `severity` | `Severity` | An error or a warning. | None |
| `file` | `Path` | The file, relative to the data folder, from `DataFolder.relative`. | Not an absolute path. |
| `place` | `BiText` or `None` | The place in the file, in both languages, such as "line 2" and "第 2 行", or "ingredient 3" and "食材 3". | `None` for a problem of the whole file, which has no line or field, such as a missing file or an unknown key at the top of a file. |
| `message` | `Message` | What is wrong, and what to do about it. | None |
| `values` | A tuple of (name, `MessageValue`) pairs | The value of each placeholder of `message`. | One pair for each placeholder, and no others. `Problem` sorts the pairs by name, so their order does not matter. |
| `values` of `error` and `warning` | `MessageValue` keyword arguments | The same values, by name. | As for the field `values`. |
| `lang` | `Lang` | The language that `text` writes. | None |

- Return value: A `Problem`.
  - `Problem.error(file, place, message, **values)` gives a problem with `Severity.ERROR`, and `Problem.warning` gives one with `Severity.WARNING`. Their first three parameters are positional only, so a message can also have a placeholder named `file`, `place`, or `message`.
  - `text(lang)` gives `message.render(lang, **values)`. F07 can show `place.get(lang)` after the file, and `text(lang)` below them.
  - `str(problem.file)` writes the path with the system's separator, such as `recipes\mapo-tofu.toml` on Windows (architecture 6).
  - Two problems are equal when all five fields are equal, and a `Problem` is hashable.

Errors:

Creating a `Problem` renders its message once in both languages, so wrong values fail at once.

| Error | When |
| --- | --- |
| `ValueError` | `file` is an absolute path. |
| `ValueError` | The names in `values` are not exactly the placeholders of `message`, or a name appears twice in `values`. |
| `TypeError` | A value is not a `str`, an `int`, or a `BiText`, or it is a `bool` or an `enum.Enum` member, which `Message.render` rejects (F02 design 2.3). |
| `ValueError` | An `int` value has more than 4,300 digits (F02 design 2.3). |

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import Problem, Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN_TAG = Message('Unknown tag "{tag}".', "未知标签“{tag}”。")
NO_ENGLISH_STEPS = Message("No English steps.", "没有英文步骤。")
rice = Path("recipes", "rice.toml")
tags = BiText("tags", "标签")

problem = Problem.error(rice, tags, UNKNOWN_TAG, tag="breakfast")
assert problem.severity is Severity.ERROR
assert problem.values == (("tag", "breakfast"),)
assert problem.text(Lang.EN) == 'Unknown tag "breakfast".'
assert problem.text(Lang.ZH) == "未知标签“breakfast”。"
assert problem == Problem(Severity.ERROR, rice, tags, UNKNOWN_TAG, (("tag", "breakfast"),))

warning = Problem.warning(rice, BiText("steps", "步骤"), NO_ENGLISH_STEPS)
assert warning.severity is Severity.WARNING
assert warning.values == ()

Problem.error(rice, tags, UNKNOWN_TAG)  # raises ValueError
Problem.error(Path.cwd() / "rice.toml", None, NO_ENGLISH_STEPS)  # raises ValueError
Problem.error(rice, tags, UNKNOWN_TAG, tag=None)  # raises TypeError
```

### 2.3 `read_toml`

- Module: datafile
- Purpose: Reads one data file as TOML 1.0 (ADR-0002). It gives the file's table, or one `Problem` that says why the file cannot be read. The readers of F03 to F06 read every file with it, so every syntax mistake gets the same messages.

Signature:

```python
def read_toml(folder: DataFolder, path: Path) -> dict[str, object] | Problem: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `path` | `Path` | The file to read, such as `folder.catalog`. | Inside `folder.root`. |

- Return value: The file's table as a `dict[str, object]`, or a `Problem` with `Severity.ERROR` and the file `folder.relative(path)`. The caller turns the table into values and never passes the table on (architecture 5).

`read_toml` works in these steps:

1. It reads the bytes of the file. When that fails with an `OSError`, the problem has no place. Its message comes from the first row of this table that applies:

   | Condition | Message |
   | --- | --- |
   | `path.is_dir()` is true. On Windows, reading a folder fails with `PermissionError`, so `read_toml` checks this row before the others. | `FILE_IS_FOLDER` |
   | The error is a `FileNotFoundError`, or a `NotADirectoryError` because a folder in the path is a file. | `FILE_MISSING` |
   | The error is a `PermissionError`. | `ACCESS_DENIED` |
   | Any other `OSError`. | `SYSTEM_ERROR`. Its value `reason` is the error's `strerror`, or the name of the error's class, such as `OSError`, when `strerror` is `None` or empty. |

2. It decodes all the bytes at once with `bytes.decode`, the `utf-8-sig` codec, and strict errors (architecture 8). The codec reads a file with or without a byte order mark. A `UnicodeDecodeError` gives `NOT_UTF8` at the line of the first byte that is not UTF-8. That line is one more than the number of LF bytes in `error.object[:error.start]`. When the file starts with a byte order mark, `error.object` holds the bytes after the mark, and `error.start` counts from there. So the bytes `EF BB BF 61 0A FF`, which are a byte order mark, `a`, a line break, and the byte FF, give line 2. Counting in the bytes of the file up to `error.start` would give line 1.
3. It parses the text with `tomllib.loads`. A `tomllib.TOMLDecodeError` gives a problem at the line where the parser stopped, with the message for the parser's reason in the table below. Two more exceptions come from files that TOML 1.0 or the parser rejects:
   - A decimal integer of more than 4,300 digits raises a plain `ValueError`, because Python does not turn such a string into an `int` (`sys.get_int_max_str_digits()`). TOML 1.0 asks a parser to reject an integer that does not fit in 64 bits, so such a number is a mistake in the file. `read_toml` gives `NUMBER_TOO_LONG`.
   - Lists or tables nested hundreds deep raise `RecursionError`. So does a key of more than 1,000 dotted parts, where Python limits key parts: Python 3.13.18 and 3.14.10 do, and 3.14.3 parses such a key. `read_toml` gives `NESTED_TOO_DEEPLY`. Only nesting raises this exception in every version, so a test of `NESTED_TOO_DEEPLY` uses nesting.

   Architecture 6 names `TOMLDecodeError` and `UnicodeDecodeError` for a syntax mistake. These two exceptions are mistakes of the same kind, so `read_toml` catches them at the same place, and no data file causes a traceback. The `except` clauses name `tomllib.TOMLDecodeError`, then `ValueError`, then `RecursionError`. `TOMLDecodeError` is a subclass of `ValueError`, so its clause comes first.

`read_toml` finds the reason and the line of a `TOMLDecodeError` this way (ADR-0002):

- The reason is the error's text without the ending ` (at line N, column M)` or ` (at end of document)` that `tomllib` adds. On Python 3.14, the reason equals the error's `msg` attribute.
- The line is the error's `lineno` attribute where Python has one (3.14). On Python 3.13, the line is the N of the ending ` (at line N, column M)`. When the ending is ` (at end of document)`, the line is one more than the number of line breaks in the text, which is what `lineno` gives there on Python 3.14.
- When the error has neither a `lineno` nor such an ending, the problem has no place. Only a `TOMLDecodeError` that `tomllib` did not raise can lack both.

A `ValueError` or a `RecursionError` carries no position, so `read_toml` finds its line itself. The line is the first line N for which parsing only lines 1 to N, each with its line break, raises the same kind of exception: a `ValueError` that is not a `TOMLDecodeError`, or a `RecursionError`. For a number of too many digits, that is the line of the number, because the parser reads the text in order, and a text that ends before the number never reaches it. A binary search finds N with about log2 of the number of lines more parses. Only a file with such a mistake pays for them.

`read_toml` knows the reasons in this table. Python 3.13 and 3.14 give the same reasons, as their `tomllib` sources show (checked in Python 3.13.18 and 3.14.10). Every other reason, and any reason that a later Python adds, gives `NOT_TOML`. The last column gives a mistake that causes each reason.

| Reason from `tomllib` | Message | A mistake that causes it |
| --- | --- | --- |
| `Unclosed array`, `Expected ']' at the end of a table declaration`, and `Expected ']]' at the end of an array declaration` | `MISSING_BRACKET` | `pantry = ["盐" "糖"]`, with no comma between two items, as in the F07 prototype "A syntax mistake". `[monday` with no `]`. |
| `Unclosed inline table` | `MISSING_BRACE` | `{ zh = "番茄" en = "Tomato" }`, with no comma between two keys. A table in braces whose line ends before its `}`. |
| `Unterminated string`, `Illegal character '\n'`, `Found invalid character '\n'`, `Expected "'"`, and `Expected "'''"` | `MISSING_QUOTE` | `zh = "番茄` with no closing `"`. In the two reasons with `'\n'`, the `\n` is the two characters `\` and `n`, as `repr` writes a line break. |
| `Invalid value` | `BAD_VALUE` | `zh = 番茄` with no quotation marks, `zh = “番茄”` with Chinese quotation marks, or `zh =` with no value. |
| `Expected '=' after a key in a key/value pair` | `MISSING_EQUALS` | `zh "番茄"` or `zh: "番茄"`. |
| `Invalid initial character for a key part` | `BAD_KEY` | `{ zh = "番茄", }`, which ends with a comma. A table in braces that goes on to the next line after a comma. `{ 中文 = "番茄" }`. |
| `Expected newline or end of document after a statement` | `EXTRA_TEXT` | `servings = 2 份`, or two keys on one line. |
| `Invalid statement` | `BAD_LINE` | A line that starts with `番茄` or with `“`. |
| `Cannot overwrite a value`, and the reasons that start with `Cannot declare `, `Duplicate inline table key `, `Cannot mutate immutable namespace `, or `Cannot redefine namespace ` | `DEFINED_TWICE` | `servings = 2` twice, `[monday]` twice, or `{ zh = "葱", zh = "大葱" }`. |
| `Unescaped '\' in a string`, `Invalid hex value`, and `Escaped character is not a Unicode scalar value` | `BAD_ESCAPE` | `editor = "C:\Program Files\notepad.exe"`, where `\P` is no escape. `"C:\users"` gives `Invalid hex value`, because `\u` starts an escape. |
| The other reasons that start with `Illegal character ` or `Found invalid character ` | `CONTROL_CHARACTER` | A text or a comment that holds a control character, such as U+0000 or a U+000D that no U+000A follows. |
| Any other reason, such as `Invalid date or datetime` | `NOT_TOML` | `day = 2026-11-31`. |

The messages of `datafile` are these. `LINE` is the place of every problem that has a line. In the templates of `MISSING_BRACE`, the brace `}` is written twice (F02 design 2.2).

| Name | English | Chinese |
| --- | --- | --- |
| `LINE` | `line {line}` | `第 {line} 行` |
| `FILE_MISSING` | `The file is missing.` | `文件不存在。` |
| `FILE_IS_FOLDER` | `The file cannot be read: it is a folder.` | `无法读取文件：它是一个文件夹。` |
| `ACCESS_DENIED` | `The file cannot be read: access is denied.` | `无法读取文件：没有访问权限。` |
| `SYSTEM_ERROR` | `The file cannot be read. The system says: {reason}` | `无法读取文件。系统提示：{reason}` |
| `NOT_UTF8` | `The file cannot be read: it is not UTF-8 text. Save it as UTF-8.` | `无法读取文件：它不是 UTF-8 文本。请把它另存为 UTF-8。` |
| `MISSING_BRACKET` | `The file cannot be read: a closing "]" is missing.` | `无法读取文件：缺少右方括号“]”。` |
| `MISSING_BRACE` | `The file cannot be read: a closing "}" is missing. A table in braces must be on one line.` | `无法读取文件：缺少右花括号“}”。花括号里的表必须写在一行里。` |
| `MISSING_QUOTE` | `The file cannot be read: a closing quotation mark is missing.` | `无法读取文件：缺少结尾的引号。` |
| `BAD_VALUE` | `The file cannot be read: a value is missing or not valid. Write a text in straight quotation marks, such as "Tomato".` | `无法读取文件：缺少值，或者值写得不对。文字要放在英文双引号里，比如 "番茄"。` |
| `MISSING_EQUALS` | `The file cannot be read: an "=" is missing after a key.` | `无法读取文件：键后面缺少“=”。` |
| `BAD_KEY` | `The file cannot be read: a key is missing or not valid. A table in braces must be on one line, and it cannot end with a comma.` | `无法读取文件：缺少键，或者键写得不对。花括号里的表必须写在一行里，而且不能以逗号结尾。` |
| `EXTRA_TEXT` | `The file cannot be read: something follows the value on this line. Write one key and its value on each line.` | `无法读取文件：这一行的值后面还有别的内容。每行只写一个键和它的值。` |
| `BAD_LINE` | `The file cannot be read: this line does not start with a key, "[", or "#".` | `无法读取文件：这一行的开头不是键、“[”或“#”。` |
| `DEFINED_TWICE` | `The file cannot be read: a key or a table is defined twice.` | `无法读取文件：同一个键或表定义了两次。` |
| `BAD_ESCAPE` | `The file cannot be read: a "\" in a text does not start a valid escape. Write "\\" for one "\", or put the text in single quotation marks.` | `无法读取文件：文字里的“\”没有构成有效的转义。一个“\”要写成“\\”，或者把文字放在单引号里。` |
| `CONTROL_CHARACTER` | `The file cannot be read: this line holds a control character, which TOML does not allow.` | `无法读取文件：这一行有 TOML 不允许的控制字符。` |
| `NOT_TOML` | `The file cannot be read: this line is not valid TOML.` | `无法读取文件：这一行不是有效的 TOML。` |
| `NUMBER_TOO_LONG` | `The file cannot be read: a number has too many digits.` | `无法读取文件：有一个数字的位数太多。` |
| `NESTED_TOO_DEEPLY` | `The file cannot be read: lists or tables are nested too deeply.` | `无法读取文件：列表或表嵌套得太深。` |

The English text of `MISSING_BRACKET` is the line of the F07 prototype "A syntax mistake".

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `path` is not inside `folder.root`, as `DataFolder.relative` finds. `read_toml` checks this before it reads. |

- Side effects: Reads the file at `path`. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10).

```python
from pathlib import Path

from recipe_menu.datafile import Problem, read_toml
from recipe_menu.lang import BiText, Lang

assert read_toml(folder, folder.pantry) == {"pantry": ["食用油", "盐", "糖", "生抽", "花椒"]}

folder.pantry.write_text('# The pantry.\npantry = ["食用油", "盐" "糖"]\n', encoding="utf-8")
problem = read_toml(folder, folder.pantry)
assert isinstance(problem, Problem)
assert problem.file == Path("pantry.toml")
assert problem.place == BiText("line 2", "第 2 行")
assert problem.text(Lang.EN) == 'The file cannot be read: a closing "]" is missing.'
assert problem.text(Lang.ZH) == "无法读取文件：缺少右方括号“]”。"

folder.settings.unlink()
missing = read_toml(folder, folder.settings)
assert isinstance(missing, Problem)
assert missing.place is None
assert missing.text(Lang.EN) == "The file is missing."

digits = "servings = " + "1" * 5000 + "\n"
folder.settings.write_text('language = "en"\n' + digits, encoding="utf-8")
too_long = read_toml(folder, folder.settings)
assert isinstance(too_long, Problem)
assert too_long.place == BiText("line 2", "第 2 行")
assert too_long.text(Lang.EN) == "The file cannot be read: a number has too many digits."

folder.catalog.write_bytes(b"tags = []\n# caf\xe9\n")
not_utf8 = read_toml(folder, folder.catalog)
assert isinstance(not_utf8, Problem)
assert not_utf8.place == BiText("line 2", "第 2 行")

folder.catalog.write_bytes(b"\xef\xbb\xbftags = []\n\xff\n")
with_mark = read_toml(folder, folder.catalog)
assert isinstance(with_mark, Problem)
assert with_mark.place == BiText("line 2", "第 2 行")

read_toml(folder, Path("D:/other/catalog.toml"))  # raises ValueError
```

### 2.4 `Category`, `Ingredient`, and `Tag`

- Module: catalog
- Purpose: The parts of the catalog ([architecture 5.2](../../architecture.md#52-values)). A `Category` is a shopping category, and the catalog's order of categories is the shopping order. An `Ingredient` has its names in both languages, its category, and its default unit. A `Tag` has its names in both languages. Recipes and the pantry refer to the same `Ingredient` values, so the shopping list merges ingredients by identity.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Category:
    key: str
    name: BiText


@dataclass(frozen=True, slots=True)
class Ingredient:
    name: BiText
    category: Category
    unit: Unit | None = None


@dataclass(frozen=True, slots=True)
class Tag:
    name: BiText
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `key` | `str` | The category's key, which an ingredient's `category` names, such as `produce`. | Holds more than whitespace. |
| `name` of a `Category` | `BiText` | The category's names, such as "Vegetables and fruit" and "蔬菜水果". | Each language that is set holds more than whitespace. One language may be missing, because `read_catalog` keeps a category whose other name is wrong, so that its ingredients still find it (2.8). |
| `name` of an `Ingredient` or a `Tag` | `BiText` | The names in English and Chinese, such as "Scallion" and "葱". | Both languages are set, and each holds more than whitespace. |
| `category` | `Category` | The ingredient's shopping category. | One of the catalog's categories (2.5). |
| `unit` | `Unit` or `None` | The default unit of a quantity without a unit (F01 design 2.7). | `None` when the ingredient has no default unit. |

- Return value: A `Category`, an `Ingredient`, or a `Tag`. Two of them are equal when all their fields are equal, and each is hashable. A `Catalog` holds no two ingredients and no two tags with matching names (2.5), so two equal ingredients of one catalog are the same object.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `Category`: `key` is empty or holds only whitespace, or a language of `name` that is set is empty or holds only whitespace. |
| `ValueError` | `Ingredient` or `Tag`: a language of `name` is `None`, is empty, or holds only whitespace. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.catalog import Category, Ingredient, Tag
from recipe_menu.lang import BiText, Lang
from recipe_menu.units import Unit

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
scallion = Ingredient(BiText("Scallion", "葱"), produce, Unit.STALK)
assert scallion.category is produce
assert scallion.unit is Unit.STALK
assert Ingredient(BiText("Tomato", "番茄"), produce).unit is None
assert Category("other", BiText(zh="其他")).name.get(Lang.EN) == "其他"
assert Tag(BiText("quick", "快手")) == Tag(BiText("quick", "快手"))

Ingredient(BiText(zh="葱"), produce)  # raises ValueError
Tag(BiText("quick", " "))  # raises ValueError
Category(" ", BiText("Other", "其他"))  # raises ValueError
```

### 2.5 `Catalog`

- Module: catalog
- Purpose: The categories, the ingredients, and the tags, in the file's order ([architecture 5.2](../../architecture.md#52-values)). It finds an ingredient or a tag by its name in either language (2.6). Tests and F12 can build one in code, with no file.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Catalog:
    categories: tuple[Category, ...]
    ingredients: tuple[Ingredient, ...]
    tags: tuple[Tag, ...]

    # Methods: find_ingredient and find_tag (2.6).
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `categories` | A tuple of `Category` values | The categories, in shopping order. | No two keys match by the rules of 2.6. Two categories may share a name, because nothing finds a category by its name. `read_catalog` reports a shared name (2.8). |
| `ingredients` | A tuple of `Ingredient` values | The ingredients, in the catalog's order, which orders the lines of a category on the shopping list. | Each one's `category` is in `categories`. No two ingredients have matching names. |
| `tags` | A tuple of `Tag` values | The tags, in the file's order. | No two tags have matching names. |

- Return value: A `Catalog`. It builds an index of the names when it is created, so a lookup of 2.6 takes the same time whatever the size of the catalog. Two catalogs are equal when their three tuples are equal, and a `Catalog` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | The keys of two categories match by the rules of 2.6. |
| `ValueError` | The `category` of an ingredient is not in `categories`. |
| `ValueError` | Two ingredients have names that match by the rules of 2.6, or two tags do, in the same language or in different languages. The two names of one ingredient, or of one tag, may match each other. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.lang import BiText

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
meat = Category("meat", BiText("Meat and seafood", "肉类水产"))
tomato = Ingredient(BiText("Tomato", "番茄"), produce)
pork = Ingredient(BiText("Pork belly", "五花肉"), meat)
quick = Tag(BiText("quick", "快手"))
catalog = Catalog((produce, meat), (tomato, pork), (quick,))
assert catalog.categories == (produce, meat)
assert catalog.find_ingredient("五花肉") is pork
assert catalog == Catalog((produce, meat), (tomato, pork), (quick,))
greens = Category("greens", BiText("Vegetables and fruit", "青菜"))
assert Catalog((produce, greens), (), ()).categories == (produce, greens)

fruit = Category("Produce", BiText("Fruit", "水果"))
tomato_again = Ingredient(BiText("tomato", "西红柿"), produce)
Catalog((produce,), (tomato, pork), ())  # raises ValueError
Catalog((produce, fruit), (), ())  # raises ValueError
Catalog((produce, meat), (tomato, tomato_again), ())  # raises ValueError
```

### 2.6 `Catalog.find_ingredient` and `Catalog.find_tag`

- Module: catalog, methods of `Catalog` (2.5)
- Purpose: Find an ingredient or a tag by its name in either language. F04 finds the ingredients and the tags of a recipe with them, F09 finds the tag of `list --tag`, and `read_pantry` finds each item of the pantry.

Signature:

```python
def find_ingredient(self, name: str) -> Ingredient | None: ...


def find_tag(self, name: str) -> Tag | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `name` | `str` | A name as written, such as `葱`, `Scallion`, or ` scallion `. | Any string. |

- Return value: The ingredient or the tag that has a name, in either language, that matches `name` by the rules below, or `None` when no name matches. A catalog has no two matching names (2.5), so at most one item matches. Ingredients and tags are kept apart: `find_ingredient` never gives a tag, and `find_tag` never gives an ingredient.

Two texts match when their matching forms are equal. The matching form of a text is the text without whitespace at both ends, as `str.strip()` removes it, with each ASCII capital letter from A to Z changed to its small letter. `Catalog`, `read_catalog`, and `read_pantry` compare every name, every category key, and every name that the pantry gives in this way. These rules follow:

1. Whitespace at the ends does not count. `str.strip()` removes each character for which `str.isspace()` is true, such as the space, the tab, U+00A0 NO-BREAK SPACE, and U+3000 IDEOGRAPHIC SPACE. It keeps U+200B ZERO WIDTH SPACE and U+FEFF ZERO WIDTH NO-BREAK SPACE, which are not whitespace. So `葱\u200B` does not match `葱`.
2. Whitespace inside a text counts as written. `Choy  sum`, with two spaces, does not match `Choy sum`.
3. Case counts only for the letters A to Z, in a text of either language. `SCALLION` matches `Scallion`, and `jalapeño` matches `Jalapeño`. `JALAPEÑO` does not match it, because `Ñ` is not a letter from A to Z.
4. Look-alike letters stay as they are. `\u212Aale`, with U+212A KELVIN SIGN, does not match `Kale`, although `str.lower()` turns U+212A into `k`. `\u017Fcallion`, with U+017F LATIN SMALL LETTER LONG S, does not match `Scallion`, although `str.casefold()` turns U+017F into `s`. A fullwidth letter, such as U+FF33 FULLWIDTH LATIN CAPITAL LETTER S, does not match its ASCII letter. So the code uses neither `str.lower()` nor `str.casefold()`.
5. No text is normalized. `e` followed by U+0301 COMBINING ACUTE ACCENT does not match U+00E9, the single character `é`.
6. Chinese characters compare exactly. `番茄` and `西红柿` are two names.
7. A text whose matching form is empty, such as `""` or `"\u3000"`, matches nothing.

F01's `parse_unit` matches English spellings in any case (F01 design 2.3 and 2.6). Its code changes the case of a text only when the whole text is ASCII (`_fold` in `src/recipe_menu/units/_ops.py`). On unit spellings the two rules agree, because every English spelling of a unit is ASCII, and no spelling mixes ASCII letters with other characters. F03 also changes A to Z in a name that holds other characters, so that `jalapeño` matches `Jalapeño`.

Errors: None. Neither method raises.

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.catalog import Catalog, Category, Ingredient, Tag
from recipe_menu.lang import BiText

produce = Category("produce", BiText("Vegetables and fruit", "蔬菜水果"))
kale = Ingredient(BiText("Kale", "羽衣甘蓝"), produce)
scallion = Ingredient(BiText("Scallion", "葱"), produce)
quick = Tag(BiText("quick", "快手"))
catalog = Catalog((produce,), (kale, scallion), (quick,))
assert catalog.find_ingredient("葱") is scallion
assert catalog.find_ingredient(" SCALLION\t") is scallion
assert catalog.find_ingredient("\u3000葱") is scallion  # U+3000 IDEOGRAPHIC SPACE
assert catalog.find_ingredient("kale") is kale
assert catalog.find_ingredient("\u212aale") is None  # U+212A KELVIN SIGN
assert catalog.find_ingredient("\u017fcallion") is None  # U+017F LATIN SMALL LETTER LONG S
assert catalog.find_ingredient("葱\u200b") is None  # U+200B ZERO WIDTH SPACE
assert catalog.find_ingredient("Scal lion") is None
assert catalog.find_ingredient("") is None
assert catalog.find_tag("QUICK") is quick
assert catalog.find_tag("葱") is None
```

### 2.7 `Pantry`

- Module: catalog
- Purpose: The ingredients that you always have at home ([architecture 5.2](../../architecture.md#52-values)). The shopping list leaves them out, and names the ones that the menu uses in one line at the end ([requirements 3](../../requirements.md#3-how-users-interact-with-it), shopping list rule 6).

Signature:

```python
@dataclass(frozen=True, slots=True)
class Pantry:
    ingredients: frozenset[Ingredient]
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `ingredients` | A frozenset of `Ingredient` values | The pantry's ingredients. | Ingredients of the catalog that `read_pantry` got. |

- Return value: A `Pantry`. Two pantries are equal when their sets are equal, and a `Pantry` is hashable. The set has no order, so F12 gives the pantry line its order, such as the catalog's order.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.catalog import Category, Ingredient, Pantry
from recipe_menu.lang import BiText

seasonings = Category("seasonings", BiText("Seasonings", "调味品"))
salt = Ingredient(BiText("Salt", "盐"), seasonings)
sugar = Ingredient(BiText("Sugar", "糖"), seasonings)
pantry = Pantry(frozenset({salt}))
assert salt in pantry.ingredients
assert sugar not in pantry.ingredients
assert pantry == Pantry(frozenset({salt}))
```

### 2.8 `read_catalog`

- Module: catalog
- Purpose: Reads `catalog.toml` into a `Catalog`, and reports each problem with its place ([requirements 4](../../requirements.md#4-features), F03). `check` shows every problem (F07). Every other command stops at the first error (architecture 6).

Signature:

```python
def read_catalog(folder: DataFolder) -> tuple[Catalog | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: A pair `(catalog, problems)`.
  - `catalog` is `None` when `read_toml` gives a problem: the file is missing, cannot be read, is not UTF-8, or is not valid TOML. Then `problems` holds only that problem.
  - Otherwise `catalog` is a `Catalog` of every category, ingredient, and tag that no check below skips, in the file's order, even when `problems` is not empty. Each name and each key is stored without whitespace at both ends. The `category` of each ingredient is the same `Category` object as the one in `catalog.categories`.
  - `problems` is a tuple of `Problem` values, each with `Severity.ERROR` and the file `catalog.toml`. F03 gives no warnings.

The file has the layout of `docs/prototypes/example-data.md`:

```toml
categories = [
  { key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" },
]

ingredients = [
  { zh = "葱", en = "Scallion", category = "produce", unit = "根" },
]

tags = [
  { zh = "快手", en = "quick" },
]
```

The places of the catalog's problems are these. N counts the items of a list from 1, skipped items included, so it is the number that you count in the file. Each table of TOML's `[[ingredients]]` form is an item of the list too.

| Place | English | Chinese |
| --- | --- | --- |
| The list `categories`, `ingredients`, or `tags` | `categories`, `ingredients`, or `tags` | `分类`, `食材`, or `标签` |
| Item N of `categories` | `category N` | `分类 N` |
| Item N of `ingredients` | `ingredient N` | `食材 N` |
| Item N of `tags` | `tag N` | `标签 N` |

`read_catalog` reads `categories`, then `ingredients`, then `tags`, and then the other keys at the top of the file. It reads the items of each list in order. For each item, it checks each field and each unknown key, and reports each problem. When none of these checks skips the item, it then checks the item for duplicates. It keeps the item when no check skips it. The problems come in the same order: the problems of a list itself, then those of each item. An item's problems come field by field, in the order of its keys below, then for its unknown keys in the file's order, and then for its duplicates: the key of a category first, and then the Chinese name and the English name.

Each kind of item has these keys, in this order:

| Kind | Keys | Required texts |
| --- | --- | --- |
| A category | `key`, `zh`, and `en` | All three |
| An ingredient | `zh`, `en`, `category`, and `unit` | `zh`, `en`, and `category` |
| A tag | `zh` and `en` | Both |
| The top of the file | `categories`, `ingredients`, and `tags` | None. They are lists. |

A required text has a problem in these cases:

| Case | Problem |
| --- | --- |
| The key is missing. | `MISSING_KEY` |
| The value is not a text, such as `3`, `true`, or a list. | `NOT_A_TEXT` |
| The text is empty or holds only whitespace: `str.strip()` gives `""`. | `EMPTY_TEXT` |

`read_catalog` makes these checks. The last column says what each check does to the item. An item that one check keeps is still skipped when another check skips it.

| Part | Check | Problem and place | What `read_catalog` does |
| --- | --- | --- | --- |
| `categories`, `ingredients`, or `tags` | The key is missing. | `MISSING_KEY`, with no place | It reads the list as empty. |
| `categories`, `ingredients`, or `tags` | The value is not a list. | `NOT_A_LIST`, at the list | It reads the list as empty. |
| Any item | The item is not a table. | `NOT_A_TABLE`, at the item | It skips the item. |
| Any item | The item has a key that its kind does not have. | `UNKNOWN_KEY`, at the item | It ignores the key. |
| A category | `key`, `zh`, or `en` has a problem as a required text. | That problem, at the category | It skips the category when `key` has a problem, or when both `zh` and `en` have one. Otherwise it keeps the category with its usable name. |
| A category | Its key matches the key of a category that it kept before. | `DUPLICATE_KEY`, at the category | It skips the category. |
| A category | Its Chinese name, then its English name, matches a name, in either language, of a category that it kept before. | `DUPLICATE_ZH_NAME` or `DUPLICATE_EN_NAME`, at the category | It keeps the category, so that its ingredients still find it. |
| An ingredient | `zh`, `en`, or `category` has a problem as a required text. | That problem, at the ingredient | It skips the ingredient. |
| An ingredient | `category` matches the key of no category that it kept. | `UNKNOWN_CATEGORY`, or `NO_CATEGORIES` when it kept no category, at the ingredient | It skips the ingredient. |
| An ingredient | `unit` is there, but it is not a text. | `NOT_A_TEXT`, at the ingredient | It keeps the ingredient with no default unit. |
| An ingredient | `unit` is a text that `parse_unit` does not know (F01 design 2.6), such as `cups` or `适量`. | `UNKNOWN_UNIT`, at the ingredient | It keeps the ingredient with no default unit. |
| An ingredient | `unit` is missing, is empty, or holds only whitespace. | None | The ingredient has no default unit. |
| An ingredient | Its Chinese name, then its English name, matches a name, in either language, of an ingredient that it kept before. | `DUPLICATE_ZH_NAME` or `DUPLICATE_EN_NAME`, at the ingredient | It skips the ingredient. |
| A tag | `zh` or `en` has a problem as a required text. | That problem, at the tag | It skips the tag. |
| A tag | Its Chinese name, then its English name, matches a name, in either language, of a tag that it kept before. | `DUPLICATE_ZH_NAME` or `DUPLICATE_EN_NAME`, at the tag | It skips the tag. |
| The top of the file | A key other than `categories`, `ingredients`, and `tags`. | `UNKNOWN_KEY`, with no place | It ignores the key. |

These rules apply to the duplicates:

- `read_catalog` checks an item for duplicates whenever no other check skips it. A check that keeps the item with a problem does not skip it: an unknown key, a `unit` that is not a text or that `parse_unit` does not know, and a wrong `zh` or `en` of a category that keeps its other name. So an ingredient with `unit = "cups"` whose Chinese name matches a name of an earlier ingredient gets `UNKNOWN_UNIT`, then `DUPLICATE_ZH_NAME`, and is skipped. A category with `en = ""`, a new Chinese name, and the key of an earlier category gets `EMPTY_TEXT`, then `DUPLICATE_KEY`, and is skipped.
- It compares the item only with the items of the same kind that it kept, so a skipped item holds no key and no name. It compares only the usable names of a category.
- Each name of an item, and the key of a category, can give a problem of its own. Each problem names the first earlier item that has that key or name.
- The two names of one item may match each other.
- Matching follows the rules of 2.6, so `rice` duplicates `Rice`.
- Two categories may not share a name, because the shopping list shows each category's name as a heading. A category whose name matches a name of an earlier category gets `DUPLICATE_ZH_NAME` or `DUPLICATE_EN_NAME`, but `read_catalog` keeps it. Ingredients name a category by its key, so the category's ingredients still find it, and `check` does not report each of them as an `UNKNOWN_CATEGORY` too. So `Catalog` does not compare the names of categories (2.5).

`read_catalog` reports the shape of the file with the messages of `datafile` (2.10): `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TABLE`, `NOT_A_TEXT`, `EMPTY_TEXT`, and `UNKNOWN_KEY`. It picks the form of `UNKNOWN_KEY` by the number of keys of the kind. These are the messages of `catalog`. A placeholder is a name in braces, such as `{category}`. `UNKNOWN_CATEGORY` is a `Plural` value (F02 design 2.4), picked by the number of categories that `read_catalog` kept.

| Name | English | Chinese |
| --- | --- | --- |
| `CATEGORIES`, `INGREDIENTS`, `TAGS`, `CATEGORY_N`, `INGREDIENT_N`, and `TAG_N` | The places in the table of places, with `{number}` for N. | The places in the table of places, with `{number}` for N. |
| `UNKNOWN_CATEGORY`, for one category | `Unknown category "{category}". The only category is {categories}.` | `未知分类“{category}”。现有分类：{categories}。` |
| `UNKNOWN_CATEGORY`, for more categories | `Unknown category "{category}". The categories are {categories}.` | `未知分类“{category}”。现有分类：{categories}。` |
| `NO_CATEGORIES` | `Unknown category "{category}". The catalog has no categories.` | `未知分类“{category}”。目录里没有分类。` |
| `UNKNOWN_UNIT` | `Unknown unit "{unit}".` | `未知单位“{unit}”。` |
| `DUPLICATE_KEY` | `The key "{key}" is also {other}'s key. Keys must be unique.` | `键“{key}”也是{other} 的键。键不能重复。` |
| `DUPLICATE_ZH_NAME` | `The Chinese name "{name}" is also {other}'s name. Names must be unique.` | `中文名称“{name}”也是{other} 的名称。名称不能重复。` |
| `DUPLICATE_EN_NAME` | `The English name "{name}" is also {other}'s name. Names must be unique.` | `英文名称“{name}”也是{other} 的名称。名称不能重复。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `key` | The key as the file writes it, such as `en`, `categories`, or an unknown key. In `DUPLICATE_KEY`, the category's key without whitespace at both ends. |
| `keys` | `and_list` of the keys of the kind, in the order of the table of keys, such as "zh, en, category, and unit" and "zh、en、category 和 unit". |
| `category` | The ingredient's `category` without whitespace at both ends. |
| `categories` | `and_list` of the keys of the categories that `read_catalog` kept, in order. The example catalog gives "produce, meat, eggs, staples, seasonings, and other", as in the F07 prototype. |
| `unit` | The ingredient's `unit` without whitespace at both ends. |
| `name` | The later item's name, without whitespace at both ends. |
| `other` | The place of the first earlier item that has the key or the name, such as "ingredient 3" and "食材 3". |
| `number` | N, the number of the item. |

The F07 prototype shows two of these problems. `catalog.toml, ingredient 12` gets `The English name "Rice" is also ingredient 4's name. Names must be unique.`, and `catalog.toml, ingredient 7` gets `Unknown category "meats". The categories are produce, meat, eggs, staples, seasonings, and other.`.

Errors: None. `read_catalog` never raises for bad data.

- Side effects: Reads `catalog.toml` through `read_toml`. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10). The second catalog has the mistakes of scenario v0.1-S07 in a shorter file, and two unknown units. Ingredient 5 also repeats the Chinese name of ingredient 4, so it gets two problems and is skipped.

```python
from recipe_menu.catalog import read_catalog
from recipe_menu.lang import BiText, Lang
from recipe_menu.units import Unit

catalog, problems = read_catalog(folder)
assert problems == ()
assert catalog is not None
assert [category.key for category in catalog.categories[:3]] == ["produce", "meat", "eggs"]
assert (len(catalog.categories), len(catalog.ingredients), len(catalog.tags)) == (6, 22, 5)
scallion = catalog.ingredients[3]
assert scallion.name == BiText("Scallion", "葱")
assert scallion.category is catalog.categories[0]
assert scallion.unit is Unit.STALK

lines = [
    'categories = [{ key = "produce", zh = "蔬菜水果", en = "Vegetables and fruit" }]',
    "ingredients = [",
    '  { zh = "西兰花", en = "Broccoli", category = "produce" },',
    '  { zh = "芥兰", en = "broccoli", category = "produce" },',
    '  { zh = "香菜", en = "Coriander", category = "meats" },',
    '  { zh = "葱", en = "Scallion", category = "produce", unit = "cups" },',
    '  { zh = "葱", en = "Green onion", category = "produce", unit = "cups" },',
    "]",
    "tags = []",
]
folder.catalog.write_text("\n".join(lines) + "\n", encoding="utf-8")
catalog, problems = read_catalog(folder)
assert catalog is not None
assert [ingredient.name.en for ingredient in catalog.ingredients] == ["Broccoli", "Scallion"]
assert catalog.ingredients[1].unit is None
assert [problem.place for problem in problems] == [
    BiText("ingredient 2", "食材 2"),
    BiText("ingredient 3", "食材 3"),
    BiText("ingredient 4", "食材 4"),
    BiText("ingredient 5", "食材 5"),
    BiText("ingredient 5", "食材 5"),
]
assert problems[0].text(Lang.ZH) == "英文名称“broccoli”也是食材 1 的名称。名称不能重复。"
assert problems[1].text(Lang.EN) == 'Unknown category "meats". The only category is produce.'
assert problems[2].text(Lang.EN) == 'Unknown unit "cups".'
assert problems[3].text(Lang.EN) == 'Unknown unit "cups".'
assert problems[4].text(Lang.ZH) == "中文名称“葱”也是食材 4 的名称。名称不能重复。"

folder.catalog.unlink()
catalog, problems = read_catalog(folder)
assert catalog is None
assert problems[0].text(Lang.EN) == "The file is missing."
```

### 2.9 `read_pantry`

- Module: catalog
- Purpose: Reads `pantry.toml` into a `Pantry`, and reports each problem with its place ([requirements 4](../../requirements.md#4-features), F03). It takes `None` for the catalog when the catalog could not be read, so that `check` still reports the pantry's own mistakes.

Signature:

```python
def read_pantry(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[Pantry | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `catalog` | `Catalog` or `None` | The catalog that the pantry's names come from. | `None` when the catalog could not be read. Then `read_pantry` checks only the form of the file. |

- Return value: A pair `(pantry, problems)`.
  - `pantry` is `None` when `read_toml` gives a problem, or when `catalog` is `None`. Otherwise it is a `Pantry` of the ingredient of every item that names one, even when `problems` is not empty. An ingredient that two items name, such as `盐` and `Salt`, is in the set once, and gives no problem.
  - `problems` holds the problem of `read_toml` alone, or the problems of the checks below. Each one has `Severity.ERROR` and the file `pantry.toml`.

The file has the layout of the example: `pantry = ["食用油", "盐", "糖", "生抽", "花椒"]`. Each item names an ingredient of the catalog in either language, and `read_pantry` finds it with `Catalog.find_ingredient` (2.6).

The places of the pantry's problems are these. N counts the items from 1, skipped items included.

| Place | English | Chinese |
| --- | --- | --- |
| The list `pantry` | `pantry` | `常备清单` |
| Item N of `pantry` | `item N` | `第 N 项` |

`read_pantry` makes these checks, in this order: the list, then each item in order, and then the other keys at the top of the file.

| Part | Check | Problem and place | What `read_pantry` does |
| --- | --- | --- | --- |
| `pantry` | The key is missing. | `MISSING_KEY`, with no place | It reads the list as empty. |
| `pantry` | The value is not a list. | `NOT_A_LIST`, at `pantry` | It reads the list as empty. |
| An item | The item is not a text. | `ITEM_NOT_A_TEXT`, at the item | It skips the item. |
| An item | The item is empty or holds only whitespace. | `EMPTY_ITEM`, at the item | It skips the item. |
| An item | `catalog` is not `None`, and `find_ingredient` finds no ingredient for the item. | `UNKNOWN_INGREDIENT`, at the item | It skips the item. |
| The top of the file | A key other than `pantry`. | `UNKNOWN_KEY`, with no place, in its form for one key | It ignores the key. |

`read_pantry` uses `MISSING_KEY`, `NOT_A_LIST`, `ITEM_NOT_A_TEXT`, `EMPTY_ITEM`, and `UNKNOWN_KEY` of `datafile` (2.10). The value `key` of `MISSING_KEY` and `NOT_A_LIST` is `pantry`. `UNKNOWN_KEY` gets the unknown key as the file writes it, and `keys` is `and_list(["pantry"])`, which gives "pantry". It also uses these messages of `catalog`:

| Name | English | Chinese |
| --- | --- | --- |
| `PANTRY` and `ITEM_N` | The places in the table of places, with `{number}` for N. | The places in the table of places, with `{number}` for N. |
| `UNKNOWN_INGREDIENT` | `Unknown ingredient "{name}".` | `未知食材“{name}”。` |

The value `name` is the item without whitespace at both ends. The F07 prototype shows `pantry.toml, item 3` with `Unknown ingredient "sesame oil".`.

Errors: None. `read_pantry` never raises for bad data.

- Side effects: Reads `pantry.toml` through `read_toml`. It writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10).

```python
from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.lang import BiText, Lang

catalog, _ = read_catalog(folder)
assert catalog is not None
pantry, problems = read_pantry(folder, catalog)
assert problems == ()
assert pantry is not None
assert len(pantry.ingredients) == 5
assert catalog.find_ingredient("Salt") in pantry.ingredients

text = 'pantry = ["食用油", "Salt", "sesame oil", 3, " "]\n'
folder.pantry.write_text(text, encoding="utf-8")
pantry, problems = read_pantry(folder, catalog)
assert pantry is not None
assert len(pantry.ingredients) == 2
assert [problem.place for problem in problems] == [
    BiText("item 3", "第 3 项"),
    BiText("item 4", "第 4 项"),
    BiText("item 5", "第 5 项"),
]
assert problems[0].text(Lang.EN) == 'Unknown ingredient "sesame oil".'
assert problems[1].text(Lang.ZH) == "这一项必须是放在引号里的文字。"
assert problems[2].text(Lang.EN) == "This item is empty."

pantry, problems = read_pantry(folder, None)
assert pantry is None
assert len(problems) == 2
```

### 2.10 `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TABLE`, `NOT_A_TEXT`, `EMPTY_TEXT`, `ITEM_NOT_A_TEXT`, `EMPTY_ITEM`, and `UNKNOWN_KEY`

- Module: datafile
- Purpose: The messages for a data file whose shape is wrong: a key that is missing, a value that is not a list, a table, or a text, a text or an item that is empty, and a key that a table may not have. Every data file can have these mistakes, so `datafile` holds the messages, and the readers of F03 to F06 give each mistake one wording. `settings` and `menus` may not import `catalog` (architecture 3), so messages kept in `catalog` would be copied. They live in `datafile/messages.py`, and `recipe_menu.datafile` exports them.

Signature:

```python
MISSING_KEY: Final[Message]
NOT_A_LIST: Final[Message]
NOT_A_TABLE: Final[Message]
NOT_A_TEXT: Final[Message]
EMPTY_TEXT: Final[Message]
ITEM_NOT_A_TEXT: Final[Message]
EMPTY_ITEM: Final[Message]
UNKNOWN_KEY: Final[Plural]
```

The messages are these. A placeholder is a name in braces, such as `{key}`. The braces of `{ ... }` and `[ ... ]` are part of the text, so the templates of `NOT_A_TABLE` write each brace twice (F02 design 2.2). `UNKNOWN_KEY` is a `Plural` value (F02 design 2.4).

| Name | English | Chinese |
| --- | --- | --- |
| `MISSING_KEY` | `The key "{key}" is missing.` | `缺少键“{key}”。` |
| `NOT_A_LIST` | `"{key}" must be a list in square brackets, [ ... ].` | `“{key}”必须是放在方括号 [ ... ] 里的列表。` |
| `NOT_A_TABLE` | `This item must be a table in braces, { ... }.` | `这一项必须是放在花括号 { ... } 里的表。` |
| `NOT_A_TEXT` | `"{key}" must be a text in quotation marks.` | `“{key}”必须是放在引号里的文字。` |
| `EMPTY_TEXT` | `"{key}" is empty.` | `“{key}”是空的。` |
| `ITEM_NOT_A_TEXT` | `This item must be a text in quotation marks.` | `这一项必须是放在引号里的文字。` |
| `EMPTY_ITEM` | `This item is empty.` | `这一项是空的。` |
| `UNKNOWN_KEY`, for one key | `Unknown key "{key}". The only key is {keys}.` | `未知键“{key}”。可用的键：{keys}。` |
| `UNKNOWN_KEY`, for more keys | `Unknown key "{key}". The keys are {keys}.` | `未知键“{key}”。可用的键：{keys}。` |

The table says when a reader uses each message.

| Constant | Mistake |
| --- | --- |
| `MISSING_KEY` | A key that the file or the table needs is missing. |
| `NOT_A_LIST` | The value of a key is not a list. |
| `NOT_A_TABLE` | An item of a list of tables is not a table. |
| `NOT_A_TEXT` | The value of a key is not a text, such as `3`, `true`, or a list. |
| `EMPTY_TEXT` | The value of a key is a text that is empty or holds only whitespace. |
| `ITEM_NOT_A_TEXT` | An item of a list of texts is not a text. |
| `EMPTY_ITEM` | An item of a list of texts is empty or holds only whitespace. |
| `UNKNOWN_KEY` | A table, or the top of the file, has a key that it may not have. The reader picks the form by the number of keys that the table may have. |

Parameters:

The values of the placeholders, which the caller passes to `Problem.error` (2.2).

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `key` | `str` | The key of the mistake, such as `en` or `categories`. For `UNKNOWN_KEY`, the unknown key as the file writes it. | Only in `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TEXT`, `EMPTY_TEXT`, and `UNKNOWN_KEY`. |
| `keys` | `BiText` | `and_list` of the keys that the table may have, in the order that the reader's design gives, such as "zh, en, category, and unit" and "zh、en、category 和 unit". | Only in `UNKNOWN_KEY`. |

- Return value: None. Each constant is a `Message`, and `UNKNOWN_KEY` is a `Plural` of two messages. `NOT_A_TABLE`, `ITEM_NOT_A_TEXT`, and `EMPTY_ITEM` have no placeholders, because the problem's place names the item.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from pathlib import Path

from recipe_menu.datafile import EMPTY_TEXT, MISSING_KEY, UNKNOWN_KEY, Problem
from recipe_menu.lang import Lang
from recipe_menu.text import and_list

missing = Problem.error(Path("catalog.toml"), None, MISSING_KEY, key="tags")
assert missing.text(Lang.EN) == 'The key "tags" is missing.'
assert EMPTY_TEXT.render(Lang.ZH, key="en") == "“en”是空的。"

only = UNKNOWN_KEY.pick(1).render(Lang.EN, key="items", keys=and_list(["pantry"]))
assert only == 'Unknown key "items". The only key is pantry.'
keys = and_list(["zh", "en", "category", "unit"])
chinese = UNKNOWN_KEY.pick(4).render(Lang.ZH, key="units", keys=keys)
assert chinese == "未知键“units”。可用的键：zh、en、category 和 unit。"
```

## 3. Changes to existing interfaces

None. F03 adds the modules `datafile` and `catalog`. It uses F01's `Unit` and `parse_unit`, and F02's `BiText`, `Lang`, `Message`, `MessageValue`, `Plural`, and `and_list`, as their designs give them, and changes none of them.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `datafile` is a base module that imports only `lang` and `text`, and `catalog` is a domain module that imports only `lang`, `units`, `text`, and `datafile`, as architecture 3 and 4 allow. Each value has the fields of architecture 5.2. `DataFolder` is the only place that knows the file names. `Problem` holds the severity, the file relative to the data folder, the place in both languages, and the message with its values. `Ingredient` and `Tag` need both names, and `Category` needs one. Choice 7 fits architecture 5.2 and 8. Sorted pairs keep `Problem` a frozen value with tuple collections, equality ignores the order of the keyword arguments, and rendering both languages at creation makes a wrong value fail in the reader that built it. The table that `read_toml` gives goes only to the reader of that file. That is what architecture 5 means by "A raw TOML table never leaves the module that reads its file", because architecture 3 gives reading a TOML file to `datafile` and reading the catalog to `catalog`. `menu_file` and `shopping_file` take the week as text, because `datafile` may not import `menus`. The index that `Catalog` builds is internal, so the Developer keeps it out of the fields that compare, hash, and print, and `Catalog` stays a value of three tuples. Choice 5 fits architecture 6 and the F07 prototype. `read_catalog` returns every item that no check skips, so one `check` run lists every problem, and `read_pantry` with `None` still reports the pantry's own mistakes. Finding 7 of round 1 is resolved. 2.8 says that two categories may not share a name, reports a shared name as an error, and keeps the category. That agrees with finding 1 and with architecture 6. The reader raises nothing, and the error makes the command exit with 1. A command other than `check` stops at the first error, so no shopping list shows two headings with one name. The ingredients of the kept category still find it by its key, so `check` reports no false `UNKNOWN_CATEGORY` for them. Architecture 5.2 sets no rule on the names of categories, so a `Catalog` that does not compare them fits the data model, as the example of 2.5 shows. 2.10 puts the messages for the shape of a file in `datafile`. That fits architecture 3, which gives problems with their places to `datafile`, and architecture 8, which puts a module's messages in its `messages.py`. `recipes`, `settings`, and `menus` may import `datafile`, and `settings` and `menus` may not import `catalog`. One wording point does not block and needs no revision before merge. The Constraints column of 2.5 says "Two categories may share a name", about the `Catalog` value, and 2.8 says "Two categories may not share a name", about the file. A later revision of 2.5 can say "A `Catalog` may hold two categories with the same name". The F13 note in section 2 does not affect F03's interfaces as designed, and it stays for Troy as finding 9 of round 1. The English pantry line of the F13 prototype, "cooking oil, salt, sugar, soy sauce, Sichuan pepper", writes four catalog names in small letters and keeps "Sichuan pepper", and v0.1-S16 expects "cooking oil, salt, sugar". No rule gives that line from names kept as written. Either F13 shows the names as the catalog writes them, which changes the prototype, v0.1-S16, and v0.1-S17 through the requirement change flow, or the catalog gets a key for a name inside a sentence, which would change `Ingredient` and `read_catalog` through the change flow. The Architect recommends the first, records the point for the F12 and F13 designs, and suggests that Troy decide it when Troy approves this design (R18), before F03 is built. |
| Follows the error handling and naming conventions | Pass | Finding 1 of round 1 is resolved. 2.8 now says that the catalog holds every item that no check skips, and that an item gets the duplicate check whenever no other check skips it. It names the checks that keep an item with a problem, and it gives the result of two cases. The Architect's model of design 0.2 gives two problems and no exception for each of the three files of round 1: `UNKNOWN_UNIT` then `DUPLICATE_ZH_NAME`, `UNKNOWN_KEY` then `DUPLICATE_EN_NAME`, and `EMPTY_TEXT` then `DUPLICATE_KEY`. It skips each of the three items. On 3,000 random catalogs that mix every check of 2.8, `read_catalog` raised no exception in Python 3.13.18 or 3.14.3. A category with the key and the Chinese name of an earlier one gets `DUPLICATE_KEY`, then `DUPLICATE_ZH_NAME`, and is skipped. Of three categories with one English name, the second and the third each name category 1, as "the first earlier item" in 2.8 says. The test plan can use these cases. Findings 4 to 6 are resolved, and the Architect checked each fact again on this PC. Finding 4: a key of 1,001 dotted parts raises `RecursionError` in 3.13.18 and parses in 3.14.3, and lists or tables nested 600 deep raise it in both. So 2.3 is right to test `NESTED_TOO_DEEPLY` with nesting. Finding 5: for the bytes `EF BB BF 61 0A FF` and for the new example of 2.3, the count in `error.object[:error.start]` gives line 2 in both versions. The count in the bytes of the file up to `error.start` gives line 1, so the example tells the two counts apart. Finding 6: after `C:\Users\Troy\recipe-menu\recipes`, `PureWindowsPath` turns `C:catalog.toml` into `catalog.toml` in that folder. After `D:\data\recipes`, it gives `C:catalog.toml`, a file in the current folder of drive C. 2.1 now gives both results. The choices of round 1 still pass. Choice 1: a decimal integer of more than 4,300 digits and nesting that is too deep are mistakes in a file, not bugs. Architecture 6 says that a reader never raises for bad data and that a traceback always means a bug, so `datafile` catches both exceptions. The `except` clauses name them at the place that makes the `Problem` (architecture 6 and 8). Choice 2: the 36 sample mistakes of round 1 still give the message that 2.3 names, in both versions, and `NOT_TOML` with the line is the general message of architecture 6. Choice 3 follows the F02 review: `catalog` decides that a blank name is missing before it builds a `BiText`. Choice 6: a name that could point outside its folder is a wrong call, so the `ValueError` follows architecture 6, and one rule on both systems follows architecture 1. Names follow PEP 8, and the messages are UPPER_SNAKE constants in each module's `messages.py` (architecture 8). Finding 8 of round 1 stays for Troy. Catching `ValueError` and `RecursionError` in `read_toml` is acceptable as designed. The Architect recommends that Troy let the row "A syntax mistake" of architecture 6 and the decision of ADR-0002 name the two exceptions. That change is wording only, and Troy approves it. |
| Does not duplicate an existing interface | Pass | `datafile` and `catalog` are new, and no interface of F01 or F02 reads a file, holds a path, or finds a name. `catalog` reads units with F01's `parse_unit`, writes lists with F02's `and_list` and plurals with `Plural`, and builds places with `Message.to_bitext`, so it writes none of them again. `Problem.text` calls `Message.render`. Finding 2 of round 1 is resolved. `datafile` exports the eight messages of 2.10, so the readers of F04 to F06 use them and do not copy them. None of the eight repeats a message of F02, because `text` exports only `RUN_CHECK`, `RUN_HELP_FOR_OPTIONS`, and `RUN_HELP_FOR_COMMANDS`. The signature of 2.10 declares each constant as `Final[Message]` or `Final[Plural]`, as `src/recipe_menu/text/messages.py` declares F02's messages. Finding 3 is resolved. 2.6 cites F01 design 2.3 and 2.6 for "English spellings match in any case", which both sections say. It cites `_fold` in `src/recipe_menu/units/_ops.py` for the ASCII rule, and that function changes case only when the text is ASCII. Choice 4: the matching form of 2.6 is a second case rule beside the one in `parse_unit`, for names and not for units. The two rules agree wherever both could apply. Every English unit spelling is ASCII, and no Chinese spelling holds an ASCII letter, so changing only A to Z gives the result of `parse_unit` for every spelling. Leaving look-alike letters as they are and normalizing nothing keeps the rule exact, and 2.6 names each case, so the test plan can cover what F01's test plan leaves open. For F10: the matching form is internal to `catalog`. If search needs the same case rule, the F10 design asks for it to be exported rather than writing another one. |
| Depends only on features earlier in the order | Pass | F03 uses F01's `Unit` and `parse_unit`, and F02's `BiText`, `Lang`, `Message`, `MessageValue`, `Plural`, and `and_list`. Both features come before F03 and pass their tests on main. The messages of 2.10 need only F02's `Message` and `Plural`. F03 depends on no later feature. The later features in section 2 call F03, and each of their designs gets its own review. The interfaces need only the standard library, such as `tomllib`, `pathlib`, `dataclasses`, `enum`, and `typing`, so R16 has no new dependency to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | Each assumption between modules is written in the design. A reader gets a table only from `read_toml`, and a name is found only through a `Catalog`, so recipes and the pantry share the catalog's `Ingredient` objects (architecture 5.2). `read_toml` depends on the English reason texts of `tomllib`. 2.3 names them with the versions that it checked, and any other text gives `NOT_TOML`, so a later Python can change a message but never the exit code. 2.10 writes down the placeholders `key` and `keys` and the mistake that each message reports, so F04 to F06 use the messages by a written contract. F03 shows no number from a file in a message. Two notes go to later designs. For F04, F06, and F09: a wrong name in `recipe_file`, `menu_file`, or `shopping_file` is a wrong call, so each caller checks the ID or the week first. F04's ID rule rejects at least the names in the Errors of 2.1, because Linux allows a file such as `recipes/a:b.toml`. F06 reports an unknown recipe ID before it builds a path, and `show ID` in F09 turns a wrong ID into its "unknown ID" output. For F04 to F06: `tomllib` reads a hexadecimal, octal, or binary integer of any length, and `0x` with 5,000 digits parses. `Problem` renders its values when it is created, so a message that shows a number from a file must bound the number first or show the file's text. Otherwise `Problem` raises the `ValueError` of F02 design 2.3 for bad data. |
| Changes an implemented interface only through the change flow | Pass | F01's `lang` and `units` and F02's `lang` and `text` are implemented. F03 uses them as their designs give them and adds nothing to them. It creates `datafile`, which architecture 3 gives to F03, and builds `catalog`. The messages of 2.10 go in the new `datafile`, not in F02's `text`, so no implemented module changes. Section 3 rightly says None. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | One blocking issue, finding 1: 2.8 lets an item that a check keeps with a problem skip the duplicate check, and `Catalog` then raises for bad data. The Architect checked the 18 `python` blocks of each file. Each one parses and equals its mirror. It built a model of section 2 and ran the 9 examples on a copy of the example data of `docs/prototypes/example-data.md`, in Python 3.13.18 and 3.14.3. Every assertion and every `# raises` holds, including the counts 6, 22, and 5 and the scallion at `catalog.ingredients[3]`. `ruff format --check` with ruff 0.17.4 reports both files formatted. Findings 2 to 7 do not block. | Changes requested. The Interface Designer revises 2.8 for finding 1 and decides on findings 2 to 7. |
| 2 | No blocking issue. Findings 1 to 7 of round 1 are resolved, and findings 8 and 9 stay for Troy. The Architect checked the 20 `python` blocks of each file. Each one parses and equals its mirror. It updated its model to design 0.2 and ran the 10 examples on a copy of the example data of `docs/prototypes/example-data.md`, in Python 3.13.18 and 3.14.3. Every assertion and every `# raises` holds, including the byte order mark of 2.3, the shared category name of 2.5, and ingredient 5 of 2.8. `ruff format --check` with ruff 0.17.4 reports both files formatted. One wording point in 2.5 does not block. | Approved. Troy decides findings 8 and 9 when Troy approves this design (R18). |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-10 | First draft. |
| 0.2 | 2026-11-10 | Answers round 1 of the Architect review. `read_catalog` keeps every item that no check skips, and checks an item for duplicates whenever no other check skips it, so an item that a check keeps with a problem still gets the duplicate check (2.8). A category whose name matches a name of an earlier category gets `DUPLICATE_ZH_NAME` or `DUPLICATE_EN_NAME` and is kept, and `Catalog` does not compare the names of categories (2.5 and 2.8). The messages for the shape of a file move from `catalog` to `datafile`, which exports them, together with `ITEM_NOT_A_TEXT` and `EMPTY_ITEM` (2.10). `NOT_UTF8` counts the line in `error.object[:error.start]`, so a byte order mark does not change it (2.3). The limit on key parts depends on the Python release, so only nesting tests `NESTED_TOO_DEEPLY` (2.3). The reason for the rule on names with a drive is corrected (2.1). The ASCII rule of `parse_unit` is cited from F01's code (2.6). The examples of 2.3, 2.5, and 2.8 cover the new cases. |
| 1.0 | 2026-11-10 | Approved by Troy. |
