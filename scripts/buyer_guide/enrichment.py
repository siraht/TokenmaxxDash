"""Finish the buyer-guide plan catalog with verified provider adapters.

The broad catalog deliberately discovers more plans than can be normalized. This
module runs after the base plan fragments and turns every plan into one of five
explicit comparison classes: token, request, managed, relative, or provider-hidden.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _plan(provider: str, plan: str, price: float, *, id: str, models: list[str], allowance: dict[str, Any], source: str,
          confidence: str = "official", owned: bool = False, windows: str | None = None, policy: str = "unknown",
          note: str | None = None, route_rates: dict[str, dict[str, float]] | None = None,
          monthly_usd_by_model: dict[str, float] | None = None,
          model_allowance_fraction: dict[str, float] | None = None,
          access_by_model: dict[str, str] | None = None,
          comparison_class: str | None = None, missing_fields: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": id, "provider": provider, "plan": plan, "priceUsd": float(price), "models": models,
        "allowance": allowance, "source": source, "confidence": confidence, "owned": owned,
        "windows": windows, "policy": policy, "note": note, "currency": "USD", "originalPrice": float(price),
        "routeRates": route_rates or {}, "monthlyUsdByModel": monthly_usd_by_model or {}, "routeNotes": {},
        "modelAllowanceFraction": model_allowance_fraction or {}, "accessByModel": access_by_model or {},
        "supplemental": False, "comparisonClass": comparison_class, "missingFields": missing_fields or [],
    }


def _replace_provider(plans: list[dict[str, Any]], provider: str, rows: list[dict[str, Any]]) -> None:
    plans[:] = [row for row in plans if row["provider"] != provider]
    plans.extend(rows)


def _kind_metadata(plan: dict[str, Any]) -> tuple[str, list[str], str]:
    kind = plan.get("allowance", {}).get("kind", "hidden")
    models = plan.get("models", [])
    if kind in {"apiPool", "apiPoolRange", "credits", "rawTokens", "rawTokensEstimate"}:
        missing: list[str] = []
        if not models:
            missing.append("exact served-model catalog")
        if kind == "apiPoolRange":
            missing.append("provider-published absolute subscription pool")
            status = "measured-range"
        elif kind == "rawTokensEstimate":
            missing.append("provider-published raw-token allowance")
            status = "secondary-estimate"
        else:
            status = "quantified"
        return "token", missing, status
    if kind == "requests":
        return "request", ["observed token distribution per request"], "quantified-request"
    if kind in {"managedTasks", "workUnits", "platformCredits", "publishedValue", "managedTokens"}:
        return "managed", ["model-token conversion", "externally comparable task-size distribution"], "quantified-managed"
    if kind == "unlimited":
        return "managed", ["sustained throughput ceiling", "fair-use throttling threshold", "model-token distribution"], "fair-use"
    if kind == "relative":
        return "relative", ["absolute base-tier allowance", "model-specific deduction formula"], "official-relative"
    if kind == "weightedPlanTokens":
        return "relative", ["complete per-model plan-token weights"], "official-partial"
    missing = ["absolute included allowance", "model-specific deduction formula"]
    if plan.get("allowance", {}).get("claim"):
        missing.append("conversion of advertised claim into a numeric pool")
    return "provider-hidden", missing, "provider-hidden"


def apply_enrichment(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]], top_catalog: list[str],
                     open_catalog: list[str], data_dir: Path) -> None:
    """Mutate ``plans`` in-place with current official adapters and audit fields."""
    frontier_models = [m for m in (
        "claude-opus-5", "claude-fable-5", "claude-sonnet-5", "claude-haiku-4.5",
        "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "grok-4.5", "kimi-k3", "glm-5.2",
        "deepseek-v4-flash", "deepseek-v4-pro") if m in models]
    jetbrains_models = [m for m in (
        "claude-opus-5", "claude-fable-5", "claude-sonnet-5", "claude-haiku-4.5",
        "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna") if m in models]

    # xAI publishes model API rates, but the consumer Build plan still uses a
    # shared opaque weekly compute pool. Keep all four current tiers visible.
    _replace_provider(plans, "Grok Build", [
        _plan("Grok Build", name, price, id=f"grok-build-{slug}", models=["grok-4.5"],
              allowance={"kind": "hidden", "claim": "shared weekly compute pool"},
              source="https://grok.com/", confidence="official-partial", owned=True,
              windows="Shared weekly pool across Grok surfaces", policy="subscription coding",
              comparison_class="provider-hidden",
              missing_fields=["absolute weekly compute pool", "Build model weighting", "cross-surface consumption formula"])
        for name, slug, price in (("Basic", "basic", 10), ("SuperGrok", "supergrok", 30),
                                  ("Pro", "pro", 100), ("Heavy", "heavy", 300))
    ])

    _replace_provider(plans, "ZenMux", [
        _plan("ZenMux", name, price, id=f"zenmux-{slug}", models=top_catalog,
              allowance={"kind": "apiPool", "monthlyUsd": value},
              source="https://zenmux.ai/docs/guide/subscription.html",
              windows=f"{five_h} Flow/5h; weekly and monthly Flow ceilings",
              policy="personal development; subscription keys are not for production",
              note="Flow is anchored to a published USD value; route deductions remain model-specific.")
        for name, slug, price, value, five_h in (("Pro", "pro", 20, 30.03, 50),
                                                  ("Max", "max", 100, 180.15, 300),
                                                  ("Ultra", "ultra", 200, 480.40, 800))
    ])
    _replace_provider(plans, "Nous Portal", [
        _plan("Nous Portal", name, price, id=f"nous-{slug}", models=top_catalog,
              allowance={"kind": "apiPool", "monthlyUsd": value}, source="https://portal.nousresearch.com/",
              policy="personal agents and hosted tools",
              note="Models, hosted tools, and cloud hosting draw from the same credit balance.")
        for name, slug, price, value in (("Plus", "plus", 20, 22), ("Super", "super", 100, 110),
                                         ("Ultra", "ultra", 200, 220))
    ])
    _replace_provider(plans, "JetBrains AI", [
        _plan("JetBrains AI", name, price, id=f"jetbrains-{slug}", models=jetbrains_models,
              allowance={"kind": "apiPool", "monthlyUsd": value},
              source="https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html",
              policy="interactive IDE and integrated agents",
              note="One AI Credit equals $1. An active supported JetBrains IDE license is also required.")
        for name, slug, price, value in (("AI Pro", "pro", 10, 10), ("AI Ultimate", "ultimate", 30, 35))
    ])

    zed_rates = {
        model_id: {"fresh": model["input"] * 1.10,
                   "cache": (model.get("cache") if model.get("cache") is not None else model["input"]) * 1.10,
                   "output": model["output"] * 1.10}
        for model_id, model in models.items()
        if model.get("input") is not None and model.get("output") is not None
    }
    _replace_provider(plans, "Zed", [
        _plan("Zed", "Pro", 10, id="zed-pro", models=frontier_models,
              allowance={"kind": "apiPool", "monthlyUsd": 5}, route_rates=zed_rates,
              source="https://zed.dev/pricing", policy="interactive coding",
              note="$5 hosted-token credit at API list price +10%; unlimited edit predictions are additional unpriced value.")
    ])
    _replace_provider(plans, "Warp", [
        _plan("Warp", name, price, id=f"warp-{slug}", models=frontier_models,
              allowance={"kind": "apiPool", "monthlyUsd": value}, source="https://www.warp.dev/pricing",
              policy="interactive and cloud agents",
              note="The published dollar value includes Warp Agent usage; hosted compute can also consume credits.")
        for name, slug, price, value in (("Build", "build", 20, 20), ("Business", "business", 50, 20),
                                         ("Max", "max", 200, 240))
    ])

    _replace_provider(plans, "Replit", [
        _plan("Replit", name, price, id=f"replit-{slug}", models=[],
              allowance={"kind": "platformCredits", "monthlyUsd": value, "parallelAgents": concurrency},
              source="https://replit.com/pricing", policy="managed app-building platform",
              comparison_class="managed", missing_fields=["model-specific token ledger", "compute/model split"])
        for name, slug, price, value, concurrency in (("Core", "core", 25, 25, 2),
                                                       ("Pro", "pro", 100, 100, 10))
    ])
    _replace_provider(plans, "Cosine", [
        _plan("Cosine", name, price, id=f"cosine-{slug}", models=[],
              allowance={"kind": "workUnits", "monthlyCredits": credits, "addonUsdPerMillionCredits": addon},
              source="https://cosine.sh/pricing", policy="coding agent and cloud execution",
              comparison_class="managed", missing_fields=["credits per standardized coding task", "model/cloud-execution split"])
        for name, slug, price, credits, addon in (("Starter", "starter", 19, 4_000_000, 6.5),
                                                   ("Team", "team", 199, 47_000_000, 5.0),
                                                   ("Enterprise", "enterprise", 999, 240_000_000, 4.5))
    ])
    _replace_provider(plans, "Codebuff", [
        _plan("Codebuff", name, price, id=f"codebuff-{slug}", models=[],
              allowance={"kind": "relative", "relativeToBase": multiplier, "paygUsdPerCredit": 0.01},
              source="https://www.codebuff.com/pricing", policy="interactive coding agent",
              comparison_class="relative", missing_fields=["absolute credits in the 1x tier", "credits per standardized task"])
        for name, slug, price, multiplier in (("1×", "1x", 100, 1.0), ("2.5×", "2-5x", 200, 2.5),
                                               ("7×", "7x", 500, 7.0))
    ])
    _replace_provider(plans, "Google Jules", [
        _plan("Google Jules", name, price, id=f"jules-{slug}", models=[],
              allowance={"kind": "managedTasks", "dailyTasks": daily, "monthlyTaskCeiling": daily * 30,
                         "concurrentTasks": concurrency},
              source="https://jules.google/docs/usage-limits", policy="managed coding agent",
              comparison_class="managed", missing_fields=["task difficulty normalization", "tokens and model route per task"])
        for name, slug, price, daily, concurrency in (("Google AI Pro", "pro", 19.99, 100, 15),
                                                       ("Google AI Ultra", "ultra", 99.99, 300, 60))
    ])
    _replace_provider(plans, "Venice.ai", [
        _plan("Venice.ai", name, price, id=f"venice-{slug}", models=open_catalog,
              allowance={"kind": "publishedValue", "monthlyUsd": value, "credits": credits, "creditsPerUsd": 100},
              source="https://venice.ai/pricing", policy="OpenAI-compatible API and consumer text",
              comparison_class="managed",
              missing_fields=["text-model-specific credit deduction table", "allocation of credits between text, image, video, and API"],
              note="Unlimited/fair-use text is separate. Premium credits are shared across text, media, and API usage.")
        for name, slug, price, credits, value in (("Pro", "pro", 18, 100, 1),
                                                   ("Pro Plus", "pro-plus", 68, 7500, 75),
                                                   ("Max", "max", 200, 22500, 225))
    ])
    _replace_provider(plans, "Fireworks Fire Pass", [
        _plan("Fireworks Fire Pass", "Early Access", 49, id="fireworks-fire-pass", models=["kimi-k2.6"],
              allowance={"kind": "unlimited", "coveredModel": "kimi-k2.6", "perTokenCharge": 0},
              source="https://docs.fireworks.ai/firepass", policy="personal agentic coding only",
              windows="Fair-use early-access pass; invite-only; renewal not guaranteed",
              comparison_class="managed", missing_fields=["sustained throughput limit", "request/concurrency throttles"],
              note="Covers Kimi K2.6 Turbo only; all other Fireworks models remain PAYG.")
    ])

    for plan in plans:
        if plan["provider"] != "Claude Code":
            continue
        plan.setdefault("modelAllowanceFraction", {})
        plan.setdefault("accessByModel", {})
        if plan["plan"] == "Pro":
            plan["modelAllowanceFraction"]["claude-fable-5"] = 0.0
            plan["accessByModel"]["claude-fable-5"] = "PAYG-only; not included"
        else:
            plan["modelAllowanceFraction"]["claude-fable-5"] = 0.5
            plan["accessByModel"]["claude-fable-5"] = "Included, capped at 50% of the shared weekly meter"

    try:
        broad = json.loads((data_dir / "plans.json").read_text())
    except (OSError, json.JSONDecodeError):
        broad = []
    broad_by_key = {(row.get("provider"), row.get("name")): row for row in broad}
    for plan in plans:
        broad_row = broad_by_key.get((plan["provider"], plan["plan"]))
        if not broad_row or broad_row.get("calculationStatus") not in {"exact", "derived"}:
            continue
        if plan.get("allowance", {}).get("kind") != "hidden":
            continue
        included = broad_row.get("includedValueUsdMonthly")
        quotas = broad_row.get("quotas") or {}
        allowance_type = (broad_row.get("allowanceType") or "").lower()
        if isinstance(included, (int, float)):
            plan["allowance"] = {"kind": "publishedValue", "monthlyUsd": included, "nativeQuotas": quotas}
            plan["comparisonClass"] = "managed"
            plan["missingFields"] = ["exact served-model catalog", "model-token or standardized-task conversion"]
        elif "monthlyRawTokens" in quotas:
            plan["allowance"] = {"kind": "rawTokens", "monthlyTokens": quotas["monthlyRawTokens"]}
        elif "dailyTasks" in quotas:
            plan["allowance"] = {"kind": "managedTasks", **quotas}
        elif "monthlyCredits" in quotas or "monthlyAiCredits" in quotas:
            plan["allowance"] = {"kind": "workUnits", **quotas}
        elif "builder" in allowance_type and "monthlyBuilderTokens" in quotas:
            plan["allowance"] = {"kind": "managedTokens", **quotas}

    for plan in plans:
        comparison_class, missing, research_status = _kind_metadata(plan)
        plan["comparisonClass"] = plan.get("comparisonClass") or comparison_class
        plan["missingFields"] = list(dict.fromkeys(plan.get("missingFields", []) + missing))
        plan["researchStatus"] = research_status
        plan["sourceType"] = "secondary" if plan.get("confidence") == "secondary" else "primary-or-measured"
        plan["rankable"] = plan["comparisonClass"] in {"token", "request"} and bool(plan.get("models"))
