"""Test parser functions that converts the incoming json from API into dataclass models."""

import datetime
from dataclasses import dataclass, field
import json

import pytest

from aiohue.util import dataclass_from_dict, dataclass_to_dict
from aiohue.v2.models.feature import OnFeature
from aiohue.v2.models.resource import ResourceIdentifier, ResourceTypes
from aiohue.v2.models.scene import Action, ActionAction, ScenePut


@dataclass
class BasicModelChild:
    """Basic test model."""

    a: int
    b: str
    c: str
    d: int | None


@dataclass
class BasicModel:
    """Basic test model."""

    a: int
    b: float
    c: str
    d: int | None
    e: BasicModelChild
    f: datetime.datetime
    g: str = "default"


def test_dataclass_from_dict():
    """Test dataclass from dict parsing."""
    raw = {
        "a": 1,
        "b": 1.0,
        "c": "hello",
        "d": 1,
        "e": {"a": 2, "b": "test", "c": "test", "d": None},
        "f": "2022-12-09T06:58:00Z",
    }
    res = dataclass_from_dict(BasicModel, raw)
    # test the basic values
    assert isinstance(res, BasicModel)
    assert res.a == 1
    assert res.b == 1.0
    assert res.d == 1
    # test recursive parsing
    assert isinstance(res.e, BasicModelChild)
    # test default value
    assert res.g == "default"
    # test int gets converted to float
    raw["b"] = 2
    res = dataclass_from_dict(BasicModel, raw)
    assert res.b == 2.0
    # test datetime string
    assert isinstance(res.f, datetime.datetime)
    assert res.f.month == 12
    assert res.f.day == 9
    # test string doesn't match int
    with pytest.raises(TypeError):
        raw2 = {**raw}
        raw2["a"] = "blah"
        dataclass_from_dict(BasicModel, raw2)
    # test missing key result in keyerror
    with pytest.raises(KeyError):
        raw2 = {**raw}
        del raw2["a"]
        dataclass_from_dict(BasicModel, raw2)
    # test extra keys silently ignored in non-strict mode
    raw2 = {**raw}
    raw2["extrakey"] = "something"
    dataclass_from_dict(BasicModel, raw2, strict=False)
    # test extra keys not silently ignored in strict mode
    with pytest.raises(KeyError):
        dataclass_from_dict(BasicModel, raw2, strict=True)


def test_dataclass_to_dict_serializes_enums_in_collections():
    """Ensure enums nested inside lists are serialized to their value."""
    update_obj = ScenePut(
        actions=[
            Action(
                target=ResourceIdentifier(rid="some-id", rtype=ResourceTypes.LIGHT),
                action=ActionAction(on=OnFeature(on=True)),
            )
        ]
    )

    result = dataclass_to_dict(update_obj)

    assert result["actions"][0]["target"]["rtype"] == "light"
    # the request body is handed to json.dumps, so it must contain no Enums
    json.dumps(result)


def test_dataclass_from_dict_uses_default_factory():
    """Ensure a field with a default_factory is not treated as required."""
    calls = []

    def counting_factory() -> list[str]:
        calls.append(1)
        return []

    @dataclass
    class ModelWithFactory:
        """Test model with a default_factory field."""

        a: int
        b: list[str] = field(default_factory=counting_factory)

    result = dataclass_from_dict(ModelWithFactory, {"a": 1})

    assert isinstance(result.b, list)
    assert not result.b
    assert len(calls) == 1

    # the factory has to run per instance, not be shared between them
    result.b.append("x")
    assert not dataclass_from_dict(ModelWithFactory, {"a": 2}).b

    # and it must not run at all when the value is supplied
    calls.clear()
    assert dataclass_from_dict(ModelWithFactory, {"a": 3, "b": ["y"]}).b == ["y"]
    assert not calls
