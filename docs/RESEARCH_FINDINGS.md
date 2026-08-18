# Research findings — 18 August 2026

Tokenmaxx no longer has one “best coding subscription.” The evidence supports separate leaders for model quality, native-agent task performance, subscription cost per expected pass, sustained passing-work throughput, entry price, speed, and raw allowance. The dashboard defaults to a **direct external intelligence floor of 60**, so large pools of weaker models stay visible without dominating frontier-quality recommendations.

## Current evidence inventory

- 219 plan tiers across 69 providers or product families.
- 77 advertised model labels and 293 plan/model routes.
- 35 model labels with direct external model or native-agent evidence; 42 broad, ambiguous, legacy, managed, or newly released labels remain visible but excluded from intelligence rankings.
- 83 external benchmark rows from Artificial Analysis, Terminal-Bench 2.1, and CursorBench 3.2.
- 68 direct subscription-task estimates where the native harness, model route, included access, and allowance denominator can be joined defensibly.
- Eight Fable-specific benchmark rows across model intelligence, Claude Code, Terminal-Bench, and CursorBench.

## Fable 5

Fable is now a first-class model rather than a string buried in an external benchmark table:

- Artificial Analysis model Intelligence Index: 60.
- Claude Code Coding Agent Index: 66 at the imported max-with-fallback configuration.
- Terminal-Bench 2.1: 83.8% for Claude Code with Fable xhigh.
- CursorBench 3.2: 65.2%–70.5% across Medium, High, Extra High, and Max, with model API cost ranging from $6.80 to $17.32 per task.

Anthropic’s plan semantics are modeled separately from benchmark quality. Fable is PAYG-only on Pro. Max includes it inside the shared quota but caps it at 50% of the weekly meter, and Anthropic says it consumes the meter faster. The multiplier is hidden, so Tokenmaxx does not invent an exact Fable token ceiling.

## Claude Code plan estimates

Anthropic does not publish absolute five-hour or weekly subscription token pools. Tokenmaxx therefore presents measured ranges, with raw mixed tokens and API-equivalent value as separate denominators:

| Plan | Mixed raw tokens/week | Average raw tokens/month | Full-utilization subscription $/1M raw tokens | API-equivalent/month | Measured value multiple |
|---|---:|---:|---:|---:|---:|
| Pro | 0.20–0.28B | 0.87–1.22B | $0.01643–$0.02300 | $523.51–$1,180.30 | 26.18–59.01× |
| Max 5× | 1.00–1.40B | 4.35–6.09B | $0.01643–$0.02300 | $2,617.57–$5,901.49 | 26.18–59.01× |
| Max 20× | 4.00–5.60B | 17.39–24.35B | $0.00821–$0.01150 | $10,470.29–$23,605.97 | 52.35–118.03× |

Every Claude plan page also calculates pure-category counterfactuals for Opus 5, Fable 5, Sonnet 5, and Haiku 4.5 across fresh input, cache reads, five-minute cache writes, one-hour cache writes, and output. Those rows answer what the measured included API-equivalent pool could buy if spent entirely on one category; they are not claims that Anthropic’s hidden subscription meter equals API billing.

## What the quality-gated Pareto fronts show

At native Coding Agent Index score 60 or higher, the **budget frontier** contains Claude Code and Codex tiers rather than StepFun. The **throughput frontier** selects Claude Max 20× Opus/Fable configurations and Codex Pro 20× Sol under the current measured denominators. Provider-specific fronts expose the best Claude and Codex choices independently, so global dominance on one axis does not erase a product family.

Model-level price/intelligence frontiers currently include high-quality Claude and OpenAI configurations alongside Kimi, Grok, DeepSeek, and other lower-cost models where they are not dominated on both intelligence and normalized token price. CursorBench remains on its own benchmark scale and is not merged into the Artificial Analysis composite.

## Where StepFun belongs

StepFun’s Flash plans remain exceptional **raw-subsidy** products. Their official credit conversion can imply more than fifty times the subscription price in provider-rate inference. Step 3.7 Flash has a substantially lower external intelligence score than the frontier models, so StepFun appears in the allowance appendix and lower-quality-volume views rather than the default frontier-quality recommendation.

## Remaining evidence gaps

The unresolved rows are not blank work items that can be completed by arithmetic. They fall into explicit categories:

- **Provider-hidden pools:** Cursor’s first-party model pool, Claude’s absolute five-hour/weekly meter and model multipliers, MiniMax included bars, Kimi absolute shared token pool, Google/xAI shared-compute pools, and similar limits.
- **Ambiguous aliases:** broad catalog labels, routing aliases, unknown quantization/provider routes, and family names that cannot inherit a specific checkpoint’s benchmark safely.
- **Managed products:** products such as Devin, Jules, Replit Agent, Bolt, and Lovable whose work units include orchestration or compute rather than a stable model-token denominator.
- **New or unbenchmarked models:** current products without a direct external result on an imported benchmark.
- **Legacy plans/models:** retained for history but excluded from current recommendations.

These records remain searchable with an exclusion reason and cannot receive fabricated intelligence, token allowance, or cost-per-task values.

## Update rule

Official price/rate/model/access changes and external benchmark releases enter through separate deterministic stages. A source change produces a review candidate; it does not silently rewrite rankings. Historical runs stay attached to the plan, model, rate, and benchmark version that existed when the evidence was recorded.
