"""Tests of F15 for the check after saving: its counts, its blocks, and its exit code (T23)."""

from collections.abc import Sequence
from pathlib import Path

from f03_support import M_ACCESS_DENIED
from f05_support import make_home
from f05_texts import lines_text
from f07_changes import catalog_brace
from f07_texts import Prob
from f08_support import DENIED, rule
from f09_texts import E_BRACE
from f13_support import pristine
from f15_blocks import BASE_FILE, BASE_NAME_LINE, EN_BLOCK
from f15_support import BASE, Hooked, add, answers, fresh, no_tomato, traced_add
from f15_texts import (
    FIX_AND_CHECK,
    ZH_NAME_PROMPT,
    base_out,
    block,
    en_step_lines,
    indented,
    ing_lines,
    item_lines,
    no_en_steps,
    no_zh_name,
    pick,
    recipe_path,
    saved_with_problems,
    unknown_in_recipe,
    whole_file,
)
from recipe_menu.datafile import DataFolder

TWO = ["番茄 300 g", "番茄 1 kg"]
ZH_LESS = BASE_FILE.replace(BASE_NAME_LINE, 'name = { en = "New dish" }')
TWO_ITEMS = item_lines(("番茄", "300 g"), ("番茄", "1 kg"))
ONE_ITEM = '  { item = "番茄", amount = "300 g" },\n'


def _tail(
    folder: DataFolder,
    errors: Sequence[Prob] = (),
    warnings: Sequence[Prob] = (),
    *,
    zh: bool = False,
) -> list[str]:
    """Gives the lines after saving: the counts, the two blocks, and the line to fix errors."""
    counts = saved_with_problems(recipe_path(folder), len(errors), len(warnings))
    lines = [pick(counts, zh), *block(zh, *errors), *block(zh, *warnings)]
    return [*lines, pick(FIX_AND_CHECK, zh)] if errors else lines


def _read(folder: DataFolder) -> bytes:
    """Reads the file of ``new-dish``."""
    return folder.recipe_file("new-dish").read_bytes()


def _check_changed_catalog(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Lines 2 to 5: the catalog loses the tomato while ``add`` waits."""
    unknown = [unknown_in_recipe("番茄", number) for number in (1, 2)]
    folder = fresh(source, tmp_path, "two")
    result = add(home, folder, Hooked(BASE, folder.root, no_tomato))
    expected = base_out(folder, tail=_tail(folder, unknown[:1]))
    assert result == (1, lines_text(*expected), "")
    assert _read(folder) == BASE_FILE.encode("utf-8")
    folder = fresh(source, tmp_path, "three")
    typed = answers(ingredients=TWO)
    result = add(home, folder, Hooked(typed, folder.root, no_tomato))
    expected = base_out(folder, ingredients=ing_lines(indented(*TWO)), tail=_tail(folder, unknown))
    assert result == (1, lines_text(*expected), "")
    assert _read(folder) == BASE_FILE.replace(ONE_ITEM, TWO_ITEMS).encode("utf-8")
    folder = fresh(source, tmp_path, "four")
    typed = answers(zh_name="")
    result = add(home, folder, Hooked(typed, folder.root, no_tomato))
    tail = _tail(folder, unknown[:1], [no_zh_name()])
    expected = base_out(folder, zh_name=[ZH_NAME_PROMPT[0]], tail=tail)
    assert result == (1, lines_text(*expected), "")
    assert _read(folder) == ZH_LESS.encode("utf-8")
    folder = fresh(source, tmp_path, "five")
    typed = answers(zh_name="", ingredients=TWO, en_steps=())
    result = add(home, folder, Hooked(typed, folder.root, no_tomato), "--lang", "zh")
    tail = _tail(folder, unknown, [no_zh_name(), no_en_steps()], zh=True)
    expected = base_out(
        folder,
        True,
        zh_name=[ZH_NAME_PROMPT[1]],
        ingredients=ing_lines(indented(*TWO), True),
        en_steps=en_step_lines([], True),
        tail=tail,
    )
    assert result == (1, lines_text(*expected), "")
    data = ZH_LESS.replace(ONE_ITEM, TWO_ITEMS).replace(EN_BLOCK, "")
    assert _read(folder) == data.encode("utf-8")


def test_f15_t23_the_check_after_saving_gives_the_counts_the_blocks_and_the_exit_code(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Eight lines: two warnings, errors from a changed catalog, and reads that are denied."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    folder = fresh(source, tmp_path, "one")
    result = add(home, folder, answers(zh_name="", en_steps=()))
    warnings = [no_zh_name(), no_en_steps()]
    expected = base_out(
        folder,
        zh_name=[ZH_NAME_PROMPT[0]],
        en_steps=en_step_lines([]),
        tail=_tail(folder, warnings=warnings),
    )
    assert result == (0, lines_text(*expected), "")
    assert _read(folder) == ZH_LESS.replace(EN_BLOCK, "").encode("utf-8")
    _check_changed_catalog(home, source, tmp_path)
    folder = fresh(source, tmp_path, "six")
    result = add(home, folder, Hooked(BASE, folder.root, catalog_brace))
    expected = base_out(folder, tail=_tail(folder, [E_BRACE]))
    assert result == (1, lines_text(*expected), "")
    assert _read(folder) == BASE_FILE.encode("utf-8")
    folder = fresh(source, tmp_path, "seven")
    denied = rule("read", folder.recipe_file("new-dish"), DENIED)
    result, _, _ = traced_add(home, folder, BASE, denied)
    problem = whole_file("recipes/new-dish.toml", M_ACCESS_DENIED)
    assert result == (1, lines_text(*base_out(folder, tail=_tail(folder, [problem]))), "")
    assert _read(folder) == BASE_FILE.encode("utf-8")
    folder = fresh(source, tmp_path, "eight")
    later = rule("read", folder.root / "catalog.toml", DENIED, "later")
    result, _, _ = traced_add(home, folder, BASE, later)
    problem = whole_file("catalog.toml", M_ACCESS_DENIED)
    assert result == (1, lines_text(*base_out(folder, tail=_tail(folder, [problem]))), "")
    assert _read(folder) == BASE_FILE.encode("utf-8")
