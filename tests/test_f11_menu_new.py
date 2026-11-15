"""Tests of F11 for recipe-menu menu new: the example, the file, the language, and the weeks."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f07_support import AFTER, AFTER_ZH
from f08_support import EXAMPLE
from f09_support import at, made
from f09_texts import FOLDER_MISSING, err, out
from f10_support import chinese_settings
from f11_support import (
    SET_LABELS,
    SETS,
    empty_menus,
    held,
    meal_set,
    meals_of,
    menu_text,
    no_menus_folder,
)
from f11_texts import (
    DATES,
    EVERY_MEAL,
    LUNCH_DINNER,
    PROTOTYPE_FILE,
    SHOW_47,
    SHOW_47_ZH,
    empty,
    exists,
    exists_zh,
    fail,
    new,
    new_zh,
    not_a_week,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek, read_week_menu
from recipe_menu.recipes import list_recipe_ids
from recipe_menu.settings import Settings

WEEK_47 = "2026-W47"
LUNCH_DINNER_EN = "lunch and dinner"
LUNCH_DINNER_ZH = "午餐和晚餐"


def test_f11_t15_the_example_of_menu_new_runs_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.2, in order: a new menu, a refusal, three meals, and a missing folder."""
    home = make_home(tmp_path)
    folder = example_folder
    empty_menus(folder.root)
    file = folder.menu_file(WEEK_47)
    expected = out(new(file, DATES[WEEK_47][0], LUNCH_DINNER_EN))
    assert at(home, folder, "menu", "new", "next") == expected
    assert held(file) == menu_text(WEEK_47, LUNCH_DINNER)
    made_at = file.stat().st_mtime_ns
    assert at(home, folder, "menu", "new", "next", "--lang", "zh") == err(1, [exists_zh(file)])
    assert file.stat().st_mtime_ns == made_at
    write(folder.settings, 'meals = ["breakfast", "lunch", "dinner"]\n')
    file = folder.menu_file("2026-W48")
    expected = out(new(file, DATES["2026-W48"][0], "breakfast, lunch, and dinner"))
    assert at(home, folder, "menu", "new", "2026-W48") == expected
    assert held(file) == menu_text("2026-W48", EVERY_MEAL)
    wrong_case = folder.menus / "2026-w49.toml"
    write(wrong_case, "")
    assert at(home, folder, "menu", "new", "2026-W49") == err(1, [exists(wrong_case)])
    names = sorted(path.name for path in folder.menus.iterdir())
    assert names == ["2026-W47.toml", "2026-W48.toml", "2026-w49.toml"]
    assert at(home, folder, "menu", "new", "2026-W99") == err(2, [not_a_week("2026-W99")])
    no_menus_folder(folder.root)
    result = at(home, folder, "menu", "new", "2026-W50")
    assert result == err(1, fail(folder.menus, FOLDER_MISSING))
    assert not folder.menus.exists()


def test_f11_t16_v0_1_s13_creates_the_prototype_file_and_the_week_shows_after_it_is_filled(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype "Create next week's menu" and "Show the week after you fill it"."""
    home = make_home(tmp_path)
    x = made(example_folder, tmp_path, "x", empty_menus)
    file = x / "menus" / "2026-W47.toml"
    first = out(new(file, DATES[WEEK_47][0], LUNCH_DINNER_EN))
    assert at(home, x, "menu", "new", "2026-W47") == first
    data = held(file)
    assert data == PROTOTYPE_FILE
    assert data is not None
    assert data.isascii()
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in data
    made_at = file.stat().st_mtime_ns
    refused = err(1, [exists_zh(file)])
    assert at(home, x, "menu", "new", "2026-W47", "--lang", "zh") == refused
    assert (held(file), file.stat().st_mtime_ns) == (PROTOTYPE_FILE, made_at)
    write(file, (EXAMPLE / "menus" / "2026-W47.toml").read_text(encoding="utf-8"))
    assert at(home, x, "check") == out(AFTER)
    assert at(home, x, "menu", "show", "2026-W47") == out(SHOW_47)
    assert at(home, x, "menu", "show", "2026-W47", "--lang", "zh") == out(SHOW_47_ZH)
    y = made(example_folder, tmp_path, "y", empty_menus)
    file = y / "menus" / "2026-W47.toml"
    assert at(home, y, "menu", "new", "next") == out(new(file, DATES[WEEK_47][0], LUNCH_DINNER_EN))
    assert at(home, y, "menu", "new", "next", "--lang", "zh") == err(1, [exists_zh(file)])
    assert held(file) == PROTOTYPE_FILE


def _check_sets(example: DataFolder, tmp_path: Path, home: Path) -> None:
    """Runs input 1 of F11-T17: the seven sets of meals in two lines each."""
    for number, (words, (label, label_zh)) in enumerate(zip(SETS, SET_LABELS, strict=True)):
        root = meal_set(example, tmp_path, f"set{number}", words)
        meals = meals_of(words)
        first, second = root / "menus" / "2026-W47.toml", root / "menus" / "2026-W48.toml"
        result = at(home, root, "menu", "new", "2026-W47")
        assert result == out(new(first, DATES["2026-W47"][0], label)), words
        result = at(home, root, "menu", "new", "2026-W48", "--lang", "zh")
        assert result == out(new_zh(second, DATES["2026-W48"][1], label_zh)), words
        assert held(first) == menu_text("2026-W47", meals), words
        assert held(second) == menu_text("2026-W48", meals), words


def test_f11_t17_the_file_has_the_lines_of_2_2_for_each_set_of_meals_and_each_week(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven sets of meals, six weeks in both languages, and the builder of the test."""
    home = make_home(tmp_path)
    _check_sets(example_folder, tmp_path, home)
    weeks = ["2026-W49", "2026-W53", "2026-W01", "2027-W01", "2026-W23", "2020-W53"]
    a = made(example_folder, tmp_path, "a", empty_menus)
    b = made(example_folder, tmp_path, "b", empty_menus)
    for week in weeks:
        english, chinese = DATES[week]
        file_a, file_b = a / "menus" / f"{week}.toml", b / "menus" / f"{week}.toml"
        result = at(home, a, "menu", "new", week)
        assert result == out(new(file_a, english, LUNCH_DINNER_EN)), week
        result = at(home, b, "menu", "new", week, "--lang", "zh")
        assert result == out(new_zh(file_b, chinese, LUNCH_DINNER_ZH)), week
        for file in (file_a, file_b):
            assert held(file) == menu_text(week, LUNCH_DINNER), week
            assert held(file) is not None
        first_line = f"# {week}: {english}\n".encode()
        assert (held(file_a) or b"").startswith(first_line), week
    assert menu_text(WEEK_47, LUNCH_DINNER) == PROTOTYPE_FILE


def test_f11_t18_lang_and_the_language_of_the_settings_change_the_output_and_not_the_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``--lang zh`` and ``language = "zh"`` give the Chinese lines and the same file."""
    home = make_home(tmp_path)
    x = made(example_folder, tmp_path, "x", empty_menus)
    file = x / "menus" / "2026-W47.toml"
    result = at(home, x, "menu", "new", "2026-W47", "--lang", "zh")
    assert result == out(new_zh(file, DATES[WEEK_47][1], LUNCH_DINNER_ZH))
    assert held(file) == PROTOTYPE_FILE
    y = made(example_folder, tmp_path, "y", empty_menus, chinese_settings)
    first, second = y / "menus" / "2026-W47.toml", y / "menus" / "2026-W48.toml"
    result = at(home, y, "menu", "new", "2026-W47")
    assert result == out(new_zh(first, DATES[WEEK_47][1], LUNCH_DINNER_ZH))
    assert held(first) == PROTOTYPE_FILE
    result = at(home, y, "menu", "new", "2026-W48", "--lang", "en")
    assert result == out(new(second, DATES["2026-W48"][0], LUNCH_DINNER_EN))
    assert held(second) == menu_text("2026-W48", LUNCH_DINNER)
    assert at(home, y, "menu", "new", "2026-W47", "--lang", "en") == err(1, [exists(first)])
    assert at(home, y, "menu", "new", "2026-W48") == err(1, [exists_zh(second)])


def _check_reads(root: Path, words: tuple[str, ...]) -> None:
    """Checks that ``read_week_menu`` reads the new file with no problem and every slot empty."""
    folder = DataFolder(root)
    ids = frozenset(list_recipe_ids(folder)[0])
    week = IsoWeek(2026, 47)
    meals = tuple(meals_of(words))
    for settings in (Settings(Lang.EN, meals, 2), Settings()):
        menu, problems = read_week_menu(folder, week, settings, ids)
        assert problems == (), (words, settings)
        assert menu is not None
        assert menu.meals == settings.meals
        slots = {(slot.day, slot.meal): slot.dishes for slot in menu.slots}
        assert len(slots) == 7 * len(settings.meals)
        assert set(slots.values()) == {()}
    assert read_week_menu(folder, week, None, ids) == (None, ())


def test_f11_t19_read_week_menu_and_check_and_menu_show_accept_the_new_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The new file has no problem and no dish for every set, and then for the example."""
    home = make_home(tmp_path)
    two_menus = [line.replace("1 week menu", "2 week menus") for line in AFTER]
    two_menus_zh = [line.replace("1 个周菜单", "2 个周菜单") for line in AFTER_ZH]
    for number, words in enumerate(SETS):
        root = meal_set(example_folder, tmp_path, f"set{number}", words)
        meals = meals_of(words)
        assert at(home, root, "menu", "new", "2026-W47")[0] == 0
        assert at(home, root, "menu", "new", "2026-W48", "--lang", "zh")[0] == 0
        assert held(Path(root, "menus", "2026-W47.toml")) == menu_text("2026-W47", meals)
        assert held(Path(root, "menus", "2026-W48.toml")) == menu_text("2026-W48", meals)
        _check_reads(root, words)
        assert at(home, root, "check") == out(two_menus)
        assert at(home, root, "menu", "show", "2026-W47") == out(empty("2026-W47", Lang.EN, meals))
        shown = at(home, root, "menu", "show", "2026-W48", "--lang", "zh")
        assert shown == out(empty("2026-W48", Lang.ZH, meals))
    file = example_folder.menu_file("2026-W48")
    expected = out(new(file, DATES["2026-W48"][0], LUNCH_DINNER_EN))
    assert at(home, example_folder, "menu", "new", "2026-W48") == expected
    assert held(file) == menu_text("2026-W48", LUNCH_DINNER)
    assert at(home, example_folder, "check") == out(two_menus)
    assert at(home, example_folder, "check", "--lang", "zh") == out(two_menus_zh)
