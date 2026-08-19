"""Current market corrections discovered after the broad snapshot was generated."""
from __future__ import annotations

from typing import Any

WEEKS_PER_MONTH = 365.2425 / 12 / 7
EUR_USD = 1.1572


def _replace_provider(plans: list[dict[str, Any]], provider: str, replacement: list[dict[str, Any]]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] != provider]
    plans.extend(replacement)


def apply_market_updates(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    ozore_models = [model_id for model_id in (
        "gpt-5.6-sol", "claude-opus-5", "glm-5.2", "deepseek-v4-pro",
        "minimax-m3", "mimo-v2.5-pro") if model_id in models]
    # Ozore's public table currently gives fresh-input/output prices. Cache reads
    # are conservatively charged at the fresh-input rate until a separate cache
    # price is exposed in billing documentation or measured exports.
    ozore_rates = {
        "gpt-5.6-sol": {"fresh": 3.25, "output": 19.50},
        "claude-opus-5": {"fresh": 3.25, "output": 16.25},
        "glm-5.2": {"fresh": 0.91, "output": 2.86},
        "deepseek-v4-pro": {"fresh": 0.28, "output": 0.57},
        "minimax-m3": {"fresh": 0.21, "output": 0.84},
        "mimo-v2.5-pro": {"fresh": 0.30, "output": 0.61},
    }
    _replace_provider(plans, "Ozore", [
        {
            "id": f"ozore-{slug}", "provider": "Ozore", "plan": name,
            "priceUsd": float(price), "models": ozore_models,
            "allowance": {"kind": "apiPool", "monthlyUsd": pool},
            "source": "https://ozore.com/", "confidence": "official",
            "owned": False, "windows": "Monthly credits refresh; separately purchased top-ups roll over",
            "policy": "OpenAI-compatible API and coding tools", "currency": "USD", "originalPrice": float(price),
            "routeRates": {model_id: ozore_rates[model_id] for model_id in ozore_models},
            "monthlyUsdByModel": {}, "routeNotes": {
                model_id: "The public table exposes fresh-input and output prices only; cache reads are conservatively priced as fresh input in Tokenmaxx."
                for model_id in ozore_models
            },
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "token", "missingFields": ["separate Ozore cache-read price"],
            "researchStatus": "quantified-conservative-cache", "sourceType": "primary-or-measured", "rankable": True,
            "note": f"${pool:g} monthly credits—double the ${price:g} subscription price—spendable across the catalog at Ozore's published discounted token rates.",
        }
        for name, slug, price, pool in (("Basic", "basic", 10, 20), ("Pro", "pro", 35, 70))
    ])

    _replace_provider(plans, "AI Router", [
        {
            "id": f"ai-router-{slug}", "provider": "AI Router", "plan": name,
            "priceUsd": round(eur_price * EUR_USD, 2), "models": [],
            "allowance": {"kind": "workUnits", "monthlyCredits": credits,
                          "simpleRequestCredits": 1, "moderateRequestCredits": 3,
                          "complexRequestCredits": 5, "classifierCredits": 0},
            "source": "https://airouter.it/", "confidence": "official",
            "owned": False, "windows": None, "policy": "OpenAI/Anthropic-compatible routed API and MCP",
            "currency": "EUR", "originalPrice": eur_price, "routeRates": {},
            "monthlyUsdByModel": {}, "routeNotes": {}, "modelAllowanceFraction": {},
            "accessByModel": {}, "supplemental": False, "comparisonClass": "managed",
            "missingFields": ["realized model distribution by complexity level", "tokens per routed request"],
            "researchStatus": "quantified-managed", "sourceType": "primary-or-measured", "rankable": False,
            "note": "The router chooses a model by complexity. Credits are exact, but a credit is a routed request class rather than a fixed number of model tokens.",
        }
        for name, slug, eur_price, credits in (("Starter", "starter", 19, 10_000),
                                                ("Pro", "pro", 49, 50_000),
                                                ("Business", "business", 149, 200_000))
    ])

    qwen_plans = {
        "catalog-qwen-global-lite": (2_500, 8),
        "catalog-qwen-global-standard": (10_000, 25),
        "catalog-qwen-global-pro": (40_000, 80),
    }
    for plan in plans:
        if plan["id"] not in qwen_plans or "qwen3.6-plus" not in models:
            continue
        weekly_credits, expected_price = qwen_plans[plan["id"]]
        plan["priceUsd"] = float(expected_price)
        plan["models"] = ["qwen3.6-plus"]
        plan["allowance"] = {
            "kind": "credits", "monthlyCredits": weekly_credits * WEEKS_PER_MONTH,
            "weeklyCredits": weekly_credits,
            "creditRatesPerM": {"qwen3.6-plus": {"fresh": 200, "cache": 20, "output": 1_200}},
        }
        plan["comparisonClass"] = "token"
        plan["researchStatus"] = "secondary-derived"
        plan["confidence"] = "secondary"
        plan["missingFields"] = ["current primary-source global-plan confirmation",
                                 "complete live multiplier table for models beyond Qwen3.6 Plus"]
        plan["rankable"] = True
        plan["note"] = "The weekly credit count is maintained by current comparison trackers; the Qwen3.6 Plus credit conversion comes from Alibaba's official worked example."

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
