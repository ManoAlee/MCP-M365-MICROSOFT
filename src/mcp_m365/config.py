"""
Configuration loader for MCP M365 Governance Server.
Loads environment variables or optional config.json.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_JSON_PATH = PROJECT_ROOT / "config.json"

_config_data: Dict[str, Any] = {}
potential_config_paths = [
    CONFIG_JSON_PATH,
    PROJECT_ROOT.parent / "mcp_m365_governance" / "config.json",
    PROJECT_ROOT.parent / "config.json"
]

for cfg_path in potential_config_paths:
    if cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8-sig") as f:
                _config_data = json.load(f)
                if _config_data.get("TenantId") or _config_data.get("ClientId"):
                    break
        except Exception:
            continue

TENANT_ID: str = os.environ.get("M365_TENANT_ID", _config_data.get("TenantId", ""))
CLIENT_ID: str = os.environ.get("M365_CLIENT_ID", _config_data.get("ClientId", ""))
CLIENT_SECRET: str = os.environ.get("M365_CLIENT_SECRET", _config_data.get("ClientSecret", ""))
PRIMARY_ADMIN: str = os.environ.get("M365_PRIMARY_ADMIN", _config_data.get("PrimaryAdmin", ""))

LOG_LEVEL: str = os.environ.get("MCP_LOG_LEVEL", "INFO")
