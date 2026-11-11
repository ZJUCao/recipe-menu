"""Shared fixtures of the tests."""

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from recipe_menu.datafile import DataFolder

EXAMPLE_DATA = Path(__file__).parent / "data" / "example"


@pytest.fixture
def default_int_limit() -> Iterator[None]:
    """Sets Python's limit on int digits to its default of 4,300, then restores the old one."""
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(4300)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(old)


@pytest.fixture
def folder(tmp_path: Path) -> DataFolder:
    """Gives a ``DataFolder`` on the empty ``tmp_path`` of the test."""
    return DataFolder(tmp_path)


@pytest.fixture
def example_folder(tmp_path: Path) -> DataFolder:
    """Copies ``tests/data/example/`` into ``tmp_path`` and gives a ``DataFolder`` on the copy.

    Each file is copied with LF line ends, whatever line ends the checkout gave it, so no test
    depends on the checkout's line ends.
    """
    root = tmp_path / "recipe-menu"
    root.mkdir()
    for source in sorted(EXAMPLE_DATA.rglob("*")):
        target = root / source.relative_to(EXAMPLE_DATA)
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
    return DataFolder(root)
