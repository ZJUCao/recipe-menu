"""The language type of the tool and the text that holds both languages."""

from dataclasses import dataclass
from enum import StrEnum

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

    The mock does not check its fields. The finished class checks them when it is built and
    raises ``ValueError`` when ``en`` and ``zh`` are both ``None``, and ``TypeError`` when
    ``en`` or ``zh`` is neither a ``str`` nor ``None``.

    Attributes:
        en: The English text, or ``None`` when the text has no English.
        zh: The Chinese text, or ``None`` when the text has no Chinese.
    """

    en: str | None = None
    zh: str | None = None

    def get(self, lang: Lang) -> str:
        """Gives the text in a language, with a fallback.

        Args:
            lang: The language to give.

        Returns:
            The text in ``lang``, or the text in the other language when the one in ``lang`` is
            ``None``. It never gives ``None``. An empty string is a text and has no fallback.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

    def exact(self, lang: Lang) -> str | None:
        """Gives the text in a language, with no fallback.

        Args:
            lang: The language to give.

        Returns:
            The text in ``lang``, or ``None`` when that text is missing. A reader uses it to
            warn about a missing language.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError
