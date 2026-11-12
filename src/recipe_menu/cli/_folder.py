"""Finding the data folder of the command line."""

import os
from collections.abc import Callable, Mapping
from pathlib import Path

from recipe_menu.cli._parse import DATA_OPTION_NAME, Line

_VARIABLE = "RECIPE_MENU_DATA"
# Both separators count on every system, as a user may type either.
_SEPARATORS = "/" + os.sep


def _expand(value: str, get_home: Callable[[], Path]) -> Path:
    r"""Replaces a leading ``~`` with the home folder.

    The text decides, not ``Path(value).parts``, because ``pathlib`` drops a leading ``.``. The
    value counts from the home folder when it is ``~``, or starts with ``~/``, or starts with
    ``~`` and the separator of the system. So ``./~/x`` stays a path in the current folder.

    Args:
        value: The text of the data folder.
        get_home: Gives the home folder. It is called only when the value needs it.

    Returns:
        The path, which may still be relative.
    """
    if value == "~":
        return get_home()
    if value[:1] == "~" and value[1:2] and value[1:2] in _SEPARATORS:
        return get_home() / value[2:].lstrip(_SEPARATORS)
    return Path(value)


def find_root(line: Line, environ: Mapping[str, str], get_home: Callable[[], Path]) -> Path:
    """Finds the data folder by rule 4 of the command line.

    Args:
        line: The arguments.
        environ: The environment variables.
        get_home: Gives the home folder. It is called only when rule 4 needs it.

    Returns:
        The absolute path of the data folder. It is the first ``--data`` that has a value, else
        ``RECIPE_MENU_DATA`` when it is set and not empty, else ``recipe-menu`` in the home
        folder. A relative path counts from the current folder, and links are not resolved.
    """
    value = line.first_value(DATA_OPTION_NAME) or environ.get(_VARIABLE)
    if not value:
        return (get_home() / "recipe-menu").absolute()
    return _expand(value, get_home).absolute()
