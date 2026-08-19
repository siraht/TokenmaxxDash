# TokenmaxxDash

Tokenmaxx answers one practical question:

> **Which monthly AI coding subscription buys the most useful model capacity for the money?**

The primary comparison unit is a **subscription × model route**. For every route with enough evidence, the dashboard calculates:

- model-specific included monthly value or token allowance;
- effective raw tokens per month under selectable token mixes;
- subscription dollars per million raw tokens;
- external model intelligence and coding-task performance;
- quality-adjusted subscription dollars per million tokens;
- external API cost per benchmark task and per expected success;
- subscription cost per benchmark-equivalent successful task;
- five-hour, weekly, monthly, concurrency, access, and policy constraints.

Claude Code, OpenAI Codex, Grok Build, Synthetic, and every alternative remain visible by default. “Already owned” is optional personal metadata and can be hidden with a filter; it never changes the public ranking logic.

## Missing data is explicit

Every monthly plan is assigned one comparison class:

- **Token:** a defensible model-specific token denominator exists.
- **Request:** request counts and weights exist, but tokens per request do not.
- **Managed:** the product sells agent tasks, app-builder tokens, platform credits, work units, or fair-use throughput.
- **Relative:** the provider publishes a tier multiplier without an absolute base pool or complete model weights.
- **Provider-hidden:** the plan exists, but the provider withholds the allowance or deduction formula required for a numerical comparison.

A provider-hidden record is a completed research result, not a zero. The plan stays visible with the exact missing fields and cannot enter only the rankings that require those fields.

The catalog includes native-unit adapters for transparent token gateways, weighted token plans, request plans, IDE credits, managed coding agents, app builders, and fair-use passes. Long-tail catalog records with published raw tokens, weighted plan tokens, request windows, daily tasks, platform credits, or concurrency limits retain those native quantities even when they cannot be reduced to model tokens.

## Claude and Fable

Anthropic does not publish absolute Claude Code subscription buckets. Claude Pro, Max 5×, and Max 20× therefore use measured ranges rather than invented exact quotas. Fable 5 is PAYG-only on Pro; Max includes it but caps it at 50% of the shared weekly meter. Because Anthropic does not publish Fable’s meter multiplier, Tokenmaxx applies the access rule and share cap without fabricating a raw-token ceiling.

## External benchmarks only

Tokenmaxx imports externally published model and coding-agent results. It does not currently run a private benchmark suite or collect user telemetry. A benchmark result remains attached to the exact model, harness, version, effort, cost denominator, and source that produced it.

The repository includes a future community-submission schema, but community results remain separate from publisher-owned results until review.

## Run locally

Astro 7 requires Node.js 22.12 or newer.

```bash
nvm use
npm install --no-audit --no-fund
npm run refresh:data
npm run verify
npm run dev
```

Build the static site:

```bash
npm run build
```

Cloudflare Pages settings:

```text
Framework preset: Astro
Build command: npm run build
Build output directory: dist
Root directory: /
Node version: 22.12.0 or newer
```

The application is static; no Cloudflare adapter is required.

## Data pipeline

```text
scripts/build_data.py
  → broad market catalog and source records

scripts/build_buyer_guide.py
  → provider-specific plan/model calculations
  → verified enrichment adapters
  → long-tail native-unit promotion
  → access corrections
  → universal and alternative-only rankings
  → src/data/buyer-guide.json
  → public/data/buyer-guide.json
```

Important modules:

- `scripts/buyer_guide/models.py` — canonical model rates, intelligence, and aliases.
- `scripts/buyer_guide/plans.py` — plan definitions and enrichment orchestration.
- `scripts/buyer_guide/enrichment.py` — verified provider adapters and explicit missing fields.
- `scripts/buyer_guide/native_units.py` — raw-token, request, work-unit, and fair-use normalization.
- `scripts/buyer_guide/finalize.py` — access constraints, rankings, shortlists, and audit records.
- `scripts/validate_buyer_guide.py` — data invariants.
- `scripts/check_sources.py` — Astro source and workflow checks.

## GitHub Actions

GitHub Actions is intentionally disabled. There are no executable workflow files under `.github/workflows/`. Refresh, validation, build, and deployment commands remain manual until automation is explicitly enabled.

## License

MIT. Source-page content and external benchmark values remain subject to their publishers’ terms and licenses.
