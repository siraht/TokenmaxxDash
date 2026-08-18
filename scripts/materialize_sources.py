#!/usr/bin/env python3
"""Reconstruct the three large generated-data programs from source fragments."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / ".materialized-sources"
OUT.mkdir(exist_ok=True)
for stem in ("build_data", "enrich_data", "build_static"):
    source = "".join(path.read_text() for path in sorted((ROOT / f"{stem}_parts").glob("*.py.part")))
    target = OUT / f"{stem}.py"
    target.write_text(source)
    print(target)
