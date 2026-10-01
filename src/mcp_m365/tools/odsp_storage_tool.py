"""
OneDrive & SharePoint Storage (ODSP) Tool for Microsoft 365.
Enables AI agents to query user OneDrive drives, browse folders, and search corporate documents.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("ODSPStorageTool")
graph_client = GraphClient()

def list_onedrive_files(user_upn: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists files and directories located in the user's personal OneDrive root or specified folder.
    
    :param user_upn: User UPN (e.g., user@domain.com)
    :param folder_id: Optional DriveItem ID of a subfolder (Default: Root)
    """
    try:
        items = graph_client.list_drive_items(user_upn=user_upn, folder_id=folder_id)
        return {
            "success": True,
            "user": user_upn,
            "folder_scope": folder_id or "root",
            "count": len(items),
            "items": items
        }
    except Exception as e:
        logger.error(f"Failed to list OneDrive items for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}

def search_onedrive_files(user_upn: str, query: str, top: int = 25) -> Dict[str, Any]:
    """
    Searches for documents and files across the user's OneDrive drive by keyword or filename.
    
    :param user_upn: User UPN
    :param query: Search keyword or document title fragment
    :param top: Maximum results to retrieve (Default: 25)
    """
    try:
        results = graph_client.search_drive_items(user_upn=user_upn, query=query, top=top)
        return {
            "success": True,
            "user": user_upn,
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to search OneDrive files for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}
