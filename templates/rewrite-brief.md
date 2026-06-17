---
type: template
template_for: rewrite-brief
output_path: "appends to: 博主计划/{region}/{platform}/04-内容卡/{card_id}-rewrite.md"
used_by: /rewrite (R3)
notes: When /daily generates one idea with multi-platform package, the skill creates ONE card per platform (not one card with all platforms). Cross-reference via `related_cards` frontmatter. This keeps each platform's data dashboard clean.
---
# R3 脚本改写器

> **零外部 API**(用 SKILL 自身 LLM,即 Hermes 当前对话模型)
> 同一 idea 改写为不同平台格式

## 触发

| 命令 | 行为 |
|---|---|
| `/rewrite <card>` | 智能改写:为该卡片所有平台生成改写版 |
| `/rewrite <card> --platform=抖音` | 改写为单一平台格式 |
| `/rewrite <card> --style=轻松` | 指定风格(轻松/严肃/搞笑/专业) |

## 改写 Prompt 模板(给 LLM 用)

### 系统提示

```
你是 [原 Niche] 领域的专业内容改写专家。
你的任务:把 [原平台] 的内容改写为 [目标平台] 的原生格式,保持核心 idea 和 hook 不变,但格式/节奏/CTA 全部按目标平台原生。

[目标平台] 规范:
{platform_specs}

输出要求:
- 不改变核心 idea
- 保持原 hook 强度
- 平台原生格式(时长/字数/分镜/标签)
- 给出 2 个版本(版本 A 保守、版本 B 大胆)
- 标注与原版的差异
```

### 用户提示

```
原内容卡信息:
- 主题: {topic}
- 原始平台: {source_platform}
- 原始时长/字数: {source_length}
- Hook: {hook}
- 核心 3 个要点: {main_points}
- 目标受众: {audience}
- 原始预测流量: {predicted_views}

请改写为 [{target_platform}] 格式,长度 {target_length},风格 {style}。
```

## 平台改写规则(用 SKILL 自带的 references/platform-specs.md 数据)

| 原 → 目标 | 关键变化 |
|---|---|
| 小红书 → 抖音 | 9 图 → 30s 竖屏 / 钩子压缩 / 字幕加重 |
| 小红书 → B站 | 9 图 → 8min 视频 / 加录屏分镜 / 加章节 |
| 抖音 → YouTube | 30s → 8min 扩展 / 加 context / 英文翻译 |
| 公众号 → 视频号 | 1500 字 → 1-3min 口播 / 改第一人称 |
| X → 公众号 | 英文 → 中文 / 去掉 carousel 概念 / 加金句 |
| 任何 → TikTok | 30-60s 竖屏 / 英文 / 强 visual hook |
| 任何 → Instagram | Reels 或 carousel / 美观优先 |

## 输出格式(改写后的内容卡增量)

```markdown
---
type: rewrite
source_card: "[[{original_card_id}]]"
target_platform: {platform}
style: {style}
rewritten_at: {date}
status: draft
---

# 改写:{topic} → {platform}

## 与原版的差异

| 维度 | 原版 | 改写版 |
|---|---|---|
| 时长 | X | Y |
| 钩子 | X | Y |
| 结构 | X | Y |
| CTA | X | Y |

## 版本 A(保守)

[完整脚本/正文]

## 版本 B(大胆)

[完整脚本/正文]

## 推荐

- 用 A 还是 B: [根据 X 选]
- 预测流量: [范围]
```

## 改写后怎么放

- 写到对应平台的 `04-内容卡/` 下,文件名 `{date}-{card_id}-rewrite-{platform}.md`
- 用 Obsidian `[[wikilink]]` 反链原卡,实现内容追溯
- 在原卡 frontmatter 加 `related_cards: ["[[{rewrite_id}]]"]`

## Common Pitfalls

1. **改写失去灵魂**:LLM 改写太"安全",把所有锐角磨平。提示词要强调"保持原 hook 强度"。
2. **平台不熟**:LLM 对 抖音/B站 视频分镜的节奏把握不准。让它在改写前先输出"我理解的 [平台] 原生格式是...",用户确认。
3. **中英混用**:YouTube/TikTok 改写要明确要求全英文。中文 → 英文翻译 + 改写是两件事,质量要分开看。
4. **过度改写**:有时原版已经够好,改写后变差。SKILL 应该先问"原版在 [目标平台] 格式适配度评分",高分就不建议改。

## 改写质量评分(LLM 自评,1-5)

| 维度 | 评分点 |
|---|---|
| 钩子强度 | 3 秒内能否抓住注意力 |
| 信息密度 | 单位时间内的有效信息量 |
| 平台原生度 | 看着像不像该平台原生内容 |
| CTA 自然度 | CTA 是不是硬塞的 |
| 独特性 | 改写后是否还保留创作者个人风格 |

总分 ≥ 18/25 才推荐使用改写版。
