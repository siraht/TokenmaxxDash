#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src/data/buyer-guide.json"
PUB = ROOT / "public/data/buyer-guide.json"
errors: list[str] = []

if not SRC.exists():
    raise SystemExit("buyer-guide.json is missing; run scripts/build_buyer_guide.py")
if not PUB.exists() or SRC.read_bytes() != PUB.read_bytes():
    errors.append("public/data/buyer-guide.json is missing or differs from src/data")
data = json.loads(SRC.read_text())
plans = {plan["id"]: plan for plan in data["plans"]}
models = {model["id"]: model for model in data["models"]}
rows = data["rows"]
request_rows = data["requestRows"]
row_ids = {row["id"] for row in rows}
request_ids = {row["id"] for row in request_rows}
all_route_ids = row_ids | request_ids

for key, actual in (
    ("planCount", len(plans)),
    ("modelCount", len(models)),
    ("comparableRouteCount", len(rows)),
    ("requestRouteCount", len(request_rows)),
    ("unquantifiedPlanCount", len(data["unquantifiedPlans"])),
):
    if data["summary"].get(key) != actual:
        errors.append(f"summary.{key} mismatch: {data['summary'].get(key)} != {actual}")

seen: set[str] = set()
for row in rows + request_rows:
    if row["id"] in seen:
        errors.append(f"duplicate route id: {row['id']}")
    seen.add(row["id"])
    if row["planId"] not in plans:
        errors.append(f"{row['id']}: missing plan")
    if row["modelId"] not in models:
        errors.append(f"{row['id']}: missing model")
    for mix_id in data["mixes"]:
        metrics = row[mix_id]
        for key, value in metrics.items():
            if isinstance(value, float) and not math.isfinite(value):
                errors.append(f"{row['id']} {mix_id}.{key}: non-finite")
        if row["id"] in row_ids:
            if not (metrics.get("monthlyTokensM") or 0) > 0:
                errors.append(f"{row['id']} {mix_id}: missing token capacity")
            if not (metrics.get("subscriptionUsdPerM") or 0) > 0:
                errors.append(f"{row['id']} {mix_id}: missing subscription token cost")
            if row.get("intelligence") and not (metrics.get("qualityAdjustedUsdPerM") or 0) > 0:
                errors.append(f"{row['id']} {mix_id}: missing quality-adjusted token cost")

valid_classes = {"token", "request", "managed", "relative", "provider-hidden"}
for plan in plans.values():
    if plan.get("comparisonClass") not in valid_classes:
        errors.append(f"{plan['id']}: invalid comparison class {plan.get('comparisonClass')}")
    if not isinstance(plan.get("missingFields"), list):
        errors.append(f"{plan['id']}: missingFields must be a list")
    if not plan.get("researchStatus"):
        errors.append(f"{plan['id']}: researchStatus missing")
    if plan.get("comparisonClass") == "provider-hidden" and not plan.get("missingFields"):
        errors.append(f"{plan['id']}: provider-hidden plan lacks exact missing fields")

for provider in ("OpenAI Codex", "Claude Code", "Grok Build", "Synthetic"):
    if not any(plan["provider"] == provider for plan in plans.values()):
        errors.append(f"baseline provider missing: {provider}")
if data["summary"].get("defaultHidesOwned") is not False:
    errors.append("owned plans must be visible by default")
if not any(row.get("owned") for row in rows):
    errors.append("no owned baseline route remains in universal rows")

for plan_id in ("grok-build-basic", "grok-build-supergrok", "grok-build-pro", "grok-build-heavy"):
    if plan_id not in plans:
        errors.append(f"missing Grok tier: {plan_id}")
for provider in ("ZenMux", "Nous Portal", "JetBrains AI", "Zed", "Warp", "Replit", "Cosine", "Codebuff", "Google Jules", "Venice.ai", "Fireworks Fire Pass"):
    if not any(plan["provider"] == provider for plan in plans.values()):
        errors.append(f"verified provider adapter missing: {provider}")

for plan_id in (
    "copilot-business", "copilot-enterprise", "command-team-pro", "cursor-teams", "kilo-teams-platform",
    "augment-business", "gitlab-duo-premium", "tabnine-code-assistant", "tabnine-agentic-platform",
    "jetbrains-organization-pro", "jetbrains-organization-ultimate", "zed-business",
):
    if plan_id not in plans:
        errors.append(f"monthly team tier missing: {plan_id}")

for plan_id in ("ozore-basic", "ozore-pro"):
    if plan_id not in plans:
        errors.append(f"current Ozore tier missing: {plan_id}")
    elif plans[plan_id].get("comparisonClass") != "token":
        errors.append(f"{plan_id}: Ozore must be token-comparable")
for stale in ("ozore-starter", "ozore-builder", "ozore-max"):
    if stale in plans:
        errors.append(f"stale Ozore tier survived: {stale}")
for plan_id in ("ai-router-starter", "ai-router-pro", "ai-router-business"):
    if plan_id not in plans:
        errors.append(f"current AI Router tier missing: {plan_id}")
    elif plans[plan_id].get("comparisonClass") != "managed":
        errors.append(f"{plan_id}: routed complexity credits must remain managed units")
for stale in ("catalog-ai-router-developer", "catalog-ai-router-max"):
    if stale in plans:
        errors.append(f"stale AI Router tier survived: {stale}")

for plan_id, weekly in (("catalog-qwen-global-lite", 2_500),
                        ("catalog-qwen-global-standard", 10_000),
                        ("catalog-qwen-global-pro", 40_000)):
    plan = plans.get(plan_id)
    if not plan:
        errors.append(f"Qwen Global tier missing: {plan_id}")
        continue
    if plan.get("allowance", {}).get("weeklyCredits") != weekly:
        errors.append(f"{plan_id}: weekly Qwen credits mismatch")
    if plan.get("models") != ["qwen3.6-plus"]:
        errors.append(f"{plan_id}: derived Qwen3.6 Plus route missing")
    if not any(row["planId"] == plan_id and row["modelId"] == "qwen3.6-plus" for row in rows):
        errors.append(f"{plan_id}: token route not generated")

if any(row["planId"] == "claude-pro" and row["modelId"] == "claude-fable-5" for row in rows):
    errors.append("Claude Pro must not receive included Fable capacity")
for plan_id in ("claude-max-5x", "claude-max-20x"):
    matches = [row for row in rows if row["planId"] == plan_id and row["modelId"] == "claude-fable-5"]
    if not matches or any(abs(row.get("allowanceFraction", 0) - .5) > 1e-9 for row in matches):
        errors.append(f"{plan_id}: Fable 50% allowance cap missing")

for plan_id in ("clinepass", "factory-pro", "factory-plus", "factory-max",
                "catalog-google-ai-plus", "catalog-google-ai-pro",
                "catalog-google-ai-ultra-5x", "catalog-google-ai-ultra-20x",
                "catalog-byteplus-modelark-lite", "catalog-byteplus-modelark-pro"):
    if plan_id not in plans:
        errors.append(f"relative-plan record missing: {plan_id}")
    elif plans[plan_id].get("comparisonClass") != "relative":
        errors.append(f"{plan_id}: expected relative comparison class")

for mix_id in data["mixes"]:
    for collection in ("frontiers", "alternativeFrontiers"):
        for ids in data[collection][mix_id].values():
            for route_id in ids:
                if route_id not in row_ids:
                    errors.append(f"{collection}.{mix_id}: missing token route {route_id}")
    for collection in ("shortlists", "alternativeShortlists"):
        for ids in data[collection][mix_id].values():
            for route_id in ids:
                if route_id not in row_ids:
                    errors.append(f"{collection}.{mix_id}: missing token route {route_id}")

if len(data.get("planSummaries", [])) != len(plans):
    errors.append("one plan summary is required for every plan")
if not data.get("researchCoverage"):
    errors.append("postprocessed research coverage is missing")
else:
    if data["researchCoverage"].get("plansWithAdvertisedModelEvidence", 0) <= 0:
        errors.append("advertised model evidence count is empty")
for model in data["models"]:
    expected = sum(row["modelId"] == model["id"] for row in rows + request_rows)
    if model.get("subscriptionRouteCount") != expected:
        errors.append(f"{model['id']}: subscriptionRouteCount {model.get('subscriptionRouteCount')} != {expected}")

workflow_dir = ROOT / ".github/workflows"
if workflow_dir.exists() and any(path.suffix.lower() in {".yml", ".yaml"} for path in workflow_dir.iterdir()):
    errors.append("active GitHub Actions workflow found")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Validated {len(plans)} plans, {len(models)} models, {len(rows)} token routes, {len(request_rows)} request routes, current Ozore/AI Router/Qwen records, team tiers, relative plans, baseline visibility, Claude Fable access, and zero active Actions workflows.")
