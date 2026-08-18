# TokenmaxxDash

Tokenmaxx is an evidence-backed Astro dashboard for comparing AI coding subscriptions by the things that produce useful work: **external model intelligence**, **native coding-agent performance**, **API cost per benchmark task**, **subscription cost per expected benchmark-equivalent pass**, sustained allowance, latency, model access, policy eligibility, and evidence confidence.

Raw tokens and advertised credit multiples remain available, but they are deliberately not the default ranking. A huge pool of a weak model cannot displace a smaller pool of a substantially stronger model merely because the token count is larger.

## Current snapshot

As of **18 August 2026**, the generated dataset contains:

- **219 subscription tiers** across **69 providers or product families**.
- **77 advertised model labels**, each with a direct external match or an explicit exclusion reason.
- **83 external benchmark rows** from publisher-owned model and coding-agent sources, including CursorBench 3.2.
- **293 plan/model access routes** with route version, access mode, transfer confidence, quality band, and plan evidence.
- **68 native subscription-task estimates** where an exact externally tested agent/model route can be joined to a defensible plan denominator.
- **Claude Fable 5** as a first-class model, Claude Code agent route, Terminal-Bench route, four CursorBench effort levels, and Max-plan access route.
- **Claude Code Pro, Max 5×, and Max 20×** measured raw-token ranges, API-equivalent ranges, and per-model/per-token-category subscription-cost estimates.
- Separate Pareto fronts for budget, passing-work throughput, API cost per expected pass, model price per intelligence point, speed, evidence-adjusted capacity, access price, and raw subsidy.

The dashboard imports Artificial Analysis model and Coding Agent Index results, Terminal-Bench 2.1, and CursorBench 3.2. It uses **external benchmarks only**. It does not currently run a private benchmark suite, simulate user workloads, or collect community telemetry. The repository includes a future community contribution schema and local JSON builder, but submitted results are not yet ingested.

## What changed from the allowance-only version

The default comparison now requires a direct external model-intelligence score of **60 or higher**. Subscription task fronts additionally require a native external coding-agent result and a directly matched included plan route.

This changes the market picture:

- **Claude Code and Codex both appear on quality-gated subscription fronts**.
- **Fable 5 remains visible even when Opus or Sol dominates it on a particular Pareto axis**.
- **StepFun remains a raw-subsidy leader**, but it no longer controls the default recommendation surface when its model score falls below the quality floor.
- Provider-specific Pareto fronts show the best configurations inside each native coding product, so one globally dominant vendor does not erase every alternative.

## Claude Code inference

Anthropic does not publish absolute subscription token pools, so Tokenmaxx stores two measured denominators rather than inventing an official quota:

| Plan | Estimated mixed raw tokens/week | Average mixed raw tokens/month | Full-utilization subscription cost per 1M raw tokens |
|---|---:|---:|---:|
| Pro | 0.20–0.28B | 0.87–1.22B | $0.01643–$0.02300 |
| Max 5× | 1.00–1.40B | 4.35–6.09B | $0.01643–$0.02300 |
| Max 20× | 4.00–5.60B | 17.39–24.35B | $0.00821–$0.01150 |

Each Claude plan page also calculates pure-category counterfactuals for Opus 5, Fable 5, Sonnet 5, and Haiku 4.5 across fresh input, cache reads, five-minute cache writes, one-hour cache writes, and output. These use the measured API-equivalent plan range and current public API rates.

Fable 5 is **PAYG-only on Pro**. It is included on Max but limited to **50% of the shared weekly meter** and consumes the meter faster; because Anthropic does not publish that multiplier, Tokenmaxx does not fabricate a raw Fable token allowance.

See [Claude Code inference](docs/CLAUDE_INFERENCE.md) for the formulas, measurements, caveats, and update rules.

## Run locally

Astro 7 requires Node.js 22.12 or newer.

```bash
nvm use
npm install --no-audit --no-fund
npm run refresh:data
npm run check:data
npm run dev
```

Build the static Astro site:

```bash
npm run build
```

The output is written to `dist/`.

## Publish on Cloudflare Pages

Create a Cloudflare Pages project from this repository with:

```text
Framework preset: Astro
Build command: npm run build
Build output directory: dist
Root directory: /
Node version: 22.12.0 or newer
```

The project is fully static, so no Cloudflare adapter is required. `wrangler.jsonc` and `public/_headers` are included for manual direct deployment.

**GitHub Actions is intentionally disabled.** There are no executable workflow files under `.github/workflows`, and this repository must remain that way until automation is explicitly enabled later. Current refresh and deployment commands are manual.

## Data pipeline

The canonical evidence and calculation logic live in `scripts/build_data.py`, `scripts/complete_data.py`, and `scripts/augment_external_benchmarks.py`. `npm run prepare:data` deterministically regenerates the gitignored `src/data/` build inputs and mirrors them into gitignored `public/data/` JSON endpoints before local development or production builds:

```text
plans.json
models.json
benchmarks.json
quality-routes.json
subscription-task-estimates.json
leaders.json
sources.json
summary.json
methodology.json
candidates.json
```

Regenerate them with:

```bash
npm run refresh:data
python3 scripts/build_coverage.py
npm run check:data
```

The pipeline is split into three stages:

1. `scripts/build_data.py` creates the broad plan catalog and provider-specific base calculations.
2. `scripts/complete_data.py` adds current external model and agent evidence, Claude inference, exact route semantics, task economics, confidence adjustments, and Pareto fronts.
3. `scripts/augment_external_benchmarks.py` imports publisher-owned benchmark tables whose cadence is independent of plan normalization, currently CursorBench 3.2.

## Validation

```bash
npm run verify
```

The validators check cross-file IDs, source provenance, status semantics, model-route completeness, benchmark-derived metrics, task-estimate ranges, Fable access behavior, all three Claude plan estimates, every CursorBench cost/pass calculation, public-data mirrors, and the absence of active GitHub Actions workflows.

## Evidence refresh

The source registry can be checked without mutating published data:

```bash
python3 scripts/watch_sources.py --validate-only
```

A manual source refresh can fingerprint and snapshot monitored pages:

```bash
python3 scripts/watch_sources.py --write-state --save-snapshots
```

Detected changes create review inputs only. They do not silently rewrite plan values, model matches, or benchmark scores.

## Methodology and contribution design

- [Data model](docs/DATA_MODEL.md)
- [Claude Code inference](docs/CLAUDE_INFERENCE.md)
- [Pareto methodology](docs/PARETO_METHODOLOGY.md)
- [Plan coverage](docs/PLAN_COVERAGE.md)
- [Research findings](docs/RESEARCH_FINDINGS.md)
- [Future community benchmark contributions](docs/COMMUNITY_BENCHMARKS.md)

## License

MIT. Source-page content and benchmark values remain subject to their publishers’ terms and licenses.
