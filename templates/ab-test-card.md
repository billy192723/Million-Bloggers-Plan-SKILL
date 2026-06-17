---
type: template
template_for: ab-test-card
output_path: 博主计划/{region}/{platform}/04-内容卡/ab/{date}-{topic_slug}-A.md
                 博主计划/{region}/{platform}/04-内容卡/ab/{date}-{topic_slug}-B.md
used_by: /ab-test (R5)
---

# R5 A/B 测试框架

> **零外部 API**。纯 SKILL 逻辑 + Obsidian frontmatter 跟踪。
> 同一 idea 多个钩子 → 发布 → 自动算胜出。

## 触发

```
/ab-test <idea> --platform=小红书 --variants=2
/ab-test <idea> --platform=小红书 --variants=3 --auto-publish
```

## 工作流

1. SKILL 基于同一 idea 生成 N 个 hook 变体(2-3 个)
2. 每变体写 1 张 A/B 测试卡,frontmatter 标记 `ab_group: "{group_id}"`
3. 用户发布各版本
4. 24h/7d 后用户回填 `actual_views` + `actual_engagement_rate`
5. SKILL 自动算出胜出版本,写入 `ab_results` frontmatter

## A/B 测试卡模板(每个变体 1 张)

```markdown
---
type: ab-test-card
date: {date}
topic: {topic}
niche: {niche}
platform: {platform}
ab_group: "{group_id}"          # 同一 group 下的卡都共享
ab_variant: "A"                  # A / B / C
ab_hypothesis: "数字钩子 vs 痛点钩子,谁更能拉 CTR"
predicted_views: {range}
predicted_engagement_rate: {range}
prediction_confidence: low
status: draft
actual_views: null
actual_engagement_rate: null
ab_result: null                  # "winner" | "loser" | "tie"
---

# A/B #{group_id} - 变体 {variant}

## 假设

{本次测试想验证什么?例如:}
- A 假设: 数字钩子 (3 个工具我砍到 1 个) 比身份钩子 (作为 5 年老 XX) 拉高 30% 完播
- B 假设: 痛点开场 (你是不是也 XX) 比反差开场 (5 个工具我砍到 1 个) 拉高 20% 互动

## 变体内容

### 钩子

{variant_hook}

### 正文/脚本(简短)

{body}

### 发布设置

- 发布时段: {time}
- 标签: {tags}
- 封面: {thumbnail_strategy}

## 24h 后回填

```yaml
actual_views: ?
actual_engagement_rate: ?
actual_完播率: ?   # 视频专属
```

## 7d 后评估

- winner: ?
- loser: ?
- 关键发现: ?
```

## A/B 结果自动评估(`scripts/ab-test-tracker.py`)

```python
"""
ab-test-tracker.py - 读所有 ab_test_card,算胜出

用法:
  python ab-test-tracker.py --platform=小红书
  python ab-test-tracker.py --group=2026-06-17-claude45
"""
```

伪代码:

```python
def evaluate_group(group_id):
    cards = load_cards_by_group(group_id)
    if not cards or any(c.actual_views is None for c in cards):
        return "pending: missing actuals"

    # 排名
    ranked = sorted(cards, key=lambda c: c.actual_views, reverse=True)
    winner = ranked[0]
    loser = ranked[-1]

    # 计算 winner 比 loser 强多少
    lift = (winner.actual_views - loser.actual_views) / loser.actual_views
    lift_pct = f"+{lift*100:.1f}%"

    # 显著性:简单经验法则
    # 2 变体, 流量差 ≥30% 才算明显;3 变体 ≥50%
    threshold = 0.3 if len(cards) == 2 else 0.5
    significant = lift >= threshold

    return {
        "winner": winner.ab_variant,
        "loser": loser.ab_variant,
        "lift": lift_pct,
        "significant": significant,
        "interpretation": (
            f"显著胜出" if significant else "差异不显著,需更多数据"
        ),
    }
```

## A/B 测试最佳实践

| 规则 | 说明 |
|---|---|
| **每次只测 1 个变量** | 钩子 OR 封面 OR 标题,不要同时改 2 个 |
| **同时段发布** | 24h 内相隔 6h 内发布,排除时段干扰 |
| **同账号** | 不要换账号,算法权重不同 |
| **样本量** | 每个变体至少 1000 播放才有意义 |
| **测试不超过 3 个变体** | 超过 3 个分流严重,结果噪音大 |
| **记录假设** | 测试前先写"我假设 X 比 Y 强,因为 Z",事后复盘 |

## 常见测试维度

- **钩子类型**:数字 vs 痛点 vs 身份 vs 反差
- **封面风格**:大字 vs 人物 vs 视觉冲击
- **标题结构**:陈述 vs 疑问 vs 命令
- **视频节奏**:快切 vs 慢节奏
- **CTA 位置**:结尾 vs 中间 vs 全文多次
- **长度**:30s vs 60s vs 3min

## 跨周期复用

每完成 5-10 组 A/B 测试,SKILL 总结:
- 哪个钩子类型在 [你的赛道] 最有效
- 哪个封面风格 CTR 最高
- 哪些假设被反复证伪(下次别用)

把结论写入 `_全局/00-总档案.md` 的"历史偏好"段,影响后续自动生成。
