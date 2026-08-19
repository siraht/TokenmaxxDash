"""Additional fixed-price team tiers published alongside individual plans."""
from __future__ import annotations

from typing import Any


def _append(plans: list[dict[str, Any]], row: dict[str, Any]) -> None:
    if not any(plan["id"] == row["id"] for plan in plans):
        plans.append(row)


def apply_team_extras(plans: list[dict[str, Any]], top_catalog: list[str]) -> None:
    _append(plans, {
        "id": "command-team-pro", "provider": "Command Code", "plan": "Team Pro",
        "priceUsd": 40.0, "models": top_catalog,
        "allowance": {"kind": "apiPool", "monthlyUsd": 40},
        "source": "https://commandcode.ai/docs/resources/pricing-limits", "confidence": "official",
        "owned": False, "windows": "$12 per rolling 5 hours; $24 per rolling week",
        "policy": "team coding subscription", "note": "$40 of included model credits per seat/month; top-up credits are exempt from rolling windows.",
        "currency": "USD", "originalPrice": 40.0, "routeRates": {}, "monthlyUsdByModel": {},
        "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
        "comparisonClass": "token", "missingFields": [], "researchStatus": "quantified",
        "sourceType": "primary-or-measured", "rankable": True,
    })
    _append(plans, {
        "id": "cursor-teams", "provider": "Cursor", "plan": "Teams",
        "priceUsd": 40.0, "models": top_catalog,
        "allowance": {"kind": "hidden", "claim": "extended agent access plus team administration"},
        "source": "https://cursor.com/pricing", "confidence": "official-partial",
        "owned": False, "windows": "Agent and cloud-agent limits are product-specific",
        "policy": "team coding subscription", "note": "The per-seat price and team features are public; a numerical model pool comparable with Pro/Pro+/Ultra is not established.",
        "currency": "USD", "originalPrice": 40.0, "routeRates": {}, "monthlyUsdByModel": {},
        "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
        "comparisonClass": "provider-hidden",
        "missingFields": ["absolute included agent/model pool", "first-party versus third-party pool split",
                          "model-specific routing and deduction weights"],
        "researchStatus": "provider-hidden", "sourceType": "primary-or-measured", "rankable": False,
    })
    _append(plans, {
        "id": "kilo-teams-platform", "provider": "Kilo Code", "plan": "Teams Platform",
        "priceUsd": 15.0, "models": [],
        "allowance": {"kind": "platformCredits", "includedModelCreditsUsd": 0,
                      "billingModel": "BYOK or separately purchased provider/model usage"},
        "source": "https://kilo.ai/pricing", "confidence": "official",
        "owned": False, "windows": None, "policy": "team coding platform",
        "note": "This buys collaboration, administration, and analytics rather than a monthly model-token pool; Kilo Pass remains the separate inference subscription.",
        "currency": "USD", "originalPrice": 15.0, "routeRates": {}, "monthlyUsdByModel": {},
        "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
        "comparisonClass": "managed", "missingFields": [], "researchStatus": "quantified-managed",
        "sourceType": "primary-or-measured", "rankable": False,
    })
    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
