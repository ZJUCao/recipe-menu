"""The messages of ``datafile``: the places in a file, the read errors, and the shape of a file.

Only the eight messages for the shape of a file are exported by ``recipe_menu.datafile``. The
others, the read errors, the folder listing, and the servings, are internal to the module, for
``read_toml``, ``list_toml_files``, and ``read_servings``.
"""

from typing import Final

from recipe_menu.text import Message, Plural

# The place of every problem that has a line.
LINE: Final[Message] = Message("line {line}", "第 {line} 行")

# Why a file cannot be read, from the first step of ``read_toml``.
FILE_MISSING: Final[Message] = Message("The file is missing.", "文件不存在。")
FILE_IS_FOLDER: Final[Message] = Message(
    "The file cannot be read: it is a folder.",
    "无法读取文件：它是一个文件夹。",
)
ACCESS_DENIED: Final[Message] = Message(
    "The file cannot be read: access is denied.",
    "无法读取文件：没有访问权限。",
)
SYSTEM_ERROR: Final[Message] = Message(
    "The file cannot be read. The system says: {reason}",
    "无法读取文件。系统提示：{reason}",
)

# Why the text of a file cannot be read, from the second and the third step.
NOT_UTF8: Final[Message] = Message(
    "The file cannot be read: it is not UTF-8 text. Save it as UTF-8.",
    "无法读取文件：它不是 UTF-8 文本。请把它另存为 UTF-8。",
)
MISSING_BRACKET: Final[Message] = Message(
    'The file cannot be read: a closing "]" is missing.',
    "无法读取文件：缺少右方括号“]”。",
)
MISSING_BRACE: Final[Message] = Message(
    'The file cannot be read: a closing "}}" is missing. A table in braces must be on one line.',
    "无法读取文件：缺少右花括号“}}”。花括号里的表必须写在一行里。",
)
MISSING_QUOTE: Final[Message] = Message(
    "The file cannot be read: a closing quotation mark is missing.",
    "无法读取文件：缺少结尾的引号。",
)
BAD_VALUE: Final[Message] = Message(
    "The file cannot be read: a value is missing or not valid. "
    'Write a text in straight quotation marks, such as "Tomato".',
    '无法读取文件：缺少值，或者值写得不对。文字要放在英文双引号里，比如 "番茄"。',
)
MISSING_EQUALS: Final[Message] = Message(
    'The file cannot be read: an "=" is missing after a key.',
    "无法读取文件：键后面缺少“=”。",
)
BAD_KEY: Final[Message] = Message(
    "The file cannot be read: a key is missing or not valid. "
    "A table in braces must be on one line, and it cannot end with a comma.",
    "无法读取文件：缺少键，或者键写得不对。花括号里的表必须写在一行里，而且不能以逗号结尾。",
)
EXTRA_TEXT: Final[Message] = Message(
    "The file cannot be read: something follows the value on this line. "
    "Write one key and its value on each line.",
    "无法读取文件：这一行的值后面还有别的内容。每行只写一个键和它的值。",
)
BAD_LINE: Final[Message] = Message(
    'The file cannot be read: this line does not start with a key, "[", or "#".',
    "无法读取文件：这一行的开头不是键、“[”或“#”。",
)
DEFINED_TWICE: Final[Message] = Message(
    "The file cannot be read: a key or a table is defined twice.",
    "无法读取文件：同一个键或表定义了两次。",
)
BAD_ESCAPE: Final[Message] = Message(
    'The file cannot be read: a "\\" in a text does not start a valid escape. '
    'Write "\\\\" for one "\\", or put the text in single quotation marks.',
    "无法读取文件：文字里的“\\”没有构成有效的转义。一个“\\”要写成“\\\\”，或者把文字放在单引号里。",
)
CONTROL_CHARACTER: Final[Message] = Message(
    "The file cannot be read: this line holds a control character, which TOML does not allow.",
    "无法读取文件：这一行有 TOML 不允许的控制字符。",
)
NOT_TOML: Final[Message] = Message(
    "The file cannot be read: this line is not valid TOML.",
    "无法读取文件：这一行不是有效的 TOML。",
)
NUMBER_TOO_LONG: Final[Message] = Message(
    "The file cannot be read: a number has too many digits.",
    "无法读取文件：有一个数字的位数太多。",
)
NESTED_TOO_DEEPLY: Final[Message] = Message(
    "The file cannot be read: lists or tables are nested too deeply.",
    "无法读取文件：列表或表嵌套得太深。",
)

# The shape of a file, which the readers of F03 to F06 share and ``datafile`` exports.
MISSING_KEY: Final[Message] = Message('The key "{key}" is missing.', "缺少键“{key}”。")
NOT_A_LIST: Final[Message] = Message(
    '"{key}" must be a list in square brackets, [ ... ].',
    "“{key}”必须是放在方括号 [ ... ] 里的列表。",
)
NOT_A_TABLE: Final[Message] = Message(
    "This item must be a table in braces, {{ ... }}.",
    "这一项必须是放在花括号 {{ ... }} 里的表。",
)
NOT_A_TEXT: Final[Message] = Message(
    '"{key}" must be a text in quotation marks.',
    "“{key}”必须是放在引号里的文字。",
)
EMPTY_TEXT: Final[Message] = Message('"{key}" is empty.', "“{key}”是空的。")
ITEM_NOT_A_TEXT: Final[Message] = Message(
    "This item must be a text in quotation marks.",
    "这一项必须是放在引号里的文字。",
)
EMPTY_ITEM: Final[Message] = Message("This item is empty.", "这一项是空的。")
UNKNOWN_KEY: Final[Plural] = Plural(
    Message(
        'Unknown key "{key}". The only key is {keys}.',
        "未知键“{key}”。可用的键：{keys}。",
    ),
    Message(
        'Unknown key "{key}". The keys are {keys}.',
        "未知键“{key}”。可用的键：{keys}。",
    ),
)

# Why a folder cannot be listed, and a file name that ``list_toml_files`` reports.
FOLDER_MISSING: Final[Message] = Message("The folder is missing.", "文件夹不存在。")
FOLDER_IS_FILE: Final[Message] = Message(
    "The folder cannot be read: it is a file.",
    "无法读取文件夹：它是一个文件。",
)
FOLDER_ACCESS_DENIED: Final[Message] = Message(
    "The folder cannot be read: access is denied.",
    "无法读取文件夹：没有访问权限。",
)
FOLDER_SYSTEM_ERROR: Final[Message] = Message(
    "The folder cannot be read. The system says: {reason}",
    "无法读取文件夹。系统提示：{reason}",
)
TOML_ENDING_NOT_SMALL: Final[Message] = Message(
    'The file name must end with ".toml" in small letters. Rename the file.',
    "文件名必须以小写的“.toml”结尾。请给文件改名。",
)

# Why a servings number is wrong, from ``read_servings``. These are internal to ``datafile``.
SERVINGS_NOT_A_NUMBER: Final[Message] = Message(
    "Servings must be a whole number from 1 to 100, such as 2.",
    "份数必须是 1 到 100 之间的整数，比如 2。",
)
SERVINGS_TOO_FEW: Final[Message] = Message(
    "Servings must be a whole number of 1 or more, not {servings}.",
    "份数必须是不小于 1 的整数，不能是 {servings}。",
)
SERVINGS_TOO_MANY: Final[Message] = Message(
    "Servings must be a whole number of 100 or less, not {servings}.",
    "份数必须是不大于 100 的整数，不能是 {servings}。",
)
