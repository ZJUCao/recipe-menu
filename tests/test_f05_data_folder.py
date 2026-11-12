"""Tests of F05 for main: how the data folder is found (T30 to T32)."""

import sys
from pathlib import Path

import pytest

from f05_support import copy_example, go, make_home, record, unreadable_name
from f05_texts import ZH, Result, no_data_folder
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

ENV = "RECIPE_MENU_DATA"


def _init_root(home: Path, *argv: str, environ: dict[str, str]) -> tuple[Result, Path]:
    """Runs a line with ``init`` and gives its result and the root that ``INIT`` got."""
    result, kit = go(home, *argv, environ=environ)
    context, _ = kit.ran("INIT")
    return result, context.folder.root


def test_f05_t30_data_option_wins_over_the_variable_over_the_home_folder(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """The first --data, else RECIPE_MENU_DATA when not empty, else recipe-menu in the home."""
    home = make_home(tmp_path)
    env, opt = tmp_path / "env", tmp_path / "opt"
    spaced = tmp_path / "One Drive" / "菜谱"
    default = home / "recipe-menu"
    cases = [
        (("init",), {}, default),
        (("init",), {ENV: str(env)}, env),
        (("init",), {ENV: ""}, default),
        (("init", "--data", str(opt)), {ENV: str(env)}, opt),
        (("init", "--data", str(opt)), {}, opt),
        (("init", "--data", str(spaced)), {}, spaced),
    ]
    for argv, environ, expected in cases:
        result, root = _init_root(home, *argv, environ=environ)
        assert result == (0, "", ""), argv
        assert str(root) == str(expected), argv
        assert root.is_absolute()
        assert not expected.exists(), "cli made a folder"
    copy_example(example_folder, default)
    result, kit = go(home, "list", environ={})
    assert result == (0, "", "")
    context, _ = kit.ran("LIST")
    assert context.settings == Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2)


def test_f05_t31_relative_paths_and_a_leading_tilde(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A relative path counts from the current folder, and a leading ~ from the home folder."""
    home = make_home(tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    cwd = Path.cwd()
    windows = sys.platform == "win32"
    backslash = home / "x" if windows else cwd / "~\\x"
    dot_backslash = cwd / "~" / "x" if windows else cwd / ".\\~\\x"
    cases = [
        (("init", "--data", "data"), {}, cwd / "data"),
        (("init",), {ENV: "data"}, cwd / "data"),
        (("init", "--data", "."), {}, cwd),
        (("init", "--data", "x/../y"), {}, cwd / "x" / ".." / "y"),
        (("init", "--data", "~"), {}, home),
        (("init", "--data", "~/x"), {}, home / "x"),
        (("init",), {ENV: "~/x"}, home / "x"),
        (("init", "--data", "~\\x"), {}, backslash),
        (("init", "--data", "~troy/x"), {}, cwd / "~troy" / "x"),
        (("init", "--data", "$HOME/x"), {}, cwd / "$HOME" / "x"),
        (("init", "--data", "%USERPROFILE%/x"), {}, cwd / "%USERPROFILE%" / "x"),
        (("init", "--data", "./~/x"), {}, cwd / "~" / "x"),
        (("init", "--data", ".\\~\\x"), {}, dot_backslash),
    ]
    for argv, environ, expected in cases:
        result, root = _init_root(home, *argv, environ=environ)
        assert result == (0, "", ""), argv
        assert str(root) == str(expected), argv
    missing = no_data_folder(home / "recipe-menu")
    assert go(home, "list", "--data", "~/recipe-menu")[0] == missing
    assert go(home, "list")[0] == missing
    assert record(work) == {}
    assert record(home) == {}


def test_f05_t32_a_file_or_an_unreadable_name_counts_as_a_missing_folder(tmp_path: Path) -> None:
    """The folder is looked at with os.path.isdir, which never raises."""
    home = make_home(tmp_path)
    file = tmp_path / "data.txt"
    file.write_bytes(b"not a folder")
    for path in (file, unreadable_name(tmp_path)):
        result, kit = go(home, "list", "--data", str(path))
        assert result == no_data_folder(path)
        assert kit.nothing_ran()
        result, kit = go(home, "list", "--data", str(path), "--lang", "zh")
        assert result == no_data_folder(path, ZH)
        assert kit.nothing_ran()
        result, kit = go(home, "init", "--data", str(path))
        assert result == (0, "", "")
        context, _ = kit.ran("INIT")
        assert str(context.folder.root) == str(path)
        assert context.settings == Settings()
