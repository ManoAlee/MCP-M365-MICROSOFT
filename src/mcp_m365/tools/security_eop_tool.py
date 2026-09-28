"""
Security, EOP, Quarantine & Tenant Allow/Block List Tool for Microsoft 365.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("SecurityEOPTool")
ps_bridge = PowerShellBridge()

def check_quarantine_messages(
    recipient_address: Optional[str] = None,
    sender_address: Optional[str] = None,
    hours_back: int = 48,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Queries messages quarantined by Microsoft Defender / Exchange Online Protection.
    
    :param recipient_address: Filter by recipient (Optional)
    :param sender_address: Filter by sender (Optional)
    :param hours_back: Number of past hours to search (Default: 48)
    :param page_size: Maximum messages to return (Default: 50)
    """
    filters = []
    if recipient_address:
        filters.append(f"-RecipientAddress '{recipient_address}'")
    if sender_address:
        filters.append(f"-SenderAddress '{sender_address}'")

    filter_str = " ".join(filters)
    ps_cmd = f"""
$start = (Get-Date).AddHours(-{hours_back})
Get-QuarantineMessage -StartReceivedDate $start {filter_str} -PageSize {page_size} | `
    Select-Object ReceivedTime, SenderAddress, RecipientAddress, Subject, Type, QuarantineTypes, PolicyType, ReleaseStatus | `
    ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "hours_checked": hours_back,
        "messages": result["data"] if result["success"] else result["stderr"]
    }

def list_tenant_allow_block_list() -> Dict[str, Any]:
    """
    Lists entries registered in Microsoft Defender Tenant Allow/Block List (Senders, Domains, URLs).
    """
    ps_cmd = """
$senders = Get-TenantAllowBlockListItems -ListType Sender | Select-Object Value, Action, ExpirationDate, SubType
$urls    = Get-TenantAllowBlockListItems -ListType Url 2>$null | Select-Object Value, Action, ExpirationDate

[PSCustomObject]@{
    AllowedOrBlockedSenders = $senders
    AllowedOrBlockedUrls    = $urls
} | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "allow_block_list": result["data"] if result["success"] else result["stderr"]
    }

def add_sender_to_tenant_allow_list(sender_or_domain: str, note: str = "Approved via MCP Governance") -> Dict[str, Any]:
    """
    Adds a trusted sender or domain to the Tenant Allow List to bypass false-positive filtering.
    
    :param sender_or_domain: Email address or domain to allow
    :param note: Business justification for allowlisting
    """
    ps_cmd = f"""
New-TenantAllowBlockListItems -ListType Sender -Entries '{sender_or_domain}' -Action Allow -Notes '{note}' -ExpirationDate (Get-Date).AddDays(90) -ErrorAction Stop
[PSCustomObject]@{{
    Entry = '{sender_or_domain}'
    Action = 'Allow'
    Status = 'Added Successfully (90-day expiration)'
}} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "entry": sender_or_domain,
        "details": result["data"] if result["success"] else result["stderr"]
    }
