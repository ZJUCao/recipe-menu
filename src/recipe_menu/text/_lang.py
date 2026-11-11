"""The choice of the language of a command."""

from recipe_menu.lang import Lang


def choose_lang(option: Lang | None, setting: Lang | None) -> Lang:
    """Picks the language of a command: ``--lang`` first, then the settings, then English.

    Args:
        option: The language that ``--lang`` names, or ``None`` when the command line has none.
        setting: The ``language`` of the settings, or ``None`` when the settings name no
            language or there are no settings.

    Returns:
        ``option`` when it is not ``None``, else ``setting`` when it is not ``None``, else
        ``Lang.EN``.
    """
    if option is not None:
        return option
    if setting is not None:
        return setting
    return Lang.EN
