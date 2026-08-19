"""Add cross-plan audit metadata after the buyer guide has been finalized."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"
PUBLIC = ROOT / "public/data"


def main() -> None:
    path = DATA / "buyer-guide.json"
    data: dict[str, Any] = json.loads(path.read_text())
    routes = data["rows"] + data["requestRows"]
    route_counts = Counter(row["modelId"] for row in routes)
    model_by_id = {model["id"]: model for model in data["models"]}

    for model in data["models"]:
        model["subscriptionRouteCount"] = route_counts.get(model["id"], 0)

    plan_by_id = {plan["id"]: plan for plan in data["plans"]}
    summary_by_id = {summary["id"]: summary for summary in data["planSummaries"]}
    for plan_id, plan in plan_by_id.items():
        model_rows = [model_by_id[model_id] for model_id in plan.get("models", []) if model_id in model_by_id]
        model_rows.sort(key=lambda model: (-(model.get("intelligence") or -1), model["name"]))
        summary = summary_by_id[plan_id]
        summary["advertisedModelIds"] = [model["id"] for model in model_rows]
        summary["advertisedModels"] = [model["name"] for model in model_rows]
        summary["bestAdvertisedModel"] = model_rows[0]["name"] if model_rows else None
        summary["bestAdvertisedIntelligence"] = model_rows[0].get("intelligence") if model_rows else None
        summary["bestAdvertisedAgenticApiUsdPerM"] = model_rows[0].get("agenticApiUsdPerM") if model_rows else None
        summary["tokenComparisonAvailable"] = summary["tokenRouteCount"] > 0
        summary["requestComparisonAvailable"] = summary["requestRouteCount"] > 0
        summary["fullyNumericallyComparable"] = summary["tokenComparisonAvailable"] and not summary.get("missingFields")

    unquantified_by_id = {plan["id"]: plan for plan in data["unquantifiedPlans"]}
    for plan_id, record in unquantified_by_id.items():
        summary = summary_by_id.get(plan_id)
        if summary:
            record["advertisedModelIds"] = summary["advertisedModelIds"]
            record["advertisedModels"] = summary["advertisedModels"]
            record["bestAdvertisedModel"] = summary["bestAdvertisedModel"]
            record["bestAdvertisedIntelligence"] = summary["bestAdvertisedIntelligence"]

    missing_counts = Counter(field for plan in data["plans"] for field in plan.get("missingFields", []))
    source_counts = Counter(plan.get("sourceType", "unknown") for plan in data["plans"])
    confidence_counts = Counter(plan.get("confidence", "unknown") for plan in data["plans"])
    data["researchCoverage"] = {
        "comparisonClassCounts": data["summary"].get("comparisonClassCounts", {}),
        "researchStatusCounts": data["summary"].get("researchStatusCounts", {}),
        "sourceTypeCounts": dict(sorted(source_counts.items())),
        "confidenceCounts": dict(sorted(confidence_counts.items())),
        "mostCommonMissingFields": [
            {"field": field, "planCount": count}
            for field, count in missing_counts.most_common(25)
        ],
        "plansWithTokenComparison": sum(summary["tokenComparisonAvailable"] for summary in data["planSummaries"]),
        "plansWithRequestComparison": sum(summary["requestComparisonAvailable"] for summary in data["planSummaries"]),
        "plansWithAdvertisedModelEvidence": sum(bool(summary["advertisedModelIds"]) for summary in data["planSummaries"]),
    }

    data["planSummaries"].sort(key=lambda row: (row["provider"].lower(), row["priceUsd"], row["plan"].lower()))
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    for destination in (DATA / "buyer-guide.json", PUBLIC / "buyer-guide.json"):
        destination.write_text(text)
    print(json.dumps(data["researchCoverage"], indent=2))


if __name__ == "__main__":
    main()
