# MCP M365 Tools Reference Guide

Comprehensive documentation of all **33 enterprise tools** available in the **MCP M365 Governance Server**.

---

## 1. Out of Office & Vacation Management

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_vacation_status` | Exchange | `user_upn: str` | Inspects current AutoReply state, time window, and active redirect rules. |
| `m365_configure_vacation` | Exchange | `user_upn: str`, `start_date: str`, `end_date: str`, `return_date: str`, `signature_name: str`, `redirect_to: list[str]?`, `inform_team_handling: bool` | Schedules out-of-office message with HTML styling and optional mailbox redirection rule. |
| `m365_disable_vacation` | Exchange | `user_upn: str` | Immediately disables out-of-office auto-reply and purges temporary vacation redirect rules. |

---

## 2. Ex-Employee Governance & Lifecycle

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_audit_ex_employees` | Exchange | *None* | Detects disabled or departing accounts with pending NDR risks and unreleased licenses. |
| `m365_convert_ex_employee_to_shared` | Exchange | `legacy_upn: str`, `target_forward_email: str`, `hide_from_gal: bool` | Converts mailbox to free SharedMailbox, configures forwarding with copy, and hides from GAL. |

---

## 3. Mailbox Operations & Permissions

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_mailbox_info` | Exchange | `identity: str` | Fetches mailbox properties, quota usage, protocols, aliases, and forwarding configuration. |
| `m365_list_mailboxes` | Exchange | `recipient_type: str?`, `result_size: int` | Lists mailboxes filtered by type (`SharedMailbox`, `UserMailbox`, `RoomMailbox`). |
| `m365_configure_shared_mailbox` | Exchange | `identity: str`, `grant_full_access: list[str]?`, `grant_send_as: list[str]?`, `disable_automapping: bool`, `copy_sent_items: bool` | Grants delegated access, manages automapping behavior, and ensures sent items retention. |

---

## 4. Rules & Transport Routing

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_inbox_rules` | Exchange | `user_upn: str` | Lists all client and server-side inbox rules active on a target mailbox. |
| `m365_list_transport_rules` | Exchange | `filter_state: str?` | Lists tenant-wide Exchange transport and routing rules. |
| `m365_remove_inbox_rule` | Exchange | `user_upn: str`, `rule_name: str` | Removes an inbox rule from a mailbox by name. |

---

## 5. Microsoft Graph API & Notifications

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `graph_send_email` | Graph API | `from_user: str`, `to_recipients: list[str]`, `subject: str`, `html_body: str`, `cc_recipients: list[str]?` | Sends high-speed HTML emails directly through Graph API application endpoints. |
| `graph_list_recent_messages` | Graph API | `user_upn: str`, `top: int` | Retrieves recent emails from a target mailbox with read status and timestamps. |
| `graph_send_teams_notification` | HTTP / Webhook | `title: str`, `message: str`, `webhook_url: str?`, `theme_color: str` | Posts rich Adaptive Cards or MessageCards to Microsoft Teams channels. |

---

## 6. Directory, Global Address List (GAL) & Contacts

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `gal_search_directory_users` | Graph API | `search_term: str`, `top: int` | Searches Microsoft Entra ID directory accounts by display name, email, or department. |
| `gal_audit_external_mail_contacts` | Exchange | `domain_filter: str?` | Lists external MailContacts in Exchange Online, optionally filtered by target domain. |

---

## 7. Compliance, Retention & Legal Hold

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `compliance_audit_domain_signatures` | Exchange | *None* | Audits tenant-wide email signatures and legal disclaimers in transport rules. |
| `compliance_audit_retention_policies` | Exchange | *None* | Audits retention policies and tags configured for GDPR, LGPD, and compliance. |
| `compliance_audit_litigation_hold` | Exchange | `identity: str?` | Audits mailboxes with Litigation Hold or Retention Hold active for legal preservation. |
| `compliance_audit_recoverable_items` | Exchange | `identity: str` | Audits Recoverable Items and Deleted Items folder sizes and quotas for storage hygiene. |

---

## 8. Mail Flow, DKIM & Connectors

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_message_trace` | Exchange | `sender_address: str?`, `recipient_address: str?`, `hours_back: int`, `status_filter: str?`, `result_size: int` | Traces email delivery status, hops, and delivery failures in Exchange Online. |
| `m365_verify_dkim_status` | Exchange | *None* | Verifies DKIM cryptographic signing keys and status across all accepted domains. |
| `m365_list_connectors` | Exchange | *None* | Inspects inbound and outbound mail connectors. |

---

## 9. Exchange Online Protection (EOP) & Quarantine

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_check_quarantine` | Exchange | `recipient_address: str?`, `sender_address: str?`, `hours_back: int`, `page_size: int` | Queries messages blocked in Microsoft Defender quarantine. |
| `m365_list_tenant_allow_list` | Exchange | *None* | Lists allowed senders, domains, and URLs in the Tenant Allow/Block List. |
| `m365_add_sender_to_allow_list` | Exchange | `sender_or_domain: str`, `note: str` | Adds a trusted sender or partner domain to the Tenant Allow List. |

---

## 10. Distribution Groups & Membership

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_distribution_groups` | Exchange | `result_size: int` | Lists distribution lists and their external reception policies. |
| `m365_get_group_members` | Exchange | `group_identity: str` | Lists all members of a distribution group. |
| `m365_manage_group_member` | Exchange | `group_identity: str`, `member_email: str`, `action: str ('add'/'remove')` | Adds or removes members from a distribution group. |
| `m365_set_group_external_delivery` | Exchange | `group_identity: str`, `allow_external: bool` | Controls whether unauthenticated external senders can email the group. |

---

## 11. Licenses & Subscription SKUs

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_list_license_skus` | Graph API | *None* | Queries all M365 subscription SKUs, enabled licenses, consumed seats, and remaining capacity. |

---

## 12. User Profile & Org Attributes

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `m365_get_user_profile` | Graph API | `user_upn: str` | Fetches corporate profile (title, department, phone numbers, office, manager). |
| `m365_update_user_profile` | Graph API / Exchange | `user_upn: str`, `department: str?`, `job_title: str?`, `mobile_phone: str?`, `business_phone: str?` | Updates directory profile attributes. |

---

## 13. Operational Intelligence & Activity Digest

| Tool Name | Engine | Parameters | Description |
|---|---|---|---|
| `graph_generate_daily_activity_summary` | Graph API | `user_upn: str`, `top_messages: int` | Categorizes recent incoming messages into Urgent, Support, Financial, and General buckets. |
