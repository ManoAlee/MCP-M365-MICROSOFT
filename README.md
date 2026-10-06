<div align="center">

# ⚡ Enterprise Microsoft 365 MCP Server

**The definitive, production-grade Model Context Protocol (MCP) server for enterprise Microsoft 365, Exchange Online, Microsoft Entra ID, and Microsoft Graph administration.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol%20(FastMCP)-blueviolet.svg?style=for-the-badge)](https://modelcontextprotocol.io)
[![Tools: 51 Enterprise](https://img.shields.io/badge/Tools-51%20Enterprise%20Tools-success.svg?style=for-the-badge&logo=wakatime&logoColor=white)](#-tool-catalog-51-tools)
[![Microsoft Graph API](https://img.shields.io/badge/Microsoft%20Graph-v1.0%20%2F%20Beta-0078D4.svg?style=for-the-badge&logo=microsoft&logoColor=white)](https://learn.microsoft.com/en-us/graph/)
[![Exchange Online](https://img.shields.io/badge/Exchange%20Online-v3%20REST-0078D4.svg?style=for-the-badge&logo=microsoft-outlook&logoColor=white)](https://learn.microsoft.com/en-us/powershell/exchange/)
[![Security: Zero Leak](https://img.shields.io/badge/Security-Zero%20Hardcoding%20%7C%20RBAC-green.svg?style=for-the-badge)](#-security--enterprise-governance)

<p align="center">
  <a href="#-key-capabilities">Key Capabilities</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-tool-catalog-51-tools">Tool Catalog (51 Tools)</a> •
  <a href="#-client-configuration">Client Setup</a> •
  <a href="#-security--enterprise-governance">Security</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 🌟 Overview

The **Enterprise Microsoft 365 MCP Server** connects Large Language Models (LLMs) and autonomous AI coding agents (such as **Claude Desktop**, **Cursor**, **Antigravity IDE**, **Cline**, and **GitHub Copilot**) directly to enterprise Microsoft 365 tenants with institutional-grade security.

Equipped with **51 specialized tools across 18 operational pillars**, it fuses:
1. **Microsoft Graph REST API** (v1.0 & Beta) for ultra-fast, modern directory, messaging, calendar, files, and org awareness.
2. **Exchange Online Management v3 REST Engine** for deep administrative operations, transport rules, litigation holds, quarantine management, and mail flow forensics.
3. **SMTP & Messaging Infrastructure Engine** for low-level socket diagnostics, real-time SMTP AUTH credential validation, Direct Send testing, and DNS security posture auditing (MX, SPF, DMARC, anti-spoofing).

---

## 🚀 Key Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ENTERPRISE M365 CAPABILITIES                                  │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────────┤
│ 📅 Vacation & OOF Automation │ 🛡️ EOP Quarantine & Security │ 👥 Entra ID & User Lifecycle      │
│ • Scheduled HTML auto-replies│ • Threat message release     │ • Ex-employee shared conversion   │
│ • Date-bounded forward rules │ • Tenant Allow/Block Lists   │ • Org hierarchy & reporting lines │
│ • Multi-language signatures  │ • Phish/Spam remediation     │ • Never-expiring service creds    │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ ⚡ SMTP & Relay Engineering  │ ⚖️ Compliance & Forensics    │ 📁 OneDrive & SharePoint (ODSP)   │
│ • Real-time SMTP AUTH test   │ • Litigation hold audits     │ • File inventory & search         │
│ • Direct Send MX verification│ • Recoverable items purge    │ • Drive item metadata extraction  │
│ • SPF, MX & DMARC DNS health │ • Message trace (24-72h)     │ • Corporate document auditing     │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ 📬 Mailbox Deep Governance   │ 📆 Calendar & Meetings       │ 💬 Teams & Notification Webhooks  │
│ • Delegate & SendAs rights   │ • Meeting scheduling         │ • Adaptive Card alerts            │
│ • Shared mailbox automapping │ • Real-time calendar events  │ • Daily operations digest bot     │
│ • Folder retention & counts  │ • Availability inspection    │ • Incident dispatch channels      │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────────┘
```

---

## 🏛️ Architecture

```
                      ┌─────────────────────────────────────────┐
                      │   AI Agents & Coding Assistants         │
                      │ (Claude, Cursor, Antigravity, Cline)    │
                      └────────────────────┬────────────────────┘
                                           │ MCP Protocol (JSON-RPC stdio)
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Enterprise M365 MCP Server Core      │
                      │       FastMCP • Pydantic • RBAC         │
                      └───────┬────────────┬────────────┬───────┘
                              │            │            │
             ┌────────────────┘            │            └────────────────┐
             ▼                             ▼                             ▼
┌────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────┐
│  Microsoft Graph Engine│   │  Exchange Online Bridge   │   │ SMTP & DNS Diagnostics │
│  OAuth2 App Client     │   │  EXO v3 REST PowerShell   │   │ Sockets • RFC 5321     │
│  • Directory & Org     │   │  • Transport Rules        │   │ • Port 25 / 587 Check  │
│  • Mail, Calendar, ODSP│   │  • Quarantine & Holds     │   │ • Real-time SMTP AUTH  │
│  • Credential Policies │   │  • Mailbox Protocols      │   │ • MX, SPF & DMARC Audit│
└────────────────────────┘   └───────────────────────────┘   └────────────────────────┘
```

---

## ⚡ Quickstart

### 1. Prerequisites
* **Python 3.10+**
* An **App Registration in Microsoft Entra ID** with Graph permissions (e.g., `Directory.Read.All`, `Mail.ReadWrite`, `User.ReadWrite.All`)
* Exchange Online Administrator rights (if utilizing PowerShell Exchange features)

### 2. Installation

Clone and install dependencies:
```bash
git clone https://github.com/ManoAlee/MCP-M365-MICROSOFT.git
cd MCP-M365-MICROSOFT
pip install -r requirements.txt
```

### 3. Configuration (Zero-Trust Security)

Create a `.env` file or export environment variables:
```bash
export M365_TENANT_ID="00000000-0000-0000-0000-000000000000"
export M365_CLIENT_ID="00000000-0000-0000-0000-000000000000"
export M365_CLIENT_SECRET="your-azure-app-client-secret"
export M365_PRIMARY_ADMIN="admin@yourdomain.com"
export MCP_LOG_LEVEL="INFO"
```

*Alternatively, copy `config.example.json` to `config.json` (strictly ignored by `.gitignore`).*

---

## 🛠️ Tool Catalog (51 Tools)

### 1. Out of Office / Vacation Automation
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_get_vacation_status` | Exchange | Queries scheduled auto-reply status and forward rules. |
| `m365_configure_vacation` | Exchange | Schedules HTML auto-reply and optional date-bounded redirect rules. |
| `m365_disable_vacation` | Exchange | Immediately deactivates out-of-office autoreply and cleans temporary rules. |

### 2. Lifecycle & Ex-Employee Governance
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_audit_ex_employees` | Exchange | Audits offboarded user mailboxes, shared status, and forwarding rules. |
| `m365_convert_ex_employee_to_shared` | Exchange | Converts user mailbox to Shared Mailbox and sets forwarding target. |

### 3. Mailbox Operations & Permissions
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_get_mailbox_info` | Exchange | Deep inspection of mailbox type, protocols (OWA, MAPI, SMTP AUTH), and aliases. |
| `m365_list_mailboxes` | Exchange | Lists tenant mailboxes filtered by type (`UserMailbox`, `SharedMailbox`, `RoomMailbox`). |
| `m365_configure_shared_mailbox` | Exchange | Grants `FullAccess`, `SendAs`, configures automapping and Sent Items copy. |

### 4. Transport Rules & Mail Routing
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_list_inbox_rules` | Exchange | Lists all client-side Inbox Rules configured on a user's mailbox. |
| `m365_list_transport_rules` | Exchange | Lists tenant-wide Exchange Transport / Mail Flow rules with priority. |
| `m365_remove_inbox_rule` | Exchange | Removes a specific inbox rule by name or GUID. |

### 5. Microsoft Graph Email & Teams Notifications
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `graph_send_email` | Graph API | Dispatches emails via Microsoft Graph REST API (`/sendMail`) with HTML & attachments. |
| `graph_list_recent_messages` | Graph API | Fetches recent messages from Inbox or custom folders with OData query filters. |
| `graph_send_teams_notification` | Webhook | Sends high-impact Teams Adaptive Cards to operational webhooks. |

### 6. Directory, GAL & External Contacts
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `gal_search_directory_users` | Graph API | Searches Global Address List (GAL) users by displayName, email, or department. |
| `gal_audit_external_mail_contacts` | Exchange | Audits Mail Contacts in the directory against authoritative local registry. |

### 7. Compliance, Retention & Legal Hold
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `compliance_audit_signatures` | Graph API | Audits user profile attributes mapped to corporate signature policies. |
| `compliance_audit_retention` | Exchange | Audits retention policies, hold statuses, and litigation hold flags. |
| `compliance_audit_litigation_hold` | Exchange | Identifies all mailboxes currently placed under active Litigation Hold. |
| `compliance_audit_mailbox_recoverable_items`| Exchange | Audits Recoverable Items folder quotas and purge activity. |

### 8. Mail Flow, Message Trace & DKIM
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_message_trace` | Exchange | Runs Exchange Message Trace (24-72h) diagnosing delivery failures and NDRs. |
| `m365_verify_dkim_status` | Exchange | Validates DKIM signing status, selector records, and key rotation. |
| `m365_list_connectors` | Exchange | Inspects Inbound and Outbound connectors, TLS validation, and sender IPs. |

### 9. Exchange Online Protection (EOP) & Quarantine
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_check_quarantine` | Exchange | Queries quarantined messages filtered by reason (`Phish`, `Spam`, `Malware`). |
| `m365_list_tenant_allow_list` | Exchange | Lists tenant allow/block entries for senders, domains, and URLs. |
| `m365_add_sender_to_allow_list` | Exchange | Adds safe sender or domain to the Tenant Allow List with expiration. |

### 10. Groups & Distribution Lists
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_list_distribution_groups` | Exchange | Lists Distribution Groups, Mail-Enabled Security Groups, and M365 Groups. |
| `m365_get_group_members` | Exchange | Retrieves full member rosters and ownership for any group. |
| `m365_manage_group_member` | Exchange | Adds or removes member UPNs from a Distribution Group. |
| `m365_set_group_external_delivery` | Exchange | Toggles `RequireSenderAuthenticationEnabled` to permit external inbound mail. |

### 11. Licensing & SKU Management
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_list_license_skus` | Graph API | Audits subscribed SKUs, total enabled seats, consumed units, and pool availability. |

### 12. Profile Sync & Organization Management
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_get_user_profile` | Graph API | Queries full Entra ID profile (department, title, office, phone, manager). |
| `m365_update_user_profile` | Exchange/Entra | Updates corporate directory fields and syncs Exchange Address Book. |

### 13. Operational Intelligence & Bot
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `graph_generate_daily_activity_summary` | Graph API | Analyzes recent mailbox traffic and compiles structured operational digests. |

### 14. Advanced Mailbox Diagnostics & Routing Forensics
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `graph_inspect_mailbox_folders` | Graph API | Recursively inspects mailbox folder hierarchy with item counts and size. |
| `graph_diagnose_mailbox_health` | Graph API | Automated forensic diagnosis of message delivery destinations and rules. |
| `graph_search_mailbox_messages` | Graph API | Searches mailbox messages using KQL, subject keywords, or sender criteria. |

### 15. Calendar & Meeting Management
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_list_calendar_events` | Graph API | Retrieves calendar events in a date window with attendee RSVP statuses. |
| `m365_create_calendar_event` | Graph API | Creates enterprise meetings with Teams link, attendees, and HTML body. |

### 16. OneDrive & SharePoint Files (ODSP)
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_list_onedrive_files` | Graph API | Lists files and folders in a user's OneDrive root or specific subfolder. |
| `m365_search_onedrive_files` | Graph API | Searches documents across OneDrive and SharePoint drives by keyword. |

### 17. Organizational Hierarchy & Management Tree
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_get_user_manager` | Graph API | Retrieves a user's direct line manager from the organizational chart. |
| `m365_get_user_direct_reports` | Graph API | Retrieves all direct reports assigned to a supervisor or executive. |
| `m365_get_department_members` | Graph API | Lists all corporate directory users belonging to a specific department. |

### 18. SMTP Diagnostics, Authentication, Test Delivery & DNS Health ⚡
| Tool | Engine | Description |
| :--- | :---: | :--- |
| `m365_test_smtp_connectivity` | Network/Socket | Tests TCP socket reachability, DNS resolution, and ESMTP EHLO handshake (ports 25, 587, 465) with latency and STARTTLS verification. |
| `m365_test_smtp_auth` | SMTP Engine | Validates SMTP AUTH credentials in real time with root-cause diagnostic guidance for code 535 (licensing, MFA, basic auth policies). |
| `m365_send_smtp_test_email` | SMTP Engine | Sends end-to-end test emails supporting Direct Send (port 25, unauthenticated) or SMTP AUTH (port 587, authenticated). |
| `m365_audit_domain_dns_health` | DNS Engine | Audits domain email DNS health (MX, SPF, DMARC), assesses spoofing risks, and cross-references public WAN IP against authorized SPF entries. |
| `m365_get_password_policy` | Graph API | Queries Microsoft Entra ID via Graph API to determine if a service account has `DisablePasswordExpiration` enabled. |
| `m365_set_password_never_expires`| Graph/PowerShell | Sets or revokes `DisablePasswordExpiration` policy for automated service accounts. |
| `m365_diagnose_smtp_relay_prerequisites` | Hybrid Engine | Pre-flight audit for SMTP Relay & Direct Send (WAN IP, MX, ports 25/587, Inbound Connectors, and SPF). |

---

## 💻 Client Configuration

Add this server to your preferred MCP environment:

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "m365-governance": {
      "command": "python",
      "args": ["-m", "mcp_m365.server"],
      "cwd": "/path/to/MCP-M365-MICROSOFT",
      "env": {
        "M365_TENANT_ID": "your-tenant-id",
        "M365_CLIENT_ID": "your-client-id",
        "M365_CLIENT_SECRET": "your-client-secret",
        "M365_PRIMARY_ADMIN": "admin@yourdomain.com"
      }
    }
  }
}
```

### Cursor (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "m365-governance": {
      "command": "python",
      "args": ["-m", "mcp_m365.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Antigravity IDE (`mcp_config.json`)
```json
{
  "mcpServers": {
    "m365-governance": {
      "command": "python.exe",
      "args": ["-m", "mcp_m365.server"],
      "cwd": "C:\\path\\to\\MCP-M365-MICROSOFT"
    }
  }
}
```

---

## 🔒 Security & Enterprise Governance

This repository adheres to strict **Zero-Trust & Zero-Leak** security standards:

1. **Zero Hardcoded Secrets**: Absolutely no client IDs, secrets, tenant GUIDs, employee PII, or company domain names exist in the codebase. All runtime identity is injected strictly via environment variables.
2. **Robust `.gitignore` Guardrails**: Production configuration files (`config.json`, `.env`, `*.token_cache.bin`, logs) are enforced in `.gitignore`.
3. **Least Privilege Principle**: Supports granular Azure App Registration permission scopes. Read operations require only `Directory.Read.All` and `Mail.ReadWrite`.
4. **Defensive SMTP Testing**: Diagnostic test email utilities do not store credentials or bypass transport policies.

---

## 🧪 Testing & Validation

The server includes a comprehensive automated test suite verifying tool registration, Pydantic schemas, and Graph/Exchange integrations:

```bash
# Run unit tests
python -m unittest discover tests

# Output:
# ..............
# ----------------------------------------------------------------------
# Ran 14 tests in 0.003s
# OK (51 Tools Operational)
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <b>Built for Enterprise Cloud Architects, SecOps & AI Engineers</b><br>
  Maintained by <a href="https://github.com/ManoAlee">Alessandro Meneses (@ManoAlee)</a>
</div>
