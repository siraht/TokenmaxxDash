#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plans = json.loads((ROOT / "src" / "data" / "plans.json").read_text(encoding="utf-8"))
sources = json.loads((ROOT / "src" / "data" / "sources.json").read_text(encoding="utf-8"))
models = json.loads((ROOT / "src" / "data" / "models.json").read_text(encoding="utf-8"))
benchmarks = json.loads((ROOT / "src" / "data" / "benchmarks.json").read_text(encoding="utf-8"))

by_provider: dict[str, list[dict]] = defaultdict(list)
for plan in plans:
    by_provider[plan["provider"]].append(plan)

lines = [
    "# Plan coverage — 18 August 2026",
    "",
    "This generated inventory separates official exact/derived formulas, measured ranges, partial calculations, secondary-source claims, and provider-hidden numerical pools. A completed provider-hidden record is not treated as a zero allowance and cannot enter a quantified-value ranking.",
    "",
    "| Provider or product family | Tiers | Exact/derived | Measured range | Partial | Secondary | Provider-hidden | Direct benchmark routes | Regions |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---|",
]
for provider in sorted(by_provider, key=str.casefold):
    rows = by_provider[provider]
    counts = Counter(row["calculationStatus"] for row in rows)
    exact_derived = counts["exact"] + counts["derived"]
    regions = ", ".join(sorted({row["region"] for row in rows}))
    direct = sum(1 for row in rows if row.get("benchmarkCoverage") in {"direct-agent-and-model", "direct-agent", "direct-model"})
    lines.append(
        f"| {provider} | {len(rows)} | {exact_derived} | {counts['measured-range']} | {counts['partial']} | {counts['secondary']} | {counts['provider-hidden']} | {direct} | {regions} |"
    )

coverage = Counter(model["benchmarkCoverage"] for model in models)
lines += [
    "",
    "## Totals",
    "",
    f"- Plan tiers: **{len(plans)}**",
    f"- Providers or product families: **{len(by_provider)}**",
    f"- Advertised model labels: **{len(models)}**",
    f"- Model labels with direct external evidence: **{sum(1 for model in models if model['rankingEligible'])}**",
    f"- Direct model + native-agent labels: **{coverage['direct-agent-and-model']}**",
    f"- External benchmark rows: **{len(benchmarks)}**",
    f"- Source records: **{len(sources)}**",
    f"- Official source records: **{sum(1 for source in sources if source['type'] == 'official')}**",
    f"- External benchmark sources: **{sum(1 for source in sources if source['type'] == 'external-benchmark')}**",
    f"- Community measurements: **{sum(1 for source in sources if source['type'] == 'measurement')}**",
    f"- Secondary discovery sources: **{sum(1 for source in sources if source['type'] == 'secondary')}**",
    "",
    "The machine-readable authorities are `src/data/plans.json`, `src/data/models.json`, and `src/data/benchmarks.json`; this file is an audit-friendly generated view.",
]

out = ROOT / "docs" / "PLAN_COVERAGE.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out}")
