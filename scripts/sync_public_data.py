#!/usr/bin/env python3
"""Copy canonical generated datasets into Astro's public directory before builds."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "data"
DESTINATION = ROOT / "public" / "data"
FILES = (
    "plans.json",
    "models.json",
    "benchmarks.json",
    "quality-routes.json",
    "subscription-task-estimates.json",
    "leaders.json",
    "sources.json",
    "summary.json",
    "methodology.json",
    "candidates.json",
)

DESTINATION.mkdir(parents=True, exist_ok=True)
for name in FILES:
    source = SOURCE / name
    if not source.exists():
        raise SystemExit(f"Missing canonical dataset: {source}")
    shutil.copyfile(source, DESTINATION / name)
print(f"Synced {len(FILES)} canonical datasets to {DESTINATION.relative_to(ROOT)}")
