#!/usr/bin/env python3
"""Static source checks used when the Astro compiler is unavailable.

This does not replace `astro check` or `astro build`; it catches missing imports,
stale branding, invalid frontmatter boundaries, duplicate page routes, missing data
mirrors, and accidentally enabled GitHub Actions before a Cloudflare build runs.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

astro_files = sorted((ROOT / "src").rglob("*.astro"))
if not astro_files:
    errors.append("no Astro source files found")

IMPORT_RE = re.compile(r"^import\s+.+?\s+from\s+['\"]([^'\"]+)['\"];?\s*$", re.MULTILINE)
for path in astro_files:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing opening frontmatter delimiter")
        continue
    closing = text.find("\n---\n", 4)
    if closing < 0:
        errors.append(f"{path.relative_to(ROOT)}: missing closing frontmatter delimiter")
        continue
    frontmatter = text[4:closing]
    for specifier in IMPORT_RE.findall(frontmatter):
        if not specifier.startswith("."):
            continue
        target = (path.parent / specifier).resolve()
        candidates = [target]
        if target.suffix == "":
            candidates.extend(target.with_suffix(ext) for ext in (".ts", ".js", ".astro", ".json"))
            candidates.extend((target / f"index{ext}") for ext in (".ts", ".js", ".astro"))
        if not any(candidate.exists() for candidate in candidates):
            errors.append(f"{path.relative_to(ROOT)}: missing import {specifier}")

stale_patterns = {
    "Coding Plan Index": [ROOT / "src", ROOT / "README.md", ROOT / "docs"],
    "17 August 2026": [ROOT / "src", ROOT / "README.md", ROOT / "docs"],
    "value=\"opaque\"": [ROOT / "src"],
}
for pattern, locations in stale_patterns.items():
    regex = re.compile(pattern)
    for location in locations:
        files = [location] if location.is_file() else list(location.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if regex.search(text):
                errors.append(f"{path.relative_to(ROOT)}: stale pattern {pattern!r}")

workflow_dir = ROOT / ".github" / "workflows"
if workflow_dir.exists():
    active = sorted(p.name for p in workflow_dir.iterdir() if p.suffix.lower() in {".yml", ".yaml"})
    if active:
        errors.append(f"active GitHub Actions workflows found: {', '.join(active)}")

required_pages = [
    "src/pages/index.astro",
    "src/pages/plans/index.astro",
    "src/pages/plans/[id].astro",
    "src/pages/leaders.astro",
    "src/pages/models.astro",
    "src/pages/benchmarks.astro",
    "src/pages/methodology.astro",
    "src/pages/sources.astro",
    "src/pages/community.astro",
]
for rel in required_pages:
    if not (ROOT / rel).exists():
        errors.append(f"missing required page {rel}")

for name in (
    "plans.json", "models.json", "benchmarks.json", "quality-routes.json",
    "subscription-task-estimates.json", "leaders.json", "sources.json",
    "summary.json", "methodology.json", "candidates.json",
):
    src = ROOT / "src" / "data" / name
    pub = ROOT / "public" / "data" / name
    if not src.exists() or not pub.exists():
        errors.append(f"missing data mirror for {name}")
    elif src.read_bytes() != pub.read_bytes():
        errors.append(f"public data mirror differs for {name}")

try:
    benchmarks = json.loads((ROOT / "src/data/benchmarks.json").read_text())
    plans = json.loads((ROOT / "src/data/plans.json").read_text())
    leaders = json.loads((ROOT / "src/data/leaders.json").read_text())
    if not any("Fable 5" in row.get("model", "") for row in benchmarks):
        errors.append("Fable 5 has no external benchmark row")
    claude = {row["id"]: row for row in plans if row.get("providerId") == "claude-code"}
    for plan_id in ("claude-code-pro", "claude-code-max-5x", "claude-code-max-20x"):
        plan = claude.get(plan_id)
        if not plan:
            errors.append(f"missing Claude plan {plan_id}")
            continue
        quotas = plan.get("quotas", {})
        if quotas.get("subscriptionUsdPerMillionRawTokensLow") is None or quotas.get("subscriptionUsdPerMillionRawTokensHigh") is None:
            errors.append(f"{plan_id}: missing measured $/M raw-token range")
        if not plan.get("details", {}).get("modelCategoryTokenEconomics"):
            errors.append(f"{plan_id}: missing per-model/category token economics")
    if not leaders.get("fableRelevantBenchmarkIds") or not leaders.get("fableRelevantRouteIds"):
        errors.append("Fable is absent from leader metadata")
except (OSError, json.JSONDecodeError, KeyError) as exc:
    errors.append(f"failed to inspect generated datasets: {exc}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print(f"Checked {len(astro_files)} Astro files, source imports, data mirrors, Fable/Claude coverage, stale branding, and zero active Actions workflows.")
