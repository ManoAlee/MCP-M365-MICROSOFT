"""
PowerShell bridge for Exchange Online Management cmdlets.
Executes commands through isolated temporary scripts to eliminate escaping issues and outputs JSON.
"""

import json
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional
from mcp_m365.config import PRIMARY_ADMIN
from mcp_m365.core.logger import get_logger

logger = get_logger("PowerShellBridge")

class PowerShellBridge:
    def __init__(self, admin_upn: Optional[str] = None):
        self.admin_upn = admin_upn or PRIMARY_ADMIN

    def run_exchange_command(self, ps_command: str, timeout: int = 180) -> Dict[str, Any]:
        """
        Executes an Exchange Online command block via Connect-ExchangeOnline.
        Connects using -DisableWAM in non-interactive sessions.
        """
        auth_line = f"Connect-ExchangeOnline -UserPrincipalName '{self.admin_upn}' -DisableWAM -ShowBanner:$false -ShowProgress:$false -ErrorAction Stop | Out-Null" if self.admin_upn else "Connect-ExchangeOnline -DisableWAM -ShowBanner:$false -ShowProgress:$false -ErrorAction Stop | Out-Null"

        wrapped_command = f"""
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Import-Module ExchangeOnlineManagement -ErrorAction Stop
{auth_line}
try {{
    {ps_command}
}} finally {{
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}}
"""
        temp_script = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", encoding="utf-8-sig", delete=False) as f:
                f.write(wrapped_command)
                temp_script = f.name

            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_script]
            logger.info(f"Running Exchange Online block: {ps_command[:80]}...")

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            success = proc.returncode == 0
        finally:
            if temp_script and os.path.exists(temp_script):
                try:
                    os.remove(temp_script)
                except Exception:
                    pass

        parsed_json: Optional[Any] = None
        if success and proc.stdout:
            raw_out = proc.stdout.strip()
            # 1. Direct JSON parse
            try:
                parsed_json = json.loads(raw_out)
            except Exception:
                # 2. Extract JSON array or object substring
                import re
                match = re.search(r'(\[.*\]|\{.*\})', raw_out, re.DOTALL)
                if match:
                    try:
                        parsed_json = json.loads(match.group(1))
                    except Exception:
                        pass

        return {
            "success": success,
            "exit_code": proc.returncode,
            "data": parsed_json if parsed_json is not None else proc.stdout.strip(),
            "raw_stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip()
        }

_default_bridge = PowerShellBridge()

def execute_exchange_script(ps_command: str, timeout: int = 180) -> Dict[str, Any]:
    """Convenience module function to execute an Exchange script using default bridge."""
    return _default_bridge.run_exchange_command(ps_command, timeout=timeout)
