"""Add/update the FreeCAD MCP server entry in Claude Desktop's config."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    python_exe = repo_root / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        print(f"Virtual-environment Python not found: {python_exe}", file=sys.stderr)
        return 2

    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("APPDATA is not set. This helper is for Windows.", file=sys.stderr)
        return 2

    config_dir = Path(appdata) / "Claude"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "claude_desktop_config.json"

    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            print(
                f"Claude config contains invalid JSON: {exc}\n"
                f"Fix it before running setup again: {config_path}",
                file=sys.stderr,
            )
            return 3

    if not isinstance(config, dict):
        print("Claude config root must be a JSON object.", file=sys.stderr)
        return 3

    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        print("'mcpServers' must be a JSON object in Claude config.", file=sys.stderr)
        return 3

    servers["freecad"] = {
        "command": str(python_exe),
        "args": ["-m", "freecad_mcp.main"],
        "cwd": str(repo_root),
    }
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Claude Desktop config: {config_path}")
    print(f"Project folder: {repo_root}")
    print(f"Python executable: {python_exe}")
    print("Existing MCP server entries were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
