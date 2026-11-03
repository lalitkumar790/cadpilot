import json
import os
from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "configure_claude.py"


def _run_configurator(tmp_path: Path, initial: str | None):
    appdata = tmp_path / "appdata"
    config_dir = appdata / "Claude"
    config_dir.mkdir(parents=True)
    repo_root = tmp_path / "project"
    python_exe = repo_root / ".venv" / "Scripts" / "python.exe"
    python_exe.parent.mkdir(parents=True)
    python_exe.write_text("test executable placeholder", encoding="utf-8")
    if initial is not None:
        (config_dir / "claude_desktop_config.json").write_text(initial, encoding="utf-8")
    env = os.environ.copy()
    env["APPDATA"] = str(appdata)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, config_dir / "claude_desktop_config.json", config_dir


def test_configurator_preserves_other_servers_and_backs_up_existing_config(tmp_path):
    original = json.dumps({
        "mcpServers": {
            "other": {"command": "node", "args": ["server.js"]},
            "another": {"command": "uvx"},
        },
        "globalShortcut": "Ctrl+Shift+Space",
    })
    result, config_path, config_dir = _run_configurator(tmp_path, original)

    assert result.returncode == 0, result.stderr
    updated = json.loads(config_path.read_text(encoding="utf-8"))
    assert updated["mcpServers"]["other"] == {"command": "node", "args": ["server.js"]}
    assert updated["mcpServers"]["another"] == {"command": "uvx"}
    assert updated["globalShortcut"] == "Ctrl+Shift+Space"
    assert updated["mcpServers"]["freecad"]["args"] == ["-m", "freecad_mcp.main"]
    backups = list(config_dir.glob("claude_desktop_config.backup-*.json"))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text(encoding="utf-8")) == json.loads(original)


def test_configurator_rejects_malformed_json_without_overwriting(tmp_path):
    original = '{"mcpServers":'
    result, config_path, config_dir = _run_configurator(tmp_path, original)

    assert result.returncode == 3
    assert config_path.read_text(encoding="utf-8") == original
    assert not list(config_dir.glob("claude_desktop_config.backup-*.json"))


def test_configurator_rejects_invalid_root_and_mcp_servers(tmp_path):
    for original in (
        '[]',
        'null',
        '"claude-config"',
        '{"mcpServers": []}',
        '{"mcpServers": null}',
    ):
        case = tmp_path / str(len(list(tmp_path.iterdir())))
        case.mkdir()
        result, config_path, _ = _run_configurator(case, original)
        assert result.returncode == 3
        assert config_path.read_text(encoding="utf-8") == original


def test_configurator_creates_config_when_missing(tmp_path):
    result, config_path, config_dir = _run_configurator(tmp_path, None)

    assert result.returncode == 0, result.stderr
    updated = json.loads(config_path.read_text(encoding="utf-8"))
    assert set(updated["mcpServers"]) == {"freecad"}
    assert not list(config_dir.glob("claude_desktop_config.backup-*.json"))


def test_repeated_configuration_keeps_distinct_backups_and_no_temp_files(tmp_path):
    original = json.dumps({"mcpServers": {"other": {"command": "node"}}})
    result, config_path, config_dir = _run_configurator(tmp_path, original)
    assert result.returncode == 0, result.stderr

    # A second invocation backs up the first generated config rather than
    # overwriting the first backup when both runs happen within one second.
    appdata = config_dir.parent
    repo_root = tmp_path / "project"
    env = os.environ.copy()
    env["APPDATA"] = str(appdata)
    second = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert second.returncode == 0, second.stderr
    backups = list(config_dir.glob("claude_desktop_config.backup-*.json"))
    assert len(backups) == 2
    assert not list(config_dir.glob("claude_desktop_config.*.tmp"))
