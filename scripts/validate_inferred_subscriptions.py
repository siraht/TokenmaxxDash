#!/usr/bin/env python3
"""Validate deep inferences reconstructed from public quota telemetry."""
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


def plan(plan_id: str):
    value = plans.get(plan_id)
    if not value:
        errors.append(f"missing inferred plan: {plan_id}")
    return value


def routes(plan_id: str, model_id: str | None = None):
    return [row for row in rows if row["planId"] == plan_id and (model_id is None or row["modelId"] == model_id)]


# Cursor: exact Other Models pools must not be assigned to first-party routes.
for plan_id, pool in (("cursor-pro", 20), ("cursor-proplus", 70), ("cursor-ultra", 400)):
    value = plan(plan_id)
    if not value:
        continue
    if value["allowance"].get("guaranteedOtherModelsUsd") != pool:
        errors.append(f"{plan_id}: guaranteed Other Models pool mismatch")
    for first_party in ("grok-4.5", "composer-2.5"):
        if first_party in value.get("models", []) and routes(plan_id, first_party):
            errors.append(f"{plan_id}: first-party Cursor model leaked into Other Models pool: {first_party}")
    if not routes(plan_id):
        errors.append(f"{plan_id}: no third-party token routes remain")

# Claude current range must remain separate from the historical high-value regime.
expected_claude = {
    "claude-pro": (135.87890625, 217.40625, 364.15546875),
    "claude-max-5x": (679.39453125, 1087.03125, 1820.77734375),
    "claude-max-20x": (2717.578125, 4348.125, 7283.109375),
}
for plan_id, expected in expected_claude.items():
    value = plan(plan_id)
    if not value:
        continue
    allowance = value["allowance"]
    actual = (allowance.get("monthlyUsdLow"), allowance.get("monthlyUsd"), allowance.get("monthlyUsdHigh"))
    if any(abs((a or 0) - e) > 1e-6 for a, e in zip(actual, expected)):
        errors.append(f"{plan_id}: current API-equivalent range mismatch: {actual}")
    if not allowance.get("historicalRegimeExcludedFromCurrentRanking"):
        errors.append(f"{plan_id}: historical Claude regime is not explicitly excluded")

# Kimi direct Allegretto measurement and official scaling.
expected_kimi = {
    "kimi-moderato": (274_000_000, 287_000_000, 300_000_000),
    "kimi-allegretto": (1_370_000_000, 1_435_000_000, 1_500_000_000),
    "kimi-allegro": (4_110_000_000, 4_305_000_000, 4_500_000_000),
    "kimi-vivace": (8_220_000_000, 8_610_000_000, 9_000_000_000),
}
for plan_id, expected in expected_kimi.items():
    value = plan(plan_id)
    if not value:
        continue
    allowance = value["allowance"]
    actual = (allowance.get("monthlyTokensLow"), allowance.get("monthlyTokens"), allowance.get("monthlyTokensHigh"))
    if actual != expected:
        errors.append(f"{plan_id}: Kimi range mismatch: {actual}")
    if not routes(plan_id, "kimi-k3-256k"):
        errors.append(f"{plan_id}: K3 256K route missing")
    if plan_id == "kimi-moderato" and routes(plan_id, "kimi-k3"):
        errors.append("kimi-moderato: full 1M K3 route must be unavailable")
    if plan_id != "kimi-moderato":
        k3 = routes(plan_id, "kimi-k3")
        if not k3 or any(abs(row.get("allowanceFraction", 0) - .5) > 1e-9 for row in k3):
            errors.append(f"{plan_id}: K3 1M two-times quota weighting missing")

# Factory standard-token pools and official model multipliers.
for plan_id, standard_tokens in (("factory-pro", 20_000_000), ("factory-plus", 100_000_000), ("factory-max", 200_000_000)):
    value = plan(plan_id)
    if not value:
        continue
    allowance = value["allowance"]
    if allowance.get("kind") != "standardTokens" or allowance.get("monthlyStandardTokens") != standard_tokens:
        errors.append(f"{plan_id}: Standard-token pool mismatch")
    for model_id, multiplier in (("gpt-5.6-luna", .08), ("gpt-5.6-sol", 2.0), ("claude-fable-5", 4.0)):
        if model_id in models:
            if allowance.get("modelMultipliers", {}).get(model_id) != multiplier:
                errors.append(f"{plan_id}: Factory multiplier mismatch for {model_id}")
            if not routes(plan_id, model_id):
                errors.append(f"{plan_id}: Factory token route missing for {model_id}")

# Google current post-boost mixed route, BytePlus request ceilings, and Cline range.
for plan_id in ("catalog-google-ai-plus", "catalog-google-ai-pro", "catalog-google-ai-ultra-5x", "catalog-google-ai-ultra-20x"):
    value = plan(plan_id)
    if value:
        if value["allowance"].get("kind") != "rawTokensEstimateRange":
            errors.append(f"{plan_id}: Antigravity measured range missing")
        if not routes(plan_id, "antigravity-mixed-coding-route"):
            errors.append(f"{plan_id}: Antigravity mixed route missing")

for plan_id, expected in (("catalog-byteplus-modelark-lite", (1200, 9000, 18000)),
                          ("catalog-byteplus-modelark-pro", (6000, 45000, 90000))):
    value = plan(plan_id)
    if not value:
        continue
    allowance = value["allowance"]
    actual = (allowance.get("fiveHourRequests"), allowance.get("weeklyRequests"), allowance.get("monthlyRequests"))
    if actual != expected:
        errors.append(f"{plan_id}: BytePlus request ceilings mismatch")
    if not any(row["planId"] == plan_id for row in request_rows):
        errors.append(f"{plan_id}: BytePlus request rows missing")

cline = plan("clinepass")
if cline:
    allowance = cline["allowance"]
    if allowance.get("advertisedApiValueMultipleRange") != [2.0, 5.0]:
        errors.append("clinepass: advertised value range missing")
    if not allowance.get("calibrationFormula") or not routes("clinepass"):
        errors.append("clinepass: calibratable token routes missing")

# Grok must remain tier-unassigned but reproducibly calibratable.
for plan_id in ("grok-build-basic", "grok-build-supergrok", "grok-build-pro", "grok-build-heavy"):
    value = plan(plan_id)
    if not value:
        continue
    sample = value["allowance"].get("publicUnmappedAccountSample", {})
    if value.get("comparisonClass") != "calibratable" or not value["allowance"].get("calibrationFormula"):
        errors.append(f"{plan_id}: Grok calibration metadata missing")
    if sample.get("monthlyLimitUsd") != 180.0 or not sample.get("planTierNotPublished"):
        errors.append(f"{plan_id}: unlabeled Grok sample must remain explicitly unmapped")
    if routes(plan_id):
        errors.append(f"{plan_id}: unlabeled Grok sample leaked into plan-specific token ranking")

# Devin and Tabnine retain useful native units instead of fake model tokens.
for plan_id in ("devin-pro", "devin-max"):
    value = plan(plan_id)
    if value and (value["allowance"].get("kind") != "requestRange" or value.get("comparisonClass") != "managed"):
        errors.append(f"{plan_id}: Devin request-range semantics missing")
for plan_id, tokens, platform_cost in (("tabnine-headless-business", 5_000_000_000, .24),
                                       ("tabnine-headless-enterprise", 50_000_000_000, .10)):
    value = plan(plan_id)
    if not value:
        continue
    allowance = value["allowance"]
    if allowance.get("monthlyProcessingTokens") != tokens or allowance.get("platformUsdPerMillionProcessingTokens") != platform_cost:
        errors.append(f"{plan_id}: processing-token economics mismatch")
    if routes(plan_id) or any(row["planId"] == plan_id for row in request_rows):
        errors.append(f"{plan_id}: Tabnine processing capacity incorrectly entered model rankings")

if errors:
    raise SystemExit("\n".join(errors))
print("Validated Cursor pool separation, current Claude ranges, Kimi scaling, Factory Standard tokens, Ollama/Antigravity measured routes, BytePlus requests, Grok/Cline calibration, Devin ranges, and Tabnine processing capacity.")
