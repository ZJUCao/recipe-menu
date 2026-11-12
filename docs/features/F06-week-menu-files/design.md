---
troy-doc: "F06-design"
lang: "en"
version: "1.0"
updated: "2026-11-12"
status: "Approved by Troy on 2026-11-12"
mirror: "design.zh-CN.md"
---

# F06 Week menu files: interface design

## 1. Feature

- ID and name: F06 Week menu files
- Requirement: [docs/requirements.md](../../requirements.md#4-features)
- Hard dependencies: None
- Soft dependencies: F04, F05

## 2. Interfaces

F06 builds the domain module `menus` ([architecture 3](../../architecture.md#3-modules)). `recipe_menu.menus` exports `Day`, `Dish`, `IsoWeek`, `MealSlot`, `NOT_A_WEEK`, `WeekMenu`, `list_menu_weeks`, `read_week_menu`, `short_date`, and `week_from_argument`, and its `__init__.py` lists them in `__all__`. Its messages live in `menus/messages.py`. `NOT_A_WEEK` is exported for the commands (2.7), and every other message is internal to the module (architecture 8). The other files behind it are the Developer's choice. A menu file has the layout of `menus/2026-W47.toml` in `docs/prototypes/example-data.md`. The F11 prototype shows the file that `menu new` writes, and the F07 prototype shows how `check` reports the problems of a menu.

The table maps each part of the requirement to the interfaces that meet it.

| The requirement says | F06 gives |
| --- | --- |
| It reads a week menu file: its ISO week. | `read_week_menu` (2.9), which reads the file of one `IsoWeek` (2.1) and checks the file's `week` against the file name. `list_menu_weeks` (2.8) gives the weeks that have a file. |
| It reads the days, the meals from the settings, and each dish with its servings. | The `WeekMenu` (2.6) that `read_week_menu` gives. It holds the meals of the `Settings`, and one `MealSlot` (2.5) for each `Day` (2.3) and each meal. Each slot holds its `Dish` values (2.4), with the servings of the file or of the settings. |
| It turns `this` and `next` into ISO weeks. A command that takes a week accepts an ISO week, `this`, or `next`, and without a week it uses this week ([requirements 3](../../requirements.md#3-how-users-interact-with-it)). | `week_from_argument` and `NOT_A_WEEK` (2.7), and `IsoWeek.of` (2.1). |
| It reports unknown recipe IDs, unknown meals, and wrong servings with their places. | The `Problem` values that `list_menu_weeks` and `read_week_menu` return, each with its file and the places of 2.9. |
| `menus` holds ISO weeks, this week and next week, and dates and day names in both languages (architecture 3). | `IsoWeek` (2.1), `IsoWeek.date_range` and `short_date` (2.2), and `Day.label` (2.3). |

These rules hold for every interface below:

- `menus` imports only `lang`, `text`, `datafile`, `settings`, and `recipes` from the package ([architecture 3](../../architecture.md#3-modules) and [4](../../architecture.md#4-dependency-rules)). From `recipes`, it uses only `is_recipe_id`.
- `menus` reaches the disk only through `datafile`: it lists `menus/` with `list_toml_files` and reads each file with `read_toml`. No interface writes a file, prints, reads the environment or today's date, or keeps state. A caller passes today's date in ([architecture 8](../../architecture.md#8-naming-and-coding-rules)).
- A reader never raises for bad data ([architecture 6](../../architecture.md#6-error-handling)). It checks the whole file, records a `Problem` for each mistake, and goes on, so one `check` run lists every problem. The exceptions in the Errors tables below come from wrong calls, which are bugs.
- Every value is a frozen dataclass with `slots=True` or an enum, and its collections are tuples or frozensets (architecture 8).
- Doc comments are in English only (R05), and troy-check rejects Chinese characters in them. So a doc comment describes a message in English and never quotes its Chinese template. Chinese text appears only in string literals.
- No F06 interface has a performance target. PT01 times `check`, which reads 52 week menus, and `menu show` and `shop`, which read one week of 63 dishes ([requirements 7.1](../../requirements.md#71-performance-targets)). So `list_menu_weeks` lists `menus/` once. `read_week_menu` reads one file once, takes time in proportion to its size, and looks up each dish's ID in a `frozenset`.

The two readers split the work as those of F04 do (architecture 8):

- `list_menu_weeks` reads no file. It gives the weeks from the file names in `menus/`, so F07 can count the menus, and F11, F13, and F14 can tell a week with no menu from a broken file, without parsing any menu.
- `read_week_menu` reads one week's file and lists no folder. Its caller passes a week that `list_menu_weeks` gave, and the recipe IDs that `list_recipe_ids` gave.

The design makes these choices. The subsection in parentheses after each choice gives its rules.

1. **A week has one written form.** A week is the ISO year in four digits, `-W`, and the week in two digits, such as `2026-W47` (2.1). `IsoWeek.parse` reads exactly the text that `str` writes, in a file name, in the key `week`, and on the command line. So `2026-w47`, `2026-W7`, and `2026-W99` are not weeks. `2025-W53` is not a week either, because 2025 has 52 weeks. On Windows, `menus/2026-w47.toml` opens for the week `2026-W47`, and on Linux it does not, so exact names keep the two systems alike (F04 design, section 4). One form also matches the help's note on weeks (F05 design 2.10) and the message `NOT_A_WEEK`.
2. **The file names give the weeks.** `list_menu_weeks` gives the week of each name in `menus/` that is a week (2.8). It passes on the problems of `list_toml_files`, and it gives an error for every other `.toml` name, as `list_recipe_ids` does for `recipes/`. A missing `menus/` folder is an error, because `init` creates it.
3. **The reader takes the settings, or none.** `read_week_menu` takes the `Settings` whose meals and servings the menu uses, or `None` when the settings could not be read (2.9). With `None`, it makes every check that does not depend on the settings. It accepts each of the three meals, it reports a key of a day that names no meal at all with `UNKNOWN_KEY`, and it gives no menu, as `read_recipe` gives no recipe without a catalog. So F07 reports no problem that comes only from the default meals of `Settings()`, which `context.settings` holds after a broken settings file (F05 design 2.4).
4. **The caller passes the recipe IDs.** `read_week_menu` takes the IDs of `list_recipe_ids` as a `frozenset`. A dish names an unknown recipe when its ID breaks the rule of `is_recipe_id` or is not in the set. F06 never builds a path from a dish. It builds the path of a menu only from an `IsoWeek`, so `DataFolder.menu_file` never gets a wrong name (F03 design 2.1). F07 makes the set once for all its menus, so 52 menus cost one listing of `recipes/`.
5. **A file may leave out days and meals.** The key `week` is required, and it names the week of the file name. A day that the file lacks holds no dishes, and so does a meal of the settings that a day lacks. Nothing is lost then, and a menu that you wrote before you added a meal to the settings stays correct. A key of a day that names no meal of the settings is an error, because `menu show` and `shop` would leave out its dishes. The one exception is a meal such as `breakfast = []` that holds no dish. So a menu that you wrote before you removed a meal from the settings stays correct too (2.9).
6. **Dishes and their servings.** A dish is a recipe ID in quotation marks, or a table with `recipe` and an optional `servings`, as in `example-data.md`. A dish without servings gets `settings.servings` ([architecture 5.2](../../architecture.md#52-values)). `read_week_menu` reads the servings with `read_servings` at the dish's place, so the range 1 to 100 and its three messages stay in one place (F05 design, choice 3). A message shows a number from the file only through `read_servings`, which limits it to 15 digits (F04 design, choice 2). The text of `week` goes into a message as a text. So no message meets F02's limit of 4,300 digits.
7. **A menu is whole or missing.** `read_week_menu` gives no menu when the file has an error, as `read_recipe` gives no recipe (2.9). Every command other than `check` stops at the first error (architecture 6), so no command uses a menu with an error. No check of a menu gives a warning.
8. **Dates and names in both languages.** `menus` gives the day names (2.3), and the date of a day and the dates of a week as texts (2.2), as architecture 3 assigns them. So F11 and F13 write the same texts. `menus` also exports `NOT_A_WEEK`, the message for a wrong week on the command line (2.7). F11, F13, and F14 show it, and `shop` may not import `menu` (architecture 3), so its one copy lives here. The message says what to write, so its `UsageError` names no hint, as ADR-0008 (decision A), the F11 prototype "A week without a menu", and v0.1-S15 have it.

These later features are meant to call them:

- F07 calls `list_menu_weeks` once, counts its weeks for "1 week menu", and reports its problems. It reads each week with `read_week_menu`. It passes the settings that `read_settings` gave, which are `None` after an error, not `context.settings`, which then holds `Settings()` (choice 3). It passes a `frozenset` of the IDs of `list_recipe_ids`, made once for every menu.
- F08 creates the empty folder `menus/`, for which `list_menu_weeks` gives no weeks and no problem.
- F11's `menu new` and `menu show` get their week with `week_from_argument(value, context.today)`, where `value` is the value of the argument `WEEK`, or `None` when the command line gives none. When it gives `None`, they raise `UsageError(NOT_A_WEEK, None, week=value)`. `menu show` looks for the week among those of `list_menu_weeks`, reads it with `read_week_menu` and `context.settings`, and stops at the first error with `first_error` and `stop_at_error`, as the F11 prototype "A menu with a mistake" shows. It names the week with `str(week)` and `date_range`, each day's row with `short_date`, and each meal's column with `Meal.heading`, and it gets the dishes of each cell with `WeekMenu.dishes`. `menu new` writes a file that `read_week_menu` reads with no problem and with every slot empty. On Windows, a file `2026-w47.toml` keeps `datafile` from creating `2026-W47.toml`, and `list_menu_weeks` reports that file, so F11's design decides what `menu new` says then.
- F12 takes the dishes from `WeekMenu.slots`, and scales each recipe by `Fraction(dish.servings, recipe.servings)`. F11 and F12 count a meal only when its slot holds a dish. That count gives "4 meals, 9 dishes" in the F11 and F13 prototypes.
- F13's `shop` gets its week as F11 does, and shows `date_range` in its heading. F11 and F13 show the same line for a week with no menu file, and `shop` may not import `menu`. So their designs decide whether `menus` exports that message too.
- F14 finds the empty meals as the slots with no dishes, and checks a menu with `read_week_menu` before it writes the file.

troy-mode's flow has one mock PR and one implementation PR. `menus` can fit in R03's five files: `__init__.py`, `messages.py`, and three internal files. The mock defines every constant, such as the members of `Day` and every message, so the module imports. A test that checks only a constant, such as the text of `NOT_A_WEEK`, passes against the mock and breaks R09, as the Architect noted for F05.

### 2.1 `IsoWeek`

- Module: menus
- Purpose: One ISO week, such as `2026-W47`, which runs from Monday 16 November to Sunday 22 November 2026 ([requirements 3](../../requirements.md#3-how-users-interact-with-it), [architecture 5.2](../../architecture.md#52-values)). It writes and reads the form of a file name, gives its seven dates, and gives the week of a date, so a caller finds this week from today's date.

Signature:

```python
@dataclass(frozen=True, slots=True, order=True)
class IsoWeek:
    year: int
    week: int

    @classmethod
    def of(cls, day: date) -> IsoWeek: ...

    @classmethod
    def parse(cls, text: str) -> IsoWeek | None: ...

    @property
    def dates(self) -> tuple[date, ...]: ...

    # Property: date_range (2.2).

    def __str__(self) -> str: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `year` | `int` | The ISO year. Near New Year, it can differ from the calendar year of a date in the week. | From 1 to 9999. Not a `bool`. |
| `week` | `int` | The week of the ISO year. | From 1 to the number of weeks of `year`, which is 53 when 28 December of `year` falls in week 53, and 52 otherwise. Not a `bool`. The week's Sunday is on or before 31 December 9999, the last date of `datetime.date`, so `9999-W52`, whose Sunday would be 2 January 10000, is not a week. |
| `day` | `date` | A date, for `of`. | Not from 27 to 31 December 9999, which fall in `9999-W52`. |
| `text` | `str` | A text to read, for `parse`, such as a file name without `.toml`. | Any string. |

- Return value: An `IsoWeek`.
  - `str(week)` gives `f"{year:04d}-W{week:02d}"`, such as `2026-W47`, `2027-W01`, or `0001-W01`. A file name, the key `week`, and every message write a week this way.
  - `IsoWeek.of(day)` gives the week that holds `day`, as `day.isocalendar()` gives its year and week. So 10 November 2026 is in `2026-W46`, 1 January 2027 is in `2026-W53`, and 30 December 2024 is in `2025-W01`.
  - `IsoWeek.parse(text)` gives the week whose `str` equals `text`, or `None` when there is no such week. So `text` is four ASCII digits, `-W`, and two ASCII digits, with nothing before or after them, and it names a week by the constraints above. `parse` never raises for a `str`.
  - `dates` gives the seven dates of the week, Monday to Sunday, in the order of `Day` (2.3).
  - Two weeks are equal when their year and their week are equal. Weeks compare by year and then by week, so `sorted` gives the order of time, which is also the order of their `str`. An `IsoWeek` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `year` or `week` is not an `int`, or it is a `bool`. |
| `ValueError` | `year` and `week` break the constraints above, such as `IsoWeek(2025, 53)`, `IsoWeek(2026, 0)`, or `IsoWeek(9999, 52)`. |
| `ValueError` | `of` gets a date from 27 to 31 December 9999. |

- Side effects: None
- Performance target: None

Example:

```python
from datetime import date

from recipe_menu.menus import IsoWeek

week = IsoWeek(2026, 47)
assert str(week) == "2026-W47"
assert IsoWeek.parse("2026-W47") == week
assert str(IsoWeek(2027, 1)) == "2027-W01"
assert IsoWeek.parse("0001-W01") == IsoWeek(1, 1)
assert IsoWeek.of(date(2026, 11, 10)) == IsoWeek(2026, 46)
assert IsoWeek.of(date(2027, 1, 1)) == IsoWeek(2026, 53)
assert IsoWeek.of(date(2024, 12, 30)) == IsoWeek(2025, 1)
assert week.dates == tuple(date(2026, 11, day) for day in range(16, 23))
assert IsoWeek(2026, 53).dates[-1] == date(2027, 1, 3)
assert IsoWeek.parse("2026-W53") == IsoWeek(2026, 53)
assert IsoWeek(2026, 53) < IsoWeek(2027, 1)
wrong = ["2025-W53", "2026-W99", "2026-W00", "2026-w47", "2026-W7", " 2026-W47", "2026-W47\n"]
assert [IsoWeek.parse(text) for text in wrong] == [None] * 7
fullwidth = "".join(chr(0xFF10 + int(digit)) for digit in "2026")
assert IsoWeek.parse(fullwidth + "-W47") is None

IsoWeek(2025, 53)  # raises ValueError
IsoWeek(2026, 0)  # raises ValueError
IsoWeek(9999, 52)  # raises ValueError
IsoWeek(2026, True)  # raises TypeError
IsoWeek.of(date(9999, 12, 31))  # raises ValueError
```

### 2.2 `IsoWeek.date_range` and `short_date`

- Module: menus. `date_range` is a property of `IsoWeek` (2.1).
- Purpose: The dates of a week and the date of one day, as texts in both languages ([architecture 3](../../architecture.md#3-modules), ADR-0004). F11 and F13 show `date_range` after the week, as in "Menu for 2026-W47, 16 to 22 November 2026", and F11 shows `short_date` at the start of each day's row, as in "Mon 16 Nov".

Signature:

```python
@property
def date_range(self) -> BiText: ...


def short_date(day: date) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `day` | `date` | The date to write. | None |

- Return value: A `BiText` with both languages set.
  - `date_range` writes the week's Monday and Sunday by the first row of the first table below that applies. `first` and `last` are the days of the month of Monday and of Sunday.
  - `short_date(day)` writes `{weekday} {day} {month}` in English and `{weekday} {month}月{day}日` in Chinese. `weekday` is the short name of the day in English and the day's `label` in Chinese (2.3), such as `Mon` and `周一`. So 16 November 2026 gives `Mon 16 Nov` and `周一 11月16日`, the first cells of the F11 prototype "Show the week after you fill it".

| When | English | Chinese | Example |
| --- | --- | --- | --- |
| Monday and Sunday are in one month. | `{first} to {last} {month} {year}` | `{year}年{month}月{first}日至{last}日` | `2026-W47`: `16 to 22 November 2026` and `2026年11月16日至22日` |
| Monday and Sunday are in two months of one year. | `{first} {first_month} to {last} {last_month} {year}` | `{year}年{first_month}月{first}日至{last_month}月{last}日` | `2026-W49`: `30 November to 6 December 2026` and `2026年11月30日至12月6日` |
| Monday and Sunday are in two years. | `{first} {first_month} {first_year} to {last} {last_month} {last_year}` | `{first_year}年{first_month}月{first}日至{last_year}年{last_month}月{last}日` | `2026-W53`: `28 December 2026 to 3 January 2027` and `2026年12月28日至2027年1月3日` |

These three templates and the one of `short_date` are messages in `menus/messages.py`. A day and a year are `int` values with no leading zero. A month is its name in English and its number in Chinese:

| Month | English in `date_range` | English in `short_date` | Chinese |
| --- | --- | --- | --- |
| 1 | `January` | `Jan` | `1` |
| 2 | `February` | `Feb` | `2` |
| 3 | `March` | `Mar` | `3` |
| 4 | `April` | `Apr` | `4` |
| 5 | `May` | `May` | `5` |
| 6 | `June` | `Jun` | `6` |
| 7 | `July` | `Jul` | `7` |
| 8 | `August` | `Aug` | `8` |
| 9 | `September` | `Sep` | `9` |
| 10 | `October` | `Oct` | `10` |
| 11 | `November` | `Nov` | `11` |
| 12 | `December` | `Dec` | `12` |

Errors: None. `date_range` and `short_date` never raise for an `IsoWeek` and a `date`.

- Side effects: None
- Performance target: None

Example:

```python
from datetime import date

from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek, short_date

november = BiText("16 to 22 November 2026", "2026年11月16日至22日")
assert IsoWeek(2026, 47).date_range == november
december = BiText("30 November to 6 December 2026", "2026年11月30日至12月6日")
assert IsoWeek(2026, 49).date_range == december
new_year = BiText("28 December 2026 to 3 January 2027", "2026年12月28日至2027年1月3日")
assert IsoWeek(2026, 53).date_range == new_year
assert short_date(date(2026, 11, 16)) == BiText("Mon 16 Nov", "周一 11月16日")
assert short_date(date(2026, 11, 22)) == BiText("Sun 22 Nov", "周日 11月22日")
assert short_date(date(2026, 12, 1)) == BiText("Tue 1 Dec", "周二 12月1日")
```

### 2.3 `Day`

- Module: menus
- Purpose: The seven days of a week, Monday to Sunday, with their names in both languages (architecture 3, ADR-0004). Each member's value is the key of the day's table in a menu file.

Signature:

```python
class Day(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @property
    def label(self) -> BiText: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `value` | `str` | The key of a file, for `Day(value)`. | A value of the table below, exactly as written there. |

- Return value: A `Day`.
  - `list(Day)` gives the members in the order of a week, Monday to Sunday. `IsoWeek.dates[i]` is the date of `list(Day)[i]`.
  - `label` gives the day's name, as in a place such as "Monday dinner" and "周一晚餐". The table lists it, with the short English name that `short_date` uses (2.2). In Chinese, `short_date` uses `label`.
  - `Day(value)` gives the member whose value is `value`, and `value in Day` tells whether a word is a day, without an exception.
  - A `Day` is a `str`, so `sorted` sorts days by their words, which is not the order of a week. Sort them with `key=list(Day).index`, as for `Meal` (F05 design 2.1).

| Member | Value | `label`, English | `label`, Chinese | Short name in `short_date`, English |
| --- | --- | --- | --- | --- |
| `MONDAY` | `monday` | `Monday` | `周一` | `Mon` |
| `TUESDAY` | `tuesday` | `Tuesday` | `周二` | `Tue` |
| `WEDNESDAY` | `wednesday` | `Wednesday` | `周三` | `Wed` |
| `THURSDAY` | `thursday` | `Thursday` | `周四` | `Thu` |
| `FRIDAY` | `friday` | `Friday` | `周五` | `Fri` |
| `SATURDAY` | `saturday` | `Saturday` | `周六` | `Sat` |
| `SUNDAY` | `sunday` | `Sunday` | `周日` | `Sun` |

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `Day(value)` gets a word that is not a member's value, such as `funday` or `Monday`. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.lang import BiText
from recipe_menu.menus import Day

assert len(Day) == 7
assert list(Day)[0] is Day.MONDAY
assert list(Day)[-1] is Day.SUNDAY
assert Day("sunday") is Day.SUNDAY
assert "friday" in Day
assert "Friday" not in Day
assert Day.MONDAY.label == BiText("Monday", "周一")
assert Day.SUNDAY.label == BiText("Sunday", "周日")
assert sorted(Day)[0] is Day.FRIDAY

Day("funday")  # raises ValueError
Day("Monday")  # raises ValueError
```

### 2.4 `Dish`

- Module: menus
- Purpose: One dish of a meal: the ID of its recipe and its servings ([architecture 5.2](../../architecture.md#52-values)). `read_week_menu` fills in the servings of the settings when the file gives none, so later modules never need the settings for a dish.

Signature:

```python
@dataclass(frozen=True, slots=True)
class Dish:
    recipe_id: str
    servings: int
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `recipe_id` | `str` | The ID of the recipe, such as `cola-wings`. | `is_recipe_id(recipe_id)` is true (F04 design 2.4). `read_week_menu` gives only IDs that `list_recipe_ids` gave. |
| `servings` | `int` | The servings of the dish. | From `MIN_SERVINGS` to `MAX_SERVINGS`, which are 1 and 100 (F05 design 3.1). Not a `bool`. |

- Return value: A `Dish`. Two dishes are equal when their two fields are equal, and a `Dish` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `recipe_id` is not a `str`. |
| `ValueError` | `is_recipe_id(recipe_id)` is false. |
| `TypeError` | `servings` is not an `int`, or it is a `bool`. |
| `ValueError` | `servings` is less than 1 or more than 100. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.menus import Dish

dish = Dish("cola-wings", 4)
assert dish.recipe_id == "cola-wings"
assert dish.servings == 4
assert dish == Dish("cola-wings", 4)

Dish(3, 4)  # raises TypeError
Dish("Cola-Wings", 4)  # raises ValueError
Dish("cola-wings", 0)  # raises ValueError
Dish("cola-wings", 101)  # raises ValueError
Dish("cola-wings", True)  # raises TypeError
```

### 2.5 `MealSlot`

- Module: menus
- Purpose: One meal of one day, such as Monday dinner, with its dishes in the file's order. A meal holds zero or more dishes ([requirements 3](../../requirements.md#3-how-users-interact-with-it), Q16). F14 fills the slots that hold no dish.

Signature:

```python
@dataclass(frozen=True, slots=True)
class MealSlot:
    day: Day
    meal: Meal
    dishes: tuple[Dish, ...] = ()
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `day` | `Day` | The day. | None |
| `meal` | `Meal` | The meal (F05 design 2.1). | None |
| `dishes` | A tuple of `Dish` values | The dishes, in the file's order. | May be empty. A dish may appear more than once. |

- Return value: A `MealSlot`. Two slots are equal when their three fields are equal, and a `MealSlot` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `day` is not a `Day`, `meal` is not a `Meal`, or `dishes` is not a tuple or holds an item that is not a `Dish`. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.menus import Day, Dish, MealSlot
from recipe_menu.settings import Meal

slot = MealSlot(Day.TUESDAY, Meal.DINNER, (Dish("mapo-tofu", 2), Dish("rice", 2)))
assert [dish.recipe_id for dish in slot.dishes] == ["mapo-tofu", "rice"]
assert MealSlot(Day.WEDNESDAY, Meal.LUNCH).dishes == ()

MealSlot(Day.TUESDAY, Meal.DINNER, [Dish("rice", 2)])  # raises TypeError
MealSlot("tuesday", Meal.DINNER)  # raises TypeError
```

### 2.6 `WeekMenu`

- Module: menus
- Purpose: The menu of one week: its ISO week, the meals of each day, and one slot for each day and each meal, Monday to Sunday ([architecture 5.2](../../architecture.md#52-values)). It holds the meals that the settings name. It refers to recipes by ID only, and a command loads the recipes that it needs (architecture 5.3).

Signature:

```python
@dataclass(frozen=True, slots=True)
class WeekMenu:
    week: IsoWeek
    meals: tuple[Meal, ...]
    slots: tuple[MealSlot, ...]

    def dishes(self, day: Day, meal: Meal) -> tuple[Dish, ...]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `week` | `IsoWeek` | The week. | None |
| `meals` | A tuple of `Meal` values | The meals of each day, from the settings. | 1 to 3 meals, in the order of `Meal`, each once, as for `Settings.meals` (F05 design 2.2). |
| `slots` | A tuple of `MealSlot` values | The meals of the week with their dishes. | Exactly one slot for each day and each meal of `meals`: Monday to Sunday, and within a day in the order of `meals`. So it holds `7 * len(meals)` slots. |
| `day` and `meal` | `Day` and `Meal` | The slot that `dishes` gives. | `meal` is in `meals`. |

- Return value: A `WeekMenu`.
  - `dishes(day, meal)` gives the dishes of the slot of `day` and `meal`. F11 fills each cell of its table with it.
  - Two menus are equal when their three fields are equal, and a `WeekMenu` is hashable.

Errors:

| Error | When |
| --- | --- |
| `TypeError` | `week` is not an `IsoWeek`, `meals` is not a tuple of `Meal` values, or `slots` is not a tuple of `MealSlot` values. |
| `ValueError` | `meals` is empty, holds a meal twice, or is not in the order of `Meal`. |
| `ValueError` | `slots` does not hold exactly one slot for each day and each meal of `meals`, in the order of the constraints. |
| `ValueError` | `dishes` gets a meal that is not in `meals`. |

- Side effects: None
- Performance target: None

Example:

```python
from recipe_menu.menus import Day, Dish, IsoWeek, MealSlot, WeekMenu
from recipe_menu.settings import Meal

meals = (Meal.LUNCH, Meal.DINNER)
friday_dinner = (Dish("rice", 2),)
slots = tuple(
    MealSlot(day, meal, friday_dinner if day is Day.FRIDAY and meal is Meal.DINNER else ())
    for day in Day
    for meal in meals
)
menu = WeekMenu(IsoWeek(2026, 48), meals, slots)
assert len(menu.slots) == 14
assert menu.slots[0] == MealSlot(Day.MONDAY, Meal.LUNCH)
assert menu.dishes(Day.FRIDAY, Meal.DINNER) == friday_dinner
assert menu.dishes(Day.MONDAY, Meal.LUNCH) == ()
assert sum(1 for slot in menu.slots if slot.dishes) == 1

WeekMenu(IsoWeek(2026, 48), meals, slots[:-1])  # raises ValueError
WeekMenu(IsoWeek(2026, 48), (Meal.DINNER, Meal.LUNCH), slots)  # raises ValueError
menu.dishes(Day.MONDAY, Meal.BREAKFAST)  # raises ValueError
```

### 2.7 `week_from_argument` and `NOT_A_WEEK`

- Module: menus
- Purpose: Turns the argument `WEEK` of a command into an ISO week: an ISO week, `this`, `next`, or no argument for this week ([requirements 3](../../requirements.md#3-how-users-interact-with-it) and [4](../../requirements.md#4-features)). F11's `menu new` and `menu show`, F13's `shop`, and F14's `menu suggest` call it with `Context.today`. `NOT_A_WEEK` is the message of their `UsageError` for any other text.

Signature:

```python
NOT_A_WEEK: Final[Message]


def week_from_argument(text: str | None, today: date) -> IsoWeek | None: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `text` | `str` or `None` | The value of the argument as you typed it, or `None` when the command line gives none. | Any string. |
| `today` | `date` | Today's date, from `Context.today` (F05 design 2.4). | None |

- Return value: The week by the first row of this table that applies, or `None`.

| `text` | Week |
| --- | --- |
| `None` | `IsoWeek.of(today)`, this week. |
| `this` | `IsoWeek.of(today)`. |
| `next` | `IsoWeek.of(today + timedelta(days=7))`, the week after this week. |
| A text that `IsoWeek.parse` reads, such as `2026-W47` | That week. |
| Any other text, such as `2026-W99`, `This`, `2026-w47`, or the empty text | `None`. The caller raises `UsageError(NOT_A_WEEK, None, week=text)`. |

`this` and `next` are exact, in these small letters, as `IsoWeek.parse` is exact (choice 1). The help's note on weeks names the same three forms (F05 design 2.10). `NOT_A_WEEK` is this message. Its English text is the line of the F11 prototype "A week without a menu". `{week}` is the text as you typed it.

| Name | English | Chinese |
| --- | --- | --- |
| `NOT_A_WEEK` | `"{week}" is not a week. Write an ISO week such as 2026-W47, "this", or "next".` | `“{week}”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。` |

The message says what to write, so its `UsageError` names no hint, and `cli` writes only the message (ADR-0008, decision A). The F11 prototype and v0.1-S15 show it that way.

Errors:

| Error | When |
| --- | --- |
| `ValueError` | `IsoWeek.of` gets a date from 27 to 31 December 9999 (2.1). For `None` and `this`, that is a `today` in those days. For `next`, it is a `today` from 20 to 24 December 9999. |
| `OverflowError` | `text` is `next`, and `today` is on or after 25 December 9999, so `today + timedelta(days=7)` is after the last date of `datetime.date`. |

The PC's clock gives no such date, so only a wrong call gets these errors.

- Side effects: None
- Performance target: None

Example:

```python
from datetime import date

from recipe_menu.app import UsageError
from recipe_menu.lang import Lang
from recipe_menu.menus import NOT_A_WEEK, IsoWeek, week_from_argument

today = date(2026, 11, 10)
assert week_from_argument(None, today) == IsoWeek(2026, 46)
assert week_from_argument("this", today) == IsoWeek(2026, 46)
assert week_from_argument("next", today) == IsoWeek(2026, 47)
assert week_from_argument("2026-W47", today) == IsoWeek(2026, 47)
assert week_from_argument("2026-W53", today) == IsoWeek(2026, 53)
assert week_from_argument("next", date(2026, 12, 30)) == IsoWeek(2027, 1)
assert week_from_argument("2026-W99", today) is None
assert week_from_argument("Next", today) is None
assert week_from_argument("", today) is None

error = UsageError(NOT_A_WEEK, None, week="2026-W99")
assert error.text(Lang.EN) == (
    '"2026-W99" is not a week. Write an ISO week such as 2026-W47, "this", or "next".'
)
chinese = error.text(Lang.ZH)
assert chinese == "“2026-W99”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。"

week_from_argument("next", date(9999, 12, 20))  # raises ValueError
```

### 2.8 `list_menu_weeks`

- Module: menus
- Purpose: Lists the weeks that have a menu file in `menus/`, from the file names, without reading any file ([architecture 8](../../architecture.md#8-naming-and-coding-rules)). F07 counts and reads the menus of these weeks, and F11, F13, and F14 look for a week among them.

Signature:

```python
def list_menu_weeks(folder: DataFolder) -> tuple[tuple[IsoWeek, ...], tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |

- Return value: A pair `(weeks, problems)`.
  - A menu file is an entry of `menus/` whose name ends with `.toml`, in these small letters, as `list_toml_files` gives it (F04 design 3.1). Every other entry, such as `notes.txt` or `2026-W47.toml.bak`, is not a menu file and gives no problem. An entry such as `2026-W48.TOML`, whose `.toml` ending has a capital letter, is not a menu file either, and `list_toml_files` gives an error for it.
  - `weeks` holds the week of each menu file whose name without `.toml` `IsoWeek.parse` reads (2.1). They are in the order of time, which is also the order of the names.
  - `problems` holds the problems that `list_toml_files` gives, and then the error `NOT_A_WEEK_NAME` for each other menu file, in the order of the names. Such a file is `2026-w47.toml`, `2026-W99.toml`, or `plan.toml`. Each problem's file is its entry, such as `menus\2026-w47.toml` on Windows, and it has no place. A name with a problem is not in `weeks`, so no reader reads its file.
  - When `menus/` is missing, is a file, or cannot be read, `list_toml_files` gives no names and one problem, with the file `menus` and no place. So `weeks` is empty, and `problems` holds only that problem.

The message of `list_menu_weeks` is this. It does not show the name, because the problem's file names it on the line above the message, as for F04's `NOT_A_RECIPE_ID`.

| Name | English | Chinese |
| --- | --- | --- |
| `NOT_A_WEEK_NAME` | `This file name is not an ISO week such as 2026-W47. Rename the file.` | `这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。` |

Errors: None. `list_menu_weeks` never raises for bad data.

- Side effects: Lists `menus/` through `list_toml_files`. It reads no file and writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` ([architecture 10](../../architecture.md#10-test-setup)).

```python
import shutil
from pathlib import Path

from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, list_menu_weeks

assert list_menu_weeks(folder) == ((IsoWeek(2026, 47),), ())

for name in ["2026-W53.toml", "2027-W01.toml", "2026-w48.toml", "2026-W99.toml", "2026-W49.TOML"]:
    (folder.menus / name).write_text("", encoding="utf-8")
(folder.menus / "notes.txt").write_text("Ideas\n", encoding="utf-8")
weeks, problems = list_menu_weeks(folder)
assert weeks == (IsoWeek(2026, 47), IsoWeek(2026, 53), IsoWeek(2027, 1))
names = [problem.file.name for problem in problems]
assert names == ["2026-W49.TOML", "2026-W99.toml", "2026-w48.toml"]
assert all(problem.place is None for problem in problems)
assert problems[2].text(Lang.ZH) == "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。"

shutil.rmtree(folder.menus)
weeks, problems = list_menu_weeks(folder)
assert weeks == ()
assert [problem.file for problem in problems] == [Path("menus")]
assert problems[0].text(Lang.EN) == "The folder is missing."
```

### 2.9 `read_week_menu`

- Module: menus
- Purpose: Reads the menu file of one week into a `WeekMenu`, and reports each problem with its place ([requirements 4](../../requirements.md#4-features), F06). `menu show`, `shop`, and `menu suggest` call it for their week, and `check` calls it for every week of `list_menu_weeks`. `check` shows every problem (F07). Every other command stops at the first error (architecture 6).

Signature:

```python
def read_week_menu(
    folder: DataFolder,
    week: IsoWeek,
    settings: Settings | None,
    recipe_ids: frozenset[str],
) -> tuple[WeekMenu | None, tuple[Problem, ...]]: ...
```

Parameters:

| Name | Type | Meaning | Constraints |
| --- | --- | --- | --- |
| `folder` | `DataFolder` | The data folder. | None |
| `week` | `IsoWeek` | The week of the file, such as `2026-W47`. | A week that `list_menu_weeks` gave. `read_week_menu` reads `folder.menu_file(str(week))` and does not list the folder. On Windows, a file named `2026-w47.toml` would also open for `2026-W47`. Taking the week from `list_menu_weeks`, which compares names exactly, keeps Windows and Linux alike. |
| `settings` | `Settings` or `None` | The meals of each day and the servings of a dish that gives none (F05 design 2.2). | `None` when the settings could not be read. Then `read_week_menu` checks only what does not depend on the settings (choice 3). |
| `recipe_ids` | A `frozenset` of `str` | The recipe IDs that a dish may name. | The IDs that `list_recipe_ids` gave (F04 design 2.5). |

- Return value: A pair `(menu, problems)`.
  - `menu` is `None` when `settings` is `None`, or when `problems` holds an error. Otherwise it is a `WeekMenu` with the week `week`, the meals `settings.meals`, and one slot for each day and each of those meals. A slot holds the dishes of its meal's list, in the file's order, or no dish when the file lacks the day or the meal. Each dish has its ID without whitespace at both ends, and the servings of its `servings`, or `settings.servings` when it gives none. A meal such as `breakfast = []` that the settings do not name is not in the menu.
  - `problems` holds the problem of `read_toml` alone, when the file is missing, cannot be read, is not UTF-8, or is not valid TOML (F03 design 2.3). Otherwise it holds the problems of the checks below, in their order. Each problem has the file `menus/<week>.toml`, such as `menus\2026-W47.toml` on Windows. When `list_menu_weeks` gave the week, only a file that was deleted or renamed since then gives `FILE_MISSING`. Every problem is an error.

The file has the layout of `docs/prototypes/example-data.md`. Here, Tuesday to Saturday are left out:

```toml
# 2026-W47: 16 to 22 November 2026
week = "2026-W47"

[monday]
lunch = []
dinner = ["tomato-egg", "choy-sum", "rice"]

[sunday]
lunch = []
dinner = [
  { recipe = "cola-wings", servings = 4 },
  { recipe = "choy-sum", servings = 4 },
  { recipe = "rice", servings = 4 },
]
```

The meals in use are `settings.meals`, or all three meals of `Meal` when `settings` is `None`. Each table of the file has these keys, in this order:

| Table | Keys | Required |
| --- | --- | --- |
| The top of the file | `week`, then the days `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, and `sunday`, the values of `Day` | `week`. A day that the file lacks holds no dishes. |
| A day | The meals in use, by the values of `Meal`. Each one is a list of dishes. | None. A meal in use that the day lacks holds no dishes. |
| A dish in braces | `recipe` and `servings` | `recipe`. Without `servings`, the dish gets `settings.servings`. |

An item of a meal's list is a dish: a recipe ID in quotation marks, or a table in braces. The places of the problems are these. N counts the dishes of a meal from 1, skipped items included, so it is the number that you count in the file.

| Place | English | Chinese |
| --- | --- | --- |
| `week` | `week` | `周次` |
| A day | The day's `label`, such as `Monday` | `周一` |
| A key of a day that is the value of a `Meal` | The day's `label` and the meal's `label`, such as `Monday dinner` | `周一晚餐` |
| Any other key of a day | The day's `label` and the key as the file writes it, such as `Friday supper` | `周五 supper` |
| Dish N of a meal | The meal of the day and N, such as `Sunday dinner, dish 1` | `周日晚餐，菜品 1` |

"The meal of the day" below is the third row, and "the key of the day" is the third or the fourth row.

`read_week_menu` makes these checks. A check whose part has a value of the wrong kind, such as a day that is not a table, is the only check of that part. Every other part is still checked, so one run reports every problem of the file. The checks of a meal and of its dishes apply to each key of a day that names a meal in use. A key that gets `UNKNOWN_MEAL` or `UNKNOWN_KEY` is not checked further.

| Part | Check | Problem | Place | Kind |
| --- | --- | --- | --- | --- |
| `week` | The key is missing. | `MISSING_KEY` | None | Error |
| `week` | The value is not a text. | `NOT_A_TEXT` | `week` | Error |
| `week` | The text is empty or holds only whitespace. | `EMPTY_TEXT` | `week` | Error |
| `week` | Without whitespace at both ends, `IsoWeek.parse` gives `None` for the text, such as `2026-w47` or `next`. | `WEEK_NOT_ISO` | `week` | Error |
| `week` | The text names a week other than the file name's, such as `2026-W48` in `2026-W47.toml`. | `WEEK_NOT_FILE_NAME` | `week` | Error |
| A day | The value is not a table, such as `monday = []`. | `NOT_A_DAY_TABLE` | The day | Error |
| A key of a day | `settings` is not `None`, and the key names no meal of `settings.meals`, such as `supper`, `Dinner`, or `breakfast` when the settings name lunch and dinner. A key that is the value of a `Meal` and holds the empty list `[]` gets no problem. | `UNKNOWN_MEAL` | The key of the day | Error |
| A key of a day | `settings` is `None`, and the key is not the value of a `Meal`, such as `supper` or `Dinner`. | `UNKNOWN_KEY` | The key of the day | Error |
| A meal | The value is not a list. | `NOT_A_LIST` | The meal of the day | Error |
| A dish | The item is neither a text nor a table. | `NOT_A_DISH` | Dish N | Error |
| A dish | The item is a text that is empty or holds only whitespace. | `EMPTY_ITEM` | Dish N | Error |
| A dish | The item is a table, and `recipe` is missing, is not a text, or is empty or holds only whitespace. | `MISSING_KEY`, `NOT_A_TEXT`, or `EMPTY_TEXT` | Dish N | Error |
| A dish | The recipe ID breaks the rule of `is_recipe_id`, such as `Rice`, or `recipe_ids` does not hold it. The ID is the text, or the text of `recipe`, without whitespace at both ends. | `UNKNOWN_RECIPE` | The meal of the day | Error |
| A dish | The item is a table with `servings`, and the value breaks the rule of `read_servings` (F05 design 3.1). | `SERVINGS_NOT_A_NUMBER`, `SERVINGS_TOO_FEW`, or `SERVINGS_TOO_MANY` | Dish N | Error |
| A dish | The item is a table with a key other than `recipe` and `servings`. | `UNKNOWN_KEY` | Dish N | Error |
| The top of the file | A key other than the eight of the table of keys. | `UNKNOWN_KEY` | None | Error |

The place of `UNKNOWN_RECIPE` is the meal of the day, as the F07 prototype shows, because the message names the recipe. The other problems of a dish are at dish N.

The problems come in this order:

1. The problems of `week`.
2. The days, in the order Monday to Sunday. A day gives its own problem, or the problems of its keys in the file's order. A meal gives its list's own problem, or the problems of each dish in order. A dish gives its own problem or the problems of its recipe ID, then those of `servings`, and then its unknown keys in the file's order.
3. The other keys of the top of the file, in the file's order.

`read_week_menu` uses the messages of `datafile` for the shape of a file (F03 design 2.10), and those of `read_servings` for the servings. It picks the form of `UNKNOWN_KEY` by the number of keys: eight at the top of the file, three in a day when `settings` is `None`, and two in a dish. These are the messages of `menus`. A placeholder is a name in braces, such as `{week}`. The braces of `{ ... }` in `NOT_A_DISH` are part of the text, so its templates write each brace twice (F02 design 2.2).

| Name | English | Chinese |
| --- | --- | --- |
| `WEEK` | `week` | `周次` |
| `DAY_MEAL` | `{day} {meal}` | `{day}{meal}` |
| `DAY_KEY` | `{day} {key}` | `{day} {key}` |
| `DISH_N` | `{place}, dish {number}` | `{place}，菜品 {number}` |
| `WEEK_NOT_ISO` | `"week" must be an ISO week such as 2026-W47, not "{week}".` | `“week”必须是 2026-W47 这样的 ISO 周，不能是“{week}”。` |
| `WEEK_NOT_FILE_NAME` | `The file name says {name}, but the file says {week}.` | `文件名是 {name}，但文件里写的是 {week}。` |
| `NOT_A_DAY_TABLE` | `"{key}" must be a table. Write the line [{key}], and below it a list of dishes for each meal, such as dinner = ["tomato-egg"].` | `“{key}”必须是表。请写一行 [{key}]，在它下面为每一餐写一个菜的列表，比如 dinner = ["tomato-egg"]。` |
| `UNKNOWN_MEAL` | `Unknown meal "{meal}". The settings name {meals}.` | `未知餐次“{meal}”。设置里的餐次：{meals}。` |
| `NOT_A_DISH` | `A dish must be a recipe ID in quotation marks, such as "tomato-egg", or a table in braces, such as { recipe = "tomato-egg", servings = 4 }.` | `一道菜必须是放在引号里的菜谱 ID，比如 "tomato-egg"，或者是放在花括号里的表，比如 { recipe = "tomato-egg", servings = 4 }。` |
| `UNKNOWN_RECIPE` | `Unknown recipe "{recipe}".` | `未知菜谱“{recipe}”。` |

The values of the placeholders are these:

| Placeholder | Value |
| --- | --- |
| `day` | The day's `label` (2.3), in `DAY_MEAL` and `DAY_KEY`. |
| `meal` | The meal's `label` (F05 design 2.1) in `DAY_MEAL`. The key as the file writes it in `UNKNOWN_MEAL`. |
| `place` | The meal of the day, from `DAY_MEAL`. |
| `number` | N, the number of the dish. |
| `key` | The key as the file writes it. The other key of a day in `DAY_KEY`. `week` or `recipe` in `MISSING_KEY`, `NOT_A_TEXT`, and `EMPTY_TEXT`. The day in `NOT_A_DAY_TABLE`. The meal in `NOT_A_LIST`. The unknown key in `UNKNOWN_KEY`. |
| `keys` | `and_list` of the keys that the table may have, in the order of the table of keys. At the top of the file, "week, monday, tuesday, wednesday, thursday, friday, saturday, and sunday". In a day when `settings` is `None`, "breakfast, lunch, and dinner". In a dish, "recipe and servings" and "recipe 和 servings". |
| `week` | The text of `week` without whitespace at both ends. In `WEEK_NOT_FILE_NAME`, it is an ISO week. |
| `name` | `str(week)` of the parameter `week`, which is the week of the file name. |
| `meals` | `and_list` of the values of `settings.meals`, in their order, such as "lunch and dinner" and "lunch 和 dinner". The Chinese text lists the English words too, because the file needs them, as F05's `UNKNOWN_MEAL` does. |
| `recipe` | The recipe ID without whitespace at both ends. |
| `servings` | The value of `servings`, as `read_servings` gives it (F05 design 3.1). |

The F07 prototype and scenarios v0.1-S05 and v0.1-S07 show four of these problems. `menus\2026-W47.toml, Monday dinner` gets `Unknown recipe "tomato-eggs".`. With the mistakes of v0.1-S07, `menus\2026-W47.toml, week` gets `The file name says 2026-W47, but the file says 2026-W48.`, `menus\2026-W47.toml, Friday supper` gets `Unknown meal "supper". The settings name lunch and dinner.`, and `menus\2026-W47.toml, Sunday dinner, dish 1` gets `Servings must be a whole number of 1 or more, not 0.`.

Errors: None. `read_week_menu` never raises for bad data. `str(week)` is always a valid name, so `DataFolder.menu_file` never raises.

- Side effects: Reads `menus/<week>.toml` through `read_toml`. It lists no folder and writes nothing.
- Performance target: None

Example:

In this example, `folder` is a `DataFolder` on a fresh copy of the example data folder `tests/data/example/` (architecture 10). The third run makes Monday dinner name `tomato-eggs`, as in the F07 prototype. The fourth run starts again from the example file and makes the three menu mistakes of v0.1-S07. The file of `lines` then has a mistake in nearly every part.

```python
from pathlib import Path

from recipe_menu.datafile import Severity
from recipe_menu.lang import BiText, Lang
from recipe_menu.menus import Day, Dish, IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Meal, Settings, read_settings

settings, _ = read_settings(folder)
ids, _ = list_recipe_ids(folder)
recipe_ids = frozenset(ids)
week = IsoWeek(2026, 47)
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert problems == ()
assert menu is not None
assert menu.week == week
assert menu.meals == (Meal.LUNCH, Meal.DINNER)
assert len(menu.slots) == 14
monday = (Dish("tomato-egg", 2), Dish("choy-sum", 2), Dish("rice", 2))
assert menu.dishes(Day.MONDAY, Meal.DINNER) == monday
assert menu.dishes(Day.SUNDAY, Meal.DINNER)[0] == Dish("cola-wings", 4)
assert sum(1 for slot in menu.slots if slot.dishes) == 4
assert sum(len(slot.dishes) for slot in menu.slots) == 9

every_meal = Settings(Lang.EN, tuple(Meal), 3)
menu, problems = read_week_menu(folder, week, every_meal, recipe_ids)
assert problems == ()
assert menu is not None
assert menu.dishes(Day.MONDAY, Meal.BREAKFAST) == ()
assert menu.dishes(Day.MONDAY, Meal.DINNER)[0] == Dish("tomato-egg", 3)
assert read_week_menu(folder, week, None, recipe_ids) == (None, ())

file = folder.menu_file("2026-W47")
text = file.read_text(encoding="utf-8")
file.write_text(text.replace('"tomato-egg"', '"tomato-eggs"'), encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert [problem.file for problem in problems] == [Path("menus", "2026-W47.toml")]
assert problems[0].place == BiText("Monday dinner", "周一晚餐")
assert problems[0].text(Lang.EN) == 'Unknown recipe "tomato-eggs".'
assert problems[0].text(Lang.ZH) == "未知菜谱“tomato-eggs”。"

text = text.replace('week = "2026-W47"', 'week = "2026-W48"')
text = text.replace("[friday]\n", "[friday]\nsupper = []\n")
text = text.replace('"cola-wings", servings = 4', '"cola-wings", servings = 0')
file.write_text(text, encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert [problem.place for problem in problems] == [
    BiText("week", "周次"),
    BiText("Friday supper", "周五 supper"),
    BiText("Sunday dinner, dish 1", "周日晚餐，菜品 1"),
]
assert problems[0].text(Lang.EN) == "The file name says 2026-W47, but the file says 2026-W48."
assert problems[1].text(Lang.EN) == 'Unknown meal "supper". The settings name lunch and dinner.'
assert problems[1].text(Lang.ZH) == "未知餐次“supper”。设置里的餐次：lunch 和 dinner。"
assert problems[2].text(Lang.EN) == "Servings must be a whole number of 1 or more, not 0."
menu, problems = read_week_menu(folder, week, None, recipe_ids)
assert len(problems) == 3
english = problems[1].text(Lang.EN)
assert english == 'Unknown key "supper". The keys are breakfast, lunch, and dinner.'

lines = [
    "week = 2026",
    "wednesday = []",
    "[monday]",
    'lunch = "rice"',
    'dinner = ["Rice", 3, " ", { recipe = "rice", servings = 0x' + "f" * 5000 + ", note = 1 }]",
    "breakfast = []",
    "[tuesday]",
    'breakfast = ["rice"]',
    "[funday]",
]
file.write_text("\n".join(lines) + "\n", encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert menu is None
assert all(problem.severity is Severity.ERROR for problem in problems)
assert [problem.place for problem in problems] == [
    BiText("week", "周次"),
    BiText("Monday lunch", "周一午餐"),
    BiText("Monday dinner", "周一晚餐"),
    BiText("Monday dinner, dish 2", "周一晚餐，菜品 2"),
    BiText("Monday dinner, dish 3", "周一晚餐，菜品 3"),
    BiText("Monday dinner, dish 4", "周一晚餐，菜品 4"),
    BiText("Monday dinner, dish 4", "周一晚餐，菜品 4"),
    BiText("Tuesday breakfast", "周二早餐"),
    BiText("Wednesday", "周三"),
    None,
]
assert problems[0].text(Lang.EN) == '"week" must be a text in quotation marks.'
assert problems[1].text(Lang.EN) == '"lunch" must be a list in square brackets, [ ... ].'
assert problems[2].text(Lang.EN) == 'Unknown recipe "Rice".'
assert problems[3].text(Lang.EN).startswith("A dish must be a recipe ID in quotation marks,")
assert problems[4].text(Lang.EN) == "This item is empty."
assert problems[5].text(Lang.EN) == "Servings must be a whole number from 1 to 100, such as 2."
assert problems[6].text(Lang.EN) == 'Unknown key "note". The keys are recipe and servings.'
assert problems[7].text(Lang.EN).startswith('Unknown meal "breakfast". The settings name')
assert problems[8].text(Lang.EN).startswith('"wednesday" must be a table.')
assert problems[9].text(Lang.EN).startswith('Unknown key "funday". The keys are week, monday,')
_, problems = read_week_menu(folder, week, None, recipe_ids)
assert len(problems) == 9

file.write_text('week = " 2026-W47 "\n', encoding="utf-8")
menu, problems = read_week_menu(folder, week, settings, recipe_ids)
assert problems == ()
assert menu is not None
assert all(slot.dishes == () for slot in menu.slots)
file.write_text('week = "2026-w47"\n', encoding="utf-8")
_, problems = read_week_menu(folder, week, settings, recipe_ids)
english = problems[0].text(Lang.EN)
assert english == '"week" must be an ISO week such as 2026-W47, not "2026-w47".'
file.write_text("[monday]\ndinner = []\n", encoding="utf-8")
_, problems = read_week_menu(folder, week, settings, recipe_ids)
assert [problem.place for problem in problems] == [None]
assert problems[0].text(Lang.EN) == 'The key "week" is missing.'
menu, problems = read_week_menu(folder, IsoWeek(2026, 48), settings, recipe_ids)
assert menu is None
assert [problem.text(Lang.EN) for problem in problems] == ["The file is missing."]
```

## 3. Changes to existing interfaces

None. No interface that F01 to F05 implemented changes. Each exported name keeps its signature and its behavior, and the tests of F01 to F05 pass unchanged. F06 adds the module `menus` and changes no file of another module.

F06 uses these interfaces as their designs give them, and changes none of them:

- F02's `BiText`, `Lang`, `Message`, and `and_list`.
- F03's `DataFolder`, `Problem`, `read_toml`, and the messages `EMPTY_ITEM`, `EMPTY_TEXT`, `MISSING_KEY`, `NOT_A_LIST`, `NOT_A_TEXT`, and `UNKNOWN_KEY` of F03 design 2.10.
- F04's `list_toml_files`, `Report`, `read_text`, and `report_unknown_keys` in `datafile` (F04 design 3.1 and 3.2), and `is_recipe_id` in `recipes` (F04 design 2.4).
- F05's `Meal` and `Settings` in `settings` (F05 design 2.1 and 2.2), and `read_servings`, `MIN_SERVINGS`, and `MAX_SERVINGS` in `datafile` (F05 design 3.1).

## 4. Architect review

| Item | Result | Note |
| --- | --- | --- |
| Fits the module layout and the data model | Pass | `menus` is the domain module of architecture 3. It imports only `lang`, `text`, `datafile`, `settings`, and `recipes`, the five modules that its row allows, takes only `is_recipe_id` from `recipes`, and reaches the disk only through `list_toml_files` and `read_toml` (architecture 4 and 8). It owns what its row lists: ISO weeks, this week and next week (`IsoWeek` and `week_from_argument`), dates and day names in both languages (`date_range`, `short_date`, and `Day.label`), and reading week menu files with their problems. `IsoWeek`, `Dish`, and `WeekMenu` hold the fields of architecture 5.2. `Dish` gets the settings' servings when the file gives none, and `WeekMenu` holds the settings' meals and refers to recipes by ID only (5.3). `Day` and `MealSlot` are helper values, as `Severity`, `Steps`, and `FolderUse` are. The file has the layout of 5.1 and `example-data.md`, with lowercase English keys (architecture 8). `read_week_menu` takes a `Settings` or `None`, as `read_recipe` takes a `Catalog` or `None`, and architecture 8 allows a `frozenset` of IDs to cross modules. `NOT_A_WEEK` belongs in `menus` (choice 8). Its text describes the forms that `week_from_argument` reads, `menus` cannot raise `UsageError` because `app` is in a higher layer, and `shop` may not import `menu`. `datafile` and `text` already export messages. Choice 5 fits requirements 3: every `WeekMenu` has the seven days and the settings' meals, and only the file may leave out what holds no dish. Note 1, not blocking: architecture 8 makes every text that the user sees a `Message`, and 2.2 names only the four templates as messages. The day labels, the short English day names, and the month names are such texts too, so they also go in `menus/messages.py`, as the labels of `Meal` are in `settings/messages.py`. Note 2, not blocking: the performance rule of section 2 speaks of "one week of 63 dishes", but requirements 7.1 gives no number of dishes. It can say "one week menu". |
| Follows the error handling and naming conventions | Pass | Readers return their problems and never raise for bad data (architecture 6). The only exceptions come from wrong calls: the constructors of 2.1 and 2.3 to 2.6, `WeekMenu.dishes`, and `week_from_argument` near the last date of `datetime.date`. `read_week_menu` builds its path only from `str(week)`, which `DataFolder.menu_file` always accepts, so no dish ever reaches a path (F03 design 2.1). Each problem names `menus/<week>.toml` relative to the data folder, and a field such as `Monday dinner` as its place, as the F07 prototype shows. A syntax mistake gets only the problem of `read_toml`, with its line. A wrong week on the command line is a `UsageError` that the command raises with no hint, as ADR-0008 (decision A), the F11 prototype, and v0.1-S15 have it. No message meets F02's limit of 4,300 digits: servings go through `read_servings` with its 15-digit limit, the text of `week` goes in as a text, and N, days, and years are small. Every message is an UPPER_SNAKE constant in `menus/messages.py` with both languages, and the names follow PEP 8 (architecture 8). Every placeholder value is a `str`, an `int`, or a `BiText`. The design passes `Day.label`, `Meal.label`, and `and_list` of each meal's value, never an enum member, which `Message.render` and `and_list` reject. The Architect weighed the three points that the Interface Designer raised. (a) Choice 5 holds. A missing day or meal holds no dishes, so a menu that you wrote before you added a meal stays correct. `breakfast = []` for a meal that the settings do not name gives no problem, so a menu that you wrote before you removed a meal stays correct too. A meal with dishes that the settings do not name stays an error, because `menu show` and `shop` would leave its dishes out. (b) `UNKNOWN_KEY` with no settings is acceptable. It shows only when `settings.toml` has an error, which F07 reports too, and its text is true. A copy of the text of `UNKNOWN_MEAL` in `settings` would keep the word "meal", at the cost of one more message. (c) The three new Chinese places follow the project's patterns. `周次` names a key, as `餐次` and `份数` do. `周五 supper` puts a space between Chinese and Latin text, as `食材 3` does. `周日晚餐，菜品 1` mirrors `Sunday dinner, dish 1`. Note 3, optional: `周日晚餐第 1 道菜` would use the word 道菜 of the prototypes, as in `9 道菜` and `每道菜`, and avoid a second "，" after the one that follows the file. Troy sees these texts when Troy approves the design (R18, with `troy_approves_first = 16`). For the Developer: with no settings, each unknown key of a day has its own place, so the reader adds `UNKNOWN_KEY.pick(3)` through `Report.add`, because `report_unknown_keys` gives one place to every key. |
| Does not duplicate an existing interface | Pass | `menus` is new and rewrites nothing that exists. It lists `menus/` with `list_toml_files` and passes its problems on, as `list_recipe_ids` does, so `TOML_ENDING_NOT_SMALL` stays in `datafile` (F04 design 3.1). It reads files with `read_toml`, texts with `read_text`, and servings with `read_servings`, so the range 1 to 100 and its three messages stay in one place (F05 design, choice 3). It checks IDs with `is_recipe_id`, and it reports the shape of the file with the messages of F03 design 2.10. Its new messages say what the shared ones cannot. A day is a `[table]` line, so `NOT_A_DAY_TABLE` takes the place of `NOT_A_TABLE`, which asks for braces. A dish may be a text or a table, so `NOT_A_DISH` takes the place of `ITEM_NOT_A_TEXT`. `UNKNOWN_MEAL` repeats a name that `settings` keeps internal, with the different text of the F07 prototype. Architecture 8 has each module keep its own messages, as F04 did with `UNKNOWN_INGREDIENT`. The check of `WeekMenu.meals` repeats the internal `_check_meals` of `settings`. It is a few lines, and a copy is better than a new export from an implemented module. Note 4, not blocking: the line `There is no menu for 2026-W48. Run "recipe-menu menu new 2026-W48" to create it.` is the same in the F11 and F13 prototypes, and `shop` may not import `menu`. That is choice 8's reason for `NOT_A_WEEK`. If `menus` does not export the line now, F11's design must add it to `menus`, which architecture 3 gives to F06 alone, or `menu` and `shop` must each keep a copy. The Architect recommends that `menus` export it now, for example as `NO_MENU` with `{week}`, with a Chinese text that Troy approves with this design. |
| Depends only on features earlier in the order | Pass | F06 uses `lang` and `text` from F02, `datafile` from F03 with what F04 and F05 added to it, `is_recipe_id` from F04, and `Meal`, `Settings`, and `read_servings` from F05. All four features come before F06 and pass their tests on main. F04 and F05 are the soft dependencies of the F06 row, and F02 and F03 come in through the shared modules that F04 and F05 also use. The plans for F07, F08, and F11 to F14 in section 2 say what each later feature is meant to call and leave the rest to its design, so they bind no later design. The interfaces need only the standard library, so R16 has no new dependency to review. `docs/rules.md` has no P rule of type Review for the Architect. |
| Adds no hidden coupling between modules | Pass | Each assumption between modules is written in the design. `read_week_menu` opens one file and lists no folder. So its caller passes a week from `list_menu_weeks`, which compares names exactly and keeps Windows and Linux alike, and the IDs from `list_recipe_ids` (choices 1 and 4, and the parameters of 2.9). F07 passes the settings that `read_settings` gave, not `context.settings` (choice 3). F11's `menu new` must write a file that `read_week_menu` reads with no problem and with every slot empty. `NOT_A_WEEK`, `week_from_argument`, and the help's note on weeks in F05 name the same three forms, and 2.7 says so, so a change to the forms changes all three. `list_toml_files` sorts its names, so `weeks` and the problems do not depend on the order of the file system. Note 5, not blocking, for F14: a `WeekMenu` does not say whether the file holds the key of an empty slot, or its day table (choice 5). F14 fills empty meals and keeps the rest of the file as it is, so it must add a missing meal key or day table. F14's design decides how. |
| Changes an implemented interface only through the change flow | Pass | Section 3 rightly says None. The PR adds only the two design files, and `src/recipe_menu/menus/` does not exist yet. Every name that F06 uses exists on the branch with the signature that the design gives: `list_toml_files`, `Report`, `read_text`, `report_unknown_keys`, `read_servings`, and the shape messages in `recipe_menu.datafile`, `is_recipe_id` in `recipes`, `Meal` and `Settings` in `settings`, and `Message`, `Plural`, and `and_list` in `text`. So no exported name of F01 to F05 changes, and their tests are not affected. Notes for the next stages: the mock defines every constant, so a test that checks only a constant, such as the text of `NOT_A_WEEK` or a `Day` label, passes against the mock and breaks R09, as section 2 says. With its doc comments, the mock PR may pass R03's 500 lines in its five files, so the main session plans a soft-limit reason, as for F04 and F05. |

| Round | Issue | Resolution |
| --- | --- | --- |
| 1 | No blocking issue. The Architect checked the eight choices against the requirements, the architecture, ADR-0008, the F07 and F11 prototypes, and v0.1-S05, v0.1-S07, and v0.1-S15. Choices 1 to 4, 6, and 8 settle the seven review notes of the brief. Choice 5 and the three new Chinese places need no change to a requirement, the architecture, or a prototype. Each file has 19 code blocks, each equal to its mirror, and the headings and table rows of the two files match line for line. The 18 `python` blocks parse, and `ruff format --check` with ruff 0.17.4 and the project's settings reports them formatted. On the F01 to F05 code of the branch, the Architect built a model of section 2 and ran the 9 examples on fresh copies of `tests/data/example/`, with Python 3.13.18 on Windows. Every assertion and all 18 `# raises` hold. The model read 3,000 random menu files with the example settings, with no settings, with all three meals, and with dinner only, and it raised no exception. No test ran, because the PR changes no code. Notes 1 to 5 do not block. | Approved. The Interface Designer can settle notes 1 to 5 in a revision, or leave them. Troy approves the design with its new Chinese texts (R18, with `troy_approves_first = 16`). |

## 5. Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-11-12 | First draft. |
| 1.0 | 2026-11-12 | Approved by Troy. |
