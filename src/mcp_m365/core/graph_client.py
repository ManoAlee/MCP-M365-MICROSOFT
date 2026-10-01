"""
Decoupled REST client for Microsoft Graph API v1.0.
Features OAuth2 Client Credentials flow, token caching, and automatic retry on HTTP 429 rate limits.
"""

import time
import requests
from typing import Any, Dict, List, Optional
from mcp_m365.config import TENANT_ID, CLIENT_ID, CLIENT_SECRET
from mcp_m365.core.logger import get_logger

logger = get_logger("GraphClient")

class GraphClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.tenant_id = tenant_id or TENANT_ID
        self.client_id = client_id or CLIENT_ID
        self.client_secret = client_secret or CLIENT_SECRET
        self._token: Optional[str] = None
        self._token_expires_at: float = 0

    @property
    def token_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def _get_token(self) -> str:
        """Acquires or refreshes Bearer token via client_credentials."""
        if not self.tenant_id or not self.client_id or not self.client_secret:
            raise ValueError("Microsoft 365 credentials missing. Configure M365_TENANT_ID, M365_CLIENT_ID and M365_CLIENT_SECRET.")

        now = time.time()
        if self._token and now < (self._token_expires_at - 120):
            return self._token

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }

        resp = requests.post(self.token_url, data=data, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 3600))
        self._token_expires_at = now + expires_in
        logger.info("Graph API Bearer token acquired successfully.")
        return self._token

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Executes an authenticated REST request with retry on HTTP 429 rate limits."""
        token = self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"

        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            res = requests.request(method, url, headers=headers, **kwargs)
            if res.status_code == 429:
                wait_sec = int(res.headers.get("Retry-After", 5))
                logger.warning(f"Graph API 429 Rate Limit. Backing off for {wait_sec}s...")
                time.sleep(wait_sec)
                continue
            res.raise_for_status()
            return res

        raise requests.HTTPError(f"Request failed for {method} {url} after {max_retries} attempts.")

    def send_mail(self, from_user: str, to_recipients: List[str], subject: str, html_body: str, cc_recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches an email via Microsoft Graph API (App-Only Mail.Send)."""
        endpoint = f"users/{from_user}/sendMail"
        to_list = [{"emailAddress": {"address": addr.strip()}} for addr in to_recipients if addr.strip()]
        cc_list = [{"emailAddress": {"address": addr.strip()}} for addr in (cc_recipients or []) if addr.strip()]

        message_payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_body
                },
                "toRecipients": to_list
            },
            "saveToSentItems": "true"
        }

        if cc_list:
            message_payload["message"]["ccRecipients"] = cc_list

        self.request("POST", endpoint, json=message_payload)
        logger.info(f"Email sent via Graph from [{from_user}] to {to_recipients}")
        return {"status": "success", "from": from_user, "to": to_recipients, "subject": subject}

    def list_users(self, filter_query: Optional[str] = None, select: Optional[str] = None, top: int = 50) -> List[Dict[str, Any]]:
        """Queries users from Microsoft Entra ID."""
        endpoint = f"users?$top={top}"
        if filter_query:
            endpoint += f"&$filter={filter_query}"
        if select:
            endpoint += f"&$select={select}"

        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def get_user_messages(self, user_upn: str, top: int = 20) -> List[Dict[str, Any]]:
        """Retrieves recent inbox messages from a target mailbox."""
        endpoint = f"users/{user_upn}/messages?$top={top}&$select=id,subject,sender,receivedDateTime,isRead,parentFolderId,hasAttachments&$orderby=receivedDateTime desc"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def get_mail_folders(self, user_upn: str, include_child_folders: bool = True) -> List[Dict[str, Any]]:
        """Recursively lists all mail folders and subfolders with message counters."""
        endpoint = f"users/{user_upn}/mailFolders?$top=100&$select=id,displayName,parentFolderId,childFolderCount,totalItemCount,unreadItemCount"
        res = self.request("GET", endpoint).json()
        folders = res.get("value", [])

        if include_child_folders:
            expanded_folders: List[Dict[str, Any]] = []
            for f in folders:
                expanded_folders.append(f)
                if f.get("childFolderCount", 0) > 0:
                    child_endpoint = f"users/{user_upn}/mailFolders/{f['id']}/childFolders?$top=100&$select=id,displayName,parentFolderId,childFolderCount,totalItemCount,unreadItemCount"
                    try:
                        c_res = self.request("GET", child_endpoint).json()
                        child_folders = c_res.get("value", [])
                        for cf in child_folders:
                            cf["parentDisplayName"] = f.get("displayName")
                            expanded_folders.append(cf)
                    except Exception as e:
                        logger.warning(f"Failed to fetch child folders for {f.get('displayName')}: {e}")
            return expanded_folders
        return folders

    def get_inbox_rules(self, user_upn: str) -> List[Dict[str, Any]]:
        """Retrieves server-side inbox rules directly via Graph API."""
        endpoint = f"users/{user_upn}/mailFolders/inbox/messageRules"
        try:
            res = self.request("GET", endpoint).json()
            return res.get("value", [])
        except requests.HTTPError as e:
            logger.warning(f"Unable to read inbox rules via Graph for {user_upn} (possible missing MailboxSettings.Read): {e}")
            return []
        except Exception as e:
            logger.warning(f"Error fetching inbox rules for {user_upn}: {e}")
            return []

    def create_inbox_rule(
        self,
        user_upn: str,
        display_name: str,
        conditions: Dict[str, Any],
        actions: Dict[str, Any],
        is_enabled: bool = True,
        sequence: int = 1
    ) -> Dict[str, Any]:
        """Creates a new inbox rule for the specified mailbox via Graph API."""
        endpoint = f"users/{user_upn}/mailFolders/inbox/messageRules"
        payload = {
            "displayName": display_name,
            "sequence": sequence,
            "isEnabled": is_enabled,
            "conditions": conditions,
            "actions": actions
        }
        res = self.request("POST", endpoint, json=payload).json()
        return res

    def delete_inbox_rule(self, user_upn: str, rule_id: str) -> Dict[str, Any]:
        """Deletes a specific inbox rule by its unique ID via Graph API."""
        endpoint = f"users/{user_upn}/mailFolders/inbox/messageRules/{rule_id}"
        self.request("DELETE", endpoint)
        return {"status": "success", "rule_id": rule_id, "user": user_upn}

    def search_messages(
        self,
        user_upn: str,
        search_query: Optional[str] = None,
        filter_query: Optional[str] = None,
        folder_id: Optional[str] = None,
        top: int = 25
    ) -> List[Dict[str, Any]]:
        """Flexible message query supporting search text, OData filters, and folder scope."""
        base = f"users/{user_upn}/mailFolders/{folder_id}/messages" if folder_id else f"users/{user_upn}/messages"
        params = [f"$top={top}", "$select=id,subject,sender,receivedDateTime,isRead,parentFolderId,hasAttachments"]
        if search_query:
            params.append(f"$search=\"{search_query}\"")
        elif filter_query:
            params.append(f"$filter={filter_query}")
        else:
            params.append("$orderby=receivedDateTime desc")

        endpoint = f"{base}?{'&'.join(params)}"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def diagnose_mailbox(self, user_upn: str, hours_back: int = 24) -> Dict[str, Any]:
        """
        Runs comprehensive diagnostic on a mailbox:
        1. Analyzes recent email arrival within the time window.
        2. Resolves destination folders (detects emails bypassing Inbox into subfolders/trash).
        3. Inspects active server-side rules.
        4. Summarizes root-cause findings for missing or empty inbox reports.
        """
        folders = self.get_mail_folders(user_upn=user_upn, include_child_folders=True)
        folder_map = {f["id"]: f.get("displayName", "Unknown") for f in folders}

        # Recent messages
        recent = self.get_user_messages(user_upn=user_upn, top=50)
        rules = self.get_inbox_rules(user_upn=user_upn)

        # Categorize recent messages by folder
        folder_distribution: Dict[str, int] = {}
        diverted_messages: List[Dict[str, Any]] = []

        inbox_ids = [f["id"] for f in folders if f.get("displayName", "").lower() in ["caixa de entrada", "inbox"]]
        inbox_id = inbox_ids[0] if inbox_ids else None

        for msg in recent:
            pid = msg.get("parentFolderId")
            pname = folder_map.get(pid, "Unknown Folder")
            folder_distribution[pname] = folder_distribution.get(pname, 0) + 1

            if inbox_id and pid != inbox_id:
                sender_info = msg.get("sender", {}).get("emailAddress", {})
                diverted_messages.append({
                    "subject": msg.get("subject"),
                    "received": msg.get("receivedDateTime"),
                    "sender": f"{sender_info.get('name')} <{sender_info.get('address')}>",
                    "destination_folder": pname
                })

        return {
            "user": user_upn,
            "total_folders_discovered": len(folders),
            "active_inbox_rules_count": len(rules),
            "recent_messages_sampled": len(recent),
            "folder_distribution": folder_distribution,
            "diverted_from_inbox_sample": diverted_messages[:15],
            "inbox_total_items": next((f["totalItemCount"] for f in folders if f.get("id") == inbox_id), 0),
            "inbox_unread_items": next((f["unreadItemCount"] for f in folders if f.get("id") == inbox_id), 0),
            "rules_summary": [{"name": r.get("displayName"), "enabled": r.get("isEnabled")} for r in rules]
        }

    # --------------------------------------------------------------------------
    # Calendar & Scheduling (Microsoft 365 Calendar)
    # --------------------------------------------------------------------------

    def list_calendar_events(
        self,
        user_upn: str,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        top: int = 20
    ) -> List[Dict[str, Any]]:
        """Queries calendar events for a specific mailbox with optional datetime range."""
        params = [f"$top={top}", "$select=id,subject,start,end,location,organizer,attendees,isOnlineMeeting,onlineMeeting"]
        if start_datetime and end_datetime:
            endpoint = f"users/{user_upn}/calendarView?startDateTime={start_datetime}&endDateTime={end_datetime}&{'&'.join(params)}"
        else:
            endpoint = f"users/{user_upn}/events?{'&'.join(params)}&$orderby=start/dateTime desc"

        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def create_calendar_event(
        self,
        user_upn: str,
        subject: str,
        start_iso: str,
        end_iso: str,
        attendees: Optional[List[str]] = None,
        body_content: str = "",
        location_name: str = "",
        is_online_meeting: bool = True
    ) -> Dict[str, Any]:
        """Creates a scheduled calendar event / Teams meeting."""
        endpoint = f"users/{user_upn}/events"
        attendee_list = [
            {"emailAddress": {"address": a.strip()}, "type": "required"}
            for a in (attendees or []) if a.strip()
        ]
        payload = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body_content
            },
            "start": {
                "dateTime": start_iso,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": "UTC"
            },
            "location": {
                "displayName": location_name
            },
            "attendees": attendee_list,
            "isOnlineMeeting": is_online_meeting,
            "onlineMeetingProvider": "teamsForBusiness" if is_online_meeting else "unknown"
        }
        res = self.request("POST", endpoint, json=payload).json()
        return res

    # --------------------------------------------------------------------------
    # OneDrive & SharePoint Files (ODSP)
    # --------------------------------------------------------------------------

    def list_drive_items(self, user_upn: str, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists files and folders from user's OneDrive root or specific subfolder."""
        if folder_id:
            endpoint = f"users/{user_upn}/drive/items/{folder_id}/children?$select=id,name,size,webUrl,file,folder,lastModifiedDateTime"
        else:
            endpoint = f"users/{user_upn}/drive/root/children?$select=id,name,size,webUrl,file,folder,lastModifiedDateTime"

        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def search_drive_items(self, user_upn: str, query: str, top: int = 25) -> List[Dict[str, Any]]:
        """Searches documents and files across the user's OneDrive storage."""
        endpoint = f"users/{user_upn}/drive/root/search(q='{query}')?$top={top}&$select=id,name,size,webUrl,file,folder,lastModifiedDateTime"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    # --------------------------------------------------------------------------
    # User & Org Awareness (Me / Manager / Direct Reports / Department)
    # --------------------------------------------------------------------------

    def get_user_manager(self, user_upn: str) -> Optional[Dict[str, Any]]:
        """Retrieves the direct reporting manager of a user in Microsoft Entra ID."""
        endpoint = f"users/{user_upn}/manager?$select=id,displayName,userPrincipalName,mail,jobTitle,department"
        try:
            res = self.request("GET", endpoint)
            return res.json()
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise

    def get_user_direct_reports(self, user_upn: str) -> List[Dict[str, Any]]:
        """Retrieves all direct reports (subordinates) for a manager."""
        endpoint = f"users/{user_upn}/directReports?$select=id,displayName,userPrincipalName,mail,jobTitle,department"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])

    def get_department_members(self, department: str, top: int = 50) -> List[Dict[str, Any]]:
        """Queries active members of a specified corporate department."""
        clean_dept = department.replace("'", "''")
        endpoint = f"users?$filter=department eq '{clean_dept}' and accountEnabled eq true&$top={top}&$select=id,displayName,userPrincipalName,mail,jobTitle,department,mobilePhone"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])

