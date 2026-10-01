"""
Enterprise Mailbox Diagnostics, Folder Hierarchy & Routing Forensics Tool.
Leverages Microsoft Graph API with OAuth2 App-Only authentication.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("DiagnosticsTool")
graph_client = GraphClient()

def inspect_mailbox_folders(user_upn: str, include_child_folders: bool = True) -> Dict[str, Any]:
    """
    Recursively inspects the entire mailbox folder tree, total item counts, and unread metrics.
    Essential for detecting deep subfolder nesting and missing email reports.
    
    :param user_upn: Mailbox UPN (e.g. user@domain.com)
    :param include_child_folders: Whether to recursively traverse subfolders (Default: True)
    """
    try:
        folders = graph_client.get_mail_folders(user_upn=user_upn, include_child_folders=include_child_folders)
        sorted_folders = sorted(folders, key=lambda x: x.get("totalItemCount", 0), reverse=True)
        return {
            "success": True,
            "user": user_upn,
            "total_folders": len(sorted_folders),
            "folders": sorted_folders
        }
    except Exception as e:
        logger.error(f"Failed to inspect mailbox folders for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}

def diagnose_mailbox_health(user_upn: str, hours_back: int = 24) -> Dict[str, Any]:
    """
    Performs comprehensive diagnostic analysis on a mailbox to diagnose 'missing email' or 'empty inbox' anomalies:
    1. Audits arrival of recent messages.
    2. Identifies actual destination folders where emails are arriving.
    3. Detects server-side routing/inbox rules diverting incoming traffic.
    4. Quantifies items in Trash, Archive, and Subfolders.
    
    :param user_upn: Mailbox UPN to analyze
    :param hours_back: Search horizon in hours (Default: 24)
    """
    try:
        diag = graph_client.diagnose_mailbox(user_upn=user_upn, hours_back=hours_back)
        return {
            "success": True,
            "diagnostic": diag
        }
    except Exception as e:
        logger.error(f"Failed to run mailbox health diagnostics for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}

def search_mailbox_messages(
    user_upn: str,
    search_query: Optional[str] = None,
    filter_query: Optional[str] = None,
    folder_id: Optional[str] = None,
    top: int = 25
) -> Dict[str, Any]:
    """
    Searches mailbox messages using text query, OData filter or specific folder ID.
    
    :param user_upn: Mailbox UPN
    :param search_query: Free text search across subject, body and sender
    :param filter_query: OData $filter string (e.g. "receivedDateTime ge 2026-10-01T00:00:00Z")
    :param folder_id: Optional target folder ID to restrict search scope
    :param top: Maximum results to retrieve (Default: 25)
    """
    try:
        msgs = graph_client.search_messages(
            user_upn=user_upn,
            search_query=search_query,
            filter_query=filter_query,
            folder_id=folder_id,
            top=top
        )
        return {
            "success": True,
            "user": user_upn,
            "count": len(msgs),
            "messages": msgs
        }
    except Exception as e:
        logger.error(f"Failed to search messages for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}
