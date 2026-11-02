"""Smoke tests: import the package, confirm tools register, confirm
dispatch() degrades gracefully when FreeCAD isn't running (no socket).

Run with: pytest tests/  (or: python -m pytest tests/)
"""
import asyncio
import json

import pytest

from freecad_mcp.server import dispatch, mcp_server
import freecad_mcp.tools  # noqa: F401  registers tools


def test_tools_registered():
    tools = asyncio.run(mcp_server.list_tools())
    names = {t.name for t in tools}
    # A representative sample across every module, not an exhaustive list.
    expected = {
        "create_box", "boolean_union", "move_object",       # part.py
        "pad", "fillet", "chamfer", "hole",                 # partdesign.py
        "capture_screenshot", "save_document", "undo",       # view.py
        "run_python",                                        # python_exec.py
        "check_freecad_connection", "continue_selection",    # selection.py
    }
    missing = expected - names
    assert not missing, f"Missing expected tools: {missing}"
    assert len(names) >= 40


def test_dispatch_without_freecad_returns_error_not_exception():
    """When FreeCAD isn't running, dispatch should return a JSON error
    string rather than raising — tool functions must never crash the
    MCP server process."""
    result = dispatch("create_box", length=1, width=1, height=1)
    parsed = json.loads(result)
    assert "error" in parsed or "raw" in parsed
