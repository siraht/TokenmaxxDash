"""Execute reviewable source fragments for build.py after extending model evidence."""
from pathlib import Path

from .models import MODELS, TASKS, TOP_CATALOG, OPEN_CATALOG
from .model_extensions import apply_model_extensions
from .dynamic_model_extensions import apply_dynamic_model_extensions

apply_model_extensions(MODELS, TASKS, TOP_CATALOG, OPEN_CATALOG)
apply_dynamic_model_extensions(MODELS, TOP_CATALOG)

_parts = Path(__file__).with_name("build_parts")
_source = "".join(path.read_text() for path in sorted(_parts.glob("*.py.part")))
exec(compile(_source, str(_parts), "exec"), globals())

# The fragment defines the stable calculator and main(). Replace only the
# dispatch function so newer measured denominators compose with old adapters.
from .capacity_extensions import wrap_compute_capacity
compute_capacity = wrap_compute_capacity(compute_capacity, MODELS, blend_rate)
