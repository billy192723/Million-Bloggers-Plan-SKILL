#!/usr/bin/env python
"""
read_file.py - Safely read a markdown file with YAML frontmatter.

Used by the agent (Hermes) to load SKILL files and Obsidian notes.
"""

import re
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

try:
    import yaml
except ImportError:
    print("[ERROR] pyyaml required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """
    Parse YAML frontmatter from a markdown string.
    Returns (metadata_dict_or_None, body_text).

    Handles:
    - Missing frontmatter → (None, content)
    - Empty frontmatter → ({}, content)
    - Multi-line YAML values
    - Comments and special chars
    """
    if not content.startswith("---"):
        return None, content
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", content, re.DOTALL)
    if not m:
        return None, content
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"[WARN] YAML parse error: {e}", file=sys.stderr)
        meta = None
    body = content[m.end():]
    return meta, body


def parse_frontmatter_file(path: Path) -> Tuple[Optional[dict], str]:
    """Read file and parse frontmatter."""
    if not path.exists():
        return None, ""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERROR] Failed to read {path}: {e}", file=sys.stderr)
        return None, ""
    return parse_frontmatter(content)


def write_with_frontmatter(path: Path, metadata: dict, body: str) -> None:
    """Write a markdown file with YAML frontmatter."""
    fm_str = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, default_flow_style=False)
    content = f"---\n{fm_str}---\n\n{body}"
    path.write_text(content, encoding="utf-8")


# === CLI ===

def main():
    """CLI: parse frontmatter from a file and print as JSON."""
    import argparse
    import json

    p = argparse.ArgumentParser(description="Parse YAML frontmatter from a markdown file")
    p.add_argument("file", help="Path to markdown file")
    p.add_argument("--body", action="store_true", help="Also print the body")
    args = p.parse_args()

    path = Path(args.file)
    meta, body = parse_frontmatter_file(path)

    print(f"--- {path} ---")
    if meta is None:
        print("(no frontmatter)")
    else:
        print(json.dumps(meta, indent=2, ensure_ascii=False))

    if args.body:
        print("\n--- body ---")
        print(body[:2000] + ("..." if len(body) > 2000 else ""))


if __name__ == "__main__":
    main()
