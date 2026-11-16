"""PT01, the only performance target of v0.1: v0.1-S27 to v0.1-S32.

Each case times 5 new processes of ``python -m recipe_menu <command> --data <PT01 folder>``, from
start to exit. A run counts only when it exits with 0 and prints what the work gives. The case
passes when the median of its 5 runs is under 1 second, with no margin. The median and the range
go to the JUnit report as properties.
"""

import statistics
import sys
import time
from collections.abc import Callable

import pytest
from pt01_folder import (
    CHECK_LINES,
    make_pt01,
    pt01_list,
    pt01_menu_show,
    pt01_search,
    pt01_show,
)
from support import Result, World, environment, start, text

RUNS = 5
LIMIT_SECONDS = 1.0
Record = Callable[[str, object], None]


@pytest.fixture(scope="module")
def pt01(tmp_path_factory: pytest.TempPathFactory) -> World:
    """Generates the PT01 data folder once, outside every timing, and gives its world.

    The world's ``data`` is the PT01 folder, in a temporary folder with a home and a working
    folder of its own.
    """
    world = World(tmp_path_factory.mktemp("pt01"))
    world.data = world.root / "pt01-data"
    make_pt01(world.data)
    return world


def timed_runs(world: World, args: list[str], check: Callable[[Result], None]) -> list[float]:
    """Runs ``python -m recipe_menu`` with the arguments and ``--data`` 5 times.

    Every run is a new process, timed from start to exit. A run that does not exit with 0 or does
    not print the expected work fails the case, whatever its time.
    """
    command = [sys.executable, "-m", "recipe_menu", *args, "--data", world.data]
    times = []
    for _ in range(RUNS):
        began = time.perf_counter()
        result = start(command, world.work, environment(world.home))
        times.append(time.perf_counter() - began)
        assert result.code == 0, result.err[:500]
        assert result.err == ""
        check(result)
    return times


def judge(record: Record, case: str, times: list[float]) -> None:
    """Records the 5 times, the median, and the range of a case, and checks the median.

    The values go to the JUnit report as properties of the test suite, named after the case,
    because pytest does not write the properties of one test in its default JUnit format.
    """
    median = statistics.median(times)
    record(f"{case}_pt01_times_seconds", ", ".join(f"{seconds:.3f}" for seconds in times))
    record(f"{case}_pt01_median_seconds", f"{median:.3f}")
    record(f"{case}_pt01_range_seconds", f"{min(times):.3f} to {max(times):.3f}")
    assert median < LIMIT_SECONDS, f"median {median:.3f} s, runs {sorted(times)}"


def same_lines(expected: list[str]) -> Callable[[Result], None]:
    """Gives a check that the output equals the lines, each ended with LF."""

    def check(result: Result) -> None:
        """Checks the output of one run."""
        assert result.out == text(expected, "")

    return check


def test_v0_1_s27_pt01_check_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S27: `check` on 1,000 recipes and 52 week menus reports no errors, no warnings."""
    judge(
        record_testsuite_property, "v0_1_s27", timed_runs(pt01, ["check"], same_lines(CHECK_LINES))
    )


def test_v0_1_s28_pt01_list_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S28: `list` prints all 1,000 recipes."""
    judge(
        record_testsuite_property, "v0_1_s28", timed_runs(pt01, ["list"], same_lines(pt01_list()))
    )


def test_v0_1_s29_pt01_show_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S29: `show` prints one recipe with its 12 ingredients."""
    judge(
        record_testsuite_property,
        "v0_1_s29",
        timed_runs(pt01, ["show", "recipe-0500"], same_lines(pt01_show())),
    )


def test_v0_1_s30_pt01_search_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S30: `search` for the shared ingredient prints all 1,000 recipes."""
    judge(
        record_testsuite_property,
        "v0_1_s30",
        timed_runs(pt01, ["search", "食材001"], same_lines(pt01_search())),
    )


def test_v0_1_s31_pt01_menu_show_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S31: `menu show` prints one week of 63 dishes."""
    args = ["menu", "show", "2026-W26"]
    judge(
        record_testsuite_property, "v0_1_s31", timed_runs(pt01, args, same_lines(pt01_menu_show()))
    )


def check_shop(world: World) -> Callable[[Result], None]:
    """Gives a check of `shop 2026-W26`: the item lines are printed, and each run saves its file.

    The check compares the item lines on stdout with the checklist lines of the saved file, then
    deletes the file, so that the next run must save it again.
    """
    saved = world.data / "shopping" / "2026-W26.md"

    def check(result: Result) -> None:
        """Checks the output of one run and the saved file."""
        lines = result.out.split("\n")
        first = "Shopping list for 2026-W26, 22 to 28 June 2026: 21 meals, 63 dishes"
        assert lines[0] == first
        assert lines[-2] == f"Saved {saved}"
        assert saved.is_file()
        listing = saved.read_text(encoding="utf-8")
        printed = sum(line.startswith("  ") for line in lines)
        assert printed > 0
        assert printed == listing.count("- [ ] ")
        saved.unlink()

    return check


def test_v0_1_s32_pt01_shop_finishes_within_1_second(
    pt01: World, record_testsuite_property: Record
) -> None:
    """v0.1-S32: `shop` builds the list of 63 dishes from 63 recipes, prints it, and saves it."""
    times = timed_runs(pt01, ["shop", "2026-W26"], check_shop(pt01))
    judge(record_testsuite_property, "v0_1_s32", times)
