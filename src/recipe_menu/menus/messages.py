"""The messages of ``menus``: dates, day names, places, and the problems of menu files.

Only ``NOT_A_WEEK`` is exported from the package, for the commands. Every other message is
internal to the module. The other problems of a menu file use the messages of ``datafile``.
"""

from typing import Final

from recipe_menu.text import Message

# The message of the ``UsageError`` for a wrong week on the command line.
NOT_A_WEEK: Final[Message] = Message(
    '"{week}" is not a week. Write an ISO week such as 2026-W47, "this", or "next".',
    "“{week}”不是一个周。请写 2026-W47 这样的 ISO 周，或者写“this”或“next”。",
)

# The name of a file in ``menus/`` that is not an ISO week.
NOT_A_WEEK_NAME: Final[Message] = Message(
    "This file name is not an ISO week such as 2026-W47. Rename the file.",
    "这个文件名不是 2026-W47 这样的 ISO 周。请给文件改名。",
)

# The names of the days, Monday to Sunday: the label in a place, and the short name in English.
MONDAY_LABEL: Final[Message] = Message("Monday", "周一")
TUESDAY_LABEL: Final[Message] = Message("Tuesday", "周二")
WEDNESDAY_LABEL: Final[Message] = Message("Wednesday", "周三")
THURSDAY_LABEL: Final[Message] = Message("Thursday", "周四")
FRIDAY_LABEL: Final[Message] = Message("Friday", "周五")
SATURDAY_LABEL: Final[Message] = Message("Saturday", "周六")
SUNDAY_LABEL: Final[Message] = Message("Sunday", "周日")
MONDAY_SHORT: Final[Message] = Message("Mon", "周一")
TUESDAY_SHORT: Final[Message] = Message("Tue", "周二")
WEDNESDAY_SHORT: Final[Message] = Message("Wed", "周三")
THURSDAY_SHORT: Final[Message] = Message("Thu", "周四")
FRIDAY_SHORT: Final[Message] = Message("Fri", "周五")
SATURDAY_SHORT: Final[Message] = Message("Sat", "周六")
SUNDAY_SHORT: Final[Message] = Message("Sun", "周日")

# The month names of ``date_range``, January to December: the English name and the Chinese number.
# They stay tuples, not 24 constants: the implementation indexes them by ``month - 1``.
MONTH_NAMES: Final[tuple[Message, ...]] = (
    Message("January", "1"),
    Message("February", "2"),
    Message("March", "3"),
    Message("April", "4"),
    Message("May", "5"),
    Message("June", "6"),
    Message("July", "7"),
    Message("August", "8"),
    Message("September", "9"),
    Message("October", "10"),
    Message("November", "11"),
    Message("December", "12"),
)

# The month names of ``short_date``, January to December.
SHORT_MONTH_NAMES: Final[tuple[Message, ...]] = (
    Message("Jan", "1"),
    Message("Feb", "2"),
    Message("Mar", "3"),
    Message("Apr", "4"),
    Message("May", "5"),
    Message("Jun", "6"),
    Message("Jul", "7"),
    Message("Aug", "8"),
    Message("Sep", "9"),
    Message("Oct", "10"),
    Message("Nov", "11"),
    Message("Dec", "12"),
)

# The dates of a week: Monday and Sunday in one month, in two months, and in two years.
RANGE_ONE_MONTH: Final[Message] = Message(
    "{first} to {last} {month} {year}",
    "{year}年{month}月{first}日至{last}日",
)
RANGE_TWO_MONTHS: Final[Message] = Message(
    "{first} {first_month} to {last} {last_month} {year}",
    "{year}年{first_month}月{first}日至{last_month}月{last}日",
)
RANGE_TWO_YEARS: Final[Message] = Message(
    "{first} {first_month} {first_year} to {last} {last_month} {last_year}",
    "{first_year}年{first_month}月{first}日至{last_year}年{last_month}月{last}日",
)
SHORT_DATE: Final[Message] = Message(
    "{weekday} {day} {month}",
    "{weekday} {month}月{day}日",
)

# The places in a menu file. ``DISH_N`` names the dish N of a meal, counted from 1.
WEEK: Final[Message] = Message("week", "周次")
DAY_MEAL: Final[Message] = Message("{day} {meal}", "{day}{meal}")
DAY_KEY: Final[Message] = Message("{day} {key}", "{day} {key}")
DISH_N: Final[Message] = Message(
    "{place}, dish {number}",
    "{place}，菜品 {number}",
)

# The problems of a menu file that ``datafile`` has no message for.
WEEK_NOT_ISO: Final[Message] = Message(
    '"week" must be an ISO week such as 2026-W47, not "{week}".',
    "“week”必须是 2026-W47 这样的 ISO 周，不能是“{week}”。",
)
WEEK_NOT_FILE_NAME: Final[Message] = Message(
    "The file name says {name}, but the file says {week}.",
    "文件名是 {name}，但文件里写的是 {week}。",
)
NOT_A_DAY_TABLE: Final[Message] = Message(
    '"{key}" must be a table. Write the line [{key}], and below it a list of dishes for each '
    'meal, such as dinner = ["tomato-egg"].',
    "“{key}”必须是表。请写一行 [{key}]，"
    "在它下面为每一餐写一个菜的列表"
    '，比如 dinner = ["tomato-egg"]。',
)
UNKNOWN_MEAL: Final[Message] = Message(
    'Unknown meal "{meal}". The settings name {meals}.',
    "未知餐次“{meal}”。设置里的餐次：{meals}。",
)
NOT_A_DISH: Final[Message] = Message(
    'A dish must be a recipe ID in quotation marks, such as "tomato-egg", or a table in braces, '
    'such as {{ recipe = "tomato-egg", servings = 4 }}.',
    "一道菜必须是放在引号里的菜谱 ID，"
    '比如 "tomato-egg"，或者是放在花括号里的表，'
    '比如 {{ recipe = "tomato-egg", servings = 4 }}。',
)
UNKNOWN_RECIPE: Final[Message] = Message(
    'Unknown recipe "{recipe}".',
    "未知菜谱“{recipe}”。",
)
