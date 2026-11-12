"""Tests of F04 for Report.warn (T55 and T56)."""

from pathlib import Path

import pytest

from f04_support import EN, ZH
from recipe_menu.datafile import (
    Problem,
    Report,
    Severity,
    read_list,
    read_text,
    report_unknown_keys,
)
from recipe_menu.lang import BiText, Lang
from recipe_menu.text import Message

FILE = Path("recipes", "rice.toml")
NO_EN = Message("No English steps.", "没有英文步骤。")
COUNT = Message("{count} steps.", "{count} 个步骤。")
UNKNOWN_TAG = Message('Unknown tag "{tag}".', "未知标签“{tag}”。")


def test_f04_t55_warn_appends_a_warning_after_the_errors_of_the_helpers() -> None:
    """The design's example, then ``add`` and ``warn`` with no place and with a value."""
    report = Report(FILE)
    table = {"tags": "主食", "ingredients": [{"item": " "}], "note": 3}
    assert read_list(table, "tags", BiText("tags", "标签"), report) == []
    item = read_text({"item": " "}, "item", BiText("ingredient 1", "食材 1"), report)
    assert item is None
    report_unknown_keys(table, ("tags", "ingredients"), None, report)
    report.warn(BiText("steps", "步骤"), NO_EN)
    report.add(None, NO_EN)
    report.warn(None, COUNT, count=3)
    problems = report.problems
    assert isinstance(problems, list)
    assert len(problems) == 6
    errors, warning = Severity.ERROR, Severity.WARNING
    assert [problem.severity for problem in problems] == [
        errors,
        errors,
        errors,
        warning,
        errors,
        warning,
    ]
    assert problems[0].text(EN) == '"tags" must be a list in square brackets, [ ... ].'
    assert problems[1].text(EN) == '"item" is empty.'
    assert problems[2].text(EN) == 'Unknown key "note". The keys are tags and ingredients.'
    assert problems[3].place == BiText("steps", "步骤")
    assert problems[3] == Problem.warning(FILE, BiText("steps", "步骤"), NO_EN)
    assert problems[4] == Problem.error(FILE, None, NO_EN)
    assert problems[5] == Problem.warning(FILE, None, COUNT, count=3)
    assert problems[5].text(EN) == "3 steps."
    assert problems[5].text(ZH) == "3 个步骤。"


@pytest.mark.usefixtures("default_int_limit")
def test_f04_t56_warn_raises_the_errors_of_problem_warning_and_appends_nothing(
    tmp_path: Path,
) -> None:
    """A message and values that do not fit, an absolute file, and a value of a wrong type."""
    report = Report(FILE)
    value_errors = [
        lambda: report.warn(None, UNKNOWN_TAG),
        lambda: report.warn(None, UNKNOWN_TAG, tag="breakfast", meal="dinner"),
        lambda: report.warn(None, NO_EN, tag="x"),
        lambda: Report(tmp_path / "rice.toml").warn(None, NO_EN),
        lambda: report.warn(None, COUNT, count=10**4300),
    ]
    for call in value_errors:
        with pytest.raises(ValueError):
            call()
    for value in (None, True, 1.5, Lang.ZH):
        with pytest.raises(TypeError):
            report.warn(None, UNKNOWN_TAG, tag=value)
    assert report.problems == []
