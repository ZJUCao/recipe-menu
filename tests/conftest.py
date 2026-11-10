"""Shared fixtures of the tests."""

import sys
from collections.abc import Iterator

import pytest


@pytest.fixture
def default_int_limit() -> Iterator[None]:
    """Sets Python's limit on int digits to its default of 4,300, then restores the old one."""
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(4300)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(old)
