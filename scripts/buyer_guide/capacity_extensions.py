"""Additional capacity denominators inferred from public quota telemetry."""
from __future__ import annotations

from typing import Any, Callable


def wrap_compute_capacity(
    original: Callable[[dict[str, Any], str, dict[str, float]], dict[str, Any]],
    models: dict[str, dict[str, Any]],
    blend_rate: Callable[[dict[str, Any], dict[str, float], dict[str, float] | None], float | None],
):
    """Extend the base calculator without duplicating its stable provider adapters."""

    def compute(plan: dict[str, Any], model_id: str, mix: dict[str, float]) -> dict[str, Any]:
        allowance = plan["allowance"]
        kind = allowance.get("kind")
        model = models[model_id]
        route_rates = plan.get("routeRates", {}).get(model_id)
        api_rate = blend_rate(model, mix, route_rates)
        basis = "subscription route" if route_rates else "public model API"

        if kind == "rawTokensEstimateRange":
            low = allowance["monthlyTokensLow"] / 1e6
            center = allowance["monthlyTokens"] / 1e6
            high = allowance["monthlyTokensHigh"] / 1e6
            out = {
                "kind": kind,
                "apiRatePerM": api_rate,
                "rateBasis": basis,
                "monthlyTokensMLow": low,
                "monthlyTokensM": center,
                "monthlyTokensMHigh": high,
                "capacityConfidence": allowance.get("capacityConfidence", "measured-range"),
            }
            if api_rate:
                out.update({
                    "allowanceUsdLow": low * api_rate,
                    "allowanceUsd": center * api_rate,
                    "allowanceUsdHigh": high * api_rate,
                })
            return out

        if kind == "rawTokensLowerBound":
            minimum = allowance["monthlyTokensMinimum"] / 1e6
            out = {
                "kind": kind,
                "apiRatePerM": api_rate,
                "rateBasis": basis,
                "monthlyTokensM": minimum,
                "monthlyTokensMMinimum": minimum,
                "capacityIsLowerBound": True,
                "effectiveCostIsUpperBound": True,
            }
            if api_rate:
                out["allowanceUsdMinimum"] = minimum * api_rate
            return out

        if kind == "standardTokens":
            multiplier = allowance.get("modelMultipliers", {}).get(model_id)
            if multiplier is None:
                return {"kind": kind, "apiRatePerM": api_rate, "rateBasis": basis}
            fresh_weight = allowance.get("freshWeight", 1.0)
            cache_weight = allowance.get("cacheReadWeight", 0.1)
            output_weight = allowance.get("outputWeight", 1.0)
            standard_per_raw = multiplier * (
                mix["fresh"] * fresh_weight
                + mix["cache"] * cache_weight
                + mix["output"] * output_weight
            )
            if standard_per_raw <= 0:
                return {"kind": kind, "apiRatePerM": api_rate, "rateBasis": basis}
            raw_tokens_m = allowance["monthlyStandardTokens"] / standard_per_raw / 1e6
            out = {
                "kind": kind,
                "apiRatePerM": api_rate,
                "rateBasis": basis,
                "monthlyTokensM": raw_tokens_m,
                "standardTokensPerRawToken": standard_per_raw,
                "modelStandardMultiplier": multiplier,
                "monthlyStandardTokens": allowance["monthlyStandardTokens"],
            }
            if api_rate:
                out["allowanceUsd"] = raw_tokens_m * api_rate
            return out

        return original(plan, model_id, mix)

    return compute
