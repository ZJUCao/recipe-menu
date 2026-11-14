"""Tests of F10 for what ``cli`` checks before ``search``, and for the files that it reads."""

from pathlib import Path

from f03_support import write
from f05_support import make_home
from f05_texts import Result, no_data_folder
from f07_changes import broken_settings, catalog_brace, mapo_mistake, menu_path, the_comma, the_typo
from f08_support import faults
from f09_support import at, made
from f09_texts import E_BRACE, E_SETTINGS, IDS, ZH, stop
from f10_support import Case, real_help, searches
from f10_texts import (
    PROTOTYPE_ZH,
    TOMATO,
    empty_word,
    no_option,
    none,
    too_few,
)
from recipe_menu.datafile import DataFolder

SETTINGS = "read settings.toml"
CATALOG = "read catalog.toml"
READ_EACH = [SETTINGS, CATALOG, *[f"read recipes/{recipe_id}.toml" for recipe_id in IDS]]


def _record(
    home: Path, folder: DataFolder, words: tuple[str, ...]
) -> tuple[list[str], list[str], Result]:
    """Runs ``search`` inside a new harness, and gives the reads, the listings, and the result."""
    with faults(folder.root) as state:
        got = at(home, folder, "search", *words)
    return state.calls, state.listings, got


def test_f10_t14_search_reads_the_catalog_once_lists_recipes_once_and_reads_each_recipe_once(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The record of the reads and the listings, and no read of the pantry or a menu."""
    home = make_home(tmp_path)
    shown = real_help(home)
    lines = [
        (("番茄",), READ_EACH, ["recipes"], TOMATO),
        (("葱", "quick", "--lang", "zh"), READ_EACH, ["recipes"], PROTOTYPE_ZH),
        (("lamb",), READ_EACH, ["recipes"], none('No recipe matches "lamb".')),
        (("",), [SETTINGS], [], empty_word()),
        (("番茄", ""), [SETTINGS], [], empty_word()),
        (("番茄", "--help"), [SETTINGS], [], shown),
        ((), [SETTINGS], [], too_few()),
    ]
    for words, reads, listings, expected in lines:
        assert _record(home, example_folder, words) == (reads, listings, expected), words
    brace = DataFolder(made(example_folder, tmp_path, "brace", catalog_brace))
    expected = ([SETTINGS, CATALOG], [], stop(E_BRACE))
    assert _record(home, brace, ("番茄",)) == expected
    the_comma(example_folder.root)
    the_typo(example_folder.root)
    write(menu_path(example_folder.root, "2026-W48"), "[[[\n")
    after: list[Case] = [(("番茄",), TOMATO), (("葱", "quick", "--lang", "zh"), PROTOTYPE_ZH)]
    searches(home, example_folder, after)


def test_f10_t15_cli_reports_the_command_line_the_folder_and_the_settings_before_search_runs(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """No word, an option that ``search`` lacks, a missing folder, broken settings, ``--help``."""
    home = make_home(tmp_path)
    searches(
        home,
        example_folder,
        [
            ((), too_few()),
            (("--lang", "zh"), too_few(ZH)),
            (("番茄", "--tag", "quick"), no_option("--tag")),
            (("番茄", "--tag", "quick", "--lang", "zh"), no_option("--tag", ZH)),
            (("--tag",), no_option("--tag")),
        ],
    )
    missing = tmp_path / "missing"
    assert at(home, missing, "search", "番茄") == no_data_folder(missing)
    assert at(home, missing, "search", "番茄", "--lang", "zh") == no_data_folder(missing, ZH)
    broken = made(example_folder, tmp_path, "broken", broken_settings)
    assert at(home, broken, "search", "番茄") == stop(E_SETTINGS)
    mapo = made(example_folder, tmp_path, "mapo", mapo_mistake)
    searches(
        home,
        mapo,
        [
            (("番茄", "--help"), real_help(home)),
            (("--help", "--lang", "zh"), real_help(home, "--lang", "zh")),
            (("lamb", "--help"), real_help(home)),
        ],
    )
    searches(home, example_folder, [(("番茄",), TOMATO)])
