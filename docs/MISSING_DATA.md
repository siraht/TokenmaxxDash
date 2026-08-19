# Missing-data audit — 19 August 2026

Tokenmaxx does not use a generic “unresolved” state. Every monthly plan is either numerically comparable in its proper unit or records the exact field that prevents a stronger comparison.

## Token-comparable

A plan enters the main subscription × model table only when all of the following are available:

1. a monthly subscription price;
2. an included dollar, token, credit, or measured-capacity denominator;
3. the model served by the plan;
4. a model-specific deduction or token-rate formula;
5. external model quality evidence for quality-adjusted rankings.

The catalog contains direct adapters for Codex, Claude measured ranges, OpenCode Go, Command Code, Synthetic, Chutes, StepFun, Z.AI, MiMo, Alibaba, GitHub Copilot, Cursor’s published third-party pool, Kilo, ZenMux, Nous Portal, JetBrains AI, Zed, Warp, and other plans whose evidence supports that join.

## Request-comparable

A plan remains in request units when the provider publishes model-weighted request consumption but does not publish the token distribution of a request. Raw request counts are never presented as tokens.

Examples include Synthetic’s weighted-request bucket, Apertis fixed request deductions, and long-tail products with numeric monthly or rolling request limits.

## Managed native units

These products expose a real allowance, but the allowance includes orchestration, compute, browser work, deployment, media, or other non-token services:

- Google Jules — daily and concurrent managed tasks;
- Replit — platform credits and parallel agents;
- Cosine — agent work credits;
- Kiro — complexity-dependent work credits;
- Bolt, Lovable, v0, Base44, VULK, and a0.dev — app-builder or product credits;
- Amazon Q — agentic requests and transformation units;
- Venice — shared premium credits plus fair-use text;
- Fireworks Fire Pass, Ollama Cloud, Arli, Claudin, CheapestInference, and similar products — fair-use or reserved-throughput access.

They stay visible with their native economics and cannot enter $/token rankings until a model-token conversion exists.

## Relative plans

A relative plan publishes a multiplier or weighted plan-token pool without enough information to recover raw model tokens. Examples include Kimi’s relative Code tiers, Codebuff’s tier multipliers, CanopyWave and Routera weighted plan tokens, and products with incomplete model-weight tables.

Required missing fields are recorded per plan, commonly:

- absolute base-tier allowance;
- complete per-model deduction weights;
- whether cached input, fresh input, and output use different weights;
- the exact checkpoint behind a model-family label.

## Provider-hidden plans

The provider publishes the subscription but withholds the numerical quota or deduction formula. These are the largest remaining gaps:

| Product | Known | Still provider-hidden |
|---|---|---|
| Grok Build | tier prices, Grok model API rates, shared weekly-meter behavior | absolute weekly pool, Build weighting, cross-surface consumption formula |
| Claude Code | prices, plan relationships, model API rates, measured user ranges | official five-hour/weekly pools and hidden model/category meter weights |
| Cursor first-party models | tier prices and third-party dollar pools | numerical first-party Cursor-model pool and routing weights |
| MiniMax included Token Plan bars | PAYG request pricing and tier prices | absolute five-hour and weekly included values |
| Kimi Code | prices, relative tier scaling, concurrency, model pricing | absolute shared token pool and Code-window deductions |
| Factory | prices and relative 5h/7d/30d structure | numerical buckets and model multipliers |
| Devin Desktop | tier prices and daily/weekly structure | absolute included daily and weekly quota |
| Google Antigravity | plan prices and relative access tiers | product-specific absolute compute pool and model weights |
| Ollama Cloud | prices, concurrency, model-dependent fair use | sustained token/request thresholds and post-threshold behavior |
| Cline Pass | price and advertised relative value | absolute five-hour, weekly, and monthly pools |
| BytePlus ModelArk | prices and relative usage claims | absolute quota and token/credit formula |
| Qwen Global Token Plan | reported tier prices and weekly credits | current primary-source regional plan and complete model multiplier table |

These records are not assigned guessed values. New user measurements can narrow them later, but a single qualitative complaint or an unscoped token count cannot become a plan denominator.

## Long-tail evidence

Many tracker-discovered plans publish useful numeric fields even without a full model join. Tokenmaxx promotes these into their native units:

- NanoGPT weekly input tokens;
- Entrim/OpenClaw daily input and output quotas;
- Routera and CanopyWave weighted plan tokens;
- Routing.sh and StreamLake rolling request windows;
- Atlas Cloud weighted points;
- Trae, SwiftRouter, DevPass, and Router9 credit pools;
- CheapestInference reserved daily access;
- managed app-builder credits and daily-task plans.

The source remains labeled secondary until a primary provider page confirms the same values.

## Promotion rule

A plan moves into a stronger comparison class only when the evidence provides the missing denominator. The generated output keeps:

```text
comparisonClass
researchStatus
missingFields[]
source
confidence
allowance
model access
```

That makes every exclusion inspectable and prevents a weakly documented plan from outranking a plan with reproducible arithmetic.
