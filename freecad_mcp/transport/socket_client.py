"""
Socket transport for talking to the FreeCAD AI Copilot workbench.

This module intentionally preserves the exact wire protocol used by the
original bridge: a JSON object ``{"tool": <name>, "args": {...}}`` sent
over a TCP socket (Windows) or a Unix domain socket (macOS/Linux), with a
JSON string returned as the response.

Nothing here changes the FreeCAD-side socket_server.py contract.
"""
from __future__ import annotations

import json
import logging
import socket
from typing import Any

from freecad_mcp.config import DEFAULT_CONFIG, SocketConfig

logger = logging.getLogger("freecad_mcp.transport")


class FreeCADConnectionError(RuntimeError):
    """Raised when FreeCAD cannot be reached over the socket."""


def _open_socket(config: SocketConfig) -> socket.socket:
    if config.is_windows:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(config.timeout_seconds)
        sock.connect((config.host, config.port))
        return sock

    if not config.is_available():
        raise FreeCADConnectionError(
            "FreeCAD socket not available. Please start FreeCAD and switch "
            "to the AI Copilot workbench."
        )
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(config.timeout_seconds)
    sock.connect(config.unix_socket_path)
    return sock


def send_command(
    tool_name: str,
    args: dict[str, Any] | None = None,
    config: SocketConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Send a single command to FreeCAD and return the parsed JSON response.

    Falls back to ``{"raw": <text>}`` if the response is not valid JSON,
    so callers never have to guard against a JSONDecodeError themselves.
    """
    payload = json.dumps({"tool": tool_name, "args": args or {}})

    try:
        sock = _open_socket(config)
    except FreeCADConnectionError:
        raise
    except OSError as exc:
        raise FreeCADConnectionError(f"Could not connect to FreeCAD: {exc}") from exc

    try:
        sock.sendall(payload.encode("utf-8"))
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(config.recv_buffer_size)
            if not chunk:
                break
            chunks.append(chunk)
            # Most responses arrive in a single recv(); stop as soon as we
            # have a complete JSON document to avoid blocking on servers
            # that keep the connection open.
            try:
                json.loads(b"".join(chunks).decode("utf-8"))
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        raw = b"".join(chunks).decode("utf-8", errors="replace")
    except OSError as exc:
        raise FreeCADConnectionError(f"Socket communication error: {exc}") from exc
    finally:
        try:
            sock.close()
        except OSError:
            pass

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
