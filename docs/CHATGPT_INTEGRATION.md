# CADPilot + GPT / ChatGPT

The original **Claude Desktop** integration stays intact. This adds a
**loopback-only Streamable HTTP MCP endpoint** for GPT-compatible clients and
OpenAI's **Secure MCP Tunnel**.

## Architecture

```text
ChatGPT (eligible workspace + custom MCP plugin)
    |  OpenAI Secure MCP Tunnel (authenticated, outbound only)
    v
tunnel-client running on your Windows PC
    |  http://127.0.0.1:8765/mcp (loopback only)
    v
CADPilot Streamable HTTP MCP server
    |  127.0.0.1:23456 local socket (unchanged)
    v
FreeCAD AICopilot workbench
```

**Do not** expose port 23456 or 8765 to the public Internet. Do not deploy
this HTTP process to a cloud host: FreeCAD and its add-on run on your PC.

## Prerequisites

- Windows 10/11, FreeCAD with CADPilot AICopilot add-on installed.
- Python 3.11+ and the existing `.venv` from `scripts/setup_windows.ps1`.
- An eligible ChatGPT workspace with permission to create custom MCP
  connections, plus an OpenAI Platform organization with Secure MCP Tunnel
  permissions. This requires additional setup/authorization in the OpenAI UI.
- The official OpenAI `tunnel-client` installed using its current onboarding
  instructions; installation commands differ by operating system.

## 1. Start FreeCAD and verify the local bridge

Open FreeCAD and confirm the AICopilot workbench/service is loaded.
In PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 23456
```

It should show `TcpTestSucceeded: True` while FreeCAD is running.

## 2. Start the GPT-compatible MCP endpoint

Open a **separate** PowerShell window in your CADPilot repository folder:

```powershell
.\.venv\Scripts\python.exe -m freecad_mcp.chatgpt_http
```

It listens at **http://127.0.0.1:8765/mcp**, on **localhost only**.

To override the local port:

```powershell
$env:CADPILOT_MCP_HTTP_PORT = "8899"
.\.venv\Scripts\python.exe -m freecad_mcp.chatgpt_http
```

The MCP endpoint is **not** a normal web page. Test with an MCP client or MCP
Inspector, not by assuming a browser GET should display a dashboard.

If using the official MCP Python client (same Python environment), try:

```powershell
.\.venv\Scripts\python.exe -c "import asyncio; from mcp import Client; async_code='async def main():\n async with Client(\"http://127.0.0.1:8765/mcp\") as c:\n  print([t.name for t in await c.list_tools()])'; exec(async_code); asyncio.run(main())"
```

If the server is unreachable, check the HTTP terminal logs and make sure the
venv contains `mcp>=2,<3`.

## 3. Connect ChatGPT securely

Follow the **official** Secure MCP Tunnel guide:
https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

1. Create/choose a tunnel in OpenAI Platform tunnel settings, associated
   with your target ChatGPT workspace.
2. Install/configure the official `tunnel-client` on the same Windows PC.
   Run `tunnel-client help quickstart`; use its current guided commands.
   Configure it to forward to `http://127.0.0.1:8765/mcp`.
3. Keep keys and tokens out of GitHub and chat transcripts. Use a
   restricted runtime key with **Tunnels Read + Use**.
4. Run `tunnel-client doctor --profile <your-profile> --explain` and
   start the tunnel. Verify readiness/active polling.
5. In ChatGPT (eligible workspace): **Plugins → Add custom MCP server →
   Connection: Tunnel**. Select the tunnel, complete authentication
   and permissions, discover CADPilot's tools, then install the plugin.
6. In a new chat, select the installed CADPilot plugin. Try
   **check_freecad_connection**, then a non-destructive tool such as listing
   the current document's objects.

ChatGPT Plus users without full custom MCP write permissions cannot
assume this path will enable CAD creation from ChatGPT web. Alternative
clients may use the same local MCP endpoint if they support Streamable HTTP,
or the original stdio endpoint.

## 4. Safety and testing

- The HTTP endpoint itself **has no authentication**. The tunnel is the
  authenticated outer boundary; loopback binding must remain in place.
- CADPilot has write/delete/export tools. Work on a copy of the CAD file
  and review tool permissions before enabling the plugin.
- `run_python` is disabled by default; leave
  `FREECAD_MCP_ENABLE_PYTHON_EXEC` unset.
- Never commit OpenAI API keys, tunnel configuration with tokens, purchased
  designs, or private customer CAD.
- Do not describe a successful ChatGPT connection until an actual tool
  call from ChatGPT has reached FreeCAD.
- MCP tool/transport support changes: use the official setup guides rather
  than assuming old UI menus or tunnel CLI flags remain accurate.

## 5. Troubleshooting

| Symptom | Check |
| --- | --- |
| FreeCAD connection error | AICopilot loaded; 127.0.0.1:23456 reachable |
| HTTP MCP not responding | Local process running; port 8765 free; /mcp path |
| ChatGPT cannot discover tools | Tunnel running; eligible workspace, plugin permissions; tunnel associated with correct organization/workspace |
| GPT tools visible but cannot edit CAD | ChatGPT plan/tool permissions; current document; AICopilot service |
| Claude Desktop stopped working | Keep using original `freecad_mcp.main` stdio entry point; HTTP server is separate |

This change is a **transport integration**, not a claim that the end-to-end
ChatGPT connection has been tested on the user's computer.
