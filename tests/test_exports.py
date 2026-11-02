"""Regression tests for explicit export tool registration."""
import asyncio

from freecad_mcp.server import mcp_server
import freecad_mcp.tools  # noqa: F401


def test_export_tools_are_registered():
    names = {tool.name for tool in asyncio.run(mcp_server.list_tools())}
    assert {"export_step", "export_stl"} <= names
