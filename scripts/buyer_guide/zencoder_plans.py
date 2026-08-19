"""Current Zencoder credit plans represented as model-specific typical requests."""
from __future__ import annotations

from typing import Any


def apply_zencoder_plans(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] != "Zencoder"]

    multipliers = {
        "claude-haiku-4.5": 1.0,
        "claude-sonnet-4.6": 3.0,
        "claude-opus-4.6": 5.0,
        "claude-opus-4.7": 5.0,
        "gemini-3.1-pro": 2.0,
        "gemini-3-flash": 1.0,
        "gpt-5.3-codex": 2.0,
        "gpt-5.4": 2.5,
        "gpt-5.4-mini": 1.25,
        "gpt-5.5": 5.0,
        "grok-code-fast-1": 0.25,
    }
    multipliers = {model_id: multiplier for model_id, multiplier in multipliers.items() if model_id in models}

    # Zencoder says a typical Sonnet 4.6 request averages roughly 250–300
    # credits and Sonnet has a 3× model multiplier. The central baseline below
    # uses 275/3 credits for a 1× model. This is a typical-request comparison,
    # not a fixed token conversion.
    baseline_central = 275.0 / 3.0
    baseline_low = 100.0 / 3.0
    baseline_high = 500.0 / 3.0

    all_models = list(multipliers)
    pro_models = [model_id for model_id in all_models if model_id not in {"claude-opus-4.6", "claude-opus-4.7", "gpt-5.5"}]
    for name, slug, price, credits, model_ids in (
        ("Pro", "pro", 45, 30_000, pro_models),
        ("Pro Plus", "pro-plus", 95, 80_000, all_models),
        ("Pro Max", "pro-max", 195, 180_000, all_models),
    ):
        per_request = {model_id: baseline_central * multipliers[model_id] for model_id in model_ids}
        plans.append({
            "id": f"zencoder-{slug}", "provider": "Zencoder", "plan": name,
            "priceUsd": float(price), "models": model_ids,
            "allowance": {
                "kind": "requests",
                "monthlyQuota": credits,
                "quotaUnit": "Zencoder credit",
                "quotaPerRequest": per_request,
                "monthlyCredits": credits,
                "modelMultipliers": {model_id: multipliers[model_id] for model_id in model_ids},
                "typicalOneXRequestCredits": baseline_central,
                "typicalOneXRequestCreditsLow": baseline_low,
                "typicalOneXRequestCreditsHigh": baseline_high,
                "typicalSonnet46RequestCredits": 275,
                "typicalSonnet46RequestCreditsRange": [100, 500],
            },
            "source": "https://docs.zencoder.ai/faq/pricing", "confidence": "official",
            "owned": False, "windows": "Monthly plan credits expire; paid top-ups remain until consumed",
            "policy": "interactive IDE coding agent; BYOK supported on every plan",
            "note": "Typical requests are derived from Zencoder's published Sonnet 4.6 average and official model multipliers. Credits vary with prompt size, response length, and model, so these are request estimates rather than raw-token limits.",
            "currency": "USD", "originalPrice": float(price), "routeRates": {},
            "monthlyUsdByModel": {},
            "routeNotes": {
                model_id: "Typical-request economics use Zencoder's 275-credit central Sonnet 4.6 example normalized by the official model multiplier."
                for model_id in model_ids
            },
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "request",
            "missingFields": ["actual per-request prompt and output distribution", "raw tokens represented by one Zencoder credit",
                              "Auto and Auto+ routed-model composition"],
            "researchStatus": "quantified-typical-request", "sourceType": "primary-or-measured", "rankable": True,
        })

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
