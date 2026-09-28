"""
Microsoft Graph Mailer & Microsoft Teams Notification Tool.
"""

from typing import Any, Dict, List, Optional
import requests
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("GraphMailerTool")
graph_client = GraphClient()

def send_graph_email(
    from_user: str,
    to_recipients: List[str],
    subject: str,
    html_body: str,
    cc_recipients: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Sends an enterprise email via Microsoft Graph API (App-Only Mail.Send) with HTML body.
    
    :param from_user: Authorized sending account (e.g., alerts@domain.com or admin@domain.com)
    :param to_recipients: Target email addresses
    :param subject: Email subject line
    :param html_body: HTML message body
    :param cc_recipients: Optional CC recipient addresses
    """
    try:
        res = graph_client.send_mail(
            from_user=from_user,
            to_recipients=to_recipients,
            subject=subject,
            html_body=html_body,
            cc_recipients=cc_recipients
        )
        return {"success": True, "details": res}
    except Exception as e:
        logger.error(f"Failed to send email via Graph: {e}")
        return {"success": False, "error": str(e)}

def list_recent_messages(user_upn: str, top: int = 10) -> Dict[str, Any]:
    """
    Queries recent messages from a target mailbox via Microsoft Graph API.
    
    :param user_upn: Mailbox UPN to inspect
    :param top: Number of messages to retrieve (Default: 10)
    """
    try:
        messages = graph_client.get_user_messages(user_upn=user_upn, top=top)
        return {"success": True, "count": len(messages), "messages": messages}
    except Exception as e:
        logger.error(f"Failed to read messages via Graph: {e}")
        return {"success": False, "error": str(e)}

def send_teams_notification(
    title: str,
    message: str,
    webhook_url: Optional[str] = None,
    theme_color: str = "0078D7"
) -> Dict[str, Any]:
    """
    Sends an actionable MessageCard notification to a Microsoft Teams channel via Incoming Webhook.
    
    :param title: Notification title
    :param message: Message text or Markdown
    :param webhook_url: Teams Incoming Webhook URL
    :param theme_color: Hex color string (Default: 0078D7 - Microsoft Blue)
    """
    card_payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": theme_color,
        "summary": title,
        "sections": [{
            "activityTitle": f"📢 **{title}**",
            "activitySubtitle": "M365 Governance MCP Notification",
            "text": message,
            "markdown": True
        }]
    }

    if webhook_url:
        try:
            res = requests.post(webhook_url, json=card_payload, timeout=10)
            res.raise_for_status()
            return {"success": True, "status": "Teams notification sent successfully"}
        except Exception as e:
            return {"success": False, "error": f"Failed to post to Teams: {e}"}

    return {"success": True, "status": "MessageCard validated", "card": card_payload}
