"""The run function of the ``init`` command."""

from recipe_menu.app import Arguments, Context


def run_init(context: Context, arguments: Arguments) -> int:
    """Creates the data folder with the example data and writes the output.

    It makes one call, ``create_data_folder(context.folder, folders, files)``, with the folders
    ``recipes/``, ``menus/``, and ``shopping/`` and the files ``settings.toml``,
    ``catalog.toml``, ``pantry.toml``, and ``recipes/tomato-egg.toml``, in that order. The text
    of ``settings.toml`` has ``context.lang`` in its ``language`` line. It reads no file.

    The mock writes nothing and gives 0.

    On a new folder, it writes to ``context.out`` the line ``CREATED`` with the data folder's
    full path, the six rows of the table, laid out by ``format_table`` with an indent of 2
    and a gap of 4, an empty line, and ``NEXT_STEP`` with
    ``str(context.folder.relative(context.folder.recipes))`` and ``os.sep`` at its end. Each
    first cell is ``str(context.folder.relative(path))`` and a folder gets ``os.sep`` at its
    end. The second cells
    describe ``settings.toml`` (the language, the meals, and the servings of
    ``Settings(context.lang)``), ``catalog.toml`` (6 categories, 22 ingredients, 5 tags),
    ``pantry.toml`` (5 ingredients), the example recipe, and the two empty folders.

    A refusal is one line on ``context.err``: ``ALREADY_HOLDS_FILES`` or ``IS_A_FILE``, each
    with the data folder's full path. A failure is three lines on ``context.err``. The first
    is the full path ``str(context.folder.root / problem.file)``, which departs from the
    relative file of the ``Problem`` on purpose (architecture 6, ADR-0009). The second is two
    spaces and the problem's text in ``context.lang``. The third is ``CHANGED_NOTHING`` when
    ``left`` is empty and ``LEFT_BEHIND`` with the data folder otherwise.

    Every line of the output, the refusal, and the failure is in ``context.lang``, never in the
    language of ``context.settings``.

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
    return 0
