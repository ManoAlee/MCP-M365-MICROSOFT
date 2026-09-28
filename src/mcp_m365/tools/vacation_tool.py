"""
Vacation & Out of Office Tool for Microsoft 365.
Configures Scheduled Auto-Replies with clean HTML entities and temporal server-side inbox rules.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.powershell_bridge import PowerShellBridge
from mcp_m365.core.logger import get_logger

logger = get_logger("VacationTool")
ps_bridge = PowerShellBridge()

def get_vacation_status(user_upn: str) -> Dict[str, Any]:
    """
    Checks the out-of-office (AutoReply) state and active vacation routing rules on a mailbox.
    
    :param user_upn: Target mailbox UPN (e.g., user@domain.com)
    """
    ps_cmd = f"""
$autoReply = Get-MailboxAutoReplyConfiguration -Identity '{user_upn}' | Select-Object AutoReplyState, StartTime, EndTime, ExternalAudience, InternalMessage
$rules = Get-InboxRule -Mailbox '{user_upn}' | Where-Object {{ $_.Name -like '*Vacation*' -or $_.Name -like '*Ferias*' -or $_.Name -like '*Ausencia*' }} | Select-Object Name, Enabled, Priority, ReceivedAfterDate, ReceivedBeforeDate, RedirectTo, ForwardTo

[PSCustomObject]@{{
    User = '{user_upn}'
    AutoReply = $autoReply
    VacationRules = $rules
}} | ConvertTo-Json -Depth 4
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "user": user_upn,
        "success": result["success"],
        "details": result["data"] if result["success"] else result["stderr"]
    }

def configure_vacation(
    user_upn: str,
    start_date: str,
    end_date: str,
    return_date: str,
    signature_name: str,
    redirect_to: Optional[List[str]] = None,
    inform_team_handling: bool = True
) -> Dict[str, Any]:
    """
    Schedules an Out-of-Office auto-reply and creates a server-side redirect rule active exclusively during the vacation window.
    
    :param user_upn: Target mailbox email
    :param start_date: Start date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    :param end_date: End date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    :param return_date: Official return date shown in message (DD/MM/YYYY)
    :param signature_name: Name displayed in email signature
    :param redirect_to: Optional list of colleagues receiving redirected emails
    :param inform_team_handling: If True, mentions incoming emails are handled by team
    """
    recipients_array = "@(" + ", ".join([f"'{email.strip()}'" for email in (redirect_to or []) if email.strip()]) + ")"
    has_redirect = bool(redirect_to and len(redirect_to) > 0)
    team_msg = "During this period, incoming messages will be redirected to the team." if inform_team_handling else ""

    ps_cmd = f"""
$StartTime = Get-Date '{start_date}'
$EndTime   = Get-Date '{end_date}'

$TemplateHtml = @"
<!DOCTYPE html>
<html lang="en">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>
<body style="font-size: 10pt; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; color: #333333; line-height: 1.6;">
    <p>Hello,</p>
    <p>Thank you for reaching out.</p>
    <p>I will be out of the office on vacation, returning on <strong>{return_date}</strong>.</p>
    <p>{team_msg}</p>
    <br>
    <p>Best regards,</p>
    <p><strong>{signature_name}</strong></p>
</body>
</html>
"@

Set-MailboxAutoReplyConfiguration -Identity '{user_upn}' `
    -AutoReplyState Scheduled `
    -StartTime $StartTime `
    -EndTime $EndTime `
    -InternalMessage $TemplateHtml `
    -ExternalAudience All `
    -ExternalMessage $TemplateHtml `
    -ErrorAction Stop

# Clean up prior vacation rules
Get-InboxRule -Mailbox '{user_upn}' | Where-Object {{ $_.Name -like '*Vacation*' -or $_.Name -like '*Ferias*' -or $_.Name -like '*Ausencia*' }} | Remove-InboxRule -Confirm:$false -ErrorAction SilentlyContinue

$RuleCreated = $false
if ({' $true ' if has_redirect else ' $false '}) {{
    $RuleName = "Vacation - Automatic Team Redirection"
    New-InboxRule -Mailbox '{user_upn}' `
        -Name $RuleName `
        -ReceivedAfterDate $StartTime `
        -ReceivedBeforeDate $EndTime `
        -RedirectTo {recipients_array} `
        -StopProcessingRules $false `
        -ErrorAction Stop | Out-Null
    $RuleCreated = $true
}}

[PSCustomObject]@{{
    User = '{user_upn}'
    Status = "Configured Successfully"
    StartTime = $StartTime
    EndTime = $EndTime
    ReturnDate = '{return_date}'
    RedirectRuleCreated = $RuleCreated
    RedirectTo = {recipients_array}
}} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "user": user_upn,
        "details": result["data"] if result["success"] else result["stderr"]
    }

def disable_vacation(user_upn: str) -> Dict[str, Any]:
    """
    Immediately disables auto-reply and removes vacation redirect rules.
    """
    ps_cmd = f"""
Set-MailboxAutoReplyConfiguration -Identity '{user_upn}' -AutoReplyState Disabled -ErrorAction Stop
Get-InboxRule -Mailbox '{user_upn}' | Where-Object {{ $_.Name -like '*Vacation*' -or $_.Name -like '*Ferias*' -or $_.Name -like '*Ausencia*' }} | Remove-InboxRule -Confirm:$false -ErrorAction SilentlyContinue
[PSCustomObject]@{{
    User = '{user_upn}'
    Status = "Out of Office Disabled and Vacation Rules Removed"
}} | ConvertTo-Json
"""
    result = ps_bridge.run_exchange_command(ps_cmd)
    return {
        "success": result["success"],
        "user": user_upn,
        "details": result["data"] if result["success"] else result["stderr"]
    }
