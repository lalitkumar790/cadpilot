"""Smoke-test a running local CADPilot Streamable HTTP MCP server.

Usage: python scripts/check_chatgpt_mcp.py
This checks MCP discovery only; it does NOT assert that FreeCAD is connected.
"""
import asyncio
import os

from mcp import Client


async def main() -> None:
    url = os.environ.get("CADPILOT_MCP_URL", "http://127.0.0.1:8765/mcp")
    async with Client(url) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools]
        print(f"MCP connected to {url}")
        print(f"Discovered {len(names)} tools:")
        for name in names:
            print(f" - {name}")


if __name__ == "__main__":
    asyncio.run(main())
