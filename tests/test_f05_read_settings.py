"""Tests of F05 for read_settings, the keys that are right and the errors of language and meals.

These are T04 to T08.
"""

from collections.abc import Sequence

from f03_support import put_bytes, write
from f05_support import record
from f05_texts import (
    EMPTY_ITEM,
    ITEM_NOT_A_TEXT,
    LANGUAGE,
    MEALS,
    NO_MEALS,
    Expected,
    assert_problems,
    empty_text,
    entry,
    language_not_en_or_zh,
    meal_n,
    not_a_list,
    not_a_text,
    unknown_meal,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.settings import Meal, Settings, read_settings


def test_f05_t04_example_settings_read_with_bom_and_crlf(example_folder: DataFolder) -> None:
    """The example's settings give English, lunch and dinner, and 2, and reading writes nothing."""
    expected = (Settings(Lang.EN, (Meal.LUNCH, Meal.DINNER), 2), ())
    before = record(example_folder.root)
    settings, problems = read_settings(example_folder)
    assert (settings, problems) == expected
    assert settings is not None
    assert settings.language is Lang.EN
    assert settings.meals == (Meal.LUNCH, Meal.DINNER)
    assert settings.servings == 2
    assert record(example_folder.root) == before
    data = example_folder.settings.read_bytes()
    put_bytes(example_folder.settings, b"\xef\xbb\xbf" + data.replace(b"\n", b"\r\n"))
    before = record(example_folder.root)
    assert read_settings(example_folder) == expected
    assert record(example_folder.root) == before


def test_f05_t05_missing_keys_get_their_defaults(folder: DataFolder) -> None:
    """Each key is optional, and the defaults come through read_settings."""
    lunch_dinner = (Meal.LUNCH, Meal.DINNER)
    cases = [
        ("", Settings(None, lunch_dinner, 2)),
        ("# recipe-menu settings\n", Settings(None, lunch_dinner, 2)),
        ('language = "zh"\n', Settings(Lang.ZH, lunch_dinner, 2)),
        ('meals = ["breakfast"]\n', Settings(None, (Meal.BREAKFAST,), 2)),
        ("servings = 4\n", Settings(None, lunch_dinner, 4)),
        ('language = "en"\nservings = 3\n', Settings(Lang.EN, lunch_dinner, 3)),
    ]
    for text, expected in cases:
        write(folder.settings, text)
        settings, problems = read_settings(folder)
        assert problems == (), text
        assert settings == expected, text
    write(folder.settings, "")
    assert read_settings(folder) == (Settings(), ())


def test_f05_t06_language_is_en_or_zh_without_whitespace_at_the_ends(folder: DataFolder) -> None:
    """Other texts, blank texts, and values that are no text are errors at language."""
    accepted = [
        ('"en"', Lang.EN),
        ('"zh"', Lang.ZH),
        ('" zh "', Lang.ZH),
        (r'"\tzh\u3000"', Lang.ZH),
        (r'"\u00a0en"', Lang.EN),
    ]
    for value, language in accepted:
        write(folder.settings, f"language = {value}\n")
        assert read_settings(folder) == (Settings(language), ()), value
    not_text = ["3", "true", '["zh"]']
    empty = ['""', '" "', r'"\u3000"']
    other = [
        ('"fr"', "fr"),
        ('"EN"', "EN"),
        ('" Zh "', "Zh"),
        ('"zh-CN"', "zh-CN"),
        ('"中文"', "中文"),
        (r'"\u200bzh"', "\u200bzh"),
        (r'"\uff5a\uff48"', "\uff5a\uff48"),
    ]
    for value in not_text:
        _rejected(folder, value, not_a_text("language"))
    for value in empty:
        _rejected(folder, value, empty_text("language"))
    for value, language in other:
        _rejected(folder, value, language_not_en_or_zh(language))


def _rejected(folder: DataFolder, value: str, message: tuple[str, str]) -> None:
    """Checks that ``language = value`` gives no settings and one problem at language."""
    write(folder.settings, f"language = {value}\n")
    settings, problems = read_settings(folder)
    assert settings is None, value
    assert_problems(problems, [entry(LANGUAGE, message)])


def test_f05_t07_meals_come_once_in_the_order_of_a_day(folder: DataFolder) -> None:
    """Meals keep the order of Meal, whatever order and count the file names."""
    b, lunch, d = Meal.BREAKFAST, Meal.LUNCH, Meal.DINNER
    cases = [
        ('["lunch", "dinner"]', (lunch, d)),
        ('["dinner", "lunch"]', (lunch, d)),
        ('["dinner", "breakfast", "dinner"]', (b, d)),
        ('["dinner", "lunch", "breakfast"]', (b, lunch, d)),
        ('["dinner"]', (d,)),
        (r'[" dinner ", "\u3000breakfast"]', (b, d)),
        ('["lunch", "lunch", "lunch"]', (lunch,)),
    ]
    for value, meals in cases:
        write(folder.settings, f"meals = {value}\n")
        assert read_settings(folder) == (Settings(None, meals, 2), ()), value


def test_f05_t08_meals_give_their_errors_in_order(folder: DataFolder) -> None:
    """The errors of meals: the list, the items, the unknown meals, and the empty list."""
    for value in ('"lunch"', "{ lunch = true }", "3"):
        _meals_error(folder, value, [entry(MEALS, not_a_list("meals"))])
    _meals_error(folder, "[]", [entry(MEALS, NO_MEALS)])
    _meals_error(folder, '["lunch", "supper"]', [entry(MEALS, unknown_meal("supper"))])
    others = [
        ('["Lunch"]', "Lunch"),
        ('[" Dinner "]', "Dinner"),
        ('["午餐"]', "午餐"),
        (r'["lunch\u200b"]', "lunch\u200b"),
    ]
    for value, meal in others:
        _meals_error(folder, value, [entry(MEALS, unknown_meal(meal))])
    value = r'["lunch", 3, " supper ", "", "dinner", true, "\u3000", ["lunch"], "supper"]'
    supper = entry(MEALS, unknown_meal("supper"))
    not_text, empty = ITEM_NOT_A_TEXT, EMPTY_ITEM
    _meals_error(
        folder,
        value,
        [
            entry(meal_n(2), not_text),
            supper,
            entry(meal_n(4), empty),
            entry(meal_n(6), not_text),
            entry(meal_n(7), empty),
            entry(meal_n(8), not_text),
            supper,
        ],
    )
    _meals_error(folder, '[" "]', [entry(meal_n(1), empty)])
    _meals_error(folder, '["supper"]', [supper])


def _meals_error(folder: DataFolder, value: str, expected: Sequence[Expected]) -> None:
    """Checks that ``meals = value`` gives no settings and the expected problems."""
    write(folder.settings, f"meals = {value}\n")
    settings, problems = read_settings(folder)
    assert settings is None, value
    assert_problems(problems, expected)
