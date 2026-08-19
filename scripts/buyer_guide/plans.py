"""Execute reviewable source fragments for plans.py."""
from pathlib import Path

_parts = Path(__file__).with_name("plans_parts")
_source = "".join(path.read_text() for path in sorted(_parts.glob("*.py.part")))
exec(compile(_source, str(_parts), "exec"), globals())
