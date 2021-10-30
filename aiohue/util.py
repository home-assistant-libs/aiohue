"""Utils for aiohue."""
from enum import Enum
import logging
from dataclasses import asdict, fields, is_dataclass, dataclass
from typing import Any, Type, Union, get_args, get_origin
from aiohttp import ClientSession
from datetime import datetime

try:
    # python 3.10
    from types import NoneType
except:  # noqa
    # older python version
    NoneType = type(None)


async def is_v2_bridge(host: str, websession: ClientSession | None = None) -> bool:
    """Check if the bridge has support for the new V2 api."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # v2 api is https only and returns a 403 forbidden when no key provided
        url = f"https://{host}/clip/v2/resources"
        async with websession.get(url, ssl=False) as res:
            return res.status == 403
    except Exception:  # pylint: disable=broad-except
        return False
    finally:
        if not websession_provided:
            await websession.close()


def normalize_bridge_id(bridge_id: str):
    """Normalize a bridge identifier."""
    bridge_id = bridge_id.lower()

    # zeroconf: properties['id'], field contains semicolons after each 2 char
    if len(bridge_id) == 17 and bridge_id.count(":") == 5:
        return bridge_id.replace(":", "")

    # nupnp: contains 4 extra characters in the middle: "fffe"
    if len(bridge_id) == 16 and bridge_id[6:10] == "fffe":
        return bridge_id[0:6] + bridge_id[-6:]

    # SSDP/UPNP and Hue Bridge API contains right ID.
    if len(bridge_id) == 12:
        return bridge_id

    logging.getLogger(__name__).warn("Received unexpected bridge id: %s", bridge_id)

    return bridge_id


def update_dataclass(org_obj: dataclass, new_obj: dataclass):
    """Update instance of dataclass with another, skipping None values."""
    for f in fields(new_obj):
        new_val = getattr(new_obj, f.name)
        cur_val = getattr(org_obj, f.name)
        if new_val is None:
            continue
        if cur_val == new_val:
            continue
        if is_dataclass(new_val):
            update_dataclass(getattr(org_obj, f.name), new_val)
        else:
            setattr(org_obj, f.name, new_val)


def dataclass_to_dict(obj_in: dataclass, skip_none: bool = True) -> dict:
    """Convert dataclass instance to dict, optionally skip None values."""
    if skip_none:
        dict_obj = asdict(
            obj_in, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
    else:
        dict_obj = asdict(obj_in)

    def _clean_dict(_dict_obj: dict):
        final = {}
        for key, value in _dict_obj.items():
            if value is None and skip_none:
                continue
            if isinstance(value, dict):
                value = _clean_dict(value)
            if isinstance(value, Enum):
                value = value.value
            final[key] = value
        return final

    return _clean_dict(dict_obj)


def parse_utc_timestamp(datetimestr: str):
    """Parse datetime from string."""
    return datetime.fromisoformat(datetimestr.replace("Z", "+00:00"))


def dataclass_from_dict(cls: dataclass, dict_obj: dict, strict=False):
    """
    Create (instance of) a dataclass by providing a dict with values.

    Including support for nested structures and common type conversions.
    If strict mode enabled, any additional keys in the provided dict will result in a KeyError.
    """
    if strict:
        extra_keys = dict_obj.keys() - set([f.name for f in fields(cls)])
        if extra_keys:
            raise KeyError("Extra keys not allowed: %s" % ",".join(extra_keys))

    def _get_val(name: str, value: Any, value_type: Type):
        if value is None and value_type is NoneType:
            return None
        if is_dataclass(value_type) and isinstance(value, dict):
            return dataclass_from_dict(value_type, value)
        origin = get_origin(value_type)
        if origin is list:
            return [_get_val(name, subval, get_args(value_type)[0]) for subval in value]
        if origin is Union:
            # try all possible types
            sub_value_types = get_args(value_type)
            for sub_arg_type in sub_value_types:
                if value is NoneType and sub_arg_type is NoneType:
                    return value
                # try them all until one succeeds
                try:
                    return _get_val(name, value, sub_arg_type)
                except (KeyError, TypeError, ValueError):
                    pass
            raise TypeError(
                f"Value {value} of type {type(value)} is invalid for {name}, "
                f"expected value of type {value_type}"
            )

        if value_type is Any:
            return value
        if value is None and value_type is not NoneType:
            raise KeyError(f"`{name}` of type `{value_type}` is required.")
        if issubclass(value_type, Enum):
            return value_type(value)
        if value_type is type(datetime):
            return parse_utc_timestamp(value)
        if not isinstance(value, value_type):
            raise TypeError(
                f"Value {value} of type {type(value)} is invalid for {name}, "
                f"expected value of type {value_type}"
            )
        return value_type(value)

    return cls(
        **{
            field.name: _get_val(
                f"{cls.__name__}.{field.name}", dict_obj.get(field.name), field.type
            )
            for field in fields(cls)
        }
    )
