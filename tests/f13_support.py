"""Helpers that the F13 tests share: the fault harness, the builders, and the named changes.

The module holds ``ShopFaults`` and ``shop_faults``, which add the rules ``move``, ``close``, and
``unlink P: later`` to the harness of ``f08_support``, the links and the messages of the system,
the builders ``shop_list``, ``shop_lines``, and ``shop_file``, which follow design 2.2 and use no
code of F13, and the named changes of the test plan. Nothing here calls an interface of F13 when
the module is imported: ``SHOP_COMMAND`` and ``replace_file`` are never called here, so the test
files import against the mock and against a broken implementation. The expected texts are in
``f13_texts`` and ``f13_blocks``.
"""

import builtins
import errno
import io
import os
import sys
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from f03_support import put_bytes, write
from f05_support import TODAY, copy_example
from f05_texts import Msg, Result
from f07_changes import edit
from f07_texts import NOT_A_WEEK_NAME, Prob, m_pantry_ingredient, p_item
from f08_support import Faults, Rule
from f08_texts import FILE_WRITE_DENIED, file_error
from f09_support import extra_recipes
from f11_support import menu_text, new_base, on
from f12_support import LUNCH_DINNER, read_week
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek
from recipe_menu.shopping import ShoppingList, build_shopping_list
from recipe_menu.text import comma_list, display_width, format_table

type Change = Callable[[Path], None]

EXISTS = partial(FileExistsError, errno.EEXIST, "File exists")

# ---------------------------------------------------------------- the records of the cases

READ_SETTINGS = "read settings.toml"
LISTINGS = ["recipes", "menus"]
TEMP_47 = "shopping/2026-W47.md.tmp"
W47 = [f"unlink {TEMP_47}", f"open {TEMP_47}", f"move {TEMP_47} shopping/2026-W47.md"]
R47_IDS = ("tomato-egg", "choy-sum", "rice", "mapo-tofu", "tomato-egg-noodles", "cola-wings")
R47 = [
    READ_SETTINGS,
    "read catalog.toml",
    "read pantry.toml",
    "read menus/2026-W47.toml",
    *[f"read recipes/{recipe_id}.toml" for recipe_id in R47_IDS],
]

# ---------------------------------------------------------------- the fault harness


class _CloseFile:
    """A file that closes for real and then raises when it is closed."""

    def __init__(self, real: Any, effect: Callable[[], BaseException]) -> None:
        """Wraps the real file that an ``open`` gave."""
        self._real = real
        self._effect = effect

    def __getattr__(self, name: str) -> Any:
        """Passes every other call to the real file."""
        return getattr(self._real, name)

    def __enter__(self) -> "_CloseFile":
        """Gives the wrapper, as a file does."""
        return self

    def close(self) -> None:
        """Closes the real file, and raises."""
        self._real.close()
        raise self._effect()

    def __exit__(self, kind: object, *rest: object) -> None:
        """Closes the real file, and raises unless another exception is on its way."""
        self._real.close()
        if kind is None:
            raise self._effect()


class ShopFaults(Faults):
    """The harness of F08 with the move, the close, and ``unlink P: later``.

    Attributes:
        calls: The calls in order, as in ``Faults``. A move is ``move A B``.
    """

    def __init__(self, base: Path, rules: Sequence[Rule]) -> None:
        """Takes the original ``os.replace`` as well."""
        super().__init__(base, rules)
        self._os["replace"] = os.replace
        self._later: dict[tuple[str, str], int] = {}

    def _run(self, kind: str, path: object, original: Callable[[], Any]) -> Any:
        """Records a call, and applies its rule. A ``later`` rule lets the first call run."""
        rel = self._rel(path)
        found = None if rel is None else self._find(kind, rel)
        if rel is None or found is None or found.how != "later":
            return super()._run(kind, path, original)
        self.calls.append(f"{kind} {rel}")
        count = self._later.get((kind, rel), 0)
        self._later[kind, rel] = count + 1
        if count == 0:
            return original()
        assert found.effect is not None
        raise found.effect()

    def replace(self, source: Any, target: Any, *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``os.replace``: records ``move A B``, and applies ``move A``."""
        rel = self._rel(source)
        if rel is None:
            return self._os["replace"](source, target, *args, **kwargs)
        self.calls.append(f"move {rel} {self._rel(target)}")
        found = self._find("move", rel)
        if found is not None:
            assert found.effect is not None
            assert found.how == "raise", found.how
            raise found.effect()
        return self._os["replace"](source, target, *args, **kwargs)

    def open(self, file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        """Stands in for ``io.open``, and wraps a file that a ``close`` rule names."""
        handle = super().open(file, mode, *args, **kwargs)
        rel = self._rel(file)
        found = self._find("close", rel) if rel is not None and "x" in mode else None
        if found is None or found.effect is None:
            return handle
        return _CloseFile(handle, found.effect)


@contextmanager
def shop_faults(base: Path, *rules: Rule) -> Iterator[ShopFaults]:
    """Replaces the calls of ``faults`` and ``os.replace`` while it is open.

    Args:
        base: The folder whose paths the harness records.
        *rules: The rules to apply.

    Yields:
        The ``ShopFaults`` with the record and the listings.
    """
    state = ShopFaults(base, rules)
    with pytest.MonkeyPatch.context() as patch:
        for name in ("mkdir", "rmdir", "unlink", "remove", "scandir", "listdir", "replace"):
            patch.setattr(os, name, getattr(state, name))
        patch.setattr(io, "open", state.open)
        patch.setattr(builtins, "open", state.open)
        yield state


# ---------------------------------------------------------------- links and system messages


def folder_link(path: Path, target: Path) -> None:
    """Makes ``path`` a link to the folder ``target``: a junction, or a symbolic link."""
    if sys.platform == "win32":
        import _winapi  # noqa: PLC0415 - exists on Windows only

        _winapi.CreateJunction(str(target), str(path))
    else:
        path.symlink_to(target, target_is_directory=True)
    assert path.is_dir()


def move_message(base: Path) -> Msg:
    """Gives the message of ``replace_file`` for a move of a file onto a folder.

    It moves a file of its own onto an empty folder of its own in ``base``, takes the row of the
    error table that the system's error gives, and removes both. Windows gives
    ``PermissionError``, and Linux gives ``IsADirectoryError`` with ``Is a directory``.
    """
    source, target = base / "move-source", base / "move-target"
    source.write_bytes(b"x")
    target.mkdir()
    try:
        source.replace(target)
    except PermissionError:
        message = FILE_WRITE_DENIED
    except OSError as error:
        message = file_error(error.strerror or type(error).__name__)
    else:
        raise AssertionError("the move onto a folder did not raise")
    finally:
        source.unlink()
        target.rmdir()
    return message


@contextmanager
def held_open(path: Path) -> Iterator[None]:
    """Holds a file open with ``open(path, "rb")``, as another program does."""
    with path.open("rb"):
        yield


def new_shop(tmp_path: Path, name: str) -> tuple[Path, DataFolder]:
    """Makes the empty ``base`` of a call and ``F`` on ``base/recipe-menu``, which exists."""
    base, folder = new_base(tmp_path, name)
    folder.root.mkdir()
    return base, folder


# ---------------------------------------------------------------- the builders of design 2.2


def shop_list(folder: DataFolder, week: IsoWeek) -> ShoppingList:
    """Reads the week with ``read_week`` and gives ``build_shopping_list`` of its values."""
    menu, recipes, catalog, pantry = read_week(folder, week, [])
    return build_shopping_list(menu, recipes, catalog, pantry)


def _counts(shopping: ShoppingList, lang: Lang) -> tuple[str, str]:
    """Gives the meals and the dishes of the list as the counts of the heading, in a language."""
    meals, dishes = shopping.meal_count, shopping.dish_count
    if lang is Lang.ZH:
        return f"{meals} 餐", f"{dishes} 道菜"
    return (
        f"{meals} meal{'' if meals == 1 else 's'}",
        f"{dishes} dish{'' if dishes == 1 else 'es'}",
    )


def _width(shopping: ShoppingList, lang: Lang) -> int:
    """Gives the largest display width of a line of a name of the whole list."""
    names = [line.ingredient.name.get(lang) for group in shopping.groups for line in group.lines]
    return max((display_width(part) for name in names for part in name.splitlines()), default=0)


def _pantry(shopping: ShoppingList, lang: Lang) -> str:
    """Gives the pantry line of a list."""
    items = comma_list(item.name for item in shopping.pantry_used).get(lang)
    head = (
        "常备，不用买：" if lang is Lang.ZH else "Not on the list, because they are in the pantry: "
    )
    return head + items


def shop_lines(shopping: ShoppingList, lang: Lang, path: Path | str) -> list[str]:
    """Gives the lines of the output of 2.2 for a list in a language, with the list file ``path``.

    They are the heading, an empty line, the groups, then an empty line and the pantry line when
    the menu uses a pantry ingredient, then an empty line and ``Saved P``.
    """
    zh = lang is Lang.ZH
    week, dates = str(shopping.week), shopping.week.date_range.get(lang)
    meals, dishes = _counts(shopping, lang)
    if zh:
        lines = [f"{week} 购物清单，{dates}：{meals}，{dishes}", ""]
    else:
        lines = [f"Shopping list for {week}, {dates}: {meals}, {dishes}", ""]
    width = _width(shopping, lang)
    for group in shopping.groups:
        lines.append(group.category.name.get(lang))
        rows = [(i.ingredient.name.get(lang), i.amount_text(lang)) for i in group.lines]
        lines.extend(format_table(rows, indent=2, min_widths=(width,)))
    if not shopping.groups:
        lines.append("没有要买的东西。" if zh else "There is nothing to buy.")
    if shopping.pantry_used:
        lines += ["", _pantry(shopping, lang)]
    return [*lines, "", f"已保存 {path}" if zh else f"Saved {path}"]


def shop_file(shopping: ShoppingList, lang: Lang) -> bytes:
    """Gives the bytes of the file of 2.2 for a list in a language, each line ended by LF."""
    zh = lang is Lang.ZH
    week, dates = str(shopping.week), shopping.week.date_range.get(lang)
    meals, dishes = _counts(shopping, lang)
    if zh:
        lines = [f"# {week} 购物清单", "", f"{dates}：{meals}，{dishes}。"]
    else:
        lines = [f"# Shopping list for {week}", "", f"{dates}: {meals}, {dishes}."]
    for group in shopping.groups:
        lines += ["", f"## {group.category.name.get(lang)}", ""]
        lines += [f"- [ ] {i.ingredient.name.get(lang)} {i.amount_text(lang)}" for i in group.lines]
    if not shopping.groups:
        lines += ["", "没有要买的东西。" if zh else "There is nothing to buy."]
    if shopping.pantry_used:
        lines += ["", _pantry(shopping, lang)]
    return "".join(f"{line}\n" for line in lines).encode("utf-8")


def pt01_shop(root: Path) -> Result:
    """Gives the result of ``shop 2026-W26`` on the PT01 folder: ``(0, out, "")``."""
    shopping = shop_list(DataFolder(root), IsoWeek(2026, 26))
    path = root / "shopping" / "2026-W26.md"
    lines = shop_lines(shopping, Lang.EN, path)
    return 0, "".join(f"{line}\n" for line in lines), ""


# ---------------------------------------------------------------- the named changes of F13


def rice_week(week: str) -> Change:
    """Gives the change that writes ``menus/<week>.toml`` with ``rice`` in its first dinner."""

    def change(root: Path) -> None:
        """Writes the rice week."""
        path = root / "menus" / f"{week}.toml"
        put_bytes(path, menu_text(week, LUNCH_DINNER))
        edit(path, "dinner = []", 'dinner = ["rice"]')

    return change


def water_week(root: Path) -> None:
    """Adds the extra recipes and ``menus/2026-W50.toml`` with ``water`` in Monday's lunch."""
    extra_recipes(root)
    write(
        root / "menus" / "2026-W50.toml",
        'week = "2026-W50"\n\n[monday]\nlunch = ["water"]\n',
    )


def egg_week(root: Path) -> None:
    """Adds the extra recipes, the egg to the pantry, and ``menus/2026-W51.toml``."""
    extra_recipes(root)
    edit(root / "pantry.toml", '"花椒"]', '"花椒", "鸡蛋"]')
    write(
        root / "menus" / "2026-W51.toml",
        'week = "2026-W51"\n\n[tuesday]\ndinner = ["water", "boiled-egg"]\n',
    )


def chicken_break(escape: str) -> Change:
    """Gives the change that puts the TOML escape ``escape`` into the chicken wings."""

    def change(root: Path) -> None:
        """Gives the English name of the chicken wings two lines."""
        edit(root / "catalog.toml", 'en = "Chicken wings"', f'en = "Chicken{escape}wings"')

    return change


def meat_break(root: Path) -> None:
    """Gives the English name of the meat category two lines, with a TOML escape."""
    edit(root / "catalog.toml", 'en = "Meat and seafood"', 'en = "Meat\\nand seafood"')


def missing_name(root: Path) -> None:
    """Deletes the English name of the cola in the catalog."""
    old = '{ zh = "可乐", en = "Cola", category = "other", unit = "罐" }'
    edit(root / "catalog.toml", old, '{ zh = "可乐", category = "other", unit = "罐" }')


def shopping_as_file(root: Path) -> None:
    """Writes the file ``shopping`` with one line of text."""
    put_bytes(root / "shopping", b"x\n")


def empty_shopping(root: Path) -> None:
    """Makes the empty folder ``shopping/``."""
    (root / "shopping").mkdir()


def ticked_list(root: Path) -> None:
    """Writes ``shopping/2026-W47.md`` with one ticked line."""
    write(root / "shopping" / "2026-W47.md", "# 2026-W47 购物清单\n\n- [x] 番茄 600 g\n")


def old_list(root: Path) -> None:
    """Writes ``shopping/2026-W47.md`` with the text ``old``."""
    put_bytes(root / "shopping" / "2026-W47.md", b"old\n")


def old_temp(root: Path) -> None:
    """Writes ``shopping/2026-W47.md.tmp`` with the text ``half``."""
    put_bytes(root / "shopping" / "2026-W47.md.tmp", b"half\n")


def no_pantry(root: Path) -> None:
    """Deletes ``pantry.toml``."""
    (root / "pantry.toml").unlink()


def empty_menu_file(name: str) -> Change:
    """Gives the change that writes the empty file ``menus/<name>``."""
    return lambda root: write(root / "menus" / name, "")


# ---------------------------------------------------------------- problems of the readers

E_PANTRY = Prob("pantry.toml", p_item(3), m_pantry_ingredient("sesame oil"))
E_LOWER_48 = Prob("menus/2026-w48.toml", None, NOT_A_WEEK_NAME)


def traced(
    home: Path, root: Path, *argv: str, today: date = TODAY
) -> tuple[Result, list[str], list[str]]:
    """Runs ``main`` on a date in a folder inside the harness, and gives the result and the record.

    Args:
        home: The home folder.
        root: The data folder.
        *argv: The command line before ``--data``.
        today: The date that ``main`` gets as today.

    Returns:
        The result, the calls that the harness recorded, and its listings.
    """
    with shop_faults(root) as state:
        result = on(home, root, today, *argv)
    return result, state.calls, state.listings


def pristine(example: DataFolder, tmp_path: Path) -> DataFolder:
    """Copies the example folder at its start, for the new examples that a case makes later.

    A case that runs ``shop`` in ``example`` writes ``shopping/`` there, and a copy made after it
    would hold that folder. The new examples of such a case are copies of this one.
    """
    return DataFolder(copy_example(example, tmp_path / "pristine"))
