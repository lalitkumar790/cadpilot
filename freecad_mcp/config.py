"""
Configuration for the FreeCAD MCP bridge.

Cross-platform socket settings used to talk to the AI Copilot workbench
running inside FreeCAD.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class SocketConfig:
    """Connection details for reaching the FreeCAD socket server."""

    host: str = "localhost"
    port: int = 23456
    unix_socket_path: str = "/tmp/freecad_mcp.sock"
    timeout_seconds: float = 15.0
    recv_buffer_size: int = 65536  # generous buffer for screenshots / large payloads

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    def is_available(self) -> bool:
        """Best-effort availability check without opening a real connection."""
        if self.is_windows:
            # On Windows we always attempt a TCP connection when needed;
            # there is no cheap way to pre-check without connecting.
            return True
        return os.path.exists(self.unix_socket_path)


DEFAULT_CONFIG = SocketConfig()
