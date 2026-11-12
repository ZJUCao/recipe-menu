"""Listing the TOML files of one folder of the data folder."""

from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem


def list_toml_files(
    folder: DataFolder,
    path: Path,
) -> tuple[tuple[str, ...], tuple[Problem, ...]]:
    """Lists the TOML files of one folder of the data folder.

    It reads no file and writes nothing. Every kind of entry counts, a folder named ``x.toml``
    too, so ``read_toml`` later reports such a folder as a folder.

    The mock only raises ``NotImplementedError``.

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
        NotImplementedError: Always, in the mock.
    """
    raise NotImplementedError
