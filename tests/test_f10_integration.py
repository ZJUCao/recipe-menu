"""Tests of F10 for the scenarios of version 0.1 at ``main``, and the entry point (T16 to T19)."""

from pathlib import Path

import pytest

from f05_support import copy_example, make_home, run_module
from f05_texts import no_data_folder
from f07_changes import make_init, mapo_mistake
from f07_support import snapshot
from f09_support import at, made
from f09_texts import E_MAPO, MAPO, MAPO_ZH, ZH, err, stop, unknown_id
from f10_support import Case, bom_and_crlf, chinese_settings, real_help, searches
from f10_texts import (
    BLOCK_A,
    BLOCK_F,
    MAPO_FOUND,
    PORK_FOUND,
    PROTOTYPE_ZH,
    TOMATO,
    TOMATO_ZH,
    empty_word,
    no_option,
    none,
    too_few,
)
from recipe_menu.datafile import DataFolder


def test_f10_t16_search_writes_no_file_whatever_it_reports(
    example_folder: DataFolder, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """v0.1-S23 for ``search``: bytes, times, and entries under ``home`` and the current folder."""
    home = make_home(tmp_path)
    root = copy_example(example_folder, home / "recipe-menu")
    (root / "shopping").mkdir()
    current = tmp_path / "cwd"
    current.mkdir()
    monkeypatch.chdir(current)
    before = (snapshot(home), snapshot(current))
    lines: list[Case] = [
        (("番茄",), TOMATO),
        (("葱", "quick", "--lang", "zh"), PROTOTYPE_ZH),
        (("lamb",), none('No recipe matches "lamb".')),
        (("",), empty_word()),
        ((), too_few()),
        (("番茄", "--tag", "quick"), no_option("--tag")),
        (("番茄", "--help"), real_help(home)),
    ]
    searches(home, None, lines)
    assert (snapshot(home), snapshot(current)) == before
    mapo_mistake(root)
    before = (snapshot(home), snapshot(current))
    searches(home, None, [(("番茄",), stop(E_MAPO)), (("lamb",), stop(E_MAPO))])
    assert (snapshot(home), snapshot(current)) == before


def test_f10_t17_the_hint_of_an_unknown_id_names_a_search_that_finds_the_recipe_by_its_name(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``show`` and then ``search``: a word of a name finds a recipe, and a typo of an ID none."""
    home = make_home(tmp_path)
    assert at(home, example_folder, "show", "mapo") == err(1, [MAPO])
    searches(home, example_folder, [(("mapo",), MAPO_FOUND)])
    assert at(home, example_folder, "show", "mapo", "--lang", "zh") == err(1, [MAPO_ZH])
    expected = BLOCK_A[("mapo", "--lang", "zh")]
    assert at(home, example_folder, "search", "mapo", "--lang", "zh") == expected
    assert at(home, example_folder, "show", "pork") == err(1, [unknown_id("pork")])
    searches(home, example_folder, [(("pork",), PORK_FOUND)])
    assert at(home, example_folder, "show", "tomato-eggs") == err(1, [unknown_id("tomato-eggs")])
    searches(home, example_folder, [(("tomato-eggs",), none('No recipe matches "tomato-eggs".'))])


def test_f10_t18_search_reads_the_folder_and_speaks_the_language_that_cli_picks(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``--data``, ``RECIPE_MENU_DATA``, ``~/recipe-menu``, ``--lang``, and the settings."""
    home = make_home(tmp_path)
    folder_b = copy_example(example_folder, tmp_path / "One Drive" / "菜谱")
    folder_c = make_init(example_folder, tmp_path / "c")
    environ = {"RECIPE_MENU_DATA": str(folder_c)}
    assert at(home, folder_b, "search", "番茄") == TOMATO
    assert at(home, None, "search", "番茄", environ=environ) == BLOCK_F[("番茄",)]
    expected = BLOCK_F[("番茄", "--lang", "zh")]
    assert at(home, None, "search", "番茄", "--lang", "zh", environ=environ) == expected
    assert at(home, folder_b, "search", "番茄", environ=environ) == TOMATO
    default = home / "recipe-menu"
    assert at(home, None, "search", "番茄") == no_data_folder(default)
    root = copy_example(example_folder, default)
    chinese_settings(root)
    assert at(home, None, "search", "番茄") == TOMATO_ZH
    assert at(home, None, "search", "番茄", "--lang", "en") == TOMATO
    assert at(home, None, "search", "葱", "quick") == PROTOTYPE_ZH
    bom = made(example_folder, tmp_path, "bom", bom_and_crlf)
    searches(home, bom, [(("番茄",), TOMATO), (("葱", "quick", "--lang", "zh"), PROTOTYPE_ZH)])


def test_f10_t19_the_entry_point_writes_the_output_as_utf_8_and_the_errors_to_stderr(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """``python -m recipe_menu`` runs ``search`` with the real commands."""
    root = str(example_folder.root)
    result = run_module(tmp_path, "search", "葱", "quick", "--lang", "zh", "--data", root)
    assert result == PROTOTYPE_ZH
    result = run_module(tmp_path, "search", "lamb", "--lang", "zh", "--data", root)
    assert result == none("没有菜谱匹配“lamb”。")
    assert run_module(tmp_path, "search", "", "--data", root) == empty_word()
    assert run_module(tmp_path, "search", "番茄", data=example_folder.root) == TOMATO
    mapo_mistake(example_folder.root)
    result = run_module(tmp_path, "search", "番茄", "--lang", "zh", "--data", root)
    assert result == stop(E_MAPO, ZH)
