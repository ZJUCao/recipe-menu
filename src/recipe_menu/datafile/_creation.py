"""Creating a data folder with its folders and files, all or nothing."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from recipe_menu.datafile._folder import DataFolder
from recipe_menu.datafile._problem import Problem


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

    The implementation checks its values in the constructor, as Raises gives them. The mock
    leaves these checks out.
    """

    outcome: CreationOutcome
    problem: Problem | None = None
    left: tuple[Path, ...] = ()


def create_data_folder(
    folder: DataFolder,
    folders: Sequence[Path],
    files: Sequence[tuple[Path, str]],
) -> Creation:
    r"""Creates a data folder with its folders and files, all or nothing.

    The mock touches nothing and gives ``Creation(CreationOutcome.CREATED)``.

    The call first checks its arguments and encodes each text as UTF-8, before it touches the
    disk. It then looks at ``folder.root``, and the first case that applies decides. When
    ``os.path.isdir`` is true, it lists the folder: a listing that fails with an ``OSError``
    gives ``FAILED`` with the file ``Path(".")``, no place, and the message of the listing
    problems of ``list_toml_files``, and an entry of any kind, hidden ones included, gives
    ``HOLDS_FILES``. With no entry, it goes on. When ``os.path.lexists`` is true, it gives
    ``NOT_A_FOLDER``. When neither applies, nothing is at the path, and it creates
    ``folder.root`` and each folder above it, from the top down, one at a time. The functions
    ``os.path.isdir`` and ``os.path.lexists`` never raise, and a probe that fails counts as
    false. A folder above the data folder is missing only when ``os.path.lexists`` is false for
    it, so a path below a file counts as missing, so the call creates nothing at or above a
    file, or a link that leads to no folder. Its first ``Path.mkdir`` below that
    entry fails with the system's error, which the rules below turn into a ``FAILED`` problem.

    It then creates each folder of ``folders`` in order with ``Path.mkdir``, with no parents and
    with an existing folder as an error. It then creates each file of ``files`` in order. It
    opens the file in exclusive mode, ``"x"``, with ``encoding="utf-8"`` and ``newline="\n"``,
    writes the text, and closes the file. So the file holds the UTF-8
    bytes of the text, with no byte order mark and with the line ends of the text, and the call
    never overwrites a file.

    Besides the probes ``os.path.isdir`` and ``os.path.lexists``, the call reaches the disk
    only through ``Path.mkdir`` with no parents, ``Path.open`` or ``open`` in mode ``"x"``,
    ``Path.unlink``, ``Path.rmdir``, and ``Path.iterdir``, ``os.scandir``, or ``os.listdir``.
    It never uses ``os.open``, ``os.makedirs``, ``Path.mkdir(parents=True)``, ``Path.touch``,
    ``Path.write_text``, or ``shutil``, because the fault harness of the tests replaces only
    the functions that the calls above use (``os.mkdir``, ``os.rmdir``, ``os.unlink``,
    ``os.remove``, ``os.scandir``, ``os.listdir``, and ``open``). Any other call escapes its
    rules, or gives a record that differs from the steps.

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
    return Creation(CreationOutcome.CREATED)
