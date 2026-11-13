"""Test of F07 for recipe-menu check on random mixes of mistakes (T24)."""

import random
import shutil
from collections.abc import Callable
from pathlib import Path

from f03_support import write
from f05_support import copy_example, make_home
from f07_changes import (
    add_friday_key,
    add_monday_breakfast,
    broken_settings,
    catalog_brace,
    catalog_s07,
    catalog_two,
    edit,
    mapo_mistake,
    menu_copy,
    menu_path,
    pantry_not_text,
    pantry_sesame,
    pork_in_english,
    servings_zero,
    the_comma,
    the_typo,
)
from f07_support import check, expected_report
from recipe_menu.datafile import DataFolder

type Change = Callable[[Path], None]


def _remove(relative: str) -> Change:
    """Makes a change that deletes a file or a folder of the data folder."""

    def change(root: Path) -> None:
        """Deletes the file or the folder."""
        target = root / relative
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

    return change


def _write(relative: str, text: str) -> Change:
    """Makes a change that writes a file of the data folder."""

    def change(root: Path) -> None:
        """Writes the file."""
        write(root / relative, text)

    return change


def _mkdir(relative: str) -> Change:
    """Makes a change that makes an empty folder in the data folder."""

    def change(root: Path) -> None:
        """Makes the folder."""
        (root / relative).mkdir()

    return change


def _edit(relative: str, old: str, new: str) -> Change:
    """Makes a change that replaces the first ``old`` of a file by ``new``."""

    def change(root: Path) -> None:
        """Replaces the text."""
        edit(root / relative, old, new)

    return change


def _friday(root: Path) -> None:
    """Adds ``supper = []`` to Friday."""
    add_friday_key(menu_path(root))


def _breakfast(root: Path) -> None:
    """Adds ``breakfast = ["rice"]`` to Monday."""
    add_monday_breakfast(menu_path(root))


def _w53(root: Path) -> None:
    """Writes the menu of 2026-W53 as a copy of the example menu."""
    menu_copy(root, "2026-W53")


def _rice_servings(root: Path) -> None:
    """Replaces the servings of ``rice`` by 0."""
    servings_zero(root, "rice")


GROUPS: list[list[Change]] = [
    [
        broken_settings,
        _remove("settings.toml"),
        _edit("settings.toml", 'language = "en"', 'language = "zh"'),
        _edit("settings.toml", 'meals = ["lunch", "dinner"]', 'meals = ["dinner"]'),
    ],
    [catalog_brace, catalog_two, catalog_s07, _remove("catalog.toml")],
    [the_comma, pantry_sesame, pantry_not_text],
    [
        mapo_mistake,
        _rice_servings,
        pork_in_english,
        _edit("recipes/tomato-egg.toml", ', en = "Tomato and egg stir-fry"', ""),
    ],
    [
        _write("recipes/Rice Bowl.toml", ""),
        _write("recipes/pancakes.TOML", ""),
        _mkdir("recipes/old.toml"),
        _remove("recipes"),
    ],
    [
        the_typo,
        _friday,
        _breakfast,
        _w53,
        _write("menus/plan.toml", ""),
        _remove("menus"),
    ],
]
LINES: list[tuple[str, ...]] = [(), ("--lang", "en"), ("--lang", "zh")]


def test_f07_t24_random_mixes_of_mistakes_give_the_report_of_the_readers(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """150 folders: code 0 or 1, the expected report, an empty error stream, and equal reruns."""
    home = make_home(tmp_path)
    rng = random.Random(20261114)  # noqa: S311 - a fixed seed, no security
    for number in range(150):
        root = copy_example(example_folder, tmp_path / f"folder-{number}")
        for group in GROUPS:
            if rng.random() < 0.5:
                rng.choice(group)(root)
        argv = rng.choice(LINES)
        option = argv[1] if argv else None
        expected = expected_report(root, option)
        assert expected[0] in (0, 1)
        first = check(home, root, *argv)
        assert first == expected, (number, argv)
        assert check(home, root, *argv) == first, (number, argv)
