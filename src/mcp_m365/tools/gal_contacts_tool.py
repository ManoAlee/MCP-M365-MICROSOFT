"""
Global Address List (GAL) & Directory Tool for Microsoft 365.
Searches users, MailContacts, and external directory entries.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.powershell_bridge import execute_exchange_script
from mcp_m365.core.logger import get_logger

logger = get_logger("GalContactsTool")
graph_client = GraphClient()

def search_directory_users(search_term: str, top: int = 20) -> Dict[str, Any]:
    """
    Searches users in Microsoft Entra ID by displayName, userPrincipalName, or mail.
    
    :param search_term: Name or email prefix to query
    :param top: Maximum entries to return (Default: 20)
    """
    try:
        filter_q = f"startswith(displayName, '{search_term}') or startswith(userPrincipalName, '{search_term}') or startswith(mail, '{search_term}')"
        select_fields = "id,displayName,userPrincipalName,mail,jobTitle,department,accountEnabled"
        users = graph_client.list_users(filter_query=filter_q, select=select_fields, top=top)
        return {
            "success": True,
            "query": search_term,
            "count": len(users),
            "results": users
        }
    except Exception as e:
        logger.error(f"Error searching directory: {e}")
        return {"success": False, "error": str(e)}

def audit_external_mail_contacts(domain_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Audits external MailContacts in Exchange Online directory, optionally filtering by target domain.
    
    :param domain_filter: Optional domain string to filter external email addresses (e.g. 'partner.com')
    """
    cmd = "Get-MailContact -ResultSize Unlimited | Select-Object DisplayName, ExternalEmailAddress, PrimarySmtpAddress, HiddenFromAddressListsEnabled"
    if domain_filter:
        cmd += f" | Where-Object {{ $_.ExternalEmailAddress -like '*@{domain_filter}*' }}"
    cmd += " | ConvertTo-Json -Depth 2"
    
    return execute_exchange_script(cmd)
