"""Add/update the FreeCAD MCP server entry in Claude Desktop's config."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from datetime import datetime
import tempfile


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

    if config_path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_path = config_path.with_name(f"claude_desktop_config.backup-{stamp}.json")
        backup_path.write_bytes(config_path.read_bytes())
        print(f"Backed up previous Claude config: {backup_path}")

    # Create the temporary file beside the destination so os.replace stays
    # on the same volume and is atomic. Unique names avoid collisions between
    # concurrent setup runs; cleanup prevents abandoned partial config files.
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix="claude_desktop_config.",
            suffix=".tmp",
            dir=config_dir,
            delete=False,
        ) as temp_file:
            temp_name = temp_file.name
            temp_file.write(json.dumps(config, indent=2) + "\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_name, config_path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass

    print(f"Updated Claude Desktop config: {config_path}")
    print(f"Project folder: {repo_root}")
    print(f"Python executable: {python_exe}")
    print("Existing MCP server entries were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
