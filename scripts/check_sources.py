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
    if 'href="/docs/' in text or "href='/docs/" in text:
        errors.append(f"{path.relative_to(ROOT)}: repository docs link would 404 on the static deployment")
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

for relative in (
    "src/pages/index.astro", "src/pages/plans/index.astro", "src/pages/plans/[id].astro",
    "src/pages/models.astro", "src/pages/benchmarks.astro", "src/pages/methodology.astro",
):
    if not (ROOT / relative).exists():
        errors.append(f"missing required page: {relative}")
index = (ROOT / "src/pages/index.astro").read_text(encoding="utf-8")
for phrase in ("Subscription $/M", "Quality-adjusted $/M", "Hide plans I already own", "Claude, Codex, Grok, and Synthetic"):
    if phrase not in index:
        errors.append(f"homepage missing core comparison field: {phrase}")
for stale in ("Default view excludes", "Include owned plans", "Codex vs Claude"):
    for path in (ROOT / "src").rglob("*"):
        if path.is_file() and stale.lower() in path.read_text(encoding="utf-8", errors="ignore").lower():
            errors.append(f"{path.relative_to(ROOT)}: stale framing {stale!r}")
app = (ROOT / "public/app.js").read_text(encoding="utf-8")
if "if (raw == null || raw.trim() === '') return fallback;" not in app:
    errors.append("public/app.js: empty metric values must be treated as missing rather than zero")
workflow_dir = ROOT / ".github/workflows"
if workflow_dir.exists() and any(path.suffix.lower() in {".yml", ".yaml"} for path in workflow_dir.iterdir()):
    errors.append("active GitHub Actions workflow found")
if errors:
    raise SystemExit("\n".join(errors))
print(f"Checked {len(astro_files)} Astro files, imports, deploy-safe links, universal comparison fields, missing-value parsing, stale owned-plan framing, and zero active Actions workflows.")
