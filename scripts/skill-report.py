#!/usr/bin/env python
"""
skill-report.py (R10)

Read Obsidian vault, generate monthly self-check report.
Pure read + LLM-summary logic. No external API.

Usage:
  python skill-report.py --month=2026-06
  python skill-report.py                # default: last month
  python skill-report.py --dry-run
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required.", file=sys.stderr)
    sys.exit(1)


VAULT = Path("E:/知识库/博主计划")


def parse_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {"_path": path, "_body": text}
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {"_path": path, "_body": text}
    meta["_path"] = path
    meta["_body"] = text
    return meta


def parse_range_low(s: str) -> int:
    """Parse '5000-15000' or '5000' → low value."""
    if not s:
        return 0
    if "-" in str(s):
        return int(str(s).split("-")[0])
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--month", help="YYYY-MM, default last month")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # Default: last month
    if not args.month:
        today = date.today()
        if today.month == 1:
            target = f"{today.year - 1}-12"
        else:
            target = f"{today.year}-{today.month - 1:02d}"
    else:
        target = args.month

    # Collect cards
    cards = []
    for md in VAULT.rglob("04-内容卡/*.md"):
        c = parse_card(md)
        if c.get("type") == "daily-content-card":
            cards.append(c)
    for md in (VAULT / "国内").rglob("04-内容卡/ab/*.md"):
        c = parse_card(md)
        if c.get("type") == "ab-test-card":
            cards.append(c)

    month_cards = [c for c in cards
                   if str(c.get("date", "")).startswith(target)]

    if not month_cards:
        print(f"[INFO] No cards found for {target}.")
        return 0

    # ---- Stats ----
    published = [c for c in month_cards if c.get("status") == "published"]
    total_published = len(published)

    total_views = sum(c.get("actual_views", 0) or 0 for c in published)
    total_likes = 0  # 不直接有,跳过

    # Engagement rates
    eng_rates = [c.get("actual_engagement_rate") for c in published
                 if c.get("actual_engagement_rate") is not None]
    eng_rates_num = []
    for e in eng_rates:
        try:
            eng_rates_num.append(float(str(e).rstrip("%")))
        except (ValueError, AttributeError):
            pass

    median_engagement = sorted(eng_rates_num)[len(eng_rates_num) // 2] if eng_rates_num else 0

    # Hit rate
    hits = 0
    total_predicted = 0
    for c in published:
        if c.get("actual_views") and c.get("predicted_views"):
            low = parse_range_low(c["predicted_views"])
            if low > 0:
                total_predicted += 1
                if c["actual_views"] >= low:
                    hits += 1
    hit_rate = round(hits / total_predicted * 100, 1) if total_predicted else 0

    # By platform
    by_platform = defaultdict(lambda: {"count": 0, "views": 0, "engagement": []})
    for c in published:
        plat = c.get("platform") or "unknown"
        by_platform[plat]["count"] += 1
        by_platform[plat]["views"] += c.get("actual_views", 0) or 0
        if c.get("actual_engagement_rate"):
            try:
                by_platform[plat]["engagement"].append(
                    float(str(c["actual_engagement_rate"]).rstrip("%"))
                )
            except (ValueError, AttributeError):
                pass

    # A/B tests
    ab_cards = [c for c in month_cards if c.get("type") == "ab-test-card"]
    ab_groups = defaultdict(list)
    for c in ab_cards:
        ab_groups[c.get("ab_group", "?")].append(c)
    ab_completed = sum(1 for g, cs in ab_groups.items()
                       if all(c.get("actual_views") for c in cs))

    # Cross-platform comparisons
    xplatform = []
    for md in (VAULT / "_全局").glob("05-跨平台对比*.md"):
        xplatform.append(parse_card(md))

    # Failure logs
    failures = []
    failure_file = VAULT / "_全局" / "07-失败案例.md"
    if failure_file.exists():
        fail_doc = parse_card(failure_file)
        # 不解析,简单计数
        failures = re.findall(r"FAIL-\d+-\d+-\d+-\d+", fail_doc.get("_body", ""))

    # ---- Render report ----
    lines = []
    lines.append(f"# 📊 SKILL 自检月报:{target}\n")
    lines.append("## 总览\n")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|---|---|")
    lines.append(f"| 发布条数 | {total_published} |")
    lines.append(f"| 总播放 | {total_views:,} |")
    lines.append(f"| 互动率(中位) | {median_engagement}% |")
    lines.append(f"| 命中率 | {hit_rate}% ({hits}/{total_predicted}) |")
    lines.append(f"| A/B 测试完成 | {ab_completed} 组 |")
    lines.append(f"| 失败案例 | {len(failures)} 条 |\n")

    lines.append("## 平台分布\n")
    lines.append("| 平台 | 发布 | 总播放 | 平均互动率 |")
    lines.append("|---|---|---|---|")
    for plat, s in sorted(by_platform.items(), key=lambda x: -x[1]["views"]):
        avg_eng = sorted(s["engagement"])[len(s["engagement"]) // 2] if s["engagement"] else 0
        lines.append(f"| {plat} | {s['count']} | {s['views']:,} | {avg_eng}% |")
    lines.append("")

    lines.append("## A/B 测试结果\n")
    for g, cs in ab_groups.items():
        result_str = "完成" if all(c.get("actual_views") for c in cs) else "未完成"
        lines.append(f"- **{g}**: {len(cs)} 变体,{result_str}")
    lines.append("")

    lines.append("## 跨平台对比\n")
    lines.append(f"- 完成 {len(xplatform)} 组对比")
    lines.append("")

    lines.append("## 失败案例\n")
    lines.append(f"- 本月 {len(failures)} 条失败记录")
    lines.append("- 详细见 `_全局/07-失败案例.md`\n")

    lines.append("## 下月建议(自动生成,需用户确认)\n")
    # Simple heuristics
    sorted_plats = sorted(by_platform.items(), key=lambda x: -x[1]["views"])
    if sorted_plats:
        top = sorted_plats[0][0]
        lines.append(f"1. **加投 {top}**:本月播放第一")
    if hit_rate < 50:
        lines.append("2. **预测校准**:命中率 < 50%,下次预测乘以 0.9")
    if ab_completed < 3:
        lines.append("3. **A/B 测试偏少**:建议下月至少完成 3 组")
    if len(failures) > 5:
        lines.append(f"4. **失败案例 {len(failures)} 条**:本周必看,识别高频错误")

    lines.append("\n---\n")
    lines.append(f"_Generated by skill-report.py at {datetime.now().isoformat()}_")

    report = "\n".join(lines)

    out_path = VAULT / "05-周复盘" / "monthly" / f"{target}.md"
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"[OK] Report written to {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    sys.exit(main())
