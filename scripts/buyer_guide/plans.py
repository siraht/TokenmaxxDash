"""Execute reviewable source fragments for plans.py, then apply verified enrichments."""
from pathlib import Path

_parts = Path(__file__).with_name("plans_parts")
_source = "".join(path.read_text() for path in sorted(_parts.glob("*.py.part")))
exec(compile(_source, str(_parts), "exec"), globals())

from .enrichment import apply_enrichment
from .native_units import apply_native_units
from .builder_units import apply_builder_units
from .corrections import apply_corrections
from .team_plans import apply_team_plans
from .team_extras import apply_team_extras
from .market_updates import apply_market_updates
from .energy_plans import apply_energy_plans
from .minimax_plans import apply_minimax_plans
from .service_updates import apply_service_updates
from .zencoder_plans import apply_zencoder_plans
from .work_credit_plans import apply_work_credit_plans
from .relative_plans import apply_relative_plans
from .inferred_subscriptions import apply_inferred_subscriptions

apply_enrichment(PLANS, MODELS, TOP_CATALOG, OPEN_CATALOG, DATA)
apply_native_units(PLANS, MODELS, DATA)
apply_builder_units(PLANS, DATA)
apply_corrections(PLANS, MODELS)
apply_team_plans(PLANS, TOP_CATALOG)
apply_team_extras(PLANS, TOP_CATALOG)
apply_market_updates(PLANS, MODELS)
apply_energy_plans(PLANS, MODELS)
apply_minimax_plans(PLANS, MODELS)
apply_service_updates(PLANS)
apply_zencoder_plans(PLANS, MODELS)
apply_work_credit_plans(PLANS)
apply_relative_plans(PLANS)
apply_inferred_subscriptions(PLANS, MODELS, OPEN_CATALOG, TOP_CATALOG)
