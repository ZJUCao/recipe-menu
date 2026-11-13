"""Test of F07 for the performance target PT01 of recipe-menu check (T25)."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pt01_support import (
    check_after_mistakes,
    check_run,
    make_pt01,
    median_and_range,
    time_limit,
    timed_runs,
)


# pytest warns that record_property is incompatible with xunit2, but pytest 9.2.0 writes the
# properties into the xunit2 JUnit file anyway, so the warning is silenced.
@pytest.mark.filterwarnings("ignore:record_property is incompatible:pytest.PytestWarning")
def test_f07_t25_check_finishes_the_pt01_folder_within_the_limit(
    tmp_path: Path, record_property: Callable[[str, object], None]
) -> None:
    """PT01: the median of 5 runs of python -m recipe_menu check is under the limit."""
    pt01 = tmp_path / "pt01"
    make_pt01(pt01)
    check_run(tmp_path, pt01)
    times = timed_runs(tmp_path, pt01)
    median, least, greatest = median_and_range(times)
    record_property("pt01_times_seconds", ", ".join(f"{seconds:.3f}" for seconds in times))
    record_property("pt01_median_seconds", f"{median:.3f}")
    record_property("pt01_range_seconds", f"{least:.3f} to {greatest:.3f}")
    check_after_mistakes(tmp_path, pt01)
    assert median < time_limit(), (median, times)
