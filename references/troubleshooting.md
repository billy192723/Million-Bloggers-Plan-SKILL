# Troubleshooting 速查表

> SKILL 常见错误 + 一行修复。详细看 `references/debugging-and-gotchas.md`。

## 命令相关

| 症状 | 原因 | 修复 |
|---|---|---|
| `/onboard` 没生成文件 | vault 路径错 | 跑 `python scripts/daily_content.py --dry-run` 验证路径 |
| `/daily` 生成的卡没有内容 | LLM 没填实 | 检查 `daily_content.py` 输出,看是不是占位符 |
| `/review` 算不出命中率 | actual 数据没填 | 在 06-数据看板.md 填实际数字 |
| `/push` IM 没收到 | webhook 错 | 检查 04-推送配置.md 的 webhook URL |
| `/fetch-stats` 报 captcha | 抖音风控 | 停 24h,网络换 IP |

## 脚本相关

| 症状 | 原因 | 修复 |
|---|---|---|
| `ModuleNotFoundError: yaml` | pyyaml 没装 | `pip install pyyaml` |
| `playwright` 找不到 | 没装 | `pip install playwright && playwright install chromium` |
| `--vault` 报错 "not found" | 路径不存在 | 确认 `E:\知识库\博主计划` 真实存在 |
| 中文路径乱码 | Windows GBK | 设 `PYTHONIOENCODING=utf-8` |
| 脚本卡住 30s+ | 平台 API 慢 | `--verbose` 看哪里卡 |

## 文件相关

| 症状 | 原因 | 修复 |
|---|---|---|
| YAML 解析错 | 缩进或冒号错 | 跑 `python scripts/skill_lint.py --strict` 看具体哪个文件 |
| frontmatter 缺 --- | 写时漏了 | 补 `---` 在文件第一行和第三行 |
| `_common.py` 找不到 | sys.path 问题 | 跑脚本用 `cd scripts && python X.py` |
| 文件名带 dash | import 失败 | 重命名为下划线(`daily-content.py` → `daily_content.py`) |

## CI 失败

| 症状 | 原因 | 修复 |
|---|---|---|
| `Process completed with exit code 1` | 某个 step 失败 | 看 GitHub Actions 详细 log |
| `'run' is already defined` | ci.yml YAML 格式错 | 删重复 `run:` 字段 |
| `Secret detected` | 误判测试 fixture | `skill_lint.py` 已排除 tests/,独立 grep 步骤也加 `--exclude-dir=tests` |
| `unit test failure` | 测试失败 | `cd tests && python -m unittest discover` 本地跑 |

## Obsidian 端

| 症状 | 原因 | 修复 |
|---|---|---|
| Dataview 查不到 | frontmatter 不对 | 看 `_global/README.md` 的 Dataview 示例 |
| 内容卡显示 raw markdown | 没用 Obsidian 打开 | 用 Obsidian 打开 .md 文件 |
| 多个平台文件结构不一致 | 漏建 | 跑 `/onboard` 重新激活 |

## 抓取相关(`/fetch-stats`)

| 症状 | 原因 | 修复 |
|---|---|---|
| 0 videos found | Douyin UI 改了 | 更新 `fetch_douyin_stats.py` 的 CSS selectors |
| "Login required" 跳转 | cookies 过期 | 重新导出 |
| Captcha 一直出 | IP 被风控 | 换 IP(手机热点),24h 后再试 |
| "Risk control" 警告 | 操作太频繁 | 等 24h,减少 daily runs |

## GitHub 推送

| 症状 | 原因 | 修复 |
|---|---|---|
| `git push` timeout | 大 commit | `git config http.postBuffer 524288000` |
| `Bad credentials` | token 失效 | 撤销旧 token,用 SSH key 推 |
| CI fail on push | 跑一下 `python scripts/skill_lint.py --strict` | 看哪个 check 失败 |

## 网络/平台

| 症状 | 原因 | 修复 |
|---|---|---|
| Google 反爬 | 触发 CAPTCHA | 改用 Bing 或平台自带发现页 |
| 小红书 explore 404 | 需登录 | 改用搜狗搜索 "site:xiaohongshu.com [topic]" |
| 抖音内容搜不到 | 关键词不对 | 换同义词 |

## 详细文档

- `references/debugging-and-gotchas.md` — 11 个 Python 技术坑
- `scripts/README.md` — 脚本完整 API
- `references/script-reference.md` — 详细 CLI 选项
