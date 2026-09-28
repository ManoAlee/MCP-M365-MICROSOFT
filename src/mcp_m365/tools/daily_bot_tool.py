"""
Activity Digest & Daily Bot Tool for Microsoft 365.
Extracts mailbox insights, categorizes communications, and summarizes operational volume.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("DailyBotTool")
graph_client = GraphClient()

def generate_daily_activity_summary(user_upn: str, top_messages: int = 25) -> Dict[str, Any]:
    """
    Analyzes recent mailbox activity via Microsoft Graph API and compiles a categorized operational digest.
    
    :param user_upn: Target mailbox UserPrincipalName (e.g. user@contoso.com)
    :param top_messages: Number of recent messages to analyze (Default: 25)
    """
    try:
        messages = graph_client.get_user_messages(user_upn=user_upn, top=top_messages)
        
        categories = {
            "urgent": [],
            "support_tickets": [],
            "financial": [],
            "general": []
        }

        for m in messages:
            subject = (m.get("subject") or "").lower()
            item = {
                "subject": m.get("subject"),
                "sender": m.get("sender", {}).get("emailAddress", {}).get("address"),
                "received": m.get("receivedDateTime"),
                "is_read": m.get("isRead")
            }

            if any(w in subject for w in ["urgente", "urgent", "alerta", "alert", "crítico", "critical", "erro", "error"]):
                categories["urgent"].append(item)
            elif any(w in subject for w in ["chamado", "ticket", "incidente", "incident", "suporte", "support"]):
                categories["support_tickets"].append(item)
            elif any(w in subject for w in ["nf", "nota fiscal", "invoice", "boleto", "fatura", "pagamento", "payment"]):
                categories["financial"].append(item)
            else:
                categories["general"].append(item)

        return {
            "success": True,
            "user": user_upn,
            "total_analyzed": len(messages),
            "summary": {
                "total_urgent": len(categories["urgent"]),
                "total_support": len(categories["support_tickets"]),
                "total_financial": len(categories["financial"]),
                "total_general": len(categories["general"]),
                "total_analyzed": len(messages)
            },
            "breakdown": categories
        }
    except Exception as e:
        logger.error(f"Error generating activity digest: {e}")
        return {"success": False, "error": str(e)}
