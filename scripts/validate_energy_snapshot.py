#!/usr/bin/env python3
"""Validate the dated Neuralwatt energy snapshot and Qwen3.6 35B route."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "src/data/buyer-guide.json").read_text())
plans = {plan["id"]: plan for plan in data["plans"]}
models = {model["id"]: model for model in data["models"]}
request_rows = data["requestRows"]
errors: list[str] = []
expected_energy = {
    "deepseek-v4-flash": 0.21882,
    "glm-5.2": 1.94,
    "gemma-4-31b": 0.04243,
    "kimi-k2.7-code": 0.66173,
    "kimi-k3": 6.78,
    "qwen3.6-35b": 0.03582,
}

qwen = models.get("qwen3.6-35b")
if not qwen:
    errors.append("Qwen3.6 35B model record is missing")
else:
    if qwen.get("intelligence") != 31.6:
        errors.append("Qwen3.6 35B intelligence snapshot mismatch")
    if (qwen.get("input"), qwen.get("cache"), qwen.get("output")) != (0.248, 0.059, 1.485):
        errors.append("Qwen3.6 35B canonical API-rate snapshot mismatch")

for plan_id in ("neuralwatt-basic", "neuralwatt-standard", "neuralwatt-pro"):
    plan = plans.get(plan_id)
    if not plan:
        errors.append(f"missing Neuralwatt plan: {plan_id}")
        continue
    allowance = plan.get("allowance", {})
    if allowance.get("energySnapshotDate") != "2026-08-19":
        errors.append(f"{plan_id}: energy snapshot date mismatch")
    if allowance.get("typicalEnergyWhPerRequest") != expected_energy:
        errors.append(f"{plan_id}: trailing-seven-day energy snapshot mismatch")
    generated = {row["modelId"] for row in request_rows if row["planId"] == plan_id}
    if generated != set(expected_energy):
        errors.append(f"{plan_id}: generated energy routes {sorted(generated)} != {sorted(expected_energy)}")

if errors:
    raise SystemExit("\n".join(errors))
print("Validated the 2026-08-19 Neuralwatt trailing-seven-day energy snapshot and exact Qwen3.6 35B model route.")
