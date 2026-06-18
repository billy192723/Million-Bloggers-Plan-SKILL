#!/usr/bin/env python
"""
fill_douyin_cards.py - Auto-fill 24h review tables from Douyin stats.

Reads stats.json (from fetch_douyin_stats.py) and updates the 24h review
tables in the 7 W1 content cards.

Usage:
  python fill_douyin_cards.py --stats stats.json
  python fill_douyin_cards.py --stats stats.json --vault "E:/知识库/博主计划"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


DEFAULT_VAULT = Path("E:/知识库/博主计划")

# Map of stat field → display value
INDICATOR_MAP = {
    "播放": "播放",
    "views": "播放",
    "view": "播放",
    "点赞": "点赞",
    "likes": "点赞",
    "like": "点赞",
    "评论": "评论",
    "comments": "评论",
    "comment": "评论",
    "涨粉": "涨粉",
    "followers": "涨粉",
    "新粉丝": "涨粉",
}


def parse_views(s: str) -> int:
    """Parse '1.2万' → 12000, '1234' → 1234."""
    if not s:
        return 0
    s = s.replace(",", "").strip()
    if "万" in s:
        try:
            return int(float(s.replace("万", "")) * 10000)
        except ValueError:
            return 0
    if "w" in s.lower():
        try:
            return int(float(s.lower().replace("w", "")) * 10000)
        except ValueError:
            return 0
    try:
        return int(s)
    except ValueError:
        return 0


def extract_title_keyword(title: str) -> str:
    """Extract a unique keyword for matching. Takes first 8 chars or so."""
    if not title:
        return ""
    # Take first 10 chars for fuzzy matching
    return title[:10].strip()


def find_matching_card(stat_video: dict, cards_dir: Path) -> Path | None:
    """Find the content card file that matches a stat video by title."""
    if not cards_dir.exists():
        return None

    stat_title = stat_video.get("title", "") or stat_video.get("topic", "")

    # First pass: exact substring match
    for card in cards_dir.glob("2026-06-*.md"):
        card_topic = ""
        with open(card, "r", encoding="utf-8") as f:
            text = f.read()
        # Try topic from frontmatter
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if m:
            try:
                meta = yaml.safe_load(m.group(1))
                card_topic = meta.get("topic", "")
            except yaml.YAMLError:
                pass
        # Also try H1
        if not card_topic:
            h1_match = re.search(r"^# .+", text, re.MULTILINE)
            if h1_match:
                card_topic = h1_match.group(0).lstrip("# ").strip()

        # Match: stat title in card topic (or vice versa)
        if stat_title and card_topic:
            if stat_title[:5] in card_topic or card_topic[:5] in stat_title:
                return card
            # Try partial match (3+ chars)
            for k in range(3, 6):
                if stat_title[:k] in card_topic:
                    return card
    return None


def update_card_with_stats(card_path: Path, stat_video: dict) -> bool:
    """
    Update the 24h review table in a content card with actual stats.
    Returns True if any field was updated.
    """
    text = card_path.read_text(encoding="utf-8")

    views = stat_video.get("views") or stat_video.get("播放")
    likes = stat_video.get("likes") or stat_video.get("点赞")
    comments = stat_video.get("comments") or stat_video.get("评论")
    followers = stat_video.get("followers") or stat_video.get("涨粉") or stat_video.get("新粉丝")
    completion = stat_video.get("completion_rate") or stat_video.get("完播率")

    today = datetime.now().strftime("%Y-%m-%d")

    # Update the 24h row in the review table
    # Pattern: | 24h | ? | ? | ? | ? | ? | ... |
    updates = [
        (r"\| 24h \| \? \| \? \| \? \| \? \|", f"| 24h | {views} | {likes} | {comments} | {followers} |"),
        (r"\| 6h \| \? \| \? \| \? \| \? \|", f"| 6h | ? | ? | ? | ? |"),
        (r"\| 1h \| \? \| \? \| \? \| \? \|", f"| 1h | ? | ? | ? | ? |"),
    ]

    updated = False
    for pattern, replacement in updates:
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text, count=1)
            updated = True

    if updated:
        card_path.write_text(text, encoding="utf-8")

    return updated


def main():
    p = argparse.ArgumentParser(
        description="Auto-fill 24h review tables from Douyin stats JSON"
    )
    p.add_argument(
        "--stats", required=True,
        help="Path to stats.json (from fetch_douyin_stats.py)"
    )
    p.add_argument(
        "--vault", default=str(DEFAULT_VAULT),
        help=f"Vault path (default: {DEFAULT_VAULT})"
    )
    args = p.parse_args()

    stats_path = Path(args.stats)
    vault = Path(args.vault)

    if not stats_path.exists():
        print(f"[ERROR] Stats file not found: {stats_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(stats_path.read_text(encoding="utf-8"))
    videos = data.get("recent_videos", [])

    if not videos:
        print("[WARN] No videos in stats. Check JSON structure.")
        sys.exit(1)

    print(f"[INFO] Loaded {len(videos)} videos from {stats_path}")

    cards_dir = vault / "国内" / "抖音" / "04-内容卡" / "W1-起号期"
    if not cards_dir.exists():
        print(f"[ERROR] Cards dir not found: {cards_dir}", file=sys.stderr)
        sys.exit(1)

    matched = 0
    for video in videos:
        title = video.get("title", "?")
        card_path = find_matching_card(video, cards_dir)
        if not card_path:
            print(f"  ⚠ No card matched: {title[:40]}")
            continue
        if update_card_with_stats(card_path, video):
            views = video.get("views") or video.get("播放")
            likes = video.get("likes") or video.get("点赞")
            print(f"  ✓ Updated: {card_path.name} (播放 {views} / 点赞 {likes})")
            matched += 1
        else:
            print(f"  ⚠ No 24h row to update in {card_path.name}")

    print(f"\n[OK] Updated {matched} / {len(videos)} cards")


if __name__ == "__main__":
    main()
