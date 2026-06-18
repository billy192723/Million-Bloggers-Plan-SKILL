# Script Reference — 12 个脚本完整 API

> 所有脚本支持 `--help` 查完整帮助。这里是手动整理的版本,便于查阅。

## 通用参数

所有脚本(除了 `read_file.py` 和 `_common.py`)支持:
- `--vault <path>` — vault 路径(默认 `E:/知识库/博主计划`)
- `--verbose` — 详细日志
- `--help` — 命令帮助
- `--dry-run` — 预览不写(部分命令)

---

## 1. `daily_content.py` — /daily

**目的**:抓平台热点 + 读用户档案/灵感/失败,生成内容卡

```bash
python daily_content.py --vault ...           # 默认(全部活跃平台)
python daily_content.py --platform=抖音       # 单平台
python daily_content.py --count=3             # 每平台 3 张
python daily_content.py --idea "AI 工具横评"  # 指定主题
python daily_content.py --dry-run             # 预览不写
```

---

## 2. `weekly_review.py` — /review

**目的**:算命中率 + 平台分布 + 建议

```bash
python weekly_review.py                        # 最近 7 天
python weekly_review.py --week=2026-W25        # 指定 ISO 周
python weekly_review.py --platform=小红书     # 单平台
python weekly_review.py --dry-run             # 预览
```

---

## 3. `xplatform_roi.py` — /xplatform

**目的**:跨平台 ROI 排名 + 迁移建议

```bash
python xplatform_roi.py                        # 全部
python xplatform_roi.py --since 2026-06-01    # 从某日期起
python xplatform_roi.py --dry-run             # 预览
```

需要内容卡 frontmatter 标 `cross_platform_group: "X"`。

---

## 4. `skill_report.py` — /monthly

**目的**:月度自检报告

```bash
python skill_report.py                         # 默认上月
python skill_report.py --month=2026-06         # 指定月
python skill_report.py --dry-run              # 预览
```

---

## 5. `inspiration_manager.py` — /inspire

**子命令**:`add` / `list` / `link` / `archive`

```bash
python inspiration_manager.py add "AI 副业实战" --tags=AI,副业
python inspiration_manager.py list --status=unused
python inspiration_manager.py list --priority=4
python inspiration_manager.py link INS-20260617-001 --card=2026-06-20-001
python inspiration_manager.py archive --days=90
```

---

## 6. `failure_manager.py` — /failure

**子命令**:`add` / `list` / `patterns` / `archive`

```bash
python failure_manager.py add 2026-06-15-002 --reason="标题党被限流"
python failure_manager.py list --category=标题党
python failure_manager.py list --severity=high
python failure_manager.py patterns
python failure_manager.py archive --days=180
```

---

## 7. `ab_test_tracker.py` — /ab-test

**目的**:评估 A/B 测试组胜出

```bash
python ab_test_tracker.py                      # 全部
python ab_test_tracker.py --platform=小红书   # 单平台
python ab_test_tracker.py --group=2026-06-17-claude45  # 指定组
python ab_test_tracker.py --dry-run
```

需要 A/B 测试卡在 `04-内容卡/ab/`,frontmatter 标 `ab_group` + `ab_variant`。

---

## 8. `push_dispatcher.py` — /push

**目的**:推内容卡到 IM(4 通道)

```bash
python push_dispatcher.py --config 04-push-config.md --test   # 测试
python push_dispatcher.py --config 04-push-config.md          # 实际推送
python push_dispatcher.py --config 04-push-config.md --dry-run
```

需要先填 `_global/04-推送配置.md` 的 webhook。

---

## 9. `skill_lint.py` — CI + dev

**目的**:SKILL 结构 lint

```bash
python skill_lint.py                            # 默认
python skill_lint.py --path /path/to/SKILL     # 指定路径
python skill_lint.py --strict                  # 失败 = exit 1
python skill_lint.py --json                    # JSON 输出
```

CI 自动跑(在 `.github/workflows/ci.yml`)。

---

## 10. `fetch_douyin_stats.py` — /fetch-stats

**目的**:抓抖音创作者后台(防封 7 道防线)

```bash
python fetch_douyin_stats.py --dry-run         # 验证
python fetch_douyin_stats.py --output stats.json
python fetch_douyin_stats.py --cookies /path/to/cookies.json
```

需要先导出 cookies(见 `export_douyin_cookies.md`)。

⚠️ **每天最多 1 次,会被风控**。

---

## 11. `fill_douyin_cards.py` — /fetch-stats 第二步

**目的**:把 stats.json 填到 24h 复盘表

```bash
python fill_douyin_cards.py --stats stats.json
python fill_douyin_cards.py --stats stats.json --vault "E:/知识库/博主计划"
```

---

## 12. `read_file.py` — 通用工具

**目的**:解析 .md 的 frontmatter

```bash
python read_file.py path/to/file.md            # 打印 YAML frontmatter
python read_file.py path/to/file.md --body    # 加上 body
```

**Python API**:
```python
from read_file import parse_frontmatter, parse_frontmatter_file, write_with_frontmatter

meta, body = parse_frontmatter_file(Path("SKILL.md"))
write_with_frontmatter(Path("output.md"), {"type": "example"}, "# Hello")
```

---

## 13. `_common.py` — 共享库(不是 CLI)

被上面 11 个 import。提供:
- `setup_logging(verbose)` — 统一 logger
- `handle_errors` (装饰器) — 友好错误处理
- `load_config(path)` — 安全 YAML 加载
- `VaultPath(root)` — 路径助手
- `format_table(headers, rows)` — Markdown 表格
- `parse_frontmatter(path)` — frontmatter 解析
- `safe_write(path, content, overwrite)` — 写文件

---

## 50 unit tests

```bash
cd tests
python -m unittest discover -s . -p "test_*.py"
```

覆盖 _common.py / daily_content.py / skill_lint.py 的核心功能。
