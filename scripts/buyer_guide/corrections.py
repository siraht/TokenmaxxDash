"""Small post-enrichment corrections that preserve every active monthly tier."""
from __future__ import annotations

from typing import Any


def apply_corrections(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    jetbrains_models = [model_id for model_id in (
        "claude-opus-5", "claude-fable-5", "claude-sonnet-5", "claude-haiku-4.5",
        "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna") if model_id in models]
    if not any(plan["id"] == "jetbrains-organization-pro" for plan in plans):
        plans.append({
            "id": "jetbrains-organization-pro", "provider": "JetBrains AI", "plan": "Organization Pro",
            "priceUsd": 20.0, "models": jetbrains_models, "allowance": {"kind": "apiPool", "monthlyUsd": 20},
            "source": "https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html",
            "confidence": "official", "owned": False, "windows": None,
            "policy": "organization IDE and integrated agents", "note": "20 AI Credits/user/month; one AI Credit equals $1.",
            "currency": "USD", "originalPrice": 20.0, "routeRates": {}, "monthlyUsdByModel": {}, "routeNotes": {},
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "token", "missingFields": [], "researchStatus": "quantified",
            "sourceType": "primary-or-measured", "rankable": True,
        })
    if not any(plan["id"] == "jetbrains-organization-ultimate" for plan in plans):
        plans.append({
            "id": "jetbrains-organization-ultimate", "provider": "JetBrains AI", "plan": "Organization Ultimate",
            "priceUsd": 60.0, "models": jetbrains_models, "allowance": {"kind": "apiPool", "monthlyUsd": 70},
            "source": "https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html",
            "confidence": "official", "owned": False, "windows": None,
            "policy": "organization IDE and integrated agents", "note": "70 AI Credits/user/month; one AI Credit equals $1.",
            "currency": "USD", "originalPrice": 60.0, "routeRates": {}, "monthlyUsdByModel": {}, "routeNotes": {},
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "token", "missingFields": [], "researchStatus": "quantified",
            "sourceType": "primary-or-measured", "rankable": True,
        })
    if not any(plan["id"] == "zed-business" for plan in plans):
        plans.append({
            "id": "zed-business", "provider": "Zed", "plan": "Business", "priceUsd": 30.0, "models": [],
            "allowance": {"kind": "hidden", "claim": "team coding subscription with edit predictions"},
            "source": "https://zed.dev/pricing", "confidence": "official-partial", "owned": False,
            "windows": None, "policy": "team coding", "note": "Team features and edit predictions are public; a separate numerical hosted-token pool is not established.",
            "currency": "USD", "originalPrice": 30.0, "routeRates": {}, "monthlyUsdByModel": {}, "routeNotes": {},
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "provider-hidden", "missingFields": ["absolute hosted-token pool", "served-model deduction table"],
            "researchStatus": "provider-hidden", "sourceType": "primary-or-measured", "rankable": False,
        })
    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
