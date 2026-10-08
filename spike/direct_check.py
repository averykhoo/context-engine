"""Call the probe server over stdio without Claude Code, to separate server bugs from client config."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=[sys.argv[1]])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("tools:", [t.name for t in tools.tools])
            res = await s.call_tool("ping", {"caller": "direct"})
            print("result:", res.content[0].text)

asyncio.run(main())
