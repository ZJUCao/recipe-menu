"""Listing the TOML files of one folder of the data folder."""

import os
from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem
from recipe_menu.datafile.messages import (
    FOLDER_ACCESS_DENIED,
    FOLDER_IS_FILE,
    FOLDER_MISSING,
    FOLDER_SYSTEM_ERROR,
    TOML_ENDING_NOT_SMALL,
)

_ENDING = ".toml"


def _is_file(path: Path) -> bool:
    """Tells whether a path is a file, and never raises.

    Args:
        path: The path to look at.

    Returns:
        ``True`` when ``path`` is a file. ``False`` when it is not, or when the probe fails.
    """
    return os.path.isfile(path)  # noqa: PTH113


def _listing_failure(relative: Path, path: Path, error: OSError) -> Problem:
    """Makes the problem of an ``OSError`` from listing a folder.

    Args:
        relative: The folder, relative to the data folder.
        path: The folder that could not be listed.
        error: The error.

    Returns:
        The problem, with no place.
    """
    if _is_file(path):
        return Problem.error(relative, None, FOLDER_IS_FILE)
    if isinstance(error, FileNotFoundError | NotADirectoryError):
        return Problem.error(relative, None, FOLDER_MISSING)
    if isinstance(error, PermissionError):
        return Problem.error(relative, None, FOLDER_ACCESS_DENIED)
    reason = error.strerror or type(error).__name__
    return Problem.error(relative, None, FOLDER_SYSTEM_ERROR, reason=reason)


def list_toml_files(
    folder: DataFolder,
    path: Path,
) -> tuple[tuple[str, ...], tuple[Problem, ...]]:
    """Lists the TOML files of one folder of the data folder.

    It reads no file and writes nothing. Every kind of entry counts, a folder named ``x.toml``
    too, so ``read_toml`` later reports such a folder as a folder.

    Args:
        folder: The data folder.
        path: The folder to list, such as ``folder.recipes``. Inside ``folder.root``.

    Returns:
        A pair ``(names, problems)``.

        ``names`` holds the name of each entry of ``path`` whose name ends with ``.toml`` in
        these small letters, without that ending. They are sorted by the name without ``.toml``,
        by code point, as ``sorted`` sorts strings, so ``a.toml`` and ``a-b.toml`` give
        ``("a", "a-b")``. A folder with no such entry gives the empty tuple.

        ``problems`` holds the error ``TOML_ENDING_NOT_SMALL`` for each entry whose ``.toml``
        ending has a capital letter, such as ``rice.TOML`` or ``rice.Toml``. Such a name ends
        with ``.`` followed by ``t`` or ``T``, ``o`` or ``O``, ``m`` or ``M``, and ``l`` or
        ``L``, and does not end with ``.toml``. The problem's file is the entry, relative to the
        data folder, such as ``Path("menus", "2026-W48.TOML")``, and it has no place. Its
        message does not show the name. The problems are sorted by the whole entry name,
        ending included, compared as a ``str``, not as a ``Path``, so ``Z.TOML`` and
        ``a-b.TOML`` come before ``a.TOML``. The name of such an entry is not in ``names``.

        When listing ``path`` fails with an ``OSError``, ``names`` is empty and ``problems``
        holds only one error. Its file is ``folder.relative(path)``, and it has no place. Its
        message is the first of these that applies. ``FOLDER_IS_FILE`` when ``path.is_file()``
        is true, where a probe that fails counts as false. ``FOLDER_MISSING`` for a
        ``FileNotFoundError``, or a ``NotADirectoryError`` because a folder above ``path`` is a
        file. ``FOLDER_ACCESS_DENIED`` for a ``PermissionError``. ``FOLDER_SYSTEM_ERROR`` for
        any other ``OSError``, with the value ``reason`` set to the error's ``strerror``, or to
        the name of the error's class, such as ``OSError``, when ``strerror`` is ``None`` or
        empty.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, as ``DataFolder.relative`` finds. It
            is checked before the listing.
    """
    relative = folder.relative(path)
    try:
        entries = [entry.name for entry in path.iterdir()]
    except OSError as error:
        return (), (_listing_failure(relative, path, error),)
    names = sorted(name[: -len(_ENDING)] for name in entries if name.endswith(_ENDING))
    capitals = sorted(
        name
        for name in entries
        if name[-len(_ENDING) :].lower() == _ENDING and name[-5:] != _ENDING
    )
    problems = tuple(
        Problem.error(relative / name, None, TOML_ENDING_NOT_SMALL) for name in capitals
    )
    return tuple(names), problems
