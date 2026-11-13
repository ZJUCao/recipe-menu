"""The run function of the ``init`` command."""

import os
from pathlib import Path
from typing import TextIO

from recipe_menu.app import Arguments, Context
from recipe_menu.commands.init._example import (
    CATALOG_TEXT,
    CATEGORY_TOTAL,
    INGREDIENT_TOTAL,
    PANTRY_TEXT,
    PANTRY_TOTAL,
    RECIPE_TEXT,
    SETTINGS_TEXT,
    TAG_TOTAL,
)
from recipe_menu.commands.init.messages import (
    ALREADY_HOLDS_FILES,
    CATALOG_LINE,
    CATEGORY_COUNT,
    CHANGED_NOTHING,
    CHINESE,
    CREATED,
    EMPTY_FOLDER,
    ENGLISH,
    EXAMPLE_RECIPE,
    INGREDIENT_COUNT,
    IS_A_FILE,
    LEFT_BEHIND,
    NEXT_STEP,
    SERVINGS_PER_DISH,
    SETTINGS_LINE,
    TAG_COUNT,
)
from recipe_menu.datafile import (
    Creation,
    CreationOutcome,
    DataFolder,
    Problem,
    create_data_folder,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.settings import Settings
from recipe_menu.text import and_list, format_table

_RECIPE_ID = "tomato-egg"


def _settings_text(lang: Lang) -> str:
    """Gives the text of ``settings.toml`` with the language of the run.

    Args:
        lang: The language of ``init``.

    Returns:
        The example text, with ``lang`` in its ``language`` line.
    """
    return SETTINGS_TEXT.replace('language = "en"', f'language = "{lang.value}"', 1)


def _create(context: Context) -> Creation:
    """Makes the one call to ``create_data_folder``.

    Args:
        context: The language and the data folder.

    Returns:
        What ``create_data_folder`` gave.
    """
    folder = context.folder
    folders = (folder.recipes, folder.menus, folder.shopping)
    files = (
        (folder.settings, _settings_text(context.lang)),
        (folder.catalog, CATALOG_TEXT),
        (folder.pantry, PANTRY_TEXT),
        (folder.recipe_file(_RECIPE_ID), RECIPE_TEXT),
    )
    return create_data_folder(folder, folders, files)


def _name(folder: DataFolder, path: Path, *, is_folder: bool = False) -> str:
    """Gives the name of a path in the table, relative to the data folder.

    Args:
        folder: The data folder.
        path: A path inside it.
        is_folder: ``True`` for a folder, which gets ``os.sep`` at its end.

    Returns:
        The name, with the system's separator.
    """
    return str(folder.relative(path)) + (os.sep if is_folder else "")


def _settings_description(lang: Lang) -> str:
    """Describes ``settings.toml`` as it is written for a language.

    Args:
        lang: The language of the run, which is also the language of the new settings.

    Returns:
        The language, the meals, and the servings.
    """
    settings = Settings(lang)
    meals = and_list([meal.label for meal in settings.meals])
    servings = SERVINGS_PER_DISH.pick(settings.servings).to_bitext(count=settings.servings)
    language: BiText = (ENGLISH if lang is Lang.EN else CHINESE).to_bitext()
    return SETTINGS_LINE.render(lang, language=language, meals=meals, servings=servings)


def _catalog_description(lang: Lang) -> str:
    """Describes ``catalog.toml`` by the counts of the example text.

    Args:
        lang: The language of the line.

    Returns:
        The categories, the ingredients, and the tags.
    """
    return CATALOG_LINE.render(
        lang,
        categories=CATEGORY_COUNT.pick(CATEGORY_TOTAL).to_bitext(count=CATEGORY_TOTAL),
        ingredients=INGREDIENT_COUNT.pick(INGREDIENT_TOTAL).to_bitext(count=INGREDIENT_TOTAL),
        tags=TAG_COUNT.pick(TAG_TOTAL).to_bitext(count=TAG_TOTAL),
    )


def _created_lines(context: Context) -> list[str]:
    """Writes the lines of a new data folder.

    Args:
        context: The language and the data folder.

    Returns:
        The lines, without line ends.
    """
    folder, lang = context.folder, context.lang
    pantry = INGREDIENT_COUNT.pick(PANTRY_TOTAL).render(lang, count=PANTRY_TOTAL)
    empty = EMPTY_FOLDER.render(lang)
    rows = [
        (_name(folder, folder.settings), _settings_description(lang)),
        (_name(folder, folder.catalog), _catalog_description(lang)),
        (_name(folder, folder.pantry), pantry),
        (_name(folder, folder.recipe_file(_RECIPE_ID)), EXAMPLE_RECIPE.render(lang)),
        (_name(folder, folder.menus, is_folder=True), empty),
        (_name(folder, folder.shopping, is_folder=True), empty),
    ]
    recipes = _name(folder, folder.recipes, is_folder=True)
    return [
        CREATED.render(lang, folder=str(folder.root)),
        *format_table(rows, indent=2, gap=4),
        "",
        NEXT_STEP.render(lang, recipes=recipes),
    ]


def _failure_lines(context: Context, problem: Problem, left: tuple[Path, ...]) -> list[str]:
    """Writes the three lines of a failure.

    Args:
        context: The language and the data folder.
        problem: The problem of the failure.
        left: What the call could not remove, as full paths.

    Returns:
        The lines, without line ends.
    """
    root = context.folder.root
    if left:
        last = LEFT_BEHIND.render(context.lang, folder=str(root))
    else:
        last = CHANGED_NOTHING.render(context.lang)
    return [
        str(root / problem.file),
        f"  {problem.text(context.lang)}",
        last,
    ]


def _error_lines(context: Context, creation: Creation) -> list[str]:
    """Writes the lines of a refusal or a failure.

    Args:
        context: The language and the data folder.
        creation: The result, with an outcome other than ``CREATED``.

    Returns:
        The lines, without line ends.
    """
    if creation.problem is not None:
        return _failure_lines(context, creation.problem, creation.left)
    folder = str(context.folder.root)
    if creation.outcome is CreationOutcome.HOLDS_FILES:
        return [ALREADY_HOLDS_FILES.render(context.lang, folder=folder)]
    return [IS_A_FILE.render(context.lang, folder=folder)]


def _write(stream: TextIO, lines: list[str]) -> None:
    """Writes lines to a stream, each ended by a line break.

    Args:
        stream: The stream.
        lines: The lines, without line ends.
    """
    stream.write("".join(f"{line}\n" for line in lines))


def run_init(context: Context, arguments: Arguments) -> int:
    """Creates the data folder with the example data and writes the output.

    It makes one call, ``create_data_folder(context.folder, folders, files)``, with the folders
    ``recipes/``, ``menus/``, and ``shopping/`` and the files ``settings.toml``,
    ``catalog.toml``, ``pantry.toml``, and ``recipes/tomato-egg.toml``, in that order. The text
    of ``settings.toml`` has ``context.lang`` in its ``language`` line. It reads no file.

    On a new folder, it writes to ``context.out`` the line ``CREATED`` with the data folder's
    full path, the six rows of the table, laid out by ``format_table`` with an indent of 2
    and a gap of 4, an empty line, and ``NEXT_STEP`` with
    ``str(context.folder.relative(context.folder.recipes))`` and ``os.sep`` at its end. Each
    first cell is ``str(context.folder.relative(path))`` and a folder gets ``os.sep`` at its
    end. The second cells describe ``settings.toml`` (the language, the meals, and the
    servings of ``Settings(context.lang)``), ``catalog.toml`` (6 categories, 22 ingredients,
    5 tags), ``pantry.toml`` (5 ingredients), the example recipe, and the two empty folders.

    A refusal is one line on ``context.err``: ``ALREADY_HOLDS_FILES`` or ``IS_A_FILE``, each
    with the data folder's full path. A failure is three lines on ``context.err``. The first
    is the full path ``str(context.folder.root / problem.file)``, which departs from the
    relative file of the ``Problem`` on purpose (architecture 6, ADR-0009). The second is two
    spaces and the problem's text in ``context.lang``. The third is ``CHANGED_NOTHING`` when
    ``left`` is empty and ``LEFT_BEHIND`` with the data folder otherwise.

    Every line of the output, the refusal, and the failure is in ``context.lang``, also when
    ``context.settings`` names another language.

    Args:
        context: The language, the data folder, and the two streams. It uses neither
            ``context.settings`` nor ``context.today``.
        arguments: What the command line gave. Empty, because ``init`` takes no argument. It is
            not read.

    Returns:
        0 when ``create_data_folder`` gave ``CREATED``, whose lines went to ``context.out``. 1
        when it gave ``HOLDS_FILES``, ``NOT_A_FOLDER``, or ``FAILED``, whose lines went to
        ``context.err``, with nothing on ``context.out``.

    Raises:
        KeyboardInterrupt: Ctrl+C interrupted the call. It goes on to ``cli`` after
            ``create_data_folder`` has run its removal. The implementation raises nothing else:
            a refusal or a failure on the disk is a value.
    """
    creation = _create(context)
    if creation.outcome is CreationOutcome.CREATED:
        _write(context.out, _created_lines(context))
        return 0
    _write(context.err, _error_lines(context, creation))
    return 1
