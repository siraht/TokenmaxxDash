"""Work-credit subscriptions whose units cannot be reduced to raw model tokens."""
from __future__ import annotations

from typing import Any


def apply_work_credit_plans(plans: list[dict[str, Any]]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] != "Codebuff"]

    # Current public pricing confirms $100/$200/$500 tiers at 1×/2.5×/7×
    # and $0.01 PAYG credits. The absolute monthly credit counts are maintained
    # by the current coding-plan tracker and remain secondary-derived evidence.
    for name, slug, price, multiplier, credits in (
        ("1×", "1x", 100, 1.0, 16_800),
        ("2.5×", "2-5x", 200, 2.5, 42_000),
        ("7×", "7x", 500, 7.0, 117_500),
    ):
        plans.append({
            "id": f"codebuff-{slug}", "provider": "Codebuff", "plan": name,
            "priceUsd": float(price), "models": [],
            "allowance": {
                "kind": "workUnits",
                "monthlyCredits": credits,
                "paygUsdPerCredit": 0.01,
                "paygEquivalentUsd": credits * 0.01,
                "officialRelativeMultiplier": multiplier,
            },
            "source": "https://codingplan.cyberwald.com/plans/codebuff/", "confidence": "secondary",
            "owned": False, "windows": "Monthly plan credits; PAYG top-ups available",
            "policy": "Codebuff coding agent",
            "note": "The price and 1×/2.5×/7× tiers are official. Absolute monthly credit counts are secondary-derived and should be rechecked against the in-product billing page. A Codebuff credit is a work/billing unit, not a raw model token.",
            "currency": "USD", "originalPrice": float(price), "routeRates": {},
            "monthlyUsdByModel": {}, "routeNotes": {}, "modelAllowanceFraction": {},
            "accessByModel": {}, "supplemental": False,
            "comparisonClass": "managed",
            "missingFields": ["served-model routing by task", "raw tokens represented by one Codebuff credit",
                              "credits consumed by a standardized external coding task"],
            "researchStatus": "secondary-derived-work-credits", "sourceType": "secondary",
            "rankable": False,
        })

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
