"""
Core MCP server instance for the FreeCAD bridge, built on the current
official MCP Python SDK (``mcp.server.mcpserver.MCPServer`` — the
successor to the earlier ``FastMCP`` class and the old low-level
``Server`` + ``@server.list_tools()`` / ``@server.call_tool()`` API).

Tool modules in ``freecad_mcp.tools`` import ``mcp_server`` from here and
register their tools on it with ``@mcp_server.tool()``.
"""
from __future__ import annotations

import json
import logging
import math
from typing import Any

from mcp.server.mcpserver import MCPServer

from freecad_mcp.config import DEFAULT_CONFIG
from freecad_mcp.transport.socket_client import FreeCADConnectionError, send_command

logging.basicConfig(level=logging.INFO, stream=None)
logger = logging.getLogger("freecad_mcp")

mcp_server = MCPServer(
    name="freecad",
    title="FreeCAD MCP Server",
    version="3.1.0",
    instructions=(
        "Tools for controlling FreeCAD via the AI Copilot workbench. "
        "Most tools require FreeCAD to be running with that workbench "
        "active. Use check_freecad_connection first if unsure."
    ),
)


def _validate_payload(value: Any, *, depth: int = 0) -> None:
    """Reject values that are unsafe or unsuitable for JSON socket transport."""
    if depth > 32:
        raise ValueError("Command arguments exceed the maximum nesting depth (32).")
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Numeric arguments must be finite (NaN and infinity are not allowed).")
        return
    if isinstance(value, str):
        if len(value) > 65536:
            raise ValueError("String arguments cannot exceed 65536 characters.")
        return
    if isinstance(value, (list, tuple)):
        if len(value) > 10000:
            raise ValueError("List arguments cannot contain more than 10000 items.")
        for item in value:
            _validate_payload(item, depth=depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > 10000:
            raise ValueError("Object arguments cannot contain more than 10000 entries.")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Argument object keys must be strings.")
            _validate_payload(key, depth=depth + 1)
            _validate_payload(item, depth=depth + 1)
        return
    raise ValueError(f"Unsupported argument type: {type(value).__name__}")


def dispatch(tool_name: str, **args: Any) -> str:
    """Send a command to FreeCAD and return a JSON string result.

    Centralizes error handling and the interactive-selection workflow so
    individual tool functions in freecad_mcp.tools stay tiny.
    """
    try:
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("tool_name must be a non-empty string.")
        _validate_payload(args)
        encoded = json.dumps(
            {"tool": tool_name, "args": args},
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(encoded) > DEFAULT_CONFIG.max_message_bytes:
            raise ValueError(
                f"Command exceeds the {DEFAULT_CONFIG.max_message_bytes}-byte message limit."
            )
        result = send_command(tool_name, args, config=DEFAULT_CONFIG)
    except (FreeCADConnectionError, ValueError, TypeError) as exc:
        return json.dumps({"error": str(exc)})

    if isinstance(result, dict) and result.get("status") == "awaiting_selection":
        return _format_selection_request(tool_name, args, result)

    return json.dumps(result)


def _format_selection_request(
    tool_name: str, original_args: dict[str, Any], selection_request: dict[str, Any]
) -> str:
    """Mirror the original bridge's interactive-selection UX."""
    message = selection_request.get("message", "Please make a selection in FreeCAD")
    selection_type = selection_request.get("selection_type", "elements")
    object_name = selection_request.get("object_name", "")
    operation_id = selection_request.get("operation_id", "")

    return json.dumps(
        {
            "interactive": True,
            "message": f"Interactive Selection Required\n\n{message}",
            "operation_id": operation_id,
            "selection_type": selection_type,
            "object_name": object_name,
            "tool_name": tool_name,
            "original_args": original_args,
            "instructions": (
                f"1. Go to FreeCAD and select {selection_type} on {object_name}\n"
                "2. Call continue_selection with this operation_id"
            ),
        }
    )
