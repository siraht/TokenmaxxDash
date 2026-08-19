"""Make range-based rankings conservative without discarding their central estimates."""
from __future__ import annotations

import math
from typing import Any


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def _reprice(row: dict[str, Any], mix_id: str) -> None:
    metrics = row[mix_id]
    original_center = metrics.get("monthlyTokensM")
    low = metrics.get("monthlyTokensMLow")
    minimum = metrics.get("monthlyTokensMMinimum")
    high = metrics.get("monthlyTokensMHigh")

    if _finite(low) and low > 0:
        conservative = low
        if _finite(original_center):
            metrics["monthlyTokensMCenter"] = original_center
        metrics["capacityEstimateType"] = "conservative-low-of-range"
        metrics["subscriptionCostInterpretation"] = "upper-bound within measured range"
    elif _finite(minimum) and minimum > 0:
        conservative = minimum
        metrics["capacityEstimateType"] = "measured-lower-bound"
        metrics["subscriptionCostInterpretation"] = "upper-bound because true capacity is at least this large"
    elif _finite(original_center) and original_center > 0:
        conservative = original_center
        metrics["capacityEstimateType"] = "point-or-exact"
        metrics["subscriptionCostInterpretation"] = "point estimate"
    else:
        return

    metrics["monthlyTokensMForRanking"] = conservative
    metrics["monthlyTokensM"] = conservative
    if _finite(high):
        metrics["monthlyTokensMHigh"] = high

    price = row["priceUsd"]
    metrics["subscriptionUsdPerM"] = price / conservative
    intelligence = row.get("intelligence")
    if _finite(intelligence) and intelligence > 0:
        normalized = intelligence / 100
        metrics["qualityAdjustedUsdPerM"] = metrics["subscriptionUsdPerM"] / normalized
        metrics["qualityTokensMPerDollar"] = conservative * normalized / price

    task_tokens = metrics.get("taskTokensM")
    pass_rate = metrics.get("taskPassRate")
    if _finite(task_tokens) and task_tokens > 0 and _finite(pass_rate) and pass_rate > 0:
        attempts = conservative / task_tokens
        successes = attempts * pass_rate
        metrics["monthlyTaskAttempts"] = attempts
        metrics["monthlySuccessfulTasks"] = successes
        metrics["subscriptionUsdPerSuccessfulTask"] = price / successes if successes else None


def _pareto(rows: list[dict[str, Any]], mix_id: str, minimum_quality: float, exclude_owned: bool) -> list[str]:
    candidates = [
        row for row in rows
        if (row.get("intelligence") or 0) >= minimum_quality
        and _finite(row[mix_id].get("qualityAdjustedUsdPerM"))
        and (not exclude_owned or not row.get("owned"))
    ]
    frontier: list[str] = []
    for row in candidates:
        dominated = False
        for other in candidates:
            if other is row:
                continue
            weak = (
                other["priceUsd"] <= row["priceUsd"]
                and (other.get("intelligence") or 0) >= (row.get("intelligence") or 0)
                and other[mix_id]["qualityAdjustedUsdPerM"] <= row[mix_id]["qualityAdjustedUsdPerM"]
            )
            strict = (
                other["priceUsd"] < row["priceUsd"]
                or (other.get("intelligence") or 0) > (row.get("intelligence") or 0)
                or other[mix_id]["qualityAdjustedUsdPerM"] < row[mix_id]["qualityAdjustedUsdPerM"]
            )
            if weak and strict:
                dominated = True
                break
        if not dominated:
            frontier.append(row["id"])
    return frontier


def _best(rows: list[dict[str, Any]], mix_id: str, key: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if _finite(row[mix_id].get(key))]
    return min(candidates, key=lambda row: row[mix_id][key]) if candidates else None


def apply_conservative_metrics(data: dict[str, Any]) -> None:
    rows = data["rows"]
    for row in rows:
        for mix_id in data["mixes"]:
            _reprice(row, mix_id)

    floors = (0, 40, 50, 55)
    data["frontiers"] = {
        mix_id: {
            "all" if floor == 0 else f"quality{floor}": _pareto(rows, mix_id, floor, False)
            for floor in floors
        }
        for mix_id in data["mixes"]
    }
    data["alternativeFrontiers"] = {
        mix_id: {
            "all" if floor == 0 else f"quality{floor}": _pareto(rows, mix_id, floor, True)
            for floor in floors
        }
        for mix_id in data["mixes"]
    }

    bands = data.get("recommendationBands", [])
    def shortlists(mix_id: str, exclude_owned: bool) -> dict[str, list[str]]:
        output: dict[str, list[str]] = {}
        for band in bands:
            candidates = [
                row for row in rows
                if row["priceUsd"] <= band["maxPrice"]
                and (row.get("intelligence") or 0) >= band["minQuality"]
                and _finite(row[mix_id].get("qualityAdjustedUsdPerM"))
                and (not exclude_owned or not row.get("owned"))
            ]
            candidates.sort(key=lambda row: (
                row[mix_id]["qualityAdjustedUsdPerM"],
                -(row.get("codingScore") or -1),
                -(row.get("intelligence") or -1),
                row["priceUsd"],
            ))
            output[band["id"]] = [candidates[0]["id"]] if candidates else []
        return output

    data["shortlists"] = {mix_id: shortlists(mix_id, False) for mix_id in data["mixes"]}
    data["alternativeShortlists"] = {mix_id: shortlists(mix_id, True) for mix_id in data["mixes"]}

    routes_by_plan: dict[str, list[dict[str, Any]]] = {plan["id"]: [] for plan in data["plans"]}
    for row in rows:
        routes_by_plan[row["planId"]].append(row)
    summary_by_id = {summary["id"]: summary for summary in data.get("planSummaries", [])}
    for plan_id, plan_rows in routes_by_plan.items():
        summary = summary_by_id.get(plan_id)
        if not summary:
            continue
        standard = _best(plan_rows, "standard", "qualityAdjustedUsdPerM")
        agentic = _best(plan_rows, "agentic", "qualityAdjustedUsdPerM")
        task = _best(plan_rows, "agentic", "subscriptionUsdPerSuccessfulTask")
        summary.update({
            "bestStandardRouteId": standard["id"] if standard else None,
            "bestAgenticRouteId": agentic["id"] if agentic else None,
            "bestTaskRouteId": task["id"] if task else None,
            "bestStandardQualityCost": standard["standard"].get("qualityAdjustedUsdPerM") if standard else None,
            "bestAgenticQualityCost": agentic["agentic"].get("qualityAdjustedUsdPerM") if agentic else None,
            "bestTaskCost": task["agentic"].get("subscriptionUsdPerSuccessfulTask") if task else None,
            "bestStandardModel": standard.get("model") if standard else None,
            "bestAgenticModel": agentic.get("model") if agentic else None,
            "bestTaskModel": task.get("model") if task else None,
        })

    data.setdefault("methodology", {})["rangeRankingRule"] = (
        "Measured ranges and lower-bound capacities are ranked using their conservative lower token-capacity bound. "
        "Central and upper estimates remain in the route data and plan detail pages."
    )
