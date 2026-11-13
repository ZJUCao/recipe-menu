"""Tests of F08 for the refusals of recipe-menu init and the data folder that it picks.

These are T17 and T18.
"""

from pathlib import Path

import pytest

from f03_support import put_bytes
from f05_support import make_home
from f08_support import (
    call_main,
    dangling_link,
    fill_entry,
    full_record,
    init,
    new_tree,
    tree,
)
from f08_texts import err_of, holds, holds_zh, is_file, is_file_zh, new, new_zh, out_of


def _make_p(tmp_path: Path, number: int) -> Path:
    """Makes the path ``P`` of case ``number`` of F08-T17 under ``tmp_path``."""
    path = tmp_path / f"p{number}"
    if number <= 6:
        fill_entry(path, number)
    elif number in (7, 8):
        text = 'language = "zh"\n' if number == 7 else 'meals = ["lunch", "supper"]\n'
        put_bytes(path / "settings.toml", text.encode("utf-8"))
    elif number == 9:
        put_bytes(path, b"Ideas\n")
    else:
        dangling_link(path)
    return path


def test_f08_t17_a_refusal_is_one_line_on_the_error_stream_in_the_right_language(
    tmp_path: Path,
) -> None:
    """A folder with an entry and a non-folder are refused, and every entry keeps its time."""
    home = make_home(tmp_path)
    paths = {number: _make_p(tmp_path, number) for number in range(1, 11)}
    before = full_record(tmp_path)
    for number, path in paths.items():
        if number == 7:
            expected = err_of(1, [holds_zh(path)])
        elif number >= 9:
            expected = err_of(1, [is_file(path)])
        else:
            expected = err_of(1, [holds(path)])
        assert init(home, folder=path) == expected, number
    assert init(home, "--lang", "zh", folder=paths[1]) == err_of(1, [holds_zh(paths[1])])
    assert init(home, "--lang", "en", folder=paths[7]) == err_of(1, [holds(paths[7])])
    assert init(home, "--lang", "zh", folder=paths[9]) == err_of(1, [is_file_zh(paths[9])])
    assert full_record(tmp_path) == before


def test_f08_t18_init_creates_the_folder_that_cli_picks_and_names_its_full_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--data`, then `RECIPE_MENU_DATA`, then the default; `~` and a relative path resolve."""
    home = make_home(tmp_path)
    folder = tmp_path / "One Drive" / "菜谱"
    assert init(home, folder=folder) == out_of(0, new(folder))

    target = tmp_path / "e"
    assert call_main(home, ["init"], {"RECIPE_MENU_DATA": str(target)}) == out_of(0, new(target))
    assert not (home / "recipe-menu").exists()

    first, second = tmp_path / "f", tmp_path / "g"
    environ = {"RECIPE_MENU_DATA": str(second)}
    assert call_main(home, ["init", "--data", str(first)], environ) == out_of(0, new(first))
    assert not second.exists()

    assert call_main(home, ["init", "--data", "~/other"]) == out_of(0, new(home / "other"))
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    assert call_main(home, ["init", "--data", "rel"]) == out_of(0, new(Path.cwd() / "rel"))
    assert tree(cwd / "rel") == new_tree()

    assert init(home, "--lang", "zh") == out_of(0, new_zh(home / "recipe-menu"))
    assert init(home) == err_of(1, [holds_zh(home / "recipe-menu")])
