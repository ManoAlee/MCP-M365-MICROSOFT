"""
User Profile & Organization Hierarchy Tool for Microsoft 365.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("ProfileSyncTool")
ps_bridge = PowerShellBridge()
graph_client = GraphClient()

def get_user_profile(user_upn: str) -> Dict[str, Any]:
    """
    Retrieves full organizational profile attributes of a user (Job Title, Department, Phones, Office, Status).
    
    :param user_upn: User Principal Name (e.g., user@domain.com)
    """
    try:
        select_fields = "id,displayName,userPrincipalName,mail,jobTitle,department,officeLocation,mobilePhone,businessPhones,accountEnabled"
        res = graph_client.request("GET", f"users/{user_upn}?$select={select_fields}").json()
        return {"success": True, "profile": res}
    except Exception as e:
        logger.error(f"Error fetching profile via Graph: {e}")
        return {"success": False, "error": str(e)}

def update_user_profile(
    user_upn: str,
    department: Optional[str] = None,
    job_title: Optional[str] = None,
    mobile_phone: Optional[str] = None,
    business_phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates organizational attributes of a user across Entra ID and Exchange Online.
    
    :param user_upn: User Principal Name
    :param department: Department name
    :param job_title: Job title
    :param mobile_phone: Corporate mobile phone
    :param business_phone: Corporate office phone / extension
    """
    fields = []
    if department:
        fields.append(f"-Department '{department}'")
    if job_title:
        fields.append(f"-Title '{job_title}'")
    if mobile_phone:
        fields.append(f"-MobilePhone '{mobile_phone}'")
    if business_phone:
        fields.append(f"-Phone '{business_phone}'")

    if not fields:
        return {"success": False, "error": "No update fields provided."}

    fields_str = " ".join(fields)
    ps_cmd = f"""
Set-User -Identity '{user_upn}' {fields_str} -ErrorAction Stop
Get-User -Identity '{user_upn}' | Select-Object DisplayName, Department, Title, Phone, MobilePhone | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "user": user_upn,
        "details": result["data"] if result["success"] else result["stderr"]
    }
