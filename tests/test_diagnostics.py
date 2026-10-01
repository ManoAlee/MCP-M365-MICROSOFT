"""
Tests for Mailbox Diagnostics, Folder Hierarchy and Routing Forensics.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_m365.tools import diagnostics_tool

class TestMailboxDiagnostics(unittest.TestCase):

    @patch("mcp_m365.tools.diagnostics_tool.graph_client")
    def test_inspect_mailbox_folders(self, mock_client):
        mock_client.get_mail_folders.return_value = [
            {"id": "f1", "displayName": "Caixa de Entrada", "totalItemCount": 34, "unreadItemCount": 0},
            {"id": "f2", "displayName": "Importação", "totalItemCount": 1050, "unreadItemCount": 5}
        ]
        res = diagnostics_tool.inspect_mailbox_folders("test.user@contoso.com")
        self.assertTrue(res["success"])
        self.assertEqual(res["total_folders"], 2)
        # Should be sorted by totalItemCount descending
        self.assertEqual(res["folders"][0]["displayName"], "Importação")
        self.assertEqual(res["folders"][1]["displayName"], "Caixa de Entrada")

    @patch("mcp_m365.tools.diagnostics_tool.graph_client")
    def test_diagnose_mailbox_health(self, mock_client):
        mock_client.diagnose_mailbox.return_value = {
            "user": "test.user@contoso.com",
            "total_folders_discovered": 15,
            "active_inbox_rules_count": 0,
            "folder_distribution": {"Caixa de Entrada": 2, "Subpasta Fornecedores": 23}
        }
        res = diagnostics_tool.diagnose_mailbox_health("test.user@contoso.com", hours_back=48)
        self.assertTrue(res["success"])
        self.assertEqual(res["diagnostic"]["total_folders_discovered"], 15)
        self.assertIn("Subpasta Fornecedores", res["diagnostic"]["folder_distribution"])

    @patch("mcp_m365.tools.diagnostics_tool.graph_client")
    def test_search_mailbox_messages(self, mock_client):
        mock_client.search_messages.return_value = [
            {"id": "m1", "subject": "Purchase Order 100", "sender": {"emailAddress": {"address": "vendor@contoso.com"}}}
        ]
        res = diagnostics_tool.search_mailbox_messages("test.user@contoso.com", search_query="Purchase Order")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["messages"][0]["subject"], "Purchase Order 100")

if __name__ == "__main__":
    unittest.main()
