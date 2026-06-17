#!/usr/bin/env python
"""
failure-manager.py - Manage the failure log.

Used by the /failure command.

Operations:
  add     - Log a failure (auto-categorize + severity)
  list    - List failures, filter by category/severity
  patterns - Analyze recurring failure patterns
  archive - Move old failures to archive

Failures stored as YAML frontmatter blocks in:
  _global/07-failures.md

Failure categories (auto-detected from reason text):
  标题党 (clickbait)
  时段错 (wrong timing)
  钩子弱 (weak hook)
  内容空洞 (empty content)
  同质化 (duplicate)
  争议性 (controversy)
  违规 (violation)
  设备/技术 (technical)

Usage:
  python failure-manager.py add 2026-06-15-002 --reason="标题党被限流"
  python failure-manager.py list
  python failure-manager.py list --category=标题党 --severity=high
  python failure-manager.py patterns
  python failure-manager.py archive --days=180
"""

import argparse
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


DEFAULT_VAULT = Path("E:/知识库/博主计划")
FAILURE_FILE = "_global/07-failures.md"

CATEGORIES = ["标题党", "时段错", "钩子弱", "内容空洞", "同质化", "争议性", "违规", "设备/技术"]


def auto_categorize(reason: str) -> list:
    """Heuristic categorization based on reason text."""
    text = reason.lower()
    cats = []
    if any(k in text for k in ["震惊", "必看", "标题党", "夸张", "标题"]):
        cats.append("标题党")
    if any(k in text for k in ["凌晨", "深夜", "时段", "时间"]):
        cats.append("时段错")
    if any(k in text for k in ["钩子", "开头", "前3秒", "跳出"]):
        cats.append("钩子弱")
    if any(k in text for k in ["内容", "空洞", "没干货", "水"]):
        cats.append("内容空洞")
    if any(k in text for k in ["同质", "重复", "相似", "搬运"]):
        cats.append("同质化")
    if any(k in text for k in ["争议", "负面", "评论骂", "差评"]):
        cats.append("争议性")
    if any(k in text for k in ["违规", "下架", "警告", "敏感"]):
        cats.append("违规")
    if any(k in text for k in ["糊", "声音", "字幕", "技术", "卡"]):
        cats.append("设备/技术")
    if not cats:
        cats.append("其他")
    return cats


def auto_severity(actual_views, predicted_views) -> str:
    """Heuristic severity from underperformance."""
    if not predicted_views:
        return "low"
    low = 0
    if isinstance(predicted_views, str) and "-" in predicted_views:
        try:
            low = int(predicted_views.split("-")[0])
        except (ValueError, IndexError):
            low = 0
    elif isinstance(predicted_views, (int, float)):
        low = int(predicted_views * 0.5)  # 50% of midpoint
    if low <= 0 or not actual_views:
        return "low"
    ratio = actual_views / low
    if ratio < 0.1:
        return "high"
    elif ratio < 0.3:
        return "medium"
    else:
        return "low"


def parse_block(text: str) -> tuple:
    m = re.match(r"^---\n(.*?)\n---\n(.*?)(?=---|\Z)", text, re.DOTALL)
    if not m:
        return None, None
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None, None
    body = m.group(2).strip()
    return meta, body


def serialize_block(meta: dict, body: str = "") -> str:
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
    return f"---\n{fm}---\n{body}\n"


def load_failures(vault: Path) -> list:
    path = vault / FAILURE_FILE
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.MULTILINE | re.DOTALL)
    failures = []
    for m in pattern.finditer(text):
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if meta.get("type") == "failure":
            failures.append({"meta": meta, "body": ""})
    return failures


def save_failures(vault: Path, failures: list):
    path = vault / FAILURE_FILE
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    header = """---
type: failure-log-header
created: 2026-06-17
status: active
---

# 失败案例库 (R12)

> 由 `/failure add <card_id> --reason="..."` 写入。
> `/daily` 跑时会读取高严重度失败,主动避开同类错误。
"""
    parts = [header]
    for f in failures:
        meta = {k: v for k, v in f["meta"].items() if k != "_raw"}
        fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
        parts.append(f"---\n{fm}---\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def cmd_add(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    failures = load_failures(vault)

    today = date.today().isoformat()
    seq = 1
    for f in failures:
        m = re.match(r"FAIL-\d{8}-(\d+)", f["meta"].get("id", ""))
        if m:
            seq = max(seq, int(m.group(1)) + 1)
    new_id = f"FAIL-{today.replace('-', '')}-{seq:03d}"

    categories = args.category.split(",") if args.category else auto_categorize(args.reason)
    severity = args.severity or "medium"

    # Try to find the actual card for context
    card = None
    for pattern in vault.rglob("04-内容卡/*.md"):
        if pattern.stem == args.card_id or args.card_id in pattern.stem:
            m = re.match(r"^---\n(.*?)\n---", pattern.read_text(encoding="utf-8"), re.DOTALL)
            if m:
                try:
                    card = yaml.safe_load(m.group(1))
                except yaml.YAMLError:
                    pass
            break

    actual = (card or {}).get("actual_views")
    predicted = (card or {}).get("predicted_views")
    if not args.severity:
        auto_sev = auto_severity(actual, predicted)
        if auto_sev == "high":
            severity = "high"

    meta = {
        "type": "failure",
        "id": new_id,
        "date": today,
        "card_id": args.card_id,
        "platform": (card or {}).get("platform", "?"),
        "topic": (card or {}).get("topic", "?"),
        "failure_reason": args.reason,
        "failure_category": categories,
        "actual_views": actual,
        "predicted_views": predicted,
        "engagement_rate": (card or {}).get("actual_engagement_rate"),
        "severity": severity,
        "status": "analyzed",
        "tags": categories,
    }
    if not card:
        meta["note"] = f"Card not found: {args.card_id} (manual entry)"

    failures.append({"meta": meta, "body": ""})
    save_failures(vault, failures)

    print(f"✓ Logged {new_id}")
    print(f"  Category: {', '.join(categories)}")
    print(f"  Severity: {severity}")
    print(f"  Reason: {args.reason}")
    if severity == "high":
        print(f"  ⭐ High severity — /daily will auto-avoid this pattern")
    return 0


def cmd_list(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    failures = load_failures(vault)

    if args.category:
        failures = [f for f in failures if args.category in f["meta"].get("failure_category", [])]
    if args.severity:
        failures = [f for f in failures if f["meta"].get("severity") == args.severity]
    if args.platform:
        failures = [f for f in failures if f["meta"].get("platform") == args.platform]

    if not failures:
        print("[INFO] No failures match filter.")
        return 0

    print(f"| ID | 日期 | 平台 | 严重度 | 类别 | 原因 |")
    print(f"|---|---|---|---|---|---|")
    for f in failures:
        m = f["meta"]
        cats = ",".join(m.get("failure_category", []))
        reason = m.get("failure_reason", "")[:50]
        if len(m.get("failure_reason", "")) > 50:
            reason += "..."
        sev = m.get("severity", "?")
        marker = "⚠️" if sev == "high" else "  "
        print(f"| {m.get('id', '?')} | {m.get('date', '?')} | {m.get('platform', '?')} | {sev} {marker}| {cats} | {reason} |")
    return 0


def cmd_patterns(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    failures = load_failures(vault)

    if not failures:
        print("[INFO] No failures recorded yet.")
        return 0

    cat_counter = Counter()
    for f in failures:
        cat_counter.update(f["meta"].get("failure_category", []))

    print(f"# 失败模式分析 ({len(failures)} 条记录)\n")
    print("## 类别分布\n")
    print("| 类别 | 次数 | 占比 |")
    print("|---|---|---|")
    for cat, n in cat_counter.most_common():
        pct = n / len(failures) * 100
        print(f"| {cat} | {n} | {pct:.0f}% |")
    print()

    # Top patterns
    print("## 高频模式\n")
    for cat, n in cat_counter.most_common(3):
        if n >= 2:
            examples = [f for f in failures if cat in f["meta"].get("failure_category", [])][:2]
            reasons = [f["meta"].get("failure_reason", "") for f in examples]
            print(f"**{cat}** ({n} 次):")
            for r in reasons:
                print(f"  - {r}")
            print()

    return 0


def cmd_archive(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    failures = load_failures(vault)

    cutoff = date.today() - timedelta(days=args.days)
    to_archive = []
    kept = []
    for f in failures:
        d_str = f["meta"].get("date")
        if d_str:
            try:
                d = date.fromisoformat(d_str)
                if d < cutoff:
                    to_archive.append(f)
                    continue
            except ValueError:
                pass
        kept.append(f)

    if not to_archive:
        print(f"[INFO] No failures to archive (cutoff: {cutoff}).")
        return 0

    archive_file = vault / "_global" / "07-failures-archive.md"
    archive_file.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if archive_file.exists():
        for b in re.split(r"^---\n", archive_file.read_text(encoding="utf-8"), flags=re.MULTILINE):
            b = b.strip()
            if not b:
                continue
            meta, body = parse_block("---\n" + b)
            if meta and meta.get("type") == "failure":
                existing.append({"meta": meta, "body": body})
    existing.extend(to_archive)
    parts = ["---\ntype: failure-archive\n---\n\n# Archived Failures\n\n"]
    for f in existing:
        parts.append(serialize_block(f["meta"], f["body"]))
    archive_file.write_text("\n".join(parts), encoding="utf-8")

    save_failures(vault, kept)
    print(f"✓ Archived {len(to_archive)} failures (>{args.days} days old).")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Manage the failure log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--vault", help=f"Vault path (default: {DEFAULT_VAULT})")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Log a new failure")
    p_add.add_argument("card_id", help="Card ID that flopped (e.g. 2026-06-15-002)")
    p_add.add_argument("--reason", required=True, help="Why did it flop")
    p_add.add_argument("--category", help="Override auto-categorization (comma-separated)")
    p_add.add_argument("--severity", help="Override auto-severity: low/medium/high")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List failures")
    p_list.add_argument("--category", help=f"Filter by category: {CATEGORIES}")
    p_list.add_argument("--severity", help="Filter: low/medium/high")
    p_list.add_argument("--platform", help="Filter by platform")
    p_list.set_defaults(func=cmd_list)

    p_pat = sub.add_parser("patterns", help="Analyze failure patterns")
    p_pat.set_defaults(func=cmd_patterns)

    p_arc = sub.add_parser("archive", help="Move old failures to archive")
    p_arc.add_argument("--days", type=int, default=180, help="Archive after N days (default: 180)")
    p_arc.set_defaults(func=cmd_archive)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
