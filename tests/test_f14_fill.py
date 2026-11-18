"""Tests of F14 for what menu suggest fills: the prototypes, v0.2-S05, and the forms (T03-T09)."""

from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from f03_support import write
from f05_support import copy_example, make_home
from f07_changes import append, edit, mapo_mistake
from f07_support import check, expect
from f09_support import at, made
from f09_texts import err, out
from f10_support import chinese_settings
from f11_texts import DATES, new, no_menu, not_a_week
from f13_support import LISTINGS, READ_SETTINGS, Change, pristine
from f14_support import (
    AFTER_40,
    DINNER,
    EVERY_MEAL,
    EXAMPLE_IDS,
    IN_ZH,
    LUNCH_DINNER,
    QUICK_IDS,
    READ_CATALOG,
    SPICY_IDS,
    SUGGEST_IDS,
    W47,
    WEEK_48,
    BackSource,
    FrontSource,
    Source,
    dinners,
    filled,
    menu_as,
    new_menu,
    one_each,
    picks,
    seeded,
    stamp,
    suggest,
    suggest_folder,
    traced,
    w47_filled,
    week_line,
    with_dishes,
    with_meals,
)
from f14_texts import (
    SHOW_47_FILLED,
    cannot,
    first,
    first_zh,
    full,
    full_zh,
    refill,
    refill_zh,
    some,
    some_zh,
    tags,
)
from recipe_menu.datafile import DataFolder
from recipe_menu.settings import Meal


def _run(home: Path, folder: DataFolder, *argv: str) -> tuple[int, str, str]:
    """Runs the example's ``run``: ``main`` with a new ``seeded(3)``."""
    return suggest(home, folder, *argv, random=seeded(3))


def _check_week_47(home: Path, example: DataFolder) -> None:
    """The first two runs of the example of 2.2: v0.2-S05, and a run that fills no meal."""
    week47 = example.menu_file(W47)
    before = week47.read_text(encoding="utf-8").splitlines()
    assert _run(home, example, *week_line(W47)) == out(some(W47, 1, 10, 4, "left"))
    after = week47.read_text(encoding="utf-8").splitlines()
    changed = [(old, new) for old, new in zip(before, after, strict=True) if old != new]
    assert changed == [("lunch = []", 'lunch = ["red-braised-pork"]')]
    assert after[3:5] == ["[monday]", 'lunch = ["red-braised-pork"]']
    made_at = week47.stat().st_mtime_ns
    assert _run(home, example, *week_line(W47)) == out(some(W47, 0, 9, 5, "left"))
    assert week47.stat().st_mtime_ns == made_at


def _check_stops(home: Path, example: DataFolder) -> None:
    """The runs of the example for an unknown tag, a week with no menu, and a wrong week."""
    assert _run(home, example, *week_line(W47, "--tag", "breakfast")) == err(1, [tags("breakfast")])
    assert _run(home, example, *week_line(WEEK_48)) == err(1, [no_menu(WEEK_48)])
    assert _run(home, example, *week_line("2026-W99")) == err(2, [not_a_week("2026-W99")])


def _check_new_lines_and_tables(home: Path, example: DataFolder) -> None:
    """The run of the example for a file that leaves out a meal and six days."""
    week48 = example.menu_file(WEEK_48)
    write(week48, 'week = "2026-W48"\n\n[monday]\ndinner = []  # leftovers\n')
    a, b, c, d, e, f, g = picks(3, EXAMPLE_IDS, 7)
    assert _run(home, example, *week_line(WEEK_48)) == out(some(WEEK_48, 7, 14, 0, "left"))
    assert week48.read_text(encoding="utf-8").splitlines() == [
        'week = "2026-W48"',
        "",
        "[monday]",
        f'lunch = ["{a}"]',
        f'dinner = ["{b}"]  # leftovers',
        "",
        "[tuesday]",
        f'lunch = ["{c}"]',
        f'dinner = ["{d}"]',
        "",
        "[wednesday]",
        f'lunch = ["{e}"]',
        f'dinner = ["{f}"]',
        "",
        "[thursday]",
        f'lunch = ["{g}"]',
    ]


def _check_refusal_and_dishes(home: Path, example: DataFolder) -> None:
    """The runs of the example for a day in braces, and for dinners of 2 dishes."""
    week49 = example.menu_file("2026-W49")
    inline = 'week = "2026-W49"\nmonday = { lunch = [], dinner = [] }\n'
    write(week49, inline)
    assert _run(home, example, *week_line("2026-W49")) == err(1, cannot("2026-W49"))
    assert week49.read_text(encoding="utf-8") == inline
    settings = example.settings
    edit(settings, '["lunch", "dinner"]', '["dinner"]')
    append(settings, "dishes = { dinner = 2 }\n")
    assert at(home, example, "menu", "new", "2026-W50")[0] == 0
    assert _run(home, example, *week_line("2026-W50")) == out(some("2026-W50", 3, 7, 0, "few"))


def test_f14_t03_the_example_of_the_command_runs_with_the_real_commands(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The example of 2.2, in order, with ``seeded(3)`` for each run."""
    home = make_home(tmp_path)
    _check_week_47(home, example_folder)
    _check_stops(home, example_folder)
    _check_new_lines_and_tables(home, example_folder)
    _check_refusal_and_dishes(home, example_folder)


def _new_week(home: Path, folder: DataFolder, week: str) -> Path:
    """Runs ``menu new`` for a week, and gives the path of its file."""
    path = folder.menu_file(week)
    result = at(home, folder, "menu", "new", week)
    assert result == out(new(path, DATES[week][0], "lunch and dinner"))
    return path


def test_f14_t04_a_first_fill_with_a_tag_gives_one_recipe_with_the_tag_to_each_meal(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype "Fill an empty week", v0.2-S01 and v0.2-S02: a tag in either name."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    r = DataFolder(suggest_folder(source, tmp_path, "r"))
    path = _new_week(home, r, WEEK_48)
    result = suggest(home, r, *week_line(WEEK_48, "--tag", "quick"), random=seeded(5))
    assert result == out(first(WEEK_48, 14, "quick"))
    expected = filled(WEEK_48, LUNCH_DINNER, one_each(picks(5, QUICK_IDS, 14)))
    assert path.read_bytes() == expected
    shown = at(home, r, "menu", "show", WEEK_48)
    assert (shown[0], shown[2]) == (0, "")
    assert shown[1].splitlines()[-1] == "14 meals, 14 dishes. \u00d7n: servings."
    assert check(home, r.root) == expect(0, AFTER_40)
    r2 = DataFolder(suggest_folder(source, tmp_path, "r2"))
    path2 = _new_week(home, r2, WEEK_48)
    result = suggest(home, r2, *week_line(WEEK_48, "--tag", "快手"), random=seeded(5))
    assert result == out(first(WEEK_48, 14, "quick"))
    assert path2.read_bytes() == expected
    r3 = DataFolder(suggest_folder(source, tmp_path, "r3"))
    path3 = _new_week(home, r3, WEEK_48)
    result = suggest(home, r3, *week_line(WEEK_48, "--tag", "quick", *IN_ZH), random=seeded(6))
    assert result == out(first_zh(WEEK_48, 14, "快手"))
    assert path3.read_bytes() == filled(WEEK_48, LUNCH_DINNER, one_each(picks(6, QUICK_IDS, 14)))


def test_f14_t05_a_swap_fills_the_one_emptied_meal_and_a_full_week_changes_nothing(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype "Swap one dish" and v0.2-S03: the removed recipe is a candidate again."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    r = DataFolder(suggest_folder(source, tmp_path, "r"))
    _new_week(home, r, WEEK_48)
    result = suggest(home, r, *week_line(WEEK_48, "--tag", "quick"), random=seeded(5))
    assert result == out(first(WEEK_48, 14, "quick"))
    chosen = picks(5, QUICK_IDS, 14)
    file = r.menu_file(WEEK_48)
    edit(file, f'dinner = ["{chosen[5]}"]', "dinner = []")
    r2 = DataFolder(copy_example(r, tmp_path / "r2"))
    before = file.read_bytes()
    held = set(chosen) - {chosen[5]}
    candidates = [recipe_id for recipe_id in SUGGEST_IDS if recipe_id not in held]
    assert len(candidates) == 27
    s = FrontSource()
    assert suggest(home, r, *week_line(WEEK_48, *IN_ZH), random=s) == out(refill_zh(WEEK_48, 1, 13))
    assert s.calls == [(candidates, 1)]
    assert chosen[5] in candidates
    new_dish = f'dinner = ["{candidates[0]}"]'
    assert file.read_bytes() == before.replace(b"dinner = []", new_dish.encode("utf-8"), 1)
    stamped = stamp(file)
    s1, s2 = FrontSource(), FrontSource()
    assert suggest(home, r, *week_line(WEEK_48), random=s1) == out(full(WEEK_48))
    assert suggest(home, r, *week_line(WEEK_48, *IN_ZH), random=s2) == out(full_zh(WEEK_48))
    assert (s1.calls, s2.calls) == ([], [])
    assert stamp(file) == stamped
    assert suggest(home, r2, *week_line(WEEK_48)) == out(refill(WEEK_48, 1, 13))


def test_f14_t06_every_candidate_goes_into_a_meal_and_the_rest_of_the_week_stays_empty(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The prototype "Not enough recipes" and v0.2-S04: three recipes with the tag spicy."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    r = DataFolder(suggest_folder(source, tmp_path, "r"))
    week = "2026-W49"
    path = _new_week(home, r, week)
    result = suggest(home, r, *week_line(week, "--tag", "spicy"), random=seeded(8))
    assert result == out(some(week, 3, 14, 0, "left", "spicy"))
    expected = filled(week, LUNCH_DINNER, one_each(picks(8, SPICY_IDS, 3)))
    assert path.read_bytes() == expected
    r2 = DataFolder(suggest_folder(source, tmp_path, "r2"))
    path2 = _new_week(home, r2, week)
    result = suggest(home, r2, *week_line(week, "--tag", "辣", *IN_ZH), random=seeded(8))
    assert result == out(some_zh(week, 3, 14, 0, "left", "辣"))
    assert path2.read_bytes() == expected


def test_f14_t07_a_week_filled_in_part_gets_the_one_recipe_that_it_does_not_hold(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """v0.2-S05: one recipe for Monday lunch, a second run with no candidate, and the language."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    week = example_folder.menu_file(W47)
    old = week.read_bytes().splitlines()
    assert suggest(home, example_folder, *week_line(W47), random=seeded(3)) == out(
        some(W47, 1, 10, 4, "left")
    )
    assert week.read_bytes() == w47_filled()
    new_lines = week.read_bytes().splitlines()
    assert [(a, b) for a, b in zip(old, new_lines, strict=True) if a != b] == [
        (b"lunch = []", b'lunch = ["red-braised-pork"]')
    ]
    stamped = stamp(week)
    assert suggest(home, example_folder, *week_line(W47, *IN_ZH)) == out(
        some_zh(W47, 0, 9, 5, "left")
    )
    assert stamp(week) == stamped
    assert at(home, example_folder, "menu", "show", W47) == out(SHOW_47_FILLED)
    fresh = DataFolder(made(source, tmp_path, "fresh"))
    assert suggest(home, fresh, *week_line(W47, *IN_ZH)) == out(some_zh(W47, 1, 10, 4, "left"))
    zh = DataFolder(made(source, tmp_path, "zh", chinese_settings))
    assert suggest(home, zh, *week_line(W47)) == out(some_zh(W47, 1, 10, 4, "left"))
    assert suggest(home, zh, *week_line(W47, "--lang", "en")) == out(some(W47, 0, 9, 5, "left"))


class Ran(NamedTuple):
    """One run of ``menu suggest`` in a new folder.

    Attributes:
        result: The exit code and the two streams.
        before: The bytes and the time of the menu file before the run.
        after: The bytes and the time of the menu file after the run.
        source: The generator that the run got.
    """

    result: tuple[int, str, str]
    before: tuple[bytes, int]
    after: tuple[bytes, int]
    source: Source


def _ran(  # noqa: PLR0917 - the inputs of one run, in the order of the test plan
    home: Path,
    base: DataFolder,
    tmp_path: Path,
    name: str,
    changes: Sequence[Change],
    rest: Sequence[str] = (),
    week: str = WEEK_48,
    random: Source | None = None,
) -> Ran:
    """Makes a new example with the changes, runs ``menu suggest`` once, and gives the run."""
    root = made(base, tmp_path, name, *changes)
    file = root / "menus" / f"{week}.toml"
    before = stamp(file)
    used = FrontSource() if random is None else random
    result = suggest(home, root, *week_line(week, *rest), random=used)
    return Ran(result, before, stamp(file), used)


TWO = with_dishes("{ dinner = 2 }")
NOT_TOO_MANY = [["choy-sum", "cola-wings"], ["mapo-tofu"], ["red-braised-pork"], ["rice"]]


def _week(*lists: Sequence[str]) -> Change:
    """Gives the change that writes ``menus/2026-W48.toml`` as a week of dinners."""
    return menu_as(WEEK_48, dinners(WEEK_48, *lists))


def _input_1(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 1: one empty meal, six kept, with and without a tag."""
    lists = [["choy-sum"], ["cola-wings"], ["mapo-tofu"], ["red-braised-pork"], ["rice"]]
    lists += [["tomato-egg"], []]
    changes = (DINNER, _week(*lists))
    expected = dinners(WEEK_48, *lists[:6], ["tomato-egg-noodles"]).encode("utf-8")
    plain = _ran(home, base, tmp_path, "a1", changes)
    assert plain.result == out(refill(WEEK_48, 1, 6))
    assert plain.after[0] == expected
    staple = _ran(home, base, tmp_path, "a2", changes, ("--tag", "staple"))
    assert staple.result == out(refill(WEEK_48, 1, 6, "staple"))
    assert staple.after[0] == expected
    assert staple.source.calls == [(["tomato-egg-noodles"], 1)]
    chinese = _ran(home, base, tmp_path, "a3", changes, ("--tag", "staple", *IN_ZH))
    assert chinese.result == out(refill_zh(WEEK_48, 1, 6, "主食"))


def _input_2(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 2: six empty meals and one kept, in both languages."""
    changes = (DINNER, _week(["rice"], [], [], [], [], [], []))
    ids = ["choy-sum", "cola-wings", "mapo-tofu", "red-braised-pork", "tomato-egg"]
    expected = dinners(WEEK_48, ["rice"], *[[i] for i in ids], ["tomato-egg-noodles"])
    plain = _ran(home, base, tmp_path, "b1", changes)
    assert plain.result == out(refill(WEEK_48, 6, 1))
    assert plain.after[0] == expected.encode("utf-8")
    chinese = _ran(home, base, tmp_path, "b2", changes, IN_ZH)
    assert chinese.result == out(refill_zh(WEEK_48, 6, 1))
    assert chinese.after[0] == plain.after[0]


def _input_3(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 3: every recipe is in the week, and the empty meal stays empty."""
    lists = [["choy-sum", "cola-wings"], ["mapo-tofu"], ["red-braised-pork"], ["rice"]]
    lists += [["tomato-egg"], ["tomato-egg-noodles"], []]
    changes = (DINNER, _week(*lists))
    for name, rest, text in (
        ("c1", (), some(WEEK_48, 0, 1, 6, "left")),
        ("c2", ("--tag", "vegetarian"), some(WEEK_48, 0, 1, 6, "left", "vegetarian")),
        ("c3", IN_ZH, some_zh(WEEK_48, 0, 1, 6, "left")),
    ):
        ran = _ran(home, base, tmp_path, name, changes, rest)
        assert ran.result == out(text), name
        assert ran.source.calls == [([], 0)], name
        assert ran.before == ran.after, name


def _input_4(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 4: a dinner of 2 dishes stays empty while one recipe is left."""
    lists = [["choy-sum", "cola-wings"], ["mapo-tofu", "red-braised-pork"], ["rice", "tomato-egg"]]
    lists += [["rice"], ["rice"], ["rice"], []]
    changes = (DINNER, TWO, _week(*lists))
    for name, rest, text in (
        ("d1", (), some(WEEK_48, 0, 1, 6, "few")),
        ("d2", ("--tag", "staple"), some(WEEK_48, 0, 1, 6, "few", "staple")),
        ("d3", IN_ZH, some_zh(WEEK_48, 0, 1, 6, "few")),
        ("d4", ("--tag", "staple", *IN_ZH), some_zh(WEEK_48, 0, 1, 6, "few", "主食")),
    ):
        ran = _ran(home, base, tmp_path, name, changes, rest)
        assert ran.result == out(text), name
        assert ran.source.calls == [(["tomato-egg-noodles"], 1)], name
        assert ran.before == ran.after, name


def _input_5(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 5: dinners of 2 dishes in an empty week, with three tags."""
    week = "2026-W50"
    changes = (DINNER, TWO, new_menu(week, [Meal.DINNER]))
    one = _ran(home, base, tmp_path, "e1", changes, ("--tag", "quick"), week)
    assert one.result == out(some(week, 1, 7, 0, "few", "quick"))
    assert one.after[0] == filled(week, [Meal.DINNER], [["choy-sum", "tomato-egg"]])
    chinese = _ran(home, base, tmp_path, "e2", changes, ("--tag", "快手", *IN_ZH), week)
    assert chinese.result == out(some_zh(week, 1, 7, 0, "few", "快手"))
    home_style = _ran(home, base, tmp_path, "e3", changes, ("--tag", "home-style"), week)
    assert home_style.result == out(some(week, 2, 7, 0, "left", "home-style"))
    fills = [["cola-wings", "mapo-tofu"], ["red-braised-pork", "tomato-egg"]]
    assert home_style.after[0] == filled(week, [Meal.DINNER], fills)


def _input_6(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 6: three meals a day with dinners of 2 dishes, and the order of the picks."""
    changes = (with_meals(*EVERY_MEAL), TWO, new_menu(WEEK_48, EVERY_MEAL))
    front = _ran(home, base, tmp_path, "f1", changes)
    assert front.result == out(some(WEEK_48, 6, 21, 0, "left"))
    fills = [["choy-sum"], ["cola-wings"], ["mapo-tofu", "red-braised-pork"], ["rice"]]
    fills += [["tomato-egg"], None, ["tomato-egg-noodles"]]
    assert front.after[0] == filled(WEEK_48, EVERY_MEAL, fills)
    back = _ran(home, base, tmp_path, "f2", changes, random=BackSource())
    assert back.result == out(some(WEEK_48, 6, 21, 0, "left"))
    fills = [["tomato-egg-noodles"], ["tomato-egg"], ["rice", "red-braised-pork"], ["mapo-tofu"]]
    fills += [["cola-wings"], None, ["choy-sum"]]
    assert back.after[0] == filled(WEEK_48, EVERY_MEAL, fills)


def _input_7(home: Path, base: DataFolder, tmp_path: Path) -> None:
    """Input 7: seven dinners in Chinese get the seven recipes in ID order."""
    changes = (DINNER, new_menu(WEEK_48, [Meal.DINNER]))
    ran = _ran(home, base, tmp_path, "g1", changes, IN_ZH)
    assert ran.result == out(first_zh(WEEK_48, 7))
    assert ran.after[0] == filled(WEEK_48, [Meal.DINNER], one_each(EXAMPLE_IDS))


def test_f14_t08_each_form_of_the_output_follows_its_counts_and_its_tag(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """Seven inputs: the forms for one, the reasons, a meal of too many dishes, and the order."""
    home = make_home(tmp_path)
    base = pristine(example_folder, tmp_path)
    for check_input in (_input_1, _input_2, _input_3, _input_4, _input_5, _input_6, _input_7):
        check_input(home, base, tmp_path)


def test_f14_t09_a_week_with_no_empty_meal_reads_no_text_and_no_recipe(
    example_folder: DataFolder, tmp_path: Path
) -> None:
    """The mistake in ``mapo-tofu`` changes nothing, because no recipe is read."""
    home = make_home(tmp_path)
    source = pristine(example_folder, tmp_path)
    lists = (
        ["choy-sum"],
        ["cola-wings"],
        ["red-braised-pork"],
        ["rice"],
        ["tomato-egg"],
        ["tomato-egg-noodles"],
        ["rice"],
    )
    root = made(
        source,
        tmp_path,
        "f",
        DINNER,
        mapo_mistake,
        menu_as(WEEK_48, dinners(WEEK_48, *lists)),
    )
    file = root / "menus" / "2026-W48.toml"
    stamped = stamp(file)
    sources = [FrontSource() for _ in range(4)]
    assert suggest(home, root, *week_line(WEEK_48), random=sources[0]) == out(full(WEEK_48))
    assert stamp(file) == stamped
    result = suggest(home, root, *week_line(WEEK_48, *IN_ZH), random=sources[1])
    assert result == out(full_zh(WEEK_48))
    assert stamp(file) == stamped
    result = suggest(home, root, *week_line(WEEK_48, "--tag", "spicy"), random=sources[2])
    assert result == out(full(WEEK_48))
    assert stamp(file) == stamped
    result, calls, listings = traced(home, root, [], *week_line(WEEK_48), random=sources[3])
    assert result == out(full(WEEK_48))
    assert calls == [READ_SETTINGS, READ_CATALOG, "read menus/2026-W48.toml"]
    assert listings == LISTINGS
    assert stamp(file) == stamped
    assert [item.calls for item in sources] == [[], [], [], []]
