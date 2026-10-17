"""Smoke-test a running FastSME MCP server over Streamable HTTP."""

from __future__ import annotations

import asyncio
import os
import urllib.request

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv


load_dotenv()


async def main() -> None:
    base_url = os.getenv("MCP_PUBLIC_URL", "http://127.0.0.1:8000/mcp")
    health_url = base_url.rsplit("/mcp", 1)[0] + "/healthz"
    print(urllib.request.urlopen(health_url, timeout=5).read().decode())

    headers = {}
    if secret := os.getenv("MCP_AUTH_SECRET"):
        headers["Authorization"] = f"Bearer {secret}"
    async with httpx2.AsyncClient(headers=headers) as http_client:
        transport = streamable_http_client(base_url, http_client=http_client)
        async with Client(transport) as client:
            tools = await client.list_tools()
            print([tool.name for tool in tools.tools])
            result = await client.call_tool("integration_status", {})
            print(result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())
