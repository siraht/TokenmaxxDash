"""Add public per-seat team subscriptions that the individual-plan importer skips."""
from __future__ import annotations

from typing import Any


def _append(plans: list[dict[str, Any]], row: dict[str, Any]) -> None:
    if not any(plan["id"] == row["id"] for plan in plans):
        plans.append(row)


def _base(*, id: str, provider: str, plan: str, price: float, source: str,
          allowance: dict[str, Any], models: list[str] | None = None,
          confidence: str = "official", comparison_class: str = "managed",
          research_status: str = "quantified-managed", missing: list[str] | None = None,
          note: str | None = None) -> dict[str, Any]:
    return {
        "id": id, "provider": provider, "plan": plan, "priceUsd": float(price),
        "models": models or [], "allowance": allowance, "source": source,
        "confidence": confidence, "owned": False, "windows": None,
        "policy": "team or organization coding subscription", "note": note,
        "currency": "USD", "originalPrice": float(price), "routeRates": {},
        "monthlyUsdByModel": {}, "routeNotes": {}, "modelAllowanceFraction": {},
        "accessByModel": {}, "supplemental": False,
        "comparisonClass": comparison_class, "missingFields": missing or [],
        "researchStatus": research_status, "sourceType": "primary-or-measured",
        "rankable": comparison_class in {"token", "request"} and bool(models),
    }


def apply_team_plans(plans: list[dict[str, Any]], top_catalog: list[str]) -> None:
    for name, slug, price, pool in (
        ("Business", "business", 19, 19),
        ("Enterprise", "enterprise", 39, 39),
    ):
        _append(plans, _base(
            id=f"copilot-{slug}", provider="GitHub Copilot", plan=name, price=price,
            models=top_catalog, allowance={"kind": "apiPool", "monthlyUsd": pool,
                                           "monthlyAiCredits": int(pool * 100)},
            source="https://docs.github.com/copilot/reference/copilot-billing/models-and-pricing",
            comparison_class="token", research_status="quantified", missing=[],
            note="Per-user organization tier; one AI Credit represents $0.01 of model token usage.",
        ))

    _append(plans, _base(
        id="augment-business", provider="Augment Code", plan="Business", price=100,
        allowance={"kind": "publishedValue", "monthlyUsd": 71.43,
                   "monthlyUsageAllowanceUsd": 100, "serviceFee": 0.40},
        source="https://www.augmentcode.com/pricing", confidence="secondary",
        missing=["exact served-model catalog", "allocation of usage between model inference and other services"],
        note="$100 usage allowance; if spent entirely on LLM inference at API list price plus a 40% service fee, the raw model-list value is at most $71.43.",
    ))
    _append(plans, _base(
        id="gitlab-duo-premium", provider="GitLab Duo", plan="Premium", price=29,
        allowance={"kind": "publishedValue", "monthlyUsd": 12, "monthlyGitLabCredits": 12},
        source="https://about.gitlab.com/pricing/",
        missing=["exact served-model catalog", "model-token deduction formula", "share of credits spent on non-token Duo features"],
        note="$12 of GitLab Credits are included per user/month; one GitLab Credit represents $1 of eligible usage.",
    ))
    for name, slug, price in (("Code Assistant", "code-assistant", 39),
                               ("Agentic Platform", "agentic-platform", 59)):
        _append(plans, _base(
            id=f"tabnine-{slug}", provider="Tabnine", plan=name, price=price,
            allowance={"kind": "hidden", "claim": "enterprise inference allowance"},
            source="https://www.tabnine.com/pricing", confidence="official-partial",
            comparison_class="provider-hidden", research_status="provider-hidden",
            missing=["absolute included inference pool", "served-model catalog and routing",
                     "model-token or work-unit deduction formula"],
            note="The per-user monthly price is public; the included inference volume needed for $/token comparison is not.",
        ))

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
