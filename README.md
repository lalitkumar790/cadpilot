# CADPilot — AI-Powered FreeCAD Assistant

CADPilot connects Claude Desktop to FreeCAD through the Model Context Protocol (MCP), allowing students and engineers to create, modify, inspect, and export CAD models using natural-language instructions.

> **Maintainer-tested:** The project has been tested successfully on the maintainer’s Windows laptop with FreeCAD and Claude Desktop. This repository packages that working setup with student-focused installation instructions. Windows is the documented target platform; other operating systems may require manual adaptation.

## Quick start for Windows

Install [FreeCAD 1.0+](https://www.freecad.org/downloads.php), [Python 3.11+ 64-bit](https://www.python.org/downloads/windows/) (enable **Add python.exe to PATH**) and [Claude Desktop](https://claude.com/download). Git for Windows is optional.

Download this repository using **Code → Download ZIP**, extract it to `C:\Users\YOUR_NAME\Documents\cadpilot`, then open PowerShell in that folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

The setup script creates a virtual environment, installs the Python MCP server, copies only `AICopilot` into FreeCAD’s user `Mod` folder, and configures Claude Desktop while preserving existing MCP entries. Restart FreeCAD and Claude Desktop. Ask Claude to run `check_freecad_connection`.

Try: “Create a 40 × 30 × 20 mm box named FirstCADPilotBox and report its dimensions.” Inspect the result in FreeCAD.

## Student CAD workflow

1. Describe the engineering component, purpose, constraints, and approximate dimensions.
2. Ask Claude for a modelling plan and assumptions before generating geometry.
3. Build incrementally: base geometry, sketches, pockets, holes, fillets, chamfers, and other features.
4. Inspect dimensions, placements, geometry, and feature history after each major operation.
5. Iterate with specific changes; save the editable `.FCStd` project and export STEP/STL as needed.
6. Independently validate fits, clearances, tolerances, wall thickness, and manufacturability. AI-generated geometry is not engineering certification.

See `SAMPLE_PROMPTS.md`, `SECURITY.md`, and `LICENSING_AND_RELEASE.md` for more guidance.

## Important paths (Windows)

- Project: `C:\Users\YOUR_NAME\Documents\cadpilot`
- Python environment: `cadpilot\.venv`
- FreeCAD workbench: FreeCAD user `Mod\AICopilot`
- Claude config: `%APPDATA%\Claude\claude_desktop_config.json`

**Do not copy the entire repository into FreeCAD’s `Mod` folder.** Keep the project in Documents; the setup script copies only `AICopilot` into `Mod`.

The setup script configures Claude automatically. The server executable must reference your own `cadpilot\.venv\Scripts\python.exe`, not another student’s absolute path. An example is in `config/claude_desktop_config.example.json`.

## Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_windows.ps1
```

## Troubleshooting

- No tools in Claude: fully quit and relaunch Claude Desktop; check the MCP config and `.venv\Scripts\python.exe` path.
- Connection fails: keep FreeCAD open and check that the workbench/socket service started in the FreeCAD report/console.
- Python not found: reinstall Python 3.11+ 64-bit with PATH enabled, then rerun setup.
- Only `AICopilot` belongs in FreeCAD’s `Mod` directory; `freecad_mcp` and `.venv` stay in the repository.

Windows is the documented setup. macOS/Linux may require manual adaptation. Bug reports should include OS, FreeCAD/Python/Claude versions, and the exact error. Do not upload sensitive project files.

Review `LICENSING_AND_RELEASE.md` for licensing and attribution requirements before redistribution.
