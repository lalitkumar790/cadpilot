# CADPilot — FreeCAD + Claude Desktop

CADPilot connects **Claude Desktop** to **FreeCAD** through a local MCP server. Ask Claude to create, inspect, and modify CAD models using natural language.

> **Target:** Windows 10/11. The maintainer has tested the integration on a Windows laptop. The included automated tests are smoke tests; every student's FreeCAD/Claude version combination may differ.

## 1. Install these three things

1. **FreeCAD 1.0 or newer:** https://www.freecad.org/downloads.php
2. **Python 3.11 or newer (64-bit):** https://www.python.org/downloads/windows/ — enable **Add Python to PATH** during setup.
3. **Claude Desktop:** https://claude.com/download — install, sign in, then quit it before running the CADPilot installer.

Git is optional. Node.js, Docker, and a separate API key are not required for this local setup.

## 2. Download CADPilot

1. Open this repository on GitHub and choose **Code → Download ZIP**.
2. Extract it to a normal folder, for example `C:\Users\YOUR_NAME\Documents\cadpilot`.
3. Open that folder. You should see `README.md`, `AICopilot`, `freecad_mcp`, and `scripts` directly inside it.

Do not put the whole repository inside FreeCAD's `Mod` folder.

## 3. Run the setup

1. Close **FreeCAD** and **Claude Desktop**.
2. Open the extracted `cadpilot` folder in File Explorer.
3. Right-click an empty area and choose **Open in Terminal**.
4. In PowerShell, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

The installer creates a Python environment in `.venv`, installs CADPilot's dependencies, copies only the `AICopilot` add-on into FreeCAD's user `Mod` folder, and adds the `freecad` MCP server to Claude Desktop's configuration. Existing Claude MCP entries are preserved, and the previous Claude config is backed up before it is changed.

### If the add-on installs to the wrong FreeCAD profile

Open FreeCAD → View → Panels → Python console and run:

```python
App.getUserAppDataDir()
```

Use the returned directory plus `Mod` as the installer path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1 -FreeCADModDirectory "C:\PATH\TO\FreeCAD\Mod"
```

Replace the example path with the actual `Mod` folder.

## 4. Start and connect

1. Open FreeCAD. The CADPilot socket service starts when the add-on loads. If FreeCAD was open during installation, restart it.
2. Completely quit Claude Desktop from its tray/menu, then reopen it.
3. In Claude Desktop, open its developer/MCP tools view and check that the `freecad` server is running. Menu wording can vary by version.
4. Ask Claude: **“Call `check_freecad_connection` and tell me whether FreeCAD is connected.”**
5. When connected, try:

   > Create a new box in FreeCAD with length 40 mm, width 30 mm, and height 20 mm. Name it StudentTestBox. Do not delete or overwrite existing objects.

You should see the box in FreeCAD. Save your document manually.

## 5. What gets installed where?

| Component | Location |
|---|---|
| CADPilot project and MCP server | The folder where you extracted the repository |
| Python environment | `cadpilot\.venv` |
| FreeCAD add-on | FreeCAD user data folder → `Mod\AICopilot` |
| Claude configuration | `%APPDATA%\Claude\claude_desktop_config.json` |

Only `AICopilot` is copied into FreeCAD. The `freecad_mcp` package stays in the project folder and runs from `.venv`.

## 6. Example prompts

- “Create a 60 × 40 × 10 mm base plate and add a 10 mm hole through its centre.”
- “Create a cylinder with radius 8 mm and height 50 mm. Place it at X = 30 mm.”
- “List the objects in the document and report their bounding-box dimensions.”
- “Create two boxes and perform a Boolean cut.”
- “Set an isometric view and fit all objects.”
- “Export the selected object as a STEP file.”

More examples: [SAMPLE_PROMPTS.md](SAMPLE_PROMPTS.md).

## Troubleshooting

**Claude does not show the FreeCAD tools**
- Fully quit and reopen Claude Desktop.
- Check Claude Desktop's developer/MCP status and logs.
- Confirm the `freecad` entry exists in `%APPDATA%\Claude\claude_desktop_config.json`.
- Confirm its `command` points to this project's `.venv\Scripts\python.exe`.

**Claude says FreeCAD is not connected**
- Start or restart FreeCAD.
- Confirm `AICopilot` is inside the active FreeCAD profile's `Mod` folder.
- In PowerShell, run `Test-NetConnection 127.0.0.1 -Port 23456` while FreeCAD is open. `TcpTestSucceeded` should be `True`.

**Python or package error**

```powershell
py -0p
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -c "import mcp; print('MCP SDK OK')"
```

If it still fails, report your Windows, FreeCAD, Python, and Claude Desktop versions with the error. Do not post private CAD files or personal data.

## Safety

- CADPilot is intended for one user's local computer. Do not expose its socket (`localhost:23456`) to the internet or campus network.
- Save a copy of important CAD documents before experimenting. Some tools can modify or delete geometry.
- Arbitrary Python execution is **disabled by default at both the MCP and FreeCAD ends**. Enabling it requires `FREECAD_MCP_ENABLE_PYTHON_EXEC=1` in both process environments and restarting both applications. Do not enable it for normal coursework; it can execute code inside FreeCAD with your user permissions.
- AI-generated geometry is not engineering certification. Check dimensions, constraints, clearances, tolerances, and manufacturability yourself.
- Read [SECURITY.md](SECURITY.md) before use.

## Uninstall

Close FreeCAD and Claude Desktop, then run PowerShell from the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_windows.ps1
```

This removes the CADPilot add-on and the `freecad` entry from Claude Desktop. It does not delete CAD documents, the project folder, or the Python environment.

## Developer tests

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

These are smoke tests, not a substitute for testing with a running FreeCAD GUI and Claude Desktop.

## Project structure

- `AICopilot/` — FreeCAD workbench and local socket service
- `freecad_mcp/` — MCP server and CAD tools
- `scripts/` — Windows setup, Claude configuration, and uninstall helpers
- `tests/` — automated smoke tests
- `SAMPLE_PROMPTS.md` — student prompt examples
- `SECURITY.md` — security guidance
