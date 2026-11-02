# Security notes

This project bridges an AI assistant to a locally running CAD application.

## Trust boundary

- Claude Desktop launches the Python MCP server as a local process.
- The MCP server connects to FreeCAD through a local socket.
- The socket service is intended for local use only and has no authentication layer.
- Do not bind the TCP socket to a public or campus-network interface.
- Do not tunnel or port-forward the FreeCAD socket.

## Dangerous capabilities

- `delete_object` removes geometry from the active document.
- `save_document` and export tools write files.
- `run_python` executes arbitrary Python inside FreeCAD.

In this student edition, `run_python` is disabled unless `FREECAD_MCP_ENABLE_PYTHON_EXEC=1` is explicitly set in the MCP server environment. This is a guardrail, not a sandbox. If enabled, code runs with the permissions of the logged-in user.

## Recommendations

1. Keep the default `run_python` setting disabled.
2. Work on copies of important CAD files.
3. Review Claude's proposed operation before allowing destructive edits.
4. Never send confidential designs or credentials in prompts.
5. Do not run this project on a shared lab computer under an administrator account.
6. Keep FreeCAD, Python, and Claude Desktop updated.

## Reporting a vulnerability

Do not publish exploit details or private design files in a public issue. Contact the repository maintainer privately.
