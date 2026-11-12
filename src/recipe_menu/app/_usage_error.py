"""The error of a wrong command line or argument value."""

from recipe_menu.lang import Lang
from recipe_menu.text import Message, MessageValue


class UsageError(Exception):
    """A wrong command line or argument value, with its message and the line that follows it.

    The parser raises it, and so does a command for a wrong argument value. ``cli`` turns it into
    exit code 2. It is a plain class and not a frozen dataclass, because Python sets attributes
    such as ``__traceback__`` on an exception. ``__init__`` sets ``message``, ``hint``, and
    ``values`` once, and no code changes them. ``str(error)`` gives the English text, so a
    traceback names the mistake if a bug lets the error escape.

    Creating a ``UsageError`` renders its message once in both languages, so wrong values fail
    where the error is made.

    Attributes:
        message: What is wrong.
        hint: The line that follows the message, such as ``RUN_HELP_FOR_OPTIONS``, or ``None``
            when the message already says what to write.
        values: The value of each placeholder of ``message``, as (name, value) pairs sorted by
            name.

    Raises:
        ValueError: The names of ``values`` are not exactly the placeholders of ``message``.
        TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool`` or
            an ``enum.Enum`` member.
        ValueError: An ``int`` value has more than 4,300 digits.
        ValueError: ``hint`` has a placeholder.
    """

    message: Message
    hint: Message | None
    values: tuple[tuple[str, MessageValue], ...]

    def __init__(
        self,
        message: Message,
        hint: Message | None,
        /,
        **values: MessageValue,
    ) -> None:
        """Makes a usage error.

        Args:
            message: What is wrong. Positional only.
            hint: The line that follows the message, or ``None`` when the message already says
                what to write. It has no placeholders. Positional only, so a message can have a
                placeholder named ``message`` or ``hint``.
            **values: The value of each placeholder of ``message``: one for each placeholder,
                and no others.

        Raises:
            ValueError: The names of ``values`` are not exactly the placeholders of ``message``.
            TypeError: A value is not a ``str``, an ``int``, or a ``BiText``, or it is a ``bool``
                or an ``enum.Enum`` member.
            ValueError: An ``int`` value has more than 4,300 digits.
            ValueError: ``hint`` has a placeholder.
        """
        if hint is not None and hint.placeholders:
            raise ValueError("the hint has a placeholder")
        english = message.render(Lang.EN, **values)
        message.render(Lang.ZH, **values)
        super().__init__(english)
        self.message = message
        self.hint = hint
        self.values = tuple(sorted(values.items(), key=lambda pair: pair[0]))

    def text(self, lang: Lang) -> str:
        """Gives the message in a language.

        Args:
            lang: The language that ``text`` writes.

        Returns:
            ``message.render(lang, **values)``. ``cli`` writes it, and then ``hint.render(lang)``
            when ``hint`` is not ``None``, each on its own line, to the error stream.
        """
        return self.message.render(lang, **dict(self.values))
