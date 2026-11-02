"""Security policy tests that do not require a running FreeCAD instance."""
from __future__ import annotations

import importlib.util
from pathlib import Path


_POLICY_PATH = Path(__file__).parents[1] / "AICopilot" / "security_policy.py"
_SPEC = importlib.util.spec_from_file_location("cadpilot_security_policy", _POLICY_PATH)
_POLICY = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_POLICY)


def test_python_execution_is_disabled_when_unset(monkeypatch):
    monkeypatch.delenv("FREECAD_MCP_ENABLE_PYTHON_EXEC", raising=False)
    assert _POLICY.python_execution_enabled() is False


def test_python_execution_requires_explicit_truthy_opt_in(monkeypatch):
    for value in ("", "0", "false", "no", "off", "enabled"):
        monkeypatch.setenv("FREECAD_MCP_ENABLE_PYTHON_EXEC", value)
        assert _POLICY.python_execution_enabled() is False


def test_python_execution_accepts_explicit_opt_in(monkeypatch):
    for value in ("1", "true", "TRUE", "yes"):
        monkeypatch.setenv("FREECAD_MCP_ENABLE_PYTHON_EXEC", value)
        assert _POLICY.python_execution_enabled() is True
