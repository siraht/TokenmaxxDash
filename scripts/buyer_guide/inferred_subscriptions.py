"""Deep quota inference for subscription providers with hidden headline limits.

This module runs after the official-plan adapters. It uses four evidence levels:

* exact published pool or request ceiling;
* measured token/API-value range tied to a named plan;
* conservative lower bound tied to a named plan; and
* account-calibratable meter whose denominator can be recovered from the
  provider's own usage endpoint plus local token/cost logs.

It never transfers an unlabeled public sample to a specific paid tier.
"""
from __future__ import annotations

from typing import Any

WEEKS_PER_MONTH = 365.2425 / 12 / 7


def _by_id(plans: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {plan["id"]: plan for plan in plans}


def _model_subset(models: dict[str, dict[str, Any]], *ids: str) -> list[str]:
    return [model_id for model_id in ids if model_id in models]


def _finish(plan: dict[str, Any], *, comparison: str, status: str, confidence: str,
            missing: list[str], rankable: bool) -> None:
    plan["comparisonClass"] = comparison
    plan["researchStatus"] = status
    plan["confidence"] = confidence
    plan["missingFields"] = list(dict.fromkeys(missing))
    plan["sourceType"] = "primary-or-measured"
    plan["rankable"] = rankable


def _append_plan(plans: list[dict[str, Any]], *, id: str, provider: str, plan: str,
                 price: float, allowance: dict[str, Any], source: str,
                 note: str, comparison: str, status: str, missing: list[str]) -> None:
    if any(row["id"] == id for row in plans):
        return
    plans.append({
        "id": id,
        "provider": provider,
        "plan": plan,
        "priceUsd": float(price),
        "models": [],
        "allowance": allowance,
        "source": source,
        "confidence": "official",
        "owned": False,
        "windows": None,
        "policy": "commercial coding automation",
        "note": note,
        "currency": "USD",
        "originalPrice": float(price),
        "routeRates": {},
        "monthlyUsdByModel": {},
        "routeNotes": {},
        "modelAllowanceFraction": {},
        "accessByModel": {},
        "supplemental": False,
        "comparisonClass": comparison,
        "missingFields": missing,
        "researchStatus": status,
        "sourceType": "primary-or-measured",
        "rankable": False,
    })


def _cursor(plans: list[dict[str, Any]]) -> None:
    first_party = ("grok-4.5", "composer-2.5")
    for plan in plans:
        if plan["id"] not in {"cursor-pro", "cursor-proplus", "cursor-ultra"}:
            continue
        pool = float(plan["allowance"]["monthlyUsd"])
        plan["allowance"].update({
            "guaranteedOtherModelsUsd": pool,
            "otherModelsBilling": "model API price",
            "cursorModelsPool": "separate numerical pool not published",
            "bonusUsage": "variable additional usage after the guaranteed pool",
        })
        plan.setdefault("modelAllowanceFraction", {})
        plan.setdefault("accessByModel", {})
        for model_id in first_party:
            if model_id in plan.get("models", []):
                plan["modelAllowanceFraction"][model_id] = 0.0
                plan["accessByModel"][model_id] = "Included through the separate Cursor Models pool; excluded from the guaranteed Other Models dollar pool."
        plan["note"] = (
            f"The ${pool:g} Other Models pool is an exact guaranteed monthly denominator charged at model API prices. "
            "Cursor Grok and Composer use a separate first-party pool, and bonus usage above the guaranteed pool is variable."
        )
        plan["evidenceSources"] = [
            "https://cursor.com/docs/models-and-pricing",
            "https://cursor.com/pricing",
        ]
        _finish(
            plan,
            comparison="token",
            status="official-exact-third-party-pool",
            confidence="official",
            missing=["numerical Cursor Models pool", "size and eligibility of variable bonus usage"],
            rankable=True,
        )


def _claude(plans: list[dict[str, Any]]) -> None:
    # Current-accounting range from 2026 issue telemetry. Historical pre-drift
    # value is retained separately rather than inflating the current estimate.
    max20_weekly_api = (625.0, 1000.0, 1675.0)
    configs = {
        "claude-pro": {
            "apiDivisor": 20.0,
            "weeklyRaw": (0.20e9, 0.25e9, 0.28e9),
        },
        "claude-max-5x": {
            "apiDivisor": 4.0,
            "weeklyRaw": (1.00e9, 1.25e9, 1.40e9),
        },
        "claude-max-20x": {
            "apiDivisor": 1.0,
            "weeklyRaw": (3.54e9, 4.57e9, 5.60e9),
        },
    }
    plan_by_id = _by_id(plans)
    for plan_id, cfg in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        divisor = cfg["apiDivisor"]
        weekly_api = tuple(value / divisor for value in max20_weekly_api)
        monthly_api = tuple(value * WEEKS_PER_MONTH for value in weekly_api)
        weekly_raw = cfg["weeklyRaw"]
        monthly_raw = tuple(value * WEEKS_PER_MONTH for value in weekly_raw)
        plan["allowance"] = {
            "kind": "apiPoolRange",
            "monthlyUsdLow": monthly_api[0],
            "monthlyUsd": monthly_api[1],
            "monthlyUsdHigh": monthly_api[2],
            "weeklyApiEquivalentUsdLow": weekly_api[0],
            "weeklyApiEquivalentUsd": weekly_api[1],
            "weeklyApiEquivalentUsdHigh": weekly_api[2],
            "weeklyRawTokensLow": weekly_raw[0],
            "weeklyRawTokens": weekly_raw[1],
            "weeklyRawTokensHigh": weekly_raw[2],
            "monthlyRawTokensLow": monthly_raw[0],
            "monthlyRawTokens": monthly_raw[1],
            "monthlyRawTokensHigh": monthly_raw[2],
            "historicalMax20WeeklyApiEquivalentUsdRange": [2508.0, 5429.0],
            "historicalRegimeExcludedFromCurrentRanking": True,
            "meterType": "shared rolling five-hour plus weekly model-weighted quota",
        }
        plan["source"] = "https://github.com/anthropics/claude-code/issues/84607"
        plan["evidenceSources"] = [
            "https://github.com/anthropics/claude-code/issues/84607",
            "https://github.com/anthropics/claude-code/issues/57699",
            "https://github.com/anthropics/claude-code/issues/43118",
            "https://platform.claude.com/docs/en/about-claude/pricing",
        ]
        plan["note"] = (
            "Current API-equivalent and raw-token ranges are reconstructed from deduplicated Claude Code logs and weekly meter movement. "
            "The much larger historical pre-accounting-change values are preserved as history, not used as the current central estimate."
        )
        plan.setdefault("modelAllowanceFraction", {})
        plan.setdefault("accessByModel", {})
        if plan_id == "claude-pro":
            plan["modelAllowanceFraction"]["claude-fable-5"] = 0.0
            plan["accessByModel"]["claude-fable-5"] = "PAYG usage credits from the first request; not included in Pro."
        else:
            plan["modelAllowanceFraction"]["claude-fable-5"] = 0.5
            plan["accessByModel"]["claude-fable-5"] = "Included on Max but capped at 50% of the shared weekly meter; the hidden Fable multiplier remains unknown."
        _finish(
            plan,
            comparison="token",
            status="measured-current-range",
            confidence="measured-low",
            missing=[
                "Anthropic-published absolute five-hour pool",
                "Anthropic-published absolute weekly pool",
                "current model, effort, cache-write, cache-read, and output meter weights",
                "Fable meter multiplier",
            ],
            rankable=True,
        )


def _kimi(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    # Direct Allegretto telemetry: 1.37–1.50B raw tokens/month. Other tiers
    # scale by Kimi's published 1×/5×/15×/30× Code relationship.
    base = (1.37e9, 1.435e9, 1.50e9)
    configs = {
        "kimi-moderato": 0.2,
        "kimi-allegretto": 1.0,
        "kimi-allegro": 3.0,
        "kimi-vivace": 6.0,
    }
    plan_by_id = _by_id(plans)
    available = _model_subset(
        models,
        "kimi-k3-256k",
        "kimi-k3",
        "kimi-k2.7-code",
        "kimi-k2.7-code-highspeed",
        "kimi-k2.6",
    )
    for plan_id, scale in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        low, center, high = (value * scale for value in base)
        plan["models"] = available
        plan["allowance"] = {
            "kind": "rawTokensEstimateRange",
            "monthlyTokensLow": low,
            "monthlyTokens": center,
            "monthlyTokensHigh": high,
            "capacityConfidence": "one-user-longitudinal-plus-official-tier-scaling",
            "directMeasurementTier": "Allegretto",
            "directMeasurementMonthlyRawTokensRange": [base[0], base[2]],
            "publishedTierScaleRelativeToAllegretto": scale,
            "fiveHourRequestsPublishedRange": [300, 1200],
            "weeklyRefreshDays": 7,
        }
        plan.setdefault("modelAllowanceFraction", {})
        plan.setdefault("accessByModel", {})
        if "kimi-k3-256k" in available:
            plan["modelAllowanceFraction"]["kimi-k3-256k"] = 1.0
            plan["accessByModel"]["kimi-k3-256k"] = "Included from Moderato upward; fixed 256K context."
        if "kimi-k3" in available:
            if plan_id == "kimi-moderato":
                plan["modelAllowanceFraction"]["kimi-k3"] = 0.0
                plan["accessByModel"]["kimi-k3"] = "Full 1M K3 context requires Allegretto or higher."
            else:
                plan["modelAllowanceFraction"]["kimi-k3"] = 0.5
                plan["accessByModel"]["kimi-k3"] = "Included; Kimi documents approximately 2× quota use versus K3 256K."
        if "kimi-k2.7-code-highspeed" in available:
            if plan_id == "kimi-moderato":
                plan["modelAllowanceFraction"]["kimi-k2.7-code-highspeed"] = 0.0
                plan["accessByModel"]["kimi-k2.7-code-highspeed"] = "HighSpeed requires Allegretto or higher."
            else:
                plan["modelAllowanceFraction"]["kimi-k2.7-code-highspeed"] = 1.0 / 3.0
                plan["accessByModel"]["kimi-k2.7-code-highspeed"] = "Same K2.7 Code ability at 5–6× output speed and approximately 3× quota use."
        plan["source"] = "https://github.com/Golden0Voyager/kimi-code-usage"
        plan["evidenceSources"] = [
            "https://github.com/Golden0Voyager/kimi-code-usage",
            "https://www.kimi.com/resources/kimi-code-introduction",
            "https://www.kimi.com/resources/kimi-k2-7-code-pricing",
            "https://forum.moonshot.ai/t/allegretto-annual-member-kimi-code-forced-highspeed-after-beta-3x-token-consumption-no-standard-toggle/460",
        ]
        plan["note"] = (
            "The raw-token range is anchored to five months of Allegretto ccusage data and scaled by Kimi's official tier relationship. "
            "Five-hour and weekly meters can bind first, and post-beta HighSpeed routing has changed realized burn for some users."
        )
        _finish(
            plan,
            comparison="token",
            status="measured-range-scaled-by-official-tier",
            confidence="measured-low",
            missing=[
                "multiple independent longitudinal token measurements",
                "absolute provider-published weekly token pool",
                "exact subscription meter weights for K3, K2.7 Standard, and HighSpeed",
            ],
            rankable=True,
        )


def _factory(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    multipliers = {
        "claude-fable-5": 4.0,
        "claude-opus-5": 2.0,
        "claude-opus-4.7": 2.0,
        "claude-opus-4.6": 2.0,
        "claude-sonnet-5": 0.8,
        "claude-sonnet-4.6": 1.2,
        "claude-haiku-4.5": 0.4,
        "gpt-5.6-sol": 2.0,
        "gpt-5.6-terra": 0.8,
        "gpt-5.6-luna": 0.08,
        "gpt-5.5": 2.0,
        "gpt-5.4": 1.0,
        "gpt-5.4-mini": 0.3,
        "gpt-5.3-codex": 0.7,
        "gemini-3.1-pro": 0.8,
        "gemini-3-flash": 0.2,
        "grok-4.5": 0.8,
        "glm-5.2": 0.56,
        "kimi-k3": 1.2,
        "kimi-k2.7-code": 0.38,
        "deepseek-v4-pro": 0.7,
        "minimax-m3": 0.12,
    }
    multipliers = {model_id: value for model_id, value in multipliers.items() if model_id in models}
    plan_units = {
        "factory-pro": (20_000_000, 10_000_000, 10_000_000),
        "factory-plus": (100_000_000, 50_000_000, 50_000_000),
        "factory-max": (200_000_000, 100_000_000, 100_000_000),
    }
    plan_by_id = _by_id(plans)
    for plan_id, (total, base, bonus) in plan_units.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        plan["models"] = list(multipliers)
        plan["allowance"] = {
            "kind": "standardTokens",
            "monthlyStandardTokens": total,
            "baseStandardTokens": base,
            "bonusStandardTokens": bonus,
            "modelMultipliers": multipliers,
            "freshWeight": 1.0,
            "cacheReadWeight": 0.1,
            "outputWeight": 5.0,
            "rollingWindows": ["five-hour", "seven-day", "thirty-day"],
            "droidCoreAfterStandardUsage": True,
        }
        plan["source"] = "https://docs.factory.ai/pricing/individuals"
        plan["evidenceSources"] = [
            "https://docs.factory.ai/pricing/individuals",
            "https://docs.factory.ai/models",
            "https://github.com/robinebers/openusage/pull/1003",
        ]
        plan["windows"] = "Independent rolling five-hour, seven-day, and thirty-day windows"
        plan["note"] = (
            "Factory's Standard-token pools are reconstructed from its usage API and published Pro/Plus/Max relationships. "
            "The model multipliers are official; raw-token capacity varies sharply with cache share, output share, and selected model."
        )
        _finish(
            plan,
            comparison="token",
            status="measured-standard-token-pool",
            confidence="measured",
            missing=[
                "numerical five-hour sublimit",
                "numerical seven-day sublimit",
                "confirmation that bonus Standard tokens remain available under every current account cohort",
            ],
            rankable=True,
        )


def _ollama(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    if "ollama-mixed-coding-route" not in models:
        return
    plan_by_id = _by_id(plans)
    pro_month = (58_000_000 / 0.408) * WEEKS_PER_MONTH
    configs = {
        "ollama-cloud-pro": pro_month,
        "ollama-cloud-max": pro_month * 5.0,
    }
    for plan_id, minimum in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        plan["models"] = ["ollama-mixed-coding-route"]
        prior = dict(plan.get("allowance", {}))
        plan["allowance"] = {
            "kind": "rawTokensLowerBound",
            "monthlyTokensMinimum": minimum,
            "measuredProWeeklyTokensObserved": 58_000_000,
            "measuredProWeeklyMeterMovement": 0.408,
            "impliedProWeeklyRawTokenMinimum": 58_000_000 / 0.408,
            "officialRelativeToPro": 1.0 if plan_id == "ollama-cloud-pro" else 5.0,
            "officialConcurrency": 3 if plan_id == "ollama-cloud-pro" else 10,
            "newSignupsPaused": bool(prior.get("newSignupsPaused")),
        }
        plan["source"] = "https://ollama.com/pricing"
        plan["evidenceSources"] = [
            "https://ollama.com/pricing",
            "https://github.com/jarvis-llm-codec/jarvis-code",
        ]
        plan["note"] = (
            "A public 10,000-turn Pro run moved the weekly meter 40.8% after at least 58M locally counted chat tokens. "
            "This yields a conservative raw-token lower bound; encoder, remote, and uncaptured usage can only increase the true capacity."
        )
        _finish(
            plan,
            comparison="token",
            status="measured-raw-token-lower-bound",
            confidence="measured-low",
            missing=[
                "complete model mix for the measured run",
                "encoder and server-side tokens omitted from local logs",
                "absolute provider-published five-hour and weekly pools",
                "numerical model usage-level weights",
            ],
            rankable=True,
        )


def _antigravity(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    route = "antigravity-mixed-coding-route"
    if route not in models:
        return
    configs = {
        "catalog-google-ai-plus": 0.5,
        "catalog-google-ai-pro": 1.0,
        "catalog-google-ai-ultra-5x": 5.0,
        "catalog-google-ai-ultra-20x": 20.0,
    }
    plan_by_id = _by_id(plans)
    # After the March report of <9M weekly input tokens, Google raised the
    # Antigravity model limits and then the weekly ceiling. The current range
    # deliberately stays below the old >300M/week regime.
    pro_weekly = (18_000_000, 24_000_000, 30_000_000)
    gemini_models = _model_subset(models, "gemini-3.1-pro", "gemini-3-flash")
    third_party = _model_subset(models, "claude-opus-4.6", "claude-sonnet-4.6")
    for plan_id, multiplier in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        weekly = tuple(value * multiplier for value in pro_weekly)
        monthly = tuple(value * WEEKS_PER_MONTH for value in weekly)
        advertised = list(gemini_models)
        if "ultra" in plan_id:
            advertised.extend(third_party)
        plan["models"] = list(dict.fromkeys(advertised + [route]))
        plan["modelAllowanceFraction"] = {model_id: 0.0 for model_id in advertised}
        plan["modelAllowanceFraction"][route] = 1.0
        plan["accessByModel"] = {
            model_id: "Model is available, but the compute-based weight is hidden; excluded from the mixed-pool raw-token estimate."
            for model_id in advertised
        }
        plan["accessByModel"][route] = "Measured mixed-route capacity; intentionally unscored because the model mix is unresolved."
        plan["allowance"] = {
            "kind": "rawTokensEstimateRange",
            "monthlyTokensLow": monthly[0],
            "monthlyTokens": monthly[1],
            "monthlyTokensHigh": monthly[2],
            "weeklyTokensLow": weekly[0],
            "weeklyTokens": weekly[1],
            "weeklyTokensHigh": weekly[2],
            "relativeToAiPro": multiplier,
            "capacityConfidence": "regime-adjusted-community-measurement",
            "historicalPreJanuaryWeeklyInputTokensGreaterThan": 300_000_000,
            "postMarchPreBoostWeeklyInputTokensLessThan": 9_000_000,
            "may2026ShortWindowIncrease": 3.0,
            "may2026WeeklyIncrease": 3.0,
            "meterType": "work-done compute budget with five-hour and weekly limits",
        }
        plan["source"] = "https://antigravity.google/docs/plans"
        plan["evidenceSources"] = [
            "https://antigravity.google/docs/plans",
            "https://antigravity.google/blog/changes-to-antigravity-plans",
            "https://www.theregister.com/2026/03/12/users_protest_as_google_antigravity_price_floats_upward/",
            "https://9to5google.com/2026/05/21/google-has-tripled-gemini-usage-limits-for-antigravity-twice/",
        ]
        plan["note"] = (
            "The range adjusts the documented March Pro measurement for Google's later paid-plan quota increases. "
            "It is intentionally modeled as an unscored mixed route because Gemini and third-party models consume a work-based pool differently."
        )
        _finish(
            plan,
            comparison="token",
            status="measured-post-boost-range",
            confidence="measured-low",
            missing=[
                "Google-published absolute compute pool",
                "per-model compute weights",
                "fresh post-boost token telemetry across multiple paid accounts",
            ],
            rankable=True,
        )


def _byteplus(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]]) -> None:
    plan_by_id = _by_id(plans)
    available = _model_subset(
        models,
        "glm-5.2",
        "glm-4.7",
        "deepseek-v4-flash",
        "deepseek-v4-pro",
        "kimi-k2.7-code",
        "minimax-m3",
    )
    configs = {
        "catalog-byteplus-modelark-lite": (1200, 9000, 18000),
        "catalog-byteplus-modelark-pro": (6000, 45000, 90000),
    }
    for plan_id, (five_h, weekly, monthly) in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        plan["models"] = available
        plan["allowance"] = {
            "kind": "requests",
            "monthlyQuota": monthly,
            "quotaPerRequest": {model_id: 1.0 for model_id in available},
            "fiveHourRequests": five_h,
            "weeklyRequests": weekly,
            "monthlyRequests": monthly,
        }
        plan["source"] = "https://docs.byteplus.com/en/docs/ModelArk/coding_plan"
        plan["note"] = (
            "Current maintained request ceilings are represented directly. A request remains a native unit because BytePlus does not publish a stable token shape for one coding request."
        )
        _finish(
            plan,
            comparison="request",
            status="official-request-ceilings",
            confidence="official",
            missing=["observed input, cache, and output token distribution per request"],
            rankable=True,
        )


def _grok(plans: list[dict[str, Any]]) -> None:
    sample_tokens = 12_340_000
    sample_weekly_fraction = 0.68
    lower_week = sample_tokens / sample_weekly_fraction
    lower_month = lower_week * WEEKS_PER_MONTH
    for plan in plans:
        if plan["provider"] != "Grok Build":
            continue
        plan["models"] = ["grok-4.5"]
        plan["allowance"] = {
            "kind": "calibratable",
            "billingEndpointWeeklyField": "weekly.usage_percent",
            "billingEndpointMonthlyUsedField": "monthly.used_usd",
            "billingEndpointMonthlyLimitField": "monthly.limit_usd",
            "settingsEndpointTierField": "subscription_tier_display",
            "localLogFields": ["input_tokens", "cached_input_tokens", "output_tokens", "model"],
            "calibrationFormula": "full bucket = normalized local usage delta / displayed quota-fraction delta",
            "publicUnmappedAccountSample": {
                "weeklyUsageFraction": sample_weekly_fraction,
                "localBuildRawTokens": sample_tokens,
                "rawWeeklyCapacityLowerBound": lower_week,
                "rawAverageMonthlyCapacityLowerBound": lower_month,
                "monthlyUsedUsd": 139.05,
                "monthlyLimitUsd": 180.0,
                "planTierNotPublished": True,
            },
        }
        plan["source"] = "https://github.com/danecwalker/groktok"
        plan["evidenceSources"] = [
            "https://github.com/danecwalker/groktok",
            "https://raw.githubusercontent.com/steipete/CodexBar/main/docs/grok.md",
            "https://grok.com/",
        ]
        plan["note"] = (
            "Grok is account-calibratable rather than unknowable: its billing API exposes weekly percentage and a USD-denominated monthly limit, while local Build logs expose tokens. "
            "The public $180 sample is retained as an unlabeled-account lower bound and is not assigned to a paid tier without a tier-labeled snapshot."
        )
        _finish(
            plan,
            comparison="calibratable",
            status="account-calibratable-public-sample",
            confidence="measured-low",
            missing=[
                "public sample pairing subscription tier with monthly.limit_usd",
                "plan-labeled clean before/after weekly meter snapshot",
                "cross-surface Grok usage not present in local Build logs",
            ],
            rankable=False,
        )


def _cline(plans: list[dict[str, Any]], open_catalog: list[str]) -> None:
    plan = _by_id(plans).get("clinepass")
    if not plan:
        return
    low = plan["priceUsd"] * 2.0
    high = plan["priceUsd"] * 5.0
    plan["models"] = list(open_catalog)
    plan["allowance"] = {
        "kind": "apiPoolRange",
        "monthlyUsdLow": low,
        "monthlyUsd": (low + high) / 2.0,
        "monthlyUsdHigh": high,
        "advertisedApiValueMultipleRange": [2.0, 5.0],
        "fiveHourUsageEndpoint": "GET https://api.cline.bot/api/v1/users/me/plan/usage-limits",
        "usageEndpointFields": ["fiveHour.percentUsed", "weekly.percentUsed", "monthly.percentUsed", "resetAt"],
        "transactionFields": ["model", "promptTokens", "completionTokens", "costUsd"],
        "calibrationFormula": "bucket API-value = summed transaction cost / displayed percent-used delta",
    }
    plan["source"] = "https://cline.bot/cline-pass"
    plan["evidenceSources"] = [
        "https://cline.bot/cline-pass",
        "https://github.com/baranbingol1/quotaboard/blob/c1d272325894a98f3ab0f60779585c36a162a9be/src/AiLimits.Infrastructure/Providers/Cline/ClinePassLimitStrategy.cs",
    ]
    plan["note"] = (
        "The 2–5× API-value claim is converted into a low/central/high monthly pool, and Cline's authenticated usage endpoint plus transaction history provides a reproducible path to replace the claim with an account measurement."
    )
    _finish(
        plan,
        comparison="token",
        status="official-value-range-account-calibratable",
        confidence="official-partial",
        missing=[
            "provider-published numerical five-hour pool",
            "provider-published numerical weekly pool",
            "provider-published numerical monthly pool",
            "clean public transaction-plus-meter calibration snapshot",
        ],
        rankable=True,
    )


def _devin(plans: list[dict[str, Any]]) -> None:
    configs = {
        "devin-pro": {
            "premiumMessagesPerDayRange": [8, 101],
            "premiumPlusMessagesPerDayRange": [7, 27],
            "lightweightMessagesPerDayRange": [47, 190],
            "dailyQuota": True,
        },
        "devin-max": {
            "premiumMessagesPerDayRange": [47, 631],
            "premiumPlusMessagesPerDayRange": [42, 170],
            "lightweightMessagesPerDayRange": [291, 1190],
            "dailyQuota": False,
        },
    }
    plan_by_id = _by_id(plans)
    for plan_id, estimates in configs.items():
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        plan["models"] = []
        plan["allowance"] = {
            "kind": "requestRange",
            **estimates,
            "weeklyQuota": True,
            "sharedSurfaces": ["Devin sessions", "Devin for Terminal", "Windsurf IDE"],
            "quotaBasis": "work and agent actions rather than a fixed message or token count",
            "onDemandCreditsAfterQuota": True,
        }
        plan["source"] = "https://docs.devin.ai/desktop/accounts/quota"
        plan["evidenceSources"] = [
            "https://docs.devin.ai/desktop/accounts/quota",
            "https://docs.devin.ai/admin/billing/self-serve",
            "https://www.creditsplan.com/",
        ]
        plan["note"] = (
            "The daily message-equivalent ranges are secondary observations layered on Devin's official work-based daily/weekly structure. They are useful for workload planning but cannot be converted to raw model tokens without Devin's action weights."
        )
        _finish(
            plan,
            comparison="managed",
            status="official-mechanics-secondary-message-range",
            confidence="secondary",
            missing=[
                "absolute weekly work-unit pool",
                "agent-action deduction formula",
                "model and token composition per message-equivalent",
            ],
            rankable=False,
        )


def _tabnine(plans: list[dict[str, Any]]) -> None:
    plan_by_id = _by_id(plans)
    for plan_id in ("tabnine-code-assistant", "tabnine-agentic-platform"):
        plan = plan_by_id.get(plan_id)
        if not plan:
            continue
        plan["models"] = []
        plan["allowance"] = {
            "kind": "platformCredits",
            "byokUsage": "unlimited at no Tabnine token charge",
            "tabnineProvidedLlmBilling": "underlying provider price plus 5% handling fee",
            "reservedTokenQuota": "purchased separately",
        }
        plan["source"] = "https://www.tabnine.com/pricing/"
        plan["note"] = (
            "The seat price buys the coding platform, governance, and agent features. BYOK inference is unlimited at no Tabnine token charge; Tabnine-hosted models are a separate provider-price-plus-5% purchase rather than a hidden included pool."
        )
        _finish(
            plan,
            comparison="managed",
            status="official-platform-plus-byok",
            confidence="official",
            missing=["price and size of any separately negotiated reserved Tabnine-hosted model quota"],
            rankable=False,
        )

    _append_plan(
        plans,
        id="tabnine-headless-business",
        provider="Tabnine",
        plan="Headless Agents Business",
        price=1200,
        allowance={
            "kind": "managedTokens",
            "monthlyProcessingTokens": 5_000_000_000,
            "platformUsdPerMillionProcessingTokens": 0.24,
            "underlyingLlmCostIncluded": False,
            "billingCommitment": "annual subscription",
        },
        source="https://www.tabnine.com/headless-agent-pricing/",
        note="Up to 5B processing tokens/month for autonomous CI/CD agents; the customer pays the selected LLM provider separately.",
        comparison="managed",
        status="official-processing-token-capacity",
        missing=["input/output/cache definition of a processing token", "underlying selected-model bill"],
    )
    _append_plan(
        plans,
        id="tabnine-headless-enterprise",
        provider="Tabnine",
        plan="Headless Agents Enterprise",
        price=5000,
        allowance={
            "kind": "managedTokens",
            "monthlyProcessingTokens": 50_000_000_000,
            "platformUsdPerMillionProcessingTokens": 0.10,
            "underlyingLlmCostIncluded": False,
            "billingCommitment": "annual subscription",
        },
        source="https://www.tabnine.com/headless-agent-pricing/",
        note="Up to 50B processing tokens/month for multi-pipeline autonomous agents; the customer pays the selected LLM provider separately.",
        comparison="managed",
        status="official-processing-token-capacity",
        missing=["input/output/cache definition of a processing token", "underlying selected-model bill"],
    )


def apply_inferred_subscriptions(plans: list[dict[str, Any]], models: dict[str, dict[str, Any]],
                                 open_catalog: list[str], top_catalog: list[str]) -> None:
    _cursor(plans)
    _claude(plans)
    _kimi(plans, models)
    _factory(plans, models)
    _ollama(plans, models)
    _antigravity(plans, models)
    _byteplus(plans, models)
    _grok(plans)
    _cline(plans, open_catalog)
    _devin(plans)
    _tabnine(plans)
    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
