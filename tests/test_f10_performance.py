"""Test of F10 for the performance target PT01 of recipe-menu search (T21)."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pt01_support import (
    command_run,
    command_runs,
    make_pt01,
    pt01_search,
    record_times,
    time_limit,
)


# pytest warns that record_property is incompatible with xunit2, but pytest 9.2.0 writes the
# properties into the xunit2 JUnit file anyway, so the warning is silenced.
@pytest.mark.filterwarnings("ignore:record_property is incompatible:pytest.PytestWarning")
def test_f10_t21_search_finishes_the_pt01_folder_within_the_limit(
    tmp_path: Path, record_property: Callable[[str, object], None]
) -> None:
    """PT01: the median of 5 runs of python -m recipe_menu search is under the limit."""
    pt01 = tmp_path / "pt01"
    make_pt01(pt01)
    argv = ["search", "食材001"]
    command_run(tmp_path, pt01, argv, pt01_search())
    times = command_runs(tmp_path, pt01, argv, pt01_search())
    median = record_times(record_property, times)
    assert median < time_limit(), (median, times)
