"""Creating a data folder with its folders and files, all or nothing."""

import os
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._listing import _listing_failure
from recipe_menu.datafile._problem import Problem, Severity
from recipe_menu.datafile.messages import (
    FILE_EXISTS,
    FILE_WRITE_DENIED,
    FILE_WRITE_ERROR,
    FOLDER_CREATE_DENIED,
    FOLDER_CREATE_ERROR,
    FOLDER_EXISTS,
)


class CreationOutcome(Enum):
    """What ``create_data_folder`` found at the data folder, or what stopped it.

    ``CREATED`` means that the call created every folder and file. ``HOLDS_FILES`` means that
    the data folder is a folder with an entry. ``NOT_A_FOLDER`` means that something other than
    a folder is at its path. ``FAILED`` means that an ``OSError`` stopped the call. The call
    created nothing for the two refusals, and it removed what it created for ``FAILED``.
    """

    CREATED = "created"
    HOLDS_FILES = "holds files"
    NOT_A_FOLDER = "not a folder"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Creation:
    """The result of ``create_data_folder``.

    Two creations are equal when their three fields are equal, and a ``Creation`` is hashable.
    The constructor checks its values, as Raises gives them.

    Attributes:
        outcome: What happened.
        problem: The ``OSError`` that stopped the call, as a problem. A ``Problem`` with
            ``Severity.ERROR`` for ``FAILED``, and ``None`` for the other outcomes.
        left: What the call created and could not remove after the failure, as full paths, in
            the order of the removal. Empty for every outcome other than ``FAILED``.

    Raises:
        ValueError: ``outcome`` is ``FAILED`` and ``problem`` is ``None``, or ``outcome`` is
            another member and ``problem`` is not ``None``. Or ``problem`` has
            ``Severity.WARNING``. Or ``left`` is not empty and ``outcome`` is not ``FAILED``.
    """

    outcome: CreationOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        """Checks the values of the three fields.

        Raises:
            ValueError: As the class doc comment gives.
        """
        failed = self.outcome is CreationOutcome.FAILED
        if failed != (self.problem is not None):
            message = "problem must be given for FAILED and for no other outcome"
            raise ValueError(message)
        if self.problem is not None and self.problem.severity is not Severity.ERROR:
            message = "problem must have the severity ERROR"
            raise ValueError(message)
        if self.left and not failed:
            message = "left must be empty unless the outcome is FAILED"
            raise ValueError(message)


def create_data_folder(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> Creation:
    r"""Creates a data folder with its folders and files, all or nothing.

    The call first checks its arguments and encodes each text as UTF-8, before it touches the
    disk. It then looks at ``folder.root``, and the first case that applies decides. When
    ``os.path.isdir`` is true, it lists the folder: a listing that fails with an ``OSError``
    gives ``FAILED`` with the file ``Path(".")``, no place, and the message of the listing
    problems of ``list_toml_files``, and an entry of any kind, hidden ones included, gives
    ``HOLDS_FILES``. With no entry, it goes on with the folders of ``folders``. When
    ``os.path.lexists`` is true, it gives ``NOT_A_FOLDER``. When neither applies, nothing is at
    the path, and it creates ``folder.root`` and each missing folder above it, from the top
    down, one at a time. The functions ``os.path.isdir`` and ``os.path.lexists`` never raise,
    and a probe that fails counts as false. A folder above the data folder is missing only when
    ``os.path.lexists`` is false for it, so a path below a file counts as missing. So the call
    creates nothing at or above a file, or a link that leads to no folder, and its first
    ``Path.mkdir`` below that entry fails with the system's error, which the rules below turn
    into a ``FAILED`` problem.

    It then creates each folder of ``folders`` in order with ``Path.mkdir``, with no parents and
    with an existing folder as an error. It then creates each file of ``files`` in order. It
    opens the file in exclusive mode, ``"x"``, with ``encoding="utf-8"`` and ``newline="\n"``,
    writes the text, and closes the file. So the file holds the UTF-8 bytes of the text, with
    no byte order mark and with the line ends of the text, and the call never overwrites a
    file.

    Besides the probes ``os.path.isdir`` and ``os.path.lexists``, and ``os.path.isfile`` after
    a listing that fails, the call reaches the disk only through ``Path.mkdir`` with no
    parents, ``Path.open`` or ``open`` in mode ``"x"``, ``Path.unlink``, ``Path.rmdir``, and
    ``Path.iterdir``, ``os.scandir``, or ``os.listdir``. It never uses ``os.open``,
    ``os.makedirs``, ``Path.mkdir(parents=True)``, ``Path.touch``, ``Path.write_text``, or
    ``shutil``, because the fault harness of the tests replaces only ``os.mkdir``,
    ``os.rmdir``, ``os.unlink``, ``os.remove``, ``os.scandir``, ``os.listdir``, ``io.open``,
    and ``builtins.open`` (test plan section 2). Any other call escapes its rules, or gives a
    record that differs from the steps.

    The first ``OSError`` that a creation raises stops the call. It then removes what it
    created and gives ``FAILED`` with a problem by the class of the error. For a folder,
    ``FileExistsError`` gives ``FOLDER_EXISTS``, ``PermissionError`` gives
    ``FOLDER_CREATE_DENIED``, and any other ``OSError`` gives ``FOLDER_CREATE_ERROR``. For a
    file, they give ``FILE_EXISTS``, ``FILE_WRITE_DENIED``, and ``FILE_WRITE_ERROR``. The value
    ``reason`` is the error's ``strerror``, or the name of the error's class when ``strerror``
    is ``None`` or empty. The problem has no place. Its file is ``folder.relative(path)`` for
    an item of ``folders`` or ``files``, and ``Path(".")`` for ``folder.root`` and the folders
    above it.

    The removal takes each folder and file that the call created, in the reverse order of their
    creation, with ``Path.unlink`` for a file and ``Path.rmdir`` for a folder. A file counts as
    created from the moment that its open succeeds, so a file that is half written is removed
    too. It never removes anything that existed before the call, so an empty data folder stays,
    and so do the folders above it. A removal that fails with an ``OSError`` is skipped, and
    its path goes into ``left`` as a full path, in the order of the removal. A folder that
    still holds a skipped file fails its ``rmdir``, so it goes into ``left`` too. Any other
    exception that interrupts the creation, such as ``KeyboardInterrupt`` for Ctrl+C, runs the
    same removal in a ``finally`` block and then goes on, so the call gives no result.

    Args:
        folder: The data folder to create. Its root and the folders above it may be missing.
        folders: The folders to create in it, in order. Each is inside ``folder.root`` and is
            not ``folder.root``. Each appears once. Its parent is ``folder.root`` or an
            earlier item.
        files: The files to create, in order, each with its text. Each path is inside
            ``folder.root``, is not ``folder.root``, appears once, and is not an item of
            ``folders``. Its parent is ``folder.root`` or an item of ``folders``. Each text
            is a ``str`` that UTF-8 can encode.

    Returns:
        ``Creation(CreationOutcome.CREATED)`` when every folder and file was created.
        ``HOLDS_FILES`` when the data folder is a folder with an entry, and ``NOT_A_FOLDER``
        when something other than a folder is at its path, both with nothing created.
        ``FAILED`` when an ``OSError`` stopped the call, with the problem of the rules above
        and, in ``left``, what the removal could not remove.

    Raises:
        ValueError: A path of ``folders`` or ``files`` is not inside ``folder.root``, is
            ``folder.root``, appears twice, or has a parent that is neither ``folder.root`` nor
            an item of ``folders`` that comes before it. The check runs before the call touches
            the disk.
        UnicodeEncodeError: A text holds a character that UTF-8 cannot encode, such as a lone
            surrogate. The check runs before the call touches the disk.
    """
    _check_arguments(folder, folders, files)
    refusal = _look_at_root(folder.root)
    if refusal is not None:
        return refusal
    plan = _plan(folder, folders, files)
    created: list[tuple[Path, bool]] = []
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
    succeeded = False
    try:
        problem = _create_all(plan, created)
        succeeded = problem is None
    finally:
        if not succeeded:
            left = _remove_all(created)
    if problem is None:
        return Creation(CreationOutcome.CREATED)
    return Creation(CreationOutcome.FAILED, problem, left)


def _check_arguments(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> None:
    """Checks the paths and the texts of a call, before anything touches the disk.

    Args:
        folder: The data folder.
        folders: The folders to create, in order.
        files: The files to create, in order, each with its text.

    Raises:
        ValueError: A path breaks a constraint of ``create_data_folder``.
        UnicodeEncodeError: A text cannot be encoded as UTF-8.
    """
    seen: set[Path] = set()
    parents = {folder.root}
    for path in folders:
        _check_path(folder, path, seen, parents)
        parents.add(path)
    for path, text in files:
        _check_path(folder, path, seen, parents)
        text.encode("utf-8")


def _check_path(folder: DataFolder, path: Path, seen: set[Path], parents: set[Path]) -> None:
    """Checks one path of ``folders`` or ``files``.

    Args:
        folder: The data folder.
        path: The path to check.
        seen: The paths checked so far. ``path`` is added to it.
        parents: The paths that may be the parent of ``path``.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, is ``folder.root``, appears twice,
            or has a parent that is not in ``parents``.
    """
    if folder.relative(path) == Path():
        message = "a path must not be the data folder"
        raise ValueError(message)
    if path in seen:
        message = f"{path} appears twice"
        raise ValueError(message)
    if path.parent not in parents:
        message = f"the parent of {path} is neither the data folder nor an earlier folder"
        raise ValueError(message)
    seen.add(path)


def _look_at_root(root: Path) -> Creation | None:
    """Looks at the data folder before anything is created.

    Args:
        root: The data folder's path.

    Returns:
        The refusal or the failure when the call must stop, and ``None`` when ``root`` is an
        empty folder or nothing is at its path.
    """
    if os.path.isdir(root):  # noqa: PTH112
        try:
            entries = list(root.iterdir())
        except OSError as error:
            return Creation(CreationOutcome.FAILED, _listing_failure(Path(), root, error))
        return Creation(CreationOutcome.HOLDS_FILES) if entries else None
    if os.path.lexists(root):
        return Creation(CreationOutcome.NOT_A_FOLDER)
    return None


def _missing_above(root: Path) -> list[Path]:
    """Finds the data folder and the folders above it that nothing is at.

    Args:
        root: The data folder's path.

    Returns:
        The paths from the top down, up to ``root``. Empty when ``root`` exists.
    """
    missing: list[Path] = []
    for path in (root, *root.parents):
        if os.path.lexists(path):
            break
        missing.append(path)
    missing.reverse()
    return missing


def _plan(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> list[tuple[Path, Path, str | None]]:
    """Lists what the call creates, in order.

    Args:
        folder: The data folder.
        folders: The folders to create.
        files: The files to create, each with its text.

    Returns:
        Triples of the path, the file that a problem names, and the text. The text is ``None``
        for a folder.
    """
    plan: list[tuple[Path, Path, str | None]] = [
        (path, Path(), None) for path in _missing_above(folder.root)
    ]
    plan.extend((path, folder.relative(path), None) for path in folders)
    plan.extend((path, folder.relative(path), text) for path, text in files)
    return plan


def _create_all(
    plan: list[tuple[Path, Path, str | None]],
    created: list[tuple[Path, bool]],
) -> Problem | None:
    """Creates each folder and file of the plan, and stops at the first error.

    Args:
        plan: What to create, from ``_plan``.
        created: Where each created path is recorded, with ``True`` for a file.

    Returns:
        The problem of the first ``OSError``, or ``None`` when everything was created.
    """
    for path, relative, text in plan:
        error = _create_folder(path, created) if text is None else _create_file(path, text, created)
        if error is not None:
            return _creation_problem(error, relative, is_file=text is not None)
    return None


def _create_folder(path: Path, created: list[tuple[Path, bool]]) -> OSError | None:
    """Creates one folder, with no parents.

    Args:
        path: The folder.
        created: Where the folder is recorded when it is created.

    Returns:
        The ``OSError`` that stopped it, or ``None``.
    """
    try:
        path.mkdir()
    except OSError as error:
        return error
    created.append((path, False))
    return None


def _create_file(path: Path, text: str, created: list[tuple[Path, bool]]) -> OSError | None:
    """Creates one file in exclusive mode and writes its text.

    Args:
        path: The file.
        text: The text to write, with one ``write`` call.
        created: Where the file is recorded as soon as it is open.

    Returns:
        The ``OSError`` that stopped it, or ``None``.
    """
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            created.append((path, True))
            handle.write(text)
    except OSError as error:
        return error
    return None


def _creation_problem(error: OSError, relative: Path, *, is_file: bool) -> Problem:
    """Turns the ``OSError`` of a creation into its problem.

    Args:
        error: The error.
        relative: The file that the problem names.
        is_file: ``True`` for a file, and ``False`` for a folder.

    Returns:
        The problem, with no place.
    """
    if isinstance(error, FileExistsError):
        return Problem.error(relative, None, FILE_EXISTS if is_file else FOLDER_EXISTS)
    if isinstance(error, PermissionError):
        denied = FILE_WRITE_DENIED if is_file else FOLDER_CREATE_DENIED
        return Problem.error(relative, None, denied)
    other = FILE_WRITE_ERROR if is_file else FOLDER_CREATE_ERROR
    return Problem.error(relative, None, other, reason=error.strerror or type(error).__name__)


def _remove_all(created: list[tuple[Path, bool]]) -> tuple[Path, ...]:
    """Removes what the call created, the last first.

    Args:
        created: Each created path, with ``True`` for a file.

    Returns:
        The paths that could not be removed, in the order of the removal.
    """
    left: list[Path] = []
    for path, is_file in reversed(created):
        try:
            if is_file:
                path.unlink()
            else:
                path.rmdir()
        except OSError:
            left.append(path)
    return tuple(left)
