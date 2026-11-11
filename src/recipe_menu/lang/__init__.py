"""The language type of the tool and the text that holds both languages."""

from dataclasses import dataclass
from enum import StrEnum
from typing import cast

__all__ = ["BiText", "Lang"]


class Lang(StrEnum):
    """The two languages of the tool.

    Every interface that writes text for the user takes a ``Lang``. Its values are the values
    that ``--lang`` and the settings' ``language`` take. ``Lang(value)`` raises ``ValueError``
    for an unknown code.
    """

    EN = "en"
    ZH = "zh"


@dataclass(frozen=True, slots=True)
class BiText:
    """A text in two languages, with at least one of them.

    It holds a recipe name or an ingredient's note. It gives the asked language, or the other
    language when the asked one is missing. Two values are equal when their ``en`` and their
    ``zh`` are equal, and a ``BiText`` is hashable. An empty string counts as a text, so ``get``
    gives it with no fallback. A reader that treats an empty name as missing passes ``None``.

    Attributes:
        en: The English text, or ``None`` when the text has no English.
        zh: The Chinese text, or ``None`` when the text has no Chinese.

    Raises:
        ValueError: ``en`` and ``zh`` are both ``None``.
        TypeError: ``en`` or ``zh`` is neither a ``str`` nor ``None``.
    """

    en: str | None = None
    zh: str | None = None

    def __post_init__(self) -> None:
        """Checks the fields.

        Raises:
            TypeError: ``en`` or ``zh`` is neither a ``str`` nor ``None``.
            ValueError: ``en`` and ``zh`` are both ``None``.
        """
        for value in (self.en, self.zh):
            if value is not None and not isinstance(value, str):
                raise TypeError(f"a text must be a str or None, not {type(value).__name__}")
        if self.en is None and self.zh is None:
            raise ValueError("a BiText needs at least one language")

    def get(self, lang: Lang) -> str:
        """Gives the text in a language, with a fallback.

        Args:
            lang: The language to give.

        Returns:
            The text in ``lang``, or the text in the other language when the one in ``lang`` is
            ``None``. It never gives ``None``. An empty string is a text and has no fallback.
        """
        first, second = (self.en, self.zh) if lang is Lang.EN else (self.zh, self.en)
        # __post_init__ keeps at least one of the two languages set.
        return first if first is not None else cast(str, second)

    def exact(self, lang: Lang) -> str | None:
        """Gives the text in a language, with no fallback.

        Args:
            lang: The language to give.

        Returns:
            The text in ``lang``, or ``None`` when that text is missing. A reader uses it to
            warn about a missing language.
        """
        return self.en if lang is Lang.EN else self.zh
