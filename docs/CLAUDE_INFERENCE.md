# Claude Code subscription inference — 18 August 2026

Anthropic publishes the price and relative tier structure of Claude Pro, Max 5×, and Max 20×, but does not publish the numerical five-hour or weekly token pools. Claude and Claude Code share those limits, and optional usage credits are separate PAYG billing. Tokenmaxx therefore treats every Claude allowance as a **measured range**, never an official exact quota.

## Two independent denominators

### Mixed raw tokens

Community `ccusage` logs paired with dashboard percentages imply:

| Plan | Weekly mixed raw tokens | Average-month mixed raw tokens | Basis |
|---|---:|---:|---|
| Pro | 0.20–0.28B | 0.87–1.22B | Max 5× range scaled by the official 5× tier relationship |
| Max 5× | 1.00–1.40B | 4.35–6.09B | Direct Max 5× measurement plus current-accounting bounds |
| Max 20× | 4.00–5.60B | 17.39–24.35B | Direct/scaled Max 20× measurements and API-value cross-checks |

Raw tokens include cached context reads and output. In heavy coding sessions, cache reads dominate, so this number is useful for reconstructing observed logs but is not “new information processed.”

```text
average_weeks_per_month = 365.2425 / 12 / 7 = 4.348125
average_monthly_raw_tokens = weekly_raw_tokens × 4.348125
subscription_USD_per_M_raw = monthly_price / monthly_raw_tokens_in_millions
```

Resulting full-utilization subscription cost:

| Plan | Subscription USD per 1M mixed raw tokens |
|---|---:|
| Pro | $0.016427–$0.022998 |
| Max 5× | $0.016427–$0.022998 |
| Max 20× | $0.008214–$0.011499 |

Pro and Max 5× have the same estimated unit cost because the measured pool and price scale by five. Max 20× appears about twice as favorable because reported current and historical weekly accounting do not scale linearly with price; this is precisely why the dashboard preserves ranges and measurement dates.

### API-equivalent value

Published API pricing allows local Claude logs to be valued by token category. Reported weekly API-equivalent consumption paired with the shared weekly meter gives the following observed range:

| Plan | Weekly API-equivalent | Average-month API-equivalent | Value multiple |
|---|---:|---:|---:|
| Pro | $120.40–$271.45 | $523.51–$1,180.30 | 26.18–59.01× |
| Max 5× | $602.00–$1,357.25 | $2,617.57–$5,901.49 | 26.18–59.01× |
| Max 20× | $2,408.00–$5,429.00 | $10,470.29–$23,605.97 | 52.35–118.03× |

The lower bound reflects conservative current-accounting telemetry. The upper bound reflects historical weekly burn before reported meter behavior changed. The range is not a claim that Anthropic promises either dollar amount.

## Model and token-category estimates

Current API rates are stored for:

- Claude Opus 5
- Claude Fable 5
- Claude Sonnet 5
- Claude Haiku 4.5

For each token category:

```text
eligible_API_value = measured_monthly_API_value × route_allowance_fraction
estimated_category_capacity_M = eligible_API_value / API_rate_USD_per_M
subscription_USD_per_M = monthly_subscription_price / estimated_category_capacity_M
```

The plan pages calculate fresh input, cache reads, five-minute cache writes, one-hour cache writes, and output separately. These are **pure-category counterfactuals**: no real workload can simultaneously consume all five ceilings.

## Fable 5

Fable is not treated like the other Claude models:

- Pro: PAYG usage credits from the first Fable request, so included Fable capacity is zero.
- Max 5× and Max 20×: included inside the shared quota, capped at 50% of the weekly meter.
- Anthropic states that Fable consumes the meter faster, but does not publish the multiplier.

The Fable category estimates apply the official 50% pool share. They do **not** translate that share into an exact raw-token allowance because doing so would require the hidden Fable meter multiplier.

## Why the ranges can change

A refresh should create a new plan-version record when any of these change:

- Anthropic alters the five-hour or weekly meter.
- Cache reads, cache writes, long context, effort, or fallback models receive new hidden weights.
- The Pro/Max tier relationship changes.
- Public API rates change.
- Fable’s 50% cap or plan eligibility changes.
- A larger controlled measurement set narrows the raw-token or API-equivalent interval.

Old runs must remain attached to the rate and meter regime active when they occurred.
