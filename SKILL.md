---
name: creator-incubator
description: "Use when the user wants to become a content creator, influencer, or 'million-follower blogger' on Chinese (小红书/抖音/B站/视频号/公众号) or international (YouTube/TikTok/Instagram/X) platforms. Triggered by phrases like '做博主', '成为网红', '孵化账号', 'I want to be an influencer', 'recommend a niche for me', 'give me a content plan', '今天该拍什么'. Provides 14 commands covering onboarding, daily content generation, weekly review, multi-platform rewrite, A/B testing, todo management, ROI tracking, monthly self-check, inspiration pool, failure logging, comment replies, holiday calendar, and IM push. Zero external API dependencies — works with any LLM agent that can read/write files."
version: 2.1.0
author: billy192723
license: MIT
platforms: [linux, macos, windows]
homepage: https://github.com/billy192723/Million-Bloggers-Plan-SKILL
---

# Creator Incubator

## Overview

This skill is a **personal creator-incubation co-pilot**. It takes someone from "I have no idea what to post" to a structured 6-month launch plan, and then runs a daily content loop that:

1. Fetches today's trending topics from the user's target platforms (8 supported: 小红书, 抖音, B站, 视频号, 公众号, YouTube, TikTok, Instagram, X).
2. Cross-references trends with the user's niche + past content performance.
3. Outputs **platform-specific content packages** (小红书 card vs 抖音 script vs B站 long video vs YouTube outline, etc.) — one idea, multiple shapes.
4. **Predicts traffic and engagement** before the user commits to filming (range, not promise).
5. Stores everything in a markdown notes folder so the user has a permanent record of what to do, why, and what came out.

Three runnable modes: `/onboard` (one-time), `/daily` (recurring), `/review` (weekly).

## When to Use

- User says they want to be a creator / 博主 / 网红 / influencer and need direction.
- User has a skill/hobby and wants to know which niche fits them.
- User has an account but no idea what to post next.
- User wants a 30/60/90-day launch calendar with concrete daily actions.
- User wants to repurpose one idea across multiple platforms automatically.
- User wants a traffic forecast before investing time in filming.

**Don't use for:**

- Generic marketing/marketing-skills questions (delegate to `coreyhaines31/marketingskills` style resources).
- Posting automation / bots / fake engagement (this skill is about *what* to post, not *how* to game the algorithm).
- Account takeover / hacking / private API scraping. The skill uses public web data only.
- Single one-off posts (no recurring need → just write the post directly).

## Quick Start

| Command | When | What happens |
|---|---|---|
| `/onboard` | First time | 6-8 question interview → niche recommendations with 3 real creator examples → 6-month milestone plan written to Obsidian |
| `/daily` | Each morning | Fetch trends from target platforms → cross-reference with niche → emit 3-5 content cards with multi-platform packages + traffic forecasts |
| `/review` | Weekly | User pastes last week's actuals (views/likes/comments/follows) → skill recomputes what's working → adjusts plan |
| `/push` (v2.0) | Manual | Push latest card summary to all enabled IM channels (DingTalk/Feishu/WeCom/WeChat via Server酱) |

### v2.1 — 10 轮扩展命令(零 API 依赖)

| Command | When | What happens | Round |
|---|---|---|---|
| `/calendar` | Anytime | Show monthly content calendar (Dataview JS, all platforms) | R1 |
| `/rewrite <card> --platform=X` | When adapting one idea to a different platform | LLM rewrites content into target platform's native format (2 versions) | R3 |
| `/ab-test <idea> --variants=N` | Testing different hooks/cover/titles | Generate N variants → A/B cards published → auto-evaluate winner/loser | R5 |
| `/todo` | Daily | Show today's + next 3 days' todos aggregated from all platforms | R8 |
| `/xplatform <idea> --platforms=A,B` | Picking the best platform | Track same idea across 2+ platforms → 7-day ROI comparison | R9 |
| `/monthly` | End of month | SKILL self-check: hit rate, growth speed, ROI, A/B progress | R10 |
| `/inspire add <text>` | Anytime user has an idea | Add to inspiration pool; `/daily` will auto-match with trends | R11 |
| `/failure add <card>` | When a post flops | Diagnose + categorize failure + write lesson; `/daily` auto-avoids | R12 |
| `/reply <comment> --tone=X` | Replying to a comment | LLM drafts a reply from 6-category playbook (感谢/提问/质疑/推销/故事/互动) | R13 |
| `/holiday` | Daily (auto in `/daily`) | Check upcoming holidays/events in next 7 days → suggest timely content | R14 |
All four commands write files into the user's notes folder. The skill **does not auto-publish anything** — it produces a plan + drafts. Publishing is the user's call.

## Note Storage (Markdown-based, agent-agnostic)

This skill writes content cards, plans, and reports as **plain Markdown files with YAML frontmatter**. You can store them anywhere — the default design assumes an Obsidian vault, but it works equally well with:

- **Obsidian vault** (best UX — Dataview queries, backlinks, daily notes)
- **Plain folder** (just files on disk)
- **Notion** (via the Notion API or sync tool)
- **Logseq** (also markdown + YAML)
- **Any markdown editor** (VS Code, Typora, etc.)

Default layout (created on first `/onboard`):

```
your-notes-folder/
├── README.md                       # Entry point, explains structure
├── _global/                        # Cross-platform shared configs
│   ├── 00-profile.md               # User profile (8-question interview, fill once)
│   ├── 01-niche.md                 # Main niche + cross-platform content mix
│   ├── 02-roadmap.md               # 6-month cross-platform milestones
│   ├── 03-calendar.md              # Dataview monthly calendar
│   ├── 03a-todo.md                 # Daily ToDo aggregation
│   ├── 04-push-config.md           # IM channel config (optional)
│   ├── 05-xplatform-compare.md     # Cross-platform ROI comparison
│   ├── 06-inspiration.md           # Inspiration pool
│   ├── 07-failures.md              # Failure log
│   ├── 08-comments.md              # Comment reply playbook
│   └── 09-holidays.md              # Holiday calendar reference
├── CN/                             # Chinese platforms
│   ├── xiaohongshu/                # Each platform = self-contained "incubation unit"
│   │   ├── 00-profile.md           # Platform-specific config (visual, posting, tags)
│   │   ├── 01-direction.md         # Platform-specific sub-niche
│   │   ├── 02-roadmap.md           # 6-month plan for THIS platform
│   │   ├── 03-trends/              # Daily trend logs (per-platform raw data)
│   │   ├── 04-cards/               # Per-idea content cards
│   │   ├── 05-weekly/              # Weekly retro
│   │   └── 06-dashboard.md         # Cross-week metrics table
│   ├── douyin/        (same structure)
│   ├── bilibili/      (same structure)
│   ├── wechat-channels/ (same structure)
│   └── wechat-mp/     (same structure)
└── INTL/
    ├── youtube/     (same structure)
    ├── tiktok/      (same structure)
    ├── instagram/   (same structure)
    └── x/           (same structure)
```

**Note on naming**: the original was `博主计划/_全局/国内/小红书/...` (Chinese folder names). For international use, English folder names (`Million-Bloggers-Plan-SKILL/_global/CN/xiaohongshu/...`) work better with non-Chinese tools. The skill is folder-name agnostic — change to whatever your toolchain supports.

## Core Workflow — `/onboard`

1. **Ask 6-8 questions in one batch** (not one-at-a-time, user prefers batch):
   - 每天能投入多少时间?(<1h / 1-2h / 2-4h / >4h)
   - 有哪些技能 / 经验 / 兴趣?(开放式,可列多个)
   - 想露脸吗?(是 / 否 / 露手可以)
   - 有哪些设备?(手机 / 麦克风 / 灯光 / 剪辑软件)
   - 优先做国内还是国外?(国内 / 国外 / 都做)
   - 目标变现路径?(带货 / 广告 / 知识付费 / 私域 / 还没想)
   - 你欣赏的 1-3 个博主是谁?为什么?
   - 你最不想做哪类内容?
2. **Cross-reference with `references/niche-templates.md`** — pick 3-5 niches that overlap user's skills, time, equipment, and stated preferences.
3. **For each niche**, surface 1-2 real creator examples (search via `web_search` if needed — only well-known accounts the user can verify).
4. **Build comparison matrix**: niche × (skill fit / time cost / monetization speed / competition / scale ceiling), scored 1-5.
5. **User picks 1 (or 2)** → write `01-方向推荐.md` + `02-孵化路径.md` to Obsidian.
6. **6-month plan** has these phases (default, adjustable):
   - **M1 (Week 1-4): 基建期** — 账号定位 / 头像 / 简介 / 视觉统一 / 拍 8-12 条"找手感"内容
   - **M2 (Week 5-8): 冷启动期** — 找爆款公式 / 测试 3 种钩子 / 目标 1k 粉
   - **M3 (Week 9-12): 第一个爆款** — 拆解 10 个同方向爆款 / 复制结构 / 目标 1 条 10w+ 或单条 1k+ 赞
   - **M4 (Week 13-18): 稳定输出** — 周更 ≥ 3 条 / 互动率 ≥ 5% / 目标 1w 粉
   - **M5 (Week 19-22): 变现试探** — 试接 1 单 / 试挂车 / 试开私域
   - **M6 (Week 23-26): 放大** — 选最有效平台加大投入 / 复制到次平台

## Core Workflow — `/daily`

1. **Read user profile** (`00-档案.md`) + last 14 days of `04-内容卡/` to avoid repeating topics.
2. **Fetch trends** for each target platform the user has selected:
   - Use `web_search` with site filters: `site:xiaohongshu.com`, `site:douyin.com`, `site:bilibili.com`, `site:youtube.com`, etc.
   - For ranking: search `[niche] 热门` / `[niche] trending` / `[niche] viral` and parse top results.
   - Budget: 3-5 searches per platform, max 30 searches total to keep latency sane.
3. **Score trends** against the user's niche:
   - Relevance (does it match their skill/interests?)
   - Heat (search-result count, recency, engagement signals)
   - Differentiation (can they add a unique angle?)
4. **Emit 3-5 content cards** (see `templates/daily-content-card.md`). Each card includes:
   - **Trend context**: what is hot, why now
   - **Platform package**: one main + at least 2 platform adaptations
   - **Hook options**: 3 alternative openings, each with predicted retention
   - **Filming checklist**: what to record (镜头清单)
   - **Traffic & engagement prediction** (see below)
   - **Publish time recommendation**
5. **Write to Obsidian** as individual cards in `04-内容卡/YYYY-MM-DD-NNN-slug.md` + a rollup at `03-热点日志/YYYY-MM-DD.md`.

## Core Workflow — `/push` (v2.0)

**Manual trigger only** (per user choice 4B — no cron auto-push). When the user says `/push`, the skill dispatches the latest un-pushed content card to all enabled IM channels.

### Subcommands

| Command | What it does |
|---|---|
| `/push` | Push the latest un-pushed content card to all enabled channels |
| `/push test` | Send a test message (channel connectivity check) |
| `/push card <path>` | Push a specific card file |
| `/push --dry-run` | Render the message but don't send (preview) |

### Channel support

4 channels supported. Each independently enabled in `_全局/04-推送配置.md`:

| Channel | Personal? | Setup time | Service |
|---|---|---|---|
| 钉钉 (DingTalk) | ✅ | 5 min | Custom robot webhook |
| 飞书 (Feishu) | ⚠️ needs enterprise | 15 min | Custom robot webhook OR app API |
| 企业微信 (WeCom) | ⚠️ needs enterprise | 10 min | Group robot webhook |
| 微信个人 | ✅ | 5 min | Server酱 OR WxPusher (3rd-party) |

Full setup tutorial: `references/push-channels.md`.

### How it works

1. Read `_全局/04-推送配置.md` → parse channel config
2. Read the target content card (frontmatter only) → render summary
3. For each enabled channel, call the corresponding sender in `scripts/push-dispatcher.py`
4. Return per-channel success/fail summary

### Message format (per choice 3A: summary + link)

Each push is a **summary card** with a link back to the Obsidian card. The link uses `file://` URI for local Obsidian, so the user can click from phone → desktop Obsidian (assuming Obsidian sync is configured).

### Webhook security

- Treat webhook URLs as passwords. Never commit.
- Default: all channels `enabled: false`.
- The skill does NOT auto-push (per choice 4B), so no accidental leak.
- If user pastes webhook in chat, the skill warns (token-leak safety rule).

### Future iterations (not implemented)

- Cron auto-push: easy to add (`cronjob` skill + daily 7:30 trigger)
- 2-way: user clicks "已选" button in IM → updates card `status` field
- Multi-card digest: weekly rollup instead of daily single card

## Core Workflow — `/calendar` (R1)

**Trigger**: `/calendar` or just opening `_全局/03-内容日历.md` in Obsidian.

**Behavior**:
- Dataview JS reads all `04-内容卡/` across platforms
- Renders a month calendar with each day's content cards (color-coded by platform)
- Shows monthly summary: planned vs published, platform distribution
- Highlights overdue items (date < today, status=draft)

**Output**: Visual calendar in Obsidian (no separate file written; the file is the source of truth).

**Template**: `templates/content-calendar.md` (the Dataview JS code is embedded in the template).

**Zero API**: ✅ Pure template + Dataview plugin.

## Core Workflow — `/rewrite` (R3)

**Trigger**: `/rewrite <card_path> --platform=抖音 --style=轻松`

**Behavior**:
- SKILL reads source card's `topic`, `hook`, `main_points`
- Prompts LLM (using SKILL's own LLM, no external API) to rewrite for target platform
- Outputs 2 versions (A: conservative, B: bold) with diff explanation
- Writes a new file: `{region}/{platform}/04-内容卡/{date}-{card_id}-rewrite.md`
- Cross-links source and rewrite via Obsidian wikilinks

**Output**: New rewrite card in target platform directory.

**Template**: `templates/rewrite-brief.md` (the LLM prompt is embedded).

**Zero API**: ✅ Uses the agent's own LLM in the conversation.

## Core Workflow — `/ab-test` (R5)

**Trigger**: `/ab-test <idea> --platform=小红书 --variants=2`

**Behavior**:
- SKILL generates N hook/cover/title variants for the same idea
- Writes N A/B cards under `{region}/{platform}/04-内容卡/ab/`, all with same `ab_group` ID
- User publishes each variant
- After 24h-7d, user fills `actual_views` + `actual_engagement_rate`
- Run `python scripts/ab-test-tracker.py --platform=小红书` → auto-evaluates winner/loser, writes `ab_result` back

**Output**: Winner declared, A/B cards tagged with result.

**Scripts**: `scripts/ab-test-tracker.py` (read A/B cards, compute lift, write back).
**Template**: `templates/ab-test-card.md`.

**Zero API**: ✅ Pure logic + user-provided actuals.

## Core Workflow — `/todo` (R8)

**Trigger**: `/todo` or `/todo --week` or `/todo --platform=小红书`

**Behavior**:
- SKILL reads all `04-内容卡/` with `status=draft|filming|editing|scheduled`
- Aggregates "拍摄清单" sections via Dataview task syntax
- Groups by platform + priority
- Renders in `_全局/03-本周任务.md`

**Output**: Daily/weekly ToDo list with checkboxes (Obsidian-native task format).

**Template**: `templates/todo-list.md` (Dataview snippets).

**Zero API**: ✅ Pure template + Dataview.

## Core Workflow — `/xplatform` (R9)

**Trigger**: `/xplatform <idea> --platforms=小红书,B站` or `/xplatform <card_id>`

**Behavior**:
- SKILL marks the involved cards with shared `cross_platform_group` ID
- User publishes on each platform
- After 7d, user pastes actuals per platform
- SKILL computes ROI: 互动质量 × 涨粉效率 / 制作成本
- Outputs ranking + migration recommendations (which platform to invest in)

**Output**: Comparison table + recommendations, written to `_全局/05-跨平台对比.md`.

**Template**: `templates/cross-platform-compare.md`.

**Zero API**: ✅ Pure logic + user actuals.

## Core Workflow — `/monthly` (R10)

**Trigger**: `/monthly` or `/monthly --month=2026-06`

**Behavior**:
- Run `python scripts/skill-report.py` (or `--dry-run` for preview)
- Reads all cards + dashboards + A/B results + failure logs from the notes folder
- Computes: hit rate, growth speed, engagement trend, ROI by platform, A/B progress, cross-platform decisions
- LLM (SKILL's own) summarizes findings + next-month recommendations
- Writes to `05-周复盘/monthly/{YYYY-MM}.md`

**Output**: Monthly self-check report.

**Scripts**: `scripts/skill-report.py`.
**Template**: `templates/skill-monthly-report.md`.

**Zero API**: ✅ Pure read + LLM summary.

## Core Workflow — `/inspire` (R11)

**Trigger**: `/inspire add <text>`, `/inspire list --unused`, `/inspire link <id>`

**Behavior**:
- `add`: write a new entry in `_全局/06-灵感库.md` with metadata (tags, niche, priority)
- `list`: show unused / queued / used groups
- `link`: mark inspiration as used in a specific card

**Auto-integration with `/daily`**:
- `/daily` reads all `status=unused` inspirations
- LLM matches them with current trends
- Matched ones get `status: queued` and become today's card candidates

**Output**: Inspiration pool with auto-matching.

**Template**: `templates/inspiration-pool.md`.

**Zero API**: ✅ Pure template + SKILL LLM.

## Core Workflow — `/failure` (R12)

**Trigger**: `/failure add <card_id> --reason="..."`, `/failure list --platform=X`, `/failure patterns`

**Behavior**:
- `add`: LLM categorizes the failure (标题党/时段错/钩子弱/...), records in `_全局/07-失败案例.md`
- `list`: show recent failures by category/severity
- `patterns`: LLM summarizes recurring mistakes (e.g. "3/5 failures are 标题党")

**Auto-integration with `/daily`**:
- `/daily` reads high-severity failures before generating
- If a new card's content would trigger the same failure pattern, SKILL warns: "⚠️ 你之前 [FAIL-001] 因 X 翻车,建议改"

**Output**: Failure log + auto-avoidance.

**Template**: `templates/failure-log.md`.

**Zero API**: ✅ Pure template + SKILL LLM.

## Core Workflow — `/reply` (R13)

**Trigger**: `/reply <comment_text> --tone=友好|专业|搞笑`

**Behavior**:
- LLM reads the comment and the 6-category playbook in `templates/comment-playbook.md`
- Categorizes the comment type
- Generates 1-3 reply candidates
- Highlights the best choice + explains why

**Output**: Reply suggestion in chat (no file written; ephemeral).

**Template**: `templates/comment-playbook.md` (the playbook is the data).

**Zero API**: ✅ Pure LLM + static reference.

## Core Workflow — `/holiday` (R14)

**Trigger**: `/holiday` or auto-triggered inside `/daily`

**Behavior**:
- SKILL reads `references/holiday-calendar.md` (100+ events)
- Filters events in next 7 days
- LLM judges relevance to user's niche
- Suggests timely content themes

**Output**: Upcoming events + content ideas (printed in `/daily` output or standalone).

**Reference**: `references/holiday-calendar.md`.

**Zero API**: ✅ Static reference + SKILL LLM.

**Custom events**: `/holiday add --name="公司周年" --date=09-15 --themes=[创业,故事]`

## Cross-Command Workflows

These 10 new commands are designed to chain:

```
morning:    /daily       → 3-5 cards (with /holiday, /inspire auto-matched)
            /calendar    → see the month
            /todo        → see today's work
            /rewrite X   → adapt for another platform
            /ab-test X   → test 2 versions of one idea
midday:     /reply X     → draft a comment reply
evening:    /failure X   → log a flop if any
monthly:    /monthly     → skill self-check
            /xplatform   → migrate to best platform
            /inspire     → capture new ideas
```

## Core Workflow — `/review`

1. Ask user to paste last week's actuals: views / likes / comments / collects / follows delta per post.
2. Compute:
   - Average views vs predicted (calibration score)
   - Top 3 performing content types
   - Bottom 3 (kill-list)
   - Engagement rate trend
3. Update `06-数据看板.md` with a new week row.
4. **Recommend 3 adjustments** for next week (e.g. "double down on 工具对比", "drop 教程类", "shift 抖音发布时段").
5. Update `02-孵化路径.md` if milestone is at risk.

## Output Format — Daily Content Card

Each card is a single `.md` file. Template lives at `templates/daily-content-card.md`. Rendered example:

```markdown
---
date: 2026-06-17
card_id: 001
topic: Claude 4.5 实际替代了哪些工具
niche: AI 工具评测
platforms: [小红书, B站, YouTube]
predicted_views: 8500-18000
predicted_engagement_rate: 4.2-6.8%
status: draft
---

# Claude 4.5 实测 3 天,我砍掉了 5 个工具

## 趋势背景
- **热点**: Claude 4.5 发布,搜索指数 +340% (近 7 天)
- **平台分布**: 小红书 9.2 / 抖音 7.8 / B站 6.5
- **为什么现在**: Anthropic 刚发布 4.5,72 小时内是黄金窗口

## 拍摄清单 🎬
- [ ] 屏幕录制:Claude 4.5 vs 5 个工具的实操对比
- [ ] 真人出镜开场 3 秒(用「我刚砍掉 5 个工具」钩子)
- [ ] 桌面整理:5 个待替换工具的图标排好
- [ ] 字幕版(双语)— 国外平台用
- [ ] 封面图:左右对比 + 5 个 ❌ + "砍掉 5 工具" 大字

## 平台方案

### 小红书(主战场)
- 标题: Claude 4.5 实测 3 天,我砍掉了 5 个工具
- 开头 3 秒: "昨天 Claude 4.5 一发布,我第一件事就是..."
- 正文: 痛点 → 5 个被砍工具 → 替代工作流 → CTA 引导评论
- 标签: #AI工具 #Claude4.5 #效率神器 #自媒体工具 #AI替代
- 长度: 800-1200 字 + 9 图
- 预测流量: 8000-15000 / 互动率 4-6%

### 抖音
- 改编: 30 秒竖屏,镜头 1: 开场钩子 / 镜头 2-4: 三个工具对比 / 镜头 5: CTA
- 标题: 5 个工具被 Claude 4.5 砍掉,你能猜到几个?
- 预测流量: 15000-35000 / 互动率 3-5%(完播率是关键)

### B站
- 改编: 8-12 分钟长视频,完整录屏 + 详细对比
- 标题: Claude 4.5 实际表现 vs 营销话术|3 天深度测评
- 预测流量: 3000-8000 / 互动率 6-10%

### YouTube
- 改编: 同 B 站长视频,英文字幕 + 英文标题
- 标题: I Replaced 5 Tools With Claude 4.5 — 3-Day Test
- 预测流量: 1500-4000 / 互动率 4-7%

## 流量预估逻辑
- **基线**: 你的账号当前平均播放 2000(可调整)
- **热度加成**: Claude 4.5 是全网热点 ×3.5
- **赛道加成**: AI 工具类平均互动率 4.5%(平台中上)
- **时段加成**: 20:30 发布,小红书美妆/科技高峰段
- **修正**: 首条爆款概率 ~15%, 取中位数

## 风险
- 同名爆款已存在(博主「差评君」已发),差异化:加入"自媒体人"第一人称视角
- 时效性:72 小时后会衰减 50%,建议 24 小时内发布

## CTA 引导
- 引导评论: "你最想看我测哪个工具?评论区 1 票"
- 引导关注: "下期测 X,关注不错过"
```

## Traffic & Engagement Prediction Model

The skill does **not** claim certainty. Every prediction is a **range with explicit assumptions** the user can audit. See `references/traffic-prediction-model.md` for full math. Quick reference:

| Factor | Weight | Source |
|---|---|---|
| Account baseline (current avg views) | ×1.0 | User-reported / from past cards |
| Trend heat multiplier | ×1.0-×5.0 | web_search result count + recency |
| Niche benchmark engagement rate | +0-3pp | Per-platform benchmark in `references/platform-specs.md` |
| Time-of-day multiplier | ×0.7-×1.3 | Platform peak-hour data |
| Hook quality (LLM self-score) | ×0.8-×1.4 | First 3-second retention estimate |
| Format fit (vertical for 抖音 etc.) | ×0.9-×1.2 | Platform native format |
| Account age trust (新号惩罚) | ×0.5-×1.0 | < 1k followers |

Output: `predicted_views: [low, high]` and `predicted_engagement_rate: [low, high]%`.

The model recalibrates weekly in `/review` — once the user has ≥ 4 weeks of actuals, predictions tighten substantially.

## Platform Coverage

| Platform | Region | Format Focus | Strength | Weakness |
|---|---|---|---|---|
| 小红书 | CN | 图文 + 9 图 / 1-3 分钟短视频 | 涨粉快,女性消费力强,搜索流量稳定 | 男粉少,纯技术类天花板低 |
| 抖音 | CN | 15-60 秒竖屏 | 流量池大,破圈机会高 | 完播率压力大,长内容不适合 |
| B站 | CN | 5-20 分钟横屏长视频 | 用户黏性高,广告单价高,中长尾流量 | 起号慢,需持续输出 30+ 条 |
| 视频号 | CN | 1-3 分钟竖屏,社交分发 | 微信生态,40+ 用户多,私域转化强 | 算法推荐弱,纯公域起号难 |
| 公众号 | CN | 1500-3000 字长文 | 深度内容,长期 SEO 价值 | 打开率下降,新号无订阅基础 |
| YouTube | INTL | 8-15 分钟长视频 | 长尾流量,广告单价最高,$CPM 4-12 | 起号 3-6 个月才有可能变现 |
| TikTok | INTL | 15-90 秒竖屏 | 全球破圈,年轻用户 | 同质化严重,变现路径长 |
| Instagram | INTL | Reels + 9 图 + Stories | 视觉类/生活方式类天花板高 | 文字内容传播弱 |
| X | INTL | 短文本(≤280)+ 推文串 1/n + Quote RT + Spaces | 病毒传播最快,科技/创业/AI niche 天花板高,实时热点 | 短生命周期(18-25 分钟),需要高密度输出 |

Note: 9 platforms shown — adjust per user preference (default 4-5 max per user).

## Content Frameworks

Detailed in `references/content-frameworks.md`. Quick hooks:

- **反差钩子**: "5 个工具我砍到 1 个,3 个月后..."
- **数字钩子**: "我用 30 天试了 17 个 AI 工具,留下来 3 个"
- **身份钩子**: "作为 XX 3 年的老 XX,说句实话"
- **痛点钩子**: "你是不是也 XX ?我之前也是"
- **预言钩子**: "2026 年,这 5 个工具会消失"

Standard structure (works for 抖音/小红书/TikTok/Reels):

```
0-3 秒: 钩子 (必须打破滑动惯性)
3-15 秒: 承诺 (这视频你将得到什么)
15-50 秒: 主体 (3 个要点,每点一个例子)
50-60 秒: CTA (评论/关注/收藏)
```

## Common Pitfalls

1. **Fetching trends every time without caching.** If user runs `/daily` twice in 1 hour, the second run still costs 20-30 web searches. Solution: always read `03-热点日志/YYYY-MM-DD.md` first; only re-fetch if older than 6 hours.

2. **Confusing "trending" with "relevant".** A K-pop scandal trending on 微博 ≠ AI-tool content. Always apply the niche filter BEFORE showing user the trends; show top 3-5 most relevant, not top 3-5 most viral.

3. **Predictions without calibration.** First 4 weeks, predictions are noisy (wide range, no user data). Always show the model as "low-confidence" with a note. Tighten language after W4 when the user has 10+ data points.

4. **One platform only.** The whole point of `/daily` is the multi-platform package. If the user only does 小红书, still suggest at least 1 "stretch platform" per week (e.g. B站 or 视频号).

5. **Ignoring user's content history.** Always read the last 14 days of `04-内容卡/` to dedupe topics. Nothing kills a niche faster than 3 videos on "ChatGPT vs Claude" in 5 days.

6. **Faking the creator examples.** The niche recommendation must show real, verifiable accounts. If unsure, mark them as "similar-style example, not direct match" rather than inventing usernames.

7. **Writing Chinese-only content for international niches.** If the user picks YouTube/X as a target, all content for that platform must be English (or whatever the platform's primary language is). Check the user's language per platform in `00-档案.md`.

8. **Overwriting user's data.** `/review` and `/daily` must never edit `02-孵化路径.md` or `00-档案.md` without confirmation. Append-only by default.

9. **Forgetting the filming checklist.** The user needs a *concrete* shot list, not "make a video about X". Every card must have a 3-7 item 镜头清单.

10. **Treating the notes folder as a write-only dump.** Files must be searchable — every card has consistent frontmatter so the user can Dataview-query "show me all predicted_views > 10000 cards".

11. **Search engine anti-scraping.** Google returns CAPTCHA, DuckDuckGo HTML scraping often returns empty shells. Use this fallback chain in `/daily`:
    1. Agent's built-in `web_search` tool (if available) — preferred
    2. Bing public search (`https://www.bing.com/search?q=...`) via `browser_navigate` + parse
    3. Each platform's own discovery pages: 小红书 `https://www.xiaohongshu.com/explore` (logged-out shows curated), 微博热搜 `https://s.weibo.com/top/summary`, B站热门 `https://www.bilibili.com/v/popular/rank/all`
    4. **Last resort**: ask the user to paste 3-5 hot topics they noticed in their feed today. This is acceptable and often more accurate than scraped data.

12. **Always check the holiday calendar in `/daily`.** Reference `references/holiday-calendar.md` — events within next 7 days get auto-suggested as content themes. Skip events irrelevant to user's niche (LLM judgment).

## Verification Checklist

After every `/daily`:

- [ ] `03-热点日志/YYYY-MM-DD.md` exists with the trend raw data
- [ ] At least 3 content cards exist in `04-内容卡/`
- [ ] Each card has: frontmatter (date, card_id, topic, niche, platforms, predicted_views, predicted_engagement_rate, status) + body (trend context, filming checklist, platform packages, traffic logic, risks, CTA)
- [ ] At least 1 card has multi-platform package (3+ platform adaptations)
- [ ] Traffic predictions show assumptions, not just numbers
- [ ] No duplicate topics with last 14 days
- [ ] User's target languages are respected per platform

After every `/onboard`:

- [ ] `00-档案.md` has all 8 interview answers
- [ ] `01-方向推荐.md` has 3-5 niches with 1-2 real creator examples each
- [ ] Comparison matrix scores every niche on 5 dimensions
- [ ] `02-孵化路径.md` has 6 monthly phases with weekly milestones
- [ ] User confirmed the picked niche before files were finalized

After every `/review`:

- [ ] `06-数据看板.md` has a new row for the week
- [ ] Calibration score is computed (predicted vs actual)
- [ ] 3 specific recommendations for next week
- [ ] `02-孵化路径.md` adjusted only if milestone at risk

## One-Shot Recipes

### "I want to be a creator, but I have no idea where to start"

```
User: /onboard
Skill: [asks 8 questions in batch]
User: [answers]
Skill: [emits 3-5 niche recommendations with comparison matrix]
User: picks niche X
Skill: [writes 00-档案.md, 01-方向推荐.md, 02-孵化路径.md to Obsidian]
Skill: "Run /daily tomorrow morning to get your first content cards."
```

### "What should I post tomorrow?"

```
User: /daily
Skill: [reads 00-档案 + 02-孵化路径 + last 14 days of 04-内容卡]
Skill: [fetches trends for user's target platforms, 3-5 searches per platform]
Skill: [emits 3-5 cards to 04-内容卡/]
Skill: [rollup at 03-热点日志/]
Skill: [summary: "5 ideas ready. Top pick: card #002 (predicted 12k-25k views on 小红书)."]
```

### "I posted 3 things last week, how am I doing?"

```
User: /review
Skill: [asks user to paste actuals]
User: [pastes table]
Skill: [computes calibration, top 3, bottom 3, trend]
Skill: [updates 06-数据看板.md]
Skill: [3 recommendations]
```

### "Add YouTube to my platforms"

```
User: 把 YouTube 加进去
Skill: [updates 00-档案.md with YouTube as new target platform]
Skill: [next /daily will include YouTube packages automatically]
```

## Notes for Skill Authors

- This skill recommends Obsidian as the default notes tool (best Dataview/backlinks support), but is folder-agnostic. The agent should ask the user where to put files.
- All "predictions" must show assumptions. Never present a number as fact.
- The model is calibrated by `/review`. First 4 weeks: wide ranges, lots of caveats. After W4: tighter.
- If the user has no notes tool, ask before defaulting to a plain folder.
