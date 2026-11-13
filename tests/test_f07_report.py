"""Tests of F07 for recipe-menu check and its report (T04 to T06)."""

from pathlib import Path

from f03_support import write
from f05_support import copy_example, make_home
from f07_changes import (
    add_monday_breakfast,
    broken_settings,
    edit,
    make_init,
    mapo_mistake,
    menu_copy,
    menu_path,
    pork_in_english,
    the_typo,
)
from f07_support import (
    AFTER,
    AFTER_ZH,
    COUNTS,
    COUNTS_ZH,
    EMPTY,
    EMPTY_ZH,
    FIX,
    FIX_ZH,
    TWO,
    TWO_ZH,
    check,
    expect,
    rep,
)
from f07_texts import MISSING_BRACKET, PORK, Prob, m_settings_meal, p_line
from recipe_menu.datafile import DataFolder

NO_PROBLEMS = [COUNTS, "", "No errors. No warnings."]
NO_PROBLEMS_ZH = [COUNTS_ZH, "", "没有错误，也没有警告。"]
_PORK_FILE = str(Path("recipes", "red-braised-pork.toml"))
_MAPO_FILE = str(Path("recipes", "mapo-tofu.toml"))
_TOMATO_FILE = str(Path("recipes", "tomato-egg.toml"))


def test_f07_t04_the_example_of_2_2_runs_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The two mistakes, a syntax mistake, broken settings, no problems, and two usage errors."""
    home = make_home(tmp_path)
    root = example_folder.root
    mapo_text = (root / "recipes" / "mapo-tofu.toml").read_text(encoding="utf-8")
    menu_text = menu_path(root).read_text(encoding="utf-8")
    pantry_text = (root / "pantry.toml").read_text(encoding="utf-8")
    settings_text = (root / "settings.toml").read_text(encoding="utf-8")
    mapo_mistake(root)
    the_typo(root)
    assert check(home, root) == expect(1, TWO)
    assert check(home, root, "--lang", "zh") == expect(1, TWO_ZH)

    write(root / "recipes" / "mapo-tofu.toml", mapo_text)
    write(menu_path(root), menu_text)
    write(root / "pantry.toml", '# The pantry.\npantry = ["食用油", "盐" "糖"]\n')
    expected = rep(1, 7, 1, [Prob("pantry.toml", p_line(2), MISSING_BRACKET)], [PORK])
    assert check(home, root) == expected

    write(root / "pantry.toml", pantry_text)
    broken_settings(root)
    add_monday_breakfast(menu_path(root))
    settings = Prob("settings.toml", ("meals", "餐次"), m_settings_meal("supper"))
    assert check(home, root) == rep(1, 7, 1, [settings], [PORK])

    write(root / "settings.toml", settings_text)
    write(menu_path(root), menu_text)
    pork_in_english(root)
    assert check(home, root) == expect(0, NO_PROBLEMS)

    empty = tmp_path / "empty"
    empty.mkdir()
    assert check(home, empty) == expect(1, EMPTY)

    missing = tmp_path / "missing"
    code, out, err = check(home, missing)
    assert (code, out) == (1, "")
    assert err.splitlines() == [
        f"There is no data folder at {missing}.",
        'Run "recipe-menu init" to create it, or name another folder with --data.',
    ]
    code, out, err = check(home, root, "extra")
    assert (code, out) == (2, "")
    assert err.splitlines() == [
        'Unexpected argument "extra". Write "recipe-menu check".',
        'Run "recipe-menu --help" to see the commands.',
    ]
    code, out, err = check(home, root, "--tag", "素")
    assert (code, out) == (2, "")
    assert err.splitlines() == [
        '"check" has no option "--tag". It has no options of its own.',
        'Run "recipe-menu --help" to see the options.',
    ]


def test_f07_t05_the_four_kinds_of_report_in_both_languages(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """No problems, a warning alone, an error alone, and an error with a warning."""
    home = make_home(tmp_path)
    one = copy_example(example_folder, tmp_path / "one")
    pork_in_english(one)
    three = copy_example(example_folder, tmp_path / "three")
    pork_in_english(three)
    mapo_mistake(three)
    four = copy_example(example_folder, tmp_path / "four")
    mapo_mistake(four)
    the_typo(four)
    error_en = [
        COUNTS,
        "",
        "1 error:",
        f"  {_MAPO_FILE}, ingredient 3",
        '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.',
        "",
        FIX,
    ]
    error_zh = [
        COUNTS_ZH,
        "",
        "1 个错误：",
        f"  {_MAPO_FILE}，食材 3",
        "    未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。",
        "",
        FIX_ZH,
    ]
    cases = [
        (one, (0, NO_PROBLEMS), (0, NO_PROBLEMS_ZH)),
        (example_folder.root, (0, AFTER), (0, AFTER_ZH)),
        (three, (1, error_en), (1, error_zh)),
        (four, (1, TWO), (1, TWO_ZH)),
    ]
    for root, english, chinese in cases:
        assert check(home, root) == expect(*english), root
        assert check(home, root, "--lang", "zh") == expect(*chinese), root


def test_f07_t06_the_counts_take_their_form_for_one_and_for_more(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """One recipe, 0 week menus, 2 warnings, and 2 week menus; and the same count in Chinese."""
    home = make_home(tmp_path)
    init = make_init(example_folder, tmp_path / "init")
    one_en = [
        "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus.",
        "",
        "No errors. No warnings.",
    ]
    one_zh = ["已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。", "", "没有错误，也没有警告。"]
    assert check(home, init) == expect(0, one_en)
    assert check(home, init, "--lang", "zh") == expect(0, one_zh)

    two = copy_example(example_folder, tmp_path / "two")
    edit(two / "recipes" / "tomato-egg.toml", ', en = "Tomato and egg stir-fry"', "")
    menu_copy(two, "2026-W48")
    two_en = [
        "Checked the settings, the catalog, the pantry, 7 recipes, and 2 week menus.",
        "",
        "No errors.",
        "",
        "2 warnings:",
        f"  {_PORK_FILE}, steps",
        "    No English steps. Commands show the Chinese steps instead.",
        f"  {_TOMATO_FILE}, name",
        "    No English name. Commands show the Chinese name instead.",
    ]
    two_zh = [
        "已检查设置、目录、常备清单、7 个菜谱和 2 个周菜单。",
        "",
        "没有错误。",
        "",
        "2 个警告：",
        f"  {_PORK_FILE}，步骤",
        "    没有英文步骤。命令会改为显示中文步骤。",
        f"  {_TOMATO_FILE}，名称",
        "    没有英文名称。命令会改为显示中文名称。",
    ]
    assert check(home, two) == expect(0, two_en)
    assert check(home, two, "--lang", "zh") == expect(0, two_zh)

    empty = tmp_path / "empty"
    empty.mkdir()
    assert check(home, empty) == expect(1, EMPTY)
    assert check(home, empty, "--lang", "zh") == expect(1, EMPTY_ZH)
