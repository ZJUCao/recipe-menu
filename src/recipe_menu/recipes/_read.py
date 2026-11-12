"""Reading recipe files into recipes."""

from collections.abc import Mapping

from recipe_menu.catalog import Catalog
from recipe_menu.datafile import (
    MISSING_KEY,
    DataFolder,
    Problem,
    Report,
    Severity,
    read_servings,
    read_toml,
    report_unknown_keys,
)
from recipe_menu.recipes._ids import is_recipe_id, list_recipe_ids
from recipe_menu.recipes._model import Recipe
from recipe_menu.recipes._read_lines import read_ingredients, read_tags
from recipe_menu.recipes._read_steps import read_name, read_steps
from recipe_menu.recipes.messages import SERVINGS

_KEYS = ("name", "servings", "tags", "ingredients", "steps")


def _read_servings(table: Mapping[str, object], report: Report) -> int | None:
    """Reads the servings of the recipe.

    Args:
        table: The table of the file.
        report: Where the problem goes.

    Returns:
        The servings from 1 to 100, or ``None`` after a problem.
    """
    if "servings" not in table:
        report.add(None, MISSING_KEY, key="servings")
        return None
    return read_servings(table["servings"], SERVINGS.to_bitext(), report)


def read_recipe(
    folder: DataFolder,
    catalog: Catalog | None,
    recipe_id: str,
) -> tuple[Recipe | None, tuple[Problem, ...]]:
    """Reads one recipe file into a recipe, and reports each problem with its place.

    It reads ``recipes/<id>.toml`` through ``read_toml``. It lists no folder and writes nothing.
    It checks the whole file and never raises for bad data, so one run reports every problem.

    Args:
        folder: The data folder.
        catalog: The catalog that the names of the ingredients and the tags come from, or
            ``None`` when the catalog could not be read. Then only the form of the file is
            checked.
        recipe_id: The ID of the recipe, such as ``tomato-egg``. ``is_recipe_id(recipe_id)`` is
            true, and it is an ID that ``list_recipe_ids`` gave.

    Returns:
        A pair ``(recipe, problems)``.

        ``recipe`` is ``None`` when ``catalog`` is ``None``, or when ``problems`` holds an
        error. Otherwise it is a ``Recipe`` with the ID ``recipe_id``, even when ``problems``
        holds warnings. Each text in it is stored without whitespace at both ends. It holds each
        tag once, in the order of the first item that names it, and each ingredient line in the
        file's order. A note with neither language is ``None``, and a language that is missing
        is ``None`` in the name, a note, or the steps.

        ``problems`` holds the one problem of ``read_toml`` alone, when the file is missing,
        cannot be read, is not UTF-8, or is not valid TOML. Otherwise it holds the problems of
        the checks of the file's layout, and each has the file ``recipes/<id>.toml``, relative
        to the data folder. The layout has the keys ``name``, ``servings``, ``tags``,
        ``ingredients``, and ``steps``, all required, and no other key at the top.

        The parts come in the order ``name``, ``servings``, ``tags``, ``ingredients``,
        ``steps``, and then the other keys at the top, in the file's order. Within a part, a
        list's own problem comes first, and then the problems of each item, in order. An
        ingredient's problems come key by key: ``item``, ``amount``, ``note``, and then its
        unknown keys in the file's order. A name, a note, or the steps give the problems of
        ``zh``, then those of ``en``, then their unknown keys in the file's order, and then
        ``NO_NAME``, ``NO_STEPS``, or the warning for the missing language.

        The places are ``name``, ``servings``, ``tags``, ``tag N``, ``ingredients``,
        ``ingredient N``, ``steps``, ``Chinese step N``, and ``English step N``. Each place is
        a ``BiText`` whose Chinese text comes from ``recipes/messages.py``. N counts the items of
        a list from 1, skipped items included. The place of ``UNKNOWN_TAG`` is ``tags``, and the
        place of every problem of a note is ``ingredient N``. A missing key at the top has no place.

        A language of the name, of a note, or of the steps is missing when its key is missing,
        or, in the name or a note, when it holds a blank text, or, in the steps, when it holds
        the empty list. It is usable when it holds a text with more than whitespace, or in the
        steps a list with such a text. It is wrong when it holds anything else, and the steps
        hold only lists, so a text in the steps, even ``""``, is wrong. So a blank text in the
        steps is never read as missing. When one language is usable and the other is missing, the
        missing one gets a warning, and when both are missing the name gets ``NO_NAME`` and the
        steps get ``NO_STEPS``. A note with both languages missing is no note.

        ``amount`` is read with ``parse_quantity(amount, unit)``, where ``unit`` is the default
        unit of the ingredient that ``item`` names. When ``item`` has a problem, or ``catalog``
        is ``None``, it is read with no default unit, and every reason except ``NO_UNIT`` is
        reported. ``NOT_A_NUMBER`` gives ``AMOUNT_NOT_A_NUMBER``, ``UNKNOWN_UNIT`` gives
        ``AMOUNT_UNKNOWN_UNIT``, ``NO_UNIT`` gives ``AMOUNT_NO_UNIT`` only when ``item`` names
        an ingredient of the catalog, and ``ZERO`` gives ``AMOUNT_ZERO``. ``EMPTY`` gives
        nothing, because ``EMPTY_TEXT`` reports a blank ``amount`` first.

        The messages for the shape of a file are those of ``datafile``. ``UNKNOWN_KEY`` has the
        form for the number of keys of the table: five at the top of the file, three in an
        ingredient, and two in ``name``, a note, and ``steps``. The values are these. ``key`` is
        the key as the file writes it. ``keys`` is ``and_list`` of the keys of the table, in the
        order above. ``servings`` is the number from the file, shown only when it has at most
        15 digits (see check (a) below). ``tag`` is the item without whitespace at both ends.
        ``name`` is ``item`` without whitespace at both ends. ``amount`` is the text of the
        ``WrongQuantity``, and ``unit`` is its unit. ``ingredient`` is the name of the
        ingredient as its ``BiText``. ``number`` is N.

        The checks, and the problem that each gives, are these. Every problem is an error,
        except the warnings in (f).

        (a) ``servings``: any value that is not an integer, such as a text, a float, a boolean
        (named because a Python ``bool`` is an ``int``), a list, a table, or a date, or an
        integer of 16 or more digits, gives ``SERVINGS_NOT_A_NUMBER``. An integer from
        -999,999,999,999,999 to 0 gives ``SERVINGS_TOO_FEW``, and one from 101 to
        999,999,999,999,999 gives ``SERVINGS_TOO_MANY``.

        (b) A ``name`` or a ``note`` that is not a table gives ``NOT_A_ZH_EN_TABLE`` with ``key``
        set to ``name`` or ``note``. A ``steps`` that is not a table gives ``NOT_A_STEPS_TABLE``.
        A part of the wrong kind gets only that check, and every other part is still checked.

        (c) A wrong language gives ``NOT_A_TEXT`` at its place in a name or a note, and
        ``NOT_A_LIST`` at ``steps``.

        (d) A missing key at the top, any of the five, gives ``MISSING_KEY`` with no place. A
        ``tags`` or ``ingredients`` that is not a list gives ``NOT_A_LIST`` at the list. A tag or
        a step that is not a text gives ``ITEM_NOT_A_TEXT``, and a blank one gives
        ``EMPTY_ITEM``, at ``tag N``, ``Chinese step N``, or ``English step N``. A tag that
        ``find_tag`` does not find gives ``UNKNOWN_TAG``. A tag that an earlier item already
        named gives no problem.

        (e) An ingredient that is not a table gives ``NOT_A_TABLE``. ``item`` is required, and
        when it is missing, not a text, or blank it gives ``MISSING_KEY``, ``NOT_A_TEXT``, or
        ``EMPTY_TEXT``. An ``item`` that ``find_ingredient`` does not find gives
        ``UNKNOWN_INGREDIENT``. ``amount`` is required, with the same three checks. ``note`` is
        optional. All at ``ingredient N``.

        (f) The warnings are ``NO_ZH_NAME``, ``NO_EN_NAME``, ``NO_ZH_NOTE``, ``NO_EN_NOTE``,
        ``NO_ZH_STEPS``, and ``NO_EN_STEPS``. Every other problem is an error.

        (g) An unknown key at the top gives ``UNKNOWN_KEY`` with no place, and an unknown key in
        a name, a note, an ingredient, or the steps gives ``UNKNOWN_KEY`` at the place of that
        table: ``name``, ``ingredient N``, or ``steps``.

        The order rules above give the order of these problems.

        With ``catalog`` ``None``, every check is made except ``UNKNOWN_TAG``,
        ``UNKNOWN_INGREDIENT``, and ``AMOUNT_NO_UNIT``.

    Raises:
        ValueError: ``is_recipe_id(recipe_id)`` is false. It is checked before the file is read.
    """
    if not is_recipe_id(recipe_id):
        raise ValueError(f"not a recipe ID: {recipe_id!r}")
    path = folder.recipe_file(recipe_id)
    table = read_toml(folder, path)
    if isinstance(table, Problem):
        return None, (table,)
    report = Report(folder.relative(path))
    name = read_name(table, report)
    servings = _read_servings(table, report)
    tags = read_tags(table, catalog, report)
    ingredients = read_ingredients(table, catalog, report)
    steps = read_steps(table, report)
    report_unknown_keys(table, _KEYS, None, report)
    problems = tuple(report.problems)
    failed = any(problem.severity is Severity.ERROR for problem in problems)
    if catalog is None or failed or name is None or servings is None or steps is None:
        return None, problems
    return Recipe(recipe_id, name, servings, tags, ingredients, steps), problems


def read_recipes(
    folder: DataFolder,
    catalog: Catalog | None,
) -> tuple[tuple[Recipe, ...], tuple[Problem, ...]]:
    """Reads every recipe file in ``recipes/``, and reports every problem.

    It calls ``list_recipe_ids`` once, and then ``read_recipe`` once for each ID, in the order of
    the IDs. It lists ``recipes/`` once through ``list_toml_files``, reads each recipe file once
    through ``read_toml``, and writes nothing. It never raises for bad data.

    Args:
        folder: The data folder.
        catalog: The catalog, as for ``read_recipe``, or ``None`` when the catalog could not be
            read.

    Returns:
        A pair ``(recipes, problems)``. ``recipes`` holds each recipe that ``read_recipe``
        gives, in the order of the IDs. A file with an error gives no recipe, and ``recipes`` is
        empty when ``catalog`` is ``None``. ``problems`` holds the problems of
        ``list_recipe_ids``, and then the problems that ``read_recipe`` gives for each ID, in
        the order of the IDs.
    """
    ids, problems = list_recipe_ids(folder)
    recipes: list[Recipe] = []
    found = list(problems)
    for recipe_id in ids:
        recipe, recipe_problems = read_recipe(folder, catalog, recipe_id)
        found.extend(recipe_problems)
        if recipe is not None:
            recipes.append(recipe)
    return tuple(recipes), tuple(found)
