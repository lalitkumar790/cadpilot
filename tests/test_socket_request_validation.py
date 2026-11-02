"""Tests for strict FreeCAD socket command validation."""
import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parents[1] / "AICopilot" / "request_validation.py"
_SPEC = importlib.util.spec_from_file_location("cadpilot_request_validation", _MODULE_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate_command_payload = _MODULE.validate_command_payload


def test_valid_command_defaults_args():
    assert validate_command_payload({"tool": "fit_all"}) == {"tool": "fit_all", "args": {}}


def test_valid_command_preserves_arguments():
    command = {"tool": "create_box", "args": {"length": 12, "label": "part"}}
    assert validate_command_payload(command) == command


@pytest.mark.parametrize("command", [
    [],
    "create_box",
    None,
    {"tool": "Create_Box"},
    {"tool": "create-box"},
    {"tool": ""},
    {"tool": "create_box", "args": []},
    {"tool": "create_box", "extra": True},
])
def test_rejects_invalid_command_shapes(command):
    with pytest.raises(ValueError):
        validate_command_payload(command)


def test_rejects_non_finite_values():
    with pytest.raises(ValueError, match="NaN or infinity"):
        validate_command_payload({"tool": "create_box", "args": {"length": float("nan")}})


def test_rejects_deeply_nested_arguments():
    value = "leaf"
    for _ in range(34):
        value = [value]
    with pytest.raises(ValueError, match="nesting depth"):
        validate_command_payload({"tool": "create_box", "args": {"payload": value}})


def test_rejects_oversized_strings_and_collections():
    with pytest.raises(ValueError, match="string exceeds"):
        validate_command_payload({"tool": "run_command", "args": {"command": "x" * 65537}})
    with pytest.raises(ValueError, match="10000-item"):
        validate_command_payload({"tool": "run_command", "args": {"items": [0] * 10001}})
