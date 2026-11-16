"""The lines that ``shop`` writes to the terminal, the Markdown text of the file, and a failure."""

from pathlib import Path
from typing import cast

from recipe_menu.app import Context
from recipe_menu.commands.shop.messages import (
    DISH_COUNT,
    FILE_DATES,
    FILE_TITLE,
    LEFT_BEHIND,
    LIST_HEADING,
    MEAL_COUNT,
    NO_FILE_SAVED,
    NOTHING_TO_BUY,
    PANTRY_LINE,
    SAVED,
)
from recipe_menu.datafile import FileCreation, Problem
from recipe_menu.lang import BiText, Lang
from recipe_menu.shopping import ShoppingList
from recipe_menu.text import comma_list, display_width, format_table


def _counts(shopping: ShoppingList) -> dict[str, BiText]:
    """Writes the counts of meals and dishes of a list, in both languages.

    Args:
        shopping: The shopping list.

    Returns:
        The values ``meals`` and ``dishes`` for ``LIST_HEADING`` and ``FILE_DATES``.
    """
    meals, dishes = shopping.meal_count, shopping.dish_count
    return {
        "meals": MEAL_COUNT.pick(meals).to_bitext(count=meals),
        "dishes": DISH_COUNT.pick(dishes).to_bitext(count=dishes),
    }


def _pantry_line(shopping: ShoppingList, lang: Lang) -> str:
    """Writes the pantry line of a list.

    Args:
        shopping: The shopping list, which uses a pantry ingredient.
        lang: The language.

    Returns:
        ``PANTRY_LINE`` with the names of ``pantry_used`` in a comma list.
    """
    items = comma_list(ingredient.name for ingredient in shopping.pantry_used)
    return PANTRY_LINE.render(lang, items=items)


def file_text(shopping: ShoppingList, lang: Lang) -> str:
    """Builds the Markdown text of the shopping list file.

    Args:
        shopping: The shopping list.
        lang: The language of the run.

    Returns:
        The blocks with one empty line between two blocks: the title, the dates line, each
        group's ``## `` heading and then its ``- [ ] `` lines, or ``NOTHING_TO_BUY``, and the
        pantry line when one is used. Each line is ended by LF, the last one included.
    """
    week, dates = str(shopping.week), shopping.week.date_range
    blocks = [
        f"# {FILE_TITLE.render(lang, week=week)}",
        FILE_DATES.render(lang, dates=dates, **_counts(shopping)),
    ]
    for group in shopping.groups:
        blocks.append(f"## {group.category.name.get(lang)}")
        lines = (f"- [ ] {i.ingredient.name.get(lang)} {i.amount_text(lang)}" for i in group.lines)
        blocks.append("\n".join(lines))
    if not shopping.groups:
        blocks.append(NOTHING_TO_BUY.render(lang))
    if shopping.pantry_used:
        blocks.append(_pantry_line(shopping, lang))
    return "".join(f"{block}\n\n" for block in blocks[:-1]) + f"{blocks[-1]}\n"


def _name_width(shopping: ShoppingList, lang: Lang) -> int:
    """Finds the largest display width of a line of an ingredient's name in the whole list.

    Args:
        shopping: The shopping list.
        lang: The language.

    Returns:
        The width, or 0 for a list with no group.
    """
    names = (line.ingredient.name.get(lang) for group in shopping.groups for line in group.lines)
    return max((display_width(part) for name in names for part in name.splitlines()), default=0)


def list_output(shopping: ShoppingList, lang: Lang, path: Path) -> str:
    """Builds the whole terminal output of a saved list.

    Args:
        shopping: The shopping list.
        lang: The language of the run.
        path: The file that was saved.

    Returns:
        The heading, an empty line, the groups or ``NOTHING_TO_BUY``, an empty line and the
        pantry line when one is used, an empty line, and ``SAVED``, each line ended by a line
        break.
    """
    week, dates = str(shopping.week), shopping.week.date_range
    lines = [LIST_HEADING.render(lang, week=week, dates=dates, **_counts(shopping)), ""]
    width = _name_width(shopping, lang)
    for group in shopping.groups:
        rows = [(i.ingredient.name.get(lang), i.amount_text(lang)) for i in group.lines]
        lines.append(group.category.name.get(lang))
        lines.extend(format_table(rows, indent=2, min_widths=(width,)))
    if not shopping.groups:
        lines.append(NOTHING_TO_BUY.render(lang))
    if shopping.pantry_used:
        lines.extend(["", _pantry_line(shopping, lang)])
    lines.extend(["", SAVED.render(lang, file=str(path))])
    return "".join(f"{line}\n" for line in lines)


def failure_output(context: Context, creation: FileCreation) -> str:
    """Builds the three lines of a failed save.

    Args:
        context: The language and the data folder.
        creation: What ``replace_file`` gave, with ``FAILED``.

    Returns:
        The full path of the file, two spaces and the problem's text, and ``NO_FILE_SAVED`` or
        ``LEFT_BEHIND`` with the full path of the temporary file, each ended by a line break.
    """
    # FAILED always holds a problem.
    problem = cast(Problem, creation.problem)
    last = (
        LEFT_BEHIND.render(context.lang, file=str(creation.left[0]))
        if creation.left
        else NO_FILE_SAVED.render(context.lang)
    )
    lines = (
        str(context.folder.root / problem.file),
        f"  {problem.text(context.lang)}",
        last,
    )
    return "".join(f"{line}\n" for line in lines)
