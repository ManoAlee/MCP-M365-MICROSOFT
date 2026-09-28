"""
Distribution Groups & Membership Tool for Microsoft 365.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("GroupsTool")
ps_bridge = PowerShellBridge()

def list_distribution_groups(result_size: int = 50) -> Dict[str, Any]:
    """
    Lists organization distribution groups and their external sender authentication settings.
    
    :param result_size: Maximum entries to return (Default: 50)
    """
    ps_cmd = f"""
Get-DistributionGroup -ResultSize {result_size} | `
    Select-Object DisplayName, PrimarySmtpAddress, RequireSenderAuthenticationEnabled, GroupType | `
    ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "groups": result["data"] if result["success"] else result["stderr"]
    }

def get_group_members(group_identity: str) -> Dict[str, Any]:
    """
    Retrieves the members of a distribution group.
    
    :param group_identity: Group email or alias
    """
    ps_cmd = f"""
Get-DistributionGroupMember -Identity '{group_identity}' | `
    Select-Object DisplayName, PrimarySmtpAddress, RecipientType | `
    ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "group": group_identity,
        "members": result["data"] if result["success"] else result["stderr"]
    }

def manage_group_member(group_identity: str, member_email: str, action: str = "add") -> Dict[str, Any]:
    """
    Adds or removes a member from a distribution group.
    
    :param group_identity: Group email address
    :param member_email: User email address to add or remove
    :param action: 'add' or 'remove'
    """
    if action.lower() == "add":
        ps_cmd = f"Add-DistributionGroupMember -Identity '{group_identity}' -Member '{member_email}' -Confirm:$false -ErrorAction Stop; [PSCustomObject]@{{ Group='{group_identity}'; Member='{member_email}'; Action='Added' }} | ConvertTo-Json"
    else:
        ps_cmd = f"Remove-DistributionGroupMember -Identity '{group_identity}' -Member '{member_email}' -Confirm:$false -ErrorAction Stop; [PSCustomObject]@{{ Group='{group_identity}'; Member='{member_email}'; Action='Removed' }} | ConvertTo-Json"

    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "details": result["data"] if result["success"] else result["stderr"]
    }

def set_group_external_delivery(group_identity: str, allow_external: bool = True) -> Dict[str, Any]:
    """
    Configures whether a distribution group accepts messages from external senders on the internet.
    
    :param group_identity: Group email address
    :param allow_external: If True, allows external senders (RequireSenderAuthenticationEnabled = $false)
    """
    require_auth = "$false" if allow_external else "$true"
    ps_cmd = f"""
Set-DistributionGroup -Identity '{group_identity}' -RequireSenderAuthenticationEnabled {require_auth} -ErrorAction Stop
[PSCustomObject]@{{
    Group = '{group_identity}'
    AllowExternalSenders = ${str(allow_external).lower()}
    Status = 'Updated Successfully'
}} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "group": group_identity,
        "allow_external": allow_external,
        "details": result["data"] if result["success"] else result["stderr"]
    }
