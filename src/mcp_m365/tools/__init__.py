"""
Consolidated export of all M365 Governance MCP tools.
"""

from .vacation_tool import get_vacation_status, configure_vacation, disable_vacation
from .ex_employee_tool import audit_ex_employees, convert_to_shared_and_forward
from .mailbox_tool import get_mailbox_info, list_mailboxes, configure_shared_mailbox
from .rules_routing_tool import list_inbox_rules, list_transport_rules, remove_inbox_rule
from .graph_mailer_tool import send_graph_email, list_recent_messages, send_teams_notification
from .gal_contacts_tool import search_directory_users, audit_external_mail_contacts
from .compliance_tool import audit_domain_signatures, audit_compliance_retention, audit_litigation_hold, audit_mailbox_recoverable_items
from .mail_flow_tool import message_trace, verify_dkim_status, list_connectors
from .security_eop_tool import check_quarantine_messages, list_tenant_allow_block_list, add_sender_to_tenant_allow_list
from .groups_tool import list_distribution_groups, get_group_members, manage_group_member, set_group_external_delivery
from .licenses_tool import list_license_skus
from .profile_sync_tool import get_user_profile, update_user_profile
from .daily_bot_tool import generate_daily_activity_summary

__all__ = [
    # 1. Out of Office / Vacation
    "get_vacation_status",
    "configure_vacation",
    "disable_vacation",
    # 2. Lifecycle & Ex-Employees
    "audit_ex_employees",
    "convert_to_shared_and_forward",
    # 3. Mailbox Operations
    "get_mailbox_info",
    "list_mailboxes",
    "configure_shared_mailbox",
    # 4. Rules & Transport
    "list_inbox_rules",
    "list_transport_rules",
    "remove_inbox_rule",
    # 5. Graph Email & Teams Notifications
    "send_graph_email",
    "list_recent_messages",
    "send_teams_notification",
    # 6. Directory, GAL & Contacts
    "search_directory_users",
    "audit_external_mail_contacts",
    # 7. Compliance, Retention & Legal Hold
    "audit_domain_signatures",
    "audit_compliance_retention",
    "audit_litigation_hold",
    "audit_mailbox_recoverable_items",
    # 8. Mail Flow, DKIM & Connectors
    "message_trace",
    "verify_dkim_status",
    "list_connectors",
    # 9. Exchange Online Protection & Quarantine
    "check_quarantine_messages",
    "list_tenant_allow_block_list",
    "add_sender_to_tenant_allow_list",
    # 10. Groups & Distribution Lists
    "list_distribution_groups",
    "get_group_members",
    "manage_group_member",
    "set_group_external_delivery",
    # 11. Licenses
    "list_license_skus",
    # 12. Profile Sync
    "get_user_profile",
    "update_user_profile",
    # 13. Operational Intelligence & Bot
    "generate_daily_activity_summary"
]
