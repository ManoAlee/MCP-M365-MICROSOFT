"""
Licensing & SKU Governance Tool for Microsoft 365.
"""

from typing import Any, Dict, List, Optional
from mcp_m365.core.graph_client import GraphClient
from mcp_m365.core.logger import get_logger

logger = get_logger("LicensesTool")
graph_client = GraphClient()

def list_license_skus() -> Dict[str, Any]:
    """
    Retrieves all licensing SKUs assigned to the tenant, showing enabled, consumed, and available units.
    """
    try:
        endpoint = "subscribedSkus"
        res = graph_client.request("GET", endpoint).json()
        skus = res.get("value", [])

        summary = []
        for s in skus:
            prepaid = s.get("prepaidUnits", {})
            enabled = prepaid.get("enabled", 0)
            consumed = s.get("consumedUnits", 0)
            available = enabled - consumed

            summary.append({
                "sku_id": s.get("skuId"),
                "sku_part_number": s.get("skuPartNumber"),
                "total_enabled": enabled,
                "consumed": consumed,
                "available": available,
                "applies_to": s.get("appliesTo")
            })

        return {
            "success": True,
            "total_skus": len(summary),
            "licenses": summary
        }
    except Exception as e:
        logger.error(f"Error querying SKUs: {e}")
        return {"success": False, "error": str(e)}
