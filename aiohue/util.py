"""Utils for aiohue."""

import logging
from dataclasses import MISSING, asdict, dataclass, fields, is_dataclass
from datetime import datetime
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from aiohttp import ClientSession

from aiohue.errors import raise_from_error


async def create_app_key(
    host: str, device_type: str, websession: ClientSession | None = None
) -> str:
    """
    Create a user on the Hue bridge and return it's app_key for authentication.

    The link button on the bridge must be pressed before executing this call,
    otherwise a LinkButtonNotPressed error will be raised.

    Parameters:
        `host`: the hostname or IP-address of the bridge as string.
        `device_type`: provide a name/type for your app for identification.
        `websession`: optionally provide a aiohttp ClientSession.
    """
    # https://developers.meethue.com/documentation/configuration-api#71_create_user
    # there is not (yet) a V2 way of creating a user.
    # so this can be used for both V1 and V2 bridges (for now).
    data = {"devicetype": device_type}
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # try both https and http
        for proto in ["https", "http"]:
            try:
                url = f"{proto}://{host}/api"
                async with websession.post(url, json=data, ssl=False) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    # response is returned as list
                    result = result[0]
                    if "error" in result:
                        raise_from_error(result["error"])
                    return result["success"]["username"]
            except Exception as exc:  # pylint: disable=broad-except
                if proto == "http":
                    raise exc
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

    logging.getLogger(__name__).warning("Received unexpected bridge id: %s", bridge_id)

    return bridge_id


def update_dataclass(cur_obj: dataclass, new_vals: dict) -> set[str]:
    """
    Update instance of dataclass from (partial) dict.

    Returns: Set with changed keys.
    """
    changed_keys = set()
    for f in fields(cur_obj):
        cur_val = getattr(cur_obj, f.name, None)
        new_val = new_vals.get(f.name)

        # handle case where value is sub dataclass/model
        if is_dataclass(cur_val) and isinstance(new_val, dict):
            for subkey in update_dataclass(cur_val, new_val):
                changed_keys.add(f"{f.name}.{subkey}")
            continue
        # parse value from type annotations
        new_val = _parse_value(f.name, new_val, f.type, cur_val)
        if cur_val == new_val:
            continue
        setattr(cur_obj, f.name, new_val)
        changed_keys.add(f.name)
    return changed_keys


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
                value = _clean_dict(value)  # noqa: PLW2901
            if isinstance(value, Enum):
                value = value.value  # noqa: PLW2901
            final[key] = value
        return final

    return _clean_dict(dict_obj)


def parse_utc_timestamp(datetimestr: str):
    """Parse datetime from string."""
    return datetime.fromisoformat(datetimestr)


def format_utc_timestamp(time: datetime):
    """Format datetime to string."""
    return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_value(name: str, value: Any, value_type: Any, default: Any = MISSING) -> Any:
    """Try to parse a value from raw (json) data and type annotations."""
    # ruff: noqa: PLR0911
    # pylint: disable=too-many-return-statements,too-many-branches
    if isinstance(value_type, str):
        # this shouldn't happen, but just in case
        value_type = get_type_hints(value_type, globals(), locals())

    if isinstance(value, dict) and hasattr(value_type, "from_dict"):
        # always prefer classes that have a from_dict
        return value_type.from_dict(value)

    if value is None and not isinstance(default, type(MISSING)):
        return default
    if value is None and value_type is NoneType:
        return None
    if is_dataclass(value_type) and isinstance(value, dict):
        return dataclass_from_dict(value_type, value)
    # get origin value type and inspect one-by-one
    origin: Any = get_origin(value_type)
    if origin in (list, tuple, set) and isinstance(value, list | tuple | set):
        return origin(
            _parse_value(name, subvalue, get_args(value_type)[0])
            for subvalue in value
            if subvalue is not None
        )
    # handle dictionary where we should inspect all values
    if origin is dict:
        subkey_type = get_args(value_type)[0]
        subvalue_type = get_args(value_type)[1]
        return {
            _parse_value(subkey, subkey, subkey_type): _parse_value(
                f"{subkey}.value", subvalue, subvalue_type
            )
            for subkey, subvalue in value.items()
        }
    # handle Union type
    if origin is Union or origin is UnionType:
        # try all possible types
        sub_value_types = get_args(value_type)
        for sub_arg_type in sub_value_types:
            if value is NoneType and sub_arg_type is NoneType:
                return value
            if value == {} and sub_arg_type is NoneType:
                # handle case where optional value is received as empty dict from api
                return None
            # try them all until one succeeds
            try:
                return _parse_value(name, value, sub_arg_type)
            except (KeyError, TypeError, ValueError):
                pass
        # if we get to this point, all possibilities failed
        # find out if we should raise or log this
        err = (
            f"Value {value} of type {type(value)} is invalid for {name}, "
            f"expected value of type {value_type}"
        )
        if NoneType not in sub_value_types:
            # raise exception, we have no idea how to handle this value
            raise TypeError(err)
        # failed to parse the (sub) value but None allowed, log only
        logging.getLogger(__name__).warning(err)
        return None
    if origin is type:
        return get_type_hints(value, globals(), locals())
    # handle Any as value type (which is basically unprocessable)
    if value_type is Any:
        return value
    # raise if value is None and the value is required according to annotations
    if value is None and value_type is not NoneType:
        raise KeyError(f"`{name}` of type `{value_type}` is required.")

    try:
        if issubclass(value_type, Enum):
            return value_type(value)
        if issubclass(value_type, datetime):
            return parse_utc_timestamp(value)
    except TypeError:
        # happens if value_type is not a class
        pass

    # common type conversions (e.g. int as string)
    if value_type is float and isinstance(value, int):
        return float(value)
    if value_type is int and isinstance(value, str) and value.isnumeric():
        return int(value)

    # If we reach this point, we could not match the value with the type and we raise
    if not isinstance(value, value_type):
        raise TypeError(
            f"Value {value} of type {type(value)} is invalid for {name}, "
            f"expected value of type {value_type}"
        )
    return value


def dataclass_from_dict(cls: dataclass, dict_obj: dict, strict=False):
    """
    Create (instance of) a dataclass by providing a dict with values.

    Including support for nested structures and common type conversions.
    If strict mode enabled, any additional keys in the provided dict will result in a KeyError.
    """
    if strict:
        extra_keys = dict_obj.keys() - set([f.name for f in fields(cls)])  # pylint: disable=consider-using-set-comprehension
        if extra_keys:
            raise KeyError(
                f"Extra key(s) {','.join(extra_keys)} not allowed for {cls!s}"
            )

    return cls(
        **{
            field.name: _parse_value(
                f"{cls.__name__}.{field.name}",
                dict_obj.get(field.name),
                field.type,
                field.default,
            )
            for field in fields(cls)
        }
    )


def mac_from_bridge_id(bridge_id: str) -> str:
    """Parse mac address from bridge id."""
    parts = [
        bridge_id[0:2],
        bridge_id[2:4],
        bridge_id[4:6],
        # part 6:10 needs to be left out (fffe)
        bridge_id[10:12],
        bridge_id[12:14],
        bridge_id[14:16],
    ]
    return ":".join(parts)
