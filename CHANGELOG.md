# Changelog

All notable changes to this project are documented here.

## [2.1.0] - 2026-06-17

### Added (10-round expansion, zero API dependencies)

- **R1** `/calendar` — Monthly content calendar (Dataview JS, all platforms)
- **R3** `/rewrite` — Adapt one idea into a different platform's native format
- **R5** `/ab-test` — Generate N hook variants + auto-evaluate winner
- **R8** `/todo` — Daily todos aggregated from all cards
- **R9** `/xplatform` — Cross-platform ROI tracking + migration recommendations
- **R10** `/monthly` — SKILL self-check (hit rate, growth speed, ROI, A/B progress)
- **R11** `/inspire` — Inspiration pool + auto-match with trends
- **R12** `/failure` — Log flops + categorize + auto-avoid next time
- **R13** `/reply` — Draft comment replies from 6-category playbook
- **R14** `/holiday` — 100+ event calendar + timely content suggestions

### Added (scripts)

- `scripts/ab-test-tracker.py` — A/B winner declaration
- `scripts/skill-report.py` — Monthly self-check report

### Added (references)

- `references/holiday-calendar.md` — 100+ marketing events and holidays

### Added (templates)

- `templates/content-calendar.md`
- `templates/rewrite-brief.md`
- `templates/ab-test-card.md`
- `templates/todo-list.md`
- `templates/cross-platform-compare.md`
- `templates/skill-monthly-report.md`
- `templates/inspiration-pool.md`
- `templates/failure-log.md`
- `templates/comment-playbook.md`

### Changed

- LinkedIn replaced with X (Twitter) — more aligned with creator/tech niche
- Folder structure: `博主计划/_全局/国内/小红书/...` → English defaults (`Million-Bloggers-Plan-SKILL/_global/CN/xiaohongshu/...`) for international compatibility

## [2.0.0] - 2026-06-17

### Added

- **Push to IM** (`/push`) — 4 channels: DingTalk, Feishu, WeCom, WeChat (via Server酱 or WxPusher)
- `scripts/push-dispatcher.py` — Manual-trigger IM push dispatcher
- `references/push-channels.md` — Channel setup tutorials
- `_global/04-push-config.md` template

### Changed

- Frontmatter updated to support manual-trigger-only push (no cron auto)
- All channels `enabled: false` by default for safety

## [1.0.0] - 2026-06-17

### Added

- **3 core commands**: `/onboard`, `/daily`, `/review`
- 9 platforms supported (5 CN + 4 INTL): 小红书 / 抖音 / B站 / 视频号 / 公众号 / YouTube / TikTok / Instagram / X
- Self-contained platform structure: each platform has its own 00-06 files
- 22 niche templates
- Content frameworks (10 hook formulas, 6 body structures, CTA library)
- Traffic & engagement prediction model with calibration
- 3 markdown templates: user-profile, incubation-plan, daily-content-card

### Notes

- Initial release
- 0 external API dependencies
- 100% markdown-based, no database
- Works with any LLM agent supporting the Agent Skills spec

---

[Unreleased]: https://github.com/billy192723/Million-Bloggers-Plan-SKILL/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/billy192723/Million-Bloggers-Plan-SKILL/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/billy192723/Million-Bloggers-Plan-SKILL/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/billy192723/Million-Bloggers-Plan-SKILL/releases/tag/v1.0.0
