#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plans = json.loads((ROOT / "src" / "data" / "plans.json").read_text(encoding="utf-8"))
sources = json.loads((ROOT / "src" / "data" / "sources.json").read_text(encoding="utf-8"))
models = json.loads((ROOT / "src" / "data" / "models.json").read_text(encoding="utf-8"))

by_provider: dict[str, list[dict]] = defaultdict(list)
for plan in plans:
    by_provider[plan["provider"]].append(plan)

lines = [
    "# Plan coverage — 17 August 2026",
    "",
    "This generated inventory shows the evidence state for each product family. `Exact/derived` means the displayed denominator is calculable; it does not imply that every provider uses the same economic unit. `Provider-hidden` means the missing numerical pool has been identified and is intentionally not guessed.",
    "",
    "| Provider or product family | Tiers | Exact/derived | Measured range | Partial | Secondary | Provider-hidden | Regions |",
    "|---|---:|---:|---:|---:|---:|---:|---|",
]
for provider in sorted(by_provider, key=str.casefold):
    rows = by_provider[provider]
    counts = Counter(row["calculationStatus"] for row in rows)
    exact_derived = counts["exact"] + counts["derived"]
    regions = ", ".join(sorted({row["region"] for row in rows}))
    lines.append(
        f"| {provider} | {len(rows)} | {exact_derived} | {counts['measured-range']} | {counts['partial']} | {counts['secondary']} | {counts['provider-hidden']} | {regions} |"
    )

coverage = Counter(row["benchmarkCoverage"] for row in models)
lines += [
    "",
    "## Totals",
    "",
    f"- Plan tiers: **{len(plans)}**",
    f"- Providers or product families: **{len(by_provider)}**",
    f"- Advertised model routes: **{len(models)}**",
    f"- Model routes with direct agent and model evidence: **{coverage['direct-agent-and-model']}**",
    f"- Model routes with direct model-only evidence: **{coverage['direct-model']}**",
    f"- Model routes with direct agent-only evidence: **{coverage['direct-agent']}**",
    f"- Model routes without a direct imported benchmark: **{coverage['no-external-benchmark']}**",
    f"- Broad catalog or managed-agent labels: **{coverage['catalog-only']}**",
    f"- Source records: **{len(sources)}**",
    f"- Official source records: **{sum(1 for source in sources if source['type'] == 'official')}**",
    f"- External benchmark sources: **{sum(1 for source in sources if source['type'] == 'external-benchmark')}**",
    f"- Community measurements: **{sum(1 for source in sources if source['type'] == 'measurement')}**",
    f"- Secondary discovery sources: **{sum(1 for source in sources if source['type'] == 'secondary')}**",
    "",
    "The machine-readable authorities are `src/data/plans.json` and `src/data/models.json`; this file is an audit-friendly generated view.",
]

out = ROOT / "docs" / "PLAN_COVERAGE.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out}")
