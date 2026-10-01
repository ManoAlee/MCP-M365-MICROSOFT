"""
Inbox & Transport Rules Tool for Microsoft 365.
Manages server-side mailbox rules and organization-wide transport rules.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

from mcp_m365.core.graph_client import GraphClient

logger = get_logger("RulesRoutingTool")
ps_bridge = PowerShellBridge()
graph_client = GraphClient()

def list_inbox_rules(user_upn: str, use_powershell: bool = False) -> Dict[str, Any]:
    """
    Lists all server-side inbox rules on a mailbox.
    Uses Microsoft Graph API by default for high speed and structured JSON, with PowerShell fallback.
    
    :param user_upn: Mailbox UPN (e.g., user@domain.com)
    :param use_powershell: Force execution through Exchange Online PowerShell (Default: False)
    """
    if not use_powershell:
        try:
            rules = graph_client.get_inbox_rules(user_upn)
            return {
                "success": True,
                "source": "Microsoft Graph API",
                "user": user_upn,
                "count": len(rules),
                "rules": rules
            }
        except Exception as e:
            logger.warning(f"Graph API inbox rule query failed for {user_upn}, falling back to PowerShell: {e}")

    ps_cmd = f"""
Get-InboxRule -Mailbox '{user_upn}' | Select-Object Name, Enabled, Priority, ReceivedAfterDate, ReceivedBeforeDate, RedirectTo, ForwardTo, MoveToFolder, StopProcessingRules | ConvertTo-Json -Depth 4
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "source": "Exchange Online PowerShell",
        "user": user_upn,
        "rules": result["data"] if result["success"] else result["stderr"]
    }

def list_transport_rules(filter_state: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists organization-wide Exchange Transport Rules.
    
    :param filter_state: Filter by state: 'Enabled' or 'Disabled' (Optional)
    """
    filter_expr = f"| Where-Object {{ $_.State -eq '{filter_state}' }}" if filter_state else ""
    ps_cmd = f"""
Get-TransportRule {filter_expr} | Select-Object Name, State, Priority, Mode, Comments | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "transport_rules": result["data"] if result["success"] else result["stderr"]
    }

def remove_inbox_rule(user_upn: str, rule_name: str) -> Dict[str, Any]:
    """
    Deletes a specific inbox rule from a mailbox.
    
    :param user_upn: Mailbox UPN
    :param rule_name: Exact name of the rule to delete
    """
    ps_cmd = f"""
Remove-InboxRule -Mailbox '{user_upn}' -Identity '{rule_name}' -Confirm:$false -ErrorAction Stop
[PSCustomObject]@{{ User = '{user_upn}'; RemovedRule = '{rule_name}'; Status = 'Deleted Successfully' }} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "user": user_upn,
        "details": result["data"] if result["success"] else result["stderr"]
    }
