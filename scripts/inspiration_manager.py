#!/usr/bin/env python
"""
inspiration-manager.py - Manage the inspiration pool.

Used by the /inspire command.

Operations:
  add     - Add a new inspiration with auto-scoring
  list    - List inspirations, filter by status
  link    - Mark an inspiration as used in a specific card
  archive - Move old used inspirations to archive

Inspirations are stored as YAML frontmatter blocks in:
  _global/06-inspiration.md

Each inspiration is auto-scored (1-5) on 5 dimensions:
  - 时效性 (timeliness)
  - 搜索潜力 (search potential)
  - 制作成本 (production cost, INVERTED: 5 = cheapest)
  - 能力匹配 (skill match)
  - 差异化 (differentiation)

Total score: 0-25. >=18 = high potential.

Usage:
  python inspiration-manager.py add "对比 5 个 AI 写作工具的实际工作流" --tags=AI,对比
  python inspiration-manager.py list
  python inspiration-manager.py list --status=unused --priority=4
  python inspiration-manager.py link INS-2026-06-17-001 --card=2026-06-20-001
  python inspiration-manager.py archive --days=90
  python inspiration-manager.py --vault "E:/..."
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


DEFAULT_VAULT = Path("E:/知识库/博主计划")
INSPIRATION_FILE = "_global/06-inspiration.md"


def parse_block(text: str) -> tuple:
    """Parse one frontmatter block from inspiration file."""
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
    """Serialize a single block to markdown."""
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
    return f"---\n{fm}---\n{body}\n"


def load_inspirations(vault: Path) -> list:
    """Load all inspirations from the vault."""
    path = vault / INSPIRATION_FILE
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # Find all frontmatter blocks: ---...\n---\n
    # Pattern: triple-dash line, content, triple-dash line
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.MULTILINE | re.DOTALL)
    inspirations = []
    for m in pattern.finditer(text):
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if meta.get("type") == "inspiration":
            inspirations.append({"meta": meta, "body": ""})
    return inspirations


def save_inspirations(vault: Path, inspirations: list, header: str = ""):
    """Write all inspirations back to file."""
    path = vault / INSPIRATION_FILE
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    if not header:
        header = """---
type: inspiration-pool-header
created: 2026-06-17
status: active
---

# 灵感库 (R11)

> 由 `/inspire add <text>` 写入。
> `/daily` 跑时会自动匹配未使用灵感 + 当前热点。

## 🆕 未使用

"""
    parts = [header]
    for insp in inspirations:
        meta = {k: v for k, v in insp["meta"].items() if k != "_raw"}
        fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
        parts.append(f"---\n{fm}---\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def generate_id() -> str:
    today = date.today().isoformat().replace("-", "")
    return f"INS-{today}-XXX"  # caller fills XXX


def auto_score(content: str) -> dict:
    """
    Heuristic auto-scoring. In production this is done by LLM.
    Here we use simple keyword signals to suggest a starting score.
    """
    scores = {
        "timeliness": 3,
        "search_potential": 3,
        "cost_inverted": 3,  # 5=cheap, 1=expensive
        "skill_match": 3,
        "differentiation": 3,
    }
    # Heuristics
    text = content.lower()
    # Timeliness signals
    if any(k in text for k in ["刚刚", "最新", "今天", "发布", "官宣", "刚出", "2026"]):
        scores["timeliness"] = 5
    if any(k in text for k in ["长期", "经典", "永恒"]):
        scores["timeliness"] = 2
    # Search potential
    if any(k in text for k in ["怎么", "如何", "推荐", "排行", "对比", "测评"]):
        scores["search_potential"] = 5
    if any(k in text for k in ["感想", "心情", "日记"]):
        scores["search_potential"] = 1
    # Cost (assume simple text = cheap, video = expensive)
    if any(k in text for k in ["视频", "拍", "vlog", "直播"]):
        scores["cost_inverted"] = 2
    if any(k in text for k in ["想法", "观点", "短评", "一句话"]):
        scores["cost_inverted"] = 5
    # Differentiation (generic = low, specific = high)
    if len(content) > 50:
        scores["differentiation"] = 4

    total = sum(scores.values())
    return {"scores": scores, "total": total}


def cmd_add(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    inspirations = load_inspirations(vault)

    today = date.today().isoformat()
    # Find next sequence number
    seq = 1
    for insp in inspirations:
        m = re.match(r"INS-\d{8}-(\d+)", insp["meta"].get("id", ""))
        if m:
            seq = max(seq, int(m.group(1)) + 1)
    new_id = f"INS-{today.replace('-', '')}-{seq:03d}"

    tags = args.tags.split(",") if args.tags else []
    score = auto_score(args.content)

    meta = {
        "type": "inspiration",
        "id": new_id,
        "created": today,
        "content": args.content,
        "tags": tags,
        "status": "unused",
        "used_in_card": None,
        "related_trend": None,
        "scores": score["scores"],
        "total_score": score["total"],
    }
    inspirations.append({"meta": meta, "body": ""})
    save_inspirations(vault, inspirations)

    print(f"✓ Added {new_id} (score: {score['total']}/25)")
    print(f"  Content: {args.content[:80]}{'...' if len(args.content) > 80 else ''}")
    if score["total"] >= 18:
        print(f"  ⭐ High potential — will be auto-matched in /daily")
    elif score["total"] < 10:
        print(f"  ⚠ Low potential — consider refining or skipping")
    return 0


def cmd_list(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    inspirations = load_inspirations(vault)

    if args.status:
        inspirations = [i for i in inspirations if i["meta"].get("status") == args.status]
    if args.priority:
        threshold = int(args.priority) * 5
        inspirations = [i for i in inspirations if i["meta"].get("total_score", 0) >= threshold]

    if not inspirations:
        print(f"[INFO] No inspirations match filter.")
        return 0

    print(f"| ID | 状态 | 评分 | 内容 |")
    print(f"|---|---|---|---|")
    for insp in inspirations:
        m = insp["meta"]
        content = m.get("content", "")[:60]
        if len(m.get("content", "")) > 60:
            content += "..."
        score = m.get("total_score", 0)
        marker = "⭐" if score >= 18 else "  "
        print(f"| {m.get('id', '?')} | {m.get('status', '?')} | {score}/25 {marker}| {content} |")
    return 0


def cmd_link(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    inspirations = load_inspirations(vault)

    target = None
    for insp in inspirations:
        if insp["meta"].get("id") == args.id:
            target = insp
            break
    if not target:
        print(f"[ERROR] Inspiration not found: {args.id}", file=sys.stderr)
        return 1

    target["meta"]["status"] = "used"
    target["meta"]["used_in_card"] = args.card
    target["meta"]["used_at"] = date.today().isoformat()
    save_inspirations(vault, inspirations)
    print(f"✓ Linked {args.id} → {args.card}")
    return 0


def cmd_archive(args) -> int:
    vault = Path(args.vault) if args.vault else DEFAULT_VAULT
    inspirations = load_inspirations(vault)

    cutoff = date.today() - timedelta(days=args.days)
    to_archive = []
    kept = []
    for insp in inspirations:
        meta = insp["meta"]
        used_at = meta.get("used_at")
        if meta.get("status") == "used" and used_at:
            try:
                d = date.fromisoformat(used_at)
                if d < cutoff:
                    to_archive.append(insp)
                    continue
            except ValueError:
                pass
        kept.append(insp)

    if not to_archive:
        print(f"[INFO] No inspirations to archive (cutoff: {cutoff}).")
        return 0

    # Write archive
    archive_file = vault / "_global" / "06-inspiration-archive.md"
    archive_file.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if archive_file.exists():
        existing_text = archive_file.read_text(encoding="utf-8")
        for b in re.split(r"^---\n", existing_text, flags=re.MULTILINE):
            b = b.strip()
            if not b:
                continue
            meta, body = parse_block("---\n" + b)
            if meta:
                existing.append({"meta": meta, "body": body})
    existing.extend(to_archive)
    parts = ["---\ntype: inspiration-archive\n---\n\n# Archived Inspirations\n\n"]
    for insp in existing:
        parts.append(serialize_block(insp["meta"], insp["body"]))
    archive_file.write_text("\n".join(parts), encoding="utf-8")

    # Save remaining
    save_inspirations(vault, kept)
    print(f"✓ Archived {len(to_archive)} inspirations (>{args.days} days old).")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Manage the inspiration pool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--vault", help=f"Vault path (default: {DEFAULT_VAULT})")
    sub = p.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new inspiration")
    p_add.add_argument("content", help="Inspiration text")
    p_add.add_argument("--tags", help="Comma-separated tags")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List inspirations")
    p_list.add_argument("--status", help="Filter by status: unused/queued/used")
    p_list.add_argument("--priority", type=int, help="Min priority (1-5, multiplies by 5 for score)")
    p_list.set_defaults(func=cmd_list)

    # link
    p_link = sub.add_parser("link", help="Mark inspiration as used in a card")
    p_link.add_argument("id", help="Inspiration ID (e.g. INS-2026-06-17-001)")
    p_link.add_argument("--card", required=True, help="Card ID it was used in")
    p_link.set_defaults(func=cmd_link)

    # archive
    p_arc = sub.add_parser("archive", help="Move old used inspirations to archive")
    p_arc.add_argument("--days", type=int, default=90, help="Archive after N days (default: 90)")
    p_arc.set_defaults(func=cmd_archive)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
