---
type: template
template_for: inspiration-pool
output_path: 博主计划/_全局/06-灵感库.md
used_by: /inspire (R11)
---

# R11 灵感库

> **零 API**。SKILL 内部 LLM 帮用户整理 + 复用灵感。
> 随手记的灵感自动被 `/daily` 关联到热点。

## 触发

```
/inspire add <text>           # 加 1 条灵感
/inspire list                 # 列出所有
/inspire list --unused        # 还没用过的
/inspire link <id>            # 关联到今天的内容卡
```

## 数据模型

每条灵感是一行 frontmatter,带 metadata:

```yaml
---
type: inspiration
id: INS-2026-06-17-001
created: 2026-06-17
content: "对比测试 5 个 AI 写作工具的实际工作流"
source: "看到差评君的视频"
tags: [AI工具, 写作, 对比]
niche: AI工具评测
status: unused         # unused / queued / used
used_in_card: null     # 用了的话填内容卡 ID
related_trend: null    # 关联热点
priority: 3            # 1-5
---
```

## Obsidian 渲染

`06-灵感库.md` 是汇总页,每条灵感按状态分组:

```markdown
## 🆕 未使用(R11 候选)

- INS-2026-06-17-001 [AI工具, 写作] — 对比测试 5 个 AI 写作工具的实际工作流
- INS-2026-06-15-003 [副业] — 整理一份"副业可行性评估表"

## 📅 已排期

- INS-2026-06-10-002 [美妆] — 油皮夏季不脱妆的 5 个 tips

## ✅ 已使用

- INS-2026-06-01-001 [AI工具] — Claude 4.5 砍 5 工具 (used in: 2026-06-17-001)
```

## `/daily` 自动关联逻辑

`/daily` 跑时,SKILL:
1. 拉 `status=unused` 的所有灵感
2. 拉今日热点
3. 让 LLM 判断哪些灵感 + 哪些热点可以结合
4. 匹配上的灵感:`status: unused → queued`,写入"今日内容卡候选"

输出示例:

```
📌 灵感库 + 热点匹配 (3 个)

1. INS-2026-06-15-003 [副业可行性评估] 
   × 热点: 「副业成功率」搜索 +200%
   → 建议: 写一篇"5 个常见副业,3 个月存活率"卡片

2. INS-2026-06-12-001 [AI 写作工具横评] 
   × 热点: Claude 4.5 发布
   → 建议: 把横评升级,加入 Claude 4.5

3. INS-2026-06-10-005 [油皮化妆] 
   × 无匹配热点
   → 跳过(可下周再看)
```

## 灵感来源

`/inspire add` 支持:
- 直接文字
- 引用 Obsidian 笔记(wikilink)
- 引用 URL(自动抓标题)
- 引用图片路径(用户手记白板)

## 灵感去重

加灵感时 SKILL 自动检查:
- 文本相似度(已有灵感 80% 相似 → 提示合并)
- 主题相似(同 niche 同方向 → 提示是否一起做)
- 时间衰减(60 天没用过 → 降低优先级)

## 灵感评分维度

LLM 每次加灵感时给 1-5 分:

| 维度 | 评分 |
|---|---|
| 时效性 | 1=永久适用, 5=48h 内必须做 |
| 搜索潜力 | 1=没人搜, 5=正在涨 |
| 制作成本 | 1=5 分钟, 5=需要 1 天 |
| 你的能力匹配 | 1=不会, 5=你最擅长的 |
| 差异化 | 1=烂大街, 5=只有你能做 |

总分 ≥ 18/25 标"高潜力",SKILL 优先用。

## 归档策略

`status=used` 的灵感保留 90 天后移到 `_归档/`,保留可查但不参与匹配。

## Common Pitfalls

1. **灵感不写就忘**:加 SKILL 的关键意义。`/inspire add` 应该 ≤ 10 秒完成。
2. **灵感不分类**:用 tags + niche 才能复用。
3. **灵感太多不收敛**:每月 50+ 灵感但只用 5 个 → 加评分机制,优先用高潜力。
4. **用了不标记**:用了不更新 `status` → 永远在 unused 列表里,容易重复。
