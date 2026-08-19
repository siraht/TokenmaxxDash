"""Finalize the universal monthly-subscription buyer guide.

The base builder performs provider-specific token arithmetic. This pass enforces
route access constraints, rebuilds Pareto sets without hiding the owner's plans,
and creates an all-plan audit surface for request, managed, relative, and
provider-hidden products.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src" / "data"
PUBLIC = ROOT / "public" / "data"


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def _recalculate(row: dict[str, Any], mix_id: str) -> None:
    metrics = row[mix_id]
    tokens_m = metrics.get("monthlyTokensM")
    price = row["priceUsd"]
    score = row.get("intelligence")
    for key in ("subscriptionUsdPerM", "qualityAdjustedUsdPerM", "qualityTokensMPerDollar",
                "monthlyTaskAttempts", "monthlySuccessfulTasks", "subscriptionUsdPerSuccessfulTask"):
        metrics.pop(key, None)
    if _finite(tokens_m) and tokens_m > 0:
        metrics["subscriptionUsdPerM"] = price / tokens_m
        if _finite(score) and score > 0:
            normalized = score / 100
            metrics["qualityAdjustedUsdPerM"] = metrics["subscriptionUsdPerM"] / normalized
            metrics["qualityTokensMPerDollar"] = tokens_m * normalized / price
        task_tokens = metrics.get("taskTokensM")
        pass_rate = metrics.get("taskPassRate")
        if _finite(task_tokens) and task_tokens > 0 and _finite(pass_rate) and pass_rate > 0:
            attempts = tokens_m / task_tokens
            successes = attempts * pass_rate
            metrics["monthlyTaskAttempts"] = attempts
            metrics["monthlySuccessfulTasks"] = successes
            metrics["subscriptionUsdPerSuccessfulTask"] = price / successes if successes else None


def _pareto(rows: list[dict[str, Any]], mix_id: str, *, min_quality: float = 0,
            metric: str = "qualityAdjustedUsdPerM", exclude_owned: bool = False) -> list[str]:
    candidates = [row for row in rows if (row.get("intelligence") or 0) >= min_quality
                  and _finite(row[mix_id].get(metric)) and (not exclude_owned or not row.get("owned"))]
    keep: list[str] = []
    for row in candidates:
        dominated = False
        for other in candidates:
            if other is row:
                continue
            weak = (other["priceUsd"] <= row["priceUsd"]
                    and (other.get("intelligence") or 0) >= (row.get("intelligence") or 0)
                    and other[mix_id][metric] <= row[mix_id][metric])
            strict = (other["priceUsd"] < row["priceUsd"]
                      or (other.get("intelligence") or 0) > (row.get("intelligence") or 0)
                      or other[mix_id][metric] < row[mix_id][metric])
            if weak and strict:
                dominated = True
                break
        if not dominated:
            keep.append(row["id"])
    return keep


def _best(rows: list[dict[str, Any]], mix_id: str, key: str) -> dict[str, Any] | None:
    valid = [row for row in rows if _finite(row[mix_id].get(key))]
    return min(valid, key=lambda row: row[mix_id][key]) if valid else None


def _plan_summary(plan: dict[str, Any], routes: list[dict[str, Any]], request_routes: list[dict[str, Any]]) -> dict[str, Any]:
    best_standard = _best(routes, "standard", "qualityAdjustedUsdPerM")
    best_agentic = _best(routes, "agentic", "qualityAdjustedUsdPerM")
    best_task = _best(routes, "agentic", "subscriptionUsdPerSuccessfulTask")
    return {
        "id": plan["id"], "provider": plan["provider"], "plan": plan["plan"], "priceUsd": plan["priceUsd"],
        "owned": plan.get("owned", False), "confidence": plan.get("confidence"),
        "comparisonClass": plan.get("comparisonClass"), "researchStatus": plan.get("researchStatus"),
        "missingFields": plan.get("missingFields", []), "allowanceKind": plan.get("allowance", {}).get("kind"),
        "allowance": plan.get("allowance", {}), "windows": plan.get("windows"), "policy": plan.get("policy"),
        "note": plan.get("note"), "source": plan.get("source"), "modelCount": len(plan.get("models", [])),
        "tokenRouteCount": len(routes), "requestRouteCount": len(request_routes),
        "bestStandardRouteId": best_standard["id"] if best_standard else None,
        "bestAgenticRouteId": best_agentic["id"] if best_agentic else None,
        "bestTaskRouteId": best_task["id"] if best_task else None,
        "bestStandardQualityCost": best_standard["standard"].get("qualityAdjustedUsdPerM") if best_standard else None,
        "bestAgenticQualityCost": best_agentic["agentic"].get("qualityAdjustedUsdPerM") if best_agentic else None,
        "bestTaskCost": best_task["agentic"].get("subscriptionUsdPerSuccessfulTask") if best_task else None,
        "bestStandardModel": best_standard.get("model") if best_standard else None,
        "bestAgenticModel": best_agentic.get("model") if best_agentic else None,
        "bestTaskModel": best_task.get("model") if best_task else None,
    }


def main() -> None:
    path = DATA / "buyer-guide.json"
    data = json.loads(path.read_text())
    plan_by_id = {plan["id"]: plan for plan in data["plans"]}

    rows: list[dict[str, Any]] = []
    for row in data["rows"]:
        plan = plan_by_id[row["planId"]]
        row["comparisonClass"] = plan.get("comparisonClass", "token")
        row["researchStatus"] = plan.get("researchStatus")
        row["missingFields"] = plan.get("missingFields", [])
        row["accessMode"] = plan.get("accessByModel", {}).get(row["modelId"], "included")
        fraction = plan.get("modelAllowanceFraction", {}).get(row["modelId"], 1.0)
        row["allowanceFraction"] = fraction
        if fraction <= 0:
            continue
        if fraction != 1:
            for mix_id in data["mixes"]:
                metrics = row[mix_id]
                for key in ("monthlyTokensMLow", "monthlyTokensM", "monthlyTokensMHigh",
                            "allowanceUsdLow", "allowanceUsd", "allowanceUsdHigh", "modelMonthlyUsageUsd"):
                    if _finite(metrics.get(key)):
                        metrics[key] *= fraction
                _recalculate(row, mix_id)
        rows.append(row)
    data["rows"] = rows

    for row in data["requestRows"]:
        plan = plan_by_id[row["planId"]]
        row["comparisonClass"] = plan.get("comparisonClass", "request")
        row["researchStatus"] = plan.get("researchStatus")
        row["missingFields"] = plan.get("missingFields", [])

    floors = (0, 40, 50, 55)
    data["frontiers"] = {
        mix_id: {f"quality{floor}" if floor else "all": _pareto(rows, mix_id, min_quality=floor) for floor in floors}
        for mix_id in data["mixes"]
    }
    data["alternativeFrontiers"] = {
        mix_id: {f"quality{floor}" if floor else "all": _pareto(rows, mix_id, min_quality=floor, exclude_owned=True) for floor in floors}
        for mix_id in data["mixes"]
    }

    bands = [
        {"id": "under10", "label": "Best under $10", "maxPrice": 10, "minQuality": 40},
        {"id": "under25", "label": "Best under $25", "maxPrice": 25, "minQuality": 50},
        {"id": "under50", "label": "Best under $50", "maxPrice": 50, "minQuality": 50},
        {"id": "under100", "label": "Best under $100", "maxPrice": 100, "minQuality": 55},
        {"id": "under200", "label": "Best under $200", "maxPrice": 200, "minQuality": 55},
    ]

    def recommendations(mix_id: str, exclude_owned: bool) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for band in bands:
            candidates = [row for row in rows if row["priceUsd"] <= band["maxPrice"]
                          and (row.get("intelligence") or 0) >= band["minQuality"]
                          and _finite(row[mix_id].get("qualityAdjustedUsdPerM"))
                          and (not exclude_owned or not row.get("owned"))]
            candidates.sort(key=lambda row: (row[mix_id]["qualityAdjustedUsdPerM"],
                                              -(row.get("codingScore") or -1),
                                              -(row.get("intelligence") or -1), row["priceUsd"]))
            result[band["id"]] = [candidates[0]["id"]] if candidates else []
        return result

    data["recommendationBands"] = bands
    data["shortlists"] = {mix_id: recommendations(mix_id, False) for mix_id in data["mixes"]}
    data["alternativeShortlists"] = {mix_id: recommendations(mix_id, True) for mix_id in data["mixes"]}

    routes_by_plan = {plan_id: [] for plan_id in plan_by_id}
    request_by_plan = {plan_id: [] for plan_id in plan_by_id}
    for row in rows:
        routes_by_plan[row["planId"]].append(row)
    for row in data["requestRows"]:
        request_by_plan[row["planId"]].append(row)
    data["planSummaries"] = [_plan_summary(plan, routes_by_plan[plan["id"]], request_by_plan[plan["id"]])
                             for plan in data["plans"]]
    data["planSummaries"].sort(key=lambda row: (row["provider"].lower(), row["priceUsd"], row["plan"].lower()))

    model_name = {model["id"]: model["name"] for model in data["models"]}
    data["unquantifiedPlans"] = [
        {"id": plan["id"], "provider": plan["provider"], "plan": plan["plan"], "priceUsd": plan["priceUsd"],
         "owned": plan.get("owned", False), "models": [model_name[m] for m in plan.get("models", []) if m in model_name],
         "comparisonClass": plan.get("comparisonClass"), "researchStatus": plan.get("researchStatus"),
         "missingFields": plan.get("missingFields", []), "allowanceKind": plan.get("allowance", {}).get("kind"),
         "allowance": plan.get("allowance", {}), "confidence": plan.get("confidence"), "windows": plan.get("windows"),
         "note": plan.get("note"), "source": plan.get("source"), "policy": plan.get("policy")}
        for plan in data["plans"] if not routes_by_plan[plan["id"]] and not request_by_plan[plan["id"]]
    ]

    class_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for plan in data["plans"]:
        cls = plan.get("comparisonClass", "provider-hidden")
        class_counts[cls] = class_counts.get(cls, 0) + 1
        status = plan.get("researchStatus", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    data["summary"].update({
        "comparableRouteCount": len(rows), "requestRouteCount": len(data["requestRows"]),
        "unquantifiedPlanCount": len(data["unquantifiedPlans"]), "comparisonClassCounts": class_counts,
        "researchStatusCounts": status_counts, "defaultHidesOwned": False,
        "baselineProvidersAlwaysVisible": ["OpenAI Codex", "Claude Code", "Grok Build", "Synthetic"],
    })
    data["methodology"]["ownedPlanRule"] = "Owned plans are visible and ranked by default. The UI offers an optional hide-owned filter and separate alternative-only frontiers."
    data["methodology"]["missingDataRule"] = "Every plan records its exact missing denominator. Provider-hidden, managed-work, relative, and fair-use plans stay visible but cannot enter token rankings without a defensible token conversion."

    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    for destination in (DATA / "buyer-guide.json", PUBLIC / "buyer-guide.json"):
        destination.write_text(text)
    print(json.dumps(data["summary"], indent=2))


if __name__ == "__main__":
    main()
