# MCP M365 Tools Reference Guide

Comprehensive, production-grade documentation of all **58 enterprise tools** across **18 operational pillars** available in the **Enterprise Microsoft 365 MCP Server**.

---

## 1. Out of Office & Vacation Management
Automates user leave, HTML out-of-office autoreplies, and cross-team coverage redirect rules.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_vacation_status` | Exchange | `user_upn: str` | Inspects current AutoReply state, scheduled time window, and active redirect rules. |
| `m365_configure_vacation` | Exchange | `user_upn: str`, `start_date: str`, `end_date: str`, `return_date: str`, `signature_name: str`, `redirect_to: list[str]?`, `inform_team_handling: bool` | Schedules out-of-office message with HTML styling and optional mailbox redirection rule. |
| `m365_disable_vacation` | Exchange | `user_upn: str`, `disable_transport_rules: bool = True` | Immediately disables out-of-office auto-reply, purges temporary vacation rules, and optionally disables active employee absence transport rules. |

---

## 2. Ex-Employee Governance & Lifecycle
Automates offboarding, zero-cost shared mailbox preservation, and eliminates NDR 550 5.1.10 errors.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_audit_ex_employees` | Exchange | *None* | Detects disabled or departing accounts with pending NDR risks and unreleased licenses. |
| `m365_convert_ex_employee_to_shared` | Exchange | `legacy_upn: str`, `target_forward_email: str`, `hide_from_gal: bool` | Converts mailbox to free SharedMailbox, configures forwarding with copy, and hides from GAL. |

---

## 3. Mailbox Operations, Hardening & Permissions
Deep administration of user/shared mailboxes, client CAS protocols, server-side forwarding, and proxy aliases.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_mailbox_info` | Exchange | `identity: str` | Fetches mailbox properties, quota usage, protocols, aliases, and forwarding configuration. |
| `m365_list_mailboxes` | Exchange | `recipient_type: str?`, `result_size: int = 100` | Lists mailboxes filtered by type (`SharedMailbox`, `UserMailbox`, `RoomMailbox`). |
| `m365_configure_shared_mailbox` | Exchange | `identity: str`, `grant_full_access: list[str]?`, `grant_send_as: list[str]?`, `disable_automapping: bool`, `copy_sent_items: bool` | Grants delegated access, manages automapping behavior, and ensures sent items retention. |
| `m365_set_mailbox_forwarding` | Exchange | `identity: str`, `forwarding_smtp_address: str?`, `deliver_to_mailbox_and_forward: bool = True` | Configures or clears server-side forwarding with optional message copy retention (`DeliverToMailboxAndForward`). |
| `m365_set_mailbox_protocol_access` | Exchange | `identity: str`, `owa_enabled: bool?`, `activesync_enabled: bool?`, `mapi_enabled: bool?`, `pop_enabled: bool?`, `imap_enabled: bool?` | Controls client CAS protocols (OWA, ActiveSync, MAPI, POP, IMAP) for security hardening. |
| `m365_manage_mailbox_alias` | Exchange | `identity: str`, `alias_email: str`, `action: str ('add'/'remove')` | Adds or removes secondary SMTP proxy email addresses/aliases on a mailbox. |

---

## 4. Rules & Transport Routing Lifecycle
Full CRUD and lifecycle control over client Inbox Rules and tenant-wide Exchange Transport / Mail Flow rules.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_inbox_rules` | Exchange | `user_upn: str` | Lists all client and server-side inbox rules active on a target mailbox. |
| `m365_list_transport_rules` | Exchange | `filter_state: str?` | Lists tenant-wide Exchange transport and routing rules with state and priority. |
| `m365_get_transport_rule_details` | Exchange | `rule_identity: str` | Deep inspection of conditions, actions, comments, state, and expiration of a transport rule. |
| `m365_disable_transport_rule` | Exchange | `rule_identity: str` | Immediately deactivates an active transport rule and verifies state. |
| `m365_enable_transport_rule` | Exchange | `rule_identity: str` | Enables an organization transport rule in Exchange Online. |
| `m365_remove_transport_rule` | Exchange | `rule_identity: str` | Permanently deletes an organization-level transport rule. |
| `m365_remove_inbox_rule` | Exchange | `user_upn: str`, `rule_name: str` | Removes an inbox rule from a mailbox by name. |

---

## 5. Microsoft Graph API & Notifications
High-speed modern messaging and Teams channel alerting via REST API.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `graph_send_email` | Graph API | `from_user: str`, `to_recipients: list[str]`, `subject: str`, `html_body: str`, `cc_recipients: list[str]?` | Sends high-speed HTML emails directly through Graph API application endpoints. |
| `graph_list_recent_messages` | Graph API | `user_upn: str`, `top: int = 10` | Retrieves recent emails from a target mailbox with read status and timestamps. |
| `graph_send_teams_notification` | HTTP / Webhook | `title: str`, `message: str`, `webhook_url: str?`, `theme_color: str` | Posts rich Adaptive Cards or MessageCards to Microsoft Teams channels. |

---

## 6. Directory, Global Address List (GAL) & Contacts
Enterprise directory discovery and external partner contact hygiene.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `gal_search_directory_users` | Graph API | `search_term: str`, `top: int = 10` | Searches Microsoft Entra ID directory accounts by display name, email, or department. |
| `gal_audit_external_mail_contacts` | Exchange | `domain_filter: str?` | Lists external MailContacts in Exchange Online, optionally filtered by target domain. |

---

## 7. Compliance, Retention & Legal Hold
Enforces legal preservation, GDPR/LGPD policies, and recoverable storage hygiene.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `compliance_audit_signatures` | Graph API | *None* | Audits user profile attributes mapped to corporate signature policies. |
| `compliance_audit_retention` | Exchange | *None* | Audits retention policies and tags configured for GDPR, LGPD, and compliance. |
| `compliance_audit_litigation_hold` | Exchange | `identity: str?` | Audits mailboxes with Litigation Hold or Retention Hold active for legal preservation. |
| `compliance_audit_mailbox_recoverable_items` | Exchange | `identity: str` | Audits Recoverable Items and Deleted Items folder sizes and quotas for storage hygiene. |

---

## 8. Mail Flow, DKIM & Connectors
Forensic message tracing, cryptographic key validation, and partner connectors.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_message_trace` | Exchange | `sender_address: str?`, `recipient_address: str?`, `hours_back: int = 24`, `status_filter: str?`, `result_size: int = 50` | Traces email delivery status, hops, and delivery failures in Exchange Online. |
| `m365_verify_dkim_status` | Exchange | *None* | Verifies DKIM cryptographic signing keys and status across all accepted domains. |
| `m365_list_connectors` | Exchange | *None* | Inspects inbound and outbound mail connectors. |

---

## 9. Exchange Online Protection (EOP) & Quarantine
Microsoft Defender quarantine management and threat allow lists.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_check_quarantine` | Exchange | `recipient_address: str?`, `sender_address: str?`, `hours_back: int = 24`, `page_size: int = 50` | Queries messages blocked in Microsoft Defender quarantine. |
| `m365_list_tenant_allow_list` | Exchange | *None* | Lists allowed senders, domains, and URLs in the Tenant Allow/Block List. |
| `m365_add_sender_to_allow_list` | Exchange | `sender_or_domain: str`, `note: str = "Added by MCP"` | Adds a trusted sender or partner domain to the Tenant Allow List. |

---

## 10. Distribution Groups & Membership
Distribution list governance, membership sync, and external sender authorization.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_distribution_groups` | Exchange | `result_size: int = 100` | Lists distribution lists and their external reception policies. |
| `m365_get_group_members` | Exchange | `group_identity: str` | Lists all members of a distribution group. |
| `m365_manage_group_member` | Exchange | `group_identity: str`, `member_email: str`, `action: str ('add'/'remove')` | Adds or removes members from a distribution group. |
| `m365_set_group_external_delivery` | Exchange | `group_identity: str`, `allow_external: bool` | Controls whether unauthenticated external senders can email the group. |

---

## 11. Licenses & Subscription SKUs
Tenant license consumption and seat availability auditing.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_license_skus` | Graph API | *None* | Queries all M365 subscription SKUs, enabled licenses, consumed seats, and remaining capacity. |

---

## 12. User Profile & Org Attributes
Directory profile synchronization across Entra ID and Exchange.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_user_profile` | Graph API | `user_upn: str` | Fetches corporate profile (title, department, phone numbers, office, manager). |
| `m365_update_user_profile` | Graph API / Exchange | `user_upn: str`, `department: str?`, `job_title: str?`, `mobile_phone: str?`, `business_phone: str?` | Updates directory profile attributes. |

---

## 13. Operational Intelligence & Activity Digest
Automated synthesis of incoming email traffic.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `graph_generate_daily_activity_summary` | Graph API | `user_upn: str`, `top_messages: int = 20` | Categorizes recent incoming messages into Urgent, Support, Financial, and General buckets. |

---

## 14. Advanced Mailbox Diagnostics & Routing Forensics
Deep folder hierarchy inspection, diverted message diagnostics, and KQL search.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `graph_inspect_mailbox_folders` | Graph API | `user_upn: str` | Recursively inspects mailbox folder hierarchy with item counts and size. |
| `graph_diagnose_mailbox_health` | Graph API | `user_upn: str` | Automated forensic diagnosis of message delivery destinations and rules. |
| `graph_search_mailbox_messages` | Graph API | `user_upn: str`, `query: str`, `folder_id: str?`, `top: int = 20` | Advanced message search with free-text, OData filters, and folder scope. |

---

## 15. Calendar & Meeting Management
Enterprise scheduling, availability checks, and Teams meeting creation.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_calendar_events` | Graph API | `user_upn: str`, `start_datetime: str?`, `end_datetime: str?`, `top: int = 10` | Queries scheduled events and meetings with datetime range filtering. |
| `m365_create_calendar_event` | Graph API | `user_upn: str`, `subject: str`, `start_datetime: str`, `end_datetime: str`, `attendees: list[str]?`, `is_online_meeting: bool = True`, `body_content: str?` | Schedule calendar events and generate Teams meeting links. |

---

## 16. OneDrive & SharePoint Files (ODSP)
Corporate document discovery and user storage auditing.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_onedrive_files` | Graph API | `user_upn: str`, `folder_id: str?`, `top: int = 25` | Browse files and directories in user OneDrive personal storage. |
| `m365_search_onedrive_files` | Graph API | `user_upn: str`, `query: str`, `top: int = 25` | Search corporate documents and files across OneDrive by keyword. |

---

## 17. Organizational Hierarchy & Management Tree
Live reporting structure, direct reports, and team roster awareness.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_user_manager` | Graph API | `user_upn: str` | Retrieves reporting manager from Entra ID corporate directory. |
| `m365_get_user_direct_reports` | Graph API | `user_upn: str` | List direct subordinates and reporting hierarchy for a leader. |
| `m365_get_department_members` | Graph API | `department: str`, `top: int = 25` | Discover collaborators and active team members in a department. |

---

## 18. SMTP Diagnostics, Authentication, Test Delivery & DNS Health ⚡
Low-level RFC 5321 socket diagnostics, real-time SMTP AUTH validation, and DNS spoofing analysis.

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_test_smtp_connectivity` | Network/Socket | `host: str`, `port: int = 587`, `use_starttls: bool = True`, `timeout: int = 10` | Tests TCP socket reachability, DNS resolution, and ESMTP EHLO handshake (ports 25, 587, 465) with latency and STARTTLS verification. |
| `m365_test_smtp_auth` | SMTP Engine | `username: str`, `password: str`, `host: str = 'smtp.office365.com'`, `port: int = 587` | Validates SMTP AUTH credentials in real time with root-cause diagnostic guidance for code 535 (licensing, MFA, basic auth policies). |
| `m365_send_smtp_test_email` | SMTP Engine | `to_email: str`, `from_email: str`, `subject: str = 'M365 SMTP Test'`, `body_text: str?`, `host: str = 'smtp.office365.com'`, `port: int = 587`, `username: str?`, `password: str?` | Sends end-to-end test emails supporting Direct Send (port 25, unauthenticated) or SMTP AUTH (port 587, authenticated). |
| `m365_audit_domain_dns_health` | DNS Engine | `domain: str`, `check_ip: str?` | Audits domain email DNS health (MX, SPF, DMARC), assesses spoofing risks, and cross-references public WAN IP against authorized SPF entries. |
| `m365_get_password_policy` | Graph API | `user_upn: str` | Queries Microsoft Entra ID via Graph API to determine if a service account has `DisablePasswordExpiration` enabled. |
| `m365_set_password_never_expires` | Graph/PowerShell | `user_upn: str`, `never_expires: bool = True` | Sets or revokes `DisablePasswordExpiration` policy for automated service accounts. |
| `m365_diagnose_smtp_relay_prerequisites` | Hybrid Engine | `domain: str`, `outbound_ip: str?` | Pre-flight audit for SMTP Relay & Direct Send (WAN IP, MX, ports 25/587, Inbound Connectors, and SPF). |
