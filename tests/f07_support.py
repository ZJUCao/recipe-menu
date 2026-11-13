"""Helpers and expected reports that the F07 tests share.

Nothing here calls an interface of ``check`` when the module is imported. At import the module
holds only texts, numbers, and tuples of them. Functions call ``main`` and read the folders.

``report`` writes the lines of the report of design 2.2 from the ``Prob`` values of
``f07_texts``, and ``rep`` gives them as the result of a call.
"""

import io
from collections.abc import Mapping, Sequence
from pathlib import Path

from f05_support import TODAY
from f07_texts import EN, ZH, Prob, Result
from recipe_menu.app import Command, problem_lines
from recipe_menu.catalog import read_catalog, read_pantry
from recipe_menu.cli import main
from recipe_menu.datafile import DataFolder, Problem, Severity
from recipe_menu.lang import Lang
from recipe_menu.menus import list_menu_weeks, read_week_menu
from recipe_menu.recipes import list_recipe_ids, read_recipes
from recipe_menu.settings import read_settings

# ---------------------------------------------------------------- the report of 2.2


def _count_line(recipes: int, weeks: int, lang: Lang) -> str:
    """Writes the count line of the report."""
    if lang is ZH:
        return f"已检查设置、目录、常备清单、{recipes} 个菜谱和 {weeks} 个周菜单。"
    recipe = "recipe" if recipes == 1 else "recipes"
    week = "week menu" if weeks == 1 else "week menus"
    return f"Checked the settings, the catalog, the pantry, {recipes} {recipe}, and {weeks} {week}."


def _heading(count: int, kind: str, lang: Lang) -> str:
    """Writes the heading of a block: ``kind`` is ``error`` or ``warning``."""
    if lang is ZH:
        return f"{count} 个{'错误' if kind == 'error' else '警告'}："
    return f"{count} {kind}{'' if count == 1 else 's'}:"


def report_of(
    recipes: int,
    weeks: int,
    errors: Sequence[tuple[str, str]],
    warnings: Sequence[tuple[str, str]],
    lang: Lang,
) -> list[str]:
    """Writes the lines of the report of design 2.2 from the ``(where, what)`` of each problem."""
    zh = lang is ZH
    lines = [_count_line(recipes, weeks, lang), ""]
    if errors:
        lines.append(_heading(len(errors), "error", lang))
        lines.extend(_two_lines(errors))
    elif warnings:
        lines.append("没有错误。" if zh else "No errors.")
    else:
        lines.append("没有错误，也没有警告。" if zh else "No errors. No warnings.")
    if warnings:
        lines += ["", _heading(len(warnings), "warning", lang), *_two_lines(warnings)]
    if errors:
        lines += ["", FIX_ZH if zh else FIX]
    return lines


def _two_lines(problems: Sequence[tuple[str, str]]) -> list[str]:
    """Writes the two lines of each problem, indented by 2 and by 4 spaces."""
    return [line for where, what in problems for line in (f"  {where}", f"    {what}")]


def _pairs(problems: Sequence[Prob], lang: Lang) -> list[tuple[str, str]]:
    """Gives the ``(where, what)`` of each problem, with the system's separator."""
    index = 1 if lang is ZH else 0
    pairs = []
    for problem in problems:
        where = str(Path(*problem.file.split("/")))
        if problem.place is not None:
            where += ("，" if lang is ZH else ", ") + problem.place[index]
        pairs.append((where, problem.msg[index]))
    return pairs


def report(
    recipes: int,
    weeks: int,
    errors: Sequence[Prob],
    warnings: Sequence[Prob],
    lang: Lang = EN,
) -> list[str]:
    """Gives the lines of ``R(r, w, E, W)`` of the test plan in a language."""
    return report_of(recipes, weeks, _pairs(errors, lang), _pairs(warnings, lang), lang)


def lines_text(lines: Sequence[str]) -> str:
    """Gives the lines of a report, each followed by a line break."""
    return "".join(f"{line}\n" for line in lines)


def expect(code: int, lines: Sequence[str]) -> Result:
    """Gives ``(c, L)`` of the test plan: the code, the lines on stdout, and an empty stderr."""
    return code, lines_text(lines), ""


def rep(  # noqa: PLR0917 - the six values of the test plan's `R`, in its order
    code: int,
    recipes: int,
    weeks: int,
    errors: Sequence[Prob],
    warnings: Sequence[Prob],
    lang: Lang = EN,
) -> Result:
    """Gives the result of a call whose report is ``R(r, w, E, W)`` in a language."""
    return expect(code, report(recipes, weeks, errors, warnings, lang))


COUNTS = "Checked the settings, the catalog, the pantry, 7 recipes, and 1 week menu."
COUNTS_ZH = "已检查设置、目录、常备清单、7 个菜谱和 1 个周菜单。"
FIX = 'Fix the errors and run "recipe-menu check" again.'
FIX_ZH = "改正错误后，再运行“recipe-menu check”。"


_PORK_FILE = str(Path("recipes", "red-braised-pork.toml"))
_MAPO_FILE = str(Path("recipes", "mapo-tofu.toml"))
_WEEK_FILE = str(Path("menus", "2026-W47.toml"))
_MAPO_UNKNOWN = (
    '    Unknown ingredient "豆瓣酱". Add it to the catalog, or use its name in the catalog.'
)

AFTER = [
    COUNTS,
    "",
    "No errors.",
    "",
    "1 warning:",
    f"  {_PORK_FILE}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
]
AFTER_ZH = [
    COUNTS_ZH,
    "",
    "没有错误。",
    "",
    "1 个警告：",
    f"  {_PORK_FILE}，步骤",
    "    没有英文步骤。命令会改为显示中文步骤。",
]
TWO = [
    COUNTS,
    "",
    "2 errors:",
    f"  {_MAPO_FILE}, ingredient 3",
    _MAPO_UNKNOWN,
    f"  {_WEEK_FILE}, Monday dinner",
    '    Unknown recipe "tomato-eggs".',
    "",
    "1 warning:",
    f"  {_PORK_FILE}, steps",
    "    No English steps. Commands show the Chinese steps instead.",
    "",
    FIX,
]
TWO_ZH = [
    COUNTS_ZH,
    "",
    "2 个错误：",
    f"  {_MAPO_FILE}，食材 3",
    "    未知食材“豆瓣酱”。请把它加入目录，或改用目录里的名称。",
    f"  {_WEEK_FILE}，周一晚餐",
    "    未知菜谱“tomato-eggs”。",
    "",
    "1 个警告：",
    f"  {_PORK_FILE}，步骤",
    "    没有英文步骤。命令会改为显示中文步骤。",
    "",
    FIX_ZH,
]
EMPTY = [
    "Checked the settings, the catalog, the pantry, 0 recipes, and 0 week menus.",
    "",
    "5 errors:",
    "  settings.toml",
    "    The file is missing.",
    "  catalog.toml",
    "    The file is missing.",
    "  pantry.toml",
    "    The file is missing.",
    "  recipes",
    "    The folder is missing.",
    "  menus",
    "    The folder is missing.",
    "",
    FIX,
]
EMPTY_ZH = [
    "已检查设置、目录、常备清单、0 个菜谱和 0 个周菜单。",
    "",
    "5 个错误：",
    "  settings.toml",
    "    文件不存在。",
    "  catalog.toml",
    "    文件不存在。",
    "  pantry.toml",
    "    文件不存在。",
    "  recipes",
    "    文件夹不存在。",
    "  menus",
    "    文件夹不存在。",
    "",
    FIX_ZH,
]

# ---------------------------------------------------------------- calling main


def call(
    home: Path,
    argv: Sequence[str],
    environ: Mapping[str, str] | None = None,
    commands: Sequence[Command] | None = None,
) -> Result:
    """Runs ``main`` as the test plan's conventions say and gives ``(code, out, err)``.

    It passes ``home``, ``environ`` (``{}`` when ``None``), and the date of ``TODAY``. With no
    ``commands``, ``main`` uses the real ``COMMANDS``.
    """
    out, err = io.StringIO(), io.StringIO()
    code = main(
        list(argv),
        environ={} if environ is None else environ,
        home=home,
        today=TODAY,
        stdout=out,
        stderr=err,
        commands=commands,
    )
    return code, out.getvalue(), err.getvalue()


def check(
    home: Path,
    folder: Path | None,
    *argv: str,
    environ: Mapping[str, str] | None = None,
) -> Result:
    """Runs ``check`` with the arguments in a folder, or with no ``--data`` when it is ``None``."""
    full = ["check", *argv]
    if folder is not None:
        full += ["--data", str(folder)]
    return call(home, full, environ)


# ---------------------------------------------------------------- the record of F07-T22


def snapshot(root: Path) -> dict[str, tuple[bytes | None, int]]:
    """Records the relative path, the bytes, and ``st_mtime_ns`` of every file and folder.

    A folder is recorded with ``None`` in place of its bytes.
    """
    return {
        path.relative_to(root).as_posix(): (
            None if path.is_dir() else path.read_bytes(),
            path.stat().st_mtime_ns,
        )
        for path in sorted(root.rglob("*"))
    }


# ---------------------------------------------------------------- the expected report of T24


def expected_report(root: Path, lang_option: str | None) -> Result:
    """Gives the result that ``check`` must give on a folder, from the readers alone.

    It follows the seven steps of design 2.2 with the readers of F03 to F06, and writes the
    report from ``problem_lines``. The problems of the recipes (steps 4 and 5) come from
    ``read_recipes`` with the catalog, as the test plan's Expected says (choice 3), and
    ``list_recipe_ids`` gives only the count and the set of IDs. The problems of
    ``read_recipes`` already hold those of ``list_recipe_ids``.
    The language is ``lang_option`` when given, else the language of the settings, else English.

    Args:
        root: The data folder.
        lang_option: ``"en"`` or ``"zh"`` for ``--lang``, or ``None`` for no ``--lang``.
    """
    folder = DataFolder(root)
    settings, problems = read_settings(folder)
    catalog, found = read_catalog(folder)
    problems += found
    problems += read_pantry(folder, catalog)[1]
    ids = list_recipe_ids(folder)[0]
    problems += read_recipes(folder, catalog)[1]
    weeks, found = list_menu_weeks(folder)
    problems += found
    id_set = frozenset(ids)
    for week in weeks:
        problems += read_week_menu(folder, week, settings, id_set)[1]
    if lang_option is not None:
        lang = Lang(lang_option)
    else:
        lang = settings.language if settings is not None and settings.language else EN
    errors, warnings = _split(problems, lang)
    lines = report_of(len(ids), len(weeks), errors, warnings, lang)
    return expect(1 if errors else 0, lines)


def _split(
    problems: Sequence[Problem], lang: Lang
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Splits problems into the ``(where, what)`` of the errors and of the warnings."""
    errors = [problem_lines(p, lang) for p in problems if p.severity is Severity.ERROR]
    warnings = [problem_lines(p, lang) for p in problems if p.severity is Severity.WARNING]
    return errors, warnings
