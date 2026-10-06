"""
Unit and integration tests for MCP M365 Governance Server using standard library unittest.
"""

import sys
import unittest
from pathlib import Path

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_m365 import tools
from mcp_m365.server import server

class TestM365Server(unittest.TestCase):

    def test_server_initialization(self):
        """Validates that MCP server initialized with expected properties and tools."""
        self.assertEqual(server.name, "mcp-m365-microsoft")
        tool_list = server._tool_manager.list_tools()
        self.assertEqual(len(tool_list), 51, f"Expected exactly 51 tools, got {len(tool_list)}")

    def test_tools_export_count(self):
        """Validates that all expected tools are exported in __all__."""
        self.assertGreaterEqual(len(tools.__all__), 35)
        expected_new_tools = [
            "inspect_mailbox_folders",
            "diagnose_mailbox_health",
            "search_mailbox_messages",
            "list_calendar_events",
            "create_calendar_event",
            "list_onedrive_files",
            "search_onedrive_files",
            "get_user_manager",
            "get_user_direct_reports",
            "get_department_members"
        ]
        for t in expected_new_tools:
            self.assertIn(t, tools.__all__, f"Missing {t} in tools.__all__")
            self.assertTrue(hasattr(tools, t), f"Tool {t} not found in tools module")
        for tool_name in tools.__all__:
            self.assertTrue(hasattr(tools, tool_name), f"Tool {tool_name} not found in tools module")

    def test_graph_client_instantiation(self):
        """Validates that GraphClient initializes cleanly without errors."""
        from mcp_m365.core.graph_client import GraphClient
        client = GraphClient(tenant_id="mock-tenant", client_id="mock-client", client_secret="mock-secret")
        self.assertEqual(client.tenant_id, "mock-tenant")
        self.assertEqual(client.client_id, "mock-client")

    def test_powershell_bridge_instantiation(self):
        """Validates that PowerShellBridge initializes with default or custom admin."""
        from mcp_m365.core.powershell_bridge import PowerShellBridge
        bridge = PowerShellBridge(admin_upn="admin@contoso.com")
        self.assertEqual(bridge.admin_upn, "admin@contoso.com")

if __name__ == "__main__":
    unittest.main()
