r"""Writing one file and replacing the file that is there, through a temporary file."""

import os
from pathlib import Path

from recipe_menu.datafile._creation import _remove_all
from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._new_file import FileCreation, FileOutcome
from recipe_menu.datafile._problem import Problem
from recipe_menu.datafile.messages import (
    FILE_WRITE_DENIED,
    FILE_WRITE_ERROR,
    FOLDER_CREATE_DENIED,
    FOLDER_CREATE_ERROR,
    PARENT_NOT_A_FOLDER,
)


def replace_file(folder: DataFolder, path: Path, text: str) -> FileCreation:
    r"""Writes one file with its text and replaces the file that is there, all or nothing.

    The call works in these steps. ``parent`` is ``path.parent``, and ``temp`` is
    ``parent / (path.name + ".tmp")``, such as ``shopping/2026-W47.md.tmp``.

    1. It checks ``path`` with ``folder.relative(path)``, checks that it is not ``folder.root``,
       and encodes ``text`` as UTF-8, before it touches the disk.
    2. When ``os.path.isdir(parent)`` is true, it goes on. Otherwise, when
       ``os.path.lexists(parent)`` is true, something other than a folder is there, such as a
       file or a link that leads to no folder, and the call gives ``FAILED`` with
       ``PARENT_NOT_A_FOLDER``, with ``folder`` as ``str(folder.relative(parent))``. Otherwise
       nothing is there, and it creates ``parent`` with ``Path.mkdir()``, with no parents and
       with an existing entry as an error. The two probes never raise, and a probe that fails
       counts as false. A folder that the call created stays when a later step fails.
    3. It removes an entry at ``temp`` with ``Path.unlink(missing_ok=True)``, which may be left
       by a call that stopped without its cleanup. A missing entry is no error.
    4. It opens ``temp`` in exclusive mode, ``"x"``, with ``encoding="utf-8"`` and
       ``newline="\n"``, writes the text with one ``write`` call on the file that the open gave,
       also when the text is empty, and closes the file. So the file holds the UTF-8 bytes of
       the text, with no byte order mark and with the line ends of the text.
    5. It moves ``temp`` over ``path`` with ``os.replace(temp, path)``, called directly or
       through ``Path.replace``. The move replaces a file at ``path`` in one step and creates
       ``path`` when nothing is there.

    Every problem of the call has the file ``folder.relative(path)``, not its folder or
    ``temp``, and no place. So a caller can name the file that it could not write by its full
    path, ``str(folder.root / problem.file)``. An ``OSError`` gives the problem of the first row
    that applies. At the creation of ``parent`` in step 2, ``PermissionError`` gives
    ``FOLDER_CREATE_DENIED``, and any other ``OSError``, ``FileExistsError`` included, gives
    ``FOLDER_CREATE_ERROR`` with ``reason``. In steps 3 to 5, ``PermissionError`` gives
    ``FILE_WRITE_DENIED``, and any other ``OSError``, ``FileExistsError`` included, gives
    ``FILE_WRITE_ERROR`` with ``reason``. So a ``FileExistsError`` never gives the ``FILE_EXISTS``
    or ``FOLDER_EXISTS`` of ``create_data_folder`` here. The value ``reason`` is the error's
    ``strerror``, or the name of the error's class when ``strerror`` is ``None`` or empty.

    ``temp`` counts as created from the moment that its open succeeds. After an ``OSError`` from
    the write, the close, or the move, the call removes ``temp`` with ``Path.unlink`` before it
    gives ``FAILED``. A removal that fails with an ``OSError`` puts the full path of ``temp`` in
    ``left``. Any other exception after the open, such as ``KeyboardInterrupt`` for Ctrl+C, runs
    the same removal in a ``finally`` block and then goes on, so the call gives no result. After
    the move, nothing is removed. No ``except`` clause catches more than ``OSError``. The file at
    ``path`` changes only through the move, so it keeps its bytes whenever the call gives
    ``FAILED`` or raises, and a reader of ``path`` sees the old text or the new text, never a
    part.

    Besides the probes ``os.path.isdir`` and ``os.path.lexists``, the call reaches the disk only
    through ``Path.mkdir``, ``Path.unlink``, ``Path.open`` or ``open`` in mode ``"x"``, one
    ``write`` on the file object, and ``os.replace`` or ``Path.replace``. It never uses
    ``os.open``, ``os.rename``, ``Path.write_text``, ``Path.touch``, ``tempfile``, or
    ``shutil``, because the fault harness of the tests replaces only ``os.mkdir``,
    ``os.rmdir``, ``os.unlink``, ``os.remove``, ``os.scandir``, ``os.listdir``, ``io.open``,
    ``builtins.open``, and ``os.replace``, which the calls above go through, and those other
    calls escape it.

    Args:
        folder: The data folder.
        path: The file to write, such as ``folder.shopping_file("2026-W47")``. It is inside
            ``folder.root`` and is not ``folder.root``.
        text: The text of the file. UTF-8 can encode it.

    Returns:
        ``FileCreation(FileOutcome.CREATED)`` when the file at ``path`` holds the text, whether
        the call replaced a file or not. ``FileCreation(FileOutcome.FAILED, problem, left)``
        when a step failed, with the problem of the rules above and, in ``left``, the full path
        of ``temp`` when its removal failed. It never gives ``EXISTS``.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, or it is ``folder.root``. The check
            runs before the call touches the disk.
        UnicodeEncodeError: ``text`` holds a character that UTF-8 cannot encode, such as a lone
            surrogate. The check runs before the call touches the disk.
    """
    relative = folder.relative(path)
    if relative == Path():
        message = "the file must not be the data folder"
        raise ValueError(message)
    text.encode("utf-8")
    failure = _prepare_parent(folder, path.parent, relative)
    if failure is not None:
        return failure
    return _write_through_temp(path, path.parent / (path.name + ".tmp"), text, relative)


def _prepare_parent(folder: DataFolder, parent: Path, relative: Path) -> FileCreation | None:
    """Makes sure that the folder of the file is a folder, and creates it when nothing is there.

    Args:
        folder: The data folder.
        parent: The folder of the file.
        relative: The file, relative to the data folder, for a problem.

    Returns:
        The ``FAILED`` result when something other than a folder is at ``parent`` or its
        creation failed, and ``None`` when ``parent`` is a folder.
    """
    if os.path.isdir(parent):  # noqa: PTH112
        return None
    if os.path.lexists(parent):
        problem = Problem.error(
            relative, None, PARENT_NOT_A_FOLDER, folder=str(folder.relative(parent))
        )
        return FileCreation(FileOutcome.FAILED, problem)
    try:
        parent.mkdir()
    except OSError as error:
        return FileCreation(FileOutcome.FAILED, _problem(error, relative, is_file=False))
    return None


def _write_through_temp(path: Path, temp: Path, text: str, relative: Path) -> FileCreation:
    """Writes ``temp``, moves it over ``path``, and removes ``temp`` after an error.

    Args:
        path: The file to write.
        temp: The temporary file next to it.
        text: The text of the file.
        relative: The file, relative to the data folder, for a problem.

    Returns:
        ``CREATED``, or ``FAILED`` with the problem and with ``temp`` in ``left`` when its
        removal failed.
    """
    created: list[tuple[Path, bool]] = []
    error: OSError | None = None
    left: tuple[Path, ...] = ()
    succeeded = False
    try:
        error = _write_and_move(path, temp, text, created)
        succeeded = error is None
    finally:
        if not succeeded:
            left = _remove_all(created)
    if error is None:
        return FileCreation(FileOutcome.CREATED)
    return FileCreation(FileOutcome.FAILED, _problem(error, relative, is_file=True), left)


def _write_and_move(
    path: Path,
    temp: Path,
    text: str,
    created: list[tuple[Path, bool]],
) -> OSError | None:
    """Clears ``temp``, writes it in exclusive mode, and moves it over ``path``.

    Args:
        path: The file to write.
        temp: The temporary file.
        text: The text, written with one ``write`` call.
        created: Where ``temp`` is recorded as soon as its open succeeds.

    Returns:
        The ``OSError`` that stopped a step, or ``None``.
    """
    try:
        temp.unlink(missing_ok=True)
        with temp.open("x", encoding="utf-8", newline="\n") as handle:
            created.append((temp, True))
            handle.write(text)
        temp.replace(path)
    except OSError as error:
        return error
    return None


def _problem(error: OSError, relative: Path, *, is_file: bool) -> Problem:
    """Turns the ``OSError`` of a step into its problem.

    Args:
        error: The error.
        relative: The file that the problem names.
        is_file: ``True`` for a step on the files, and ``False`` for the creation of the folder.

    Returns:
        The problem, with no place. ``FileExistsError`` is a plain error here.
    """
    if isinstance(error, PermissionError):
        denied = FILE_WRITE_DENIED if is_file else FOLDER_CREATE_DENIED
        return Problem.error(relative, None, denied)
    other = FILE_WRITE_ERROR if is_file else FOLDER_CREATE_ERROR
    return Problem.error(relative, None, other, reason=error.strerror or type(error).__name__)
