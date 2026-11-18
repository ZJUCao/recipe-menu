"""Tests of F14 on the PT01 data folder, which holds 1,000 recipes: v0.2-S16 step 1 (T34)."""

from pathlib import Path

from f05_support import make_home
from f07_support import check, expect
from f09_texts import out
from f14_support import EVERY_MEAL, filled, new_menu, one_each, picks, seeded, suggest, week_line
from f14_texts import first
from pt01_support import PT01_LINES, make_pt01

WEEK = "2026-W53"


def test_f14_t34_v0_2_s16_a_folder_of_1000_recipes_gives_21_different_recipes_to_a_week(
    tmp_path: Path,
) -> None:
    """The command reads every recipe and fills 21 meals, and ``check`` finds no problem."""
    home = make_home(tmp_path)
    root = tmp_path / "pt01"
    make_pt01(root)
    new_menu(WEEK, EVERY_MEAL)(root)
    ids = sorted(path.stem for path in (root / "recipes").glob("*.toml"))
    assert len(ids) == 1000
    assert suggest(home, root, *week_line(WEEK), random=seeded(53)) == out(first(WEEK, 21))
    file = root / "menus" / f"{WEEK}.toml"
    chosen = picks(53, ids, 21)
    assert len(set(chosen)) == 21
    assert file.read_bytes() == filled(WEEK, EVERY_MEAL, one_each(chosen))
    lines = [PT01_LINES[0].replace("52 week menus", "53 week menus"), *PT01_LINES[1:]]
    assert check(home, root) == expect(0, lines)
