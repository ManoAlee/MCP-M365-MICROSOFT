"""
Mail Flow, Message Trace, DKIM & Connectors Tool for Microsoft 365.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("MailFlowTool")
ps_bridge = PowerShellBridge()

def message_trace(
    sender_address: Optional[str] = None,
    recipient_address: Optional[str] = None,
    hours_back: int = 24,
    status_filter: Optional[str] = None,
    result_size: int = 50
) -> Dict[str, Any]:
    """
    Runs an Exchange Online Message Trace to diagnose delivery status and routing events.
    
    :param sender_address: Sender email address (Optional)
    :param recipient_address: Recipient email address (Optional)
    :param hours_back: Search window in hours from current time (Default: 24)
    :param status_filter: Filter by status: 'Delivered', 'Failed', 'Pending', 'Quarantined', 'Expanded'
    :param result_size: Maximum events to return (Default: 50)
    """
    filters = []
    if sender_address:
        filters.append(f"-SenderAddress '{sender_address}'")
    if recipient_address:
        filters.append(f"-RecipientAddress '{recipient_address}'")
    if status_filter:
        filters.append(f"-Status '{status_filter}'")

    filter_str = " ".join(filters)
    ps_cmd = f"""
$startDate = (Get-Date).AddHours(-{hours_back})
$endDate   = Get-Date
try {{
    Get-MessageTraceV2 -StartDate $startDate -EndDate $endDate {filter_str} -PageSize {result_size} -ErrorAction Stop | `
        Select-Object Received, SenderAddress, RecipientAddress, Subject, Status, FromIP, Size | `
        ConvertTo-Json -Depth 3
}} catch {{
    Get-MessageTrace -StartDate $startDate -EndDate $endDate {filter_str} -PageSize {result_size} -ErrorAction SilentlyContinue | `
        Select-Object Received, SenderAddress, RecipientAddress, Subject, Status, FromIP, Size | `
        ConvertTo-Json -Depth 3
}}
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "hours_searched": hours_back,
        "results": result["data"] if result["success"] else result["stderr"]
    }

def verify_dkim_status() -> Dict[str, Any]:
    """
    Checks active DKIM signing configurations and key status across organization domains.
    """
    ps_cmd = """
Get-DkimSigningConfig | Select-Object DomainName, Enabled, Status, KeySize, PrimaryKeySelector | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "dkim_configs": result["data"] if result["success"] else result["stderr"]
    }

def list_connectors() -> Dict[str, Any]:
    """
    Lists all Inbound and Outbound mail connectors configured on the Exchange Online tenant.
    """
    ps_cmd = """
$inbound = Get-InboundConnector | Select-Object Name, Enabled, ConnectorType, SenderDomains
$outbound = Get-OutboundConnector | Select-Object Name, Enabled, ConnectorType, RecipientDomains

[PSCustomObject]@{
    InboundConnectors = $inbound
    OutboundConnectors = $outbound
} | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "connectors": result["data"] if result["success"] else result["stderr"]
    }
