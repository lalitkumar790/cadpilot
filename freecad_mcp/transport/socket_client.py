"""Bounded, cross-platform socket transport for the local FreeCAD service.

New clients use newline-delimited JSON. The reader also accepts a complete
legacy JSON document without a trailing newline so older bridge clients remain
compatible during upgrades.
"""
from __future__ import annotations

import json
import logging
import socket
from typing import Any

from freecad_mcp.config import DEFAULT_CONFIG, SocketConfig

logger = logging.getLogger("freecad_mcp.transport")


class FreeCADConnectionError(RuntimeError):
    """Raised when FreeCAD cannot be reached or its response is invalid."""


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


def _decode_response(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        raise FreeCADConnectionError("FreeCAD closed the connection without a response.")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    if isinstance(value, dict):
        return value
    return {"result": value}


def _receive_response(sock: socket.socket, config: SocketConfig) -> dict[str, Any]:
    chunks = bytearray()
    while True:
        try:
            chunk = sock.recv(config.recv_buffer_size)
        except socket.timeout as exc:
            raise FreeCADConnectionError(
                f"Timed out after {config.timeout_seconds:g}s waiting for FreeCAD."
            ) from exc
        except OSError as exc:
            raise FreeCADConnectionError(f"Socket receive failed: {exc}") from exc

        if not chunk:
            return _decode_response(bytes(chunks))

        chunks.extend(chunk)
        if len(chunks) > config.max_message_bytes:
            raise FreeCADConnectionError(
                f"FreeCAD response exceeded the {config.max_message_bytes}-byte limit."
            )

        newline = chunks.find(b"\n")
        if newline >= 0:
            return _decode_response(bytes(chunks[:newline]))

        # Compatibility with the previous server, which sends one complete
        # JSON response without a delimiter and keeps the connection open.
        try:
            parsed = json.loads(chunks.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(parsed, dict):
            return parsed
        return {"result": parsed}


def send_command(
    tool_name: str,
    args: dict[str, Any] | None = None,
    config: SocketConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Send one bounded JSON command and return its JSON response."""
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name must be a non-empty string")
    if args is not None and not isinstance(args, dict):
        raise TypeError("args must be a dictionary or None")

    try:
        payload = json.dumps(
            {"tool": tool_name, "args": args or {}},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Command arguments must be JSON serializable: {exc}") from exc

    if len(payload) > config.max_message_bytes:
        raise ValueError(
            f"Command exceeds the {config.max_message_bytes}-byte message limit."
        )

    try:
        sock = _open_socket(config)
    except FreeCADConnectionError:
        raise
    except OSError as exc:
        raise FreeCADConnectionError(f"Could not connect to FreeCAD: {exc}") from exc

    try:
        sock.sendall(payload)
        # One request per connection. Half-close also lets a legacy server
        # detect end-of-request after it has received the complete JSON.
        try:
            sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        return _receive_response(sock, config)
    except FreeCADConnectionError:
        raise
    except OSError as exc:
        raise FreeCADConnectionError(f"Socket communication error: {exc}") from exc
    finally:
        try:
            sock.close()
        except OSError:
            pass
