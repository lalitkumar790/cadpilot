"""Read-only checks for the local Claude Desktop MCP configuration."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def inspect_claude_config(
    config_path: str | Path,
    project_root: str | Path,
    python_executable: str | Path,
) -> dict[str, Any]:
    """Check the configured freecad server without changing the user's config."""
    path = Path(config_path)
    root = Path(project_root).resolve()
    python_path = Path(python_executable).resolve()

    if not path.is_file():
        return {"ok": False, "detail": f"Claude config not found: {path}"}
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"ok": False, "detail": f"Cannot read valid Claude config: {exc}"}
    if not isinstance(config, dict):
        return {"ok": False, "detail": "Claude config root must be a JSON object."}

    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        return {"ok": False, "detail": "'mcpServers' is missing or is not a JSON object."}
    entry = servers.get("freecad")
    if not isinstance(entry, dict):
        return {"ok": False, "detail": "The 'freecad' MCP server entry is missing."}

    command = entry.get("command")
    args = entry.get("args")
    cwd = entry.get("cwd")
    if not isinstance(command, str) or not command.strip():
        return {"ok": False, "detail": "The freecad server command is missing or invalid."}
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        return {"ok": False, "detail": "The freecad server args must be a list of strings."}
    if not isinstance(cwd, str) or not cwd.strip():
        return {"ok": False, "detail": "The freecad server working directory is missing or invalid."}

    configured_command = Path(command)
    try:
        command_matches = configured_command.resolve() == python_path
        cwd_matches = Path(cwd).resolve() == root
    except (OSError, RuntimeError):
        command_matches = cwd_matches = False

    if not command_matches:
        return {"ok": False, "detail": f"Claude is configured to use a different Python executable: {command}"}
    if args != ["-m", "freecad_mcp.main"]:
        return {"ok": False, "detail": "The freecad server args should be ['-m', 'freecad_mcp.main']."}
    if not cwd_matches:
        return {"ok": False, "detail": f"Claude is configured with a different project folder: {cwd}"}
    if not python_path.is_file():
        return {"ok": False, "detail": f"Configured Python executable does not exist: {python_path}"}
    return {"ok": True, "detail": "Claude Desktop points to this CADPilot project and virtual environment."}
