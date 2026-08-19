"""Neuralwatt energy subscriptions represented as model-specific typical-request capacity."""
from __future__ import annotations

from typing import Any

ENERGY_SNAPSHOT_DATE = "2026-08-19"


def apply_energy_plans(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] not in {"Neural Watt", "Neuralwatt", "Neuralwatt Cloud"}]

    # Neuralwatt publishes a trailing-seven-day average energy per request.
    # These values are a dated snapshot because they move as request size,
    # output length, cache mix, and serving efficiency change.
    typical_wh = {
        "deepseek-v4-flash": 0.21882,
        "glm-5.2": 1.94,
        "gemma-4-31b": 0.04243,
        "kimi-k2.7-code": 0.66173,
        "kimi-k3": 6.78,
        "qwen3.6-35b": 0.03582,
    }
    typical_wh = {model_id: value for model_id, value in typical_wh.items() if model_id in models}
    route_rates = {
        "deepseek-v4-flash": {"fresh": 0.14, "cache": 0.03, "output": 0.28},
        "glm-5.2": {"fresh": 1.45, "cache": 0.14, "output": 4.50},
        "gemma-4-31b": {"fresh": 0.14, "cache": 0.01, "output": 0.42},
        "kimi-k2.7-code": {"fresh": 0.95, "cache": 0.10, "output": 4.00},
        "kimi-k3": {"fresh": 3.00, "cache": 0.30, "output": 15.00},
        "qwen3.6-35b": {"fresh": 0.29, "cache": 0.03, "output": 1.15},
    }
    route_rates = {model_id: value for model_id, value in route_rates.items() if model_id in models}

    for name, slug, price, kwh, overage in (
        ("Basic", "basic", 20, 2.35, 8.50),
        ("Standard", "standard", 50, 6.25, 8.00),
        ("Pro", "pro", 100, 13.33, 7.50),
    ):
        plans.append({
            "id": f"neuralwatt-{slug}", "provider": "Neuralwatt Cloud", "plan": name,
            "priceUsd": float(price), "models": list(typical_wh),
            "allowance": {
                "kind": "requests",
                "monthlyQuota": kwh * 1000,
                "quotaUnit": "Wh",
                "quotaPerRequest": typical_wh,
                "monthlyKwh": kwh,
                "overageUsdPerKwh": overage,
                "paygUsdPerKwh": 10.00,
                "typicalEnergyWhPerRequest": typical_wh,
                "measurementWindow": "trailing seven days",
                "energySnapshotDate": ENERGY_SNAPSHOT_DATE,
            },
            "source": "https://portal.neuralwatt.com/pricing", "confidence": "official",
            "owned": False, "windows": "Monthly energy allocation; no hard usage cap after allocation",
            "policy": "OpenAI-compatible inference API and coding agents",
            "note": f"Request capacities use Neuralwatt's trailing-seven-day average energy snapshot dated {ENERGY_SNAPSHOT_DATE}. Actual energy varies by prompt size, output length, cache rate, model, and serving changes, so no fixed raw-token allowance is inferred.",
            "currency": "USD", "originalPrice": float(price), "routeRates": route_rates,
            "monthlyUsdByModel": {},
            "routeNotes": {
                model_id: f"Typical-request capacity uses Neuralwatt's trailing-seven-day average energy captured {ENERGY_SNAPSHOT_DATE}; refresh before making a purchase decision."
                for model_id in typical_wh
            },
            "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "request",
            "missingFields": ["fixed tokens per request", "stable energy per million tokens independent of workload mix"],
            "researchStatus": "quantified-live-energy", "sourceType": "primary-or-measured", "rankable": True,
        })

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
