"""Tests for validation at the MCP-to-FreeCAD dispatch boundary."""
import json

import pytest

from freecad_mcp import server


def test_dispatch_rejects_nan_before_socket(monkeypatch):
    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("socket must not be called")

    monkeypatch.setattr(server, "send_command", fail_if_called)
    result = json.loads(server.dispatch("create_box", length=float("nan")))
    assert "finite" in result["error"]
    assert called is False


def test_dispatch_rejects_deeply_nested_values(monkeypatch):
    monkeypatch.setattr(
        server, "send_command",
        lambda *args, **kwargs: pytest.fail("socket must not be called"),
    )
    nested = []
    cursor = nested
    for _ in range(34):
        child = []
        cursor.append(child)
        cursor = child
    result = json.loads(server.dispatch("test_tool", value=nested))
    assert "nesting depth" in result["error"]


def test_dispatch_rejects_oversized_payload(monkeypatch):
    monkeypatch.setattr(
        server, "send_command",
        lambda *args, **kwargs: pytest.fail("socket must not be called"),
    )
    original = server.DEFAULT_CONFIG
    class SmallConfig:
        max_message_bytes = 32
    monkeypatch.setattr(server, "DEFAULT_CONFIG", SmallConfig())
    result = json.loads(server.dispatch("create_box", name="a" * 100))
    assert "message limit" in result["error"]
    monkeypatch.setattr(server, "DEFAULT_CONFIG", original)


def test_dispatch_passes_valid_arguments(monkeypatch):
    monkeypatch.setattr(
        server, "send_command",
        lambda name, args, config: {"tool": name, "args": args},
    )
    result = json.loads(server.dispatch("create_box", length=12.5, name="Bracket"))
    assert result == {"tool": "create_box", "args": {"length": 12.5, "name": "Bracket"}}
