# Quality-adjusted Pareto methodology

Tokenmaxx does not publish one master score. It calculates several non-dominated sets because monthly price, model intelligence, native-agent pass rate, API cost per task, sustained allowance, latency, and evidence confidence are semantically different quantities.

## Default quality gate

The default plan/model surface requires a directly matched external **model Intelligence Index of at least 60**. Native subscription-task surfaces require a directly matched external coding-agent result at score 60 or higher.

Lower-scoring models remain available in the `capable` and `volume` fronts. They simply cannot dominate the default frontier by offering an enormous low-cost token pool.

## Native subscription-task front

A route is eligible only when all of these are known:

```text
subscription plan
included model access mode
exact externally tested native harness
exact model or defensible route match
API-priced benchmark cost per task
benchmark pass-rate-like score
defensible included subscription denominator
```

Two fronts are calculated:

### Budget front

Maximize quality while minimizing:

```text
monthly subscription price
conservative subscription USD per expected pass
```

This preserves smaller plans that are cheaper to enter even when a $200 tier has superior unit economics.

### Throughput front

Maximize:

```text
conservative expected passes per average month
agent score
```

while minimizing conservative subscription cost per expected pass. This surface favors sustained passing-work output and often selects larger tiers.

## Provider-specific fronts

A global Pareto front can legitimately contain mostly one product. That result should not erase the best available configuration inside every other product family. Tokenmaxx therefore recalculates the same frontier independently for Claude Code, Codex, Cursor, and future native products with sufficient evidence.

Provider-specific membership is not a claim that a row is globally non-dominated. It answers, “what are the non-dominated choices if I have already chosen this native product?”

## External agent cost-quality front

```text
API_USD_per_expected_pass = API_cost_per_task / (agent_score / 100)
```

This front measures the external benchmark’s provider-priced economics. It does not use subscription prices or inferred plan pools.

## Model price-intelligence front

```text
blended_USD_per_M = 0.70 × cache_read + 0.20 × fresh_input + 0.10 × output
blended_USD_per_intelligence_point = blended_USD_per_M / Intelligence_Index
```

Rows with unknown or placeholder zero pricing are excluded. Speed is calculated on a separate frontier because cheap and fast are independent advantages.

## Evidence-adjusted capacity

For routes with a quantified plan-value lower bound:

```text
quality_capacity = conservative_plan_value_multiple × normalized_intelligence

evidence_adjusted_quality_capacity = quality_capacity × evidence_confidence_factor
```

This is a secondary heuristic, not a task-success estimate. It exists to prevent a weakly measured allowance from appearing identical to an official exact allowance. The unadjusted values remain visible.

## Fable visibility

Fable 5 may be dominated by Opus 5 or a Codex configuration on a selected global axis. It remains visible in:

- the model registry;
- external model and agent benchmark tables;
- Terminal-Bench;
- Claude Max plan routes;
- Fable-specific subscription task estimates;
- Claude model/category token-economics tables.

Pareto membership controls a leader table, not whether evidence is shown.

## Raw subsidy

Raw plan-value multiples are published in an appendix and on plan pages. They never enter the default recommendation surface without a directly benchmarked model route that passes the selected intelligence floor.
