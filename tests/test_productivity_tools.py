"""
Unit tests for Microsoft 365 Calendar, ODSP (OneDrive/SharePoint) and Org Hierarchy tools.
"""

import sys
import unittest
from unittest.mock import patch
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_m365.tools import calendar_tool, odsp_storage_tool, org_hierarchy_tool

class TestProductivityTools(unittest.TestCase):

    # 1. Calendar Tests
    @patch("mcp_m365.tools.calendar_tool.graph_client")
    def test_list_calendar_events(self, mock_client):
        mock_client.list_calendar_events.return_value = [
            {"id": "evt1", "subject": "Architecture Review", "start": {"dateTime": "2026-10-02T10:00:00Z"}}
        ]
        res = calendar_tool.list_calendar_events("user@contoso.com")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["events"][0]["subject"], "Architecture Review")

    @patch("mcp_m365.tools.calendar_tool.graph_client")
    def test_create_calendar_event(self, mock_client):
        mock_client.create_calendar_event.return_value = {
            "id": "evt-new-123",
            "webLink": "https://outlook.office365.com/calendar/event123",
            "onlineMeeting": {"joinUrl": "https://teams.microsoft.com/meet/123"}
        }
        res = calendar_tool.create_calendar_event(
            user_upn="user@contoso.com",
            subject="Sprint Planning",
            start_iso="2026-10-02T14:00:00Z",
            end_iso="2026-10-02T15:00:00Z"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["event_id"], "evt-new-123")
        self.assertIn("teams.microsoft.com", res["online_meeting_url"])

    # 2. ODSP Tests
    @patch("mcp_m365.tools.odsp_storage_tool.graph_client")
    def test_list_onedrive_files(self, mock_client):
        mock_client.list_drive_items.return_value = [
            {"id": "doc1", "name": "Report.xlsx", "size": 1024, "file": {}},
            {"id": "fld1", "name": "Projects", "folder": {}}
        ]
        res = odsp_storage_tool.list_onedrive_files("user@contoso.com")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["items"][0]["name"], "Report.xlsx")

    @patch("mcp_m365.tools.odsp_storage_tool.graph_client")
    def test_search_onedrive_files(self, mock_client):
        mock_client.search_drive_items.return_value = [
            {"id": "doc2", "name": "Compliance_Guidelines.pdf", "size": 2048}
        ]
        res = odsp_storage_tool.search_onedrive_files("user@contoso.com", query="Compliance")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 1)

    # 3. Org Hierarchy Tests
    @patch("mcp_m365.tools.org_hierarchy_tool.graph_client")
    def test_get_user_manager(self, mock_client):
        mock_client.get_user_manager.return_value = {
            "displayName": "Director Name",
            "mail": "director@contoso.com",
            "jobTitle": "IT Director"
        }
        res = org_hierarchy_tool.get_user_manager("engineer@contoso.com")
        self.assertTrue(res["success"])
        self.assertTrue(res["has_manager"])
        self.assertEqual(res["manager"]["displayName"], "Director Name")

    @patch("mcp_m365.tools.org_hierarchy_tool.graph_client")
    def test_get_user_direct_reports(self, mock_client):
        mock_client.get_user_direct_reports.return_value = [
            {"displayName": "Subordinate 1", "mail": "sub1@contoso.com"}
        ]
        res = org_hierarchy_tool.get_user_direct_reports("director@contoso.com")
        self.assertTrue(res["success"])
        self.assertEqual(res["direct_reports_count"], 1)

    @patch("mcp_m365.tools.org_hierarchy_tool.graph_client")
    def test_get_department_members(self, mock_client):
        mock_client.get_department_members.return_value = [
            {"displayName": "Team Member 1", "department": "Logistics"}
        ]
        res = org_hierarchy_tool.get_department_members("Logistics")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 1)

if __name__ == "__main__":
    unittest.main()
