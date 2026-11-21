# Use CADPilot from the repository with GitHub Copilot Free

CADPilot can be configured from this repository itself, without copying
an absolute Windows path into VS Code settings.

## Requirements

- FreeCAD with the existing CADPilot AICopilot add-on installed.
- Python 3.11+ and CADPilot's editable Python installation.
- VS Code with GitHub Copilot signed in. A Copilot account with remaining
  free usage allowance, and an eligible agent/MCP experience.
- Open the **whole repository folder** as your VS Code workspace.

## Set up on Windows

In the terminal opened at the cloned CADPilot repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

If the existing `.venv` is set up already, skip the first command.

For the workspace-root `.mcp.json` to run the venv's Python,
configure the environment used to launch VS Code so that `python`
resolves to `.venv\Scripts\python.exe`. The easiest option is to
activate the venv in a PowerShell terminal and launch VS Code from there:

```powershell
.\.venv\Scripts\Activate.ps1
code .
```

**Important:** VS Code already running may reuse an existing process and
inherit its environment instead. Close old VS Code processes if needed, or
choose a Python interpreter/environment recognized by your Copilot host.
The MCP runtime may use a different environment from the integrated terminal.

For a machine-specific fallback, create your own **untracked** Copilot
global config at `~/.copilot/mcp-config.json` and set the `command`
to the absolute path of your venv Python, with the same args:

```json
{
  "mcpServers": {
    "cadpilot": {
      "type": "stdio",
      "command": "C:\\path\\to\\cadpilot\\.venv\\Scripts\\python.exe",
      "args": ["-m", "freecad_mcp.main"],
      "tools": ["*"]
    }
  }
}
```

That machine-specific file must NOT be committed to the repository.

## Using the repo configuration

1. Start FreeCAD and verify the CADPilot add-on is running.
2. Open this repo folder in VS Code.
3. Open Copilot Chat, choose the Copilot agent and an available GPT model.
4. Open **Chat: Open Customizations → MCP Servers** and locate
   `cadpilot` loaded from the workspace-root `.mcp.json`.
5. Enable/start the server and approve only tools you intend to use.
6. Ask: "Use cadpilot to call check_freecad_connection. Do not modify CAD."
7. After a successful connection check, create a *new* test document.

The new `.mcp.json` uses Copilot's current portable format:
`mcpServers`, not the older editor-only `.vscode/mcp.json`
schema (`servers`). These two schemas are not interchangeable.

## Security

- Inspect MCP tools before authorizing writes, deletion, or exports.
- The underlying FreeCAD socket stays bound to `127.0.0.1:23456`.
- Leave `FREECAD_MCP_ENABLE_PYTHON_EXEC` disabled.
- Do not commit private customer CAD, machine-specific absolute paths,
  access tokens, or credentials.
- GitHub Copilot Free AI usage is limited; availability of specific GPT
  models and agent capabilities may change.

Official VS Code reference:
https://code.visualstudio.com/docs/agents/reference/mcp-configuration
