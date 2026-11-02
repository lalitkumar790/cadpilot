"""Strict validation for commands received by the in-process FreeCAD socket server.

This module intentionally has no FreeCAD or Qt dependencies so its policy can
be regression-tested with the normal Python test suite.
"""
import math
import re

_TOOL_NAME = re.compile(r"^[a-z][a-z0-9_]{0,127}$")
_MAX_DEPTH = 32
_MAX_STRING_LENGTH = 65536
_MAX_COLLECTION_ITEMS = 10000


def _validate_value(value, depth=0):
    if depth > _MAX_DEPTH:
        raise ValueError("Command arguments exceed the maximum nesting depth.")
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Command arguments must not contain NaN or infinity.")
        return
    if isinstance(value, str):
        if len(value) > _MAX_STRING_LENGTH:
            raise ValueError("Command argument string exceeds the 65536-character limit.")
        return
    if isinstance(value, list):
        if len(value) > _MAX_COLLECTION_ITEMS:
            raise ValueError("Command argument list exceeds the 10000-item limit.")
        for item in value:
            _validate_value(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > _MAX_COLLECTION_ITEMS:
            raise ValueError("Command argument object exceeds the 10000-item limit.")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Command argument keys must be strings.")
            if len(key) > _MAX_STRING_LENGTH:
                raise ValueError("Command argument key exceeds the 65536-character limit.")
            _validate_value(item, depth + 1)
        return
    raise ValueError("Command arguments contain an unsupported JSON value.")


def validate_command_payload(command):
    """Validate and return a normalized {tool, args} socket command."""
    if not isinstance(command, dict):
        raise ValueError("Command must be a JSON object.")
    unexpected = set(command) - {"tool", "args"}
    if unexpected:
        raise ValueError("Command contains unsupported top-level fields.")
    tool_name = command.get("tool")
    if not isinstance(tool_name, str) or not _TOOL_NAME.fullmatch(tool_name):
        raise ValueError("Command tool must be a valid lowercase tool identifier.")
    args = command.get("args", {})
    if not isinstance(args, dict):
        raise ValueError("Command args must be a JSON object.")
    _validate_value(args)
    return {"tool": tool_name, "args": args}
