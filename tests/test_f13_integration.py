"""Tests of F13 for shop with the whole program: folders, v0.1 steps, entry point (T23-T28)."""

from datetime import date
from pathlib import Path

import pytest

from f05_support import copy_example, make_home, run_module
from f05_texts import HELP_EN, no_data_folder
from f07_changes import edit, make_init
from f07_support import call, snapshot
from f09_support import at, made
from f09_texts import RUN_HELP_OPTIONS, err, out
from f10_support import bom_and_crlf, chinese_settings
from f11_support import empty_menus, on
from f11_texts import no_menu, not_a_week, not_a_week_zh
from f12_support import s18_changes
from f13_blocks import block_c, block_c_zh, block_g, block_g_zh
from f13_support import (
    empty_shopping,
    pristine,
    shop_file,
    shop_list,
    shopping_as_file,
)
from f13_texts import (
    FILE_47,
    PROTOTYPE_FILE,
    no_dishes,
    no_dishes_zh,
    parent,
    shop_47,
    shop_47_zh,
    shop_fail,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek


def _check_file(root: Path, expected: bytes) -> None:
    """Checks the saved file of 2026-W47: its bytes, no byte order mark, and no CR."""
    data = (root / "shopping" / "2026-W47.md").read_bytes()
    assert data == expected
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in data


def _check_settings_and_bom(home: Path, source: DataFolder, tmp_path: Path) -> None:
    """Inputs 5 and 6 of F13-T23: Chinese settings, and a byte order mark with CRLF."""
    c = made(source, tmp_path, "c", chinese_settings)
    file = c / "shopping" / "2026-W47.md"
    assert at(home, c, "shop", "2026-W47") == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    assert at(home, c, "shop", "2026-W47", "--lang", "en") == out(shop_47(file))
    assert file.read_bytes() == FILE_47
    d = made(source, tmp_path, "d", bom_and_crlf)
    assert at(home, d, "shop", "2026-W47") == out(shop_47(d / "shopping" / "2026-W47.md"))
    _check_file(d, FILE_47)


def test_f13_t23_shop_uses_the_folder_and_the_language_that_cli_picks(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--data``, ``RECIPE_MENU_DATA``, ``~/recipe-menu``, ``--lang``, the settings, and BOM."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    b = copy_example(source, tmp_path / "One Drive" / "菜谱")
    environ = {"RECIPE_MENU_DATA": str(b)}
    shown = at(home, None, "shop", "2026-W47", environ=environ)
    assert shown == out(shop_47(b / "shopping" / "2026-W47.md"))
    _check_file(b, FILE_47)
    assert at(home, None, "shop", "2026-W47") == no_data_folder(home / "recipe-menu")
    by_home = copy_example(source, home / "recipe-menu")
    shown = at(home, None, "shop", "2026-W47")
    assert shown == out(shop_47(by_home / "shopping" / "2026-W47.md"))
    _check_file(by_home, FILE_47)
    cwd = tmp_path / "cwd"
    copy_example(source, cwd / "rel")
    monkeypatch.chdir(cwd)
    shown = call(home, ["shop", "2026-W47", "--data", "rel"])
    assert shown == out(shop_47(Path.cwd() / "rel" / "shopping" / "2026-W47.md"))
    _check_file(Path.cwd() / "rel", FILE_47)
    other = copy_example(source, home / "other")
    shown = call(home, ["shop", "2026-W47", "--data", "~/other"])
    assert shown == out(shop_47(other / "shopping" / "2026-W47.md"))
    _check_file(other, FILE_47)
    _check_settings_and_bom(home, source, tmp_path)


# The dates of F13-T24 with the week of the date and the week 7 days later.
DAYS = [
    (date(2026, 11, 10), "2026-W46", "2026-W47"),
    (date(2026, 12, 30), "2026-W53", "2027-W01"),
    (date(2027, 1, 3), "2026-W53", "2027-W01"),
]


def test_f13_t24_v0_1_s14_a_new_empty_menu_gives_no_dishes_and_saves_nothing(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``menu new`` makes two empty menus, and ``shop`` says that there is nothing to buy."""
    home = make_home(tmp_path)
    for number, (today, this, following) in enumerate(DAYS):
        root = made(example_folder, tmp_path, f"day{number}", empty_menus, empty_shopping)
        assert on(home, root, today, "menu", "new")[0] == 0
        assert on(home, root, today, "menu", "new", "next")[0] == 0
        names = sorted(path.name for path in (root / "menus").iterdir())
        assert names == sorted([f"{this}.toml", f"{following}.toml"])
        assert on(home, root, today, "shop") == out([no_dishes(this)])
        assert on(home, root, today, "shop", "next") == out([no_dishes(following)])
        assert on(home, root, today, "shop", "this", "--lang", "zh") == out([no_dishes_zh(this)])
        assert list((root / "shopping").iterdir()) == []


def test_f13_t25_v0_1_s16_the_settings_name_the_meals_and_the_servings_of_the_list(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The init folder with three meals and 3 servings: a new menu, one dish, and the list."""
    home = make_home(tmp_path)
    root = make_init(example_folder, tmp_path / "init")
    settings = root / "settings.toml"
    edit(settings, 'meals = ["lunch", "dinner"]', 'meals = ["breakfast", "lunch", "dinner"]')
    edit(settings, "servings = 2 ", "servings = 3 ")
    file = root / "shopping" / "2026-W48.md"
    assert at(home, root, "menu", "new", "2026-W48")[0] == 0
    edit(
        root / "menus" / "2026-W48.toml",
        "[monday]\nbreakfast = []",
        '[monday]\nbreakfast = ["tomato-egg"]',
    )
    assert at(home, root, "menu", "show", "2026-W48")[0] == 0
    english = at(home, root, "shop", "2026-W48")
    assert english == out(block_c(file))
    assert (
        english[1].split("\n")[0]
        == "Shopping list for 2026-W48, 23 to 29 November 2026: 1 meal, 1 dish"
    )
    assert english[1].split("\n")[-4] == (
        "Not on the list, because they are in the pantry: Cooking oil, Salt, Sugar"
    )
    assert at(home, root, "shop", "2026-W48", "--lang", "zh") == out(block_c_zh(file))


def test_f13_t26_v0_1_s18_amounts_that_cannot_be_added_share_one_line(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Amounts that cannot be added share one line, in English and in Chinese."""
    home = make_home(tmp_path)
    root = made(example_folder, tmp_path, "s18", lambda path: s18_changes(DataFolder(path)))
    file = root / "shopping" / "2026-W48.md"
    shopping = shop_list(DataFolder(root), IsoWeek(2026, 48))
    english = at(home, root, "shop", "2026-W48")
    assert english == out(block_g(file))
    assert "  Scallion       5 stalks + 1 bunch\n" in english[1]
    assert "  Soy sauce      30 ml + 10 g\n" in english[1]
    assert file.read_bytes() == shop_file(shopping, Lang.EN)
    assert b"- [ ] Scallion 5 stalks + 1 bunch\n" in file.read_bytes()
    chinese = at(home, root, "shop", "2026-W48", "--lang", "zh")
    assert chinese == out(block_g_zh(file))
    assert "  葱         5 根 + 1 把\n" in chinese[1]
    assert "  生抽       30 ml + 10 g\n" in chinese[1]
    assert file.read_bytes() == shop_file(shopping, Lang.ZH)
    assert "- [ ] 葱 5 根 + 1 把\n".encode() in file.read_bytes()


def test_f13_t27_v0_1_s23_two_runs_change_only_the_list_file_of_the_week(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A snapshot of ``home`` and of the current folder is the same after each run but one file."""
    home = make_home(tmp_path)
    root = copy_example(pristine(example_folder, tmp_path), home / "recipe-menu")
    (root / "shopping").mkdir()
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    tag = '"shop" has no option "--tag". It has no options of its own.'
    before = (snapshot(home), snapshot(cwd))
    assert at(home, None, "shop", "2026-W48") == err(1, [no_menu("2026-W48")])
    assert at(home, None, "shop", "2026-W99") == err(2, [not_a_week("2026-W99")])
    assert at(home, None, "shop", "--help") == (0, HELP_EN, "")
    assert at(home, None, "shop", "--tag", "x") == err(2, [tag, RUN_HELP_OPTIONS[0]])
    assert (snapshot(home), snapshot(cwd)) == before
    skip = {"recipe-menu/shopping", "recipe-menu/shopping/2026-W47.md"}
    file = root / "shopping" / "2026-W47.md"
    for _ in range(2):
        before = (snapshot(home), snapshot(cwd))
        assert at(home, None, "shop", "2026-W47") == out(shop_47(file))
        after = snapshot(home)
        assert {k: v for k, v in after.items() if k not in skip} == {
            k: v for k, v in before[0].items() if k not in skip
        }
        assert after["recipe-menu/shopping/2026-W47.md"][0] == FILE_47
        assert [path.name for path in (root / "shopping").iterdir()] == ["2026-W47.md"]
        assert snapshot(cwd) == before[1]


def test_f13_t28_python_dash_m_runs_shop_and_writes_utf8(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The real entry point: a Chinese list, an English list, a wrong week, no menu, a file."""
    source = pristine(example_folder, tmp_path)
    root = example_folder.root
    file = example_folder.shopping_file("2026-W47")
    zh = run_module(tmp_path, "shop", "2026-W47", "--lang", "zh", "--data", str(root))
    assert zh == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    en = run_module(tmp_path, "shop", "2026-W47", "--data", str(root))
    assert en == out(shop_47(file))
    assert file.read_bytes() == FILE_47
    wrong = run_module(tmp_path, "shop", "2026-W99", "--lang", "zh", "--data", str(root))
    assert wrong == err(2, [not_a_week_zh("2026-W99")])
    assert run_module(tmp_path, "shop", "2026-W48", data=root) == err(1, [no_menu("2026-W48")])
    x = made(source, tmp_path, "x", shopping_as_file)
    shown = run_module(tmp_path, "shop", "2026-W47", "--data", str(x))
    path = x / "shopping" / "2026-W47.md"
    assert shown == err(1, shop_fail(path, parent("shopping")))
