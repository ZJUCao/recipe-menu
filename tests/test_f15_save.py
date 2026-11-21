"""Tests of F15 for an entry that appears while ``add`` waits and for a failed save (T21, T22)."""

from pathlib import Path

from f05_support import make_home
from f05_texts import lines_text
from f08_support import DENIED, IO, NO_SPACE, rule
from f08_texts import FILE_WRITE_DENIED, file_error
from f09_support import no_recipes_folder
from f09_texts import FOLDER_MISSING
from f13_support import Change, pristine
from f15_blocks import BASE_FILE
from f15_support import (
    BASE,
    Hooked,
    add,
    entry,
    folder_new_dish,
    fresh,
    listing,
    recipe_names,
    traced_add,
)
from f15_texts import (
    NOTHING_SAVED,
    appeared,
    base_out,
    entry_path,
    left_behind,
    pick,
    recipe_path,
    relative,
)
from recipe_menu.datafile import DataFolder


def _hooked_run(home: Path, folder: DataFolder, change: Change) -> tuple[int, str, str]:
    """Runs ``add`` with BASE and a change just before the last answer."""
    return add(home, folder, Hooked(BASE, folder.root, change))


def test_f15_t21_an_entry_that_appears_while_add_waits_is_never_replaced(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Five lines: a race at the open, the Chinese text, and three entries made by a hook."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    for zh, name in ((False, "race"), (True, "race-zh")):
        folder = fresh(source, tmp_path, name)
        race = rule("open", folder.recipe_file("new-dish"), None, "race")
        extra = ("--lang", "zh") if zh else ()
        result, _, _ = traced_add(home, folder, BASE, race, extra=extra)
        shown = appeared(recipe_path(folder))[zh]
        expected = (1, lines_text(*base_out(folder, zh, tail=[])), shown + "\n")
        assert result == expected, name
        assert folder.recipe_file("new-dish").read_bytes() == b"mine\n"
    for name, entry_name, change in (
        ("capital", "New-Dish.toml", entry("New-Dish.toml")),
        ("folder", "new-dish.toml", folder_new_dish),
        ("small", "new-dish.TOML", entry("new-dish.TOML")),
    ):
        folder = fresh(source, tmp_path, name)
        result = _hooked_run(home, folder, change)
        shown = appeared(entry_path(folder, entry_name))[0]
        assert result == (1, lines_text(*base_out(folder, tail=[])), shown + "\n"), name
        names = recipe_names(folder)
        assert names == listing(entry_name), name
        held = folder.root / "recipes" / entry_name
        if name == "folder":
            assert held.is_dir()
            assert list(held.iterdir()) == []
        else:
            assert held.read_bytes() == b"mine\n"
            assert "new-dish.toml" not in names


def test_f15_t22_a_failed_save_gives_three_lines_on_the_error_stream_and_exit_code_1(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven lines: an open, a write, a close, a failed removal, and a deleted folder."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    denied, no_space = FILE_WRITE_DENIED, file_error("No space left on device")
    broken = file_error("Input/output error")
    half = BASE_FILE[: len(BASE_FILE) // 2].encode("utf-8")
    cases = [
        ("open", DENIED, None, False, denied, False),
        ("write", IO, None, False, broken, False),
        ("write", NO_SPACE, None, True, no_space, False),
        ("close", IO, None, False, broken, False),
        ("write", IO, ("unlink", DENIED), False, broken, True),
        ("write", IO, ("unlink", DENIED), True, broken, True),
    ]
    for number, (kind, effect, second, zh, msg, stays) in enumerate(cases, 1):
        folder = fresh(source, tmp_path, f"line-{number}")
        target = folder.recipe_file("new-dish")
        rules = [rule(kind, target, effect)]
        if second is not None:
            rules.append(rule(second[0], target, second[1]))
        extra = ("--lang", "zh") if zh else ()
        result, calls, _ = traced_add(home, folder, BASE, *rules, extra=extra)
        last = pick(left_behind(recipe_path(folder)) if stays else NOTHING_SAVED, zh)
        failure = lines_text(relative(), f"  {pick(msg, zh)}", last)
        assert result == (1, lines_text(*base_out(folder, zh, tail=[])), failure), number
        if stays:
            assert target.read_bytes() == half, number
        else:
            assert not target.exists(), number
        if kind != "open" and not stays:
            assert "unlink recipes/new-dish.toml" in calls, number
    folder = fresh(source, tmp_path, "line-7")
    result = add(home, folder, Hooked(BASE, folder.root, no_recipes_folder))
    failure = lines_text("recipes", f"  {FOLDER_MISSING[0]}", NOTHING_SAVED[0])
    assert result == (1, lines_text(*base_out(folder, tail=[])), failure)
    assert not (folder.root / "recipes").exists()
