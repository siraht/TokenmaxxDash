#!/usr/bin/env python3
"""Validate recently verified service-specific quotas and unit semantics."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "src/data/buyer-guide.json").read_text())
plans = {plan["id"]: plan for plan in data["plans"]}
rows = data["rows"]
request_rows = data["requestRows"]
errors: list[str] = []


def require(plan_id: str):
    plan = plans.get(plan_id)
    if not plan:
        errors.append(f"missing plan: {plan_id}")
    return plan


for plan_id, price, kwh, overage in (
    ("neuralwatt-basic", 20, 2.35, 8.50),
    ("neuralwatt-standard", 50, 6.25, 8.00),
    ("neuralwatt-pro", 100, 13.33, 7.50),
):
    plan = require(plan_id)
    if not plan:
        continue
    allowance = plan["allowance"]
    if plan["comparisonClass"] != "request":
        errors.append(f"{plan_id}: Neuralwatt must remain request-comparable, not raw-token comparable")
    if allowance.get("monthlyKwh") != kwh or allowance.get("overageUsdPerKwh") != overage:
        errors.append(f"{plan_id}: Neuralwatt energy allocation mismatch")
    if plan["priceUsd"] != price:
        errors.append(f"{plan_id}: Neuralwatt price mismatch")
    if not any(row["planId"] == plan_id for row in request_rows):
        errors.append(f"{plan_id}: no model-specific typical-request rows generated")
    if any(row["planId"] == plan_id for row in rows):
        errors.append(f"{plan_id}: energy plan incorrectly generated raw-token routes")

for plan_id, price, tokens_b in (
    ("minimax-plus", 20, 1.7),
    ("minimax-max", 50, 5.1),
    ("minimax-ultra", 120, 12.5),
):
    plan = require(plan_id)
    if not plan:
        continue
    if plan["priceUsd"] != price or plan["allowance"].get("publishedMonthlyTokensB") != tokens_b:
        errors.append(f"{plan_id}: MiniMax published token estimate mismatch")
    if not any(row["planId"] == plan_id and row["modelId"] == "minimax-m3" for row in rows):
        errors.append(f"{plan_id}: MiniMax M3 token route missing")
starter = require("minimax-starter")
if starter:
    if starter["allowance"].get("fiveHourRequests") != 1_500 or starter["allowance"].get("weeklyRequests") != 15_000:
        errors.append("minimax-starter: request windows mismatch")
    if not any(row["planId"] == "minimax-starter" for row in request_rows):
        errors.append("minimax-starter: request row missing")

amazon = require("amazon-q-pro")
if amazon:
    allowance = amazon["allowance"]
    if allowance.get("monthlyInferenceCalls") != 10_000 or allowance.get("approxMonthlyUserInputs") != 1_000:
        errors.append("amazon-q-pro: official inference-call quota mismatch")
    if amazon["comparisonClass"] != "managed":
        errors.append("amazon-q-pro: inference calls must remain managed units without an exact model/token route")

ollama_pro = require("ollama-cloud-pro")
ollama_max = require("ollama-cloud-max")
ollama_team = require("ollama-cloud-team")
if ollama_pro and (ollama_pro["allowance"].get("relativeToFree") != 50 or ollama_pro["allowance"].get("concurrentCloudModels") != 3):
    errors.append("ollama-cloud-pro: official relative usage or concurrency mismatch")
if ollama_max and (ollama_max["allowance"].get("relativeToPro") != 5 or ollama_max["allowance"].get("concurrentCloudModels") != 10 or not ollama_max["allowance"].get("newSignupsPaused")):
    errors.append("ollama-cloud-max: official relative usage, concurrency, or paused status mismatch")
if ollama_team and ollama_team["allowance"].get("minimumSeats") != 5:
    errors.append("ollama-cloud-team: five-seat minimum missing")

team = require("devin-teams-full-seat")
if team and (team["priceUsd"] != 40 or team["allowance"].get("accountMinimumUsd") != 80):
    errors.append("devin-teams-full-seat: price or account minimum mismatch")

if errors:
    raise SystemExit("\n".join(errors))
print("Validated Neuralwatt energy/request capacity, current MiniMax token and request tiers, Amazon Q inference calls, Ollama relative plans, and Devin Teams semantics.")
