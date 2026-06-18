---
name: creator-incubator
description: "Use when the user wants to become a content creator, influencer, or 'million-follower blogger' on Chinese (小红书/抖音/B站/视频号/公众号) or international (YouTube/TikTok/Instagram/X) platforms. Triggered by '做博主', '成为网红', '孵化账号', 'I want to be an influencer', 'recommend a niche for me', 'give me a content plan', '今天该拍什么'. Provides 15 LLM-driven commands + 12 zero-API Python scripts. Zero external API. **Before writing new code, see the 'Workflow Principle' — report 热点+目的+流量逻辑 first.**"
version: 2.2.0
author: billy192723
license: MIT
platforms: [linux, macos, windows]
homepage: https://github.com/billy192723/Million-Bloggers-Plan-SKILL
---

# Creator Incubator

## Quickstart(30 秒上手)

```bash
# 1. 装依赖
pip install pyyaml playwright && playwright install chromium

# 2. 第一次跑 onboard
# 在新对话说:"我要做 AI 领域博主,想做抖音"
# SKILL 问 8 个问题,生成 _global/00-档案.md

# 3. 每天早上跑 daily
# 说:"跑今天的 daily"
# SKILL 抓热点 + 生成 3-5 张内容卡,写到 04-内容卡/

# 4. 每周日跑 review
# 说:"跑本周 review"
# SKILL 算命中率 + Top 3 / Bottom 3 + 下周建议
```

**核心循环**:`/onboard` 一次 → `/daily` 每天 → `/review` 每周 → 持续优化

## 15 个命令总览

| 命令 | 何时 | 做什么 | Round |
|---|---|---|---|
| `/onboard` | 首次 | 8 问 → 方向 + 6 月计划 | v1 |
| `/daily` | 每天早上 | 抓热点 → 3-5 张内容卡 | v1 |
| `/review` | 每周日 | 算命中率 + 建议 | v1 |
| `/push` | 手动 | 推内容卡到 IM(钉钉/飞书/企微/微信) | v2.0 |
| `/calendar` | 随时 | Dataview 月历 | R1 |
| `/rewrite` | 改稿 | LLM 改写为其他平台格式 | R3 |
| `/ab-test` | 测钩子 | N 个变体 + 自动评估胜出 | R5 |
| `/todo` | 每天 | 拍摄清单汇总 | R8 |
| `/xplatform` | 跨平台 | 7 天 ROI 排名 | R9 |
| `/monthly` | 月底 | SKILL 自检月报 | R10 |
| `/inspire` | 任意 | 加/列灵感,自动配趋势 | R11 |
| `/failure` | 翻车时 | 记录失败 + 主动规避 | R12 |
| `/reply` | 评论回复 | 6 类话术生成 | R13 |
| `/holiday` | 每天(auto) | 节日节点蹭点 | R14 |
| `/fetch-stats` | 发布后 | 抓抖音后台 + 自动填 24h 表 | R15 |

## 3 个核心流程(必看)

### 1. `/onboard` — 首次开号(1 次)

**SKILL 问 8 个问题**(一次性):
1. 每天能投入多少时间?
2. 哪些技能/经验/兴趣?
3. 露脸吗?
4. 设备?
5. 优先国内还是国外?
6. 目标变现?
7. 欣赏的 1-3 个博主?
8. 最不想做哪类内容?

**SKILL 输出**:
- `_global/00-档案.md`(填实)
- `_global/01-方向.md`(选定主方向)
- `_global/02-路径.md`(6 个月 M1-M6 里程碑)
- 各平台 `00-平台档案.md` / `01-方向.md` / `02-路径.md` / `06-数据看板.md`

### 2. `/daily` — 每天早上(必跑)

**SKILL 流程**:
1. 读 `_global/00-档案.md`(用户方向)
2. 读 `_global/06-灵感库.md`(未用灵感)
3. 读 `_global/07-失败案例.md`(高严重度失败)
4. 抓平台热点(web_search / 平台发现页)
5. LLM 匹配灵感 + 热点
6. 生成 3-5 张内容卡,写到 `{region}/{platform}/04-内容卡/`

**每张卡含**:主题 / 钩子 / 完整脚本(分镜) / 拍摄清单 / 标签 / 流量预估 / CTA

### 3. `/review` — 每周日(必跑)

**SKILL 流程**:
1. 问用户过去 7 天实际数据(播放/点赞/评论/涨粉)
2. 算命中率(actual vs predicted)
3. 按平台分组统计
4. Top 3 / Bottom 3 内容
5. 失败模式分析
6. 下周 3-5 条建议
7. 写到 `05-周复盘/{ISO-week}.md`

## 12 个脚本(`scripts/`,全零 API)

| 脚本 | 触发 | 用法 |
|---|---|---|
| `daily_content.py` | /daily | `python daily_content.py --vault ...` |
| `weekly_review.py` | /review | `python weekly_review.py` |
| `xplatform_roi.py` | /xplatform | `python xplatform_roi.py --since 2026-06-01` |
| `inspiration_manager.py` | /inspire | `add/list/link` |
| `failure_manager.py` | /failure | `add/list/patterns` |
| `ab_test_tracker.py` | /ab-test | `python ab_test_tracker.py --platform=小红书` |
| `push_dispatcher.py` | /push | `python push_dispatcher.py --config ... --test` |
| `skill_report.py` | /monthly | `python skill_report.py --month=2026-06` |
| `skill_lint.py` | CI | `python skill_lint.py --strict` |
| `fetch_douyin_stats.py` | /fetch-stats | 见 `export_douyin_cookies.md` |
| `fill_douyin_cards.py` | /fetch-stats | `python fill_douyin_cards.py --stats stats.json` |
| `_common.py` | shared | logger/error/VaultPath,被上面 11 个 import |

**通用 flags**:
- `--vault <path>` — vault 路径(默认 `E:/知识库/博主计划`)
- `--verbose` — 详细日志
- `--help` — 命令帮助

详细看 `scripts/README.md` 或 `references/script-reference.md`。

## Note Storage(默认 Obsidian)

```
博主计划/                     ← 你的 vault
├── _global/                  ← 跨平台共享(13 个文件)
│   ├── README.md             ← 总览
│   ├── 00-档案.md            ← /onboard 填实
│   ├── 01-方向.md            ← /onboard 选定
│   ├── 02-路径.md            ← 6 个月里程碑
│   ├── 03-内容日历.md        ← R1 月历
│   ├── 03a-本周任务.md       ← R8 任务
│   ├── 04-推送配置.md        ← /push IM 配置
│   ├── 05-跨平台对比.md      ← /xplatform 输出
│   ├── 06-灵感库.md          ← /inspire
│   ├── 07-失败案例.md        ← /failure
│   ├── 08-评论话术.md        ← /reply
│   ├── 09-节日日历.md        ← /holiday
│   ├── 10-抖音-cookies指南.md ← /fetch-stats 操作
│   └── 11-数据抓取日志.md    ← /fetch-stats 运行记录
├── 国内/
│   └── {platform}/
│       ├── 00-平台档案.md    ← 平台基础信息
│       ├── 01-方向.md        ← 平台特定子方向
│       ├── 02-路径.md        ← 平台 6 月路径
│       ├── 03-热点日志/      ← /daily 原始数据
│       ├── 04-内容卡/        ← /daily 生成的卡
│       ├── 05-周复盘/        ← /review 输出
│       └── 06-数据看板.md    ← 周度数据表
└── 国外/  ← 同上结构
```

每个 `_global/` 文件的细节看 `_global/README.md`。

## 其他命令(用得少,需要时看)

- **`/calendar` (R1)** — Dataview 跨平台月历,见 `templates/content-calendar.md`
- **`/rewrite` (R3)** — 同一 idea 改写为其他平台格式,见 `templates/rewrite-brief.md`
- **`/ab-test` (R5)** — N 个钩子变体 + 自动评估,见 `templates/ab-test-card.md`
- **`/todo` (R8)** — 每天拍摄清单汇总,见 `templates/todo-list.md`
- **`/monthly` (R10)** — 月度自检,看 `references/script-reference.md` 的 `skill_report.py` 段
- **`/inspire` (R11)** — 灵感库,见 `templates/inspiration-pool.md`
- **`/failure` (R12)** — 失败案例,见 `templates/failure-log.md`
- **`/reply` (R13)** — 6 类评论话术,见 `templates/comment-playbook.md`
- **`/holiday` (R14)** — 节日节点,见 `references/holiday-calendar.md`
- **`/push` (v2.0)** — 4 通道 IM 推送,见 `references/push-channels.md`

## Workflow Principle(写新东西前必读)

每次写新脚本/模板/章节,先报备 3 件事:

1. **热点** — 为什么这个时间点写这个?
2. **目的** — 解决什么用户痛点?
3. **流量逻辑** — 为什么这样写有人用?

不报备不动手。详见 `references/debugging-and-gotchas.md`。

## 详细文档(本文件不展开)

- `references/script-reference.md` — 12 个脚本详细 API
- `references/platform-specs.md` — 9 平台算法/格式/最佳实践
- `references/niche-templates.md` — 22 个 niche 模板
- `references/content-frameworks.md` — 10 钩子 + 6 结构
- `references/traffic-prediction-model.md` — 流量预估公式
- `references/push-channels.md` — 4 IM 通道配置
- `references/holiday-calendar.md` — 100+ 节日
- `references/debugging-and-gotchas.md` — 10 常见坑 + 修复
- `references/troubleshooting.md` — 速查表
- `templates/platforms/` — 6 平台特定 00-06 模板
- `templates/` — 12 通用模板
- `tests/` — 50 unit tests

## 7 道防封号机制(`/fetch-stats` 专用)

1. 只读不动(脚本**只**GET 数据)
2. 慢动作(2-7s 随机延迟)
3. 真实 Chrome profile
4. 反指纹(移除 `navigator.webdriver`)
5. 限速(每天 ≤ 1 次,强 20h 间隔)
6. Cookie 注入(你手动登录,脚本不做登录)
7. 人工化滚动(非直线 + 停顿)

详见 `scripts/export_douyin_cookies.md` + SKILL.md `/fetch-stats` 章节。

## License

MIT. 见 [LICENSE](LICENSE).
