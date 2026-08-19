"""Normalize app-builder credit fields missed by the generic broad-plan adapter."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def apply_builder_units(plans: list[dict[str, Any]], data_dir: Path) -> None:
    try:
        broad = json.loads((data_dir / "plans.json").read_text())
    except (OSError, json.JSONDecodeError):
        return
    broad_by_key = {(row.get("provider"), row.get("name")): row for row in broad}

    for plan in plans:
        broad_row = broad_by_key.get((plan["provider"], plan["plan"]))
        if not broad_row:
            continue
        quotas = broad_row.get("quotas") or {}
        if plan["provider"] == "Base44" and isinstance(quotas.get("monthlyMessageCredits"), (int, float)):
            plan["allowance"] = {
                "kind": "segmentedPools",
                "monthlyMessageCredits": quotas["monthlyMessageCredits"],
                "monthlyIntegrationCredits": quotas.get("monthlyIntegrationCredits", 0),
                "poolsFungible": False,
            }
            plan["comparisonClass"] = "managed"
            plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "quantified-managed"
            plan["missingFields"] = ["model-token conversion for message credits",
                                     "integration-action conversion for integration credits"]
            plan["rankable"] = False
            plan["note"] = "Message and integration credits are separate product units and cannot be added together or converted to model tokens without Base44's internal deduction table."
        elif plan["provider"] == "a0.dev" and isinstance(quotas.get("monthlyBuildCredits"), (int, float)):
            plan["allowance"] = {"kind": "workUnits", "monthlyBuildCredits": quotas["monthlyBuildCredits"]}
            plan["comparisonClass"] = "managed"
            plan["researchStatus"] = "secondary-native-unit" if plan.get("confidence") == "secondary" else "quantified-managed"
            plan["missingFields"] = ["model-token conversion per build credit",
                                     "externally comparable work completed per build credit"]
            plan["rankable"] = False
            plan["note"] = "Build credits measure managed app-building work rather than a fixed number of model tokens."
