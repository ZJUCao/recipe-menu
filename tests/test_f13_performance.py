"""Test of F13 for the performance target PT01 of recipe-menu shop (T30)."""

from collections.abc import Callable
from pathlib import Path

import pytest

from f13_support import pt01_shop, shop_file, shop_list
from pt01_support import command_run, command_runs, make_pt01, record_times, time_limit
from recipe_menu.datafile import DataFolder
from recipe_menu.lang import Lang
from recipe_menu.menus import IsoWeek

CATEGORIES = [
    "Vegetables and fruit",
    "Meat and seafood",
    "Eggs, dairy, and tofu",
    "Rice, flour, and oil",
    "Seasonings",
    "Other",
]


def _check_facts(text: str) -> None:
    """Checks the facts that the plan takes from the model: the lines, the groups, the pantry."""
    lines = text.split("\n")[:-1]
    assert lines[0] == "Shopping list for 2026-W26, 22 to 28 June 2026: 21 meals, 63 dishes"
    assert len(lines) == 302
    assert [line for line in lines if line in CATEGORIES] == CATEGORIES
    assert sum(line.startswith("  ") for line in lines) == 290
    pantry = next(line for line in lines if line.startswith("Not on the list"))
    assert len(pantry.split(": ", 1)[1].split(", ")) == 10


# pytest warns that record_property is incompatible with xunit2, but pytest 9.2.0 writes the
# properties into the xunit2 JUnit file anyway, so the warning is silenced.
@pytest.mark.filterwarnings("ignore:record_property is incompatible:pytest.PytestWarning")
def test_f13_t30_shop_finishes_the_pt01_week_within_the_limit(
    tmp_path: Path, record_property: Callable[[str, object], None]
) -> None:
    """PT01: the median of 5 runs of python -m recipe_menu shop is under the limit."""
    pt01 = tmp_path / "pt01"
    make_pt01(pt01)
    expected = pt01_shop(pt01)
    _check_facts(expected[1])
    argv = ["shop", "2026-W26"]
    command_run(tmp_path, pt01, argv, expected)
    times = command_runs(tmp_path, pt01, argv, expected)
    saved = pt01 / "shopping"
    assert [path.name for path in saved.iterdir()] == ["2026-W26.md"]
    shopping = shop_list(DataFolder(pt01), IsoWeek(2026, 26))
    data = (saved / "2026-W26.md").read_bytes()
    assert data == shop_file(shopping, Lang.EN)
    assert len(data) == 10345
    median = record_times(record_property, times)
    assert median < time_limit(), (median, times)
