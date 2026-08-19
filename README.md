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

- **Token:** an exact, measured-range, or measured-lower-bound token denominator exists.
- **Request:** request counts and weights exist, but tokens per request do not.
- **Managed:** the product sells agent tasks, app-builder tokens, platform credits, work units, energy, or fair-use throughput.
- **Relative:** the provider publishes a tier multiplier without an absolute base pool or complete model weights.
- **Calibratable:** the provider’s own usage API and local logs expose a reproducible way to recover the account’s denominator, but no plan-labeled public sample identifies a universal tier value yet.
- **Provider-hidden:** the plan exists, but the provider withholds the allowance or deduction fields required for a numerical comparison and no defensible external measurement closes the gap.

A provider-hidden record is a completed research result, not a zero. The plan stays visible with the exact missing fields and cannot enter only the rankings that require those fields.

Range-based plans are ranked with their **conservative lower capacity bound**. Midpoint and upper estimates remain visible on the plan page and in the generated JSON.

The catalog includes native-unit adapters for transparent token gateways, weighted token plans, request plans, IDE credits, managed coding agents, app builders, fair-use passes, Standard-token pools, API-value ranges, lower-bound measurements, and authenticated usage-meter calibration.

## Deep quota inference

Tokenmaxx no longer stops at provider marketing pages. It also inspects:

- authenticated usage endpoints and billing-response schemas;
- local JSONL token records and transaction histories;
- plan-labeled meter deltas;
- independently maintained quota clients;
- official relative tier relationships;
- quantified user reports whose plan, model, time window, and reset state are identifiable.

This has produced useful current records for:

- Cursor’s exact $20/$70/$400 Other Models pools;
- current Claude Code raw-token and API-equivalent ranges;
- Kimi Allegretto’s measured 1.37–1.50B monthly raw-token range and official tier scaling;
- Factory’s reconstructed 20M/100M/200M Standard-token pools and model multipliers;
- Ollama Pro and Max measured raw-token lower bounds;
- Google Antigravity post-boost mixed-route ranges;
- BytePlus Lite and Pro request ceilings;
- ClinePass’s 2–5× API-value range and authenticated calibration path;
- Grok Build’s billing/local-log calibration formula;
- Devin’s managed message-equivalent ranges;
- Tabnine’s BYOK, hosted-model surcharge, and Headless processing-token economics.

See [Hidden-quota inference](docs/QUOTA_INFERENCE.md) for formulas, source chains, evidence levels, and remaining measurement targets.

## Claude and Fable

Anthropic does not publish absolute Claude Code subscription buckets. Claude Pro, Max 5×, and Max 20× therefore use current measured ranges rather than invented exact quotas. Older, substantially more generous accounting regimes remain historical evidence and are excluded from current rankings.

Fable 5 is PAYG-only on Pro; Max includes it but caps it at 50% of the shared weekly meter. Because Anthropic does not publish Fable’s meter multiplier, Tokenmaxx applies the access rule and share cap without fabricating a raw-token ceiling.

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
  → deep hidden-quota inference
  → model-access corrections
  → conservative range ranking
  → universal and alternative-only frontiers
  → src/data/buyer-guide.json
  → public/data/buyer-guide.json
```

Important modules:

- `scripts/buyer_guide/models.py` — canonical model rates, intelligence, aliases, and task evidence.
- `scripts/buyer_guide/plans.py` — plan definitions and enrichment orchestration.
- `scripts/buyer_guide/enrichment.py` — verified provider adapters and explicit missing fields.
- `scripts/buyer_guide/native_units.py` — raw-token, request, work-unit, and fair-use normalization.
- `scripts/buyer_guide/inferred_subscriptions.py` — Cursor, Claude, Kimi, Factory, Ollama, Antigravity, BytePlus, Grok, ClinePass, Devin, and Tabnine inference.
- `scripts/buyer_guide/capacity_extensions.py` — range, lower-bound, and Standard-token calculations.
- `scripts/buyer_guide/conservative_metrics.py` — conservative default economics and frontiers.
- `scripts/buyer_guide/finalize.py` — access constraints and initial plan-route joins.
- `scripts/buyer_guide/postprocess.py` — conservative rankings and audit metadata.
- `scripts/validate_inferred_subscriptions.py` — deep-inference invariants.
- `scripts/check_sources.py` — Astro source and workflow checks.

## GitHub Actions

GitHub Actions is intentionally disabled. There are no executable workflow files under `.github/workflows/`. Refresh, validation, build, and deployment commands remain manual until automation is explicitly enabled.

## License

MIT. Source-page content and external benchmark values remain subject to their publishers’ terms and licenses.
