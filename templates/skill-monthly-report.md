---
type: template
template_for: skill-monthly-report
output_path: 博主计划/05-周复盘/monthly/{YYYY-MM}.md
used_by: /monthly (R10)
---

# R10 SKILL 自检月报

> **零 API**。读 Obsidian vault + 用 SKILL 自身 LLM 总结。
> 每月末自动跑,评估 SKILL 是否真的帮到了用户。

## 触发

```
/monthly
/monthly --month=2026-06
```

## 评估维度

| 维度 | 数据来源 | 评估问题 |
|---|---|---|
| **命中率** | `04-内容卡/` 中 `actual_views >= predicted_views_low` 的比例 | 预测准不准? |
| **执行率** | `status="draft"` 中按时发布比例 | 计划执行如何? |
| **涨粉速度** | 各平台 `06-数据看板.md` 的"新增粉丝" | SKILL 是否帮你涨粉? |
| **变现率** | `06-数据看板.md` 的"商单收入" | SKILL 是否帮你赚钱? |
| **内容质量** | 互动率中位数 vs niche benchmark | 内容质量是否在提升? |
| **A/B 进展** | `ab-test-card` 数量 + 显著性比例 | 是否有数据驱动决策? |
| **跨平台决策** | `cross-platform-compare` 累计 | 是否在向高 ROI 平台迁移? |

## 月报模板

```markdown
---
type: skill-monthly-report
month: {YYYY-MM}
generated_at: {date}
status: draft
---

# 📊 SKILL 自检月报:{YYYY-MM}

## 总览

| 指标 | 本月 | 上月 | 变化 |
|---|---|---|---|
| 发布条数 | 24 | 18 | +33% ↑ |
| 总播放 | 145,000 | 89,000 | +63% ↑ |
| 新增粉丝 | +1,250 | +780 | +60% ↑ |
| 总互动率(中位) | 5.8% | 4.2% | +1.6pp ↑ |
| 变现 | ¥320 | ¥0 | +¥320 ↑ |
| SKILL 生成的卡 | 32 | 22 | +45% ↑ |
| 命中率(实际 ≥ 预测下界) | 41% | 28% | +13pp ↑ |

## 平台分布

| 平台 | 发布 | 总播放 | 涨粉 | 互动率 | 变现 | ROI 评分 |
|---|---|---|---|---|---|---|
| 小红书 | 14 | 89,000 | +820 | 5.5% | ¥220 | A |
| 抖音 | 6 | 32,000 | +280 | 4.1% | ¥100 | B+ |
| B站 | 3 | 18,000 | +120 | 7.2% | ¥0 | B+ |
| YouTube | 1 | 6,000 | +30 | 5.8% | ¥0 | B- |

## 预测精度

| 区间 | 命中 | 偏多 | 偏少 | 命中率 |
|---|---|---|---|---|
| 预测 0-1000 | 6 | 3 | 2 | 55% |
| 预测 1000-5000 | 8 | 4 | 1 | 62% |
| 预测 5000-10000 | 5 | 2 | 1 | 63% |
| 预测 10000+ | 2 | 0 | 1 | 67% |
| **总计** | **21** | **9** | **5** | **60%** |

校准建议:下次预测乘以 0.9(略偏多)。

## A/B 测试累计

- 完成的 A/B 组: 5
- 显著胜出: 2 (40%)
- 主要发现:
  - 数字钩子完胜身份钩子(3/3 次)
  - 痛点封面比大字封面的 CTR 高 28%
  - 视频 30s 比 60s 完播率高 40%

## 跨平台决策累计

- 完成对比: 3 组
- 主要发现:
  - 小红书 ROI 持续 A 级 → 加投
  - YouTube 前 3 个月 ROI 模糊 → 保留观察
  - B站互动质量高但制作成本高 → 保持 1 条/周

## Top 3 内容

1. **{{topic}}** (小红书, 8.5w 播放, 互动 7.2%)
2. **{{topic}}** (B站, 2.3w 播放, 完播 65%)
3. **{{topic}}** (抖音, 1.8w 播放, 完播 78%)

## Bottom 3 内容(失败案例)

1. **{{topic}}** (播放 50, 互动 0.5%) — 原因: 时段不对 + 钩子弱
2. ...

## SKILL 使用频率

- /daily 调用: 28 次
- /onboard 重新跑: 1 次(改了 niche)
- A/B 测试触发: 5 次
- /review 触发: 4 次

## 下月建议

1. **继续加投小红书**:连续 2 月 A 级,产能提到 70%
2. **暂停抖音**:连续 1 月 B+ 级,投入回报不符
3. **B站加大中视频产出**:互动质量最高,7% 是 niche top
4. **A/B 测试钩子**:数据已支持"数字钩子"作为默认,可降为单卡直发
5. **预测模型校准**:乘 0.9,3 个月后重评

## 自我评估

- 整体方向: ⭐⭐⭐⭐ 进展良好
- 内容质量: ⭐⭐⭐ 稳定提升
- 涨粉速度: ⭐⭐⭐⭐ 超预期
- 变现: ⭐⭐ 起步阶段,符合 6 个月计划

下月重点:变现路径打磨(从涨粉到赚钱的转化)。
```

## 脚本实现(`scripts/skill-report.py`)

伪代码:

```python
"""
skill-report.py - 读 Obsidian vault,生成月报

用法:
  python skill-report.py --month=2026-06
  python skill-report.py                # 默认上个月
"""
```

```python
import re
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import date, timedelta

VAULT = Path("E:/知识库/博主计划")

def load_cards():
    cards = []
    for md in VAULT.rglob("04-内容卡/*.md"):
        meta = parse_frontmatter(md)
        if meta.get("type") == "daily-content-card":
            meta["_path"] = md
            cards.append(meta)
    return cards

def main(month):
    cards = load_cards()
    month_cards = [c for c in cards if c.get("date", "").startswith(month)]

    # 总览统计
    total_published = sum(1 for c in month_cards if c.get("status") == "published")
    total_views = sum(c.get("actual_views", 0) or 0 for c in month_cards)
    total_follows = sum_from_dashboards(month)  # 从 06-数据看板.md 读

    # 命中率
    hit = sum(1 for c in month_cards
              if c.get("actual_views") and c.get("predicted_views")
              and c["actual_views"] >= parse_range_low(c["predicted_views"]))

    # 按平台分组
    by_platform = group_by(month_cards, "platform")

    # 渲染模板
    template = Path("templates/skill-monthly-report.md").read_text(encoding="utf-8")
    # 替换占位符 ...
    return render(template, stats)
```

## 自我校准

SKILL 用了 3 个月以上,月报本身要校准:
- 预测精度趋势: 升 / 降 / 稳
- 内容质量趋势: 升 / 降 / 稳
- 涨粉速度趋势
- ROI 趋势

如果某指标连续 3 月下降,SKILL 在月报里给出"SOS 警告",提示需要大方向调整。

## Common Pitfalls

1. **数据不全**:用户没回填 actual_views,月报空着。SKILL 应在 `/monthly` 前先检查数据完整度。
2. **时间窗口错位**:6 月月报应包含 6 月发布的内容,而不是 6 月回填的数据。
3. **过度乐观**:前 3 个月数据少,月报波动大,要提醒"样本不足,谨慎解读"。
4. **没有行动**:月报如果只是数字堆砌,没用。要有"下月建议"且可执行。
