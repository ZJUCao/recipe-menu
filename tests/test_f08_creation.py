"""Tests of F08 for CreationOutcome and Creation (T01 and T02)."""

from pathlib import Path

import pytest

from recipe_menu.datafile import Creation, CreationOutcome, Problem
from recipe_menu.text import Message

DENIED = Message(
    "The folder cannot be created: access is denied.", "无法创建文件夹：没有访问权限。"
)


def test_f08_t01_the_example_of_3_1_values_fields_equality_hash_and_wrong_calls(
    tmp_path: Path,
) -> None:
    """The example of 3.1: members, a valid creation, equality, hashing, and four wrong calls."""
    values = [outcome.value for outcome in CreationOutcome]
    assert values == ["created", "holds files", "not a folder", "failed"]
    created = Creation(CreationOutcome.CREATED)
    assert (created.problem, created.left) == (None, ())
    problem = Problem.error(Path("recipes"), None, DENIED)
    left = (tmp_path / "recipe-menu" / "recipes",)
    failed = Creation(CreationOutcome.FAILED, problem, left)
    assert (failed.problem, failed.left) == (problem, left)
    assert failed == Creation(CreationOutcome.FAILED, problem, left)
    assert isinstance(hash(created), int)
    assert isinstance(hash(failed), int)
    assert hash(failed) == hash(Creation(CreationOutcome.FAILED, problem, left))

    with pytest.raises(ValueError, match=r"."):
        Creation(CreationOutcome.FAILED)
    with pytest.raises(ValueError, match=r"."):
        Creation(CreationOutcome.HOLDS_FILES, problem)
    with pytest.raises(ValueError, match=r"."):
        Creation(CreationOutcome.CREATED, None, left)
    warning = Problem.warning(Path("recipes"), None, DENIED)
    with pytest.raises(ValueError, match=r"."):
        Creation(CreationOutcome.FAILED, warning)


def test_f08_t02_every_combination_of_the_three_fields_follows_the_table(tmp_path: Path) -> None:
    """24 calls: exactly 5 give a Creation with its three fields, and 19 raise ValueError."""
    error = Problem.error(Path("recipes"), None, DENIED)
    warning = Problem.warning(Path("recipes"), None, DENIED)
    full = (tmp_path / "recipe-menu" / "recipes",)
    valid = {
        (CreationOutcome.FAILED, error, ()),
        (CreationOutcome.FAILED, error, full),
        (CreationOutcome.CREATED, None, ()),
        (CreationOutcome.HOLDS_FILES, None, ()),
        (CreationOutcome.NOT_A_FOLDER, None, ()),
    }
    made = 0
    for outcome in CreationOutcome:
        for problem in (None, error, warning):
            for left in ((), full):
                if (outcome, problem, left) in valid:
                    creation = Creation(outcome, problem, left)
                    assert (creation.outcome, creation.problem, creation.left) == (
                        outcome,
                        problem,
                        left,
                    )
                    made += 1
                else:
                    with pytest.raises(ValueError, match=r"."):
                        Creation(outcome, problem, left)
    assert made == 5
