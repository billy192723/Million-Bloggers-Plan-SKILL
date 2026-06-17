---
type: platform-dashboard-template
template_for: 公众号-platform-dashboard
output_path: 博主计划/国内/公众号/06-数据看板.md
used_by: /onboard
status: empty
---

# 公众号 数据看板(模板)

## 周度数据

| 周 | 日期范围 | 发布数 | 总阅读 | 平均阅读 | 打开率 | 在看率 | 完读率 | 新增关注 | 商单收入 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|
| W0 | 启动周 | 0 | 0 | - | - | - | - | 0 | ¥0 |  |

## 累计

- 总发布: 0
- 总阅读: 0
- 当前关注: 0
- 累计变现: ¥0

## 校准记录

| 校准日期 | 样本数 | 校准系数 | 备注 |
|---|---|---|---|
| - | 0 | 1.0 | 初始 |

## Dataview

```dataview
TABLE date, topic, predicted_views, actual_views, prediction_confidence
FROM "博主计划/国内/公众号/04-内容卡"
WHERE status = "published"
SORT date DESC
LIMIT 20
```
