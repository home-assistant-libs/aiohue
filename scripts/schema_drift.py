"""
Compare a raw Hue bridge dump against the aiohue models.

Resources are parsed with `dataclass_from_dict(..., strict=False)`, which drops
any key the model does not declare. New fields therefore arrive silently and
stay invisible until somebody notices a missing feature. This makes that
drift explicit.

Reported findings:
  UNMAPPED_TYPE    resource type in the dump with no aiohue model
  EXTRA            key the bridge sends that the model discards
  ENUM_DRIFT       value that is not a declared member, so it becomes UNKNOWN
  MISSING_REQUIRED non-nullable field without a default that the bridge omits,
                   which makes parsing raise and the resource get dropped
  MISSING_NULLABLE optional field without a default; parses fine, but has to be
                   passed positionally when constructing the model by hand

Usage:
    python scripts/schema_drift.py <dump.json> [--type light] [--verbose]

Produce the dump with scripts/dump_bridge.py.
"""

import argparse
from collections import defaultdict
import dataclasses
from enum import Enum
import importlib
import json
from pathlib import Path
import pkgutil
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

import aiohue.v2.models as models_package
from aiohue.v2.models.resource import ResourceTypes

# rtypes the bridge references but never serves as a resource of its own
REFERENCE_ONLY = {
    "motion_area_candidate",
    "private_group",
    "public_image",
    "recipe",
    "taurus_7455",
}

parser = argparse.ArgumentParser(description="Diff a Hue bridge dump vs the models")
parser.add_argument("dump", help="path to a dump produced by dump_bridge.py")
parser.add_argument("--type", help="only audit this resource type")
parser.add_argument("--verbose", action="store_true", help="report every occurrence")
args = parser.parse_args()

findings: list[tuple[str, str, str, Any]] = []
seen_fields: dict[str, set[str]] = defaultdict(set)
type_hint_cache: dict[type, dict[str, Any]] = {}


def build_registry() -> dict[str, type]:
    """Map each CLIP resource type string to the model that represents it."""
    registry: dict[str, type] = {}
    for module_info in pkgutil.iter_modules(models_package.__path__):
        module = importlib.import_module(
            f"{models_package.__name__}.{module_info.name}"
        )
        for obj in vars(module).values():
            if not (isinstance(obj, type) and dataclasses.is_dataclass(obj)):
                continue
            if obj.__module__ != module.__name__:
                continue
            if obj.__name__.endswith(("Put", "Post", "Delete")):
                continue
            for field in dataclasses.fields(obj):
                if field.name == "type" and isinstance(field.default, ResourceTypes):
                    registry.setdefault(field.default.value, obj)
    return registry


REGISTRY = build_registry()


def compare(data: dict, cls: type, path: str) -> None:
    """Compare one resource against the model that should represent it."""
    fields = {f.name: f for f in dataclasses.fields(cls)}
    hints = _hints_for(cls)

    for key in data.keys() - fields.keys():
        findings.append(
            (
                "EXTRA",
                f"{path}.{key}",
                f"{cls.__name__} does not declare {key!r}, the value is discarded",
                data[key],
            )
        )

    seen_fields[f"{path}|{cls.__name__}"] |= data.keys() & fields.keys()

    for name, field in fields.items():
        annotation = hints.get(name, field.type)
        if name in data:
            _walk(data[name], annotation, f"{path}.{name}")
            continue
        if not (
            field.default is dataclasses.MISSING
            and field.default_factory is dataclasses.MISSING
        ):
            continue
        if NoneType in get_args(annotation) or annotation is NoneType:
            findings.append(
                (
                    "MISSING_NULLABLE",
                    f"{path}.{name}",
                    f"{cls.__name__}.{name} is optional but has no default",
                    None,
                )
            )
        else:
            findings.append(
                (
                    "MISSING_REQUIRED",
                    f"{path}.{name}",
                    (
                        f"{cls.__name__}.{name} is required and non-nullable but "
                        f"the bridge omitted it, so parsing raises and the "
                        f"resource is dropped"
                    ),
                    None,
                )
            )


def report(unmapped: list[tuple[str, int, dict]], audited: dict[str, type]) -> int:
    """Print every section and return the number of distinct drift points."""
    extra = _dedupe("EXTRA")
    enum_drift = _dedupe("ENUM_DRIFT")
    missing = _dedupe("MISSING_REQUIRED")

    _report_unmapped(unmapped)
    _report_extra(extra)
    _report_detail("ENUM DRIFT  (value silently becomes UNKNOWN)", enum_drift)
    _report_detail("MISSING REQUIRED FIELDS  (parsing raises)", missing)
    _section(
        "NO DEFAULT BUT OPTIONAL  (harmless, awkward to construct)",
        [f"  {path}" for path in sorted(_dedupe("MISSING_NULLABLE"))],
    )
    _report_never_seen(audited)

    return len(extra) + len(enum_drift) + len(missing) + len(unmapped)


def _hints_for(cls: type) -> dict[str, Any]:
    """Resolve and cache the type hints of a model."""
    if cls not in type_hint_cache:
        try:
            type_hint_cache[cls] = get_type_hints(cls)
        except (NameError, TypeError):  # fall back to the raw annotations
            type_hint_cache[cls] = {f.name: f.type for f in dataclasses.fields(cls)}
    return type_hint_cache[cls]


def _members(annotation: Any) -> list[Any]:
    """Return the non-None members of a union annotation."""
    if get_origin(annotation) in (Union, UnionType):
        return [a for a in get_args(annotation) if a is not NoneType]
    return [annotation]


def _walk(value: Any, annotation: Any, path: str) -> None:
    """Recursively compare a value against its declared annotation."""
    if value is None:
        return

    for member in _members(annotation):
        if isinstance(member, type) and issubclass(member, Enum):
            if isinstance(value, str) and value not in {e.value for e in member}:
                findings.append(
                    (
                        "ENUM_DRIFT",
                        path,
                        (
                            f"{member.__name__} has no member for {value!r} "
                            f"(declared: {sorted(e.value for e in member)})"
                        ),
                        value,
                    )
                )
            return

    for member in _members(annotation):
        origin = get_origin(member)
        if origin in (list, tuple, set) and isinstance(value, list):
            for index, item in enumerate(value):
                suffix = f"[{index}]" if args.verbose else "[]"
                _walk(item, get_args(member)[0], f"{path}{suffix}")
            return
        if origin is dict and isinstance(value, dict):
            for key, item in value.items():
                suffix = f".{{{key}}}" if args.verbose else ".{}"
                _walk(item, get_args(member)[1], f"{path}{suffix}")
            return

    candidates = [
        m
        for m in _members(annotation)
        if isinstance(m, type) and dataclasses.is_dataclass(m)
    ]
    if candidates and isinstance(value, dict):
        # a union of models: pick whichever explains the most keys
        best = max(
            candidates,
            key=lambda c: len({f.name for f in dataclasses.fields(c)} & value.keys()),
        )
        compare(value, best, path)


def _dedupe(kind: str) -> dict[str, tuple[int, Any, str]]:
    """Collapse repeated findings of one kind into one entry per path."""
    result: dict[str, tuple[int, Any, str]] = {}
    for found_kind, path, detail, sample in findings:
        if found_kind != kind:
            continue
        if path in result:
            count, first, first_detail = result[path]
            result[path] = (count + 1, first, first_detail)
        else:
            result[path] = (1, sample, detail)
    return result


def _report_unmapped(unmapped: list[tuple[str, int, dict]]) -> None:
    """List resource types with no model at all."""
    lines = []
    for rtype, count, sample in unmapped:
        known = rtype in {t.value for t in ResourceTypes}
        tag = "in ResourceTypes but no model" if known else "COMPLETELY UNKNOWN"
        lines.append(f"  {rtype:<32} x{count:<5} {tag}")
        lines.append(f"      keys: {sorted(sample.keys())}")
    _section("UNMAPPED RESOURCE TYPES", lines)


def _report_extra(extra: dict[str, tuple[int, Any, str]]) -> None:
    """List keys the bridge sends that the models discard."""
    lines = []
    for path in sorted(extra):
        count, sample, _ = extra[path]
        value = json.dumps(sample)
        if len(value) > 120:
            value = value[:117] + "..."
        lines.append(f"  {path:<52} x{count}")
        lines.append(f"      value seen: {value}")
    _section("EXTRA KEYS  (the bridge sends it, aiohue discards it)", lines)


def _report_detail(title: str, collected: dict[str, tuple[int, Any, str]]) -> None:
    """List findings that carry an explanation."""
    lines = []
    for path in sorted(collected):
        count, _, detail = collected[path]
        lines.append(f"  {path:<52} x{count}")
        lines.append(f"      {detail}")
    _section(title, lines)


def _report_never_seen(audited: dict[str, type]) -> None:
    """List declared fields this bridge never sent."""
    lines = []
    for rtype, cls in sorted(audited.items()):
        declared = {f.name for f in dataclasses.fields(cls)}
        never = declared - seen_fields.get(f"{rtype}|{cls.__name__}", set()) - {"type"}
        if never:
            lines.append(f"  {rtype:<28} {cls.__name__}: {sorted(never)}")
    _section("DECLARED BUT NEVER SEEN  (unused here, or gone upstream)", lines)


def _section(title: str, lines: list[str]) -> None:
    """Print a report section, unless it is empty."""
    if not lines:
        return
    print(f"\n{title}")
    print("=" * len(title))
    for line in lines:
        print(line)


def main() -> None:
    """Load the dump, compare every resource, print the report."""
    with Path(args.dump).open(encoding="utf-8") as handle:
        dump = json.load(handle)
    if isinstance(dump, dict) and "data" in dump:
        dump = dump["data"]

    by_type: dict[str, list[dict]] = defaultdict(list)
    for resource in dump:
        by_type[resource.get("type", "<no type>")].append(resource)

    unmapped: list[tuple[str, int, dict]] = []
    audited: dict[str, type] = {}
    for resource_type, items in sorted(by_type.items()):
        if args.type and resource_type != args.type:
            continue
        model = REGISTRY.get(resource_type)
        if model is None:
            unmapped.append((resource_type, len(items), items[0]))
            continue
        audited[resource_type] = model
        for resource in items:
            compare(resource, model, resource_type)

    print("\naiohue schema drift report")
    print(f"dump: {args.dump}")
    print(
        f"resource types: {len(by_type)}   modelled: {len(audited)}   "
        f"unmapped: {len(unmapped)}"
    )
    print(f"\n{report(unmapped, audited)} distinct drift point(s).")
    print(
        "Only covers resource types present on this bridge; "
        "unowned devices can hide more."
    )


main()
