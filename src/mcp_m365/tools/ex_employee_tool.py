"""
Ex-Employee Governance & NDR 550 5.1.10 Elimination Tool for Microsoft 365.
Converts offboarded mailboxes to zero-license Shared Mailboxes and configures native forwarding.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("ExEmployeeTool")
ps_bridge = PowerShellBridge()

def audit_ex_employees(custom_check_list: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Scans ex-employee mailboxes to detect delivery failure risks (NDR 550 5.1.10 Resolver.RST.RecipientNotFound).
    Validates whether the recipient is a SharedMailbox and has an active ForwardingSmtpAddress.
    
    :param custom_check_list: Optional list of dicts with 'legacy_email' and 'target_email'
    """
    if custom_check_list:
        items_ps = "@(\n" + ",\n".join([f"@{{ Legacy = '{i['legacy_email']}'; Target = '{i['target_email']}' }}" for i in custom_check_list]) + "\n)"
    else:
        items_ps = "@()"

    ps_cmd = f"""
$exFuncs = {items_ps}
if ($exFuncs.Count -eq 0) {{
    $shareds = Get-Mailbox -RecipientTypeDetails SharedMailbox -ResultSize 50 | Select-Object DisplayName, UserPrincipalName, ForwardingSmtpAddress, DeliverToMailboxAndForward, HiddenFromAddressListsEnabled
    $shareds | ConvertTo-Json -Depth 3
}} else {{
    $results = @()
    foreach ($item in $exFuncs) {{
        $mbx = Get-Mailbox -Identity $item.Legacy -ErrorAction SilentlyContinue
        if ($mbx) {{
            $status = if ($mbx.RecipientTypeDetails -eq 'SharedMailbox' -and $mbx.ForwardingSmtpAddress) {{ "In Compliance" }} else {{ "Attention Required" }}
            $results += [PSCustomObject]@{{
                LegacyEmail = $item.Legacy
                ExpectedTarget = $item.Target
                CurrentForward = $mbx.ForwardingSmtpAddress
                DeliverToMailboxAndForward = $mbx.DeliverToMailboxAndForward
                RecipientType = $mbx.RecipientTypeDetails
                HiddenFromGAL = $mbx.HiddenFromAddressListsEnabled
                Status = $status
            }}
        }} else {{
            $results += [PSCustomObject]@{{
                LegacyEmail = $item.Legacy
                ExpectedTarget = $item.Target
                Status = "Object Missing (High NDR 550 Risk in Authoritative Domains)"
            }}
        }}
    }}
    $results | ConvertTo-Json -Depth 3
}}
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "audit_data": result["data"] if result["success"] else result["stderr"]
    }

def convert_to_shared_and_forward(
    legacy_upn: str,
    target_forward_email: str,
    hide_from_gal: bool = True
) -> Dict[str, Any]:
    """
    Converts an offboarded user mailbox to a zero-cost Shared Mailbox and enables native forwarding with local copy retention.
    
    :param legacy_upn: Target mailbox to convert
    :param target_forward_email: Designated successor / team mailbox to receive forwarded mail
    :param hide_from_gal: If True, hides mailbox from Global Address List
    """
    ps_cmd = f"""
Set-Mailbox -Identity '{legacy_upn}' -Type Shared -ErrorAction Stop
Set-Mailbox -Identity '{legacy_upn}' `
    -ForwardingSmtpAddress '{target_forward_email}' `
    -DeliverToMailboxAndForward $true `
    -HiddenFromAddressListsEnabled ${str(hide_from_gal).lower()} `
    -ErrorAction Stop

$mbx = Get-Mailbox -Identity '{legacy_upn}' | Select-Object DisplayName, RecipientTypeDetails, ForwardingSmtpAddress, DeliverToMailboxAndForward, HiddenFromAddressListsEnabled
$mbx | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "legacy_email": legacy_upn,
        "details": result["data"] if result["success"] else result["stderr"]
    }
