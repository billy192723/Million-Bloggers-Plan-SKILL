# Traffic & Engagement Prediction Model

The `creator-incubator` skill produces **range forecasts with explicit assumptions** for every content card. This file is the math.

## Core Principles

1. **Never a point estimate.** Always a range `[low, high]`. The width narrows after W4 as the user accumulates actuals.
2. **Always show assumptions.** The user (and you, the agent) can audit the inputs.
3. **Calibrate weekly.** After W4, the model adjusts based on `predicted_vs_actual` from past cards.
4. **Account history matters more than content quality for new accounts.** First 30 posts get a "新号" penalty.

## Formula

```
predicted_views = baseline
                 × trend_heat
                 × time_multiplier
                 × hook_quality
                 × format_fit
                 × account_age_factor
                 × niche_benchmark_factor
```

```
predicted_engagement_rate = niche_benchmark_engagement
                            + hook_quality_bonus
                            + format_fit_bonus
                            - account_age_penalty
```

## Variables

### `baseline` (基线)
The user's account's recent average views per post.

| Source | Value |
|---|---|
| 0 actuals (truly new account) | 200 (most platforms), 50 (B站), 500 (YouTube/TikTok) |
| 1-3 actuals | arithmetic mean |
| 4+ actuals | median of last 10 posts |

### `trend_heat` (热度加成)
Multiplier based on how trending the topic is right now.

| Signal | Multiplier |
|---|---|
| No trend (evergreen content) | ×1.0 |
| Mild trend (search up 50-150% vs avg) | ×1.3 |
| Strong trend (search up 150-500%) | ×2.0 |
| Hot trend (search up 500-1500%) | ×3.0 |
| Explosive (news/事件级) | ×4.0-5.0 |

How to measure: count search results in `web_search` for `[topic] 热门 [platform]` and compare to evergreen baseline. Or use public trending pages (微博热搜, 小红书发现页 Top 20, YouTube Trending).

### `time_multiplier` (时段加成)
| Time | Multiplier |
|---|---|
| Off-peak (凌晨 2-6 am) | ×0.7 |
| Mid (工作日上午 10-12) | ×1.0 |
| Peak (晚 19-22) | ×1.2-1.3 |
| Over-saturated (周末晚高峰, 大事件当晚) | ×0.9 (竞争激烈) |

Always use the platform's *target audience* timezone, not the user's.

### `hook_quality` (钩子质量)
LLM self-evaluates the proposed hook on:
- Specificity (has numbers/具体名词?)
- Contrast (反差强不强?)
- Visual / verbal (if video: 有视觉冲击?)
- Curiosity gap (留白多不多?)

Self-score 1-5, maps to:
| Score | Multiplier |
|---|---|
| 1 | ×0.6 |
| 2 | ×0.8 |
| 3 | ×1.0 |
| 4 | ×1.2 |
| 5 | ×1.4 |

Be honest. The LLM should not default to 4-5.

### `format_fit` (格式适配)
| Situation | Multiplier |
|---|---|
| 创意原生该平台格式 (e.g. 30s 竖屏发抖音) | ×1.2 |
| 轻度适配 (e.g. 8min 横屏发抖音) | ×0.7 |
| 强行复用 (e.g. 1500 字长文发抖音) | ×0.5 |

### `account_age_factor` (账号年龄)
| Account State | Multiplier |
|---|---|
| < 30 天, < 100 粉 | ×0.5 |
| < 30 天, > 100 粉 | ×0.7 |
| 30-90 天, < 1k 粉 | ×0.8 |
| 90-180 天, < 1k 粉 | ×0.9 |
| 180+ 天, 1k-1w 粉 | ×1.0 |
| 1w-10w 粉 | ×1.0-1.1 |
| 10w+ 粉 | ×1.1-1.2 |

### `niche_benchmark_factor` (赛道加成)
Some niches have higher baseline engagement (e.g. AI tools on 小红书 averages 6% engagement vs general 3%).

| Niche-tier | Multiplier |
|---|---|
| Hot niche (AI / 极简 / 副业) | ×1.2 |
| Average niche | ×1.0 |
| Saturated niche (美食, 美妆) | ×0.85 |

## Engagement Rate

```
predicted_engagement_rate = niche_benchmark_engagement
                            + hook_quality_bonus
                            + format_fit_bonus
                            - account_age_penalty
```

`niche_benchmark_engagement` from `references/platform-specs.md` per platform.

| Engagement Component | Adjustment |
|---|---|
| Hook score 5 | +1.5pp |
| Hook score 4 | +0.8pp |
| Hook score 3 | +0pp |
| Hook score 2 | -0.5pp |
| Format fit (native) | +0.5pp |
| Format fit (forced) | -0.5pp |
| Account age < 30 天 | -1.0pp |
| Account age 30-90 天 | -0.5pp |

## Calibration (W4+)

After 4 weeks, the user has ≥ 10 data points. Compute:

```
calibration_score = mean(actual_views / predicted_views_mid)
```

| Score | Interpretation | Action |
|---|---|---|
| 0.5-0.8 | Predictions too optimistic | Multiply next 2 weeks by 0.7 |
| 0.8-1.2 | Calibrated | No adjustment |
| 1.2-1.5 | Predictions too conservative | Multiply next 2 weeks by 1.2 |
| 1.5+ | Either lucky or model wrong | Investigate before adjusting |

Show the user their calibration score in `/review` output. It's the single most useful number to track.

## Confidence Intervals

The model outputs a `[low, high]` range. Width depends on data:

| Data State | Width |
|---|---|
| 0 actuals (W1) | ±70% of midpoint (e.g. 5k ± 3.5k → 1.5k-8.5k) |
| 1-3 actuals (W2) | ±50% |
| 4-10 actuals (W3-4) | ±35% |
| 11-20 actuals (W5-8) | ±25% |
| 21+ actuals (W9+) | ±15% |

## Worked Example

User state:
- New 小红书 account, 50 followers, 12 days old
- Niche: AI 工具评测
- Topic: Claude 4.5 release (trending ×3.0)
- 钩子: "5 个工具我砍到 1 个" (hook score 4)
- Format: 9 图图文 (native 小红书, ×1.2)
- Publish time: 周二 20:30 (peak, ×1.2)

Compute predicted_views:
- baseline (new account): 200
- × trend_heat 3.0 = 600
- × time 1.2 = 720
- × hook 1.2 = 864
- × format 1.2 = 1037
- × account_age 0.5 (新号) = 518
- × niche_factor 1.2 (AI hot) = 622

predicted_engagement_rate:
- niche_benchmark: 4.5% (AI 工具 小红书)
- + hook_bonus 0.8 (score 4) = 5.3%
- + format_bonus 0.5 (native) = 5.8%
- - account_age_penalty 1.0 = 4.8%

Width: ±70% (0 actuals)
- predicted_views: 187-1057 (rounded: ~200-1050)
- predicted_engagement_rate: 1.4-8.2%

Output to user:
> 预测流量: 200-1000 / 互动率: 1.5-8% (新号,基线低,范围较宽,4 周后校准)

## Output Format

Always emit in content card frontmatter:

```yaml
predicted_views: 200-1000
predicted_engagement_rate: 1.5-8.0%
prediction_confidence: low   # low | medium | high
prediction_basis: "baseline=200 (new acct), trend=3.0 (Claude 4.5 release), hook=4, format=native, niche=AI"
```

After 4+ weeks of actuals, the skill should *retrospectively* fill in `actual_views` and `actual_engagement_rate` and `calibration_delta` in the frontmatter when the user pastes actuals in `/review`.

## What the Model Deliberately Doesn't Predict

- **Conversion rate** (click → follow / buy). Too noisy without historical data.
- **Long-tail views** (3+ month residual). Requires ≥ 6 months of data.
- **Sentiment / virality surprise**. Model assumes normal distribution, not power-law.

Always caveat: "This is a baseline forecast, not a ceiling. 1 in 10 posts will 5-10x the prediction. 1 in 10 will flop to 10% of prediction. We can't predict which."

## When to Update This File

Re-validate against `references/platform-specs.md` every 6 months. Platform algorithms shift; the multipliers above are estimates, not constants.
