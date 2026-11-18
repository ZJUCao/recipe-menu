"""Tests of F14 on random weeks and random settings, checked with the rules of the plan (T33)."""

import random
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from f03_support import put_bytes, write
from f05_support import make_home
from f05_texts import lines_text
from f09_support import made
from f09_texts import out
from f13_support import pristine
from f14_support import (
    DAYS,
    IN_ZH,
    BackSource,
    dish_list,
    picks,
    seeded,
    stamp,
    suggest,
    suggest_folder,
    week_line,
)
from f14_texts import outcome
from recipe_menu.datafile import DataFolder
from recipe_menu.menus import Dish, IsoWeek, read_week_menu
from recipe_menu.settings import Meal, Settings

SEED = 20261117
FOLDERS = 100
WEEK = "2026-W48"
TAGS = (("quick", "快手"), ("home-style", "家常"), ("vegetarian", "素"), ("spicy", "辣"))
TAGS += (("staple", "主食"),)
EMPTY_FORMS = ("{m}=[]", "{m} = [ ]  # nothing yet", '"{m}" = []', "\t'{m}'\t=\t[\t]")
KEPT_FORMS = ("{m} = {items}", "{m} = {items}  # kept", '"{m}" = {items}')
HEADERS = ("[{d}]", '["{d}"]', "[ '{d}' ]  # guests", "[{d}]  # busy", "[ {d} ]")
FILLERS = ("# a note", "", "# plan below", "  # indented")
BRACKETS = re.compile(r"\[[ \t]*\]")

type Key = tuple[str, Meal]


@dataclass
class Item:
    """One line of the table of a day.

    Attributes:
        text: The line.
        meal: The meal of an empty line, or ``None`` for any other line.
    """

    text: str
    meal: Meal | None = None


@dataclass
class DayTable:
    """The table of a day that the file writes.

    Attributes:
        header: The header line.
        items: The lines after the header, in order.
        missing: The meals of the settings that the table leaves out, in the settings' order.
    """

    header: str
    items: list[Item] = field(default_factory=list)
    missing: list[Meal] = field(default_factory=list)


@dataclass
class Layout:
    """A random week: the settings, the lines of the file, and what each meal holds.

    Attributes:
        meals: The meals of the settings, in order.
        table: The number of dishes of the meals that the table of the settings names.
        top: The lines before the first header.
        days: The tables of the days that the file writes.
        empties: The empty meals, in the order of the slots.
    """

    meals: list[Meal]
    table: dict[Meal, int]
    top: list[str]
    days: dict[str, DayTable] = field(default_factory=dict)
    empties: list[Key] = field(default_factory=list)

    def dishes_for(self, meal: Meal) -> int:
        """Gives the number of dishes of a meal."""
        return self.table.get(meal, 1)

    def settings(self) -> Settings:
        """Gives the ``Settings`` that the settings file of the layout reads as."""
        return Settings(None, tuple(self.meals), 2, tuple(self.dishes_for(m) for m in Meal))


def _fillers(rng: random.Random, chance: float) -> list[str]:
    """Gives no lines, or one or two lines of a comment or a blank, by chance."""
    if rng.random() >= chance:
        return []
    return [rng.choice(FILLERS) for _ in range(rng.randint(1, 2))]


def _day_table(rng: random.Random, layout: Layout, day: str, ids: list[str]) -> DayTable:
    """Builds the table of a day: a header, and for each meal no line, an empty line, or dishes.

    It adds the empty meals of the day to ``layout.empties``.
    """
    table = DayTable(rng.choice(HEADERS).format(d=day))
    for meal in layout.meals:
        state = rng.choice(("missing", "empty", "empty", "kept", "kept"))
        if state == "missing":
            table.missing.append(meal)
            layout.empties.append((day, meal))
            continue
        table.items += [Item(line) for line in _fillers(rng, 0.3)]
        if state == "empty":
            table.items.append(Item(rng.choice(EMPTY_FORMS).format(m=meal.value), meal))
            layout.empties.append((day, meal))
        else:
            items = dish_list([rng.choice(ids) for _ in range(rng.randint(1, 3))])
            table.items.append(Item(rng.choice(KEPT_FORMS).format(m=meal.value, items=items)))
    return table


def _build(rng: random.Random, ids: list[str]) -> Layout:
    """Builds a random layout: 1 to 3 meals, a table of dishes or none, and a random week."""
    meals = sorted(rng.sample(list(Meal), rng.randint(1, 3)), key=list(Meal).index)
    numbers = {meal: rng.randint(1, 3) for meal in meals if rng.random() < 0.6}
    layout = Layout(meals, numbers if rng.random() < 0.7 else {}, [])
    layout.top = [*_fillers(rng, 0.3), f'week = "{WEEK}"']
    for day in DAYS:
        if rng.random() < 0.25:
            layout.empties += [(day, meal) for meal in meals]
        else:
            layout.days[day] = _day_table(rng, layout, day, ids)
    return layout


def _text(layout: Layout) -> str:
    """Gives the text of the menu file of a layout."""
    lines = list(layout.top)
    for table in layout.days.values():
        lines += [table.header, *(item.text for item in table.items)]
    return lines_text(*lines)


def _expected(layout: Layout, fills: dict[Key, list[str]]) -> str:
    """Gives the text after a run: each filled meal gets its list, and the rules add its lines."""
    lines = list(layout.top)
    for day, table in layout.days.items():
        lines.append(table.header)
        lines += [
            f"{m.value} = {dish_list(fills[day, m])}" for m in table.missing if (day, m) in fills
        ]
        for item in table.items:
            if item.meal is not None and (day, item.meal) in fills:
                lines.append(BRACKETS.sub(dish_list(fills[day, item.meal]), item.text, count=1))
            else:
                lines.append(item.text)
    for day in DAYS:
        added = [
            f"{m.value} = {dish_list(fills[day, m])}" for m in layout.meals if (day, m) in fills
        ]
        if day not in layout.days and added:
            lines += ["", f"[{day}]", *added]
    return lines_text(*lines)


def _assign(layout: Layout, chosen: list[str]) -> dict[Key, list[str]]:
    """Walks the empty meals in order: a meal takes dishes from the front when enough are left."""
    left = list(chosen)
    fills: dict[Key, list[str]] = {}
    for day, meal in layout.empties:
        count = layout.dishes_for(meal)
        if count <= len(left):
            fills[day, meal] = left[:count]
            del left[:count]
    return fills


def _candidates(root: Path, ids: list[str], held: set[str], tag: str | None) -> list[str]:
    """Gives the IDs that no dish names, in ID order, with the tag when it is given."""
    found = [recipe_id for recipe_id in ids if recipe_id not in held]
    if tag is None:
        return found
    texts = {i: (root / "recipes" / f"{i}.toml").read_text(encoding="utf-8") for i in found}
    return [i for i in found if tag in tomllib.loads(texts[i])["tags"]]


def _write_folder(layout: Layout, root: Path) -> None:
    """Writes the settings and the menu file of a layout."""
    names = ", ".join(f'"{meal.value}"' for meal in layout.meals)
    lines = [f"meals = [{names}]"]
    if layout.table:
        pairs = ", ".join(f"{meal.value} = {number}" for meal, number in layout.table.items())
        lines.append(f"dishes = {{ {pairs} }}")
    write(root / "settings.toml", lines_text(*lines))
    write(root / "menus" / f"{WEEK}.toml", _text(layout))


def _slots(folder: DataFolder, layout: Layout, ids: list[str]) -> dict[Key, tuple[Dish, ...]]:
    """Reads the week and gives the dishes of each slot. The reader finds no problem."""
    menu, problems = read_week_menu(folder, IsoWeek(2026, 48), layout.settings(), frozenset(ids))
    assert problems == ()
    assert menu is not None
    return {(slot.day.value, slot.meal): slot.dishes for slot in menu.slots}


@dataclass
class Case:
    """The choices of one folder: its tag, its language, and the seed of the first run.

    Attributes:
        tag: The English and the Chinese name of the tag, or ``None``.
        by: The name of the tag that the line gives.
        zh: Whether the output is in Chinese.
        seed: The seed of the first run.
    """

    tag: tuple[str, str] | None
    by: str | None
    zh: bool
    seed: int


def _check_run(  # noqa: PLR0917 - the values of one run
    home: Path, root: Path, layout: Layout, ids: list[str], case: Case, back: bool
) -> None:
    """Runs the line once on the file of the layout, and checks the properties of the plan.

    The file gets its old bytes back at the end, for the next run.
    """
    folder = DataFolder(root)
    file = folder.menu_file(WEEK)
    old = _slots(folder, layout, ids)
    assert [key for key, dishes in old.items() if not dishes] == layout.empties
    held = {dish.recipe_id for dishes in old.values() for dish in dishes}
    pool = _candidates(root, ids, held, None if case.tag is None else case.tag[1])
    count = min(sum(layout.dishes_for(meal) for _, meal in layout.empties), len(pool))
    if back:
        source: random.Random = BackSource()
        chosen = pool[::-1][:count]
    else:
        source = seeded(case.seed)
        chosen = picks(case.seed, pool, count)
    fills = _assign(layout, chosen)
    before = stamp(file)
    rest = [*([] if case.by is None else ["--tag", case.by]), *(IN_ZH if case.zh else ())]
    result = suggest(home, folder, *week_line(WEEK, *rest), random=source)
    used = sum(len(items) for items in fills.values())
    why = "left" if len(pool) == used else "few"
    kept = len(old) - len(layout.empties)
    lines = outcome(WEEK, len(layout.empties), len(fills), kept, why, case.tag, case.zh)
    assert result == out(lines), (root, rest)
    if isinstance(source, BackSource):
        assert source.calls == ([(pool, count)] if layout.empties else [])
    _check_file(folder, layout, ids, old, fills, pool, before)
    put_bytes(file, before[0])


def _check_file(  # noqa: PLR0917 - the values that one run gives
    folder: DataFolder,
    layout: Layout,
    ids: list[str],
    old: dict[Key, tuple[Dish, ...]],
    fills: dict[Key, list[str]],
    pool: list[str],
    before: tuple[bytes, int],
) -> None:
    """Checks the file after a run: the dishes of each meal, the new recipes, and the text."""
    file = folder.menu_file(WEEK)
    new = _slots(folder, layout, ids)
    for key, dishes in old.items():
        want = dishes if dishes else tuple(Dish(item, 2) for item in fills.get(key, []))
        assert new[key] == want, (file, key)
    added = [dish.recipe_id for key in layout.empties for dish in new[key]]
    assert len(set(added)) == len(added)
    assert set(added) <= set(pool)
    if not fills:
        assert stamp(file) == before
    else:
        assert file.read_text(encoding="utf-8") == _expected(layout, fills), file


def _one_folder(rng: random.Random, home: Path, root: Path) -> None:
    """Builds a random layout in a folder, and runs the line with a seeded and a back source."""
    ids = sorted(path.stem for path in (root / "recipes").glob("*.toml"))
    layout = _build(rng, ids)
    _write_folder(layout, root)
    tag = rng.choice(TAGS) if rng.random() < 0.5 else None
    by = None if tag is None else rng.choice(tag)
    case = Case(tag, by, rng.random() < 1 / 3, rng.randrange(1000))
    _check_run(home, root, layout, ids, case, back=False)
    _check_run(home, root, layout, ids, case, back=True)


def test_f14_t33_random_weeks_keep_what_the_rules_keep_and_fill_what_they_fill(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """A hundred random folders: the settings, the layout, the tag, the language, and the source."""
    home = make_home(tmp_path)
    base = pristine(example_folder, tmp_path)
    rng = seeded(SEED)
    for number in range(FOLDERS):
        if number % 4 == 0:
            root = suggest_folder(base, tmp_path, f"week-{number}")
        else:
            root = made(base, tmp_path, f"week-{number}")
        _one_folder(rng, home, root)
