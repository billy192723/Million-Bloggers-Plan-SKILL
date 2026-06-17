#!/usr/bin/env python
"""
daily-content.py - Generate daily content card(s) for the active platforms.

Used by the /daily command in the creator-incubator SKILL.

Reads from the user's vault:
  - _global/00-profile.md (active platforms + niche)
  - _global/06-inspiration.md (unused inspirations)
  - _global/07-failures.md (avoid patterns)
  - references/holiday-calendar.md (upcoming events)

Writes new content cards to each active platform's 04-cards/ directory.

Usage:
  python daily-content.py --generate              # Generate today's cards (1 per active platform)
  python daily-content.py --platform=抖音          # Generate for one platform
  python daily-content.py --count=3               # Generate 3 ideas per platform
  python daily-content.py --dry-run               # Preview without writing
  python daily-content.py --idea "AI 工具横评"    # Use specific idea
  python daily-content.py --vault "E:/知识库/博主计划"  # Override vault path
"""

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---- Configuration ----
DEFAULT_VAULT = Path("E:/知识库/博主计划")
TEMPLATE_FILE = Path(__file__).parent.parent / "templates" / "daily-content-card.md"

PLATFORM_DURATIONS = {
    "小红书": "图文 600-1200 字 + 9 图",
    "抖音": "21-34 秒竖屏",
    "B站": "8-12 分钟长视频",
    "视频号": "1-3 分钟",
    "公众号": "1500-2500 字长文",
    "YouTube": "8-12 分钟横屏",
    "TikTok": "15-30 秒竖屏",
    "Instagram": "Reels 15-30 秒或 9 图",
    "X": "≤280 字符或推文串 1/n",
}


# ---- Helpers ----
def parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
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


def find_active_platforms(vault: Path) -> list:
    """Read _global/00-profile.md, return list of (region, platform) for active ones."""
    profile = parse_frontmatter(vault / "_global" / "00-profile.md")
    target_platforms = profile.get("target_platforms", [])

    if not target_platforms:
        # Fallback: read from raw markdown checkboxes
        profile_file = vault / "_global" / "00-profile.md"
        if profile_file.exists():
            text = profile_file.read_text(encoding="utf-8")
            for region, plats in [
                ("CN", ["小红书", "抖音", "B站", "视频号", "公众号"]),
                ("INTL", ["YouTube", "TikTok", "Instagram", "X"]),
            ]:
                for p in plats:
                    if f"- [x] {p}" in text or f"- [X] {p}" in text:
                        target_platforms.append((region, p))

    # Normalize: convert lists to tuples (in case YAML stored as list-of-list)
    normalized = []
    for item in target_platforms:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            normalized.append((str(item[0]), str(item[1])))
        elif isinstance(item, str):
            # "region:platform" format
            if ":" in item:
                r, p = item.split(":", 1)
                normalized.append((r.strip(), p.strip()))

    return normalized if normalized else [("CN", "抖音")]


def find_unused_inspirations(vault: Path) -> list:
    """Read _global/06-inspiration.md, return unused entries with metadata."""
    insp_file = vault / "_global" / "06-inspiration.md"
    if not insp_file.exists():
        return []

    inspirations = []
    text = insp_file.read_text(encoding="utf-8")
    # Split on --- frontmatter blocks
    blocks = re.findall(r"---\n(.*?)\n---\n(.*?)(?=---|\Z)", text, re.DOTALL)
    for fm, body in blocks:
        try:
            meta = yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            continue
        if meta.get("type") == "inspiration" and meta.get("status") == "unused":
            inspirations.append({**meta, "_body": body.strip()[:200]})
    return inspirations


def find_upcoming_holidays(vault: Path, days_ahead: int = 7) -> list:
    """Return list of (date, name, themes) for upcoming holidays in next N days."""
    # Built-in: most relevant 2026-2027 Chinese/AI-relevant events
    EVENTS = [
        ("01-01", "元旦", "新年计划 年度回顾"),
        ("02-14", "情人节", "礼物 情侣"),
        ("03-08", "妇女节", "女性独立"),
        ("04-23", "世界读书日", "书单 阅读"),
        ("05-04", "青年节", "青春 梦想"),
        ("05-20", "520 告白日", "表白 情侣"),
        ("06-01", "儿童节", "亲子 童年"),
        ("06-18", "618 年中大促", "购物 比价"),
        ("07-04", "美国独立日", ""),
        ("08-04", "七夕", "情侣 礼物"),
        ("09-10", "教师节", "老师 感恩"),
        ("10-01", "国庆", "出游 爱国"),
        ("10-31", "万圣节", "恐怖 cosplay"),
        ("11-11", "双 11", "购物 比价"),
        ("11-26", "感恩节", "感恩"),
        ("12-25", "圣诞节", "礼物"),
    ]
    today = date.today()
    upcoming = []
    for mmdd, name, themes in EVENTS:
        try:
            month, day = mmdd.split("-")
            event_date = date(today.year, int(month), int(day))
            if event_date < today:
                event_date = date(today.year + 1, int(month), int(day))
            days_until = (event_date - today).days
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    "date": event_date.isoformat(),
                    "days_until": days_until,
                    "name": name,
                    "themes": themes,
                })
        except ValueError:
            continue
    return sorted(upcoming, key=lambda x: x["days_until"])


def find_failure_warnings(vault: Path) -> list:
    """Read _global/07-failures.md, return high-severity failure categories."""
    fail_file = vault / "_global" / "07-failures.md"
    if not fail_file.exists():
        return []

    warnings = []
    text = fail_file.read_text(encoding="utf-8")
    blocks = re.findall(r"---\n(.*?)\n---", text, re.DOTALL)
    for fm in blocks:
        try:
            meta = yaml.safe_load(fm) or {}
        except yaml.YAMLError:
            continue
        if meta.get("severity") == "high" and meta.get("failure_category"):
            warnings.append({
                "category": meta.get("failure_category", []),
                "lesson": meta.get("lesson", ""),
                "id": meta.get("id", ""),
            })
    return warnings


def render_card_template(
    *,
    today: str,
    card_id: str,
    topic: str,
    niche: str,
    platform: str,
    region: str,
    duration: str,
    predicted_views: str,
    predicted_engagement_rate: str,
    basis: str,
    hook_a: str,
    hook_b: str,
    body_main: str = "",
    inspiration_ref: str = "",
    holiday_ref: str = "",
    failure_warnings: str = "",
) -> str:
    """Render a content card using the template format."""
    warnings_block = ""
    if failure_warnings:
        warnings_block = "\n## ⚠️ 自动警告(基于历史失败)\n\n"
        for w in failure_warnings:
            warnings_block += f"- **{w['category']}**: {w['lesson']}\n"

    inspiration_block = f"\n## 灵感来源\n\n{inspiration_ref}\n" if inspiration_ref else ""
    holiday_block = f"\n## 节日参考\n\n{holiday_ref}\n" if holiday_ref else ""

    return f"""---
type: daily-content-card
date: {today}
card_id: {card_id}
topic: "{topic}"
niche: {niche}
platform: {platform}
region: {region}
duration_seconds: 0
predicted_views: "{predicted_views}"
predicted_engagement_rate: "{predicted_engagement_rate}"
prediction_confidence: medium
prediction_basis: "{basis}"
status: draft
inspiration_ref: "{inspiration_ref}"
---

# {topic}

## 拍摄清单 🎬

- [ ] 真人出镜 3 秒(开场钩子)
- [ ] 主体内容录屏/出镜
- [ ] 字幕版
- [ ] 封面图(标题 + 主体)
{inspiration_block}
{holiday_block}
{warnings_block}
## 钩子选项(选 1)

### A. ⭐ 推荐
{hook_a}

### B. 备选
{hook_b}

## 完整脚本

(由 LLM 在生成时填充 / 手动撰写)

## 标签

(由 LLM 填充:`#AI` `#工具` ...)

## 发布设置

- 平台: {platform}
- 时长: {duration}
- 时段: (建议 19:00-22:00 高峰)
- 封面: (待制作)

## 流量预估

- 预测流量: {predicted_views}
- 预测互动率: {predicted_engagement_rate}
- 预测依据: {basis}

## CTA

- 评论: "扣 1 告诉我你的看法"
- 关注: "关注我,日更 AI 实操"
"""


# ---- Main ----
def generate(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    vault.mkdir(parents=True, exist_ok=True)

    if not vault.exists():
        print(f"[ERROR] Vault not found: {vault}", file=sys.stderr)
        return 2

    today = date.today().isoformat()
    platforms = find_active_platforms(vault)
    if args.platform:
        platforms = [(r, p) for r, p in platforms if p == args.platform]
        if not platforms:
            print(f"[WARN] Platform {args.platform} not in active list", file=sys.stderr)
            return 1

    inspirations = find_unused_inspirations(vault)
    holidays = find_upcoming_holidays(vault)
    failures = find_failure_warnings(vault)

    print(f"[INFO] Active platforms: {[p for _, p in platforms]}")
    print(f"[INFO] Inspirations available: {len(inspirations)}")
    print(f"[INFO] Upcoming holidays (7d): {[h['name'] for h in holidays]}")
    print(f"[INFO] High-severity failures to avoid: {len(failures)}")
    print()

    cards_created = 0
    count = args.count

    for region, platform in platforms:
        for i in range(count):
            card_id = f"{today.replace('-', '')}-{platform[:2]}-{i+1:03d}"

            # If user provided idea, use it
            topic = args.idea or f"[AI 提示] 用 {platform} 表达 [niche] 的 [角度]"

            # Pick inspiration
            inspiration = inspirations[i] if i < len(inspirations) else None
            insp_ref = ""
            if inspiration:
                insp_ref = f"灵感: {inspiration.get('content', '')} (id: {inspiration.get('id', '')})"

            # Pick holiday
            holiday_ref = ""
            if holidays and i < len(holidays):
                h = holidays[i % len(holidays)]
                holiday_ref = f"节日: {h['name']} ({h['days_until']} 天后), 主题: {h['themes']}"

            # Hooks
            hook_a = f"[钩子 A - 由 LLM 生成,基于:反差 + 数字]"
            hook_b = f"[钩子 B - 由 LLM 生成,基于:痛点 + 身份]"

            # Failure warnings
            fail_str = ""
            if failures:
                fail_str = f"{len(failures)} 条历史失败模式需要避免(详见文件)"

            # Render
            card_content = render_card_template(
                today=today,
                card_id=card_id,
                topic=topic,
                niche="[用户 niche]",
                platform=platform,
                region=region,
                duration=PLATFORM_DURATIONS.get(platform, ""),
                predicted_views="[依赖 LLM 评估]",
                predicted_engagement_rate="[依赖 LLM 评估]",
                basis="基线 × 钩子加成 × 时段加成 × 账号权重",
                hook_a=hook_a,
                hook_b=hook_b,
                inspiration_ref=insp_ref,
                holiday_ref=holiday_ref,
                failure_warnings=fail_str,
            )

            # Write
            if region == "CN":
                region_folder = "国内"
            else:
                region_folder = "国外"
            out_dir = vault / region_folder / platform / "04-内容卡" / f"W-{today[:7]}"
            if args.dry_run:
                print(f"[DRY] Would write: {out_dir}/{today}-{card_id}.md")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"{today}-{card_id}.md"
                out_path.write_text(card_content, encoding="utf-8")
                print(f"✓ {out_path.relative_to(vault)}")
                cards_created += 1

    print()
    if args.dry_run:
        print(f"[DRY-RUN] Would create {len(platforms) * count} cards.")
    else:
        print(f"[OK] Created {cards_created} content cards.")
        print()
        print("Next steps:")
        print("  1. LLM fills in the [brackets] in each card")
        print("  2. Edit / refine each card")
        print("  3. Mark status=draft → filming when recording starts")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Generate daily content cards for active platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--vault", help=f"Vault path (default: {DEFAULT_VAULT})")
    p.add_argument("--platform", help="Generate for one platform only")
    p.add_argument("--count", type=int, default=1, help="Cards per platform (default: 1)")
    p.add_argument("--idea", help="Specific idea/topic to use")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.add_argument("--generate", action="store_true", default=True, help="(default action)")
    args = p.parse_args()
    sys.exit(generate(args))


if __name__ == "__main__":
    main()
