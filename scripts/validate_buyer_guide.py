#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "data" / "buyer-guide.json"
PUB = ROOT / "public" / "data" / "buyer-guide.json"
errors: list[str] = []

if not SRC.exists():
    raise SystemExit("buyer-guide.json is missing; run scripts/build_buyer_guide.py")
if not PUB.exists() or SRC.read_bytes() != PUB.read_bytes():
    errors.append("public/data/buyer-guide.json is missing or differs from src/data")

data = json.loads(SRC.read_text())
models = {model["id"]: model for model in data["models"]}
plans = {plan["id"]: plan for plan in data["plans"]}
rows = data["rows"]
request_rows = data["requestRows"]

if len(models) != data["summary"]["modelCount"]:
    errors.append("model count mismatch")
if len(plans) != data["summary"]["planCount"]:
    errors.append("plan count mismatch")
if len(rows) != data["summary"]["comparableRouteCount"]:
    errors.append("comparable row count mismatch")
if len(request_rows) != data["summary"]["requestRouteCount"]:
    errors.append("request row count mismatch")

seen = set()
for row in rows + request_rows:
    if row["id"] in seen:
        errors.append(f"duplicate row id: {row['id']}")
    seen.add(row["id"])
    if row["planId"] not in plans:
        errors.append(f"{row['id']}: missing plan")
    if row["modelId"] not in models:
        errors.append(f"{row['id']}: missing model")
    if row.get("intelligence") is not None and not 0 <= row["intelligence"] <= 100:
        errors.append(f"{row['id']}: invalid intelligence")
    for mix in data["mixes"]:
        metrics = row[mix]
        for key, value in metrics.items():
            if isinstance(value, float) and not math.isfinite(value):
                errors.append(f"{row['id']} {mix}.{key}: non-finite")
        if row in rows:
            if metrics.get("kind") in {"apiPool", "apiPoolRange"} and not (metrics.get("apiRatePerM") or 0) > 0:
                errors.append(f"{row['id']} {mix}: dollar pool lacks route-billed token rate")
            if metrics.get("rateBasis") not in {"subscription route", "public model API"}:
                errors.append(f"{row['id']} {mix}: invalid route-rate basis")
            if not (metrics.get("monthlyTokensM") or 0) > 0:
                errors.append(f"{row['id']} {mix}: missing token capacity")
            if not (metrics.get("subscriptionUsdPerM") or 0) > 0:
                errors.append(f"{row['id']} {mix}: missing subscription token cost")
            if row.get("intelligence") and not (metrics.get("qualityAdjustedUsdPerM") or 0) > 0:
                errors.append(f"{row['id']} {mix}: missing quality-adjusted token cost")
            if row.get("codingScore") is not None:
                if not 0 < row["codingScore"] <= 100:
                    errors.append(f"{row['id']}: invalid coding score")
                if not (metrics.get("taskTokensM") or 0) > 0 or not (metrics.get("taskPassRate") or 0) > 0:
                    errors.append(f"{row['id']} {mix}: coding score lacks task denominator")
                if not (metrics.get("subscriptionUsdPerSuccessfulTask") or 0) > 0:
                    errors.append(f"{row['id']} {mix}: missing subscription task cost")
        if row in request_rows and row.get("intelligence") and not (metrics.get("qualityAdjustedUsdPer1000Requests") or 0) > 0:
            errors.append(f"{row['id']} {mix}: missing quality-adjusted request cost")

for plan in data["plans"]:
    if plan["owned"] and plan["provider"] not in data["summary"]["ownedProviders"]:
        errors.append(f"owned provider not declared: {plan['provider']}")

definition_ids = {definition["id"] for definition in data.get("shortlistDefinitions", [])}
if definition_ids != set(data["shortlists"].get("standard", {})):
    errors.append("shortlist definitions do not match generated standard cards")
for mix, lists in data["shortlists"].items():
    selected_rows = []
    for name, ids in lists.items():
        if len(ids) > 1:
            errors.append(f"shortlist {mix}.{name}: expected one card")
        for row_id in ids:
            if row_id not in seen:
                errors.append(f"shortlist {mix}.{name}: missing row {row_id}")
            else:
                row = next(row for row in rows if row["id"] == row_id)
                selected_rows.append(row_id)
                if row["owned"]:
                    errors.append(f"shortlist {mix}.{name}: owned row leaked")
    if len(selected_rows) != len(set(selected_rows)):
        errors.append(f"shortlist {mix}: identical route repeated across cards")

workflow_dir = ROOT / ".github" / "workflows"
if workflow_dir.exists() and any(path.suffix in {".yml", ".yaml"} for path in workflow_dir.iterdir()):
    errors.append("active GitHub Actions workflow found")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Validated {len(plans)} plans, {len(models)} models, {len(rows)} token rows, {len(request_rows)} request rows, and {len(data['unquantifiedPlans'])} unquantified plans.")
