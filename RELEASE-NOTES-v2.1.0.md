# v2.1.0 — Creator Incubator

> AI agent skill that helps you become a content creator / million-follower blogger on Chinese and international platforms.

## Highlights

- **14 commands** covering the full creator journey: onboarding, daily content, weekly review, multi-platform rewrite, A/B testing, todo management, ROI tracking, monthly self-check, inspiration pool, failure logging, comment replies, holiday calendar, and IM push.
- **9 platforms** (5 Chinese + 4 international): 小红书 / 抖音 / B站 / 视频号 / 公众号 / YouTube / TikTok / Instagram / X.
- **Zero external API dependencies** — works with any LLM agent's own capabilities.
- **Markdown as database** — all plans, cards, retros, and reports are plain `.md` files with YAML frontmatter. Version-controllable, portable, no lock-in.

## What's new since v1.0.0

### 10-round expansion (zero-API)

| Round | Command | What |
|---|---|---|
| R1 | `/calendar` | Monthly content calendar (Dataview JS, all platforms) |
| R3 | `/rewrite` | Adapt one idea into a different platform's native format |
| R5 | `/ab-test` | Generate N hook variants + auto-evaluate winner |
| R8 | `/todo` | Daily todos aggregated from all cards |
| R9 | `/xplatform` | Cross-platform ROI tracking + migration recommendations |
| R10 | `/monthly` | SKILL self-check (hit rate, growth speed, ROI, A/B progress) |
| R11 | `/inspire` | Inspiration pool + auto-match with trends |
| R12 | `/failure` | Log flops + categorize + auto-avoid next time |
| R13 | `/reply` | Draft comment replies from 6-category playbook |
| R14 | `/holiday` | 100+ event calendar + timely content suggestions |

### v2.0 — IM push

- `/push` — manual-trigger push to 4 IM channels (DingTalk / Feishu / WeCom / WeChat via Server酱 or WxPusher)
- `scripts/push-dispatcher.py` — standalone dispatcher

## Files

- 1 `SKILL.md` (main entry)
- 6 `references/*.md` (domain knowledge)
- 3 `scripts/*.py` (zero-dependency Python tools)
- 12 `templates/*.md` (output templates)
- 5 top-level docs (`README.md`, `INSTALLATION.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`)

## Installation

See [INSTALLATION.md](https://github.com/billy192723/Million-Bloggers-Plan-SKILL/blob/main/INSTALLATION.md) for agent-specific setup. Works with:

- Claude Code
- Cursor
- Windsurf
- OpenCode
- Codex
- Hermes Agent
- Continue.dev
- Cline
- Aider (via system prompt)
- Any agent supporting the [Agent Skills spec](https://agentskills.io)

## Compatibility

| Agent | Status |
|---|---|
| Claude Code | ✅ Tested |
| Cursor | ✅ Compatible |
| Hermes Agent | ✅ Originally built for |
| Others (Codex, Windsurf, OpenCode, etc.) | 🟡 Should work (any Agent Skills spec consumer) |

## Contributing

PRs welcome. See [CONTRIBUTING.md](https://github.com/billy192723/Million-Bloggers-Plan-SKILL/blob/main/CONTRIBUTING.md).

## License

MIT.
