"""The matching form of a name or a key."""

from typing import Final

_ASCII_SMALL: Final = {code: code + 32 for code in range(ord("A"), ord("Z") + 1)}


def matching_form(text: str) -> str:
    """Gives the matching form of a text.

    Args:
        text: A name or a key, as written.

    Returns:
        The text without whitespace at both ends (``str.strip()``), with each ASCII capital
        letter from A to Z changed to its small letter. Nothing else changes: look-alike letters
        stay, and no text is normalized. Two texts match when their matching forms are equal.
    """
    return text.strip().translate(_ASCII_SMALL)


def is_blank(text: str) -> bool:
    """Tells whether a text is empty or holds only whitespace.

    Args:
        text: Any string.

    Returns:
        ``True`` when ``text.strip()`` is empty.
    """
    return not text.strip()
