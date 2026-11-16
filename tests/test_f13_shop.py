"""Tests of F13 for shop with the real commands: the example and other weeks (T11 to T14)."""

import re
import shutil
from collections.abc import Callable
from pathlib import Path

from f03_support import put_bytes, write
from f05_support import make_home
from f07_changes import edit
from f07_texts import TYPO
from f09_support import at, made
from f09_texts import err, out, stop
from f10_support import chinese_settings
from f11_support import empty_menus, held, menu_text, week_b
from f11_texts import no_menu, not_a_week
from f12_support import LUNCH_DINNER, s16_folder
from f13_blocks import (
    FILE_E,
    FILE_E_ZH,
    FILE_F,
    FILE_F_ZH,
    block_b,
    block_b_zh,
    block_c,
    block_c_zh,
    block_d,
    block_e,
    block_e_zh,
    block_f,
    block_f_zh,
    block_h,
    block_h_zh,
    file_h,
    file_h_zh,
)
from f13_support import (
    LISTINGS,
    READ_SETTINGS,
    chicken_break,
    egg_week,
    empty_shopping,
    meat_break,
    old_temp,
    rice_week,
    shop_faults,
    shop_file,
    shop_lines,
    shop_list,
    ticked_list,
    water_week,
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
from recipe_menu.text import display_width

Lines = Callable[[Path], list[str]]


def _amount_columns(lines: list[str], count: int) -> set[int]:
    """Gives the display widths of what comes before the amount in each line of a group.

    A line of a group starts with two spaces. The check also counts those lines.
    """
    widths = set()
    group = [line for line in lines if line.startswith("  ")]
    assert len(group) == count, group
    for line in group:
        found = re.match(r"(  \S.*?\s{3,})\S", line)
        assert found is not None, line
        widths.add(display_width(found.group(1)))
    return widths


def _iso(week: str) -> IsoWeek:
    """Gives the ``IsoWeek`` of a text such as ``2026-W47``, read by ``IsoWeek.parse``."""
    parsed = IsoWeek.parse(week)
    assert parsed is not None, week
    return parsed


def test_f13_t11_the_example_of_shop_holds_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The English list that makes ``shopping/``, the Chinese file, no menu, a mistake, a file."""
    home = make_home(tmp_path)
    folder = example_folder
    file = folder.shopping_file("2026-W47")
    assert not folder.shopping.exists()
    assert at(home, folder, "shop", "2026-W47") == out(shop_47(file))
    assert at(home, folder, "shop", "2026-W47", "--lang", "zh") == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]
    assert at(home, folder, "shop", "2026-W48") == err(1, [no_menu("2026-W48")])
    assert at(home, folder, "shop", "2026-W99") == err(2, [not_a_week("2026-W99")])
    edit(folder.menu_file("2026-W47"), '"tomato-egg"', '"tomato-eggs"')
    assert at(home, folder, "shop", "next") == stop(TYPO)
    assert file.read_bytes() == PROTOTYPE_FILE
    assert at(home, folder, "menu", "new", "this")[0] == 0
    assert at(home, folder, "shop") == out([no_dishes("2026-W46")])
    assert at(home, folder, "shop", "this", "--lang", "zh") == out([no_dishes_zh("2026-W46")])
    assert [path.name for path in folder.shopping.iterdir()] == ["2026-W47.md"]
    edit(folder.menu_file("2026-W47"), '"tomato-eggs"', '"tomato-egg"')
    shutil.rmtree(folder.shopping)
    write(folder.shopping, "")
    result = at(home, folder, "shop", "2026-W47")
    assert result == err(1, shop_fail(file, parent("shopping")))
    assert folder.shopping.read_bytes() == b""


def test_f13_t12_v0_1_s17_replaces_the_file_of_the_week_in_the_language_of_the_run(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype's outputs and file, a ticked list that loses its ticks, and the builders."""
    home = make_home(tmp_path)
    x = made(example_folder, tmp_path, "x")
    file = x / "shopping" / "2026-W47.md"
    assert not (x / "shopping").exists()
    english = at(home, x, "shop", "2026-W47")
    assert english == out(shop_47(file))
    assert [path.name for path in file.parent.iterdir()] == ["2026-W47.md"]
    data = file.read_bytes()
    assert data == FILE_47
    assert not data.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in data
    assert sum(line.startswith(b"- [ ] ") for line in data.split(b"\n")) == 14
    chinese = at(home, x, "shop", "2026-W47", "--lang", "zh")
    assert chinese == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    assert [path.name for path in file.parent.iterdir()] == ["2026-W47.md"]
    assert _amount_columns(english[1].split("\n"), 14) == {18}
    assert _amount_columns(chinese[1].split("\n"), 14) == {15}
    ticked_list(x)
    old_temp(x)
    assert at(home, x, "shop", "next") == out(shop_47(file))
    assert file.read_bytes() == FILE_47
    assert b"- [x]" not in file.read_bytes()
    assert [path.name for path in file.parent.iterdir()] == ["2026-W47.md"]
    assert at(home, x, "shop", "next", "--lang", "zh") == out(shop_47_zh(file))
    assert file.read_bytes() == PROTOTYPE_FILE
    y = made(example_folder, tmp_path, "y", chinese_settings, empty_shopping)
    shown = y / "shopping" / "2026-W47.md"
    assert at(home, y, "shop", "2026-W47") == out(shop_47_zh(shown))
    assert shown.read_bytes() == PROTOTYPE_FILE
    assert at(home, y, "shop", "2026-W47", "--lang", "en") == out(shop_47(shown))
    assert shown.read_bytes() == FILE_47
    week = shop_list(DataFolder(x), IsoWeek(2026, 47))
    assert shop_lines(week, Lang.EN, file) == shop_47(file)
    assert shop_lines(week, Lang.ZH, file) == shop_47_zh(file)
    assert shop_file(week, Lang.EN) == FILE_47
    assert shop_file(week, Lang.ZH) == PROTOTYPE_FILE


def _run_both(home: Path, root: Path, week: str, blocks: tuple[Lines, Lines]) -> list[list[str]]:
    """Runs ``shop`` in English and in Chinese, and checks the outputs, the files, and builders.

    Args:
        home: The home folder.
        root: The data folder.
        week: The week to run, such as ``2026-W48``.
        blocks: The functions that give the two outputs for the list file.

    Returns:
        The two outputs as lines.
    """
    folder = DataFolder(root)
    file = folder.shopping_file(week)
    shopping = shop_list(folder, _iso(week))
    shown = []
    for lang, argv, block in ((Lang.EN, [], blocks[0]), (Lang.ZH, ["--lang", "zh"], blocks[1])):
        result = at(home, root, "shop", week, *argv)
        assert result == out(block(file)), lang
        assert held(file) == shop_file(shopping, lang), lang
        assert shop_lines(shopping, lang, file) == block(file), lang
        shown.append(result[1].split("\n"))
    return shown


def _check_week_b(example: DataFolder, home: Path, tmp_path: Path) -> None:
    """Input 1 of F13-T13: week B, with ``Pork belly`` before ``Minced pork``."""
    root = made(example, tmp_path, "b", week_b)
    english, chinese = _run_both(home, root, "2026-W48", (block_b, block_b_zh))
    assert _amount_columns(english, 10) == {16}
    assert _amount_columns(chinese, 10) == {15}
    top = b"# Shopping list for 2026-W48\n\n23 to 29 November 2026: 4 meals, 5 dishes.\n"
    file = root / "shopping" / "2026-W48.md"
    assert at(home, root, "shop", "2026-W48") == out(block_b(file))
    assert file.read_bytes().startswith(top)


def _check_s16(example: DataFolder, home: Path, tmp_path: Path) -> None:
    """Input 2 of F13-T13: the S16 folder."""
    folder = s16_folder(example, tmp_path / "init")
    english, chinese = _run_both(home, folder.root, "2026-W48", (block_c, block_c_zh))
    assert _amount_columns(english, 3) == {13}
    assert _amount_columns(chinese, 3) == {9}


def _check_chicken_break(example: DataFolder, home: Path, tmp_path: Path) -> None:
    """Input 3 of F13-T13: each line break of the chicken break gives the same output."""
    for number, escape in enumerate(["\\n", "\\r\\n", "\\u2028"]):
        root = made(example, tmp_path, f"d{number}", chicken_break(escape))
        file = root / "shopping" / "2026-W47.md"
        result = at(home, root, "shop", "2026-W47")
        assert result == out(block_d(file)), escape
        assert "\r" not in result[1]
        assert "\u2028" not in result[1]
        assert "  wings\n" in result[1]
        shopping = shop_list(DataFolder(root), IsoWeek(2026, 47))
        assert file.read_bytes() == shop_file(shopping, Lang.EN)
        assert shop_lines(shopping, Lang.EN, file) == block_d(file)
        if escape == "\\n":
            assert b"- [ ] Chicken\nwings 1 kg\n" in file.read_bytes()


def _check_meat_break_and_rice(example: DataFolder, home: Path, tmp_path: Path) -> None:
    """Inputs 4 and 5 of F13-T13: a category with a line break, and a week with no pantry line."""
    root = made(example, tmp_path, "meat", meat_break)
    file = root / "shopping" / "2026-W47.md"
    lines = shop_47(file)
    place = lines.index("Meat and seafood")
    lines[place : place + 1] = ["Meat", "and seafood"]
    assert at(home, root, "shop", "2026-W47") == out(lines)
    assert file.read_bytes() == FILE_47.replace(b"## Meat and seafood\n", b"## Meat\nand seafood\n")
    root = made(example, tmp_path, "h", rice_week("2026-W49"))
    en, zh = "30 November to 6 December 2026", "2026年11月30日至12月6日"
    blocks = (
        lambda path: block_h("2026-W49", en, path),
        lambda path: block_h_zh("2026-W49", zh, path),
    )
    english, chinese = _run_both(home, root, "2026-W49", blocks)
    assert not any("pantry" in line for line in english)
    assert not any("常备" in line for line in chinese)
    file = root / "shopping" / "2026-W49.md"
    assert at(home, root, "shop", "2026-W49")[0] == 0
    assert file.read_bytes() == file_h("2026-W49", en)
    assert at(home, root, "shop", "2026-W49", "--lang", "zh")[0] == 0
    assert file.read_bytes() == file_h_zh("2026-W49", zh)


def test_f13_t13_each_week_gets_the_width_of_its_own_names(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Week B, the S16 folder, the chicken break, the meat break, and the rice week."""
    home = make_home(tmp_path)
    _check_week_b(example_folder, home, tmp_path)
    _check_s16(example_folder, home, tmp_path)
    _check_chicken_break(example_folder, home, tmp_path)
    _check_meat_break_and_rice(example_folder, home, tmp_path)


def _nothing_input(
    example: DataFolder, tmp_path: Path, name: str, with_shopping: bool = False
) -> Path:
    """Makes an empty-menus example with ``menus/2026-W46.toml``, and an empty shopping if asked."""
    root = made(example, tmp_path, name, empty_menus)
    put_bytes(root / "menus" / "2026-W46.toml", menu_text("2026-W46", LUNCH_DINNER))
    if with_shopping:
        empty_shopping(root)
    return root


def _check_no_dishes(home: Path, root: Path) -> None:
    """Runs ``shop`` and ``shop this --lang zh`` for 2026-W46: the line, and the calls."""
    lines = (
        (("shop",), no_dishes("2026-W46")),
        (("shop", "this", "--lang", "zh"), no_dishes_zh("2026-W46")),
    )
    for argv, line in lines:
        with shop_faults(root) as state:
            assert at(home, root, *argv) == out([line])
        assert state.calls == [
            READ_SETTINGS,
            "read catalog.toml",
            "read pantry.toml",
            "read menus/2026-W46.toml",
        ]
        assert state.listings == LISTINGS


def test_f13_t14_a_week_with_no_dish_saves_nothing_and_nothing_to_buy_saves_a_file(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``NO_DISHES``, the old file that stays, the water week, and the egg week."""
    home = make_home(tmp_path)
    x = _nothing_input(example_folder, tmp_path, "x")
    _check_no_dishes(home, x)
    assert not (x / "shopping").exists()
    y = _nothing_input(example_folder, tmp_path, "y", True)
    old = y / "shopping" / "2026-W46.md"
    put_bytes(old, b"old\n")
    stamp = old.stat().st_mtime_ns
    _check_no_dishes(home, y)
    assert [path.name for path in old.parent.iterdir()] == ["2026-W46.md"]
    assert (old.read_bytes(), old.stat().st_mtime_ns) == (b"old\n", stamp)
    z = made(example_folder, tmp_path, "z")
    write(z / "menus" / "2026-W52.toml", 'week = "2026-W52"\n')
    assert at(home, z, "shop", "2026-W52") == out([no_dishes("2026-W52")])
    assert not (z / "shopping").exists()
    water = (water_week, "2026-W50", (block_e, block_e_zh), (FILE_E, FILE_E_ZH))
    eggs = (egg_week, "2026-W51", (block_f, block_f_zh), (FILE_F, FILE_F_ZH))
    for change, week, blocks, files in (water, eggs):
        root = made(example_folder, tmp_path, f"week-{week}", change)
        _run_both(home, root, week, blocks)
        file = root / "shopping" / f"{week}.md"
        assert file.read_bytes() == files[1]
        shopping = shop_list(DataFolder(root), _iso(week))
        assert (shop_file(shopping, Lang.EN), shop_file(shopping, Lang.ZH)) == files
