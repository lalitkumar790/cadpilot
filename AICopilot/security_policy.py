"""Shared local policy checks for dangerous FreeCAD-side capabilities."""
from __future__ import annotations

import os


def python_execution_enabled() -> bool:
    """Return whether arbitrary Python execution was explicitly enabled.

    This check runs inside the FreeCAD process, independently of the MCP
    server's own opt-in check. Both processes must opt in.
    """
    value = os.environ.get("FREECAD_MCP_ENABLE_PYTHON_EXEC", "")
    return value.strip().lower() in {"1", "true", "yes"}
