# Million Bloggers Plan SKILL

> An AI agent skill that helps you become a content creator / influencer / "million-follower blogger" on Chinese and international platforms — by automating the boring parts and giving you data-driven decisions.

![Status: v2.1.0](https://img.shields.io/badge/version-2.1.0-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![API: Zero](https://img.shields.io/badge/external_API-zero-brightgreen)
![Platforms: 9](https://img.shields.io/badge/platforms-9-orange)

---

## What is this?

**Creator Incubator** is a structured, opinionated skill for any LLM-based coding agent (Claude Code, Cursor, Windsurf, OpenCode, Codex, Hermes, etc.) that turns "I want to be a content creator" into a concrete 6-month plan, then runs a daily content loop:

1. Fetches today's trends on your target platforms
2. Cross-references trends with your niche and history
3. Generates **content cards** with traffic/engagement predictions
4. Tracks what you publish, retro-fits actuals, calibrates predictions
5. Helps you grow, A/B test, expand to new platforms, and monetize

All in **plain Markdown files**. No database. No external API. No SaaS lock-in.

---

## What it does (14 commands)

### Core (v1)
| Command | What |
|---|---|
| `/onboard` | 8-question interview → niche recommendation + 6-month plan |
| `/daily` | Fetch trends → generate 3-5 content cards with predictions |
| `/review` | Weekly retro: paste actuals → skill recalibrates predictions |
| `/push` | Push today's content card to IM (DingTalk / Feishu / WeCom / WeChat via Server酱) |

### 10-round expansion (v2.1, zero-API)
| Command | What | Round |
|---|---|---|
| `/calendar` | Monthly content calendar (all platforms) | R1 |
| `/rewrite` | Adapt one idea into a different platform's native format | R3 |
| `/ab-test` | Generate N hook variants → auto-evaluate winner | R5 |
| `/todo` | Daily todos aggregated from all cards | R8 |
| `/xplatform` | Track same idea across 2+ platforms → ROI ranking | R9 |
| `/monthly` | SKILL self-check: hit rate, growth speed, ROI | R10 |
| `/inspire` | Inspiration pool + auto-match with trends | R11 |
| `/failure` | Log a flop → categorized, auto-avoided next time | R12 |
| `/reply` | Draft a comment reply from 6-category playbook | R13 |
| `/holiday` | Upcoming holidays + content suggestions | R14 |

---

## Supported Platforms (9)

| Region | Platform | Format | Strength |
|---|---|---|---|
| 🇨🇳 | 小红书 (RedNote) | 9 图 + 1-3 min video | Search SEO, female 25-35 |
| 🇨🇳 | 抖音 (Douyin) | 15-60s vertical | Volume, breakout |
| 🇨🇳 | B站 (Bilibili) | 5-20 min long video | High engagement, long-tail |
| 🇨🇳 | 视频号 (WeChat Channels) | 1-3 min social-distributed | 40+ users, WeChat ecosystem |
| 🇨🇳 | 公众号 (WeChat Official Account) | 1500-3000 word articles | Deep content, B2B |
| 🌍 | YouTube | 8-15 min long video | Highest CPM, long-tail SEO |
| 🌍 | TikTok | 15-90s vertical | Global reach, Gen Z |
| 🌍 | Instagram | Reels + 9-grid + Stories | Visual, lifestyle |
| 🌍 | X (Twitter) | ≤280 chars + threads | Tech/startup/AI, viral |

---

## Why this exists

The user is a normal person who has skills and interests but **no idea what to post, when, or why**. Existing creator tools fall into two traps:

1. **SaaS lock-in** (Buffer, Hootsuite, Later) — monthly fees, you don't own your data.
2. **AI content mills** (Jasper, Copy.ai) — they write for you, you don't learn.

This skill is different:
- **You own your data** (markdown files in a folder).
- **You learn** (every command teaches you something about your niche).
- **The agent does the boring part** (fetching trends, predicting traffic, tracking metrics).
- **You do the creative part** (filming, writing, engaging).

---

## Quick Start (3 minutes)

### 1. Install the skill in your agent

Drop this `SKILL.md` into your agent's skills folder. Examples:

```bash
# Claude Code
cp -r Million-Bloggers-Plan-SKILL ~/.claude/skills/creator-incubator/

# Cursor
cp -r Million-Bloggers-Plan-SKILL ~/.cursor/skills/creator-incubator/

# OpenCode
cp -r Million-Bloggers-Plan-SKILL ~/.config/opencode/skills/creator-incubator/

# Generic (any agent supporting the Agent Skills spec)
cp -r Million-Bloggers-Plan-SKILL ~/.agents/skills/creator-incubator/
```

See [INSTALLATION.md](INSTALLATION.md) for agent-specific instructions.

### 2. Run `/onboard`

The agent will ask 8 questions (time, skills, platforms, monetization, etc.) and create a personalized niche recommendation + 6-month plan.

### 3. Run `/daily` every morning

Get 3-5 content cards with predicted traffic, filming checklists, and multi-platform packages.

### 4. Run `/review` every Sunday

Paste last week's actuals. The skill recalibrates and adjusts next week's plan.

---

## Repository structure

```
Million-Bloggers-Plan-SKILL/
├── README.md                    ← you are here
├── LICENSE                      ← MIT
├── INSTALLATION.md              ← agent-specific setup
├── CHANGELOG.md                 ← version history
├── SKILL.md                     ← main entry, 14 commands
├── references/                  ← domain knowledge (load on demand)
│   ├── platform-specs.md        ← 9 platforms × algorithm/format/data
│   ├── niche-templates.md       ← 22 niche templates
│   ├── content-frameworks.md    ← hooks, structures, CTAs
│   ├── traffic-prediction-model.md
│   ├── push-channels.md         ← 4 IM channels setup
│   └── holiday-calendar.md      ← 100+ events
├── scripts/                     ← pure Python, no API key needed (10 files)
│   ├── _common.py              ← shared: logger, error handler, VaultPath
│   ├── daily_content.py        ← /daily: generate today's cards
│   ├── weekly_review.py        ← /review: hit rate + platform breakdown + recs
│   ├── xplatform_roi.py        ← /xplatform: ROI ranking + migration recs
│   ├── skill_report.py         ← /monthly: monthly self-check
│   ├── inspiration_manager.py  ← /inspire: pool management
│   ├── failure_manager.py      ← /failure: log + pattern analysis
│   ├── ab_test_tracker.py      ← /ab-test: winner/loser declaration
│   ├── push_dispatcher.py      ← /push: IM push (DingTalk/Feishu/WeCom/WeChat)
│   └── skill_lint.py           ← CI + dev: validate frontmatter, scripts, secrets
├── tests/                      ← 50 unit tests for the shared utilities
│   ├── test_common.py          ← VaultPath, load_config, parse_frontmatter, etc.
│   ├── test_daily_content.py   ← /daily helpers
│   ├── test_skill_lint.py      ← frontmatter + secret detection
│   └── README.md
└── templates/                  ← markdown templates
    ├── platform-profile.md
    ├── incubation-plan.md
    ├── daily-content-card.md
    ├── content-calendar.md
    ├── rewrite-brief.md
    ├── ab-test-card.md
    ├── todo-list.md
    ├── cross-platform-compare.md
    ├── skill-monthly-report.md
    ├── inspiration-pool.md
    ├── failure-log.md
    └── comment-playbook.md
```

---

## Design Philosophy

1. **Zero external API.** Everything works with the agent's own LLM + local files. No API keys, no subscriptions, no rate limits.

2. **Markdown as the database.** Every plan, card, retro, and report is a `.md` file with YAML frontmatter. Searchable, version-controllable, portable.

3. **Lazy activation.** You don't fill out 9 platform profiles upfront. Pick 1-3 platforms in `/onboard`, the rest stay as placeholders until you add them later.

4. **Data-driven but humble.** Predictions are ranges, not promises. They get tighter as you accumulate 4+ weeks of actuals.

5. **Honest about failure.** The `/failure` command logs flops and the LLM categorizes them. The skill learns to avoid repeating them.

6. **Cross-platform by design.** One idea, multiple platform adaptations. Each platform is a self-contained "incubation unit."

---

## Roadmap

### Done (v2.1.0)
- 14 commands covering onboarding, daily content, review, multi-platform, A/B, todo, ROI, monthly check, inspiration, failures, comments, holidays, push
- 9 platforms × full specs
- 22 niche templates
- 100+ holiday/event calendar
- 3 Python scripts (push, A/B, monthly report)
- 12 markdown templates

### Next (v2.2 candidates — not yet implemented)
- Cron auto-push (currently manual)
- 2-way IM replies (user clicks "已选" in IM → updates card)
- AI cover generation (needs API, currently excluded)
- Platform API auto-fetch (Xiaohongshu/Douyin/Bilibili)
- Competitor monitoring (subscribe to N accounts → notify on new viral)

---

## Contributing

PRs welcome. Particularly:

- New platform specs (Threads? Substack? Pinterest? YouTube Shorts?)
- New niche templates (地域限制类 / 行业垂直类)
- Better traffic prediction model (more calibration data)
- More scripts (auto-publish? data scraper?)

Please read the existing files first to match tone and structure.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Author

[billy192723](https://github.com/billy192723) — built this because no existing tool fit "I'm a person who has skills and wants to be a creator, but I don't know where to start."

If this skill helped you, ⭐ the repo and tell me which niche you picked.
