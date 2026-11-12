"""Tests of F05 with random input: command lines and settings files (T55 and T56)."""

import random
from pathlib import Path

import pytest

from f03_support import write
from f05_support import VERSION_LINE, StandIns, go, in_folder, make_folder, make_home
from f05_texts import (
    CHECK_EN,
    CHECK_ZH,
    COMMANDS_EN,
    COMMANDS_ZH,
    EN,
    HELP_EN,
    HELP_ZH,
    INIT_EN,
    INIT_ZH,
    OPTIONS_EN,
    OPTIONS_ZH,
    Result,
)
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings, read_settings

WORDS = ["list", "show", "menu", "new", "search", "init", "check", "shop", "cook", "", "番茄", "-x"]
OPTIONS = ["--lang", "--data", "--help", "--version", "--tag", "--servings", "--tags", "--lang=zh"]
INIT_LINES = {INIT_EN, INIT_ZH}
CHECK_LINES = {CHECK_EN, CHECK_ZH}
HINT_LINES = {OPTIONS_EN, OPTIONS_ZH, COMMANDS_EN, COMMANDS_ZH}


def _line(rng: random.Random, values: list[str]) -> list[str]:
    """Builds a command line of 0 to 6 arguments: a word, an option, or a value, at random."""
    groups = (WORDS, OPTIONS, values)
    return [rng.choice(rng.choice(groups)) for _ in range(rng.randint(0, 6))]


def _check_result(result: Result, kit: StandIns, argv: list[str]) -> None:
    """Checks that a result has the exit code, the stream, and the lines of its kind."""
    code, out, err = result
    ran = sum(len(calls) for calls in (kit.calls(name) for name in kit.names))
    if code == 0:
        assert err == "", argv
        if out:
            assert out in (HELP_EN, HELP_ZH, VERSION_LINE), argv
            assert ran == 0, argv
        else:
            assert ran == 1, argv
        return
    assert out == "", argv
    assert ran == 0, argv
    lines = err.splitlines()
    assert err.endswith("\n"), argv
    if code == 1:
        assert (len(lines), lines[-1] in INIT_LINES) in ((2, True), (3, False)), argv
        assert lines[-1] in INIT_LINES | CHECK_LINES, argv
    else:
        assert code == 2, argv
        assert len(lines) in (1, 2), argv
        assert len(lines) == 1 or lines[1] in HINT_LINES, argv


def test_f05_t55_random_command_lines_give_a_code_and_never_raise(
    tmp_path: Path, example_folder: DataFolder, monkeypatch: pytest.MonkeyPatch
) -> None:
    """500 random lines give code 0, 1, or 2 with the right streams, the same twice."""
    monkeypatch.chdir(tmp_path)
    home = make_home(tmp_path)
    folders = [
        example_folder.root,
        make_folder(tmp_path, "missing"),
        make_folder(tmp_path, "broken_zh"),
    ]
    values = ["en", "zh", "fr", " ", *(str(folder) for folder in folders)]
    rng = random.Random(20261112)  # noqa: S311 - a fixed seed, no security
    for _ in range(500):
        argv = _line(rng, values)
        environ = rng.choice([{}, *(in_folder(folder) for folder in folders)])
        first, first_kit = go(home, *argv, environ=environ)
        second, second_kit = go(home, *argv, environ=environ)
        assert first == second, argv
        assert first_kit.snapshot() == second_kit.snapshot(), argv
        _check_result(first, first_kit, argv)


LANGUAGES = [
    '"en"',
    '"zh"',
    '" zh "',
    '"fr"',
    '"EN"',
    '""',
    '" "',
    '"\u3000"',
    "3",
    "true",
    '["zh"]',
]
MEAL_ITEMS = [
    '"breakfast"',
    '"lunch"',
    '"dinner"',
    '" dinner "',
    '"Lunch"',
    '"supper"',
    '""',
    '" "',
    "3",
    '["lunch"]',
]
SERVINGS = [
    "2",
    "1",
    "100",
    "0",
    "101",
    "-1",
    "999999999999999",
    "1000000000000000",
    '"2"',
    "2.5",
    "true",
    "0x" + "f" * 5000,
]


def _settings_text(rng: random.Random) -> str:
    """Builds a random settings file whose text holds no quotation mark or backslash."""
    keys = []
    if rng.randrange(4):
        keys.append(f"language = {rng.choice(LANGUAGES)}")
    if rng.randrange(4):
        if rng.randrange(10) == 0:
            keys.append('meals = "lunch"')
        else:
            items = [rng.choice(MEAL_ITEMS) for _ in range(rng.randint(0, 4))]
            keys.append(f"meals = [{', '.join(items)}]")
    if rng.randrange(4):
        keys.append(f"servings = {rng.choice(SERVINGS)}")
    if rng.randrange(8) == 0:
        keys.append("colour = 1")
    rng.shuffle(keys)
    return "".join(f"{key}\n" for key in keys)


def _check_places(problems: tuple[Problem, ...]) -> None:
    """Checks that each problem is an error of settings.toml, and that the places are in order."""
    ranks = {"language": 0, "meals": 1, "servings": 2}
    last_rank, last_number = 0, 0
    for problem in problems:
        assert problem.severity is Severity.ERROR
        assert str(problem.file) == "settings.toml"
        place = None if problem.place is None else problem.place.get(EN)
        if place is None:
            rank = 3
        elif place.startswith("meal "):
            rank = 1
            number = int(place.removeprefix("meal "))
            assert 1 <= number <= 4
            assert number > last_number
            last_number = number
        else:
            rank = ranks[place]
        assert rank >= last_rank
        last_rank = rank


def _check_settings(settings: Settings) -> None:
    """Checks the constraints of 2.2 on settings that ``read_settings`` gave."""
    assert settings.language in (None, Lang.EN, Lang.ZH)
    assert 1 <= len(settings.meals) <= 3
    assert list(settings.meals) == sorted(set(settings.meals), key=list(Meal).index)
    assert type(settings.servings) is int
    assert 1 <= settings.servings <= 100


@pytest.mark.usefixtures("default_int_limit")
def test_f05_t56_random_settings_files_give_settings_or_problems(tmp_path: Path) -> None:
    """300 random files: settings exactly when there is no problem, and main follows."""
    home = make_home(tmp_path)
    folder = DataFolder(make_folder(tmp_path, "bare"))
    rng = random.Random(20261113)  # noqa: S311 - a fixed seed, no security
    for _ in range(300):
        text = _settings_text(rng)
        write(folder.settings, text)
        settings, problems = read_settings(folder)
        assert read_settings(folder) == (settings, problems), text
        assert (settings is None) == bool(problems), text
        _check_places(problems)
        result, kit = go(home, "list", environ=in_folder(folder.root))
        if settings is None:
            _check_stopped(result, kit, problems[0])
        else:
            _check_settings(settings)
            assert result == (0, "", ""), text
            context, _ = kit.ran("LIST")
            assert context.settings == settings


def _check_stopped(result: Result, kit: StandIns, first: Problem) -> None:
    """Checks that ``list`` stopped at the first problem with the three English lines."""
    place = "" if first.place is None else f", {first.place.get(EN)}"
    expected = f"settings.toml{place}\n  {first.text(EN)}\n{CHECK_EN}\n"
    assert result == (1, "", expected)
    assert kit.nothing_ran()
