"""Importing this package registers every tool on freecad_mcp.server.mcp_server.

Order doesn't matter for registration, but keeping it alphabetical-ish
mirrors the module layout for readability.
"""
from freecad_mcp.tools import part  # noqa: F401
from freecad_mcp.tools import partdesign  # noqa: F401
from freecad_mcp.tools import python_exec  # noqa: F401
from freecad_mcp.tools import selection  # noqa: F401
from freecad_mcp.tools import view  # noqa: F401

__all__ = ["part", "partdesign", "python_exec", "selection", "view"]
