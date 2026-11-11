"""Messages with an English and a Chinese template, and English plurals."""

from dataclasses import dataclass

from recipe_menu.lang import BiText, Lang

type MessageValue = str | int | BiText


@dataclass(frozen=True, slots=True)
class Message:
    """A text that the tool shows, with an English and a Chinese template.

    Both templates hold the same ``{name}`` placeholders. A placeholder is a name in braces. The
    name has lowercase ASCII letters, digits, and ``_``, and starts with a letter. A name can
    appear more than once, and the templates can hold the names in different orders. A
    placeholder has no conversion and no format spec, not even an empty one such as
    ``{count:}``. To show a brace itself, a template writes it twice, as ``str.format`` does.
    Two messages are equal when both templates are equal, and a ``Message`` is hashable.

    The mock does not check its templates, so that the constants of the module build at import.
    The finished class checks them when it is built and raises ``TypeError`` when ``en`` or
    ``zh`` is not a ``str``. It raises ``ValueError`` when a template is empty or only
    whitespace, when a template is not a valid format string (such as a single brace), when a
    placeholder is not a name by the rules above (such as ``{}``, ``{0}``, ``{Name}``,
    ``{tag.en}``), when a placeholder has a conversion or a format spec (such as ``{count!r}``,
    ``{count:>3}``, ``{count:}``), and when the two templates hold different sets of names.

    Attributes:
        en: The English template.
        zh: The Chinese template.
    """

    en: str
    zh: str

    @property
    def placeholders(self) -> frozenset[str]:
        """Gives the placeholder names of the templates.

        Returns:
            The set of names in the two templates, which is empty for a message with no
            placeholders.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

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
            NotImplementedError: In the mock.
        """
        raise NotImplementedError

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
            NotImplementedError: In the mock.
        """
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Plural:
    """An English plural: one message for a count of 1, and one for every other count.

    Chinese has no plural, so the Chinese templates of the two messages are usually the same.
    Two values are equal when both messages are equal, and a ``Plural`` is hashable.

    The mock does not check its messages. The finished class raises ``ValueError`` when it is
    built and ``one`` and ``other`` have different placeholder names.

    Attributes:
        one: The message for a count of 1.
        other: The message for every other count, 0 included.
    """

    one: Message
    other: Message

    def pick(self, count: int) -> Message:
        """Chooses the message for a count.

        Args:
            count: The count to choose by. Any ``int``.

        Returns:
            ``one`` when ``count`` is 1, and ``other`` for every other count, such as 0, 2, or 7.

        Raises:
            NotImplementedError: In the mock.
        """
        raise NotImplementedError
