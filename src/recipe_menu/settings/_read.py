"""The reader of ``settings.toml``."""

from dataclasses import replace
from typing import Any

from recipe_menu.datafile import DataFolder, Problem, Report, read_toml, report_unknown_keys
from recipe_menu.settings._read_parts import (
    read_dishes,
    read_language,
    read_meals,
    read_servings_key,
)
from recipe_menu.settings._settings import Settings

_KEYS = ("language", "meals", "servings", "dishes")


def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]:
    """Reads ``settings.toml`` into a ``Settings``, and reports each problem with its place.

    Every key is optional. A missing key gives no problem and has its default: no language,
    lunch and dinner, 2 servings, and 1 dish for each meal. The file itself is required. No
    check gives a warning, and every problem has the file ``settings.toml``.

    Args:
        folder: The data folder.

    Returns:
        A pair ``(settings, problems)``. ``settings`` is ``None`` when ``problems`` holds an
        error, and otherwise a ``Settings`` whose meals are in the order of ``Meal``, whatever
        order the file lists them in, each once. ``problems`` holds the problem of ``read_toml``
        alone when the file is missing, cannot be read, is not UTF-8, or is not valid TOML.
        Otherwise it holds these problems, in this order: those of ``language``, then those of
        ``meals``, then those of ``servings``, then those of ``dishes``, and then the unknown
        keys in the file's order.

        The places are ``language``, ``meals``, ``meal N``, ``servings``, ``dishes``, and
        ``dishes of M``, each with its Chinese name. The checks of ``language``, all at the place
        ``language``: ``NOT_A_TEXT`` for a value that is not a text, ``EMPTY_TEXT`` for an empty
        text or one with only whitespace, and ``LANGUAGE_NOT_EN_OR_ZH`` when the text, without
        whitespace at both ends, is neither ``en`` nor ``zh``, such as ``fr`` or ``EN``. The
        value ``language`` of the message is the text without whitespace at both ends. The value
        ``key`` of ``NOT_A_TEXT`` and ``EMPTY_TEXT`` is ``language``.

        The checks of ``meals``, in this order: ``NOT_A_LIST`` at ``meals`` for a value that is
        not a list, which comes alone, and whose value ``key`` is ``meals``. Then, for each item
        in order, ``ITEM_NOT_A_TEXT`` at ``meal N`` for an item that is not a text,
        ``EMPTY_ITEM`` at ``meal N`` for an empty item or one with only whitespace, and
        ``UNKNOWN_MEAL`` at ``meals``, not at ``meal N``, when the item without whitespace at
        both ends is not the value of a ``Meal``, such as ``supper`` or ``Lunch``. N counts the
        items from 1, skipped items included. The value ``meal`` of ``UNKNOWN_MEAL`` is the item
        without whitespace at both ends. The value ``meals`` of ``UNKNOWN_MEAL`` and of
        ``NO_MEALS`` is ``and_list`` of the values of ``Meal``, in their order. An item that
        names a meal that an earlier item named gives no problem, and the settings hold the meal
        once. ``NO_MEALS`` at ``meals`` comes only for the empty list ``[]``, and it comes alone.
        A list whose items all give problems gives only those problems, with no ``NO_MEALS``.

        The check of ``servings``: ``read_servings`` gives ``SERVINGS_NOT_A_NUMBER``,
        ``SERVINGS_TOO_FEW``, or ``SERVINGS_TOO_MANY`` at ``servings``.

        The checks of ``dishes``, a table with a number of dishes for each meal that needs one:
        ``DISHES_NOT_A_TABLE`` at ``dishes`` for a value that is not a table, which comes alone.
        Otherwise, for each key in the file's order, ``UNKNOWN_MEAL`` at ``dishes`` for a key
        that is not the value of a ``Meal``, and ``DISHES_NOT_1_TO_10`` at ``dishes of M`` for a
        value that is not an ``int`` from 1 to 10 or is a ``bool``. A meal that the table leaves
        out gets 1 dish.

        The check of the top of the file: ``UNKNOWN_KEY`` with no place for each key other than
        ``language``, ``meals``, ``servings``, and ``dishes``. Its value ``key`` is the unknown
        key and its value ``keys`` is ``and_list`` of ``language``, ``meals``, ``servings``, and
        ``dishes``, in the form for four keys.
    """
    table = read_toml(folder, folder.settings)
    if isinstance(table, Problem):
        return None, (table,)
    report = Report(folder.relative(folder.settings))
    language = read_language(table, report)
    meals = read_meals(table, report)
    servings = read_servings_key(table, report)
    dishes = read_dishes(table, report)
    report_unknown_keys(table, _KEYS, None, report)
    problems = tuple(report.problems)
    if problems:
        return None, problems
    given: dict[str, Any] = {
        "language": language,
        "meals": meals,
        "servings": servings,
        "dishes": dishes,
    }
    return replace(Settings(), **{k: v for k, v in given.items() if v is not None}), problems
