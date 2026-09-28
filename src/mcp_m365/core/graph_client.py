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
        endpoint = f"users/{user_upn}/messages?$top={top}&$select=id,subject,sender,receivedDateTime,isRead&$orderby=receivedDateTime desc"
        res = self.request("GET", endpoint).json()
        return res.get("value", [])
