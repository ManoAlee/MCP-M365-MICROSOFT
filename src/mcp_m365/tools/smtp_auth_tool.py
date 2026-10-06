"""
SMTP Connectivity, Authentication (SMTP AUTH), Test Delivery & DNS Health Tool for Microsoft 365.
Provides enterprise diagnosis of SMTP relay, direct send, client submission and password expiration policies.
"""

import time
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List, Optional
import requests

from mcp_m365.core.logger import get_logger
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.powershell_bridge import PowerShellBridge

logger = get_logger("SmtpAuthTool")
ps_bridge = PowerShellBridge()
graph_client = GraphClient()


def test_smtp_connectivity(
    host: str = "smtp.office365.com",
    port: int = 587,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Tests low-level TCP socket connectivity and ESMTP handshake against a mail endpoint.
    Evaluates DNS resolution, port reachability (firewall/ISP blocks), connection latency, and STARTTLS support.

    :param host: Mail server hostname or IP (Default: 'smtp.office365.com')
    :param port: Target port: 25 (MX / Direct Send), 587 (SMTP AUTH Submission), 465 (SMTPS)
    :param timeout: Socket timeout in seconds (Default: 10)
    """
    logger.info(f"Testing TCP socket connectivity on {host}:{port}...")
    start_time = time.time()

    # 1. DNS Resolution
    try:
        resolved_ips = socket.gethostbyname_ex(host)[2]
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": f"DNS resolution failed for host: {e}",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    # 2. TCP Socket Connection
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
    except socket.timeout:
        return {
            "success": False,
            "host": host,
            "port": port,
            "resolved_ips": resolved_ips,
            "error": f"Connection timed out after {timeout}s. Port {port} may be blocked by your firewall or ISP.",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "host": host,
            "port": port,
            "resolved_ips": resolved_ips,
            "error": f"Connection refused or unreachable on port {port}: {e}",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    # 3. ESMTP Handshake & Features
    server_capabilities = []
    has_starttls = False
    banner = ""
    try:
        smtp_conn = smtplib.SMTP(host, port, timeout=timeout)
        reply = smtp_conn.ehlo()
        banner = reply[1].decode("utf-8", errors="ignore") if isinstance(reply[1], bytes) else str(reply[1])
        has_starttls = smtp_conn.has_extn("STARTTLS")
        if smtp_conn.esmtp_features:
            server_capabilities = list(smtp_conn.esmtp_features.keys())
        smtp_conn.quit()
    except Exception as e:
        logger.warning(f"ESMTP EHLO handshake notice for {host}:{port}: {e}")

    total_latency = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "host": host,
        "port": port,
        "resolved_ips": resolved_ips,
        "tcp_connection": "ESTABLISHED",
        "latency_ms": total_latency,
        "has_starttls": has_starttls,
        "esmtp_capabilities": server_capabilities,
        "banner_preview": banner[:200].strip() if banner else "N/A"
    }


def test_smtp_auth(
    user: str,
    password: str,
    host: str = "smtp.office365.com",
    port: int = 587,
    use_tls: bool = True,
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Validates SMTP AUTH credentials in real time with root-cause diagnostic feedback (535, licensing, MFA).

    :param user: Full UPN / email address of the account
    :param password: Password for authentication
    :param host: SMTP server endpoint (Default: 'smtp.office365.com')
    :param port: SMTP submission port (Default: 587)
    :param use_tls: Establish STARTTLS encryption before authentication (Default: True)
    :param timeout: Connection timeout in seconds (Default: 15)
    """
    logger.info(f"Validating SMTP AUTH credentials for user [{user}] on {host}:{port}...")
    start_time = time.time()

    try:
        smtp_conn = smtplib.SMTP(host, port, timeout=timeout)
        smtp_conn.ehlo()
        if use_tls:
            if not smtp_conn.has_extn("STARTTLS"):
                smtp_conn.quit()
                return {
                    "success": False,
                    "user": user,
                    "host": host,
                    "port": port,
                    "error": "The mail server does not advertise STARTTLS encryption on this port."
                }
            smtp_conn.starttls()
            smtp_conn.ehlo()

        smtp_conn.login(user, password)
        smtp_conn.quit()

        return {
            "success": True,
            "status": "AUTHENTICATED",
            "user": user,
            "host": host,
            "port": port,
            "security": "STARTTLS" if use_tls else "PLAIN",
            "message": f"SMTP AUTH successful for {user}.",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }

    except smtplib.SMTPAuthenticationError as e:
        code = e.smtp_code
        err_msg = e.smtp_error.decode("utf-8", errors="ignore") if isinstance(e.smtp_error, bytes) else str(e.smtp_error)

        diagnostic_hint = "Verify credentials in Entra ID."
        if code == 535:
            diagnostic_hint = (
                "Code 535: Common causes in Microsoft 365: "
                "1. Incorrect or expired password. "
                "2. Account is a Shared Mailbox lacking an active Exchange Online license. "
                "3. Protocol SMTP AUTH is disabled at mailbox/tenant level (SmtpClientAuthenticationDisabled). "
                "4. Security Defaults or Conditional Access policies blocking legacy Basic Authentication."
            )

        return {
            "success": False,
            "status": "AUTH_FAILED",
            "user": user,
            "host": host,
            "port": port,
            "smtp_code": code,
            "error_details": err_msg,
            "diagnostic_hint": diagnostic_hint,
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "status": "CONNECTION_ERROR",
            "user": user,
            "host": host,
            "port": port,
            "error": str(e),
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }


def send_smtp_test_email(
    sender: str,
    recipient: str,
    host: str = "smtp.office365.com",
    port: int = 587,
    password: Optional[str] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    use_tls: bool = True
) -> Dict[str, Any]:
    """
    Sends an end-to-end test email via SMTP supporting Direct Send (port 25, no auth) or SMTP AUTH (port 587, authenticated).

    :param sender: Envelope sender address
    :param recipient: Envelope recipient address
    :param host: SMTP server host (Default: 'smtp.office365.com')
    :param port: SMTP port: 25 for Direct Send, 587 for SMTP AUTH
    :param password: Password for authentication (Leave None for port 25 Direct Send)
    :param subject: Email subject (Optional)
    :param body: Plain text email body (Optional)
    :param use_tls: Use STARTTLS encryption (Default: True)
    """
    logger.info(f"Dispatching test email from [{sender}] to [{recipient}] via {host}:{port}...")
    start_time = time.time()

    is_direct_send = (port == 25 or not password)
    sub = subject or f"[M365 Test] SMTP Pipeline Validation ({'Direct Send' if is_direct_send else 'SMTP AUTH'})"
    content = body or f"""Hello,

This is an automated test email generated by the MCP M365 Governance Server.
- Method: {'Direct Send (MX Port 25)' if is_direct_send else 'SMTP AUTH Authenticated (Port 587)'}
- Server: {host}
- Port: {port}
- Sender: {sender}
- Recipient: {recipient}
- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

Delivery queued successfully.
"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = sub
    msg.attach(MIMEText(content, "plain", "utf-8"))

    try:
        smtp_conn = smtplib.SMTP(host, port, timeout=20)
        smtp_conn.ehlo()
        if use_tls and smtp_conn.has_extn("STARTTLS"):
            smtp_conn.starttls()
            smtp_conn.ehlo()

        if password:
            smtp_conn.login(sender, password)

        send_res = smtp_conn.sendmail(sender, [recipient], msg.as_string())
        smtp_conn.quit()

        return {
            "success": True,
            "delivery_status": "QUEUED_FOR_DELIVERY",
            "sender": sender,
            "recipient": recipient,
            "host": host,
            "port": port,
            "mode": "DIRECT_SEND" if is_direct_send else "SMTP_AUTH",
            "smtp_reply": "250 OK / Mail Accepted",
            "refused_recipients": send_res,
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "delivery_status": "FAILED",
            "sender": sender,
            "recipient": recipient,
            "host": host,
            "port": port,
            "error": str(e),
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }


def audit_domain_dns_health(domain: str) -> Dict[str, Any]:
    """
    Audits email delivery and authentication DNS records (MX, SPF, DMARC) for any domain.
    Assesses spoofing risk and cross-references public WAN IP against authorized SPF entries.

    :param domain: Target domain to audit (e.g., 'contoso.com')
    """
    import dns.resolver

    logger.info(f"Auditing email DNS health for domain [{domain}]...")
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5

    # 1. Resolve current outbound WAN IP
    wan_ip = None
    try:
        r_ip = requests.get("https://api.ipify.org?format=json", timeout=4)
        if r_ip.status_code == 200:
            wan_ip = r_ip.json().get("ip")
    except Exception:
        try:
            r_ip2 = requests.get("https://ifconfig.me/ip", timeout=4)
            wan_ip = r_ip2.text.strip()
        except Exception:
            pass

    # 2. MX Records
    mx_records = []
    try:
        answers_mx = resolver.resolve(domain, "MX")
        for rdata in answers_mx:
            mx_records.append({
                "host": str(rdata.exchange).rstrip("."),
                "preference": rdata.preference
            })
        mx_records.sort(key=lambda x: x["preference"])
    except Exception as e:
        logger.warning(f"Error resolving MX for {domain}: {e}")

    # 3. TXT / SPF Records
    spf_record = None
    txt_records = []
    try:
        answers_txt = resolver.resolve(domain, "TXT")
        for rdata in answers_txt:
            full_txt = "".join([b.decode("utf-8", errors="ignore") for b in rdata.strings])
            txt_records.append(full_txt)
            if full_txt.startswith("v=spf1"):
                spf_record = full_txt
    except Exception as e:
        logger.warning(f"Error resolving TXT for {domain}: {e}")

    # 4. DMARC Records
    dmarc_record = None
    dmarc_policy = "NOT_CONFIGURED"
    try:
        answers_dmarc = resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in answers_dmarc:
            full_dmarc = "".join([b.decode("utf-8", errors="ignore") for b in rdata.strings])
            if full_dmarc.startswith("v=DMARC1"):
                dmarc_record = full_dmarc
                for tag in full_dmarc.split(";"):
                    tag_clean = tag.strip()
                    if tag_clean.startswith("p="):
                        dmarc_policy = tag_clean.split("=")[1].lower()
    except Exception as e:
        logger.warning(f"Error resolving DMARC for {domain}: {e}")

    # 5. Risk Assessment
    spf_has_outlook = False
    wan_ip_in_spf = False
    if spf_record:
        if "spf.protection.outlook.com" in spf_record:
            spf_has_outlook = True
        if wan_ip and f"ip4:{wan_ip}" in spf_record:
            wan_ip_in_spf = True

    spoofing_risk = "LOW"
    if dmarc_policy in ["none", "NOT_CONFIGURED"]:
        spoofing_risk = "HIGH (DMARC policy does not reject spoofed messages)"
    elif dmarc_policy == "quarantine":
        spoofing_risk = "MEDIUM (Spoofed messages routed to Quarantine/Spam)"
    elif dmarc_policy == "reject":
        spoofing_risk = "MINIMAL (Spoofed messages rejected at gateway)"

    return {
        "success": True,
        "domain": domain,
        "current_wan_ip": wan_ip,
        "mx_records": mx_records,
        "spf": {
            "raw": spf_record,
            "includes_microsoft_365": spf_has_outlook,
            "wan_ip_authorized": wan_ip_in_spf,
            "qualifier": spf_record.split()[-1] if spf_record else None
        },
        "dmarc": {
            "raw": dmarc_record,
            "policy": dmarc_policy,
            "spoofing_protection_risk": spoofing_risk
        }
    }


def get_password_policy(user_upn: str) -> Dict[str, Any]:
    """
    Retrieves password expiration policies and credential status from Microsoft Entra ID via Graph API.
    Identifies whether the account has 'DisablePasswordExpiration' enabled.

    :param user_upn: User Principal Name (UPN) or email address
    """
    logger.info(f"Querying password policy for [{user_upn}] via Microsoft Graph...")

    try:
        token = graph_client._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/beta/users/{user_upn}?$select=id,displayName,userPrincipalName,accountEnabled,passwordPolicies,lastPasswordChangeDateTime"

        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            policies = data.get("passwordPolicies")
            never_expires = bool(policies and "DisablePasswordExpiration" in policies)

            return {
                "success": True,
                "user_upn": user_upn,
                "display_name": data.get("displayName"),
                "account_enabled": data.get("accountEnabled"),
                "password_policies": policies if policies else "DEFAULT_EXPIRATION",
                "password_never_expires": never_expires,
                "last_password_change": data.get("lastPasswordChangeDateTime")
            }
        else:
            return {
                "success": False,
                "user_upn": user_upn,
                "error": f"Graph API error ({r.status_code}): {r.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "user_upn": user_upn,
            "error": str(e)
        }


def set_password_never_expires(user_upn: str, never_expires: bool = True) -> Dict[str, Any]:
    """
    Sets or revokes the 'DisablePasswordExpiration' policy for a service account in Microsoft Entra ID.

    :param user_upn: User Principal Name (UPN) or email address
    :param never_expires: True to disable password expiration, False to restore default tenant expiration
    """
    logger.info(f"Setting 'Password Never Expires' = {never_expires} for [{user_upn}]...")
    policy_value = "DisablePasswordExpiration" if never_expires else "None"

    # 1. Attempt via Graph REST API
    try:
        token = graph_client._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"https://graph.microsoft.com/beta/users/{user_upn}"
        r = requests.patch(url, headers=headers, json={"passwordPolicies": policy_value}, timeout=10)

        if r.status_code in [200, 204]:
            return {
                "success": True,
                "user_upn": user_upn,
                "password_never_expires": never_expires,
                "method": "GRAPH_REST_API",
                "message": f"Password policy updated to {policy_value}."
            }
    except Exception as e:
        logger.warning(f"Graph REST attempt notice: {e}")

    # 2. Fallback via PowerShell Bridge
    ps_cmd = f"""
Update-MgUser -UserId '{user_upn}' -PasswordPolicies '{policy_value}' -ErrorAction Stop
Get-MgUser -UserId '{user_upn}' -Property PasswordPolicies | Select-Object Id, UserPrincipalName, PasswordPolicies | ConvertTo-Json
"""
    ps_res = ps_bridge.run_exchange_command(ps_cmd)
    if ps_res["success"]:
        return {
            "success": True,
            "user_upn": user_upn,
            "password_never_expires": never_expires,
            "method": "POWERSHELL_MGUSER",
            "data": ps_res["data"]
        }

    return {
        "success": False,
        "user_upn": user_upn,
        "error": "Insufficient privileges in dedicated App Registration (requires User.ReadWrite.All).",
        "recommended_action": f"Run in administrative PowerShell: Update-MgUser -UserId '{user_upn}' -PasswordPolicies '{policy_value}'",
        "raw_stderr": ps_res.get("stderr")
    }


def diagnose_smtp_relay_prerequisites(domain: str) -> Dict[str, Any]:
    """
    Performs comprehensive pre-flight audit for SMTP Relay and Direct Send
    (WAN IP, MX resolution, port 25/587 reachability, Exchange Inbound Connectors, and SPF authorization).

    :param domain: Organization domain to diagnose (e.g. 'contoso.com')
    """
    dns_audit = audit_domain_dns_health(domain=domain)
    wan_ip = dns_audit.get("current_wan_ip")
    mx_list = dns_audit.get("mx_records", [])
    primary_mx = mx_list[0]["host"] if mx_list else f"{domain.replace('.', '-')}.mail.protection.outlook.com"

    test_p25 = test_smtp_connectivity(host=primary_mx, port=25, timeout=6)
    test_p587 = test_smtp_connectivity(host="smtp.office365.com", port=587, timeout=6)

    ps_connectors = """
Get-InboundConnector | Select-Object Name, Enabled, ConnectorType, SenderIPAddresses, SenderDomains | ConvertTo-Json
"""
    conn_res = ps_bridge.run_exchange_command(ps_connectors)
    inbound_connectors = conn_res.get("data", []) if conn_res["success"] else []

    can_direct_send = test_p25.get("success", False)
    can_external_relay = (
        test_p25.get("success", False) and
        dns_audit["spf"]["wan_ip_authorized"] and
        any(c.get("Enabled") for c in (inbound_connectors if isinstance(inbound_connectors, list) else [inbound_connectors]))
    )

    return {
        "success": True,
        "domain": domain,
        "current_wan_ip": wan_ip,
        "primary_mx": primary_mx,
        "ports_status": {
            "mx_port_25_direct_send": "OPEN" if test_p25.get("success") else "BLOCKED",
            "smtp_port_587_client_submission": "OPEN" if test_p587.get("success") else "BLOCKED"
        },
        "inbound_connectors": inbound_connectors,
        "verdict": {
            "direct_send_internal_only": {
                "ready": can_direct_send,
                "details": f"Ready for unauthenticated internal delivery to @{domain}." if can_direct_send else "Port 25 blocked."
            },
            "external_relay": {
                "ready": can_external_relay,
                "blockers": [
                    *([] if dns_audit["spf"]["wan_ip_authorized"] else [f"Public IP {wan_ip} missing from domain SPF record"]),
                    *([] if any(c.get("Enabled") for c in (inbound_connectors if isinstance(inbound_connectors, list) else [inbound_connectors])) else ["No active Inbound Connector validating outbound IP in Exchange"])
                ]
            }
        }
    }
