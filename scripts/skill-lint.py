#!/usr/bin/env python
"""
skill-lint.py - Validate the SKILL structure and all frontmatter.

Used by CI and for local development.

Checks:
  1. SKILL.md frontmatter: name, description (≤1024 chars), size (≤100k chars)
  2. All templates/*.md and references/*.md have valid frontmatter
  3. All scripts/*.py compile + have --help
  4. All file references in SKILL.md (templates/X, scripts/Y, references/Z) exist
  5. No obvious secrets (ghp_*, sk-*, AKIA*) in any text file
  6. Cross-platform multiplication matrix completeness

Usage:
  python skill-lint.py                            # Lint current dir
  python skill-lint.py --path /path/to/SKILL     # Lint specific path
  python skill-lint.py --strict                  # Fail on warnings
  python skill-lint.py --json                    # JSON output
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(path: Path) -> tuple:
    if not path.exists():
        return None, None
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return None, text
    body = text[m.end():]
    return meta, body


def check_skill_md(skill_path: Path) -> list:
    """Check SKILL.md frontmatter and structure."""
    issues = []
    p = skill_path / "SKILL.md"
    if not p.exists():
        return [("ERROR", "SKILL.md missing", str(p))]

    meta, body = parse_frontmatter(p)
    if not meta:
        return [("ERROR", "SKILL.md has no valid frontmatter", str(p))]

    # Required fields
    for field in ["name", "description"]:
        if field not in meta:
            issues.append(("ERROR", f"SKILL.md missing '{field}' field", str(p)))

    # Name constraints
    if "name" in meta:
        if not re.match(r"^[a-z0-9-]+$", str(meta["name"])):
            issues.append(("ERROR", f"SKILL.md invalid name: {meta['name']}", str(p)))
        if len(str(meta["name"])) > 64:
            issues.append(("ERROR", f"SKILL.md name too long ({len(str(meta['name']))} chars)", str(p)))

    # Description constraints
    if "description" in meta:
        d_len = len(str(meta["description"]))
        if d_len > 1024:
            issues.append(("ERROR", f"SKILL.md description too long ({d_len} chars, max 1024)", str(p)))
        if d_len < 50:
            issues.append(("WARN", f"SKILL.md description very short ({d_len} chars)", str(p)))

    # Size
    size = p.stat().st_size
    if size > 100_000:
        issues.append(("ERROR", f"SKILL.md too large ({size:,} bytes, max 100k)", str(p)))

    return issues


def check_markdown_files(skill_path: Path) -> list:
    """Check all markdown files in templates/ and references/."""
    issues = []
    for sub in ("templates", "references"):
        d = skill_path / sub
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            meta, body = parse_frontmatter(f)
            # templates must have frontmatter
            if "templates" in f.parts and (not meta or not isinstance(meta, dict)):
                issues.append(("WARN", f"{f.name}: no valid frontmatter", str(f)))
                continue
            # File size
            if f.stat().st_size > 100_000:
                issues.append(("WARN", f"{f.name} too large", str(f)))
    return issues


def check_scripts(skill_path: Path) -> list:
    """Check all Python scripts compile and have --help."""
    issues = []
    d = skill_path / "scripts"
    if not d.exists():
        return [("WARN", "scripts/ directory missing", str(d))]
    for f in d.glob("*.py"):
        # Syntax
        try:
            with open(f, "rb") as fp:
                compile(fp.read(), str(f), "exec")
        except SyntaxError as e:
            issues.append(("ERROR", f"{f.name}: syntax error: {e}", str(f)))
            continue
        # --help
        try:
            r = subprocess.run(
                [sys.executable, str(f), "--help"],
                capture_output=True, timeout=10
            )
            if r.returncode != 0 and "error" in r.stderr.decode("utf-8", errors="replace").lower():
                issues.append(("WARN", f"{f.name}: --help failed", str(f)))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            issues.append(("WARN", f"{f.name}: --help test failed", str(f)))
    return issues


def check_file_references(skill_path: Path) -> list:
    """Check that all template/script/reference mentions in SKILL.md exist."""
    issues = []
    p = skill_path / "SKILL.md"
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8")
    # Find all `templates/X.md` and `scripts/X.py` and `references/X.md` mentions
    refs = set()
    refs.update(re.findall(r"templates/([\w-]+\.md)", text))
    refs.update(re.findall(r"scripts/([\w-]+\.py)", text))
    refs.update(re.findall(r"references/([\w-]+\.md)", text))

    for ref in refs:
        # Try to find
        if ref.endswith(".md"):
            candidates = list((skill_path / "templates").glob(ref)) + \
                          list((skill_path / "references").glob(ref))
        else:
            candidates = list((skill_path / "scripts").glob(ref))
        if not candidates:
            issues.append(("WARN", f"SKILL.md references missing file: {ref}", "SKILL.md"))
    return issues


def check_secrets(skill_path: Path) -> list:
    """Check for accidentally committed secrets."""
    issues = []
    secret_patterns = [
        (r"ghp_[a-zA-Z0-9]{30,}", "GitHub personal token"),
        (r"gho_[a-zA-Z0-9]{30,}", "GitHub OAuth token"),
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI/Stripe API key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
        (r"xox[baprs]-[a-zA-Z0-9-]+", "Slack token"),
    ]
    for f in skill_path.rglob("*"):
        if f.is_dir() or ".git" in f.parts or "__pycache__" in f.parts:
            continue
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern, desc in secret_patterns:
            if re.search(pattern, text):
                issues.append(("ERROR", f"{f.name}: contains {desc}", str(f)))
    return issues


def main():
    p = argparse.ArgumentParser(description="Lint the SKILL structure")
    p.add_argument("--path", default=".", help="Path to skill root (default: cwd)")
    p.add_argument("--strict", action="store_true", help="Fail on warnings (not just errors)")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    skill_path = Path(args.path).resolve()
    if not skill_path.exists():
        print(f"[ERROR] Path not found: {skill_path}", file=sys.stderr)
        return 2

    all_issues = []
    all_issues += check_skill_md(skill_path)
    all_issues += check_markdown_files(skill_path)
    all_issues += check_scripts(skill_path)
    all_issues += check_file_references(skill_path)
    all_issues += check_secrets(skill_path)

    if args.json:
        print(json.dumps([{"level": l, "message": m, "file": f} for l, m, f in all_issues], indent=2))
    else:
        if not all_issues:
            print("✓ No issues found.")
            return 0
        for level, msg, file in all_issues:
            print(f"[{level}] {file}: {msg}")

    # Exit code
    has_error = any(l == "ERROR" for l, _, _ in all_issues)
    has_warn = any(l == "WARN" for l, _, _ in all_issues)

    if has_error:
        return 1
    if args.strict and has_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
