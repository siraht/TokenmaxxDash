#!/usr/bin/env python3
"""Execute the reviewable source fragments for complete_data.py.

The implementation is split into small text fragments so GitHub connector commits
remain reviewable. Run ``python3 scripts/materialize_sources.py`` to reconstruct
monolithic copies under ``.materialized-sources/`` for local editing or diffing.
"""
from pathlib import Path

_parts = Path(__file__).with_name("complete_data_parts")
_source = "".join(path.read_text() for path in sorted(_parts.glob("*.py.part")))
exec(compile(_source, str(_parts), "exec"), {"__name__": "__main__", "__file__": __file__})
