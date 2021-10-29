"""Utils for aiohue."""
from enum import Enum
import logging
from dataclasses import asdict, fields, is_dataclass, dataclass


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


def to_dict(obj_in: dataclass, skip_none: bool = True) -> dict:
    """Convert dataclass instance to dict, optionally skip None values."""
    dict_obj = asdict(
        obj_in, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
    )

    def _clean_dict(_dict: dict):
        # convert unserializable types
        for key, value in _dict.items():
            if isinstance(value, Enum):
                _dict[key] = value.value
            elif isinstance(value, dict):
                _clean_dict(value)

    _clean_dict(dict_obj)
    return dict_obj
