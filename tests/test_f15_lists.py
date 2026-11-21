"""Tests of F15 for the ingredient lines and the steps (T14 and T15)."""

from pathlib import Path

from f04_support import m_amount_unit, m_not_a_number, m_zero
from f05_support import make_home
from f05_texts import Msg, lines_text
from f13_support import pristine
from f15_blocks import BASE_FILE, EN_BLOCK, ING_BLOCK, ZH_BLOCK
from f15_support import BASE, add, answers, fresh
from f15_texts import (
    EN_STEPS_OPTIONAL_PROMPT,
    EN_STEPS_PROMPT,
    NAME_AND_QUANTITY,
    STEPS_NEEDED,
    ZH_STEPS_PROMPT,
    base_out,
    block,
    en_step_lines,
    indented,
    ing_lines,
    item_lines,
    no_en_steps,
    no_unit,
    no_zh_steps,
    pick,
    recipe_path,
    rounds,
    saved_with_problems,
    unknown_ingredient,
    zh_step_lines,
)
from recipe_menu.datafile import DataFolder

RIGHT = [
    "西兰花 300 g",
    "Cooking oil 2 tbsp",
    "Salt to taste",
    "盐 适量",
    "Egg 3",
    "西兰花 300g",
    "Salt TO taste",
    "broccoli 1 kg",
    "大蒜\u30004 瓣",
    "Egg 2",
    "Scallion 1 stalk",
]
KEPT = [
    ("西兰花", "300 g"),
    ("Cooking oil", "2 tbsp"),
    ("Salt", "to taste"),
    ("盐", "适量"),
    ("Egg", "3"),
    ("西兰花", "300g"),
    ("Salt", "TO taste"),
    ("broccoli", "1 kg"),
    ("大蒜", "4 瓣"),
    ("Egg", "2"),
    ("Scallion", "1 stalk"),
]
RICE: Msg = ("Rice", "大米")
BIG = "1234567890123456 g"
WRONG_LINES: list[tuple[str, Msg | None]] = [
    ("Peanut", NAME_AND_QUANTITY),
    ("300 g", NAME_AND_QUANTITY),
    ("盐适量", NAME_AND_QUANTITY),
    ("西兰花300g", NAME_AND_QUANTITY),
    ("to taste", NAME_AND_QUANTITY),
    ("适量", NAME_AND_QUANTITY),
    ("Peanut 30 g", unknown_ingredient("Peanut")),
    ("7-Up 1 can", unknown_ingredient("7-Up")),
    ("Choy  sum 1 斤", unknown_ingredient("Choy  sum")),
    ("Peanut 1 cups", unknown_ingredient("Peanut")),
    ("Rice 1 cups", m_amount_unit("cups", "1 cups")),
    ("Rice 300", no_unit("300", RICE)),
    ("Rice 0 g", m_zero("0 g")),
    (f"Rice {BIG}", m_not_a_number(BIG)),
    ("番茄 300 g", None),
]


def _lines(typed: list[str], zh: bool) -> list[str]:
    """Gives the lines of answers of WRONG_LINES, each message after two spaces."""
    messages = dict(WRONG_LINES)
    items: list[str | tuple[str, str]] = []
    for answer in typed:
        msg = messages[answer]
        items.append(answer if msg is None else (answer, pick(msg, zh)))
    return rounds("  ", *items, indent="  ")


def test_f15_t14_an_ingredient_line_is_split_checked_and_kept_as_typed(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Four lines: right lines, wrong lines in English and in Chinese, and no ingredients."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    one_line = '  { item = "番茄", amount = "300 g" },\n'
    first = fresh(source, tmp_path, "first")
    expected = base_out(first, ingredients=ing_lines(indented(*RIGHT)))
    assert add(home, first, answers(ingredients=RIGHT)) == (0, lines_text(*expected), "")
    data = BASE_FILE.replace(one_line, item_lines(*KEPT)).encode("utf-8")
    assert first.recipe_file("new-dish").read_bytes() == data
    second = fresh(source, tmp_path, "second")
    typed = [answer for answer, _ in WRONG_LINES]
    expected = base_out(second, ingredients=ing_lines(_lines(typed, False)))
    assert add(home, second, answers(ingredients=typed)) == (0, lines_text(*expected), "")
    assert second.recipe_file("new-dish").read_bytes() == BASE_FILE.encode("utf-8")
    third = fresh(source, tmp_path, "third")
    chosen = ["盐适量", "Peanut 30 g", "Rice 1 cups", "Rice 300", "Rice 0 g", f"Rice {BIG}"]
    chosen.append("番茄 300 g")
    expected = base_out(third, True, ingredients=ing_lines(_lines(chosen, True), True))
    result = add(home, third, answers(ingredients=chosen), "--lang", "zh")
    assert result == (0, lines_text(*expected), "")
    assert third.recipe_file("new-dish").read_bytes() == BASE_FILE.encode("utf-8")
    fourth = fresh(source, tmp_path, "fourth")
    expected = base_out(fourth, ingredients=ing_lines([]))
    assert add(home, fourth, answers(ingredients=())) == (0, lines_text(*expected), "")
    empty = BASE_FILE.replace(ING_BLOCK, "ingredients = []\n")
    assert fourth.recipe_file("new-dish").read_bytes() == empty.encode("utf-8")


def test_f15_t15_the_steps_may_stay_empty_in_one_language_but_not_in_both(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five lines: no Chinese steps, no English steps, no steps at all, and blank lines."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    cut = ["  Cut the tomatoes."]
    first = fresh(source, tmp_path, "first")
    tail = [saved_with_problems(recipe_path(first), 0, 1)[0], *block(False, no_zh_steps())]
    no_zh = {
        "zh_steps": zh_step_lines([]),
        "en_steps": en_step_lines(cut, optional=False),
        "tail": tail,
    }
    expected = base_out(first, **no_zh)
    assert add(home, first, answers(zh_steps=())) == (0, lines_text(*expected), "")
    without_zh = BASE_FILE.replace(ZH_BLOCK, "").encode("utf-8")
    assert first.recipe_file("new-dish").read_bytes() == without_zh
    second = fresh(source, tmp_path, "second")
    tail = [saved_with_problems(recipe_path(second), 0, 1)[0], *block(False, no_en_steps())]
    expected = base_out(second, en_steps=en_step_lines([]), tail=tail)
    assert add(home, second, answers(en_steps=())) == (0, lines_text(*expected), "")
    without_en = BASE_FILE.replace(EN_BLOCK, "").encode("utf-8")
    assert second.recipe_file("new-dish").read_bytes() == without_en
    for zh, name in ((False, "third"), (True, "fourth")):
        _check_steps_needed(home, fresh(source, tmp_path, name), zh)
    fifth = fresh(source, tmp_path, "fifth")
    typed = [*BASE[:7], "第一步。", "第二步。", "\u3000 ", "Step one.", "\t"]
    expected = base_out(
        fifth,
        zh_steps=[ZH_STEPS_PROMPT[0], *indented("第一步。", "第二步。", "\u3000 ")],
        en_steps=[EN_STEPS_OPTIONAL_PROMPT[0], *indented("Step one.", "\t")],
    )
    assert add(home, fifth, typed) == (0, lines_text(*expected), "")
    steps = BASE_FILE.replace('  "番茄切块。",\n', '  "第一步。",\n  "第二步。",\n')
    data = steps.replace("Cut the tomatoes.", "Step one.").encode("utf-8")
    assert fifth.recipe_file("new-dish").read_bytes() == data


def _check_steps_needed(home: Path, folder: DataFolder, zh: bool) -> None:
    """Checks the lines of a run with no steps asked for twice, and then an English step."""
    typed = [*BASE[:7], "", "", "", "Cut the tomatoes.", ""]
    needed = pick(STEPS_NEEDED, zh)
    asked = pick(EN_STEPS_PROMPT, zh)
    tail = [
        pick(saved_with_problems(recipe_path(folder), 0, 1), zh),
        *block(zh, no_zh_steps()),
    ]
    expected = base_out(
        folder,
        zh,
        zh_steps=[pick(ZH_STEPS_PROMPT, zh), "  "],
        en_steps=[asked, "  ", needed, asked, "  ", needed, asked, "  Cut the tomatoes.", "  "],
        tail=tail,
    )
    extra = ("--lang", "zh") if zh else ()
    assert add(home, folder, typed, *extra) == (0, lines_text(*expected), "")
    without_zh = BASE_FILE.replace(ZH_BLOCK, "").encode("utf-8")
    assert folder.recipe_file("new-dish").read_bytes() == without_zh
