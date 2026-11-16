"""Fixtures of the version tests."""

from pathlib import Path

import pytest

pytest.register_assert_rewrite("support")

from support import World  # noqa: E402


@pytest.fixture
def world(tmp_path: Path) -> World:
    """Gives the folders of one scenario, all under the test's ``tmp_path``."""
    return World(tmp_path)
