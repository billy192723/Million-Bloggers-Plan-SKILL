#!/usr/bin/env python
"""
weekly-review.py - Generate weekly review report from past 7 days of content.

Used by the /review command.

Reads:
  - All daily-content-card files from each platform's 04-cards/
  - Each platform's 06-dashboard.md (for follower delta + income)
  - _global/07-failures.md (failure log)

Writes:
  - 05-周复盘/W{ISO-week}.md (per platform) OR 05-weekly/W{ISO-week}.md (cross-platform)

Computes:
  - Hit rate (actual_views >= predicted_views_low)
  - Engagement rate distribution
  - Top 3 / Bottom 3 content
  - Per-platform ROI
  - Failure pattern analysis
  - Next-week recommendations

Usage:
  python weekly-review.py                          # Auto-detect last 7 days
  python weekly-review.py --week=2026-W25          # Specific ISO week
  python weekly-review.py --platform=小红书         # Single platform
  python weekly-review.py --dry-run                # Preview only
  python weekly-review.py --vault "E:/知识库/博主计划"
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
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


def parse_range_low(s: str) -> int:
    if not s:
        return 0
    s = str(s)
    if "-" in s:
        try:
            return int(s.split("-")[0])
        except (ValueError, IndexError):
            return 0
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def parse_engagement_rate(s) -> float:
    if s is None:
        return 0.0
    s = str(s).rstrip("%")
    try:
        return float(s)
    except (ValueError, AttributeError):
        return 0.0


def collect_cards(vault: Path, since: date) -> list:
    """Collect all daily-content-card .md files in the vault, with metadata."""
    cards = []
    for md in vault.rglob("04-内容卡/*.md"):
        meta = parse_frontmatter(md)
        if meta.get("type") not in ("daily-content-card", "ab-test-card"):
            continue
        # Date filter
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
        if d < since:
            continue
        meta["_path"] = md
        meta["_date"] = d
        cards.append(meta)
    return cards


def collect_dashboards(vault: Path) -> dict:
    """Read all 06-dashboard.md files, return {platform: latest_week_row}."""
    dashboards = {}
    for md in vault.rglob("06-数据看板.md"):
        meta = parse_frontmatter(md)
        platform = meta.get("platform", md.parent.name)
        dashboards[platform] = md
    return dashboards


def collect_failures(vault: Path, since: date) -> list:
    """Read failure log entries from this week."""
    fail_file = vault / "_global" / "07-failures.md"
    if not fail_file.exists():
        return []
    text = fail_file.read_text(encoding="utf-8")
    failures = []
    blocks = re.findall(r"---\n(.*?)\n---", text, re.DOTALL)
    for fm in blocks:
        try:
            meta = yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            continue
        if meta.get("type") != "failure":
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
        if d >= since:
            failures.append(meta)
    return failures


def compute_hit_rate(cards: list) -> tuple:
    """Return (hits, total, rate%)."""
    hits = 0
    total = 0
    for c in cards:
        if c.get("status") != "published":
            continue
        actual = c.get("actual_views")
        predicted = c.get("predicted_views")
        if actual is None or not predicted:
            continue
        low = parse_range_low(predicted)
        if low > 0:
            total += 1
            if actual >= low:
                hits += 1
    rate = (hits / total * 100) if total else 0
    return hits, total, rate


def compute_platform_breakdown(cards: list) -> dict:
    """Return {platform: {count, views, engagement_rates: []}}"""
    by_plat = defaultdict(lambda: {"count": 0, "views": 0, "engagement": []})
    for c in cards:
        if c.get("status") != "published":
            continue
        plat = c.get("platform") or "unknown"
        by_plat[plat]["count"] += 1
        v = c.get("actual_views")
        if v:
            by_plat[plat]["views"] += v
        e = parse_engagement_rate(c.get("actual_engagement_rate"))
        if e > 0:
            by_plat[plat]["engagement"].append(e)
    return dict(by_plat)


def find_top_bottom(cards: list, n: int = 3) -> tuple:
    """Return (top_n, bottom_n) by actual_views."""
    published = [c for c in cards if c.get("status") == "published" and c.get("actual_views")]
    sorted_cards = sorted(published, key=lambda c: c.get("actual_views", 0), reverse=True)
    return sorted_cards[:n], sorted_cards[-n:]


def generate_recommendations(cards: list, by_plat: dict, failures: list) -> list:
    """Generate 3-5 next-week recommendations based on this week's data."""
    recs = []
    # Top platform gets more
    if by_plat:
        top_plat = max(by_plat.items(), key=lambda x: x[1]["views"])
        recs.append(f"加投 {top_plat[0]}:本周播放 {top_plat[1]['views']:,},排名第一")
    # Worst platform reduces
    if len(by_plat) > 1:
        worst = min(by_plat.items(), key=lambda x: x[1]["views"])
        worst_plat = worst[0]
        worst_views = worst[1]["views"]
        recs.append(f"减少 {worst_plat}:本周仅 {worst_views:,} 播放")
    # Failure patterns
    if failures:
        cats = []
        for f in failures:
            cats.extend(f.get("failure_category", []))
        from collections import Counter
        top_cat = Counter(cats).most_common(1)
        if top_cat:
            recs.append(f"避免重复错误:本周 {top_cat[0][0]} 失败 {top_cat[0][1]} 次")
    # Hit rate
    hits, total, rate = compute_hit_rate(cards)
    if rate < 50 and total > 0:
        recs.append(f"预测校准:本周命中率 {rate:.0f}%,下次预测乘以 0.9")
    # Engagement
    engs = []
    for s in by_plat.values():
        engs.extend(s["engagement"])
    if engs:
        avg_eng = sum(engs) / len(engs)
        if avg_eng < 3:
            recs.append(f"互动率偏低 ({avg_eng:.1f}%),下期加更多互动型内容(投票/评论征集)")
    return recs[:5]


def generate_report(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    if not vault.exists():
        print(f"[ERROR] Vault not found: {vault}", file=sys.stderr)
        return 2

    # Determine date range
    today = date.today()
    if args.week:
        # ISO week format: 2026-W25
        try:
            year, week = args.week.split("-W")
            year, week = int(year), int(week)
            # ISO week 1 is the week containing Jan 4
            jan4 = date(year, 1, 4)
            start = jan4 - timedelta(days=jan4.isoweekday() - 1) + timedelta(weeks=week - 1)
            end = start + timedelta(days=6)
        except (ValueError, IndexError):
            print(f"[ERROR] Invalid week format: {args.week} (use YYYY-Www, e.g. 2026-W25)", file=sys.stderr)
            return 1
    else:
        end = today
        start = today - timedelta(days=6)
    since = start

    print(f"[INFO] Reviewing {start} to {end}")
    print(f"[INFO] Vault: {vault}")
    print()

    # Filter by platform
    platforms_filter = [args.platform] if args.platform else None

    all_cards = collect_cards(vault, since)
    if platforms_filter:
        all_cards = [c for c in all_cards if c.get("platform") in platforms_filter]
    failures = collect_failures(vault, since)
    dashboards = collect_dashboards(vault)

    if not all_cards:
        print(f"[INFO] No cards found between {start} and {end}.")
        return 0

    # ---- Compute ----
    hits, total, hit_rate = compute_hit_rate(all_cards)
    by_plat = compute_platform_breakdown(all_cards)
    top, bottom = find_top_bottom(all_cards, n=3)
    recs = generate_recommendations(all_cards, by_plat, failures)

    # ---- Render ----
    iso_week = today.isocalendar()
    week_label = f"{iso_week[0]}-W{iso_week[1]:02d}"
    lines = []
    lines.append(f"# 📊 周复盘:{start} ~ {end} ({week_label})\n")
    lines.append(f"## 总览\n")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|---|---|")
    lines.append(f"| 发布条数 | {len(all_cards)} |")
    lines.append(f"| 已发布 | {len([c for c in all_cards if c.get('status') == 'published'])} |")
    lines.append(f"| 总播放 | {sum(c.get('actual_views', 0) or 0 for c in all_cards):,} |")
    lines.append(f"| 命中率 | {hit_rate:.1f}% ({hits}/{total}) |")
    lines.append(f"| 失败记录 | {len(failures)} |\n")

    if by_plat:
        lines.append("## 平台分布\n")
        lines.append("| 平台 | 发布 | 总播放 | 平均互动率 |")
        lines.append("|---|---|---|---|")
        for plat, s in sorted(by_plat.items(), key=lambda x: -x[1]["views"]):
            avg_eng = sum(s["engagement"]) / len(s["engagement"]) if s["engagement"] else 0
            lines.append(f"| {plat} | {s['count']} | {s['views']:,} | {avg_eng:.1f}% |")
        lines.append("")

    if top:
        lines.append("## 🏆 Top 3 内容\n")
        for c in top:
            lines.append(f"- **{c.get('topic', '?')}** ({c.get('platform', '?')}) — {c.get('actual_views', 0):,} 播放")
        lines.append("")

    if bottom:
        lines.append("## 📉 Bottom 3 内容\n")
        for c in bottom:
            lines.append(f"- **{c.get('topic', '?')}** ({c.get('platform', '?')}) — {c.get('actual_views', 0):,} 播放")
        lines.append("")

    if failures:
        lines.append("## 失败分析\n")
        from collections import Counter
        cat_counter = Counter()
        for f in failures:
            cat_counter.update(f.get("failure_category", []))
        lines.append("| 失败类别 | 次数 |")
        lines.append("|---|---|")
        for cat, n in cat_counter.most_common():
            lines.append(f"| {cat} | {n} |")
        lines.append("")

    if recs:
        lines.append("## 下周建议\n")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")
        lines.append("")

    lines.append("---")
    lines.append(f"_Generated by weekly-review.py at {datetime.now().isoformat()}_")

    report = "\n".join(lines)

    if args.dry_run:
        print(report)
        return 0

    out_dir = vault / "05-周复盘"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{week_label}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"[OK] Wrote {out_path.relative_to(vault)}")
    print()
    print("--- PREVIEW ---")
    print(report[:800] + "..." if len(report) > 800 else report)
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Generate weekly review from content cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--vault", help=f"Vault path (default: {DEFAULT_VAULT})")
    p.add_argument("--week", help="ISO week, e.g. 2026-W25 (default: last 7 days)")
    p.add_argument("--platform", help="Filter to one platform")
    p.add_argument("--dry-run", action="store_true", help="Preview only")
    args = p.parse_args()
    sys.exit(generate_report(args))


if __name__ == "__main__":
    main()
