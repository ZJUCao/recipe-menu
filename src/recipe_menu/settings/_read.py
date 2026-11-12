"""The reader of ``settings.toml``."""

from recipe_menu.datafile import DataFolder, Problem
from recipe_menu.settings._settings import Settings


def read_settings(folder: DataFolder) -> tuple[Settings | None, tuple[Problem, ...]]:
    """Reads ``settings.toml`` into a ``Settings``, and reports each problem with its place.

    The mock raises ``NotImplementedError``. The implementation follows the rules below.

    Every key is optional. A missing key gives no problem and has its default: no language,
    lunch and dinner, and 2 servings. The file itself is required. No check gives a warning, and
    every problem has the file ``settings.toml``.

    Args:
        folder: The data folder.

    Returns:
        A pair ``(settings, problems)``. ``settings`` is ``None`` when ``problems`` holds an
        error, and otherwise a ``Settings`` whose meals are in the order of ``Meal``, whatever
        order the file lists them in, each once. ``problems`` holds the problem of ``read_toml``
        alone when the file is missing, cannot be read, is not UTF-8, or is not valid TOML.
        Otherwise it holds these problems, in this order: those of ``language``, then those of
        ``meals``, then those of ``servings``, and then the unknown keys in the file's order.

        The places are ``language``, ``meals``, ``meal N``, and ``servings``, each with its
        Chinese name. The checks of ``language``, all at the place ``language``: ``NOT_A_TEXT``
        for a value that is not a text, ``EMPTY_TEXT`` for an empty text or one with only
        whitespace, and ``LANGUAGE_NOT_EN_OR_ZH`` when the text, without whitespace at both
        ends, is neither ``en`` nor ``zh``, such as ``fr`` or ``EN``. The value ``language`` of
        the message is the text without whitespace at both ends. The value ``key`` of
        ``NOT_A_TEXT`` and ``EMPTY_TEXT`` is ``language``.

        The checks of ``meals``, in this order: ``NOT_A_LIST`` at ``meals`` for a value that is
        not a list, which comes alone, with the value ``key`` ``meals``. Then, for each item in
        order, ``ITEM_NOT_A_TEXT`` at
        ``meal N`` for an item that is not a text, ``EMPTY_ITEM`` at ``meal N`` for an empty
        item or one with only whitespace, and ``UNKNOWN_MEAL`` at ``meals``, not at ``meal N``,
        when the item without whitespace at both ends is not the value of a ``Meal``, such as
        ``supper`` or ``Lunch``. N counts the items from 1, skipped items included. The value
        ``meal`` of ``UNKNOWN_MEAL`` is the item without whitespace at both ends. The value
        ``meals`` of ``UNKNOWN_MEAL`` and of ``NO_MEALS`` is ``and_list`` of the values of
        ``Meal``, in their order. An item that names a meal that an earlier item
        named gives no problem, and the settings hold the meal once. ``NO_MEALS`` at ``meals``
        comes only for the empty list ``[]``, and it comes alone. A list whose items all give
        problems gives only those problems, with no ``NO_MEALS``.

        The check of ``servings``: ``read_servings`` gives ``SERVINGS_NOT_A_NUMBER``,
        ``SERVINGS_TOO_FEW``, or ``SERVINGS_TOO_MANY`` at ``servings``.

        The check of the top of the file: ``UNKNOWN_KEY`` with no place for each key other than
        ``language``, ``meals``, and ``servings``. Its value ``key`` is the unknown key and its
        value ``keys`` is ``and_list`` of ``language``, ``meals``, and ``servings``, in the
        form for three keys.

    Raises:
        NotImplementedError: Always, in the mock. The implementation never raises for bad data.
    """
    raise NotImplementedError
