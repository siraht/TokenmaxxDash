"""Promote officially published tier multipliers into relative comparisons.

Relative plans are useful for comparing tiers inside a product even when the
provider withholds the absolute base pool. They remain excluded from $/token
rankings until that base denominator and the model-specific weights are known.
"""
from __future__ import annotations

from typing import Any


def _set_relative(plan: dict[str, Any], allowance: dict[str, Any], *, missing: list[str], note: str | None = None) -> None:
    plan["allowance"] = {"kind": "relative", **allowance}
    plan["comparisonClass"] = "relative"
    plan["researchStatus"] = "official-relative" if plan.get("confidence") != "secondary" else "secondary-relative"
    plan["missingFields"] = list(dict.fromkeys(missing))
    plan["rankable"] = False
    if note:
        plan["note"] = note


def apply_relative_plans(plans: list[dict[str, Any]]) -> None:
    by_id = {plan["id"]: plan for plan in plans}

    cline = by_id.get("clinepass")
    if cline:
        _set_relative(
            cline,
            {"advertisedApiValueMultipleLow": 2.0, "advertisedApiValueMultipleHigh": 5.0,
             "windows": ["five-hour", "weekly", "monthly"]},
            missing=["absolute five-hour allowance", "absolute weekly allowance", "absolute monthly allowance",
                     "model-specific deduction formula"],
            note="Cline advertises roughly 2–5× standard API-rate usage, but the numerical five-hour, weekly, and monthly pools are not published.",
        )

    factory_multipliers = {"factory-pro": 1.0, "factory-plus": 5.0, "factory-max": 10.0}
    for plan_id, multiplier in factory_multipliers.items():
        plan = by_id.get(plan_id)
        if plan:
            _set_relative(
                plan,
                {"relativeToFactoryPro": multiplier, "windows": ["five-hour", "seven-day", "thirty-day"]},
                missing=["absolute Factory Pro five-hour pool", "absolute Factory Pro seven-day pool",
                         "absolute Factory Pro thirty-day pool", "model-specific deduction multipliers"],
                note=f"Factory publishes this tier as approximately {multiplier:g}× Pro capacity across rolling windows; the absolute Pro buckets remain hidden.",
            )

    google_multipliers = {
        "catalog-google-ai-plus": {"relativeToFree": 2.0, "relativeToPro": 0.5},
        "catalog-google-ai-pro": {"relativeToFree": 4.0, "relativeToPro": 1.0},
        "catalog-google-ai-ultra-5x": {"relativeToPro": 5.0},
        "catalog-google-ai-ultra-20x": {"relativeToPro": 20.0},
    }
    for plan_id, multipliers in google_multipliers.items():
        plan = by_id.get(plan_id)
        if plan:
            _set_relative(
                plan,
                {**multipliers, "products": ["Gemini CLI", "Gemini Code Assist", "Antigravity"]},
                missing=["absolute product-specific base quota", "Antigravity model-specific weights",
                         "cross-product shared-pool formula"],
                note="Google publishes relative access levels, while Gemini CLI, Code Assist, Antigravity, and other plan surfaces retain separate or product-specific limits.",
            )

    byteplus_multipliers = {
        "catalog-byteplus-modelark-lite": 1.0,
        "catalog-byteplus-modelark-pro": 5.0,
    }
    for plan_id, multiplier in byteplus_multipliers.items():
        plan = by_id.get(plan_id)
        if plan:
            _set_relative(
                plan,
                {"relativeToModelArkLite": multiplier, "secondaryClaim": "Lite is marketed as roughly three Claude Pro allowances"},
                missing=["absolute ModelArk Lite pool", "primary-source numerical quota",
                         "model-specific token or credit formula"],
                note="The maintained market sources describe Pro as five times Lite and Lite as roughly three Claude Pro allowances; no primary numerical base pool was found.",
            )
