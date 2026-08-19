"""Promote broad-catalog quota facts into useful native-unit comparisons."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WEEKS_PER_MONTH = 365.2425 / 12 / 7


def _classify(plan: dict[str, Any]) -> None:
    kind = plan.get("allowance", {}).get("kind", "hidden")
    models = plan.get("models", [])
    missing = list(plan.get("missingFields", []))
    if kind in {"apiPool", "apiPoolRange", "credits", "rawTokens", "rawTokensEstimate"}:
        plan["comparisonClass"] = "token"
        plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "quantified"
        if not models:
            missing.append("exact served-model catalog")
    elif kind == "requests":
        plan["comparisonClass"] = "request"
        plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "quantified-request"
        missing.append("observed token distribution per request")
    elif kind in {"weightedPlanTokens", "relative"}:
        plan["comparisonClass"] = "relative"
        plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "official-partial"
        missing.append("complete per-model deduction weights")
    elif kind in {"managedTasks", "workUnits", "platformCredits", "publishedValue", "managedTokens", "requestWindow", "segmentedPools"}:
        plan["comparisonClass"] = "managed"
        plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "quantified-managed"
        missing.extend(["model-token conversion", "externally comparable task-size distribution"])
    elif kind == "unlimited":
        plan["comparisonClass"] = "managed"
        plan["researchStatus"] = "fair-use"
        missing.extend(["sustained throughput ceiling", "fair-use throttling threshold", "model-token distribution"])
    plan["missingFields"] = list(dict.fromkeys(missing))
    plan["rankable"] = plan.get("comparisonClass") in {"token", "request"} and bool(models)


def apply_native_units(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]], data_dir: Path) -> None:
    try:
        broad = json.loads((data_dir / "plans.json").read_text())
    except (OSError, json.JSONDecodeError):
        return
    broad_by_id = {row["id"]: row for row in broad}

    for plan in plans:
        if not plan["id"].startswith("catalog-"):
            continue
        broad_row = broad_by_id.get(plan["id"].removeprefix("catalog-"))
        if not broad_row:
            continue
        quotas = broad_row.get("quotas") or {}
        allowance_type = (broad_row.get("allowanceType") or "").lower()
        current_kind = plan.get("allowance", {}).get("kind")

        # Preserve stronger provider-specific adapters.
        if current_kind not in {"hidden", None}:
            _classify(plan)
            continue

        if isinstance(quotas.get("monthlyModelValueUsd"), (int, float)):
            plan["allowance"] = {"kind": "apiPool" if plan.get("models") else "publishedValue",
                                 "monthlyUsd": quotas["monthlyModelValueUsd"]}
        elif isinstance(quotas.get("monthlyUsd"), (int, float)):
            plan["allowance"] = {"kind": "apiPool" if plan.get("models") else "publishedValue",
                                 "monthlyUsd": quotas["monthlyUsd"]}
        elif isinstance(quotas.get("monthlyTokenCreditsUsd"), (int, float)):
            plan["allowance"] = {"kind": "apiPool" if plan.get("models") else "publishedValue",
                                 "monthlyUsd": quotas["monthlyTokenCreditsUsd"]}
        elif isinstance(quotas.get("monthlyApiCreditsUsd"), (int, float)):
            plan["allowance"] = {"kind": "apiPool" if plan.get("models") else "publishedValue",
                                 "monthlyUsd": quotas["monthlyApiCreditsUsd"]}
        elif isinstance(quotas.get("includedAgentUsageUsd"), (int, float)):
            plan["allowance"] = {"kind": "publishedValue", "monthlyUsd": quotas["includedAgentUsageUsd"], **quotas}
        elif isinstance(quotas.get("monthlyCreditsUsd"), (int, float)):
            plan["allowance"] = {"kind": "publishedValue", "monthlyUsd": quotas["monthlyCreditsUsd"], **quotas}
        elif isinstance(quotas.get("monthlyRawTokens"), (int, float)):
            plan["allowance"] = {"kind": "rawTokens", "monthlyTokens": quotas["monthlyRawTokens"]}
        elif isinstance(quotas.get("thirtyDayRawTokensB"), (int, float)):
            plan["allowance"] = {"kind": "rawTokens", "monthlyTokens": quotas["thirtyDayRawTokensB"] * 1_000_000_000,
                                 "separateInputOutputBuckets": True}
        elif isinstance(quotas.get("averageMonthlyInputTokens"), (int, float)):
            plan["allowance"] = {"kind": "rawTokens", "monthlyTokens": quotas["averageMonthlyInputTokens"],
                                 "inputOnly": True}
        elif isinstance(quotas.get("weeklyInputTokens"), (int, float)):
            plan["allowance"] = {"kind": "rawTokens", "monthlyTokens": quotas["weeklyInputTokens"] * WEEKS_PER_MONTH,
                                 "inputOnly": True}
        elif isinstance(quotas.get("dailyInputTokens"), (int, float)) and isinstance(quotas.get("dailyOutputTokens"), (int, float)):
            plan["allowance"] = {"kind": "rawTokens",
                                 "monthlyTokens": (quotas["dailyInputTokens"] + quotas["dailyOutputTokens"]) * 30,
                                 "separateInputOutputBuckets": True,
                                 "dailyInputTokens": quotas["dailyInputTokens"], "dailyOutputTokens": quotas["dailyOutputTokens"]}
        elif isinstance(quotas.get("monthlyPlanTokens"), (int, float)):
            plan["allowance"] = {"kind": "weightedPlanTokens", "monthlyPlanTokens": quotas["monthlyPlanTokens"]}
        elif isinstance(quotas.get("monthlyRequests"), (int, float)):
            if plan.get("models"):
                plan["allowance"] = {"kind": "requests", "monthlyQuota": quotas["monthlyRequests"],
                                     "quotaPerRequest": {model_id: 1 for model_id in plan["models"]}, **quotas}
            else:
                plan["allowance"] = {"kind": "requestWindow", **quotas}
        elif isinstance(quotas.get("dailyTasks"), (int, float)):
            plan["allowance"] = {"kind": "managedTasks", **quotas}
        elif isinstance(quotas.get("monthlyBuilderTokens"), (int, float)):
            plan["allowance"] = {"kind": "managedTokens", **quotas}
        elif isinstance(quotas.get("monthlyPurchasedCredits"), (int, float)) or isinstance(quotas.get("monthlyCredits"), (int, float)) or isinstance(quotas.get("monthlyAiCredits"), (int, float)) or isinstance(quotas.get("monthlyAgentCredits"), (int, float)):
            plan["allowance"] = {"kind": "workUnits", **quotas}
        elif isinstance(quotas.get("universalCreditsUsd"), (int, float)):
            plan["allowance"] = {"kind": "segmentedPools", **quotas}
        elif isinstance(quotas.get("weeklyPoints"), (int, float)) or isinstance(quotas.get("monthlyCredits"), (int, float)):
            plan["allowance"] = {"kind": "workUnits", **quotas}
        elif any(key in quotas for key in ("fiveHourRequests", "fiveHourPrompts", "fourHourRequests", "estimatedFiveHourBackendRequests")):
            plan["allowance"] = {"kind": "requestWindow", **quotas}
        elif quotas.get("activeHoursPerDay") or ("unlimited" in allowance_type and quotas.get("tokenCeiling") is None):
            plan["allowance"] = {"kind": "unlimited", **quotas}

        if plan["id"] == "catalog-entrim-openclaw-deepseek-v4-flash" and "deepseek-v4-flash" in models:
            plan["models"] = ["deepseek-v4-flash"]
        elif plan["id"] == "catalog-entrim-openclaw-gemma-31b" and "gemma-4-31b" in models:
            plan["models"] = ["gemma-4-31b"]
            plan.setdefault("routeNotes", {})["gemma-4-31b"] = "Secondary plan label says Gemma 31B; generation match should be reverified before treating the intelligence score as exact."
        elif plan["id"] == "catalog-cheapest-inference-core":
            plan["models"] = [model_id for model_id in ("deepseek-v4-flash", "mimo-v2.5") if model_id in models]
        elif plan["id"] == "catalog-cheapest-inference-flagship" and "kimi-k3" in models:
            plan["models"] = ["kimi-k3"]

        plan["note"] = plan.get("note") or broad_row.get("headline")
        _classify(plan)
