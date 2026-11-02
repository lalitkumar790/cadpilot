# Changelog — v3.0.0 (MCP SDK migration)

## Why

The repo's `working_bridge.py` targeted an old MCP SDK API:

```python
from mcp.server import NotificationOptions, Server
server = Server("freecad")

@server.list_tools()
async def handle_list_tools(): ...

@server.call_tool()
async def handle_call_tool(name, arguments): ...

async with mcp.server.stdio.stdio_server() as (r, w):
    await server.run(r, w, InitializationOptions(...))
```

Against `mcp==2.0.0` this raises `AttributeError: 'Server' object has no
attribute 'list_tools'` — that low-level decorator style was removed.
The current SDK exposes `mcp.server.mcpserver.MCPServer` (the successor
to the earlier `FastMCP` class) with a `@server.tool()` decorator that
auto-generates JSON schemas from Python type hints, and a synchronous
`server.run(transport="stdio")` that manages its own event loop.

## What changed

- **Removed**: `working_bridge.py`'s monolithic `main()` with manual
  `list_tools`/`call_tool` handlers, `NotificationOptions`,
  `InitializationOptions`, and manual `stdio_server()` context manager.
- **Added**: `freecad_mcp/` package using `MCPServer` + `@mcp_server.tool()`.
- **Replaced** the four smart-dispatcher tools (`part_operations`,
  `partdesign_operations`, `view_control`, `execute_python`) with **45
  explicit tools** (`create_box`, `boolean_cut`, `fillet`,
  `capture_screenshot`, `export_step`, ...), each with proper type-hinted
  parameters instead of a single free-form `operation` enum + a bag of
  optional fields.
- **Preserved, unchanged**:
  - The socket wire protocol to `AICopilot/socket_server.py`
    (`{"tool": ..., "args": {...}}` over TCP on Windows / Unix socket
    elsewhere) — `freecad_mcp/transport/socket_client.py` is a direct
    port of the original `send_to_freecad()`, not a rewrite of the
    protocol.
  - The interactive-selection workflow (`awaiting_selection` →
    `continue_selection`) — reimplemented faithfully in
    `freecad_mcp/server.py::_format_selection_request`.
  - Every explicit tool_name FreeCAD's socket server already understood
    (`create_box`, `fillet_edges`, `get_screenshot`, etc.) — new tools
    map directly onto these; no FreeCAD-side code was touched.
- **Added** `export_step` / `export_stl` as first-class tools (previously
  only reachable via `execute_python`).
- **Added** a smoke-test suite (`tests/test_server.py`) verifying tool
  registration and that connection failures return JSON errors instead
  of raising exceptions that would crash the stdio server.

## Verification performed

Run against the actual installed `mcp==2.0.0` package (not assumed from
docs):

- ✅ `import freecad_mcp` succeeds, no import errors
- ✅ `freecad_mcp.tools` registers **45** tools on `mcp_server`
      (confirmed via `await mcp_server.list_tools()`)
- ✅ `python -m freecad_mcp.main` starts over stdio and exits cleanly
      (tested with a 3s timeout + EOF stdin, no exceptions)
- ✅ `pytest tests/` — 2/2 passed, including confirming `dispatch()`
      returns a JSON error (not an exception) when FreeCAD's socket is
      unreachable
- ✅ No remaining references to `list_tools()`, `call_tool()`,
      `NotificationOptions`, `InitializationOptions`, or
      `mcp.server.stdio.stdio_server` anywhere in `freecad_mcp/`
      (grep-verified)
- ⚠️ Not verified in this environment: an actual live connection to a
  running FreeCAD instance (this sandbox has no FreeCAD/GUI). The
  socket protocol itself is unchanged from the original working
  bridge, and `AICopilot/` is carried over byte-for-byte, so behavior
  once connected should match the original bridge's behavior — but
  please do a live smoke test (`check_freecad_connection`, then
  `create_box`) on your machine before relying on it.

## Install / run

```bash
pip install -r requirements.txt
python -m freecad_mcp.main   # or: pip install -e . && freecad-mcp
```

See README.md for the Claude Desktop/Code config block.


## v3.1.0 — Student distribution preparation

- Removed generated Python bytecode/cache files and stale egg metadata from the distribution.
- Removed the machine-specific Claude Desktop config containing a developer's local path.
- Added a Windows setup script, Claude config merge helper, and uninstall script.
- Added student-focused installation, usage, troubleshooting, and safety documentation.
- Requires Python 3.11+ to match the official MCP Python SDK v2 runtime requirement.
- Disabled arbitrary `run_python` execution by default; it is now explicit opt-in.
- Changed the connection check to perform a real local socket request rather than relying on a file/path heuristic.
- Added a release checklist documenting the remaining live integration and licensing checks.
