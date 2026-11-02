"""Tests for non-destructive CAD export path validation."""
import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).parents[1] / "AICopilot" / "export_validation.py"
_SPEC = importlib.util.spec_from_file_location("cadpilot_export_validation", _PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate_export_path = _MODULE.validate_export_path


def test_accepts_new_step_and_stl_targets(tmp_path):
    assert validate_export_path(str(tmp_path / "part.step"), {".step", ".stp"}).endswith("part.step")
    assert validate_export_path(str(tmp_path / "part.stl"), {".stl"}).endswith("part.stl")


@pytest.mark.parametrize("filename", ["", "  ", "part.obj", "bad\x00name.step", "bad\nname.step"])
def test_rejects_invalid_names(tmp_path, filename):
    with pytest.raises(ValueError):
        validate_export_path(str(tmp_path) + "/" + filename, {".step", ".stp"})


def test_rejects_missing_directory(tmp_path):
    with pytest.raises(ValueError, match="directory does not exist"):
        validate_export_path(str(tmp_path / "missing" / "part.step"), {".step"})


def test_refuses_to_overwrite_existing_file(tmp_path):
    target = tmp_path / "existing.step"
    target.write_text("keep me")
    with pytest.raises(ValueError, match="already exists"):
        validate_export_path(str(target), {".step"})
    assert target.read_text() == "keep me"


def test_refuses_directory_as_export_target(tmp_path):
    target = tmp_path / "folder.stl"
    target.mkdir()
    with pytest.raises(ValueError, match="directory"):
        validate_export_path(str(target), {".stl"})


def test_rejects_extremely_long_paths(tmp_path):
    with pytest.raises(ValueError, match="4096-character"):
        validate_export_path("x" * 4097 + ".step", {".step"})
