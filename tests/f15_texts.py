"""The expected texts of F15, as literals and as builders from literal templates.

The module holds the short expected texts and the builders of the other texts, which the large
literals of ``f15_blocks`` complete. A message is a pair of its English text and its Chinese
text. Every text is written out in full, so a test imports no message of the command, of the
check, of the application, or of the text module, and reads no prototype file. A problem names
its file with the system's separator, and a message names a saved file by its full path, as the
test plan says. Nothing here calls an interface of F15 when the module is imported. Invisible
and look-alike characters are written as escapes.
"""

from collections.abc import Sequence
from pathlib import Path

from f04_support import M_NO_EN_NAME, M_NO_EN_STEPS, M_NO_ZH_NAME, M_NO_ZH_STEPS
from f05_texts import Msg
from f07_texts import P_NAME, P_STEPS, Prob, p_ingredient
from f09_texts import pair
from f09_texts import unknown_ingredient as _recipe_unknown
from f15_blocks import (
    BASE_OUT_LINES,
    BASE_OUT_LINES_ZH,
    PT01_OUT_LINES,
    S09_OUT_LINES,
    S10_OUT_LINES,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

type Lines = Sequence[str]

# ---------------------------------------------------------------- the prompts

ADD_HELP: Msg = ("Add a recipe by answering questions.", "回答问题，添加一个菜谱。")
ID_PROMPT: Msg = ("Recipe ID (also the file name): ", "菜谱 ID（也是文件名）：")
ZH_NAME_PROMPT: Msg = ("Chinese name: ", "中文名：")
EN_NAME_PROMPT: Msg = ("English name: ", "英文名：")
TAGS_PROMPT: Msg = ("Tags, separated by commas: ", "标签，用逗号分隔：")
INGREDIENTS_PROMPT: Msg = (
    'Ingredients, one per line, as "name quantity". An empty line ends the list:',
    "食材，每行一个，写“名称 数量”，空行结束：",
)
ZH_STEPS_PROMPT: Msg = (
    "Chinese steps, one per line. An empty line ends the list:",
    "中文步骤，每行一步，空行结束：",
)
EN_STEPS_PROMPT: Msg = (
    "English steps, one per line. An empty line ends the list:",
    "英文步骤，每行一步，空行结束：",
)
EN_STEPS_OPTIONAL_PROMPT: Msg = (
    "English steps, one per line. An empty line ends the list (optional):",
    "英文步骤，每行一步，空行结束（可以不写）：",
)


def servings_prompt(servings: int = 2) -> Msg:
    """Gives the prompt of question 4 for the servings of the settings."""
    return f"Servings [{servings}]: ", f"份数 [{servings}]："


# ---------------------------------------------------------------- the messages

NAME_NEEDED: Msg = (
    "A recipe needs a name in at least one language. Enter its English name.",
    "菜谱至少要有一种语言的名称。请输入它的英文名。",
)
SERVINGS_WRONG: Msg = (
    "Servings must be a whole number from 1 to 100, such as 2.",
    "份数必须是 1 到 100 之间的整数，比如 2。",
)
NAME_AND_QUANTITY: Msg = (
    'Write the name, a space, and the quantity, such as "Tomato 300 g" or "Salt to taste".',
    "请写上名称、空格和数量，比如“番茄 300 g”或“盐 适量”。",
)
STEPS_NEEDED: Msg = (
    "A recipe needs steps in at least one language. Enter at least one English step.",
    "菜谱至少要有一种语言的步骤。请至少输入一步英文步骤。",
)
FIX_AND_CHECK: Msg = (
    'Fix the errors, then run "recipe-menu check".',
    "改正错误后，运行“recipe-menu check”。",
)
INPUT_ENDED: Msg = (
    "The answers ended before the recipe was complete. Nothing was saved.",
    "回答在菜谱完成之前就结束了。没有保存任何东西。",
)
NOTHING_SAVED: Msg = ("Nothing was saved.", "没有保存任何东西。")


def not_an_id(value: str) -> Msg:
    """Gives ``NOT_AN_ID`` for an answer."""
    return (
        f'"{value}" cannot be a recipe ID. An ID has only the small letters a to z, digits, '
        'and "-", and starts with a letter or a digit, such as "tomato-egg". Windows device '
        'names, such as "con", are not IDs.',
        f"“{value}”不能用作菜谱 ID。ID 只能由小写字母 a 到 z、数字和“-”组成，"
        "并以字母或数字开头，比如“tomato-egg”。“con”这样的 Windows 设备名不能用作 ID。",
    )


def id_exists(value: str) -> Msg:
    """Gives ``ID_EXISTS`` for an ID."""
    return (
        f'The recipe {value} already exists. Enter another ID, or run "recipe-menu edit {value}".',
        f"菜谱 {value} 已经存在。请输入另一个 ID，或者运行“recipe-menu edit {value}”。",
    )


def unknown_ingredient(name: str) -> Msg:
    """Gives ``UNKNOWN_INGREDIENT`` of ``add`` for a name."""
    return (
        f'The catalog has no "{name}". Enter a name from the catalog, or add it to the catalog '
        "first and then run add again.",
        f"目录里没有“{name}”。请输入目录里的名称，或先把它加入目录后再运行 add。",
    )


def no_unit(amount: str, ingredient: Msg) -> Msg:
    """Gives ``AMOUNT_NO_UNIT`` for an amount and the names of the ingredient, English first."""
    return (
        f'The amount "{amount}" has no unit, and the catalog gives "{ingredient[0]}" no default '
        'unit. Write a unit after the number, such as "300 g".',
        f"数量“{amount}”没有单位，目录也没有给“{ingredient[1]}”默认单位。"
        "请在数字后面写上单位，比如“300 g”。",
    )


def appeared(file: str) -> Msg:
    """Gives ``APPEARED`` for the full path of an entry."""
    return (
        f'Nothing was saved: {file} appeared while you answered. Run "recipe-menu add" again '
        "with another ID.",
        f"没有保存任何东西：你回答问题时出现了 {file}。请换一个 ID，再运行“recipe-menu add”。",
    )


def left_behind(file: str) -> Msg:
    """Gives ``LEFT_BEHIND`` for the full path of the file."""
    return (
        f"Nothing was saved, but add could not remove {file}. Delete it.",
        f"没有保存任何东西，但 add 没能删除 {file}。请删除它。",
    )


def saved(file: str) -> Msg:
    """Gives ``SAVED`` for the full path of the file."""
    return (
        f"Saved {file}. The check found no problems.",
        f"已保存 {file}。检查没有发现问题。",
    )


def _counts(errors: int, warnings: int) -> Msg:
    """Gives the counts of a check, leaving out a count of 0."""
    english: list[str] = []
    chinese: list[str] = []
    if errors:
        english.append(f"{errors} error" + ("" if errors == 1 else "s"))
        chinese.append(f"{errors} 个错误")
    if warnings:
        english.append(f"{warnings} warning" + ("" if warnings == 1 else "s"))
        chinese.append(f"{warnings} 个警告")
    return " and ".join(english), "和 ".join(chinese)


def saved_with_problems(file: str, errors: int, warnings: int) -> Msg:
    """Gives ``SAVED_WITH_PROBLEMS`` for the full path and the counts."""
    english, chinese = _counts(errors, warnings)
    return (
        f"Saved {file}. The check found {english}:",
        f"已保存 {file}。检查发现了 {chinese}：",
    )


def pick(msg: Msg, zh: bool) -> str:
    """Gives the text of a message in a language."""
    return msg[1] if zh else msg[0]


# ---------------------------------------------------------------- paths and problems


def _root(folder: DataFolder | Path) -> Path:
    """Gives the path of a data folder."""
    return folder.root if isinstance(folder, DataFolder) else folder


def recipe_path(folder: DataFolder | Path, recipe_id: str = "new-dish") -> str:
    """Gives the full path of the file of a recipe, as a message shows it."""
    return str(_root(folder) / "recipes" / f"{recipe_id}.toml")


def entry_path(folder: DataFolder | Path, name: str) -> str:
    """Gives the full path of an entry of ``recipes/`` by its name."""
    return str(_root(folder) / "recipes" / name)


def relative(recipe_id: str = "new-dish") -> str:
    """Gives the file of a recipe relative to the data folder, with the system's separator."""
    return str(Path("recipes", f"{recipe_id}.toml"))


def _file(recipe_id: str) -> str:
    """Gives the file of a recipe with ``/`` separators, as a ``Prob`` holds it."""
    return f"recipes/{recipe_id}.toml"


def no_zh_name(recipe_id: str = "new-dish") -> Prob:
    """Gives the warning of a recipe with no Chinese name."""
    return Prob(_file(recipe_id), P_NAME, M_NO_ZH_NAME)


def no_en_name(recipe_id: str = "new-dish") -> Prob:
    """Gives the warning of a recipe with no English name."""
    return Prob(_file(recipe_id), P_NAME, M_NO_EN_NAME)


def no_zh_steps(recipe_id: str = "new-dish") -> Prob:
    """Gives the warning of a recipe with no Chinese steps."""
    return Prob(_file(recipe_id), P_STEPS, M_NO_ZH_STEPS)


def no_en_steps(recipe_id: str = "new-dish") -> Prob:
    """Gives the warning of a recipe with no English steps."""
    return Prob(_file(recipe_id), P_STEPS, M_NO_EN_STEPS)


def unknown_in_recipe(name: str, number: int, recipe_id: str = "new-dish") -> Prob:
    """Gives the error of ingredient ``number`` of a recipe, which the catalog lacks."""
    return Prob(_file(recipe_id), p_ingredient(number), _recipe_unknown(name))


def whole_file(file: str, msg: Msg) -> Prob:
    """Gives a problem of a whole file, with no place."""
    return Prob(file, None, msg)


def block(zh: bool, *problems: Prob) -> list[str]:
    """Gives the lines of ``problem_block``: two lines for each problem, in a language."""
    lines: list[str] = []
    for problem in problems:
        where, what = pair(problem, Lang.ZH if zh else Lang.EN)
        lines += [f"  {where}", f"    {what}"]
    return lines


# ---------------------------------------------------------------- the lines of a session


def rounds(prompt: str, *items: str | tuple[str, str], indent: str = "") -> list[str]:
    """Gives the lines of the answers to one question, each after the prompt.

    An item is an answer, or an answer and the message that follows it. The message gets the
    indent first.
    """
    lines: list[str] = []
    for item in items:
        answer, message = (item, None) if isinstance(item, str) else item
        lines.append(prompt + answer)
        if message is not None:
            lines.append(indent + message)
    return lines


def ing_lines(items: Lines, zh: bool = False) -> list[str]:
    """Gives the prompt of the ingredients, the lines of the list, and the empty line."""
    return [INGREDIENTS_PROMPT[zh], *items, "  "]


def zh_step_lines(items: Lines, zh: bool = False) -> list[str]:
    """Gives the prompt of the Chinese steps, the lines of the list, and the empty line."""
    return [ZH_STEPS_PROMPT[zh], *items, "  "]


def en_step_lines(items: Lines, zh: bool = False, *, optional: bool = True) -> list[str]:
    """Gives the prompt of the English steps, the lines of the list, and the empty line."""
    prompt = EN_STEPS_OPTIONAL_PROMPT if optional else EN_STEPS_PROMPT
    return [prompt[zh], *items, "  "]


def indented(*texts: str) -> list[str]:
    """Gives each text after two spaces, as a line of a list."""
    return [f"  {text}" for text in texts]


_ORDER = ("id", "zh_name", "en_name", "servings", "tags", "ingredients", "zh_steps", "en_steps")


def base_out(
    folder: DataFolder | Path,
    zh: bool = False,
    recipe_id: str = "new-dish",
    **sections: Lines,
) -> list[str]:
    """Gives the lines of the output of BASE, with the lines of some sections replaced.

    A section is ``id``, ``zh_name``, ``en_name``, ``servings``, ``tags``, ``ingredients``,
    ``zh_steps``, ``en_steps``, or ``tail``. The three lists hold their prompt and their empty
    line. ``tail`` is the line after saving. For a recipe ID other than ``new-dish``, the file
    in the tail is the file of that ID.
    """
    base = BASE_OUT_LINES_ZH if zh else BASE_OUT_LINES
    parts: dict[str, Lines] = {
        "id": [ID_PROMPT[zh] + recipe_id],
        "zh_name": base[1:2],
        "en_name": base[2:3],
        "servings": base[3:4],
        "tags": base[4:5],
        "ingredients": base[5:8],
        "zh_steps": base[8:11],
        "en_steps": base[11:14],
        "tail": [pick(saved(recipe_path(folder, recipe_id)), zh)],
    }
    assert set(sections) <= set(parts), sections
    parts.update(sections)
    return [line for key in (*_ORDER, "tail") for line in parts[key]]


_ROWS = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 7, 8: 9, 9: 10, 10: 12, 11: 13}


def answer_cut(folder: DataFolder | Path, given: int, zh: bool = False) -> tuple[list[str], str]:
    """Gives the lines of BASE before the line of the next answer, and that line's prompt.

    Args:
        folder: The data folder.
        given: The number of answers that were given, from 0 to 10.
        zh: Whether the output is in Chinese.

    Returns:
        The lines of ``base_out`` before the line of answer ``given + 1``, and the prompt that
        starts that line: a prompt of questions 1 to 5, or two spaces in a list.
    """
    prompts = [ID_PROMPT, ZH_NAME_PROMPT, EN_NAME_PROMPT, servings_prompt(), TAGS_PROMPT]
    prompt = pick(prompts[given], zh) if given < 5 else "  "
    return base_out(folder, zh)[: _ROWS[given + 1]], prompt


def item_lines(*pairs: tuple[str, str]) -> str:
    """Gives the ingredient lines of a recipe file for names and quantities."""
    return "".join(f'  {{ item = "{item}", amount = "{amount}" }},\n' for item, amount in pairs)


def s09_out(folder: DataFolder | Path) -> list[str]:
    """Gives the lines of the first run of the design's example: S09 in Chinese."""
    return [*S09_OUT_LINES, pick(saved(recipe_path(folder, "garlic-broccoli")), True)]


def s10_out(folder: DataFolder | Path) -> list[str]:
    """Gives the lines of S10, the English run of the design's example."""
    return [*S10_OUT_LINES, saved(recipe_path(folder, "egg-fried-rice"))[0]]


def pt01_out(folder: DataFolder | Path) -> list[str]:
    """Gives the lines of the output of the answers of the PT01 data folder."""
    return [*PT01_OUT_LINES, saved(recipe_path(folder, "size-check"))[0]]


def partly_out(folder: DataFolder | Path) -> list[str]:
    """Gives the lines of the run that leaves out the English name and the English steps."""
    path = recipe_path(folder, "scallion-egg")
    return [
        ID_PROMPT[0] + "scallion-egg",
        ZH_NAME_PROMPT[0] + "葱花蛋",
        EN_NAME_PROMPT[0],
        servings_prompt()[0],
        TAGS_PROMPT[0] + "快手，quick",
        *ing_lines(indented("鸡蛋 3", "葱 2")),
        *zh_step_lines(indented("鸡蛋打散，加葱花煎熟。")),
        *en_step_lines([]),
        saved_with_problems(path, 0, 2)[0],
        *block(False, no_en_name("scallion-egg"), no_en_steps("scallion-egg")),
    ]
