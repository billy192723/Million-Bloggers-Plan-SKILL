#!/usr/bin/env python
"""
ab-test-tracker.py (R5)

Read all A/B test cards under a platform's 04-内容卡/ab/ directory,
evaluate winner/loser for each group, and write results back to frontmatter.

Usage:
  python ab-test-tracker.py --platform=小红书
  python ab-test-tracker.py --group=2026-06-17-claude45
  python ab-test-tracker.py --platform=小红书 --dry-run
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(1)


VAULT = Path("E:/知识库/博主计划")


def parse_card(path: Path) -> dict:
    """Read .md, return frontmatter + body."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {"_body": text, "_path": path}
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {"_body": text, "_path": path}
    meta["_path"] = path
    meta["_body"] = text
    return meta


def write_card(path: Path, meta: dict, body: str) -> None:
    """Write back frontmatter + body."""
    # Strip _body and _path before serialization
    clean = {k: v for k, v in meta.items() if not k.startswith("_")}
    fm_str = yaml.safe_dump(clean, allow_unicode=True, sort_keys=False)
    path.write_text(f"---\n{fm_str}---\n{body}", encoding="utf-8")


def extract_body(text: str) -> str:
    """Extract body (after frontmatter)."""
    m = re.match(r"^---\n.*?\n---\n(.*)$", text, re.DOTALL)
    return m.group(1) if m else text


def evaluate_group(cards: list) -> dict:
    """Given cards in same ab_group, return winner/loser/significance."""
    valid = [c for c in cards if c.get("actual_views") is not None]
    if len(valid) < len(cards):
        return {"status": "pending", "missing": len(cards) - len(valid)}
    if len(valid) < 2:
        return {"status": "single-variant"}

    ranked = sorted(valid, key=lambda c: c["actual_views"], reverse=True)
    winner = ranked[0]
    loser = ranked[-1]

    if winner["actual_views"] == 0:
        return {"status": "no-data"}

    lift = (winner["actual_views"] - loser["actual_views"]) / loser["actual_views"]
    threshold = 0.3 if len(valid) == 2 else 0.5
    significant = lift >= threshold

    # Engagement tie-breaker
    winner_eng = winner.get("actual_engagement_rate") or 0
    loser_eng = loser.get("actual_engagement_rate") or 0
    eng_lift = winner_eng - loser_eng

    return {
        "status": "evaluated",
        "winner_variant": winner.get("ab_variant"),
        "winner_card": str(winner["_path"].name),
        "loser_variant": loser.get("ab_variant"),
        "loser_card": str(loser["_path"].name),
        "winner_views": winner["actual_views"],
        "loser_views": loser["actual_views"],
        "views_lift_pct": round(lift * 100, 1),
        "winner_engagement": winner_eng,
        "loser_engagement": loser_eng,
        "engagement_lift_pp": round(eng_lift, 2),
        "significant": significant,
        "interpretation": (
            "显著胜出" if significant else "差异不显著,需更多数据"
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--platform", help="Filter by platform")
    p.add_argument("--group", help="Specific ab_group id")
    p.add_argument("--dry-run", action="store_true", help="Print only, don't write")
    args = p.parse_args()

    # Find all ab cards
    if args.platform:
        search_dirs = [VAULT / "国内" / args.platform / "04-内容卡" / "ab",
                       VAULT / "国外" / args.platform / "04-内容卡" / "ab"]
    else:
        search_dirs = list((VAULT / "国内").rglob("04-内容卡/ab")) + \
                      list((VAULT / "国外").rglob("04-内容卡/ab"))

    all_cards = []
    for d in search_dirs:
        if d.exists():
            for f in d.glob("*.md"):
                all_cards.append(parse_card(f))

    # Filter
    if args.group:
        all_cards = [c for c in all_cards if c.get("ab_group") == args.group]
    else:
        all_cards = [c for c in all_cards if c.get("type") == "ab-test-card"]

    if not all_cards:
        print("[INFO] No A/B test cards found.")
        return 0

    # Group by ab_group
    groups = defaultdict(list)
    for c in all_cards:
        g = c.get("ab_group", "ungrouped")
        groups[g].append(c)

    print(f"[OK] Found {len(all_cards)} A/B cards in {len(groups)} groups.\n")

    updated = 0
    for group_id, cards in groups.items():
        print(f"=== Group: {group_id} ({len(cards)} variants) ===")
        result = evaluate_group(cards)
        print(f"  Status: {result['status']}")

        if result["status"] == "pending":
            print(f"  Missing: {result['missing']} card(s) without actuals")
            print()
            continue
        if result["status"] == "no-data" or result["status"] == "single-variant":
            print()
            continue

        print(f"  Winner: {result['winner_variant']} ({result['winner_views']} views)")
        print(f"  Loser:  {result['loser_variant']} ({result['loser_views']} views)")
        print(f"  Lift:   {result['views_lift_pct']:+.1f}% views, "
              f"{result['engagement_lift_pp']:+.2f}pp engagement")
        print(f"  Verdict: {result['interpretation']}")
        print()

        # Write back
        if not args.dry_run:
            for c in cards:
                if c.get("ab_variant") == result["winner_variant"]:
                    c["ab_result"] = "winner"
                elif c.get("ab_variant") == result["loser_variant"]:
                    c["ab_result"] = "loser"
                else:
                    c["ab_result"] = "tie"
                body = extract_body(c["_body"])
                write_card(c["_path"], c, body)
                updated += 1

    if not args.dry_run:
        print(f"[OK] Updated {updated} cards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
