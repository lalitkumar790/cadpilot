# CADPilot — AI-Powered FreeCAD Assistant
The script will:

- Verify that Python 3.11+ is available.
- Create a local virtual environment at `.venv`.
- Install the project and its MCP dependencies into that environment.
- Copy the `AICopilot` folder into the FreeCAD user `Mod` directory. It uses `%APPDATA%\FreeCAD\Mod` for FreeCAD 1.0 and checks for a version-specific folder such as `%APPDATA%\FreeCAD\v1-1\Mod` for FreeCAD 1.1+.
- Back up an existing `AICopilot` folder before replacing it.
- Add/update only the `freecad` entry in Claude Desktop's config, preserving other MCP server entries.
- Use the virtual environment's exact `python.exe` path, so Claude does not depend on the Windows PATH.

If the script reports that Python 3.11 is missing, install it and run the script again. Do not use FreeCAD's bundled Python as the MCP environment.

If your FreeCAD user-data directory is non-standard, run `App.getUserAppDataDir()` in FreeCAD's Python console and pass its existing `Mod` folder explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1 -FreeCADModDirectory "C:\FULL\PATH\TO\FreeCAD\Mod"
```

### Step 3 — Start FreeCAD

1. Launch FreeCAD.
2. If FreeCAD was already open during installation, close it and open it again.
3. Open **View → Panels → Python console** if you want to see startup messages.
4. Look for a message similar to `CADPilot ready` or `AI Socket Server started`.
5. You may use any workbench. The service starts when FreeCAD loads; the AI Copilot workbench is an optional management interface.

If the workbench is not listed or the service fails to start, see [Troubleshooting](#troubleshooting).

### Step 4 — Restart Claude Desktop

Completely quit Claude Desktop (not just close its window), then reopen it.

To verify that the MCP server is available:

1. Open a new Claude Desktop conversation.
2. Open the **Connectors / tools** menu (the exact location can vary by Claude Desktop version).
3. Look for the `freecad` server and its tools.
4. Ask Claude:

   `Call check_freecad_connection and tell me whether FreeCAD is connected.`

You should see `connected: true`.

### Step 5 — Run a safe first CAD test

In Claude Desktop, send:

> In FreeCAD, create a new box with length 40 mm, width 30 mm, and height 20 mm. Give it the name StudentTestBox. Fit the view and tell me the resulting object name. Do not delete or overwrite any existing object.

Check that the box appears in FreeCAD. Then ask:

> List all objects in the current FreeCAD document and report the bounding box of StudentTestBox.

Save your document manually or ask Claude to save it.

## What folder goes where?

The installer does this automatically. These are common locations on Windows; FreeCAD 1.1+ may use a version-specific folder. To confirm the active location, open FreeCAD's Python console and run `App.getUserAppDataDir()`, then append `Mod` to the returned path.

| Item | Location |
|---|---|
| Project repository | `C:\Users\YOUR_NAME\Documents\cadpilot` |
| Python virtual environment | `PROJECT_FOLDER\.venv` |
| FreeCAD workbench | `%APPDATA%\FreeCAD\Mod\AICopilot` (FreeCAD 1.0) or `%APPDATA%\FreeCAD\v1-1\Mod\AICopilot` (common FreeCAD 1.1 layout) |
| Claude Desktop config | `%APPDATA%\Claude\claude_desktop_config.json` |

**Do not copy the entire repository into FreeCAD's `Mod` folder.** Only the `AICopilot` folder belongs there. The Python MCP package stays in the project folder.

## Manual setup (if the installer does not work)

Open PowerShell in the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

Copy the FreeCAD workbench:

```powershell
$mod = Join-Path $env:APPDATA "FreeCAD\Mod"
New-Item -ItemType Directory -Force -Path $mod | Out-Null
Copy-Item -Recurse -Force .\AICopilot (Join-Path $mod "AICopilot")
```

Then open Claude Desktop → **Settings → Developer → Edit Config**. Add the following server entry to the existing JSON. Replace both example paths with the real project path. Do not delete other entries already under `mcpServers`.

```json
{
  "mcpServers": {
    "freecad": {
      "command": "C:/Users/YOUR_NAME/Documents/cadpilot/.venv/Scripts/python.exe",
      "args": ["-m", "freecad_mcp.main"],
      "cwd": "C:/Users/YOUR_NAME/Documents/cadpilot"
    }
  }
}
```

Save the file and completely restart Claude Desktop.

## Example things to ask Claude

See [`SAMPLE_PROMPTS.md`](SAMPLE_PROMPTS.md) for a longer list. Start with:

- "Create a 60 × 40 × 10 mm base plate and a 10 mm diameter hole through its centre."
- "Create a cylinder of radius 8 mm and height 50 mm, then place it at X=30 mm."
- "List all objects and report their bounding-box dimensions."
- "Create two overlapping boxes and perform a Boolean cut."
- "Set the view to isometric and fit all objects."
- "Export the selected object as a STEP file to my Documents folder."

For operations that need edge/face selection (fillet, chamfer, hole, shell), Claude may ask you to select geometry in FreeCAD and then continue the operation.

## Security and safe use

- The MCP bridge is designed for a **single user's local computer**. Do not expose its socket port or Unix socket to the internet or a campus network.
- The FreeCAD socket service does not implement user authentication. Its Windows TCP listener binds to localhost; do not change that to `0.0.0.0`.
- CAD tools can create, move, hide, export, and delete geometry. Save important documents before experimenting.
- **Arbitrary Python execution (`run_python`) is disabled by default in this student build.** It can run any Python code in FreeCAD's process and may read, modify, or delete files accessible to your account. Do not enable it for routine coursework.
- Never paste untrusted scripts into `run_python`. Never enable it just because Claude asks.
- AI-generated CAD models may be dimensionally or structurally wrong. Verify critical dimensions, constraints, tolerances, and manufacturing suitability yourself.
- This software is an educational project, not a certified engineering tool.

### Optional: enable `run_python` (advanced users only)

Only do this if you understand the risks. Open `%APPDATA%\Claude\claude_desktop_config.json` and add the `env` property to the `freecad` entry:

```json
"env": {
  "FREECAD_MCP_ENABLE_PYTHON_EXEC": "1"
}
```

Keep the rest of the entry unchanged, save, and restart Claude Desktop. Remove this environment setting to disable it again.

## Troubleshooting

### Claude does not show the FreeCAD tools

1. Confirm Claude Desktop is fully quit and restarted.
2. Open Settings → Developer and inspect the MCP server status/logs.
3. Confirm the `freecad` entry exists under `mcpServers`.
4. Confirm `command` points to the `.venv\Scripts\python.exe` inside this project.
5. Confirm `cwd` points to the project root.
6. Run this in PowerShell from the project folder:

   ```powershell
   .\.venv\Scripts\python.exe -c "import mcp; print('MCP SDK import OK')"
   ```

### `check_freecad_connection` says not connected

1. Start FreeCAD.
2. Confirm the `AICopilot` folder exists at `%APPDATA%\FreeCAD\Mod\AICopilot`.
3. Restart FreeCAD after installing/updating the workbench.
4. Check the FreeCAD Python console for `AI Socket Server started`.
5. Confirm no other process is occupying TCP port `23456`.
6. Run `Test-NetConnection 127.0.0.1 -Port 23456` in PowerShell. `TcpTestSucceeded` should be `True` while FreeCAD is running.

### Python version error

The MCP Python SDK v2 requires Python 3.11 or newer. Run:

```powershell
py -0p
py -3.11 --version
```

Install Python 3.11+ if necessary, then rerun the setup script.

### `ModuleNotFoundError: No module named 'freecad_mcp'`

The MCP package was not installed into the interpreter Claude is launching. From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

Then restart Claude Desktop.

### FreeCAD does not show AI Copilot

- Verify the folder nesting is exactly `...\FreeCAD\Mod\AICopilot\Init.py` and `...\AICopilot\InitGui.py`.
- Do not accidentally create `...\Mod\AICopilot\AICopilot\Init.py`.
- Restart FreeCAD completely.
- Check FreeCAD's Python console for import errors.

### The MCP server starts but tools return socket errors

FreeCAD must be open and its AI Copilot service must have started. The MCP server alone does not create or display CAD geometry.

## Uninstall

1. Close FreeCAD and Claude Desktop.
2. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_windows.ps1
   ```

3. The script removes the FreeCAD add-on and the `freecad` MCP config entry. It does not delete your CAD documents or the project folder.

## macOS and Linux

The bridge contains Unix-domain-socket support, but this student release's automated installer and step-by-step validation target Windows first. For macOS/Linux, the manual setup is:

1. Install FreeCAD 1.0+, Python 3.11+, and Claude Desktop where supported by your OS.
2. Copy `AICopilot` into the FreeCAD user `Mod` directory:
   - macOS: `~/Library/Preferences/FreeCAD/Mod/AICopilot`
   - Linux: `~/.local/share/FreeCAD/Mod/AICopilot`
3. Create a virtual environment in the project root, install with `python -m pip install -e .`, and configure Claude Desktop with the absolute path to that environment's Python executable.
4. Restart FreeCAD and Claude Desktop.

The Unix socket path is `/tmp/freecad_mcp.sock`. macOS/Linux packaging has not yet been validated end-to-end; please report issues with OS version, FreeCAD version, Python version, and Claude Desktop logs.

## Developer checks

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

The included tests check MCP tool registration and graceful handling when FreeCAD is not running. They do **not** replace a live FreeCAD/Claude integration test.

## Project layout

```text
AICopilot/                 FreeCAD-side workbench and local socket service
freecad_mcp/               Python MCP server package
  tools/                   CAD tools exposed to Claude
  transport/               Local socket client
scripts/                   Windows setup/configuration/uninstall helpers
tests/                     MCP smoke tests
README.md                  This guide
SAMPLE_PROMPTS.md          Student examples
SECURITY.md                Security notes and reporting
```

## Contributing

Bug reports and improvements are welcome. Please include OS, FreeCAD version, Python version, Claude Desktop version, and relevant logs. Do not include private CAD files or personal data in public issues.
=======
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
>>>>>>> 223b66b062578a32115cbd39a5feafc845db8b2a
