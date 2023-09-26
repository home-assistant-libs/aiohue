# Aiohue

## Asynchronous library to control Philips Hue

Requires Python 3.10+ and uses asyncio and aiohttp.

For usage examples, see the examples folder.

## Hue Bridge version

This library supports both the new style V2 API (only available on V2 bridges) and the old style V1 API.
The biggest advantage of the V2 API is that it supports event based updates so polling is not required.

## Contribution guidelines

Object hierarchy and property/method names should match the Philips Hue API.
