"""Common utilities for fixtures."""

import json
import pathlib


def load_fixture(name: str):
    """Load a fixture from disk."""
    path = pathlib.Path(__file__).parent / "fixtures" / name

    content = path.read_text()

    if name.endswith(".json"):
        return json.loads(content)

    return content
