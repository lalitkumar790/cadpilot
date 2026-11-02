"""Entry point: `python -m freecad_mcp.main` or the `freecad-mcp` console script.

Migrated from the old low-level ``Server`` + manual ``stdio_server()`` +
``asyncio.run(main())`` boilerplate to the current MCPServer API, whose
``run()`` is a synchronous call that manages its own event loop internally.
"""
from __future__ import annotations

import logging
import sys

# Import tools BEFORE importing mcp_server's run — this registers every
# @mcp_server.tool() defined across freecad_mcp/tools/*.py.
from freecad_mcp.server import mcp_server
import freecad_mcp.tools  # noqa: F401  (registers tools as a side effect)

logger = logging.getLogger("freecad_mcp.main")


def run() -> None:
    try:
        mcp_server.run(transport="stdio")
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        logger.exception("freecad-mcp server crashed")
        sys.exit(1)


if __name__ == "__main__":
    run()
