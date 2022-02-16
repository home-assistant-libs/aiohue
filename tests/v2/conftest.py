"""Test helpers for v2."""

import pytest

from tests.common import load_fixture


@pytest.fixture(scope="session")
def v2_resources():
    """Load v2 resources."""
    return load_fixture("v2_resources.json")
