"""
Configuration for the local FreeCAD MCP bridge.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class SocketConfig:
    """Connection details and resource limits for the FreeCAD socket service."""

    host: str = "127.0.0.1"
    port: int = 23456
    unix_socket_path: str = "/tmp/freecad_mcp.sock"
    timeout_seconds: float = 30.0
    recv_buffer_size: int = 65536
    max_message_bytes: int = 8 * 1024 * 1024

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    def is_available(self) -> bool:
        """Best-effort availability check without opening a real connection."""
        if self.is_windows:
            return True
        return os.path.exists(self.unix_socket_path)


DEFAULT_CONFIG = SocketConfig()
