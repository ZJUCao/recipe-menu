"""A problem in a data file, with its severity, file, place, and message."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message, MessageValue


class Severity(Enum):
    """Whether a problem is an error or a warning.

    An error makes a command exit with 1. A warning never changes the exit code.
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Problem:
    """A problem in a data file: its severity, its file, its place, and its message with values.

    Readers return problems and never raise them. Two problems are equal when all five fields
    are equal, and a ``Problem`` is hashable. ``str(problem.file)`` writes the path with the
    system's separator.

    The constructor checks its values by rendering ``message`` once in both languages, so wrong
    values fail at once. It also sorts ``values`` by name, so their order does not matter.

    Attributes:
        severity: An error or a warning.
        file: The file, relative to the data folder, from ``DataFolder.relative``. Not an
            absolute path.
        place: The place in the file, in both languages, such as "line 2" and its Chinese
            text. ``None`` for a problem of the whole file.
        message: What is wrong, and what to do about it.
        values: The value of each placeholder of ``message``, as (name, value) pairs. One pair
            for each placeholder, and no others.

    Raises:
        ValueError: ``file`` is an absolute path, the names in ``values`` are not exactly the
            placeholders of ``message``, a name appears twice in ``values``, or an ``int``
            value has more than 4,300 digits.
        TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
            or an ``enum.Enum`` member, which ``Message.render`` rejects.
    """

    severity: Severity
    file: Path
    place: BiText | None
    message: Message
    values: tuple[tuple[str, MessageValue], ...] = ()

    def __post_init__(self) -> None:
        """Checks the values by rendering the message in both languages, and sorts them.

        Raises:
            ValueError: ``file`` is an absolute path, a name appears twice in ``values``, or the
                names are not exactly the placeholders of ``message``, or an ``int`` has too
                many digits.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
                or an ``enum.Enum`` member.
        """
        if self.file.is_absolute():
            raise ValueError(f"the file of a problem must be relative: {self.file}")
        names = [name for name, _ in self.values]
        if len(set(names)) != len(names):
            raise ValueError("a name appears twice in the values of a problem")
        values = dict(self.values)
        for lang in Lang:
            self.message.render(lang, **values)
        object.__setattr__(self, "values", tuple(sorted(self.values, key=lambda pair: pair[0])))

    @classmethod
    def _make(
        cls,
        severity: Severity,
        file: Path,
        place: BiText | None,
        message: Message,
        values: dict[str, MessageValue],
    ) -> Problem:
        """Makes a problem of a severity, with its values as pairs.

        Args:
            severity: The severity.
            file: The file, relative to the data folder.
            place: The place in the file, or ``None``.
            message: What is wrong.
            values: The value of each placeholder, by its name.

        Returns:
            The ``Problem``.

        Raises:
            ValueError: As the constructor.
            TypeError: As the constructor.
        """
        return cls(severity, file, place, message, tuple(values.items()))

    @classmethod
    def error(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem:
        """Makes a problem with ``Severity.ERROR``.

        Args:
            file: The file, relative to the data folder. Positional only, so a message can have
                a placeholder named ``file``.
            place: The place in the file, or ``None`` for a problem of the whole file.
                Positional only.
            message: What is wrong. Positional only.
            **values: The value of each placeholder of ``message``, by its name. One for each
                placeholder, and no others.

        Returns:
            A ``Problem`` with ``Severity.ERROR``, the given file, place, and message, and
            ``values`` as pairs sorted by name.

        Raises:
            ValueError: ``file`` is an absolute path, the names of ``values`` are not exactly
                the placeholders of ``message``, or an ``int`` value has more than 4,300 digits.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a
                ``bool`` or an ``enum.Enum`` member.
        """
        return cls._make(Severity.ERROR, file, place, message, values)

    @classmethod
    def warning(
        cls,
        file: Path,
        place: BiText | None,
        message: Message,
        /,
        **values: MessageValue,
    ) -> Problem:
        """Makes a problem with ``Severity.WARNING``.

        Args:
            file: The file, relative to the data folder. Positional only, so a message can have
                a placeholder named ``file``.
            place: The place in the file, or ``None`` for a problem of the whole file.
                Positional only.
            message: What is wrong. Positional only.
            **values: The value of each placeholder of ``message``, by its name. One for each
                placeholder, and no others.

        Returns:
            A ``Problem`` with ``Severity.WARNING``, the given file, place, and message, and
            ``values`` as pairs sorted by name.

        Raises:
            ValueError: ``file`` is an absolute path, the names of ``values`` are not exactly
                the placeholders of ``message``, or an ``int`` value has more than 4,300 digits.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a
                ``bool`` or an ``enum.Enum`` member.
        """
        return cls._make(Severity.WARNING, file, place, message, values)

    def text(self, lang: Lang) -> str:
        """Writes the message of the problem in one language.

        Args:
            lang: The language to write.

        Returns:
            ``message.render(lang, **values)``, with the values of the problem.
        """
        return self.message.render(lang, **dict(self.values))
