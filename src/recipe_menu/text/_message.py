"""Messages with an English and a Chinese template, and English plurals."""

import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from recipe_menu.lang import BiText, Lang

type MessageValue = str | int | BiText

# One token of a template: an escaped brace, a braced span, or a lone brace.
_TOKEN = re.compile(r"\{\{|\}\}|\{([^{}]*)\}|[{}]")
_NAME = re.compile(r"[a-z][a-z0-9_]*")


def _names(template: str) -> frozenset[str]:
    """Reads the placeholder names of a template.

    Args:
        template: A template.

    Returns:
        The set of names.

    Raises:
        ValueError: The template is not a valid format string, or a placeholder is not a plain
            name (it is empty, has a conversion or a format spec, or has other characters).
    """
    names: set[str] = set()
    for match in _TOKEN.finditer(template):
        token = match.group(0)
        if token in ("{{", "}}"):
            continue
        name = match.group(1)
        if name is None:
            raise ValueError(f"a single brace in {template!r}")
        if not _NAME.fullmatch(name):
            raise ValueError(f"{name!r} is not a placeholder name in {template!r}")
        names.add(name)
    return frozenset(names)


def _check_template(template: object) -> None:
    """Checks the type and the content of a template.

    Args:
        template: The value to check.

    Raises:
        TypeError: ``template`` is not a ``str``.
        ValueError: ``template`` is empty or only whitespace.
    """
    if not isinstance(template, str):
        raise TypeError(f"a template must be a str, not {type(template).__name__}")
    if not template.strip():
        raise ValueError("a template must hold more than whitespace")


def _text_of(value: object, lang: Lang) -> str:
    """Writes one value as text.

    Args:
        value: The value of a placeholder.
        lang: The language for a ``BiText``.

    Returns:
        The text of the value.

    Raises:
        TypeError: The value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
            or an ``enum.Enum`` member.
        ValueError: An ``int`` has more digits than ``sys.int_info.default_max_str_digits``.
    """
    if isinstance(value, Enum | bool) or not isinstance(value, str | int | BiText):
        raise TypeError(f"a value must be a str, an int, or a BiText, not {type(value).__name__}")
    if isinstance(value, BiText):
        return value.get(lang)
    if isinstance(value, int):
        limit = sys.int_info.default_max_str_digits
        if abs(value).bit_length() > 3 * limit and abs(value) >= 10**limit:
            raise ValueError(f"an int value has more than {limit} digits")
        return str(Decimal(value))
    return value


@dataclass(frozen=True, slots=True)
class Message:
    """A text that the tool shows, with an English and a Chinese template.

    Both templates hold the same ``{name}`` placeholders. A placeholder is a name in braces. The
    name has lowercase ASCII letters, digits, and ``_``, and starts with a letter. A name can
    appear more than once, and the templates can hold the names in different orders. A
    placeholder has no conversion and no format spec, not even an empty one such as
    ``{count:}``. To show a brace itself, a template writes it twice, as ``str.format`` does.
    Two messages are equal when both templates are equal, and a ``Message`` is hashable.

    Attributes:
        en: The English template.
        zh: The Chinese template.

    Raises:
        TypeError: ``en`` or ``zh`` is not a ``str``.
        ValueError: A template is empty or only whitespace, a template is not a valid format
            string (such as a single brace), a placeholder is not a name by the rules above
            (such as ``{}``, ``{0}``, ``{Name}``, ``{tag.en}``), a placeholder has a conversion
            or a format spec (such as ``{count!r}``, ``{count:>3}``, ``{count:}``), or the two
            templates hold different sets of names.
    """

    en: str
    zh: str

    def __post_init__(self) -> None:
        """Checks the templates.

        Raises:
            TypeError: ``en`` or ``zh`` is not a ``str``.
            ValueError: A template is wrong, or the two hold different names.
        """
        _check_template(self.en)
        _check_template(self.zh)
        if _names(self.en) != _names(self.zh):
            raise ValueError("the two templates hold different placeholder names")

    @property
    def placeholders(self) -> frozenset[str]:
        """Gives the placeholder names of the templates.

        Returns:
            The set of names in the two templates, which is empty for a message with no
            placeholders.
        """
        return _names(self.en)

    def render(self, lang: Lang, /, **values: MessageValue) -> str:
        """Writes the message in one language with its values.

        Args:
            lang: The language to write. Positional only, so a template can have a placeholder
                named ``lang``.
            **values: The value of each placeholder, by its name. One for each placeholder, and
                no others.

        Returns:
            The template in ``lang`` with each placeholder replaced by its value. A ``str`` goes
            in as it is, and an ``int`` as its decimal digits with no thousands separator. A
            ``BiText`` goes in as its ``get(lang)``, so a value that lacks ``lang`` falls back
            to its other language. A value goes in as it is, so a brace in a value is never
            read as a placeholder.

        Raises:
            ValueError: The names of ``values`` are not exactly the placeholders. This is
                checked before the types. Also when an ``int`` value has more than 4,300 digits
                (``sys.int_info.default_max_str_digits``).
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, such as a
                ``float`` or ``None``. A ``bool`` and an ``enum.Enum`` member are wrong too,
                including a ``StrEnum`` member such as ``Lang.ZH``.
        """
        if values.keys() != self.placeholders:
            raise ValueError("the names of the values are not exactly the placeholders")
        texts = {name: _text_of(value, lang) for name, value in values.items()}

        def fill(match: re.Match[str]) -> str:
            """Replaces one token of the template.

            Args:
                match: The token.

            Returns:
                The text that takes its place.
            """
            token = match.group(0)
            if token in ("{{", "}}"):
                return token[0]
            return texts[match.group(1)]

        template = self.en if lang is Lang.EN else self.zh
        return _TOKEN.sub(fill, template)

    def to_bitext(self, /, **values: MessageValue) -> BiText:
        """Writes the message in both languages.

        Args:
            **values: The value of each placeholder, by its name. One for each placeholder, and
                no others.

        Returns:
            ``BiText(self.render(Lang.EN, **values), self.render(Lang.ZH, **values))``, with
            the value rules of ``render``.

        Raises:
            ValueError: As ``render``: the names of ``values`` are not exactly the
                placeholders, checked before the types, or an ``int`` has more than 4,300
                digits.
            TypeError: As ``render``: a value is not a ``str``, an ``int``, or a ``BiText``,
                or it is a ``bool`` or an ``enum.Enum`` member.
        """
        return BiText(self.render(Lang.EN, **values), self.render(Lang.ZH, **values))


@dataclass(frozen=True, slots=True)
class Plural:
    """An English plural: one message for a count of 1, and one for every other count.

    Chinese has no plural, so the Chinese templates of the two messages are usually the same.
    Two values are equal when both messages are equal, and a ``Plural`` is hashable.

    Attributes:
        one: The message for a count of 1.
        other: The message for every other count, 0 included.

    Raises:
        ValueError: ``one`` and ``other`` have different placeholder names.
    """

    one: Message
    other: Message

    def __post_init__(self) -> None:
        """Checks that the two messages hold the same names.

        Raises:
            ValueError: ``one`` and ``other`` have different placeholder names.
        """
        if self.one.placeholders != self.other.placeholders:
            raise ValueError("one and other have different placeholder names")

    def pick(self, count: int) -> Message:
        """Chooses the message for a count.

        Args:
            count: The count to choose by. Any ``int``.

        Returns:
            ``one`` when ``count`` is 1, and ``other`` for every other count, such as 0, 2, or 7.
        """
        return self.one if count == 1 else self.other
