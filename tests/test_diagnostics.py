import json

from freecad_mcp.diagnostics import inspect_claude_config


def write_config(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def valid_config(python, root):
    return {
        "mcpServers": {
            "freecad": {
                "command": str(python),
                "args": ["-m", "freecad_mcp.main"],
                "cwd": str(root),
            },
            "another-server": {"command": "preserve-me"},
        }
    }


def test_valid_claude_config_passes(tmp_path):
    root = tmp_path / "cadpilot"
    root.mkdir()
    python = root / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.write_text("python", encoding="utf-8")
    config = tmp_path / "claude_desktop_config.json"
    write_config(config, valid_config(python, root))

    result = inspect_claude_config(config, root, python)

    assert result["ok"] is True


def test_missing_config_fails_with_actionable_detail(tmp_path):
    result = inspect_claude_config(tmp_path / "missing.json", tmp_path, tmp_path / "python.exe")
    assert result["ok"] is False
    assert "not found" in result["detail"]


def test_invalid_json_fails(tmp_path):
    config = tmp_path / "claude_desktop_config.json"
    config.write_text("{broken", encoding="utf-8")
    result = inspect_claude_config(config, tmp_path, tmp_path / "python.exe")
    assert result["ok"] is False
    assert "valid Claude config" in result["detail"]


def test_missing_freecad_entry_fails(tmp_path):
    config = tmp_path / "claude_desktop_config.json"
    write_config(config, {"mcpServers": {}})
    result = inspect_claude_config(config, tmp_path, tmp_path / "python.exe")
    assert result["ok"] is False
    assert "entry is missing" in result["detail"]


def test_wrong_python_executable_fails(tmp_path):
    root = tmp_path / "cadpilot"
    root.mkdir()
    expected = root / ".venv" / "Scripts" / "python.exe"
    actual = tmp_path / "other-python.exe"
    expected.parent.mkdir(parents=True)
    expected.write_text("python", encoding="utf-8")
    actual.write_text("python", encoding="utf-8")
    config = tmp_path / "claude_desktop_config.json"
    write_config(config, valid_config(actual, root))

    result = inspect_claude_config(config, root, expected)

    assert result["ok"] is False
    assert "different Python" in result["detail"]


def test_wrong_arguments_or_working_directory_fail(tmp_path):
    root = tmp_path / "cadpilot"
    root.mkdir()
    python = root / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.write_text("python", encoding="utf-8")
    config = tmp_path / "claude_desktop_config.json"
    value = valid_config(python, tmp_path)
    write_config(config, value)

    result = inspect_claude_config(config, root, python)

    assert result["ok"] is False
    assert "different project folder" in result["detail"]


def test_wrong_module_arguments_fail(tmp_path):
    root = tmp_path / "cadpilot"
    root.mkdir()
    python = root / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.write_text("python", encoding="utf-8")
    config = tmp_path / "claude_desktop_config.json"
    value = valid_config(python, root)
    value["mcpServers"]["freecad"]["args"] = ["-m", "wrong.module"]
    write_config(config, value)

    result = inspect_claude_config(config, root, python)

    assert result["ok"] is False
    assert "args should be" in result["detail"]


def test_missing_configured_python_fails(tmp_path):
    root = tmp_path / "cadpilot"
    root.mkdir()
    python = root / ".venv" / "Scripts" / "python.exe"
    config = tmp_path / "claude_desktop_config.json"
    write_config(config, valid_config(python, root))

    result = inspect_claude_config(config, root, python)

    assert result["ok"] is False
    assert "does not exist" in result["detail"]
