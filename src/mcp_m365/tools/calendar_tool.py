"""
Microsoft 365 Calendar & Meeting Scheduling Tool.
Integrates with Microsoft Graph Calendar API to manage events, meetings and scheduling.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("CalendarTool")
graph_client = GraphClient()

def list_calendar_events(
    user_upn: str,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    top: int = 20
) -> Dict[str, Any]:
    """
    Retrieves scheduled events from a user's Microsoft 365 calendar.
    Supports calendarView with date range filtering.
    
    :param user_upn: Mailbox UPN (e.g., user@domain.com)
    :param start_datetime: Optional start datetime in ISO 8601 (e.g. '2026-10-01T00:00:00Z')
    :param end_datetime: Optional end datetime in ISO 8601 (e.g. '2026-10-07T23:59:59Z')
    :param top: Maximum events to return (Default: 20)
    """
    try:
        events = graph_client.list_calendar_events(
            user_upn=user_upn,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            top=top
        )
        return {
            "success": True,
            "user": user_upn,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Failed to list calendar events for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}

def create_calendar_event(
    user_upn: str,
    subject: str,
    start_iso: str,
    end_iso: str,
    attendees: Optional[List[str]] = None,
    body_content: str = "",
    location_name: str = "",
    is_online_meeting: bool = True
) -> Dict[str, Any]:
    """
    Creates a new calendar event or Microsoft Teams meeting on behalf of the user.
    
    :param user_upn: Mailbox UPN of the organizer
    :param subject: Meeting or appointment subject title
    :param start_iso: Start time in ISO 8601 format (e.g. '2026-10-02T14:00:00Z')
    :param end_iso: End time in ISO 8601 format (e.g. '2026-10-02T15:00:00Z')
    :param attendees: Optional list of attendee email addresses
    :param body_content: Meeting agenda or notes (HTML/Text)
    :param location_name: Conference room or physical location name
    :param is_online_meeting: Whether to generate a Microsoft Teams meeting link (Default: True)
    """
    try:
        res = graph_client.create_calendar_event(
            user_upn=user_upn,
            subject=subject,
            start_iso=start_iso,
            end_iso=end_iso,
            attendees=attendees,
            body_content=body_content,
            location_name=location_name,
            is_online_meeting=is_online_meeting
        )
        return {
            "success": True,
            "user": user_upn,
            "event_id": res.get("id"),
            "web_link": res.get("webLink"),
            "online_meeting_url": res.get("onlineMeeting", {}).get("joinUrl") if is_online_meeting else None
        }
    except Exception as e:
        logger.error(f"Failed to create calendar event for {user_upn}: {e}")
        return {"success": False, "error": str(e), "user": user_upn}
