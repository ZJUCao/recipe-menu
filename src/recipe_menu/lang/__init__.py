"""The language type of the tool."""

from enum import StrEnum

__all__ = ["Lang"]


class Lang(StrEnum):
    """The two languages of the tool.

    Every interface that writes text for the user takes a ``Lang``. Its values are the values
    that ``--lang`` and the settings' ``language`` take. ``Lang(value)`` raises ``ValueError``
    for an unknown code.
    """

    EN = "en"
    ZH = "zh"
