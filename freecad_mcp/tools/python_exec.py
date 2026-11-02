"""Opt-in escape hatch: run arbitrary Python inside FreeCAD's interpreter.

Disabled by default for student safety. Enable explicitly with
FREECAD_MCP_ENABLE_PYTHON_EXEC=1 in the MCP server environment.
"""
from __future__ import annotations

import json
import os

from freecad_mcp.server import dispatch, mcp_server


@mcp_server.tool()
def run_python(code: str) -> str:
    """Execute arbitrary Python inside FreeCAD. Disabled unless explicitly enabled.

    When enabled, FreeCAD, Part, Sketcher, and other FreeCAD modules are available.
    Only enable this for code and prompts you trust.
    """
    enabled = os.environ.get("FREECAD_MCP_ENABLE_PYTHON_EXEC", "").strip().lower()
    if enabled not in {"1", "true", "yes"}:
        return json.dumps({
            "error": "run_python is disabled by default. Enable it only if you understand "
                     "the risks by setting FREECAD_MCP_ENABLE_PYTHON_EXEC=1 in the MCP "
                     "server environment, then restart Claude Desktop."
        })
    return dispatch("execute_python", code=code)
