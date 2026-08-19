"""Official native-unit updates for Amazon Q, Ollama Cloud, and Devin."""
from __future__ import annotations

from typing import Any


def _remove_provider(plans: list[dict[str, Any]], names: set[str]) -> None:
    plans[:] = [plan for plan in plans if plan["provider"] not in names]


def apply_service_updates(plans: list[dict[str, Any]]) -> None:
    _remove_provider(plans, {"Amazon Q", "Amazon Q Developer"})
    plans.append({
        "id": "amazon-q-pro", "provider": "Amazon Q Developer", "plan": "Pro",
        "priceUsd": 19.0, "models": [],
        "allowance": {
            "kind": "requestWindow",
            "monthlyInferenceCalls": 10_000,
            "approxMonthlyUserInputs": 1_000,
            "monthlyTransformationLines": 4_000,
            "codeCatalystDevelopmentTasks": 30,
            "codeCatalystPullRequestSummaries": 20,
        },
        "source": "https://docs.aws.amazon.com/general/latest/gr/amazonqdev.html",
        "confidence": "official", "owned": False, "windows": "Monthly per-user inference-call quota",
        "policy": "IDE, CLI, Kiro, and AWS development workflows",
        "note": "AWS publishes 10,000 agentic inference calls—roughly 1,000 user requests—per user/month. The routed Claude model and tokens per user request are not fixed.",
        "currency": "USD", "originalPrice": 19.0, "routeRates": {}, "monthlyUsdByModel": {},
        "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
        "comparisonClass": "managed",
        "missingFields": ["exact routed Claude checkpoint per request", "tokens per inference call and per user input"],
        "researchStatus": "quantified-managed", "sourceType": "primary-or-measured", "rankable": False,
    })

    _remove_provider(plans, {"Ollama", "Ollama Cloud"})
    plans.extend([
        {
            "id": "ollama-cloud-pro", "provider": "Ollama Cloud", "plan": "Pro",
            "priceUsd": 20.0, "models": [],
            "allowance": {"kind": "relative", "relativeToFree": 50.0, "concurrentCloudModels": 3,
                          "windows": ["five-hour", "weekly"], "usageLevels": [1, 2, 3, 4]},
            "source": "https://ollama.com/pricing", "confidence": "official", "owned": False,
            "windows": "Five-hour session and seven-day weekly limits; usage weighted by model and input/cache/output tokens",
            "policy": "personal cloud models and coding automation",
            "note": "Pro includes 50× Free cloud usage and three concurrent cloud models, but Ollama does not publish the absolute Free pool.",
            "currency": "USD", "originalPrice": 20.0, "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "relative",
            "missingFields": ["absolute Free five-hour pool", "absolute Free weekly pool", "numerical model usage-level weights"],
            "researchStatus": "official-relative", "sourceType": "primary-or-measured", "rankable": False,
        },
        {
            "id": "ollama-cloud-max", "provider": "Ollama Cloud", "plan": "Max",
            "priceUsd": 100.0, "models": [],
            "allowance": {"kind": "relative", "relativeToPro": 5.0, "relativeToFree": 250.0,
                          "concurrentCloudModels": 10, "windows": ["five-hour", "weekly"],
                          "newSignupsPaused": True, "usageLevels": [1, 2, 3, 4]},
            "source": "https://ollama.com/pricing", "confidence": "official", "owned": False,
            "windows": "Five-hour session and seven-day weekly limits; new Max sign-ups currently paused",
            "policy": "personal heavy and sustained cloud-model usage",
            "note": "Max includes five times Pro usage and ten concurrent cloud models. Existing subscribers retain the plan, while new sign-ups are paused.",
            "currency": "USD", "originalPrice": 100.0, "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "relative",
            "missingFields": ["absolute Pro five-hour pool", "absolute Pro weekly pool", "numerical model usage-level weights"],
            "researchStatus": "official-relative-paused", "sourceType": "primary-or-measured", "rankable": False,
        },
        {
            "id": "ollama-cloud-team", "provider": "Ollama Cloud", "plan": "Team",
            "priceUsd": 25.0, "models": [],
            "allowance": {"kind": "hidden", "perSeat": True, "minimumSeats": 5,
                          "minimumMonthlySeatChargeUsd": 125, "extraUsage": "shared PAYG team balance"},
            "source": "https://ollama.com/pricing", "confidence": "official-partial", "owned": False,
            "windows": "Per-seat included usage, followed by a shared team extra-usage balance",
            "policy": "team cloud models, administration, and zero-retention hosting",
            "note": "$25 per seat with a five-seat minimum. Ollama publishes that usage is included but not the absolute per-seat pool.",
            "currency": "USD", "originalPrice": 25.0, "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "provider-hidden",
            "missingFields": ["absolute included usage per team seat", "model-specific deduction weights"],
            "researchStatus": "provider-hidden", "sourceType": "primary-or-measured", "rankable": False,
        },
    ])

    # Preserve the individual Devin plans while replacing vague missing-data
    # labels with the exact known quota structure.
    for plan in plans:
        if plan["provider"] not in {"Devin", "Devin Desktop"}:
            continue
        if plan["plan"] == "Pro":
            plan["allowance"] = {"kind": "hidden", "dailyQuota": True, "weeklyQuota": True,
                                 "sharedSurfaces": ["Devin sessions", "Devin for Terminal", "Windsurf IDE"],
                                 "onDemandCreditsAfterQuota": True}
            plan["comparisonClass"] = "provider-hidden"
            plan["researchStatus"] = "provider-hidden"
            plan["missingFields"] = ["absolute daily quota", "absolute weekly quota", "usage-unit deduction formula"]
            plan["source"] = "https://docs.devin.ai/admin/billing/self-serve"
        elif plan["plan"] == "Max":
            plan["allowance"] = {"kind": "relative", "largerThanPro": True, "dailyCap": False,
                                 "weeklyQuota": True,
                                 "sharedSurfaces": ["Devin sessions", "Devin for Terminal", "Windsurf IDE"]}
            plan["comparisonClass"] = "relative"
            plan["researchStatus"] = "official-relative"
            plan["missingFields"] = ["absolute Max weekly quota", "numeric Max-to-Pro multiplier", "usage-unit deduction formula"]
            plan["source"] = "https://docs.devin.ai/admin/billing/self-serve"

    if not any(plan["id"] == "devin-teams-full-seat" for plan in plans):
        plans.append({
            "id": "devin-teams-full-seat", "provider": "Devin", "plan": "Teams Full Seat",
            "priceUsd": 40.0, "models": [],
            "allowance": {"kind": "relative", "relativeToDevinPro": 1.0, "dailyQuota": True,
                          "weeklyQuota": True, "accountMinimumUsd": 80, "unlimitedFlexSeats": True},
            "source": "https://docs.devin.ai/admin/billing/self-serve", "confidence": "official",
            "owned": False, "windows": "Daily and weekly quota equivalent to Devin Pro",
            "policy": "team managed coding agent and Windsurf",
            "note": "$40 per full seat, with an $80 account minimum; flex seats are free and use shared on-demand credits.",
            "currency": "USD", "originalPrice": 40.0, "routeRates": {}, "monthlyUsdByModel": {},
            "routeNotes": {}, "modelAllowanceFraction": {}, "accessByModel": {}, "supplemental": False,
            "comparisonClass": "relative",
            "missingFields": ["absolute Devin Pro daily quota", "absolute Devin Pro weekly quota", "usage-unit deduction formula"],
            "researchStatus": "official-relative", "sourceType": "primary-or-measured", "rankable": False,
        })

    plans.sort(key=lambda plan: (plan["provider"].lower(), plan["priceUsd"], plan["plan"].lower()))
