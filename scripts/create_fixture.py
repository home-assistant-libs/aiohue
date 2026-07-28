"""
Build the anonymized test fixture from a real bridge dump.

Referential integrity is preserved: every uuid gets a deterministic replacement
applied to both `id` and every `rid` pointing at it, so the resource graph still
resolves. Sampling keeps one device per archetype plus a slice of every resource
type, so all types stay represented without the fixture growing unmanageable.

Usage:
    python scripts/create_fixture.py <dump.json> [--out FILE] [--per-type N]

Produce the dump with scripts/dump_bridge.py. Redaction is not required, this
script replaces names and identifiers regardless.
"""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

# rtypes the bridge references but never serves, so a reference to one of them
# is expected to resolve to nothing
REFERENCE_ONLY = {
    "motion_area_candidate",
    "private_group",
    "public_image",
    "recipe",
    "taurus_7455",
}
SALT = "aiohue-fixture-v1"
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

parser = argparse.ArgumentParser(description="Build the anonymized test fixture")
parser.add_argument("dump", help="path to a dump produced by dump_bridge.py")
parser.add_argument(
    "--out", default="tests/fixtures/v2_resources.json", help="output file"
)
parser.add_argument("--per-type", type=int, default=4, help="instances per type")
args = parser.parse_args()

name_counters: dict[str, int] = defaultdict(int)
name_map: dict[str, str] = {}


def references(
    obj: object, *, structural_only: bool, in_list: bool = False
) -> set[str]:
    """
    Collect the rids referenced inside a resource.

    With structural_only, references reachable only through a collection are
    skipped. A scalar reference such as owner or group is structural: the
    resource makes no sense without it. Collection members can be pruned.
    """
    found: set[str] = set()
    if isinstance(obj, dict):
        rid, rtype = obj.get("rid"), obj.get("rtype")
        if (
            isinstance(rid, str)
            and rtype not in REFERENCE_ONLY
            and not (structural_only and in_list)
        ):
            found.add(rid)
        for value in obj.values():
            # once inside a collection everything below it stays non-structural
            found |= references(value, structural_only=structural_only, in_list=in_list)
    elif isinstance(obj, list):
        for value in obj:
            found |= references(value, structural_only=structural_only, in_list=True)
    return found


def main() -> None:
    """Select, anonymize and write the fixture."""
    with Path(args.dump).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("data", data)

    by_id = {r["id"]: r for r in data if "id" in r}
    by_type: dict[str, list[dict]] = defaultdict(list)
    for resource in data:
        by_type[resource.get("type")].append(resource)

    selected = _select(data, by_id, by_type)
    kept = sorted(
        (r for r in data if r.get("id") in selected),
        key=lambda r: (r.get("type", ""), r["id"]),
    )
    # names are assigned up front, keyed on the resource id, so every resource
    # gets a distinct name even though the dump may have redacted them all to
    # the same placeholder
    for resource in kept:
        _assign_name(resource["id"], resource.get("type", "resource"))

    fixture = [_scrub(_prune(r, selected), r["id"]) for r in kept]

    with Path(args.out).open("w", encoding="utf-8") as handle:
        json.dump(fixture, handle, indent=2, sort_keys=True)
        handle.write("\n")

    _report(fixture)


def _select(data: list[dict], by_id: dict[str, dict], by_type: dict) -> set[str]:
    """Choose which resources end up in the fixture."""
    selected = _select_devices(by_type)

    for resource_type, items in by_type.items():
        if resource_type in ("device", "scene"):
            continue
        # prefer services whose owner is already included, so the fixture holds
        # a few fully populated devices instead of many bare ones
        ordered = sorted(
            (r for r in items if "id" in r),
            key=lambda r: ((r.get("owner") or {}).get("rid") not in selected, r["id"]),
        )
        selected.update(r["id"] for r in ordered[: max(args.per_type, 2)])

    selected |= _select_scenes(by_type, by_id)

    # an area is only meaningful together with its motion sensors
    for resource in data:
        owner = (resource.get("owner") or {}).get("rid")
        if owner in selected and by_id.get(owner, {}).get("type") == (
            "motion_area_configuration"
        ):
            selected.add(resource["id"])

    return _close_over_owners(selected, by_id)


def _select_devices(by_type: dict) -> set[str]:
    """
    Take one device per archetype.

    That covers every distinct service layout (bulb, sensor, switch, plug,
    camera, chime) without dragging in near-duplicate bulbs.
    """
    selected: set[str] = set()
    seen_archetypes: set[str] = set()
    for device in sorted(by_type.get("device", []), key=lambda r: r["id"]):
        archetype = (device.get("product_data") or {}).get("product_archetype")
        key = archetype or device["id"]
        if key in seen_archetypes:
            continue
        seen_archetypes.add(key)
        selected.add(device["id"])
    return selected


def _close_over_owners(selected: set[str], by_id: dict[str, dict]) -> set[str]:
    """Pull in every structurally required reference of the current selection."""
    frontier = set(selected)
    while frontier:
        following: set[str] = set()
        for rid in frontier:
            for ref in references(by_id.get(rid, {}), structural_only=True):
                if ref in by_id and ref not in selected:
                    selected.add(ref)
                    following.add(ref)
        frontier = following
    return selected


def _select_scenes(by_type: dict, by_id: dict[str, dict]) -> set[str]:
    """Pick the smallest scenes, plus one dynamic and one static one."""
    selected: set[str] = set()
    by_size = sorted(
        (r for r in by_type.get("scene", []) if "id" in r),
        key=lambda r: (len(r.get("actions") or []), r["id"]),
    )
    chosen = [r for r in by_size if r.get("actions")][: args.per_type]
    for wanted in ("dynamic_palette", "static"):
        for scene in by_size:
            if (scene.get("status") or {}).get("active") == wanted:
                chosen.append(scene)
                break

    for scene in chosen:
        selected.add(scene["id"])
        for action in scene.get("actions") or []:
            target = (action.get("target") or {}).get("rid")
            if target in by_id:
                selected.add(target)
    return selected


def _prune(obj: object, selected: set[str]) -> object:
    """
    Drop collection members referencing anything outside the fixture.

    Members are checked at any depth: a scene action carries its target one
    level down, and an action aimed at a light we left out would dangle.
    """
    if isinstance(obj, dict):
        return {k: _prune(v, selected) for k, v in obj.items()}
    if isinstance(obj, list):
        kept = []
        for value in obj:
            refs = (
                references(value, structural_only=False)
                if isinstance(value, dict)
                else set()
            )
            if any(ref not in selected for ref in refs):
                continue
            kept.append(_prune(value, selected))
        return kept
    return obj


def _scrub(obj: object, resource_id: str) -> object:
    """Replace uuids and identifying values, consistently across the dump."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key in ("id", "rid") and isinstance(value, str):
                result[key] = (
                    _anonymous_uuid(value) if UUID_PATTERN.match(value) else value
                )
            elif key == "name" and isinstance(value, str):
                result[key] = name_map[resource_id]
            elif key == "bridge_id":
                result[key] = "aabbccddeeffggh"
            elif key == "mac_address":
                result[key] = "00:11:22:33:44:55"
            elif key in ("extended_pan_id", "public_key", "serial_number"):
                result[key] = "0000000000000000"
            else:
                result[key] = _scrub(value, resource_id)
        return result
    if isinstance(obj, list):
        return [_scrub(value, resource_id) for value in obj]
    return obj


def _anonymous_uuid(original: str) -> str:
    """Map a uuid to a stable stand-in, so references keep resolving."""
    digest = hashlib.sha256((SALT + original).encode()).hexdigest()
    return (
        f"{digest[0:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"
    )


def _assign_name(resource_id: str, rtype: str) -> None:
    """Reserve a distinct readable name for a resource."""
    name_counters[rtype] += 1
    name_map[resource_id] = f"{rtype.replace('_', ' ').title()} {name_counters[rtype]}"


def _report(fixture: list[dict]) -> None:
    """Print what was written and confirm no reference dangles."""
    ids = {r["id"] for r in fixture if "id" in r}
    dangling: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    for resource in fixture:
        counts[resource.get("type")] += 1
        for ref in references(resource, structural_only=False):
            if ref not in ids:
                dangling[resource.get("type")] += 1

    print(f"wrote {len(fixture)} resources ({len(counts)} types) -> {args.out}")
    for rtype, count in sorted(counts.items()):
        print(f"  {rtype:<32} {count}")
    if dangling:
        print("\nWARNING: dangling references remain:")
        for rtype, count in sorted(dangling.items()):
            print(f"  {rtype}: {count}")
    else:
        print("\nreferential integrity OK - no dangling rids")


main()
