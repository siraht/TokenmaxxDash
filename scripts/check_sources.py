#!/usr/bin/env python3
"""Lightweight source checks before Astro's compiler runs in Cloudflare."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
astro_files = sorted((ROOT / "src").rglob("*.astro"))
import_re = re.compile(r"^import\s+.+?\s+from\s+['\"]([^'\"]+)['\"];?\s*$", re.MULTILINE)

for path in astro_files:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append(f"{path.relative_to(ROOT)}: malformed Astro frontmatter")
        continue
    frontmatter = text[4:text.find("\n---\n", 4)]
    for specifier in import_re.findall(frontmatter):
        if not specifier.startswith("."):
            continue
        target = (path.parent / specifier).resolve()
        candidates = [target]
        if not target.suffix:
            candidates.extend(target.with_suffix(ext) for ext in (".astro", ".ts", ".js", ".json"))
        if not any(candidate.exists() for candidate in candidates):
            errors.append(f"{path.relative_to(ROOT)}: missing import {specifier}")

required = [
    "src/pages/index.astro",
    "src/pages/plans/index.astro",
    "src/pages/plans/[id].astro",
    "src/pages/models.astro",
    "src/pages/benchmarks.astro",
    "src/pages/leaders.astro",
    "src/pages/methodology.astro",
]
for relative in required:
    if not (ROOT / relative).exists():
        errors.append(f"missing required page: {relative}")

index = (ROOT / "src/pages/index.astro").read_text(encoding="utf-8")
for phrase in ("Route billed $ / 1M", "Coding score", "Include owned plans"):
    if phrase not in index:
        errors.append(f"homepage missing primary buying field: {phrase}")

for stale in ("Codex vs Claude", "No arbitrary master score", "quality-gated Pareto"):
    for path in (ROOT / "src").rglob("*"):
        if path.is_file() and stale.lower() in path.read_text(encoding="utf-8", errors="ignore").lower():
            errors.append(f"{path.relative_to(ROOT)}: stale comparison framing {stale!r}")

workflow_dir = ROOT / ".github" / "workflows"
if workflow_dir.exists() and any(path.suffix.lower() in {".yml", ".yaml"} for path in workflow_dir.iterdir()):
    errors.append("active GitHub Actions workflow found")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Checked {len(astro_files)} Astro files, imports, core buying fields, stale framing, and zero active Actions workflows.")
