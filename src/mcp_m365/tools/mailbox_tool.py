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

def set_mailbox_forwarding(
    identity: str,
    forwarding_smtp_address: Optional[str] = None,
    deliver_to_mailbox_and_forward: bool = True
) -> Dict[str, Any]:
    """
    Configures or clears server-side email forwarding (ForwardingSmtpAddress) on a mailbox.
    
    :param identity: Mailbox UPN or email address
    :param forwarding_smtp_address: Forwarding destination SMTP address. If None or empty, disables forwarding.
    :param deliver_to_mailbox_and_forward: If True, keeps a copy in the original mailbox.
    """
    if forwarding_smtp_address and forwarding_smtp_address.strip():
        fwd_addr = f"'{forwarding_smtp_address.strip()}'"
        deliver_val = "$true" if deliver_to_mailbox_and_forward else "$false"
        ps_cmd = f"""
Set-Mailbox -Identity '{identity}' -ForwardingSmtpAddress {fwd_addr} -DeliverToMailboxAndForward {deliver_val} -ErrorAction Stop
Get-Mailbox -Identity '{identity}' | Select-Object DisplayName, UserPrincipalName, ForwardingSmtpAddress, DeliverToMailboxAndForward | ConvertTo-Json
"""
    else:
        ps_cmd = f"""
Set-Mailbox -Identity '{identity}' -ForwardingSmtpAddress $null -DeliverToMailboxAndForward $true -ErrorAction Stop
Get-Mailbox -Identity '{identity}' | Select-Object DisplayName, UserPrincipalName, ForwardingSmtpAddress, DeliverToMailboxAndForward | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "identity": identity,
        "details": result["data"] if result["success"] else result["stderr"]
    }

def set_mailbox_protocol_access(
    identity: str,
    owa_enabled: Optional[bool] = None,
    activesync_enabled: Optional[bool] = None,
    mapi_enabled: Optional[bool] = None,
    pop_enabled: Optional[bool] = None,
    imap_enabled: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Controls client protocol access (CASMailbox) for a user (OWA, ActiveSync mobile, MAPI desktop, POP, IMAP).
    
    :param identity: Mailbox UPN or email address
    :param owa_enabled: Enable/disable Outlook Web App
    :param activesync_enabled: Enable/disable Exchange ActiveSync
    :param mapi_enabled: Enable/disable MAPI (Outlook Desktop)
    :param pop_enabled: Enable/disable POP3 protocol
    :param imap_enabled: Enable/disable IMAP4 protocol
    """
    params = []
    if owa_enabled is not None:
        params.append(f"-OWAEnabled {'$true' if owa_enabled else '$false'}")
    if activesync_enabled is not None:
        params.append(f"-ActiveSyncEnabled {'$true' if activesync_enabled else '$false'}")
    if mapi_enabled is not None:
        params.append(f"-MAPIEnabled {'$true' if mapi_enabled else '$false'}")
    if pop_enabled is not None:
        params.append(f"-PopEnabled {'$true' if pop_enabled else '$false'}")
    if imap_enabled is not None:
        params.append(f"-ImapEnabled {'$true' if imap_enabled else '$false'}")

    if not params:
        return {"success": False, "error": "No protocol parameters specified."}

    param_str = " ".join(params)
    ps_cmd = f"""
Set-CASMailbox -Identity '{identity}' {param_str} -ErrorAction Stop
Get-CASMailbox -Identity '{identity}' | Select-Object Identity, OWAEnabled, ActiveSyncEnabled, MAPIEnabled, PopEnabled, ImapEnabled, SmtpClientAuthenticationDisabled | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "identity": identity,
        "details": result["data"] if result["success"] else result["stderr"]
    }

def manage_mailbox_alias(
    identity: str,
    alias_email: str,
    action: str = "add"
) -> Dict[str, Any]:
    """
    Adds or removes a secondary email address (SMTP alias) from a mailbox.
    
    :param identity: Primary mailbox UPN or email address
    :param alias_email: Alias email address to add or remove
    :param action: 'add' or 'remove'
    """
    clean_action = action.strip().lower()
    clean_alias = alias_email.strip().lower()

    if clean_action == "add":
        action_expr = f"@{{Add='smtp:{clean_alias}'}}"
    elif clean_action == "remove":
        action_expr = f"@{{Remove='smtp:{clean_alias}'}}"
    else:
        return {"success": False, "error": "Invalid action. Use 'add' or 'remove'."}

    ps_cmd = f"""
Set-Mailbox -Identity '{identity}' -EmailAddresses {action_expr} -ErrorAction Stop
$aliases = (Get-Mailbox -Identity '{identity}').EmailAddresses | Where-Object {{ $_ -like 'smtp:*' }}
[PSCustomObject]@{{
    Identity = '{identity}'
    Action = '{clean_action}'
    Alias = '{clean_alias}'
    CurrentAliases = $aliases
}} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "identity": identity,
        "details": result["data"] if result["success"] else result["stderr"]
    }
