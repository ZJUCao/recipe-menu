"""Tests of F05 for main: what each FolderUse checks, and the Context that main builds.

These are T35 to T38.
"""

import io
from datetime import date, datetime
from pathlib import Path

from f05_support import (
    TODAY,
    Recorder,
    StandIns,
    go,
    in_folder,
    make_folder,
    make_home,
    make_settings_folder,
)
from f05_texts import ZH, no_data_folder, stopped
from recipe_menu.app import Context
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings

UNKNOWN_SUPPER = 'Unknown meal "supper". The meals are breakfast, lunch, and dinner.'
NO_MEALS_ZH = "“meals”至少要写上一个餐次。可用的餐次：breakfast、lunch 和 dinner。"
LUNCH_DINNER = (Meal.LUNCH, Meal.DINNER)


def test_f05_t35_read_stops_at_a_missing_folder_and_at_a_settings_error(tmp_path: Path) -> None:
    """A READ command does not run for a missing folder or settings with an error."""
    home = make_home(tmp_path)
    missing = home / "recipe-menu"
    broken = in_folder(make_folder(tmp_path, "broken"))
    bare = in_folder(make_folder(tmp_path, "bare"))
    broken_zh = in_folder(make_folder(tmp_path, "broken_zh"))
    french = 'language = "fr"\nmeals = []\n'
    fr = in_folder(make_settings_folder(tmp_path, "french", french))
    cases = [
        (("list",), {}, no_data_folder(missing)),
        (("list", "--lang", "zh"), {}, no_data_folder(missing, ZH)),
        (("list",), broken, stopped("settings.toml, meals", UNKNOWN_SUPPER)),
        (("list",), bare, stopped("settings.toml", "The file is missing.")),
        (
            ("list",),
            fr,
            stopped("settings.toml, language", 'The language must be "en" or "zh", not "fr".'),
        ),
        (("list", "--lang", "zh"), broken_zh, stopped("settings.toml，餐次", NO_MEALS_ZH, ZH)),
    ]
    for argv, environ, expected in cases:
        result, kit = go(home, *argv, environ=environ)
        assert result == expected, argv
        assert kit.nothing_ran(), argv
    text = 'language = "zh"\nmeals = ["dinner", "breakfast"]\nservings = 3\n'
    good = in_folder(make_settings_folder(tmp_path, "good", text))
    result, kit = go(home, "list", environ=good)
    assert result == (0, "", "")
    context, _ = kit.ran("LIST")
    assert context.settings == Settings(Lang.ZH, (Meal.BREAKFAST, Meal.DINNER), 3)


def test_f05_t36_check_stops_only_at_a_missing_folder(
    tmp_path: Path, example_folder: DataFolder
) -> None:
    """CHECK runs with Settings() after an error, and gives the exit code of run."""
    home = make_home(tmp_path)
    behave = {"CHECK": Recorder(code=1)}
    result, kit = go(home, "check", behave=behave)
    assert result == no_data_folder(home / "recipe-menu")
    assert kit.nothing_ran()
    cases = [
        (in_folder(make_folder(tmp_path, "broken")), Settings()),
        (in_folder(make_folder(tmp_path, "bare")), Settings()),
        (in_folder(example_folder.root), Settings(Lang.EN, LUNCH_DINNER, 2)),
    ]
    for environ, settings in cases:
        result, kit = go(home, "check", environ=environ, behave={"CHECK": Recorder(code=1)})
        assert result == (1, "", "")
        context, _ = kit.ran("CHECK")
        assert context.settings == settings


def test_f05_t37_init_runs_for_a_missing_folder_and_for_a_settings_error(tmp_path: Path) -> None:
    """INIT gets Settings() when the folder is missing or its settings cannot be read."""
    home = make_home(tmp_path)
    result, kit = go(home, "init")
    assert result == (0, "", "")
    context, _ = kit.ran("INIT")
    assert context.settings == Settings()
    assert str(context.folder.root) == str(home / "recipe-menu")
    assert not (home / "recipe-menu").exists()
    cases = [
        ("broken", Settings()),
        ("bare", Settings()),
        ("zh", Settings(Lang.ZH)),
    ]
    for name, settings in cases:
        environ = in_folder(make_folder(tmp_path, name))
        result, kit = go(home, "init", environ=environ)
        assert result == (0, "", ""), name
        context, _ = kit.ran("INIT")
        assert context.settings == settings, name


def test_f05_t38_main_builds_the_context(tmp_path: Path, example_folder: DataFolder) -> None:
    """The design's example of 2.4, then the context that main builds, and today=None."""
    out, err = io.StringIO(), io.StringIO()
    context = Context(Lang.ZH, DataFolder(tmp_path), Settings(), out, err, date(2026, 11, 10))
    assert context.settings.servings == 2
    assert context.today.isocalendar().week == 46
    context.out.write("共 7 个菜谱。\n")
    assert out.getvalue() == "共 7 个菜谱。\n"
    home = make_home(tmp_path)
    kit = StandIns()
    out, err = io.StringIO(), io.StringIO()
    code = main(
        ["list", "--tag", "素"],
        environ=in_folder(example_folder.root),
        home=home,
        today=TODAY,
        stdout=out,
        stderr=err,
        commands=kit.commands,
    )
    assert code == 0
    built, _ = kit.ran("LIST")
    assert built.lang is Lang.EN
    assert str(built.folder.root) == str(example_folder.root)
    assert built.settings == Settings(Lang.EN, LUNCH_DINNER, 2)
    assert built.out is out
    assert built.err is err
    assert built.today == TODAY
    kit = StandIns()
    before = datetime.now().astimezone().date()
    code = main(
        ["list"],
        environ=in_folder(example_folder.root),
        home=home,
        today=None,
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        commands=kit.commands,
    )
    after = datetime.now().astimezone().date()
    assert code == 0
    assert kit.ran("LIST")[0].today in (before, after)
