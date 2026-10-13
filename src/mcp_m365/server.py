"""
Enterprise Microsoft 365 Model Context Protocol (MCP) Server.
Orchestrates 33 enterprise tools covering Exchange Online, Microsoft Graph API,
Security & Compliance, EOP, Directory & Licensing.
"""

from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_m365.core.logger import get_logger
from mcp_m365 import tools

logger = get_logger("Server")

# Initialize MCP Server
server = MCPServer(
    name="mcp-m365-microsoft",
    description="Enterprise Microsoft 365 Governance & Administration MCP Server (Graph API & Exchange Online)"
)

# ------------------------------------------------------------------------------
# 1. Out of Office & Vacation Management
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_get_vacation_status",
    description="Checks the scheduled automatic reply (OOF / Out-of-Office) and vacation forwarding rules for a mailbox."
)
def tool_get_vacation_status(user_upn: str) -> Dict[str, Any]:
    return tools.get_vacation_status(user_upn=user_upn)

@server.tool(
    name="m365_configure_vacation",
    description="Configures scheduled out-of-office auto-reply with HTML formatting and optional forwarding/redirection."
)
def tool_configure_vacation(
    user_upn: str,
    start_date: str,
    end_date: str,
    return_date: str,
    signature_name: str,
    redirect_to: Optional[List[str]] = None,
    inform_team_handling: bool = True
) -> Dict[str, Any]:
    return tools.configure_vacation(
        user_upn=user_upn,
        start_date=start_date,
        end_date=end_date,
        return_date=return_date,
        signature_name=signature_name,
        redirect_to=redirect_to,
        inform_team_handling=inform_team_handling
    )

@server.tool(
    name="m365_disable_vacation",
    description="Immediately disables automatic out-of-office replies, clears mailbox vacation rules, and optionally disables absence transport rules."
)
def tool_disable_vacation(user_upn: str, disable_transport_rules: bool = True) -> Dict[str, Any]:
    return tools.disable_vacation(user_upn=user_upn, disable_transport_rules=disable_transport_rules)

# ------------------------------------------------------------------------------
# 2. Ex-Employee Governance & Lifecycle
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_audit_ex_employees",
    description="Audits disabled or terminated accounts for NDR 550 5.1.10 risks and license optimization opportunities."
)
def tool_audit_ex_employees() -> Dict[str, Any]:
    return tools.audit_ex_employees()

@server.tool(
    name="m365_convert_ex_employee_to_shared",
    description="Converts a departing employee's mailbox to a free SharedMailbox, sets forwarding with copy, and hides from GAL."
)
def tool_convert_ex_employee_to_shared(
    legacy_upn: str,
    target_forward_email: str,
    hide_from_gal: bool = True
) -> Dict[str, Any]:
    return tools.convert_to_shared_and_forward(
        legacy_upn=legacy_upn,
        target_forward_email=target_forward_email,
        hide_from_gal=hide_from_gal
    )

# ------------------------------------------------------------------------------
# 3. Mailbox Operations & Permissions
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_get_mailbox_info",
    description="Retrieves comprehensive mailbox properties (type, protocols, UPN, aliases, forwarding, quotas)."
)
def tool_get_mailbox_info(identity: str) -> Dict[str, Any]:
    return tools.get_mailbox_info(identity=identity)

@server.tool(
    name="m365_list_mailboxes",
    description="Lists mailboxes filtered by type (SharedMailbox, UserMailbox, RoomMailbox)."
)
def tool_list_mailboxes(recipient_type: Optional[str] = "SharedMailbox", result_size: int = 50) -> Dict[str, Any]:
    return tools.list_mailboxes(recipient_type=recipient_type, result_size=result_size)

@server.tool(
    name="m365_configure_shared_mailbox",
    description="Configures shared mailbox permissions (FullAccess, SendAs, automapping toggle, copy sent items)."
)
def tool_configure_shared_mailbox(
    identity: str,
    grant_full_access: Optional[List[str]] = None,
    grant_send_as: Optional[List[str]] = None,
    disable_automapping: bool = True,
    copy_sent_items: bool = True
) -> Dict[str, Any]:
    return tools.configure_shared_mailbox(
        identity=identity,
        grant_full_access=grant_full_access,
        grant_send_as=grant_send_as,
        disable_automapping=disable_automapping,
        copy_sent_items=copy_sent_items
    )

@server.tool(
    name="m365_set_mailbox_forwarding",
    description="Configures or clears server-side email forwarding (ForwardingSmtpAddress) on a mailbox with deliver-and-forward option."
)
def tool_set_mailbox_forwarding(
    identity: str,
    forwarding_smtp_address: Optional[str] = None,
    deliver_to_mailbox_and_forward: bool = True
) -> Dict[str, Any]:
    return tools.set_mailbox_forwarding(
        identity=identity,
        forwarding_smtp_address=forwarding_smtp_address,
        deliver_to_mailbox_and_forward=deliver_to_mailbox_and_forward
    )

@server.tool(
    name="m365_set_mailbox_protocol_access",
    description="Controls client protocol access (CASMailbox) for a user (OWA, ActiveSync mobile, MAPI desktop, POP, IMAP)."
)
def tool_set_mailbox_protocol_access(
    identity: str,
    owa_enabled: Optional[bool] = None,
    activesync_enabled: Optional[bool] = None,
    mapi_enabled: Optional[bool] = None,
    pop_enabled: Optional[bool] = None,
    imap_enabled: Optional[bool] = None
) -> Dict[str, Any]:
    return tools.set_mailbox_protocol_access(
        identity=identity,
        owa_enabled=owa_enabled,
        activesync_enabled=activesync_enabled,
        mapi_enabled=mapi_enabled,
        pop_enabled=pop_enabled,
        imap_enabled=imap_enabled
    )

@server.tool(
    name="m365_manage_mailbox_alias",
    description="Adds or removes a secondary email address (SMTP alias) from a mailbox (action: 'add' or 'remove')."
)
def tool_manage_mailbox_alias(
    identity: str,
    alias_email: str,
    action: str = "add"
) -> Dict[str, Any]:
    return tools.manage_mailbox_alias(
        identity=identity,
        alias_email=alias_email,
        action=action
    )

# ------------------------------------------------------------------------------
# 4. Rules & Transport Routing
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_list_inbox_rules",
    description="Lists all client-side and server-side inbox rules configured on a specific mailbox."
)
def tool_list_inbox_rules(user_upn: str) -> Dict[str, Any]:
    return tools.list_inbox_rules(user_upn=user_upn)

@server.tool(
    name="m365_list_transport_rules",
    description="Lists tenant-wide mail flow and transport rules in Exchange Online."
)
def tool_list_transport_rules(filter_state: Optional[str] = None) -> Dict[str, Any]:
    return tools.list_transport_rules(filter_state=filter_state)

@server.tool(
    name="m365_get_transport_rule_details",
    description="Retrieves comprehensive configuration, conditions, actions, and comments of an Exchange Online transport rule."
)
def tool_get_transport_rule_details(rule_identity: str) -> Dict[str, Any]:
    return tools.get_transport_rule_details(rule_identity=rule_identity)

@server.tool(
    name="m365_disable_transport_rule",
    description="Disables an Exchange Online transport rule immediately and validates the updated state (Disabled)."
)
def tool_disable_transport_rule(rule_identity: str) -> Dict[str, Any]:
    return tools.disable_transport_rule(rule_identity=rule_identity)

@server.tool(
    name="m365_enable_transport_rule",
    description="Enables an Exchange Online transport rule and validates the updated state (Enabled)."
)
def tool_enable_transport_rule(rule_identity: str) -> Dict[str, Any]:
    return tools.enable_transport_rule(rule_identity=rule_identity)

@server.tool(
    name="m365_remove_transport_rule",
    description="Permanently deletes an organization-level Exchange Online transport rule."
)
def tool_remove_transport_rule(rule_identity: str) -> Dict[str, Any]:
    return tools.remove_transport_rule(rule_identity=rule_identity)

@server.tool(
    name="m365_remove_inbox_rule",
    description="Removes a specific inbox rule from a mailbox by its RuleIdentity or Name."
)
def tool_remove_inbox_rule(user_upn: str, rule_name: str) -> Dict[str, Any]:
    return tools.remove_inbox_rule(user_upn=user_upn, rule_name=rule_name)

# ------------------------------------------------------------------------------
# 5. Microsoft Graph API & Notifications
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_send_email",
    description="Sends corporate email with HTML formatting via Microsoft Graph API with application permissions."
)
def tool_send_graph_email(
    from_user: str,
    to_recipients: List[str],
    subject: str,
    html_body: str,
    cc_recipients: Optional[List[str]] = None
) -> Dict[str, Any]:
    return tools.send_graph_email(
        from_user=from_user,
        to_recipients=to_recipients,
        subject=subject,
        html_body=html_body,
        cc_recipients=cc_recipients
    )

@server.tool(
    name="graph_list_recent_messages",
    description="Fetches recent emails from a mailbox via Microsoft Graph API."
)
def tool_list_recent_messages(user_upn: str, top: int = 10) -> Dict[str, Any]:
    return tools.list_recent_messages(user_upn=user_upn, top=top)

@server.tool(
    name="graph_send_teams_notification",
    description="Sends rich formatted card notifications to Microsoft Teams channels via Incoming Webhooks."
)
def tool_send_teams_notification(
    title: str,
    message: str,
    webhook_url: Optional[str] = None,
    theme_color: str = "0078D7"
) -> Dict[str, Any]:
    return tools.send_teams_notification(
        title=title,
        message=message,
        webhook_url=webhook_url,
        theme_color=theme_color
    )

# ------------------------------------------------------------------------------
# 6. Directory, Global Address List (GAL) & Contacts
# ------------------------------------------------------------------------------

@server.tool(
    name="gal_search_directory_users",
    description="Searches directory accounts in Microsoft Entra ID by displayName, UPN, or email address."
)
def tool_search_directory_users(search_term: str, top: int = 20) -> Dict[str, Any]:
    return tools.search_directory_users(search_term=search_term, top=top)

@server.tool(
    name="gal_audit_external_mail_contacts",
    description="Audits external MailContacts in Exchange Online directory, optionally filtered by target domain."
)
def tool_audit_external_mail_contacts(domain_filter: Optional[str] = None) -> Dict[str, Any]:
    return tools.audit_external_mail_contacts(domain_filter=domain_filter)

# ------------------------------------------------------------------------------
# 7. Compliance, Retention & Legal Hold
# ------------------------------------------------------------------------------

@server.tool(
    name="compliance_audit_domain_signatures",
    description="Audits tenant-wide email signatures and legal disclaimers configured via Exchange Transport Rules."
)
def tool_audit_domain_signatures() -> Dict[str, Any]:
    return tools.audit_domain_signatures()

@server.tool(
    name="compliance_audit_retention_policies",
    description="Audits retention policies and MRM tags configured in Exchange Online for compliance/GDPR/LGPD."
)
def tool_audit_compliance_retention() -> Dict[str, Any]:
    return tools.audit_compliance_retention()

@server.tool(
    name="compliance_audit_litigation_hold",
    description="Audits mailboxes with Litigation Hold or Retention Hold enabled for legal preservation."
)
def tool_audit_litigation_hold(identity: Optional[str] = None) -> Dict[str, Any]:
    return tools.audit_litigation_hold(identity=identity)

@server.tool(
    name="compliance_audit_recoverable_items",
    description="Audits mailbox Recoverable Items and Deleted Items folder sizes and quotas for compliance and storage hygiene."
)
def tool_audit_mailbox_recoverable_items(identity: str) -> Dict[str, Any]:
    return tools.audit_mailbox_recoverable_items(identity=identity)

# ------------------------------------------------------------------------------
# 8. Mail Flow, DKIM & Connectors
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_message_trace",
    description="Traces message delivery events in Exchange Online by sender, recipient, status, and time window."
)
def tool_message_trace(
    sender_address: Optional[str] = None,
    recipient_address: Optional[str] = None,
    hours_back: int = 24,
    status_filter: Optional[str] = None,
    result_size: int = 50
) -> Dict[str, Any]:
    return tools.message_trace(
        sender_address=sender_address,
        recipient_address=recipient_address,
        hours_back=hours_back,
        status_filter=status_filter,
        result_size=result_size
    )

@server.tool(
    name="m365_verify_dkim_status",
    description="Verifies DKIM signing status and active key configuration for tenant accepted domains."
)
def tool_verify_dkim_status() -> Dict[str, Any]:
    return tools.verify_dkim_status()

@server.tool(
    name="m365_list_connectors",
    description="Lists inbound and outbound email connectors configured in Exchange Online."
)
def tool_list_connectors() -> Dict[str, Any]:
    return tools.list_connectors()

# ------------------------------------------------------------------------------
# 9. Exchange Online Protection (EOP) & Quarantine
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_check_quarantine",
    description="Checks quarantined messages in Microsoft Defender / EOP by recipient, sender, or hours back."
)
def tool_check_quarantine(
    recipient_address: Optional[str] = None,
    sender_address: Optional[str] = None,
    hours_back: int = 48,
    page_size: int = 50
) -> Dict[str, Any]:
    return tools.check_quarantine_messages(
        recipient_address=recipient_address,
        sender_address=sender_address,
        hours_back=hours_back,
        page_size=page_size
    )

@server.tool(
    name="m365_list_tenant_allow_list",
    description="Lists entries in the Microsoft Defender Tenant Allow/Block List (senders, domains, URLs)."
)
def tool_list_tenant_allow_list() -> Dict[str, Any]:
    return tools.list_tenant_allow_block_list()

@server.tool(
    name="m365_add_sender_to_allow_list",
    description="Adds a sender email or domain to the Tenant Allow List with an expiration period."
)
def tool_add_sender_to_allow_list(sender_or_domain: str, note: str = "Approved via M365 MCP") -> Dict[str, Any]:
    return tools.add_sender_to_tenant_allow_list(sender_or_domain=sender_or_domain, note=note)

# ------------------------------------------------------------------------------
# 10. Distribution Groups & Membership
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_list_distribution_groups",
    description="Lists distribution groups in Exchange Online with authentication and external delivery settings."
)
def tool_list_distribution_groups(result_size: int = 50) -> Dict[str, Any]:
    return tools.list_distribution_groups(result_size=result_size)

@server.tool(
    name="m365_get_group_members",
    description="Retrieves the member list of a distribution group."
)
def tool_get_group_members(group_identity: str) -> Dict[str, Any]:
    return tools.get_group_members(group_identity=group_identity)

@server.tool(
    name="m365_manage_group_member",
    description="Adds or removes a user from a distribution group (action: 'add' or 'remove')."
)
def tool_manage_group_member(group_identity: str, member_email: str, action: str = "add") -> Dict[str, Any]:
    return tools.manage_group_member(group_identity=group_identity, member_email=member_email, action=action)

@server.tool(
    name="m365_set_group_external_delivery",
    description="Configures whether a distribution group accepts messages from unauthenticated external senders."
)
def tool_set_group_external_delivery(group_identity: str, allow_external: bool = True) -> Dict[str, Any]:
    return tools.set_group_external_delivery(group_identity=group_identity, allow_external=allow_external)

# ------------------------------------------------------------------------------
# 11. Licenses & Subscription SKUs
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_list_license_skus",
    description="Lists all M365 license subscription SKUs showing enabled, consumed, and available seats."
)
def tool_list_license_skus() -> Dict[str, Any]:
    return tools.list_license_skus()

# ------------------------------------------------------------------------------
# 12. User Profile & Org Attributes
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_get_user_profile",
    description="Retrieves a user's corporate profile (department, jobTitle, phone numbers, office, account status)."
)
def tool_get_user_profile(user_upn: str) -> Dict[str, Any]:
    return tools.get_user_profile(user_upn=user_upn)

@server.tool(
    name="m365_update_user_profile",
    description="Updates user directory attributes (department, job title, mobile phone, business phone)."
)
def tool_update_user_profile(
    user_upn: str,
    department: Optional[str] = None,
    job_title: Optional[str] = None,
    mobile_phone: Optional[str] = None,
    business_phone: Optional[str] = None
) -> Dict[str, Any]:
    return tools.update_user_profile(
        user_upn=user_upn,
        department=department,
        job_title=job_title,
        mobile_phone=mobile_phone,
        business_phone=business_phone
    )

# ------------------------------------------------------------------------------
# 13. Operational Intelligence & Activity Digest
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_generate_daily_activity_summary",
    description="Analyzes mailbox messages and generates a categorized summary for daily operational reviews."
)
def tool_generate_daily_activity_summary(user_upn: str, top_messages: int = 25) -> Dict[str, Any]:
    return tools.generate_daily_activity_summary(user_upn=user_upn, top_messages=top_messages)

# ------------------------------------------------------------------------------
# 14. Advanced Mailbox Diagnostics & Routing Forensics
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_inspect_mailbox_folders",
    description="Recursively inspects a mailbox folder tree with item counts and unread metrics to detect deep subfolder routing."
)
def tool_inspect_mailbox_folders(user_upn: str, include_child_folders: bool = True) -> Dict[str, Any]:
    return tools.inspect_mailbox_folders(user_upn=user_upn, include_child_folders=include_child_folders)

@server.tool(
    name="graph_diagnose_mailbox_health",
    description="Runs automated diagnostic on a mailbox to identify missing emails, incoming message distribution across subfolders, and diverted rules."
)
def tool_diagnose_mailbox_health(user_upn: str, hours_back: int = 24) -> Dict[str, Any]:
    return tools.diagnose_mailbox_health(user_upn=user_upn, hours_back=hours_back)

@server.tool(
    name="graph_search_mailbox_messages",
    description="Searches mailbox messages using free-text queries, OData filters, or folder scope via Microsoft Graph."
)
def tool_search_mailbox_messages(
    user_upn: str,
    search_query: Optional[str] = None,
    filter_query: Optional[str] = None,
    folder_id: Optional[str] = None,
    top: int = 25
) -> Dict[str, Any]:
    return tools.search_mailbox_messages(
        user_upn=user_upn,
        search_query=search_query,
        filter_query=filter_query,
        folder_id=folder_id,
        top=top
    )

# ------------------------------------------------------------------------------
# 15. Calendar & Meetings (Microsoft 365 Calendar)
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_list_calendar_events",
    description="Retrieves scheduled events and meetings from a user's calendar with optional date range."
)
def tool_list_calendar_events(
    user_upn: str,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    top: int = 20
) -> Dict[str, Any]:
    return tools.list_calendar_events(
        user_upn=user_upn,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        top=top
    )

@server.tool(
    name="graph_create_calendar_event",
    description="Creates a new calendar event or Microsoft Teams meeting on behalf of the user."
)
def tool_create_calendar_event(
    user_upn: str,
    subject: str,
    start_iso: str,
    end_iso: str,
    attendees: Optional[List[str]] = None,
    body_content: str = "",
    location_name: str = "",
    is_online_meeting: bool = True
) -> Dict[str, Any]:
    return tools.create_calendar_event(
        user_upn=user_upn,
        subject=subject,
        start_iso=start_iso,
        end_iso=end_iso,
        attendees=attendees,
        body_content=body_content,
        location_name=location_name,
        is_online_meeting=is_online_meeting
    )

# ------------------------------------------------------------------------------
# 16. OneDrive & SharePoint Storage (ODSP)
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_list_onedrive_files",
    description="Lists files and subdirectories located in a user's OneDrive drive."
)
def tool_list_onedrive_files(user_upn: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
    return tools.list_onedrive_files(user_upn=user_upn, folder_id=folder_id)

@server.tool(
    name="graph_search_onedrive_files",
    description="Searches for documents and files across the user's OneDrive drive by keyword or filename."
)
def tool_search_onedrive_files(user_upn: str, query: str, top: int = 25) -> Dict[str, Any]:
    return tools.search_onedrive_files(user_upn=user_upn, query=query, top=top)

# ------------------------------------------------------------------------------
# 17. User & Organizational Hierarchy Awareness
# ------------------------------------------------------------------------------

@server.tool(
    name="graph_get_user_manager",
    description="Retrieves the direct reporting manager of a user in Microsoft Entra ID."
)
def tool_get_user_manager(user_upn: str) -> Dict[str, Any]:
    return tools.get_user_manager(user_upn=user_upn)

@server.tool(
    name="graph_get_user_direct_reports",
    description="Retrieves all direct reports (subordinates) for a manager."
)
def tool_get_user_direct_reports(user_upn: str) -> Dict[str, Any]:
    return tools.get_user_direct_reports(user_upn=user_upn)

@server.tool(
    name="graph_get_department_members",
    description="Queries active members of a specified corporate department."
)
def tool_get_department_members(department: str, top: int = 50) -> Dict[str, Any]:
    return tools.get_department_members(department=department, top=top)



# ------------------------------------------------------------------------------
# 14. SMTP Diagnostics, Authentication, Test Delivery & DNS
# ------------------------------------------------------------------------------

@server.tool(
    name="m365_test_smtp_connectivity",
    description="Tests low-level TCP socket connectivity and ESMTP handshake across SMTP ports (25, 587, 465) with latency and STARTTLS support."
)
def tool_test_smtp_connectivity(
    host: str = "smtp.office365.com",
    port: int = 587,
    timeout: int = 10
) -> Dict[str, Any]:
    return tools.test_smtp_connectivity(host=host, port=port, timeout=timeout)

@server.tool(
    name="m365_test_smtp_auth",
    description="Validates SMTP AUTH credentials in real time against Microsoft 365 with root-cause diagnostic guidance (535, licensing, MFA)."
)
def tool_test_smtp_auth(
    user: str,
    password: str,
    host: str = "smtp.office365.com",
    port: int = 587,
    use_tls: bool = True,
    timeout: int = 15
) -> Dict[str, Any]:
    return tools.test_smtp_auth(user=user, password=password, host=host, port=port, use_tls=use_tls, timeout=timeout)

@server.tool(
    name="m365_send_smtp_test_email",
    description="Sends an end-to-end test email via SMTP supporting Direct Send (port 25, no auth) or SMTP AUTH (port 587, authenticated)."
)
def tool_send_smtp_test_email(
    sender: str,
    recipient: str,
    host: str = "smtp.office365.com",
    port: int = 587,
    password: Optional[str] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    use_tls: bool = True
) -> Dict[str, Any]:
    return tools.send_smtp_test_email(
        sender=sender,
        recipient=recipient,
        host=host,
        port=port,
        password=password,
        subject=subject,
        body=body,
        use_tls=use_tls
    )

@server.tool(
    name="m365_audit_domain_dns_health",
    description="Audits email DNS records (MX, SPF, DMARC) for any domain, evaluates spoofing risks and validates outbound WAN IP."
)
def tool_audit_domain_dns_health(domain: str) -> Dict[str, Any]:
    return tools.audit_domain_dns_health(domain=domain)

@server.tool(
    name="m365_get_password_policy",
    description="Queries Microsoft Entra ID via Graph API to determine if a service account has 'DisablePasswordExpiration' enabled."
)
def tool_get_password_policy(user_upn: str) -> Dict[str, Any]:
    return tools.get_password_policy(user_upn=user_upn)

@server.tool(
    name="m365_set_password_never_expires",
    description="Sets or revokes the 'DisablePasswordExpiration' policy for a service account in Microsoft Entra ID."
)
def tool_set_password_never_expires(user_upn: str, never_expires: bool = True) -> Dict[str, Any]:
    return tools.set_password_never_expires(user_upn=user_upn, never_expires=never_expires)

@server.tool(
    name="m365_diagnose_smtp_relay_prerequisites",
    description="Performs comprehensive pre-flight audit for SMTP Relay and Direct Send (WAN IP, MX, ports 25/587, Inbound Connectors, SPF)."
)
def tool_diagnose_smtp_relay_prerequisites(domain: str) -> Dict[str, Any]:
    return tools.diagnose_smtp_relay_prerequisites(domain=domain)


def run_stdio():
    """Starts the MCP server using standard I/O (stdio) transport."""
    logger.info("Starting Enterprise M365 Governance MCP Server (stdio)...")
    server.run(transport="stdio")

if __name__ == "__main__":
    run_stdio()
