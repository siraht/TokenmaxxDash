# Plan and model coverage — 18 August 2026

Tokenmaxx currently catalogs **219 subscription tiers across 69 providers or product families**. Every plan receives an evidence status, every advertised model label receives a benchmark-coverage status, and provider-hidden quantities stay explicit rather than becoming zeroes or guessed values.

## Plan calculation coverage

| Evidence class | Plan tiers | Meaning |
|---|---:|---|
| Official exact | 50 | The provider publishes enough numerical allowance and deduction information for a direct calculation. |
| Evidence-derived | 28 | An official formula is combined with an official worked example or a measured hidden variable. |
| Measured range | 3 | Claude Pro, Max 5×, and Max 20× use externally observable raw-token and API-equivalent intervals. |
| Partial | 17 | Some arithmetic is exact, but at least one binding pool, multiplier, or work-unit conversion remains hidden. |
| Secondary-source | 97 | Current plan values rely materially on a comparison tracker pending primary confirmation. |
| Provider-hidden | 24 | The plan exists, but the provider withholds the numerical denominator needed for a defensible allowance calculation. |

A **provider-hidden** record is complete as an evidence record: it identifies the missing field and remains excluded from quantified-value rankings. It is not treated as an unresolved zero.

## Model-route coverage

The catalog contains **77 advertised model labels** across **293 plan/model routes**.

| Benchmark coverage | Model labels | Ranking behavior |
|---|---:|---|
| Direct model and native-agent evidence | 6 | Eligible for model and native subscription-task comparisons when plan access is included and the allowance denominator is known. |
| Direct model evidence | 28 | Eligible for model intelligence, price/intelligence, speed, and quality-gated plan-route comparisons. |
| Direct native-agent evidence only | 1 | Eligible only on the directly tested agent scale. |
| No exact external benchmark | 27 | Searchable, but excluded from intelligence rankings. |
| Broad catalog or family label | 15 | Searchable catalog access; no score is inherited from the strongest member. |

That produces **35 model labels with direct external evidence** and **42 explicit exclusions**. The exclusions are mainly broad catalogs, ambiguous aliases, managed-agent products, legacy routes, newly released models, and checkpoints without an imported external result.

## Directly benchmarked subscription families

Current plan-level direct benchmark coverage is concentrated in:

- **OpenAI Codex:** 5 plan tiers with direct Sol, Terra, or Luna evidence.
- **Claude Code:** Pro, Max 5×, and Max 20× with direct Opus/Fable model and Claude Code evidence.
- **Kimi Code:** 4 tiers with direct Kimi model or Kimi Code CLI evidence.
- **Cursor:** 3 tiers with direct Composer/Grok or Cursor Agent evidence, while the first-party subscription pool remains partially hidden.
- **StepFun:** 8 tiers with direct Step model evidence, but current Step intelligence falls below the default frontier-quality gate.

Other providers can still have exact allowance arithmetic without a directly benchmarked current model route, or direct model evidence without enough allowance information for subscription task economics.

## External evidence inventory

- **83 external benchmark rows** across Artificial Analysis, Terminal-Bench 2.1, and CursorBench 3.2.
- **94 source records**: 40 official sources, 40 external benchmark sources, 8 community measurements, 5 secondary discovery sources, and 1 methodology source.
- **68 native subscription-task estimates** where an exact externally tested agent/model route can be joined to included access and a defensible plan denominator.
- **Eight Fable-specific benchmark rows** spanning model intelligence, Claude Code, Terminal-Bench, and four CursorBench effort levels.

## What remains provider-hidden

The largest unresolved numerical denominators include Claude’s absolute meter weights, Cursor’s first-party model pool, MiniMax’s included bars, Kimi’s absolute shared token pool, Google and xAI shared-compute pools, and managed-product work-unit conversions. These cannot be completed by token-price arithmetic alone.

The machine-readable authorities are generated at build time as:

```text
src/data/plans.json
src/data/models.json
src/data/benchmarks.json
src/data/quality-routes.json
src/data/subscription-task-estimates.json
src/data/leaders.json
```

Run `python3 scripts/build_coverage.py` after `npm run refresh:data` to regenerate the full provider-by-provider audit table locally.
