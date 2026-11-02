"""Filesystem path policy for explicit CAD exports (no FreeCAD dependency)."""
import os


def validate_export_path(filename, allowed_extensions):
    """Return a canonical export path, rejecting ambiguous or destructive targets."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename must be a non-empty path")
    if len(filename) > 4096:
        raise ValueError("filename exceeds the 4096-character path limit")
    if any(ord(char) < 32 or ord(char) == 127 for char in filename):
        raise ValueError("filename must not contain control characters")
    extension = os.path.splitext(filename)[1].lower()
    if extension not in set(allowed_extensions):
        expected = " or ".join(sorted(allowed_extensions))
        raise ValueError(f"filename must end in {expected}")
    expanded = os.path.abspath(os.path.expanduser(filename))
    parent = os.path.realpath(os.path.dirname(expanded))
    if not os.path.isdir(parent):
        raise ValueError(f"export directory does not exist: {parent}")
    path = os.path.join(parent, os.path.basename(expanded))
    if os.path.isdir(path):
        raise ValueError("export target is a directory")
    if os.path.lexists(path):
        raise ValueError("export target already exists; choose a new filename to avoid overwriting it")
    return path
