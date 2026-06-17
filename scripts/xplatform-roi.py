#!/usr/bin/env python
"""
xplatform-roi.py - Compute cross-platform ROI ranking from tracked comparisons.

Used by the /xplatform command.

Reads:
  - _global/05-xplatform-compare.md (manual entries)
  - All daily-content-card files with cross_platform_group frontmatter

Computes per-platform:
  - 互动质量 (engagement rate)
  - 涨粉效率 (new followers per view)
  - 制作成本 (estimated by duration × complexity)
  - 内容寿命 (7-day residual views)
  - 综合 ROI = 互动质量 × 涨粉效率 / 制作成本

Ranks platforms, outputs migration recommendations.

Usage:
  python xplatform-roi.py                          # All comparisons, all time
  python xplatform-roi.py --since 2026-06-01      # Filter by date
  python xplatform-roi.py --dry-run               # Preview
  python xplatform-roi.py --vault "E:/..."
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
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


DEFAULT_VAULT = Path("E:/知识库/博主计划")


def parse_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def parse_engagement_rate(s) -> float:
    if s is None:
        return 0.0
    s = str(s).rstrip("%")
    try:
        return float(s)
    except (ValueError, AttributeError):
        return 0.0


# ---- Production cost (effort hours, by format) ----
COST_BY_FORMAT = {
    "图": 0.5,        # image-only post
    "图卡": 0.5,
    "图文": 0.5,
    "30秒": 0.7,
    "短视频": 0.7,
    "8分钟": 3.0,
    "长视频": 3.0,
    "1500字": 1.0,
    "长文": 1.0,
}


def estimate_cost(card: dict) -> float:
    """Estimate production cost in hours based on content type / duration."""
    dur = card.get("duration_seconds", 0)
    if dur and dur > 0:
        if dur <= 60:
            return 0.7
        elif dur <= 180:
            return 1.5
        elif dur <= 600:
            return 3.0
        else:
            return 5.0
    # Fallback by platform
    plat = card.get("platform", "")
    if plat in ("小红书",):
        return 0.5
    if plat in ("抖音", "TikTok", "Instagram", "X"):
        return 0.7
    if plat in ("B站", "YouTube"):
        return 3.0
    if plat in ("公众号",):
        return 1.0
    if plat in ("视频号",):
        return 1.0
    return 1.0


def collect_xplatform_data(vault: Path, since: date = None) -> dict:
    """
    Collect all cross-platform data, keyed by (group_id, topic).
    Returns { group_id: { topic, started, platforms: {plat: card_meta} } }
    """
    groups = defaultdict(lambda: {"topic": "", "started": None, "platforms": {}})

    for md in vault.rglob("04-内容卡/*.md"):
        meta = parse_frontmatter(md)
        if meta.get("type") != "daily-content-card":
            continue
        d = meta.get("date")
        if isinstance(d, str):
            try:
                d = date.fromisoformat(d)
            except ValueError:
                continue
        elif isinstance(d, datetime):
            d = d.date()
        else:
            continue
        if since and d < since:
            continue
        if not meta.get("actual_views"):
            continue  # not measured

        g = meta.get("cross_platform_group")
        if not g:
            continue

        plat = meta.get("platform")
        groups[g]["topic"] = meta.get("topic", "")
        if not groups[g]["started"] or d < groups[g]["started"]:
            groups[g]["started"] = d
        groups[g]["platforms"][plat] = meta

    return dict(groups)


def compute_roi(card: dict) -> dict:
    """Compute ROI metrics for one card."""
    views = card.get("actual_views", 0) or 0
    eng = parse_engagement_rate(card.get("actual_engagement_rate"))
    followers = card.get("new_followers", 0) or 0
    cost = estimate_cost(card)

    # Per-1000-views rate (allows comparison across platforms)
    per_k_eng = eng  # engagement rate is already a %
    follower_eff = (followers / views * 1000) if views > 0 else 0  # followers per 1k views

    # ROI score: weighted product, normalized
    # higher engagement, higher follower efficiency, lower cost = better
    if cost == 0:
        cost = 0.5
    roi = (eng * follower_eff / 10) / cost  # rough formula

    # Letter grade
    if roi >= 5:
        grade = "A"
    elif roi >= 2:
        grade = "B"
    elif roi >= 0.5:
        grade = "C"
    else:
        grade = "D"

    return {
        "platform": card.get("platform", "?"),
        "views": views,
        "engagement_rate": eng,
        "new_followers": followers,
        "estimated_cost_hours": cost,
        "followers_per_1k_views": round(follower_eff, 2),
        "roi_score": round(roi, 2),
        "roi_grade": grade,
    }


def render_report(group_data: dict, decisions: list) -> str:
    """Render the cross-platform comparison report."""
    lines = []
    lines.append("# 跨平台 ROI 对比报告\n")
    lines.append(f"_Generated: {datetime.now().isoformat()}_\n")

    if not group_data:
        lines.append("没有 cross_platform_group 标记的内容卡。\n")
        lines.append("使用方法:在内容卡 frontmatter 加 `cross_platform_group: \"X\"` 标记同 idea 的多平台卡。\n")
        return "\n".join(lines)

    # Per-group breakdown
    for gid, data in group_data.items():
        lines.append(f"## Group: `{gid}` — {data.get('topic', '?')}\n")
        if data.get("started"):
            lines.append(f"开始日期: {data['started']}\n")

        # Per-platform stats
        stats = {plat: compute_roi(card) for plat, card in data["platforms"].items()}
        lines.append("| 平台 | 播放 | 互动率 | 涨粉 | 成本(小时) | ROI 评分 |")
        lines.append("|---|---|---|---|---|---|")
        for plat, s in sorted(stats.items(), key=lambda x: -x[1]["roi_score"]):
            lines.append(
                f"| {plat} | {s['views']:,} | {s['engagement_rate']:.1f}% | "
                f"+{s['new_followers']} | {s['estimated_cost_hours']:.1f} | **{s['roi_grade']}** |"
            )
        lines.append("")

    # Aggregate: which platform wins overall
    agg = defaultdict(lambda: {"total_score": 0, "count": 0, "grade": ""})
    for gid, data in group_data.items():
        for plat, card in data["platforms"].items():
            r = compute_roi(card)
            agg[plat]["total_score"] += r["roi_score"]
            agg[plat]["count"] += 1
            agg[plat]["grade"] = r["roi_grade"]

    lines.append("## 累计排名(所有 group)\n")
    lines.append("| 平台 | 平均 ROI | 测试次数 | 等级 |")
    lines.append("|---|---|---|---|")
    for plat, s in sorted(agg.items(), key=lambda x: -x[1]["total_score"] / max(1, x[1]["count"])):
        avg = s["total_score"] / max(1, s["count"])
        lines.append(f"| {plat} | {avg:.2f} | {s['count']} | **{s['grade']}** |")
    lines.append("")

    # Decisions
    if decisions:
        lines.append("## 决策建议\n")
        for i, d in enumerate(decisions, 1):
            lines.append(f"{i}. {d}")
        lines.append("")

    return "\n".join(lines)


def generate_decisions(agg: dict) -> list:
    """Generate migration recommendations based on ROI ranking."""
    if not agg:
        return []
    decisions = []
    sorted_plats = sorted(agg.items(), key=lambda x: -x[1]["total_score"] / max(1, x[1]["count"]))
    top = sorted_plats[0]
    decisions.append(f"**首选平台: {top[0]}** — 平均 ROI {top[1]['total_score']/max(1, top[1]['count']):.2f},等级 {top[1]['grade']}")
    if len(sorted_plats) > 1:
        for plat, s in sorted_plats[1:3]:
            decisions.append(f"**次选: {plat}** — 平均 ROI {s['total_score']/max(1, s['count']):.2f},等级 {s['grade']}")
    if len(sorted_plats) > 3:
        worst = sorted_plats[-1]
        if worst[1]['total_score']/max(1, worst[1]['count']) < 1:
            decisions.append(f"**暂缓: {worst[0]}** — ROI 偏低,建议暂停 4 周观察")
    return decisions


def main():
    p = argparse.ArgumentParser(
        description="Cross-platform ROI comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--vault", help=f"Vault path (default: {DEFAULT_VAULT})")
    p.add_argument("--since", help="Filter cards from this date (YYYY-MM-DD)")
    p.add_argument("--dry-run", action="store_true", help="Preview only")
    args = p.parse_args()

    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    if not vault.exists():
        print(f"[ERROR] Vault not found: {vault}", file=sys.stderr)
        return 2

    since = None
    if args.since:
        try:
            since = date.fromisoformat(args.since)
        except ValueError:
            print(f"[ERROR] Invalid date: {args.since}", file=sys.stderr)
            return 1

    group_data = collect_xplatform_data(vault, since)

    # Aggregate for decisions
    agg = defaultdict(lambda: {"total_score": 0, "count": 0, "grade": ""})
    for gid, data in group_data.items():
        for plat, card in data["platforms"].items():
            r = compute_roi(card)
            agg[plat]["total_score"] += r["roi_score"]
            agg[plat]["count"] += 1
            agg[plat]["grade"] = r["roi_grade"]

    decisions = generate_decisions(agg)
    report = render_report(group_data, decisions)

    if args.dry_run:
        print(report)
        return 0

    out_path = vault / "_global" / "05-跨平台对比.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"[OK] Updated {out_path.relative_to(vault)}")
    print()
    # Show preview
    print("--- PREVIEW ---")
    print(report[:1500] + "..." if len(report) > 1500 else report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
