#!/usr/bin/env python3
"""Validate Zencoder model multipliers and Codebuff work-credit economics."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "src/data/buyer-guide.json").read_text())
plans = {plan["id"]: plan for plan in data["plans"]}
models = {model["id"]: model for model in data["models"]}
rows = data["rows"]
request_rows = data["requestRows"]
errors: list[str] = []

required_models = {
    "claude-opus-4.6": 38.0,
    "claude-opus-4.7": 54.0,
    "claude-sonnet-4.6": 47.0,
    "gpt-5.3-codex": 46.0,
    "gpt-5.4": 53.0,
    "gpt-5.4-mini": 41.0,
    "gpt-5.5": 55.0,
    "gemini-3.1-pro": 46.0,
    "gemini-3-flash": 38.0,
    "grok-code-fast-1": 22.0,
}
for model_id, score in required_models.items():
    model = models.get(model_id)
    if not model:
        errors.append(f"missing extended model: {model_id}")
    elif model.get("intelligence") != score:
        errors.append(f"{model_id}: intelligence {model.get('intelligence')} != {score}")

zencoder_tiers = {
    "zencoder-pro": (45, 30_000),
    "zencoder-pro-plus": (95, 80_000),
    "zencoder-pro-max": (195, 180_000),
}
for plan_id, (price, credits) in zencoder_tiers.items():
    plan = plans.get(plan_id)
    if not plan:
        errors.append(f"missing Zencoder tier: {plan_id}")
        continue
    if plan.get("priceUsd") != price or plan.get("allowance", {}).get("monthlyCredits") != credits:
        errors.append(f"{plan_id}: price or monthly credits mismatch")
    if plan.get("comparisonClass") != "request":
        errors.append(f"{plan_id}: Zencoder must remain request-comparable")
    generated = [row for row in request_rows if row["planId"] == plan_id]
    if not generated:
        errors.append(f"{plan_id}: no model-specific request rows generated")
    if any(row["planId"] == plan_id for row in rows):
        errors.append(f"{plan_id}: Zencoder credits incorrectly generated raw-token routes")

pro = plans.get("zencoder-pro")
if pro:
    for restricted in ("claude-opus-4.6", "claude-opus-4.7", "gpt-5.5"):
        if restricted in pro.get("models", []):
            errors.append(f"zencoder-pro: restricted model leaked into Pro: {restricted}")
for plan_id in ("zencoder-pro-plus", "zencoder-pro-max"):
    plan = plans.get(plan_id)
    if plan:
        for required in ("claude-opus-4.7", "gpt-5.5", "grok-code-fast-1"):
            if required not in plan.get("models", []):
                errors.append(f"{plan_id}: expected model missing: {required}")

codebuff_tiers = {
    "codebuff-1x": (100, 16_800, 168.0),
    "codebuff-2-5x": (200, 42_000, 420.0),
    "codebuff-7x": (500, 117_500, 1_175.0),
}
for plan_id, (price, credits, equivalent) in codebuff_tiers.items():
    plan = plans.get(plan_id)
    if not plan:
        errors.append(f"missing Codebuff tier: {plan_id}")
        continue
    allowance = plan.get("allowance", {})
    if plan.get("priceUsd") != price or allowance.get("monthlyCredits") != credits:
        errors.append(f"{plan_id}: price or work-credit count mismatch")
    if allowance.get("paygEquivalentUsd") != equivalent or allowance.get("paygUsdPerCredit") != 0.01:
        errors.append(f"{plan_id}: PAYG-equivalent calculation mismatch")
    if plan.get("comparisonClass") != "managed":
        errors.append(f"{plan_id}: Codebuff must remain a managed work-credit plan")
    if any(row["planId"] == plan_id for row in rows + request_rows):
        errors.append(f"{plan_id}: Codebuff work credits incorrectly entered model token/request rankings")

if errors:
    raise SystemExit("\n".join(errors))
print("Validated ten extended model records, all Zencoder plan/model request routes, and Codebuff work-credit tiers without fake raw-token conversions.")
