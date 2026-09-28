"""
Mailbox & Shared Mailbox Management Tool for Microsoft 365.
Controls permissions, automapping, protocol access, and aliases.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("MailboxTool")
ps_bridge = PowerShellBridge()

def get_mailbox_info(identity: str) -> Dict[str, Any]:
    """
    Retrieves detailed metadata of a mailbox from Exchange Online.
    
    :param identity: UPN, Alias or Primary SMTP address
    """
    ps_cmd = f"""
$mbx = Get-Mailbox -Identity '{identity}' | Select-Object DisplayName, UserPrincipalName, PrimarySmtpAddress, RecipientTypeDetails, ForwardingSmtpAddress, DeliverToMailboxAndForward, HiddenFromAddressListsEnabled, WhenCreated
$cas = Get-CASMailbox -Identity '{identity}' | Select-Object OWAEnabled, ActiveSyncEnabled, MAPIEnabled, SmtpClientAuthenticationDisabled
$aliases = (Get-Mailbox -Identity '{identity}').EmailAddresses | Where-Object {{ $_ -like 'smtp:*' }}

[PSCustomObject]@{{
    Mailbox = $mbx
    Protocols = $cas
    Aliases = $aliases
}} | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "identity": identity,
        "details": result["data"] if result["success"] else result["stderr"]
    }

def list_mailboxes(recipient_type: Optional[str] = "SharedMailbox", result_size: int = 50) -> Dict[str, Any]:
    """
    Lists mailboxes filtered by recipient type (UserMailbox, SharedMailbox, RoomMailbox).
    
    :param recipient_type: Recipient type (Default: SharedMailbox)
    :param result_size: Maximum entries to return (Default: 50)
    """
    filter_expr = f"-RecipientTypeDetails '{recipient_type}'" if recipient_type else ""
    ps_cmd = f"""
Get-Mailbox {filter_expr} -ResultSize {result_size} | Select-Object DisplayName, UserPrincipalName, PrimarySmtpAddress, RecipientTypeDetails, ForwardingSmtpAddress, DeliverToMailboxAndForward | ConvertTo-Json -Depth 3
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "count": len(result["data"]) if isinstance(result["data"], list) else (1 if result["data"] else 0),
        "mailboxes": result["data"] if result["success"] else result["stderr"]
    }

def configure_shared_mailbox(
    identity: str,
    grant_full_access: Optional[List[str]] = None,
    grant_send_as: Optional[List[str]] = None,
    disable_automapping: bool = True,
    copy_sent_items: bool = True
) -> Dict[str, Any]:
    """
    Configures permissions and behavior for a Shared Mailbox.
    
    :param identity: Email address of the Shared Mailbox
    :param grant_full_access: List of users receiving FullAccess
    :param grant_send_as: List of users receiving SendAs
    :param disable_automapping: If True, prevents Outlook clients from auto-downloading large shared OSTs
    :param copy_sent_items: If True, retains copy of sent items in the shared mailbox Sent Items folder
    """
    actions = []
    if grant_full_access:
        for user in grant_full_access:
            automap_val = "$false" if disable_automapping else "$true"
            actions.append(f"Add-MailboxPermission -Identity '{identity}' -User '{user}' -AccessRights FullAccess -AutoMapping {automap_val} -InheritanceType All -Confirm:$false | Out-Null")

    if grant_send_as:
        for user in grant_send_as:
            actions.append(f"Add-RecipientPermission -Identity '{identity}' -Trustee '{user}' -AccessRights SendAs -Confirm:$false | Out-Null")

    if copy_sent_items:
        actions.append(f"Set-Mailbox -Identity '{identity}' -MessageCopyForSentAsEnabled $true -MessageCopyForSendOnBehalfEnabled $true | Out-Null")

    full_script = "\n".join(actions) + f"\n[PSCustomObject]@{{ Mailbox = '{identity}'; Status = 'Permissions and Settings Applied' }} | ConvertTo-Json"
    result = ps_bridge.run_exchange_command(full_script)
    return {
        "success": result["success"],
        "mailbox": identity,
        "details": result["data"] if result["success"] else result["stderr"]
    }
