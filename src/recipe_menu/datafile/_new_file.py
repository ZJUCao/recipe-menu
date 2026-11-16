r"""Creating one new file, never overwriting an entry."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from recipe_menu.datafile._creation import _create_file, _creation_problem, _remove_all
from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._listing import _listing_failure
from recipe_menu.datafile._problem import Problem, Severity

# Maps each capital letter A to Z to its small letter, and changes no other character.
_ASCII_FOLD: Final = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


class FileOutcome(Enum):
    """What ``create_file`` or ``replace_file`` found, or what stopped it.

    For ``create_file``, ``CREATED`` means that the call created the file and wrote its text.
    ``EXISTS`` means that an entry with the file's name, or with a name that differs from it only
    in the case of A to Z, is in the file's folder. ``FAILED`` means that the listing of the
    folder failed or that an ``OSError`` stopped the file. The call created nothing for
    ``EXISTS``, and it removed, or tried to remove, the file for ``FAILED`` when it had created
    it.

    For ``replace_file``, ``CREATED`` means that the file at the path holds the text, whether the
    call replaced a file or not. ``FAILED`` means that something other than a folder is at the
    file's folder or that an ``OSError`` stopped a step, and, when its open of the temporary
    file had succeeded, the call removed, or tried to remove, that file. ``replace_file`` never
    gives ``EXISTS``.
    """

    CREATED = "created"
    EXISTS = "exists"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class FileCreation:
    """The result of ``create_file`` or ``replace_file``.

    ``replace_file`` gives only ``CREATED`` and ``FAILED``, and for ``FAILED`` its ``left`` holds
    at most its temporary file.

    Two values are equal when their four fields are equal, and a ``FileCreation`` is hashable.
    The constructor checks its values, as Raises gives them.

    What each outcome holds:

    | Outcome | ``problem`` | ``left`` | ``existing`` |
    | --- | --- | --- | --- |
    | ``CREATED`` | ``None`` | Empty | ``None`` |
    | ``EXISTS`` | ``None`` | Empty | The entry |
    | ``FAILED`` | The error | The file when it could not be removed, else empty | ``None`` |

    Attributes:
        outcome: What happened.
        problem: What stopped the call, as a problem. A ``Problem`` with ``Severity.ERROR`` for
            ``FAILED``, and ``None`` for the other outcomes.
        left: The file, or for ``replace_file`` its temporary file, as a full path, when the call
            created it and could not remove it after the failure. Empty or one path for
            ``FAILED``, and empty for the other outcomes.
        existing: The entry that is already there, as a full path. A ``Path`` for ``EXISTS``, and
            ``None`` for the other outcomes.

    Raises:
        ValueError: ``outcome`` is ``FAILED`` and ``problem`` is ``None``, or ``outcome`` is
            another member and ``problem`` is not ``None``. Or ``problem`` has
            ``Severity.WARNING``. Or ``left`` holds more than one path, or it is not empty and
            ``outcome`` is not ``FAILED``. Or ``outcome`` is ``EXISTS`` and ``existing`` is
            ``None``, or ``outcome`` is another member and ``existing`` is not ``None``.
    """

    outcome: FileOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()
    existing: Path | None = None

    def __post_init__(self) -> None:
        """Checks the values of the four fields.

        Raises:
            ValueError: As the class doc comment gives.
        """
        failed = self.outcome is FileOutcome.FAILED
        if failed != (self.problem is not None):
            message = "problem must be given for FAILED and for no other outcome"
            raise ValueError(message)
        if self.problem is not None and self.problem.severity is not Severity.ERROR:
            message = "problem must have the severity ERROR"
            raise ValueError(message)
        if len(self.left) > 1 or (self.left and not failed):
            message = "left must be empty, or one path for FAILED"
            raise ValueError(message)
        if (self.outcome is FileOutcome.EXISTS) != (self.existing is not None):
            message = "existing must be given for EXISTS and for no other outcome"
            raise ValueError(message)


def create_file(folder: DataFolder, path: Path, text: str) -> FileCreation:
    r"""Creates one new file with its text, and never overwrites an entry.

    The call works in these steps. First it checks ``path`` with ``folder.relative(path)`` and
    encodes ``text`` as UTF-8, before it touches the disk. Then it lists ``path.parent`` with
    ``Path.iterdir``. A listing that fails with an ``OSError`` gives ``FAILED`` with the file
    ``folder.relative(path.parent)``, no place, and the message of the four listing problems of
    ``list_toml_files``: ``FOLDER_IS_FILE``, ``FOLDER_MISSING``, ``FOLDER_ACCESS_DENIED``, or
    ``FOLDER_SYSTEM_ERROR``. Then an entry whose name equals ``path.name``, when each ASCII
    capital letter from A to Z in both names is changed to its small letter, gives ``EXISTS``
    with ``existing`` set to ``path.parent`` joined with the entry's name. When several entries
    match, the entry with exactly the name counts, and otherwise the first match in the order of
    ``sorted``. An entry of any kind counts, and the call opens no entry. Last, it opens ``path``
    in exclusive mode, ``"x"``, with ``encoding="utf-8"`` and ``newline="\n"``, writes the text
    with one ``write`` call, also when the text is empty, and closes the file. So the file holds
    the UTF-8 bytes of the text, with no byte order mark and with the line ends of the text.

    The open, the write, and the close can raise an ``OSError``. The first row that applies
    gives the result, with ``relative`` as ``folder.relative(path)`` and no place.
    ``FileExistsError`` from the open gives ``EXISTS`` with ``existing=path``, as an entry
    appeared after the listing. ``PermissionError`` gives ``FAILED`` with ``FILE_WRITE_DENIED``
    at ``relative``. Any other ``OSError`` gives ``FAILED`` with ``FILE_WRITE_ERROR`` and
    ``reason`` at ``relative``. The value ``reason`` is the error's ``strerror``, or the name of
    the error's class when ``strerror`` is ``None`` or empty.

    A file counts as created from the moment that its open succeeds. After an ``OSError`` from
    the write or the close, the call removes the file with ``Path.unlink`` before it gives
    ``FAILED``. A removal that fails with an ``OSError`` puts the full path of the file in
    ``left``. Any other exception after the open, such as ``KeyboardInterrupt`` for Ctrl+C, runs
    the same removal in a ``finally`` block and then goes on, so the call gives no result. No
    ``except`` clause catches more than ``OSError``.

    Besides the probe ``os.path.isfile`` after a listing that fails, the call reaches the disk
    only through ``Path.iterdir``, ``os.scandir``, or ``os.listdir`` for the listing,
    ``Path.open`` or ``open`` in mode ``"x"``, one ``write`` on the file object, and
    ``Path.unlink``. It never uses ``os.open``, ``Path.write_text``, ``Path.touch``,
    ``os.replace``, or ``shutil``, because the fault harness of the tests replaces only
    ``os.mkdir``, ``os.rmdir``, ``os.unlink``, ``os.remove``, ``os.scandir``, ``os.listdir``,
    ``io.open``, and ``builtins.open`` (test plan section 2), which those calls go through.

    Args:
        folder: The data folder.
        path: The file to create, such as ``folder.menu_file("2026-W47")``. It is inside
            ``folder.root`` and is not ``folder.root``.
        text: The text of the file. UTF-8 can encode it.

    Returns:
        ``FileCreation(FileOutcome.CREATED)`` when the call created the file and wrote its
        text. ``EXISTS`` with ``existing`` when the folder holds an entry of the file's name, as
        the case rule above gives it, or when the exclusive open found one, with nothing
        created. ``FAILED`` when the listing or an ``OSError`` stopped the call, with the
        problem of the rules above and, in ``left``, the file when its removal failed.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, or it is ``folder.root``. The check
            runs before the call touches the disk.
        UnicodeEncodeError: ``text`` holds a character that UTF-8 cannot encode, such as a lone
            surrogate. The check runs before the call touches the disk.
    """
    _check_call(folder, path, text)
    entries = _list_entries(folder, path)
    if isinstance(entries, FileCreation):
        return entries
    entry = _find_entry(path.name, entries)
    if entry is not None:
        return FileCreation(FileOutcome.EXISTS, existing=path.parent / entry)
    return _write_file(folder, path, text)


def _check_call(folder: DataFolder, path: Path, text: str) -> None:
    """Checks the path and the text of a call, before anything touches the disk.

    Args:
        folder: The data folder.
        path: The file to create.
        text: The text of the file.

    Raises:
        ValueError: ``path`` is not inside ``folder.root``, or it is ``folder.root``.
        UnicodeEncodeError: ``text`` cannot be encoded as UTF-8.
    """
    if folder.relative(path) == Path():
        message = "the file must not be the data folder"
        raise ValueError(message)
    text.encode("utf-8")


def _list_entries(folder: DataFolder, path: Path) -> list[str] | FileCreation:
    """Lists the names in the folder of the file.

    Args:
        folder: The data folder.
        path: The file to create.

    Returns:
        The names of the entries of ``path.parent``, or the ``FAILED`` result when the listing
        raised an ``OSError``.
    """
    try:
        return [entry.name for entry in path.parent.iterdir()]
    except OSError as error:
        problem = _listing_failure(folder.relative(path.parent), path.parent, error)
        return FileCreation(FileOutcome.FAILED, problem)


def _find_entry(name: str, entries: list[str]) -> str | None:
    """Finds the entry that counts as the file, by the rule of the case of A to Z.

    Args:
        name: The name of the new file.
        entries: The names of the entries of its folder.

    Returns:
        ``name`` when it is among the entries. Otherwise the first entry in the order of
        ``sorted`` whose name equals ``name`` when A to Z are changed to small letters, and
        ``None`` when no entry does.
    """
    folded = name.translate(_ASCII_FOLD)
    matches = sorted(entry for entry in entries if entry.translate(_ASCII_FOLD) == folded)
    if name in matches:
        return name
    return matches[0] if matches else None


def _write_file(folder: DataFolder, path: Path, text: str) -> FileCreation:
    """Creates the file, and removes it after an error or an interruption.

    Args:
        folder: The data folder.
        path: The file to create.
        text: The text of the file.

    Returns:
        The result of the open, the write, and the close.
    """
    created: list[tuple[Path, bool]] = []
    error: OSError | None = None
    left: tuple[Path, ...] = ()
    succeeded = False
    try:
        error = _create_file(path, text, created)
        succeeded = error is None
    finally:
        if not succeeded:
            left = _remove_all(created)
    if error is None:
        return FileCreation(FileOutcome.CREATED)
    if isinstance(error, FileExistsError) and not created:
        return FileCreation(FileOutcome.EXISTS, existing=path)
    problem = _creation_problem(error, folder.relative(path), is_file=True)
    return FileCreation(FileOutcome.FAILED, problem, left)
