#!/usr/bin/env python3
"""Reconstruct monolithic generator sources from reviewable fragments."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / ".materialized-sources"
DESTINATION.mkdir(parents=True, exist_ok=True)

for name in ("build_data", "enrich_data", "complete_data"):
    parts = ROOT / "scripts" / f"{name}_parts"
    if not parts.exists():
        continue
    source = "".join(path.read_text() for path in sorted(parts.glob("*.py.part")))
    destination = DESTINATION / f"{name}.py"
    destination.write_text(source)
    print(f"Materialized {destination.relative_to(ROOT)} from {len(list(parts.glob('*.py.part')))} fragments")
