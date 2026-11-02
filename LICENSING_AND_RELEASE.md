# Before publishing this repository

This package is technically prepared for a public GitHub repository, but the project owner must make the legal release decisions.

## License

The supplied source ZIP did not contain a root-level license file. One source file contains an LGPL-2.1-or-later SPDX header, but that alone does not establish the license for every file in the project.

Before making the repository public:

1. Confirm that you own or have permission to redistribute every source file, icon, and dependency-related asset.
2. Confirm the intended license with the original authors/contributors.
3. Add the chosen license text as `LICENSE` and add appropriate copyright notices.
4. Do not label the whole repository MIT, Apache-2.0, or LGPL without confirming that the choice is authorized.

## Pre-release test checklist

- [ ] Run setup on a clean Windows 10/11 laptop with Python 3.11.
- [ ] Run setup on a clean Windows 10/11 laptop with Python 3.12 or newer.
- [ ] Confirm the add-on appears in FreeCAD 1.0.
- [ ] Confirm the add-on appears in FreeCAD 1.1 if that version is supported.
- [ ] Confirm Claude Desktop lists the `freecad` MCP server.
- [ ] Confirm `check_freecad_connection` reports `connected: true`.
- [ ] Create a box, inspect its bounding box, save the document, and export STEP.
- [ ] Confirm `run_python` returns a disabled message by default.
- [ ] Confirm the setup script preserves other MCP entries in an existing Claude config.
- [ ] Test uninstall and verify other MCP entries remain.
- [ ] Review all tool behaviors and document destructive operations.
- [ ] Add a release tag only after the live tests pass.

## Known validation boundary

The supplied source was statically inspected and Python syntax-compiled. The current execution environment does not include FreeCAD or Claude Desktop, so a real GUI/socket/MCP integration test has not been performed here. Do not claim that the complete stack is tested until the checklist above is completed.
