---
troy-doc: "F02-design"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "design.zh-CN.md"
---

# F02 Bilingual terminal output: interface design

## 1. Feature

- ID and name: F02 Bilingual terminal output
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: None

## 2. Interfaces

F02 adds one value to the base module `lang` and builds the base module `text` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.lang` exports `BiText` beside F01's `Lang`. `recipe_menu.text` exports `Message`, `MessageValue`, `Plural`, `RUN_CHECK`, `RUN_HELP_FOR_COMMANDS`, `RUN_HELP_FOR_OPTIONS`, `and_list`, `choose_lang`, `comma_list`, `display_width`, `format_table`, and `use_utf8`. Each module's `__init__.py` lists its names in `__all__`. The three shared messages live in `text/messages.py` (architecture 8). The other files behind each module are the Developer's choice.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F02 gives |
| --- | --- |
| It holds every message of the tool in English and Chinese. | `Message` (2.2 and 2.3), which cannot exist in one language only, and the messages that `text` shares (2.5). Every other message is a `Message` constant in the `messages.py` of the module that shows it ([architecture 8](../../architecture.md#8-naming-and-coding-rules), ADR-0004). |
| It picks the language: `--lang` first, then the settings, then English. | `choose_lang` (2.7). |
| It shows text that has two languages in the chosen language, and falls back to the other one. | `BiText` (2.1). `Message.render` (2.3) and the lists of 2.6 give their `BiText` values the same fallback. |
| English plurals and lists such as "a, b, and c" and "a、b、c" come from `text` (architecture 8). | `Plural` (2.4), `and_list`, and `comma_list` (2.6). |
| It prints aligned tables in which a Chinese character takes two columns. | `display_width` (2.8) and `format_table` (2.9). |
| It prints Chinese correctly in PowerShell whatever the console code page is. | `use_utf8` (2.10). |

These rules hold for every interface below:

- `lang` imports nothing from the package, and `text` imports only `lang` ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)).
- No interface prints, reads a file or the environment, or keeps state. `format_table` returns lines, and the caller writes them to the streams in `Context` (architecture 8). `use_utf8` changes only the stream that it gets.
- The exceptions below come from wrong calls, which are bugs ([architecture 6](../../architecture.md#6-error-handling)). A reader checks the values in a file before it builds a `BiText` from them, and reports a wrong value as a `Problem`.
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F02 interface has a performance target. PT01 times commands that print through `format_table`, such as `list` with 1,000 recipes. So `format_table` and `display_width` take time in proportion to the characters that they get.

These later features are meant to call them:

- F03 builds `Problem` in `datafile` from a `Message` and its `MessageValue` values, with the place as a `BiText` from `Message.to_bitext`. `catalog` holds each name as a `BiText`, and names the categories in a message with `and_list`.
- F04 holds recipe names and notes as `BiText` values, and finds a missing language with `BiText.exact`.
- F05 picks the language with `choose_lang`, sets stdout and stderr to UTF-8 with `use_utf8`, lays out the help with `format_table`, and ends a usage error with `RUN_HELP_FOR_OPTIONS` or `RUN_HELP_FOR_COMMANDS`.
- F07 counts the errors and the warnings with `Plural`, and lists what it checked with `and_list`.
- F09, F10, F11, and F13 print their tables with `format_table`, join tags and other short lists with `comma_list`, and count with `Plural`. They add `RUN_CHECK` when an error in a data file stops them.

### 2.1 `BiText`

- Module: lang
- Purpose: A text in two languages, with at least one of them, such as a recipe name or an ingredient's note. It gives the asked language, or the other language when the asked one is missing ([architecture 5.2](../../architecture.md#52-values)). `Message.to_bitext` (2.3) and the lists of 2.6 give one too, so a rendered text can be the value of another message or the place of a `Problem`.

Signature:

```python
@dataclass(frozen=True, slots=True)
class BiText:
    en: str | None = None
    zh: str | None = None

    def get(self, lang: Lang) -> str: ...

    def exact(self, lang: Lang) -> str | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `en` | `str` or `None` | The English text. | `None` when the text has no English. |
| `zh` | `str` or `None` | The Chinese text. | `None` when the text has no Chinese. `en` and `zh` are not both `None`. |
| `lang` | `Lang` | The language that `get` or `exact` gives. | None |

- Return value: A `BiText`.
  - `get(lang)` gives the text in `lang`, or the text in the other language when the one in `lang` is `None`. It never gives `None`.
  - `exact(lang)` gives the text in `lang`, or `None` when that text is missing. A reader uses it to warn about a missing language.
  - An empty string counts as a text, so `get` gives it with no fallback. A reader that treats an empty name in a file as missing passes `None` for it.
  - Two `BiText` values are equal when their `en` and their `zh` are equal, and a `BiText` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `en` and `zh` are both `None`. |
| `TypeError` | `en` or `zh` is neither a `str` nor `None`, such as a number read from a TOML file. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import BiText, Lang

name = BiText("Tomato and egg stir-fry", "番茄炒蛋")
assert name.get(Lang.ZH) == "番茄炒蛋"
assert name.exact(Lang.EN) == "Tomato and egg stir-fry"
pork = BiText(zh="红烧肉")
assert pork.get(Lang.EN) == "红烧肉"
assert pork.exact(Lang.EN) is None
assert BiText("", "盐").get(Lang.EN) == ""
assert BiText("Salt", "盐") == BiText(en="Salt", zh="盐")
BiText()  # raises ValueError
BiText(en=3)  # raises TypeError
```

### 2.2 `Message` and `MessageValue`

- Module: text
- Purpose: A text that the tool shows, with an English and a Chinese template that have the same `{name}` placeholders ([architecture 5.2](../../architecture.md#52-values)). Creating one without both languages, or with different placeholders, fails at once. So any test that imports the module that defines a message catches the mistake (ADR-0004). `MessageValue` is the type of a placeholder's value.

Signature:

```python
type MessageValue = str | int | BiText


@dataclass(frozen=True, slots=True)
class Message:
    en: str
    zh: str

    @property
    def placeholders(self) -> frozenset[str]: ...

    # Methods: render and to_bitext (2.3).
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `en` | `str` | The English template. | Holds more than whitespace. |
| `zh` | `str` | The Chinese template. | Holds more than whitespace, and the same placeholder names as `en`. |

A template follows these rules:

1. A placeholder is a name in braces, such as `{name}`. The name has lowercase ASCII letters, digits, and `_`, and starts with a letter.
2. Both templates hold the same set of names. A name can appear more than once, and the two templates can hold the names in different orders.
3. A placeholder has no conversion and no format spec, not even an empty one such as `{count:}`. `string.Formatter().parse` reads `{count:}` the same as `{count}`, so the check reads the characters between the braces. A value is already text, or an `int` or a `BiText` that `render` turns into text (2.3).
4. To show a brace itself, a template writes it twice, as `str.format` does.

- Return value: A `Message`. `placeholders` gives the set of names in its templates, which is empty for a message with no placeholders. Two messages are equal when both of their templates are equal, and a `Message` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `en` or `zh` is not a `str`. |
| `ValueError` | `en` or `zh` is empty or holds only whitespace. |
| `ValueError` | A template is not a valid format string, such as one that holds a single `{` or a single `}`. |
| `ValueError` | A placeholder is not a name by the rules above, such as `{}`, `{0}`, `{Name}`, `{ name }`, `{tag.en}`, or `{items[0]}`. |
| `ValueError` | A placeholder has a conversion or a format spec, even an empty one, such as `{count!r}`, `{count:>3}`, or `{count:}`. |
| `ValueError` | The two templates hold different sets of names. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.text import Message

UNKNOWN_RECIPE = Message('Unknown recipe "{recipe}".', "未知菜谱“{recipe}”。")
assert UNKNOWN_RECIPE.placeholders == frozenset({"recipe"})
assert Message("No errors.", "没有错误。").placeholders == frozenset()
Message("{count} recipes.", "共 {total} 个菜谱。")  # raises ValueError
Message("Saved {path}.", " ")  # raises ValueError
Message("Saved {0}.", "已保存 {0}。")  # raises ValueError
Message("{count:>3} recipes.", "{count:>3} 个菜谱。")  # raises ValueError
Message("{count:} recipes.", "{count:} 个菜谱。")  # raises ValueError
```

### 2.3 `Message.render` and `Message.to_bitext`

- Module: text, methods of `Message` (2.2)
- Purpose: `render` writes a message in one language with its values. `to_bitext` writes it in both languages, for a text that is shown later or inside another message, such as the place of a `Problem` or a part of a list.

Signature:

```python
def render(self, lang: Lang, /, **values: MessageValue) -> str: ...


def to_bitext(self, /, **values: MessageValue) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `lang` | `Lang` | The language that `render` writes. | Positional only, so a template can also have a placeholder named `lang`. |
| `values` | `MessageValue` keyword arguments | The value of each placeholder, by its name. | One for each placeholder, and no others. |

- Return value:
  - `render` gives the template in `lang`, with each placeholder replaced by its value. A `str` goes in as it is, and an `int` as its decimal digits with no thousands separator. A `BiText` goes in as its `get(lang)`, so a value that lacks `lang` falls back to its other language.
  - A value goes in as it is, so a brace in a value is never read as a placeholder.
  - `to_bitext` gives `BiText(self.render(Lang.EN, **values), self.render(Lang.ZH, **values))`.

Errors:

Both methods check the names of the values before their types.

| Error | When |
| --- | --- |
| `ValueError` | The names of `values` are not exactly the placeholders: a placeholder has no value, or a value has no placeholder. |
| `TypeError` | A value is not a `str`, an `int`, or a `BiText`, such as a `float` or `None`. A `bool` and an `enum.Enum` member are wrong too, although a `bool` is an `int` and a `StrEnum` member, such as `Lang.ZH` or a `Meal` of architecture 5.2, is a `str`. A `StrEnum` member would show its English value in Chinese text. |
| `ValueError` | An `int` value has more than 4,300 digits, Python's limit on writing an `int` (`sys.int_info.default_max_str_digits`). This error comes only from a wrong call. Counts come nowhere near the limit, and F05, F06, and F09 give servings an upper bound (F01 design, section 4). |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

UNKNOWN_RECIPE = Message('Unknown recipe "{recipe}".', "未知菜谱“{recipe}”。")
assert UNKNOWN_RECIPE.render(Lang.ZH, recipe="tomato-eggs") == "未知菜谱“tomato-eggs”。"
assert UNKNOWN_RECIPE.render(Lang.EN, recipe="{x}") == 'Unknown recipe "{x}".'
both = UNKNOWN_RECIPE.to_bitext(recipe="tomato-eggs")
assert both == BiText('Unknown recipe "tomato-eggs".', "未知菜谱“tomato-eggs”。")

SERVINGS = Message("Servings: {count}   Tags: {tags}", "份数：{count}   标签：{tags}")
tags = BiText("quick, home-style", "快手、家常")
assert SERVINGS.render(Lang.EN, count=2, tags=tags) == "Servings: 2   Tags: quick, home-style"
assert SERVINGS.render(Lang.ZH, count=2, tags=tags) == "份数：2   标签：快手、家常"

NO_OTHER = Message('No other recipe has the tag "{tag}".', "没有别的菜谱带有标签“{tag}”。")
assert NO_OTHER.render(Lang.EN, tag=BiText(zh="素")) == 'No other recipe has the tag "素".'

UNKNOWN_RECIPE.render(Lang.EN)  # raises ValueError
UNKNOWN_RECIPE.render(Lang.EN, recipe="rice", meal="dinner")  # raises ValueError
UNKNOWN_RECIPE.render(Lang.EN, recipe=None)  # raises TypeError
SERVINGS.render(Lang.EN, count=True, tags=tags)  # raises TypeError
UNKNOWN_RECIPE.render(Lang.ZH, recipe=Lang.ZH)  # raises TypeError
```

### 2.4 `Plural`

- Module: text
- Purpose: An English plural: one message for a count of 1, and one for every other count, such as "1 recipe" and "7 recipes". Chinese has no plural, so the Chinese templates of the two messages are usually the same.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Plural:
    one: Message
    other: Message

    def pick(self, count: int) -> Message: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `one` | `Message` | The message for a count of 1. | The same placeholder names as `other`. |
| `other` | `Message` | The message for every other count, 0 included. | The same placeholder names as `one`. |
| `count` | `int` | The count that `pick` chooses by. | Any `int`. |

- Return value: A `Plural`. `pick(count)` gives `one` when `count` is 1, and `other` for every other count, such as 0, 2, or 7. The caller then renders the message with its values, which usually include the count. Two `Plural` values are equal when both of their messages are equal, and a `Plural` is hashable.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `one` and `other` have different placeholder names. |

- Side effects: None
- Performance target: None

Example:

The second and third cases are lines of the F09 prototype "List the recipes with one tag".

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural

WITH_TAG = Plural(
    Message('{count} recipe has the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
    Message('{count} recipes have the tag "{tag}".', "共 {count} 个菜谱带有标签“{tag}”。"),
)
quick = BiText("quick", "快手")
assert WITH_TAG.pick(1).render(Lang.EN, count=1, tag=quick) == '1 recipe has the tag "quick".'
assert WITH_TAG.pick(3).render(Lang.EN, count=3, tag=quick) == '3 recipes have the tag "quick".'
assert WITH_TAG.pick(3).render(Lang.ZH, count=3, tag=quick) == "共 3 个菜谱带有标签“快手”。"
assert WITH_TAG.pick(0) is WITH_TAG.other

ONE_ERROR = Message("{count} error", "{count} 个错误")
Plural(ONE_ERROR, Message("errors", "错误"))  # raises ValueError
```

### 2.5 `RUN_CHECK`, `RUN_HELP_FOR_OPTIONS`, and `RUN_HELP_FOR_COMMANDS`

- Module: text
- Purpose: The shared messages that architecture 3 and ADR-0004 give `text`: the line that ends a command that an error in a data file stopped, and the two lines that point to `--help`. Every other message lives in the `messages.py` of the module that shows it (architecture 8).

Signature:

```python
RUN_CHECK: Final[Message] = Message(
    'Run "recipe-menu check" to see every problem.',
    "运行“recipe-menu check”查看所有问题。",
)
RUN_HELP_FOR_OPTIONS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the options.',
    "运行“recipe-menu --help”查看选项。",
)
RUN_HELP_FOR_COMMANDS: Final[Message] = Message(
    'Run "recipe-menu --help" to see the commands.',
    "运行“recipe-menu --help”查看命令。",
)
```

The table says where each message comes from and when a command shows it.

| Constant | Source | Shown after |
| --- | --- | --- |
| `RUN_CHECK` | The English text is in [architecture 6](../../architecture.md#6-error-handling) and in the F11 prototype "A menu with a mistake". The Chinese text is in section 6 of `architecture.zh-CN.md`. | The first error in a data file stops a command other than `check`. |
| `RUN_HELP_FOR_OPTIONS` | The English text is in the F05 prototype "Mistakes on the command line". No prototype shows the Chinese text. | A wrong option or option value, such as `--lang fr`. |
| `RUN_HELP_FOR_COMMANDS` | The English text is in the F05 prototype "Mistakes on the command line". No prototype shows the Chinese text. | An unknown command, such as `cook`. |

Parameters: None

- Return value: None. Each constant is a `Message` with no placeholders, so `render` takes only the language.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.text import RUN_CHECK, RUN_HELP_FOR_COMMANDS

assert RUN_CHECK.render(Lang.EN) == 'Run "recipe-menu check" to see every problem.'
assert RUN_CHECK.render(Lang.ZH) == "运行“recipe-menu check”查看所有问题。"
assert RUN_HELP_FOR_COMMANDS.placeholders == frozenset()
```

### 2.6 `and_list` and `comma_list`

- Module: text
- Purpose: Joins texts into one list in both languages (architecture 8). `and_list` writes a list inside a sentence, such as "breakfast, lunch, and dinner" and "早餐、午餐和晚餐". `comma_list` writes a plain list, such as the tags in a table cell, "quick, vegetarian" and "快手、素".

Signature:

```python
def and_list(items: Iterable[str | BiText]) -> BiText: ...


def comma_list(items: Iterable[str | BiText]) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `items` | An iterable of `str` or `BiText` items | The texts to join, in order. A `str` item is the same in both languages, such as a recipe ID or a category key. | Any number of items, none included. Not a single `str`. |

- Return value: A `BiText` with both languages set. The English text joins each item's `get(Lang.EN)`, and the Chinese text joins each item's `get(Lang.ZH)`. So an item that lacks a language falls back on its own. The table gives the text for each number of items, with the items `a`, `b`, `c`, and `d`.

| Items | `and_list`, English | `and_list`, Chinese | `comma_list`, English | `comma_list`, Chinese |
| --- | --- | --- | --- | --- |
| No items | The empty string | The empty string | The empty string | The empty string |
| a | `a` | `a` | `a` | `a` |
| a, b | `a and b` | `a 和 b` | `a, b` | `a、b` |
| a, b, c | `a, b, and c` | `a、b 和 c` | `a, b, c` | `a、b、c` |
| a, b, c, d | `a, b, c, and d` | `a、b、c 和 d` | `a, b, c, d` | `a、b、c、d` |

More items follow the last row. In English, `and_list` joins two items with " and ". With three or more, it puts ", " between the items and "and " before the last one. In Chinese, it puts "、" between the items and "和" before the last one. These rules give the spaces that the two functions add in Chinese:

1. No space goes next to "、", in `and_list` or in `comma_list`.
2. A space goes between "和" and an item when the item's character next to "和" is an ASCII letter or digit (`A` to `Z`, `a` to `z`, or `0` to `9`). That character is the last one of the item before "和", or the first one of the item after it.
3. An empty item has no character next to "和", so no space goes between it and "和".
4. The rules read each item's `get(Lang.ZH)`, so they also apply to the English text of an item that has no Chinese.

So the items `a`, `b`, and `c` give `a、b 和 c`. The F07 items `7 个菜谱` and `1 个周菜单` give `7 个菜谱和 1 个周菜单`. The F10 items `“葱”` and `“quick”` give `“葱”和“quick”`, because a Chinese quotation mark is not an ASCII letter or digit.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `items` is a `str`. A `str` is an iterable of its characters, so `and_list("abc")` would otherwise list `a`, `b`, and `c`. |
| `TypeError` | An item is neither a `str` nor a `BiText`, such as `None`. An `enum.Enum` member is wrong too, although a `StrEnum` member such as `Lang.ZH` is a `str`. It would show its English value in Chinese text, as in 2.3. |

- Side effects: None
- Performance target: None

Example:

The case with `QUOTED` gives the two words of the F10 prototype "Two words, in Chinese". The case with `CHECKED` gives the first line of the F07 prototype in both languages.

```python
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, Plural, and_list, comma_list

meals = [BiText("breakfast", "早餐"), BiText("lunch", "午餐"), BiText("dinner", "晚餐")]
assert and_list(meals) == BiText("breakfast, lunch, and dinner", "早餐、午餐和晚餐")
assert and_list(meals[1:]) == BiText("lunch and dinner", "午餐和晚餐")
assert and_list(meals[2:]) == BiText("dinner", "晚餐")
assert and_list([]) == BiText("", "")
assert and_list(["a", "b", "c", "d"]) == BiText("a, b, c, and d", "a、b、c 和 d")
assert and_list(["produce", "meat", "eggs"]).get(Lang.EN) == "produce, meat, and eggs"
assert and_list([BiText("tofu", "豆腐"), BiText(en="quick")]).get(Lang.ZH) == "豆腐和 quick"
tags = [BiText("quick", "快手"), BiText(zh="素")]
assert comma_list(tags) == BiText("quick, 素", "快手、素")

QUOTED = Message('"{word}"', "“{word}”")
words = [QUOTED.to_bitext(word="葱"), QUOTED.to_bitext(word="quick")]
assert and_list(words) == BiText('"葱" and "quick"', "“葱”和“quick”")

SETTINGS = Message("the settings", "设置")
CATALOG = Message("the catalog", "目录")
PANTRY = Message("the pantry", "常备清单")
RECIPES = Plural(
    Message("{count} recipe", "{count} 个菜谱"),
    Message("{count} recipes", "{count} 个菜谱"),
)
WEEK_MENUS = Plural(
    Message("{count} week menu", "{count} 个周菜单"),
    Message("{count} week menus", "{count} 个周菜单"),
)
CHECKED = Message("Checked {files}.", "已检查{files}。")
parts = [
    SETTINGS.to_bitext(),
    CATALOG.to_bitext(),
    PANTRY.to_bitext(),
    RECIPES.pick(7).to_bitext(count=7),
    WEEK_MENUS.pick(1).to_bitext(count=1),
]
files = and_list(parts)
english = CHECKED.render(Lang.EN, files=files)
assert english == "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
chinese = CHECKED.render(Lang.ZH, files=files)
assert chinese == "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。"

and_list("abc")  # raises TypeError
comma_list([Lang.ZH])  # raises TypeError
```

### 2.7 `choose_lang`

- Module: text
- Purpose: Picks the language of a command by [requirements 3](../../requirements.md#3-how-users-interact-with-it): `--lang` first, then the settings, then English. `cli` calls it at start (F05).

Signature:

```python
def choose_lang(option: Lang | None, setting: Lang | None) -> Lang: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `option` | `Lang` or `None` | The language that `--lang` names. | `None` when the command line has no `--lang`. |
| `setting` | `Lang` or `None` | The `language` of the settings. | `None` when the settings name no language, or when there are no settings. |

- Return value: `option` when it is not `None`, else `setting` when it is not `None`, else `Lang.EN`.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import Lang
from recipe_menu.text import choose_lang

assert choose_lang(Lang.EN, Lang.ZH) is Lang.EN
assert choose_lang(None, Lang.ZH) is Lang.ZH
assert choose_lang(None, None) is Lang.EN
```

### 2.8 `display_width`

- Module: text
- Purpose: The number of columns that a text takes in Windows Terminal, by the rule of ADR-0004. Only `text` measures width (ADR-0004), and `format_table` aligns its columns with it.

Signature:

```python
def display_width(text: str) -> int: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` | The text to measure, such as one line of a table cell. | Any string. A line break counts as one column like any other character, so measure one line at a time. |

- Return value: The sum of the columns of the characters in `text`, 0 for the empty string. `display_width` gives each character its columns by the first of these rules that applies, with the `unicodedata` module of the running Python:
  1. A combining mark takes 0 columns. A combining mark is a character whose general category is `Mn` (nonspacing mark) or `Me` (enclosing mark).
  2. A character whose East Asian width is `W` (wide) or `F` (fullwidth) takes 2 columns.
  3. Every other character takes 1 column. That includes the ambiguous characters, such as `“`, `—`, and `×`, which Windows Terminal draws one column wide, and the spacing marks of category `Mc`.

Errors: None

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.text import display_width

assert display_width("Tomato") == 6
assert display_width("番茄鸡蛋面") == 10
assert display_width("周一 11月16日") == 13
assert display_width("，、：") == 6
assert display_width("—×“”") == 4
assert display_width("e\N{COMBINING ACUTE ACCENT}") == 1
assert display_width("") == 0
```

### 2.9 `format_table`

- Module: text
- Purpose: Lays out rows as aligned columns by display width. It gives the tables of the prototypes: `list` and `search` (F09 and F10), the ingredients of `show` (F09), `menu show` (F11), the shopping list (F13), the help (F05), and the list of files that `init` writes (F08). Every column is left-aligned, as in every prototype.

Signature:

```python
def format_table(
    rows: Sequence[Sequence[str]],
    *,
    indent: int = 0,
    gap: int = 3,
    min_widths: Sequence[int] = (),
) -> tuple[str, ...]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `rows` | A sequence of rows, each a sequence of `str` cells | The rows, with the header first when the table has one. | Not a `str`, and no row is a `str`. Every row has the same number of cells, 1 or more. May be empty. |
| `indent` | `int` | The spaces before each line, such as 2 for the ingredients of `show`. | 0 or more. |
| `gap` | `int` | The spaces between two columns. Every prototype uses 3, except the file list of `init`, which uses 4. | 1 or more. |
| `min_widths` | A sequence of `int` | The smallest width of each column, from the left, in columns, before the gap. F05 needs it, because the help has the same column width in both languages. | Each 0 or more. No more items than a row has cells. A column after the last item has no minimum. |

- Return value: The lines of the table, without line ends, by these rules:
  1. A cell's lines are `cell.splitlines()`, or one empty line when that gives none, as for `""`. A row takes as many lines as its cell with the most lines. A cell with fewer lines is empty in the row's later lines.
  2. A column's width is the largest `display_width` of the lines in its cells, or its item of `min_widths` when that is larger.
  3. Each line starts with `indent` spaces. Each column's line follows, left-aligned. A column other than the last is padded with spaces to its width, and `gap` more spaces follow it. The last column is not padded, so its item of `min_widths` has no effect.
  4. Spaces (U+0020) at the end of each line are removed. So an empty cell at the end of a line adds nothing, and a line whose cells are all empty is the empty string.
  5. The lines come in the order of the rows. With no rows, `format_table` gives the empty tuple.
  6. A cell is never cut or wrapped.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `rows` or one of its rows is a `str`. A `str` is a sequence of its characters, so `format_table(["ab", "cd"])` would otherwise give each letter a cell. `format_table` checks for this error before the others. |
| `ValueError` | The rows do not all have the same number of cells, or the rows have no cells. |
| `ValueError` | `indent` is less than 0, `gap` is less than 1, or an item of `min_widths` is less than 0. These are checked with no rows too. |
| `ValueError` | `min_widths` has more items than a row has cells. |

- Side effects: None
- Performance target: None

Example:

Each expected line is a line of the prototype named in the comment above it.

```python
from recipe_menu.text import format_table

# F09 "List the recipes", in Chinese.
recipes = [
    ("ID", "名称", "份数", "标签"),
    ("choy-sum", "清炒菜心", "2", "快手、素"),
    ("tomato-egg-noodles", "番茄鸡蛋面", "2", "快手、主食"),
]
assert format_table(recipes) == (
    "ID                   名称         份数   标签",
    "choy-sum             清炒菜心     2      快手、素",
    "tomato-egg-noodles   番茄鸡蛋面   2      快手、主食",
)

# F11 "Show the week after you fill it": a cell with two lines.
week = [
    ("Day", "Lunch", "Dinner"),
    ("Mon 16 Nov", "—", "Tomato and egg stir-fry ×2\nStir-fried choy sum ×2"),
    ("Sat 21 Nov", "Tomato and egg noodles ×2", "—"),
]
assert format_table(week) == (
    "Day          Lunch                       Dinner",
    "Mon 16 Nov   —                           Tomato and egg stir-fry ×2",
    "                                         Stir-fried choy sum ×2",
    "Sat 21 Nov   Tomato and egg noodles ×2   —",
)

# F09 "Show one recipe for 4 servings, in Chinese": an indent and empty last cells.
ingredients = [
    ("番茄", "600 g", "切块"),
    ("鸡蛋", "6 个", ""),
    ("食用油", "4 汤匙", ""),
]
assert format_table(ingredients, indent=2) == (
    "  番茄     600 g    切块",
    "  鸡蛋     6 个",
    "  食用油   4 汤匙",
)

# F08 "In English": a gap of 4.
listing = [
    ("catalog.toml", "6 categories, 22 ingredients, 5 tags"),
    ("recipes\\tomato-egg.toml", "an example recipe in both languages"),
]
assert format_table(listing, indent=2, gap=4) == (
    "  catalog.toml               6 categories, 22 ingredients, 5 tags",
    "  recipes\\tomato-egg.toml    an example recipe in both languages",
)

# F05 "Help in Chinese": the width of "menu show [WEEK]" in the English help.
commands = [
    ("init", "创建数据文件夹和示例数据。"),
    ("menu show [周]", "查看一个周菜单。"),
]
assert format_table(commands, indent=2, min_widths=(16,)) == (
    "  init               创建数据文件夹和示例数据。",
    "  menu show [周]     查看一个周菜单。",
)

assert format_table([]) == ()
format_table([("a", "b"), ("c",)])  # raises ValueError
format_table(recipes, gap=0)  # raises ValueError
format_table(recipes, min_widths=(1, 1, 1, 1, 1))  # raises ValueError
format_table(["ab", "cd"])  # raises TypeError
```

### 2.10 `use_utf8`

- Module: text
- Purpose: Makes a console stream write UTF-8, so Chinese shows correctly whatever the console code page is (ADR-0004). At start, `cli` calls it on `sys.stdout` and `sys.stderr`, and then passes the streams on in `Context` ([architecture 8](../../architecture.md#8-naming-and-coding-rules)).

Signature:

```python
def use_utf8(stream: TextIO) -> None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `stream` | `TextIO` | An output stream, such as `sys.stdout`. | Open. |

- Return value: None

Errors: None

- Side effects:
  - When `stream` is an `io.TextIOWrapper`, as `sys.stdout` and `sys.stderr` are, `use_utf8` calls its `reconfigure` with `encoding="utf-8"` and `errors="backslashreplace"`. `reconfigure` first flushes what the stream holds. From then on, the stream writes UTF-8. It writes a lone surrogate, the only kind of code point that UTF-8 cannot encode, as an escape such as `\udcff`, and never raises for it.
  - Any other stream, such as the `io.StringIO` of a test, stays as it is.
  - On a Windows console, Python writes through the console's Unicode interface, so the code page does not matter there. Output that PowerShell redirects or pipes is UTF-8 after this call (ADR-0004, section 5).
- Performance target: None

Example:

```python
import io

from recipe_menu.text import use_utf8

raw = io.BytesIO()
stream = io.TextIOWrapper(raw, encoding="cp1252")
use_utf8(stream)
assert stream.encoding == "utf-8"
stream.write("番茄 \udcff")
stream.flush()
assert raw.getvalue() == "番茄 \\udcff".encode()
use_utf8(io.StringIO())  # changes nothing
```

## 3. Changes to existing interfaces

None. F02 adds `BiText` to `recipe_menu.lang` and to its `__all__`. `Lang` stays as F01 design 2.1 gives it, and architecture 3 gives `lang` to both F01 and F02.

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `BiText` joins `Lang` in `lang`, which architecture 3 gives to F01 and F02, and it has the fields and the fallback of architecture 5.2. `text` gets exactly what architecture 3 lists for it, and it imports only `lang`. `BiText`, `Message`, and `Plural` are frozen dataclasses with `slots=True`, and the collections that the interfaces return are tuples and frozensets (architecture 8). A place as a `BiText` and values of type `MessageValue` fit `Problem` and `UsageError` in architecture 5.2. `format_table` returns lines, and `use_utf8` takes its stream as an argument, so only `cli` touches the console and output goes to the streams in `Context` (architecture 8). The Architect built a model of the rules of 2.9 in Python 3.13.18 and rebuilt every table of the prototypes with it. Each line came out exactly as the prototype shows it: the F05 commands and options in both languages with `min_widths=(16,)`, the F08 file lists with `gap=4`, the F09 recipe lists and ingredients, the F10 results, the F11 weeks with cells of several lines, and the F13 lists. That covers choice 5. In round 2 the model follows version 0.2, and every table still comes out exactly, because the new `TypeError` of 2.9 changes no layout. Two points go to later designs and do not block. The English help of F05 needs `min_widths` too, because its options column takes the width of its commands column. F13 can lay out its list as one table over all categories and put each category heading between the lines, because no cell of that table has a line break. |
| Follows the error handling and naming conventions | Pass | Finding 1 of round 1 is resolved. Rules 1 to 4 of 2.6 put a space between "和" and an item only when the item's character next to "和" is an ASCII letter or digit. The project's Chinese templates space Chinese and ASCII text the same way, as in `共 {count} 个菜谱`. So `and_list` gives every Chinese list of the prototypes: `7 个菜谱和 1 个周菜单` in F07, the meals `午餐和晚餐` in F08, and `“葱”和“quick”` and `“豆腐”和“quick”` in F10. No command needs to build a list by hand (architecture 8). The rules put no space next to a letter outside ASCII, as in `café和茶`, and no prototype has such a case. The Interface Designer took findings 2 to 5. Each new error comes from a wrong call (architecture 6): a `TypeError` for a value of the wrong type, and a `ValueError` for the template `{count:}`. Rejecting every `enum.Enum` member keeps the English value of a `StrEnum`, such as a `Meal`, out of Chinese text, so a caller passes the meal's names as a `BiText`. `format_table` checks for a `str` before its other errors, so a `str` row always gives the `TypeError` that names the mistake. One point does not block. `format_table` does not check the type of a cell, so a `StrEnum` cell would show its English value in a Chinese table. A test that compares a Chinese table with its prototype line by line catches that. The choices that the Interface Designer named in round 1 still pass. Choice 1: an empty string as a text keeps `and_list([])` a valid `BiText`, and the `TypeError` of `BiText` catches a reader that skipped its check of the file's values (architecture 6). Choice 2: with no conversion and no format spec, a template cannot pad a value. `str.format` pads by code points, so this keeps width in `text` (ADR-0004). The errors of `render` come from wrong calls (architecture 6), and rejecting `bool` keeps `True` out of the text. Choice 3: the Chinese of `RUN_HELP_FOR_OPTIONS` and `RUN_HELP_FOR_COMMANDS` has the form of `RUN_CHECK` in architecture 6 and of the Chinese prototypes, such as `运行“recipe-menu init”创建它`. Troy reads both texts when Troy approves this PR (R18). Choice 4: ADR-0004 does not define a combining mark. The common `wcwidth` rule gives `Mn` and `Me` no column, and spacing marks (`Mc`) occur only in scripts that the tool does not show, so the ADR needs no change. Choice 6: `errors="backslashreplace"` writes a lone surrogate as an escape. A file name can hold one, and so can a recipe ID, so bad data never causes a traceback here (architecture 6). Names follow PEP 8. |
| Does not duplicate an existing interface | Pass | F01 exports `Lang` and the names of `units`. Its unit names are plain data behind `Unit.label` and `Quantity.to_text` (ADR-0004), and no F01 type holds a text in two languages, so `BiText` repeats nothing. `Plural` picks one of two messages, and `Unit.label(plural=True)` gives a unit name, as the F01 review recorded. `and_list` writes a list inside a sentence, and `comma_list` writes a plain list. These are the two kinds of list in the prototypes. One `format_table` lays out every table of the prototypes. |
| Depends only on features earlier in the order | Pass | F02 has no feature dependencies. It uses `lang`, which F01 created, as architecture 4 lists. Its interfaces need only the standard library, such as `enum`, `unicodedata`, and `io`, so R16 has no new dependency to review. The later features that section 2 names call F02, and F02 calls none of them. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | `text` imports only `lang`, keeps no state, reads nothing, and prints nothing. `use_utf8` changes only the stream that it gets. Each caller gives `format_table` its layout in `indent`, `gap`, and `min_widths`, so no command relies on a width that only `text` knows. The spacing rules of 2.6 read only the text of the items, so no caller needs to know them, and F07 and F10 get their lines from the same function. The plans for F03 to F13 in section 2 bind no later design, and each design gets its own review. Two notes go to later designs. For F03 and F04: an empty string is a text, so each reader decides whether an empty or blank name in a file is missing, and passes `None` for a missing one. Otherwise `list` shows an empty name and `check` gives no warning. For F05 and F11: architecture 6 says that an error with exit code 2 ends with a line that points to `recipe-menu --help`, but the F11 prototype shows `"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` with no such line. F02's interfaces stand either way, because `app` and `cli` decide which hint follows a `UsageError`. The Architect recommends that the F05 design let a `UsageError` name its hint, or no hint. Architecture 6 would then exempt a message that already says what to write. Troy decides that change to architecture 6 during the F05 design. |
| Changes an implemented interface only through the change flow | Pass | F01's `lang` is implemented. F02 adds `BiText` to `recipe_menu.lang` and its `__all__`, and it keeps `Lang` as F01 design 2.1 gives it, as architecture 3 plans. No F01 test checks the names that `lang` exports, so the addition breaks no test. Section 3 rightly says None. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | One blocking issue, finding 1. In Chinese, `and_list` puts no spaces around "和" (2.6), so it cannot give the F07 prototype's `7 个菜谱和 1 个周菜单`, and the last example of 2.6 fails. The Architect ran every example of section 2 against a model of the design's rules in Python 3.13.18. Every code block parses and equals its mirror, and every other expected value follows from the rules. Findings 2 to 5 do not block. A `StrEnum` value, such as `Lang.ZH` or a `Meal` of architecture 5.2, passes `render` as a `str` and shows its English value in Chinese text (2.3). 2.2 does not say whether `{count:}`, with an empty format spec, is wrong. A single `str` passed to `and_list`, `comma_list`, or `format_table` passes the type check and gives a list of its letters (2.6 and 2.9). The `é` of 2.8 is `e` followed by U+0301, which a later edit could turn into U+00E9 and so stop testing rule 1. | Changes requested. The Interface Designer revises 2.6 for finding 1 and decides on findings 2 to 5. |
| 2 | No blocking issue. The Architect checked each change since round 1 with `git diff f55f9de HEAD`, updated its model to version 0.2, and ran every example of section 2 again in Python 3.13.18. Every code block parses and equals its mirror, and every assertion and every `# raises` holds. Every prototype table that the model rebuilds still matches the prototype exactly. Probes confirm the rules of 2.6 on lists of two and three quoted words, on empty items, and on items that fall back to English. They also confirm that `string.Formatter().parse` gives `{count:}` and `{count}` the same result, as 2.2 says. One point does not block: `format_table` does not check the type of a cell (Follows the error handling and naming conventions). | Approved. Rules 1 to 4 of 2.6 resolve finding 1, and the Interface Designer took findings 2 to 5. |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-10 | First draft. |
| 0.2 | 2026-11-10 | Answers round 1 of the Architect review. In Chinese, `and_list` puts a space between "和" and an item whose character next to "和" is an ASCII letter or digit, so it gives the F07 line and still gives the F10 line (2.6). A template rejects an empty format spec such as `{count:}` (2.2). `render` rejects an `enum.Enum` member (2.3). `and_list` and `comma_list` reject a single `str` as `items`, an item that is neither a `str` nor a `BiText`, and an `enum.Enum` member (2.6). `format_table` rejects a `str` as `rows` or as a row (2.9). The example of a combining mark in 2.8 names U+0301 with an escape. |
| 1.0 | 2026-11-10 | Approved by Troy. |
