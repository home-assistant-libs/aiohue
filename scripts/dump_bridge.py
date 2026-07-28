"""
Dump the full raw CLIP v2 state of a Hue bridge to a JSON file.

The output deliberately bypasses the aiohue models, so it is ground truth for
what the bridge actually sends. Feed it to schema_drift.py to find fields the
models discard, or to create_fixture.py to refresh the test fixture.

Usage:
    python scripts/dump_bridge.py <host> <appkey> [--out FILE] [--redact]

Use --redact when the dump will be shared or committed. It replaces names, macs
and ip addresses while leaving every key and value shape intact.

Bridges serve a self-signed certificate, so this script does not verify it. The
appkey is sent over that connection, so only run it on a network you trust.
"""

import argparse
import asyncio
import json
from pathlib import Path
import re
import ssl
import sys

import aiohttp

# keys whose values identify a person or a network, scrubbed with --redact.
# field names are never touched, they are the thing being audited.
REDACT_KEYS = {
    "bridge_id",
    "certified",
    "email",
    "ip_address",
    "ipaddress",
    "mac_address",
    "owner_name",
    "public_key",
    "serial_number",
    "username",
}
MAC_PATTERN = re.compile(r"\b([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b")
IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

parser = argparse.ArgumentParser(description="Dump raw Hue CLIP v2 bridge state")
parser.add_argument("host", help="hostname or IP of the Hue bridge")
parser.add_argument("appkey", help="hue-application-key for the bridge")
parser.add_argument("--out", default="bridge_dump.json", help="output file")
parser.add_argument(
    "--redact",
    action="store_true",
    help="scrub identifying values but keep all structure",
)
args = parser.parse_args()


async def main() -> None:
    """Fetch the full bridge state and write it to disk."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context),
        headers={"hue-application-key": args.appkey},
    ) as session:
        url = f"https://{args.host}/clip/v2/resource"
        async with session.get(url) as resp:
            if resp.status == 401:
                print("The bridge rejected the appkey (401).")
                sys.exit(1)
            resp.raise_for_status()
            payload = await resp.json()

    if errors := payload.get("errors"):
        print(f"Bridge reported {len(errors)} error(s): {errors}")

    data = payload.get("data", [])
    if args.redact:
        data = _redact(data)

    with Path(args.out).open("w", encoding="utf-8") as output:
        json.dump(data, output, indent=2, sort_keys=True)

    counts: dict[str, int] = {}
    for resource in data:
        rtype = resource.get("type", "<no type>")
        counts[rtype] = counts.get(rtype, 0) + 1

    print(f"\nWrote {len(data)} resources to {args.out}\n")
    print(f"{'resource type':<34} count")
    print("-" * 44)
    for rtype, count in sorted(counts.items()):
        print(f"{rtype:<34} {count}")


def _redact(obj: object) -> object:
    """Recursively replace identifying values, preserving every key."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key in REDACT_KEYS and isinstance(value, str):
                result[key] = f"<redacted:{key}>"
            elif key == "name" and isinstance(value, str):
                # keep the length, it occasionally explains a parsing quirk
                result[key] = f"<name len={len(value)}>"
            else:
                result[key] = _redact(value)
        return result
    if isinstance(obj, list):
        return [_redact(value) for value in obj]
    if isinstance(obj, str):
        return IP_PATTERN.sub("<ip>", MAC_PATTERN.sub("<mac>", obj))
    return obj


asyncio.run(main())
