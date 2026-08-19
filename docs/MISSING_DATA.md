# Missing-data audit — 19 August 2026

Tokenmaxx does not use a generic “unresolved” state. Every monthly plan is either numerically comparable in its proper unit, measurable as a range or lower bound, account-calibratable, or documented with the exact field that prevents a stronger comparison.

## Evidence states

| State | Ranking treatment |
|---|---|
| Exact token pool | Full plan × model token economics. |
| Measured token range | Lower capacity bound drives rankings; midpoint and high remain visible. |
| Measured lower bound | Included in raw-token comparisons as a conservative minimum; displayed $/token is an upper bound. |
| Native request pool | $/1,000 requests and quality-adjusted request economics; no fabricated tokens/request. |
| Managed/work-unit pool | Native tasks, credits, energy, processing tokens, or platform units only. |
| Relative | Tier multiplier is shown, but no raw-token ranking without an absolute base pool. |
| Account-calibratable | Provider meter and local logs expose a reproducible inversion formula, but no public tier-labeled snapshot identifies a universal plan value. |
| Provider-hidden | No official or measured path currently identifies the requested denominator. |

## Previously “unpublished” providers now quantified

| Product | Current treatment |
|---|---|
| Cursor | Exact $20/$70/$400 third-party Other Models pools. First-party Cursor Models remain a separate unquantified pool. |
| Claude Code | Current raw-token and API-equivalent ranges from plan-labeled logs and weekly-meter movement. Historical high-capacity accounting is retained separately. |
| Kimi Code | Allegretto 1.37–1.50B raw tokens/month measured over five months; other tiers scaled by official plan relationships; K3 1M and HighSpeed weights applied. |
| Factory | 20M/100M/200M Standard-token pools plus current official model multipliers; raw capacity is calculated per model and token mix. |
| Ollama Cloud | Pro and Max raw-token lower bounds from a measured Pro run plus the official 5× Max relationship. |
| Google Antigravity | Post-boost mixed-route ranges reconstructed from measured Pro telemetry and Google’s paid-plan increases; individual model weights remain hidden. |
| BytePlus ModelArk | Lite 1,200/9,000/18,000 and Pro 6,000/45,000/90,000 request ceilings. |
| ClinePass | $19.98–$49.95 monthly API-equivalent range from the official 2–5× claim, plus an authenticated usage/transaction calibration path. |
| Grok Build | Account-calibratable from weekly percentage, monthly billing fields, subscription tier display, and local Build token logs. The available $180 public sample remains tier-unassigned. |
| Devin | Native daily message-equivalent ranges layered on the official work-based daily/weekly structure. |
| Tabnine | BYOK and hosted-model billing semantics plus exact 5B/50B Headless processing-token plans; underlying LLM bill remains separate. |

The complete formulas and evidence links are in [`QUOTA_INFERENCE.md`](QUOTA_INFERENCE.md).

## Token-comparable plans

A plan enters the plan × model token table only when all of the following are available:

1. monthly subscription price;
2. exact, ranged, or lower-bound included capacity;
3. exact served model or an explicitly unscored mixed route;
4. model-specific deduction or a defensible raw-token measurement;
5. external quality evidence when the route enters intelligence-adjusted rankings.

Mixed-route lower bounds remain useful for absolute capacity and $/raw-token, but they receive no intelligence score unless the model mix is identified.

## Request-comparable plans

A plan remains in request units when it publishes request counts or weights without a stable token distribution. This includes Synthetic weighted requests, Apertis fixed deductions, BytePlus ModelArk, Neuralwatt energy-per-typical-request, Zencoder model-weighted credits, and MiniMax Starter.

Raw request counts are never presented as model tokens.

## Managed native units

These products expose real allowance units that include orchestration, compute, browser work, deployment, media, or other non-token services:

- Google Jules daily and concurrent managed tasks;
- Replit platform credits and parallel agents;
- Cosine and Codebuff work credits;
- Kiro complexity-dependent work credits;
- Bolt, Lovable, v0, Base44, VULK, and a0.dev app-builder credits;
- Amazon Q agentic inference calls and transformation lines;
- Devin work- and action-based quota ranges;
- Venice shared premium credits;
- Tabnine Headless processing tokens with separate LLM billing.

They remain visible with native economics and cannot enter model-token rankings until the required conversion exists.

## Remaining narrow unknowns

| Product | What is still required |
|---|---|
| Grok Build | A clean public snapshot pairing `subscription_tier_display`, the billing response, and local token deltas for each paid tier. |
| Claude Code | Stable current server-side model/category weights and independent clean windows across multiple accounts. |
| Cursor first-party models | Numerical Cursor Models pool and the distribution of bonus usage. |
| Kimi Code | Independent longitudinal datasets and stable post-beta Standard/HighSpeed routing behavior. |
| Factory | Numerical five-hour and seven-day Standard-token sublimits. |
| Google Antigravity | Fresh post-boost multi-account telemetry and model-specific work/compute weights. |
| Ollama Cloud | Complete model mix plus server-side input/cache/output totals for clean meter windows. |
| ClinePass | A public transaction-history + meter-delta calibration window to replace the advertised 2–5× range. |
| Tabnine reserved hosted inference | Price and size of separately negotiated reserved model quota. |
| Qwen Global Token Plan | Current primary-source global-plan confirmation and complete live multipliers beyond the official Qwen3.6 Plus worked example. |

These are measurable research targets rather than generic unknown cells.

## Promotion rule

A plan moves into a stronger comparison class only when the evidence provides the missing denominator. The generated output keeps:

```text
comparisonClass
researchStatus
missingFields[]
source
confidence
allowance
evidenceSources[]
model access
capacity estimate type
```

That makes every exclusion inspectable and prevents a weakly documented plan from outranking a plan with reproducible arithmetic.
