"""Step-0 spike: a one-tool stdio MCP server that reports which process answered.

Every call appends one line to $CTX_PROBE_LOG (if set), so a run can tell whether the main
agent and a subagent reached the same server process.
"""
import datetime
import os

from mcp.server.mcpserver import MCPServer

STARTED = datetime.datetime.now().isoformat(timespec="seconds")
server = MCPServer(name="probe")


@server.tool()
def ping(caller: str) -> str:
    """Return the answering process's pid and start time. `caller` is a free label, e.g. 'main' or 'subagent'."""
    line = f"caller={caller} pid={os.getpid()} ppid={os.getppid()} started={STARTED} cwd={os.getcwd()}"
    log = os.environ.get("CTX_PROBE_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    return line


if __name__ == "__main__":
    server.run("stdio")
