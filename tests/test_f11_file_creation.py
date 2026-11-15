"""Tests of F11 for FileOutcome and FileCreation: the example and the table of 3.2 (T05, T06)."""

import itertools
from pathlib import Path

import pytest

from recipe_menu.datafile import FileCreation, FileOutcome, Problem
from recipe_menu.text import Message

DENIED = Message("Access is denied.", "没有访问权限。")


def test_f11_t05_a_file_creation_holds_its_fields_and_refuses_the_six_wrong_calls() -> None:
    """The example of 3.2, and the hash of a ``FileCreation``."""
    assert [outcome.value for outcome in FileOutcome] == ["created", "exists", "failed"]
    created = FileCreation(FileOutcome.CREATED)
    assert (created.problem, created.left, created.existing) == (None, (), None)
    entry = Path.cwd() / "menus" / "2026-w47.toml"
    assert FileCreation(FileOutcome.EXISTS, existing=entry).existing == entry
    problem = Problem.error(Path("menus", "2026-W47.toml"), None, DENIED)
    left = (Path.cwd() / "menus" / "2026-W47.toml",)
    failed = FileCreation(FileOutcome.FAILED, problem, left)
    assert failed == FileCreation(FileOutcome.FAILED, problem, left)
    warning = Problem.warning(problem.file, None, DENIED)
    wrong = [
        lambda: FileCreation(FileOutcome.FAILED),
        lambda: FileCreation(FileOutcome.EXISTS),
        lambda: FileCreation(FileOutcome.CREATED, problem),
        lambda: FileCreation(FileOutcome.CREATED, left=left),
        lambda: FileCreation(FileOutcome.FAILED, problem, left + left),
        lambda: FileCreation(FileOutcome.FAILED, warning),
    ]
    for make in wrong:
        with pytest.raises(ValueError):
            make()
    assert isinstance(hash(created), int)
    assert isinstance(hash(failed), int)
    assert hash(failed) == hash(FileCreation(FileOutcome.FAILED, problem, left))


def test_f11_t06_every_combination_of_the_four_fields_follows_the_table(tmp_path: Path) -> None:
    """Exactly 4 of the 54 combinations make a ``FileCreation``, and the other 50 raise."""
    message = Message(
        "The file cannot be written: access is denied.", "无法写入文件：没有访问权限。"
    )
    file = Path("menus", "2026-W47.toml")
    error = Problem.error(file, None, message)
    warning = Problem.warning(file, None, message)
    path = tmp_path / "recipe-menu" / "menus" / "2026-W47.toml"
    paths = (path,)
    valid = {
        (FileOutcome.CREATED, None, (), None),
        (FileOutcome.EXISTS, None, (), path),
        (FileOutcome.FAILED, error, (), None),
        (FileOutcome.FAILED, error, paths, None),
    }
    made, refused = 0, 0
    combinations = itertools.product(
        FileOutcome, (None, error, warning), ((), paths, paths + paths), (None, path)
    )
    for combination in combinations:
        if combination in valid:
            creation = FileCreation(*combination)
            fields = (creation.outcome, creation.problem, creation.left, creation.existing)
            assert fields == combination
            made += 1
        else:
            with pytest.raises(ValueError):
                FileCreation(*combination)
            refused += 1
    assert (made, refused) == (4, 50)
