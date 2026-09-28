"""
Compliance & Retention Tool for Microsoft 365.
Audits tenant email disclaimers, signatures, retention tags, recoverable items, and legal holds.
"""

from typing import Any, Dict, Optional
from mcp_m365.core.powershell_bridge import execute_exchange_script
from mcp_m365.core.logger import get_logger

logger = get_logger("ComplianceTool")

def audit_domain_signatures() -> Dict[str, Any]:
    """
    Audits tenant-wide email signatures and legal disclaimers configured via Exchange Transport Rules.
    """
    cmd = (
        "Get-TransportRule | "
        "Where-Object { $_.ApplyHtmlDisclaimerText -ne $null -or $_.ApplyHtmlDisclaimerLocation -ne $null } | "
        "Select-Object Name, State, Priority, ApplyHtmlDisclaimerLocation, ApplyHtmlDisclaimerText | "
        "ConvertTo-Json -Depth 3"
    )
    return execute_exchange_script(cmd)

def audit_compliance_retention() -> Dict[str, Any]:
    """
    Audits retention policies and MRM tags configured in Exchange Online for compliance/GDPR/LGPD.
    """
    cmd = (
        "Get-RetentionPolicy | "
        "Select-Object Name, RetentionPolicyTagLinks, IsDefault | "
        "ConvertTo-Json -Depth 3"
    )
    return execute_exchange_script(cmd)

def audit_litigation_hold(identity: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks if mailboxes have Litigation Hold or Retention Hold enabled for legal preservation.
    
    :param identity: Optional specific user UPN or mailbox. If omitted, checks all mailboxes with hold active.
    """
    if identity:
        cmd = (
            f"Get-Mailbox -Identity '{identity}' | "
            "Select-Object DisplayName, UserPrincipalName, LitigationHoldEnabled, LitigationHoldDate, LitigationHoldOwner, RetentionHoldEnabled | "
            "ConvertTo-Json -Depth 2"
        )
    else:
        cmd = (
            "Get-Mailbox -ResultSize Unlimited | "
            "Where-Object { $_.LitigationHoldEnabled -eq $true -or $_.RetentionHoldEnabled -eq $true } | "
            "Select-Object DisplayName, UserPrincipalName, LitigationHoldEnabled, LitigationHoldDate, RetentionHoldEnabled | "
            "ConvertTo-Json -Depth 2"
        )
    return execute_exchange_script(cmd)

def audit_mailbox_recoverable_items(identity: str) -> Dict[str, Any]:
    """
    Audits Recoverable Items and Deleted Items folder sizes and quotas for compliance and storage hygiene.
    
    :param identity: User mailbox identity or email address.
    """
    cmd = (
        f"Get-MailboxFolderStatistics -Identity '{identity}' -FolderScope RecoverableItems | "
        "Select-Object Name, FolderAndSubfolderSize, ItemsInFolderAndSubfolders | "
        "ConvertTo-Json -Depth 2"
    )
    return execute_exchange_script(cmd)
