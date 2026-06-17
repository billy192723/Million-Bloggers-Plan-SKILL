---
type: platform-dashboard-template
template_for: 视频号-platform-dashboard
output_path: 博主计划/国内/视频号/06-数据看板.md
used_by: /onboard
status: empty
---

# 视频号 数据看板(模板)

## 周度数据

| 周 | 日期范围 | 发布数 | 总播放 | 平均播放 | 点赞 | 转发 | 新增粉丝 | 加微信 | 变现 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|
| W0 | 启动周 | 0 | 0 | - | 0 | 0 | 0 | 0 | ¥0 |  |

## 累计

- 总发布: 0
- 总播放: 0
- 当前粉丝: 0
- 私域好友: 0
- 累计变现: ¥0

## 校准记录

| 校准日期 | 样本数 | 校准系数 | 备注 |
|---|---|---|---|
| - | 0 | 1.0 | 初始 |

## Dataview

```dataview
TABLE date, topic, predicted_views, actual_views, prediction_confidence
FROM "博主计划/国内/视频号/04-内容卡"
WHERE status = "published"
SORT date DESC
LIMIT 20
```
