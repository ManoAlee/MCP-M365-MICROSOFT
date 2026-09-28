"""
Package entrypoint for MCP M365 Governance Server.
"""

from mcp_m365.server import run_stdio

def main():
    run_stdio()

if __name__ == "__main__":
    main()
