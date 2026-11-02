"""Connection status and the interactive-selection continuation workflow."""
from __future__ import annotations

import json

from freecad_mcp.config import DEFAULT_CONFIG
from freecad_mcp.server import dispatch, mcp_server
from freecad_mcp.transport.socket_client import FreeCADConnectionError, send_command


@mcp_server.tool()
def check_freecad_connection() -> str:
    """Check whether the FreeCAD AI Copilot socket is actually responding."""
    socket_path = (
        f"{DEFAULT_CONFIG.host}:{DEFAULT_CONFIG.port}"
        if DEFAULT_CONFIG.is_windows
        else DEFAULT_CONFIG.unix_socket_path
    )
    try:
        response = send_command("list_all_objects", {}, config=DEFAULT_CONFIG)
        status = {
            "connected": True,
            "socket_path": socket_path,
            "status": "Connected to the FreeCAD AI Copilot service",
            "probe": response,
        }
    except FreeCADConnectionError as exc:
        status = {
            "connected": False,
            "socket_path": socket_path,
            "status": str(exc),
        }
    return json.dumps(status, indent=2)


@mcp_server.tool()
def continue_selection(operation_id: str) -> str:
    """Continue an interactive selection operation after selecting elements in FreeCAD."""
    if not operation_id:
        return json.dumps({"error": "operation_id is required to continue selection"})
    return dispatch("continue_selection", operation_id=operation_id)
