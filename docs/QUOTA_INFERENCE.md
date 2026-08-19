# Hidden-quota inference — 19 August 2026

Many coding subscriptions omit an absolute token allowance, but that does not make every plan economically unknowable. Tokenmaxx searches four evidence layers before classifying a denominator as unavailable:

1. official price, rate card, model catalog, and quota mechanics;
2. authenticated usage APIs and local token/cost logs exposed by the product;
3. quantified plan-labeled user measurements with clear time windows and meter deltas;
4. official relative tier relationships that can scale a directly measured base tier.

The generated dashboard keeps four numerical evidence states separate:

- **Exact:** the provider publishes the pool and deduction formula.
- **Measured range:** plan-labeled telemetry identifies a low, midpoint, and high capacity.
- **Measured lower bound:** the observed usage proves at least this much capacity, but omitted usage prevents an upper estimate.
- **Account-calibratable:** the provider exposes enough usage fields to recover a user’s own denominator, but no public plan-labeled sample identifies a market-wide tier value yet.

All range-based rankings use the lower capacity bound. Midpoints and high estimates remain visible on plan pages and in `buyer-guide.json`.

## Generic inversion

For a percentage meter and normalized local usage:

```text
full_bucket_units ≈ normalized_usage_delta / displayed_fraction_delta
```

For a model-priced pool:

```text
normalized_usage_usd = Σ(token_category / 1M × category_rate)
full_bucket_usd      ≈ normalized_usage_usd / displayed_fraction_delta
```

For a measured raw-token range:

```text
average_monthly_tokens = weekly_tokens × 365.2425 / 12 / 7
subscription_USD_per_M = monthly_plan_price / monthly_tokens_in_millions
```

Measurements are rejected when they omit the plan, model, time window, meter movement, reset event, or token-category accounting required to identify the bucket.

## Cursor

Cursor now publishes two distinct monthly pools:

- **Other Models:** Pro $20, Pro Plus $70, Ultra $400, debited at the selected model’s API price.
- **Cursor Models:** a separate larger pool for Cursor Grok and Composer whose numerical size is not published.

Tokenmaxx calculates exact subscription token economics for third-party models from the guaranteed Other Models pool. Cursor Grok and Composer do not inherit that pool. Bonus usage above the guaranteed amount remains additional unranked upside.

Evidence:

- <https://cursor.com/docs/models-and-pricing>
- <https://cursor.com/pricing>

## Claude Code

Anthropic publishes prices, model API rates, the shared Claude/Claude Code quota structure, and relative plan tiers, but not the absolute five-hour and weekly buckets. Current telemetry also shows substantial accounting variance, so Tokenmaxx preserves a current measured range rather than choosing the most generous historical regime.

Current average-month API-equivalent ranges used by the dashboard:

| Plan | Conservative | Midpoint | High |
|---|---:|---:|---:|
| Pro | $135.88 | $217.41 | $364.16 |
| Max 5× | $679.39 | $1,087.03 | $1,820.78 |
| Max 20× | $2,717.58 | $4,348.13 | $7,283.11 |

Current mixed raw-token ranges:

| Plan | Weekly range | Average-month range |
|---|---:|---:|
| Pro | 0.20–0.28B | 0.87–1.22B |
| Max 5× | 1.00–1.40B | 4.35–6.09B |
| Max 20× | 3.54–5.60B | 15.39–24.35B |

The historical Max 20× regime of roughly $2,508–$5,429 API-equivalent per week remains stored as history and is excluded from the current ranking.

Fable 5 is PAYG-only on Pro. Max includes Fable but limits it to 50% of the shared weekly meter. The hidden Fable multiplier prevents an exact raw-token ceiling, so the official share cap is applied without fabricating that multiplier.

Evidence:

- <https://github.com/anthropics/claude-code/issues/84607>
- <https://github.com/anthropics/claude-code/issues/57699>
- <https://github.com/anthropics/claude-code/issues/43118>
- <https://platform.claude.com/docs/en/about-claude/pricing>

## Kimi Code

A five-month Allegretto dataset reports approximately 3.152B total tokens and a 91.9% cache-read share. Continuous weekly sampling implies approximately 1.37–1.50B raw tokens per month on Allegretto.

Tokenmaxx scales that directly measured base using Kimi’s published Code tier relationship:

| Plan | Measured/scaled raw tokens per month |
|---|---:|
| Moderato | 0.274–0.300B |
| Allegretto | 1.370–1.500B |
| Allegro | 4.110–4.500B |
| Vivace | 8.220–9.000B |

K3 1M consumes approximately twice the plan quota of K3 256K, so its route receives half the raw-token capacity. HighSpeed consumes approximately three times Standard quota and therefore receives one-third capacity. HighSpeed is unavailable on Moderato.

Evidence:

- <https://github.com/Golden0Voyager/kimi-code-usage>
- <https://www.kimi.com/resources/kimi-code-introduction>
- <https://www.kimi.com/resources/kimi-k2-7-code-pricing>
- <https://forum.moonshot.ai/t/allegretto-annual-member-kimi-code-forced-highspeed-after-beta-3x-token-consumption-no-standard-toggle/460>

## Factory

Factory publishes model multipliers and three independent rolling windows. Its usage API exposes Standard usage as token units, allowing the monthly pools to be reconstructed:

| Plan | Monthly Standard tokens |
|---|---:|
| Pro | 20M |
| Plus | 100M |
| Max | 200M |

Raw-token capacity is model- and workload-specific:

```text
standard_tokens_per_raw_token = model_multiplier × (
    fresh_share × 1.0
  + cache_read_share × 0.1
  + output_share × 5.0
)

raw_tokens = Standard_pool / standard_tokens_per_raw_token
```

Examples of current official model multipliers include Luna 0.08×, GPT-5.4 mini 0.3×, Terra 0.8×, Sol 2×, and Fable 5 4×. The numerical five-hour and seven-day sublimits remain unknown and may bind before the monthly pool.

Evidence:

- <https://docs.factory.ai/pricing/individuals>
- <https://docs.factory.ai/models>
- <https://github.com/robinebers/openusage/pull/1003>

## Ollama Cloud

Ollama officially publishes Pro as 50× Free and Max as 5× Pro, with model-dependent five-hour and weekly usage. A public Pro coding run recorded at least 58M local chat tokens while moving the weekly meter 40.8%.

```text
Pro weekly raw-token lower bound = 58M / 0.408 = 142.16M
Pro average-month lower bound     = 618.12M
Max average-month lower bound     = 5 × Pro = 3.09B
```

These are lower bounds because encoder usage, remote/server-side tokens, and parts of the model mix were not captured locally. The route remains intentionally unscored because no single model represents the measured workload.

Evidence:

- <https://ollama.com/pricing>
- <https://github.com/jarvis-llm-codec/jarvis-code>

## Google Antigravity

Antigravity meters “work done,” not a fixed token count. A Pro user measured more than 300M weekly input tokens before January 2026 and less than 9M after the March quota reduction. Google then changed the plan structure and increased paid Gemini limits twice in May.

Tokenmaxx uses a deliberately conservative current Pro range of 18–30M raw tokens per week, centered at 24M, then applies the documented relative individual tiers:

| Plan | Average-month mixed-route range |
|---|---:|
| Google AI Plus | 39.13–65.22M |
| Google AI Pro | 78.27–130.44M |
| Ultra 5× | 391.33–652.22M |
| Ultra 20× | 1.565–2.609B |

This is an unscored mixed route. Gemini and third-party models remain visible as available models, but they do not inherit the mixed pool because Google does not publish their compute weights.

Evidence:

- <https://antigravity.google/docs/plans>
- <https://antigravity.google/blog/changes-to-antigravity-plans>
- <https://www.theregister.com/2026/03/12/users-protest-as-google-antigravity-price_floats_upward/>
- <https://9to5google.com/2026/05/21/google-has-tripled-gemini-usage-limits-for-antigravity-twice/>

## BytePlus ModelArk

Current plans are represented directly in request units:

| Plan | Five hours | Weekly | Monthly |
|---|---:|---:|---:|
| Lite | 1,200 | 9,000 | 18,000 |
| Pro | 6,000 | 45,000 | 90,000 |

The request ceilings are useful, but BytePlus does not publish a stable input/cache/output distribution per coding request. Tokenmaxx therefore calculates $/1,000 requests and quality-adjusted request economics without converting requests into fabricated tokens.

Evidence:

- <https://docs.byteplus.com/en/docs/ModelArk/2188958>
- <https://ai.byteplus.com/en/activity/codingplan>

## ClinePass

Cline advertises $9.99 per month and approximately 2–5× standard API-rate usage. Tokenmaxx converts that claim into a $19.98–$49.95 monthly API-equivalent range and ranks the lower bound.

Cline is also directly account-calibratable. Its authenticated usage endpoint exposes five-hour, weekly, and monthly percentages, while transaction history exposes model, prompt tokens, completion tokens, and USD cost:

```text
bucket_API_value ≈ summed_transaction_cost / displayed_fraction_delta
```

A clean public transaction-plus-meter snapshot would replace the advertised range with a measured range.

Evidence:

- <https://cline.bot/blog/clinepass-best-of-value-for-open-weight-models>
- <https://github.com/baranbingol1/quotaboard/blob/c1d272325894a98f3ab0f60779585c36a162a9be/src/AiLimits.Infrastructure/Providers/Cline/ClinePassLimitStrategy.cs>

## Grok Build

Grok’s consumer subscription pool is shared weekly across Build, Chat, Imagine, Voice, and other products. The official UI exposes a percentage, while Grok’s billing API and local Build logs expose enough information for account-specific inversion:

- weekly usage percentage and period;
- monthly used and limit values in USD;
- subscription tier display;
- local input, cached-input, output, and model totals.

```text
weekly_capacity ≈ normalized_local_usage_delta / weekly_fraction_delta
```

A public sample reports 68% weekly use, 12.34M local Build tokens, $139.05 monthly used, and a $180 monthly limit. The plan tier is not published, so Tokenmaxx stores it as an unlabeled-account lower bound and does not assign it to Basic, SuperGrok, Pro, or Heavy.

Evidence:

- <https://github.com/danecwalker/groktok>
- <https://docs.x.ai/grok/faq>
- <https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/src/extensions/billing.rs>

## Devin

Devin publishes work-based daily and weekly quotas rather than raw tokens. Maintained user observations provide broad daily message-equivalent ranges:

| Plan | Premium/day | Premium Plus/day | Lightweight/day |
|---|---:|---:|---:|
| Pro | 8–101 | 7–27 | 47–190 |
| Max | 47–631 | 42–170 | 291–1,190 |

These remain managed-work estimates because one message can contain a very different number of agent actions, model calls, tokens, and cloud-compute steps.

Evidence:

- <https://docs.devin.ai/desktop/accounts/quota>
- <https://docs.devin.ai/admin/billing/self-serve>

## Tabnine

Tabnine’s seat subscription is a coding platform rather than a bundled hidden model pool:

- BYOK inference is unlimited at no Tabnine token charge.
- Tabnine-provided LLM usage is purchased separately at the underlying provider price plus a 5% handling fee.
- Headless Business includes up to 5B processing tokens/month for $1,200/month.
- Headless Enterprise includes up to 50B processing tokens/month for $5,000/month.
- The selected LLM provider bill remains separate from the headless-platform price.

Tokenmaxx therefore reports headless platform cost as $0.24 and $0.10 per million processing tokens, while keeping underlying model inference separate.

Evidence:

- <https://www.tabnine.com/pricing/>
- <https://www.tabnine.com/headless-agent-pricing/>

## Remaining evidence gaps

The strongest remaining unknowns are narrower than “the plan limit is unpublished”:

- Grok: one tier-labeled clean billing + local-token snapshot per paid tier.
- Claude: stable current server-side token/category weights and clean multi-account windows.
- Cursor: the numerical Cursor Models pool and bonus-usage distribution.
- Kimi: independent longitudinal datasets and stable post-beta HighSpeed routing.
- Factory: numerical five-hour and seven-day Standard-token buckets.
- Antigravity: fresh post-boost multi-account token telemetry and model compute weights.
- Ollama: complete model mix and server-side token totals for clean meter windows.
- ClinePass: a clean transaction-history and meter-delta calibration window.

These are now represented as measurable research targets rather than generic unresolved cells.
