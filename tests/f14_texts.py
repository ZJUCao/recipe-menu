"""The expected texts of F14: the outputs of ``menu suggest``, the help, and the menu files.

Every text is written out as a literal, or built from literal templates, so a test imports no
message of the command, of the settings, or of the menus, and reads no prototype file. A count of
1 takes the form for one, as the test plan says. The module holds the lines of a first fill, a
refill, a fill that leaves meals empty, a week with no empty meal, a refusal, a failed save, and
the unknown tags, the choice among them for the counts of a run, the help of nine commands, the
messages and places of the key for the dishes, the five blocks of menu text of the test plan and
what each becomes after a run, and the four texts of a layout that the command refuses.
Nothing here calls an interface of F14 when the module is imported. U+00D7 is written as an
escape.
"""

from pathlib import Path

from f05_texts import HELP_EN_LINES, HELP_ZH_LINES, Msg, lines_text
from f07_texts import Prob
from f11_texts import SHOW_47
from recipe_menu.lang import BiText

# ---------------------------------------------------------------- the lines of one output


def _file(week: str) -> str:
    """Gives the menu file of a week relative to the data folder, with the system's separator."""
    return str(Path("menus", f"{week}.toml"))


def _meals(count: int) -> str:
    """Gives ``meal`` for 1 and ``meals`` for any other count."""
    return "meal" if count == 1 else "meals"


def _stay(count: int) -> str:
    """Gives ``stays`` for 1 and ``stay`` for any other count."""
    return "stays" if count == 1 else "stay"


def _filled(week: str, count: int, tag: str | None) -> str:
    """Gives the first line of a first fill in English."""
    with_tag = "" if tag is None else f' with recipes that have the tag "{tag}"'
    return f"Filled {count} empty {_meals(count)} of {week}{with_tag}."


def _filled_zh(week: str, count: int, tag: str | None) -> str:
    """Gives the first line of a first fill in Chinese."""
    with_tag = "" if tag is None else f"，用的都是带有标签“{tag}”的菜谱"
    return f"已为 {week} 填好 {count} 个空餐{with_tag}。"


def _kept(count: int) -> str:
    """Gives the sentence about the kept meals in English."""
    form = "meal that already has" if count == 1 else "meals that already have"
    return f"Kept the {count} {form} dishes."


def _kept_zh(count: int) -> str:
    """Gives the sentence about the kept meals in Chinese."""
    return f"保留了已经有菜的 {count} 餐。"


def _show(week: str) -> str:
    """Gives the line that points to ``menu show`` in English."""
    return f'Run "recipe-menu menu show {week}" to see the week.'


def _show_zh(week: str) -> str:
    """Gives the line that points to ``menu show`` in Chinese."""
    return f"运行“recipe-menu menu show {week}”查看这一周。"


def swap(week: str) -> str:
    """Gives the line that tells how to swap a dish, in English."""
    again = f'then run "recipe-menu menu suggest {week}" again.'
    return f"To swap a dish, empty its meal in {_file(week)}, {again}"


def swap_zh(week: str) -> str:
    """Gives the line that tells how to swap a dish, in Chinese."""
    again = f"然后再运行“recipe-menu menu suggest {week}”。"
    return f"要换掉一道菜，就在 {_file(week)} 里清空它那一餐，{again}"


def first(week: str, count: int, tag: str | None = None) -> list[str]:
    """Gives the four lines of a first fill in English."""
    return [
        _filled(week, count, tag),
        "No recipe appears twice in the week.",
        _show(week),
        swap(week),
    ]


def first_zh(week: str, count: int, tag: str | None = None) -> list[str]:
    """Gives the four lines of a first fill in Chinese."""
    return [
        _filled_zh(week, count, tag),
        "这一周里没有重复的菜谱。",
        _show_zh(week),
        swap_zh(week),
    ]


def refill(week: str, count: int, kept: int, tag: str | None = None) -> list[str]:
    """Gives the two lines of a fill of every empty meal when some meals held dishes, in English."""
    return [f"{_filled(week, count, tag)} {_kept(kept)}", _show(week)]


def refill_zh(week: str, count: int, kept: int, tag: str | None = None) -> list[str]:
    """Gives the two lines of a fill of every empty meal when some meals held dishes, in Chinese."""
    return [f"{_filled_zh(week, count, tag)}{_kept_zh(kept)}", _show_zh(week)]


def _reason(missing: int, why: str, tag: str | None) -> str:
    """Gives the second line of a fill that leaves meals empty, in English.

    Args:
        missing: The number of meals that stay empty.
        why: ``left`` when every candidate went into a meal, ``few`` when candidates are left.
        tag: The name of the tag in English, or ``None``.
    """
    head = f"{missing} {_meals(missing)} {_stay(missing)} empty: "
    if why == "left":
        return head + (
            "no other recipe is left." if tag is None else f'no other recipe has the tag "{tag}".'
        )
    if tag is None:
        return head + "too few other recipes are left."
    return head + f'too few other recipes have the tag "{tag}".'


def _reason_zh(missing: int, why: str, tag: str | None) -> str:
    """Gives the second line of a fill that leaves meals empty, in Chinese."""
    head = f"{missing} 餐仍是空的："
    if why == "left":
        return head + ("没有别的菜谱可选了。" if tag is None else f"没有别的菜谱带有标签“{tag}”。")
    return head + ("剩下的菜谱不够了。" if tag is None else f"带有标签“{tag}”的别的菜谱不够了。")


def some(  # noqa: PLR0917 - the six values of the test plan, in its order
    week: str, filled: int, empty: int, kept: int, why: str, tag: str | None = None
) -> list[str]:
    """Gives the two lines of a fill of some of the empty meals, in English."""
    with_tag = "" if tag is None else f' with recipes that have the tag "{tag}"'
    head = f"Filled {filled} of {empty} empty {_meals(empty)} of {week}{with_tag}."
    if kept > 0:
        head += " " + _kept(kept)
    return [head, _reason(empty - filled, why, tag)]


def some_zh(  # noqa: PLR0917 - the six values of the test plan, in its order
    week: str, filled: int, empty: int, kept: int, why: str, tag: str | None = None
) -> list[str]:
    """Gives the two lines of a fill of some of the empty meals, in Chinese."""
    with_tag = "" if tag is None else f"，用的都是带有标签“{tag}”的菜谱"
    head = f"已为 {week} 填好 {empty} 个空餐中的 {filled} 个{with_tag}。"
    if kept > 0:
        head += _kept_zh(kept)
    return [head, _reason_zh(empty - filled, why, tag)]


def full(week: str) -> list[str]:
    """Gives the two lines of a week with no empty meal, in English."""
    return [f"{week} has no empty meal. Nothing was changed.", swap(week)]


def full_zh(week: str) -> list[str]:
    """Gives the two lines of a week with no empty meal, in Chinese."""
    return [f"{week} 没有空餐。没有做任何修改。", swap_zh(week)]


def outcome(  # noqa: PLR0917 - the values of one run, in the order of the output table
    week: str, empty: int, filled: int, kept: int, why: str, tags: Msg | None, zh: bool
) -> list[str]:
    """Gives the lines of the table of the output for the counts of a run.

    Args:
        week: The week, such as ``2026-W48``.
        empty: The number of empty meals before the run.
        filled: The number of empty meals that got dishes.
        kept: The number of meals that held dishes before the run.
        why: ``left`` or ``few``, the reason that meals stay empty.
        tags: The English and the Chinese name of the tag, or ``None``.
        zh: Whether the output is in Chinese.
    """
    tag = None if tags is None else tags[1 if zh else 0]
    if empty == 0:
        return full_zh(week) if zh else full(week)
    if filled < empty:
        build = some_zh if zh else some
        return build(week, filled, empty, kept, why, tag)
    if kept > 0:
        return refill_zh(week, filled, kept, tag) if zh else refill(week, filled, kept, tag)
    return first_zh(week, filled, tag) if zh else first(week, filled, tag)


# ---------------------------------------------------------------- refusals and failures


def cannot(week: str) -> list[str]:
    """Gives the three lines of a file that the command cannot fill, in English."""
    what = (
        "  menu suggest cannot fill this file: write each day as a line such as [monday], "
        'and each empty meal as a line such as dinner = [], as "recipe-menu menu new" does.'
    )
    return [_file(week), what, "Nothing was changed."]


def cannot_zh(week: str) -> list[str]:
    """Gives the three lines of a file that the command cannot fill, in Chinese."""
    what = (
        "  menu suggest 无法填写这个文件：请把每一天写成 [monday] 这样的一行，"
        "把每个空餐写成 dinner = [] 这样的一行，和“recipe-menu menu new”写的一样。"
    )
    return [_file(week), what, "没有做任何修改。"]


def failed(week: str, msg: Msg) -> list[str]:
    """Gives the three lines of a failed save in English."""
    return [_file(week), f"  {msg[0]}", "Nothing was changed."]


def failed_zh(week: str, msg: Msg) -> list[str]:
    """Gives the three lines of a failed save in Chinese."""
    return [_file(week), f"  {msg[1]}", "没有做任何修改。"]


def left_behind(week: str, msg: Msg, temp: Path | str) -> list[str]:
    """Gives the three lines of a failed save in English when ``temp`` could not be removed."""
    last = f"Nothing was changed, but menu suggest could not remove {temp}. Delete it."
    return [_file(week), f"  {msg[0]}", last]


def left_behind_zh(week: str, msg: Msg, temp: Path | str) -> list[str]:
    """Gives the three lines of a failed save in Chinese when ``temp`` could not be removed."""
    return [
        _file(week),
        f"  {msg[1]}",
        f"没有做任何修改，但 menu suggest 没能删除 {temp}。请删除它。",
    ]


# ---------------------------------------------------------------- the tags


def tags(value: str) -> str:
    """Gives the message of an unknown tag in English for the five tags of the example."""
    return f'Unknown tag "{value}". The tags are quick, home-style, vegetarian, spicy, and staple.'


def tags_zh(value: str) -> str:
    """Gives the message of an unknown tag in Chinese for the five tags of the example."""
    return f"未知标签“{value}”。现有标签：快手、家常、素、辣和主食。"


def one_tag_text(value: str) -> str:
    """Gives the message of an unknown tag in English for a catalog with the tag quick only."""
    return f'Unknown tag "{value}". The only tag is quick.'


def one_tag_text_zh(value: str) -> str:
    """Gives the message of an unknown tag in Chinese for a catalog with the tag quick only."""
    return f"未知标签“{value}”。现有标签：快手。"


def no_tags_text(value: str) -> str:
    """Gives the message of an unknown tag in English for a catalog with no tags."""
    return f'Unknown tag "{value}". The catalog has no tags.'


def no_tags_text_zh(value: str) -> str:
    """Gives the message of an unknown tag in Chinese for a catalog with no tags."""
    return f"未知标签“{value}”。目录里没有标签。"


# ---------------------------------------------------------------- the help of nine commands

_BLOCK_EN = [
    "Commands:",
    "  init                  Create the data folder with example data.",
    "  check                 Check every data file for mistakes.",
    "  list                  List the recipes.",
    "  show ID               Show one recipe.",
    "  search WORD...        Find recipes by name, ingredient, or tag.",
    "  menu new [WEEK]       Create an empty week menu.",
    "  menu show [WEEK]      Show a week menu.",
    "  menu suggest [WEEK]   Fill the empty meals of a week menu.",
    "  shop [WEEK]           Make the shopping list of a week menu.",
    "",
    "Options:",
    "  --lang en|zh          The language of the output. Default: the settings, else English.",
    "  --data FOLDER         The data folder. Default: RECIPE_MENU_DATA, else ~/recipe-menu.",
    "  --version             Show the version.",
    "  --help                Show this help.",
]
_BLOCK_ZH = [
    "命令：",
    "  init                  创建数据文件夹和示例数据。",
    "  check                 检查每个数据文件有没有错误。",
    "  list                  列出菜谱。",
    "  show ID               查看一个菜谱。",
    "  search 词...          按名称、食材或标签找菜谱。",
    "  menu new [周]         创建一个空的周菜单。",
    "  menu show [周]        查看一个周菜单。",
    "  menu suggest [周]     给一个周菜单的空餐填上菜。",
    "  shop [周]             生成一个周菜单的购物清单。",
    "",
    "选项：",
    "  --lang en|zh          输出语言。默认：设置里的语言，否则英文。",
    "  --data 文件夹         数据文件夹。默认：RECIPE_MENU_DATA，否则 ~/recipe-menu。",
    "  --version             显示版本。",
    "  --help                显示这份帮助。",
]
HELP_14 = [*HELP_EN_LINES[:4], *_BLOCK_EN, "", HELP_EN_LINES[-1]]
HELP_14_ZH = [*HELP_ZH_LINES[:4], *_BLOCK_ZH, "", HELP_ZH_LINES[-1]]

# ---------------------------------------------------------------- the settings of the dishes

DISHES_NOT_A_TABLE: Msg = (
    '"dishes" must be a table in braces, such as dishes = { dinner = 2 }.',
    "“dishes”必须是放在花括号里的表，比如 dishes = { dinner = 2 }。",
)
DISHES_NOT_1_TO_10: Msg = (
    "The number of dishes must be a whole number from 1 to 10, such as 2.",
    "菜数必须是 1 到 10 之间的整数，比如 2。",
)
DISHES = BiText("dishes", "菜数")
_OF_MEAL = {
    "breakfast": BiText("dishes of breakfast", "早餐的菜数"),
    "lunch": BiText("dishes of lunch", "午餐的菜数"),
    "dinner": BiText("dishes of dinner", "晚餐的菜数"),
}


def dishes_of(meal: str) -> BiText:
    """Gives the place of the dishes of a meal: ``breakfast``, ``lunch``, or ``dinner``."""
    return _OF_MEAL[meal]


E_DISHES_ZERO = Prob("settings.toml", ("dishes of dinner", "晚餐的菜数"), DISHES_NOT_1_TO_10)
E_DISHES_TABLE = Prob("settings.toml", ("dishes", "菜数"), DISHES_NOT_A_TABLE)

# ---------------------------------------------------------------- the output of menu show

SHOW_47_FILLED = [
    *SHOW_47[:3],
    "Mon 16 Nov   Red-braised pork belly \u00d72   Tomato and egg stir-fry \u00d72",
    *SHOW_47[4:-1],
    "5 meals, 10 dishes. \u00d7n: servings.",
]

# ---------------------------------------------------------------- the texts of the test plan


TEXT_A = lines_text(
    'week = "2026-W48"',
    "",
    "[monday]",
    "lunch=[]",
    "dinner = [ ]  # nothing yet",
    "",
    "[ 'tuesday' ]  # guests",
    '"lunch" = []',
    "\t'dinner'\t=\t[\t]",
)
TEXT_A_AFTER = lines_text(
    'week = "2026-W48"',
    "",
    "[monday]",
    'lunch=["choy-sum"]',
    'dinner = ["cola-wings"]  # nothing yet',
    "",
    "[ 'tuesday' ]  # guests",
    '"lunch" = ["mapo-tofu"]',
    "\t'dinner'\t=\t[\"red-braised-pork\"]",
    "",
    "[wednesday]",
    'lunch = ["rice"]',
    'dinner = ["tomato-egg"]',
    "",
    "[thursday]",
    'lunch = ["tomato-egg-noodles"]',
)
TEXT_B = lines_text(
    'week = "2026-W48"',
    "",
    "[monday]  # busy",
    "# plan below",
    "lunch = []",
)
TEXT_B_AFTER = lines_text(
    'week = "2026-W48"',
    "",
    "[monday]  # busy",
    'breakfast = ["choy-sum"]',
    'dinner = ["mapo-tofu"]',
    "# plan below",
    'lunch = ["cola-wings"]',
    "",
    "[tuesday]",
    'breakfast = ["red-braised-pork"]',
    'lunch = ["rice"]',
    'dinner = ["tomato-egg"]',
    "",
    "[wednesday]",
    'breakfast = ["tomato-egg-noodles"]',
)
TEXT_C = "\n".join(
    ['week = "2026-W48"', "[sunday]", "dinner = []", "[monday]", 'dinner = ["rice"]']
)
TEXT_C_AFTER = lines_text(
    'week = "2026-W48"',
    "[sunday]",
    'dinner = ["tomato-egg-noodles"]',
    "[monday]",
    'dinner = ["rice"]',
    "",
    "[tuesday]",
    'dinner = ["choy-sum"]',
    "",
    "[wednesday]",
    'dinner = ["cola-wings"]',
    "",
    "[thursday]",
    'dinner = ["mapo-tofu"]',
    "",
    "[friday]",
    'dinner = ["red-braised-pork"]',
    "",
    "[saturday]",
    'dinner = ["tomato-egg"]',
)
TEXT_D = 'week = "2026-W48"'
TEXT_D_LF = TEXT_D + "\n"
TEXT_D_AFTER = lines_text(
    'week = "2026-W48"',
    "",
    "[monday]",
    'dinner = ["choy-sum"]',
    "",
    "[tuesday]",
    'dinner = ["cola-wings"]',
    "",
    "[wednesday]",
    'dinner = ["mapo-tofu"]',
    "",
    "[thursday]",
    'dinner = ["red-braised-pork"]',
    "",
    "[friday]",
    'dinner = ["rice"]',
    "",
    "[saturday]",
    'dinner = ["tomato-egg"]',
    "",
    "[sunday]",
    'dinner = ["tomato-egg-noodles"]',
)

# The layouts that the command refuses, written as menus/2026-W49.toml.
R3 = lines_text('week = "2026-W49"', "monday = { lunch = [], dinner = [] }")
R4 = lines_text('week = "2026-W49"', "monday.dinner = []")
R5 = lines_text('week = "2026-W49"', "", "[monday]", "lunch = []", r'"din\u006eer" = []')
R6 = lines_text('week = "2026-W49"', "", r'["mon\u0064ay"]', "dinner = []")
