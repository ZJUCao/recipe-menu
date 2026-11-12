"""Tests of F05 for problem_lines, first_error, and stop_at_error (T18 to T20)."""

import io
from datetime import date
from pathlib import Path

import pytest

from f03_support import write
from f05_texts import CHECK_EN, CHECK_ZH, EN, ZH
from recipe_menu.app import Context, first_error, problem_lines, stop_at_error
from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings, read_settings
from recipe_menu.text import Message

UNKNOWN = Message('Unknown ingredient "{name}".', "未知食材“{name}”。")
FILE_MISSING = Message("The file is missing.", "文件不存在。")
MAPO = Path("recipes", "mapo-tofu.toml")
INGREDIENT_3 = BiText("ingredient 3", "食材 3")
TODAY = date(2026, 11, 10)


def test_f05_t18_problem_lines_give_where_and_what() -> None:
    """The file and the place on one line, the message on the other, with no indent."""
    menu = Path("menus", "2026-W47.toml")
    problem = Problem.error(MAPO, INGREDIENT_3, UNKNOWN, name="豆瓣酱")
    missing = Problem.error(Path("settings.toml"), None, FILE_MISSING)
    warning = Problem.warning(MAPO, None, FILE_MISSING)
    assert problem_lines(problem, EN) == (f"{MAPO}, ingredient 3", 'Unknown ingredient "豆瓣酱".')
    assert problem_lines(problem, ZH) == (f"{MAPO}，食材 3", "未知食材“豆瓣酱”。")
    assert problem_lines(missing, EN) == ("settings.toml", "The file is missing.")
    assert problem_lines(missing, ZH) == ("settings.toml", "文件不存在。")
    assert problem_lines(warning, EN) == (str(MAPO), "The file is missing.")
    monday = Problem.error(menu, BiText("Monday dinner", "周一晚餐"), UNKNOWN, name="tomato-eggs")
    assert problem_lines(monday, EN) == (
        f"{menu}, Monday dinner",
        'Unknown ingredient "tomato-eggs".',
    )
    assert problem_lines(monday, ZH) == (f"{menu}，周一晚餐", "未知食材“tomato-eggs”。")
    braces = Problem.error(Path("recipes", "{x}.toml"), INGREDIENT_3, UNKNOWN, name="x")
    where, _ = problem_lines(braces, EN)
    assert where == str(Path("recipes", "{x}.toml")) + ", ingredient 3"


def test_f05_t19_first_error_gives_the_first_error_by_position() -> None:
    """The first problem with the severity error, or None, from any iterable."""
    warning = Problem.warning(MAPO, None, FILE_MISSING)
    missing = Problem.error(Path("settings.toml"), None, FILE_MISSING)
    problem = Problem.error(MAPO, INGREDIENT_3, UNKNOWN, name="豆瓣酱")
    assert first_error([warning, missing, problem]) is missing
    assert first_error([problem, missing]) is problem
    assert first_error((warning, problem)) is problem
    assert first_error(item for item in (warning, problem)) is problem
    assert first_error([warning]) is None
    assert first_error([]) is None


def test_f05_t20_stop_at_error_writes_three_lines_to_the_error_stream(
    example_folder: DataFolder,
) -> None:
    """The prototype's broken settings file, in both languages, and a warning that is refused."""
    write(example_folder.settings, 'meals = ["lunch", "supper"]\n')
    error = first_error(read_settings(example_folder)[1])
    assert error is not None
    expected = {
        EN: (
            "settings.toml, meals\n"
            '  Unknown meal "supper". The meals are breakfast, lunch, and dinner.\n'
            'Run "recipe-menu check" to see every problem.\n'
        ),
        ZH: (
            "settings.toml，餐次\n"
            "  未知餐次“supper”。可用的餐次：breakfast、lunch 和 dinner。\n"
            "运行“recipe-menu check”查看所有问题。\n"
        ),
    }
    for lang in (EN, ZH):
        assert _stop(example_folder, lang, error) == (1, "", expected[lang])
    missing = Problem.error(Path("settings.toml"), None, FILE_MISSING)
    assert _stop(example_folder, EN, missing) == (
        1,
        "",
        f"settings.toml\n  The file is missing.\n{CHECK_EN}\n",
    )
    problem = Problem.error(MAPO, INGREDIENT_3, UNKNOWN, name="豆瓣酱")
    assert _stop(example_folder, EN, problem) == (
        1,
        "",
        f'{MAPO}, ingredient 3\n  Unknown ingredient "豆瓣酱".\n{CHECK_EN}\n',
    )
    assert _stop(example_folder, ZH, missing)[2].endswith(f"{CHECK_ZH}\n")
    out, err = io.StringIO(), io.StringIO()
    context = Context(EN, example_folder, Settings(), out, err, TODAY)
    with pytest.raises(ValueError):
        stop_at_error(context, Problem.warning(MAPO, None, FILE_MISSING))
    assert err.getvalue() == ""
    assert out.getvalue() == ""


def _stop(folder: DataFolder, lang: Lang, error: Problem) -> tuple[int, str, str]:
    """Runs ``stop_at_error`` with new streams and gives ``(code, out, err)``."""
    out, err = io.StringIO(), io.StringIO()
    code = stop_at_error(Context(lang, folder, Settings(), out, err, TODAY), error)
    return code, out.getvalue(), err.getvalue()
