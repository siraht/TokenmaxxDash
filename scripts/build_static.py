#!/usr/bin/env python3
"""Execute the reviewable source fragments for build_static.py.

The implementation is split only to keep GitHub connector commits reviewable.
Run ``python3 scripts/materialize_sources.py`` to reconstruct monolithic files
under ``.materialized-sources/`` for local editing or diffing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "public").mkdir(exist_ok=True)
(ROOT / "public" / "global.css").write_text((ROOT / "src" / "styles" / "global.css").read_text())

_parts = Path(__file__).with_name("build_static_parts")
_source = "".join(path.read_text() for path in sorted(_parts.glob("*.py.part")))
exec(compile(_source, str(_parts), "exec"), {"__name__": "__main__", "__file__": __file__})
