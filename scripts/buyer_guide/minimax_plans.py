"""Current MiniMax Token Plan tiers and published M3 usage estimates."""
from __future__ import annotations

from typing import Any

WEEKS_PER_MONTH = 365.2425 / 12 / 7


def apply_minimax_plans(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] != "MiniMax Token Plan"]

    if "minimax-m2.7" in models:
        plans.append({
            "id": "minimax-starter", "provider": "MiniMax Token Plan", "plan": "Starter",
            "priceUsd": 10.0, "models": ["minimax-m2.7"],
            "allowance": {
                "kind": "requests",
                "monthlyQuota": 1_500 * 10 * WEEKS_PER_MONTH,
                "quotaPerRequest": {"minimax-m2.7": 1},
                "fiveHourRequests": 1_500,
                "weeklyRequests": 15_000,
                "weeklyMultiplierOfFiveHourQuota": 10,
            },
            "source": "https://platform.minimax.io/docs/guides/pricing-token-plan",
            "confidence": "official", "owned": False,
            "windows": "1,500 requests per rolling five hours; weekly quota is 10× the five-hour quota",
            "policy": "Token Plan API key for AI agents and coding tools",
            "note": "Starter remains request-denominated because the current subscription page does not publish a monthly raw-token estimate for this tier.",
            "currency": "USD", "originalPrice": 10.0, "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "request", "missingFields": ["observed token distribution per M2.7 request"],
            "researchStatus": "quantified-request", "sourceType": "primary-or-measured", "rankable": True,
        })

    for name, slug, price, tokens_b, five_h, weekly, concurrency in (
        ("Plus", "plus", 20, 1.7, 4_500, 45_000, "3–4"),
        ("Max", "max", 50, 5.1, 15_000, 150_000, "4–5"),
        ("Ultra", "ultra", 120, 12.5, None, None, "6–7"),
    ):
        if "minimax-m3" not in models:
            continue
        allowance = {
            "kind": "rawTokensEstimate",
            "monthlyTokens": tokens_b * 1_000_000_000,
            "publishedMonthlyTokensB": tokens_b,
            "publishedAssumption": "approximately 50K tokens per M3 coding call",
            "publishedMonthlyCodingCalls": int(tokens_b * 1_000_000_000 / 50_000),
            "agentConcurrency": concurrency,
        }
        if five_h is not None:
            allowance.update({"fiveHourRequests": five_h, "weeklyRequests": weekly,
                              "weeklyMultiplierOfFiveHourQuota": 10})
        plans.append({
            "id": f"minimax-{slug}", "provider": "MiniMax Token Plan", "plan": name,
            "priceUsd": float(price), "models": ["minimax-m3"], "allowance": allowance,
            "source": "https://platform.minimax.io/subscribe/token-plan", "confidence": "official",
            "owned": False,
            "windows": (f"{five_h:,} requests per rolling five hours; {weekly:,} per week" if five_h else "Published monthly M3 token estimate and concurrency"),
            "policy": "Token Plan API key, MiniMax Code, and supported coding tools",
            "note": "The raw-token figure is MiniMax's own monthly M3 estimate, derived from its published approximately-50K-token coding-call convention. Real request sizes vary.",
            "currency": "USD", "originalPrice": float(price), "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "token", "missingFields": ["actual workload-specific tokens per request"],
            "researchStatus": "official-estimate", "sourceType": "primary-or-measured", "rankable": True,
        })

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
