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

In this student edition, arbitrary Python execution is disabled by default at **both ends**: the MCP tool wrapper checks the MCP server process environment, and the FreeCAD socket server independently checks the FreeCAD process environment before resolving `execute_python`. To enable it, set `FREECAD_MCP_ENABLE_PYTHON_EXEC=1` in **both** process environments and restart both applications. Setting it only for Claude Desktop/MCP does not enable execution inside FreeCAD; a raw local socket request is also rejected unless FreeCAD itself opted in. This is a guardrail, not a sandbox. If enabled, code runs with the permissions of the logged-in user.

## Local socket protocol and resource limits

- The TCP listener is bound to the loopback interface (`127.0.0.1`/`localhost`) on Windows; Unix-like systems use a local domain socket.
- The bridge sends one newline-delimited JSON request per connection. The FreeCAD listener also accepts a complete legacy JSON request without a newline during upgrades.
- Requests and responses are limited to 8 MiB by the bridge and FreeCAD listener. Socket operations use finite timeouts.
- The FreeCAD listener validates the decoded command independently: the top-level value must contain only a valid `tool` identifier and an optional object-valued `args`; nested values reject non-finite numbers, excessive nesting, oversized strings, and oversized collections.
- These checks protect the protocol boundary; they do not authenticate local clients or make arbitrary FreeCAD operations safe.
- The socket is still unauthenticated. Loopback binding reduces network exposure but does not protect against other processes running as the same user or malware on the machine.

## Recommendations

1. Keep the default `run_python` setting disabled.
2. Work on copies of important CAD files.
3. Review Claude's proposed operation before allowing destructive edits.
4. Never send confidential designs or credentials in prompts.
5. Do not run this project on a shared lab computer under an administrator account.
6. Keep FreeCAD, Python, and Claude Desktop updated.

## Reporting a vulnerability

Do not publish exploit details or private design files in a public issue. Contact the repository maintainer privately.
