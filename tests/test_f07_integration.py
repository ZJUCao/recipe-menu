"""Tests of F07 for the scenarios and the prototypes at main and at the entry point (T18 to T23)."""

from pathlib import Path

from f03_support import edit_ingredients, ing, put_bytes, write
from f05_support import copy_example, make_home, run_module
from f07_changes import edit, make_init, mapo_mistake, s07_mistakes, the_comma, the_typo, undo_two
from f07_support import AFTER, TWO, TWO_ZH, check, expect, rep, snapshot
from f07_texts import MISSING_BRACKET, PORK, Prob, m_unknown_ingredient, p_ingredient, p_line
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang

CUCUMBER = (
    'name = { zh = "拍黄瓜", en = "Smashed cucumber" }',
    "servings = 2",
    'tags = ["快手", "素"]',
    "ingredients = [",
    '  { item = "黄瓜", amount = "2 个" },',
    '  { item = "大蒜", amount = "2 瓣" },',
    "]",
    "[steps]",
    'zh = ["黄瓜拍碎，加蒜末拌匀。"]',
    'en = ["Smash the cucumbers and toss them with the garlic."]',
)
ONE_RECIPE = "Checked the settings, the catalog, the pantry, 1 recipe, and 0 week menus."
ONE_RECIPE_ZH = "已检查设置、目录、常备清单、1 个菜谱和 0 个周菜单。"


def test_f07_t18_scenario_s05_gives_the_two_outputs_and_the_report_after_the_fixes(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The two mistakes in English and Chinese, then the fixes, with the folder at the home."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    mapo_mistake(root)
    the_typo(root)
    assert check(home, None) == expect(1, TWO)
    assert check(home, None, "--lang", "zh") == expect(1, TWO_ZH)
    undo_two(root, example_folder)
    assert check(home, None) == expect(0, AFTER)


def test_f07_t19_a_syntax_mistake_on_the_init_folder_and_on_the_example_folder(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S06 on the init folder, and design 2.2 with its warning on the example folder."""
    home = make_home(tmp_path)
    init = make_init(example_folder, home / "recipe-menu")
    the_comma(init)
    english = [
        ONE_RECIPE,
        "",
        "1 error:",
        "  pantry.toml, line 2",
        '    The file cannot be read: a closing "]" is missing.',
        "",
        'Fix the errors and run "recipe-menu check" again.',
    ]
    chinese = [
        ONE_RECIPE_ZH,
        "",
        "1 个错误：",
        "  pantry.toml，第 2 行",
        "    无法读取文件：缺少右方括号“]”。",
        "",
        "改正错误后，再运行“recipe-menu check”。",
    ]
    assert check(home, None) == expect(1, english)
    assert check(home, None, "--lang", "zh") == expect(1, chinese)

    root = copy_example(example_folder, tmp_path / "example")
    the_comma(root)
    problem = Prob("pantry.toml", p_line(2), MISSING_BRACKET)
    assert check(home, root) == rep(1, 7, 1, [problem], [PORK])
    assert check(home, root, "--lang", "zh") == rep(1, 7, 1, [problem], [PORK], Lang.ZH)


def test_f07_t20_the_init_folder_checks_clean_and_a_new_recipe_is_checked(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S01 step 2, S02 step 2, and S04 on the init folder."""
    home = make_home(tmp_path)
    root = make_init(example_folder, home / "recipe-menu")
    clean = [ONE_RECIPE, "", "No errors. No warnings."]
    clean_zh = [ONE_RECIPE_ZH, "", "没有错误，也没有警告。"]
    assert check(home, None) == expect(0, clean)

    settings = root / "settings.toml"
    original = settings.read_text(encoding="utf-8")
    edit(settings, 'language = "en"', 'language = "zh"')
    assert check(home, None) == expect(0, clean_zh)

    write(settings, original)
    write(root / "recipes" / "cucumber-salad.toml", "".join(f"{line}\n" for line in CUCUMBER))
    unknown = Prob("recipes/cucumber-salad.toml", p_ingredient(1), m_unknown_ingredient("黄瓜"))
    assert check(home, None) == rep(1, 2, 0, [unknown], [])

    edit_ingredients(DataFolder(root), added=[ing("黄瓜", "Cucumber")])
    two = "Checked the settings, the catalog, the pantry, 2 recipes, and 0 week menus."
    assert check(home, None) == expect(0, [two, "", "No errors. No warnings."])


def test_f07_t21_a_byte_order_mark_and_crlf_line_ends_give_the_same_report(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.1-S08 step 1: every .toml file written with a BOM and CRLF checks as before."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    for path in sorted(root.rglob("*.toml")):
        text = path.read_bytes().decode("utf-8")
        put_bytes(path, b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    assert check(home, None) == expect(0, AFTER)


def test_f07_t22_check_writes_no_file_and_keeps_no_state(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Every file and folder keeps its bytes and its time, and a line gives equal results."""
    home = make_home(tmp_path)
    root = example_folder.root
    mistaken = copy_example(example_folder, tmp_path / "mistaken")
    s07_mistakes(mistaken)
    empty = tmp_path / "empty"
    empty.mkdir()
    before = snapshot(tmp_path)
    lines = [
        (root,),
        (root, "--lang", "zh"),
        (mistaken,),
        (empty,),
        (None,),
        (root, "--help"),
        (root, "extra"),
    ]
    results = []
    for folder, *argv in lines:
        first = check(home, folder, *argv)
        assert check(home, folder, *argv) == first, (folder, argv)
        results.append(first)
    assert results[0] == expect(0, AFTER)
    assert snapshot(tmp_path) == before


def test_f07_t23_the_entry_point_writes_the_report_as_utf8(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Python -m recipe_menu check, with the encoding of its streams set to ascii."""
    root = example_folder.root
    pristine = DataFolder(copy_example(example_folder, tmp_path / "pristine"))
    mapo_mistake(root)
    the_typo(root)
    assert run_module(tmp_path, "check", "--data", str(root)) == expect(1, TWO)
    zh = run_module(tmp_path, "check", "--data", str(root), "--lang", "zh")
    assert zh == expect(1, TWO_ZH)
    undo_two(root, pristine)
    assert run_module(tmp_path, "check", data=root) == expect(0, AFTER)
