"""The lines that ``menu suggest`` writes: the result of a fill, a refusal, and a failure."""

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from recipe_menu.app import Context, problem_lines
from recipe_menu.catalog import Tag
from recipe_menu.commands.suggest.messages import (
    CANNOT_FILL,
    CHANGED_NOTHING,
    FILLED,
    FILLED_SOME,
    FILLED_SOME_WITH_TAG,
    FILLED_WITH_TAG,
    KEPT,
    LEFT_BEHIND,
    NO_EMPTY_MEAL,
    NO_TWICE,
    RUN_SHOW,
    STAY_EMPTY,
    STAY_EMPTY_WITH_TAG,
    SWAP_HINT,
    TOO_FEW,
    TOO_FEW_WITH_TAG,
    WITH_KEPT,
)
from recipe_menu.datafile import FileCreation, Problem
from recipe_menu.lang import BiText
from recipe_menu.menus import IsoWeek


@dataclass(frozen=True, slots=True)
class Counts:
    """The numbers that the output of a fill reports.

    Attributes:
        empty: The number of empty meals.
        filled: The number of empty meals that got dishes.
        kept: The number of meals that already had dishes.
        candidates_left: Whether drawn recipes are left that no remaining meal could take.
    """

    empty: int
    filled: int
    kept: int
    candidates_left: bool


def _swap_hint(context: Context, week: IsoWeek, path: Path) -> str:
    """Writes the line that tells how to swap a dish.

    Args:
        context: The language and the data folder.
        week: The week.
        path: The menu file.

    Returns:
        ``SWAP_HINT`` with the file relative to the data folder.
    """
    file = str(context.folder.relative(path))
    return SWAP_HINT.render(context.lang, file=file, week=str(week))


def no_empty_meal(context: Context, week: IsoWeek, path: Path) -> str:
    """Builds the output for a week with no empty meal.

    Args:
        context: The language and the data folder.
        week: The week.
        path: The menu file.

    Returns:
        ``NO_EMPTY_MEAL`` and the swap line, each ended by a line break.
    """
    lines = [NO_EMPTY_MEAL.render(context.lang, week=str(week)), _swap_hint(context, week, path)]
    return "".join(f"{line}\n" for line in lines)


def _first_line(week: IsoWeek, tag: Tag | None, empty: int, filled: int) -> BiText:
    """Writes the first line of the output, in both languages.

    Args:
        week: The week.
        tag: The tag of ``--tag``, or ``None``.
        empty: The number of empty meals.
        filled: The number of empty meals that got dishes.

    Returns:
        The line for a fill of every empty meal or of some, with the tag when it is given.
    """
    values: dict[str, str | int | BiText] = {"week": str(week)}
    if tag is not None:
        values["tag"] = tag.name
    if filled == empty:
        plural = FILLED if tag is None else FILLED_WITH_TAG
        return plural.pick(filled).to_bitext(count=filled, **values)
    plural = FILLED_SOME if tag is None else FILLED_SOME_WITH_TAG
    return plural.pick(empty).to_bitext(count=empty, filled=filled, **values)


def _reason(context: Context, tag: Tag | None, count: int, candidates_left: bool) -> str:
    """Writes the line that says why some empty meals stay empty.

    Args:
        context: The language.
        tag: The tag of ``--tag``, or ``None``.
        count: The number of meals that stay empty.
        candidates_left: Whether candidates are left that no remaining meal can take.

    Returns:
        ``TOO_FEW`` when candidates are left and ``STAY_EMPTY`` otherwise, each in its form with
        the tag when it is given.
    """
    plurals = (TOO_FEW, TOO_FEW_WITH_TAG) if candidates_left else (STAY_EMPTY, STAY_EMPTY_WITH_TAG)
    if tag is None:
        return plurals[0].pick(count).render(context.lang, count=count)
    return plurals[1].pick(count).render(context.lang, count=count, tag=tag.name)


def _head(context: Context, first: BiText, kept: int) -> str:
    """Writes the first line of the output, joined with the kept meals when there are any.

    Args:
        context: The language.
        first: The first line, in both languages.
        kept: The number of kept meals.

    Returns:
        One line: ``first`` alone, or ``WITH_KEPT`` with ``first`` and the kept meals.
    """
    if kept == 0:
        return first.get(context.lang)
    return WITH_KEPT.render(context.lang, first=first, kept=KEPT.pick(kept).to_bitext(count=kept))


def fill_output(
    context: Context,
    week: IsoWeek,
    path: Path,
    tag: Tag | None,
    counts: Counts,
) -> str:
    """Builds the output of a run that saved a fill or filled no meal.

    Args:
        context: The language and the data folder.
        week: The week.
        path: The menu file.
        tag: The tag of ``--tag``, or ``None``.
        counts: The numbers that the output reports.

    Returns:
        The lines of the table of the output, each ended by a line break.
    """
    first = _first_line(week, tag, counts.empty, counts.filled)
    lines = [_head(context, first, counts.kept)]
    if counts.filled < counts.empty:
        missing = counts.empty - counts.filled
        lines.append(_reason(context, tag, missing, counts.candidates_left))
    else:
        lines.append(RUN_SHOW.render(context.lang, week=str(week)))
        if counts.kept == 0:
            lines.insert(1, NO_TWICE.render(context.lang))
            lines.append(_swap_hint(context, week, path))
    return "".join(f"{line}\n" for line in lines)


def cannot_fill(context: Context, path: Path) -> str:
    """Builds the three lines of the refusal for a file that cannot be filled.

    Args:
        context: The language and the data folder.
        path: The menu file.

    Returns:
        The file relative to the data folder, the message after two spaces, and
        ``CHANGED_NOTHING``, each ended by a line break.
    """
    problem = Problem.error(context.folder.relative(path), None, CANNOT_FILL)
    where, what = problem_lines(problem, context.lang)
    return f"{where}\n  {what}\n{CHANGED_NOTHING.render(context.lang)}\n"


def failure_output(context: Context, creation: FileCreation) -> str:
    """Builds the three lines of a failed save.

    Args:
        context: The language.
        creation: What ``replace_file`` gave, with ``FAILED``.

    Returns:
        The file relative to the data folder as the problem holds it, the problem's text after
        two spaces, and ``CHANGED_NOTHING`` or ``LEFT_BEHIND`` with the full path of the
        temporary file, each ended by a line break.
    """
    # FAILED always holds a problem.
    problem = cast(Problem, creation.problem)
    lang = context.lang
    if creation.left:
        last = LEFT_BEHIND.render(lang, file=str(creation.left[0]))
    else:
        last = CHANGED_NOTHING.render(lang)
    lines = (str(problem.file), f"  {problem.text(lang)}", last)
    return "".join(f"{line}\n" for line in lines)
