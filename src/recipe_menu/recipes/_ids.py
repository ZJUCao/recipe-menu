"""The recipe IDs: the rule for an ID, and the IDs of the files in ``recipes/``."""

import re
from typing import Final

from recipe_menu.datafile import DataFolder, Problem, list_toml_files
from recipe_menu.recipes.messages import NOT_A_RECIPE_ID, RESERVED_RECIPE_ID
from recipe_menu.text import Message

_ID: Final = re.compile(r"[a-z0-9][a-z0-9-]*")
_DEVICE: Final = re.compile(r"con|prn|aux|nul|(com|lpt)[0-9]")


def _refusal(name: str) -> Message:
    """Chooses the message for a file name that is not a recipe ID.

    Args:
        name: The name of the file without ``.toml``.

    Returns:
        ``RESERVED_RECIPE_ID`` when ``name`` is exactly a Windows device name, and
        ``NOT_A_RECIPE_ID`` for every other name.
    """
    return RESERVED_RECIPE_ID if _DEVICE.fullmatch(name) else NOT_A_RECIPE_ID


def is_recipe_id(text: str) -> bool:
    """Checks a name against the rule for a recipe ID.

    A file in ``recipes/`` is a recipe only when its name without ``.toml`` follows the rule.
    The rule rejects every name that ``DataFolder.recipe_file`` rejects, and more. It is the
    same on Windows and Linux.

    Args:
        text: A name to check, such as a file name without ``.toml`` or an ID that you typed.
            Any string.

    Returns:
        ``True`` when ``text`` follows all of these rules, and ``False`` otherwise.
        (1) It has at least one character.
        (2) Its first character is a small letter from ``a`` to ``z`` or a digit from ``0`` to
        ``9``.
        (3) Each other character is a small letter from ``a`` to ``z``, a digit from ``0`` to
        ``9``, or ``-``, which is U+002D HYPHEN-MINUS.
        (4) It is not a Windows device name: ``con``, ``prn``, ``aux``, ``nul``, ``com0`` to
        ``com9``, or ``lpt0`` to ``lpt9``.
        So a capital letter, a space, ``_``, a dot, a separator, ``:``, U+0000, and every
        character outside ASCII are rejected, and so are ``Tomato-Egg``, ``-tomato``, ``rice.``,
        and ``nul.v2``. It never raises.
    """
    return _ID.fullmatch(text) is not None and _DEVICE.fullmatch(text) is None


def list_recipe_ids(folder: DataFolder) -> tuple[tuple[str, ...], tuple[Problem, ...]]:
    """Lists the recipe IDs from the file names in ``recipes/``, without reading any file.

    It lists ``recipes/`` through ``list_toml_files``, reads no file, and writes nothing.

    Args:
        folder: The data folder.

    Returns:
        A pair ``(ids, problems)``.

        A recipe file is an entry of ``recipes/`` whose name ends with ``.toml`` in small
        letters, as ``list_toml_files`` gives it. Its ID is its name without ``.toml``. Every
        other entry, such as ``notes.txt`` or ``rice.toml.bak``, gives no problem. An entry
        such as ``rice.TOML`` is not a recipe file either, and ``list_toml_files`` gives an
        error for it.

        ``ids`` holds the ID of each recipe file whose name without ``.toml`` follows the rule
        of ``is_recipe_id``, sorted by code point, as ``sorted`` sorts strings. So ``-`` sorts
        before the digits and the digits before the letters, and ``tomato-egg`` comes before
        ``tomato-egg-noodles``.

        ``problems`` holds the problems that ``list_toml_files`` gives, and then one error for
        each recipe file whose name without ``.toml`` breaks the rule of ``is_recipe_id``, in
        the order of the names. The message is ``RESERVED_RECIPE_ID`` for a name that is exactly
        one of the Windows device names of rule (4) of ``is_recipe_id``, and ``NOT_A_RECIPE_ID``
        for every other name, so ``CON`` and ``nul.v2`` get ``NOT_A_RECIPE_ID``. Neither message
        shows the name. Each problem's file is its entry, relative to the data folder, such as
        ``Path("recipes", "Rice Bowl.toml")``, and it has no place. A name with a problem is
        not in ``ids``.

        When ``recipes/`` is missing, is a file, or cannot be read, ``list_toml_files`` gives no
        names and one problem, with the file ``recipes`` and no place. So ``ids`` is empty, and
        ``problems`` holds only that problem.

        It never raises for bad data.
    """
    names, problems = list_toml_files(folder, folder.recipes)
    ids = tuple(name for name in names if is_recipe_id(name))
    relative = folder.relative(folder.recipes)
    refused = tuple(
        Problem.error(relative / f"{name}.toml", None, _refusal(name))
        for name in names
        if not is_recipe_id(name)
    )
    return ids, problems + refused
