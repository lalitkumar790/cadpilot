"""Loopback-only Streamable HTTP entry point for ChatGPT Secure MCP Tunnel.

Claude Desktop continues using freecad_mcp.main (stdio).  The HTTP endpoint
must stay local.  A separate, authenticated OpenAI Secure MCP Tunnel client
can forward ChatGPT MCP calls to http://127.0.0.1:8765/mcp without exposing
FreeCAD or its unauthenticated socket to the Internet.
"""
from __future__ import annotations

import os

from freecad_mcp.server import mcp_server
import freecad_mcp.tools  # noqa: F401  Register the same tools as the stdio entry point.

DEFAULT_PORT = 8765


def get_port() -> int:
    """Read and validate a non-privileged local TCP port."""
    value = os.environ.get("CADPILOT_MCP_HTTP_PORT", str(DEFAULT_PORT))
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError("CADPILOT_MCP_HTTP_PORT must be an integer") from exc
    if not 1024 <= port <= 65535:
        raise ValueError("CADPILOT_MCP_HTTP_PORT must be between 1024 and 65535")
    return port


def run() -> None:
    """Serve a local endpoint; do not change the binding to a public address."""
    mcp_server.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=get_port(),
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    run()
