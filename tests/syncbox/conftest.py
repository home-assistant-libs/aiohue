"""Test helpers for syncbox."""
import pytest
from tests.common import load_fixture

@pytest.fixture(scope="session")
def syncbox_state():
    """Load syncbox state."""
    return load_fixture("syncbox_state.json")
