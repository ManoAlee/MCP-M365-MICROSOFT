"""
Microsoft 365 User & Organizational Awareness Tool (Me / Manager / Direct Reports).
Grounds AI agents in corporate reporting structures and departmental collaboration maps.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("OrgHierarchyTool")
graph_client = GraphClient()

def get_user_manager(user_upn: str) -> Dict[str, Any]:
    """
    Retrieves the direct manager of a user according to the Entra ID corporate directory.
    
    :param user_upn: User UPN (e.g. user@domain.com)
    """
    try:
        manager = graph_client.get_user_manager(user_upn=user_upn)
        return {
            "success": True,
            "user": user_upn,
            "has_manager": manager is not None,
            "manager": manager
        }
    except Exception as e:
        logger.error(f"Failed to get manager for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}

def get_user_direct_reports(user_upn: str) -> Dict[str, Any]:
    """
    Retrieves the list of direct subordinates reporting to this user.
    
    :param user_upn: Manager's UPN
    """
    try:
        reports = graph_client.get_user_direct_reports(user_upn=user_upn)
        return {
            "success": True,
            "manager": user_upn,
            "direct_reports_count": len(reports),
            "direct_reports": reports
        }
    except Exception as e:
        logger.error(f"Failed to get direct reports for {user_upn}: {e}")
        return {"success": False, "error": str(e), "manager": user_upn}

def get_department_members(department: str, top: int = 50) -> Dict[str, Any]:
    """
    Queries all active collaborators belonging to a specific department in the company.
    
    :param department: Department name (e.g., 'Finance', 'Engineering', 'Compras')
    :param top: Maximum number of team members to retrieve (Default: 50)
    """
    try:
        members = graph_client.get_department_members(department=department, top=top)
        return {
            "success": True,
            "department": department,
            "count": len(members),
            "members": members
        }
    except Exception as e:
        logger.error(f"Failed to query department members for '{department}': {e}")
        return {"success": False, "error": str(e), "department": department}
